# LOCKED BLOCKS — verbatim copy-paste library

Ye blocks final tested versions hain (gauss-concept-COMPLETE pack se). **Copy verbatim, fill `{variables}` only.** Rewording = regression. Jahan variants hain, segment type se choose karo.

Contents: §1 Header/Voiceover/Audio · §2 Frame Layout (A/B/C/D) · §3 No-Diagram · §4 3D Render Quality · §5 Diagram Spec + object library · §6 Timing Sync · §7 Equation + Highlight · §8 Text Correctness · §9 Text Style · §10 Entry/Exit · §11 Script/Layout/Visual Style · §12 Background + Screen At Start · §13 Negatives · §14 Pack header house style

---

## §1 — Header, Voiceover, Audio (every segment)

```
VIDEO PROMPT — SEGMENT {X} OF {N}

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

VOICEOVER NARRATION (spoken audio): an energetic, warm Indian male physics teacher voice speaks this exact Hinglish narration during the clip — nothing more, nothing less. The same script also appears on screen word for word, one phrase at a time:
"{full segment script}"

AUDIO: only the voiceover above. No background music. Only very soft whoosh and pop sounds on text animations are allowed.
```

(Chemistry/Bio/Maths ho to "physics teacher" ko subject ke hisaab se badlo. Baaki line same.)

## §2 — FRAME LAYOUT (the 50% background rule)

Middle line kabhi number/percentage se describe nahi hoti — "invisible line" language hi use hoti hai (warna `12-30%`, `Band D` screen par print ho jata hai).

**Variant A — TEXT_ONLY segment:**
```
FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, filling the width, starting close to the top edge, large enough to fill the upper area comfortably. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.
```

**Variant B — DIAGRAM segment:** same as A, but replace sentence 2-3 with:
```
The script text sits at the very top of the frame, starting close to the top edge. The diagram sits directly below the script text and fills the space between the text and the invisible middle line, so the top half never looks empty. The lowest part of the diagram stops with a clear visible gap above the invisible middle line and never touches it; if it does not fit, make it smaller.
```

**Variant C — EQUATION_ONLY segment:** same as A, but replace sentence 2-3 with:
```
The script text sits at the very top of the frame, starting close to the top edge. The equation sits directly below the script text, comfortably above the invisible middle line, and is large enough that the top half does not look empty.
```

**Variant D — TRANSITION / DIAGRAM+EQUATION:** same as A, but:
```
The script text sits at the very top of the frame, starting close to the top edge. The diagram and then the equation sit directly below the script text, filling the space between the text and the invisible middle line. The lowest element stops with a clear visible gap above the invisible middle line and never touches it; if it does not fit, make it smaller.
```

## §3 — NO DIAGRAM block

**TEXT_ONLY version:**
```
NO DIAGRAM IN THIS CLIP (CRITICAL): this clip contains NO three dimensional object of any kind. There is no sphere, no ball, no charge, no arrow, no field line, no surface, no shape, no icon and no illustration anywhere in the frame at any moment. The only things on screen are the script text and the plain background. Do not invent, add or imagine any diagram, object or graphic. The space below the script text stays as plain empty background.
```

**EQUATION_ONLY version:** same but the "only things" sentence becomes:
```
The only things on screen are the script text, the equation, and the plain background. Do not invent, add or imagine any diagram, object or graphic.
```
(Topic ke hisaab se "no sphere, no ball..." list me us chapter ke objects ke naam daalo.)

## §4 — 3D RENDER QUALITY (DIAGRAM segments)

