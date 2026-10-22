# संक्रमण तत्वों के गुण — चार गुण, चार कारण

## GLOBAL VISUAL STRATEGY

**Teaching objective:** four numbered properties, each with its REASON. He says
it outright at the end: *"इन चारों गुणों के पीछे का कारण मत भूलना"*. So every
property scene must show property AND cause together — a property alone is half
the answer.

**Key concepts:** the general configuration (n−1)d¹⁻¹⁰ns¹⁻² is the ROOT — all
four properties are consequences of it, and he says so at 00:41. Then:
(1) variable oxidation states, because ns and (n−1)d energies are close;
(2) ionisation enthalpy intermediate and rising left→right, with the Zn/Cd/Hg
exception; (3) radius decreasing but nearly constant Cr→Cu, because nuclear
charge and d-shielding balance; (4) metallic character.

**Visual language:** a **four-slot progress spine** down one side, one slot per
property, lit as each is taught and ticked when finished. The student always
knows which of the four they are in, across three parts. Each property gets a
**property → कारण** pair, never a bare statement.

**Main visual assets:** the configuration card; the 4-slot spine; four
property/cause pairs; the Mn oxidation-state row; the two-opposing-effects
balance for radius; the final four-point recap.

**Avatar strategy:** MODE A over hooks and transitions; MODE B for
property/cause pairs; MODE C for the oxidation-state row and the balance figure.

**BATCH-1 DEFECT THIS FIXES:** part 3's list lost item ①. Every list item's state
here is set explicitly from its own reveal time — revealed items stay revealed.

---

# SCENE 01
TIME: 00:21 – 00:45
NARRATION: "सबसे पहले याद रखो, सामान्य इलेक्ट्रॉनिक विन्यास… संक्रमण तत्वों में d कक्षक में 1-10 और s कक्षक में 1-2 इलेक्ट्रॉन होते हैं… अब इसी विन्यास से संक्रमण तत्वों के ये चारों गुण समझ में आएंगे।"
TEACHING INTENT: DEFINITION + KEYWORD — **the root**
VISUAL DECISION: the configuration, large and alone, then the four slots
branching from it — because he says explicitly that all four follow from it.
WHAT APPEARS:
  - 00:23 heading **सामान्य इलेक्ट्रॉनिक विन्यास**
  - 00:32 **(n−1)d¹⁻¹⁰ ns¹⁻²** — LARGE, boxed
  - 00:41 four empty numbered slots fan out below it: ① ② ③ ④
ANIMATION: the configuration writes; then four connector lines draw down to four
empty slots, as he says "इसी विन्यास से… ये चारों गुण".
WHY: this makes the structure of the whole answer visible in one image — one
cause, four consequences — instead of four unrelated facts.
LAYOUT: configuration upper-centre and large; the four slots beneath it, compact.
AVATAR: MODE B.
COLOURS: configuration in brand accent; slots neutral and dim until taught.
PERSISTENCE: **the four-slot spine persists across all three parts**, sitting
small at the side with the current slot lit.
IMPLEMENTATION: MANIM

---

# SCENE 02
TIME: 00:45 – 01:09
NARRATION: "चलो पहला गुण समझते हैं — ऑक्सीकरण अवस्था। …मुख्य कारण है कि (n−1)d और ns कक्षकों की ऊर्जाओं में बहुत अधिक अंतर नहीं होता। इसलिए, बन्ध बनाने में केवल ns के इलेक्ट्रॉन ही नहीं, बल्कि d-इलेक्ट्रॉन भी भाग ले सकते हैं।"
TEACHING INTENT: CONCEPT_EXPLANATION + CAUSE_EFFECT
VISUAL DECISION: slot ① lights; show the property with its cause as a two-step
chain — and draw the cause, because "energies are close" is a spatial fact.
WHAT APPEARS:
  - slot ① lights: **① ऑक्सीकरण अवस्था**
  - a small energy-level sketch: two levels, **ns** and **(n−1)d**, drawn
    CLOSE TOGETHER, with the small gap marked **ऊर्जा अंतर कम**
  - then the consequence: **दोनों के इलेक्ट्रॉन बन्ध में भाग लेते हैं**
  - then: **→ कई ऑक्सीकरण अवस्थाएँ**
ANIMATION: the two levels draw with the gap visibly small; electrons on both
levels flash as he says both take part; the consequence lines write in order.
WHY: the cause is that two energies are close — that is a picture, not a
sentence. Drawing the small gap is what makes the reason land.
LAYOUT: energy sketch left, consequence chain right — a cause and its effect
read left to right.
AVATAR: MODE B.
PERSISTENCE: holds ~24s.
IMPLEMENTATION: MANIM

