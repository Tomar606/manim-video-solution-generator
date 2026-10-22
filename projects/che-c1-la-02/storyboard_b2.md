# क्वथनांक में उन्नयन — कारण एवं ग्राफ

## GLOBAL VISUAL STRATEGY

**Teaching objective:** define boiling point, explain why a non-volatile solute
raises it, and read that explanation off a graph. The question says
**ग्राफ की सहायता से समझाइये** — so the GRAPH IS MANDATORY and is the spine of
part 1. A version without it fails the question as asked.

**Key concepts:** boiling point = the temperature where vapour pressure meets
atmospheric pressure. Adding a non-volatile solute LOWERS vapour pressure, so
the solution's curve sits below the solvent's, so it needs a HIGHER temperature
to reach the same atmospheric line — and that gap is ΔT_b.

**Visual language:** one vapour-pressure vs temperature axis, built up in the
same order as the reasoning: atmospheric line, then solvent curve, then solution
curve, then the two boiling points, then the gap between them. It is never
replaced, only added to.

**Main visual assets:** the P–T graph (Manim); a definition card; the formula
ΔT_b = T_b − T_b⁰; a four-point recall list.

**Avatar strategy:** MODE A over the hook and the framing. MODE B for the
definition and the vapour-pressure reasoning. MODE C for the graph — the graph
is the subject and needs the frame. MODE B for the formula and the list.

---

# SCENE 01
TIME: 00:19 – 00:27
NARRATION: "सबसे पहले समझते हैं क्वथनांक किसे कहते हैं? ध्यान से सुनना, क्योंकि परीक्षा में इसकी परिभाषा से ही शुरुआत करनी है।"
TEACHING INTENT: TRANSITION + WARNING
VISUAL DECISION: **VISUAL: NONE**
WHY: he is announcing a definition, not yet giving it.
AVATAR: MODE A — large, bottom-centre.
IMPLEMENTATION: NONE

---

# SCENE 02
TIME: 00:27 – 00:42
NARRATION: "किसी द्रव का क्वथनांक वह ताप है, जिस पर उसके वाष्पदाब का मान वायुमण्डलीय दाब के बराबर हो जाता है।"
TEACHING INTENT: DEFINITION
VISUAL DECISION: the exam definition, short, plus the condition as a relation.
VISUAL TYPE: Manim text + equation
WHAT APPEARS:
  - heading **क्वथनांक**
  - one line: **वह ताप जिस पर वाष्पदाब = वायुमण्डलीय दाब**
  - below it, boxed: **P_वाष्प = P_वायुमण्डलीय**  (LaTeX with Devanagari
    subscripts set as separate Text — never glued inside MathTex)
WHY: the definition is what he says they must open the answer with. The screen
carries the compressed exam form, not the spoken sentence.
LAYOUT: upper-centre of the visual area, centred, generous size.
AVATAR: MODE B — reduced, low, bottom-centre.
COLOURS: heading brand accent, condition boxed in accent.
PERSISTENCE: holds until 00:42, then clears — the next section is a different idea.
IMPLEMENTATION: MANIM

---

# SCENE 03
TIME: 00:42 – 00:51
NARRATION: "अब असली सवाल — अवाष्पशील विलेय मिलाने पर क्वथनांक बढ़ता क्यों है? इसे ध्यान से समझो"
TEACHING INTENT: QUESTION + TRANSITION
VISUAL DECISION: **VISUAL: NONE**
WHY: he is posing the question the rest of the video answers. Let it land on
the presenter.
AVATAR: MODE A — grows, one eased change.
IMPLEMENTATION: NONE

---

# SCENE 04
TIME: 00:51 – 01:19
NARRATION: "जब हम किसी शुद्ध विलायक में अवाष्पशील विलेय मिलाते हैं, तो बने हुए विलयन का वाष्पदाब… कम हो जाता है।" → "…तो विलयन का क्वथनांक भी बढ़ जाएगा।"
TEACHING INTENT: CAUSE_EFFECT — the causal chain
VISUAL DECISION: a three-link chain, built one link per spoken step. This is the
reasoning the exam wants reproduced, and it is a chain, so it should look like one.
VISUAL TYPE: Manim
WHAT APPEARS — each link on its own sentence:
  - 00:51 **विलेय मिलाया**
  - 00:55 ↓  **वाष्पदाब घटा**
  - 01:05 ↓  **P_atm तक पहुँचने को अधिक ताप चाहिए**
  - 01:13 ↓  **क्वथनांक बढ़ा**
ANIMATION: each box fades in and the arrow above it draws, ~0.4s. Earlier links
stay visible and quieten; the current link is in accent.
LAYOUT: vertical stack, centred, in the primary visual area. Four short boxes —
vertical stacking is right for a chain.
AVATAR: MODE B — reduced and low, one change on entry.
COLOURS: boxes neutral, current link accent, arrows quiet.
PERSISTENCE: the completed chain holds to 01:19 — it is the written answer.
TRANSITION: clears into the graph, which restates the same chain visually.
IMPLEMENTATION: MANIM

---

