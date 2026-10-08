# Biology — what Manim can carry, and how to make it look real

Derived from **reading all fourteen biology scripts** in `inbox/bio_scripts/`,
not from the question text. That matters: the question says what the answer
must contain, but the script says what the teacher is looking at when he says
it, and those are different lists. This file supersedes the routing table in
`bio-animation-plan.md`, which was written from question text alone.

The fifteenth Long Answer, **BIO-C5-LA-04 (DNA प्रतिकृति)**, has no script in
that folder; its animation was built from the sheet's answer and is delivered
at `~/Desktop/Diagrams/BIO-C5-LA-04_dna-replication.mp4`.

---

## The double helix, answered directly

Yes — and it is not a compromise. `projects/_scratch/dna_helix.py` renders a
shaded, rotating B-DNA model at 1080×1920, and then **stops and measures
itself**: व्यास 2 nm, एक पूर्ण मोड़ 3.4 nm, 10 क्षारक युग्म प्रति मोड़, दो
निकटवर्ती क्षारक युग्मों के बीच 0.34 nm, प्रतिसमानांतर 5′/3′ ends,
दक्षिणावर्ती coiling.

Those are the Watson–Crick script's own nine points. One Manim unit is one
nanometre, so the callouts are **reading the model, not captioning a picture**.
That is the whole argument for Manim here: a generated clip can produce a
handsome helix, but it cannot promise ten base pairs to a turn, cannot be
measured, cannot be guaranteed right-handed, and will not coil the same way
twice across three parts of the same video. This question is nine measurements
wearing a picture. Measurements are what Manim is for.

Three things make it read as an object rather than a diagram, and they
generalise to everything below:

1. **Swept tube `Surface`s for the backbones**, not stroked curves. Surfaces
   take light and occlude each other; a stroke in 3D reads as wireframe.
2. **The two backbones are ~140° apart, not 180°.** That asymmetry is what
   carves the major and minor grooves. At 180° you get a flat twisted ribbon
   that nobody recognises as DNA — it is the single most common giveaway in a
   fake helix.
3. **It turns.** Ambient camera rotation supplies the depth cue that no amount
   of shading will.

---

## What "looks real" means in Manim — the seven levers

Realism in this material is not photorealism. It is the absence of the specific
tells that make a drawing read as a drawing.

| lever | what it fixes | where it earns its keep |
|---|---|---|
| **Shaded solids over strokes** — `Surface`, `Sphere`, `Cylinder` | outlines read as symbols; shaded volumes read as things | helix backbones, RBC, phage head, chromosomes |
| **~140°, not 180°; irregular, not perfect** | a perfect circle is a symbol; a slightly irregular closed bezier is a cell | membranes, nucellus, ovule outline, pond bed |
| **A rest state that moves** | living things never hold still. A sine updater on a flagellum, a 2% breathing scale on a cell, slow ambient rotation | sperm tail, phage settling, helix |
| **Occlusion and depth falloff** | overlap is the cheapest 3D cue there is | anything with a camera |
| **Proportions from the script's own numbers** | when the ratios are right the eye forgives flat colour | 2 : 3.4 : 0.34 nm; 1 → 2 → 4; 7 cells / 8 nuclei |
| **Soft edges where biology is soft** | a hard rectangle is never a gel band | electrophoresis bands, stains, cytoplasm |
| **Two or three hues plus one accent** | textbook figures are legible because they are not rainbow | everything |

And the counter-rule, which is load-bearing: **stop short of realism wherever
the exam wants a line drawing.** Two of these questions
(`BIO-C1-LA-01` ovule, `BIO-C12-LA-03` pond) say *चित्र बनाइए* — the student has
to reproduce the figure by hand in the answer book. A beautiful shaded render
of an ovule teaches them nothing they can draw. Those two match the NCERT line
look on purpose, and the animation value is in the *order* the labels arrive.

---

## The fourteen scripts

