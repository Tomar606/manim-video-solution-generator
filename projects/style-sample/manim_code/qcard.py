"""The opening question card, in the approved design.

Layout numbers live in src/question_card.py, measured off the reference still
and off the notepaper asset. The text fit is the part that matters for a batch:
it wraps on measured width, shrinks until it fits the writable area, and then
`fits()` asserts containment — so a long question cannot leak off the paper.
"""
from manim import *  # noqa: F403
import numpy as np

from src.manim_helpers import ThemedScene, norm_point, register_fonts
from src.question_card import (CREAM, GOLD, PAPER, PAPER_HILITE,
                               PAPER_INK, PAPER_TILT, PAPER_W, PAPER_Y,
                               Q_MARK_R, Q_MARK_Y, Q_WORD_SIZE, Q_WORD_Y,
                               RULE_W, RULE_Y, TEAL, TICK_PAD, YEARS_Y, fit_lines,
                               fits, writable_box)

FONT, FONT_W = "Khand", "BOLD"


class QuestionCard(ThemedScene):
    CAPTION_MODE = "narration"

    # A batch supplies these per video. Defaults are the approved reference.
    import os as _os
    QUESTION = _os.getenv("CARD_Q", "फैराडे के विद्युत्-अपघटन के नियम लिखिए।")
    HIGHLIGHT = _os.getenv("CARD_HL", "विद्युत्-अपघटन")
    YEARS = _os.getenv("CARD_YEARS", "2023-2025")

    def t(self, s, size, colour=CREAM, weight=FONT_W):
        return Text(s, font=FONT, font_size=size, color=colour, weight=weight)

    def _w(self, word, size):
        k = (word, size)
        if k not in self._cache:
            self._cache[k] = Text(word, font=FONT, font_size=size,
                                  weight=FONT_W).width
        return self._cache[k]

    def sparks(self, around, colour=GOLD, n=6, pad=0.42):
        """Gold ticks radiating OUTSIDE what they surround.

        Placed on the bounding box, pushed out by `pad`. Placed on an ellipse
        instead they landed on the glyphs — Devanagari is wider than it is tall,
        so the ellipse cut through the word.
        """
        g = VGroup()
        hw, hh = around.width / 2 + pad, around.height / 2 + pad * 0.55
        spots = [(-hw, hh * 0.55), (-hw * 0.96, -hh * 0.15), (-hw * 0.80, hh * 0.95),
                 (hw, hh * 0.55), (hw * 0.96, -hh * 0.15), (hw * 0.80, hh * 0.95)]
        for i, (x, y) in enumerate(spots[:n]):
            # Tapered, not a rectangle: thin at the inner end, thick at the
            # outer, the way a pen tick actually lands.
            L, w0, w1 = 0.24, 0.020, 0.062
            tick = Polygon([0, -w0, 0], [L, -w1, 0], [L, w1, 0], [0, w0, 0])
            tick.set_fill(colour, 1).set_stroke(width=0)
            out = -1 if x < 0 else 1
            tick.rotate(PI if out < 0 else 0)                 # point outward
            tick.rotate(out * (0.30 + 0.32 * (i % 3)))
            tick.move_to(around.get_center() + np.array([x, y, 0]))
            g.add(tick)
        return g

    def scribble(self, width, colour=CREAM, wobble=0.035, n=26):
        """A pen-drawn underline, not a ruled line.

        The reference stroke wanders and varies in weight; a straight Line reads
        as a UI divider on a page that is otherwise hand-made.
        """
        pts = []
        for i in range(n):
            u = i / (n - 1)
            x = (u - 0.5) * width
            y = (np.sin(u * 5.2) * 0.3 + np.sin(u * 11.0 + 1.1) * 0.18) * wobble
            y += (u - 0.5) ** 2 * -wobble * 1.4                # slight bow
            pts.append([x, y, 0])
        s = VMobject().set_points_smoothly([np.array(p) for p in pts])
        s.set_stroke(colour, 7, opacity=0.95)
        # a lighter second pass, offset, the way a pen doubles back
        s2 = s.copy().shift(DOWN * wobble * 0.9 + RIGHT * width * 0.012)
        s2.set_stroke(colour, 4, opacity=0.55)
        return VGroup(s, s2)

    def construct(self):
        register_fonts()
        self._cache = {}
        fw, fh = config.frame_width, config.frame_height

        # ---- ? in a ring ------------------------------------------------- #
        ring = Circle(radius=fh * Q_MARK_R).set_stroke(TEAL, 5).set_fill(opacity=0)
        qm = self.t("?", int(fh * Q_MARK_R * 105), TEAL).move_to(ring.get_center())
        head = VGroup(ring, qm).move_to(norm_point(0.5, Q_MARK_Y))

        # ---- प्रश्न, gold, with sparks and a rule under it ---------------- #
        word = self.t("प्रश्न", Q_WORD_SIZE, GOLD).move_to(norm_point(0.5, Q_WORD_Y))
        sp = self.sparks(word, pad=TICK_PAD)
        rule = self.scribble(word.width * RULE_W, CREAM, wobble=0.018)
        rule.rotate(PAPER_TILT * 0.7).move_to(norm_point(0.5, RULE_Y))

        # ---- the notepaper ----------------------------------------------- #
        paper = ImageMobject(PAPER)
        paper.width = fw * PAPER_W          # width is what the reference fixes
        paper.move_to(norm_point(0.5, PAPER_Y))

        # ---- the question, fitted so it CANNOT leak ---------------------- #
        (cx, cy), bw, bh = writable_box(paper)
        size, lines = fit_lines(
            self.QUESTION,
            width_of=self._w,
            limit_w=bw,
            limit_h=bh,
            line_h_of=lambda s: self._w("क", s) * 2.35,
            space_of=lambda s: self._w(" ", s),
        )
        rows = VGroup()
        for words in lines:
            line = " ".join(words)
            t2c = {self.HIGHLIGHT: PAPER_HILITE} if self.HIGHLIGHT in line else {}
            rows.add(Text(line, font=FONT, font_size=size, color=PAPER_INK,
                          weight=FONT_W, t2c=t2c))
        rows.arrange(DOWN, buff=0.16, aligned_edge=LEFT)
        if rows.width > bw:                       # a single very long word
            rows.scale(bw / rows.width)
        rows.rotate(PAPER_TILT)                # sit on the ruled lines
        rows.move_to([cx, cy, 0])
        if not fits(rows, paper):
            raise ValueError(
                f"question does not fit the paper at size {size} — "
                f"text {rows.width:.2f}x{rows.height:.2f}, box {bw:.2f}x{bh:.2f}")

        # the hand-drawn double underline
        swoosh = self.scribble(rows.width * 0.62, PAPER_INK, wobble=0.045)
        swoosh.rotate(PAPER_TILT)
        swoosh.next_to(rows, DOWN, buff=0.20)

        # ---- the years pill ---------------------------------------------- #
        yr = VGroup(self.t("वर्ष ", 36, CREAM), self.t(self.YEARS, 42, TEAL),
                    self.t(" में", 36, CREAM)).arrange(RIGHT, buff=0.10)
        yr2 = self.t("ये प्रश्न था", 36, CREAM)
        ytxt = VGroup(yr, yr2).arrange(DOWN, buff=0.12)
        pill = RoundedRectangle(width=ytxt.width + 0.85, height=ytxt.height + 0.48,
                                corner_radius=0.30)
        pill.set_stroke(GOLD, 4).set_fill(opacity=0)
        pills = VGroup(pill, ytxt)
        pills.rotate(PAPER_TILT * 0.8).move_to(norm_point(0.5, YEARS_Y))
        psp = self.sparks(pill, GOLD, n=4, pad=0.22)

        # ---- play --------------------------------------------------------- #
        self.play(FadeIn(head, scale=1.15), run_time=0.5)
        self.play(FadeIn(word, shift=UP * 0.14), run_time=0.45)
        self.play(LaggedStart(*[GrowFromCenter(s) for s in sp], lag_ratio=0.08),
                  GrowFromEdge(rule, LEFT), run_time=0.55)
        self.play(FadeIn(paper, shift=DOWN * 0.30, scale=1.04), run_time=0.7)
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.14) for r in rows],
                              lag_ratio=0.20), run_time=0.9)
        self.play(Create(swoosh), run_time=0.45)
        self.play(FadeIn(pills, shift=UP * 0.12),
                  LaggedStart(*[GrowFromCenter(s) for s in psp], lag_ratio=0.08),
                  run_time=0.6)
        self.wait(2.2)
