# 3D: for a closed surface, every Area Vector points outward.
class SegmentScene(Themed3DScene):
    def construct(self):
        R = 2.0
        sphere = make_gold_sphere(R)
        pts = [(-25 * DEGREES, 52 * DEGREES), (45 * DEGREES, 62 * DEGREES),
               (-75 * DEGREES, 78 * DEGREES), (20 * DEGREES, 38 * DEGREES),
               (-50 * DEGREES, 100 * DEGREES), (80 * DEGREES, 95 * DEGREES)]
        arrows = []
        for u, v in pts:
            P = sphere_point(u, v, R)
            n = P / np.linalg.norm(P)
            arrows.append(Arrow3D(P, P + 1.2 * n, color="#FFE24A",
                                  thickness=0.018, base_radius=0.085))
        self.stage(sphere, *arrows)

        cap = self.label("For a closed surface, every Area Vector points OUTWARD",
                         color="#FFFFFF", scale=0.56)
        cap.to_edge(UP, buff=0.7)
        self.hud(cap)

        self.play(Create(sphere), run_time=1.6)
        self.play(LaggedStart(*[Create(a) for a in arrows], lag_ratio=0.15),
                  run_time=2.0)
        self.play(FadeIn(cap), run_time=0.6)
        self.begin_ambient_camera_rotation(rate=0.10)
        self.wait(2.0)
