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