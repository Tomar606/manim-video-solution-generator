# विटामिन्स — परिभाषा, वर्गीकरण और रोग-विटामिन जोड़े

## GLOBAL VISUAL STRATEGY

**Teaching objective:** two things — define vitamins, then give the vitamin for
each named disease. The question is *"विटामिन्स क्या हैं? उन विटामिन्स के नाम
लिखिये जिनकी कमी से निम्नलिखित बीमारियाँ उत्पन्न होती हैं"*, so the second half
is a **disease → vitamin** lookup, in that direction. The script's own On Screen
directions confirm it: every one is a row of *रोग | विटामिन | रासायनिक नाम*.

**Key concepts:** definition (complex organic compounds, needed in small amounts,
not synthesised in the body, deficiency causes specific diseases), the exception
(calciferol from sunlight, phylloquinone from gut bacteria), the fat/water
solubility split, then five or six disease→vitamin pairs.

**Visual language:** part 1 is a definition card and a two-group classification.
Part 2 is a **three-column table keyed on the DISEASE**, filling one row per pair
— matching both the question's direction and the script's directions.

**Main visual assets:** definition card; the exception callout; the fat/water
solubility split; the disease→vitamin→chemical-name table.

**Avatar strategy:** MODE A over the hook; MODE B for the definition and the
classification; MODE C once the table has more than three rows.

**NOTE ON PART 2:** its recording was never transcribed, which is why this video
never completed in batch 1. The part-2 scenes below are planned against the
script's On Screen directions and the question; timings are attached once the
transcription lands, and any scripted row with no spoken moment is dropped, not
forced in.

---

# PART 1

# SCENE 01
TIME: 00:15 – 00:23
NARRATION: "सबसे पहले समझते हैं विटामिन किसे कहते हैं और डेफिनिशन ध्यान से सुनना, क्योंकि एग्ज़ाम में यही लाइन लिखोगे तो नंबर मिलेंगे।"
TEACHING INTENT: TRANSITION + WARNING
VISUAL DECISION: **VISUAL: NONE**
WHY: he is announcing the definition, not giving it. Batch 1 put a food
photograph over this exact stretch — over the MP Board hook, in fact.
AVATAR: MODE A — large, bottom-centre.
IMPLEMENTATION: NONE

---

# SCENE 02
TIME: 00:23 – 00:40
NARRATION: "विटामिन जटिल कार्बनिक यौगिक हैं, जो शरीर की सामान्य वृद्धि, स्वास्थ्य तथा चयापचय के लिए अल्प मात्रा में आवश्यक होते हैं। ये शरीर में संश्लेषित नहीं होते हैं या अपर्याप्त मात्रा में बनते हैं। इनकी कमी से विशिष्ट रोग उत्पन्न होते हैं।"
TEACHING INTENT: DEFINITION
VISUAL DECISION: the definition as three numbered clauses, filling as he says
them — it is a three-clause definition and the student writes all three.
WHAT APPEARS:
  - heading **विटामिन — परिभाषा**
  - ① **जटिल कार्बनिक यौगिक — अल्प मात्रा में आवश्यक**  (00:23)
  - ② **शरीर में संश्लेषित नहीं होते / अपर्याप्त बनते हैं**  (00:32)
  - ③ **कमी से विशिष्ट रोग**  (00:37)
ANIMATION: each clause fades in on its own sentence and stays. Earlier clauses
quieten but remain fully legible.
WHY: three separate marks in the exam, so three separate lines on screen. A
single paragraph would be the "screen repeats the narration" failure.
LAYOUT: left-aligned block, centred; three short lines.
AVATAR: MODE B.
COLOURS: heading brand accent; clauses neutral, current one accented.
PERSISTENCE: all three hold through 00:50.
IMPLEMENTATION: MANIM

---

# SCENE 03
TIME: 00:40 – 00:50
NARRATION: "मतलब थोड़ी सी मात्रा बहुत काम की है। शरीर इन्हें पर्याप्त नहीं बना पाता। इसलिए आहार से लेने पड़ते हैं। वरना खास तरह के रोग हो जाते हैं।"
TEACHING INTENT: CONCEPT_EXPLANATION
VISUAL DECISION: no new object — he is restating the three clauses in plain
language. Each clause brightens as its plain-language version is spoken.
ANIMATION: clause ① brightens at "थोड़ी सी मात्रा", ② at "शरीर बना नहीं पाता",
③ at "रोग हो जाते हैं"; a fourth short line is added at 00:46:
**→ आहार से लेने पड़ते हैं**
WHY: he is glossing what is already on screen. Replacing it would discard the
definition mid-explanation; adding the one genuinely new consequence is enough.
AVATAR: MODE B, unchanged. No resize.
IMPLEMENTATION: MANIM (state change + one line)

---

# SCENE 04
TIME: 00:50 – 00:59
NARRATION: "अब एक ज़रूरी बात, जिसे ज़्यादातर बच्चे लिखना भूल जाते हैं। कैल्सिफेरॉल धूप में त्वचा में बन सकता है और फिल्लोक्विनोन आँत के जीवाणु बना देते हैं।"
TEACHING INTENT: COMMON_MISTAKE + EXAMPLE
VISUAL DECISION: a marked exception callout — it directly qualifies clause ②,
so it attaches to clause ②.
WHAT APPEARS: a callout linked by a short leader to clause ②:
  **अपवाद — कैल्सिफेरॉल (D): धूप में त्वचा में · फिल्लोक्विनोन (K): आँत के जीवाणु**
ANIMATION: the callout appears with an exception marker; clause ② pulses once as
the connection is made.
WHY: he flags it as the thing most students omit. Attaching it to the clause it
qualifies is what stops it reading as an unrelated fact.
COLOURS: warning tone, distinct from the definition's neutral.
AVATAR: MODE B, unchanged.
IMPLEMENTATION: MANIM

