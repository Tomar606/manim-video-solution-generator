# We can't count them — so we use Gauss's Law.
class SegmentScene(ThemedScene):
    def construct(self):
        c = self.stage_center
        field = make_radial_field(c, n=12, r_in=0.62, r_out=2.25,
                                  color="#FFFFFF").set_opacity(0.25)
        charge = make_charge(c).set_opacity(0.5)
        self.add(field, charge)

        title = self.heading("Gauss's Law", color="#FFE24A").scale(1.3)
        title.move_to(c)
        box = SurroundingRectangle(title, color="#FFFFFF", buff=0.35, stroke_width=4)

        self.play(FadeIn(VGroup(title, box), scale=0.85), run_time=1.0)
        self.play(Indicate(title, color="#FFFFFF", scale_factor=1.05), run_time=0.8)
        self.wait(0.8)
