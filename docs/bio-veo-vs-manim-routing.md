# Biology: what Veo can carry, and what it structurally cannot

Written after generating all 14 Long-Answer clips on chroma and grading every one
against its own biology checks. Not a prediction — a post-mortem with evidence.

Result after fixes: **7 ship, 7 route to Manim/SVG.**

## The finding

The failures are not spread evenly. Every one of them fails on the same thing:

> **A discrete quantity that IS the answer.**

Veo renders *manner* reliably and *quantity* unreliably. It knows what a polar
body looks like, what a phage does, what a pond contains. It does not reliably
produce THREE of something when three is the marked fact, and it does not
reliably orient a structure when the orientation is the marked fact.

| clip | the marked quantity | what Veo drew |
|---|---|---|
| C4-LA-02 | 9 : 3 : 3 : 1 | 9 : 4 : 4 : 4 |
| C1-LA-01 | 3 egg-apparatus + 3 antipodals | 1 + 2 |
| C1-LA-01 | micropyle BESIDE the funicle (anatropous) | at the far end (orthotropous) |
| C12-LA-01 | arrow direction: eaten → eater | reversed; chains crossed |
| C12-LA-02 | tier order by trophic level | inverted and scrambled |
| C5-LA-03 | A–T and G–C, consistently | any base with any base |
| C5-LA-01 | child's bands traceable to a parent | random bands |

And every clip that PASSED asks for no such quantity:

| clip | what it asks for | why Veo is fine |
|---|---|---|
| C4-LA-01 | blend vs patch | a visual contrast, not a count |
| C2-LA-01 | unequal division | the *manner* of dividing |
| C2-LA-03 | a sperm's shape | morphology |
| C5-LA-02 | phages inject, DNA enters | an action |
| C12-LA-03 | a pond has layers of life | a habitat |
| C1-LA-02 | four here, one there | ONE small count, heavily contrasted |

C4-LA-03 (the pedigree) passed, and it is the interesting exception: it has both
a count and an orientation. It came out right, once. It should not be trusted to
come out right again — a pedigree is a symbol grid, and the next generation is a
fresh roll.

## Confirmation: the briefs were fixed, and it failed anyway

Three clips were regenerated with briefs corrected precisely against the finding.
This was the test of whether the failures were prompt-craft or capability.

| clip | the fix | result |
|---|---|---|
| C1-LA-01 | anatropous stated three ways; 3+3 cells named explicitly | **still fails** — 4 and 6 cells; funicle drawn free, attached to nothing; micropyle still at the far end |
| C5-LA-03 | only TWO legal rung pairings, named by colour, with every other pairing banned | **still fails** — yellow met blue, red met yellow, magenta appeared as a fifth colour |
| C2-LA-02 | ovaries added; "a wide band of empty green on every side" | **half** — ovaries correct, framing worse; drawing grew and both ovaries clipped |
| C2-LA-02 (2nd) | framing ONLY, and stated concretely: "spans the middle THIRD of the picture width" | **passes** — ovaries kept, nothing touches an edge |

That settles it. A brief that names the exact number, bans every alternative and
states the constraint three ways still does not produce three cells. This is a
capability boundary, not a wording problem, and no further prompt iteration is
warranted on these rows.

Two of my own errors are visible in that table and both are already in the ledger:

- I specified yellow-with-GREEN rungs on a GREEN chroma field. Had the model
  complied, half of every such rung would have keyed out into a hole. Same class
  as the green embryo sac on green. **Check every named colour against the chroma
  field before the prompt is sent** — this is now a mechanical check, not a habit.
- C2-LA-02 asked for anatomy AND framing in one prompt and got only anatomy.
  Emphasis is zero-sum: two new demands in one revision means one lands. Re-run
  with framing alone, stated as a concrete fraction of the frame rather than as
  "a wide band", and it passed. **One new demand per revision, named in units
  the model can measure.**

## The routing

### Manim / SVG — because the answer is a quantity or a topology

| ID | why |
|---|---|
| **C4-LA-02** | 9:3:3:1 in a 4×4 grid. The ratio IS the mark. Unreachable by generation. |
| **C4-LA-03** | pedigree symbols, filled/half-filled, generation lines. A diagram, not a scene. |
| **C12-LA-01** | arrows with direction. Direction is topology; generators do not respect it. |
| **C12-LA-02** | tiers ordered by trophic level, with counts. Ordering IS the concept. |
| **C5-LA-01** | band-sharing between lanes. The relationship between marks is the answer. |
| **C1-LA-01** | 7 cells / 8 nuclei, plus anatropous orientation. Both are marked facts. |

Six of fourteen. Note that this is almost exactly the split the FIRST routing doc
predicted from the question text alone, before any clip existed — it put the
genetics and ecology rows in Manim for the same reason. The generation run did
not overturn that judgement; it confirmed it with evidence.

### Veo — because the answer is a manner, an action or a habitat

| ID | keep as-is |
|---|---|
| **C4-LA-01** | ship |
| **C2-LA-01** | ship |
| **C2-LA-03** | ship |
| **C5-LA-02** | ship |
| **C12-LA-03** | ship |
| **C1-LA-02** | ship |
| **C2-LA-02** | ship — passed on the framing-only retry |

### Veo, but regenerate

| ID | fix |
|---|---|
| **C5-LA-03** | moved to Manim — the named-pairing fix was tried and failed |

## The rule this yields

> **Ask Veo for the verb. Ask Manim for the number.**

If you can state the mark as a count, a ratio, an order or a direction, it is
Manim's. If the mark is "show me how this happens", it is Veo's.

A hybrid follows naturally and is probably the real answer for several rows:
generate the organic body in Veo on chroma, and composite Manim's counts, arrows
and labels over it. C1-LA-01 is the clearest candidate — the ovule's *form* is
organic and Veo draws it beautifully; the seven cells and the anatropous
orientation are geometry and belong to Manim.

## A process failure worth recording

`bio_BIO-C1-LA-01_plan.md` contains a section headed CORRECTION, which states
that the ovule is anatropous and the micropyle therefore sits BESIDE the funicle,
not opposite it. That correction was written, and then **never propagated into
either brief file**. `bio_animations.py` still said "a small opening at the narrow
end"; `bio_ovule_clips.py` still said "the gap is at the end opposite the stalk".

Veo rendered the brief faithfully. The clip is orthotropous because the brief is.

The frame review could not catch it, because the review grades the clip against
the brief. This is the third occurrence of the same failure mode in this project
(GAG/GTG, the accuracy brief, now this): **a wrong brief produces a confidently
wrong clip that passes review.** The correction must live in the file the
generator reads, or it does not exist.
