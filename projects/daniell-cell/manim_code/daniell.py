"""विद्युत्-रासायनिक सेल एवं डेनियल सेल — CHE-C2-LA-04, two parts.

Timed against the real HeyGen clips: `lines_part{N}.json` is the caption track,
built from the clip's own transcript (see tools/README.md — no script matches a
recording), and `timing_part{N}.json` is the animation cue list.

ACCURACY — the trap in this chapter
-----------------------------------
In the Daniell cell the ANODE IS NEGATIVE and the cathode positive. That is the
OPPOSITE of the electrolytic cell in projects/faraday-electrolysis, which sits in
the same chapter and is the most-reversed detail in the whole topic:

    galvanic (Daniell)   anode −, cathode +   reaction drives the current
    electrolytic         anode +, cathode −   current drives the reaction

Both remain true of oxidation and reduction: oxidation at the anode, reduction
at the cathode, in both cells. Only the SIGN flips. Do not "fix" one to match
the other.

Everything else that must not drift:
  · electrons travel through the WIRE, Zn -> Cu; they never cross the solution
  · charge inside the cell is carried by IONS through the salt bridge
  · Zn dissolves (rod thins), Cu deposits (rod thickens)
  · cell notation runs anode -> cathode, left to right:
        Zn(s) | ZnSO₄(aq) | CuSO₄(aq) | Cu(s)

WHY THIS IS DRAWN AND NOT A GENERATED IMAGE
-------------------------------------------
The Faraday series apparatus is an image because it is a static object whose
look carries the meaning. Here the meaning is MOTION — electrons leaving zinc,
crossing the wire, and being taken up by copper ions. A still cannot show that,
and every part is labelled and signed, so it has to be exact.

Layout guarantees, same as the other two scenes:
  · `place()` fits every block inside the stage band
  · `cue()` clears the stage by default; opt out with keep=True
  · captions are one line at a time on their own clock, and expire at their end
"""
from manim import *  # noqa: F403
import json
import os as _os
from pathlib import Path as _Path

import numpy as np

from src.manim_helpers import (ThemedScene, along, fit_caption, mark_group,
                               norm_point, register_fonts, wrap_measured)

INK   = "#FFFFFF"
DIM   = "#B9C6DC"
CU    = "#E08A4A"          # copper
ZN    = "#D6E2EE"          # zinc — light, so it reads against its solution
LIQ_CU = "#2E6FA8"         # copper sulphate — blue
LIQ_ZN = "#2A4059"         # zinc sulphate — colourless in life, drawn dark
                           # so the pale zinc electrode stays legible on it
POS   = "#FF7B6B"
NEG   = "#5BC8F9"
GOLD  = "#FFC15C"
GREEN = "#7CE0B0"
VIO   = "#C792EA"

FONT, FONT_W = "Khand", "BOLD"
CAPTION_SIZE, CAPTION_W, CAPTION_TOP = 36, 0.90, 0.105
STAGE_TOP, STAGE_BOT, STAGE_W = 0.225, 0.545, 0.84
CAPTION_GAP = 0.28

PART = int(_os.getenv("DANIELL_PART", "1"))
TIMING = json.loads((_Path(ASSET_ROOT) /
    f"projects/daniell-cell/timing_part{PART}.json").read_text(encoding="utf-8"))
LINES = json.loads((_Path(ASSET_ROOT) /
    f"projects/daniell-cell/lines_part{PART}.json").read_text(encoding="utf-8"))
CLIP_END = {1: 113.51, 2: 108.09}[PART]

HILITE = {
    "विद्युत्-रासायनिक सेल": GOLD, "डेनियल सेल": GOLD,
    "ऑक्सीकरण": GREEN, "अपचयन": VIO, "ऐनोड": GREEN, "कैथोड": VIO,
    "इलेक्ट्रॉन": NEG, "लवण सेतु": GOLD, "ऋण ध्रुव": GREEN, "धन ध्रुव": VIO,
}


class _Stop(Exception):
    pass


