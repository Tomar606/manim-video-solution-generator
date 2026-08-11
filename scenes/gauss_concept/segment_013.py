# This is Gauss's Law — boxed with a soft glow.
class SegmentScene(ThemedScene):
    def construct(self):
        c = self.stage_center
        title = self.heading("This is Gauss's Law", color="#FFE24A").scale(0.95)
        self.top_caption(title, buff=0.9)

        eq = MathTex(r"\oint_S \vec{E}\cdot d\vec{a} = \frac{Q_{\text{enc}}}{\varepsilon_0}",
                     color="#FFFFFF").scale(1.3)
        eq.move_to(c)
        box = SurroundingRectangle(eq, color="#FFFFFF", buff=0.35, stroke_width=4)
        glow = SurroundingRectangle(eq, color="#FFE24A", buff=0.35,
                                    stroke_width=10, stroke_opacity=0.3)

        self.play(FadeIn(title, shift=DOWN * 0.2), run_time=0.5)
        self.play(Write(eq), run_time=1.4)
        self.play(Create(box), FadeIn(glow), run_time=0.7)
        self.wait(1.0)
