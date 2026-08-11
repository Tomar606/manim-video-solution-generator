# Flux definition — keep Coulomb faintly above for a beat, then let it go.
class SegmentScene(ThemedScene):
    def construct(self):
        cur = MathTex(r"\Phi=\oint_S \vec E\cdot d\vec A", color=THEME["primary"])
        self.fit_safe(cur, pad=0.8)
        prev = MathTex(r"\vec{E}=\frac{1}{4\pi\varepsilon_0}\frac{Q}{r^2}\hat r",
                       color=THEME["muted"]).scale(0.55)
        prev.next_to(cur, UP, buff=0.7)

        self.add(prev)
        self.play(Write(cur), run_time=1.8)
        self.wait(0.6)
        self.play(FadeOut(prev, shift=0.2 * UP), run_time=0.6)
        self.wait(0.3)
