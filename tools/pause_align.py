"""Retime lines_part1.json onto the audio's own pauses (no Whisper): cue boundaries snap to the longest pause
near the SRT time, and lines inside a cue split at the longest pauses inside it (HeyGen pauses at every comma).

    python tools/pause_align.py projects/<slug> [--write]

Run after tools/lines_from_srt.py has written lines_part1.json from the SRT. Without --write it only prints
the old and new start of every line, to check the joins against a loudness envelope first.
"""
import json, re, subprocess, sys
from pathlib import Path


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    proj = Path(sys.argv[1]); P = proj / "src"
    def parse(p):
        out = []
        for blk in re.split(r"\n\s*\n", p.read_text().strip()):
            ls = blk.strip().splitlines(); a, b = ls[1].split(" --> ")
            f = lambda s: int(s[:2])*3600 + int(s[3:5])*60 + float(s[6:].replace(",", "."))
            out.append([f(a), f(b), " ".join(ls[2:])])
        return out
    cues = parse(P / "part1.srt")
    L = json.loads((proj / "lines_part1.json").read_text())
    err = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(P / "part1.mp4"), "-vn", "-af", "silencedetect=n=-38dB:d=0.07", "-f", "null", "-"], capture_output=True, text=True).stderr
    ss = [float(x) for x in re.findall(r"silence_start: ([0-9.]+)", err)]; se = [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", err)]
    pauses = list(zip(ss, se))           # (start, end)
    dur = float(re.search(r"Duration: (\d+):(\d+):([\d.]+)", err).group(3)) + 60 * int(re.search(r"Duration: (\d+):(\d+)", err).group(2))
    # which cue does each line belong to
    norm = lambda s: re.sub(r"[^\w]", "", s)
    owner, ci, acc = [], 0, ""
    for l in L:
        while norm(l["text"])[:6] not in norm(cues[ci][2]) and ci < len(cues) - 1:
            ci += 1
        owner.append(ci)
    def best(lo, hi, avoid=()):
        c = [p for p in pauses if lo <= p[1] and p[0] <= hi and p not in avoid]
        return max(c, key=lambda p: p[1] - p[0]) if c else None
    # cue boundaries
    cb = []
    for k in range(1, len(cues)):
        t = cues[k][0]; c = [p for p in pauses if t - 0.9 <= p[1] and p[0] <= t + 0.9]
        p = max(c, key=lambda p: (p[1] - p[0]) - 0.15 * abs((p[0] + p[1]) / 2 - t)) if c else None
        cb.append(p if p else (t, t))
    first = next(p for p in pauses if p[0] < 0.05)[1] if pauses and pauses[0][0] < 0.05 else cues[0][0]
    spans = [(first if k == 0 else cb[k - 1][1], cb[k][0] if k < len(cb) else min(dur, cues[-1][1] + 0.3)) for k in range(len(cues))]
    out = []
    for k, (a, b) in enumerate(spans):
        idx = [i for i, o in enumerate(owner) if o == k]
        n = len(idx)
        inner = sorted([p for p in pauses if a + 0.4 < p[0] and p[1] < b - 0.4], key=lambda p: p[1] - p[0], reverse=True)
        # internal pauses = one per comma in the cue; the line breaks are the commas lines_from_srt split at
        # each internal line break: the strongest pause near where its share of the cue's characters puts it
        tot = sum(len(L[i]["text"]) for i in idx); bounds, cum, prev = [], 0, a
        for i in idx[:-1]:
            cum += len(L[i]["text"]); e = a + (b - a) * cum / tot
            c = [p for p in pauses if prev + 0.5 < p[0] and p[1] < b - 0.5 and abs((p[0] + p[1]) / 2 - e) < 1.4 and p[1] - p[0] >= 0.09]
            p = max(c, key=lambda p: (p[1] - p[0]) - 0.12 * abs((p[0] + p[1]) / 2 - e)) if c else (e, e)
            bounds.append((prev, p[0])); prev = p[1]
        bounds.append((prev, b))
        for i, (s, e) in zip(idx, bounds):
            out.append({"start": round(s, 2), "end": round(e, 2), "text": L[i]["text"]})
    for i in range(len(out) - 1):
        out[i]["end"] = round(min(out[i + 1]["start"], out[i]["end"] + 0.25), 2)
    YEARS = {"दो हज़ार बाईस": "2022", "दो हज़ार चौबीस": "2024", "दो हज़ार सत्ताईस": "2027", "दो हज़ार पच्चीस": "2025"}
    for o in out:
        for k, v in YEARS.items():
            o["text"] = o["text"].replace(k, v)
    for i, (o, l) in enumerate(zip(out, L)):
        print(f"{i:2d} {l['start']:7.2f} -> {o['start']:7.2f} {o['end']:7.2f}  {o['text']}")
    if "--write" in sys.argv:
        (proj / "lines_part1.srt.json").write_text(json.dumps(L, ensure_ascii=False, indent=1))
        (proj / "lines_part1.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
