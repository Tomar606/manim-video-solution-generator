# शून्य कोटि अभिक्रिया — अर्द्ध-आयुकाल ∝ प्रारम्भिक सान्द्रण

## GLOBAL VISUAL STRATEGY

**Teaching objective:** the question is **सिद्ध कीजिए** — prove it. So the whole
video is DERIVATION MODE, and the student must watch the result being
constructed, not be handed it.

**Key concepts:** for zero order, rate = k, independent of concentration. The
integrated form gives kt = [A₀] − [A]. At half-life, t = t½ and [A] = [A₀]/2.
Substituting gives t½ = [A₀]/2k, and since k and 2 are constants, t½ ∝ [A₀].

**Visual language:** ONE derivation column that grows a line at a time. Earlier
lines stay visible and quiet, the current line is boxed. Nothing is replaced
until the proof is complete.

**Main visual assets:** definition card; the derivation chain (six lines); the
conclusion t½ ∝ [A₀]; a first-order contrast; the [A]-vs-t graph.

**Avatar strategy:** MODE A over the hook and transitions. MODE B for the
definition. **MODE C throughout the derivation** — a growing stack of equations
needs vertical room and is the subject.

**PACING CHECK:** part 1 carries about 8 steps across 103 seconds and part 2
about 8 across 77 — roughly 10–13 seconds per step. That is comfortable as a
GROWING CHAIN. It would not be comfortable as sixteen separate screens, and that
distinction is the whole design here.

**BATCH-1 DEFECT THIS FIXES:** the built video jumped from the rate law straight
to the answer, so `k = x/t` appeared with `x` never defined, and the next beat
substituted `[A] = [A₀]/2` into an equation that contained no `[A]`. Every
intermediate step below is mandatory, and each must visibly follow from the last.

---

# SCENE 01
TIME: 00:19 – 00:27
NARRATION: "उससे पहले समझते हैं अर्द्ध-आयुकाल होता क्या है? ये दिमाग में बिठा लो, क्योंकि परीक्षा में सबसे पहले यही परिभाषा लिखनी है।"
TEACHING INTENT: TRANSITION + WARNING
VISUAL DECISION: **VISUAL: NONE**
AVATAR: MODE A — large, bottom-centre.
IMPLEMENTATION: NONE

---

# SCENE 02
TIME: 00:27 – 00:46
NARRATION: "किसी अभिक्रिया का अर्द्ध-आयुकाल वो समय है, जिसमें किसी अभिकारक का सान्द्रण घटकर अपने प्रारम्भिक सान्द्रण का आधा रह जाता है… इसे t1 बाई 2 से प्रदर्शित करते हैं।"
TEACHING INTENT: DEFINITION
VISUAL DECISION: the exam definition plus the condition in symbols, because the
condition is what the proof will substitute later.
WHAT APPEARS:
  - heading **अर्द्ध-आयुकाल (t₁/₂)**
  - one line: **वह समय जिसमें सान्द्रण आधा रह जाता है**
  - 00:43 boxed: **[A] = [A₀]/2**
ANIMATION: definition line fades in; the symbolic condition appears as he names
the symbol.
WHY: introducing **[A] = [A₀]/2** here, at the definition, means that when it is
substituted at 01:16 the student already knows where it came from.
LAYOUT: upper-centre, generous size.
AVATAR: MODE B.
PERSISTENCE: the symbolic condition is deliberately carried forward — it
reappears as a substitution step later.
IMPLEMENTATION: MANIM

---

# SCENE 03
TIME: 00:48 – 00:56
NARRATION: "अब हमें सिद्ध करना है कि शून्य कोटि की अभिक्रिया का अर्द्ध-आयुकाल अभिकारक के प्रारम्भिक सान्द्रण के समानुपाती होता है।"
TEACHING INTENT: QUESTION — the statement to be proved
VISUAL DECISION: state the target, then leave it visible at the top of the
derivation. A proof should show what it is aiming at.
WHAT APPEARS: at the top of the visual area, quietly:
  **सिद्ध करना है:  t₁/₂ ∝ [A₀]**