class _Base(ThemedScene):
    CAPTION_MODE = "narration"
    # The shared layout guard reports content that overlaps other content or
    # leaves the stage band. See src/manim_helpers.audit_layout.
    STAGE_BAND = (STAGE_TOP, STAGE_BOT)

    # ---- text ---------------------------------------------------------- #
    def hindi(self, text, size=CAPTION_SIZE, color=INK, weight=FONT_W):
        return Text(text, font=FONT, font_size=size, color=color, weight=weight)

    def _hl(self, line):
        """Words to colour, extended to whole words.

        Colouring a bare key splits the string wherever it matches, and a split
        inside a Devanagari cluster orphans the combining mark — "इलेक्ट्रॉन"
        matching inside "इलेक्ट्रॉनों" left the "ों" on its own and it rendered
        as a dotted circle. Matching the key but colouring the full word keeps
        every cluster intact.
        """
        out = {}
        for w in sorted(HILITE, key=len, reverse=True):
            if w not in line or any(w in k for k in out):
                continue
            colour = HILITE[w]
            for token in line.split():
                if w in token:
                    whole = token.strip(",।?!—:;")
                    if whole and not any(whole in k for k in out):
                        out[whole] = colour
        return out

    def _measure(self, line, size):
        """Mobject for a whole candidate LINE, cached.

        Whole LINE, not word: a space has no ink, so Manim measures it as
        0.0000 wide. Summing word widths therefore treats spaces as free, every
        line takes one word too many, and the caption reaches the frame edge.
        """
        # Lazily created: not every scene in this file has a construct() that
        # sets it up, and a caption must never depend on one having run.
        cache = self.__dict__.setdefault("_wcache", {})
        k = (line, size)
        if k not in cache:
            cache[k] = Text(line, font=FONT, font_size=size, weight=FONT_W)
        return cache[k]

    def caption(self, text, size=CAPTION_SIZE):
        """Wrapped on the measured width of each LINE. Devanagari conjuncts are
        not equal width so a character count overflows; summing word widths
        overflows too, because a space has no ink and Manim measures it as
        0.0000 wide. Either way the caption reaches the frame edge."""
        limit = config.frame_width * CAPTION_W
        lines = wrap_measured(text, limit, lambda l: self._measure(l, size))
        g = VGroup(*[Text(l, font=FONT, font_size=size, color=INK,
                          weight=FONT_W, t2c=self._hl(l)) for l in lines])
        g.arrange(DOWN, buff=0.16)
        fit_caption(g, limit)
        g.move_to(norm_point(0.5, CAPTION_TOP))
        g.shift(DOWN * g.height / 2)      # top-anchored: keeps the top 10% clear
        return g

    # ---- layout guard --------------------------------------------------- #
    def stage_box(self):
        top, bot = norm_point(0.5, STAGE_TOP)[1], norm_point(0.5, STAGE_BOT)[1]
        if self.caption_mob is not None:
            top = min(top, self.caption_mob.get_bottom()[1] - CAPTION_GAP)
        return np.array([0., (top + bot) / 2, 0.]), config.frame_width * STAGE_W, top - bot

    def place(self, mob, y=0.5, pad=0.94):
        c, w, h = self.stage_box()
        s = min((w * pad) / mob.width if mob.width > w * pad else 1.0,
                (h * pad) / mob.height if mob.height > h * pad else 1.0)
        if s < 1.0:
            mob.scale(s)
        top, bot = c[1] + h / 2, c[1] - h / 2
        cy = top - (top - bot) * y
        mob.move_to([0, max(bot + mob.height / 2, min(top - mob.height / 2, cy)), 0])
        return mob

    def rows(self, *mobs, buff=0.40, y=0.5):
        return self.place(VGroup(*mobs).arrange(DOWN, buff=buff), y=y)

    # ---- timing --------------------------------------------------------- #
    def cue(self, i, caption=True, keep=False):
        if i >= len(TIMING):
            raise _Stop
        c = TIMING[i]
        if not keep:
            self.clear_stage()
        # A cue that wants no caption owns the screen — the question card is the
        # visual, and a caption over it is clutter.
        if not caption:
            nxt = TIMING[i + 1]["start"] if i + 1 < len(TIMING) else CLIP_END
            self._pending = [l for l in self._pending if l["start"] >= nxt]
        self.at(c["start"] - 0.30)
        self._i = i

    def _line(self, text):
        """Uses Scene.play directly — self.play flushes due lines and would recurse."""
        new = self.caption(text)
        if self.caption_mob is None:
            super().play(FadeIn(new, shift=DOWN * 0.10), run_time=0.22)
        else:
            old = self.caption_mob
            super().play(FadeOut(old, shift=UP * 0.10),
                         FadeIn(new, shift=DOWN * 0.10), run_time=0.22)
            self.remove(old)
        self.caption_mob = new

    def _clear_caption(self):
        if self.caption_mob is None:
            return
        old = self.caption_mob
        self.caption_mob = None
        super().play(FadeOut(old, shift=UP * 0.08), run_time=0.20)
        self.remove(old)

    def _expire(self, upto):
        """Take a caption down when its sentence is over, so it does not hang
        through the pause before the next one."""
        end = self._cap_end
        if self.caption_mob is None or end is None or upto < end:
            return
        nxt = self._pending[0]["start"] if self._pending else None
        if nxt is None or nxt - end > 0.45:
            gap = end - self.time
            if gap > 0.02:
                self.wait(gap)
            self._clear_caption()
            self._cap_end = None

    def _due(self, upto=None):
        limit = self.time if upto is None else upto
        while True:
            self._expire(limit)
            if not (self._pending and self._pending[0]["start"] <= limit + 1e-3):
                break
            nxt = self._pending.pop(0)
            gap = nxt["start"] - self.time
            if gap > 0.02:
                self.wait(gap)
            self._line(nxt["text"])
            self._cap_end = nxt.get("end")

    def play(self, *args, **kwargs):
        self._due()               # an animation must not swallow a due line
        super().play(*args, **kwargs)

    def at(self, t):
        self._due(t)
        left = t - self.time
        if left > 0.02:
            self.wait(left)

    def hold(self):
        i = getattr(self, "_i", 0)
        self.at(TIMING[i + 1]["start"] - 0.30 if i + 1 < len(TIMING) else CLIP_END)

    def clear_stage(self, rt=0.35):
        keep = {self.caption_mob, self.background}
        if self.chroma_zone is not None:
            keep.add(self.chroma_zone)
        doomed = [m for m in self.mobjects if m not in keep]
        if doomed:
            self.play(*[FadeOut(m) for m in doomed], run_time=rt)

    def boot(self):
        register_fonts()
        self.caption_mob = None
        self._wcache = {}
        self._pending = list(LINES)
        self._cap_end = None

    # ---- the cell ------------------------------------------------------- #
    def half_cell(self, rod_col, liq_col, scale=1.0, rod_side=-1):
        """One beaker, its solution and its electrode.

        `rod_side` puts the electrode on the OUTER side of the beaker (-1 for
        the left half-cell, +1 for the right). The inner side is then free for
        the salt bridge to dip into — drawn down the middle, the bridge came
        straight through the electrode and its label.
        """
        w, h = 2.55 * scale, 2.15 * scale
        glass = VGroup(Line([-w/2, h/2, 0], [-w/2, -h/2, 0]),
                       Line([-w/2, -h/2, 0], [w/2, -h/2, 0]),
                       Line([w/2, -h/2, 0], [w/2, h/2, 0])).set_stroke(DIM, 4)
        liquid = Rectangle(width=w - 0.10, height=h - 0.62, fill_color=liq_col,
                           fill_opacity=0.55, stroke_width=0)
        liquid.move_to([0, -0.31 * scale, 0])
        rod = Rectangle(width=0.32 * scale, height=1.85 * scale, fill_color=rod_col,
                        fill_opacity=1, stroke_width=2, stroke_color=rod_col)
        rod.move_to([rod_side * 0.62 * scale, 0.16 * scale, 0])
        g = VGroup(glass, liquid, rod)
        g.rod, g.liquid, g.glass = rod, liquid, glass
        g.dip_x = -rod_side * 0.70 * scale        # where the bridge comes down
        return g

    def cell(self, scale=1.0):
        """The whole Daniell cell: two half-cells, salt bridge, external wire.

        Returns the group with the parts attached, so the caller can animate
        electrons along `.wire` and label `.zn` / `.cu` without re-deriving
        any geometry.
        """
        left = self.half_cell(ZN, LIQ_ZN, scale, rod_side=-1)
        right = self.half_cell(CU, LIQ_CU, scale, rod_side=+1)
        pair = VGroup(left, right).arrange(RIGHT, buff=1.30 * scale)

        # Salt bridge — an inverted U dipping into both solutions on their INNER
        # sides, below the wire and clear of both electrodes.
        ly = left.liquid.get_top()[1]
        blx = left.get_center()[0] + left.dip_x
        brx = right.get_center()[0] + right.dip_x
        btop = ly + 0.62 * scale
        bridge = VMobject().set_points_as_corners(
            [[blx, ly - 0.58 * scale, 0], [blx, btop, 0],
             [brx, btop, 0], [brx, ly - 0.58 * scale, 0]]
        ).set_stroke(GOLD, 9)

        # External wire — from rod top, up and across ABOVE the bridge, so the
        # two never cross. Electrons go here; ions go through the bridge.
        wy = max(left.rod.get_top()[1], btop) + 0.95 * scale
        lrx, rrx = left.rod.get_center()[0], right.rod.get_center()[0]
        wire = VMobject().set_points_as_corners(
            [left.rod.get_top(), [lrx, wy, 0], [rrx, wy, 0], right.rod.get_top()]
        ).set_stroke(DIM, 5)

        g = VGroup(pair, bridge, wire)
        g.left, g.right, g.bridge, g.wire = left, right, bridge, wire
        g.zn, g.cu = left.rod, right.rod
        # The cell is revealed piece by piece, so its parts enter the scene as
        # separate top-level mobjects. Tag them as one thing or the guard reads
        # a rod sitting inside its own beaker as an overlap.
        mark_group(g)
        # No stored point list. `place()` scales and moves this group, and a
        # remembered path does not follow — that is exactly how the electrons
        # ended up crossing the gap through the air instead of along the wire.
        # Take the path from `g.wire` at animation time, via along().
        return g

    def electrons(self, cell, n=5):
        """Dots that travel ALONG THE WIRE from zinc to copper.

        The path comes from `cell.wire` itself — the object on screen — so it
        stays correct however the cell has been scaled or moved. Rebuilding it
        from remembered coordinates is what sent the electrons straight across
        the gap between the beakers.

        Direction is not decorative: electrons leave the metal being oxidised.
        Zinc is the anode, so they run LEFT to RIGHT through the wire, and they
        never pass through the solution — that is what the salt bridge is for.
        """
        path = along(cell.wire)
        dots = VGroup(*[Dot(radius=0.075, color=NEG) for _ in range(n)])
        for k, d in enumerate(dots):
            d.move_to(path.point_from_proportion(k / max(n, 1) * 0.2))
        return dots, path


