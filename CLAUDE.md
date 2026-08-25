# Context for working on this repo

Read this before changing anything. It records *why* the pipeline is shaped the
way it is — the constraints that aren't visible from the code, and the decisions
that look arbitrary until you know what they're avoiding.

> **New here? Read [`PIPELINE.md`](PIPELINE.md) first.** It is the operational
> walkthrough: what to run, what the outputs mean, and the mistakes already made
> and fixed. This file explains *why*; that one explains *how*.

## Two tracks, one repo

The **reels track** is what most of this file describes: a topic string becomes
a landscape Hinglish video with Manim animation and a keyed presenter.

The **PYQ track** is the current focus and is documented in `PIPELINE.md`: one
row of an MP Board question sheet becomes a portrait Hindi script
(`src/pyq_writer.py`), reviewed as a Google Doc, then rendered either by Manim
or via a Gemini/Veo prompt pack. It shares `src/llm.py`, `src/style.py` and the
render/composite stages; it does **not** share the script format.

The routing decision between Manim and Veo is not cosmetic — see
"Route: Manim or Veo" in `PIPELINE.md`. Roughly two thirds of the PYQ scripts
written so far are equation and graph work, which Veo is actively bad at and
Manim renders correctly by construction.

## What this produces

An educational video: a written script → Manim animations → ElevenLabs narration
→ automatic sound effects → a chroma-keyed HeyGen presenter composited on top →
a final answer card. Roughly 1–3 minutes, landscape or portrait, Hinglish
narration.

It replaces a manual process: someone wrote the script, generated clips,
reviewed them by eye, then keyed and composited the avatar in an editor.

## The load-bearing ideas

**`script.md` is the source of truth.** Narration, timing, animation direction,
photos and the answer card all come from it. Every stage reads it. To change a
video you change the script and re-render — never patch generated scene code,
which is overwritten on the next run.

**Narration sets the clock.** Segment length comes from the *measured* length of
the synthesized audio, and everything downstream is conformed to it. That's why
`narrate` must run before `background`, and why you can't drag a clip to retime
it in the dashboard — the audio would no longer match.

**A beat is a clip; a stage is a track.** The dashboard is a timeline because
the pipeline already had that shape.

**The chroma zone is the presenter's box** — for the reels track. A script that
reserves space with `chroma: right_half` renders that half flat green with all
content kept out; the compositor then keys the presenter into exactly that
region. `avatar.placement: auto` reads it straight off the script.

**The PYQ track does the opposite: `chroma: none`.** HeyGen already delivers a
green-screened avatar, so painting green in Manim as well is redundant — it
discards real background and any despill error eats into the plate. The Manim
render carries the FULL background; the avatar clip carries the key. Content is
still composed inside the top 60% so the presenter never covers it, but that is
a layout convention now, not a painted zone.

**Repair loops instead of one-shot generation.** The renderer feeds Manim
tracebacks back to Claude; the script writer feeds voice-evaluation findings
back. Anywhere output can be checked mechanically, it gets checked and retried.

**Deterministic where variance is worthless.** Photo beats and the answer card
render from fixed templates in `src/scene_templates.py` — no model call, so they
look identical in every video.

## Every PYQ video goes through the visual director

`src/visual_director.py` decides what the student SEES at each moment. It is a
pipeline stage (`video beats <project>`), not an optional polish pass, and every
video built from now on runs through it.

The question it answers is *what visual would make this sentence easier for a
Class 12 Hindi-medium student to understand, remember, or reproduce in the
exam* — never *what graphic can I put here*. That second question is what
produced the version where the screen spent the whole video restating the
captions.

Three things follow from that, and all three are load-bearing:

- **"No graphic" is a valid answer.** On the dry-cell part the director chose a
  visual for 7 windows out of 58. A quiet moment with the presenter, the
  captions and a clean plate is correct whenever a graphic would not add
  understanding. `preflight` warns if almost nothing is left quiet, because
  that means the director has stopped choosing.
- **Screen text is not caption text.** Captions say what was said; the screen
  ORGANISES it — a heading, a list, a comparison. preflight warns when a block's
  words mostly repeat the caption underneath it.
- **The question's own wording sets the strategy.** सचित्र means the diagram is
  the spine; सिद्ध कीजिए means a derivation built step by step; लाभ/कारक/उपाय
  means a progressive list. `question_strategy()` reads this off the question
  and biases the whole part. preflight FAILS a part whose question demands a
  figure and has none — that shipped once.

