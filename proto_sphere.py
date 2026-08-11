"""Prototype: Image #1 style — checkered Gaussian sphere with a highlighted
area element, outward normal (area vector), E vector, and the boxed E.da HUD.
Portrait, 3D, slow camera orbit."""
from manim import *
import numpy as np

config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 8.0
config.frame_height = 14.222222
config.frame_rate = 30
config.background_color = "#4A63E7"   # cornflower blue, like the reference

R = 2.1
UP_SHIFT = OUT * 3.2   # raise the 3D content into the upper half of the frame


def sphere_pt(u, v):
    return np.array([R * np.cos(u) * np.sin(v),
                     R * np.sin(u) * np.sin(v),
                     R * np.cos(v)])


class SegmentScene(ThreeDScene):
    def construct(self):
        self.set_camera_orientation(phi=62 * DEGREES, theta=-45 * DEGREES)

        sphere = Surface(
            lambda u, v: sphere_pt(u, v),
            u_range=[0, TAU], v_range=[0, PI],
            resolution=(32, 32),
            checkerboard_colors=["#F4C842", "#FBE7A6"],
            fill_opacity=1.0, stroke_width=0.4, stroke_color="#B8860B",
        )

        # Area element patch (red), sitting just above the surface.
        u0, v0 = -25 * DEGREES, 52 * DEGREES
        d = 12 * DEGREES
        patch = Surface(
            lambda u, v: sphere_pt(u, v) * 1.01,
            u_range=[u0 - d, u0 + d], v_range=[v0 - d, v0 + d],
            resolution=(6, 6),
            checkerboard_colors=["#E5484D", "#E5484D"],
            fill_opacity=1.0, stroke_width=0,
        )

        P = sphere_pt(u0, v0)
        nrm = P / np.linalg.norm(P)
        normal = Arrow3D(P, P + 1.5 * nrm, color=BLACK,
                         thickness=0.02, base_radius=0.09)

        # E vector: mostly tangential (illustrates the angle in E . da).
        tu = np.array([-np.sin(u0) * np.sin(v0), np.cos(u0) * np.sin(v0), 0.0])
        tu = tu / np.linalg.norm(tu)
        efield = Arrow3D(P, P + 1.15 * (-tu), color="#F2E30C",
                         thickness=0.02, base_radius=0.09)

        # HUD equation, fixed in frame (does not rotate with the camera).
        eq = MathTex(r"\vec{E}", r"\cdot", r"d\vec{a}").scale(1.6)
        eq[0].set_color("#F2C200")
        eq[1].set_color("#111111")
        eq[2].set_color("#111111")
        box = SurroundingRectangle(eq, color=WHITE, buff=0.28, stroke_width=4)
        hud = VGroup(box, eq).to_edge(UP, buff=1.0)
        self.add_fixed_in_frame_mobjects(hud)

        # Raise all 3D content into the upper half; lower half stays background.
        world = Group(sphere, patch, normal, efield).shift(UP_SHIFT)

        self.play(Create(sphere), run_time=2.0)
        self.play(FadeIn(patch), Create(normal), run_time=1.0)
        self.play(Create(efield), run_time=0.8)
        self.begin_ambient_camera_rotation(rate=0.12)
        self.wait(4.0)
