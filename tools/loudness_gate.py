"""Refuse a finished video that is too quiet, too loud, or clips.

    python tools/loudness_gate.py <video.mp4> [--target -16] [--tolerance 1.5] [--peak -1.0]

The reels are watched on phones, one after another. One reel 4 dB quieter than the last reads as
broken, and a peak above full scale distorts on exactly the cheap speakers they play on. The
deliveries agree on about -16 LUFS; the Wheatstone reel (24 Oct 2026) still shipped with a true
peak of +0.2 dBFS, because nothing measured it. This measures it: EBU R128 integrated loudness and
true peak, from ffmpeg's ebur128 filter.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys


def measure(video: str) -> tuple[float, float]:
    err = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", video, "-vn", "-af", "ebur128=peak=true",
                          "-f", "null", "-"], capture_output=True, text=True).stderr
    summary = err[err.rfind("Summary:"):]
    i = re.search(r"I:\s+(-?[\d.]+) LUFS", summary)
    p = re.search(r"Peak:\s+(-?[\d.]+|-inf) dBFS", summary)
    if not i or not p:
        raise SystemExit(f"FAIL could not measure loudness of {video}")
    return float(i.group(1)), float("-inf") if p.group(1) == "-inf" else float(p.group(1))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("video")
    ap.add_argument("--target", type=float, default=-16.0)
    ap.add_argument("--tolerance", type=float, default=1.5)
    ap.add_argument("--peak", type=float, default=-1.0)
    a = ap.parse_args()
    lufs, peak = measure(a.video)
    bad = []
    if abs(lufs - a.target) > a.tolerance:
        bad.append(f"integrated {lufs:.1f} LUFS, want {a.target:.0f} ± {a.tolerance}")
    if peak > a.peak:
        bad.append(f"true peak {peak:+.1f} dBFS, want at or below {a.peak:.0f}")
    if bad:
        print("FAIL " + "; ".join(bad))
        return 1
    print(f"ok {lufs:.1f} LUFS, true peak {peak:+.1f} dBFS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
