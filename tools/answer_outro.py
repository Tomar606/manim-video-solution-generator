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
    # THE FLOOR IS RELATIVE TO THIS SHEET'S OWN BLANK PAPER, not a constant.
    # A fixed 0.025 is the coverage of a line of HANDWRITING across the sheet.
    # A diagram is not writing: its lower reaches — the vagina tube and its one
    # label on BIO-C2-SA-02 — are a narrow column of thin pencil covering 0.9%
    # of the row, so the constant floor declared the answer finished 6% of the
    # page early. The band of "blank" paper taken from below that point still
    # had the drawing in it, and tiling it to extend the sheet printed the
    # vagina and योनि THREE TIMES down the finished frame.
    #
    # Blank paper on these sheets is not zero either — the red margin rule runs
    # down every row — so the baseline is measured rather than assumed: the
    # tenth percentile is paper plus margin, and anything appreciably above it
    # is content. Capped at the old constant so this can only ever find MORE
    # of the answer than before, never less.
    baseline = float(np.percentile(smooth, 10))
    floor = min(INK_FLOOR, baseline + 0.004)
    rows = np.nonzero(smooth > floor)[0]
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

    # Ground the page in the sheet's own paper colour, NOT the default black.
    # Every failure below — no ruling found, no blank band to copy, a band that
    # runs past the sheet — then degrades to plain paper, which reads as the
    # bottom of a page. It used to degrade to black, and a 300px black bar under
    # the answer is the one outcome that cannot be mistaken for a sheet of paper.
    blank = arr[int(arr.shape[0] * 0.90):]
    paper = tuple(int(v) for v in np.median(blank.reshape(-1, 3), axis=0))
    page = Image.new("RGB", (frame_w, frame_h), paper)
    page.paste(im, (0, 0))

    written = written_bottom(np.asarray(im.convert("L")).astype(int))
    diffs = [b - a for a, b in zip(rows, rows[1:])] if len(rows) > 2 else []
    pitch = int(np.median(diffs)) if diffs else 0

    # A band starting ON a line, a whole number of pitches tall, taken from
    # paper that is genuinely BLANK — the first rule clear of the last written
    # row. Picking by a fraction of the page instead repeated the closing lines
    # of the answer three times down the extension.
    band = None
    if pitch >= 8 and rows:
        floor = (written + pitch) if written is not None else int(im.height * 0.55)
        band_top = next((r for r in rows if r > floor), None)
        if band_top is not None:
            # CLAMPED to the sheet. Cropping past the bottom edge returns BLACK
            # padding, and pasting that under the answer put a 300px black bar
            # at the end of the video — the one thing this function exists to
            # prevent. An answer whose figure runs to the foot of the sheet
            # leaves no blank band at all, which is exactly when it happened.
            usable = (arr.shape[0] - band_top) // pitch
            n = min(max(1, (frame_h - im.height) // pitch + 1), usable)
            if n >= 1:
                band = im.crop((0, band_top, frame_w, band_top + n * pitch))

    start_y = rows[-1] + pitch if rows else im.height

    # NO HORIZONTAL RULING AT ALL. Some house sheets have none — just a red
    # margin rule down the left and a drawn table — so rule_rows finds nothing
    # and the fallback above fills the extension with FLAT paper colour. That
    # is paper, so it passes the check below, but it drops the MARGIN rule:
    # the red lines stop dead partway down the finished frame, and the join is
    # the first thing the eye goes to.
    #
    # Same principle as the ruled path — copy the sheet's own paper rather than
    # draw a substitute — but tile a blank STRIP instead of a ruled band. A
    # strip carries the margin rule and the grain, so the page just continues.
    #
    # It also cuts the sheet at its last clean row. A photographed sheet ends
    # on its physical corner, and that dark wedge sat in the middle of the
    # frame with paper below it.
    if band is None:
        g = np.asarray(im.convert("L")).astype(int)
        paper_lum = float(np.median(g))
        mid = slice(int(frame_w * 0.25), int(frame_w * 0.95))
        # The far left is checked TOO, and separately. A sheet's bottom corner
        # is rounded, so its last few rows are clean across the middle and dark
        # only at x=0 — they passed a middle-only test, went into the tiled
        # strip, and printed a little dark notch down the left edge once per
        # tile. The margin rule itself sits further in, so this narrow band is
        # blank paper on a good row.
        edge = slice(0, max(4, int(frame_w * 0.037)))
        clear = np.array([g[y, mid].min() > paper_lum - 40
                          and g[y, edge].min() > paper_lum - 40
                          for y in range(g.shape[0])])
        # The LAST long run of blank paper, found by scanning the sheet itself.
        #
        # `written_bottom` cannot be used to locate it: a photographed sheet
        # ends on a dark physical EDGE, which reads as writing, so it returned
        # 1504 of 1505 and every search below it came back empty. Runs of clear
        # paper are immune to that — the edge simply is not one.
        runs, start = [], None
        for y, v in enumerate(clear):
            if v and start is None:
                start = y
            elif not v and start is not None:
                if y - start >= 12:
                    runs.append((start, y - 1))
                start = None
        if start is not None and len(clear) - start >= 12:
            runs.append((start, len(clear) - 1))
        if runs:
            top, bot = runs[-1]
            page.paste(im.crop((0, 0, frame_w, bot)), (0, 0))   # drop the edge
            band = im.crop((0, top, frame_w, min(bot, top + 200)))
            start_y = bot

    if band is not None and band.height > 0:
        y = start_y
        while y < frame_h:
            page.paste(band, (0, y))
            y += band.height
    page.save(dest)

    # The EXTENSION must be paper to the last row. Only below the sheet: a row
    # of handwriting is legitimately darker than blank paper, so checking the
    # whole page flagged the question line every time and the warning stopped
    # meaning anything. Below the sheet there is nothing but paper to find.
    lum = np.asarray(Image.open(dest).convert("L")).astype(int).mean(axis=1)
    limit = float(np.median(np.asarray(im.convert("L")).astype(int))) - 55
    bad = np.nonzero(lum[im.height:] < limit)[0]
    if len(bad):
        print(f"   \u26a0 the page is not paper below y={im.height + int(bad.min())} "
              f"({len(bad)} row(s)) \u2014 the ruling extension failed")
    return dest


def build(video: Path, card: Path, out: Path, hold: float, fade: float,
          plate: str | None = None, card2: Path | None = None,
          hold2: float | None = None, in_fade: float | None = None) -> None:
    """One card, or two shown in turn.

    A long answer runs to two sheets, and a student cannot read the second if it
    never appears. With `card2` the first page holds, cross-fades to the second,
    and only the second fades to black — one ending, not two.
    """
    v = probe(video)
    w, h, fps, dur = v["w"], v["h"], v["fps"], v["dur"]
    if dur <= fade:
        raise SystemExit(f"❌ {video.name} is shorter than the fade ({dur:.1f}s)")

    plate = plate or plate_colour(video, dur - 2.0)
    hold2 = hold if hold2 is None else hold2
    ifade = fade if in_fade is None else in_fade

    def page(idx: int, seconds: float, tag: str) -> str:
        # The page already fills the frame exactly (to_full_page), so the plate
        # is only there as a ground for an odd-sized image.
        return (f"color=c={plate}:s={w}x{h}:r={fps}:d={seconds}[pl{tag}];"
                f"[{idx}:v]scale={w}:{h}:force_original_aspect_ratio=increase,"
                f"crop={w}:{h}[cd{tag}];"
                f"[pl{tag}][cd{tag}]overlay=(W-w)/2:(H-h)/2:format=auto[{tag}];")

    if card2 is None:
        card_dur = fade + hold + fade    # fade up, hold, fade to black
        tail = (page(2, card_dur, "t0") +
                # black at the very end, not a dissolve back to the plate
                f"[t0]fade=t=out:st={fade + hold}:d={fade}:color=black,"
                f"format=yuv420p[tail];")
    else:
        # ALL BUT A CUT BETWEEN PAGES. These are two dense sheets of
        # handwriting: cross-faded over a second, both sets of text are legible
        # at once and the result is mud. A page turn is a cut.
        #
        # Done with a very short xfade rather than `concat`, which returned
        # exit 234 here — concat demands identical stream properties from both
        # sides and the two `color` sources differ in duration. xfade is the
        # path already proven in this graph, and at 0.08s reads as a cut.
        cut = 0.08
        a_dur = ifade + hold + cut
        b_dur = cut + hold2 + fade
        card_dur = ifade + hold + cut + hold2 + fade
        tail = (page(2, a_dur, "ta") + page(3, b_dur, "tb") +
                f"[ta][tb]xfade=transition=fade:duration={cut}"
                f":offset={ifade + hold}[t0];"
                # only page two fades to black, so the ending happens once
                f"[t0]fade=t=out:st={ifade + hold + cut + hold2}:d={fade}:color=black,"
                f"format=yuv420p[tail];")
    total = dur - ifade + card_dur
    chain = (
        tail +
        f"[0:v]fps={fps},format=yuv420p[main];"
        f"[main][tail]xfade=transition=fade:duration={ifade}"
        f":offset={dur - ifade}[v];"
        # the card runs past the narration, so the audio is padded rather than
        # the video being cut back to it
        f"[1:a]apad=whole_dur={total}[a]"
    )

    partial = out.with_suffix(".partial.mp4")
    partial.parent.mkdir(parents=True, exist_ok=True)
    ins = ["-i", str(video), "-i", str(video), "-loop", "1", "-i", str(card)]
    if card2 is not None:
        ins += ["-loop", "1", "-i", str(card2)]
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", *ins,
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
    p.add_argument("--then", help="a SECOND page, shown after the first")
    p.add_argument("--then-hold", type=float,
                   help="seconds the second page holds (default: same as --hold)")
    p.add_argument("--in-fade", type=float,
                   help="seconds for the page to ARRIVE (default: same as --fade). "
                        "A one-second dissolve has no single moment of arrival, so a "
                        "sound effect can never line up with it; 0.4 gives the page a "
                        "definite instant to land on.")
    a = p.parse_args()

    video, card, out = Path(a.video), Path(a.card), Path(a.out)
    card2 = Path(a.then) if a.then else None
    for path in [video, card] + ([card2] if card2 else []):
        if not path.exists():
            raise SystemExit(f"❌ not found: {path}")
    print(f"🎬 answer outro -> {out}")
    # NOT trimmed first: fitting to the frame's width scales the sheet the same
    # either way, so trimming buys no size — it only removes the blank paper the
    # extension needs to carry the ruling down the page.
    v = probe(video)
    card = to_full_page(card, v["w"], v["h"], card.with_name(f"{card.stem}_page.png"))
    if card2 is not None:
        card2 = to_full_page(card2, v["w"], v["h"],
                             card2.with_name(f"{card2.stem}_page.png"))
    build(video, card, out, a.hold, a.fade, a.plate, card2, a.then_hold,
          in_fade=a.in_fade)
    return 0


if __name__ == "__main__":
    sys.exit(main())
