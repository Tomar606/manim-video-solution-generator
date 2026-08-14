"""Key the presenter onto the Manim background and write the final video.

    python tools/composite.py bg.mp4 avatar.mp4 key.json out.mp4 [windows.json]

`key.json` comes from tools/calibrate_key.py. `windows.json` is the optional
output of tools/avatar_windows.py: the times when Manim content sits behind the
presenter, during which the presenter shrinks and drops so the content shows.

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
Implemented as two complete composites blended by a time expression, NOT by
scaling the avatar stream. `scale` cannot change output size per frame, and
`zoompan` destroys the alpha the key just produced. Blending two finished RGB
frames is smooth, keeps the key intact, and ramps over 0.6s so the change reads
as the presenter stepping back rather than as a cut.

It is slow — `blend=all_expr` evaluates its expression per pixel, and a 90s
1080x1920 part takes roughly 40 minutes. With no windows it falls back to a
single composite, which is a few minutes.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

# where the presenter sits, full size and reduced
FULL_W, FULL_Y = 1040, 955
SMALL_W, SMALL_Y = 846, 1140
RAMP = 0.6


def _weight_expr(windows) -> str:
    """W(T): 0 = full size, 1 = shrunk, with a ramp at each edge."""
    terms = [f"min((T-{a:.2f})/{RAMP}\\,1)*min(({b:.2f}-T)/{RAMP}\\,1)"
             for a, b in windows]
    inner = terms[0] if len(terms) == 1 else "max(" + "\\,".join(terms) + ")"
    while inner.count("max(") > 1:            # ffmpeg's max takes two arguments
        inner = inner.replace("max(", "max(", 1)
    return f"clip({inner}\\,0\\,1)"


def composite(bg, avatar, key, out, windows=None):
    k = (f"hsvkey=hue={key['hue']}:sat={key['sat']}:val=%s:"
         f"similarity={key['sim']}:blend=0.05,format=rgba,alphaextract")
    alpha = ("[a1][a2]blend=all_mode=darken,dilation,dilation,erosion,erosion,"
             "eq=contrast=2.2:brightness=-0.10,erosion,erosion,gblur=sigma=1.0")
    head = (f"[1:v]crop=650:930:650:150,format=rgba,"
            f"despill=type=green:mix=0.7:expand=0.5,split=3[c][d1][d2];"
            f"[d1]{k % key['v1']}[a1];[d2]{k % key['v2']}[a2];{alpha}[al];")

    if windows:
        w = _weight_expr(windows)
        fc = (head +
              f"[c][al]alphamerge,split=2[av1][av2];"
              f"[av1]scale={FULL_W}:-2:flags=lanczos[big];"
              f"[av2]scale={SMALL_W}:-2:flags=lanczos[small];"
              f"[0:v]format=rgba,split=2[bg1][bg2];"
              f"[bg1][big]overlay=x=(W-w)/2:y={FULL_Y}:eval=init,format=yuv420p[full];"
              f"[bg2][small]overlay=x=(W-w)/2:y={SMALL_Y}:eval=init,format=yuv420p[shr];"
              f"[full][shr]blend=all_expr='A*(1-({w}))+B*({w})'[v]")
    else:
        fc = (head +
              f"[c][al]alphamerge,scale={FULL_W}:-2:flags=lanczos[av];"
              f"[0:v]format=rgba[bg];"
              f"[bg][av]overlay=x=(W-w)/2:y={FULL_Y}:eval=init,format=yuv420p[v]")

    cmd = ["ffmpeg", "-v", "error", "-i", str(bg), "-i", str(avatar),
           "-filter_complex", fc, "-map", "[v]", "-map", "1:a",
           "-c:v", "libx264", "-preset", "medium", "-crf", "19",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
           "-movflags", "+faststart", str(out), "-y"]
    print(f"compositing -> {out}" + (f" ({len(windows)} resize window(s))" if windows else ""))
    subprocess.run(cmd, check=True)
    print("done")


if __name__ == "__main__":
    if len(sys.argv) < 5:
        sys.exit(__doc__)
    bg, av, keyf, out = sys.argv[1:5]
    wins = json.loads(Path(sys.argv[5]).read_text()) if len(sys.argv) > 5 else None
    composite(bg, av, json.loads(Path(keyf).read_text()), out, wins)
