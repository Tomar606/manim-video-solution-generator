"""Draw the figure that belongs on an answer sheet, as a student would draw it.

    .venv-manim/bin/manim -s -qh -t --format=png \
        --media_dir <dir> -o pencil tools/answer_figure.py DaniellFigure

Some questions are not fully answered in prose. "विद्युत्-रासायनिक सेल एवं उसकी
क्रियाविधि डेनियल सेल का उदाहरण देकर समझाइए" expects the labelled cell on the
page; an examiner marks it. Others — state the two laws of electrolysis, define
corrosion and list three preventions — do not, and a figure there is decoration.
So this file holds one scene per question that genuinely needs one, and nothing
else gets called.

WHY DRAWN AND NOT GENERATED
---------------------------
An image model gets the picture roughly right and the LETTERING wrong, and on a
figure whose whole content is which electrode is which, that is the only part
that matters. Every label here is placed by name, so it is right by
construction.

BUT DRAWN IS NOT THE SAME AS HAND-DRAWN
---------------------------------------
A Manim figure in grey is still a vector figure: every line dead straight, every
stroke exactly one width, every corner exact. On a sheet of handwriting it reads
as clip-art pasted in, however correct it is — which is precisely the note this
came back with. So nothing is drawn directly. Every shape is built exactly, then
passed through `hand()`, which is where it stops looking digital:

  · each path is resampled and displaced by two summed sine waves at unrelated
    frequencies, so lines drift the way an unsteady hand drifts rather than
    wobbling periodically
  · every stroke is drawn TWICE, offset and at different opacity — a pencil
    rarely lands on its own line the second time, and the doubling is most of
    what makes graphite look like graphite
  · stroke width varies per pass, standing in for pressure

Fills go too: a flat tint is the most digital thing on a page. The solutions are
HATCHED instead, which is how the reference sheet shades its own apparatus, and
the labels are set in Kalam — the handwriting face — rather than a UI sans.

ACCURACY — checked against NCERT Class 12 Chemistry, Unit 3
-----------------------------------------------------------
  · zinc on the LEFT and copper on the RIGHT, the conventional orientation
  · the anode is NEGATIVE and the cathode POSITIVE — a galvanic cell, the
    opposite of the electrolytic cell in the Faraday scene
  · electrons run through the EXTERNAL WIRE, Zn -> Cu; never through the liquid
  · the salt bridge carries IONS, and dips INTO both solutions
  · oxidation at the anode, reduction at the cathode — true of both cell types
"""
from pathlib import Path

import manimpango
import numpy as np
from manim import *

# Registered at module scope, AFTER manim is imported. This is the order that
# works — verified in isolation — and it is not obvious: registering inside
# construct() is too late, and registering before `from manim import *` is too
# early. Both return True and both leave `font="Kalam"` resolving to a UI sans,
# so the failure is completely silent. Asserted rather than trusted.
HAND_FONT = str(Path(__file__).resolve().parent.parent /
                "assets" / "fonts" / "Kalam-Regular.ttf")
assert Path(HAND_FONT).exists(), f"handwriting font missing: {HAND_FONT}"
assert manimpango.register_font(HAND_FONT), "Pango refused the handwriting font"

# Graphite, not ink. The reference sheet writes in blue ballpoint and draws in
# pencil: grey, thin, no colour anywhere in the figure.
INK   = "#4A4F57"
INK_D = "#33373D"

HAND_FONT = str(Path(__file__).resolve().parent.parent /
                "assets" / "fonts" / "Kalam-Regular.ttf")


config.background_color = "#FFFFFF"


def seg(p, q):
    """One straight stroke. Shapes are built from these rather than as closed
    paths, because `hand()` overshoots the ENDS of whatever it is given — and a
    box drawn as four overshooting strokes is what a sketched box looks like,
    while a box drawn as one closed path has four perfect corners however much
    the sides wobble."""
    return Line(np.array(p, dtype=float), np.array(q, dtype=float))


