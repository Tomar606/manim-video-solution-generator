# पोटैशियम डाइक्रोमेट — क्रोमाइट अयस्क से निर्माण

## GLOBAL VISUAL STRATEGY

**Teaching objective:** reproduce a three-step preparation IN ORDER with correct
equations, then three oxidation reactions. He says twice that the order is what
scores — *"क्रम बदला तो नंबर गया"* — so the visual must carry the ORDER as
strongly as it carries the chemistry.

**Key concepts:** ore → sodium chromate → sodium dichromate → potassium
dichromate, one equation per arrow. Then K₂Cr₂O₇ as an oxidising agent: Fe²⁺→Fe³⁺,
I⁻→I₂, H₂S→S.

**Visual language:** a **three-stage flow rail** that is built once in part 1 and
persists across all three parts as the spine. Each step's equation appears
attached to its own stage of the rail. The student always knows where they are
in the sequence.

**Main visual assets:** the 3-stage flow rail; three preparation equations; three
oxidation equations; a one-line summary of the three products.

**Avatar strategy:** MODE A over hooks and framing; MODE C for equations, which
are wide and need the frame; MODE B for the rail alone.

**BATCH-1 DEFECT THIS FIXES:** the equations rendered small and the green section
headings were smaller than the body text. Every equation here is LARGE and
**splits at the arrow** when it exceeds the width — reactants on line one,
products on line two — rather than shrinking to fit.

---

# SCENE 01
TIME: 00:17 – 00:34
NARRATION: "K₂Cr₂O₇ यानी पोटैशियम डाइक्रोमेट को क्रोमाइट अयस्क से बनाया जाता है। क्रोमाइट अयस्क का सूत्र है FeO·Cr₂O₃, और इसकी पूरी प्रिपरेशन तीन मुख्य स्टेप्स में होती है।"
TEACHING INTENT: INTRODUCTION + KEYWORD
VISUAL DECISION: two written facts — the ore's formula, and that there are three
steps.
WHAT APPEARS:
  - 00:19 **क्रोमाइट अयस्क — FeO·Cr₂O₃**
  - 00:30 below it, **तीन स्टेप्स में**
WHY: the formula is a discrete thing to be written in the exam. A photograph of
ore would teach nothing about it — batch 1 put one here, over the words
"परीक्षा में पूरा आंसर लिखना भी आ जाएगा".
LAYOUT: upper-centre, two lines.
AVATAR: MODE A — still framing.
IMPLEMENTATION: MANIM

---

# SCENE 02
TIME: 00:34 – 00:50
NARRATION: "ये तीनों नाम क्रम से याद होने चाहिए, क्रम बदला तो नंबर गया। पहला — क्रोमाइट अयस्क को सोडियम क्रोमेट में बदलना। दूसरा — … और तीसरा — …"
TEACHING INTENT: SEQUENCE + MEMORY_CUE — **the spine is created here**
VISUAL DECISION: build a horizontal flow rail, one stage per name.
VISUAL TYPE: Manim process rail
WHAT APPEARS, each on its own sentence:
  - 00:38 **क्रोमाइट अयस्क → Na₂CrO₄**  (stage 1)
  - 00:42 **→ Na₂Cr₂O₇**                (stage 2)
  - 00:46 **→ K₂Cr₂O₇**                 (stage 3)
ANIMATION: each stage box fades in and the arrow into it draws. The stage just
named is in accent; earlier stages stay fully legible and quiet.
LAYOUT: horizontal rail across the full width of the primary visual area — a
sequence reads left to right. Compact boxes, formula only.
AVATAR: MODE B.
COLOURS: stages neutral; current stage accent; arrows quiet.
PERSISTENCE: **the rail persists through parts 1, 2 and 3.** In part 2 and 3 it
sits small at the top of the visual area with the current stage lit — this is
what keeps the ORDER present while the equations change.
IMPLEMENTATION: MANIM

---

# SCENE 03
TIME: 00:54 – 01:18
NARRATION: "Step 1 — अयस्क से सोडियम क्रोमेट। क्रोमाइट अयस्क को NaOH या Na₂CO₃ के साथ वायु की उपस्थिति में परावर्तनी भट्टी में गर्म किया जाता है। इससे पीले रंग का सोडियम क्रोमेट यानी Na₂CrO₄ बनता है।"
TEACHING INTENT: PROCESS + FORMULA
VISUAL DECISION: stage 1 lights on the rail; its equation writes below.
WHAT APPEARS:
  - stage 1 of the rail brightens
  - heading **पद 1 — अयस्क से सोडियम क्रोमेट**
  - the equation, LARGE:
    **4FeCr₂O₄ + 8Na₂CO₃ + 7O₂ → 8Na₂CrO₄ + 2Fe₂O₃ + 8CO₂**
  - condition noted beside it: **वायु की उपस्थिति, परावर्तनी भट्टी**
