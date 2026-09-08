"""Cut a stretch out of a finished part and cross-dissolve across the join.

    python tools/cut_and_dissolve.py <in.mp4> <out.mp4> <cut_start> <cut_end> [dissolve]

For removing a stumble or a false start after the video is built. The cut takes
picture and sound together, so burnt-in captions go with it.

VIDEO DISSOLVES, AUDIO BUTTS. They are not given the same transition on purpose:
an audio crossfade here would have to blend across the first syllable of the
word the cut lands on -- "रुको" begins the instant the stumble ends, with no
silence after it -- and that reads as the word fading in. The picture dissolves
over the pause before the cut, where nothing is being said, and the sound is
cut clean with a 30ms taper that removes the click and nothing else.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def main() -> int:
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    a_end, b_start = float(sys.argv[3]), float(sys.argv[4])
    d = float(sys.argv[5]) if len(sys.argv) > 5 else 0.30
    total = float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(src)], capture_output=True, text=True).stdout)
    b_dur = total - b_start
    if a_end <= d or b_dur <= d:
        raise SystemExit("dissolve is longer than the material either side of it")

    threads = os.environ.get("FFMPEG_THREADS", "3")
    fc = (
        f"[0:v]trim=0:{a_end:.3f},setpts=PTS-STARTPTS[va];"
        f"[0:v]trim={b_start:.3f},setpts=PTS-STARTPTS[vb];"
        f"[va][vb]xfade=transition=fade:duration={d:.3f}:offset={a_end - d:.3f}[v];"
        # A/V SYNC. xfade puts B's frame at `b_start` on the new timeline at
        # `a_end - d`, so the audio has to switch at exactly the same instant
        # and start from exactly `b_start`. Offsetting the audio cut by d/2 --
        # which looks symmetrical and is what I wrote first -- slides sound
        # 0.15s against picture AND eats the first syllable of the word the cut
        # lands on, which is the one word the cut exists to preserve.
        f"[0:a]atrim=0:{a_end - d:.3f},asetpts=PTS-STARTPTS,"
        f"afade=t=out:st={max(0, a_end - d - 0.03):.3f}:d=0.03[aa];"
        f"[0:a]atrim={b_start:.3f},asetpts=PTS-STARTPTS,"
        f"afade=t=in:st=0:d=0.03[ab];"
        f"[aa][ab]concat=n=2:v=0:a=1[a]"
    )
    tmp = dst.with_suffix(".partial.mp4")
    subprocess.run(
        ["ffmpeg", "-v", "error", "-threads", threads, "-i", str(src),
         "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
         "-c:v", "libx264", "-preset", "medium", "-crf", "19",
         "-pix_fmt", "yuv420p", "-r", "30", "-fps_mode", "cfr",
         "-c:a", "aac", "-b:a", "192k",
         "-movflags", "+faststart", str(tmp), "-y"], check=True)
    out = float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(tmp)], capture_output=True, text=True).stdout)
    tmp.replace(dst)
    print(f"  {src.name}: {total:.2f}s -> {out:.2f}s "
          f"(cut {b_start - a_end:.2f}s, {d:.2f}s dissolve)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
