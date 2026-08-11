# SCENE 4 — DIFFRACTION. ONE narrow slit. Plane wavefronts in, semicircular
# wavefronts out: light bends round the slit edges and spreads.
class SegmentScene(ThemedScene):
    def construct(self):
        SRC_Y, BAR_Y, SCR_Y = 4.86, 3.55, -0.30
        HALF = 3.45
        SLIT_W = 0.22
        slit_pt = np.array([0.0, BAR_Y, 0.0])

        # Incoming plane wave — a distant source, so the crests arrive flat.
        feed = plane_wavefronts(HALF * 1.20, n=3, y_top=SRC_Y, dy=0.36,
                                color=WAVE_BLUE, stroke_width=2.6)
        feed_arrow = Arrow([2.72, SRC_Y + 0.04, 0], [2.72, BAR_Y + 0.28, 0],
                           buff=0, color=WAVE_BLUE, stroke_width=4.0,
                           max_tip_length_to_length_ratio=0.22)

        barrier = slit_barrier(HALF * 2, [(0.0, SLIT_W)], thickness=0.22, y=BAR_Y)
        lbl_slit = chip("Single Narrow Slit", HL_ORANGE, size=23)
        lbl_slit.move_to([0.0, BAR_Y - 0.66, 0])

        # Huygens: every point of the slit is a new source, so beyond the slit
        # the crests are semicircular — the wave bends into the geometric shadow.
        fronts = circular_wavefronts(slit_pt, n=9, r0=0.72, dr=0.42,
                                     color=WAVE_PURPLE, stroke_width=2.5)

        # Edges of the geometric shadow vs. where light actually reaches.
        spread = VGroup()
        for sgn in (-1, 1):
            spread.add(DashedVMobject(
                Line(slit_pt, [sgn * 3.05, SCR_Y - 0.05, 0],
                     stroke_color=HL_ORANGE, stroke_width=2.4,
                     stroke_opacity=0.85),
                num_dashes=20))
        geom = VGroup(*[
            DashedVMobject(Line([sgn * SLIT_W / 2, BAR_Y, 0],
                                [sgn * SLIT_W / 2, SCR_Y, 0],
                                stroke_color="#7F8CA6", stroke_width=2.0,
                                stroke_opacity=0.7), num_dashes=16)
            for sgn in (-1, 1)])
        lbl_spread = chip("Light Spreads", HL_GREEN, size=23)
        lbl_spread.move_to([0.0, SCR_Y + 1.15, 0])

        screen = screen_plate(HALF * 2, 0.62).move_to([0, SCR_Y, 0])
        plate, bands = diffraction_pattern(HALF * 2 * 0.97, 0.54)
        bands.move_to([0, SCR_Y, 0])
        lbl_screen = opt_label("Screen", "#9FB6D8", size=20)
        lbl_screen.move_to([0.0, SCR_Y - 0.60, 0])

        setup = VGroup(feed, feed_arrow, barrier, lbl_slit, fronts,
                       spread, geom, lbl_spread, screen, bands, lbl_screen)

        # --- build ----------------------------------------------------------- #
        self.show_caption("Diffraction")                              # 0.55
        self.play(FadeIn(feed, shift=DOWN * 0.25),
                  GrowArrow(feed_arrow), run_time=0.80)               # 0.80
        self.play(Create(barrier), run_time=0.65)                     # 0.65
        self.play(FadeIn(lbl_slit, shift=UP * 0.18), run_time=0.50)   # 0.50
        # The wave bends out of the slit.
        self.play(LaggedStart(*[Create(a) for a in fronts], lag_ratio=0.11),
                  run_time=1.85)                                      # 1.85
        self.play(Create(geom), run_time=0.45)                        # 0.45
        self.play(LaggedStart(*[Create(s) for s in spread], lag_ratio=0.25),
                  FadeIn(lbl_spread, shift=UP * 0.18), run_time=0.85) # 0.85
        # The spread is the one beat that genuinely needs more vertical room, so
        # the diagram opens into the wide area — then settles back before the cut.
        self.play(setup.animate.scale(1.11, about_point=self.stage_center)
                  .shift(DOWN * 0.32), run_time=0.55)                 # 0.55
        self.play(FadeIn(screen, shift=UP * 0.15), FadeIn(lbl_screen),
                  run_time=0.45)                                      # 0.45
        self.play(LaggedStart(*[FadeIn(b, scale=0.85) for b in bands],
                              lag_ratio=0.13), run_time=1.15)         # 1.15
        self.wait(0.65)                                               # 0.65
        self.play(setup.animate.shift(UP * 0.32)
                  .scale(1 / 1.11, about_point=self.stage_center),
                  run_time=0.55)                                      # 0.55
        _ = plate
