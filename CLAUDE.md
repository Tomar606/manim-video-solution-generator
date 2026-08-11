# Context for working on this repo

Read this before changing anything. It records *why* the pipeline is shaped the
way it is — the constraints that aren't visible from the code, and the decisions
that look arbitrary until you know what they're avoiding.

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

**The chroma zone is the presenter's box.** A script that reserves space with
`chroma: right_half` renders that half flat green with all content kept out; the
compositor then keys the presenter into exactly that region. `avatar.placement:
auto` reads it straight off the script. One concept, two stages.

**Repair loops instead of one-shot generation.** The renderer feeds Manim
tracebacks back to Claude; the script writer feeds voice-evaluation findings
back. Anywhere output can be checked mechanically, it gets checked and retried.

**Deterministic where variance is worthless.** Photo beats and the answer card
render from fixed templates in `src/scene_templates.py` — no model call, so they
look identical in every video.

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

## Layout

```
video.py              CLI — every stage
src/project.py        projects/<slug>/ + stage state (job.json)
src/script_parser.py  script format -> VideoScript
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
src/qc.py             Claude vision review of rendered frames
src/assemble.py       conform -> concat -> mix -> mux
src/dashboard.py      the browser editor (single self-contained page)
```

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