---

# SCENE 03
TIME: 01:09 – 01:35
NARRATION: "अब यहाँ एक बहुत आम गलती होती है… Mn को सिर्फ +2 या +3 वाला मत समझ लेना। 3d श्रेणी में Mn की उच्चतम ऑक्सीकरण अवस्था +7 होती है, क्योंकि Mn में सबसे अधिक अयुग्मित d इलेक्ट्रॉन होते हैं। उच्चतम ऑक्सीकरण अवस्थाएँ — +2, +3, +4, +5, +6, और +7।"
TEACHING INTENT: COMMON_MISTAKE + LIST
VISUAL DECISION: a wrong/right correction, then the run of states filling in.
WHAT APPEARS:
  - a correction pair: **✗ Mn = केवल +2, +3**  /  **✓ Mn की उच्चतम अवस्था = +7**
  - the reason beneath: **सबसे अधिक अयुग्मित d इलेक्ट्रॉन**
  - then a horizontal run of states filling one at a time as he counts:
    **+2 +3 +4 +5 +6 +7**, with **+7** landing in accent
ANIMATION: the ✗ line appears and is struck through; the ✓ line writes beneath
it. Then the six states fill left to right in time with his counting.
WHY: he flags this as the mistake almost everyone makes. A struck-through wrong
answer beside the right one is unmistakable; a bare correct statement is not.
LAYOUT: correction pair upper area; the state run below it, full width.
AVATAR: **MODE C** — the run of six states needs the width.
COLOURS: ✗ in the warning tone, ✓ in the positive tone, +7 in brand accent.
IMPLEMENTATION: MANIM

---

# SCENE 04
TIME: 01:35 – 01:40
NARRATION: "इसके बाद, Fe से Zn तक उच्च ऑक्सीकरण अवस्थाओं की प्रवृत्ति घटने लगती हैं।"
TEACHING INTENT: SEQUENCE
VISUAL DECISION: mark the trend on the run already on screen.
WHAT APPEARS: a downward arrow drawn across the right-hand end of the series,
labelled **Fe → Zn : प्रवृत्ति घटती है**.
AVATAR: MODE C, unchanged. No resize.
PERSISTENCE: then slot ① is ticked as the part ends.
IMPLEMENTATION: MANIM

---

# PART 2

# SCENE 05
TIME: 00:14 – 00:30
NARRATION: "संक्रमण तत्वों की आयनीकरण एन्थैल्पी S ब्लॉक और P ब्लॉक के बीच की होती है और एक श्रेणी में बाएँ से दाएँ जाने पर सामान्यतः बढ़ती है, क्योंकि नाभिक का आकर्षण बढ़ता है और परमाणु का आकार छोटा होता जाता है।"
TEACHING INTENT: CONCEPT_EXPLANATION + CAUSE_EFFECT
VISUAL DECISION: slot ② lights. Show "between s and p" as an actual position,
and the trend as a direction.
WHAT APPEARS:
  - slot ② lights: **② आयनीकरण एन्थैल्पी**
  - a three-band strip: **s ब्लॉक — निम्न** | **संक्रमण — मध्यम** | **p ब्लॉक — उच्च**,
    with the middle band in accent
  - then a left→right arrow labelled **बाएँ → दाएँ : बढ़ती है**
  - two causes beneath it: **नाभिकीय आकर्षण ↑** and **आकार ↓**
ANIMATION: the strip appears, middle band lights; the trend arrow draws
left→right; the two causes write.
WHY: "between s and p" is a position — a strip shows it instantly. The two causes
are stated as a pair because he gives them as a pair.
LAYOUT: strip full width; causes beneath, side by side.
AVATAR: MODE B.
IMPLEMENTATION: MANIM

---

# SCENE 06
TIME: 00:30 – 00:51
NARRATION: "अब एक अपवाद है, इसे ध्यान से सुनना — यही परीक्षा में पूछ लेते हैं। जिंक, कैडमियम और मरकरी की आयनीकरण एन्थैल्पी अपेक्षाकृत अधिक होती है, क्योंकि इनका विन्यास है n माइनस वन d टेन ns टू। यानी d उपकोश पूरी तरह भरी हुई और इलेक्ट्रॉन युग्मित होते हैं।"
TEACHING INTENT: WARNING + CAUSE_EFFECT — the exception
VISUAL DECISION: mark it as an exception visually, and show the configuration
that causes it.
WHAT APPEARS:
  - a callout marked **अपवाद**: **Zn, Cd, Hg — अपेक्षाकृत अधिक**
  - the reason as configuration: **(n−1)d¹⁰ ns²**
  - beneath: **d पूर्ण भरी + इलेक्ट्रॉन युग्मित → अधिक स्थायी → अधिक ऊर्जा चाहिए**
