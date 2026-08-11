# SCENE 3 — INTERFERENCE. Young's double-slit, built bottom-of-chain upward:
# source -> barrier -> two coherent slits -> overlapping wavefronts -> screen.
class SegmentScene(ThemedScene):
    def construct(self):
        SRC_Y, BAR_Y, SCR_Y = 4.78, 3.78, -0.38
        D_SLIT, LAM = 1.50, 0.42          # slit separation, drawn wavelength
        HALF = 3.45                        # barrier / screen half-width
        D = BAR_Y - SCR_Y                  # slit-to-screen distance

        src = np.array([0.0, SRC_Y, 0.0])
        s1 = np.array([-D_SLIT / 2, BAR_Y, 0.0])
        s2 = np.array([D_SLIT / 2, BAR_Y, 0.0])

        source = point_source(src, radius=0.12)
        src_fronts = circular_wavefronts(src, n=3, r0=0.26, dr=0.30,
                                         color=WAVE_BLUE, stroke_width=2.4)
        lbl_src = chip("Light Source", "#DCE8FF", size=22)
        lbl_src.move_to([2.25, SRC_Y, 0])

        barrier = slit_barrier(HALF * 2, [(-D_SLIT / 2, 0.17), (D_SLIT / 2, 0.17)],
                               thickness=0.20, y=BAR_Y)
        dot1, dot2 = Dot(s1, radius=0.075, color=FRINGE_YELLOW), \
            Dot(s2, radius=0.075, color=FRINGE_YELLOW)
        lbl_slits = chip("Two Coherent Sources", HL_ORANGE, size=22)
        lbl_slits.move_to([0.0, BAR_Y - 0.62, 0])

        # First drawn crest starts a wavelength out, which keeps a clean band
        # under the barrier for the label without misrepresenting the physics.
        f1 = circular_wavefronts(s1, n=7, r0=0.78, dr=LAM, color=WAVE_BLUE,
                                 stroke_width=2.4)
        f2 = circular_wavefronts(s2, n=7, r0=0.78, dr=LAM, color=WAVE_PURPLE,
                                 stroke_width=2.4)

        screen = screen_plate(HALF * 2, 0.62).move_to([0, SCR_Y, 0])
        lbl_screen = opt_label("Screen", "#9FB6D8", size=20)
        lbl_screen.move_to([0.0, SCR_Y - 0.60, 0])

        xs = ydse_bright_positions(D_SLIT, D, LAM, HALF - 0.25)
        bands = VGroup(*[bright_band(x, 0.30, 0.54, 1.0, FRINGE_WHITE, SCR_Y)
                         for x in sorted(xs, key=abs)])

        # One dashed hyperbola per bright fringe: the exact locus of
        # constructive interference, landing on its band.
        antinodal = VGroup()
        for n in (0, 1, -1, 2, -2):
            curve = ydse_antinodal_curve(D_SLIT, LAM, n, BAR_Y, SCR_Y)
            if curve is not None:
                antinodal.add(curve)

        # --- build ----------------------------------------------------------- #
        self.show_caption("Interference")                             # 0.55
        self.play(FadeIn(source, scale=0.7), FadeIn(lbl_src, shift=LEFT * 0.2),
                  run_time=0.70)                                      # 0.70
        self.play(Create(src_fronts), run_time=0.65)                  # 0.65
        self.play(Create(barrier), run_time=0.70)                     # 0.70
        self.play(LaggedStart(FadeIn(dot1, scale=0.6), FadeIn(dot2, scale=0.6),
                              FadeIn(lbl_slits, shift=UP * 0.18),
                              lag_ratio=0.30), run_time=0.90)         # 0.90
        # The two wavefront families expand and overlap.
        self.play(LaggedStart(Create(f1), Create(f2), lag_ratio=0.22),
                  run_time=2.00)                                      # 2.00
        # Where crest meets crest, light reinforces — the antinodal hyperbolae.
        self.play(LaggedStart(*[Create(c) for c in antinodal], lag_ratio=0.14),
                  run_time=0.90)                                      # 0.90
        self.play(FadeIn(screen, shift=UP * 0.15),
                  FadeIn(lbl_screen), run_time=0.50)                  # 0.50
        self.play(LaggedStart(*[FadeIn(b, scale=0.85) for b in bands],
                              lag_ratio=0.16), run_time=1.20)         # 1.20
        self.wait(0.90)                                               # 0.90
