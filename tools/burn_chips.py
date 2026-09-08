"""Lay overlay chips onto a FINISHED video, one ffmpeg pass.

    python tools/burn_chips.py <in.mp4> <out.mp4> <plan.json>

`plan.json` is a list of {png, start, end}. Each chip is dropped at y=BAND_TOP,
fades in and out over FADE seconds and is on screen for nothing else.

WHY A SEPARATE PASS
-------------------
The video is already rendered, composited, gated and approved. An addition that
sits in the empty band does not need any of that redone -- and redoing it would
put the approved picture at risk for the sake of a caption card. So the chips go
on top of the finished file and the audio stream is copied through untouched.

THE TIMING
----------
`tpad` pads the front of each chip with TRANSPARENT frames so overlay always has
a second input to read; without it overlay stalls waiting for frames that do not
exist yet and the chip lands at the start of the video instead of its window.
`fps` after tpad pins the padded frames to the 1/30 grid -- pad frames off the
grid get generated and then dropped, which is how a clip came out a tenth of a
second short once before.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

BAND_TOP = 380       # the stage band: diagrams and equations already live here
FADE = 0.35
FPS = 30


def burn(src: Path, out: Path, plan: list[dict]) -> None:
    inputs: list[str] = []
    parts: list[str] = []
    for i, c in enumerate(plan, start=1):
        dur = round(c["end"] - c["start"], 3)
        if dur <= 2 * FADE:
            raise SystemExit(f"{c['png']}: window {dur}s is shorter than its fades")
        inputs += ["-loop", "1", "-framerate", str(FPS), "-t", f"{dur}",
                   "-i", str(c["png"])]
        parts.append(
            f"[{i}:v]format=rgba,"
            f"fade=t=in:st=0:d={FADE}:alpha=1,"
            f"fade=t=out:st={dur - FADE:.3f}:d={FADE}:alpha=1,"
            f"tpad=start_duration={c['start']:.3f}:start_mode=add:color=black@0,"
            f"fps={FPS}[c{i}]")

    chain, last = [], "0:v"
    for i, c in enumerate(plan, start=1):
        lbl = f"v{i}"
        chain.append(f"[{last}][c{i}]overlay=0:{BAND_TOP}:eof_action=pass:"
                     f"enable='between(t,{c['start']:.3f},{c['end']:.3f})'[{lbl}]")
        last = lbl
    fc = ";".join(parts + chain)

    threads = os.environ.get("FFMPEG_THREADS", "2")
    tmp = out.with_suffix(".partial.mp4")
    cmd = ["ffmpeg", "-v", "error", "-threads", threads,
           "-filter_threads", threads, "-filter_complex_threads", threads,
           "-i", str(src), *inputs,
           "-filter_complex", fc, "-map", f"[{last}]", "-map", "0:a?",
           "-c:v", "libx264", "-preset", "medium", "-crf", "19",
           "-pix_fmt", "yuv420p", "-r", str(FPS), "-fps_mode", "cfr",
           "-threads", threads, "-c:a", "copy",
           "-movflags", "+faststart", str(tmp), "-y"]
    print(f"burning {len(plan)} chip(s) -> {out}")
    subprocess.run(cmd, check=True)

    errs = subprocess.run(["ffmpeg", "-v", "error", "-i", str(tmp), "-f", "null", "-"],
                          capture_output=True, text=True).stderr.strip()
    if errs:
        raise SystemExit(f"{tmp} decodes with errors, not moving into place:\n"
                         f"{errs.splitlines()[0]}")
    tmp.replace(out)

    # CARRY THE GEOMETRY RECORD FORWARD. An overlay pass does not touch the
    # presenter, but the output gate reads placement from `<file>.geom.json` and
    # refuses a file that has none -- so patching a delivered video used to make
    # it un-checkable, which is the opposite of the point.
    side = Path(str(src) + ".geom.json")
    if side.exists():
        Path(str(out) + ".geom.json").write_text(side.read_text())
    else:
        print("  ! no geometry sidecar beside the input — the output gate "
              "will not be able to verify placement")
    print("done")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    src, out, plan = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    burn(src, out, json.loads(plan.read_text()))
