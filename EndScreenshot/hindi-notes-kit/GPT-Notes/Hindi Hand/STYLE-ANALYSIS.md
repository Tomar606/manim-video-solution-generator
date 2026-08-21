# The Hindi hand — what makes it look like that

Analysis of `hand-anchor-full.jpg` (the real page: "पंशागति का आणविक आधार"). These are the traits
encoded in `prompt-hindi.md`; if a render looks wrong, check it against this list first.

## Page furniture
* Plain white sheet, **no body ruling at all**.
* **Double vertical rule** down the left edge; **double horizontal rule** across the top making a
  narrow header band. The chapter title sits *inside that band*, roughly centred.
* No right-hand margin — the writer runs text out to the edge of the sheet.
* Reproduced synthetically by `make_paper.py` → `paper-hindi.png`.

## The pen
* ONE ink for everything: muted, greyed dark **ballpoint blue** — title, headings, body, bullets,
  boxes and arrows alike. No black, no red, no highlighter anywhere.
* Darkness varies stroke to stroke; occasional dry-pen skips, small pools where the pen paused,
  and visibly **retraced** (doubled) strokes — especially on box edges.

## The shirorekha (head-line) — the signature trait
* Never one long level printed bar. Drawn in **short segments**, often two or three per word.
* Each segment **slants** — mostly up to the right — and neighbouring segments disagree on angle.
* Segments **break** mid-word and **overshoot** past the last letter, leaving a small tail.
* Segments sit at slightly different heights, so letters hang from a crooked wire.

## Nothing is on a baseline
* Letters inside one word differ ~15–25% in height and ride high/low against each other.
* Whole words step up and down within a row — reading across, the line visibly waves.
* Each row follows its own crooked, slightly sloping path, at a different angle from the row above.
* Row-to-row vertical spacing is uneven too.

## Matras
* The ि hook varies a lot in height and curl; sometimes towering, sometimes a stub.
* ी े ै ो ौ are quick slanted ticks of varying length/angle, sometimes detached from the head-line.
* ं / ँ dots land at varying heights, occasionally off-centre.
* Conjuncts (क्ष, त्र, न्यू, क्लि, स्त) are compressed and fast but still identifiable.

## Spacing and line ends
* Word gaps vary wildly on the same row — some words nearly collide, others sit far apart.
* Line ends are **crowded**: the last word or two is squeezed narrower to fit, and the odd letter
  or danda spills past where the previous rows ended. Right edge badly ragged, never justified.
* Row starts wander a few millimetres left/right of the margin rule.

## Two sub-hands on one page
* **Devanagari**: broadly upright with a slight forward lean; the lean is inconsistent letter to letter.
* **Latin/English** (mostly inside brackets — "(Genetic Material)", "(Replication)", "(E. coli)"):
  noticeably **smaller**, **joined rounded cursive**, clearly right-leaning, often cramped so a
  two-word term nearly runs together. A visibly different texture from the Devanagari around it.
* Digits are small Latin numerals; superscripts (10⁶, 10⁹) are drawn small and clearly raised.

## Line-work
* Boxes are freehand quadrilaterals: straight-feeling sides that are not parallel, so each box leans;
  sharp corners that **overshoot**; some edges retraced and doubled. No fill, no shading.
* Arrows have straight-but-slanted shafts and small uneven V heads.
* Text inside a box may nearly touch or slightly cross the right border.

## Known render gap (as of 2026-08-12)
gpt-image-2 pulls hard toward a tidy, font-like Devanagari. Two levers that measurably helped:
1. Feeding the anchor as a **native-resolution crop** (`hand-anchor.jpg`, ~958×662) instead of the
   full page — cost_guard downscales any input to 1024px long edge, which was destroying the
   stroke detail on the full-page version. Full page kept as `hand-anchor-full.jpg`.
2. The explicit **"five failure tests"** block at the top of the prompt.

Output is still tidier than the reference (head-lines too continuous, rows too level). The next
untried lever is quality — cost_guard clamps every call to `medium`; a single `COST_GUARD_DISABLE=1`
run at `high` would show whether the remaining gap is a quality ceiling or a prompt gap.
