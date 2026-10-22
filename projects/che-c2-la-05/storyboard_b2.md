# शुष्क सेल — सचित्र वर्णन

## GLOBAL VISUAL STRATEGY

**Teaching objective:** the question is **सचित्र वर्णन कीजिए** — describe WITH a
diagram. The labelled cross-section is not a support graphic, it IS the answer.
The presenter himself says *"प्रश्न में साफ़ लिखा है सचित्र वर्णन, इसीलिए परीक्षा
में चित्र ज़रूर बनाना"*. A version where the diagram is small is a failed version
— that shipped in batch 1 and the diagram sat under an oversized presenter.

**Key concepts:** four labelled parts (Zn casing = anode; NH₄Cl + ZnCl₂ paste =
electrolyte; carbon rod = cathode; MnO₂ + carbon powder around it). Then the
working: Zn loses electrons, electrons travel the external circuit to the carbon
rod, MnO₂ is reduced there. Then NH₃ trapped as a complex ion, ≈1.5 V, and the
leak-proof variant.

**Visual language:** ONE cross-section, built layer by layer, then animated, then
annotated with the reactions. It persists across most of both parts.

**Main visual assets:** the traced dry-cell cross-section (from the textbook
scan — do not redraw); electron-flow animation; anode/cathode/overall equations;
the complex-ion equation; a defect→fix comparison.

**Avatar strategy:** **MODE C dominates this video.** Whenever the cross-section
is on screen the presenter is chest-height at the bottom and the diagram owns
the frame. MODE A only over the hook and the transitions.

---

# SCENE 01
TIME: 00:16 – 00:30
NARRATION: "शुष्क सेल का उपयोग टॉर्च, टेप रिकॉर्डर, रेडियो, खिलौने, कैलकुलेटर आदि में… ये सेल लेकलांशी सेल के सिद्धान्त पर कार्य करता है, जिसका आविष्कार जी लेकलांशी ने 1868 में किया था।"
TEACHING INTENT: INTRODUCTION + KEYWORD
VISUAL DECISION: one small keyword card, not pictures of torches.
WHAT APPEARS: **लेक्लांशी सेल के सिद्धान्त पर — जी. लेक्लांशी, 1868**
WHY: the uses are conversational framing and their appearance teaches nothing —
a photo of a torch is exactly the decoration rule. The inventor and year are a
discrete written fact worth one line.
LAYOUT: single line, upper-centre, modest size.
AVATAR: MODE A — large; this is still framing.
PERSISTENCE: ~6s, then clears.
IMPLEMENTATION: MANIM (text)

---

# SCENE 02
TIME: 00:35 – 01:02
NARRATION: "शुष्क सेल में जिंक का एक खोखला आवरण होता है… यही जिंक का आवरण ऐनोड का काम करता है।" → "…MnO₂ और कार्बन चूर्ण का काला पेस्ट भरा होता है।"
TEACHING INTENT: APPARATUS + DIAGRAM_EXPLANATION — **the spine**
VISUAL DECISION: build the cross-section from the outside in, exactly in the
order he names the layers.
VISUAL TYPE: Manim (traced figure + anchored labels)
WHAT APPEARS:
  - 00:35 outer zinc casing, hollow, label **Zn आवरण (ऐनोड)**
  - 00:42 the paste inside it, label **NH₄Cl + ZnCl₂ पेस्ट**
  - 00:52 carbon rod down the centre, label **कार्बन छड़ (कैथोड)**
  - 00:57 black paste around the rod, label **MnO₂ + कार्बन चूर्ण**
ANIMATION: each layer fades in on its sentence and stays. Labels attach to their
layer BY NAME through the anchor table, sitting ON or beside their own layer with
a short leader — never floating loose beside the figure.
LAYOUT: **graphic-dominant.** The cross-section is the largest object in the
video: full width of the primary visual area, tall enough that all four labels
are comfortably readable on a phone. Labels alternate left/right so they never
collide.
AVATAR: **MODE C** — chest-height, bottom-centre. One eased change on entry.
COLOURS: each layer a distinct neutral; the layer just named in accent, earlier
layers quiet.
PERSISTENCE: **the cross-section stays from 00:35 to 02:17** — the whole
structural and working section. Never regenerated.
IMPLEMENTATION: MANIM

---