# =========================================================================== #
class DaniellPart1(_Base):
    def construct(self):
        self.boot()
        try:
            self._build()
        except _Stop:
            pass

    def _build(self):
        # ---- cue 0: question card, no caption --------------------------- #
        self.cue(0, caption=False)
        # The approved opening design, the same one the other PYQ scenes use —
        # geometry measured off the still in src/question_card.py, with the
        # question wrapped and shrunk to the paper's writable area so it cannot
        # leak off the page.
        self.question_card("विद्युत्-रासायनिक सेल एवं उसकी क्रियाविधि "
                           "डेनियल सेल का उदाहरण देकर समझाइए।",
                           "डेनियल सेल", "2018 और 2023")
        self.hold()

        # ---- cue 1: the question ---------------------------------------- #
        self.cue(1)
        q = self.hindi("विद्युत्-रासायनिक सेल", size=48, color=GOLD)
        qm = self.hindi("किसे कहते हैं?", size=38, color=INK)
        self.rows(q, qm, buff=0.34, y=0.45)
        self.play(FadeIn(q, shift=UP * 0.15), run_time=0.6)
        self.play(FadeIn(qm, shift=UP * 0.10), run_time=0.5)
        self.hold()

        # ---- cue 2: the definition -------------------------------------- #
        self.cue(2)
        d1 = self.hindi("रासायनिक अभिक्रिया से", size=34, color=INK)
        d2 = self.hindi("विद्युत् ऊर्जा प्राप्त होती है", size=34, color=GREEN)
        d3 = self.hindi("= विद्युत्-रासायनिक सेल", size=36, color=GOLD)
        box = VGroup(d1, d2, d3).arrange(DOWN, buff=0.30)
        self.place(box, y=0.45)
        for m in (d1, d2, d3):
            self.play(FadeIn(m, shift=UP * 0.12), run_time=0.55)
        self.hold()

        # ---- cue 3: the energy conversion ------------------------------- #
        self.cue(3)
        a = self.hindi("रासायनिक ऊर्जा", size=34, color=CU)
        arrow = Arrow(LEFT * 0.8, RIGHT * 0.8, buff=0, stroke_width=7,
                      color=GOLD, max_tip_length_to_length_ratio=0.28)
        b = self.hindi("विद्युत् ऊर्जा", size=34, color=NEG)
        conv = VGroup(a, arrow, b).arrange(RIGHT, buff=0.42)
        self.place(conv, y=0.45)
        self.play(FadeIn(a, shift=RIGHT * 0.15), run_time=0.5)
        self.play(GrowArrow(arrow), run_time=0.5)
        self.play(FadeIn(b, shift=RIGHT * 0.15), run_time=0.5)
        self.hold()

        # ---- cue 4: the other names ------------------------------------- #
        self.cue(4, keep=True)
        alt = VGroup(self.hindi("गैल्वेनिक सेल", size=32, color=GREEN),
                     self.hindi("वोल्टाइक सेल", size=32, color=VIO)
                     ).arrange(RIGHT, buff=0.85)
        alt.next_to(conv, DOWN, buff=0.55)
        self.play(FadeIn(alt, shift=UP * 0.12), run_time=0.6)
        self.hold()

        # ---- cue 5-8: build the cell, piece by piece -------------------- #
        # Assembled in the order the teacher describes it, so each new part
        # arrives on the sentence that introduces it.
        self.cue(5)
        cell = self.cell(0.92)
        self.place(cell, y=0.46)
        self.play(FadeIn(cell.left.glass), FadeIn(cell.right.glass), run_time=0.7)
        self.hold()

        self.cue(6, keep=True)
        # Labels go ABOVE the rods, shifted outward — never beside them.
        # `half_cell` puts each electrode INSIDE its beaker, so LEFT of the zinc
        # rod and RIGHT of the copper rod are both beaker wall: the labels sat on
        # the glass. Above the rod is clear of the rim (rod top 0.998, glass top
        # 0.989), and the outward shift keeps them off the wire's vertical leg,
        # which drops onto the rod's own x.
        zl = self.hindi("जिंक", size=26, color=ZN).next_to(
            cell.zn, UP, buff=0.16).shift(LEFT * 0.55)
        cl = self.hindi("कॉपर", size=26, color=CU).next_to(
            cell.cu, UP, buff=0.16).shift(RIGHT * 0.55)
        self.play(FadeIn(cell.zn, shift=DOWN * 0.15), FadeIn(cell.cu, shift=DOWN * 0.15),
                  run_time=0.7)
        self.play(FadeIn(zl), FadeIn(cl), run_time=0.5)
        self.hold()

        self.cue(7, keep=True)
        znso4 = MathTex(r"ZnSO_4").scale(0.62).set_color(ZN)
        cuso4 = MathTex(r"CuSO_4").scale(0.62).set_color(CU)
        znso4.next_to(cell.left, DOWN, buff=0.20)
        cuso4.next_to(cell.right, DOWN, buff=0.20)
        self.play(FadeIn(cell.left.liquid), FadeIn(cell.right.liquid), run_time=0.7)
        self.play(FadeIn(znso4, shift=UP * 0.1), FadeIn(cuso4, shift=UP * 0.1), run_time=0.5)
        self.hold()

        self.cue(8, keep=True)
        bl = self.hindi("लवण सेतु", size=25, color=GOLD)
        bl.next_to(cell.bridge, UP, buff=0.10)
        self.play(Create(cell.bridge), run_time=0.8)
        self.play(FadeIn(bl), run_time=0.4)
        self.play(Create(cell.wire), run_time=0.8)
        self.hold()

        # ---- cue 9-10: zinc gives up electrons -------------------------- #
        self.cue(9, keep=True)
        self.play(Indicate(cell.zn, color=GREEN, scale_factor=1.10), run_time=0.9)
        self.hold()

        self.cue(10)
        eq = MathTex(r"Zn \rightarrow Zn^{2+} + 2e^{-}").scale(1.05).set_color(INK)
        eq[0][:2].set_color(ZN)
        frame = SurroundingRectangle(eq, color=GREEN, buff=0.28, corner_radius=0.12)
        self.place(VGroup(eq, frame), y=0.42)
        self.play(Write(eq), run_time=0.9)
        self.play(Create(frame), run_time=0.5)
        self.hold()

        # ---- cue 11-12: oxidation, therefore anode ---------------------- #
        self.cue(11, keep=True)
        ox = self.hindi("इलेक्ट्रॉन छोड़े  =  ऑक्सीकरण", size=32, color=GREEN)
        ox.next_to(frame, DOWN, buff=0.42)
        self.play(FadeIn(ox, shift=UP * 0.12), run_time=0.6)
        self.hold()

        self.cue(12, keep=True)
        an = self.hindi("ऑक्सीकरण  =  ऐनोड", size=32, color=GREEN)
        an.next_to(ox, DOWN, buff=0.30)
        self.play(FadeIn(an, shift=UP * 0.12), run_time=0.6)
        self.hold()

        # ---- cue 13: electrons travel the wire, zinc -> copper ---------- #
        self.cue(13)
        cell2 = self.cell(0.92)
        self.place(cell2, y=0.46)
        z2 = self.hindi("ऐनोड", size=25, color=GREEN).next_to(cell2.zn, LEFT, buff=0.30)
        c2 = self.hindi("कॉपर", size=25, color=CU).next_to(cell2.cu, RIGHT, buff=0.30)
        self.play(FadeIn(cell2), FadeIn(z2), FadeIn(c2), run_time=0.8)
        dots, path = self.electrons(cell2, n=5)
        self.add(dots)
        eflow = self.hindi("इलेक्ट्रॉन", size=25, color=NEG)
        eflow.next_to(cell2.wire, UP, buff=0.14)
        self.play(FadeIn(eflow), run_time=0.4)
        # two passes so the direction registers
        for _ in range(2):
            self.play(*[MoveAlongPath(d, path) for d in dots],
                      run_time=1.8, rate_func=linear)
            for k, d in enumerate(dots):
                d.move_to(path.point_from_proportion(k / len(dots) * 0.2))
        self.hold()

        # ---- cue 14: handoff -------------------------------------------- #
        self.cue(14)
        nxt = VGroup(self.hindi("अगला पार्ट", size=30, color=DIM),
                     self.hindi("कॉपर पर क्या होता है?", size=42, color=VIO)
                     ).arrange(DOWN, buff=0.30)
        self.place(nxt, y=0.45)
        self.play(FadeIn(nxt, scale=1.05), run_time=0.8)
        self.hold()


