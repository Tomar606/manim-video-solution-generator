"""Refuse a video whose Veo clips still carry Flow's burned-in marker.

    python tools/veo_logo_gate.py projects/<slug>/clips_part1.json [--final out.mp4]

Flow stamps a small four-pointed sparkle into every clip it renders, AFTER
generation, so no prompt prevents it (memory: flow-burns-an-ai-marker). It is
covered per clip by tools/prep_veo_clip.py — and "covered" was until now a thing
somebody remembered to do and nobody checked. This checks it.

HOW A BURNED-IN MARK IS TOLD FROM THE PICTURE
---------------------------------------------
It is BRIGHT, SMALL, STATIC and sits in the margin. So: take the pixel-wise
MINIMUM across frames spread through the clip — anything the picture moves
through goes dark, and only what never moves stays bright — subtract a blurred
copy of that minimum to leave what is brighter than its own surroundings, and
keep blobs in the outer margin. A lamp in the middle of the room is not in the
margin; the clip's own bright corner sky is not compact.

WHERE THIS DETECTION FAILS, and why the box is not found by search. Flow's mark
is semi-TRANSPARENT. Over a still wall the minimum keeps it and it stands out;
over constantly moving foliage the darker leaves show through it on some frame
or other, so the minimum goes dark straight through the mark and it vanishes
from the min-image. On the sunlit-leaves clip the whole corner measured 2.6 grey
levels while the sparkle was plainly visible by eye at 2s and at 6s. That is why
this gate checks a box that was RECORDED when the clip was prepared rather than
hunting for one: the position is known from the clip's shape, and a search
would report "clean" on exactly the clips that are not.

Every clip listed is checked, and the RAW download is checked too when it is on
disk: the raw must show the mark and the prepared clip must not. That way a
prep step that silently did nothing fails here rather than shipping.
"""
from __future__ import annotations

import argparse
import io
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
MARGIN = 0.14          # a watermark lives in the outer band, not the middle
BRIGHT = 16            # grey levels above its own surroundings
MIN_AREA = 120         # px in the min-image; smaller is noise
MAX_AREA = 6000        # bigger than this is scenery, not a mark
SIDE = (18, 130)       # a mark's bounding box, px
ASPECT = (0.55, 1.8)   # and it is roughly as wide as it is tall
SAMPLES = 9


def frames(clip: Path, n: int = SAMPLES) -> list[np.ndarray]:
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                "-of", "csv=p=0", str(clip)], capture_output=True,
                               text=True).stdout or 0)
    out = []
    for i in range(n):
        t = dur * (0.06 + 0.88 * i / max(1, n - 1))
        raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.2f}", "-i", str(clip),
                              "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-"],
                             capture_output=True).stdout
        if raw:
            out.append(np.asarray(Image.open(io.BytesIO(raw)).convert("L")).astype(float))
    return out


