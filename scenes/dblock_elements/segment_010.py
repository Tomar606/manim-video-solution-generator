# SCENE 5 intro — the second characteristic.
class SegmentScene(ThemedScene):
    CAPTION_MODE = "narration"

    def construct(self):
        badge = Circle(radius=0.46, stroke_width=3.0, stroke_color=DB_PURPLE,
                       fill_color="#12203C", fill_opacity=0.9)
        badge.move_to(self.stage_center + UP * 1.55)
        num = opt_label("2", DB_PURPLE, size=38, weight="BOLD")
        num.move_to(badge.get_center())
        title = chip("Characteristic 2", DB_PURPLE, size=27)
        title.next_to(badge, DOWN, buff=0.46)

        self.show_caption("Ab doosri important characteristic.")     # 0.55
        self.play(FadeIn(badge, scale=0.6), FadeIn(num, scale=0.6),
                  run_time=0.60)                                     # 0.60
        self.play(FadeIn(title, shift=UP * 0.22), run_time=0.55)     # 0.55
        self.wait(0.30)                                              # 0.30