```
3D RENDER QUALITY (CRITICAL — THIS MAKES THE DIAGRAM LOOK THREE DIMENSIONAL):
The diagram is a real three dimensional object rendered in depth, not a flat drawing.
- CAMERA: a fixed three-quarter view from slightly above the object, so the viewer looks slightly down at it and can clearly read its roundness. Never a flat straight-on front view.
- PERSPECTIVE: circles that run around the object appear as flattened ellipses because of the viewing angle, becoming flatter near the top and bottom and rounder near the middle. Nothing is drawn as a plain flat circle.
- DEPTH: the parts nearest the camera are brighter, thicker and sharper. The parts on the far side, seen through the transparent surface, are noticeably dimmer, thinner and softer. This difference is clear and obvious.
- LIGHTING: one soft cool rim light along the upper left edge and a gentle ambient fill, giving a rounded sculpted look with a soft falloff toward the lower right.
- MATERIAL: a smooth glossy glass-like surface with a faint specular highlight near the upper left, and a soft inner glow.
- FORESHORTENING: any arrow pointing toward the camera looks shorter and thicker with a larger arrowhead, and any arrow pointing away looks longer and thinner. They are never all the same length on screen.
- MOTION: the object turns very slowly and steadily around its vertical axis so the depth reads clearly. It never wobbles, never squashes, never deforms and never changes size once settled.
```

**Short version (TRANSITION segments, diagram sirf pehle 3-4 sec):**
```
3D RENDER QUALITY (for the diagram in the first half of this clip):
The diagram is a real three dimensional object rendered in depth, not a flat drawing — a fixed three-quarter view from slightly above, circles appearing as flattened ellipses, near-side lines brighter and sharper than far-side lines, a soft cool rim light along the upper left edge, glossy glass-like material with a faint specular highlight, and a very slow steady turn around the vertical axis.
```

## §5 — DIAGRAM SPECIFICATION

Header line hamesha: `DIAGRAM SPECIFICATION (build exactly this, nothing else):`
Phir har object ek `- THE {NAME}:` bullet. Tested object library (naye topics ke liye inhi ka density-of-detail match karo — surface style, colours, motion, "never" clauses sab):

```
- THE GAUSSIAN SURFACE: one large transparent sphere rendered in full three dimensions, made of a thin cyan-blue grid of about eight vertical longitude lines and about five horizontal latitude lines drawn on its surface. Seen from the three-quarter camera angle, the latitude lines appear as flattened ellipses, flatter near the top and bottom and rounder near the middle. The grid lines on the near side are bright and crisp; the lines on the far side, seen through the glass, are clearly dimmer and thinner. The sphere is see-through. Its outer edge carries a soft cool rim light along the upper left. It turns very slowly and steadily. It never becomes solid or filled, never wobbles and never deforms.
- THE FLUX ARROWS: twelve straight arrows arranged in three dimensions all around the sphere, starting inside it and pointing outward in every direction including toward the camera and away from it, passing cleanly through the transparent surface. They are bright cyan with small neat conical arrowheads. Because of perspective the arrows toward the camera appear short and thick with large heads, the side ones appear at full length, and the ones going away appear thin and faint. They are evenly spaced with equal angles between them, never tangled, never crossing each other.
- THE ENCLOSED CHARGE: one small solid sphere in full three dimensions, deep red-orange with a bright glowing yellow-white core visible through its surface, like a glass marble lit from inside, with a soft round glow, a crisp specular highlight on its upper left and a gentle slow breathing pulse. It sits at the exact centre of the large transparent sphere and is clearly visible through it. It is NOT on fire, it never flickers, flares, burns, throws sparks or emits smoke.
- THE LABEL: exactly ONE label exists in this clip — a small white rounded plate with dark bold letters reading "{label text}", joined to the {object} by one short thin white leader line, drawn as a flat overlay in front of the three dimensional scene. It appears only at the time given in the timeline. No other plate, chip, tag, number or floating letter exists anywhere.
```

**Fade-out spec (TRANSITION segments):**
```
DIAGRAM SPECIFICATION: the scene from the previous clip — {carry-over description} — is present at the very first frame. It shrinks smoothly to about half its size, drifts upward, and fades away completely by 4.0 seconds, leaving the area below the script text free for the equation. LABELS: this clip has NO labels at all. Never invent a label.
```

**Fixed colour system (har pack me same):** point charge = glowing red-orange sphere + bright yellow core · Gaussian surface / field lines = translucent cyan-blue · active highlight = yellow · final result = green (green rounded box, formula turns bright green) · cancellation strike = red · labels = white rounded plate + dark bold letters + short thin white leader line.

## §6 — DIAGRAM TIMING SYNC

