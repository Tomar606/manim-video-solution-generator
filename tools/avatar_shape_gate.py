"""Is the presenter the shape he actually is?

    python tools/avatar_shape_gate.py <final.mp4> <source_plate.mp4> [--tol 0.04]

WHY THIS EXISTS
---------------
A delivered cut had the presenter resized straight from a 760x620 keyed crop
into a 640x640 circle and a 400x500 card. Neither resize preserved aspect, so
he was squeezed to 82% and 65% of his true width. It reads as "he looks a bit
compressed, not natural" and it is close to invisible frame by frame, because
every frame is wrong by the same amount and nothing in shot is a known shape.

The in-renderer check (work/frame_gate.scale_log_gate) asserts the code applied
one scale factor. This is the independent one: it measures the SHIPPED video.
Same person, same camera, same lens in both files, so his face has one true
aspect ratio. Any difference between the final and the plate it was cut from
was introduced by the compositor, and that is exactly the defect.

Measuring the face rather than the whole silhouette is deliberate: the
silhouette changes shape whenever he gestures, the face does not.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import numpy as np


def _duration(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(path)],
        capture_output=True, text=True).stdout.strip()
    return float(out) if out else 0.0


def _frames(path: Path, times: list[float]):
    """Decode one RGB frame per timestamp."""
    import io
    from PIL import Image
    for t in times:
        raw = subprocess.run(
            ["ffmpeg", "-v", "error", "-ss", f"{t:.2f}", "-i", str(path),
             "-frames:v", "1", "-f", "image2", "-c:v", "png", "-"],
            capture_output=True).stdout
        if raw:
            yield Image.open(io.BytesIO(raw)).convert("RGB")


def face_aspects(path: Path, times: list[float], detector) -> list[float]:
    """Median-friendly list of face width/height ratios at those timestamps."""
    out = []
    for im in _frames(path, times):
        boxes, probs = detector.detect(im)
        if boxes is None:
            continue
        # the most confident face only; b-roll can contain other people
        i = int(np.argmax(probs))
        if probs[i] < 0.95:
            continue
        x0, y0, x1, y1 = boxes[i]
        h = y1 - y0
        if h > 1:
            out.append((x1 - x0) / h)
    return out


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    tol = 0.04
    if "--tol" in sys.argv:
        tol = float(sys.argv[sys.argv.index("--tol") + 1])
    if len(args) < 2:
        print(__doc__)
        return 2
    final, plate = Path(args[0]), Path(args[1])
    for p in (final, plate):
        if not p.exists():
            print(f"FAIL avatar_shape_gate: {p} does not exist")
            return 1

    try:
        from facenet_pytorch import MTCNN
    except ImportError:
        print("SKIP avatar_shape_gate: facenet-pytorch not installed "
              "(run under .venv-tools)")
        return 0

    det = MTCNN(keep_all=True, device="cpu")
    n = 9
    ft = [_duration(final) * (i + 0.5) / n for i in range(n)]
    pt = [_duration(plate) * (i + 0.5) / n for i in range(n)]

    fa = face_aspects(final, ft, det)
    pa = face_aspects(plate, pt, det)
    if len(fa) < 3 or len(pa) < 3:
        print(f"SKIP avatar_shape_gate: too few faces found "
              f"(final {len(fa)}, plate {len(pa)})")
        return 0

    f, p = float(np.median(fa)), float(np.median(pa))
    ratio = f / p
    err = abs(ratio - 1.0)
    ok = err <= tol
    print(f"  plate face aspect  {p:.3f}   (n={len(pa)})")
    print(f"  final face aspect  {f:.3f}   (n={len(fa)})")
    print(f"  he is rendered at {100*ratio:.1f}% of his true width "
          f"(tolerance {100*tol:.0f}%)")
    if ok:
        print("PASS avatar_shape_gate")
        return 0
    which = "squeezed" if ratio < 1 else "stretched"
    print(f"FAIL avatar_shape_gate: the presenter is {which} — "
          f"a placement is not preserving aspect ratio")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
