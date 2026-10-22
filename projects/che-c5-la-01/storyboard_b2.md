# संकुल आयन — संकरण एवं ज्यामिति

## GLOBAL VISUAL STRATEGY

**Teaching objective:** work two complexes through the SAME fixed procedure and
end with the contrast between them. He opens by saying students reverse the
order — *"बहुत सारे बच्चे ऑर्डर उल्टा कर देते हैं"* — so the procedure itself is
the primary visual, and each complex is that procedure being executed.

**Key concepts:** oxidation state → d-configuration → ligand strength → pairing
or not → hybridisation → geometry → unpaired electrons → magnetic behaviour.
[NiCl₄]²⁻ with a weak ligand: no pairing, sp³, tetrahedral, 2 unpaired.
[Fe(CN)₆]³⁻ with a strong ligand: pairing, d²sp³, octahedral, 1 unpaired.

**Visual language:** a **procedure ladder** built once in part 1 and reused as
the frame for both complexes. Each complex fills the same rungs, so the student
sees one method applied twice, not two unrelated worked examples. Orbital boxes
show pairing physically — this is the one place an animation carries the actual
mechanism.

**Main visual assets:** the procedure ladder; two filled instances of it; orbital
box diagrams showing electrons pairing or not pairing; the closing comparison.

**Avatar strategy:** MODE A over hooks and transitions; MODE C for the ladder and
the orbital diagrams, which are the subject; MODE B for the closing comparison.

---

# SCENE 01
TIME: 00:20 – 00:40
NARRATION: "सबसे पहले एक क्रम याद कर लो, क्योंकि यहाँ बहुत सारे बच्चे ऑर्डर उल्टा कर देते हैं… पहले धातु की ऑक्सीकरण अवस्था और d-विन्यास निकालो। फिर देखो, लिगैंड दुर्बल है या प्रबल, इसी से तय होता है कि युग्मन होगा या नहीं। और युग्मन से ही संकरण बनता है। और संकरण से ज्यामिति।"
TEACHING INTENT: PROCESS + MEMORY_CUE — **the spine is created here**
VISUAL DECISION: build the procedure as a numbered ladder, one rung per step, in
the exact order he gives it. Getting the order right IS the lesson.
VISUAL TYPE: Manim process ladder
WHAT APPEARS, one rung per phrase:
  ① **ऑक्सीकरण अवस्था → d-विन्यास**
  ② **लिगैंड — दुर्बल या प्रबल?**
  ③ **युग्मन होगा या नहीं**
  ④ **संकरण**
  ⑤ **ज्यामिति**
ANIMATION: each rung fades in with a downward arrow from the one above, in time
with him naming it. The chain of arrows is the point — each step feeds the next.
LAYOUT: vertical ladder, centred — a sequence of dependencies reads downward.
Compact rungs so all five fit at a readable size.
AVATAR: MODE B.
COLOURS: rungs neutral; the arrow chain in accent so the dependency reads.
PERSISTENCE: **the ladder persists through both parts.** For each complex it sits
to one side, small, with the current rung lit.
IMPLEMENTATION: MANIM

---

# SCENE 02
TIME: 00:45 – 00:55
NARRATION: "[NiCl₄]²⁻, संकरण और ज्यामिति। मतलब इस संकुल में Ni की ऑक्सीकरण अवस्था प्लस 2 है। और इसका विन्यास है आर्गन 3d⁸।"
TEACHING INTENT: EXAMPLE — rung ①
VISUAL DECISION: the complex as a title, then rung ① executed.
WHAT APPEARS:
  - title **[NiCl₄]²⁻**, large, at the top
  - ladder to the side with **rung ① lit**
  - the working: **Ni: +2** then **[Ar] 3d⁸**
ANIMATION: oxidation state writes, then the configuration.
LAYOUT: complex title top-centre; ladder small at the left; working centre.
AVATAR: MODE B.
COLOURS: this complex keeps ONE accent for both parts, so it stays identifiable
in the final comparison.
IMPLEMENTATION: MANIM

---

