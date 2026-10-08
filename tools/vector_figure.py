"""Clean vector geometry from a mask: smooth closed outlines and fitted ellipses.

potrace fits curves to the pixels it is given, so a boundary that is ragged in
the scan stays ragged in the SVG — smoothing settings only soften it. To get the
shape the illustrator drew rather than the shape the scanner recorded, the
boundary is walked, resampled at even arc length, low-pass filtered around the
loop, and re-emitted as a Catmull-Rom spline converted to cubic Béziers.

Filtering AROUND THE LOOP (wrapping) matters: filter it as an open list and the
join where the boundary closes gets a corner that was never there.
"""
from __future__ import annotations

import numpy as np

NEI = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)]


def boundary(mask: np.ndarray) -> np.ndarray:
    """Moore-neighbourhood walk of the outer boundary, in order.

    The backtrack pixel has to be carried explicitly: the search around each new
    boundary pixel must START from where you came from, or the walk oscillates
    between two neighbours and never closes.
    """
    m = np.pad(mask, 1)
    ys, xs = np.nonzero(m)
    y0 = int(ys.min())
    x0 = int(xs[ys == y0].min())
    start = (y0, x0)
    b, c, out = start, (y0, x0 - 1), [start]
    for _ in range(500000):
        d = NEI.index((c[0] - b[0], c[1] - b[1]))
        nxt = None
        for k in range(1, 9):
            nd = (d + k) % 8
            n = (b[0] + NEI[nd][0], b[1] + NEI[nd][1])
            if m[n]:
                back = (b[0] + NEI[(nd - 1) % 8][0], b[1] + NEI[(nd - 1) % 8][1])
                nxt = (n, back)
                break
        if nxt is None:
            break
        b, c = nxt
        if b == start:
            break
        out.append(b)
    return np.array(out, float) - 1


def resample(pts: np.ndarray, n: int) -> np.ndarray:
    d = np.r_[0, np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))]
    t = np.linspace(0, d[-1], n, endpoint=False)
    return np.c_[np.interp(t, d, pts[:, 0]), np.interp(t, d, pts[:, 1])]


def smooth_loop(pts: np.ndarray, win: int) -> np.ndarray:
    k = np.ones(win) / win
    out = np.empty_like(pts)
    for i in (0, 1):
        out[:, i] = np.convolve(np.r_[pts[-win:, i], pts[:, i], pts[:win, i]],
                                k, "same")[win:-win]
    return out


def to_bezier(pts: np.ndarray, flip_h: int = 0) -> str:
    """Catmull-Rom through the points, as cubics.

    flip_h is for paths that will sit inside potrace's flipped group. In plain
    SVG space pass 0: flipping there turns the figure upside down, and the tell
    is subtle -- the micropyle notch simply appears at the bottom instead of the
    top, which reads as a dent rather than as an error.
    """
    P = [(p[1], (flip_h - p[0]) if flip_h else p[0]) for p in pts]
    n = len(P)
    d = [f"M{P[0][0]:.1f},{P[0][1]:.1f}"]
    for i in range(n):
        p0, p1 = P[(i - 1) % n], P[i]
        p2, p3 = P[(i + 1) % n], P[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d.append(f"C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} "
                 f"{p2[0]:.1f},{p2[1]:.1f}")
    return " ".join(d) + " Z"


def outline(mask: np.ndarray, points: int = 130, win: int = 11) -> str:
    return to_bezier(smooth_loop(resample(boundary(mask), points), win))


def ellipse_of(mask: np.ndarray) -> tuple:
    """Centre, radii and rotation of the ellipse that matches this blob."""
    ys, xs = np.nonzero(mask)
    cy, cx = ys.mean(), xs.mean()
    cov = np.cov(np.c_[xs - cx, ys - cy].T)
    val, vec = np.linalg.eigh(cov)
    order = np.argsort(-val)
    val, vec = val[order], vec[:, order]
    rx, ry = 2 * np.sqrt(val)
    ang = np.degrees(np.arctan2(vec[1, 0], vec[0, 0]))
    return cx, cy, rx, ry, ang
