"""Measure the crop that holds the whole presenter, for one clip.

    python tools/avatar_crop.py inbox/CHE-C4-LA-03/part1.mp4

tools/composite.py cropped every clip to a FIXED 650x930 window at (650,150).
That window was measured off one shoot, and any gesture outside it is sliced —
in संक्रमण तत्व part 1 the presenter's forearm ends at a hard vertical edge
mid-frame. A crop that is right for one clip is wrong for the next: he stands in
a different place and gestures differently every time.

So the window is measured. Frames are sampled across the clip, the green is
keyed the same way the compositor keys it, and the union of the subject's extent
over all samples — plus a margin — is the crop. Nothing he does in the clip can
then fall outside it.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

MARGIN = 40          # px of air around the widest reach
SAMPLES = 24


def duration(clip: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", str(clip)], capture_output=True, text=True)
    return float(out.stdout.strip())


def measure(clip: Path, samples: int = SAMPLES) -> dict:
    import numpy as np
    from PIL import Image
    dur = duration(clip)
    x0 = y0 = 10 ** 9
    x1 = y1 = -1
    W = H = 0
    for i in range(samples):
        t = dur * (i + 0.5) / samples
        raw = subprocess.run(
            ["ffmpeg", "-v", "error", "-ss", f"{t:.2f}", "-i", str(clip),
             "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-"],
            capture_output=True).stdout
        if not raw:
            continue
        import io
        a = np.asarray(Image.open(io.BytesIO(raw)).convert("RGB")).astype(int)
        H, W = a.shape[:2]
        r, g, b = a[..., 0], a[..., 1], a[..., 2]
        # the same idea as the key: green screen is where green dominates
        green = (g > 90) & (g > r * 1.25) & (g > b * 1.25)
        # "not green" is not the presenter: the shoot has a whiteboard, wall and
        # stands outside the screen, and taking every non-green pixel returned
        # the whole frame. Take the LARGEST CONNECTED non-green region that
        # touches the bottom of the frame — that is the person standing in it.
        from scipy import ndimage
        subj = ndimage.binary_opening(~green, np.ones((5, 5)))
        lab, n = ndimage.label(subj)
        if not n:
            continue
        floor = set(np.unique(lab[-12:, :])) - {0}
        cands = floor or set(np.unique(lab)) - {0}
        best = max(cands, key=lambda k: int((lab == k).sum()))
        ys, xs = np.where(lab == best)
        if not len(xs):
            continue
        x0, x1 = min(x0, int(xs.min())), max(x1, int(xs.max()))
        y0, y1 = min(y0, int(ys.min())), max(y1, int(ys.max()))
    if x1 < 0:
        raise SystemExit(f"{clip}: found no subject — is it a green screen clip?")
    x0 = max(0, x0 - MARGIN); y0 = max(0, y0 - MARGIN)
    x1 = min(W - 1, x1 + MARGIN)
    # NEVER trim the bottom: he is standing on it, and the composite anchors his
    # feet to the bottom of the frame. A crop that stops above the source's
    # bottom edge makes him float above the frame edge.
    y1 = H - 1
    w, h = (x1 - x0) // 2 * 2, (y1 - y0) // 2 * 2      # even dims for x264
    return {"x": x0, "y": y0, "w": w, "h": h, "src_w": W, "src_h": H}


def main() -> int:
    clip = Path(sys.argv[1])
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    box = measure(clip)
    print(f"{clip.name}: crop={box['w']}:{box['h']}:{box['x']}:{box['y']}"
          f"  (source {box['src_w']}x{box['src_h']})")
    if out:
        out.write_text(json.dumps(box, indent=1), encoding="utf-8")
        print(f"-> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
