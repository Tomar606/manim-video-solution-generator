# Key definition (the caption the user asked for).
class SegmentScene(ThemedScene):
    def construct(self):
        c = self.stage_center
        title = self.heading("Electric Flux", color="#FFE24A").scale(1.05)
        self.top_caption(title, buff=0.9)

        defn = self.label(
            "= Total electric field crossing\na closed surface",
            color="#FFFFFF", scale=0.72)
        defn.move_to(c)
        line = Line(defn.get_corner(DL) + DOWN * 0.15,
                    defn.get_corner(DR) + DOWN * 0.15,
                    color="#6E86F0", stroke_width=3)

        self.play(FadeIn(title, shift=DOWN * 0.2), run_time=0.7)
        self.play(Write(defn), run_time=1.6)
        self.play(Create(line), run_time=0.6)
        self.wait(1.6)
