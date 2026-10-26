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

MULTI-PAGE ANSWERS, AND WHY THE CLIP GETS LONGER
------------------------------------------------
Some answers run to several pages (KMnO4 has three). The time between the cue
and the end of the clip is split equally between them — and on CHE-C1-SA-01
that was 7.9 seconds for two pages, so each page of handwriting was up for 4.0
seconds. The page was there, the gate passed, and nobody could read it. A page
nobody can read is the same as no page.

So the clip is EXTENDED instead: the last frame is held (and the audio padded
with silence) until every page gets MIN_DWELL seconds. The alternative was to
flash the pages faster, which is the failure dressed up as a pass.

MIN_PAGE is still the floor at which the tool refuses outright. MIN_DWELL is
what it aims for, and `--min-dwell` moves it per video — a one-paragraph answer
does not need as long as a full derivation.
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
# WHAT A PAGE ACTUALLY NEEDS. Measured by reading one on a phone: a full
# sheet of handwritten Hindi takes about eight seconds to get through. The
# clip is stretched to give every page this much rather than the pages being
# sped up to fit the clip.
MIN_DWELL = 8.0         # seconds each page is aimed to hold
# The cue is wherever the presenter hands the answer over. Two phrasings so far:
# "इसका पूरा उत्तर आपकी स्क्रीन पर आ जाएगा", and — on the vitamins clips — "इसका
# पूरा आंसर राइट साइड में दिये नोट्स बटन में मिल जाएगा". The second one points at
# the notes button rather than the screen, but it is the same moment in the video:
# he has finished teaching and is handing over the written answer.
# THE CUE MAY BE WRITTEN IN LATIN. The caption rule is that a word a student is
# used to SEEING in English stays in English, so a clip that says "Notes button"
# has it in the captions as "Notes button" — and a matcher that only knew
# नोट्स बटन found nothing and dropped the answer page silently, which is the
# exact failure tools/lines_from_srt.py warns about. Both spellings now match,
# and so does "screen par aa" in either script.
CUE = re.compile(
    # ...and in Devanagari the word after नोट्स varies the same way the Latin
    # one does: बटन, में, पर. Requiring बटन found nothing on CHE-C4-LA-01's
    # "वो नोट्स में पूरा आंसर देख लेना", which is the same handover. One of the
    # three is still REQUIRED — a bare नोट्स can turn up in an ordinary sentence.
    r"स्क्रीन\s*पर\s*आ|नोट्स\s*(?:बटन|में|पर)|आंसर\s+राइट\s*साइड"
    # ...and the word after "Notes" varies: button, में, पर. Requiring "button"
    # found nothing on the clips that say "अब इसका answer आपको Notes में मिल
    # जाएगा", which is the same handover.
    r"|notes\s*(?:button|में|me|par|पर)?|screen\s*(?:में|me|par|पर)",
    re.IGNORECASE)


def _ink(path: Path, area: str = "page") -> float:
    """How much of the sheet is handwriting, as a percentage of its pixels.

    `area="written"` measures down to the last line of writing only, so a short
    page is not judged against the blank rules beneath it.
    """
    import numpy as np
    from PIL import Image
    a = np.asarray(Image.open(path).convert("L")).astype(float)
    if area == "written":
        a = a[:_written_bottom(a)]
    return float((a < 130).mean() * 100)