### Tier 1 — Manim is the only correct answer
Every one of these turns on a count, a ratio, a grid or a direction. A
generated clip cannot set Devanagari, cannot be trusted with a number, and
cannot keep a symbol stable between parts.

| ID | topic | what the script demands on screen | the realism lever that matters |
|---|---|---|---|
| **BIO-C5-LA-03** | वाटसन-क्रिक द्विकुण्डली | nine measurable facts; the script itself warns *80% बच्चे 5′→3′ की direction में गलती करते हैं* | shaded tubes + 140° grooves + rotation; then **flatten the helix into the 2D ladder they must draw**. That morph is free in Manim and impossible in Veo |
| **BIO-C2-LA-02** | आर्तव चक्र | a 28-day timeline with four dated phases (3–5, 5–13, 14, 15–28), FSH/LH curves with the day-14 **LH surge**, estrogen and progesterone, endometrium thickness | not realism — **coupling**. One playhead driving four stacked tracks (day, ovary, endometrium, hormones) so the student sees the *cause*. The script's own correction — "LH surge वजह है, अण्डोत्सर्ग नतीजा" — only lands if the spike visibly precedes the release |
| **BIO-C4-LA-02** | स्वतंत्र अपव्यूहन | 4×4 checkerboard, 16 boxes filled one at a time, 9 : 3 : 3 : 1, and the 9-term genotype ratio | fill the grid as he speaks, then **re-colour the 16 cells into 9/3/3/1 so the ratio is counted on screen**, not asserted. Real pea seeds (round/wrinkled, yellow/green) as the phenotype icons |
| **BIO-C4-LA-03** | हीमोफीलिया | Xᴴ / Xʰ / Y symbols, XʰY × XᴴXᴴ, gametes, Punnett square, 50% carrier daughters | draw **actual chromosome shapes** with a centromere and a coloured affected segment, not letters. Then criss-cross inheritance is *seen*: the father's coloured X can only reach daughters |
| **BIO-C4-LA-01** | सह-/अपूर्ण प्रभाविता | ABO antigens on the RBC surface, three alleles, AB showing both, RR × rr → Rr pink, F₂ 1 : 2 : 1 | the RBC as a real **biconcave disc** (surface of revolution) with shaded antigen knobs. Red→pink is literally `interpolate_color` — the blend the script argues *against* is worth animating and then undoing at F₂ |
| **BIO-C12-LA-02** | पारिस्थितिक पिरामिड | producers at base, three types, upright vs inverted, ocean biomass and single-tree number examples | animate the **inversion** — flip the bar widths so "उल्टा" is a thing seen. Organism silhouettes inside each bar so levels are recognisable |
| **BIO-C12-LA-01** | पारिस्थितिकी — 6 अन्तर | six two-column comparisons | one of the six deserves motion: build the food **chain**, grow the extra edges into a **web**, then cut one link — the chain breaks, the web survives. That is the script's stability point, animated |
| **BIO-C1-LA-02** | लघु-/गुरुबीजाणुजनन | anther T.S. with one microsporangium per corner, four wall layers **in order**, many MMCs vs one, 4 microspores all surviving vs 4 megaspores of which **only the chalazal one** survives | concentric shaded rings for the four layers; the three degenerating megaspores **shrink and fade** rather than vanish — that is the difference the script says everyone confuses |

### Tier 2 — Manim, and the "organic" objection does not survive contact
The earlier plan sent these to Veo on the grounds that Manim renders organic 3D
stiffly. Having built the helix, that premise does not hold for this material —
and each of these questions also carries a number that Veo would put at risk.

