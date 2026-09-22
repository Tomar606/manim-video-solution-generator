"""Mix a scene's sound cues onto the narration track.

    python tools/mix_cues.py <narration.(mp4|wav)> <cues.json> <out.wav> [--asset-root DIR]

The scenes emit `(time, name, gain)` while they render — see src/sfx.py. The PYQ
build muxes the HeyGen take's audio straight onto the composited video, so there
was nowhere for those cues to land. This is that step: it reads the sidecar, mixes
each effect onto the narration at its own timestamp, and writes a new track the
build muxes instead.

The cue times are scene-relative and the PYQ scene IS the whole part, so no
offset is needed — unlike the reels track, where each segment is a separate clip.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src import sfx  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("narration")
    ap.add_argument("cues")
    ap.add_argument("out")
    ap.add_argument("--asset-root", default=str(ROOT))
    a = ap.parse_args()

    if not Path(a.cues).is_file():
        print(f"  no cues at {a.cues} — nothing to mix")
        return 0
    sfx.ensure_library(a.asset_root)
    cues = sfx.read_cue_file(a.cues)
    if not cues:
        print("  cue file is empty — nothing to mix")
        return 0
    sfx.mix(a.narration, cues, a.out, asset_root=a.asset_root)
    print(f"  mixed {len(cues)} cue(s) -> {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
