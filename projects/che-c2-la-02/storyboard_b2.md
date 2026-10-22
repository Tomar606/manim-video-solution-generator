# संक्षारण — परिभाषा, तीन कारक, तीन उपाय

## GLOBAL VISUAL STRATEGY

**Teaching objective:** the question has three explicit parts — define corrosion,
give THREE factors, give THREE preventive measures. It is a counted answer, so
the governing visual is **two counted lists that fill in**, preceded by a
definition. Nothing else is needed and nothing else should appear.

**Key concepts:** corrosion = metal + atmospheric gases + moisture → unwanted
compounds. Three factors: nature of the metal, impurities, environment. Three
measures: barrier (paint/grease/oil), sacrificial protection (galvanising with
zinc), electroplating.

**Visual language:** a three-ingredient cause figure for the definition, then two
counted lists, each complete and held. The two lists are the answer sheet.

**Main visual assets:** the three-ingredient definition figure; the three-factor
list; the three-measure list; a closing pair showing both threes together.

**Avatar strategy:** MODE A over the hook; MODE B for the definition and the
lists — neither needs the full frame; no MODE C in this video, because nothing
here is a large diagram.

**PACING:** three factors over ~30s and three measures over ~35s — about 10s per
item. Comfortable; each item gets a statement plus its "मतलब" gloss.

---

# SCENE 01
TIME: 00:19 – 00:34
NARRATION: "वायुमण्डल में उपस्थित गैसों तथा नमी के कारण धातुओं के धीरे-धीरे अवांछित यौगिकों में बदलने की प्रक्रिया को संक्षारण कहते हैं। इसे याद रखने का आसान तरीका है— धातु, वायुमण्डल की गैसें और नमी, इन तीनों के कारण होता है संक्षारण।"
TEACHING INTENT: DEFINITION + MEMORY_CUE
VISUAL DECISION: the definition, then his own memory device drawn as what it is —
three inputs producing one outcome.
WHAT APPEARS:
  - 00:19 heading **संक्षारण**, and the exam definition in one compressed line:
    **धातुओं का धीरे-धीरे अवांछित यौगिकों में बदलना**
  - 00:29 three labelled inputs converging on one output:
    **धातु** + **वायुमण्डलीय गैसें** + **नमी**  →  **संक्षारण**
ANIMATION: the definition line writes; then the three inputs appear one per named
item and their arrows converge on the outcome, which lands last.
WHY: he explicitly offers "these three together" as the way to remember it. Three
arrows meeting one point is that sentence as a picture, and it is what the
student will recall in the exam.
LAYOUT: definition upper-centre; the converging figure below it, horizontal —
three inputs need width.
AVATAR: MODE B.
COLOURS: the three inputs neutral; the outcome in the warning tone, since
corrosion is the damage.
PERSISTENCE: holds ~10s, then clears for the factors.
IMPLEMENTATION: MANIM

---

# SCENE 02
TIME: 00:34 – 00:38
NARRATION: "और इसका सबसे आसान उदाहरण है— लोहे में जंग लगना।"
TEACHING INTENT: EXAMPLE
VISUAL DECISION: one line of text, no picture.
WHAT APPEARS: **उदाहरण — लोहे में जंग**
WHY: rust is named as a familiar example, not described. Its appearance carries
no exam information, and the student already knows what rust looks like. Batch 1
put a photograph of a rusty nail here — over the words "परीक्षा में सही तरीके से
लिखना भी सीख जाओगे", which is not even this sentence.
AVATAR: MODE B, unchanged.
IMPLEMENTATION: MANIM (text)

---

# SCENE 03
TIME: 00:38 – 01:11
NARRATION: "अब संक्षारण को प्रभावित करने वाले तीन कारक समझो। पहला—धातु की प्रकृति… दूसरा—धातु में अशुद्धियाँ हों… तीसरा—वातावरण…"
TEACHING INTENT: LIST — the three factors the question demands
VISUAL DECISION: a three-slot list that FILLS IN, with each item's "मतलब" gloss
appearing under it as he explains it.
VISUAL TYPE: Manim progressive list
WHAT APPEARS:
  - 00:38 heading **संक्षारण को प्रभावित करने वाले तीन कारक**, three empty slots
  - 00:41 ① **धातु की प्रकृति** — gloss at 00:44: *अधिक क्रियाशील → जल्दी संक्षारण*
  - 00:50 ② **धातु में अशुद्धियाँ** — gloss at 00:53: *अशुद्धियाँ → तेज़ संक्षारण*
  - 00:58 ③ **वातावरण** — gloss at 01:01: *हवा, नमी, गैसें → संक्षारण बढ़ता है*
ANIMATION: each numbered item fades to full on its sentence; its gloss follows
about three seconds later on the "मतलब" clause. Earlier items quieten but stay
FULLY legible.
**Each item's state is set explicitly from its own reveal time** — the batch-1
bug that erased item ① when ② arrived must not recur.
LAYOUT: left-aligned block, centred, three items with a smaller gloss line under
each. Showing the empty slots first tells the student three are coming.
AVATAR: MODE B — reduced and low, list above him.
COLOURS: current item accent; earlier items neutral-quiet; glosses quieter still.
PERSISTENCE: **all three stay** through 01:11 — the completed list is copied down.
IMPLEMENTATION: MANIM

