# SCENE 5a — variable valency: the oxidation state morphs +2 -> +3 -> +4 -> +6.
class SegmentScene(ThemedScene):
    CAPTION_MODE = "narration"

    def construct(self):
        head = chip("Variable Oxidation State", DB_PURPLE, size=26)
        head.move_to(self.stage_center + UP * 2.00)

        ring = Circle(radius=0.78, stroke_width=3.0, stroke_color=DB_BLUE,
                      fill_color="#12203C", fill_opacity=0.85)
        ring.move_to(self.stage_center + UP * 0.30)

        states = ["+2", "+3", "+4", "+6"]
        labels = [opt_label(s, DB_ORANGE, size=44, weight="BOLD"
                            ).move_to(ring.get_center()) for s in states]

        self.show_caption("Ye variable valency aur variable oxidation "
                          "state dikhate hain.")                     # 0.55
        self.play(FadeIn(head, shift=DOWN * 0.18), Create(ring),
                  run_time=0.60)                                     # 0.60
        self.play(FadeIn(labels[0], scale=0.7), run_time=0.40)       # 0.40
        for a, b in zip(labels, labels[1:]):                         # 3 x 0.45
            self.play(ReplacementTransform(a, b), run_time=0.45)
        self.play(Indicate(labels[-1], scale_factor=1.15, color=DB_ORANGE),
                  run_time=0.50)                                     # 0.50
        self.wait(0.60)                                              # 0.60