LAYOUT: small, top of the primary area, above where the derivation will grow.
AVATAR: MODE B.
PERSISTENCE: **stays for the whole derivation**, dim, until it is proved — then
it brightens.
IMPLEMENTATION: MANIM

---

# SCENE 04
TIME: 00:56 – 01:05
NARRATION: "शून्य कोटि की अभिक्रिया के लिए हमारे पास समीकरण होती है। अब यहाँ से ज़रा ध्यान से देखना, यही तो पूरे व्युत्पादन का असली स्टेप है।"
TEACHING INTENT: DERIVATION — steps 1 and 2
VISUAL DECISION: **begin the chain.** Do not show the final form yet.
DERIVATION STEPS:
  - **Step 1** — CURRENT EQUATION: **दर = k[A]⁰ = k**
    TRANSFORMATION: none, this is the starting fact
    VISUAL ACTION: line 1 writes; boxed as current
    WHY IT MATTERS: zero order means the rate does not depend on concentration
  - **Step 2** — CURRENT EQUATION: **−d[A]/dt = k**
    TRANSFORMATION: the rate written as the rate of change of [A]
    VISUAL ACTION: line 2 writes below line 1; the box moves down to it; line 1
    quietens but stays
ANIMATION: each line writes over ~0.5s; the focus box slides from the previous
line to the current one, never leaving an empty box behind.
LAYOUT: derivation grows as a **left-aligned vertical column**, centred as a
block. Lines LARGE.
AVATAR: **MODE C** — one eased change on entry; no further resizing for the
rest of the derivation.
COLOURS: current line in accent inside the focus box; earlier lines neutral-quiet.
PERSISTENCE: **every line stays.** The completed chain is the exam answer.
IMPLEMENTATION: MANIM

---

# SCENE 05
TIME: 01:05 – 01:16
NARRATION: "…यही तो पूरे व्युत्पादन का असली स्टेप है।" (integration, spoken over as the working step)
TEACHING INTENT: DERIVATION — steps 3, 4, 5
VISUAL DECISION: **the middle of the proof — the part batch 1 dropped.**
DERIVATION STEPS:
  - **Step 3** — **−d[A] = k dt**
    TRANSFORMATION: variables separated
    VISUAL ACTION: dt migrates across the equals sign; line writes
  - **Step 4** — **∫[A₀]^[A] d[A] = − ∫₀^t k dt**
    TRANSFORMATION: both sides integrated between limits
    VISUAL ACTION: the integral signs and limits fade in around the existing
    terms, so the student sees it is the SAME equation with limits applied
  - **Step 5** — **[A] = [A₀] − k t**
    TRANSFORMATION: integration performed
    VISUAL ACTION: line writes; the focus box moves to it
WHAT REMAINS: all previous lines, quiet.
WHAT DISAPPEARS: nothing.
AVATAR: MODE C, unchanged.
IMPLEMENTATION: MANIM

---

# SCENE 06
TIME: 01:16 – 01:19
NARRATION: (rearrangement, spoken into the next step)
TEACHING INTENT: DERIVATION — step 6
DERIVATION STEP:
  - **Step 6** — **k t = [A₀] − [A]**
    TRANSFORMATION: rearranged so the constant is isolated
    VISUAL ACTION: the terms of step 5 physically swap sides — animate the move
    rather than writing a new line from scratch, so it reads as a rearrangement
    and not a new fact
**This is the line the substitution needs.** It contains [A] explicitly, which
is exactly what was missing when `k = x/t` shipped.
AVATAR: MODE C, unchanged.
IMPLEMENTATION: MANIM

---

# SCENE 07
TIME: 01:05 – 01:16 (spoken) — "जब अभिक्रिया आधी पूर्ण हो जाती है, तब समय t इक्वल्स t वन बाई टू होगा। और उस समय अभिकारक की सांद्रता उसकी प्रारम्भिक सांद्रता की आधी रह जाएगी।"
TEACHING INTENT: DERIVATION — the substitution values
VISUAL DECISION: show the two values to be substituted, beside the chain, before
substituting them.
WHAT APPEARS, to the right of the derivation column:
  **t = t₁/₂**  and  **[A] = [A₀]/2**
