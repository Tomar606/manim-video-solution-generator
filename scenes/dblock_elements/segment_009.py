# SCENE 4d — good conductors of heat and electricity.
class SegmentScene(ThemedScene):
    CAPTION_MODE = "narration"

    def construct(self):
        icon_y = self.stage_center[1] + 1.15
        bolt = icon_bolt().scale(1.85).move_to([-1.55, icon_y, 0])
        heat = icon_heatwave().scale(1.70).move_to([1.55, icon_y, 0])
        t_e = opt_label("Electricity", FRINGE_YELLOW, size=22)
        t_e.move_to([-1.55, icon_y - 1.35, 0])
        t_h = opt_label("Heat", DB_RED, size=22)
        t_h.move_to([1.55, icon_y - 1.35, 0])

        arr = flow_arrow(0.46, color=DB_GREEN)
        arr.move_to([0.0, icon_y - 2.10, 0])
        lbl = chip("Good Conductor", DB_GREEN, size=26)
        lbl.next_to(arr, DOWN, buff=0.24)

        self.show_caption("aur ye heat aur electricity ke achhe "
                          "conductors hote hain.")                   # 0.55
        self.play(LaggedStart(FadeIn(bolt, scale=0.7), FadeIn(heat, scale=0.7),
                              lag_ratio=0.30), run_time=0.85)        # 0.85
        self.play(FadeIn(t_e, shift=UP * 0.16), FadeIn(t_h, shift=UP * 0.16),
                  run_time=0.45)                                     # 0.45
        self.play(GrowArrow(arr), run_time=0.35)                     # 0.35
        self.play(FadeIn(lbl, shift=UP * 0.20), run_time=0.50)       # 0.50
        self.wait(0.80)                                              # 0.80
