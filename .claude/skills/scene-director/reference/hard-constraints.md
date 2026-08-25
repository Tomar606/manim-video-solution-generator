# Hard constraints — every one of these SHIPPED

These override visual ambition. A plan that violates one is a failed plan, no
matter how good the teaching idea is.

## The presenter

- **Anchored to the bottom border.** His feet land on 1920. Never floating.
  The compositor derives the top from the scaled height; a plan must never ask
  for a fixed vertical offset. Cause when it broke: crop and anchor are coupled —
  a wider crop scales to a SHORTER avatar at the same on-screen width, so a fixed
  top left him hanging in mid-air across a whole rebuild.
- **Centred horizontally.** Always.
- **Never cropped.** No limb may leave the frame at a hard edge. The crop is
  MEASURED per clip (`tools/avatar_crop.py`), never a constant — the fixed
  650x930 window sliced a forearm off every clip where he gestured wider, and
  the true extent runs 680-886 px.
- **Size changes are rare and eased.** One change entering graphic mode, one
  leaving. Never resize for a passing keyword.
- Three sizes exist: BIG (81% wide, for presenter-focused stretches), FULL (66%),
  SMALL (56%, when content is behind him).

## Layout

- Captions own the top ~20%. Nothing may overlap them.
- No visual may overlap the presenter's face or body.
- No two visual elements may overlap each other.
- Content sits in the primary visual area between captions and presenter.
- A diagram that is the SUBJECT gets the frame: presenter goes small and low,
  diagram gets the space. A small diagram under a large presenter is backwards —
  this shipped in the dry-cell video.

## Size and legibility

- Equations must be LARGE. A long equation splits at the arrow rather than
  shrinking to fit the width — reactants on one line, products on the next.
  Both the plain and the progressive formula paths must do this.
- Section headings match the body scale; a heading smaller than the text under
  it reads as a mistake.
- A diagram carrying labels must be scaled so the labels are readable, and the
  labels must sit ON their part, not floating beside the figure.

## Text rendering

- **Hindi and formulae render by different paths and cannot be mixed.** Poppins
  covers Devanagari and has no Greek, no sub/superscripts, no arrows; LaTeX has
  those and no Devanagari. `E°सेल` is not renderable — split it.
- **Maths inside a text block is written `$...$`** and every renderer must honour
  it. It was implemented for `compare` only, so a points list printed
  `$\Delta T_b = T_b - T_b^{0}$` on screen verbatim.
- No degree sign as a superscript zero: `E°` is a standard potential, `T_b^{0}`
  is an initial value. Preflight fails on the confusion.

## Screen that is dead

- **EMPTY** — nothing on the stage. Fill it by ENLARGING THE PRESENTER, never by
  inventing a picture.
- **FROZEN** — one block unchanged for 20s+ while the teacher keeps talking. Just
  as dead, and invisible to every check until `visual_gaps.py` learned to report
  it. The Daniell cell held one table for 59 of its 112 seconds.
- A revealed list item must STAY revealed. Set every item's state explicitly from
  its reveal time; conditional dimming is order-dependent and made item ① vanish
  outright when ② arrived.

## Images

- An image is placed ONLY where the narration dwells on that object as its own
  subject. Never to fill space. Gaps sit over the hook and the exam framing,
  which is the one place in a video where no object can earn a picture — placing
  by gap put a food photo over an MP Board hook and left ten named diseases
  unillustrated.
- Every image request answers: what information does it communicate, why an image
  rather than a diagram, what must be shown, what must NOT be shown, and which
  exact sentence it supports. If any answer is missing, do not request it.

## Mechanism

- If a concept has a direction or an order, animate it — and get the direction
  right. A backwards animation teaches the reverse of the answer and is more
  convincing than a wrong caption, because the student watches it happen.
- Checked cases: Berkeley-Hartley — water moves INTO the solution, the capillary
  level FALLS. Dry cell — electrons LEAVE the zinc. Daniell — the salt bridge
  carries anions toward the ANODE.

## Derivations

- A derivation GROWS, one line per spoken step, earlier lines dimmed and the
  current one boxed. Sixteen separate screens loses the student.
- Every step must FOLLOW from the last. `k = x/t` shipped with `x` undefined, and
  the next beat substituted `[A]` into an equation that did not contain it.
- Pace around 10-15s per step. Under 5s is too fast to absorb: merge steps.

## The question card

- The question is printed into the sheet PNG and must not leak off the torn
  paper. It shrinks to a legibility floor, then TRUNCATES with an ellipsis.
- Years read as digits.

## The gates — a rule is a check that BLOCKS, not a constant in a file

Three defects came back after being fixed in source: the presenter floating, the
presenter off-centre, audio drifting against picture. Each was corrected, and
each returned, because nothing refused to hand over a broken file.

| Gate | Runs | Refuses |
|---|---|---|
| `tools/preflight_beats.py` | before any render | wrong beat shapes, maths mixed with Devanagari, Devanagari inside LaTeX, labels that would straddle a figure, missing figures/images, reveal counts, beats too close, meta missing `clip_end`/`card_lines` |
| `tools/layout_gate.py` | after render, before composite | any text-on-text overlap, out-of-band content |
| `tools/output_gate.py` | after composite, before delivery | presenter floating clear of the bottom, presenter off centre, head above 50% while graphics show, audio/video length mismatch, output not 30 fps |
| `tools/machine_ready.py` | before starting | swap or disk too low to render without freezing the machine |

If a defect can ship twice, the answer is a new row in this table — not a more
careful edit.
