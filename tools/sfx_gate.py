"""Refuse to ship sound that marks nothing, or marks it at the wrong moment.

    python tools/sfx_gate.py <video.mp4> <cues.json> [--tol 0.20] [--band TOP:HEIGHT]

WHY THIS EXISTS
---------------
On the first biology demo three pops were placed on "the three labels appearing".
The labels were baked into a static diagram PNG and had never appeared at all, so
three sounds played over a picture that did not change. Nothing in the pipeline
noticed: the mix succeeded, the file played, and only watching it caught the lie.

A sound effect is a CLAIM that something happened on screen. This checks the
claim against the picture.

WHAT IT CHECKS
--------------
1. EVERY CUE MARKS A REAL EVENT. The stage band is sampled and frame-to-frame
   change measured; a cue with no visual change near it FAILS.
2. THE PEAK LANDS ON THE EVENT, not the file's start. Effects with a build (the
   swoosh peaks 43% in) must be started early; the registry carries the measured
   offset per effect and the gate compares peak time, not start time.
3. NO CUE FIRES ON A CAPTION. The band deliberately excludes the subtitle strip
   and the presenter, so a caption change or a gesture cannot satisfy a cue.
4. NO STACKING. Two cues inside 0.12s read as one thickened sound, not two —
   UNLESS the later one is marked `"layer": true`, which declares that it is
   meant to thicken the one before it. A transition is one moment carried by a
   whoosh cresting and a low accent landing together; that is a layer, not two
   claims. An accidental stack still fails, because it will not be marked.

Unmarked events are reported but never fail: silence is a legitimate choice, and
most of a video should have none.

TWO THINGS IT CANNOT SEE — verify these by hand before dismissing a FAIL
-----------------------------------------------------------------------
`events()` takes the frame-to-frame delta over the whole band and keeps local
maxima above the 92nd percentile OF THE WHOLE VIDEO. That works when the stage
is still between events. It does not work when the picture is continuously in
motion:

1. A LABEL FADING IN OVER A MOVING MAP. On HIS-C2-SA-06 the camera pans and
   flies for most of every map segment, so the floor is high and a label fading
   up over 0.45s never reaches it — all five correct pops were reported as
   marking nothing. Confirmed by measuring the label ink itself inside the
   window: it rose by 1000 to 1500 px across each cue.
2. THE ARRIVAL AT A HELD STATE. A fade to black ENDS in zero change, so the
   moment the picture actually lands on dark registers as no event at all, and
   an accent placed there reads as marking nothing.

Both want a detector with local prominence rather than one global floor. Until
then: a FAIL on a moving background or on the end of a fade is a prompt to
measure that specific thing, not proof the cue is wrong.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

# The band a cue may be justified by: below the caption strip, above the
# presenter at full size. Content lives here and nothing else does.
#
# It is a DEFAULT, not a constant, because the layout is no longer only one. The
# biology split puts the animation panel at the TOP and the presenter below a
# torn divider, so the band that excludes him there is 0:540 — with 420:580 the
# band overlaps his head at full size and a HAND GESTURE can satisfy a cue,
# which is the exact failure this gate was written to catch. Pass --band.
BAND_TOP, BAND_H = 420, 580
FPS = 10
REGISTRY = Path("assets/sfx/registry.json")


def stage_change(video: Path, band: tuple[int, int] = (BAND_TOP, BAND_H)) -> tuple[np.ndarray, float]:
    top, height = band
    with tempfile.TemporaryDirectory() as td:
        subprocess.run(["ffmpeg", "-v", "error", "-i", str(video), "-vf",
                        f"fps={FPS},crop=1080:{height}:0:{top},scale=192:-1",
                        f"{td}/f%05d.png"], check=True)
        fr = sorted(Path(td).glob("*.png"))
        a = np.stack([np.asarray(Image.open(p).convert("L")).astype(float) for p in fr])
    return np.abs(np.diff(a, axis=0)).mean(axis=(1, 2)), FPS


def events(diff: np.ndarray, fps: float) -> list[float]:
    floor = max(0.25, float(np.percentile(diff, 92)))
    out: list[float] = []
    for i in range(1, len(diff) - 1):
        if diff[i] >= floor and diff[i] >= diff[i-1] and diff[i] >= diff[i+1]:
            t = (i + 1) / fps
            if not out or t - out[-1] > 0.8:
                out.append(round(t, 2))
    return out


def check(video: Path, cues: list[dict], tol: float,
          band: tuple[int, int] = (BAND_TOP, BAND_H)) -> list[str]:
    reg = json.loads(REGISTRY.read_text(encoding="utf-8")) if REGISTRY.is_file() else {}
    diff, fps = stage_change(video, band)
    ev = events(diff, fps)
    bad: list[str] = []

    peaks = []
    for c in cues:
        name = str(c.get("name", "pop"))
        off = float(reg.get(name, {}).get("peak_offset", 0.0))
        peaks.append((float(c["time"]) + off, name, float(c["time"])))

    for pk, name, start in sorted(peaks):
        near = min((abs(pk - e) for e in ev), default=99.0)
        if near > tol:
            bad.append(f"{pk:7.2f}s  {name}: marks NOTHING — nearest change is "
                       f"{near:.2f}s away (tolerance {tol:.2f}s)")
        elif near > tol * 0.6:
            bad.append(f"{pk:7.2f}s  {name}: LATE/EARLY by {near:.2f}s "
                       f"(cue starts {start:.2f}s, peaks {pk:.2f}s)")

    marked = sorted(((float(c["time"]) + float(reg.get(str(c.get("name", "pop")), {})
                      .get("peak_offset", 0.0)), c.get("layer"))
                     for c in cues), key=lambda x: x[0])
    for (a, la), (b, lb) in zip(marked, marked[1:]):
        # a shared layer id means the two were WRITTEN to land together
        if b - a < 0.12 and not (la is not None and la == lb):
            bad.append(f"{a:7.2f}s  two cues {b-a:.3f}s apart — they read as one sound")

    unmarked = [e for e in ev if min((abs(e - p[0]) for p in peaks), default=99) > tol]
    if unmarked:
        print(f"   note: {len(unmarked)} visual change(s) with no sound "
              f"(fine — silence is a choice): {unmarked[:8]}")
    return bad


def main() -> int:
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    video, cue_file = Path(sys.argv[1]), Path(sys.argv[2])
    tol = 0.20
    if "--tol" in sys.argv:
        tol = float(sys.argv[sys.argv.index("--tol") + 1])
    band = (BAND_TOP, BAND_H)
    if "--band" in sys.argv:
        top, _, height = sys.argv[sys.argv.index("--band") + 1].partition(":")
        band = (int(top), int(height))
    cues = json.loads(cue_file.read_text(encoding="utf-8"))
    if isinstance(cues, dict):
        cues = cues.get("cues", [])
    bad = check(video, cues, tol, band)
    if bad:
        print(f"  SFX GATE FAILED — {video.name}")
        for b in bad:
            print(f"    {b}")
        return 1
    print(f"  sfx ok: {video.name} ({len(cues)} cue(s) all land on a real change, "
          f"band {band[0]}..{band[0] + band[1]})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
