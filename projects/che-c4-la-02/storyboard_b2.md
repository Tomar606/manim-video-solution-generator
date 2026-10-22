# KMnO₄ के ऑक्सीकारक गुण — तीन माध्यमों में

## GLOBAL VISUAL STRATEGY

**Teaching objective:** the question asks for the oxidising behaviour in THREE
media with TWO examples each. The whole answer is a three-way comparison, so the
governing visual is a **three-column comparison table that fills in** — and it
must be on screen, complete, when he does the final recall.

**Key concepts:** the reduction product differs by medium — acidic → Mn²⁺,
alkaline → MnO₄²⁻, neutral → MnO₂. Everything else hangs off that one contrast,
which he states three separate times.

**Visual language:** one persistent three-column frame, filled column by column
as each medium is taught, with each column's equation shown large while that
column is live. The frame never disappears; only its contents grow.

**Main visual assets:** the three-medium comparison table; six equations
(one reduction + one example per medium); oxidation-state annotations.

**Avatar strategy:** MODE B while the table is being filled; MODE C for the
long equations; MODE A over the hook and the transitions.

**BATCH-1 DEFECTS THIS FIXES:** `Mn^{2+}` printed as raw markup because maths was
written into a text cell; equations rendered small; the comparison sat frozen
for 36 seconds. Here every superscript is MATHS, equations split at the arrow,
and the table changes on every medium.

---

# SCENE 01
TIME: 00:23 – 00:40
NARRATION: "तो KMnO₄ का विलयन अम्लीय हो, क्षारीय हो या उदासीन — तीनों ही माध्यमों में यह ऑक्सीकारक की तरह काम करता है, लेकिन तीनों माध्यमों में KMnO₄ का अपचयन अलग-अलग तरीके से होता है।"
TEACHING INTENT: INTRODUCTION + COMPARISON — **the frame is created here**
VISUAL DECISION: put up the empty three-column frame. The student sees the shape
of the answer before any content arrives, and knows three columns are coming.
VISUAL TYPE: Manim comparison table
WHAT APPEARS:
  - three column headings: **अम्लीय** | **क्षारीय** | **उदासीन**
  - one empty row beneath, labelled **अपचयन उत्पाद**
ANIMATION: the three headings appear together as he names the three media; the
empty row rules in.
LAYOUT: three columns, **full width** — a three-way comparison needs horizontal
room. Upper-centre of the primary visual area.
AVATAR: MODE B — reduced, low, so the table sits above him.
COLOURS: one distinct accent per medium, fixed for the whole video. Every later
equation borrows its column's colour, so the student always knows which medium
they are looking at.
PERSISTENCE: **the table persists to the end of part 2.** It is the answer.
IMPLEMENTATION: MANIM

---

# SCENE 02
TIME: 00:40 – 00:54
NARRATION: "अम्लीय माध्यम में KMnO₄, Mn²⁺ में अपचयित होता है"
TEACHING INTENT: CONCEPT_EXPLANATION
VISUAL DECISION: fill the first cell only.
WHAT APPEARS: under **अम्लीय**, the cell fills with **Mn²⁺**
NOTE: **Mn²⁺ is MATHS.** In batch 1 this cell was written as text and printed
`Mn^{2+}` on screen literally. Superscripts render through LaTeX; the column
heading in Devanagari renders through Text. The two never mix in one object.
ANIMATION: the cell fills, the acidic column brightens, the other two stay dim.
AVATAR: MODE B, unchanged.
IMPLEMENTATION: MANIM

---

# SCENE 03
TIME: 00:54 – 01:06
NARRATION: "सबसे पहले अम्लीय माध्यम — अम्लीय माध्यम में KMnO₄ तनु H₂SO₄ की उपस्थिति में अपचयित होकर Mn²⁺ बनाता है"
TEACHING INTENT: FORMULA
VISUAL DECISION: the acidic reduction equation, shown large below the table.
WHAT APPEARS:
  - heading **अम्लीय माध्यम (तनु H₂SO₄)**
  - **2KMnO₄ + 3H₂SO₄ → K₂SO₄ + 2MnSO₄ + 3H₂O + 5[O]**
ANIMATION: reactants, arrow, products, in spoken order. **[O]** appears last and
in accent — it is the oxidising species the examples will consume.
LAYOUT: equation LARGE, **splits at the arrow** if it exceeds the width. Table
stays above it, acidic column lit.
AVATAR: **MODE C** — long equation.
COLOURS: equation in the acidic accent; **[O]** highlighted.
PERSISTENCE: holds while the example is given.
IMPLEMENTATION: MANIM

