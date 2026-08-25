"""Check a generated clip before it is spliced into a video.

    python tools/check_gemini_clip.py <clip.mp4>

A clip from an image model arrives with no guarantees, and the one thing that
makes it unusable is invisible until composite time: any mark below y=960 sits
under the presenter. This measures that, and the other layout rules, so a bad
clip is rejected before it costs a render.
"""
from __future__ import annotations

import io
import subprocess
import sys
from pathlib import Path

STAGE_TOP, STAGE_BOT, HALF = 380, 850, 960


def main() -> int:
    import numpy as np
    from PIL import Image
    v = Path(sys.argv[1])
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                                "format=duration", "-of", "csv=p=0", str(v)],
                               capture_output=True, text=True).stdout.strip() or 0)
    w, h = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v",
                           "-show_entries", "stream=width,height", "-of", "csv=p=0:s=x",
                           str(v)], capture_output=True, text=True).stdout.strip().split("x")[:2]
    bad = []
    if (int(w), int(h)) != (1080, 1920):
        bad.append(f"wrong size {w}x{h}, must be 1080x1920")
    worst_low, worst_cap = 0, 0
    for t in [dur * f for f in (0.1, 0.3, 0.5, 0.7, 0.9)]:
        raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.2f}", "-i", str(v),
                              "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-"],
                             capture_output=True).stdout
        if not raw:
            continue
        a = np.asarray(Image.open(io.BytesIO(raw)).convert("RGB")).astype(int)
        plate = np.median(a[STAGE_TOP - 60:STAGE_TOP - 10, :], axis=(0, 1))
        ink = np.abs(a - plate).sum(axis=2) > 60
        worst_low = max(worst_low, int(ink[HALF:, :].sum()))
        worst_cap = max(worst_cap, int(ink[:STAGE_TOP - 20, :].sum()))
    if worst_low > 4000:
        bad.append(f"DRAWS BELOW THE HALFWAY LINE: {worst_low} px under y={HALF} — "
                   f"the presenter stands there")
    if worst_cap > 4000:
        bad.append(f"DRAWS IN THE CAPTION BAND: {worst_cap} px above y={STAGE_TOP-20}")
    if not bad:
        print(f"  clip ok: {v.name}, {dur:.1f}s, stage-only")
        return 0
    print(f"  CLIP REJECTED — {v.name}")
    for b in bad:
        print(f"    {b}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
