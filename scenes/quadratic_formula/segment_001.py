# Student beat — a spoken question. Show it as a caption.
class SegmentScene(ThemedScene):
    def construct(self):
        q = self.caption("Where do we even start?", scale=1.0)
        q.set_color(THEME["secondary"])
        self.fit_safe(q, pad=0.75)
        self.play(FadeIn(q, shift=0.25 * UP), run_time=0.8)
        self.play(Indicate(q, color=THEME["accent_2"], scale_factor=1.05),
                  run_time=0.7)
        self.wait(0.4)