| ID | topic | the "organic" moment | why Manim still wins |
|---|---|---|---|
| **BIO-C5-LA-02** | हर्षे व चेज | phage settling on a bacterium and injecting DNA | the experiment's logic is **where the radioactivity ends up**: ³²P in the pellet, ³⁵S in the supernatant. That is two labelled containers and a population of dots moving between them. The phage is an icosahedral head and a tail — geometry. Veo would give a lovely phage and an untrustworthy tube |
| **BIO-C2-LA-03** | शुक्रजनन | spermiogenesis — a round spermatid reshaping into a motile sperm | the counting tree (1 primary, 46 → 2 secondary, 23 → 4 spermatids) is non-negotiable and numeric. The morph itself is a few primitives: an acrosome arc sweeping over a condensing nucleus, cytoplasm shed as a residual body, and a **flagellum on a sine updater** — which is the cheapest convincing "alive" in Manim |
| **BIO-C2-LA-01** | अण्डजनन | the unequal division, polar body pinching off | 20 लाख → 60–80 हजार, and 1 large + 1 tiny, are counts. The pinch is a closed curve with a necking updater — organic-looking and exactly reproducible. Meiosis II arrested until fertilisation is a *pause*, which is a timeline instruction |
| **BIO-C5-LA-01** | DNA अंगुलीछाप | the gel run | electrophoresis is a **physics animation**: fragments migrating at rates set by size, in a field. Manim's home turf, and genuinely satisfying to watch. Soft-edged bands and a black autoradiograph with white bands do the realism; two lanes side by side make match/no-match read |

### Tier 3 — deliberately not realistic
| ID | topic | why |
|---|---|---|
| **BIO-C1-LA-01** | प्रारूपिक बीजाण्ड | the question is *स्पष्ट एवं साफ-सुथरा नामांकित चित्र बनाइए*, 6 marks. The student reproduces this by hand. NCERT line look, labels arriving as he names them, and the **7 cells / 8 nuclei counted on screen** — 1 egg + 2 synergids + 3 antipodals + 1 central cell, with the central cell's two polar nuclei making the eighth |
| **BIO-C12-LA-03** | तालाब का पारितंत्र | *केवल चित्र की सहायता से दर्शाइए*. A labelled cross-section with zones. A photoreal pond is off-brief; one real photograph as an opening establishing shot is fine, a generated clip is not |

---

## What changed from the earlier plan

`bio-animation-plan.md` routed six topics to Veo. After reading the scripts,
**none of them should go to Veo.** The reason is consistent across all six: in
every case the "organic" element the plan was buying is decoration, and the
thing the marks actually hang on is a number, a direction or a label that a
generated clip cannot be held to.

The general rule this produces, and it is worth keeping:

> **Route on what the marks hang on, not on what the subject is.** Biology
> *sounds* organic and Veo-shaped. But an MP Board 4-mark biology answer is
> almost always a count, an order, a ratio or a named part — and those are the
> four things a generated clip is worst at.

---

## Build order

Cheapest to hardest, and the first three share machinery with work already
delivered:

1. **BIO-C5-LA-03** double helix — the model exists; add the flatten-to-ladder morph and the A=T / C≡G hydrogen-bond counts
2. **BIO-C4-LA-02**, **BIO-C4-LA-03** — Punnett grids; one grid component serves both
3. **BIO-C12-LA-02**, **BIO-C12-LA-01** — bars and comparisons
4. **BIO-C2-LA-02** menstrual cycle — the four coupled tracks; the highest-value single animation in the set
5. **BIO-C5-LA-01** electrophoresis, **BIO-C5-LA-02** Hershey–Chase — container physics
6. **BIO-C2-LA-03**, **BIO-C2-LA-01** — the morph and the pinch
7. **BIO-C1-LA-01**, **BIO-C1-LA-02**, **BIO-C12-LA-03** — line-drawing figures

---

## What was built (per script part)

Source: `projects/_scratch/bio/`. One scene class per script part, because each
part is its own video and because one frame cannot hold a whole topic without
the labels fighting — the gate said so on the first attempt.

