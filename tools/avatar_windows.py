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

# the presenter at his FULL size: 66% of 1080 wide, head at 50.3%
AV_TOP, AV_L, AV_R = 966, 184, 896
INK = 4000                              # px of content before it is worth moving
PAD = 0.8                               # start the shrink before content appears
MERGE_GAP = 8.0                         # windows closer than this become one
MIN_LEN = 2.5                           # a window shorter than this is not worth it
PER_MINUTE = 2                          # at most this many moves per minute


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
        if out and a <= out[-1][1] + MERGE_GAP:
            out[-1][1] = max(out[-1][1], b)     # near neighbours become one move
        else:
            out.append([round(a, 1), round(b, 1)])

    # Every resize costs the viewer attention, so only the ones that earn it
    # survive: long enough to be worth doing, and no more than PER_MINUTE of
    # them. Six moves in a 91s clip read as fidgeting.
    out = [w for w in out if w[1] - w[0] >= MIN_LEN]
    cap = max(1, int(round(dur / 60.0 * PER_MINUTE)))
    if len(out) > cap:
        out.sort(key=lambda w: w[0] - w[1])     # longest first
        out = sorted(out[:cap])
    return [[round(a, 1), round(b, 1)] for a, b in out]


if __name__ == "__main__":
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    w = windows(sys.argv[1], float(sys.argv[3]))
    json.dump(w, open(sys.argv[2], "w"), indent=2)
    print(f"{len(w)} window(s) where content is behind the presenter")
    for a, b in w:
        print(f"   {a:6.1f}s - {b:6.1f}s")
