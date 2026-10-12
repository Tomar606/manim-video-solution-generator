#!/usr/bin/env python3
"""Move an existing caption track onto measured word onsets, keeping its words.

    python tools/retime_lines.py lines_part1.json words_part1.json [--write]

WHY THIS EXISTS
---------------
A caption track can be right about WHAT is said and wrong about WHEN. That is
the failure mode nobody catches by reading the file: every line holds the
correct sentence, the totals add up, the last cue lands on the last word, and a
stretch in the middle is still two seconds behind the voice.

BIO-C12-LA-02 arrived that way. Its bundle reported "worst drift 0.00s", which
was true and useless — the drift had been measured against the same transcript
the captions were built from, so it could only ever agree with itself. Measured
against a FRESH transcription of the delivered audio, part 1 lines 15-23 ran
2.0 to 3.25 seconds late in one contiguous block.

WHY IT RETIMES INSTEAD OF REBUILDING
------------------------------------
`lines_from_words.py` would produce a better-cut track, but a different one:
different line count, different indices. Anchors, beat design and every `at`
offset in a design file are expressed in LINE INDICES, so rebuilding the track
silently invalidates the whole plan. This keeps the partition exactly as it is
and changes only the clock, so nothing downstream has to be re-derived.

HOW THE ALIGNMENT IS DONE
-------------------------
`difflib` over normalised tokens, not a forward scan. Caption text carries the
SCRIPT's spelling and the transcript carries whisper's, so a nearest-match walk
desynchronises on the first disagreement and reports nonsense from there on.
A longest-common-subsequence alignment steps over the disagreements instead.

A line with no matched token keeps its shape rather than being guessed at: it
is interpolated between the neighbours that did match, and reported.
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
import unicodedata
from pathlib import Path

GAP = 0.06          # daylight between one caption and the next
MIN_HOLD = 0.55     # a line never shorter than this if the room exists


def norm(s: str) -> str:
    """Letters, marks and digits — and the MARKS are the point.

    This was `re.sub(r"[^\\w]", "", s)`. Python's \\w does not match combining
    marks (Unicode Mn/Mc), so every Devanagari vowel sign and virama was
    deleted: पोषण -> पषण, पारिस्थितिक -> परसथतक. Both sides were stripped alike,
    so a correctly spelled word still matched itself — the damage was the
    opposite: different words collapse onto one consonant skeleton (पर, पार and
    पुर all become पर), and the alignment gains FALSE matches that can anchor a
    caption to the wrong word.
    """
    s = unicodedata.normalize("NFC", s)
    return "".join(ch for ch in s if unicodedata.category(ch)[0] in "LMN").lower()


def align(lines: list, words: list) -> tuple[dict, dict, int]:
    """(line -> first onset, line -> last offset, tokens matched).

    THE ONSET IS BACKED UP OVER THE LINE'S UNMATCHED LEADING TOKENS.
    ------------------------------------------------------------------
    Taking the first MATCHED token's onset as the line's start is wrong
    whenever the line's opening words did not match, and there are two common
    ways for that to happen:

      * a repeated phrase. BIO-C2-LA-01 part 3 line 10 ends `...विभाजन दो की
        बात` and line 11 opens `अर्धसूत्री विभाजन-दो में ...`. The LCS spends
        line 11's opening words against line 10's copy of them, so line 11's
        first surviving match is `में` — its FOURTH word — and the caption was
        placed at 68.53 when he starts saying it at 66.90. That is 1.66s late,
        measured independently by tools/srt_drift.py, and it is the single
        worst boundary in the video.
      * whisper misspelling the opening word, which it does freely in Hindi.

    Both look identical here: n leading tokens of the line produced no match.
    Those words were still SPOKEN, and they were spoken immediately before the
    first token that did match, so the line starts n words earlier in the
    transcript. Backing up by exactly that count recovers the onset without
    guessing at a duration.

    The walk back is clamped to the previous line's last matched word so a line
    can never reach back over its neighbour and claim words that are not its
    own - which is the failure a plain forward-only scan produces.
    """
    ltok, lidx = [], []
    line_head: dict[int, int] = {}          # line -> its first index in ltok
    line_tail: dict[int, int] = {}          # line -> its last index in ltok
    for i, l in enumerate(lines):
        for t in l["text"].split():
            if norm(t):
                line_head.setdefault(i, len(ltok))
                line_tail[i] = len(ltok)
                ltok.append(norm(t))
                lidx.append(i)
    wtok = [norm(w["w"]) for w in words]
    sm = difflib.SequenceMatcher(None, ltok, wtok, autojunk=False)

    # first/last MATCHED word index per line, in `words` coordinates
    first_w: dict[int, int] = {}
    first_l: dict[int, int] = {}            # ltok position of that first match
    last_w: dict[int, int] = {}
    last_l: dict[int, int] = {}
    hits = 0
    for a, b, size in sm.get_matching_blocks():
        hits += size
        for k in range(size):
            li = lidx[a + k]
            if li not in first_w:
                first_w[li], first_l[li] = b + k, a + k
            last_w[li], last_l[li] = b + k, a + k

    first: dict[int, float] = {}
    last: dict[int, float] = {}
    for li in sorted(first_w):
        prev = max((j for j in last_w if j < li), default=None)

        # PREFERRED: the first word the previous line did not claim.
        #
        # When the previous line matched all the way to its OWN last token,
        # every transcript word after that match belongs to this line, so this
        # line starts on the very next one. That is exact, and it does not care
        # how the two sides tokenise - which is what a leading-token count
        # cannot survive: the caption writes `अर्धसूत्री` as one word and
        # whisper returns it as two (`अर्द` + `सूत्री`), so counting the line's
        # unmatched leading tokens undercounts by one and lands the caption on
        # `विभाजन`, 0.70s into a line that has already begun.
        w0 = None
        if prev is not None and last_l.get(prev) == line_tail.get(prev):
            w0 = last_w[prev] + 1

        # FALLBACK: the previous line's own tail did not match, so words after
        # it may still be the previous line's. Step back over this line's
        # unmatched leading tokens instead, clamped so it cannot cross over.
        if w0 is None:
            w0 = first_w[li] - (first_l[li] - line_head[li])
            if prev is not None:
                w0 = max(w0, last_w[prev] + 1)

        first[li] = float(words[max(0, min(w0, first_w[li]))]["s"])
        last[li] = float(words[last_w[li]]["e"])
    return first, last, hits


def retime(lines: list, words: list, clip_end: float | None = None) -> dict:
    first, last, hits = align(lines, words)
    n = len(lines)
    missing = [i for i in range(n) if i not in first]

    # interpolate any line the alignment could not place, between its neighbours
    for i in missing:
        lo = max((j for j in first if j < i), default=None)
        hi = min((j for j in first if j > i), default=None)
        if lo is None and hi is None:
            first[i] = lines[i]["start"]
        elif lo is None:
            first[i] = max(0.0, first[hi] - 0.8)
        elif hi is None:
            first[i] = last.get(lo, first[lo]) + GAP
        else:
            span = first[hi] - first[lo]
            first[i] = first[lo] + span * (i - lo) / (hi - lo)

    end = float(clip_end) if clip_end else max(
        [last.get(i, first[i]) for i in range(n)] + [lines[-1]["end"]])

    out, moved = [], []
    starts = [first[i] for i in range(n)]
    # monotonic: a caption never starts before the one before it
    for i in range(1, n):
        starts[i] = max(starts[i], starts[i - 1] + 0.12)
    for i, l in enumerate(lines):
        s = round(max(0.0, starts[i]), 3)
        nxt = starts[i + 1] if i + 1 < n else end
        e = round(min(max(last.get(i, s + MIN_HOLD), s + MIN_HOLD), nxt - GAP), 3)
        if e <= s:
            e = round(min(nxt - 0.01, s + 0.2), 3)
        d = round(s - float(l["start"]), 3)
        if abs(d) > 0.3:
            moved.append((i, d))
        out.append({**l, "start": s, "end": e})
    return {"lines": out, "moved": moved, "missing": missing,
            "hits": hits, "tokens": sum(len(l["text"].split()) for l in lines)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("lines"); ap.add_argument("words")
    ap.add_argument("--clip-end", type=float, default=None)
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()
    lines = json.loads(Path(a.lines).read_text(encoding="utf-8"))
    W = json.loads(Path(a.words).read_text(encoding="utf-8"))
    words = W if isinstance(W, list) else W["words"]
    r = retime(lines, words, a.clip_end)
    print(f"  {Path(a.lines).name}: {r['hits']} token(s) aligned, "
          f"{len(r['missing'])} line(s) interpolated")
    late = [(i, d) for i, d in r["moved"] if d > 0]
    early = [(i, d) for i, d in r["moved"] if d < 0]
    print(f"  {len(r['moved'])} line(s) moved by more than 0.3s "
          f"({len(late)} were LATE, {len(early)} were EARLY)")
    for i, d in sorted(r["moved"], key=lambda x: -abs(x[1]))[:8]:
        print(f"     line {i:3d}  was {d:+.2f}s off   {lines[i]['text'][:44]}")
    if a.write:
        Path(a.lines).write_text(
            json.dumps(r["lines"], ensure_ascii=False, indent=1) + "\n",
            encoding="utf-8")
        print(f"  -> {a.lines}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
