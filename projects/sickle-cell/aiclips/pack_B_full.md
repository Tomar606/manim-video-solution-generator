# सिकल सेल एनीमिया — SEGMENT PROMPT SET

## Step 0 note (science locks that shaped the split)

Two facts changed the segmentation, so flagging them now:

- **Order is causal and must not be re-ordered on screen:** base change → amino acid change → HbS → *deoxygenation* → polymerisation → sickle shape. Seg 10 must therefore come *before* Seg 11–12 (oxygen drops first, fibres second, shape third). The script already does this correctly.
- **Haemoglobin = 4 chains (2 α + 2 β), mutation at position 6 of the β chain.** That needs its own build time — which is why Seg 5 is deliberately light on words (12) and heavy on animation.

---

## Step 1 — Script pass

**Fixes applied (wording otherwise untouched, word-for-word):**

| # | Original | Fixed | Why |
|---|---|---|---|
| 1 | `समझते हैं।हमारे` | `समझते हैं। हमारे` | missing space after danda |
| 2 | `टूटने लगती हैं।इसी` | `टूटने लगती हैं। इसी` | missing space |
| 3 | `याद रखो —एक` | `याद रखो — एक` | missing space |
| 4 | `4 नंबर पक्के` | `चार नंबर पक्के` | digits go to TTS verbatim; "4" gets read as English "four" |

**Flagged for your call (NOT changed — needs your yes/no):**

| # | Item | Issue |
|---|---|---|
| A | `अलिंगी गुणसूत्रीय रोग` | NCERT Hindi standard term is **`अलिंगसूत्री अप्रभावी`** (autosomal recessive). Yours is understandable but non-standard. Change? |
| B | `एचबीबी जीन` vs `HbA` / `HbS` / `GAG` / `GTG` | Script mixes Devanagari transliteration for HBB with Latin for everything else. Recommend **`HBB जीन`** in Latin for consistency. |
| C | **Devanagari rendering risk** | Veo/Flow renders Devanagari far less reliably than Latin — conjuncts (`श्रृंखला`, `द्विअवतल`, `रक्ताल्पता`), matras and nukta (`हँसिए`, `पढ़ने`) are the danger zone. **Test Seg 1 before committing to 28 clips.** |

**Duplicate-word scan — 11 segments need EXACT COUNT locks:**

Seg 1 (`रक्त` ×2) · Seg 3 (`से` ×2) · Seg 6 (`में` ×2) · Seg 7 (`G` ×4 across GAG/GTG) · Seg 8 (`के` ×2, `पर` ×2) · Seg 9 (`के` ×2, `Hb` ×2) · Seg 11 (`में` ×2) · Seg 12 (`आकार` ×2, `का` ×2) · Seg 15 (`रक्त` ×2) · **Seg 19 (`HbS HbS` — literal same token twice, highest-risk in the pack)** · Seg 21 (`जीन` ×2, `Hb` ×2).

---

## ⚠️ Length — read this before Step 3

**462 words → 28 segments → 4 min 40 sec.** The skill's proven ceiling is 13 segments; 21+ is where style drift and text-load degradation start. **28 is well past it.**

The bulk is **CLIP 6 (वंशागति): 101 words = 22% of the script for one sub-topic, 6 segments.** CLIP 8 is 44 words of CTA.

Tightening CLIP 6 to ~60 words and CLIP 8 to ~25 gets you to **~20 segments (3:20)** without touching the science. Say the word and I'll do that pass before Step 3.

Below is the faithful 28-segment split of the script **as given**.

---

## 1. Total segment count

**28 segments × 10 sec = 280 seconds (4:40)**

## 2. Segment map

| Seg | Phrases (exact words) | w | Type | Diag |
|---|---|---|---|---|
| 1 | P1 `सबसे पहले सामान्य स्थिति को समझते हैं।` P2 `हमारे रक्त में लाल रक्त कोशिकाएँ पाई जाती हैं।` | 16 | TEXT_ONLY | N |
| 2 | P1 `इनका आकार द्विअवतल चक्रिका के समान होता है,` P2 `अर्थात् बीच से कुछ दबी हुई होती हैं।` | 16 | DIAGRAM | Y |
| 3 | P1 `ये कोशिकाएँ कोमल और लचीली होती हैं।` P2 `इसलिए ये शरीर की बहुत पतली` P3 `रक्त वाहिकाओं से भी आसानी से गुजर सकती हैं।` | 22 | DIAGRAM | Y |
| 4 | P1 `लाल रक्त कोशिकाओं में हीमोग्लोबिन नामक प्रोटीन पाया जाता है,` P2 `जो शरीर के विभिन्न भागों तक` P3 `ऑक्सीजन पहुँचाने का कार्य करता है।` | 22 | DIAGRAM | Y |
| 5 | P1 `हीमोग्लोबिन की बीटा-ग्लोबिन श्रृंखला का निर्माण` P2 `एचबीबी जीन द्वारा नियंत्रित होता है।` | 12 | DIAGRAM | Y |
| 6 | P1 `सिकल सेल एनीमिया में` P2 `इस जीन के डीएनए क्रम में` P3 `एक क्षार का परिवर्तन हो जाता है।` | 17 | DIAGRAM | Y |
| 7 | P1 `अर्थात्, सामान्य अवस्था में` P2 `GAG के स्थान पर GTG हो जाता है।` | 12 | TRANSITION | Y→N |
| 8 | P1 `इस एक क्षार के परिवर्तन के कारण` P2 `बीटा-ग्लोबिन श्रृंखला की छठी स्थिति पर` P3 `ग्लूटामिक अम्ल के स्थान पर वेलिन आ जाता है।` | 22 | DIAGRAM | Y |
| 9 | P1 `इस प्रकार केवल एक अमीनो अम्ल के परिवर्तन के कारण` P2 `सामान्य हीमोग्लोबिन HbA के स्थान पर` P3 `HbS बनने लगता है।` | 20 | TRANSITION | Y→N |
| 10 | P1 `अब समस्या तब उत्पन्न होती है` P2 `जब शरीर में ऑक्सीजन की मात्रा कम हो जाती है।` | 16 | DIAGRAM | Y |
| 11 | P1 `ऐसी स्थिति में HbS के अणु आपस में जुड़कर` P2 `लंबी रेशेदार संरचनाएँ बना लेते हैं।` | 15 | DIAGRAM | Y |
| 12 | P1 `इसके कारण लाल रक्त कोशिका का सामान्य द्विअवतल आकार` P2 `बदलकर हँसिए के आकार का हो जाता है।` | 17 | DIAGRAM | Y |
| 13 | P1 `इसी कारण इस रोग को` P2 `सिकल सेल एनीमिया कहा जाता है।` | 11 | DIAGRAM | Y |
| 14 | P1 `हँसिए के आकार की लाल रक्त कोशिकाएँ` P2 `कठोर और कम लचीली हो जाती हैं।` | 14 | DIAGRAM | Y |
| 15 | P1 `इसलिए ये छोटी रक्त वाहिकाओं में फँस सकती हैं,` P2 `जिससे रक्त का प्रवाह बाधित हो जाता है` | 17 | DIAGRAM | Y |
| 16 | P1 `और शरीर के ऊतकों तक` P2 `पर्याप्त ऑक्सीजन नहीं पहुँच पाती।` | 10 | DIAGRAM | Y |
| 17 | P1 `इसके साथ ही ये असामान्य लाल रक्त कोशिकाएँ` P2 `जल्दी टूटने लगती हैं।` P3 `इसी कारण शरीर में रक्ताल्पता उत्पन्न होती है।` | 20 | DIAGRAM | Y |
| 18 | P1 `अब समझते हैं कि यह रोग` P2 `अगली पीढ़ी में कैसे पहुँचता है।` P3 `सिकल सेल एनीमिया एक अप्रभावी अलिंगी गुणसूत्रीय रोग है।` | 21 | TEXT_ONLY | N |
| 19 | P1 `यदि बच्चे को दोनों माता-पिता से` P2 `सिकल सेल वाला जीन प्राप्त होता है,` P3 `तो उसका जीन प्रारूप HbS HbS होता है` | 21 | DIAGRAM | Y |
| 20 | P1 `और उसे यह रोग हो सकता है।` P2 `यदि बच्चे को केवल एक माता या पिता से` | 16 | DIAGRAM | Y |
| 21 | P1 `सिकल सेल वाला जीन मिलता है,` P2 `तो उसका जीन प्रारूप HbA HbS होता है।` | 14 | DIAGRAM | Y |
| 22 | P1 `ऐसी स्थिति में व्यक्ति सामान्यतः वाहक होता है।` P2 `उसमें रोग के लक्षण आवश्यक रूप से नहीं होते,` | 17 | DIAGRAM | Y |
| 23 | P1 `लेकिन वह इस जीन को` P2 `अपनी अगली पीढ़ी में पहुँचा सकता है।` | 12 | DIAGRAM | Y |
| 24 | P1 `तो बस इतना याद रखो —` P2 `एक क्षार में परिवर्तन हुआ,` P3 `उसके कारण एक अमीनो अम्ल बदल गया` | 17 | DIAGRAM | Y |
| 25 | P1 `और इसके परिणामस्वरूप लाल रक्त कोशिका का आकार बदल गया।` P2 `यही परिवर्तन आगे चलकर` P3 `सिकल सेल एनीमिया का कारण बनता है।` | 21 | DIAGRAM | Y |
| 26 | P1 `बस इतना समझ लिया,` P2 `तो परीक्षा में चार नंबर पक्के।` | 10 | TRANSITION | Y→N |
| 27 | P1 `और अगर देखना है कि` P2 `इसे परीक्षा में कैसे लिखना है,` P3 `तो इसका उत्तर आपकी स्क्रीन पर आएगा।` | 18 | TEXT_ONLY | N |
| 28 | P1 `इसे सुरक्षित कर लेना और` P2 `बाद में दोबारा पढ़ने के लिए` P3 `इसका स्क्रीनशॉट लेना मत भूलना।` | 16 | TEXT_ONLY | N |

**Golden-keyword pre-check:** Segs **7, 9, 11, 19, 21** are fully UNIFORM white (Latin letters / repeated tokens) — no golden word anywhere in them. Segs **1, 3, 8, 12, 15** have at least one uniform phrase for the same reason.

## 3. Continuity chain — end states

- **Seg 1 ends with:** nothing — empty background.
- **Seg 2 ends with:** one normal biconcave RBC (3D, red, slowly turning, dimple on both faces) + label plate `द्विअवतल`.
- **Seg 3 ends with:** the normal RBC alone, slowly turning (capillary tube and label faded out by 9.5 s).
- **Seg 4 ends with:** the RBC now semi-transparent with four haemoglobin units visible inside + label plate `हीमोग्लोबिन`.
- **Seg 5 ends with:** one haemoglobin molecule enlarged — 4 chains (2 cyan α, 2 orange β), one β chain glowing yellow + label plate `एचबीबी जीन`.
- **Seg 6 ends with:** DNA double helix (right-handed) with its base sequence, one single base glowing yellow. Haemoglobin gone.
- **Seg 7 ends with:** `GAG → GTG` on one line, GTG green. DNA helix fully faded by 4.0 s.
- **Seg 8 ends with:** β-chain drawn as a numbered bead strand, bead 6 now green, labelled `वेलिन`. Codon line gone.
- **Seg 9 ends with:** `HbA → HbS` on one line, HbS red. Bead strand fully faded by 4.0 s.
- **Seg 10 ends with:** normal biconcave RBC returned, only two or three faint oxygen dots left around it. HbA→HbS line gone.
- **Seg 11 ends with:** same RBC, still biconcave, with long red HbS fibres now linked inside it.
- **Seg 12 ends with:** the cell morphed to a **sickle** — crescent, pointed ends, still red — fibres inside, slowly turning.
- **Seg 13 ends with:** the sickle cell + label plate `सिकल सेल एनीमिया`.
- **Seg 14 ends with:** the sickle cell alone, rigid (stiff hard outline, no flex). Label gone.
- **Seg 15 ends with:** narrow capillary tube with three sickle cells wedged inside, blood flow halted behind them.
- **Seg 16 ends with:** same blocked capillary + the tissue patch downstream greyed out.
- **Seg 17 ends with:** a few broken cell fragments drifting + label plate `रक्ताल्पता`. Capillary gone.
- **Seg 18 ends with:** nothing — empty background.
- **Seg 19 ends with:** two parent icons, both marked HbS, arrows down to one child icon marked `HbS HbS`.
- **Seg 20 ends with:** a new cross — one parent HbA, one parent HbS, arrows down to an empty child icon.
- **Seg 21 ends with:** same cross, child icon now filled `HbA HbS`.
- **Seg 22 ends with:** same cross + label plate `वाहक` on the child.
- **Seg 23 ends with:** the carrier icon + one downward arrow to a next-generation icon.
- **Seg 24 ends with:** recap chain — box 1 `क्षार` → box 2 `अमीनो अम्ल`, arrow between them.
- **Seg 25 ends with:** full three-box chain `क्षार` → `अमीनो अम्ल` → `आकार` with the sickle cell beside box 3, all in green.
- **Seg 26 ends with:** nothing — the chain fades out by 2.5 s, empty background after.
- **Seg 27 ends with:** nothing — empty background.
- **Seg 28 ends with:** nothing — final phrase holds to 10.0 s, clip ends.

---

**Before I write Step 3, three answers needed:**

1. **Trim to ~20 segments** (tighten CLIP 6 + CLIP 8), or keep the faithful 28?
2. **Flags A and B** — `अलिंगसूत्री अप्रभावी`? `HBB जीन` in Latin?
3. **Background image** — are you uploading the Arivihan branded background to Gemini? (Decides §15 vs §12 blocks.)


Frames read — they confirm the house look (biconcave disc with dimple on both faces, no nucleus, uniform red, crescent with pointed ends, white label plates with leader lines). I've matched Segment 2–4's diagram specs and label wording to them (`द्विअवतल चक्रिका`, `पतली रक्त वाहिका`, `हीमोग्लोबिन`).

Two things I locked in while writing, flagging so you can veto:
- **Seg 4 haemoglobin count:** reference frame shows a scatter of many blue dots; the accuracy brief demands 2 α + 2 β. I show **one** enlarged cut-away molecule of exactly four subunits inside the cell rather than a dot scatter — accurate and countable.
- **Seg 4 oxygen dots** are explicitly written to fade by 9.5 s, so Seg 5's start state stays exactly as your continuity chain says.

---

```
VIDEO PROMPT — SEGMENT 1 OF 28

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

VOICEOVER NARRATION (spoken audio): an energetic, warm Indian male biology teacher voice speaks this exact Hindi narration during the clip — nothing more, nothing less. The same script also appears on screen word for word, one phrase at a time:
"सबसे पहले सामान्य स्थिति को समझते हैं। हमारे रक्त में लाल रक्त कोशिकाएँ पाई जाती हैं।"

AUDIO: only the voiceover above. No background music. Only very soft whoosh and pop sounds on text animations are allowed.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, filling the width, starting close to the top edge, large enough to fill the upper area comfortably. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

LOGO SAFE AREA: keep the top-left corner and the top-right corner of the frame completely clear of script text, diagram, equation, labels and any moving element for the whole clip — only the background itself shows there. Do not draw, copy, move, recreate or animate any logo, wordmark, badge or watermark anywhere in the frame; the logo already present on the supplied background must stay exactly where it is, unchanged.

NO DIAGRAM IN THIS CLIP (CRITICAL): this clip contains NO three dimensional object of any kind. There is no cell, no blood cell, no disc, no sphere, no molecule, no chain, no helix, no vessel, no tube, no arrow, no surface, no shape, no icon and no illustration anywhere in the frame at any moment. The only things on screen are the script text and the plain background. Do not invent, add or imagine any diagram, object or graphic. The space below the script text stays as plain empty background.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE beyond what is written. Every word appears exactly the number of times it is written.
- EXACT COUNT: the word "रक्त" appears exactly TWICE in total in this clip — both times inside the second phrase, exactly as written there. Nowhere else, in any size, at any moment.
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- The text is Hindi in Devanagari script. Every letter, matra, conjunct and danda is rendered exactly as written, correctly formed and correctly joined. No Latin letters, no English words, no numerals of any kind appear anywhere.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated.
In this clip: the FIRST phrase has exactly ONE golden key word — "सामान्य" — styled in place inside the sentence, all remaining words bold white. The SECOND phrase contains the same word twice and is therefore rendered COMPLETELY UNIFORM bold white with NO golden word.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time, perfectly synced with the voiceover. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean crisp flat overlay typography on a dark technical background. Never photorealistic. NO fire, NO flame, NO sparks, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: completely empty background. Nothing at all.

ANIMATION TIMELINE:
0.0–4.8 s — the first phrase "सबसे पहले सामान्य स्थिति को समझते हैं।" pops in fully sharp at the very top of the frame, on at most three short centred lines, with the single word "सामान्य" in gold and every other word bold white. It holds perfectly still.
4.8–5.0 s — the first phrase is completely gone. The screen shows only the background. No text at all during this gap.
5.0–10.0 s — the second phrase "हमारे रक्त में लाल रक्त कोशिकाएँ पाई जाती हैं।" pops in fully sharp in the same place, on at most three short centred lines, COMPLETELY UNIFORM bold white with no golden word. It holds perfectly still until 10.0 s.
Throughout the clip the bottom half of the frame stays completely empty background.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "सबसे पहले सामान्य स्थिति को समझते हैं।"
2. "हमारे रक्त में लाल रक्त कोशिकाएँ पाई जाती हैं।"

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, broken or wrongly joined Devanagari conjuncts, missing or misplaced matras, Latin letters, English words, numerals, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, a third "रक्त" anywhere, a golden word in the second phrase, invented labels, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, any red blood cell, any cell, disc, sphere, molecule, chain, helix, vessel, tube, arrow, shape, icon or illustration of any kind, any label plate, equations, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, a new logo, a duplicated logo, a redrawn logo, a moved logo, a watermark of any kind, text or diagram overlapping either top corner
```

---

```
VIDEO PROMPT — SEGMENT 2 OF 28

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

VOICEOVER NARRATION (spoken audio): an energetic, warm Indian male biology teacher voice speaks this exact Hindi narration during the clip — nothing more, nothing less. The same script also appears on screen word for word, one phrase at a time:
"इनका आकार द्विअवतल चक्रिका के समान होता है, अर्थात् बीच से कुछ दबी हुई होती हैं।"

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
- MATERIAL: a smooth slightly glossy surface with a faint specular highlight near the upper left, and a soft inner glow.
- FORESHORTENING: any arrow pointing toward the camera looks shorter and thicker with a larger arrowhead, and any arrow pointing away looks longer and thinner. They are never all the same length on screen.
- MOTION: the object turns very slowly and steadily around its vertical axis so the depth reads clearly. It never wobbles, never squashes, never deforms and never changes size once settled.

DIAGRAM SPECIFICATION (build exactly this, nothing else):
- THE RED BLOOD CELL: one single red blood cell rendered in full three dimensions as a BICONCAVE DISC — round when seen from above, with a smooth shallow dimple pressed into BOTH the upper face and the lower face, so a cut through it would look like a dumbbell. It is a solid closed disc: the dimple is a shallow depression only, it NEVER becomes a hole, a ring, a doughnut or an open opening, and light never passes through the middle. The whole cell is a uniform rich red, slightly brighter at the raised rim and slightly deeper in the dimple; it is never blue, never purple, never grey. Its surface is smooth and softly glossy with a gentle specular highlight on the upper left. It contains NO nucleus, NO dark central blob, NO inner circle, NO dot and NO organelle of any kind — the paler centre is only thinness, never a drawn object. It turns very slowly and steadily around its vertical axis. It never becomes flat, never becomes a plain circle, never wobbles and never deforms.
- THE LABEL: exactly ONE label exists in this clip — a small white rounded plate with dark bold letters reading "द्विअवतल चक्रिका", joined to the rim of the red blood cell by one short thin white leader line, drawn as a flat overlay in front of the three dimensional scene. It appears only at the time given in the timeline. No other plate, chip, tag, number or floating letter exists anywhere.

DIAGRAM TIMING SYNC (CRITICAL): every object appears at the exact moment its name is visible in the written phrase on screen, and never a frame before. Once an object appears it stays to the end of the clip.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE beyond what is written. Every word appears exactly the number of times it is written.
- EXACT COUNT: the word "द्विअवतल" appears exactly TWICE in total in this clip — once inside the first phrase and once inside the single label plate. Nowhere else, in any size, at any moment.
- EXACT COUNT: the word "चक्रिका" appears exactly TWICE in total in this clip — once inside the first phrase and once inside the single label plate. Nowhere else, in any size, at any moment.
- There is exactly ONE label plate in this clip and it reads "द्विअवतल चक्रिका". No second plate, no chip, no floating letter, no extra leader line, no stray symbol. Never invent a label.
- The text is Hindi in Devanagari script. Every letter, matra, conjunct and danda is rendered exactly as written, correctly formed and correctly joined. No Latin letters, no English words, no numerals of any kind appear anywhere.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated.
In this clip: the FIRST phrase is rendered COMPLETELY UNIFORM bold white with NO golden word, because its words also appear on the label plate. The SECOND phrase has exactly ONE golden key word — "बीच" — styled in place inside the sentence, all remaining words bold white.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time, perfectly synced with the voiceover. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean, glossy, textbook-style biology illustration rendered in three dimensions — smooth shapes, flat bright colours, soft even glow, like a modern NCERT diagram built in 3D. Never photorealistic. NO fire, NO flame, NO burning, NO spark, NO ember, NO explosion, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: completely empty background. Nothing at all.

ANIMATION TIMELINE:
0.0–4.8 s — the first phrase "इनका आकार द्विअवतल चक्रिका के समान होता है," pops in fully sharp at the very top of the frame, completely uniform bold white, and holds perfectly still.
At 1.6 s, exactly as the word "द्विअवतल" is visible on screen inside that phrase, the biconcave red blood cell pops in below the script text, already at its final size, and begins its very slow steady turn. It stays to the end of the clip.
4.8–5.0 s — the first phrase is completely gone. Only the red blood cell and the background are visible. No text at all during this gap.
5.0–10.0 s — the second phrase "अर्थात् बीच से कुछ दबी हुई होती हैं।" pops in fully sharp in the same place at the top, with the single word "बीच" in gold and every other word bold white. It holds perfectly still until 10.0 s.
At 7.5 s the single label plate reading "द्विअवतल चक्रिका" pops in beside the cell with its short thin white leader line touching the cell rim, and holds to the end.
Throughout the clip the bottom half of the frame stays completely empty background.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "इनका आकार द्विअवतल चक्रिका के समान होता है,"
2. "अर्थात् बीच से कुछ दबी हुई होती हैं।"
3. "द्विअवतल चक्रिका"

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, broken or wrongly joined Devanagari conjuncts, missing or misplaced matras, Latin letters, English words, numerals, a red blood cell with a visible nucleus, a dark blob or dot drawn in the centre of the cell, a hole through the middle of the cell, a doughnut, a ring, a torus, a bowl or a cup shape, a dimple on only one face, a flat two dimensional circle instead of a three dimensional biconcave disc, a straight-on front view with no depth, a blue, purple, grey or colourless blood cell, a sickled, crescent, banana, star or spiky cell, more than one cell, a cell membrane drawn as a thick outline, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, a third "द्विअवतल", a second label plate, invented labels, stray floating letters or symbols, the cell appearing before 1.6 seconds, the label appearing before 7.5 seconds, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, equations, camera movement, zoom, scene change, background change, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, a new logo, a duplicated logo, a redrawn logo, a moved logo, a watermark of any kind, text or diagram overlapping either top corner
```

---

