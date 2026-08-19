#!/usr/bin/env python3
"""Stage 1b — typeset a chapter's blocks into page mock-ups. ZERO API calls.

    typeset_mockup.py Hindi-Ch7
      -> notes/Hindi-Ch7/mockups/page-NN.png   the blueprint shown to the image model
      -> notes/Hindi-Ch7/plans.json            per-page tagged content for the text prompt
      -> notes/Hindi-Ch7/rows.json             what landed on which row (debugging)

The mock-up is TYPED on a BLANK WHITE PAGE — it is a blueprint, not a style reference. The
handwriting style comes from separate anchor images at Stage 2, and the real notebook paper is
what actually gets written on. Anything that looks like paper furniture (margin rules, tint)
would only confuse the model about what it is copying, so the blueprint carries none of it.

GEOMETRY (measured off the approved page-01 render — BUILD_PROMPT §2.1, never guessed):
    page            1024 x 1536
    row pitch       46.7 px, 28 usable rows
    body text x     85, ragged right edge stops at 990
    wrapped indent  118 (a wrapped point aligns under its text, not under its marker)
FONT (calibrated per §2.2 against a measured 900 px line on the same page):
    Devanagari Sangam MN 36px -> 895 px for that line (0.6% off)

Text measurement and rasterising both go through Chromium, because Devanagari needs complex
shaping (matra reordering and conjuncts). Pillow has no libraqm here, so it would render the
script wrongly and every line break would be wrong with it.

Determinism: layout depends only on the blocks and a fixed seed, so a rebuild is byte-identical
and Stage 2 can redraw only the pages that actually changed.
"""
from __future__ import annotations

import base64
import hashlib
import io
import os
import json
import random
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageFilter, ImageOps
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
NOTES = HERE.parent / "notes"

W, H = 1024, 1536
PITCH = 43.0              # tightened from 46.7 on request: rows sit a little closer
ROW0_BASE = 193.0          # baseline of the first body row
USABLE = 30               # ...so two more rows fit before the foot of the sheet
TEXT_X = 85
RIGHT_X = 990
INDENT_X = 132   # wrapped point text; leaves room for a "12." marker
BULLET_X = 88
FIG_MIN_ROWS = 4
FIG_MAX_ROWS = 15          # a figure may grow into a page's leftover rows
# How strongly the line-art guide is shown. Crisp line art is best for label accuracy, but on
# anatomy figures it can trip the image API's OUTPUT moderation filter (Ch2 page-02 was rejected
# three times as [sexual] once the figure sharpened). Lower this for those pages and re-typeset.
GHOST_OPACITY = float(os.environ.get("GHOST_OPACITY", "0.55"))

FONT = "Devanagari Sangam MN"

# Superscripts and subscripts (32-P, 15-N, I^A, F_1, CO_2, N_t+1) must come from ONE font or they
# come out mismatched. Devanagari Sangam MN happens to carry the Latin-1 trio -- ^1 ^2 ^3 -- but
# none of the others, so a plain fallback list is not enough: "35" rendered as a small 3 from the
# primary next to a big 5 from whatever Chromium picked, which reads as "3 5". A unicode-range
# face pinned to Verdana takes ALL of these codepoints away from the primary font, so a run is
# uniform. It claims only those ranges, so every other glyph still resolves to FONT and the line
# breaks of already-drawn chapters are untouched.
SCRIPT_FONT = "MockupScripts"
FONT_STACK = f'"{SCRIPT_FONT}","{FONT}"'
FACE_CSS = (f"@font-face{{font-family:'{SCRIPT_FONT}';src:local('Verdana');"
            "unicode-range:U+00B2-00B3,U+00B9,U+2070-209F,U+02B0-02FF,U+1D2C-1D6B;}")

SIZE_BODY = 36
SIZE_HEAD = 36
SIZE_TITLE = 40
INK_BLUE = "#26307a"
INK_BLACK = "#000000"      # a TRUE black: at #2c2826 it read as the same dark pen as the body
                           # blue in the blueprint, so the model wrote headings in blue

# Hand-drift, applied per row and per word. Deterministic (seeded per page), so a rebuild is
# byte-identical and Stage 2 only redraws pages that really changed.
# Jitter budget. This is the BLUEPRINT, not the finished page: the un-uniformity of the hand comes
# from IMAGE 2 and the prompt, so the blueprint only needs enough drift to stop the model laying the
# rows out like a printed book. Drift bought at the price of legibility is a bad trade — two rows
# that close on each other are exactly where the model starts guessing letters and dropping matras.
# Worst case, two neighbouring rows can close by JIT_Y*2 + slope-rise*2; that must stay well inside
# PITCH (43) with the 36px glyphs.
JIT_ROW_X = (-7.0, 8.0)    # where a row starts — costs nothing vertically
JIT_Y = (-3.5, 3.5)        # a row sits above or below its nominal height
JIT_SLOPE = (-0.40, 0.40)  # degrees: the row climbs or sags across the page (±6px over 900px)
JIT_WORD_Y = (-3.0, 3.0)   # a word rides high or low within its own row
BOX_FOOT = 20.0            # clearance under the last baseline inside a <<BOX>> rule
FIG_THRESH = 150           # grey level below which a figure pixel counts as ink (see line_art)

# Per-figure escape hatch, keyed "<chapter>/<file>". The global value is tuned and load-bearing
# (see the note in line_art), so a single awkward source figure must never be fixed by moving it.
# UP-Ch5/fig-03 is a stylised web graphic — saturated colour fills with near-WHITE grey labels —
# so at 150 its lettering never enters the guide at all and preflight measures 1.09% ink.
FIG_THRESH_OVERRIDE = {
    "UP-Ch5/fig-03.jpg": 210,
}

