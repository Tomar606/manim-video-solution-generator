"""Scale each animated overlay until it clears the presenter.

    python tools/fit_clips.py <prechip.mp4> <bg.mp4> <plan.json>

The chip version of this raises a chip; a full-frame render cannot be raised,
because its title is drawn at the top of the frame and moving it down would
push the whole thing into the presenter anyway. So the clip is SCALED about the
top of the frame instead, and the scale comes from the measured head position.

Measured per clip, not once per part: the presenter zooms and pans, so his head
is not at the same height throughout, and one clip's window may sit entirely
inside a push-in.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

CLEAR = 28          # px of daylight between the artwork and his hair
SAMPLES = 5


def frame(path, t, td, tag):
    p = Path(td) / f"{tag}_{t:.2f}.png"
    subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.2f}", "-i", str(path),
                    "-frames:v", "1", str(p), "-y"], check=True)
    return np.asarray(Image.open(p).convert("RGB")).astype(int)


def head_top(pre, bg, t, td):
    """Topmost row where the composited frame differs from the plate.

    The difference against the background IS the presenter -- nothing else was
    added at this stage, because the clips are burned after compositing.
    """
    d = np.abs(frame(pre, t, td, "p") - frame(bg, t, td, "b")).mean(axis=2)
    rows = np.nonzero((d > 18).sum(axis=1) > 12)[0]
    return int(rows.min()) if len(rows) else 1920


def ink_bottom(mov, td):
    """Lowest row the artwork ever reaches, over the whole clip."""
    out = subprocess.run(["ffmpeg", "-v", "error", "-i", str(mov), "-vf",
                          "fps=2,format=rgba,scale=108:192", "-f", "rawvideo", "-"],
                         capture_output=True).stdout
    fsz = 108 * 192 * 4
    lo = 0
    for i in range(len(out) // fsz):
        a = np.frombuffer(out[i * fsz:(i + 1) * fsz], np.uint8).reshape(192, 108, 4)
        ys = np.nonzero((a[..., 3] > 8).any(axis=1))[0]
        if len(ys):
            lo = max(lo, int(ys.max()) * 10)
    return lo


def main() -> int:
    pre, bg, planf = sys.argv[1:4]
    plan = json.loads(Path(planf).read_text())
    print(f"  {'clip':26s} {'ink to':>7s} {'head':>6s} {'scale':>6s} {'clears':>7s}")
    with tempfile.TemporaryDirectory() as td:
        for c in plan:
            a, b = c["start"], c["end"]
            ts = [a + (b - a) * k / (SAMPLES - 1) for k in range(SAMPLES)]
            head = min(head_top(pre, bg, t, td) for t in ts)
            bottom = ink_bottom(c["mov"], td)
            s = min(1.0, (head - CLEAR) / max(bottom, 1))
            c["scale"] = round(s, 3)
            c["top"] = 0
            print(f"  {Path(c['mov']).stem[13:]:26s} {bottom:7d} {head:6d} "
                  f"{c['scale']:6.3f} {head - bottom * c['scale']:7.0f}")
    Path(planf).write_text(json.dumps(plan, ensure_ascii=False, indent=1))
    print(f"  written: {planf}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