# SCENE 03
TIME: 01:02 – 01:37
NARRATION: "एग्ज़ाम में शुष्क सेल का चित्र बनाते समय ये चार चीज़ें बिल्कुल मत भूलना। सबसे पहले, Zn का बाहरी आवरण… दूसरा… तीसरा… और चौथा…"
TEACHING INTENT: MEMORY_CUE + LIST — the four things the diagram must carry
VISUAL DECISION: do NOT build a separate list. Number the four parts ON the
diagram that is already there.
WHAT APPEARS: numbered markers ① ② ③ ④ appear on the four layers as he counts
them, each with its exam-ready caption:
  - 01:08 ① **Zn आवरण — ऐनोड**
  - 01:13 ② **NH₄Cl + ZnCl₂ — विद्युत्-अपघट्य**
  - 01:18 ③ **कार्बन छड़ — कैथोड**
  - 01:22 ④ **MnO₂ + कार्बन चूर्ण**
ANIMATION: each marker pops on its layer and that layer brightens; the previous
one quietens but stays labelled.
WHY: he is telling them what to draw and label in the exam. Putting the numbers
on the drawing means the student memorises the placement, not a detached list.
This is also the anti-frozen answer — four changes across 35 seconds.
AVATAR: MODE C, unchanged. **No resize** through the whole sequence.
PERSISTENCE: all four numbers and labels remain.
IMPLEMENTATION: MANIM

---

# SCENE 04
TIME: 01:37 – 01:46
NARRATION: "क्योंकि प्रश्न में साफ़ लिखा है सचित्र वर्णन, इसीलिए परीक्षा में चित्र ज़रूर बनाना, सिर्फ़ लिख कर मत छोड़ना।"
TEACHING INTENT: WARNING
VISUAL DECISION: keep the diagram, add nothing but emphasis.
WHAT APPEARS: the complete labelled figure pulses once as a whole.
AVATAR: MODE C, unchanged.
IMPLEMENTATION: MANIM (state change)

---

# SCENE 05
TIME: 01:56 – 02:17
NARRATION: "जब सेल काम करता है, तो जिंक इलेक्ट्रॉन खोकर, Zn²⁺ आयन के रूप में विद्युत्-अपघट्य में चला जाता है… इसलिए जिंक ऐनोड है, और ये इलेक्ट्रॉन बाहरी परिपथ से कार्बन की छड़ की ओर जाते हैं।"
TEACHING INTENT: PROCESS + CAUSE_EFFECT — **the mechanism**
VISUAL DECISION: animate it on the existing diagram. He says eighty students in
a hundred get this wrong, which is precisely the case for showing rather than
telling.
WHAT APPEARS:
  - 01:56 electrons leave the zinc wall: small **e⁻** marks detach from the Zn
    layer; a **Zn²⁺** label moves from the wall into the paste
  - 02:03 the zinc layer is marked **ऑक्सीकरण** and **ऐनोड (−)**
  - 02:11 **e⁻** marks travel OUT of the zinc, along an external circuit line
    drawn over the top of the cell, and INTO the carbon rod, which is marked
    **कैथोड (+)**
ANIMATION: electrons move continuously along the external path over ~3s.
**DIRECTION CHECK — critical:** electrons LEAVE the zinc and travel to the
carbon rod. Zn is the anode and is negative in a galvanic cell. Reversed, this
teaches the opposite of the answer.
LAYOUT: the external circuit line arcs above the cell, inside the visual area,
never crossing into the caption band.
AVATAR: MODE C, unchanged.
COLOURS: electrons in a single bright accent so the eye follows one thing.
PERSISTENCE: the anode/cathode labels stay; the moving electrons loop quietly.
IMPLEMENTATION: MANIM

---

# PART 2

# SCENE 06
TIME: 00:10 – 00:27
NARRATION: "जिंक से निकले इलेक्ट्रॉन बाहरी परिपथ से कार्बन की छड़ तक पहुँचते हैं। यहाँ दो NH₄⁺ आयन, दो MnO₂ और ऐनोड से आने वाले दो इलेक्ट्रॉन आपस में मिलते हैं, इसके परिणामस्वरूप Mn₂O₃, H₂O और NH₃ बनते हैं।"
TEACHING INTENT: FORMULA + PROCESS
VISUAL DECISION: the cathode half-reaction, built as it is spoken.
WHAT APPEARS: heading **कैथोड पर अपचयन**, then the equation assembled in three
beats — reactants as he names them, arrow, then products:
  **2NH₄⁺ + 2MnO₂ + 2e⁻ → Mn₂O₃ + H₂O + 2NH₃**