# =========================================================================== #
class DaniellPart2(_Base):
    def construct(self):
        self.boot()
        try:
            self._build()
        except _Stop:
            pass

    def _build(self):
        # ---- cue 0-1: where part 1 left off ----------------------------- #
        self.cue(0)
        cell = self.cell(0.92)
        self.place(cell, y=0.46)
        # Labels go ABOVE the rods, shifted outward — never beside them.
        # `half_cell` puts each electrode INSIDE its beaker, so LEFT of the zinc
        # rod and RIGHT of the copper rod are both beaker wall: the labels sat on
        # the glass. Above the rod is clear of the rim (rod top 0.998, glass top
        # 0.989), and the outward shift keeps them off the wire's vertical leg,
        # which drops onto the rod's own x.
        zl = self.hindi("ऐनोड", size=25, color=GREEN).next_to(
            cell.zn, UP, buff=0.16).shift(LEFT * 0.55)
        cl = self.hindi("कॉपर", size=25, color=CU).next_to(
            cell.cu, UP, buff=0.16).shift(RIGHT * 0.55)
        self.play(FadeIn(cell), FadeIn(zl), FadeIn(cl), run_time=0.8)
        dots, path = self.electrons(cell, n=5)
        self.add(dots)
        self.play(*[MoveAlongPath(d, path) for d in dots], run_time=1.8, rate_func=linear)
        self.hold()

        self.cue(1, keep=True)
        ask = self.hindi("कॉपर पर क्या?", size=30, color=VIO)
        # below the BEAKER, not the rod: below the rod is the solution
        ask.next_to(cell.right, DOWN, buff=0.24)
        self.play(Indicate(cell.cu, color=CU, scale_factor=1.12), run_time=0.8)
        self.play(FadeIn(ask, shift=UP * 0.1), run_time=0.5)
        self.hold()

        # ---- cue 2: the cathode half-reaction --------------------------- #
        self.cue(2)
        eq = MathTex(r"Cu^{2+} + 2e^{-} \rightarrow Cu").scale(1.05).set_color(INK)
        eq[0][:3].set_color(CU)
        frame = SurroundingRectangle(eq, color=VIO, buff=0.28, corner_radius=0.12)
        self.place(VGroup(eq, frame), y=0.42)
        self.play(Write(eq), run_time=0.9)
        self.play(Create(frame), run_time=0.5)
        self.hold()

        # ---- cue 3-4: reduction, therefore cathode ---------------------- #
        self.cue(3, keep=True)
        red = self.hindi("इलेक्ट्रॉन ग्रहण  =  अपचयन", size=32, color=VIO)
        red.next_to(frame, DOWN, buff=0.42)
        self.play(FadeIn(red, shift=UP * 0.12), run_time=0.6)
        self.hold()

        self.cue(4, keep=True)
        cat = self.hindi("अपचयन  =  कैथोड", size=32, color=VIO)
        cat.next_to(red, DOWN, buff=0.30)
        self.play(FadeIn(cat, shift=UP * 0.12), run_time=0.6)
        self.hold()

        # ---- cue 5-6: the rule students reverse ------------------------- #
        self.cue(5)
        warn = self.hindi("यहाँ अक्सर गलती होती है", size=34, color=GOLD)
        self.place(warn, y=0.42)
        self.play(FadeIn(warn, scale=1.06), run_time=0.7)
        self.hold()

        self.cue(6)
        r1 = VGroup(self.hindi("ऑक्सीकरण", size=34, color=GREEN),
                    self.hindi("=", size=34, color=DIM),
                    self.hindi("ऐनोड", size=34, color=GREEN)).arrange(RIGHT, buff=0.32)
        r2 = VGroup(self.hindi("अपचयन", size=34, color=VIO),
                    self.hindi("=", size=34, color=DIM),
                    self.hindi("कैथोड", size=34, color=VIO)).arrange(RIGHT, buff=0.32)
        rule = VGroup(r1, r2).arrange(DOWN, buff=0.38)
        box = SurroundingRectangle(rule, color=GOLD, buff=0.34, corner_radius=0.14)
        self.place(VGroup(rule, box), y=0.44)
        self.play(FadeIn(r1, shift=RIGHT * 0.12), run_time=0.55)
        self.play(FadeIn(r2, shift=RIGHT * 0.12), run_time=0.55)
        self.play(Create(box), run_time=0.5)
        self.hold()

        # ---- cue 7-8: the whole cell, both signs ------------------------ #
        # The signs are the point of this beat: in a GALVANIC cell the anode is
        # NEGATIVE. See the accuracy note at the top of this file.
        self.cue(7)
        c2 = self.cell(0.92)
        self.place(c2, y=0.46)
        self.play(FadeIn(c2), run_time=0.7)
        dots2, path2 = self.electrons(c2, n=5)
        self.add(dots2)
        self.play(*[MoveAlongPath(d, path2) for d in dots2], run_time=1.8, rate_func=linear)
        self.hold()

        self.cue(8, keep=True)
        an = VGroup(self.hindi("ऐनोड", size=26, color=GREEN),
                    self.hindi("ऋण ध्रुव (−)", size=23, color=GREEN)
                    ).arrange(DOWN, buff=0.10).next_to(c2.left, DOWN, buff=0.22)
        ca = VGroup(self.hindi("कैथोड", size=26, color=VIO),
                    self.hindi("धन ध्रुव (+)", size=23, color=VIO)
                    ).arrange(DOWN, buff=0.10).next_to(c2.right, DOWN, buff=0.22)
        self.play(FadeIn(an, shift=UP * 0.1), run_time=0.5)
        self.play(FadeIn(ca, shift=UP * 0.1), run_time=0.5)
        self.hold()

        # ---- cue 9: the two halves add to the cell reaction ------------- #
        self.cue(9)
        h1 = MathTex(r"Zn \rightarrow Zn^{2+} + 2e^{-}").scale(0.78).set_color(GREEN)
        h2 = MathTex(r"Cu^{2+} + 2e^{-} \rightarrow Cu").scale(0.78).set_color(VIO)
        bar = Line(LEFT, RIGHT).set_stroke(DIM, 3)
        net = MathTex(r"Zn(s) + Cu^{2+}(aq) \rightarrow Zn^{2+}(aq) + Cu(s)"
                      ).scale(0.72).set_color(INK)
        stack = VGroup(h1, h2, bar, net).arrange(DOWN, buff=0.28)
        bar.set_width(max(h1.width, h2.width, net.width) * 1.04)
        self.place(stack, y=0.44)
        self.play(Write(h1), run_time=0.7)
        self.play(Write(h2), run_time=0.7)
        self.play(Create(bar), run_time=0.35)
        self.play(Write(net), run_time=0.9)
        self.hold()

        # ---- cue 10-11: how it is written in the exam ------------------- #
        self.cue(10)
        head = self.hindi("सेल का निरूपण", size=36, color=GOLD)
        self.place(head, y=0.42)
        self.play(FadeIn(head, shift=UP * 0.12), run_time=0.6)
        self.hold()

        self.cue(11)
        notation = MathTex(r"Zn(s)", r"\,|\,", r"ZnSO_4(aq)", r"\,\|\,",
                           r"CuSO_4(aq)", r"\,|\,", r"Cu(s)").scale(0.74)
        notation[0].set_color(ZN); notation[2].set_color(ZN)
        notation[4].set_color(CU); notation[6].set_color(CU)
        nb = SurroundingRectangle(notation, color=GOLD, buff=0.30, corner_radius=0.12)
        self.place(VGroup(notation, nb), y=0.42)
        self.play(LaggedStart(*[FadeIn(p, shift=RIGHT * 0.12) for p in notation],
                              lag_ratio=0.28), run_time=1.6)
        self.play(Create(nb), run_time=0.5)
        self.hold()

        # ---- cue 12: which end is which sign ---------------------------- #
        self.cue(12, keep=True)
        lft = self.hindi("ऐनोड — ऋण ध्रुव", size=27, color=GREEN)
        rgt = self.hindi("कैथोड — धन ध्रुव", size=27, color=VIO)
        signs = VGroup(lft, rgt).arrange(RIGHT, buff=0.80)
        signs.next_to(nb, DOWN, buff=0.40)
        self.play(FadeIn(lft, shift=UP * 0.1), FadeIn(rgt, shift=UP * 0.1), run_time=0.6)
        self.hold()

        # ---- cue 13: the order to memorise ------------------------------ #
        self.cue(13)
        order = VGroup(*[self.hindi(t, size=28, color=c) for t, c in
                         [("जिंक", ZN), ("जिंक सल्फेट", ZN),
                          ("कॉपर सल्फेट", CU), ("कॉपर", CU)]])
        arrows = VGroup()
        order.arrange(DOWN, buff=0.34)
        for a, b in zip(order[:-1], order[1:]):
            arrows.add(Arrow(a.get_bottom(), b.get_top(), buff=0.06,
                             stroke_width=4, color=DIM,
                             max_tip_length_to_length_ratio=0.35))
        chain = VGroup(order, arrows)
        self.place(chain, y=0.44)
        for i, m in enumerate(order):
            self.play(FadeIn(m, shift=UP * 0.10), run_time=0.4)
            if i < len(arrows):
                self.play(GrowArrow(arrows[i]), run_time=0.25)
        self.hold()

        # ---- cue 14: the answer card ------------------------------------ #
        self.cue(14)
        title = self.hindi("उत्तर — डेनियल सेल", size=34, color=GOLD)
        pts = VGroup(
            self.hindi("रासायनिक ऊर्जा → विद्युत् ऊर्जा", size=25, color=INK),
            self.hindi("ऐनोड (−): जिंक, ऑक्सीकरण", size=25, color=GREEN),
            self.hindi("कैथोड (+): कॉपर, अपचयन", size=25, color=VIO),
        ).arrange(DOWN, buff=0.22, aligned_edge=LEFT)
        neteq = MathTex(r"Zn(s) + Cu^{2+}(aq) \rightarrow Zn^{2+}(aq) + Cu(s)"
                        ).scale(0.55).set_color(INK)
        noteq = MathTex(r"Zn(s)\,|\,ZnSO_4(aq)\,\|\,CuSO_4(aq)\,|\,Cu(s)"
                        ).scale(0.55).set_color(GOLD)
        card = VGroup(title, pts, neteq, noteq).arrange(DOWN, buff=0.28)
        self.place(card, y=0.44)
        self.play(FadeIn(title, shift=UP * 0.12), run_time=0.5)
        for m in pts:
            self.play(FadeIn(m, shift=RIGHT * 0.12), run_time=0.35)
        self.play(Write(neteq), run_time=0.7)
        self.play(Write(noteq), run_time=0.7)
        self.hold()

        # ---- cue 15: screenshot + CTA ----------------------------------- #
        self.cue(15, keep=True)
        shot = self.hindi("स्क्रीनशॉट लेना मत भूलना", size=28, color=GOLD)
        shot.next_to(card, DOWN, buff=0.36)
        self.play(FadeIn(shot, scale=1.05), run_time=0.6)
        self.hold()
