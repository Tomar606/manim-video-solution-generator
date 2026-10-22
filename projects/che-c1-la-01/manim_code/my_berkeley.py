"""Berkeley–Hartley, drawn from what I already believe it looks like.

No scan consulted, no trace loaded — this is the apparatus I produce when asked
cold, so it can be held up against the page the student actually revises from.
"""
from pathlib import Path
import manimpango
from manim import *

R = Path(__file__).resolve().parents[3]
for f in (R / "assets" / "fonts").glob("*.ttf"):
    manimpango.register_font(str(f))
config.pixel_width, config.pixel_height = 1280, 940
config.frame_height = 9.6
config.frame_width = 9.6 * 1280 / 940

INK, WATER, SOLN, MEM = "#1A1A1A", "#4FA9E8", "#E0A33C", "#B06A3B"
F = "Poppins"


class MyBerkeley(Scene):
    def construct(self):
        self.camera.background_color = "#FFFFFF"
        # --- my mental model: one horizontal outer barrel, an inner porous tube
        OX, OY, OW, OH = 0.0, -0.2, 6.2, 2.3
        outer = RoundedRectangle(width=OW, height=OH, corner_radius=0.28)
        outer.set_stroke(INK, 4).set_fill("#EDEDED", 1).move_to([OX, OY, 0])
        inner = RoundedRectangle(width=OW - 1.5, height=OH - 1.15, corner_radius=0.16)
        inner.set_stroke(INK, 3.5).set_fill("#FFFFFF", 1).move_to([OX, OY, 0])
        # membrane drawn as a band on the inner tube wall
        mem = VGroup(*[Line([inner.get_left()[0] + 0.06, inner.get_top()[1] + s, 0],
                            [inner.get_right()[0] - 0.06, inner.get_top()[1] + s, 0],
                            stroke_width=6, color=MEM) for s in (0.0,)],
                     *[Line([inner.get_left()[0] + 0.06, inner.get_bottom()[1] + s, 0],
                            [inner.get_right()[0] - 0.06, inner.get_bottom()[1] + s, 0],
                            stroke_width=6, color=MEM) for s in (0.0,)])
        # capillary rising from the left end
        cap_x = OX - OW / 2 - 0.55
        cap = Rectangle(width=0.30, height=3.0).set_stroke(INK, 3.5).set_fill("#FFFFFF", 1)
        cap.move_to([cap_x, OY + 1.9, 0])
        cap_arm = Line([OX - OW / 2, OY, 0], [cap_x, OY, 0], stroke_width=4, color=INK)
        cap_up = Line([cap_x, OY, 0], [cap_x, cap.get_bottom()[1], 0], stroke_width=4, color=INK)
        # stopcock funnel at the right end
        fx = OX + OW / 2 + 0.75
        funnel = Polygon([fx - 0.55, OY + 2.5, 0], [fx + 0.55, OY + 2.5, 0], [fx, OY + 1.7, 0])
        funnel.set_stroke(INK, 3.5).set_fill("#FFFFFF", 1)
        f_stem = Line([fx, OY + 1.7, 0], [fx, OY, 0], stroke_width=4, color=INK)
        f_arm = Line([fx, OY, 0], [OX + OW / 2, OY, 0], stroke_width=4, color=INK)
        tap = Circle(radius=0.14).set_stroke(INK, 3).set_fill("#FFFFFF", 1)
        tap.move_to([fx, OY + 1.15, 0])
        # piston and pressure gauge on top of the barrel
        px = OX + 1.2
        p_rod = Rectangle(width=0.22, height=1.25).set_stroke(INK, 3.5).set_fill("#BBBBBB", 1)
        p_rod.move_to([px, OY + OH / 2 + 0.55, 0])
        p_head = Rectangle(width=1.1, height=0.22).set_stroke(INK, 3.5).set_fill("#999999", 1)
        p_head.next_to(p_rod, UP, buff=0)
        gauge = Circle(radius=0.42).set_stroke(INK, 3.5).set_fill("#FFFFFF", 1)
        gauge.move_to([px + 1.7, OY + OH / 2 + 1.0, 0])
        needle = Line(gauge.get_center(), gauge.get_center() + UP * 0.28, stroke_width=4, color="#C0392B")
        g_arm = Line(p_rod.get_top() + DOWN * 0.1, gauge.get_left(), stroke_width=3, color=INK)

        rig = VGroup(outer, inner, mem, cap, cap_arm, cap_up, funnel, f_stem, f_arm,
                     tap, p_rod, p_head, gauge, needle, g_arm)
        self.play(Create(rig), run_time=2.2)

        def lab(t, at, to):
            m = Text(t, font=F, font_size=20, color=INK).move_to(at)
            return VGroup(m, Line(m.get_bottom() + DOWN * 0.05, to, stroke_width=1.8, color=INK))
        labels = VGroup(
            lab("capillary tube", [cap_x - 1.25, OY + 3.1, 0], [cap_x, OY + 2.6, 0]),
            lab("stopcock funnel", [fx + 1.35, OY + 3.0, 0], [fx + 0.2, OY + 2.4, 0]),
            lab("piston", [px - 1.5, OY + OH / 2 + 1.35, 0], [px - 0.15, OY + OH / 2 + 0.9, 0]),
            lab("pressure gauge", [px + 1.7, OY + OH / 2 + 1.95, 0], gauge.get_top()),
            lab("semipermeable membrane", [OX + 0.3, OY - 2.5, 0], [OX + 0.3, inner.get_bottom()[1], 0]),
            lab("inner porous tube", [OX - 2.2, OY - 1.9, 0], [OX - 1.4, inner.get_bottom()[1] + 0.2, 0]),
        )
        self.play(LaggedStart(*[FadeIn(m) for m in labels], lag_ratio=0.15), run_time=2.0)

        # water in, level marked
        water = Rectangle(width=inner.width - 0.12, height=inner.height - 0.12)
        water.set_fill(WATER, 0.55).set_stroke(width=0).move_to(inner)
        col = Rectangle(width=0.22, height=1.5).set_fill(WATER, 0.75).set_stroke(width=0)
        col.move_to([cap_x, OY + 1.15, 0])
        mark = Line([cap_x - 0.32, col.get_top()[1], 0], [cap_x + 0.32, col.get_top()[1], 0],
                    stroke_width=3, color="#C0392B")
        self.play(FadeIn(water), GrowFromEdge(col, DOWN), run_time=1.2)
        self.play(Create(mark), run_time=0.4)
        # solution into the outer barrel
        soln = VGroup()
        for dx in (-1, 1):
            r = Rectangle(width=(OW - inner.width) / 2 - 0.30, height=OH - 0.35)
            r.set_fill(SOLN, 0.45).set_stroke(width=0)
            r.move_to([OX + dx * (inner.width / 2 + (OW - inner.width) / 4 + 0.02), OY, 0])
            soln.add(r)
        self.play(FadeIn(soln), run_time=0.9)

        # osmosis: water leaves the inner tube, capillary level falls
        dots = VGroup(*[Dot(radius=0.07, color=WATER) for _ in range(6)])
        anims = []
        for i, dcirc in enumerate(dots):
            sx = inner.get_left()[0] + 0.6 + i * 0.75
            dcirc.move_to([sx, OY + 0.2, 0])
            anims.append(dcirc.animate.move_to([sx, OY + OH / 2 - 0.25, 0]))
        self.add(dots)
        self.play(*anims, col.animate.stretch_to_fit_height(0.75).move_to([cap_x, OY + 0.78, 0]),
                  run_time=2.2)
        self.play(FadeOut(dots), run_time=0.3)
        drop = Text("level falls", font=F, font_size=20, color="#C0392B")
        drop.next_to(mark, LEFT, buff=0.35)
        self.play(FadeIn(drop), run_time=0.4)

        # piston pushes, level returns to the mark
        self.play(p_rod.animate.shift(DOWN * 0.35), p_head.animate.shift(DOWN * 0.35),
                  Rotate(needle, -1.0, about_point=gauge.get_center()),
                  col.animate.stretch_to_fit_height(1.5).move_to([cap_x, OY + 1.15, 0]),
                  FadeOut(drop), run_time=1.8)
        res = Text("applied pressure = osmotic pressure", font=F, font_size=24, color=INK)
        res.to_edge(DOWN, buff=0.25)
        self.play(FadeIn(res), run_time=0.6)
        self.wait(0.8)