```
VIDEO PROMPT — SEGMENT 3 OF 28

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

VOICEOVER NARRATION (spoken audio): an energetic, warm Indian male biology teacher voice speaks this exact Hindi narration during the clip — nothing more, nothing less. The same script also appears on screen word for word, one phrase at a time:
"ये कोशिकाएँ कोमल और लचीली होती हैं। इसलिए ये शरीर की बहुत पतली रक्त वाहिकाओं से भी आसानी से गुजर सकती हैं।"

AUDIO: only the voiceover above. No background music. Only very soft whoosh and pop sounds on text animations are allowed.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, starting close to the top edge. The diagram sits directly below the script text and fills the space between the text and the invisible middle line, so the top half never looks empty. The lowest part of the diagram stops with a clear visible gap above the invisible middle line and never touches it; if it does not fit, make it smaller. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

LOGO SAFE AREA: keep the top-left corner and the top-right corner of the frame completely clear of script text, diagram, equation, labels and any moving element for the whole clip — only the background itself shows there. Do not draw, copy, move, recreate or animate any logo, wordmark, badge or watermark anywhere in the frame; the logo already present on the supplied background must stay exactly where it is, unchanged.

3D RENDER QUALITY (CRITICAL — THIS MAKES THE DIAGRAM LOOK THREE DIMENSIONAL):
The diagram is a real three dimensional object rendered in depth, not a flat drawing.
- CAMERA: a fixed three-quarter view from slightly above the object, so the viewer looks slightly down at it and can clearly read its roundness. Never a flat straight-on front view.
- PERSPECTIVE: circles that run around the object appear as flattened ellipses because of the viewing angle, becoming flatter near the top and bottom and rounder near the middle. Nothing is drawn as a plain flat circle.
- DEPTH: the parts nearest the camera are brighter, thicker and sharper. The parts on the far side, seen through the transparent tube, are noticeably dimmer, thinner and softer. This difference is clear and obvious.
- LIGHTING: one soft cool rim light along the upper left edge and a gentle ambient fill, giving a rounded sculpted look with a soft falloff toward the lower right.
- MATERIAL: a smooth slightly glossy surface with a faint specular highlight near the upper left, and a soft inner glow.
- FORESHORTENING: any arrow pointing toward the camera looks shorter and thicker with a larger arrowhead, and any arrow pointing away looks longer and thinner. They are never all the same length on screen.
- MOTION: objects move slowly and steadily. Nothing wobbles, nothing squashes randomly, nothing changes size once settled.

DIAGRAM SPECIFICATION (build exactly this, nothing else):
- THE RED BLOOD CELL: the same single red blood cell carried over from the previous clip — one biconcave disc rendered in full three dimensions, round seen from above, with a smooth shallow dimple on BOTH faces, uniform rich red, smooth and softly glossy, with NO nucleus, NO dark central blob, NO inner circle and NO hole of any kind. It is already present at the very first frame and does not fade in again.
- THE CAPILLARY: one narrow transparent tube rendered in full three dimensions, running gently across the frame from left to right, drawn as pale grey-white glass with a soft cyan rim light along its upper left edge and clearly visible round openings at both ends so its roundness reads. It is noticeably NARROWER than the red blood cell is wide. Its far wall, seen through the glass, is dimmer and softer than its near wall. It never becomes solid or filled.
- THE SQUEEZE MOTION: the red blood cell moves smoothly into the tube from the left, and as it passes through the narrow part it bends and folds into a soft elongated slipper shape, then springs smoothly back to its full biconcave disc shape as it comes out on the right. It stays a smooth soft deformable object at every moment — it never cracks, never breaks, never tears, never becomes rigid or pointed, and never turns into a crescent.
- THE LABEL: exactly ONE label exists in this clip — a small white rounded plate with dark bold letters reading "पतली रक्त वाहिका", joined to the tube by one short thin white leader line, drawn as a flat overlay in front of the three dimensional scene. It appears only at the time given in the timeline. No other plate, chip, tag, number or floating letter exists anywhere.

DIAGRAM TIMING SYNC (CRITICAL): every object appears at the exact moment its name is visible in the written phrase on screen, and never a frame before. The diagram carried over from the previous clip is already present at the very first frame and does not fade in again. As an explicit exception stated here, the capillary tube and the label both fade out smoothly and completely between 9.0 and 9.5 seconds, leaving only the red blood cell alone and slowly turning from 9.5 s to 10.0 s.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE beyond what is written. In the third phrase the word "से" is written exactly as given — it appears exactly twice there and never a third time anywhere.
- EXACT COUNT: the word "रक्त" appears exactly TWICE in total in this clip — once inside the third phrase and once inside the single label plate. Nowhere else, in any size, at any moment.
- EXACT COUNT: the word "पतली" appears exactly TWICE in total in this clip — once inside the second phrase and once inside the single label plate. Nowhere else, in any size, at any moment.
- There is exactly ONE label plate in this clip and it reads "पतली रक्त वाहिका". No second plate, no chip, no floating letter, no extra leader line, no stray symbol. Never invent a label.
- The text is Hindi in Devanagari script. Every letter, matra, conjunct and danda is rendered exactly as written, correctly formed and correctly joined. No Latin letters, no English words, no numerals of any kind appear anywhere.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated.
In this clip: the FIRST phrase has exactly ONE golden key word — "लचीली" — styled in place inside the sentence, all remaining words bold white. The SECOND phrase is rendered COMPLETELY UNIFORM bold white with NO golden word, because its words also appear on the label plate. The THIRD phrase contains the same word twice and is therefore rendered COMPLETELY UNIFORM bold white with NO golden word.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time, perfectly synced with the voiceover. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean, glossy, textbook-style biology illustration rendered in three dimensions — smooth shapes, flat bright colours, soft even glow, like a modern NCERT diagram built in 3D. Never photorealistic. NO fire, NO flame, NO burning, NO spark, NO ember, NO explosion, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: continuing exactly from the previous clip — one normal biconcave red blood cell, deep red, dimple on both faces, turning very slowly below where the script text will appear. Nothing else. The label from the previous clip is gone.

ANIMATION TIMELINE:
0.0–3.3 s — the first phrase "ये कोशिकाएँ कोमल और लचीली होती हैं।" pops in fully sharp at the very top of the frame, with the single word "लचीली" in gold and every other word bold white. The red blood cell continues its slow steady turn below it.
3.3–3.5 s — the first phrase is completely gone. No text at all during this gap.
3.5–6.6 s — the second phrase "इसलिए ये शरीर की बहुत पतली" pops in fully sharp in the same place, completely uniform bold white.
At 5.0 s, exactly as the word "पतली" is visible on screen inside that phrase, the narrow transparent capillary tube pops in behind the red blood cell, already at its final size.
6.6–6.8 s — the second phrase is completely gone. No text at all during this gap.
6.8–10.0 s — the third phrase "रक्त वाहिकाओं से भी आसानी से गुजर सकती हैं।" pops in fully sharp in the same place, completely uniform bold white, and holds perfectly still until 10.0 s.
From 6.8 to 8.6 s the red blood cell travels smoothly through the tube from left to right, folding softly as it passes the narrow part and springing back to its full biconcave disc shape as it exits.
At 7.2 s the single label plate reading "पतली रक्त वाहिका" pops in beside the tube with its short thin white leader line.
9.0–9.5 s — the capillary tube and the label plate fade out smoothly and completely together.
9.5–10.0 s — only the red blood cell remains, turning very slowly, with the third phrase still on screen.
Throughout the clip the bottom half of the frame stays completely empty background.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "ये कोशिकाएँ कोमल और लचीली होती हैं।"
2. "इसलिए ये शरीर की बहुत पतली"
3. "रक्त वाहिकाओं से भी आसानी से गुजर सकती हैं।"
4. "पतली रक्त वाहिका"

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, broken or wrongly joined Devanagari conjuncts, missing or misplaced matras, Latin letters, English words, numerals, a red blood cell with a visible nucleus, a dark blob or dot drawn in the centre of the cell, a hole through the middle of the cell, a doughnut, a ring, a torus, a bowl or a cup shape, a dimple on only one face, a flat two dimensional circle instead of a three dimensional biconcave disc, a straight-on front view with no depth, a blue, purple, grey or colourless blood cell, a sickled, crescent, banana, star or spiky cell, a cell that cracks, tears or breaks while squeezing, a rigid or stiff cell, a tube wider than the cell, a solid or filled tube, more than one cell, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word beyond what is written, a repeated key word, a keyword written as a separate line, a third "से", a third "रक्त", a second label plate, a second "पतली रक्त वाहिका", invented labels, stray floating letters or symbols, the tube appearing before 5.0 seconds, the label appearing before 7.2 seconds, a golden word in the second or third phrase, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, equations, camera movement, zoom, scene change, background change, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, a new logo, a duplicated logo, a redrawn logo, a moved logo, a watermark of any kind, text or diagram overlapping either top corner
```

---

```
VIDEO PROMPT — SEGMENT 4 OF 28

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

VOICEOVER NARRATION (spoken audio): an energetic, warm Indian male biology teacher voice speaks this exact Hindi narration during the clip — nothing more, nothing less. The same script also appears on screen word for word, one phrase at a time:
"लाल रक्त कोशिकाओं में हीमोग्लोबिन नामक प्रोटीन पाया जाता है, जो शरीर के विभिन्न भागों तक ऑक्सीजन पहुँचाने का कार्य करता है।"

AUDIO: only the voiceover above. No background music. Only very soft whoosh and pop sounds on text animations are allowed.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, starting close to the top edge. The diagram sits directly below the script text and fills the space between the text and the invisible middle line, so the top half never looks empty. The lowest part of the diagram stops with a clear visible gap above the invisible middle line and never touches it; if it does not fit, make it smaller. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

LOGO SAFE AREA: keep the top-left corner and the top-right corner of the frame completely clear of script text, diagram, equation, labels and any moving element for the whole clip — only the background itself shows there. Do not draw, copy, move, recreate or animate any logo, wordmark, badge or watermark anywhere in the frame; the logo already present on the supplied background must stay exactly where it is, unchanged.

3D RENDER QUALITY (CRITICAL — THIS MAKES THE DIAGRAM LOOK THREE DIMENSIONAL):
The diagram is a real three dimensional object rendered in depth, not a flat drawing.
- CAMERA: a fixed three-quarter view from slightly above the object, so the viewer looks slightly down at it and can clearly read its roundness. Never a flat straight-on front view.
- PERSPECTIVE: circles that run around the object appear as flattened ellipses because of the viewing angle, becoming flatter near the top and bottom and rounder near the middle. Nothing is drawn as a plain flat circle.
- DEPTH: the parts nearest the camera are brighter, thicker and sharper. The parts on the far side, seen through the now semi-transparent cell, are noticeably dimmer, thinner and softer. This difference is clear and obvious.
- LIGHTING: one soft cool rim light along the upper left edge and a gentle ambient fill, giving a rounded sculpted look with a soft falloff toward the lower right.
- MATERIAL: a smooth glossy glass-like surface with a faint specular highlight near the upper left, and a soft inner glow.
- FORESHORTENING: any arrow pointing toward the camera looks shorter and thicker with a larger arrowhead, and any arrow pointing away looks longer and thinner. They are never all the same length on screen.
- MOTION: the cell turns very slowly and steadily around its vertical axis so the depth reads clearly. It never wobbles, never squashes, never deforms and never changes size once settled.

DIAGRAM SPECIFICATION (build exactly this, nothing else):
- THE RED BLOOD CELL: the same single red blood cell carried over from the previous clip — one biconcave disc rendered in full three dimensions, round seen from above, with a smooth shallow dimple on BOTH faces, uniform rich red, with NO nucleus, NO dark central blob, NO inner circle and NO hole of any kind. It is already present at the very first frame and does not fade in again. Partway through the clip its red surface becomes semi-transparent glass-like red, so the inside can be seen, while its outline, colour and biconcave shape stay exactly the same. It keeps turning very slowly and steadily.
- THE HAEMOGLOBIN MOLECULE: exactly ONE haemoglobin molecule is shown inside the semi-transparent cell, drawn much larger than true scale so it reads clearly. It is made of exactly FOUR rounded subunits packed together into one compact cluster: exactly TWO cyan-blue subunits and exactly TWO orange subunits, arranged so the two cyan ones sit opposite each other and the two orange ones sit opposite each other. Each subunit is a smooth glossy three dimensional lobe with a soft specular highlight on its upper left. There are exactly four subunits — never three, never five, never six, never a single featureless blob and never a scatter of many small dots. The cluster turns gently with the cell and never separates, never deforms and never changes its colours.
- THE OXYGEN DOTS: six small bright pale-blue glowing dots, all the same size, which drift smoothly outward from the haemoglobin molecule through the semi-transparent cell wall and away, evenly spaced and never tangled, never crossing each other. They carry no letters, no numbers and no symbols of any kind.
- THE LABEL: exactly ONE label exists in this clip — a small white rounded plate with dark bold letters reading "हीमोग्लोबिन", joined to the haemoglobin molecule by one short thin white leader line, drawn as a flat overlay in front of the three dimensional scene. It appears only at the time given in the timeline. No other plate, chip, tag, number or floating letter exists anywhere.

DIAGRAM TIMING SYNC (CRITICAL): every object appears at the exact moment its name is visible in the written phrase on screen, and never a frame before. The diagram carried over from the previous clip is already present at the very first frame and does not fade in again. As an explicit exception stated here, the six oxygen dots fade out smoothly and completely between 9.0 and 9.5 seconds, leaving the semi-transparent cell, the four-subunit haemoglobin molecule inside it and the single label plate on screen from 9.5 s to 10.0 s.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE. Every word appears exactly the number of times it is written.
- EXACT COUNT: the word "हीमोग्लोबिन" appears exactly TWICE in total in this clip — once inside the first phrase and once inside the single label plate. Nowhere else, in any size, at any moment.
- EXACT COUNT: the word "ऑक्सीजन" appears exactly ONCE in total in this clip — only inside the third phrase. It is never written on, beside or near the oxygen dots, and never appears as a chemical formula or symbol of any kind.
- There is exactly ONE label plate in this clip and it reads "हीमोग्लोबिन". No second plate, no chip, no floating letter, no extra leader line, no stray symbol. Never invent a label.
- The text is Hindi in Devanagari script. Every letter, matra, conjunct and danda is rendered exactly as written, correctly formed and correctly joined. No Latin letters, no English words, no numerals of any kind appear anywhere.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated.
In this clip: the FIRST phrase is rendered COMPLETELY UNIFORM bold white with NO golden word, because one of its words also appears on the label plate. The SECOND phrase is rendered COMPLETELY UNIFORM bold white with NO golden word. The THIRD phrase has exactly ONE golden key word — "ऑक्सीजन" — styled in place inside the sentence, all remaining words bold white.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time, perfectly synced with the voiceover. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean, glossy, textbook-style biology illustration rendered in three dimensions — smooth shapes, flat bright colours, soft even glow, like a modern NCERT diagram built in 3D. Never photorealistic. NO fire, NO flame, NO burning, NO spark, NO ember, NO explosion, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: continuing exactly from the previous clip — one normal biconcave red blood cell, deep red, dimple on both faces, turning very slowly below where the script text will appear. Nothing else.

ANIMATION TIMELINE:
0.0–3.3 s — the first phrase "लाल रक्त कोशिकाओं में हीमोग्लोबिन नामक प्रोटीन पाया जाता है," pops in fully sharp at the very top of the frame, completely uniform bold white. The red blood cell continues its slow steady turn below it.
At 1.4 s, exactly as the word "हीमोग्लोबिन" is visible on screen inside that phrase, the red cell's surface becomes semi-transparent glass-like red over 0.4 seconds — its outline, colour and biconcave shape unchanged — and the single haemoglobin molecule of exactly four subunits, two cyan and two orange, pops into view inside it, already at its final size. Both stay to the end of the clip.
3.3–3.5 s — the first phrase is completely gone. No text at all during this gap.
3.5–6.6 s — the second phrase "जो शरीर के विभिन्न भागों तक" pops in fully sharp in the same place, completely uniform bold white.
6.6–6.8 s — the second phrase is completely gone. No text at all during this gap.
6.8–10.0 s — the third phrase "ऑक्सीजन पहुँचाने का कार्य करता है।" pops in fully sharp in the same place, with the single word "ऑक्सीजन" in gold and every other word bold white. It holds perfectly still until 10.0 s.
At 7.0 s, exactly as the word "ऑक्सीजन" is visible on screen inside that phrase, the six pale-blue oxygen dots begin drifting outward from the haemoglobin molecule through the semi-transparent cell wall.
At 8.2 s the single label plate reading "हीमोग्लोबिन" pops in beside the haemoglobin molecule with its short thin white leader line, and holds to the end.
9.0–9.5 s — the six oxygen dots fade out smoothly and completely.
Throughout the clip the bottom half of the frame stays completely empty background.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "लाल रक्त कोशिकाओं में हीमोग्लोबिन नामक प्रोटीन पाया जाता है,"
2. "जो शरीर के विभिन्न भागों तक"
3. "ऑक्सीजन पहुँचाने का कार्य करता है।"
4. "हीमोग्लोबिन"

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, broken or wrongly joined Devanagari conjuncts, missing or misplaced matras, Latin letters, English words, numerals, chemical formulas, a subscript or superscript of any kind, a red blood cell with a visible nucleus, a dark blob or dot drawn in the centre of the cell, a hole through the middle of the cell, a doughnut, a ring, a torus, a bowl or a cup shape, a dimple on only one face, a flat two dimensional circle instead of a three dimensional biconcave disc, a straight-on front view with no depth, a blue, purple, grey or colourless blood cell, a sickled, crescent, banana, star or spiky cell, haemoglobin drawn as one single blob, haemoglobin drawn as three, five or six subunits, haemoglobin drawn as a scatter of many small dots, more than one haemoglobin molecule, all four subunits the same colour, a DNA helix, a protein chain of beads, more than one cell, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, a third "हीमोग्लोबिन", a second "ऑक्सीजन", a second label plate, invented labels, stray floating letters or symbols, letters or symbols written on the oxygen dots, the haemoglobin molecule appearing before 1.4 seconds, the oxygen dots appearing before 7.0 seconds, the label appearing before 8.2 seconds, a golden word in the first or second phrase, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, equations, camera movement, zoom, scene change, background change, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, a new logo, a duplicated logo, a redrawn logo, a moved logo, a watermark of any kind, text or diagram overlapping either top corner
```

---

**Test Segment 1 first** before I write 5–28 — it's pure Devanagari typography with no diagram, so it's the cleanest read on whether Veo/Flow renders the conjuncts (`कोशिकाएँ`, `द्विअवतल`) reliably. If Seg 1 comes back with broken matras, the whole 28-clip plan needs a Latin/Devanagari decision before we go further.

Frames read — they confirm the house look I'm matching: biconcave red RBC (no nucleus, dimple both faces), haemoglobin as discrete units inside the cell, and the sickle as a pointed-ended crescent. Below are Segments 5–8, full blocks, tested order, uploaded-background (§15) + LOGO SAFE AREA (§16) in every one.

---

## Segment 5 — DIAGRAM (haemoglobin → 4 chains → HBB gene)

```
VIDEO PROMPT — SEGMENT 5 OF 28

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
- PERSPECTIVE: circles that run around the object appear as flattened ellipses because of the viewing angle, becoming flatter near the top and bottom and rounder near the middle. Nothing is drawn as a plain flat circle.
- DEPTH: the parts nearest the camera are brighter, thicker and sharper. The parts on the far side, seen through the transparent surface, are noticeably dimmer, thinner and softer. This difference is clear and obvious.
- LIGHTING: one soft cool rim light along the upper left edge and a gentle ambient fill, giving a rounded sculpted look with a soft falloff toward the lower right.
- MATERIAL: a smooth glossy glass-like surface with a faint specular highlight near the upper left, and a soft inner glow.
- FORESHORTENING: any arrow pointing toward the camera looks shorter and thicker with a larger arrowhead, and any arrow pointing away looks longer and thinner. They are never all the same length on screen.
- MOTION: the object turns very slowly and steadily around its vertical axis so the depth reads clearly. It never wobbles, never squashes, never deforms and never changes size once settled.

DIAGRAM SPECIFICATION (build exactly this, nothing else):
- THE RED BLOOD CELL (present only in the first part of the clip): one three dimensional biconcave disc, uniformly red, glossy and semi-transparent, shaped like a rounded disc that is pressed inward into a shallow dimple on BOTH of its flat faces — it is never a bowl with only one dimple, never a flat circle, never a ring or doughnut with a hole through the middle. It contains NO nucleus and NO dark central blob of any kind; the paler centre is only the thinner part of the cell. Four small haemoglobin units float inside it, visible through the semi-transparent surface. It turns very slowly and steadily.
- THE HAEMOGLOBIN MOLECULE: one single haemoglobin molecule rendered in full three dimensions as EXACTLY FOUR rounded glossy subunits packed together into one compact cluster — exactly TWO cyan-blue subunits and exactly TWO orange subunits, arranged in facing pairs so both colours are clearly readable. There are never three subunits, never five, never six, and never one single blob. The two cyan subunits are the alpha chains and the two orange subunits are the beta chains; only an orange subunit is ever highlighted in this clip, the cyan ones stay exactly as they are and never change colour. Each subunit has a faint specular highlight on its upper left and a soft inner glow. The cluster turns very slowly and steadily and never deforms.
- THE HIGHLIGHT ON ONE BETA CHAIN: exactly ONE of the two orange subunits turns bright yellow and glows in place at the time given in the timeline. It does not move, does not detach, does not duplicate and does not grow. The other orange subunit and both cyan subunits are untouched.
- THE CARRIED-OVER LABEL: exactly ONE label plate reading "हीमोग्लोबिन" is present at the very first frame — a small white rounded plate with dark bold letters, joined to the red blood cell by one short thin white leader line, drawn as a flat overlay in front of the three dimensional scene. It fades out at the time given in the timeline and never returns.
- THE NEW LABEL: exactly ONE label plate reading "एचबीबी जीन" — a small white rounded plate with dark bold letters, joined to the glowing yellow subunit by one short thin white leader line, drawn as a flat overlay in front of the three dimensional scene. It appears only at the time given in the timeline. No other plate, chip, tag, number or floating letter exists anywhere.

DIAGRAM TIMING SYNC (CRITICAL): every object appears at the exact moment its name is visible in the written phrase on screen, and never a frame before. Once an object appears it stays to the end of the clip. The diagram carried over from the previous clip is already present at the very first frame and does not fade in again.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE. Every word appears exactly the number of times it is written.
- EXACT COUNT: the word "हीमोग्लोबिन" appears exactly TWICE in total in this clip — once inside the first phrase and once on the carried-over label plate. Nowhere else, in any size, at any moment.
- EXACT COUNT: the word "जीन" appears exactly TWICE in total in this clip — once inside the second phrase and once on the label plate reading "एचबीबी जीन". Nowhere else.
- EXACT COUNT: the word "एचबीबी" appears exactly TWICE in total in this clip — once inside the second phrase and once on the label plate reading "एचबीबी जीन". Nowhere else.
- EXACT COUNT: exactly TWO label plates exist in this whole clip and never more — one reading "हीमोग्लोबिन" and one reading "एचबीबी जीन". They are never on screen with a third plate of any kind.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol, matra by matra.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. In this clip: the FIRST phrase has exactly ONE golden word, "निर्माण", styled in place inside the sentence. The SECOND phrase is rendered COMPLETELY UNIFORM in bold white with NO golden word at all. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters or matras are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time, perfectly synced with the voiceover. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean, glossy, textbook-style biology illustration rendered in three dimensions — smooth shapes, flat bright colours, soft even glow, like a modern NCERT diagram built in 3D. Never photorealistic. NO fire, NO flame, NO burning, NO spark, NO ember, NO explosion, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: continuing exactly from the previous clip — one semi-transparent red biconcave red blood cell turning slowly, with four small haemoglobin units visible inside it, and one white label plate reading "हीमोग्लोबिन" joined to it by a short thin white leader line. Nothing else.

ANIMATION TIMELINE:
0.0 s — the first phrase "हीमोग्लोबिन की बीटा-ग्लोबिन श्रृंखला का निर्माण" pops in at the top, fully sharp, with the golden word "निर्माण" styled in place. The red blood cell and its label are already present and do not fade in again.
1.0 s — exactly as the word "हीमोग्लोबिन" is visible on screen, one of the four haemoglobin units inside the cell begins to enlarge smoothly toward the centre of the diagram area.
1.8 s — the red blood cell and the label plate "हीमोग्लोबिन" fade out completely together while the enlarging haemoglobin unit continues to grow.
2.6 s — the haemoglobin molecule settles at full size as one compact cluster of exactly four subunits: two cyan and two orange, clearly readable, turning very slowly.
4.8 s — the first phrase disappears completely.
5.0 s — after a 0.2 second gap of no phrase, the second phrase "एचबीबी जीन द्वारा नियंत्रित होता है।" pops in at the top, fully sharp, completely uniform bold white with no golden word.
6.0 s — exactly as the words "एचबीबी जीन" are visible on screen, exactly ONE of the two orange subunits turns bright yellow and glows in place, and holds that glow to the end. Nothing detaches and nothing is copied out of the molecule.
7.6 s — the white label plate reading "एचबीबी जीन" pops in, joined to the glowing yellow subunit by one short thin white leader line, and holds to the end.
10.0 s — the clip ends with the second phrase, the four-subunit haemoglobin molecule with one yellow-glowing subunit, and the single label plate on screen.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "हीमोग्लोबिन की बीटा-ग्लोबिन श्रृंखला का निर्माण"
2. "एचबीबी जीन द्वारा नियंत्रित होता है।"
3. "हीमोग्लोबिन"
4. "एचबीबी जीन"

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters or broken matras during a transition, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, invented labels, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, a new logo, a duplicated logo, a redrawn logo, a moved logo, a watermark of any kind, text or diagram overlapping either top corner, a red blood cell with a visible nucleus, a dark blob or dot drawn in the centre of the red blood cell, a red blood cell drawn as a flat two dimensional circle, a red blood cell drawn as a ring or doughnut with a hole through it, a red blood cell drawn as a bowl with a dimple on only one side, a blue or purple red blood cell, a haemoglobin molecule drawn as one single blob, three subunits, five subunits, six subunits, all four subunits the same colour, a cyan subunit turning yellow, both orange subunits glowing at the same time, a subunit detaching or floating away from the cluster, any DNA, any helix, any letters A T G or C anywhere, any bead chain, any sickle or crescent shaped cell, the haemoglobin appearing before 1.0 seconds, the yellow glow appearing before 6.0 seconds, the label "एचबीबी जीन" appearing before 7.6 seconds, a third label plate, a second "हीमोग्लोबिन", a second "एचबीबी जीन", equations, a golden word in the second phrase
```

---

## Segment 6 — DIAGRAM (gene → DNA → one base changes)

```
VIDEO PROMPT — SEGMENT 6 OF 28

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

VOICEOVER NARRATION (spoken audio): an energetic, warm Indian male biology teacher voice speaks this exact Hinglish narration during the clip — nothing more, nothing less. The same script also appears on screen word for word, one phrase at a time:
"सिकल सेल एनीमिया में इस जीन के डीएनए क्रम में एक क्षार का परिवर्तन हो जाता है।"

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
- THE CARRIED-OVER HAEMOGLOBIN (present only in the first part of the clip): the compact cluster of exactly four subunits — exactly two cyan and exactly two orange, with exactly ONE orange subunit glowing bright yellow — is present at the very first frame, together with its white label plate reading "एचबीबी जीन" joined by one short thin white leader line. It shrinks smoothly, drifts upward and fades away completely, together with its label plate, at the time given in the timeline, and never returns.
- THE DNA DOUBLE HELIX: one three dimensional double helix, clearly RIGHT-HANDED — seen from the front, the strand nearest the camera rises from the lower left toward the upper right. It is never left-handed and never mirrored. It is made of two smooth glossy backbone ribbons in cool cyan-blue that twist evenly around a common vertical axis, joined by short straight rungs. Because of the three-quarter camera angle the turns of the helix read as flattened ellipses, flatter at the top and bottom of each turn and rounder in the middle; the near-side backbone and rungs are bright, thick and sharp, while the far-side backbone and rungs seen behind them are clearly dimmer, thinner and softer. The rungs are plain coloured bars only — there are NO letters, NO characters and NO writing of any kind anywhere on the helix. The helix turns very slowly and steadily around its vertical axis and never wobbles, never stretches and never unzips.
- THE CHANGED BASE: exactly ONE single rung near the middle of the helix turns bright yellow and glows in place. It is a change of colour only, exactly one rung, in the same position — the rung never moves, never falls out, never is removed, and no rung is ever added or deleted. The number of rungs is exactly the same before and after, and the spacing between all rungs is unchanged.
- LABELS: after the carried-over plate fades, this clip has NO labels at all. Never invent a label.

DIAGRAM TIMING SYNC (CRITICAL): every object appears at the exact moment its name is visible in the written phrase on screen, and never a frame before. Once an object appears it stays to the end of the clip. The diagram carried over from the previous clip is already present at the very first frame and does not fade in again.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE. Every word appears exactly the number of times it is written.
- EXACT COUNT: the word "में" appears exactly TWICE in total in this clip — once at the end of the first phrase and once at the end of the second phrase. Never a third time, in any size, at any moment.
- EXACT COUNT: the word "जीन" appears exactly TWICE in total in this clip — once inside the second phrase and once on the carried-over label plate reading "एचबीबी जीन". Nowhere else.
- EXACT COUNT: exactly ONE label plate exists in this clip, the carried-over "एचबीबी जीन", and it fades away and never returns. After it fades there is no plate, no chip, no floating letter, no leader line and no stray symbol anywhere. Never invent a label.
- The DNA double helix carries NO text: no letters, no A, no T, no G, no C, no numbers, no symbols of any kind are written on it or beside it at any moment.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol, matra by matra.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. In this clip: the FIRST phrase has exactly ONE golden word, "एनीमिया". The SECOND phrase is rendered COMPLETELY UNIFORM in bold white with NO golden word at all. The THIRD phrase has exactly ONE golden word, "क्षार". Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters or matras are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time, perfectly synced with the voiceover. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean, glossy, textbook-style biology illustration rendered in three dimensions — smooth shapes, flat bright colours, soft even glow, like a modern NCERT diagram built in 3D. Never photorealistic. NO fire, NO flame, NO burning, NO spark, NO ember, NO explosion, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: continuing exactly from the previous clip — the compact haemoglobin cluster of exactly four subunits, two cyan and two orange, with exactly one orange subunit glowing bright yellow, and one white label plate reading "एचबीबी जीन" joined to that glowing subunit by a short thin white leader line. Nothing else.

ANIMATION TIMELINE:
0.0 s — the first phrase "सिकल सेल एनीमिया में" pops in at the top, fully sharp, with the golden word "एनीमिया" styled in place. The haemoglobin cluster and its label are already present and do not fade in again.
3.3 s — the first phrase disappears completely.
3.5 s — after a 0.2 second gap of no phrase, the second phrase "इस जीन के डीएनए क्रम में" pops in at the top, fully sharp, completely uniform bold white with no golden word.
4.2 s — exactly as the word "डीएनए" is visible on screen, the haemoglobin cluster and the label plate "एचबीबी जीन" shrink, drift upward and fade away completely together, and the right-handed DNA double helix pops in below the script text and settles, turning very slowly.
6.6 s — the second phrase disappears completely.
6.8 s — after a 0.2 second gap of no phrase, the third phrase "एक क्षार का परिवर्तन हो जाता है।" pops in at the top, fully sharp, with the golden word "क्षार" styled in place.
7.8 s — exactly as the word "क्षार" is visible on screen, exactly ONE single rung near the middle of the helix turns bright yellow and glows in place, and holds that glow to the end. The rung stays in its own position; no rung is added, removed or shifted.
10.0 s — the clip ends with the third phrase and the slowly turning right-handed DNA double helix with exactly one glowing yellow rung on screen.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "सिकल सेल एनीमिया में"
2. "इस जीन के डीएनए क्रम में"
3. "एक क्षार का परिवर्तन हो जाता है।"
4. "एचबीबी जीन"

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters or broken matras during a transition, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, invented labels, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, a new logo, a duplicated logo, a redrawn logo, a moved logo, a watermark of any kind, text or diagram overlapping either top corner, a left-handed DNA helix, a mirrored helix, a flat two dimensional ladder instead of a three dimensional helix, a helix drawn as a flat wavy line, the helix unzipping or splitting apart, any letters A T G C or U written on the helix, any letters or numbers anywhere on the DNA, a rung being removed, a rung being deleted, a rung falling out, an extra rung being inserted, the rungs shifting sideways, a frameshift, more than one glowing rung, a red blood cell with a visible nucleus, a red blood cell drawn as a flat circle or as a ring with a hole, a haemoglobin drawn as one single blob, all four subunits the same colour, a mutation shown on a cyan subunit, a sickle or crescent shaped cell, the DNA helix appearing before 4.2 seconds, the yellow rung appearing before 7.8 seconds, a second label plate, a second "एचबीबी जीन", equations, a golden word in the second phrase
```