The second is the SAME box introduced at the definition in scene 02 — animate it
travelling from where it has been sitting, so the student sees it is not new.
AVATAR: MODE C, unchanged.
LAYOUT: substitution values in a side panel, clear of the main column.
IMPLEMENTATION: MANIM

---

# SCENE 08
TIME: 01:16 – 01:24
NARRATION: "अब इन दोनों मानों को समीकरण में रख देते हैं। अब इसे हल करने पर"
TEACHING INTENT: DERIVATION — substitution and simplification
DERIVATION STEPS:
  - **Step 7** — **k t₁/₂ = [A₀] − [A₀]/2**
    TRANSFORMATION: both values substituted into step 6
    VISUAL ACTION: **t** in step 6 is highlighted and the **t₁/₂** panel flies
    into its place; **[A]** is highlighted and **[A₀]/2** flies into its place.
    The new line writes below.
  - **Step 8** — **k t₁/₂ = [A₀]/2**
    TRANSFORMATION: right side simplified
    VISUAL ACTION: **[A₀] − [A₀]/2** briefly highlights, then collapses to
    **[A₀]/2** in place — the arithmetic happens where the student is looking
  - **Step 9** — **t₁/₂ = [A₀] / (2k)**
    TRANSFORMATION: divided through by k
    VISUAL ACTION: k moves across the equals sign into the denominator
HIGHLIGHT: each substituted symbol flashes in accent at the moment it is replaced.
WHAT REMAINS: the full chain.
AVATAR: MODE C, unchanged.
IMPLEMENTATION: MANIM

---

# SCENE 09
TIME: 01:24 – 01:35
NARRATION: "अब बच्चों यहाँ से ज़रूरी निष्कर्ष निकलता है। क्योंकि k और टू नियत हैं। इसलिए, यानी शून्य कोटि की अभिक्रिया का अर्द्ध-आयुकाल अभिकारक की प्रारम्भिक सांद्रता के समानुपाती होता है।"
TEACHING INTENT: CONCLUSION
VISUAL DECISION: show WHY the proportionality follows, then close the loop with
the target stated at the start.
WHAT APPEARS:
  - **2k** in the denominator of step 9 is highlighted and annotated **नियत**
  - the final line writes, boxed in brand accent: **t₁/₂ ∝ [A₀]**
  - the dim target line at the top (**सिद्ध करना है: t₁/₂ ∝ [A₀]**) brightens to
    match, and a tick appears beside it
ANIMATION: the highlight on 2k, then the conclusion line, then the target
brightening — in that order, so the proof visibly closes.
WHY: naming 2k as constant is the actual reason; without it the last line is an
assertion.
AVATAR: MODE C, unchanged.
PERSISTENCE: the whole chain plus the conclusion holds to the end of the part.
IMPLEMENTATION: MANIM

---

# SCENE 10
TIME: 01:35 – 01:43 (end of part 1)
NARRATION: "बच्चों अभी हमने समझा… वो समझेंगे नेक्स्ट पार्ट में।"
TEACHING INTENT: RECAP + TRANSITION
VISUAL DECISION: **VISUAL: NONE** — clear, presenter returns.
AVATAR: MODE A, one eased change.
IMPLEMENTATION: NONE

---

# PART 2

# SCENE 11
TIME: 00:00 – 00:15
NARRATION: recap, "…क्योंकि सौ में से अस्सी बच्चे यहीं गलती करते हैं।"
TEACHING INTENT: RECAP + WARNING
VISUAL DECISION: **VISUAL: NONE**
AVATAR: MODE A — large. Batch 1 put an unrelated beaker photograph here.
IMPLEMENTATION: NONE

---

# SCENE 12
TIME: 00:15 – 00:38
NARRATION: "तो सबसे पहले लिखेंगे शून्य कोटि की अभिक्रिया का समीकरण। अब हमें अर्द्ध-आयुकाल निकालना है, तो यहाँ t उस समय को दर्शाता है… अर्द्ध-आयुकाल पर अभिकारक का सान्द्रण उसके प्रारम्भिक सान्द्रण का आधा रह जाता है।"
TEACHING INTENT: DERIVATION — the exam-ready rewrite
VISUAL DECISION: this part is "how to write it in the exam", so show the
**compact answer form** — the three lines a student actually writes — not the
full nine-step working again.
WHAT APPEARS, one line per spoken step:
  - 00:15 **[A] = [A₀] − k t**       ← the integrated equation
  - 00:18 **k t = [A₀] − [A]**       ← rearranged
  - 00:26 **t = t₁/₂ ,  [A] = [A₀]/2**  ← the substitution, as a labelled aside