**Fresh objects:**
```
DIAGRAM TIMING SYNC (CRITICAL): every object appears at the exact moment its name is visible in the written phrase on screen, and never a frame before. Once an object appears it stays to the end of the clip.
```
**With carry-over:** second sentence becomes:
```
The diagram carried over from the previous clip is already present at the very first frame and does not fade in again.
```
**Equation entry (transition seg):**
```
DIAGRAM TIMING SYNC (CRITICAL): the equation appears at the exact moment the word naming the formula is visible in the written phrase on screen, and never before.
```

## §7 — EQUATION RULE + HIGHLIGHT RULE

**Equation already on screen (steps segments):**
```
EQUATION RULE (CRITICAL): there is only ONE equation in this clip and it is already on screen at the very first frame. It is flat two dimensional overlay text, not a three dimensional object. It never moves, never resizes, never duplicates and never leaves its place below the script text. It is ONE single clean horizontal line of large bold white mathematical text, perfectly sharp, with every symbol correct. Not on a card, not in a box, never stacked onto two lines.
```
**Equation appears mid-clip (intro segment):**
```
EQUATION RULE (CRITICAL): the equation is flat two dimensional overlay text, not a three dimensional object. It is ONE single clean horizontal line of large bold white mathematical text with a soft cyan glow, centred below the script text, perfectly sharp, with every symbol correct and correctly sized. It is not on a card, not in a box, and never stacked onto two lines. If it is too wide, reduce its size until the whole line fits comfortably inside the frame width with clear margins on both sides. It appears exactly once and holds to the end of the clip. The script text stays at the top and the equation stays below it — they never overlap and never swap places.
```
**Highlight (every equation segment jahan koi part emphasise hota hai):**
```
HIGHLIGHT RULE (CRITICAL — NO NEW TEXT IS EVER CREATED): when a part of the equation is emphasised, that part of the EXISTING equation simply changes colour and glows brighter in place. NEVER copy a symbol out of the equation. NEVER draw a second copy of any symbol anywhere. NEVER create a label, plate, chip, callout or floating letter for it. The equation itself is the only place any symbol ever appears.
```
Timeline me highlight aise likho: `At 1.5 s the letter E inside the existing equation turns bright yellow and glows, staying exactly in its place inside the equation, and holds that glow.` — aur agla highlight aane par pichla `returns to white`.

## §8 — TEXT CORRECTNESS RULES

```
TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE. Every word appears exactly the number of times it is written.
{EXACT COUNT lines — one per word/symbol that legitimately appears more than once in the clip, e.g.:}
- EXACT COUNT: the letter "E" appears exactly TWICE in total in this clip — once inside the first phrase and once inside the equation. Nowhere else, in any size, at any moment.
{If clip has no labels:}
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.
```
Script me deliberate repeat ho to usko bhi lock karo: `NEVER REPEAT A WORD INSIDE A PHRASE beyond what is written. In the second phrase the words "step by step" are written exactly as given — the word step appears exactly twice there and never a third time anywhere.`

## §9 — TEXT STYLE RULE (final evolved version — "same word twice" clause included)

```
TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated.
```

## §10 — TEXT ENTRY AND EXIT RULE

```
TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.
```
(Equation segments me "letters" ke saath "or mathematical symbols" add karo.)

## §11 — SCRIPT TEXT / STRICT LAYOUT / VISUAL STYLE

```
SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time, perfectly synced with the voiceover. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.
```
**VISUAL STYLE — diagram segments:**
```
VISUAL STYLE: clean, glossy, textbook-style physics illustration rendered in three dimensions — smooth shapes, flat bright colours, soft even glow, like a modern NCERT diagram built in 3D. Never photorealistic. NO fire, NO flame, NO burning, NO spark, NO ember, NO explosion, NO smoke.
```
**VISUAL STYLE — text/equation-only segments:**
```
VISUAL STYLE: clean crisp flat overlay typography on a dark technical background. Never photorealistic. NO fire, NO flame, NO sparks, NO smoke.
```

## §12 — BACKGROUND + SCREEN AT START

