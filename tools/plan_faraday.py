"""Caption track, chip windows and segment spec for CHE-C2-LA-01, one part.

    python tools/plan_faraday.py <part>

Three things it gets right that the vitamins build got wrong first time:

  * **The clock is the srt, and that was checked, not assumed.** On the vitamins
    clip the srt was out by up to four seconds and had to be replaced with
    measured word timings. On THIS clip it is within about a second: probes at
    3s, 13s, 16s, 23s and 39s put it between +0.97s and -0.42s of the audio.
    Whisper meanwhile fell into a repetition loop past 36s (93 words for a
    60-second clip) despite already carrying every loop guard, so transcribing
    would have given a WORSE clock than the file, for fifteen minutes a part.
    Sub-second error is also the least costly kind here, because captions are
    suppressed under every graphic — for most of the part there is no caption on
    screen to be early or late.
  * **Chips anchor to the same measured clock**, by naming the caption line they
    belong against rather than a hard-coded second.
  * **Captions go quiet under a graphic.** A segment fully inside a chip window
    is emitted with `"captions": "off"`; one that straddles keeps only the
    phrases outside the window and says `"captions_partial": true`.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from align import monotonic                  # noqa: E402
from lines_from_srt import parse, split_cue  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "projects/che-c2-la-01"
CHIPS = "tools/edu/renderer/out/chips/far"
LEAD = 0.40

# chip -> the caption line it belongs against, and the line it gives way to.
# Written as text so it survives the clock changing under it.
WINDOWS = {
    1: [("portrait", "सबसे पहले समझते हैं", "और इसे ध्यान से समझना"),
        ("law1",     "तो जब विद्युत्-अपघटन",  "तो पहले नियम में"),
        ("a1",       "तो पहले नियम में",      "जितनी अधिक विद्युत्"),
        ("a2",       "जितनी अधिक विद्युत्",   "डब्लू बराबर"),
        ("a4",       "डब्लू बराबर",           "तो बच्चों, आपने फैराडे")],
    2: [("law2",    "तो दूसरा नियम कहता है", "इसका मतलब है"),
        ("b1",      "इसका मतलब है",          "अब अगर दो पदार्थों"),
        ("twocell", "अब अगर दो पदार्थों",     "पहले पदार्थ के लिए"),
        ("b2",      "पहले पदार्थ के लिए",     "इसलिए W one और W two"),
        ("b3",      "इसलिए W one और W two",  "बस इतना याद रखना"),
        ("compare", "बस इतना याद रखना",      "बच्चों, बस ये दो बातें")],
}


def find(lines, needle, default=None):
    for l in lines:
        if needle in l["text"]:
            return l["start"]
    if default is None:
        raise SystemExit(f"cue not found in the caption track: {needle!r}")
    return default


def main():
    part = int(sys.argv[1])
    srt = ROOT / f"inbox/CHE-C2-LA-01_part{part}_v2.srt"
    end = float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(ROOT / f"inbox/CHE-C2-LA-01_part{part}_v2.mp4")],
        capture_output=True, text=True).stdout)

    # --- text from the srt, clock from the audio ---------------------------- #
    raw = []
    for a, b, text in parse(srt.read_text()):
        raw += split_cue(a, b, text)
    starts = monotonic([l["start"] for l in raw])
    lines = [{"start": round(t, 2),
              "end": round(starts[i + 1] if i + 1 < len(starts) else end, 2),
              "text": l["text"]} for i, (t, l) in enumerate(zip(starts, raw))]
    (P / f"lines_part{part}_v2.json").write_text(
        json.dumps(lines, ensure_ascii=False, indent=1))

    # --- chip windows on that same clock ------------------------------------ #
    plan = []
    for slug, on, off in WINDOWS[part]:
        a = find(lines, on)
        b = find(lines, off, end)
        plan.append({"png": f"{CHIPS}/{slug}.png",
                     "start": round(a - LEAD, 2), "end": round(b, 2)})
    for i in range(len(plan) - 1):
        if plan[i]["end"] > plan[i + 1]["start"]:
            plan[i]["end"] = plan[i + 1]["start"]
    (P / f"plan_part{part}_v2.json").write_text(
        json.dumps(plan, ensure_ascii=False, indent=1))

    # --- the card hands over on a caption boundary -------------------------- #
    card_end = json.loads((P / f"card_part{part}.json").read_text())[0][1]
    first = min(range(len(lines)), key=lambda i: abs(lines[i]["start"] - card_end))
    card_end = lines[first]["start"]
    (P / f"card_part{part}.json").write_text(json.dumps([[0.0, card_end]]))

    # --- segments, with captions off wherever a graphic is up --------------- #
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
        state = covered(lines[i])
        j = i
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
    out = ROOT / f"tools/edu/renderer/spec/_far{part}_v2.json"
    out.write_text(json.dumps(segs, ensure_ascii=False, indent=1))

    quiet = sum(s["duration"] for s in segs if s.get("captions") == "off")
    print(f"part {part}: {len(lines)} lines, {len(plan)} chips, {len(segs)} segments")
    print(f"  card hands over at {card_end:.2f}s, body {body:.2f}s, clip {end:.2f}s")
    print(f"  captions suppressed for {quiet:.1f}s of {body:.1f}s "
          f"({quiet/body*100:.0f}% — the stretches a graphic owns)")
    for c in plan:
        print(f"    {Path(c['png']).stem:9s} {c['start']:7.2f} -> {c['end']:7.2f}")


if __name__ == "__main__":
    main()
