# Lemma: summing dA over the closed sphere gives its surface area (blue accent).
class SegmentScene(ThemedScene):
    def construct(self):
        src = MathTex(r"\oint_S dA", color=THEME["primary"])
        self.fit_safe(src, pad=0.6)
        self.play(Write(src), run_time=1.2)
        self.play(Indicate(src, color=THEME["accent"], scale_factor=1.15),
                  run_time=0.7)
        dst = MathTex(r"\oint_S dA", r"=", r"4\pi r^2", color=THEME["primary"])
        self.fit_safe(dst, pad=0.75)
        self.play(TransformMatchingShapes(src, dst), run_time=1.6)
        self.play(Indicate(dst[2], color=THEME["accent"], scale_factor=1.2),
                  run_time=0.7)
        self.wait(0.4)
