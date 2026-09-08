"""गॉस का प्रमेय -> कूलॉम का व्युत्क्रम वर्ग नियम, parts 1-2.

    PYQ_PROJECT=phy-c1-la-02 PYQ_PART=1 manim -qh pyq_composed.py PyqPart
    PYQ_PROJECT=phy-c1-la-02 PYQ_PART=2 manim -qh pyq_composed.py PyqPart

Modelled on ``projects/phy-c5-la-01/manim_code/pyq.py`` (the caption-walk
scaffold: ``STAGE_BAND``, ``stage_box()``, ``place()``, ``caption()``/``_hl()``/
``_measure()``, ``_line()``, ``clear_stage()``, ``at()``, the question-card
intro) copied here unchanged, because that is the compositor's geometry
contract (``tools/composite.py`` overlays the presenter at a fixed point) and
every hand-written scene in this track has to keep it identical. Everything
below that scaffold is authored fresh for this question.

Part 2 (``PYQ_PART=2``) picks up immediately after Part 1's boxed
"समीकरण 1" (``Φ_E = E·4πr²``) and finishes the derivation: Gauss's theorem
is written again and tagged "समीकरण 2", the two are equated on the strength
of both being the same flux, and the result is walked through the same
divide-then-rearrange steps Part 1 used for its own equation chain, ending
in a boxed, unlabelled E formula plus a small "E ∝ 1/r²" note. There is no
diagram in this part — it is pure algebra on results Part 1 already
established — so its equation chain runs down the CENTRE of the stage band
(``_eq_center_step``) instead of sharing it with a diagram in a left/right
split. ``_tag_equation1`` (Part 1's box-and-label helper) is generalised to
take the target equation, the mobject to fade out alongside it, and an
optional label, so this part reuses the exact same visual grammar for
"समीकरण 2" and for the final boxed E formula (``label=None`` — the
transcript never numbers that one, so it is boxed as the take-away but not
tagged as an equation).

Reveal indices below are 0-based positions into ``lines_part2.json``:

    line  0 (  0.00s)  a light recap of समीकरण 1, faded straight back out
    line  5 (  9.54s)  ...once the presenter turns to Gauss's theorem again
    line  7 ( 12.72s)  oint(E.dS) = Q/eps0 is written
    line  8 ( 14.82s)  ...and boxed as समीकरण 2
    line 10 ( 19.90s)  समीकरण 1 reappears, dimmed, stacked above समीकरण 2
    line 11 ( 21.76s)  both are highlighted -- same flux, two notations
    line 12 ( 23.62s)  both fade out ("so we'll equate them")
    line 13 ( 24.90s)  E.4*pi*r^2 = Q/eps0 lands
    line 16 ( 31.20s)  the division step is shown, not skipped
    line 17 ( 32.90s)  E = Q / (4*pi*eps0*r^2)
    line 20 ( 41.26s)  the textbook rearrangement: E = (1/4*pi*eps0)*(Q/r^2)
    line 22 ( 45.42s)  boxed as the take-away (no label -- not numbered)
    line 24 ( 49.98s)  "E ∝ 1/r^2" note, alongside the box

Two things this part actually has to show, and neither fits an existing
``beat_*`` helper in ``src/manim_helpers.py``:

1. Gauss's law itself, landing as a formula the moment it is spoken, with its
   three symbols (E, dS, epsilon-nought) glossed one at a time underneath it.
2. The derivation diagram — a point charge +Q at O, a sphere of radius R
   through a point P, and at P the two vectors (dS, E) whose zero angle is
   the entire justification for the next four algebra steps.

The sphere is drawn as a 2D cross-section circle, not a 3D ``Surface``: the
stage band is a narrow strip (``STAGE_TOP``/``STAGE_BOT`` below, ~20% of the
frame height) that a rotatable 3D sphere would need a whole scene to itself
to read clearly in, and a flat circle is exactly what
``src/manim_helpers.make_gaussian_circle`` already draws for this same
"point charge inside a Gaussian surface" situation — reused here directly,
along with ``make_charge`` for the +Q marker. ``make_gold_sphere`` /
``make_area_patch`` (the 3D builders in the same file) are left alone; they
need a ``ThreeDScene`` camera this track's ``ThemedScene`` does not set up.
There is no reference scan for this diagram (unlike the figures traced in
``tools/figure_from_scan.py``), so its exact layout — angle of P, arrow
lengths, label offsets — is this file's own judgement call, built for
legibility rather than matched to any textbook printing.

Reveal indices below are 0-based positions into ``lines_part1.json``,
matched against its actual timestamps by hand:

    line 14 ( 36.89s)  headline formula lands: Phi = oint E.dS = Q/eps0
    line 18 ( 48.85s)  gloss: E = electric field intensity
    line 19 ( 51.11s)  gloss: dS = small area-element vector
    line 21 ( 56.87s)  gloss: eps0 = 8.85e-12 ... (permittivity of free space)
    line 24 ( 65.69s)  "definition and formula done" -> clear the stage
    line 28 ( 76.37s)  diagram starts: O, +Q
    line 29 ( 78.79s)  R (radius line)
    line 30 ( 80.61s)  P (surface point)
    line 31 ( 82.41s)  the sphere itself (Gaussian surface)
    line 32 ( 83.91s)  "गॉसियन पृष्ठ" tag
    line 33 ( 86.23s)  dS drawn at P, outward
    line 36 ( 93.51s)  E drawn at P, also outward
    line 37 ( 96.21s)  theta named
    line 38 ( 99.49s)  theta settles to "= 0 deg"

From there the diagram shrinks into a left-hand slot (``_split_diagram``)
and the flux integral builds step by step in the space that frees up on the
right, each step revealed at the line that actually speaks it — see
``EQ_STEPS`` below. Only two equation lines are ever on screen at once (the
newest, bright, and the one just before it, dimmed): CLAUDE.md's rule for a
derivation is "never show the final line from the start, dim the previous
step, brighten the new one," and a derivation is a single evolving
statement, not an accumulating list like the sibling file's comparison
table — so unlike that file's cells, superseded steps are allowed to drop
off once a third one arrives, rather than every step staying on screen.

The theta=0 moment is the one place this diagram takes a deliberate liberty:
dS and E are drawn as two separate, exactly PARALLEL outward arrows (offset
sideways along the tangent, never angled apart) because that is what the
caption is actually saying — an angle arc drawn between two truly parallel
arrows has zero opening and is invisible, and faking a visible nonzero arc
to make the angle "look drawable" would show the opposite of what the
narration says. Two arrows pointing the same way, plus a plain "theta = 0
deg" label between them, says it accurately instead.
"""
from manim import *  # noqa: F403
import json
import os as _os
from pathlib import Path as _Path

