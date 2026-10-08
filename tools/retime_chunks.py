"""Put short one-line caption chunks on the audio's own word clock.

    python tools/retime_chunks.py projects/<slug> [--part 1]

For the reference look's one-line captions (tools/split_captions.py). The
windowed retimer (retime_lines.py) was built for long lines; on 30-character
chunks it bunched three consecutive chunks into 0.44-0.49s each and stretched
the line before them to 5.25s, because the SRT times it starts from are out by
up to 2.2s (memory: heygen-srt-timings-are-wrong).

This anchors every chunk GLOBALLY with tools.align.anchor (difflib over the
whole transcript — the aligner that placed 22/30 lines where a window search
placed 2), interpolates the few it cannot anchor, ends each chunk where the next
begins (or shortly after its last word, before a real pause), and then makes
sure no chunk is on screen for less than MIN_ON by borrowing from a neighbour
that can spare it.
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.align import anchor, skel, toks  # noqa: E402

MIN_ON = 0.80
PAUSE = 1.20        # a gap longer than this is a pause: the caption comes down
TAIL = 0.30


def retime(lines: list[dict], words: list[dict]) -> list[dict]:
    texts = [l["text"] for l in lines]
    starts, ratio, hits = anchor(texts, words)
    n = len(lines)
    # interpolate the unanchored by character count between known neighbours
    known = [i for i, s in enumerate(starts) if s is not None]
    if not known:
        return lines
    for i in range(n):
        if starts[i] is not None:
            continue
        a = max([k for k in known if k < i], default=None)
        b = min([k for k in known if k > i], default=None)
        if a is None:
            starts[i] = max(0.0, starts[b] - 0.08 * sum(len(texts[j]) for j in range(i, b)))
        elif b is None:
            starts[i] = starts[a] + 0.08 * sum(len(texts[j]) for j in range(a, i))
        else:
            span = sum(len(texts[j]) for j in range(a, b)) or 1
            starts[i] = starts[a] + (starts[b] - starts[a]) * \
                sum(len(texts[j]) for j in range(a, i)) / span
    for i in range(1, n):                      # never before the previous one
        starts[i] = max(starts[i], starts[i - 1] + 0.30)
    clip_end = max(float(lines[-1]["end"]), words[-1]["e"] if words else 0)
    out = []
    for i in range(n):
        s = starts[i]
        nxt = starts[i + 1] if i + 1 < n else clip_end
        # last word spoken inside this chunk's slot
        inside = [w["e"] for w in words if s - 0.05 <= w["s"] < nxt]
        e = nxt
        if inside and nxt - max(inside) > PAUSE:
            e = max(inside) + TAIL
        out.append(dict(lines[i], start=round(s, 3), end=round(min(e, nxt), 3)))
    # no flashes: borrow time from a neighbour that can spare it
    for i, l in enumerate(out):
        short = MIN_ON - (l["end"] - l["start"])
        if short <= 0:
            continue
        if i > 0 and (out[i - 1]["end"] - out[i - 1]["start"]) - short >= MIN_ON:
            out[i - 1]["end"] = round(out[i - 1]["end"] - short, 3)
            l["start"] = round(l["start"] - short, 3)
        elif i + 1 < len(out) and (out[i + 1]["end"] - out[i + 1]["start"]) - short >= MIN_ON:
            l["end"] = round(l["end"] + short, 3)
            out[i + 1]["start"] = round(out[i + 1]["start"] + short, 3)
    return out


def score(lines, words):
    ov = []
    for l in lines:
        heard = {skel(w["w"]) for w in words if w["s"] < l["end"] and w["e"] > l["start"]}
        t = toks(l["text"])
        ov.append(sum(1 for x in t if x in heard) / max(1, len(t)))
    return ov


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--part", default="1")
    a = ap.parse_args()
    root = Path(a.project)
    lp, wp = root / f"lines_part{a.part}.json", root / f"words_part{a.part}.json"
    lines = json.loads(lp.read_text(encoding="utf-8"))
    words = json.loads(wp.read_text(encoding="utf-8"))
    before = statistics.median(score(lines, words))
    new = retime(lines, words)
    ov = score(new, words)
    lp.write_text(json.dumps(new, ensure_ascii=False, indent=1), encoding="utf-8")
    short = [i for i, l in enumerate(new) if l["end"] - l["start"] < MIN_ON]
    print(f"  {lp.name}: overlap median {before:.0%} -> {statistics.median(ov):.0%}; "
          f"{sum(o < 0.3 for o in ov)} under 30%; {len(short)} under {MIN_ON}s {short}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
