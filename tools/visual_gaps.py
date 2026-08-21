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
MAX_STATIC = 20.0     # a block nobody changes for this long is dead screen


def static_spans(root: Path, part: int) -> list[tuple[float, float, str]]:
    """Stretches where one block sits unchanged for too long.

    `gaps()` finds screen that is EMPTY. This finds screen that is FROZEN, which
    looks fine in a still and is just as dead in motion: the Daniell cell held
    its last block for 57 of its 112 seconds — over half the video — and nothing
    flagged it, because something was technically on the stage the whole time.

    A beat holds until the next one replaces it, so the span of the LAST beat
    runs to the end of the clip. That is usually the longest and the worst.
    """
    lines = json.loads((root / f"lines_part{part}.json").read_text(encoding="utf-8"))
    beats = sorted(json.loads((root / f"beats_part{part}.json").read_text(encoding="utf-8")),
                   key=lambda b: int(b["at"]))
    meta = json.loads((root / "meta.json").read_text(encoding="utf-8"))
    end = float(meta["clip_end"][str(part)])

    def t(i):
        i = max(0, min(int(i), len(lines) - 1))
        return float(lines[i]["start"])

    out = []
    for n, b in enumerate(beats):
        start = t(b["at"])
        stop = t(beats[n + 1]["at"]) if n + 1 < len(beats) else end
        # anything that ARRIVES during the block counts as a change: a list
        # filling in, and a diagram whose labels are named one at a time. Without
        # the labels a fully-annotated figure read as frozen for its whole span.
        changes = [t(r) for r in b.get("reveal_at", [])]
        changes += [t(l["at"]) for l in b.get("labels", [])]
        changes += [t(st.get("at", b["at"])) for st in b.get("steps", [])]
        last_change = max([start] + changes)
        if stop - last_change >= MAX_STATIC:
            out.append((last_change, stop,
                        f"{b['type']} {b.get('title') or b.get('label') or ''}".strip()))
    return out


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
            print(f"  {slug} part{part}: EMPTY  {a:6.1f}s - {b:6.1f}s  ({b - a:.1f}s)")
            total += b - a
        for a, b, what in static_spans(root, part):
            print(f"  {slug} part{part}: FROZEN {a:6.1f}s - {b:6.1f}s  ({b - a:.1f}s) — {what}")
            total += b - a
    if total:
        print(f"  -> {total:.1f}s of empty graphic area")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
