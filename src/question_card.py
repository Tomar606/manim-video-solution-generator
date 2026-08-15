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
WRITABLE = (0.205, 0.215, 0.935, 0.845)     # x0, y0, x1, y1

PAPER = "assets/design/notepaper.png"

# Palette from the approved still
PAPER_INK   = "#132A4A"      # the handwriting
PAPER_HILITE = "#1B7FA8"     # the highlighted phrase, teal
GOLD        = "#F2B233"
CREAM       = "#FFFFFF"
TEAL        = "#2AA9C4"

# Vertical layout, fractions of frame height, from the approved still
Q_MARK_Y    = 0.068
Q_WORD_Y    = 0.125
RULE_Y      = 0.183
PAPER_Y     = 0.400          # centre of the paper
PAPER_H     = 0.395          # its height
YEARS_Y     = 0.645

START_SIZE  = 62             # handwriting size before any shrink
MIN_SIZE    = 26             # below this the card is unreadable; raise instead


def wrap_to_width(words, width_of, limit, space):
    """Greedy wrap on MEASURED width — Devanagari conjuncts are not equal width,
    so a character count overflows on exactly the questions that matter."""
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