---

## Segment 7 — TRANSITION (DNA fades → `GAG → GTG`)

```
VIDEO PROMPT — SEGMENT 7 OF 28

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

VOICEOVER NARRATION (spoken audio): an energetic, warm Indian male biology teacher voice speaks this exact Hinglish narration during the clip — nothing more, nothing less. The same script also appears on screen word for word, one phrase at a time:
"अर्थात्, सामान्य अवस्था में GAG के स्थान पर GTG हो जाता है।"

AUDIO: only the voiceover above. No background music. Only very soft whoosh and pop sounds on text animations are allowed.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, starting close to the top edge. The diagram and then the equation sit directly below the script text, filling the space between the text and the invisible middle line. The lowest element stops with a clear visible gap above the invisible middle line and never touches it; if it does not fit, make it smaller. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

LOGO SAFE AREA: keep the top-left corner and the top-right corner of the frame completely clear of script text, diagram, equation, labels and any moving element for the whole clip — only the background itself shows there. Do not draw, copy, move, recreate or animate any logo, wordmark, badge or watermark anywhere in the frame; the logo already present on the supplied background must stay exactly where it is, unchanged.

3D RENDER QUALITY (for the diagram in the first half of this clip):
The diagram is a real three dimensional object rendered in depth, not a flat drawing — a fixed three-quarter view from slightly above, circles appearing as flattened ellipses, near-side lines brighter and sharper than far-side lines, a soft cool rim light along the upper left edge, glossy glass-like material with a faint specular highlight, and a very slow steady turn around the vertical axis.

DIAGRAM SPECIFICATION: the scene from the previous clip — one three dimensional RIGHT-HANDED DNA double helix in cool cyan-blue with plain coloured rungs carrying no letters of any kind, and exactly ONE rung near its middle glowing bright yellow — is present at the very first frame. It shrinks smoothly to about half its size, drifts upward, and fades away completely by 4.0 seconds, leaving the area below the script text free for the codon line. The helix stays right-handed and unchanged in every other way while it fades; it never unzips, never straightens, never mirrors and never gains letters. LABELS: this clip has NO labels at all. Never invent a label.

DIAGRAM TIMING SYNC (CRITICAL): the codon line appears at the exact moment the letters naming it are visible in the written phrase on screen, and never before.

EQUATION RULE (CRITICAL): the codon line is flat two dimensional overlay text, not a three dimensional object. It is ONE single clean horizontal line of large bold white text with a soft cyan glow, reading exactly "GAG → GTG", centred below the script text, perfectly sharp, with every letter correct and correctly sized. It is not on a card, not in a box, and never stacked onto two lines. If it is too wide, reduce its size until the whole line fits comfortably inside the frame width with clear margins on both sides. It appears exactly once and holds to the end of the clip. The script text stays at the top and the codon line stays below it — they never overlap and never swap places. The three letters on the left are exactly G, A, G and the three letters on the right are exactly G, T, G. The middle letter on the right is T and is NEVER U. Only the middle letter differs between the two sides; the first and last letters are identical on both sides.

HIGHLIGHT RULE (CRITICAL — NO NEW TEXT IS EVER CREATED): when a part of the codon line is emphasised, that part of the EXISTING line simply changes colour and glows brighter in place. NEVER copy a letter out of the line. NEVER draw a second copy of any letter anywhere. NEVER create a label, plate, chip, callout or floating letter for it. The codon line itself is the only place any of these letters ever appears.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE. Every word appears exactly the number of times it is written.
- EXACT COUNT: the group of letters "GAG" appears exactly TWICE in total in this clip — once inside the second phrase and once on the left side of the codon line. Nowhere else, in any size, at any moment.
- EXACT COUNT: the group of letters "GTG" appears exactly TWICE in total in this clip — once inside the second phrase and once on the right side of the codon line. Nowhere else, in any size, at any moment.
- EXACT COUNT: the letter "G" appears exactly EIGHT times in total in this whole clip and never more — four times inside the second phrase, two in "GAG" and two in "GTG", and four times inside the codon line, two in "GAG" and two in "GTG". There is never a stray, floating or extra G anywhere.
- EXACT COUNT: the letter "A" in Latin script appears exactly TWICE in total in this clip — once in "GAG" inside the second phrase and once in "GAG" inside the codon line. The letter "T" in Latin script appears exactly TWICE in total — once in "GTG" inside the second phrase and once in "GTG" inside the codon line.
- The letter "U" never appears anywhere in this clip in any form.
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol, matra by matra.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. In this clip BOTH phrases are rendered COMPLETELY UNIFORM in bold white with NO golden word anywhere at any moment. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters, matras or mathematical symbols individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters, matras or symbols are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time, perfectly synced with the voiceover. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean crisp flat overlay typography on a dark technical background, with the fading three dimensional helix in the first half rendered as a glossy textbook-style biology illustration. Never photorealistic. NO fire, NO flame, NO sparks, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: continuing exactly from the previous clip — the slowly turning right-handed DNA double helix with exactly one bright yellow glowing rung near its middle and no letters anywhere on it. Nothing else.

ANIMATION TIMELINE:
0.0 s — the first phrase "अर्थात्, सामान्य अवस्था में" pops in at the top, fully sharp, completely uniform bold white with no golden word. The helix is already present and does not fade in again.
1.5 s — the helix begins to shrink to about half its size and drift upward, still turning slowly.
4.0 s — the helix has faded away completely; the area below the script text is now empty background.
4.8 s — the first phrase disappears completely.
5.0 s — after a 0.2 second gap of no phrase, the second phrase "GAG के स्थान पर GTG हो जाता है।" pops in at the top, fully sharp, completely uniform bold white with no golden word.
5.8 s — exactly as the letters "GAG" are visible on screen, the single codon line "GAG → GTG" pops in below the script text as one clean horizontal line of large bold white text with a soft cyan glow, fully sharp from its first visible frame, and holds to the end without moving or resizing.
7.5 s — the three letters "GTG" inside the EXISTING codon line turn bright green and glow, staying exactly in their place inside that line, and hold that glow to the end. Nothing is copied out of the line and no new text is created.
10.0 s — the clip ends with the second phrase and the single codon line "GAG → GTG" with GTG glowing green on screen.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "अर्थात्, सामान्य अवस्था में"
2. "GAG के स्थान पर GTG हो जाता है।"
3. "GAG → GTG"

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters or broken matras during a transition, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, invented labels, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, a new logo, a duplicated logo, a redrawn logo, a moved logo, a watermark of any kind, text or diagram overlapping either top corner, the letter U anywhere, "GUG", "GAU", a left-handed or mirrored DNA helix, letters written on the helix, the helix unzipping, a red blood cell, a sickle or crescent cell, a bead chain, a haemoglobin cluster, any sphere, ball, arrow, cell, vessel, icon or illustration after 4.0 seconds, a copy of any letter taken out of the codon line, a floating letter G, A or T anywhere outside the codon line and outside the second phrase, any label plate, any chip, any callout, any leader line, two copies of the codon line, the codon line moving or resizing, the codon line stacked onto two lines, the codon line appearing before 5.8 seconds, the green glow appearing before 7.5 seconds, more than one letter differing between the two sides, a golden word in either phrase, extra equations, extra codons
```

---

## Segment 8 — DIAGRAM (one base change → position 6 → Valine)

```
VIDEO PROMPT — SEGMENT 8 OF 28

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

VOICEOVER NARRATION (spoken audio): an energetic, warm Indian male biology teacher voice speaks this exact Hinglish narration during the clip — nothing more, nothing less. The same script also appears on screen word for word, one phrase at a time:
"इस एक क्षार के परिवर्तन के कारण बीटा-ग्लोबिन श्रृंखला की छठी स्थिति पर ग्लूटामिक अम्ल के स्थान पर वेलिन आ जाता है।"

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
- THE CARRIED-OVER CODON LINE (present only in the first part of the clip): the single flat horizontal line of large bold white text reading "GAG → GTG", with "GTG" glowing green, is present at the very first frame. It fades away completely at the time given in the timeline and never returns. While it is on screen it never moves, never resizes and never duplicates.
- THE BETA CHAIN BEAD STRAND: one gently curving strand of exactly TEN identical rounded glossy three dimensional beads in warm orange, evenly spaced and joined by short thick connectors, laid out from the left of the frame to the right and curving slightly, rendered with real depth so the beads nearer the camera are larger, brighter and sharper and the beads farther away are smaller, dimmer and softer. The leftmost bead is the start of the chain. The strand represents the beta chain only; no second strand and no cyan chain is ever drawn. The strand drifts very slowly and never deforms, never stretches, never loses a bead and never gains a bead — the count of beads is exactly the same at the start and at the end of the clip.
- THE SIXTH BEAD: exactly ONE bead — the SIXTH bead counting from the leftmost bead — first glows bright yellow, then turns bright green, in its own place. It never moves out of the strand, never detaches, never is replaced by a gap and never duplicates. The fifth bead and the seventh bead are untouched and stay warm orange, as do all the other beads.
- THE NUMBER MARKER: exactly ONE small numeral "6" in white, sitting just below the sixth bead, joined to it by one short thin white leader line, drawn as a flat overlay in front of the three dimensional scene. There is no other numeral, digit or number anywhere in the frame at any moment; the other beads are not numbered.
- THE LABEL: exactly ONE label plate exists in this clip — a small white rounded plate with dark bold letters reading "वेलिन", joined to the green sixth bead by one short thin white leader line, drawn as a flat overlay in front of the three dimensional scene. It appears only at the time given in the timeline. No other plate, chip, tag, number or floating letter exists anywhere.

DIAGRAM TIMING SYNC (CRITICAL): every object appears at the exact moment its name is visible in the written phrase on screen, and never a frame before. Once an object appears it stays to the end of the clip. The codon line carried over from the previous clip is already present at the very first frame and does not fade in again.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE beyond what is written. In the first phrase the word "के" is written exactly twice as given and never a third time in that phrase.
- EXACT COUNT: the word "के" appears exactly THREE times in total in this clip — twice inside the first phrase and once inside the third phrase. Never a fourth time, in any size, at any moment.
- EXACT COUNT: the word "पर" appears exactly TWICE in total in this clip — once at the end of the second phrase and once inside the third phrase. Never a third time.
- EXACT COUNT: the word "स्थान" appears exactly ONCE in this clip, inside the third phrase. The word "स्थिति" appears exactly ONCE in this clip, inside the second phrase. They are never swapped and never repeated.
- EXACT COUNT: the word "वेलिन" appears exactly TWICE in total in this clip — once inside the third phrase and once on the single label plate. Nowhere else.
- EXACT COUNT: the numeral "6" appears exactly ONCE in this whole clip, as the single marker under the sixth bead. No other digit and no other number appears anywhere, in any size, at any moment.
- EXACT COUNT: the carried-over line "GAG → GTG" appears exactly ONCE in this clip and then fades away for good.
- EXACT COUNT: exactly ONE label plate exists in this whole clip, reading "वेलिन", and never a second plate of any kind.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol, matra by matra.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. In this clip: the FIRST phrase is rendered COMPLETELY UNIFORM in bold white with NO golden word, because it contains the same word twice. The SECOND phrase has exactly ONE golden word, "छठी", styled in place inside the sentence. The THIRD phrase is rendered COMPLETELY UNIFORM in bold white with NO golden word at all. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters, matras or mathematical symbols individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters, matras or symbols are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time, perfectly synced with the voiceover. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean, glossy, textbook-style biology illustration rendered in three dimensions — smooth shapes, flat bright colours, soft even glow, like a modern NCERT diagram built in 3D. Never photorealistic. NO fire, NO flame, NO burning, NO spark, NO ember, NO explosion, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: continuing exactly from the previous clip — the single flat line "GAG → GTG" sitting alone below where the script text will appear, sharp and still, with "GTG" glowing green. Nothing else.

ANIMATION TIMELINE:
0.0 s — the first phrase "इस एक क्षार के परिवर्तन के कारण" pops in at the top, fully sharp, completely uniform bold white with no golden word. The line "GAG → GTG" is already present and does not fade in again.
2.4 s — the line "GAG → GTG" fades away completely and never returns.
3.3 s — the first phrase disappears completely.
3.5 s — after a 0.2 second gap of no phrase, the second phrase "बीटा-ग्लोबिन श्रृंखला की छठी स्थिति पर" pops in at the top, fully sharp, with the golden word "छठी" styled in place.
4.2 s — exactly as the word "श्रृंखला" is visible on screen, the strand of exactly ten orange beads pops in below the script text and settles, drifting very slowly.
5.6 s — exactly as the word "छठी" is visible on screen, the SIXTH bead counting from the leftmost bead glows bright yellow in its own place, and the small white numeral "6" pops in just below it with one short thin white leader line, and both hold.
6.6 s — the second phrase disappears completely.
6.8 s — after a 0.2 second gap of no phrase, the third phrase "ग्लूटामिक अम्ल के स्थान पर वेलिन आ जाता है।" pops in at the top, fully sharp, completely uniform bold white with no golden word.
8.0 s — exactly as the word "वेलिन" is visible on screen, the yellow sixth bead turns bright green in its own place, still inside the strand, and holds. Every other bead stays warm orange and untouched.
8.8 s — the white label plate reading "वेलिन" pops in, joined to the green sixth bead by one short thin white leader line, and holds to the end.
10.0 s — the clip ends with the third phrase, the ten-bead orange strand with a green sixth bead, the numeral "6" and the single label plate on screen.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "इस एक क्षार के परिवर्तन के कारण"
2. "बीटा-ग्लोबिन श्रृंखला की छठी स्थिति पर"
3. "ग्लूटामिक अम्ल के स्थान पर वेलिन आ जाता है।"
4. "GAG → GTG"
5. "6"
6. "वेलिन"

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters or broken matras during a transition, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, invented labels, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, a new logo, a duplicated logo, a redrawn logo, a moved logo, a watermark of any kind, text or diagram overlapping either top corner, the fifth bead changing colour, the seventh bead changing colour, more than one bead changing colour, a bead being removed, a bead falling out, a gap in the strand, an extra bead being inserted, the strand getting longer or shorter, a frameshift, all the beads changing colour, a second bead strand, a cyan alpha chain being changed, a haemoglobin cluster, a DNA helix, any letters A T G C or U, a red blood cell with a visible nucleus, a red blood cell drawn as a flat circle or as a ring with a hole, a sickle or crescent shaped cell, any digit other than the single "6", numbers printed on the other beads, the bead strand appearing before 4.2 seconds, the numeral "6" appearing before 5.6 seconds, the green bead appearing before 8.0 seconds, the label "वेलिन" appearing before 8.8 seconds, a second label plate, a second "वेलिन", a second "6", a golden word in the first or third phrase, extra equations
```

---

**Notes on decisions I locked in while writing these four:**

- **Seg 5 P2 and Seg 7 both phrases are fully UNIFORM** — Seg 5 P2 because `जीन`/`एचबीबी` also live on a label plate, Seg 7 because of Latin codons. Golden words used: Seg 5 `निर्माण`, Seg 6 `एनीमिया` + `क्षार`, Seg 8 `छठी` only.
- **DNA rungs carry no letters** in Seg 6 — deliberate. Putting A/T/G/C on the helix would collide with Seg 7's `GAG → GTG` counts and is the single most likely garble source. The codon reveal is Seg 7's job.
- **Position 6 is shown as a 10-bead strand with only bead six numbered** — one numeral on screen, counted from the leftmost (N-terminus) bead. Numbering every bead would flood the frame with digits.
- Every COMMON ERROR from the brief that could plausibly render in these four clips is an explicit ban: nucleus, flat/ring RBC, left-handed helix, U instead of T, alpha-chain mutation, all-four-chains changed, position 5/7, frameshift/deletion.

Test Segment 5 first — it is the Devanagari conjunct stress test (`श्रृंखला`, `हीमोग्लोबिन`) for this whole block. If it renders clean, 6–8 will follow.

Frames read. One deviation I'm making from the plan, flagged up front: your reference art draws HbS polymer fibres **blue-violet inside the red cell** (frames 3a/3b), not red. Red fibres inside a red cell won't read at all, so Segs 11–12 below spec the fibres as deep blue-violet to match your own artwork. Everything else follows the plan verbatim.

---

## SEGMENT 9 OF 28 — TRANSITION (bead strand → HbA → HbS line)

```
VIDEO PROMPT — SEGMENT 9 OF 28

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

VOICEOVER NARRATION (spoken audio): an energetic, warm Indian male biology teacher voice speaks this exact Hinglish narration during the clip — nothing more, nothing less. The same script also appears on screen word for word, one phrase at a time:
"इस प्रकार केवल एक अमीनो अम्ल के परिवर्तन के कारण सामान्य हीमोग्लोबिन HbA के स्थान पर HbS बनने लगता है।"

AUDIO: only the voiceover above. No background music. Only very soft whoosh and pop sounds on text animations are allowed.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, starting close to the top edge. The diagram and then the equation sit directly below the script text, filling the space between the text and the invisible middle line. The lowest element stops with a clear visible gap above the invisible middle line and never touches it; if it does not fit, make it smaller. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

LOGO SAFE AREA: keep the top-left corner and the top-right corner of the frame completely clear of script text, diagram, equation, labels and any moving element for the whole clip — only the background itself shows there. Do not draw, copy, move, recreate or animate any logo, wordmark, badge or watermark anywhere in the frame; the logo already present on the supplied background must stay exactly where it is, unchanged.

3D RENDER QUALITY (for the diagram in the first half of this clip):
The diagram is a real three dimensional object rendered in depth, not a flat drawing — a fixed three-quarter view from slightly above, rounded beads rendered as spheres with visible near-side and far-side depth, near-side beads brighter and sharper than far-side beads, a soft cool rim light along the upper left edge, glossy glass-like material with a faint specular highlight, and a very slow steady drift.

DIAGRAM SPECIFICATION: the scene from the previous clip — the beta-globin chain drawn as a single strand of small numbered three dimensional beads in a gentle curve, all beads soft orange except the sixth bead counting from the left end of the strand which is bright green, with one small white rounded label plate reading "वेलिन" joined to that green bead by one short thin white leader line — is present at the very first frame, exactly as it ended in the previous clip, and does not fade in again. Starting at 2.0 seconds it shrinks smoothly to about half its size, drifts upward, and fades away completely by 4.0 seconds, taking its label plate with it, leaving the area below the script text free for the equation. The green bead is and stays the SIXTH bead — never the fifth, never the seventh — and only that one bead is green; every other bead stays soft orange and unchanged. LABELS: after 4.0 seconds this clip has NO labels at all. Never invent a label.

DIAGRAM TIMING SYNC (CRITICAL): the diagram carried over from the previous clip is already present at the very first frame and does not fade in again. The equation appears at the exact moment the letters naming the normal haemoglobin are visible in the written phrase on screen, and never a frame before.

EQUATION RULE (CRITICAL): the equation is flat two dimensional overlay text, not a three dimensional object. It is ONE single clean horizontal line of large bold white text with a soft cyan glow, centred below the script text, perfectly sharp, with every letter correct and correctly sized, reading exactly: HbA → HbS. It is not on a card, not in a box, and never stacked onto two lines. If it is too wide, reduce its size until the whole line fits comfortably inside the frame width with clear margins on both sides. It appears exactly once and holds to the end of the clip. The casing is exactly HbA and exactly HbS — never HBA, never HBS, never HgB, never Hba. The script text stays at the top and the equation stays below it — they never overlap and never swap places.

HIGHLIGHT RULE (CRITICAL — NO NEW TEXT IS EVER CREATED): when a part of the equation is emphasised, that part of the EXISTING equation simply changes colour and glows brighter in place. NEVER copy a symbol out of the equation. NEVER draw a second copy of any symbol anywhere. NEVER create a label, plate, chip, callout or floating letter for it. The equation itself is the only place any symbol ever appears.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE. Every word appears exactly the number of times it is written.
- EXACT COUNT: the word "के" appears exactly TWICE in total in this clip — once inside the first phrase and once inside the second phrase. Nowhere else, in any size, at any moment.
- EXACT COUNT: the text "HbA" appears exactly TWICE in total in this clip — once inside the second phrase and once inside the equation. Nowhere else, in any size, at any moment.
- EXACT COUNT: the text "HbS" appears exactly TWICE in total in this clip — once inside the third phrase and once inside the equation. Nowhere else, in any size, at any moment.
- EXACT COUNT: the letters "Hb" therefore appear exactly FOUR times in total in this clip and only as part of those four items. There is no fifth "Hb" and no floating "Hb" anywhere.
- The only label plate in this clip is the carried-over "वेलिन" plate, which is present from the very first frame and is gone by 4.0 seconds. After that there is no plate, no chip, no floating letter, no leader line and no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol, matra by matra. The Devanagari conjuncts and matras are rendered perfectly and are never broken, doubled or reshaped.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. In this clip ALL THREE phrases are rendered COMPLETELY UNIFORM in bold white with NO golden word anywhere. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters or mathematical symbols into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time, perfectly synced with the voiceover. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean, glossy, textbook-style biology illustration rendered in three dimensions — smooth shapes, flat bright colours, soft even glow, like a modern NCERT diagram built in 3D. Never photorealistic. NO fire, NO flame, NO burning, NO spark, NO ember, NO explosion, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: continuing exactly from the previous clip — the beta-globin bead strand sits below where the text will appear, with the sixth bead bright green and the small white "वेलिन" label plate joined to it by a short thin white leader line. Nothing else.

ANIMATION TIMELINE:
0.0–3.3 s — phrase 1 "इस प्रकार केवल एक अमीनो अम्ल के परिवर्तन के कारण" pops on at the very top, fully sharp. The bead strand holds still and unchanged.
2.0–4.0 s — the bead strand with its "वेलिन" plate shrinks to about half size, drifts upward and fades out completely, gone by 4.0 s.
3.3–3.5 s — phrase 1 is fully gone; empty gap, no phrase on screen.
3.5–6.6 s — phrase 2 "सामान्य हीमोग्लोबिन HbA के स्थान पर" pops on at the very top, fully sharp.
4.2 s — exactly as the letters HbA are visible on screen inside phrase 2, the single equation line HbA → HbS pops on below the script text in large bold white with a soft cyan glow, fully sharp from its first visible frame, and holds its exact position to the end of the clip.
6.6–6.8 s — phrase 2 is fully gone; empty gap, no phrase on screen.
6.8–10.0 s — phrase 3 "HbS बनने लगता है।" pops on at the very top, fully sharp.
7.2 s — exactly as the letters HbS are visible on screen inside phrase 3, the letters HbS INSIDE the existing equation turn bright red and glow, staying exactly in their place inside the equation, and hold that glow to 10.0 s. HbA inside the equation stays white. No symbol is ever copied out of the equation.
10.0 s — clip ends with phrase 3 and the equation HbA → HbS on screen, HbS glowing red.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "इस प्रकार केवल एक अमीनो अम्ल के परिवर्तन के कारण"
2. "सामान्य हीमोग्लोबिन HbA के स्थान पर"
3. "HbS बनने लगता है।"
4. "वेलिन"
5. "HbA → HbS"

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, broken or reshaped Devanagari matras, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, invented labels, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, a new logo, a duplicated logo, a redrawn logo, a moved logo, a watermark of any kind, text or diagram overlapping either top corner, the equation appearing before 4.2 seconds, the bead strand fading before 2.0 seconds, the bead strand still visible after 4.0 seconds, a second label plate, a second "वेलिन", the green bead being the fifth or the seventh bead, more than one green bead, a bead being deleted or the strand becoming shorter, a copy of any letter taken out of the equation, a floating "HbA" or "HbS" anywhere outside the equation and the phrases, any label plate after 4.0 seconds, any chip, any callout, any leader line after 4.0 seconds, two copies of the equation, the equation moving or resizing, the equation stacked onto two lines, a golden word in any phrase, the casing HBA, HBS, Hba, Hbs or HgB, a red blood cell, a sickle cell, a DNA helix, an alpha chain being changed, any sphere, ball, cell, arrow, vessel, icon or illustration other than the carried-over bead strand, extra equations
```

---

## SEGMENT 10 OF 28 — DIAGRAM (normal RBC returns, oxygen drops)

