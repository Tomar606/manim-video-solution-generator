"""Find the times when Manim content sits behind the presenter.

Measured from the rendered background, never guessed: any ink inside the
presenter's own rectangle is content he would cover. tools/composite.py shrinks
him during these windows and restores full size outside them.

    python tools/avatar_windows.py bg.mp4 windows.json 91

This is a safety net, not the primary defence. The primary defence is the
scene's own layout guard — `place()` fits every block inside the stage band and
`cue()` clears the stage by default. Content still reaches the presenter when a
label is attached with `next_to` AFTER placement, since that escapes the clamp;
if this script reports a long window, fix the scene rather than relying on the
resize.
"""
from __future__ import annotations

import io
import json
import subprocess
import sys

import numpy as np
from PIL import Image

AV_TOP, AV_L, AV_R = 955, 20, 1060      # the presenter's rectangle, full size
INK = 1200                              # px of content before it is worth resizing
PAD = 0.8                               # start the shrink before content appears


def windows(video, dur, step=0.5):
    hits = []
    for t in np.arange(step, dur, step):
        raw = subprocess.run(
            ["ffmpeg", "-v", "error", "-ss", f"{t:.1f}", "-i", str(video),
             "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-"],
            capture_output=True).stdout
        if not raw:
            continue
        a = np.asarray(Image.open(io.BytesIO(raw)).convert("L")).astype(int)
        if (a[AV_TOP:, AV_L:AV_R] > 140).sum() > INK:
            hits.append(round(float(t), 1))

    runs = []
    if hits:
        start = prev = hits[0]
        for t in hits[1:]:
            if t - prev > 1.5:
                runs.append([start, prev])
                start = t
            prev = t
        runs.append([start, prev])

    out = []
    for a, b in ([max(0.0, a - PAD), min(dur, b + PAD)] for a, b in runs):
        if out and a <= out[-1][1] + 0.4:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([round(a, 1), round(b, 1)])
    return out


if __name__ == "__main__":
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    w = windows(sys.argv[1], float(sys.argv[3]))
    json.dump(w, open(sys.argv[2], "w"), indent=2)
    print(f"{len(w)} window(s) where content is behind the presenter")
    for a, b in w:
        print(f"   {a:6.1f}s - {b:6.1f}s")