What the director does **not** decide: which figure belongs to which question,
and when each of its labels is named. Those are judgements about the question
rather than about a sentence, so they stay hand-placed in the beats file and are
merged back in untouched.

Counted lists FILL IN rather than landing whole — every item ends up on screen
so the student has the map, with the one being spoken bright and the rest quiet.
Diagram labels work the same way, attached to a part BY NAME through an anchor
table so they survive the diagram being rescaled.

## Models: per-stage, on purpose

| Stage | Model | Why |
|---|---|---|
| Script writing | OpenAI (`SCRIPT_LLM=openai`) | team preference |
| Manim codegen + repair | Claude | long multi-turn repair loops |
| QC frame review | Claude (vision) | |

`src/llm.py` has three backends — `cli` (Claude Code CLI, billed to a Claude
subscription, **no API key**), `api` (Anthropic key), `openai`. Default is
`auto`: prefer the CLI, then Anthropic, then OpenAI. Any caller can override
with `provider=`.

**The CLI backend is why rendering is split.** The container has no Claude
login and the host has no Manim, but the repair loop needs both. So
`RENDER_BACKEND=docker` keeps Claude on the host and sends *only* the
`manim render` call into the container (`src/manim_render.py`).

## Gotchas that cost time

- **`src/dashboard.py` must not use `from __future__ import annotations`.**
  FastAPI resolves route signatures at runtime, and the fastapi types are
  imported inside `create_app()`. With postponed annotations every
  `Request`/`UploadFile` silently becomes a required query param — HTTP 422 on
  every POST and PUT. There's a comment at the top; don't "tidy" it away.
- **`src/scene_codegen.py` must not import `src.manim_helpers`.** It only needs
  the file's *path*; importing it drags Manim into every process, breaking the
  CLI and dashboard on machines without it.
- **Spoken lines must contain no digits or symbols.** They go to TTS verbatim.
  "paanch kilogram", never "5 kg". `src/script_eval.py` enforces this.
- **Photos are `Group`, not `VGroup`.** `ImageMobject` is not a `VMobject`.
- **macOS: `pip install manim` needs `pkg-config`** or pycairo fails to build,
  even with cairo installed.
- **Manim 0.18 needs Python 3.10–3.12.**
- **Hindi and formulas render by different paths and cannot be mixed.** Poppins
  (in `assets/fonts/`) covers Devanagari completely but has no Greek letters,
  no sub/superscripts and no arrows; LaTeX has all of those and no Devanagari.
  So Hindi goes through `Text()`, formulae through `MathTex()`, and Devanagari
  must never be glued inside a symbol (`E°सेल`). Getting this wrong gives tofu
  boxes one way and a LaTeX failure the other.
- **Pillow needs libraqm, or every Devanagari image is silently wrong.** Without
  it Pillow has no complex-script shaping: it draws the codepoints in storage
  order, so `विद्युत्` comes out `वदि्युत्` and `नियम` comes out `नयिम` — the
  `ि` matra sitting after its consonant instead of before it. Nothing errors,
  and it is easy to read past. This bites `EndScreenshot`, whose typeset temp is
  the reference the image model copies, so a garbled temp becomes a garbled
  answer card. Check with `PIL.features.check("raqm")`; fix with
  `brew install libraqm` then `pip install --force-reinstall --no-binary Pillow
  --no-build-isolation pillow` (Pillow 12 also needs `pybind11` present first,
  and `--no-binary :all:` instead of `--no-binary Pillow` will sit for half an
  hour building every build dependency from source).
- **Never write "logo", "watermark", "badge" or "wordmark" into a generation
  prompt — not even as a negative.** Naming a thing is a signal to draw it; a
  block that said "logo" five times while asking for empty corners produced a
  logo in both corners. See `.claude/skills/video-prompt/references/bug-ledger.md`.
- **A bare `complete()` resolves to the Claude CLI**, so `SCRIPT_LLM` is
  ignored unless a caller passes `provider=` explicitly.
- **A generated clip carries the animation and NOTHING else.** No text in any
  script (Veo cannot set Devanagari, so labels are typeset by
  `src/veo_labels.py` and composited over the top), and no decoration — no
  border, vignette, sparkle, lens flare or title card. Say it positively in the
  prompt and enumerate it in the NEGATIVE list, never the other way round.
