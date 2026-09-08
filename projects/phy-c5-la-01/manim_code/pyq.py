"""चुम्बकीय पदार्थों के प्रकार: one comparison table, hand-built, revealed
across two parts — part 1 the first 3 rows, part 2 the remaining 4.

    PYQ_PROJECT=phy-c5-la-01 PYQ_PART=1 manim -qh pyq_composed.py PyqPart
    PYQ_PROJECT=phy-c5-la-01 PYQ_PART=2 manim -qh pyq_composed.py PyqPart

Every other PYQ project in this repo (see ``projects/phy-c1-la-01/manim_code/
pyq.py``, the template this file is modelled on) is driven by
``beats_part<N>.json``: a list of blocks the shared scene already knows how to
place, written by ``src/visual_director.py``. This part is NOT — its
``beats_part1.json`` calls for a "points" list and a two-column "compare"
whose items ("भारी चुंबकीय प्रभाव", "प्रतिकर्षित: डायमैग्नेटिक", ...) do not
match what the real HeyGen clip actually says at those moments. The clip is
the thing that cannot be re-shot, so the visual has to match the TRANSCRIPT
(``lines_part1.json``), not the auto-generated plan — and the transcript is,
word for word, a teacher filling in a 3x3 table (three properties x three
material types) one cell at a time. That shape has no generic "beat" for it
(`beat_table` reveals whole ROWS, not individual cells), so this part is
authored directly instead of through ``build_beat``. ``beats_part1.json`` is
left untouched — it simply isn't read here.

Column headers (प्रतिचुम्बकीय / अनुचुम्बकीय / लौहचुम्बकीय) and row labels
(the three properties) are the table's SCAFFOLDING: once named they stay at
full brightness for the rest of the part, exactly like axis labels on a
graph, because the student needs them legible throughout to read every cell
that follows. Only the nine DATA CELLS take part in the fill-in-and-dim dance
CLAUDE.md describes for counted lists: the cell currently being spoken is
full white, everything already revealed sits dimmed (``DIM``, this file's
already-established muted tone — see the sibling's own DIM/GOLD/GREEN
constants, which are hand-picked hex values rather than a runtime THEME
lookup, matching the convention already set by every other hand-written scene
in this track), and by the closing summary (line 82 onward, ~17.5s with no
new content) every cell settles to that same muted tone together, so the last
thing on screen is the complete, legible, evenly-styled answer.

The reveal indices below are 0-based positions into ``lines_part1.json``
and were matched against its actual timestamps line by line before writing
this file:

    line  6 ( 14.14s)  table frame + 3 column headers appear
    line 21 ( 41.66s)  row 1 label  — "चुम्बक के प्रति व्यवहार"
    line 24 ( 47.32s)    दिया  cell 1 — "हल्का-सा प्रतिकर्षित"
    line 27 ( 54.58s)    अनु   cell 1 — "हल्का-सा आकर्षित"
    line 30 ( 60.76s)    लौह   cell 1 — "प्रबल रूप से आकर्षित"
    line 40 ( 80.48s)  row 2 label  — "क्षेत्र में अभिविन्यास"
    line 45 ( 88.14s)    दिया  cell 2 — "क्षेत्र के लंबवत्"
    line 50 ( 99.14s)    अनु   cell 2 — "क्षेत्र के समान्तर"
    line 55 (109.32s)    लौह   cell 2 — "क्षेत्र के समान्तर"
    line 65 (124.62s)  row 3 label  — "असमान क्षेत्र में गमन"
    line 69 (129.64s)    दिया  cell 3 — "कम तीव्रता की ओर"
    line 73 (135.58s)    अनु   cell 3 — "अधिक तीव्रता की ओर"
    line 77 (142.16s)    लौह   cell 3 — "अधिक तीव्रता की ओर (तेज़ी से)"
    line 82 (149.40s)  summary begins — settle every cell to the muted tone

Everything else (the question card, the caption pill, ``place()``'s
grow-or-shrink fit into the stage band, the compositor's geometry contract)
is copied from the sibling file unchanged, because that contract is what
keeps this render compatible with tools/composite.py.

Part 2 (``lines_part2.json``) picks up the SAME table and adds four more
rows — it does not start a new one. ``meta.json`` marks it ``no_card`` (no
question-card intro, per its own transcript) and gives it its own
``clip_end``. The table-building code is shared with part 1 through
``_build_table(rows, cells, ...)`` rather than duplicated: part 1 still
calls it with its original 3-row ``ROWS``/``CELLS`` and default sizing —
byte-for-byte the same call as before this file grew a second part — while
part 2 calls it with the full 7-row ``ROWS_ALL``/``CELLS_ALL`` and smaller
fonts (see the note above ``TABLE2_CELL_SIZE``). ``_reveal_row_label``,
``_reveal_cell`` and ``_settle_table`` needed no changes at all: they already
index into whatever ``self._row_labels``/``self._cells`` the last
``_build_table`` call produced, so the same three methods drive both parts.

Part 2 opens on the finished part-1 table (3 rows filled and dimmed, headers
and their row labels bright) rather than replaying the build — the student
already watched that happen once, and CLAUDE.md's "no graphic" rule is really
"no re-teaching a graphic that already did its job". ``_build_table`` grew a
``settled_rows`` argument for exactly this: it paints that many rows into
their post-``_settle_table`` state with no animation and no cue, instead of
this file forking a second table-builder to fake the same thing.

The reveal indices below are 0-based positions into ``lines_part2.json``,
matched against its actual timestamps the same way part 1's were:

    line  3 ( 11.88s)  row 4 label  — "आपेक्षिक चुम्बकशीलता"
    line  4 ( 14.86s)    दिया  cell 4 — "एक से कम"
    line  5 ( 20.08s)    अनु   cell 4 — "एक से कुछ अधिक"
    line  6 ( 24.88s)    लौह   cell 4 — "बहुत अधिक"
    line 10 ( 35.10s)  row 5 label  — "स्थायी चुम्बक निर्माण"
    line 12 ( 41.06s)    दिया  cell 5 — "नहीं"
    line 13 ( 45.22s)    अनु   cell 5 — "नहीं"
    line 14 ( 49.10s)    लौह   cell 5 — "हाँ"
    line 17 ( 65.98s)  row 6 label  — "चुम्बकीय प्रवृत्ति"
    line 18 ( 67.80s)    दिया  cell 6 — "ऋणात्मक तथा अल्प"
    line 19 ( 73.60s)    अनु   cell 6 — "धनात्मक किन्तु अल्प"
    line 20 ( 78.50s)    लौह   cell 6 — "धनात्मक एवं बहुत अधिक"
    line 24 ( 95.82s)  row 7 label  — "उदाहरण"
    line 25 ( 98.72s)    दिया  cell 7 — 5 examples, wrapped to 2 lines
    line 26 (103.38s)    अनु   cell 7 — 4 examples, wrapped to 2 lines
    line 27 (108.98s)    लौह   cell 7 — 4 examples, wrapped to 2 lines
    line 28 (113.40s)  summary begins — settle every cell to the muted tone
"""
from manim import *  # noqa: F403
import json
import os as _os
from pathlib import Path as _Path

