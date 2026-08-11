# SCENE 6b — LEFT. The cos² intensity curve draws: every maximum reaches the
# same height, so all the bright fringes are equally bright.
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

        curve = interference_intensity_curve(
            lay["plate_w"], lay["curve_h"], n_bright=N_INTERFERENCE_FRINGES,
            color=WAVE_BLUE)
        curve.shift([lay["left_x"], lay["curve_y"], 0])

        lbl = opt_label("Nearly Same\nIntensity", HL_ORANGE, size=25)
        lbl.move_to([lay["left_x"], lay["label_y"] - 0.62, 0])

        # Pulse the fringes together — equal brightness, seen not just stated.
        self.play(LaggedStart(*[Indicate(b, scale_factor=1.04, color=WHITE)
                                for b in l_bands], lag_ratio=0.045),
                  run_time=1.30)                                     # 1.30
        self.play(Create(curve), run_time=1.60)                      # 1.60
        self.play(FadeIn(lbl, shift=UP * 0.20), run_time=0.55)       # 0.55
        self.wait(1.55)                                              # 1.55
