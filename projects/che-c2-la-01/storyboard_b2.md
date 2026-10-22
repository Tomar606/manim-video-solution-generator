# फैराडे के विद्युत्-अपघटन के नियम

## GLOBAL VISUAL STRATEGY

**Teaching objective:** state both laws and derive each one's formula. The
question is simply *नियम लिखिए*, so the exam answer is: statement, symbols,
derivation, final formula — for each law. Then the distinction between them,
which he spells out at the end and calls the thing to remember.

**Key concepts:** First law — W ∝ Q, and since Q = i×t, W = Z·i·t. Second law —
with the SAME quantity of electricity through different electrolytes,
W ∝ E, so W₁/W₂ = E₁/E₂. The contrast is that in the first law the charge varies
and in the second it is held constant.

**Visual language:** each law is a short DERIVATION that grows line by line — the
script gives exactly the chain, and it is short enough to hold whole. The two
final formulae are then set side by side as the closing contrast.

**Main visual assets:** two derivation chains; symbol glosses; the closing
two-law comparison.

**Avatar strategy:** MODE A over hooks and transitions; MODE C for the derivation
chains; MODE B for the closing comparison.

**PACING:** first law is four lines over ~35s, second law five lines over ~25s —
roughly 6–9s per line. Short enough that each line must be a small, clearly
motivated step, which it is; nothing needs merging.

---

# SCENE 01
TIME: 00:25 – 00:38
NARRATION: "जब विद्युत्-अपघटन के दौरान किसी इलेक्ट्रोड पर मुक्त होने वाले पदार्थ की मात्रा प्रवाहित विद्युत् की मात्रा के समानुपाती होती है"
TEACHING INTENT: DEFINITION — the statement of the first law
VISUAL DECISION: the statement in exam-compressed form, as a heading the
derivation will hang under.
WHAT APPEARS:
  - heading **फैराडे का प्रथम नियम**
  - one line: **मुक्त पदार्थ की मात्रा ∝ प्रवाहित विद्युत् की मात्रा**
WHY: the screen carries the compressed form the student writes, not the spoken
sentence. Repeating the caption underneath would be the "screen restates the
narration" failure.
LAYOUT: upper-centre; heading at the same scale as the body text, never smaller.
AVATAR: MODE B.
PERSISTENCE: the heading stays above the derivation for the whole law.
IMPLEMENTATION: MANIM

---

# SCENE 02
TIME: 00:38 – 00:45
NARRATION: "W समानुपाती Q। यहाँ W है मुक्त पदार्थ की मात्रा और Q है प्रवाहित विद्युत् की मात्रा"
TEACHING INTENT: DERIVATION — step 1
DERIVATION STEP:
  - **Step 1** — CURRENT: **W ∝ Q**
    TRANSFORMATION: the statement written in symbols
    VISUAL ACTION: line 1 writes and is boxed as current; then, as he names each
    symbol, a gloss appears beside it — **W = मुक्त पदार्थ की मात्रा**,
    **Q = प्रवाहित विद्युत् की मात्रा**
WHY: every symbol is glossed at the moment it is introduced. Nothing later in
the chain uses a symbol the student has not been given.
LAYOUT: derivation as a left-aligned column, centred as a block, LARGE. Glosses
smaller, to the right.
AVATAR: **MODE C** — a growing chain needs vertical room.
COLOURS: current line in accent inside the focus box; glosses quiet.
PERSISTENCE: all lines stay.
IMPLEMENTATION: MANIM

---

# SCENE 03
TIME: 00:45 – 00:57
NARRATION: "अब विद्युत् की मात्रा को हम ऐसे लिख सकते हैं — Q बराबर i गुना t, जहाँ i है विद्युत् धारा और t है समय। इसलिए Q की जगह इसका मान रख देते हैं"
TEACHING INTENT: DERIVATION — steps 2 and 3
DERIVATION STEPS:
  - **Step 2** — **Q = i × t**, with glosses **i = धारा**, **t = समय**
  - **Step 3** — **W ∝ i × t**
    TRANSFORMATION: Q replaced by i×t
    VISUAL ACTION: the **Q** in line 1 highlights, and the **i × t** from line 2
    physically travels into its position. The new line writes below.
