# SCENE 3a — most d-block elements are also called Transition Elements.
class SegmentScene(ThemedScene):
    CAPTION_MODE = "narration"

    def construct(self):
        src = chip("d-Block Elements", DB_ORANGE, size=29)
        src.move_to(self.stage_center + UP * 1.55)
        note = opt_label("zyadatar", DB_BLUE, size=23)
        arrow = flow_arrow(0.62)
        dst = chip("Transition Elements", DB_GREEN, size=29)

        arrow.next_to(src, DOWN, buff=0.30)
        note.next_to(arrow, RIGHT, buff=0.24)
        dst.next_to(arrow, DOWN, buff=0.30)

        self.show_caption("d-block ke zyadatar elements ko Transition "
                          "Elements bhi kaha jata hai.")             # 0.55
        self.play(FadeIn(src, shift=DOWN * 0.20), run_time=0.65)     # 0.65
        self.play(GrowArrow(arrow), FadeIn(note, shift=LEFT * 0.18),
                  run_time=0.60)                                     # 0.60
        self.play(FadeIn(dst, shift=UP * 0.22), run_time=0.70)       # 0.70
        self.play(Indicate(dst, scale_factor=1.06, color=DB_GREEN),
                  run_time=0.70)                                     # 0.70
        self.wait(1.30)                                              # 1.30