# Fraction of a figure's HEIGHT to cut off the top before anything else. strip_header() finds a
# printed running header only on the pale textbook scans it was tuned for; a web graphic with
# WHITE lettering on a BLACK ground defeats it entirely. UP-Ch1/fig-01 carries its own bold title
# ("पराग कण के अंकुरण की प्रक्रिया") baked into the image, and the model dutifully copied it into
# the page's header band — which must stay bare on a continuation page. Cut the title, not the
# behaviour: with nothing to copy there is nothing to forbid.
FIG_CROP_TOP = {
    "UP-Ch1/fig-01.jpg": 0.08,
    "UP-Ch1/fig-02.jpg": 0.1,
    "UP-Ch1/fig-03.png": 0.09,
    "UP-Ch1/fig-04.png": 0.20,
    "UP-Ch2/fig-02.jpg": 0.04,
    "UP-Ch2/fig-03.jpg": 0.2,
    "UP-Ch4/fig-01.jpg": 0.11,
    "UP-Ch4/fig-02.jpg": 0.07,
    "UP-Ch5/fig-01.png": 0.10,
    "UP-Ch5/fig-02.jpg": 0.06,
    "UP-Ch6/fig-01.jpg": 0.05,
    "UP-Ch7/fig-01.png": 0.07,
    "UP-Ch9/fig-02.jpg": 0.08,
    "UP-Ch11/fig-01.jpg": 0.12,
}

# Same, off the BOTTOM. strip_caption() removes at most ONE short ink band, which is all a caption
# usually is — but some of these sources carry a whole printed legend block instead, several lines
# deep, and the model copies it as text inside the drawing.
FIG_CROP_BOTTOM = {
    "UP-Ch1/fig-04.png": 0.12,
    "UP-Ch1/fig-02.jpg": 0.03,
    "UP-Ch1/fig-03.png": 0.12,
    "UP-Ch2/fig-01.jpg": 0.12,
    "UP-Ch2/fig-03.jpg": 0.08,
    "UP-Ch2/fig-05.jpg": 0.26,
    "UP-Ch5/fig-01.png": 0.07,
    "UP-Ch5/fig-02.jpg": 0.08,
    "UP-Ch5/fig-03.jpg": 0.15,
    "UP-Ch6/fig-01.jpg": 0.08,
    "UP-Ch7/fig-01.png": 0.09,
    "UP-Ch9/fig-02.jpg": 0.2,
}

# Left/right crops, same keying. Several NCERT crops are multi-panel composites where only one
# panel is the figure we want, or carry a page-number block down one edge.
FIG_CROP_LEFT = {
    "UP-Ch1/fig-04.png": 0.05,
    "UP-Ch1/fig-02.jpg": 0.5,
}
FIG_CROP_RIGHT = {
    "UP-Ch1/fig-04.png": 0.02,
    "UP-Ch1/fig-02.jpg": 0.13,
    "UP-Ch2/fig-01.jpg": 0.12,
    "UP-Ch5/fig-01.png": 0.13,
    "UP-Ch5/fig-02.jpg": 0.28,
}

# Point a figure at a DIFFERENT source file. The imported figures are regenerated from the booklet
# by import_pyq.py, so a replacement copied over them would be silently undone on the next import;
# an override survives that. Paths are relative to the repo root.
REPO_ROOT = HERE.parent.parent.parent
FIG_SOURCE_OVERRIDE = {
    # Clean NCERT Hindi artwork replacing the booklet's embedded phone photos / dark web graphics.
    # Each was opened and confirmed to be the SAME figure before being listed here.
    "UP-Ch1/fig-02.jpg": "pulled_rj_biology/Hindi/Ch1/figures/Ch1_fig05.jpg",   # ovule — 4-panel composite, right panel
    "UP-Ch1/fig-03.png": "GPT-Notes/Hindi Hand/updated figures/WhatsApp Image 2026-08-18 at 15.10.25.jpeg",
    "UP-Ch1/fig-04.png": "GPT-Notes/Hindi Hand/updated figures/WhatsApp Image 2026-08-18 at 15.46.16.jpeg",
    "UP-Ch2/fig-01.jpg": "pulled_rj_biology/Hindi/Ch2/figures/Ch2_fig04.jpg",   # female tract
    "UP-Ch2/fig-02.jpg": "pulled_rj_biology/Hindi/Ch2/figures/Ch2_fig11.jpg",   # menstrual cycle
    "UP-Ch2/fig-03.jpg": "pulled_rj_biology/Hindi/Ch2/figures/Ch2_fig10.jpg",   # spermato/oogenesis
    "UP-Ch2/fig-04.jpg": "pulled_rj_biology/Hindi/Ch2/figures/mig01.jpg",       # ovary T.S.
    "UP-Ch2/fig-05.jpg": "pulled_rj_biology/Hindi/Ch2/figures/Ch2_fig02.jpg",   # male tract
    "UP-Ch5/fig-01.png": "pulled_rj_biology/Hindi/Ch5/figures/Ch5_fig05.jpg",   # Hershey-Chase
    "UP-Ch5/fig-02.jpg": "pulled_rj_biology/Hindi/Ch5/figures/Ch5_fig08.jpg",   # replication fork
    "UP-Ch6/fig-01.jpg": "pulled_rj_biology/Hindi/Ch6/figures/Ch6_fig01.jpg",   # Miller apparatus
    "UP-Ch7/fig-02.png": "pulled_rj_biology/Hindi/Ch7/figures/Ch7_fig02.jpg",   # antibody
    "UP-Ch9/fig-01.jpg": "GPT-Notes/Bio Ch9 BPP/figures/fig-04.png",  # pBR322
    "UP-Ch9/fig-02.jpg": "pulled_rj_biology/Hindi/Ch9/figures/Ch9_fig03.jpg",   # PCR
    "UP-Ch11/fig-01.jpg": "pulled_rj_biology/Hindi/Ch11/figures/Ch11_fig03.jpg",# growth curves
    "UP-Ch12/fig-02.jpg": "pulled_rj_biology/Hindi/Ch12/figures/Ch12_fig01.jpg",# trophic levels
}


