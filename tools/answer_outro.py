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


def written_bottom(grey) -> int | None:
    """Last row of the sheet that carries handwriting.

    A ruled line spans the full width, so a per-row ink count cannot tell one
    from a line of text — both light up. Smoothing the profile over roughly one
    line pitch does separate them: writing raises the average across the band it
    sits in, a hairline rule barely moves it.
    """
    import numpy as np
    h, w = grey.shape
    profile = (grey < INK_LEVEL).sum(axis=1) / w
    window = max(9, h // 50)
    smooth = np.convolve(profile, np.ones(window) / window, mode="same")
    rows = np.nonzero(smooth > INK_FLOOR)[0]
    return int(rows.max()) if len(rows) else None


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


def rule_rows(arr, x: int) -> list[int]:
    """Rows where a ruled line crosses, probed down a single column."""
    import numpy as np
    col = arr[:, x].astype(int).mean(axis=1)
    paper = float(np.median(col))
    dark = [i for i, v in enumerate(col) if v < paper - 14]
    if not dark:
        return []
    runs, start, prev = [], dark[0], dark[0]
    for i in dark[1:]:
        if i - prev > 3:
            runs.append((start + prev) // 2)
            start = i
        prev = i
    runs.append((start + prev) // 2)
    return runs


def to_full_page(card: Path, frame_w: int, frame_h: int, dest: Path) -> Path:
    """Make the sheet fill the whole 9:16 frame, at the largest readable size.

    The sheet is 2:3 and the frame is 9:16, so one of the two has to give. The
    options are not equal:

      crop the sides   scaling to the frame's HEIGHT makes the sheet 1280 wide
                       and 200px would have to come off it — straight through
                       the text, which starts 60px in
      bars             centring the sheet leaves the plate showing top and
                       bottom, which is not a full page
      extend the paper fit the WIDTH, then continue the ruling below

    So: fit the width, then keep drawing the sheet's own ruled paper until the
    frame is full. The lines are found by probing a column, and the extension is
    pasted a whole pitch after the last one, so the ruling carries on at its own
    spacing instead of jumping. The paper is copied from the sheet's blank tail
    rather than drawn, so it keeps the photographed grain and stays the same
    page rather than becoming a graphic stuck underneath one.
    """
    import numpy as np
    from PIL import Image

    im = Image.open(card).convert("RGB")
    scale = frame_w / im.width
    im = im.resize((frame_w, max(1, round(im.height * scale))), Image.LANCZOS)
    if im.height >= frame_h:
        im = im.crop((0, 0, frame_w, frame_h))      # keep the top: writing is there
        im.save(dest)
        return dest

    arr = np.asarray(im)
    probe = max(2, int(frame_w * 0.5))              # mid-page: blank below the text
    rows = rule_rows(arr, probe)
    page = Image.new("RGB", (frame_w, frame_h))
    page.paste(im, (0, 0))

    written = written_bottom(np.asarray(im.convert("L")).astype(int))
    diffs = [b - a for a, b in zip(rows, rows[1:])] if len(rows) > 2 else []
    pitch = int(np.median(diffs)) if diffs else 0
    if pitch < 8 or not rows:
        # no ruling to continue — fill with the paper's own colour, which still
        # gives a full page rather than a letterboxed card
        paper = tuple(np.median(arr[-20:].reshape(-1, 3), axis=0).astype(int))
        page.paste(Image.new("RGB", (frame_w, frame_h - im.height), paper),
                   (0, im.height))
        page.save(dest)
        return dest

    # A band starting ON a line, a whole number of pitches tall, taken from
    # paper that is genuinely BLANK — the first rule clear of the last written
    # row. Picking by a fraction of the page instead repeated the closing lines
    # of the answer three times down the extension.
    floor = (written + pitch) if written is not None else int(im.height * 0.55)
    band_top = next((r for r in rows if r > floor), None)
    if band_top is None:
        paper = tuple(np.median(arr[-20:].reshape(-1, 3), axis=0).astype(int))
        page.paste(Image.new("RGB", (frame_w, frame_h - im.height), paper),
                   (0, im.height))
        page.save(dest)
        return dest
    n = max(1, (frame_h - im.height) // pitch + 1)
    band_bottom = min(arr.shape[0], band_top + n * pitch)
    n = max(1, (band_bottom - band_top) // pitch)
    band = im.crop((0, band_top, frame_w, band_top + n * pitch))

    y = rows[-1] + pitch
    while y < frame_h:
        page.paste(band, (0, y))
        y += band.height
    page.save(dest)
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

    # The page already fills the frame exactly (to_full_page), so the plate is
    # only there as a ground in case a caller passes an odd-sized image.
    tail = (
        f"color=c={plate}:s={w}x{h}:r={fps}:d={card_dur}[plate];"
        f"[2:v]scale={w}:{h}:force_original_aspect_ratio=increase,"
        f"crop={w}:{h}[card];"
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
    # NOT trimmed first: fitting to the frame's width scales the sheet the same
    # either way, so trimming buys no size — it only removes the blank paper the
    # extension needs to carry the ruling down the page.
    v = probe(video)
    card = to_full_page(card, v["w"], v["h"], card.with_name(f"{card.stem}_page.png"))
    build(video, card, out, a.hold, a.fade, a.plate)
    return 0


if __name__ == "__main__":
    sys.exit(main())