```
VIDEO PROMPT — SEGMENT 10 OF 28

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

VOICEOVER NARRATION (spoken audio): an energetic, warm Indian male biology teacher voice speaks this exact Hinglish narration during the clip — nothing more, nothing less. The same script also appears on screen word for word, one phrase at a time:
"अब समस्या तब उत्पन्न होती है जब शरीर में ऑक्सीजन की मात्रा कम हो जाती है।"

AUDIO: only the voiceover above. No background music. Only very soft whoosh and pop sounds on text animations are allowed.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, starting close to the top edge. The diagram sits directly below the script text and fills the space between the text and the invisible middle line, so the top half never looks empty. The lowest part of the diagram stops with a clear visible gap above the invisible middle line and never touches it; if it does not fit, make it smaller. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

LOGO SAFE AREA: keep the top-left corner and the top-right corner of the frame completely clear of script text, diagram, equation, labels and any moving element for the whole clip — only the background itself shows there. Do not draw, copy, move, recreate or animate any logo, wordmark, badge or watermark anywhere in the frame; the logo already present on the supplied background must stay exactly where it is, unchanged.

3D RENDER QUALITY (CRITICAL — THIS MAKES THE DIAGRAM LOOK THREE DIMENSIONAL):
The diagram is a real three dimensional object rendered in depth, not a flat drawing.
- CAMERA: a fixed three-quarter view from slightly above the object, so the viewer looks slightly down at it and can clearly read its roundness. Never a flat straight-on front view.
- PERSPECTIVE: circles that run around the object appear as flattened ellipses because of the viewing angle, becoming flatter near the top and bottom and rounder near the middle. Nothing is drawn as a plain flat circle.
- DEPTH: the parts nearest the camera are brighter, thicker and sharper. The parts on the far side are noticeably dimmer, softer and smaller. This difference is clear and obvious.
- LIGHTING: one soft cool rim light along the upper left edge and a gentle ambient fill, giving a rounded sculpted look with a soft falloff toward the lower right.
- MATERIAL: a smooth glossy slightly waxy surface with a faint specular highlight near the upper left, and a soft inner glow.
- FORESHORTENING: any small sphere nearer the camera looks larger and sharper, and any sphere further away looks smaller and fainter. They are never all the same size on screen.
- MOTION: the object turns very slowly and steadily around its vertical axis so the depth reads clearly. It never wobbles, never squashes, never deforms and never changes size once settled.

DIAGRAM SPECIFICATION (build exactly this, nothing else):
- THE NORMAL RED BLOOD CELL: one large biconcave disc rendered in full three dimensions — circular seen from above, with a smooth shallow dimple pressed into BOTH faces, front and back, exactly like a doughnut that was never pierced. The centre is thinner and slightly paler ONLY because it is thinner, and there is NO hole, NO ring opening, NO gap and NO dark blob at the centre. It is uniformly red, a rich glossy haemoglobin red across its whole surface. It has NO nucleus and NO organelle of any kind inside it — nothing dark, nothing round and nothing separate is ever drawn at its centre. Its rim is thicker and rounded, catching the cool rim light along the upper left. It turns very slowly and steadily so the dimple on the near face and the thickness of the rim both read clearly. It never becomes flat, never becomes a ring, never becomes a bowl and never deforms.
- THE OXYGEN DOTS: small glossy blue three dimensional spheres scattered evenly in and around the red blood cell, some in front of it and some behind it, the nearer ones larger and sharper and the further ones smaller and fainter. They drift very gently. There are about sixteen of them when they first appear, and they fade away one by one until only two or three faint ones remain at the end of the clip. They never change colour, never merge into a blob and never form lines or chains.
LABELS: this clip has NO labels at all. Never invent a label.

DIAGRAM TIMING SYNC (CRITICAL): every object appears at the exact moment its name is visible in the written phrase on screen, and never a frame before. Once an object appears it stays to the end of the clip unless the timeline says it fades.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE. Every word appears exactly the number of times it is written.
- EXACT COUNT: the word "है" appears exactly TWICE in total in this clip — once at the end of the first phrase and once at the end of the second phrase. Nowhere else, in any size, at any moment.
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol, matra by matra. The Devanagari conjuncts and matras are rendered perfectly and are never broken, doubled or reshaped.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. In this clip the first phrase has exactly ONE golden key word: "समस्या". The second phrase has exactly ONE golden key word: "ऑक्सीजन". Each golden word is styled in place inside its own sentence and is never written again anywhere else, never on its own line, never as a label. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time, perfectly synced with the voiceover. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean, glossy, textbook-style biology illustration rendered in three dimensions — smooth shapes, flat bright colours, soft even glow, like a modern NCERT diagram built in 3D. Never photorealistic. NO fire, NO flame, NO burning, NO spark, NO ember, NO explosion, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: continuing exactly from the previous clip — the single line HbA → HbS sits below where the text will appear, sharp and still, with HbS glowing red. Nothing else.

ANIMATION TIMELINE:
0.0–4.8 s — phrase 1 "अब समस्या तब उत्पन्न होती है" pops on at the very top, fully sharp, with "समस्या" golden in place.
1.0–2.4 s — the line HbA → HbS shrinks slightly, drifts upward and fades out completely, gone by 2.4 s.
2.8 s — the normal red blood cell fades and scales in below the script text: a fully three dimensional biconcave disc, uniformly red, dimpled on both faces, no hole and no nucleus, and begins its very slow steady turn. It stays to the end of the clip.
4.8–5.0 s — phrase 1 is fully gone; empty gap, no phrase on screen.
5.0–10.0 s — phrase 2 "जब शरीर में ऑक्सीजन की मात्रा कम हो जाती है।" pops on at the very top, fully sharp, with "ऑक्सीजन" golden in place.
6.4 s — exactly as the word "ऑक्सीजन" is visible on screen inside phrase 2, about sixteen small glossy blue oxygen spheres pop in around and over the red blood cell, the nearer ones larger and sharper.
7.4–9.6 s — the blue oxygen spheres fade away one by one, steadily thinning out, until only two or three faint ones remain.
10.0 s — clip ends with phrase 2 on screen, the normal biconcave red blood cell still slowly turning, and only two or three faint blue oxygen spheres left around it.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "अब समस्या तब उत्पन्न होती है"
2. "जब शरीर में ऑक्सीजन की मात्रा कम हो जाती है।"

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, broken or reshaped Devanagari matras, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, invented labels, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, a new logo, a duplicated logo, a redrawn logo, a moved logo, a watermark of any kind, text or diagram overlapping either top corner, a red blood cell with a visible nucleus, a dark blob or dot drawn at the centre of the red blood cell, a red blood cell drawn as a flat two dimensional circle, a red blood cell drawn as a ring or doughnut with a hole through it, a bowl shaped cell dimpled on only one face, a blue or purple red blood cell, a sickle shaped cell, a crescent cell, a banana shaped cell, HbS fibres, any rod or fibre inside the cell, the red blood cell appearing before 2.8 seconds, the oxygen spheres appearing before 6.4 seconds, all the oxygen spheres disappearing at once, the oxygen spheres merging into a blob, the line HbA → HbS still visible after 2.4 seconds, a second red blood cell, any label plate, any chip, any callout, any leader line, any equation, any text inside the diagram, a golden word repeated outside its sentence, a straight-on front view with no depth, a diagram that looks like a flat line drawing, a squashed or wobbling cell
```

---

## SEGMENT 11 OF 28 — DIAGRAM (HbS molecules polymerise into fibres)

```
VIDEO PROMPT — SEGMENT 11 OF 28

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

VOICEOVER NARRATION (spoken audio): an energetic, warm Indian male biology teacher voice speaks this exact Hinglish narration during the clip — nothing more, nothing less. The same script also appears on screen word for word, one phrase at a time:
"ऐसी स्थिति में HbS के अणु आपस में जुड़कर लंबी रेशेदार संरचनाएँ बना लेते हैं।"

AUDIO: only the voiceover above. No background music. Only very soft whoosh and pop sounds on text animations are allowed.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, starting close to the top edge. The diagram sits directly below the script text and fills the space between the text and the invisible middle line, so the top half never looks empty. The lowest part of the diagram stops with a clear visible gap above the invisible middle line and never touches it; if it does not fit, make it smaller. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

LOGO SAFE AREA: keep the top-left corner and the top-right corner of the frame completely clear of script text, diagram, equation, labels and any moving element for the whole clip — only the background itself shows there. Do not draw, copy, move, recreate or animate any logo, wordmark, badge or watermark anywhere in the frame; the logo already present on the supplied background must stay exactly where it is, unchanged.

3D RENDER QUALITY (CRITICAL — THIS MAKES THE DIAGRAM LOOK THREE DIMENSIONAL):
The diagram is a real three dimensional object rendered in depth, not a flat drawing.
- CAMERA: a fixed three-quarter view from slightly above the object, so the viewer looks slightly down at it and can clearly read its roundness. Never a flat straight-on front view.
- PERSPECTIVE: circles that run around the object appear as flattened ellipses because of the viewing angle, becoming flatter near the top and bottom and rounder near the middle. Nothing is drawn as a plain flat circle.
- DEPTH: the parts nearest the camera are brighter, thicker and sharper. The parts on the far side, seen through the slightly translucent surface, are noticeably dimmer, thinner and softer. This difference is clear and obvious.
- LIGHTING: one soft cool rim light along the upper left edge and a gentle ambient fill, giving a rounded sculpted look with a soft falloff toward the lower right.
- MATERIAL: a smooth glossy slightly waxy surface with a faint specular highlight near the upper left, and a soft inner glow.
- FORESHORTENING: any fibre pointing toward the camera looks shorter and thicker, and any fibre pointing away looks longer and thinner. They are never all the same length on screen.
- MOTION: the object turns very slowly and steadily around its vertical axis so the depth reads clearly. It never wobbles, never squashes, never deforms and never changes size once settled.

DIAGRAM SPECIFICATION (build exactly this, nothing else):
- THE RED BLOOD CELL: the same large biconcave disc carried over from the previous clip, rendered in full three dimensions — circular seen from above, with a smooth shallow dimple pressed into BOTH faces, front and back. The centre is thinner and slightly paler ONLY because it is thinner, and there is NO hole, NO ring opening and NO dark blob at the centre. It is uniformly rich glossy red, has NO nucleus and NO organelle of any kind inside it, and its surface is slightly translucent so the contents inside can be seen. Throughout THIS clip it KEEPS its normal biconcave disc shape and does NOT change shape at any moment. It turns very slowly and steadily.
- THE OXYGEN DOTS: only two or three small faint glossy blue spheres remain, carried over from the previous clip, drifting very gently near the cell. No new oxygen spheres are ever added.
- THE HbS MOLECULES: small deep blue-violet three dimensional beads that appear scattered inside the translucent red cell, the nearer ones larger and sharper and the further ones smaller and fainter. They drift slowly toward each other and link up end to end.
- THE FIBRES: the linked HbS beads form about five LONG STRAIGHT RIGID rods of beads inside the cell, deep blue-violet, running roughly parallel to one another across the inside of the cell, clearly visible through the translucent red surface, the near-side rods brighter and thicker and the far-side rods dimmer and thinner. They are straight and stiff — never curled, never coiled, never wavy, never tangled and never crossing each other. They stay entirely inside the cell and never pierce or stretch its surface in this clip.
LABELS: this clip has NO labels at all. Never invent a label.

DIAGRAM TIMING SYNC (CRITICAL): every object appears at the exact moment its name is visible in the written phrase on screen, and never a frame before. The diagram carried over from the previous clip is already present at the very first frame and does not fade in again. Once an object appears it stays to the end of the clip.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE beyond what is written. In the first phrase the word "में" is written exactly TWICE as given — it appears exactly twice there and never a third time anywhere in this clip, in any size, at any moment.
- EXACT COUNT: the text "HbS" appears exactly ONCE in total in this clip — inside the first phrase only. Nowhere else, in any size, at any moment. There is no "HbS" on the diagram, no "HbS" label and no floating "HbS".
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol, matra by matra. The Devanagari conjuncts and matras are rendered perfectly and are never broken, doubled or reshaped.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. In this clip the FIRST phrase is rendered COMPLETELY UNIFORM in bold white with NO golden word, because it contains Latin letters and the same word twice. The SECOND phrase has exactly ONE golden key word: "रेशेदार", styled in place inside the sentence and never written again anywhere else. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time, perfectly synced with the voiceover. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean, glossy, textbook-style biology illustration rendered in three dimensions — smooth shapes, flat bright colours, soft even glow, like a modern NCERT diagram built in 3D. Never photorealistic. NO fire, NO flame, NO burning, NO spark, NO ember, NO explosion, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: continuing exactly from the previous clip — the normal biconcave red blood cell sits below where the text will appear, uniformly red, dimpled on both faces, turning very slowly, with only two or three faint blue oxygen spheres drifting around it. Nothing else.

ANIMATION TIMELINE:
0.0–4.8 s — phrase 1 "ऐसी स्थिति में HbS के अणु आपस में जुड़कर" pops on at the very top, fully sharp, COMPLETELY UNIFORM white. The red blood cell holds its biconcave shape and keeps turning slowly.
1.6 s — exactly as the letters HbS are visible on screen inside phrase 1, about twenty small deep blue-violet HbS beads pop in scattered inside the translucent red cell, the nearer ones larger and sharper.
3.2–4.6 s — the blue-violet beads drift slowly toward each other and begin linking end to end into short bead chains inside the cell.
4.8–5.0 s — phrase 1 is fully gone; empty gap, no phrase on screen.
5.0–10.0 s — phrase 2 "लंबी रेशेदार संरचनाएँ बना लेते हैं।" pops on at the very top, fully sharp, with "रेशेदार" golden in place.
5.6–7.6 s — exactly as the word "रेशेदार" is visible on screen inside phrase 2, the bead chains join into about five LONG STRAIGHT RIGID rods running roughly parallel across the inside of the cell, clearly visible through the translucent red surface, near-side rods brighter and thicker, far-side rods dimmer and thinner. They never curl, coil, wave, tangle or cross.
7.6–10.0 s — the fibres hold still and glossy inside the cell. The cell keeps its normal biconcave disc shape and continues turning very slowly.
10.0 s — clip ends with phrase 2 on screen, the still-biconcave red blood cell slowly turning with the long straight blue-violet fibres linked inside it.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "ऐसी स्थिति में HbS के अणु आपस में जुड़कर"
2. "लंबी रेशेदार संरचनाएँ बना लेते हैं।"

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, broken or reshaped Devanagari matras, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word beyond what is written, a repeated key word, a keyword written as a separate line, invented labels, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, a new logo, a duplicated logo, a redrawn logo, a moved logo, a watermark of any kind, text or diagram overlapping either top corner, a red blood cell with a visible nucleus, a dark blob or dot drawn at the centre of the red blood cell, a red blood cell drawn as a flat two dimensional circle, a red blood cell drawn as a ring or doughnut with a hole through it, a bowl shaped cell dimpled on only one face, a blue or purple red blood cell, the cell changing shape in this clip, the cell becoming a sickle or crescent or banana in this clip, the cell becoming pointed, curled coiled wavy or tangled fibres, fibres crossing each other, fibres piercing or bursting through the cell surface, fibres appearing outside the cell, the HbS beads appearing before 1.6 seconds, the fibres forming before 5.6 seconds, new oxygen spheres being added, the oxygen spheres increasing in number, a second red blood cell, any label plate, any chip, any callout, any leader line, any equation, a floating "HbS" anywhere outside the first phrase, any text inside the diagram, a golden word in the first phrase, a golden word repeated outside its sentence, a straight-on front view with no depth, a diagram that looks like a flat line drawing, a squashed or wobbling cell
```

---

## SEGMENT 12 OF 28 — DIAGRAM (biconcave → sickle)

```
VIDEO PROMPT — SEGMENT 12 OF 28

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

VOICEOVER NARRATION (spoken audio): an energetic, warm Indian male biology teacher voice speaks this exact Hinglish narration during the clip — nothing more, nothing less. The same script also appears on screen word for word, one phrase at a time:
"इसके कारण लाल रक्त कोशिका का सामान्य द्विअवतल आकार बदलकर हँसिए के आकार का हो जाता है।"

AUDIO: only the voiceover above. No background music. Only very soft whoosh and pop sounds on text animations are allowed.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, starting close to the top edge. The diagram sits directly below the script text and fills the space between the text and the invisible middle line, so the top half never looks empty. The lowest part of the diagram stops with a clear visible gap above the invisible middle line and never touches it; if it does not fit, make it smaller. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

LOGO SAFE AREA: keep the top-left corner and the top-right corner of the frame completely clear of script text, diagram, equation, labels and any moving element for the whole clip — only the background itself shows there. Do not draw, copy, move, recreate or animate any logo, wordmark, badge or watermark anywhere in the frame; the logo already present on the supplied background must stay exactly where it is, unchanged.

3D RENDER QUALITY (CRITICAL — THIS MAKES THE DIAGRAM LOOK THREE DIMENSIONAL):
The diagram is a real three dimensional object rendered in depth, not a flat drawing.
- CAMERA: a fixed three-quarter view from slightly above the object, so the viewer looks slightly down at it and can clearly read its roundness. Never a flat straight-on front view.
- PERSPECTIVE: circles that run around the object appear as flattened ellipses because of the viewing angle, becoming flatter near the top and bottom and rounder near the middle. Nothing is drawn as a plain flat circle.
- DEPTH: the parts nearest the camera are brighter, thicker and sharper. The parts on the far side, seen through the slightly translucent surface, are noticeably dimmer, thinner and softer. This difference is clear and obvious.
- LIGHTING: one soft cool rim light along the upper left edge and a gentle ambient fill, giving a rounded sculpted look with a soft falloff toward the lower right.
- MATERIAL: a smooth glossy slightly waxy surface with a faint specular highlight near the upper left, and a soft inner glow.
- FORESHORTENING: any fibre pointing toward the camera looks shorter and thicker, and any fibre pointing away looks longer and thinner. They are never all the same length on screen.
- MOTION: the object turns very slowly and steadily around its vertical axis so the depth reads clearly. It never wobbles, never squashes and never changes size once settled. The only shape change in this clip is the single deliberate morph described in the timeline.

DIAGRAM SPECIFICATION (build exactly this, nothing else):
- THE CELL BEFORE THE CHANGE: the same large biconcave disc carried over from the previous clip, rendered in full three dimensions — circular seen from above, with a smooth shallow dimple pressed into BOTH faces, front and back, no hole, no ring opening, no dark blob at the centre, no nucleus and no organelle of any kind inside it. It is uniformly rich glossy red with a slightly translucent surface.
- THE FIBRES: about five LONG STRAIGHT RIGID rods of deep blue-violet beads carried over from the previous clip, running roughly parallel across the inside of the cell, visible through the translucent red surface, near-side rods brighter and thicker and far-side rods dimmer and thinner. They are straight and stiff — never curled, never coiled, never wavy, never tangled and never crossing each other. As the shape changes they lengthen and align along the long axis of the new shape, still straight and still inside the cell.
- THE OXYGEN DOTS: only two or three small faint glossy blue spheres remain, carried over from the previous clip, drifting very gently near the cell. No new oxygen spheres are ever added.
- THE CELL AFTER THE CHANGE: a SICKLE shaped cell — a true crescent that is SHARPLY POINTED at BOTH ends, with one clearly concave inner edge and one clearly convex outer edge, thick and rounded in the middle and tapering to fine points at the two tips. It stays the same rich glossy red, keeps its slightly translucent surface, still has NO nucleus and NO hole, and turns very slowly and steadily. It is never a smooth banana with blunt rounded ends, never a crescent moon with rounded tips, never a star, never spiky and never lumpy.
LABELS: this clip has NO labels at all. Never invent a label.

DIAGRAM TIMING SYNC (CRITICAL): the diagram carried over from the previous clip is already present at the very first frame and does not fade in again. The shape change begins at the exact moment the word naming the sickle shape is visible in the written phrase on screen, and never a frame before.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE. Every word appears exactly the number of times it is written.
- EXACT COUNT: the word "आकार" appears exactly TWICE in total in this clip — once at the end of the first phrase and once inside the second phrase. Nowhere else, in any size, at any moment.
- EXACT COUNT: the word "का" appears exactly TWICE in total in this clip — once inside the first phrase and once inside the second phrase. Nowhere else, in any size, at any moment.
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol, matra by matra. The Devanagari conjuncts and matras, including the chandrabindu in "हँसिए" and the conjunct in "द्विअवतल", are rendered perfectly and are never broken, doubled or reshaped.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. In this clip BOTH phrases are rendered COMPLETELY UNIFORM in bold white with NO golden word anywhere, because words are shared between the two phrases. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear. The word "morph" applies ONLY to the cell shape described in the timeline and NEVER to any text.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time, perfectly synced with the voiceover. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean, glossy, textbook-style biology illustration rendered in three dimensions — smooth shapes, flat bright colours, soft even glow, like a modern NCERT diagram built in 3D. Never photorealistic. NO fire, NO flame, NO burning, NO spark, NO ember, NO explosion, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: continuing exactly from the previous clip — the normal biconcave red blood cell sits below where the text will appear, turning very slowly, with about five long straight deep blue-violet fibres linked inside it and only two or three faint blue oxygen spheres drifting nearby. Nothing else.

ANIMATION TIMELINE:
0.0–4.8 s — phrase 1 "इसके कारण लाल रक्त कोशिका का सामान्य द्विअवतल आकार" pops on at the very top, fully sharp, COMPLETELY UNIFORM white. The cell holds its normal biconcave shape, dimple visible on the near face, turning very slowly.
4.8–5.0 s — phrase 1 is fully gone; empty gap, no phrase on screen.
5.0–10.0 s — phrase 2 "बदलकर हँसिए के आकार का हो जाता है।" pops on at the very top, fully sharp, COMPLETELY UNIFORM white.
5.6–7.8 s — exactly as the word "हँसिए" is visible on screen inside phrase 2, the cell changes shape ONCE, smoothly and continuously: the straight blue-violet fibres inside lengthen and align along one axis, pushing the cell outward from within, and the round biconcave disc is drawn out into a SICKLE — a true crescent, sharply pointed at BOTH ends, one concave inner edge, one convex outer edge, thick in the middle and tapering to fine points at the two tips. It stays the same rich glossy red throughout and never changes colour, never gains a nucleus and never gains a hole. This is the only shape change in the clip.
7.8–10.0 s — the sickle cell settles at its final size and turns very slowly and steadily, its straight blue-violet fibres visible inside through the translucent red surface. The two or three faint oxygen spheres keep drifting gently nearby.
10.0 s — clip ends with phrase 2 on screen and the sickle cell slowly turning, fibres inside.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "इसके कारण लाल रक्त कोशिका का सामान्य द्विअवतल आकार"
2. "बदलकर हँसिए के आकार का हो जाता है।"

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, broken or reshaped Devanagari matras, a missing or doubled chandrabindu in "हँसिए", fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, invented labels, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, a new logo, a duplicated logo, a redrawn logo, a moved logo, a watermark of any kind, text or diagram overlapping either top corner, a red blood cell with a visible nucleus, a dark blob or dot drawn at the centre of the cell, a cell drawn as a flat two dimensional circle, a cell drawn as a ring or doughnut with a hole through it, a bowl shaped cell dimpled on only one face, a blue or purple cell, a sickle cell shaped like a smooth banana with rounded ends, a crescent with blunt tips, a star shaped cell, a spiky cell, a lumpy or blobby cell, a sickle cell with only one pointed end, the shape change starting before 5.6 seconds, the cell changing shape more than once, the cell flipping back to a disc after the change, two cells on screen, a second sickle cell, a field of many cells, curled coiled wavy or tangled fibres, fibres crossing each other, fibres piercing or bursting through the cell surface, fibres appearing outside the cell, new oxygen spheres being added, any label plate, any chip, any callout, any leader line, any equation, any text inside the diagram, a golden word in either phrase, a straight-on front view with no depth, a diagram that looks like a flat line drawing, a squashed or wobbling cell
```

---

**Notes:**
- **Fibre colour deviation** (flagged above) — say the word and I'll flip Segs 11–12 back to red fibres, but it will lose contrast against the red cell.
- **Seg 9 `Hb` risk** is the highest in this batch: `Hb` appears four times legitimately (two phrases + two sides of the equation). The three stacked EXACT COUNT lines are load-bearing — don't trim them.
- **Seg 12** is the only clip in the pack with a deliberate shape morph, which is why the TEXT ENTRY rule there carries the extra sentence quarantining the word "morph" to the cell only.
- Test **Seg 12** first, not Seg 9 — the sickle morph plus `हँसिए` chandrabindu is where this batch is most likely to break.

Frames read — they lock the visual language I'll use: crescent with **pointed ends** (not banana), **blue-violet HbS fibre bundles inside the red cell**, translucent grey capillary tube, white rounded label plates with dark bold text + thin leader line.

⚠️ **One assumption flagged:** your plan's Seg-11 end-state says "long **red** HbS fibres", but both reference frames draw the fibres **blue** (red-on-red is invisible). I've written Segs 13–16 with **deep blue-violet fibres** to match the reference art. If Segs 11–12 were already generated with red fibres, tell me and I'll swap the colour word — it appears in one bullet per segment.

---

## Segment 13

