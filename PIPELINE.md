# How this project actually works

Written so someone — or some other Claude session — can pick this up cold and
know what to run, what the outputs mean, and which mistakes have already been
made and fixed. `CLAUDE.md` holds the design rationale; this holds the flow.

There are **two products** in this repo. They share `src/llm.py`, the style
system and the render/composite stages, and diverge everywhere else.

| | Reels track (original) | **PYQ track (current focus)** |
|---|---|---|
| Input | a topic string, or a `.docx` in `inbox/` | one row of the Google question sheet |
| Script format | `[narrator]` beats + `$$LaTeX$$` | `भाग` sections, formulas under `On Screen:` |
| Written by | `src/script_writer.py` | `src/pyq_writer.py` |
| Language | Hinglish (Latin) | Hindi (Devanagari) |
| Layout | landscape, `chroma: right_half` | portrait 1080×1920, top 60% animation / bottom 40% avatar |
| Reviewed as | `script.md` | a Google Doc in `Scripts/<Subject>/` |

Everything below is the PYQ track.

---

## 1. The question sheet is the entry point

One Google Sheet, one tab per subject, one row per previous-year question.
`src/pyq_writer.py:load_questions("Chemistry")` pulls it as CSV — no auth, no
API key, just the `gviz` export URL.

A row gives: question ID, chapter, category, **the question**, **the sheet's
answer**, and the year(s) it appeared. `_years()` parses the shorthand the sheet
uses — `"2019, 20, 22 , 24"` becomes `[2019, 2020, 2022, 2024]`.

**The sheet's answer is a starting point, not the authority.** Every answer
checked so far has contained real errors: `E₁ > E₂` on the dipole equatorial
line (it is `E₁ = E₂`, and the whole derivation rests on that), and five in the
कोलरॉश answer including `Λ°(NaCl) = λ°(Na⁺) + 2λ°(Cl⁻)` — NaCl has one chloride.
This is why step 2 exists.

## 2. Verify → write → check → repair

`src.pyq_writer.draft(q)` runs the whole loop:

1. **`verify_answer(q)`** — Claude cross-checks the sheet's answer against NCERT
   and returns corrections, omissions, frozen terminology and the errors to
   avoid if it gets animated. Saved as `verification.md`.
2. **`write_script(q, verification)`** — writes the script in the भाग format,
   with the style corpus (below) prepended. Runs on whatever `SCRIPT_LLM` says.
3. **`check_script(text, q)`** — mechanical checks, no model: digits in spoken
   lines, algebra in spoken lines, the year phrase, `त्रैमासिक परीक्षा`, the
   `मतलब` gloss, a focus cue, the fixed closing, भाग count, breath length.
4. Findings are fed back and the script is rewritten, up to `max_attempts`.

**The checks were validated against the two manually approved scripts in
`style/samples/`.** If a check fires on those, the check is wrong — three did,
and all three were bugs in the checker, not in the scripts. Keep that test:
when you add a rule, run it against the samples first.

Outputs per question, in `projects/<qid-slug>/`:

```
script_bhaag.md    the reviewable script — full question at the top, then भाग
script.md          the same thing converted to the pipeline's [narrator] format
verification.md    what NCERT says the sheet got wrong
accuracy_brief.md  (if a pack was built) the visual facts and banned errors
```

`to_pipeline_script()` does the conversion, and it is careful about one thing:
**on-screen formulas must never reach TTS.** They go into the director note
marked `ON SCREEN (exact, never spoken)`, never into the narration.

## 3. The style corpus is what makes it sound right

Three inputs, all in `style/`, all fed to the writer by `src/style.py`:

- **`samples/`** — the manually approved scripts, verbatim. These carry more
  weight than any written instruction. There are two; more is better.
- **`NOTES.md`** — the prose rules, loaded by `_read_notes()` and prepended as
  `HOUSE STYLE NOTES`. This file did not exist until the format was worked out;
  the writer had been running on samples alone.
- **`variations.yaml`** — approved phrasings per recurring moment (`year_hook`,
  `focus_cue`, `definition_opener`, `gloss`, `closing`), shuffled per video so
  ten scripts don't open identically.

`video style` prints what's loaded. The full written format, with worked
examples of how a sheet row becomes a script, is in `style/pyq_script_format.md`.

## 4. Then route: Manim or Veo — this decision matters

**Not every video should go through Gemini/Veo.** Classify by what the beats
have to *show*, not by subject:

| goes to | when the beats are | examples |
|---|---|---|
| **Manim** | equation chains, algebraic derivations, graphs with axes and intersections, geometric construction, schematic apparatus | Faraday's laws, कोलरॉश, क्वथनांक उन्नयन, first/zero-order kinetics |
| **Veo** | photoreal or organic imagery, texture, real-world objects | विटामिन deficiencies, संक्षारण (rust) |

Of the 16 scripts written so far, **11 classify as Manim**.

The evidence is inside the generated Veo packs: roughly half of every NEGATIVE
list exists only to suppress Veo's text failures — *"the proportionality sign
drawn as the Greek letter alpha"*, *"broken words split across lines"*, *"a
floating letter W"*. Manim renders `∝` correctly by construction. If a beat is
mostly notation, Veo is the wrong tool and the pack is fighting it.

### If Veo: the prompt pack

`src/frames.py` builds it:

```
research_visual_facts(script)   -> accuracy brief: what must be drawn correctly
select_anchor_beats(script)     -> 1–2 beats, never one frame per scene (cost)
generate_for_script(...)        -> the anchor frames (OpenAI images, ~$0.04 each)
build_prompt_pack_batched(...)  -> the segment prompts, in batches of 4
```

