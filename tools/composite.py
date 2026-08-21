"""Key the presenter onto the Manim background and write the final video.

    python tools/composite.py bg.mp4 avatar.mp4 key.json out.mp4 \
        [windows.json] [presenter.json] [clips_part1.json]

`key.json` comes from tools/calibrate_key.py. `windows.json` is the optional
output of tools/avatar_windows.py: the times when Manim content sits behind the
presenter, during which the presenter shrinks and drops so the content shows.
`presenter.json` comes from tools/presenter_windows.py. `clips_part<N>.json`
comes from `video veo` and lists the Veo clips laid over the background — see
VEO_CUT and _veo_chain() below.

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
import os
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

# A THIRD size, for stretches with nothing on the stage. Filling an empty strip
# with a picture that has not earned its place is worse than leaving it empty —
# so the presenter grows into it instead. 81% wide, head higher, so the frame
# reads as composed rather than half-used.
BIG_W, BIG_Y = 880, 800
FULL_W, FULL_Y = 712, 966          # 66% of 1080
SMALL_W, SMALL_Y = 668, 1245        # a 6% step, not 15% — just enough
                                    # to clear content that stops at 60%       # 56% of 1080
EASE = 0.75                         # seconds, the ramp at each edge
PRESENTER_FADE = 0.9                # slow enough to read as direction,
                                    # not as a dropped frame
FPS = 30
CANVAS_W, CANVAS_H = 800, 1150      # holds the small avatar; zoom reaches full

# Where a Veo clip is laid over the Manim background.
#
# The clip was generated ON the same background plate Manim renders (the PNG is
# uploaded to Flow — see src/veo.py), so the two are the same picture with
# different things drawn on them, and the seam between them is invisible. That
# is the whole reason the plate is attached rather than described.
#
# Only the rows below VEO_CUT are taken. Above it is the caption strip, and the
# caption is Manim's — it has to keep running over the top of the clip, because
# the presenter goes on talking through it. 500 of 1920 is 26%: clear of two
# caption lines at 55pt starting at 0.090, and still above the scene template's
# STAGE_TOP of 0.290. If either of those moves, this moves with it.
VEO_CUT = 500
VEO_FADE = 0.30                    # softens the two cuts; cheap, unlike a blend expr


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


def _veo_chain(clips, first_input):
    """Lay each Veo clip over the background for its own window.

    Returns (filter fragment, name of the resulting background label).

    `tpad` rather than `setpts` to place a clip in time: shifting PTS forward
    leaves overlay with no second input at all before the window opens, and it
    stalls waiting for one instead of passing the background through. Padding
    the front with frames gives it something to consume at every timestamp, and
    `enable=` decides which ones are actually drawn.

    The fade is on alpha and lasts a third of a second at each edge. The plate
    matches, so there is nothing to hide — but a generated clip's first frame
    can still land a shade off, and a ramp that short costs one filter and
    removes the whole question. It is `fade`, not a blend expression: per
    tools/composite.py's own history, a per-pixel expression cost 17x.
    """
    parts, base, n = [], "[0:v]", first_input
    for i, c in enumerate(clips):
        start, end = float(c["start"]), float(c["end"])
        fade_out = max(start, end - VEO_FADE)
        parts.append(
            f"[{n}:v]fps={FPS},scale=1080:1920:flags=lanczos,"
            f"crop=1080:{1920 - VEO_CUT}:0:{VEO_CUT},format=rgba,"
            f"tpad=start_duration={start:.2f}:start_mode=add:color=black@0,"
            f"fade=t=in:st={start:.2f}:d={VEO_FADE}:alpha=1,"
            f"fade=t=out:st={fade_out:.2f}:d={VEO_FADE}:alpha=1[vc{i}];")
        parts.append(
            f"{base}[vc{i}]overlay=x=0:y={VEO_CUT}:"
            f"enable='between(t,{start:.2f},{end:.2f})':"
            f"eof_action=pass:repeatlast=0[vb{i}];")
        base = f"[vb{i}]"
        n += 1

        # The labels go over their own clip and nothing else — they are the one
        # thing besides the animation allowed on screen, and they are typeset by
        # src/veo_labels.py because Veo cannot set Devanagari. Each arrives on
        # the caption that names its part and leaves with the clip.
        for j, lab in enumerate(c.get("labels") or []):
            ls, le = float(lab["start"]), float(lab["end"])
            lf = max(ls, le - VEO_FADE)
            parts.append(
                f"[{n}:v]format=rgba,"
                f"fade=t=in:st={ls:.2f}:d={VEO_FADE}:alpha=1,"
                f"fade=t=out:st={lf:.2f}:d={VEO_FADE}:alpha=1[vl{i}_{j}];")
            parts.append(
                f"{base}[vl{i}_{j}]overlay=x={int(lab['x'])}:y={int(lab['y'])}:"
                f"enable='between(t,{ls:.2f},{le:.2f})':"
                f"eof_action=pass:repeatlast=0[vm{i}_{j}];")
            base = f"[vm{i}_{j}]"
            n += 1
    return "".join(parts), base


def _inputs(clips):
    """ffmpeg -i arguments for the clips and their labels, in the exact order
    _veo_chain() indexes them: each clip, then that clip's labels, then the next.

    A label PNG is a still, so it is looped — `overlay` takes its duration from
    the MAIN input, so an endless second input cannot extend the output. It is
    `-loop 1` rather than a fixed `-t` because the compositor does not know how
    long the finished video is, and guessing short would drop the label early.
    """
    args = []
    for c in clips or []:
        args += ["-i", str(c["path"])]
        for lab in c.get("labels") or []:
            args += ["-loop", "1", "-i", str(lab["png"])]
    return args


def composite(bg, avatar, key, out, windows=None, presenter=None, clips=None,
              big=None, crop=None):
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

    # Veo clips go on FIRST, so the presenter is keyed over the finished
    # background rather than the other way round — he stands in front of the
    # animation, exactly as he does in front of a Manim one.
    veo_fc, BG = _veo_chain(clips or [], 2)

    # The crop MUST come from the clip, not from a constant. The fixed
    # 650x930 window below was measured off one shoot, and it sliced the
    # presenter's forearm off at a hard vertical edge in any clip where he
    # stands or gestures wider — the true extent measures 680 to 886 px across
    # this batch alone. tools/avatar_crop.py measures it per clip.
    cbox = crop or {}
    cw, ch = int(cbox.get("w") or 650), int(cbox.get("h") or 930)
    cx, cy = int(cbox.get("x") or 650), int(cbox.get("y") or 150)
    if not crop:
        print("  ! no measured crop — legacy window, limbs may clip")
    head = (veo_fc +
            f"[1:v]fps={FPS},crop={cw}:{ch}:{cx}:{cy},format=rgba,split=3[c][d1][d2];"
            f"[d1]{k % key['v1']}[a1];[d2]{k % key['v2']}[a2];{alpha}{hide}[al];"
            f"[c]despill=type=green:mix=0.7:expand=0.5[cc];")

    # ANCHOR HIS FEET TO THE BOTTOM OF THE FRAME.
    # FULL_Y/SMALL_Y/BIG_Y were fixed top offsets that only worked while the
    # crop was a fixed 650x930: a wider measured crop scales to a SHORTER
    # avatar at the same on-screen width, so a fixed top left him floating
    # clear of the frame edge. Derive the top from the scaled height instead —
    # then whatever the crop, his feet land on 1920 and only his SIZE changes.
    FRAME_H = 1920
    def top_for(width_px):
        return int(FRAME_H - ch * (width_px / max(cw, 1)))
    full_y, small_y, big_y = top_for(FULL_W), top_for(SMALL_W), top_for(BIG_W)

    if windows or big:
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
        big_ratio = BIG_W / SMALL_W
        T = f"(on/{FPS})"                       # zoompan's only usable clock
        ease_z = _ease_expr(windows, T) if windows else "0"
        ease_y = _ease_expr(windows, "t") if windows else "0"
        # three sizes on one curve: small inside a shrink window, full normally,
        # big inside a `big` window. The two eases never overlap in practice —
        # a shrink window means content is on the stage, a big window means it
        # is empty — so adding them is safe.
        bz = _ease_expr(big, T) if big else "0"
        by = _ease_expr(big, "t") if big else "0"
        z = (f"1+{ratio - 1:.4f}*(1-({ease_z}))"
             f"+{big_ratio - ratio:.4f}*({bz})")
        # zoompan zooms about x=0,y=0 unless told otherwise, which walks the
        # presenter left as he scales — the off-centre drift the manager spotted.
        # Anchoring x to the canvas centre keeps him centred at every zoom level.
        pan = (f"pad={CANVAS_W}:{CANVAS_H}:(ow-iw)/2:0:%s,"
               f"zoompan=z='{z}':d=1:s={CANVAS_W}x{CANVAS_H}:fps={FPS}"
               f":x='iw/2-(iw/zoom/2)':y='0'")
        y = (f"{full_y}+({small_y - full_y})*({ease_y})"
             f"+({big_y - full_y})*({by})")
        fc = (head +
              f"[cc][al]alphamerge,split=2[colr][alph];"
              f"[colr]scale={SMALL_W}:-2:flags=lanczos,{pan % 'black@0'}[zc];"
              f"[alph]alphaextract,scale={SMALL_W}:-2:flags=lanczos,"
              f"{pan % 'black'}[za];"
              f"[zc][za]alphamerge[av];"
              f"{BG}format=rgba[bg];"
              f"[bg][av]overlay=x=(W-w)/2:y='{y}':eval=frame:"
              f"eof_action=pass,format=yuv420p[v]")

    else:
        fc = (head +
              f"[cc][al]alphamerge,scale={FULL_W}:-2:flags=lanczos[av];"
              f"{BG}format=rgba[bg];"
              f"[bg][av]overlay=x=(W-w)/2:y={full_y}:eval=init:eof_action=pass,format=yuv420p[v]")

    # Write to a temp name and move into place. A previous run killed mid-write
    # left a partial file at the destination, and the next run wrote to the same
    # path while the dying process still held it — two writers, and the result
    # decoded with 2604 errors while still reporting a valid duration.
    out = Path(out)
    tmp = out.with_suffix(".partial.mp4")
    # THREADS is capped on purpose. Unbounded, ffmpeg took 320% CPU and about
    # 600MB for a single composite; three of those at once drove an 8GB machine
    # into swap and started killing the user's other apps. x264 also holds a
    # frame buffer per thread, so the cap bounds memory as well as CPU.
    # Raise FFMPEG_THREADS on a bigger machine.
    threads = os.environ.get("FFMPEG_THREADS", "3")
    cmd = ["ffmpeg", "-v", "error", "-threads", threads,
           "-i", str(bg), "-i", str(avatar),
           # Input order is the contract _veo_chain() indexes against: bg is 0,
           # the avatar is 1, then each clip followed by its own labels.
           *_inputs(clips),
           "-filter_complex", fc, "-map", "[v]", "-map", "1:a",
           "-c:v", "libx264", "-preset", "medium", "-crf", "19",
           "-threads", threads, "-x264-params", f"threads={threads}:lookahead-threads=1",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
           "-max_muxing_queue_size", "512",
           "-movflags", "+faststart", str(tmp), "-y"]
    print(f"compositing -> {out}"
          + (f" ({len(windows)} resize window(s))" if windows else "")
          + (f" ({len(presenter)} presenter fade(s))" if presenter else "")
          + (f" ({len(clips)} veo clip(s))" if clips else ""))
    subprocess.run(cmd, check=True)

    # refuse to publish a file that does not decode cleanly
    errs = subprocess.run(["ffmpeg", "-v", "error", "-i", str(tmp), "-f", "null", "-"],
                          capture_output=True, text=True).stderr.strip()
    if errs:
        raise SystemExit(f"{tmp} decodes with errors, not moving into place:\n"
                         f"{errs.splitlines()[0]}")
    tmp.replace(out)
    print("done")


def load_clips(path, root=None):
    """`clips_part<N>.json` from src/veo.py -> what composite() wants.

    Only clips that PASSED the visual review are laid in. A failed one is still
    on disk and still listed, because a clip somebody can watch and overrule is
    more useful than a deleted one — but it does not reach the finished video by
    default. `src` is stored relative to the project so the file survives the
    project being moved.
    """
    path = Path(path)
    root = Path(root) if root else path.parent
    out = []
    for c in json.loads(path.read_text(encoding="utf-8")):
        if not c.get("usable", True):
            print(f"skipping beat@{c['at']} — it did not pass the visual review "
                  f"({c['src']})")
            continue
        labels = []
        for lab in c.get("labels") or []:
            labels.append(dict(lab, png=root / lab["png"]))
        out.append(dict(c, path=root / c["src"], labels=labels))
    return out


if __name__ == "__main__":
    if len(sys.argv) < 5:
        sys.exit(__doc__)
    bg, av, keyf, out = sys.argv[1:5]

    def opt(i):
        """The optional trailing arguments are positional, so there has to be a
        way to say "not this one, but the next one". `-` means skip."""
        if len(sys.argv) <= i:
            return None
        v = sys.argv[i].strip()
        return None if v in ("", "-", "none") else v

    wins = json.loads(Path(opt(5)).read_text()) if opt(5) else None
    pres = json.loads(Path(opt(6)).read_text()) if opt(6) else None
    clips = load_clips(opt(7)) if opt(7) else None
    bigw = json.loads(Path(opt(8)).read_text()) if opt(8) else None
    cbox = json.loads(Path(opt(9)).read_text()) if opt(9) else None
    if cbox is None:
        try:
            from tools.avatar_crop import measure
            cbox = measure(Path(av))
            print(f"  measured crop {cbox['w']}x{cbox['h']} at {cbox['x']},{cbox['y']}")
        except Exception as e:                      # noqa: BLE001
            print(f"  ! crop measurement failed ({type(e).__name__}); legacy window")
    composite(bg, av, json.loads(Path(keyf).read_text()), out, wins, pres, clips,
              big=bigw, crop=cbox)
