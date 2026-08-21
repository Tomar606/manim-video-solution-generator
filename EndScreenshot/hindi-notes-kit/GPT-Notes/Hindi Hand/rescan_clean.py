#!/usr/bin/env python3
"""Re-apply scan_effect to already-rendered CLEAN pages — NO API call, NO cost.

gen_final.py saves the clean (pre-scan) render to generated/clean/<id>.png. Whenever
scan_effect.py is re-tuned, run this to regenerate generated/<id>.jpg from those clean
PNGs instead of paying for a fresh image render. Uses the SAME deterministic per-page
seed as gen_final so a page's wear pattern stays stable.

Usage:
  python rescan_clean.py                 # rescans every clean/*.png (per-page varied look)
  python rescan_clean.py page-01 dia-01  # only these ids
  SCAN_UNIFORM=1 python rescan_clean.py  # UNIFORM: identical scan on EVERY page

UNIFORM mode (SCAN_UNIFORM=1): every page uses ONE fixed seed, so the tone, tilt, lighting,
vignette, binding shadow and grain are identical on every page (looks like the whole notebook
was scanned in one pass on one machine); wear artifacts (foxing/crease) are turned off so no page
carries a spot another lacks. Without it, each page keeps its own deterministic per-page variation.
"""
from __future__ import annotations
import os, sys, zlib
from pathlib import Path
from PIL import Image
from scan_effect import scan_effect

HERE = Path(__file__).resolve().parent
CHAPTER = "Bio Ch1 SRFP"
CLEAN_DIR = HERE / "generated" / "clean"
OUT_DIR = HERE / "generated"
WEAR = 0.5
UNIFORM = bool(os.environ.get("SCAN_UNIFORM"))
UNIFORM_SEED = zlib.crc32(b"Bio Ch1 SRFP|uniform-scan")   # one seed shared by all pages


def main() -> int:
    if not CLEAN_DIR.exists():
        print(f"no clean dir at {CLEAN_DIR} — render once with gen_final.py first", file=sys.stderr)
        return 1
    ids = sys.argv[1:] or sorted(p.stem for p in CLEAN_DIR.glob("*.png"))
    if UNIFORM:
        print("[uniform] one fixed seed + wear off — identical scan on every page")
    for page_id in ids:
        src = CLEAN_DIR / f"{page_id}.png"
        if not src.exists():
            print(f"[{page_id}] SKIP: no clean/{page_id}.png", file=sys.stderr); continue
        # UNIFORM: same seed for every page (identical treatment) + wear off (no per-page spots).
        seed = UNIFORM_SEED if UNIFORM else zlib.crc32(f"{CHAPTER}|{page_id}".encode())
        wear = 0.0 if UNIFORM else WEAR
        final = scan_effect(Image.open(src), seed=seed, wear_boost=wear)
        final.save(OUT_DIR / f"{page_id}.jpg", format="JPEG", quality=95)
        print(f"[{page_id}] rescanned -> generated/{page_id}.jpg (seed={seed}{', uniform' if UNIFORM else ''})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
