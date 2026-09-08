"""Raise every chip until it clears the presenter, then say where it should sit.

    python tools/fit_chips_above_avatar.py <prechip.mp4> <bg.mp4> <plan.json>

Chips default to y=380 because that is where the stage band starts. But the
presenter's head is at ~980 and the chips are 750px tall, so the default puts
every one of them 130px into his face. Captions are suppressed underneath a
graphic anyway, so the room they would have used is the graphic's — the chip
simply moves up into it.

Measured per chip, not once globally: the presenter zooms and pans, so his head
is not at the same height throughout.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

BAND_TOP, CLEAR, CEIL = 380, 28, 176      # CEIL: below the caption band


def frame(path, t, td):
    p = Path(td) / f"{Path(path).stem}_{t}.png"
    subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", str(path),
                    "-frames:v", "1", "-y", str(p)], check=True)
    return np.asarray(Image.open(p).convert("L")).astype(int)


def head_top(pre, bg, t, td):
    d = np.abs(frame(pre, t, td) - frame(bg, t, td))
    rows = np.where((d > 26).sum(axis=1) > 12)[0]
    return int(rows[0]) if len(rows) else 1920


def main():
    pre, bg, planf = sys.argv[1:4]
    plan = json.loads(Path(planf).read_text())
    with tempfile.TemporaryDirectory() as td:
        print("  chip        head top   height   top: was -> now   clearance")
        for c in plan:
            name = Path(c["png"]).stem
            h = Image.open(c["png"]).height
            ts = np.linspace(c["start"] + 0.3, c["end"] - 0.3, 5)
            head = min(head_top(pre, bg, round(float(t), 2), td) for t in ts)
            was = c.get("top", BAND_TOP)
            want = min(was, head - CLEAR - h)
            if want < CEIL:                 # cannot fit: the chip has to shrink
                print(f"  {name:10s} {head:6d}   {h:5d}   DOES NOT FIT — "
                      f"needs top={want}, floor is {CEIL}")
                c["top"] = CEIL
            else:
                c["top"] = int(want)
            print(f"  {name:10s} {head:6d}   {h:5d}   {was:4d} -> {c['top']:4d}"
                  f"        {head - (c['top'] + h):+5d}")
    Path(planf).write_text(json.dumps(plan, ensure_ascii=False, indent=1))
    print(f"\n  written: {planf}")


if __name__ == "__main__":
    main()
