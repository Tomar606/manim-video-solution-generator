# The result IS Gauss's law — box it with a soft white glow and hold.
class SegmentScene(ThemedScene):
    def construct(self):
        YEL = "#FFD54F"
        eq = MathTex(
            r"\oint_S \vec E\cdot d\vec A = \frac{Q_{\text{enclosed}}}{\varepsilon_0}",
            color=THEME["primary"],
        )
        self.fit_safe(eq, pad=0.82)
        self.play(Write(eq), run_time=2.0)

        box = SurroundingRectangle(eq, color="#FFFFFF", buff=0.35,
                                   stroke_width=2.5)
        glow = SurroundingRectangle(eq, color="#FFFFFF", buff=0.35,
                                    stroke_width=9, stroke_opacity=0.25)
        self.play(Create(box), FadeIn(glow), run_time=1.0)
        self.play(Indicate(eq, color=YEL, scale_factor=1.05), run_time=1.0)
        self.play(FadeOut(glow), run_time=0.8)
        self.wait(1.5)
