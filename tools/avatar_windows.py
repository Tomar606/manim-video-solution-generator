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
    # ONE DECODE, NOT ONE PER SAMPLE.
    #
    # This used to spawn an ffmpeg per 0.5s sample — about 300 process launches
    # for a 150-second part, each re-opening and seeking the file. Two builds in
    # parallel took SEVENTY-FIVE MINUTES here, with the composite not yet
    # started, and it reads as a hung build because the stage prints nothing.
    # Decoding the whole video once at the sample rate and walking the pipe is
    # the same measurement in seconds. The frames are cropped to the
    # presenter's rectangle in the filter graph, so only the pixels that matter
    # are carried across the pipe.
    fps = 1.0 / step
    w, h = AV_R - AV_L, None
    proc = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(video),
         "-vf", f"fps={fps:g},crop={w}:in_h-{AV_TOP}:{AV_L}:{AV_TOP},format=gray",
         "-f", "rawvideo", "-pix_fmt", "gray", "-"],
        capture_output=True)
    buf = np.frombuffer(proc.stdout, dtype=np.uint8)
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
         "stream=height", "-of", "csv=p=0", str(video)],
        capture_output=True, text=True).stdout.strip()
    ih = int(probe or 1920)
    h = ih - AV_TOP
    n = buf.size // (w * h) if w and h else 0
    frames = buf[:n * w * h].reshape(n, h, w).astype(int)
    hits = []
    for i in range(n):
        t = (i + 1) * step
        if t >= dur:
            break
        if (frames[i] > 140).sum() > INK:
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
