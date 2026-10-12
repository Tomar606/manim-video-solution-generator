"""Recover a render's background with nothing on it.

    python tools/plate_from_render.py <render.mp4> <plate.png> [--fps 2]

The end card sits on a band of the video's own background, so that band has to
come from somewhere. The obvious sources both fail:

  * the background ASSET (`assets/backgrounds/chemistry.png`) is the input to
    the render, not its output — the theme scales, crops and darkens it, and a
    band pasted straight from the asset is visibly lighter than the frame it
    butts against
  * a frame LIFTED from the render carries whatever was on screen at that
    moment, and on a part where the captions hold through the pauses there is
    no clean moment to lift

So take the per-pixel MEDIAN across the whole part. The background is the only
thing that does not move: a caption glyph, a label or a diagram stroke covers
any given pixel for a minority of the runtime, and the median throws it out.
Measured on CHE-C4-LA-01 part 3 — 240 frames — the plate came back matching the
render's own cleanest frame to within 102 pixels of 2,073,600.

Feed it the MANIM/edu render, never the composited file: the presenter does not
move enough between frames for a median to remove him.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

MAX_FRAMES = 180        # 180 x 1920 x 1080 x 3 is about 1.1GB held at once


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("render", type=Path)
    ap.add_argument("out", type=Path)
    ap.add_argument("--fps", type=float, default=2.0,
                    help="frames sampled per second (default 2)")
    a = ap.parse_args()
    if not a.render.exists():
        raise SystemExit(f"❌ not found: {a.render}")

    import numpy as np
    from PIL import Image

    tmp = Path(tempfile.mkdtemp(prefix="plate-"))
    try:
        subprocess.run(["ffmpeg", "-v", "error", "-i", str(a.render),
                        "-vf", f"fps={a.fps}", "-f", "image2",
                        str(tmp / "%05d.png"), "-y"], check=True)
        fs = sorted(tmp.glob("*.png"))
        if not fs:
            raise SystemExit("❌ no frames came out of the render")
        # Evenly thinned, not truncated: the first N frames of a part are one
        # scene, and their median is that scene's graphic, not the background.
        if len(fs) > MAX_FRAMES:
            step = len(fs) / MAX_FRAMES
            fs = [fs[int(i * step)] for i in range(MAX_FRAMES)]

        first = np.asarray(Image.open(fs[0]).convert("RGB"))
        stack = np.empty((len(fs), *first.shape), dtype=np.uint8)
        stack[0] = first
        for i, f in enumerate(fs[1:], 1):
            stack[i] = np.asarray(Image.open(f).convert("RGB"))
        plate = np.median(stack, axis=0).astype(np.uint8)

        a.out.parent.mkdir(parents=True, exist_ok=True)
        Image.fromarray(plate).save(a.out)

        # Say how well it worked, because a part that is never quiet cannot
        # give a clean plate and the caller has to know that before using it.
        off = min(int((np.abs(f.astype(int) - plate.astype(int)).sum(axis=2) > 40).sum())
                  for f in stack)
        px = plate.shape[0] * plate.shape[1]
        print(f"   {a.out}  {plate.shape[1]}x{plate.shape[0]} from {len(fs)} frames — "
              f"closest frame differs in {off} px of {px} ({off / px:.3%})")
        if off > px * 0.02:
            print("   ⚠ no frame of this render comes close to the plate; "
                  "something is on screen for most of the part")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
