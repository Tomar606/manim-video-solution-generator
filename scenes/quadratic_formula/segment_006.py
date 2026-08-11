# Student beat — "take the square root of both sides?"
class SegmentScene(ThemedScene):
    def construct(self):
        q = self.caption("Take the square root of both sides?", scale=0.95)
        q.set_color(THEME["secondary"])
        hint = self.eq(r"\sqrt{\phantom{x}}", color=THEME["accent_2"]).scale(1.2)
        group = VGroup(q, hint).arrange(DOWN, buff=0.6)
        self.fit_safe(group, pad=0.75)

        self.play(FadeIn(q, shift=0.2 * UP), run_time=0.8)
        self.play(Write(hint), run_time=0.7)
        self.wait(0.4)
