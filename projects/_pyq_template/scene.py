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
E_CYAN, ION_GOLD, K_GREEN = "#5BC8F9", "#FFC15C", "#8FE3B0"
ANSWER, REASON = "#7BE3A0", "#FFC15C"   # what the question asks for / why
FONT_UI = "Poppins"      # chain/table bodies use the theme face; labels use Khand
# THE DEVANAGARI LABEL FACE. Poppins mis-sets a reph over a following i-matra:
# in आकर्षित / प्रतिकर्षित the र् hook lands on the ि stroke and at label size the
# two merge — the word reads आकषित. Khand is no better; it is condensed, so the
# same collision is tighter still. Noto Sans Devanagari is drawn for exactly
# this (it is the reference face for Devanagari shaping) and keeps the reph
# clear of the matra at small sizes. Vendored into assets/fonts so a render does
# not depend on which fonts a particular machine happens to have installed.
FONT_LABEL = "Noto Sans Devanagari"
GREEN, VIOLET, CYAN = "#7CE0B0", "#C792EA", "#5BC8F9"
def _lift(hex_colour, k=1.70):
    """A quiet lift of the theme's OWN background, used to fill pole pieces and
    specimen bodies. This was the constant navy #16233C, which is correct on the
    chemistry plate and plainly foreign on the teal physics one — a filled shape
    has to sit on the plate it is actually drawn on, so it follows the theme."""
    h = str(hex_colour).lstrip("#")
    rgb = [int(h[i:i + 2], 16) for i in (0, 2, 4)]
    return "#%02X%02X%02X" % tuple(min(255, int(c * k) + 6) for c in rgb)


# Field lines are THIN STROKES and need more contrast than text, not less.
# #5B9DF9 measured 4.11:1 against the physics plate's content band — below the
# 4.5 floor, on the one element these magnetism diagrams are made of. #9FCFFF
# measures 10.3 on the chemistry plate and 6.9 on the physics one.
FIELD, POLE = "#9FCFFF", "#C9D8F0"
# THE CLASSIC MAGNET, and metal that looks like metal. Every physics book a
# Class 12 student has seen prints the north pole red and the south pole blue,
# so a magnet drawn in the house blue-grey reads as "some block" and has to be
# decoded from its letter. The specimen is a bar of metal and is drawn as one —
# which material it is stays in its coloured LABEL, and that is the honest split:
# the three bodies really are indistinguishable to look at, and only behave
# differently.
MAG_N, MAG_S = "#E0574F", "#4C86DE"
METAL_EDGE, METAL_FILL = "#C9D0D8", "#5C666F"
PLATE = _lift(THEME.get("background", "#0B1B3A"))
# ONE COLOUR PER MATERIAL, taken from the house palette rather than invented. A
# comparison video is only readable if the same substance is the same colour on
# every screen of it, so the beats below look their colour up here by name.
TONES = {"dia": E_CYAN, "para": ION_GOLD, "ferro": K_GREEN,
         "answer": ANSWER, "reason": REASON, "ink": INK, "quiet": DIM,
         "field": FIELD}

