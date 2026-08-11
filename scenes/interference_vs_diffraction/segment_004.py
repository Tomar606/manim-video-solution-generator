# SCENE 5a — "Fringe Pattern". Both screens appear, still dark. Establishes the
# geometry that segments 5-9 all reuse, so the cuts read as one continuous shot.
class SegmentScene(ThemedScene):
    def construct(self):
        lay, p = compare_base(self.stage_center, self.stage_w)
        _ = lay

        self.show_caption("Fringe Pattern")                          # 0.55
        self.play(Create(p["divider"]), run_time=0.40)               # 0.40
        self.play(FadeIn(p["head_l"], shift=DOWN * 0.20),
                  FadeIn(p["head_r"], shift=DOWN * 0.20),
                  run_time=0.55)                                     # 0.55
        self.play(LaggedStart(FadeIn(p["plate_l"], shift=UP * 0.20),
                              FadeIn(p["plate_r"], shift=UP * 0.20),
                              lag_ratio=0.30), run_time=0.95)        # 0.95
        self.play(FadeIn(p["cap_l"]), FadeIn(p["cap_r"]),
                  run_time=0.45)                                     # 0.45
        self.wait(1.10)                                              # 1.10
