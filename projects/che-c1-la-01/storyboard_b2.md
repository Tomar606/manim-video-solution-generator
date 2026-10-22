# बर्कले एवं हार्टले विधि — परासरण दाब मापन

## GLOBAL VISUAL STRATEGY

**Teaching objective:** the student must describe the apparatus and the
measuring procedure in order, and list four advantages. The question is
*संक्षिप्त वर्णन कीजिए तथा लाभ बताइये* — a description of a physical apparatus,
so the APPARATUS IS THE SPINE and everything else hangs off it.

**Key concepts:** two concentric tubes; the inner one porous, carrying a copper
ferrocyanide semipermeable membrane; capillary at one end, stopcock funnel at
the other; gun-metal outer tube with a watertight piston. Then the procedure:
water in, solution out, osmosis pulls water OUT of the inner tube toward the
solution, capillary level FALLS, piston pressure restores it, and the pressure
that restores it IS the osmotic pressure.

**Visual language:** one traced apparatus figure that is built up label by label
and then ANIMATED. Nothing is replaced; the figure persists for 95 seconds and
only the highlight, the labels and the moving water change.

**Main visual assets:** the traced Berkeley–Hartley apparatus (already exists as
scan_figure, from the textbook scan — do not redraw); water-column animation;
π = P_applied result card; four-item advantages list.

**Avatar strategy:** MODE A for the hook and the exam framing (nothing to teach).
MODE C for the whole apparatus and procedure section — the diagram is the
subject, presenter chest-height at the bottom. MODE B for the advantages list.
Two size changes in part 1, one in part 2. No other movement.

---

# SCENE 01
TIME: 00:20 – 00:31
NARRATION: "सबसे पहले समझते हैं, बर्कले एवं हार्टले की विधि में परासरण दाब कैसे मापा जाता है… यहाँ से ध्यान से सुनना"
TEACHING INTENT: TRANSITION + WARNING
VISUAL DECISION: **VISUAL: NONE**
WHY: he is announcing what is coming and telling them to pay attention. No
object is being described. A graphic here would be decoration, and this is
exactly where batch 1 put a photograph of a membrane.
AVATAR: MODE A — presenter large, occupying the frame, anchored bottom-centre.
CAPTIONS: normal.
IMPLEMENTATION: NONE

---

# SCENE 02
TIME: 00:31 – 01:10
NARRATION: "इस विधि के उपकरण में दो समकेंद्रीय नलियाँ होती हैं…" through "…जिसकी मदद से विलयन पर दाब डाला जाता है।"
TEACHING INTENT: APPARATUS + DIAGRAM_EXPLANATION
VISUAL DECISION: the traced apparatus, assembled part by part as each part is
named. This single figure carries the next 95 seconds.
VISUAL TYPE: Manim (traced figure + labels)
WHY: the exam answer is a labelled diagram plus a description. Building it as he
names each part means the student sees the same order they must write.
WHAT APPEARS — each element arrives ON the sentence that names it:
  - 00:31 two concentric tubes, drawn as outline only
  - 00:34 inner tube shaded to read as porous, label **भीतरी नली (संरंध्र)**
  - 00:37 membrane drawn on the inner tube wall, label
          **कॉपर फेरोसायनाइड अर्धपारगम्य झिल्ली**
  - 00:51 capillary tube at one end, label **केशिका नली**
  - 00:53 stopcock funnel at the other, label **टोंटीदार कीप**
  - 00:57 outer tube closes around it, label **गन मेटल बाहरी नली**
  - 01:02 piston in the outer tube, label **जलरोधक पिस्टन**
ANIMATION: each part fades in over ~0.4s and stays. Labels attach to the part BY
NAME through the anchor table so they survive rescaling — never floating beside
the figure.
LAYOUT: figure centred in the primary visual area, full-width, sized so the
smallest label is legible on a phone. Labels outside the figure's silhouette,
connected by short leader lines.
AVATAR: MODE C — chest-height, bottom-centre, well clear of the figure.
COLOURS: figure neutral ink; the part just named in accent; earlier parts quiet.
PERSISTENCE: **the figure stays until 02:00.** It is not cleared between scenes.
TRANSITION: none — the next scene evolves this figure.
IMPLEMENTATION: MANIM

---

# SCENE 03
TIME: 00:44 – 00:51
NARRATION: "अब इस बात को याद रखना — अर्धपारगम्य झिल्ली इस विधि का बहुत महत्वपूर्ण हिस्सा है।"
TEACHING INTENT: KEYWORD + MEMORY_CUE
VISUAL DECISION: highlight, not a new visual.
WHAT APPEARS: the membrane already on the figure pulses to accent and its label
brightens. Everything else dims slightly.
WHY: he is flagging one existing part as important. Replacing the screen would
throw away the diagram he just built.
AVATAR: unchanged (MODE C). **No resize** — this is the "do not resize for a
keyword" case.
PERSISTENCE: highlight decays after ~3s; figure unchanged.
IMPLEMENTATION: MANIM (highlight on the existing object)

