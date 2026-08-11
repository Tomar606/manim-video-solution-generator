# SCENE 8b — the right concept card: an obstacle makes light spread, and that
# spreading is diffraction.
class SegmentScene(ThemedScene):
    def construct(self):
        lay = compare_layout(self.stage_center, self.stage_w)

        # Left card exactly as segment 11 left it.
        self.add(
            recap_card(lay["left_x"], WAVE_BLUE),
            opt_label("Two Coherent\nSources", "#FFFFFF", size=23
                      ).move_to([lay["left_x"], 3.92, 0]),
            flow_arrow(0.50).move_to([lay["left_x"], 3.28, 0]),
            opt_label("Interference", WAVE_BLUE, size=27, weight="SEMIBOLD"
                      ).move_to([lay["left_x"], 2.62, 0]),
            check_mark(0.85).move_to([lay["left_x"], 1.62, 0]),
        )
        self.caption_mob = caption_pill("Remember This")
        self.add(self.caption_mob)

        card = recap_card(lay["right_x"], WAVE_PURPLE)
        title = opt_label("Obstacle", "#FFFFFF", size=23)
        title.move_to([lay["right_x"], 3.98, 0])
        a1 = flow_arrow(0.38).move_to([lay["right_x"], 3.50, 0])
        mid = opt_label("Light Spreads", "#FFFFFF", size=23)
        mid.move_to([lay["right_x"], 3.02, 0])
        a2 = flow_arrow(0.38).move_to([lay["right_x"], 2.54, 0])
        result = opt_label("Diffraction", WAVE_PURPLE, size=27, weight="SEMIBOLD")
        result.move_to([lay["right_x"], 2.06, 0])
        tick = check_mark(0.85).move_to([lay["right_x"], 1.42, 0])

        self.play(FadeIn(card, scale=0.92), run_time=0.65)           # 0.65
        self.play(FadeIn(title, shift=UP * 0.20), run_time=0.50)     # 0.50
        self.play(GrowArrow(a1), run_time=0.40)                      # 0.40
        self.play(FadeIn(mid, shift=UP * 0.20), run_time=0.50)       # 0.50
        self.play(GrowArrow(a2), run_time=0.40)                      # 0.40
        self.play(FadeIn(result, shift=UP * 0.20), run_time=0.55)    # 0.55
        self.play(Create(tick), run_time=0.55)                       # 0.55
        self.wait(1.95)                                              # 1.95