import numpy as np

from src.manim_helpers import (ThemedScene, fit_caption, norm_point, register_fonts, wrap_measured, mark_group, make_charge, make_gaussian_circle, CHARGE_COLOR, FIELD_COLOR)

INK, DIM, GOLD = "#FFFFFF", "#B9C6DC", "#FFC15C"
GREEN, VIOLET, CYAN = "#7CE0B0", "#C792EA", "#5BC8F9"
DS_COLOR = "#FFC15C"

FONT, FONT_W = "Khand", "BOLD"

PROJECT = _os.getenv("PYQ_PROJECT", "phy-c1-la-02")
PART = int(_os.getenv("PYQ_PART", "1"))
ROOT = _Path(ASSET_ROOT) / "projects" / PROJECT
FIGURES = ROOT / "assets" / "figures"

LINES = json.loads((ROOT / f"lines_part{PART}.json").read_text(encoding="utf-8"))
META = json.loads((ROOT / "meta.json").read_text(encoding="utf-8"))
CLIP_END = float((META.get("clip_end") or {}).get(str(PART), float(LINES[-1]["start"]) + 3.0))

# PYQ_UNTIL=<seconds> stops the scene early, as in the sibling file — useful
# for previewing the diagram build without sitting through the whole clip.
_UNTIL = float(_os.environ.get("PYQ_UNTIL", "0") or 0)

# The CEILING, not the size every caption renders at. `caption()` shrinks
# from here automatically when a line runs long.
CAPTION_SIZE = 55
MAX_CAPTION_LINES = 2
CAPTION_MIN_SIZE = 32
CAPTION_W, CAPTION_TOP = 0.90, 0.090
# STAGE_BOT is derived from where the compositor actually puts the presenter
# (tools/composite.py overlays him at FULL_Y=966 of a 1920-high frame, so his
# head starts at 0.503) — copied verbatim from the sibling file. If the
# compositor's placement ever changes, both files have to change together.
STAGE_TOP, STAGE_BOT, STAGE_W = 0.290, 0.492, 0.86
CAPTION_GAP = 0.30

HILITE = {k: GOLD for k in META.get("hilite", [])}

# --- reveal indices into LINES, matched by hand against lines_part1.json --- #
# idx 6 ("पहले गॉस का प्रमेय...") to idx 14 (the formula itself) is ~21s of
# the theorem being stated in WORDS before its notation is spoken — long
# enough to trip `tools/visual_gaps.py`'s empty-stage check if the stage
# stays blank. A plain topic heading fills it without repeating the
# caption (CLAUDE.md: screen text organises, it does not restate).
HEADING_AT = 6           # "पहले गॉस का प्रमेय और इसकी डेफिनेशन ध्यान"
FORMULA_AT = 14          # "E डॉट dS बराबर Q बटा एप्सिलॉन नॉट" — formula spoken
EDEF_AT = 18             # "E सदिश विद्युत क्षेत्र की तीव्रता है"
DSDEF_AT = 19            # "dS सदिश एक छोटे क्षेत्रफल का सदिश"
EPS_AT = 21              # "विद्युतशीलता का मान 8 दशमलव 8 पाँच..."
FORMULA_CLEAR_AT = 24    # "डेफिनिशन और फॉर्मूला तो हो गया, अब"

