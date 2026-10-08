"""Caption track, chip windows and segment spec for BIO-C4-LA-01, one part.

    python tools/plan_bio4.py <part>

Same shape as plan_bio1.py. The clock is the HeyGen srt again -- all three end
within 0.02s of their clips -- so nothing is transcribed.
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
P = ROOT / "projects/bio-c4-la-01"
CHIPS = "tools/edu/renderer/out/chips/bio4"
LEAD = 0.40

WINDOWS = {
    1: [("p1-defn",    "जब किसी विषमयुग्मजी",      "और परीक्षा में ये परिभाषा"),
        ("p1-antigen", "अगर RBC पर A एंटीजन",      "यहीं सबसे ज्यादा बच्चे"),
        ("p1-allele",  "इस जीन के तीन एलील",       "तो यहाँ तक तो बेटा")],
    2: [("p2-ab",      "न A ने B को दबाया",        "अब आते हैं दूसरे वाले"),
        ("p2-defn",    "अपूर्ण प्रभाविता वह वंशागति", "चलो अब इसका उदाहरण"),
        ("p2-cross",   "सोचो बच्चों शुद्ध लाल",      "AB रक्त समूह में A और B"),
        ("p2-compare", "AB रक्त समूह में A और B",    "बच्चों इतना तो हो गया")],
    3: [("p3-punnett", "क्योंकि F₁ पौधों को",       "अब सोचो - अगर रंग"),
        ("p3-ratio",   "और ये अनुपात मुह",          "अब एक आखिरी बात"),
        ("p3-enzyme",  "अपूर्ण प्रभाविता में लाल रंग", "और अगर सब कुछ याद"),
        ("p3-oneline", "तो ये एक लाइन पक्की कर लो", "बस यही एक लाइन")],
}

# Where the card hands over. The card finishes ANIMATING at ~3.3s and is a
# still picture after that, so this number is really "how long do we hold a
# frozen frame while he talks with no captions under him".
# Part 1 was 18.43s -- 12.2s of frozen card, and the opening read as captions
# arriving late. Parts 2 and 3 hold 6.6s and 8.0s and were fine, so part 1 is
# brought in line rather than all three being redesigned.
CARD = {1: 8.74, 2: 9.82, 3: 11.19}


def find(lines, needle, default=None):
    for l in lines:
        if needle in l["text"]:
            return l["start"]
    if default is None:
        raise SystemExit(f"cue not found in the caption track: {needle!r}")
    return default


def main():
    part = int(sys.argv[1])
    srt = ROOT / f"inbox/bio4/part{part}.srt"
    end = float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(ROOT / f"inbox/bio4/part{part}.mp4")],
        capture_output=True, text=True).stdout)

    raw = []
    for a, b, text in parse(srt.read_text()):
        raw += split_cue(a, b, text)
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
                     "start": round(a - LEAD, 2), "end": round(b, 2)})
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
    (ROOT / f"tools/edu/renderer/spec/_bio4_{part}.json").write_text(
        json.dumps(segs, ensure_ascii=False, indent=1))

    quiet = sum(s["duration"] for s in segs if s.get("captions") == "off")
    print(f"part {part}: {len(lines)} lines, {len(plan)} chips, {len(segs)} segments")
    print(f"  card hands over at {card_end:.2f}s, body {body:.2f}s, clip {end:.2f}s")
    print(f"  captions quiet for {quiet:.1f}s of {body:.1f}s ({quiet/body*100:.0f}%)")
    for c in plan:
        print(f"    {Path(c['png']).stem:12s} {c['start']:7.2f} -> {c['end']:7.2f}")


if __name__ == "__main__":
    raise SystemExit(main())