ANIMATION: reactants appear as he names them, arrow draws, products appear.
LAYOUT: **the equation splits at the arrow** — it is far too long for one line at
a readable size. Reactants line one, products line two, arrow at the break.
Heading at the SAME scale as the body, never smaller.
AVATAR: **MODE C** — the equation needs the width and the height.
COLOURS: equation neutral; **Na₂CrO₄** in accent, because it is the product this
step exists to make.
PERSISTENCE: holds ~24s while he discusses it.
IMPLEMENTATION: MANIM

---

# SCENE 04
TIME: 01:18 – 01:26
NARRATION: "एक छोटी सी बात है जो लिखना अक्सर भूल जाते हैं। पदार्थ को छिद्रमय रखने के लिए कुछ मात्रा में शुष्क चूना मिलाया जाता है।"
TEACHING INTENT: COMMON_MISTAKE
VISUAL DECISION: a marked aside beside the equation, not a new screen.
WHAT APPEARS: a callout with a warning marker:
  **अक्सर भूल जाते हैं — शुष्क चूना मिलाया जाता है (पदार्थ छिद्रमय रहे)**
WHY: he explicitly flags it as the thing students omit. A visually distinct
callout is how the student notices it is separate from the equation.
LAYOUT: right of the equation, or beneath it — clear of both.
COLOURS: warning tone, distinct from the equation's neutral.
AVATAR: MODE C, unchanged. No resize for a callout.
IMPLEMENTATION: MANIM

---

# SCENE 05
TIME: 01:26 – 01:39
NARRATION: "इसके बाद जल के साथ Na₂CrO₄ विलयन में चला जाता है, जबकि Fe₂O₃ पीछे रह जाता है। फिर Fe₂O₃ को छानकर अलग कर लेते हैं।"
TEACHING INTENT: PROCESS — separation
VISUAL DECISION: a small two-branch split, showing what dissolves and what
does not.
WHAT APPEARS:
  **जल के साथ** → branches to **Na₂CrO₄ (विलयन में)** and **Fe₂O₃ (अवशेष — छानकर अलग)**
ANIMATION: the branch to the solution draws first, then the residue branch; the
residue is marked with a filter symbol.
WHY: two things go two different ways — a branch shows that in one glance where
a sentence has to be read twice.
AVATAR: MODE B.
PERSISTENCE: ~13s, then clears with the rest of step 1.
IMPLEMENTATION: MANIM

---

# SCENE 06
TIME: 01:39 – 01:56
NARRATION: "तो बच्चों, पहला स्टेप ऐसे पक्का कर लो — क्रोमाइट अयस्क से सोडियम क्रोमेट। लेकिन अभी K₂Cr₂O₇ नहीं बना है।"
TEACHING INTENT: RECAP + TRANSITION
VISUAL DECISION: return to the rail alone — stage 1 marked done, stages 2 and 3
still pending.
WHAT APPEARS: rail with stage 1 ticked; stages 2 and 3 dim.
WHY: this is exactly the "not finished yet" point he is making, and the rail
says it without words.
AVATAR: MODE B.
IMPLEMENTATION: MANIM

---

# PART 2

# SCENE 07
TIME: 00:15 – 00:37
NARRATION: "Step 2 — Sodium chromate से Sodium dichromate… Sodium chromate के विलयन को सांद्र H₂SO₄ के साथ उपचार करने पर Sodium dichromate बनता है"
TEACHING INTENT: PROCESS + FORMULA
VISUAL DECISION: rail at top with stage 2 lighting; equation below.
WHAT APPEARS:
  - rail, stage 1 ticked, **stage 2 now in accent**
  - heading **पद 2 — सोडियम क्रोमेट से सोडियम डाइक्रोमेट**
  - **2Na₂CrO₄ + H₂SO₄ → Na₂Cr₂O₇ + Na₂SO₄ + H₂O**