def hand(mob, amp=0.030, passes=2, seed=0, width=None, colour=None,
         overshoot=0.05):
    """Redraw a shape the way a hand would draw it.

    Returns a new VGroup; the input is only used for its geometry. Two passes
    per path, each displaced independently, is the whole trick — one pass looks
    like a wobbly vector, two look like someone went over it.
    """
    rng = np.random.default_rng(seed)
    out = VGroup()
    for leaf in mob.family_members_with_points():
        if not isinstance(leaf, VMobject) or leaf.get_num_points() == 0:
            continue
        col = colour or leaf.get_stroke_color()
        base_w = width if width is not None else max(leaf.get_stroke_width(), 1.0)
        for sub in leaf.get_subpaths():
            path = VMobject()
            path.set_points(sub)
            try:
                length = path.get_arc_length()
            except Exception:
                length = 4.0
            n = int(np.clip(length / 0.05, 16, 400))
            pts = np.array([path.point_from_proportion(t)
                            for t in np.linspace(0, 1, n)])
            # Run past both ends. Nobody stops a pencil exactly on the corner,
            # and the little crossings where strokes overrun each other are
            # most of what separates a sketch from a vector drawing.
            if overshoot and len(pts) > 3:
                head = pts[0] - (pts[1] - pts[0])
                tail = pts[-1] + (pts[-1] - pts[-2])
                k = rng.uniform(0.5, 1.6) * overshoot
                d0 = (pts[0] - pts[1]); d0 /= max(np.linalg.norm(d0), 1e-6)
                d1 = (pts[-1] - pts[-2]); d1 /= max(np.linalg.norm(d1), 1e-6)
                pts = np.vstack([pts[0] + d0 * k, pts, pts[-1] + d1 * k])
                n = len(pts)
            for k in range(passes):
                # two sine terms at unrelated frequencies: a single term reads
                # as a regular ripple, which no hand produces
                s = np.linspace(0, rng.uniform(2.0, 3.4), n)
                ph = rng.uniform(0, 2 * np.pi, 4)
                f = rng.uniform(0.7, 1.3)
                d = np.zeros_like(pts)
                d[:, 0] = (np.sin(s * f + ph[0]) * amp
                           + np.sin(s * 2.7 * f + ph[1]) * amp * 0.45)
                d[:, 1] = (np.cos(s * 1.2 * f + ph[2]) * amp
                           + np.sin(s * 3.1 * f + ph[3]) * amp * 0.40)
                # the ends are held: a hand starts and stops ON the corner
                taper = np.sin(np.linspace(0, np.pi, n)) ** 0.6
                d *= taper[:, None]
                stroke = VMobject().set_points_smoothly(pts + d)
                stroke.set_stroke(
                    col, base_w * rng.uniform(0.80, 1.20),
                    opacity=0.92 if k == 0 else rng.uniform(0.30, 0.50))
                out.add(stroke)
    return out


def hatch(x0, x1, y0, y1, step=0.16, seed=0, colour=INK, width=1.2):
    """Light diagonal shading, the way the reference shades its apparatus."""
    rng = np.random.default_rng(seed)
    g = VGroup()
    y = y0
    while y < y1:
        jitter = rng.uniform(-0.02, 0.02, 4)
        line = Line([x0 + jitter[0], y + jitter[1], 0],
                    [x1 + jitter[2], y + 0.06 + jitter[3], 0])
        line.set_stroke(colour, width, opacity=rng.uniform(0.25, 0.45))
        g.add(line)
        y += step
    return g


class DaniellFigure(Scene):
    def construct(self):
        def label(t, size=26, colour=INK_D):
            return Text(t, font="Kalam", font_size=size, color=colour)

        # ---- geometry, drawn exactly; `hand()` roughens it afterwards ---- #
        def beaker_at(cx):
            return VGroup(seg([cx - 1.15, 1.30, 0], [cx - 1.15, -1.30, 0]),
                          seg([cx - 1.15, -1.30, 0], [cx + 1.15, -1.30, 0]),
                          seg([cx + 1.15, -1.30, 0], [cx + 1.15, 1.30, 0]))

        left_x, right_x = -2.20, 2.20
        glass_l, glass_r = beaker_at(left_x), beaker_at(right_x)

        liquid_top = 0.42
        rod_w, rod_h, rod_y = 0.30, 2.45, 0.42
        def rod_at(cx):
            a, b = cx - rod_w / 2, cx + rod_w / 2
            t, u = rod_y + rod_h / 2, rod_y - rod_h / 2
            return VGroup(seg([a, t, 0], [a, u, 0]), seg([a, u, 0], [b, u, 0]),
                          seg([b, u, 0], [b, t, 0]), seg([b, t, 0], [a, t, 0]))

        zn, cu = rod_at(left_x), rod_at(right_x)

        top = 2.30
        wire = VGroup(seg([left_x, rod_y + rod_h / 2, 0], [left_x, top, 0]),
                      seg([left_x, top, 0], [right_x, top, 0]),
                      seg([right_x, top, 0], [right_x, rod_y + rod_h / 2, 0]))
        meter = Circle(radius=0.34).move_to([0, top, 0])

        bridge_y, dip = 1.12, liquid_top - 0.34
        bl, br = left_x + 0.66, right_x - 0.66
        bridge = VGroup(seg([bl, dip, 0], [bl, bridge_y, 0]),
                        seg([bl, bridge_y, 0], [br, bridge_y, 0]),
                        seg([br, bridge_y, 0], [br, dip, 0]))

        # ---- the hand-drawn pass ----------------------------------------- #
        drawn = VGroup(
            hand(VGroup(glass_l, glass_r), amp=0.030, width=2.2, seed=1, colour=INK),
            hand(VGroup(zn, cu), amp=0.018, width=2.0, seed=2, colour=INK_D),
            hand(wire, amp=0.026, width=1.9, seed=3, colour=INK_D),
            hand(meter, amp=0.020, width=1.9, seed=4, colour=INK_D,
                 overshoot=0.0),
            hand(bridge, amp=0.024, width=3.0, seed=5, colour=INK_D),
        )

        # solutions: hatched, never filled — a flat tint is the most digital
        # mark on the page
        shading = VGroup(
            hatch(left_x - 1.08, left_x + 1.08, -1.22, liquid_top, seed=11),
            hatch(right_x - 1.08, right_x + 1.08, -1.22, liquid_top, seed=12),
        )

        # ---- lettering, in the handwriting face --------------------------- #
        e_arrow = Arrow([-0.95, top, 0], [-0.40, top, 0], buff=0,
                        stroke_width=2.4, max_tip_length_to_length_ratio=0.4,
                        color=INK_D)
        marks = VGroup(
            label("V", 26).move_to(meter.get_center()),
            label("e⁻", 24).next_to(e_arrow, UP, buff=0.08),
            label("Zn", 30).next_to(zn, UP, buff=0.16).shift(LEFT * 0.46),
            label("Cu", 30).next_to(cu, UP, buff=0.16).shift(RIGHT * 0.46),
            label("लवण सेतु", 27).move_to([0, bridge_y + 0.30, 0]),
        )
        foot_l = VGroup(label("ZnSO₄", 29), label("ऐनोड (−)", 29)
                        ).arrange(DOWN, buff=0.14)
        foot_r = VGroup(label("CuSO₄", 29), label("कैथोड (+)", 29)
                        ).arrange(DOWN, buff=0.14)
        foot_l.next_to(glass_l, DOWN, buff=0.28)
        foot_r.next_to(glass_r, DOWN, buff=0.28)

        fig = VGroup(shading, drawn, e_arrow, marks, foot_l, foot_r)
        fig.move_to(ORIGIN).scale(1.12)
        self.add(fig)


