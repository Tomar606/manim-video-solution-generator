# Complete the square: add (b/2a)^2 to both sides. (director note: highlight)
class SegmentScene(ThemedScene):
    def construct(self):
        prev = self.eq(r"x^2 + \frac{b}{a} x = -\frac{c}{a}",
                       color=THEME["muted"]).scale(0.85)
        cur = self.eq(
            r"x^2 + \frac{b}{a} x + \left(\frac{b}{2a}\right)^2 "
            r"= \left(\frac{b}{2a}\right)^2 - \frac{c}{a}"
        )
        added = self.caption("complete the square", scale=0.7)
        added.set_color(THEME["accent_2"])
        group = VGroup(prev, cur).arrange(DOWN, buff=0.8)
        self.fit_safe(group, pad=0.9)
        added.next_to(cur, DOWN, buff=0.35)

        self.play(FadeIn(prev, shift=0.2 * UP), run_time=0.6)
        self.play(Write(cur), run_time=2.0)
        self.play(FadeIn(added, shift=0.15 * UP), run_time=0.6)
        self.play(Indicate(cur, color=THEME["accent"], scale_factor=1.04),
                  run_time=0.8)
        self.wait(0.4)
