# SCENE 2 — orbitals fill s, then p, then d. The LAST electron enters d.
class SegmentScene(ThemedScene):
    CAPTION_MODE = "narration"

    def construct(self):
        rows_y = [3.55, 2.62, 1.69]
        X_START = -0.62          # every row's first box starts here
        BW = 0.46

        def make_row(n, y, name, color, filled, paired=None):
            boxes, arrows = orbital_boxes(n, filled, width=BW, gap=0.09,
                                          color=color, paired=paired)
            row = VGroup(boxes, arrows) if len(arrows) else VGroup(boxes)
            row.move_to([0, y, 0])
            row.align_to(np.array([X_START, 0, 0]), LEFT)
            tag = opt_label(name, color, size=28, weight="SEMIBOLD")
            tag.move_to([X_START - 0.52, y, 0])
            return boxes, arrows, tag

        s_b, s_a, s_t = make_row(1, rows_y[0], "s", DB_GREEN, [0], [0])
        p_b, p_a, p_t = make_row(3, rows_y[1], "p", DB_PURPLE, [0, 1, 2],
                                 [0, 1, 2])
        d_b, d_a, d_t = make_row(5, rows_y[2], "d", DB_ORANGE, [])

        # The final electron lands in the first d box.
        slot = d_b[0].get_center()
        last = Arrow(slot + DOWN * 0.15, slot + UP * 0.15, buff=0,
                     color="#FFFFFF", stroke_width=3.2,
                     max_tip_length_to_length_ratio=0.34)
        halo = Circle(radius=0.36, stroke_width=0, fill_color=DB_ORANGE,
                      fill_opacity=0.32).move_to(slot)

        c1 = chip("Last Electron", "#FFFFFF", size=26)
        c1.move_to([0.0, 0.62, 0])
        arr = flow_arrow(0.46, color=DB_ORANGE).next_to(c1, DOWN, buff=0.18)
        c2 = chip("d-Orbital", DB_ORANGE, size=26)
        c2.next_to(arr, DOWN, buff=0.18)

        self.show_caption("Jin elements ka last electron d-orbital mein "
                          "hota hai, unhe d-block elements kehte hain.")
        self.play(LaggedStart(
            AnimationGroup(FadeIn(s_t), Create(s_b), FadeIn(s_a)),
            AnimationGroup(FadeIn(p_t), Create(p_b), FadeIn(p_a)),
            AnimationGroup(FadeIn(d_t), Create(d_b)),
            lag_ratio=0.42), run_time=2.05)                          # 2.05
        self.play(FadeIn(halo, scale=0.5), GrowArrow(last),
                  run_time=0.65)                                     # 0.65
        self.play(Indicate(halo, scale_factor=1.30, color=DB_ORANGE),
                  run_time=0.50)                                     # 0.50
        self.play(FadeIn(c1, shift=UP * 0.18), run_time=0.40)        # 0.40
        self.play(GrowArrow(arr), run_time=0.30)                     # 0.30
        self.play(FadeIn(c2, shift=UP * 0.18), run_time=0.40)        # 0.40
        self.wait(0.65)                                              # 0.65