```
VIDEO PROMPT — SEGMENT 13 OF 28

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

VOICEOVER NARRATION (spoken audio): an energetic, warm Indian male biology teacher voice speaks this exact Hinglish narration during the clip — nothing more, nothing less. The same script also appears on screen word for word, one phrase at a time:
"इसी कारण इस रोग को सिकल सेल एनीमिया कहा जाता है।"

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
- THE SICKLE CELL: one single red blood cell rendered in full three dimensions, already present at the very first frame, carried over unchanged from the previous clip. It is a crescent shape — a sickle — with a smooth concave inner edge and a smooth convex outer edge, and BOTH ends drawn as clear sharp points, tapering to fine tips. It is deep red with a glossy rounded surface, a soft cool rim light along its upper left edge and a faint specular highlight. It is NOT a banana, NOT a crescent moon with blunt or rounded ends, NOT a star, NOT spiky, NOT a bowl, NOT a ring and NOT a doughnut with a hole. It has NO nucleus and no dark central blob of any kind — there is no organelle inside it. It turns very slowly and steadily around its vertical axis and never wobbles, never deforms, never changes shape and never changes size during this clip.
- THE HbS FIBRES: several long straight rigid rod-like fibres in deep blue-violet, already present at the very first frame, lying inside the sickle cell and running lengthwise along its long curved axis, packed as a neat parallel bundle and clearly visible through the translucent red surface. They are perfectly straight and stiff — never wavy, never tangled, never crossing each other. They turn together with the cell as one solid piece and never move independently.
- THE LABEL: exactly ONE label exists in this clip — a small white rounded plate with dark bold letters reading "सिकल सेल एनीमिया", joined to the sickle cell by one short thin white leader line, drawn as a flat overlay in front of the three dimensional scene. It appears only at the time given in the timeline. No other plate, chip, tag, number or floating letter exists anywhere.

DIAGRAM TIMING SYNC (CRITICAL): every object appears at the exact moment its name is visible in the written phrase on screen, and never a frame before. Once an object appears it stays to the end of the clip. The diagram carried over from the previous clip is already present at the very first frame and does not fade in again.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE. Every word appears exactly the number of times it is written.
- EXACT COUNT: the words "सिकल सेल एनीमिया" appear exactly TWICE in total in this clip — once inside the second phrase and once inside the single label plate. Nowhere else, in any size, at any moment.
- EXACT COUNT: exactly ONE label plate exists in this whole clip. There is never a second plate, a second leader line, or a second copy of the label text.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol, including every matra and every chandrabindu in the Devanagari.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated. In this clip: the FIRST phrase has exactly ONE golden key word — "रोग" — and nothing else is golden in it. The SECOND phrase is rendered COMPLETELY UNIFORM in bold white with NO golden word at all, because its words also appear on the label plate.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time, perfectly synced with the voiceover. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean, glossy, textbook-style biology illustration rendered in three dimensions — smooth shapes, flat bright colours, soft even glow, like a modern NCERT diagram built in 3D. Never photorealistic. NO fire, NO flame, NO burning, NO spark, NO ember, NO explosion, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: continuing exactly from the previous clip — the single red sickle-shaped cell with sharp pointed ends and the straight blue-violet fibre bundle inside it, sitting below where the text will appear, turning very slowly. Nothing else.

ANIMATION TIMELINE:
- 0.0 s: the sickle cell with its fibres is already on screen from the previous clip, mid-turn, and does not fade in again. The first phrase "इसी कारण इस रोग को" pops in fully sharp at the very top of the frame, with the word "रोग" golden inside the sentence.
- 0.0 to 4.8 s: the first phrase holds. The sickle cell keeps its slow steady turn.
- 4.8 s: the first phrase disappears completely.
- 4.8 to 5.0 s: a tiny gap with no phrase on screen.
- 5.0 s: the second phrase "सिकल सेल एनीमिया कहा जाता है।" pops in fully sharp, completely uniform bold white.
- 7.5 s, exactly while the words "सिकल सेल एनीमिया" are visible on screen inside the second phrase, the single white rounded label plate reading "सिकल सेल एनीमिया" pops in beside the cell, joined to it by one short thin white leader line, and holds to the end.
- 7.5 to 10.0 s: the second phrase, the sickle cell and the one label all hold. The cell continues its slow steady turn. Nothing else appears.
- 10.0 s: clip ends.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "इसी कारण इस रोग को"
2. "सिकल सेल एनीमिया कहा जाता है।"
3. "सिकल सेल एनीमिया"

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, invented labels, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, missing matras, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, a new logo, a duplicated logo, a redrawn logo, a moved logo, a watermark of any kind, text or diagram overlapping either top corner, a flat two dimensional drawing instead of a three dimensional cell, a straight-on front view with no depth, a diagram that looks like a flat line drawing, a red blood cell with a visible nucleus, a dark blob or organelle inside the cell, a red blood cell drawn as a ring or a doughnut with a hole in the middle, a flat circle instead of a rounded three dimensional cell, a sickle cell shaped like a smooth banana, a sickle cell with blunt or rounded ends, a crescent moon shape with rounded tips, a star shaped cell, a spiky cell, a blue or purple red blood cell, wavy or tangled fibres, fibres that cross each other, the cell changing shape during this clip, a second red blood cell, a normal biconcave cell in this clip, the label appearing before 7.5 seconds, a second label plate, a second "सिकल सेल एनीमिया", a third copy of the words सिकल सेल एनीमिया, a golden word in the second phrase, equations, DNA, chromosomes, blood vessels, oxygen dots
```

---

## Segment 14

```
VIDEO PROMPT — SEGMENT 14 OF 28

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

VOICEOVER NARRATION (spoken audio): an energetic, warm Indian male biology teacher voice speaks this exact Hinglish narration during the clip — nothing more, nothing less. The same script also appears on screen word for word, one phrase at a time:
"हँसिए के आकार की लाल रक्त कोशिकाएँ कठोर और कम लचीली हो जाती हैं।"

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
- THE SICKLE CELL: one single red blood cell rendered in full three dimensions, already present at the very first frame, carried over unchanged from the previous clip. It is a crescent shape — a sickle — with a smooth concave inner edge and a smooth convex outer edge, and BOTH ends drawn as clear sharp points, tapering to fine tips. It is deep red with a glossy rounded surface, a soft cool rim light along its upper left edge and a faint specular highlight. It is NOT a banana, NOT a crescent moon with blunt or rounded ends, NOT a star, NOT spiky, NOT a bowl, NOT a ring and NOT a doughnut with a hole. It has NO nucleus and no dark central blob of any kind. It turns very slowly and steadily around its vertical axis and never wobbles, never deforms and never changes size.
- THE HbS FIBRES: several long straight rigid rod-like fibres in deep blue-violet, already present at the very first frame, lying inside the sickle cell and running lengthwise along its long curved axis as a neat parallel bundle, clearly visible through the translucent red surface. They are perfectly straight and stiff — never wavy, never tangled, never crossing each other. They turn together with the cell as one solid piece.
- THE RIGID LOOK: during this clip the outline of the sickle cell becomes visibly harder and stiffer — its edge sharpens into a crisp firm hard rim with a slightly cooler, harder sheen, and the whole cell reads as a stiff solid object. It becomes completely rigid: it does not bend, does not flex, does not ripple, does not squash and does not wobble at any moment. Its shape and its size stay exactly the same; only the hardness of the edge and the sheen change. This is a change of surface look only, never a change of form.
- LABELS: this clip has NO labels at all. The label plate from the previous clip and its leader line fade away smoothly and completely by 2.0 seconds and never return. After 2.0 seconds there is no plate, no chip, no tag, no floating letter and no leader line anywhere in the frame. Never invent a label.

DIAGRAM TIMING SYNC (CRITICAL): every object appears at the exact moment its name is visible in the written phrase on screen, and never a frame before. Once an object appears it stays to the end of the clip. The diagram carried over from the previous clip is already present at the very first frame and does not fade in again.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE. Every word appears exactly the number of times it is written.
- This clip has NO label plates at all after 2.0 seconds. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- The label carried over from the previous clip reads "सिकल सेल एनीमिया" and appears exactly ONCE, only until it has fully faded by 2.0 seconds. It is never duplicated and never redrawn.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol, including every matra and every chandrabindu in the Devanagari.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated. In this clip: the FIRST phrase has exactly ONE golden key word — "आकार" — and nothing else is golden in it. The SECOND phrase has exactly ONE golden key word — "कठोर" — and nothing else is golden in it.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time, perfectly synced with the voiceover. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean, glossy, textbook-style biology illustration rendered in three dimensions — smooth shapes, flat bright colours, soft even glow, like a modern NCERT diagram built in 3D. Never photorealistic. NO fire, NO flame, NO burning, NO spark, NO ember, NO explosion, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: continuing exactly from the previous clip — the single red sickle-shaped cell with sharp pointed ends and the straight blue-violet fibre bundle inside it, turning very slowly, with the white rounded label plate reading "सिकल सेल एनीमिया" still attached to it by its short thin white leader line. Nothing else.

ANIMATION TIMELINE:
- 0.0 s: the sickle cell with its fibres and the carried-over label are already on screen from the previous clip and do not fade in again. The first phrase "हँसिए के आकार की लाल रक्त कोशिकाएँ" pops in fully sharp at the very top of the frame, with the word "आकार" golden inside the sentence.
- 0.0 to 2.0 s: the carried-over label plate and its leader line fade away smoothly and are completely gone by 2.0 seconds. The sickle cell keeps its slow steady turn.
- 0.0 to 4.8 s: the first phrase holds.
- 4.8 s: the first phrase disappears completely.
- 4.8 to 5.0 s: a tiny gap with no phrase on screen.
- 5.0 s: the second phrase "कठोर और कम लचीली हो जाती हैं।" pops in fully sharp, with the word "कठोर" golden inside the sentence.
- 5.4 to 6.6 s, exactly while the word "कठोर" is visible on screen, the outline of the sickle cell hardens: its edge sharpens into a crisp firm hard rim with a slightly cooler harder sheen, and it holds that hard rigid look to the end. Its shape and size do not change at all.
- 6.6 to 10.0 s: the second phrase and the rigid sickle cell hold. The cell continues its slow steady turn, completely stiff, with no bending, flexing, rippling or wobbling. Nothing else appears.
- 10.0 s: clip ends.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "हँसिए के आकार की लाल रक्त कोशिकाएँ"
2. "कठोर और कम लचीली हो जाती हैं।"

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, invented labels, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, missing matras, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, a new logo, a duplicated logo, a redrawn logo, a moved logo, a watermark of any kind, text or diagram overlapping either top corner, any label plate after 2.0 seconds, a new label plate, a label reappearing, a second leader line, a flat two dimensional drawing instead of a three dimensional cell, a straight-on front view with no depth, a red blood cell with a visible nucleus, a dark blob or organelle inside the cell, a red blood cell drawn as a ring or a doughnut with a hole in the middle, a sickle cell shaped like a smooth banana, a sickle cell with blunt or rounded ends, a crescent moon shape with rounded tips, a star shaped cell, a spiky cell, a blue or purple red blood cell, the cell bending, the cell flexing, the cell squashing, the cell rippling, the cell changing shape, the cell changing size, wavy or tangled fibres, fibres that cross each other, a second red blood cell, a normal biconcave cell in this clip, equations, DNA, chromosomes, blood vessels, oxygen dots
```

---

## Segment 15

```
VIDEO PROMPT — SEGMENT 15 OF 28

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

VOICEOVER NARRATION (spoken audio): an energetic, warm Indian male biology teacher voice speaks this exact Hinglish narration during the clip — nothing more, nothing less. The same script also appears on screen word for word, one phrase at a time:
"इसलिए ये छोटी रक्त वाहिकाओं में फँस सकती हैं, जिससे रक्त का प्रवाह बाधित हो जाता है"

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
- THE CAPILLARY: one narrow horizontal tube rendered in full three dimensions, running across the frame below the script text, made of pale translucent grey glass with a soft cool rim light along its upper left edge and a faint specular highlight. Its open circular ends appear as flattened ellipses because of the three-quarter viewing angle. The tube narrows visibly toward its right side. It is see-through, so everything inside it is clearly visible. It is fixed in place, never rotates, never bends and never changes size once settled.
- THE THREE SICKLE CELLS: exactly THREE red sickle-shaped cells inside the tube, each a crescent with a smooth concave inner edge, a smooth convex outer edge and BOTH ends drawn as clear sharp points tapering to fine tips. Each is deep red, glossy and rounded, with a crisp hard rigid rim, and each carries the same straight blue-violet fibre bundle running lengthwise inside it, clearly visible through the translucent red surface. They are completely rigid — they never bend, never flex, never squash and never change shape as they move. They wedge and jam against each other at the narrow part of the tube and stop there, stacked at an angle, blocking it completely.
- THE HALTED FLOW: behind the jam, on the left side of the tube, a few small rounded deep-red cells and a gentle pale flow are moving to the right; they slow down and come to a complete stop against the block and then stay perfectly still. On the right side of the tube, downstream of the jam, the tube is empty and pale — no cells and no flow move there at all. Every one of these small cells is a plain smooth rounded biconcave disc, deep red, with no nucleus and no dark centre spot.
- LABELS: this clip has NO labels at all. No plate, no chip, no tag, no floating letter, no leader line and no stray symbol appears anywhere at any moment. Never invent a label.

DIAGRAM TIMING SYNC (CRITICAL): every object appears at the exact moment its name is visible in the written phrase on screen, and never a frame before. Once an object appears it stays to the end of the clip.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE. Every word appears exactly the number of times it is written.
- EXACT COUNT: the word "रक्त" appears exactly TWICE in total in this clip — once inside the first phrase and once inside the second phrase. Nowhere else, in any size, at any moment, and never twice inside the same phrase.
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol, including every matra and every chandrabindu in the Devanagari.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated. In this clip: BOTH phrases are rendered COMPLETELY UNIFORM in bold white with NO golden word anywhere, because the word "रक्त" is shared between them.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time, perfectly synced with the voiceover. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean, glossy, textbook-style biology illustration rendered in three dimensions — smooth shapes, flat bright colours, soft even glow, like a modern NCERT diagram built in 3D. Never photorealistic. NO fire, NO flame, NO burning, NO spark, NO ember, NO explosion, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: continuing exactly from the previous clip — the single rigid red sickle-shaped cell with sharp pointed ends and the straight blue-violet fibre bundle inside it, sitting alone below where the text will appear. Nothing else.

ANIMATION TIMELINE:
- 0.0 s: the rigid sickle cell from the previous clip is already on screen and does not fade in again. The first phrase "इसलिए ये छोटी रक्त वाहिकाओं में फँस सकती हैं," pops in fully sharp at the very top of the frame, completely uniform bold white.
- 1.2 s, exactly while the words "रक्त वाहिकाओं" are visible on screen, the narrow translucent grey capillary tube fades in around the sickle cell, running horizontally and narrowing toward its right side, and holds to the end.
- 2.2 s, exactly while the word "फँस" is visible on screen, two more identical rigid sickle cells slide in from the left inside the tube, joining the first one, so there are now exactly THREE sickle cells in total. All three drift right, wedge against each other at the narrow part of the tube and come to a complete stop by 4.0 seconds, jamming it. They stay stacked and perfectly still to the end.
- 0.0 to 4.8 s: the first phrase holds.
- 4.8 s: the first phrase disappears completely.
- 4.8 to 5.0 s: a tiny gap with no phrase on screen.
- 5.0 s: the second phrase "जिससे रक्त का प्रवाह बाधित हो जाता है" pops in fully sharp, completely uniform bold white.
- 5.6 to 7.2 s, exactly while the words "रक्त का प्रवाह" are visible on screen, a few small smooth rounded deep-red biconcave cells and a gentle pale flow move rightward along the left part of the tube, slow down against the jam and come to a complete stop, then stay perfectly still to the end. The tube to the right of the jam stays empty and pale, with nothing moving in it at any moment.
- 7.2 to 10.0 s: the second phrase, the tube, the three jammed sickle cells and the halted flow all hold, completely still. Nothing else appears.
- 10.0 s: clip ends.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "इसलिए ये छोटी रक्त वाहिकाओं में फँस सकती हैं,"
2. "जिससे रक्त का प्रवाह बाधित हो जाता है"

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, invented labels, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, missing matras, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, a new logo, a duplicated logo, a redrawn logo, a moved logo, a watermark of any kind, text or diagram overlapping either top corner, any label plate, any chip, any callout, any leader line, a golden word in either phrase, a flat two dimensional drawing instead of a three dimensional scene, a straight-on front view with no depth, a red blood cell with a visible nucleus, a dark blob or organelle inside any cell, a red blood cell drawn as a ring or a doughnut with a hole in the middle, a sickle cell shaped like a smooth banana, a sickle cell with blunt or rounded ends, a crescent moon shape with rounded tips, a star shaped cell, a spiky cell, a blue or purple red blood cell, a sickle cell bending or flexing to squeeze through the tube, a sickle cell passing through the narrow part, a fourth sickle cell, only two sickle cells, every cell in the tube drawn as a sickle cell, blood continuing to flow past the block, flow moving on the right side of the jam, the tube bending or moving, the capillary appearing before 1.2 seconds, the extra sickle cells appearing before 2.2 seconds, equations, DNA, chromosomes, oxygen dots
```

---

## Segment 16

```
VIDEO PROMPT — SEGMENT 16 OF 28

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

VOICEOVER NARRATION (spoken audio): an energetic, warm Indian male biology teacher voice speaks this exact Hinglish narration during the clip — nothing more, nothing less. The same script also appears on screen word for word, one phrase at a time:
"और शरीर के ऊतकों तक पर्याप्त ऑक्सीजन नहीं पहुँच पाती।"

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
- THE CAPILLARY: one narrow horizontal tube rendered in full three dimensions, already present at the very first frame, carried over unchanged from the previous clip — pale translucent grey glass, narrowing toward its right side, with a soft cool rim light along its upper left edge, its open circular ends appearing as flattened ellipses. It is fixed in place, never rotates, never bends and never changes size.
- THE THREE JAMMED SICKLE CELLS: exactly THREE red sickle-shaped cells, already present at the very first frame, wedged and stacked against each other at the narrow part of the tube, completely still. Each is a crescent with a smooth concave inner edge, a smooth convex outer edge and BOTH ends drawn as clear sharp points tapering to fine tips, deep red and glossy with a crisp hard rigid rim, each carrying the same straight blue-violet fibre bundle running lengthwise inside it. They never bend, never flex, never move and never change shape during this clip.
- THE HALTED FLOW: behind the jam, on the left of the tube, a few small smooth rounded deep-red biconcave cells sit completely still against the block, already present at the very first frame. Each has no nucleus and no dark centre spot. Downstream of the jam, on the right of the tube, nothing moves at any moment.
- THE TISSUE PATCH: one rounded soft-edged patch of body tissue rendered in three dimensions, sitting just beyond the right end of the tube, downstream of the block, made of a few smooth rounded cell shapes clustered together with a gentle glossy surface. It starts warm healthy pink. During this clip it drains of colour and turns a dull desaturated grey-blue, dimming slightly, and holds that greyed look to the end. It never changes shape, never moves and never leaves its place.
- LABELS: this clip has NO labels at all. No plate, no chip, no tag, no floating letter, no leader line and no stray symbol appears anywhere at any moment. Never invent a label.

DIAGRAM TIMING SYNC (CRITICAL): every object appears at the exact moment its name is visible in the written phrase on screen, and never a frame before. Once an object appears it stays to the end of the clip. The diagram carried over from the previous clip is already present at the very first frame and does not fade in again.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE. Every word appears exactly the number of times it is written.
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol, including every matra and every chandrabindu in the Devanagari.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated. In this clip: the FIRST phrase has exactly ONE golden key word — "ऊतकों" — and nothing else is golden in it. The SECOND phrase has exactly ONE golden key word — "ऑक्सीजन" — and nothing else is golden in it.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time, perfectly synced with the voiceover. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean, glossy, textbook-style biology illustration rendered in three dimensions — smooth shapes, flat bright colours, soft even glow, like a modern NCERT diagram built in 3D. Never photorealistic. NO fire, NO flame, NO burning, NO spark, NO ember, NO explosion, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: continuing exactly from the previous clip — the narrow translucent grey capillary tube with exactly three rigid red sickle cells jammed at its narrow right side, and a few small still deep-red biconcave cells stopped behind them on the left. Everything is completely still. Nothing else.

ANIMATION TIMELINE:
- 0.0 s: the capillary tube, the three jammed sickle cells and the halted cells behind them are already on screen from the previous clip and do not fade in again. The first phrase "और शरीर के ऊतकों तक" pops in fully sharp at the very top of the frame, with the word "ऊतकों" golden inside the sentence.
- 1.4 s, exactly while the word "ऊतकों" is visible on screen, the rounded warm pink tissue patch fades in just beyond the right end of the tube, downstream of the block, and holds to the end.
- 0.0 to 4.8 s: the first phrase holds. The whole scene stays completely still.
- 4.8 s: the first phrase disappears completely.
- 4.8 to 5.0 s: a tiny gap with no phrase on screen.
- 5.0 s: the second phrase "पर्याप्त ऑक्सीजन नहीं पहुँच पाती।" pops in fully sharp, with the word "ऑक्सीजन" golden inside the sentence.
- 5.6 to 7.6 s, exactly while the word "ऑक्सीजन" is visible on screen, the tissue patch smoothly drains of colour, turning from warm healthy pink to a dull desaturated grey-blue and dimming slightly. It keeps exactly the same shape, size and place while it changes colour, and holds the greyed look to the end.
- 7.6 to 10.0 s: the second phrase, the blocked tube, the three still sickle cells and the greyed tissue patch all hold, completely still. Nothing else appears.
- 10.0 s: clip ends.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "और शरीर के ऊतकों तक"
2. "पर्याप्त ऑक्सीजन नहीं पहुँच पाती।"

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, invented labels, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, missing matras, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, a new logo, a duplicated logo, a redrawn logo, a moved logo, a watermark of any kind, text or diagram overlapping either top corner, any label plate, any chip, any callout, any leader line, the letters O2 or any oxygen symbol written on screen, any gauge, meter or dial, a red blood cell with a visible nucleus, a dark blob or organelle inside any cell, a red blood cell drawn as a ring or a doughnut with a hole in the middle, a sickle cell shaped like a smooth banana, a sickle cell with blunt or rounded ends, a crescent moon shape with rounded tips, a star shaped cell, a spiky cell, a blue or purple red blood cell, a sickle cell bending or flexing, the jammed cells moving or coming free, blood flowing past the block, flow moving on the right side of the jam, a fourth sickle cell, only two sickle cells, the tissue patch appearing before 1.4 seconds, the tissue patch changing shape or moving while it greys, the tissue turning black, the tissue patch on the left side of the block, equations, DNA, chromosomes, oxygen dots
```

---

**End states carried forward (unchanged from your plan):** Seg 13 → sickle cell + label · Seg 14 → rigid sickle cell alone · Seg 15 → blocked capillary, 3 wedged sickle cells, flow halted · Seg 16 → same + greyed tissue patch. Seg 17 opens by fading the capillary and showing broken fragments + `रक्ताल्पता` plate.

**Two things to decide before generating:** (1) the red-vs-blue fibre colour above, and (2) test **Segment 13 alone first** — it's the Devanagari conjunct stress test (`हँसिए`, `कोशिकाएँ`, `फँस` come in Segs 14–15), so if the label plate `सिकल सेल एनीमिया` renders clean, the rest of the pack is safe.

Frames read — they confirm the visual conventions I'll lock into the specs: **red biconcave RBC with no nucleus**, **blue HbS fibre strands inside a red crescent**, **white rounded label plates with dark bold text**. Segments 17–20 below match that house look.

**Two judgement calls I made (tell me if you want them changed):**

1. **Seg 19 parents are drawn as normal-looking icons with NO genotype chips** — only two red gene arrows descend from them. Reason: the accuracy brief bans carriers drawn as sick, and putting `HbS` chips on both parents would have pushed `HbS` to six on-screen copies in the pack's highest-risk duplicate segment. Arrows carry the meaning without text.
2. **Seg 18 is TEXT_ONLY but opens with a carry-over fade** (the fragments + `रक्ताल्पता` plate from Seg 17 fade out by 1.5 s), because Seg 17's end-state must equal Seg 18's start-state. After 1.5 s it is a pure no-diagram clip.

**Golden keywords:** Seg 17 → `असामान्य` (one only). Seg 18 → **none** (रोग and है repeat across phrases). Seg 19 → **none** (Latin letters + जीन/होता repeat). Seg 20 → `रोग` (P1 only; P2 uniform).

---

```
VIDEO PROMPT — SEGMENT 17 OF 28

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

VOICEOVER NARRATION (spoken audio): an energetic, warm Indian male biology teacher voice speaks this exact Hindi narration during the clip — nothing more, nothing less. The same script also appears on screen word for word, one phrase at a time:
"इसके साथ ही ये असामान्य लाल रक्त कोशिकाएँ जल्दी टूटने लगती हैं। इसी कारण शरीर में रक्ताल्पता उत्पन्न होती है।"

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
- THE CAPILLARY (carried over, already present at the very first frame): one narrow horizontal transparent glass-like tube running across the upper area, pale grey-white with a soft rim light along its upper left edge, seen from the three-quarter angle so it reads as a round tube and not a flat rectangle. It is see-through. It never becomes solid.
- THE JAMMED SICKLE CELLS (carried over, already present at the very first frame): exactly THREE crescent-shaped red blood cells wedged and stacked inside the narrow part of the tube, blocking it. Each one is a true crescent — a curved solid body that is POINTED AND SHARP AT BOTH ENDS, with one concave inner edge and one convex outer edge, deep glossy red all over, with thin blue fibre strands visible lengthwise inside it. They are rigid and stiff: they never bend, never flex and never squash against the tube wall. They are NOT bananas, NOT crescent moons with blunt rounded ends, NOT stars, NOT spiky, and they never contain a nucleus, a dark central blob or a hole.
- THE HALTED FLOW (carried over): behind the block, three or four small round red blood cells sit completely still with no forward motion at all. Each of these is a normal biconcave red disc — uniform glossy red, circular seen face-on, with a shallow dimple on BOTH faces so it reads as a dumbbell in profile. Never a ring, never a doughnut with a hole through it, never a flat circle, and never with a nucleus or any dark central spot.
- THE GREYED TISSUE PATCH (carried over, already present at the very first frame): a soft rounded patch of tissue downstream of the block, drained of colour to a dull desaturated grey. It stays grey and unchanged for the whole clip.
- THE RUPTURING: at the time given in the timeline, ONE of the three jammed sickle cells breaks apart into four or five small irregular deep red fragments that drift gently apart and outward with a soft slow motion. The fragments stay red. They never turn into dust, sparks, smoke or particles.
- THE LABEL: exactly ONE label exists in this clip — a small white rounded plate with dark bold letters reading "रक्ताल्पता", joined to the drifting fragments by one short thin white leader line, drawn as a flat overlay in front of the three dimensional scene. It appears only at the time given in the timeline. No other plate, chip, tag, number or floating letter exists anywhere.

DIAGRAM TIMING SYNC (CRITICAL): every object appears at the exact moment its name is visible in the written phrase on screen, and never a frame before. The diagram carried over from the previous clip is already present at the very first frame and does not fade in again.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE. Every word appears exactly the number of times it is written.
- EXACT COUNT: the word "रक्ताल्पता" appears exactly TWICE in total in this clip — once inside the third phrase and once on the single label plate. Nowhere else, in any size, at any moment.
- EXACT COUNT: the standalone word "रक्त" appears exactly ONCE in total in this clip, inside the first phrase only. The letters that begin the word "रक्ताल्पता" are part of that longer word and are never separated out, never repeated and never shown on their own.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol. Every Devanagari conjunct, matra and bindu is formed correctly and completely.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. In this clip the ONLY golden word is "असामान्य" inside the first phrase; the second phrase and the third phrase are rendered COMPLETELY UNIFORM in bold white with no golden word at all. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time, perfectly synced with the voiceover. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean, glossy, textbook-style biology illustration rendered in three dimensions — smooth shapes, flat bright colours, soft even glow, like a modern NCERT diagram built in 3D. Never photorealistic. NO fire, NO flame, NO burning, NO spark, NO ember, NO explosion, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: continuing exactly from the previous clip — the narrow transparent capillary tube with three rigid crescent sickle cells wedged and stacking inside it, the halted normal biconcave red cells sitting still behind the block, and the greyed-out tissue patch downstream. Nothing else.

ANIMATION TIMELINE:
- 0.0 s: the first phrase "इसके साथ ही ये असामान्य लाल रक्त कोशिकाएँ" pops on at the top, fully sharp, with the single golden word "असामान्य" styled in place. The carried-over capillary scene is already fully present and does not fade in again.
- 1.4 s, exactly as the words "असामान्य लाल रक्त कोशिकाएँ" are visible on screen, the three wedged crescent sickle cells brighten slightly and hold that brightness. Nothing moves.
- 3.3 s: the first phrase disappears completely. 0.2 second gap with no phrase on screen.
- 3.5 s: the second phrase "जल्दी टूटने लगती हैं।" pops on, fully sharp, completely uniform bold white.
- 4.2 s, exactly as the word "टूटने" is visible on screen, ONE of the three jammed sickle cells breaks apart into four or five small irregular deep red fragments that drift gently apart and outward. The other two stay whole and wedged.
- 6.6 s: the second phrase disappears completely. 0.2 second gap with no phrase on screen.
- 6.8 s: the third phrase "इसी कारण शरीर में रक्ताल्पता उत्पन्न होती है।" pops on, fully sharp, completely uniform bold white.
- 6.8 s to 7.4 s: the capillary tube, the two remaining wedged sickle cells, the halted cells behind the block and the greyed tissue patch all fade out smoothly and completely, leaving only the drifting red fragments.
- 7.6 s, exactly as the word "रक्ताल्पता" is visible on screen, the single white rounded label plate reading "रक्ताल्पता" pops on beside the drifting fragments with one short thin white leader line, and holds to the end.
- 10.0 s: clip ends with the third phrase, the drifting red fragments and the one label plate on screen.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "इसके साथ ही ये असामान्य लाल रक्त कोशिकाएँ"
2. "जल्दी टूटने लगती हैं।"
3. "इसी कारण शरीर में रक्ताल्पता उत्पन्न होती है।"
4. "रक्ताल्पता"

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, broken or malformed Devanagari conjuncts, missing or misplaced matras, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, invented labels, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, a new logo, a duplicated logo, a redrawn logo, a moved logo, a watermark of any kind, text or diagram overlapping either top corner, a red blood cell with a visible nucleus, a dark central blob inside any red blood cell, a red blood cell drawn as a flat circle, a red blood cell drawn as a ring or doughnut with a hole through it, a sickle cell shaped like a banana with rounded ends, a crescent moon with blunt ends, a star-shaped or spiky cell, a blue or purple red blood cell, every cell in the frame sickled, a sickle cell bending or flexing, the cell fragments turning into dust sparks or smoke, any DNA, any helix, any bead chain, any gene, any parent icon, any equation, a flat two dimensional circle instead of a three dimensional cell, a straight-on front view with no depth, a diagram that looks like a flat line drawing, the rupture happening before 4.2 seconds, the label appearing before 7.6 seconds, a second label plate, a second "रक्ताल्पता", the capillary reappearing after it fades
```

