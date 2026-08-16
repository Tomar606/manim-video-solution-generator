"""STEP 1 — the temp: a typeset mock-up of the finished page. No API calls.

This is the stage the notes-editor pipeline was rebuilt around, and the reason
it is here. The old route described the layout to the image model *in prose*
("write about 24 rows, spread it to the bottom") and paid an image every time
it guessed wrong. The mock-up removes the guessing: the content is typeset
deterministically onto a copy of the REAL ruled sheet at the REAL geometry, so
the model can SEE the finished layout and only has to re-write it by hand.

Two things follow from that, and both matter:

* **Pagination becomes exact.** Rows are no longer estimated from a
  words-per-row constant — the typesetter measures the actual wrapped width of
  every line in the actual font, so "does this fit" is a measurement, not a
  guess. The Devanagari words-per-row fudge disappears entirely.
* **It is free and instant.** You can look at the temp, fix the wording, and
  look again without spending anything.

The jitter is deliberate and deterministic (seeded from page, row and the words
themselves, so a re-run reproduces it exactly). A machine-perfect blueprint
produces machine-perfect handwriting — every line starting on the same vertical
reads as printed. notes-editor learned the hard way that the scatter belongs
SIDEWAYS and mostly at paragraph level: vertical jitter makes words hover
between rules, which reads as broken rather than human.
"""
from __future__ import annotations

import json
import random
from dataclasses import dataclass, field
from pathlib import Path

from .api import PAGE_SIZE, fit_page

# --- ink -------------------------------------------------------------------
INK_BLUE = (38, 58, 122)      # body / answers
INK_BLACK = (44, 40, 38)      # questions and headings

# --- fonts -----------------------------------------------------------------
# Devanagari needs a shaping engine; Pillow uses libraqm/harfbuzz when built
# with it. Kohinoor renders conjuncts (अर्द्धपारगम्य) cleanly at this size.
F_DIR = "/System/Library/Fonts/Supplemental"
FONT_DEVANAGARI = f"{F_DIR}/Kohinoor.ttc"
FONT_LATIN = f"{F_DIR}/Arial.ttf"
FONT_LATIN_BOLD = f"{F_DIR}/Arial Bold.ttf"

# Body size as a fraction of the ruled pitch. notes-editor calibrated Arial 36
# against a 46.862 pitch by measuring the real hand's line width; that ratio
# (0.768) is what keeps the mock-up's wrap points where the handwriting's wrap
# points will land. Carried over rather than re-guessed.
BODY_RATIO = 0.768
HEAD_RATIO = 0.700
# A pure Latin/maths row is CENTRED in the ruled gap rather than hanging from
# the rule the way Devanagari does. At full body size Arial fills the whole
# gap and its descenders strike the next row's शिरोरेखा, so those rows are
# written a touch smaller — as a hand writing English between rules does.
LATIN_BODY_SHRINK = 0.82

# --- jitter (see module docstring) -----------------------------------------
HAND_JITTER = True
JIT_BLOCK_X = (-11.0, 20.0)    # per paragraph — the big one
JIT_ROW_X = (-9.0, 10.0)       # per row inside a paragraph
JIT_SPACE = (-1.3, 2.4)       # word-gap wobble
JIT_Y = 0.0                   # NO vertical scatter: every baseline on its rule


def _jit(*parts) -> random.Random:
    return random.Random("|".join(str(p) for p in parts))


# --------------------------------------------------------------------------- #
# Geometry, measured off the sheet rather than hard-coded                      #
# --------------------------------------------------------------------------- #
@dataclass
class Geometry:
    rule_ys: list[float]
    text_x: float
    right_x: float
    first_row: int
    last_row: int
    body_size: int
    head_size: int

    @property
    def usable(self) -> int:
        return self.last_row - self.first_row + 1

    @property
    def pitch(self) -> float:
        d = [b - a for a, b in zip(self.rule_ys, self.rule_ys[1:])]
        return sum(d) / len(d) if d else 44.0

    def y(self, row: int) -> float:
        return self.rule_ys[max(0, min(row, len(self.rule_ys) - 1))]


