# Divide through by a.
class SegmentScene(ThemedScene):
    def construct(self):
        prev = self.eq(r"a x^2 + b x + c = 0", color=THEME["muted"]).scale(0.85)
        cur = self.eq(r"x^2 + \frac{b}{a} x + \frac{c}{a} = 0")
        group = VGroup(prev, cur).arrange(DOWN, buff=0.8)
        self.fit_safe(group, pad=0.85)

        self.play(FadeIn(prev, shift=0.2 * UP), run_time=0.6)
        self.play(Write(cur), run_time=1.7)
        self.play(Indicate(cur, color=THEME["accent"], scale_factor=1.05),
                  run_time=0.7)
        self.wait(0.4)
