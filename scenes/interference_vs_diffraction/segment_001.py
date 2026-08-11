# SCENE 2 — "Kab Hote Hain?" Establishes LEFT = Interference, RIGHT = Diffraction.
class SegmentScene(ThemedScene):
    def construct(self):
        lay = compare_layout(self.stage_center, self.stage_w)
        emit_y = self.stage_center[1] + 1.42     # source / slit line
        label_y = self.stage_center[1] - 0.52
        sub_y = self.stage_center[1] - 1.52

        divider = divider_line(lay["divider_x"], lay["header_y"] - 0.55,
                               sub_y - 0.50)

        head_l = chip("Interference", WAVE_BLUE, size=28)
        head_l.move_to([lay["left_x"], lay["header_y"], 0])
        head_r = chip("Diffraction", WAVE_PURPLE, size=28)
        head_r.move_to([lay["right_x"], lay["header_y"], 0])

        # LEFT — two coherent sources whose wavefronts overlap.
        s1 = np.array([lay["left_x"] - 0.32, emit_y, 0.0])
        s2 = np.array([lay["left_x"] + 0.32, emit_y, 0.0])
        icon_l = VGroup(
            circular_wavefronts(s1, n=5, r0=0.24, dr=0.27, color=WAVE_BLUE,
                                stroke_width=2.4),
            circular_wavefronts(s2, n=5, r0=0.24, dr=0.27, color=WAVE_PURPLE,
                                stroke_width=2.4),
            Dot(s1, radius=0.085, color=FRINGE_YELLOW),
            Dot(s2, radius=0.085, color=FRINGE_YELLOW),
        )

        # RIGHT — one narrow slit, light spreading past it.
        slit_pt = np.array([lay["right_x"], emit_y, 0.0])
        icon_r = VGroup(
            plane_wavefronts(lay["col_w"] * 0.70, n=2, y_top=emit_y + 0.54,
                             dy=0.27, color=WAVE_PURPLE, stroke_width=2.4,
                             center_x=lay["right_x"]),
            slit_barrier(lay["col_w"] * 0.94, [(lay["right_x"], 0.20)],
                         thickness=0.17, y=emit_y, center_x=lay["right_x"]),
            circular_wavefronts(slit_pt, n=5, r0=0.24, dr=0.27,
                                color=WAVE_PURPLE, stroke_width=2.4),
        )

        cond_l = opt_label("Do Coherent\nSources", "#FFFFFF", size=27)
        cond_l.move_to([lay["left_x"], label_y, 0])
        cond_r = opt_label("Ek Narrow\nSlit", "#FFFFFF", size=27)
        cond_r.move_to([lay["right_x"], label_y, 0])

        sub_l = opt_label("Waves Superpose", WAVE_BLUE, size=21)
        sub_l.move_to([lay["left_x"], sub_y, 0])
        sub_r = opt_label("Light Spreads", WAVE_PURPLE, size=21)
        sub_r.move_to([lay["right_x"], sub_y, 0])

        self.show_caption("Kab Hote Hain?")                          # 0.55
        self.play(Create(divider), run_time=0.40)                    # 0.40
        self.play(FadeIn(head_l, shift=DOWN * 0.20),
                  FadeIn(head_r, shift=DOWN * 0.20), run_time=0.55)  # 0.55
        self.play(LaggedStart(Create(icon_l), Create(icon_r), lag_ratio=0.28),
                  run_time=1.50)                                     # 1.50
        self.play(LaggedStart(
            AnimationGroup(FadeIn(cond_l, shift=UP * 0.22),
                           FadeIn(cond_r, shift=UP * 0.22)),
            AnimationGroup(FadeIn(sub_l, shift=UP * 0.18),
                           FadeIn(sub_r, shift=UP * 0.18)),
            lag_ratio=0.45), run_time=1.00)                          # 1.00
        self.wait(0.50)                                              # 0.50
