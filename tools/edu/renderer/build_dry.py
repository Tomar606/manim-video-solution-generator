#!/usr/bin/env python3
"""Build an edu-renderer spec from the presenter's own word timings.

    python3 build_dry.py 1 > spec/segments.json

WHY THIS EXISTS
---------------
Segment boundaries must land on LINE boundaries. The hand-built spec placed
them on a fixed clock instead, so a caption that straddled a boundary was
clipped at the segment end and never re-shown in the next one. Seven captions
in part 1 flashed for two frames and then left the screen blank for up to five
seconds each. Nothing downstream can see that — the renderer, the QA pass and
the compositor all believe the spec — so it has to be right here.

Two rules the plan below is built to keep:

  * A LABEL NEVER EXPIRES. Once revealed it is carried into every later segment
    of its section, so the section ends with the figure fully labelled. Same for
    the legs of an animated path: the stretch already travelled stays lit while
    the next one lights up.

  * A REVEAL IS SYNCED TO THE WORD. Every entry in REVEALS/LABELS is an absolute
    clip time taken from the line that names the thing. Sync when a label first
    appears; never sync it leaving.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROJ = ROOT.parents[2] / "projects" / "che-c2-la-05"

CELL = "assets/dry-cell.svg"
WORK = "assets/dry-cell-working.svg"
# The working section is the one stretch where the presenter is gone (he fades
# out over PRESENTER_FADE and does not come back), so the stage may use the
# whole frame. Every other segment keeps the band from style.css, above the
# halfway line, because he is standing in front of it.
TALL = {"top": 330, "h": 1000}

# --------------------------------------------------------------------------- #
# PART 1                                                                       #
# --------------------------------------------------------------------------- #
# groups are [first_line, last_line] into lines_part1.json; a segment runs from
# its first line's start to the NEXT segment's first line, so the sections tile
# the clip with no gap.
P1 = [
    dict(asset=None, stage=None, groups=[(6, 7), (8, 9), (10, 11)]),
    dict(asset=CELL, stage=None,
         groups=[(12, 13), (14, 15), (16, 17), (18, 19), (20, 21), (22, 23),
                 (24, 25), (26, 27), (28, 29), (30, 31), (32, 34), (35, 37)],
         reveals=[
             # part of the cell            named at
             (35.58, "dc_zinc",          "fade_in", 0.6),   # 35.18 जिंक का खोखला आवरण
             (36.28, "lead_zinc",        "fade_in", 0.5),
             (42.08, "dc_electrolyte",   "fade_in", 0.6),   # 41.68 NH₄Cl और ZnCl₂
             (42.78, "lead_electrolyte", "fade_in", 0.5),
             (52.58, "dc_rod",           "fade_in", 0.6),   # 52.22 कार्बन की छड़
             (53.08, "dc_cap",           "fade_in", 0.5),
             (53.28, "lead_rod",         "fade_in", 0.5),
             (57.08, "dc_mno2",          "fade_in", 0.6),   # 56.68 MnO₂ और कार्बन चूर्ण
             (57.78, "lead_mno2",        "fade_in", 0.5),
             (63.20, "dc_seal",          "fade_in", 0.6),   # never named; completes the figure
             (63.90, "lead_seal",        "fade_in", 0.5),   # as the recap opens
             # the recap counts the four things off — each lifts as it is said
             (68.90, "dc_zinc",        "pulse", 1.1),   # सबसे पहले, Zn का बाहरी आवरण
             (72.64, "dc_electrolyte", "pulse", 1.1),   # दूसरा, NH₄Cl और ZnCl₂
             (78.02, "dc_rod",         "pulse", 1.1),   # तीसरा, कार्बन रॉड
             (81.86, "dc_mno2",        "pulse", 1.1),   # और चौथा, MnO₂
             # the figure leaves before the working section replaces it
             (105.20, "dc_zinc",          "fade_out", 0.9),
             (105.20, "dc_electrolyte",   "fade_out", 0.9),
             (105.20, "dc_rod",           "fade_out", 0.9),
             (105.20, "dc_cap",           "fade_out", 0.9),
             (105.20, "dc_mno2",          "fade_out", 0.9),
             (105.20, "dc_seal",          "fade_out", 0.9),
             (105.20, "lead_zinc",        "fade_out", 0.9),
             (105.20, "lead_electrolyte", "fade_out", 0.9),
             (105.20, "lead_rod",         "fade_out", 0.9),
             (105.20, "lead_mno2",        "fade_out", 0.9),
             (105.20, "lead_seal",        "fade_out", 0.9),
         ],
         labels=[
             (36.48, "जिंक पात्र",    0.22, 0.34, 105.20),
             (42.98, "NH₄Cl + ZnCl₂", 0.21, 0.79, 105.20),
             (53.48, "कार्बन छड़",     0.79, 0.14, 105.20),
             (57.98, "MnO₂ + कार्बन", 0.78, 0.79, 105.20),
             (64.10, "सील",           0.22, 0.12, 105.20),
             # THE RECAP IS A COUNTED LIST, so it is numbered with digits, not
             # dashes: the student is copying it into an answer where the
             # numbering is part of the mark scheme. Each digit lands on the
             # word that counts it and stays for the rest of the figure.
             (68.90, "1", 0.105, 0.34, 105.20, True),
             (72.64, "2", 0.045, 0.79, 105.20, True),
             (78.02, "3", 0.915, 0.14, 105.20, True),
             (81.86, "4", 0.955, 0.79, 105.20, True),
         ]),
    dict(asset=WORK, stage=TALL,
         groups=[(38, 40), (41, 42), (43, 44), (45, 46),
                 (47, 49), (50, 52), (53, 55)],
         reveals=[
             # the same cell, drawn large, built back up in one breath
             (106.66, "w_zinc",        "fade_in", 0.6),
             (106.86, "w_electrolyte", "fade_in", 0.6),
             (107.06, "w_mno2",        "fade_in", 0.6),
             (107.26, "w_rod",         "fade_in", 0.6),
             (107.46, "w_seal",        "fade_in", 0.5),
             (107.46, "w_cap",         "fade_in", 0.5),
             (107.66, "w_base",        "fade_in", 0.5),
             # 116.44 जिंक इलेक्ट्रॉन खोकर / 119.20 Zn²⁺ आयन के रूप में
             (117.40, "w_ion1", "fade_in", 0.5),
             (117.90, "w_ion2", "fade_in", 0.5),
             (118.40, "w_ion3", "fade_in", 0.5),
             # 123.18 जिंक पर इलेक्ट्रॉन निकल रहे हैं
             (123.60, "w_e_metal", "fade_in", 0.6),
             # 127.98 इसलिए जिंक ऐनोड है
             (128.30, "w_minus", "fade_in", 0.5),
             # 129.84 और ये इलेक्ट्रॉन बाहरी परिपथ से
             (130.10, "w_wire",  "draw",    0.9),
             (130.60, "w_e_out", "fade_in", 0.6),
             # 131.68 कार्बन की छड़ की ओर जाते हैं
             (131.90, "w_e_run", "fade_in", 0.6),
             (132.70, "w_e_rod", "fade_in", 0.6),
             # 133.62 अभी के लिए बस इतना पक्का कर लो — जिंक ऐनोड है
             (134.60, "w_zinc",  "pulse", 1.1),
             (134.60, "w_minus", "pulse", 1.1),
             # 138.68 अब कैथोड पर क्या होता है
             (139.00, "w_plus",  "fade_in", 0.5),
         ],
         labels=[
             (119.30, "Zn²⁺",      0.440, 0.235, None),
             (128.50, "ऐनोड (−)",  0.800, 0.851, None),
             (131.00, "e⁻",        0.251, 0.611, None),
             (139.20, "कैथोड (+)", 0.785, 0.089, None),
         ]),
]

# Whisper mis-heard nothing that survives into part 1 now that the captions are
# rebuilt from the recorded script (script_master.md); the table stays because
# the next clip will need it.
TEXT_FIX = {}

# --------------------------------------------------------------------------- #
# PART 2 — the chemistry. No figure: the equations ARE the organisation here,   #
# and the labelled cell was part 1's job. Where neither an equation nor a       #
# figure would teach anything, the screen stays quiet and the presenter carries #
# it — restating the caption on screen is a defect, not a filler.               #
# --------------------------------------------------------------------------- #
P2 = [
    dict(asset=None, stage=None,
         groups=[(3, 5), (6, 9), (10, 12), (13, 14), (15, 17), (18, 20),
                 (21, 23), (24, 27), (28, 30), (31, 33), (34, 37), (38, 41),
                 (42, 44), (45, 48), (49, 50), (51, 53), (54, 57), (58, 61),
                 (62, 65), (66, 67)],
         equations=[
             # LONG REACTIONS BREAK AT THE ARROW. Typeset on one line a
             # six-species reaction has to shrink to about 40% of house size to
             # fit the frame, which is the "equation too small" defect again.
             # Broken after the reactants it stays large and reads the way it is
             # written in an answer book.
             # cathode half-reaction — spoken 14.90 -> 26.50
             (15.50, 26.60,
              r"\begin{aligned}"
              r"& 2NH_4^+ + 2MnO_2 + 2e^- \\[4pt]"
              r"& \longrightarrow\; Mn_2O_3 + H_2O + 2NH_3"
              r"\end{aligned}"),
             # manganese drops +4 -> +3 — spoken 28.95 -> 37.09
             (29.40, 41.20, r"Mn:\;\; +4 \longrightarrow +3"),
             # the two halves together, right as he says "जोड़ते हैं"
             (44.30, 51.00,
              r"\begin{aligned}"
              r"& Zn \longrightarrow Zn^{2+} + 2e^- \\[10pt]"
              r"& 2NH_4^+ + 2MnO_2 + 2e^- \\[4pt]"
              r"& \longrightarrow\; Mn_2O_3 + H_2O + 2NH_3"
              r"\end{aligned}"),
             # ...and their sum
             (51.20, 67.20,
              r"\begin{aligned}"
              r"& Zn + 2NH_4^+ + 2MnO_2 \\[4pt]"
              r"& \longrightarrow\; Zn^{2+} + Mn_2O_3 + H_2O + 2NH_3"
              r"\end{aligned}"),
             # the complex ion that keeps the ammonia in — spoken 92.90
             (93.50, 104.40,
              r"\begin{aligned}"
              r"& Zn^{2+} + 4NH_3 \\[4pt]"
              r"& \longrightarrow\; [Zn(NH_3)_4]^{2+}"
              r"\end{aligned}"),
             # the cell voltage — spoken 123.16
             (123.60, 130.00, r"E_{\text{cell}} \approx 1.25 - 1.5\ \text{V}"),
         ]),
]

PARTS = {1: dict(lines=PROJ / "lines_part1.json", first=7, end=144.52,
                 sections=P1),
         2: dict(lines=PROJ / "lines_part2.json", first=3, end=176.16,
                 sections=P2)}

# Words the house style paints gold. Only ever applied when the word is present
# in the phrase verbatim — the renderer throws rather than ship a plain one.
HILITE = json.loads((PROJ / "meta.json").read_text())["hilite"]
SEPS = set(" \t\u0964\u0965.,;:!?()[]\"'\u2014-")


def golden_for(text: str) -> str | None:
    """The same match the renderer makes, so it can never throw on our output.

    Python's look-behind must be fixed width, so the boundary is checked by
    hand rather than in the pattern — but the rule is character for character
    the one in goldenize(): a separator or the end of the string on each side.
    """
    for w in HILITE:
        for m in re.finditer(re.escape(w), text):
            before = text[m.start() - 1] if m.start() else None
            after = text[m.end()] if m.end() < len(text) else None
            if (before is None or before in SEPS) and (after is None or after in SEPS):
                return w
    return None


def build(part: int) -> list[dict]:
    cfg = PARTS[part]
    lines = json.loads(Path(cfg["lines"]).read_text())

    # flatten the groups so each segment knows where the next one starts
    flat = [(s, g) for s in cfg["sections"] for g in s["groups"]]
    starts = [lines[g[0]]["start"] for _, g in flat] + [cfg["end"]]

    out, seg_id = [], 0
    for si, (sec, (i0, i1)) in enumerate(flat):
        seg_id += 1
        t0, t1 = starts[si], starts[si + 1]
        dur = round(t1 - t0, 2)

        # captions: each line runs until the NEXT one starts, so the band is
        # never blank across the micro-gaps between lines.
        phrases = []
        for i in range(i0, i1 + 1):
            nxt = lines[i + 1]["start"] if i + 1 < len(lines) else cfg["end"]
            a = max(0.0, round(lines[i]["start"] - t0, 2))
            b = min(dur, round(min(nxt, t1) - t0, 2))
            if b - a < 0.25:                    # would flash; fold into the previous
                if phrases:
                    phrases[-1]["t_out"] = b
                continue
            text = TEXT_FIX.get(part, {}).get(i, lines[i]["text"])
            phrases.append({"text": text, "golden": golden_for(text),
                            "t_in": a, "t_out": b})
        phrases[-1]["t_out"] = dur

        seg = {"seg_id": seg_id, "duration": dur,
               "voiceover": " ".join(p["text"] for p in phrases),
               "phrases": phrases,
               # tells validate.py the clock came from the recording, not from
               # an author choosing how long to leave each line up
               "timing": "transcript",
               "type": "DIAGRAM" if sec["asset"] else "TEXT_ONLY"}
        if sec["stage"]:
            seg["stage"] = sec["stage"]

        # An equation may span several segments; the engine builds one segment
        # at a time, so it is repeated in each with a negative t_in meaning
        # "already up when we opened".
        for a, z, latex in sec.get("equations", []):
            if a >= t1 or z <= t0:
                continue
            eq = {"latex": latex, "t_in": round(a - t0, 2) if a >= t0 else -0.6}
            if t0 < z < t1:
                eq["t_out"] = round(z - t0, 2)
            seg["equation"] = eq
            seg["type"] = "EQUATION"
            break

        if sec["asset"]:
            # what is ALREADY on screen when this segment opens
            shown: set[str] = set()
            for at, sid, act, _d in sec.get("reveals", []):
                if at >= t0:
                    break
                shown.discard(sid) if act == "fade_out" else shown.add(sid)
            timeline = [{"id": sid, "action": act,
                         "t": round(at - t0, 2), "dur": d}
                        for at, sid, act, d in sec.get("reveals", [])
                        if t0 <= at < t1]
            # a pulse or a fade_out acts on something already visible, so its id
            # has to be carried in as well or the engine starts it at opacity 0
            carry = sorted(shown)
            after = set(shown)
            for a in timeline:
                after.discard(a["id"]) if a["action"] == "fade_out" else after.add(a["id"])
            seg["diagram"] = {"asset": sec["asset"], "carry_over": carry,
                              "timeline": timeline}
            seg["end_state"] = sorted(after)

            # LABELS ACCUMULATE. Everything revealed so far in this section is
            # listed again; a negative t_in means "already up when we opened".
            labels = []
            for at, text, x, y, out_at, *rest in sec.get("labels", []):
                if at >= t1 or (out_at is not None and out_at <= t0):
                    continue
                lab = {"text": text, "x": x, "y": y,
                       "t_in": round(at - t0, 2) if at >= t0 else -0.6,
                       "accent": bool(rest[0]) if rest else False}
                if out_at is not None and t0 <= out_at < t1:
                    lab["t_out"] = round(out_at - t0, 2)
                labels.append(lab)
            seg["labels"] = labels
        else:
            seg["labels"] = []

        out.append(seg)
    return out


if __name__ == "__main__":
    # WRITES spec/segments.json ITSELF. It used to print to stdout and the spec
    # was moved around by hand between the two parts; a stale snapshot got
    # copied back over a newer plan and a whole part rendered without the
    # numbering that had just been added to it. One command, one file, no copies.
    part = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    segs = build(part)
    total = round(sum(s["duration"] for s in segs), 2)
    text = json.dumps(segs, ensure_ascii=False, indent=1)
    (ROOT / "spec" / "segments.json").write_text(text)
    (ROOT / "spec" / f"_p{part}_final.json").write_text(text)
    print(f"part {part}: {len(segs)} segments, {total}s -> spec/segments.json")