---

# SCENE 04
TIME: 01:06 – 01:26
NARRATION: "चलो अब इसका एक उदाहरण देखते हैं। यहाँ आयरन का ऑक्सीकरण और मैंगनीज़ का अपचयन हो रहा है… इसीलिए KMnO₄ ऑक्सीकारक और FeSO₄ अपचायक है"
TEACHING INTENT: EXAMPLE + CONCEPT_EXPLANATION
VISUAL DECISION: the example equation, with the two changes marked on it — this
is where oxidising vs reducing agent is decided, so both must be visible at once.
WHAT APPEARS:
  - **2FeSO₄ + H₂SO₄ + [O] → Fe₂(SO₄)₃ + H₂O**
  - the **[O]** in this equation flashes and links back to the **[O]** in the
    equation above — they are the same species, produced there and used here
  - two annotations: **Fe²⁺ → Fe³⁺ (ऑक्सीकरण)** and **Mn: +7 → +2 (अपचयन)**
  - conclusion line: **KMnO₄ — ऑक्सीकारक ; FeSO₄ — अपचायक**
ANIMATION: equation assembles; the [O] link draws; the two annotations appear on
their phrases; the conclusion writes last.
WHY: he names oxidation and reduction in the same breath — showing both changes
on one equation is what makes "इसलिए" mean something.
LAYOUT: example equation below the reduction equation; annotations beside the
species they describe.
AVATAR: MODE C, unchanged.
IMPLEMENTATION: MANIM

---

# PART 2

# SCENE 05
TIME: 00:09 – 00:31
NARRATION: "क्षारीय माध्यम में KMnO₄, MnO₄²⁻ में अपचयित होता है… अम्लीय — Mn²⁺, क्षारीय — MnO₄²⁻। इसे ऐसे दिमाग में बिठा लो"
TEACHING INTENT: COMPARISON + MEMORY_CUE
VISUAL DECISION: the table returns with the acidic cell already filled; the
alkaline cell now fills. He is explicitly contrasting the two, so both must be
visible together.
WHAT APPEARS:
  - table, **अम्लीय → Mn²⁺** already there
  - **क्षारीय → MnO₄²⁻** fills
  - as he says "अम्लीय — Mn²⁺, क्षारीय — MnO₄²⁻", both cells brighten in turn
ANIMATION: the alkaline cell fills; then an alternating highlight between the
two cells, matching his back-and-forth.
WHY: this is the comparison the question is built on. Two filled cells side by
side say it better than any sentence.
AVATAR: MODE B.
PERSISTENCE: both cells stay filled for the rest of the video.
IMPLEMENTATION: MANIM

---

# SCENE 06
TIME: 00:31 – 00:46
NARRATION: "क्षारीय माध्यम में KMnO₄ अपचयित होकर K₂MnO₄ या MnO₄²⁻ बनाता है। इसमें Mn की ऑक्सीकरण अवस्था प्लस 7 से प्लस 6 हो जाती है, इसलिए अपचयन होता है"
TEACHING INTENT: FORMULA + CONCEPT_EXPLANATION
VISUAL DECISION: the alkaline reduction equation with the oxidation-state change
marked on the Mn itself.
WHAT APPEARS:
  - heading **क्षारीय माध्यम**
  - **2KMnO₄ + 2KOH → 2K₂MnO₄ + H₂O + [O]**
  - **+7** above the Mn on the left, **+6** above the Mn on the right, with a
    short arrow between them labelled **अपचयन**
ANIMATION: equation assembles; then +7 appears, then +6, then the arrow — in the
order he says them.
WHY: the oxidation-state change is his stated reason. Placed on the atoms, it is
checkable; written as prose, it is a claim.
LAYOUT: equation large, splits at the arrow if needed; states directly above
their atoms.
AVATAR: MODE C.
COLOURS: alkaline accent throughout.
IMPLEMENTATION: MANIM

---

# SCENE 07
TIME: 00:46 – 01:04
NARRATION: "चलो अब इसे एक उदाहरण से समझते हैं। KI का KIO₃ में ऑक्सीकरण… यहाँ I⁻ से KIO₃ बन रहा है, इसलिए यह ऑक्सीकरण, और MnO₂ बन रहा है… इसलिए KI अपचायक और KMnO₄ ऑक्सीकारक है"
TEACHING INTENT: EXAMPLE
WHAT APPEARS:
  - **2KMnO₄ + H₂O + KI → KIO₃ + 2MnO₂ + 2KOH**
  - annotation: **I⁻ → IO₃⁻ (ऑक्सीकरण)**
  - conclusion: **KI — अपचायक ; KMnO₄ — ऑक्सीकारक**