import numpy as np

from src.manim_helpers import ThemedScene, fit_caption, norm_point, register_fonts, wrap_measured

INK, DIM, GOLD = "#FFFFFF", "#B9C6DC", "#FFC15C"
GREEN, VIOLET, CYAN = "#7CE0B0", "#C792EA", "#5BC8F9"

FONT, FONT_W = "Khand", "BOLD"

PROJECT = _os.getenv("PYQ_PROJECT", "phy-c5-la-01")
PART = int(_os.getenv("PYQ_PART", "1"))
ROOT = _Path(ASSET_ROOT) / "projects" / PROJECT
FIGURES = ROOT / "assets" / "figures"

LINES = json.loads((ROOT / f"lines_part{PART}.json").read_text(encoding="utf-8"))
META = json.loads((ROOT / "meta.json").read_text(encoding="utf-8"))
CLIP_END = float((META.get("clip_end") or {}).get(str(PART), float(LINES[-1]["start"]) + 3.0))

# PYQ_UNTIL=<seconds> stops the scene early, exactly as in the sibling file —
# useful for previewing just the table build without sitting through the
# whole 167s clip.
_UNTIL = float(_os.environ.get("PYQ_UNTIL", "0") or 0)

# The CEILING, not the size every caption renders at. `caption()` below
# shrinks from here automatically when a line is long.
CAPTION_SIZE = 55
MAX_CAPTION_LINES = 2
CAPTION_MIN_SIZE = 32
CAPTION_W, CAPTION_TOP = 0.90, 0.090
# STAGE_BOT is derived from where the compositor actually puts the presenter
# (tools/composite.py overlays him at FULL_Y=966 of a 1920-high frame, so his
# head starts at 0.503) — copied verbatim from the sibling file. If the
# compositor's placement ever changes, both files have to change together.
STAGE_TOP, STAGE_BOT, STAGE_W = 0.290, 0.492, 0.86
CAPTION_GAP = 0.30

