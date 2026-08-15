"""A sample frame set in the reference layout — for approval before any rebuild.

Every number comes from src/reference_style.py, which was measured off the three
approved stills. Three beats, matching the three references:

    1  caption alone, dropped to the vertical middle   (reference2)
    2  caption + a large formula with its legend       (reference3)
    3  caption + a labelled diagram                    (reference1)

The presenter is NOT in these frames — he is composited afterwards — but the
space he occupies is reserved: 66% of frame width with his head at 50%, or 56%
at 62% while a diagram is up.
"""
from manim import *  # noqa: F403
import numpy as np

from src.manim_helpers import ThemedScene, norm_point, register_fonts
from src.reference_style import (CAPTION_SIZE, CAPTION_TOP_Y, CAPTION_MID_Y,
                                 CAPTION_W, CYAN, COPPER, DIM, DIVIDER_W,
                                 DIVIDER_Y, GOLD, INK, SILVER, STAGE_BOT,
                                 STAGE_TOP, STAGE_W)

FONT, FONT_W = "Khand", "BOLD"


class StyleSample(ThemedScene):
    CAPTION_MODE = "narration"
    STAGE_BAND = (STAGE_TOP, STAGE_BOT)

    # ---- building blocks ------------------------------------------------ #
    def hindi(self, text, size=CAPTION_SIZE, color=INK, weight=FONT_W):
        return Text(text, font=FONT, font_size=size, color=color, weight=weight)

    def caption(self, lines, highlight=None, centred=False):
        """Two big white lines, one word optionally gold.

        The references put this at 8.5% when something is below it and drop it
        to the middle of the empty space when nothing is.
        """
        t2c = {highlight: GOLD} if highlight else {}
        g = VGroup(*[Text(l, font=FONT, font_size=CAPTION_SIZE, color=INK,
                          weight=FONT_W, t2c=t2c) for l in lines])
        g.arrange(DOWN, buff=0.22)
        limit = config.frame_width * CAPTION_W
        if g.width > limit:
            g.scale(limit / g.width)
        g.move_to(norm_point(0.5, CAPTION_MID_Y if centred else CAPTION_TOP_Y))
        g.shift(DOWN * g.height / 2)
        return g

    def divider(self, y=DIVIDER_Y):
        """Hairline rule with a glowing dot at its centre."""
        line = Line(LEFT, RIGHT).set_width(DIVIDER_W)
        line.set_stroke(DIM, 2, opacity=0.45)
        line.move_to(norm_point(0.5, y))
        dot = Dot(radius=0.075, color=CYAN).move_to(line.get_center())
        glow = VGroup(*[Dot(radius=0.075 * s, color=CYAN,
                            fill_opacity=0.13).move_to(line.get_center())
                        for s in (3.2, 2.2, 1.6)])
        return VGroup(line, glow, dot)

    def place(self, mob, y=0.5, pad=0.94):
        top, bot = norm_point(0.5, STAGE_TOP)[1], norm_point(0.5, STAGE_BOT)[1]
        w, h = config.frame_width * STAGE_W, top - bot
        s = min((w * pad) / mob.width if mob.width > w * pad else 1.0,
                (h * pad) / mob.height if mob.height > h * pad else 1.0)
        if s < 1.0:
            mob.scale(s)
        cy = top - (top - bot) * y
        mob.move_to([0, max(bot + mob.height / 2, min(top - mob.height / 2, cy)), 0])
        return mob

    def glowing(self, mob, color=CYAN, layers=5):
        """The soft bloom the references put behind a formula."""
        glow = VGroup()
        for i in range(layers, 0, -1):
            c = mob.copy().set_stroke(color, width=6 * i, opacity=0.035)
            c.set_fill(opacity=0)
            glow.add(c)
        return VGroup(glow, mob)

    def cell(self, scale=1.0):
        """The electrolysis cell from reference1 — glass, liquid, two electrodes."""
        w, h = 4.6 * scale, 2.6 * scale
        glass = RoundedRectangle(width=w, height=h, corner_radius=0.22 * scale)
        glass.set_stroke(SILVER, 5, opacity=0.85).set_fill(opacity=0)
        liquid = RoundedRectangle(width=w - 0.22, height=h - 0.75,
                                  corner_radius=0.16 * scale)
        liquid.set_fill(color="#2E6FA8", opacity=0.72).set_stroke(width=0)
        liquid.move_to(glass.get_center() + DOWN * 0.20 * scale)
        surface = Line(liquid.get_left() + RIGHT * 0.10, liquid.get_right() + LEFT * 0.10)
        surface.set_stroke("#6FB3E8", 3, opacity=0.55)
        surface.move_to([liquid.get_center()[0], liquid.get_top()[1], 0])
        bubbles = VGroup(*[
            Dot(radius=0.028 * scale, color="#9FD4F5", fill_opacity=0.5).move_to(
                [liquid.get_center()[0] + x, liquid.get_center()[1] + y, 0])
            for x, y in [(-0.5, -0.2), (-0.2, 0.25), (0.1, -0.35), (0.45, 0.1),
                         (0.75, -0.15), (-0.8, 0.05), (0.3, 0.4)]])
        an = Rectangle(width=0.30 * scale, height=2.15 * scale)
        an.set_fill(COPPER, 1).set_stroke("#F0A868", 2)
        an.move_to([glass.get_center()[0] - 1.5 * scale, glass.get_center()[1] + 0.12, 0])
        ca = Rectangle(width=0.30 * scale, height=2.15 * scale)
        ca.set_fill(SILVER, 1).set_stroke("#E6EEF7", 2)
        ca.move_to([glass.get_center()[0] + 1.5 * scale, glass.get_center()[1] + 0.12, 0])
        wy = glass.get_top()[1] + 1.05 * scale
        wire = VMobject().set_points_as_corners(
            [an.get_top(), [an.get_x(), wy, 0], [ca.get_x(), wy, 0], ca.get_top()]
        ).set_stroke(SILVER, 4, opacity=0.9)
        plus = Text("+", font=FONT, font_size=44, color=COPPER, weight=FONT_W)
        plus.move_to([an.get_x() + 0.55, wy + 0.30, 0])
        minus = Text("−", font=FONT, font_size=44, color=CYAN, weight=FONT_W)
        minus.move_to([ca.get_x() - 0.55, wy + 0.30, 0])
        bat = VGroup(Line([-0.02, wy - 0.30, 0], [-0.02, wy + 0.30, 0]).set_stroke(COPPER, 7),
                     Line([0.20, wy - 0.16, 0], [0.20, wy + 0.16, 0]).set_stroke(CYAN, 7))
        g = VGroup(glass, liquid, surface, bubbles, an, ca, wire, bat, plus, minus)
        g.an, g.ca = an, ca
        return g

    def pointer(self, target, label, sub, colour, side=-1):
        """Colour-coded label with a dashed curve up to what it names."""
        lab = Text(label, font=FONT, font_size=34, color=colour, weight=FONT_W)
        s1 = Text(sub[0], font=FONT, font_size=21, color=INK, weight=FONT_W)
        s2 = Text(sub[1], font=FONT, font_size=21, color=INK, weight=FONT_W)
        block = VGroup(lab, VGroup(s1, s2).arrange(DOWN, buff=0.08)
                       ).arrange(DOWN, buff=0.16)
        # Pinned to the band, not hung off the electrode: `next_to` put these
        # wherever the diagram happened to end, which was under the presenter.
        block.move_to([target.get_x() + side * 0.62,
                       norm_point(0.5, 0.545)[1], 0])
        arc = DashedVMobject(
            ArcBetweenPoints(block.get_top() + UP * 0.06,
                             target.get_bottom() + DOWN * 0.04,
                             angle=side * 0.5), num_dashes=9)
        arc.set_stroke(colour, 3, opacity=0.85)
        tip = Triangle(fill_opacity=1, color=colour).scale(0.075)
        tip.rotate(PI).move_to(target.get_bottom() + DOWN * 0.05)
        return VGroup(block, arc, tip)

    # ---- the three beats ------------------------------------------------- #
    def construct(self):
        register_fonts()
        self.caption_mob = None

        # ---- 1: caption alone, dropped to the middle (reference2) -------- #
        cap = self.caption(["कि परीक्षा में आपके", "चार नम्बर पक्के हो जाएं"],
                           centred=True)
        self.play(LaggedStart(*[FadeIn(l, shift=UP * 0.18) for l in cap],
                              lag_ratio=0.25), run_time=1.0)
        self.wait(1.6)
        self.play(FadeOut(cap), run_time=0.4)

        # ---- 2: caption + big formula + legend (reference3) --------------- #
        cap = self.caption(["यहाँ W है", "मुक्त पदार्थ की मात्रा"], highlight="मुक्त")
        self.caption_mob = cap
        div = self.divider()
        self.play(FadeIn(cap, shift=DOWN * 0.12), run_time=0.7)
        self.play(Create(div[0]), FadeIn(div[1:]), run_time=0.5)

        eq = MathTex(r"W", r"\propto", r"Q").scale(3.6)
        eq[0].set_color(INK); eq[1].set_color(CYAN); eq[2].set_color(INK)
        eq.move_to(norm_point(0.5, 0.365))
        # keep the glow group: fading only `eq` left its bloom copies on screen,
        # and they showed through the next beat as a ghost formula
        eq_g = self.glowing(eq)
        self.play(FadeIn(eq_g, scale=1.06), run_time=0.9)

        l1 = VGroup(Text("W", font=FONT, font_size=38, color=GOLD, weight=FONT_W),
                    Text("=  मुक्त पदार्थ की मात्रा", font=FONT, font_size=34,
                         color=INK, weight=FONT_W)).arrange(RIGHT, buff=0.24)
        l2 = VGroup(Text("Q", font=FONT, font_size=38, color=CYAN, weight=FONT_W),
                    Text("=  प्रवाहित विद्युत की मात्रा", font=FONT, font_size=34,
                         color=INK, weight=FONT_W)).arrange(RIGHT, buff=0.24)
        legend = VGroup(l1, l2).arrange(DOWN, buff=0.26)
        legend.move_to(norm_point(0.5, 0.505))
        self.play(FadeIn(l1, shift=UP * 0.10), run_time=0.45)
        self.play(FadeIn(l2, shift=UP * 0.10), run_time=0.45)
        self.wait(1.4)
        self.play(FadeOut(VGroup(cap, div, eq_g, legend)), run_time=0.45)

        # ---- 3: caption + labelled diagram (reference1) ------------------- #
        cap = self.caption(["और इसे ध्यान से", "समझना, क्योंकि"])
        self.caption_mob = cap
        self.play(FadeIn(cap, shift=DOWN * 0.12), run_time=0.7)

        rig = self.cell(0.95)
        rig.height = config.frame_height * 0.165
        rig.move_to(norm_point(0.5, 0.385))
        self.play(FadeIn(rig, shift=UP * 0.10), run_time=0.9)

        anode = self.pointer(rig.an, "एनोड (+)",
                             ["यहाँ ऑक्सीकरण होता है", "और इलेक्ट्रॉन निकलते हैं।"],
                             COPPER, side=-1)
        cathode = self.pointer(rig.ca, "कैथोड (−)",
                               ["यहाँ अपचयन होता है", "और इलेक्ट्रॉन प्राप्त होते हैं।"],
                               CYAN, side=+1)
        self.play(FadeIn(anode, shift=UP * 0.10), run_time=0.6)
        self.play(FadeIn(cathode, shift=UP * 0.10), run_time=0.6)
        self.wait(2.0)
