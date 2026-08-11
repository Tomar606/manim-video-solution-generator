# Constants Q and r^2 are the same everywhere on the sphere -> pull them out.
class SegmentScene(ThemedScene):
    def construct(self):
        YEL = "#FFD54F"
        src = MathTex(
            r"\Phi=\oint_S \left(\frac{Q}{4\pi\varepsilon_0 r^2}\hat r\right)"
            r"\cdot d\vec A",
            color=THEME["primary"],
        )
        self.fit_safe(src, pad=0.9)
        self.add(src)
        dst = MathTex(
            r"\Phi=\frac{Q}{4\pi\varepsilon_0 r^2}\oint_S \hat r\cdot d\vec A",
            color=THEME["primary"],
        )
        self.fit_safe(dst, pad=0.9)
        self.play(TransformMatchingShapes(src, dst), run_time=2.0)
        self.play(Indicate(dst, color=YEL, scale_factor=1.06), run_time=0.8)
        self.wait(0.4)
