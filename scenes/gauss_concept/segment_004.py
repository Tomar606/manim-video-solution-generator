# Draw an imaginary closed surface around the charge — the Gaussian surface.
class SegmentScene(ThemedScene):
    def construct(self):
        c = self.stage_center
        field = make_radial_field(c, n=12, r_in=0.62, r_out=2.5, color="#FFFFFF")
        charge = make_charge(c)
        self.add(field, charge)

        gauss = make_gaussian_circle(c, radius=2.1, color="#DCE6FF")
        cap = self.label(
            "Draw an imaginary closed surface\naround the charge — a Gaussian Surface",
            color="#FFFFFF", scale=0.58)
        self.top_caption(cap)

        self.play(FadeIn(gauss[0]), Create(gauss[1]), run_time=1.6)
        self.play(FadeIn(cap, shift=DOWN * 0.2), run_time=0.8)
        self.wait(1.2)
