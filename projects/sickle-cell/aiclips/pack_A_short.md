# सिकल सेल एनीमिया — SEGMENT PROMPT SET

## 1. Total segment count

**21 segments × 10 sec = 210 sec (3:30)**

Script = 341 words. At safe Hindi teacher pace (~16–24 words / 10 s) and the ≤9-words-per-phrase / max-3-phrases rule, 21 is the lowest count this script fits into without over-loading a clip. Flagging honestly: the proven-clean benchmark is 13 segments — **21 is at the top of the risk band** (ledger #16, style drift). If you can cut ~50 words (CLIP 6 is the fattest at 67 words, CLIP 8 at 26), we land at 18 and quality goes up. Say the word and I'll propose the trim.

### Script-pass changes (punctuation only — no wording touched)
| Where | Change | Why |
|---|---|---|
| CLIP 6 "…वाहक होता है **—** लक्षण…" | `—` → `।`, new phrase starts at "लक्षण" | trailing em dash renders as a stray mark on screen |
| CLIP 7 "याद रखो **—** एक क्षार…" | `—` dropped, phrase break instead | same |
| CLIP 8 "**4** नंबर" | → "**चार** नंबर" | digit in narration = Veo reads it in English; also keeps on-screen text all-Devanagari. **Confirm this one.** |

Sentences are split across segments only at commas (natural pauses) — never mid-clause.

---

## 2. Segment map

| Seg | Phrases (exact words) | Type | Diagram |
|---|---|---|---|
| 1 | 1. हमारे रक्त में लाल रक्त कोशिकाएँ पाई जाती हैं।<br>2. इनका आकार द्विअवतल चक्रिका के समान होता है,<br>3. अर्थात् बीच से कुछ दबी हुई। | DIAGRAM | Y |
| 2 | 1. ये कोमल और लचीली होती हैं,<br>2. इसलिए बहुत पतली रक्त वाहिकाओं से भी<br>3. आसानी से गुजर सकती हैं। | DIAGRAM | Y |
| 3 | 1. इनमें हीमोग्लोबिन नामक प्रोटीन पाया जाता है,<br>2. जो शरीर के विभिन्न भागों तक ऑक्सीजन पहुँचाता है। | DIAGRAM (tube fades 0–2 s) | Y |
| 4 | 1. हीमोग्लोबिन की बीटा-ग्लोबिन श्रृंखला का निर्माण<br>2. एचबीबी जीन द्वारा नियंत्रित होता है। | DIAGRAM | Y |
| 5 | 1. सिकल सेल एनीमिया में<br>2. इस जीन के डीएनए क्रम में<br>3. GAG के स्थान पर GTG हो जाता है। | TRANSITION (diagram → equation) | N (fades by 4.0 s) |
| 6 | 1. इस एक क्षार के परिवर्तन के कारण<br>2. बीटा-ग्लोबिन श्रृंखला की छठी स्थिति पर<br>3. ग्लूटामिक अम्ल के स्थान पर वेलिन आ जाता है। | EQUATION_ONLY (prev line fades 0–1.5 s) | N |
| 7 | 1. इस प्रकार सामान्य हीमोग्लोबिन HbA के स्थान पर<br>2. HbS बनने लगता है। | EQUATION_ONLY (prev line fades 0–1.5 s) | N |
| 8 | 1. समस्या तब उत्पन्न होती है जब<br>2. शरीर में ऑक्सीजन की मात्रा कम हो जाती है। | TEXT_ONLY (prev line fades 0–1.5 s) | N |
| 9 | 1. ऐसी स्थिति में HbS के अणु<br>2. आपस में जुड़कर लंबी रेशेदार संरचनाएँ बना लेते हैं, | DIAGRAM (fresh, empty start) | Y |
| 10 | 1. और लाल रक्त कोशिका का द्विअवतल आकार<br>2. बदलकर हँसिए के आकार का हो जाता है।<br>3. इसी कारण इसे सिकल सेल एनीमिया कहा जाता है। | DIAGRAM (shape morph) | Y |
| 11 | 1. ये कोशिकाएँ कठोर और कम लचीली हो जाती हैं,<br>2. इसलिए छोटी रक्त वाहिकाओं में फँस सकती हैं, | DIAGRAM | Y |
| 12 | 1. जिससे रक्त प्रवाह बाधित हो जाता है<br>2. और ऊतकों तक पर्याप्त ऑक्सीजन नहीं पहुँच पाती। | DIAGRAM (same scene, no new objects) | Y |
| 13 | 1. साथ ही ये जल्दी टूटने लगती हैं,<br>2. इसी कारण रक्ताल्पता उत्पन्न होती है। | DIAGRAM (vessel fades 0–2 s) | Y |
| 14 | 1. सिकल सेल एनीमिया एक अप्रभावी अलिंगी गुणसूत्रीय रोग है।<br>2. यदि बच्चे को दोनों माता-पिता से<br>3. सिकल सेल वाला जीन मिलता है, | TRANSITION (diagram fades → text) | N (fades by 3.5 s) |
| 15 | 1. तो जीन प्रारूप HbS HbS होता है<br>2. और उसे रोग हो सकता है। | EQUATION_ONLY | N |
| 16 | 1. केवल एक से मिलने पर<br>2. जीन प्रारूप HbA HbS होता है<br>3. और व्यक्ति सामान्यतः वाहक होता है। | EQUATION_ONLY (prev line fades 0–1.5 s) | N |
| 17 | 1. लक्षण आवश्यक रूप से नहीं होते,<br>2. लेकिन वह यह जीन<br>3. अगली पीढ़ी में पहुँचा सकता है। | TEXT_ONLY (prev line fades 0–1.5 s) | N |
| 18 | 1. तो बस इतना याद रखो<br>2. एक क्षार बदला, एक अमीनो अम्ल बदला, | TEXT_ONLY | N |
| 19 | 1. और लाल रक्त कोशिका का आकार बदल गया।<br>2. यही सिकल सेल एनीमिया का कारण बनता है। | DIAGRAM (simple before/after) | Y |
| 20 | 1. बस इतना समझ लिया,<br>2. तो परीक्षा में चार नंबर पक्के।<br>3. इसे परीक्षा में कैसे लिखना है, | TEXT_ONLY (cells fade 0–2 s) | N |
| 21 | 1. इसका उत्तर आपकी स्क्रीन पर आएगा।<br>2. स्क्रीनशॉट लेना मत भूलना। | TEXT_ONLY | N |

**Equation-solo respected:** every segment carrying a code/genotype/amino-acid line (5, 6, 7, 15, 16) has zero diagram on screen.

---

## 3. Continuity chain (end-state of each segment)

In every case the last phrase clears by 10.0 s, so the next clip opens text-free; only the objects listed carry over.

- **Seg 1 ends with:** one normal RBC — 3D biconcave red disc, dimple on both faces, no hole, slowly turning. Nothing else.
- **Seg 2 ends with:** the same RBC + a thin translucent capillary tube it has bent through.
- **Seg 3 ends with:** the RBC (tube gone, faded 0–2 s) with a glowing haemoglobin molecule inside it and a few cyan oxygen dots.
- **Seg 4 ends with:** the enlarged haemoglobin molecule as **4 chains (2 α + 2 β)** with one β chain lit, plus the एचबीबी gene strip. RBC gone. No labels.
- **Seg 5 ends with:** one single line — `GAG → GTG`. Diagram fully gone by 4.0 s. Nothing else.
- **Seg 6 ends with:** one single line — `ग्लूटामिक अम्ल → वेलिन`. Nothing else.
- **Seg 7 ends with:** one single line — `HbA → HbS`. Nothing else.
- **Seg 8 ends with:** completely empty background (equation gone by 1.5 s).
- **Seg 9 ends with:** one RBC, still biconcave, with long stiff HbS fibre rods bundled inside it.
- **Seg 10 ends with:** one sickle cell — red crescent with pointed ends, fibres inside. Normal shape gone.
- **Seg 11 ends with:** a narrow capillary tube with two sickle cells wedged in it and normal RBCs queued behind.
- **Seg 12 ends with:** the same scene, unchanged — stalled RBCs behind the block, dimmed tissue beyond. No new objects.
- **Seg 13 ends with:** one sickle cell alone, broken into fragments (capillary scene faded 0–2 s).
- **Seg 14 ends with:** completely empty background (fragments gone by 3.5 s).
- **Seg 15 ends with:** one single line — `HbS HbS`. Nothing else.
- **Seg 16 ends with:** one single line — `HbA HbS`. Nothing else.
- **Seg 17 ends with:** completely empty background.
- **Seg 18 ends with:** completely empty background.
- **Seg 19 ends with:** two small cells side by side — normal biconcave RBC (left) and sickle cell (right), both red.
- **Seg 20 ends with:** completely empty background (cells gone by 2.0 s).
- **Seg 21 ends with:** completely empty background (answer card is added in edit).

---

## Duplicate scan + style decisions (feeds Step 3)

| Seg | Style | EXACT COUNT locks needed |
|---|---|---|
| 1 | P1 **UNIFORM** (रक्त twice) | रक्त = 2× total |
| 5 | P3 **UNIFORM** (Latin caps) | GAG = 2× (phrase + line), GTG = 2× |
| 6 | P3 UNIFORM | ग्लूटामिक = 2×, वेलिन = 2× |
| 7 | both UNIFORM (HbA/HbS) | HbA = 2×, HbS = 2× |
| 9 | P1 UNIFORM (HbS) | HbS = 1× |
| 10 | UNIFORM | आकार = 2× (P1 + P2) |
| 14 | UNIFORM | सिकल = 2×, सेल = 2× (P1 + P3) |
| 15 | **UNIFORM — highest risk** | HbS = 3× total (twice in phrase, once in line) — must be stated explicitly |
| 16 | UNIFORM | HbA = 2×, HbS = 2× |
| 18 | P2 **UNIFORM** (एक ×2, बदला ×2) | एक = 2×, बदला = 2× |
| 19–21 | one golden word allowed | परीक्षा = 2× (Seg 20) |

All other segments get exactly one golden keyword — single clean Devanagari word, no hyphen (so **never** बीटा-ग्लोबिन or माता-पिता).

**Hindi-specific note:** auxiliaries (है, में, के, जाता, होता) repeat constantly. Count-locks go on **content words and Latin/code strings only** — locking auxiliaries would produce 8 count lines per clip and dilute the rule.

**Science pins already locked for Step 3:** RBC red + biconcave + **no nucleus** + no hole; haemoglobin = 2 α + 2 β; mutation at **β-chain position 6**; order is low oxygen → HbS polymerises → *then* shape changes; sickle = pointed-end crescent, still red; autosomal recessive.

Next: say go and I'll write Step 3 (full prompts). Recommend generating **Segment 1 alone first**, checking it, then the rest.


Frames read — they confirm the visual language I'll pin into the specs: **red biconcave disc with a shallow dimple (no hole, no nucleus)**, **blue spherical Hb molecules**, **blue rod-fibres**, and the crescent with **pointed ends**. Segments 1–4 below encode that.

---

## SEGMENT 1 OF 21

```
VIDEO PROMPT — SEGMENT 1 OF 21

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

VOICEOVER NARRATION (spoken audio): an energetic, warm Indian male biology teacher voice speaks this exact Hinglish narration during the clip — nothing more, nothing less. The same script also appears on screen word for word, one phrase at a time:
"हमारे रक्त में लाल रक्त कोशिकाएँ पाई जाती हैं। इनका आकार द्विअवतल चक्रिका के समान होता है, अर्थात् बीच से कुछ दबी हुई।"

AUDIO: only the voiceover above. No background music. Only very soft whoosh and pop sounds on text animations are allowed.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, starting close to the top edge. The diagram sits directly below the script text and fills the space between the text and the invisible middle line, so the top half never looks empty. The lowest part of the diagram stops with a clear visible gap above the invisible middle line and never touches it; if it does not fit, make it smaller. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

LOGO SAFE AREA: keep the top-left corner and the top-right corner of the frame completely clear of script text, diagram, equation, labels and any moving element for the whole clip — only the background itself shows there. Do not draw, copy, move, recreate or animate any logo, wordmark, badge or watermark anywhere in the frame; the logo already present on the supplied background must stay exactly where it is, unchanged.

3D RENDER QUALITY (CRITICAL — THIS MAKES THE DIAGRAM LOOK THREE DIMENSIONAL):
The diagram is a real three dimensional object rendered in depth, not a flat drawing.
- CAMERA: a fixed three-quarter view from slightly above the object, so the viewer looks slightly down at it and can clearly read its roundness. Never a flat straight-on front view.
- PERSPECTIVE: circles that run around the object appear as flattened ellipses because of the viewing angle, becoming flatter near the top and bottom and rounder near the middle. Nothing is drawn as a plain flat circle.
- DEPTH: the parts nearest the camera are brighter, thicker and sharper. The parts on the far side are noticeably dimmer, softer and less detailed. This difference is clear and obvious.
- LIGHTING: one soft cool rim light along the upper left edge and a gentle ambient fill, giving a rounded sculpted look with a soft falloff toward the lower right.
- MATERIAL: a smooth glossy slightly wet-looking surface with a faint specular highlight near the upper left, and a soft inner glow.
- FORESHORTENING: any element pointing toward the camera looks shorter and thicker, and any element pointing away looks longer and thinner. They are never all the same length on screen.
- MOTION: the object turns very slowly and steadily around its vertical axis so the depth reads clearly. It never wobbles, never squashes, never deforms and never changes size once settled.

DIAGRAM SPECIFICATION (build exactly this, nothing else):
- THE RED BLOOD CELL: one single large three dimensional biconcave disc, glossy deep red all over, like a soft rounded doughnut whose hole has been completely filled in. Seen from the three-quarter camera angle it reads as a round disc with a thick raised rim and a shallow smooth dimple pressed into the centre of the face turned toward the camera; the far face carries an identical dimple, so the cell is dented on BOTH faces. The dimple is a gentle shallow depression only — it NEVER becomes a hole, an opening, a ring, a gap or a tunnel, and nothing is ever visible through the middle of the cell. The centre of the cell is simply a slightly paler, thinner red because the cell is thinner there; it is NEVER a dark blob, NEVER a circle of a different colour, and there is NO nucleus, NO organelle, NO inner sphere and NO dark core of any kind inside this cell. The whole cell is uniformly red with soft internal shading, a crisp specular highlight on its upper left rim, and a soft warm rim light. It turns very slowly and steadily around its vertical axis so that its rounded three dimensional thickness and both dimples read clearly. It never becomes flat, never becomes a ring, never wobbles and never deforms.
- LABELS: this clip has NO labels at all. No plate, no chip, no tag, no number, no arrow, no leader line and no floating letter exists anywhere in the frame. Never invent a label.

DIAGRAM TIMING SYNC (CRITICAL): every object appears at the exact moment its name is visible in the written phrase on screen, and never a frame before. Once an object appears it stays to the end of the clip.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE beyond what is written. Every word appears exactly the number of times it is written.
- EXACT COUNT: the word "रक्त" appears exactly TWICE in total in this clip — both times inside the first phrase, exactly where it is written. Nowhere else, in any size, at any moment.
- EXACT COUNT: the word "आकार" appears exactly ONCE in this clip, inside the second phrase. Nowhere else.
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, matra by matra, symbol by symbol, in correct Devanagari script.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. In this clip: the FIRST phrase is COMPLETELY UNIFORM bold white with NO golden word, because the word "रक्त" occurs twice in it. The SECOND phrase has exactly ONE golden word: "द्विअवतल". The THIRD phrase has exactly ONE golden word: "दबी". Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters or matras are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time, perfectly synced with the voiceover. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean, glossy, textbook-style biology illustration rendered in three dimensions — smooth shapes, flat bright colours, soft even glow, like a modern NCERT diagram built in 3D. Never photorealistic, never a microscope photograph. NO fire, NO flame, NO burning, NO spark, NO ember, NO explosion, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: completely empty background. Nothing at all.

ANIMATION TIMELINE:
- 0.0 s: the first phrase "हमारे रक्त में लाल रक्त कोशिकाएँ पाई जाती हैं।" pops in at the very top of the frame, fully sharp, completely uniform bold white. It holds until 3.3 s and then disappears completely.
- At 1.2 s, exactly as the words "लाल रक्त कोशिकाएँ" are visible on screen, the three dimensional biconcave red blood cell pops in below the script text and settles at its final size. From this moment it turns very slowly and steadily and stays on screen to the end of the clip.
- 3.5 s: the second phrase "इनका आकार द्विअवतल चक्रिका के समान होता है," pops in at the very top, with only the single word "द्विअवतल" in warm golden colour, styled in place inside the sentence. It holds until 6.6 s and then disappears completely.
- 6.8 s: the third phrase "अर्थात् बीच से कुछ दबी हुई।" pops in at the very top, with only the single word "दबी" in warm golden colour, styled in place inside the sentence. It holds to 10.0 s.
- From 6.8 s to 10.0 s the cell's slow turn brings the dimpled face gently toward the camera so the shallow central depression on the near face reads clearly, while the cell keeps exactly the same size and position.
- The clip ends at 10.0 s with the red blood cell alone on screen and no text.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "हमारे रक्त में लाल रक्त कोशिकाएँ पाई जाती हैं।"
2. "इनका आकार द्विअवतल चक्रिका के समान होता है,"
3. "अर्थात् बीच से कुछ दबी हुई।"
Nothing else is written anywhere on screen at any moment.

NEGATIVE (must never appear): a red blood cell with a visible nucleus, a dark blob or dark core inside the red blood cell, a ring or doughnut with an open hole in the middle, a hole, gap, opening or tunnel through the cell, a flat two dimensional circle instead of a three dimensional biconcave disc, a straight-on front view with no depth, a bowl or cup shape dented on only one face, a cell of any colour other than red, a blue or purple blood cell, a sickle or crescent shaped cell in this clip, more than one cell, any label plate, any chip, any tag, any arrow, any leader line, any callout, any floating letter or symbol, any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, the cell appearing before 1.2 seconds, two phrases visible at the same time, garbled letters or broken matras during a transition, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, more than one golden word in a phrase, a golden word in the first phrase, invented labels, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken Devanagari, detached matras, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, any English text, equations, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, a new logo, a duplicated logo, a redrawn logo, a moved logo, a watermark of any kind, text or diagram overlapping either top corner
```

---

## SEGMENT 2 OF 21

```
VIDEO PROMPT — SEGMENT 2 OF 21

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

VOICEOVER NARRATION (spoken audio): an energetic, warm Indian male biology teacher voice speaks this exact Hinglish narration during the clip — nothing more, nothing less. The same script also appears on screen word for word, one phrase at a time:
"ये कोमल और लचीली होती हैं, इसलिए बहुत पतली रक्त वाहिकाओं से भी आसानी से गुजर सकती हैं।"

AUDIO: only the voiceover above. No background music. Only very soft whoosh and pop sounds on text animations are allowed.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, starting close to the top edge. The diagram sits directly below the script text and fills the space between the text and the invisible middle line, so the top half never looks empty. The lowest part of the diagram stops with a clear visible gap above the invisible middle line and never touches it; if it does not fit, make it smaller. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

LOGO SAFE AREA: keep the top-left corner and the top-right corner of the frame completely clear of script text, diagram, equation, labels and any moving element for the whole clip — only the background itself shows there. Do not draw, copy, move, recreate or animate any logo, wordmark, badge or watermark anywhere in the frame; the logo already present on the supplied background must stay exactly where it is, unchanged.

3D RENDER QUALITY (CRITICAL — THIS MAKES THE DIAGRAM LOOK THREE DIMENSIONAL):
The diagram is a real three dimensional object rendered in depth, not a flat drawing.
- CAMERA: a fixed three-quarter view from slightly above the objects, so the viewer looks slightly down at them and can clearly read their roundness. Never a flat straight-on front view.
- PERSPECTIVE: circles that run around the objects appear as flattened ellipses because of the viewing angle, becoming flatter near the top and bottom and rounder near the middle. Nothing is drawn as a plain flat circle.
- DEPTH: the parts nearest the camera are brighter, thicker and sharper. The parts on the far side, seen through the transparent tube wall, are noticeably dimmer, thinner and softer. This difference is clear and obvious.
- LIGHTING: one soft cool rim light along the upper left edge and a gentle ambient fill, giving a rounded sculpted look with a soft falloff toward the lower right.
- MATERIAL: smooth glossy surfaces with a faint specular highlight near the upper left, and a soft inner glow; the tube is glass-like and see-through.
- FORESHORTENING: the end of the tube nearer the camera appears wider and the far end appears narrower. The tube is never drawn as a plain flat rectangle.
- MOTION: objects move only as described in the timeline. Nothing wobbles, nothing squashes randomly, nothing changes size once settled.

DIAGRAM SPECIFICATION (build exactly this, nothing else):
- THE RED BLOOD CELL: the same single three dimensional biconcave disc from the previous clip, glossy deep red all over, with a thick raised rim and a shallow smooth dimple on BOTH faces. The dimple is a gentle shallow depression only — it NEVER becomes a hole, an opening, a ring, a gap or a tunnel, and nothing is ever visible through the middle of the cell. The centre is only a slightly paler thinner red; there is NO nucleus, NO organelle, NO inner sphere and NO dark core of any kind inside this cell. It is already present at the very first frame and does not fade in again.
- THE CAPILLARY TUBE: one narrow horizontal three dimensional tube made of thin transparent pale grey glass-like material with faint soft walls, clearly NARROWER than the red blood cell is wide, running across the frame below the script text. Its near wall is bright and crisp and its far wall, seen through the glass, is clearly dimmer and thinner. It is see-through, never solid, never filled with colour, and it never carries any text, tick mark, number or scale.
- THE SQUEEZE: as the red blood cell enters the tube it bends and folds smoothly into a soft elongated parachute-like shape, staying the same glossy red and the same volume, then springs gently back toward its rounded biconcave form as it clears the far end. It never tears, never breaks into pieces, never becomes pointed at the ends and never turns into a crescent or sickle shape in this clip.
- LABELS: this clip has NO labels at all. No plate, no chip, no tag, no number, no arrow, no leader line and no floating letter exists anywhere in the frame. Never invent a label.

DIAGRAM TIMING SYNC (CRITICAL): every object appears at the exact moment its name is visible in the written phrase on screen, and never a frame before. Once an object appears it stays to the end of the clip. The diagram carried over from the previous clip is already present at the very first frame and does not fade in again.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE beyond what is written. Every word appears exactly the number of times it is written.
- EXACT COUNT: the word "रक्त" appears exactly ONCE in this clip, inside the second phrase. Nowhere else, in any size, at any moment.
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, matra by matra, symbol by symbol, in correct Devanagari script.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. In this clip: the FIRST phrase has exactly ONE golden word: "लचीली". The SECOND phrase has exactly ONE golden word: "पतली". The THIRD phrase has exactly ONE golden word: "आसानी". Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters or matras are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time, perfectly synced with the voiceover. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean, glossy, textbook-style biology illustration rendered in three dimensions — smooth shapes, flat bright colours, soft even glow, like a modern NCERT diagram built in 3D. Never photorealistic, never a microscope photograph. NO fire, NO flame, NO burning, NO spark, NO ember, NO explosion, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: continuing exactly from the previous clip — the single three dimensional biconcave red blood cell, dimpled on both faces, with no hole and no nucleus, sits below where the script text will appear, turning very slowly. Nothing else.

ANIMATION TIMELINE:
- 0.0 s: the first phrase "ये कोमल और लचीली होती हैं," pops in at the very top of the frame, fully sharp, with only the single word "लचीली" in warm golden colour, styled in place inside the sentence. It holds until 3.3 s and then disappears completely. The red blood cell is already on screen from the very first frame and does not fade in again.
- From 0.0 s to 3.3 s the red blood cell flexes very gently, softening and rounding again, showing that it is soft and elastic, while keeping the same size and position.
- 3.5 s: the second phrase "इसलिए बहुत पतली रक्त वाहिकाओं से भी" pops in at the very top, with only the single word "पतली" in warm golden colour. It holds until 6.6 s and then disappears completely.
- At 4.3 s, exactly as the words "पतली रक्त वाहिकाओं" are visible on screen, the narrow transparent capillary tube pops in behind the cell, running horizontally below the script text, and stays to the end of the clip. The red blood cell is clearly wider than the tube.
- 6.8 s: the third phrase "आसानी से गुजर सकती हैं।" pops in at the very top, with only the single word "आसानी" in warm golden colour. It holds to 10.0 s.
- From 6.8 s to 10.0 s the red blood cell moves smoothly into the tube, bending and folding into a soft elongated shape as it passes through the narrow section, and begins springing back toward its rounded form as it reaches the far end, coming to rest still inside the tube.
- The clip ends at 10.0 s with the red blood cell resting inside the transparent capillary tube and no text.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "ये कोमल और लचीली होती हैं,"
2. "इसलिए बहुत पतली रक्त वाहिकाओं से भी"
3. "आसानी से गुजर सकती हैं।"
Nothing else is written anywhere on screen at any moment.

NEGATIVE (must never appear): a red blood cell with a visible nucleus, a dark blob or dark core inside the red blood cell, a ring or doughnut with an open hole in the middle, a hole, gap, opening or tunnel through the cell, a flat two dimensional circle instead of a three dimensional biconcave disc, a straight-on front view with no depth, a cell of any colour other than red, a blue or purple blood cell, a sickle or crescent shaped cell, a cell with pointed ends, a cell tearing or breaking apart in this clip, more than one cell, a solid or opaque tube, a tube wider than the cell, a flat rectangle instead of a three dimensional tube, any tick mark, number or scale on the tube, any label plate, any chip, any tag, any arrow, any leader line, any callout, any floating letter or symbol, any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, the tube appearing before 4.3 seconds, the cell fading in again at the start, two phrases visible at the same time, garbled letters or broken matras during a transition, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, more than one golden word in a phrase, invented labels, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken Devanagari, detached matras, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, any English text, equations, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, a new logo, a duplicated logo, a redrawn logo, a moved logo, a watermark of any kind, text or diagram overlapping either top corner
```

---

## SEGMENT 3 OF 21

```
VIDEO PROMPT — SEGMENT 3 OF 21

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

VOICEOVER NARRATION (spoken audio): an energetic, warm Indian male biology teacher voice speaks this exact Hinglish narration during the clip — nothing more, nothing less. The same script also appears on screen word for word, one phrase at a time:
"इनमें हीमोग्लोबिन नामक प्रोटीन पाया जाता है, जो शरीर के विभिन्न भागों तक ऑक्सीजन पहुँचाता है।"

AUDIO: only the voiceover above. No background music. Only very soft whoosh and pop sounds on text animations are allowed.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, starting close to the top edge. The diagram sits directly below the script text and fills the space between the text and the invisible middle line, so the top half never looks empty. The lowest part of the diagram stops with a clear visible gap above the invisible middle line and never touches it; if it does not fit, make it smaller. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

LOGO SAFE AREA: keep the top-left corner and the top-right corner of the frame completely clear of script text, diagram, equation, labels and any moving element for the whole clip — only the background itself shows there. Do not draw, copy, move, recreate or animate any logo, wordmark, badge or watermark anywhere in the frame; the logo already present on the supplied background must stay exactly where it is, unchanged.

3D RENDER QUALITY (CRITICAL — THIS MAKES THE DIAGRAM LOOK THREE DIMENSIONAL):
The diagram is a real three dimensional object rendered in depth, not a flat drawing.
- CAMERA: a fixed three-quarter view from slightly above the object, so the viewer looks slightly down at it and can clearly read its roundness. Never a flat straight-on front view.
- PERSPECTIVE: circles that run around the object appear as flattened ellipses because of the viewing angle, becoming flatter near the top and bottom and rounder near the middle. Nothing is drawn as a plain flat circle.
- DEPTH: the parts nearest the camera are brighter, thicker and sharper. The parts on the far side, seen through the translucent cell, are noticeably dimmer, smaller and softer. This difference is clear and obvious.
- LIGHTING: one soft cool rim light along the upper left edge and a gentle ambient fill, giving a rounded sculpted look with a soft falloff toward the lower right.
- MATERIAL: smooth glossy surfaces with a faint specular highlight near the upper left, and a soft inner glow.
- FORESHORTENING: the small spheres nearer the camera appear larger and brighter, and those further inside the cell appear smaller and fainter. They are never all drawn at the same size.
- MOTION: the cell turns very slowly and steadily around its vertical axis so the depth reads clearly. It never wobbles, never squashes, never deforms and never changes size once settled.

DIAGRAM SPECIFICATION (build exactly this, nothing else):
- THE RED BLOOD CELL: the same single three dimensional biconcave disc from the previous clip, glossy deep red all over, with a thick raised rim and a shallow smooth dimple on BOTH faces. The dimple never becomes a hole, an opening, a ring, a gap or a tunnel, and nothing is ever visible through the middle of the cell. The centre is only a slightly paler thinner red; there is NO nucleus, NO organelle, NO inner sphere and NO dark core of any kind inside this cell. Its surface becomes very slightly translucent from 4.0 seconds onward so that what is inside it can be seen. It is already present at the very first frame and does not fade in again.
- THE CAPILLARY TUBE: the narrow transparent tube carried over from the previous clip. It is present at the very first frame, then fades away smoothly and completely by 2.0 seconds, leaving only the red blood cell, which stays exactly where it is and does not move or resize while the tube fades.
- THE HAEMOGLOBIN MOLECULES: about ten small three dimensional spheres of deep blue glossy material with a soft inner glow and a crisp specular highlight on the upper left, scattered evenly INSIDE the red blood cell and seen through its slightly translucent surface. Because of perspective the ones nearer the camera are larger and brighter and the ones deeper inside are smaller and fainter. They drift extremely gently in place. They never leave the cell, never form chains, never form rods or fibres, and never touch each other in this clip.
- THE OXYGEN DOTS: about six very small bright cyan glowing dots, clearly smaller than the blue haemoglobin spheres and a clearly different colour from them, drifting slowly outward from the cell into the space around it in gentle curved paths. They fade softly at the ends of their paths. They never form text, never form arrows, never form letters or numbers, and never enter the bottom half of the frame.
- LABELS: this clip has NO labels at all. No plate, no chip, no tag, no number, no arrow, no leader line and no floating letter exists anywhere in the frame. Never invent a label.

DIAGRAM TIMING SYNC (CRITICAL): every object appears at the exact moment its name is visible in the written phrase on screen, and never a frame before. Once an object appears it stays to the end of the clip. The diagram carried over from the previous clip is already present at the very first frame and does not fade in again.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE beyond what is written. Every word appears exactly the number of times it is written.
- EXACT COUNT: the word "हीमोग्लोबिन" appears exactly ONCE in this clip, inside the first phrase. Nowhere else, in any size, at any moment.
- EXACT COUNT: the word "ऑक्सीजन" appears exactly ONCE in this clip, inside the second phrase. Nowhere else, in any size, at any moment.
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, matra by matra, symbol by symbol, in correct Devanagari script.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. In this clip: the FIRST phrase has exactly ONE golden word: "हीमोग्लोबिन". The SECOND phrase has exactly ONE golden word: "ऑक्सीजन". Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters or matras are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time, perfectly synced with the voiceover. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean, glossy, textbook-style biology illustration rendered in three dimensions — smooth shapes, flat bright colours, soft even glow, like a modern NCERT diagram built in 3D. Never photorealistic, never a microscope photograph. NO fire, NO flame, NO burning, NO spark, NO ember, NO explosion, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: continuing exactly from the previous clip — the single three dimensional biconcave red blood cell resting inside the narrow transparent capillary tube, below where the script text will appear. Nothing else.

ANIMATION TIMELINE:
- 0.0 s: the first phrase "इनमें हीमोग्लोबिन नामक प्रोटीन पाया जाता है," pops in at the very top of the frame, fully sharp, with only the single word "हीमोग्लोबिन" in warm golden colour, styled in place inside the sentence. It holds until 4.8 s and then disappears completely.
- From 0.0 s to 2.0 s the transparent capillary tube fades away smoothly and completely. The red blood cell stays exactly where it is, keeps its size, does not fade and does not fade in again; it turns very slowly and steadily.
- At 1.4 s, exactly as the word "हीमोग्लोबिन" is visible on screen, the red blood cell's surface becomes slightly translucent and the ten small deep blue haemoglobin spheres pop in INSIDE it, scattered evenly, larger and brighter near the camera and smaller and fainter deeper inside. They stay inside the cell to the end of the clip.
- 5.0 s: the second phrase "जो शरीर के विभिन्न भागों तक ऑक्सीजन पहुँचाता है।" pops in at the very top, with only the single word "ऑक्सीजन" in warm golden colour. It holds to 10.0 s.
- At 6.0 s, exactly as the word "ऑक्सीजन" is visible on screen, the small bright cyan oxygen dots begin drifting outward from the cell in gentle curved paths, staying well inside the top half of the frame, and continue to the end of the clip.
- The clip ends at 10.0 s with the red blood cell holding the blue haemoglobin spheres inside it and a few cyan oxygen dots around it, and no text.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "इनमें हीमोग्लोबिन नामक प्रोटीन पाया जाता है,"
2. "जो शरीर के विभिन्न भागों तक ऑक्सीजन पहुँचाता है।"
Nothing else is written anywhere on screen at any moment.

NEGATIVE (must never appear): a red blood cell with a visible nucleus, a dark blob or dark core inside the red blood cell, the haemoglobin spheres clustering into one central blob that looks like a nucleus, a ring or doughnut with an open hole in the middle, a hole, gap, opening or tunnel through the cell, a flat two dimensional circle instead of a three dimensional biconcave disc, a straight-on front view with no depth, a cell of any colour other than red, a blue or purple blood cell, a sickle or crescent shaped cell, a cell with pointed ends, haemoglobin drawn as a single blob, haemoglobin spheres joined into chains, rods, fibres or strands in this clip, haemoglobin spheres leaving the cell, oxygen dots drawn the same colour or size as the haemoglobin spheres, oxygen dots forming letters, numbers, arrows or words, the tube still visible after 2 seconds, the cell fading in again at the start, any label plate, any chip, any tag, any arrow, any leader line, any callout, any floating letter or symbol, any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, the haemoglobin spheres appearing before 1.4 seconds, the oxygen dots appearing before 6.0 seconds, two phrases visible at the same time, garbled letters or broken matras during a transition, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, more than one golden word in a phrase, invented labels, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken Devanagari, detached matras, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, any English text, equations, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, a new logo, a duplicated logo, a redrawn logo, a moved logo, a watermark of any kind, text or diagram overlapping either top corner
```

---

## SEGMENT 4 OF 21

```
VIDEO PROMPT — SEGMENT 4 OF 21

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

VOICEOVER NARRATION (spoken audio): an energetic, warm Indian male biology teacher voice speaks this exact Hinglish narration during the clip — nothing more, nothing less. The same script also appears on screen word for word, one phrase at a time:
"हीमोग्लोबिन की बीटा-ग्लोबिन श्रृंखला का निर्माण एचबीबी जीन द्वारा नियंत्रित होता है।"

AUDIO: only the voiceover above. No background music. Only very soft whoosh and pop sounds on text animations are allowed.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, starting close to the top edge. The diagram sits directly below the script text and fills the space between the text and the invisible middle line, so the top half never looks empty. The lowest part of the diagram stops with a clear visible gap above the invisible middle line and never touches it; if it does not fit, make it smaller. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

LOGO SAFE AREA: keep the top-left corner and the top-right corner of the frame completely clear of script text, diagram, equation, labels and any moving element for the whole clip — only the background itself shows there. Do not draw, copy, move, recreate or animate any logo, wordmark, badge or watermark anywhere in the frame; the logo already present on the supplied background must stay exactly where it is, unchanged.

3D RENDER QUALITY (CRITICAL — THIS MAKES THE DIAGRAM LOOK THREE DIMENSIONAL):
The diagram is a real three dimensional object rendered in depth, not a flat drawing.
- CAMERA: a fixed three-quarter view from slightly above the object, so the viewer looks slightly down at it and can clearly read its roundness. Never a flat straight-on front view.
- PERSPECTIVE: curves that wind around the object appear as flattened ellipses because of the viewing angle, becoming flatter near the top and bottom and rounder near the middle. Nothing is drawn as a plain flat circle.
- DEPTH: the parts nearest the camera are brighter, thicker and sharper. The parts on the far side are noticeably dimmer, thinner and softer. This difference is clear and obvious.
- LIGHTING: one soft cool rim light along the upper left edge and a gentle ambient fill, giving a rounded sculpted look with a soft falloff toward the lower right.
- MATERIAL: smooth glossy surfaces with a faint specular highlight near the upper left, and a soft inner glow.
- FORESHORTENING: the subunits nearer the camera appear larger and the ones behind appear smaller and partly hidden. They are never all drawn at the same size in a flat row.
- MOTION: the molecule turns very slowly and steadily around its vertical axis so the depth reads clearly. It never wobbles, never squashes, never deforms and never changes size once settled.

DIAGRAM SPECIFICATION (build exactly this, nothing else):
- THE HAEMOGLOBIN MOLECULE: one single three dimensional molecule made of EXACTLY FOUR rounded glossy coiled subunits packed together into one compact cluster, arranged as TWO matching pairs. The two subunits of the first pair are deep blue and identical to each other. The two subunits of the second pair are teal-green and identical to each other. There are exactly four subunits in total — never three, never five, never six. Each subunit is a smoothly coiled ribbon-like blob with soft inner shading, a specular highlight on its upper left and a gentle glow. The pairs sit diagonally opposite each other so both colours are clearly visible from the three-quarter camera angle. The molecule turns very slowly and steadily. It never splits apart, never changes its number of subunits and never deforms.
- THE HIGHLIGHTED CHAIN: exactly ONE of the two teal-green subunits brightens to a warm glowing yellow-green and pulses very gently, staying in its place inside the cluster and keeping its size and shape. Only ONE subunit is ever highlighted. The two deep blue subunits NEVER change colour, never glow and are never highlighted at any moment.
- THE GENE STRIP: one short horizontal three dimensional strip like a small rounded bar of double-stranded DNA, made of two gently twisting cyan-blue rails joined by small evenly spaced cross-rungs, sitting below the molecule. Its near rail is bright and crisp and its far rail is dimmer and thinner. On the strip, in small dark bold Devanagari letters on a small white rounded plate joined to the strip by one short thin white leader line, the text "एचबीबी" is written exactly ONCE. No other plate, chip, tag, number, letter or symbol exists anywhere in the frame. The strip carries no base letters, no A, T, G or C, no numbers and no scale.
- The red blood cell, the oxygen dots and the capillary tube from the previous clip are NOT present in this clip at any moment.

DIAGRAM TIMING SYNC (CRITICAL): every object appears at the exact moment its name is visible in the written phrase on screen, and never a frame before. Once an object appears it stays to the end of the clip.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE beyond what is written. Every word appears exactly the number of times it is written.
- EXACT COUNT: the word "एचबीबी" appears exactly TWICE in total in this clip — once inside the second phrase and once on the single white plate attached to the gene strip. Nowhere else, in any size, at any moment.
- EXACT COUNT: the word "हीमोग्लोबिन" appears exactly ONCE in this clip, inside the first phrase. Nowhere else.
- EXACT COUNT: exactly ONE label plate exists in this clip. There is no second plate, no chip, no tag, no callout and no other leader line anywhere.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, matra by matra, symbol by symbol, in correct Devanagari script.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, a hyphenated word, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. In this clip BOTH phrases are rendered COMPLETELY UNIFORM in bold white with NO golden word at all — the first phrase because it contains the hyphenated word "बीटा-ग्लोबिन", and the second phrase because the word "एचबीबी" also appears on the plate in the diagram. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated beyond the hyphen already written inside "बीटा-ग्लोबिन", which is written exactly as given, on one line, never broken across two lines.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters or matras are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time, perfectly synced with the voiceover. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean, glossy, textbook-style biology illustration rendered in three dimensions — smooth shapes, flat bright colours, soft even glow, like a modern NCERT diagram built in 3D. Never photorealistic, never a microscope photograph. NO fire, NO flame, NO burning, NO spark, NO ember, NO explosion, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: continuing exactly from the previous clip — the single three dimensional biconcave red blood cell with the small deep blue haemoglobin spheres inside it and a few cyan oxygen dots around it, sitting below where the script text will appear. Nothing else.

ANIMATION TIMELINE:
- 0.0 s: the first phrase "हीमोग्लोबिन की बीटा-ग्लोबिन श्रृंखला का निर्माण" pops in at the very top of the frame, fully sharp, completely uniform bold white with no golden word. It holds until 4.8 s and then disappears completely.
- From 0.0 s to 1.5 s the cyan oxygen dots and the red blood cell shrink slightly and fade away completely, leaving the space below the script text clear. They never return.
- At 1.6 s, exactly as the word "हीमोग्लोबिन" is visible on screen, ONE of the deep blue haemoglobin spheres grows smoothly into the large three dimensional haemoglobin molecule made of exactly four coiled subunits — two deep blue and two teal-green, arranged as two matching pairs — which settles below the script text and turns very slowly. It stays to the end of the clip.
- At 3.4 s, exactly as the words "बीटा-ग्लोबिन श्रृंखला" are visible on screen, exactly ONE of the two teal-green subunits brightens to a warm glowing yellow-green and pulses very gently, staying exactly in its place inside the cluster. The two deep blue subunits stay unchanged.
- 5.0 s: the second phrase "एचबीबी जीन द्वारा नियंत्रित होता है।" pops in at the very top, completely uniform bold white with no golden word. It holds to 10.0 s.
- At 6.0 s, exactly as the word "एचबीबी" is visible on screen, the short cyan-blue double-stranded gene strip pops in below the haemoglobin molecule and stays to the end of the clip.
- At 7.6 s the single small white rounded plate reading "एचबीबी" pops in beside the gene strip, joined to it by one short thin white leader line, and holds to the end of the clip. One soft thin glowing line brightens briefly from the gene strip toward the highlighted teal-green subunit, showing that the gene controls that chain.
- The clip ends at 10.0 s with the four-subunit haemoglobin molecule, one teal-green subunit glowing, the gene strip and its single "एचबीबी" plate on screen, and no script text.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "हीमोग्लोबिन की बीटा-ग्लोबिन श्रृंखला का निर्माण"
2. "एचबीबी जीन द्वारा नियंत्रित होता है।"
3. "एचबीबी"   (on the single white plate attached to the gene strip)
Nothing else is written anywhere on screen at any moment.

NEGATIVE (must never appear): a haemoglobin molecule with three, five, six or any number of subunits other than exactly four, all four subunits drawn the same colour, the two pairs not matching each other, more than one subunit highlighted, a deep blue subunit glowing or highlighted, the highlight moving from one subunit to another, the highlight jumping to the pair that must stay unchanged, a haemoglobin molecule drawn as one single blob, a subunit leaving the cluster, the molecule splitting apart, any base letters A T G C or U anywhere, a U appearing anywhere, any number or position digit anywhere, any sex chromosome, any X or Y symbol, any chromosome pair, a red blood cell with a visible nucleus, a red blood cell still visible after 1.5 seconds, a sickle or crescent shaped cell, a second label plate, a second "एचबीबी", any other plate, chip, tag, callout or leader line, a plate with English text, any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, the haemoglobin molecule appearing before 1.6 seconds, the highlight appearing before 3.4 seconds, the gene strip appearing before 6.0 seconds, the plate appearing before 7.6 seconds, two phrases visible at the same time, garbled letters or broken matras during a transition, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, a golden word in either phrase, invented labels, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken Devanagari, detached matras, the word "बीटा-ग्लोबिन" broken across two lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, any English text, equations, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, a new logo, a duplicated logo, a redrawn logo, a moved logo, a watermark of any kind, text or diagram overlapping either top corner
```

---

**Notes / assumptions**

- **Seg 4 style deviation, flagged:** both phrases are UNIFORM white — no golden word. P1 contains the hyphenated `बीटा-ग्लोबिन` (ledger #7: hyphens break the keyword), and P2's `एचबीबी` also appears on the gene-strip plate (ledger #9: a word living in two places must not also be styled). This is the safe read of the rules, but it means Seg 4 has zero golden emphasis.
- **Seg 4 end-state deviation:** your plan says "No labels" for Seg 4, but the strip must be identifiable as the gene, so I gave it exactly **one** white plate reading `एचबीबी`, count-locked. If you'd rather keep it label-free, delete the plate, drop the 7.6 s beat, and remove item 3 from MANDATORY.
- Accuracy pins enforced in every spec above: **no nucleus, no hole/ring, red only, exactly 4 subunits as 2+2, only a β (teal-green) subunit highlighted, no A/T/G/C or U yet, no X/Y symbols.**

**Generate Segment 1 alone first, check it, then run the rest.** Say the word and I'll continue with segments 5–21.

Frames read — they confirm the house look: RBC red with a **both-sided dimple** (no hole, no nucleus), haemoglobin drawn as **blue bead units**, sickle cell as a **pointed-end crescent** with blue fibre rods. I've kept segments 5–8 consistent with that palette and with the accuracy brief.

---

## SEGMENT 5 — TRANSITION (diagram fades → `GAG → GTG` line)

```
VIDEO PROMPT — SEGMENT 5 OF 21

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

VOICEOVER NARRATION (spoken audio): an energetic, warm Indian male biology teacher voice speaks this exact Hinglish narration during the clip — nothing more, nothing less. The same script also appears on screen word for word, one phrase at a time:
"सिकल सेल एनीमिया में इस जीन के डीएनए क्रम में GAG के स्थान पर GTG हो जाता है।"

AUDIO: only the voiceover above. No background music. Only very soft whoosh and pop sounds on text animations are allowed.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, starting close to the top edge. The diagram and then the equation sit directly below the script text, filling the space between the text and the invisible middle line. The lowest element stops with a clear visible gap above the invisible middle line and never touches it; if it does not fit, make it smaller. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

LOGO SAFE AREA: keep the top-left corner and the top-right corner of the frame completely clear of script text, diagram, equation, labels and any moving element for the whole clip — only the background itself shows there. Do not draw, copy, move, recreate or animate any logo, wordmark, badge or watermark anywhere in the frame; the logo already present on the supplied background must stay exactly where it is, unchanged.

3D RENDER QUALITY (for the diagram in the first half of this clip):
The diagram is a real three dimensional object rendered in depth, not a flat drawing — a fixed three-quarter view from slightly above, curved surfaces appearing as rounded volumes rather than flat shapes, near-side parts brighter and sharper than far-side parts, a soft cool rim light along the upper left edge, glossy glass-like material with a faint specular highlight, and a very slow steady turn around the vertical axis.

DIAGRAM SPECIFICATION: the scene from the previous clip — one enlarged haemoglobin molecule made of exactly FOUR rounded glossy subunits arranged as two matched pairs, two identical alpha subunits in deep blue and two identical beta subunits in a lighter steel blue, packed together as one compact four-part cluster, with exactly ONE of the two beta subunits glowing softly yellow; and directly beneath it one short horizontal gene strip drawn as a slim translucent cyan-blue DNA ribbon carrying the plain Devanagari letters "एचबीबी" — is present at the very first frame exactly as it ended in the previous clip. It shrinks smoothly to about half its size, drifts upward, and fades away completely by 4.0 seconds, leaving the area below the script text free for the equation. The four-part cluster never gains or loses a subunit, never becomes three or five parts, and the glow never moves off the beta subunit onto an alpha subunit while it is visible. LABELS: this clip has NO labels at all. Never invent a label.

DIAGRAM TIMING SYNC (CRITICAL): the diagram carried over from the previous clip is already present at the very first frame and does not fade in again. The equation line appears at the exact moment the letters GAG are visible in the written phrase on screen, and never a frame before.

EQUATION RULE (CRITICAL): the equation is flat two dimensional overlay text, not a three dimensional object. It is ONE single clean horizontal line of large bold white mathematical text with a soft cyan glow, centred below the script text, perfectly sharp, with every symbol correct and correctly sized. It reads exactly "GAG → GTG" — three Latin capital letters, one arrow, three Latin capital letters, and nothing else. It is not on a card, not in a box, and never stacked onto two lines. If it is too wide, reduce its size until the whole line fits comfortably inside the frame width with clear margins on both sides. It appears exactly once and holds to the end of the clip. The script text stays at the top and the equation stays below it — they never overlap and never swap places.

HIGHLIGHT RULE (CRITICAL — NO NEW TEXT IS EVER CREATED): when a part of the equation is emphasised, that part of the EXISTING equation simply changes colour and glows brighter in place. NEVER copy a symbol out of the equation. NEVER draw a second copy of any symbol anywhere. NEVER create a label, plate, chip, callout or floating letter for it. The equation itself is the only place any symbol ever appears.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE. Every word appears exactly the number of times it is written.
- EXACT COUNT: the letters "GAG" appear exactly TWICE in total in this clip — once inside the third phrase and once inside the equation line. Nowhere else, in any size, at any moment.
- EXACT COUNT: the letters "GTG" appear exactly TWICE in total in this clip — once inside the third phrase and once inside the equation line. Nowhere else, in any size, at any moment. The middle letter is the capital letter T. It is never the letter U.
- EXACT COUNT: the letters "एचबीबी" appear exactly ONCE in this clip, only on the gene strip carried over from the previous clip, and they fade away with it by 4.0 seconds. They are never re-drawn afterwards.
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated. In this clip: the first phrase has the single golden word "एनीमिया", the second phrase has the single golden word "जीन", and the third phrase is COMPLETELY UNIFORM bold white with NO golden word because it contains the Latin letter groups GAG and GTG.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters or mathematical symbols individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time, perfectly synced with the voiceover. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean, glossy, textbook-style biology illustration rendered in three dimensions — smooth shapes, flat bright colours, soft even glow, like a modern NCERT diagram built in 3D. Never photorealistic. NO fire, NO flame, NO burning, NO spark, NO ember, NO explosion, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: continuing exactly from the previous clip — the enlarged four-part haemoglobin molecule, two deep blue alpha subunits and two lighter steel blue beta subunits, with one beta subunit glowing softly yellow, and the short "एचबीबी" gene strip directly beneath it. No red blood cell. No labels. Nothing else.

ANIMATION TIMELINE:
- 0.0 s: the carried-over haemoglobin cluster and gene strip are already fully visible and sharp, turning very slowly. The first phrase pops in at the top of the frame.
- 0.0–3.3 s: the first phrase is visible. From 2.0 s the cluster and gene strip begin shrinking to about half size and drifting upward while fading.
- 3.3 s: the first phrase disappears completely.
- 3.5 s: the second phrase pops in.
- 4.0 s: the haemoglobin cluster and the gene strip have faded away completely and are gone for the rest of the clip.
- 3.5–6.6 s: the second phrase is visible over an otherwise empty upper half.
- 6.6 s: the second phrase disappears completely.
- 6.8 s: the third phrase pops in.
- 7.2 s: exactly as the letters GAG are visible in the phrase on screen, the single equation line "GAG → GTG" pops in below the script text, fully sharp from its first visible frame, and holds unchanged to the end.
- 8.5 s: the middle letter T inside the existing "GTG" in the equation turns bright yellow and glows, staying exactly in its place inside the equation, and holds that glow to the end. No copy of it is ever made.
- 10.0 s: the clip ends with the third phrase and the equation line on screen.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "सिकल सेल एनीमिया में"
2. "इस जीन के डीएनए क्रम में"
3. "GAG के स्थान पर GTG हो जाता है।"
4. "GAG → GTG"
5. "एचबीबी" (already present on the carried-over gene strip at the first frame; fades away with it by 4.0 seconds and is never re-drawn)

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, invented labels, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, a new logo, a duplicated logo, a redrawn logo, a moved logo, a watermark of any kind, text or diagram overlapping either top corner, the letters GUG anywhere, the letter U inside either triplet, the letter A remaining in the middle of the second triplet, more than one letter differing between the two triplets, a deletion or insertion of a letter, the two triplets having different lengths, a shifted or frameshifted sequence, the equation appearing before 7.0 seconds, the haemoglobin cluster still visible after 4.0 seconds, a haemoglobin molecule with three or five subunits, a haemoglobin molecule drawn as one single blob, the glow appearing on an alpha subunit, all four subunits glowing, a red blood cell of any kind in this clip, a red blood cell with a visible nucleus, a doughnut or ring shaped cell with a hole, a sickle cell shaped like a smooth banana or a crescent moon with blunt ends, any label plate, any chip, any callout, any leader line, two copies of the equation, a copy of any letter taken out of the equation, a floating letter G or A or T anywhere outside the equation and the phrase, the equation moving or resizing, the equation stacked onto two lines, a golden word in the third phrase, wrong mathematical symbols, extra equations
```

---

## SEGMENT 6 — EQUATION_ONLY (`ग्लूटामिक अम्ल → वेलिन`)

```
VIDEO PROMPT — SEGMENT 6 OF 21

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

VOICEOVER NARRATION (spoken audio): an energetic, warm Indian male biology teacher voice speaks this exact Hinglish narration during the clip — nothing more, nothing less. The same script also appears on screen word for word, one phrase at a time:
"इस एक क्षार के परिवर्तन के कारण बीटा-ग्लोबिन श्रृंखला की छठी स्थिति पर ग्लूटामिक अम्ल के स्थान पर वेलिन आ जाता है।"

AUDIO: only the voiceover above. No background music. Only very soft whoosh and pop sounds on text animations are allowed.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, starting close to the top edge. The equation sits directly below the script text, comfortably above the invisible middle line, and is large enough that the top half does not look empty. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

LOGO SAFE AREA: keep the top-left corner and the top-right corner of the frame completely clear of script text, diagram, equation, labels and any moving element for the whole clip — only the background itself shows there. Do not draw, copy, move, recreate or animate any logo, wordmark, badge or watermark anywhere in the frame; the logo already present on the supplied background must stay exactly where it is, unchanged.

NO DIAGRAM IN THIS CLIP (CRITICAL): this clip contains NO three dimensional object of any kind. There is no red blood cell, no disc, no crescent, no cell, no haemoglobin molecule, no subunit, no bead, no chain, no DNA strand, no gene strip, no fibre, no blood vessel, no arrow into or out of a cell, no shape, no icon and no illustration anywhere in the frame at any moment. The only things on screen are the script text, the equation, the single line carried over from the previous clip which fades away by 1.5 seconds, and the plain background. Do not invent, add or imagine any diagram, object or graphic.

EQUATION RULE (CRITICAL): the line "GAG → GTG" carried over from the previous clip is present at the very first frame, does not move, and fades out completely by 1.5 seconds, never returning in any form. After it, exactly ONE equation exists in this clip. It is flat two dimensional overlay text, not a three dimensional object. It is ONE single clean horizontal line of large bold white text with a soft cyan glow, centred below the script text, perfectly sharp, with every letter correct and correctly sized. It reads exactly "ग्लूटामिक अम्ल → वेलिन". It is not on a card, not in a box, and never stacked onto two lines. If it is too wide, reduce its size until the whole line fits comfortably inside the frame width with clear margins on both sides. It appears exactly once and holds to the end of the clip. It never moves, never resizes and never duplicates. The script text stays at the top and the equation stays below it — they never overlap and never swap places.

HIGHLIGHT RULE (CRITICAL — NO NEW TEXT IS EVER CREATED): when a part of the equation is emphasised, that part of the EXISTING equation simply changes colour and glows brighter in place. NEVER copy a word out of the equation. NEVER draw a second copy of any word anywhere. NEVER create a label, plate, chip, callout or floating letter for it. The equation itself is the only place any word of it ever appears.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE. Every word appears exactly the number of times it is written.
- EXACT COUNT: the word "ग्लूटामिक" appears exactly TWICE in total in this clip — once inside the third phrase and once inside the equation line. Nowhere else, in any size, at any moment.
- EXACT COUNT: the word "अम्ल" appears exactly TWICE in total in this clip — once inside the third phrase and once inside the equation line. Nowhere else.
- EXACT COUNT: the word "वेलिन" appears exactly TWICE in total in this clip — once inside the third phrase and once inside the equation line. Nowhere else.
- EXACT COUNT: the letters "GAG" and the letters "GTG" appear exactly ONCE each in this clip, only inside the carried-over line at the very start, and they are gone by 1.5 seconds. They are never re-drawn afterwards.
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated. In this clip: the first phrase has the single golden word "क्षार", the second phrase has the single golden word "श्रृंखला", and the third phrase is COMPLETELY UNIFORM bold white with NO golden word because its words are repeated inside the equation line.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters or mathematical symbols individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time, perfectly synced with the voiceover. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean crisp flat overlay typography on a dark technical background. Never photorealistic. NO fire, NO flame, NO sparks, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: continuing exactly from the previous clip — the single line "GAG → GTG" sits alone below where the text will appear, sharp and still, with the middle letter T glowing yellow. Nothing else.

ANIMATION TIMELINE:
- 0.0 s: the carried-over line "GAG → GTG" is already fully visible and sharp. The first phrase pops in at the top of the frame.
- 0.0–1.5 s: the carried-over line fades out smoothly in place, without moving or resizing, and is completely gone at 1.5 seconds.
- 0.0–3.3 s: the first phrase is visible.
- 3.3 s: the first phrase disappears completely.
- 3.5–6.6 s: the second phrase is visible over an otherwise empty upper half.
- 6.6 s: the second phrase disappears completely.
- 6.8 s: the third phrase pops in.
- 7.3 s: exactly as the words ग्लूटामिक अम्ल are visible in the phrase on screen, the single line "ग्लूटामिक अम्ल → वेलिन" pops in below the script text, fully sharp from its first visible frame, and holds unchanged to the end.
- 8.6 s: the word वेलिन inside the existing line turns bright yellow and glows, staying exactly in its place inside the line, and holds that glow to the end. No copy of it is ever made.
- 10.0 s: the clip ends with the third phrase and the line "ग्लूटामिक अम्ल → वेलिन" on screen.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "इस एक क्षार के परिवर्तन के कारण"
2. "बीटा-ग्लोबिन श्रृंखला की छठी स्थिति पर"
3. "ग्लूटामिक अम्ल के स्थान पर वेलिन आ जाता है।"
4. "ग्लूटामिक अम्ल → वेलिन"
5. "GAG → GTG" (already present at the first frame from the previous clip; fades out by 1.5 seconds and is never re-drawn)

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, invented labels, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, a new logo, a duplicated logo, a redrawn logo, a moved logo, a watermark of any kind, text or diagram overlapping either top corner, any red blood cell, any crescent or sickle shaped cell, any haemoglobin molecule, any bead chain, any DNA strand, any gene strip, any blood vessel, any shape, icon or illustration, a copy of any word taken out of the line, a floating word ग्लूटामिक or वेलिन anywhere outside the line and the phrase, any label plate, any chip, any callout, any leader line, two copies of the line, the line moving or resizing, the line stacked onto two lines, a golden word in the third phrase, the carried-over line still visible after 1.5 seconds, the new line appearing before 7.0 seconds, any number other than what is written, the numbers 5 or 7 written anywhere, a position number written as a digit, a change shown on an alpha chain, more than one amino acid changing, wrong spellings such as HBs or HgB, extra equations
```

---

## SEGMENT 7 — EQUATION_ONLY (`HbA → HbS`)

```
VIDEO PROMPT — SEGMENT 7 OF 21

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

VOICEOVER NARRATION (spoken audio): an energetic, warm Indian male biology teacher voice speaks this exact Hinglish narration during the clip — nothing more, nothing less. The same script also appears on screen word for word, one phrase at a time:
"इस प्रकार सामान्य हीमोग्लोबिन HbA के स्थान पर HbS बनने लगता है।"

AUDIO: only the voiceover above. No background music. Only very soft whoosh and pop sounds on text animations are allowed.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, starting close to the top edge. The equation sits directly below the script text, comfortably above the invisible middle line, and is large enough that the top half does not look empty. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

LOGO SAFE AREA: keep the top-left corner and the top-right corner of the frame completely clear of script text, diagram, equation, labels and any moving element for the whole clip — only the background itself shows there. Do not draw, copy, move, recreate or animate any logo, wordmark, badge or watermark anywhere in the frame; the logo already present on the supplied background must stay exactly where it is, unchanged.

NO DIAGRAM IN THIS CLIP (CRITICAL): this clip contains NO three dimensional object of any kind. There is no red blood cell, no disc, no crescent, no cell, no haemoglobin molecule, no subunit, no bead, no chain, no DNA strand, no gene strip, no fibre, no blood vessel, no arrow into or out of a cell, no shape, no icon and no illustration anywhere in the frame at any moment. The only things on screen are the script text, the equation, the single line carried over from the previous clip which fades away by 1.5 seconds, and the plain background. Do not invent, add or imagine any diagram, object or graphic.

EQUATION RULE (CRITICAL): the line "ग्लूटामिक अम्ल → वेलिन" carried over from the previous clip is present at the very first frame, does not move, and fades out completely by 1.5 seconds, never returning in any form. After it, exactly ONE equation exists in this clip. It is flat two dimensional overlay text, not a three dimensional object. It is ONE single clean horizontal line of large bold white text with a soft cyan glow, centred below the script text, perfectly sharp, with every letter correct and correctly sized. It reads exactly "HbA → HbS" — capital H, small b, capital A, one arrow, capital H, small b, capital S, and nothing else. It is not on a card, not in a box, and never stacked onto two lines. If it is too wide, reduce its size until the whole line fits comfortably inside the frame width with clear margins on both sides. It appears exactly once and holds to the end of the clip. It never moves, never resizes and never duplicates. The script text stays at the top and the equation stays below it — they never overlap and never swap places.

HIGHLIGHT RULE (CRITICAL — NO NEW TEXT IS EVER CREATED): when a part of the equation is emphasised, that part of the EXISTING equation simply changes colour and glows brighter in place. NEVER copy a symbol out of the equation. NEVER draw a second copy of any symbol anywhere. NEVER create a label, plate, chip, callout or floating letter for it. The equation itself is the only place any symbol ever appears.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE. Every word appears exactly the number of times it is written.
- EXACT COUNT: the letters "HbA" appear exactly TWICE in total in this clip — once inside the first phrase and once inside the equation line. Nowhere else, in any size, at any moment. They are always written capital H, small b, capital A — never HBA, never HBa, never HgB.
- EXACT COUNT: the letters "HbS" appear exactly TWICE in total in this clip — once inside the second phrase and once inside the equation line. Nowhere else, in any size, at any moment. They are always written capital H, small b, capital S — never HBS, never HBs, never HgB.
- EXACT COUNT: the words "ग्लूटामिक", "अम्ल" and "वेलिन" appear exactly ONCE each in this clip, only inside the carried-over line at the very start, and they are gone by 1.5 seconds. They are never re-drawn afterwards.
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated. In this clip BOTH phrases are COMPLETELY UNIFORM bold white with NO golden word anywhere, because each contains a Latin letter code.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters or mathematical symbols individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time, perfectly synced with the voiceover. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean crisp flat overlay typography on a dark technical background. Never photorealistic. NO fire, NO flame, NO sparks, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: continuing exactly from the previous clip — the single line "ग्लूटामिक अम्ल → वेलिन" sits alone below where the text will appear, sharp and still, with the word वेलिन glowing yellow. Nothing else.

ANIMATION TIMELINE:
- 0.0 s: the carried-over line "ग्लूटामिक अम्ल → वेलिन" is already fully visible and sharp. The first phrase pops in at the top of the frame.
- 0.0–1.5 s: the carried-over line fades out smoothly in place, without moving or resizing, and is completely gone at 1.5 seconds.
- 0.0–4.8 s: the first phrase is visible.
- 2.6 s: exactly as the letters HbA are visible in the first phrase on screen, the single line "HbA → HbS" pops in below the script text, fully sharp from its first visible frame, and holds unchanged to the end.
- 4.8 s: the first phrase disappears completely.
- 5.0 s: the second phrase pops in and stays to the end.
- 6.5 s: the letters HbS inside the existing line turn bright yellow and glow, staying exactly in their place inside the line, and hold that glow to the end. No copy of them is ever made.
- 10.0 s: the clip ends with the second phrase and the line "HbA → HbS" on screen.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "इस प्रकार सामान्य हीमोग्लोबिन HbA के स्थान पर"
2. "HbS बनने लगता है।"
3. "HbA → HbS"
4. "ग्लूटामिक अम्ल → वेलिन" (already present at the first frame from the previous clip; fades out by 1.5 seconds and is never re-drawn)

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, invented labels, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, a new logo, a duplicated logo, a redrawn logo, a moved logo, a watermark of any kind, text or diagram overlapping either top corner, any red blood cell, any red blood cell with a visible nucleus, any doughnut or ring shaped cell with a hole, any crescent or sickle shaped cell, any smooth banana shape, any haemoglobin molecule, any bead chain, any DNA strand, any gene strip, any blood vessel, any shape, icon or illustration, the spellings HBs, HBS, HGB, HgB, Hbs or HBa, a subscript or superscript added to HbA or HbS, a copy of any symbol taken out of the line, a floating HbA or HbS anywhere outside the line and the phrases, a third HbA, a third HbS, any label plate, any chip, any callout, any leader line, two copies of the line, the line moving or resizing, the line stacked onto two lines, a golden word in either phrase, the carried-over line still visible after 1.5 seconds, the new line appearing before 2.4 seconds, extra equations
```

---

## SEGMENT 8 — TEXT_ONLY (low-oxygen trigger)

```
VIDEO PROMPT — SEGMENT 8 OF 21

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

VOICEOVER NARRATION (spoken audio): an energetic, warm Indian male biology teacher voice speaks this exact Hinglish narration during the clip — nothing more, nothing less. The same script also appears on screen word for word, one phrase at a time:
"समस्या तब उत्पन्न होती है जब शरीर में ऑक्सीजन की मात्रा कम हो जाती है।"

AUDIO: only the voiceover above. No background music. Only very soft whoosh and pop sounds on text animations are allowed.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, filling the width, starting close to the top edge, large enough to fill the upper area comfortably. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

LOGO SAFE AREA: keep the top-left corner and the top-right corner of the frame completely clear of script text, diagram, equation, labels and any moving element for the whole clip — only the background itself shows there. Do not draw, copy, move, recreate or animate any logo, wordmark, badge or watermark anywhere in the frame; the logo already present on the supplied background must stay exactly where it is, unchanged.

NO DIAGRAM IN THIS CLIP (CRITICAL): this clip contains NO three dimensional object of any kind. There is no red blood cell, no disc, no crescent, no cell, no haemoglobin molecule, no subunit, no bead, no chain, no DNA strand, no gene strip, no fibre, no blood vessel, no oxygen dot, no gauge, no meter, no arrow, no surface, no shape, no icon and no illustration anywhere in the frame at any moment. The only things on screen are the script text, the single line carried over from the previous clip which fades away by 1.5 seconds, and the plain background. Do not invent, add or imagine any diagram, object or graphic. After 1.5 seconds the space below the script text stays as plain empty background for the rest of the clip.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE. Every word appears exactly the number of times it is written.
- EXACT COUNT: the letters "HbA" and the letters "HbS" appear exactly ONCE each in this clip, only inside the carried-over line at the very start, and they are gone by 1.5 seconds. They are never re-drawn afterwards, in any size, at any moment.
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated. In this clip: the first phrase has the single golden word "समस्या" and the second phrase has the single golden word "ऑक्सीजन". No other word is coloured.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time, perfectly synced with the voiceover. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean crisp flat overlay typography on a dark technical background. Never photorealistic. NO fire, NO flame, NO sparks, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: continuing exactly from the previous clip — the single line "HbA → HbS" sits alone below where the text will appear, sharp and still, with HbS glowing yellow. Nothing else.

ANIMATION TIMELINE:
- 0.0 s: the carried-over line "HbA → HbS" is already fully visible and sharp. The first phrase pops in at the top of the frame.
- 0.0–1.5 s: the carried-over line fades out smoothly in place, without moving or resizing, and is completely gone at 1.5 seconds. From 1.5 seconds onward the whole area below the script text is plain empty background.
- 0.0–4.8 s: the first phrase is visible.
- 4.8 s: the first phrase disappears completely.
- 5.0 s: the second phrase pops in, fully sharp from its first visible frame, and holds to the end.
- 10.0 s: the clip ends with only the second phrase on screen and the rest of the frame empty.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "समस्या तब उत्पन्न होती है जब"
2. "शरीर में ऑक्सीजन की मात्रा कम हो जाती है।"
3. "HbA → HbS" (already present at the first frame from the previous clip; fades out by 1.5 seconds and is never re-drawn)

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, invented labels, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, a new logo, a duplicated logo, a redrawn logo, a moved logo, a watermark of any kind, text or diagram overlapping either top corner, any red blood cell, any red blood cell with a visible nucleus, any doughnut or ring shaped cell with a hole, any crescent or sickle shaped cell, any smooth banana shape, any haemoglobin molecule, any fibre or rod, any DNA strand, any gene strip, any blood vessel, any oxygen molecule or dot, any oxygen gauge, meter or dial, the symbol O2 anywhere, any sphere, ball, arrow, surface, shape, icon or illustration of any kind, any label plate, any chip, any callout, any leader line, equations, the carried-over line still visible after 1.5 seconds, a second golden word in either phrase, a golden word written again as a separate line
```

---

**Notes on choices made here**

- **Seg 5 golden words:** `एनीमिया` (P1), `जीन` (P2); P3 forced uniform — it carries `GAG`/`GTG`. Avoided `बीटा-ग्लोबिन` and `माता-पिता` style hyphenated words as keywords throughout (ledger #7).
- **Accuracy bans wired in:** no-U-in-triplet, single-base substitution only, no α-chain change, no position 5/7, no nucleus, no ring/doughnut, no blunt banana crescent, no `HBs`/`HgB` casing — each appears as an explicit NEGATIVE in the segments where the model could plausibly draw it.
- **`एचबीबी` gene strip** is declared in Seg 5's MANDATORY list as a carried-over string that fades by 4.0 s, so it can't be re-invented later (ledger #6).
- Every equation clip states the **exact character composition** of its line, which is the main defence against symbol garbling in Devanagari + Latin mixes.

Generate **Segment 5 first and check it** — it's the only transition in this block and the riskiest (diagram fade + Latin triplets in one clip). If 5 lands clean, 6–8 will follow.

Frames confirm the house look I'll lock into the specs: **red biconcave RBC (no nucleus, no hole), blue HbS molecules/rods inside, pointed-end red crescent** — so these prompts stay visually consistent with the Hindi card set.

Below are Segments 9–12, full blocks, tested order, uploaded-background (§15) + LOGO SAFE AREA (§16) in every one.

```
VIDEO PROMPT — SEGMENT 9 OF 21

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

VOICEOVER NARRATION (spoken audio): an energetic, warm Indian male biology teacher voice speaks this exact Hinglish narration during the clip — nothing more, nothing less. The same script also appears on screen word for word, one phrase at a time:
"ऐसी स्थिति में HbS के अणु आपस में जुड़कर लंबी रेशेदार संरचनाएँ बना लेते हैं,"

AUDIO: only the voiceover above. No background music. Only very soft whoosh and pop sounds on text animations are allowed.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, starting close to the top edge. The diagram sits directly below the script text and fills the space between the text and the invisible middle line, so the top half never looks empty. The lowest part of the diagram stops with a clear visible gap above the invisible middle line and never touches it; if it does not fit, make it smaller. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

LOGO SAFE AREA: keep the top-left corner and the top-right corner of the frame completely clear of script text, diagram, equation, labels and any moving element for the whole clip — only the background itself shows there. Do not draw, copy, move, recreate or animate any logo, wordmark, badge or watermark anywhere in the frame; the logo already present on the supplied background must stay exactly where it is, unchanged.

3D RENDER QUALITY (CRITICAL — THIS MAKES THE DIAGRAM LOOK THREE DIMENSIONAL):
The diagram is a real three dimensional object rendered in depth, not a flat drawing.
- CAMERA: a fixed three-quarter view from slightly above the object, so the viewer looks slightly down at it and can clearly read its roundness. Never a flat straight-on front view.
- PERSPECTIVE: circles that run around the object appear as flattened ellipses because of the viewing angle, becoming flatter near the top and bottom and rounder near the middle. Nothing is drawn as a plain flat circle.
- DEPTH: the parts nearest the camera are brighter, thicker and sharper. The parts on the far side, seen through the transparent surface, are noticeably dimmer, thinner and softer. This difference is clear and obvious.
- LIGHTING: one soft cool rim light along the upper left edge and a gentle ambient fill, giving a rounded sculpted look with a soft falloff toward the lower right.
- MATERIAL: a smooth glossy glass-like surface with a faint specular highlight near the upper left, and a soft inner glow.
- FORESHORTENING: any rod pointing toward the camera looks shorter and thicker, and any rod pointing away looks longer and thinner. They are never all the same length on screen.
- MOTION: the object turns very slowly and steadily around its vertical axis so the depth reads clearly. It never wobbles, never squashes, never deforms and never changes size once settled.

DIAGRAM SPECIFICATION (build exactly this, nothing else):
- THE RED BLOOD CELL: one single red blood cell rendered in full three dimensions as a BICONCAVE DISC — a rounded red disc that is pressed inward into a shallow dimple on BOTH of its flat faces, so it reads as a soft cushion pinched in the middle. Seen from the three-quarter camera angle its outline is a flattened ellipse and the near dimple is clearly visible as a smooth shallow depression. It is uniformly deep red all over, glossy, soft-edged, with a soft cool rim light along the upper left. There is NO hole through it, it is NOT a ring, NOT a doughnut, NOT a bowl, and there is NO dark blob, NO nucleus and NO organelle of any kind inside it — the paler centre is only thinness, never a drawn object. It turns very slowly and steadily and never deforms in this clip.
- THE HbS MOLECULES: about sixteen small round beads of deep blue, glossy, evenly scattered inside the transparent red cell and clearly seen through its surface, each with a tiny specular highlight on its upper left. They drift very slightly and never leave the cell.
- THE HbS FIBRES: four long straight stiff rods formed inside the same cell, each rod built from the same deep blue beads stacked end to end in a perfectly straight line, lying roughly parallel to one another in a neat bundle. The rods are rigid and straight — never curved, never wavy, never tangled, never branching. Because of perspective the rod nearest the camera reads shorter and thicker and the far one thinner and dimmer. The cell KEEPS its biconcave shape for the whole of this clip — the rods form inside it but the cell does not change shape yet.
- LABELS: this clip has NO labels at all. No plate, no chip, no tag, no floating letter, no leader line. Never invent a label.

DIAGRAM TIMING SYNC (CRITICAL): every object appears at the exact moment its name is visible in the written phrase on screen, and never a frame before. The single exception is the red blood cell that holds everything: it fades in once at 0.5 seconds as the container for the molecules, and then stays. Once an object appears it stays to the end of the clip.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE. Every word appears exactly the number of times it is written.
- EXACT COUNT: the letters "HbS" appear exactly ONCE in total in this clip — once inside the first phrase and nowhere else, in any size, at any moment. They are written with a capital H, a small b and a capital S, never "HBs", never "HgB".
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol, in correct Devanagari with every matra placed correctly.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. In this clip the FIRST phrase contains the letters HbS, so the first phrase is COMPLETELY UNIFORM bold white with NO golden word. In the SECOND phrase exactly one word, "रेशेदार", is golden, styled in place inside the sentence. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time, perfectly synced with the voiceover. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean, glossy, textbook-style biology illustration rendered in three dimensions — smooth shapes, flat bright colours, soft even glow, like a modern NCERT diagram built in 3D. Never photorealistic, never a microscope photograph. NO fire, NO flame, NO burning, NO spark, NO ember, NO explosion, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: completely empty background. Nothing at all.

ANIMATION TIMELINE:
- 0.0 s: the first phrase "ऐसी स्थिति में HbS के अणु" pops in at the very top of the frame, fully sharp, completely uniform bold white.
- 0.5 s: the red blood cell fades in below the script text as a three dimensional biconcave red disc with a dimple on both faces, and begins its very slow steady turn.
- 2.0 s, exactly as the word "अणु" is visible on screen, about sixteen small deep blue HbS molecule beads pop in one by one inside the cell, seen through its transparent red surface, and drift very slightly.
- 4.8 s: the first phrase fades out completely.
- 4.8 s to 5.0 s: no phrase is on screen.
- 5.0 s: the second phrase "आपस में जुड़कर लंबी रेशेदार संरचनाएँ बना लेते हैं," pops in at the very top, fully sharp, with only the word "रेशेदार" in gold.
- 6.4 s, exactly as the word "रेशेदार" is visible on screen, the scattered blue beads slide together and lock end to end into four long straight rigid rods lying parallel in a neat bundle inside the cell. The rods are perfectly straight and stiff.
- 7.5 s to 10.0 s: the rods hold, the cell keeps its biconcave shape and keeps turning very slowly. The second phrase holds on screen to 10.0 s.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "ऐसी स्थिति में HbS के अणु"
2. "आपस में जुड़कर लंबी रेशेदार संरचनाएँ बना लेते हैं,"

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, broken or misplaced Devanagari matras, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, invented labels, any label plate, any chip, any callout, any leader line, stray floating letters or symbols, a second "HbS" anywhere, "HBs", "HGB", "HbA" anywhere in this clip, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, a new logo, a duplicated logo, a redrawn logo, a moved logo, a watermark of any kind, text or diagram overlapping either top corner, a red blood cell with a visible nucleus, a dark blob or dot drawn at the centre of the cell as an organelle, a red blood cell drawn as a flat circle, a ring or a doughnut with a hole through it, a bowl or cup shape with a dimple on only one face, a blue or purple red blood cell, the cell changing into a sickle or crescent shape in this clip, the cell deforming, curving or bending, wavy, curved, tangled, branching or spiral fibres, fibres outside the cell, the fibres appearing before 6.4 seconds, the molecules appearing before 2.0 seconds, the cell appearing before 0.5 seconds, oxygen molecules, gauges, dials, meters, arrows, DNA strands, chromosomes, equations, chemical formulae, microscope views
```

```
VIDEO PROMPT — SEGMENT 10 OF 21

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

VOICEOVER NARRATION (spoken audio): an energetic, warm Indian male biology teacher voice speaks this exact Hinglish narration during the clip — nothing more, nothing less. The same script also appears on screen word for word, one phrase at a time:
"और लाल रक्त कोशिका का द्विअवतल आकार बदलकर हँसिए के आकार का हो जाता है। इसी कारण इसे सिकल सेल एनीमिया कहा जाता है।"

AUDIO: only the voiceover above. No background music. Only very soft whoosh and pop sounds on text animations are allowed.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, starting close to the top edge. The diagram sits directly below the script text and fills the space between the text and the invisible middle line, so the top half never looks empty. The lowest part of the diagram stops with a clear visible gap above the invisible middle line and never touches it; if it does not fit, make it smaller. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

LOGO SAFE AREA: keep the top-left corner and the top-right corner of the frame completely clear of script text, diagram, equation, labels and any moving element for the whole clip — only the background itself shows there. Do not draw, copy, move, recreate or animate any logo, wordmark, badge or watermark anywhere in the frame; the logo already present on the supplied background must stay exactly where it is, unchanged.

3D RENDER QUALITY (CRITICAL — THIS MAKES THE DIAGRAM LOOK THREE DIMENSIONAL):
The diagram is a real three dimensional object rendered in depth, not a flat drawing.
- CAMERA: a fixed three-quarter view from slightly above the object, so the viewer looks slightly down at it and can clearly read its roundness. Never a flat straight-on front view.
- PERSPECTIVE: circles that run around the object appear as flattened ellipses because of the viewing angle, becoming flatter near the top and bottom and rounder near the middle. Nothing is drawn as a plain flat circle.
- DEPTH: the parts nearest the camera are brighter, thicker and sharper. The parts on the far side, seen through the transparent surface, are noticeably dimmer, thinner and softer. This difference is clear and obvious.
- LIGHTING: one soft cool rim light along the upper left edge and a gentle ambient fill, giving a rounded sculpted look with a soft falloff toward the lower right.
- MATERIAL: a smooth glossy glass-like surface with a faint specular highlight near the upper left, and a soft inner glow.
- FORESHORTENING: any rod pointing toward the camera looks shorter and thicker, and any rod pointing away looks longer and thinner. They are never all the same length on screen.
- MOTION: the object turns very slowly and steadily around its vertical axis so the depth reads clearly. It never wobbles, never squashes, never deforms and never changes size once settled, apart from the single shape change described in the timeline.

DIAGRAM SPECIFICATION (build exactly this, nothing else):
- THE CELL AT THE START: the scene from the previous clip is already present at the very first frame and does not fade in again — one single red blood cell in full three dimensions as a BICONCAVE DISC, uniformly deep red, glossy, pressed inward into a shallow dimple on BOTH flat faces, with NO hole, NO ring, NO doughnut opening, NO dark blob, NO nucleus and NO organelle inside it, turning very slowly; and inside it four long straight stiff deep blue rods lying parallel in a neat bundle.
- THE SHAPE CHANGE: the same single cell changes shape exactly once, driven from inside by the stiff blue rods pushing outward, so the disc is drawn out along the line of the rods. This is one smooth continuous deformation of the SAME cell — no second cell is created, nothing is swapped, nothing cuts.
- THE SICKLE CELL AT THE END: the cell becomes a CRESCENT — a curved red sickle that is POINTED and sharp at BOTH ends, with one clearly concave inner edge and one convex outer edge, still the same deep red, still glossy with the soft cool rim light along the upper left. It is NOT a banana, NOT a smooth crescent moon with blunt rounded ends, NOT a star, NOT spiky, NOT a hook, NOT an oval. The four straight blue rods remain inside it, now running along the long axis of the crescent and clearly visible through the red surface. The crescent turns very slowly and steadily and then holds.
- LABELS: this clip has NO labels at all. No plate, no chip, no tag, no floating letter, no leader line. Never invent a label.

DIAGRAM TIMING SYNC (CRITICAL): the shape change happens at the exact moment the word naming the new shape is visible in the written phrase on screen, and never a frame before. The diagram carried over from the previous clip is already present at the very first frame and does not fade in again. Once the new shape is reached it stays to the end of the clip.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE. Every word appears exactly the number of times it is written.
- EXACT COUNT: the word "आकार" appears exactly TWICE in total in this clip — once inside the first phrase and once inside the second phrase. Nowhere else, in any size, at any moment.
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol, in correct Devanagari with every matra placed correctly.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. In this clip the word "आकार" is shared across the first two phrases, so ALL THREE phrases in this clip are rendered COMPLETELY UNIFORM bold white with NO golden word anywhere. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time, perfectly synced with the voiceover. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean, glossy, textbook-style biology illustration rendered in three dimensions — smooth shapes, flat bright colours, soft even glow, like a modern NCERT diagram built in 3D. Never photorealistic, never a microscope photograph. NO fire, NO flame, NO burning, NO spark, NO ember, NO explosion, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: continuing exactly from the previous clip — one three dimensional biconcave red blood cell, dimple on both faces, no hole and no nucleus, with four long straight stiff deep blue rods bundled inside it, turning very slowly below where the script text will appear. Nothing else.

ANIMATION TIMELINE:
- 0.0 s: the first phrase "और लाल रक्त कोशिका का द्विअवतल आकार" pops in at the very top of the frame, fully sharp, completely uniform bold white. The cell keeps its biconcave shape and keeps turning.
- 3.3 s: the first phrase fades out completely. 3.3 s to 3.5 s: no phrase on screen.
- 3.5 s: the second phrase "बदलकर हँसिए के आकार का हो जाता है।" pops in at the very top, fully sharp, completely uniform bold white.
- 4.6 s, exactly as the word "हँसिए" is visible on screen, the stiff blue rods push outward and the SAME cell deforms smoothly and continuously over about 1.2 seconds into a red crescent that is pointed and sharp at both ends, with one concave edge and one convex edge. The rods now run along its long axis.
- 5.8 s: the shape change is complete. The crescent holds and turns very slowly.
- 6.6 s: the second phrase fades out completely. 6.6 s to 6.8 s: no phrase on screen.
- 6.8 s: the third phrase "इसी कारण इसे सिकल सेल एनीमिया कहा जाता है।" pops in at the very top, fully sharp, completely uniform bold white, and holds to 10.0 s while the crescent keeps turning slowly. No new object appears after 5.8 seconds.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "और लाल रक्त कोशिका का द्विअवतल आकार"
2. "बदलकर हँसिए के आकार का हो जाता है।"
3. "इसी कारण इसे सिकल सेल एनीमिया कहा जाता है।"

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, broken or misplaced Devanagari matras, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, a golden word in any phrase, a third "आकार", invented labels, any label plate, any chip, any callout, any leader line, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, a new logo, a duplicated logo, a redrawn logo, a moved logo, a watermark of any kind, text or diagram overlapping either top corner, a second cell appearing beside the first, the biconcave cell and the sickle cell both on screen at the same time, a red blood cell with a visible nucleus, a dark blob or dot drawn at the centre of the cell as an organelle, a cell drawn as a flat circle, a ring or a doughnut with a hole through it, a sickle cell drawn as a smooth banana with rounded blunt ends, a crescent moon shape with blunt ends, a star shape, a spiky cell, a hooked or S shaped cell, a blue or purple cell, the shape change starting before 4.6 seconds, the shape changing more than once, the cell changing back, wavy, curved, tangled or branching fibres, fibres outside the cell, oxygen molecules, gauges, dials, meters, arrows, DNA strands, chromosomes, equations, chemical formulae, HbA, HbS or any Latin letters on screen, microscope views
```

```
VIDEO PROMPT — SEGMENT 11 OF 21

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

VOICEOVER NARRATION (spoken audio): an energetic, warm Indian male biology teacher voice speaks this exact Hinglish narration during the clip — nothing more, nothing less. The same script also appears on screen word for word, one phrase at a time:
"ये कोशिकाएँ कठोर और कम लचीली हो जाती हैं, इसलिए छोटी रक्त वाहिकाओं में फँस सकती हैं,"

AUDIO: only the voiceover above. No background music. Only very soft whoosh and pop sounds on text animations are allowed.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, starting close to the top edge. The diagram sits directly below the script text and fills the space between the text and the invisible middle line, so the top half never looks empty. The lowest part of the diagram stops with a clear visible gap above the invisible middle line and never touches it; if it does not fit, make it smaller. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

LOGO SAFE AREA: keep the top-left corner and the top-right corner of the frame completely clear of script text, diagram, equation, labels and any moving element for the whole clip — only the background itself shows there. Do not draw, copy, move, recreate or animate any logo, wordmark, badge or watermark anywhere in the frame; the logo already present on the supplied background must stay exactly where it is, unchanged.

3D RENDER QUALITY (CRITICAL — THIS MAKES THE DIAGRAM LOOK THREE DIMENSIONAL):
The diagram is a real three dimensional object rendered in depth, not a flat drawing.
- CAMERA: a fixed three-quarter view from slightly above the scene, so the viewer looks slightly down at it and can clearly read the roundness of the tube and the cells. Never a flat straight-on front view.
- PERSPECTIVE: the circular openings of the tube appear as flattened ellipses because of the viewing angle, and the tube narrows toward its far end. Nothing is drawn as a plain flat circle or a plain flat rectangle.
- DEPTH: the parts nearest the camera are brighter, thicker and sharper. The parts on the far side, seen through the transparent tube wall, are noticeably dimmer, thinner and softer. This difference is clear and obvious.
- LIGHTING: one soft cool rim light along the upper left edge and a gentle ambient fill, giving a rounded sculpted look with a soft falloff toward the lower right.
- MATERIAL: the tube is smooth glossy glass-like and see-through; the cells are glossy with a faint specular highlight near the upper left and a soft inner glow.
- FORESHORTENING: cells further along the tube read smaller and dimmer than the ones near the camera. They are never all the same size on screen.
- MOTION: nothing wobbles, nothing squashes, nothing deforms and nothing changes size once settled. The wedged cells are completely rigid and motionless.

DIAGRAM SPECIFICATION (build exactly this, nothing else):
- THE SICKLE CELL AT THE START: the cell from the previous clip is already present at the very first frame and does not fade in again — one red crescent in full three dimensions, POINTED and sharp at BOTH ends, one concave inner edge and one convex outer edge, deep red and glossy, with four long straight stiff deep blue rods running along its long axis inside it. It is NOT a banana, NOT a blunt-ended crescent moon, NOT a star, NOT spiky.
- THE BLOOD VESSEL: one narrow transparent tube in full three dimensions running gently across the diagram area and tapering to a visibly narrower neck, made of a thin pale grey-blue see-through wall with a soft cool rim light along its upper left. Its openings read as flattened ellipses. It is see-through so everything inside it is clearly visible. It never becomes solid, never bends and never pulses.
- THE WEDGED SICKLE CELLS: exactly TWO red crescents, both pointed at both ends with blue rods inside, jammed hard against the narrow neck of the tube and against each other, held completely rigid and motionless — they do not bend, do not squeeze through and do not deform in any way. One of them is the crescent carried over from the previous clip, which moves into the tube; the second one arrives behind it.
- THE NORMAL RED BLOOD CELLS: exactly THREE normal red blood cells queued in the tube behind the block — each a three dimensional BICONCAVE red disc with a shallow dimple on BOTH faces, uniformly deep red, glossy, with NO hole, NO ring opening, NO nucleus and NO dark central blob. They are soft and flexible looking and drift slowly forward until they reach the queue and stop. The field is mixed — normal cells and sickle cells are both present, never all cells sickled.
- LABELS: this clip has NO labels at all. No plate, no chip, no tag, no floating letter, no leader line. Never invent a label.

DIAGRAM TIMING SYNC (CRITICAL): every object appears at the exact moment its name is visible in the written phrase on screen, and never a frame before. The diagram carried over from the previous clip is already present at the very first frame and does not fade in again. Once an object appears it stays to the end of the clip.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE. Every word appears exactly the number of times it is written.
- EXACT COUNT: the word "कठोर" appears exactly ONCE in this clip and the word "वाहिकाओं" appears exactly ONCE in this clip. Neither is ever written a second time, in any size, at any moment, and neither is ever written as a separate line of its own.
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol, in correct Devanagari with every matra placed correctly.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. In this clip the first phrase has exactly one golden word, "कठोर", and the second phrase has exactly one golden word, "वाहिकाओं", each styled in place inside its own sentence. No other word is coloured. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time, perfectly synced with the voiceover. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean, glossy, textbook-style biology illustration rendered in three dimensions — smooth shapes, flat bright colours, soft even glow, like a modern NCERT diagram built in 3D. Never photorealistic, never a microscope photograph. NO fire, NO flame, NO burning, NO spark, NO ember, NO explosion, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: continuing exactly from the previous clip — one three dimensional red crescent sickle cell, pointed at both ends, with four straight stiff deep blue rods inside it, turning very slowly below where the script text will appear. Nothing else.

ANIMATION TIMELINE:
- 0.0 s: the first phrase "ये कोशिकाएँ कठोर और कम लचीली हो जाती हैं," pops in at the very top of the frame, fully sharp, with only the word "कठोर" in gold.
- 1.4 s, exactly as the word "कठोर" is visible on screen, the crescent stops turning and locks completely rigid and motionless, its edges reading sharper and harder.
- 4.8 s: the first phrase fades out completely. 4.8 s to 5.0 s: no phrase on screen.
- 5.0 s: the second phrase "इसलिए छोटी रक्त वाहिकाओं में फँस सकती हैं," pops in at the very top, fully sharp, with only the word "वाहिकाओं" in gold.
- 6.2 s, exactly as the word "वाहिकाओं" is visible on screen, the narrow transparent tube fades in around the crescent, tapering to a visibly narrower neck, and the crescent settles inside it.
- 7.4 s: a second red crescent drifts in from the wide end and jams hard against the first one at the narrow neck. Both stop dead and stay completely rigid.
- 8.4 s: three normal biconcave red discs drift slowly along the tube behind the block, reach the queue and stop.
- 9.0 s to 10.0 s: the whole scene holds completely still, the second phrase holding on screen to 10.0 s. No new object appears after 8.4 seconds.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "ये कोशिकाएँ कठोर और कम लचीली हो जाती हैं,"
2. "इसलिए छोटी रक्त वाहिकाओं में फँस सकती हैं,"

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, broken or misplaced Devanagari matras, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, a second golden word inside one phrase, invented labels, any label plate, any chip, any callout, any leader line, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, a new logo, a duplicated logo, a redrawn logo, a moved logo, a watermark of any kind, text or diagram overlapping either top corner, every cell in the vessel drawn as a sickle cell, a field with no normal red blood cells, a third sickle cell, a fourth normal cell, a red blood cell with a visible nucleus, a dark blob or dot drawn at the centre of a cell as an organelle, a cell drawn as a flat circle, a ring or a doughnut with a hole through it, a sickle cell drawn as a smooth banana with rounded blunt ends, a crescent moon with blunt ends, a star shape, a spiky cell, a blue or purple cell, a sickle cell bending, squeezing through or deforming, the tube appearing before 6.2 seconds, the second crescent appearing before 7.4 seconds, the normal cells appearing before 8.4 seconds, a solid or opaque vessel wall, a pulsing or bending vessel, oxygen molecules, gauges, dials, meters, arrows, DNA strands, chromosomes, equations, chemical formulae, HbA, HbS or any Latin letters on screen, microscope views
```

```
VIDEO PROMPT — SEGMENT 12 OF 21

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

VOICEOVER NARRATION (spoken audio): an energetic, warm Indian male biology teacher voice speaks this exact Hinglish narration during the clip — nothing more, nothing less. The same script also appears on screen word for word, one phrase at a time:
"जिससे रक्त प्रवाह बाधित हो जाता है और ऊतकों तक पर्याप्त ऑक्सीजन नहीं पहुँच पाती।"

AUDIO: only the voiceover above. No background music. Only very soft whoosh and pop sounds on text animations are allowed.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, starting close to the top edge. The diagram sits directly below the script text and fills the space between the text and the invisible middle line, so the top half never looks empty. The lowest part of the diagram stops with a clear visible gap above the invisible middle line and never touches it; if it does not fit, make it smaller. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

LOGO SAFE AREA: keep the top-left corner and the top-right corner of the frame completely clear of script text, diagram, equation, labels and any moving element for the whole clip — only the background itself shows there. Do not draw, copy, move, recreate or animate any logo, wordmark, badge or watermark anywhere in the frame; the logo already present on the supplied background must stay exactly where it is, unchanged.

3D RENDER QUALITY (CRITICAL — THIS MAKES THE DIAGRAM LOOK THREE DIMENSIONAL):
The diagram is a real three dimensional object rendered in depth, not a flat drawing.
- CAMERA: a fixed three-quarter view from slightly above the scene, so the viewer looks slightly down at it and can clearly read the roundness of the tube and the cells. Never a flat straight-on front view.
- PERSPECTIVE: the circular openings of the tube appear as flattened ellipses because of the viewing angle, and the tube narrows toward its far end. Nothing is drawn as a plain flat circle or a plain flat rectangle.
- DEPTH: the parts nearest the camera are brighter, thicker and sharper. The parts on the far side, seen through the transparent tube wall, are noticeably dimmer, thinner and softer. This difference is clear and obvious.
- LIGHTING: one soft cool rim light along the upper left edge and a gentle ambient fill, giving a rounded sculpted look with a soft falloff toward the lower right.
- MATERIAL: the tube is smooth glossy glass-like and see-through; the cells are glossy with a faint specular highlight near the upper left and a soft inner glow.
- FORESHORTENING: cells further along the tube read smaller and dimmer than the ones near the camera. They are never all the same size on screen.
- MOTION: nothing wobbles, nothing squashes, nothing deforms and nothing changes size at any moment. Every cell in this clip is completely still.

DIAGRAM SPECIFICATION (build exactly this, nothing else):
- NO NEW OBJECT IS CREATED IN THIS CLIP. The entire scene from the previous clip is already present at the very first frame and does not fade in again, and nothing whatsoever is added to it: one narrow transparent tube in full three dimensions with a visibly narrower neck, made of a thin pale grey-blue see-through wall with a soft cool rim light along its upper left; exactly TWO red crescent sickle cells, each pointed and sharp at BOTH ends with one concave and one convex edge and four straight stiff deep blue rods inside, jammed rigid against the narrow neck; and exactly THREE normal red blood cells, each a three dimensional BICONCAVE red disc with a shallow dimple on BOTH faces, uniformly deep red, with NO hole, NO ring opening, NO nucleus and NO dark central blob, queued still behind the block.
- THE ONLY CHANGE IN THIS CLIP IS LIGHTING AND STILLNESS: the queued cells, which were drifting, come to a complete stop, and the far part of the tube beyond the block gradually loses its glow and dims to a duller, greyer, desaturated red-grey, showing that nothing is reaching it. The near part of the tube, before the block, keeps its normal brightness. No object moves position, no object is added, no object is removed.
- LABELS: this clip has NO labels at all. No plate, no chip, no tag, no floating letter, no leader line. Never invent a label.

DIAGRAM TIMING SYNC (CRITICAL): no new object appears at any moment in this clip. The diagram carried over from the previous clip is already present at the very first frame and does not fade in again. The two lighting changes happen at the exact moments given in the timeline, each as the matching word is visible in the written phrase on screen, and never a frame before.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE. Every word appears exactly the number of times it is written.
- EXACT COUNT: the word "बाधित" appears exactly ONCE in this clip and the word "ऑक्सीजन" appears exactly ONCE in this clip. Neither is ever written a second time, in any size, at any moment, and neither is ever written as a separate line of its own.
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol, in correct Devanagari with every matra placed correctly.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. In this clip the first phrase has exactly one golden word, "बाधित", and the second phrase has exactly one golden word, "ऑक्सीजन", each styled in place inside its own sentence. No other word is coloured. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time, perfectly synced with the voiceover. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean, glossy, textbook-style biology illustration rendered in three dimensions — smooth shapes, flat bright colours, soft even glow, like a modern NCERT diagram built in 3D. Never photorealistic, never a microscope photograph. NO fire, NO flame, NO burning, NO spark, NO ember, NO explosion, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: continuing exactly from the previous clip — one narrow transparent tube with a narrower neck, two rigid red crescent sickle cells jammed at that neck, and three normal biconcave red discs queued behind them, all sitting below where the script text will appear. Nothing else.

ANIMATION TIMELINE:
- 0.0 s: the first phrase "जिससे रक्त प्रवाह बाधित हो जाता है" pops in at the very top of the frame, fully sharp, with only the word "बाधित" in gold.
- 2.0 s, exactly as the word "बाधित" is visible on screen, the three queued normal cells come to a complete stop and the whole flow freezes. Nothing new appears.
- 4.8 s: the first phrase fades out completely. 4.8 s to 5.0 s: no phrase on screen.
- 5.0 s: the second phrase "और ऊतकों तक पर्याप्त ऑक्सीजन नहीं पहुँच पाती।" pops in at the very top, fully sharp, with only the word "ऑक्सीजन" in gold.
- 6.5 s, exactly as the word "ऑक्सीजन" is visible on screen, the part of the tube beyond the block slowly loses its glow over about 1.5 seconds and dims to a duller greyer desaturated tone, while the part before the block stays normally bright. No object moves and no object is added.
- 8.0 s to 10.0 s: the whole scene holds completely still and unchanged, the second phrase holding on screen to 10.0 s.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "जिससे रक्त प्रवाह बाधित हो जाता है"
2. "और ऊतकों तक पर्याप्त ऑक्सीजन नहीं पहुँच पाती।"

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, broken or misplaced Devanagari matras, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, a second golden word inside one phrase, invented labels, any label plate, any chip, any callout, any leader line, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, a new logo, a duplicated logo, a redrawn logo, a moved logo, a watermark of any kind, text or diagram overlapping either top corner, any new object appearing in this clip, an extra sickle cell, an extra normal cell, oxygen molecules or dots, cyan particles, gauges, dials, meters, arrows, cross marks, warning signs, tissue drawn as a new organ or body part, every cell in the vessel drawn as a sickle cell, a field with no normal red blood cells, a red blood cell with a visible nucleus, a dark blob or dot drawn at the centre of a cell as an organelle, a cell drawn as a flat circle, a ring or a doughnut with a hole through it, a sickle cell drawn as a smooth banana with rounded blunt ends, a crescent moon with blunt ends, a star shape, a spiky cell, a blue or purple cell, a sickle cell bending, squeezing through or deforming, the block clearing, cells resuming flow, the dimming starting before 6.5 seconds, the near part of the tube dimming, DNA strands, chromosomes, equations, chemical formulae, HbA, HbS or any Latin letters on screen, microscope views
```

**Notes on choices you may want to override:**
- **Seg 9 carve-out:** the red blood cell isn't named in Seg 9's script, so strict timing-sync had no anchor. I let it fade in once at 0.5 s as the container and wrote that exception explicitly into the sync block — otherwise the model invents its own entry time.
- **Seg 10 golden word:** all three phrases forced UNIFORM (not just P1/P2), because `आकार` crosses phrases and a gold word in P3 next to two uniform phrases reliably triggers the "keyword as separate line" bug.
- **Seg 12** is the riskiest clip in this block — a segment with *no* new object is something these models fight. The `NO NEW OBJECT IS CREATED` header plus the explicit "any new object appearing in this clip" ban is what holds it.
- Colours match the Hindi cards you're already using: red cells, deep-blue HbS beads/rods, pale grey-blue vessel.

Generate **Segment 9 alone first**, check it, then run 10–12.

Frames confirm the house look I'll pin in the diagram specs: **red biconcave disc with no nucleus and no hole, blue HbS fibre rods running lengthwise, crescent pointed at both ends.** Prompts below follow that.

**One correction to the plan's count-lock, Segment 15:** the plan says `HbS = 3×`, but phrase 1 ("जीन प्रारूप HbS HbS होता है") carries it twice and the genotype line `HbS HbS` carries it twice again — that's **FOUR**. A wrong count line is worse than none (the model will "fix" the count by deleting a real HbS), so I've locked it at four. Same reason Segment 16's lock is written as time-scoped: the carried-over `HbS HbS` line is alive for the first 1.5 s, so a flat "HbS appears twice" would contradict the first frames.

---

```
VIDEO PROMPT — SEGMENT 13 OF 21

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

VOICEOVER NARRATION (spoken audio): an energetic, warm Indian male biology teacher voice speaks this exact Hinglish narration during the clip — nothing more, nothing less. The same script also appears on screen word for word, one phrase at a time:
"साथ ही ये जल्दी टूटने लगती हैं, इसी कारण रक्ताल्पता उत्पन्न होती है।"

AUDIO: only the voiceover above. No background music. Only very soft whoosh and pop sounds on text animations are allowed.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, starting close to the top edge. The diagram sits directly below the script text and fills the space between the text and the invisible middle line, so the top half never looks empty. The lowest part of the diagram stops with a clear visible gap above the invisible middle line and never touches it; if it does not fit, make it smaller. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

LOGO SAFE AREA: keep the top-left corner and the top-right corner of the frame completely clear of script text, diagram, equation, labels and any moving element for the whole clip — only the background itself shows there. Do not draw, copy, move, recreate or animate any logo, wordmark, badge or watermark anywhere in the frame; the logo already present on the supplied background must stay exactly where it is, unchanged.

3D RENDER QUALITY (CRITICAL — THIS MAKES THE DIAGRAM LOOK THREE DIMENSIONAL):
The diagram is a real three dimensional object rendered in depth, not a flat drawing.
- CAMERA: a fixed three-quarter view from slightly above the object, so the viewer looks slightly down at it and can clearly read its roundness. Never a flat straight-on front view.
- PERSPECTIVE: circles that run around the object appear as flattened ellipses because of the viewing angle, becoming flatter near the top and bottom and rounder near the middle. Nothing is drawn as a plain flat circle.
- DEPTH: the parts nearest the camera are brighter, thicker and sharper. The parts on the far side, seen through the transparent surface, are noticeably dimmer, thinner and softer. This difference is clear and obvious.
- LIGHTING: one soft cool rim light along the upper left edge and a gentle ambient fill, giving a rounded sculpted look with a soft falloff toward the lower right.
- MATERIAL: a smooth glossy glass-like surface with a faint specular highlight near the upper left, and a soft inner glow.
- FORESHORTENING: any arrow pointing toward the camera looks shorter and thicker with a larger arrowhead, and any arrow pointing away looks longer and thinner. They are never all the same length on screen.
- MOTION: the object turns very slowly and steadily around its vertical axis so the depth reads clearly. It never wobbles, never squashes, never deforms and never changes size once settled.

DIAGRAM SPECIFICATION (build exactly this, nothing else):
- THE CARRIED-OVER VESSEL SCENE: the scene from the previous clip is present at the very first frame, exactly as it ended — one narrow translucent pale-grey capillary tube running across the frame, with two rigid crescent-shaped sickle cells wedged and stuck inside its narrowest part, and three normal biconcave red discs stalled in a queue behind them, with the tissue beyond the blockage dimmed. It does not fade in again. From 0.0 to 2.0 seconds this whole vessel scene — the tube, the stalled normal discs and one of the two sickle cells — shrinks slightly and fades away completely, leaving ONE single sickle cell alone in the centre of the diagram area. Nothing else remains.
- THE SICKLE CELL: one three dimensional crescent-shaped red blood cell, deep red all over, curved like a farming sickle with a sharply POINTED tip at BOTH ends, one concave inner edge and one convex outer edge. It is a solid rounded three dimensional body with a glossy surface, a soft cool rim light along its upper left edge and a specular highlight, never a flat cut-out shape. Inside it, seen faintly through the surface, run several long straight stiff blue fibre rods lying lengthwise along the crescent, which is what makes it rigid. It has NO nucleus, NO dark central blob, NO hole, NO ring and NO opening of any kind. It is never blue, never purple, never grey.
- THE BREAKING: from 2.8 seconds the surface of this same sickle cell develops thin cracks and it splits apart into four or five irregular deep red fragments of clearly different sizes, which drift slowly apart from one another and keep drifting gently and steadily for the rest of the clip. The fragments are the SAME cell broken up — no new cell is ever created and no fragment is ever added after 4.0 seconds. The fragments never reassemble, never explode, never burst outward fast, never scatter as sparks and never leave the diagram area.
- THE PALING: from 6.5 seconds the drifting fragments slowly lose colour intensity together, going from deep red to a noticeably paler washed-out red, and hold that paler colour to the end. This is a colour change of the existing fragments only — nothing new appears and nothing is removed.
- LABELS: this clip has NO labels at all. No plate, no chip, no tag, no leader line, no floating letter. Never invent a label.

DIAGRAM TIMING SYNC (CRITICAL): every object appears at the exact moment its name is visible in the written phrase on screen, and never a frame before. Once an object appears it stays to the end of the clip. The diagram carried over from the previous clip is already present at the very first frame and does not fade in again.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE. Every word appears exactly the number of times it is written.
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol, in Devanagari script.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. In the first phrase the ONE golden word is टूटने. In the second phrase the ONE golden word is रक्ताल्पता. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time, perfectly synced with the voiceover. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean, glossy, textbook-style biology illustration rendered in three dimensions — smooth shapes, flat bright colours, soft even glow, like a modern NCERT diagram built in 3D. Never photorealistic. NO fire, NO flame, NO burning, NO spark, NO ember, NO explosion, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: continuing exactly from the previous clip — the narrow translucent capillary tube with two rigid pointed-end sickle cells wedged in its narrowest part, three normal biconcave red discs stalled in a queue behind them, and the tissue beyond the blockage dimmed. No text on screen yet. Nothing else.

ANIMATION TIMELINE:
- 0.0 s: the carried-over vessel scene is already fully present and sharp, exactly as described in SCREEN AT START.
- 0.0–2.0 s: the capillary tube, the stalled normal discs, the dimmed tissue and one of the two sickle cells shrink slightly and fade away completely, leaving ONE sickle cell alone in the centre of the diagram area, turning very slowly.
- 0.0–4.8 s: the first phrase "साथ ही ये जल्दी टूटने लगती हैं," is visible at the very top of the frame, fully sharp from its first frame, with the word टूटने styled in gold in place inside the sentence.
- 2.8 s, exactly as the word टूटने is visible on screen, thin cracks appear across the surface of that same sickle cell.
- 2.8–4.0 s: the cell splits into four or five irregular deep red fragments of different sizes, which begin drifting slowly apart. No fragment is added after 4.0 s.
- 4.8 s: the first phrase disappears completely.
- 4.8–5.0 s: no phrase is on screen at all.
- 5.0–10.0 s: the second phrase "इसी कारण रक्ताल्पता उत्पन्न होती है।" is visible at the very top of the frame, fully sharp from its first frame, with the word रक्ताल्पता styled in gold in place inside the sentence, and holds to the end.
- 6.5–8.0 s: the drifting fragments slowly fade from deep red to a noticeably paler washed-out red, and hold that paler colour to 10.0 s.
- 10.0 s: the clip ends with the second phrase at the top and the pale drifting fragments below it.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "साथ ही ये जल्दी टूटने लगती हैं,"
2. "इसी कारण रक्ताल्पता उत्पन्न होती है।"

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, invented labels, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, a new logo, a duplicated logo, a redrawn logo, a moved logo, a watermark of any kind, text or diagram overlapping either top corner, a red blood cell with a visible nucleus, a dark central blob inside any red blood cell, a red blood cell drawn as a ring or doughnut with a hole, a red blood cell drawn as a flat two dimensional circle, a sickle cell shaped like a smooth banana with blunt rounded ends, a sickle cell shaped like a crescent moon with blunt ends, a sickle cell with only one pointed end, a star-shaped or spiky cell, a blue or purple or grey red blood cell, a nucleus or organelle inside any fragment, any DNA strand, any letters G A T C anywhere, any chromosome, any sex chromosome, any X or Y symbol, any pedigree chart, any label plate, any chip, any callout, any leader line, any equation, any genotype text, any new whole cell appearing after 2.8 seconds, the fragments reassembling into a whole cell, the cell bursting or exploding outward, cracks appearing before 2.8 seconds, the vessel scene still visible after 2.0 seconds, more than five fragments, a flat two dimensional cut-out instead of a three dimensional body, a straight-on front view with no depth
```

---

```
VIDEO PROMPT — SEGMENT 14 OF 21

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

VOICEOVER NARRATION (spoken audio): an energetic, warm Indian male biology teacher voice speaks this exact Hinglish narration during the clip — nothing more, nothing less. The same script also appears on screen word for word, one phrase at a time:
"सिकल सेल एनीमिया एक अप्रभावी अलिंगी गुणसूत्रीय रोग है। यदि बच्चे को दोनों माता-पिता से सिकल सेल वाला जीन मिलता है,"

AUDIO: only the voiceover above. No background music. Only very soft whoosh and pop sounds on text animations are allowed.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, starting close to the top edge. The diagram sits directly below the script text and fills the space between the text and the invisible middle line, so the top half never looks empty. The lowest part of the diagram stops with a clear visible gap above the invisible middle line and never touches it; if it does not fit, make it smaller. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

LOGO SAFE AREA: keep the top-left corner and the top-right corner of the frame completely clear of script text, diagram, equation, labels and any moving element for the whole clip — only the background itself shows there. Do not draw, copy, move, recreate or animate any logo, wordmark, badge or watermark anywhere in the frame; the logo already present on the supplied background must stay exactly where it is, unchanged.

3D RENDER QUALITY (for the diagram in the first half of this clip):
The diagram is a real three dimensional object rendered in depth, not a flat drawing — a fixed three-quarter view from slightly above, circles appearing as flattened ellipses, near-side lines brighter and sharper than far-side lines, a soft cool rim light along the upper left edge, glossy glass-like material with a faint specular highlight, and a very slow steady turn around the vertical axis.

DIAGRAM SPECIFICATION: the scene from the previous clip — four or five irregular pale washed-out red fragments of one broken sickle cell, drifting slowly apart, with faint short blue fibre rods visible inside some of them, no nucleus and no hole in any fragment — is present at the very first frame and does not fade in again. It shrinks smoothly to about half its size, drifts upward, and fades away completely by 3.5 seconds, leaving the whole area below the script text as plain empty background for the rest of the clip. From 3.5 seconds to 10.0 seconds this clip contains NO three dimensional object of any kind: no cell, no fragment, no fibre, no vessel, no chromosome, no shape, no icon and no illustration anywhere in the frame. LABELS: this clip has NO labels at all. Never invent a label.

DIAGRAM TIMING SYNC (CRITICAL): no object appears at any point in this clip. The diagram carried over from the previous clip is already present at the very first frame, does not fade in again, and only fades out as described. Nothing is ever added.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE beyond what is written. Every word appears exactly the number of times it is written.
- EXACT COUNT: the word "सिकल" appears exactly TWICE in total in this clip — once inside the first phrase and once inside the third phrase. Nowhere else, in any size, at any moment.
- EXACT COUNT: the word "सेल" appears exactly TWICE in total in this clip — once inside the first phrase and once inside the third phrase. Nowhere else, in any size, at any moment.
- The word "माता-पिता" is written exactly as given, with its hyphen, on one single line, and is never split across two lines.
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol, in Devanagari script.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. In this clip ALL THREE phrases are rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word anywhere in this clip. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time, perfectly synced with the voiceover. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean crisp flat overlay typography on a dark technical background. Never photorealistic. NO fire, NO flame, NO sparks, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: continuing exactly from the previous clip — four or five irregular pale washed-out red fragments of one broken sickle cell drifting slowly apart, faint blue fibre rods visible inside some of them. No text on screen yet. Nothing else.

ANIMATION TIMELINE:
- 0.0 s: the drifting pale red fragments are already fully present and sharp, exactly as described in SCREEN AT START.
- 0.0–3.5 s: the fragments shrink smoothly to about half their size, drift gently upward, and fade away completely by 3.5 s. After 3.5 s the area below the script text is plain empty background for the rest of the clip.
- 0.0–3.3 s: the first phrase "सिकल सेल एनीमिया एक अप्रभावी अलिंगी गुणसूत्रीय रोग है।" is visible at the very top of the frame, fully sharp from its first frame, completely uniform bold white.
- 3.3 s: the first phrase disappears completely. 3.3–3.5 s: no phrase is on screen at all.
- 3.5–6.6 s: the second phrase "यदि बच्चे को दोनों माता-पिता से" is visible at the very top of the frame, fully sharp from its first frame, completely uniform bold white.
- 6.6 s: the second phrase disappears completely. 6.6–6.8 s: no phrase is on screen at all.
- 6.8–10.0 s: the third phrase "सिकल सेल वाला जीन मिलता है," is visible at the very top of the frame, fully sharp from its first frame, completely uniform bold white, and holds to the end.
- 10.0 s: the clip ends with the third phrase at the top and completely empty background below it.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "सिकल सेल एनीमिया एक अप्रभावी अलिंगी गुणसूत्रीय रोग है।"
2. "यदि बच्चे को दोनों माता-पिता से"
3. "सिकल सेल वाला जीन मिलता है,"

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, invented labels, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, a new logo, a duplicated logo, a redrawn logo, a moved logo, a watermark of any kind, text or diagram overlapping either top corner, a golden word in any phrase, any cell, fragment, fibre, vessel, shape, icon or illustration visible after 3.5 seconds, any new object appearing at any moment, the fragments reassembling into a whole cell, a red blood cell with a visible nucleus, a red blood cell drawn as a ring or doughnut with a hole, a sickle cell shaped like a smooth banana with blunt rounded ends, any chromosome, any sex chromosome, any X chromosome, any Y chromosome, any pedigree chart, any family tree, any male or female pedigree symbol, any Punnett square, any DNA strand, any letters G A T C, any equation, any genotype text, any label plate, any chip, any callout, any leader line, "सिकल" appearing a third time, "सेल" appearing a third time, "माता-पिता" broken across two lines
```

---

```
VIDEO PROMPT — SEGMENT 15 OF 21

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

VOICEOVER NARRATION (spoken audio): an energetic, warm Indian male biology teacher voice speaks this exact Hinglish narration during the clip — nothing more, nothing less. The same script also appears on screen word for word, one phrase at a time:
"तो जीन प्रारूप HbS HbS होता है और उसे रोग हो सकता है।"

AUDIO: only the voiceover above. No background music. Only very soft whoosh and pop sounds on text animations are allowed.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, starting close to the top edge. The equation sits directly below the script text, comfortably above the invisible middle line, and is large enough that the top half does not look empty. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

LOGO SAFE AREA: keep the top-left corner and the top-right corner of the frame completely clear of script text, diagram, equation, labels and any moving element for the whole clip — only the background itself shows there. Do not draw, copy, move, recreate or animate any logo, wordmark, badge or watermark anywhere in the frame; the logo already present on the supplied background must stay exactly where it is, unchanged.

NO DIAGRAM IN THIS CLIP (CRITICAL): this clip contains NO three dimensional object of any kind. There is no cell, no red blood cell, no sickle cell, no fragment, no fibre, no haemoglobin molecule, no blood vessel, no chromosome, no DNA strand, no arrow, no shape, no icon and no illustration anywhere in the frame at any moment. The only things on screen are the script text, the equation, and the plain background. Do not invent, add or imagine any diagram, object or graphic. The space below the equation stays as plain empty background.

EQUATION RULE (CRITICAL): the equation is flat two dimensional overlay text, not a three dimensional object. It is ONE single clean horizontal line of large bold white text with a soft cyan glow, centred below the script text, perfectly sharp, with every symbol correct and correctly sized, reading exactly "HbS HbS" — capital H, lowercase b, capital S, twice, separated by one single space. It is not on a card, not in a box, and never stacked onto two lines. If it is too wide, reduce its size until the whole line fits comfortably inside the frame width with clear margins on both sides. It appears exactly once and holds to the end of the clip. The script text stays at the top and the equation stays below it — they never overlap and never swap places.

HIGHLIGHT RULE (CRITICAL — NO NEW TEXT IS EVER CREATED): when a part of the equation is emphasised, that part of the EXISTING equation simply changes colour and glows brighter in place. NEVER copy a symbol out of the equation. NEVER draw a second copy of any symbol anywhere. NEVER create a label, plate, chip, callout or floating letter for it. The equation itself is the only place any symbol ever appears.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE beyond what is written. Every word appears exactly the number of times it is written.
- EXACT COUNT: the group of letters "HbS" appears exactly FOUR times in total in this clip — exactly TWICE inside the first phrase, where it is written "HbS HbS", and exactly TWICE inside the equation line, which is also written "HbS HbS". There is no fifth "HbS" anywhere, in any size, at any moment. There is never a single lonely "HbS" on its own.
- The letters "HbA" do NOT appear anywhere in this clip.
- The letters H, b and S never appear on their own, separated from the group "HbS", anywhere on screen.
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol; the Devanagari words in Devanagari script and "HbS" in Latin letters with capital H, lowercase b, capital S.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. In this clip BOTH phrases are rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word anywhere in this clip. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated, and "HbS HbS" is never split across two lines.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters or mathematical symbols individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters or mathematical symbols are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time, perfectly synced with the voiceover. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean crisp flat overlay typography on a dark technical background. Never photorealistic. NO fire, NO flame, NO sparks, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: completely empty background. Nothing at all.

ANIMATION TIMELINE:
- 0.0–4.8 s: the first phrase "तो जीन प्रारूप HbS HbS होता है" is visible at the very top of the frame, fully sharp from its first frame, completely uniform bold white.
- At 1.8 s, exactly as "HbS HbS" is visible on screen inside the first phrase, the equation line "HbS HbS" pops in once below the script text, fully sharp from its first visible frame, and holds without moving to the end of the clip.
- 4.8 s: the first phrase disappears completely. The equation line stays exactly where it is.
- 4.8–5.0 s: no phrase is on screen at all; only the equation line remains.
- 5.0–10.0 s: the second phrase "और उसे रोग हो सकता है।" is visible at the very top of the frame, fully sharp from its first frame, completely uniform bold white, and holds to the end.
- At 6.5 s both "HbS" groups inside the EXISTING equation line turn bright yellow and glow, staying exactly in their places inside that same line, and hold that glow to the end. No copy of them is made and no new text is created.
- 10.0 s: the clip ends with the second phrase at the top and the glowing "HbS HbS" line below it.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "तो जीन प्रारूप HbS HbS होता है"
2. "और उसे रोग हो सकता है।"
3. "HbS HbS"

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, invented labels, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, a new logo, a duplicated logo, a redrawn logo, a moved logo, a watermark of any kind, text or diagram overlapping either top corner, any cell, red blood cell, sickle cell, fragment, fibre, haemoglobin molecule, blood vessel, arrow, shape, icon or illustration, a copy of any symbol taken out of the equation, a floating "HbS" anywhere outside the first phrase and the equation line, a fifth "HbS", a lone "HbS" on its own, the letters "HbA" anywhere, a lone letter H, a lone letter b, a lone letter S, "HBs", "Hbs", "HGB", "HbSS" written as one word, any label plate, any chip, any callout, any leader line, two copies of the equation, the equation moving or resizing, the equation stacked onto two lines, the equation inside a box or card, a golden word in either phrase, the equation appearing before 1.8 seconds, wrong letters in the equation, extra equations, any chromosome, any sex chromosome, any X or Y symbol, any pedigree chart, any Punnett square, any DNA strand, any letters G A T C, any number or digit
```

---

```
VIDEO PROMPT — SEGMENT 16 OF 21

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

VOICEOVER NARRATION (spoken audio): an energetic, warm Indian male biology teacher voice speaks this exact Hinglish narration during the clip — nothing more, nothing less. The same script also appears on screen word for word, one phrase at a time:
"केवल एक से मिलने पर जीन प्रारूप HbA HbS होता है और व्यक्ति सामान्यतः वाहक होता है।"

AUDIO: only the voiceover above. No background music. Only very soft whoosh and pop sounds on text animations are allowed.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, starting close to the top edge. The equation sits directly below the script text, comfortably above the invisible middle line, and is large enough that the top half does not look empty. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

LOGO SAFE AREA: keep the top-left corner and the top-right corner of the frame completely clear of script text, diagram, equation, labels and any moving element for the whole clip — only the background itself shows there. Do not draw, copy, move, recreate or animate any logo, wordmark, badge or watermark anywhere in the frame; the logo already present on the supplied background must stay exactly where it is, unchanged.

NO DIAGRAM IN THIS CLIP (CRITICAL): this clip contains NO three dimensional object of any kind. There is no cell, no red blood cell, no sickle cell, no fragment, no fibre, no haemoglobin molecule, no blood vessel, no chromosome, no DNA strand, no arrow, no shape, no icon and no illustration anywhere in the frame at any moment. The only things on screen are the script text, the equation, and the plain background. Do not invent, add or imagine any diagram, object or graphic. The space below the equation stays as plain empty background.

EQUATION RULE (CRITICAL): the equation is flat two dimensional overlay text, not a three dimensional object. It is ONE single clean horizontal line of large bold white text with a soft cyan glow, centred below the script text, perfectly sharp, with every symbol correct and correctly sized, reading exactly "HbA HbS" — capital H, lowercase b, capital A, then one single space, then capital H, lowercase b, capital S. It is not on a card, not in a box, and never stacked onto two lines. If it is too wide, reduce its size until the whole line fits comfortably inside the frame width with clear margins on both sides. It appears exactly once and holds to the end of the clip. Only ONE equation line is ever on screen after 1.5 seconds. The script text stays at the top and the equation stays below it — they never overlap and never swap places.

HIGHLIGHT RULE (CRITICAL — NO NEW TEXT IS EVER CREATED): when a part of the equation is emphasised, that part of the EXISTING equation simply changes colour and glows brighter in place. NEVER copy a symbol out of the equation. NEVER draw a second copy of any symbol anywhere. NEVER create a label, plate, chip, callout or floating letter for it. The equation itself is the only place any symbol ever appears.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE beyond what is written. Every word appears exactly the number of times it is written.
- THE CARRIED-OVER LINE: the line "HbS HbS" from the previous clip is on screen at the very first frame, exactly as it ended, and fades away completely by 1.5 seconds. It never returns, never moves and is never written again after 1.5 seconds. From 1.5 seconds onward the letters "HbS HbS" never appear as a pair anywhere.
- EXACT COUNT: the group of letters "HbA" appears exactly TWICE in total in this clip — once inside the second phrase and once inside the equation line. Nowhere else, in any size, at any moment.
- EXACT COUNT: after 1.5 seconds, the group of letters "HbS" appears exactly TWICE in total in this clip — once inside the second phrase and once inside the equation line. Nowhere else, in any size, at any moment. Before 1.5 seconds it appears only inside the fading carried-over line.
- The letters H, b, A and S never appear on their own, separated from the groups "HbA" and "HbS", anywhere on screen.
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol; the Devanagari words in Devanagari script and "HbA" and "HbS" in Latin letters.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. In this clip ALL THREE phrases are rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word anywhere in this clip. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated, and "HbA HbS" is never split across two lines.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters or mathematical symbols individually. NEVER morph one phrase into another. NEVER morph the old line into the new line — the old line must fade out completely and the new line pops in separately. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters or mathematical symbols are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time, perfectly synced with the voiceover. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean crisp flat overlay typography on a dark technical background. Never photorealistic. NO fire, NO flame, NO sparks, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: continuing exactly from the previous clip — one single line reading "HbS HbS" sits alone below where the script text will appear, sharp and still, glowing yellow. No script phrase is on screen yet. Nothing else.

ANIMATION TIMELINE:
- 0.0 s: the carried-over line "HbS HbS" is already fully present and sharp, exactly as described in SCREEN AT START. It does not pop in again.
- 0.0–1.5 s: the carried-over line "HbS HbS" fades away completely and is gone by 1.5 s. It never returns. Between 1.5 s and 5.0 s there is no equation line on screen.
- 0.0–3.3 s: the first phrase "केवल एक से मिलने पर" is visible at the very top of the frame, fully sharp from its first frame, completely uniform bold white.
- 3.3 s: the first phrase disappears completely. 3.3–3.5 s: no phrase is on screen at all.
- 3.5–6.6 s: the second phrase "जीन प्रारूप HbA HbS होता है" is visible at the very top of the frame, fully sharp from its first frame, completely uniform bold white.
- At 5.0 s, exactly as "HbA HbS" is visible on screen inside the second phrase, the equation line "HbA HbS" pops in once below the script text, fully sharp from its first visible frame, and holds without moving to the end of the clip.
- 6.6 s: the second phrase disappears completely. The equation line stays exactly where it is. 6.6–6.8 s: no phrase is on screen at all.
- 6.8–10.0 s: the third phrase "और व्यक्ति सामान्यतः वाहक होता है।" is visible at the very top of the frame, fully sharp from its first frame, completely uniform bold white, and holds to the end.
- At 7.5 s the whole EXISTING equation line "HbA HbS" turns bright green and glows, staying exactly in its place, and holds that colour to the end. No copy of it is made and no new text is created.
- 10.0 s: the clip ends with the third phrase at the top and the green glowing "HbA HbS" line below it.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "केवल एक से मिलने पर"
2. "जीन प्रारूप HbA HbS होता है"
3. "और व्यक्ति सामान्यतः वाहक होता है।"
4. "HbA HbS"

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, invented labels, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, a new logo, a duplicated logo, a redrawn logo, a moved logo, a watermark of any kind, text or diagram overlapping either top corner, any cell, red blood cell, sickle cell, fragment, fibre, haemoglobin molecule, blood vessel, arrow, shape, icon or illustration, a sickled cell shown for a carrier, any symptom or damage shown for a carrier, a copy of any symbol taken out of the equation, a floating "HbA" or "HbS" anywhere outside the second phrase and the equation line, a third "HbA", a third "HbS", the old line "HbS HbS" visible after 1.5 seconds, the old line morphing into the new line, two equation lines on screen at the same time after 1.5 seconds, a lone letter H, a lone letter b, a lone letter A, a lone letter S, "HBs", "Hbs", "HGB", "HbAS" written as one word, any label plate, any chip, any callout, any leader line, two copies of the equation, the equation moving or resizing, the equation stacked onto two lines, the equation inside a box or card, a golden word in any phrase, the equation appearing before 5.0 seconds, extra equations, any chromosome, any sex chromosome, any X or Y symbol, any pedigree chart, any Punnett square, any DNA strand, any letters G A T C, any number or digit
```

---

**Continuity handoff for Segment 17:** empty background is *not* where Seg 16 ends — it ends with the green `HbA HbS` line still on screen. Seg 17 in the plan is "prev line fades 0–1.5 s", so its SCREEN AT START must read *"one single line reading `HbA HbS`, sharp and still, glowing green"* and its `HbA`/`HbS` count locks must be time-scoped the same way this one's are.

Frames confirm the house look — red biconcave disc, blue HbS fibre bundles, pointed-end crescent — so Segment 19's diagram spec below is pinned to exactly that.

Here are Segments 17–20, full blocks, tested order, nothing abbreviated.

---

**Segment 17 of 21** — TEXT_ONLY (carried `HbA HbS` line fades out 0–1.5 s)

```
VIDEO PROMPT — SEGMENT 17 OF 21

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

VOICEOVER NARRATION (spoken audio): an energetic, warm Indian male biology teacher voice speaks this exact Hinglish narration during the clip — nothing more, nothing less. The same script also appears on screen word for word, one phrase at a time:
"लक्षण आवश्यक रूप से नहीं होते, लेकिन वह यह जीन अगली पीढ़ी में पहुँचा सकता है।"

AUDIO: only the voiceover above. No background music. Only very soft whoosh and pop sounds on text animations are allowed.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, filling the width, starting close to the top edge, large enough to fill the upper area comfortably. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

LOGO SAFE AREA: keep the top-left corner and the top-right corner of the frame completely clear of script text, diagram, equation, labels and any moving element for the whole clip — only the background itself shows there. Do not draw, copy, move, recreate or animate any logo, wordmark, badge or watermark anywhere in the frame; the logo already present on the supplied background must stay exactly where it is, unchanged.

NO DIAGRAM IN THIS CLIP (CRITICAL): this clip contains NO three dimensional object of any kind. There is no red blood cell, no sickle cell, no blood vessel, no haemoglobin molecule, no DNA strand, no chain of beads, no fibre, no arrow, no icon and no illustration anywhere in the frame at any moment. The only things on screen are the script text, the single carried-over genotype line described below which fades away early, and the plain background. Do not invent, add or imagine any diagram, object or graphic. The space below the script text stays as plain empty background.

CARRIED-OVER LINE (the only non-script text in this clip): the single line "HbA HbS" is already present at the very first frame, sitting alone on one single horizontal line below where the script text appears, sharp and still, as flat two dimensional overlay text. It does not fade in again, never moves, never resizes and never duplicates. It fades out smoothly and completely between 0.0 and 1.5 seconds and is gone for the rest of the clip, leaving plain empty background beneath the script text. No new copy of it is ever drawn.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE. Every word appears exactly the number of times it is written.
- EXACT COUNT: the string "HbA" appears exactly ONCE in total in this clip, inside the carried-over line, and the string "HbS" appears exactly ONCE in total in this clip, inside the same carried-over line. Neither appears anywhere else, in any size, at any moment, and neither appears at all after 1.5 seconds.
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol, in correct Devanagari with every matra and conjunct correct.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. In this clip the ONLY golden word is "लक्षण" in the first phrase. The second phrase and the third phrase are rendered completely uniform in bold white with no golden word at all. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time, perfectly synced with the voiceover. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean crisp flat overlay typography on a dark technical background. Never photorealistic. NO fire, NO flame, NO sparks, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: continuing exactly from the previous clip — one single line reading "HbA HbS" sitting alone below where the script text will appear, sharp and still. Nothing else.

ANIMATION TIMELINE:
0.0 s — the line "HbA HbS" is already on screen from the very first frame, sharp and still, and immediately begins fading out.
0.0–3.3 s — first phrase "लक्षण आवश्यक रूप से नहीं होते," pops in fully sharp at the top of the frame and holds, then disappears completely at 3.3 s.
0.0–1.5 s — the line "HbA HbS" fades out smoothly and is completely gone by 1.5 s, leaving plain empty background below the script text for the rest of the clip.
3.3–3.5 s — no phrase is visible at all.
3.5–6.6 s — second phrase "लेकिन वह यह जीन" pops in fully sharp and holds, then disappears completely at 6.6 s.
6.6–6.8 s — no phrase is visible at all.
6.8–10.0 s — third phrase "अगली पीढ़ी में पहुँचा सकता है।" pops in fully sharp and holds to the very end of the clip.
Nothing else appears, moves or changes at any moment. The area below the script text is plain empty background from 1.5 s onward.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "लक्षण आवश्यक रूप से नहीं होते,"
2. "लेकिन वह यह जीन"
3. "अगली पीढ़ी में पहुँचा सकता है।"
4. "HbA HbS"

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, invented labels, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken Devanagari conjuncts, missing or misplaced matras, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, a new logo, a duplicated logo, a redrawn logo, a moved logo, a watermark of any kind, text or diagram overlapping either top corner, any red blood cell, any sickle cell, any crescent shape, any blood vessel, any haemoglobin molecule, any chain of beads, any fibre, any DNA strand, any arrow, any shape, any icon or illustration of any kind, any label plate, any equation, a second copy of "HbA", a second copy of "HbS", the line "HbA HbS" still visible after 1.5 seconds, the line "HbA HbS" moving or resizing, a golden word in the second phrase, a golden word in the third phrase, a family tree, a pedigree chart, a Punnett square, sex chromosome symbols, an X or Y chromosome, a sick-looking or sickled cell drawn beside the word वाहक, a red blood cell with a visible nucleus
```

---

**Segment 18 of 21** — TEXT_ONLY, empty start

```
VIDEO PROMPT — SEGMENT 18 OF 21

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

VOICEOVER NARRATION (spoken audio): an energetic, warm Indian male biology teacher voice speaks this exact Hinglish narration during the clip — nothing more, nothing less. The same script also appears on screen word for word, one phrase at a time:
"तो बस इतना याद रखो एक क्षार बदला, एक अमीनो अम्ल बदला,"

AUDIO: only the voiceover above. No background music. Only very soft whoosh and pop sounds on text animations are allowed.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, filling the width, starting close to the top edge, large enough to fill the upper area comfortably. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

LOGO SAFE AREA: keep the top-left corner and the top-right corner of the frame completely clear of script text, diagram, equation, labels and any moving element for the whole clip — only the background itself shows there. Do not draw, copy, move, recreate or animate any logo, wordmark, badge or watermark anywhere in the frame; the logo already present on the supplied background must stay exactly where it is, unchanged.

NO DIAGRAM IN THIS CLIP (CRITICAL): this clip contains NO three dimensional object of any kind. There is no red blood cell, no sickle cell, no blood vessel, no haemoglobin molecule, no DNA strand, no chain of beads, no fibre, no arrow, no icon and no illustration anywhere in the frame at any moment. The only things on screen are the script text and the plain background. Do not invent, add or imagine any diagram, object or graphic. The space below the script text stays as plain empty background.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE beyond what is written. In the second phrase the words "एक" and "बदला" are written exactly as given.
- EXACT COUNT: the word "एक" appears exactly TWICE in total in this clip, both times inside the second phrase, and never a third time anywhere, in any size, at any moment.
- EXACT COUNT: the word "बदला" appears exactly TWICE in total in this clip, both times inside the second phrase, and never a third time anywhere, in any size, at any moment.
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol, in correct Devanagari with every matra and conjunct correct.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. In this clip the second phrase contains the same word twice and is therefore rendered COMPLETELY UNIFORM in bold white with NO golden word. The ONLY golden word in this clip is "याद" in the first phrase. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time, perfectly synced with the voiceover. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean crisp flat overlay typography on a dark technical background. Never photorealistic. NO fire, NO flame, NO sparks, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: completely empty background. Nothing at all.

ANIMATION TIMELINE:
0.0–4.8 s — first phrase "तो बस इतना याद रखो" pops in fully sharp at the top of the frame, with the single word "याद" styled golden in place inside the sentence, and holds, then disappears completely at 4.8 s.
4.8–5.0 s — no phrase is visible at all; the screen shows only the plain background.
5.0–10.0 s — second phrase "एक क्षार बदला, एक अमीनो अम्ल बदला," pops in fully sharp, completely uniform in bold white with no golden word, and holds to the very end of the clip.
Nothing else appears, moves or changes at any moment. The area below the script text is plain empty background for the whole clip.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "तो बस इतना याद रखो"
2. "एक क्षार बदला, एक अमीनो अम्ल बदला,"

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word beyond what is written, a third "एक", a third "बदला", a repeated key word, a keyword written as a separate line, invented labels, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken Devanagari conjuncts, missing or misplaced matras, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, a new logo, a duplicated logo, a redrawn logo, a moved logo, a watermark of any kind, text or diagram overlapping either top corner, any red blood cell, any sickle cell, any crescent shape, any blood vessel, any haemoglobin molecule, any chain of beads, any fibre, any DNA strand, any letter sequence such as GAG or GTG, any equation, any genotype line, any arrow, any shape, any icon or illustration of any kind, any label plate, a golden word in the second phrase, a red blood cell with a visible nucleus
```

---

**Segment 19 of 21** — DIAGRAM (normal cell + sickle cell, side by side)

```
VIDEO PROMPT — SEGMENT 19 OF 21

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

VOICEOVER NARRATION (spoken audio): an energetic, warm Indian male biology teacher voice speaks this exact Hinglish narration during the clip — nothing more, nothing less. The same script also appears on screen word for word, one phrase at a time:
"और लाल रक्त कोशिका का आकार बदल गया। यही सिकल सेल एनीमिया का कारण बनता है।"

AUDIO: only the voiceover above. No background music. Only very soft whoosh and pop sounds on text animations are allowed.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, starting close to the top edge. The diagram sits directly below the script text and fills the space between the text and the invisible middle line, so the top half never looks empty. The lowest part of the diagram stops with a clear visible gap above the invisible middle line and never touches it; if it does not fit, make it smaller. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

LOGO SAFE AREA: keep the top-left corner and the top-right corner of the frame completely clear of script text, diagram, equation, labels and any moving element for the whole clip — only the background itself shows there. Do not draw, copy, move, recreate or animate any logo, wordmark, badge or watermark anywhere in the frame; the logo already present on the supplied background must stay exactly where it is, unchanged.

3D RENDER QUALITY (CRITICAL — THIS MAKES THE DIAGRAM LOOK THREE DIMENSIONAL):
The diagram is a real three dimensional object rendered in depth, not a flat drawing.
- CAMERA: a fixed three-quarter view from slightly above the cells, so the viewer looks slightly down at them and can clearly read their roundness. Never a flat straight-on front view.
- PERSPECTIVE: circles that run around the cells appear as flattened ellipses because of the viewing angle, becoming flatter near the top and bottom and rounder near the middle. Nothing is drawn as a plain flat circle.
- DEPTH: the parts nearest the camera are brighter, thicker and sharper. The parts on the far side are noticeably dimmer, thinner and softer. This difference is clear and obvious.
- LIGHTING: one soft cool rim light along the upper left edge and a gentle ambient fill, giving a rounded sculpted look with a soft falloff toward the lower right.
- MATERIAL: a smooth glossy slightly wet-looking surface with a faint specular highlight near the upper left, and a soft inner glow.
- FORESHORTENING: the fibre rods inside the sickled cell that point toward the camera look shorter and thicker, and the ones pointing away look longer and thinner. They are never all the same length on screen.
- MOTION: each cell turns very slowly and steadily around its vertical axis so the depth reads clearly. Neither cell ever wobbles, squashes, deforms or changes size once settled.

DIAGRAM SPECIFICATION (build exactly this, nothing else):
- THE NORMAL RED BLOOD CELL (on the left): one three dimensional biconcave disc, uniform bright red all over, glossy and rounded, seen from a three-quarter angle from slightly above. It is circular seen from above, with a shallow dimple pressed into BOTH of its flat faces so that the middle looks slightly paler and thinner — the pale centre is thinness only. It is NOT a bowl, NOT a doughnut, and it has NO hole of any kind through the middle. It contains NO nucleus, NO dark central blob, NO organelle and NO inner circle. Its interior is smooth and uniformly red with nothing drawn inside it. Its rim is thick and softly rounded. It turns very slowly and steadily.
- THE SICKLE CELL (on the right, the same size as the normal cell): one three dimensional crescent-shaped cell, the same bright red colour as the normal cell, clearly POINTED and sharp at BOTH ends, with one concave inner edge and one convex outer edge. It is not a banana, not a smooth crescent moon with blunt rounded ends, not a star, not spiky, not blue and not grey. Inside it, running lengthwise along its long axis, are several long straight stiff blue-violet fibre rods bundled parallel to each other, clearly visible through the cell and stretching the cell out from the inside. The rods are straight and rigid, never curly, never tangled, never crossing each other. It turns very slowly and steadily and contains NO nucleus.
- LABELS: this clip has NO labels at all. No plate, no chip, no tag, no number, no leader line and no floating letter exists anywhere. Never invent a label.
- The two cells sit side by side at the same height, with clear space between them, both fully inside the space between the script text and the invisible middle line.

DIAGRAM TIMING SYNC (CRITICAL): every object appears at the exact moment its name is visible in the written phrase on screen, and never a frame before. Once an object appears it stays to the end of the clip.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE. Every word appears exactly the number of times it is written.
- EXACT COUNT: the word "आकार" appears exactly ONCE in total in this clip, inside the first phrase, and nowhere else, in any size, at any moment.
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol, in correct Devanagari with every matra and conjunct correct.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. In this clip the ONLY golden word is "आकार" in the first phrase. The second phrase is rendered completely uniform in bold white with no golden word at all. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time, perfectly synced with the voiceover. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean, glossy, textbook-style biology illustration rendered in three dimensions — smooth shapes, flat bright colours, soft even glow, like a modern NCERT diagram built in 3D. Never photorealistic. NO fire, NO flame, NO burning, NO spark, NO ember, NO explosion, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: completely empty background. Nothing at all.

ANIMATION TIMELINE:
0.0–4.8 s — first phrase "और लाल रक्त कोशिका का आकार बदल गया।" pops in fully sharp at the top of the frame, with the single word "आकार" styled golden in place inside the sentence, and holds, then disappears completely at 4.8 s.
1.2 s — exactly as the words "लाल रक्त कोशिका" are visible on screen, the normal red blood cell pops in on the left side of the space below the script text, fully formed and biconcave from the first visible frame, and begins its very slow steady turn. It holds to the end of the clip.
3.6 s — exactly as the words "बदल गया" are visible on screen, the sickle cell pops in on the right side, already fully formed as a pointed-ended crescent with its blue-violet fibre rods inside, and begins its very slow steady turn. It holds to the end of the clip.
4.8–5.0 s — no phrase is visible at all; the two cells stay on screen unchanged.
5.0–10.0 s — second phrase "यही सिकल सेल एनीमिया का कारण बनता है।" pops in fully sharp, completely uniform in bold white, and holds to the very end of the clip.
Throughout, both cells only turn slowly in place. Nothing moves, resizes, morphs or changes colour, and no new object appears after 3.6 s.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "और लाल रक्त कोशिका का आकार बदल गया।"
2. "यही सिकल सेल एनीमिया का कारण बनता है।"

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, invented labels, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken Devanagari conjuncts, missing or misplaced matras, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, a new logo, a duplicated logo, a redrawn logo, a moved logo, a watermark of any kind, text or diagram overlapping either top corner, a red blood cell with a visible nucleus, a dark blob or inner circle drawn inside either cell, a red blood cell drawn as a flat two dimensional circle, a ring or doughnut with a hole through the middle, a bowl-shaped cell with a dimple on only one face, a sickle cell drawn as a smooth banana with rounded ends, a crescent moon with blunt ends, a star-shaped or spiky cell, a blue, purple, grey or colourless red blood cell, curly or tangled fibres inside the sickle cell, fibres drawn outside the cells, a third cell, a whole field of cells, every cell drawn sickled, a straight-on front view with no depth, a flat line drawing, a squashed or wobbling cell, the normal red blood cell appearing before 1.2 seconds, the sickle cell appearing before 3.6 seconds, any label plate, any chip, any callout, any leader line, any equation, any letter sequence such as GAG or GTG, any genotype line, any DNA strand, any blood vessel, a golden word in the second phrase, a family tree, a pedigree chart, a Punnett square, sex chromosome symbols, an X or Y chromosome
```

---

**Segment 20 of 21** — TEXT_ONLY (the two cells fade out 0–2.0 s)

```
VIDEO PROMPT — SEGMENT 20 OF 21

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

VOICEOVER NARRATION (spoken audio): an energetic, warm Indian male biology teacher voice speaks this exact Hinglish narration during the clip — nothing more, nothing less. The same script also appears on screen word for word, one phrase at a time:
"बस इतना समझ लिया, तो परीक्षा में चार नंबर पक्के। इसे परीक्षा में कैसे लिखना है,"

AUDIO: only the voiceover above. No background music. Only very soft whoosh and pop sounds on text animations are allowed.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, filling the width, starting close to the top edge, large enough to fill the upper area comfortably. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

LOGO SAFE AREA: keep the top-left corner and the top-right corner of the frame completely clear of script text, diagram, equation, labels and any moving element for the whole clip — only the background itself shows there. Do not draw, copy, move, recreate or animate any logo, wordmark, badge or watermark anywhere in the frame; the logo already present on the supplied background must stay exactly where it is, unchanged.

NO DIAGRAM IN THIS CLIP AFTER THE OPENING FADE (CRITICAL): the only objects in this clip are the two cells carried over from the previous clip, described below, and they leave early. Apart from them there is NO three dimensional object of any kind — no other red blood cell, no other sickle cell, no blood vessel, no haemoglobin molecule, no DNA strand, no chain of beads, no fibre, no arrow, no icon and no illustration anywhere in the frame at any moment. From 2.0 seconds onward the only things on screen are the script text and the plain background. Do not invent, add or imagine any diagram, object or graphic.

CARRIED-OVER OBJECTS: the scene from the previous clip — one normal biconcave red blood cell on the left, uniform bright red with a shallow dimple on both faces, no hole and no nucleus, and one pointed-ended red crescent sickle cell on the right with straight blue-violet fibre rods inside it — is already present at the very first frame and does not fade in again. Both cells simply fade out smoothly together, shrinking very slightly, and are completely gone by 2.0 seconds, leaving plain empty background beneath the script text for the rest of the clip. Neither cell changes shape, colour or position while fading, and neither is ever redrawn afterwards.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE. Every word appears exactly the number of times it is written.
- EXACT COUNT: the word "परीक्षा" appears exactly TWICE in total in this clip — once inside the second phrase and once inside the third phrase. Nowhere else, in any size, at any moment, and never twice inside the same phrase.
- The word "चार" is written in Devanagari letters. No digit, no numeral and no figure appears anywhere on screen at any moment.
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol, in correct Devanagari with every matra and conjunct correct.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. In this clip the ONLY golden word is "समझ" in the first phrase. The second phrase and the third phrase are rendered completely uniform in bold white with no golden word at all, because the word "परीक्षा" is shared between them. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time, perfectly synced with the voiceover. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean crisp flat overlay typography on a dark technical background, with the two carried-over cells rendered as clean glossy textbook-style three dimensional biology illustration during the opening fade only. Never photorealistic. NO fire, NO flame, NO sparks, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: continuing exactly from the previous clip — two small cells side by side below where the script text appears, a normal biconcave red blood cell on the left and a pointed-ended red sickle cell with blue-violet fibres on the right. Nothing else.

ANIMATION TIMELINE:
0.0 s — both carried-over cells are already on screen from the very first frame and immediately begin fading out together.
0.0–3.3 s — first phrase "बस इतना समझ लिया," pops in fully sharp at the top of the frame, with the single word "समझ" styled golden in place inside the sentence, and holds, then disappears completely at 3.3 s.
0.0–2.0 s — both cells fade out smoothly and are completely gone by 2.0 s, leaving plain empty background below the script text for the rest of the clip.
3.3–3.5 s — no phrase is visible at all.
3.5–6.6 s — second phrase "तो परीक्षा में चार नंबर पक्के।" pops in fully sharp, completely uniform in bold white, and holds, then disappears completely at 6.6 s.
6.6–6.8 s — no phrase is visible at all.
6.8–10.0 s — third phrase "इसे परीक्षा में कैसे लिखना है," pops in fully sharp, completely uniform in bold white, and holds to the very end of the clip.
Nothing else appears, moves or changes at any moment. The area below the script text is plain empty background from 2.0 s onward.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "बस इतना समझ लिया,"
2. "तो परीक्षा में चार नंबर पक्के।"
3. "इसे परीक्षा में कैसे लिखना है,"

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, any digit or numeral of any kind, the figure 4, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a third "परीक्षा", two copies of "परीक्षा" inside one phrase, a repeated key word, a keyword written as a separate line, invented labels, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken Devanagari conjuncts, missing or misplaced matras, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, a new logo, a duplicated logo, a redrawn logo, a moved logo, a watermark of any kind, text or diagram overlapping either top corner, either cell still visible after 2.0 seconds, a cell reappearing later in the clip, a third cell, a new red blood cell, a red blood cell with a visible nucleus, a red blood cell drawn as a flat circle or a ring with a hole, a sickle cell drawn as a smooth banana with rounded ends, a blue or grey red blood cell, any blood vessel, any DNA strand, any equation, any genotype line, any letter sequence such as GAG or GTG, any label plate, any chip, any callout, any leader line, any arrow, a golden word in the second phrase, a golden word in the third phrase, a family tree, a pedigree chart, a Punnett square, sex chromosome symbols, an X or Y chromosome
```

---

**Notes / assumptions**
- Seg 20 uses **"चार"** in Devanagari (the digit-swap I flagged in the plan) — the NEGATIVE explicitly bans any numeral so Veo can't "helpfully" print `4`. Confirm if you'd rather keep `4`.
- Seg 19's diagram is pinned to your reference frames: uniform red biconcave disc (no nucleus, no hole) and a pointed-ended red crescent with straight blue-violet fibre rods — the two errors most likely to slip through.
- Seg 17 and Seg 20 both open with a carried-over element fading; their `SCREEN AT START` matches Seg 16 (`HbA HbS`) and Seg 19 (two cells) exactly.
- Golden-word budget: one per segment (लक्षण / याद / आकार / समझ), everything sharing a repeated word rendered uniform.

Generate **Segment 17 alone first** and check the carried-line fade and Devanagari matras before running 18–20.

I read the three reference frames — they're accurate to the brief (biconcave with dimple, no nucleus, red sickle with pointed ends, blue HbS fibre rods, O₂ gauge dropping *before* the shape change). They're a good visual anchor for the diagram segments, but **Segment 21 is TEXT_ONLY**, so they don't feed into it directly.

**One blocker first:** the plan you gave me is **21 segments total** (21 × 10 s = 210 s, and Seg 21 is the closing "स्क्रीनशॉट लेना मत भूलना" beat, ending on empty background because the answer card is added in edit). **Segments 22, 23 and 24 do not exist in the plan.** So below is the full Segment 21 prompt. If you've since extended the script past 210 s, paste the new lines for 22–24 and I'll write them in the same order.

---

## SEGMENT 21 OF 21

```
VIDEO PROMPT — SEGMENT 21 OF 21

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

VOICEOVER NARRATION (spoken audio): an energetic, warm Indian male biology teacher voice speaks this exact Hinglish narration during the clip — nothing more, nothing less. The same script also appears on screen word for word, one phrase at a time:
"इसका उत्तर आपकी स्क्रीन पर आएगा। स्क्रीनशॉट लेना मत भूलना।"

AUDIO: only the voiceover above. No background music. Only very soft whoosh and pop sounds on text animations are allowed.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, filling the width, starting close to the top edge, large enough to fill the upper area comfortably. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

LOGO SAFE AREA: keep the top-left corner and the top-right corner of the frame completely clear of script text, diagram, equation, labels and any moving element for the whole clip — only the background itself shows there. Do not draw, copy, move, recreate or animate any logo, wordmark, badge or watermark anywhere in the frame; the logo already present on the supplied background must stay exactly where it is, unchanged.

NO DIAGRAM IN THIS CLIP (CRITICAL): this clip contains NO three dimensional object of any kind. There is no red blood cell, no sickle cell, no biconcave disc, no capillary, no blood vessel, no haemoglobin molecule, no protein chain, no DNA strand, no fibre, no rod, no oxygen dot, no gauge, no arrow, no shape, no icon and no illustration anywhere in the frame at any moment. The only things on screen are the script text and the plain background. Do not invent, add or imagine any diagram, object or graphic. The space below the script text stays as plain empty background.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE. Every word appears exactly the number of times it is written.
- EXACT COUNT: the word "स्क्रीन" appears exactly ONCE in total in this clip, inside the first phrase only, and nowhere else in any size at any moment.
- EXACT COUNT: the word "स्क्रीनशॉट" appears exactly ONCE in total in this clip, inside the second phrase only. It is a different, longer word from "स्क्रीन" and the two are never mixed up, never merged, never swapped and never written a second time.
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol, in correct Devanagari script with every matra attached to the correct letter.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated.
In this clip: in the FIRST phrase the single word "उत्तर" is the golden key word, styled in place inside the sentence and never written again anywhere. The SECOND phrase is rendered COMPLETELY UNIFORM in bold white with NO golden word.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time, perfectly synced with the voiceover. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean crisp flat overlay typography on a dark technical background. Never photorealistic. NO fire, NO flame, NO sparks, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: completely empty background. Nothing at all.

ANIMATION TIMELINE:
0.0 s — the frame is completely empty except for the supplied background.
0.0–4.8 s — the first phrase "इसका उत्तर आपकी स्क्रीन पर आएगा।" is on screen at the very top of the frame, fully sharp from its first visible frame, on at most three short centred lines. The single word "उत्तर" is golden in place inside the sentence; every other word is bold white.
4.8 s — the first phrase disappears completely in one clean fade.
4.8–5.0 s — a tiny gap with no phrase on screen at all.
5.0–10.0 s — the second phrase "स्क्रीनशॉट लेना मत भूलना।" pops in at the very top of the frame, fully sharp from its first visible frame, rendered completely uniform in bold white with no golden word, and holds to the end of the clip.
Throughout the whole clip the area below the script text stays plain empty background, and the bottom half of the frame stays completely empty.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "इसका उत्तर आपकी स्क्रीन पर आएगा।"
2. "स्क्रीनशॉट लेना मत भूलना।"

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, invented labels, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, a new logo, a duplicated logo, a redrawn logo, a moved logo, a watermark of any kind, text or diagram overlapping either top corner, any red blood cell, any sickle cell, any crescent shape, any biconcave disc, any capillary or blood vessel, any haemoglobin molecule, any protein chain, any DNA strand, any fibre or rod, any oxygen dot, any gauge, any arrow, any shape, icon or illustration of any kind, any label plate, any equation, any genotype text such as HbA or HbS, any English letters, any Latin letters, any digits, a red blood cell with a visible nucleus, a red blood cell drawn as a flat ring or doughnut with a hole, a sickle cell drawn as a smooth banana or a blunt-ended crescent moon, a spiky or star-shaped cell, an answer card, a results card, a screenshot frame, a phone or camera icon
```

---

**On 22–24:** if you want the video to run past 21 segments, the natural additions would be an on-screen answer-card beat and a CTA — but the plan explicitly says the answer card is added in edit, not generated. Send me the extra script lines (and whether the answer card is now generated in-clip) and I'll write 22–24 with the same continuity chain: Seg 21 ends on **completely empty background**, so Seg 22 would open text-free.

## Rok raha hoon — segments 25–28 exist nahi karte

Plan me **total 21 segments** hain (21 × 10 sec = 210 sec, 3:30). Seg 21 hi last hai — "इसका उत्तर आपकी स्क्रीन पर आएगा। स्क्रीनशॉट लेना मत भूलना।" Uske aage koi content nahi hai, aur continuity chain bhi Seg 21 par khatam ("completely empty background, answer card is added in edit").

Agar main 25–28 likh doon to mujhe script khud invent karni padegi — aur skill ka pehla rule yahi hai ki har on-screen shabd word-for-word user ki script se aata hai. Invented segments = galat video.

**Teen possibilities, batao kaunsi:**

1. **Numbering ka confusion** — kya aap actually **last four segments (18, 19, 20, 21)** chahte the? Ye main abhi likh sakta hoon, full blocks, uploaded-background (§15) + LOGO SAFE AREA (§16) ke saath. Continuity Seg 17 ke end-state (completely empty background) se shuru hogi — jo aapke "previous segment's end state" wale instruction se match karta hai.

2. **Script extend hui hai** — agar aapke paas 21 ke baad ka naya Hinglish script text hai (Punnett square / 1:2:1 inheritance wala hissa abhi video me visual form me nahi hai, sirf text me), wo paste kar do. Main 22–28 ka segment map + full prompts bana doonga. Note: accuracy brief ka **Beat 5 (autosomal recessive, HbA HbS × HbA HbS → 1:2:1)** abhi sirf Seg 14–17 me text ke roop me hai, koi Punnett diagram nahi — extension ke liye ye sabse natural jagah hai.

3. **Aap chahte ho main 22–28 propose karoon** — main Punnett square + carrier + "exam me kaise likhna hai" ka expanded ending draft kar doonga (script + prompts), phir aap approve karo.

---

Do cheezein jo maine reference frames se pin kar li hain (jo bhi segments likhoonga, wahan use hongi):

- **Sickle cell rendering:** frame 3 ka crescent — dono ends **pointed**, ek concave edge + ek convex, andar **straight blue HbS fibre rods bundles** me. Frame 2 ka version blunt-ish tail ke saath hai → us type ko NEGATIVE me explicitly ban karoonga (`a sickle cell shaped like a banana or crescent moon with blunt rounded ends`).
- **Normal RBC:** frame 1 ka top-down doughnut-look **खतरनाak** hai — wo shallow dimple hai, hole nahi, lekin model isse ring bana deta hai. Isliye har RBC spec me "dimple on both faces, never a hole through the centre, never a ring or torus" + cross-section reference, aur NEGATIVE me `a red blood cell drawn as a ring or doughnut with a hole through the centre`, `a nucleus inside the red blood cell`.

Batao — **option 1 (Seg 18–21 abhi likhoon)** ya naya script paste karte ho?

Rukiye — segments 29–31 exist hi nahi.

**Plan me total 21 segments hain** (21 × 10 sec = 210 sec / 3:30). Segment map 21 par khatam ho jata hai (`इसका उत्तर आपकी स्क्रीन पर आएगा। / स्क्रीनशॉट लेना मत भूलना।`), aur continuity chain bhi "Seg 21 ends with: completely empty background" par band hota hai. 29–31 ke liye na script phrases hain, na type, na continuity end-state — main inhe invent karke likh doon to poora pack ka continuity chain jhooth ho jayega (ledger ka sabse mehnga bug).

Reference frames maine dekh liye — teenon accuracy-brief se match karte hain aur useful pins dete hain:
- Frame 1: biconcave disc, **koi nucleus nahi**, cross-section dumbbell (doughnut/hole nahi), lachili cell capillary me deform hoti hui — ye Seg 1–2 ke DIAGRAM SPEC ka exact reference hai.
- Frame 4 (dono versions): O₂ gauge "अधिक → कम" pehle girta hai, **phir** HbS lambi seedhi rods me polymerise hota hai, **tab** shape crescent banta hai — yani order (deoxygenation → polymer → shape) sahi hai. Sickle cell pointed-ends crescent, red, fibres andar — Seg 9–10 ka reference.

Ab bataiye kya chahiye — main turant likh doonga:

1. **Segments 19–21** (pack ke aakhri teen: before/after cells + परीक्षा wrap + screenshot CTA) — agar aapka matlab "last three" tha, ye sabse sambhavit hai.
2. **Koi aur teen** — jaise 9–11 (sickling + rigidity + blockage, sabse diagram-heavy) ya 5–7 (GAG→GTG → ग्लूटामिक→वेलिन → HbA→HbS, equation-solo chain).
3. **Script extend** — agar sach me 31 segments chahiye, to naya script content dijiye (Seg 22 onwards), main pehle plan extend karunga phir prompts.

Number bata dijiye, prompts full-block order me, uploaded-background (§15) + LOGO SAFE AREA (§16) ke saath ready hain.