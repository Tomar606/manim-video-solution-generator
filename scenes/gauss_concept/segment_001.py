# Field lines represent direction & strength, not electrons.
class SegmentScene(ThemedScene):
    def construct(self):
        c = self.stage_center
        field = make_radial_field(c, n=12, r_in=0.62, r_out=2.25, color="#FFFFFF")
        charge = make_charge(c)
        self.add(field, charge)   # continues seamlessly from the previous beat
        cap = self.label(
            "These lines are not electrons.\n"
            "They show the field's direction and strength.",
            color="#FFFFFF", scale=0.56)
        self.top_caption(cap)

        self.play(FadeIn(cap, shift=DOWN * 0.2), run_time=0.7)
        self.play(LaggedStart(*[Indicate(a, color="#FFE24A", scale_factor=1.15)
                                for a in field], lag_ratio=0.04), run_time=1.6)
        self.wait(1.0)
