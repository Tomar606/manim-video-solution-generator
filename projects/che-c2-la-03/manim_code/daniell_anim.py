"""Daniell cell — CONSTRUCTED, not traced, and animated.

    manim -qm -r 1080,1920 -o daniell_anim daniell_anim.py DaniellAnim

The book's Daniell figure is drawn freehand and traces to a wobbly line; the dry
cell's is ruled and traces clean. Rather than inherit one book's handwriting,
this builds the apparatus from primitives — and because every part is placed by
this file, the electron and ion paths are exact instead of measured off a bitmap.
"""
from pathlib import Path
import numpy as np
import manimpango
from manim import *

ROOT = Path(__file__).resolve().parents[3]
for f in (ROOT / "assets" / "fonts").glob("*.ttf"):
    manimpango.register_font(str(f))

BG, INK, GOLD, CYAN, GREEN = "#0B1B3A", "#EAF2FF", "#FFC15C", "#5BC8F9", "#8FE3B0"
ZN_SOL, CU_SOL, ZN_MET, CU_MET = "#8FA6BC", "#2E86C1", "#C8D4E0", "#C87137"
FONT, SW = "Poppins", 3.2

config.pixel_width, config.pixel_height = 1080, 1920
config.frame_height = 9.6
config.frame_width = 9.6 * 1080 / 1920      # 5.4

# --- geometry, in figure units; one place, so every path can quote it -------- #
BK_W, BK_H, BK_R = 1.42, 1.55, 0.18        # beaker
BK_Y = -1.55                                # beaker floor
LBX, RBX = -1.22, 1.22                      # beaker centres
LIQ_Y = BK_Y + 1.05                         # liquid surface
ROD_W, ROD_TOP, ROD_BOT = 0.19, 0.78, BK_Y + 0.26
ZNX, CUX = LBX - 0.34, RBX + 0.34           # rods sit inboard of the far wall
WIRE_Y = 2.40                                # the horizontal wire
BR_X, BR_TOP, BR_BOT = 0.52, 0.95, LIQ_Y - 0.42   # salt bridge limbs
G_X, R_X = 0.92, -0.92                       # galvanometer, resistor


