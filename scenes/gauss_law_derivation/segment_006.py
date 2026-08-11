# Apply the lemma: the integral simplifies to the integral of dA.
class SegmentScene(ThemedScene):
    def construct(self):
        src = MathTex(
            r"\Phi=\frac{Q}{4\pi\varepsilon_0 r^2}\oint_S \hat r\cdot d\vec A",
            color=THEME["primary"],
        )
        self.fit_safe(src, pad=0.9)
        self.add(src)
        dst = MathTex(
            r"\Phi=\frac{Q}{4\pi\varepsilon_0 r^2}\oint_S dA",
            color=THEME["primary"],
        )
        self.fit_safe(dst, pad=0.9)
        self.play(TransformMatchingShapes(src, dst), run_time=1.8)
        self.wait(0.4)
