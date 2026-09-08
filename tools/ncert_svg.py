"""Rebuild an NCERT figure as clean vector art, using the scan only for geometry.

    python tools/ncert_svg.py <scan.png> <out.svg>

`trace_ncert.py` traced the scan, artefacts and all: the outline came from the
printed ink, so it inherited every ragged pixel, and line weight varied wherever
the print was heavy. That reads as a photocopy, not as a diagram.

This does it the other way round:

  * the outline is NOT traced. Each region is traced as an AREA and then the same
    path is both filled and STROKED, so every border is exactly one width by
    construction and no ragged ink is reproduced;
  * potrace runs with heavy smoothing, because the target is the shape the
    illustrator drew, not the shape the scanner recorded;
  * the mask is opened before tracing, which removes the stipple speckle and the
    scanner's edge noise without moving the boundary.
"""
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from scipy import ndimage as nd

from trace_ncert import _morph, _shift, close, fill_holes, main_body, strip_leaders  # noqa
from vector_figure import ellipse_of, outline  # noqa

STROKE = 3.2       # every border, one weight, like the book's pen


def smooth(mask, k=2):
    """Open then close: speckle and hairline noise go, the boundary stays."""
    return close(_morph(_morph(mask, k, False), k, True), 3)


def bridge(mask, gap=9):
    """Heal the cut a leader strip makes across a near-vertical stroke.

    strip_leaders deletes the WHOLE horizontal run, and where an integument arc
    crosses a leader the arc's own pixels are part of that run -- so the arc is
    cut in two. Below the cut it is a short fragment, which potrace's turdsize
    either drops (the arcs ended half way down the figure) or keeps as a speck
    floating on the tissue (two of those shipped).

    Restore any deleted pixel that has ink BOTH above and below it: true across
    the cut in an arc, false along the rest of the leader, which has ink only to
    its left and right. Filtering the fragments afterwards cannot do this -- a
    leader stub is just as "long" as an arc, and keeping it put horizontal ticks
    on the tissue.
    """
    up = np.zeros_like(mask)
    dn = np.zeros_like(mask)
    for d in range(1, gap + 1):
        up |= _shift(mask, d, 0)
        dn |= _shift(mask, -d, 0)
    return mask | (up & dn)


def despeck(mask, diag=70):
    """Drop components too short to be a stroke.

    Filter on LENGTH only. Filtering out wide-flat components as well looks
    reasonable -- a leader stub is wide, an arc is tall -- and it deleted the
    BASE of the silhouette, which is the widest flat stroke in the figure.
    """
    lab, _ = nd.label(mask)
    keep = np.zeros_like(mask)
    for i, sl in enumerate(nd.find_objects(lab), 1):
        dh, dw = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        if (dh * dh + dw * dw) ** 0.5 >= diag:
            keep[sl] |= lab[sl] == i
    return keep


def path_of(mask, td, name, smoothness="1.334"):
    pbm, svg = Path(td) / f"{name}.pbm", Path(td) / f"{name}.svg"
    Image.fromarray(np.where(mask, 0, 255).astype(np.uint8)).save(pbm)
    subprocess.run(["potrace", str(pbm), "-s", "-o", str(svg), "--turdsize", "60",
                    "--alphamax", smoothness, "--opttolerance", "0.8"], check=True)
    return " ".join(re.findall(r'\sd="([^"]+)"', svg.read_text()))


def main():
    src, out = sys.argv[1], sys.argv[2]
    im = np.asarray(Image.open(src).convert("RGB")).astype(int)
    h, w = im.shape[:2]
    r, g, b = im[..., 0], im[..., 1], im[..., 2]
    lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
    white = (r > 235) & (g > 235) & (b > 235)
    dark = lum < 110
    chroma = im.max(axis=2) - im.min(axis=2)
    ink = (~white) & (~dark) & (chroma > 22)
    green = g - (r + b) / 2

    # OPEN before choosing the component. Closing alone leaves hairline bridges
    # from the figure to specks near the leaders, and a single boundary walk
    # follows such a bridge and returns a contour enclosing half the page --
    # potrace never showed this because it traces subpaths separately and drops
    # the small ones.
    body = fill_holes(main_body(_morph(_morph(close(ink, 3), 5, False), 5, True)))
    # Largest component only. The left flank of the scan carries a green fringe
    # that satisfies the same test, and an ellipse fitted to sac-plus-fringe
    # spans the entire figure -- which is exactly what it did.
    core = main_body(fill_holes(close(ink & (green > 26) & (lum < 205))) & body)
    cells = fill_holes(close(ink & ((r - g) > 18))) & body
    # Horizontal at the normal run; vertical only for runs FAR longer than any
    # curve in the figure. A leader's vertical elbow is a couple of hundred
    # pixels of dead-straight line; an arc, even where it looks vertical, is
    # curving, so its longest single-column run is a few dozen.
    lead = strip_leaders(strip_leaders(dark, axes=(1,)), axes=(0,), run=120)
    arcs = bridge(lead) & _morph(body, 3, True)

    # The silhouette is NOT potraced. potrace fits curves to the pixels it is
    # handed, so scanner noise survives as wobble no matter how high the
    # smoothing goes. Walking the boundary, resampling it evenly and low-pass
    # filtering around the loop gives the curve the illustrator drew.
    # 400 points and a 5-wide window. At 150/13 the filter spanned nearly a
    # tenth of the perimeter and erased both the funicle neck and the micropyle
    # notch -- the two features the figure exists to show.
    d_body = outline(smooth(body, 2), points=400, win=5)
    # And the embryo sac is an ELLIPSE in the book, so it is fitted as one
    # rather than approximated by a closed path with a hundred control points.
    ex, ey, erx, ery, eang = ellipse_of(core)
    with tempfile.TemporaryDirectory() as td:
        d_cells = path_of(smooth(cells, 2), td, "cells") if cells.sum() > 3000 else ""
        d_arcs = path_of(despeck(close(arcs, 3), 150), td, "arcs", "0.9")

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}"
     width="{w}" height="{h}">
  <defs>
    <linearGradient id="tissue" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#CBE08A"/>
      <stop offset="0.55" stop-color="#E6EFAE"/>
      <stop offset="1" stop-color="#F4F3CE"/>
    </linearGradient>
    <linearGradient id="sac" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#8FC63D"/>
      <stop offset="1" stop-color="#BCDF74"/>
    </linearGradient>
  </defs>
  <g stroke="#1A1A1A" stroke-width="{STROKE}" stroke-linejoin="round"
     stroke-linecap="round">
    <path id="body" d="{d_body}" fill="url(#tissue)"/>
    <g transform="translate(0,{h}) scale(0.1,-0.1)">
      <path id="arcs" d="{d_arcs}" fill="#1A1A1A" stroke="none"/>
      {'<path id="cells" d="' + d_cells + '" fill="#F2A0A0" stroke="#1A1A1A" stroke-width="' + str(STROKE / 0.1) + '"/>' if d_cells else ''}
    </g>
    <ellipse id="core" cx="{ex:.1f}" cy="{ey:.1f}" rx="{erx:.1f}" ry="{ery:.1f}"
             transform="rotate({eang:.1f} {ex:.1f} {ey:.1f})" fill="url(#sac)"/>
  </g>
</svg>'''
    Path(out).write_text(svg)
    print(f"  {out}")


if __name__ == "__main__":
    main()
