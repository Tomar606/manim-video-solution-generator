# 4*pi*r^2 cancels top and bottom -> Q over epsilon-nought.
# TransformMatchingShapes fades the unmatched 4pi r^2 terms (reads as cancellation).
class SegmentScene(ThemedScene):
    def construct(self):
        YEL = "#FFD54F"
        src = MathTex(
            r"\Phi=\frac{Q}{4\pi\varepsilon_0 r^2}\left(4\pi r^2\right)",
            color=THEME["primary"],
        )
        self.fit_safe(src, pad=0.9)
        self.add(src)
        dst = MathTex(r"\Phi=\frac{Q}{\varepsilon_0}", color=THEME["primary"])
        self.fit_safe(dst, pad=0.7)
        self.play(TransformMatchingShapes(src, dst), run_time=2.0)
        self.play(Indicate(dst, color=YEL, scale_factor=1.1), run_time=0.9)
        self.wait(0.5)
