#!/usr/bin/env python3
"""whiten.py — make a rendered page look like the ORIGINAL reference SCAN.

No API call: this is pure local post-processing.

The reference photo (hand-anchor-full.jpg) is a hard, high-contrast phone/scanner capture:
  * paper is BLOWN OUT to pure white -- ~82% of the page is >= 250 luminance, and the median
    pixel is exactly 255. There is no cream, no grain, no vignette left in it.
  * the ink is dark and only mildly blue: midtone strokes average about (99, 99, 106), i.e. the
    harsh exposure has desaturated the ballpoint blue and crushed the stroke cores to near-black.

Our renders are the opposite: warm off-white paper around 224, soft shading, and a livelier,
more saturated blue. This script closes that gap in four steps:

  1. FLAT-FIELD  -- estimate the paper level per-pixel (max-filter + heavy blur on a downscaled
     copy) and divide it out, so shading/vignette/grain disappear and the sheet is evenly lit.
  2. WHITE CUT   -- everything above `white_cut` is snapped to pure 255 white, reproducing the
     blown-out look. Tuned so the >=250 coverage lands near the reference's 82%.
  3. BLACK LIFT + GAMMA -- pull the stroke cores down toward black so the pen stays crisp and
     dark against the flat white instead of turning grey.
  4. DESATURATE  -- ease the blue back toward the reference's muted, slightly grey blue.

Usage:
  python whiten.py                       # every page in generated/clean/ -> generated/whitened/
  python whiten.py page-01 page-01-v1    # named pages only
  python whiten.py --compare             # also print the colour stats vs the reference
"""
from __future__ import annotations
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

HERE = Path(__file__).resolve().parent
SRC_DIR = HERE / "generated" / "clean"
OUT_DIR = HERE / "generated" / "whitened"
REFERENCE = HERE / "hand-anchor-full.jpg"

# --- tuning ---------------------------------------------------------------
WHITE_CUT = 0.86   # normalised paper level at/above which a pixel becomes pure white
BLACK_LIFT = 0.10  # normalised level mapped to pure black (deepens the stroke cores)
GAMMA = 1.15       # >1 darkens the midtones -> crisper strokes
SATURATION = 0.72  # <1 mutes the blue toward the reference's greyer ink
BG_DOWNSCALE = 8   # background estimated on a 1/8 copy (fast, and ignores stroke detail)
BG_MAX_RADIUS = 3  # max-filter radius on the downscaled copy: must exceed stroke thickness
BG_BLUR = 12       # blur radius on the downscaled copy -> smooth illumination field


def whiten(img: Image.Image) -> Image.Image:
    rgb = np.asarray(img.convert("RGB")).astype(np.float32) / 255.0
    h, w = rgb.shape[:2]

    # 1. FLAT-FIELD: paper level per pixel, estimated small then blown back up.
    small = img.convert("L").resize((max(1, w // BG_DOWNSCALE), max(1, h // BG_DOWNSCALE)),
                                    Image.BILINEAR)
    small = small.filter(ImageFilter.MaxFilter(BG_MAX_RADIUS * 2 + 1))   # erase the ink
    small = small.filter(ImageFilter.GaussianBlur(BG_BLUR))              # smooth illumination
    bg = np.asarray(small.resize((w, h), Image.BICUBIC)).astype(np.float32) / 255.0
    bg = np.clip(bg, 0.35, 1.0)[..., None]
    flat = np.clip(rgb / bg, 0.0, 1.0)

    # 2+3. Levels: black lift -> white cut, with a darkening gamma between them.
    lo, hi = BLACK_LIFT, WHITE_CUT
    lev = np.clip((flat - lo) / (hi - lo), 0.0, 1.0) ** GAMMA

    # 4. Desaturate toward the reference's muted ink (paper is already neutral after flat-fielding).
    grey = lev @ np.array([0.299, 0.587, 0.114], dtype=np.float32)
    lev = np.clip(grey[..., None] + (lev - grey[..., None]) * SATURATION, 0.0, 1.0)

    return Image.fromarray((lev * 255.0 + 0.5).astype(np.uint8), "RGB")


def stats(path: Path, label: str) -> None:
    a = np.asarray(Image.open(path).convert("RGB")).astype(np.float32)
    lum = a.mean(2)
    mid = (lum > 40) & (lum < 170)
    print(f"  {label:<28} paper(p80+)={a[lum >= np.percentile(lum, 80)].mean(0).round(1)} "
          f"median={np.median(lum):5.1f} pure-white={float((lum >= 250).mean()):.3f} "
          f"ink-mid={a[mid].mean(0).round(1) if mid.any() else '-'}")


def main() -> int:
    argv = [a for a in sys.argv[1:] if not a.startswith("--")]
    compare = "--compare" in sys.argv
    pages = argv or sorted(p.stem for p in SRC_DIR.glob("*.png"))
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for page_id in pages:
        src = SRC_DIR / f"{page_id}.png"
        if not src.exists():
            print(f"[{page_id}] SKIP: no {src}", file=sys.stderr)
            continue
        out = OUT_DIR / f"{page_id}.jpg"
        whiten(Image.open(src)).save(out, format="JPEG", quality=95)
        print(f"[{page_id}] -> {out.relative_to(HERE)}")

    if compare:
        print("\ncolour check:")
        stats(REFERENCE, "REFERENCE (original)")
        for page_id in pages:
            if (SRC_DIR / f"{page_id}.png").exists():
                stats(SRC_DIR / f"{page_id}.png", f"{page_id} before")
                stats(OUT_DIR / f"{page_id}.jpg", f"{page_id} whitened")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