The pack is driven by `.claude/skills/video-prompt/`, the team's battle-tested
skill. Its `references/bug-ledger.md` records every visual bug and the rule that
fixed it — **read it before changing any prompt block.**

### If Manim

Working. Docker is not required and its image is currently broken anyway — the
local path is `brew install pkg-config`, Manim on Python 3.11, and **TinyTeX**
for LaTeX (`~/Library/TinyTeX`, no sudo, unlike BasicTeX's .pkg). Install
`standalone preview amsmath physics dvisvgm mhchem` via `tlmgr`.

Two things that will waste an hour if missed:

- **Compose the scene, don't import the helpers.** `compose_file()` inlines
  `manim_helpers.py` beneath a header that sets `THEME`, `CHROMA`, `ORIENTATION`
  and the frame size. A scene that does `from src.manim_helpers import ...`
  gets an 8x8 default frame, so `norm_point(0.5, 0.085)` lands at 37% instead
  of 8%, and no background image.
- **`chroma: none` for this track.** The green screen comes from HeyGen; Manim
  renders the full background. See CLAUDE.md.

`TransformMatchingTex` leaves unmatched source glyphs on screen — use
`ReplacementTransform`. `FadeOut` leaves the mobject in the scene, so captions
stack up as ghosts unless you `self.remove()` them.

### Rendering order: the avatar comes first

**The Manim video is rendered after the HeyGen clip exists, not before.** The
avatar's audio is the clock — each caption has to be the line being spoken at
that instant, and both clips must end together. Rendering to a guessed duration
puts the words on screen out of step with the words in the ear.

`src/avatar_sync.py` produces the timing plan:

```python
from src.avatar_sync import plan, write_plan
cues = plan("projects/<slug>/script_bhaag.md",
            "inbox/<avatar>.mp4",
            captions="inbox/<avatar>.srt",   # ask HeyGen for this — it is exact
            part=1)
write_plan(cues, "projects/<slug>/timing_part1.json")
```

With no caption file it apportions the measured duration by **syllable weight**,
not word count — Hindi word lengths vary far too much for words to work
("और" and "व्युत्क्रमानुपाती" are one word each).

**Screen layout is fixed.** The top strip carries the caption and nothing else,
readable but modest (~27pt, at most two lines) — every point it grows is space
the animation loses. Everything else on screen is animation, formulae,
derivation and labelling.

## 5. Backgrounds

`assets/backgrounds/{physics,chemistry,biology,maths}.png` at 1080×1920,
downscaled 4:1 from 8K originals (the originals live in `inbox/`, which is
gitignored — 130 MB).

Content must stay inside the top 60% *and* clear of the border art:

| plate | safe width | side margins |
|---|---|---|
| physics, chemistry | 702 px | 20% L · 15% R |
| biology | 648 px | 20% L · 20% R |
| **maths** | **594 px** | **30% L** · 15% R |

Maths is the tight one — its formulas bleed edge-to-edge and the top-left block
reaches 30% inward.

## 6. Delivery

Scripts go to Google Drive as Docs under `Scripts/<Subject>/`, and the link goes
into the sheet row.

- **The whole question goes at the top of the document** (`doc_header()`), so a
  reviewer can check the script against what was asked without opening the
  sheet. The count the question asks for — "तीन कारक", "दो अनुप्रयोग" — is the
  thing most likely to be under-delivered.
- **Sharing is set once on the parent `Scripts` folder** and inherited. The
  available Drive tools are read-only for permissions, so a human has to do it.

## 7. What things cost

Only OpenAI is billed; Claude runs on the CLI backend against a Max
subscription. `video spend` reads the ledger at `.usage/spend.jsonl`.

- anchor frames: ~$0.04 each, **1–2 per topic, never per scene**
- scripts: a few cents each on gpt-5
- accuracy briefs, anchor selection, prompt packs, Manim codegen: Claude, $0

## 8. Mistakes already made — do not remake them

- **Naming a thing in positive instructions is a signal to draw it.** A "LOGO
  SAFE AREA" block that said "logo" five times produced logos in both top
  corners. §16 is removed; never write logo/watermark/badge/wordmark into a
  prompt, *not even as a negative*. (`watermark` inside the base NEGATIVE list
  is the one documented exception.)
- **A pack is six or seven long calls.** Retry each one and flush after each —
  a single transient 529 once discarded 24 completed segments.
- **The image cache keys on a model-written prompt**, which differs every run,
  so it could never hit and re-runs silently paid twice. Prompts are cached in
  `frames/prompts.json`; seed it before re-running.
- **`SCRIPT_LLM` has to be read explicitly.** A bare `complete()` resolves to
  `auto` → the Claude CLI, so the configured provider gets silently ignored.
- **Hindi and formulas render by different paths.** Poppins covers Devanagari
  fully but has no Greek, subscripts or arrows; LaTeX has those but no
  Devanagari. Hindi → `Text()`, formulas → `MathTex()`, and never glue
  Devanagari inside a symbol (`E°सेल`).
- **Spoken lines carry no digits.** Years become Hindi words
  ("दो हज़ार पच्चीस"), values become English tokens ("two-ell"). Digits still
  appear on screen — the rule governs only the mouth.

## 9. Quick reference

```bash
video style                     # what voice reference is loaded
video spend                     # what the paid keys have cost
video status <project>          # pipeline state
video doctor                    # what this machine is missing
```

```python
from src.pyq_writer import load_questions, draft, to_pipeline_script
qs = load_questions("Chemistry")
text, checks, verification = draft(qs[0])
print(checks.ok, checks.findings)
```
