# SCENE 3b — because the d-orbital is only PARTIALLY filled.
class SegmentScene(ThemedScene):
    CAPTION_MODE = "narration"

    def construct(self):
        head = chip("Transition Elements", DB_GREEN, size=27)
        head.move_to(self.stage_center + UP * 2.05)

        boxes, arrows = orbital_boxes(5, [0, 1, 2], width=0.52, gap=0.11,
                                      color=DB_ORANGE)
        boxes.move_to(self.stage_center + UP * 0.60)
        arrows.move_to(self.stage_center + UP * 0.60)

        # Glow only the occupied boxes — that is what "partially filled" means.
        glow = VGroup(*[
            RoundedRectangle(width=0.62, height=0.56, corner_radius=0.07,
                             stroke_width=0, fill_color=DB_ORANGE,
                             fill_opacity=0.26).move_to(boxes[i].get_center())
            for i in (0, 1, 2)])

        lbl = chip("Partially Filled d-Orbital", DB_ORANGE, size=25)
        lbl.next_to(boxes, DOWN, buff=0.62)

        self.show_caption("Kyunki inke atom ya kisi oxidation state mein "
                          "d-orbital partially filled hota hai.")    # 0.55
        self.add(head)
        self.play(Create(boxes), run_time=0.80)                      # 0.80
        self.play(LaggedStart(*[FadeIn(a, scale=0.7) for a in arrows],
                              lag_ratio=0.22), run_time=0.90)        # 0.90
        self.play(FadeIn(glow), run_time=0.50)                       # 0.50
        self.play(LaggedStart(*[Indicate(g, scale_factor=1.18,
                                         color=DB_ORANGE) for g in glow],
                              lag_ratio=0.18), run_time=0.85)        # 0.85
        self.play(FadeIn(lbl, shift=UP * 0.20), run_time=0.55)       # 0.55
        self.wait(0.85)                                              # 0.85
