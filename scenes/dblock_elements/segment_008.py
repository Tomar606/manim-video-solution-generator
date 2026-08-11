# SCENE 4c — high melting and boiling points.
class SegmentScene(ThemedScene):
    CAPTION_MODE = "narration"

    def construct(self):
        xs = [-1.65, 1.65]
        icon_y = self.stage_center[1] + 1.00
        lbl_y = icon_y - 1.95

        specs = [
            (icon_thermometer(), "High\nMelting Point", DB_RED),
            (icon_flame(), "High\nBoiling Point", DB_ORANGE),
        ]
        items = []
        for x, (icon, name, color) in zip(xs, specs):
            icon.scale(1.85).move_to([x, icon_y, 0])
            tag = opt_label(name, color, size=24, weight="SEMIBOLD")
            tag.move_to([x, lbl_y, 0])
            arr = flow_arrow(0.34, color=color)
            arr.move_to([x, (icon_y + lbl_y) / 2 + 0.02, 0])
            items.append(VGroup(icon, arr, tag))

        self.show_caption("Inka melting point aur boiling point bhi "
                          "kaafi high hota hai,")                    # 0.55
        for it in items:                                             # 2 x 1.10
            self.play(LaggedStart(FadeIn(it[0], scale=0.7),
                                  GrowArrow(it[1]),
                                  FadeIn(it[2], shift=UP * 0.18),
                                  lag_ratio=0.45), run_time=1.10)
        self.wait(1.25)                                              # 1.25