def patch_stats(clip: Path, box) -> tuple[float, float]:
    """(contrast inside the marker box, contrast of the ring around it).

    Measured on the pixel-wise MINIMUM across frames, so only what never moves
    counts. CONTRAST, not brightness: the box sits wherever Flow put its
    sparkle, which may be over a bright sofa arm or a dark doorway, and
    brightness there says more about the furniture than about the mark. What a
    surviving sparkle always is, is a hard-edged blob — high contrast inside a
    small box. What a covered one always is, is SMOOTH, because the cover
    interpolates the cloth or wall across it.
    """
    fs = frames(clip)
    if len(fs) < 3:
        return (0.0, 0.0)
    mn = np.min(np.stack(fs), axis=0)
    h, w = mn.shape
    x, y, bw, bh = box
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(w, x + bw), min(h, y + bh)
    if x1 - x0 < 4 or y1 - y0 < 4:
        return (0.0, 0.0)
    inner = mn[y0:y1, x0:x1].ravel()
    m = 16
    rx0, ry0 = max(0, x0 - m), max(0, y0 - m)
    rx1, ry1 = min(w, x1 + m), min(h, y1 + m)
    ring = np.concatenate([mn[ry0:y0, rx0:rx1].ravel(), mn[y1:ry1, rx0:rx1].ravel(),
                           mn[y0:y1, rx0:x0].ravel(), mn[y0:y1, x1:rx1].ravel()])
    if not ring.size:
        return (0.0, 0.0)
    span = lambda v: float(np.percentile(v, 95) - np.percentile(v, 30))
    return (span(inner), span(ring))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("clips")
    ap.add_argument("--max-contrast", type=float, default=18.0,
                    help="grey levels of contrast the covered box may still carry")
    ap.add_argument("--min-drop", type=float, default=0.35,
                    help="share of the raw's box contrast a real cover removes")
    a = ap.parse_args()
    cj = Path(a.clips)
    if not cj.is_file():
        print(f"  no clips file: {cj}")
        return 0
    proj = cj.parent
    clips = json.loads(cj.read_text(encoding="utf-8"))
    bad, ok = [], 0
    for c in clips:
        name = Path(c["src"]).name
        src = proj / c["src"]
        if not src.is_file():
            bad.append(f"{name}: missing")
            continue
        box = c.get("mark")
        if not box:
            bad.append(f"{name}: no marker box recorded — this clip never went "
                       f"through tools/prep_veo_clip.py, so Flow's sparkle is "
                       f"still on it")
            continue
        inside, ring = patch_stats(src, box)
        # RELATIVE TO THE PROJECT, like `src` — not to the working directory.
        # Resolved against the CWD it never existed, so the raw comparison
        # below has been silently skipped for every clip since it was written,
        # and the gate has been deciding on absolute contrast alone.
        raw = Path(c.get("raw", ""))
        if raw.parts and not raw.is_absolute():
            raw = proj / raw
        raw_inside = patch_stats(raw, box)[0] if raw.is_file() else None
        limit = max(a.max_contrast, 0.6 * ring)
        # A REAL EDGE THROUGH THE BOX IS NOT A WATERMARK. Where Flow puts its
        # sparkle is not always flat: on one clip the box straddled the join
        # between a blue cloth and the bench, on another the presenter's
        # shoulder against a green wall. Both read as high contrast whether or
        # not the mark is there, and both were reported as "still there" with
        # the sparkle demonstrably gone.
        #
        # The raw download settles it. An edge is in BOTH the raw and the
        # covered clip, so it cannot explain a large DROP; a removed sparkle
        # can, and does. So a box that lost a good share of its contrast
        # against the raw has been cleaned, whatever its absolute level.
        if inside > limit and raw_inside and raw_inside > 0:
            drop = 1.0 - inside / raw_inside
            if drop >= a.min_drop:
                print(f"  {name}: covered — the box lost {drop:.0%} of its contrast "
                      f"against the raw ({raw_inside:.0f} -> {inside:.0f}); what is "
                      f"left is picture, not the mark")
                ok += 1
                continue
        if inside > limit:
            bad.append(f"{name}: the marker box at {tuple(box)} still carries "
                       f"{inside:.0f} grey levels of contrast (limit {limit:.0f}) "
                       f"— Flow's mark is still there; re-run prep with the "
                       f"right --mark")
            continue
        if raw_inside is not None and raw_inside <= limit:
            print(f"  {name}: box is smooth ({inside:.0f}), but the RAW download "
                  f"was smooth there too ({raw_inside:.0f}) — check where Flow "
                  f"put the sparkle in this clip")
        else:
            print(f"  {name}: covered ({inside:.0f} of {limit:.0f} allowed"
                  + (f", raw was {raw_inside:.0f})" if raw_inside is not None else ")"))
        ok += 1
    if bad:
        print("  VEO LOGO GATE FAILED")
        for b in bad:
            print(f"    {b}")
        return 1
    print(f"  veo logo ok: {ok} clip(s), Flow's mark covered on each")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