---

# SCENE 04
TIME: 01:14 – 01:23
NARRATION: "सबसे पहले भीतरी नली में आसुत जल भरते हैं, और जल का स्तर केशिका नली में एक निश्चित निशान तक रखते हैं।"
TEACHING INTENT: PROCESS step 1
VISUAL DECISION: fill the existing figure.
WHAT APPEARS: water fills the inner tube; the capillary column rises to a marked
level; a horizontal reference line with the label **प्रारम्भिक निशान** is drawn
at that level and STAYS — the whole method is defined against this mark.
ANIMATION: fill rises over ~1.2s, then the mark line draws.
COLOURS: water in a cool accent, distinct from the solution colour used next.
AVATAR: MODE C, unchanged.
PERSISTENCE: mark line persists to 02:00.
IMPLEMENTATION: MANIM

---

# SCENE 05
TIME: 01:23 – 01:29
NARRATION: "इसके बाद बाहरी नली में वह विलयन भरते हैं, जिसका परासरण दाब ज्ञात करना है।"
TEACHING INTENT: PROCESS step 2
WHAT APPEARS: the outer tube fills with solution, in a visibly different colour
from the water. Label **विलयन**.
WHY: the two liquids must be told apart at a glance, because the next scene is
about which way water moves between them.
AVATAR: MODE C, unchanged.
IMPLEMENTATION: MANIM

---

# SCENE 06
TIME: 01:29 – 01:38
NARRATION: "अब परासरण के कारण जल अर्धपारगम्य झिल्ली से होकर विलयन की ओर जाने लगता है। इस वजह से केशिका नली में जल का स्तर नीचे आने लगता है।"
TEACHING INTENT: PROCESS + CAUSE_EFFECT — **the mechanism**
VISUAL DECISION: animate it. This is the one moment where the direction of
movement IS the physics.
WHAT APPEARS:
  - small water-molecule marks cross the membrane **from the inner tube OUT into
    the solution** — water leaves the water side and joins the solution
  - simultaneously the capillary column **FALLS** below the mark
  - a short arrow labelled **परासरण** points from water to solution
ANIMATION: molecules cross over ~2s, staggered; the column falls in the same
2s so cause and effect are visibly linked; the gap between the falling level and
the mark line is left visible.
**DIRECTION CHECK — this is the mechanically critical one:** water moves INTO
the solution and the capillary level FALLS. Reversed, this teaches the opposite
of the answer and looks entirely convincing.
COLOURS: moving water in the water colour so the eye tracks where it goes.
AVATAR: MODE C, unchanged.
PERSISTENCE: the fallen level and the mark both stay — the discrepancy is the
thing the next step cancels.
IMPLEMENTATION: MANIM

---

# SCENE 07
TIME: 01:43 – 01:52
NARRATION: "अब पिस्टन की सहायता से विलयन पर दाब डालते हैं और केशिका नली में जल के स्तर को वापस पहले वाले निशान पर स्थिर कर देते हैं।"
TEACHING INTENT: PROCESS step 4 — the measurement itself
WHAT APPEARS: the piston moves in; a force arrow labelled **P** appears on it;
the capillary column **rises back to the mark line** and stops exactly there.
ANIMATION: piston travel and column rise happen together over ~1.5s. The column
settles ON the mark and a brief accent flash confirms the match.
WHY: the entire method is "push until the level returns" — the student should
see the level land back on the same line they saw drawn in scene 04.
AVATAR: MODE C, unchanged.
IMPLEMENTATION: MANIM

---

# SCENE 08
TIME: 01:52 – 02:00
NARRATION: "जब यह स्थायी स्थिति आ जाती है, तब पिस्टन द्वारा लगाया गया दाब ही उस विलयन का परासरण दाब होता है।"
TEACHING INTENT: FORMULA + CONCLUSION
VISUAL DECISION: the result, stated on the figure that produced it.
WHAT APPEARS: a single boxed line in the primary area above the figure:
  **π = P_applied**   (LaTeX: `\pi = P_{\text{applied}}`)
with a short caption **साम्य पर — कोई निवल प्रवाह नहीं**.
ANIMATION: the piston's **P** arrow transforms into the **P** in the equation —
so the symbol is visibly the same quantity, not a new one.
LAYOUT: equation upper-centre of the visual area, LARGE; figure stays below it,
scaled down slightly to make room. No overlap with captions or presenter.
COLOURS: equation in accent, boxed.
PERSISTENCE: both hold to the end of the part.
IMPLEMENTATION: MANIM

---