class DaniellAnim(Scene):
    def construct(self):
        self.camera.background_color = BG
        fig = VGroup(*self.beaker(LBX), *self.beaker(RBX))
        liq = VGroup(self.liquid(LBX, ZN_SOL), self.liquid(RBX, CU_SOL))
        rods = VGroup(self.rod(ZNX, ZN_MET), self.rod(CUX, CU_MET))
        wire = self.circuit()
        bridge = self.bridge()

        self.play(Create(fig), run_time=1.2)
        self.play(FadeIn(liq), run_time=0.6)
        self.play(Create(rods), run_time=0.7)
        self.play(Create(bridge), run_time=0.9)
        self.play(Create(wire), run_time=1.1)

        self.play(LaggedStart(*[FadeIn(m) for m in self.labels()],
                              lag_ratio=0.16), run_time=2.2)
        self.wait(0.3)
        self.mechanism()
        self.wait(0.8)

    # ---- parts ------------------------------------------------------------- #
    def beaker(self, cx):
        x0, x1 = cx - BK_W / 2, cx + BK_W / 2
        y0, y1 = BK_Y, BK_Y + BK_H
        body = VMobject().set_points_as_corners([
            [x0, y1, 0], [x0, y0 + BK_R, 0]])
        arcl = ArcBetweenPoints([x0, y0 + BK_R, 0], [x0 + BK_R, y0, 0], angle=-PI / 2)
        base = Line([x0 + BK_R, y0, 0], [x1 - BK_R, y0, 0])
        arcr = ArcBetweenPoints([x1 - BK_R, y0, 0], [x1, y0 + BK_R, 0], angle=-PI / 2)
        rgt = Line([x1, y0 + BK_R, 0], [x1, y1, 0])
        rim = VGroup(Line([x0 - 0.07, y1, 0], [x0, y1, 0]),
                     Line([x1, y1, 0], [x1 + 0.07, y1, 0]))
        g = VGroup(body, arcl, base, arcr, rgt, rim)
        g.set_stroke(INK, SW, 1).set_fill(opacity=0)
        return [g]

    def liquid(self, cx, colour):
        x0, x1 = cx - BK_W / 2 + 0.05, cx + BK_W / 2 - 0.05
        top, bot = LIQ_Y, BK_Y + 0.05
        r = Rectangle(width=x1 - x0, height=top - bot)
        r.set_fill(colour, 0.5).set_stroke(width=0)
        r.move_to([(x0 + x1) / 2, (top + bot) / 2, 0])
        return r

    def rod(self, x, colour):
        r = Rectangle(width=ROD_W, height=ROD_TOP - ROD_BOT)
        r.set_fill(colour, 0.85).set_stroke(INK, 2.0, 1)
        r.move_to([x, (ROD_TOP + ROD_BOT) / 2, 0])
        return r

    def bridge(self):
        left = Line([-BR_X, BR_BOT, 0], [-BR_X, BR_TOP, 0])
        arc = ArcBetweenPoints([-BR_X, BR_TOP, 0], [BR_X, BR_TOP, 0], angle=-PI)
        right = Line([BR_X, BR_TOP, 0], [BR_X, BR_BOT, 0])
        g = VGroup(left, arc, right).set_stroke(INK, 11, 1)
        g.set_cap_style(CapStyleType.ROUND) if hasattr(g, "set_cap_style") else None
        return g

    def circuit(self):
        up_l = Line([ZNX, ROD_TOP, 0], [ZNX, WIRE_Y, 0])
        up_r = Line([CUX, ROD_TOP, 0], [CUX, WIRE_Y, 0])
        seg1 = Line([ZNX, WIRE_Y, 0], [R_X - 0.42, WIRE_Y, 0])
        zig = VMobject().set_points_as_corners(
            [[R_X - 0.42, WIRE_Y, 0]] +
            [[R_X - 0.42 + i * 0.12, WIRE_Y + (0.16 if i % 2 else -0.16), 0]
             for i in range(1, 8)] + [[R_X + 0.42, WIRE_Y, 0]])
        seg2 = Line([R_X + 0.42, WIRE_Y, 0], [G_X - 0.26, WIRE_Y, 0])
        g = Circle(radius=0.26).move_to([G_X, WIRE_Y, 0])
        gl = Text("G", font=FONT, font_size=26, color=INK).move_to(g.get_center())
        seg3 = Line([G_X + 0.26, WIRE_Y, 0], [CUX, WIRE_Y, 0])
        w = VGroup(up_l, seg1, zig, seg2, g, seg3, up_r)
        w.set_stroke(INK, SW, 1).set_fill(opacity=0)
        return VGroup(w, gl)

    # ---- labels ------------------------------------------------------------ #
    @staticmethod
    def _p3(v):
        v = np.asarray(v, dtype=float)
        return v if v.size == 3 else np.array([v[0], v[1], 0.0])

    def leader(self, a, b):
        """A thin line from a label to the thing it names. Textbook figures put
        the word where there is room and let a leader carry it to the part; that
        is what makes a label near-source even when the gutter is narrow."""
        return Line(self._p3(a), self._p3(b),
                    stroke_width=1.8, color=INK).set_opacity(0.75)

    def tagged(self, text, at, to, size=23, col=INK, bold=False, plate=None):
        """label placed at `at`, joined to `to` by a leader."""
        t = Text(text, font=FONT, font_size=size, color=col,
                 weight=BOLD if bold else NORMAL)
        t.move_to(self._p3(at))
        body = t
        if plate:
            box = RoundedRectangle(width=t.width + 0.26, height=t.height + 0.20,
                                   corner_radius=0.08).set_fill(plate, 1).set_stroke(width=0)
            box.move_to(t.get_center())
            body = VGroup(box, t)
        to3 = self._p3(to)
        d = to3 - body.get_center()
        edge = body.get_boundary_point(d / (np.linalg.norm(d) or 1.0))
        return VGroup(body, self.leader(edge, to3))

    def labels(self):
        """Every label sits as close to its part as the frame allows, and a
        leader closes the gap. The two solutions are named INSIDE their own
        beaker, where the book puts them and no leader is needed at all."""
        out = []
        # electrodes — outside the beaker, leader across to the rod
        out.append(self.tagged("जिंक", [-2.18, 0.62], [ZNX - 0.10, 0.30],
                               size=24, col=GOLD, bold=True))
        out.append(self.tagged("कॉपर", [2.18, 0.62], [CUX + 0.10, 0.30], size=24))
        # salt bridge — above the arch, leader down onto it
        out.append(self.tagged("लवण सेतु", [0.0, BR_TOP + 0.86],
                               [0.0, BR_TOP + BR_X - 0.06], size=24))
        # the two half reactions, named beneath their own electrode
        out.append(self.tagged("ऑक्सीकरण", [LBX, BK_Y - 0.52], [LBX, BK_Y - 0.10],
                               size=22, col="#FFD6D6", bold=True, plate="#7E2F2F"))
        out.append(self.tagged("अपचयन", [RBX, BK_Y - 0.52], [RBX, BK_Y - 0.10],
                               size=22, col="#C6F5DC", bold=True, plate="#1E5B3A"))
        # solutions: named where they are, no leader needed
        for x, tex in ((LBX + 0.02, r"ZnSO_4"), (RBX - 0.02, r"CuSO_4")):
            m = MathTex(tex, color=INK).scale(0.55).move_to([x, LIQ_Y - 0.92, 0])
            out.append(VGroup(m))
        return out

    # ---- the mechanism ----------------------------------------------------- #
    def dots(self, pts, colour, n, rt, r=0.075, lag=0.12):
        path = VMobject().set_points_as_corners([np.array(p, dtype=float) for p in pts])
        ds = VGroup(*[Dot(radius=r, color=colour).set_stroke(colour, 6, 0.30, background=True)
                      for _ in range(n)])
        return ds, LaggedStart(*[MoveAlongPath(d, path, run_time=rt, rate_func=linear)
                                 for d in ds], lag_ratio=lag)

    def bridge_path(self, right_to_left=True):
        """The route an ion actually takes: down one limb, round the bend, up
        the other. Built from the SAME primitives as bridge(), so a dot cannot
        drift off the tube. Corner points alone gave a straight chord across the
        top — the ions climbed the limb and then cut horizontally through open
        air above the arch."""
        if right_to_left:
            a, b = BR_X, -BR_X
            arc = ArcBetweenPoints([a, BR_TOP, 0], [b, BR_TOP, 0], angle=PI)
        else:
            a, b = -BR_X, BR_X
            arc = ArcBetweenPoints([a, BR_TOP, 0], [b, BR_TOP, 0], angle=-PI)
        up = Line([a, BR_BOT, 0], [a, BR_TOP, 0])
        down = Line([b, BR_TOP, 0], [b, BR_BOT, 0])
        path = VMobject()
        path.append_points(up.get_points())
        path.append_points(arc.get_points())
        path.append_points(down.get_points())
        return path

    def dots_on(self, path, colour, n, rt, r=0.075, lag=0.12):
        ds = VGroup(*[Dot(radius=r, color=colour).set_stroke(colour, 6, 0.30, background=True)
                      for _ in range(n)])
        return ds, LaggedStart(*[MoveAlongPath(d, path, run_time=rt, rate_func=linear)
                                 for d in ds], lag_ratio=lag)

    def mechanism(self):
        e = MathTex(r"e^{-}", color=CYAN).scale(0.62).move_to([0.0, WIRE_Y + 0.34, 0])
        self.play(FadeIn(e, scale=1.2), run_time=0.35)
        route = [[ZNX, 0.0, 0], [ZNX, WIRE_Y, 0], [CUX, WIRE_Y, 0], [CUX, 0.0, 0]]
        znt = MathTex(r"Zn^{2+}", color=GOLD).scale(0.55).move_to([ZNX + 0.50, LIQ_Y - 0.16, 0])
        cut = MathTex(r"Cu^{2+}", color=GOLD).scale(0.55).move_to([CUX - 0.50, LIQ_Y - 0.16, 0])
        no3 = MathTex(r"NO_3^{-}", color=INK).scale(0.5).move_to([0.0, BR_TOP - 0.30, 0])
        kp = MathTex(r"K^{+}", color=GREEN).scale(0.5).move_to([0.0, BR_TOP - 0.74, 0])
        self.play(FadeIn(znt), FadeIn(cut), FadeIn(no3), FadeIn(kp), run_time=0.5)

        # NO3- travels toward the ANODE (left), K+ toward the CATHODE (right)
        p_no3 = self.bridge_path(right_to_left=True)
        p_k = self.bridge_path(right_to_left=False)
        for _ in range(2):
            ed, ea = self.dots(route, CYAN, 7, 3.2, 0.085, 0.10)
            zd, za = self.dots([[ZNX + 0.10, LIQ_Y - 0.55, 0], [LBX + 0.55, LIQ_Y - 0.80, 0]],
                               GOLD, 4, 2.4, 0.065)
            cd, ca = self.dots([[RBX - 0.55, LIQ_Y - 0.80, 0], [CUX - 0.10, LIQ_Y - 0.55, 0]],
                               GOLD, 4, 2.4, 0.065)
            nd, na = self.dots_on(p_no3, INK, 3, 3.4, 0.065)
            kd, ka = self.dots_on(p_k, GREEN, 3, 3.4, 0.065)
            self.add(ed, zd, cd, nd, kd)
            self.play(ea, za, ca, na, ka)
            self.remove(ed, zd, cd, nd, kd)
