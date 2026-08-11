# A positive charge with its electric field radiating outward.
class SegmentScene(ThemedScene):
    def construct(self):
        c = self.stage_center
        field = make_radial_field(c, n=12, r_in=0.62, r_out=2.25, color="#FFFFFF")
        charge = make_charge(c)
        cap = self.label(
            "A positive charge sends its Electric Field\noutward in every direction",
            color="#FFFFFF", scale=0.6)
        self.top_caption(cap)

        self.play(FadeIn(charge, scale=0.5), run_time=0.8)
        self.play(LaggedStart(*[GrowArrow(a) for a in field], lag_ratio=0.06),
                  run_time=1.8)
        self.play(FadeIn(cap, shift=DOWN * 0.2), run_time=0.8)
        self.wait(1.4)
