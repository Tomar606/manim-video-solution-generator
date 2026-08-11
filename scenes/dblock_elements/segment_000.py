# SCENE 1 — the periodic table builds, then everything but the d-block dims.
class SegmentScene(ThemedScene):
    CAPTION_MODE = "narration"

    def construct(self):
        table, cells = periodic_table(self.stage_w * 0.98)
        table.move_to(self.stage_center + UP * 0.55)
        d_cells = d_block_cells(cells)
        rest = other_cells(cells)

        glow = SurroundingRectangle(d_cells, color=DB_ORANGE, buff=0.07,
                                    stroke_width=3.0, corner_radius=0.08)
        tag = chip("d-Block Elements", DB_ORANGE, size=27)
        tag.next_to(table, DOWN, buff=0.52)

        self.show_caption(
            "Baccho, aaj Chemistry mein hum samjhenge d-block elements "
            "aur unki 2 sabse important characteristics, jo exam ke liye "
            "bahut zaroori hain.")                                   # 0.55
        self.play(LaggedStart(*[FadeIn(c, scale=0.7) for c in table],
                              lag_ratio=0.006), run_time=1.90)       # 1.90
        self.play(rest.animate.set_opacity(0.22),
                  d_cells.animate.set_fill(DB_BLUE, opacity=0.92),
                  run_time=0.95)                                     # 0.95
        self.play(Create(glow), run_time=0.70)                       # 0.70
        self.play(LaggedStart(*[Indicate(c, scale_factor=1.10, color=DB_ORANGE)
                                for c in d_cells], lag_ratio=0.018),
                  run_time=1.20)                                     # 1.20
        self.play(FadeIn(tag, shift=UP * 0.22), run_time=0.60)       # 0.60
        self.wait(1.10)                                              # 1.10
