"""Bring the answer page up on its cue and hold it to the end of the clip.

    python tools/answer_overlay.py projects/che-c1-la-01 2 answer.png [--fade 0.7]

The presenter says "इसका पूरा उत्तर आपकी स्क्रीन पर आ जाएगा", and the answer has
to be there when they say it — not after the video finishes. So the page comes up
ON the cue caption and stays for the rest of the clip, under the save/screenshot
line and the Unnati CTA.

That is a change from `tools/answer_outro.py`, which appends the card after the
last frame. Keep that one for videos whose script never promises the answer
on screen; use this one whenever the narration makes the promise, because a
student told to screenshot an answer that is not up yet screenshots the CTA.

FINDING THE CUE
---------------
Matched on *स्क्रीन पर आ*, not the whole sentence. The clips vary between उत्तर
and answer, Whisper transcribes आ जाएगा / आजाएगा / आ जायेगा differently, and one
clip drops पूरा. The short anchor survives all of it. If it is not found the tool
REFUSES rather than guessing a time — a page that lands on the wrong sentence is
worse than one that is missing, and the caller can fall back to answer_outro.

THE PAGE
--------
The pages are 2:3 and the frame is 9:16, so the page is RELATIVELY WIDER than
the frame. Scaling it to cover would crop the left and right margins — on a
handwritten answer that means slicing the ends off every line. So it is fitted
to the frame WIDTH and padded above and below onto an opaque plate, which also
hides the presenter: the promise is that the answer is on the screen.

MULTI-PAGE ANSWERS
------------------
Some answers run to several pages (KMnO4 has three). The time between the cue
and the end of the clip is split equally between them. If that gives a page less
than MIN_PAGE seconds the tool says so rather than flashing pages the student
cannot read — the fix there is a longer tail, not a faster slideshow.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

MIN_PAGE = 3.0          # a page shown for less than this cannot be read
# The cue is wherever the presenter hands the answer over. Two phrasings so far:
# "इसका पूरा उत्तर आपकी स्क्रीन पर आ जाएगा", and — on the vitamins clips — "इसका
# पूरा आंसर राइट साइड में दिये नोट्स बटन में मिल जाएगा". The second one points at
# the notes button rather than the screen, but it is the same moment in the video:
# he has finished teaching and is handing over the written answer.
CUE = re.compile(r"स्क्रीन\s*पर\s*आ|नोट्स\s*बटन|आंसर\s+राइट\s*साइड")


def _has_writing(path: Path, floor: float = 0.8) -> bool:
    """True if the page carries handwriting, not just printed rules."""
    import numpy as np
    from PIL import Image
    a = np.asarray(Image.open(path).convert("L")).astype(float)
    return float((a < 130).mean() * 100) >= floor


def cue_time(lines: list[dict]) -> float | None:
    for l in lines:
        if CUE.search(str(l.get("text", ""))):
            return float(l["start"])
    return None


def probe(path: Path, stream: str, keys: str) -> list[str]:
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", stream,
                          "-show_entries", keys, "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True, check=True).stdout
    return out.strip().split(",")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("root", type=Path)
    ap.add_argument("part")
    ap.add_argument("answer", type=Path, nargs="+")
    ap.add_argument("--fade", type=float, default=0.7)
    ap.add_argument("--video", type=Path, default=None)
    a = ap.parse_args()

    lines = json.loads((a.root / f"lines_part{a.part}.json").read_text(encoding="utf-8"))
    at = cue_time(lines)
    if at is None:
        print(f"no answer cue in lines_part{a.part}.json — refusing to guess a time")
        return 2
    missing = [str(p) for p in a.answer if not p.is_file()]
    if missing:
        print("answer page not found: " + ", ".join(missing))
        return 2

    # A page set can contain blank ruled sheets — the Berkeley set had two of
    # four. Holding a blank page on screen for seconds of a short tail wastes
    # the time the written pages need, so they are dropped here rather than
    # relied on being spotted by eye.
    written = [q for q in a.answer if _has_writing(q)]
    if not written:
        print("every supplied page is blank")
        return 2
    if len(written) != len(a.answer):
        print(f"  skipping {len(a.answer) - len(written)} blank page(s)")
    a.answer = written

    src = a.video or (a.root / "final" / f"{a.root.name}_part{a.part}.mp4")
    w, h = probe(src, "v:0", "stream=width,height")
    dst = src.with_name(src.stem + ".withanswer.mp4")
    tmp = dst.with_suffix(".partial.mp4")

    end = float(probe(src, "v:0", "format=duration")[0]) if False else \
        float(subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                              "format=duration", "-of", "csv=p=0", str(src)],
                             capture_output=True, text=True,
                             check=True).stdout.strip())
    span = (end - at) / len(a.answer)
    if span < MIN_PAGE:
        print(f"{len(a.answer)} pages over {end - at:.1f}s is {span:.1f}s each — "
              f"under {MIN_PAGE}s a page cannot be read; not building")
        return 2

    ins, chains, last = [], [], "[0:v]"
    for i, page in enumerate(a.answer):
        ins += ["-loop", "1", "-i", str(page)]
        t0 = at + i * span
        t1 = end if i == len(a.answer) - 1 else at + (i + 1) * span
        # fit to WIDTH, pad onto an opaque plate so nothing is cropped away
        chains.append(
            f"[{i + 1}:v]scale={w}:-1:force_original_aspect_ratio=decrease,"
            f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:color=0x0A1526,format=yuva420p,"
            f"fade=t=in:st={t0:.2f}:d={a.fade}:alpha=1[p{i}];"
            f"{last}[p{i}]overlay=0:0:enable='between(t,{t0:.2f},{t1:.2f})'[v{i}]")
        last = f"[v{i}]"
    vf = ";".join(chains)
    subprocess.run(["ffmpeg", "-v", "error", "-i", str(src), *ins,
                    "-filter_complex", vf,
                    "-map", last, "-map", "0:a?", "-c:v", "libx264", "-crf", "18",
                    "-preset", "medium", "-c:a", "copy", "-shortest",
                    str(tmp), "-y"], check=True)
    subprocess.run(["ffprobe", "-v", "error", "-i", str(tmp)], check=True)
    shutil.move(str(tmp), str(dst))
    print(f"answer up at {at:.2f}s, {len(a.answer)} page(s) x {span:.1f}s "
          f"-> {dst}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
