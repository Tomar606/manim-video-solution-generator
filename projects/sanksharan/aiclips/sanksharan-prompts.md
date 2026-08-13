# संक्षारण — SEGMENT PROMPT SET

## 1. Total segment count

**18 segments × 10 sec = 180 sec (3:00)**

Word load: 18–22 Hindi words per segment, except the deliberate light ones (Seg 6 diagram beat, Seg 13 diagram beat, Seg 17 screenshot-pause beat).

---

## ⚠️ Route flag before you go further

This script is ~85% Hindi kinetic typography + list recaps. Veo/Flow renders Devanagari unreliably (conjuncts, `ँ` `ृ` matras, `विद्युत्` halant, `12वीं` digit+Devanagari mix) — and that's the one bug no prompt rule fixes. **Manim + Poppins renders all of this correctly by construction**, and 15 of 18 segments have zero animation Veo is uniquely good at. Recommend: Manim for all TEXT_ONLY + the word-equation, Veo only for Seg 6 / 11 / 13 if you want organic rust/coating visuals. Say the word and I'll plan it that way instead.

---

## 2. Segment map

| Seg | Phrases (exact words) | Type | Diagram |
|---|---|---|---|
| 1 | "एमपी बोर्ड कक्षा 12वीं के बच्चों!" · "ये सवाल 2025 में आ चुका है" | TEXT_ONLY | N |
| 2 | "और इस साल भी आपकी त्रैमासिक परीक्षा में आ सकता है।" · "और इस वीडियो के अंत तक" · "आप इसे पूरा याद करके," | TEXT_ONLY | N |
| 3 | "परीक्षा में सही तरीके से लिखना भी सीख जाओगे।" · "तो चलिए, सबसे पहले समझते हैं, संक्षारण किसे कहते हैं?" | TEXT_ONLY | N |
| 4 | "वायुमण्डल में उपस्थित गैसों तथा नमी के कारण" · "धातुओं के धीरे-धीरे अवांछित यौगिकों में बदलने की प्रक्रिया को" · "संक्षारण कहते हैं।" | TEXT_ONLY | N |
| 5 | "इसे याद रखने का आसान तरीका है" · **equation line:** "धातु + वायुमण्डल की गैसें + नमी = संक्षारण" | EQUATION_ONLY | N |
| 6 | "और इसका सबसे आसान उदाहरण है," · "लोहे में जंग लगना।" | DIAGRAM | **Y** — clean iron nail/bar → orange-brown rust spreading |
| 7 | "अब संक्षारण को प्रभावित करने वाले तीन कारक समझो।" · "पहला, धातु की प्रकृति," · "मतलब धातु जितनी अधिक क्रियाशील होगी," | TEXT_ONLY | N |
| 8 | "उस पर संक्षारण उतनी जल्दी होगा।" · "दूसरा, धातु में अशुद्धियाँ," · "मतलब धातु में अशुद्धियाँ होने पर संक्षारण अधिक तेजी से होगा।" | TEXT_ONLY | N |
| 9 | "तीसरा, वातावरण, मतलब हवा, नमी और कुछ गैसों की मौजूदगी" · "संक्षारण को बढ़ाती है।" · "बस, इन तीनों को याद रखो," | TEXT_ONLY | N |
| 10 | "धातु की प्रकृति, अशुद्धियाँ और वातावरण।" · "अब समझते हैं संक्षारण से बचाव के तीन उपाय।" | TEXT_ONLY (recap phrase itself is the 3-line list — no label plates) | N |
| 11 | "पहला, रोधिका स्थापित करना," · "मतलब लोहे पर पेंट, ग्रीस या तेल की परत लगाकर" · "उसे हवा और नमी से बचाना।" | DIAGRAM | **Y** — iron bar + one protective coating layer sliding over it (no labels) |
| 12 | "दूसरा, समर्पित बचाव," · "मतलब लोहे से अधिक क्रियाशील धातु की तह चढ़ाना," · "जो पहले नष्ट होकर लोहे को बचाती है।" | TEXT_ONLY | N |
| 13 | "इसका उदाहरण है गैल्वेनीकरण," · "जिसमें लोहे पर जिंक की तह चढ़ाई जाती है।" | DIAGRAM | **Y** — iron bar getting a bluish-grey zinc coat |
| 14 | "तीसरा, विद्युत् प्लेटिंग," · "मतलब जिंक, निकिल या क्रोमियम जैसी धातुओं की परत चढ़ाकर" · "धातु को सुरक्षित करना।" | TEXT_ONLY | N |
| 15 | "बच्चों, बस इतना याद रख लिया," · "तो परीक्षा में संक्षारण का ये पूरा उत्तर कभी नहीं भूलोगे।" | TEXT_ONLY | N |
| 16 | "अब इसे परीक्षा में कैसे लिखना है," · "इसका पूरा उत्तर आपकी स्क्रीन पर आ जाएगा।" | TEXT_ONLY | N |
| 17 | "इसे सेव कर लेना" · "और इसका स्क्रीनशॉट लेना मत भूलना।" | TEXT_ONLY (light on purpose — screenshot pause) | N |
| 18 | "और ऐसे ही आसान और मजेदार तरीके से पढ़ने के लिए" · "अरिहान के उन्नति बैच से जुड़ो।" | TEXT_ONLY | N |

---

## 3. End-state chain

- **Seg 1 ends with:** "ये सवाल 2025 में आ चुका है" on screen, nothing else.
- **Seg 2 ends with:** "आप इसे पूरा याद करके," on screen, nothing else.
- **Seg 3 ends with:** "तो चलिए, सबसे पहले समझते हैं, संक्षारण किसे कहते हैं?" on screen, nothing else.
- **Seg 4 ends with:** "संक्षारण कहते हैं।" on screen, nothing else.
- **Seg 5 ends with:** the single equation line "धातु + वायुमण्डल की गैसें + नमी = संक्षारण" on screen; script phrase already gone. **(Only place a symbol may appear.)**
- **Seg 6 ends with:** "लोहे में जंग लगना।" on screen; rust diagram fades out completely by 9.0 s → clean background below the text at 10.0 s.
- **Seg 7 ends with:** "मतलब धातु जितनी अधिक क्रियाशील होगी," on screen, nothing else.
- **Seg 8 ends with:** "मतलब धातु में अशुद्धियाँ होने पर संक्षारण अधिक तेजी से होगा।" on screen, nothing else.
- **Seg 9 ends with:** "बस, इन तीनों को याद रखो," on screen, nothing else.
- **Seg 10 ends with:** "अब समझते हैं संक्षारण से बचाव के तीन उपाय।" on screen, nothing else.
- **Seg 11 ends with:** "उसे हवा और नमी से बचाना।" on screen; coated-bar diagram fades out by 9.0 s → clean background below the text.
- **Seg 12 ends with:** "जो पहले नष्ट होकर लोहे को बचाती है।" on screen, nothing else.
- **Seg 13 ends with:** "जिसमें लोहे पर जिंक की तह चढ़ाई जाती है।" on screen; galvanised-bar diagram fades out by 9.0 s → clean background below the text.
- **Seg 14 ends with:** "धातु को सुरक्षित करना।" on screen, nothing else.
- **Seg 15 ends with:** "तो परीक्षा में संक्षारण का ये पूरा उत्तर कभी नहीं भूलोगे।" on screen, nothing else.
- **Seg 16 ends with:** "इसका पूरा उत्तर आपकी स्क्रीन पर आ जाएगा।" on screen, nothing else.
- **Seg 17 ends with:** "और इसका स्क्रीनशॉट लेना मत भूलना।" on screen, nothing else.
- **Seg 18 ends with:** "अरिहान के उन्नति बैच से जुड़ो।" on screen, nothing else.

Every diagram fades before its own clip ends, so each next segment's SCREEN AT START = empty background — no cross-clip carry-over to break.

---

## Step-1 changes I made (words untouched, marks only)

