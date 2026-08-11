# Coulomb's law for E — build left-to-right, emphasize the pieces.
class SegmentScene(ThemedScene):
    def construct(self):
        YEL = "#FFD54F"
        eq = MathTex(
            r"\vec{E}", r"=", r"\frac{1}{4\pi\varepsilon_0}",
            r"\frac{Q}{r^2}", r"\hat r",
            color=THEME["primary"],
        )
        self.fit_safe(eq, pad=0.8)
        self.play(Write(eq), run_time=2.2)          # natural left-to-right build
        self.play(Indicate(eq[3], color=YEL, scale_factor=1.18), run_time=0.7)   # Q / r^2
        self.play(Indicate(eq[2], color=THEME["accent"], scale_factor=1.10),
                  run_time=0.7)                                                   # 1/(4πε0)
        self.wait(0.4)
