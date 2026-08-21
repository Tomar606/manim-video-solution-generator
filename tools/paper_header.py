"""Build the MP Board question-paper header, one template per subject.

    python tools/paper_header.py                       # all four subjects
    python tools/paper_header.py --subject physics

The approved design (`inbox/sticky_note_design.png`) is a torn corner of the
real Higher Secondary paper: roll-number box, printed-pages and marks, a QR
code, the paper serial, the SET stamp, the board line, the year, then the
subject, then the question. Everything on it is fixed across the batch EXCEPT
the subject line and the question, so this rewrites the subject line in place
and leaves the rest of the sheet — texture, creases, torn edge, drop shadow —
exactly as approved.

WHY REWRITE INSTEAD OF REBUILD
------------------------------
The header could be drawn from scratch, but the paper is photographed: it is
creased, unevenly lit, torn along two edges and slightly rotated, and none of
that survives being redrawn. Replacing one line keeps the photograph.

MATCHING THE TYPE
-----------------
The design sets the subject in a bold Devanagari serif beside a bold Latin
serif. Measured off it: cap height 58px, baseline rising 1.89° to the right
(the sheet is rotated, so every line does), centred at x=612.

  Devanagari   Shree Devanagari 714 Bold — the serif Devanagari that Indian
               exam papers are actually set in, and a match for the design
  Latin        Times New Roman Bold

THE ERASE
---------
The line above drops descendants to y≈556 and "(Hindi & English Version)"
starts at y≈643, so the band that may be cleared is only 558..641 — narrow, and
worth knowing before widening it. The paper behind is shaded and creased, so it
is rebuilt by interpolating down each column between the row above the band and
the row below it, which follows the shading instead of flattening it.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
DESIGN = ROOT / "inbox" / "sticky_note_design.png"
OUT = ROOT / "inbox" / "preview"

DEV_FONT = "/System/Library/Fonts/Supplemental/Shree714.ttc"
LAT_FONT = "/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf"
DEV_INDEX = 1                     # Shree714.ttc faces: 0 regular, 1 BOLD,
                                  # 2 italic, 3 bold italic. Index 2 set the
                                  # subject in italic, which the design is not.

# Measured off the approved design, in its own pixels.
BAND = (290, 558, 950, 641)       # the rectangle the subject line may occupy
CENTRE_X = 612                    # the line is centred on this
BASELINE_Y = 625                  # where the glyphs sit at CENTRE_X
TILT_DEG = -2.70                  # the sheet's rotation, so every line follows it.
                                  # Median of the printed lines that fit cleanly
                                  # (board -2.38, year -3.23, subject -2.06,
                                  # marks -3.07). The sheet is CRUMPLED, so no two
                                  # lines agree exactly; taking the subject line's
                                  # own -1.9 left it visibly flatter than its
                                  # neighbours.
CAP_PX = 58                       # Devanagari headline-to-baseline, measured
INK = (26, 26, 26)

# MP Board names each subject in Hindi and then in English, on one line.
SUBJECTS = {
    "physics":   ("भौतिक शास्त्र", "PHYSICS"),
    "chemistry": ("रसायन शास्त्र", "CHEMISTRY"),
    "biology":   ("जीव विज्ञान", "BIOLOGY"),
    "maths":     ("गणित", "MATHEMATICS"),
}

# The question the sample card carries. Chemistry keeps the one the design was
# drawn with; the rest are typical MP Board Class 12 long answers for the
# subject, so each sample shows a real question rather than a borrowed one.
QUESTIONS = {
    "physics":   "गॉस का नियम लिखिए तथा इसे सिद्ध कीजिए।",
    "chemistry": "फैराडे के विद्युत्-अपघटन के नियम लिखिए।",
    "biology":   "मेण्डल के आनुवंशिकता के नियम लिखिए।",
    "maths":     "समाकलन विधि से वृत्त का क्षेत्रफल ज्ञात कीजिए।",
}

# The question is set in a Devanagari SANS, not the serif of the header above it.
Q_FONT   = str(Path.home() / "Library/Fonts/NotoSansDevanagari.ttf")
Q_BAND   = (345, 815, 1020, 1032)   # ONLY where the design's question ink sits.
                                    # Clearing further right and further down
                                    # flattened the sheet's diagonal fold and its
                                    # torn corner into a pale block. A replacement
                                    # that runs to three lines simply writes the
                                    # last one onto clean paper below.
Q_LEFT   = 330                      # where the first line starts. '(1)' ends
                                    # at x=260, so this is as far left as the
                                    # question can begin — the extra width buys
                                    # a line back on the longest questions.
Q_TOP    = 820                      # top of the first line's ink
Q_LINE_H = 105                      # measured line pitch at Q_INK_H
Q_BOTTOM = 1112                     # last row the paper can carry text on.
                                    # 1168 put the closing line of the two
                                    # longest questions ON the torn edge.
Q_INK_H  = 98                       # measured height of one line's ink


def inpaint_band(im: Image.Image, band) -> Image.Image:
    """Rebuild the paper inside `band`, keeping its shading and grain.

    Two obvious approaches both fail on this sheet:

      interpolate from the rows just outside the band — the line above drops
      descenders INTO the row above, so that ink gets dragged down the whole
      band as vertical streaks;

      filter the ink out of the band itself — a max filter lifts the patch
      above the surrounding paper, and a median wide enough to be safe still
      leaves grey ghosts where the original bold capitals were, because their
      strokes are thicker than the window.

    So it samples neither: it finds the nearest row ABOVE and BELOW that is
    genuinely clean across this x-range, and interpolates between those. No ink
    is ever read, so nothing can be smeared or left behind, and the crease
    shading still varies down the band because the two ends differ.
    """
    x0, y0, x1, y1 = band
    rgb = im.convert("RGB")
    g = np.asarray(rgb.convert("L")).astype(int)
    alpha = np.asarray(im.convert("RGBA"))[..., 3] > 128
    h = g.shape[0]

    def clean(y: int) -> bool:
        """A row of plain paper across this x-range.

        Alpha matters: off the torn edge the sheet is transparent, which
        converts to BLACK and reads as ink. Testing without it found no clean
        row below the question — the paper simply ends there — and the whole
        erase silently did nothing, leaving the old question under the new one.
        """
        on = alpha[y, x0:x1]
        if on.mean() < 0.9:
            return False
        return (g[y, x0:x1][on] < 130).mean() < 0.01

    up = next((y for y in range(y0 - 1, max(0, y0 - 140), -1) if clean(y)), None)
    dn = next((y for y in range(y1 + 1, min(h, y1 + 140)) if clean(y)), None)
    if up is None and dn is None:
        return im
    # The question is the last block on the sheet, so there is nothing clean
    # below it. One end is enough: the shading is then held constant down the
    # band instead of graded, which on this much paper is not visible.
    if up is None:
        up = dn
    if dn is None:
        dn = up

    a = np.asarray(rgb).astype(float)

    def smooth(row):
        """Keep the shading, drop the grain.

        Interpolating between two RAW rows repeats each row's per-pixel noise
        down its own column, which reads as vertical striping across the whole
        band — and any crease pixel in a source row becomes a full-height line.
        Averaging along the row first leaves only the slow left-to-right
        shading, which is the part that should carry down.
        """
        k = 31
        pad = np.pad(row, ((k // 2, k // 2), (0, 0)), mode="edge")
        ker = np.ones(k) / k
        return np.stack([np.convolve(pad[:, c], ker, mode="valid")
                         for c in range(row.shape[1])], axis=1)

    top, bot = smooth(a[up, x0:x1]), smooth(a[dn, x0:x1])
    for y in range(y0, y1):
        t = 0.0 if dn == up else (y - up) / (dn - up)
        a[y, x0:x1] = top * (1 - t) + bot * t

    rng = np.random.default_rng(7)              # the sheet has visible grain
    n = y1 - y0
    a[y0:y1, x0:x1] = np.clip(
        a[y0:y1, x0:x1] + rng.normal(0, 2.2, (n, x1 - x0, 1)), 0, 255)

    # Write back through the ALPHA channel, never by pasting.
    # `out.paste(rgb_image, (0, 0))` on an RGBA sheet sets alpha to 255
    # everywhere, so the transparent surround around the torn edge becomes
    # opaque — and the card then rendered as a black rectangle behind the paper.
    out = np.array(im.convert("RGBA"))
    out[..., :3] = a.astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def measure_original() -> tuple[int, int, int, int]:
    """Ink bounding box of the subject line as the design sets it."""
    im = Image.open(DESIGN).convert("L")
    g = np.asarray(im).astype(int)
    x0, y0, x1, y1 = BAND
    ink = g[y0:y1, x0:x1] < 110
    rows = np.nonzero(ink.any(axis=1))[0]
    cols = np.nonzero(ink.any(axis=0))[0]
    return (x0 + int(cols.min()), y0 + int(rows.min()),
            x0 + int(cols.max()), y0 + int(rows.max()))


def subject_line(hindi: str, english: str, target_h: int,
                 max_w: int) -> Image.Image:
    """The subject, set the way the design sets it, cropped to its ink.

    Sized by MEASURING what was drawn rather than by choosing a point size:
    the Devanagari and the Latin have different vertical metrics, and a font
    size that matches one overshoots the other. Rendering, measuring the ink and
    scaling to the height the design uses gets both right at once, and never
    depends on which font happens to be installed.
    """
    size = target_h
    probe = ImageDraw.Draw(Image.new("L", (1, 1)))
    joiner = "  –  "

    def render(px: int) -> Image.Image:
        dev = ImageFont.truetype(DEV_FONT, px, index=DEV_INDEX)
        lat = ImageFont.truetype(LAT_FONT, px)
        head = hindi + joiner
        w = probe.textlength(head, font=dev) + probe.textlength(english, font=lat)
        img = Image.new("RGBA", (int(w) + px * 2, px * 4), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        base = px * 3                      # one shared baseline for both runs
        d.text((px, base), head, font=dev, fill=INK + (255,), anchor="ls")
        d.text((px + probe.textlength(head, font=dev), base), english,
               font=lat, fill=INK + (255,), anchor="ls")
        a = np.asarray(img)[..., 3] > 40
        ys, xs = np.nonzero(a)
        return img.crop((int(xs.min()), int(ys.min()),
                         int(xs.max()) + 1, int(ys.max()) + 1))

    img = render(size)
    for _ in range(8):
        if abs(img.height - target_h) <= 1:
            break
        size = max(8, round(size * target_h / max(1, img.height)))
        img = render(size)
    if img.width > max_w:                  # a long subject may not fit the sheet
        k = max_w / img.width
        img = img.resize((max_w, max(1, round(img.height * k))), Image.LANCZOS)
    return img


def question_block(text: str, ink_h: int, max_w: int,
                   avail_h: int | None = None):
    """The question, wrapped and set the way the design sets it.

    Wrapped on MEASURED width — Devanagari conjuncts are not equal width, so a
    character count overflows exactly on the long questions, and this sheet has
    a hard right edge where the paper is torn.

    And wrapped to a HEIGHT as well. The design was drawn with a nine-word
    question; four of the five in this batch are two to three times that, and
    wrapping to width alone simply kept adding lines — they ran off the torn
    bottom edge of the paper. So the type shrinks until the block fits the paper
    it is written on, exactly as the notepaper card does.

    Returns (rows, line_pitch): the pitch scales with the type, or a shrunken
    block would still be set on the original spacing and run off anyway.
    """
    probe = ImageDraw.Draw(Image.new("L", (1, 1)))

    def font(px):
        return ImageFont.truetype(Q_FONT, px)

    def ink_of(img):
        a = np.asarray(img)[..., 3] > 40
        ys, xs = np.nonzero(a)
        return img.crop((int(xs.min()), int(ys.min()),
                         int(xs.max()) + 1, int(ys.max()) + 1))

    def draw(line, px):
        """A line cropped horizontally to its ink but NOT vertically.

        Cropping vertically too and then stacking the crops aligns their TOPS,
        and Devanagari lines are not the same height — one with a high matra is
        taller than one without, so the line under it gets pushed down into it.
        Every line keeps the same vertical window here, so stacking them at a
        fixed pitch aligns their BASELINES, which is what leading means.
        """
        f = font(px)
        w = int(probe.textlength(line, font=f)) + px * 2
        img = Image.new("RGBA", (w, px * 3), (0, 0, 0, 0))
        ImageDraw.Draw(img).text((px, px * 2), line, font=f,
                                 fill=INK + (255,), anchor="ls")
        a = np.asarray(img)[..., 3] > 40
        cols = np.nonzero(a.any(axis=0))[0]
        return img.crop((int(cols.min()), 0, int(cols.max()) + 1, img.height))

    def draw_width(line, px):
        return probe.textbbox((0, 0), line, font=font(px))[2]

    def wrap(px):
        f = font(px)
        lines, cur = [], ""
        for word in text.split():
            trial = f"{cur} {word}".strip()
            if cur and probe.textlength(trial, font=f) > max_w:
                lines.append(cur); cur = word
            else:
                cur = trial
        if cur:
            lines.append(cur)
        return lines

    # Size so one line's INK matches the design's line height. `size` is a font
    # size and `ink_h` is a measured pixel height — they are different units, so
    # the pitch below is scaled by size/base_size, never by size/ink_h. Scaling
    # by the latter collapsed four lines into two overlapping ones.
    size = ink_h
    probe_word = max(text.split(), key=len)
    for _ in range(8):
        h = draw(probe_word, size)
        a = np.asarray(h)[..., 3] > 40
        ys = np.nonzero(a.any(axis=1))[0]
        got = int(ys.max() - ys.min() + 1) if len(ys) else ink_h
        if abs(got - ink_h) <= 2:
            break
        size = max(8, round(size * ink_h / max(1, got)))
    base_size = size

    def pitch_for(px):
        # 1.10: a block set smaller needs proportionally MORE leading, because
        # Devanagari carries matras above the headline and conjuncts below the
        # baseline whatever the size.
        return max(1, round(Q_LINE_H * (px / base_size) * 1.10))

    floor = max(16, int(base_size * 0.55))
    while size > floor:
        lines = wrap(size)
        if avail_h is None or len(lines) * pitch_for(size) <= avail_h:
            break
        size -= 2
    lines = wrap(size)

    # Last resort: TRUNCATE. The loop above shrinks the type until the block
    # fits, but it stops at a legibility floor — and below that floor it used to
    # print anyway, so the longest questions ran off the torn bottom edge and
    # onto the background. A question that cannot fit at a readable size is cut
    # at the last line that fits and ends in an ellipsis; the card is a hook, and
    # the full question is on screen in the caption and on the answer page.
    if avail_h is not None:
        pitch = pitch_for(size)
        keep = max(1, int(avail_h // pitch))
        if len(lines) > keep:
            lines = lines[:keep]
            tail = lines[-1].rstrip(" ।,;:-")
            # trim words until the ellipsis itself also fits the width
            while tail and draw_width(tail + " ...", size) > max_w:
                tail = " ".join(tail.split(" ")[:-1]).rstrip(" ।,;:-")
            lines[-1] = (tail + " ...") if tail else "..."
    return [draw(l, size) for l in lines], pitch_for(size), size * 2


def build(subject: str, dest: Path, question: str | None = None) -> Path:
    """One sheet. `question` overrides the sample question for that subject."""
    hindi, english = SUBJECTS[subject]
    ox0, oy0, ox1, oy1 = measure_original()
    sheet = inpaint_band(Image.open(DESIGN).convert("RGBA"), BAND)

    line = subject_line(hindi, english, oy1 - oy0, BAND[2] - BAND[0] - 20)
    line = line.rotate(-TILT_DEG, expand=True, resample=Image.BICUBIC)

    # Land it exactly where the original ink sat: same horizontal centre, same
    # bottom. Anchoring on a computed baseline instead means trusting the font's
    # metrics and the rotation maths at once, and getting either wrong moves the
    # line visibly on a sheet where everything else is fixed.
    cx = (ox0 + ox1) // 2
    sheet.alpha_composite(line, (cx - line.width // 2, oy1 - line.height))

    # ---- the question ------------------------------------------------- #
    # "प्रश्न –" and "(1)" are fixed furniture and stay; only the sentence to
    # the right of them is replaced, so each sample carries its own subject's
    # question instead of borrowing chemistry's.
    sheet = inpaint_band(sheet, Q_BAND)
    rows, pitch, baseline = question_block(question or QUESTIONS[subject],
                                           Q_INK_H, Q_BAND[2] - Q_LEFT - 10,
                                           avail_h=Q_BOTTOM - Q_TOP)
    for i, row in enumerate(rows):
        row = row.rotate(-TILT_DEG, expand=True, resample=Image.BICUBIC)
        # baselines, not tops: `baseline` is where the text sits inside every
        # crop, so subtracting it puts each line's baseline on the same rail
        y = Q_TOP + i * pitch - baseline + int(Q_INK_H * 0.80)
        # each line starts a little further left as the sheet rises to the right
        x = Q_LEFT - int(i * pitch * np.tan(np.radians(-TILT_DEG)))
        sheet.alpha_composite(row, (x, y))

    dest.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(dest)
    return dest


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--subject", choices=sorted(SUBJECTS))
    p.add_argument("--out", default=str(OUT))
    p.add_argument("--question", help="override the sample question")
    p.add_argument("--name", help="output filename stem")
    a = p.parse_args()
    todo = [a.subject] if a.subject else sorted(SUBJECTS)
    for s in todo:
        stem = a.name or f"paper_header_{s}"
        dest = Path(a.out) / f"{stem}.png"
        build(s, dest, question=a.question)
        print(f"   {SUBJECTS[s][0]} – {SUBJECTS[s][1]:12} -> {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
