# Substitute Coulomb's E into the flux integral (morph, not a cut).
class SegmentScene(ThemedScene):
    def construct(self):
        src = MathTex(r"\Phi=\oint_S \vec E\cdot d\vec A", color=THEME["primary"])
        self.fit_safe(src, pad=0.8)
        self.add(src)
        dst = MathTex(
            r"\Phi=\oint_S \left(\frac{Q}{4\pi\varepsilon_0 r^2}\hat r\right)"
            r"\cdot d\vec A",
            color=THEME["primary"],
        )
        self.fit_safe(dst, pad=0.9)
        self.play(TransformMatchingShapes(src, dst), run_time=2.0)
        self.wait(0.5)