ANIMATION: reactants fade in one group at a time on their own phrase; the arrow
draws; products appear together.
LAYOUT: equation LARGE, upper-centre. If it exceeds the width it **splits at the
arrow** — reactants on line one, products on line two — rather than shrinking.
AVATAR: MODE B — the equation needs less height than the diagram did.
COLOURS: equation neutral, boxed in accent.
PERSISTENCE: holds through the next scene, which annotates it.
IMPLEMENTATION: MANIM

---

# SCENE 07
TIME: 00:27 – 00:41
NARRATION: "MnO₂ में मैंगनीज की ऑक्सीकरण अवस्था प्लस फोर होती है, जो घट कर Mn₂O₃ में प्लस थ्री हो जाती है। इसका मतलब है कि कैथोड पर मैंगनीज की कमी हो रही है।"
TEACHING INTENT: CONCEPT_EXPLANATION
VISUAL DECISION: annotate the equation already on screen.
WHAT APPEARS: **+4** appears above the Mn in MnO₂, **+3** above the Mn in Mn₂O₃,
and a short arrow between them labelled **अपचयन**.
ANIMATION: the two oxidation numbers fade in on their phrases; the arrow draws
between them as he says the state falls.
WHY: the oxidation-state change is the reason this is reduction; showing it on
the equation makes the claim checkable rather than asserted.
AVATAR: MODE B, unchanged.
PERSISTENCE: annotations stay while the equation does.
IMPLEMENTATION: MANIM

---

# SCENE 08
TIME: 00:41 – 01:07
NARRATION: "जब ऐनोड पर होने वाली अभिक्रिया और कैथोड पर होने वाली इस अभिक्रिया को आपस में जोड़ते हैं… यानी पूरी अभिक्रिया में Zn इलेक्ट्रॉन देता है और उसका ऑक्सीकरण होता है, जबकि MnO₂ इलेक्ट्रॉन ग्रहण करके रिडक्शन करता है।"
TEACHING INTENT: DERIVATION (adding half-reactions) + COMPARISON
VISUAL DECISION: show the addition happening — anode above, cathode below, rule,
sum. The student must be able to reproduce this.
WHAT APPEARS:
  - **ऐनोड:** Zn → Zn²⁺ + 2e⁻
  - **कैथोड:** 2NH₄⁺ + 2MnO₂ + 2e⁻ → Mn₂O₃ + H₂O + 2NH₃
  - a horizontal rule
  - **पूर्ण:** Zn + 2NH₄⁺ + 2MnO₂ → Zn²⁺ + Mn₂O₃ + H₂O + 2NH₃
ANIMATION: the cathode equation already on screen slides up to make room; the
anode equation appears above it; the electrons on both sides flash and cancel;
the rule draws; the overall equation writes underneath.
**Every step must follow:** the 2e⁻ visibly cancels — that is why it disappears.
LAYOUT: vertical stack — a sum needs vertical stacking. Each line splits at the
arrow if needed.
AVATAR: **MODE C** — three stacked equations need the height.
COLOURS: Zn in the oxidation accent, MnO₂ in the reduction accent, carried from
the diagram.
PERSISTENCE: the overall equation holds; the half-reactions quieten.
IMPLEMENTATION: MANIM

---

# SCENE 09
TIME: 01:26 – 01:52
NARRATION: "ये ऐनोड पर बनने वाले Zn²⁺ आयनों के साथ अभिक्रिया करके एक जटिल आयन बनाती है। यानी एक Zn²⁺ आयन और चार NH₃ अणु आपस में मिलकर बनाते हैं… इसलिए अमोनिया गैस के बाहर निकलने की समस्या नहीं होती"
TEACHING INTENT: CONCEPT_EXPLANATION + COMMON_MISTAKE (he says this point is
usually missed)
VISUAL DECISION: the complex-ion equation plus its consequence.
WHAT APPEARS:
  - **Zn²⁺ + 4NH₃ → [Zn(NH₃)₄]²⁺**
  - beneath it, a two-link consequence: **NH₃ बँध गई → गैस नहीं निकलती → दाब नहीं बढ़ता**
