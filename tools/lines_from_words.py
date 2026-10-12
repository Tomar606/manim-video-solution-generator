#!/usr/bin/env python3
"""Build a caption track whose every boundary is a MEASURED word onset.

    python tools/lines_from_words.py <words.json> <out_lines.json> [--srt out.srt]

WHY NOT SPLIT THE SRT INSTEAD
-----------------------------
PROCESS.md step 3 is "the SRT keeps its words and loses its clock": a delivered
SRT carries the exact wording and approximate times, so you keep the text and
re-time it. BIO-C5-LA-01 shipped with NO SRT — the only transcript is Whisper's
own, whose long-form segmentation produced cues of 17 and 24 seconds. Splitting
those by hand invents every boundary inside them, and an invented boundary is
the whole failure the step exists to prevent.

So when the words are all you have, the lines are built FROM the words and every
start is an onset that was measured rather than chosen. The tool that splits a
real SRT is a different tool, and this one does not pretend to be it.

WHERE THE BREAKS GO, AND WHY
----------------------------
In order of preference:

  a PAUSE          a gap >= PAUSE between two words is where the speaker
                   actually stopped, and a caption that changes there reads as
                   natural. This outranks everything below it.
  PUNCTUATION      a danda or comma, if the line already has MIN_WORDS.
  MAX_WORDS        the backstop. Ten words is the house maximum; past that the
                   band needs three lines at the smallest size.

A line never ends mid-pause-free-run under MIN_WORDS, because a 2-word caption
flashing for 0.4s is less readable than a slightly long one — measured on
BIO-C2-LA-01, where the aligner bunched lines onto one word and fanned them out
into 0.35s flashes.

ENDS
----
`end` is the last word's measured end plus TAIL, clamped so it never reaches the
next line's start. A caption that outlives its own words reads as lagging; one
that is cut short reads as flickering. Where the following gap is a real pause
(> HOLD) the caption comes down and the band goes quiet, which is what a pause
should look like.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

MIN_WORDS = 4
MAX_WORDS = 10
PAUSE = 0.42        # a gap this long is where the speaker stopped
HOLD = 0.80         # a gap longer than this is a real beat: let the band clear
TAIL = 0.18         # how long a caption outlives its last word
GAP = 0.06          # daylight between consecutive captions
BREAK = re.compile(r"[।?!,;:]$")


def build(words: list[dict], clip_end: float | None = None) -> list[dict]:
    lines, cur = [], []
    for i, w in enumerate(words):
        cur.append(w)
        nxt = words[i + 1] if i + 1 < len(words) else None
        gap = (nxt["s"] - w["e"]) if nxt else 999.0
        if nxt is None:
            break
        if len(cur) >= MAX_WORDS:
            lines.append(cur); cur = []
        elif len(cur) >= MIN_WORDS and (gap >= PAUSE or BREAK.search(w["w"])):
            lines.append(cur); cur = []
    if cur:
        lines.append(cur)

    # a trailing runt is absorbed rather than left to flash
    if len(lines) > 1 and len(lines[-1]) < MIN_WORDS:
        lines[-2] += lines.pop()

    out = []
    for k, ws in enumerate(lines):
        start = ws[0]["s"]
        end = ws[-1]["e"] + TAIL
        if k + 1 < len(lines):
            # The clamp against the next line's start is applied LAST and is
            # never overridden. A minimum-duration floor used to run after it
            # and pushed every caption 0.02s past its successor — 32 of 36
            # boundaries overlapped, which renders as the outgoing caption
            # flickering under the incoming one. If a line ever comes out too
            # short, that is reported below, not silently corrected by
            # borrowing time the next line owns.
            end = min(end, lines[k + 1][0]["s"] - GAP)
        if k + 1 == len(lines) and clip_end is not None:
            # the last caption may not outlive the clip: composite.py cuts the
            # background to the clip length, so a caption past the end is drawn
            # on a frame that does not exist
            end = min(end, clip_end)
        out.append({"text": " ".join(x["w"] for x in ws).strip(),
                    "start": round(start, 3), "end": round(end, 3),
                    "words": len(ws)})
    return out


def ts(x: float) -> str:
    h, r = divmod(x, 3600); m, s = divmod(r, 60)
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int(round((s % 1) * 1000)):03d}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("words"); ap.add_argument("out"); ap.add_argument("--srt")
    ap.add_argument("--clip-end", type=float, default=None)
    a = ap.parse_args()
    words = json.loads(Path(a.words).read_text(encoding="utf-8"))
    lines = build(words, a.clip_end)
    Path(a.out).write_text(json.dumps(lines, ensure_ascii=False, indent=1),
                           encoding="utf-8")
    if a.srt:
        Path(a.srt).write_text(
            "\n".join(f"{i}\n{ts(l['start'])} --> {ts(l['end'])}\n{l['text']}\n"
                      for i, l in enumerate(lines, 1)), encoding="utf-8")

    durs = sorted(l["end"] - l["start"] for l in lines)
    short = [l for l in lines if l["end"] - l["start"] < 0.8]
    mono = all(a_["end"] <= b_["start"] + 1e-6 for a_, b_ in zip(lines, lines[1:]))
    print(f"  {len(lines)} lines from {len(words)} words -> {a.out}")
    print(f"     duration  min {durs[0]:.2f}s  median {durs[len(durs)//2]:.2f}s  "
          f"max {durs[-1]:.2f}s")
    print(f"     words/line  min {min(l['words'] for l in lines)}  "
          f"max {max(l['words'] for l in lines)}")
    print(f"     monotonic {mono}   under 0.8s: {len(short)}")
    for l in short:
        print(f"       short {l['start']:7.2f}-{l['end']:7.2f}  {l['text'][:40]!r}")
    return 0 if mono and not short else 1


if __name__ == "__main__":
    raise SystemExit(main())
