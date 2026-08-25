# Gemini prompt — dry cell, HOW THE CELL WORKS (38 seconds)

This clip replaces one section of a finished video, so the layout is not
negotiable: it has to drop into the same frame as everything around it.

Attach `projects/che-c2-la-05/answer/figure.png` (the textbook dry-cell figure)
as the reference image.

---

Produce a **38-second animation**, **1080 × 1920 portrait, 30 fps, no audio, no
text of any kind**, that shows how a dry cell works.

## Layout — hard, because this clip is spliced into an existing video

The 1920-tall frame is divided and I cannot change it:

| band | y range | what goes there |
|---|---|---|
| captions | 64 – 304 | **LEAVE EMPTY.** Subtitles are burned in later. |
| stage | 380 – 850 | **All drawing goes here, and only here.** |
| gap | 850 – 960 | empty |
| presenter | 960 – 1920 | **LEAVE COMPLETELY EMPTY.** A person is composited here. |

Nothing may be drawn below y = 850. Not a stray line, not a glow, not a shadow,
not a watermark. If any mark appears in the lower half the clip is unusable,
because a presenter stands there.

Background: **transparent**, or flat `#0A1628` if transparency is impossible. Do
not invent a background — the real one is behind this clip and must show through.

## What the animation must show

The cell is the one in the attached figure: a tall cylindrical cell, zinc
container as the outer wall, a carbon rod down the centre, MnO₂ + carbon powder
packed around the rod, NH₄Cl + ZnCl₂ paste between that and the zinc wall, a
pitch seal and a metal cap on top.

Draw it in **cross-section, from the side**, so the inside is visible. Keep the
same proportions as the figure: tall, with the rod on the centre line.

The sequence, over 38 seconds:

1. **(0–4s)** the cell sits complete and still.
2. **(4–14s)** **zinc dissolving.** On the inner face of the zinc wall, atoms
   leave the metal and move into the paste as **Zn²⁺** ions — small positive
   particles drifting away from the wall into the electrolyte. The zinc wall is
   being consumed. Mark it **(−)**.
3. **(14–24s)** **electrons leaving.** Each departing Zn²⁺ leaves two electrons
   behind IN the zinc wall. Show them collecting in the metal, then flowing UP
   the zinc wall, OUT through a wire over the top of the cell, and DOWN into the
   metal cap and carbon rod. A continuous, unmistakable one-way stream.
4. **(24–32s)** electrons arriving at the rod; mark the rod **(+)**.
5. **(32–38s)** the whole loop runs once more, slowly, end to end.

## The direction is the entire point

Electrons leave the **ZINC** and travel through the external wire to the
**CARBON ROD**. Zinc dissolves; the rod does not. Zinc is the negative
electrode, the rod is positive. Reversed, this teaches the exact opposite of the
correct answer, and it will look completely convincing while doing it. If you
are unsure, do not guess — leave that element out.

Zn²⁺ ions move INTO the paste, away from the zinc wall. They never travel up
the wire; only electrons do.

## Style

Clean chalkboard schematic on a dark ground. Line art, not photorealism, not 3D.

- structure lines: pale cyan `#7FD4FF`, 8–10 px
- electrons: green `#7BE3A0`, clearly round, large enough to follow on a phone
- Zn²⁺ ions: red `#FF5A5A`
- the part being acted on: gold `#FFC53D`

Motion should be steady and readable, not fast or flashy. A student must be able
to follow one electron with their eye.

## Not wanted

No text, no labels, no numbers, no chemical formulae — Devanagari labels are
typeset separately and composited on top; anything you write will collide with
them. No title card, no border, no frame, no vignette, no lens flare, no
particles, no camera moves, no zooms, no 3D perspective, no photorealistic
metal, no logo or watermark.

## Checks before you return it

- Is every drawn pixel between y = 380 and y = 850?
- Is the lower half of the frame completely empty?
- Do electrons go from the zinc, through the wire, to the rod — and never the
  other way?
- Do Zn²⁺ ions go into the paste, never up the wire?
- Is there any text anywhere in the frame? There must not be.
