"""Draw the NCERT embryo sac as clean vector art.

    python tools/embryo_sac_svg.py <scan.png> <out.svg>

`ncert_svg.py` cannot do this figure. It assumes one silhouette with one
embryo sac ellipse inside it -- true of the ovule, and exactly wrong here,
where the figure IS the sac and the whole point is the SEVEN cells in it. Run
generically, the fitted ellipse swallowed the lot and the result was a plain
green egg.

So the silhouette and the cell positions are measured from the scan (the
outline walked and filtered, the cells located as connected components), and
everything else is drawn: the wall stipple, the egg apparatus, the polar
nuclei, the antipodal chamber. The labels in spec/chips/ovule.json point at
normalised coordinates, so the viewBox stays the scan's and the cells stay
where the scan put them -- move one and its label goes with it.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from trace_ncert import _morph, close, fill_holes, main_body  # noqa
from vector_figure import boundary, resample, smooth_loop, to_bezier  # noqa

STROKE = 3.2
INK = "#1A1A1A"
WALL = 56          # stipple band thickness, measured off the scan
RNG = np.random.default_rng(7)   # seeded: the stipple must not move between runs


def walls(mask, thick, points=260, win=13):
    """Outer and inner wall outlines, exactly parallel.

    The inner line used to come from eroding the mask and outlining that
    separately, which gives a boundary that wanders relative to the outer one --
    the band pinches and swells and the figure reads as hand-traced. Offsetting
    the SAME smoothed loop along its own normals keeps the band one width the
    whole way round, which is what the book's pen does.
    """
    P = smooth_loop(resample(boundary(mask), points), win)
    T = np.roll(P, -1, 0) - np.roll(P, 1, 0)
    n = np.stack([-T[:, 1], T[:, 0]], 1)
    n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-9
    if np.dot(n[0], P.mean(0) - P[0]) < 0:      # point the normals inward
        n = -n
    return P, to_bezier(P), to_bezier(smooth_loop(P + n * thick, win))


def masks(src):
    im = np.asarray(Image.open(src).convert("RGB")).astype(int)
    h, w = im.shape[:2]
    r, g, b = im[..., 0], im[..., 1], im[..., 2]
    lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
    white = (r > 235) & (g > 235) & (b > 235)
    ink = (~white) & (lum >= 110) & (im.max(axis=2) - im.min(axis=2) > 22)
    # close(.., 10) bridges the slot a leader line cuts through the wall.
    # At 3 the slot survives, the opening widens it, and the silhouette
    # comes out with a bite taken from the right flank.
    body = fill_holes(main_body(_morph(_morph(close(ink, 10), 5, False), 5, True)))
    return w, h, body


def dots(band, step=15):
    """Stipple on a JITTERED GRID, not on random pixels of the band.

    Sampling n random pixels clumps: some places get four dots on top of each
    other and others none, so the band reads as dirt rather than as stipple. A
    grid jittered by less than half its spacing can neither clump nor leave a
    hole. Placement is still tested against the mask, so it cannot leak outside.
    """
    ys, xs = np.nonzero(band)
    out = []
    for y in range(ys.min(), ys.max() + 1, step):
        for x in range(xs.min(), xs.max() + 1, step):
            py = int(y + RNG.uniform(-step * 0.42, step * 0.42))
            px = int(x + RNG.uniform(-step * 0.42, step * 0.42))
            if 0 <= py < band.shape[0] and 0 <= px < band.shape[1] and band[py, px]:
                out.append(f'<circle cx="{px}" cy="{py}" '
                           f'r="{RNG.uniform(1.7, 2.6):.1f}"/>')
    return "".join(out)


def filiform(cx, cy, rx, ry, n=24):
    """Filiform apparatus: finger-like LOBES hanging into the micropylar tip.

    Drawn as closed teardrops, not as pen strokes -- as strokes they read as
    handwriting, which is what the first version looked like.
    """
    out = []
    for k in range(n):
        t = (k + 0.5) / n
        x = cx + (t * 2 - 1) * rx
        y = cy + (1 - abs(t * 2 - 1) ** 2) * ry * 0.30 + RNG.uniform(-8, 8)
        L, W = RNG.uniform(58, 104), RNG.uniform(19, 29)
        out.append(f'<path d="M{x:.0f} {y:.0f}c{-W:.0f} {L*.5:.0f} {-W*.7:.0f} '
                   f'{L:.0f} 0 {L:.0f}c{W*.7:.0f} 0 {W:.0f} {-L*.5:.0f} 0 {-L:.0f}z"/>')
    return (f'<g fill="#EDF4C8" stroke="{INK}" stroke-width="6">{"".join(out)}</g>')


def chromatin(cx, cy, rx, ry, n=34):
    """The speckled chromatin inside a polar nucleus -- short dark dashes."""
    out = []
    for _ in range(n):
        a, t = RNG.uniform(0, 6.283), np.sqrt(RNG.uniform(0, 1)) * 0.82
        x, y = cx + np.cos(a) * rx * t, cy + np.sin(a) * ry * t
        dx, dy = RNG.uniform(-9, 9), RNG.uniform(-9, 9)
        out.append(f'<path d="M{x:.0f} {y:.0f}l{dx:.0f} {dy:.0f}"/>')
    return (f'<g fill="none" stroke="{INK}" stroke-width="4" '
            f'stroke-linecap="round">{"".join(out)}</g>')


def nucleus(cx, cy, r, dot=0.22):
    """Red nucleus: pale centre, red rim, dark spot -- the book's cell marker."""
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#nuc)" stroke="{INK}"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r*dot:.1f}" fill="#241209" stroke="none"/>')


