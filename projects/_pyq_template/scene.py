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

from src.manim_helpers import (ThemedScene, fit_caption, norm_point,
                               register_fonts, wrap_measured)

INK, DIM, GOLD = "#FFFFFF", "#B9C6DC", "#FFC15C"
GREEN, VIOLET, CYAN = "#7CE0B0", "#C792EA", "#5BC8F9"

FONT, FONT_W = "Khand", "BOLD"
CAPTION_SIZE, CAPTION_W, CAPTION_TOP = 62, 0.90, 0.090
STAGE_TOP, STAGE_BOT, STAGE_W = 0.290, 0.600, 0.86
CAPTION_GAP = 0.30

PROJECT = _os.getenv("PYQ_PROJECT", "che-c2-la-05")
PART = int(_os.getenv("PYQ_PART", "1"))
ROOT = _Path(ASSET_ROOT) / "projects" / PROJECT

LINES = json.loads((ROOT / f"lines_part{PART}.json").read_text(encoding="utf-8"))
BEATS = json.loads((ROOT / f"beats_part{PART}.json").read_text(encoding="utf-8"))
META = json.loads((ROOT / "meta.json").read_text(encoding="utf-8"))
CLIP_END = float(META["clip_end"][str(PART)])

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

    def place(self, mob, y=0.5, pad=0.94):
        c, w, h = self.stage_box()
        s = min((w * pad) / mob.width if mob.width > w * pad else 1.0,
                (h * pad) / mob.height if mob.height > h * pad else 1.0)
        if s < 1.0:
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
            body = VGroup(ax, line, half, drop, tag)
            xl.next_to(ax, DOWN, buff=0.20)
            yl.next_to(ax, LEFT, buff=0.20)
            body = VGroup(body, xl, yl)
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

    def build_beat(self, spec):
        t = spec["type"]
        if t == "points":
            return self.beat_points(spec["items"], spec.get("title"),
                                    hi=spec.get("hi"))
        if t == "formula":
            return self.beat_formula(spec["tex"], spec.get("label"))
        if t == "flow":
            return self.beat_flow(spec["items"])
        if t == "compare":
            return self.beat_compare(spec["left"], spec["right"])
        if t == "image":
            return self.beat_image(ROOT / spec["src"], spec.get("caption"))
        if t == "graph":
            return self.graph(spec.get("kind", "zero_order"))
        if t == "apparatus":
            return self.apparatus(spec["kind"])
        raise ValueError(f"unknown beat type: {t}")

    def construct(self):
        # ThemedScene.setup() already registered fonts and painted the theme;
        # calling a setup_theme() of our own would be a second background.
        register_fonts()
        self.caption_mob = None
        self._wcache = {}
        self.stage_mobs = []

        # cue 0 is always the question card; the sheet carries the question
        card_at = float(LINES[0]["start"])
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
        card_until = int(_cl[str(PART)] if isinstance(_cl, dict) else _cl)
        for i, line in enumerate(LINES):
            self.at(max(0.0, float(line["start"]) - 0.35))
            if i == card_until or i in beats:
                self.clear_stage()          # the card goes here, and every beat
                                            # replaces the one before it
                self.stage_mobs = []
            if i in beats:
                built = self.build_beat(beats[i])
                self.stage_mobs.append(built)
                self.play(FadeIn(built, shift=UP * 0.12), run_time=0.35)
                self.audit_layout(f"beat@{i}")
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