def measure(base) -> Geometry:
    """Find the printed rules and the writable box on the base sheet."""
    import numpy as np

    g = np.asarray(base.convert("L"), dtype=float)
    band = g[:, int(g.shape[1] * 0.20):int(g.shape[1] * 0.90)]
    prof = np.median(band, axis=1)
    dark = prof < (np.median(prof) - 4)

    ys: list[float] = []
    run: list[int] = []
    for i, d in enumerate(dark):
        if d:
            run.append(i)
        elif run:
            ys.append(sum(run) / len(run))
            run = []
    if run:
        ys.append(sum(run) / len(run))
    if len(ys) < 5:
        raise ValueError("could not find ruled lines on the base sheet")

    # Horizontal extent of a rule = the writable width.
    mid = int(ys[len(ys) // 2])
    row = g[mid - 1:mid + 2, :].min(axis=0)
    xs = np.where(row < np.median(g) - 4)[0]
    left, right = (float(xs.min()), float(xs.max())) if len(xs) else (80.0, 940.0)

    pitch = (ys[-1] - ys[0]) / max(1, len(ys) - 1)
    return Geometry(
        rule_ys=ys,
        text_x=left + 16,             # clear of the rule's left end
        right_x=right - 8,
        first_row=0,                  # write from the very first rule
        last_row=len(ys) - 2,         # and the bottom one
        body_size=max(12, round(BODY_RATIO * pitch)),
        head_size=max(12, round(HEAD_RATIO * pitch)),
    )



# --------------------------------------------------------------------------- #
# Diagrams: a box the text flows around                                        #
# --------------------------------------------------------------------------- #
# The figure is pasted GHOSTED — faint grey rather than crisp. notes-editor
# found that a sharp printed panel gets copied pixel-for-pixel by the image
# model instead of redrawn by hand; ghosting still shows WHAT the figure is,
# WHERE it sits and HOW BIG it is, with nothing solid enough to trace.
GHOST_STRENGTH = 0.42          # 0 = invisible, 1 = full contrast
DIAGRAM_GUTTER = 60            # px of air between the text and the figure.
                               # 18 was enough for the TYPESET mock-up but not
                               # for the handwriting drawn from it: the model
                               # ran a word past the wrap point and the figure
                               # then covered it, silently dropping 'में' from a
                               # sentence. The gutter has to absorb the model's
                               # slop, not just the typesetter's.


# The supplied sheet's rules are extremely faint. Measured against them, the
# image model's output scattered +-19px on a 44px pitch: it treats near-white
# ruling as optional texture, lays down its own grid, and floats the writing
# between the lines. Darkening the rules on the base gives it something it
# cannot ignore — and the base and the mock-up must carry the SAME rules, or
# the model is being shown two different pages.
RULE_INK = (120, 145, 190)     # a real notebook blue, still light
RULE_WIDTH = 2


def strengthen_rules(base, geo: "Geometry", ink=RULE_INK, width=RULE_WIDTH):
    """Redraw the printed rules darker, in place, at their measured positions."""
    from PIL import ImageDraw

    out = base.copy()
    d = ImageDraw.Draw(out)
    x0, x1 = geo.text_x - 26, geo.right_x + 14
    for y in geo.rule_ys:
        d.line([(x0, y), (x1, y)], fill=ink, width=width)
    return out


@dataclass
class Diagram:
    """A figure occupying a rectangle of the page, with text flowing beside it."""
    path: str
    row: int                   # first ruled row it covers (page-relative)
    rows: int                  # how many rows it spans
    width_frac: float = 0.42   # of the page width
    side: str = "right"        # which side the figure sits on

    x0: float = 0.0            # filled in by place()
    x1: float = 0.0
    y0: float = 0.0
    y1: float = 0.0


def ghost(img, strength: float = GHOST_STRENGTH):
    """Turn a figure into faint grey INK on a TRANSPARENT ground.

    The source scan has a white background. Pasting it opaquely stamps a white
    rectangle over the notebook and wipes out the ruled lines behind it — the
    figure then reads as a sticker on the page rather than something drawn on
    it. So the paper is dropped entirely: the drawn strokes become alpha, and
    the page's own rules and texture show straight through the figure.
    """
    from PIL import Image

    g = img.convert("L")
    # Dark pixels are ink -> opaque; white paper -> fully transparent.
    alpha = Image.eval(g, lambda v: int((255 - v) * strength))
    out = Image.new("RGBA", g.size, (70, 70, 78, 0))
    out.putalpha(alpha)
    return out


def place(diagram: Diagram, geo: "Geometry"):
    """Work out the figure's pixel rectangle from its row span."""
    from PIL import Image

    src = Image.open(diagram.path)
    page_w = geo.right_x + 24
    w = page_w * diagram.width_frac
    h = w * src.height / src.width
    # Snap the height to whole ruled rows so the text beside it lines up.
    diagram.rows = max(1, round(h / geo.pitch))
    h = diagram.rows * geo.pitch

    if diagram.side == "right":
        diagram.x1 = geo.right_x
        diagram.x0 = diagram.x1 - w
    else:
        diagram.x0 = geo.text_x
        diagram.x1 = diagram.x0 + w
    diagram.y0 = geo.y(geo.first_row + diagram.row) - geo.pitch * 0.75
    diagram.y1 = diagram.y0 + h
    return diagram


def covers_row(geo: "Geometry", diagram, row: int) -> bool:
    """Does the figure's rectangle actually touch this row's band of ink?

    Tested geometrically rather than by counting rows: the figure's top is
    nudged off the rule and its height is rounded, so a counter-based range
    disagreed with the pixels by one row — and that row's text ran straight
    through the bottom of the diagram.
    """
    if diagram is None:
        return False
    y = geo.y(geo.first_row + row)
    top = y - geo.pitch * 0.95        # upper matras rise about this far
    bot = y + geo.pitch * 0.85        # descenders hang about this far
    return not (bot < diagram.y0 or top > diagram.y1)


def right_limit(geo: "Geometry", diagram, row: int) -> float:
    """Right edge available to text on this row — pulled in beside a figure."""
    if covers_row(geo, diagram, row) and diagram.side == "right":
        return diagram.x0 - DIAGRAM_GUTTER
    return geo.right_x


def left_limit(geo: "Geometry", diagram, row: int) -> float:
    if covers_row(geo, diagram, row) and diagram.side == "left":
        return diagram.x1 + DIAGRAM_GUTTER
    return geo.text_x


# --------------------------------------------------------------------------- #
# Fonts + measured wrapping                                                    #
# --------------------------------------------------------------------------- #
_DEV = None


def _has_devanagari(text: str) -> bool:
    return any("ऀ" <= ch <= "ॿ" for ch in text)


def load_fonts(geo: Geometry) -> dict:
    from PIL import ImageFont

    def _try(path, size, index=0):
        try:
            return ImageFont.truetype(path, size, index=index)
        except Exception:
            return ImageFont.load_default()

    return {
        "body": _try(FONT_DEVANAGARI, geo.body_size),
        "head": _try(FONT_DEVANAGARI, geo.head_size),
        "body_latin": _try(FONT_LATIN, int(geo.body_size * LATIN_BODY_SHRINK)),
        "head_latin": _try(FONT_LATIN_BOLD, geo.head_size),
    }


def font_for(fonts: dict, text: str, heading: bool) -> object:
    """Devanagari text needs the Devanagari face; pure Latin looks better in
    Arial, which is also what the width calibration was done against."""
    if _has_devanagari(text):
        return fonts["head" if heading else "body"]
    return fonts["head_latin" if heading else "body_latin"]



_HEADLINE: dict = {}


def headline_offset(font) -> float:
    """How far the शिरोरेखा sits ABOVE the Latin baseline, in pixels.

    Devanagari hangs FROM its head-line the way Latin sits ON its baseline: in
    a ruled notebook the शिरोरेखा is drawn along the printed rule and the
    letters descend beneath it. Putting the Latin baseline on the rule instead
    leaves the whole word floating above it — which is exactly what the first
    mock-up did.

    Measured rather than guessed: the glyphs are rendered once and the darkest
    horizontal row of the raster IS the head-line, so this stays correct if the
    font or size changes.
    """
    key = (getattr(font, "path", ""), getattr(font, "size", 0))
    if key in _HEADLINE:
        return _HEADLINE[key]
    from PIL import Image, ImageDraw
    import numpy as np

    size = int(getattr(font, "size", 32) or 32)
    base = size * 3
    img = Image.new("L", (size * 22, size * 5), 255)
    ImageDraw.Draw(img).text((4, base), "भीतरी नली सरन्ध्र होती",
                             font=font, fill=0, anchor="ls")
    dark = (np.asarray(img, dtype=float) < 128).sum(axis=1)
    off = float(base - int(np.argmax(dark))) if dark.max() > 0 else 0.0
    # A sane band: the head-line is always well inside the letter body.
    _HEADLINE[key] = off if 0.35 * size <= off <= 0.85 * size else 0.62 * size
    return _HEADLINE[key]


def page_baseline_offset(rows, pitch: float) -> float:
    """One baseline offset for the WHOLE page, not per row.

    Devanagari hangs below its rule; Latin sits on it. Deciding that per row
    put a Latin row only ~18px under the Devanagari row above it instead of a
    full pitch, and the two collided. On a Hindi page the Latin words share the
    Devanagari baseline anyway — that is how they are written by hand — so the
    offset is resolved once, from the first Devanagari row, and used by every
    row on the page.
    """
    for r in rows:
        if r.text and _has_devanagari(r.text):
            return headline_offset(r.font)
    return -pitch * 0.10


_probe = None


def _draw_probe():
    global _probe
    if _probe is None:
        from PIL import Image, ImageDraw
        _probe = ImageDraw.Draw(Image.new("RGB", (8, 8)))
    return _probe


def text_width(text: str, font) -> float:
    return _draw_probe().textlength(text, font=font)


def wrap(text: str, font, x_start: float, x_cont: float,
         right: float) -> list[tuple[str, float]]:
    """Greedy word wrap against the REAL font. One entry per ruled row."""
    return wrap_flow(text, font, x_start, x_cont, lambda r: right, 0)


def wrap_flow(text: str, font, x_start: float, x_cont: float,
              right_of, start_row: int) -> list[tuple[str, float]]:
    """Wrap with a per-row right edge, so text can flow around a figure.

    ``right_of(row)`` is consulted for the row each line actually lands on —
    which is why this cannot be done with a fixed width: the row a line falls
    on is only known once the preceding lines have been wrapped.
    """
    out: list[tuple[str, float]] = []
    cur, x, row = "", x_start, start_row
    for w in text.split():
        trial = (cur + " " + w).strip()
        if cur and x + text_width(trial, font) > right_of(row):
            out.append((cur, x))
            row += 1
            cur, x = w, x_cont
        else:
            cur = trial
    if cur:
        out.append((cur, x))
    return out


# --------------------------------------------------------------------------- #
# Laying tagged lines out into rows                                            #
# --------------------------------------------------------------------------- #
_TAGS = ("TITLE", "SUBHEAD", "TEXT", "POINT", "GAP", "Q", "ANS")


def _split_tag(line: str) -> tuple[str, str]:
    line = line.strip()
    if line.startswith("<<") and ">>" in line:
        tag, rest = line[2:].split(">>", 1)
        tag = tag.strip().upper()
        if tag in _TAGS:
            return tag, rest.strip()
    return "TEXT", line


@dataclass
class Row:
    text: str
    x: float
    font: object
    fill: tuple
    bullet_x: float | None = None
    block: int = 0
    label: str = ""              # "Q1:" / "Ans:" — always in the question ink
    label_x: float = 0.0


def layout_rows(lines: list[str], geo: Geometry, fonts: dict,
                diagram=None) -> list[Row]:
    """Turn tagged lines into concrete rows, measured in the real font."""
    rows: list[Row] = []
    bullet_dx = geo.pitch * 0.24
    text_dx = geo.pitch * 1.00
    RIGHT = lambda r: right_limit(geo, diagram, r)

    for block, raw in enumerate(lines):
        tag, text = _split_tag(raw)
        if tag == "GAP":
            rows.append(Row("", geo.text_x, fonts["body"], INK_BLUE, block=block))
            continue

        heading = tag in ("TITLE", "SUBHEAD")
        font = font_for(fonts, text, heading)
        # Questions and headings in black; everything the student answers in blue.
        fill = INK_BLACK if tag in ("Q", "TITLE", "SUBHEAD") else INK_BLUE

        # "Q1:" and "Ans:" are labels, not body text: they stay BLACK even on
        # the blue answer, the way a student writes them. The sheet has no
        # vertical margin rule to park them in, so they sit inline and the
        # first row's text is indented past them.
        label = ""
        if tag == "Q":
            head, sep, rest = text.partition(":")
            if sep and len(head) <= 6:
                label, text = head + ":", rest.strip()
        elif tag == "ANS":
            label = "Ans:"
        if label:
            lw = text_width(label + " ", font)
            wrapped = wrap_flow(text, font, geo.text_x + lw, geo.text_x,
                                RIGHT, len(rows))
            for i, (t, x) in enumerate(wrapped):
                rows.append(Row(t, x, font, fill, block=block,
                                label=label if i == 0 else "",
                                label_x=geo.text_x if i == 0 else 0.0))
            continue

        if tag == "POINT":
            x0 = geo.text_x + text_dx
            wrapped = wrap_flow(text, font, x0, x0, RIGHT, len(rows))
            for i, (t, x) in enumerate(wrapped):
                rows.append(Row(t, x, font, fill, block=block,
                                bullet_x=geo.text_x + bullet_dx if i == 0 else None))
            continue

        wrapped = wrap_flow(text, font, geo.text_x, geo.text_x, RIGHT, len(rows))
        for t_, x in wrapped:
            rows.append(Row(t_, x, font, fill, block=block))
    return rows


def paginate(rows: list[Row], geo: Geometry) -> list[list[Row]]:
    """Split measured rows into pages. Exact — no row estimates involved."""
    pages, cur = [], []
    for row in rows:
        if len(cur) >= geo.usable:
            pages.append(cur)
            cur = []
        # A blank row at the top of a fresh page is the page break itself.
        if not cur and not row.text:
            continue
        cur.append(row)
    if cur:
        pages.append(cur)
    return pages


# --------------------------------------------------------------------------- #
# Drawing                                                                      #
# --------------------------------------------------------------------------- #
def draw_page(base, rows: list[Row], geo: Geometry, page_no: int,
              diagram=None):
    """Typeset one page onto a copy of the base sheet."""
    from PIL import ImageDraw

    from PIL import Image

    img = base.copy()
    if diagram is not None:
        fig = ghost(Image.open(diagram.path))
        w = max(1, int(diagram.x1 - diagram.x0))
        h = max(1, int(diagram.y1 - diagram.y0))
        fig = fig.resize((w, h), Image.LANCZOS)
        img = img.convert("RGBA")
        layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
        layer.paste(fig, (int(diagram.x0), int(diagram.y0)), fig)
        img = Image.alpha_composite(img, layer).convert("RGB")
    d = ImageDraw.Draw(img)

    # Resolved once so Devanagari and Latin rows never collide (see above).
    page_off = page_baseline_offset(rows, geo.pitch)

    block_dx: dict[int, float] = {}
    for i, row in enumerate(rows):
        if not row.text:
            continue
        y = geo.y(geo.first_row + i)
        if HAND_JITTER:
            if row.block not in block_dx:
                block_dx[row.block] = _jit("blk", page_no, row.block).uniform(*JIT_BLOCK_X)
            rng = _jit("row", page_no, i, row.text[:24])
            dx = block_dx[row.block] + rng.uniform(*JIT_ROW_X)
        else:
            rng, dx = _jit("x"), 0.0

        if row.bullet_x is not None:
            r = max(2.0, geo.pitch * 0.055)
            bx, byd = row.bullet_x + dx, y + geo.pitch * 0.28
            d.ellipse([bx - r, byd - r, bx + r, byd + r], fill=row.fill)

        # Devanagari hangs from its शिरोरेखा on the rule; a line of pure
        # Latin/maths is written vertically CENTRED in the ruled gap instead.
        if _has_devanagari(row.text):
            by = y + page_off
        else:
            ascent, descent = row.font.getmetrics()
            by = y + geo.pitch / 2 + (ascent - descent) / 2
        if row.label:
            d.text((row.label_x + dx, by), row.label,
                   font=row.font, fill=INK_BLACK, anchor="ls")

        # Word-by-word so the gaps are never twice the same width.
        x = row.x + dx
        space = text_width(" ", row.font)
        for w in row.text.split(" "):
            if w:
                d.text((x, by), w, font=row.font, fill=row.fill, anchor="ls")
            x += text_width(w, row.font) + space + (
                rng.uniform(*JIT_SPACE) if HAND_JITTER else 0.0)
    return img


# --------------------------------------------------------------------------- #
# The step-1 entry point                                                       #
# --------------------------------------------------------------------------- #
def build_mockup(lines: list[str], sheet: str | Path, out_dir: str | Path,
                 stem: str = "temp", diagram: "Diagram | None" = None,
                 log=None) -> dict:
    """Typeset ``lines`` onto ``sheet``. Returns pages, plans and geometry.

    Writes ``<stem>_page_N.png`` (the mock-ups the drawing step shows the
    model), ``<stem>_plans.json`` (the tagged lines per page) and
    ``<stem>_geometry.json``.
    """
    from PIL import Image

    log = log or (lambda m: None)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    base = fit_page(Image.open(sheet).convert("RGB"))
    geo = measure(base)
    base = strengthen_rules(base, geo)
    fonts = load_fonts(geo)
    log(f"sheet {base.size[0]}x{base.size[1]} · {len(geo.rule_ys)} rules · "
        f"pitch {geo.pitch:.1f} · body {geo.body_size}px · "
        f"{geo.usable} writable rows")

    if diagram is not None:
        place(diagram, geo)
        log(f"diagram {Path(diagram.path).name} · {diagram.rows} rows · "
            f"x {diagram.x0:.0f}-{diagram.x1:.0f} · text wraps beside it")
    rows = layout_rows(lines, geo, fonts, diagram)
    pages = paginate(rows, geo)
    log(f"{len(rows)} measured rows -> {len(pages)} page(s)")

    # Plans: the tagged source lines that ended up on each page, so the drawing
    # step can hand the model the words as text as well as the picture.
    plans: list[str] = []
    for page in pages:
        blocks = sorted({r.block for r in page})
        plans.append("\n".join(lines[b] for b in blocks))

    written = []
    for i, page in enumerate(pages):
        img = draw_page(base, page, geo, i + 1,
                        diagram if i == 0 else None)
        dest = out / (f"{stem}_page_1.png" if len(pages) == 1
                      else f"{stem}_page_{i + 1}.png")
        img.save(dest)
        written.append(dest)
        log(f"  page {i + 1}: {len(page)}/{geo.usable} rows -> {dest.name}")

    # A shorter run must not leave pages from a longer previous run behind —
    # a stale temp_page_3.png reads as if the content still spans three pages.
    for stale in out.glob(f"{stem}_page_*.png"):
        if stale not in written:
            stale.unlink()

    (out / f"{stem}_plans.json").write_text(
        json.dumps(plans, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / f"{stem}_geometry.json").write_text(json.dumps({
        "size": list(PAGE_SIZE), "rules": len(geo.rule_ys),
        "pitch": round(geo.pitch, 3), "text_x": round(geo.text_x, 1),
        "right_x": round(geo.right_x, 1), "body_size": geo.body_size,
        "head_size": geo.head_size, "usable_rows": geo.usable,
    }, indent=2), encoding="utf-8")

    base_path = out / f"{stem}_base.png"
    base.save(base_path)
    return {"pages": written, "plans": plans, "geometry": geo,
            "base": base_path, "rows": len(rows)}
