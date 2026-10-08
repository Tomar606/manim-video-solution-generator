"""A frame of a biology video before the presenter clip exists.

    python tools/mock_bio_frame.py <chip.png> "<caption>" <out.png> [top]

Plate, chip at its band position, caption at the top, and a marker for where the
presenter will be keyed in. No avatar clip has been shot for this question yet,
so the bottom band is drawn as a reserved zone rather than faked with a stand-in
from another video — a borrowed presenter would make the composition look
settled when it has not been checked against the real one.
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
W, H, BAND_TOP, FLOOR = 1080, 1920, 380, 1344


def main():
    chip, caption, out = sys.argv[1:4]
    top = int(sys.argv[4]) if len(sys.argv) > 4 else BAND_TOP
    f = Image.open(ROOT / "assets/backgrounds/biology.png").convert("RGBA").resize((W, H))
    c = Image.open(chip).convert("RGBA")
    f.alpha_composite(c, (0, top))

    d = ImageDraw.Draw(f)
    if caption != "-":
        fnt = ImageFont.truetype(str(ROOT / "assets/fonts/Khand-Bold.ttf"), 46)
        for i, ln in enumerate(caption.split("|")):
            w = d.textbbox((0, 0), ln, font=fnt)[2]
            d.text(((W - w) / 2, 60 + i * 58), ln, font=fnt, fill=(255, 255, 255),
                   stroke_width=4, stroke_fill=(0, 0, 0))

    d.line([(0, FLOOR), (W, FLOOR)], fill=(255, 255, 255, 60), width=2)
    small = ImageFont.truetype(str(ROOT / "assets/fonts/Khand-Medium.ttf"), 30)
    t = "प्रस्तुतकर्ता का क्षेत्र  ·  presenter keys in here"
    w = d.textbbox((0, 0), t, font=small)[2]
    d.text(((W - w) / 2, FLOOR + 26), t, font=small, fill=(255, 255, 255, 90))
    f.convert("RGB").save(out)
    print(out)


if __name__ == "__main__":
    main()
