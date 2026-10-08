"""Compose a project's scene in the REFERENCE LOOK (22 Sept 2026).

    python tools/make_ref_scene.py <slug> [<slug> ...]

Takes the newest composed PYQ scene (the one every recent chemistry video was
built from), patches its main loop for the reference reel's rules, and appends
projects/_pyq_template/ref_look.py, which carries the new beat types and the
caption. Writes projects/<slug>/manim_code/pyq_composed.py.

The loop patches, each asserted so a changed base fails loudly instead of
silently rendering the old look:

  * CAPTIONS STAY ON under a graphic (the reference never hides them).
  * a beat marked "keep": true is laid UNDER what is on the stage instead of
    replacing it (fact pills under a finished table).
  * beats can schedule work on later caption lines (`_later`), which is how a
    table fills row by row and a diagram gains its labels as they are named.
  * the question card is laid out for a presenter who never shrinks: heading
    "MP Board · कक्षा 12", sheet and year badge all above his head.
  * THE BACKDROP IS THE PROJECT'S OWN SUBJECT'S. The base scene belongs to a
    chemistry project and the THEME — plate, palette, accents — travels with
    the file, so every project composed here inherited flasks and test tubes.
    Four biology videos shipped that way before anyone noticed. The subject is
    in the project's meta.json, so it is read and the theme replaced; tools/
    plate_gate.py then refuses a mismatch before a single frame is rendered.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
BASE = ROOT / "projects" / "che-c3-sa-10" / "manim_code" / "pyq_composed.py"
# The same mapping tools/recompose.py uses.
SUBJECT_THEME = {"physics": "physics-plate", "chemistry": "chemistry-bg",
                 "biology": "biology-bg", "maths": "maths-bg",
                 "mathematics": "maths-bg"}


def retheme(src: str, slug: str) -> str:
    """Point the composed scene at the subject's own theme."""
    import json
    import re
    from dataclasses import asdict, is_dataclass
    meta_p = ROOT / "projects" / slug / "meta.json"
    if not meta_p.is_file():
        return src
    subject = str(json.loads(meta_p.read_text(encoding="utf-8")).get("subject", "")).strip()
    key = SUBJECT_THEME.get(subject.lower())
    if not key:
        print(f"    {slug}: subject {subject!r} has no theme of its own — "
              f"leaving the base scene's")
        return src
    from src.themes import THEMES
    t = THEMES[key]
    d = asdict(t) if is_dataclass(t) else dict(t.__dict__)
    d = {k: (v.value if hasattr(v, "value") else v) for k, v in d.items()}
    m = re.search(r"^THEME = \{.*?\}$", src, flags=re.M | re.S)
    if not m:
        return src
    was = re.search(r"'background_image':\s*'([^']*)'", m.group(0))
    if was and Path(was.group(1)).name != Path(d["background_image"]).name:
        print(f"    {slug}: {subject} -> {Path(was.group(1)).name} "
              f"becomes {Path(d['background_image']).name}")
    return src[:m.start()] + "THEME = " + repr(d) + src[m.end():]
LOOK = ROOT / "projects" / "_pyq_template" / "ref_look.py"