# SCENE 03
TIME: 00:55 – 01:10
NARRATION: "चूँकि Cl⁻ दुर्बल क्षेत्र लिगैंड है, इसलिए इलेक्ट्रॉनों का युग्मन नहीं होता और sp³ संकरण होता है। इसमें दो अयुग्मित इलेक्ट्रॉन बचते हैं, इसलिए यह अनुचुम्बकीय प्रकृति का है और इसकी ज्यामिति चतुष्फलकीय होती है।"
TEACHING INTENT: CONCEPT_EXPLANATION + PROCESS — rungs ②–⑤
VISUAL DECISION: **show the orbital boxes and let the student SEE that nothing
pairs.** This is the mechanism; stating "no pairing" teaches far less than
showing electrons staying apart.
WHAT APPEARS, rung by rung as he speaks:
  - ② **Cl⁻ — दुर्बल क्षेत्र**
  - ③ orbital boxes for 3d⁸ drawn; as he says युग्मन नहीं होता, the electrons
    **stay where they are** — two boxes visibly keep single electrons, and a
    label **युग्मन नहीं** appears
  - ④ the vacant **4s + 4p³** boxes highlight and merge into **sp³**
  - ⑤ **चतुष्फलकीय** — a tetrahedron sketch draws
  - beside it: **अयुग्मित n = 2 → अनुचुम्बकीय**
ANIMATION: the two unpaired electrons pulse when he says "दो अयुग्मित इलेक्ट्रॉन
बचते हैं" — the student counts them on screen. The 4s and 4p boxes visibly
combine into the sp³ label.
**MECHANISM CHECK:** a weak-field ligand does NOT pair the d electrons. The boxes
must stay as they are; animating a pairing here would teach the opposite.
LAYOUT: orbital boxes centre, full width; geometry sketch to the right; ladder
still lit at the left.
AVATAR: **MODE C** — orbital boxes plus a geometry sketch need the frame.
PERSISTENCE: the completed result line holds; the boxes stay until the part ends.
IMPLEMENTATION: MANIM

---

# SCENE 04
TIME: 01:11 – 01:22
NARRATION: "बस यहाँ एक बात पक्की याद रखना, दुर्बल क्षेत्र लिगैंड में इलेक्ट्रॉनों का युग्मन नहीं होता, इसलिए sp³ संकरण और चतुष्फलकीय ज्यामिति बनती है।"
TEACHING INTENT: MEMORY_CUE
VISUAL DECISION: compress what is already on screen into the one line to
remember; no new object.
WHAT APPEARS, boxed beneath the existing diagram:
  **दुर्बल लिगैंड → युग्मन नहीं → sp³ → चतुष्फलकीय**
ANIMATION: the three existing results (no pairing, sp³, tetrahedral) each fly
down into their place in this single chain — reusing the objects rather than
writing new ones.
AVATAR: MODE C, unchanged.
PERSISTENCE: **this chain is kept** — it becomes the left column of the final
comparison in part 2.
IMPLEMENTATION: MANIM

---

# PART 2

# SCENE 05
TIME: 00:12 – 00:33
NARRATION: "[Fe(CN)₆]³⁻ — संकरण और ज्यामिति। अब वही पूरा क्रम यहाँ भी लगाते हैं… इस संकुल में Fe की ऑक्सीकरण अवस्था प्लस थ्री है, और इसका विन्यास है आर्गन 3d⁵।"
TEACHING INTENT: EXAMPLE — rung ① again
VISUAL DECISION: the SAME ladder returns, reset, with the new complex. He says
"वही पूरा क्रम यहाँ भी लगाते हैं" — so the visual must visibly be the same
procedure, not a new one.
WHAT APPEARS:
  - title **[Fe(CN)₆]³⁻**
  - the ladder returns, rungs reset to neutral, **rung ① lit**
  - **Fe: +3** then **[Ar] 3d⁵**
ANIMATION: the ladder slides back in — same object, same order — and resets.
AVATAR: MODE B.
COLOURS: this complex takes the SECOND accent, held for the rest of the video.
IMPLEMENTATION: MANIM

---

