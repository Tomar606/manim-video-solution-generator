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

### A third route: one beat goes to Veo, the rest stays in Manim

The table above is a whole-video decision, and it is the wrong grain for the
common case — a part that is entirely Manim work except for one moment where
something has to be seen *moving* and no amount of Manim will show it. Rust
creeping across wet iron. Gas bubbling off an electrode. Tissue swelling under
osmosis. Those are photoreal and organic; everything around them is still
equations and a labelled diagram.

So a single beat can be routed to Flow on its own:

```json
{"at": 21, "type": "video", "brief": "rust creeping outward across a wet iron nail,\n            the bright metal going orange-brown from the wet edge inward",
 "seconds": 12, "motion": "one_way", "presenter": "hidden",
 "labels": [{"at": 23, "text": "जंग की परत", "x": 0.42, "y": 0.62}]}
```

Then `video veo <project> --part 1`. Per beat it writes the prompt, audits it
before spending a credit, attaches the subject background plate, submits it to
Flow through the browser, waits, downloads the clip, grades its frames, and
revises and regenerates up to three times. Manim draws nothing at that beat;
`tools/composite.py` lays the clip over those frames.

**`brief` is hand-written, like a figure.** Which moment deserves a generated
clip is a judgement about the question, not about a sentence, so the visual
director does not decide it — the same reasoning that keeps `apparatus` and
`scan_figure` hand-placed.

Four rules the route is built around, each enforced in more than one place:

- **The background is attached, not described.** `assets/backgrounds/<subject>.png`
  is uploaded into Flow itself, so the clip is generated ON the plate Manim
  renders. That is what lets it be spliced into the middle of a part without a
  visible cut. Describing a background in words guarantees a mismatch; skill §15
  says so, `audit()` refuses a prompt that does not reference the supplied
  image, and check B of the visual review compares the first and last frame for
  drift.
- **The clip carries the animation and nothing else.** No text in any script, no
  numerals, no equations — and no decoration either: no borders, vignettes,
  sparkles, lens flares or title cards. Stated positively in the prompt,
  enumerated in the NEGATIVE list (never in the body — naming a thing is a
  signal to draw it), and graded as checks A1 and A2.
- **Labels are ours.** Veo cannot set Devanagari, so `src/veo_labels.py` typesets
  them in Khand and the compositor lays them over the clip — which also means
  each one arrives on the caption that names it, as everywhere else in this
  track. A label below 50% is flagged, because the presenter is there.
- **The clip is fitted to the presenter, never the reverse.** Flow returns a
  fixed ~8s; the window is however long the teacher talks. The review reports
  where the clip stops being correct — Veo is usually right at the start and
  drifts — that tail is cut, and the good part is slowed, looped or held to fill
  the window, chosen by the beat's `motion`. **It is never reversed:** boomerang
  would double the length and teach rust un-rusting.

Outputs: `clips_part<N>.json` (tracked — the decision record), `veo/` (the clips
and every rejected attempt, gitignored), `veo_review_part<N>.json`.
`tools/preflight.py` FAILS a part with an ungenerated video beat, because the
render would have a hole in it. Setup is in [`flow/README.md`](flow/README.md).

### If Veo for the whole video: the prompt pack

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

- **`\;` in a regex is a bare semicolon, not LaTeX's thin space.** A cleanup
  pass meant to strip `\quad`, `\,`, `\!` and `\;` from the sheet's LaTeX
  deleted **every semicolon in the prose** of all 14 chemistry scripts — 219 of
  them — leaving double spaces mid-sentence. Escape it as `\\;`. More
  generally: a cleaner that edits delivered text needs its own before/after
  diff, because the damage reads as ordinary whitespace.

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

## 10. Avatar-synced videos (the PYQ Manim track)

A video whose clock comes from a **real HeyGen clip** rather than from
synthesized narration. The audio already exists and cannot be changed, so every
stage conforms to it. Tooling: [`tools/`](tools/README.md).

`projects/faraday-electrolysis/` and `projects/sanksharan/` are the two worked
examples; their scene files are **hand-written source**, not build output, and
are committed.

### The order that matters

