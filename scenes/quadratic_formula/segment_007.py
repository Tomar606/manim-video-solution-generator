# Take the square root; introduce the plus-or-minus.
class SegmentScene(ThemedScene):
    def construct(self):
        prev = self.eq(
            r"\left(x + \frac{b}{2a}\right)^2 = \frac{b^2 - 4ac}{4a^2}",
            color=THEME["muted"],
        ).scale(0.8)
        cur = self.eq(
            r"x + \frac{b}{2a} = \pm \frac{\sqrt{b^2 - 4ac}}{2a}"
        )
        group = VGroup(prev, cur).arrange(DOWN, buff=0.8)
        self.fit_safe(group, pad=0.9)

        self.play(FadeIn(prev, shift=0.2 * UP), run_time=0.6)
        self.play(Write(cur), run_time=1.9)
        self.play(Indicate(cur, color=THEME["accent"], scale_factor=1.05),
                  run_time=0.8)
        self.wait(0.4)