ANIMATION: the callout appears with the exception marker; the configuration
writes; the consequence chain draws.
WHY: he says this exact exception gets asked in the exam. Giving it its own
marked callout is how the student registers it as separate from the general trend.
LAYOUT: callout to one side of the trend strip, which stays visible — the
exception must be seen AGAINST the rule.
COLOURS: exception in the warning tone against the general trend's neutral.
AVATAR: MODE B, unchanged.
IMPLEMENTATION: MANIM

---

# SCENE 07
TIME: 00:51 – 01:02
NARRATION: "चलो अब तीसरा गुण — परमाणु त्रिज्या और आयनिक आकार। 3d श्रेणी में बाएँ से दाएँ जाने पर आकार सामान्यतः घटता है, क्योंकि प्रभावी नाभिकीय आवेश बढ़ता जाता है।"
TEACHING INTENT: CONCEPT_EXPLANATION
VISUAL DECISION: slot ③ lights; show size as SIZE — a row of circles that shrink.
WHAT APPEARS:
  - slot ③ lights: **③ परमाणु त्रिज्या**
  - a row of circles across the 3d series, each slightly smaller than the last,
    left to right
  - label: **प्रभावी नाभिकीय आवेश ↑ → आकार ↓**
ANIMATION: the circles appear left to right, visibly diminishing.
WHY: radius is a size. Drawing it as sizes means the student sees the trend
rather than reading about it.
AVATAR: **MODE C** — a row across the series needs the width.
IMPLEMENTATION: MANIM

---

# SCENE 08
TIME: 01:02 – 01:34
NARRATION: "लेकिन बच्चों, यहाँ एक और बात है — इसे छोड़ दिया तो आंसर अधूरा लगेगा… तो एक तरफ नाभिकीय आवेश आकार घटा रहा है, दूसरी तरफ d इलेक्ट्रॉनों का परिरक्षण प्रभाव उसे बढ़ाने की कोशिश कर रहा है। दोनों प्रभाव काफी हद तक एक दूसरे को संतुलित कर देते हैं। इसीलिए क्रोमियम से कॉपर तक परमाणु त्रिज्या में बहुत कम और लगभग समान परिवर्तन दिखाई देता है।"
TEACHING INTENT: CAUSE_EFFECT — **two opposing effects**
VISUAL DECISION: draw the balance. This is the heart of the property and it is
literally a tug-of-war, so show two arrows pulling against each other.
WHAT APPEARS:
  - two opposing arrows on one axis:
    **नाभिकीय आवेश → आकार घटाता है** (pulling one way)
    **d परिरक्षण → आकार बढ़ाता है** (pulling the other)
  - then they meet in the middle and the label **लगभग संतुलित** appears
  - the circle row from scene 07 is then marked: **Cr → Cu : लगभग समान**, with
    those circles shown at visibly equal size
ANIMATION: arrow one draws, arrow two draws opposite it, they meet and both
settle; then the Cr–Cu span on the circle row is bracketed and its circles
equalise.
WHY: "two effects balance" is a mechanical idea with a direction each — exactly
the case for animating rather than stating. He also says omitting this makes the
answer incomplete.
LAYOUT: the balance figure centre; the circle row beneath it, retained from
scene 07 rather than redrawn.
AVATAR: MODE C, unchanged.
COLOURS: the two effects in two opposing accents; the balanced result neutral.
PERSISTENCE: holds to the end of the part; slot ③ then ticks.
IMPLEMENTATION: MANIM

---

# PART 3

