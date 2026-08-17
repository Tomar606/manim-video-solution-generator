"""Times the presenter should step aside, read off the beats.

    python tools/presenter_windows.py projects/<slug> 1

The presenter is composited AFTER the Manim render, so a scene cannot hide him
itself — it can only declare that a beat wants the frame. This turns those
declarations into absolute time windows the compositor can act on, the same way
`avatar_windows.py` turns rendered content into resize windows.

A window opens when a beat marked `presenter: hidden` begins and closes when the
next beat that does NOT want the frame begins — so the presenter is away for the
whole demonstration rather than blinking out per beat. Windows shorter than
MIN_LEN are dropped: fading a presenter out and back inside three seconds reads
as a glitch, not as direction.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

MIN_LEN = 6.0        # a shorter absence reads as a glitch
MERGE_GAP = 4.0      # two absences this close become one
FADE = 0.9           # seconds of opacity ramp at each edge


def windows(beats, lines, clip_end):
    """Absolute [start, end] spans where the presenter should be faded out."""
    def t(idx):
        idx = max(0, min(int(idx), len(lines) - 1))
        return float(lines[idx]["start"])

    marked = sorted((b for b in beats if b.get("presenter") == "hidden"),
                    key=lambda b: b["at"])
    others = sorted((b["at"] for b in beats if b.get("presenter") != "hidden"))

    spans = []
    for b in marked:
        start = t(b["at"])
        after = [a for a in others if a > b["at"]]
        end = t(after[0]) if after else float(clip_end)
        spans.append([start, end])

    spans.sort()
    merged = []
    for a, z in spans:
        if merged and a - merged[-1][1] <= MERGE_GAP:
            merged[-1][1] = max(merged[-1][1], z)
        else:
            merged.append([a, z])
    return [[round(a, 2), round(z, 2)] for a, z in merged if z - a >= MIN_LEN]


def main() -> int:
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    root, part = Path(sys.argv[1]), sys.argv[2]
    beats = json.loads((root / f"beats_part{part}.json").read_text(encoding="utf-8"))
    lines = json.loads((root / f"lines_part{part}.json").read_text(encoding="utf-8"))
    meta = json.loads((root / "meta.json").read_text(encoding="utf-8"))
    clip_end = float(meta["clip_end"][str(part)])

    out = windows(beats, lines, clip_end)
    dest = root / f"presenter_part{part}.json"
    dest.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"{dest.name}: {len(out)} window(s) with the presenter faded out")
    for a, z in out:
        print(f"   {a:7.2f}s - {z:7.2f}s  ({z - a:.1f}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
