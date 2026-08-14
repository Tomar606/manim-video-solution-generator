"""फैराडे के विद्युत्-अपघटन के नियम — CHE-C2-LA-01, two parts.

Timed against the real HeyGen clips. `timing_part1.json` / `timing_part2.json`
hold one cue per spoken line, anchored to word-level transcript timings, so each
caption is up exactly while it is spoken and each render ends with its audio.

Carries the same guarantees as the corrosion scene:
  · `place()` fits every block inside the stage band, so nothing can cross into
    the caption above or the presenter below
  · `cue()` clears the stage by default — opt out with keep=True for a block
    that is meant to persist, so an overlap can never happen by omission
  · captions are one fixed size and wrap rather than shrink

Accuracy, from accuracy_brief.md: in electrolysis the CATHODE is the negative
terminal (the most-reversed detail), current inside the liquid is carried by
ions and never by electrons, the second law needs the cells in SERIES, and Z
(electrochemical equivalent) is never drawn in E's colour.
"""
from manim import *  # noqa: F403
import json
import os as _os
from pathlib import Path as _Path

import numpy as np

from src.manim_helpers import ThemedScene, norm_point, register_fonts

INK    = "#FFFFFF"
DIM    = "#B9C6DC"
CU     = "#E08A4A"
ZN     = "#9FB4C7"
POS    = "#FF7B6B"
NEG    = "#5BC8F9"
LIQ    = "#2E6FA8"
GOLD   = "#FFC15C"
Z_COL  = "#7CE0B0"
E_COL  = "#C792EA"

FONT, FONT_W = "Khand", "BOLD"
CAPTION_SIZE, CAPTION_W, CAPTION_TOP = 36, 0.88, 0.105
STAGE_TOP, STAGE_BOT, STAGE_W = 0.225, 0.545, 0.84
CAPTION_GAP = 0.28          # clear space under the caption, scene units

PART = int(_os.getenv("FARADAY_PART", "1"))
TIMING = json.loads((_Path(ASSET_ROOT) /
    f"projects/faraday-electrolysis/timing_part{PART}.json").read_text(encoding="utf-8"))
CLIP_END = {1: 91.05, 2: 107.67}[PART]
# The caption track. One LINE per entry, on its own absolute timeline —
# deliberately NOT tied to the animation cues.
#
# The captions are built from the clip's own transcript, not from the script:
# the shoot took some lines from the master script, some from an earlier draft,
# and paraphrased others, so no script matches the recording. The transcript is
# the only source that does, and it carries word-level timings with it.
LINES = json.loads((_Path(ASSET_ROOT) /
    f"projects/faraday-electrolysis/lines_part{PART}.json").read_text(encoding="utf-8"))

# Generated illustrations. Used where a drawn diagram genuinely fails to teach:
# the series apparatus rendered as vectors was two empty rectangles joined by a
# bar, with the electrolytes, the electrode metals and the single shared circuit
# — the whole point of "same current through both" — all invisible.
#
# The image carries NO text. Generated lettering is unreliable, and unreliable
# lettering on an exam diagram is worse than none; every label below is drawn in
# Manim, where it is correct by construction.
IMAGES = {
    "series_cells": "projects/faraday-electrolysis/images/series_cells_4ae74384589f0415.png",
}

HILITE = {
    "विद्युत्-रासायनिक तुल्यांक": Z_COL, "रासायनिक तुल्यांक": E_COL,
    "प्रथम नियम": Z_COL, "पहला नियम": Z_COL, "दूसरा नियम": E_COL,
    "दूसरे नियम": E_COL, "पहले नियम": Z_COL,
    "समानुपाती": GOLD, "समान": GOLD, "मुक्त": CU,
}


class _Stop(Exception):
    pass


def _y(t):
    return norm_point(0.5, STAGE_TOP + t * (STAGE_BOT - STAGE_TOP))[1]