---

```
VIDEO PROMPT — SEGMENT 18 OF 28

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

VOICEOVER NARRATION (spoken audio): an energetic, warm Indian male biology teacher voice speaks this exact Hindi narration during the clip — nothing more, nothing less. The same script also appears on screen word for word, one phrase at a time:
"अब समझते हैं कि यह रोग अगली पीढ़ी में कैसे पहुँचता है। सिकल सेल एनीमिया एक अप्रभावी अलिंगी गुणसूत्रीय रोग है।"

AUDIO: only the voiceover above. No background music. Only very soft whoosh and pop sounds on text animations are allowed.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, filling the width, starting close to the top edge, large enough to fill the upper area comfortably. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

LOGO SAFE AREA: keep the top-left corner and the top-right corner of the frame completely clear of script text, diagram, equation, labels and any moving element for the whole clip — only the background itself shows there. Do not draw, copy, move, recreate or animate any logo, wordmark, badge or watermark anywhere in the frame; the logo already present on the supplied background must stay exactly where it is, unchanged.

DIAGRAM SPECIFICATION: the scene from the previous clip — a few small irregular deep red cell fragments drifting gently, and one white rounded label plate reading "रक्ताल्पता" with its short thin white leader line — is present at the very first frame. It shrinks smoothly to about half its size, drifts upward, and fades away completely by 1.5 seconds. From 1.5 seconds onward the area below the script text is plain empty background. LABELS: after the carried-over plate fades at 1.5 seconds this clip has NO labels at all. Never invent a label.

NO DIAGRAM IN THIS CLIP AFTER 1.5 SECONDS (CRITICAL): from 1.5 seconds to the end, this clip contains NO three dimensional object of any kind. There is no red blood cell, no sickle cell, no cell fragment, no capillary, no tube, no tissue, no haemoglobin, no DNA, no helix, no bead chain, no chromosome, no parent icon, no arrow, no shape, no icon and no illustration anywhere in the frame at any moment. The only things on screen are the script text and the plain background. Do not invent, add or imagine any diagram, object or graphic. The space below the script text stays as plain empty background.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE. Every word appears exactly the number of times it is written.
- EXACT COUNT: the word "रोग" appears exactly TWICE in total in this clip — once inside the first phrase and once inside the third phrase. Nowhere else, in any size, at any moment, and never twice inside the same phrase.
- EXACT COUNT: the word "है" appears exactly TWICE in total in this clip — once at the end of the second phrase and once at the end of the third phrase. Nowhere else.
- This clip has NO label plates at all after the carried-over plate fades. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol. Every Devanagari conjunct, matra and bindu is formed correctly and completely.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. In this clip ALL THREE phrases are rendered COMPLETELY UNIFORM in bold white with NO golden word anywhere, because words repeat across the phrases. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time, perfectly synced with the voiceover. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean crisp flat overlay typography on a dark technical background. Never photorealistic. NO fire, NO flame, NO sparks, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: continuing exactly from the previous clip — a few small irregular deep red cell fragments drifting gently, with one white rounded label plate reading "रक्ताल्पता" joined to them by a short thin white leader line. Nothing else.

ANIMATION TIMELINE:
- 0.0 s: the first phrase "अब समझते हैं कि यह रोग" pops on at the top, fully sharp, completely uniform bold white. The carried-over fragments and the "रक्ताल्पता" plate are already fully present and do not fade in again.
- 0.3 s to 1.5 s: the fragments and the "रक्ताल्पता" plate shrink to about half size, drift upward and fade away completely. After 1.5 seconds the area below the script text is plain empty background and stays that way.
- 3.3 s: the first phrase disappears completely. 0.2 second gap with no phrase on screen.
- 3.5 s: the second phrase "अगली पीढ़ी में कैसे पहुँचता है।" pops on, fully sharp, completely uniform bold white.
- 6.6 s: the second phrase disappears completely. 0.2 second gap with no phrase on screen.
- 6.8 s: the third phrase "सिकल सेल एनीमिया एक अप्रभावी अलिंगी गुणसूत्रीय रोग है।" pops on, fully sharp, completely uniform bold white, and holds to the end.
- 10.0 s: clip ends with only the third phrase on screen and plain empty background below it.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "अब समझते हैं कि यह रोग"
2. "अगली पीढ़ी में कैसे पहुँचता है।"
3. "सिकल सेल एनीमिया एक अप्रभावी अलिंगी गुणसूत्रीय रोग है।"
4. "रक्ताल्पता" (carried over from the previous clip, visible only until it fades at 1.5 seconds)

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, broken or malformed Devanagari conjuncts, missing or misplaced matras, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, invented labels, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, a new logo, a duplicated logo, a redrawn logo, a moved logo, a watermark of any kind, text or diagram overlapping either top corner, any red blood cell, any sickle cell, any cell fragment after 1.5 seconds, any capillary or tube, any chromosome, any X chromosome, any Y chromosome, any sex chromosome symbol, any pedigree chart, any parent or child icon, any DNA or helix, any equation, any label plate after 1.5 seconds, a golden word in any phrase, the fragments reappearing after they fade, a third "रोग", a second copy of any phrase
```

---

```
VIDEO PROMPT — SEGMENT 19 OF 28

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

VOICEOVER NARRATION (spoken audio): an energetic, warm Indian male biology teacher voice speaks this exact Hindi narration during the clip — nothing more, nothing less. The same script also appears on screen word for word, one phrase at a time:
"यदि बच्चे को दोनों माता-पिता से सिकल सेल वाला जीन प्राप्त होता है, तो उसका जीन प्रारूप HbS HbS होता है"

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
- THE TWO PARENT ICONS: exactly TWO simple glossy three dimensional icons side by side in the upper diagram area, one on the left and one on the right, evenly spaced with a clear gap between them. Each is a smooth rounded human bust silhouette rendered as a solid glossy shape in calm slate blue, with a soft cool rim light along its upper left edge, seen from the three-quarter angle so it reads as a solid rounded volume and not a flat cut-out. Both parents look completely healthy and normal — they are never drawn as sick, never grey, never cracked, never marked with any symbol of illness, and no sickle cell, blood cell, chromosome or letter is ever drawn on or inside them. They carry NO text of any kind. They are perfectly still once settled.
- THE TWO GENE ARROWS: exactly TWO straight arrows, one descending from each parent icon, angling inward and downward to meet at the child icon below. They are deep red with small neat conical arrowheads. Because of perspective they are drawn with clear depth, slightly thicker near the camera. They never cross each other, never tangle and never bend.
- THE CHILD ICON: exactly ONE simple glossy three dimensional icon below and centred between the two parents, the same smooth rounded human bust silhouette in calm slate blue, smaller than the parents, with the same rim light and three-quarter angle. It appears only at the time given in the timeline.
- THE GENOTYPE PLATE: exactly ONE plate exists in this clip — a small white rounded plate with dark bold Latin letters reading "HbS HbS", joined to the child icon by one short thin white leader line, drawn as a flat overlay in front of the three dimensional scene. The two words sit on ONE single horizontal line with one normal space between them, both the same size, both perfectly sharp, with a capital H, a lowercase b and a capital S in each. It appears only at the time given in the timeline. No other plate, chip, tag, number or floating letter exists anywhere on the parents, on the arrows, or anywhere else in the frame.

DIAGRAM TIMING SYNC (CRITICAL): every object appears at the exact moment its name is visible in the written phrase on screen, and never a frame before. Once an object appears it stays to the end of the clip.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE beyond what is written. Every word appears exactly the number of times it is written.
- EXACT COUNT: the token "HbS" appears exactly FOUR times in total in this clip and nowhere else, in any size, at any moment — exactly TWICE side by side inside the third phrase, written as "HbS HbS" on one line, and exactly TWICE side by side on the single white plate, written as "HbS HbS" on one line. It is written this way deliberately; it is never shown a fifth time, never appears alone anywhere, and never appears on a parent icon or on an arrow.
- EXACT COUNT: the token "HbA" appears ZERO times in this clip. It must not appear anywhere, on any icon, plate or phrase.
- EXACT COUNT: the word "जीन" appears exactly TWICE in total in this clip — once inside the second phrase and once inside the third phrase. Nowhere else, and never twice inside the same phrase.
- EXACT COUNT: the word "होता" appears exactly TWICE in total in this clip — once inside the second phrase and once inside the third phrase. Nowhere else.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol. Every Devanagari conjunct, matra and bindu is formed correctly and completely, and every Latin letter keeps its exact capitalisation.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. In this clip ALL THREE phrases are rendered COMPLETELY UNIFORM in bold white with NO golden word anywhere, because the phrases contain Latin letter tokens, a hyphenated word and words that repeat. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated, and "HbS HbS" always stays together on one line.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters or mathematical symbols into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time, perfectly synced with the voiceover. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment. The parent and child icons are plain smooth silhouettes with no facial features of any kind.

VISUAL STYLE: clean, glossy, textbook-style biology illustration rendered in three dimensions — smooth shapes, flat bright colours, soft even glow, like a modern NCERT diagram built in 3D. Never photorealistic. NO fire, NO flame, NO burning, NO spark, NO ember, NO explosion, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: completely empty background. Nothing at all.

ANIMATION TIMELINE:
- 0.0 s: the first phrase "यदि बच्चे को दोनों माता-पिता से" pops on at the top, fully sharp, completely uniform bold white.
- 1.6 s, exactly as the words "दोनों माता-पिता" are visible on screen, the TWO parent icons pop on side by side below the script text and settle. They stay to the end.
- 3.3 s: the first phrase disappears completely. 0.2 second gap with no phrase on screen.
- 3.5 s: the second phrase "सिकल सेल वाला जीन प्राप्त होता है," pops on, fully sharp, completely uniform bold white.
- 4.6 s, exactly as the word "जीन" is visible on screen, the TWO deep red gene arrows draw downward and inward from the two parent icons, one from each, meeting at the empty space below. They stay to the end.
- 6.6 s: the second phrase disappears completely. 0.2 second gap with no phrase on screen.
- 6.8 s: the third phrase "तो उसका जीन प्रारूप HbS HbS होता है" pops on, fully sharp, completely uniform bold white, with "HbS HbS" kept together on one line.
- 7.4 s, exactly as the word "प्रारूप" is visible on screen, the child icon pops on where the two arrows meet and settles.
- 8.4 s: the single white rounded plate reading "HbS HbS" pops on beside the child icon with one short thin white leader line, and holds to the end.
- 10.0 s: clip ends with the third phrase, the two parent icons, the two red arrows, the child icon and the one "HbS HbS" plate on screen.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "यदि बच्चे को दोनों माता-पिता से"
2. "सिकल सेल वाला जीन प्राप्त होता है,"
3. "तो उसका जीन प्रारूप HbS HbS होता है"
4. "HbS HbS" (the single label plate on the child icon)

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, broken or malformed Devanagari conjuncts, missing or misplaced matras, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, people, faces, teachers, characters, avatars, hands, facial features on the icons, double text, duplicated text, two copies of the same sentence, a repeated word beyond what is written, a repeated key word, a keyword written as a separate line, invented labels, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, a new logo, a duplicated logo, a redrawn logo, a moved logo, a watermark of any kind, text or diagram overlapping either top corner, a fifth "HbS", a lone "HbS" anywhere outside the phrase and the plate, "HbS" written on a parent icon, "HbS" written on an arrow, the token "HbA" anywhere, the spellings "HBs", "HgB", "Hbs" or "HBS", "HbS HbS" split across two lines, a second label plate, two copies of the plate, any X chromosome, any Y chromosome, any sex chromosome, an X-linked or sex-linked pedigree, any chromosome drawn at all, parents drawn as sick or grey or damaged, sickle cells drawn on or inside the parent icons, any red blood cell, any sickle cell, any capillary, any DNA or helix, any bead chain, any equation, a flat two dimensional silhouette with no depth, a straight-on front view with no depth, arrows all drawn the same length on screen, tangled or crossing arrows, the parent icons appearing before 1.6 seconds, the arrows appearing before 4.6 seconds, the child icon appearing before 7.4 seconds, the plate appearing before 8.4 seconds, a golden word in any phrase
```

---

```
VIDEO PROMPT — SEGMENT 20 OF 28

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

VOICEOVER NARRATION (spoken audio): an energetic, warm Indian male biology teacher voice speaks this exact Hindi narration during the clip — nothing more, nothing less. The same script also appears on screen word for word, one phrase at a time:
"और उसे यह रोग हो सकता है। यदि बच्चे को केवल एक माता या पिता से"

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
- THE CARRIED-OVER CROSS (already present at the very first frame): two glossy slate blue three dimensional parent bust silhouettes side by side, two deep red arrows descending inward from them, one smaller child bust silhouette where the arrows meet, and one white rounded plate reading "HbS HbS" joined to the child by a short thin white leader line. It does not fade in again. At the time given in the timeline this entire group — both parents, both arrows, the child and the plate — shrinks smoothly to about half its size, drifts upward and fades away completely, leaving the area below the script text free for the new cross.
- THE AFFECTED GLOW: at the time given in the timeline, the carried-over child silhouette turns a warm deep red and glows softly in place, staying exactly where it is and keeping its shape. NOTHING is copied out of it. No new symbol, letter, plate or callout is created for it.
- THE NEW PARENT ICONS: exactly TWO glossy slate blue three dimensional bust silhouettes, one on the left and one on the right, evenly spaced with a clear gap between them, rendered from the three-quarter angle with a soft cool rim light along the upper left edge. Both look completely healthy and normal — never sick, never grey, never cracked, and no sickle cell, blood cell or chromosome is ever drawn on or inside them. They appear only at the time given in the timeline.
- THE TWO GENOTYPE CHIPS: exactly TWO small white rounded plates with dark bold Latin letters, drawn as flat overlays in front of the three dimensional scene, each joined to its parent by one short thin white leader line. The LEFT parent carries exactly ONE plate reading "HbA". The RIGHT parent carries exactly ONE plate reading "HbS". Each token sits on ONE line, perfectly sharp, with a capital H, a lowercase b and a capital final letter. There are exactly two plates in the second half of this clip and no others.
- THE NEW ARROWS: exactly TWO straight deep red arrows with small neat conical arrowheads, one descending inward from each new parent icon, meeting below at the child position. They never cross, never tangle and never bend.
- THE EMPTY CHILD ICON: exactly ONE smaller glossy slate blue bust silhouette where the two new arrows meet, drawn plain and completely EMPTY — it carries NO plate, NO chip, NO letter and NO text of any kind, and none is ever invented for it in this clip.

DIAGRAM TIMING SYNC (CRITICAL): every object appears at the exact moment its name is visible in the written phrase on screen, and never a frame before. The diagram carried over from the previous clip is already present at the very first frame and does not fade in again.

HIGHLIGHT RULE (CRITICAL — NO NEW TEXT IS EVER CREATED): when a part of the diagram is emphasised, that existing part simply changes colour and glows brighter in place. NEVER copy a symbol, letter or plate out of the scene. NEVER draw a second copy of anything anywhere. NEVER create a label, plate, chip, callout or floating letter for an emphasis. The plates listed in the diagram specification are the only places any Latin letters ever appear.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE. Every word appears exactly the number of times it is written.
- EXACT COUNT: the token "HbS" appears exactly THREE times in total in this clip and nowhere else, in any size, at any moment — exactly TWICE side by side inside the carried-over plate reading "HbS HbS" which is visible only until it fades, and exactly ONCE on the right-hand parent chip in the second half of the clip.
- EXACT COUNT: the token "HbA" appears exactly ONCE in total in this clip, on the left-hand parent chip only. Nowhere else, at any moment.
- EXACT COUNT: the word "रोग" appears exactly ONCE in total in this clip, inside the first phrase only.
- The new child icon in the second half of this clip has NO plate, NO chip, NO floating letter, NO leader line and NO stray symbol. Never invent a label for it.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol. Every Devanagari conjunct, matra and bindu is formed correctly and completely, and every Latin letter keeps its exact capitalisation.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. In this clip the ONLY golden word is "रोग" inside the first phrase; the second phrase is rendered COMPLETELY UNIFORM in bold white with no golden word at all. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters or mathematical symbols into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time, perfectly synced with the voiceover. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment. The parent and child icons are plain smooth silhouettes with no facial features of any kind.

VISUAL STYLE: clean, glossy, textbook-style biology illustration rendered in three dimensions — smooth shapes, flat bright colours, soft even glow, like a modern NCERT diagram built in 3D. Never photorealistic. NO fire, NO flame, NO burning, NO spark, NO ember, NO explosion, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: continuing exactly from the previous clip — two slate blue parent bust silhouettes side by side, two deep red arrows descending inward from them to one smaller child bust silhouette, and one white rounded plate reading "HbS HbS" joined to that child by a short thin white leader line. Nothing else.

ANIMATION TIMELINE:
- 0.0 s: the first phrase "और उसे यह रोग हो सकता है।" pops on at the top, fully sharp, with the single golden word "रोग" styled in place. The carried-over cross is already fully present and does not fade in again.
- 1.6 s, exactly as the word "रोग" is visible on screen, the carried-over child silhouette turns a warm deep red and glows softly, staying exactly in its place and keeping its shape. Nothing is copied out of it and no new text is created.
- 4.8 s: the first phrase disappears completely. 0.2 second gap with no phrase on screen.
- 5.0 s: the second phrase "यदि बच्चे को केवल एक माता या पिता से" pops on, fully sharp, completely uniform bold white.
- 5.0 s to 5.8 s: the entire carried-over cross — both parents, both arrows, the glowing child and the "HbS HbS" plate — shrinks to about half size, drifts upward and fades away completely.
- 6.2 s, exactly as the words "केवल एक" are visible on screen, the TWO new parent icons pop on side by side below the script text and settle.
- 7.2 s, exactly as the word "माता" is visible on screen, the left parent's white chip reading "HbA" pops on with its short thin white leader line and holds to the end.
- 7.9 s, exactly as the word "पिता" is visible on screen, the right parent's white chip reading "HbS" pops on with its short thin white leader line and holds to the end.
- 8.8 s: the two new deep red arrows draw downward and inward from the two parent icons, and the plain EMPTY child icon pops on where they meet. It carries no text at all.
- 10.0 s: clip ends with the second phrase, the two new parent icons, the "HbA" chip, the "HbS" chip, the two red arrows and the empty child icon on screen.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "और उसे यह रोग हो सकता है।"
2. "यदि बच्चे को केवल एक माता या पिता से"
3. "HbS HbS" (the carried-over plate from the previous clip, visible only until it fades at 5.8 seconds)
4. "HbA" (the left parent chip)
5. "HbS" (the right parent chip)

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, broken or malformed Devanagari conjuncts, missing or misplaced matras, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, people, faces, teachers, characters, avatars, hands, facial features on the icons, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, invented labels, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, a new logo, a duplicated logo, a redrawn logo, a moved logo, a watermark of any kind, text or diagram overlapping either top corner, a plate or chip on the new child icon, a genotype written under the new child, a fourth "HbS", a second "HbA", the spellings "HBs", "HgB", "Hbs" or "HBS", a copy of any letter taken out of a plate, a floating letter anywhere outside the plates, the carried-over cross reappearing after it fades, both new parents given the same chip, the new parents drawn as sick or grey or damaged, sickle cells drawn on or inside any parent icon, any X chromosome, any Y chromosome, any sex chromosome, an X-linked or sex-linked pedigree, any chromosome drawn at all, any red blood cell, any sickle cell, any capillary, any DNA or helix, any equation, a flat two dimensional silhouette with no depth, a straight-on front view with no depth, arrows all drawn the same length on screen, tangled or crossing arrows, the new parent icons appearing before 6.2 seconds, the "HbA" chip appearing before 7.2 seconds, the "HbS" chip appearing before 7.9 seconds, the new arrows or child appearing before 8.8 seconds
```

---

**One thing to watch when you test:** Seg 19 is the pack's highest-risk clip — `HbS HbS` appears as a literal doubled token in both the phrase and the plate. Generate Seg 19 **first**, before 17, 18 or 20. If the model produces a stray fifth `HbS` or splits the plate across two lines, the fallback is to drop the plate entirely and let the phrase carry the genotype — tell me and I'll rewrite it that way.

Frames confirm the visual grammar (white rounded label plates + thin leader lines, biconcave RBC, pointed-end crescent, blue bead HbS fibres) — the specs below match it.

**Segments 21–24 — all DIAGRAM type. Continuity carried: Seg 21 opens on the HbA × HbS cross with an empty child icon.**

```
VIDEO PROMPT — SEGMENT 21 OF 28

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

VOICEOVER NARRATION (spoken audio): an energetic, warm Indian male biology teacher voice speaks this exact Hinglish narration during the clip — nothing more, nothing less. The same script also appears on screen word for word, one phrase at a time:
"सिकल सेल वाला जीन मिलता है, तो उसका जीन प्रारूप HbA HbS होता है।"

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
- THE CROSS CARRIED OVER FROM THE PREVIOUS CLIP: the whole inheritance cross is already present at the very first frame and does not fade in again. It is a simple three dimensional family cross: TWO parent icons side by side in the upper part of the diagram area, and ONE child icon below and centred between them.
- THE FIRST PARENT ICON: one smooth rounded three dimensional plate, glossy and glass-like, tinted soft cyan-blue, standing upright with a faint specular highlight on its upper left, carrying the dark bold Latin text "HbA" on its face. This parent is the normal-looking parent. It never changes during this clip.
- THE SECOND PARENT ICON: an identical rounded three dimensional plate, same size and same style, tinted soft warm orange, carrying the dark bold Latin text "HbS" on its face. This parent is the carrier parent and looks completely healthy and normal — it is never drawn sick, never sickled, never damaged. It never changes during this clip. Both parent icons are exactly the same size and equally bright: neither parent is bigger, stronger, highlighted or shown as the main source of the gene. Neither parent icon is a male or female symbol, a chromosome, a human figure or a face — they are plain rounded plates only.
- THE INHERITANCE ARROWS: exactly TWO short thick three dimensional arrows, one running down and inward from each parent icon and meeting at the child icon. Both arrows are exactly the same length, the same thickness and the same brightness, in soft neutral white-grey with small neat conical arrowheads. They are already present at the very first frame and never move.
- THE CHILD ICON: one rounded three dimensional plate of the same style, sitting below the two arrows, EMPTY at the very first frame with a plain pale glass face and no writing on it. At the moment given in the timeline it fills in with the dark bold Latin text "HbA HbS" written once on its face, on ONE single horizontal line, and its face takes on a soft green tint. The plate itself does not move, does not resize and does not duplicate.
- THE GENE IS ON AN ORDINARY BODY CHROMOSOME. No sex chromosome, no X shape, no Y shape, no pedigree square, no pedigree circle, no karyotype and no human figure appears anywhere in this clip.
- LABELS: this clip has NO label plates at all. Never invent a label. The only writing inside the diagram is the text on the three icon faces.

DIAGRAM TIMING SYNC (CRITICAL): every object appears at the exact moment its name is visible in the written phrase on screen, and never a frame before. The diagram carried over from the previous clip is already present at the very first frame and does not fade in again. At 6.0 seconds, exactly as the letters "HbA HbS" are visible in the written phrase on screen, the child icon fills in with "HbA HbS". Once it appears it stays to the end of the clip.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE. Every word appears exactly the number of times it is written.
- EXACT COUNT: the word "जीन" appears exactly TWICE in total in this clip — once inside the first phrase and once inside the second phrase. Nowhere else, in any size, at any moment.
- EXACT COUNT: the letters "HbA" appear exactly TWICE in total in this clip — once on the first parent icon and once inside the child icon text "HbA HbS". Nowhere else, in any size, at any moment.
- EXACT COUNT: the letters "HbS" appear exactly TWICE in total in this clip — once on the second parent icon and once inside the child icon text "HbA HbS". Nowhere else, in any size, at any moment.
- EXACT COUNT: the line "HbA HbS" appears exactly TWICE in total in this clip — once inside the second phrase of the script text and once on the child icon. Nowhere else, in any size, at any moment.
- The letters are always written exactly as "HbA" and "HbS" — capital H, small b, then a capital letter. Never "HBs", "HBS", "Hgb", "HgB", "hba" or any other spelling.
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol. Every Hindi word is rendered in correct clean Devanagari with all matras and conjuncts exactly as written.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated. In this clip BOTH phrases are rendered COMPLETELY UNIFORM in bold white, with NO golden word anywhere, because the word "जीन" is repeated across the phrases and the second phrase contains the Latin letter groups "HbA HbS".

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time, perfectly synced with the voiceover. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean, glossy, textbook-style biology illustration rendered in three dimensions — smooth shapes, flat bright colours, soft even glow, like a modern NCERT diagram built in 3D. Never photorealistic. NO fire, NO flame, NO burning, NO spark, NO ember, NO explosion, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: continuing exactly from the previous clip — the inheritance cross is already fully present: one parent icon reading "HbA" on the left, one parent icon reading "HbS" on the right, two equal arrows running down from them to one EMPTY child icon below with no writing on its face. No script text yet. Nothing else.

ANIMATION TIMELINE:
- 0.0 s: the cross described above is already on screen exactly as it ended in the previous clip, still and sharp. It does not fade in again.
- 0.0–4.8 s: the first phrase "सिकल सेल वाला जीन मिलता है," is visible at the top of the frame in uniform bold white, popping in fully sharp at 0.0 s and holding.
- 4.8 s: the first phrase disappears completely.
- 4.8–5.0 s: a tiny gap with no script phrase on screen.
- 5.0–10.0 s: the second phrase "तो उसका जीन प्रारूप HbA HbS होता है।" is visible at the top of the frame in uniform bold white, popping in fully sharp at 5.0 s and holding to the end.
- 6.0 s: exactly as the letters "HbA HbS" are visible in the written phrase on screen, the empty child icon fills in — the dark bold text "HbA HbS" pops onto its face on one single line and the plate face takes on a soft green tint. The plate does not move or resize. It holds exactly like this to the end.
- 6.0–10.0 s: the whole cross holds still, with only the very slow steady turn of the three dimensional plates. Nothing else moves, appears or disappears.
- 10.0 s: clip ends with the second phrase and the completed cross on screen.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "सिकल सेल वाला जीन मिलता है,"
2. "तो उसका जीन प्रारूप HbA HbS होता है।"
3. "HbA" (on the first parent icon)
4. "HbS" (on the second parent icon)
5. "HbA HbS" (on the child icon)

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, broken or malformed Devanagari letters, missing or wrong matras, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, invented labels, any label plate, any chip, any callout, any leader line, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, a new logo, a duplicated logo, a redrawn logo, a moved logo, a watermark of any kind, text or diagram overlapping either top corner, the child icon text appearing before 6.0 seconds, a third parent icon, a second child icon, a second copy of "HbA HbS", a third arrow, arrows of unequal length, one parent drawn larger, brighter or as the only source of the gene, an X chromosome, a Y chromosome, any sex chromosome, a pedigree square or circle, a human figure, a male or female symbol, a karyotype, a red blood cell with a visible nucleus, a red blood cell drawn as a flat ring or doughnut with a hole, a sickle cell drawn as a smooth banana or a crescent moon with blunt ends, a carrier drawn with sickled cells or disease symptoms, a sick-looking parent, the spellings "HBs", "HBS", "HgB" or "Hgb", equations, any sphere, cell, fibre, capillary, DNA strand or bead chain
```

