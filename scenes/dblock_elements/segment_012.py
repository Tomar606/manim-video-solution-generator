# SCENE 5b — ns and (n-1)d sit at nearly the same energy.
class SegmentScene(ThemedScene):
    CAPTION_MODE = "narration"

    def construct(self):
        base_y = self.stage_center[1] - 0.95
        xs = (-1.25, 1.25)

        axis = Arrow([-2.45, base_y, 0], [-2.45, base_y + 3.05, 0], buff=0,
                     color="#5E7BA8", stroke_width=2.6,
                     max_tip_length_to_length_ratio=0.10)
        axis_tag = opt_label("Energy", "#8FA6C8", size=20)
        axis_tag.rotate(PI / 2).next_to(axis, LEFT, buff=0.14)

        # Start clearly apart, then converge — the whole point of the beat.
        h_ns, h_nd = 1.30, 2.55
        bar_ns = _rr(0.86, h_ns, 0.10, DB_BLUE, op=0.9)
        bar_ns.move_to([xs[0], base_y + h_ns / 2, 0])
        bar_nd = _rr(0.86, h_nd, 0.10, DB_PURPLE, op=0.9)
        bar_nd.move_to([xs[1], base_y + h_nd / 2, 0])

        t_ns = opt_label("ns", DB_BLUE, size=25, weight="SEMIBOLD")
        t_ns.move_to([xs[0], base_y - 0.34, 0])
        t_nd = opt_label("(n-1)d", DB_PURPLE, size=25, weight="SEMIBOLD")
        t_nd.move_to([xs[1], base_y - 0.34, 0])

        final_h = 2.00
        lvl = DashedVMobject(
            Line([xs[0] - 0.75, base_y + final_h, 0],
                 [xs[1] + 0.75, base_y + final_h, 0],
                 stroke_color=DB_ORANGE, stroke_width=2.6), num_dashes=24)
        lbl = chip("Nearly Same Energy", DB_ORANGE, size=25)
        lbl.move_to([0.0, base_y + final_h + 0.72, 0])

        self.show_caption("Kyunki inke n s aur n minus one d orbitals ki "
                          "energy lagbhag same hoti hai.")           # 0.55
        self.play(Create(axis), FadeIn(axis_tag), run_time=0.55)     # 0.55
        self.play(LaggedStart(FadeIn(bar_ns, shift=UP * 0.25),
                              FadeIn(bar_nd, shift=UP * 0.25),
                              lag_ratio=0.30), run_time=0.90)        # 0.90
        self.play(FadeIn(t_ns), FadeIn(t_nd), run_time=0.40)         # 0.40
        # Converge to almost the same level.
        n1 = _rr(0.86, final_h, 0.10, DB_BLUE, op=0.9)
        n1.move_to([xs[0], base_y + final_h / 2, 0])
        n2 = _rr(0.86, final_h - 0.16, 0.10, DB_PURPLE, op=0.9)
        n2.move_to([xs[1], base_y + (final_h - 0.16) / 2, 0])
        self.play(Transform(bar_ns, n1), Transform(bar_nd, n2),
                  run_time=1.15)                                     # 1.15
        self.play(Create(lvl), run_time=0.55)                        # 0.55
        self.play(FadeIn(lbl, shift=UP * 0.20), run_time=0.55)       # 0.55
        self.wait(0.80)                                              # 0.80
