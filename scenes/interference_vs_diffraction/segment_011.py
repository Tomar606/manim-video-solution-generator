# SCENE 8a — "Remember This". The left concept card: two coherent sources
# always means interference.
class SegmentScene(ThemedScene):
    def construct(self):
        lay = compare_layout(self.stage_center, self.stage_w)
        card = recap_card(lay["left_x"], WAVE_BLUE)
        title = opt_label("Two Coherent\nSources", "#FFFFFF", size=23)
        title.move_to([lay["left_x"], 3.92, 0])
        arrow = flow_arrow(0.50).move_to([lay["left_x"], 3.28, 0])
        result = opt_label("Interference", WAVE_BLUE, size=27, weight="SEMIBOLD")
        result.move_to([lay["left_x"], 2.62, 0])
        tick = check_mark(0.85).move_to([lay["left_x"], 1.62, 0])

        self.show_caption("Remember This")                           # 0.55
        self.play(FadeIn(card, scale=0.92), run_time=0.65)           # 0.65
        self.play(FadeIn(title, shift=UP * 0.20), run_time=0.60)     # 0.60
        self.play(GrowArrow(arrow), run_time=0.50)                   # 0.50
        self.play(FadeIn(result, shift=UP * 0.20), run_time=0.60)    # 0.60
        self.play(Create(tick), run_time=0.60)                       # 0.60
        self.wait(2.00)                                              # 2.00