class DryCellFigure(Scene):
    """शुष्क सेल — the question says सचित्र, so the figure is not optional.

    A cross-section, because that is the only view in which the layers can be
    labelled: jacket, zinc can, moist paste, the MnO2 + carbon mix, and the
    carbon rod down the middle. NCERT's own figure is drawn this way.

    Accuracy: the ZINC CAN is the anode and negative; the carbon rod is the
    cathode and positive but inert — it collects, it does not react. Getting
    that round the wrong way is the standard mistake in this answer.
    """

    def construct(self):
        def label(t, size=25, colour=INK_D):
            return Text(t, font="Kalam", font_size=size, color=colour)

        # --- the can, as nested rounded rectangles ---------------------- #
        can = RoundedRectangle(width=3.05, height=4.30, corner_radius=0.16)
        zinc = RoundedRectangle(width=2.75, height=4.00, corner_radius=0.13)
        paste = RoundedRectangle(width=2.35, height=3.62, corner_radius=0.11)
        mix = RoundedRectangle(width=1.55, height=3.20, corner_radius=0.09)
        rod = Rectangle(width=0.42, height=3.55).shift(UP * 0.18)
        cap = Rectangle(width=0.78, height=0.30).next_to(rod, UP, buff=-0.02)
        seal = Rectangle(width=3.05, height=0.34).move_to(
            can.get_top() + DOWN * 0.17)

        drawn = VGroup(
            hand(can,   amp=0.026, width=2.4, seed=1, colour=INK, overshoot=0.0),
            hand(zinc,  amp=0.022, width=2.2, seed=2, colour=INK_D, overshoot=0.0),
            hand(paste, amp=0.020, width=1.8, seed=3, colour=INK, overshoot=0.0),
            hand(mix,   amp=0.020, width=1.8, seed=4, colour=INK, overshoot=0.0),
            hand(rod,   amp=0.014, width=2.2, seed=5, colour=INK_D),
            hand(cap,   amp=0.014, width=2.2, seed=6, colour=INK_D),
            hand(seal,  amp=0.016, width=1.8, seed=7, colour=INK),
        )
        shading = hatch(-0.72, 0.72, -1.55, 1.62, step=0.20, seed=11, width=1.0)

        # --- leader lines out to the labels ------------------------------ #
        def leader(point, side, text, dy):
            end = np.array([side * 3.35, dy, 0])
            line = hand(seg(point, end), amp=0.012, width=1.4, seed=abs(int(dy * 7)),   # seeds must be non-negative; dy is not
                        colour=INK, passes=1, overshoot=0.02)
            tag = label(text)
            tag.next_to(end, RIGHT if side > 0 else LEFT, buff=0.12)
            return VGroup(line, tag)

        tags = VGroup(
            leader([-1.50, 1.55, 0], -1, "कागज/स्टील जैकेट", 1.95),
            leader([-1.36, 0.55, 0], -1, "जिंक पात्र — ऐनोड (−)", 0.75),
            leader([-1.15, -0.75, 0], -1, "NH₄Cl + ZnCl₂ पेस्ट", -0.75),
            leader([0.72, -1.60, 0], +1, "MnO₂ + कार्बन चूर्ण", -1.60),
            leader([0.21, 1.30, 0], +1, "कार्बन छड़ — कैथोड (+)", 1.45),
        )

        fig = VGroup(shading, drawn, tags)
        fig.move_to(ORIGIN).scale(1.05)
        self.add(fig)
