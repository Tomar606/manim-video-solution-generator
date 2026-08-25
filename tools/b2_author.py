"""Helpers for authoring batch-2 beats from a storyboard.

The storyboard is written in TIMES because that is how a director thinks; the
renderer works in CAPTION INDICES because a beat must land on the sentence that
earns it. `at()` converts, choosing the caption whose start is nearest the
storyboard's time — never the caption that merely contains it, which drifts a
beat onto the tail of the previous sentence.
"""
from __future__ import annotations

import json
from pathlib import Path


def lines(slug: str, part: int):
    return json.loads(
        (Path("projects") / slug / f"lines_part{part}.json").read_text(encoding="utf-8"))


def at(L, t: float) -> int:
    """Caption index whose start is nearest t."""
    return min(range(len(L)), key=lambda i: abs(float(L[i]["start"]) - t))


def write(slug: str, part: int, beats: list) -> None:
    beats = sorted(beats, key=lambda b: int(b["at"]))
    dest = Path("projects") / slug / f"beats_b2_part{part}.json"
    dest.write_text(json.dumps(beats, ensure_ascii=False, indent=1), encoding="utf-8")
    L = lines(slug, part)
    print(f"  {slug} p{part}: {len(beats)} beats")
    for b in beats:
        i = int(b["at"])
        lab = b.get("title") or b.get("label") or (b.get("cols") or [""])[0]
        print(f"     {L[i]['start']:6.1f}s  {b['type']:8} {str(lab)[:38]}")
