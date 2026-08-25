# Arivihan video pipeline

Turns one exam question into a finished portrait video: a question card, an
animated explanation with Hindi captions, and the presenter keyed on top.

```
question ──► script ──► HeyGen clip ──► transcript ──► captions ──► scene plan
                                            │                           │
                                            └── sets the clock ─────────┘
                                                                        ▼
                        final.mp4 ◄── gate ◄── composite ◄── render ◄── plan
                                                    ▲
                                        presenter clip (chroma-keyed)
```

The presenter's recorded audio is fixed and cannot be changed, so **everything
else conforms to it**. Word-level timings come out of the clip first, and every
caption, every reveal and every animation cue is placed against them.

---

## The two tracks

| | **PYQ track** — what we build now | **Reels track** — older, still wired up |
|---|---|---|
| input | a row of an MP Board question sheet | a topic string |
| clock | the presenter's recorded audio | synthesized narration |
| entry point | [`tools/`](tools/) + [`tools/edu/`](tools/edu/) | [`video.py`](video.py) |
| read | [tools/README.md](tools/README.md) | [PIPELINE.md](PIPELINE.md) |

Both share `src/llm.py`, `src/style.py` and the compositor. They do **not**
share a script format.

---

## Setup

Three environments, on purpose. Manim 0.18 pins an old numpy and whisper wants a
new one; whichever is installed second downgrades the other and one of the two
stops importing.

```bash
# 1. Manim (rendering only).  Python 3.10-3.12; 3.13 will not build Manim 0.18
python3.11 -m venv .venv-manim  && .venv-manim/bin/pip install manim

# 2. Everything else: whisper, pillow, the gates, the compositor
python3.11 -m venv .venv-tools  && .venv-tools/bin/pip install -r requirements-tools.txt

# 3. The HTML renderer (only if you use that route)
cd tools/edu/renderer && npm install && npx playwright install chromium
```

Also needed: **ffmpeg**, **LaTeX**, and on macOS `pkg-config` (pycairo will not
build without it) and `libraqm` (without it Pillow silently mis-shapes every
Devanagari image — see [CLAUDE.md](CLAUDE.md)).

Copy `.env.example` to `.env` and fill in the keys you need. The Claude CLI
backend needs no key at all and is the default.

---

## Building one video

### Step 1 — the clip decides everything

```bash
# word-level timings; everything downstream derives from this
.venv-tools/bin/python tools/transcribe.py inbox/<clip>.mp4 \
    projects/<slug>/words_part1.json
```

Check the output covers the whole clip before going on. Whisper drops stretches
silently — it swallowed 15 seconds of one clip and emitted it as a single
15-second "word", and the captions had a hole in them for a whole section. A
word longer than about two seconds is that bug.

### Step 2 — captions: the transcript gives the clock, the script gives the words

```bash
PYTHONPATH=. .venv-tools/bin/python tools/captions_from_audio.py \
    projects/<slug>/words_part1.json \
    projects/<slug>/script_master.md \
    projects/<slug>/lines_part1.json
```

`script_master.md` must be **the draft that was actually recorded**. An earlier
draft looks close enough to pass review and puts the wrong wording on screen.
Coverage below ~0.80 in the tool's output means they disagree — look by hand.

### Step 3 — plan the scene, then check the plan

Two render routes. Pick by what the question needs.

**A. Manim route** — the default, and the whole job in one command:

```bash
bash tools/build_one.sh <slug> b2
```

That runs, in order: machine check → plan check → render → layout gate →
presenter windows → composite → answer page → output gate. It stops before
delivery so you can look at it.

**B. HTML route** ([tools/edu/renderer/](tools/edu/renderer/)) — a Chromium page
rendered frame by frame. Better for captions, typeset equations and hand-drawn
SVG figures; no LaTeX install needed.

```bash
cd tools/edu/renderer
python3 build_dry.py 1          # writes spec/segments.json from the caption track
python3 validate.py             # the plan on paper
node qa.mjs                     # the plan in a real browser, frame by frame
node shots.mjs 4:5.0 9:6.0      # stills at chosen moments — look before rendering
OUT=out/part1.mp4 node full.mjs # ~2.5 min per 2 min of video
```

