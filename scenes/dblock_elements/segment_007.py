# SCENE 4b — hard, ductile, malleable. Icons, not paragraphs.
class SegmentScene(ThemedScene):
    CAPTION_MODE = "narration"

    def construct(self):
        xs = [-2.20, 0.0, 2.20]
        icon_y = self.stage_center[1] + 0.95
        lbl_y = icon_y - 1.70

        specs = [
            (icon_hammer(), "Hard", DB_ORANGE),
            (icon_wire(), "Ductile", DB_GREEN),
            (icon_sheet(), "Malleable", DB_BLUE),
        ]
        items = []
        for x, (icon, name, color) in zip(xs, specs):
            icon.scale(1.70).move_to([x, icon_y, 0])
            tag = chip(name, color, size=24)
            tag.move_to([x, lbl_y, 0])
            arr = flow_arrow(0.34, color=color)
            arr.move_to([x, (icon_y + lbl_y) / 2 - 0.02, 0])
            items.append(VGroup(icon, arr, tag))

        self.show_caption("Isi wajah se ye hard, ductile aur malleable "
                          "hote hain.")                              # 0.55
        for it in items:                                             # 3 x 0.92
            self.play(LaggedStart(FadeIn(it[0], scale=0.7),
                                  GrowArrow(it[1]),
                                  FadeIn(it[2], shift=UP * 0.18),
                                  lag_ratio=0.45), run_time=0.92)
        self.wait(0.69)                                              # 0.69