ANIMATION: lines write in sequence; the focus box advances.
**Every symbol used must already be defined on screen** — no `x`, no quantity
that has not been introduced.
LAYOUT: vertical column, LARGE, centred block.
AVATAR: MODE C.
PERSISTENCE: all lines stay.
IMPLEMENTATION: MANIM

---

# SCENE 13
TIME: 00:38 – 00:49
NARRATION: "अब इसे हल करने पर मिलता है। और एक बात दिमाग में बैठा लो, इस समीकरण में A जीरो ऊपर है और टू के नियत है, इसलिए t वन भाई टू A जीरो के समानुपाती होगा।"
TEACHING INTENT: DERIVATION + CONCLUSION + KEYWORD
VISUAL DECISION: the result, with the reason marked ON the expression.
WHAT APPEARS:
  - **t₁/₂ = [A₀] / (2k)**
  - **[A₀]** in the numerator highlighted, annotated **ऊपर है**
  - **2k** in the denominator highlighted, annotated **नियत**
  - then **t₁/₂ ∝ [A₀]**, boxed in brand accent
ANIMATION: numerator highlight, then denominator highlight, then the conclusion —
matching the order he says them.
WHY: he is pointing at two positions in one expression. The annotations must sit
on those positions, not be restated as prose.
AVATAR: MODE C, unchanged.
PERSISTENCE: holds.
IMPLEMENTATION: MANIM

---

# SCENE 14
TIME: 00:49 – 00:59
NARRATION: "इससे स्पष्ट है कि शून्य कोटि की अभिक्रिया का अर्द्ध-आयुकाल अभिकारक के प्रारम्भिक सान्द्रण के समानुपाती होता है।"
TEACHING INTENT: CONCLUSION + COMPARISON
VISUAL DECISION: contrast with first order — the script asks for it, and the
contrast is what makes the zero-order result memorable.
WHAT APPEARS, as a two-column comparison:
  | **शून्य कोटि** | **प्रथम कोटि** |
  | t₁/₂ = [A₀]/2k | t₁/₂ = 0.693/k |
  | **[A₀] पर निर्भर** | **[A₀] से स्वतंत्र** |
ANIMATION: the zero-order column is already known and slides left; the
first-order column fades in beside it; the contrasting bottom row appears last.
LAYOUT: two columns, full width, rows aligned so the student compares like with
like.
AVATAR: MODE B — a comparison is wider than it is tall.
COLOURS: zero order in the working accent; first order in a neutral second tone.
PERSISTENCE: holds to the end of the teaching section.
IMPLEMENTATION: MANIM

---

# SCENE 15
TIME: 01:03 onward — "…आपकी स्क्रीन पर आ जाएगा"
VISUAL DECISION: answer-page template on the cue. Not planned here.
IMPLEMENTATION: TEMPLATE

---

# FINAL SCENE SUMMARY

**Manim**
- half-life definition card + the symbolic condition [A] = [A₀]/2, introduced
  early and REUSED as the substitution later
- the target statement t₁/₂ ∝ [A₀], held dim through the proof and brightened
  when proved
- **the nine-step derivation chain**, growing one line at a time, focus box
  advancing, every earlier line retained
- substitution animation: symbols flying into the positions they replace
- conclusion with 2k annotated as constant
- exam-form rewrite in part 2
- zero-order vs first-order comparison table

**Images**
- none. This is entirely symbolic; Manim is exact and an image could only be
  less accurate.

**No visual**
- part 1: 00:00–00:19 (hook), 00:19–00:27 (warning), 01:35–01:43 (transition)
- part 2: 00:00–00:15 (recap and warning)

**Reusable**
- **[A] = [A₀]/2** is created once at the definition and travels into the
  substitution — one object, not two
- the derivation column is built once and only added to; never rebuilt

**New assets**
- none requiring generation. No image cost.
