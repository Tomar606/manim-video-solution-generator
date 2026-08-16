"""Fill stretches where the presenter is speaking but no caption appears.

    python tools/fill_caption_gaps.py projects/<slug>/lines_part1.json \
        projects/<slug>/words_part1.json

`captions_from_audio.py` matches the transcript against the script so it can fix
Whisper's spelling. Where the presenter says something the script never had —
reading an equation aloud, an aside, a repeated line — there is nothing to match
against, and the line is dropped rather than spelt wrong. On the KMnO4 clip that
left two holes of 14.5s and 12.6s with the presenter talking and the screen
silent, which is the caption/audio mismatch this pipeline exists to prevent.

So: any gap longer than MAX_GAP is refilled straight from the transcript, split
into caption-length lines on the pauses between words. The words are Whisper's
own, spelling included — unmatched text cannot be corrected against a script,
and showing what was actually said beats showing nothing.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

MAX_GAP = 4.0          # seconds of speech with no caption before we step in
MAX_HOLD = 7.0         # a single caption held longer than this is not one line
MAX_CHARS = 46         # a caption line is one breath, not one paragraph
SPLIT_PAUSE = 0.34     # a pause this long is a natural line break


def words_between(words, lo, hi):
    return [w for w in words if w["s"] >= lo - 0.05 and w["e"] <= hi + 0.05]


def to_lines(chunk):
    """Group words into caption-length lines, breaking on pauses."""
    out, cur = [], []
    for i, w in enumerate(chunk):
        cur.append(w)
        text = " ".join(x["w"] for x in cur)
        nxt = chunk[i + 1] if i + 1 < len(chunk) else None
        pause = (nxt["s"] - w["e"]) if nxt else 99
        if len(text) >= MAX_CHARS or pause >= SPLIT_PAUSE or nxt is None:
            out.append({"start": round(cur[0]["s"], 2),
                        "end": round(cur[-1]["e"], 2),
                        "text": text})
            cur = []
    return out


def fill(lines_path: Path, words_path: Path) -> int:
    lines = json.loads(lines_path.read_text(encoding="utf-8"))
    words = json.loads(words_path.read_text(encoding="utf-8"))
    if not lines or not words:
        return 0

    filled, added = [], 0
    for i, line in enumerate(lines):
        nxt_start = lines[i + 1]["start"] if i + 1 < len(lines) else words[-1]["e"]
        end = float(line.get("end", line["start"]))

        # A caption HELD across a long stretch is the same defect as a blank
        # one, and it is the form it actually took: the track had no holes, it
        # had one line sitting on screen for 14.5s while the presenter read an
        # equation aloud. Anything held past MAX_HOLD is rebuilt from what was
        # actually said in that window.
        span = nxt_start - float(line["start"])
        if span > MAX_HOLD:
            chunk = words_between(words, float(line["start"]), nxt_start)
            if len(chunk) >= 4:
                new = to_lines(chunk)
                filled.extend(new)
                added += len(new) - 1
                continue

        filled.append(line)
        if nxt_start - end > MAX_GAP:
            chunk = words_between(words, end, nxt_start)
            if len(chunk) >= 3:
                new = to_lines(chunk)
                filled.extend(new)
                added += len(new)

    filled.sort(key=lambda l: l["start"])
    lines_path.write_text(json.dumps(filled, ensure_ascii=False, indent=2),
                          encoding="utf-8")
    return added


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    n = fill(Path(sys.argv[1]), Path(sys.argv[2]))
    print(f"{Path(sys.argv[1]).name}: {n} caption line(s) recovered from the "
          f"transcript" if n else f"{Path(sys.argv[1]).name}: no gaps to fill")
