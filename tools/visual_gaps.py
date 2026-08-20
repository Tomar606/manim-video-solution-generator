"""Report stretches where the graphic area sits empty.

    python tools/visual_gaps.py che-c1-la-01

The stage clears when the question card comes down and stays empty until the
first beat, and a beat holds the screen until the next one replaces it. So the
holes are the span between the card clearing and the first beat, plus any span
after a beat that explicitly clears to nothing.

Anything longer than MIN_EMPTY is dead screen: the presenter is talking and the
area above him is blank. The fix is a topic image, not a rearranged beat — see
tools/fill_visual_gaps.py.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

MIN_EMPTY = 3.0


def gaps(root: Path, part: int) -> list[tuple[float, float]]:
    lines = json.loads((root / f"lines_part{part}.json").read_text(encoding="utf-8"))
    beats = json.loads((root / f"beats_part{part}.json").read_text(encoding="utf-8"))
    meta = json.loads((root / "meta.json").read_text(encoding="utf-8"))
    cl = meta.get("card_lines", 0)
    card_until = int(cl[str(part)] if isinstance(cl, dict) else cl)

    def t(i):
        i = max(0, min(int(i), len(lines) - 1))
        return float(lines[i]["start"])

    out = []
    if beats:
        first = min(int(b["at"]) for b in beats)
        if t(first) - t(card_until) >= MIN_EMPTY:
            out.append((t(card_until), t(first)))
    else:
        out.append((t(card_until), float(meta["clip_end"][str(part)])))
    return out


def main() -> int:
    slug = sys.argv[1]
    root = Path("projects") / slug
    total = 0.0
    for f in sorted(root.glob("lines_part*.json")):
        part = int(f.stem.split("part")[1])
        for a, b in gaps(root, part):
            print(f"  {slug} part{part}: empty {a:6.1f}s - {b:6.1f}s  ({b - a:.1f}s)")
            total += b - a
    if total:
        print(f"  -> {total:.1f}s of empty graphic area")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
