"""Where the presenter's head is, and whether any chip is sitting on it.

    python tools/avatar_clearance.py <prechip.mp4> <bg.mp4> <plan.json>

The presenter is composited over the background, so differencing the two isolates
his silhouette exactly — the topmost row that differs IS the top of his head, per
frame, including whatever the zoom and pan are doing at that moment.

A chip is placed at `top` and is as tall as its PNG. If its bottom reaches the
head, the graphic and the presenter are fighting for the same pixels, which is
what put "माइकल फैराडे (1791–1867)" across his forehead.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

BAND_TOP = 380
CLEAR = 24          # px of daylight we insist on between graphic and head


def frame(path, t, td):
    p = Path(td) / f"{Path(path).stem}_{t}.png"
    subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", str(path),
                    "-frames:v", "1", "-y", str(p)], check=True)
    return np.asarray(Image.open(p).convert("L")).astype(int)


def head_top(pre, bg, t, td):
    d = np.abs(frame(pre, t, td) - frame(bg, t, td))
    rows = np.where((d > 26).sum(axis=1) > 12)[0]      # a real silhouette, not noise
    return int(rows[0]) if len(rows) else 1920


def main():
    pre, bg, planf = sys.argv[1:4]
    plan = json.loads(Path(planf).read_text())
    bad = []
    with tempfile.TemporaryDirectory() as td:
        print("  chip        window            chip bottom   head top   clearance")
        for c in plan:
            name = Path(c["png"]).stem
            h = Image.open(c["png"]).height
            bottom = c.get("top", BAND_TOP) + h
            ts = np.linspace(c["start"] + 0.3, c["end"] - 0.3, 5)
            head = min(head_top(pre, bg, round(float(t), 2), td) for t in ts)
            gap = head - bottom
            flag = "" if gap >= CLEAR else "   <<< OVERLAP"
            print(f"  {name:10s} {c['start']:6.2f}-{c['end']:6.2f}"
                  f"      {bottom:5d}       {head:5d}     {gap:+5d}{flag}")
            if gap < CLEAR:
                bad.append((name, bottom, head, gap))
    if bad:
        print(f"\n  {len(bad)} chip(s) reach the presenter. Raise `top` or shrink the chip.")
        return 1
    print("\n  every chip clears the presenter")
    return 0


if __name__ == "__main__":
    sys.exit(main())