# SCENE 05
TIME: 01:19 – 01:40
NARRATION: "अब इसे ग्राफ में देखो। ग्राफ में शुद्ध विलायक का वाष्पदाब बढ़ते हुए वायुमण्डलीय दाब तक पहुँचता है, इसलिए उसका क्वथनांक टी-बी-ज़ीरो होता है"
TEACHING INTENT: GRAPH_EXPLANATION — **the question demands this**
VISUAL DECISION: build the graph in reasoning order. Never show the finished
graph at once; every element arrives when it is spoken.
VISUAL TYPE: Manim axes + curves
WHAT APPEARS:
  - 01:19 axes: x = **ताप (T)**, y = **वाष्पदाब (P)**
  - 01:21 horizontal dashed line labelled **वायुमण्डलीय दाब (P_atm)**
  - 01:23 the pure-solvent curve rises and MEETS the dashed line; the meeting
          point drops a vertical dashed line to the x-axis, labelled **T_b⁰**
ANIMATION: axes draw (~0.6s), then the atmospheric line, then the curve is
traced left→right over ~1.5s so the student watches it climb to the line. The
intersection flashes, then the drop-line draws.
LAYOUT: graph **full-width, graphic-dominant**, occupying the primary visual
area. Axis labels outside the plot. T_b⁰ label below the axis, clear of the
presenter.
AVATAR: **MODE C** — chest-height, bottom-centre, one eased change. The graph is
the subject; the presenter must not compete with it.
COLOURS: solvent curve in one accent; atmospheric line neutral dashed; labels
matched to their curve.
PERSISTENCE: **the graph stays to 02:00.** It is the whole back half of the part.
IMPLEMENTATION: MANIM

---

# SCENE 06
TIME: 01:40 – 01:45
NARRATION: "लेकिन विलयन का वाष्पदाब कम है, इसलिए वह वायुमण्डलीय दाब तक थोड़े अधिक तापमान पर पहुँचता है, इसलिए विलयन का क्वथनांक टी-बी होगा"
TEACHING INTENT: GRAPH_EXPLANATION + COMPARISON
VISUAL DECISION: add the second curve to the SAME axes. The comparison is the
point; two separate graphs would destroy it.
WHAT APPEARS: the solution curve, drawn **visibly below** the solvent curve
across the whole range, meeting the atmospheric line **further right**. Its drop
line lands at **T_b**, to the right of T_b⁰.
ANIMATION: traced left→right over ~1.5s so the student sees it staying below.
**DIRECTION CHECK:** the solution curve is BELOW and meets the line LATER
(higher T). Drawn above, it would teach that boiling point falls.
COLOURS: solution curve in a second, clearly distinct accent. Both labels
colour-matched to their curve.
AVATAR: MODE C, unchanged — no resize.
PERSISTENCE: both curves hold.
IMPLEMENTATION: MANIM

---

# SCENE 07
TIME: 01:45 – 01:52
NARRATION: "बच्चों, इस असमानता को बिल्कुल मत भूलना — यही इस ग्राफ का सबसे ज़रूरी निष्कर्ष है"
TEACHING INTENT: MEMORY_CUE + CONCLUSION
VISUAL DECISION: mark the gap on the graph that already exists.
WHAT APPEARS: a bracket along the x-axis spanning T_b⁰ → T_b, labelled
**ΔT_b**, with the inequality **T_b > T_b⁰** beside it.
ANIMATION: the bracket draws between the two existing drop-lines and the label
fades in. Both drop-lines brighten together.
WHY: this is the conclusion the question is really testing, and it is a distance
on the graph — so it should be drawn ON the graph, not restated as text.
LAYOUT: bracket under the axis; the inequality to its right, clear of captions.
AVATAR: MODE C, unchanged.
COLOURS: bracket and ΔT_b in brand accent — the one thing to carry away.
PERSISTENCE: holds to the end of the part.
IMPLEMENTATION: MANIM

---

# SCENE 08
TIME: 01:52 – 02:00 (end of part 1)
NARRATION: "तो बच्चों, इतना तो समझ लिया… ये देखेंगे अगले पार्ट में।"
TEACHING INTENT: RECAP + TRANSITION
VISUAL DECISION: **VISUAL: NONE** — clear the graph, presenter returns.
WHY: holding the graph while he talks about the next part is frozen screen.
AVATAR: MODE A, one eased change.
IMPLEMENTATION: NONE

---

# PART 2

# SCENE 09
TIME: 00:00 – 00:23
NARRATION: recap and "…तभी नंबर मिलेंगे।"
TEACHING INTENT: RECAP + EXAM FRAMING
VISUAL DECISION: **VISUAL: NONE**
AVATAR: MODE A — large. This is a 23-second presenter-focused stretch; batch 1
filled it with a photograph of nothing in particular.
IMPLEMENTATION: NONE

---

