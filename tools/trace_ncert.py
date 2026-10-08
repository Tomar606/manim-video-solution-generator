"""Trace an NCERT figure scan into clean SVG layers.

    python tools/trace_ncert.py <scan.png> <out.svg>

The scans carry the book's leader lines drawn straight across the figure, so a
naive trace of the black linework reproduces the leaders as if they were anatomy.
Two passes avoid that:

  * **fills** come from COLOUR regions, where a thin black leader simply is not
    present;
  * **linework** is traced only after pixels belonging to long straight runs are
    removed. A leader is a continuous horizontal or vertical run of dark pixels
    tens of pixels long; the anatomy is curved, so no run along it survives more
    than a few pixels in one direction.

potrace does the curve fitting — hand-fitting beziers off a screenshot is how a
traced figure ends up "close enough" and visibly not the book's shape.
"""
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

RUN = 46          # a dark run this long in one direction is a leader, not anatomy
CLOSE = 5         # bridge the slots the leaders cut through the colour fills


def strip_leaders(dark: np.ndarray, axes=(1, 0), run: int = RUN) -> np.ndarray:
    """Drop pixels that sit in a long straight run along each axis in `axes`.

    Pass axes=(1,) where the figure has near-VERTICAL strokes of its own. NCERT
    leader lines run horizontally to the labels, so the vertical pass adds
    nothing there -- but it deletes any stroke that runs straight down for RUN
    pixels, which is exactly what the lower half of an integument arc does. That
    is why those arcs stopped half way down the ovule.
    """
    keep = dark.copy()
    for axis in axes:
        d = dark if axis == 1 else dark.T
        k = keep if axis == 1 else keep.T
        for i in range(d.shape[0]):
            row = d[i]
            if not row.any():
                continue
            idx = np.flatnonzero(np.diff(np.r_[0, row.view(np.int8), 0]))
            for a, b in zip(idx[::2], idx[1::2]):
                if b - a >= run:
                    k[i, a:b] = False
    return keep


def _shift(a, dy, dx):
    out = np.zeros_like(a)
    ys = slice(max(0, dy), a.shape[0] + min(0, dy))
    xs = slice(max(0, dx), a.shape[1] + min(0, dx))
    yt = slice(max(0, -dy), a.shape[0] + min(0, -dy))
    xt = slice(max(0, -dx), a.shape[1] + min(0, -dx))
    out[yt, xt] = a[ys, xs]
    return out


def _morph(a, k, grow):
    """Binary dilate (grow=True) or erode, with a square kernel of side 2k+1."""
    out = a.copy()
    for dy in range(-k, k + 1):
        for dx in range(-k, k + 1):
            out = (out | _shift(a, dy, dx)) if grow else (out & _shift(a, dy, dx))
    return out


def close(a, k=CLOSE):
    """Dilate then erode: heals the leader slots without moving the outline."""
    return _morph(_morph(a, k, True), k, False)


def main_body(a):
    """Keep only the largest connected blob.

    NCERT prints an orientation arrow beside the embryo sac; it is the same ink
    as the cells, so it traces as anatomy floating in space. Anything not joined
    to the figure is not part of the figure."""
    seen = np.zeros_like(a)
    best = np.zeros_like(a)
    ys, xs = np.nonzero(a)
    for y0, x0 in zip(ys[::400], xs[::400]):
        if seen[y0, x0]:
            continue
        blob = np.zeros_like(a)
        blob[y0, x0] = True
        while True:
            g = _morph(blob, 1, True) & a
            if g.sum() == blob.sum():
                break
            blob = g
        seen |= blob
        if blob.sum() > best.sum():
            best = blob
    return best if best.any() else a


def fill_holes(a):
    """Solidify a region. NCERT stipples a tissue with dots to shade it; each dot
    is a hole in the colour mask, and tracing them verbatim turns a smooth flank
    into a chequerboard. Anything enclosed by the region IS the region."""
    free = np.zeros_like(a)
    free[0, :] = free[-1, :] = True
    free[:, 0] = free[:, -1] = True
    free &= ~a
    while True:
        grown = (_morph(free, 1, True)) & ~a
        if grown.sum() == free.sum():
            break
        free = grown
    return ~free


