# Substitute the surface area 4*pi*r^2 into the flux expression.
class SegmentScene(ThemedScene):
    def construct(self):
        src = MathTex(
            r"\Phi=\frac{Q}{4\pi\varepsilon_0 r^2}\oint_S dA",
            color=THEME["primary"],
        )
        self.fit_safe(src, pad=0.9)
        self.add(src)
        dst = MathTex(
            r"\Phi=\frac{Q}{4\pi\varepsilon_0 r^2}\left(4\pi r^2\right)",
            color=THEME["primary"],
        )
        self.fit_safe(dst, pad=0.9)
        self.play(TransformMatchingShapes(src, dst), run_time=1.8)
        self.wait(0.4)
