#!/usr/bin/env python3
"""Build anchor-combined.png — ONE reference image that replaces TWO.

    python make_anchor.py            # writes Hindi Hand/anchor-combined.png

Why this exists (cost): every billed page call used to ship FOUR input images —
blank paper, a handwriting close-up, the page blueprint, and a whole already-drawn
page. The close-up and the already-drawn page carry OVERLAPPING information (one
says how a stroke looks, the other says how big it is and how dark the ink is), so
they are merged onto a single sheet and the call drops from four images to three.

Layout of the result (1024x1536, the same shape as a real page):

    top band   (0..616)      hand-anchor.jpg, MAGNIFIED — stroke texture
    ---- divider ----
    bottom band (616..1536)  a crop of style-anchor.png at TRUE PAGE SCALE

The bottom crop is taken at native resolution and full page width, never resized,
because that is what makes it a valid size reference: letter height relative to the
1024px page width is preserved exactly. The crop deliberately starts BELOW the
style anchor's header band so the chapter title in it can never be copied.
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
HAND_REF = HERE / "hand-anchor.jpg"
STYLE_REF = HERE / "style-anchor.png"
OUT = HERE / "anchor-combined.png"

W, H = 1024, 1536
SPLIT = 616                 # top band height: the magnified stroke close-up
STYLE_TOP = 300             # first row of the style anchor to keep (clears the header band)
PAPER_TINT = (253, 252, 248)


def main() -> int:
    canvas = Image.new("RGB", (W, H), PAPER_TINT)

    # --- top band: the stroke close-up, scaled to fit, never cropped ---------
    with Image.open(HAND_REF) as hand:
        hand = hand.convert("RGB")
        s = min(W / hand.width, SPLIT / hand.height)
        hw, hh = round(hand.width * s), round(hand.height * s)
        canvas.paste(hand.resize((hw, hh), Image.LANCZOS),
                     ((W - hw) // 2, (SPLIT - hh) // 2))

    # --- bottom band: a true-scale crop of a finished page -------------------
    with Image.open(STYLE_REF) as style:
        style = style.convert("RGB")
        if style.width != W:
            # only ever scale to match page WIDTH, so relative letter size survives
            s = W / style.width
            style = style.resize((W, round(style.height * s)), Image.LANCZOS)
        band = H - SPLIT
        top = min(STYLE_TOP, max(0, style.height - band))
        canvas.paste(style.crop((0, top, W, min(style.height, top + band))), (0, SPLIT))

    # --- divider: an unmistakable seam, so the two halves are never read as one page ---
    d = ImageDraw.Draw(canvas)
    d.rectangle([0, SPLIT - 6, W, SPLIT + 2], fill=(120, 120, 120))

    canvas.save(OUT, format="PNG")
    print(f"wrote {OUT.name}  {canvas.size}  {OUT.stat().st_size // 1024} KB")
    print("  top band   : hand-anchor.jpg (magnified strokes)")
    print("  bottom band: style-anchor.png rows "
          f"{STYLE_TOP}..{STYLE_TOP + (H - SPLIT)} at true page scale")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
