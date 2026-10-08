"""Refuse to ship a video where the presenter covers content that teaches.

    python tools/avatar_cover_gate.py <background.mp4> <final.mp4> [--max 0.02]

WHY THIS AND NOT avatar_windows.py
----------------------------------
`avatar_windows.py` predicts where content WOULD be behind the presenter, from
the background alone, against his full-size rectangle. It is the input to the
resize, so it necessarily reports windows even when the resize then fixes them.
It cannot tell you whether the finished video is actually clean.

This compares the two videos. Content the presenter covers is ink that exists in
the BACKGROUND and is gone from the FINAL — that is exactly what "he covered it"
means, and it is measurable no matter what size he was resized to. Content he
does not cover appears in both.

It caught a real one: item 2 of a two-item list printed across his forehead and
a raised hand covered the word "नहीं", on a build whose other four gates all
passed.

WHAT COUNTS AS CONTENT
----------------------
Bright ink only. The plates carry decorative line art — flasks, molecules, DNA —
which the presenter covers constantly and which nobody needs to read. The
threshold is taken from the background's own quiet frames rather than guessed,
so a darker plate does not silently raise the bar.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image

FPS = 2                    # samples per second
MARGIN = 26                # a covered run shorter than this many samples is a gesture


def frames(path: str, fps: int = FPS):
    out = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(path), "-vf", f"fps={fps},scale=270:480",
         "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
        capture_output=True)
    a = np.frombuffer(out.stdout, dtype=np.uint8)
    n = a.size // (270 * 480 * 3)
    return a[:n * 270 * 480 * 3].reshape(n, 480, 270, 3).astype(int)


def main() -> int:
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    bg_p, fin_p = sys.argv[1], sys.argv[2]
    tol = 0.02
    if "--max" in sys.argv:
        tol = float(sys.argv[sys.argv.index("--max") + 1])
    bg, fin = frames(bg_p), frames(fin_p)
    n = min(len(bg), len(fin))
    if n == 0:
        print("  AVATAR COVER GATE FAILED — could not read frames")
        return 1
    bg, fin = bg[:n], fin[:n]

    # the content threshold, taken from the background itself: decorative plate
    # art sits well below the ink the scene draws
    lum_bg = bg.sum(axis=3)
    thr = np.percentile(lum_bg, 99.3)
    content = lum_bg > thr
    gone = content & ~(fin.sum(axis=3) > thr * 0.86)

    per = gone.reshape(n, -1).sum(axis=1) / np.maximum(
        content.reshape(n, -1).sum(axis=1), 1)
    bad = per > tol
    runs, start = [], None
    for i, b in enumerate(bad):
        if b and start is None:
            start = i
        elif not b and start is not None:
            runs.append((start, i - 1)); start = None
    if start is not None:
        runs.append((start, n - 1))
    runs = [r for r in runs if r[1] - r[0] + 1 >= MARGIN]

    if not runs:
        worst = per.max() if n else 0
        # SAY WHAT WAS ACTUALLY FOUND. This used to print "avatar covers
        # nothing" next to the worst frame's number whatever that number was —
        # so a video with an answer page over the last ten seconds passed while
        # reporting that 100% of the content was hidden. Both halves were true
        # (nothing was hidden for long enough to fail) and together they read as
        # a clean pass, which it was not. A high worst frame with no sustained
        # run now says so, and names the usual cause.
        if worst > tol:
            print(f"  avatar covers nothing for long enough to fail, but the "
                  f"worst single frame hides {worst:.1%} of content "
                  f"(limit {tol:.0%} sustained). If this video ends on an answer "
                  f"page that is expected — the page is opaque by design; gate "
                  f"the pre-answer cut to check the presenter.")
        else:
            print(f"  avatar covers nothing: worst frame hides {worst:.1%} of "
                  f"content (limit {tol:.0%})")
        return 0
    print(f"  AVATAR COVER GATE FAILED — {Path(fin_p).name}")
    for a, b in runs:
        print(f"    {a/FPS:6.1f}s - {b/FPS:6.1f}s   up to "
              f"{per[a:b+1].max():.0%} of the content is behind him")
    print("    fix the scene's layout, or pass windows.json so he shrinks there")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
