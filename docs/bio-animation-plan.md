# Biology Class 12 — animation plan

> **SUPERSEDED by [`bio-manim-plan.md`](bio-manim-plan.md).** This file was
> routed from the QUESTION TEXT alone, because the scripts were not readable
> at the time. They are now, and reading them moves every one of the six
> Veo rows below into Manim — in each case the "organic" element was
> decoration and the marks hung on a count, a direction or a label that a
> generated clip cannot be held to. Kept for the reasoning, not the routing.

Derived from the tracking sheet's Biology tab (62 questions; the 15 Long Answers
are the ones carrying scripts). Routed by `PIPELINE.md`'s rule: **what do the
beats have to SHOW**, not what subject they belong to.

> The `.docx` scripts are linked from the sheet but the hyperlinks do not survive
> CSV or HTML export, so this plan is derived from the QUESTION TEXT alone. That
> is the right input for routing — the question says what must be shown — but the
> scripts will refine shot counts and emphasis. Expect this list to move once
> they are readable.

## Why biology routes differently from chemistry

Of the chemistry PYQ scripts, roughly two thirds were equation and graph work,
which Veo renders badly and Manim renders correctly by construction. Biology
inverts that for a specific subset: **molecular and cellular processes are
organic, three-dimensional and in motion** — a helix unwinding, a phage
injecting, a cell dividing — which is precisely what Manim renders stiffly and
Veo renders well.

But genetics is the opposite extreme. Punnett squares, pedigrees and ratios are
grids, symbols and numbers: Veo cannot set them and should never be asked to.

## The routing

### Veo — generated on chroma green, keyed and composited

| ID | what moves | why not Manim |
|---|---|---|
| **BIO-C5-LA-04** | DNA replication: the helix unwinds, strands separate, new strands build along each template | continuous 3D helical motion; Manim's version is a stiff schematic |
| **BIO-C5-LA-03** | the double helix itself — turning, showing the two backbones and the paired bases | 3D form with depth and foreshortening |
| **BIO-C5-LA-02** | Hershey–Chase: phages settling on a bacterium and injecting | organic shapes, photoreal texture |
| **BIO-C2-LA-01** | oogenesis — one cell dividing unequally, the polar body pinching off | the *act* of division is organic |
| **BIO-C2-LA-03** | spermatogenesis — a spermatid reshaping into a sperm | organic morphological change |
| **BIO-C12-LA-03** | a pond as a living system — organisms at their levels | photoreal habitat |

### Manim — correct by construction, no Veo involvement

| ID | what it is |
|---|---|
| BIO-C4-LA-01 | co-dominance / incomplete dominance — crosses and ratios |
| BIO-C4-LA-02 | independent assortment — 4×4 Punnett square, 9:3:3:1 |
| BIO-C4-LA-03 | haemophilia pedigree — X-linked symbols and a cross |
| BIO-C12-LA-01 | four labelled comparisons (grazing vs detritus, etc.) |
| BIO-C12-LA-02 | ecological pyramids — bars with counts, upright and inverted |
| BIO-C1-LA-01 | labelled ovule diagram — the question ASKS for a clean labelled figure |
| BIO-C2-LA-02 | menstrual cycle — hormone curves against a timeline |
| BIO-C5-LA-01 | DNA fingerprinting — gel bands and steps |

### Split — Manim frame, one Veo insert

| ID | Manim | Veo |
|---|---|---|
| BIO-C1-LA-02 | the counts (4 microspores; 1 functional megaspore of 4) and labels | one meiotic division shown organically |

**Counts and labels never go to Veo.** Where a question turns on a number —
four microspores, three polar bodies, 9:3:3:1 — that number is Manim's, and the
Veo clip shows the *manner* of the change, not the tally.

## Sequencing

Start with **BIO-C5-LA-04 (DNA replication)**. It is the strongest case for the
route — the motion is continuous, three-dimensional and genuinely beyond Manim —
and if the green-screen pipeline holds for a turning, unwinding helix it will
hold for the rest of the list.

Everything in the Manim column needs no Veo work at all, which is most of the
list. The generation effort concentrates on six questions, not fifteen.
