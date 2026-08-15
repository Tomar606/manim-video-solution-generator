"""The house layout, measured off the reference stills rather than invented.

Three approved frames were analysed (`inbox/reference{1,2,3}.jpeg`, 900x1600).
Everything here is a number taken from them, so a scene built on this module
looks like the reference by construction instead of by eye.

WHAT THE REFERENCES ACTUALLY DO
-------------------------------
Caption          two lines, WHITE, centred, and BIG — 8.4% of frame height per
                 line, which is about twice the size we had been using. One
                 keyword may be gold.
Caption position moves with the content. Sitting at 8-11% from the top when
                 something is below it; dropped to 28-44% — vertically centred
                 in the empty space — when the frame is otherwise bare.
Divider          a hairline rule with a small glowing dot at its centre,
                 between the caption and the content.
Formula          very large, serif italic, with a soft glow behind it; 12% of
                 frame height, 64% of frame width.
Legend           under the formula, each symbol coloured to match how it was
                 drawn in the formula itself.
Labels           colour-coded, sitting under what they name, joined to it by a
                 dashed curve, with a smaller white gloss line beneath.
Presenter        56-66% of frame width — NOT the 96% we shipped. Larger when
                 the frame is otherwise empty, smaller when a diagram is up.

The two presenter sizes are why the resize exists: the references are already
doing it. tools/composite.py eases between them over half a second.
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# Palette, sampled from the stills
# ---------------------------------------------------------------------------
INK        = "#FFFFFF"
DIM        = "#B9C6DC"
PLATE      = "#0B1B3A"
GOLD       = "#FFC15C"      # the highlighted keyword, and W in the legend
CYAN       = "#5BC8F9"      # cathode, Q in the legend, the divider's dot
COPPER     = "#E08A4A"      # anode, copper electrode
SILVER     = "#C6D3E0"
GREEN      = "#7CE0B0"
VIOLET     = "#C792EA"

# ---------------------------------------------------------------------------
# Vertical layout, as fractions of frame height
# ---------------------------------------------------------------------------
CAPTION_TOP_Y     = 0.085     # ref1 8.5%, ref3 11.2%
CAPTION_MID_Y     = 0.310     # ref2 — centred when nothing else is on screen
CAPTION_LINE_H    = 0.084     # ref1: 16.7% over two lines
CAPTION_SIZE      = 72        # ~2x what we had; matches the measured line height
CAPTION_W         = 0.92      # ref1 spans 4.6%..96.2%

DIVIDER_Y         = 0.265
DIVIDER_W         = 0.56

STAGE_TOP         = 0.295     # content starts below the divider
STAGE_BOT         = 0.615     # and clears the presenter's head at 64%
STAGE_W           = 0.86

FORMULA_H         = 0.12      # ref3: 30.6%..42.6%
LEGEND_Y          = 0.50

# ---------------------------------------------------------------------------
# The presenter — the composite owns these; they live here so a scene can
# reserve the right space without guessing.
# ---------------------------------------------------------------------------
PRESENTER_FULL_W  = 0.66      # of frame width
PRESENTER_FULL_Y  = 0.503     # head top
PRESENTER_SMALL_W = 0.56
PRESENTER_SMALL_Y = 0.620
PRESENTER_EASE    = 0.5       # seconds


def scene_constants(frame_w: float, frame_h: float) -> dict:
    """The layout in scene units, for a Manim scene to unpack."""
    return {
        "caption_top": CAPTION_TOP_Y,
        "caption_mid": CAPTION_MID_Y,
        "caption_size": CAPTION_SIZE,
        "caption_w": CAPTION_W,
        "divider_y": DIVIDER_Y,
        "divider_w": DIVIDER_W * frame_w,
        "stage": (STAGE_TOP, STAGE_BOT),
        "stage_w": STAGE_W * frame_w,
    }