def main():
    src, out = sys.argv[1], sys.argv[2]
    w, h, body = masks(src)
    # 260/13: this outline has no feature to protect, unlike the ovule's,
    # so it is smoothed until it reads as the drawn oval it is.
    P, d_out, d_in = walls(body, WALL)
    inner = _morph(body, WALL, False)
    band = body & ~inner

    # The chalazal chamber: an arc across the base walls off the antipodals.
    # Drawn, not traced -- in the scan it is a single pen stroke and tracing it
    # as an area gives a sliver with two edges.
    cy_ch, x_l, x_r = 1462, 152, 764
    chamber = f'M{x_l} {cy_ch}Q{w/2:.0f} {cy_ch-132:.0f} {x_r} {cy_ch}'
    # each partition starts ON the arc and runs to the base, splaying outward
    parts = "".join(f'<path d="M{x0} {y0}Q{x0+(x1-x0)*.35:.0f} {(y0+y1)/2:.0f} '
                    f'{x1} {y1}" fill="none"/>'
                    for x0, y0, x1, y1 in [(372, 1352, 276, 1730), (572, 1358, 668, 1726)])

    E = 458, 486          # egg apparatus centre
    syn = [(350, 336, 56, 336, 524, 78, 104), (558, 358, 52, 528, 556, 76, 94)]
    anti = [(338, 1520, 36), (464, 1492, 38), (582, 1528, 36)]

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}"
     width="{w}" height="{h}">
  <defs>
    <linearGradient id="cell" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#F6F8CE"/><stop offset="1" stop-color="#DCEB94"/>
    </linearGradient>
    <linearGradient id="wall" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#D3E48D"/><stop offset="1" stop-color="#C3DC77"/>
    </linearGradient>
    <linearGradient id="egg" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#A6D157"/><stop offset="1" stop-color="#BEDD7E"/>
    </linearGradient>
    <radialGradient id="nuc" cx="0.42" cy="0.34" r="0.78">
      <stop offset="0" stop-color="#F7B79A"/><stop offset="0.62" stop-color="#EE6070"/>
      <stop offset="1" stop-color="#E2394F"/>
    </radialGradient>
    <linearGradient id="polar" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#EA4257"/><stop offset="1" stop-color="#F6A882"/>
    </linearGradient>
    <linearGradient id="vac" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#FBD5DC"/><stop offset="1" stop-color="#F7B3C1"/>
    </linearGradient>
    <clipPath id="bandclip"><path d="{d_out} {d_in}" fill-rule="evenodd"/></clipPath>
    <clipPath id="inclip"><path d="{d_in}"/></clipPath>
  </defs>
  <g stroke="{INK}" stroke-width="{STROKE}" stroke-linejoin="round" stroke-linecap="round">

    <path d="{d_out}" fill="url(#wall)"/>
    <g clip-path="url(#bandclip)" fill="#4A5C18" stroke="none">{dots(band)}</g>
    <path d="{d_out}" fill="none"/>
    <path d="{d_in}" fill="url(#cell)"/>

    <!-- chalazal chamber, then the three antipodals inside it -->
    <g clip-path="url(#inclip)">
      <path d="{chamber}" fill="none"/>
      {parts}
      {"".join(nucleus(*a) for a in anti)}
    </g>

    <!-- egg apparatus -->
    <ellipse cx="{E[0]}" cy="{E[1]}" rx="230" ry="248" fill="url(#egg)"/>
    <path d="M{E[0]} {E[1]-254}L{E[0]} {E[1]+212}" fill="none"/>
    {filiform(E[0], 274, 196, 66, 21)}
    {"".join(f'<ellipse cx="{vx}" cy="{vy}" rx="{vrx}" ry="{vry}" fill="url(#vac)"/>'
             + nucleus(nx, ny, nr) for nx, ny, nr, vx, vy, vrx, vry in syn)}
    <ellipse cx="452" cy="660" rx="122" ry="66" fill="url(#egg)"/>
    <ellipse cx="462" cy="666" rx="58" ry="42" fill="url(#vac)"/>
    {nucleus(408, 650, 34)}

    <!-- two polar nuclei in the central cell -->
    <ellipse cx="391" cy="828" rx="60" ry="102" fill="url(#polar)"/>
    <ellipse cx="503" cy="828" rx="60" ry="102" fill="url(#polar)"/>
    <ellipse cx="391" cy="812" rx="38" ry="56" fill="#FFFFFF"/>
    <ellipse cx="503" cy="812" rx="38" ry="56" fill="#FFFFFF"/>
    {chromatin(391, 812, 38, 56)}{chromatin(503, 812, 38, 56)}
  </g>
</svg>'''
    Path(out).write_text(svg)
    print(f"  {out}")


if __name__ == "__main__":
    main()
