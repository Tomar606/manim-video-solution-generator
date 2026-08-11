# SCENE 4 intro — the first of the two characteristics.
class SegmentScene(ThemedScene):
    CAPTION_MODE = "narration"

    def construct(self):
        badge = Circle(radius=0.46, stroke_width=3.0, stroke_color=DB_ORANGE,
                       fill_color="#12203C", fill_opacity=0.9)
        badge.move_to(self.stage_center + UP * 1.70)
        num = opt_label("1", DB_ORANGE, size=38, weight="BOLD")
        num.move_to(badge.get_center())

        title = chip("Characteristic 1", DB_ORANGE, size=27)
        title.next_to(badge, DOWN, buff=0.46)
        sub = chip("Strong Metallic Bonding", "#FFFFFF", size=25)
        sub.next_to(title, DOWN, buff=0.34)

        self.show_caption("To ab samajhte hain d-block elements ki pehli "
                          "important characteristic.")               # 0.55
        self.play(FadeIn(badge, scale=0.6), FadeIn(num, scale=0.6),
                  run_time=0.75)                                     # 0.75
        self.play(FadeIn(title, shift=UP * 0.22), run_time=0.60)     # 0.60
        self.play(FadeIn(sub, shift=UP * 0.22), run_time=0.60)       # 0.60
        self.wait(1.50)                                              # 1.50