def _trim_blank_tail(src: Path, dest: Path) -> Path:
    """NO LONGER USED — kept only so the reason it was removed stays attached.

    Cropping the unwritten bottom made short pages fill the frame, but the
    Arivihan watermark sits low on the sheet and is light grey, so the <130 ink
    test never counted it and the crop went straight through it on SEVENTEEN
    answer pages. The page now goes in whole, with the bands above and below
    filled in its own paper colour. Do not reintroduce this without checking
    the watermark survives.

    Crop the unwritten bottom of the sheet away, or return it untouched.

    CHE-C1-SA-01's second page carries three lines and then two thirds of empty
    ruled paper. Fitted whole to the frame width, those three lines came out
    tiny at the top and the video ENDED on what reads as a blank sheet — the
    answer was there and looked like it was missing.

    tools/answer_outro.py has done this since it was written; this one never
    did, which is why the overlay route shipped the untrimmed page. Same method:
    a ruled line spans the full width so a per-row ink count cannot tell it from
    a line of text, but smoothing over about one line pitch does — writing lifts
    the average across its band, a hairline rule barely moves it.
    """
    import numpy as np
    from PIL import Image
    im = Image.open(src)
    a = np.asarray(im.convert("L")).astype(int)
    h, w = a.shape
    profile = (a < 130).sum(axis=1) / w
    window = max(9, h // 50)
    smooth = np.convolve(profile, np.ones(window) / window, mode="same")
    rows = np.where(smooth > 0.025)[0]
    if not len(rows):
        return src                                   # nothing found — don't guess
    bottom = min(h, int(rows.max() + h * 0.045))

    # NEVER CUT THE WATERMARK. It is light grey — around 200 against white —
    # so the <130 ink test does not see it at all, and on a page whose writing
    # stops high the crop went straight through the Arivihan mark. Seventeen
    # answer pages lost it that way before anyone noticed, including
    # CHE-C1-SA-01 and CHE-C2-SA-03. The mark is part of the page's identity,
    # so the crop stops below it or does not happen.
    grey = ((a > 150) & (a < 243)).sum(axis=1) / w
    mark = np.where(grey > 0.02)[0]
    if len(mark):
        bottom = max(bottom, min(h, int(mark.max() + h * 0.02)))

    if bottom >= h * 0.92:
        return src                                   # already full; no gain
    dest.parent.mkdir(parents=True, exist_ok=True)
    im.crop((0, 0, w, bottom)).save(dest)
    print(f"  {src.name}: trimmed blank tail {h}px -> {bottom}px")
    return dest


def _written_bottom(a) -> int:
    """Row below the last line of writing — the measuring window, not a crop."""
    import numpy as np
    h, w = a.shape
    prof = (a < 130).sum(axis=1) / w
    win = max(9, h // 50)
    sm = np.convolve(prof, np.ones(win) / win, mode="same")
    rows = np.where(sm > 0.025)[0]
    return min(h, int(rows.max() + h * 0.045)) if len(rows) else h


def _has_writing(path: Path, floor: float = 0.8, area: str = "page") -> bool:
    """True if the page carries handwriting, not just printed rules.

    `area="written"` measures only down to the last line of writing. Over the
    whole sheet a short page looks blank — CHE-C2-SA-04's second page holds the
    entire unit derivation and scores 0.60% of the full page, which is under
    the floor and got it dropped from the video.
    """
    import numpy as np
    from PIL import Image
    a = np.asarray(Image.open(path).convert("L")).astype(float)
    if area == "written":
        a = a[:_written_bottom(a)]
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


def _paper(path: Path) -> str:
    """The page's own paper colour, as 0xRRGGBB, for the bands above and below.

    The page is 2:3 and the frame is 9:16, so fitting to WIDTH always leaves a
    strip at the top and bottom. Filling those with the house navy left two dark
    bands across an otherwise white screen and the answer read as a photo of a
    page rather than as the page. Sampling the paper makes the whole frame one
    sheet.

    Sampled from the MARGINS, not the whole image: the median of the outer rows
    and columns, which is paper on every page in the set. The median of the
    whole image would be dragged by the ruled lines and the handwriting.
    """
    try:
        import numpy as np
        from PIL import Image
        a = np.asarray(Image.open(path).convert("RGB"))
        h, w = a.shape[:2]
        m = max(2, min(h, w) // 40)
        edge = np.concatenate([a[:m].reshape(-1, 3), a[-m:].reshape(-1, 3),
                               a[:, :m].reshape(-1, 3), a[:, -m:].reshape(-1, 3)])
        r, g, b = (int(v) for v in np.median(edge, axis=0))
        return f"0x{r:02X}{g:02X}{b:02X}"
    except Exception:                                    # noqa: BLE001
        return "0xF4F1EA"            # a warm paper white, not the navy plate


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("root", type=Path)
    ap.add_argument("part")
    ap.add_argument("answer", type=Path, nargs="+")
    ap.add_argument("--fade", type=float, default=0.7)
    ap.add_argument("--min-dwell", type=float, default=MIN_DWELL,
                    help="seconds each page should hold; the clip is "
                         "extended on its last frame to make room")
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
    # THE PAGE IS NEVER CROPPED. An earlier version cut the unwritten bottom
    # away so a short page would fill the frame, and that sliced the Arivihan
    # watermark off seventeen answer pages — the mark sits low and is light
    # grey, so the ink test never saw it. The page now goes in whole and the
    # bands above and below are filled with its OWN paper colour (see _paper),
    # which is what makes the frame read as one sheet rather than a cut-out.
    #
    # The blank-page test still measures the WRITTEN AREA only, because ink as
    # a share of the whole sheet makes a real but short page look empty:
    # CHE-C2-SA-04's second page carries the entire unit derivation and scores
    # 0.60% of the full page, under the 0.8% floor, and was dropped.
    written = [q for q in a.answer if _has_writing(q, area="written")]
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
    # THE CUE HAS TO BE IN THIS VIDEO. A caller that hands over a transcript
    # belonging to a DIFFERENT part gets a cue time past the end of the clip —
    # and because the tail is then negative, the extension below would pad a
    # 60s part 1 by 43 seconds to make room for a page cued at 95s. It happened
    # on CHE-C2-LA-01. A cue outside the clip is not a short tail, it is the
    # wrong transcript, so it REFUSES here rather than being papered over.
    if at >= end:
        print(f"cue at {at:.1f}s but the video is {end:.1f}s long — this is not "
              f"this part's transcript; refusing")
        return 2

    # HOLD THE LAST FRAME RATHER THAN HURRY THE PAGES. If the tail between the
    # cue and the end cannot give every page its dwell, the clip grows: the
    # final frame is cloned and the audio padded with silence. Nothing already
    # in the video moves, so a composite that was approved stays approved.
    want = max(MIN_PAGE, a.min_dwell) * len(a.answer)
    extend = max(0.0, (at + want) - end)
    # and the hold can never be longer than the pages need, whatever the cue says
    if extend > want:
        print(f"the hold would be {extend:.1f}s for {want:.1f}s of pages — "
              f"the cue at {at:.1f}s does not belong to this clip; refusing")
        return 2
    if extend:
        print(f"  {len(a.answer)} page(s) need {want:.1f}s and the tail is "
              f"{end - at:.1f}s — holding the last frame {extend:.1f}s longer")
        end += extend
    # TIME BY CONTENT, not equal shares. A page with four lines does not need
    # as long as a page with thirty, and giving it the same slice is what left
    # CHE-C1-SA-01 sitting on its nearly empty second page for eight seconds.
    weights = [max(0.35, _ink(q, area="written")) for q in a.answer]
    tot = sum(weights)
    spans = [(end - at) * wt / tot for wt in weights]
    span = min(spans)
    if span < MIN_PAGE:
        print(f"{len(a.answer)} pages over {end - at:.1f}s is {span:.1f}s each — "
              f"under {MIN_PAGE}s a page cannot be read; not building")
        return 2

    ins, chains, last = [], [], "[0:v]"
    if extend:
        chains.append(f"[0:v]tpad=stop_mode=clone:stop_duration={extend:.3f}[base]")
        last = "[base]"
    for i, page in enumerate(a.answer):
        ins += ["-loop", "1", "-i", str(page)]
        t0 = at + sum(spans[:i])
        # EVERY PAGE STAYS ON TO THE END, so page two dissolves out of page one
        # instead of out of the video. Ending page one at its own slot left the
        # frozen presenter showing through for the 0.7s the next page took to
        # fade up — measured at 182,187,192 where the paper is 253,253,253.
        # The later page is composited after, so it simply covers the earlier.
        t1 = end
        # fit to WIDTH, pad onto the PAGE'S OWN PAPER so the whole screen is
        # one sheet rather than a page floating on a dark plate
        paper = _paper(page)
        chains.append(
            f"[{i + 1}:v]scale={w}:-1:force_original_aspect_ratio=decrease,"
            f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:color={paper},format=yuva420p,"
            f"fade=t=in:st={t0:.2f}:d={a.fade}:alpha=1[p{i}];"
            f"{last}[p{i}]overlay=0:0:enable='between(t,{t0:.2f},{t1:.2f})'[v{i}]")
        last = f"[v{i}]"
    amap, acodec = ["-map", "0:a?"], ["-c:a", "copy"]
    if extend:
        # the padded picture outlasts the audio, and -shortest would then cut
        # the hold straight back off again, so the audio is padded to match
        chains.append(f"[0:a]apad=pad_dur={extend:.3f}[a]")
        amap, acodec = ["-map", "[a]"], ["-c:a", "aac", "-b:a", "192k",
                                         "-ar", "48000"]
    vf = ";".join(chains)
    subprocess.run(["ffmpeg", "-v", "error", "-i", str(src), *ins,
                    "-filter_complex", vf,
                    "-map", last, *amap, "-c:v", "libx264", "-crf", "18",
                    "-preset", "medium", *acodec,
                    *([] if extend else ["-shortest"]),
                    "-t", f"{end:.3f}", str(tmp), "-y"], check=True)
    subprocess.run(["ffprobe", "-v", "error", "-i", str(tmp)], check=True)
    shutil.move(str(tmp), str(dst))
    print(f"answer up at {at:.2f}s, {len(a.answer)} page(s) x {span:.1f}s "
          f"-> {dst}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
