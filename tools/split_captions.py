"""Split caption lines so each one fits ONE line of the reference look.

    python tools/split_captions.py projects/<slug> [--part 1] [--max 30]

The reference reel shows one short line at the top of the frame at all times.
Our SRT-derived lines run to 13 words and wrap to two lines, and a wrapped
line pushed its first row off the top of the frame. A line longer than `--max`
characters is cut at the word boundary nearest its middle, repeatedly, and its
time is divided by the words Whisper heard inside it — or by characters when
it heard none.

Beat line numbers move when lines split, so the beats file is REMAPPED in the
same run: every index a beat refers to (at, reveal_at, per-row at, *_at) points
at the first chunk of the line it used to name. So do meta.json's card_lines
and card_part<N>.json.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

MIN_ON = 0.80          # the checklist's shortest readable caption


def chunks(text: str, limit: int) -> list[str]:
    words = text.split()
    if len(text) <= limit or len(words) < 2:
        return [text]
    best, k = None, 1
    for i in range(1, len(words)):
        a, b = " ".join(words[:i]), " ".join(words[i:])
        d = abs(len(a) - len(b))
        if best is None or d < best:
            best, k = d, i
    return chunks(" ".join(words[:k]), limit) + chunks(" ".join(words[k:]), limit)


def split_lines(lines: list[dict], words: list[dict], limit: int):
    out, first = [], {}
    for i, l in enumerate(lines):
        parts = chunks(l["text"], limit)
        first[i] = len(out)
        if len(parts) == 1:
            out.append(l)
            continue
        s, e = float(l["start"]), float(l["end"])
        # BY CHARACTERS, not by Whisper's word times. The line's window and
        # Whisper's clock do not always agree, and splitting on the words that
        # fell inside the window gave chunks of 0.12s. Speech runs at a near
        # constant rate, so characters divide the time honestly; each chunk
        # then gets at least MIN_ON seconds if the line is long enough to allow it.
        total = sum(len(p) for p in parts)
        cuts, acc = [s], 0
        for p in parts[:-1]:
            acc += len(p)
            cuts.append(s + (e - s) * acc / total)
        cuts.append(e)
        if (e - s) >= MIN_ON * len(parts):
            for j in range(1, len(cuts) - 1):
                cuts[j] = max(cuts[j], cuts[j - 1] + MIN_ON)
            for j in range(len(cuts) - 2, 0, -1):
                cuts[j] = min(cuts[j], cuts[j + 1] - MIN_ON)
        for j, p in enumerate(parts):
            out.append(dict(l, start=round(cuts[j], 3), end=round(cuts[j + 1], 3), text=p))
    return out, first


def remap(obj, first):
    """Every *_at / at / reveal_at in a beat, pointed at the new first chunk.

    NOT EVERY NUMBER UNDER AN *_at KEY IS A LINE. `focus_at` is a list of
    [row, line] PAIRS — the revision pass walking the gold outline down a list
    that is already full — and remapping the row as though it were a line
    turned [[0,24],[1,26],[2,28],[3,30]] into rows 0,2,3,4 of a four-row list.
    Row 4 does not exist, so the last row of the revision silently never lit.
    A pair is remapped in its second position only.
    """
    def m(v, pair=False):
        if isinstance(v, int):
            return first.get(v, v)
        if isinstance(v, list):
            if pair and len(v) == 2 and all(isinstance(x, int) for x in v):
                return [v[0], m(v[1])]
            return [m(x, pair) for x in v]
        return v
    if isinstance(obj, list):
        return [remap(x, first) for x in obj]
    if isinstance(obj, dict):
        return {k: (m(v, pair=(k == "focus_at")) if (k == "at" or k.endswith("_at"))
                    else remap(v, first))
                for k, v in obj.items()}
    return obj


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--part", default="1")
    ap.add_argument("--max", type=int, default=30)
    a = ap.parse_args()
    root = Path(a.project)
    lp = root / f"lines_part{a.part}.json"
    wp = root / f"words_part{a.part}.json"
    lines = json.loads(lp.read_text(encoding="utf-8"))
    words = json.loads(wp.read_text(encoding="utf-8")) if wp.is_file() else []
    if isinstance(words, dict):
        words = words.get("words", [])
    new, first = split_lines(lines, words, a.max)
    lp.write_text(json.dumps(new, ensure_ascii=False, indent=1), encoding="utf-8")
    bp = root / f"beats_part{a.part}.json"
    if bp.is_file():
        bp.write_text(json.dumps(remap(json.loads(bp.read_text(encoding="utf-8")), first),
                                 ensure_ascii=False, indent=1), encoding="utf-8")
    mp = root / "meta.json"
    meta = json.loads(mp.read_text(encoding="utf-8"))
    cl = meta.get("card_lines")
    if isinstance(cl, dict) and a.part in cl:
        cl[a.part] = first.get(int(cl[a.part]), int(cl[a.part]))
        mp.write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    cp = root / f"card_part{a.part}.json"
    if cp.is_file() and isinstance(cl, dict) and a.part in cl:
        k = int(cl[a.part]) - 1
        cp.write_text(json.dumps([[0.0, round(float(new[k]["end"]), 2)]]))
    short = [round(l["end"] - l["start"], 2) for l in new if l["end"] - l["start"] < 0.8]
    print(f"  {len(lines)} lines -> {len(new)}; longest {max(len(l['text']) for l in new)} chars; "
          f"{len(short)} under 0.8s {short}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
