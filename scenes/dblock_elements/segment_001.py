# BRIDGE — the d-block lifts out of the table and hands over to the definition.
class SegmentScene(ThemedScene):
    CAPTION_MODE = "narration"

    def construct(self):
        table, cells = periodic_table(self.stage_w * 0.98)
        table.move_to(self.stage_center + UP * 0.55)
        d_cells = d_block_cells(cells)
        rest = other_cells(cells)
        rest.set_opacity(0.22)
        d_cells.set_fill(DB_BLUE, opacity=0.92)
        glow = SurroundingRectangle(d_cells, color=DB_ORANGE, buff=0.07,
                                    stroke_width=3.0)
        tag = chip("d-Block Elements", DB_ORANGE, size=27)
        tag.next_to(table, DOWN, buff=0.52)
        self.add(table, glow, tag)
        self.caption_mob = self.make_caption(
            "Baccho, aaj Chemistry mein hum samjhenge d-block elements "
            "aur unki 2 sabse important characteristics, jo exam ke liye "
            "bahut zaroori hain.")
        self.add(self.caption_mob)

        target = chip("d-Block Elements", DB_ORANGE, size=30)
        target.move_to(self.stage_center + UP * 1.15)
        arrow = flow_arrow(0.58).next_to(target, DOWN, buff=0.28)
        question = chip("Definition", DB_BLUE, size=27)
        question.next_to(arrow, DOWN, buff=0.28)

        self.show_caption("Sabse pehle definition samajhte hain.")   # 0.55
        self.play(FadeOut(table, shift=UP * 0.25), FadeOut(glow),
                  ReplacementTransform(tag, target), run_time=0.85)  # 0.85
        self.play(GrowArrow(arrow), run_time=0.40)                   # 0.40
        self.play(FadeIn(question, shift=UP * 0.20), run_time=0.45)  # 0.45
        self.wait(0.25)                                              # 0.25