> `build_dry.py` holds the plan for **one specific video** in a table at the top
> — which figure part appears at which second, where each label sits. Copy it
> and rewrite that table for the next question; the machinery below it is
> general.

### Step 4 — put the presenter on

```bash
FFMPEG_THREADS=2 PYTHONPATH=. .venv-tools/bin/python tools/composite.py \
    background.mp4 inbox/<clip>.mp4 projects/<slug>/keys/part1.json \
    projects/<slug>/final/<slug>_part1.mp4 \
    - projects/<slug>/presenter_part1.json - - \
    projects/<slug>/crop_part1.json projects/<slug>/card_part1.json
```

The trailing arguments are positional; `-` means "skip this one". They are, in
order: shrink windows, presenter-hide windows, Veo clips, grow windows, the
measured crop, the question-card window.

### Step 5 — the answer page, then the gate

```bash
.venv-tools/bin/python tools/answer_overlay.py projects/<slug> 2 answer.png
.venv-tools/bin/python tools/output_gate.py projects/<slug>/final/<file>.mp4
```

### Adding to a finished video

If something needs to go into empty screen space **after** the video is done,
do not re-render — lay it on top:

```bash
.venv-tools/bin/python tools/burn_chips.py in.mp4 out.mp4 plan.json
```

One ffmpeg pass, audio copied through untouched, the approved picture
undisturbed.

---

## The gates

Every one of these exists because the defect it catches shipped at least once.
Defects fixed only in source came back; defects behind a gate did not.

| gate | runs | refuses |
|---|---|---|
| [`machine_ready.py`](tools/machine_ready.py) | before anything | starting when swap or disk is exhausted — renders die silently and the machine stops responding |
| [`preflight_beats.py`](tools/preflight_beats.py) | before rendering | a plan with maths glued into Devanagari, a figure a "सचित्र" question demands and does not have, labels that are never spoken |
| [`validate.py`](tools/edu/renderer/validate.py) | before rendering | a spec with caption gaps, unknown SVG ids, or a golden word that isn't in its phrase |
| [`qa.mjs`](tools/edu/renderer/qa.mjs) | before rendering | overlapping labels, anything crossing the presenter's line, a diagram element that never becomes visible |
| [`layout_gate.py`](tools/layout_gate.py) | before compositing | text on text, content out of band, content off screen |
| [`output_gate.py`](tools/output_gate.py) | before delivery | a floating or off-centre presenter, audio drifting against picture, the wrong frame rate |

**Look at stills before you render, and at frames before you deliver.** A
two-minute render costs three minutes; a wrong one costs an hour.

---

## Layout

```
video.py               reels-track CLI — every stage
src/                   the reels track: script writing, codegen, QC, assembly
tools/                 the PYQ track: transcript, captions, gates, compositor
  transcribe.py          word timings from a presenter clip
  captions_from_audio.py transcript for the clock, script for the words
  composite.py           chromakey, despill, presenter geometry
  build_one.sh           one video, Manim route, all gates in order
  burn_chips.py          additions laid onto a finished file
  edu/renderer/          the HTML route: engine.js, specs, SVG figures
flow/                  the Chrome extension that drives Google Flow (Veo)
EndScreenshot/         the handwritten answer card generator
projects/<slug>/       one video: script, captions, beats, meta
  script_master.md       the recorded script — the caption reference
  words_part<N>.json     word timings
  lines_part<N>.json     the caption track
  meta.json              question, years, clip lengths, card lengths
.claude/skills/        the Claude Code skills that drive all of the above
```

Everything under `projects/<slug>/` except the script, the captions and
`assets/` is regenerated. Rendered media is never committed.

---

## Read next

| | |
|---|---|
| [CLAUDE.md](CLAUDE.md) | **why** the pipeline is shaped this way, and the gotchas that cost time |
| [PIPELINE.md](PIPELINE.md) | the operational walkthrough, and the mistakes already made |
| [tools/README.md](tools/README.md) | the avatar-synced track in detail |
| [tools/edu/renderer/README.md](tools/edu/renderer/README.md) | the HTML renderer |

Read CLAUDE.md before changing anything. It records the constraints that are not
visible from the code — the decisions that look arbitrary until you know what
they are avoiding.
