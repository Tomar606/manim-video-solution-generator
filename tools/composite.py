"""Key the presenter onto the Manim background and write the final video.

    python tools/composite.py bg.mp4 avatar.mp4 key.json out.mp4 [windows.json]

`key.json` comes from tools/calibrate_key.py. `windows.json` is the optional
output of tools/avatar_windows.py: the times when Manim content sits behind the
presenter, during which the presenter shrinks and drops so the content shows.

THE END CARD
------------
The last part closes on the answer photo, which runs several seconds PAST the
presenter's audio. `eof_action=pass` on every overlay lets the background carry
on once the avatar clip ends, instead of the composite stopping at the shorter
of the two.

THE KEY
-------
Hue-based, keyed twice, combined with `darken`. See tools/calibrate_key.py for
why — briefly: the screen is lit unuevenly, so an RGB-distance key wide enough
for its dark side also matches skin and holes the face.

The alpha is then repaired in four steps, each fixing something visible:
  close (dilate/erode)  fills pinholes in hair and shirt
  crush (eq)            drives soft background alpha to zero without touching
                        the fully-opaque interior
  erode x2              cuts the outer ring of spill-contaminated pixels, which
                        despill otherwise turns into a dark olive rim on the hair
  gblur                 feathers the edge so it does not alias on the plate

THE RESIZE
----------
`scale` cannot change output size per frame and `zoompan` destroys the alpha the
key just produced, so the two sizes are two pre-scaled streams and `overlay
enable=` picks between them per frame. That costs nothing; blending two finished
composites with an expression cost 9x the whole rest of the job.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

# Where the presenter sits. Measured off the reference stills, not guessed:
# the presenter is 56-66% of frame width there, against 96% in our first cut —
# he was half again too big and crowding every diagram.
#   no diagram on screen : ~66% wide, head at ~51%
#   diagram on screen    : ~56% wide, head at ~69% — measured off the
#                          question-card still, where the years pill has
#                          to clear his forehead
FULL_W, FULL_Y = 712, 966          # 66% of 1080
SMALL_W, SMALL_Y = 668, 1245        # a 6% step, not 15% — just enough
                                    # to clear content that stops at 60%       # 56% of 1080
EASE = 0.75                         # seconds, the ramp at each edge
PRESENTER_FADE = 0.9                # slow enough to read as direction,
                                    # not as a dropped frame
FPS = 30
CANVAS_W, CANVAS_H = 800, 1150      # holds the small avatar; zoom reaches full


def _ease_expr(windows, var="t") -> str:
    """0 outside every window, 1 inside, easing across EASE seconds at each edge.

    `(1-cos(pi*x))/2` is the cosine ease-in-ease-out: flat at both ends, fastest
    in the middle. ffmpeg's max() takes two arguments, so several windows nest.

    `var` matters: zoompan has NO `t` — its clock is `it` (input timestamp) —
    while overlay uses `t`. Passing `t` to zoompan makes the expression evaluate
    to a constant, and the resize becomes the hard cut this exists to avoid.
    """
    h = EASE / 2

    def one(a, b):
        up = f"(1-cos(PI*clip(({var}-{a - h:.2f})/{EASE}\\,0\\,1)))/2"
        dn = f"(1-cos(PI*clip(({b + h:.2f}-{var})/{EASE}\\,0\\,1)))/2"
        return f"min({up}\\,{dn})"

    expr = one(*windows[0])
    for a, b in windows[1:]:
        expr = f"max({expr}\\,{one(a, b)})"
    return expr


def composite(bg, avatar, key, out, windows=None, presenter=None):
    k = (f"hsvkey=hue={key['hue']}:sat={key['sat']}:val=%s:"
         f"similarity={key['sim']}:blend=0.05,format=rgba,alphaextract")
    alpha = ("[a1][a2]blend=all_mode=darken,dilation,dilation,erosion,erosion,"
             "eq=contrast=2.2:brightness=-0.10,erosion,erosion,gblur=sigma=1.0")
    # ORDER IS LOAD-BEARING: despill runs on the COLOUR branch only, never
    # before the key. Despilling first turns the green screen brown, so hsvkey
    # no longer finds the hue it is looking for, nothing becomes transparent,
    # and the whole despilled background composites as a brown rectangle behind
    # the presenter. The keys must see the raw crop.
    # NORMALISE THE FRAMERATE FIRST. The HeyGen clips are 25fps while the Manim
    # background is 30. Plain `overlay` reconciles that on its own, but zoompan
    # re-times the stream against its own clock and the picture then drifts off
    # the audio — a desync that grows through the clip and only shows up on
    # playback. `fps` duplicates frames with correct timestamps; zoompan can be
    # trusted once every stream reaching it is already at the target rate.
    # THE PRESENTER STEPPING ASIDE.
    # Where a diagram or a derivation needs the whole vertical frame, he fades
    # out and returns when the demonstration ends. Done on the keyed alpha with
    # `fade=alpha=1`, which is a cheap per-frame ramp — NOT with
    # colorchannelmixer=aa, which zeroed the alpha permanently and lost him for
    # the rest of the clip, and not with blend expressions, which cost 17x.
    # Fade the MASK's luma, not an alpha channel. `[al]` is a greyscale matte
    # that alphamerge applies later — it has no alpha plane of its own, so
    # `fade=alpha=1` on it is a no-op and the presenter stayed fully visible
    # through the whole derivation. Fading the matte to black is what makes him
    # transparent.
    hide = ""
    for a, z in (presenter or []):
        ramp_in = max(a + PRESENTER_FADE, z - PRESENTER_FADE)
        hide += (
            # ramp out, ONLY across its own seconds
            f",fade=t=out:st={a:.2f}:d={PRESENTER_FADE}:color=black"
            f":enable='between(t,{a:.2f},{a + PRESENTER_FADE:.2f})'"
            # hold him hidden for the body of the window
            f",lutyuv=y=0:enable='between(t,{a + PRESENTER_FADE:.2f},{ramp_in:.2f})'"
            # ramp back in, again only across its own seconds
            f",fade=t=in:st={ramp_in:.2f}:d={PRESENTER_FADE}:color=black"
            f":enable='between(t,{ramp_in:.2f},{z:.2f})'")

    head = (f"[1:v]fps={FPS},crop=650:930:650:150,format=rgba,split=3[c][d1][d2];"
            f"[d1]{k % key['v1']}[a1];[d2]{k % key['v2']}[a2];{alpha}{hide}[al];"
            f"[c]despill=type=green:mix=0.7:expand=0.5[cc];")

    if windows:
        # The size change RAMPS over EASE seconds — a true scale, per frame.
        #
        # Five attempts got here; recorded so nobody repeats them:
        #   `scale`            cannot change output size per frame at all
        #   `blend=all_expr`   works, but per-pixel: 17x the whole job
        #   `zoompan` with it/ot  DOES NOT RAMP. Tested in isolation, `z` follows
        #                      neither `it` nor `ot` — only `on`, the output
        #                      FRAME NUMBER. That one substitution is the whole
        #                      fix; everything below had been right before.
        #   fade + colorchannelmixer=aa=0  zeroed alpha for good; presenter gone
        #   alpha cross-dissolve  showed BOTH sizes at once — a double exposure,
        #                      because the two differ in position as well as size
        #
        # zoompan destroys alpha, so colour and alpha are zoomed as two separate
        # streams with the identical curve and merged after. The alpha travels
        # as its own greyscale video and survives intact.
        #
        # zoompan only zooms IN, so the canvas carries the presenter at his
        # SMALL size and zooms out to full when nothing is behind him.
        ratio = FULL_W / SMALL_W
        T = f"(on/{FPS})"                       # zoompan's only usable clock
        ease_z = _ease_expr(windows, T)
        ease_y = _ease_expr(windows, "t")       # overlay does have `t`
        z = f"1+{ratio - 1:.4f}*(1-({ease_z}))"
        # zoompan zooms about x=0,y=0 unless told otherwise, which walks the
        # presenter left as he scales — the off-centre drift the manager spotted.
        # Anchoring x to the canvas centre keeps him centred at every zoom level.
        pan = (f"pad={CANVAS_W}:{CANVAS_H}:(ow-iw)/2:0:%s,"
               f"zoompan=z='{z}':d=1:s={CANVAS_W}x{CANVAS_H}:fps={FPS}"
               f":x='iw/2-(iw/zoom/2)':y='0'")
        y = f"{FULL_Y}+({SMALL_Y - FULL_Y})*({ease_y})"
        fc = (head +
              f"[cc][al]alphamerge,split=2[colr][alph];"
              f"[colr]scale={SMALL_W}:-2:flags=lanczos,{pan % 'black@0'}[zc];"
              f"[alph]alphaextract,scale={SMALL_W}:-2:flags=lanczos,"
              f"{pan % 'black'}[za];"
              f"[zc][za]alphamerge[av];"
              f"[0:v]format=rgba[bg];"
              f"[bg][av]overlay=x=(W-w)/2:y='{y}':eval=frame:"
              f"eof_action=pass,format=yuv420p[v]")

    else:
        fc = (head +
              f"[cc][al]alphamerge,scale={FULL_W}:-2:flags=lanczos[av];"
              f"[0:v]format=rgba[bg];"
              f"[bg][av]overlay=x=(W-w)/2:y={FULL_Y}:eval=init:eof_action=pass,format=yuv420p[v]")

    # Write to a temp name and move into place. A previous run killed mid-write
    # left a partial file at the destination, and the next run wrote to the same
    # path while the dying process still held it — two writers, and the result
    # decoded with 2604 errors while still reporting a valid duration.
    out = Path(out)
    tmp = out.with_suffix(".partial.mp4")
    cmd = ["ffmpeg", "-v", "error", "-i", str(bg), "-i", str(avatar),
           "-filter_complex", fc, "-map", "[v]", "-map", "1:a",
           "-c:v", "libx264", "-preset", "medium", "-crf", "19",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
           "-movflags", "+faststart", str(tmp), "-y"]
    print(f"compositing -> {out}"
          + (f" ({len(windows)} resize window(s))" if windows else "")
          + (f" ({len(presenter)} presenter fade(s))" if presenter else ""))
    subprocess.run(cmd, check=True)

    # refuse to publish a file that does not decode cleanly
    errs = subprocess.run(["ffmpeg", "-v", "error", "-i", str(tmp), "-f", "null", "-"],
                          capture_output=True, text=True).stderr.strip()
    if errs:
        raise SystemExit(f"{tmp} decodes with errors, not moving into place:\n"
                         f"{errs.splitlines()[0]}")
    tmp.replace(out)
    print("done")


if __name__ == "__main__":
    if len(sys.argv) < 5:
        sys.exit(__doc__)
    bg, av, keyf, out = sys.argv[1:5]
    wins = json.loads(Path(sys.argv[5]).read_text()) if len(sys.argv) > 5 else None
    pres = json.loads(Path(sys.argv[6]).read_text()) if len(sys.argv) > 6 else None
    composite(bg, av, json.loads(Path(keyf).read_text()), out, wins, pres)