DIAG_O_AT = 28           # "मान लेते हैं O पर प्लस Q आवेश"
DIAG_R_AT = 29           # "रखा है और उससे R दूरी पर एक"
DIAG_P_AT = 30           # "बिंदु P है। O को सेंटर मानकर और"
DIAG_CIRCLE_AT = 31      # "R को त्रिज्या लेकर एक गोला बनाते"
DIAG_GAUSS_LABEL_AT = 32 # "हैं—यही हमारा गौसियन पृष्ठ है। अब इस"
DIAG_DS_AT = 33          # "गोलीय पृष्ठ पर एक छोटा area dS लेते"
DIAG_E_AT = 36           # "भी त्रिज्या की दिशा में है, इसी"
DIAG_THETA_AT = 37       # "लिए इनके बीच कोण θ बराबर 0 डिग्री"
DIAG_THETA_SETTLE_AT = 38  # "होगा। अब इलेक्ट्रिक फ्लक्स का छोटा सा"

# The flux-integral derivation, each line keyed to the caption that actually
# speaks it. Kept short and un-simplified-looking on purpose — a student
# copying this down should see the same steps the teacher says out loud,
# not a jump from the dot product straight to the answer.
EQ_STEPS = {
    39: r"d\varphi = \vec{E}\cdot d\vec{S}",
    41: r"d\varphi = E\,dS\cos\theta",
    42: r"\cos 0^\circ = 1 \;\Rightarrow\; d\varphi = E\,dS",
    49: r"\Phi_E = \oint d\varphi",
    52: r"\Phi_E = \oint E\,dS",
    57: r"\Phi_E = E\oint dS",
    59: r"\oint dS = 4\pi r^2",
    62: r"\Phi_E = E\cdot 4\pi r^2",
}
EQ_TAG_AT = 63           # "इसे equation 1 मान लेते हैं"

# --- reveal indices into LINES, matched by hand against lines_part2.json --- #
RECAP_AT = 0             # "पार्ट वन में हमने..." — Part 1's boxed result recap
RECAP_CLEAR_AT = 5       # "तुम्हें याद है न, गॉस प्रमेय" — topic turns to eq. 2
GAUSS2_FORMULA_AT = 7    # "∮ E बराबर Q बटा एप्सिलॉन" — Gauss's theorem written
EQ2_TAG_AT = 8           # "...इसे equation 2 मान लेते हैं"
EQ1_STACK_AT = 10        # "equation 1 और equation 2 में" — eq.1 recap returns
HILITE_COMMON_AT = 11    # "दोनों जगह ∮ E समान हैं" — same flux, two notations
COMBINE_CLEAR_AT = 12    # "इसलिए दोनों को बराबर कर देंगे" — about to equate
COMBINE_EQ_AT = 13       # "यानी E गुणा 4π r² बराबर Q" — combined equation lands
DIVIDE_STEP_AT = 16      # "4π r² से भाग देंगे" — division shown, not skipped
DIVIDE_RESULT_AT = 17    # "तो मिलेगा E बराबर Q बटा" — E = Q/(4*pi*eps0*r^2)
REARRANGE_AT = 20        # "E बराबर 1 बटा 4π एप्सिलॉन" — textbook form
BOX_FINAL_AT = 22        # "इस equation को अच्छे से दिमाग में" — box the take-away
PROPORTION_NOTE_AT = 24  # "कि E बराबर 1 बटा r²" — E is proportional 1/r^2 note


