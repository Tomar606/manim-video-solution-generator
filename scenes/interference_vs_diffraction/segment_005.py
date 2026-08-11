# SCENE 5b — the interference pattern fills the LEFT screen: 9 fringes of equal
# width, equal spacing, equal brightness.
class SegmentScene(ThemedScene):
    def construct(self):
        lay, p = compare_base(self.stage_center, self.stage_w)
        base = VGroup(p["divider"], p["head_l"], p["head_r"],
                      p["plate_l"], p["plate_r"], p["cap_l"], p["cap_r"])
        self.add(base)
        self.caption_mob = caption_pill("Fringe Pattern")
        self.add(self.caption_mob)

        N = 9
        _, bands = interference_pattern(lay["plate_w"], lay["plate_h"] * 0.86,
                                        n_bright=N)
        bands.move_to([lay["left_x"], lay["plate_y"], 0])

        # Two adjacent fringes measured against each other — the spacing is the
        # same wherever you look, which is what "equal fringe width" means.
        period = lay["plate_w"] / (N + 0.4)
        half = (N - 1) / 2.0
        bracket_y = lay["plate_y"] - lay["plate_h"] / 2 - 0.34
        b1 = measure_bracket(lay["left_x"] + (0 - half) * period,
                             lay["left_x"] + (1 - half) * period, bracket_y)
        b2 = measure_bracket(lay["left_x"] + (3 - half) * period,
                             lay["left_x"] + (4 - half) * period, bracket_y)

        lbl = opt_label("Equal Fringe\nWidth", HL_ORANGE, size=25)
        lbl.move_to([lay["left_x"], lay["label_y"] + 0.30, 0])

        self.play(FadeOut(p["cap_l"]), run_time=0.30)                # 0.30
        # Fringes bloom outward from the central maximum.
        self.play(LaggedStart(*[FadeIn(b, scale=0.86) for b in bands],
                              lag_ratio=0.10), run_time=1.70)        # 1.70
        self.play(LaggedStart(Create(b1), Create(b2), lag_ratio=0.35),
                  run_time=0.90)                                     # 0.90
        self.play(FadeIn(lbl, shift=UP * 0.20), run_time=0.55)       # 0.55
        self.wait(1.55)                                              # 1.55
