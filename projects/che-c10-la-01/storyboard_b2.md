# विटामिन की कमी से रोग

## GLOBAL VISUAL STRATEGY

**Teaching objective:** the question names FOUR compounds — ऐस्कॉर्बिक अम्ल,
थायमीन, रेटिनॉल, निकोटिनिक अम्ल — and asks for the diseases their deficiency
causes. The narration covers ten vitamins, so the screen must hold all ten AND
mark the four the exam actually asks about.

**The teacher specifies the visual himself.** At 00:19 he says each vitamin needs
three things remembered together — *"उसका नाम, उसका स्रोत और उसकी कमी से होने
वाला रोग"* — and at 01:43 he says *"तो अब पूरा टेबल हो गया"*. He is describing a
three-column table and calling it a table. The screen builds exactly that.

**Key concepts:** a name → source → deficiency-disease mapping across ten
vitamins, then a reverse recall trick (disease → vitamin) for the four biggest.

**Visual language:** one table, appearing empty with its three column headings at
00:19, then filling ONE ROW PER VITAMIN as each is named. The completed table is
the answer and stays on screen for the recall.

**Main visual assets:** the three-column table (10 rows); highlight marking of
the four exam compounds; the reverse-recall pairs.

**Avatar strategy:** MODE A for the hook; MODE B once the table starts filling;
**MODE C from row six onward** — a ten-row table needs the height, and the
presenter must not cover its lower rows.

**BATCH-1 DEFECT THIS FIXES:** the delivered version put ONE food photograph at
00:00 over the MP Board hook and showed nothing at any of the ten moments a
disease is named, then held a static list for 27 seconds. Every row here lands
on the sentence that names it.

---

# SCENE 01
TIME: 00:17 – 00:32
NARRATION: "तो आज ऐसा करते हैं कि हर विटामिन के साथ बस तीन चीज़ें याद रखनी हैं — उसका नाम, उसका स्रोत और उसकी कमी से होने वाला रोग। बस ये तीनों साथ में याद हो गए तो आंसर लिखते समय कन्फ़्यूज़न नहीं होगा।"
TEACHING INTENT: INTRODUCTION + MEMORY_CUE — **the table is created here**
VISUAL DECISION: put up the empty table with its three headings, exactly as he
names them. The student sees the shape of the whole answer before any content.
VISUAL TYPE: Manim table
WHAT APPEARS: three column headings, appearing one per named item:
  **विटामिन** | **स्रोत** | **कमी से रोग**
then the empty grid rules in beneath them.
ANIMATION: each heading lands on its own phrase; the grid draws last.
WHY: he is literally describing the columns. Building them as he speaks means
the structure is his, not imposed.
LAYOUT: three columns, full width, upper portion of the visual area. Rows sized
so ten will fit legibly — this constrains the row height from the start.
AVATAR: MODE B.
COLOURS: headings in brand accent; grid quiet.
PERSISTENCE: **the table persists from 00:19 to the end of the teaching section.**
IMPLEMENTATION: MANIM

---

# SCENE 02
TIME: 00:34 – 00:44
NARRATION: "विटामिन A यानी रेटिनॉल — ये गाजर, दूध और अंडे में मिलता है। इसकी कमी से रतौंधी होती है, यानी रात में दिखना कम हो जाता है।"
TEACHING INTENT: LIST — row 1
VISUAL DECISION: the first row fills, cell by cell, in the order he says them.
WHAT APPEARS: **A — रेटिनॉल** | **गाजर, दूध, अंडे** | **रतौंधी**
ANIMATION: the vitamin cell at 00:34, the source cell at 00:36, the disease cell
at 00:39 — each on its own clause. The disease cell lands in accent.
**रेटिनॉल is one of the four the question names** — the row carries a small exam
marker from the moment it appears.
AVATAR: MODE B, unchanged.
IMPLEMENTATION: MANIM

---

