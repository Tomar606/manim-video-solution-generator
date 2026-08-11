# SCENE 4a — metal cations held in a sea of delocalised electrons.
class SegmentScene(ThemedScene):
    CAPTION_MODE = "narration"

    def construct(self):
        ions, electrons = electron_sea(nx=4, ny=3, spacing=0.70)
        sea = VGroup(ions, electrons)
        sea.move_to(self.stage_center + UP * 0.85)

        halo = RoundedRectangle(width=sea.width + 0.55, height=sea.height + 0.45,
                                corner_radius=0.24, stroke_width=2.0,
                                stroke_color=DB_BLUE, stroke_opacity=0.55,
                                fill_color=DB_BLUE, fill_opacity=0.08)
        halo.move_to(sea.get_center())

        lbl = chip("Strong Metallic Bonding", DB_ORANGE, size=26)
        lbl.next_to(halo, DOWN, buff=0.55)

        self.show_caption("Inke atoms ke beech metallic bonding kaafi "
                          "strong hoti hai.")                        # 0.55
        self.play(FadeIn(halo), LaggedStart(
            *[FadeIn(i, scale=0.7) for i in ions], lag_ratio=0.05),
            run_time=1.10)                                           # 1.10
        self.play(LaggedStart(*[FadeIn(e, scale=0.4) for e in electrons],
                              lag_ratio=0.025), run_time=0.85)       # 0.85
        # The lattice pulls tight — the bonding is strong.
        self.play(ions.animate.scale(0.94, about_point=sea.get_center()),
                  electrons.animate.scale(0.94, about_point=sea.get_center()),
                  run_time=0.55)                                     # 0.55
        self.play(FadeIn(lbl, shift=UP * 0.20), run_time=0.50)       # 0.50
        self.wait(0.45)                                              # 0.45
