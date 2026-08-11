# 3D: flux is the dot product of E and the Area Vector.
class SegmentScene(Themed3DScene):
    def construct(self):
        R = 2.0
        sphere = make_gold_sphere(R)
        u0, v0 = -25 * DEGREES, 52 * DEGREES
        patch = make_area_patch(u0, v0, R, half=0.2)
        P = sphere_point(u0, v0, R)
        n = P / np.linalg.norm(P)
        # Area vector (outward, yellow)
        avec = Arrow3D(P, P + 1.5 * n, color="#FFE24A",
                       thickness=0.02, base_radius=0.1)
        # E vector (white) at an angle to the normal
        tu = np.array([-np.sin(u0) * np.sin(v0), np.cos(u0) * np.sin(v0), 0.0])
        tu = tu / np.linalg.norm(tu)
        edir = 0.7 * n + 0.7 * tu
        edir = edir / np.linalg.norm(edir)
        evec = Arrow3D(P, P + 1.5 * edir, color="#FFFFFF",
                       thickness=0.02, base_radius=0.1)
        self.stage(sphere, patch, avec, evec)

        cap = self.label("Electric Flux uses the dot product of E and dA",
                         color="#FFFFFF", scale=0.58)
        cap.to_edge(UP, buff=0.7)
        self.hud(cap)
        eq = MathTex(r"\Phi = \vec{E}\cdot d\vec{a}", color="#FFE24A").scale(1.2)
        eq.move_to([0.0, 0.4, 0.0])
        self.hud(eq)

        self.play(Create(sphere), run_time=1.4)
        self.play(FadeIn(patch), Create(avec), Create(evec), run_time=1.1)
        self.play(FadeIn(cap), Write(eq), run_time=0.8)
        self.begin_ambient_camera_rotation(rate=0.10)
        self.wait(1.8)
