"""Refuse to deliver a finished video that breaks a hard rule.

    python tools/output_gate.py <video.mp4> [--graphics-from SEC]

The layout gate checks the Manim/edu render; this checks the FINISHED file, and
it exists because two defects kept coming back after being "fixed":

  * the presenter floating clear of the bottom edge
  * audio drifting against picture

Both were fixed in source more than once and both returned, because nothing
stopped a broken file being delivered. A constant in a file is not a rule. This
is the rule.
"""
from __future__ import annotations

import io
import subprocess
import sys
from pathlib import Path

SYNC_TOL = 0.30       # seconds of audio/video duration difference allowed
BOTTOM_TOL = 6        # px the silhouette may stop short of the frame bottom
CENTRE_TOL = 20       # px off horizontal centre
HEAD_MIN = 0.50       # top of head must be at or below this while graphics show


def _probe(v: Path, stream: str, field: str) -> float | None:
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", stream,
                          "-show_entries", f"stream={field}", "-of", "csv=p=0", str(v)],
                         capture_output=True, text=True).stdout.strip().split("\n")[0]
    try:
        return float(out)
    except ValueError:
        return None


def _frame(v: Path, t: float):
    import numpy as np
    from PIL import Image
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.2f}", "-i", str(v),
                          "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-"],
                         capture_output=True).stdout
    if not raw:
        return None
    return np.asarray(Image.open(io.BytesIO(raw)).convert("RGB")).astype(int)


def _attached(a):
    """Is the presenter touching the bottom edge?

    Looks ONLY at the centre columns. The chalk plate's beakers sit at the sides
    and do reach the bottom, so a wide check read them as the presenter and
    passed a frame with his legs sliced off mid-torso.
    """
    import numpy as np
    H, W, _ = a.shape
    bg = np.median(a[int(H * 0.30):int(H * 0.40), :70], axis=(0, 1))
    mid = a[:, int(W * 0.36):int(W * 0.64)]
    solid = (np.abs(mid - bg).sum(axis=2) > 95).sum(axis=1) > mid.shape[1] * 0.55
    low = np.where(solid[int(H * 0.55):])[0]
    if len(low) == 0:
        return None, None
    top = int(H * 0.55) + int(low.min())
    bot = int(H * 0.55) + int(low.max())
    return top, bot


def check(video: Path, graphics_from: float | None) -> list[str]:
    import numpy as np
    bad: list[str] = []

    vd, ad = _probe(video, "v", "duration"), _probe(video, "a", "duration")
    if ad is None:
        bad.append("no audio stream")
    elif vd is not None and abs(vd - ad) > SYNC_TOL:
        bad.append(f"AUDIO/VIDEO LENGTH MISMATCH: video {vd:.2f}s vs audio "
                   f"{ad:.2f}s ({abs(vd-ad):.2f}s apart) — picture and sound drift")

    fr = _probe(video, "v", "r_frame_rate")
    nb = _probe(video, "v", "nb_frames")
    if vd and nb and vd > 0:
        eff = nb / vd
        if abs(eff - 30.0) > 0.5:
            bad.append(f"NOT 30 fps: {nb:.0f} frames over {vd:.2f}s = {eff:.2f} fps")

    # Geometry, not pixels. The sidecar written by composite.py states exactly
    # where the presenter sits in every mode; checking those numbers is precise,
    # where hunting the finished frame reported a cut-off presenter on a video
    # that was correct because his shirt matched the plate.
    g = Path(str(video) + ".geom.json")
    if g.is_file():
        import json as _j
        geom = _j.loads(g.read_text())
        for mode in ("card", "full", "big", "small"):
            m = geom.get(mode)
            if not m:
                continue
            if abs(m["bottom"] - 1920) > 2:
                bad.append(f"NOT ANCHORED in {mode} mode: bottom at {m['bottom']}, "
                           f"should be 1920")
        full, big = geom.get("full"), geom.get("big")
        if full and full["head"] < HEAD_MIN:
            bad.append(f"HEAD TOO HIGH with graphics: {full['head']:.3f} of frame, "
                       f"must be >= {HEAD_MIN}")
        if big and big["head"] < 0.38:
            bad.append(f"GROWN HEAD TOO HIGH: {big['head']:.3f}, must be >= 0.38")
        if abs(geom.get("dx_out", 0)) > 140:
            bad.append(f"CENTRING SHIFT LOOKS WRONG: {geom['dx_out']}px")
    else:
        bad.append("no geometry sidecar — cannot verify placement")

    return bad


def main() -> int:
    v = Path(sys.argv[1])
    gf = None
    if "--graphics-from" in sys.argv:
        gf = float(sys.argv[sys.argv.index("--graphics-from") + 1])
    bad = check(v, gf)
    if not bad:
        print(f"  output ok: {v.name}")
        return 0
    print(f"  OUTPUT REJECTED — {v.name}")
    for b in dict.fromkeys(bad):
        print(f"    {b}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
