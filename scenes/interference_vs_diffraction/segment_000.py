# SCENE 1 — HOOK. Split screen: superposing waves | light spreading through a slit.
class SegmentScene(ThemedScene):
    def construct(self):
        lay = compare_layout(self.stage_center, self.stage_w)
        HALF = lay["col_w"] / 2                 # column half-width (~1.67)
        wave_y = self.stage_center[1] + 0.68
        slit_y = self.stage_center[1] + 1.42
        label_y = self.stage_center[1] - 0.82
        wave_w = lay["col_w"] * 0.84

        # --- live wave trains (left): two crests sliding through each other --- #
        phase = ValueTracker(0.0)

        def wave_points(amp, ph0):
            pts = []
            for i in range(161):
                x = -wave_w / 2 + wave_w * i / 160
                y = amp * np.sin(2 * PI * 2.0 * x / wave_w + phase.get_value() + ph0)
                pts.append([lay["left_x"] + x, wave_y + y, 0.0])
            return pts

        def make_wave(color, ph0, amp):
            m = _polyline(wave_points(amp, ph0), color, 3.2)
            m.add_updater(
                lambda mob, ph0=ph0, amp=amp:
                mob.set_points_as_corners(wave_points(amp, ph0))
            )
            return m

        # --- live circular wavefronts (right): crests marching outward -------- #
        travel = ValueTracker(0.0)
        slit_pt = np.array([lay["right_x"], slit_y, 0.0])
        SPACING, N_FRONTS = 0.26, 5
        REACH = SPACING * N_FRONTS              # 1.30 — stays inside the column

        def fronts_group():
            g = VGroup()
            for i in range(N_FRONTS):
                r = 0.14 + ((travel.get_value() + i * SPACING) % REACH)
                op = float(np.clip(0.95 - (r - 0.14) / REACH * 0.80, 0.12, 0.95))
                g.add(Arc(radius=r, start_angle=PI, angle=PI, arc_center=slit_pt,
                          stroke_color=WAVE_PURPLE, stroke_width=2.8,
                          stroke_opacity=op))
            return g

        barrier = slit_barrier(lay["col_w"] * 0.94, [(lay["right_x"], 0.20)],
                               thickness=0.16, y=slit_y, center_x=lay["right_x"])
        feed = plane_wavefronts(lay["col_w"] * 0.74, n=2, y_top=slit_y + 0.56,
                                dy=0.28, color=WAVE_PURPLE, stroke_width=2.4,
                                center_x=lay["right_x"])

        divider = divider_line(lay["divider_x"], slit_y + 0.80, label_y - 0.62)

        lbl_l = opt_label("Interference", "#DCE8FF", size=30, weight="SEMIBOLD")
        lbl_l.move_to([lay["left_x"], label_y, 0])
        lbl_r = opt_label("Diffraction", "#DCE8FF", size=30, weight="SEMIBOLD")
        lbl_r.move_to([lay["right_x"], label_y, 0])
        _ = HALF

        # --- build ----------------------------------------------------------- #
        self.show_caption("Interference vs Diffraction")             # 0.55
        self.play(Create(divider), run_time=0.45)                    # 0.45

        w_a = make_wave(WAVE_BLUE, 0.0, 0.40)
        w_b = make_wave(WAVE_PURPLE, PI * 0.62, 0.40)
        static_fronts = fronts_group()
        self.play(
            LaggedStart(Create(w_a), Create(w_b), lag_ratio=0.30),
            LaggedStart(FadeIn(feed, shift=DOWN * 0.15), Create(barrier),
                        lag_ratio=0.35),
            run_time=1.30,
        )                                                            # 1.30
        self.play(LaggedStart(*[Create(a) for a in static_fronts],
                              lag_ratio=0.16), run_time=0.95)        # 0.95
        self.remove(static_fronts)
        self.add(always_redraw(fronts_group))

        self.play(FadeIn(lbl_l, shift=UP * 0.25), FadeIn(lbl_r, shift=UP * 0.25),
                  phase.animate.set_value(PI * 1.2),
                  travel.animate.set_value(0.45),
                  run_time=0.85)                                     # 0.85
        # Hold with both sides alive — never a static frame under narration.
        self.play(phase.animate.set_value(PI * 6.0),
                  travel.animate.set_value(3.0),
                  rate_func=linear, run_time=2.85)                   # 2.85
