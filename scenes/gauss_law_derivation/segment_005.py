# Lemma: r-hat and dA are parallel on a sphere, so the dot product is just dA.
class SegmentScene(ThemedScene):
    def construct(self):
        YEL = "#FFD54F"
        eq = MathTex(r"\hat r\cdot d\vec A", r"=", r"dA", color=THEME["primary"])
        self.fit_safe(eq, pad=0.65)
        self.play(Write(eq), run_time=1.6)
        self.play(Indicate(eq[2], color=YEL, scale_factor=1.35), run_time=0.9)  # dA grows
        self.wait(0.4)
