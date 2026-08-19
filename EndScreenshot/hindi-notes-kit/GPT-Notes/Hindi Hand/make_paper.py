#!/usr/bin/env python3
"""Build the BLANK base page for the Hindi handwriting notes (paper-hindi.png).

Mirrors the page furniture of hand-anchor.jpg (the real Hindi notebook page):
  * plain, very slightly warm white paper, NO body ruling at all
  * a DOUBLE VERTICAL margin rule down the LEFT edge (two thin dark lines, close together)
  * a DOUBLE HORIZONTAL rule across the TOP, making a narrow header band for the chapter title
Nothing else -- no spiral, no logo, no Date/Page box.

Output: paper-hindi.png (1024x1536, the gpt-image-1 portrait size).
"""
from __future__ import annotations
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

W, H = 1024, 1536
HERE = Path(__file__).resolve().parent
OUT = HERE / "paper-hindi.png"

rng = random.Random(20260812)


def jitter_line(d, x0, y0, x1, y1, colour, width, wobble=1.2, segs=24):
    """A hand/press-printed line that is straight in feel but not machine-perfect."""
    px, py = x0, y0
    for i in range(1, segs + 1):
        t = i / segs
        nx = x0 + (x1 - x0) * t + rng.uniform(-wobble, wobble)
        ny = y0 + (y1 - y0) * t + rng.uniform(-wobble, wobble)
        d.line([(px, py), (nx, ny)], fill=colour, width=width)
        px, py = nx, ny


def main() -> None:
    paper = Image.new("RGB", (W, H), (250, 249, 245))
    # gentle paper grain + a soft vignette-ish shading so it photographs like real paper
    noise = Image.new("L", (W // 2, H // 2))
    noise.putdata([rng.randint(238, 255) for _ in range(noise.width * noise.height)])
    noise = noise.resize((W, H), Image.BILINEAR).filter(ImageFilter.GaussianBlur(0.6))
    paper = Image.composite(paper, Image.new("RGB", (W, H), (243, 241, 236)),
                            noise.point(lambda v: 255 if v > 247 else 0))
    paper = paper.filter(ImageFilter.GaussianBlur(0.3))

    d = ImageDraw.Draw(paper)
    ink = (58, 56, 58)

    # LEFT double vertical margin rule
    x1 = int(W * 0.052)
    x2 = x1 + 11
    jitter_line(d, x1, 0, x1 + 2, H, ink, 3, wobble=0.8, segs=40)
    jitter_line(d, x2, 0, x2 + 2, H, ink, 2, wobble=0.8, segs=40)

    # TOP double horizontal rule -> narrow header band for the chapter title
    y1 = int(H * 0.083)
    y2 = y1 + 12
    jitter_line(d, 0, y1, W, y1 + 2, ink, 3, wobble=0.7, segs=40)
    jitter_line(d, 0, y2, W, y2 + 1, ink, 2, wobble=0.7, segs=40)

    paper.save(OUT, format="PNG")
    print(f"wrote {OUT} ({W}x{H})")


if __name__ == "__main__":
    main()
