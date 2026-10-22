"""A dry cell drawn the way a model draws one when nobody hands it the page.

Nothing here is copied from the book — this is the generic dry cell: the shape
that turns up when you ask for "a dry cell diagram", assembled from what the
model already believes one looks like. That is the point of the comparison.
"""
from pathlib import Path
import manimpango
from manim import *

R = Path(__file__).resolve().parents[3]
for f in (R / "assets" / "fonts").glob("*.ttf"):
    manimpango.register_font(str(f))
config.pixel_width, config.pixel_height = 1300, 1000
config.frame_height = 8.0
config.frame_width = 8.0 * 1300 / 1000

INK = "#1A1A1A"


class GenericDryCell(Scene):
    def construct(self):
        self.camera.background_color = "#FFFFFF"
        W, H = 2.6, 4.4
        # rounded battery body — the shape everyone's mental image defaults to
        body = RoundedRectangle(width=W, height=H, corner_radius=0.30)
        body.set_stroke(INK, 4).set_fill("#D8D2C4", 1)
        # a domed positive terminal on top, like an AA cell
        cap = RoundedRectangle(width=0.62, height=0.34, corner_radius=0.12)
        cap.set_stroke(INK, 4).set_fill("#BFBFBF", 1).next_to(body, UP, buff=-0.04)
        # concentric coloured layers
        zinc = RoundedRectangle(width=W - 0.34, height=H - 0.44, corner_radius=0.22)
        zinc.set_stroke(INK, 3).set_fill("#AEB6BD", 1).move_to(body)
        paste = RoundedRectangle(width=W - 0.94, height=H - 1.00, corner_radius=0.18)
        paste.set_stroke(INK, 3).set_fill("#E4CE93", 1).move_to(body)
        core = RoundedRectangle(width=W - 1.62, height=H - 1.46, corner_radius=0.14)
        core.set_stroke(INK, 3).set_fill("#6E6E6E", 1).move_to(body)
        rod = Rectangle(width=0.30, height=H - 0.70)
        rod.set_stroke(INK, 3).set_fill("#3A3A3A", 1).move_to(body).shift(UP * 0.30)

        cell = VGroup(body, zinc, paste, core, rod, cap)
        cell.move_to(ORIGIN).shift(LEFT * 1.85 + DOWN * 0.15)

        def lab(text, target, dy):
            t = Text(text, font="Poppins", font_size=21, color=INK)
            t.move_to([cell.get_right()[0] + 1.55, cell.get_center()[1] + dy, 0])
            t.shift(RIGHT * t.width / 2)
            arm = Line(t.get_left() + LEFT * 0.08, target, stroke_width=2, color=INK)
            return VGroup(t, arm)

        labels = VGroup(
            lab("carbon rod (+)", rod.get_top() + DOWN * 0.25, 1.72),
            lab("manganese dioxide", core.get_right() + LEFT * 0.10, 0.85),
            lab("ammonium chloride paste", paste.get_right() + LEFT * 0.10, 0.05),
            lab("zinc container (−)", zinc.get_right() + LEFT * 0.08, -0.85),
            lab("outer casing", body.get_right() + LEFT * 0.04, -1.70),
        )
        self.add(cell, labels)
        self.wait(0.1)
