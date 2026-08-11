"""Environment self-test. Renders text + an equation, so a successful render
proves Cairo (shapes), Pango (text) and LaTeX + dvisvgm (MathTex) all work.

    docker-compose run --rm manim-video-generator \
        manim render -ql selftest_scene.py SelfTest

A green "Manim OK" video in media/ means the stack is ready. A LaTeX error here
(before running generate.py) points straight at a missing TeX package.
"""
from manim import *


class SelfTest(Scene):
    def construct(self):
        label = Text("Manim OK", color=GREEN)
        eq = MathTex(r"\oint \vec{E}\cdot d\vec{A}=\frac{Q_{enc}}{\varepsilon_0}")
        VGroup(label, eq).arrange(DOWN, buff=0.8)
        self.add(label, eq)
        self.wait(0.3)