**BACKGROUND (final no-bokeh version — purani bokeh wali line stray `°` `©` marks banati thi):**
```
BACKGROUND (identical in every segment): one single continuous deep slate charcoal surface filling the whole frame from the very top edge to the very bottom edge, with a faint uniform blueprint grid of thin darker lines spread evenly across the entire frame. The background is completely flat and clean — no floating particles, no drifting dust, no bokeh dots, no specks, no sparkles, no light streaks, no glare, no lens flare. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.
```
**SCREEN AT START patterns:**
- Fresh: `SCREEN AT START: completely empty background. Nothing at all.`
- Carry-over: `SCREEN AT START: continuing exactly from the previous clip — {exact end-state description}. Nothing else.`
- Equation steps: `SCREEN AT START: the equation sits alone on one single line below where the text will appear, sharp and still, glowing softly cyan. Nothing else.`

## §13 — NEGATIVE lists

Ek hi lambi comma-separated line, `NEGATIVE (must never appear):` se shuru. Base = universal bans; upar se segment-specific time/count locks.

**Universal core (har segment):**
```
any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, invented labels, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change
```
**TEXT_ONLY add:** `any sphere, ball, charge, arrow, field line, surface, shape, icon or illustration of any kind, any label plate, equations`
**DIAGRAM add:** `a flat two dimensional circle instead of a three dimensional sphere, a straight-on front view with no depth, arrows all drawn the same length on screen, a diagram that looks like a flat line drawing, a solid or filled sphere, a squashed or wobbling sphere, tangled or crossing arrows, {object} appearing before {t} seconds, the label appearing before {t} seconds, a second label plate, a second "{label}", equations`
**EQUATION add:** `any sphere, ball, charge, arrow, field line, surface, shape, icon or illustration, a copy of any symbol taken out of the equation, a floating letter {X} anywhere outside the equation, any label plate, any chip, any callout, any leader line, two copies of the equation, the equation moving or resizing, the equation stacked onto two lines, a golden word in either phrase, wrong mathematical symbols, extra equations`

## §14 — Pack header house style (file ke top par)

```
# {Topic} — {N} SEGMENT PROMPT SET (FINAL)

**{N} × 10 sec = {total} seconds.** Har prompt fully self-contained — copy → paste → generate.

## Fix checklist (har prompt mein maujood)
{table: Fix | Kya solve karta hai — bug-ledger se relevant rows}

## Segment map
{table: Seg | Content | Diagram ✅/❌}

**Tool setting:** 1080×1920 select karna.
```

## MANDATORY ON-SCREEN TEXT pattern (§ har segment ke end me, NEGATIVE se pehle)

```
MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "{phrase 1}"
2. "{phrase 2}"
3. "{label / equation}"
```
Har cheez jo screen par likhi aayegi — phrases, labels, equation — is list me honi chahiye. Kuch bhi jo list me nahi = screen par nahi.

---

## §15 — BACKGROUND when the background is UPLOADED (new default)

Ab hum Gemini ko background image khud upload karte hain (Arivihan branded slate
+ grid + logo). Isliye background ko **describe karna band** — describe karoge to
model apna naya background bana dega aur uploaded wala discard ho jayega, ya
dono blend ho kar seam aa jayega.

**BACKGROUND (uploaded-background version — use this whenever a background image is attached):**
```
BACKGROUND (identical in every segment): the supplied background image is the
background for the entire clip, used exactly as provided, completely unchanged
from the very first frame to the very last. Its colour, texture, grid, lighting
and every mark already on it stay exactly as they are — nothing on the
background is redrawn, recoloured, brightened, darkened, blurred, replaced,
extended, cropped, shifted, scaled or animated at any moment. No new background
is generated. All animated elements sit ON TOP of this unchanged background.
The background looks exactly the same in the upper half and the lower half — no
split, no seam, no dividing line, no separate panels, no colour change, no
vignette and no band across the middle. Camera fully locked and static.
```

**§13 NEGATIVE me ye additions zaroori hain (uploaded background ke saath):**
```
a regenerated background, a redrawn background, a replaced background, a second
background layer, the background being recoloured, the background being blurred,
the background grid changing, the background sliding or drifting, a border or
frame added around the background, the supplied background being cropped or zoomed
```

## §16 — REMOVED (do not reinstate)

Yahan pehle "LOGO SAFE AREA" block tha jo model ko kehta tha ki logo mat banao
aur top corners khaali rakho. **Usi ne dono top corners me random logos bana
diye.** Prompt ke positive section me "logo" shabd likhna hi kaafi hai — model
usko draw kar deta hai, chahe sentence mana kar raha ho.