`transcribe` → `captions_from_audio` → `calibrate_key` → `recompose` → render →
`avatar_windows` → `composite`.

### Mistakes already made here

- **Captions must come from the AUDIO, not the script.** A shoot mixes lines
  from the current script, an earlier draft, and paraphrase. The approved
  Faraday master covered only 51% / 58% of what its own clips actually say, and
  whole sentences — including the formal statement of the first law — played
  under a caption showing something else. Diagnose with
  `tools/align.coverage()`, and note it must be measured **audio→text**:
  script→audio looks fine even when the script is the wrong draft, because
  every script line does appear somewhere.
- **`chromakey` cannot key this green screen.** It is lit unevenly (value
  0.67–0.99 within one frame), so a tolerance wide enough for the dark side also
  matches skin midtones — 8.3% of the presenter's face was transparent with the
  background showing through. The key is `hsvkey` on **hue**, which does not
  drift with lighting, applied twice at different value references and combined
  with `blend=darken`. Calibrate per clip: the three clips so far needed three
  different settings.
- **Despill leaves a dark olive rim** on hair unless the alpha is eroded twice
  first; that ring is spill-contaminated pixels, not subject.
- **`overlay=format=yuv420` destroys alpha.** Stay RGBA until the final
  `format=yuv420p`.
- **One caption line at a time.** A whole sentence held while only its first
  half is spoken reads as out of sync even when correctly timed. The caption
  track is a flat `{start, text}` list on its own clock, deliberately *not*
  keyed to the animation cues, and `self.play` is overridden so a long animation
  cannot hold a stale line.
- **Wrap captions on measured width, not character count.** Devanagari conjuncts
  are not equal width; a character-count wrap ran captions to the frame edge
  with zero margin.
- **The stage band's top is not a constant.** It is derived from the current
  caption's actual bottom, or a three-line caption collides with the animation.
- **`scale` cannot resize per frame and `zoompan` destroys alpha.** The
  presenter's shrink is two complete composites blended by a time expression.
  It is slow (~40 min for a 90s part); skip the windows argument when not needed.
- **`--max-turns 1` on the Claude CLI loses the whole response** if the model
  reaches for a tool: the denial consumes the only turn and it returns
  `error_max_turns` with no text. `src/llm.py` allows 6.

### PYQ script rules learned the hard way

- **The assigned hook mechanism must be the actual first line.** Every approved
  sample opens on the board/year line because they happen to use `exam_fomo`, so
  the model copies that opening for every topic and still reports the assigned
  mechanism in its META. Five physics scripts opened with the identical
  sentence. `check_script(hook_mech=...)` now fails that.
- **Record the decision, not the model's echo.** History drove hook rotation off
  the META line, which drifts, so `problem` came up three times running and the
  rotation never rotated. `draft()` records what was *asked for*.
- **Every part after the first opens with a bridge.** Parts publish as separate
  clips. `BRIDGE_RE` enforces it — and it must accept the many ways to word one
  ("पिछले हिस्से में", "अब तक हमने"), or the repair loop oscillates forever
  fixing a bridge that was already there.
- **A whole-script repair regresses.** Fixing the opening rewrites the script and
  restores the sample's opening. Splice single lines in with code instead.
- **Keep the best draft.** A repair pass can fix one finding and introduce two.
- **`estimate_parts` measures the FIRST draft**, but writing it as parts makes it
  longer; re-measure until the count settles or the part plan comes up short.
- **Multi-letter Latin in a spoken line is read as an English word** by TTS
  (`dS`, `dl`, `cos`). Write them as said: "डी-एस", "कॉस". *Single* letters are
  fine — the approved samples say `W₁` and `W₂` aloud.

---

## PYQ video build — what this session added

Everything below is wired into `tools/preflight.py`, so a build cannot get past
a defect these describe. Run `python tools/preflight.py <slug>` before rendering.

### Figures come from the question's own textbook page
`tools/figure_from_scan.py` — the sheet's column 11 holds a Mathpix scan of the
page each question came from. The figure in the video is traced from that scan
with `potrace`, not generated and not redrawn: three attempts at generating the
Berkeley–Hartley apparatus each produced a plausible but *different* machine.
The trace threshold is per-scan (Berkeley 118, dry cell 80) — always look at the
`_preview.png`. Scanned labels are erased and re-typeset; the book's leader lines
are kept.