class _Base(ThemedScene):
    CAPTION_MODE = "narration"

    def hindi(self, text, size=CAPTION_SIZE, color=INK, weight=FONT_W):
        return Text(text, font=FONT, font_size=size, color=color, weight=weight)

    def _hl(self, line):
        out = {}
        for w in sorted(HILITE, key=len, reverse=True):
            if w in line and not any(w in k for k in out):
                out[w] = HILITE[w]
        return out

    def _w(self, word, size):
        """Rendered width of one word, cached — wrapping measures, not counts."""
        k = (word, size)
        if k not in self._wcache:
            self._wcache[k] = Text(word, font=FONT, font_size=size,
                                   weight=FONT_W).width
        return self._wcache[k]

    def caption(self, text, size=CAPTION_SIZE):
        # Wrap on MEASURED width, not character count. A character count
        # assumes every glyph is equally wide, which Devanagari conjuncts are
        # not, so long captions ran to the frame edge with no margin at all.
        # The old code then forced everything back to two lines by splitting
        # the word list in half, which made the overflow worse rather than
        # better. A caption that needs a third line now takes one.
        limit = config.frame_width * CAPTION_W
        space = self._w(" ", size)
        lines, cur, cw = [], "", 0.0
        for word in text.split():
            ww = self._w(word, size)
            trial = cw + (space + ww if cur else ww)
            if cur and trial > limit:
                lines.append(cur); cur, cw = word, ww
            else:
                cur, cw = (f"{cur} {word}".strip()), trial
        if cur:
            lines.append(cur)
        g = VGroup(*[Text(l, font=FONT, font_size=size, color=INK,
                          weight=FONT_W, t2c=self._hl(l)) for l in lines])
        g.arrange(DOWN, buff=0.16)          # never scaled: fixed type size
        # Top 10% stays empty; anchor by top edge so a taller caption grows
        # downward into the gap rather than bleeding off the frame.
        g.move_to(norm_point(0.5, CAPTION_TOP))
        g.shift(DOWN * g.height / 2)
        return g

    # --- layout guard ---------------------------------------------------- #
    def stage_box(self):
        """The band animations may occupy — never overlapping the caption.

        The top is not a constant. A three-line caption reaches lower than a
        one-line caption, and a fixed STAGE_TOP let the two collide; the stage
        now starts below whatever the current caption actually occupies.
        """
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

    # --- timing ---------------------------------------------------------- #
    def cue(self, i, caption=True, keep=False):
        if i >= len(TIMING):
            raise _Stop
        c = TIMING[i]
        if not keep:
            self.clear_stage()
        # A cue asking for no caption owns the screen — the question card is
        # the visual, and a caption over it is clutter. The track is decoupled
        # from the cues now, so silence it explicitly until this cue ends
        # rather than relying on the caption=False flag alone.
        if not caption:
            nxt = TIMING[i + 1]["start"] if i + 1 < len(TIMING) else CLIP_END
            self._pending = [l for l in self._pending if l["start"] >= nxt]
        self.at(c["start"] - 0.30)
        self._i = i

    def _line(self, text):
        """Swap in one caption line. Uses Scene.play directly — self.play is
        overridden to flush due lines first, and that would recurse."""
        new = self.caption(text)
        if self.caption_mob is None:
            super().play(FadeIn(new, shift=DOWN * 0.10), run_time=0.22)
        else:
            old = self.caption_mob
            super().play(FadeOut(old, shift=UP * 0.10),
                         FadeIn(new, shift=DOWN * 0.10), run_time=0.22)
            self.remove(old)
        self.caption_mob = new

    def _due(self, upto=None):
        """Show every caption line whose moment has arrived.

        Driven by the clock, not by the cue, so a long animation cannot hold a
        stale caption on screen while the avatar has moved on.
        """
        limit = self.time if upto is None else upto
        while self._pending and self._pending[0]["start"] <= limit + 1e-3:
            nxt = self._pending.pop(0)
            gap = nxt["start"] - self.time
            if gap > 0.02:
                self.wait(gap)
            self._line(nxt["text"])

    def play(self, *args, **kwargs):
        # An animation must not swallow a line that falls due while it runs.
        self._due()
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

    # --- pieces ---------------------------------------------------------- #
    def cell(self, scale=1.0, battery=True):
        """One vessel, two electrodes, ONE dc source. Anode +, cathode −."""
        w, h = 4.4 * scale, 2.8 * scale
        beaker = VGroup(Line([-w/2, h/2, 0], [-w/2, -h/2, 0]),
                        Line([-w/2, -h/2, 0], [w/2, -h/2, 0]),
                        Line([w/2, -h/2, 0], [w/2, h/2, 0])).set_stroke(DIM, 5)
        liquid = Rectangle(width=w - 0.12, height=h - 0.55, fill_color=LIQ,
                           fill_opacity=0.40, stroke_width=0).move_to([0, -0.26*scale, 0])
        an = Rectangle(width=0.28*scale, height=2.05*scale, fill_color=ZN,
                       fill_opacity=1, stroke_width=0).move_to([-1.2*scale, -0.1*scale, 0])
        ca = an.copy().move_to([1.2*scale, -0.1*scale, 0])
        g = VGroup(beaker, liquid, an, ca)
        if battery:
            wy = h/2 + 0.95*scale
            wire = VMobject().set_points_as_corners(
                [an.get_top(), [an.get_x(), wy, 0], [ca.get_x(), wy, 0], ca.get_top()]
            ).set_stroke(DIM, 4)
            bat = VGroup(Line([-0.15, wy-0.32, 0], [-0.15, wy+0.32, 0]).set_stroke(POS, 7),
                         Line([0.15, wy-0.17, 0], [0.15, wy+0.17, 0]).set_stroke(NEG, 7))
            g.add(wire, bat)
        g.an, g.ca, g.liquid = an, ca, liquid
        return g

    def electrode_labels(self, c):
        return VGroup(
            self.hindi("ऐनोड (+)", size=25, color=POS).next_to(c.an, DOWN, buff=0.24),
            self.hindi("कैथोड (−)", size=25, color=NEG).next_to(c.ca, DOWN, buff=0.24))

    def eq(self, *tex, scale=1.6):
        m = MathTex(*tex).scale(scale)
        m.set_color(INK)
        return m


