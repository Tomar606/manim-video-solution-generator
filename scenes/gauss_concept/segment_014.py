# Teaser for the next part: the derivation.
class SegmentScene(ThemedScene):
    def construct(self):
        c = self.stage_center
        t1 = self.label("Concept done", color="#EAF2FF", scale=0.7)
        t2 = self.heading("Next: the Derivation", color="#FFE24A").scale(1.05)
        arrow = MathTex(r"\rightarrow", color="#FFFFFF").scale(1.6)
        grp = VGroup(t1, t2, arrow).arrange(DOWN, buff=0.55).move_to(c)

        self.play(FadeIn(t1, shift=UP * 0.2), run_time=0.6)
        self.play(Write(t2), run_time=0.9)
        self.play(FadeIn(arrow, shift=RIGHT * 0.3), run_time=0.6)
        self.play(Indicate(t2, color="#FFFFFF", scale_factor=1.05), run_time=0.8)
        self.wait(0.8)
