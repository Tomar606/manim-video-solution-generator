#!/usr/bin/env python3
"""Build the edu-renderer spec for PHY-C1-LA-01 (Gauss's law) from the real
HeyGen clip's word timings — the Week-1 migration pilot: rebuild an already
-shipped Manim video (projects/phy-c1-la-01/final/part1.mp4) through the
truth-layer renderer for a side-by-side comparison. See tools/edu/renderer/README.md.

    python3 build_gauss.py > /dev/null   # writes spec/segments.json directly

Follows the same shape as build_dry.py: segment boundaries land on caption
LINE boundaries (never a fixed clock), a phrase runs until the NEXT line
starts so pauses never leave the caption band blank, and diagram state
(carry_over / end_state) is derived automatically from a chronological
`reveals` list rather than hand-computed per segment.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROJ = ROOT.parents[2] / "projects" / "phy-c1-la-01"

GAUSS = "assets/gauss-sphere.svg"

PHI_EQ = r"\Phi_E = \dfrac{q}{\varepsilon_0}"
E_EQ = r"E = \dfrac{1}{4\pi\varepsilon_0}\dfrac{q}{r^2}"

# index 5 is a bare `"` left over from the transcript's quote formatting —
# not a word, just the closing mark of the "गॉस का नियम क्या कहता है?" quote.
# Every other line keeps stray `"` characters stripped for display; the mark
# was how the transcript denoted direct speech, never meant to be a glyph
# on screen.
TEXT_FIX = {5: ""}

P1 = [
    # hook -> statement -> "memorising it isn't enough" bridge into the proof
    dict(asset=None, stage=None, groups=[(0, 2), (3, 4), (6, 8)]),
    dict(asset=None, stage=None, groups=[(9, 12), (13, 15)],
         equations=[(18.3, 36.904, PHI_EQ)]),
    dict(asset=None, stage=None, groups=[(16, 19)]),

    # sphere + point charge at centre O, radius r, point P on the surface
    dict(asset=GAUSS, stage=None, groups=[(20, 24)],
         reveals=[
             (48.9, "charge", "pop_in", 0.45),   # 48.212 "q धन आवेश"
             (50.5, "sphere", "fade_in", 0.8),    # 50.379 "गोले की"
             (53.1, "radius", "draw", 0.6),       # 52.702 "त्रिज्या r है"
         ],
         labels=[
             (48.9, "q", 0.50, 0.36, None),
             (50.5, "O", 0.50, 0.60, None),
             (53.1, "r", 0.62, 0.40, None),
             (56.6, "P", 0.72, 0.42, None),       # 56.164 "बिंदु P पर"
         ]),

    # E at that point — cut to a clean equation-only frame
    dict(asset=None, stage=None, groups=[(25, 26), (27, 28)],
         equations=[(60.4, 70.893, E_EQ)]),

    # back to the diagram: field direction, then the area element dS and
    # the angle it makes with E
    dict(asset=GAUSS, stage=None, groups=[(29, 30), (31, 34), (35, 37), (38, 40)],
         reveals=[
             # re-establish what was already drawn before the equation cut —
             # a quick fade rather than a carry_over, because validate.py only
             # allows carry_over from the IMMEDIATELY preceding segment, and
             # that one is the equation-only cut with nothing on its stage.
             (70.95, "charge", "fade_in", 0.25),
             (70.95, "sphere", "fade_in", 0.25),
             (70.95, "radius", "fade_in", 0.25),
             (73.9, "field", "fade_in", 0.9),      # 73.421 "बाहर की ओर होगी"
             (82.4, "dA_patch", "fade_in", 0.6),   # 81.866 "dS है"
         ],
         labels=[
             (73.9, "E", 0.50, 0.045, None),
             (82.4, "dS", 0.56, 0.34, None),
             (94.2, "θ = 0°", 0.78, 0.13, None),  # 93.766 "zero degree"
         ]),

    # wrap part 1, tee up part 2
    dict(asset=None, stage=None, groups=[(41, 44)]),
]

PART = dict(lines=PROJ / "lines_part1.json", end=113.8, sections=P1)

HILITE = json.loads((PROJ / "meta.json").read_text(encoding="utf-8"))["hilite"]
SEPS = set(" \t।॥.,;:!?()[]\"'—-")


def clean(text: str) -> str:
    return text.replace('"', "").strip()


def golden_for(text: str) -> str | None:
    """Same match the renderer makes at render time — see build_dry.py."""
    for w in HILITE:
        for m in re.finditer(re.escape(w), text):
            before = text[m.start() - 1] if m.start() else None
            after = text[m.end()] if m.end() < len(text) else None
            if (before is None or before in SEPS) and (after is None or after in SEPS):
                return w
    return None


def build() -> list[dict]:
    cfg = PART
    lines = json.loads(Path(cfg["lines"]).read_text(encoding="utf-8"))

    flat = [(s, g) for s in cfg["sections"] for g in s["groups"]]
    starts = [lines[g[0]]["start"] for _, g in flat] + [cfg["end"]]

    out, seg_id = [], 0
    for si, (sec, (i0, i1)) in enumerate(flat):
        seg_id += 1
        t0, t1 = starts[si], starts[si + 1]
        dur = round(t1 - t0, 2)

        phrases = []
        for i in range(i0, i1 + 1):
            nxt = lines[i + 1]["start"] if i + 1 < len(lines) else cfg["end"]
            a = max(0.0, round(lines[i]["start"] - t0, 2))
            b = min(dur, round(min(nxt, t1) - t0, 2))
            text = clean(TEXT_FIX.get(i, lines[i]["text"]))
            if not text or b - a < 0.65:
                # empty after cleanup (the bare-quote line), or too short to
                # sit on screen for the 0.6s transcript-mode floor — its
                # window is folded into the caption already up instead of
                # flashing a near-empty phrase.
                if phrases:
                    phrases[-1]["t_out"] = b
                continue
            phrases.append({"text": text, "golden": golden_for(text),
                            "t_in": a, "t_out": b})
        phrases[-1]["t_out"] = dur

        seg = {"seg_id": seg_id, "duration": dur,
               "voiceover": " ".join(p["text"] for p in phrases),
               "phrases": phrases,
               "timing": "transcript",
               "type": "DIAGRAM" if sec["asset"] else "TEXT_ONLY"}
        if sec["stage"]:
            seg["stage"] = sec["stage"]

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
            shown: set[str] = set()
            for at, sid, act, _d in sec.get("reveals", []):
                if at >= t0:
                    break
                shown.discard(sid) if act == "fade_out" else shown.add(sid)
            timeline = [{"id": sid, "action": act,
                         "t": round(at - t0, 2), "dur": d}
                        for at, sid, act, d in sec.get("reveals", [])
                        if t0 <= at < t1]
            carry = sorted(shown)
            after = set(shown)
            for a in timeline:
                after.discard(a["id"]) if a["action"] == "fade_out" else after.add(a["id"])
            seg["diagram"] = {"asset": sec["asset"], "carry_over": carry,
                              "timeline": timeline}
            seg["end_state"] = sorted(after)

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
    segs = build()
    total = round(sum(s["duration"] for s in segs), 2)
    text = json.dumps(segs, ensure_ascii=False, indent=1)
    (ROOT / "spec" / "segments.json").write_text(text, encoding="utf-8")
    (ROOT / "spec" / "_gauss_part1.json").write_text(text, encoding="utf-8")
    print(f"phy-c1-la-01 part 1: {len(segs)} segments, {total}s -> spec/segments.json")
