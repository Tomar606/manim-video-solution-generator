"""One PYQ part, rendered from data.

    PYQ_PROJECT=che-c2-la-05 PYQ_PART=1 manim -qh scene_composed.py PyqPart

Nine parts had to be built in one pass, and nine hand-laid scenes is nine
chances to put a label through a beaker. So the layout lives here once and each
part is authored as `beats_part<N>.json` — a list of blocks, each one a type the
scene already knows how to place safely:

    {"at": 4, "type": "points",  "title": "…", "items": ["…", "…"]}
    {"at": 9, "type": "formula", "label": "…", "tex": ["k = \\\\frac{x}{t}"]}
    {"at": 14,"type": "flow",    "items": ["…", "…", "…"]}
    {"at": 20,"type": "compare", "left": ["अम्लीय", ["…"]], "right": [...]}
    {"at": 26,"type": "image",   "src": "images/dry_cell.png", "caption": "…"}
    {"at": 31,"type": "graph",   "kind": "zero_order"}
    {"at": 36,"type": "video",   "brief": "rust creeping across wet iron", "seconds": 8,
              "presenter": "hidden"}

`video` is the one type that draws nothing. It reserves the stage for a Veo clip
generated on this same background plate and laid over the render by
tools/composite.py — for the handful of beats where the thing that has to move is
photoreal or organic and neither Manim nor a still can show it moving. `brief` is
hand-written (it is a judgement about the question, like a figure), and
`video veo <project> --part N` is what fills it.

`at` is an index into the caption track, not a timestamp: the captions come from
the clip's own transcript, so anchoring to them keeps every block on the words
that describe it even when the presenter takes longer than the script did.

Every block goes through `place()`, so none of them can reach the caption above
or the presenter below. The scene's layout guard audits after each one and
writes `layout_violations.json`, which preflight refuses to render past.
"""
from manim import *  # noqa: F403
import json
import os as _os
from pathlib import Path as _Path

import numpy as np

from src.manim_helpers import (ThemedScene, fit_caption, keep_clear, mark_group,
                               norm_point, register_fonts, wrap_measured)

INK, DIM, GOLD = "#FFFFFF", "#B9C6DC", "#FFC15C"
GREEN, VIOLET, CYAN = "#7CE0B0", "#C792EA", "#5BC8F9"

FONT, FONT_W = "Khand", "BOLD"
CAPTION_SIZE, CAPTION_W, CAPTION_TOP = 55, 0.90, 0.090
# STAGE_BOT is derived from where the compositor actually puts the presenter:
# tools/composite.py overlays him at FULL_Y=966 of a 1920-high frame, so his head
# starts at 0.503. The band used to run to 0.600 — a hundred pixels INSIDE him —
# so the layout guard happily passed content that the avatar then covered, which
# is how "Mn: +7 -> +2" ended up behind his head. Keep this above 966/1920 with a
# margin; if the compositor's placement changes, this has to change with it.
STAGE_TOP, STAGE_BOT, STAGE_W = 0.290, 0.492, 0.86
CAPTION_GAP = 0.30

PROJECT = _os.getenv("PYQ_PROJECT", "che-c2-la-05")
PART = int(_os.getenv("PYQ_PART", "1"))
ROOT = _Path(ASSET_ROOT) / "projects" / PROJECT
FIGURES = ROOT / "assets" / "figures"

LINES = json.loads((ROOT / f"lines_part{PART}.json").read_text(encoding="utf-8"))
# PYQ_BATCH=b2 renders the scene-director plan (`beats_b2_part<N>.json`) instead
# of the original beats, so both batches can be built from one project without
# either overwriting the other's plan.
_BATCH = _os.environ.get("PYQ_BATCH", "")
# PYQ_UNTIL=<seconds> stops the scene early. Rendering 132 seconds to use the
# first 14 wasted nine minutes; the card is often all that is wanted when the
# body of the video comes from somewhere else.
_UNTIL = float(_os.environ.get("PYQ_UNTIL", "0") or 0)
_bf = ROOT / (f"beats_b2_part{PART}.json" if _BATCH == "b2" else f"beats_part{PART}.json")
BEATS = json.loads(_bf.read_text(encoding="utf-8"))
META = json.loads((ROOT / "meta.json").read_text(encoding="utf-8"))
CLIP_END = float((META.get("clip_end") or {}).get(str(PART), float(LINES[-1]["start"]) + 3.0))

HILITE = {k: GOLD for k in META.get("hilite", [])}