# SCENE 03
TIME: 00:44 – 00:58
NARRATION: "B ग्रुप देखो — B वन यानी थायमीन, इसकी कमी से बेरी-बेरी। B टू यानी राइबोफ्लेविन, इसकी कमी से डर्मेटाइटिस। और B फोर यानी निकोटिनिक अम्ल, इसकी कमी से पेलैग्रा।"
TEACHING INTENT: LIST — rows 2, 3, 4
WHAT APPEARS, one row per vitamin as he names it:
  - 00:45 **B₁ — थायमीन** | — | **बेरी-बेरी**   ← exam marker
  - 00:48 **B₂ — राइबोफ्लेविन** | — | **डर्मेटाइटिस**
  - 00:53 **B₃ — निकोटिनिक अम्ल** | — | **पेलैग्रा**   ← exam marker
ANIMATION: each row fills on its sentence; the previously filled rows quieten but
stay fully legible.
NOTE: he says "B फोर" but निकोटिनिक अम्ल is **B₃**. The screen carries the
correct **B₃** — the caption reports what was said, the table teaches what is
right, and the answer page must agree with the table.
AVATAR: MODE B → **MODE C** at row 4; one eased change as the table grows past
half its height.
IMPLEMENTATION: MANIM

---

# SCENE 04
TIME: 00:58 – 01:08
NARRATION: "ये B वाले अक्सर घुमा देते हैं, इसलिए नाम और रोग साथ-साथ याद करना। और इस हिस्से को ध्यान से सुनना, क्योंकि एग्ज़ाम में यहीं पर बच्चे सबसे ज़्यादा मिक्स अप करते हैं।"
TEACHING INTENT: COMMON_MISTAKE + WARNING
VISUAL DECISION: mark the B block as the danger zone — no new object.
WHAT APPEARS: a bracket drawn down the left of the three B rows, labelled
**यहाँ सबसे ज़्यादा गड़बड़**; the name and disease cells of those rows brighten
together, since he says to memorise them as pairs.
ANIMATION: bracket draws; the two columns pulse in unison.
WHY: he identifies exactly where students mix up. Bracketing those rows is what
makes the warning specific instead of general.
COLOURS: bracket in the warning tone.
AVATAR: MODE C, unchanged.
IMPLEMENTATION: MANIM

---

# SCENE 05
TIME: 01:08 – 01:20
NARRATION: "B टेन यानी फोलिक अम्ल, इसकी कमी से एनीमिया। और B ट्वेल्व यानी सायनोकोबालामिन, इसकी कमी से रक्ताल्पता और मेरुदंड कमज़ोर होना।"
TEACHING INTENT: LIST — rows 5 and 6
WHAT APPEARS:
  - 01:08 **B₉ — फोलिक अम्ल** | — | **एनीमिया**
  - 01:13 **B₁₂ — सायनोकोबालामिन** | — | **रक्ताल्पता, मेरुदंड कमज़ोरी**
NOTE: he says "B टेन" for folic acid, which is conventionally **B₉**. The table
carries B₉.
AVATAR: MODE C.
IMPLEMENTATION: MANIM

---

# SCENE 06
TIME: 01:24 – 01:43
NARRATION: "अब आखिरी तीन — विटामिन C यानी ऐस्कॉर्बिक अम्ल, इसकी कमी से स्कर्वी और मसूड़ों का फूलना। विटामिन D यानी कैल्सिफेरॉल, जो धूप से मिलता है, इसकी कमी से रिकेट्स यानी सूखा रोग। और विटामिन E यानी टोकोफेरॉल, इसकी कमी से प्रजनन शक्ति में कमी।"
TEACHING INTENT: LIST — rows 7, 8, 9
WHAT APPEARS:
  - 01:25 **C — ऐस्कॉर्बिक अम्ल** | — | **स्कर्वी, मसूड़ों का फूलना**  ← exam marker
  - 01:31 **D — कैल्सिफेरॉल** | **धूप** | **रिकेट्स (सूखा रोग)**
  - 01:38 **E — टोकोफेरॉल** | — | **प्रजनन शक्ति में कमी**
ANIMATION: three rows filling on their sentences. On the last one the whole table
pulses once — it is complete.
AVATAR: MODE C — the table is now at full height and owns the frame.
IMPLEMENTATION: MANIM

---

