# The Gaussian surface is imaginary — just a calculation tool.
class SegmentScene(ThemedScene):
    def construct(self):
        c = self.stage_center
        field = make_radial_field(c, n=12, r_in=0.62, r_out=2.5, color="#FFFFFF")
        charge = make_charge(c)
        gauss = make_gaussian_circle(c, radius=2.1, color="#DCE6FF")
        self.add(field, charge, gauss)

        cap = self.label(
            "The Gaussian Surface is imaginary —\nonly a tool to make the maths easy",
            color="#FFFFFF", scale=0.58)
        self.top_caption(cap)
        tag = self.label("imaginary", color="#FFE24A", scale=0.6)
        tag.next_to(gauss, DOWN, buff=0.3)

        self.play(FadeIn(cap), run_time=0.7)
        self.play(gauss[1].animate.set_stroke(width=6),
                  rate_func=there_and_back, run_time=1.4)
        self.play(FadeIn(tag, shift=UP * 0.2), run_time=0.6)
        self.wait(2.2)