# SCENE 09
TIME: 02:00 – 02:10 (end of part 1)
NARRATION: "तो बच्चों, अब तक हमने बर्कले और हार्टले विधि को समझ लिया… ये समझेंगे अगले पार्ट में।"
TEACHING INTENT: RECAP + TRANSITION
VISUAL DECISION: **VISUAL: NONE** — clear the figure, return the presenter.
WHY: he is closing the part and pointing forward. Holding the diagram here is
the FROZEN-screen failure; nothing is being taught against it any more.
AVATAR: MODE A — presenter grows back to full frame, eased, single change.
IMPLEMENTATION: NONE

---

# PART 2

# SCENE 10
TIME: 00:00 – 00:18
NARRATION: "बच्चों, पार्ट एक में हमने समझाया… क्योंकि परीक्षा में विधि के साथ ये लाभ लिखना भी जरूरी है।"
TEACHING INTENT: RECAP + EXAM FRAMING
VISUAL DECISION: **VISUAL: NONE**
WHY: recap and exam framing. Batch 1 put the apparatus photograph here, over the
words "परीक्षा में विधि के साथ ये लाभ लिखना भी जरूरी है" — a picture with
nothing to do with the sentence.
AVATAR: MODE A — presenter large.
IMPLEMENTATION: NONE

---

# SCENE 11
TIME: 00:18 – 01:06
NARRATION: the four advantages, from "इस विधि का पहला लाभ" to "…उसका मापन किया जा सकता है।"
TEACHING INTENT: LIST + ADVANTAGES
VISUAL DECISION: a four-item list that FILLS IN. The heading appears first, so
the student knows four are coming and can leave room in their answer.
VISUAL TYPE: Manim progressive list
WHAT APPEARS:
  - 00:18 heading **विधि के चार लाभ**, and four empty numbered slots ① ② ③ ④
  - 00:19 ① **कम समय लगता है**
  - 00:28 ② **सांद्रता बदलने पर भी सही परिणाम**
  - 00:40 ③ **झिल्ली अधिक दाब पर टूटती नहीं**
  - 00:53 ④ **अधिक परासरण दाब वाले विलयन भी मापे जा सकते हैं**
ANIMATION: each item fades to full on its sentence; earlier items drop to a
quieter tone but **remain fully legible**. Every item's state is set explicitly
from its own reveal time — the conditional-dimming rule is what made item ①
disappear in batch 1.
LAYOUT: list left-aligned, centred block, in the primary visual area. Four short
lines at a readable size; the wording above is the SCREEN wording, deliberately
shorter than the spoken sentence — the screen organises, the caption says.
AVATAR: MODE B — moderate graphic, presenter reduced and low, bottom-centre.
One size change entering this scene.
COLOURS: current item accent, earlier items neutral-quiet, heading brand accent.
PERSISTENCE: **all four stay on screen** through 01:06 — the completed list is
the thing the student copies.
IMPLEMENTATION: MANIM

---

# SCENE 12
TIME: 01:06 – 01:11
NARRATION: "बच्चों, बस इतना याद लिए तो परीक्षा में बर्कले और हार्टले की विधि कभी नहीं भूलोगे।"
TEACHING INTENT: MEMORY_CUE
VISUAL DECISION: keep the completed list, brighten all four equally.
WHY: he is telling them this is the set to remember; showing the whole set at
once is exactly right here. No new object.
AVATAR: MODE B, unchanged.
PERSISTENCE: list holds.
IMPLEMENTATION: MANIM (state change only)

---

# SCENE 13
TIME: 01:11 onward
NARRATION: "अब इसे परीक्षा में कैसे लिखना है? इसका पूरा उत्तर आपकी स्क्रीन पर आ जाएगा…"
TEACHING INTENT: (template)
VISUAL DECISION: hand over to the existing answer-page template on the cue
"स्क्रीन पर आ जाएगा". Not planned here.
AVATAR: per template.
IMPLEMENTATION: TEMPLATE

---

# FINAL SCENE SUMMARY

**Manim**
- Berkeley–Hartley apparatus, traced from the textbook scan (REUSE — exists)
- seven part labels, anchored by name
- water fill + capillary column with a persistent mark line
- osmosis animation: water crossing the membrane INTO the solution, level FALLING
- piston pressure animation: level returning to the mark
- π = P_applied result card, transformed out of the piston's P arrow
- four-item progressive advantages list

**Images**
- none. Every object here is a schematic apparatus, which Manim renders more
  accurately than a generated photograph, and no real-world appearance matters.

**Text**
- part labels, the mark label, the advantages list wording

**No visual**
- part 1: 00:00–00:31 (hook, framing), 02:00–02:10 (recap/transition)
- part 2: 00:00–00:18 (recap, exam framing)

**Reusable across scenes**
- the apparatus figure persists 00:31 → 02:00 in part 1. Built once, filled,
  animated, annotated. Never regenerated.

**New assets**
- none requiring generation. No image cost.