class PyqPart(ThemedScene):
    CAPTION_MODE = "narration"
    STAGE_BAND = (STAGE_TOP, STAGE_BOT)

    # ---- text ----------------------------------------------------------- #
    def hindi(self, text, size=CAPTION_SIZE, color=INK, weight=FONT_W):
        return Text(text, font=FONT, font_size=size, color=color, weight=weight)

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
        limit = config.frame_width * CAPTION_W
        lines = wrap_measured(text, limit, lambda l: self._measure(l, size))
        g = VGroup(*[Text(l, font=FONT, font_size=size, color=INK,
                          weight=FONT_W, t2c=self._hl(l)) for l in lines])
        g.arrange(DOWN, buff=0.16)
        fit_caption(g, limit)
        g.move_to(norm_point(0.5, CAPTION_TOP))
        g.shift(DOWN * g.height / 2)
        return g

    # ---- layout ----------------------------------------------------------- #
    def stage_box(self):
        top, bot = norm_point(0.5, STAGE_TOP)[1], norm_point(0.5, STAGE_BOT)[1]
        if getattr(self, "caption_mob", None) is not None:
            top = min(top, self.caption_mob.get_bottom()[1] - CAPTION_GAP)
        return (np.array([0., (top + bot) / 2, 0.]),
                config.frame_width * STAGE_W, top - bot)

    MAX_GROW = 2.2          # a two-word block must not become a billboard

    def place(self, mob, y=0.5, pad=0.94, grow=True):
        """Fit a block to the stage band — shrinking it OR growing it.

        This only ever shrank. That was fine when the band was 60% of the frame,
        but the band now stops above the presenter at 0.492, and a short block
        kept its authored font size inside a 388px strip: readable on a desktop
        preview, too small on the phone these are watched on. Growing to fill the
        band is what makes the type mobile-legible without hand-tuning every
        beat's font size.
        """
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

    # ---- graphs ------------------------------------------------------------ #
    def graph(self, kind):
        """The two graphs these questions actually ask for, drawn not generated.

        A graph is the one visual whose MEANING is its shape, so it is built
        from axes and a plotted function rather than an illustration: the
        zero-order line has to be straight and the vapour-pressure curves have
        to meet the atmospheric line at two different temperatures, or the
        figure argues the opposite of the answer.
        """
        ax = Axes(x_range=[0, 5, 1], y_range=[0, 5, 1], x_length=5.0,
                  y_length=3.4, tips=False,
                  axis_config={"stroke_color": DIM, "stroke_width": 3,
                               "include_ticks": False})
        if kind == "zero_order":
            line = ax.plot(lambda x: 4.2 - 0.78 * x, x_range=[0, 4.6],
                           color=CYAN, stroke_width=6)
            xl = Text("समय (t)", font=FONT, font_size=26, color=DIM)
            yl = Text("[A]", font=FONT, font_size=26, color=DIM)
            half = DashedLine(ax.c2p(0, 2.1), ax.c2p(2.7, 2.1),
                              dash_length=0.10).set_stroke(GOLD, 3)
            drop = DashedLine(ax.c2p(2.7, 2.1), ax.c2p(2.7, 0),
                              dash_length=0.10).set_stroke(GOLD, 3)
            tag = Text("t½", font=FONT, font_size=26, color=GOLD
                       ).next_to(ax.c2p(2.7, 0), DOWN, buff=0.16)
            xl.next_to(ax, DOWN, buff=0.20)
            yl.next_to(ax, LEFT, buff=0.20)
            # The tag marks a point ON the axis, so its x is meaningful and the
            # axis label sits under the middle of the same axis — they were
            # drawn straight through each other. The tag keeps its x and is
            # pushed clear; `xl` is passed first because its position is the
            # one that must not move.
            keep_clear([xl, tag])
            body = VGroup(VGroup(ax, line, half, drop, tag), xl, yl)
        else:                                   # boiling-point elevation
            solvent = ax.plot(lambda x: 0.55 * np.exp(0.52 * x),
                              x_range=[0, 4.2], color=CYAN, stroke_width=6)
            solution = ax.plot(lambda x: 0.40 * np.exp(0.52 * x),
                               x_range=[0, 4.6], color=VIOLET, stroke_width=6)
            atm = DashedLine(ax.c2p(0, 3.6), ax.c2p(5, 3.6),
                             dash_length=0.10).set_stroke(GOLD, 3)
            xl = Text("ताप", font=FONT, font_size=26, color=DIM)
            yl = Text("वाष्प दाब", font=FONT, font_size=26, color=DIM)
            xl.next_to(ax, DOWN, buff=0.20)
            yl.next_to(ax, LEFT, buff=0.20)
            body = VGroup(VGroup(ax, solvent, solution, atm), xl, yl)
        return self.place(body)

    # ---- diagrams ---------------------------------------------------------- #
    # Two questions in this batch name a piece of apparatus, and one says
    # "सचित्र" outright. Those are drawn, not generated: every part carries a
    # label, and a generated illustration gets the picture roughly right and the
    # lettering wrong.

    def figure(self, name, draw="scan", hide=None):
        """The question's figure — rebuilt in Manim where we have a builder.

        Tracing the scan (see `tools/figure_from_scan.py`) gets the arrangement
        exactly right, and that is what the builders below are measured from.
        But a trace is the book's ink: at scan resolution its lines wobble and
        its edges are soft, and recoloured white on the dark plate that reads as
        a blurry photocopy rather than as part of the video. So the trace is used
        as the REFERENCE and the figure is redrawn from primitives — same layout,
        same labels, clean strokes, and every stroke animatable on its own.

        The traced scan is the DEFAULT and is what ships: rebuilding the figure
        in Manim gives cleaner strokes, but it is a redrawing, and a redrawing can
        drift from the figure the student actually has in front of them. The
        rebuild stays available behind `"draw": "manim"` on the beat.
        """
        if draw == "manim" and name == "berkeley":
            return self._berkeley_figure()
        if draw == "manim" and name == "boiling":
            return self._boiling_figure()
        return self.scan_figure(name, hide=hide)

    def _boiling_figure(self):
        """क्वथनांक में उन्नयन, drawn rather than traced.

        The book's own graph is traced like every other figure, but at the size
        it gets on a 9:16 stage its scanned curves and hand lettering go muddy —
        so this one is redrawn. The GEOMETRY still comes from the book: two
        vapour-pressure curves, the solution's below the solvent's, both meeting
        the one-atmosphere line, and the two boiling points those meetings drop
        to, with the gap between them marked as delta-Tb.

        The solvent meets the line FIRST (lower temperature): the whole answer is
        that adding a solute pushes the boiling point right, so a figure with the
        curves the other way round argues the opposite of the narration.
        """
        ax = Axes(x_range=[0, 6, 1], y_range=[0, 5, 1], x_length=5.4,
                  y_length=3.5, tips=False,
                  axis_config={"stroke_color": INK, "stroke_width": 3,
                               "include_ticks": False})
        ATM = 3.6
        solvent = ax.plot(lambda x: 0.55 * np.exp(0.52 * x), x_range=[0.2, 4.05],
                          color=CYAN, stroke_width=6)
        solution = ax.plot(lambda x: 0.40 * np.exp(0.52 * x), x_range=[0.2, 4.62],
                           color=VIOLET, stroke_width=6)
        xs = np.log(ATM / 0.55) / 0.52          # solvent  boils here
        xl_ = np.log(ATM / 0.40) / 0.52         # solution boils here
        atm = DashedLine(ax.c2p(0, ATM), ax.c2p(5.2, ATM),
                         dash_length=0.11).set_stroke(GOLD, 3)
        drop_s = DashedLine(ax.c2p(xs, ATM), ax.c2p(xs, 0),
                            dash_length=0.09).set_stroke(DIM, 2.5)
        drop_l = DashedLine(ax.c2p(xl_, ATM), ax.c2p(xl_, 0),
                            dash_length=0.09).set_stroke(DIM, 2.5)
        gap = DoubleArrow(ax.c2p(xs, 1.05), ax.c2p(xl_, 1.05), buff=0,
                          color=GOLD, stroke_width=4,
                          max_tip_length_to_length_ratio=0.22)
        xlab = Text("ताप", font=FONT, font_size=26, color=DIM).next_to(ax, DOWN, buff=0.22)
        ylab = Text("वाष्प दाब", font=FONT, font_size=26, color=DIM
                    ).next_to(ax, LEFT, buff=0.22).rotate(PI / 2)
        rig = VGroup(ax, solvent, solution, atm, drop_s, drop_l, gap, xlab, ylab)

        marks = {}
        for k, pt in {"solvent": ax.c2p(2.6, 0.55 * np.exp(0.52 * 2.6)),
                      "solution": ax.c2p(3.3, 0.40 * np.exp(0.52 * 3.3)),
                      "tb0": ax.c2p(xs, 0), "tb": ax.c2p(xl_, 0),
                      "atm": ax.c2p(0.4, ATM), "gap": ax.c2p((xs + xl_) / 2, 1.05)}.items():
            d = Dot(pt, radius=0.001).set_opacity(0)
            marks[k] = d
            rig.add(d)

        c, w, h = self.stage_box()
        rig.scale(min(w * 0.72 / rig.width, h * 0.80 / rig.height))
        self.place(rig, pad=0.99)
        rig.anchors = marks
        return rig

    def _berkeley_figure(self):
        """बर्कले एवं हार्टले, laid out exactly as the textbook prints it.

        Measured off the scan: a flattened vessel whose middle band is the inner
        tube (जल), with विलयन above and below it, the two tube walls drawn as
        solid bars, the piston a cup on the centre of the top edge with the
        applied pressure arrow landing inside it, the gauge hanging off the
        piston neck by its own pipe, the stopcock funnel rising on the right and
        the capillary bundle leaving to the left.
        """
        def poly(*pts, w=4, colour=INK):
            m = VMobject().set_points_as_corners([np.array([x, y, 0.]) for x, y in pts])
            return m.set_stroke(colour, w)

        # vessel — flat top and bottom, chamfered ends, inner tube across the middle
        top = poly((-2.40, 0.55), (-2.00, 1.35), (2.00, 1.35), (2.40, 0.55))
        bot = poly((-2.40, -0.55), (-2.00, -1.35), (2.00, -1.35), (2.40, -0.55))
        tube = poly((-2.60, 0.55), (-2.60, -0.55), w=4)
        tube_r = poly((2.60, 0.55), (2.60, -0.55), w=4)
        soln_t = Polygon(*[np.array([x, y, 0.]) for x, y in
                           ((-2.40, 0.55), (-2.00, 1.35), (2.00, 1.35), (2.40, 0.55))])
        soln_b = Polygon(*[np.array([x, y, 0.]) for x, y in
                           ((-2.40, -0.55), (-2.00, -1.35), (2.00, -1.35), (2.40, -0.55))])
        for s in (soln_t, soln_b):
            s.set_stroke(width=0).set_fill(VIOLET, 0.13)
        water = Rectangle(width=5.2, height=1.10, stroke_width=0)
        water.set_fill(CYAN, 0.13)

        # the two solid bars ARE the semipermeable wall — the figure's strongest mark
        bars = VGroup(*[Rectangle(width=5.2, height=0.10, stroke_width=0)
                        .set_fill(INK, 1).move_to([0, y, 0]) for y in (0.55, -0.55)])
        # porous wall, hatched at each end of the inner tube
        hatch = VGroup(*[Line([sx * 2.52, y, 0], [sx * 2.22, y, 0]).set_stroke(INK, 2.5)
                         for sx in (-1, 1) for y in (-0.30, -0.15, 0.0, 0.15, 0.30)])

        # piston: a cup on a neck, with the applied pressure landing inside it
        neck = Rectangle(width=0.34, height=0.95).set_stroke(INK, 4).move_to([0, 1.02, 0])
        cup = poly((-0.52, 2.10), (-0.52, 1.50), (0.52, 1.50), (0.52, 2.10))
        fill_line = Line([-0.44, 1.86, 0], [0.44, 1.86, 0]).set_stroke(INK, 2.5)
        press = Arrow([0, 2.92, 0], [0, 2.16, 0], buff=0, color=GOLD, stroke_width=6,
                      max_tip_length_to_length_ratio=0.30)

        # gauge, piped off the neck exactly as the book pipes it
        gpipe = poly((0.17, 1.12), (1.34, 1.12), (1.34, 1.52), w=3.5)
        dial = Circle(radius=0.30).set_stroke(INK, 4).move_to([1.34, 1.82, 0])
        needle = Line([1.34, 1.82, 0], [1.20, 2.02, 0]).set_stroke(INK, 3)

        # stopcock funnel on the right
        rtube = poly((2.60, 0.0), (3.38, 0.0), (3.38, 1.78), w=3.5)
        tap = Square(0.17).set_stroke(INK, 3).set_fill(INK, 1).move_to([3.38, 1.24, 0])
        fun = VGroup(poly((3.38, 1.78), (3.16, 2.12), w=3.5),
                     poly((3.38, 1.78), (3.60, 2.12), w=3.5))

        # capillary bundle leaving to the left and turning down
        cap = VGroup(*[poly((-2.60, dy), (-3.34, dy), (-3.68, dy - 1.05), w=3)
                       for dy in (-0.20, 0.0, 0.20)])

        rig = VGroup(soln_t, soln_b, water, top, bot, tube, tube_r, bars, hatch,
                     neck, cup, fill_line, gpipe, dial, needle, rtube, tap, fun,
                     cap, press)

        # Invisible anchors ride INSIDE the group, so they are scaled and moved
        # by place() along with the drawing. A label can then name the part it
        # points at and its leader stays attached — the traced version got its
        # leaders free because they were part of the scan, and redrawing the
        # figure lost them, leaving every label floating unattached.
        anchors = {"membrane": (-2.62, 0.55), "capillary": (-3.52, -0.86),
                   "funnel": (3.44, 1.98), "pressure": (0.0, 2.62),
                   "gauge": (1.34, 1.82), "water": (0.0, 0.0),
                   "soln_top": (-1.1, 0.95), "soln_bot": (-1.1, -0.95)}
        marks = {k: Dot([x, y, 0], radius=0.001).set_opacity(0)
                 for k, (x, y) in anchors.items()}
        rig.add(*marks.values())

        c, w, h = self.stage_box()
        rig.scale(min(w * 0.70 / rig.width, h * 0.92 / rig.height))
        self.place(rig, pad=0.99)
        rig.anchors = marks
        return rig

    def scan_figure(self, name, hide=None):
        """The figure from the QUESTION'S OWN textbook page, as vector art.

        `tools/figure_from_scan.py` traces the scan the question was extracted
        from, so this is the book's own ink rather than a redrawing of it — which
        matters because the student meets that exact figure in the exam. Being
        vector, it can be drawn on stroke by stroke instead of fading in.

        Recoloured to INK: the trace is black-on-white and the stage is dark, so
        importing it unchanged puts a black figure on a near-black plate.
        """
        fig = SVGMobject(str(FIGURES / f"{name}.svg"))
        fig.set_fill(INK, opacity=1).set_stroke(INK, width=1.0, opacity=1)
        # Some figures letter themselves INSIDE the drawing — the boiling-point
        # graph writes विलायक and विलयन along the two curves. At scan resolution
        # those words trace to solid blobs, and they cannot be erased from the
        # bitmap first: the curve runs through the same box, so erasing takes the
        # line with it and every repair attempt either gapped or deformed the
        # curve the whole figure is about. Dropping the glyphs HERE is safe —
        # each traced word is its own submobject, so the curves are untouched —
        # and the word is then re-typeset over the space it left.
        for zone in hide or []:
            x0, y0, x1, y1 = zone
            ul, w, h = fig.get_corner(UL), fig.width, fig.height
            # Size guard: a zone is matched on the submobject's CENTRE, and a
            # curve spanning the plot has its centre in the middle of the plot
            # too — without this, hiding a word deleted the curve it labelled.
            doomed = [m for m in fig.submobjects
                      if x0 <= (m.get_center()[0] - ul[0]) / w <= x1
                      and y0 <= (ul[1] - m.get_center()[1]) / h <= y1
                      and m.width < w * 0.22 and m.height < h * 0.22]
            fig.remove(*doomed)
        # SVGMobject imports at its own default height, which has nothing to do
        # with the stage — the first render put the apparatus in a 330px band in
        # the middle of a 1080 frame. `place()` only ever scales DOWN, so the
        # figure has to be grown to the stage here before it is placed. Room is
        # left at the sides for the labels that hang off the drawing.
        c, w, h = self.stage_box()
        fig.scale(min(w * 0.62 / fig.width, h * 0.86 / fig.height))
        return self.place(fig, pad=0.99)

    def clamp_to_band(self, mob):
        """Pull a mobject back inside the stage band.

        `place()` clamps whatever it is given, but labels and focus boxes are
        built AFTER the block they belong to and are never passed through it, so
        they escape the band: a label hanging under a diagram and a focus box
        drawn around the last line of a derivation both dipped below the band and
        into the presenter. Raising the band made that visible rather than
        causing it — the content was always going there.
        """
        _, _, _ = self.stage_box()
        top = norm_point(0.5, STAGE_TOP)[1]
        bot = norm_point(0.5, STAGE_BOT)[1]
        if getattr(self, "caption_mob", None) is not None:
            top = min(top, self.caption_mob.get_bottom()[1] - CAPTION_GAP)
        low, high = mob.get_bottom()[1], mob.get_top()[1]
        if low < bot:
            mob.shift(UP * (bot - low))
        elif high > top:
            mob.shift(DOWN * (high - top))
        return mob

    def figure_label(self, fig, fx, fy, text, rel=0.075, align="c"):
        """A label at a fraction of the FIGURE's own box.

        Positions are fractions rather than scene coordinates because `place()`
        rescales the figure to whatever room the stage has left, and a label
        written in scene coordinates lands somewhere else the moment it does.
        The scan already carries the book's leader lines, so these sit at the
        far end of a leader that is part of the drawing.
        """
        ul = fig.get_corner(UL)
        p = ul + np.array([fx * fig.width, -fy * fig.height, 0])
        # `$...$` routes the label through LaTeX. Some figures name their parts
        # with a formula — MnO₂ + C, NH₄Cl+ZnCl₂ — and Devanagari fonts have no
        # subscripts, so those set in Text() come out as tofu. Devanagari must
        # never go INSIDE the maths, so a part named in both is authored as two
        # labels, which is how the book stacks them anyway.
        s = str(text)
        if s.startswith("$") and s.endswith("$"):
            t = MathTex(s[1:-1], color=INK)
        else:
            t = Text(s, font=FONT, font_size=40, color=INK, weight=FONT_W)
        # Sized against a REFERENCE glyph, not against this label's own height.
        # Devanagari height depends on which matras a word happens to carry, so
        # scaling each label to the same box makes "जल" tower over "अर्धपारगम्य".
        # A fixed font size is no good either: the figure is scaled to the stage,
        # so absolute text came out huge on it and the labels ran through each
        # other in the first render.
        ref = Text("क", font=FONT, font_size=40, weight=FONT_W)
        t.scale(rel * fig.height / ref.height)
        edge = {"c": ORIGIN, "l": LEFT, "r": RIGHT}[align]
        t.move_to(p, aligned_edge=edge)
        return t

    def apparatus(self, kind):
        if kind == "berkeley":
            return self._berkeley()
        if kind == "dry_cell":
            return self._dry_cell()
        raise ValueError(f"unknown apparatus: {kind}")

    def _berkeley(self):
        """बर्कले एवं हार्टले — two concentric tubes.

        The inner tube is porous and carries the semipermeable membrane; the
        outer one is gun metal with the piston. Water crosses INWARD-to-OUTWARD
        (into the solution), so the arrow points at the solution, and the
        capillary is on the inner tube, which is what falls.
        """
        outer = RoundedRectangle(width=5.2, height=1.85, corner_radius=0.18
                                 ).set_stroke(DIM, 4)
        soln = Rectangle(width=5.0, height=1.6, stroke_width=0,
                         fill_color="#2E6FA8", fill_opacity=0.45)
        inner = RoundedRectangle(width=3.3, height=0.82, corner_radius=0.12
                                 ).set_stroke(CYAN, 4)
        water = Rectangle(width=3.15, height=0.66, stroke_width=0,
                          fill_color="#8FD3F4", fill_opacity=0.55)
        membrane = DashedLine(inner.get_corner(UL) + RIGHT * 0.06,
                              inner.get_corner(DL) + RIGHT * 0.06,
                              dash_length=0.07).set_stroke(GREEN, 5)
        cap = Line([0, 0, 0], [0, 1.05, 0]).set_stroke(CYAN, 4)
        cap.next_to(inner, UP, buff=0).shift(LEFT * 1.15)
        funnel = Polygon([-0.22, 0, 0], [0.22, 0, 0], [0.06, -0.34, 0],
                         [-0.06, -0.34, 0]).set_stroke(DIM, 3)
        funnel.next_to(inner, UP, buff=0).shift(RIGHT * 1.15).rotate(PI)
        piston = Rectangle(width=0.26, height=0.95).set_stroke(GOLD, 4)
        piston.next_to(outer, UP, buff=-0.10).shift(RIGHT * 2.0)
        arrow = Arrow([-0.5, 0, 0], [0.6, 0, 0], buff=0, color=GREEN,
                      stroke_width=5, max_tip_length_to_length_ratio=0.28)
        arrow.next_to(membrane, RIGHT, buff=0.10)

        soln.move_to(outer.get_center())
        water.move_to(inner.get_center())
        rig = VGroup(outer, soln, inner, water, membrane, cap, funnel,
                     piston, arrow)

        # Labelled, because an unlabelled schematic teaches nothing — the first
        # render was a row of rectangles. Names go OUTSIDE the rig on alternating
        # sides so no leader crosses another.
        def tag(text, colour, target, side, dy):
            t = Text(text, font=FONT, font_size=26, color=colour, weight="BOLD")
            t.next_to(rig, side, buff=0.22).shift(UP * dy)
            arm = DashedLine(t.get_edge_center(-side), target,
                             dash_length=0.06).set_stroke(colour, 2.5)
            return VGroup(arm, t)

        # SHORT labels, tight to the rig. Long ones on both sides widened the
        # group until place() shrank the whole diagram to half the stage — the
        # names were unreadable and the apparatus was a row of small boxes. The
        # caption is already saying the full term while each one appears.
        labels = VGroup(
            tag("झिल्ली", GREEN, membrane.get_center(), LEFT, 0.34),
            tag("सरन्ध्र नली", CYAN, inner.get_bottom(), LEFT, -0.52),
            tag("केशिका", CYAN, cap.get_top(), UP, 0.0),
            tag("पिस्टन", GOLD, piston.get_top(), RIGHT, 0.52),
            tag("विलयन", VIOLET, soln.get_corner(DR) + LEFT * 0.5, RIGHT, -0.42),
        )
        return self.place(VGroup(rig, labels), pad=0.99)

    # Named anchors on each apparatus, so a label can be attached to a PART by
    # name from the beat file. Without these, labelling means writing screen
    # coordinates into the data, which breaks the moment the diagram is rescaled.
    ANCHORS = {
        "dry_cell": {"zinc": (-0.86, 0.55), "rod": (0.06, 0.95),
                     "paste": (-0.62, -0.75), "mix": (0.42, -0.30),
                     "can": (-1.05, 1.35)},
        "berkeley": {"membrane": (-0.60, 0.30), "inner": (-1.30, -0.20),
                     "cap": (-2.40, 0.95), "piston": (2.05, 0.90),
                     "solution": (1.30, -0.55)},
    }

    def label_part(self, rig, kind, part, text, colour=None, side=LEFT, slot=0):
        """One label, joined to a named part of the diagram by a leader.

        Attached by NAME, and to the rig as a whole for placement, so the label
        sits outside the drawing and the leader crosses into it — which is how
        the reference sheets label apparatus, and why nothing lands on top of
        the thing it is naming.
        """
        ax, ay = self.ANCHORS[kind][part]
        target = rig.get_center() + np.array([ax, ay, 0]) * (rig.width / 5.2)
        t = Text(str(text), font=FONT, font_size=26,
                 color=colour or GOLD, weight="BOLD")
        # `slot` staggers labels that share a side. Alternating LEFT/RIGHT alone
        # puts the 1st and 3rd label at the same height on the same side, and
        # they render straight through each other — which is exactly what the
        # first labelled render did.
        t.next_to(rig, side, buff=0.24).shift(UP * (0.62 - slot * 0.78))
        arm = DashedLine(t.get_edge_center(-side), target, dash_length=0.07)
        arm.set_stroke(colour or GOLD, 2.5)
        return VGroup(arm, t)

    def _dry_cell(self):
        """शुष्क सेल, in cross-section — the only view its layers can be
        labelled in. Zinc can = anode = NEGATIVE; carbon rod = cathode =
        positive but inert. Reversing those is the standard mistake."""
        can = RoundedRectangle(width=2.5, height=3.5, corner_radius=0.14
                               ).set_stroke("#C6D3E0", 4)
        zinc = RoundedRectangle(width=2.25, height=3.25, corner_radius=0.12,
                                stroke_width=0, fill_color="#9FB4C7",
                                fill_opacity=0.35)
        paste = RoundedRectangle(width=1.85, height=2.9, corner_radius=0.10,
                                 stroke_width=0, fill_color="#3E7CB1",
                                 fill_opacity=0.40)
        mix = RoundedRectangle(width=1.15, height=2.5, corner_radius=0.08,
                               stroke_width=0, fill_color="#4A4238",
                               fill_opacity=0.75)
        rod = Rectangle(width=0.32, height=2.85, stroke_width=2,
                        stroke_color="#E0C089", fill_color="#6E5B3A",
                        fill_opacity=1.0).shift(UP * 0.12)
        cap = Rectangle(width=0.62, height=0.22, stroke_width=2,
                        stroke_color="#E0C089", fill_color="#E0C089",
                        fill_opacity=1.0)
        cap.next_to(rod, UP, buff=0)
        body = VGroup(can, zinc, paste, mix, rod, cap)
        for m in (zinc, paste, mix):
            m.move_to(can.get_center())
        rod.move_to(can.get_center() + UP * 0.12)
        cap.next_to(rod, UP, buff=0)
        return self.place(body)

    # ---- timing ------------------------------------------------------------ #
    def _line(self, text, end=None):
        new = self.caption(text)
        if getattr(self, "caption_mob", None) is not None:
            self.remove(self.caption_mob)
        self.caption_mob = new
        self.add(new)
        self._cap_end = end

    def reveal_points(self, spec):
        """A list that fills in as the teacher speaks, instead of arriving whole.

        The brief is explicit: when four things are being listed, all four should
        end up on screen — a persistent map — but they should appear as they are
        named, with the current one emphasised and the earlier ones quieter.
        Dumping all four at the first mention gives the student nothing to track;
        replacing the block each time gives them nothing to hold on to.
        """
        title = spec.get("title")
        items = spec["items"]
        rows = VGroup()
        if title:
            rows.add(Text(str(title), font=FONT, font_size=38, color=GOLD,
                          weight="BOLD"))
        marks = ["①", "②", "③", "④", "⑤"]
        bodies = []
        for i, it in enumerate(items[:5]):
            t = str(it)
            # `$...$` is maths, not text. This is the reveal path — the same slip
            # that printed "$\Delta T_b = T_b - T_b^{0}$" verbatim in the
            # क्वथनांक summary, because only `compare` had learned the rule.
            if t.startswith("$") and t.endswith("$"):
                body = MathTex(t[1:-1], color=INK)
                ref = Text("H", font=FONT, font_size=32, weight="MEDIUM")
                body.scale(ref.height / max(MathTex("H").height, 1e-6))
            else:
                body = Text(t, font=FONT, font_size=32, color=INK, weight="MEDIUM")
            line = VGroup(Text(marks[i], font=FONT, font_size=32, color=CYAN),
                          body).arrange(RIGHT, buff=0.22)
            bodies.append(line)
            rows.add(line)
        rows.arrange(DOWN, buff=0.30, aligned_edge=LEFT)
        self.place(rows)
        for b in bodies:
            b.set_opacity(0.0)
        return rows, bodies

    def build_formula_steps(self, spec):
        """A derivation the student watches being CONSTRUCTED, not one that
        arrives finished.

        The brief is explicit: do not show the final equation from the
        beginning, and at any moment the student must be able to answer "what
        changed?". So each line is written when the narration reaches it, the
        line just written carries a box, and the lines above it stay visible but
        go quiet — the worked steps remain as context while exactly one thing
        holds the focus.
        """
        raw = spec["tex"] if isinstance(spec["tex"], list) else [spec["tex"]]
        # A full chemical equation is wider than the stage, so place() fits it by
        # WIDTH and the whole block — heading included — comes out small. Break it
        # at the arrow, the way it would be written on a board, and the block can
        # then be grown to fill the band instead.
        ARROWS = (r"\longrightarrow", r"\rightarrow", r"\to ")
        lines = []
        for t in raw:
            arrow = next((a for a in ARROWS if a in t), None)
            if arrow and len(t) > 34:
                lhs, rhs = t.split(arrow, 1)
                lines.append(lhs.strip())
                lines.append(arrow.strip() + " " + rhs.strip())
            else:
                lines.append(t)
        rows = VGroup()
        if spec.get("label"):
            # sized like a compare-column heading, which reads correctly on a phone
            rows.add(Text(str(spec["label"]), font=FONT, font_size=40,
                          color=GREEN, weight="BOLD"))
        eqs = [MathTex(t).scale(1.05).set_color(INK) for t in lines]
        for e in eqs:
            rows.add(e)
        rows.arrange(DOWN, buff=0.38)
        self.place(rows)
        for e in eqs:
            e.set_opacity(0.0)
        return rows, eqs

    def _asides(self, spec, host):
        """Photographs shown BESIDE a block instead of replacing it.

        A beat replaces whatever is on stage, so a photo authored as its own
        beat wipes the table or derivation underneath it. But a disease photo
        belongs WITH the row that names the disease, and a rust photo belongs
        with the definition it illustrates. An aside is placed clear of the host
        block, appears on its own caption, and is swapped for the next one.
        """
        out = []
        for a in spec.get("images", []):
            img = ImageMobject(str(ROOT / a["src"]))
            side = a.get("side", "right")
            if side == "below":
                # BELOW the block, centred, and large. Beside it, a photograph
                # gets pushed to the frame edge and clipped — which is what the
                # disease photos did. Directly under the table it can be big,
                # and the presenter is hidden for this stretch so nothing has to
                # share the space.
                img.height = float(a.get("h", 4.2))
                img.next_to(host, DOWN, buff=0.42)
                img.set_x(host.get_x())
                _, bw, _ = self.stage_box()
                if img.width > bw * 0.86:
                    img.scale(bw * 0.86 / img.width)
                # Do NOT clamp this one back into the stage band. The band stops
                # above the presenter, and clamping dragged the photo up onto the
                # table it was meant to sit under. The presenter is hidden for
                # this stretch, so the space below the band is free — the only
                # limit is the bottom of the frame.
                floor = -config.frame_height / 2 + 0.45
                if img.get_bottom()[1] < floor:
                    img.shift(UP * (floor - img.get_bottom()[1]))
                if img.get_top()[1] > host.get_bottom()[1] - 0.25:
                    img.next_to(host, DOWN, buff=0.30)
                    img.set_x(host.get_x())
                out.append((int(a["at"]), img))
                continue
            else:
                img.height = float(a.get("h", 2.6))
                img.next_to(host, RIGHT if side == "right" else LEFT, buff=0.45)
            # keep it inside the stage band, never over the caption or presenter
            self.clamp_to_band(img)
            out.append((int(a["at"]), img))
        return out

    def build_beat(self, spec):
        t = spec["type"]
        if t == "points":
            return self.beat_points(spec["items"], spec.get("title"),
                                    hi=spec.get("hi"))
        if t == "formula":
            grp = self.beat_formula(spec["tex"], spec.get("label"))
            self._pending_asides = self._asides(spec, grp)
            return grp
        if t == "flow":
            return self.beat_flow(spec["items"])
        if t == "compare":
            return self.beat_compare(spec["left"], spec["right"])
        if t == "table":
            grp, rows = self.beat_table(spec["cols"], spec["rows"],
                                        size=spec.get("size", 26))
            self._pending_asides = self._asides(spec, grp)
            # rows arrive on their own caption, exactly like a progressive list
            self._pending_reveal = list(zip(spec.get("reveal_at", []), rows))
            if spec.get("reveal_at"):
                for r in rows:
                    r.set_opacity(0.0)
            return grp
        if t == "chain":
            grp, links = self.beat_chain(spec["items"],
                                         direction=spec.get("direction", "down"),
                                         size=spec.get("size", 28),
                                         title=spec.get("title"))
            self._pending_reveal = list(zip(spec.get("reveal_at", []), links))
            if spec.get("reveal_at"):
                for b in links:
                    b.set_opacity(0.0)
            return grp
        if t == "video":
            # Nothing is drawn, and that is the point. A Veo clip is laid over
            # these frames by tools/composite.py — the clip was generated on
            # THIS background plate, so it replaces the picture from VEO_CUT
            # down while the caption above it keeps running. Anything Manim drew
            # here would sit underneath it, invisible except at the two fades
            # where it would flicker into view.
            return VGroup()
        if t == "image":
            return self.beat_image(ROOT / spec["src"], spec.get("caption"))
        if t == "graph":
            return self.graph(spec.get("kind", "zero_order"))
        if t in ("figure", "scan_figure"):
            fig = self.figure(spec["name"], draw=spec.get("draw", "scan"),
                              hide=spec.get("hide"))
            # A सचित्र question's diagram IS the answer, so it takes the band
            # rather than being capped by the generic MAX_GROW that suits a
            # block of text. The dry cell shipped at about a sixth of the frame
            # under a full-size presenter, twice.
            c, bw, bh = self.stage_box()
            want = float(spec.get("fill", 0.92))
            if fig.height > 0 and fig.width > 0:
                k = min((bw * want) / fig.width, (bh * want) / fig.height)
                if k > 1.0:
                    fig.scale(k)
                    fig.move_to(c)
            # Same contract as `apparatus`: built now, revealed one label per
            # caption that names a part.
            self._labels = []
            # The figure and its labels are ONE diagram: विलयन and जल sit inside
            # the vessel's own bands, exactly as the book prints them, so every
            # label reads as a 100% overlap unless they share a layout group.
            tag = id(fig)
            mark_group(fig, tag)
            for spec_l in spec.get("labels", []):
                lab = self.figure_label(fig, spec_l["x"], spec_l["y"],
                                        spec_l["text"],
                                        rel=spec_l.get("rel", 0.075),
                                        align=spec_l.get("align", "c"))
                part = spec_l.get("part")
                anchors = getattr(fig, "anchors", None)
                if part and anchors and part in anchors:
                    tgt = anchors[part].get_center()
                    d = tgt - lab.get_center()
                    n = d / (np.linalg.norm(d) or 1.0)
                    arm = Line(lab.get_boundary_point(n) + n * 0.10, tgt)
                    lab = VGroup(arm.set_stroke(INK, 2.5), lab)
                self.clamp_to_band(lab)
                mark_group(lab, tag)
                self._labels.append((int(spec_l["at"]), lab))
            return fig
        if t == "apparatus":
            rig = self.apparatus(spec["kind"])
            # Labels are BUILT here but revealed later, each on the caption that
            # names its part — a bare diagram with everything labelled at once
            # tells the student nothing about which bit is being discussed.
            self._labels = []
            used = {"L": 0, "R": 0}
            for j, spec_l in enumerate(spec.get("labels", [])):
                side = LEFT if j % 2 == 0 else RIGHT
                key = "L" if j % 2 == 0 else "R"
                lab = self.label_part(rig, spec["kind"], spec_l["part"],
                                      spec_l["text"], side=side,
                                      slot=used[key])
                used[key] += 1
                self._labels.append((int(spec_l["at"]), lab))
            return rig
        raise ValueError(f"unknown beat type: {t}")

    def construct(self):
        # ThemedScene.setup() already registered fonts and painted the theme;
        # calling a setup_theme() of our own would be a second background.
        register_fonts()
        self.caption_mob = None
        self._wcache = {}
        self.stage_mobs = []

        # cue 0 is always the question card; the sheet carries the question.
        # Except for a REPLACEMENT ENDING rendered as its own part: it is spliced
        # onto the middle of a finished video, so opening it on the question card
        # would show the card twice.
        no_card = str(PART) in set(META.get("no_card", []))
        card_at = float(LINES[0]["start"])
        if not no_card:
            self.question_card(META["question"], META.get("highlight", ""),
                               META.get("years", ""),
                               sheet=ROOT / "assets" / "design" / "question_sheet.png")
        self.at(card_at)

        beats = {int(b["at"]): b for b in BEATS}
        first = min(beats) if beats else None
        # The card owns the screen while it is up: no captions over it. Its own
        # heading sits exactly where a caption would go, and the first render
        # had "ये सवाल दो हज़ार चौबीस में" written straight across प्रश्न.
        # per PART: part 1 opens on the question and holds the card through the
        # hook, part 2 only needs it briefly over the recap.
        _cl = META.get("card_lines", first or 0)
        card_until = -1 if no_card else int(
            _cl[str(PART)] if isinstance(_cl, dict) else _cl)
        for i, line in enumerate(LINES):
            self.at(max(0.0, float(line["start"]) - 0.35))
            if i == card_until or i in beats:
                self._pending_asides = []
                self.clear_stage()          # the card goes here, and every beat
                                            # replaces the one before it
                self.stage_mobs = []
            if i in beats:
                spec = beats[i]
                if spec.get("reveal") == "progressive" and spec["type"] == "points":
                    rows, bodies = self.reveal_points(spec)
                    self.stage_mobs.append(rows)
                    self.add(rows)
                    self._pending_reveal = list(zip(spec.get("reveal_at", []), bodies))
                    self._pending_steps = []
                elif spec["type"] == "video":
                    # The stage was cleared above and stays cleared: a Veo clip
                    # covers these frames at composite time. There is nothing to
                    # build, nothing to fade in, and nothing for the layout
                    # guard to audit — an empty VGroup through FadeIn animates a
                    # mobject with no points and warns on every render.
                    self._pending_reveal = []
                    self._pending_steps = []
                    self._labels = []
                elif spec["type"] in ("table", "chain") and spec.get("reveal_at"):
                    mob = self.build_beat(spec)
                    self.stage_mobs.append(mob)
                    self.add(mob)
                    self._pending_steps = []
                    self.audit_layout(spec.get("type", ""))
                elif spec["type"] == "formula" and spec.get("build") == "progressive":
                    self._pending_reveal = []
                    self._labels = []
                    rows, eqs = self.build_formula_steps(spec)
                    self.stage_mobs.append(rows)
                    self.add(rows)
                    self._pending_steps = list(zip(spec.get("reveal_at", []), eqs))
                    self._focus_box = None
                else:
                    # Cleared BEFORE the build, never after: build_beat is what
                    # populates _labels for an apparatus, and resetting it
                    # afterwards wiped every label the diagram had just been
                    # given — the render came out as a bare unlabelled cell.
                    self._pending_reveal = []
                    self._labels = []
                    built = self.build_beat(spec)
                    self.stage_mobs.append(built)
                    if spec["type"] in ("figure", "scan_figure"):
                        # Drawn on, not faded in: the figure is vector, so the
                        # student watches the apparatus being built up the way a
                        # teacher draws it on the board. Kept under two seconds —
                        # `at()` can wait but never rewind, so an animation that
                        # overruns eats into the next caption's window.
                        self.play(Write(built, lag_ratio=0.02), run_time=1.8)
                    else:
                        self.play(FadeIn(built, shift=UP * 0.12), run_time=0.35)
                self.audit_layout(f"beat@{i}")

            # items and diagram labels arrive on the caption that names them
            for at, body in list(getattr(self, "_pending_reveal", [])):
                if at == i:
                    # Set EVERY item's state explicitly from its reveal time.
                    # The old rule dimmed "anything currently brighter than 0.5",
                    # which made the result depend on the order things happened
                    # in — and item ① vanished outright once ② arrived instead of
                    # going quiet. Deterministic beats clever: already revealed
                    # is 0.55, the current one is 1.0, the rest stay hidden.
                    for at2, other in self._pending_reveal:
                        if other is body:
                            continue
                        other.set_opacity(0.55 if at2 <= i else 0.0)
                    self.play(body.animate.set_opacity(1.0), run_time=0.30)
                    # every item revealed so far must still be on screen
                    gone = [j for j, (a2, o) in enumerate(self._pending_reveal, 1)
                            if a2 <= i and o.get_fill_opacity() < 0.2]
                    if gone:
                        self._layout_violations.append(
                            f"t={self.time:6.2f}s REVEALED ITEM VANISHED: {gone}")
            # a photograph that belongs beside the block, not instead of it
            for at, img in list(getattr(self, "_pending_asides", [])):
                if at == i:
                    for _, other in self._pending_asides:
                        if other is not img and other in self.mobjects:
                            self.remove(other)      # one aside at a time
                    self.add(img)
                    self.stage_mobs.append(img)
                    self.play(FadeIn(img, shift=UP * 0.08), run_time=0.30)
            # a derivation advances one line at a time, and the line just
            # written is the one that is boxed
            for at, eq in list(getattr(self, "_pending_steps", [])):
                if at == i:
                    for _, other in self._pending_steps:
                        if other is not eq and other.get_fill_opacity() > 0.5:
                            other.set_opacity(0.45)
                    # set_opacity, not Write: the lines are pre-built at
                    # opacity 0 so the group can be laid out once, and Write
                    # animates a mobject that is still invisible — the first
                    # render showed the focus box around empty space.
                    self.play(eq.animate.set_opacity(1.0), run_time=0.45)
                    box = self.clamp_to_band(
                        SurroundingRectangle(eq, color=GOLD, buff=0.16))
                    box.set_stroke(width=3)
                    old = getattr(self, "_focus_box", None)
                    if old is not None:
                        self.remove(old)
                    self._focus_box = box
                    self.stage_mobs.append(box)
                    self.play(Create(box), run_time=0.30)
            for at, lab in list(getattr(self, "_labels", [])):
                if at == i:
                    self.play(FadeIn(lab, shift=RIGHT * 0.10), run_time=0.30)
                    self.stage_mobs.append(lab)
                    # audit HERE: a diagram label arrives long after its figure
                    # was built, so auditing only at build time inspected the
                    # figure alone and passed four labels lying across it.
                    self.audit_layout("figure-label")
            if _UNTIL and float(line["start"]) > _UNTIL:
                break
            self.at(float(line["start"]))
            if i >= card_until:
                self._line(line["text"], line.get("end"))
        self.at(CLIP_END)
        self.report_layout()

    def clear_stage(self, rt=0.30):
        """Take everything off the stage except the caption and the plate.

        Clearing is automatic and opt-out, exactly as in the hand-built scenes:
        the failure mode of opt-in clearing is a SILENT overlap. Without this
        the question card — which deliberately fills the whole frame — stayed up
        for the entire video with every beat and caption drawn on top of it.
        """
        keep = {getattr(self, "caption_mob", None),
                getattr(self, "background", None),
                getattr(self, "chroma_zone", None)}
        doomed = [m for m in self.mobjects if m not in keep and m is not None]
        if doomed:
            self.play(*[FadeOut(m) for m in doomed], run_time=rt)
        self._card_up = False       # the stage is ours again — resume auditing

    def at(self, t):
        """Advance the clock to an absolute time in the CLIP.

        `self.time` is Manim's own running total, which is what makes the
        caption track line up with the recording: every block and every caption
        is scheduled against the transcript's timestamps, not against how long
        the animations happened to take.
        """
        left = float(t) - self.time
        if left > 0.02:
            self.wait(left)
