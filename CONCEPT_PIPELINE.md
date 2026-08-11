# Concept & Derivation Video Generator

The **new** pipeline (`generate.py`). You submit an authored **script** — narration
+ equations, with multiple speakers — and it produces a clean, themed explainer
video: Manim animations over a config-driven background, multi-voice ElevenLabs
narration, optional chroma-key zones, in **landscape or portrait**.

> This lives alongside the original question→solution tool (`main.py`), which is
> unchanged. New work happens here.

```
authored script (.md)
      │  parse (frontmatter + tagged body)
      ▼
[1] ElevenLabs TTS  ── per line, per speaker ──►  measured clip durations
      │
[2] Claude (Opus 4.8) per segment ──►  Manim scene  ──►  render
      │                                    ▲   │
      │            render-repair loop ◄─────┘   │ (traceback fed back on failure)
      ▼
[3] conform each clip to its audio length ► concat video ► concat audio ► mux
      ▼
   final .mp4  (landscape 1920×1080  or  portrait 1080×1920)
```

## Why it's built this way

- **Claude everywhere** for reasoning + Manim codegen, with a real **render-repair
  loop**: a scene that crashes at render time has its traceback fed back to Claude
  to fix (up to `--max-attempts`, default 4). Syntax is checked before spending a
  render. (The original tool only `ast.parse`d and failed late.)
- **Timing is driven by real audio.** Each line is synthesized first; its measured
  duration sets the segment's target. Every rendered segment is then *conformed* to
  exactly that length in post — so A/V stays locked regardless of animation timing.
- **Backgrounds are injected, not re-invented.** A fixed scaffolding
  (`src/manim_helpers.py`) paints the theme background, chroma zones, and a safe
  drawing area; it's prepended to every generated scene. Consistent backgrounds mean
  seamless cuts and less for the model to get wrong.
- **Orientation-native.** Landscape and portrait set real Manim frame + pixel
  dimensions; the safe-area math and `fit_safe` helper keep content on-screen in the
  tall/narrow portrait frame.

## Script format

YAML frontmatter, then a tagged body:

```markdown
---
title: Deriving the Quadratic Formula
orientation: landscape          # landscape | portrait
theme: midnight                 # named theme, or an inline brandable mapping
chroma: none                    # none | lower_third | bottom_half | left_half | ...
speakers:
  narrator: { voice: Rachel }   # ElevenLabs voice name or voice_id
  student:  { voice: Josh }
---

[narrator] We begin with the general quadratic equation.
$$ a x^2 + b x + c = 0 $$

[student] Where do we start?

[narrator] Divide through by a.
%% highlight the leading coefficient
$$ x^2 + \frac{b}{a} x + \frac{c}{a} = 0 $$
```

Body rules:
- `[speaker] text` starts a segment; text runs until the next tag.
- `$$ … $$` (may span lines) and `\[ … \]` become that segment's **equations**;
  everything else is spoken **narration**.
- `%% …` inside a segment is a **director note** (not spoken, passed to the model).
- Speakers used but not declared are auto-created (fall back to a default voice).

### Brandable / inline theme

`theme:` can be a mapping that names a base and overrides any field:

```yaml
theme:
  base: midnight
  accent: "#FF3366"
  font: "Poppins"
  background: "#0A0A12"
```

Built-in themes (see `src/themes.py`): `midnight`, `charcoal`, `slate-grid`,
`deep-space`, `blackboard` (dark); `ivory`, `paper-grid` (light).

### Chroma-key zones (for compositing)

Render a flat green (or blue) region so an editor can key it out and drop in a
presenter or graphics. Content is automatically kept out of the keyed region.

```yaml
chroma: lower_third              # preset region
# or, granular:
chroma:
  preset: bottom_half
  color: "#00FF00"
  animate_in: true               # transition the zone in mid-scene
  # rect: [0.0, 0.66, 1.0, 0.34] # custom normalized region (top-left origin)
  # safe: [0.0, 0.0, 1.0, 0.66]  # custom safe area
```

Presets: `lower_third`, `upper_third`, `bottom_half`, `left_half`, `right_half`,
`full`, `custom`.

## Usage

```bash
cp .env.example .env         # add ANTHROPIC_API_KEY and ELEVENLABS_API_KEY
docker-compose build

# Default sample:
docker-compose run --rm manim-video-generator \
  python generate.py scripts/quadratic_formula.md

# Overrides (no script edit needed):
docker-compose run --rm manim-video-generator \
  python generate.py scripts/quadratic_formula.md \
    --orientation portrait --theme charcoal --chroma lower_third --animate-chroma
```

CLI flags: `--orientation`, `--theme`, `--chroma`, `--chroma-color`,
`--animate-chroma`, `--continue-on-error`, `--max-attempts`, `--output`.

Output lands in `output/final/`; intermediates (per-segment `.py`, renders,
narration, conformed clips) are kept under `output/` for debugging.

## Offline mode (no Anthropic key)

Scene codegen normally uses Claude. If you don't have an Anthropic key, you can
supply **pre-written** scene files and render with **only** your ElevenLabs key —
Claude is skipped entirely (so is the render-repair loop; a scene that fails to
render is reported, not auto-fixed).

Put one file per segment in a directory, each a full
`class SegmentScene(ThemedScene):` using the same helpers, named
`segment_000.py`, `segment_001.py`, … (indices match the parsed segments):

```bash
docker-compose run --rm manim-video-generator \
  python generate.py scripts/quadratic_formula.md \
    --scenes-dir scenes/quadratic_formula
```

A worked example set ships in `scenes/quadratic_formula/` (9 scenes for the
sample script). Each scene only writes the animation; the header + background +
chroma + safe-area scaffolding is still injected automatically.

## Module map

| File | Role |
|------|------|
| `generate.py` | CLI entrypoint / orchestration |
| `src/config.py` | orientation, resolution, chroma zones, render settings |
| `src/themes.py` | theme library + brandable resolution |
| `src/script_models.py` | dataclasses (`VideoScript`, `DialogueSegment`, …) |
| `src/script_parser.py` | frontmatter + tagged-body parser |
| `src/tts_elevenlabs.py` | multi-voice narration, measured durations |
| `src/manim_helpers.py` | injected scaffolding: background, chroma, safe area, `ThemedScene` |
| `src/scene_codegen.py` | Claude codegen + **render-repair loop** |
| `src/manim_render.py` | orientation-aware Manim rendering |
| `src/media.py` | ffmpeg/ffprobe: conform, concat, mux |
| `src/assemble.py` | conform → concat → mux |
| `src/llm.py` | Claude client wrapper |

## Status / not yet wired

- Cross-segment equation continuity is passed to the model as context (prior
  equations shown de-emphasized); it is not yet a shared persistent object.
- ElevenLabs voice resolution matches by name against your account library, or
  accepts raw voice IDs; set `ELEVENLABS_DEFAULT_VOICE` as a fallback.
- Requires running in the Docker image (Manim + FFmpeg + LaTeX). Local Python
  3.14 is fine for parsing/config but Manim renders in the container.
