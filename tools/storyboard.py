"""See every beat of a scene before committing to a real render.

The review loop was: render 12 minutes, watch, report one layout problem, fix,
render again. This collapses it. `PREVIEW=1` clamps the waits that conform the
scene to the audio clock — a 113-second part spends almost all of its render
sitting still — and the scene is drawn at a low resolution. What comes out is
one contact sheet with every beat on it, so ALL the layout feedback can be given
at once, before the expensive render exists.

    python tools/storyboard.py daniell-cell dan_composed DaniellPart1 \\
        --env DANIELL_PART=1

Writes `projects/<slug>/storyboard_<Scene>.png`, and prints whatever the layout
guard caught while drawing.
"""
from __future__ import annotations

import argparse
import io
import os
import subprocess
import sys
from pathlib import Path

RES = (480, 854)          # a ninth of the pixels of the real render
FPS = 12
COLS = 5


def render_preview(slug, module, scene, extra_env, quality_res=RES):
    root = Path("projects") / slug
    comp = root / "manim_code" / f"{module}.py"
    if not comp.exists():
        sys.exit(f"no composed file at {comp} — run tools/recompose.py")

    env = dict(os.environ, PREVIEW="1")
    env.update(extra_env)
    env["PATH"] = f"{Path.home()}/Library/TinyTeX/bin/universal-darwin:" + env["PATH"]

    out = f"preview_{scene}.mp4"
    cmd = [".venv-manim/bin/python", "-m", "manim", "render", "--disable_caching",
           "-r", f"{quality_res[0]},{quality_res[1]}", "--fps", str(FPS),
           "--media_dir", str(root / "media"), "-o", out, str(comp), scene]
    print(f"drawing {scene} at {quality_res[0]}x{quality_res[1]} with waits collapsed…")
    res = subprocess.run(cmd, env=env, capture_output=True, text=True)
    if res.returncode != 0:
        tail = "\n".join(res.stderr.strip().splitlines()[-12:])
        sys.exit(f"preview render failed:\n{tail}")

    # the layout guard prints at tear-down; surface it here where it is useful
    log = res.stdout + res.stderr
    if "LAYOUT GUARD" in log:
        start = log.index("LAYOUT GUARD")
        print("\n" + log[start:start + 2200].split("=" * 70)[0])

    made = sorted((root / "media" / "videos").rglob(out))
    if not made:
        sys.exit("preview rendered but no file was produced")
    return made[0]


def contact_sheet(video: Path, dest: Path, cols=COLS):
    from PIL import Image, ImageDraw

    dur = float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(video)], capture_output=True, text=True).stdout.strip())
    # one frame per beat: sample densely, then drop frames identical to the last
    n = max(24, min(90, int(dur * 6)))
    shots = []
    last = None
    for k in range(n):
        t = dur * (k + 0.5) / n
        raw = subprocess.run(
            ["ffmpeg", "-v", "error", "-ss", f"{t:.2f}", "-i", str(video),
             "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-"],
            capture_output=True).stdout
        if not raw:
            continue
        im = Image.open(io.BytesIO(raw)).convert("RGB")
        small = im.resize((96, 170))
        if last is not None and _almost_equal(small, last):
            continue
        last = small
        shots.append((t, im))

    if not shots:
        sys.exit("no frames extracted")
    w, h = shots[0][1].size
    rows = (len(shots) + cols - 1) // cols
    sheet = Image.new("RGB", (w * cols, (h + 22) * rows), (16, 18, 24))
    d = ImageDraw.Draw(sheet)
    for i, (t, im) in enumerate(shots):
        x, y = (i % cols) * w, (i // cols) * (h + 22)
        sheet.paste(im, (x, y + 22))
        d.text((x + 6, y + 6), f"{t:6.1f}s", fill=(160, 176, 200))
    dest.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(dest)
    print(f"\n{len(shots)} distinct beats -> {dest}")
    return dest


def _almost_equal(a, b, tol=2.5):
    import numpy as np
    return float(np.abs(np.asarray(a, float) - np.asarray(b, float)).mean()) < tol


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("module")
    ap.add_argument("scene")
    ap.add_argument("--env", action="append", default=[],
                    help="KEY=VALUE passed to the render, e.g. DANIELL_PART=1")
    a = ap.parse_args()
    extra = dict(e.split("=", 1) for e in a.env)
    vid = render_preview(a.slug, a.module, a.scene, extra)
    contact_sheet(vid, Path("projects") / a.slug / f"storyboard_{a.scene}.png")