class PyqPart(ThemedScene):
    CAPTION_MODE = "narration"
    STAGE_BAND = (STAGE_TOP, STAGE_BOT)

    # ---- text (copied verbatim from the sibling file) --------------------- #
    def _hl(self, line):
        out = {}
        for w in sorted(HILITE, key=len, reverse=True):
            if w not in line or any(w in k for k in out):
                continue
            for token in line.split():
                if w in token:
                    whole = token.strip(",।?!—:;")
                    if whole and not any(whole in k for k in out):
                        out[whole] = HILITE[w]
        return out

    def _measure(self, line, size):
        cache = self.__dict__.setdefault("_wcache", {})
        k = (line, size)
        if k not in cache:
            cache[k] = Text(line, font=FONT, font_size=size, weight=FONT_W)
        return cache[k]

    def caption(self, text, size=CAPTION_SIZE):
        """Wrap at `size`, then shrink toward CAPTION_MIN_SIZE if that still
        wraps to more than MAX_CAPTION_LINES lines. Copied from the sibling
        file — this is the compositor's caption contract, not this part's."""
        limit = config.frame_width * CAPTION_W
        lines = wrap_measured(text, limit, lambda l: self._measure(l, size))
        while len(lines) > MAX_CAPTION_LINES and size > CAPTION_MIN_SIZE:
            size -= 2
            lines = wrap_measured(text, limit, lambda l: self._measure(l, size))
        g = VGroup(*[Text(l, font=FONT, font_size=size, color=INK,
                          weight=FONT_W, t2c=self._hl(l)) for l in lines])
        g.arrange(DOWN, buff=0.16)
        fit_caption(g, limit)
        g.move_to(norm_point(0.5, CAPTION_TOP))
        g.shift(DOWN * g.height / 2)
        return g

    # ---- layout (copied verbatim from the sibling file) -------------------- #
    def stage_box(self):
        top, bot = norm_point(0.5, STAGE_TOP)[1], norm_point(0.5, STAGE_BOT)[1]
        if getattr(self, "caption_mob", None) is not None:
            top = min(top, self.caption_mob.get_bottom()[1] - CAPTION_GAP)
        return (np.array([0., (top + bot) / 2, 0.]),
                config.frame_width * STAGE_W, top - bot)

    MAX_GROW = 2.2

    def place(self, mob, y=0.5, pad=0.94, grow=True):
        """Fit a block to the stage band — shrinking OR growing it. Copied
        from the sibling file; see its docstring for why growth is capped."""
        c, w, h = self.stage_box()
        if mob.width <= 0 or mob.height <= 0:
            return mob
        s = min((w * pad) / mob.width, (h * pad) / mob.height)
        if s > 1.0:
            s = min(s, self.MAX_GROW) if grow else 1.0
        if abs(s - 1.0) > 0.01:
            mob.scale(s)
        top, bot = c[1] + h / 2, c[1] - h / 2
        cy = top - (top - bot) * y
        mob.move_to([0, max(bot + mob.height / 2,
                            min(top - mob.height / 2, cy)), 0])
        return mob

    def _fit_into(self, mob, box, pad=0.92, grow=True):
        """`place()` generalised to an arbitrary (center, width, height) box
        instead of the whole stage band — needed once the diagram and the
        equation chain have to share the band side by side (see
        `_split_diagram`) rather than each owning the full width in turn."""
        c, w, h = box
        if mob.width <= 0 or mob.height <= 0:
            return mob
        s = min((w * pad) / mob.width, (h * pad) / mob.height)
        if s > 1.0:
            s = min(s, self.MAX_GROW) if grow else 1.0
        if abs(s - 1.0) > 0.01:
            mob.scale(s)
        mob.move_to(c)
        return mob

    def _split_box(self, left_frac=0.40, gap=0.06):
        """The stage band cut into a left slot (the settled diagram) and a
        right slot (the growing equation chain), so neither has to fight the
        other for the centred anchor `place()` would otherwise give both."""
        c, w, h = self.stage_box()
        lw = w * left_frac
        rw = w * (1.0 - left_frac - gap)
        lx = c[0] - w / 2 + lw / 2
        rx = c[0] + w / 2 - rw / 2
        return (np.array([lx, c[1], 0.0]), lw, h), (np.array([rx, c[1], 0.0]), rw, h)

    # ---- timing (copied verbatim from the sibling file) --------------------- #
    def _line(self, text, end=None):
        new = self.caption(text)
        if getattr(self, "caption_mob", None) is not None:
            self.remove(self.caption_mob)
        self.caption_mob = new
        self.add(new)
        self._cap_end = end

    def clear_stage(self, rt=0.30):
        keep = {getattr(self, "caption_mob", None),
                getattr(self, "background", None),
                getattr(self, "chroma_zone", None)}
        doomed = [m for m in self.mobjects if m not in keep and m is not None]
        if doomed:
            self.play(*[FadeOut(m) for m in doomed], run_time=rt)
        self._card_up = False

    def at(self, t):
        left = float(t) - self.renderer.time
        if left > 0.02:
            self.wait(left)

    # ---- the headline formula + its symbol glosses -------------------------- #
    def _show_heading(self):
        """A plain topic heading — not a restatement of the caption — to
        cover the ~21s the theorem is stated in words before its formula is
        spoken. See the note above HEADING_AT."""
        self._heading = Text("गॉस का प्रमेय", font=FONT, weight=FONT_W,
                             font_size=44, color=GOLD)
        self.place(self._heading, pad=0.7)
        self.play(FadeIn(self._heading, shift=UP * 0.15), run_time=0.5)

    def _show_formula(self):
        # Fade the heading out BEFORE writing the formula, never alongside it:
        # place() puts both mobjects in overlapping screen space (the heading
        # centred, the formula at y=0.30), so playing FadeOut(heading) and
        # Write(formula) together left the fading heading double-exposed over
        # the formula's fraction bar for the length of the transition.
        if getattr(self, "_heading", None) is not None:
            self.play(FadeOut(self._heading), run_time=0.35)
            self._heading = None
        self._formula = MathTex(
            r"\Phi = \oint \vec{E}\cdot d\vec{S} = \dfrac{Q}{\varepsilon_0}",
            color=INK,
        )
        self.place(self._formula, y=0.30, pad=0.9)
        self.cue("write")
        self.play(Write(self._formula), run_time=0.9)

    def _def_mob(self, sym_tex, hindi_text):
        """A symbol (LaTeX) beside its meaning (Devanagari) as two SEPARATE
        mobjects arranged with a gap — never one string mixing both, per
        CLAUDE.md's font-mixing rule (Poppins/Khand have no Greek letters or
        vector arrows; LaTeX has no Devanagari)."""
        sym = MathTex(sym_tex, color=GOLD)
        words = Text(f" = {hindi_text}", font=FONT, weight=FONT_W,
                     font_size=26, color=INK)
        return VGroup(sym, words).arrange(RIGHT, buff=0.10)

    def _eps_mob(self):
        sym = MathTex(
            r"\varepsilon_0 = 8.85\times10^{-12}\ \text{C}^2\text{N}^{-1}\text{m}^{-2}",
            color=GOLD,
        ).scale(0.78)
        words = Text("निर्वात की विद्युतशीलता", font=FONT, weight=FONT_W,
                     font_size=22, color=DIM)
        return VGroup(sym, words).arrange(DOWN, buff=0.14)

    def _set_note(self, mob):
        """Swap the small gloss line under the headline formula. Only one is
        ever on screen — E, then dS, then epsilon-nought — each replacing
        the last exactly when its own word is spoken."""
        old = getattr(self, "_note", None)
        self._note = mob
        group = VGroup(*(x for x in (self._formula, self._note) if x is not None))
        group.arrange(DOWN, buff=0.34)
        self.place(group, y=0.42, pad=0.9)
        anims = [FadeIn(mob, shift=UP * 0.12)]
        if old is not None:
            anims.append(FadeOut(old))
        self.play(*anims, run_time=0.4)

    # ---- the derivation diagram: O, +Q, R, P, the sphere, dS, E, theta ----- #
    def _build_diagram(self):
        """Build the whole diagram up front, invisible, and place it ONCE —
        exactly the sibling file's `_build_table` technique — so nothing
        re-flows once a piece becomes visible. Only O/+Q are revealed here;
        every later index in DIAG_*_AT just raises one more piece's opacity.
        """
        O = LEFT * 0.55
        RAD = 1.05
        ANG = 34 * PI / 180
        OUT = np.array([np.cos(ANG), np.sin(ANG), 0.0])
        PERP = np.array([-np.sin(ANG), np.cos(ANG), 0.0])
        P = O + OUT * RAD

        # make_charge's glow ring is deliberately translucent (0.18) against
        # the core's solid 1.0 — a blanket `charge.set_opacity(1.0)` on
        # reveal would flatten that glow to fully opaque, so its three
        # pieces are tracked separately, the same fix already needed for
        # the circle's disc-vs-ring pair below.
        charge = make_charge(center=O, radius=0.16, color=CHARGE_COLOR)
        charge_glow, charge_core, charge_plus = charge
        o_label = MathTex("O", color=INK).scale(0.6)
        o_label.move_to(O + DOWN * 0.34 + LEFT * 0.05)
        q_label = MathTex("+Q", color=CHARGE_COLOR).scale(0.6)
        q_label.move_to(O + UP * 0.34 + LEFT * 0.12)

        disc, ring = make_gaussian_circle(center=O, radius=RAD, color="#BFE9FF")
        gauss_ang = ANG + 145 * PI / 180
        gauss_label = Text("गॉसियन पृष्ठ", font=FONT, weight=FONT_W,
                           font_size=20, color="#BFE9FF")
        gauss_label.move_to(O + (RAD + 0.32) * np.array(
            [np.cos(gauss_ang), np.sin(gauss_ang), 0.0]))

        r_line = Line(O, P, color=DIM, stroke_width=2.5)
        r_label = MathTex("R", color=GOLD).scale(0.6)
        r_label.move_to(r_line.point_from_proportion(0.5) + PERP * 0.22)

        p_dot = Dot(P, radius=0.045, color=INK)
        p_label = MathTex("P", color=INK).scale(0.6)
        p_label.move_to(P + PERP * 0.40)

        # dS and E: two separate, exactly PARALLEL outward arrows (offset
        # sideways along the tangent, never angled apart) — see the module
        # docstring's note on why theta is shown this way rather than with
        # an angle arc.
        ds_start = P - PERP * 0.10
        ds_end = ds_start + OUT * 0.34
        ds_arrow = Arrow(ds_start, ds_end, buff=0, color=DS_COLOR,
                         stroke_width=4, max_tip_length_to_length_ratio=0.36)
        ds_label = MathTex(r"d\vec{S}", color=DS_COLOR).scale(0.5)
        ds_label.move_to(ds_end + OUT * 0.20)

        e_start = P + PERP * 0.10
        e_end = e_start + OUT * 0.62
        e_arrow = Arrow(e_start, e_end, buff=0, color=FIELD_COLOR,
                        stroke_width=5, max_tip_length_to_length_ratio=0.22)
        e_label = MathTex(r"\vec{E}", color=FIELD_COLOR).scale(0.6)
        e_label.move_to(e_end + OUT * 0.22)

        theta_pt = P + OUT * 0.06
        theta_label = MathTex(r"\theta", color=GOLD).scale(0.5).move_to(theta_pt)
        theta_settled = MathTex(r"\theta = 0^\circ", color=GOLD).scale(0.5)
        theta_settled.move_to(theta_pt)

        whole = VGroup(disc, ring, r_line, r_label, charge, o_label, q_label,
                       p_dot, p_label, gauss_label, ds_arrow, ds_label,
                       e_arrow, e_label, theta_label, theta_settled)
        for m in whole:
            m.set_opacity(0.0)
        mark_group(whole)
        self.place(whole, pad=0.92)
        self.add(whole)

        self._diagram = whole
        self._diag = dict(
            disc=disc, ring=ring, r_line=r_line, r_label=r_label,
            charge=charge, o_label=o_label, q_label=q_label,
            p_dot=p_dot, p_label=p_label, gauss_label=gauss_label,
            ds_arrow=ds_arrow, ds_label=ds_label, e_arrow=e_arrow,
            e_label=e_label, theta_label=theta_label,
            theta_settled=theta_settled,
        )

        self.cue("pop")
        self.play(charge_glow.animate.set_opacity(0.18),
                  charge_core.animate.set_opacity(1.0),
                  charge_plus.animate.set_opacity(1.0),
                  o_label.animate.set_opacity(1.0),
                  q_label.animate.set_opacity(1.0), run_time=0.5)

    def _reveal(self, *keys, run_time=0.4):
        self.play(*[self._diag[k].animate.set_opacity(1.0) for k in keys],
                  run_time=run_time)

    def _split_diagram(self):
        """Shrink the now-settled diagram into a slot on the left, freeing
        the right for the flux-integral steps. Called once, the first time
        an equation step is revealed (EQ_STEPS' lowest key, 39)."""
        left, right = self._split_box()
        c, w, h = left
        s = min((w * 0.90) / self._diagram.width,
                (h * 0.90) / self._diagram.height, 1.0)
        self.play(self._diagram.animate.scale(s).move_to(c), run_time=0.6)

        _, ew, eh = right
        self._eq_box = right
        # Two FIXED anchor points inside the right slot rather than
        # re-`arrange`-ing the pair every step: a step's box only ever
        # changes colour and fades in/out, it never has to fight the other
        # slot for room, so nothing jumps sideways as the chain grows.
        self._eq_cur_pt = right[0] + DOWN * eh * 0.10
        self._eq_prev_pt = right[0] + UP * eh * 0.26
        self._eq_w = ew * 0.90

    # ---- the flux-integral chain: at most two lines on screen at once ------ #
    def _eq_step(self, tex):
        if getattr(self, "_eq_box", None) is None:
            self._split_diagram()
        new = MathTex(tex, color=INK).scale(1.15)
        if new.width > self._eq_w:
            new.scale(self._eq_w / new.width)
        new.move_to(self._eq_cur_pt)

        anims = [FadeIn(new, shift=UP * 0.18)]
        if getattr(self, "_eq_prev", None) is not None:
            anims.append(FadeOut(self._eq_prev))     # oldest falls off
        if getattr(self, "_eq_cur", None) is not None:
            cur = self._eq_cur
            anims.append(cur.animate.set_color(DIM).move_to(self._eq_prev_pt))
        self._eq_prev, self._eq_cur = getattr(self, "_eq_cur", None), new
        self.play(*anims, run_time=0.45)

    def _tag_equation1(self, target=None, prev=None, label="समीकरण 1"):
        """Box a settled equation and stamp it with a take-away label.
        Started life hardcoded to Part 1's single call site (box
        ``self._eq_cur``, label "समीकरण 1"); generalised so Part 2 can draw
        "समीकरण 2" with the exact same visual language, and box its final,
        un-numbered E formula with no label at all (``label=None`` skips the
        tag text and draws just the box). ``prev`` is whatever dimmed
        mobject should fade out alongside — passed explicitly rather than
        read off a fixed attribute name, because Part 1 and Part 2 keep
        their equation chains in different attributes (``_eq_prev`` vs
        ``_eq2_prev``) and this helper has no business knowing which."""
        if target is None:
            target = self._eq_cur
        box = SurroundingRectangle(target, color=GOLD, buff=0.18,
                                   stroke_width=3)
        anims = [Create(box)]
        tag = None
        if label:
            tag = Text(label, font=FONT, weight=FONT_W, font_size=22,
                       color=GOLD)
            tag.next_to(box, UP, buff=0.14)
            anims.append(FadeIn(tag, shift=UP * 0.08))
        if prev is not None:
            anims.append(FadeOut(prev))
        self.cue("ding")
        self.play(*anims, run_time=0.5)
        return box, tag

    # ---- Part 2: recalling eq. 2, equating it with eq. 1, isolating E ------- #
    def _show_recap(self):
        """A light callback to Part 1's boxed result while the presenter
        says "we found this flux in part 1, now we'll equate it" — the
        transcript never names the diagram, only the equation, so this
        recaps just the equation, small, and is gone again by the time the
        topic actually turns to restating Gauss's theorem (RECAP_CLEAR_AT).
        Deliberately light: CLAUDE.md's own rule is that "no graphic" is a
        valid answer, and a full diagram rebuild here would only repeat
        what Part 1 already showed once."""
        tex = MathTex(r"\Phi_E = E\cdot4\pi r^2", color=INK).scale(0.85)
        box = SurroundingRectangle(tex, color=GOLD, buff=0.16, stroke_width=2.5)
        tag = Text("पार्ट 1 का परिणाम", font=FONT, weight=FONT_W,
                   font_size=20, color=DIM)
        tag.next_to(box, UP, buff=0.12)
        self._recap = VGroup(tex, box, tag)
        self.place(self._recap, y=0.38, pad=0.75)
        self.play(FadeIn(self._recap, shift=UP * 0.12), run_time=0.4)

    def _clear_recap(self):
        if getattr(self, "_recap", None) is not None:
            self.play(FadeOut(self._recap), run_time=0.3)
            self._recap = None

    def _show_gauss2_formula(self):
        """Gauss's theorem, written again exactly as Part 1 wrote it the
        first time — same tex, same style — since this is the same
        equation being recalled, not a new one."""
        self._eq2_formula = MathTex(
            r"\oint \vec{E}\cdot d\vec{S} = \dfrac{Q}{\varepsilon_0}",
            color=INK,
        )
        # grow=False: place() growing this to fill the band left zero margin
        # for the box `_tag_equation1` draws around it a few lines later —
        # the box's buff pushed straight through the band's top edge.
        self.place(self._eq2_formula, y=0.45, pad=0.85, grow=False)
        self.cue("write")
        self.play(Write(self._eq2_formula), run_time=0.8)

    def _stack_eq1_above(self):
        """The pedagogical crux, made visible: समीकरण 1 (dimmed, this
        part's own recap) sits stacked above the just-tagged समीकरण 2 so
        the "these are the same flux" claim the caption is about to make is
        something the viewer can look at, not just take on faith."""
        eq1 = MathTex(r"\Phi_E = E\cdot4\pi r^2", color=DIM).scale(0.8)
        tag1 = Text("समीकरण 1", font=FONT, weight=FONT_W, font_size=18,
                    color=DIM)
        pair = VGroup(tag1, eq1).arrange(RIGHT, buff=0.16)
        pair.next_to(self._eq2_group, UP, buff=0.28)
        self._eq1_pair = pair
        self.play(FadeIn(pair, shift=UP * 0.12), run_time=0.4)

    def _highlight_common_flux(self):
        """Both equations glow together — Φ_E on one is DEFINED as
        ∮E⃗·dS⃗ on the other, so this is one flux wearing two notations,
        which is exactly what licenses equating their two sides next."""
        targets = [m for m in (getattr(self, "_eq1_pair", None),
                               getattr(self, "_eq2_formula", None))
                   if m is not None]
        if targets:
            self.play(*[Indicate(m, color=GOLD, scale_factor=1.06)
                        for m in targets], run_time=0.7)

    def _clear_paired_equations(self):
        """Fade समीकरण 1 and समीकरण 2 out TOGETHER, before the combined
        line is written next beat — never simultaneously with that Write,
        per this file's own rule in `_show_formula`."""
        doomed = [m for m in (getattr(self, "_eq1_pair", None),
                              getattr(self, "_eq2_group", None))
                  if m is not None]
        if doomed:
            self.play(*[FadeOut(m) for m in doomed], run_time=0.35)
        self._eq1_pair = None
        self._eq2_group = None

    def _eq2_anchors(self):
        if getattr(self, "_eq2_cur_pt", None) is not None:
            return
        c, w, h = self.stage_box()
        # Part 2's chain runs through two side-by-side \dfrac fractions
        # (DIVIDE_STEP_AT) that render ~1.1-1.35 units tall -- much taller
        # than Part 1's single-line steps this file's original 0.08/0.30
        # split was sized for. That gap (~1.09 units) was shorter than two
        # such equations' combined half-heights, so the incoming bright
        # equation and the outgoing dimmed one visibly overlapped, and the
        # dimmed one's own top edge poked out of the stage band. Widened the
        # split and shrink the dimmed copy further (see `_eq_center_step`);
        # verified against actual rendered MathTex heights before, not after,
        # touching the render (`_smoketest/measure4.py`).
        self._eq2_cur_pt = c + DOWN * h * 0.14
        self._eq2_prev_pt = c + UP * h * 0.32
        self._eq2_w = w * 0.82

    def _eq_center_step(self, tex, scale=0.95):
        """Part 2's equation chain: the same "newest line bright, previous
        line dimmed above it, oldest drops off" rule as Part 1's
        `_eq_step`, but anchored to the CENTRE of the stage band instead of
        a left/right split — Part 2 has no diagram to share the band with,
        so splitting it here would just leave a dead column on one side."""
        self._eq2_anchors()
        new = MathTex(tex, color=INK).scale(scale)
        if new.width > self._eq2_w:
            new.scale(self._eq2_w / new.width)
        new.move_to(self._eq2_cur_pt)

        anims = [FadeIn(new, shift=UP * 0.18)]
        if getattr(self, "_eq2_prev", None) is not None:
            anims.append(FadeOut(self._eq2_prev))       # oldest falls off
        if getattr(self, "_eq2_cur", None) is not None:
            cur = self._eq2_cur
            # Shrink the demoted line too -- at full size even the widened
            # split above isn't enough room for the tallest fraction pairs.
            anims.append(cur.animate.set_color(DIM).scale(0.8)
                         .move_to(self._eq2_prev_pt))
        self._eq2_prev, self._eq2_cur = getattr(self, "_eq2_cur", None), new
        self.play(*anims, run_time=0.45)

    # ---- the walk ------------------------------------------------------------ #
    def construct(self):
        register_fonts()
        self.caption_mob = None
        self._wcache = {}
        self.stage_mobs = []
        self._heading = None
        self._formula = None
        self._note = None
        self._diagram = None
        self._eq_box = None
        self._eq_prev = None
        self._eq_cur = None
        self._recap = None
        self._eq2_formula = None
        self._eq2_group = None
        self._eq1_pair = None
        self._eq2_cur_pt = None
        self._eq2_prev = None
        self._eq2_cur = None
        self._final_box = None

        no_card = str(PART) in set(META.get("no_card", []))
        card_at = float(LINES[0]["start"])
        if not no_card:
            _sheet = ROOT / "assets" / "design" / "question_sheet.png"
            self.question_card(META["question"], META.get("highlight", ""),
                               META.get("years", ""),
                               sheet=_sheet if _sheet.is_file() else None)
        self.at(card_at)

        _cl = META.get("card_lines", 0)
        card_until = -1 if no_card else int(
            _cl[str(PART)] if isinstance(_cl, dict) else _cl)

        for i, line in enumerate(LINES):
            self.at(max(0.0, float(line["start"]) - 0.35))
            if i == card_until:
                self.clear_stage()

            if PART == 1:
                if i == HEADING_AT:
                    self._show_heading()
                elif i == FORMULA_AT:
                    self._show_formula()
                elif i == EDEF_AT:
                    self._set_note(self._def_mob(r"\vec{E}", "विद्युत क्षेत्र की तीव्रता"))
                elif i == DSDEF_AT:
                    self._set_note(self._def_mob(r"d\vec{S}", "क्षेत्रफल अवयव सदिश"))
                elif i == EPS_AT:
                    self._set_note(self._eps_mob())
                elif i == FORMULA_CLEAR_AT:
                    self.clear_stage()
                    self._formula = None
                    self._note = None
                elif i == DIAG_O_AT:
                    self._build_diagram()
                elif i == DIAG_R_AT:
                    self._reveal("r_line", "r_label")
                elif i == DIAG_P_AT:
                    self._reveal("p_dot", "p_label")
                elif i == DIAG_CIRCLE_AT:
                    self.cue("whoosh")
                    self.play(Create(self._diag["ring"]),
                              self._diag["disc"].animate.set_opacity(0.10),
                              run_time=0.6)
                elif i == DIAG_GAUSS_LABEL_AT:
                    self._reveal("gauss_label")
                elif i == DIAG_DS_AT:
                    self._reveal("ds_arrow", "ds_label")
                elif i == DIAG_E_AT:
                    self._reveal("e_arrow", "e_label")
                elif i == DIAG_THETA_AT:
                    self._reveal("theta_label")
                elif i == DIAG_THETA_SETTLE_AT:
                    self.cue("reveal")
                    self.play(self._diag["theta_label"].animate.set_opacity(0.0),
                              self._diag["theta_settled"].animate.set_opacity(1.0),
                              run_time=0.4)
                elif i in EQ_STEPS:
                    self._eq_step(EQ_STEPS[i])
                elif i == EQ_TAG_AT:
                    self._tag_equation1(prev=self._eq_prev)
                    self._eq_prev = None

            elif PART == 2:
                if i == RECAP_AT:
                    self._show_recap()
                elif i == RECAP_CLEAR_AT:
                    self._clear_recap()
                elif i == GAUSS2_FORMULA_AT:
                    self._show_gauss2_formula()
                elif i == EQ2_TAG_AT:
                    box, tag = self._tag_equation1(
                        target=self._eq2_formula, label="समीकरण 2")
                    self._eq2_group = VGroup(self._eq2_formula, box, tag)
                elif i == EQ1_STACK_AT:
                    self._stack_eq1_above()
                elif i == HILITE_COMMON_AT:
                    self._highlight_common_flux()
                elif i == COMBINE_CLEAR_AT:
                    self._clear_paired_equations()
                elif i == COMBINE_EQ_AT:
                    self.cue("pop")
                    self._eq_center_step(r"E\cdot4\pi r^2 = \dfrac{Q}{\varepsilon_0}")
                elif i == DIVIDE_STEP_AT:
                    self._eq_center_step(
                        r"\dfrac{E\cdot4\pi r^2}{4\pi r^2} = \dfrac{Q}{4\pi r^2\,\varepsilon_0}")
                elif i == DIVIDE_RESULT_AT:
                    self._eq_center_step(r"E = \dfrac{Q}{4\pi\varepsilon_0 r^2}")
                elif i == REARRANGE_AT:
                    self._eq_center_step(
                        r"E = \dfrac{1}{4\pi\varepsilon_0}\cdot\dfrac{Q}{r^2}")
                elif i == BOX_FINAL_AT:
                    self._final_box, _ = self._tag_equation1(
                        target=self._eq2_cur, prev=self._eq2_prev, label=None)
                    self._eq2_prev = None
                elif i == PROPORTION_NOTE_AT:
                    note = MathTex(r"E \propto \dfrac{1}{r^2}", color=GOLD).scale(0.8)
                    # The final box sits low in the band (its equation's
                    # cur_pt is below centre -- see `_eq2_anchors`), so a
                    # \dfrac note hung BELOW it by a fixed buff pushed clean
                    # through the band's bottom edge -- only ~0.33 units of
                    # headroom was left there. The box doesn't fill the
                    # band's width, though, so the note sits beside it
                    # instead, where there is ~1.8 units of clear room.
                    note.next_to(self._final_box, RIGHT, buff=0.3)
                    self.play(FadeIn(note, shift=RIGHT * 0.1), run_time=0.4)

            if _UNTIL and float(line["start"]) > _UNTIL:
                break
            self.at(float(line["start"]))
            if i >= card_until:
                self._line(line["text"], line.get("end"))
        self.at(CLIP_END)
        self.report_layout()
