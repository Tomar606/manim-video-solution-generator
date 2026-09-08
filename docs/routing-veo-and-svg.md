# Veo or SVG: the rule, and the gate that enforces it

**The rule, in one line:**

> **Ask Veo for the verb. Ask Manim for the number.**

Enforced by `tools/route_gate.py`, which refuses a build rather than reporting a
preference. This file is the *rule*;
[`bio-veo-vs-manim-routing.md`](bio-veo-vs-manim-routing.md) is the *evidence* it
came from — a post-mortem on fourteen generated clips, each graded against its
own checks.

---

## Why there is a rule at all

Veo is not unreliable in general. It is unreliable in one specific way, and that
way is predictable:

> **A discrete quantity that IS the answer.**

Across fourteen clips, every failure was the same failure:

| asked for | drew |
|---|---|
| 9 : 3 : 3 : 1 | 9 : 4 : 4 : 4 |
| 3 egg-apparatus cells + 3 antipodals | 1 + 2 |
| micropyle beside the funicle (anatropous) | at the far end (orthotropous) |
| arrows: eaten → eater | reversed, chains crossed |
| trophic tiers in order | inverted and scrambled |
| A–T and G–C only | any base with any base |

And every clip that passed asked for no such thing: *unequal division*, *a
sperm's shape*, *phages injecting*, *a pond with layers of life*. Manner, not
quantity.

**This was tested, not assumed.** Three failures were re-briefed with the exact
number named, every alternative banned, and the constraint stated three ways.
They failed again — four cells instead of three, a funicle attached to nothing,
yellow pairing with blue. That is a capability boundary, so the gate's checks are
hard. No wording gets a beat past them, and each attempt costs a generation
cycle.

---

## The decision

For each beat, declare what it must get **right** — not what it looks like:

```json
{ "slug": "unwind", "route": "veo",
  "mark": "helicase unzips the helix and a Y-shaped fork opens",
  "marked": {},
  "labels": ["प्रतिकृति द्विशाख"], "overlay": "manim" }
```

`marked` names the facts the beat is graded on. Any one of these forces a drawn
route:

| flag | means |
|---|---|
| `quantity` | an exact count is the marked fact — three cells, two bonds |
| `order` | a sequence or ranking is the marked fact — trophic tiers |
| `direction` | a direction is the marked fact — 5′→3′, eaten → eater |
| `pairing` | which thing goes with which — A–T, G–C |
| `reproduce` | the student copies this exact figure into the answer book |

**Empty `marked` → Veo.** Where a beat could go either way it is generated. Not
because the drawing would be worse, but because the generated clip is what makes
the video feel *made* rather than assembled, and engagement is a requirement
rather than a decoration. The gate warns on a drawn beat with no marked fact:
that is a choice someone should justify.

---

## What the gate checks

`python tools/route_gate.py projects/<slug>/route_part<N>.json [--explain]`

| check | result |
|---|---|
| a Veo beat declares any marked fact | **fail**, naming which |
| a drawn beat declares none | warn — this could be generated |
| a Veo beat has labels but no `"overlay": "manim"` | **fail** |
| fewer than 1 Veo beat in the video | **fail** |
| fewer than 2 | warn |
| a Veo beat has a clip but no QC verdict | **fail** |
| its QC verdict is not `pass` | **fail** |
| its prompt trips `veo_prompts.audit()` | **fail** |

### The minimum is deliberate

`MIN_VEO = 1`, `WANT_VEO = 2`. Three videos in a row shipped with **no**
generated clips — each decision defensible alone, and the cumulative result was a
series of slideshows. A floor forces the question to be asked. If a question
genuinely has nothing generatable, that has to be stated rather than arrived at
by default.

### Labels are never generated

No video model sets Devanagari correctly, and a neat wrong letterform is still a
defect. Labels on a generated clip are composited by `src/veo_labels.py`. A Veo
beat carrying `labels` must say `"overlay": "manim"`, or the gate assumes the
clip will come back with invented lettering.

---

## The hybrid, which is usually the right answer

Generate the organic body on chroma; composite the counts, arrows and labels over
it. The ovule is the clearest case: its *form* is organic and Veo draws it
beautifully, while the seven cells and the anatropous orientation are marked
facts that it cannot hold. Splitting them gets both.

Declare it as a Veo beat with `overlay: manim` and the labels listed.

---

## Keeping retries down

Each regeneration is minutes and a fresh roll of the dice. These are the rules
that cost a cycle when broken — all from the bug ledger:

- **One new demand per revision.** Emphasis is zero-sum. A revision asking for
  corrected anatomy *and* corrected framing produced anatomy only; framing alone
  on the next pass passed.
- **State a constraint in units the model can measure.** "A wide band of empty
  green" failed; "spans the middle third of the picture width" passed.
- **Check every named colour against the chroma field.** A prompt once asked for
  yellow-with-green rungs on a green screen — had it complied, half of every rung
  would have keyed out into a hole.
- **Naming a thing is a signal to draw it, even in a negative.** Never write
  logo, watermark, badge or wordmark anywhere in a prompt. `audit()` enforces the
  rest: no percentages, no pixel counts, no zone names.
- **Never carry a rejected clip forward.** A frame the review just condemned,
  used to seed the next generation, turns one bad clip into five that look more
  consistent than the correct version.

---

## Worked example — BIO-C5-LA-04, DNA replication

| beat | route | why |
|---|---|---|
| opener: nucleus → chromosome → DNA | **veo** | no marked fact at all; pure engagement |
| helicase unzipping, fork opens | **veo** + labels | the verb; Y label composited |
| topoisomerase relieving supercoils | **veo** | manner, not quantity |
| semiconservative: one old + one new | manim | `pairing` |
| *ori*: one site vs many | svg | `quantity` — the contrast is the mark |
| 5′→3′ only | manim | `direction`; the script itself warns about it |
| leading vs lagging | manim | `direction`, `order` |
| Okazaki + ligase | manim | `quantity` |
| two phosphate bonds, once per cycle | chip | `quantity` |

Three generated, above the target of two, and every one of them a verb.
