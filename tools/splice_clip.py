"""Replace a stretch of a finished part with another clip, dissolving both joins.

    python tools/splice_clip.py <in.mp4> <insert.mp4> <out.mp4> <a_end> <b_start> [dissolve]

For a re-recorded correction. `a_end` and `b_start` bracket the material being
removed from `in.mp4`; `insert.mp4` takes its place. Both joins get a picture
cross-dissolve; the audio butts at each, for the same reason cut_and_dissolve.py
gives -- a crossfade lands on the first syllable of the word either side and
makes it sound like the word fades in.

Choose the boundaries from WORD TIMINGS, in the silence between phrases, and
check the insert has some lead-in and tail silence of its own. This one had
0.25s and 0.21s, which is what the dissolves are laid over.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def dur(p) -> float:
    return float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(p)], capture_output=True, text=True).stdout)


def geom(path: Path) -> tuple[int, int, int]:
    """(width, height, fps) of a video, so an insert can be made to match it."""
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
         "stream=width,height,r_frame_rate", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True, check=True).stdout.strip().split(",")
    num, den = (r[2].split("/") + ["1"])[:2]
    return int(r[0]), int(r[1]), max(1, round(float(num) / float(den)))


def main() -> int:
    src, ins, dst = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    a_end, b_start = float(sys.argv[4]), float(sys.argv[5])
    d = float(sys.argv[6]) if len(sys.argv) > 6 else 0.25
    total, ilen = dur(src), dur(ins)
    # MATCH WHATEVER IS BEING SPLICED INTO, rather than assuming the finished
    # portrait frame. This was written for a correction to a delivered video, so
    # it hard-coded 1080x1920 at 30fps; used on SOURCE avatar footage — which is
    # where a re-recorded line belongs, so the rebuild keeps the fix — the
    # insert was squeezed into portrait and ffmpeg died with a bare exit 234.
    w, h, fps = geom(src)
    print(f"  splicing into {w}x{h} @ {fps}fps")
    if min(a_end, ilen, total - b_start) <= d * 2:
        raise SystemExit("dissolve is longer than the material around it")

    # xfade puts B's first frame on the new timeline at (A - d), so each audio
    # switch has to happen at exactly that instant and start from exactly the
    # other side's in-point, or sound slides against picture.
    fc = (
        f"[0:v]trim=0:{a_end:.3f},setpts=PTS-STARTPTS,fps={fps},settb=1/{fps}[va];"
        f"[1:v]trim=0:{ilen:.3f},setpts=PTS-STARTPTS,scale={w}:{h},"
        f"setsar=1,fps={fps},settb=1/{fps}[vi];"
        f"[0:v]trim={b_start:.3f},setpts=PTS-STARTPTS,fps={fps},settb=1/{fps}[vb];"
        f"[va][vi]xfade=transition=fade:duration={d:.3f}:offset={a_end - d:.3f}[v1];"
        f"[v1][vb]xfade=transition=fade:duration={d:.3f}:"
        f"offset={a_end - d + ilen - d:.3f}[v];"
        f"[0:a]atrim=0:{a_end - d:.3f},asetpts=PTS-STARTPTS,"
        f"afade=t=out:st={max(0, a_end - d - 0.03):.3f}:d=0.03[a0];"
        f"[1:a]atrim=0:{ilen - d:.3f},asetpts=PTS-STARTPTS,"
        f"afade=t=in:st=0:d=0.03,"
        f"afade=t=out:st={max(0, ilen - d - 0.03):.3f}:d=0.03[a1];"
        f"[0:a]atrim={b_start:.3f},asetpts=PTS-STARTPTS,"
        f"afade=t=in:st=0:d=0.03[a2];"
        f"[a0][a1][a2]concat=n=3:v=0:a=1[a]"
    )
    threads = os.environ.get("FFMPEG_THREADS", "3")
    tmp = dst.with_suffix(".partial.mp4")
    subprocess.run(
        ["ffmpeg", "-v", "error", "-threads", threads, "-i", str(src), "-i", str(ins),
         "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
         "-c:v", "libx264", "-preset", "medium", "-crf", "19",
         "-pix_fmt", "yuv420p", "-r", str(fps), "-fps_mode", "cfr",
         "-c:a", "aac", "-b:a", "192k",
         "-movflags", "+faststart", str(tmp), "-y"], check=True)
    out = dur(tmp)
    tmp.replace(dst)
    print(f"  {src.name}: {total:.2f}s -> {out:.2f}s "
          f"(removed {b_start - a_end:.2f}s, inserted {ilen:.2f}s, {d:.2f}s dissolves)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