- **A Veo clip's background is UPLOADED, not described.** The subject plate goes
  into Flow itself, so the clip is generated on the same picture Manim renders
  and can be spliced into the middle of a part invisibly. Describe a background
  and Veo builds its own, discards ours, and the splice reads as a jump cut.
- **Consecutive generated clips do not match unless you make them.** Veo
  remembers nothing between generations, so the same prompt on the same plate
  builds a slightly different apparatus every time — a shade greener, two
  millimetres wider, lit from the other side. Each clip passes its own review;
  the sequence is what is broken. Beats sharing a `sequence` id are generated
  from the previous clip's final frame (`src/veo_sequence.py`) and the seam is
  graded before the clip is accepted. And a **rejected** clip is never carried
  forward — propagating a frame the review just condemned makes one bad
  generation into five, while looking *more* consistent than the correct
  version.
- **A generated clip is never reversed to make it longer.** Boomerang is the
  obvious way to stretch eight seconds over fifteen and it teaches rust
  un-rusting and gas dissolving back into an electrode — wrong in a way that
  looks completely fine to anyone not paying attention. `src/veo_conform.py`
  slows, loops or holds instead, chosen by the beat's `motion`.
- **`tpad` after `minterpolate` needs an `fps` between them.** minterpolate emits
  timestamps off the 1/FPS grid, so the cloned pad frames land past where `-t`
  cuts: the pad is generated and immediately discarded, and the clip comes out a
  tenth of a second short of its window. Cost an hour; measured at 7.87s where
  8.00s was asked for.
- **Model-written prompts break caches.** `src/frames.py` keys its image cache
  on the prompt, but the prompt itself is generated, so it differs every run and
  never hits. Prompts are cached in `frames/prompts.json` — seed it before any
  re-run or you pay for the same frame twice.

## Layout

```
video.py              CLI — every stage
src/project.py        projects/<slug>/ + stage state (job.json)
src/script_parser.py  script format -> VideoScript
src/pyq_writer.py     question sheet -> verified Hindi PYQ script
src/script_edit.py    write a single beat back to script.md losslessly
src/script_writer.py  topic -> draft, with the voice repair loop
src/script_eval.py    "does this sound spoken" checks
src/style.py          house voice, learned from style/samples + variations.yaml
src/scene_codegen.py  Claude codegen + render-repair
src/scene_templates.py fixed scenes (photo beats, answer card)
src/manim_helpers.py  injected scaffolding: theme, chroma, photos, sound cues
src/manim_render.py   render locally or inside the container
src/sfx.py            synthesized effects + cue mixing
src/avatar.py         briefs, manual drop, HeyGen provider
src/composite.py      chromakey + despill + placement
src/veo.py            the Flow route: one beat -> a checked, fitted clip
src/veo_prompts.py    writing that beat's prompt, and revising it when it fails
src/veo_qc.py         grading the frames, and where a clip stops being usable
src/veo_sequence.py   carrying a clip's final frame into the next generation
src/veo_conform.py    cutting the hallucinated tail, fitting the rest to the window
src/veo_labels.py     the Devanagari labels that go over a generated clip
src/flow_bridge.py    the local half of the browser bridge
flow/extension/       the Chrome extension that drives Flow in a background tab
src/qc.py             Claude vision review of rendered frames
src/assemble.py       conform -> concat -> mix -> mux
src/dashboard.py      the browser editor (single self-contained page)
```

See also `PIPELINE.md` for the operational flow.

`projects/<slug>/` holds one video. Everything except `script.md` and `assets/`
is regenerated.

## State of things

**Verified working:** script generation and voice scoring, image/photo beats and
the answer card, sound-effect cues and mixing, chromakey compositing (checked on
a real frame), avatar briefs and ingest, QC vision review, the CLI, the dashboard
including single-beat editing round-trip.

**Written but unverified — no credentials yet:** the HeyGen client
(`src/avatar.py`) and the OpenAI backend (`src/llm.py`). Both fail loudly with
the raw API response rather than guessing, so the first real run says exactly
what to fix.

**Never yet run end-to-end:** the actual Manim render. It needs the Docker image
or a local Manim+LaTeX install; the machine this was built on had neither and
ran out of disk mid-build.

## Conventions

- Don't hand-edit `manim_code/`, `work/`, `media/`, `final/` — build output.
- Don't commit `.env`, rendered media, or `projects/*/` output.
- New stages go through `video.py` so the CLI, dashboard and Claude Code skills
  all get them at once.
