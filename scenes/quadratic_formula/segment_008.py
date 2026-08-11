# Isolate x — the quadratic formula. Emphasize the final result.
class SegmentScene(ThemedScene):
    def construct(self):
        prev = self.eq(
            r"x + \frac{b}{2a} = \pm \frac{\sqrt{b^2 - 4ac}}{2a}",
            color=THEME["muted"],
        ).scale(0.8)
        cur = self.eq(r"x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}")
        group = VGroup(prev, cur).arrange(DOWN, buff=0.9)
        self.fit_safe(group, pad=0.85)

        self.play(FadeIn(prev, shift=0.2 * UP), run_time=0.6)
        self.play(Write(cur), run_time=2.0)
        box = SurroundingRectangle(cur, color=THEME["accent"], buff=0.28)
        self.play(Create(box), run_time=1.0)
        self.play(Indicate(cur, color=THEME["accent_2"], scale_factor=1.06),
                  run_time=0.9)
        self.wait(0.7)