class FaradayPart1(_Base):
    def construct(self):
        register_fonts()
        self.caption_mob = None
        self._wcache = {}
        self._pending = list(LINES)
        try:
            self._build()
        except _Stop:
            pass

    def _build(self):
        # ---- cue 0: question card, no caption --------------------------- #
        self.cue(0, caption=False)
        qb = VGroup(*[self.hindi(l, size=40) for l in
                      ["फैराडे के विद्युत्-अपघटन के", "नियम लिखिए।"]]
                    ).arrange(DOWN, buff=0.28, aligned_edge=LEFT)
        marks = VGroup(self.hindi("अंक", size=25, color=DIM),
                       self.hindi("4", size=46, color=GOLD)).arrange(DOWN, buff=0.12)
        years = VGroup(self.hindi("वर्ष", size=25, color=DIM),
                       self.hindi("2023, 25", size=44, color=GOLD)).arrange(DOWN, buff=0.12)
        meta = VGroup(marks, years).arrange(RIGHT, buff=1.0, aligned_edge=UP)
        rule = Line(LEFT, RIGHT).set_stroke(GOLD, 4).set_width(meta.width * 1.05)
        card = VGroup(qb, rule, meta).arrange(DOWN, buff=0.60)
        qb.align_to(card, LEFT); rule.align_to(card, RIGHT); meta.align_to(card, RIGHT)
        self.place(card, y=0.44)
        self.play(LaggedStart(*[FadeIn(l, shift=RIGHT*0.25) for l in qb],
                              lag_ratio=0.22), run_time=1.3)
        self.play(GrowFromEdge(rule, RIGHT), run_time=0.4)
        self.play(FadeIn(meta, shift=UP*0.15), run_time=0.7)
        self.hold()

        self.cue(1); self.hold()

        # ---- cue 2-3: the cell, ions, deposit --------------------------- #
        self.cue(2)
        c = self.place(self.cell(0.95), y=0.42)
        lab = self.electrode_labels(c)
        self.play(Create(c[0]), FadeIn(c.liquid), run_time=0.7)
        self.play(FadeIn(c[2]), FadeIn(c[3]), Create(c[4]), FadeIn(c[5]), run_time=0.8)
        self.play(FadeIn(lab, shift=UP*0.1), run_time=0.5)
        self.hold()

        self.cue(3, keep=True)      # the cell stays; ions move through it
        rng = np.random.default_rng(7)
        cat = VGroup(*[Dot(point=[rng.uniform(-0.6, 0.4),
                                  c.liquid.get_y() + rng.uniform(-0.6, 0.6), 0],
                           radius=0.075, color=CU) for _ in range(7)])
        ani = VGroup(*[Dot(point=[rng.uniform(-0.4, 0.6),
                                  c.liquid.get_y() + rng.uniform(-0.6, 0.6), 0],
                           radius=0.062, color=NEG) for _ in range(7)])
        self.play(FadeIn(cat), FadeIn(ani), run_time=0.5)
        self.play(*[d.animate.move_to([c.ca.get_x()-0.26, d.get_y(), 0]) for d in cat],
                  *[d.animate.move_to([c.an.get_x()+0.26, d.get_y(), 0]) for d in ani],
                  run_time=1.6)
        dep = Rectangle(width=0.30, height=2.05*0.95, fill_color=CU,
                        fill_opacity=1, stroke_width=0)
        dep.next_to(c.ca, LEFT, buff=0.0).align_to(c.ca, UP)
        self.play(FadeIn(dep), run_time=0.5)
        self.hold()

        # ---- cue 4-10: the derivation, one line replacing the last ------ #
        self.cue(4)
        e = self.eq(r"W \propto Q")
        self.place(e, y=0.45)
        self.play(Write(e), run_time=0.7)
        self.hold()

        self.cue(5, keep=True)
        legend = VGroup(self.hindi("W = मुक्त पदार्थ की मात्रा", size=27, color=CU),
                        self.hindi("Q = प्रवाहित विद्युत् की मात्रा", size=27, color=NEG)
                        ).arrange(DOWN, buff=0.22)
        legend.next_to(e, DOWN, buff=0.65)
        self.play(FadeIn(legend, shift=UP*0.12), run_time=0.6)
        self.hold()

        self.cue(6)
        e2 = self.place(self.eq(r"Q = i \times t"), y=0.45)
        self.play(Write(e2), run_time=0.7)
        self.hold()

        self.cue(7, keep=True)
        leg2 = VGroup(self.hindi("i = विद्युत् धारा", size=27, color=NEG),
                      self.hindi("t = समय", size=27, color=DIM)
                      ).arrange(DOWN, buff=0.22).next_to(e2, DOWN, buff=0.65)
        self.play(FadeIn(leg2, shift=UP*0.12), run_time=0.6)
        self.hold()

        self.cue(8)
        e3 = self.place(self.eq(r"W \propto i \times t"), y=0.45)
        self.play(Write(e3), run_time=0.7)
        self.hold()

        self.cue(9)
        e4 = MathTex("W", "=", "Z", "i", "t").scale(1.8)
        e4.set_color(INK); e4[2].set_color(Z_COL)
        self.place(e4, y=0.42)
        self.play(Write(e4), run_time=0.8)
        box = SurroundingRectangle(e4, color=GOLD, buff=0.24, corner_radius=0.12)
        self.play(Create(box), run_time=0.5)
        self.hold()

        self.cue(10, keep=True)
        zl = self.hindi("Z = विद्युत्-रासायनिक तुल्यांक", size=28, color=Z_COL)
        zl.next_to(box, DOWN, buff=0.60)
        self.play(FadeIn(zl, shift=UP*0.12), run_time=0.6)
        self.hold()

        # ---- cue 11-13: recap, then the handoff ------------------------- #
        self.cue(11)
        recap = VGroup(self.hindi("पहला नियम", size=34, color=Z_COL),
                       MathTex("W", "=", "Z", "i", "t").scale(1.5).set_color(INK)
                       ).arrange(DOWN, buff=0.40)
        recap[1][2].set_color(Z_COL)
        self.place(recap, y=0.42)
        self.play(FadeIn(recap, shift=UP*0.15), run_time=0.7)
        self.hold()

        self.cue(12, keep=True)
        more = VGroup(self.hindi("ज्यादा विद्युत्", size=30, color=NEG),
                      MathTex(r"\Longrightarrow", color=GOLD).scale(1.2),
                      self.hindi("ज्यादा पदार्थ", size=30, color=CU)
                      ).arrange(RIGHT, buff=0.35)
        more.next_to(recap, DOWN, buff=0.62)
        self.play(FadeIn(more, shift=UP*0.12), run_time=0.6)
        self.hold()

        self.cue(13)
        nxt = VGroup(self.hindi("अगला पार्ट", size=30, color=DIM),
                     self.hindi("दूसरा नियम", size=46, color=E_COL)
                     ).arrange(DOWN, buff=0.26)
        self.place(nxt, y=0.44)
        self.play(FadeIn(nxt, scale=1.06), run_time=0.7)
        self.hold()


