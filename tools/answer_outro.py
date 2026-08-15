"""Close a finished video on the handwritten answer card.

    python tools/answer_outro.py in.mp4 answer.png out.mp4 [--hold 5] [--fade 1]

The card fades up over the last frame, holds long enough to be read, then fades
to black and the video ends. That shape is the brief; the numbers are flags so a
longer answer can hold longer without touching this file.

WHY THIS IS A TOOL AND NOT A MANIM BEAT
---------------------------------------
`answer_image:` in script.md already turns the card into an ordinary beat, and
for a script written through `src/script_writer.py` that is the right path — it
gets narration, QC and compositing for free. But a hand-built scene that is
already rendered and composited would have to go round the whole loop again to
gain six seconds of still image. This appends it to the finished file instead,
which costs one ffmpeg pass and cannot disturb anything already approved.

THE PLATE
---------
The card is 2:3 and the frame is 9:16, so something has to fill the sides. It is
sampled from the video's own corners rather than fixed in code: the two tracks
use different backgrounds, and a hard-coded navy that matched one of them would
band visibly against the other.

BATCH SAFETY
------------
Everything that varies between questions is measured, not assumed: the frame
size, the frame rate, the duration and the plate all come from the input. The
output is written to `.partial.mp4`, decoded end to end, and only then moved
into place — an interrupted run leaves the previous approved file untouched
rather than a half-written one that plays for three seconds.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

CARD_W = 0.86           # of frame width — the margins the reference stills keep
CARD_H = 0.82           # of frame height

# Trimming the blank tail off the sheet. An answer that fills eleven of the
# thirty-three writable rows leaves two thirds of the page empty, and placing
# the whole sheet in frame shrinks the handwriting to about half the size it
# could be — on a phone that is the difference between reading it and pausing.
INK_LEVEL  = 130        # darker than this is handwriting, not the ruled line
INK_FLOOR  = 0.025      # smoothed row coverage that counts as written
TRIM_PAD   = 0.045      # blank paper left below the last line, as a fraction


def probe(video: Path) -> dict:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height,r_frame_rate:format=duration",
         "-of", "json", str(video)],
        capture_output=True, text=True, check=True).stdout
    d = json.loads(out)
    s = d["streams"][0]
    num, den = s["r_frame_rate"].split("/")
    return {"w": int(s["width"]), "h": int(s["height"]),
            "fps": float(num) / float(den),
            "dur": float(d["format"]["duration"])}


def plate_colour(video: Path, at: float) -> str:
    """Median of the two top corners — background wherever the content isn't."""
    import io

    import numpy as np
    from PIL import Image

    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-ss", f"{max(0.0, at):.2f}", "-i", str(video),
         "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-"],
        capture_output=True).stdout
    if not raw:
        return "0x000000"
    a = np.asarray(Image.open(io.BytesIO(raw)).convert("RGB"))
    h, w, _ = a.shape
    box = min(200, h // 4, w // 4)
    patch = np.concatenate([a[box // 4:box, box // 4:box].reshape(-1, 3),
                            a[box // 4:box, w - box:w - box // 4].reshape(-1, 3)])
    r, g, b = np.median(patch, axis=0).astype(int)
    return f"0x{r:02X}{g:02X}{b:02X}"


def trim_blank_tail(card: Path, dest: Path) -> Path:
    """Crop the unwritten bottom of the sheet away, or return it untouched.

    A ruled line spans the full width, so a per-row ink count cannot tell one
    from a line of text — both light up. Smoothing the profile over roughly one
    line pitch does separate them: writing raises the average across the band it
    sits in, a hairline rule barely moves it.

    The crop keeps the paper's own top and side edges so the result still reads
    as a photographed sheet running off the bottom of frame, not as a cut-out.
    """
    import numpy as np
    from PIL import Image

    im = Image.open(card)
    a = np.asarray(im.convert("L")).astype(int)
    h, w = a.shape
    profile = (a < INK_LEVEL).sum(axis=1) / w
    window = max(9, h // 50)
    smooth = np.convolve(profile, np.ones(window) / window, mode="same")
    rows = np.where(smooth > INK_FLOOR)[0]
    if not len(rows):
        return card                                  # nothing found — don't guess
    bottom = min(h, int(rows.max() + h * TRIM_PAD))
    if bottom >= h * 0.92:
        return card                                  # already full; no gain
    dest.parent.mkdir(parents=True, exist_ok=True)
    im.crop((0, 0, w, bottom)).save(dest)
    print(f"   trimmed the blank tail: {h}px -> {bottom}px of sheet")
    return dest


def build(video: Path, card: Path, out: Path, hold: float, fade: float,
          plate: str | None = None) -> None:
    v = probe(video)
    w, h, fps, dur = v["w"], v["h"], v["fps"], v["dur"]
    if dur <= fade:
        raise SystemExit(f"❌ {video.name} is shorter than the fade ({dur:.1f}s)")

    plate = plate or plate_colour(video, dur - 2.0)
    card_dur = fade + hold + fade        # fade up, hold, fade to black
    total = dur - fade + card_dur

    # The card sits on the plate at its own aspect; `force_original_aspect_ratio`
    # is what keeps a landscape answer sheet from being stretched to portrait.
    tail = (
        f"color=c={plate}:s={w}x{h}:r={fps}:d={card_dur}[plate];"
        f"[2:v]scale={int(w * CARD_W)}:{int(h * CARD_H)}"
        f":force_original_aspect_ratio=decrease[card];"
        f"[plate][card]overlay=(W-w)/2:(H-h)/2:format=auto[tail0];"
        # black at the very end, not a dissolve back to the plate
        f"[tail0]fade=t=out:st={fade + hold}:d={fade}:color=black,"
        f"format=yuv420p[tail];"
    )
    chain = (
        tail +
        f"[0:v]fps={fps},format=yuv420p[main];"
        f"[main][tail]xfade=transition=fade:duration={fade}"
        f":offset={dur - fade}[v];"
        # the card runs past the narration, so the audio is padded rather than
        # the video being cut back to it
        f"[1:a]apad=whole_dur={total}[a]"
    )

    partial = out.with_suffix(".partial.mp4")
    partial.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error",
         "-i", str(video), "-i", str(video), "-loop", "1", "-i", str(card),
         "-filter_complex", chain, "-map", "[v]", "-map", "[a]",
         "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "192k", "-t", f"{total:.3f}", str(partial)],
        check=True)

    subprocess.run(["ffmpeg", "-v", "error", "-i", str(partial),
                    "-f", "null", "-"], check=True)
    shutil.move(str(partial), str(out))
    print(f"   {dur:.2f}s + {card_dur:.1f}s card -> {total:.2f}s  plate {plate}")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("video"), p.add_argument("card"), p.add_argument("out")
    p.add_argument("--hold", type=float, default=5.0,
                   help="seconds the card is fully visible (default 5)")
    p.add_argument("--fade", type=float, default=1.0,
                   help="seconds for the fade up and the fade to black")
    p.add_argument("--plate", help="background colour, e.g. 0x000B1F "
                                   "(default: sampled from the video)")
    p.add_argument("--no-trim", action="store_true",
                   help="place the whole sheet, blank rows and all")
    a = p.parse_args()

    video, card, out = Path(a.video), Path(a.card), Path(a.out)
    for path in (video, card):
        if not path.exists():
            raise SystemExit(f"❌ not found: {path}")
    print(f"🎬 answer outro -> {out}")
    if not a.no_trim:
        # beside the card, not beside the video: `final/` holds deliverables
        card = trim_blank_tail(card, card.with_name(f"{card.stem}_trimmed.png"))
    build(video, card, out, a.hold, a.fade, a.plate)
    return 0


if __name__ == "__main__":
    sys.exit(main())
