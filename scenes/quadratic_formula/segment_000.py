# Opening — title + the general quadratic equation.
class SegmentScene(ThemedScene):
    def construct(self):
        title = self.heading("The Quadratic Formula")
        eq = self.eq(r"a x^2 + b x + c = 0")
        group = VGroup(title, eq).arrange(DOWN, buff=0.9)
        self.fit_safe(group, pad=0.8)

        self.play(FadeIn(title, shift=0.3 * UP), run_time=0.9)
        self.play(Write(eq), run_time=1.8)
        u = self.underline(eq)
        self.play(Create(u), run_time=0.7)
        self.wait(0.6)
