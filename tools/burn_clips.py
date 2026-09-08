"""Lay ANIMATED overlays onto a finished video, one ffmpeg pass.

    python tools/burn_clips.py <in.mp4> <out.mp4> <plan.json>

`plan.json` is a list of {mov, start, end, scale, top} where `mov` is a
transparent 1080x1920 clip. Same idea as burn_chips.py, three differences:

  * the overlay MOVES, so it is a video input rather than a looped still;
  * a clip is almost always shorter than the window it has to fill, so it plays
    once and then HOLDS its last frame. Not looped and not reversed. All eight
    were measured before this was written: every one BUILDS -- first frame
    against last differs by 6 to 15 grey levels, and there is no motion at all
    in the final second. Looping such a clip replays the build, so the labels
    pop in again every few seconds; reversing it would show DNA un-coiling and
    hydrogen bonds coming apart, wrong in a way that looks completely fine. The
    finished build IS the deliverable state, which is why these clips were
    authored never to fade out;
  * it is SCALED. The clips are full-frame renders whose content runs to y=1311,
    which is above the 30% floor they were built to but still inside the
    presenter's head once he is composited in. Scaling about the top of the
    frame is what buys the clearance, so `scale` comes from measurement, not
    from taste.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

FADE = 0.4
FPS = 30


def check_overlaps(plan: list[dict]) -> None:
    """Two different animations must never be on screen together."""
    bad = []
    for a, b in zip(plan, plan[1:]):
        if b["start"] < a["end"] - 1e-6:
            bad.append(f'  {Path(a["mov"]).stem} ends {a["end"]:.2f} but '
                       f'{Path(b["mov"]).stem} starts {b["start"]:.2f}')
    if bad:
        raise SystemExit("two animations would be on screen at once:\n" + "\n".join(bad))


def burn(src: Path, out: Path, plan: list[dict]) -> None:
    check_overlaps(plan)
    inputs: list[str] = []
    parts: list[str] = []
    for i, c in enumerate(plan, start=1):
        dur = round(c["end"] - c["start"], 3)
        if dur <= 2 * FADE:
            raise SystemExit(f"{c['mov']}: window {dur}s is shorter than its fades")
        s = float(c.get("scale", 1.0))
        clip_len = float(subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "csv=p=0", str(c["mov"])], capture_output=True,
            text=True).stdout)
        if clip_len > dur + 0.05:
            raise SystemExit(f"{c['mov']}: {clip_len:.1f}s clip does not fit a "
                             f"{dur:.1f}s window -- the build would be cut off")
        inputs += ["-i", str(c["mov"])]
        w = int(round(1080 * s / 2)) * 2
        # tpad clones the LAST frame for the rest of the window, then trim cuts
        # it to length; the out-fade is applied after the hold so it lands at
        # the end of the window rather than the end of the clip.
        parts.append(
            f"[{i}:v]format=rgba,scale={w}:-2,"
            f"tpad=stop_mode=clone:stop_duration={dur:.3f},"
            f"trim=0:{dur:.3f},setpts=PTS-STARTPTS,"
            f"fade=t=in:st=0:d={FADE}:alpha=1,"
            f"fade=t=out:st={dur - FADE:.3f}:d={FADE}:alpha=1,"
            f"tpad=start_duration={c['start']:.3f}:start_mode=add:color=black@0,"
            f"fps={FPS}[c{i}]")

    chain, last = [], "0:v"
    for i, c in enumerate(plan, start=1):
        lbl = f"v{i}"
        s = float(c.get("scale", 1.0))
        x = int(round((1080 - 1080 * s) / 2))          # centred horizontally
        y = int(c.get("top", 0))
        chain.append(f"[{last}][c{i}]overlay={x}:{y}:eof_action=pass:"
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
    print(f"burning {len(plan)} animation(s) -> {out}")
    subprocess.run(cmd, check=True)

    errs = subprocess.run(["ffmpeg", "-v", "error", "-i", str(tmp), "-f", "null", "-"],
                          capture_output=True, text=True).stderr.strip()
    if errs:
        raise SystemExit(f"{tmp} decodes with errors, not moving into place:\n"
                         f"{errs.splitlines()[0]}")
    tmp.replace(out)


def main() -> int:
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    src, out, planf = sys.argv[1:4]
    burn(Path(src), Path(out), json.loads(Path(planf).read_text()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
