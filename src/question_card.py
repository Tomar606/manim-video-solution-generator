"""The opening question card, built to the approved design.

    ?            a ringed question mark
    प्रश्न        gold, with sparks, over a hairline rule
    [notepaper]  the question handwritten on torn ruled paper, taped at the top
    वर्ष …        a gold pill naming the years the question appeared
    presenter    composited below

The whole point of this module is that it must survive a BATCH. Question text
varies from eight words to forty, and the failure everyone fears is text
leaking off the paper. So the fit is not eyeballed:

  1. the writable area is measured from the asset — right of the red margin
     rule, inside the torn edge, clear of the tape
  2. the text is wrapped to that width at a starting size
  3. if it still overflows, the size drops and it re-wraps, until it fits
  4. `fits()` then asserts containment, and raises rather than rendering a card
     with text hanging off the paper

`assets/design/notepaper.png` is 3316x3044 with real alpha. Measured on it:
red margin at x 16.2%, opaque bbox x 4.1%..98.0%, y 5.0%..95.8%.
"""
from __future__ import annotations

# Fractions of the paper image. Generous of the measured values because the
# paper is drawn at a slight angle and the bottom-right corner is torn away.
WRITABLE = (0.200, 0.190, 0.940, 0.870)     # x0, y0, x1, y1

PAPER = "assets/design/notepaper.png"

# The angle everything drawn ON the sheet takes, or the card reads as a straight
# caption sitting on a crooked paper.
#
# Measured off the RULED LINES, by tracking six of them across the sheet and
# fitting each: +5.75 degrees. It was previously measured off the top edge and
# came out at +2.54, which is a different angle and the wrong one — the top edge
# is TORN, so its slope is whatever the tear happened to do, while the ruled
# lines are printed parallel and are what handwriting actually sits on. Text
# rotated by the edge angle sat visibly across the lines it was meant to follow.
PAPER_TILT = 0.1003          # radians, +5.75 degrees

# Palette from the approved still
PAPER_INK   = "#132A4A"      # the handwriting
PAPER_HILITE = "#1B7FA8"     # the highlighted phrase, teal
GOLD        = "#F2B233"
CREAM       = "#FFFFFF"
TEAL        = "#2AA9C4"

# Every number below is MEASURED off the approved still and checked against a
# render of this card, component by component. Earlier versions had the tilt
# measured and everything else guessed, and the header overlapped the ring.
#
#   component   reference (fraction of frame)
#   ? ring      y  4.4%.. 9.9%   h  5.4%   w  9.4%   centred
#   प्रश्न+ticks y  7.7%..17.8%   h 10.1%   w 40.9%
#   notepaper   y 19.7%..66.6%   h 46.9%   w 83.7%
#   years pill  y 57.2%..79.9%   h 22.7%   w 60.6%
Q_MARK_Y    = 0.033          # ring centre — clear of प्रश्न below it
Q_MARK_R    = 0.027          # ring radius, fraction of frame HEIGHT
Q_WORD_Y    = 0.095
Q_WORD_SIZE = 78             # was 96 — the word crowded the ring above it
TICK_PAD    = 0.30           # ticks sit CLOSE to the word, as in the still           # ticks reach out to the reference's 40.9% width
RULE_Y      = 0.140
RULE_W      = 1.55           # the rule runs WIDER than the word
PAPER_Y     = 0.345          # centre: reference spans 19.7%..66.6%
PAPER_W     = 0.72          # slightly smaller than the still reads          # width drives the fit, not height
YEARS_Y     = 0.593          # BELOW the torn edge, never on it

START_SIZE  = 62             # handwriting size before any shrink
# Measured, not guessed: at font_size 26 a Khand Bold line renders 44px tall on
# a 1080x1920 frame — about the size of the labels under a diagram, which read
# fine on a phone. Below that it stops being handwriting and starts being fine
# print, so the card raises instead of shrinking further.
MIN_SIZE    = 26


def split_long(word, width_of, limit):
    """Break a token that is wider than the paper, whatever the size.

    Hyphenated compounds — "वाष्प-दाब-में-आपेक्षिक-अवनमन" — are a single
    unbreakable token to a greedy wrapper, and one of them ran nearly three
    times the width of the paper at the smallest readable size. They break at
    their own hyphens; anything else breaks mid-word rather than leaking.
    """
    if width_of(word) <= limit:
        return [word]
    if "-" in word:
        out, cur = [], ""
        for part in word.split("-"):
            trial = f"{cur}-{part}" if cur else part
            if cur and width_of(trial) > limit:
                out.append(cur + "-")
                cur = part
            else:
                cur = trial
        return out + ([cur] if cur else [])
    lo, out = 0, []
    while lo < len(word):
        hi = len(word)
        while hi > lo + 1 and width_of(word[lo:hi]) > limit:
            hi -= 1
        out.append(word[lo:hi])
        lo = hi
    return out


def wrap_to_width(words, width_of, limit, space):
    """Greedy wrap on MEASURED width — Devanagari conjuncts are not equal width,
    so a character count overflows on exactly the questions that matter."""
    words = [p for w in words for p in split_long(w, width_of, limit)]
    lines, cur, w = [], [], 0.0
    for word in words:
        ww = width_of(word)
        trial = w + (space + ww if cur else ww)
        if cur and trial > limit:
            lines.append(cur)
            cur, w = [word], ww
        else:
            cur.append(word)
            w = trial
    if cur:
        lines.append(cur)
    return lines


def fit_lines(text, width_of, limit_w, limit_h, line_h_of, space_of,
              start=START_SIZE, floor=MIN_SIZE):
    """Largest size at which the question fits the writable area.

    Returns (size, lines). Shrinks in steps rather than solving analytically —
    the wrap changes as the size changes, so the height is not a smooth function
    of it and a closed form would be wrong.
    """
    words = text.split()
    size = start
    while size >= floor:
        lines = wrap_to_width(words, lambda w: width_of(w, size), limit_w,
                              space_of(size))
        if len(lines) * line_h_of(size) <= limit_h:
            return size, lines
        size -= 3
    # at the floor, take what we have — fits() below is what actually refuses
    return floor, wrap_to_width(words, lambda w: width_of(w, floor), limit_w,
                                space_of(floor))


def writable_box(paper_mob):
    """(centre, width, height) of the area that may carry text, in scene units."""
    x0, y0, x1, y1 = WRITABLE
    w, h = paper_mob.width, paper_mob.height
    left = paper_mob.get_left()[0]
    top = paper_mob.get_top()[1]
    cx = left + w * (x0 + x1) / 2
    cy = top - h * (y0 + y1) / 2
    return (cx, cy), w * (x1 - x0), h * (y1 - y0)


def fits(text_mob, paper_mob, slack=0.02):
    """True when the text is inside the paper's writable area.

    Called before the card is returned. A batch that silently ships one card
    with the question hanging off the paper is worse than one that stops.
    """
    (cx, cy), bw, bh = writable_box(paper_mob)
    return (abs(text_mob.get_center()[0] - cx) <= bw / 2 + slack and
            abs(text_mob.get_center()[1] - cy) <= bh / 2 + slack and
            text_mob.width <= bw * (1 + slack) and
            text_mob.height <= bh * (1 + slack))