class FaradayPart2(_Base):
    def construct(self):
        register_fonts()
        self.caption_mob = None
        self._wcache = {}
        self._pending = list(LINES)
        try:
            self._build()
        except _Stop:
            pass

    def _build(self):
        # ---- cue 0: the bridge, showing part 1's result ----------------- #
        self.cue(0)
        b = VGroup(self.hindi("पार्ट एक", size=28, color=DIM),
                   MathTex("W", "=", "Z", "i", "t").scale(1.4).set_color(INK)
                   ).arrange(DOWN, buff=0.32)
        b[1][2].set_color(Z_COL)
        self.place(b, y=0.42)
        self.play(FadeIn(b, shift=UP*0.12), run_time=0.7)
        self.hold()

        # ---- cue 1-2: two cells IN SERIES ------------------------------- #
        # An image, not drawn shapes. See IMAGES above for why. ImageMobject is
        # a Mobject and not a VMobject, so this is a Group and never a VGroup.
        self.cue(1)
        rig = ImageMobject(str(_Path(ASSET_ROOT) / IMAGES["series_cells"]))
        rig.height = 4.5
        e1 = MathTex(r"CuSO_4").scale(0.75).set_color(CU)
        e2 = MathTex(r"AgNO_3").scale(0.75).set_color(ZN)
        e1.next_to(rig, DOWN, buff=0.10).shift(LEFT * rig.width * 0.24)
        e2.next_to(rig, DOWN, buff=0.10).shift(RIGHT * rig.width * 0.24)
        ser = self.hindi("श्रेणीक्रम — दोनों में समान विद्युत्", size=26, color=GOLD)
        grp = Group(rig, e1, e2)
        ser.next_to(grp, DOWN, buff=0.26)
        grp.add(ser)
        self.place(grp, y=0.42)
        self.play(FadeIn(rig, scale=1.03), run_time=0.9)
        self.play(FadeIn(e1, shift=UP*0.10), FadeIn(e2, shift=UP*0.10), run_time=0.5)
        self.play(FadeIn(ser, shift=UP*0.10), run_time=0.5)
        self.hold()

        self.cue(2, keep=True)
        self.hold()

        # ---- cue 3-5: the second law ------------------------------------ #
        self.cue(3)
        e5 = MathTex("W", r"\propto", "E").scale(1.8)
        e5.set_color(INK); e5[2].set_color(E_COL)
        self.place(e5, y=0.40)
        self.play(Write(e5), run_time=0.7)
        el = self.hindi("E = रासायनिक तुल्यांक", size=28, color=E_COL)
        el.next_to(e5, DOWN, buff=0.60)
        self.play(FadeIn(el, shift=UP*0.12), run_time=0.5)
        self.hold()

        self.cue(4)
        pairs = VGroup(MathTex(r"W_1 \propto E_1").scale(1.35).set_color(INK),
                       MathTex(r"W_2 \propto E_2").scale(1.35).set_color(INK)
                       ).arrange(DOWN, buff=0.36)
        self.place(pairs, y=0.42)
        self.play(LaggedStart(*[Write(m) for m in pairs], lag_ratio=0.35), run_time=1.1)
        self.hold()

        self.cue(5)
        e6 = MathTex(r"\frac{W_1}{W_2}", "=", r"\frac{E_1}{E_2}").scale(1.9)
        e6.set_color(INK); e6[2].set_color(E_COL)
        self.place(e6, y=0.42)
        self.play(Write(e6), run_time=0.9)
        box2 = SurroundingRectangle(e6, color=GOLD, buff=0.26, corner_radius=0.12)
        self.play(Create(box2), run_time=0.5)
        self.hold()

        # ---- cue 6-8: both laws together -------------------------------- #
        self.cue(6)
        law1 = VGroup(self.hindi("पहला नियम", size=30, color=Z_COL),
                      MathTex("W", "=", "Z", "i", "t").scale(1.25).set_color(INK)
                      ).arrange(DOWN, buff=0.26)
        law1[1][2].set_color(Z_COL)
        law2 = VGroup(self.hindi("दूसरा नियम", size=30, color=E_COL),
                      MathTex(r"\frac{W_1}{W_2} = \frac{E_1}{E_2}").scale(1.25).set_color(INK)
                      ).arrange(DOWN, buff=0.26)
        both = VGroup(law1, law2).arrange(DOWN, buff=0.75)
        self.place(both, y=0.44)
        self.play(FadeIn(law1, shift=UP*0.14), run_time=0.7)
        self.hold()

        self.cue(7, keep=True)
        n1 = self.hindi("विद्युत् बदली → पदार्थ बदला", size=26, color=Z_COL)
        n1.next_to(law1, RIGHT, buff=0.5) if False else n1.next_to(both, DOWN, buff=0.45)
        self.play(FadeIn(n1, shift=UP*0.1), run_time=0.5)
        self.hold()

        self.cue(8, keep=True)
        self.play(FadeOut(n1), run_time=0.25)
        self.play(FadeIn(law2, shift=UP*0.14), run_time=0.7)
        n2 = self.hindi("विद्युत् समान → तुल्यांक तय करेगा", size=26, color=E_COL)
        n2.next_to(both, DOWN, buff=0.45)
        self.play(FadeIn(n2, shift=UP*0.1), run_time=0.5)
        self.hold()

        # ---- cue 9-11: recap and sign-off ------------------------------- #
        self.cue(9)
        keys = VGroup(
            VGroup(self.hindi("पहला", size=27, color=Z_COL),
                   MathTex("W = Z i t").scale(1.0).set_color(INK)).arrange(RIGHT, buff=0.4),
            VGroup(self.hindi("दूसरा", size=27, color=E_COL),
                   MathTex(r"W_1/W_2 = E_1/E_2").scale(1.0).set_color(INK)).arrange(RIGHT, buff=0.4),
        ).arrange(DOWN, buff=0.42)
        self.place(keys, y=0.42)
        self.play(LaggedStart(*[FadeIn(k, shift=UP*0.12) for k in keys],
                              lag_ratio=0.3), run_time=1.0)
        self.hold()

        self.cue(10); self.hold()

        self.cue(11)
        end = VGroup(self.hindi("अरिविहान", size=56, color=GOLD),
                     self.hindi("उन्नति बैच", size=34, color=INK)
                     ).arrange(DOWN, buff=0.28)
        self.place(end, y=0.44)
        self.play(FadeIn(end, scale=1.06), run_time=0.7)
        self.hold()