`--heal` reconnects strokes an erase box cuts, and `hide` zones in a beat drop a
traced word at the mobject level (with a size guard, or it deletes the curve the
word sits on).

### Every diagram label must be spoken
`tools/check_labels.py` proves each label is named by the audio at the moment it
appears. The default cue is the label's LONGEST word — matching on any word let
`दाब मापक` pass against a caption that merely said दाब. Parts the narration never
names (`दाब मापक`, `धातु की टोपी`) must be declared `"spoken": false` and appear
WITH the figure, never at a later caption.

### Overlaps are prevented, not reported
The layout guard used to compare only top-level blocks, so a collision *inside*
one block was invisible — which is why `t½` printed through `समय (t)` for weeks.
It now compares every text mobject on the stage against every other, names both
offenders, and `keep_clear()` resolves collisions at build time.

`clamp_to_band()` pulls late-added elements (diagram labels, formula focus
boxes) back inside the band — they never went through `place()`.

### The stage band is derived from the compositor
`STAGE_BOT = 0.492` because `tools/composite.py` puts the presenter at
`FULL_Y = 966` of 1920, i.e. his head starts at 0.503. The band used to run to
0.600 — a hundred pixels *inside* him. If the compositor's placement changes,
this must change with it.

### `place()` grows as well as shrinks
It only ever scaled down, so a short block kept its authored font size inside a
388px band: fine on a desktop preview, too small on a phone. It now grows blocks
to fill the band, capped at `MAX_GROW`.

### No dead screen
`tools/visual_gaps.py` reports any stretch over 3s with nothing on the stage
(there were 111 seconds across the first six videos — the band clears when the
question card comes down and nothing replaces it). `tools/fill_visual_gaps.py`
fills them with a captioned photograph of the actual substance or apparatus.
`tools/example_images.py` does the same where the teacher names a real object.

Both generate on a keyable ground and cut it out, because gpt-image-2 refuses
`background="transparent"`. Opaque subjects use magenta; **glassware must use the
grey path** — magenta shows *through* the glass and the key takes the liquid with
it, leaving a pink hollow beaker. Both are pinned to 1024x1024 / medium quality:
these sit behind a talking presenter and the larger sizes buy detail nobody sees.

### The answer page arrives on its cue
`tools/answer_overlay.py` finds "स्क्रीन पर आ" in the caption track and holds the
page from there to the last frame, fitted to frame width (the pages are 2:3 and
the frame is 9:16 — covering would crop the ends off every handwritten line).
Blank ruled sheets in a page set are detected and skipped.

**Not every video should get one.** The replacement endings say the answer is on
the *notes button*; overlaying a page there contradicts the narration. Check what
the clip actually says.

### Replacement endings
Cut the original at the caption where the new ending re-records the same line,
then composite the ending with `windows=[[-1.0, 0.375]]` so the avatar starts at
the geometry the original holds at the cut and eases to centre — otherwise he
jumps in size and position and the edit is obvious.

### Traps that cost time here
- **The sheet's IDs are not the only IDs.** An older sheet numbered chapter 2 and
  3 differently; answer pages and ending clips follow the new one. Match on the
  QUESTION TEXT when they disagree.
- **Clip filenames lie.** Two vitamin clips were filed by name and turned out to
  be different questions — the year each part 1 speaks ("ये सवाल 2018 में") is
  in the sheet and settles it. Check before building.
- **Devanagari inside `MathTex` kills the render.** Put the Hindi in the beat's
  label. Preflight now fails it.
- **LaTeX markup in a `points`/`flow`/`compare` item prints literally** — those
  render through `Text()`. Wrap maths in `$...$`.
- **Two parts of one project cannot render in parallel** — they share
  `media/partial_movie_files` and clobber each other. Parallelise across
  projects.
- **The card's year is digits; the narration's year is words.** They are not the
  same field.
- **Compositing is single-threaded** (189s with the CPU 84% idle). Run three at
  once.