---

# SCENE 04
TIME: 01:05 – 01:11
NARRATION: "बस, इन तीनों को याद रखो— धातु की प्रकृति, अशुद्धियाँ और वातावरण।"
TEACHING INTENT: MEMORY_CUE
VISUAL DECISION: no new object — the three glosses fade back and the three item
names brighten together, exactly the three words he is reciting.
ANIMATION: glosses dim, the three names pulse in sequence with his recital.
WHY: he is compressing to three words; the screen compresses to the same three.
AVATAR: MODE B, unchanged. No resize.
IMPLEMENTATION: MANIM (state change)

---

# SCENE 05
TIME: 01:11 – 01:48
NARRATION: "अब समझते हैं संक्षारण से बचाव के तीन उपाय। पहला—रोधिका स्थापित करना… दूसरा—समर्पित बचाव… इसका उदाहरण है गैल्वेनीकरण, जिसमें लोहे पर जिंक की तह चढ़ाई जाती है। तीसरा—विद्युत् प्लेटिंग…"
TEACHING INTENT: LIST — the three measures the question demands
VISUAL DECISION: a second three-slot list, laid out identically to the first, so
the answer's two halves visibly match.
WHAT APPEARS:
  - 01:11 heading **बचाव के तीन उपाय**, three empty slots
  - 01:15 ① **रोधिका स्थापित करना** — gloss: *पेंट, ग्रीस या तेल की परत*
  - 01:24 ② **समर्पित बचाव** — gloss: *अधिक क्रियाशील धातु की तह, जो पहले नष्ट होती है*
    and at 01:34 a sub-line: *उदाहरण — गैल्वेनीकरण (लोहे पर जिंक)*
  - 01:40 ③ **विद्युत् प्लेटिंग** — gloss: *जिंक, निकिल या क्रोमियम की परत*
ANIMATION: same rhythm as the factor list — name, then gloss. The galvanising
example appears as a sub-line under ② rather than as a fourth item, because it
is an example of ②, not a separate measure.
**MECHANISM NOTE:** sacrificial protection means the coating metal is destroyed
FIRST, protecting the iron. If this is ever animated, the coating must corrode
and the iron stay intact — reversed, it teaches the opposite.
LAYOUT: identical to scene 03, so the two lists read as a matched pair.
AVATAR: MODE B, unchanged — no resize between the two lists.
PERSISTENCE: **all three stay** to the end of the teaching section.
IMPLEMENTATION: MANIM

---

# SCENE 06
TIME: 01:48 – 01:54
NARRATION: "बच्चों, बस इतना याद रख लिया, तो परीक्षा में संक्षारण का ये पूरा उत्तर कभी नहीं भूलोगे।"
TEACHING INTENT: RECAP + MEMORY_CUE — **the payoff**
VISUAL DECISION: show BOTH threes together — the complete answer in one frame.
This is the only moment the whole answer is visible at once, and it is exactly
when he says "पूरा उत्तर".
WHAT APPEARS: two columns side by side, both already known:
  | **तीन कारक** | **तीन उपाय** |
  | ① धातु की प्रकृति | ① रोधिका |
  | ② अशुद्धियाँ | ② समर्पित बचाव |
  | ③ वातावरण | ③ विद्युत् प्लेटिंग |
ANIMATION: the factor list shrinks and moves left; the measure list moves right;
they settle side by side. Both are objects already on screen — nothing is redrawn.
LAYOUT: two columns, full width, three short rows each.
AVATAR: MODE B — low, so both columns have the height.
COLOURS: factors in the warning tone (what causes damage), measures in the
positive tone (what prevents it) — colour carrying meaning, not decoration.
PERSISTENCE: holds to the end.
IMPLEMENTATION: MANIM

---

# SCENE 07
TIME: 01:56 onward — "…आपकी स्क्रीन पर आ जाएगा"
VISUAL DECISION: answer-page template on the cue. Not planned here.
IMPLEMENTATION: TEMPLATE

---

# FINAL SCENE SUMMARY

**Manim**
- definition line + three-input converging figure (metal + gases + moisture → corrosion)
- three-factor list, filling in, each with a "मतलब" gloss
- three-measure list, laid out identically, with galvanising as a sub-line under ②
- the closing two-column pairing of both threes

**Images**
- none. Rust is named as a familiar example and its appearance teaches nothing
  the student does not already know; every other element here is a definition or
  a counted list.

**No visual**
- 00:00–00:19 (hook and framing)

**Reusable**
- both lists are built once and REUSED as the two columns of the closing recap —
  they move, they are not redrawn
- the warning/positive tone pair carries meaning consistently: causes of damage
  in one tone, protections in the other

**New assets**
- none requiring generation. No image cost.

**NOTE:** this is a single-part video with a simple counted answer. The
temptation is to fill it with pictures of rust and paint tins; the question asks
for six specific written points, and the screen's job is to hold those six.
