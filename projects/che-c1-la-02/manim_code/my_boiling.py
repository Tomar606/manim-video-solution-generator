"""Elevation of boiling point, drawn from what I already believe the graph is.

No scan consulted. This is the vapour-pressure curve I produce when asked cold,
so it can be held against the page the student revises from.
"""
from pathlib import Path
import numpy as np
import manimpango
from manim import *

R = Path(__file__).resolve().parents[3]
for f in (R / "assets" / "fonts").glob("*.ttf"):
    manimpango.register_font(str(f))
config.pixel_width, config.pixel_height = 1280, 940
config.frame_height = 8.6
config.frame_width = 8.6 * 1280 / 940

INK, SOLV, SOLN, ACC = "#1A1A1A", "#1F6FB2", "#C0392B", "#1E8449"
F = "Poppins"


class MyBoiling(Scene):
    def construct(self):
        self.camera.background_color = "#FFFFFF"
        ax = Axes(x_range=[0, 10, 1], y_range=[0, 6, 1], x_length=7.4, y_length=4.6,
                  axis_config={"include_ticks": False, "stroke_width": 3,
                               "color": INK, "tip_width": 0.18, "tip_height": 0.18})
        ax.shift(DOWN * 0.4 + LEFT * 0.3)
        xl = Text("Temperature", font=F, font_size=22, color=INK).next_to(ax.x_axis, DOWN, buff=0.28)
        yl = Text("Vapour pressure", font=F, font_size=22, color=INK).rotate(PI / 2)
        yl.next_to(ax.y_axis, LEFT, buff=0.22)

        solv = ax.plot(lambda x: 0.30 * np.exp(0.30 * x), x_range=[0.4, 9.0], color=SOLV, stroke_width=5)
        soln = ax.plot(lambda x: 0.30 * np.exp(0.30 * (x - 1.35)), x_range=[1.6, 10.0], color=SOLN, stroke_width=5)

        P = 4.4                                     # the 1 atm line
        atm = DashedLine(ax.c2p(0, P), ax.c2p(10, P), stroke_width=3, color=INK).set_opacity(0.7)
        atm_t = Text("1 atm", font=F, font_size=20, color=INK).next_to(atm, UP, buff=0.06).align_to(atm, LEFT)

        xb0 = np.log(P / 0.30) / 0.30                # pure solvent boils here
        xb = xb0 + 1.35                              # solution boils later
        d0 = DashedLine(ax.c2p(xb0, 0), ax.c2p(xb0, P), stroke_width=2.5, color=SOLV).set_opacity(0.8)
        d1 = DashedLine(ax.c2p(xb, 0), ax.c2p(xb, P), stroke_width=2.5, color=SOLN).set_opacity(0.8)
        t0 = MathTex(r"T_b^{0}", color=SOLV).scale(0.75).next_to(ax.c2p(xb0, 0), DOWN, buff=0.16)
        t1 = MathTex(r"T_b", color=SOLN).scale(0.75).next_to(ax.c2p(xb, 0), DOWN, buff=0.16)

        c_solv = Text("pure solvent", font=F, font_size=21, color=SOLV)
        c_solv.move_to(ax.c2p(4.6, 3.3)).shift(UP * 0.30 + LEFT * 0.35)
        c_soln = Text("solution", font=F, font_size=21, color=SOLN)
        c_soln.move_to(ax.c2p(7.4, 2.1)).shift(DOWN * 0.15 + RIGHT * 0.35)

        br = DoubleArrow(ax.c2p(xb0, 1.0), ax.c2p(xb, 1.0), buff=0,
                         stroke_width=3, color=ACC, tip_length=0.16)
        dt = MathTex(r"\Delta T_b", color=ACC).scale(0.8).next_to(br, UP, buff=0.10)

        self.play(Create(ax), FadeIn(xl), FadeIn(yl), run_time=1.4)
        self.play(Create(atm), FadeIn(atm_t), run_time=0.7)
        self.play(Create(solv), FadeIn(c_solv), run_time=1.4)
        self.play(Create(soln), FadeIn(c_soln), run_time=1.4)
        self.play(Create(d0), FadeIn(t0), run_time=0.8)
        self.play(Create(d1), FadeIn(t1), run_time=0.8)
        self.play(GrowFromCenter(br), FadeIn(dt), run_time=0.9)
        eq = MathTex(r"\Delta T_b = T_b - T_b^{0}", color=INK).scale(0.85)
        eq.to_edge(DOWN, buff=0.22)
        self.play(FadeIn(eq), run_time=0.6)
        self.wait(0.8)
