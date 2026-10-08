"""Cut a span out of a generated clip and heal the join with a short crossfade.

    python tools/clip_cut.py <clip.mp4> --from 5.86 --to 6.48 [--fade 0.12]

For the defect that does not need a new generation: a stammer, a doubled word,
a breath in the wrong place. A reshoot costs credits and rolls the dice on
everything else in the take — the face, the framing, the rest of the line — so
when the only fault is a span of audio, take the span out.

WHERE TO CUT. Land both ends in SILENCE, not on a word boundary. Whisper's word
times are approximate and a cut on a consonant leaves a click; the gap either
side of the repeat is the honest place to join, and `silencedetect` finds it:

    ffmpeg -ss <t> -t <n> -i clip.mp4 -vn -af silencedetect=noise=-38dB:d=0.04 \\
        -f null -

WHY A CROSSFADE AND NOT A BUTT JOIN. The picture is a talking head; his hands
and head are somewhere different either side of the cut, so a hard splice reads
as a jump. A tenth of a second of dissolve hides that without smearing anything
a viewer can catch. The audio crossfades over the same span, which is why the
cut has to land in silence — crossfading two silences is inaudible, crossfading
two syllables is not.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def dur(p: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                          "format=duration", "-of", "csv=p=0", str(p)],
                         capture_output=True, text=True).stdout.strip()
    return float(out) if out else 0.0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("clip")
    ap.add_argument("--from", dest="t0", type=float, required=True)
    ap.add_argument("--to", dest="t1", type=float, required=True)
    ap.add_argument("--fade", type=float, default=0.12)
    ap.add_argument("--out", default="", help="default: replace, keeping a .orig")
    a = ap.parse_args()

    clip = Path(a.clip)
    if not clip.is_file():
        print(f"  {clip} not found"); return 1
    total = dur(clip)
    if not 0 < a.t0 < a.t1 < total:
        print(f"  the span must sit inside the clip (0 .. {total:.2f}s)"); return 1
    head, tail = a.t0, total - a.t1
    if head <= a.fade or tail <= a.fade:
        print(f"  a {a.fade:.2f}s crossfade needs that much clip either side "
              f"(head {head:.2f}s, tail {tail:.2f}s)")
        return 1

    out = Path(a.out) if a.out else clip
    work = clip.with_suffix(".cut.mp4")
    off = head - a.fade
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y",
         "-t", f"{head:.3f}", "-i", str(clip),
         "-ss", f"{a.t1:.3f}", "-i", str(clip),
         "-filter_complex",
         f"[0:v][1:v]xfade=transition=fade:duration={a.fade:.3f}:offset={off:.3f}[v];"
         f"[0:a][1:a]acrossfade=d={a.fade:.3f}[a]",
         "-map", "[v]", "-map", "[a]",
         "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "192k", "-ar", "48000", str(work)], check=True)

    if out == clip:
        keep = clip.with_suffix(".orig.mp4")
        if not keep.exists():
            shutil.copy2(clip, keep)
            print(f"  kept the original at {keep.name}")
    work.replace(out)
    print(f"  {out.name}  {total:.2f}s -> {dur(out):.2f}s "
          f"(took out {a.t1 - a.t0:.2f}s at {a.t0:.2f}s, {a.fade:.2f}s crossfade)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