WHY: showing the substitution as a movement is what makes step 3 follow from
steps 1 and 2 rather than appear from nowhere.
HIGHLIGHT: Q flashes at the moment it is replaced.
AVATAR: MODE C, unchanged.
IMPLEMENTATION: MANIM

---

# SCENE 04
TIME: 00:57 – 01:08
NARRATION: "हटाने पर W बराबर Z गुना i गुना t, जहाँ Z है विद्युत्-रासायनिक तुल्यांक"
TEACHING INTENT: DERIVATION — step 4, the result
DERIVATION STEP:
  - **Step 4** — **W = Z i t**
    TRANSFORMATION: proportionality removed by introducing the constant Z
    VISUAL ACTION: the **∝** in line 3 morphs into **=** while **Z** appears in
    front of i t — so the student sees exactly what removing a proportionality
    costs. Gloss: **Z = विद्युत्-रासायनिक तुल्यांक**
LAYOUT: final line boxed in brand accent.
AVATAR: MODE C, unchanged.
PERSISTENCE: the complete four-line chain holds.
IMPLEMENTATION: MANIM

---

# SCENE 05
TIME: 01:08 – 01:18
NARRATION: "तो पहले नियम में बस इतना याद रहना चाहिए — जितनी अधिक विद्युत् प्रवाहित होगी, उतनी ही अधिक पदार्थ की मात्रा मुक्त होगी। W बराबर Z गुना i गुना t"
TEACHING INTENT: MEMORY_CUE + CAUSE_EFFECT
VISUAL DECISION: state the qualitative meaning beside the formula that already
exists — the formula alone does not say "more current, more substance".
WHAT APPEARS: beside the boxed result, **विद्युत् ↑ → मुक्त पदार्थ ↑**
ANIMATION: the two up-arrows appear together; **W** and **i t** in the formula
brighten with them.
AVATAR: MODE C, unchanged.
PERSISTENCE: **the result W = Z i t is KEPT** — it becomes the left half of the
final comparison in part 2.
IMPLEMENTATION: MANIM

---

# PART 2

# SCENE 06
TIME: 00:16 – 00:37
NARRATION: "दूसरा नियम कहता है कि जब अलग-अलग विद्युत्-अपघट्यों में समान मात्रा में विद्युत् प्रवाहित की जाती है, तो इलेक्ट्रोड पर मुक्त होने वाले पदार्थों की मात्राएँ उनके रासायनिक तुल्यांक के समानुपाती होती हैं।"
TEACHING INTENT: DEFINITION — the statement of the second law
VISUAL DECISION: the statement, with the condition marked as the condition —
"समान मात्रा में विद्युत्" is what distinguishes this law from the first, so it
must be visually separate, not buried in a sentence.
WHAT APPEARS:
  - heading **फैराडे का द्वितीय नियम**
  - a marked condition band: **शर्त — विद्युत् की मात्रा समान**
  - the statement: **मुक्त मात्राएँ ∝ रासायनिक तुल्यांक**
ANIMATION: the condition band appears first and is held in a distinct tone; the
statement follows.
WHY: the entire difference between the two laws is which quantity is held fixed.
Giving the condition its own band is what makes the contrast legible later.
LAYOUT: upper-centre; condition band above the statement.
AVATAR: MODE B.
COLOURS: the condition in a distinct tone kept for the whole part.
IMPLEMENTATION: MANIM

---

# SCENE 07
TIME: 00:37 – 00:53
NARRATION: "मतलब, रासायनिक तुल्यांक जितना अधिक होगा, अब पदार्थ की मात्रा भी उतनी ही अधिक होगी। W, E के समानुपाती है। अब अगर दो पदार्थों की मुक्त मात्राएँ W1 और W2 हैं, और उनके रासायनिक तुल्यांक E1 और E2 हैं"
TEACHING INTENT: DERIVATION — steps 1 and 2
DERIVATION STEPS:
  - **Step 1** — **W ∝ E**, gloss **E = रासायनिक तुल्यांक**
  - **Step 2** — two substances introduced side by side:
    **पदार्थ 1: W₁, E₁**   **पदार्थ 2: W₂, E₂**
VISUAL ACTION: the two substances appear as two small labelled groups, left and
right — a ratio is about to be taken between them, so they should be spatially
separate from the start.
AVATAR: **MODE C.**
IMPLEMENTATION: MANIM

---