PATCHES = [
    # 0. the conductor figure PHY-C3-SA-04 is built around
    ("""        elif kind == "membrane":""",
     '        elif kind == "wire_la":\n            # THE FIGURE THIS QUESTION IS ABOUT: a conductor with its length and\n            # its cross-section drawn, because every row of the answer is about\n            # those two things.\n            #\n            # The first cut of this video was a table and a formula and nothing\n            # else — correct, and nothing to look at. The third row is the one\n            # students get wrong (rho does NOT depend on l and A, R does), and a\n            # table can only assert that. Here it is shown: the bar stretches and\n            # R rises, the bar thickens and R falls, and rho never moves.\n            #\n            # Grey metal, not a house accent — the classical convention for a\n            # conductor (memory: use-classical-conventions).\n            spec = getattr(self, "_graph_spec", {}) or {}\n            _wire_tag = f"wire_la_{id(self)}"      # one tag for every part, incl. replacements\n            BODY_L, BODY_H, DEPTH = 3.9, 1.05, 0.52\n            METAL, EDGE = "#9AA6B2", "#D7DEE6"\n\n            body = Rectangle(width=BODY_L, height=BODY_H, stroke_width=3)\n            body.set_stroke(EDGE).set_fill(METAL, 0.85)\n            # the end face IS the cross-section, so it is drawn as a face and\n            # shaded differently rather than merely labelled\n            face = Polygon([0, BODY_H / 2, 0], [DEPTH, BODY_H / 2 + DEPTH * 0.55, 0],\n                           [DEPTH, -BODY_H / 2 + DEPTH * 0.55, 0], [0, -BODY_H / 2, 0],\n                           stroke_width=3)\n            face.set_stroke(EDGE).set_fill(GOLD, 0.30)\n            face.shift(RIGHT * BODY_L / 2)\n            top = Polygon([-BODY_L / 2, BODY_H / 2, 0], [BODY_L / 2, BODY_H / 2, 0],\n                          [BODY_L / 2 + DEPTH, BODY_H / 2 + DEPTH * 0.55, 0],\n                          [-BODY_L / 2 + DEPTH, BODY_H / 2 + DEPTH * 0.55, 0],\n                          stroke_width=3)\n            top.set_stroke(EDGE).set_fill(METAL, 0.55)\n            bar = VGroup(body, top, face)\n\n            # l, under the bar: a drawn dimension line. No arrow glyph exists in\n            # the house face (CLAUDE.md), so the heads are triangles.\n            def dim_line(x0, x1, y):\n                sh = Line([x0, y, 0], [x1, y, 0]).set_stroke(GOLD, 3)\n                h = VGroup()\n                for x, d in ((x0, 1), (x1, -1)):\n                    t = Triangle().set_fill(GOLD, 1).set_stroke(width=0)\n                    t.set_height(0.17).rotate(-PI / 2 * d).move_to([x, y, 0])\n                    h.add(t)\n                return VGroup(sh, h)\n            dim = dim_line(-BODY_L / 2, BODY_L / 2, -BODY_H / 2 - 0.42)\n            l_lab = MathTex("l", color=GOLD, font_size=46)\n            l_lab.next_to(dim, DOWN, buff=0.12)\n\n            a_lab = MathTex("A", color=GOLD, font_size=46)\n            a_lab.next_to(face, RIGHT, buff=0.30)\n            a_tick = Line(face.get_right() + RIGHT * 0.05, a_lab.get_left() + LEFT * 0.06)\n            a_tick.set_stroke(GOLD, 2.4)\n\n            cur = VGroup()\n            for i in range(3):\n                t = Triangle().set_fill(CYAN, 1).set_stroke(width=0)\n                t.set_height(0.19).rotate(-PI / 2)\n                t.move_to([-BODY_L / 2 - 0.95 + i * 0.30, 0, 0])\n                cur.add(t)\n\n            fig = VGroup(bar, dim, l_lab, a_lab, a_tick, cur)\n            TOPR, BOTR = 300, 930\n            k = config.frame_height / config.pixel_height\n            top_y = (config.pixel_height / 2 - TOPR) * k\n            bot_y = (config.pixel_height / 2 - BOTR) * k\n            sc = min(config.frame_width * 0.80 / fig.width,\n                     (top_y - bot_y) * 0.62 / fig.height)\n            fig.scale(sc).move_to([0, (top_y + bot_y) / 2 + (top_y - bot_y) * 0.14, 0])\n\n            # the two readouts: what MOVES and what does not\n            def readout(sym, word, colour):\n                m = MathTex(sym, color=colour, font_size=40)\n                w = Text(word, font=FONT, font_size=24, color=colour)\n                g = VGroup(m, w).arrange(RIGHT, buff=0.18)\n                box = RoundedRectangle(corner_radius=0.10, width=g.width + 0.42,\n                                       height=g.height + 0.30)\n                box.set_stroke(colour, 2).set_fill("#0E1A24", 0.85)\n                g.move_to(box)\n                return VGroup(box, g)\n            r_out = readout("R", "बढ़ा", GOLD)\n            rho_out = readout(r"\\rho", "अपरिवर्तित", CYAN)\n            pair = VGroup(r_out, rho_out).arrange(RIGHT, buff=0.34)\n            pair.scale(min(1.0, config.frame_width * 0.80 / pair.width))\n            pair.next_to(fig, DOWN, buff=0.34)\n            pair.set_opacity(0)\n            fig.add(pair)\n\n            # l GROWS -> R grows, rho does not. Then A grows -> R falls, rho\n            # still does not. Scheduled on the captions that say each one.\n            def stretch():\n                self.cue("reveal", gain=-3.0)\n                self.play(bar.animate.stretch(1.45, 0).shift(RIGHT * 0.0),\n                          dim.animate.stretch(1.45, 0),\n                          pair.animate.set_opacity(1), run_time=0.8)\n                for m in (fig, bar, dim, pair):\n                    mark_group(m, _wire_tag)\n            def widen():\n                new = readout("R", "घटा", GOLD)\n                new.move_to(r_out)\n                mark_group(new, _wire_tag)\n                self.cue("reveal", gain=-3.0)\n                self.play(bar.animate.stretch(1.5, 1, about_edge=DOWN),\n                          Transform(r_out, new), run_time=0.8)\n                for m in (fig, bar, dim, pair, r_out):\n                    mark_group(m, _wire_tag)\n            if spec.get("stretch_at") is not None:\n                self._later(int(spec["stretch_at"]), stretch)\n            if spec.get("widen_at") is not None:\n                self._later(int(spec["widen_at"]), widen)\n            # ONE DIAGRAM, so the layout audit stops comparing its own parts\n            # against each other. Animating the bar lifts it to the top level\n            # beside the dimension line and the readouts, which sit over it by\n            # design — without this the guard reported ten 100% overlaps on a\n            # figure that is visually correct.\n            mark_group(fig, _wire_tag)\n            return fig\n        elif kind == "membrane":'),
    # 0. a bitmap figure cannot be drawn stroke by stroke
    ("""                        self.play(Write(built, lag_ratio=0.02), run_time=1.8)""",
     """                        # WRITE IS VECTOR-ONLY. A `draw: "image"` figure is an
                        # ImageMobject in a Group and Manim raises "Write only
                        # works for vectorized Mobjects" on it, killing the whole
                        # render at the figure beat. A picture fades instead.
                        if all(isinstance(_m, VMobject)
                               for _m in built.family_members_with_points()):
                            self.play(Write(built, lag_ratio=0.02), run_time=1.8)
                        else:
                            self.play(FadeIn(built), run_time=0.8)"""),
    # 1. the card, laid out above a full-height presenter
    ('''            self.question_card(META["question"], META.get("highlight", ""),
                               META.get("years", ""),
                               sheet=ROOT / "assets" / "design" / "question_sheet.png",
                               marks=META.get("marks"))''',
     '''            if globals().get("LOOK") == "reference":
                # the reference card: everything above the presenter's head,
                # which in this look stays at ~0.65 for the whole video
                import src.question_card as _QC
                _QC.Q_MARK_Y, _QC.Q_WORD_Y, _QC.RULE_Y = 0.036, 0.084, 0.112
                _QC.SHEET_W, _QC.SHEET_Y, _QC.SHEET_YEARS_Y = 0.68, 0.332, 0.572
            self.question_card(META["question"], META.get("highlight", ""),
                               META.get("years", ""),
                               sheet=ROOT / "assets" / "design" / "question_sheet.png",
                               marks=META.get("marks"),
                               sheet_head=META.get("sheet_head"))'''),
    # 2. a "keep" beat does not clear the stage
    ('''            if i == card_until or i in beats:''',
     '''            if i == card_until or (i in beats and not beats[i].get("keep")):'''),
    ('''                self._pending_asides = []
                self._flows = []
                self.clear_stage()''',
     '''                self._pending_asides = []
                self._flows = []
                self._pending_calls = []
                self.clear_stage()'''),
    # 3. captions are not suppressed when a beat arrives
    ('''                if getattr(self, "caption_mob", None) is not None:
                    self.remove(self.caption_mob)
                    self.caption_mob = None
                spec = beats[i]''',
     '''                if globals().get("LOOK") != "reference" and \\
                        getattr(self, "caption_mob", None) is not None:
                    self.remove(self.caption_mob)
                    self.caption_mob = None
                spec = beats[i]'''),
    # 4. scheduled work, then the caption for this line, always
    ('''            if _UNTIL and float(line["start"]) > _UNTIL:
                break
            self.at(float(line["start"]))
            if i >= card_until and not self.stage_mobs:
                self._line(line["text"], line.get("end"))''',
     '''            for at, fn in list(getattr(self, "_pending_calls", [])):
                if at == i:
                    fn()
                    self.audit_layout(f"ref@{i}")
            if _UNTIL and float(line["start"]) > _UNTIL:
                break
            self.at(float(line["start"]))
            if i >= card_until and (globals().get("LOOK") == "reference"
                                    or not self.stage_mobs):
                self._line(line["text"], line.get("end"))'''),
]


def compose(slug: str) -> Path:
    s = BASE.read_text(encoding="utf-8")
    for old, new in PATCHES:
        if s.count(old) != 1:
            raise SystemExit(f"patch target not found exactly once in {BASE.name}:\n{old[:120]}")
        s = s.replace(old, new)
    s = retheme(s, slug)
    s = s.rstrip() + "\n\n" + LOOK.read_text(encoding="utf-8")
    out = ROOT / "projects" / slug / "manim_code" / "pyq_composed.py"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(s, encoding="utf-8")
    return out


if __name__ == "__main__":
    for slug in sys.argv[1:] or []:
        print(f"  {compose(slug).relative_to(ROOT)}")
