# The total field crossing the surface = Electric Flux.
class SegmentScene(ThemedScene):
    def construct(self):
        c = self.stage_center
        field = make_radial_field(c, n=12, r_in=0.62, r_out=2.6, color="#FFFFFF")
        charge = make_charge(c)
        gauss = make_gaussian_circle(c, radius=2.1, color="#DCE6FF")
        self.add(charge, gauss, field)

        cap = self.label(
            "The total field crossing the surface\nis the Electric Flux",
            color="#FFFFFF", scale=0.6)
        self.top_caption(cap)
        phi = MathTex(r"\Phi", color="#FFE24A").scale(1.5)
        phi.next_to(gauss, DOWN, buff=0.35)

        self.play(FadeIn(cap), run_time=0.7)
        self.play(LaggedStart(*[Indicate(a, color="#FFE24A", scale_factor=1.12)
                                for a in field], lag_ratio=0.05), run_time=1.8)
        self.play(Write(phi), run_time=0.6)
        self.wait(1.6)
