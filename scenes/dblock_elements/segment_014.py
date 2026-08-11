# ENDING — the two points to remember, then the frame clears for the
# answer-writing shot.
class SegmentScene(ThemedScene):
    CAPTION_MODE = "narration"

    def construct(self):
        head = chip("Remember These 2 Points", DB_GREEN, size=26)
        head.move_to(self.stage_center + UP * 2.30)

        def point(num, lines, color, y):
            card = RoundedRectangle(width=6.45, height=1.52, corner_radius=0.24,
                                    stroke_width=2.0, stroke_color=color,
                                    stroke_opacity=0.55, fill_color="#0B1830",
                                    fill_opacity=0.55).move_to([0.0, y, 0])
            badge = Circle(radius=0.28, stroke_width=2.4, stroke_color=color,
                           fill_color="#12203C", fill_opacity=0.95)
            badge.move_to([-2.62, y, 0])
            n = opt_label(num, color, size=25, weight="BOLD")
            n.move_to(badge.get_center())
            body = opt_label(lines, "#FFFFFF", size=23, weight="SEMIBOLD")
            body.move_to([-0.05, y, 0])
            tick = check_mark(0.70).move_to([2.66, y, 0])
            return VGroup(card, badge, n, body), tick

        p1, t1 = point("1", "Last Electron in d-Orbital", DB_ORANGE,
                       self.stage_center[1] + 0.62)
        p2, t2 = point("2", "Strong Metallic Bonding +\nVariable Oxidation State",
                       DB_PURPLE, self.stage_center[1] - 1.20)

        self.show_caption("Bas itna yaad rakhna—jin elements ka last "
                          "electron d-orbital mein enter karta hai, unhe "
                          "d-block elements kehte hain.")            # 0.55
        self.play(FadeIn(head, shift=DOWN * 0.20), run_time=0.50)    # 0.50
        self.play(FadeIn(p1, shift=UP * 0.22), run_time=0.60)        # 0.60
        self.play(Create(t1), run_time=0.50)                         # 0.50
        self.play(FadeIn(p2, shift=UP * 0.22), run_time=0.60)        # 0.60
        self.play(Create(t2), run_time=0.50)                         # 0.50
        self.wait(1.55)                                              # 1.55
        self.play(FadeOut(VGroup(head, p1, t1, p2, t2), shift=UP * 0.25),
                  FadeOut(self.caption_mob, shift=UP * 0.20),
                  run_time=0.70)                                     # 0.70