# SCENE 07
TIME: 01:43 – 01:48
NARRATION: "तो अब पूरा टेबल हो गया।"
TEACHING INTENT: RECAP
VISUAL DECISION: **this is the moment the design was built for.** The complete
table is on screen, exactly as he says the word टेबल. Nothing is added.
WHAT APPEARS: the full nine-row table, all cells filled, the four exam compounds
marked.
AVATAR: MODE C, unchanged.
PERSISTENCE: holds.
IMPLEMENTATION: MANIM

---

# SCENE 08
TIME: 01:48 – 02:00
NARRATION: "चलो अब एक आसान ट्रिक से इसे पक्का करते हैं। याद रखने का आसान तरीका — रोग के नाम से विटामिन याद करो। रतौंधी मतलब A, बेरी-बेरी मतलब B वन, स्कर्वी मतलब C, रिकेट्स मतलब D।"
TEACHING INTENT: MEMORY_CUE — the reverse mapping
VISUAL DECISION: the table stays; four **reverse arrows** are drawn from disease
back to vitamin, one per pair he recites. The trick is a direction, so show the
direction.
WHAT APPEARS, one per phrase:
  **रतौंधी → A** · **बेरी-बेरी → B₁** · **स्कर्वी → C** · **रिकेट्स → D**
each drawn as an arrow running RIGHT-TO-LEFT across its own row, from the
disease column back to the vitamin column.
ANIMATION: each arrow draws on its phrase and its row brightens. The other rows
dim, leaving these four lit.
WHY: the whole video has taught vitamin → disease. He is now teaching the reverse
lookup, which is how exam questions are actually phrased. Arrows running the
other way across rows the student already knows makes the reversal explicit.
AVATAR: MODE C, unchanged.
COLOURS: the four reverse arrows in brand accent.
PERSISTENCE: holds to the end of the teaching section.
IMPLEMENTATION: MANIM

---

# SCENE 09
TIME: 02:00 – 02:03
NARRATION: "ये चार एकदम पक्के कर लो और इनके नाम ऐसे ही एग्ज़ाम में लिखना।"
TEACHING INTENT: MEMORY_CUE
VISUAL DECISION: the four exam-marked rows brighten together and the rest fade
back — the exam answer isolated from the fuller list.
WHY: the question asks for four compounds; the narration covered ten. Ending on
the four is what aligns the video with the question.
AVATAR: MODE C, unchanged.
IMPLEMENTATION: MANIM (state change)

---

# SCENE 10
TIME: 02:07 onward — "…नोट्स बटन पर मिल जाएगा"
VISUAL DECISION: this video points to the NOTES button, so the answer page
follows at the end rather than on an on-screen cue. Template.
IMPLEMENTATION: TEMPLATE

---

# FINAL SCENE SUMMARY

**Manim**
- **the three-column table** — headings built as he names them, nine rows filled
  one per vitamin, persisting from 00:19 to the end
- exam markers on the four compounds the question actually names
- the warning bracket down the B-vitamin rows
- four reverse-recall arrows, disease → vitamin

**Images — PROPOSED, NOT GENERATED**
The user asked for disease photographs at the moment each disease is named, and
that is a legitimate image use under the framework: a real medical condition
whose appearance is not conveyable by a diagram. The rows they would attach to
are रतौंधी (00:39), बेरी-बेरी (00:45), डर्मेटाइटिस (00:48), पेलैग्रा (00:53),
स्कर्वी (01:25) and रिकेट्स (01:31).

**Not generated in this pass** — generation costs money and was not approved
before the user went AFK, and medical imagery of deficiency conditions warrants
a human decision about what is appropriate for a Class 12 audience. Estimated
cost for six images at 1024×1024: **≈ $0.24**.

Recommendation if approved: **three, not six** — रतौंधी, स्कर्वी and रिकेट्स.
They are the most visually distinctive, and three of the four exam compounds.
Each should be a clean clinical illustration on a plain ground, no text in the
image (labels are typeset in Manim), placed beside its own table row while that
row is being spoken, and removed when the next row fills.

**The table teaches the answer without them.** The photographs would deepen
recall; they are not load-bearing.

**No visual**
- 00:00–00:17 (hook and framing)

**Reusable**
- one table, nine rows, filled at nine separate moments; never rebuilt
- the four exam markers are placed as rows appear and reused for the closing
  isolation

**New assets**
- none generated. Six optional disease images pending approval (≈$0.24).