# SCENE 09
TIME: 00:05 – 00:41
NARRATION: "अब चलते हैं आखिरी गुण पर — धात्विक लक्षण… सभी संक्रमण तत्व धातु हैं, इसलिए इनमें धात्विक चमक, उच्च घनत्व, उच्च गलनांक और क्वथनांक, आघातवर्ध्यता और तन्यता जैसे गुण पाए जाते हैं। इनकी आयनीकरण एन्थैल्पी तुलनात्मक रूप से कम होती है, और बाहरी स्तर पर एक या दो इलेक्ट्रॉन होते हैं। इस कारण ये धात्विक बंध बनाते हैं।"
TEACHING INTENT: LIST + CAUSE_EFFECT
VISUAL DECISION: slot ④ lights. The observable properties as a filling list,
then the cause beneath them — property and reason, as the whole video demands.
WHAT APPEARS:
  - slot ④ lights: **④ धात्विक लक्षण**
  - properties fill as he names them: **धात्विक चमक · उच्च घनत्व · उच्च गलनांक व
    क्वथनांक · आघातवर्ध्यता · तन्यता**
  - then, beneath, the cause chain: **कम आयनन एन्थैल्पी + बाहरी 1–2 इलेक्ट्रॉन
    → धात्विक बंध → कठोर धातुएँ**
  - final addition at 00:34: **d इलेक्ट्रॉन भी बंधन में योगदान**
ANIMATION: each property appears on its own name and STAYS; then the cause chain
draws link by link.
**Every revealed item's state is set explicitly from its own reveal time** —
this is the exact scene where batch 1 lost item ①.
LAYOUT: properties as a compact horizontal set; cause chain below, horizontal.
AVATAR: MODE B.
IMPLEMENTATION: MANIM

---

# SCENE 10
TIME: 00:41 – 01:03
NARRATION: "तो बच्चों, अब पूरे प्रश्न की चारों बातें एक बार याद कर लेते हैं। इनमें कई ऑक्सीकरण अवस्थाएँ, मध्यम आयनीकरण एन्थैल्पी, परमाणु आकार में थोड़ा परिवर्तन और प्रबल धात्विक गुण पाए जाते हैं। और सबसे ज़रूरी बात — इन चारों गुणों के पीछे का कारण मत भूलना।"
TEACHING INTENT: RECAP + MEMORY_CUE — **the payoff**
VISUAL DECISION: the four-slot spine, which has been present all three parts,
comes to full size with all four now filled — and each shows its CAUSE, because
that is his closing instruction.
WHAT APPEARS, all four filling in as he names them:
  ① **कई ऑक्सीकरण अवस्थाएँ** — *कारण:* ns व (n−1)d की ऊर्जा पास-पास
  ② **मध्यम आयनन एन्थैल्पी** — *कारण:* s व p ब्लॉक के बीच
  ③ **आकार में कम परिवर्तन** — *कारण:* आवेश व परिरक्षण संतुलित
  ④ **प्रबल धात्विक गुण** — *कारण:* धात्विक बंध
ANIMATION: each row fills on its phrase; earlier rows quieten but STAY fully
legible. At "कारण मत भूलना" the four *कारण* clauses all brighten together.
WHY: he asks for the four properties AND their reasons. Pairing them in the
final image is the difference between a list and an answer.
LAYOUT: four rows, property left, cause right, aligned in two columns.
AVATAR: **MODE C** — four two-part rows need the height.
COLOURS: properties neutral; the four causes in brand accent when they brighten.
PERSISTENCE: holds to the end of the teaching section.
IMPLEMENTATION: MANIM

---

# SCENE 11
TIME: 01:05 onward — "…नोट्स बटन पर मिल जाएगा"
VISUAL DECISION: this video points to the NOTES button rather than promising the
screen, so the answer page follows at the end rather than on a cue. Template.
IMPLEMENTATION: TEMPLATE

---

# FINAL SCENE SUMMARY

**Manim**
- general configuration (n−1)d¹⁻¹⁰ns¹⁻², with four connectors fanning to the
  four properties — one root, four consequences
- **the four-slot spine**, persisting across all three parts, lit and ticked
- energy-level sketch with a deliberately small ns/(n−1)d gap
- Mn ✗/✓ correction and the +2…+7 run filling in
- s/transition/p ionisation-enthalpy strip with the Zn·Cd·Hg exception callout
- shrinking-circle row for atomic radius
- **the two-opposing-effects balance** for the Cr–Cu near-constant radius
- metallic-property list plus its cause chain
- the four property↔cause pairs as the closing recap

**Images**
- none. Every idea here is a trend, a configuration or a balance of effects —
  all more accurate in Manim, and none of them has a real-world appearance that
  carries exam information.

**No visual**
- part 1: 00:00–00:21 (hook and framing), 01:40–01:47 (transition)
- part 2: 00:00–00:14 (recap and warning), 01:34–01:42 (transition)
- part 3: 00:00–00:05 (recap)

**Reusable**
- the four-slot spine spans all three parts — created once, lit four times
- the circle row from scene 07 is annotated in scene 08, not redrawn
- the four causes stated in scenes 02, 05, 08 and 09 return as the closing pairs

**New assets**
- none requiring generation. No image cost.
