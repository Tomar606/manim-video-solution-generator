# SCENE 8c — hold on the two takeaways, then clear the lower frame so the video
# can cut into the answer-writing shot.
class SegmentScene(ThemedScene):
    def construct(self):
        lay = compare_layout(self.stage_center, self.stage_w)

        left = VGroup(
            recap_card(lay["left_x"], WAVE_BLUE),
            opt_label("Two Coherent\nSources", "#FFFFFF", size=23
                      ).move_to([lay["left_x"], 3.92, 0]),
            flow_arrow(0.50).move_to([lay["left_x"], 3.28, 0]),
            opt_label("Interference", WAVE_BLUE, size=27, weight="SEMIBOLD"
                      ).move_to([lay["left_x"], 2.62, 0]),
            check_mark(0.85).move_to([lay["left_x"], 1.62, 0]),
        )
        right = VGroup(
            recap_card(lay["right_x"], WAVE_PURPLE),
            opt_label("Obstacle", "#FFFFFF", size=23
                      ).move_to([lay["right_x"], 3.98, 0]),
            flow_arrow(0.38).move_to([lay["right_x"], 3.50, 0]),
            opt_label("Light Spreads", "#FFFFFF", size=23
                      ).move_to([lay["right_x"], 3.02, 0]),
            flow_arrow(0.38).move_to([lay["right_x"], 2.54, 0]),
            opt_label("Diffraction", WAVE_PURPLE, size=27, weight="SEMIBOLD"
                      ).move_to([lay["right_x"], 2.06, 0]),
            check_mark(0.85).move_to([lay["right_x"], 1.42, 0]),
        )
        self.add(left, right)
        self.caption_mob = caption_pill("Remember This")
        self.add(self.caption_mob)

        cards = VGroup(left, right)

        # Both takeaways land together...
        self.play(LaggedStart(
            Indicate(left[3], scale_factor=1.06, color=WAVE_BLUE),
            Indicate(right[5], scale_factor=1.06, color=WAVE_PURPLE),
            lag_ratio=0.40), run_time=1.30)                          # 1.30
        self.wait(2.00)                                              # 2.00
        # ...then settle upward, leaving the lower frame clean for the cut.
        self.play(cards.animate.scale(0.94, about_point=self.stage_center)
                  .shift(UP * 0.30), run_time=0.90)                  # 0.90
        self.wait(1.20)                                              # 1.20
        self.play(FadeOut(cards, shift=UP * 0.25),
                  FadeOut(self.caption_mob, shift=UP * 0.20),
                  run_time=1.10)                                     # 1.10
