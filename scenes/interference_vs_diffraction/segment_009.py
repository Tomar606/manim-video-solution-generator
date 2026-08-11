# SCENE 6c — RIGHT. The sinc² curve draws: a towering central peak and side
# peaks that collapse to a few percent of it.
class SegmentScene(ThemedScene):
    def construct(self):
        lay, p = compare_base(self.stage_center, self.stage_w)
        l_bands, r_bands = fringe_bands(lay)
        self.add(p["divider"], p["head_l"], p["head_r"],
                 p["plate_l"], p["plate_r"], l_bands, r_bands,
                 intensity_axis(lay["left_x"], lay),
                 intensity_axis(lay["right_x"], lay))
        self.caption_mob = caption_pill("Brightness Difference")
        self.add(self.caption_mob)

        l_curve = interference_intensity_curve(
            lay["plate_w"], lay["curve_h"], n_bright=N_INTERFERENCE_FRINGES,
            color=WAVE_BLUE)
        l_curve.shift([lay["left_x"], lay["curve_y"], 0])
        l_lbl = opt_label("Nearly Same\nIntensity", HL_ORANGE, size=25)
        l_lbl.move_to([lay["left_x"], lay["label_y"] - 0.62, 0])
        self.add(l_curve, l_lbl)

        curve = diffraction_intensity_curve(lay["plate_w"] * DIFF_PLATE_FRAC,
                                            lay["curve_h"], color=WAVE_PURPLE)
        curve.shift([lay["right_x"], lay["curve_y"], 0])

        centre = r_bands[0]
        sides = VGroup(*r_bands[1:])

        lbl = opt_label("Central Fringe\nBrightest", HL_GREEN, size=25)
        lbl.move_to([lay["right_x"], lay["label_y"] - 0.62, 0])

        # The central maximum blazes; the side maxima visibly give way.
        self.play(Indicate(centre, scale_factor=1.06, color=WHITE),
                  run_time=0.85)                                     # 0.85
        self.play(Create(curve), run_time=1.90)                      # 1.90
        self.play(LaggedStart(*[FadeToColor(b, "#8FA6C8") for b in sides],
                              lag_ratio=0.10), run_time=1.00)        # 1.00
        self.play(LaggedStart(*[FadeToColor(b, FRINGE_WHITE) for b in sides],
                              lag_ratio=0.10), run_time=0.80)        # 0.80
        self.play(FadeIn(lbl, shift=UP * 0.20), run_time=0.55)       # 0.55
        self.wait(3.40)                                              # 3.40
