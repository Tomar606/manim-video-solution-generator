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
SMALL_W, SMALL_Y = 605, 1325       # 56% of 1080
EASE = 0.5                          # seconds, ease-in-ease-out each edge
CANVAS_W, CANVAS_H = 800, 1100      # holds the small avatar; zoom reaches full


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


def composite(bg, avatar, key, out, windows=None):
    k = (f"hsvkey=hue={key['hue']}:sat={key['sat']}:val=%s:"
         f"similarity={key['sim']}:blend=0.05,format=rgba,alphaextract")
    alpha = ("[a1][a2]blend=all_mode=darken,dilation,dilation,erosion,erosion,"
             "eq=contrast=2.2:brightness=-0.10,erosion,erosion,gblur=sigma=1.0")
    # ORDER IS LOAD-BEARING: despill runs on the COLOUR branch only, never
    # before the key. Despilling first turns the green screen brown, so hsvkey
    # no longer finds the hue it is looking for, nothing becomes transparent,
    # and the whole despilled background composites as a brown rectangle behind
    # the presenter. The keys must see the raw crop.
    head = (f"[1:v]crop=650:930:650:150,format=rgba,split=3[c][d1][d2];"
            f"[d1]{k % key['v1']}[a1];[d2]{k % key['v2']}[a2];{alpha}[al];"
            f"[c]despill=type=green:mix=0.7:expand=0.5[cc];")

    if windows:
        # The presenter switches between two sizes with overlay `enable`.
        #
        # THIS IS A CUT, NOT A RAMP, and four attempts at a smooth one have
        # failed — recorded here so the fifth does not repeat them:
        #   `scale`            cannot change output size per frame at all
        #   `blend=all_expr`   works, but evaluates per pixel: 17x the whole job
        #   `zoompan`          its `z` did not follow the time expression here;
        #                      measured, the presenter still stepped in a frame
        #   alpha cross-fade   `colorchannelmixer=aa=0` zeroes alpha for good
        #                      and `fade` cannot restore what is no longer there,
        #                      so the presenter disappeared entirely
        # A working cut beats a broken dissolve. The cut lands where the stage
        # content appears or clears anyway.
        inside = "+".join(f"between(t\\,{a:.2f}\\,{b:.2f})" for a, b in windows)
        fc = (head +
              f"[cc][al]alphamerge,split=2[av1][av2];"
              f"[av1]scale={FULL_W}:-2:flags=lanczos[big];"
              f"[av2]scale={SMALL_W}:-2:flags=lanczos[small];"
              f"[0:v]format=rgba[bg];"
              f"[bg][big]overlay=x=(W-w)/2:y={FULL_Y}:eval=init:"
              f"enable='not({inside})':eof_action=pass[o1];"
              f"[o1][small]overlay=x=(W-w)/2:y={SMALL_Y}:eval=init:"
              f"enable='{inside}':eof_action=pass,format=yuv420p[v]")

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
    print(f"compositing -> {out}" + (f" ({len(windows)} resize window(s))" if windows else ""))
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
    composite(bg, av, json.loads(Path(keyf).read_text()), out, wins)
