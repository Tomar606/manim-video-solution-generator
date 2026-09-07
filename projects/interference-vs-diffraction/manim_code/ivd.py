"""Interference vs Diffraction — the standard PYQ portrait track (see
projects/_pyq_template/scene.py), driven by a REAL recorded presenter clip
(inbox/IvD_final_1080p.mp4) instead of synthesized narration.

    IVD_UNTIL=<seconds> manim -qh scene_composed.py IvdScene

Content lives in `beats_part1.json` (a list of `{"at": <caption line index>,
"type": ...}` blocks), exactly like the PYQ track: `at` indexes the caption
track (`lines_part1.json`, itself converted from the recorded clip's own
SRT — never from a script), so every block lands on the words that describe
it however long the presenter actually talks.

The recorded clip is landscape (HeyGen always delivers landscape), but that is
normal for this track: tools/avatar_crop.py crops a portrait-appropriate
region out of it and tools/composite.py keys that into the BOTTOM band of a
1080x1920 frame, exactly as every other PYQ project does. This file used to
render its own frame in landscape with the presenter keyed into the right
half instead — a one-off layout that does not match the rest of the track and
was reverted; geometry here is now identical to the portrait template.
"""
from manim import *  # noqa: F403
import json
import os as _os
from pathlib import Path as _Path

import numpy as np

from src.manim_helpers import (ThemedScene, fit_caption, norm_point,
                               register_fonts, wrap_measured)

INK, DIM, GOLD = "#FFFFFF", "#B9C6DC", "#FFC15C"
CYAN, VIOLET = "#5BC8F9", "#C792EA"

FONT, FONT_W = "Khand", "BOLD"
# Same full-width stage as projects/_pyq_template/scene.py. CAPTION_SIZE here
# is a CEILING, not the size every caption renders at — caption() below
# shrinks toward CAPTION_MIN_SIZE automatically when a line wraps past
# MAX_CAPTION_LINES, which is what a real-speech transcript needs (sentences
# run far longer than a TTS-engineered script ever would).
CAPTION_SIZE, CAPTION_W, CAPTION_TOP = 55, 0.90, 0.090
MAX_CAPTION_LINES = 2
CAPTION_MIN_SIZE = 32
# STAGE_BOT is derived from where tools/composite.py actually puts the
# presenter: FULL_Y anchors his head at ~0.503 of a 1920-high frame. Keep this
# above that with a margin, same as the portrait template.
STAGE_TOP, STAGE_BOT, STAGE_W = 0.290, 0.492, 0.86
CAPTION_GAP = 0.30
CENTER_X = 0.5           # normalized x of the FULL frame's own center

ROOT = _Path(ASSET_ROOT) / "projects" / "interference-vs-diffraction"
PART = int(_os.getenv("IVD_PART", "1"))
_UNTIL = float(_os.environ.get("IVD_UNTIL", "0") or 0)

LINES = json.loads((ROOT / f"lines_part{PART}.json").read_text(encoding="utf-8"))
BEATS = json.loads((ROOT / f"beats_part{PART}.json").read_text(encoding="utf-8"))
META = json.loads((ROOT / "meta.json").read_text(encoding="utf-8"))
CLIP_END = float((META.get("clip_end") or {}).get(str(PART), float(LINES[-1]["start"]) + 2.0))

HILITE = {k: GOLD for k in META.get("hilite", [])}


