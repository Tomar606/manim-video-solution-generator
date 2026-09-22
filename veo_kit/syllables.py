"""Check that a spoken Hindi line fills one generated clip at a natural pace.

    python veo_kit/syllables.py "पहला कारण — मगध में खेती ..."
    python veo_kit/syllables.py --file projects/<slug>/veo/lines.json
    python veo_kit/syllables.py --measure          # his rate, from our own videos

WHY SYLLABLES AND NOT WORDS
---------------------------
Hindi words vary too much in length to budget with: है is one syllable,
महत्वाकांक्षी is six. Lines sized at "19 words or fewer" came out filling
4.0-5.5 seconds of an 8-second clip, and a generator handed dead time fills it
with invented speech — which is exactly the gibberish the first HIS-C2-LA-01
clips came back with.

THE BUDGET IS MEASURED
----------------------
300 caption lines across Ritesh sir's 8 short-answer videos: median 5.79
syllables/second, middle half 5.12-6.43. Google's spec says a clip with
reference images is 8 seconds; leave ~0.7s before the line and ~0.8s after it,
and 6.5 seconds of speech holds about 38 syllables. Below 33 there is dead air
for the model to fill; above 42 he has to rush.

Flow actually returned 10.0-second clips on 22 Sept 2026, and the budget held:
lines of 36-37 syllables filled 6.0-8.4 s, and the scripted actions before and
after the line took the rest with no invented speech. Keep the budget AND the
before/after actions; the actions are what absorb the extra two seconds.
"""
from __future__ import annotations

import argparse
import glob
import json
import re
import statistics
import sys

CONS = r"[क-हक़-य़]"
VOW = r"[ऄ-औॠ-ॡ]"
HAL = "्"
RATE = 5.79                     # his median syllables/second — see --measure
SPEECH = 6.5                    # seconds of an 8s clip that carry speech
LO, HI = 33, 42


def syllables(text: str) -> int:
    """Aksharas: every independent vowel, and every consonant not closed by a
    halant, carries one vowel sound. Latin words count by vowel groups."""
    n = 0
    for w in text.split():
        if re.search(r"[A-Za-z]", w):
            n += max(1, len(re.findall(r"[aeiouyAEIOUY]+", w)))
            continue
        n += len(re.findall(VOW, w))
        n += len([m for m in re.finditer(CONS, w) if w[m.end():m.end() + 1] != HAL])
    return n


def verdict(text: str) -> tuple[int, float, str]:
    s = syllables(text)
    sec = s / RATE
    if s < LO:
        return s, sec, f"SHORT by {LO - s} — dead air the model will fill"
    if s > HI:
        return s, sec, f"LONG by {s - HI} — he will rush"
    return s, sec, "ok"


def measure() -> int:
    """Re-measure his rate from the caption timings of finished PYQ videos.

    Needs projects/<slug>/lines_part1.json from real HeyGen takes, which only a
    machine that has built those videos has. The constants above are the result
    on 300 lines, so a fresh machine does not need to run this."""
    rates = []
    for f in sorted(glob.glob("projects/*/lines_part1.json")):
        if not re.search(r"(che|phy)-c\d+-sa-\d+", f):
            continue
        for l in json.load(open(f, encoding="utf-8")):
            d = l["end"] - l["start"]
            if d >= 1.2 and len(l["text"].split()) >= 3:
                rates.append(syllables(l["text"]) / d)
    if not rates:
        print("no caption lines found"); return 1
    q = statistics.quantiles(rates, n=4)
    print(f"{len(rates)} lines: median {statistics.median(rates):.2f} syl/s, "
          f"middle half {q[0]:.2f}-{q[2]:.2f}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("text", nargs="?")
    ap.add_argument("--file")
    ap.add_argument("--measure", action="store_true")
    a = ap.parse_args()
    if a.measure:
        return measure()
    lines = {}
    if a.file:
        d = json.load(open(a.file, encoding="utf-8"))
        lines = d if isinstance(d, dict) else {str(i): t for i, t in enumerate(d, 1)}
    elif a.text:
        lines = {"-": a.text}
    else:
        ap.error("give a line, --file or --measure")
    bad = 0
    for k, t in lines.items():
        s, sec, v = verdict(t)
        bad += v != "ok"
        print(f"  {k:>3}  {s:3d} syl  {sec:4.1f}s  {v}")
    print(f"\n  {len(lines) - bad}/{len(lines)} within {LO}-{HI} syllables "
          f"({LO / RATE:.1f}-{HI / RATE:.1f}s at {RATE}/s)")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