ANIMATION: equation assembles; then the consequence chain draws left to right.
WHY: he explicitly flags this as the thing students forget after writing the
reactions — so it gets its own screen, not a footnote.
LAYOUT: equation upper-centre, consequence chain below it, horizontal.
AVATAR: MODE B.
PERSISTENCE: holds ~20s.
IMPLEMENTATION: MANIM

---

# SCENE 10
TIME: 02:00 – 02:10
NARRATION: "शुष्क सेल का वोल्टेज लगभग वन पॉइंट टू फाइव वोल्ट से वन पॉइंट फाइव वोल्ट होता है। इसे भी आंसर में ज़रूर लिखना।"
TEACHING INTENT: KEYWORD + MEMORY_CUE
VISUAL DECISION: one number, large.
WHAT APPEARS: **E_cell ≈ 1.25 – 1.5 V**
WHY: a single exam-scoring fact. It needs a screen of its own and nothing else.
LAYOUT: centred, large, boxed.
AVATAR: MODE B.
PERSISTENCE: ~8s.
IMPLEMENTATION: MANIM

---

# SCENE 11
TIME: 02:10 – 02:37
NARRATION: "पुराने शुष्क सेल में एक कमी थी। NH₄Cl की अम्लीय प्रकृति के कारण जिंक के पात्र का संक्षारण होने लगता है और उसमें छेद हो जाते हैं… इसी समस्या से बचने के लिए आजकल रिसाव-रोधी शुष्क सेल बनाए जाते हैं। इनमें NH₄Cl के स्थान पर KOH का उपयोग किया जाता है"
TEACHING INTENT: CAUSE_EFFECT + COMPARISON
VISUAL DECISION: a two-column comparison — the defect and the fix, aligned.
WHAT APPEARS:
  | **पुराना शुष्क सेल** | **रिसाव-रोधी सेल** |
  | NH₄Cl (अम्लीय) | KOH (क्षारीय) |
  | Zn पात्र का संक्षारण | संक्षारण नहीं |
  | छेद → रिसाव | रिसाव नहीं |
ANIMATION: the left column fills first as he describes the problem, then the
right column fills row by row as he gives the fix, each new right-hand cell
appearing opposite the problem it solves.
WHY: a defect and its remedy are a comparison; aligned rows mean the student
never has to search for which fix answers which problem.
LAYOUT: two columns, full width — a comparison needs horizontal room.
AVATAR: MODE B — low, so the table sits above him.
COLOURS: left column in the warning tone, right column in the positive tone.
PERSISTENCE: the completed table holds to the end of the teaching section.
IMPLEMENTATION: MANIM

---

# SCENE 12
TIME: from "…आपकी स्क्रीन पर आ जाएगा"
VISUAL DECISION: answer-page template on the cue. Not planned here.
IMPLEMENTATION: TEMPLATE

---

# FINAL SCENE SUMMARY

**Manim**
- **the dry-cell cross-section**, traced from the textbook scan (REUSE), built
  layer by layer, numbered ①–④ on the layers, persisting 00:35 → 02:17 in part 1
- electron-flow animation: e⁻ leaving Zn, along an external circuit, into the
  carbon rod
- cathode half-reaction with oxidation numbers annotated (+4 → +3)
- half-reaction addition with 2e⁻ visibly cancelling → overall equation
- complex-ion equation + consequence chain
- E_cell ≈ 1.25–1.5 V card
- old-cell vs leak-proof comparison table

**Images**
- none. Every object is a schematic section or an equation.

**No visual**
- part 1: 00:00–00:16 (hook), 01:46–01:56 (transition), 02:17–02:23
- part 2: 00:00–00:10 (recap)

**Reusable**
- the cross-section persists for ~100 seconds of part 1 and is never rebuilt
- the oxidation/reduction accent colours carry from the diagram into every
  equation, so Zn and MnO₂ keep their identity across the whole video

**New assets**
- none requiring generation. No image cost.

**NOTE — batch 1 defect this fixes:** the diagram was rendered small under an
oversized presenter. Here the cross-section is graphic-dominant and the presenter
is MODE C for the entire structural section.