ANIMATION: reactants, arrow, products, in spoken order.
LAYOUT: equation LARGE; splits at the arrow if it exceeds the width.
AVATAR: MODE C.
COLOURS: **Na₂Cr₂O₇** in accent — the product of this step.
IMPLEMENTATION: MANIM

---

# SCENE 08
TIME: 00:37 – 00:53
NARRATION: "अब इसे अलग करने के लिए विलयन का वाष्पन किया जाता है, Na₂SO₄·10H₂O के रूप में क्रिस्टलीकृत हो जाता है, जिसे अलग कर लेते हैं… पहले सोडियम क्रोमेट फिर सोडियम डाइक्रोमेट, एग्ज़ाम में यही क्रम लिखना है।"
TEACHING INTENT: PROCESS + MEMORY_CUE
VISUAL DECISION: show the separation as a split, then re-assert the order on the
rail.
WHAT APPEARS:
  - **वाष्पन** → **Na₂SO₄·10H₂O (क्रिस्टल — अलग)** and **Na₂Cr₂O₇ (विलयन में)**
  - then the rail brightens stages 1→2 in sequence as he repeats the order
ANIMATION: branch draws; then a travelling highlight runs along the rail 1→2.
AVATAR: MODE B.
IMPLEMENTATION: MANIM

---

# SCENE 09
TIME: 00:53 – 01:14
NARRATION: "Step 3 — Sodium dichromate से Potassium dichromate… Sodium dichromate के जलीय विलयन का KCl के साथ उपचार किया जाता है। Potassium dichromate कम विलेय होता है। इसलिए ठंडा करने पर इसके क्रिस्टल प्राप्त हो जाते हैं।"
TEACHING INTENT: PROCESS + FORMULA + CAUSE_EFFECT
VISUAL DECISION: stage 3 lights; equation; then the reason the crystals separate.
WHAT APPEARS:
  - rail, **stage 3 in accent**, stages 1 and 2 ticked
  - heading **पद 3 — सोडियम डाइक्रोमेट से पोटैशियम डाइक्रोमेट**
  - **Na₂Cr₂O₇ + 2KCl → K₂Cr₂O₇ + 2NaCl**
  - then a two-link cause: **K₂Cr₂O₇ कम विलेय → ठंडा करने पर क्रिस्टल**
ANIMATION: equation assembles; the cause chain draws after it.
LAYOUT: equation large, centred; cause chain beneath, horizontal.
AVATAR: MODE C for the equation, no resize for the chain.
COLOURS: **K₂Cr₂O₇** in brand accent — the final product of the whole question.
IMPLEMENTATION: MANIM

---

# SCENE 10
TIME: 01:14 – 01:28
NARRATION: "अब पूरी बात को एक बार क्रम से दोहरा लेते हैं। Sodium Chromate, फिर Sodium Dichromate, और फिर Potassium Dichromate. एग्ज़ाम में तीनों steps के नाम और reactions ज़रूर लिखना।"
TEACHING INTENT: RECAP + MEMORY_CUE
VISUAL DECISION: the complete rail, all three stages lit, nothing else on screen.
WHAT APPEARS: the full rail at FULL size — this is the one moment it is the sole
object — with all three stages in accent and all three ticked.
ANIMATION: a highlight travels 1 → 2 → 3 in time with him naming them.
WHY: the whole video's ordering lesson, in one image, at the moment he asks for
it. Nothing else should be on screen competing.
AVATAR: MODE B.
PERSISTENCE: holds to the end of the part.
IMPLEMENTATION: MANIM

---

# PART 3

# SCENE 11
TIME: 00:16 – 00:50
NARRATION: "पहली अभिक्रिया — अम्लीय फेरस सल्फेट के साथ। K₂Cr₂O₇ अम्लीय माध्यम में फेरस सल्फेट यानी Fe²⁺ को फेरिक यानी Fe³⁺ में ऑक्सीकृत करता है।"
TEACHING INTENT: FORMULA + CONCEPT_EXPLANATION
VISUAL DECISION: the equation, with the oxidation it performs marked on it.
WHAT APPEARS:
  - heading **अम्लीय माध्यम — फेरस सल्फेट के साथ**
  - **K₂Cr₂O₇ + 7H₂SO₄ + 6FeSO₄ → K₂SO₄ + Cr₂(SO₄)₃ + 3Fe₂(SO₄)₃ + 7H₂O**
  - beneath it, the essential change alone: **Fe²⁺ → Fe³⁺ (ऑक्सीकरण)**