# SCENE 10
TIME: 00:23 – 00:47
NARRATION: "शुद्ध विलायक में कोई विलेय मिला देने पर उसके क्वथनांक में होने वाली वृद्धि को उन्नयन कहते हैं… दोनों के क्वथनांकों के अंतर को हम क्वथनांक में उन्नयन कहते हैं।"
TEACHING INTENT: DEFINITION
VISUAL DECISION: show the two boiling points as two marks and the difference
between them — the definition IS a difference, so show a difference.
VISUAL TYPE: Manim
WHAT APPEARS:
  - 00:23 heading **क्वथनांक में उन्नयन**
  - 00:32 a short temperature line with **T_b⁰ — शुद्ध विलायक** marked
  - 00:36 **T_b — विलयन** marked to its right
  - 00:42 a bracket between them labelled **उन्नयन**
ANIMATION: marks appear on their sentences; the bracket draws last, as he says
"अंतर".
LAYOUT: horizontal — a comparison of two points needs width. Centred.
AVATAR: MODE B.
COLOURS: solvent and solution keep the SAME two accents as the part-1 graph, so
the student connects them.
PERSISTENCE: holds into the next scene, which turns it into the formula.
IMPLEMENTATION: MANIM

---

# SCENE 11
TIME: 00:47 – 00:55
NARRATION: "बस बच्चों, ये फॉर्मूला पक्का याद कर लेना। यहाँ टी-बी है विलयन का क्वथनांक और टी-बी ज़ीरो है शुद्ध विलायक का क्वथनांक।"
TEACHING INTENT: FORMULA + KEYWORD
VISUAL DECISION: transform the bracket into the formula, so the symbol is
visibly the same quantity that was just drawn.
WHAT APPEARS: boxed, LARGE:
  **ΔT_b = T_b − T_b⁰**   (LaTeX: `\Delta T_b = T_b - T_b^{0}`)
then, as he names each symbol, a short gloss appears beside it:
  T_b → विलयन का क्वथनांक ; T_b⁰ → शुद्ध विलायक का क्वथनांक
ANIMATION: the **उन्नयन** bracket morphs into **ΔT_b**; the two marks morph into
their symbols. Glosses fade in on their own sentence.
**NOTE — the batch-1 defect:** this expression must render as MATHS. Written in
a text block it printed as `$\Delta T_b = T_b - T_b^{0}$` on screen, literally.
T_b⁰ is a SUPERSCRIPT ZERO, not a degree sign.
LAYOUT: equation centred, large, boxed; glosses smaller, beneath.
AVATAR: MODE B, unchanged.
PERSISTENCE: the formula stays to the end of the teaching section.
IMPLEMENTATION: MANIM

---

# SCENE 12
TIME: 00:55 – 01:15
NARRATION: "अब बस ये चार ज़रूरी बातें याद रहना। पहली — … दूसरी — … तीसरी — … और चौथी — इसका सूत्र है डेल्टा टी-बी बराबर टी-बी माइनस टी-बी ज़ीरो।"
TEACHING INTENT: MEMORY_CUE + LIST
VISUAL DECISION: a four-item list that fills in — he counts them off, so the
screen counts them off.
WHAT APPEARS:
  - 00:55 heading **याद रखने की चार बातें**, four empty slots
  - 00:59 ① **विलेय मिलाने पर वाष्पदाब घटता है**
  - 01:02 ② **वाष्पदाब घटने से क्वथनांक बढ़ता है**
  - 01:06 ③ **यही वृद्धि = क्वथनांक में उन्नयन**
  - 01:10 ④ **ΔT_b = T_b − T_b⁰**  ← rendered as MATHS, sized to match the text
ANIMATION: each fills on its sentence; earlier items quieten but stay fully
legible. State set explicitly per item — the batch-1 bug made ① vanish.
LAYOUT: left-aligned block, centred; four lines at readable size.
AVATAR: MODE B.
PERSISTENCE: all four hold — this is the copy-down moment.
IMPLEMENTATION: MANIM

---

# SCENE 13
TIME: 01:21 onward — "…आपकी स्क्रीन पर आ जाएगा"
VISUAL DECISION: hand to the answer-page template on the cue. Not planned here.
IMPLEMENTATION: TEMPLATE

---

# FINAL SCENE SUMMARY

**Manim**
- definition card + P_वाष्प = P_वायुमण्डलीय condition
- four-link causal chain (solute → vapour pressure ↓ → more heat → bp ↑)
- **the P–T graph**: axes, atmospheric line, solvent curve, solution curve,
  T_b⁰ and T_b drop-lines, ΔT_b bracket — built in reasoning order, persists 40s
- T_b⁰ / T_b temperature line and the उन्नयन bracket
- ΔT_b = T_b − T_b⁰ formula, morphed out of the bracket
- four-point recall list

**Images**
- none. Everything here is a graph, a relation or a definition — Manim is exact
  and a generated image could only be less accurate.

**No visual**
- part 1: hook to 00:19; 00:42–00:51; 01:52–02:00
- part 2: 00:00–00:23

**Reusable**
- the two accent colours for solvent vs solution carry from the part-1 graph
  into the part-2 definition, so the student links them.
- the graph persists 01:19 → 02:00; built once, added to three times.

**New assets**
- none requiring generation. No image cost.