LAYOUT: same layout as the acidic example, so the pattern repeats and the
student learns the shape of the answer.
AVATAR: MODE C.
IMPLEMENTATION: MANIM

---

# SCENE 08
TIME: 01:08 – 01:20
NARRATION: "उदासीन माध्यम में KMnO₄ ऑक्सीकारक की तरह कार्य करता है और MnO₂ में अपचयित हो जाता है"
TEACHING INTENT: CONCEPT_EXPLANATION + FORMULA
VISUAL DECISION: the third cell fills — the table is now complete.
WHAT APPEARS:
  - **उदासीन → MnO₂** fills the last cell; **all three columns now full**
  - below: heading **उदासीन माध्यम** and
    **2KMnO₄ + H₂O → 2MnO₂ + 2KOH + 3[O]**
ANIMATION: the cell fills; the whole table pulses once — it is complete for the
first time.
AVATAR: MODE C for the equation.
COLOURS: neutral-medium accent.
IMPLEMENTATION: MANIM

---

# SCENE 09
TIME: 01:20 – 01:26
NARRATION: "तो चलो इसे भी एक उदाहरण से समझते हैं। H₂S का ऑक्सीकरण। इसमें H₂S का ऑक्सीकरण होकर सल्फर यानी S बनता है"
TEACHING INTENT: EXAMPLE
WHAT APPEARS:
  - **2KMnO₄ + H₂O + 3H₂S → 2MnO₂ + 2KOH + 3S + 2H₂O**
  - annotation: **H₂S → S (ऑक्सीकरण)**
LAYOUT: same as the other two examples.
AVATAR: MODE C.
IMPLEMENTATION: MANIM

---

# SCENE 10
TIME: 01:26 – 01:37
NARRATION: "अब यहाँ एक बात दिमाग में छाप लो — अम्लीय में Mn²⁺, क्षारीय में MnO₄²⁻ और उदासीन में MnO₂। बच्चों, बस इतना याद रख लिया तो परीक्षा में कभी नहीं भूलोगे।"
TEACHING INTENT: MEMORY_CUE + RECAP — **the payoff**
VISUAL DECISION: clear the equations, leave the completed table ALONE, at full
size. This is the one thing he wants them to carry out of the video.
WHAT APPEARS: the three-column table, complete:
  | **अम्लीय** | **क्षारीय** | **उदासीन** |
  | **Mn²⁺** | **MnO₄²⁻** | **MnO₂** |
ANIMATION: equations fade out; the table grows to full size; a highlight travels
across the three cells in time with him naming them.
WHY: he is reciting exactly the three cells that have been on screen since 00:23.
Nothing else should compete with them here.
LAYOUT: table centred, full width, LARGE — the only object on the stage.
AVATAR: MODE B — low, so the table has the height.
COLOURS: each cell in its own medium accent, held all video.
PERSISTENCE: holds to the end of the teaching section.
IMPLEMENTATION: MANIM

---

# SCENE 11
TIME: 01:40 onward — "…आपकी स्क्रीन पर आ जाएगा"
VISUAL DECISION: answer-page template on the cue. Not planned here.
IMPLEMENTATION: TEMPLATE

---

# FINAL SCENE SUMMARY

**Manim**
- **the three-medium comparison table**, created empty at 00:23 of part 1 and
  filled one cell per medium — the spine and the final payoff
- three reduction equations (acidic, alkaline, neutral), each large, each split
  at the arrow when long
- three example equations, laid out identically so the answer pattern repeats
- oxidation-state annotations (+7 → +6) placed on the atoms
- the [O] link between a reduction equation and the example that consumes it

**Images**
- none. Every object is an equation or a table.

**No visual**
- part 1: 00:00–00:23 (hook), 01:26–01:37 (transition)
- part 2: 00:00–00:09 (recap)

**Reusable**
- the table exists from the first teaching moment to the last; three cells fill
  at three different times. One object, never rebuilt.
- one accent colour per medium, fixed across both parts, so an equation's colour
  tells the student which column it belongs to

**New assets**
- none requiring generation. No image cost.

**NOTE:** every superscript and charge here (Mn²⁺, MnO₄²⁻, I⁻, Fe³⁺) is MATHS,
not text. Batch 1 printed `Mn^{2+}` on screen because a maths string was placed
in a text cell.
