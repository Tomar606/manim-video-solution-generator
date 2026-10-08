"""Caption track, chip windows and segment spec for BIO-C1-LA-01, one part.

    python tools/plan_bio1.py <part>

Same shape as plan_faraday.py, on a clock that needed no repair: every one of
these four HeyGen srt files ends within 0.04s of its own clip, so the export IS
the clock and Whisper was never run.

The chip prefixes do NOT line up with the recorded part numbers -- the chips
were authored against the written script and the faculty split the recording
differently, so part 2 of the video carries chips named p1d and p2a-b. Windows
are therefore written as (chip, caption it comes up on, caption it gives way
to), and the chip's name is just a filename.

`p4c-order` has no window. The written script had a "क्रम एक बार बोलकर याद कर
लो" recap and the recorded narration drops it, so there is no line to anchor it
against -- and a graphic the narration does not support is worse than no
graphic. It stays unused rather than being wedged in somewhere plausible.
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
P = ROOT / "projects/bio-c1-la-01"
CHIPS = "tools/edu/renderer/out/chips/ovule"
LEAD = 0.40

WINDOWS = {
    1: [("p1a-plain",    "आवृतबीजियों में",        "अब बीजाण्ड के parts"),
        ("p1b-funicle",  "एक छोटे डंठल जैसी",       "चलो, एक हो गया"),
        ("p1c-integ",    "प्रत्येक बीजाण्ड प्रायः दो", "यहाँ तक बीजाण्ड के दो main")],
    2: [("p1d-micro",    "यह बीजाण्ड का वह भाग",     "एकदम दिमाग में बिठा लो"),
        ("p2a-nucellus", "मृदूतकी कोशिकाओं से बना",  "विपरीत सिरे को निभाग"),
        ("p2b-chalaza",  "विपरीत सिरे को निभाग",     "चार मुख्य भाग हो गए")],
    3: [("p2c-sac",      "के अंदर, लगभग बीच में",    "अब सबसे जरूरी बात"),
        ("p4a-count",    "कुल 7 कोशिकाएँ होती हैं",   "तो यहाँ तक तो बेटा")],
    4: [("p3b-egg",      "बीजाण्डद्वार के सिरे की ओर", "अब दूसरा"),
        ("p3c-anti",     "यानी निभागी सिरे की ओर",   "और अब बीच में क्या है"),
        ("p3d-polar",    "भ्रूणकोष के बीच में",       "अब एक और जरूरी बात"),
        ("p4b-pen",      "द्विनिषेचन के समय",         "अब समझ आया कि इसे"),
        ("p4a-count",    "एक अण्ड कोशिका + दो",      "ये गिनती वाली बात")],
}

# where the question card gives way to the caption body; snapped to the nearest
# caption boundary below so the handover never lands mid-sentence
CARD = {1: 15.35, 2: 9.51, 3: 9.24, 4: 11.31}


def find(lines, needle, default=None):
    for l in lines:
        if needle in l["text"]:
            return l["start"]
    if default is None:
        raise SystemExit(f"cue not found in the caption track: {needle!r}")
    return default


def main():
    part = int(sys.argv[1])
    srt = ROOT / f"inbox/bio1/part{part}.srt"
    end = float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(ROOT / f"inbox/bio1/part{part}.mp4")],
        capture_output=True, text=True).stdout)

    raw = []
    for a, b, text in parse(srt.read_text()):
        raw += split_cue(a, b, text)
    lines = [{"start": round(l["start"], 2),
              "end": round(raw[i + 1]["start"] if i + 1 < len(raw) else end, 2),
              "text": l["text"]} for i, l in enumerate(raw)]
    # Both ends of every caption onto the audio's word clock. As shipped, this
    # question's parts 2-4 overlapped the words being spoken only 38-40% of the
    # time -- the srt was never checked against the audio for this one.
    wf = P / f"words_part{part}.json"
    if wf.is_file():
        lines, rep = retime(lines, json.loads(wf.read_text()))
        print(f"  retimed: {rep['placed']}/{rep['total']} on the word clock, "
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
    SEPS = set(" \t।॥.,;:!?()[]\"'—-")

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
    (ROOT / f"tools/edu/renderer/spec/_bio1_{part}.json").write_text(
        json.dumps(segs, ensure_ascii=False, indent=1))

    quiet = sum(s["duration"] for s in segs if s.get("captions") == "off")
    print(f"part {part}: {len(lines)} lines, {len(plan)} chips, {len(segs)} segments")
    print(f"  card hands over at {card_end:.2f}s, body {body:.2f}s, clip {end:.2f}s")
    print(f"  captions quiet for {quiet:.1f}s of {body:.1f}s ({quiet/body*100:.0f}%)")
    for c in plan:
        print(f"    {Path(c['png']).stem:13s} {c['start']:7.2f} -> {c['end']:7.2f}")


if __name__ == "__main__":
    main()