```
VIDEO PROMPT — SEGMENT 22 OF 28

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

VOICEOVER NARRATION (spoken audio): an energetic, warm Indian male biology teacher voice speaks this exact Hinglish narration during the clip — nothing more, nothing less. The same script also appears on screen word for word, one phrase at a time:
"ऐसी स्थिति में व्यक्ति सामान्यतः वाहक होता है। उसमें रोग के लक्षण आवश्यक रूप से नहीं होते,"

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
- THE CROSS CARRIED OVER FROM THE PREVIOUS CLIP: the complete inheritance cross is already present at the very first frame and does not fade in again — the left parent icon reading "HbA", the right parent icon reading "HbS", two equal arrows running down and inward, and the child icon below reading "HbA HbS" on one single line with a soft green tinted face. Every icon keeps exactly the size, position, colour and text it had at the end of the previous clip. Nothing in the cross moves, resizes, recolours or duplicates during this clip.
- BOTH PARENT ICONS stay exactly the same size and equally bright: neither parent is bigger, stronger, highlighted or shown as the main source of the gene. Neither icon is a male or female symbol, a chromosome, a human figure or a face — they are plain rounded three dimensional plates only.
- THE CHILD ICON IS A CARRIER AND LOOKS COMPLETELY NORMAL AND HEALTHY: its plate stays clean, smooth and evenly tinted. It is never drawn half-sick, never cracked, never split into two halves, never partly red, never marked with a warning sign, and no sickled cell, damaged cell or symptom of any kind is ever attached to it.
- THE LABEL: exactly ONE label exists in this clip — a small white rounded plate with dark bold letters reading "वाहक", joined to the child icon by one short thin white leader line, drawn as a flat overlay in front of the three dimensional scene. It appears only at the time given in the timeline. No other plate, chip, tag, number or floating letter exists anywhere.
- THE GENE IS ON AN ORDINARY BODY CHROMOSOME. No sex chromosome, no X shape, no Y shape, no pedigree square, no pedigree circle, no karyotype and no human figure appears anywhere in this clip.

DIAGRAM TIMING SYNC (CRITICAL): every object appears at the exact moment its name is visible in the written phrase on screen, and never a frame before. The diagram carried over from the previous clip is already present at the very first frame and does not fade in again. The label "वाहक" appears at 3.6 seconds, exactly while the word "वाहक" is visible inside the written first phrase on screen. Once it appears it stays to the end of the clip.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE. Every word appears exactly the number of times it is written.
- EXACT COUNT: the word "वाहक" appears exactly TWICE in total in this clip — once inside the first phrase and once inside the single white label plate attached to the child icon. Nowhere else, in any size, at any moment.
- EXACT COUNT: the letters "HbA" appear exactly TWICE in total in this clip — once on the left parent icon and once inside the child icon text "HbA HbS". Nowhere else, in any size, at any moment.
- EXACT COUNT: the letters "HbS" appear exactly TWICE in total in this clip — once on the right parent icon and once inside the child icon text "HbA HbS". Nowhere else, in any size, at any moment.
- The letters are always written exactly as "HbA" and "HbS" — capital H, small b, then a capital letter. Never "HBs", "HBS", "Hgb", "HgB", "hba" or any other spelling.
- There is exactly ONE label plate in this clip and it reads "वाहक". No second plate, no chip, no floating letter, no extra leader line, no stray symbol. Never invent another label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol. Every Hindi word is rendered in correct clean Devanagari with all matras and conjuncts exactly as written.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated. In this clip the FIRST phrase is rendered COMPLETELY UNIFORM in bold white with NO golden word, because the word "वाहक" also appears on the label plate. In the SECOND phrase exactly ONE word — "लक्षण" — is golden, styled in place inside the sentence and never written again anywhere else; all other words of that phrase are bold white.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time, perfectly synced with the voiceover. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean, glossy, textbook-style biology illustration rendered in three dimensions — smooth shapes, flat bright colours, soft even glow, like a modern NCERT diagram built in 3D. Never photorealistic. NO fire, NO flame, NO burning, NO spark, NO ember, NO explosion, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: continuing exactly from the previous clip — the complete cross is on screen: parent icon "HbA" on the left, parent icon "HbS" on the right, two equal arrows down to the child icon reading "HbA HbS" with a soft green tinted face. No label plate yet, no script text yet. Nothing else.

ANIMATION TIMELINE:
- 0.0 s: the completed cross is already on screen exactly as it ended in the previous clip, still and sharp. It does not fade in again.
- 0.0–4.8 s: the first phrase "ऐसी स्थिति में व्यक्ति सामान्यतः वाहक होता है।" is visible at the top of the frame in uniform bold white, popping in fully sharp at 0.0 s and holding.
- 3.6 s: exactly while the word "वाहक" is visible inside the written phrase on screen, the single white rounded label plate reading "वाहक" pops in beside the child icon with its one short thin white leader line, and holds to the end.
- 4.8 s: the first phrase disappears completely.
- 4.8–5.0 s: a tiny gap with no script phrase on screen. The cross and the label plate stay untouched.
- 5.0–10.0 s: the second phrase "उसमें रोग के लक्षण आवश्यक रूप से नहीं होते," is visible at the top of the frame, the word "लक्षण" golden in place and the rest bold white, popping in fully sharp at 5.0 s and holding to the end.
- 5.0–10.0 s: the cross and the label hold still, with only the very slow steady turn of the three dimensional plates. Nothing else moves, appears or disappears.
- 10.0 s: clip ends with the second phrase, the completed cross and the single "वाहक" label on screen.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "ऐसी स्थिति में व्यक्ति सामान्यतः वाहक होता है।"
2. "उसमें रोग के लक्षण आवश्यक रूप से नहीं होते,"
3. "HbA" (on the left parent icon)
4. "HbS" (on the right parent icon)
5. "HbA HbS" (on the child icon)
6. "वाहक" (the single white label plate on the child icon)

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, broken or malformed Devanagari letters, missing or wrong matras, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, invented labels, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, a new logo, a duplicated logo, a redrawn logo, a moved logo, a watermark of any kind, text or diagram overlapping either top corner, the label appearing before 3.6 seconds, a second label plate, a second "वाहक", a golden word in the first phrase, a third parent icon, a second child icon, a third arrow, arrows of unequal length, one parent drawn larger or brighter than the other, an X chromosome, a Y chromosome, any sex chromosome, a pedigree square or circle, a human figure, a male or female symbol, a karyotype, the carrier drawn half-sick, cracked, split, partly red or marked with a warning sign, a sickled cell attached to the carrier, a sickle cell drawn as a smooth banana or a crescent moon with blunt ends, a red blood cell with a visible nucleus, a red blood cell drawn as a flat ring or doughnut with a hole, the spellings "HBs", "HBS", "HgB" or "Hgb", equations, any sphere, cell, fibre, capillary, DNA strand or bead chain
```

```
VIDEO PROMPT — SEGMENT 23 OF 28

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

VOICEOVER NARRATION (spoken audio): an energetic, warm Indian male biology teacher voice speaks this exact Hinglish narration during the clip — nothing more, nothing less. The same script also appears on screen word for word, one phrase at a time:
"लेकिन वह इस जीन को अपनी अगली पीढ़ी में पहुँचा सकता है।"

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
- THE SCENE CARRIED OVER FROM THE PREVIOUS CLIP: the whole cross — the left parent icon "HbA", the right parent icon "HbS", the two equal arrows, the child icon "HbA HbS" and its single white label plate reading "वाहक" — is already present at the very first frame and does not fade in again.
- THE FADE: between 1.5 and 3.0 seconds the two parent icons and the two arrows between them fade away completely and smoothly, while the child icon and its "वाहक" label stay. As they fade out, the child icon drifts smoothly to the upper part of the diagram area and settles there, keeping exactly the same size, colour and text. After 3.0 seconds the parent icons and their arrows are completely gone and never come back.
- THE CARRIER ICON: the surviving rounded three dimensional plate, glossy and glass-like with a soft green tinted face, reading the dark bold Latin text "HbA HbS" on one single line, with its one white rounded label plate reading "वाहक" joined by one short thin white leader line. It looks completely normal and healthy — never cracked, never split, never half-red, never marked with a warning sign, and no sickled cell or symptom is ever attached to it.
- THE NEXT-GENERATION ARROW: exactly ONE straight three dimensional arrow, soft neutral white-grey with a small neat conical arrowhead, running straight downward from the carrier icon. It appears only at the time given in the timeline.
- THE NEXT-GENERATION ICON: exactly ONE rounded three dimensional plate of the same style as the carrier icon but with a plain pale glass face and NO writing on it at all, sitting below the arrow. It stays empty and blank for the whole clip. It is never a human figure, never a face, never a baby, never a pedigree symbol.
- THE GENE IS ON AN ORDINARY BODY CHROMOSOME. No sex chromosome, no X shape, no Y shape, no pedigree square, no pedigree circle, no karyotype and no human figure appears anywhere in this clip.
- LABELS: exactly ONE label exists in this clip, the "वाहक" plate carried over from the previous clip. Never invent another label.

DIAGRAM TIMING SYNC (CRITICAL): every object appears at the exact moment its name is visible in the written phrase on screen, and never a frame before. The diagram carried over from the previous clip is already present at the very first frame and does not fade in again. At 6.2 seconds, exactly as the words "अगली पीढ़ी" are visible in the written phrase on screen, the single downward arrow and the empty next-generation icon appear together. Once they appear they stay to the end of the clip.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE. Every word appears exactly the number of times it is written.
- EXACT COUNT: the line "HbA HbS" appears exactly ONCE in total in this clip — only on the carrier icon. Nowhere else, in any size, at any moment. After 3.0 seconds no other Latin letters exist anywhere in the frame.
- EXACT COUNT: the word "वाहक" appears exactly ONCE in total in this clip — only on the single white label plate. Nowhere else, in any size, at any moment.
- The letters are always written exactly as "HbA" and "HbS" — capital H, small b, then a capital letter. Never "HBs", "HBS", "Hgb", "HgB", "hba" or any other spelling.
- The next-generation icon carries NO text of any kind at any moment. It never fills in, never gets letters, never gets a label.
- There is exactly ONE label plate in this clip. No second plate, no chip, no floating letter, no extra leader line, no stray symbol. Never invent another label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol. Every Hindi word is rendered in correct clean Devanagari with all matras and conjuncts exactly as written.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated. In this clip the FIRST phrase has exactly ONE golden word — "जीन" — styled in place inside the sentence, and the SECOND phrase has exactly ONE golden word — "अगली" — styled in place inside the sentence. All other words in both phrases are bold white. No golden word is ever written again anywhere else on screen.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time, perfectly synced with the voiceover. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean, glossy, textbook-style biology illustration rendered in three dimensions — smooth shapes, flat bright colours, soft even glow, like a modern NCERT diagram built in 3D. Never photorealistic. NO fire, NO flame, NO burning, NO spark, NO ember, NO explosion, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: continuing exactly from the previous clip — the complete cross is on screen: parent icon "HbA" on the left, parent icon "HbS" on the right, two equal arrows down to the child icon reading "HbA HbS" with its single white label plate reading "वाहक". No script text yet. Nothing else.

ANIMATION TIMELINE:
- 0.0 s: the scene is already on screen exactly as it ended in the previous clip, still and sharp. It does not fade in again.
- 0.0–4.8 s: the first phrase "लेकिन वह इस जीन को" is visible at the top of the frame, the word "जीन" golden in place and the rest bold white, popping in fully sharp at 0.0 s and holding.
- 1.5–3.0 s: the two parent icons and the two arrows between them fade away smoothly and completely, while the child icon with its "HbA HbS" text and its "वाहक" label drifts up and settles in the upper part of the diagram area at the same size. By 3.0 s only the carrier icon and its single label remain.
- 4.8 s: the first phrase disappears completely.
- 4.8–5.0 s: a tiny gap with no script phrase on screen.
- 5.0–10.0 s: the second phrase "अपनी अगली पीढ़ी में पहुँचा सकता है।" is visible at the top of the frame, the word "अगली" golden in place and the rest bold white, popping in fully sharp at 5.0 s and holding to the end.
- 6.2 s: exactly as the words "अगली पीढ़ी" are visible in the written phrase on screen, one single downward arrow pops in below the carrier icon and, immediately with it, one empty rounded next-generation icon with no writing pops in below that arrow. Both hold to the end.
- 6.2–10.0 s: everything holds still, with only the very slow steady turn of the three dimensional plates. Nothing else moves, appears or disappears.
- 10.0 s: clip ends with the second phrase, the carrier icon with its "वाहक" label, the single downward arrow and the empty next-generation icon on screen.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "लेकिन वह इस जीन को"
2. "अपनी अगली पीढ़ी में पहुँचा सकता है।"
3. "HbA HbS" (on the carrier icon)
4. "वाहक" (the single white label plate on the carrier icon)

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, broken or malformed Devanagari letters, missing or wrong matras, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, people, faces, teachers, characters, avatars, hands, babies, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, invented labels, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, a new logo, a duplicated logo, a redrawn logo, a moved logo, a watermark of any kind, text or diagram overlapping either top corner, the downward arrow or the next-generation icon appearing before 6.2 seconds, the parent icons still visible after 3.0 seconds, the parent icons returning, a second arrow below the carrier, two next-generation icons, any writing on the next-generation icon, a second label plate, a second "वाहक", a second copy of "HbA HbS", an X chromosome, a Y chromosome, any sex chromosome, a pedigree square or circle, a human figure, a male or female symbol, a karyotype, the carrier drawn half-sick, cracked, split, partly red or marked with a warning sign, a sickled cell attached to the carrier, a sickle cell drawn as a smooth banana or a crescent moon with blunt ends, a red blood cell with a visible nucleus, a red blood cell drawn as a flat ring or doughnut with a hole, the spellings "HBs", "HBS", "HgB" or "Hgb", equations, any sphere, cell, fibre, capillary, DNA strand or bead chain
```

```
VIDEO PROMPT — SEGMENT 24 OF 28

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

VOICEOVER NARRATION (spoken audio): an energetic, warm Indian male biology teacher voice speaks this exact Hinglish narration during the clip — nothing more, nothing less. The same script also appears on screen word for word, one phrase at a time:
"तो बस इतना याद रखो — एक क्षार में परिवर्तन हुआ, उसके कारण एक अमीनो अम्ल बदल गया"

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
- THE SCENE CARRIED OVER FROM THE PREVIOUS CLIP: the carrier icon reading "HbA HbS" with its white "वाहक" label, the single downward arrow and the empty next-generation icon are already present at the very first frame and do not fade in again. Between 1.0 and 2.5 seconds this entire carried-over group shrinks smoothly to about half its size, drifts upward and fades away completely, leaving the area below the script text free. After 2.5 seconds nothing of it remains and it never comes back.
- THE RECAP CHAIN: a simple horizontal chain of rounded three dimensional boxes built after the carried-over scene is gone, sitting centred below the script text.
- BOX ONE: one rounded three dimensional box, glossy and glass-like with a faint specular highlight on its upper left, tinted soft cyan-blue, carrying the dark bold Devanagari text "क्षार" written once on its face on one single line. It appears at the time given in the timeline, then stays fixed — it never moves, never resizes and never duplicates.
- THE CHAIN ARROW: exactly ONE short thick three dimensional arrow, soft neutral white-grey with a small neat conical arrowhead, pointing horizontally from box one toward box two. It appears together with box two and never moves afterwards.
- BOX TWO: one rounded three dimensional box, identical in style and size to box one, tinted soft warm orange, carrying the dark bold Devanagari text "अमीनो अम्ल" written once on its face on one single line. It sits to the side of box one with the arrow between them. It never moves, never resizes and never duplicates.
- Both boxes sit side by side with a clear even gap, exactly the same size and exactly the same height, turning very slowly and steadily so their depth reads clearly.
- LABELS: this clip has NO label plates at all after the carried-over "वाहक" label fades away with the rest of the previous scene. Never invent a label. The only writing inside the diagram after 2.5 seconds is the text on the two boxes.
- No cell, no chromosome, no DNA strand, no haemoglobin molecule and no bead chain is drawn in this clip — the recap chain is boxes and one arrow only.

DIAGRAM TIMING SYNC (CRITICAL): every object appears at the exact moment its name is visible in the written phrase on screen, and never a frame before. The diagram carried over from the previous clip is already present at the very first frame and does not fade in again. Box one appears at 4.2 seconds, exactly while the word "क्षार" is visible inside the written second phrase on screen. Box two and the arrow between the boxes appear together at 8.2 seconds, exactly while the words "अमीनो अम्ल" are visible inside the written third phrase on screen. Once an object appears it stays to the end of the clip.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE. Every word appears exactly the number of times it is written.
- EXACT COUNT: the word "क्षार" appears exactly TWICE in total in this clip — once inside the second phrase of the script text and once on the face of box one. Nowhere else, in any size, at any moment.
- EXACT COUNT: the words "अमीनो अम्ल" appear exactly TWICE in total in this clip — once inside the third phrase of the script text and once on the face of box two. Nowhere else, in any size, at any moment.
- EXACT COUNT: the word "एक" appears exactly TWICE in total in this clip — once inside the second phrase and once inside the third phrase. It appears only once inside each of those phrases and never a third time anywhere.
- The line "HbA HbS" and the word "वाहक" appear only on the carried-over scene during the first 2.5 seconds, exactly once each, and never again after it fades. They are never redrawn.
- This clip has NO label plates at all in the recap chain. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol. Every Hindi word is rendered in correct clean Devanagari with all matras and conjuncts exactly as written.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated. In this clip the FIRST phrase has exactly ONE golden word — "याद" — styled in place inside the sentence. The SECOND and THIRD phrases are rendered COMPLETELY UNIFORM in bold white with NO golden word, because their words also appear on the boxes and the word "एक" is repeated across them.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time, perfectly synced with the voiceover. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean, glossy, textbook-style biology illustration rendered in three dimensions — smooth shapes, flat bright colours, soft even glow, like a modern NCERT diagram built in 3D. Never photorealistic. NO fire, NO flame, NO burning, NO spark, NO ember, NO explosion, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: continuing exactly from the previous clip — the carrier icon reading "HbA HbS" with its single white "वाहक" label, one downward arrow below it, and one empty next-generation icon with no writing. No script text yet. Nothing else.

ANIMATION TIMELINE:
- 0.0 s: the carried-over scene is already on screen exactly as it ended in the previous clip, still and sharp. It does not fade in again.
- 0.0–3.3 s: the first phrase "तो बस इतना याद रखो —" is visible at the top of the frame, the word "याद" golden in place and the rest bold white, popping in fully sharp at 0.0 s and holding.
- 1.0–2.5 s: the whole carried-over group shrinks to about half its size, drifts upward and fades away completely. By 2.5 s the area below the script text is empty background.
- 3.3 s: the first phrase disappears completely.
- 3.3–3.5 s: a tiny gap with no script phrase on screen.
- 3.5–6.6 s: the second phrase "एक क्षार में परिवर्तन हुआ," is visible at the top of the frame in uniform bold white, popping in fully sharp at 3.5 s and holding.
- 4.2 s: exactly while the word "क्षार" is visible inside the written phrase on screen, box one pops in below the script text, reading "क्षार" on its face, and holds still to the end.
- 6.6 s: the second phrase disappears completely.
- 6.6–6.8 s: a tiny gap with no script phrase on screen. Box one stays untouched.
- 6.8–10.0 s: the third phrase "उसके कारण एक अमीनो अम्ल बदल गया" is visible at the top of the frame in uniform bold white, popping in fully sharp at 6.8 s and holding to the end.
- 8.2 s: exactly while the words "अमीनो अम्ल" are visible inside the written phrase on screen, box one slides slightly to one side to make room and the single horizontal arrow pops in beside it together with box two reading "अमीनो अम्ल". Both hold still to the end.
- 8.2–10.0 s: the two boxes and the arrow hold still, with only the very slow steady turn of the three dimensional boxes. Nothing else moves, appears or disappears.
- 10.0 s: clip ends with the third phrase on screen and the two-box chain "क्षार" arrow "अमीनो अम्ल" below it.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "तो बस इतना याद रखो —"
2. "एक क्षार में परिवर्तन हुआ,"
3. "उसके कारण एक अमीनो अम्ल बदल गया"
4. "HbA HbS" (only on the carried-over carrier icon, until it fades by 2.5 seconds)
5. "वाहक" (only on the carried-over label, until it fades by 2.5 seconds)
6. "क्षार" (on box one)
7. "अमीनो अम्ल" (on box two)

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, broken or malformed Devanagari letters, missing or wrong matras, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, invented labels, any label plate in the recap chain, any chip, any callout, any leader line, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, a new logo, a duplicated logo, a redrawn logo, a moved logo, a watermark of any kind, text or diagram overlapping either top corner, box one appearing before 4.2 seconds, box two or the chain arrow appearing before 8.2 seconds, the carried-over carrier icon still visible after 2.5 seconds, the carried-over scene returning, a third box, a second arrow in the chain, a second copy of "क्षार", a second copy of "अमीनो अम्ल", boxes of unequal size, a golden word in the second or third phrase, any DNA helix, a left-handed DNA helix, the letter U in any triplet, a chromosome, an X chromosome, a Y chromosome, a pedigree symbol, a haemoglobin molecule, a bead chain, a red blood cell with a visible nucleus, a red blood cell drawn as a flat ring or doughnut with a hole, a sickle cell drawn as a smooth banana or a crescent moon with blunt ends, the spellings "HBs", "HBS", "HgB" or "Hgb", equations, any sphere, cell, fibre or capillary
```

Notes on decisions baked in (flag if you disagree):
- **Seg 21 has no golden word at all** — `जीन` repeats across phrases and P2 carries Latin `HbA HbS`; both phrases are uniform white per the style rule.
- **Seg 22 P1 is uniform** (not golden on `वाहक`) because `वाहक` also appears on the label plate — golden + label was the exact shape of bug #7/#9. Golden moved to `लक्षण` in P2.
- **Seg 23** fades the parents out mid-clip so the carrier line reads cleanly; the next-generation icon stays deliberately blank (no genotype implied).
- **Seg 24** carries the recap-chain build in-clip, so its end state matches your plan (`क्षार` → `अमीनो अम्ल`) for Seg 25 to extend to three boxes.
- Accuracy bans (nucleus, doughnut RBC, blunt banana sickle, GUG, α-chain mutation, X/Y symbols, half-sick carrier) are in every NEGATIVE, plus a carrier-specific "never drawn half-sick/cracked/partly red" clause in the diagram specs of 22 and 23.

Frames read — they confirm the house look I'll lock into the diagram spec: crescent **pointed at both ends** (one concave edge, one convex), red cell body, blue HbS fibre rods inside, biconcave disc drawn with a dimple (never a hole). Segments 25–28 below.

**Note on Seg 25→26 continuity:** Seg 25 opens exactly on your stated end-state (box 1 `क्षार` → arrow → box 2 `अमीनो अम्ल`), builds box 3 `आकार` + the sickle cell, and turns the whole chain green. Seg 26 fades that chain out by 2.5 s. Segs 27–28 are TEXT_ONLY.

---

