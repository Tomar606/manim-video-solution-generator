# फैराडे के विद्युत्-अपघटन के नियम — SEGMENT PROMPT SET

## Step 0/1 — script pass (fixes found before chunking)

**Factual check vs NCERT / MP Board — script is clean.** W ∝ Q, Q = i×t, W = Z i t, Z = विद्युत्-रासायनिक तुल्यांक, and W₁/W₂ = E₁/E₂ all match the standard statement. No correction needed. (Diagram accuracy notes are in the flags below.)

**Corrections applied (wording otherwise untouched):**

| # | Source | Fixed | Why |
|---|---|---|---|
| 1 | "दूसरा नियम कहता है **की**" | "कहता है **कि**" | grammar; goes on screen verbatim |
| 2 | "**अरिहान** के 'उन्नति बैच'" | "**अरिविहान** के उन्नति बैच" | brand spelling + curly quotes ‘ ’ removed (stray-punctuation bug #12) — **confirm** |

**Repeat-word scan (these segments will need EXACT COUNT lines in Step 3):** S6 (मात्रा ×2, अधिक ×2), S7 (मात्रा ×2, है ×2), S8 (मात्रा ×2), S12/S21 (अलग-अलग — a repeat *inside* one word, highest stutter risk), S14 (अधिक ×2), S16 (मात्रा ×2), S17 (W₁ W₂ E₁ E₂), S18 ("के समानुपाती है" ×2), S19 (अनुपात ×2), S20 (ज्यादा ×2, मात्रा ×2).

**Golden-keyword consequence:** every phrase in Clips 2–4 carries either a math symbol (W, Q, i, t, Z, W₁…) or a repeated word → **UNIFORM bold white, no golden word** in almost all of them. Golden keyword is available only in S1, S3, S4, S15, S22, S23, S24 — and never on a hyphenated word (विद्युत्-अपघटन, अलग-अलग can never be golden).

---

## 1. Total segment count

**24 segments × 10 sec = 240 sec (4:00)**

Split by clip: Clip 1 → 3 · Clip 2 → 8 · Clip 3 → 8 · Clip 4 → 2 · Clip 5 → 3.

---

## 2. Segment map

| Seg | Phrases (exact words) | Type | Diagram |
|---|---|---|---|
| 1 | "एमपी बोर्ड कक्षा 12वीं के बच्चों!" / "ये सवाल 2023 या 2025 में आ चुका है" | TEXT_ONLY · 15w | N |
| 2 | "और इस साल भी आपकी त्रैमासिक परीक्षा में आ सकता है।" / "और इस वीडियो के अंत तक" | TEXT_ONLY · 16w | N |
| 3 | "आप फैराडे के दोनों नियमों को पूरा याद करके," / "परीक्षा में सही तरीके से लिखना भी सीख जाओगे।" / "तो चलिए।" | TEXT_ONLY · 20w | N |
| 4 | "सबसे पहले समझते हैं—फैराडे का पहला नियम।" / "और इसे ध्यान से समझना," / "क्योंकि अगर परीक्षा में बिल्कुल ऐसा ही लिख दिया," | TEXT_ONLY · 22w | N |
| 5 | "तो आपके नंबर पक्के हैं।" / "तो जब विद्युत्-अपघटन के दौरान किसी इलेक्ट्रोड पर" / "मुक्त होने वाले पदार्थ की मात्रा," | DIAGRAM · 19w | **Y** (cell builds) |
| 6 | "प्रवाहित विद्युत् की मात्रा के समानुपाती होती है।" / "मतलब, जितनी अधिक विद्युत् प्रवाहित होगी," / "उतनी ही अधिक मात्रा में पदार्थ इलेक्ट्रोड पर मुक्त होगा।" | DIAGRAM · 23w | **Y** (deposit grows) |
| 7 | "यहाँ W है मुक्त पदार्थ की मात्रा" / "और Q है प्रवाहित विद्युत् की मात्रा।" — eq **W ∝ Q** | TRANSITION · 14w | Y→fades by 4.0 s |
| 8 | "ये याद रखना," / "यहाँ संबंध विद्युत् की मात्रा" / "और मुक्त पदार्थ की मात्रा के बीच है।" — **W ∝ Q** holds | EQUATION_ONLY · 16w | N |
| 9 | "अब कूलम्ब में विद्युत् की मात्रा—" / "जहाँ i है विद्युत् धारा की तीव्रता" / "और t है धारा के प्रवाहित होने का समय।" — eq **Q = i × t** | EQUATION_ONLY · 22w | N |
| 10 | "इसलिए—" / "और समानुपात हटाने पर—" / "यहाँ Z है विद्युत्-रासायनिक तुल्यांक।" — **W ∝ i × t** → **W = Z i t** | EQUATION_ONLY · 10w | N |
| 11 | "तो बच्चों, जैसे फैराडे का पहला नियम याद किया," / "वैसे ही दूसरा नियम भी इसी तरह याद कर लो।" — **W = Z i t** holds, then clears | EQUATION_ONLY · 19w | N |
| 12 | "तो दूसरा नियम कहता है कि" / "जब अलग-अलग विद्युत्-अपघट्यों में" / "समान मात्रा में विद्युत् प्रवाहित की जाती है," | DIAGRAM · 18w | **Y** (two cells, series) |
| 13 | "तो इलेक्ट्रोड पर मुक्त होने वाले पदार्थों की मात्राएँ" / "उनके रासायनिक तुल्यांक के समानुपाती होती हैं।" — eq **W ∝ E** | TRANSITION · 15w | Y→fades by 4.0 s |
| 14 | "मतलब, रासायनिक तुल्यांक जितना अधिक होगा," / "मुक्त होने वाले पदार्थ की मात्रा भी" / "उतनी ही अधिक होगी।" — **W ∝ E** holds | EQUATION_ONLY · 17w | N |
| 15 | "और यहाँ एक बात ध्यान से याद रखना—" / "बहुत सारे बच्चे यहीं गलती करते हैं।" — **W ∝ E** fades by 2.0 s | TRANSITION · 15w | N |
| 16 | "दूसरे नियम में विद्युत् की मात्रा समान रहती है" / "और संबंध मुक्त पदार्थ की मात्रा तथा" / "रासायनिक तुल्यांक के बीच होता है।" | TEXT_ONLY · 22w | N |
| 17 | "अब अगर दो पदार्थों की मात्राएँ W₁ और W₂" / "तथा उनके रासायनिक तुल्यांक E₁ और E₂ हैं, तो—" | TEXT_ONLY · 18w | N |
| 18 | "मतलब, W₁, E₁ के समानुपाती है" / "और W₂, E₂ के समानुपाती है।" — eq **W₁ ∝ E₁   W₂ ∝ E₂** (one line) | EQUATION_ONLY · 12w | N |
| 19 | "इसलिए दोनों पदार्थों की मात्राओं का अनुपात," / "उनके रासायनिक तुल्यांकों के अनुपात के बराबर होगा।" — eq **W₁ / W₂ = E₁ / E₂** (green) | EQUATION_ONLY · 15w | N |
| 20 | "बस इतना याद रखना—" / "पहले नियम में जितनी ज्यादा विद्युत् की मात्रा प्रवाहित होगी," / "उतनी ही ज्यादा पदार्थ की मात्रा मुक्त होगी।" — eq **W = Z i t** | EQUATION_ONLY · 22w | N |
| 21 | "और दूसरे नियम में जब समान विद्युत् प्रवाहित की जाए," / "तो अलग-अलग पदार्थों की मुक्त मात्रा" / "उनके रासायनिक तुल्यांक के अनुपात में होगी।" — eq **W₁ / W₂ = E₁ / E₂** | EQUATION_ONLY · 23w | N |
| 22 | "बच्चों, बस इतना याद रख लिया," / "तो परीक्षा में फैराडे के दोनों नियमों का" / "ये पूरा उत्तर कभी नहीं भूलोगे।" | TEXT_ONLY · 20w | N |
| 23 | "अब इसे परीक्षा में कैसे लिखना है," / "इसका पूरा उत्तर आपकी स्क्रीन पर आ जाएगा।" / "इसे सेव कर लेना और इसका स्क्रीनशॉट लेना मत भूलना।" | TEXT_ONLY · 25w | N |
| 24 | "और ऐसे ही आसान और मजेदार तरीके से" / "पढ़ने के लिए अरिविहान के उन्नति बैच से जुड़ो।" | TEXT_ONLY · 17w | N |

---

## 3. Continuity chain (end-state of each segment)

- **Seg 1 ends with:** empty background — last phrase clears at 10.0 s.
- **Seg 2 ends with:** empty background.
- **Seg 3 ends with:** empty background.
- **Seg 4 ends with:** empty background.
- **Seg 5 ends with:** the 3D electrolysis cell — glass beaker with translucent cyan electrolyte, two vertical electrodes, battery with connecting wires, current-direction arrows. No labels, no text. Cell holds to 10.0 s.
- **Seg 6 ends with:** the same cell, unchanged in size/position, plus the thickened deposit layer on the cathode and brighter current arrows. No labels, no equation.
- **Seg 7 ends with:** the equation **W ∝ Q** alone on one line (cell shrank, drifted up and fully faded by 4.0 s).
- **Seg 8 ends with:** **W ∝ Q** alone, all symbols back to white.
- **Seg 9 ends with:** **Q = i × t** alone (W ∝ Q replaced at 1.5 s; only one equation line on screen).
- **Seg 10 ends with:** **W = Z i t** alone, Z glowing yellow.
- **Seg 11 ends with:** empty background — W = Z i t fades out by 10.0 s (clip boundary reset).
- **Seg 12 ends with:** the 3D two-cell series diagram — two glass beakers with different-coloured electrolytes, one battery, a single wire loop through both, equal current arrows. No labels.
- **Seg 13 ends with:** the equation **W ∝ E** alone (two-cell diagram faded by 4.0 s).
- **Seg 14 ends with:** **W ∝ E** alone, symbols back to white.
- **Seg 15 ends with:** empty background (W ∝ E faded out by 2.0 s, text-only after that).
- **Seg 16 ends with:** empty background.
- **Seg 17 ends with:** empty background.
- **Seg 18 ends with:** one equation line **W₁ ∝ E₁   W₂ ∝ E₂**.
- **Seg 19 ends with:** empty background — the line is replaced at 3.5 s by **W₁ / W₂ = E₁ / E₂** in green, which then fades out by 10.0 s (clip boundary).
- **Seg 20 ends with:** **W = Z i t** alone on one line.
- **Seg 21 ends with:** empty background — W = Z i t fades by 1.5 s, **W₁ / W₂ = E₁ / E₂** appears at 4.0 s in green, clears at 10.0 s.
- **Seg 22 ends with:** empty background.
- **Seg 23 ends with:** empty background (the actual written answer card is added in editing, not generated here).
- **Seg 24 ends with:** empty background.

---

## Flags before I write prompts (need your call on 1–3)

1. **Devanagari is a brand-new risk for this pipeline.** Every proven pack so far was Latin-script Hinglish. Veo garbles conjuncts and matras far more than Latin — विद्युत्-अपघट्यों, त्रैमासिक, तुल्यांकों, and the halant in विद्युत् are the danger words. **Recommend: generate Seg 1 alone first as a script-render test.** If Devanagari comes out broken, the fix is architectural (burn text in during editing, Veo generates visuals only) — not a prompt tweak.
2. **Equation chain = one line at a time, replaced.** Locked rule §7 allows only ONE equation line per clip, and the top-half constraint won't hold a 4-line stack. So the derivation reads W ∝ Q → Q = i × t → W ∝ i × t → W = Z i t, each replacing the last, rather than building a visible stack. Confirm — if you want the chain to stay visible, Clip 2 needs a different (riskier) layout.
3. **अरिहान → अरिविहान** and dropping the ‘ ’ quotes in Seg 24 — confirm.
4. **24 segments vs the 13-segment proven ceiling.** This is a full 5-clip lesson, not a single reel, so length is inherent — but style drift across 24 clips is real (bug #16). Mitigation: generate clip-by-clip (3 / 8 / 8 / 2 / 3) and keep BACKGROUND + VISUAL STYLE blocks word-for-word identical. Alternatively, Clip 2's sentence B ("...तो आपके नंबर पक्के हैं") and Clip 3's sentence L (the "गलती करते हैं" warning) are the two trimmable beats — cutting them saves ~2 segments.
5. Seg 10 is the highest-risk prompt in the pack: 10 words, two equation reveals in 10 sec. If it breaks, the split is to give "इसलिए—" its own beat.

Say go and I'll write the 24 prompts (Step 3), starting with Seg 1 as the test clip.


Frame read — it confirms the accuracy brief (electrolytic cell, ammeter, `W ∝ Q → Q = i × t → W ∝ i × t → W = Z i t`, `i` lowercase). Segments 1–4 are all TEXT_ONLY, so no diagram blocks; the frame governs Seg 5+.

Two calls I made, flag them before you generate:

1. **Seg 1 keeps "2023 या 2025" on screen.** The brief bans it as burnt text "since narration handles it" — but under §17 the clip is silent, so nothing else carries the line. Text stays. Say the word and I'll strip it from Seg 1.
2. **Golden keyword dropped in Seg 1 and 2** (digits `12वीं`, `2023`/`2025` in Seg 1; repeated `और`/`इस` across Seg 2). Golden survives in Seg 3 (`फैराडे`) and Seg 4 (`ध्यान` — Seg 4's phrase 1 has an em dash, so it stays uniform).
3. §11's "synced with the voiceover" is reworded to "synced with the timeline" — a voiceover no longer exists in a silent clip.

---

```
VIDEO PROMPT — SEGMENT 1 OF 24

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

AUDIO: this clip is completely SILENT. There is no voiceover, no narration, no speech, no singing, no music, no sound effects and no ambient sound of any kind. No voice is generated at any moment. The audio track is empty. The spoken narration is added separately in editing from a different source.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, filling the width, starting close to the top edge, large enough to fill the upper area comfortably. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

NO DIAGRAM IN THIS CLIP (CRITICAL): this clip contains NO three dimensional object of any kind. There is no beaker, no jar, no liquid, no electrode, no battery, no cell, no wire, no ammeter, no ion, no bubble, no arrow, no equation, no shape, no icon and no illustration anywhere in the frame at any moment. The only things on screen are the script text and the plain background. Do not invent, add or imagine any diagram, object or graphic. The space below the script text stays as plain empty background.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE. Every word appears exactly the number of times it is written.
- SCRIPT LOCK: all text in this clip is written in the Devanagari script exactly as given, character by character, matra by matra. It is NEVER transliterated into Latin or Roman letters, NEVER translated into English, and NEVER mixed with English words. Conjunct letters stay joined, vowel signs stay attached to their consonant, and the halant mark stays exactly where it is written.
- EXACT COUNT: the digits in this clip appear exactly as written and nowhere else — "12" appears exactly ONCE, "2023" appears exactly ONCE and "2025" appears exactly ONCE, all three inside the script phrases only. No other number, digit, date, year, count or numeral appears anywhere on screen, in any size, at any moment.
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, a number, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. In THIS clip both phrases contain numbers, so BOTH phrases are completely uniform bold white and there is NO golden word anywhere in this clip. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters, matras or conjuncts are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time, perfectly synced with the animation timeline below. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean crisp flat overlay typography on a dark technical background. Never photorealistic. NO fire, NO flame, NO sparks, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: completely empty background. Nothing at all.

ANIMATION TIMELINE:
0.0–4.8 s — the first phrase "एमपी बोर्ड कक्षा 12वीं के बच्चों!" pops in fully sharp at the very top of the frame, completely uniform bold white, and holds perfectly still. At 4.8 s it disappears completely in a single clean fade.
4.8–5.0 s — a 0.2 second gap in which no phrase is visible anywhere on screen.
5.0–10.0 s — the second phrase "ये सवाल 2023 या 2025 में आ चुका है" pops in fully sharp in the same place at the very top of the frame, completely uniform bold white, and holds perfectly still until 10.0 s.
Nothing else happens. Nothing enters the lower half of the frame at any moment.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "एमपी बोर्ड कक्षा 12वीं के बच्चों!"
2. "ये सवाल 2023 या 2025 में आ चुका है"

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, curly quotation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, invented labels, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, any voiceover, any narration, any spoken words, any human voice, any singing, background music, sound effects, an automatic caption, an auto-generated subtitle, a burnt-in subtitle bar, closed captions, a transcript line, any text that appears because speech was generated, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, Latin or Roman letters, English words, Devanagari text transliterated into Latin letters, detached vowel signs, broken matras, split conjunct letters, a missing or misplaced halant mark, any beaker, jar, liquid, electrode, battery, cell, wire, ammeter, ion, bubble, arrow, shape, icon or illustration of any kind, any electrolysis apparatus, any galvanic or voltaic cell, any label plate, any equation, any mathematical symbol, the proportionality sign, the letters W, Q, i, t, Z or E anywhere on screen, any extra year, date, digit or numeral beyond the ones written, a golden word in either phrase
```

---

```
VIDEO PROMPT — SEGMENT 2 OF 24

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

AUDIO: this clip is completely SILENT. There is no voiceover, no narration, no speech, no singing, no music, no sound effects and no ambient sound of any kind. No voice is generated at any moment. The audio track is empty. The spoken narration is added separately in editing from a different source.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, filling the width, starting close to the top edge, large enough to fill the upper area comfortably. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

NO DIAGRAM IN THIS CLIP (CRITICAL): this clip contains NO three dimensional object of any kind. There is no beaker, no jar, no liquid, no electrode, no battery, no cell, no wire, no ammeter, no ion, no bubble, no arrow, no equation, no shape, no icon and no illustration anywhere in the frame at any moment. The only things on screen are the script text and the plain background. Do not invent, add or imagine any diagram, object or graphic. The space below the script text stays as plain empty background.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE. Every word appears exactly the number of times it is written.
- SCRIPT LOCK: all text in this clip is written in the Devanagari script exactly as given, character by character, matra by matra. It is NEVER transliterated into Latin or Roman letters, NEVER translated into English, and NEVER mixed with English words. Conjunct letters stay joined, vowel signs stay attached to their consonant, and the halant mark stays exactly where it is written.
- EXACT COUNT: the word "और" appears exactly TWICE in total in this clip — once as the first word of the first phrase and once as the first word of the second phrase. Nowhere else, in any size, at any moment, and never twice inside the same phrase.
- EXACT COUNT: the word "इस" appears exactly TWICE in total in this clip — once in the first phrase and once in the second phrase. Nowhere else, in any size, at any moment, and never twice inside the same phrase.
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, a number, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. In THIS clip words repeat across the phrases, so BOTH phrases are completely uniform bold white and there is NO golden word anywhere in this clip. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters, matras or conjuncts are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time, perfectly synced with the animation timeline below. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean crisp flat overlay typography on a dark technical background. Never photorealistic. NO fire, NO flame, NO sparks, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: completely empty background. Nothing at all.

ANIMATION TIMELINE:
0.0–4.8 s — the first phrase "और इस साल भी आपकी त्रैमासिक परीक्षा में आ सकता है।" pops in fully sharp at the very top of the frame, completely uniform bold white, and holds perfectly still. At 4.8 s it disappears completely in a single clean fade.
4.8–5.0 s — a 0.2 second gap in which no phrase is visible anywhere on screen.
5.0–10.0 s — the second phrase "और इस वीडियो के अंत तक" pops in fully sharp in the same place at the very top of the frame, completely uniform bold white, and holds perfectly still until 10.0 s.
Nothing else happens. Nothing enters the lower half of the frame at any moment.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "और इस साल भी आपकी त्रैमासिक परीक्षा में आ सकता है।"
2. "और इस वीडियो के अंत तक"

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, curly quotation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, invented labels, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, any voiceover, any narration, any spoken words, any human voice, any singing, background music, sound effects, an automatic caption, an auto-generated subtitle, a burnt-in subtitle bar, closed captions, a transcript line, any text that appears because speech was generated, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, Latin or Roman letters, English words, Devanagari text transliterated into Latin letters, detached vowel signs, broken matras, split conjunct letters, a missing or misplaced halant mark, the word "और" appearing three or more times, the word "इस" appearing three or more times, any beaker, jar, liquid, electrode, battery, cell, wire, ammeter, ion, bubble, arrow, shape, icon or illustration of any kind, any electrolysis apparatus, any galvanic or voltaic cell, any label plate, any equation, any mathematical symbol, the proportionality sign, the letters W, Q, i, t, Z or E anywhere on screen, any digit, number, year or date, a golden word in either phrase
```

---

```
VIDEO PROMPT — SEGMENT 3 OF 24

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

AUDIO: this clip is completely SILENT. There is no voiceover, no narration, no speech, no singing, no music, no sound effects and no ambient sound of any kind. No voice is generated at any moment. The audio track is empty. The spoken narration is added separately in editing from a different source.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, filling the width, starting close to the top edge, large enough to fill the upper area comfortably. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

NO DIAGRAM IN THIS CLIP (CRITICAL): this clip contains NO three dimensional object of any kind. There is no beaker, no jar, no liquid, no electrode, no battery, no cell, no wire, no ammeter, no ion, no bubble, no arrow, no equation, no shape, no icon and no illustration anywhere in the frame at any moment. The only things on screen are the script text and the plain background. Do not invent, add or imagine any diagram, object or graphic. The space below the script text stays as plain empty background.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE. Every word appears exactly the number of times it is written.
- SCRIPT LOCK: all text in this clip is written in the Devanagari script exactly as given, character by character, matra by matra. It is NEVER transliterated into Latin or Roman letters, NEVER translated into English, and NEVER mixed with English words. Conjunct letters stay joined, vowel signs stay attached to their consonant, and the halant mark stays exactly where it is written.
- EXACT COUNT: the word "फैराडे" appears exactly ONCE in this whole clip, inside the first phrase, styled in golden in its own place inside that sentence. It is never written a second time, never repeated on its own line, never enlarged into a separate title and never placed anywhere outside that sentence.
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, a number, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. In THIS clip there is exactly ONE golden word in the whole clip: the word "फैराडे" inside the first phrase, coloured warm golden while every other word of that phrase stays bold white. The second phrase and the third phrase are completely uniform bold white with NO golden word. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters, matras or conjuncts are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time, perfectly synced with the animation timeline below. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean crisp flat overlay typography on a dark technical background. Never photorealistic. NO fire, NO flame, NO sparks, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: completely empty background. Nothing at all.

ANIMATION TIMELINE:
0.0–3.3 s — the first phrase "आप फैराडे के दोनों नियमों को पूरा याद करके," pops in fully sharp at the very top of the frame, bold white with the single word "फैराडे" in warm golden in its own place inside the sentence, and holds perfectly still. At 3.3 s the whole phrase disappears completely in a single clean fade.
3.3–3.5 s — a 0.2 second gap in which no phrase is visible anywhere on screen.
3.5–6.6 s — the second phrase "परीक्षा में सही तरीके से लिखना भी सीख जाओगे।" pops in fully sharp in the same place, completely uniform bold white, and holds perfectly still. At 6.6 s it disappears completely in a single clean fade.
6.6–6.8 s — a 0.2 second gap in which no phrase is visible anywhere on screen.
6.8–10.0 s — the third phrase "तो चलिए।" pops in fully sharp in the same place, completely uniform bold white, and holds perfectly still until 10.0 s.
Nothing else happens. Nothing enters the lower half of the frame at any moment.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "आप फैराडे के दोनों नियमों को पूरा याद करके,"
2. "परीक्षा में सही तरीके से लिखना भी सीख जाओगे।"
3. "तो चलिए।"

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, curly quotation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, the golden word written a second time anywhere, the word "फैराडे" appearing twice, a golden word in the second or third phrase, more than one golden word in the clip, invented labels, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, any voiceover, any narration, any spoken words, any human voice, any singing, background music, sound effects, an automatic caption, an auto-generated subtitle, a burnt-in subtitle bar, closed captions, a transcript line, any text that appears because speech was generated, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, Latin or Roman letters, English words, Devanagari text transliterated into Latin letters, detached vowel signs, broken matras, split conjunct letters, a missing or misplaced halant mark, any beaker, jar, liquid, electrode, battery, cell, wire, ammeter, ion, bubble, arrow, shape, icon or illustration of any kind, any electrolysis apparatus, any galvanic or voltaic cell, any label plate, any equation, any mathematical symbol, the proportionality sign, the letters W, Q, i, t, Z or E anywhere on screen, any digit, number, year or date
```

---

```
VIDEO PROMPT — SEGMENT 4 OF 24

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

AUDIO: this clip is completely SILENT. There is no voiceover, no narration, no speech, no singing, no music, no sound effects and no ambient sound of any kind. No voice is generated at any moment. The audio track is empty. The spoken narration is added separately in editing from a different source.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, filling the width, starting close to the top edge, large enough to fill the upper area comfortably. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

NO DIAGRAM IN THIS CLIP (CRITICAL): this clip contains NO three dimensional object of any kind. There is no beaker, no jar, no liquid, no electrode, no battery, no cell, no wire, no ammeter, no ion, no bubble, no arrow, no equation, no shape, no icon and no illustration anywhere in the frame at any moment. The only things on screen are the script text and the plain background. Do not invent, add or imagine any diagram, object or graphic. The space below the script text stays as plain empty background.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE. Every word appears exactly the number of times it is written.
- SCRIPT LOCK: all text in this clip is written in the Devanagari script exactly as given, character by character, matra by matra. It is NEVER transliterated into Latin or Roman letters, NEVER translated into English, and NEVER mixed with English words. Conjunct letters stay joined, vowel signs stay attached to their consonant, and the halant mark stays exactly where it is written.
- EXACT COUNT: the long dash inside the first phrase appears exactly ONCE, as a single plain horizontal dash between "हैं" and "फैराडे", with no space turned into a second dash, no double dash and no line break at that dash. The words on both sides of it stay on the same running sentence.
- EXACT COUNT: the word "ध्यान" appears exactly ONCE in this whole clip, inside the second phrase, styled in golden in its own place inside that sentence. It is never written a second time and never placed on its own line.
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, a number, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. In THIS clip there is exactly ONE golden word in the whole clip: the word "ध्यान" inside the second phrase, coloured warm golden while every other word of that phrase stays bold white. The first phrase and the third phrase are completely uniform bold white with NO golden word. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters, matras or conjuncts are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time, perfectly synced with the animation timeline below. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean crisp flat overlay typography on a dark technical background. Never photorealistic. NO fire, NO flame, NO sparks, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: completely empty background. Nothing at all.

ANIMATION TIMELINE:
0.0–3.3 s — the first phrase "सबसे पहले समझते हैं—फैराडे का पहला नियम।" pops in fully sharp at the very top of the frame, completely uniform bold white, and holds perfectly still. At 3.3 s it disappears completely in a single clean fade.
3.3–3.5 s — a 0.2 second gap in which no phrase is visible anywhere on screen.
3.5–6.6 s — the second phrase "और इसे ध्यान से समझना," pops in fully sharp in the same place, bold white with the single word "ध्यान" in warm golden in its own place inside the sentence, and holds perfectly still. At 6.6 s the whole phrase disappears completely in a single clean fade.
6.6–6.8 s — a 0.2 second gap in which no phrase is visible anywhere on screen.
6.8–10.0 s — the third phrase "क्योंकि अगर परीक्षा में बिल्कुल ऐसा ही लिख दिया," pops in fully sharp in the same place, completely uniform bold white, and holds perfectly still until 10.0 s.
Nothing else happens. Nothing enters the lower half of the frame at any moment.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "सबसे पहले समझते हैं—फैराडे का पहला नियम।"
2. "और इसे ध्यान से समझना,"
3. "क्योंकि अगर परीक्षा में बिल्कुल ऐसा ही लिख दिया,"

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, curly quotation marks, a double dash, an extra dash, a dash turning into a line break, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, the golden word written a second time anywhere, the word "ध्यान" appearing twice, a golden word in the first or third phrase, more than one golden word in the clip, invented labels, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, any voiceover, any narration, any spoken words, any human voice, any singing, background music, sound effects, an automatic caption, an auto-generated subtitle, a burnt-in subtitle bar, closed captions, a transcript line, any text that appears because speech was generated, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, Latin or Roman letters, English words, Devanagari text transliterated into Latin letters, detached vowel signs, broken matras, split conjunct letters, a missing or misplaced halant mark, any beaker, jar, liquid, electrode, battery, cell, wire, ammeter, ion, bubble, arrow, shape, icon or illustration of any kind, any electrolysis apparatus, any galvanic or voltaic cell, any label plate, any equation, any mathematical symbol, the proportionality sign, the letters W, Q, i, t, Z or E anywhere on screen, any digit, number, year or date
```

---

**Tool setting:** 1080×1920 select karna. Background image upload karna.

Generate **Segment 1 alone first**. It is the Devanagari test — if `12वीं`, the matras or the conjuncts come out broken, the fix is architectural (Veo renders visuals only, text burnt in during editing) and segments 5–24 shouldn't be written against a prompt shape that can't work. Once Seg 1 reads clean, run 2–4, then say go and I'll write Clip 2 (Seg 5–12), where the cell diagram and §18 top-half enforcement enter.

Reference frame read — it confirms the cell layout (beaker, two electrodes, battery **+** left / **−** right, ammeter, deposit on the right-hand electrode = cathode). I've used that orientation so the generated cell matches the answer card, and locked it against the galvanic-cell error.

Two things applied that the plan predated: **§17 SILENT CLIP** (audio comes from the HeyGen avatar now — Veo's own voiceover also drags in burnt-in captions), and **§18 top-half enforcement** on both diagram segments, since your reference frame is a landscape full-bleed poster and that exact shape caused the diagram to cross the middle line last time. Seg 6 also gets **§19 SAME ELEMENT RULE** — the deposit must thicken on the cathode and nothing else may change.

---

## SEGMENT 5 — DIAGRAM (cell builds)

```
VIDEO PROMPT — SEGMENT 5 OF 24

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

AUDIO: this clip is completely SILENT. There is no voiceover, no narration, no speech, no singing, no music, no sound effects and no ambient sound of any kind. No voice is generated at any moment. The audio track is empty. The spoken narration is added separately in editing from a different source.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, starting close to the top edge. The diagram sits directly below the script text and fills the space between the text and the invisible middle line, so the top half never looks empty. The lowest part of the diagram stops with a clear visible gap above the invisible middle line and never touches it; if it does not fit, make it smaller. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

SIZE AND POSITION CHECK (CRITICAL): before anything is drawn, the diagram is scaled so that its complete height — including every wire, arrow, glow and shadow — fits inside the upper half of the frame with a clear visible margin still left below it. If any part of the diagram would reach the middle of the frame, the whole diagram is made smaller until it does not. The diagram never grows, drifts downward, expands or scales up at any moment during the clip. The lower half of the frame contains nothing but the background from the first frame to the last. This is a vertical composition — never a wide full-bleed poster layout that fills the whole frame.

3D RENDER QUALITY (CRITICAL — THIS MAKES THE DIAGRAM LOOK THREE DIMENSIONAL):
The diagram is a real three dimensional object rendered in depth, not a flat drawing.
- CAMERA: a fixed three-quarter view from slightly above the object, so the viewer looks slightly down at it and can clearly read its roundness. Never a flat straight-on front view.
- PERSPECTIVE: circles that run around the object appear as flattened ellipses because of the viewing angle, becoming flatter near the top and bottom and rounder near the middle. Nothing is drawn as a plain flat circle.
- DEPTH: the parts nearest the camera are brighter, thicker and sharper. The parts on the far side, seen through the transparent surface, are noticeably dimmer, thinner and softer. This difference is clear and obvious.
- LIGHTING: one soft cool rim light along the upper left edge and a gentle ambient fill, giving a rounded sculpted look with a soft falloff toward the lower right.
- MATERIAL: a smooth glossy glass-like surface with a faint specular highlight near the upper left, and a soft inner glow.
- FORESHORTENING: any arrow pointing toward the camera looks shorter and thicker with a larger arrowhead, and any arrow pointing away looks longer and thinner. They are never all the same length on screen.
- MOTION: the object holds perfectly still once settled. It never wobbles, never squashes, never deforms and never changes size once settled.

DIAGRAM SPECIFICATION (build exactly this, nothing else):
- THE BEAKER: one wide glass beaker rendered in full three dimensions, seen from a three-quarter view slightly above, so its circular rim reads as a flattened ellipse. The glass is clear and see-through with a soft cool rim light along its upper left edge and a faint specular highlight. It never becomes solid or opaque.
- THE ELECTROLYTE: a translucent pale cyan-blue liquid filling the lower two thirds of the beaker, with a calm flat elliptical surface. It never boils, never bubbles, never froths and never changes colour.
- THE ELECTRODES: exactly TWO flat vertical rectangular plates dipped straight down into the liquid from above, one on the left and one on the right, clearly separated by a wide gap of liquid between them. The left plate is brushed grey metal. The right plate is warm brown-copper metal. Both hang freely — they never touch each other, never touch the walls of the beaker and never touch the bottom of the beaker. A clear gap of liquid is visible under each plate.
- THE BATTERY AND CIRCUIT: one battery drawn above the beaker as a small three dimensional cylinder lying horizontally, its LEFT end marked with a small plus sign as the positive terminal and its RIGHT end marked with a small minus sign as the negative terminal. Two thin grey wires run from the battery down the outside of the beaker, one to the top of the left plate and one to the top of the right plate, forming ONE single unbroken closed loop with no gaps and no open switch anywhere. A small round analogue meter with a thin needle sits in the wire on the right side of the battery. The circuit is complete and closed from the very first frame it exists.
- THE CURRENT ARROWS: small bright cyan arrows sitting on the wires outside the beaker, all pointing the same way around the loop, leaving the battery from its positive left end and travelling around to the right plate.
- THE IONS: small round dots drifting slowly inside the liquid. Blue dots drift steadily to the RIGHT, toward the right-hand plate. Orange dots drift steadily to the LEFT, toward the left-hand plate. The two colours always move in OPPOSITE directions and never travel the same way.
- THE DEPOSIT: a thin even reddish-brown layer that forms on the face of the RIGHT-HAND plate only. It stays thin in this clip.
- LABELS: this clip has NO labels at all. No plate, no chip, no tag, no floating letter, no leader line. Never invent a label.

DIAGRAM TIMING SYNC (CRITICAL): every object appears at the exact moment its name is visible in the written phrase on screen, and never a frame before. Once an object appears it stays to the end of the clip. The battery, the wires, the meter and the electrodes all appear together in the same instant as one already-complete closed circuit — the circuit is never shown broken, half-drawn or unconnected at any moment.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE. Every word appears exactly the number of times it is written.
- The text is Hindi in the Devanagari script. Every matra, every vowel sign, every conjunct and every halant is rendered exactly as written, letter by letter. The word "विद्युत्" ends in a halant and is always written exactly that way. The word "विद्युत्-अपघटन" carries one single hyphen and is never split across two lines.
- EXACT COUNT: the word "मात्रा" appears exactly ONCE in this whole clip, inside the third phrase. Nowhere else, in any size, at any moment.
- EXACT COUNT: the word "इलेक्ट्रोड" appears exactly ONCE in this whole clip, inside the second phrase. It is never written again as a label or beside the diagram.
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. In this clip EVERY phrase is rendered completely uniform in bold white with NO golden word anywhere. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean, glossy, textbook-style chemistry illustration rendered in three dimensions — smooth shapes, flat bright colours, soft even glow, like a modern NCERT diagram built in 3D. Never photorealistic. NO fire, NO flame, NO burning, NO spark, NO ember, NO explosion, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: completely empty background. Nothing at all.

ANIMATION TIMELINE:
0.0–3.3 s — the first phrase "तो आपके नंबर पक्के हैं।" pops in at the very top of the frame, fully sharp from its first visible frame, and holds. The rest of the frame is empty background.
3.3 s — the first phrase disappears completely.
3.5–6.6 s — after a 0.2 second gap the second phrase "तो जब विद्युत्-अपघटन के दौरान किसी इलेक्ट्रोड पर" pops in at the top and holds.
4.2 s — exactly as the word विद्युत्-अपघटन is visible on screen, the glass beaker with its pale cyan electrolyte pops in below the text, already at its final size, sitting in the upper half with a clear gap above the middle of the frame.
5.2 s — exactly as the word इलेक्ट्रोड is visible on screen, the two electrode plates, the battery, both wires and the round meter appear together in one instant as a single complete closed circuit, and the cyan current arrows begin travelling around the wire loop.
6.6 s — the second phrase disappears completely.
6.8–10.0 s — after a 0.2 second gap the third phrase "मुक्त होने वाले पदार्थ की मात्रा," pops in at the top and holds to the end.
7.4 s — exactly as the word पदार्थ is visible on screen, the blue dots begin drifting to the right and the orange dots begin drifting to the left inside the liquid, and a thin reddish-brown deposit layer appears on the face of the right-hand plate.
7.4–10.0 s — the diagram holds completely still at the same size and position, the ions keep drifting, and nothing else enters the frame.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "तो आपके नंबर पक्के हैं।"
2. "तो जब विद्युत्-अपघटन के दौरान किसी इलेक्ट्रोड पर"
3. "मुक्त होने वाले पदार्थ की मात्रा,"
Nothing else is written anywhere on screen at any moment.

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, the diagram crossing the middle of the frame, the diagram touching the middle of the frame, the diagram growing or expanding during the clip, the diagram drifting downward, an arrow or wire reaching into the lower half, the illustration filling the whole frame, a full-frame poster layout, a wide landscape composition, two phrases visible at the same time, garbled letters during a transition, broken Devanagari conjuncts, a missing or misplaced matra, a missing halant, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, a golden or coloured word in any phrase, invented labels, any label plate, any chip, any tag, any callout, any leader line, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, any equation, any formula, any mathematical symbol, the letters W, Q, i, t, Z or E anywhere on screen, any number or digit, any unit, the value 96500, a Faraday constant, the letter F, watermark, an automatic subtitle bar at the bottom, any voiceover, any narration, any spoken words, any human voice, any singing, background music, sound effects, an automatic caption, an auto-generated subtitle, a burnt-in subtitle bar, closed captions, a transcript line, any text that appears because speech was generated, a galvanic cell, a voltaic cell, a cell with its negative terminal driving the deposit, the deposit forming on the left-hand plate, deposit on both plates, blue and orange dots drifting in the same direction, all ions moving the same way, a broken or open circuit while current arrows are moving, an open switch, a light bulb, an alternating current source, bubbles at any electrode, gas bubbles rising in the liquid, boiling liquid, the electrodes touching each other, an electrode touching the bottom of the beaker, only one electrode, three or more electrodes, the beaker appearing before 4.2 seconds, the electrodes appearing before 5.2 seconds, the ions or deposit appearing before 7.4 seconds, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, camera movement, zoom, scene change, background change
```

---

## SEGMENT 6 — DIAGRAM (deposit grows)

```
VIDEO PROMPT — SEGMENT 6 OF 24

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

AUDIO: this clip is completely SILENT. There is no voiceover, no narration, no speech, no singing, no music, no sound effects and no ambient sound of any kind. No voice is generated at any moment. The audio track is empty. The spoken narration is added separately in editing from a different source.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, starting close to the top edge. The diagram sits directly below the script text and fills the space between the text and the invisible middle line, so the top half never looks empty. The lowest part of the diagram stops with a clear visible gap above the invisible middle line and never touches it; if it does not fit, make it smaller. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

SIZE AND POSITION CHECK (CRITICAL): before anything is drawn, the diagram is scaled so that its complete height — including every wire, arrow, glow and shadow — fits inside the upper half of the frame with a clear visible margin still left below it. If any part of the diagram would reach the middle of the frame, the whole diagram is made smaller until it does not. The diagram never grows, drifts downward, expands or scales up at any moment during the clip. The lower half of the frame contains nothing but the background from the first frame to the last. This is a vertical composition — never a wide full-bleed poster layout that fills the whole frame.

3D RENDER QUALITY (CRITICAL — THIS MAKES THE DIAGRAM LOOK THREE DIMENSIONAL):
The diagram is a real three dimensional object rendered in depth, not a flat drawing.
- CAMERA: a fixed three-quarter view from slightly above the object, so the viewer looks slightly down at it and can clearly read its roundness. Never a flat straight-on front view.
- PERSPECTIVE: circles that run around the object appear as flattened ellipses because of the viewing angle, becoming flatter near the top and bottom and rounder near the middle. Nothing is drawn as a plain flat circle.
- DEPTH: the parts nearest the camera are brighter, thicker and sharper. The parts on the far side, seen through the transparent surface, are noticeably dimmer, thinner and softer. This difference is clear and obvious.
- LIGHTING: one soft cool rim light along the upper left edge and a gentle ambient fill, giving a rounded sculpted look with a soft falloff toward the lower right.
- MATERIAL: a smooth glossy glass-like surface with a faint specular highlight near the upper left, and a soft inner glow.
- FORESHORTENING: any arrow pointing toward the camera looks shorter and thicker with a larger arrowhead, and any arrow pointing away looks longer and thinner. They are never all the same length on screen.
- MOTION: the object holds perfectly still. It never wobbles, never squashes, never deforms and never changes size.

DIAGRAM SPECIFICATION (build exactly this, nothing else — it is identical to the previous clip and is already fully present at the very first frame):
- THE BEAKER: one wide glass beaker rendered in full three dimensions, seen from a three-quarter view slightly above, so its circular rim reads as a flattened ellipse. The glass is clear and see-through with a soft cool rim light along its upper left edge. It never becomes solid or opaque.
- THE ELECTROLYTE: a translucent pale cyan-blue liquid filling the lower two thirds of the beaker, with a calm flat elliptical surface. It never boils, never bubbles, never froths and never changes colour.
- THE ELECTRODES: exactly TWO flat vertical rectangular plates dipped straight down into the liquid, one on the left and one on the right, clearly separated by a wide gap of liquid. The left plate is brushed grey metal. The right plate is warm brown-copper metal. Neither plate touches the other, the beaker walls or the beaker bottom.
- THE BATTERY AND CIRCUIT: one battery above the beaker as a small horizontal three dimensional cylinder, its LEFT end marked with a small plus sign as the positive terminal and its RIGHT end marked with a small minus sign as the negative terminal, joined by two thin grey wires down to the tops of the two plates in ONE single unbroken closed loop, with a small round analogue meter in the wire on the right side of the battery. The loop is closed at every moment of the clip.
- THE CURRENT ARROWS: small bright cyan arrows on the wires outside the beaker, all pointing the same way around the loop, leaving the battery from its positive left end. They keep the same size, the same number and the same positions for the whole clip and only change in brightness.
- THE IONS: small round dots drifting slowly inside the liquid — blue dots drifting steadily to the RIGHT toward the right-hand plate, orange dots drifting steadily to the LEFT toward the left-hand plate. The two colours always move in OPPOSITE directions.
- THE DEPOSIT: a reddish-brown layer on the face of the RIGHT-HAND plate only. It begins thin and grows thicker during this clip. It never appears on the left-hand plate.
- LABELS: this clip has NO labels at all. No plate, no chip, no tag, no floating letter, no leader line. Never invent a label.

DIAGRAM TIMING SYNC (CRITICAL): the diagram carried over from the previous clip is already present at the very first frame and does not fade in again. Nothing new enters the frame at any moment; the only change in the whole clip is the deposit thickening on the right-hand plate and the current arrows brightening.

SAME ELEMENT RULE (CRITICAL): the plate that carries the deposit and the plate on which the deposit thickens are THE SAME SINGLE plate — not the other one, not both, not an additional one. Counting from the left-hand end, it is plate number two, the right-hand brown-copper plate joined to the minus end of the battery, and it is the only element in the whole clip that changes in any way. Every other element — the left-hand grey plate, the beaker, the liquid, the battery, the wires, the meter and the ions — keeps its original colour, size and position from the first frame to the last, without exception. The change happens in place, on the plate that already carries the thin deposit.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE beyond what is written. Every word appears exactly the number of times it is written.
- The text is Hindi in the Devanagari script. Every matra, every vowel sign, every conjunct and every halant is rendered exactly as written, letter by letter. The word "विद्युत्" ends in a halant and is always written exactly that way.
- EXACT COUNT: the word "मात्रा" appears exactly TWICE in total in this clip — once inside the first phrase and once inside the third phrase. Nowhere else, in any size, at any moment.
- EXACT COUNT: the word "अधिक" appears exactly TWICE in total in this clip — once inside the second phrase and once inside the third phrase. Nowhere else.
- EXACT COUNT: the word "विद्युत्" appears exactly TWICE in total in this clip — once inside the first phrase and once inside the second phrase. Nowhere else.
- EXACT COUNT: the word "प्रवाहित" appears exactly TWICE in total in this clip — once inside the first phrase and once inside the second phrase. Nowhere else.
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. In this clip EVERY phrase is rendered completely uniform in bold white with NO golden word anywhere. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean, glossy, textbook-style chemistry illustration rendered in three dimensions — smooth shapes, flat bright colours, soft even glow, like a modern NCERT diagram built in 3D. Never photorealistic. NO fire, NO flame, NO burning, NO spark, NO ember, NO explosion, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: continuing exactly from the previous clip — the complete three dimensional electrolysis cell is already fully present at the very first frame in the upper half of the frame: the glass beaker with pale cyan electrolyte, the grey left plate and the brown-copper right plate dipped in it, the battery above with its plus end on the left and minus end on the right, both wires and the round meter forming one closed loop, cyan current arrows travelling around the wires, blue dots drifting right and orange dots drifting left inside the liquid, and a thin reddish-brown deposit already on the face of the right-hand plate. There is no text on screen at the very first frame. Nothing else.

ANIMATION TIMELINE:
0.0 s — the diagram is already present, exactly as described, and does not fade in again.
0.0–3.3 s — the first phrase "प्रवाहित विद्युत् की मात्रा के समानुपाती होती है।" pops in at the very top of the frame, fully sharp from its first visible frame, and holds.
3.3 s — the first phrase disappears completely.
3.5–6.6 s — after a 0.2 second gap the second phrase "मतलब, जितनी अधिक विद्युत् प्रवाहित होगी," pops in at the top and holds.
4.0–5.0 s — the cyan current arrows on the wires brighten smoothly and keep that brightness for the rest of the clip. They do not change size, number or position.
6.6 s — the second phrase disappears completely.
6.8–10.0 s — after a 0.2 second gap the third phrase "उतनी ही अधिक मात्रा में पदार्थ इलेक्ट्रोड पर मुक्त होगा।" pops in at the top and holds to the end.
7.2–9.0 s — exactly as the word पदार्थ is visible on screen, the reddish-brown deposit already on the right-hand plate thickens smoothly and evenly in place on that same plate, and then holds. No other element changes in any way.
9.0–10.0 s — everything holds perfectly still.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "प्रवाहित विद्युत् की मात्रा के समानुपाती होती है।"
2. "मतलब, जितनी अधिक विद्युत् प्रवाहित होगी,"
3. "उतनी ही अधिक मात्रा में पदार्थ इलेक्ट्रोड पर मुक्त होगा।"
Nothing else is written anywhere on screen at any moment.

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, the diagram crossing the middle of the frame, the diagram touching the middle of the frame, the diagram growing or expanding during the clip, the diagram drifting downward, an arrow or wire reaching into the lower half, the illustration filling the whole frame, a full-frame poster layout, a wide landscape composition, two phrases visible at the same time, garbled letters during a transition, broken Devanagari conjuncts, a missing or misplaced matra, a missing halant, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, a golden or coloured word in any phrase, invented labels, any label plate, any chip, any tag, any callout, any leader line, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, any equation, any formula, any mathematical symbol, the letters W, Q, i, t, Z or E anywhere on screen, any number or digit, any unit, the value 96500, a Faraday constant, the letter F, watermark, an automatic subtitle bar at the bottom, any voiceover, any narration, any spoken words, any human voice, any singing, background music, sound effects, an automatic caption, an auto-generated subtitle, a burnt-in subtitle bar, closed captions, a transcript line, any text that appears because speech was generated, a galvanic cell, a voltaic cell, the deposit forming on the left-hand plate, deposit on both plates, the left-hand grey plate changing colour, the left-hand plate changing in any way, two plates changing, the deposit moving to the other plate, a different element changing colour, the deposit growing on a neighbouring element, blue and orange dots drifting in the same direction, all ions moving the same way, a broken or open circuit while current arrows are moving, an open switch, a light bulb, an alternating current source, bubbles at any electrode, gas bubbles rising in the liquid, boiling liquid, the electrodes touching each other, an electrode touching the bottom of the beaker, only one electrode, three or more electrodes, the cell fading in again, the cell disappearing, a new object entering the frame, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, camera movement, zoom, scene change, background change
```

---

## SEGMENT 7 — TRANSITION (cell fades → **W ∝ Q**)

```
VIDEO PROMPT — SEGMENT 7 OF 24

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

AUDIO: this clip is completely SILENT. There is no voiceover, no narration, no speech, no singing, no music, no sound effects and no ambient sound of any kind. No voice is generated at any moment. The audio track is empty. The spoken narration is added separately in editing from a different source.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, starting close to the top edge. The diagram and then the equation sit directly below the script text, filling the space between the text and the invisible middle line. The lowest element stops with a clear visible gap above the invisible middle line and never touches it; if it does not fit, make it smaller. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

SIZE AND POSITION CHECK (CRITICAL): the diagram is scaled so that its complete height — including every wire, arrow, glow and shadow — fits inside the upper half of the frame with a clear visible margin still left below it. If any part of it would reach the middle of the frame, the whole diagram is made smaller until it does not. The diagram never grows, drifts downward, expands or scales up at any moment; it only shrinks as described in the timeline. The equation likewise sits comfortably above the invisible middle line. The lower half of the frame contains nothing but the background from the first frame to the last. This is a vertical composition — never a wide full-bleed poster layout that fills the whole frame.

3D RENDER QUALITY (for the diagram in the first half of this clip):
The diagram is a real three dimensional object rendered in depth, not a flat drawing — a fixed three-quarter view from slightly above, circles appearing as flattened ellipses, near-side lines brighter and sharper than far-side lines, a soft cool rim light along the upper left edge, glossy glass-like material with a faint specular highlight, and no wobble, no deformation and no change of shape.

DIAGRAM SPECIFICATION: the scene from the previous clip — the complete three dimensional electrolysis cell with its glass beaker of pale cyan electrolyte, the grey left plate and the brown-copper right plate carrying its reddish-brown deposit, the battery above with its plus end on the left and minus end on the right, both wires, the round meter, the cyan current arrows on the wires, and the blue dots drifting right and orange dots drifting left inside the liquid — is present at the very first frame. It shrinks smoothly to about half its size, drifts upward, and fades away completely by 4.0 seconds, leaving the area below the script text free for the equation. While it shrinks nothing about it changes: no new part appears, the deposit stays only on the right-hand plate, the circuit stays closed, and the two ion colours keep moving in opposite directions. LABELS: this clip has NO labels at all. Never invent a label.

DIAGRAM TIMING SYNC (CRITICAL): the diagram carried over from the previous clip is already present at the very first frame and does not fade in again. The equation appears at the exact moment the letter that names it is visible in the written phrase on screen, and never before.

EQUATION RULE (CRITICAL): the equation is flat two dimensional overlay text, not a three dimensional object. It is ONE single clean horizontal line of large bold white mathematical text with a soft cyan glow, centred below the script text, perfectly sharp, with every symbol correct and correctly sized. It reads exactly: W ∝ Q — a capital W, then the proportionality sign, then a capital Q, in that order, with nothing else on the line. The proportionality sign is the curled proportional-to glyph and is NEVER the Greek letter alpha, NEVER an infinity sign and NEVER an equals sign. The letters are italic mathematical letters. It is not on a card, not in a box, and never stacked onto two lines. If it is too wide, reduce its size until the whole line fits comfortably inside the frame width with clear margins on both sides. It appears exactly once and holds to the end of the clip. The script text stays at the top and the equation stays below it — they never overlap and never swap places.

HIGHLIGHT RULE (CRITICAL — NO NEW TEXT IS EVER CREATED): when a part of the equation is emphasised, that part of the EXISTING equation simply changes colour and glows brighter in place. NEVER copy a symbol out of the equation. NEVER draw a second copy of any symbol anywhere. NEVER create a label, plate, chip, callout or floating letter for it. The equation itself is the only place any symbol ever appears.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE. Every word appears exactly the number of times it is written.
- The text is Hindi in the Devanagari script. Every matra, every vowel sign, every conjunct and every halant is rendered exactly as written, letter by letter. The word "विद्युत्" ends in a halant and is always written exactly that way.
- EXACT COUNT: the letter "W" appears exactly TWICE in total in this clip — once inside the first phrase and once inside the equation. Nowhere else, in any size, at any moment.
- EXACT COUNT: the letter "Q" appears exactly TWICE in total in this clip — once inside the second phrase and once inside the equation. Nowhere else, in any size, at any moment.
- EXACT COUNT: the word "मात्रा" appears exactly TWICE in total in this clip — once inside the first phrase and once inside the second phrase. Nowhere else.
- EXACT COUNT: the proportionality sign appears exactly ONCE in this clip, inside the equation. Nowhere else.
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Both phrases in this clip contain a standalone single letter, so BOTH are rendered completely uniform in bold white with NO golden word anywhere. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters or mathematical symbols individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters or mathematical symbols are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean, glossy, textbook-style chemistry illustration rendered in three dimensions for the diagram, and clean crisp flat overlay typography for the equation. Never photorealistic. NO fire, NO flame, NO burning, NO spark, NO ember, NO explosion, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: continuing exactly from the previous clip — the complete three dimensional electrolysis cell is already fully present at the very first frame in the upper half of the frame: the glass beaker with pale cyan electrolyte, the grey left plate, the brown-copper right plate with its thick reddish-brown deposit, the battery above with plus on the left and minus on the right, both wires and the round meter forming one closed loop, bright cyan current arrows on the wires, blue dots drifting right and orange dots drifting left inside the liquid. There is no text and no equation on screen at the very first frame. Nothing else.

ANIMATION TIMELINE:
0.0 s — the cell is already present, exactly as described, and does not fade in again.
0.0–4.8 s — the first phrase "यहाँ W है मुक्त पदार्थ की मात्रा" pops in at the very top of the frame, fully sharp from its first visible frame, and holds.
1.0–4.0 s — the whole cell shrinks smoothly to about half its size, drifts upward, and fades out completely, so that by 4.0 seconds nothing of it remains anywhere on screen.
4.8 s — the first phrase disappears completely.
5.0–10.0 s — after a 0.2 second gap the second phrase "और Q है प्रवाहित विद्युत् की मात्रा।" pops in at the top and holds to the end.
5.4 s — exactly as the letter Q is visible on screen inside the phrase, the equation W ∝ Q pops in as one single sharp horizontal line below the script text, fully correct from its first visible frame, and holds completely still to the end of the clip.
5.4–10.0 s — the equation never moves, never resizes, never duplicates. Nothing else is on screen.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "यहाँ W है मुक्त पदार्थ की मात्रा"
2. "और Q है प्रवाहित विद्युत् की मात्रा।"
3. "W ∝ Q"
Nothing else is written anywhere on screen at any moment.

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, the diagram crossing the middle of the frame, the diagram growing or expanding, the diagram drifting downward, the equation crossing the middle of the frame, the illustration filling the whole frame, a full-frame poster layout, a wide landscape composition, two phrases visible at the same time, garbled letters during a transition, broken Devanagari conjuncts, a missing or misplaced matra, a missing halant, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, a golden or coloured word in either phrase, invented labels, any label plate, any chip, any callout, any leader line, stray floating letters or symbols, a copy of any symbol taken out of the equation, a floating letter W anywhere outside the equation and the first phrase, a floating letter Q anywhere outside the equation and the second phrase, two copies of the equation, the equation moving or resizing, the equation stacked onto two lines, extra equations, a second formula, the equation appearing before 5.4 seconds, the cell still visible after 4.0 seconds, the cell fading back in, the proportionality sign drawn as the Greek letter alpha, the proportionality sign drawn as an infinity sign, the proportionality sign replaced by an equals sign, a capital I in place of anything, the letters Z, E, i or t appearing in this clip, W written after Q, any number or digit, any unit, the value 96500, a Faraday constant, the letter F, overlapping text, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, any voiceover, any narration, any spoken words, any human voice, any singing, background music, sound effects, an automatic caption, an auto-generated subtitle, a burnt-in subtitle bar, closed captions, a transcript line, any text that appears because speech was generated, a galvanic cell, the deposit on the left-hand plate, both ion colours moving the same way, an open circuit, bubbles at any electrode, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, camera movement, zoom, scene change, background change
```

---

## SEGMENT 8 — EQUATION_ONLY (**W ∝ Q** holds, highlights)

```
VIDEO PROMPT — SEGMENT 8 OF 24

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

AUDIO: this clip is completely SILENT. There is no voiceover, no narration, no speech, no singing, no music, no sound effects and no ambient sound of any kind. No voice is generated at any moment. The audio track is empty. The spoken narration is added separately in editing from a different source.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, starting close to the top edge. The equation sits directly below the script text, comfortably above the invisible middle line, and is large enough that the top half does not look empty. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

NO DIAGRAM IN THIS CLIP (CRITICAL): this clip contains NO three dimensional object of any kind. There is no beaker, no liquid, no electrode, no plate, no battery, no wire, no meter, no ion, no dot, no arrow, no shape, no icon and no illustration anywhere in the frame at any moment. The only things on screen are the script text, the equation, and the plain background. Do not invent, add or imagine any diagram, object or graphic. The space below the equation stays as plain empty background.

EQUATION RULE (CRITICAL): there is only ONE equation in this clip and it is already on screen at the very first frame. It reads exactly: W ∝ Q — a capital W, then the proportionality sign, then a capital Q, in that order, with nothing else on the line. The proportionality sign is the curled proportional-to glyph and is NEVER the Greek letter alpha, NEVER an infinity sign and NEVER an equals sign. It is flat two dimensional overlay text, not a three dimensional object. It never moves, never resizes, never duplicates and never leaves its place below the script text. It is ONE single clean horizontal line of large bold white mathematical text, perfectly sharp, with every symbol correct. Not on a card, not in a box, never stacked onto two lines.

HIGHLIGHT RULE (CRITICAL — NO NEW TEXT IS EVER CREATED): when a part of the equation is emphasised, that part of the EXISTING equation simply changes colour and glows brighter in place. NEVER copy a symbol out of the equation. NEVER draw a second copy of any symbol anywhere. NEVER create a label, plate, chip, callout or floating letter for it. The equation itself is the only place any symbol ever appears.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE beyond what is written. Every word appears exactly the number of times it is written.
- The text is Hindi in the Devanagari script. Every matra, every vowel sign, every conjunct and every halant is rendered exactly as written, letter by letter. The word "विद्युत्" ends in a halant and is always written exactly that way.
- EXACT COUNT: the word "मात्रा" appears exactly TWICE in total in this clip — once inside the second phrase and once inside the third phrase. Nowhere else, in any size, at any moment.
- EXACT COUNT: the letter "W" appears exactly ONCE in this whole clip, inside the equation. Nowhere else, in any size, at any moment.
- EXACT COUNT: the letter "Q" appears exactly ONCE in this whole clip, inside the equation. Nowhere else, in any size, at any moment.
- EXACT COUNT: the proportionality sign appears exactly ONCE in this clip, inside the equation. Nowhere else.
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. In this clip EVERY phrase is rendered completely uniform in bold white with NO golden word anywhere. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters or mathematical symbols individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters or mathematical symbols are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean crisp flat overlay typography on a dark technical background. Never photorealistic. NO fire, NO flame, NO sparks, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: continuing exactly from the previous clip — the equation W ∝ Q sits alone on one single line below where the text will appear, sharp and still, in bold white with a soft cyan glow. There is no text at the very first frame. Nothing else.

ANIMATION TIMELINE:
0.0 s — the equation is already present, exactly as described, and does not fade in again. It stays in exactly the same place, at exactly the same size, for the whole clip.
0.0–3.3 s — the first phrase "ये याद रखना," pops in at the very top of the frame, fully sharp from its first visible frame, and holds.
3.3 s — the first phrase disappears completely.
3.5–6.6 s — after a 0.2 second gap the second phrase "यहाँ संबंध विद्युत् की मात्रा" pops in at the top and holds.
4.4 s — the letter Q inside the existing equation turns bright yellow and glows, staying exactly in its place inside the equation, and holds that glow.
6.6 s — the second phrase disappears completely.
6.8–10.0 s — after a 0.2 second gap the third phrase "और मुक्त पदार्थ की मात्रा के बीच है।" pops in at the top and holds to the end.
7.4 s — the letter Q inside the equation returns to white, and at the same moment the letter W inside the existing equation turns bright yellow and glows, staying exactly in its place inside the equation.
9.4 s — the letter W returns to white, so the whole equation is bold white again and holds that way to 10.0 seconds.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "ये याद रखना,"
2. "यहाँ संबंध विद्युत् की मात्रा"
3. "और मुक्त पदार्थ की मात्रा के बीच है।"
4. "W ∝ Q"
Nothing else is written anywhere on screen at any moment.

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, the equation crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, broken Devanagari conjuncts, a missing or misplaced matra, a missing halant, any beaker, liquid, electrode, plate, battery, wire, meter, ion, dot, arrow, shape, icon or illustration of any kind, an electrolysis cell reappearing, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, a golden or coloured word in any phrase, invented labels, any label plate, any chip, any callout, any leader line, stray floating letters or symbols, a copy of any symbol taken out of the equation, a floating letter W anywhere outside the equation, a floating letter Q anywhere outside the equation, two copies of the equation, the equation moving or resizing, the equation stacked onto two lines, extra equations, a second formula, both letters glowing yellow at the same time, the proportionality sign changing colour, the proportionality sign drawn as the Greek letter alpha, the proportionality sign drawn as an infinity sign, the proportionality sign replaced by an equals sign, W written after Q, the letters Z, E, i or t appearing in this clip, a capital I, any number or digit, any unit, the value 96500, a Faraday constant, the letter F, wrong mathematical symbols, overlapping text, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, any voiceover, any narration, any spoken words, any human voice, any singing, background music, sound effects, an automatic caption, an auto-generated subtitle, a burnt-in subtitle bar, closed captions, a transcript line, any text that appears because speech was generated, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, camera movement, zoom, scene change, background change
```

---

**Notes on choices you may want to overrule:**

- **Seg 5–6 golden keyword:** none, per your plan's Clip-2 rule. Seg 5's first phrase ("तो आपके नंबर पक्के हैं।") technically qualifies for one golden word (नंबर) — say the word and I'll add it.
- **Deposit side is locked to the right-hand plate = minus terminal = cathode**, matching your reference frame, so the generated cell and the answer card agree. Both ion colours are specified moving in opposite directions (common error #4), and bubbles are banned outright rather than risking the one-electrode error (#8).
- **Devanagari is still unproven** — Seg 5 is the first clip in this set carrying a hyphenated conjunct-heavy word (विद्युत्-अपघटन). Generate **Seg 5 first as the test clip**; if the Devanagari breaks, don't burn the other three — the fix is architectural (Veo renders visuals only, text burned in during editing).

Frame confirms the exact symbol forms (`W ∝ Q`, `Q = i × t`, `W ∝ i × t`, `W = Z i t`, lowercase italic *i*, deposit on the cathode side, closed circuit with ammeter) — the specs below match it.

---

```
VIDEO PROMPT — SEGMENT 9 OF 24

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

AUDIO: this clip is completely SILENT. There is no voiceover, no narration, no speech, no singing, no music, no sound effects and no ambient sound of any kind. No voice is generated at any moment. The audio track is empty. The spoken narration is added separately in editing from a different source.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, starting close to the top edge. The equation sits directly below the script text, comfortably above the invisible middle line, and is large enough that the top half does not look empty. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

NO DIAGRAM IN THIS CLIP (CRITICAL): this clip contains NO three dimensional object of any kind. There is no beaker, no glass vessel, no liquid, no electrode, no metal plate, no battery, no wire, no ammeter, no ion, no bubble, no arrow, no icon and no illustration anywhere in the frame at any moment. The only things on screen are the script text, the equation, and the plain background. Do not invent, add or imagine any diagram, object or graphic. The space below the equation stays as plain empty background.

EQUATION RULE (CRITICAL): only ONE equation line is visible at any single moment in this clip. At the very first frame the line "W ∝ Q" is already on screen, alone, on one single line below where the script text appears. At 1.5 seconds it is replaced by the line "Q = i × t": the old line becomes completely invisible first, then the new line appears with a clean pop. The two lines are NEVER on screen together, never stacked, never crossfaded. The equation is flat two dimensional overlay text, not a three dimensional object. It is ONE single clean horizontal line of large bold white mathematical text, perfectly sharp, centred below the script text, with every symbol correct and correctly sized. It is not on a card, not in a box, not in a rounded plate, and never stacked onto two lines. It never moves, never resizes, never duplicates and never leaves its place below the script text.
SYMBOL FORMS (CRITICAL — EXACT GLYPHS): the sign "∝" is the mathematical proportionality sign, a small curled open glyph. It is NOT the Greek letter alpha, NOT the infinity sign, NOT the letter a and NOT an equals sign. The letter "i" is lowercase italic i — never capital I, never the letter A. The letter "Q" is capital Q, the letter "t" is lowercase t, the letter "W" is capital W. The multiplication sign in "Q = i × t" is a small centred cross. The order of the symbols is exactly "Q = i × t" — never "t × i", never "Q = i / t".

HIGHLIGHT RULE (CRITICAL — NO NEW TEXT IS EVER CREATED): when a part of the equation is emphasised, that part of the EXISTING equation simply changes colour and glows brighter in place. NEVER copy a symbol out of the equation. NEVER draw a second copy of any symbol anywhere. NEVER create a label, plate, chip, callout or floating letter for it. The equation itself is the only place any symbol ever appears.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE. Every word appears exactly the number of times it is written.
- EXACT COUNT: the lowercase letter "i" appears exactly TWICE in total in this clip — once inside the second phrase and once inside the equation "Q = i × t". Nowhere else, in any size, at any moment.
- EXACT COUNT: the lowercase letter "t" appears exactly TWICE in total in this clip — once inside the third phrase and once inside the equation "Q = i × t". Nowhere else, in any size, at any moment.
- EXACT COUNT: the capital letter "Q" appears exactly ONCE in the whole clip, inside the equation "Q = i × t", and nowhere else.
- EXACT COUNT: the word "विद्युत्" appears exactly TWICE in total in this clip — once inside the first phrase and once inside the second phrase. Nowhere else.
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol, matra by matra. The Devanagari text must be rendered with correct conjuncts, correct matras and the correct halant in "विद्युत्".
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. In THIS clip every phrase contains a standalone letter or a repeated word, so ALL THREE phrases are COMPLETELY UNIFORM bold white with NO golden word anywhere. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters or mathematical symbols individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters or mathematical symbols are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time. The exact script of this clip is:
"अब कूलम्ब में विद्युत् की मात्रा— जहाँ i है विद्युत् धारा की तीव्रता और t है धारा के प्रवाहित होने का समय।"
Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean crisp flat overlay typography on a dark technical background. Never photorealistic. NO fire, NO flame, NO sparks, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: continuing exactly from the previous clip — the equation "W ∝ Q" sits alone on one single line below where the script text will appear, sharp and still, all its symbols plain white. Nothing else.

ANIMATION TIMELINE:
0.0 s — "W ∝ Q" is already on screen, alone, white and still. It does not fade in again.
0.0–3.3 s — phrase 1 "अब कूलम्ब में विद्युत् की मात्रा—" pops in at the top of the frame, fully sharp, uniform bold white.
1.5 s — "W ∝ Q" becomes completely invisible, and only after it is fully gone the line "Q = i × t" pops in at exactly the same place, on one single line, large bold white, sharp from its first visible frame. From here to the end this is the only equation on screen.
3.3 s — phrase 1 disappears completely. 0.2 second gap with no phrase.
3.5–6.6 s — phrase 2 "जहाँ i है विद्युत् धारा की तीव्रता" pops in, uniform bold white.
3.9 s — exactly as the letter i is visible inside the written phrase on screen, the letter i inside the EXISTING equation turns bright yellow and glows, staying exactly in its place inside the equation.
6.6 s — phrase 2 disappears completely. 0.2 second gap with no phrase.
6.8–10.0 s — phrase 3 "और t है धारा के प्रवाहित होने का समय।" pops in, uniform bold white, and holds to 10.0 s.
7.2 s — the letter i inside the equation returns to white, and at the same moment the letter t inside the EXISTING equation turns bright yellow and glows in place, holding that glow to the end.
10.0 s — the clip ends with "Q = i × t" on screen and the third phrase above it.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "अब कूलम्ब में विद्युत् की मात्रा—"
2. "जहाँ i है विद्युत् धारा की तीव्रता"
3. "और t है धारा के प्रवाहित होने का समय।"
4. "W ∝ Q"
5. "Q = i × t"
Nothing else is written anywhere on screen at any moment.

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, broken or misplaced Devanagari matras, a missing or misplaced halant, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, curly quotation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, invented labels, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, any voiceover, any narration, any spoken words, any human voice, any singing, background music, sound effects, an automatic caption, an auto-generated subtitle, a burnt-in subtitle bar, closed captions, a transcript line, any text that appears because speech was generated, any beaker, glass vessel, liquid, electrode, metal plate, battery, wire, ammeter, ion, bubble, arrow, shape, icon or illustration of any kind, any label plate, any chip, any callout, any leader line, a copy of any symbol taken out of the equation, a floating letter i anywhere outside the equation, a floating letter t anywhere outside the equation, a floating letter Q anywhere outside the equation, two equation lines visible at the same time, "W ∝ Q" and "Q = i × t" on screen together, two copies of the equation, the equation moving or resizing, the equation stacked onto two lines, a golden word in any phrase, the proportionality sign drawn as the Greek letter alpha, the proportionality sign drawn as an infinity sign, the proportionality sign drawn as an equals sign, a capital letter I in place of the lowercase i, the letter A in place of i, the equation written as "Q = t × i", the equation written as "Q = i / t", the constant Z appearing in this clip, the letter Z anywhere, any number, any digit, any unit, the value 96500, the letter F, the Faraday constant, wrong mathematical symbols, extra equations
```

---

```
VIDEO PROMPT — SEGMENT 10 OF 24

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

AUDIO: this clip is completely SILENT. There is no voiceover, no narration, no speech, no singing, no music, no sound effects and no ambient sound of any kind. No voice is generated at any moment. The audio track is empty. The spoken narration is added separately in editing from a different source.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, starting close to the top edge. The equation sits directly below the script text, comfortably above the invisible middle line, and is large enough that the top half does not look empty. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

NO DIAGRAM IN THIS CLIP (CRITICAL): this clip contains NO three dimensional object of any kind. There is no beaker, no glass vessel, no liquid, no electrode, no metal plate, no battery, no wire, no ammeter, no ion, no bubble, no arrow, no icon and no illustration anywhere in the frame at any moment. The only things on screen are the script text, the equation, and the plain background. Do not invent, add or imagine any diagram, object or graphic. The space below the equation stays as plain empty background.

EQUATION RULE (CRITICAL): only ONE equation line is visible at any single moment in this clip. At the very first frame the line "Q = i × t" is already on screen, alone, on one single line below where the script text appears. It is replaced twice, always the same way: the line on screen becomes completely invisible first, then the new line appears in exactly the same place with a clean pop. First "Q = i × t" is replaced by "W ∝ i × t", then "W ∝ i × t" is replaced by "W = Z i t". Two equation lines are NEVER on screen together, never stacked, never crossfaded, never shown side by side. The equation is flat two dimensional overlay text, not a three dimensional object. It is ONE single clean horizontal line of large bold white mathematical text, perfectly sharp, centred below the script text, with every symbol correct and correctly sized. It is not on a card, not in a box, not in a rounded plate, and never stacked onto two lines. It never moves, never resizes and never leaves its place below the script text.
SYMBOL FORMS (CRITICAL — EXACT GLYPHS): the sign "∝" is the mathematical proportionality sign, a small curled open glyph. It is NOT the Greek letter alpha, NOT the infinity sign, NOT the letter a and NOT an equals sign. The letter "i" is lowercase italic i — never capital I, never the letter A. "W" and "Z" are capital letters; the Z is clearly the letter Z with flat top and bottom strokes and never looks like the digit 2. In "W = Z i t" the symbols stand side by side with normal spacing and NO multiplication dots and NO cross signs between Z, i and t, and Z always comes first, immediately after the equals sign. The multiplication sign in "W ∝ i × t" is a small centred cross.

BUILD ORDER RULE (CRITICAL): the constant Z does not exist anywhere on screen before 6.8 seconds. It appears for the first time only in the final line "W = Z i t". It is never pre-placed, never previewed, never faded in early and never visible next to the earlier lines.

HIGHLIGHT RULE (CRITICAL — NO NEW TEXT IS EVER CREATED): when a part of the equation is emphasised, that part of the EXISTING equation simply changes colour and glows brighter in place. NEVER copy a symbol out of the equation. NEVER draw a second copy of any symbol anywhere. NEVER create a label, plate, chip, callout or floating letter for it. The equation itself is the only place any symbol ever appears.

SAME ELEMENT RULE (CRITICAL): the element that is highlighted and the element that changes are THE SAME SINGLE element — not a neighbour, not a different one, not an additional one. In the final line "W = Z i t", counting from the left-hand end, the highlighted element is symbol number 3, the letter Z, and it is the only symbol in the whole clip that changes colour. Every other symbol in that line keeps its plain white colour, size and position from the moment the line appears to the last frame, without exception. The change happens in place, on the same symbol that already carries the highlight, while the highlight is still visible on it.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE. Every word appears exactly the number of times it is written.
- EXACT COUNT: the capital letter "Z" appears exactly TWICE in total in this clip — once inside the third phrase and once inside the equation line "W = Z i t". Nowhere else, in any size, at any moment.
- EXACT COUNT: at any single moment there is exactly ONE equation line on screen and never two. The letters i and t are each visible exactly once at any moment, inside whichever equation line is currently on screen, and nowhere else.
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol, matra by matra. The Devanagari text must be rendered with correct conjuncts, correct matras and the correct halant in "विद्युत्-रासायनिक".
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. In THIS clip ALL THREE phrases are COMPLETELY UNIFORM bold white with NO golden word anywhere — the third phrase contains a standalone letter and a hyphenated word, and the first two are too short for any highlight. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated beyond the hyphen already written in "विद्युत्-रासायनिक".

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters or mathematical symbols individually. NEVER morph one phrase into another and NEVER morph one equation line into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters or mathematical symbols are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear, and the outgoing equation line must be completely invisible before the incoming equation line begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time. The exact script of this clip is:
"इसलिए— और समानुपात हटाने पर— यहाँ Z है विद्युत्-रासायनिक तुल्यांक।"
Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean crisp flat overlay typography on a dark technical background. Never photorealistic. NO fire, NO flame, NO sparks, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: continuing exactly from the previous clip — the equation "Q = i × t" sits alone on one single line below where the script text will appear, sharp and still, all its symbols plain white. Nothing else.

ANIMATION TIMELINE:
0.0 s — "Q = i × t" is already on screen, alone, white and still. It does not fade in again.
0.0–3.3 s — phrase 1 "इसलिए—" pops in at the top of the frame, fully sharp, uniform bold white.
1.5 s — "Q = i × t" becomes completely invisible, and only after it is fully gone the line "W ∝ i × t" pops in at exactly the same place, on one single line, large bold white, sharp from its first visible frame.
3.3 s — phrase 1 disappears completely. 0.2 second gap with no phrase.
3.5–6.6 s — phrase 2 "और समानुपात हटाने पर—" pops in, uniform bold white.
5.0 s — "W ∝ i × t" becomes completely invisible, and only after it is fully gone the line "W = Z i t" pops in at exactly the same place, on one single line, large bold white, sharp from its first visible frame. This is the final line and it holds to 10.0 s.
6.6 s — phrase 2 disappears completely. 0.2 second gap with no phrase.
6.8–10.0 s — phrase 3 "यहाँ Z है विद्युत्-रासायनिक तुल्यांक।" pops in, uniform bold white, and holds to 10.0 s.
7.2 s — exactly as the letter Z is visible inside the written phrase on screen, the letter Z inside the EXISTING equation line "W = Z i t" turns bright yellow and glows, staying exactly in its place inside that line, and holds that glow to the end. No other symbol changes.
10.0 s — the clip ends with "W = Z i t" on screen, its Z glowing yellow, and the third phrase above it.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "इसलिए—"
2. "और समानुपात हटाने पर—"
3. "यहाँ Z है विद्युत्-रासायनिक तुल्यांक।"
4. "Q = i × t"
5. "W ∝ i × t"
6. "W = Z i t"
Nothing else is written anywhere on screen at any moment.

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, broken or misplaced Devanagari matras, a missing or misplaced halant, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, curly quotation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, invented labels, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, any voiceover, any narration, any spoken words, any human voice, any singing, background music, sound effects, an automatic caption, an auto-generated subtitle, a burnt-in subtitle bar, closed captions, a transcript line, any text that appears because speech was generated, any beaker, glass vessel, liquid, electrode, metal plate, battery, wire, ammeter, ion, bubble, arrow, shape, icon or illustration of any kind, any label plate, any chip, any callout, any leader line, a copy of any symbol taken out of the equation, a floating letter Z anywhere outside the equation and outside the third phrase, a floating letter W, i or t anywhere outside the equation, two equation lines visible at the same time, "Q = i × t" and "W ∝ i × t" on screen together, "W ∝ i × t" and "W = Z i t" on screen together, a stack of equations, two copies of the equation, the equation moving or resizing, the equation stacked onto two lines, one equation line morphing into the next, a golden word in any phrase, the letter Z appearing before 6.8 seconds, the letter Z appearing in "W ∝ i × t", the letter Z drawn as the digit 2, a capital letter I in place of the lowercase i, the letter A in place of i, the proportionality sign drawn as the Greek letter alpha, the proportionality sign drawn as an infinity sign, the proportionality sign drawn as an equals sign, an equals sign in place of the proportionality sign in "W ∝ i × t", multiplication dots or cross signs between Z, i and t, the final line written as "W = i Z t", any number, any digit, any unit, the value 96500, the letter F, the Faraday constant, wrong mathematical symbols, extra equations
```

---

```
VIDEO PROMPT — SEGMENT 11 OF 24

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

AUDIO: this clip is completely SILENT. There is no voiceover, no narration, no speech, no singing, no music, no sound effects and no ambient sound of any kind. No voice is generated at any moment. The audio track is empty. The spoken narration is added separately in editing from a different source.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, starting close to the top edge. The equation sits directly below the script text, comfortably above the invisible middle line, and is large enough that the top half does not look empty. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

NO DIAGRAM IN THIS CLIP (CRITICAL): this clip contains NO three dimensional object of any kind. There is no beaker, no glass vessel, no liquid, no electrode, no metal plate, no battery, no wire, no ammeter, no ion, no bubble, no arrow, no icon and no illustration anywhere in the frame at any moment. The only things on screen are the script text, the equation, and the plain background. Do not invent, add or imagine any diagram, object or graphic. The space below the equation stays as plain empty background.

EQUATION RULE (CRITICAL): there is only ONE equation in this clip and it is already on screen at the very first frame: "W = Z i t". It is flat two dimensional overlay text, not a three dimensional object. It never moves, never resizes, never duplicates and never leaves its place below the script text. It is ONE single clean horizontal line of large bold white mathematical text, perfectly sharp, with every symbol correct. Not on a card, not in a box, never stacked onto two lines. Its letter Z is glowing yellow at the first frame, exactly as the previous clip left it. The equation fades away smoothly and completely between 8.5 and 10.0 seconds and no other equation ever replaces it.
SYMBOL FORMS (CRITICAL — EXACT GLYPHS): "W" and "Z" are capital letters; the Z is clearly the letter Z with flat top and bottom strokes and never looks like the digit 2. The letter "i" is lowercase italic i — never capital I, never the letter A. The letter "t" is lowercase t. The symbols stand side by side with normal spacing and NO multiplication dots and NO cross signs between Z, i and t, and Z comes first, immediately after the equals sign.

HIGHLIGHT RULE (CRITICAL — NO NEW TEXT IS EVER CREATED): when a part of the equation is emphasised, that part of the EXISTING equation simply changes colour and glows brighter in place. NEVER copy a symbol out of the equation. NEVER draw a second copy of any symbol anywhere. NEVER create a label, plate, chip, callout or floating letter for it. The equation itself is the only place any symbol ever appears.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE beyond what is written. Every word appears exactly the number of times it is written.
- EXACT COUNT: the word "नियम" appears exactly TWICE in total in this clip — once inside the first phrase and once inside the second phrase. Never a third time, in any size, at any moment.
- EXACT COUNT: the word "याद" appears exactly TWICE in total in this clip — once inside the first phrase and once inside the second phrase. Never a third time.
- EXACT COUNT: the letters "W", "Z", "i" and "t" each appear exactly ONCE in the whole clip, inside the single equation "W = Z i t", and nowhere else.
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol, matra by matra. The Devanagari text must be rendered with correct conjuncts and correct matras.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. In THIS clip the word "नियम" and the word "याद" each appear in both phrases, so BOTH phrases are COMPLETELY UNIFORM bold white with NO golden word anywhere. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters or mathematical symbols individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters or mathematical symbols are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time. The exact script of this clip is:
"तो बच्चों, जैसे फैराडे का पहला नियम याद किया, वैसे ही दूसरा नियम भी इसी तरह याद कर लो।"
Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean crisp flat overlay typography on a dark technical background. Never photorealistic. NO fire, NO flame, NO sparks, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: continuing exactly from the previous clip — the equation "W = Z i t" sits alone on one single line below where the script text will appear, sharp and still, its letter Z glowing bright yellow and every other symbol plain white. Nothing else.

ANIMATION TIMELINE:
0.0 s — "W = Z i t" is already on screen, alone, with the letter Z glowing yellow. It does not fade in again and it does not move.
0.0–4.8 s — phrase 1 "तो बच्चों, जैसे फैराडे का पहला नियम याद किया," pops in at the top of the frame, fully sharp, uniform bold white.
1.8 s — the letter Z inside the EXISTING equation returns to plain white, in place. No other change happens to the equation.
4.8 s — phrase 1 disappears completely. 0.2 second gap with no phrase.
5.0–8.3 s — phrase 2 "वैसे ही दूसरा नियम भी इसी तरह याद कर लो।" pops in, uniform bold white.
8.3 s — phrase 2 disappears completely.
8.5–10.0 s — the equation "W = Z i t" fades away smoothly and completely, without moving, without shrinking and without being replaced.
10.0 s — the frame is completely empty except for the unchanged background.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "तो बच्चों, जैसे फैराडे का पहला नियम याद किया,"
2. "वैसे ही दूसरा नियम भी इसी तरह याद कर लो।"
3. "W = Z i t"
Nothing else is written anywhere on screen at any moment.

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, broken or misplaced Devanagari matras, a missing or misplaced halant, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, curly quotation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, "नियम" appearing three times, "याद" appearing three times, a repeated key word, a keyword written as a separate line, invented labels, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, any voiceover, any narration, any spoken words, any human voice, any singing, background music, sound effects, an automatic caption, an auto-generated subtitle, a burnt-in subtitle bar, closed captions, a transcript line, any text that appears because speech was generated, any beaker, glass vessel, liquid, electrode, metal plate, battery, wire, ammeter, ion, bubble, arrow, shape, icon or illustration of any kind, any label plate, any chip, any callout, any leader line, a copy of any symbol taken out of the equation, a floating letter W, Z, i or t anywhere outside the equation, a second equation, a new equation appearing after the first fades, two copies of the equation, the equation moving or resizing, the equation stacked onto two lines, a golden word in either phrase, the letter Z drawn as the digit 2, a capital letter I in place of the lowercase i, multiplication dots or cross signs between Z, i and t, the line written as "W = i Z t", any proportionality sign in this clip, any number, any digit, any unit, the value 96500, the letter F, the Faraday constant, subscripts on W or E, wrong mathematical symbols, extra equations
```

---

```
VIDEO PROMPT — SEGMENT 12 OF 24

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

AUDIO: this clip is completely SILENT. There is no voiceover, no narration, no speech, no singing, no music, no sound effects and no ambient sound of any kind. No voice is generated at any moment. The audio track is empty. The spoken narration is added separately in editing from a different source.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, starting close to the top edge. The diagram sits directly below the script text and fills the space between the text and the invisible middle line, so the top half never looks empty. The lowest part of the diagram stops with a clear visible gap above the invisible middle line and never touches it; if it does not fit, make it smaller. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

SIZE AND POSITION CHECK (CRITICAL): before anything is drawn, the diagram is scaled so that its complete height — including every wire, arrow, glow and shadow — fits inside the upper half of the frame with a clear visible margin still left below it. If any part of the diagram would reach the middle of the frame, the whole diagram is made smaller until it does not. The diagram never grows, drifts downward, expands or scales up at any moment during the clip. The lower half of the frame contains nothing but the background from the first frame to the last.

3D RENDER QUALITY (CRITICAL — THIS MAKES THE DIAGRAM LOOK THREE DIMENSIONAL):
The diagram is a real three dimensional object rendered in depth, not a flat drawing.
- CAMERA: a fixed three-quarter view from slightly above the objects, so the viewer looks slightly down at them and can clearly read their roundness. Never a flat straight-on front view.
- PERSPECTIVE: the circular rims and bases of the vessels appear as flattened ellipses because of the viewing angle. Nothing is drawn as a plain flat circle.
- DEPTH: the parts nearest the camera are brighter, thicker and sharper. The parts on the far side, seen through the transparent glass and liquid, are noticeably dimmer, thinner and softer. This difference is clear and obvious.
- LIGHTING: one soft cool rim light along the upper left edge and a gentle ambient fill, giving a rounded sculpted look with a soft falloff toward the lower right.
- MATERIAL: smooth glossy glass-like vessels with a faint specular highlight near the upper left and a soft inner glow; the electrodes are matte brushed metal.
- FORESHORTENING: any arrow pointing toward the camera looks shorter and thicker with a larger arrowhead, and any arrow pointing away looks longer and thinner. They are never all the same length on screen.
- MOTION: the whole assembly is completely still except for the slow steady drift of the ions inside the liquids and a gentle pulse along the current arrows. Nothing wobbles, squashes, deforms or changes size once settled.

DIAGRAM SPECIFICATION (build exactly this, nothing else):
- THE TWO CELLS: exactly TWO glass beakers standing side by side at the same height and the same size, each rendered in full three dimensions with an elliptical rim and a visible rounded base. The left beaker is filled a little more than half with a translucent pale cyan-blue electrolyte; the right beaker is filled to the same level with a translucent pale amber-green electrolyte, so the two liquids are clearly different from each other. The liquid surface in each beaker is a flattened ellipse with a soft specular highlight on the upper left. Nothing floats on top and no liquid ever spills.
- THE ELECTRODES: exactly TWO flat vertical metal plates dipped into each beaker, four plates in total. In each beaker the two plates hang from above, are clearly separated from each other, do not touch each other, and stop with a clear gap above the bottom of the beaker. The plates are matte grey brushed metal with a soft rim light on the upper left. In each beaker, the left plate is connected toward the negative side of the circuit and the right plate toward the positive side.
- THE BATTERY AND THE SERIES WIRING: exactly ONE battery, drawn as the standard cell symbol — one long thin line for the positive terminal and one short thick line for the negative terminal, side by side. There is exactly ONE closed continuous loop of thin bright wire: it leaves the positive terminal, runs to an electrode of the right-hand beaker, comes out of that beaker's other electrode, runs across to an electrode of the left-hand beaker, comes out of that beaker's other electrode, and returns to the negative terminal. The wire is unbroken everywhere, with no gap, no break, no open end and no switch. The two beakers are wired one after the other in the same single loop, never on two separate loops and never on two separate batteries.
- THE CURRENT ARROWS IN THE WIRE: small neat bright cyan arrowheads spaced along the wire, all pointing the same way around the loop, running out of the long thin positive line, through both beakers in turn, and back to the short thick negative line. Because the current is the same everywhere in the loop, the arrows are identical in size and identical in brightness in every part of the loop, including both beakers.
- THE IONS IN EACH LIQUID: inside each beaker a few small glowing spheres drift slowly. In each beaker the positive ions drift toward the plate connected to the negative side and the negative ions drift in the OPPOSITE direction, toward the plate connected to the positive side. The two kinds of ions in one beaker always move in opposite directions, never the same way. The positive ions are warm orange-red and the negative ions are cool cyan-blue.
- LABELS: this clip has NO labels at all. No plate, no chip, no tag, no letter, no number, no leader line. Never invent a label.

DIAGRAM TIMING SYNC (CRITICAL): every object appears at the exact moment its name is visible in the written phrase on screen, and never a frame before. Once an object appears it stays to the end of the clip, unchanged in size and position.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE beyond what is written. Every word appears exactly the number of times it is written.
- EXACT COUNT: in the second phrase the word "अलग" is written twice as the single hyphenated word "अलग-अलग" — exactly two occurrences joined by one hyphen, never three, never a separate loose "अलग" anywhere else in the clip.
- EXACT COUNT: the word "विद्युत्" appears exactly TWICE in total in this clip — once inside the second phrase, as the first part of "विद्युत्-अपघट्यों", and once inside the third phrase. Nowhere else, in any size, at any moment.
- EXACT COUNT: the word "नियम" appears exactly ONCE in this clip, inside the first phrase, and nowhere else.
- This clip has NO label plates and NO equation at all. No plate, no chip, no floating letter, no leader line, no stray symbol, no mathematical text.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, matra by matra. The Devanagari text must be rendered with correct conjuncts, correct matras and the correct halant in "विद्युत्".
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. In THIS clip ALL THREE phrases are COMPLETELY UNIFORM bold white with NO golden word anywhere — the second phrase contains the doubled hyphenated word and the word "विद्युत्" appears in two phrases. A hyphenated word is NEVER golden and is never coloured differently from the rest of its phrase. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated beyond the hyphens already written.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time. The exact script of this clip is:
"तो दूसरा नियम कहता है कि जब अलग-अलग विद्युत्-अपघट्यों में समान मात्रा में विद्युत् प्रवाहित की जाती है,"
Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean, glossy, textbook-style physics illustration rendered in three dimensions — smooth shapes, flat bright colours, soft even glow, like a modern NCERT diagram built in 3D. Never photorealistic. NO fire, NO flame, NO burning, NO spark, NO ember, NO explosion, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: completely empty background. Nothing at all.

ANIMATION TIMELINE:
0.0–3.3 s — phrase 1 "तो दूसरा नियम कहता है कि" pops in at the top of the frame, fully sharp, uniform bold white. Below it the frame stays empty background.
3.3 s — phrase 1 disappears completely. 0.2 second gap with no phrase.
3.5–6.6 s — phrase 2 "जब अलग-अलग विद्युत्-अपघट्यों में" pops in, uniform bold white.
4.2 s — exactly as the words "अलग-अलग विद्युत्-अपघट्यों" are visible in the written phrase on screen, the TWO glass beakers with their two different-coloured electrolytes, their four metal electrodes and their drifting ions pop into view together, sitting below the script text, already scaled to fit inside the upper half of the frame. They never move or grow after this.
6.6 s — phrase 2 disappears completely. 0.2 second gap with no phrase.
6.8–10.0 s — phrase 3 "समान मात्रा में विद्युत् प्रवाहित की जाती है," pops in, uniform bold white, and holds to 10.0 s.
7.4 s — exactly as the word "विद्युत्" is visible in the written phrase on screen, the single battery and the single closed loop of wire appear, joining both beakers one after the other, and the identical cyan current arrows begin to pulse slowly around the whole loop. The circuit is closed and unbroken from this moment to the end.
10.0 s — the clip ends with the complete two-cell series circuit on screen, entirely inside the upper half of the frame, and the third phrase above it.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "तो दूसरा नियम कहता है कि"
2. "जब अलग-अलग विद्युत्-अपघट्यों में"
3. "समान मात्रा में विद्युत् प्रवाहित की जाती है,"
Nothing else is written anywhere on screen at any moment — no labels, no equation, no numbers, no units.

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, the diagram crossing the middle of the frame, the diagram touching the middle of the frame, the diagram growing or expanding during the clip, the diagram drifting downward, an arrow or wire reaching into the lower half, the illustration filling the whole frame, a full-frame poster layout, two phrases visible at the same time, garbled letters during a transition, broken or misplaced Devanagari matras, a missing or misplaced halant, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, curly quotation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, "अलग" written three times, a loose separate "अलग" outside the hyphenated word, "विद्युत्" appearing a third time, a repeated key word, a keyword written as a separate line, a golden word in any phrase, a coloured or highlighted hyphenated word, invented labels, any label plate, any chip, any tag, any callout, any leader line, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, any voiceover, any narration, any spoken words, any human voice, any singing, background music, sound effects, an automatic caption, an auto-generated subtitle, a burnt-in subtitle bar, closed captions, a transcript line, any text that appears because speech was generated, a flat two dimensional drawing instead of a three dimensional scene, a straight-on front view with no depth, arrows all drawn the same length on screen, a diagram that looks like a flat line drawing, a wobbling or deforming beaker, a galvanic cell, a voltaic cell, a salt bridge, an electrode marked as a negative anode, the two beakers wired in parallel, two separate loops, two batteries, a second battery, three or more beakers, only one beaker, a broken wire, an open gap in the circuit, an open switch, any switch, a bulb, an alternating current source, a wavy alternating current symbol, both kinds of ions in one beaker drifting the same way, current arrows brighter in one beaker than in the other, current arrows of different sizes in the two beakers, arrows pointing in opposite directions in the two halves of the wire loop, electrodes touching each other, electrodes touching the bottom of the beaker, liquid spilling, the two electrolytes drawn in the same colour, any equation, any mathematical symbol, any proportionality sign, the letters W, Q, i, t, Z or E anywhere, any subscript, any number, any digit, any unit, the value 96500, the letter F, the Faraday constant, an ammeter dial with a printed number
```

**Continuity handshake:** Seg 12 ends with the two-cell series circuit complete and unlabelled — which is exactly what Seg 13's `SCREEN AT START` must carry over before it shrinks and fades by 4.0 s.