HILITE = {k: GOLD for k in META.get("hilite", [])}

# --- the table's content, in the order the transcript reveals it ---------- #
COLS = ["प्रतिचुम्बकीय", "अनुचुम्बकीय", "लौहचुम्बकीय"]
ROWS = ["चुम्बक के प्रति व्यवहार", "क्षेत्र में अभिविन्यास", "असमान क्षेत्र में गमन"]
CELLS = [
    ["हल्का-सा प्रतिकर्षित", "हल्का-सा आकर्षित", "प्रबल रूप से आकर्षित"],
    ["क्षेत्र के लंबवत्", "क्षेत्र के समान्तर", "क्षेत्र के समान्तर"],
    # Wrapped onto two lines: it is the one cell wider than the rest of its
    # column, and an outlier that long would have dragged the whole table's
    # scale down when `place()` fits it into the (narrow) stage band — see
    # `place()`'s own note in the sibling file about growing vs. shrinking.
    ["कम तीव्रता की ओर", "अधिक तीव्रता की ओर", "अधिक तीव्रता की ओर\n(तेज़ी से)"],
]

# 0-based line indices into LINES, matched against lines_part1.json by hand —
# see the module docstring for the timestamp each one lands on.
HEADER_AT = 6
ROW_LABEL_AT = {21: 0, 40: 1, 65: 2}
CELL_AT = {
    24: (0, 0), 27: (0, 1), 30: (0, 2),
    45: (1, 0), 50: (1, 1), 55: (1, 2),
    69: (2, 0), 73: (2, 1), 77: (2, 2),
}
SETTLE_AT = 82

# --- part 2 extends the same table with 4 more rows ----------------------- #
# ROWS_ALL/CELLS_ALL EXTEND part 1's own ROWS/CELLS rather than restating
# them, so the first three rows can never drift between the two parts — the
# exact failure mode CLAUDE.md warns about for anything authored twice.
ROWS_ALL = ROWS + [
    "आपेक्षिक चुम्बकशीलता",
    "स्थायी चुम्बक निर्माण",
    "चुम्बकीय प्रवृत्ति",
    "उदाहरण",
]
CELLS_ALL = CELLS + [
    ["एक से कम", "एक से कुछ अधिक", "बहुत अधिक"],
    ["नहीं", "नहीं", "हाँ"],
    ["ऋणात्मक तथा अल्प", "धनात्मक किन्तु अल्प", "धनात्मक एवं बहुत अधिक"],
    # Row 7 (examples) is the widest content in the whole table — 4-5 items
    # per cell against 2-4 words everywhere else. Left unwrapped it would
    # have widened column 0 alone by roughly 2x (col width is the max item
    # width in that COLUMN, across every row), dragging the whole table's
    # `place()` scale down for a reason that has nothing to do with legible
    # font size. Wrapped to 2 lines each, same move part 1 made for its one
    # wide Ferro cell.
    [
        "बिस्मथ, फास्फोरस,\nएंटिमनी, पारा, वायु",
        "मैंगनीज, प्लेटिनम,\nसोडियम, ऐल्युमिनियम",
        "लोहा, इस्पात,\nनिकिल, कोबाल्ट",
    ],
]

# Part 2's table carries 7 rows (8 grid rows including the header) against
# part 1's 3 (4 grid rows) — roughly twice the vertical content in the same
# STAGE_BAND, before even counting row 7's taller two-line cells. `place()`
# will shrink whatever it is handed to fit, but leaning on that alone at
# part 1's font size and row spacing would come out legible on a desktop
# preview and too small on the phone this is watched on (the same reasoning
# `place()`'s own docstring gives for GROWING a short block — here it cuts
# the other way). Smaller fonts and tighter row spacing keep the amount
# `place()` still has to shrink modest instead of drastic.
TABLE2_HEADER_SIZE, TABLE2_LABEL_SIZE, TABLE2_CELL_SIZE = 20, 17, 17
TABLE2_BUFF_Y, TABLE2_COL_PAD = 0.14, 0.22