---

# SCENE 05
TIME: 00:59 – 01:15
NARRATION: "चलो, परिभाषा तो हो गई; अब वर्गीकरण, क्योंकि पूरी तालिका इसी पर टिकी है। वसा में विलेय विटामिन हैं ए, डी, ई और के। जल में विलेय विटामिन हैं बी समूह और सी।"
TEACHING INTENT: CLASSIFICATION
VISUAL DECISION: two groups, side by side, filled as he names each set. He says
the whole table rests on this, so it gets its own clean screen.
WHAT APPEARS:
  | **वसा में विलेय** | **जल में विलेय** |
  | **A, D, E, K** | **B समूह, C** |
ANIMATION: the two column headings appear together; the fat-soluble set fills at
01:05 as he lists A, D, E, K one at a time; the water-soluble set fills at 01:09.
LAYOUT: two columns, full width — a two-way split reads horizontally.
AVATAR: MODE B.
COLOURS: two distinct accents, **fixed for the rest of the video** — every
vitamin named in part 2's table carries its solubility colour, so the
classification keeps paying off instead of being forgotten.
PERSISTENCE: holds through the recap.
IMPLEMENTATION: MANIM

---

# SCENE 06
TIME: 01:31 – 01:40
NARRATION: "बस, एक बार पक्का कर लो — ए, डी, ई और वसा में विलेय हैं, जबकि बी समूह और सी जल में विलेय हैं।"
TEACHING INTENT: MEMORY_CUE
VISUAL DECISION: no new object — the two groups brighten in turn as he recites
them.
ANIMATION: fat-soluble set pulses, then water-soluble set.
AVATAR: MODE B, unchanged.
IMPLEMENTATION: MANIM (state change)

---

# SCENE 07
TIME: 01:42 – 01:49 (end of part 1)
NARRATION: "कौन सी डेफिशिएंसी में कौन सा विटामिन — यही बच्चे सबसे ज़्यादा गड़बड़ करते हैं। तो अब Part Two में रोग और विटामिन के सही जोड़ एक-एक करके पक्के करेंगे।"
TEACHING INTENT: TRANSITION
VISUAL DECISION: **VISUAL: NONE** — clear, presenter returns.
AVATAR: MODE A, one eased change.
IMPLEMENTATION: NONE

---

# PART 2 — planned against the script's own On Screen directions

# SCENE 08
TIME: on the first teaching line of part 2
TEACHING INTENT: LIST — **the table is created**
VISUAL DECISION: a three-column table keyed on the DISEASE, because that is the
direction the question asks in.
WHAT APPEARS: three headings — **रोग** | **विटामिन** | **रासायनिक नाम** — and an
empty grid.
LAYOUT: three columns, full width, rows sized so six will fit legibly.
AVATAR: MODE B.
PERSISTENCE: **persists to the end of the video.**
IMPLEMENTATION: MANIM

---

# SCENES 09–14
TEACHING INTENT: LIST — one row per disease, each landing on the sentence that
names it. From the script's On Screen directions, in order:
  - **रतौंधी** | A | रेटिनॉल
  - **रक्त अल्पता (प्रणाशी)** | B₁₂ | सायनोकोबालऐमिन
  - **रिकेट्स (सूखा रोग)** | D | कैल्सिफेरॉल
  - **स्कर्वी / पायरिया** | C | ऐस्कॉर्बिक अम्ल
  - **बन्ध्यता** | E | टोकोफेरॉल
  - **अरक्तता** | फोलिक अम्ल (B₉) | —
ANIMATION: each row fills disease-cell first, then vitamin, then chemical name —
matching the lookup direction the student performs in the exam. Earlier rows
quieten but stay fully legible; **each row's state is set explicitly from its own
reveal time.**
COLOURS: each vitamin cell carries its solubility accent from part 1's
classification.
AVATAR: MODE B → **MODE C** once four rows are filled.
NOTE: the script pairs रक्त अल्पता with B₁₂ and अरक्तता with folic acid, and its
own direction says so explicitly — *"रक्त अल्पता ऊपर बी बारह के साथ जुड़ चुका
है"*. Both rows are kept and the distinction preserved; collapsing them would
lose a mark.
IMPLEMENTATION: MANIM

---

# SCENE 15
TIME: the recap line of part 2
TEACHING INTENT: RECAP — **the payoff**
VISUAL DECISION: the completed table alone, at full size — the whole answer in
one frame.
AVATAR: MODE C — low, so all six rows clear the presenter.
PERSISTENCE: holds to the end of the teaching section.
IMPLEMENTATION: MANIM

---

# FINAL SCENE SUMMARY

**Manim**
- three-clause definition, filling in
- the calciferol/phylloquinone exception callout, attached to clause ②
- fat-soluble vs water-soluble classification, two groups, two fixed accents
- **the disease → vitamin → chemical-name table**, six rows, filling one per
  spoken pair, persisting to the end

**Images**
- none required. The question asks for NAMES against diseases — a written
  mapping. Disease photographs would suit the sister video (विटामिन की कमी),
  where diseases are the subject; here the subject is the definition and the
  name lookup, and a photograph carries none of it.

**No visual**
- part 1: 00:00–00:15 (hook), 00:15–00:23 (announcement), 01:42–01:49 (transition)

**Reusable**
- the two solubility accents from part 1 carry into every vitamin cell of the
  part-2 table, so the classification stays live instead of being a passing fact
- one table, six rows, six separate moments

**New assets**
- none requiring generation. No image cost.

**BLOCKER CLEARED IN THIS PASS:** part 2's recording had never been transcribed,
which is why this video was never completed. Transcription has been started;
part-2 scene timings attach to it when it lands.
