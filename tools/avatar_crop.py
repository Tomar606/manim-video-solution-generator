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

# The margin is generous ON PURPOSE. The crop is measured from SAMPLED frames,
# so a gesture that peaks between two samples is never seen — the presenter's
# hand was sliced at a hard vertical edge in the first second of the vitamin
# video because his widest reach fell between samples. Margin covers the reach
# the sampling missed; denser sampling reduces how much it has to cover.
MARGIN = 90
SAMPLES = 56


def duration(clip: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", str(clip)], capture_output=True, text=True)
    return float(out.stdout.strip())


def measure(clip: Path, samples: int = SAMPLES) -> dict:
    """Cached: the same clip is composited several times across a rebuild and
    the measurement is the slow part."""
    import hashlib, json as _json
    st = clip.stat()
    key = hashlib.md5(f"{clip}|{st.st_size}|{MARGIN}|{samples}".encode()).hexdigest()[:16]
    cache = Path("/private/tmp/claude-501/avatar_crop_cache")
    cache.mkdir(parents=True, exist_ok=True)
    cf = cache / f"{key}.json"
    if cf.is_file():
        try:
            return _json.loads(cf.read_text())
        except ValueError:
            pass
    box = _measure(clip, samples)
    cf.write_text(_json.dumps(box))
    return box


def _measure(clip: Path, samples: int = SAMPLES) -> dict:
    import numpy as np
    from PIL import Image
    dur = duration(clip)
    x0 = y0 = 10 ** 9
    x1 = y1 = -1
    W = H = 0
    times = [dur * (i + 0.5) / samples for i in range(samples)]
    # The opening and closing seconds carry the biggest gestures and the uniform
    # sweep starts half a step in, so the first ~1.3s was never sampled — which
    # is exactly where the presenter's hand was being sliced.
    times += [0.05, 0.2, 0.4, 0.6, 0.8, 1.0, 1.3, 1.7, 2.2, 3.0]
    times += [max(0.0, dur - x) for x in (0.2, 0.6, 1.0, 1.6, 2.4)]
    widths = []
    centres = []
    for t in sorted(set(round(x, 2) for x in times if 0 <= x < dur)):
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
        fl, fr = int(xs.min()), int(xs.max())
        widths.append(fr - fl)
        # The BODY's centre, measured across the torso only. The full extent
        # includes an outstretched arm, which drags the midpoint sideways; the
        # torso does not move. This is what the frame must be centred on.
        ytop, ybot = int(ys.min()), int(ys.max())
        t0 = ytop + int((ybot - ytop) * 0.45)
        t1 = ytop + int((ybot - ytop) * 0.75)
        tor = np.where(lab[t0:t1, :] == best)[1]
        if len(tor) > 40:
            centres.append((int(tor.min()) + int(tor.max())) / 2.0)
        x0, x1 = min(x0, fl), max(x1, fr)
        y0, y1 = min(y0, int(ys.min())), max(y1, int(ys.max()))
    if x1 < 0:
        raise SystemExit(f"{clip}: found no subject — is it a green screen clip?")
    sx0, sy0, sx1, sy1 = x0, y0, x1, y1        # the subject, before padding
    x0 = max(0, x0 - MARGIN); y0 = max(0, y0 - MARGIN)
    x1 = min(W - 1, x1 + MARGIN)
    # NEVER trim the bottom: he is standing on it, and the composite anchors his
    # feet to the bottom of the frame. A crop that stops above the source's
    # bottom edge makes him float above the frame edge.
    y1 = H - 1
    w, h = (x1 - x0) // 2 * 2, (y1 - y0) // 2 * 2      # even dims for x264
    # The padded box is what gets CROPPED, so no gesture is ever sliced. The
    # SUBJECT box is what the on-screen size is computed from — otherwise adding
    # margin to stop the clipping would shrink the presenter, because he is
    # scaled to a fixed on-screen WIDTH and the padding would be counted as part
    # of him. Crop generously; size from the subject.
    # SIZE from the MEDIAN width, CROP from the union. One frame with an arm
    # fully extended must widen the crop so nothing is sliced, but it must not
    # shrink the presenter for the whole video — his body is the same size
    # throughout, only his reach changes.
    med = int(sorted(widths)[len(widths) // 2]) if widths else (sx1 - sx0)
    body_cx = (sorted(centres)[len(centres) // 2] if centres
               else (sx0 + sx1) / 2.0)
    return {"x": x0, "y": y0, "w": w, "h": h, "src_w": W, "src_h": H,
            "subj_w": max(2, med), "subj_h": max(2, sy1 - sy0),
            "union_w": max(2, sx1 - sx0), "body_cx": round(body_cx, 1)}


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
