"""Caption track, ANIMATION windows and segment spec for BIO-C5-LA-03, one part.

    python tools/plan_bio5.py <part>

Unlike the other two biology questions, the graphics here are not chips but the
eight helix animations already built in media/videos/helix_parts/. So the plan
names a `mov` instead of a `png` and carries a `scale`, which tools/fit_clips.py
fills in once the presenter has been measured.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lines_from_srt import parse, split_cue  # noqa: E402
from retime_lines import retime  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "projects/bio-c5-la-04"
CHIPS = "tools/edu/renderer/out/chips/bio5b"
LEAD = 0.40

WINDOWS = {
    1: [("p1-defn",     "डी एन ए अणु के द्विगुणन",   "अब इसकी सबसे important"),
        ("p1-semicons", "इसका अर्थ है कि एक",        "चलो अब इसकी क्रियाविधि"),
        ("p1-steps",    "जिसके 4 प्रमुख पद",          "DNA के अंदर की वह खास"),
        ("p1-ori",      "इसमें प्रोकैरियोटिक कोशिका", "बच्चों, पहला समझ गए")],
    2: [("p2-primer",   "RNA का एक छोटा-सा खण्ड",     "इसे आसान तरीके से याद"),
        ("p2-polymerase","इसे आसान तरीके से याद",     "अब आते हैं replication"),
        ("p2-direction","DNA पॉलीमरेज एंजाइम केवल",   "चूँकि DNA के दोनों"),
        ("p2-leading",  "जिस टेम्पलेट स्ट्रैण्ड की ध्रुवता 3", "अब DNA खुल गया")],
    3: [("p3-lagging",  "जिस टेम्पलेट स्ट्रैण्ड की ध्रुवता,", "और इन्हीं छोटे छोटे"),
        ("p3-okazaki",  "और इन्हीं छोटे छोटे",        "यहाँ एक बात बहुत"),
        ("p3-compare",  "leading strand सतत बनती है", "और Lagging strand में"),
        ("p3-energy",   "संश्लेषण में प्रयुक्त",       "अब एक कोशिका-चक्र"),
        ("p3-cycle",    "एक कोशिका-चक्र में पूरे",     "तो बच्चों, पूरा DNA")],
}

CARD = {1: 12.81, 2: 9.68, 3: 9.22}

# Per-part caption shift, in seconds, added to every cue.
# Measured against the audio, not guessed: speech onsets were detected at four
# thresholds (floor +12/+8/+6/+4 dB) and each cue start compared to the onset it
# belongs to. Parts 1 and 2 swing with the threshold (-0.19s to +0.55s), which is
# the detector's own bias -- it only fires after a loud onset, so a phrase that
# starts quietly reads as an early caption. Part 3 sits at -0.74s at EVERY
# threshold, and an offset that does not move with the detector is the clip's,
# not the detector's. So only part 3 is corrected.
# Superseded by per-line retiming below, which measures each caption
# instead of shifting the whole track by one number. Kept at zero so the
# two corrections can never be applied on top of each other.
SHIFT = {1: 0.0, 2: 0.0, 3: 0.0}


def find(lines, needle, default=None):
    for l in lines:
        if needle in l["text"]:
            return l["start"]
    if default is None:
        raise SystemExit(f"cue not found in the caption track: {needle!r}")
    return default


def main():
    part = int(sys.argv[1])
    srt = ROOT / f"inbox/bio5b/part{part}.srt"
    end = float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(ROOT / f"inbox/bio5b/part{part}.mp4")],
        capture_output=True, text=True).stdout)

    raw = []
    sh = SHIFT.get(part, 0.0)
    for a, b, text in parse(srt.read_text()):
        raw += split_cue(a + sh, b + sh, text)
    lines = [{"start": round(l["start"], 2),
              "end": round(raw[i + 1]["start"] if i + 1 < len(raw) else end, 2),
              "text": l["text"]} for i, l in enumerate(raw)]
    # Put both ends of every caption on the audio's own word clock, if the clip
    # has been transcribed. The srt is a good starting point and no better than
    # that: measured against the transcript, part 3's captions overlapped the
    # words being spoken only 29% of the time before this ran.
    wf = P / f"words_part{part}.json"
    if wf.is_file():
        lines, rep = retime(lines, json.loads(wf.read_text()))
        print(f"  retimed: {rep['placed']}/{rep['total']} lines on the word clock, "
              f"{rep['moved']} moved (median {rep['median']:+.2f}s)")
    (P / f"lines_part{part}.json").write_text(
        json.dumps(lines, ensure_ascii=False, indent=1))

    plan = []
    for slug, on, off in WINDOWS[part]:
        a, b = find(lines, on), find(lines, off, end)
        plan.append({"png": f"{CHIPS}/{slug}.png",
                     "start": round(a - LEAD, 2), "end": round(b, 2),
                     "top": 380})
    for i in range(len(plan) - 1):
        plan[i]["end"] = min(plan[i]["end"], plan[i + 1]["start"])
    (P / f"plan_part{part}.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1))

    first = min(range(len(lines)), key=lambda i: abs(lines[i]["start"] - CARD[part]))
    card_end = lines[first]["start"]
    (P / f"card_part{part}.json").write_text(json.dumps([[0.0, card_end]]))

    meta = json.loads((P / "meta.json").read_text())
    SEPS = set(" \t।॥.,;:!?()[]\"'-")

    def golden(t):
        for w in meta.get("hilite", []):
            for m in re.finditer(re.escape(w), t):
                b = t[m.start() - 1] if m.start() else None
                a = t[m.end()] if m.end() < len(t) else None
                if (b is None or b in SEPS) and (a is None or a in SEPS):
                    return w
        return None

    def covered(l):
        mid = (l["start"] + l["end"]) / 2
        return any(c["start"] <= mid < c["end"] for c in plan)

    segs, i, sid = [], first, 0
    while i < len(lines):
        state, j = covered(lines[i]), i
        while j < len(lines) and covered(lines[j]) == state and j - i < 4:
            j += 1
        t0 = lines[i]["start"]
        t1 = lines[j]["start"] if j < len(lines) else end
        sid += 1
        seg = {"seg_id": sid, "duration": round(t1 - t0, 2), "type": "TEXT_ONLY",
               "timing": "transcript", "labels": []}
        if state:
            seg["captions"] = "off"
            seg["voiceover"] = " ".join(lines[k]["text"] for k in range(i, j))
            seg["phrases"] = []
        else:
            ph = []
            for k in range(i, j):
                a = max(0.0, round(lines[k]["start"] - t0, 2))
                b = min(seg["duration"],
                        round((lines[k + 1]["start"] if k + 1 < len(lines) else end) - t0, 2))
                ph.append({"text": lines[k]["text"], "golden": golden(lines[k]["text"]),
                           "t_in": a, "t_out": b})
            ph[-1]["t_out"] = seg["duration"]
            seg["voiceover"] = " ".join(x["text"] for x in ph)
            seg["phrases"] = ph
        segs.append(seg)
        i = j

    body = sum(s["duration"] for s in segs)
    assert abs(card_end + body - end) < 0.10, (
        f"card {card_end:.2f} + body {body:.2f} != clip {end:.2f}")
    (ROOT / f"tools/edu/renderer/spec/_bio5b_{part}.json").write_text(
        json.dumps(segs, ensure_ascii=False, indent=1))

    quiet = sum(s["duration"] for s in segs if s.get("captions") == "off")
    print(f"part {part}: {len(lines)} lines, {len(plan)} animations, {len(segs)} segments")
    print(f"  card hands over at {card_end:.2f}s, body {body:.2f}s, clip {end:.2f}s")
    print(f"  captions quiet for {quiet:.1f}s of {body:.1f}s ({quiet/body*100:.0f}%)")
    for c in plan:
        # chips are stills, so there is no duration to probe -- the window is
        # the whole story here, unlike the helix clips this was adapted from
        w = c["end"] - c["start"]
        print(f"    {Path(c['png']).stem:14s} {c['start']:7.2f} -> {c['end']:7.2f}"
              f"  ({w:5.1f}s window)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
