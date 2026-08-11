# 3D: every area element dA has an outward Area Vector.
class SegmentScene(Themed3DScene):
    def construct(self):
        R = 2.0
        sphere = make_gold_sphere(R)
        u0, v0 = -25 * DEGREES, 52 * DEGREES
        patch = make_area_patch(u0, v0, R, half=0.2)
        P = sphere_point(u0, v0, R)
        n = P / np.linalg.norm(P)
        avec = Arrow3D(P, P + 1.5 * n, color="#FFE24A",
                       thickness=0.02, base_radius=0.1)
        self.stage(sphere, patch, avec)

        cap = self.label("Every small area dA has an outward Area Vector",
                         color="#FFFFFF", scale=0.58)
        cap.to_edge(UP, buff=0.7)
        self.hud(cap)

        self.play(Create(sphere), run_time=1.6)
        self.play(FadeIn(patch), Create(avec), run_time=1.0)
        self.play(FadeIn(cap), run_time=0.6)
        self.begin_ambient_camera_rotation(rate=0.10)
        self.wait(2.6)
