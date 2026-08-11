# SCENE 7 — "Quick Comparison". The whole video collapsed into one table, built
# a row at a time. Portrait has no room for a left label column, so each row is
# introduced by a centred tag with its two values beneath.
class SegmentScene(ThemedScene):
    def construct(self):
        lay = compare_layout(self.stage_center, self.stage_w)
        LX, RX = lay["left_x"], lay["right_x"]
        SPAN = self.stage_w / 2 - 0.10

        head_l = chip("Interference", WAVE_BLUE, size=25).move_to([LX, 4.55, 0])
        head_r = chip("Diffraction", WAVE_PURPLE, size=25).move_to([RX, 4.55, 0])
        rule = Line([-SPAN, 4.12, 0], [SPAN, 4.12, 0],
                    stroke_color="#3C5C8C", stroke_width=2.2, stroke_opacity=0.75)

        rows = [
            ("Formation", "Two Coherent\nSources", "Single Slit\nor Obstacle"),
            ("Pattern", "Equal\nFringes", "Wide Central\nFringe"),
            ("Brightness", "Almost\nSame", "Central\nBrightest"),
        ]
        tag_ys = [3.72, 2.32, 0.92]
        val_ys = [3.12, 1.72, 0.32]
        sep_ys = [2.70, 1.30, -0.10]

        built = []
        for (name, a, b), ty, vy, sy in zip(rows, tag_ys, val_ys, sep_ys):
            tag = chip(name, HL_ORANGE, size=21, pad_x=0.26, pad_y=0.13)
            tag.move_to([0.0, ty, 0])
            cell_a = opt_label(a, "#FFFFFF", size=22).move_to([LX, vy, 0])
            cell_b = opt_label(b, "#FFFFFF", size=22).move_to([RX, vy, 0])
            sep = Line([-SPAN, sy, 0], [SPAN, sy, 0], stroke_color="#2A4C7E",
                       stroke_width=1.6, stroke_opacity=0.55)
            built.append(VGroup(tag, cell_a, cell_b, sep))

        v_rule = DashedVMobject(
            Line([0.0, 4.12, 0], [0.0, sep_ys[-1], 0], stroke_color="#2A4C7E",
                 stroke_width=1.6, stroke_opacity=0.55), num_dashes=22)

        self.show_caption("Quick Comparison")                        # 0.55
        self.play(FadeIn(head_l, shift=DOWN * 0.20),
                  FadeIn(head_r, shift=DOWN * 0.20),
                  Create(rule), run_time=0.80)                       # 0.80
        self.play(Create(v_rule), run_time=0.40)                     # 0.40
        for row in built:                                            # 3 x 1.15
            self.play(LaggedStart(
                FadeIn(row[0], shift=DOWN * 0.16),
                AnimationGroup(FadeIn(row[1], shift=RIGHT * 0.24),
                               FadeIn(row[2], shift=LEFT * 0.24)),
                Create(row[3]), lag_ratio=0.35), run_time=1.15)
        self.wait(1.80)                                              # 1.80
