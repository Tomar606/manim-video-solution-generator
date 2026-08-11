# Total flux is proportional to the enclosed charge.
class SegmentScene(ThemedScene):
    def construct(self):
        c = self.stage_center
        cap = self.label("Total Flux is proportional to the charge enclosed",
                         color="#FFFFFF", scale=0.58)
        self.top_caption(cap)

        prop = MathTex(r"\Phi \;\propto\; Q_{\text{enc}}", color="#FFE24A").scale(1.7)
        eq = MathTex(r"\Phi = \frac{Q_{\text{enc}}}{\varepsilon_0}",
                     color="#FFFFFF").scale(1.5)
        grp = VGroup(prop, eq).arrange(DOWN, buff=0.7).move_to(c)

        self.play(FadeIn(cap), run_time=0.6)
        self.play(Write(prop), run_time=1.0)
        self.play(TransformMatchingShapes(prop.copy(), eq), run_time=1.2)
        self.wait(1.2)