def trace(mask: np.ndarray, td: str, name: str) -> str:
    """One binary mask -> one SVG path payload, via potrace."""
    pbm = Path(td) / f"{name}.pbm"
    svg = Path(td) / f"{name}.svg"
    Image.fromarray(np.where(mask, 0, 255).astype(np.uint8)).save(pbm)
    subprocess.run(["potrace", str(pbm), "-s", "-o", str(svg),
                    "--turdsize", "120", "--alphamax", "1.2", "--opttolerance", "0.3"],
                   check=True)
    body = svg.read_text()
    d = " ".join(re.findall(r'\sd="([^"]+)"', body))
    keep = []
    for sub in ("M" + x for x in d.split("M") if x.strip()):
        nums = [float(v) for v in re.findall(r"-?\d+(?:\.\d+)?", sub)]
        xs, ys = nums[0::2], nums[1::2]
        if not xs:
            continue
        w_, h_ = max(xs) - min(xs), max(ys) - min(ys)
        thin, long_ = min(w_, h_), max(w_, h_)
        # A leader fragment is a hairline: very thin and comparatively long.
        # Anatomy is never that. This drops the pieces of leader that survived
        # the run-length pass because the figure's own outline broke them up.
        if thin < 60 and long_ > 300:
            continue
        keep.append(sub)
    return '<path d="' + " ".join(keep) + '"/>'  


def main():
    src, out = sys.argv[1], sys.argv[2]
    im = np.asarray(Image.open(src).convert("RGB")).astype(int)
    h, w = im.shape[:2]
    r, g, b = im[..., 0], im[..., 1], im[..., 2]
    lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
    white = (r > 235) & (g > 235) & (b > 235)
    dark = lum < 110
    green = g - (r + b) / 2
    pink = (r - g) > 18
    # A leader line is grey, and grey survives every threshold that is only about
    # lightness -- which is how the first pass grew pale ghosts of the leaders
    # out to the edge of the frame. The anatomy is always COLOURED, so chroma
    # tells them apart where luminance cannot.
    chroma = im.max(axis=2) - im.min(axis=2)
    colour = chroma > 22

    # Fills are CLOSED first. A leader crossing the figure removes a 3-4px stripe
    # of colour, and tracing that verbatim leaves white slashes through the
    # anatomy -- visible straight away on the first attempt.
    layers = {
        "body":   fill_holes(close((~white) & (~dark) & colour, 7)),
        # NO threshold splits the body. The greenness histogram looks bimodal,
        # but the two modes are the two ends of a left-to-right SHADING GRADIENT,
        # not two tissues -- thresholding it cut the ovule vertically down the
        # middle, which is nothing the book contains. The shading is reproduced
        # as a gradient fill instead, which is what it is.
        # The embryo sac is the one genuinely distinct fill in the figure: the
        # greenest AND the darkest. Tightening this to match the (mistaken)
        # body split shrank it to 0.7% and it vanished into the gradient.
        "core":   fill_holes(close((~white) & (~dark) & colour & (green > 26)
                                   & (lum < 205))),
        "cells":  close((~white) & (~dark) & colour & pink),
        "line":   strip_leaders(dark),
    }
    keep = main_body(layers["body"])
    for k in layers:
        if k != "line":
            layers[k] = layers[k] & keep
        else:
            layers[k] = layers[k] & _morph(keep, 3, True)

    parts = []
    with tempfile.TemporaryDirectory() as td:
        for name, mask in layers.items():
            if mask.sum() < 400:
                continue
            parts.append((name, trace(mask, td, name), int(mask.sum())))

    fill = {"body": "url(#tissue)", "core": "url(#core)",
            "cells": "#F2A0A0", "line": "#1A1A1A"}
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
           f'width="{w}" height="{h}">',
           '  <defs>',
           '    <linearGradient id="tissue" x1="0" y1="0" x2="1" y2="0">',
           '      <stop offset="0" stop-color="#CBE08A"/>',
           '      <stop offset="0.55" stop-color="#E6EFAE"/>',
           '      <stop offset="1" stop-color="#F4F3CE"/>',
           '    </linearGradient>',
           '    <linearGradient id="core" x1="0" y1="0" x2="1" y2="0">',
           '      <stop offset="0" stop-color="#8FC63D"/>',
           '      <stop offset="1" stop-color="#B8DC6B"/>',
           '    </linearGradient>',
           '  </defs>',
           f'  <g transform="translate(0,{h}) scale(0.1,-0.1)">']
    for name, paths, n in parts:
        svg.append(f'    <g id="{name}" fill="{fill[name]}">')
        svg.append("      " + paths.replace("\n", "\n      "))
        svg.append("    </g>")
    svg += ["  </g>", "</svg>"]
    Path(out).write_text("\n".join(svg))
    print(f"  {out}")
    for name, _, n in parts:
        print(f"    {name:6s} {n/(h*w)*100:5.1f}% of the frame")


if __name__ == "__main__":
    main()
