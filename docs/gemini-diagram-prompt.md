# Prompt for Gemini — Berkeley–Hartley apparatus, animated

Paste everything below the line. Attach `projects/che-c1-la-01/answer/figure.png`
(the answer-sheet figure) as the reference image.

---

You are producing a single animated diagram for a Class 12 MP Board chemistry
revision reel, in Hindi, for students who have seen this exact figure in their
textbook. The diagram is the Berkeley–Hartley apparatus for measuring osmotic
pressure (परासरण दाब).

## Output I want

A self-contained **SVG animation** (SMIL or CSS keyframes inside the SVG, no
external JS), 1080 × 470 user units, `viewBox="0 0 1080 470"`, transparent
background. It must run for 116 seconds and follow the beat list below.

If SVG animation cannot express something, give me the static SVG plus a plain
list of which element id changes at which second — I will drive it myself.

## The apparatus — copy the attached figure's STRUCTURE exactly

A horizontal vessel drawn as a flattened hexagon: a long rectangular body with a
triangular point at each end, left and right. Inside it, running the full length,
an inner tube drawn as two horizontal lines. Then, and this is where diagrams of
this apparatus usually go wrong:

- the **capillary tube** rises from the **LEFT TRIANGULAR END** of the vessel —
  not from the top edge, not floating beside it. It is a narrow two-walled tube
  with a horizontal reference mark across it.
- the **piston** stands on the **TOP EDGE** in the middle: a cylinder open into
  the vessel, a piston head inside the cylinder, and a rod out of the top. It is
  a piston, not a plain rectangle.
- the **pressure gauge** is mounted on the **PISTON'S BODY** — a short stem from
  the side of the cylinder to a circular dial. It is not attached to the vessel.
- the **stopcock funnel** rises from the **RIGHT TRIANGULAR END** of the vessel,
  a stem with a cone on top.
- the **semipermeable membrane** (copper ferrocyanide) sits ON the inner tube's
  two walls, and is the only part drawn in a different colour.

Everything that is physically joined must be DRAWN joined. No part may float
next to the vessel.

## Colours

Strokes `#7FD4FF` (pale cyan). Membrane and anything being emphasised `#FFC53D`
(gold). Movement that means "wrong way / falling" `#FF5A5A` (red). Fills are
translucent tints of the stroke colour, never opaque. Dark background is assumed,
so nothing may be dark grey or black.

Strokes 8–10 units wide, circles radius ≥ 40. This is watched on a phone at
roughly 1/3 size; thin lines vanish.

## No text in the SVG

Do not put a single `<text>` element in the file. Labels are typeset separately
in Devanagari and composited over the top. Instead, for each labelled part give
me a **leader line**: a thin `#9FB6CC` line with a small filled dot at the end
that touches the part, plus the (x, y) where the label should be placed. Leaders
belong to these parts: capillary, mark, membrane, piston, gauge, funnel, water,
solution, inner tube, outer vessel.

## Layout constraints — these are hard

- Everything drawn must sit inside x 24–1056 and y 18–452. Nothing may touch a
  frame edge.
- No two parts may overlap. Space the top-mounted parts along the vessel.
- A label placed at the far end of a leader must not land on top of any other
  part or any other label.

## The animation — the physics must be right

The apparatus builds up as each part is named, then it is operated. In order:

1. vessel and inner tube appear
2. membrane appears on the inner tube (gold)
3. capillary and funnel appear
4. piston and gauge appear
5. water fills the inner tube; the capillary column rises to the mark
6. solution fills the outer vessel (a different tint from the water)
7. **osmosis**: three arrows rise from inside the inner tube, THROUGH the
   membrane, OUT into the solution — water leaves the water side
8. the capillary column **FALLS** below the mark (red)
9. the piston is pushed DOWN (red arrow on the rod)
10. the column **rises back to the mark** and stops exactly on it (gold)

Step 7 is the one to get right. Water moves OUT of the inner tube into the
solution, and because of that the level FALLS. Reversed, the animation teaches
the opposite of the answer and looks entirely convincing while doing it.

Step 10 must land the column exactly on the mark drawn in step 5, because the
whole method is "push until the level returns", and π = P_applied at that moment.

## What I do not want

No text, no title, no border or frame, no drop shadows, no gradient on a straight
line, no decorative particles, no 3D perspective, no photorealism. A clean
chalkboard-style schematic, nothing else.