# 0-based line indices into lines_part2.json, matched by hand the same way —
# see the module docstring for the timestamp each one lands on.
ROW_LABEL_AT2 = {3: 3, 10: 4, 17: 5, 24: 6}
CELL_AT2 = {
    4: (3, 0), 5: (3, 1), 6: (3, 2),
    12: (4, 0), 13: (4, 1), 14: (4, 2),
    18: (5, 0), 19: (5, 1), 20: (5, 2),
    25: (6, 0), 26: (6, 1), 27: (6, 2),
}
SETTLE_AT2 = 28


class PyqPart(ThemedScene):
    CAPTION_MODE = "narration"
    STAGE_BAND = (STAGE_TOP, STAGE_BOT)

    # ---- text ------------------------------------------------------------ #
    def _cell(self, text, colour, size=22, weight=FONT_W):
        return Text(str(text), font=FONT, font_size=size, color=colour, weight=weight)

    def _hl(self, line):
        out = {}
        for w in sorted(HILITE, key=len, reverse=True):
            if w not in line or any(w in k for k in out):
                continue
            for token in line.split():
                if w in token:
                    whole = token.strip(",।?!—:;")
                    if whole and not any(whole in k for k in out):
                        out[whole] = HILITE[w]
        return out

    def _measure(self, line, size):
        cache = self.__dict__.setdefault("_wcache", {})
        k = (line, size)
        if k not in cache:
            cache[k] = Text(line, font=FONT, font_size=size, weight=FONT_W)
        return cache[k]

    def caption(self, text, size=CAPTION_SIZE):
        """Wrap at `size`, then shrink toward CAPTION_MIN_SIZE if that still
        wraps to more than MAX_CAPTION_LINES lines. Copied from the sibling
        file — this is the compositor's caption contract, not this part's."""
        limit = config.frame_width * CAPTION_W
        lines = wrap_measured(text, limit, lambda l: self._measure(l, size))
        while len(lines) > MAX_CAPTION_LINES and size > CAPTION_MIN_SIZE:
            size -= 2
            lines = wrap_measured(text, limit, lambda l: self._measure(l, size))
        g = VGroup(*[Text(l, font=FONT, font_size=size, color=INK,
                          weight=FONT_W, t2c=self._hl(l)) for l in lines])
        g.arrange(DOWN, buff=0.16)
        fit_caption(g, limit)
        g.move_to(norm_point(0.5, CAPTION_TOP))
        g.shift(DOWN * g.height / 2)
        return g

    # ---- layout ------------------------------------------------------------ #
    def stage_box(self):
        top, bot = norm_point(0.5, STAGE_TOP)[1], norm_point(0.5, STAGE_BOT)[1]
        if getattr(self, "caption_mob", None) is not None:
            top = min(top, self.caption_mob.get_bottom()[1] - CAPTION_GAP)
        return (np.array([0., (top + bot) / 2, 0.]),
                config.frame_width * STAGE_W, top - bot)

    MAX_GROW = 2.2

    def place(self, mob, y=0.5, pad=0.94, grow=True):
        """Fit a block to the stage band — shrinking OR growing it. Copied
        from the sibling file; see its docstring for why growth is capped."""
        c, w, h = self.stage_box()
        if mob.width <= 0 or mob.height <= 0:
            return mob
        s = min((w * pad) / mob.width, (h * pad) / mob.height)
        if s > 1.0:
            s = min(s, self.MAX_GROW) if grow else 1.0
        if abs(s - 1.0) > 0.01:
            mob.scale(s)
        top, bot = c[1] + h / 2, c[1] - h / 2
        cy = top - (top - bot) * y
        mob.move_to([0, max(bot + mob.height / 2,
                            min(top - mob.height / 2, cy)), 0])
        return mob

    # ---- the table ---------------------------------------------------------- #
    def _build_table(self, rows, cells, *, cell_size=22, label_size=22,
                     header_size=24, buff_y=0.26, col_pad=0.34, pad=0.92,
                     animate=True, settled_rows=0):
        """Build the whole (len(rows)+1)-row x 4-col grid (corner blank,
        3 headers, one row label + 3 cells per row) up front so it never
        re-flows once something is on screen, but only the column headers
        start visible.

        Cells are positioned by hand at absolute (x, y) offsets rather than
        with `.arrange()` — the corner slot is an empty ``Text("")`` with no
        drawable points, so a VGroup wrapping it and the header row would
        compute its bounding box from the headers alone, and `aligned_edge`
        would then anchor the header row one column to the right of every
        data row beneath it. Explicit coordinates sidestep that entirely.

        `rows`/`cells` and the sizing knobs are all parameters, not module
        constants, so this one method serves both parts: part 1 passes its
        original 3-row ``ROWS``/``CELLS`` with the defaults below (which are
        exactly its old hardcoded values — 22/22/24/0.26/0.34/0.92 — so its
        render is unchanged), and part 2 passes the full 7-row
        ``ROWS_ALL``/``CELLS_ALL`` with smaller sizing so a table twice as
        tall still fits the same STAGE_BAND legibly instead of leaning on
        `place()` to shrink it however far that takes.

        `settled_rows` lets a later part open on an EARLIER part's finished
        state instead of replaying the build: that many rows are painted
        straight into `_settle_table`'s end state (row label bright, its
        cells dimmed) with no animation and no cue, since the student
        already watched those rows fill in once.
        """
        heads = [self._cell(c, GOLD, size=header_size) for c in COLS]
        row_labels = [self._cell(r, GREEN, size=label_size) for r in rows]
        body = [[self._cell(t, INK, size=cell_size) for t in row] for row in cells]
        for h in heads:
            h.set_opacity(0.0)
        for rl in row_labels:
            rl.set_opacity(0.0)
        for row in body:
            for c in row:
                c.set_opacity(0.0)

        n = len(rows)
        grid_rows = [[None] + heads] + [[row_labels[r]] + body[r] for r in range(n)]
        ncol = 4

        col_w = []
        for c in range(ncol):
            items = [row[c] for row in grid_rows if row[c] is not None]
            col_w.append(max((m.width for m in items), default=0.5) + col_pad)
        row_h = []
        for row in grid_rows:
            items = [m for m in row if m is not None]
            row_h.append(max((m.height for m in items), default=0.4))

        y = 0.0
        for r, row in enumerate(grid_rows):
            cy = y + row_h[r] / 2
            x = 0.0
            for c, m in enumerate(row):
                cx = x + col_w[c] / 2
                if m is not None:
                    m.move_to(np.array([cx, -cy, 0.0]))
                x += col_w[c]
            y += row_h[r] + buff_y
        total_w = sum(col_w)
        total_h = y - buff_y

        flat = [m for row in grid_rows for m in row if m is not None]
        grid_group = VGroup(*flat)

        # A frame appears from the first moment too — headers with nothing
        # under them read as a title, not a table, without the rule marking
        # where the body starts and the divider separating the row labels
        # from the data columns.
        top_y = -(row_h[0] + buff_y * 0.45)
        hrule = Line([0.0, top_y, 0.0], [total_w, top_y, 0.0],
                    stroke_width=2, color=DIM).set_opacity(0.5)
        vrule = Line([col_w[0], 0.15, 0.0], [col_w[0], -(total_h - 0.15), 0.0],
                    stroke_width=2, color=DIM).set_opacity(0.35)

        whole = VGroup(grid_group, hrule, vrule)
        self.place(whole, pad=pad)
        self.add(whole)
        self.stage_mobs = [whole]

        self._heads = heads
        self._row_labels = row_labels
        self._cells = body
        self._active = None

        for r in range(settled_rows):
            row_labels[r].set_opacity(1.0)
            for c in body[r]:
                c.set_opacity(1.0)
                c.set_color(DIM)

        if animate:
            self.cue("whoosh")
            self.play(Create(hrule), Create(vrule),
                      *[h.animate.set_opacity(1.0) for h in heads], run_time=0.5)
        else:
            for h in heads:
                h.set_opacity(1.0)

    def _reveal_row_label(self, r):
        """A row label is scaffolding like a column header: once it names the
        property being compared it stays bright for the rest of the part."""
        self.cue("pop")
        anims = [self._row_labels[r].animate.set_opacity(1.0)]
        if self._active is not None:
            ar, ac = self._active
            anims.append(self._cells[ar][ac].animate.set_color(DIM))
            self._active = None
        self.play(*anims, run_time=0.35)

    def _reveal_cell(self, r, c):
        """The counted-list fill-in: the cell just named goes to full white,
        whatever was last active dims to this file's muted tone but stays on
        screen — never removed, per CLAUDE.md's rule for progressive lists."""
        anims = [self._cells[r][c].animate.set_opacity(1.0)]
        if self._active is not None:
            ar, ac = self._active
            anims.append(self._cells[ar][ac].animate.set_color(DIM))
        self.play(*anims, run_time=0.35)
        self._active = (r, c)

    def _settle_table(self):
        """The summary (line 82 onward) names nothing new for ~17.5s, so
        there is no later cell to dim the last one spoken. Without this the
        final freeze-frame would show eight muted cells and one still bright
        for no reason — the table should read as ONE finished answer, not as
        a still-in-progress list that happened to stop."""
        if self._active is not None:
            ar, ac = self._active
            self.cue("ding")
            self.play(self._cells[ar][ac].animate.set_color(DIM), run_time=0.4)
            self._active = None

    # ---- timing (copied from the sibling file) ------------------------------ #
    def _line(self, text, end=None):
        new = self.caption(text)
        if getattr(self, "caption_mob", None) is not None:
            self.remove(self.caption_mob)
        self.caption_mob = new
        self.add(new)
        self._cap_end = end

    def clear_stage(self, rt=0.30):
        keep = {getattr(self, "caption_mob", None),
                getattr(self, "background", None),
                getattr(self, "chroma_zone", None)}
        doomed = [m for m in self.mobjects if m not in keep and m is not None]
        if doomed:
            self.play(*[FadeOut(m) for m in doomed], run_time=rt)
        self._card_up = False

    def at(self, t):
        left = float(t) - self.renderer.time
        if left > 0.02:
            self.wait(left)

    def construct(self):
        register_fonts()
        self.caption_mob = None
        self._wcache = {}
        self.stage_mobs = []
        self._active = None

        # cue 0 is the question card; card_lines in meta.json (6) says how
        # far into the transcript it stays up — which lands exactly on
        # HEADER_AT, so the card clears the instant the table starts.
        no_card = str(PART) in set(META.get("no_card", []))
        card_at = float(LINES[0]["start"])
        if not no_card:
            _sheet = ROOT / "assets" / "design" / "question_sheet.png"
            self.question_card(META["question"], META.get("highlight", ""),
                               META.get("years", ""),
                               sheet=_sheet if _sheet.is_file() else None)
        self.at(card_at)

        _cl = META.get("card_lines", 0)
        card_until = -1 if no_card else int(
            _cl[str(PART)] if isinstance(_cl, dict) else _cl)

        if PART == 2:
            # Continuation, not a fresh table: the first 3 rows are already
            # known going into this clip's very first frame, so they are
            # painted straight into their finished (dimmed) state — see
            # `_build_table`'s `settled_rows` note.
            self._build_table(ROWS_ALL, CELLS_ALL,
                              cell_size=TABLE2_CELL_SIZE,
                              label_size=TABLE2_LABEL_SIZE,
                              header_size=TABLE2_HEADER_SIZE,
                              buff_y=TABLE2_BUFF_Y, col_pad=TABLE2_COL_PAD,
                              animate=False, settled_rows=3)

        for i, line in enumerate(LINES):
            self.at(max(0.0, float(line["start"]) - 0.35))
            if i == card_until:
                self.clear_stage()

            if PART == 1:
                if i == HEADER_AT:
                    self._build_table(ROWS, CELLS)
                elif i in ROW_LABEL_AT:
                    self._reveal_row_label(ROW_LABEL_AT[i])
                elif i in CELL_AT:
                    self._reveal_cell(*CELL_AT[i])
                elif i == SETTLE_AT:
                    self._settle_table()
            elif PART == 2:
                if i in ROW_LABEL_AT2:
                    self._reveal_row_label(ROW_LABEL_AT2[i])
                elif i in CELL_AT2:
                    self._reveal_cell(*CELL_AT2[i])
                elif i == SETTLE_AT2:
                    self._settle_table()

            if _UNTIL and float(line["start"]) > _UNTIL:
                break
            self.at(float(line["start"]))
            if i >= card_until:
                self._line(line["text"], line.get("end"))
        self.at(CLIP_END)
        self.report_layout()
