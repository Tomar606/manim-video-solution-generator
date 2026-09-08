"""Correct a phrase on an answer page using handwriting lifted from another page.

    python tools/patch_answer.py

WHY LIFT RATHER THAN TYPESET
----------------------------
The answer pages are handwriting. A correction set in Mukta or Poppins over one
reads as a sticker, and re-running the generator to fix two words returns a page
that differs everywhere else. Both chapter-10 pages came from the same hand and
the phrase needed -- "B₉" and "फोलिक अम्ल" -- is already on the other one, so the
correction is a copy, not a font.

WHAT IS BEING CORRECTED
-----------------------
CHE-C10-LA-02 item (vii) read:

    (साइडरोब्लास्टिक एनीमिया)–विटामिन-B₆ (पिरिडॉक्सीन)।

The narration says plainly "B6 मत लिखना" and pairs अरक्तता with फोलिक अम्ल, and
the team's own CHE-C10-LA-01 key agrees: row 5 is "विटामिन B₉ | फोलिक अम्ल |
यीस्ट, हरी पत्तेदार सब्ज़ी | एनीमिया". The parenthetical goes with the number:
sideroblastic anaemia IS the B₆ one, so leaving it beside B₉ would swap one
contradiction for another. The whole line is relaid as:

    –विटामिन-B₉ (फोलिक अम्ल)।

ERASING
-------
By tiling blank ruled paper from the same line further right, never a flat fill:
the page has a ruling and a paper grain, and a filled rectangle shows up as a
patch under compression. Every glyph is captured BEFORE the wipe -- taking them
after returns blank paper, which is how the first attempt lost its brackets.
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image

SRC = Path("inbox/answers/endscreenshot/CHEC10LA01.png")     # has the handwriting
TGT = Path("inbox/answers/endscreenshot/CHE-C10-LA-02.png")  # gets corrected
OUT = Path("inbox/answers/endscreenshot/CHE-C10-LA-02.corrected.png")

TOP, BOT = 1274, 1332                 # the line being relaid
LEFT, RIGHT = 86, 874                 # its ink, end to end
BASE = 1281                           # where the tall letters start

G_B9    = (132, 1020, 172, 1060)      # "B₉"          — LA-01, table row 5
G_FOLIC = (268,  994, 440, 1036)      # "फोलिक अम्ल"   — LA-01, table row 5
T_DASH  = (442, 1274, 600, 1332)      # "–विटामिन-"    — already on this line
T_OPEN  = (655, 1280, 672, 1330)      # "("  alone — wider crops caught the पि
T_CLOSE = (816, 1280, 846, 1330)      # ")।" — the ) is at 819..828, not 830
T_B6    = (600, 1280, 645, 1330)      # the old "B₆", for its size
CLEAN   = (884, 1274, 1012, 1332)     # blank ruled paper, same line


def main() -> None:
    src = Image.open(SRC).convert("RGB")
    tgt = Image.open(TGT).convert("RGB")

    # capture everything first — after the wipe these regions are blank paper
    b9 = src.crop(G_B9)
    folic = src.crop(G_FOLIC)
    dash, opn, close = tgt.crop(T_DASH), tgt.crop(T_OPEN), tgt.crop(T_CLOSE)
    b6_w, b6_h = T_B6[2] - T_B6[0], T_B6[3] - T_B6[1]
    b9 = b9.resize((b6_w, b6_h), Image.LANCZOS)      # the table hand is smaller

    # PASTE THE INK, NOT A RECTANGLE. Shifting a crop's brightness to match the
    # target's paper washed out the pen along with it, and any opaque paste
    # carries its own paper tone as a visible patch. Building a mask from the
    # crop's darkness means only the strokes land and the target's own paper
    # shows between them, so there is no seam to match.
    def ink_mask(im, lo=155, hi=232):   # thin bracket strokes were falling in the
        # transparent half of a tighter ramp and coming through as dots
        g = im.convert("L")
        return g.point(lambda v: 255 if v < lo else
                       (0 if v > hi else int(255 * (hi - v) / (hi - lo))))

    clean = tgt.crop(CLEAN)
    for x in range(LEFT, RIGHT, clean.width):
        tgt.paste(clean.crop((0, 0, min(clean.width, RIGHT - x), BOT - TOP)), (x, TOP))

    pen = LEFT
    for glyph, top, gap in ((dash, TOP, 6), (b9, T_B6[1], 10),
                            (opn, T_OPEN[1], 4), (folic, T_OPEN[1] - 2, 4),
                            (close, T_CLOSE[1], 0)):
        tgt.paste(glyph, (pen, top), mask=ink_mask(glyph))
        pen += glyph.width + gap
    tgt.save(OUT)

    before = Image.open(TGT).convert("RGB").crop((0, 1215, 1024, 1340))
    proof = Image.new("RGB", (1024, 260), "white")
    proof.paste(before, (0, 0))
    proof.paste(tgt.crop((0, 1215, 1024, 1340)), (0, 130))
    proof.save(OUT.with_name("patch_proof.png"))
    print(f"corrected -> {OUT}\nproof (before above, after below) -> "
          f"{OUT.with_name('patch_proof.png')}")


if __name__ == "__main__":
    main()