```
VIDEO PROMPT — SEGMENT 25 OF 28

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

VOICEOVER NARRATION (spoken audio): an energetic, warm Indian male biology teacher voice speaks this exact Hinglish narration during the clip — nothing more, nothing less. The same script also appears on screen word for word, one phrase at a time:
"और इसके परिणामस्वरूप लाल रक्त कोशिका का आकार बदल गया। यही परिवर्तन आगे चलकर सिकल सेल एनीमिया का कारण बनता है।"

AUDIO: only the voiceover above. No background music. Only very soft whoosh and pop sounds on text animations are allowed.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, starting close to the top edge. The diagram sits directly below the script text and fills the space between the text and the invisible middle line, so the top half never looks empty. The lowest part of the diagram stops with a clear visible gap above the invisible middle line and never touches it; if it does not fit, make it smaller. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

LOGO SAFE AREA: keep the top-left corner and the top-right corner of the frame completely clear of script text, diagram, equation, labels and any moving element for the whole clip — only the background itself shows there. Do not draw, copy, move, recreate or animate any logo, wordmark, badge or watermark anywhere in the frame; the logo already present on the supplied background must stay exactly where it is, unchanged.

3D RENDER QUALITY (CRITICAL — THIS MAKES THE DIAGRAM LOOK THREE DIMENSIONAL):
The diagram is a real three dimensional object rendered in depth, not a flat drawing.
- CAMERA: a fixed three-quarter view from slightly above the object, so the viewer looks slightly down at it and can clearly read its roundness. Never a flat straight-on front view.
- PERSPECTIVE: circles that run around the object appear as flattened ellipses because of the viewing angle, becoming flatter near the top and bottom and rounder near the middle. Nothing is drawn as a plain flat circle.
- DEPTH: the parts nearest the camera are brighter, thicker and sharper. The parts on the far side are noticeably dimmer, thinner and softer. This difference is clear and obvious.
- LIGHTING: one soft cool rim light along the upper left edge and a gentle ambient fill, giving a rounded sculpted look with a soft falloff toward the lower right.
- MATERIAL: a smooth glossy surface with a faint specular highlight near the upper left, and a soft inner glow.
- FORESHORTENING: any arrow pointing toward the camera looks shorter and thicker with a larger arrowhead, and any arrow pointing away looks longer and thinner. They are never all the same length on screen.
- MOTION: the object turns very slowly and steadily around its vertical axis so the depth reads clearly. It never wobbles, never squashes, never deforms and never changes size once settled.

DIAGRAM SPECIFICATION (build exactly this, nothing else):
- THE RECAP CHAIN (carried over): two flat rounded boxes with thin white outlines, side by side in a single horizontal row directly below the script text, joined left to right by one short white arrow. The left box contains the dark bold word "क्षार". The right box contains the dark bold words "अमीनो अम्ल". Both boxes and the arrow are already present at the very first frame, exactly as they ended the previous clip, and they do not fade in again, do not move and do not resize.
- THE THIRD BOX: exactly ONE additional flat rounded box with a thin white outline, appearing to the right of the second box in the same single horizontal row, joined to it by one short white arrow identical in style to the first arrow. It contains the dark bold word "आकार". It appears only at the time given in the timeline. The finished chain is exactly THREE boxes and exactly TWO arrows — never four boxes, never a second row, never a stacked column.
- THE SICKLE CELL: one red blood cell rendered in full three dimensions, positioned beside and slightly below the third box, small enough that the whole chain and the cell together stay clearly above the invisible middle line. Its shape is a crescent, a हँसिया — clearly POINTED at BOTH ends, with one smoothly concave inner edge and one convex outer edge. It is uniform deep red with a glossy surface and a soft cool rim light along the upper left. Inside it, three or four long straight rigid blue-violet fibre rods run lengthwise along the curve of the crescent, visible faintly through the red surface. The cell has NO nucleus, NO dark central blob, NO hole and NO ring. It is not a banana, not a smooth crescent moon with blunt rounded ends, not a star and not a spiky shape. It turns very slowly and steadily and never deforms once settled.
- LABELS: this clip has NO label plates at all. The only words in the diagram are the words printed inside the three boxes. Never invent a label.

DIAGRAM TIMING SYNC (CRITICAL): every object appears at the exact moment its name is visible in the written phrase on screen, and never a frame before. Once an object appears it stays to the end of the clip. The diagram carried over from the previous clip is already present at the very first frame and does not fade in again.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE. Every word appears exactly the number of times it is written.
- EXACT COUNT: the word "आकार" appears exactly TWICE in total in this clip — once inside the first phrase and once inside the third box of the chain. Nowhere else, in any size, at any moment.
- EXACT COUNT: the word "का" appears exactly TWICE in total in this clip — once inside the first phrase and once inside the third phrase. Nowhere else.
- EXACT COUNT: the word "क्षार" appears exactly ONCE, inside the first box. The words "अमीनो अम्ल" appear exactly ONCE, inside the second box.
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol, with every matra and every conjunct correct.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated.
In this clip: in the first phrase the single golden word is "कोशिका". In the second phrase the single golden word is "परिवर्तन". In the third phrase the single golden word is "कारण". No other word is golden.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time, perfectly synced with the voiceover. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean, glossy, textbook-style biology illustration rendered in three dimensions — smooth shapes, flat bright colours, soft even glow, like a modern NCERT diagram built in 3D. Never photorealistic. NO fire, NO flame, NO burning, NO spark, NO ember, NO explosion, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: continuing exactly from the previous clip — one rounded box reading "क्षार", one short white arrow, and one rounded box reading "अमीनो अम्ल", sitting in a single horizontal row below where the script text will appear. Nothing else.

ANIMATION TIMELINE:
0.0–3.3 s: phrase 1 "और इसके परिणामस्वरूप लाल रक्त कोशिका का आकार बदल गया।" pops in at the top of the frame. The two carried-over boxes and their arrow stay exactly where they are.
At 1.4 s, exactly as the word "कोशिका" is visible on screen inside the phrase, the sickle-shaped red blood cell pops in to the right of the second box, slightly below the chain row, and begins its very slow steady turn.
At 2.2 s, exactly as the word "आकार" is visible on screen inside the phrase, the second white arrow and the third box reading "आकार" pop in together, completing the single horizontal chain.
3.3–3.5 s: phrase 1 is fully gone. No phrase on screen. The chain and the cell hold.
3.5–6.6 s: phrase 2 "यही परिवर्तन आगे चलकर" pops in. Nothing else changes.
6.6–6.8 s: phrase 2 is fully gone. No phrase on screen.
6.8–10.0 s: phrase 3 "सिकल सेल एनीमिया का कारण बनता है।" pops in.
At 8.2 s all three box outlines and both arrows turn bright green in place and glow softly, and the words inside the boxes stay exactly where they are without being redrawn or duplicated. The chain, the green glow and the cell hold to 10.0 s.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "और इसके परिणामस्वरूप लाल रक्त कोशिका का आकार बदल गया।"
2. "यही परिवर्तन आगे चलकर"
3. "सिकल सेल एनीमिया का कारण बनता है।"
4. "क्षार"
5. "अमीनो अम्ल"
6. "आकार"

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, broken or misformed Devanagari conjuncts, missing or misplaced matras, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, invented labels, any label plate, any chip, any callout, any leader line, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, a flat two dimensional drawing instead of a three dimensional cell, a straight-on front view with no depth, a fourth box, a second row of boxes, a third arrow, a second copy of the word "आकार" outside the third box, the sickle cell appearing before 1.4 seconds, the third box appearing before 2.2 seconds, a red blood cell with a visible nucleus, a dark blob drawn inside the red blood cell, a red blood cell drawn as a flat circle, a red blood cell drawn as a ring or doughnut with a hole in the middle, a sickle cell shaped like a smooth banana, a crescent with blunt rounded ends, a star-shaped or spiky cell, a blue or purple red blood cell, a normal biconcave disc in this clip, DNA, a helix, chromosomes, sex chromosomes, an X or Y symbol, a pedigree chart, parent or child icons, equations, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, a new logo, a duplicated logo, a redrawn logo, a moved logo, a watermark of any kind, text or diagram overlapping either top corner
```

---

```
VIDEO PROMPT — SEGMENT 26 OF 28

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

VOICEOVER NARRATION (spoken audio): an energetic, warm Indian male biology teacher voice speaks this exact Hinglish narration during the clip — nothing more, nothing less. The same script also appears on screen word for word, one phrase at a time:
"बस इतना समझ लिया, तो परीक्षा में चार नंबर पक्के।"

AUDIO: only the voiceover above. No background music. Only very soft whoosh and pop sounds on text animations are allowed.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, starting close to the top edge. The diagram sits directly below the script text and fills the space between the text and the invisible middle line, so the top half never looks empty. The lowest part of the diagram stops with a clear visible gap above the invisible middle line and never touches it; if it does not fit, make it smaller. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

LOGO SAFE AREA: keep the top-left corner and the top-right corner of the frame completely clear of script text, diagram, equation, labels and any moving element for the whole clip — only the background itself shows there. Do not draw, copy, move, recreate or animate any logo, wordmark, badge or watermark anywhere in the frame; the logo already present on the supplied background must stay exactly where it is, unchanged.

3D RENDER QUALITY (for the diagram in the first part of this clip):
The diagram is a real three dimensional object rendered in depth, not a flat drawing — a fixed three-quarter view from slightly above, curved surfaces appearing as flattened ellipses, near-side edges brighter and sharper than far-side edges, a soft cool rim light along the upper left edge, glossy material with a faint specular highlight, and a very slow steady turn around the vertical axis.

DIAGRAM SPECIFICATION: the scene from the previous clip — the single horizontal chain of exactly three rounded boxes reading "क्षार", "अमीनो अम्ल" and "आकार", joined by exactly two short white arrows, all outlined in glowing green, together with the three dimensional crescent-shaped red sickle cell beside the third box, pointed at both ends with one concave and one convex edge and long straight blue-violet fibre rods inside it — is present at the very first frame. It shrinks smoothly to about half its size, drifts upward, and fades away completely by 2.5 seconds, leaving the space below the script text as plain empty background for the rest of the clip. From 2.5 seconds to 10.0 seconds there is NO object of any kind on screen — no cell, no box, no arrow, no shape, no icon and no illustration — only the script text and the plain background. LABELS: this clip has NO labels at all. Never invent a label.

DIAGRAM TIMING SYNC (CRITICAL): the carried-over diagram is already present at the very first frame and does not fade in again. Nothing new ever appears in this clip except the script text.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE. Every word appears exactly the number of times it is written.
- EXACT COUNT: the words "क्षार", "अमीनो अम्ल" and "आकार" each appear exactly ONCE in this clip, only inside the carried-over boxes during the first 2.5 seconds, and never again after the boxes have faded.
- The word "चार" is written as this Devanagari word only. NEVER render it as a digit, a numeral or an English word.
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol, with every matra and every conjunct correct.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated.
In this clip: in the first phrase the single golden word is "समझ". In the second phrase the single golden word is "पक्के". No other word is golden.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time, perfectly synced with the voiceover. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean, glossy, textbook-style biology illustration rendered in three dimensions for the fading diagram, and clean crisp flat overlay typography for the text. Never photorealistic. NO fire, NO flame, NO burning, NO spark, NO ember, NO explosion, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: continuing exactly from the previous clip — the green-glowing horizontal chain of three rounded boxes reading "क्षार", "अमीनो अम्ल" and "आकार" joined by two short white arrows, with the crescent-shaped red sickle cell beside the third box. Nothing else.

ANIMATION TIMELINE:
0.0–4.8 s: phrase 1 "बस इतना समझ लिया," pops in at the top of the frame.
0.0–2.5 s: the carried-over chain and the sickle cell shrink smoothly to about half size, drift upward and fade out completely, finishing fully invisible at 2.5 s.
2.5–10.0 s: the area below the script text is plain empty background. Nothing appears there at any moment.
4.8–5.0 s: phrase 1 is fully gone. No phrase on screen.
5.0–10.0 s: phrase 2 "तो परीक्षा में चार नंबर पक्के।" pops in and holds to 10.0 s.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "बस इतना समझ लिया,"
2. "तो परीक्षा में चार नंबर पक्के।"
3. "क्षार" (only inside the carried-over first box, before it fades)
4. "अमीनो अम्ल" (only inside the carried-over second box, before it fades)
5. "आकार" (only inside the carried-over third box, before it fades)

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, broken or misformed Devanagari conjuncts, missing or misplaced matras, the word "चार" written as a digit or numeral, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, invented labels, any label plate, any chip, any callout, any leader line, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, the chain or the cell still visible after 2.5 seconds, the chain or the cell fading back in, any new object appearing after 2.5 seconds, any sphere, ball, cell, box, arrow, shape, icon or illustration appearing in the second half of the clip, a red blood cell with a visible nucleus, a red blood cell drawn as a flat circle, a red blood cell drawn as a ring or doughnut with a hole in the middle, a sickle cell shaped like a smooth banana, a crescent with blunt rounded ends, a star-shaped or spiky cell, a blue or purple red blood cell, DNA, a helix, chromosomes, sex chromosomes, an X or Y symbol, a pedigree chart, equations, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, a new logo, a duplicated logo, a redrawn logo, a moved logo, a watermark of any kind, text or diagram overlapping either top corner
```

---

```
VIDEO PROMPT — SEGMENT 27 OF 28

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

VOICEOVER NARRATION (spoken audio): an energetic, warm Indian male biology teacher voice speaks this exact Hinglish narration during the clip — nothing more, nothing less. The same script also appears on screen word for word, one phrase at a time:
"और अगर देखना है कि इसे परीक्षा में कैसे लिखना है, तो इसका उत्तर आपकी स्क्रीन पर आएगा।"

AUDIO: only the voiceover above. No background music. Only very soft whoosh and pop sounds on text animations are allowed.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, filling the width, starting close to the top edge, large enough to fill the upper area comfortably. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

LOGO SAFE AREA: keep the top-left corner and the top-right corner of the frame completely clear of script text, diagram, equation, labels and any moving element for the whole clip — only the background itself shows there. Do not draw, copy, move, recreate or animate any logo, wordmark, badge or watermark anywhere in the frame; the logo already present on the supplied background must stay exactly where it is, unchanged.

NO DIAGRAM IN THIS CLIP (CRITICAL): this clip contains NO three dimensional object of any kind. There is no cell, no red blood cell, no sickle cell, no haemoglobin, no DNA, no helix, no chromosome, no box, no arrow, no fibre, no capillary, no parent or child icon, no shape, no icon and no illustration anywhere in the frame at any moment. The only things on screen are the script text and the plain background. Do not invent, add or imagine any diagram, object or graphic. The space below the script text stays as plain empty background.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE. Every word appears exactly the number of times it is written.
- EXACT COUNT: the word "है" appears exactly TWICE in total in this clip — once at the end of the first phrase and once at the end of the second phrase. Nowhere else, in any size, at any moment.
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol, with every matra and every conjunct correct.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated.
In this clip: in the first phrase the single golden word is "देखना". In the second phrase the single golden word is "लिखना". In the third phrase the single golden word is "उत्तर". No other word is golden.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time, perfectly synced with the voiceover. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean crisp flat overlay typography on a dark technical background. Never photorealistic. NO fire, NO flame, NO sparks, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: completely empty background. Nothing at all.

ANIMATION TIMELINE:
0.0–3.3 s: phrase 1 "और अगर देखना है कि" pops in at the top of the frame. Nothing else is on screen.
3.3–3.5 s: phrase 1 is fully gone. No phrase on screen.
3.5–6.6 s: phrase 2 "इसे परीक्षा में कैसे लिखना है," pops in. Nothing else is on screen.
6.6–6.8 s: phrase 2 is fully gone. No phrase on screen.
6.8–10.0 s: phrase 3 "तो इसका उत्तर आपकी स्क्रीन पर आएगा।" pops in and holds to 10.0 s. The space below the text stays plain empty background throughout.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "और अगर देखना है कि"
2. "इसे परीक्षा में कैसे लिखना है,"
3. "तो इसका उत्तर आपकी स्क्रीन पर आएगा।"

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, broken or misformed Devanagari conjuncts, missing or misplaced matras, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, invented labels, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, any cell, red blood cell, sickle cell, haemoglobin, DNA, helix, chromosome, box, arrow, fibre, capillary, parent or child icon, shape, icon or illustration of any kind, a screen, a phone, a mockup, a card, a button, an arrow pointing to anything, any label plate, equations, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, a new logo, a duplicated logo, a redrawn logo, a moved logo, a watermark of any kind, text or diagram overlapping either top corner
```

---

```
VIDEO PROMPT — SEGMENT 28 OF 28

Duration: exactly 10 seconds. Vertical video 9:16 (1080 x 1920). One continuous scene, no cuts.

VOICEOVER NARRATION (spoken audio): an energetic, warm Indian male biology teacher voice speaks this exact Hinglish narration during the clip — nothing more, nothing less. The same script also appears on screen word for word, one phrase at a time:
"इसे सुरक्षित कर लेना और बाद में दोबारा पढ़ने के लिए इसका स्क्रीनशॉट लेना मत भूलना।"

AUDIO: only the voiceover above. No background music. Only very soft whoosh and pop sounds on text animations are allowed.

FRAME LAYOUT (CRITICAL — MUST NOT BE BROKEN):
Imagine an invisible horizontal line running across the exact middle of the frame. EVERYTHING in this video is placed ABOVE that invisible line, in the top half of the frame. The script text sits at the very top of the frame, filling the width, starting close to the top edge, large enough to fill the upper area comfortably. The BOTTOM HALF of the frame, below the invisible middle line, stays COMPLETELY EMPTY for the whole clip: only the plain background is visible there, with no text, no letters, no numbers, no symbols, no diagram, no glow, no shadow, no reflection and no marks of any kind. This clear space is reserved for a presenter who will be added later in editing. The invisible middle line is a composition guide only. It is NEVER drawn — no line, no edge, no band, no seam, no divider and no border is ever visible anywhere on screen. NEVER write any measurement, percentage, number of pixels, coordinate, zone name, band name, layout note or any instruction from this description as visible text in the video. There are no annotations, no guides, no rulers and no layout labels anywhere in the frame.

LOGO SAFE AREA: keep the top-left corner and the top-right corner of the frame completely clear of script text, diagram, equation, labels and any moving element for the whole clip — only the background itself shows there. Do not draw, copy, move, recreate or animate any logo, wordmark, badge or watermark anywhere in the frame; the logo already present on the supplied background must stay exactly where it is, unchanged.

NO DIAGRAM IN THIS CLIP (CRITICAL): this clip contains NO three dimensional object of any kind. There is no cell, no red blood cell, no sickle cell, no haemoglobin, no DNA, no helix, no chromosome, no box, no arrow, no fibre, no capillary, no parent or child icon, no shape, no icon and no illustration anywhere in the frame at any moment. The only things on screen are the script text and the plain background. Do not invent, add or imagine any diagram, object or graphic. The space below the script text stays as plain empty background.

TEXT CORRECTNESS RULES (CRITICAL — THIS FIXES DOUBLE TEXT):
- Only ONE script phrase is visible at any moment. The previous phrase must FULLY disappear first, then a tiny 0.2 second gap of no phrase, then the next phrase appears. NEVER crossfade or overlap two phrases — crossfading creates double text.
- Every text in this clip is rendered EXACTLY ONE time. Never show two copies of the same text, word or sentence anywhere on screen.
- NEVER REPEAT A WORD INSIDE A PHRASE. Every word appears exactly the number of times it is written.
- EXACT COUNT: the word "लेना" appears exactly TWICE in total in this clip — once inside the first phrase and once inside the third phrase. Nowhere else, in any size, at any moment.
- The word "पढ़ने" carries a nukta under the letter and must be rendered exactly as written, with the nukta present and correctly placed.
- This clip has NO label plates at all. No plate, no chip, no floating letter, no leader line, no stray symbol. Never invent a label.
- No overlapping text layers, no ghost text, no echo text, no semi-transparent duplicate text, no mirrored text, no shadow copies of text.
- Text must be sharp, clean, and spelled EXACTLY as written — letter by letter, symbol by symbol, with every matra and every conjunct correct.
- Do not invent or add ANY text, letter, number, dot, bullet, punctuation mark or symbol that is not written in this prompt.

TEXT STYLE RULE: A phrase that contains a mathematical symbol, a standalone single letter, or the same word twice is rendered COMPLETELY UNIFORM in bold white rounded letters with a soft dark shadow, all the same colour, size and weight, with NO golden word. Only a phrase with none of those may have ONE golden key word, always a single simple word with no apostrophe and no hyphen, styled in place inside the sentence, never written again anywhere else. Every phrase sits on at most three short centred lines with clear space between them. A word is never split across two lines and never hyphenated.
In this clip: in the first phrase the single golden word is "सुरक्षित". In the second phrase the single golden word is "दोबारा". In the third phrase the single golden word is "स्क्रीनशॉट". No other word is golden.

TEXT ENTRY AND EXIT RULE (CRITICAL — THIS FIXES GARBLED TEXT): Every text element appears with a simple clean pop: it fades in and scales up slightly over 0.15 seconds, and it is FULLY SHARP AND CORRECTLY SPELLED FROM THE VERY FIRST VISIBLE FRAME. NEVER animate letters individually. NEVER morph one phrase into another. NEVER scramble, warp, stretch, squeeze, distort, blur, type out letter by letter, or slide letters into position one at a time. There must be no frame anywhere in this clip where letters are half-formed, merged, stuttered, mid-transformation or partially readable. The outgoing phrase must be completely invisible before the incoming phrase begins to appear.

SCRIPT TEXT ON SCREEN: the COMPLETE script of this clip appears on screen word for word, as big animated kinetic typography — ONE phrase at a time, perfectly synced with the voiceover. Do NOT change, shorten, translate, paraphrase, or skip a single word. There is no background panel, box, plate or caption bar behind the script text.

STRICT FRAME LAYOUT: TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher, NO character, NO face, NO hands at any moment.

VISUAL STYLE: clean crisp flat overlay typography on a dark technical background. Never photorealistic. NO fire, NO flame, NO sparks, NO smoke.

BACKGROUND (identical in every segment): the supplied background image is the background for the entire clip, used exactly as provided, completely unchanged from the very first frame to the very last. Its colour, texture, grid, lighting and every mark already on it stay exactly as they are — nothing on the background is redrawn, recoloured, brightened, darkened, blurred, replaced, extended, cropped, shifted, scaled or animated at any moment. No new background is generated. All animated elements sit ON TOP of this unchanged background. The background looks exactly the same in the upper half and the lower half — no split, no seam, no dividing line, no separate panels, no colour change, no vignette and no band across the middle. Camera fully locked and static.

SCREEN AT START: completely empty background. Nothing at all.

ANIMATION TIMELINE:
0.0–3.3 s: phrase 1 "इसे सुरक्षित कर लेना और" pops in at the top of the frame. Nothing else is on screen.
3.3–3.5 s: phrase 1 is fully gone. No phrase on screen.
3.5–6.6 s: phrase 2 "बाद में दोबारा पढ़ने के लिए" pops in. Nothing else is on screen.
6.6–6.8 s: phrase 2 is fully gone. No phrase on screen.
6.8–10.0 s: phrase 3 "इसका स्क्रीनशॉट लेना मत भूलना।" pops in and holds, still and sharp, right through to 10.0 s. The clip ends with this phrase on screen. The space below the text stays plain empty background throughout.

MANDATORY ON-SCREEN TEXT — every line below MUST appear exactly ONCE, spelled exactly like this, never duplicated:
1. "इसे सुरक्षित कर लेना और"
2. "बाद में दोबारा पढ़ने के लिए"
3. "इसका स्क्रीनशॉट लेना मत भूलना।"

NEGATIVE (must never appear): any percentage sign, any measurement, any pixel number, any coordinate, any zone name, any band name, any layout note, any ruler, any guide line, any annotation about the composition, a visible line or seam across the middle of the frame, any text or graphic in the bottom half of the frame, anything touching or crossing the middle of the frame, two phrases visible at the same time, garbled letters during a transition, broken or misformed Devanagari conjuncts, missing or misplaced matras, a missing nukta, fire, flames, sparks, embers, smoke, floating particles, bokeh dots, specks, light streaks, stray dots, stray punctuation marks, people, faces, teachers, characters, avatars, hands, double text, duplicated text, two copies of the same sentence, a repeated word, a repeated key word, a keyword written as a separate line, invented labels, stray floating letters or symbols, overlapping text, overlapping plates, ghost text, echo text, semi-transparent duplicate text, mirrored text, gibberish words, misspelled words, broken words split across lines, merged letters, half-formed letters, morphing or warping text, letters sliding or scrambling into place, distorted letters, missing text lines, extra unwanted text, watermark, an automatic subtitle bar at the bottom, random symbols, camera movement, zoom, scene change, background change, any cell, red blood cell, sickle cell, haemoglobin, DNA, helix, chromosome, box, arrow, fibre, capillary, parent or child icon, shape, icon or illustration of any kind, a camera icon, a screenshot icon, a save icon, a bookmark icon, a phone or screen mockup, a button, a like or subscribe graphic, any label plate, equations, the final phrase fading out before 10.0 seconds, a regenerated background, a redrawn background, a replaced background, a second background layer, the background being recoloured, the background being blurred, the background grid changing, the background sliding or drifting, a border or frame added around the background, the supplied background being cropped or zoomed, a new logo, a duplicated logo, a redrawn logo, a moved logo, a watermark of any kind, text or diagram overlapping either top corner
```

---

**Two things to flag:**

1. **Seg 26's `चार`** — I locked it as the Devanagari word with an explicit ban on rendering it as a digit, per your Step 1 fix #4.
2. **Devanagari risk stands** (your flag C). Segs 27–28 are the safest ones to test first (pure text, no diagram, no Latin mixing) — if `पढ़ने`, `स्क्रीनशॉट` and `परिणामस्वरूप` render cleanly, the rest of the pack is viable. Test Seg 28 before committing to the other 27.

I read the three reference frames, but I can't write Segments 29–32 yet — **the plan tops out at 28.**

The continuity line you gave me ("nothing — final phrase holds to 10.0 s, clip ends") is Segment **28**'s end state, i.e. the end of the CTA (`इसका स्क्रीनशॉट लेना मत भूलना।`). There is no script text, no phrase split, no type/diagram assignment and no end-state chain for 29, 30, 31 or 32. Writing them would mean inventing Hinglish/Hindi narration — and the whole point of this pipeline is that on-screen text is the script **word for word**. Invented words would go to TTS and to the screen verbatim.

**What I need (one of these):**

1. **The words for 29–32** — ~16–20 words each. Are these a new CLIP 9 (extra content after the CTA), or the tail of a *re-split* script? If the latter, the earlier segment boundaries shift too and I'd need the new map, not just the last four.
2. **Or: you meant 25–28** (the last four of the existing plan — recap chain + CTA). Say the word and I'll write those four in full immediately; I have everything I need for them, including the continuity chain.

Also still open from the plan, and they change the text inside these blocks:

- **Flag A/B** — `अलिंगसूत्री अप्रभावी` instead of `अलिंगी गुणसूत्रीय`? `HBB जीन` in Latin? (Affects Seg 5, 18, 21.)
- **28 vs ~20 segments** — unresolved. If you're extending to 32, the drift risk gets worse, not better.

**One thing the frames did settle** — they're good accuracy references and I'll build the diagram specs off them, with two corrections baked into the NEGATIVEs:

- Frame 1's top-view RBC reads close to a **bowl/doughnut** — deep open central well. The spec will say dimple on **both** faces, shallow, never a ring, never a hole, and I'll keep the `अनुप्रस्थ काट` dumbbell view as the shape anchor.
- Frames 3 show HbA/HbS as **blue** dots inside a red cell. That's fine as a convention, but it collides with the skill's fixed colour system (cyan-blue = surfaces/field lines). I'll keep haemoglobin blue-violet and reserve cyan for nothing in this pack — flagging so it's a decision, not a drift.

Frame 3's causal order (`O₂ कमी` → HbS fibres → sickle) matches the brief and the Seg 10→11→12 split exactly. Sickle shape in both frames is correctly pointed at both ends, one concave/one convex edge — that's the shape I'll spec.

Give me the four segments' words (or confirm you meant 25–28) and I'll write them out complete, every block, uploaded-background §15 + §16 logo safe area in each.