ANIMATION: the long equation assembles; then the short change line writes and
is boxed.
WHY: he says the thing to lock in is just Fe²⁺→Fe³⁺. The full equation is for
the answer sheet; the short line is what is memorised. Both belong, at different
weights.
LAYOUT: **this equation MUST split at the arrow** — it is the longest in the
video. Products on their own line. Large.
AVATAR: MODE C.
COLOURS: Fe²⁺ and Fe³⁺ in accent in both the long equation and the short line,
so the eye connects them.
IMPLEMENTATION: MANIM

---

# SCENE 12
TIME: 00:51 – 01:06
NARRATION: "अब दूसरी इम्पॉर्टेंट अभिक्रिया — KI वाली। अम्लीय माध्यम में K₂Cr₂O₇ आयोडाइड आयन को आयोडीन यानी I₂ में ऑक्सीकृत कर देता है। इसमें याद रखने बात बस एक है — कि I⁻ से I₂ बनता है।"
TEACHING INTENT: FORMULA
VISUAL DECISION: same treatment — full equation plus the one change to remember.
WHAT APPEARS:
  - **6KI + K₂Cr₂O₇ + 7H₂SO₄ → 4K₂SO₄ + Cr₂(SO₄)₃ + 7H₂O + 3I₂**
  - **I⁻ → I₂ (ऑक्सीकरण)**
LAYOUT: splits at the arrow. Same layout as the previous reaction so the pattern
is obvious.
AVATAR: MODE C.
IMPLEMENTATION: MANIM

---

# SCENE 13
TIME: 01:06 – 01:18
NARRATION: "और अब तीसरी — H₂S वाली। अम्लीय K₂Cr₂O₇, H₂S को सल्फर यानी S में ऑक्सीकृत कर देता है।"
TEACHING INTENT: FORMULA
WHAT APPEARS:
  - **K₂Cr₂O₇ + 4H₂SO₄ + 3H₂S → K₂SO₄ + Cr₂(SO₄)₃ + 7H₂O + 3S**
  - **H₂S → S (ऑक्सीकरण)**
LAYOUT: splits at the arrow. Same as the other two.
AVATAR: MODE C.
IMPLEMENTATION: MANIM

---

# SCENE 14
TIME: 01:18 – 01:32
NARRATION: "अब तीनों रिएक्शन्स को एक लाइन में याद करो — Fe²⁺ से Fe³⁺ बनता है, KI से I₂ बनता है, और H₂S का S बनता है।"
TEACHING INTENT: MEMORY_CUE + LIST
VISUAL DECISION: strip away the full equations and show only the three changes,
together. He is explicitly compressing; the screen should compress with him.
WHAT APPEARS, three lines filling in as he says them:
  ① **Fe²⁺ → Fe³⁺**
  ② **I⁻ → I₂**
  ③ **H₂S → S**
ANIMATION: the three short lines that have appeared under each equation converge
into this single list — reusing the same objects rather than drawing new ones.
LAYOUT: centred, three lines, large.
AVATAR: MODE B.
COLOURS: all three in brand accent — this is the carry-away.
PERSISTENCE: holds to the end of the teaching section.
IMPLEMENTATION: MANIM

---

# SCENE 15
TIME: 01:44 onward — "…वो नोट्स में पूरा आंसर देख लेना"
VISUAL DECISION: answer-page template on the cue. Not planned here.
IMPLEMENTATION: TEMPLATE

---

# FINAL SCENE SUMMARY

**Manim**
- **the three-stage flow rail** — created in part 1, persists across all three
  parts, current stage lit. This is the ORDER, which is what he says scores.
- ore formula card
- three preparation equations, each split at the arrow, each with its product
  in accent
- the "शुष्क चूना" common-mistake callout
- two separation branches (Fe₂O₃ filtered; Na₂SO₄·10H₂O crystallised)
- three oxidation equations, identically laid out, each with its one-line change
- the three changes converging into a single recall list

**Images**
- none. Ore and crystals are named, not described — their appearance carries no
  exam information, and batch 1's ore photograph sat over an exam-framing line.

**No visual**
- part 1: 00:00–00:17 (hook), 01:56–02:08 (transition)
- part 2: 00:00–00:15 (recap)
- part 3: 00:00–00:16 (recap and framing)

**Reusable**
- the rail: one object, three parts, lit differently in eight scenes
- the three short change-lines are created under their equations and REUSED as
  the final recall list — not redrawn

**New assets**
- none requiring generation. No image cost.
