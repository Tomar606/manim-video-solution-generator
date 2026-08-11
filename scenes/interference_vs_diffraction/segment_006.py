# SCENE 5c — the diffraction pattern fills the RIGHT screen: central maximum
# exactly twice as wide as the side maxima, which then narrow outward.
class SegmentScene(ThemedScene):
    def construct(self):
        lay, p = compare_base(self.stage_center, self.stage_w)
        base = VGroup(p["divider"], p["head_l"], p["head_r"],
                      p["plate_l"], p["plate_r"], p["cap_r"])
        self.add(base)
        self.caption_mob = caption_pill("Fringe Pattern")
        self.add(self.caption_mob)

        # Left side stays on screen, exactly as segment 5 left it.
        N = 9
        _, l_bands = interference_pattern(lay["plate_w"], lay["plate_h"] * 0.86,
                                          n_bright=N)
        l_bands.move_to([lay["left_x"], lay["plate_y"], 0])
        period = lay["plate_w"] / (N + 0.4)
        half = (N - 1) / 2.0
        bracket_y = lay["plate_y"] - lay["plate_h"] / 2 - 0.34
        l_brackets = VGroup(
            measure_bracket(lay["left_x"] + (0 - half) * period,
                            lay["left_x"] + (1 - half) * period, bracket_y),
            measure_bracket(lay["left_x"] + (3 - half) * period,
                            lay["left_x"] + (4 - half) * period, bracket_y),
        )
        l_lbl = opt_label("Equal Fringe\nWidth", HL_ORANGE, size=25)
        l_lbl.move_to([lay["left_x"], lay["label_y"] + 0.30, 0])
        self.add(l_bands, l_brackets, l_lbl)

        _, r_bands = diffraction_pattern(lay["plate_w"] * 0.94,
                                         lay["plate_h"] * 0.86)
        r_bands.move_to([lay["right_x"], lay["plate_y"], 0])

        # The central maximum spans β ∈ (−π, π); each side maximum spans π, so
        # measuring them side by side makes the exact 2:1 ratio explicit.
        unit = lay["plate_w"] * 0.94 / 8.0
        b_centre = measure_bracket(lay["right_x"] - unit, lay["right_x"] + unit,
                                   bracket_y, color=HL_GREEN)
        b_side = measure_bracket(lay["right_x"] + unit, lay["right_x"] + 2 * unit,
                                 bracket_y, color=HL_ORANGE)

        r_lbl = opt_label("Wide Central\nFringe", HL_GREEN, size=25)
        r_lbl.move_to([lay["right_x"], lay["label_y"] + 0.30, 0])
        r_sub = opt_label("Twice the side width", "#C9D8F0", size=19)
        r_sub.move_to([lay["right_x"], lay["label_y"] - 0.62, 0])

        self.play(FadeOut(p["cap_r"]), run_time=0.30)                # 0.30
        self.play(LaggedStart(*[FadeIn(b, scale=0.86) for b in r_bands],
                              lag_ratio=0.13), run_time=2.10)        # 2.10
        self.play(Create(b_centre), run_time=0.65)                   # 0.65
        self.play(Create(b_side), run_time=0.55)                     # 0.55
        self.play(FadeIn(r_lbl, shift=UP * 0.20), run_time=0.55)     # 0.55
        self.play(FadeIn(r_sub, shift=UP * 0.18), run_time=0.50)     # 0.50
        self.wait(3.35)                                              # 3.35