# Reverse of FIG_SOURCE_OVERRIDE: a replacement file must still be crop/threshold-tuned under the
# LOGICAL slot it fills ("UP-Ch2/fig-01.jpg"), not under its own name in some other chapter.
LINE_ART_KEY = {str(REPO_ROOT / v): k for k, v in FIG_SOURCE_OVERRIDE.items()}


# Pin a figure to a FIXED row count. A replacement with a different aspect ratio takes a different
# number of rows, which reflows every page after it in the chapter — turning a 3-page fix into a
# whole-chapter re-render, at ~$0.10 a page. Pinning each replacement to the row count its
# predecessor occupied keeps the layout byte-identical, so ONLY the pages actually being corrected
# have to be drawn again.
FIG_ROWS_PIN = {
    "UP-Ch1/fig-02.jpg": 13,
    "UP-Ch1/fig-03.png": 8,
    "UP-Ch2/fig-01.jpg": 11,
    "UP-Ch2/fig-03.jpg": 10,
}


def fig_path(figures_dir: Path, src: str) -> Path:
    """Where a figure's pixels actually come from — the import, or a curated replacement."""
    key = f"{figures_dir.parent.name}/{Path(src).name}"
    over = FIG_SOURCE_OVERRIDE.get(key)
    return (REPO_ROOT / over) if over else (figures_dir / Path(src).name)


WRAP_W = RIGHT_X - TEXT_X
WRAP_W_IND = RIGHT_X - INDENT_X


def fig_rows(figures_dir: Path, src: str) -> int:
    """How many grid rows a figure gets: enough that it is drawn at a readable size."""
    pin = FIG_ROWS_PIN.get(f"{figures_dir.parent.name}/{Path(src).name}")
    if pin:
        return pin
    fp = fig_path(figures_dir, src)
    if not fp.exists():
        return 8
    with Image.open(fp) as im:
        w, h = strip_caption(ImageOps.autocontrast(im.convert("L"))).size
    full = (RIGHT_X - TEXT_X) * h / max(1, w)     # height if drawn the full column width
    return max(6, min(13, round(full / PITCH)))


