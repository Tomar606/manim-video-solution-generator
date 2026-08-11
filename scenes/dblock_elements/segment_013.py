# SCENE 5c — electrons from BOTH orbitals go into bonding.
class SegmentScene(ThemedScene):
    CAPTION_MODE = "narration"

    def construct(self):
        base_y = self.stage_center[1] - 0.95
        xs = (-1.25, 1.25)
        final_h = 2.00

        bar_ns = _rr(0.86, final_h, 0.10, DB_BLUE, op=0.9)
        bar_ns.move_to([xs[0], base_y + final_h / 2, 0])
        bar_nd = _rr(0.86, final_h - 0.16, 0.10, DB_PURPLE, op=0.9)
        bar_nd.move_to([xs[1], base_y + (final_h - 0.16) / 2, 0])
        t_ns = opt_label("ns", DB_BLUE, size=25, weight="SEMIBOLD")
        t_ns.move_to([xs[0], base_y - 0.34, 0])
        t_nd = opt_label("(n-1)d", DB_PURPLE, size=25, weight="SEMIBOLD")
        t_nd.move_to([xs[1], base_y - 0.34, 0])
        self.add(bar_ns, bar_nd, t_ns, t_nd)
        self.caption_mob = self.make_caption(
            "Kyunki inke n s aur n minus one d orbitals ki energy "
            "lagbhag same hoti hai.")
        self.add(self.caption_mob)

        target = chip("Bonding", DB_GREEN, size=26)
        target.move_to([0.0, base_y + 3.10, 0])

        e_left = VGroup(*[Dot([xs[0] - 0.18 + i * 0.36,
                               base_y + final_h - 0.28, 0],
                              radius=0.075, color=FRINGE_YELLOW)
                          for i in range(2)])
        e_right = VGroup(*[Dot([xs[1] - 0.18 + i * 0.36,
                                base_y + final_h - 0.44, 0],
                               radius=0.075, color=FRINGE_YELLOW)
                           for i in range(2)])

        self.show_caption("Isliye dono orbitals ke electrons bonding mein "
                          "participate kar sakte hain.")             # 0.55
        self.play(FadeIn(e_left, scale=0.5), FadeIn(e_right, scale=0.5),
                  run_time=0.55)                                     # 0.55
        self.play(FadeIn(target, shift=DOWN * 0.20), run_time=0.45)  # 0.45
        # Both sets of electrons travel up into the bond.
        self.play(LaggedStart(
            *[e.animate.move_to(target.get_center() + DOWN * 0.44
                                + RIGHT * (0.28 * (k - 1.5)))
              for k, e in enumerate([*e_left, *e_right])],
            lag_ratio=0.16), run_time=1.30)                          # 1.30
        self.play(Indicate(target, scale_factor=1.08, color=DB_GREEN),
                  run_time=0.60)                                     # 0.60
        self.wait(0.55)                                              # 0.55
