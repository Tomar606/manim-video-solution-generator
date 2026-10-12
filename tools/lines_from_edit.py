#!/usr/bin/env python3
"""Captions from an EDITED transcript: corrected words, measured clock.

    python3 tools/lines_from_edit.py <words.json> <edit.json> <out_lines.json> \
        --clip-end 130.76

A drop with no SRT has one source of wording — whisper — and whisper cannot
spell Hindi: `वनशागती` for `वंशागति`, `rogue` for `रोग`, `पुरुशों` for
`पुरुषों`. Those cannot go on screen. `lines_from_words.py` also breaks lines on
a word count, so `है।` lands at the head of the next caption, which reads as
the caption running a word behind the voice.

So the text is corrected by hand, and the clock is not touched by hand at all.
The edit file names each caption as a RANGE OF TRANSCRIPT WORD INDICES plus the
corrected text for that range:

    [ {"w": [0, 9],  "text": "MP Board कक्षा 12 के बच्चों, ये सवाल 2020 में"},
      {"w": [10, 17], "text": "..."} ]

and this file derives every time from the words:

    start  = onset of word i                        (measured)
    end    = end of word j + TAIL, or — when the next caption starts within
             HOLD — held to the next start minus GAP, so the band does not
             blink empty across a breath (CLIP_VIDEO_RUNBOOK §5, "hold through
             short pauses"); a longer pause lets the band clear.

WHAT IT REFUSES
---------------
  * ranges that skip, overlap or reorder words — every spoken word belongs to
    exactly one caption, or a caption silently lost a phrase;
  * a line whose corrected text has drifted from the words it claims: the
    consonant skeletons (`tools.align.skel`) must agree at SIM or better. A
    range pointed one line off still "looks" right in the file and would put
    every later caption a sentence away from the voice;
  * a caption shorter than MIN_DUR, which cannot be read.
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.align import skel, spoken  # noqa: E402

TAIL = 0.18
HOLD = 0.80
GAP = 0.06
SIM = 0.55
MIN_DUR = 1.05


def sk(text: str) -> str:
    text = spoken(text)             # notation is compared as it is said (align.py)
    return "".join(skel(w) for w in re.sub(r"[।,.?!;:()\"'-]", " ", text).split())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("words"); ap.add_argument("edit"); ap.add_argument("out")
    ap.add_argument("--clip-end", type=float, required=True)
    a = ap.parse_args()
    words = json.loads(Path(a.words).read_text(encoding="utf-8"))
    edit = json.loads(Path(a.edit).read_text(encoding="utf-8"))

    errs, nxt = [], 0
    for k, e in enumerate(edit):
        i, j = e["w"]
        if i != nxt:
            errs.append(f"line {k}: starts at word {i}, expected {nxt}")
        if j < i:
            errs.append(f"line {k}: empty range {i}-{j}")
        nxt = j + 1
    if nxt != len(words):
        errs.append(f"ranges end at word {nxt - 1}, transcript has {len(words)} words")

    out = []
    for k, e in enumerate(edit):
        i, j = e["w"]
        got = " ".join(w["w"] for w in words[i:j + 1])
        r = difflib.SequenceMatcher(None, sk(got), sk(e["text"])).ratio()
        if r < SIM:
            errs.append(f"line {k}: text does not match its words (sim {r:.2f})\n"
                        f"      words: {got}\n      text:  {e['text']}")
        start = words[i]["s"]
        end = words[j]["e"] + TAIL
        if k + 1 < len(edit):
            ns = words[edit[k + 1]["w"][0]]["s"]
            end = ns - GAP if ns - words[j]["e"] <= HOLD else min(end, ns - GAP)
        else:
            end = min(max(end, words[j]["e"]), a.clip_end)
        # `w` travels with the line so tools/build_spec.py can anchor an
        # animation step to a WORD INDEX and check the word is inside the beat.
        out.append({"text": e["text"].strip(), "start": round(start, 3),
                    "end": round(end, 3), "words": j - i + 1, "w": [i, j],
                    "sim": round(r, 2)})

    for k, l in enumerate(out):
        # the SAME floor validate.py applies: 4.5 words/sec, never under
        # MIN_DUR. Checking only the flat floor here let a ten-word caption
        # held 2.10s through, and validate failed it two stages later.
        need = max(MIN_DUR, len(l["text"].split()) / 4.5)
        if l["end"] - l["start"] < need - 0.002:
            errs.append(f"line {k}: {l['end'] - l['start']:.2f}s is too short to read "
                        f"{len(l['text'].split())} words, needs {need:.2f}s ({l['text']!r})")
    mono = all(x["end"] <= y["start"] + 1e-6 for x, y in zip(out, out[1:]))
    if not mono:
        errs.append("track is not monotonic")

    Path(a.out).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    durs = sorted(l["end"] - l["start"] for l in out)
    print(f"  {len(out)} lines from {len(words)} words -> {a.out}")
    print(f"     duration min {durs[0]:.2f}s  median {durs[len(durs) // 2]:.2f}s  "
          f"max {durs[-1]:.2f}s   lowest sim {min(l['sim'] for l in out):.2f}")
    for x in errs:
        print(f"  FAIL {x}")
    return 1 if errs else 0


if __name__ == "__main__":
    raise SystemExit(main())