def strip_caption(g: Image.Image) -> Image.Image:
    """Cut the printed caption band ("चित्र 4.16 …") off the bottom of a textbook figure.

    The prompt tells the model not to copy the caption, and it copies it anyway — it is printed
    text sitting inside the picture it is being asked to draw. Removing it from the guide is the
    only reliable fix. A caption is the bottom-most ink band that is SHORT (a line or two of small
    type) and SEPARATED from the drawing by clear white; anything taller is part of the figure and
    is left alone.
    """
    a = np.asarray(g, dtype=np.uint8)
    h = a.shape[0]
    bands = _ink_bands(a)
    if len(bands) < 2:
        return g
    # AT MOST ONE band is removed — the bottom-most. Walking further up eats real content: on the
    # pedigree-symbols figure every symbol row is itself short and well separated, and a greedy
    # walk took five of them off. One band is all a caption ever is.
    top, bot = bands[-1]
    gap = top - bands[-2][1]
    if not ((bot - top) <= 0.13 * h and gap >= 0.015 * h and top >= 0.55 * h):
        return g
    # A caption can run to a second line. Take it too ONLY when the two lines are packed tighter
    # than the space that separates them from the drawing — that ratio is what tells a wrapped
    # caption apart from the evenly-spaced rows of a symbol key.
    if len(bands) >= 3:
        ptop, pbot = bands[-2]
        pgap = ptop - bands[-3][1]
        if (pbot - ptop) <= 0.09 * h and gap < 0.6 * pgap and ptop >= 0.55 * h:
            top, gap = ptop, pgap
    return g.crop((0, 0, a.shape[1], top - max(2, gap // 3)))


def _ink_bands(a):
    """Horizontal bands of ink in a greyscale figure, with 1-2px scanner specks glued to their
    neighbours (left alone they masquerade as their own band and break the gap arithmetic)."""
    rowink = (a < 150).sum(1)
    on = rowink > max(2, rowink.max() * 0.01)
    bands, s = [], None
    for i, v in enumerate(on):
        if v and s is None:
            s = i
        elif not v and s is not None:
            bands.append((s, i))
            s = None
    if s is not None:
        bands.append((s, len(on)))
    merged = []
    for b in bands:
        if merged and b[0] - merged[-1][1] < 6:
            merged[-1] = (merged[-1][0], b[1])
        else:
            merged.append(b)
    return [b for b in merged if b[1] - b[0] > 2]


def strip_header(g: Image.Image) -> Image.Image:
    """Cut the textbook's RUNNING HEADER ("विकास", "जीव विज्ञान") off the top of a figure.

    Deliberately much stricter than strip_caption: a caption is reliably the bottom band, but the
    top band of a figure is usually real content. An earlier, looser version of this test would
    have deleted mig03's `नर` legend row and mig01's `क्रॉस A / क्रॉस B` header. So a band is only
    removed when it is ALL of: tiny (<=3.5% of height), narrow (<15% of the width — a header is one
    short word, a content row spans the figure), hard against the top edge, and clearly separated.
    Verified against all ten Ch4+Ch6 figures: strips the two running headers, touches nothing else.
    """
    a = np.asarray(g, dtype=np.uint8)
    h, w = a.shape
    bands = _ink_bands(a)
    if len(bands) < 2:
        return g
    top, bot = bands[0]
    gap = bands[1][0] - bot
    span = ((a[top:bot] < 150).any(0)).sum() / w
    if (bot - top) <= 0.035 * h and span < 0.15 and bot <= 0.10 * h and gap >= 0.02 * h:
        return g.crop((0, bot + max(2, gap // 3), w, h))
    return g


def line_art(path: Path) -> str:
    """Turn a printed textbook figure into pure LINE ART, as a data: URI.

    The source figures carry colour fills and stipple texture, and the model copies what it can
    see: every shaded diagram we shipped was it faithfully reproducing tone that was really in
    the guide. Prose ("no shading") loses that argument. So the tone is removed from the guide:
    solid regions are opened out and replaced by their OUTLINE, thin strokes and all label text
    are kept intact. Result is ~3% ink coverage with nothing to shade.
    """
    key = LINE_ART_KEY.get(str(path), f"{path.parent.parent.name}/{path.name}")
    with Image.open(path) as im:
        g = ImageOps.autocontrast(im.convert("L"))
        top = FIG_CROP_TOP.get(key, 0.0)
        bot = FIG_CROP_BOTTOM.get(key, 0.0)
        lft = FIG_CROP_LEFT.get(key, 0.0)
        rgt = FIG_CROP_RIGHT.get(key, 0.0)
        if top or bot or lft or rgt:
            g = g.crop((int(g.width * lft), int(g.height * top),
                        g.width - int(g.width * rgt),
                        g.height - int(g.height * bot)))
        g = strip_header(strip_caption(g))
    # ⚠️ THE THRESHOLD IS LOAD-BEARING. At 110 the printed MID-GREY line work never entered the
    # line art at all: Ch4 page-13's honeybee chart lost every arrow, circle and connector and
    # reached the model as a few floating labels in white space — so the model drew no figure.
    # Above ~160 the opposite failure returns: solid fills and stipple survive and get copied as
    # shading. 150 keeps the strokes and drops the tone.
    thr = FIG_THRESH_OVERRIDE.get(key, FIG_THRESH)
    dark = g.point(lambda v: 255 if v < thr else 0)
    blob = dark.filter(ImageFilter.MinFilter(7)).filter(ImageFilter.MaxFilter(7))
    thin = ImageChops.subtract(dark, blob)                       # strokes + labels
    edge = ImageChops.subtract(blob.filter(ImageFilter.MaxFilter(3)), blob)   # fills -> outlines
    out = ImageChops.invert(ImageChops.lighter(thin, edge))
    buf = io.BytesIO()
    out.convert("L").save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


def assert_glyphs(M, items) -> None:
    """Refuse to build a blueprint that would show a missing-glyph box.

    A super/subscript comes from the pinned face, and a codepoint that face does not carry is
    painted as .notdef -- a hollow rectangle -- which the image model then draws as a rectangle.
    Chromium gives every .notdef the same advance, so an unassigned codepoint is a reliable
    yardstick: a script glyph measuring exactly that wide is not really there.
    """
    used = {c for it in items if it.get("text") for c in it["text"]
            if 0x2070 <= ord(c) <= 0x209F or 0x02B0 <= ord(c) <= 0x02FF
            or 0x1D2C <= ord(c) <= 0x1D6B or ord(c) in (0xB2, 0xB3, 0xB9)}
    if not used:
        return
    notdef = M.width("￿")
    missing = sorted(c for c in used if abs(M.width(c) - notdef) < 0.01)
    if missing:
        raise SystemExit("cannot typeset: no glyph for " + " ".join(f"{c!r} U+{ord(c):04X}"
                                                                   for c in missing)
                         + "\n  the pinned face (FACE_CSS) does not carry it — widen its "
                           "unicode-range, pick another local() font, or drop it from SUP_MAP.")


class Measurer:
    """Text width oracle backed by Chromium's canvas, with a cache so runs stay cheap."""

    def __init__(self, page):
        self.page = page
        self.cache: dict[tuple[str, int, bool], float] = {}

    def width(self, text: str, size: int = SIZE_BODY, bold: bool = False) -> float:
        key = (text, size, bold)
        if key not in self.cache:
            self.cache[key] = self.page.evaluate(
                """([t,s,b,f])=>{const c=document.createElement('canvas').getContext('2d');
                   c.font=(b?'bold ':'')+s+'px '+f;return c.measureText(t).width;}""",
                [text, size, bold, FONT_STACK])
        return self.cache[key]

    def wrap(self, text: str, avail: float, size: int = SIZE_BODY, bold: bool = False):
        """Greedy word wrap to a pixel width. Returns a list of lines."""
        words, lines, cur = text.split(), [], ""
        for w in words:
            trial = f"{cur} {w}".strip()
            if cur and self.width(trial, size, bold) > avail:
                lines.append(cur)
                cur = w
            else:
                cur = trial
        if cur:
            lines.append(cur)
        return lines or [""]


# --------------------------------------------------------------------------- blocks -> rows
def rows_for_blocks(blocks, M, figures_dir: Path):
    """Flatten blocks into ROW items -- the pagination unit is the row, not the paragraph."""
    items = []

    def gap():
        # one blank row separates topics; two in a row is just a hole (BUILD_PROMPT §3.7)
        if items and items[-1]["t"] != "gap":
            items.append({"t": "gap"})

    for bi, b in enumerate(blocks):
        k = b["kind"]
        if k == "dropped":
            continue                          # declared front matter, deliberately not written
        if k == "title":
            for j, ln in enumerate(M.wrap(b["text"], WRAP_W, SIZE_TITLE, True)):
                items.append({"t": "line", "text": ln, "x": TEXT_X, "size": SIZE_TITLE,
                              "bold": True, "ink": INK_BLACK, "bid": bi, "tag": "TITLE",
                              "centre": True, "hard": j > 0})
            gap()
        elif k == "subhead":
            # A PYQ card is two black runs that belong hard against each other: the "प्र.N [year ·
            # marks · Nx]" strap and the question itself. A gap between them reads as two separate
            # headings, so a block may suppress the gap on either side. Notes blocks set neither
            # and keep the original behaviour.
            if not b.get("nogap_before"):
                gap()
            for j, ln in enumerate(M.wrap(b["text"], WRAP_W, SIZE_HEAD, True)):
                items.append({"t": "line", "text": ln, "x": TEXT_X, "size": SIZE_HEAD,
                              "bold": True, "ink": INK_BLACK, "bid": bi, "tag": "SUBHEAD",
                              "head": True, "hard": j > 0})
            if not b.get("nogap_after"):
                gap()
        elif k == "text":
            for ln in M.wrap(b["text"], WRAP_W):
                items.append({"t": "line", "text": ln, "x": TEXT_X, "size": SIZE_BODY,
                              "bold": False, "ink": INK_BLUE, "bid": bi, "tag": "TEXT"})
        elif k == "point":
            # a numeral is wider than a dot, so it needs more room before the text starts
            marker = f"{b['num']}." if b.get("num") else "•"
            lines = M.wrap(b["text"], WRAP_W_IND)
            for j, ln in enumerate(lines):
                items.append({"t": "line", "text": ln, "x": INDENT_X, "size": SIZE_BODY,
                              "bold": False, "ink": INK_BLUE, "bid": bi, "tag": "POINT",
                              "bullet": marker if j == 0 else None})
        elif k == "box":
            gap()
            lines = M.wrap(f"{b['label']} : {b['text']}", WRAP_W - 30)
            items.append({"t": "boxrect", "rows": len(lines), "bid": bi, "tag": "BOX",
                          "hard": True})
            for j, ln in enumerate(lines):
                items.append({"t": "line", "text": ln, "x": TEXT_X + 15, "size": SIZE_BODY,
                              "bold": False, "ink": INK_BLUE, "bid": bi, "tag": "BOX",
                              "box": ("open" if j == 0 else "mid") if j < len(lines) - 1 else "close",
                              "label": b["label"] if j == 0 else None, "hard": j > 0})
            gap()
        elif k == "table":
            gap()
            rows = b["rows"]
            ncol = max(len(r) for r in rows)
            colw = (RIGHT_X - TEXT_X) / ncol
            for ri, r in enumerate(rows):
                wrapped = [M.wrap(c, colw - 22, 30) for c in r]
                items.append({"t": "trow", "cells": r, "lines": wrapped, "ncol": ncol,
                              "colw": colw, "rows": max(len(w) for w in wrapped),
                              "bid": bi, "tag": "TABLE", "first": ri == 0,
                              "last": ri == len(rows) - 1, "hard": ri > 0})
            gap()
        elif k == "flow":
            gap()
            for si, st in enumerate(b["steps"]):
                items.append({"t": "step", "text": st["text"], "note": st.get("note", ""),
                              "bid": bi, "tag": "FLOW", "arrow": si < len(b["steps"]) - 1,
                              "hard": si > 0})
            # The flow's own caption was never emitted, so every flowchart caption in the source
            # was silently lost at this stage -- after the import gate had certified the text.
            # It is glued (hard) to the steps so a page break can never strand it from its chart.
            if b.get("caption"):
                items.append({"t": "line", "text": b["caption"], "x": TEXT_X, "size": SIZE_BODY,
                              "bold": False, "ink": INK_BLUE, "bid": bi, "tag": "TEXT",
                              "centre": True, "hard": True})
            gap()
        elif k == "mindmap":
            gap()
            if b.get("caption"):
                items.append({"t": "line", "text": b["caption"], "x": TEXT_X, "size": SIZE_HEAD,
                              "bold": True, "ink": INK_BLACK, "bid": bi, "tag": "SUBHEAD",
                              "head": True})
            for ni, n in enumerate(b["nodes"]):
                items.append({"t": "node", "text": n["text"], "note": n.get("note", ""),
                              "bid": bi, "tag": "MINDMAP", "first": ni == 0, "hard": ni > 0})
            gap()
        elif k == "fig":
            gap()
            # A fixed 8 rows squeezes a TALL figure into a narrow column — the pedigree-symbol key
            # came out 235px wide with labels the model could not read, so it invented them. Height
            # follows the figure's own aspect (capped) so a portrait figure gets the room it needs.
            items.append({"t": "fig", "src": b["src"], "rows": fig_rows(figures_dir, b["src"]),
                          "bid": bi, "tag": "FIG"})
            gap()
    while items and items[0]["t"] == "gap":
        items.pop(0)

    # A heading may never be the last thing on a sheet, and neither may a heading + its blank.
    # Glue the heading, the blank under it AND the first real row after it into one group, by
    # forbidding a page break immediately before any of them (BUILD_PROMPT §3.7).
    for i, it in enumerate(items):
        if not it.get("head"):
            continue
        j = i + 1
        while j < len(items) and items[j]["t"] == "gap":
            items[j]["hard"] = True
            j += 1
        if j < len(items):
            items[j]["hard"] = True
    return items


def row_height(it) -> int:
    if it["t"] == "boxrect":
        return 0                       # drawn behind its text rows; occupies no row itself
    if it["t"] == "trow":
        return it.get("rows", 1)
    if it["t"] in ("step", "node"):
        return 2
    return it.get("rows", 1) if it["t"] == "fig" else 1


# --------------------------------------------------------------------------- pagination
def paginate(items):
    """Backwards DP for the minimum sheet count, then a forward greedy fill (§3.8).

    Greedy packing -- deliberately NOT a squared-slack minimiser, which would spread blank rows
    evenly across every sheet instead of pushing the slack onto the last page.
    """
    n = len(items)
    INF = float("inf")
    minp = [INF] * (n + 1)
    minp[n] = 0
    for i in range(n - 1, -1, -1):
        used = 0
        for j in range(i, n):
            h = row_height(items[j])
            if used + h > USABLE:
                break
            used += h
            if items[j + 1]["hard"] if j + 1 < n and items[j + 1].get("hard") else False:
                continue                      # may not break immediately before a hard row
            if minp[j + 1] + 1 < minp[i]:
                minp[i] = minp[j + 1] + 1
    if minp[0] == INF:
        raise SystemExit("cannot paginate: a single block is taller than a page")

    pages, i = [], 0
    while i < n:
        used, best = 0, None
        for j in range(i, n):
            h = row_height(items[j])
            if used + h > USABLE:
                break
            used += h
            nxt = j + 1
            if nxt < n and items[nxt].get("hard"):
                continue
            if minp[nxt] + 1 == minp[i]:
                best = nxt                    # fullest break that keeps the minimum reachable
        if best is None:
            best = min(n, i + 1)
        pages.append(items[i:best])
        i = best
    # a page never opens or closes on a blank row
    out = []
    for pg in pages:
        while pg and pg[0]["t"] == "gap":
            pg.pop(0)
        while pg and pg[-1]["t"] == "gap":
            pg.pop()
        if pg:
            out.append(pg)
    # A box split across a page break keeps its rectangle only on the first page, so the
    # continuation page shows bare text and the model draws no box there. Give every page that
    # carries box lines its own rectangle, sized to the lines it actually holds.
    for pg in out:
        have = {r["bid"] for r in pg if r["t"] == "boxrect"}
        need = {}
        for r in pg:
            if r["t"] == "line" and r.get("tag") == "BOX" and r["bid"] not in have:
                need[r["bid"]] = need.get(r["bid"], 0) + 1
        for bid, n in need.items():
            at = next(i for i, r in enumerate(pg)
                      if r["t"] == "line" and r.get("tag") == "BOX" and r["bid"] == bid)
            pg.insert(at, {"t": "boxrect", "rows": n, "bid": bid, "tag": "BOX", "hard": True})

    # A box rectangle whose text was paginated onto the next page is an orphan: it draws an
    # empty rectangle on this sheet. Drop any rectangle with no box lines beside it.
    for pg in out:
        keep = []
        for r in pg:
            if r["t"] == "boxrect" and not any(
                    q["t"] == "line" and q.get("tag") == "BOX" and q["bid"] == r["bid"] for q in pg):
                continue
            keep.append(r)
        pg[:] = keep

    sweep_headings(out)

    # After the sweeps a page can be left nearly empty (e.g. a box whose heading group moved on).
    # If its rows fit entirely on the following page, merge them forward rather than ship a stub.
    merged = []
    i = 0
    while i < len(out):
        pg = out[i]
        if (i + 1 < len(out)
                and sum(row_height(r) for r in pg) + sum(row_height(r) for r in out[i + 1]) <= USABLE):
            out[i + 1] = pg + out[i + 1]
        else:
            merged.append(pg)
        i += 1
    out = merged

    out = balance_tail(out)
    # balance_tail moves rows off the second-to-last page, which can strand a heading there all
    # over again (Ch9 page-29 ended on "भाग 1 : सिद्धांत एवं उपकरण" with its mind map on the next
    # sheet). Sweep once more AFTER it, so the last thing done is the rule that must hold.
    sweep_headings(out)
    return [spread_slack(pg, last=(i == len(out) - 1)) for i, pg in enumerate(out)]


def sweep_headings(out):
    """A heading must never be the last thing on a sheet.

    The glue rule forbids breaking right after one, but the greedy paginator has a fallback break
    for when nothing else fits, and the tail balancer moves rows off a page after the fact; both
    can still strand a heading with its content on the next page. Push the whole heading forward.
    """
    for i in range(len(out) - 1):
        pg = out[i]
        tail = len(pg)
        while tail and pg[tail - 1]["t"] == "gap":
            tail -= 1
        if tail and pg[tail - 1].get("head"):
            j = tail - 1
            while j > 0 and pg[j - 1].get("head"):      # take the whole multi-row heading
                j -= 1
            moved, out[i] = pg[j:], pg[:j]
            out[i + 1] = [m for m in moved if m["t"] != "gap"] + out[i + 1]
            while out[i] and out[i][-1]["t"] == "gap":
                out[i].pop()


def balance_tail(pages):
    """Stop a chapter ending on a stub. A 3-row final page looks like a mistake, so shift whole
    rows back from the page before it until the two are comparably full."""
    if len(pages) < 2:
        return pages
    a, b = pages[-2], pages[-1]
    rows = lambda pg: sum(row_height(r) for r in pg)
    while len(a) > 1 and rows(b) < rows(a):
        moved = a[-1]
        if abs((rows(a) - row_height(moved)) - (rows(b) + row_height(moved))) >= abs(rows(a) - rows(b)):
            break
        a, b = a[:-1], [moved] + b
    while b and b[0]["t"] == "gap":
        b.pop(0)
    pages[-2], pages[-1] = a, b
    return pages


def spread_slack(pg, last: bool):
    """Push a page's leftover rows OUT as breathing space between blocks, not into a hole.

    When a group is moved to the next sheet to avoid orphaning a heading, the rows it leaves
    behind should widen the gaps between the topics that remain — otherwise the page just ends
    early and looks half-empty. The last page keeps its slack, as a chapter's tail should.
    """
    if last:
        return pg
    slack = USABLE - sum(row_height(r) for r in pg)
    if slack <= 0:
        return pg

    # 1. A figure is elastic: let it take the leftover rows rather than leave a hole beside it.
    for it in pg:
        if it["t"] == "fig" and slack > 0:
            grow = min(slack, FIG_MAX_ROWS - it["rows"])
            if grow > 0:
                it["rows"] += grow
                slack -= grow

    # 2. Widen the page at block boundaries that have no blank row yet.
    cands = [i for i in range(1, len(pg))
             if pg[i].get("bid") != pg[i - 1].get("bid")
             and pg[i]["t"] != "gap" and pg[i - 1]["t"] != "gap"
             and not pg[i].get("hard")]
    if cands and slack > 0:
        take = min(slack, len(cands))
        step = len(cands) / take
        chosen = sorted({cands[int(k * step)] for k in range(take)}, reverse=True)
        for i in chosen:
            pg.insert(i, {"t": "gap", "spread": True})
        slack -= len(chosen)

    # 3. Last resort: widen the blank rows that are already there, one extra row each. Two blank
    #    rows together are normally a hole, but they beat a page that stops short of the foot.
    if slack > 0:
        for i in range(len(pg) - 1, 0, -1):
            if slack <= 0:
                break
            if pg[i]["t"] == "gap" and not pg[i].get("wide"):
                pg[i]["wide"] = True
                pg.insert(i, {"t": "gap", "spread": True, "wide": True})
                slack -= 1
    return pg


# --------------------------------------------------------------------------- drawing
def page_html(pg, figures_dir: Path, seed: int) -> str:
    """One mock-up page as absolutely-positioned HTML on a blank white sheet."""
    rnd = random.Random(seed)
    out = []
    y = 0.0

    def base(r):
        return ROW0_BASE + PITCH * r

    for it in pg:
        t = it["t"]
        if t == "gap":
            y += 1
            continue
        jx = rnd.uniform(-7.0, 8.0)
        if t == "line":
            bx = it["x"] + jx
            if it.get("centre"):
                bx = None
            # Vertical drift and slope. The reference build forbids these because its sheet has
            # PRINTED RULES, and a word off its rule reads as a fault. This sheet is UNRULED, so
            # there is nothing to betray: a real hand's rows sag, climb and sit at their own
            # heights, and the blueprint has to show that or the drawn page comes back too even.
            jy = rnd.uniform(*JIT_Y)
            slope = rnd.uniform(*JIT_SLOPE)
            tf = f"transform:rotate({slope:.2f}deg);transform-origin:left center;"
            style = (f"top:{base(y) - it['size'] + jy:.1f}px;font-size:{it['size']}px;"
                     f"color:{it['ink']};{'font-weight:700;' if it['bold'] else ''}{tf}")
            # each WORD also rides a little high or low, so no row sits on one clean baseline
            words = "".join(
                f"<span style='position:relative;top:{rnd.uniform(*JIT_WORD_Y):.1f}px'>{w}</span> "
                for w in it["text"].split())
            if bx is None:
                out.append(f"<div class=r style='{style}left:0;width:{W}px;text-align:center'>"
                           f"{words}</div>")
            else:
                if it.get("bullet"):
                    # the marker carries its OWN offsets, so dots and numerals never form a
                    # perfect vertical column down the page (BUILD_PROMPT §3.10)
                    mjx, mjy = rnd.uniform(-5.0, 5.0), rnd.uniform(*JIT_Y)
                    out.append(f"<div class=r style='top:{base(y) - it['size'] + mjy:.1f}px;"
                               f"left:{BULLET_X + mjx:.1f}px;font-size:{it['size']}px;"
                               f"color:{it['ink']}'>{it['bullet']}</div>")
                out.append(f"<div class=r style='{style}left:{bx:.1f}px'>{words}</div>")
            y += 1
        elif t == "boxrect":
            # The rule must clear the LAST line inside it. Its baseline sits PITCH*(rows-1) below
            # the first, and under that baseline come the descenders plus the row/word jitter — so
            # a height of rows*PITCH lands the rule ON that last line and strikes the text through.
            # (That is what put a rule across "पर काम किया।" in the earlier blueprints.)
            top = base(y) - SIZE_BODY - 6
            bottom = base(y) + PITCH * (it["rows"] - 1) + BOX_FOOT
            out.append(f"<div style='position:absolute;left:{TEXT_X + 4}px;"
                       f"top:{top:.0f}px;width:{RIGHT_X - TEXT_X - 8}px;"
                       f"height:{bottom - top:.0f}px;border:2px solid #444'></div>")
            continue
        elif t == "trow":
            span = it.get("rows", 1)
            for ci, lines in enumerate(it.get("lines") or [[c] for c in it["cells"]]):
                for li, ln in enumerate(lines):
                    out.append(f"<div class=r style='top:{base(y + li) - SIZE_BODY:.1f}px;"
                               f"left:{TEXT_X + 8 + ci * it['colw']:.1f}px;"
                               f"font-size:30px;color:{INK_BLUE}'>{ln}</div>")
            out.append(f"<div style='position:absolute;left:{TEXT_X}px;"
                       f"top:{base(y + span - 1) + 6:.1f}px;width:{RIGHT_X - TEXT_X}px;"
                       f"border-bottom:2px solid #444'></div>")
            y += span
        elif t == "step":
            # Parentheses, NOT an em-dash: plan_for() writes this note as "(note)" in the prompt,
            # so a dash here showed the model one thing and told it another. It resolved the
            # conflict by opening a bracket it never closed — 9 pages of Ch5 shipped with
            # "न्यूक्लियोसोम (~200 क्षार युग्म" and no ")". The two must agree.
            note = (f"<small style='font-size:22px'> ({it['note']})</small>") if it["note"] else ""
            out.append(f"<div style='position:absolute;left:{TEXT_X + 60 + jx:.0f}px;"
                       f"top:{base(y) - 34:.1f}px;padding:4px 12px;border:2px solid #444;"
                       f"font-size:30px;color:{INK_BLUE}'>{it['text']}{note}</div>")
            if it["arrow"]:
                out.append(f"<div class=r style='left:{TEXT_X + 90:.0f}px;top:{base(y) + 8:.1f}px;"
                           f"font-size:28px;color:#444'>&#8595;</div>")
            y += 2
        elif t == "node":
            # Parentheses, NOT an em-dash: plan_for() writes this note as "(note)" in the prompt,
            # so a dash here showed the model one thing and told it another. It resolved the
            # conflict by opening a bracket it never closed — 9 pages of Ch5 shipped with
            # "न्यूक्लियोसोम (~200 क्षार युग्म" and no ")". The two must agree.
            note = (f"<small style='font-size:22px'> ({it['note']})</small>") if it["note"] else ""
            out.append(f"<div style='position:absolute;left:{TEXT_X + 40 + jx:.0f}px;"
                       f"top:{base(y) - 34:.1f}px;padding:3px 10px;border:2px solid #444;"
                       f"border-radius:2px;font-size:29px;color:{INK_BLUE};"
                       f"max-width:{RIGHT_X - TEXT_X - 60}px'>{it['text']}{note}</div>")
            out.append(f"<div style='position:absolute;left:{TEXT_X + 12}px;"
                       f"top:{base(y) - 30:.0f}px;width:26px;height:2px;background:#444'></div>")
            y += 2
        elif t == "fig":
            fp = fig_path(figures_dir, it["src"])
            h = it["rows"] * PITCH
            if fp.exists():
                # full-width box + contain: a portrait figure is centred in the column instead of
                # being pinned to the left with a lake of blank paper beside it
                out.append(f"<img src='data:image/png;base64,{line_art(fp)}' style='position:absolute;"
                           f"left:{TEXT_X}px;top:{base(y) - SIZE_BODY:.0f}px;width:{RIGHT_X - TEXT_X}px;"
                           f"height:{h:.0f}px;object-fit:contain;opacity:{GHOST_OPACITY}'>")
            else:
                out.append(f"<div style='position:absolute;left:{TEXT_X}px;"
                           f"top:{base(y) - SIZE_BODY:.0f}px;width:{RIGHT_X - TEXT_X}px;height:{h:.0f}px;"
                           f"border:2px dashed #999;color:#999;font-size:26px'>[figure]</div>")
            y += it["rows"]
    return (f"<html><body style='margin:0;width:{W}px;height:{H}px;background:#fff;"
            f"font-family:{FONT_STACK}'>"
            f"<style>{FACE_CSS}.r{{position:absolute;white-space:nowrap}}</style>"
            + "".join(out) + "</body></html>")


def plan_for(pg) -> str:
    """The tagged, logically-rejoined content for this page (§3.12)."""
    lines, buf, tag = [], [], None

    def flush():
        nonlocal buf, tag
        if buf:
            lines.append(f"<<{tag}>> " + " ".join(buf))
            buf = []

    for it in pg:
        if it["t"] == "gap":
            flush(); lines.append("<<GAP>>")
        elif it["t"] == "line":
            if it["tag"] != tag or it.get("bullet") or it.get("centre"):
                flush(); tag = it["tag"]
            # The blueprint draws a numbered point's marker as "5.", but the prompt used to say
            # only <<POINT>>, so the model wrote a bullet and the numbering was lost (Ch5 pages
            # 14/29/30/35/36 ran "1, •, 3, 4"). Carry the numeral into the text it belongs to.
            mark = it.get("bullet")
            if mark and mark != "•" and not buf:
                buf.append(mark)
            buf.append(it["text"])
        elif it["t"] == "trow":
            flush(); tag = None
            lines.append(("[[TABLE hand-ruled, %d columns]]" % it["ncol"]) if it["first"] else "")
            lines.append("Row: " + " | ".join(it["cells"]))
        elif it["t"] == "node":
            flush(); tag = None
            if it.get("first"):
                lines.append("[[MINDMAP hand-drawn, one small box per item, joined to a spine]]")
            lines.append(f"Item: {it['text']}" + (f" ({it['note']})" if it["note"] else ""))
        elif it["t"] == "step":
            flush(); tag = None
            lines.append(f"Step: {it['text']}" + (f" ({it['note']})" if it["note"] else "")
                         + ("  ↓" if it["arrow"] else ""))
        elif it["t"] == "fig":
            flush(); tag = None
            lines.append(f"[[DIAGRAM {Path(it['src']).name}]]")
    flush()
    return "\n".join(l for l in lines if l != "")


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    key = sys.argv[1]
    root = NOTES / key
    data = json.loads((root / "blocks.json").read_text(encoding="utf-8"))
    figures_dir = Path(data["figures_dir"])

    # Clear old mock-ups first: a re-typeset can produce FEWER pages, and a stale page-NN.png
    # left behind would be rendered as if it were current.
    (root / "mockups").mkdir(parents=True, exist_ok=True)
    for old in (root / "mockups").glob("page-*.png"):
        old.unlink()
    with sync_playwright() as p:
        br = p.chromium.launch()
        pg0 = br.new_page(viewport={"width": W, "height": H})
        # the measuring page needs the same face declaration as the drawn one, or the widths the
        # wrapper is given come from a different font than the one that finally paints the line
        pg0.set_content(f"<html><head><style>{FACE_CSS}</style></head><body></body></html>")
        M = Measurer(pg0)

        items = rows_for_blocks(data["blocks"], M, figures_dir)
        assert_glyphs(M, items)
        pages = paginate(items)

        plans = []
        for i, pgrows in enumerate(pages, 1):
            seed = int(hashlib.md5(f"{key}|{i}".encode()).hexdigest()[:8], 16)
            html = page_html(pgrows, figures_dir, seed)
            pg0.set_content(html)
            pg0.screenshot(path=str(root / "mockups" / f"page-{i:02d}.png"))
            plans.append({"page": f"page-{i:02d}", "content": plan_for(pgrows),
                          "gaps": sum(1 for r in pgrows if r["t"] == "gap")})
        br.close()

    (root / "plans.json").write_text(json.dumps(plans, ensure_ascii=False, indent=1), encoding="utf-8")
    (root / "rows.json").write_text(json.dumps(
        [[{k: v for k, v in r.items() if k != "cells"} for r in pgr] for pgr in pages],
        ensure_ascii=False), encoding="utf-8")

    used = [sum(row_height(r) for r in pgr) for pgr in pages]
    print(f"{key}: {len(items)} rows -> {len(pages)} pages  (rows used per page: {used})")
    print(f"  mockups -> {root / 'mockups'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