---

## Presenter geometry — measured, never assumed

Two constants controlled how the presenter was placed, and both were measured
off a single shoot. Every later clip inherited numbers that were wrong for it.

**The crop.** `crop=650:930:650:150` was hardcoded. The true extent measures 680
to 886 px across one batch, so the fixed window sliced a forearm off at a hard
vertical edge whenever he stood or gestured wider. `tools/avatar_crop.py`
measures it per clip: it samples frames, keys the green the same way the
compositor does, and takes the largest connected non-green region touching the
bottom of the frame. Plain "not green" returns the whole frame — the shoot has a
whiteboard and stands outside the screen.

**The vertical anchor, which is coupled to the crop.** `FULL_Y = 966` was a fixed
TOP offset. The avatar is scaled to a fixed on-screen WIDTH, so a wider crop
scales to a SHORTER avatar — and with a fixed top he floats clear of the frame
edge. The top is now derived from the scaled height so his feet land on 1920
whatever the crop measures: the crop sets his SIZE, never his POSITION. The crop
also always extends to the bottom of the source, because he is standing on it.

Fixing the crop without the anchor produced a floating presenter across a whole
rebuild. They are one change, not two.

**A third size.** Stretches with nothing on the stage no longer get a filler
image — the presenter grows into them instead (`biggrow_part<N>.json`, 81% wide).
An image is placed only where the narration dwells on that object as its own
subject; a gap sits over the hook and the exam framing, which is the one place
in a video where no object can earn a picture.

## Screen that is dead in two different ways

`tools/visual_gaps.py` reports both:

- **EMPTY** — nothing on the stage.
- **FROZEN** — one block unchanged for 20s+ while the teacher keeps talking. The
  Daniell cell held one comparison table for 59 of its 112 seconds, straight
  through the passage about ions moving. Nothing detected it, because something
  *was* technically on screen.

Arrivals count as movement: `reveal_at` items, figure `labels[].at`, formula
steps. Without counting labels a fully annotated diagram reads as frozen.

`tools/scene_script.py <slug>` prints the plan as text — every block, what
arrives when, the words spoken over it, and a **Needs a decision** section
listing every EMPTY and FROZEN stretch. Read it before rendering: every visual
change made after watching a composite costs a full render and composite.

## The script is the teaching plan

`script_bhaag.md` carries `On Screen:` directions. Authoring beats from the
transcript alone dropped the middle of a derivation — शून्य कोटि's script
specifies 8 steps for part 1 (separation of variables, the integral, the units)
and the built video jumped from the rate law to the answer, so `k = x/t` appeared
with `x` undefined and the next beat substituted `[A]` into an equation that did
not contain it.

Read the script first; the transcript is the CLOCK and the arbiter of what was
actually said. A derivation GROWS one line at a time — 16 separate screens loses
the student; pace around 10-15s per step.

## More traps found the hard way

- **Editing a running bash script corrupts it.** Bash reads incrementally; an
  edit mid-execution killed a queue partway through. Runners execute from a
  frozen copy.
- **`pkill` on a parent leaves orphaned children.** An orphan plus a new runner
  meant two workers on the same project — the memory spike that killed the
  user's apps AND the partial-file collision. The runner takes a lock.
- **ffmpeg unbounded took 320% CPU and ~600MB.** Capped via `FFMPEG_THREADS`
  (x264 holds a frame buffer per thread, so the cap bounds memory too).
- **A full disk fails renders silently.** Manim wrote nothing and reported
  success; a fix appeared not to work for an hour. Check `df` before blaming code.
- **`$...$` maths support must exist in EVERY text renderer.** It was added to
  `compare` only, so `points` printed `$\Delta T_b = T_b - T_b^{0}$` verbatim.
- **Conditional reveal state is order-dependent.** "Dim anything brighter than
  0.5" made list item ① vanish outright when ② arrived. Set every item's state
  explicitly from its reveal time.
- **A question printed into the sheet PNG can overflow the paper.** The shrink
  loop stops at a legibility floor and used to print anyway, running off the torn
  edge onto the background. It now truncates with an ellipsis.