# SCENE 08
TIME: 00:53 – 01:02
NARRATION: "तो W1, E1 के समानुपाती है। W2, E2 के समानुपाती है। इसलिए दोनों मुक्त मात्राओं का अनुपात उनके रासायनिक तुल्यांकों के अनुपात के बराबर होगा। W1 बटा W2 बराबर E1 बटा E2"
TEACHING INTENT: DERIVATION — steps 3, 4 and the result
DERIVATION STEPS:
  - **Step 3** — **W₁ ∝ E₁** (under substance 1)
  - **Step 4** — **W₂ ∝ E₂** (under substance 2)
  - **Step 5** — **W₁ / W₂ = E₁ / E₂**
    TRANSFORMATION: the two proportionalities divided
    VISUAL ACTION: the two lines visibly slide together — W₁ over W₂ on the left,
    E₁ over E₂ on the right — forming the ratio in place. The **∝** becomes **=**
    as the constants cancel.
WHY: a ratio formed by two expressions moving into numerator and denominator is
self-explaining; written as a new line it is a fact to be taken on trust.
LAYOUT: final result boxed, centred, LARGE.
AVATAR: MODE C, unchanged.
PERSISTENCE: **the result is KEPT** for the comparison.
IMPLEMENTATION: MANIM

---

# SCENE 09
TIME: 01:02 – 01:24
NARRATION: "बस इतना याद रखना— पहले नियम में विद्युत् की मात्रा बदलेगी तो पदार्थ की मात्रा बदलेगी। W बराबर Z गुणा i गुणा t। और दूसरे नियम में विद्युत् की मात्रा समान होगी। तो पदार्थ की मात्रा रासायनिक तुल्यांक पर निर्भर करेगी। W1 बटा W2 बराबर E1 बटा E2"
TEACHING INTENT: COMPARISON + MEMORY_CUE — **the payoff**
VISUAL DECISION: the two laws side by side, aligned on the thing that differs.
He states the contrast explicitly and twice; this is what the screen must hold.
WHAT APPEARS:
  |                    | **प्रथम नियम** | **द्वितीय नियम** |
  | विद्युत् की मात्रा | **बदलती है** | **समान रहती है** |
  | निर्भरता           | विद्युत् पर | रासायनिक तुल्यांक पर |
  | सूत्र              | **W = Z i t** | **W₁/W₂ = E₁/E₂** |
ANIMATION: the first-law formula kept from part 1 flies into the left column;
the second-law result flies into the right. The middle rows then fill as he
states each contrast. The two "विद्युत् की मात्रा" cells brighten together — the
single row that separates the laws.
LAYOUT: two columns, **full width**; rows aligned so each contrast reads across.
AVATAR: MODE B — low, so the table has the height.
COLOURS: one accent per law, held from where each was derived.
PERSISTENCE: holds to the end of the teaching section.
IMPLEMENTATION: MANIM

---

# SCENE 10
TIME: from "…स्क्रीन पर आ जाएगा"
VISUAL DECISION: answer-page template on the cue. Not planned here.
IMPLEMENTATION: TEMPLATE

---

# FINAL SCENE SUMMARY

**Manim**
- first-law statement + four-step derivation (W ∝ Q → Q = i t → W ∝ i t → W = Z i t)
  with every symbol glossed as it is introduced
- the ∝ → = morph as Z is introduced
- **विद्युत् ↑ → मुक्त पदार्थ ↑** qualitative reading
- second-law statement with the "same quantity of electricity" condition banded
  separately
- second-law derivation, with the two proportionalities sliding together to form
  the ratio
- the closing two-law comparison table

**Images**
- none. Both laws are relations between quantities; there is nothing here with a
  real-world appearance that carries exam information. Batch 1 put a picture of
  two electrolytic cells over the words "जैसे पहला नियम याद किया, वैसे ही अब
  दूसरा नियम भी याद कर लो" — framing, not an object.

**No visual**
- part 1: 00:00–00:25 (hook and framing), 01:18–01:29 (transition)
- part 2: 00:00–00:16 (recap and framing)

**Reusable**
- **W = Z i t** is derived in part 1 and REUSED as the left cell of the part-2
  comparison — the same object, moved, not rewritten
- likewise W₁/W₂ = E₁/E₂ into the right cell

**New assets**
- none requiring generation. No image cost.
