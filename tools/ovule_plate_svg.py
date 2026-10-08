"""Colour the faculty's ovule plate — its OWN lines, not a redrawing of them.

    python tools/ovule_plate_svg.py [reference.jpeg] [out.svg] [--debug out.png]

FOUR ATTEMPTS BEFORE THIS ONE, AND WHY THEY FAILED
--------------------------------------------------
`ovule_svg.py` and `ovule_ncert_svg.py` DRAW an ovule from parameters. Both were
anatomically right and neither was this drawing: the funicle at its own angle,
the nucellus its own width, ninety-odd cells of the illustrator's own sizes.
Shape cannot be argued into place.

The third tried to measure regions off the plate and re-emit them as smooth
shapes — silhouette, nucellus blob, sac ellipse. That is still a redrawing, and
worse, it traced masks that had been upscaled with `np.kron`, which turns every
source pixel into a hard 4x4 block; potrace then fits curves to a staircase and
the result is a green blob with square corners.

WHAT THIS ONE DOES
------------------
It traces the plate's REGIONS and fills them. Not its ink — that was the fifth
attempt, and it drags the label leaders in with the drawing. The leaders cross
the integument and run deep into the nucellus, so they chop the integument into
compartments that then colour up as a neat grid of squares off the ovule's
right-hand side, and removing them afterwards does not work either: a leader is
a long straight thin run, and so, over any length that catches one, is the
nucellus ring, the inner integument and the funicle's own walls. Detecting them
took out half the drawing with them.

Filling regions instead makes the whole question disappear. A leader has no
area, so it is never a region, so it is never drawn. What IS drawn comes off the
plate:

    silhouette   what the outline contains, holes filled
    cells        every small enclosed area whose middle lies in the nucellus.
                 These are the illustrator's own cells, at the illustrator's own
                 sizes; an earlier version generated a Voronoi tessellation in
                 their place and it read as gravel.
    nucellus     the region those cells cover, so it is defined BY them and
                 cannot come out the wrong width
    integument   the rest of the silhouette, in two shells: the areas that touch
                 the nucellus are the inner integument, the rest is the outer.
                 They are split this way BECAUSE of the leaders — the annulus is
                 in pieces, and asking which pieces hug the nucellus puts it
                 back together without caring how many pieces there are.
    strand       the solid black band in the funicle, darker than any line

THE SOURCE IS 320x292. That is the whole budget: the cells are about ten pixels
across. So the GREYSCALE is upscaled with LANCZOS *before* thresholding, which
recovers the edge position from the antialiasing and gives potrace something
smooth to fit. Upscaling the mask instead is what produced the staircase.

The crop is decided at native resolution: the label column and its leader lines
have to go, and `strip_leaders` only works at native scale — at 6x its run
length is shorter than the drawing's own long curves and it cuts the outline
into confetti. So the body is found small, and its bounding box is what gets
cropped out of the full-resolution original.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ncert_svg import despeck, smooth  # noqa: E402
from trace_ncert import close, fill_holes, main_body, strip_leaders  # noqa: E402

INK = "#33421F"         # the plate's lines, warmed towards the palette
C_OUTER = "#7E9E33"     # outer integument
C_OUTER2 = "#92B345"    # the outer integument, shaded across
C_GROUND = "#BAD371"    # inner integument, the shell hugging the nucellus
C_NUCEL = "#89A93F"     # nucellus, behind its cells
C_CELL = "#EEF5D2"      # a nucellus cell's lumen
C_SAC = "#FBFDF0"       # the embryo sac's cells
C_SACB = "#E8F1C8"      # the embryo sac's ground
C_EGG = "#C3DB86"       # a cell of the egg apparatus
C_NUCLEUS = "#5C7A22"   # a nucleus
C_VASC = "#415A16"      # the vascular strand's solid band
UP = 6                  # trace at 6x: 320px of source is the whole budget
CLOSE, OPEN = 2, 3      # source-scale morphology, swept and measured
SIL_SMOOTH = 60         # figure px of wobble taken off the outer boundary
PIN_HOLD, PIN_FREE = 600, 2600   # potrace units: stalk held, then smoothed
STALK_FLARE = 26        # figure px added each side at the base of the funicle
CANVAS_ROWS = 250       # source rows kept: caps how tall the figure gets


def trace(mask: np.ndarray, td: str, name: str, alpha: str = "1.0",
          opt: str = "0.4") -> str:
    """One mask -> one path payload.

    `opt` is potrace's curve-optimisation tolerance and it is the knob that
    smooths a CONTOUR without moving the mask underneath it: raising it lets
    potrace span more of the boundary with each Bezier, so the pen's wobble
    drops out while the shape it is wobbling around stays put. Blurring the mask
    harder does the same job to the outline but eats the funicle, which is only
    eight source pixels wide.
    """
    if mask.sum() < 40:
        return ""
    pbm, svg = Path(td) / f"{name}.pbm", Path(td) / f"{name}.svg"
    Image.fromarray(np.where(mask, 0, 255).astype(np.uint8)).save(pbm)
    subprocess.run(["potrace", str(pbm), "-s", "-o", str(svg), "--turdsize", "4",
                    "--alphamax", alpha, "--opttolerance", opt], check=True)
    return " ".join(re.findall(r'\sd="([^"]+)"', svg.read_text()))


def _bez(p0, p1, p2, p3, step):
    n = max(int((abs(p1[0] - p0[0]) + abs(p1[1] - p0[1]) + abs(p2[0] - p1[0])
                 + abs(p2[1] - p1[1]) + abs(p3[0] - p2[0]) + abs(p3[1] - p2[1]))
                / step), 2)
    t = np.linspace(0, 1, n + 1)[1:]
    u = 1 - t
    return list(zip(u**3 * p0[0] + 3*u*u*t * p1[0] + 3*u*t*t * p2[0] + t**3 * p3[0],
                    u**3 * p0[1] + 3*u*u*t * p1[1] + 3*u*t*t * p2[1] + t**3 * p3[1]))


def smooth_outline(d: str, sigma_px: float, step: float = 20.0) -> str:
    """Take the wobble out of a traced boundary, leaving the shape it wobbles about.

    Nothing else available here could do this. potrace's own `--opttolerance`
    saturates almost at once — past 3 the path stops getting shorter, because
    the bumps are really in the mask and it is tracing them faithfully. Blurring
    the mask harder does smooth them, and it also thins the funicle, which is
    only about forty-eight pixels across at this scale: by sigma 4.5 the stalk
    had pulled away from the ovule altogether.

    So the CONTOUR is smoothed instead of the region. The path is resampled into
    dense points in order, the two coordinate series are low-passed around the
    loop, and the result is emitted as a polyline. A width is never touched,
    because the two sides of the funicle are half a perimeter apart in the
    ordering and the filter only ever looks along it.

    Coordinates stay in potrace's tenths-of-a-pixel space, so `sigma_px` is
    given in figure pixels and scaled here.
    """
    sigma = max(sigma_px * 10.0 / step, 0.5)
    out, pts = [], []
    cur = start = (0.0, 0.0)
    tok = re.findall(r"[A-Za-z]|-?\d+(?:\.\d+)?", d)
    i, cmd = 0, None
    while i < len(tok):
        if tok[i].isalpha():
            cmd = tok[i]
            i += 1
            if cmd in "Zz":
                if len(pts) > 8:
                    out.append(np.array(pts))
                pts, cur = [], start
            continue
        if cmd in "Mm":
            x, y = float(tok[i]), float(tok[i + 1])
            i += 2
            if cmd == "m":
                x, y = cur[0] + x, cur[1] + y
            cur = start = (x, y)
            pts = [cur]
            cmd = "L" if cmd == "M" else "l"
        elif cmd in "Cc":
            v = [float(tok[i + k]) for k in range(6)]
            i += 6
            if cmd == "c":
                v = [cur[0] + v[0], cur[1] + v[1], cur[0] + v[2],
                     cur[1] + v[3], cur[0] + v[4], cur[1] + v[5]]
            pts.extend(_bez(cur, v[0:2], v[2:4], v[4:6], step))
            cur = (v[4], v[5])
        elif cmd in "Ll":
            x, y = float(tok[i]), float(tok[i + 1])
            i += 2
            if cmd == "l":
                x, y = cur[0] + x, cur[1] + y
            pts.append((x, y))
            cur = (x, y)
        else:
            i += 1
    if len(pts) > 8:
        out.append(np.array(pts))

    d2 = []
    for c in out:
        x = ndi.gaussian_filter1d(c[:, 0], sigma, mode="wrap")
        y = ndi.gaussian_filter1d(c[:, 1], sigma, mode="wrap")
        # HOLD THE BOTTOM OF THE STALK. The funicle runs off the bottom of the
        # scan, so the contour crosses the page edge as a flat line between two
        # right angles — and a filter this wide reads those corners as the
        # sharpest feature on the whole loop and rounds them off, tapering the
        # stalk over its last stretch. Measured against the plate: it holds 55
        # pixels of width down to the edge, and the smoothed version had fallen
        # to 35. Those corners are not wobble, they are where the drawing stops,
        # so the smoothing is faded out over the lower part of the stalk and the
        # plate's own width is kept. potrace's y runs upwards, so the page edge
        # is y near zero; the ovule's body bottom is well above PIN_FREE.
        t = np.clip((c[:, 1] - PIN_HOLD) / (PIN_FREE - PIN_HOLD), 0.0, 1.0)
        x, y = t * x + (1 - t) * c[:, 0], t * y + (1 - t) * c[:, 1]
        # Thinned to keep the file small — but NOT across the held corners. At
        # one vertex every sixty pixels the polyline simply cut the base of the
        # stalk off diagonally, undoing the hold above: the width fell from 75
        # back to 33 in the last few rows. Wherever the smoothing is faded out,
        # every point is kept.
        stride = max(int(sigma), 1)
        keep = np.nonzero((np.arange(len(x)) % stride == 0) | (t < 0.99))[0]
        d2.append("M" + "L".join(f"{x[j]:.0f} {y[j]:.0f}" for j in keep) + "z")
    return "".join(d2)


def solid(mask: np.ndarray, close_k: int, open_k: int) -> np.ndarray:
    """The figure as a solid area, with the leader lines taken off it.

    Fill what the outline encloses, then OPEN with a kernel wider than a leader
    and narrower than the funicle. That is the whole trick: a leader is a line
    about a pixel and a half across at source scale and the funicle is eight, so
    a single number separates them, while opening leaves the boundary itself
    where the illustrator put it.

    `strip_leaders` was tried here first and does not work on this plate — it
    looks for long runs along an axis and every leader on this page is DIAGONAL,
    so all of them survived, the body blob reached into the label column, and
    the crop came back four times too wide.

    BOTH strengths are measured, not guessed, and the closing is the one that
    matters. The plate's outline is broken by paper texture, and at CLOSE=1 the
    gaps stay open, the fill leaks out through them, and the only thing left
    solid enough to survive the opening is the mass of cell walls — so the
    "silhouette" came back as the nucellus alone and the crop cut the funicle
    off at both ends. At CLOSE=2 the outline seals and the area jumps from
    20560px to 28109px; above that the closing starts swallowing the label
    column. Opening is flat anywhere from 2 to 5, so 3 sits in the middle.
    """
    filled = fill_holes(main_body(close(mask, close_k)))
    kk = np.ones((2 * open_k + 1, 2 * open_k + 1))
    return main_body(ndi.binary_dilation(ndi.binary_erosion(filled, kk), kk))


def trim(sil: np.ndarray, floor: int = 12) -> np.ndarray:
    """Cut the box back to where the figure has BODY, not just a line.

    A leader that reaches past the outline still gets closed into the blob and
    still stretches its bounding box. But a leader is one or two pixels across
    and every real part of this drawing — the funicle included — is at least
    eight, so a column holding fewer than `floor` pixels of body is a leader and
    not the ovule. Measured on this plate: the outline's right edge is column
    223, where the height falls 65 -> 20 -> 9, and the stray ink beyond it runs
    to column 248.
    """
    col, row = sil.sum(0), sil.sum(1)
    xs, ys = np.nonzero(col >= floor)[0], np.nonzero(row >= floor)[0]
    box = np.zeros_like(sil)
    box[ys.min():ys.max() + 1, xs.min():xs.max() + 1] = True
    return sil & box


def ribbon(mask, sigma, taper=0.10):
    """The band redrawn from its own centreline, as a smooth tapering ribbon.

    Morphology could not clean this up. The plate inks the vascular bundle by
    hand over three hundred pixels, so its mask arrives stepped, notched and
    flecked, and closing it fattened the lumps while opening bit new holes —
    it stayed a blotch either way, which is what "patchy" meant.

    A bundle is a ribbon, so it is measured as one: at every row, where its
    middle is and how wide it is. Both series are then smoothed ALONG the band,
    which is a one-dimensional problem and well behaved, and the two edges are
    walked back as a polygon. Outliers are kept out by reading the width between
    percentiles rather than between the extremes — a single stray pixel from the
    scan would otherwise throw the edge sideways for that row.
    """
    ys = np.nonzero(mask.any(1))[0]
    y0, y1 = int(ys.min()), int(ys.max())
    n = y1 - y0 + 1
    cx, hw = np.full(n, np.nan), np.full(n, np.nan)
    for i in range(n):
        xs = np.nonzero(mask[y0 + i])[0]
        if len(xs) < 2:
            continue
        lo, hi = np.percentile(xs, 6), np.percentile(xs, 94)
        cx[i], hw[i] = (lo + hi) / 2, max((hi - lo) / 2, 1.0)
    idx = np.arange(n)
    ok = ~np.isnan(cx)
    cx = ndi.gaussian_filter1d(np.interp(idx, idx[ok], cx[ok]), sigma)
    hw = ndi.gaussian_filter1d(np.interp(idx, idx[ok], hw[ok]), sigma)
    # Close the top end off. The bundle thins out towards the chalaza on the
    # plate; left square it reads as a cut pipe.
    t = max(int(taper * n), 1)
    hw[:t] *= np.linspace(0.15, 1.0, t)
    step = max(n // 90, 1)
    rows = list(range(0, n, step)) + [n - 1]
    return ([(cx[i] - hw[i], y0 + i) for i in rows]
            + [(cx[i] + hw[i], y0 + i) for i in reversed(rows)])


def poly_path(pts) -> str:
    d = f"M{pts[0][0]:.1f} {pts[0][1]:.1f}"
    return d + "".join(f"L{x:.1f} {y:.1f}" for x, y in pts[1:]) + "Z"


def raster(pts, shape) -> np.ndarray:
    """The drawn shape, back as a mask, so the anchors are checked against what
    is actually on screen rather than against the mask it was derived from."""
    im = Image.new("1", (shape[1], shape[0]), 0)
    ImageDraw.Draw(im).polygon([(float(x), float(y)) for x, y in pts], fill=1)
    return np.asarray(im, bool)


def embryo_sac(c, r) -> str:
    """The seven cells, to the classical layout, at the plate's own position.

    Laid out for the MICROPYLE AT THE BOTTOM, which is this plate's orientation
    and the opposite of the figure the video used before — so the egg apparatus
    is at the bottom and the antipodals at the top. Getting that the wrong way
    round draws a correct-looking sac that teaches the ovule upside down.

    Every offset is a fraction of the sac's own radii, so the whole group moves
    and scales with the ellipse fitted to the plate. Cells are placed by the
    width available AT THEIR OWN HEIGHT: an ellipse is narrow near its ends, and
    cells spaced by the width at the middle push out through the top and bottom.
    """
    (cx, cy), (rx, ry) = c, r
    o = [f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" '
         f'fill="{C_SACB}" stroke-width="{0.012 * (rx + ry):.1f}"/>']
    sw = f'stroke-width="{0.008 * (rx + ry):.1f}"'

    def cell(dx, dy, wx, wy, nucleus=0.42):
        x, y = cx + dx * rx, cy + dy * ry
        s = (f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{wx * rx:.1f}" '
             f'ry="{wy * ry:.1f}" fill="{C_EGG}" {sw}/>')
        if nucleus:
            s += (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{nucleus * wx * rx:.1f}" '
                  f'fill="{C_NUCLEUS}" stroke="none"/>')
        return s

    # chalazal end, at the top: three antipodals
    for dx, dy in ((-0.40, -0.66), (0.02, -0.79), (0.42, -0.64)):
        o.append(cell(dx, dy, 0.21, 0.075))
    # the middle: two polar nuclei in one central cell
    o.append(f'<ellipse cx="{cx:.1f}" cy="{cy - 0.02 * ry:.1f}" rx="{0.62 * rx:.1f}" '
             f'ry="{0.15 * ry:.1f}" fill="{C_EGG}" {sw}/>')
    for dx in (-0.24, 0.24):
        o.append(f'<circle cx="{cx + dx * rx:.1f}" cy="{cy - 0.02 * ry:.1f}" '
                 f'r="{0.15 * rx:.1f}" fill="{C_NUCLEUS}" stroke="none"/>')
    # micropylar end, at the bottom: the egg cell, then the two synergids below it
    o.append(cell(0.0, 0.52, 0.34, 0.115))
    for dx in (-0.33, 0.33):
        o.append(cell(dx, 0.75, 0.24, 0.085))
    return "    " + "\n    ".join(o)


# The eleven places the plate names, as fractions of the figure. They are
# computed from the masks and then CHECKED against them, because a label that
# has drifted off the part it names is the defect this figure keeps producing —
# the nucellus label ended up inside the embryo sac once, after the sac was
# enlarged and nobody re-measured. Fractions rather than pixels so they survive
# the figure being rescaled into a band of any height.
def anchors(out, w, h, sil, nucellus, sac, strand, ring, micro):
    ny, nx = np.nonzero(nucellus)
    n_top, n_bot, n_l, n_r = ny.min(), ny.max(), nx.min(), nx.max()
    ncx, ncy = (n_l + n_r) / 2, (n_top + n_bot) / 2
    sy, sx = np.nonzero(sac)
    s_top, s_bot = sy.min(), sy.max()
    scx = (sx.min() + sx.max()) / 2
    sh = s_bot - s_top

    # The ovule's body, told from the stalk by width: the body is the widest
    # part of the figure and the funicle is a fraction of it.
    rows = sil.sum(1)
    body_rows = np.nonzero(rows > 0.45 * rows.max())[0]
    b_top, b_bot = body_rows.min(), body_rows.max()
    row = sil[int(ncy)]
    b_r = np.nonzero(row)[0].max()

    ty, tx = np.nonzero(strand)
    low = ty > np.percentile(ty, 82)

    def pick(mask, y, frac=0.5):
        """A point that is genuinely ON `mask`, at row `y`, `frac` across it.

        Computing an anchor as the middle of a bounding box is what put the
        polar-nuclei label outside the embryo sac: the sac is the union of the
        plate's own cells and its middle row is not centred on its box. Reading
        the row off the mask cannot miss. If the row is empty the nearest
        occupied one is used, so an anchor never falls in a gap.
        """
        ys = np.nonzero(mask.any(1))[0]
        y = int(ys[np.argmin(np.abs(ys - y))])
        xs = np.nonzero(mask[y])[0]
        return float(xs[int(round(frac * (len(xs) - 1)))]), float(y)

    pts = {
        "निभाग":            (ncx, (b_top + n_top) / 2),
        "अध्यावरण":          ((n_r + b_r) / 2, ncy),
        "बीजाण्डकाय":         pick(nucellus & ~sac, n_top + (n_bot - n_top) * 0.22, 0.30),
        "प्रतिध्रुवी कोशिकाएँ":  pick(sac, s_top + sh * 0.10),
        "द्वितीयक केन्द्रक":     pick(sac, s_top + sh * 0.42),
        "भ्रूणकोष":           pick(sac, s_top + sh * 0.60),
        "अण्ड कोशिका":        pick(sac, s_bot - sh * 0.14),
        "सहायक कोशिका":       pick(sac, s_bot - sh * 0.03),
        "बीजाण्डद्वार":        pick(micro, (n_bot + b_bot) / 2, 0.5),
        "हाइलम":            pick(strand, b_bot - (b_bot - b_top) * 0.04),
        "बीजाण्डवृन्त":         pick(strand, np.percentile(ty, 88)),
    }
    # Every anchor has to land in the thing it names.
    holds = {"निभाग": sil & ~nucellus, "अध्यावरण": sil & ~nucellus,
             "बीजाण्डकाय": nucellus & ~sac, "प्रतिध्रुवी कोशिकाएँ": sac,
             "द्वितीयक केन्द्रक": sac, "भ्रूणकोष": sac, "अण्ड कोशिका": sac,
             "सहायक कोशिका": sac, "बीजाण्डद्वार": micro,
             "हाइलम": sil, "बीजाण्डवृन्त": sil}
    bad = []
    for name, (x, y) in pts.items():
        if not holds[name][int(round(y)), int(round(x))]:
            bad.append(name)
    path = out.with_suffix(".anchors.json")
    path.write_text(json.dumps(
        {"figure": [w, h],
         "anchors": {k: [round(x / w, 4), round(y / h, 4)] for k, (x, y) in pts.items()}},
        ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"  {path}  {len(pts)} anchors")
    if bad:
        print("  OFF THE PART THEY NAME: " + ", ".join(bad))
        sys.exit(1)
    print("  every anchor lands inside the part it names")


def main() -> None:
    argv = [a for a in sys.argv[1:] if not a.startswith("--")]
    debug = "--debug" in sys.argv
    src = Path(argv[0] if argv else "inbox/figures/ovule-real.jpeg")
    out = Path(argv[1] if len(argv) > 1
               else "tools/edu/renderer/assets/ovule-plate.svg")

    im = Image.open(src).convert("L")
    g = np.asarray(im).astype(int)

    # THE FIGURE IS FOUND SMALL AND USED AS A STENCIL. Everything about the
    # leaders is easier at source scale: there are fewer of them, they are
    # broken by scan noise, and the morphology that separates them from the
    # drawing was swept and measured here. Upscaling first and hoping does not
    # work — LANCZOS joins up every broken leader, the closing then welds the
    # ones that converge on the figure into solid wedges, and `fill_holes`
    # paints their insides. That is what produced a neat grid of green squares
    # off the right-hand side of the ovule where the label column had been.
    # The funicle runs off the bottom of the scan, so the area between its two
    # walls is not enclosed by anything and `fill_holes` leaves it empty — the
    # stalk came out as the dark vascular band with no tissue around it. Inking
    # the last row closes it against the edge of the page.
    ink_n = g < 150
    ink_n[-1, :] = True
    sil_n = solid(ink_n, CLOSE, OPEN)
    stencil = trim(sil_n)
    ys, xs = np.nonzero(stencil)
    pad = 3
    box = (max(xs.min() - pad, 0), max(ys.min() - pad, 0),
           min(xs.max() + pad + 1, g.shape[1]), min(ys.max() + pad + 1, g.shape[0]))
    # THE FUNICLE IS CUT SHORT ON PURPOSE. The plate's stalk runs off the bottom
    # of the page, so the figure came out 1.77 times taller than it is wide, and
    # the chip is fitted to the band BY HEIGHT — which made the ovule narrow
    # enough that its cells fell to four pixels across, and still left the stalk
    # hanging into the presenter. The stalk is the least informative part of the
    # drawing and it is already cut arbitrarily by the edge of the scan, so it
    # is cut a little higher instead and the body keeps its size.
    box = (box[0], box[1], box[2], min(box[3], box[1] + CANVAS_ROWS))

    im = im.crop(box)
    # LANCZOS on the GREY, then threshold. The other order gives a staircase.
    im = im.resize((im.width * UP, im.height * UP), Image.LANCZOS)
    a = np.asarray(im).astype(int)
    h, w = a.shape

    # THE OUTLINE COMES FROM THE SMALL MASK, RESAMPLED — not from the big one.
    # Re-finding the silhouette at 6x needs a closing of twelve pixels to seal
    # the gaps the pen left in the outline, and a closing that big welds the
    # leaders converging on the right-hand side into one solid wedge, which
    # fills and prints as a stepped bulge two source pixels outside the ovule.
    # Anything smaller does not seal at all: the fill escapes and the only thing
    # left is the nucellus (485k pixels against the true 938k). Both were
    # measured. So the silhouette is settled at source scale, where the sweep
    # says CLOSE=2 seals it, and then resampled with interpolation so its edge
    # lands between source pixels instead of on the corners of them.
    m = Image.fromarray((stencil[box[1]:box[3], box[0]:box[2]] * 255).astype(np.uint8))
    sil = np.asarray(m.resize((w, h), Image.BILINEAR)) > 127
    # Even at source scale the closing welds the odd pair of leaders where they
    # almost touch the outline, and the fill runs a few pixels into the gap
    # between them. Those bumps are two to four pixels deep and twenty long —
    # too shallow for an opening to lift off, and very visible once the region
    # is a flat colour, which is what the notches down the right-hand edge were.
    # The ovule's outline is a smooth closed curve, so blurring the mask and
    # re-thresholding takes them out without moving the curve.
    sil = ndi.gaussian_filter(sil.astype(float), 1.5 * UP) > 0.5

    # THE STALK FLARES TOWARDS ITS BASE. The plate draws the funicle at an even
    # width all the way down and it reads as a thin tail hanging off the ovule,
    # so it is widened — a deliberate change to the plate, and the only one made
    # to the outline. The stalk is told from the body by width: the body is the
    # widest part of the figure and the funicle a fraction of it, so the widening
    # starts where the figure narrows past half and ramps to STALK_FLARE at the
    # bottom of the frame. Ramped rather than switched on, or the stalk gains a
    # visible step where the two meet.
    rows = sil.sum(1)
    top = int(np.nonzero(rows > 0.45 * rows.max())[0].max())
    grow = np.zeros(h, int)
    grow[top:] = np.linspace(0, STALK_FLARE, h - top).astype(int)
    wide = sil.copy()
    for k in range(1, STALK_FLARE + 1):
        at = (grow >= k)[:, None]
        for sh in (k, -k):
            r = np.roll(sil, sh, axis=1)
            r[:, :k] = False if sh > 0 else r[:, :k]
            r[:, -k:] = False if sh < 0 else r[:, -k:]
            wide |= r & at
    sil = wide

    ink = despeck(a < 150, diag=2 * UP) & sil

    # THE NUCELLUS, FOUND FIRST AND FOUND SMALL. Closing the ink merges the
    # cell walls into one solid patch, and opening that with a kernel wider
    # than the funicle's band leaves the patch alone and deletes everything
    # else. It only has to be good enough to say which enclosed areas are
    # cells; the cells then redefine it exactly.
    dense = fill_holes(close(ink_n & ndi.binary_erosion(sil_n, np.ones((9, 9))), 4))
    k = np.ones((11, 11))
    seed = main_body(ndi.binary_dilation(ndi.binary_erosion(dense, k), k))
    seed = np.kron(seed[box[1]:box[3], box[0]:box[2]], np.ones((UP, UP), bool))

    # THE ENCLOSED AREAS. Every hole the ink leaves inside the silhouette is
    # something the illustrator drew a boundary around.
    lab, n = ndi.label(~ink & sil)
    areas = ndi.sum(np.ones_like(lab), lab, range(1, n + 1))
    ids = np.arange(1, n + 1)
    cent = np.array(ndi.center_of_mass(~ink & sil, lab, list(ids)))

    # A cell is small AND sits in the nucellus. Size alone is not enough: the
    # strips the leaders cut the integument into are the same size as cells,
    # which is exactly how they ended up coloured as tissue.
    in_seed = seed[cent[:, 0].astype(int), cent[:, 1].astype(int)]
    is_cell = in_seed & (areas <= (10 * UP) ** 2) & (areas >= (1.2 * UP) ** 2)
    cells = np.isin(lab, ids[is_cell])

    # Now the nucellus is wherever those cells are.
    nucellus = fill_holes(main_body(close(cells, 3 * UP)))

    # THE EMBRYO SAC, by where it is rather than by how big its cells are. An
    # earlier version took the largest cells and got the gaps between the
    # leader lines instead. The position was measured off this plate: a third of
    # the nucellus wide, just under half its height, sitting BELOW the middle,
    # which is what puts the egg apparatus at the micropylar end.
    ny, nx = np.nonzero(nucellus)
    ncy, ncx = (ny.min() + ny.max()) / 2, (nx.min() + nx.max()) / 2
    nh, nw = ny.max() - ny.min(), nx.max() - nx.min()
    inside = is_cell & ((((cent[:, 1] - (ncx - 0.04 * nw)) / (0.21 * nw)) ** 2
                         + ((cent[:, 0] - (ncy + 0.16 * nh)) / (0.27 * nh)) ** 2) <= 1.0)
    sac = np.isin(lab, ids[inside])

    # THE SAC IS THE ONE THING THAT IS DRAWN, and it is the only part of this
    # figure that is. Its POSITION AND SIZE still come from the plate — the
    # ellipse below is fitted to the cells just found — but at 320 pixels of
    # source the seven cells inside it are three pixels each, and tracing them
    # gave a torn blob with staircase edges that read as damage rather than as
    # an embryo sac. It is also the one structure a student has to be able to
    # reproduce in the exam, so it is drawn to the classical layout instead:
    # egg apparatus at the micropylar end, which on this plate is the BOTTOM,
    # two polar nuclei at the middle, three antipodals at the chalazal end.
    # Sized against the NUCELLUS, not against the cells that were detected. The
    # detection ellipse is deliberately generous — it has to catch every cell of
    # the sac — so fitting the drawing to what it caught made a sac 52% of the
    # nucellus wide where the plate draws about 35%, and it crowded out the
    # tissue either side of it.
    sac_c = (ncx - 0.05 * nw, ncy + 0.16 * nh)
    sac_r = (0.175 * nw, 0.25 * nh)
    yy, xx = np.mgrid[0:h, 0:w]
    sac_area = ((((xx - sac_c[0]) / sac_r[0]) ** 2
                 + ((yy - sac_c[1]) / sac_r[1]) ** 2) <= 1.0)

    # A CLEAN INTERIOR. The nucellus was closed out of the cell mass, so its
    # edge is a staircase of square steps; the cells carry the scan's crumbs as
    # extra fragments between them. Blurring and re-thresholding settles both,
    # the same way it settles the outline.
    # Closed BEFORE it is blurred. Blurring lifts a bump off an edge but it
    # cannot fill a notch, and the nucellus had a deep square hook cut into its
    # bottom right where a leader had crossed the base — no amount of smoothing
    # touched it. Closing fills a concavity and leaves the convex outline alone,
    # which is exactly the right way round for this shape.
    nucellus = close(nucellus, 4 * UP)
    nucellus = ndi.gaussian_filter(nucellus.astype(float), 2.0 * UP) > 0.5
    cells = cells & ~ndi.binary_dilation(sac_area, np.ones((UP, UP)))
    cl, cn = ndi.label(cells)
    keep = []
    for i, o in enumerate(ndi.find_objects(cl), 1):
        dh, dw = o[0].stop - o[0].start, o[1].stop - o[1].start
        # Crumbs are not cells, and neither is a long bar. Where the plate's
        # walls are faint — along the base of the nucellus especially — several
        # cells run together into one shape three or four times longer than it
        # is wide, and it prints as a pale streak lying across the tissue.
        if (cl[o] == i).sum() < (2.6 * UP) ** 2:
            continue
        if max(dh, dw) / max(min(dh, dw), 1) > 3.0:
            continue
        keep.append(i)
    cells = np.isin(cl, keep)
    cells = ndi.gaussian_filter(cells.astype(float), 0.4 * UP) > 0.5
    # Held INSIDE the nucellus by a clear margin. The cells defined the nucellus
    # in the first place, but smoothing its edge into an oval moves it, and any
    # cell the smoothing left outside stays drawn — one of them hung off the
    # bottom right like a blister. Keeping them a wall's width inside also gives
    # the tissue a clean rim instead of cells running into the boundary.
    cells = cells & ndi.binary_erosion(nucellus, np.ones((2 * UP, 2 * UP)))

    # THE TWO INTEGUMENTS, split by PROPORTION rather than by a fixed distance.
    # A shell of even thickness cannot do this job: the coat is about 150 pixels
    # deep on the right of the ovule and more than twice that over the top, so
    # any one thickness is either a hairline down one side or most of the coat
    # down the other. Both integuments are drawn a comparable share of the coat
    # on the plate, so the split is made a comparable share here — for every
    # point in the coat, how far it lies between the nucellus and the outside.
    #
    # Collecting the inner one as "the enclosed areas that touch the nucellus",
    # which is what the plate literally shows, does not survive the leaders:
    # they cut the annulus into four pieces of very different sizes and closing
    # those back together left a lopsided patch with straight edges down one
    # side.
    coat = sil & ~nucellus
    d_in = ndi.distance_transform_edt(~nucellus)     # out from the nucellus
    d_out = ndi.distance_transform_edt(sil)          # in from the outer surface
    ring = coat & (d_in <= 0.42 * (d_in + d_out))
    ring = ndi.gaussian_filter(ring.astype(float), 0.6 * UP) > 0.5

    dark = close((a < 100) & sil & ~nucellus, UP // 2)
    kb = np.ones((5 * UP // 2, 5 * UP // 2))
    # GROW THE CORE BACK, BUT ONLY AS FAR AS THE EROSION TOOK IT. Unbounded
    # reconstruction does not work here: the plate has a genuinely dark, genuinely
    # thick patch at the base of the nucellus, every leader touches the nucellus
    # outline, and the whole lot is one connected component — so the patch seeded
    # it and the growth ran out along all nine leaders at full length, putting the
    # grid of dark bars back over the right-hand integument for the third time.
    # Dilating the core a fixed distance inside the mask restores the band's true
    # width and lets a leader gain only those few pixels.
    seed_band = ndi.binary_erosion(dark, kb)
    grown = ndi.binary_dilation(seed_band, np.ones((3, 3)), iterations=2 * UP,
                                mask=dark)
    # What is left that is still not the strand is short. The band runs the whole
    # funicle; nothing else in the figure is forty source pixels long.
    # The plate fills this band solid; the white flecks through it are the scan,
    # and left in they read as a damaged vessel rather than a vascular strand.
    # ONE BAND, NOT THREE. What survives here is the funicle's bundle plus two
    # fragments: a detached lump high in the integument, where the plate's pen
    # ran light for twenty source pixels and broke the band in two, and a clot
    # under the nucellus that is dense drawing rather than vascular tissue.
    # Both read as stains on a flat green field. The gap in the first cannot be
    # bridged without inventing the missing stretch, so the bundle we can
    # actually follow is the one that gets drawn.
    strand = fill_holes(main_body(despeck(grown, diag=40 * UP)))
    strand = ndi.gaussian_filter(strand.astype(float), 0.9 * UP) > 0.5

    # THE MICROPYLE, cut as a canal. The plate shows it as a passage through the
    # coat at the base, and the figure had nothing there at all — the label
    # pointed at flat tissue, so it did not read as a way in. It runs from the
    # base of the nucellus straight out through the coat, widening as it goes,
    # the way a textbook draws it.
    col = np.nonzero(sil[:, int(ncx)])[0]
    outer = int(col[col > ny.max()].max()) if (col > ny.max()).any() else h - 1
    wt, wb = 0.042 * nw, 0.066 * nw
    # Cut a generous wedge and CLIP IT TO THE COAT. Ending it at the outer
    # surface by arithmetic does not work: the base is a slope, so a canal wide
    # enough to read poked out through the low side and hung in the background
    # like a peg. Intersecting with the silhouette makes its mouth exactly the
    # ovule's own edge, which is what an opening should look like.
    micro = raster([(ncx - wt, ny.max() - 0.015 * nh), (ncx - wb, outer + 0.05 * nh),
                    (ncx + wb, outer + 0.05 * nh), (ncx + wt, ny.max() - 0.015 * nh)],
                   (h, w)) & sil

    band = ribbon(strand, 6.0 * UP)
    strand = raster(band, (h, w))

    if debug:
        rgb = np.zeros(a.shape + (3,), np.uint8)
        rgb[sil] = (215, 235, 175)
        rgb[ring] = (250, 220, 120)
        rgb[nucellus] = (190, 215, 150)
        rgb[cells] = (120, 190, 90)
        rgb[micro] = (255, 150, 60)
        rgb[sac_area] = (255, 200, 200)
        rgb[sac] = (255, 90, 90)
        rgb[strand] = (60, 60, 200)
        Image.fromarray(rgb).save("ovule_debug.png")

    with tempfile.TemporaryDirectory() as td:
        # The ring and the nucellus are smoothed; the cells are NOT. At ten
        # source pixels across a cell is the same size as the speckle, and
        # smoothing rounds every one of them into a bead.
        d_sil = smooth_outline(trace(sil, td, "sil", "1.334", "3"), SIL_SMOOTH)
        d_ring = trace(smooth(ring, UP // 2), td, "ring")
        d_nuc = trace(smooth(nucellus, UP // 2), td, "nuc")
        d_micro = trace(micro, td, "micro")
        d_cells = trace(cells, td, "cells", "1.2")

    def layer(d, fill, stroke=None):
        if not d:
            return ""
        st = f' stroke="{INK}" stroke-width="{stroke * 10}"' if stroke else ' stroke="none"'
        return f'<path d="{d}" fill="{fill}" fill-rule="evenodd"{st}/>'

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}"
     width="{w}" height="{h}">
  <defs>
    <linearGradient id="coat" x1="0.1" y1="0" x2="0.95" y2="0.25">
      <stop offset="0" stop-color="{C_OUTER}"/>
      <stop offset="1" stop-color="{C_OUTER2}"/>
    </linearGradient>
  </defs>
  <!-- POTRACE'S OWN SPACE: it emits TENTHS of a pixel with Y pointing up, so
       every path is scaled by 0.1 and flipped about the height, and every
       stroke width is multiplied by ten to survive it. Leave the tenth out and
       the figure lands ten times too big, off the canvas, and the file renders
       as nothing at all. -->
  <g transform="translate(0,{h}) scale(0.1,-0.1)" stroke-linejoin="round">
    {layer(d_sil, "url(#coat)", 2.5)}
    {layer(d_ring, C_GROUND, 2.0)}
    {layer(d_nuc, C_NUCEL, 2.0)}
    {layer(d_micro, C_CELL, 2.0)}
    {layer(d_cells, C_CELL, 1.6)}
  </g>
  <!-- The sac, in plain figure pixels. It is NOT inside the group above: those
       paths live in potrace's flipped tenths, and an ellipse written there
       comes out upside down and ten times too big. -->
  <g stroke="{INK}" stroke-linejoin="round">
    <path d="{poly_path(band)}" fill="{C_VASC}" stroke-width="{0.003 * (w + h):.1f}"/>
{embryo_sac(sac_c, sac_r)}
  </g>
</svg>
'''
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(svg, encoding="utf-8")
    anchors(out, w, h, sil, nucellus, sac_area, strand, ring, micro)
    print(f"  {out}   crop={box} -> {w}x{h}")
    print(f"  cells={int(is_cell.sum())}  sac={int(inside.sum())}  "
          f"ring={ring.sum()//UP**2}px  strand={strand.sum()//UP**2}px")


if __name__ == "__main__":
    main()