1. **em-dash `—` → comma** everywhere (`पहला—धातु` → `पहला, धातु`). Dashes render as stray marks (bug-ledger #12 family).
2. **`3 उपाय` → `तीन उपाय`** — matches spoken narration and the `तीन कारक` already in the script.
3. **Quote marks around `‘उन्नति बैच’` dropped** — curly quotes are a stray-punctuation magnet.
4. `12वीं` / `2025` kept as digits (natural, and they're content not layout numbers).

## Repeat-word locks already identified (will become EXACT COUNT lines in Step 3)

- Seg 4 — `धीरे-धीरे` (hyphen + doubled word) → whole phrase UNIFORM white, **no golden word**
- Seg 7 — `धातु` ×2
- Seg 8 — `धातु` ×2, `अशुद्धियाँ` ×2, `संक्षारण` ×2 → all three phrases UNIFORM, no golden word
- Seg 12 — `लोहे` ×2
- Seg 5 — `+` ×2 and `=` inside the equation → phrase UNIFORM, symbols exist **only** inside the equation line

## Three things to confirm before Step 3

1. **`अरिहान` spelling** — brand is *Arivihan*, so on screen it should probably be **`अरिविहान`**. Confirm which one goes on screen.
2. **Seg 16's "पूरा उत्तर स्क्रीन पर"** — I've planned it as text-only; the actual written answer card is an editing overlay, not a generated frame (a full answer inside the clip would blow the top-half rule). Correct?
3. **Diagrams at 6 / 11 / 13** — enough, or do you also want a plating-cell visual on Seg 14?


Read the reference frame — rust palette confirmed (orange-brown flaky, steel-grey metal); that frame is a landscape answer-card poster, so it informs colour only, not layout.

**Assumptions I resolved myself (no questions asked):** brand spelling doesn't occur in Segments 1–4, so it's deferred; Segments 1–4 are all TEXT_ONLY per the plan, so no diagram blocks anywhere; digits (`12वीं`, `2025`) are treated as content and their phrases are rendered fully UNIFORM white with no golden word, since a digit-plus-Devanagari cluster behaves like a standalone-symbol phrase and breaks golden styling; Segment 3's second phrase contains `हैं` twice and Segment 4's second contains `धीरे-धीरे`, so both are UNIFORM with EXACT COUNT locks.

---

```
VIDEO PROMPT — SEGMENT 1 OF 18

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

AUDIO: this clip is completely SILENT. There is no voiceover, no narration, no speech, no singing, no music, no sound effects and no ambient sound of any kind. No voice is generated at any moment. The audio track is empty. The spoken narration is added separately in editing from a different source.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, filling the width, starting close to the top edge, large enough to fill the upper area comfortably. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

NO DIAGRAM IN THIS CLIP (CRITICAL): this clip contains NO three dimensional object of any kind. There is no metal bar, no iron nail, no test tube, no rust, no beaker, no droplet, no arrow, no coating layer, no shape, no icon and no illustration anywhere in the frame at any moment. The only things on screen are the script text and the plain background. Do not invent, add or imagine any diagram, object or graphic. The space below the script text stays as plain empty background.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE. Every word appears exactly the number of times it is written.
- The text is Hindi written in the Devanagari script. Every letter, every matra, every conjunct and every nukta is rendered exactly as written, correctly joined and correctly positioned. Never substitute a Latin letter, never transliterate, never leave an empty box, never drop a matra and never break a conjunct.
- EXACT COUNT: the digits "12" appear exactly ONCE in this whole clip, inside the first phrase, joined directly to वीं with no space, as "12वीं". Nowhere else, in any size, at any moment.
- EXACT COUNT: the digits "2025" appear exactly ONCE in this whole clip, inside the second phrase. Nowhere else, in any size, at any moment.
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated. In this clip BOTH phrases contain digits and are therefore rendered COMPLETELY UNIFORM in bold white, with NO golden word anywhere in this clip.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time, perfectly synced with the intended narration. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean crisp flat overlay typography on a dark technical background. Never photorealistic. NO fire, NO flame, NO sparks, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: completely empty background. Nothing at all.

ANIMATION TIMELINE:
- 0.0 s: the background is already fully visible, unchanged and static.
- 0.0–4.8 s: the first phrase "एमपी बोर्ड कक्षा 12वीं के बच्चों!" pops in fully sharp at the very top of the frame in uniform bold white, on at most three short centred lines, and holds perfectly still.
- 4.8 s: the first phrase disappears completely in a single clean fade.
- 4.8–5.0 s: a short gap with no phrase on screen at all.
- 5.0–10.0 s: the second phrase "ये सवाल 2025 में आ चुका है" pops in fully sharp in the same place, in uniform bold white, and holds perfectly still to the very last frame.
- The lower half of the frame contains nothing but the unchanged background from the first frame to the last.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "एमपी बोर्ड कक्षा 12वीं के बच्चों!"
2. "ये सवाल 2025 में आ चुका है"

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, invented labels, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, any metal bar, iron nail, test tube, beaker, water droplet, rust patch, coating layer, arrow, shape, icon or illustration of any kind, any label plate, equations, a golden word in either phrase, empty boxes or tofu squares instead of Devanagari letters, broken or separated conjuncts, missing or misplaced matras, Latin transliteration of the Hindi text, any voiceover, any narration, any spoken words, any human voice, any singing, background music, sound effects, an automatic caption, an auto-generated subtitle, a burnt-in subtitle bar, closed captions, a transcript line, any text that appears because speech was generated, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed
```

---

```
VIDEO PROMPT — SEGMENT 2 OF 18

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

AUDIO: this clip is completely SILENT. There is no voiceover, no narration, no speech, no singing, no music, no sound effects and no ambient sound of any kind. No voice is generated at any moment. The audio track is empty. The spoken narration is added separately in editing from a different source.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, filling the width, starting close to the top edge, large enough to fill the upper area comfortably. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

NO DIAGRAM IN THIS CLIP (CRITICAL): this clip contains NO three dimensional object of any kind. There is no metal bar, no iron nail, no test tube, no rust, no beaker, no droplet, no arrow, no coating layer, no shape, no icon and no illustration anywhere in the frame at any moment. The only things on screen are the script text and the plain background. Do not invent, add or imagine any diagram, object or graphic. The space below the script text stays as plain empty background.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE. Every word appears exactly the number of times it is written.
- The text is Hindi written in the Devanagari script. Every letter, every matra, every conjunct and every nukta is rendered exactly as written, correctly joined and correctly positioned. Never substitute a Latin letter, never transliterate, never leave an empty box, never drop a matra and never break a conjunct.
- EXACT COUNT: the word "और" appears exactly TWICE in total in this clip — once as the first word of the first phrase and once as the first word of the second phrase. It never appears a third time, never inside the third phrase, and never anywhere else in any size at any moment.
- EXACT COUNT: the word "इस" appears exactly TWICE in total in this clip — once inside the first phrase and once inside the second phrase. Nowhere else.
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated. In this clip: the FIRST phrase has exactly ONE golden word, the single word "परीक्षा", styled in place inside the sentence; the SECOND phrase is COMPLETELY UNIFORM bold white with NO golden word; the THIRD phrase has exactly ONE golden word, the single word "याद", styled in place inside the sentence. No other word anywhere in this clip is golden.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time, perfectly synced with the intended narration. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean crisp flat overlay typography on a dark technical background. Never photorealistic. NO fire, NO flame, NO sparks, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: completely empty background. Nothing at all. The phrase from the previous clip is already gone before this clip begins.

ANIMATION TIMELINE:
- 0.0 s: the background is already fully visible, unchanged and static.
- 0.0–3.3 s: the first phrase "और इस साल भी आपकी त्रैमासिक परीक्षा में आ सकता है।" pops in fully sharp at the very top of the frame, on at most three short centred lines, with the single word "परीक्षा" golden in place inside the sentence, and holds perfectly still.
- 3.3 s: the first phrase disappears completely in a single clean fade.
- 3.3–3.5 s: a short gap with no phrase on screen at all.
- 3.5–6.6 s: the second phrase "और इस वीडियो के अंत तक" pops in fully sharp in the same place, in uniform bold white with no golden word, and holds perfectly still.
- 6.6 s: the second phrase disappears completely in a single clean fade.
- 6.6–6.8 s: a short gap with no phrase on screen at all.
- 6.8–10.0 s: the third phrase "आप इसे पूरा याद करके," pops in fully sharp in the same place, with the single word "याद" golden in place inside the sentence, and holds perfectly still to the very last frame.
- The lower half of the frame contains nothing but the unchanged background from the first frame to the last.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "और इस साल भी आपकी त्रैमासिक परीक्षा में आ सकता है।"
2. "और इस वीडियो के अंत तक"
3. "आप इसे पूरा याद करके,"

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, the word परीक्षा written a second time, the word याद written a second time, a third "और", invented labels, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, any metal bar, iron nail, test tube, beaker, water droplet, rust patch, coating layer, arrow, shape, icon or illustration of any kind, any label plate, equations, a golden word in the second phrase, more than one golden word in any phrase, empty boxes or tofu squares instead of Devanagari letters, broken or separated conjuncts, missing or misplaced matras, Latin transliteration of the Hindi text, any voiceover, any narration, any spoken words, any human voice, any singing, background music, sound effects, an automatic caption, an auto-generated subtitle, a burnt-in subtitle bar, closed captions, a transcript line, any text that appears because speech was generated, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed
```

---

```
VIDEO PROMPT — SEGMENT 3 OF 18

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

AUDIO: this clip is completely SILENT. There is no voiceover, no narration, no speech, no singing, no music, no sound effects and no ambient sound of any kind. No voice is generated at any moment. The audio track is empty. The spoken narration is added separately in editing from a different source.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, filling the width, starting close to the top edge, large enough to fill the upper area comfortably. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

NO DIAGRAM IN THIS CLIP (CRITICAL): this clip contains NO three dimensional object of any kind. There is no metal bar, no iron nail, no test tube, no rust, no beaker, no droplet, no arrow, no coating layer, no shape, no icon and no illustration anywhere in the frame at any moment. The only things on screen are the script text and the plain background. Do not invent, add or imagine any diagram, object or graphic. The space below the script text stays as plain empty background.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE beyond what is written. Every word appears exactly the number of times it is written.
- EXACT COUNT: in the second phrase the word "हैं" is written exactly TWICE, once in "समझते हैं," and once in "कहते हैं?", exactly as given. It never appears a third time, and it never appears in the first phrase, in any size, at any moment.
- The text is Hindi written in the Devanagari script. Every letter, every matra, every conjunct and every nukta is rendered exactly as written, correctly joined and correctly positioned. The conjunct in "संक्षारण" is rendered as one correctly formed cluster. Never substitute a Latin letter, never transliterate, never leave an empty box, never drop a matra and never break a conjunct.
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated. In this clip: the FIRST phrase has exactly ONE golden word, the single word "सही", styled in place inside the sentence; the SECOND phrase contains the same word twice and is therefore rendered COMPLETELY UNIFORM bold white with NO golden word at all.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time, perfectly synced with the intended narration. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean crisp flat overlay typography on a dark technical background. Never photorealistic. NO fire, NO flame, NO sparks, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: completely empty background. Nothing at all. The phrase from the previous clip is already gone before this clip begins.

ANIMATION TIMELINE:
- 0.0 s: the background is already fully visible, unchanged and static.
- 0.0–4.8 s: the first phrase "परीक्षा में सही तरीके से लिखना भी सीख जाओगे।" pops in fully sharp at the very top of the frame, on at most three short centred lines, with the single word "सही" golden in place inside the sentence, and holds perfectly still.
- 4.8 s: the first phrase disappears completely in a single clean fade.
- 4.8–5.0 s: a short gap with no phrase on screen at all.
- 5.0–10.0 s: the second phrase "तो चलिए, सबसे पहले समझते हैं, संक्षारण किसे कहते हैं?" pops in fully sharp in the same place, completely uniform bold white with no golden word, on at most three short centred lines, and holds perfectly still to the very last frame.
- The lower half of the frame contains nothing but the unchanged background from the first frame to the last.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "परीक्षा में सही तरीके से लिखना भी सीख जाओगे।"
2. "तो चलिए, सबसे पहले समझते हैं, संक्षारण किसे कहते हैं?"

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, the word सही written a second time, the word संक्षारण written a second time, a third "हैं", invented labels, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, any metal bar, iron nail, test tube, beaker, water droplet, rust patch, coating layer, arrow, shape, icon or illustration of any kind, any label plate, equations, a golden word in the second phrase, more than one golden word in any phrase, empty boxes or tofu squares instead of Devanagari letters, broken or separated conjuncts, missing or misplaced matras, Latin transliteration of the Hindi text, any voiceover, any narration, any spoken words, any human voice, any singing, background music, sound effects, an automatic caption, an auto-generated subtitle, a burnt-in subtitle bar, closed captions, a transcript line, any text that appears because speech was generated, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed
```

---

```
VIDEO PROMPT — SEGMENT 4 OF 18

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

AUDIO: this clip is completely SILENT. There is no voiceover, no narration, no speech, no singing, no music, no sound effects and no ambient sound of any kind. No voice is generated at any moment. The audio track is empty. The spoken narration is added separately in editing from a different source.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, filling the width, starting close to the top edge, large enough to fill the upper area comfortably. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

NO DIAGRAM IN THIS CLIP (CRITICAL): this clip contains NO three dimensional object of any kind. There is no metal bar, no iron nail, no test tube, no rust, no beaker, no droplet, no gas cloud, no arrow, no coating layer, no shape, no icon and no illustration anywhere in the frame at any moment. Even though the words describe gases, moisture and metals, NOTHING is ever drawn or illustrated. The only things on screen are the script text and the plain background. Do not invent, add or imagine any diagram, object or graphic. The space below the script text stays as plain empty background.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE beyond what is written. Every word appears exactly the number of times it is written.
- EXACT COUNT: in the second phrase the word "धीरे" is written exactly TWICE, joined by a single hyphen as "धीरे-धीरे", exactly as given. It never appears a third time, the hyphen appears exactly once, and neither the word nor the hyphen appears anywhere else in this clip in any size at any moment.
- EXACT COUNT: the word "संक्षारण" appears exactly ONCE in this whole clip, inside the third phrase. It never appears in the first or second phrase, and never a second time anywhere.
- The text is Hindi written in the Devanagari script. Every letter, every matra, every conjunct and every nukta is rendered exactly as written, correctly joined and correctly positioned. The conjuncts in "वायुमण्डल" and "संक्षारण" are rendered as correctly formed clusters. Never substitute a Latin letter, never transliterate, never leave an empty box, never drop a matra and never break a conjunct.
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated. In this clip: the FIRST phrase has exactly ONE golden word, the single word "नमी", styled in place inside the sentence; the SECOND phrase contains a hyphenated doubled word and is therefore rendered COMPLETELY UNIFORM bold white with NO golden word at all; the THIRD phrase is rendered COMPLETELY UNIFORM bold white with NO golden word at all.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time, perfectly synced with the intended narration. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean crisp flat overlay typography on a dark technical background. Never photorealistic. NO fire, NO flame, NO sparks, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: completely empty background. Nothing at all. The phrase from the previous clip is already gone before this clip begins.

ANIMATION TIMELINE:
- 0.0 s: the background is already fully visible, unchanged and static.
- 0.0–3.3 s: the first phrase "वायुमण्डल में उपस्थित गैसों तथा नमी के कारण" pops in fully sharp at the very top of the frame, on at most three short centred lines, with the single word "नमी" golden in place inside the sentence, and holds perfectly still.
- 3.3 s: the first phrase disappears completely in a single clean fade.
- 3.3–3.5 s: a short gap with no phrase on screen at all.
- 3.5–6.6 s: the second phrase "धातुओं के धीरे-धीरे अवांछित यौगिकों में बदलने की प्रक्रिया को" pops in fully sharp in the same place, completely uniform bold white with no golden word, and holds perfectly still.
- 6.6 s: the second phrase disappears completely in a single clean fade.
- 6.6–6.8 s: a short gap with no phrase on screen at all.
- 6.8–10.0 s: the third phrase "संक्षारण कहते हैं।" pops in fully sharp in the same place, completely uniform bold white with no golden word, and holds perfectly still to the very last frame.
- The lower half of the frame contains nothing but the unchanged background from the first frame to the last.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "वायुमण्डल में उपस्थित गैसों तथा नमी के कारण"
2. "धातुओं के धीरे-धीरे अवांछित यौगिकों में बदलने की प्रक्रिया को"
3. "संक्षारण कहते हैं।"

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, the word नमी written a second time, a third "धीरे", a second hyphen, the word संक्षारण written a second time, invented labels, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, any metal bar, iron nail, test tube, beaker, water droplet, water tank, gas cloud, rust patch, coating layer, arrow, shape, icon or illustration of any kind, a rusted nail, an orange-brown rust patch, a green corroded surface, green rust on iron, a smooth glossy rust coating, a golden or brassy metal coating, a chemical formula, Fe2O3, Fe3O4, FeO, any label plate, equations, a golden word in the second or third phrase, more than one golden word in any phrase, empty boxes or tofu squares instead of Devanagari letters, broken or separated conjuncts, missing or misplaced matras, Latin transliteration of the Hindi text, any voiceover, any narration, any spoken words, any human voice, any singing, background music, sound effects, an automatic caption, an auto-generated subtitle, a burnt-in subtitle bar, closed captions, a transcript line, any text that appears because speech was generated, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed
```

---

**Notes for the batch owner (no action needed to proceed):** Segments 1–4 are entirely TEXT_ONLY, so no diagram spec, 3D-render or timing-sync blocks apply; the accuracy brief still lands in the negatives as explicit bans (green rust, brassy zinc, Fe₃O₄/FeO as rust, glossy rust) so no chemistry imagery can leak into a text clip. The plan's route flag stands — these four segments are pure Devanagari typography and would render more reliably in Manim + Poppins than in Veo. **Tool setting: 1080×1920.** Test Segment 1 first before generating the rest.

Read the reference frame — note it is a **landscape full-bleed poster**, exactly the composition that previously pushed a diagram past the middle line, so Segment 6 uses §18 SIZE AND POSITION CHECK and does **not** copy that layout (single bar, top half only, no label plates). Colour/texture reference taken from its rightmost panel: brushed grey metal, reddish-orange flaky rust, blue moisture droplets with descending arrows.

**Assumption stated once:** Segments 5–8 contain no brand word, so the `अरिहान/अरिविहान` question does not affect this batch; Seg 6's diagram shows air **and** moisture together (blue droplets + descending arrows onto the bar) to satisfy the "rusting needs BOTH" rule without adding a second test tube, which would not fit the top half.

---

```
VIDEO PROMPT — SEGMENT 5 OF 18

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

AUDIO: this clip is completely SILENT. There is no voiceover, no narration, no speech, no singing, no music, no sound effects and no ambient sound of any kind. No voice is generated at any moment. The audio track is empty. The spoken narration is added separately in editing from a different source.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, starting close to the top edge. The equation sits directly below the script text, comfortably above the invisible middle line, and is large enough that the top half does not look empty. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

NO DIAGRAM IN THIS CLIP (CRITICAL): this clip contains NO three dimensional object of any kind. There is no metal bar, no nail, no rod, no rust patch, no water droplet, no test tube, no arrow, no coating layer, no shape, no icon and no illustration anywhere in the frame at any moment. The only things on screen are the script text, the equation, and the plain background. Do not invent, add or imagine any diagram, object or graphic. The space below the equation stays as plain empty background.

EQUATION RULE (CRITICAL): the equation is flat two dimensional overlay text, not a three dimensional object. It is ONE single clean horizontal line of large bold white text with a soft cyan glow, centred below the script text, perfectly sharp, with every letter and symbol correct and correctly sized. It is not on a card, not in a box, and never stacked onto two lines. If it is too wide, reduce its size until the whole line fits comfortably inside the frame width with clear margins on both sides. It appears exactly once and holds to the end of the clip. The script text stays at the top and the equation stays below it — they never overlap and never swap places. The equation is written exactly: "धातु + वायुमण्डल की गैसें + नमी = संक्षारण"

HIGHLIGHT RULE (CRITICAL — NO NEW TEXT IS EVER CREATED): when a part of the equation is emphasised, that part of the EXISTING equation simply changes colour and glows brighter in place. NEVER copy a word or symbol out of the equation. NEVER draw a second copy of any word or symbol anywhere. NEVER create a label, plate, chip, callout or floating letter for it. The equation itself is the only place any of these words or symbols ever appears.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next element appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE. Every word appears exactly the number of times it is written.
- EXACT COUNT: the word "संक्षारण" appears exactly TWICE in total in this clip — once inside the carried-over phrase at the start, and once inside the equation. The two are never on screen at the same time. Nowhere else, in any size, at any moment.
- EXACT COUNT: the plus sign "+" appears exactly TWICE in this clip and the equals sign "=" appears exactly ONCE, and all three exist only inside the single equation line. No plus sign, no equals sign and no other mathematical symbol appears anywhere outside the equation.
- EXACT COUNT: the word "धातु" appears exactly ONCE in this clip, inside the equation, and nowhere else.
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol, with every Devanagari matra, dot and conjunct correct.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. In this clip the phrase "इसे याद रखने का आसान तरीका है" has ONE golden word: "आसान", styled in place inside the sentence. The equation line contains mathematical symbols and is therefore COMPLETELY UNIFORM bold white with NO golden word. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters or mathematical symbols individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters or mathematical symbols into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming element begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time, perfectly synced. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean crisp flat overlay typography on a dark technical background. Never photorealistic. NO fire, NO flame, NO sparks, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: continuing exactly from the previous clip — the phrase "संक्षारण कहते हैं।" is already present at the very top of the frame at the very first frame, sharp and still, and does not fade in again. Nothing else.

ANIMATION TIMELINE:
- 0.0–0.6 s: the carried-over phrase "संक्षारण कहते हैं।" holds, then fades out completely by 0.6 s. A 0.2 second gap with no text follows.
- 0.8–4.6 s: the phrase "इसे याद रखने का आसान तरीका है" pops in at the very top of the frame, fully sharp from its first visible frame, with the single golden word "आसान" styled in place. It holds, then fades out completely by 4.6 s. A 0.2 second gap with no text follows.
- 4.8 s: the equation "धातु + वायुमण्डल की गैसें + नमी = संक्षारण" pops in as ONE single horizontal line below where the script text was, large, bold white with a soft cyan glow, fully sharp and correctly spelled from its first visible frame. It never moves, never resizes and holds to the end of the clip.
- 7.5 s: the word "संक्षारण" inside the EXISTING equation turns bright green and glows, staying exactly in its place inside the equation, and holds that glow to 10.0 s. No copy of it is made anywhere.
- 10.0 s: the clip ends with only the equation on screen, the word "संक्षारण" inside it glowing green.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "संक्षारण कहते हैं।"
2. "इसे याद रखने का आसान तरीका है"
3. "धातु + वायुमण्डल की गैसें + नमी = संक्षारण"

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, broken or missing Devanagari matras, incorrect conjunct letters, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, invented labels, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, any voiceover, any narration, any spoken words, any human voice, any singing, background music, sound effects, an automatic caption, an auto-generated subtitle, a burnt-in subtitle bar, closed captions, a transcript line, any text that appears because speech was generated, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, any metal bar, nail, rod, rust patch, water droplet, test tube, arrow, coating layer, shape, icon or illustration, a copy of any word or symbol taken out of the equation, a floating plus sign anywhere outside the equation, a floating equals sign anywhere outside the equation, a third plus sign, a second equals sign, a floating word "संक्षारण" anywhere outside the equation and the carried-over phrase, three copies of "संक्षारण", any label plate, any chip, any callout, any leader line, two copies of the equation, the equation moving or resizing, the equation stacked onto two lines, a golden word inside the equation, wrong mathematical symbols, extra equations, a chemical formula, Fe2O3, Fe3O4, FeO, any English text
```

---

```
VIDEO PROMPT — SEGMENT 6 OF 18

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

AUDIO: this clip is completely SILENT. There is no voiceover, no narration, no speech, no singing, no music, no sound effects and no ambient sound of any kind. No voice is generated at any moment. The audio track is empty. The spoken narration is added separately in editing from a different source.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, starting close to the top edge. The diagram sits directly below the script text and fills the space between the text and the invisible middle line, so the top half never looks empty. The lowest part of the diagram stops with a clear visible gap above the invisible middle line and never touches it; if it does not fit, make it smaller. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

SIZE AND POSITION CHECK (CRITICAL): before anything is drawn, the diagram is scaled so that its complete height — including every droplet, arrow, glow and shadow — fits inside the upper half of the frame with a clear visible margin still left below it. If any part of the diagram would reach the middle of the frame, the whole diagram is made smaller until it does not. The diagram never grows, drifts downward, expands or scales up at any moment during the clip. The lower half of the frame contains nothing but the background from the first frame to the last. This is a vertical composition with one small object in the upper half — it is never a full-frame poster, never a landscape panel layout, never a chart of several boxes side by side.

3D RENDER QUALITY (CRITICAL — THIS MAKES THE DIAGRAM LOOK THREE DIMENSIONAL):
The diagram is a real three dimensional object rendered in depth, not a flat drawing.
- CAMERA: a fixed three-quarter view from slightly above the object, so the viewer looks slightly down at it and can clearly read its thickness and its top face. Never a flat straight-on front view.
- PERSPECTIVE: the edges of the object recede correctly, the far edge appearing shorter than the near edge. Nothing is drawn as a plain flat rectangle.
- DEPTH: the parts nearest the camera are brighter, thicker and sharper. The parts on the far side are noticeably dimmer, thinner and softer. This difference is clear and obvious.
- LIGHTING: one soft cool rim light along the upper left edge and a gentle ambient fill, giving a rounded sculpted look with a soft falloff toward the lower right.
- MATERIAL: the metal is smooth brushed steel-grey with a faint specular highlight near the upper left. The rust on it is the opposite — dull, matte, flaky and powdery, with no shine at all.
- FORESHORTENING: any arrow pointing toward the camera looks shorter and thicker with a larger arrowhead, and any arrow pointing away looks longer and thinner. They are never all the same length on screen.
- MOTION: the object turns very slowly and steadily around its vertical axis so the depth reads clearly. It never wobbles, never squashes, never deforms and never changes size once settled.

DIAGRAM SPECIFICATION (build exactly this, nothing else):
- THE IRON BAR: one single rectangular iron bar rendered in full three dimensions, lying flat and seen from the three-quarter camera angle from slightly above, so its long top face and its near side face are both visible. Its material is clean brushed steel-grey metal with fine horizontal brush lines, slightly rounded corners, a faint cool specular highlight along its upper left edge and a soft contact shadow beneath it. It turns very slowly and steadily. It never becomes a nail, never becomes a rod, never becomes a sheet, never bends, never melts and never deforms.
- THE MOISTURE AND AIR: exactly six small glossy blue spheres of different sizes floating in the space above the iron bar, and exactly five short straight blue arrows below them pointing downward onto the top face of the bar, showing damp air reaching the metal. Because of perspective the arrows nearer the camera appear shorter and thicker with larger heads and the ones further away appear thinner and fainter. The arrows are evenly spaced, never tangled and never crossing each other. They are calm and still, and they never turn into rain, splashes, waves, a pool of water or a container of liquid.
- THE RUST: an irregular patch of corrosion spreading across the middle of the top face of the iron bar, reddish-brown to orange-brown, matte, flaky and powdery in texture, with rough uneven granular edges like dry crumbling powder sitting on the surface. It grows outward slowly from the centre of the bar and stays entirely on the bar. It is NEVER green, NEVER blue-green, NEVER black, NEVER white-grey, NEVER golden and NEVER smooth or glossy. The clean brushed metal is still clearly visible around it on both ends of the bar.
- LABELS: this clip has NO labels at all. There is no plate, no chip, no tag, no number, no leader line and no floating letter anywhere in the frame. Never invent a label.

DIAGRAM TIMING SYNC (CRITICAL): every object appears at the exact moment its name is visible in the written phrase on screen, and never a frame before. The iron bar appears exactly as the word "लोहे" is visible on screen, and the rust appears exactly as the word "जंग" is visible on screen.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE. Every word appears exactly the number of times it is written.
- EXACT COUNT: the word "जंग" appears exactly ONCE in this whole clip, inside the second phrase only. It never appears on or near the iron bar, in any size, at any moment.
- EXACT COUNT: the word "लोहे" appears exactly ONCE in this whole clip, inside the second phrase only.
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol, with every Devanagari matra, dot and conjunct correct.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. In this clip the phrase "और इसका सबसे आसान उदाहरण है," has ONE golden word: "उदाहरण". The phrase "लोहे में जंग लगना।" has ONE golden word: "जंग". Each golden word is styled in place inside its own sentence and is never written again anywhere else. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time, perfectly synced. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean, glossy, textbook-style chemistry illustration rendered in three dimensions — smooth shapes, flat bright colours, soft even glow, like a modern NCERT diagram built in 3D. Never photorealistic. NO fire, NO flame, NO burning, NO spark, NO ember, NO explosion, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: continuing exactly from the previous clip — the equation "धातु + वायुमण्डल की गैसें + नमी = संक्षारण" is already present below the top of the frame at the very first frame, sharp and still, with the word "संक्षारण" inside it glowing green, and it does not fade in again. Nothing else.

ANIMATION TIMELINE:
- 0.0–0.5 s: the carried-over equation holds, then fades out completely by 0.5 s, leaving empty background below the top of the frame. A 0.2 second gap with no text follows.
- 0.7–4.6 s: the phrase "और इसका सबसे आसान उदाहरण है," pops in at the very top of the frame, fully sharp from its first visible frame, with the golden word "उदाहरण" styled in place. It holds, then fades out completely by 4.6 s. A 0.2 second gap with no text follows. Nothing else is on screen during this time — the space below the phrase is plain background.
- 4.8 s: the phrase "लोहे में जंग लगना।" pops in at the very top of the frame, fully sharp, with the golden word "जंग" styled in place. It holds to the end of the clip.
- 5.2 s: exactly as the word "लोहे" is visible on screen, the clean brushed steel-grey iron bar fades in below the phrase, settles at its size and begins its very slow steady turn. It never changes size after settling.
- 6.0 s: the six blue moisture spheres and the five short downward blue arrows fade in above the bar.
- 6.6 s: exactly as the word "जंग" is visible on screen, the reddish-brown flaky rust patch begins to appear at the centre of the bar's top face and spreads slowly outward across the middle of the bar, staying matte and powdery, with clean metal still visible at both ends.
- 8.4–9.0 s: the whole diagram — bar, spheres, arrows and rust together — fades out completely by 9.0 s.
- 9.0–10.0 s: only the phrase "लोहे में जंग लगना।" remains at the top of the frame, with plain empty background below it.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "धातु + वायुमण्डल की गैसें + नमी = संक्षारण"
2. "और इसका सबसे आसान उदाहरण है,"
3. "लोहे में जंग लगना।"

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, broken or missing Devanagari matras, incorrect conjunct letters, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, invented labels, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, any voiceover, any narration, any spoken words, any human voice, any singing, background music, sound effects, an automatic caption, an auto-generated subtitle, a burnt-in subtitle bar, closed captions, a transcript line, any text that appears because speech was generated, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, the diagram crossing the middle of the frame, the diagram touching the middle of the frame, the diagram growing or expanding during the clip, the diagram drifting downward, an arrow or droplet reaching into the lower half, an inset circle in the lower half, the illustration filling the whole frame, a full-frame poster layout, several panels side by side, a landscape layout, a flat two dimensional rectangle instead of a three dimensional bar, a straight-on front view with no depth, arrows all drawn the same length on screen, a diagram that looks like a flat line drawing, a second iron bar, a third arrow group, a nail, a rod, a screw, a bolt, a chain, a pipe, a test tube, a beaker, a glass container, a pool or puddle of water, rain, splashing water, waves, green rust, blue-green corrosion, a green patch on the iron, black tarnish on the iron, white-grey powder on the iron, a golden or brassy coating on the iron, a shiny glossy smooth rust surface, rust that looks like wet paint, the bar shown only in water with no air, the bar shown only in dry air with no moisture, gold, platinum or stainless steel corroding, a chemical formula, Fe2O3, Fe3O4, FeO, any label plate, any chip, any callout, any leader line, the iron bar appearing before 5.2 seconds, the moisture spheres or arrows appearing before 6.0 seconds, the rust appearing before 6.6 seconds, the diagram still visible at 9.5 seconds, equations, any English text
```

---

```
VIDEO PROMPT — SEGMENT 7 OF 18

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

AUDIO: this clip is completely SILENT. There is no voiceover, no narration, no speech, no singing, no music, no sound effects and no ambient sound of any kind. No voice is generated at any moment. The audio track is empty. The spoken narration is added separately in editing from a different source.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, filling the width, starting close to the top edge, large enough to fill the upper area comfortably. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

NO DIAGRAM IN THIS CLIP (CRITICAL): this clip contains NO three dimensional object of any kind. There is no iron bar, no nail, no rod, no rust patch, no water droplet, no blue sphere, no test tube, no arrow, no coating layer, no shape, no icon and no illustration anywhere in the frame at any moment. The only things on screen are the script text and the plain background. Do not invent, add or imagine any diagram, object or graphic. The space below the script text stays as plain empty background.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE. Every word appears exactly the number of times it is written.
- EXACT COUNT: the word "धातु" appears exactly TWICE in total in this clip — once inside the second phrase and once inside the third phrase. The two are never on screen at the same time. Nowhere else, in any size, at any moment.
- EXACT COUNT: the word "संक्षारण" appears exactly ONCE in this whole clip, inside the first phrase only.
- EXACT COUNT: the word "तीन" appears exactly ONCE in this whole clip, inside the first phrase only. No numbered list, no counter, no digit and no bullet is ever drawn.
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol, with every Devanagari matra, dot and conjunct correct.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. In this clip the phrase "अब संक्षारण को प्रभावित करने वाले तीन कारक समझो।" has ONE golden word: "कारक", styled in place inside the sentence. The phrase "पहला, धातु की प्रकृति," and the phrase "मतलब धातु जितनी अधिक क्रियाशील होगी," both share the word "धातु" with each other and are therefore rendered COMPLETELY UNIFORM in bold white with NO golden word. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time, perfectly synced. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean crisp flat overlay typography on a dark technical background. Never photorealistic. NO fire, NO flame, NO sparks, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: continuing exactly from the previous clip — the phrase "लोहे में जंग लगना।" is already present at the very top of the frame at the very first frame, sharp and still, and does not fade in again. The rest of the frame is plain empty background. Nothing else.

ANIMATION TIMELINE:
- 0.0–0.5 s: the carried-over phrase "लोहे में जंग लगना।" holds, then fades out completely by 0.5 s. A 0.2 second gap with no text follows.
- 0.7–3.3 s: the phrase "अब संक्षारण को प्रभावित करने वाले तीन कारक समझो।" pops in at the very top of the frame, fully sharp from its first visible frame, with the single golden word "कारक" styled in place. It holds, then fades out completely by 3.3 s. A 0.2 second gap with no text follows.
- 3.5–6.6 s: the phrase "पहला, धातु की प्रकृति," pops in at the very top of the frame, fully sharp, completely uniform bold white with no golden word. It holds, then fades out completely by 6.6 s. A 0.2 second gap with no text follows.
- 6.8–10.0 s: the phrase "मतलब धातु जितनी अधिक क्रियाशील होगी," pops in at the very top of the frame, fully sharp, completely uniform bold white with no golden word. It holds to the end of the clip.
- 10.0 s: the clip ends with only this phrase on screen and plain empty background below it.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "लोहे में जंग लगना।"
2. "अब संक्षारण को प्रभावित करने वाले तीन कारक समझो।"
3. "पहला, धातु की प्रकृति,"
4. "मतलब धातु जितनी अधिक क्रियाशील होगी,"

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, broken or missing Devanagari matras, incorrect conjunct letters, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, invented labels, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, any voiceover, any narration, any spoken words, any human voice, any singing, background music, sound effects, an automatic caption, an auto-generated subtitle, a burnt-in subtitle bar, closed captions, a transcript line, any text that appears because speech was generated, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, any iron bar, nail, rod, rust patch, water droplet, blue sphere, test tube, arrow, coating layer, shape, icon or illustration of any kind, any label plate, any chip, any callout, any leader line, a numbered list, a bulleted list, digits, a counter, a panel of three boxes, three side-by-side cards, a table, a chart, a fourth factor, a fifth factor, a golden word in the second or third phrase, two golden words in one phrase, a third copy of the word "धातु", a chemical formula, equations, any English text
```

---

```
VIDEO PROMPT — SEGMENT 8 OF 18

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

AUDIO: this clip is completely SILENT. There is no voiceover, no narration, no speech, no singing, no music, no sound effects and no ambient sound of any kind. No voice is generated at any moment. The audio track is empty. The spoken narration is added separately in editing from a different source.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, filling the width, starting close to the top edge, large enough to fill the upper area comfortably. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

NO DIAGRAM IN THIS CLIP (CRITICAL): this clip contains NO three dimensional object of any kind. There is no iron bar, no nail, no rod, no rust patch, no water droplet, no blue sphere, no test tube, no arrow, no coating layer, no shape, no icon and no illustration anywhere in the frame at any moment. The only things on screen are the script text and the plain background. Do not invent, add or imagine any diagram, object or graphic. The space below the script text stays as plain empty background.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE. Every word appears exactly the number of times it is written.
- EXACT COUNT: the word "संक्षारण" appears exactly TWICE in total in this clip — once inside the first phrase and once inside the third phrase. The two are never on screen at the same time. Nowhere else, in any size, at any moment.
- EXACT COUNT: the word "धातु" appears exactly TWICE in total in this clip — once inside the second phrase and once inside the third phrase. Nowhere else, in any size, at any moment.
- EXACT COUNT: the word "अशुद्धियाँ" appears exactly TWICE in total in this clip — once inside the second phrase and once inside the third phrase. Nowhere else, in any size, at any moment. It is spelled exactly "अशुद्धियाँ" both times, with the chandrabindu correct.
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol, with every Devanagari matra, dot and conjunct correct.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. In this clip ALL THREE phrases share repeated words with each other and are therefore ALL rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight. THERE IS NO GOLDEN WORD ANYWHERE IN THIS CLIP. No word is coloured differently, enlarged, glowed or emphasised in any way. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time, perfectly synced. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean crisp flat overlay typography on a dark technical background. Never photorealistic. NO fire, NO flame, NO sparks, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: continuing exactly from the previous clip — the phrase "मतलब धातु जितनी अधिक क्रियाशील होगी," is already present at the very top of the frame at the very first frame, sharp and still, and does not fade in again. The rest of the frame is plain empty background. Nothing else.

ANIMATION TIMELINE:
- 0.0–0.5 s: the carried-over phrase "मतलब धातु जितनी अधिक क्रियाशील होगी," holds, then fades out completely by 0.5 s. A 0.2 second gap with no text follows.
- 0.7–3.3 s: the phrase "उस पर संक्षारण उतनी जल्दी होगा।" pops in at the very top of the frame, fully sharp from its first visible frame, completely uniform bold white with no golden word. It holds, then fades out completely by 3.3 s. A 0.2 second gap with no text follows.
- 3.5–6.6 s: the phrase "दूसरा, धातु में अशुद्धियाँ," pops in at the very top of the frame, fully sharp, completely uniform bold white with no golden word. It holds, then fades out completely by 6.6 s. A 0.2 second gap with no text follows.
- 6.8–10.0 s: the phrase "मतलब धातु में अशुद्धियाँ होने पर संक्षारण अधिक तेजी से होगा।" pops in at the very top of the frame, fully sharp, completely uniform bold white with no golden word, sitting on at most three short centred lines. It holds to the end of the clip.
- 10.0 s: the clip ends with only this phrase on screen and plain empty background below it.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "मतलब धातु जितनी अधिक क्रियाशील होगी,"
2. "उस पर संक्षारण उतनी जल्दी होगा।"
3. "दूसरा, धातु में अशुद्धियाँ,"
4. "मतलब धातु में अशुद्धियाँ होने पर संक्षारण अधिक तेजी से होगा।"

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, broken or missing Devanagari matras, a missing chandrabindu, incorrect conjunct letters, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, invented labels, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, any voiceover, any narration, any spoken words, any human voice, any singing, background music, sound effects, an automatic caption, an auto-generated subtitle, a burnt-in subtitle bar, closed captions, a transcript line, any text that appears because speech was generated, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, any iron bar, nail, rod, rust patch, water droplet, blue sphere, test tube, arrow, coating layer, shape, icon or illustration of any kind, any label plate, any chip, any callout, any leader line, a golden word, a coloured word, a highlighted word, an enlarged word, a numbered list, a bulleted list, digits, a counter, a panel of three boxes, a table, a chart, a third copy of "धातु", a third copy of "अशुद्धियाँ", a third copy of "संक्षारण", a chemical formula, equations, any English text
```

**Batch notes:** Seg 5 is the only place a symbol may appear (equation line, locked by count). Seg 6 is the only diagram here — one bar, air **and** moisture together, reddish-brown flaky rust only, no labels, faded out by 9.0 s so Seg 7 starts clean. Seg 8 deliberately carries **no golden word** because all three phrases share repeated words.

Read the anchor frame. One note before the prompts: **that frame is a landscape full-bleed poster — I did not use it as a composition anchor.** Per bug-ledger (sickle-cell test), a landscape full-bleed reference is a suspected cause of the "diagram crossed the middle line" bug, so these prompts specify portrait top-half composition in words only and add §18 enforcement.

**Assumptions I resolved myself (headless):** brand spells **अरिविहान** on screen (not in segs 9–12); Seg 16's answer card stays an editing overlay; **no plating-cell diagram added** — diagrams remain only at 6 / 11 / 13, so of this batch only Seg 11 is a DIAGRAM segment. Seg 11's coating is drawn as a dark blue-slate glossy film (never green — green on iron is the copper-patina error) and no rust appears in that clip.

---

**SEGMENT 9 OF 18**

```
VIDEO PROMPT — SEGMENT 9 OF 18

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

FULL SCRIPT OF THIS CLIP (this exact Hindi text appears on screen, word for word, one phrase at a time, and nowhere is it spoken):
"तीसरा, वातावरण, मतलब हवा, नमी और कुछ गैसों की मौजूदगी संक्षारण को बढ़ाती है। बस, इन तीनों को याद रखो,"

AUDIO: this clip is completely SILENT. There is no voiceover, no narration, no speech, no singing, no music, no sound effects and no ambient sound of any kind. No voice is generated at any moment. The audio track is empty. The spoken narration is added separately in editing from a different source.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, filling the width, starting close to the top edge, large enough to fill the upper area comfortably. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

NO DIAGRAM IN THIS CLIP (CRITICAL): this clip contains NO three dimensional object of any kind. There is no metal bar, no iron nail, no rust, no rust patch, no coating layer, no paint film, no water droplet, no gas bubble, no test tube, no arrow, no surface, no shape, no icon and no illustration anywhere in the frame at any moment. The only things on screen are the script text and the plain background. Do not invent, add or imagine any diagram, object or graphic. The space below the script text stays as plain empty background.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE. Every word appears exactly the number of times it is written.
- EXACT COUNT: the word "वातावरण" appears exactly ONCE in this whole clip, inside the first phrase. Nowhere else, in any size, at any moment.
- EXACT COUNT: the word "संक्षारण" appears exactly ONCE in this whole clip, inside the second phrase. Nowhere else, in any size, at any moment.
- EXACT COUNT: the word "तीनों" appears exactly ONCE in this whole clip, inside the third phrase. Nowhere else.
- The text is Devanagari (Hindi). Every letter, every matra, every vowel sign, every conjunct and every nukta is rendered exactly as written, correctly attached to its own letter. No matra is dropped, doubled, detached or moved to another letter. No empty box, no tofu box, no placeholder glyph, no Latin letter and no Devanagari letter that is not written here ever appears.
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated.
In this clip: the first phrase has exactly ONE golden word, "वातावरण". The second phrase has exactly ONE golden word, "संक्षारण". The third phrase has exactly ONE golden word, "तीनों". Every other word in every phrase is bold white.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time, exactly on the times given in the animation timeline. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean crisp flat overlay typography on a dark technical background. Never photorealistic. NO fire, NO flame, NO sparks, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: continuing exactly from the previous clip — the phrase "मतलब धातु में अशुद्धियाँ होने पर संक्षारण अधिक तेजी से होगा।" is on screen at the top of the frame. Nothing else.

ANIMATION TIMELINE:
0.0 s — the carried-over phrase "मतलब धातु में अशुद्धियाँ होने पर संक्षारण अधिक तेजी से होगा।" is present at the very first frame and immediately fades out over 0.15 seconds, becoming completely invisible.
0.2–3.3 s — the phrase "तीसरा, वातावरण, मतलब हवा, नमी और कुछ गैसों की मौजूदगी" pops in fully sharp at the top of the frame, with the single word "वातावरण" in gold in its place inside the sentence, and holds still. It fades out completely by 3.3 s.
3.5–6.6 s — the phrase "संक्षारण को बढ़ाती है।" pops in fully sharp in the same place, with the single word "संक्षारण" in gold, and holds still. It fades out completely by 6.6 s.
6.8–10.0 s — the phrase "बस, इन तीनों को याद रखो," pops in fully sharp in the same place, with the single word "तीनों" in gold, and holds perfectly still until the last frame of the clip.
Throughout — nothing else appears, moves, enters or leaves. The area below the script text is empty background for the whole 10 seconds.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "तीसरा, वातावरण, मतलब हवा, नमी और कुछ गैसों की मौजूदगी"
2. "संक्षारण को बढ़ाती है।"
3. "बस, इन तीनों को याद रखो,"

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, an em dash, a curly quote mark, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, a second copy of "वातावरण", a second copy of "संक्षारण", a second copy of "तीनों", invented labels, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, a dropped or detached matra, a matra attached to the wrong letter, an empty tofu box, a placeholder glyph, Latin or English letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, any metal bar, any iron nail, any rust, any rust patch, any coating layer, any water droplet, any gas bubble, any test tube, any arrow, any surface, any shape, any icon or illustration of any kind, any label plate, equations, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, any voiceover, any narration, any spoken words, any human voice, any singing, background music, sound effects, an automatic caption, an auto-generated subtitle, a burnt-in subtitle bar, closed captions, a transcript line, any text that appears because speech was generated
```

---

**SEGMENT 10 OF 18**

```
VIDEO PROMPT — SEGMENT 10 OF 18

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

FULL SCRIPT OF THIS CLIP (this exact Hindi text appears on screen, word for word, one phrase at a time, and nowhere is it spoken):
"धातु की प्रकृति, अशुद्धियाँ और वातावरण। अब समझते हैं संक्षारण से बचाव के तीन उपाय।"

AUDIO: this clip is completely SILENT. There is no voiceover, no narration, no speech, no singing, no music, no sound effects and no ambient sound of any kind. No voice is generated at any moment. The audio track is empty. The spoken narration is added separately in editing from a different source.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, filling the width, starting close to the top edge, large enough to fill the upper area comfortably. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

NO DIAGRAM IN THIS CLIP (CRITICAL): this clip contains NO three dimensional object of any kind. There is no metal bar, no iron nail, no rust, no rust patch, no coating layer, no paint film, no water droplet, no gas bubble, no test tube, no arrow, no surface, no shape, no icon and no illustration anywhere in the frame at any moment. The only things on screen are the script text and the plain background. Do not invent, add or imagine any diagram, object or graphic. The space below the script text stays as plain empty background.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE. Every word appears exactly the number of times it is written.
- The first phrase is a list of three items written as one single sentence, exactly as given, with commas and the word "और" as written. It is never turned into bullet points, never numbered, never split into separate plates or panels, and no fourth item is ever added.
- EXACT COUNT: the word "धातु" appears exactly ONCE in this whole clip, inside the first phrase. Nowhere else, in any size, at any moment.
- EXACT COUNT: the word "वातावरण" appears exactly ONCE in this whole clip, at the end of the first phrase. Nowhere else.
- EXACT COUNT: the word "अशुद्धियाँ" appears exactly ONCE in this whole clip, inside the first phrase. Nowhere else.
- EXACT COUNT: the word "संक्षारण" appears exactly ONCE in this whole clip, inside the second phrase. Nowhere else.
- EXACT COUNT: the word "तीन" appears exactly ONCE in this whole clip, inside the second phrase. Nowhere else.
- The text is Devanagari (Hindi). Every letter, every matra, every vowel sign, every conjunct and every nukta is rendered exactly as written, correctly attached to its own letter. No matra is dropped, doubled, detached or moved to another letter. No empty box, no tofu box, no placeholder glyph, no Latin letter and no Devanagari letter that is not written here ever appears.
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated.
In this clip: the first phrase has exactly ONE golden word, "प्रकृति". The second phrase has exactly ONE golden word, "बचाव". Every other word in both phrases is bold white.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time, exactly on the times given in the animation timeline. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean crisp flat overlay typography on a dark technical background. Never photorealistic. NO fire, NO flame, NO sparks, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: continuing exactly from the previous clip — the phrase "बस, इन तीनों को याद रखो," is on screen at the top of the frame. Nothing else.

ANIMATION TIMELINE:
0.0 s — the carried-over phrase "बस, इन तीनों को याद रखो," is present at the very first frame and immediately fades out over 0.15 seconds, becoming completely invisible.
0.2–4.8 s — the phrase "धातु की प्रकृति, अशुद्धियाँ और वातावरण।" pops in fully sharp at the top of the frame, as one sentence on at most three short centred lines, with the single word "प्रकृति" in gold in its place inside the sentence, and holds still. It fades out completely by 4.8 s.
5.0–10.0 s — the phrase "अब समझते हैं संक्षारण से बचाव के तीन उपाय।" pops in fully sharp in the same place, with the single word "बचाव" in gold, and holds perfectly still until the last frame of the clip.
Throughout — nothing else appears, moves, enters or leaves. The area below the script text is empty background for the whole 10 seconds.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "धातु की प्रकृति, अशुद्धियाँ और वातावरण।"
2. "अब समझते हैं संक्षारण से बचाव के तीन उपाय।"

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, bullet points, numbered list markers, a fourth item added to the list of three, four or five factors instead of three, separate panels or plates for the list items, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, an em dash, a curly quote mark, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, a second copy of "धातु", a second copy of "वातावरण", a second copy of "संक्षारण", invented labels, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, a dropped or detached matra, a matra attached to the wrong letter, an empty tofu box, a placeholder glyph, Latin or English letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, any metal bar, any iron nail, any rust, any coating layer, any water droplet, any test tube, any arrow, any surface, any shape, any icon or illustration of any kind, any label plate, equations, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, any voiceover, any narration, any spoken words, any human voice, any singing, background music, sound effects, an automatic caption, an auto-generated subtitle, a burnt-in subtitle bar, closed captions, a transcript line, any text that appears because speech was generated
```

---

**SEGMENT 11 OF 18** — the one DIAGRAM segment in this batch

```
VIDEO PROMPT — SEGMENT 11 OF 18

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

FULL SCRIPT OF THIS CLIP (this exact Hindi text appears on screen, word for word, one phrase at a time, and nowhere is it spoken):
"पहला, रोधिका स्थापित करना, मतलब लोहे पर पेंट, ग्रीस या तेल की परत लगाकर उसे हवा और नमी से बचाना।"

AUDIO: this clip is completely SILENT. There is no voiceover, no narration, no speech, no singing, no music, no sound effects and no ambient sound of any kind. No voice is generated at any moment. The audio track is empty. The spoken narration is added separately in editing from a different source.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, starting close to the top edge. The diagram sits directly below the script text and fills the space between the text and the invisible middle line, so the top half never looks empty. The lowest part of the diagram stops with a clear visible gap above the invisible middle line and never touches it; if it does not fit, make it smaller. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

SIZE AND POSITION CHECK (CRITICAL): before anything is drawn, the diagram is scaled so that its complete height — including every label, arrow, glow, shadow and the magnified inset — fits inside the upper half of the frame with a clear visible margin still left below it. If any part of the diagram would reach the middle of the frame, the whole diagram is made smaller until it does not. The diagram never grows, drifts downward, expands or scales up at any moment during the clip. The lower half of the frame contains nothing but the background from the first frame to the last.

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
- THE IRON BAR: exactly ONE rectangular iron bar rendered in full three dimensions, lying horizontally and seen from the three-quarter camera angle from slightly above, so its top face, its front long face and one short end face are all visible and its thickness reads clearly. Its material is brushed neutral steel grey with a smooth clean unrusted surface, a faint cool specular highlight running along its upper left edge and slightly darker grey on the faces turned away from the light. It is completely CLEAN metal for the whole clip: there is no rust, no orange patch, no brown patch, no green patch, no pitting, no flaking and no discolouration on it at any moment. It turns very slowly and steadily around its vertical axis and never wobbles, never deforms and never changes size once settled.
- THE PROTECTIVE COATING LAYER: exactly ONE thin continuous unbroken film that slides smoothly over the iron bar from the left and settles as a single even skin covering the bar's whole visible top face and front face, following its shape exactly like a coat of paint. It is a deep blue-slate glossy translucent film with a soft wet sheen and one faint specular highlight near its upper left, thin enough that the grey iron underneath still reads as the body of the bar. It is a single layer only — never two layers, never a second film, never a gap, never a crack, never a scratch, never a peeling edge and never a hole. It is NEVER green, NEVER gold, NEVER yellow, NEVER brassy and NEVER metallic silver. It sits ON TOP of the iron; the iron is never drawn on top of it. Once settled it stays perfectly still on the bar.
- LABELS: this clip has NO labels at all. No plate, no chip, no tag, no number, no floating letter and no leader line exists anywhere. Never invent a label.
- FADE OUT: after the coating has settled, the whole diagram — bar and coating together as one — shrinks smoothly to about half its size, drifts slightly upward and fades away completely by 9.0 seconds, leaving plain empty background below the script text for the rest of the clip.

DIAGRAM TIMING SYNC (CRITICAL): every object appears at the exact moment its name is visible in the written phrase on screen, and never a frame before. The iron bar appears only when the word "लोहे" is visible on screen, and the coating layer begins to slide over it only when the word "परत" is visible on screen. Nothing is drawn during the first phrase at all.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE. Every word appears exactly the number of times it is written.
- EXACT COUNT: the word "लोहे" appears exactly ONCE in this whole clip, inside the second phrase. Nowhere else, in any size, at any moment.
- EXACT COUNT: the word "परत" appears exactly ONCE in this whole clip, inside the second phrase. Nowhere else.
- EXACT COUNT: the word "नमी" appears exactly ONCE in this whole clip, inside the third phrase. Nowhere else.
- The text is Devanagari (Hindi). Every letter, every matra, every vowel sign, every conjunct and every nukta is rendered exactly as written, correctly attached to its own letter. No matra is dropped, doubled, detached or moved to another letter. No empty box, no tofu box, no placeholder glyph, no Latin letter and no Devanagari letter that is not written here ever appears.
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated.
In this clip: the first phrase has exactly ONE golden word, "रोधिका". The second phrase has exactly ONE golden word, "परत". The third phrase has exactly ONE golden word, "नमी". Every other word in every phrase is bold white.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time, exactly on the times given in the animation timeline. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean, glossy, textbook-style chemistry illustration rendered in three dimensions — smooth shapes, flat bright colours, soft even glow, like a modern NCERT diagram built in 3D. Never photorealistic. NO fire, NO flame, NO burning, NO spark, NO ember, NO explosion, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: continuing exactly from the previous clip — the phrase "अब समझते हैं संक्षारण से बचाव के तीन उपाय।" is on screen at the top of the frame. Nothing else — no diagram, no object, no label.

ANIMATION TIMELINE:
0.0 s — the carried-over phrase "अब समझते हैं संक्षारण से बचाव के तीन उपाय।" is present at the very first frame and immediately fades out over 0.15 seconds, becoming completely invisible.
0.2–3.3 s — the phrase "पहला, रोधिका स्थापित करना," pops in fully sharp at the top of the frame, with the single word "रोधिका" in gold in its place inside the sentence, and holds still. The area below it stays empty background — no object is drawn yet. The phrase fades out completely by 3.3 s.
3.5–6.6 s — the phrase "मतलब लोहे पर पेंट, ग्रीस या तेल की परत लगाकर" pops in fully sharp in the same place, with the single word "परत" in gold, and holds still.
At 4.0 s, exactly as the word "लोहे" is on screen, the single clean grey iron bar pops in below the script text, already at its final size, and begins its very slow steady turn.
At 5.2 s, exactly as the word "परत" is on screen, the single thin deep blue-slate coating film slides in from the left over the bar and settles as one even unbroken skin on it by 6.2 s, then stays still. The phrase fades out completely by 6.6 s.
6.8–10.0 s — the phrase "उसे हवा और नमी से बचाना।" pops in fully sharp in the same place, with the single word "नमी" in gold, and holds perfectly still until the last frame.
7.6–9.0 s — the coated bar, as one single object, shrinks smoothly to about half its size, drifts slightly upward and fades away completely by 9.0 s.
9.0–10.0 s — only the third phrase remains on screen, with plain empty background below it.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "पहला, रोधिका स्थापित करना,"
2. "मतलब लोहे पर पेंट, ग्रीस या तेल की परत लगाकर"
3. "उसे हवा और नमी से बचाना।"

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, the diagram crossing the middle of the frame, the diagram touching the middle of the frame, the diagram growing or expanding during the clip, the diagram drifting downward, a label or arrow reaching into the lower half, an inset circle in the lower half, the illustration filling the whole frame, a full-frame poster layout, a landscape layout, two phrases visible at the same time, garbled letters during a transition, the iron bar appearing before 4.0 seconds, the coating appearing before 5.2 seconds, any object visible during the first phrase, the diagram still visible after 9.0 seconds, a second iron bar, a second coating layer, a third object, any label plate, any chip, any callout, any leader line, any rust on the bar, any orange or reddish-brown patch, any brown flakes, any green coating, any green patch on iron, any gold, golden, yellow or brassy coating, a metallic silver or mirror-bright coating, a zinc coating in this clip, iron drawn on top of the coating, a cracked, scratched, broken, peeling or holed coating film, rust appearing through the coating, a corroding gold, platinum or stainless steel object, smooth glossy rust, a test tube, a beaker, a water tank, a nail, a chemical formula, a flat two dimensional rectangle instead of a three dimensional bar, a straight-on front view with no depth, a diagram that looks like a flat line drawing, a squashed or wobbling bar, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, an em dash, a curly quote mark, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, a second copy of "लोहे", a second copy of "परत", invented labels, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, a dropped or detached matra, a matra attached to the wrong letter, an empty tofu box, a placeholder glyph, Latin or English letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, equations, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, any voiceover, any narration, any spoken words, any human voice, any singing, background music, sound effects, an automatic caption, an auto-generated subtitle, a burnt-in subtitle bar, closed captions, a transcript line, any text that appears because speech was generated
```

---

**SEGMENT 12 OF 18**

```
VIDEO PROMPT — SEGMENT 12 OF 18

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

FULL SCRIPT OF THIS CLIP (this exact Hindi text appears on screen, word for word, one phrase at a time, and nowhere is it spoken):
"दूसरा, समर्पित बचाव, मतलब लोहे से अधिक क्रियाशील धातु की तह चढ़ाना, जो पहले नष्ट होकर लोहे को बचाती है।"

AUDIO: this clip is completely SILENT. There is no voiceover, no narration, no speech, no singing, no music, no sound effects and no ambient sound of any kind. No voice is generated at any moment. The audio track is empty. The spoken narration is added separately in editing from a different source.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, filling the width, starting close to the top edge, large enough to fill the upper area comfortably. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

NO DIAGRAM IN THIS CLIP (CRITICAL): this clip contains NO three dimensional object of any kind. There is no metal bar, no iron nail, no rust, no rust patch, no coating layer, no zinc layer, no paint film, no water droplet, no gas bubble, no test tube, no reactivity ladder, no arrow, no surface, no shape, no icon and no illustration anywhere in the frame at any moment. The only things on screen are the script text and the plain background. Do not invent, add or imagine any diagram, object or graphic. The space below the script text stays as plain empty background.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE. Every word appears exactly the number of times it is written.
- EXACT COUNT: the word "लोहे" appears exactly TWICE in total in this clip — once inside the second phrase and once inside the third phrase, exactly as written. Never a third time, nowhere else, in any size, at any moment. Within each single phrase it appears exactly once.
- EXACT COUNT: the word "धातु" appears exactly ONCE in this whole clip, inside the second phrase. Nowhere else.
- EXACT COUNT: the word "बचाव" appears exactly ONCE in this whole clip, inside the first phrase. Nowhere else.
- EXACT COUNT: the word "क्रियाशील" appears exactly ONCE in this whole clip, inside the second phrase. Nowhere else.
- The text is Devanagari (Hindi). Every letter, every matra, every vowel sign, every conjunct and every nukta is rendered exactly as written, correctly attached to its own letter. No matra is dropped, doubled, detached or moved to another letter. No empty box, no tofu box, no placeholder glyph, no Latin letter and no Devanagari letter that is not written here ever appears.
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated.
In this clip: the first phrase has exactly ONE golden word, "समर्पित". The second phrase has exactly ONE golden word, "क्रियाशील". The third phrase has exactly ONE golden word, "नष्ट". The word "लोहे" is NEVER golden in either phrase — it stays bold white both times. Every other word in every phrase is bold white.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time, exactly on the times given in the animation timeline. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean crisp flat overlay typography on a dark technical background. Never photorealistic. NO fire, NO flame, NO sparks, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: continuing exactly from the previous clip — the phrase "उसे हवा और नमी से बचाना।" is on screen at the top of the frame. Nothing else — the diagram from the previous clip is already gone and never returns.

ANIMATION TIMELINE:
0.0 s — the carried-over phrase "उसे हवा और नमी से बचाना।" is present at the very first frame and immediately fades out over 0.15 seconds, becoming completely invisible.
0.2–3.3 s — the phrase "दूसरा, समर्पित बचाव," pops in fully sharp at the top of the frame, with the single word "समर्पित" in gold in its place inside the sentence, and holds still. It fades out completely by 3.3 s.
3.5–6.6 s — the phrase "मतलब लोहे से अधिक क्रियाशील धातु की तह चढ़ाना," pops in fully sharp in the same place, with the single word "क्रियाशील" in gold, and holds still. It fades out completely by 6.6 s.
6.8–10.0 s — the phrase "जो पहले नष्ट होकर लोहे को बचाती है।" pops in fully sharp in the same place, with the single word "नष्ट" in gold, and holds perfectly still until the last frame of the clip.
Throughout — nothing else appears, moves, enters or leaves. The area below the script text is empty background for the whole 10 seconds.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "दूसरा, समर्पित बचाव,"
2. "मतलब लोहे से अधिक क्रियाशील धातु की तह चढ़ाना,"
3. "जो पहले नष्ट होकर लोहे को बचाती है।"

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, a third copy of "लोहे", the word "लोहे" written twice inside one phrase, "लोहे" styled in gold, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, an em dash, a curly quote mark, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, invented labels, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, a dropped or detached matra, a matra attached to the wrong letter, an empty tofu box, a placeholder glyph, Latin or English letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, any metal bar, any iron nail, any rust, any orange or reddish-brown patch, any green patch on iron, any zinc or coating layer, a golden or brassy metal coating, iron drawn coating zinc, a reactivity ladder with zinc placed below iron, a chemical formula, FeO, Fe3O4, any water droplet, any test tube, any arrow, any surface, any shape, any icon or illustration of any kind, any label plate, equations, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, any voiceover, any narration, any spoken words, any human voice, any singing, background music, sound effects, an automatic caption, an auto-generated subtitle, a burnt-in subtitle bar, closed captions, a transcript line, any text that appears because speech was generated
```

---

Standing route flag (unchanged, not blocking this batch): Segs 9, 10 and 12 are pure Devanagari typography — Manim + Poppins renders those correctly by construction, and Veo's Devanagari matra/conjunct handling is the one failure mode no prompt rule fixes. Seg 11 is the only clip here with animation worth generating.

Read the anchor frame — it's a landscape, full-bleed poster layout (content spans the entire frame, no reserved lower half), which is exactly the composition that caused the "diagram crossed the middle" bug. So Segment 13 carries the full §18 SIZE AND POSITION CHECK block plus its negatives, and the zinc bar is spec'd small and top-anchored.

**Assumptions (unresolved items resolved by me, no confirmation sought):** brand spelling doesn't occur in 13–16 so it's moot here; Seg 16 stays TEXT_ONLY (the written answer card is an editing overlay, never generated inside the clip); no plating-cell diagram added to Seg 14 — three measures stay three, and a cell would force a cathode/anode label load that breaks the top-half rule. Rust colour in the anchor frame (orange-brown flaky) matches the accuracy brief and is reused as the reference for zinc's contrast (zinc = dull bluish-grey, never gold).

```
VIDEO PROMPT — SEGMENT 13 OF 18

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

AUDIO: this clip is completely SILENT. There is no voiceover, no narration, no speech, no singing, no music, no sound effects and no ambient sound of any kind. No voice is generated at any moment. The audio track is empty. The spoken narration is added separately in editing from a different source.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, starting close to the top edge. The diagram sits directly below the script text and fills the space between the text and the invisible middle line, so the top half never looks empty. The lowest part of the diagram stops with a clear visible gap above the invisible middle line and never touches it; if it does not fit, make it smaller. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

SIZE AND POSITION CHECK (CRITICAL): before anything is drawn, the diagram is scaled so that its complete height — including every label, arrow, glow, shadow and the magnified inset — fits inside the upper half of the frame with a clear visible margin still left below it. If any part of the diagram would reach the middle of the frame, the whole diagram is made smaller until it does not. The diagram never grows, drifts downward, expands or scales up at any moment during the clip. The lower half of the frame contains nothing but the background from the first frame to the last.

3D RENDER QUALITY (CRITICAL — THIS MAKES THE DIAGRAM LOOK THREE DIMENSIONAL):
The diagram is a real three dimensional object rendered in depth, not a flat drawing.
- CAMERA: a fixed three-quarter view from slightly above the object, so the viewer looks slightly down at it and can clearly read its roundness and thickness. Never a flat straight-on front view.
- PERSPECTIVE: the edges of the bar recede toward the back of the frame, the far end appearing slightly smaller than the near end. Nothing is drawn as a plain flat rectangle.
- DEPTH: the parts nearest the camera are brighter, thicker and sharper. The parts on the far side are noticeably dimmer, softer and less detailed. This difference is clear and obvious.
- LIGHTING: one soft cool rim light along the upper left edge and a gentle ambient fill, giving a rounded sculpted look with a soft falloff toward the lower right.
- MATERIAL: a smooth brushed metallic surface with a faint specular highlight near the upper left, and a soft inner sheen.
- FORESHORTENING: the top face of the bar reads as a flattened parallelogram because of the viewing angle, never as a straight-on rectangle.
- MOTION: the object turns very slowly and steadily around its vertical axis so the depth reads clearly. It never wobbles, never squashes, never deforms and never changes size once settled.

DIAGRAM SPECIFICATION (build exactly this, nothing else):
- THE IRON BAR: one small rectangular metal bar rendered in full three dimensions, lying at a gentle diagonal, with clearly visible thickness and rounded edges. Its surface is a clean brushed steel grey with a faint cool sheen and fine lengthwise brush lines, exactly the grey of clean untreated iron. It is completely free of rust — no orange, no brown, no red, no flakes, no powder and no pitting anywhere on it at any moment. It turns very slowly and steadily. It never becomes flat, never wobbles and never deforms.
- THE ZINC COATING: one continuous smooth outer layer that forms ON TOP OF the iron bar, wrapping over its upper and side faces like a poured skin, while the iron bar stays intact inside it and is still understood to be there. The coating is a dull bluish-grey silvery metal with a soft matte sheen and a faint slightly mottled spangled texture, clearly cooler and duller than the iron beneath it. It is NEVER gold, NEVER yellow, NEVER brassy, NEVER copper-coloured and NEVER green. It forms by sweeping smoothly from the near end of the bar to the far end in one single pass, then stays exactly as it is. The coating always sits outside the iron and the iron always stays inside — the reverse never happens. There is never any rust, orange powder, brown flaking or corrosion on either the iron or the coating in this clip.
- LABELS: this clip has NO labels at all. No plate, no chip, no tag, no number, no arrow, no leader line and no floating letter exists anywhere in the frame. Never invent a label.

DIAGRAM TIMING SYNC (CRITICAL): every object appears at the exact moment its name is visible in the written phrase on screen, and never a frame before. The iron bar appears exactly as the word लोहे is visible on screen, and the zinc coating begins exactly as the word जिंक is visible on screen. Nothing from the previous clip is carried over; the frame begins empty except for the script text described below.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE. Every word appears exactly the number of times it is written.
- EXACT COUNT: the word "जिंक" appears exactly ONCE in total in this clip, inside the second phrase only. It is never written a second time, in any size, at any moment, and it never appears next to the diagram.
- EXACT COUNT: the word "लोहे" appears exactly ONCE in total in this clip, inside the second phrase only. Nowhere else.
- EXACT COUNT: the word "गैल्वेनीकरण" appears exactly ONCE in total in this clip, inside the first phrase only. Nowhere else.
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol. All script text is in the Devanagari script. Every conjunct letter, every matra and every vowel mark is formed correctly and completely. No Latin letters, no Roman transliteration and no English words appear anywhere.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated.
- In the FIRST phrase, the single golden key word is "गैल्वेनीकरण". Every other word in that phrase is bold white.
- In the SECOND phrase, the single golden key word is "जिंक". Every other word in that phrase is bold white.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time, appearing exactly at the times given in the animation timeline. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean, glossy, textbook-style chemistry illustration rendered in three dimensions — smooth shapes, flat bright colours, soft even glow, like a modern NCERT diagram built in 3D. Never photorealistic. NO fire, NO flame, NO burning, NO spark, NO ember, NO explosion, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: completely empty background. Nothing at all.

ANIMATION TIMELINE:
- 0.0 s: the first phrase "इसका उदाहरण है गैल्वेनीकरण," pops in sharp and complete at the very top of the frame, on at most three short centred lines, with "गैल्वेनीकरण" in gold and every other word in bold white. The area below it stays empty background.
- 0.0–4.8 s: the first phrase holds, perfectly still and sharp.
- 4.8 s: the first phrase disappears completely.
- 4.8–5.0 s: no phrase is on screen.
- 5.0 s: the second phrase "जिसमें लोहे पर जिंक की तह चढ़ाई जाती है।" pops in sharp and complete at the very top of the frame, with "जिंक" in gold and every other word in bold white. It holds to the end of the clip.
- 5.4 s: exactly as the word लोहे is visible on screen, the clean brushed grey iron bar fades in below the script text, small, well above the middle of the frame, and begins turning very slowly.
- 6.6 s: exactly as the word जिंक is visible on screen, the dull bluish-grey zinc coating begins forming on top of the iron bar, sweeping in one smooth pass from the near end to the far end.
- 7.8 s: the coating is complete and covers the outside of the bar. The bar keeps turning very slowly and does not change size or position.
- 8.4–9.0 s: the coated bar fades out smoothly and completely.
- 9.0–10.0 s: only the second phrase remains on screen, with plain empty background below it.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "इसका उदाहरण है गैल्वेनीकरण,"
2. "जिसमें लोहे पर जिंक की तह चढ़ाई जाती है।"

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, the diagram crossing the middle of the frame, the diagram touching the middle of the frame, the diagram growing or expanding during the clip, the diagram drifting downward, a label or arrow reaching into the lower half, an inset circle in the lower half, the illustration filling the whole frame, a full-frame poster layout, a landscape composition, two phrases visible at the same time, garbled letters during a transition, a gold or yellow or brassy zinc coating, a copper-coloured coating, a green coating, green rust on iron, any green corrosion, any rust of any colour in this clip, orange or brown powder on the bar, flaky corrosion, smooth glossy rust, iron drawn as a coating on top of zinc, the coating placed inside the bar with the iron outside, a broken or patchy coating, the coating peeling off, a chemical formula, the text Fe3O4, the text FeO, the text Fe2O3, any test tube, any liquid, any water drop, any paint layer, any grease, any reactivity ladder, any electroplating cell, any electrode, any battery, any wire, a fourth or fifth panel of measures, four preventive measures, any Latin letters, any English words, any Roman transliteration, broken conjunct letters, missing or misplaced matras, stray vowel marks, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, invented labels, any label plate, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, equations, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, any voiceover, any narration, any spoken words, any human voice, any singing, background music, sound effects, an automatic caption, an auto-generated subtitle, a burnt-in subtitle bar, closed captions, a transcript line, any text that appears because speech was generated, the iron bar appearing before 5.4 seconds, the zinc coating appearing before 6.6 seconds, the diagram still visible after 9.0 seconds
```

```
VIDEO PROMPT — SEGMENT 14 OF 18

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

AUDIO: this clip is completely SILENT. There is no voiceover, no narration, no speech, no singing, no music, no sound effects and no ambient sound of any kind. No voice is generated at any moment. The audio track is empty. The spoken narration is added separately in editing from a different source.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, filling the width, starting close to the top edge, large enough to fill the upper area comfortably. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

NO DIAGRAM IN THIS CLIP (CRITICAL): this clip contains NO three dimensional object of any kind. There is no metal bar, no nail, no test tube, no beaker, no coating layer, no electroplating cell, no electrode, no wire, no battery, no arrow, no droplet, no shape, no icon and no illustration anywhere in the frame at any moment. The only things on screen are the script text and the plain background. Do not invent, add or imagine any diagram, object or graphic. The space below the script text stays as plain empty background.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE. Every word appears exactly the number of times it is written.
- EXACT COUNT: the word "जिंक" appears exactly ONCE in total in this clip, inside the second phrase only. Nowhere else, in any size, at any moment.
- EXACT COUNT: the word "क्रोमियम" appears exactly ONCE in total in this clip, inside the second phrase only. Nowhere else.
- EXACT COUNT: the second phrase names exactly THREE metals and no more — "जिंक", "निकिल" and "क्रोमियम", in that order. No fourth metal name is ever added anywhere.
- EXACT COUNT: the word "धातु" is written exactly ONCE, inside the third phrase. The word "धातुओं" is written exactly ONCE, inside the second phrase. They are two different written words and neither is ever repeated.
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol. All script text is in the Devanagari script. Every conjunct letter, every matra, every vowel mark and the halant mark in "विद्युत्" is formed correctly and completely. No Latin letters, no Roman transliteration and no English words appear anywhere.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated.
- In the FIRST phrase, the single golden key word is "प्लेटिंग". Every other word in that phrase is bold white.
- In the SECOND phrase, the single golden key word is "क्रोमियम". Every other word in that phrase is bold white.
- In the THIRD phrase, the single golden key word is "सुरक्षित". Every other word in that phrase is bold white.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time, appearing exactly at the times given in the animation timeline. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean crisp flat overlay typography on a dark technical background. Never photorealistic. NO fire, NO flame, NO sparks, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: completely empty background. Nothing at all.

ANIMATION TIMELINE:
- 0.0 s: the first phrase "तीसरा, विद्युत् प्लेटिंग," pops in sharp and complete at the very top of the frame, with "प्लेटिंग" in gold and every other word in bold white.
- 0.0–3.3 s: the first phrase holds, perfectly still and sharp.
- 3.3 s: the first phrase disappears completely.
- 3.3–3.5 s: no phrase is on screen.
- 3.5 s: the second phrase "मतलब जिंक, निकिल या क्रोमियम जैसी धातुओं की परत चढ़ाकर" pops in sharp and complete, on at most three short centred lines, with "क्रोमियम" in gold and every other word in bold white.
- 3.5–6.6 s: the second phrase holds, perfectly still and sharp.
- 6.6 s: the second phrase disappears completely.
- 6.6–6.8 s: no phrase is on screen.
- 6.8 s: the third phrase "धातु को सुरक्षित करना।" pops in sharp and complete, with "सुरक्षित" in gold and every other word in bold white. It holds to the end of the clip.
- Throughout the whole clip the area below the script text stays plain empty background, and the bottom half of the frame stays completely empty.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "तीसरा, विद्युत् प्लेटिंग,"
2. "मतलब जिंक, निकिल या क्रोमियम जैसी धातुओं की परत चढ़ाकर"
3. "धातु को सुरक्षित करना।"

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, any metal bar, any nail, any test tube, any beaker, any coating layer, any electroplating cell, any electrode, any anode, any cathode, any battery, any wire, any arrow, any droplet, any rust, any orange or brown powder, any green corrosion, any shape, icon or illustration of any kind, any label plate, equations, any chemical formula, a fourth metal name, a fourth preventive measure, a list of four or five measures, any mention of alloying, any mention of anodising, any Latin letters, any English words, any Roman transliteration, broken conjunct letters, missing or misplaced matras, a missing halant in विद्युत्, stray vowel marks, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, invented labels, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, any voiceover, any narration, any spoken words, any human voice, any singing, background music, sound effects, an automatic caption, an auto-generated subtitle, a burnt-in subtitle bar, closed captions, a transcript line, any text that appears because speech was generated, the second phrase appearing before 3.5 seconds, the third phrase appearing before 6.8 seconds
```

```
VIDEO PROMPT — SEGMENT 15 OF 18

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

AUDIO: this clip is completely SILENT. There is no voiceover, no narration, no speech, no singing, no music, no sound effects and no ambient sound of any kind. No voice is generated at any moment. The audio track is empty. The spoken narration is added separately in editing from a different source.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, filling the width, starting close to the top edge, large enough to fill the upper area comfortably. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

NO DIAGRAM IN THIS CLIP (CRITICAL): this clip contains NO three dimensional object of any kind. There is no metal bar, no nail, no test tube, no beaker, no coating layer, no electroplating cell, no electrode, no wire, no battery, no arrow, no droplet, no shape, no icon and no illustration anywhere in the frame at any moment. The only things on screen are the script text and the plain background. Do not invent, add or imagine any diagram, object or graphic. The space below the script text stays as plain empty background.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE. Every word appears exactly the number of times it is written.
- EXACT COUNT: the word "संक्षारण" appears exactly ONCE in total in this clip, inside the second phrase only. Nowhere else, in any size, at any moment.
- EXACT COUNT: the word "याद" appears exactly ONCE in total in this clip, inside the first phrase only. Nowhere else.
- EXACT COUNT: the word "बस" appears exactly ONCE, inside the first phrase, and is never written a second time.
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol. All script text is in the Devanagari script. Every conjunct letter, every matra and every vowel mark is formed correctly and completely. No Latin letters, no Roman transliteration and no English words appear anywhere.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated.
- In the FIRST phrase, the single golden key word is "याद". Every other word in that phrase is bold white.
- In the SECOND phrase, the single golden key word is "संक्षारण". Every other word in that phrase is bold white.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time, appearing exactly at the times given in the animation timeline. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean crisp flat overlay typography on a dark technical background. Never photorealistic. NO fire, NO flame, NO sparks, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: completely empty background. Nothing at all.

ANIMATION TIMELINE:
- 0.0 s: the first phrase "बच्चों, बस इतना याद रख लिया," pops in sharp and complete at the very top of the frame, with "याद" in gold and every other word in bold white.
- 0.0–4.8 s: the first phrase holds, perfectly still and sharp.
- 4.8 s: the first phrase disappears completely.
- 4.8–5.0 s: no phrase is on screen.
- 5.0 s: the second phrase "तो परीक्षा में संक्षारण का ये पूरा उत्तर कभी नहीं भूलोगे।" pops in sharp and complete, on at most three short centred lines, with "संक्षारण" in gold and every other word in bold white. It holds to the end of the clip.
- Throughout the whole clip the area below the script text stays plain empty background, and the bottom half of the frame stays completely empty.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "बच्चों, बस इतना याद रख लिया,"
2. "तो परीक्षा में संक्षारण का ये पूरा उत्तर कभी नहीं भूलोगे।"

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, any metal bar, any nail, any test tube, any beaker, any coating layer, any electroplating cell, any electrode, any battery, any wire, any arrow, any droplet, any rust, any orange or brown powder, any green corrosion, any shape, icon or illustration of any kind, any label plate, equations, any chemical formula, any bullet list of factors or measures, any Latin letters, any English words, any Roman transliteration, broken conjunct letters, missing or misplaced matras, stray vowel marks, the word नहीं written twice, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, invented labels, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, any voiceover, any narration, any spoken words, any human voice, any singing, background music, sound effects, an automatic caption, an auto-generated subtitle, a burnt-in subtitle bar, closed captions, a transcript line, any text that appears because speech was generated, the second phrase appearing before 5.0 seconds
```

```
VIDEO PROMPT — SEGMENT 16 OF 18

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

AUDIO: this clip is completely SILENT. There is no voiceover, no narration, no speech, no singing, no music, no sound effects and no ambient sound of any kind. No voice is generated at any moment. The audio track is empty. The spoken narration is added separately in editing from a different source.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, filling the width, starting close to the top edge, large enough to fill the upper area comfortably. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

NO DIAGRAM IN THIS CLIP (CRITICAL): this clip contains NO three dimensional object of any kind. There is no metal bar, no nail, no test tube, no beaker, no coating layer, no electroplating cell, no electrode, no wire, no battery, no arrow, no droplet, no shape, no icon and no illustration anywhere in the frame at any moment. There is also no written answer, no answer sheet, no notebook page, no list of points, no answer card and no panel of text of any kind — the full written answer belongs to a later editing step and is never drawn inside this clip. The only things on screen are the two script phrases and the plain background. Do not invent, add or imagine any diagram, object or graphic. The space below the script text stays as plain empty background.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE. Every word appears exactly the number of times it is written.
- EXACT COUNT: the only text visible anywhere in this clip is the two phrases listed below, each written exactly ONCE. No third block of text exists at any moment, in any size, anywhere in the frame.
- EXACT COUNT: the word "उत्तर" appears exactly ONCE in total in this clip, inside the second phrase only. Nowhere else.
- EXACT COUNT: the word "स्क्रीन" appears exactly ONCE in total in this clip, inside the second phrase only. Nowhere else.
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol. All script text is in the Devanagari script. Every conjunct letter, every matra and every vowel mark is formed correctly and completely. No Latin letters, no Roman transliteration and no English words appear anywhere.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated.
- In the FIRST phrase, the single golden key word is "लिखना". Every other word in that phrase is bold white.
- In the SECOND phrase, the single golden key word is "स्क्रीन". Every other word in that phrase is bold white.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time, appearing exactly at the times given in the animation timeline. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean crisp flat overlay typography on a dark technical background. Never photorealistic. NO fire, NO flame, NO sparks, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: completely empty background. Nothing at all.

ANIMATION TIMELINE:
- 0.0 s: the first phrase "अब इसे परीक्षा में कैसे लिखना है," pops in sharp and complete at the very top of the frame, with "लिखना" in gold and every other word in bold white.
- 0.0–4.8 s: the first phrase holds, perfectly still and sharp.
- 4.8 s: the first phrase disappears completely.
- 4.8–5.0 s: no phrase is on screen.
- 5.0 s: the second phrase "इसका पूरा उत्तर आपकी स्क्रीन पर आ जाएगा।" pops in sharp and complete, with "स्क्रीन" in gold and every other word in bold white. It holds to the end of the clip.
- Throughout the whole clip the area below the script text stays plain empty background, and the bottom half of the frame stays completely empty. Nothing else ever appears — no answer, no list, no card, no page.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "अब इसे परीक्षा में कैसे लिखना है,"
2. "इसका पूरा उत्तर आपकी स्क्रीन पर आ जाएगा।"

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, a written answer appearing on screen, an answer card, an answer sheet, a notebook page, a exam paper, a list of points, a bulleted list, a numbered list, a panel or box of text, a third block of text, any metal bar, any nail, any test tube, any beaker, any coating layer, any electroplating cell, any electrode, any battery, any wire, any arrow, any droplet, any rust, any orange or brown powder, any green corrosion, any shape, icon or illustration of any kind, any label plate, equations, any chemical formula, any Latin letters, any English words, any Roman transliteration, broken conjunct letters, missing or misplaced matras, stray vowel marks, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, invented labels, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, any voiceover, any narration, any spoken words, any human voice, any singing, background music, sound effects, an automatic caption, an auto-generated subtitle, a burnt-in subtitle bar, closed captions, a transcript line, any text that appears because speech was generated, the second phrase appearing before 5.0 seconds
```

Continuity note: Seg 13 opens on an empty frame — Seg 12's phrase ends with that clip, and every diagram in this pack fades before its own clip ends, so 14/15/16 also start empty. Standing route caveat from the plan still holds: these four are 100% Devanagari kinetic typography plus one coating animation, and Manim + Poppins would render 14/15/16 correctly by construction; only Seg 13's organic zinc-coat sweep genuinely needs Veo.

**Assumption stated (headless, resolved myself):** brand goes on screen as **`अरिविहान`** (Arivihan transliterated), not `अरिहान` — the plan flagged it and this matches the brand. Both segments are TEXT_ONLY, silent (§17), uploaded background (§15), no §16 block, and every accuracy-brief COMMON ERROR is banned explicitly even though no diagram exists here.

---

### SEGMENT 17 OF 18

```
VIDEO PROMPT — SEGMENT 17 OF 18

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

ON-SCREEN SCRIPT (this text is shown, never spoken):
"इसे सेव कर लेना और इसका स्क्रीनशॉट लेना मत भूलना।"

AUDIO: this clip is completely SILENT. There is no voiceover, no narration, no speech, no singing, no music, no sound effects and no ambient sound of any kind. No voice is generated at any moment. The audio track is empty. The spoken narration is added separately in editing from a different source.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, filling the width, starting close to the top edge, large enough to fill the upper area comfortably. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

NO DIAGRAM IN THIS CLIP (CRITICAL): this clip contains NO three dimensional object of any kind. There is no iron bar, no nail, no metal plate, no rust, no coating layer, no test tube, no water, no droplet, no arrow, no shape, no icon and no illustration anywhere in the frame at any moment. The only things on screen are the script text and the plain background. Do not invent, add or imagine any diagram, object or graphic. The space below the script text stays as plain empty background.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE. Every word appears exactly the number of times it is written.
- EXACT COUNT: the word "लेना" appears exactly TWICE in total in this clip — once inside the first phrase and once inside the second phrase. Nowhere else, in any size, at any moment.
- EXACT COUNT: the carried-over sentence "इसका पूरा उत्तर आपकी स्क्रीन पर आ जाएगा।" appears exactly ONCE, only at the very start, and is never redrawn after it has faded away.
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol. This is Hindi in the Devanagari script: every matra, every vowel sign, every conjunct and every full stop danda is drawn exactly as written and is never dropped, doubled, swapped or attached to the wrong letter.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated.
In this clip: in the first phrase the single golden key word is "सेव". In the second phrase the single golden key word is "स्क्रीनशॉट". No other word in this clip is golden.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean crisp flat overlay typography on a dark technical background. Never photorealistic. NO fire, NO flame, NO sparks, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: continuing exactly from the previous clip — the sentence "इसका पूरा उत्तर आपकी स्क्रीन पर आ जाएगा।" is already present, sharp and still, in the top half of the frame at the very first frame and does not fade in again. Nothing else.

ANIMATION TIMELINE:
0.0–0.6 s: the carried-over sentence "इसका पूरा उत्तर आपकी स्क्रीन पर आ जाएगा।" holds sharp and still, then fades out completely by 0.6 s. It never returns.
0.6–0.8 s: a tiny gap with no phrase on screen. Only the unchanged background is visible.
0.8–4.8 s: the first phrase "इसे सेव कर लेना" appears with a clean pop at the very top of the frame, fully sharp from its first visible frame, with the word "सेव" golden in place inside the sentence. It holds still, then fades out completely by 4.8 s.
4.8–5.0 s: a tiny gap with no phrase on screen.
5.0–10.0 s: the second phrase "और इसका स्क्रीनशॉट लेना मत भूलना।" appears with a clean pop in the same top area, fully sharp from its first visible frame, with the word "स्क्रीनशॉट" golden in place inside the sentence. It holds completely still and unchanged to the very end of the clip at 10.0 s — this is a deliberate quiet pause, so nothing else moves, appears or changes for the rest of the clip.
Throughout: the bottom half of the frame stays completely empty background.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "इसका पूरा उत्तर आपकी स्क्रीन पर आ जाएगा।"
2. "इसे सेव कर लेना"
3. "और इसका स्क्रीनशॉट लेना मत भूलना।"

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, broken Devanagari conjuncts, missing or misplaced matras, a danda drawn twice, Latin letters mixed into the Hindi words, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, invented labels, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, any iron bar, nail, metal plate, test tube, water, droplet, rust, rust patch, coating layer, arrow, shape, icon or illustration of any kind, any label plate, equations, green rust on iron, an iron nail with a green coating, a golden or brassy zinc coating, iron shown coating zinc, the formulae Fe₃O₄ or FeO shown as rust, four or five items in any list, rust appearing through unbroken paint, gold or platinum or stainless steel shown corroding, smooth glossy rust, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, any voiceover, any narration, any spoken words, any human voice, any singing, background music, sound effects, an automatic caption, an auto-generated subtitle, a burnt-in subtitle bar, closed captions, a transcript line, any text that appears because speech was generated, the first phrase appearing before 0.8 seconds, the second phrase appearing before 5.0 seconds, the carried-over sentence reappearing after it has faded, a third phrase
```

---

### SEGMENT 18 OF 18

```
VIDEO PROMPT — SEGMENT 18 OF 18

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

ON-SCREEN SCRIPT (this text is shown, never spoken):
"और ऐसे ही आसान और मजेदार तरीके से पढ़ने के लिए अरिविहान के उन्नति बैच से जुड़ो।"

AUDIO: this clip is completely SILENT. There is no voiceover, no narration, no speech, no singing, no music, no sound effects and no ambient sound of any kind. No voice is generated at any moment. The audio track is empty. The spoken narration is added separately in editing from a different source.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, filling the width, starting close to the top edge, large enough to fill the upper area comfortably. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

NO DIAGRAM IN THIS CLIP (CRITICAL): this clip contains NO three dimensional object of any kind. There is no iron bar, no nail, no metal plate, no rust, no coating layer, no test tube, no water, no droplet, no arrow, no shape, no icon and no illustration anywhere in the frame at any moment. The only things on screen are the script text and the plain background. Do not invent, add or imagine any diagram, object or graphic. The space below the script text stays as plain empty background.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE beyond what is written. In the first phrase the word "और" is written exactly as given — it appears exactly TWICE inside that phrase and never a third time anywhere in the clip, in any size, at any moment.
- EXACT COUNT: the word "से" appears exactly TWICE in total in this clip — once inside the first phrase and once inside the second phrase. Nowhere else.
- EXACT COUNT: the carried-over sentence "और इसका स्क्रीनशॉट लेना मत भूलना।" appears exactly ONCE, only at the very start, and is never redrawn after it has faded away.
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol. This is Hindi in the Devanagari script: every matra, every vowel sign, every conjunct and every full stop danda is drawn exactly as written and is never dropped, doubled, swapped or attached to the wrong letter. The brand name is spelled exactly "अरिविहान" and in no other way.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated.
In this clip: the first phrase contains the same word twice, so the first phrase is rendered COMPLETELY UNIFORM in bold white with NO golden word at all. In the second phrase the single golden key word is "उन्नति". No other word in this clip is golden.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean crisp flat overlay typography on a dark technical background. Never photorealistic. NO fire, NO flame, NO sparks, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: continuing exactly from the previous clip — the sentence "और इसका स्क्रीनशॉट लेना मत भूलना।" is already present, sharp and still, in the top half of the frame at the very first frame and does not fade in again. Nothing else.

ANIMATION TIMELINE:
0.0–0.6 s: the carried-over sentence "और इसका स्क्रीनशॉट लेना मत भूलना।" holds sharp and still, then fades out completely by 0.6 s. It never returns.
0.6–0.8 s: a tiny gap with no phrase on screen. Only the unchanged background is visible.
0.8–4.8 s: the first phrase "और ऐसे ही आसान और मजेदार तरीके से पढ़ने के लिए" appears with a clean pop at the very top of the frame, fully sharp from its first visible frame, rendered completely uniform in bold white with no golden word. It holds still, then fades out completely by 4.8 s.
4.8–5.0 s: a tiny gap with no phrase on screen.
5.0–10.0 s: the second phrase "अरिविहान के उन्नति बैच से जुड़ो।" appears with a clean pop in the same top area, fully sharp from its first visible frame, with the word "उन्नति" golden in place inside the sentence. It holds completely still and unchanged to the very end of the clip at 10.0 s. Nothing else appears, moves or changes after this.
Throughout: the bottom half of the frame stays completely empty background.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "और इसका स्क्रीनशॉट लेना मत भूलना।"
2. "और ऐसे ही आसान और मजेदार तरीके से पढ़ने के लिए"
3. "अरिविहान के उन्नति बैच से जुड़ो।"

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, broken Devanagari conjuncts, missing or misplaced matras, a danda drawn twice, Latin letters mixed into the Hindi words, quotation marks around any word, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, invented labels, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, any iron bar, nail, metal plate, test tube, water, droplet, rust, rust patch, coating layer, arrow, shape, icon or illustration of any kind, any label plate, equations, green rust on iron, an iron nail with a green coating, a golden or brassy zinc coating, iron shown coating zinc, the formulae Fe₃O₄ or FeO shown as rust, four or five items in any list, rust appearing through unbroken paint, gold or platinum or stainless steel shown corroding, smooth glossy rust, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, any voiceover, any narration, any spoken words, any human voice, any singing, background music, sound effects, an automatic caption, an auto-generated subtitle, a burnt-in subtitle bar, closed captions, a transcript line, any text that appears because speech was generated, the first phrase appearing before 0.8 seconds, the second phrase appearing before 5.0 seconds, the carried-over sentence reappearing after it has faded, a golden word in the first phrase, a third phrase
```

**Tool setting:** 1080×1920 select karna.