# Title card — "Gauss's Law Derivation" over the blueprint grid.
class SegmentScene(ThemedScene):
    def construct(self):
        title = self.heading("Gauss's Law Derivation")
        self.fit_safe(title, pad=0.8)
        self.play(FadeIn(title, shift=0.3 * UP), run_time=1.0)
        self.play(Indicate(title, color=THEME["accent"], scale_factor=1.06),
                  run_time=0.9)
        self.wait(0.6)
