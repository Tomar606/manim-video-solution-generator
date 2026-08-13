# संक्षारण — SEGMENT PROMPT SET

## Step 1 — Script pass

**Chunking:** 300 words total → **17 segments** (~18 words/segment; Hindi particle-heavy lines run ~2.2 words/sec). Diagram/equation segments carry slightly fewer words on purpose — the build fills the time.

**Corrections applied (wording kept, only fixed):**

| # | Source | On screen | Why |
|---|---|---|---|
| 1 | `संक्षारण से बचाव के 3 उपाय` | `...के तीन उपाय` | Parallel with `तीन कारक` in Clip 3; digit vs word inconsistency in the same answer |
| 2 | `अरिहान` | `अरिविहान` | Brand is Arivihan — this goes on screen |
| 3 | `विद्युत् प्लेटिंग` | `विद्युत प्लेटिंग` | Halant + following consonant garbles in generation; standard modern spelling |
| 4 | `‘उन्नति बैच’` | `उन्नति बैच` | Curly quotes render as stray marks (bug #12 / stray-punctuation ban) |
| 5 | `पहला—`, `दूसरा—`, `तीसरा—` em-dashes | comma, and the dash becomes the phrase break | Em-dash renders as a stray line/mark; the break is already structural |
| 6 | `तो चलिए,` (end of Clip 1) | moved to head of Seg 3 | Reads as the lead-in to the definition, not a hook tail |

**Not changed — flagging for your call:** `गैल्वेनीकरण` (some MP Board Hindi texts print `गैल्वनीकरण`) and `समर्पित बचाव` (sacrificial protection; some books use `बलिदानी सुरक्षा`). Tell me if your board copy differs — I'll match the textbook.

**Duplicate-word scan — segments needing EXACT COUNT locks in Step 3:**

| Seg | Repeat | Style consequence |
|---|---|---|
| 4 | `धीरे-धीरे` (repeat + hyphen, inside one phrase) | phrase UNIFORM white, no golden word |
| 7 | `धातु` ×2 (P1, P2) | count lock |
| **8** | `धातु में अशुद्धियाँ` ×2 (P1, P2) — **highest risk in the pack** | split across two phrases + hard count lock on all three words |
| 12 | `लोहे` ×2 (P2, P3) | count lock |
| **16** | `लेना` ×2 **inside P3**, `इसे`/`इसका` ×2 across phrases | P3 UNIFORM white, no golden word + count lock |
| 17 | `और` ×2 **inside P1** | P1 UNIFORM white, no golden word + count lock |

---

## 1. Total segment count

**17 segments × 10 sec = 170 sec (2:50).**

## 2. Segment map

| Seg | Phrases (exact words) | Type | Diagram |
|---|---|---|---|
| 1 | `एमपी बोर्ड कक्षा 12वीं के बच्चों!` • `ये सवाल 2025 में आ चुका है` • `और इस साल भी आपकी त्रैमासिक परीक्षा में आ सकता है।` | TEXT_ONLY | N |
| 2 | `और इस वीडियो के अंत तक आप इसे पूरा याद करके,` • `परीक्षा में सही तरीके से लिखना भी सीख जाओगे।` | TEXT_ONLY | N |
| 3 | `तो चलिए, सबसे पहले समझते हैं` • `संक्षारण किसे कहते हैं?` • `वायुमण्डल में उपस्थित गैसों तथा नमी के कारण` | TEXT_ONLY | N |
| 4 | `धातुओं के धीरे-धीरे अवांछित यौगिकों में` • `बदलने की प्रक्रिया को संक्षारण कहते हैं।` | TEXT_ONLY | N |
| 5 | `इसे याद रखने का आसान तरीका है` • **equation:** `धातु + वायुमण्डल की गैसें + नमी = संक्षारण` • `और इसका सबसे आसान उदाहरण है` | EQUATION_ONLY | N |
| 6 | `लोहे में जंग लगना।` • `अब संक्षारण को प्रभावित करने वाले तीन कारक समझो।` | DIAGRAM | **Y** — rusting iron nail |
| 7 | `पहला, धातु की प्रकृति,` • `मतलब धातु जितनी अधिक क्रियाशील होगी,` • `उस पर संक्षारण उतनी जल्दी होगा।` | TEXT_ONLY | N |
| 8 | `दूसरा, धातु में अशुद्धियाँ,` • `मतलब धातु में अशुद्धियाँ होने पर` • `संक्षारण अधिक तेजी से होगा।` | TEXT_ONLY | N |
| 9 | `तीसरा, वातावरण,` • `मतलब हवा, नमी और कुछ गैसों की मौजूदगी` • `संक्षारण को बढ़ाती है।` | TEXT_ONLY | N |
| 10 | `बस, इन तीनों को याद रखो` • `धातु की प्रकृति, अशुद्धियाँ और वातावरण।` • `अब समझते हैं संक्षारण से बचाव के तीन उपाय।` | TEXT_ONLY | N |
| 11 | `पहला, रोधिका स्थापित करना,` • `मतलब लोहे पर पेंट, ग्रीस या तेल की परत लगाकर` • `उसे हवा और नमी से बचाना।` | DIAGRAM | **Y** — iron bar + protective coat |
| 12 | `दूसरा, समर्पित बचाव,` • `मतलब लोहे से अधिक क्रियाशील धातु की तह चढ़ाना,` • `जो पहले नष्ट होकर लोहे को बचाती है।` | TEXT_ONLY | N |
| 13 | `इसका उदाहरण है गैल्वेनीकरण,` • `जिसमें लोहे पर जिंक की तह चढ़ाई जाती है।` | DIAGRAM | **Y** — iron sheet + zinc layer |
| 14 | `तीसरा, विद्युत प्लेटिंग,` • `मतलब जिंक, निकिल या क्रोमियम जैसी धातुओं की परत चढ़ाकर` • `धातु को सुरक्षित करना।` | TEXT_ONLY | N |
| 15 | `बच्चों, बस इतना याद रख लिया,` • `तो परीक्षा में संक्षारण का ये पूरा उत्तर` • `कभी नहीं भूलोगे।` | TEXT_ONLY | N |
| 16 | `अब इसे परीक्षा में कैसे लिखना है,` • `इसका पूरा उत्तर आपकी स्क्रीन पर आ जाएगा।` • `इसे सेव कर लेना और इसका स्क्रीनशॉट लेना मत भूलना।` | TEXT_ONLY | N |
| 17 | `और ऐसे ही आसान और मजेदार तरीके से पढ़ने के लिए` • `अरिविहान के उन्नति बैच से जुड़ो।` | TEXT_ONLY | N |

**All three diagram segments carry LABELS: none** — every label text here would duplicate a word already in the phrase (`जिंक की तह`, `गैल्वेनीकरण`, `परत`), which is exactly bugs #6/#9. Meaning is carried by colour instead.

## 3. End-states (continuity chain)

- **Seg 1 ends with:** empty background (last phrase clears by 10.0 s)
- **Seg 2 ends with:** empty background
- **Seg 3 ends with:** empty background
- **Seg 4 ends with:** empty background
- **Seg 5 ends with:** the equation `धातु + वायुमण्डल की गैसें + नमी = संक्षारण` alone on one line ⟶ *intentional hard cut into Seg 6 (section change); Seg 6 starts empty*
- **Seg 6 ends with:** the rusted iron nail (reddish-brown rust patches on a grey nail), holding ⟶ *intentional hard cut into Seg 7 (section change)*
- **Seg 7 ends with:** empty background
- **Seg 8 ends with:** empty background
- **Seg 9 ends with:** empty background
- **Seg 10 ends with:** empty background
- **Seg 11 ends with:** the iron bar with its unbroken coating layer, holding ⟶ *hard cut into Seg 12 (new point, दूसरा)*
- **Seg 12 ends with:** empty background
- **Seg 13 ends with:** the iron sheet with the silvery-grey zinc layer on its outside, holding ⟶ *hard cut into Seg 14 (new point, तीसरा)*
- **Seg 14 ends with:** empty background
- **Seg 15 ends with:** empty background
- **Seg 16 ends with:** empty background
- **Seg 17 ends with:** empty background

---

**Assumptions I've locked in (say the word if any is wrong):**
- **Silent clips** (§17) — no Veo voiceover, no auto-captions; audio comes from the HeyGen avatar.
- The **answer card** promised in Seg 16 is added in editing, not generated — a full written answer in Veo garbles.
- Diagram facts pinned for Step 0: rust = reddish-brown flaky layer on grey iron (never green/black); zinc layer sits **outside** the iron and is silvery-grey; coating is one unbroken layer.

**Three questions before I write the prompts:** (1) `गैल्वेनीकरण` vs `गैल्वनीकरण` — which spelling is in your board copy? (2) Keep `2025` and `12वीं` as digits on screen, or spell them out? (3) Are 3 diagrams enough, or do you want one for `विद्युत प्लेटिंग` too (Seg 14 is already text-heavy at 17 words)?


Read the frame — note it's a **landscape, white, full-bleed poster** (reference art for the topic, not the 9:16 background). That's exactly the anchor-frame shape the bug ledger flags as a "fill the whole frame / poster layout" signal, so don't feed it to the tool as an anchor; the uploaded Arivihan 9:16 background is the only image attached. Segments 1–4 are all TEXT_ONLY, so §18 doesn't apply yet — it will from Seg 6.

Per your instruction, `watermark` is removed from the base negative list too (skill's tested exception overridden).

```
VIDEO PROMPT — SEGMENT 1 OF 17

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

ON-SCREEN SCRIPT (this is written text only — it is NEVER spoken): the complete Hindi text of this clip appears on screen word for word in Devanagari script, one phrase at a time:
"एमपी बोर्ड कक्षा 12वीं के बच्चों! ये सवाल 2025 में आ चुका है और इस साल भी आपकी त्रैमासिक परीक्षा में आ सकता है।"

AUDIO: this clip is completely SILENT. There is no voiceover, no narration, no speech, no singing, no music, no sound effects and no ambient sound of any kind. No voice is generated at any moment. The audio track is empty. The spoken narration is added separately in editing from a different source.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, filling the width, starting close to the top edge, large enough to fill the upper area comfortably. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

NO DIAGRAM IN THIS CLIP (CRITICAL): this clip contains NO three dimensional object of any kind. There is no nail, no iron bar, no metal sheet, no rust, no rust patch, no water drop, no gas molecule, no beaker, no test tube, no arrow, no chemical formula, no shape, no icon and no illustration anywhere in the frame at any moment. The only things on screen are the script text and the plain background. Do not invent, add or imagine any diagram, object or graphic. The space below the script text stays as plain empty background.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE. Every word appears exactly the number of times it is written.
- All on-screen text is Hindi written in the Devanagari script, reproduced exactly as given — every matra, every conjunct, every nukta, every anusvara identical to the text in this prompt. Never transliterate into Latin letters, never translate into English, never mix in an English word.
- EXACT COUNT: the word "है" appears exactly TWICE in total in this clip — once inside the second phrase and once inside the third phrase. Nowhere else, in any size, at any moment.
- EXACT COUNT: the word "आ" appears exactly TWICE in total in this clip — once inside the second phrase and once inside the third phrase. Nowhere else, in any size, at any moment.
- EXACT COUNT: the digits "12" appear exactly ONCE in this clip, inside the first phrase only, and the digits "2025" appear exactly ONCE in this clip, inside the second phrase only. No other number of any kind appears anywhere.
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated.
Applying this rule to this clip: the FIRST phrase contains digits, so it is COMPLETELY UNIFORM bold white with NO golden word. The SECOND phrase contains digits, so it is COMPLETELY UNIFORM bold white with NO golden word. The THIRD phrase has ONE golden key word: "त्रैमासिक".

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean crisp flat overlay typography on a dark technical background. Never photorealistic. NO fire, NO flame, NO sparks, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: completely empty background. Nothing at all.

ANIMATION TIMELINE:
0.0 s — the first phrase "एमपी बोर्ड कक्षा 12वीं के बच्चों!" pops in at the very top of the frame, fully sharp, completely uniform bold white.
3.3 s — the first phrase disappears completely.
3.3–3.5 s — no phrase on screen at all.
3.5 s — the second phrase "ये सवाल 2025 में आ चुका है" pops in in the same place, fully sharp, completely uniform bold white.
6.6 s — the second phrase disappears completely.
6.6–6.8 s — no phrase on screen at all.
6.8 s — the third phrase "और इस साल भी आपकी त्रैमासिक परीक्षा में आ सकता है।" pops in in the same place, with only the word "त्रैमासिक" golden in place inside the sentence and every other word bold white.
10.0 s — the third phrase has faded out and the screen is empty background again.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "एमपी बोर्ड कक्षा 12वीं के बच्चों!"
2. "ये सवाल 2025 में आ चुका है"
3. "और इस साल भी आपकी त्रैमासिक परीक्षा में आ सकता है।"

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, curly quotation marks, an em dash, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, invented labels, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken Devanagari conjuncts, detached matras, a word split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, English or Latin letters, romanised transliteration, an English heading, the word Corrosion, an automatic subtitle bar at the bottom, an auto-generated subtitle, a burnt-in caption, closed captions, a transcript line, any text that appears because speech was generated, any voiceover, any narration, any spoken words, any human voice, any singing, background music, sound effects, random symbols, camera movement, zoom, scene change, background change, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, any nail, iron bar, metal sheet, rust, rust patch, water drop, gas molecule, beaker, test tube, arrow, chemical formula, shape, icon or illustration of any kind, any label plate, equations, a golden word in the first phrase, a golden word in the second phrase, more than one golden word in the third phrase, any number other than 12 and 2025
```

```
VIDEO PROMPT — SEGMENT 2 OF 17

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

ON-SCREEN SCRIPT (this is written text only — it is NEVER spoken): the complete Hindi text of this clip appears on screen word for word in Devanagari script, one phrase at a time:
"और इस वीडियो के अंत तक आप इसे पूरा याद करके, परीक्षा में सही तरीके से लिखना भी सीख जाओगे।"

AUDIO: this clip is completely SILENT. There is no voiceover, no narration, no speech, no singing, no music, no sound effects and no ambient sound of any kind. No voice is generated at any moment. The audio track is empty. The spoken narration is added separately in editing from a different source.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, filling the width, starting close to the top edge, large enough to fill the upper area comfortably. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

NO DIAGRAM IN THIS CLIP (CRITICAL): this clip contains NO three dimensional object of any kind. There is no nail, no iron bar, no metal sheet, no rust, no rust patch, no water drop, no gas molecule, no beaker, no test tube, no arrow, no chemical formula, no shape, no icon and no illustration anywhere in the frame at any moment. The only things on screen are the script text and the plain background. Do not invent, add or imagine any diagram, object or graphic. The space below the script text stays as plain empty background.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE. Every word appears exactly the number of times it is written.
- All on-screen text is Hindi written in the Devanagari script, reproduced exactly as given — every matra, every conjunct, every nukta, every anusvara identical to the text in this prompt. Never transliterate into Latin letters, never translate into English, never mix in an English word.
- EXACT COUNT: the word "इस" appears exactly ONCE in this clip, inside the first phrase, and the word "इसे" appears exactly ONCE in this clip, inside the first phrase. They are two different words and neither is ever written a second time.
- This clip contains NO digits and NO numbers of any kind, anywhere, at any moment.
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated.
Applying this rule to this clip: the FIRST phrase has ONE golden key word: "याद". The SECOND phrase has ONE golden key word: "परीक्षा". Every other word in both phrases is bold white.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean crisp flat overlay typography on a dark technical background. Never photorealistic. NO fire, NO flame, NO sparks, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: completely empty background. Nothing at all.

ANIMATION TIMELINE:
0.0 s — the first phrase "और इस वीडियो के अंत तक आप इसे पूरा याद करके," pops in at the very top of the frame, fully sharp, with only the word "याद" golden in place inside the sentence.
4.8 s — the first phrase disappears completely.
4.8–5.0 s — no phrase on screen at all.
5.0 s — the second phrase "परीक्षा में सही तरीके से लिखना भी सीख जाओगे।" pops in in the same place, fully sharp, with only the word "परीक्षा" golden in place inside the sentence.
10.0 s — the second phrase has faded out and the screen is empty background again.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "और इस वीडियो के अंत तक आप इसे पूरा याद करके,"
2. "परीक्षा में सही तरीके से लिखना भी सीख जाओगे।"

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, curly quotation marks, an em dash, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, invented labels, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken Devanagari conjuncts, detached matras, a word split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, English or Latin letters, romanised transliteration, an English heading, the word Corrosion, any digit or number, an automatic subtitle bar at the bottom, an auto-generated subtitle, a burnt-in caption, closed captions, a transcript line, any text that appears because speech was generated, any voiceover, any narration, any spoken words, any human voice, any singing, background music, sound effects, random symbols, camera movement, zoom, scene change, background change, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, any nail, iron bar, metal sheet, rust, rust patch, water drop, gas molecule, beaker, test tube, arrow, chemical formula, shape, icon or illustration of any kind, any label plate, equations, two golden words in one phrase, a golden word written again as a separate line
```

```
VIDEO PROMPT — SEGMENT 3 OF 17

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

ON-SCREEN SCRIPT (this is written text only — it is NEVER spoken): the complete Hindi text of this clip appears on screen word for word in Devanagari script, one phrase at a time:
"तो चलिए, सबसे पहले समझते हैं संक्षारण किसे कहते हैं? वायुमण्डल में उपस्थित गैसों तथा नमी के कारण"

AUDIO: this clip is completely SILENT. There is no voiceover, no narration, no speech, no singing, no music, no sound effects and no ambient sound of any kind. No voice is generated at any moment. The audio track is empty. The spoken narration is added separately in editing from a different source.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, filling the width, starting close to the top edge, large enough to fill the upper area comfortably. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

NO DIAGRAM IN THIS CLIP (CRITICAL): this clip contains NO three dimensional object of any kind. There is no nail, no iron bar, no metal sheet, no rust, no rust patch, no water drop, no gas molecule, no beaker, no test tube, no arrow, no chemical formula, no shape, no icon and no illustration anywhere in the frame at any moment. The only things on screen are the script text and the plain background. Do not invent, add or imagine any diagram, object or graphic. The space below the script text stays as plain empty background.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE. Every word appears exactly the number of times it is written.
- All on-screen text is Hindi written in the Devanagari script, reproduced exactly as given — every matra, every conjunct, every nukta, every anusvara identical to the text in this prompt. Never transliterate into Latin letters, never translate into English, never mix in an English word.
- EXACT COUNT: the word "हैं" appears exactly TWICE in total in this clip — once at the end of the first phrase and once at the end of the second phrase. Nowhere else, in any size, at any moment.
- EXACT COUNT: the word "संक्षारण" appears exactly ONCE in this whole clip, inside the second phrase only. It is never written a second time, never repeated as a heading, never repeated as a title and never placed on its own separate line.
- EXACT COUNT: the question mark appears exactly ONCE in this clip, at the end of the second phrase. No other punctuation mark is added anywhere.
- This clip contains NO digits and NO numbers of any kind, anywhere, at any moment.
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated.
Applying this rule to this clip: the FIRST phrase has ONE golden key word: "पहले". The SECOND phrase has ONE golden key word: "संक्षारण". The THIRD phrase has ONE golden key word: "नमी". Every other word in every phrase is bold white.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean crisp flat overlay typography on a dark technical background. Never photorealistic. NO fire, NO flame, NO sparks, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: completely empty background. Nothing at all.

ANIMATION TIMELINE:
0.0 s — the first phrase "तो चलिए, सबसे पहले समझते हैं" pops in at the very top of the frame, fully sharp, with only the word "पहले" golden in place inside the sentence.
3.3 s — the first phrase disappears completely.
3.3–3.5 s — no phrase on screen at all.
3.5 s — the second phrase "संक्षारण किसे कहते हैं?" pops in in the same place, fully sharp, with only the word "संक्षारण" golden in place inside the sentence.
6.6 s — the second phrase disappears completely.
6.6–6.8 s — no phrase on screen at all.
6.8 s — the third phrase "वायुमण्डल में उपस्थित गैसों तथा नमी के कारण" pops in in the same place, fully sharp, with only the word "नमी" golden in place inside the sentence.
10.0 s — the third phrase has faded out and the screen is empty background again.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "तो चलिए, सबसे पहले समझते हैं"
2. "संक्षारण किसे कहते हैं?"
3. "वायुमण्डल में उपस्थित गैसों तथा नमी के कारण"

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, curly quotation marks, an em dash, a second question mark, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a second "संक्षारण", the word "संक्षारण" written as a heading or title, a keyword written as a separate line, invented labels, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken Devanagari conjuncts, detached matras, a word split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, English or Latin letters, romanised transliteration, an English heading, the word Corrosion, any digit or number, an automatic subtitle bar at the bottom, an auto-generated subtitle, a burnt-in caption, closed captions, a transcript line, any text that appears because speech was generated, any voiceover, any narration, any spoken words, any human voice, any singing, background music, sound effects, random symbols, camera movement, zoom, scene change, background change, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, any nail, iron bar, metal sheet, rust, rust patch, water drop, gas molecule, beaker, test tube, arrow, chemical formula, shape, icon or illustration of any kind, any label plate, equations, two golden words in one phrase
```

```
VIDEO PROMPT — SEGMENT 4 OF 17

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

ON-SCREEN SCRIPT (this is written text only — it is NEVER spoken): the complete Hindi text of this clip appears on screen word for word in Devanagari script, one phrase at a time:
"धातुओं के धीरे-धीरे अवांछित यौगिकों में बदलने की प्रक्रिया को संक्षारण कहते हैं।"

AUDIO: this clip is completely SILENT. There is no voiceover, no narration, no speech, no singing, no music, no sound effects and no ambient sound of any kind. No voice is generated at any moment. The audio track is empty. The spoken narration is added separately in editing from a different source.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, filling the width, starting close to the top edge, large enough to fill the upper area comfortably. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

NO DIAGRAM IN THIS CLIP (CRITICAL): this clip contains NO three dimensional object of any kind. There is no nail, no iron bar, no metal sheet, no rust, no rust patch, no water drop, no gas molecule, no beaker, no test tube, no arrow, no chemical formula, no shape, no icon and no illustration anywhere in the frame at any moment. The only things on screen are the script text and the plain background. Do not invent, add or imagine any diagram, object or graphic. The space below the script text stays as plain empty background.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE beyond what is written. In the first phrase the words "धीरे-धीरे" are written exactly as given.
- EXACT COUNT: the word "धीरे" appears exactly TWICE in this whole clip, both times inside the first phrase, joined by one single short hyphen as "धीरे-धीरे", written on one line and never split. It never appears a third time, in any size, at any moment.
- EXACT COUNT: the word "संक्षारण" appears exactly ONCE in this whole clip, inside the second phrase only. It is never written a second time, never repeated as a heading and never placed on its own separate line.
- All on-screen text is Hindi written in the Devanagari script, reproduced exactly as given — every matra, every conjunct, every nukta, every anusvara identical to the text in this prompt. Never transliterate into Latin letters, never translate into English, never mix in an English word.
- This clip contains NO digits and NO numbers of any kind, anywhere, at any moment.
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated.
Applying this rule to this clip: the FIRST phrase contains the same word twice, so it is COMPLETELY UNIFORM bold white with NO golden word anywhere in it. The SECOND phrase has ONE golden key word: "संक्षारण"; every other word in it is bold white.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean crisp flat overlay typography on a dark technical background. Never photorealistic. NO fire, NO flame, NO sparks, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: completely empty background. Nothing at all.

ANIMATION TIMELINE:
0.0 s — the first phrase "धातुओं के धीरे-धीरे अवांछित यौगिकों में" pops in at the very top of the frame, fully sharp, completely uniform bold white with no golden word.
4.8 s — the first phrase disappears completely.
4.8–5.0 s — no phrase on screen at all.
5.0 s — the second phrase "बदलने की प्रक्रिया को संक्षारण कहते हैं।" pops in in the same place, fully sharp, with only the word "संक्षारण" golden in place inside the sentence.
10.0 s — the second phrase has faded out and the screen is empty background again.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "धातुओं के धीरे-धीरे अवांछित यौगिकों में"
2. "बदलने की प्रक्रिया को संक्षारण कहते हैं।"

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, curly quotation marks, an em dash, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a third "धीरे", "धीरे" written on its own line, "धीरे-धीरे" split across two lines, a repeated word, a repeated key word, a second "संक्षारण", the word "संक्षारण" written as a heading or title, a golden word in the first phrase, two golden words in the second phrase, a keyword written as a separate line, invented labels, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken Devanagari conjuncts, detached matras, a word split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, English or Latin letters, romanised transliteration, an English heading, the word Corrosion, any digit or number, an automatic subtitle bar at the bottom, an auto-generated subtitle, a burnt-in caption, closed captions, a transcript line, any text that appears because speech was generated, any voiceover, any narration, any spoken words, any human voice, any singing, background music, sound effects, random symbols, camera movement, zoom, scene change, background change, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, any nail, iron bar, metal sheet, rust, rust patch, bright red rust, green patina, a smooth even rust coat, water drop, gas molecule, beaker, test tube, arrow, chemical formula, shape, icon or illustration of any kind, any label plate, equations
```

Notes on choices I locked while writing these four:
- **Seg 1** keeps the digits `12वीं` and `2025` as written (your open question 2 — say the word and I'll spell them out; the digits are on-screen text only, never spoken, so the no-digits-in-spoken-lines rule isn't violated).
- **Seg 1 P1 and P2 got no golden word** — they contain digits, which the style rule treats like a math symbol. Only P3 carries gold.
- **Seg 4 P1 is uniform white** as planned (`धीरे-धीरे` = same word twice + hyphen), with a hard count lock plus a no-line-split ban, since a hyphenated repeat is the exact shape of bugs #7 and #8.
- **Devanagari integrity** is a new correctness line in all four (matras/conjuncts/nukta) plus `broken Devanagari conjuncts, detached matras` in every negative — the Hindi analogue of the garbled-letter bug.
- No image other than the uploaded 9:16 background should be attached; the landscape poster frame you pointed me at is reference art and would push the model toward a full-bleed layout.

Test Segment 1 first, then generate the rest — say go and I'll write 5–17.

Read. One flag before the prompts: that reference frame is a **landscape, full-bleed poster** — exactly the anchor-frame shape the ledger blames for the "diagram crossed the middle" bug. Use it as a *fact reference only* (rust colour, nail look, three-input equation), never as an attached style/anchor frame. §18 is included in Segment 6 regardless.

Style decisions locked for these four:
- **Seg 5** — golden `तरीका` / `उदाहरण`; `आसान` appears in both phrases → EXACT COUNT.
- **Seg 6** — golden `जंग` / `तीन`; nail enters exactly on `जंग`.
- **Seg 7** — `धातु` ×2 across phrases → EXACT COUNT (golden still allowed, repeat isn't inside one phrase).
- **Seg 8** — highest-risk in the pack: P1 and P2 both carry `धातु में अशुद्धियाँ`, so **both go UNIFORM white, no golden word**; only P3 gets a golden word. Hard count locks on all three words.

---

```
VIDEO PROMPT — SEGMENT 5 OF 17

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

AUDIO: this clip is completely SILENT. There is no voiceover, no narration, no speech, no singing, no music, no sound effects and no ambient sound of any kind. No voice is generated at any moment. The audio track is empty. The spoken narration is added separately in editing from a different source.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, starting close to the top edge. The equation sits directly below the script text, comfortably above the invisible middle line, and is large enough that the top half does not look empty. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

NO DIAGRAM IN THIS CLIP (CRITICAL): this clip contains NO three dimensional object of any kind. There is no nail, no iron bar, no metal sheet, no rust patch, no water drop, no gas bubble, no beaker, no arrow, no icon and no illustration anywhere in the frame at any moment. The only things on screen are the script text, the equation, and the plain background. Do not invent, add or imagine any diagram, object or graphic. The space below the equation stays as plain empty background.

EQUATION RULE (CRITICAL): the equation is flat two dimensional overlay text, not a three dimensional object. It is ONE single clean horizontal line of large bold white text with a soft cyan glow, centred below the script text, perfectly sharp, with every character correct and correctly sized. It is not on a card, not in a box, and never stacked onto two lines. If it is too wide, reduce its size until the whole line fits comfortably inside the frame width with clear margins on both sides. It appears exactly once and holds to the end of the clip. The script text stays at the top and the equation stays below it — they never overlap and never swap places. The equation is written in Devanagari exactly as: धातु + वायुमण्डल की गैसें + नमी = संक्षारण — with exactly two plus signs and exactly one equals sign, and with all four Devanagari terms present. The moisture term नमी is never dropped.

HIGHLIGHT RULE (CRITICAL — NO NEW TEXT IS EVER CREATED): when a part of the equation is emphasised, that part of the EXISTING equation simply changes colour and glows brighter in place. NEVER copy a word or symbol out of the equation. NEVER draw a second copy of any word or symbol anywhere. NEVER create a label, plate, chip, callout or floating letter for it. The equation itself is the only place any of its words ever appears.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE. Every word appears exactly the number of times it is written.
- EXACT COUNT: the word "आसान" appears exactly TWICE in total in this clip — once inside the first phrase and once inside the second phrase. Nowhere else, in any size, at any moment.
- EXACT COUNT: the word "धातु" appears exactly ONCE in this clip, inside the equation only. It never appears in any phrase.
- EXACT COUNT: the word "संक्षारण" appears exactly ONCE in this clip, inside the equation only.
- EXACT COUNT: the word "नमी" appears exactly ONCE in this clip, inside the equation only.
- All on-screen text is in Devanagari script. No English word, no Latin letter and no digit appears anywhere in this clip.
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, character by character, with every matra and every conjunct correct.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. In this clip the first phrase has exactly one golden word: "तरीका". The second phrase has exactly one golden word: "उदाहरण". The equation is completely uniform bold white with a soft cyan glow and has NO golden word. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters or mathematical symbols individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean crisp flat overlay typography on a dark technical background. Never photorealistic. NO fire, NO flame, NO sparks, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: completely empty background. Nothing at all.

ANIMATION TIMELINE:
0.0–4.8 s — the first phrase "इसे याद रखने का आसान तरीका है" pops in at the very top of the frame, fully sharp from its first visible frame, with the single word "तरीका" in gold inside the sentence. It holds until 4.8 s, then disappears completely.
At 3.0 s, while the first phrase is still on screen, the equation धातु + वायुमण्डल की गैसें + नमी = संक्षारण pops in on ONE single line below the script text, fully sharp and complete from its first visible frame. It holds, motionless and unchanged in size and position, to the end of the clip.
At 6.5 s the word नमी inside the EXISTING equation turns bright yellow and glows, staying exactly in its place inside the equation, and holds that glow to the end. No copy of it is made anywhere.
4.8–5.0 s — a 0.2 second gap with no phrase on screen. The equation stays.
5.0–10.0 s — the second phrase "और इसका सबसे आसान उदाहरण है" pops in at the very top of the frame, fully sharp from its first visible frame, with the single word "उदाहरण" in gold inside the sentence. It holds to 10.0 s.
The bottom half of the frame stays completely empty for all ten seconds.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "इसे याद रखने का आसान तरीका है"
2. "धातु + वायुमण्डल की गैसें + नमी = संक्षारण"
3. "और इसका सबसे आसान उदाहरण है"

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, curly quotation marks, em dashes, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, invented labels, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken Devanagari conjuncts, missing or floating matras, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, any voiceover, any narration, any spoken words, any human voice, any singing, background music, sound effects, an automatic caption, an auto-generated subtitle, a burnt-in subtitle bar, closed captions, a transcript line, any text that appears because speech was generated, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, any nail, iron bar, metal sheet, rust patch, water drop, gas bubble, beaker, arrow, icon or illustration, a copy of any word taken out of the equation, a floating word "धातु" or "नमी" or "संक्षारण" anywhere outside the equation, any label plate, any chip, any callout, any leader line, two copies of the equation, the equation moving or resizing, the equation stacked onto two lines, the equation appearing before 3.0 seconds, a golden word inside the equation, the word नमी missing from the equation, only two terms on the left side of the equation, a fourth term added to the equation, an English word, a Latin letter, the heading "Corrosion" in English, any digit, chemical formulas such as FeO or Fe2O3, wrong or extra plus and equals signs, extra equations
```

---

```
VIDEO PROMPT — SEGMENT 6 OF 17

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

AUDIO: this clip is completely SILENT. There is no voiceover, no narration, no speech, no singing, no music, no sound effects and no ambient sound of any kind. No voice is generated at any moment. The audio track is empty. The spoken narration is added separately in editing from a different source.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, starting close to the top edge. The diagram sits directly below the script text and fills the space between the text and the invisible middle line, so the top half never looks empty. The lowest part of the diagram stops with a clear visible gap above the invisible middle line and never touches it; if it does not fit, make it smaller. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

SIZE AND POSITION CHECK (CRITICAL): before anything is drawn, the diagram is scaled so that its complete height — including every arrow, glow and shadow — fits inside the upper half of the frame with a clear visible margin still left below it. If any part of the diagram would reach the middle of the frame, the whole diagram is made smaller until it does not. The diagram never grows, drifts downward, expands or scales up at any moment during the clip. The lower half of the frame contains nothing but the background from the first frame to the last.

3D RENDER QUALITY (CRITICAL — THIS MAKES THE DIAGRAM LOOK THREE DIMENSIONAL):
The diagram is a real three dimensional object rendered in depth, not a flat drawing.
- CAMERA: a fixed three-quarter view from slightly above the object, so the viewer looks slightly down at it and can clearly read its roundness. Never a flat straight-on front view.
- PERSPECTIVE: circles that run around the object appear as flattened ellipses because of the viewing angle, becoming flatter near the top and bottom and rounder near the middle. Nothing is drawn as a plain flat circle.
- DEPTH: the parts nearest the camera are brighter, thicker and sharper. The parts on the far side are noticeably dimmer, softer and less detailed. This difference is clear and obvious.
- LIGHTING: one soft cool rim light along the upper left edge and a gentle ambient fill, giving a rounded sculpted look with a soft falloff toward the lower right.
- MATERIAL: the bare metal is a smooth dull metallic surface with a faint specular highlight near the upper left; the corroded areas are matte, rough and non-reflective.
- FORESHORTENING: the pointed end of the object aimed toward the camera looks shorter and thicker, and the end aimed away looks longer and thinner. The two ends are never drawn the same size on screen.
- MOTION: the object turns very slowly and steadily around its long axis so the depth reads clearly. It never wobbles, never squashes, never deforms and never changes size once settled.

DIAGRAM SPECIFICATION (build exactly this, nothing else):
- THE IRON NAIL: one single iron nail lying at a gentle diagonal, rendered in full three dimensions, with a round flat head at one end and a tapering point at the other. Its uncorroded metal is GREY-SILVER with a dull metallic sheen — never chrome-mirror bright, never yellow, never golden, never white.
- THE RUST: rough patches of rust that grow outward from the nail's surface in uneven blotches, spreading from the middle of the shaft toward both ends. The rust is REDDISH-BROWN to ORANGE-BROWN, matte, flaky and powdery, with a visibly crumbly raised texture standing slightly proud of the metal. It is NEVER bright red, never green, never black, never blue and never a smooth even glossy coat. It covers the nail only in patches — clean grey-silver metal always stays visible between the patches, and the patches never join into one continuous sealed protective film over the whole nail. A few small rust flakes lift and detach at the edges of the patches, exposing fresh grey metal beneath.
- LABELS: this clip has NO labels at all. No plate, no chip, no tag, no letter, no leader line and no arrow of any kind. Never invent a label.

DIAGRAM TIMING SYNC (CRITICAL): every object appears at the exact moment its name is visible in the written phrase on screen, and never a frame before. The nail with its rust appears only at the moment described in the timeline. Once it appears it stays to the end of the clip.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE. Every word appears exactly the number of times it is written.
- EXACT COUNT: the word "जंग" appears exactly ONCE in this whole clip, inside the first phrase only. Nowhere else, in any size, at any moment.
- EXACT COUNT: the word "संक्षारण" appears exactly ONCE in this whole clip, inside the second phrase only.
- EXACT COUNT: the word "तीन" appears exactly ONCE in this whole clip, inside the second phrase only. No numbered list, no numerals and no counting marks appear anywhere.
- All on-screen text is in Devanagari script. No English word, no Latin letter and no digit appears anywhere in this clip.
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, character by character, with every matra and every conjunct correct.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. In this clip the first phrase has exactly one golden word: "जंग". The second phrase has exactly one golden word: "तीन". Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean, glossy, textbook-style chemistry illustration rendered in three dimensions — smooth shapes, flat bright colours, soft even glow, like a modern NCERT diagram built in 3D. Never photorealistic. NO fire, NO flame, NO burning, NO spark, NO ember, NO explosion, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: completely empty background. Nothing at all.

ANIMATION TIMELINE:
0.0–4.8 s — the first phrase "लोहे में जंग लगना।" pops in at the very top of the frame, fully sharp from its first visible frame, with the single word "जंग" in gold inside the sentence. It holds until 4.8 s, then disappears completely.
At 1.4 s, exactly as the word जंग is visible on screen inside the first phrase, the grey-silver iron nail pops in below the script text with its reddish-brown flaky rust patches already on it, correctly sized to sit entirely in the upper half with a clear gap above the middle of the frame. From 1.4 s onward it turns very slowly and steadily around its long axis and never changes size or position again.
4.8–5.0 s — a 0.2 second gap with no phrase on screen. The nail stays.
5.0–10.0 s — the second phrase "अब संक्षारण को प्रभावित करने वाले तीन कारक समझो।" pops in at the very top of the frame, fully sharp from its first visible frame, with the single word "तीन" in gold inside the sentence. It holds to 10.0 s while the nail continues its slow turn below it.
The bottom half of the frame stays completely empty for all ten seconds.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "लोहे में जंग लगना।"
2. "अब संक्षारण को प्रभावित करने वाले तीन कारक समझो।"

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, the diagram crossing the middle of the frame, the diagram touching the middle of the frame, the diagram growing or expanding during the clip, the diagram drifting downward, an arrow reaching into the lower half, the illustration filling the whole frame, a full-frame poster layout, a landscape composition, two phrases visible at the same time, garbled letters during a transition, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, curly quotation marks, em dashes, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, invented labels, label plates, chips, tags, callouts, leader lines, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken Devanagari conjuncts, missing or floating matras, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, any voiceover, any narration, any spoken words, any human voice, any singing, background music, sound effects, an automatic caption, an auto-generated subtitle, a burnt-in subtitle bar, closed captions, a transcript line, any text that appears because speech was generated, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, a flat two dimensional drawing of a nail instead of a three dimensional object, a straight-on front view with no depth, a diagram that looks like a flat line drawing, bright red rust, green rust, green patina on the iron, black tarnish on the iron, blue corrosion on the iron, smooth glossy evenly coloured rust, rust as a continuous sealed protective film covering the whole nail, a uniform unbroken oxide coating over the iron, a nail with no bare grey metal left visible, a chrome-mirror bright nail, a golden or yellow nail, more than one nail, a second nail, a screw or bolt instead of a nail, water drops, gas bubbles, beakers, test tubes, chemical formulas, equations, any English word, any Latin letter, any digit, the nail appearing before 1.4 seconds, a numbered list, numerals for the count
```

---

```
VIDEO PROMPT — SEGMENT 7 OF 17

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

AUDIO: this clip is completely SILENT. There is no voiceover, no narration, no speech, no singing, no music, no sound effects and no ambient sound of any kind. No voice is generated at any moment. The audio track is empty. The spoken narration is added separately in editing from a different source.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, filling the width, starting close to the top edge, large enough to fill the upper area comfortably. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

NO DIAGRAM IN THIS CLIP (CRITICAL): this clip contains NO three dimensional object of any kind. There is no nail, no iron bar, no metal sheet, no rust patch, no water drop, no gas bubble, no beaker, no reactivity chart, no arrow, no field line, no shape, no icon and no illustration anywhere in the frame at any moment. The only things on screen are the script text and the plain background. Do not invent, add or imagine any diagram, object or graphic. The space below the script text stays as plain empty background.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE. Every word appears exactly the number of times it is written.
- EXACT COUNT: the word "धातु" appears exactly TWICE in total in this clip — once inside the first phrase and once inside the second phrase. It never appears a third time, in any size, at any moment, and it never appears twice inside the same phrase.
- EXACT COUNT: the word "पहला" appears exactly ONCE in this clip, inside the first phrase only. No numeral, no numbered bullet and no counting mark is ever drawn beside it or anywhere else.
- EXACT COUNT: the word "संक्षारण" appears exactly ONCE in this clip, inside the third phrase only.
- All on-screen text is in Devanagari script. No English word, no Latin letter and no digit appears anywhere in this clip.
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, character by character, with every matra and every conjunct correct. The commas at the end of the first and second phrases are the only punctuation in those phrases.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. In this clip the first phrase has exactly one golden word: "प्रकृति". The second phrase has exactly one golden word: "क्रियाशील". The third phrase has exactly one golden word: "संक्षारण". The word "धातु" is NEVER golden in either phrase. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean crisp flat overlay typography on a dark technical background. Never photorealistic. NO fire, NO flame, NO sparks, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: completely empty background. Nothing at all.

ANIMATION TIMELINE:
0.0–3.3 s — the first phrase "पहला, धातु की प्रकृति," pops in at the very top of the frame, fully sharp from its first visible frame, with the single word "प्रकृति" in gold inside the sentence. It disappears completely at 3.3 s.
3.3–3.5 s — a 0.2 second gap with nothing on screen at all.
3.5–6.6 s — the second phrase "मतलब धातु जितनी अधिक क्रियाशील होगी," pops in in the same place, fully sharp from its first visible frame, with the single word "क्रियाशील" in gold inside the sentence. It disappears completely at 6.6 s.
6.6–6.8 s — a 0.2 second gap with nothing on screen at all.
6.8–10.0 s — the third phrase "उस पर संक्षारण उतनी जल्दी होगा।" pops in in the same place, fully sharp from its first visible frame, with the single word "संक्षारण" in gold inside the sentence. It holds to 10.0 s and the clip ends with it on screen.
The bottom half of the frame stays completely empty for all ten seconds. Nothing else ever appears.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "पहला, धातु की प्रकृति,"
2. "मतलब धातु जितनी अधिक क्रियाशील होगी,"
3. "उस पर संक्षारण उतनी जल्दी होगा।"

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, curly quotation marks, em dashes, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, a third copy of the word "धातु", the word "धातु" written twice inside one phrase, the word "धातु" rendered in gold, invented labels, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken Devanagari conjuncts, missing or floating matras, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, any voiceover, any narration, any spoken words, any human voice, any singing, background music, sound effects, an automatic caption, an auto-generated subtitle, a burnt-in subtitle bar, closed captions, a transcript line, any text that appears because speech was generated, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, any nail, iron bar, metal sheet, rust patch, water drop, gas bubble, beaker, arrow, shape, icon or illustration of any kind, a reactivity series list, a metal symbol such as Fe or Zn or Cu, any label plate, equations, any English word, any Latin letter, any digit, a numeral beside the word पहला, a numbered list, bullet points, a second or third item appearing in this clip
```

---

```
VIDEO PROMPT — SEGMENT 8 OF 17

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

AUDIO: this clip is completely SILENT. There is no voiceover, no narration, no speech, no singing, no music, no sound effects and no ambient sound of any kind. No voice is generated at any moment. The audio track is empty. The spoken narration is added separately in editing from a different source.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, filling the width, starting close to the top edge, large enough to fill the upper area comfortably. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

NO DIAGRAM IN THIS CLIP (CRITICAL): this clip contains NO three dimensional object of any kind. There is no nail, no iron bar, no metal sheet, no rust patch, no impurity speck, no water drop, no gas bubble, no beaker, no arrow, no shape, no icon and no illustration anywhere in the frame at any moment. The only things on screen are the script text and the plain background. Do not invent, add or imagine any diagram, object or graphic. The space below the script text stays as plain empty background.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT — THIS CLIP REPEATS A PHRASE FRAGMENT AND MUST BE COUNTED EXACTLY):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE. Every word appears exactly the number of times it is written.
- EXACT COUNT: the word "धातु" appears exactly TWICE in total in this clip — once inside the first phrase and once inside the second phrase. It never appears a third time, in any size, at any moment, and it never appears twice inside the same phrase.
- EXACT COUNT: the word "में" appears exactly TWICE in total in this clip — once inside the first phrase and once inside the second phrase. Never a third time, never twice inside one phrase.
- EXACT COUNT: the word "अशुद्धियाँ" appears exactly TWICE in total in this clip — once inside the first phrase and once inside the second phrase. It never appears a third time, in any size, at any moment, and it never appears twice inside the same phrase.
- The words "धातु में अशुद्धियाँ" appear together as a group exactly TWICE in this whole clip — once at the end of the first phrase and once at the start of the second phrase — and these two occurrences are NEVER visible at the same moment, because only one phrase is ever on screen at a time.
- EXACT COUNT: the word "दूसरा" appears exactly ONCE in this clip, inside the first phrase only. No numeral, no numbered bullet and no counting mark is ever drawn beside it or anywhere else.
- EXACT COUNT: the word "संक्षारण" appears exactly ONCE in this clip, inside the third phrase only.
- All on-screen text is in Devanagari script. No English word, no Latin letter and no digit appears anywhere in this clip.
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, character by character, with every matra and every conjunct correct, including the nasal mark on "अशुद्धियाँ".
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. In this clip the FIRST phrase is rendered COMPLETELY UNIFORM in bold white with NO golden word, and the SECOND phrase is also rendered COMPLETELY UNIFORM in bold white with NO golden word, because they share the same words. Only the THIRD phrase has exactly one golden word: "संक्षारण". The words "धातु" and "अशुद्धियाँ" are NEVER golden, never coloured, never enlarged and never emphasised in any way. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another — in particular, the first phrase is NOT transformed, extended or re-used to build the second phrase even though they share words; the first phrase is removed completely and the second phrase is drawn fresh. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean crisp flat overlay typography on a dark technical background. Never photorealistic. NO fire, NO flame, NO sparks, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: completely empty background. Nothing at all.

ANIMATION TIMELINE:
0.0–3.3 s — the first phrase "दूसरा, धातु में अशुद्धियाँ," pops in at the very top of the frame, fully sharp from its first visible frame, completely uniform bold white with no golden word. It disappears completely at 3.3 s.
3.3–3.5 s — a 0.2 second gap with nothing on screen at all. The screen is fully clear of text before the next phrase begins.
3.5–6.6 s — the second phrase "मतलब धातु में अशुद्धियाँ होने पर" pops in in the same place, drawn fresh, fully sharp from its first visible frame, completely uniform bold white with no golden word. It disappears completely at 6.6 s.
6.6–6.8 s — a 0.2 second gap with nothing on screen at all.
6.8–10.0 s — the third phrase "संक्षारण अधिक तेजी से होगा।" pops in in the same place, fully sharp from its first visible frame, with the single word "संक्षारण" in gold inside the sentence. It holds to 10.0 s and the clip ends with it on screen.
The bottom half of the frame stays completely empty for all ten seconds. Nothing else ever appears.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "दूसरा, धातु में अशुद्धियाँ,"
2. "मतलब धातु में अशुद्धियाँ होने पर"
3. "संक्षारण अधिक तेजी से होगा।"

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, the first phrase still visible while the second phrase appears, garbled letters during a transition, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, curly quotation marks, em dashes, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, two copies of "धातु में अशुद्धियाँ" on screen at the same moment, a third copy of the word "धातु", a third copy of the word "अशुद्धियाँ", the word "धातु" written twice inside one phrase, the word "अशुद्धियाँ" written twice inside one phrase, a repeated word, a repeated key word, a golden word in the first phrase, a golden word in the second phrase, the word "धातु" rendered in gold, the word "अशुद्धियाँ" rendered in gold, a keyword written as a separate line, invented labels, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, a missing nasal mark on अशुद्धियाँ, broken Devanagari conjuncts, missing or floating matras, broken words split across lines, merged letters, half-formed letters, morphing or warping text, one phrase morphing into the next, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, any voiceover, any narration, any spoken words, any human voice, any singing, background music, sound effects, an automatic caption, an auto-generated subtitle, a burnt-in subtitle bar, closed captions, a transcript line, any text that appears because speech was generated, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, any nail, iron bar, metal sheet, rust patch, impurity speck, water drop, gas bubble, beaker, arrow, shape, icon or illustration of any kind, a comparison of pure and impure samples drawn as a picture, any label plate, equations, any English word, any Latin letter, any digit, a numeral beside the word दूसरा, a numbered list, bullet points
```

---

Two things still open from the plan that affect later segments, not these four: the `गैल्वेनीकरण` spelling (Seg 13) and whether `2025` / `12वीं` stay as digits (Seg 1). Test Segment 6 first — it is the only diagram in this batch and the one carrying the §18 top-half fix.

Read the reference frame. Two flags before the prompts:

- **The frame is landscape, full-bleed, white-background, and label-heavy** — that is exactly the anchor-frame shape that caused the "diagram crossed the middle line" bug in the sickle-cell test (bug ledger, Aug 2026). I have **not** used it as an anchor. If you feed it to the tool as a reference image, expect the poster layout to fight §18. The uploaded Arivihan slate background is the only image that should go in.
- The frame's `जंग लगना` / `अवांछित यौगिक` label plates would duplicate words already in the phrases — per plan, **LABELS: none** in Seg 11.

Segments 9–12 below. Silent clips (§17), uploaded background (§15), no §16, no `logo`/`watermark`/`badge`/`wordmark` anywhere.

---

**SEGMENT 9 OF 17** — TEXT_ONLY

```
VIDEO PROMPT — SEGMENT 9 OF 17

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

ON-SCREEN SCRIPT (this text appears on screen only — it is NOT spoken and no voice is generated): "तीसरा, वातावरण, मतलब हवा, नमी और कुछ गैसों की मौजूदगी संक्षारण को बढ़ाती है।"

AUDIO: this clip is completely SILENT. There is no voiceover, no narration, no speech, no singing, no music, no sound effects and no ambient sound of any kind. No voice is generated at any moment. The audio track is empty. The spoken narration is added separately in editing from a different source.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, filling the width, starting close to the top edge, large enough to fill the upper area comfortably. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

NO DIAGRAM IN THIS CLIP (CRITICAL): this clip contains NO three dimensional object of any kind. There is no nail, no iron bar, no metal sheet, no rust patch, no water droplet, no gas bubble, no sphere, no arrow, no layer, no coating, no cross-section, no beaker, no cell, no shape, no icon and no illustration anywhere in the frame at any moment. The only things on screen are the script text and the plain background. Do not invent, add or imagine any diagram, object or graphic. The space below the script text stays as plain empty background.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE. Every word appears exactly the number of times it is written.
- EXACT COUNT: the word "वातावरण" appears exactly ONCE in total in this clip — inside the first phrase only. Nowhere else, in any size, at any moment.
- EXACT COUNT: the word "नमी" appears exactly ONCE in total in this clip — inside the second phrase only. Nowhere else, in any size, at any moment.
- EXACT COUNT: the word "संक्षारण" appears exactly ONCE in total in this clip — inside the third phrase only. Nowhere else, in any size, at any moment.
- EXACT COUNT: the word "और" appears exactly ONCE in total in this clip — inside the second phrase only. Nowhere else, at any moment.
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol. The text is Devanagari Hindi; every matra, every bindu and every conjunct is formed correctly and completely.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt. No English words anywhere.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated.
In this clip: in the first phrase the single golden word is "वातावरण". In the second phrase the single golden word is "नमी". In the third phrase the single golden word is "संक्षारण". There is no other golden word anywhere.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean crisp flat overlay typography on a dark technical background. Never photorealistic. NO fire, NO flame, NO sparks, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: completely empty background. Nothing at all.

ANIMATION TIMELINE:
0.0 s — the first phrase "तीसरा, वातावरण," pops in at the very top of the frame, fully sharp, with the word "वातावरण" golden in place inside the sentence.
3.3 s — the first phrase disappears completely.
3.5 s — the second phrase "मतलब हवा, नमी और कुछ गैसों की मौजूदगी" pops in in the same place, fully sharp, with the word "नमी" golden in place inside the sentence.
6.6 s — the second phrase disappears completely.
6.8 s — the third phrase "संक्षारण को बढ़ाती है।" pops in in the same place, fully sharp, with the word "संक्षारण" golden in place inside the sentence.
9.8 s — the third phrase fades out completely.
10.0 s — the frame is empty background again.
Throughout: nothing else ever appears. The bottom half of the frame contains nothing but the background from the first frame to the last.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "तीसरा, वातावरण,"
2. "मतलब हवा, नमी और कुछ गैसों की मौजूदगी"
3. "संक्षारण को बढ़ाती है।"
Nothing else is written anywhere on screen at any moment.

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, broken Devanagari conjuncts, missing or floating matras, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, curly quotes, em-dashes, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, a second "वातावरण", a second "नमी", a second "संक्षारण", invented labels, any label plate, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, English words, digits, chemical formulas, equations, any nail, iron bar, metal sheet, rust patch, water droplet, gas bubble, sphere, arrow, coating, layer, cross-section, shape, icon or illustration of any kind, a reddish-brown rust patch, a green patina, a black tarnish, a reactivity series list, any voiceover, any narration, any spoken words, any human voice, any singing, background music, sound effects, an automatic caption, an auto-generated subtitle, a burnt-in subtitle bar, closed captions, a transcript line, any text that appears because speech was generated, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed
```

---

**SEGMENT 10 OF 17** — TEXT_ONLY

```
VIDEO PROMPT — SEGMENT 10 OF 17

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

ON-SCREEN SCRIPT (this text appears on screen only — it is NOT spoken and no voice is generated): "बस, इन तीनों को याद रखो धातु की प्रकृति, अशुद्धियाँ और वातावरण। अब समझते हैं संक्षारण से बचाव के तीन उपाय।"

AUDIO: this clip is completely SILENT. There is no voiceover, no narration, no speech, no singing, no music, no sound effects and no ambient sound of any kind. No voice is generated at any moment. The audio track is empty. The spoken narration is added separately in editing from a different source.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, filling the width, starting close to the top edge, large enough to fill the upper area comfortably. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

NO DIAGRAM IN THIS CLIP (CRITICAL): this clip contains NO three dimensional object of any kind. There is no nail, no iron bar, no metal sheet, no rust patch, no water droplet, no gas bubble, no sphere, no arrow, no layer, no coating, no cross-section, no beaker, no cell, no shape, no icon and no illustration anywhere in the frame at any moment. There is also NO numbered list, NO bullet list and NO three-item chart of any kind — the three ideas exist only as the words inside the written phrases. The only things on screen are the script text and the plain background. Do not invent, add or imagine any diagram, object, list or graphic. The space below the script text stays as plain empty background.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE. Every word appears exactly the number of times it is written.
- EXACT COUNT: the word "तीनों" appears exactly ONCE in total in this clip — inside the first phrase only. Nowhere else, at any moment.
- EXACT COUNT: the word "तीन" appears exactly ONCE in total in this clip — inside the third phrase only. It is never written a second time, and it never appears inside the first phrase.
- EXACT COUNT: the word "वातावरण" appears exactly ONCE in total in this clip — inside the second phrase only. Nowhere else, at any moment.
- EXACT COUNT: the word "संक्षारण" appears exactly ONCE in total in this clip — inside the third phrase only. Nowhere else, at any moment.
- EXACT COUNT: the word "अशुद्धियाँ" appears exactly ONCE in total in this clip — inside the second phrase only. Nowhere else, at any moment.
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol. The text is Devanagari Hindi; every matra, every bindu and every conjunct is formed correctly and completely.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt. No English words anywhere, and no digits anywhere.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated.
In this clip: in the first phrase the single golden word is "याद". In the second phrase the single golden word is "वातावरण". In the third phrase the single golden word is "बचाव". There is no other golden word anywhere.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean crisp flat overlay typography on a dark technical background. Never photorealistic. NO fire, NO flame, NO sparks, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: completely empty background. Nothing at all.

ANIMATION TIMELINE:
0.0 s — the first phrase "बस, इन तीनों को याद रखो" pops in at the very top of the frame, fully sharp, with the word "याद" golden in place inside the sentence.
3.3 s — the first phrase disappears completely.
3.5 s — the second phrase "धातु की प्रकृति, अशुद्धियाँ और वातावरण।" pops in in the same place, fully sharp, with the word "वातावरण" golden in place inside the sentence. It is written as one running sentence on at most three centred lines — never as a numbered list, never as separate stacked items.
6.6 s — the second phrase disappears completely.
6.8 s — the third phrase "अब समझते हैं संक्षारण से बचाव के तीन उपाय।" pops in in the same place, fully sharp, with the word "बचाव" golden in place inside the sentence.
9.8 s — the third phrase fades out completely.
10.0 s — the frame is empty background again.
Throughout: nothing else ever appears. The bottom half of the frame contains nothing but the background from the first frame to the last.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "बस, इन तीनों को याद रखो"
2. "धातु की प्रकृति, अशुद्धियाँ और वातावरण।"
3. "अब समझते हैं संक्षारण से बचाव के तीन उपाय।"
Nothing else is written anywhere on screen at any moment.

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, broken Devanagari conjuncts, missing or floating matras, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, curly quotes, em-dashes, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, a second "वातावरण", a second "संक्षारण", a second "तीन", the word "तीन" inside the first phrase, a numbered list, a bulleted list, the numerals १ २ ३ or 1 2 3 on screen, a four-item list, a two-item list, invented labels, any label plate, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, English words, the English word Corrosion, digits, chemical formulas, equations, any nail, iron bar, metal sheet, rust patch, water droplet, gas bubble, sphere, arrow, coating, layer, cross-section, shape, icon or illustration of any kind, a reddish-brown rust patch, a green patina, a black tarnish, a reactivity series list, any voiceover, any narration, any spoken words, any human voice, any singing, background music, sound effects, an automatic caption, an auto-generated subtitle, a burnt-in subtitle bar, closed captions, a transcript line, any text that appears because speech was generated, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed
```

---

**SEGMENT 11 OF 17** — DIAGRAM (iron bar + unbroken protective coating). Ends holding the diagram.

```
VIDEO PROMPT — SEGMENT 11 OF 17

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

ON-SCREEN SCRIPT (this text appears on screen only — it is NOT spoken and no voice is generated): "पहला, रोधिका स्थापित करना, मतलब लोहे पर पेंट, ग्रीस या तेल की परत लगाकर उसे हवा और नमी से बचाना।"

AUDIO: this clip is completely SILENT. There is no voiceover, no narration, no speech, no singing, no music, no sound effects and no ambient sound of any kind. No voice is generated at any moment. The audio track is empty. The spoken narration is added separately in editing from a different source.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, starting close to the top edge. The diagram sits directly below the script text and fills the space between the text and the invisible middle line, so the top half never looks empty. The lowest part of the diagram stops with a clear visible gap above the invisible middle line and never touches it; if it does not fit, make it smaller. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

SIZE AND POSITION CHECK (CRITICAL): before anything is drawn, the diagram is scaled so that its complete height — including every arrow, glow and shadow — fits inside the upper half of the frame with a clear visible margin still left below it. If any part of the diagram would reach the middle of the frame, the whole diagram is made smaller until it does not. The diagram never grows, drifts downward, expands or scales up at any moment during the clip. The lower half of the frame contains nothing but the background from the first frame to the last.

3D RENDER QUALITY (CRITICAL — THIS MAKES THE DIAGRAM LOOK THREE DIMENSIONAL):
The diagram is a real three dimensional object rendered in depth, not a flat drawing.
- CAMERA: a fixed three-quarter view from slightly above the object, so the viewer looks slightly down at it and can clearly read its roundness. Never a flat straight-on front view.
- PERSPECTIVE: circles that run around the object appear as flattened ellipses because of the viewing angle, becoming flatter near the top and bottom and rounder near the middle. Nothing is drawn as a plain flat circle.
- DEPTH: the parts nearest the camera are brighter, thicker and sharper. The parts on the far side are noticeably dimmer, thinner and softer. This difference is clear and obvious.
- LIGHTING: one soft cool rim light along the upper left edge and a gentle ambient fill, giving a rounded sculpted look with a soft falloff toward the lower right.
- MATERIAL: a smooth surface with a faint specular highlight near the upper left, and a soft inner glow.
- FORESHORTENING: any arrow pointing toward the camera looks shorter and thicker with a larger arrowhead, and any arrow pointing away looks longer and thinner. They are never all the same length on screen.
- MOTION: the object turns very slowly and steadily around its vertical axis so the depth reads clearly. It never wobbles, never squashes, never deforms and never changes size once settled.

DIAGRAM SPECIFICATION (build exactly this, nothing else):
- THE IRON BAR: one short horizontal three dimensional iron bar with rounded ends, rendered in full depth in the three-quarter view from slightly above. Its material is dull grey-silver metal with a soft brushed sheen and a faint specular highlight along its upper left edge — a matte industrial grey, never a chrome mirror, never yellow, never golden, never orange. Its surface is completely clean and bare when it first appears: there is no rust, no reddish-brown patch, no flaking, no green film and no discoloration on it at any moment of this clip. It turns very slowly and steadily around its vertical axis. It never becomes hollow, never wobbles and never deforms.
- THE PROTECTIVE COATING LAYER: one single continuous unbroken band of glossy deep teal-blue material lying ON TOP OF the iron bar, covering its entire upper and outer surface from one rounded end to the other rounded end with no gap, no break, no crack, no scratch, no hole and no missing patch anywhere along it. It reads clearly as a separate layer sitting above the grey metal — the grey iron stays visible below it and the coating is never drawn underneath the iron. It is smooth and even, with a wet glossy specular highlight along its upper left, and it wraps over the bar following its curve in three dimensions. It grows on smoothly from one end to the other over 0.5 seconds when it appears, and once complete it stays complete and unbroken to the end of the clip.
- THE ENVIRONMENT ABOVE: exactly FOUR small pale blue-white water droplet shapes and exactly FOUR small pale blue translucent spheres, all rendered in three dimensions, floating in the space ABOVE the coated bar, arranged in an even scattered row with clear space between them. Each one drifts gently downward a short distance, meets the glossy coating layer, and is stopped there with a small soft pale ring of light at the point of contact — none of them ever passes through the coating, and none of them ever touches the grey iron. They never change colour, never become red, never become brown and never leave a mark on the bar.
- LABELS: this clip has NO labels at all. No plate, no chip, no tag, no number, no leader line and no floating letter exists anywhere in the scene. Never invent a label.

DIAGRAM TIMING SYNC (CRITICAL): every object appears at the exact moment its name is visible in the written phrase on screen, and never a frame before. Once an object appears it stays to the end of the clip.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE. Every word appears exactly the number of times it is written.
- EXACT COUNT: the word "लोहे" appears exactly ONCE in total in this clip — inside the second phrase only. Nowhere else, in any size, at any moment.
- EXACT COUNT: the word "परत" appears exactly ONCE in total in this clip — inside the second phrase only. It is never repeated and never written next to the diagram.
- EXACT COUNT: the word "नमी" appears exactly ONCE in total in this clip — inside the third phrase only. Nowhere else, at any moment.
- EXACT COUNT: the word "रोधिका" appears exactly ONCE in total in this clip — inside the first phrase only. Nowhere else, at any moment.
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol. The text is Devanagari Hindi; every matra, every bindu and every conjunct is formed correctly and completely.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt. No English words anywhere, and no digits anywhere.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated.
In this clip: in the first phrase the single golden word is "रोधिका". In the second phrase the single golden word is "परत". In the third phrase the single golden word is "नमी". There is no other golden word anywhere.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean, glossy, textbook-style chemistry illustration rendered in three dimensions — smooth shapes, flat bright colours, soft even glow, like a modern NCERT diagram built in 3D. Never photorealistic. NO fire, NO flame, NO burning, NO spark, NO ember, NO explosion, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: completely empty background. Nothing at all.

ANIMATION TIMELINE:
0.0 s — the first phrase "पहला, रोधिका स्थापित करना," pops in at the very top of the frame, fully sharp, with the word "रोधिका" golden in place inside the sentence.
3.3 s — the first phrase disappears completely.
3.5 s — the second phrase "मतलब लोहे पर पेंट, ग्रीस या तेल की परत लगाकर" pops in in the same place, fully sharp, with the word "परत" golden in place inside the sentence.
4.0 s — exactly as the word लोहे is visible on screen, the bare grey iron bar pops in in the space below the script text, already correctly sized inside the upper half, and begins its very slow steady turn. It is completely clean, with no rust anywhere.
5.6 s — exactly as the word परत is visible on screen, the glossy deep teal-blue coating layer begins to grow across the top and outer surface of the iron bar from its left end to its right end, completing as one continuous unbroken layer by 6.1 s. It stays complete for the rest of the clip.
6.6 s — the second phrase disappears completely.
6.8 s — the third phrase "उसे हवा और नमी से बचाना।" pops in in the same place, fully sharp, with the word "नमी" golden in place inside the sentence.
7.4 s — exactly as the words हवा and नमी are visible on screen, the four pale blue translucent spheres and the four pale blue-white droplets pop in above the coated bar and begin drifting gently downward.
8.4 s — each droplet and each sphere reaches the glossy coating layer and is stopped there, each making one small soft pale ring of light at the point of contact. None passes through. They hold in place.
9.8 s — the third phrase fades out completely. The iron bar with its complete unbroken coating layer, and the eight small shapes resting against it, remain on screen.
10.0 s — the diagram is still on screen, unchanged, still inside the upper half.
Throughout: the diagram never grows, never drifts downward and never crosses the middle of the frame. No rust ever appears on the bar.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "पहला, रोधिका स्थापित करना,"
2. "मतलब लोहे पर पेंट, ग्रीस या तेल की परत लगाकर"
3. "उसे हवा और नमी से बचाना।"
Nothing else is written anywhere on screen at any moment. The diagram carries no text of any kind.

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, the diagram crossing the middle of the frame, the diagram touching the middle of the frame, the diagram growing or expanding during the clip, the diagram drifting downward, an arrow reaching into the lower half, an inset circle in the lower half, the illustration filling the whole frame, a full-frame poster layout, a landscape composition, a white or light background, two phrases visible at the same time, garbled letters during a transition, broken Devanagari conjuncts, missing or floating matras, a flat two dimensional drawing instead of a three dimensional bar, a straight-on front view with no depth, a diagram that looks like a flat line drawing, a squashed or wobbling bar, the iron bar appearing before 4.0 seconds, the coating layer appearing before 5.6 seconds, the droplets or spheres appearing before 7.4 seconds, a broken coating layer, a coating layer with a gap, a crack, a scratch or a missing patch, a coating layer drawn underneath the iron, the coating and the iron swapped in order, a droplet or sphere passing through the coating, a droplet or sphere touching the grey iron, more than four droplets, more than four spheres, a fifth droplet, a fifth sphere, any rust on the bar, a reddish-brown patch, an orange-brown flake, a bright red coating, a smooth even red coat, a green patina on iron, a black tarnish on iron, a chrome-mirror bar, a golden bar, a shiny golden coating, a zinc layer, a tin coating, a copper coating, an electroplating cell, a beaker, an electrolyte, electrodes, a reactivity series list, a rust layer drawn as a sealed protective film that stops corrosion, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, curly quotes, em-dashes, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, a second "लोहे", a second "परत", a second "नमी", invented labels, any label plate, any chip, any tag, any callout, any leader line, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, English words, the English word Corrosion, digits, chemical formulas, equations, any voiceover, any narration, any spoken words, any human voice, any singing, background music, sound effects, an automatic caption, an auto-generated subtitle, a burnt-in subtitle bar, closed captions, a transcript line, any text that appears because speech was generated, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed
```

---

**SEGMENT 12 OF 17** — TEXT_ONLY, hard cut from Seg 11 (starts empty)

```
VIDEO PROMPT — SEGMENT 12 OF 17

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

ON-SCREEN SCRIPT (this text appears on screen only — it is NOT spoken and no voice is generated): "दूसरा, समर्पित बचाव, मतलब लोहे से अधिक क्रियाशील धातु की तह चढ़ाना, जो पहले नष्ट होकर लोहे को बचाती है।"

AUDIO: this clip is completely SILENT. There is no voiceover, no narration, no speech, no singing, no music, no sound effects and no ambient sound of any kind. No voice is generated at any moment. The audio track is empty. The spoken narration is added separately in editing from a different source.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, filling the width, starting close to the top edge, large enough to fill the upper area comfortably. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

NO DIAGRAM IN THIS CLIP (CRITICAL): this clip contains NO three dimensional object of any kind. There is no nail, no iron bar, no metal sheet, no coating, no layer, no cross-section, no rust patch, no water droplet, no gas bubble, no sphere, no arrow, no beaker, no cell, no shape, no icon and no illustration anywhere in the frame at any moment. Nothing is carried over from the previous clip — the previous scene does not continue, does not reappear and does not fade in. The only things on screen are the script text and the plain background. Do not invent, add or imagine any diagram, object or graphic. The space below the script text stays as plain empty background.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE beyond what is written. Every word appears exactly the number of times it is written.
- EXACT COUNT: the word "लोहे" appears exactly TWICE in total in this clip — once inside the second phrase and once inside the third phrase, exactly as written. It never appears a third time, in any size, at any moment, and it never appears twice inside the same phrase.
- EXACT COUNT: the word "बचाव" appears exactly ONCE in total in this clip — inside the first phrase only. The word "बचाती" appears exactly ONCE, inside the third phrase only. These two words are never swapped and never repeated.
- EXACT COUNT: the word "धातु" appears exactly ONCE in total in this clip — inside the second phrase only. Nowhere else, at any moment.
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol. The text is Devanagari Hindi; every matra, every bindu and every conjunct is formed correctly and completely.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt. No English words anywhere, and no digits anywhere.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated.
In this clip: the first phrase has ONE golden word, "बचाव". Because the word "लोहे" is written in both the second phrase and the third phrase, the second phrase and the third phrase are rendered COMPLETELY UNIFORM in bold white, all the same colour, size and weight, with NO golden word at all in either of them. There is exactly one golden word in the whole clip.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean crisp flat overlay typography on a dark technical background. Never photorealistic. NO fire, NO flame, NO sparks, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: completely empty background. Nothing at all. This is a deliberate hard cut — nothing from the previous clip is present at the first frame.

ANIMATION TIMELINE:
0.0 s — the first phrase "दूसरा, समर्पित बचाव," pops in at the very top of the frame, fully sharp, with the word "बचाव" golden in place inside the sentence.
3.3 s — the first phrase disappears completely.
3.5 s — the second phrase "मतलब लोहे से अधिक क्रियाशील धातु की तह चढ़ाना," pops in in the same place, fully sharp, completely uniform bold white with no golden word.
6.6 s — the second phrase disappears completely.
6.8 s — the third phrase "जो पहले नष्ट होकर लोहे को बचाती है।" pops in in the same place, fully sharp, completely uniform bold white with no golden word.
9.8 s — the third phrase fades out completely.
10.0 s — the frame is empty background again.
Throughout: nothing else ever appears. The bottom half of the frame contains nothing but the background from the first frame to the last.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "दूसरा, समर्पित बचाव,"
2. "मतलब लोहे से अधिक क्रियाशील धातु की तह चढ़ाना,"
3. "जो पहले नष्ट होकर लोहे को बचाती है।"
Nothing else is written anywhere on screen at any moment.

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, broken Devanagari conjuncts, missing or floating matras, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, curly quotes, em-dashes, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, a third "लोहे", the word "लोहे" twice inside the same phrase, a second "बचाव", a second "धातु", a golden word in the second phrase, a golden word in the third phrase, two golden words, invented labels, any label plate, any chip, any callout, any leader line, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, English words, the English word Corrosion, digits, chemical formulas, equations, any nail, iron bar, metal sheet, coating, layer, cross-section, rust patch, water droplet, gas bubble, sphere, arrow, beaker, cell, shape, icon or illustration of any kind, the diagram from the previous clip reappearing, a coated bar fading in, a reddish-brown rust patch, a bright red rust, a green patina on iron, a black tarnish on iron, a shiny golden zinc layer, a mirror-bright galvanised sheet, a tin coating shown as sacrificial protection, a copper coating on iron, an electroplating cell with the object as anode, a reactivity series with iron above zinc, a coating drawn beneath the iron, any voiceover, any narration, any spoken words, any human voice, any singing, background music, sound effects, an automatic caption, an auto-generated subtitle, a burnt-in subtitle bar, closed captions, a transcript line, any text that appears because speech was generated, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed
```

---

**Notes on choices inside these four:**

- **Seg 12 style break from the plan:** the plan called for a count lock on `लोहे` only. I also stripped the golden word from phrases 2 **and** 3, because `लोहे` appearing in both phrases is exactly the bug-#7 shape (golden word duplicating into a separate line). One golden word in the whole clip.
- **Seg 11 carries no `जंग`/`रust` visual at all** — the barrier point is "rust never starts", so any reddish-brown patch there would teach the opposite. Rust is banned by name in that segment's negatives.
- **Seg 11 counts are literal** (four droplets, four spheres) with `a fifth…` bans, per the exactly-three/four accuracy error class.
- Still open from the plan: `गैल्वेनीकरण` spelling, digits vs words for `2025`/`12वीं`, and whether Seg 14 gets a fourth diagram. None of those affect 9–12, so these four are testable now — **generate Segment 11 first** (it is the only diagram in this batch and the one most likely to break the middle line).

Reference frame read — it confirms the rust palette (orange-brown flaky over grey iron) and is exactly the landscape full-bleed composition that triggered bug §18, so Segment 13 carries the SIZE AND POSITION CHECK block.

Here are Segments 13–16, full and self-contained.

---

### SEGMENT 13 — DIAGRAM (iron sheet + zinc layer)

```
VIDEO PROMPT — SEGMENT 13 OF 17

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

AUDIO: this clip is completely SILENT. There is no voiceover, no narration, no speech, no singing, no music, no sound effects and no ambient sound of any kind. No voice is generated at any moment. The audio track is empty. The spoken narration is added separately in editing from a different source.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, starting close to the top edge. The diagram sits directly below the script text and fills the space between the text and the invisible middle line, so the top half never looks empty. The lowest part of the diagram stops with a clear visible gap above the invisible middle line and never touches it; if it does not fit, make it smaller. Before the diagram appears, the area below the script text stays plain background. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

SIZE AND POSITION CHECK (CRITICAL): before anything is drawn, the diagram is scaled so that its complete height — including every arrow, glow and shadow — fits inside the upper half of the frame with a clear visible margin still left below it. If any part of the diagram would reach the middle of the frame, the whole diagram is made smaller until it does not. The diagram never grows, drifts downward, expands or scales up at any moment during the clip. The lower half of the frame contains nothing but the background from the first frame to the last.

3D RENDER QUALITY (CRITICAL — THIS MAKES THE DIAGRAM LOOK THREE DIMENSIONAL):
The diagram is a real three dimensional object rendered in depth, not a flat drawing.
- CAMERA: a fixed three-quarter view from slightly above the object, so the viewer looks slightly down at it and can clearly read its thickness and its edges. Never a flat straight-on front view.
- PERSPECTIVE: the rectangular sheet recedes toward the back, its far edge appearing shorter than its near edge because of the viewing angle. Nothing is drawn as a plain flat rectangle.
- DEPTH: the parts nearest the camera are brighter, thicker and sharper. The parts on the far side are noticeably dimmer, softer and slightly smaller. This difference is clear and obvious.
- LIGHTING: one soft cool rim light along the upper left edge and a gentle ambient fill, giving a rounded sculpted look with a soft falloff toward the lower right.
- MATERIAL: the metal reads as real metal — a matte brushed surface with a soft broad specular sheen near the upper left, never a mirror and never chrome.
- FORESHORTENING: the cut end of the sheet, facing the camera, appears thicker and clearer than the far end, which appears thinner and fainter. The two ends are never drawn the same size on screen.
- MOTION: the object turns very slowly and steadily around its vertical axis so the depth reads clearly. It never wobbles, never squashes, never deforms and never changes size once settled.

DIAGRAM SPECIFICATION (build exactly this, nothing else):
- THE IRON SHEET: one thick rectangular metal sheet rendered in full three dimensions, seen in three-quarter view from slightly above, tilted so that its top face, its front long edge and its cut end are all visible. Its colour is a plain dull grey-silver with a faint brushed metallic sheen and soft darker shading along the lower right. It is never yellow, never golden, never chrome-mirror, never reflective like a mirror, never orange and never brown. Its cut end shows the sheet's thickness as one single solid grey band of metal. It turns very slowly and steadily and never deforms.
- THE ZINC LAYER: one thin even covering layer that lies entirely ON THE OUTSIDE of the iron sheet, wrapping over its top face and down its front long edge, sitting above the grey iron and never underneath it. Its colour is a dull matte bluish-grey with a faint frosted spangle texture of soft irregular crystalline patches, clearly duller than the iron beneath it. It is never shiny gold, never yellow, never mirror-bright, never polished, never orange and never brown. It is one single continuous unbroken layer with no gap, no crack, no hole and no missing patch anywhere along its length. At the cut end of the sheet the layering reads as exactly TWO stacked bands: the grey iron band at the bottom and the thinner dull bluish-grey zinc band directly on top of it, in that order and never reversed. There are exactly two metals in this clip and no third one.
- LABELS: this clip has NO labels at all. No plate, no chip, no tag, no floating letter, no leader line and no arrow. Never invent a label.

DIAGRAM TIMING SYNC (CRITICAL): every object appears at the exact moment its name is visible in the written phrase on screen, and never a frame before. Once an object appears it stays to the end of the clip.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE. Every word appears exactly the number of times it is written.
- EXACT COUNT: the word "गैल्वेनीकरण" appears exactly ONCE in total in this clip, inside the first phrase only. Nowhere else, in any size, at any moment.
- EXACT COUNT: the word "जिंक" appears exactly ONCE in total in this clip, inside the second phrase only. Nowhere else, in any size, at any moment.
- EXACT COUNT: the word "लोहे" appears exactly ONCE in total in this clip, inside the second phrase only. Nowhere else, in any size, at any moment.
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol, in Devanagari script.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. In this clip the first phrase has the single golden word "गैल्वेनीकरण" and the second phrase has the single golden word "जिंक"; every other word in both phrases is bold white. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean, glossy, textbook-style chemistry illustration rendered in three dimensions — smooth shapes, flat bright colours, soft even glow, like a modern NCERT diagram built in 3D. Never photorealistic. NO fire, NO flame, NO burning, NO spark, NO ember, NO explosion, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: completely empty background. Nothing at all.

ANIMATION TIMELINE:
0.0–4.8 s — the first phrase "इसका उदाहरण है गैल्वेनीकरण," pops in at the very top of the frame, fully sharp, and holds. The word "गैल्वेनीकरण" is golden inside the sentence. The area below it stays plain empty background.
4.8–5.0 s — the first phrase is completely gone. Nothing is on screen except the background.
5.0–10.0 s — the second phrase "जिसमें लोहे पर जिंक की तह चढ़ाई जाती है।" pops in at the very top of the frame, fully sharp, and holds to the end. The word "जिंक" is golden inside the sentence.
At 5.4 s, exactly as the word लोहे is visible on screen, the plain grey-silver iron sheet pops in below the script text, already at its final size, and begins its very slow steady turn. It holds to the end.
At 6.6 s, exactly as the word जिंक is visible on screen, the dull matte bluish-grey zinc layer sweeps smoothly along the outside of the iron sheet from the near end to the far end over 1.0 second, settling as one continuous unbroken covering layer sitting on top of the grey iron. It holds to the end.
7.6–10.0 s — nothing new appears. The iron sheet with its zinc layer keeps turning very slowly at a fixed size and a fixed position, staying entirely in the top half of the frame.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "इसका उदाहरण है गैल्वेनीकरण,"
2. "जिसमें लोहे पर जिंक की तह चढ़ाई जाती है।"

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, invented labels, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, any voiceover, any narration, any spoken words, any human voice, any singing, background music, sound effects, an automatic caption, an auto-generated subtitle, a burnt-in subtitle bar, closed captions, a transcript line, any text that appears because speech was generated, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, the diagram crossing the middle of the frame, the diagram touching the middle of the frame, the diagram growing or expanding during the clip, the diagram drifting downward, an inset circle in the lower half, the illustration filling the whole frame, a full-frame poster layout, a flat two dimensional rectangle instead of a three dimensional sheet, a straight-on front view with no depth, a diagram that looks like a flat line drawing, a shiny golden coating, a yellow coating, a mirror-bright or polished coating, a chrome or mirror-finish iron sheet, the zinc layer drawn underneath the iron, the coating drawn beneath the base metal, a broken coating, a cracked coating, a gap or hole in the coating, a scratched or peeling coating, a third metal layer, more than two stacked bands at the cut end, any rust, any orange-brown or reddish-brown patch, any brown flaking, any green patina, any black tarnish, a tin coating, a copper coating, the iron sheet appearing before 5.4 seconds, the zinc layer appearing before 6.6 seconds, any label plate, any chip, any callout, any leader line, any arrow, equations, any chemical formula, any digit
```

---

### SEGMENT 14 — TEXT_ONLY

```
VIDEO PROMPT — SEGMENT 14 OF 17

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

AUDIO: this clip is completely SILENT. There is no voiceover, no narration, no speech, no singing, no music, no sound effects and no ambient sound of any kind. No voice is generated at any moment. The audio track is empty. The spoken narration is added separately in editing from a different source.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, filling the width, starting close to the top edge, large enough to fill the upper area comfortably. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

NO DIAGRAM IN THIS CLIP (CRITICAL): this clip contains NO three dimensional object of any kind. There is no metal sheet, no nail, no bar, no coating layer, no beaker, no cell, no electrode, no wire, no battery, no droplet, no arrow, no shape, no icon and no illustration anywhere in the frame at any moment. The only things on screen are the script text and the plain background. Do not invent, add or imagine any diagram, object or graphic. The space below the script text stays as plain empty background.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE. Every word appears exactly the number of times it is written.
- EXACT COUNT: the word "धातुओं" appears exactly ONCE in total in this clip, inside the second phrase only. Nowhere else, in any size, at any moment.
- EXACT COUNT: the word "धातु" appears exactly ONCE in total in this clip, inside the third phrase only. Nowhere else, in any size, at any moment.
- EXACT COUNT: the word "प्लेटिंग" appears exactly ONCE in total in this clip, inside the first phrase only. Nowhere else, in any size, at any moment.
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol, in Devanagari script.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. In this clip the first phrase has the single golden word "प्लेटिंग", the second phrase has the single golden word "क्रोमियम", and the third phrase has the single golden word "सुरक्षित"; every other word in every phrase is bold white. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean crisp flat overlay typography on a dark technical background. Never photorealistic. NO fire, NO flame, NO sparks, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: completely empty background. Nothing at all.

ANIMATION TIMELINE:
0.0–3.3 s — the first phrase "तीसरा, विद्युत प्लेटिंग," pops in at the very top of the frame, fully sharp, and holds. The word "प्लेटिंग" is golden inside the sentence.
3.3–3.5 s — the first phrase is completely gone. Nothing is on screen except the background.
3.5–6.6 s — the second phrase "मतलब जिंक, निकिल या क्रोमियम जैसी धातुओं की परत चढ़ाकर" pops in at the very top of the frame, fully sharp, and holds. The word "क्रोमियम" is golden inside the sentence.
6.6–6.8 s — the second phrase is completely gone. Nothing is on screen except the background.
6.8–10.0 s — the third phrase "धातु को सुरक्षित करना।" pops in at the very top of the frame, fully sharp, and holds to the end. The word "सुरक्षित" is golden inside the sentence.
Nothing else ever appears. The area below the script text stays plain empty background for the whole clip.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "तीसरा, विद्युत प्लेटिंग,"
2. "मतलब जिंक, निकिल या क्रोमियम जैसी धातुओं की परत चढ़ाकर"
3. "धातु को सुरक्षित करना।"

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, invented labels, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, any voiceover, any narration, any spoken words, any human voice, any singing, background music, sound effects, an automatic caption, an auto-generated subtitle, a burnt-in subtitle bar, closed captions, a transcript line, any text that appears because speech was generated, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, any metal sheet, any nail, any bar, any coating layer, any beaker, any electrolytic cell, any electrode, any wire, any battery, any droplet, any arrow, any shape, any icon or illustration of any kind, any label plate, equations, any chemical formula, any digit, English words on screen, the heading Corrosion written in English, an extra fourth item, only two items
```

---

### SEGMENT 15 — TEXT_ONLY

```
VIDEO PROMPT — SEGMENT 15 OF 17

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

AUDIO: this clip is completely SILENT. There is no voiceover, no narration, no speech, no singing, no music, no sound effects and no ambient sound of any kind. No voice is generated at any moment. The audio track is empty. The spoken narration is added separately in editing from a different source.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, filling the width, starting close to the top edge, large enough to fill the upper area comfortably. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

NO DIAGRAM IN THIS CLIP (CRITICAL): this clip contains NO three dimensional object of any kind. There is no metal sheet, no nail, no bar, no coating layer, no beaker, no cell, no electrode, no wire, no battery, no droplet, no arrow, no shape, no icon and no illustration anywhere in the frame at any moment. The only things on screen are the script text and the plain background. Do not invent, add or imagine any diagram, object or graphic. The space below the script text stays as plain empty background.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE. Every word appears exactly the number of times it is written.
- EXACT COUNT: the word "संक्षारण" appears exactly ONCE in total in this clip, inside the second phrase only. Nowhere else, in any size, at any moment.
- EXACT COUNT: the word "याद" appears exactly ONCE in total in this clip, inside the first phrase only. Nowhere else, in any size, at any moment.
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol, in Devanagari script.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. In this clip the first phrase has the single golden word "याद", the second phrase has the single golden word "संक्षारण", and the third phrase has the single golden word "कभी"; every other word in every phrase is bold white. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean crisp flat overlay typography on a dark technical background. Never photorealistic. NO fire, NO flame, NO sparks, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: completely empty background. Nothing at all.

ANIMATION TIMELINE:
0.0–3.3 s — the first phrase "बच्चों, बस इतना याद रख लिया," pops in at the very top of the frame, fully sharp, and holds. The word "याद" is golden inside the sentence.
3.3–3.5 s — the first phrase is completely gone. Nothing is on screen except the background.
3.5–6.6 s — the second phrase "तो परीक्षा में संक्षारण का ये पूरा उत्तर" pops in at the very top of the frame, fully sharp, and holds. The word "संक्षारण" is golden inside the sentence.
6.6–6.8 s — the second phrase is completely gone. Nothing is on screen except the background.
6.8–10.0 s — the third phrase "कभी नहीं भूलोगे।" pops in at the very top of the frame, fully sharp, and holds to the end. The word "कभी" is golden inside the sentence.
Nothing else ever appears. The area below the script text stays plain empty background for the whole clip.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "बच्चों, बस इतना याद रख लिया,"
2. "तो परीक्षा में संक्षारण का ये पूरा उत्तर"
3. "कभी नहीं भूलोगे।"

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, invented labels, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, any voiceover, any narration, any spoken words, any human voice, any singing, background music, sound effects, an automatic caption, an auto-generated subtitle, a burnt-in subtitle bar, closed captions, a transcript line, any text that appears because speech was generated, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, any metal sheet, any nail, any bar, any coating layer, any beaker, any electrolytic cell, any electrode, any wire, any battery, any droplet, any arrow, any shape, any icon or illustration of any kind, any label plate, equations, any chemical formula, any digit, English words on screen, the heading Corrosion written in English
```

---

### SEGMENT 16 — TEXT_ONLY

```
VIDEO PROMPT — SEGMENT 16 OF 17

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

AUDIO: this clip is completely SILENT. There is no voiceover, no narration, no speech, no singing, no music, no sound effects and no ambient sound of any kind. No voice is generated at any moment. The audio track is empty. The spoken narration is added separately in editing from a different source.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, filling the width, starting close to the top edge, large enough to fill the upper area comfortably. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

NO DIAGRAM IN THIS CLIP (CRITICAL): this clip contains NO three dimensional object of any kind. There is no metal sheet, no nail, no bar, no coating layer, no beaker, no cell, no electrode, no wire, no battery, no droplet, no arrow, no shape, no icon, no phone, no screen device, no camera, no button and no illustration anywhere in the frame at any moment. The only things on screen are the script text and the plain background. Do not invent, add or imagine any diagram, object or graphic. The space below the script text stays as plain empty background.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE beyond what is written. Every word appears exactly the number of times it is written.
- EXACT COUNT: in the third phrase the word "लेना" is written exactly TWICE, exactly as given, and never a third time anywhere in this clip, in any size, at any moment.
- EXACT COUNT: the word "इसे" appears exactly TWICE in total in this clip — once inside the first phrase and once inside the third phrase. Nowhere else, in any size, at any moment.
- EXACT COUNT: the word "इसका" appears exactly TWICE in total in this clip — once inside the second phrase and once inside the third phrase. Nowhere else, in any size, at any moment.
- EXACT COUNT: the word "परीक्षा" appears exactly ONCE in total in this clip, inside the first phrase only. Nowhere else, in any size, at any moment.
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol, in Devanagari script.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. In this clip the first phrase has the single golden word "परीक्षा" and the second phrase has the single golden word "स्क्रीन". The THIRD phrase contains the same word twice, so the third phrase is rendered COMPLETELY UNIFORM in bold white, all one colour, size and weight, with NO golden word at all. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean crisp flat overlay typography on a dark technical background. Never photorealistic. NO fire, NO flame, NO sparks, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: completely empty background. Nothing at all.

ANIMATION TIMELINE:
0.0–3.3 s — the first phrase "अब इसे परीक्षा में कैसे लिखना है," pops in at the very top of the frame, fully sharp, and holds. The word "परीक्षा" is golden inside the sentence.
3.3–3.5 s — the first phrase is completely gone. Nothing is on screen except the background.
3.5–6.6 s — the second phrase "इसका पूरा उत्तर आपकी स्क्रीन पर आ जाएगा।" pops in at the very top of the frame, fully sharp, and holds. The word "स्क्रीन" is golden inside the sentence.
6.6–6.8 s — the second phrase is completely gone. Nothing is on screen except the background.
6.8–10.0 s — the third phrase "इसे सेव कर लेना और इसका स्क्रीनशॉट लेना मत भूलना।" pops in at the very top of the frame, fully sharp, entirely uniform bold white with no golden word, and holds to the end.
Nothing else ever appears. The area below the script text stays plain empty background for the whole clip.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "अब इसे परीक्षा में कैसे लिखना है,"
2. "इसका पूरा उत्तर आपकी स्क्रीन पर आ जाएगा।"
3. "इसे सेव कर लेना और इसका स्क्रीनशॉट लेना मत भूलना।"

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word beyond what is written, a third copy of the word लेना, a repeated key word, a keyword written as a separate line, a golden word in the third phrase, invented labels, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, any voiceover, any narration, any spoken words, any human voice, any singing, background music, sound effects, an automatic caption, an auto-generated subtitle, a burnt-in subtitle bar, closed captions, a transcript line, any text that appears because speech was generated, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, an answer card, a written answer sheet, a list of points, a bulleted summary, a phone, a screen device, a camera, a screenshot icon, a save icon, a button, any metal sheet, any nail, any coating layer, any beaker, any electrolytic cell, any electrode, any arrow, any shape, any icon or illustration of any kind, any label plate, equations, any chemical formula, any digit, English words on screen
```

---

**Notes on these four**

- **Seg 13** is the only diagram segment here, so it carries §18 SIZE AND POSITION CHECK — the reference frame you gave me is exactly the landscape full-bleed composition that caused the diagram to cross the middle line, so the scale-first language is load-bearing. LABELS: none, per the plan; meaning is carried by colour (dull grey iron vs. matte bluish-grey zinc).
- **Accuracy bans wired in** at Seg 13: zinc never gold/mirror, coating never under the iron, exactly two stacked bands, no tin/copper, no rust or green patina on the galvanised sheet.
- **Seg 16** third phrase is uniform white by rule (`लेना` twice) — that plus the three EXACT COUNT locks is the highest-risk text in the pack.
- The words logo/watermark/badge/wordmark appear nowhere except the single tested `watermark` token inside the base negative list — nothing added around it.
- Still open from the plan: `गैल्वेनीकरण` vs `गैल्वनीकरण` spelling (it's golden text in Seg 13, so it's worth confirming before you generate).

It looks like the plan ends at Segment 17. Please confirm: should I generate only Segment 17, or do you have scripts for Segments 18–20 to add? For now, here is the full tested-order prompt for Segment 17.

``` 
VIDEO PROMPT — SEGMENT 17 OF 17

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

AUDIO: this clip is completely SILENT. There is no voiceover, no narration, no speech, no singing, no music, no sound effects and no ambient sound of any kind. No voice is generated at any moment. The audio track is empty. The spoken narration is added separately in editing from a different source.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, filling the width, starting close to the top edge, large enough to fill the upper area comfortably. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

NO DIAGRAM IN THIS CLIP (CRITICAL): this clip contains NO three dimensional object of any kind. There is no sphere, no ball, no charge, no arrow, no field line, no surface, no shape, no icon and no illustration anywhere in the frame at any moment. The only things on screen are the script text and the plain background. Do not invent, add or imagine any diagram, object or graphic. The space below the script text stays as plain empty background.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE beyond what is written. In the first phrase the word "और" is written exactly as given — it appears exactly twice there and never a third time anywhere.
- EXACT COUNT: the word "और" appears exactly TWICE in total in this clip — both appearances are inside the first phrase. Nowhere else, in any size, at any moment.
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time, perfectly synced with the voiceover. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean crisp flat overlay typography on a dark technical background. Never photorealistic. NO fire, NO flame, NO sparks, NO smoke.

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

SCREEN AT START: completely empty background. Nothing at all.

ANIMATION TIMELINE:
- 0.0–4.8 s: Phrase 1 visible, then fully clears.
- 5.0–10.0 s: Phrase 2 visible and holds to the end.
- No diagrams, no labels, no equations appear in this clip.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "और ऐसे ही आसान और मजेदार तरीके से पढ़ने के लिए"
2. "अरिविहान के उन्नति बैच से जुड़ो।"

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, invented labels, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, any sphere, ball, charge, arrow, field line, surface, shape, icon or illustration of any kind, any label plate, equations, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, any voiceover, any narration, any spoken words, any human voice, any singing, background music, sound effects, an automatic caption, an auto-generated subtitle, a burnt-in subtitle bar, closed captions, a transcript line, any text that appears because speech was generated, rust shown as bright red or as a smooth even coat, water or moisture omitted from any rusting equation if an equation is ever shown, zinc drawn as shiny golden or mirror-bright, tin-coating shown as an example of sacrificial protection, an electroplating cell with the object as anode, green patina used for iron rust, four or two items where the script says three, rust drawn as a protective sealed layer that stops further corrosion, the English word "Corrosion" as a heading when narration says "संक्षारण", any digit or symbol rendered inside a spoken line.
```

I can't write segments 21–24 — **the plan tops out at 17 segments** (17 × 10 s = 170 s / 2:50). There is no Seg 18, 19, 20, 21… anywhere in the segment map or the end-state continuity chain. Writing four prompts for beats that don't exist would mean inventing script text, which is exactly the thing this pack must never do (every on-screen word is copied verbatim from your script — no paraphrase, no invention).

So, before I write anything, tell me which of these you meant:

1. **Segments 14–17** — the last four of the plan (`विद्युत प्लेटिंग` → `बच्चों, बस इतना याद रख लिया` → screenshot ask → `अरिविहान के उन्नति बैच`). Most likely if you wanted "the closing four."
2. **A different, longer pack** — you have a 24-segment version of this script (or another topic) that I haven't been given. Paste it and I'll write 21–24 from it.
3. **Genuinely new segments 18–24** — the script needs extending past `उन्नति बैच`. Give me the additional Hinglish lines and I'll chunk and build them.

Two things I noticed meanwhile, both worth settling in the same reply:

**The reference frame you had me read is a landscape full-bleed poster** (white background, content edge-to-edge, 8+ text plates, English `O₂` / `H₂O` inside a Devanagari frame). That is the exact anchor-frame shape the ledger blames for the "animation crossed the 50% line" bug on the sickle-cell test — a full-bleed poster signals *fill the whole frame*, which is the opposite of the top-half rule. If this is going in as a Veo reference image, I'd re-shoot it portrait with everything composed in the upper half and the lower half empty. If it's just a content reference for me, it's fine — and it confirms the accuracy brief nicely (grey nail, reddish-brown flaky rust growing outward, three inputs including नमी).

**Your three open questions from the plan are still unanswered**, and two of them change the prompt text I'd write:
- `गैल्वेनीकरण` vs `गैल्वनीकरण` — which is in your board copy? (Seg 13 on-screen text.)
- `2025` / `12वीं` as digits on screen, or spelled out? (Seg 1. Note: digits on *screen* are fine — the no-digits rule is only for spoken lines, and these clips are silent per §17.)
- Three diagrams enough, or add one for `विद्युत प्लेटिंग` at Seg 14?

Answer the segment-range question plus these, and I'll write the full block-by-block prompts — §15 uploaded-background, §17 silent, §18 top-half enforcement on every diagram segment, no mention of the b-word family anywhere.

I can't write those — **the plan tops out at 17 segments** (17 × 10 s = 170 s). There is no segment 25, 26 or 27, so writing them would mean inventing script lines that aren't in your approved chunking, and every phrase in these packs has to be word-for-word from the script.

Tell me which you meant and I'll write them in full:

- **Segments 15–17** (the last three: "बच्चों, बस इतना याद रख लिया…", the screenshot line, the अरिविहान outro) — likeliest if you meant "the last three".
- **Some other trio** — just name them (e.g. "11, 12, 13" — the prevention block, two diagrams + one text).
- **The script actually grew past 17** — paste the new chunking and I'll re-plan the tail before writing.

Two things blocking a clean write regardless, both still unanswered from the plan:

1. **`गैल्वेनीकरण` vs `गैल्वनीकरण`** — which is in your board copy? (Seg 13 puts it on screen.)
2. **`2025` and `12वीं` as digits, or spelled out?** (Seg 1 only.)
3. Segments 16 and 17 are the two hardest in the pack for repeated words — 16 has `लेना` twice inside one phrase plus `इसे`/`इसका`, and 17 has `और` twice inside phrase 1. Both get UNIFORM white with no golden word plus hard EXACT COUNT locks. Confirming so you're not surprised there's no golden keyword in the outro.

One flag from the reference frame you had me read: it's a **landscape full-bleed poster** — content edge to edge, diagram dead-centre. That's the exact anchor-frame shape the bug ledger blames for the "animation crossed the 50% line" failure on the sickle-cell test. If that frame is going into the tool as a style/anchor reference, it will fight the top-half rule no matter how hard §18 is worded. Use it as a *fact reference only* (rust colour, three-input equation, layer order) and don't attach it as an anchor frame — or crop a portrait, top-half-composed version first.

Say the word on the segment numbers and I'll write the full prompts — every block in tested order, §15 uploaded-background, §17 silent, no §16.