**Rule: prompt me logo/watermark/badge/wordmark kabhi mat likho — kisi bhi form
me, mana karne ke liye bhi nahi.** Logo ka kaam editing me hota hai, generation
me nahi. Base NEGATIVE list me jo `watermark` pehle se hai wo rehne do (wo tested
hai); uske alawa kuch mat jodo.

Gemini apna mark bottom-right me, bottom edge se thoda upar lagata hai. Wo editing
me patch ho jata hai, aur us jagah koi kaam ki cheez hoti nahi — isliye prompt me
uske liye koi safe-area, koi instruction, kuch bhi nahi chahiye.

## §17 — SILENT CLIP (replaces §1's VOICEOVER + AUDIO blocks)

Ab audio HeyGen avatar se aata hai — avatar hi poori baat bolta hai. Veo ka
apna voiceover generate karna do problem deta hai: (a) do awaazein overlap hoti
hain, (b) jahan voiceover hota hai wahan tool apne aap burnt-in captions bhi
laga deta hai.

Isliye VOICEOVER NARRATION aur AUDIO blocks **hata do**, aur ye lagao:

```
AUDIO: this clip is completely SILENT. There is no voiceover, no narration, no
speech, no singing, no music, no sound effects and no ambient sound of any kind.
No voice is generated at any moment. The audio track is empty. The spoken
narration is added separately in editing from a different source.
```

**NEGATIVE additions (zaroori):**
```
any voiceover, any narration, any spoken words, any human voice, any singing,
background music, sound effects, an automatic caption, an auto-generated
subtitle, a burnt-in subtitle bar, closed captions, a transcript line, any text
that appears because speech was generated
```

> Script text on screen (kinetic typography) alag cheez hai — wo SCRIPT TEXT ON
> SCREEN block se aati hai aur design ka hissa hai. Sirf tool ki apni auto-caption
> band karni hai.

## §18 — TOP-HALF ENFORCEMENT (jab diagram 50% se neeche aa jaye)

§2 ki language kaafi nahi padi — diagram invisible line cross kar gaya. Ye
reinforcement block §2 ke turant baad, har DIAGRAM segment me:

```
SIZE AND POSITION CHECK (CRITICAL): before anything is drawn, the diagram is
scaled so that its complete height — including every label, arrow, glow, shadow
and the magnified inset — fits inside the upper half of the frame with a clear
visible margin still left below it. If any part of the diagram would reach the
middle of the frame, the whole diagram is made smaller until it does not. The
diagram never grows, drifts downward, expands or scales up at any moment during
the clip. The lower half of the frame contains nothing but the background from
the first frame to the last.
```

**NEGATIVE additions:**
```
the diagram crossing the middle of the frame, the diagram touching the middle of
the frame, the diagram growing or expanding during the clip, the diagram drifting
downward, a label or arrow reaching into the lower half, an inset circle in the
lower half, the illustration filling the whole frame, a full-frame poster layout
```

## §19 — SAME-ELEMENT CHANGE RULE

Bug: 6th bead par ring sahi aayi, par colour kisi DOOSRE bead ka badla. Model
"highlight" aur "change" ko do alag elements par apply kar deta hai.

Jab bhi ek hi element pe do cheezein honi hain (ring + colour, glow + move),
explicitly bandho:

```
SAME ELEMENT RULE (CRITICAL): the element that is highlighted and the element
that changes are THE SAME SINGLE element — not a neighbour, not a different one,
not an additional one. Counting from the {left/right}-hand end, it is element
number {N}, and it is the only element in the whole clip that changes in any way.
Every other element keeps its original colour, size and position from the first
frame to the last, without exception. The change happens in place, on the element
that already carries the highlight, while the highlight is still visible on it.
```

**NEGATIVE additions (numbers ko literal likho):**
```
a different element changing colour, the element before or after number {N}
changing, element number {N-1} changing, element number {N+1} changing, two
elements changing, the highlight on one element and the colour change on another,
the change moving to a neighbouring element, the highlighted element and the
changed element being different
```
