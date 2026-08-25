"""Turn the textbook scan of a question into a vector figure Manim can draw.

    python tools/figure_from_scan.py inbox/scans/che-c1-la-01.png \
        --crop 398,150,700,400 \
        --erase 498,152,570,178 --erase 565,189,638,210 \
        --out projects/che-c1-la-01/assets/figures/berkeley

Every PYQ row carries a Mathpix scan of the book page it was extracted from
(column 11 of the sheet). That scan holds the figure the student will actually
meet in the exam, and the answer they are expected to reproduce — so the figure
in the video should BE that figure, not an artist's impression of it.

Generating the figure from a description does not work. Three separate attempts
at the Berkeley-Hartley apparatus each produced a plausible piece of apparatus
that was not the one in the book: the book draws it as double-line pipework with
two solid bars for the membrane walls, a piston shaped like a cup that the
pressure arrow lands inside, and the gauge hanging off the piston neck by its own
pipe. A model asked for "the Berkeley-Hartley apparatus" invents a different
arrangement every time, and a student comparing it against the book sees two
different machines.

So the figure is traced, not drawn. The scan is thresholded and run through
potrace, which gives an SVG of the book's own ink. Manim loads that SVG directly,
which means the exact printed figure can be animated line by line.

The scanned LABELS are erased before tracing, and re-typeset in Poppins over the
result: at scan resolution the book's Devanagari traces to blobs, and blurry
labels on a sharp drawing look like a mistake. Leader lines are NOT erased — they
belong to the drawing, and re-typeset labels sit at their far ends.

Needs `potrace` (brew install potrace).
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps

# Chosen against the Berkeley scan: 118 keeps the thin pipe lines continuous
# while stopping the strokes from merging into blobs, and 7x gives potrace enough
# pixels to round the corners instead of stepping them.
THRESHOLD = 118
UPSCALE = 7
TURDSIZE = 6            # drop specks smaller than this (paper grain, JPEG dirt)



def _measure(im: Image.Image, box: tuple[int, int, int, int],
          cut: int = 150) -> list:
    """Reconnect strokes that an erase box cut through.

    The boiling-point graph labels its two curves by writing विलायक and विलयन
    ALONG them. Those words trace to solid blobs, so they have to be erased and
    re-typeset — but the curve runs through the same box, and erasing left a
    visible gap in the middle of the line the whole figure is about.

    So the columns just outside each edge are sampled, the black runs found
    there are paired in order, and each pair is joined across the gap. A curve
    is locally straight over a word's width, so a straight join is invisible.
    """
    x0, y0, x1, y1 = box
    px = im.load()
    w, h = im.size
    pad = 8

    def runs(x):
        out, start = [], None
        if not (0 <= x < w):
            return out
        for y in range(max(0, y0 - pad), min(h, y1 + pad)):
            dark = px[x, y] < cut
            if dark and start is None:
                start = y
            elif not dark and start is not None:
                out.append((start + y - 1) // 2); start = None
        if start is not None:
            out.append((start + min(h, y1 + pad) - 1) // 2)
        return out

    lx, rx = max(0, x0 - 2), min(w - 1, x1 + 2)
    left, right = runs(lx), runs(rx)
    # `cut` has to match what the tracer will treat as ink. Sampling at <128 on
    # the raw scan found nothing at all on the boiling-point curves — they sit
    # around 150 grey — so every heal silently no-opped and the gaps shipped.
    if not left or not right or len(left) != len(right):
        return []                   # ambiguous — leave the gap rather than invent
    return [((lx, ly), (rx, ry)) for ly, ry in zip(left, right)]


def trace(scan: Path, crop: tuple[int, int, int, int],
          erase: list[tuple[int, int, int, int]], out: Path,
          *, threshold: int = THRESHOLD, upscale: int = UPSCALE,
          heal: bool = False) -> Path:
    """Crop `scan` to the figure, erase label text, and trace it to SVG."""
    im = Image.open(scan).convert("L")
    d = ImageDraw.Draw(im)
    for box in erase:
        crossings = _measure(im, box) if heal else None
        d.rectangle(box, fill=255)
        if crossings:
            dd = ImageDraw.Draw(im)
            for (lx, ly), (rx, ry) in crossings:
                dd.line([(lx, ly), (rx, ry)], fill=0, width=4)

    fig = im.crop(crop)
    # The crop as the book prints it, kept before thresholding throws the greys
    # away. Manim wants the trace; Google Flow wants this. A Veo generation is
    # given it as a reference so the apparatus it animates is the one the student
    # revises from — see `reference_for` in src/veo_prompts.py — and for that job
    # the shading and line weight are most of the signal, so the traced version
    # is a poor substitute even though it is the same ink.
    #
    # Saved from the ERASED image, deliberately: the labels are typeset over the
    # clip afterwards in Poppins, and a scan with Devanagari still on it is a
    # picture of text handed to a tool that must not draw text.
    scan_ref = out.with_name(out.stem + "_scan.png")
    scan_ref.parent.mkdir(parents=True, exist_ok=True)
    fig.save(scan_ref)

    fig = fig.resize((fig.width * upscale, fig.height * upscale), Image.LANCZOS)
    fig = ImageOps.autocontrast(fig, cutoff=1)
    bw = fig.point(lambda p: 0 if p < threshold else 255, mode="1")

    out.parent.mkdir(parents=True, exist_ok=True)
    pbm = out.with_suffix(".pbm")
    bw.save(pbm)
    svg = out.with_suffix(".svg")
    subprocess.run(["potrace", "-s", "-o", str(svg), "--turdsize", str(TURDSIZE),
                    "--alphamax", "1.0", "--opttolerance", "0.2", str(pbm)],
                   check=True)
    pbm.unlink()
    return svg


def preview(svg: Path, width: int = 1400) -> Path:
    """Rasterise the SVG so the figure can be eyeballed before it is used."""
    import cairosvg
    png = svg.with_name(svg.stem + "_preview.png")
    cairosvg.svg2png(url=str(svg), write_to=str(png),
                     output_width=width, background_color="white")
    return png


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("scan", type=Path)
    ap.add_argument("--crop", required=True,
                    help="x0,y0,x1,y1 of the figure inside the scan")
    ap.add_argument("--erase", action="append", default=[],
                    help="x0,y0,x1,y1 of a label to remove; repeatable")
    ap.add_argument("--out", required=True, type=Path,
                    help="output path without extension")
    ap.add_argument("--threshold", type=int, default=THRESHOLD)
    ap.add_argument("--heal", action="store_true",
                    help="rejoin strokes an erase box cuts through")
    ap.add_argument("--labels", type=Path,
                    help="JSON of {name: [x, y, text, anchor]} in figure fractions")
    args = ap.parse_args()

    box = lambda s: tuple(int(v) for v in s.split(","))  # noqa: E731
    svg = trace(args.scan, box(args.crop), [box(e) for e in args.erase],
                args.out, threshold=args.threshold, heal=args.heal)
    png = preview(svg)
    print(f"{svg}  ({svg.stat().st_size // 1024} KB)")
    print(f"{png}  <- check this before rendering")
    scan_ref = args.out.with_name(args.out.stem + "_scan.png")
    if scan_ref.is_file():
        print(f"{scan_ref}  <- the book's own picture, for `reference:` on a Veo beat")

    if args.labels and args.labels.is_file():
        dest = svg.with_name(svg.stem + "_labels.json")
        dest.write_text(args.labels.read_text(encoding="utf-8"), encoding="utf-8")
        print(dest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