| ID | parts | what each part carries |
|---|---|---|
| BIO-C5-LA-03 | 3 | flat ladder → **twists into the helix** · A=T two bonds, C≡G three · 2 nm, 3.4 nm, 10 bp · 0.34 nm, complementarity, stability |
| BIO-C5-LA-02 | 3 | P vs S chemistry, both labellings · infection, then pellet vs supernatant · conclusion and both sequences |
| BIO-C5-LA-01 | 2 | VNTR/STR, isolation, digestion, **the gel run** · blotting, probe, autoradiograph |
| BIO-C5-LA-04 | 1 | replication (built earlier, no script in the folder) |
| BIO-C4-LA-02 | 3 | symbols and F₁ · **checkerboard filled then recoloured into 9:3:3:1** · the law |
| BIO-C4-LA-03 | 3 | X-linked recessive on drawn chromosomes · criss-cross · Punnett and result |
| BIO-C4-LA-01 | 3 | ABO on biconcave RBCs · AB vs pink flower · 1:2:1 and the enzyme |
| BIO-C2-LA-02 | 3 | definition and shedding · **surge drawn before the release** · luteal, feedback, regulation |
| BIO-C2-LA-03 | 3 | definition and multiplication · **1(46) → 2(23) → 4** · spermiogenesis morph with a beating tail |
| BIO-C2-LA-01 | 2 | 20 lakh → 60–80 thousand as a thinning field · arrest, unequal division, hormones |
| BIO-C12-LA-02 | 3 | definition and three types · **bars inverting** · energy always upright |
| BIO-C1-LA-02 | 3 | two columns, anther and ovule · MMC counts · **three megaspores visibly degenerate** |

## Not built, on purpose

Three topics would be worse as animation than as a clean static figure, so they
were left out rather than forced:

- **BIO-C1-LA-01 (प्रारूपिक बीजाण्ड)** — the question is *स्पष्ट एवं साफ-सुथरा
  नामांकित चित्र बनाइए*, 6 marks. The student reproduces this by hand. Nothing
  moves, and making it look "real" actively hurts.
- **BIO-C12-LA-03 (तालाब का पारितंत्र)** — *केवल चित्र की सहायता से दर्शाइए*.
  A labelled cross-section. Same reason.
- **BIO-C12-LA-01 (छह अन्तर)** — six two-column text comparisons. Five of the
  six are tables. Only food-chain-vs-food-web has any motion in it.

These belong in `~/Desktop/Diagrams/` as SVG figures alongside the chemistry
ones, not as clips.

## The two rules, enforced rather than checked

`bio_common.py` re-runs a gate after **every** `play()` and `wait()`:

- nothing may sit below **y = −3.2**, which is the top of the bottom 30%
- no two labels may overlap, and no label may sit on a filled figure

It raises before a frame is written, so a render that finishes is a render that
obeyed both at every keyframe. It earned its keep immediately — it caught a
day label 0.09 units into the presenter's band, a counts block touching the
checkerboard, `"ग्राफी पुटक"` sitting on `"14"`, and a chain of text lying
across the ovary.

It checks **keyframes, not the middle of a tween**, which is why captions cut
instead of cross-fading.

And it is structurally blind to the 3D helix scenes: their world-space bounding
boxes say nothing about where a thing lands on screen once the camera has
projected it. That blind spot is not theoretical — it shipped all three helix
clips with their caption notes sitting in the presenter's band, at y = −4.75 to
−6.40. Looking at frames did not catch it either; the text was plainly visible
in a frame that had already been reviewed.

So there is a **second gate that works on pixels**, `band_check.sh`, and nothing
reaches the delivery folder without passing it. It crops the bottom 30% of eight
frames spread across the clip and reads peak luminance: the plate is ~20 and
near-white text is ~250, so a threshold of 45 is nowhere near the noise. It
found the three bad clips immediately, and then found a second cause after the
first fix — the ladder's bottom 5′/3′ labels hanging below the model.

The general shape of this is worth keeping: **a geometric gate cannot check a
projection, and a reviewer cannot be trusted to notice what they have already
looked at once.** Where both are true, check the output rather than the input.