# SCENE 06
TIME: 00:33 – 00:56
NARRATION: "CN⁻ प्रबल क्षेत्र लिगैंड है, इसकी उपस्थिति में 3d इलेक्ट्रॉनों का युग्मन हो जाता है, और केवल एक अयुग्मित इलेक्ट्रॉन शेष रहता है। इसी कारण d²sp³ संकरण होता है, जिससे यह आंतरिक कक्षक संकुल बनाता है, और इसकी ज्यामिति अष्टफलकीय होती है। एक अयुग्मित इलेक्ट्रॉन होने से यह अनुचुम्बकीय प्रकृति का है।"
TEACHING INTENT: CONCEPT_EXPLANATION + PROCESS — rungs ②–⑤
VISUAL DECISION: **animate the pairing.** This is the exact contrast with part 1
and the only way the student feels the difference a strong ligand makes.
WHAT APPEARS, rung by rung:
  - ② **CN⁻ — प्रबल क्षेत्र**
  - ③ orbital boxes for 3d⁵ drawn with five single electrons; then, as he says
    युग्मन हो जाता है, **electrons visibly MOVE and pair up** — four collapse
    into two paired boxes, leaving **one** unpaired, which pulses
  - the freed d boxes are marked **रिक्त**
  - ④ **two vacant d + 4s + 4p³** highlight and merge into **d²sp³**;
    label **आंतरिक कक्षक संकुल**
  - ⑤ **अष्टफलकीय** — an octahedron sketch draws
  - beside it: **अयुग्मित n = 1 → अनुचुम्बकीय**
ANIMATION: the pairing movement takes ~1.5s and is the visual centrepiece —
electrons sliding together, boxes emptying, and the emptied boxes then being
consumed by the hybridisation. Cause and consequence in one continuous motion.
**MECHANISM CHECK:** a strong-field ligand DOES pair the d electrons, and the
pairing is what frees the d orbitals that d²sp³ needs. The order matters: pair
first, then hybridise.
LAYOUT: orbital boxes centre, full width; geometry sketch right.
AVATAR: **MODE C.**
PERSISTENCE: results hold into the comparison.
IMPLEMENTATION: MANIM

---

# SCENE 07
TIME: 00:56 – 01:15
NARRATION: "त्वरित तुलना — याद करने की युक्ति। अब सबसे ज़रूरी हिस्सा — दोनों का फर्क… मतलब दुर्बल लिगैंड में sp³ के साथ चतुष्फलकीय, और प्रबल लिगैंड में d²sp³ के साथ अष्टफलकीय।"
TEACHING INTENT: COMPARISON — **the payoff**
VISUAL DECISION: two columns, one per complex, rows aligned so every line
contrasts directly. He calls this the most important part and the place students
go wrong, so nothing else should be on screen.
WHAT APPEARS:
  |                | **[NiCl₄]²⁻** | **[Fe(CN)₆]³⁻** |
  | लिगैंड         | Cl⁻ — दुर्बल | CN⁻ — प्रबल |
  | युग्मन         | नहीं | होता है |
  | संकरण          | **sp³** | **d²sp³** |
  | ज्यामिति       | **चतुष्फलकीय** | **अष्टफलकीय** |
  | अयुग्मित (n)   | 2 | 1 |
ANIMATION: the left column is already known — the chain kept from part 1 scene 04
slides into place. The right column then fills row by row as he says each
contrast, each cell landing opposite its counterpart.
WHY: aligned rows mean the student never hunts for which weak-ligand result
matches which strong-ligand result — that hunting is the confusion he names.
LAYOUT: two columns, **full width** — comparisons need horizontal room. Five
short rows.
AVATAR: MODE B — low, so the table has the height.
COLOURS: each column keeps the accent its complex has carried since it was
introduced.
PERSISTENCE: holds to the end of the teaching section.
IMPLEMENTATION: MANIM

---

# SCENE 08
TIME: 01:18 onward — "…नोट्स बटन पर मिल जाएगा"
VISUAL DECISION: this video points to the NOTES button, so the answer page
follows at the end rather than on an on-screen cue. Template.
IMPLEMENTATION: TEMPLATE

---

# FINAL SCENE SUMMARY

**Manim**
- **the five-rung procedure ladder**, built in part 1 and REUSED unchanged for
  the second complex — the visual statement that one method covers both
- orbital box diagrams, twice: electrons staying apart (weak field) and
  electrons visibly pairing (strong field)
- hybrid-orbital merge animations: 4s+4p³ → sp³, and 2d+4s+4p³ → d²sp³
- tetrahedron and octahedron sketches
- the weak-ligand result chain, kept from part 1 and reused as the left column
- the five-row final comparison

**Images**
- none. Orbital occupancy and coordination geometry are exactly what Manim is
  for; a generated picture of a molecule would be less accurate and could not be
  animated to show pairing.

**No visual**
- part 1: 00:00–00:20 (hook), 01:22–01:32 (transition)
- part 2: 00:00–00:12 (recap)

**Reusable**
- the ladder: one object, two complexes, both parts
- the part-1 result chain becomes the comparison's left column — created once
- one fixed accent per complex, held across both parts

**New assets**
- none requiring generation. No image cost.
