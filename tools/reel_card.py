"""The question card for an all-Veo reel, as an overlay PNG.

    python tools/reel_card.py <slug> [--out card.png]

The PYQ route draws this card in Manim, inside the scene. This route has no
Manim scene at all — the picture is a generated clip — so the card is built as
one RGBA overlay the reel lays over its opening shot, which is what the other
subjects do visually anyway: the card sits over the presenter while he reads the
question out.

The geometry is taken from src/question_card.py rather than re-measured, so a
political science card and a chemistry one are the same card. What is drawn:

    ? ring          a thin gold ring, centred, at the very top
    MP Board · कक्षा 12    the heading, with a rule under it
    the sheet       assets/design/question_sheet.png, tilted as photographed
    marks sticker   a gold disc on the sheet's top right — every card has one
                    (memory: marks-sticker-on-every-card)
    years pill      gold, under the torn edge, naming when it was asked

WHY THE TEXT IS NOT DRAWN HERE. The question itself is already baked into the
sheet PNG by tools/paper_header.py — that is the whole point of that tool, and
editing meta.json changes nothing on screen (memory:
question-card-text-is-baked-in). This only places the sheet and the furniture
around it.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, features

ROOT = Path(__file__).resolve().parents[1]
FONTS = ROOT / "assets" / "fonts"
# MEASURED off a delivered card (BIO-C5-SA-03 part 1, frame at 5s), not chosen:
# the heading is GOLD and the rule under it is WHITE, which is the opposite of
# what it looks like at thumbnail size, and the years pill is an OUTLINE with
# nothing behind it rather than a solid gold lozenge. Never trust a by-eye
# colour reading here (CLAUDE.md).
GOLD = (241, 175, 42)
TEAL = (34, 167, 194)        # the year digits, and the tape across the sheet
INK = (18, 40, 58)
WHITE = (250, 252, 253)

Q_MARK_Y, Q_MARK_R = 0.033, 0.027
Q_WORD_Y = 0.095
RULE_Y, RULE_W_MAX = 0.140, 0.66
HEAD_W_MAX = 0.60
PAPER_Y, PAPER_W = 0.345, 0.72
PAPER_TILT = 5.75            # degrees, as the sheet was photographed
TAPE_W, TAPE_H = 0.20, 0.026
# MEASURED off a delivered card, not chosen. The pill's top edge has slope
# -0.0311 in image coordinates, which is a rise of 1.78 degrees to the RIGHT —
# the same direction the paper leans, and the opposite of the -2 degrees this
# had. Rotated the wrong way a tilt does not read as "hand-placed", it reads as
# a mistake, because it fights the sheet above it.
PILL_TILT = 1.8              # degrees, counter-clockwise: right side up
# The tape crosses the paper rather than sitting square on it: src/question_card
# gives it -0.055 rad against the paper's +0.1003, so about nine degrees off the
# sheet's own lean.
TAPE_TILT = -3.15
YEARS_Y = 0.593
MARKS_R, MARKS_DX, MARKS_DY = 0.047, 0.055, 0.030
MARKS_TILT = -8.0


def fit(draw, text, font_path, target_w, start=110):
    size = start
    while size > 12:
        f = ImageFont.truetype(str(font_path), size)
        if draw.textlength(text, font=f) <= target_w:
            return f
        size -= 2
    return ImageFont.truetype(str(font_path), 12)


def rotated_text(text, font, fill, deg):
    probe = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    w = int(probe.textlength(text, font=font)) + 40
    h = int(font.size * 2.0)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((20, int(font.size * 1.4)), text, font=font,
                            fill=fill + (255,), anchor="ls")
    bb = im.getbbox()
    im = im.crop(bb) if bb else im
    return im.rotate(deg, expand=True, resample=Image.BICUBIC)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--out", default="")
    ap.add_argument("--frame", default="1080x1920")
    a = ap.parse_args()
    if not features.check("raqm"):
        print("  Pillow has no raqm — Devanagari would be mis-shaped silently "
              "(memory: pillow-raqm-needs-dyld). Set DYLD_LIBRARY_PATH=/opt/homebrew/lib.")
        return 1
    proj = ROOT / "projects" / a.slug
    meta = json.loads((proj / "meta.json").read_text(encoding="utf-8"))
    sheet_p = proj / "assets" / "design" / "question_sheet.png"
    if not sheet_p.is_file():
        print(f"  no question sheet at {sheet_p} — build it with tools/paper_header.py")
        return 1
    FW, FH = (int(v) for v in a.frame.lower().split("x"))
    out = Path(a.out) if a.out else proj / "work" / "card.png"
    out.parent.mkdir(parents=True, exist_ok=True)

    khand = FONTS / "Khand-Bold.ttf"
    deva = FONTS / "NotoSansDevanagari.ttf"
    im = Image.new("RGBA", (FW, FH), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    # ---- the ? ring -------------------------------------------------------
    r = int(Q_MARK_R * FH)
    cx, cy = FW // 2, int(Q_MARK_Y * FH)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=GOLD + (255,), width=5)
    qf = ImageFont.truetype(str(khand), int(r * 1.6))
    d.text((cx, cy + r // 6), "?", font=qf, fill=GOLD + (255,), anchor="mm")

    # ---- the heading, its ticks, and the WHITE rule under it ---------------
    # Khand is the face the delivered cards are set in — condensed, so the
    # heading fits across the frame at a size that still reads on a phone. The
    # word is GOLD and the rule beneath it is WHITE (measured, see above).
    head = meta.get("sheet_head", "MP Board · कक्षा 12")
    # KHAND, NOT NOTO. Khand covers Devanagari AND Latin and is condensed, which
    # is what the delivered cards are set in: the same string is 527px wide in
    # Khand against 679 in Noto at the same size, so Khand fits across the frame
    # at a size that still reads on a phone. Checked by rendering both.
    hf = fit(d, head, khand, FW * HEAD_W_MAX, start=140)
    hy = int(Q_WORD_Y * FH)
    d.text((FW // 2, hy), head, font=hf, fill=GOLD + (255,), anchor="mm")
    hw = d.textlength(head, font=hf)
    # three small wedges either side, as on the reference
    for side in (-1, 1):
        for k, (dx, dy, ln) in enumerate(((0.10, -0.42, 0.10),
                                          (0.18, 0.00, 0.13),
                                          (0.10, 0.42, 0.10))):
            x0 = FW / 2 + side * (hw / 2 + dx * hw)
            y0 = hy + dy * hf.size
            d.line([x0, y0 - ln * hf.size, x0 + side * 0.055 * hw, y0 + ln * hf.size],
                   fill=GOLD + (255,), width=max(4, int(hf.size * 0.10)))
    rw = min(hw * 1.30, FW * RULE_W_MAX)
    ry = int(RULE_Y * FH)
    d.line([FW / 2 - rw / 2, ry + 6, FW / 2 + rw / 2, ry - 6], fill=WHITE + (255,), width=6)

    # ---- the sheet, tilted as photographed ---------------------------------
    sheet = Image.open(sheet_p).convert("RGBA")
    tw = int(FW * PAPER_W)
    sheet = sheet.resize((tw, int(sheet.height * tw / sheet.width)), Image.LANCZOS)
    sheet = sheet.rotate(PAPER_TILT, expand=True, resample=Image.BICUBIC)
    sx, sy = (FW - sheet.width) // 2, int(PAPER_Y * FH) - sheet.height // 2
    im.alpha_composite(sheet, (sx, sy))

    # ---- the washi tape across the sheet's top -----------------------------
    tw_, th_ = int(FW * TAPE_W), int(FH * TAPE_H)
    tape = Image.new("RGBA", (tw_, th_), TEAL + (215,))
    tape = tape.rotate(TAPE_TILT, expand=True, resample=Image.BICUBIC)
    # ON the sheet, not above it. `sheet` has transparent padding from the
    # rotation, so its top edge is lower in the bitmap than its bounding box —
    # offsetting from the box left the tape floating clear of the paper.
    edge = (sheet.getbbox() or (0, 0, sheet.width, sheet.height))[1]
    im.alpha_composite(tape, (sx + sheet.width // 2 - tape.width // 2 - int(FW * 0.02),
                              sy + edge + int(sheet.height * 0.035)))

    # ---- the marks sticker, on the sheet's top right ------------------------
    marks = meta.get("marks")
    if marks:
        mr = int(MARKS_R * FH)
        disc = Image.new("RGBA", (mr * 2, mr * 2), (0, 0, 0, 0))
        dd = ImageDraw.Draw(disc)
        dd.ellipse([0, 0, mr * 2 - 1, mr * 2 - 1], fill=GOLD + (255,))
        nf = ImageFont.truetype(str(khand), int(mr * 1.15))
        wf = ImageFont.truetype(str(khand), int(mr * 0.62))
        dd.text((mr, mr - int(mr * 0.18)), str(marks), font=nf, fill=INK + (255,), anchor="mm")
        dd.text((mr, mr + int(mr * 0.52)), "अंक", font=wf, fill=INK + (255,), anchor="mm")
        disc = disc.rotate(MARKS_TILT, expand=True, resample=Image.BICUBIC)
        mx = sx + sheet.width - int(MARKS_DX * FW) - disc.width // 2
        my = sy + int(MARKS_DY * FH)
        im.alpha_composite(disc, (max(0, mx), max(0, my)))

    # ---- the years pill: an OUTLINE, two lines, year in teal ----------------
    # Not a solid gold lozenge — the delivered card draws a gold border with the
    # plate showing through, "वर्ष <years> में" on the first line with only the
    # YEARS in teal, "ये प्रश्न था" on the second, and small gold wedges at the
    # corners.
    years = meta.get("years", "")
    if years:
        l1a, l1b, l1c = "वर्ष ", years, " में"
        l2 = "ये प्रश्न था"
        # SIZED FROM THE PILL'S HEIGHT, not from how much width is free. Fitting
        # to width made Khand pick 110px, and the pill grew tall enough to cover
        # the last line of the question on the sheet above it. The delivered
        # pill measures about 9% of frame height for two lines, so the type is
        # set from that and only shrunk further if the year string is long.
        psize = int(FH * 0.034)
        pf = ImageFont.truetype(str(khand), psize)
        while psize > 20 and d.textlength(l1a + l1b + l1c, font=pf) > FW * 0.54:
            psize -= 2
            pf = ImageFont.truetype(str(khand), psize)
        yf = ImageFont.truetype(str(khand), int(pf.size * 1.10))
        w1 = (d.textlength(l1a, font=pf) + d.textlength(l1b, font=yf)
              + d.textlength(l1c, font=pf))
        w2 = d.textlength(l2, font=pf)
        pad_x, pad_y = int(pf.size * 1.10), int(pf.size * 0.70)
        pw = int(max(w1, w2)) + pad_x * 2
        ph = int(pf.size * 2.9) + pad_y
        pill = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
        pd = ImageDraw.Draw(pill)
        pd.rounded_rectangle([3, 3, pw - 4, ph - 4], radius=int(pf.size * 0.55),
                             outline=GOLD + (255,), width=6)
        y1 = int(ph * 0.36)
        x = (pw - w1) / 2
        pd.text((x, y1), l1a, font=pf, fill=WHITE + (255,), anchor="lm")
        x += d.textlength(l1a, font=pf)
        pd.text((x, y1), l1b, font=yf, fill=TEAL + (255,), anchor="lm")
        x += d.textlength(l1b, font=yf)
        pd.text((x, y1), l1c, font=pf, fill=WHITE + (255,), anchor="lm")
        pd.text((pw // 2, int(ph * 0.72)), l2, font=pf, fill=WHITE + (255,), anchor="mm")
        for cx_, cy_, ex, ey in ((0.02, 0.10, -1, -1), (0.98, 0.10, 1, -1),
                                 (0.02, 0.90, -1, 1), (0.98, 0.90, 1, 1)):
            bx, by = pw * cx_, ph * cy_
            pd.line([bx, by, bx + ex * pf.size * 0.55, by + ey * pf.size * 0.42],
                    fill=GOLD + (255,), width=6)
        # the whole pill turns, border and both lines of type together, so the
        # text leans with the box instead of sitting level inside a tilted frame
        pill = pill.rotate(PILL_TILT, expand=True, resample=Image.BICUBIC)
        # BELOW THE TORN EDGE, measured from the sheet rather than from a fixed
        # height: the sheet's height depends on how many lines the question ran
        # to, so a constant y put the pill across the last line of a three-line
        # question and left a gap under a one-line one.
        py = max(int(YEARS_Y * FH) - pill.height // 2, sy + sheet.height + int(FH * 0.012))
        im.alpha_composite(pill, ((FW - pill.width) // 2, py))

    im.save(out)
    print(f"  {out.relative_to(ROOT)}  {FW}x{FH}  "
          f"sheet {sheet.width}x{sheet.height} at ({sx},{sy})"
          + (f", {marks} marks" if marks else "")
          + (f", years '{years}'" if years else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
