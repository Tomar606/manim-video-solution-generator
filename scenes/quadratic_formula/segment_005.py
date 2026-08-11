# Left side is a perfect square; combine fractions on the right.
class SegmentScene(ThemedScene):
    def construct(self):
        prev = self.eq(
            r"x^2 + \frac{b}{a} x + \left(\frac{b}{2a}\right)^2 "
            r"= \left(\frac{b}{2a}\right)^2 - \frac{c}{a}",
            color=THEME["muted"],
        ).scale(0.8)
        cur = self.eq(
            r"\left(x + \frac{b}{2a}\right)^2 = \frac{b^2 - 4ac}{4a^2}"
        )
        group = VGroup(prev, cur).arrange(DOWN, buff=0.8)
        self.fit_safe(group, pad=0.9)

        self.play(FadeIn(prev, shift=0.2 * UP), run_time=0.6)
        self.play(Write(cur), run_time=1.9)
        self.play(Indicate(cur, color=THEME["accent"], scale_factor=1.05),
                  run_time=0.8)
        self.wait(0.4)
