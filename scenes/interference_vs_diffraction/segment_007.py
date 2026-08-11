# SCENE 6a — "Brightness Difference". The width labels clear out and intensity
# axes take their place under each pattern.
class SegmentScene(ThemedScene):
    def construct(self):
        lay, p = compare_base(self.stage_center, self.stage_w)
        self.add(p["divider"], p["head_l"], p["head_r"],
                 p["plate_l"], p["plate_r"])
        self.caption_mob = caption_pill("Fringe Pattern")
        self.add(self.caption_mob)

        l_bands, r_bands = fringe_bands(lay)
        self.add(l_bands, r_bands)

        # Carry over exactly what segment 6 ended on, then retire it.
        N = N_INTERFERENCE_FRINGES
        period = lay["plate_w"] / (N + 0.4)
        half = (N - 1) / 2.0
        bracket_y = lay["plate_y"] - lay["plate_h"] / 2 - 0.34
        unit = lay["plate_w"] * DIFF_PLATE_FRAC / 8.0
        old = VGroup(
            measure_bracket(lay["left_x"] + (0 - half) * period,
                            lay["left_x"] + (1 - half) * period, bracket_y),
            measure_bracket(lay["left_x"] + (3 - half) * period,
                            lay["left_x"] + (4 - half) * period, bracket_y),
            measure_bracket(lay["right_x"] - unit, lay["right_x"] + unit,
                            bracket_y, color=HL_GREEN),
            measure_bracket(lay["right_x"] + unit, lay["right_x"] + 2 * unit,
                            bracket_y, color=HL_ORANGE),
            opt_label("Equal Fringe\nWidth", HL_ORANGE, size=25
                      ).move_to([lay["left_x"], lay["label_y"] + 0.30, 0]),
            opt_label("Wide Central\nFringe", HL_GREEN, size=25
                      ).move_to([lay["right_x"], lay["label_y"] + 0.30, 0]),
            opt_label("Twice the side width", "#C9D8F0", size=19
                      ).move_to([lay["right_x"], lay["label_y"] - 0.62, 0]),
        )
        self.add(old)

        # Intensity axes: I plotted against position on the screen.
        ax_l = intensity_axis(lay["left_x"], lay)
        ax_r = intensity_axis(lay["right_x"], lay)

        self.show_caption("Brightness Difference")                   # 0.55
        self.play(FadeOut(old, shift=DOWN * 0.20), run_time=0.60)    # 0.60
        self.play(LaggedStart(Create(ax_l), Create(ax_r), lag_ratio=0.30),
                  run_time=1.10)                                     # 1.10
        # A quick reminder that both screens are still in play.
        self.play(LaggedStart(
            Indicate(p["head_l"], scale_factor=1.05, color=WAVE_BLUE),
            Indicate(p["head_r"], scale_factor=1.05, color=WAVE_PURPLE),
            lag_ratio=0.35), run_time=1.00)                          # 1.00
        self.wait(2.25)                                              # 2.25