FONT, FONT_W = "Khand", "BOLD"
CAPTION_SIZE, CAPTION_W, CAPTION_TOP = 55, 0.90, 0.090
# STAGE_BOT is derived from where the compositor actually puts the presenter:
# tools/composite.py overlays him at FULL_Y=966 of a 1920-high frame, so his head
# starts at 0.503. The band used to run to 0.600 — a hundred pixels INSIDE him —
# so the layout guard happily passed content that the avatar then covered, which
# is how "Mn: +7 -> +2" ended up behind his head. Keep this above 966/1920 with a
# margin; if the compositor's placement changes, this has to change with it.
STAGE_TOP, STAGE_BOT, STAGE_W = 0.290, 0.492, 0.86
# How far down a CONSTRUCTED CELL may reach while the presenter is still on
# screen. STAGE_BOT stops at 0.492 because it was drawn for a full-size
# presenter; during a diagram the compositor shrinks him to SMALL, whose head
# measures 0.765 at the shrunk size (tools/composite.py writes the geometry
# beside every render, so this is read rather than guessed). 0.720 clears it —
# which nearly doubles the band, and is why the cell does not have to choose
# between being legible and letting him be seen.
CELL_FLOOR = 0.720
# And how far UP it may reach. STAGE_TOP=0.290 exists to clear the caption — but
# a cell beat suppresses the caption (see the caption rule in construct), so that
# strip is empty and reserving it just made the cell smaller. Starting at 0.15
# adds a quarter of the frame's height back to the fit.
CELL_TOP = 0.15
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
    # THE AUDIT MUST MEASURE AGAINST THE BAND THE LAYOUT ACTUALLY USED. While a
    # beat is up the caption is suppressed, so stage_box() hands it the taller
    # CELL_TOP..CELL_FLOOR band — and auditing that content against the
    # caption-present band reported every single beat as "OUTSIDE BAND". Sixty
    # bogus entries per render is how a report stops being read, and a real
    # overlap then hides among them.
    @property
    def STAGE_BAND(self):
        if getattr(self, "caption_mob", None) is not None:
            return (STAGE_TOP, STAGE_BOT)
        return (CELL_TOP, CELL_FLOOR)

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
        else:
            # NO CAPTION, NO CAPTION STRIP. STAGE_TOP is where content starts so
            # that it clears the caption — but a beat suppresses the caption, so
            # while one is up that strip is empty and reserving it only shrank
            # the beat. The overall cell reaction was wrapping every line at the
            # arrow and setting them at half size against a band that was mostly
            # unused space.
            #
            # The FLOOR moves with it, for the same reason: no caption means a
            # beat is up, a beat on the stage means the compositor has shrunk
            # the presenter, and STAGE_BOT was measured against a FULL-height
            # one. Leaving the floor there rendered the ladder visibly smaller
            # than the orbital screen beside it in the same video.
            top = norm_point(0.5, CELL_TOP)[1]
            bot = norm_point(0.5, CELL_FLOOR)[1]
        return (np.array([0., (top + bot) / 2, 0.]),
                config.frame_width * STAGE_W, top - bot)

    MAX_GROW = 2.2          # a two-word block must not become a billboard

    def place(self, mob, y=0.5, pad=0.94, grow=True, pad_w=None):
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
        # A WIDE BLOCK RUNS OUT OF WIDTH LONG BEFORE IT RUNS OUT OF HEIGHT.
        # The seven-row comparison table came out at a third of the frame, with
        # type too small to read on a phone, because the band's width is 0.86 of
        # the frame and that capped the scale while half the band's height went
        # unused. `pad_w` spends that spare height by widening. The band's FLOOR
        # is not negotiable — the presenter starts there — but its width is a
        # convention.
        s = min((w * (pad_w or pad)) / mob.width, (h * pad) / mob.height)
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

    def figure(self, name, draw="scan", hide=None, width=0.88):
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
        if draw == "image":
            # A BITMAP FIGURE, not a trace. scan_figure() imports an SVG, but
            # this question's figure is a raster the answer sheet's own diagram
            # was checked against, so it comes in as an image. ImageMobject is
            # NOT a VMobject, so it must ride in a Group — a VGroup silently
            # drops it (CLAUDE.md).
            # ROOT is already projects/<slug>; prefixing it again doubled the path
            img = ImageMobject(str(ROOT / "assets" / f"{name}.png"))
            # SIZED HERE, because place() only ever GROWS a figure (k > 1.0) and
            # this one arrives larger than the frame — left alone it ran off
            # both edges and took the ovaries with it. Narrow on purpose: the
            # margins either side carry fifteen labels.
            img.scale_to_fit_width(config.frame_width * width)
            g = Group(img)
            # NAMED ANCHORS THAT RIDE WITH THE PICTURE. place() rescales the
            # figure to whatever room the stage has, so a leader drawn to a
            # scene coordinate lands somewhere else the moment it does. These
            # are invisible dots INSIDE the group at fractions of the image, so
            # they scale and move with it and a label can point at a PART by
            # name. Fractions come from assets/anchors.json, placed on the
            # picture and checked by eye against the structures.
            import json as _j
            af = ROOT / "anchors.json"
            if af.is_file():
                marks = {}
                ul, w, h = img.get_corner(UL), img.width, img.height
                for key, (fx, fy) in _j.loads(af.read_text(encoding="utf-8")).items():
                    # EVERY ANCHOR GETS A MIRROR TWIN, "<name>#m", at 1-fx.
                    # The female reproductive tract is bilaterally symmetric and
                    # the figure draws both sides, so a part anchored on the left
                    # can be named from the RIGHT margin by pointing at its own
                    # other copy. Without this, ten of the fifteen anchors fell
                    # left of centre and the left column carried ten labels to
                    # the right column's five.
                    for nm, px in ((key, fx), (key + "#m", 1.0 - fx)):
                        d = Dot(radius=0.001).set_opacity(0)
                        d.move_to(ul + np.array([px * w, -fy * h, 0]))
                        marks[nm] = d
                        g.add(d)
                g.anchors = marks
            return g
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
        # USE THE BAND stage_box() ACTUALLY REPORTS. This called stage_box(),
        # threw the answer away, and rebuilt the limits from STAGE_TOP/STAGE_BOT
        # — the CAPTION-PRESENT band. While a beat is up the caption is
        # suppressed and the block is laid out in the taller CELL_TOP..CELL_FLOOR
        # band, so every equation below STAGE_BOT was "out of band" and got
        # shoved upward. For a focus box that meant it slid off the line it
        # surrounds and onto the one above: boxes enclosing the wrong equation,
        # overlapping each other, apparently placed at random.
        c, _, h = self.stage_box()
        top, bot = c[1] + h / 2, c[1] - h / 2
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

    def eq_number(self, n, target):
        """The equation number the way it is actually written by hand: a short
        rule out to the right of the line, then the numeral in a small circle.

        It replaced a heading that read "समीकरण एक" — a label above the equation
        is a title, whereas `——— (1)` beside it is a REFERENCE, which is what the
        narration then uses ("समीकरण one से मान रखने पर").
        """
        num = MathTex(str(n), color=GOLD).scale(0.68)
        ring = Circle(radius=max(num.width, num.height) * 0.86).set_stroke(GOLD, 2.2)
        ring.move_to(num.get_center())
        tag = VGroup(ring, num)
        rule = Line(ORIGIN, RIGHT * 0.62).set_stroke(GOLD, 2.2, 0.9)
        g = VGroup(rule, tag).arrange(RIGHT, buff=0.16)
        g.next_to(target, RIGHT, buff=0.30)
        return g


    def build_formula_morph(self, spec):
        """One equation that TURNS INTO the next, instead of a stack of lines.

        A derivation that is really one quantity being rewritten — ohm-inverse
        becoming one-over-ohm becoming siemens — reads as three separate facts
        when it is printed as three lines, and the student has to work out what
        changed. Morphing says it: the symbol the narration is talking about
        moves, and everything else stays put.

        Returns (group, steps) where `steps` are the MathTex stages. Only the
        first is visible; the reveal loop transforms stage n into stage n+1 at
        the caption named in `reveal_at`.

        SIZED BY THE WIDEST STAGE, not by the one on screen. Each stage is laid
        out at the same centre so nothing jumps, and the scale comes from the
        widest of them — otherwise a two-symbol first stage is grown to fill the
        band and the stage after it, which is longer, overflows the frame. That
        is what put S m^-1 below the stage floor at 959.
        """
        raw = spec["tex"] if isinstance(spec["tex"], list) else [spec["tex"]]
        head = None
        if spec.get("label"):
            head = Text(str(spec["label"]), font=FONT, font_size=40,
                        color=GREEN, weight="BOLD")
        steps = [MathTex(t, color=INK).scale(1.25) for t in raw]
        widest = max(steps, key=lambda m: m.width)
        # the band the azeotrope/membrane graphs use, so the presenter is clear
        TOPR, BOTR = 300, 900
        k = config.frame_height / config.pixel_height
        top_y = (config.pixel_height / 2 - TOPR) * k
        bot_y = (config.pixel_height / 2 - BOTR) * k
        avail_w = config.frame_width * 0.82
        avail_h = (top_y - bot_y) * 0.62
        s = min(avail_w / max(widest.width, 1e-6), avail_h / max(widest.height, 1e-6))
        s = min(s, 1.6)                     # never a billboard
        cy = (top_y + bot_y) / 2 - (0.55 if head is not None else 0.0)
        for m in steps:
            m.scale(s)
            m.move_to([0, cy, 0])
        for m in steps[1:]:
            m.set_opacity(0.0)
        grp = VGroup(*steps)
        if head is not None:
            head.move_to([0, top_y - head.height / 2 - 0.25, 0])
            grp = VGroup(head, *steps)
        return grp, steps

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


    # ---- the galvanic cell, CONSTRUCTED ------------------------------------ #
    # The book's Daniell figure is drawn freehand and traces to a wobbly line,
    # where the dry cell's is ruled and traces clean. Rather than inherit one
    # page's handwriting, this builds the apparatus from primitives — and
    # because every part is placed HERE, the electron and ion routes quote the
    # same constants the wire and the bridge are drawn from instead of being
    # measured off a bitmap. A path measured off the trace's preview PNG was
    # offset by the crop's whitespace margin and the electrons flew through
    # open air; a path that IS the tube cannot.
    CELL = dict(bk_w=1.42, bk_h=1.55, bk_r=0.18, bk_y=-1.55, lbx=-1.22, rbx=1.22,
                rod_w=0.19, rod_top=0.78, wire_y=2.40, br_x=0.52, br_top=0.95,
                g_x=0.92, r_x=-0.92)
    CELL_INK = dict(zn="#C8D4E0", cu="#C87137", zn_sol="#8FA6BC", cu_sol="#2E86C1")

    def _cell_geom(self):
        C = self.CELL
        g = dict(C)
        g["liq"] = C["bk_y"] + 1.05
        g["rod_bot"] = C["bk_y"] + 0.26
        g["znx"] = C["lbx"] - 0.34
        g["cux"] = C["rbx"] + 0.34
        g["br_bot"] = g["liq"] - 0.42
        return g

    def _beaker(self, cx, G):
        w, h, r, y0 = G["bk_w"], G["bk_h"], G["bk_r"], G["bk_y"]
        x0, x1, y1 = cx - w / 2, cx + w / 2, y0 + h
        parts = [Line([x0, y1, 0], [x0, y0 + r, 0]),
                 ArcBetweenPoints([x0, y0 + r, 0], [x0 + r, y0, 0], angle=-PI / 2),
                 Line([x0 + r, y0, 0], [x1 - r, y0, 0]),
                 ArcBetweenPoints([x1 - r, y0, 0], [x1, y0 + r, 0], angle=-PI / 2),
                 Line([x1, y0 + r, 0], [x1, y1, 0]),
                 Line([x0 - 0.07, y1, 0], [x0, y1, 0]),
                 Line([x1, y1, 0], [x1 + 0.07, y1, 0])]
        return VGroup(*parts).set_stroke(INK, 3.2, 1).set_fill(opacity=0)

    def _bridge_path(self, G, right_to_left=True):
        """The route an ion actually takes: up one limb, ROUND THE BEND, down the
        other. Built from the same primitives as the bridge, so a dot cannot
        leave the tube — corner points alone gave a chord across the top and the
        ions cut horizontally through open air above the arch."""
        bx, bt, bb = G["br_x"], G["br_top"], G["br_bot"]
        a, b = (bx, -bx) if right_to_left else (-bx, bx)
        arc = ArcBetweenPoints([a, bt, 0], [b, bt, 0], angle=PI if right_to_left else -PI)
        path = VMobject()
        path.append_points(Line([a, bb, 0], [a, bt, 0]).get_points())
        path.append_points(arc.get_points())
        path.append_points(Line([b, bt, 0], [b, bb, 0]).get_points())
        return path

    def cell_rig(self):
        G = self._cell_geom()
        C = self.CELL_INK
        beakers = VGroup(self._beaker(G["lbx"], G), self._beaker(G["rbx"], G))
        liq = VGroup()
        for cx, col in ((G["lbx"], C["zn_sol"]), (G["rbx"], C["cu_sol"])):
            r = Rectangle(width=G["bk_w"] - 0.10, height=G["liq"] - (G["bk_y"] + 0.05))
            r.set_fill(col, 0.5).set_stroke(width=0)
            r.move_to([cx, (G["liq"] + G["bk_y"] + 0.05) / 2, 0])
            liq.add(r)
        rods = VGroup()
        for x, col in ((G["znx"], C["zn"]), (G["cux"], C["cu"])):
            r = Rectangle(width=G["rod_w"], height=G["rod_top"] - G["rod_bot"])
            r.set_fill(col, 0.85).set_stroke(INK, 2.0, 1)
            r.move_to([x, (G["rod_top"] + G["rod_bot"]) / 2, 0])
            rods.add(r)
        bx, bt, bb = G["br_x"], G["br_top"], G["br_bot"]
        bridge = VGroup(Line([-bx, bb, 0], [-bx, bt, 0]),
                        ArcBetweenPoints([-bx, bt, 0], [bx, bt, 0], angle=-PI),
                        Line([bx, bt, 0], [bx, bb, 0])).set_stroke(INK, 11, 1)
        wy, gx, rx = G["wire_y"], G["g_x"], G["r_x"]
        zig = VMobject().set_points_as_corners(
            [[rx - 0.42, wy, 0]] +
            [[rx - 0.42 + i * 0.12, wy + (0.16 if i % 2 else -0.16), 0] for i in range(1, 8)] +
            [[rx + 0.42, wy, 0]])
        circ = Circle(radius=0.26).move_to([gx, wy, 0])
        wire = VGroup(Line([G["znx"], G["rod_top"], 0], [G["znx"], wy, 0]),
                      Line([G["znx"], wy, 0], [rx - 0.42, wy, 0]), zig,
                      Line([rx + 0.42, wy, 0], [gx - 0.26, wy, 0]), circ,
                      Line([gx + 0.26, wy, 0], [G["cux"], wy, 0]),
                      Line([G["cux"], G["rod_top"], 0], [G["cux"], wy, 0]))
        wire.set_stroke(INK, 3.2, 1).set_fill(opacity=0)
        gl = Text("G", font=FONT, font_size=26, color=INK).move_to(circ.get_center())
        return VGroup(beakers, liq, rods, bridge, wire, gl), G


    def start_flow(self, kind):
        """Dots travelling a route, as a LOOPING UPDATER rather than an
        animation. `play()` would block, and at() can wait but never rewind — a
        three-second electron run placed on a caption would eat the next one. As
        an updater the motion simply continues underneath while the teacher goes
        on talking, which is also what the mechanism actually does."""
        from manim.animation.updaters.mobject_update_utils import turn_animation_into_updater
        st = getattr(self, "_cell", None)
        if not st:
            return VGroup()
        G, P, k = st["G"], st["P"], st["k"]

        def route(pts):
            v = VMobject().set_points_as_corners([P(x, y) for x, y in pts])
            return v

        specs = {
            # up out of the zinc, along the wire through G, down into the copper
            "electrons": (route([(G["znx"], 0.0), (G["znx"], G["wire_y"]),
                                 (G["cux"], G["wire_y"]), (G["cux"], 0.0)]),
                          E_CYAN, 7, 3.2, 0.085),
            # Zn2+ leaving the rod INTO its solution
            "zn_ions": (route([(G["znx"] + 0.10, G["liq"] - 0.55),
                               (G["lbx"] + 0.55, G["liq"] - 0.80)]), ION_GOLD, 4, 2.4, 0.065),
            # Cu2+ arriving AT the rod and plating out
            "cu_ions": (route([(G["rbx"] - 0.55, G["liq"] - 0.80),
                               (G["cux"] - 0.10, G["liq"] - 0.55)]), ION_GOLD, 4, 2.4, 0.065),
            # NO3- toward the ANODE, K+ toward the CATHODE
            "no3": (self._scaled_bridge(True), INK, 3, 3.4, 0.065),
            "k": (self._scaled_bridge(False), K_GREEN, 3, 3.4, 0.065),
        }
        if kind not in specs:
            return VGroup()
        path, col, n, period, r = specs[kind]
        ds = VGroup()
        for j in range(n):
            d = Dot(radius=r * k, color=col).set_stroke(col, 6, 0.30, background=True)
            d.move_to(path.point_from_proportion(0))
            anim = MoveAlongPath(d, path, run_time=period, rate_func=linear)
            turn_animation_into_updater(anim, cycle=True, delay=j * period / n)
            ds.add(d)
        self.add(ds)
        return ds

    def _scaled_bridge(self, right_to_left):
        st = self._cell
        G, P = st["G"], st["P"]
        bx, bt, bb = G["br_x"], G["br_top"], G["br_bot"]
        a, b = (bx, -bx) if right_to_left else (-bx, bx)
        arc = ArcBetweenPoints(P(a, bt), P(b, bt), angle=PI if right_to_left else -PI)
        path = VMobject()
        path.append_points(Line(P(a, bb), P(a, bt)).get_points())
        path.append_points(arc.get_points())
        path.append_points(Line(P(b, bt), P(b, bb)).get_points())
        return path


    # ---- orbital-box diagrams ---------------------------------------------- #
    # Boxes and arrows are the one figure every textbook draws identically, so
    # unlike an apparatus there is no book-specific shape to inherit. What must
    # match is the layout the marker expects: 3d as five boxes, then 4s, then 4p
    # as three, and a brace under EXACTLY the orbitals that hybridise.
    OBW = 0.42                     # one orbital box; the diagram is the answer,
                                   # so everything else is sized around it
    def _electron(self, up=True):
        """NOT manim's Arrow: Arrow.scale() holds its tip size constant, so
        scale_to_fit_height() does not shrink it and the arrow hangs out of both
        ends of its box. A Line with an explicit tip scales like anything else."""
        h = self.OBW * 0.62
        a, b = ([0,-h/2,0],[0,h/2,0]) if up else ([0,h/2,0],[0,-h/2,0])
        ln = Line(a, b).set_stroke(E_CYAN if up else ION_GOLD, 2.4)
        ln.add_tip(tip_length=h*0.30, tip_width=h*0.26)
        if ln.height > h:
            ln.scale(h / ln.height)
        return ln

    def _orow(self, spec, x0, tag, ring=()):
        boxes, els, rings = VGroup(), VGroup(), VGroup()
        for i, c in enumerate(spec):
            b = Square(self.OBW).set_stroke(INK, 2.0).set_fill(opacity=0)
            b.move_to([x0 + i*self.OBW, 0, 0]); boxes.add(b)
            if c and c != ".":
                g = (VGroup(self._electron(True)) if c == "u" else
                     VGroup(self._electron(True).shift(LEFT*self.OBW*0.17),
                            self._electron(False).shift(RIGHT*self.OBW*0.17)))
                g.move_to(b.get_center()); els.add(g)
            if i in ring:
                rings.add(SurroundingRectangle(b, buff=0.012, color=ANSWER, stroke_width=2.0))
        cap = MathTex(tag, color="#C9D8F0").scale(0.50).next_to(boxes, UP, buff=0.085)
        return VGroup(boxes, els, rings, cap), boxes

    def _shape(self, kind):
        c = ANSWER
        if kind == "octa":
            t,bo,l,r,f_,bk = [0,.74,0],[0,-.74,0],[-.66,0,0],[.66,0,0],[-.22,-.15,0],[.26,.17,0]
            e = ((t,l),(t,r),(t,f_),(t,bk),(bo,l),(bo,r),(bo,f_),(bo,bk),(l,f_),(f_,r),(r,bk),(bk,l))
            pts = (t,bo,l,r,f_,bk)
        else:
            a,b,cc,d = [-.60,-.40,0],[.60,-.40,0],[.10,.13,0],[0,.70,0]
            e = ((a,b),(a,d),(b,d),(a,cc),(b,cc),(cc,d)); pts = (a,b,cc,d)
        g = VGroup(*[Line(x,y,stroke_width=2.4,color=c) for x,y in e])
        g.add(*[Dot(q, radius=0.045, color=c) for q in pts])
        return g

    ORB_RUNGS = ["अवस्था · विन्यास", "लिगेण्ड", "युग्मन", "संकरण", "ज्यामिति"]
    def _rail(self, lit=()):
        chips = VGroup()
        for i, t in enumerate(self.ORB_RUNGS):
            on = i in lit
            tt = Text(t, font=FONT_UI, font_size=14, color=INK if on else "#38507A")
            b = SurroundingRectangle(tt, buff=0.075, color=ANSWER if on else "#38507A")
            b.set_stroke(width=1.5).set_fill("#0E2438", 0.7 if on else 0.3)
            chips.add(VGroup(b, tt))
        chips.arrange(RIGHT, buff=0.085)
        ar = VGroup(*[Line(a.get_right(), b.get_left(), stroke_width=1.2, color="#38507A")
                      for a, b in zip(chips, chips[1:])])
        g = VGroup(chips, ar)
        return g.scale(min(1.0, (config.frame_width*0.94)/g.width))


    # ---- comparing materials in a field ------------------------------------ #
    # A comparison question is answered by a PICTURE OF THE DIFFERENCE: the same
    # body drawn the same way several times with only the physics changed. These
    # five beats exist so that picture is DATA rather than a scene hand-built per
    # project — and so the thing that differs is the drawing, never just the
    # caption underneath it.

    def tone(self, name, default=INK):
        return TONES.get(str(name or ""), default)

    def pole_piece(self, x, label, w=0.34, h=1.30):
        """A pole piece with a hatched face, the way the textbook draws it."""
        col = MAG_N if label == "N" else MAG_S
        body = Rectangle(width=w, height=h).set_stroke(col, 2.6).set_fill(col, 0.85)
        body.move_to([x, 0, 0])
        fx = x + (w / 2 if label == "N" else -w / 2)
        dx = 0.12 if label == "N" else -0.12
        hatch = VGroup(*[Line([fx, y, 0], [fx + dx, y - 0.10, 0],
                              stroke_width=1.6, color=col).set_opacity(0.8)
                         for y in np.linspace(-h / 2 + 0.10, h / 2 - 0.02, 9)])
        t = Text(label, font=FONT, font_size=26, color=INK, weight=FONT_W)
        return VGroup(body, hatch, t.move_to(body.get_center()))

    def field_lines(self, x0, x1, ys, route=None, colour=FIELD, width=2.0,
                    tips=True):
        """Field lines left to right, each displaced by ``route(y, t)``.

        The displacement IS the physics: a diamagnetic body pushes the lines out
        of itself, a paramagnetic one draws them slightly in, a ferromagnetic one
        crowds them in hard. Three identical line patterns with three different
        captions under them teach nothing.
        """
        g = VGroup()
        for y in ys:
            pts = [[x0 + t * (x1 - x0), y + (route(y, t) if route else 0.0), 0]
                   for t in np.linspace(0, 1, 60)]
            ln = VMobject().set_points_smoothly([np.array(q) for q in pts])
            g.add(ln.set_stroke(colour, width, 1))
            if tips:
                tip = Triangle().scale(0.05).set_fill(colour, 1).set_stroke(width=0)
                g.add(tip.rotate(-PI / 2).move_to(pts[len(pts) // 5]))
        return g

    @staticmethod
    def flux_route(kind):
        """``expel`` / ``weak`` / ``strong`` -> what the lines do at the body."""
        k = {"expel": -1, "weak": 1, "strong": 3}.get(str(kind), 0)
        def f(y, t):
            env = np.exp(-((t - 0.5) ** 2) / 0.030)      # only near the body
            if k < 0:
                return 0.30 * env * np.sign(y or 1)      # pushed OUT
            if k == 0:
                return 0.0
            return (-min(abs(y), 0.34) * (0.55 if k == 1 else 0.92)
                    * env * np.sign(y or 1))
        return f

    def bar_magnet(self, w=1.70, h=0.56):
        """A bar magnet carrying its poles INSIDE it."""
        sh = Rectangle(width=w / 2, height=h).set_stroke(MAG_S, 2.4).set_fill(MAG_S, 0.85)
        nh = Rectangle(width=w / 2, height=h).set_stroke(MAG_N, 2.4).set_fill(MAG_N, 0.85)
        sh.move_to([-w / 4, 0, 0]); nh.move_to([w / 4, 0, 0])
        return VGroup(sh, nh,
                      Text("S", font=FONT, font_size=19, color=INK,
                           weight=FONT_W).move_to(sh),
                      Text("N", font=FONT, font_size=19, color=INK,
                           weight=FONT_W).move_to(nh))

    @staticmethod
    def force_arrow(length, toward, colour):
        """NOT manim's Arrow: Arrow.scale() deliberately holds its tip size
        constant, so a scaled one comes out all head and hangs out of its box."""
        d = -1 if toward else 1
        ln = Line([0, 0, 0], [d * length, 0, 0]).set_stroke(colour, 3.2, 1)
        ln.add_tip(tip_length=0.16, tip_width=0.15)
        return ln

    @staticmethod
    def moment(angle, size=0.30, colour=INK, w=2.2):
        """One atomic moment, same construction and for the same reason."""
        ln = Line([0, -size / 2, 0], [0, size / 2, 0]).set_stroke(colour, w, 1)
        ln.add_tip(tip_length=size * 0.36, tip_width=size * 0.30)
        return ln.rotate(angle)

    def beat_magnet(self, spec):
        """What a body DOES near a magnet — and it does it, rather than being
        labelled with an arrow saying it would.

        All three start at the SAME distance, because a comparison in which the
        answer is already baked into the starting positions is not a comparison.
        On its own caption each body MOVES: the diamagnetic one drifts away, the
        paramagnetic one creeps in, the ferromagnetic one is pulled hard onto the
        pole. Distance travelled is the physics, and it is the thing the student
        remembers. `travel` is read by construct(), which plays the move and the
        label together.
        """
        rows, items = VGroup(), []
        start = float(spec.get("start_gap", 1.95))
        for r in spec["rows"]:
            col = self.tone(r.get("tone"))
            g = VGroup(self.bar_magnet().move_to([-1.85, 0, 0]))
            box = RoundedRectangle(corner_radius=0.08, width=0.78, height=0.78)
            box.set_stroke(METAL_EDGE, 3.2).set_fill(METAL_FILL, 1)
            box.move_to([-1.85 + start, 0, 0])
            gap = float(r.get("gap", start))
            dx = gap - start                      # where it ENDS UP, relative
            toward = bool(r.get("toward", True))
            ln = float(r.get("force", 0.40))
            a = self.force_arrow(ln, toward, col)
            # the arrow sits over the body's DESTINATION, so it reads as "this
            # way, to here" rather than fighting the body for the same space.
            a.move_to(box.get_center() + RIGHT * dx + UP * 0.66
                      + RIGHT * ((-1 if toward else 1) * ln / 2))
            # A FIXED RIGHT EDGE on every row. Without it arrange() centres each
            # row on its own width and the magnets stop lining up, which is the
            # one thing this frame is comparing.
            g.add(box, a, Dot([1.30, 0, 0], radius=0.001).set_opacity(0))
            cap = VGroup(Text(r["name"], font=FONT, font_size=23, color=col,
                              weight=FONT_W),
                         Text(r["verdict"], font=FONT_LABEL, font_size=18, color=DIM)).arrange(RIGHT, buff=0.22)
            row = VGroup(g, cap).arrange(DOWN, buff=0.16)
            rows.add(row)
            item = VGroup(a, cap)
            item.travel = (box, dx)
            items.append(item)
        rows.arrange(DOWN, buff=0.42)
        return rows, items

    def beat_poles(self, spec):
        """Bodies between two poles, one row per material.

        ``body: ellipse`` routes the field lines around or into the specimen;
        ``body: bar`` keeps the lines straight and turns the specimen instead —
        a suspended rod seen from above.
        """
        rows, items = VGroup(), []
        for r in spec["rows"]:
            col = self.tone(r.get("tone"))
            g = VGroup(self.pole_piece(-1.75, "N", w=0.30, h=1.05),
                       self.pole_piece(1.75, "S", w=0.30, h=1.05))
            if r.get("body", "ellipse") == "bar":
                g.add(self.field_lines(-1.56, 1.56, [-0.50, 0.50], None,
                                       FIELD, 1.8))
                perp = r.get("orient") == "perp"
                bar = Rectangle(width=0.24 if perp else 1.15,
                                height=0.86 if perp else 0.24)
                hold = bar.set_stroke(METAL_EDGE, 3.0).set_fill(METAL_FILL, 1)
                g.add(hold)
            else:
                flux = r.get("flux", "weak")
                g.add(self.field_lines(-1.74, 1.74,
                                       [-0.46, -0.16, 0.16, 0.46],
                                       self.flux_route(flux)))
                e = Ellipse(width=1.15, height=0.66).set_stroke(col, 2.8)
                # ONLY the diamagnetic body is genuinely empty. Through a para or
                # ferro body the flux is CONTINUOUS, so masking it there breaks
                # every line at the outline and the picture reads as a mistake.
                e.set_fill(PLATE, 1.0 if flux == "expel" else 0.0)
                hold = VGroup(e)
                if flux == "strong":
                    hold.add(self.field_lines(-0.50, 0.50, [-0.10, 0.10], None,
                                              FIELD, 1.6, tips=False))
                g.add(hold)
            cap = VGroup(Text(r["name"], font=FONT, font_size=23, color=col,
                              weight=FONT_W))
            if r.get("note"):
                cap.add(Text(r["note"], font=FONT_LABEL, font_size=17, color=DIM))
            # the perpendicular / parallel mark is exam vocabulary, so it rides
            # in the CAPTION. Placed on the diagram it sat on a field line.
            if r.get("maths"):
                cap.add(MathTex(r["maths"], color=col).scale(0.52))
            cap.arrange(RIGHT, buff=0.20)
            row = VGroup(g, cap).arrange(DOWN, buff=0.12)
            rows.add(row)
            # the poles and the field are the SET-UP; the suspended body's
            # orientation and its name are the answer.
            items.append(VGroup(hold, cap))
        rows.arrange(DOWN, buff=0.34)
        return rows, items

    def beat_axis(self, spec):
        """An axis carrying POSITION and a legend carrying the words.

        "less than one / a little more / very much more" is three sentences a
        student has to hold apart; on one axis it is a single picture. Hanging
        the words over the axis instead made the notes collide and sized the
        whole frame by the longest of them.
        """
        tick = spec.get("tick", {})
        tx = float(tick.get("x", 0.0))
        ax = VGroup()
        ln = Line([-2.35, 0, 0], [2.55, 0, 0]).set_stroke(DIM, 2.4, 1)
        ln.add_tip(tip_length=0.16, tip_width=0.14)
        ax.add(ln, DashedLine([tx, -0.30, 0], [tx, 0.92, 0], dash_length=0.07
                              ).set_stroke(DIM, 1.8, 1))
        if tick.get("label"):
            ax.add(MathTex(str(tick["label"]), color=DIM).scale(0.60)
                   .move_to([tx, -0.52, 0]))
        marks, legend = VGroup(), VGroup()
        for rd in spec["readings"]:
            col = self.tone(rd.get("tone"))
            x = float(rd["x"])
            marks.add(VGroup(Dot([x, 0, 0], radius=0.075, color=col),
                             MathTex(str(rd["maths"]), color=col).scale(0.60)
                             .move_to([x, 0.62, 0])))
            row = VGroup(Dot(radius=0.075, color=col),
                         Text(rd["name"], font=FONT, font_size=25, color=col,
                              weight=FONT_W))
            if rd.get("note"):
                row.add(Text(rd["note"], font=FONT_LABEL, font_size=18, color=DIM))
            legend.add(row.arrange(RIGHT, buff=0.20))
        legend.arrange(DOWN, buff=0.26, aligned_edge=LEFT)
        ax.add(marks)
        grp = VGroup(ax, legend).arrange(DOWN, buff=0.55)
        # a reading is its mark AND its legend line: they arrive together, so
        # the axis never shows a dot whose name has not been said yet.
        pairs = [VGroup(m, l) for m, l in zip(marks, legend)]
        return grp, pairs

    def beat_domains(self, spec):
        """What the moments do once the field is taken away. Whether a permanent
        magnet can be made is a CONSEQUENCE of that, not a yes/no column."""
        rng = np.random.default_rng(int(spec.get("seed", 7)))
        rows, items = VGroup(), []
        for r in spec["rows"]:
            col = self.tone(r.get("tone"))
            kind = r.get("kind", "random")
            box = Rectangle(width=3.15, height=0.92, stroke_width=2.6
                            ).set_stroke(METAL_EDGE).set_fill(METAL_FILL, 1)
            inner = VGroup()
            for ri in range(2):
                for c in range(7):
                    at = [-1.05 + c * 0.35, 0.20 - ri * 0.40, 0]
                    if kind == "none":
                        inner.add(Dot(at, radius=0.048, color=DIM))
                    elif kind == "random":
                        inner.add(self.moment(rng.uniform(0, TAU), 0.30, col)
                                  .move_to(at))
                    else:
                        # S on the left, N on the right, so the moments point
                        # RIGHT: inside a magnetised body they run S to N.
                        inner.add(self.moment(-PI / 2, 0.32, col, 2.6).move_to(at))
            body = VGroup(box, inner)
            if kind == "aligned":
                # poles INSIDE the body. Hung outside they fall past the frame
                # edge the moment the rows are left-aligned.
                body.add(Text("S", font=FONT, font_size=19, color=DIM,
                              weight=FONT_W).move_to(box.get_left() + RIGHT * 0.20),
                         Text("N", font=FONT, font_size=19, color=DIM,
                              weight=FONT_W).move_to(box.get_right() + LEFT * 0.20))
            ok = bool(r.get("ok"))
            mark = VGroup()
            if ok:
                mark.add(Line([-0.10, 0, 0], [-0.02, -0.09, 0]).set_stroke(K_GREEN, 3.4),
                         Line([-0.02, -0.09, 0], [0.14, 0.13, 0]).set_stroke(K_GREEN, 3.4))
            else:
                mark.add(Line([-0.10, 0.10, 0], [0.10, -0.10, 0]).set_stroke(DIM, 3.0),
                         Line([-0.10, -0.10, 0], [0.10, 0.10, 0]).set_stroke(DIM, 3.0))
            right = VGroup(Text(r["name"], font=FONT, font_size=23, color=col,
                                weight=FONT_W),
                           Text(r["why"], font=FONT_LABEL, font_size=15, color=DIM),
                           VGroup(mark, Text(r["verdict"], font=FONT_LABEL,
                                             font_size=17,
                                             color=K_GREEN if ok else DIM)
                                  ).arrange(RIGHT, buff=0.14))
            right.arrange(DOWN, buff=0.10, aligned_edge=LEFT)
            row = VGroup(body, right).arrange(RIGHT, buff=0.34)
            rows.add(row)
            items.append(VGroup(inner, right))
        rows.arrange(DOWN, buff=0.40, aligned_edge=LEFT)
        return rows, items

    def beat_photos(self, spec):
        """Real photographs beside their label.

        A schematic asserts; a photograph proves — iron filings ARE the field
        lines a diagram only claims, and a student has never seen bismuth. Files
        come from tools/fetch_photos.py, which keeps only licences permitting
        commercial use; every one has an author line in credits.json.

        Returns a Group, not a VGroup: ImageMobject is not a VMobject and putting
        one in a VGroup fails deep inside arrange().
        """
        rows, items = Group(), []
        tall = float(spec.get("size", 1.45))
        wide = float(spec.get("wide", 1.85))
        for r in spec["rows"]:
            col = self.tone(r.get("tone"))
            im = ImageMobject(str(ROOT / r["src"]))
            im.width = wide
            if im.height > tall:
                im.height = tall
            fr = Rectangle(width=im.width + 0.05, height=im.height + 0.05
                           ).set_stroke(col, 2.0, 0.9).move_to(im.get_center())
            txt = VGroup(Text(r["name"], font=FONT, font_size=25, color=col,
                              weight=FONT_W))
            if r.get("note"):
                txt.add(Text(r["note"], font=FONT_LABEL, font_size=18, color=INK))
            txt.arrange(DOWN, buff=0.14, aligned_edge=LEFT)
            row = Group(Group(im, fr), txt).arrange(RIGHT, buff=0.36)
            rows.add(row); items.append(row)
        rows.arrange(DOWN, buff=0.38, aligned_edge=LEFT)
        return rows, items

    def beat_gradient(self, spec):
        """A NON-UNIFORM field: one pole pointed, one flat, so the lines really
        do crowd at the sharp pole rather than being labelled as if they did.

        The strong pole is drawn on the LEFT, so a body drawn toward the strong
        field moves left. Getting that backwards passes every check and teaches
        the wrong thing, which is exactly what happened the first time.
        """
        g = VGroup()
        tip = Polygon([-2.05, 0.62, 0], [-2.05, -0.62, 0], [-1.15, 0, 0])
        g.add(tip.set_stroke(MAG_N, 2.6).set_fill(MAG_N, 0.85),
              Text("N", font=FONT, font_size=24, color=INK,
                   weight=FONT_W).move_to([-1.72, 0, 0]))
        flat = Rectangle(width=0.34, height=1.55).set_stroke(MAG_S, 2.6)
        flat.set_fill(MAG_S, 0.85).move_to([2.05, 0, 0])
        g.add(flat, Text("S", font=FONT, font_size=24, color=INK,
                         weight=FONT_W).move_to([2.05, 0, 0]))
        for ye in np.linspace(-0.62, 0.62, 9):
            pts = [[-1.13, ye * 0.10, 0], [0.2, ye * 0.62, 0], [1.86, ye, 0]]
            ln = VMobject().set_points_smoothly([np.array(q) for q in pts])
            g.add(ln.set_stroke(FIELD, 1.7, 1))
        g.add(Text(spec.get("strong", "प्रबल"), font=FONT_LABEL, font_size=17,
                   color=DIM).move_to([-1.35, 1.02, 0]),
              Text(spec.get("weak", "दुर्बल"), font=FONT_LABEL, font_size=17,
                   color=DIM).move_to([1.55, 1.02, 0]))
        moves, items = VGroup(), []
        for r in spec["rows"]:
            col = self.tone(r.get("tone"))
            to_strong = bool(r.get("to_strong", True))
            ln = float(r.get("force", 0.62))
            a = self.force_arrow(ln, to_strong, col)
            chip = Rectangle(width=0.30, height=0.15).set_stroke(METAL_EDGE, 2).set_fill(METAL_FILL, 1)
            chip.next_to(a, RIGHT if to_strong else LEFT, buff=0.06)
            row = VGroup(VGroup(chip, a),
                         Text(r["name"], font=FONT, font_size=20, color=col,
                              weight=FONT_W),
                         Text(r["verdict"], font=FONT_LABEL, font_size=16, color=DIM))
            moves.add(row.arrange(DOWN, buff=0.08)); items.append(row)
        moves.arrange(RIGHT, buff=0.42)
        return VGroup(g, moves).arrange(DOWN, buff=0.44), items

    # ---- the Gaussian sphere ----------------------------------------------- #
    # A closed surface with the charge at its CENTRE, the field crossing it
    # perpendicularly, and one area element on it. verification.md for
    # PHY-C1-LA-01 is explicit about the traps: arrows that stop at the rim
    # (then it reads as a disc, not a closed surface), a flat dS tile whose
    # normal is tangential, and the charge drawn off-centre — which destroys the
    # symmetry the whole derivation rests on.

    GS_RAD, GS_PHI, GS_SQUASH = 1.62, 52 * DEGREES, 0.30

    def gauss_ball(self):
        """Circle plus latitude/longitude ellipses. The wireframe is what makes
        it read as a BALL; without it the radial arrows are spokes on a wheel."""
        R = self.GS_RAD
        g = VGroup(Circle(radius=R).set_stroke(POLE, 3.0).set_fill(_lift(PLATE, 1.25), 0.55),
                   Ellipse(width=2 * R, height=2 * R * self.GS_SQUASH
                           ).set_stroke(POLE, 1.6, 0.5).set_fill(opacity=0))
        for k in (0.62, -0.62):
            w = 2 * R * np.sqrt(max(1 - k * k, 0.01))
            g.add(Ellipse(width=w, height=w * self.GS_SQUASH).set_fill(opacity=0)
                  .set_stroke(POLE, 1.2, 0.30).shift(UP * R * k))
        g.add(Ellipse(width=2 * R * self.GS_SQUASH, height=2 * R)
              .set_stroke(POLE, 1.2, 0.30).set_fill(opacity=0))
        return g

    def gauss_arrows(self, n=16, extra=0.62, skip=None):
        """EVERY ARROW THE SAME LENGTH. |E| = q/4*pi*eps0*r^2 depends only on r,
        so it is identical at every point of this sphere — and that constancy is
        exactly what lets E leave the integral later. Foreshortening them to fake
        depth draws a field stronger at the poles and teaches the opposite."""
        g = VGroup()
        R = self.GS_RAD
        for i in range(n):
            a = i * TAU / n
            if skip is not None and abs(((a - skip + PI) % TAU) - PI) < 12 * DEGREES:
                continue
            d = np.array([np.cos(a), np.sin(a), 0])
            ln = Line(d * R, d * (R + extra)).set_stroke(FIELD, 2.6, 1)
            ln.add_tip(tip_length=0.17, tip_width=0.15)
            g.add(ln)
        return g

    def gauss_patch(self, half=13 * DEGREES, depth=0.13):
        """dS, lying ON the surface: bounded by an arc of the sphere and a second
        just inside it, so it curves with the ball instead of being a flat tile."""
        R, phi = self.GS_RAD, self.GS_PHI
        outer = [np.array([np.cos(t), np.sin(t), 0]) * R
                 for t in np.linspace(phi - half, phi + half, 24)]
        inner = [np.array([np.cos(t), np.sin(t), 0]) * (R - depth)
                 for t in np.linspace(phi + half, phi - half, 24)]
        m = VMobject().set_points_as_corners(outer + inner + [outer[0]])
        return m.set_fill(ION_GOLD, 0.85).set_stroke(ION_GOLD, 2.2)

    def gauss_tiles(self, n=18, half=None, depth=0.13):
        """The whole surface cut into elements — what the closed integral MEANS.

        Parts 2 and 3 spend a minute each on "add up every dS over the sphere"
        with nothing on screen but algebra. One patch says what an element is;
        a ring of them says what summing them is, and keeps the equation tied to
        the picture it came from.
        """
        R = self.GS_RAD
        half = half if half is not None else (TAU / n) * 0.40
        g = VGroup()
        for i in range(n):
            phi = i * TAU / n
            outer = [np.array([np.cos(t), np.sin(t), 0]) * R
                     for t in np.linspace(phi - half, phi + half, 12)]
            inner = [np.array([np.cos(t), np.sin(t), 0]) * (R - depth)
                     for t in np.linspace(phi + half, phi - half, 12)]
            m = VMobject().set_points_as_corners(outer + inner + [outer[0]])
            # the one the derivation follows stays bright; the rest are the
            # "and all the others" that the integral sweeps up
            lit = abs(((phi - self.GS_PHI + PI) % TAU) - PI) < half
            m.set_fill(ION_GOLD, 0.85 if lit else 0.34)
            m.set_stroke(ION_GOLD, 2.0 if lit else 1.2, 1.0 if lit else 0.55)
            g.add(m)
        return g

    def beat_gauss(self, spec):
        R, phi = self.GS_RAD, self.GS_PHI
        d = np.array([np.cos(phi), np.sin(phi), 0])
        perp = np.array([-d[1], d[0], 0])
        want = lambda k: spec.get(k) is not None
        g, items = VGroup(), []

        g.add(self.gauss_ball())
        g.add(Dot(ORIGIN, radius=0.115, color="#FF8A6B"),
              Dot(ORIGIN, radius=0.155).set_fill("#FF8A6B", 0.25).set_stroke(width=0),
              MathTex("+q", color="#FF8A6B").scale(0.68).move_to(UP * 0.36 + LEFT * 0.30),
              MathTex("O", color=DIM).scale(0.55).move_to(DOWN * 0.34 + LEFT * 0.24))
        # the radius stops short of the surface when the patch is drawn there
        stop = R - (0.16 if (want("patch") or want("tile")) else 0.0)
        g.add(DashedLine(ORIGIN, d * stop, dash_length=0.09).set_stroke(DIM, 2.0),
              MathTex("r", color=DIM).scale(0.60).move_to(d * R * 0.50 + np.array([-0.28, -0.06, 0])))
        if want("patch") or want("tile"):
            # the element IS at P, so a separate dot sits under it: the name
            # moves inside the ball where the fill is dark and nothing else is
            g.add(MathTex("P", color=INK).scale(0.55).move_to(d * (R - 0.42) + perp * 0.26))
        else:
            g.add(Dot(d * R, radius=0.055, color=INK),
                  MathTex("P", color=INK).scale(0.55).move_to(d * R + perp * 0.30 + d * 0.16))

        def timed(mob, key):
            v = spec.get(key)
            g.add(mob)
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                items.append((int(v), mob))

        if want("arrows"):
            timed(self.gauss_arrows(skip=phi if want("vectors") else None), "arrows")
        if want("tile"):
            grp = VGroup(self.gauss_tiles())
            lab = Text("हर छोटा अवयव जोड़ना है", font=FONT_LABEL, font_size=21,
                       color=ION_GOLD)
            lab.move_to(np.array([0, -R - 0.62, 0]))
            grp.add(lab)
            timed(grp, "tile")
        if want("patch"):
            grp = VGroup(self.gauss_patch())
            if not want("vectors"):
                lab = Text("क्षेत्रफल अवयव  dS", font=FONT_LABEL, font_size=21, color=ION_GOLD)
                lab.move_to(d * (R + 1.02) + np.array([1.02, 0.30, 0]))
                grp.add(Line(lab.get_left() + LEFT * 0.06, d * (R - 0.06)
                             ).set_stroke(ION_GOLD, 1.6, 0.55), lab)
            timed(grp, "patch")
        if want("vectors"):
            L = 1.30
            n = Line(d * R + perp * 0.11, d * (R + L) + perp * 0.11)
            n.set_stroke(K_GREEN, 3.6, 1); n.add_tip(tip_length=0.22, tip_width=0.19)
            e = Line(d * R - perp * 0.11, d * (R + L) - perp * 0.11)
            e.set_stroke(FIELD, 3.6, 1); e.add_tip(tip_length=0.22, tip_width=0.19)
            out = perp if perp[0] >= 0 else -perp
            mid = d * (R + L * 0.62)
            v = VGroup(n, e,
                       MathTex(r"d\vec{S}", color=K_GREEN).scale(0.66
                           ).move_to(d * (R + L + 0.26) + perp * 0.30),
                       MathTex(r"\vec{E}", color=FIELD).scale(0.66
                           ).move_to(d * (R + L + 0.26) - perp * 0.34),
                       # the angle mark is a TIE ACROSS THE TWO SHAFTS, nothing
                       # more: a tie plus a leader reads as one stroke cutting
                       # through the very arrow being measured.
                       Line(mid + perp * 0.12, mid - perp * 0.12).set_stroke(ION_GOLD, 2.0, 0.9),
                       MathTex(r"\theta = 0^{\circ}", color=ION_GOLD).scale(0.58
                           ).move_to(mid + out * 0.62))
            timed(v, "vectors")
        # PULLED IN FROM THE MARGINS. The subject plates carry line art down
        # both edges (assets/backgrounds/*.png), so a figure fitted to the full
        # band width puts its outermost label on top of that art — the E label
        # landed squarely on the plate's own "s = ut + 1/2 at^2". The layout
        # guard cannot see this: it checks content against CONTENT, never
        # against the backdrop.
        self.place(g, pad=0.84)
        return g, items

    def beat_law(self, spec):
        """A law: the equation, the picture it describes, and what each symbol
        means — all on screen at once.

        Written because splitting them fails three ways. A formula beat followed
        by a list REPLACES the equation, so the student hears "phi E is the total
        flux" with no phi E in front of them. The list also spelled the symbols
        out in Devanagari ("फाई E", "एप्सिलॉन नॉट"), which is not what they have
        to recognise in the exam — the symbol is the thing being defined. And a
        statement about flux through a closed surface with no closed surface
        drawn is an assertion, not an explanation.
        """
        eq = MathTex(spec["tex"], color=INK).scale(float(spec.get("scale", 1.05)))

        fig = VGroup()
        if spec.get("figure") == "gauss":
            fig.add(self.gauss_ball(), self.gauss_arrows(n=12, extra=0.52),
                    Dot(ORIGIN, radius=0.115, color="#FF8A6B"),
                    Dot(ORIGIN, radius=0.155).set_fill("#FF8A6B", 0.25).set_stroke(width=0),
                    MathTex("+q", color="#FF8A6B").scale(0.62
                        ).move_to(UP * 0.36 + LEFT * 0.30))
            fig.scale(float(spec.get("figure_scale", 0.62)))

        rows, items = VGroup(), []
        # ONE SHARED SYMBOL COLUMN, aligned by POSITION and nothing else.
        # An invisible spacer mobject cannot be used here: the reveal plays
        # `set_opacity(1.0)` over the whole row, which turns a transparent
        # spacer into a solid grey box sitting behind the symbol. Every symbol
        # is placed by hand instead, so there is nothing that can be made
        # visible by accident.
        syms = [MathTex(r["sym"], color=GOLD).scale(0.72) for r in spec["rows"]]
        wide = max((m.width for m in syms), default=0.0)
        pairs = []
        for r, sym in zip(spec["rows"], syms):
            rest = VGroup(Text(":", font=FONT_LABEL, font_size=20, color=DIM),
                          Text(r["text"], font=FONT_LABEL, font_size=20, color=INK)
                          ).arrange(RIGHT, buff=0.16)
            row = VGroup(sym, rest)
            rows.add(row); pairs.append((sym, rest))
            if r.get("at") is not None:
                items.append((int(r["at"]), row))
        rows.arrange(DOWN, buff=0.26, aligned_edge=LEFT)
        left = rows.get_left()[0]
        for sym, rest in pairs:
            sym.move_to([left + wide / 2, sym.get_center()[1], 0])
            rest.move_to([left + wide + 0.18 + rest.width / 2,
                          rest.get_center()[1], 0])

        body = VGroup(fig, rows).arrange(RIGHT, buff=0.46) if len(fig) else rows
        whole = VGroup(eq, body).arrange(DOWN, buff=0.44)
        self.place(whole, pad=0.86)
        return whole, items

    def build_beat(self, spec):
        t = spec["type"]
        if t == "points":
            return self.beat_points(spec["items"], spec.get("title"),
                                    hi=spec.get("hi"))
        if t == "cube":
            return self.beat_cube(spec)
        if t == "formula":
            # `terms` is the symbol legend under the equation (memory:
            # formulas-carry-a-symbol-legend). It existed only in the COMPOSED
            # files, never in this source, so recomposing a project silently
            # dropped every legend it had — an equation a student is copying
            # with nothing saying what its symbols mean.
            grp = self.beat_formula(spec["tex"], spec.get("label"),
                                    terms=spec.get("terms"))
            if spec.get("eqno") is not None:
                # beside the LAST line of the block, which is the equation the
                # number refers to
                body = grp[-1] if len(grp) > 1 else grp
                grp.add(self.eq_number(spec["eqno"], body))
                self.place(grp)
            self._pending_asides = self._asides(spec, grp)
            return grp
        if t == "flow":
            return self.beat_flow(spec["items"])
        if t == "compare":
            return self.beat_compare(spec["left"], spec["right"])
        if t == "table":
            grp, rows = self.beat_table(spec["cols"], spec["rows"],
                                        size=spec.get("size", 26),
                                        col_tones=spec.get("col_tones"),
                                        font=spec.get("font"))
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
        if t == "orbitals":
            rl = self._rail(tuple(spec.get("rail", ())))
            rl.move_to([0, norm_point(0.5, CELL_TOP)[1], 0])
            def _set(txt, size, colour, bold=False):
                """`$...$` goes to LaTeX. Ion CHARGES must be set as maths: the
                Unicode superscripts put the sign visibly ABOVE the digit because
                U+207A and U+00B2 sit at different heights in Poppins and Khand,
                which the faculty flagged. Without this branch the beat printed
                the markup itself — the screen read `$[NiCl_4]^{2-}$`."""
                t = str(txt)
                if t.startswith("$") and t.endswith("$"):
                    m = MathTex(t[1:-1], color=colour)
                    ref = Text("H", font=FONT, font_size=size, weight=FONT_W)
                    m.scale(ref.height / max(MathTex("H").height, 1e-6))
                    if bold:
                        m.set_stroke(colour, width=1.4, opacity=1.0, background=True)
                    return m
                return Text(t, font=(FONT if bold else FONT_UI), font_size=size,
                            color=colour, weight=(FONT_W if bold else NORMAL))

            head = VGroup(_set(spec["ion"], 36, INK, bold=True))
            if spec.get("cfg"):
                head.add(Text("·", font=FONT_UI, font_size=22, color="#38507A"))
                for piece in spec["cfg"] if isinstance(spec["cfg"], list) else [spec["cfg"]]:
                    head.add(_set(piece, 21, DIM))
            head.arrange(RIGHT, buff=0.22)

            # PIECES THAT ARRIVE ON THEIR OWN CAPTION are laid out with the rest
            # so they hold their place, then LIFTED OUT of the returned group —
            # exactly as scan_figure does with its labels. Leaving them in and
            # zeroing their opacity does not work: the beat is revealed with
            # FadeIn, and FadeIn restores a mobject to ITS OWN current opacity,
            # so anything pre-zeroed stays invisible for the whole beat.
            self._labels = []
            pending = []
            def timed(mob, at):
                if at is not None:
                    pending.append((int(at), mob))
                return mob

            stack, boxes = [], []
            rev = spec.get("reveal", {})
            for i, r in enumerate(spec["rows"]):
                if i and r.get("cap"):
                    stack.append(timed(Text(r["cap"], font=FONT, font_size=21,
                                            color=REASON, weight=FONT_W), r.get("cap_at")))
                g1, b1 = self._orow(r["d"], -1.95, "3d", tuple(r.get("ring_d", ())))
                g2, b2 = self._orow(r["s"], 0.35, "4s", tuple(r.get("ring_s", ())))
                g3, b3 = self._orow(r["p"], 1.05, "4p", tuple(r.get("ring_p", ())))
                boxes.append((b1, b2, b3))
                stack.append(timed(VGroup(g1, g2, g3), r.get("at")))
            orb = VGroup(*stack).arrange(DOWN, buff=0.26)

            bi = int(spec.get("brace_row", len(spec["rows"]) - 1))
            b1, b2, b3 = boxes[bi]
            keep = tuple(spec["rows"][bi].get("ring_d", ()))
            span = VGroup(*([VGroup(*[b1[j] for j in keep])] if keep else []), b2, b3)
            br = Brace(span, DOWN, buff=0.09).set_color(ANSWER)
            hy = MathTex(spec["hyb"], color=ANSWER).scale(0.80)
            line = VGroup(hy)
            if spec.get("extra"):
                line = VGroup(hy, Text("—", font=FONT_UI, font_size=22, color="#38507A"),
                              Text(spec["extra"], font=FONT, font_size=24,
                                   color=ANSWER, weight=FONT_W)).arrange(RIGHT, buff=0.20)
            line.next_to(br, DOWN, buff=0.06)
            hyb_grp = timed(VGroup(br, line), rev.get("hyb"))
            # the brace is positioned against the REAL box coordinates, so it
            # must not be re-arranged afterwards — grouping it with the rows
            # means arrange() moves the pair as one and it stays attached.
            orb_full = VGroup(orb, hyb_grp)

            # A FORMULA INSIDE A HINDI SENTENCE IS TWO MOBJECTS, NOT ONE STRING.
            # preflight refuses maths mixed with Devanagari in a single label —
            # LaTeX cannot set Devanagari — so `Cl⁻ दुर्बल` had to be authored as
            # Unicode, and U+207B puts the minus ABOVE the letter instead of level
            # with it, which is the exact fault the faculty flagged. Authoring it
            # as ["$Cl^-$", "दुर्बल, युग्मन नहीं"] lays the maths and the words
            # side by side, each set by the renderer that can do it properly.
            _r = spec["reason"]
            rsn = VGroup(*[_set(x, 26, REASON, bold=True)
                           for x in (_r if isinstance(_r, list) else [_r])]
                         ).arrange(RIGHT, buff=0.14)
            unp = Text(spec.get("unpaired", ""), font=FONT_UI, font_size=17, color=DIM)
            txt = VGroup(rsn, unp).arrange(DOWN, buff=0.16)
            geo = VGroup(self._shape(spec.get("geometry", "tetra")).scale(0.72),
                         Text(spec["gname"], font=FONT, font_size=27, color=ANSWER, weight=FONT_W)
                         ).arrange(DOWN, buff=0.12)
            timed(txt, rev.get("reason")); timed(geo, rev.get("geometry"))
            foot = VGroup(txt, geo).arrange(RIGHT, buff=0.60)

            body = VGroup(head, orb_full, foot).arrange(DOWN, buff=0.34)
            top = rl.get_bottom()[1] - 0.28
            bot = norm_point(0.5, CELL_FLOOR)[1]
            # Grow as well as shrink. Capping at 1.0 left the diagram sitting in
            # the top half of a band it was free to fill — on a phone that is the
            # difference between an orbital box you can read and one you cannot.
            k = min((top - bot) / body.height, (config.frame_width * 0.98) / body.width)
            body.scale(k).move_to([0, top - body.height/2, 0])
            for at, mob in pending:
                for parent in body.submobjects:
                    if mob in parent.submobjects:
                        parent.remove(mob)
                        break
                else:
                    body.remove(mob)
                self._labels.append((at, mob))
            return VGroup(rl, body)
        if t == "cell":
            rig, G = self.cell_rig()
            c, bw, bh = self.stage_box()
            # A CONSTRUCTED CELL IS TALLER THAN IT IS WIDE — wire above, beakers
            # below — so the 388px stage band scales it to about a third and the
            # labels with it. This question is a सचित्र one: the apparatus IS the
            # answer, so when the beat sends the presenter away it takes the
            # frame instead of being capped at band height. tools/
            # presenter_windows.py turns the same `presenter: hidden` into the
            # compositor's fade, so the two agree.
            top = norm_point(0.5, CELL_TOP)[1]
            bot = (-config.frame_height / 2 + 0.45
                   if spec.get("presenter") == "hidden"
                   else norm_point(0.5, CELL_FLOOR)[1])
            c = np.array([0.0, (top + bot) / 2, 0.0])
            bh = top - bot
            # The badge rows hang BELOW the rig's own bounding box, so fitting
            # the rig alone pushed them off the bottom edge. Reserve their band
            # in the fit and the rig rides correspondingly higher — which also
            # fills the empty top the old centring left.
            f = float(spec.get("fill", 0.94))
            pad = 1.55 if any(l.get("part", "").endswith("2")
                              for l in spec.get("labels", [])) else 0.85
            k = min(bw * f / rig.width, bh * f / (rig.height + pad))
            pre = rig.get_center()
            rig.scale(k)
            target = c + UP * (pad * k) / 2.0
            rig.move_to(target)

            def P(x, y):
                return target + k * (np.array([x, y, 0.0]) - pre)

            self._cell = dict(G=G, P=P, k=k)
            # LABELS: each near its own part, joined by a leader, and revealed on
            # the caption that names it — same contract as a scan_figure.
            anchors = {
                "zn_rod": ((-2.18, 0.62), (G["znx"] - 0.10, 0.30)),
                "cu_rod": ((2.18, 0.62), (G["cux"] + 0.10, 0.30)),
                "bridge": ((0.0, G["br_top"] + 0.86), (0.0, G["br_top"] + G["br_x"] - 0.06)),
                "anode": ((G["lbx"], G["bk_y"] - 0.52), (G["lbx"], G["bk_y"] - 0.10)),
                "cathode": ((G["rbx"], G["bk_y"] - 0.52), (G["rbx"], G["bk_y"] - 0.10)),
                "anode2": ((G["lbx"], G["bk_y"] - 1.06), None),
                "cathode2": ((G["rbx"], G["bk_y"] - 1.06), None),
                "zn_sol": ((G["lbx"] + 0.02, G["liq"] - 0.92), None),
                "cu_sol": ((G["rbx"] - 0.02, G["liq"] - 0.92), None)}
            self._labels = []
            for sl in spec.get("labels", []):
                at_, to = anchors[sl["part"]]
                txt, face = sl["text"], sl.get("plate")
                if txt.startswith("$") and txt.endswith("$"):
                    body = MathTex(txt[1:-1], color=INK).scale(0.55 * k)
                else:
                    body = Text(txt, font=FONT, font_size=max(14, int(24 * k)),
                                color=GOLD if sl.get("hi") else INK,
                                weight=BOLD if (sl.get("hi") or face) else NORMAL)
                    if face:
                        box = RoundedRectangle(width=body.width + 0.26 * k,
                                               height=body.height + 0.20 * k,
                                               corner_radius=0.08 * k)
                        box.set_fill(face, 1).set_stroke(width=0).move_to(body.get_center())
                        body = VGroup(box, body)
                body.move_to(P(*at_))
                lab = body
                if to is not None:
                    tgt = P(*to)
                    d = tgt - body.get_center()
                    edge = body.get_boundary_point(d / (np.linalg.norm(d) or 1.0))
                    lab = VGroup(body, Line(edge, tgt, stroke_width=1.8,
                                            color=INK).set_opacity(0.75))
                # NEVER clamp a cell label. clamp_to_band() drags a mobject into
                # STAGE_TOP..STAGE_BOT, and a cell computes its OWN box — taller,
                # because it suppresses the caption above and only has to clear
                # the shrunk presenter below. Clamping flattened all seven labels
                # into one strip on top of each other, twice: once when the box
                # was the full frame, and again the moment the `presenter` key
                # that guarded it was removed. The cell keeps its own labels
                # inside its own box by construction.
                self._labels.append((int(sl["at"]), lab))
            self._flows = [(int(f["at"]), f["kind"]) for f in spec.get("flows", [])]
            return rig
        if t == "law":
            grp, timed = self.beat_law(spec)
            if timed:
                self._pending_reveal = timed
                for _, m in timed:
                    m.set_opacity(0.0)
            return grp
        if t == "gauss":
            grp, timed = self.beat_gauss(spec)
            if timed:
                self._pending_reveal = timed
                for _, m in timed:
                    m.set_opacity(0.0)
            return grp
        if t in ("magnet", "poles", "axis", "domains", "photos", "gradient"):
            grp, items = {"magnet": self.beat_magnet, "poles": self.beat_poles,
                          "axis": self.beat_axis, "domains": self.beat_domains,
                          "photos": self.beat_photos,
                          "gradient": self.beat_gradient}[t](spec)
            w0 = grp.width
            self.place(grp)
            k = (grp.width / w0) if w0 else 1.0
            for it in items:
                tr = getattr(it, "travel", None)
                if tr is not None:
                    it.travel = (tr[0], tr[1] * k)
            # Rows arrive on the caption that names them, exactly like a
            # progressive list: the one being spoken is bright, the ones already
            # covered stay on screen at 0.55 so the student keeps the map.
            reveal = spec.get("reveal_at") or [r.get("at") for r in
                                               spec.get("rows", spec.get("readings", []))]
            reveal = [a for a in reveal if a is not None]
            if len(reveal) == len(items):
                if isinstance(grp, VGroup):
                    self._pending_reveal = list(zip((int(a) for a in reveal),
                                                    items))
                    for it in items:
                        it.set_opacity(0.0)
                else:
                    # A PHOTO ROW IS A Group HOLDING AN ImageMobject, and
                    # ImageMobject has no fill_opacity — the opacity reveal
                    # every other beat uses raises AttributeError on it. So the
                    # rows after the first are lifted out of the group and faded
                    # in on their own caption, the way a diagram's labels
                    # arrive. The first row stays IN, because a beat that
                    # returns an empty group fades in a mobject with no points
                    # and warns on every frame of the render.
                    self._labels = [(int(a), it) for a, it
                                    in zip(reveal[1:], items[1:])]
                    for it in items[1:]:
                        grp.remove(it)
            return grp
        if t == "clear":
            # "No graphic" is a valid director decision, and until now there was
            # no way to SAY it once a beat was up: the stage only ever changed
            # from one graphic to another, so the last one sat there to the end
            # of the part. A clear beat empties the stage, which also brings the
            # captions back — see the caption rule in construct().
            return VGroup()
        if t == "image":
            return self.beat_image(ROOT / spec["src"], spec.get("caption"))
        if t == "graph":
            return self.graph(spec.get("kind", "zero_order"))
        if t in ("figure", "scan_figure"):
            fig = self.figure(spec["name"], draw=spec.get("draw", "scan"),
                              hide=spec.get("hide"),
                              width=float(spec.get("width", 0.88)))
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
                elif spec.get("draw") == "image":
                    # CENTRE IT ANYWAY. The fit only ever GROWS a figure, so a
                    # beat that deliberately asks for a SMALL one — an image
                    # narrowed to leave both margins free for label columns —
                    # never reached move_to and sat wherever ImageMobject put
                    # it, which is the origin. The band is not centred on the
                    # origin (it is the upper region, above the presenter), so
                    # the picture hung 0.29 units below the floor and the layout
                    # guard reported sixty frames out of band.
                    fig.move_to(c)
            # Same contract as `apparatus`: built now, revealed one label per
            # caption that names a part.
            self._labels = []
            # The figure and its labels are ONE diagram: विलयन and जल sit inside
            # the vessel's own bands, exactly as the book prints them, so every
            # label reads as a 100% overlap unless they share a layout group.
            tag = id(fig)
            mark_group(fig, tag)
            # TWO MARGIN COLUMNS, NOT FIFTEEN POINTS ON THE PICTURE.
            # Placing each label at its own anchor is what a textbook does when
            # it has room; this figure does not have room. Fifteen names on a
            # drawing this size piled up on the left — एम्पुला over इस्थमस over
            # अंडवाहिनी, and एंडोमेट्रियम straight through मायोमेट्रियम — because
            # the parts themselves are clustered, so their labels are too, and
            # nudging them apart one at a time just moved the collision.
            #
            # A column cannot collide BY CONSTRUCTION: each side gets a stack of
            # evenly spaced slots running the full height of the stage, which is
            # roughly twice the figure's own height, and the leader line carries
            # the name back to the part. That is also how the book prints it.
            col_specs = [l for l in spec.get("labels", []) if l.get("col")]
            if col_specs:
                c0, bw, bh = self.stage_box()
                # Pixels at the 1080-wide portrait plate, expressed in scene
                # units. The first draft of this block leaned on a per-pixel
                # helper that exists in no source file — it survived only in the
                # composed scene I had hand-patched, and vanished the moment
                # that scene was regenerated. NameError at render time, which is
                # exactly the trap this template is meant to close.
                _px = _fw() / 1080.0
                # The margin is what is left either side of the picture. Labels
                # are scaled to FIT it rather than set at a fixed size: the long
                # ones (एंडोमेट्रियम, इन्फन्डीबुलम) decide the size, and letting
                # them overrun is what pushed अंडाशय off the frame edge.
                margin = max((bw - fig.width) / 2.0 - 10 * _px, 120 * _px)
                sides = {}
                for l in col_specs:
                    sides.setdefault(l["col"], []).append(l)
                for side, items in sides.items():
                    items.sort(key=lambda l: l.get("slot", 0))
                    n = len(items)
                    # Slots span the stage, not the figure, so a name whose part
                    # sits in the crowded middle can still be written level with
                    # clear space above or below it.
                    top, bot = c0[1] + bh / 2 - 30 * _px, c0[1] - bh / 2 + 30 * _px
                    for i, l in enumerate(items):
                        y = top if n == 1 else top - (top - bot) * i / (n - 1)
                        t = Text(str(l["text"]), font=FONT, font_size=40,
                                 color=INK, weight=FONT_W)
                        t.scale(float(l.get("rel", 0.055)) * fig.height
                                / Text("क", font=FONT, font_size=40,
                                       weight=FONT_W).height)
                        if t.width > margin:
                            t.scale(margin / t.width)
                        if side == "l":
                            t.move_to([c0[0] - bw / 2, y, 0], aligned_edge=LEFT)
                        else:
                            t.move_to([c0[0] + bw / 2, y, 0], aligned_edge=RIGHT)
                        lab = t
                        anchors = getattr(fig, "anchors", None)
                        part = l.get("part")
                        if anchors and part in (anchors or {}):
                            tgt = anchors[part].get_center()
                            # The leader leaves the label on the side FACING the
                            # figure and turns once, so it reads as a pointer
                            # rather than a line drawn across the drawing.
                            start = (t.get_right() + RIGHT * 6 * _px) if side == "l" \
                                else (t.get_left() + LEFT * 6 * _px)
                            elbow = np.array([start[0] + (18 * _px if side == "l"
                                                          else -18 * _px),
                                              tgt[1], 0])
                            arm = VMobject().set_points_as_corners(
                                [start, elbow, tgt])
                            arm.set_stroke(INK, 2.2)
                            dot = Dot(tgt, radius=5 * _px, color=INK)
                            lab = VGroup(arm, dot, t)
                        mark_group(lab, tag)
                        self._labels.append((int(l["at"]), lab))
            for spec_l in [l for l in spec.get("labels", []) if not l.get("col")]:
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
        self._pending_morphs = []
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
                               sheet=ROOT / "assets" / "design" / "question_sheet.png",
                               marks=META.get("marks"))
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
                self._flows = []
                self.clear_stage()          # the card goes here, and every beat
                                            # replaces the one before it
                self.stage_mobs = []
            if i in beats:
                # CAPTIONS ONLY WHEN THE STAGE IS EMPTY. A caption is a subtitle
                # of the presenter, and it earns its place while there is nothing
                # else to read — but once a diagram, table or equation is up,
                # THAT is what the student should be reading, and a running
                # subtitle over it is just a second thing competing for the same
                # attention. So the caption stops when a beat takes the stage and
                # returns when the stage is cleared. Losing it also gives the
                # band back its top: stage_box() stops subtracting the caption,
                # so the figure below is drawn larger.
                if getattr(self, "caption_mob", None) is not None:
                    self.remove(self.caption_mob)
                    self.caption_mob = None
                spec = beats[i]
                if spec.get("reveal") == "progressive" and spec["type"] == "points":
                    rows, bodies = self.reveal_points(spec)
                    self.stage_mobs.append(rows)
                    self.add(rows)
                    self._pending_reveal = list(zip(spec.get("reveal_at", []), bodies))
                    self._pending_steps = []
                    self._pending_morphs = []
                elif spec["type"] == "clear":
                    # The stage was emptied above and stays empty. Nothing is
                    # appended to stage_mobs, which is what lets the captions
                    # start running again — an empty VGroup appended here would
                    # read as "a graphic is up" and keep them suppressed.
                    self._pending_reveal = []
                    self._pending_steps = []
                    self._pending_morphs = []
                    self._labels = []
                elif spec["type"] == "video":
                    # The stage was cleared above and stays cleared: a Veo clip
                    # covers these frames at composite time. There is nothing to
                    # build, nothing to fade in, and nothing for the layout
                    # guard to audit — an empty VGroup through FadeIn animates a
                    # mobject with no points and warns on every render.
                    #
                    # BUT THE STAGE IS NOT FREE, AND `stage_mobs` IS WHAT SAYS SO.
                    # Left empty it reads as "nothing is up" and the captions
                    # resume underneath. That is how CHE-C1-SA-02 rendered four
                    # lines of subtitle running from row 173 to row 659 — three
                    # of them inside the 300..908 panel band the raisin clip was
                    # about to be laid into, which would have buried them. A clip
                    # IS a graphic; it just arrives one stage later, so the
                    # caption goes off exactly as it does for a diagram.
                    #
                    # The marker is NOT added to the scene, so _stage_mobjects()
                    # (which reads self.mobjects) and clear_stage() never see it
                    # — no empty-mobject FadeIn, nothing for the audit to flag.
                    self.stage_mobs.append(VGroup())
                    self._pending_reveal = []
                    self._pending_steps = []
                    self._pending_morphs = []
                    self._labels = []
                elif spec["type"] in ("table", "chain") and spec.get("reveal_at"):
                    mob = self.build_beat(spec)
                    self.stage_mobs.append(mob)
                    self.add(mob)
                    self._pending_steps = []
                    self._pending_morphs = []
                    self.audit_layout(spec.get("type", ""))
                elif spec["type"] == "formula" and spec.get("build") == "morph":
                    # ONE EQUATION REWRITTEN, not a stack. See
                    # build_formula_morph: the stages share a centre and the
                    # reveal loop transforms one into the next.
                    self._pending_reveal = []
                    self._labels = []
                    rows, steps = self.build_formula_morph(spec)
                    self.stage_mobs.append(rows)
                    self.add(rows)
                    self._pending_steps = []
                    self._pending_morphs = []
                    self._pending_morphs = list(zip(spec.get("reveal_at", []),
                                                    steps[:-1], steps[1:]))
                    self._focus_box = None
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
                        #
                        # BUT WRITE IS VECTOR-ONLY. A `draw: "image"` figure is
                        # an ImageMobject riding in a Group, and Manim raises
                        # "Write only works for vectorized Mobjects" on it — the
                        # whole render dies at the figure beat. A bitmap cannot
                        # be drawn stroke by stroke, so it fades instead.
                        if all(isinstance(m, VMobject)
                               for m in built.family_members_with_points()):
                            self.play(Write(built, lag_ratio=0.02), run_time=1.8)
                        else:
                            self.play(FadeIn(built), run_time=0.8)
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
                    if getattr(body, "arrow_first", False) and len(body.submobjects) == 2:
                        # THE CONNECTOR LEADS ITS BOX. Arriving together, the
                        # arrow reads as decoration; arriving a beat earlier it
                        # reads as "and therefore", which is the whole point of
                        # drawing a chain rather than a list.
                        arr, box = body.submobjects
                        self.play(arr.animate.set_opacity(1.0), run_time=0.16)
                        self.play(box.animate.set_opacity(1.0), run_time=0.24)
                    elif getattr(body, "travel", None) is not None:
                        # THE BODY MOVES. Its label and its motion are one event:
                        # "प्रबल आकर्षित" and being yanked onto the pole are the
                        # same fact, and splitting them makes the caption look
                        # like a claim about a picture that is not doing it.
                        mob, dx = body.travel
                        self.play(body.animate.set_opacity(1.0),
                                  mob.animate.shift(RIGHT * dx),
                                  run_time=0.65)
                    else:
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
            for at, frm, to in list(getattr(self, "_pending_morphs", [])):
                if at == i:
                    # TransformMatchingTex moves the parts that BOTH stages
                    # share and rewrites the rest, which is exactly the claim
                    # being made: this symbol became that one.
                    to.set_opacity(1.0)
                    self.play(TransformMatchingTex(frm, to), run_time=0.85)
                    if frm in self.mobjects:
                        self.remove(frm)
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
                    # NOT clamped. A focus box means "this line" — moving it to
                    # satisfy a band breaks the only thing it says. The line it
                    # surrounds was already placed inside the band, so its
                    # rectangle is too.
                    box = SurroundingRectangle(eq, color=GOLD, buff=0.16)
                    box.set_stroke(width=3)
                    old = getattr(self, "_focus_box", None)
                    if old is not None:
                        self.remove(old)
                    self._focus_box = box
                    self.stage_mobs.append(box)
                    self.play(Create(box), run_time=0.30)
            for at, kind in list(getattr(self, "_flows", [])):
                if at == i:
                    self.stage_mobs.append(self.start_flow(kind))
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
            if i >= card_until and not self.stage_mobs:
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