class IvdScene(ThemedScene):
    CAPTION_MODE = "narration"
    STAGE_BAND = (STAGE_TOP, STAGE_BOT)

    # ---- text ----------------------------------------------------------- #
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
        """Shrinks toward CAPTION_MIN_SIZE when `text` wraps past
        MAX_CAPTION_LINES — see projects/_pyq_template/scene.py's caption()
        for why: this clip's lines come from real recorded speech, which
        varies in length far more than a written script ever would."""
        limit = config.frame_width * CAPTION_W
        lines = wrap_measured(text, limit, lambda l: self._measure(l, size))
        while len(lines) > MAX_CAPTION_LINES and size > CAPTION_MIN_SIZE:
            size -= 2
            lines = wrap_measured(text, limit, lambda l: self._measure(l, size))
        g = VGroup(*[Text(l, font=FONT, font_size=size, color=INK,
                          weight=FONT_W, t2c=self._hl(l)) for l in lines])
        g.arrange(DOWN, buff=0.14)
        fit_caption(g, limit)
        g.move_to(norm_point(CENTER_X, CAPTION_TOP))
        g.shift(DOWN * g.height / 2)
        return g

    # ---- layout ----------------------------------------------------------- #
    def stage_box(self):
        top, bot = norm_point(CENTER_X, STAGE_TOP)[1], norm_point(CENTER_X, STAGE_BOT)[1]
        if getattr(self, "caption_mob", None) is not None:
            top = min(top, self.caption_mob.get_bottom()[1] - CAPTION_GAP)
        cx = norm_point(CENTER_X, 0.0)[0]
        return (np.array([cx, (top + bot) / 2, 0.]),
                config.frame_width * STAGE_W, top - bot)

    MAX_GROW = 2.0

    def place(self, mob, y=0.5, pad=0.92, grow=True):
        """Fit a block to the LEFT-HALF stage band, centered on its own x.

        Identical to the portrait template's place() except the final
        move_to uses the stage's own center x (`c[0]`) instead of a
        hardcoded 0 — the portrait version centers on the full frame, which
        would straddle the chroma boundary here and put half of every block
        on top of the presenter.
        """
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
        mob.move_to([c[0], max(bot + mob.height / 2,
                               min(top - mob.height / 2, cy)), 0])
        return mob

    def clamp_to_band(self, mob):
        top = norm_point(CENTER_X, STAGE_TOP)[1]
        bot = norm_point(CENTER_X, STAGE_BOT)[1]
        if getattr(self, "caption_mob", None) is not None:
            top = min(top, self.caption_mob.get_bottom()[1] - CAPTION_GAP)
        low, high = mob.get_bottom()[1], mob.get_top()[1]
        if low < bot:
            mob.shift(UP * (bot - low))
        elif high > top:
            mob.shift(DOWN * (high - top))
        return mob

    # ---- the one diagram this topic needs ----------------------------------- #
    def fringes_diagram(self):
        """Two labelled rows of bars: what the screen actually looks like.

        The bar HEIGHT and OPACITY together carry both facts the narration
        makes about the pattern — interference fringes are equal width and
        equal brightness; diffraction's central fringe is both the widest
        and the brightest, tapering symmetrically outward. Baking both facts
        into one static diagram (rather than animating brightness in as a
        second step) is deliberate: they are true at the same time, so
        showing them at the same time is more honest than pretending shape
        arrives before brightness does.
        """
        def row(heights, opacities, colour):
            bars = VGroup(*[
                Rectangle(width=0.40, height=h, stroke_width=0,
                         fill_color=colour, fill_opacity=o)
                for h, o in zip(heights, opacities)
            ])
            bars.arrange(RIGHT, buff=0.16, aligned_edge=DOWN)
            return bars

        inter_row = row([0.85] * 7, [0.85] * 7, CYAN)
        diff_row = row([0.30, 0.50, 0.80, 1.30, 0.80, 0.50, 0.30],
                       [0.35, 0.50, 0.70, 1.00, 0.70, 0.50, 0.35], GOLD)

        inter_lbl = Text("Interference", font=FONT, font_size=34,
                         color=CYAN, weight="BOLD")
        diff_lbl = Text("Diffraction", font=FONT, font_size=34,
                        color=GOLD, weight="BOLD")

        inter_block = VGroup(inter_lbl, inter_row).arrange(DOWN, buff=0.30)
        diff_block = VGroup(diff_lbl, diff_row).arrange(DOWN, buff=0.30)
        whole = VGroup(inter_block, diff_block).arrange(DOWN, buff=0.70)
        return self.place(whole)

    def build_beat(self, spec):
        t = spec["type"]
        if t == "compare":
            return self.beat_compare(spec["left"], spec["right"])
        if t == "fringes":
            return self.fringes_diagram()
        raise ValueError(f"unknown beat type: {t}")

    # ---- timing ------------------------------------------------------------ #
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

    def at(self, t):
        left = float(t) - self.renderer.time
        if left > 0.02:
            self.wait(left)

    def construct(self):
        register_fonts()
        self.caption_mob = None
        self._wcache = {}
        self.stage_mobs = []

        beats = {int(b["at"]): b for b in BEATS}
        for i, line in enumerate(LINES):
            self.at(max(0.0, float(line["start"]) - 0.35))
            if i in beats:
                self.clear_stage()
                spec = beats[i]
                built = self.build_beat(spec)
                self.stage_mobs.append(built)
                self.play(FadeIn(built, shift=UP * 0.12), run_time=0.35)
                self.audit_layout(f"beat@{i}")
            if _UNTIL and float(line["start"]) > _UNTIL:
                break
            self.at(float(line["start"]))
            self._line(line["text"], line.get("end"))
        self.at(CLIP_END)
        self.report_layout()
