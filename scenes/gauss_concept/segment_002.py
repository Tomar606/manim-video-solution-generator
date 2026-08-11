# Can we count the total field escaping? (the motivating question)
class SegmentScene(ThemedScene):
    def construct(self):
        c = self.stage_center
        field = make_radial_field(c, n=12, r_in=0.62, r_out=2.25, color="#FFFFFF")
        charge = make_charge(c)
        self.add(field, charge)
        cap = self.label(
            "How much field escapes in total?\n"
            "Can we count every single line?",
            color="#FFFFFF", scale=0.58)
        self.top_caption(cap)
        q = MathTex("?", color="#FFE24A").scale(2.6)
        q.next_to(field, RIGHT, buff=0.3)

        self.play(FadeIn(cap, shift=DOWN * 0.2), run_time=0.7)
        self.play(Write(q), run_time=0.6)
        self.play(Indicate(q, color="#FFFFFF", scale_factor=1.3), run_time=0.8)
        self.wait(1.2)
