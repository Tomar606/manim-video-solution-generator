"""Draw the figure that belongs on an answer sheet, as a student would draw it.

    .venv-manim/bin/manim -s -qh --format=png -o daniell \
        tools/answer_figure.py DaniellFigure

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
construction. This is the same reasoning that keeps text out of the generated
illustrations in the video itself (see CLAUDE.md).

ACCURACY — checked against NCERT Class 12 Chemistry, Unit 3
-----------------------------------------------------------
  · zinc on the LEFT and copper on the RIGHT, the conventional orientation
  · the anode is NEGATIVE and the cathode POSITIVE — a galvanic cell, the
    opposite of the electrolytic cell in the Faraday scene
  · electrons run through the EXTERNAL WIRE, Zn -> Cu; never through the liquid
  · the salt bridge carries IONS, and is drawn as an inverted U above the
    liquids, dipping into both
  · oxidation at the anode, reduction at the cathode — true of both cell types
  · Zn(s) | ZnSO4(aq) || CuSO4(aq) | Cu(s), anode first, left to right

It is drawn in ink on white because it sits on ruled paper, not on the video's
dark plate.
"""
from manim import *

# PENCIL, not pen. The reference answer sheet (inbox/answer_reference.jpeg)
# writes in blue ballpoint and draws in GRAPHITE: grey, thin, no colour fills,
# the shading suggested by hatching rather than by a flat tint. A figure in
# saturated colour reads as clip-art dropped onto the page, however accurate it
# is. So there is one ink here and everything is drawn in it.
INK   = "#5A5F66"        # graphite
INK_D = "#3E434A"        # a harder press, for the parts that carry meaning
FILL  = "#D8DCE1"        # the lightest possible tone, for a metal rod
LIQ   = "#EDEFF2"        # liquid: barely there, so labels stay legible over it

config.background_color = "#FFFFFF"


class DaniellFigure(Scene):
    def construct(self):
        F = "Khand"

        def label(t, size=26, color=INK_D):
            # pencil lettering is lighter than the ballpoint prose around it
            return Text(t, font=F, font_size=size, color=color, weight="MEDIUM")

        # ---- the two beakers -------------------------------------------- #
        def beaker(fill):
            glass = VMobject().set_points_as_corners([
                [-1.15, 1.30, 0], [-1.15, -1.30, 0],
                [1.15, -1.30, 0], [1.15, 1.30, 0]]).set_stroke(INK, 2.4)
            liquid = Rectangle(width=2.24, height=1.72, stroke_width=0,
                               fill_color=fill, fill_opacity=1.0)
            liquid.move_to([0, -1.30 + 1.72 / 2, 0])
            return VGroup(glass, liquid)

        left, right = beaker(LIQ), beaker(LIQ)
        VGroup(left, right).arrange(RIGHT, buff=1.9)

        # ---- electrodes -------------------------------------------------- #
        def rod(colour, x):
            r = Rectangle(width=0.30, height=2.45, stroke_color=INK_D,
                          stroke_width=2.2, fill_color=colour, fill_opacity=1.0)
            r.move_to([x, 0.42, 0])
            return r

        zn = rod(FILL, left.get_center()[0])
        cu = rod(FILL, right.get_center()[0])

        # ---- external circuit: rods -> up -> across, with the meter ------ #
        top = 2.30
        wire = VMobject().set_points_as_corners([
            zn.get_top(), [zn.get_x(), top, 0],
            [cu.get_x(), top, 0], cu.get_top()]).set_stroke(INK_D, 2.2)
        meter = Circle(radius=0.34, stroke_color=INK_D, stroke_width=2.2,
                       fill_color="#FFFFFF", fill_opacity=1.0)
        meter.move_to([0, top, 0])
        meter_g = VGroup(meter, label("V", 26).move_to(meter.get_center()))

        # electron flow: an arrow ON the wire, pointing zinc -> copper
        e_arrow = Arrow([-0.95, top, 0], [-0.45, top, 0], buff=0,
                        stroke_width=2.6, max_tip_length_to_length_ratio=0.45,
                        color=INK_D)
        e_lab = label("e⁻", 24).next_to(e_arrow, UP, buff=0.10)

        # ---- salt bridge: an inverted U dipping INTO both liquids -------- #
        # The liquid surface is at y = 0.42, so the arms have to end BELOW that
        # or the bridge is drawn hanging in the air — which is exactly the
        # detail an examiner looks for, since the bridge is what carries the
        # ions. Its top clears the rods but stays under the wire.
        liquid_top = -1.30 + 1.72
        bridge_y, dip = 1.12, liquid_top - 0.34
        bridge = VMobject().set_points_as_corners([
            [zn.get_x() + 0.66, dip, 0], [zn.get_x() + 0.66, bridge_y, 0],
            [cu.get_x() - 0.66, bridge_y, 0], [cu.get_x() - 0.66, dip, 0],
        ]).set_stroke(INK_D, 3.6)
        bridge_lab = label("लवण सेतु", 27).next_to(bridge, UP, buff=0.10)

        # ---- labels ------------------------------------------------------ #
        # Everything that names a beaker goes BELOW it, stacked. Putting the
        # solution name inside the liquid ran it straight through the electrode.
        zn_lab = label("Zn", 30).next_to(zn, UP, buff=0.14).shift(LEFT * 0.44)
        cu_lab = label("Cu", 30).next_to(cu, UP, buff=0.14).shift(RIGHT * 0.44)
        # Kept SHORT on purpose. The figure sits inline at about 45% of the page
        # width, so it is drawn small; "(−) ऐनोड — ऑक्सीकरण" under each beaker
        # became unreadable at that size. The reference sheet labels its parts
        # with one or two words each and leaves the explaining to the prose,
        # which is where oxidation and reduction are already stated.
        zn_foot = VGroup(label("ZnSO₄", 30), label("ऐनोड (−)", 30)
                         ).arrange(DOWN, buff=0.14).next_to(left, DOWN, buff=0.26)
        cu_foot = VGroup(label("CuSO₄", 30), label("कैथोड (+)", 30)
                         ).arrange(DOWN, buff=0.14).next_to(right, DOWN, buff=0.26)

        fig = VGroup(left, right, zn, cu, wire, meter_g, e_arrow, e_lab,
                     bridge, bridge_lab, zn_lab, cu_lab, zn_foot, cu_foot)
        fig.move_to(ORIGIN).scale(1.15)
        self.add(fig)
