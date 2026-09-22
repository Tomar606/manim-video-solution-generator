"""Move every sound cue onto the visual change it is meant to mark.

    python tools/snap_cues.py <background.mp4> <cues.json> [--window 0.8]

WHY THIS INSTEAD OF AN OFFSET
-----------------------------
A cue is emitted when the scene ASKS for an animation; the picture changes some
way into it, and how far in depends on the animation — a stage clearing peaks
mid-fade, an equation revealing peaks almost at once. Chasing that with a
constant offset took four rebuilds and never fitted both: +0.23 landed the
turnovers and pushed the reveals 0.45s out.

So this measures instead. It finds the frame-difference peaks the same way
sfx_gate does — the gate is the specification — and moves each cue onto the
nearest one. A cue with no peak inside `window` is marking nothing and is
dropped rather than moved, because inventing a change to justify a sound is the
exact failure sfx_gate exists to catch.

Run it on the BACKGROUND render, not the final: the presenter moves constantly
and his gestures swamp the stage's own changes.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.sfx_gate import events, stage_change  # noqa: E402



def attack(name: str) -> float:
    """Seconds from an effect's start to its loudest moment, PER THE REGISTRY.

    sfx_gate compares the effect's peak to the visual change, and it takes that
    offset from assets/sfx/registry.json — not from the wav. Measuring the file
    independently gave 0.09s for `write` where the registry says 0.239s, so the
    cue was placed to satisfy a number the gate does not use and failed on the
    one it does. Same source, same answer.
    """
    try:
        reg = json.loads((ROOT / "assets" / "sfx" / "registry.json")
                         .read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return 0.0
    return float((reg.get(name) or {}).get("peak_offset", 0.0))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("cues")
    ap.add_argument("--window", type=float, default=0.8)
    a = ap.parse_args()

    f = Path(a.cues)
    if not f.is_file():
        print(f"  no cues at {f}")
        return 0
    doc = json.loads(f.read_text(encoding="utf-8"))
    cues = doc.get("cues") or []
    if not cues:
        print("  no cues to snap")
        return 0

    # the same band the gate measures, so what this snaps to is what it checks
    diff, fps = stage_change(a.video)
    peaks = events(diff, fps)
    if not peaks:
        print("  no visual changes found — leaving cues alone")
        return 0

    kept, dropped, moved = [], 0, 0
    for c in cues:
        t = float(c["time"])
        near = min(peaks, key=lambda p: abs(p - t))
        if abs(near - t) > a.window:
            print(f"    {t:7.2f}s {c['name']}: no change within {a.window}s — dropped")
            dropped += 1
            continue
        want = max(0.0, near - attack(c["name"]))
        if abs(want - t) > 0.01:
            print(f"    {t:7.2f}s {c['name']} -> {want:7.2f}s "
                  f"(peak on {near:.2f}s, attack {attack(c['name']):.2f}s)")
            moved += 1
        c["time"] = round(want, 3)
        kept.append(c)

    # two effects on one peak are one effect played twice
    kept.sort(key=lambda c: c["time"])
    out = []
    for c in kept:
        if out and abs(c["time"] - out[-1]["time"]) < 0.35:
            continue
        out.append(c)

    doc["cues"] = out
    f.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    print(f"  {len(out)} cue(s) on measured peaks "
          f"({moved} moved, {dropped} dropped, {len(kept) - len(out)} merged)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
