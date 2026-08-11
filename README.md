# AI educational video pipeline

Turn a topic into a finished explainer: a written script, Manim animations,
multi-voice narration, automatic sound effects, real photographs, an answer
card, and a chroma-keyed presenter composited on top.

```
topic ──► script.md ──► narration ──► animation ──► QC ──► composite ──► final.mp4
          (Claude)     (ElevenLabs)   (Manim +      (Claude   (ffmpeg
                                       Claude)      vision)   chromakey)
                                                                  ▲
                                          presenter clips ────────┘
                                          (HeyGen — dropped in or fetched)
```

Everything for one video lives in `projects/<slug>/`. Every stage reads and
writes that folder, so stages are re-runnable, resumable, and drivable from the
CLI, the browser dashboard, or Claude Code — all three call the same code.

---

## Setup

You need **ffmpeg**, **LaTeX**, and **Python 3.10–3.12** (Manim 0.18 doesn't
build on 3.13+). Two ways to get there.

### Native — faster renders

```bash
# macOS / Linux
./bin/bootstrap.sh

# Windows (PowerShell, from the repo root)
powershell -ExecutionPolicy Bypass -File .\bin\bootstrap.ps1
```

The script checks what's missing, prints the exact install command for your OS,
creates `.venv`, installs dependencies, copies `.env.example` to `.env`, and
builds the sound-effect library. Run it with `--check` to only report.

### Docker — nothing to install but Docker

```bash
docker compose build
docker compose run --rm app python video.py doctor
```

The image carries ffmpeg, LaTeX and Manim, so renders are identical on every
machine. Slower to start, ~4 GB.

### Credentials

Copy `.env.example` to `.env` (bootstrap does this) and fill in:

- **ElevenLabs** — `ELEVENLABS_API_KEY`, required for narration.
- **Claude** — two options:
  - *Subscription (default).* `npm install -g @anthropic-ai/claude-code`, then
    run `claude` once to log in. No API key, billed to your Claude plan.
  - *API key.* Set `ANTHROPIC_API_KEY`. Needed for unattended runs (CI, Docker),
    where there's no CLI login.
- **HeyGen** — optional. Without a key you use the manual clip workflow below.

Check everything with:

```bash
./bin/video doctor
```

---

## Making a video

### The browser dashboard (easiest)

```bash
./bin/video dashboard          # opens http://localhost:8000
```

Create a video, edit the script in the page, run each stage with live logs,
drag-and-drop the HeyGen clips, read the QC report with its frames, then preview
and download the result. No terminal after the first command.

It binds to localhost only. It's an unauthenticated file-editing UI — don't
expose it beyond a machine you trust.

### The command line

```bash
./bin/video new "Deriving the quadratic formula"   # project + first-draft script
# → read projects/deriving-the-quadratic-formula/script.md and fix the wording
./bin/video build deriving-the-quadratic-formula   # everything, in order
```

Or one stage at a time:

| Command | What it does |
|---|---|
| `video new "<topic>"` | Create the project and draft a script |
| `video script <slug>` | Re-draft the script (`--force` to overwrite) |
| `video narrate <slug>` | Synthesize narration — **this sets all the timing** |
| `video background <slug>` | Animate, render, assemble the Manim side |
| `video avatar <slug> --briefs` | Write per-segment briefs for HeyGen |
| `video avatar <slug>` | Ingest dropped clips (or fetch them via the API) |
| `video qc <slug>` | Claude reviews the rendered frames |
| `video composite <slug>` | Key the presenter over the animation |
| `video status` | Where every project stands |

Narration runs first because segment lengths come from the measured audio, and
every later stage is timed against it.

### Claude Code

`/make-video`, `/write-script` and `/video-qc` skills in `.claude/skills/` drive
the same commands conversationally, with the failure modes documented.

---

## The presenter

The animation and the presenter meet through the **chroma zone**. A script that
reserves space:

```yaml
chroma: right_half
avatar:
  placement: auto      # the reserved zone *is* the presenter's box
  timing: audio        # narration is the clock (default)
```

renders with that half painted flat green and all content kept out of it. At
composite time the presenter is keyed, despilled, feathered and fitted into
exactly that box, standing on its bottom edge.

**Without a HeyGen key** (today):

```bash
./bin/video avatar <slug> --briefs
```

writes `projects/<slug>/avatar/briefs/` — a manifest plus a text brief per
segment with the exact line, its target length, and the narration `.wav` to
upload as the avatar's voice track (that's what makes the lip-sync land). Save
each clip as `segment_000.mp4`, `segment_001.mp4` … in
`projects/<slug>/avatar/`, then run `video avatar <slug>` to ingest and validate
them, and `video composite <slug>`.

**With a key**, set `HEYGEN_API_KEY` and `HEYGEN_AVATAR_ID` and the same
`avatar` stage generates and downloads the clips instead. Nothing else changes.

> The HeyGen client is written but unverified — we have no key yet. It fails
> loudly with the raw API response rather than guessing, so the first real run
> will show exactly what to adjust.

---

## Writing scripts that sound spoken

The narration is read aloud by a synthetic voice and lip-synced to a presenter,
so the bar isn't "good writing", it's "would a teacher say this out loud". Three
pieces enforce that.

**The voice comes from your own scripts.** Put approved scripts in
`style/samples/` and the recurring lines in `style/variations.yaml` — how a video
opens, how it moves between steps, how the answer lands. The writer matches the
samples' rhythm and picks a *different* approved phrasing each time a moment
recurs, which is what stops ten videos sounding identical.

```bash
video style --init        # create style/ with a template
video style               # what's currently loaded
```

**Every draft is scored.** `src/script_eval.py` checks the mechanical tells that
make narration sound synthetic — and they're all things a listener notices:

| Check | Why it matters |
|---|---|
| digits, `=`, `^`, `%`, LaTeX | the voice can't pronounce them — "do", not "2" |
| Devanagari | our voices expect Hinglish in Latin script |
| repeated openers | three beats starting the same way is *the* machine-written tell |
| uniform line length | real speech mixes short and long; flat lengths sound flat |
| "furthermore", "firstly", "as we can see" | written register, not speech |
| "as shown", "in the figure" | narration is heard — it can't point at anything |
| over 32 words | can't be said in one breath |

**Failures go back for another pass.** Same loop as the renderer: draft →
evaluate → hand back the specific defects → redraft, until it scores clean.

```bash
video script <slug>            # draft, score, and fix
video eval <slug>              # score an existing script
video eval <slug> --judge      # + a model's read against your samples
```

Script writing is the one stage that can run on a different provider:

```bash
SCRIPT_LLM=openai              # in .env — Manim codegen and QC stay on Claude
video script <slug> --provider openai
```

## Photos and the answer card

Put an image on any beat:

```markdown
[narrator]
Yeh actual apparatus hai jo Millikan ne use kiya.
![Millikan's apparatus](assets/apparatus.png){full,kenburns}
```

Layouts: `full` | `side` | `inset`. Effects: `kenburns` | `static` | `frame` |
`noframe`. Paths resolve against the script's folder, the project's `assets/`,
an absolute path, or an `https://` URL (downloaded and cached once).

The closing answer image is frontmatter:

```yaml
answer_image: assets/answer.png
answer_narration: Toh yeh raha final answer.
answer_caption: Charge of an electron
```

It becomes a real final beat, so it gets narration, timing, QC and compositing
like everything else. Photo-only beats render from a fixed template rather than
generated code — deterministic, so they look identical in every video.

---

## Sound

Scenes score themselves. A scene calls `self.cue("whoosh")` just before an
animation; the render stays silent, the cue is written to a sidecar file, and at
assembly every cue is offset onto the final timeline and mixed under the
narration. The templates cue themselves, and the animator prompt asks Claude to
cue its own key moments.

The seven default effects (`pop`, `ding`, `whoosh`, `click`, `write`, `reveal`,
`impact`) are synthesized locally with ffmpeg — no downloads, no licensing, and
identical everywhere. Drop your own `assets/sfx/<name>.wav` to override one, or
rebuild with `video sfx --force`. Disable per-render with `--no-sfx`.

---

## Layout

```
projects/<slug>/
  job.json         stage state and timing — the contract between stages
  script.md        the source of truth; edit this to change the video
  assets/          photos this video uses
  avatar/          presenter clips (segment_000.mp4 …)
    briefs/        what to generate for each segment
  audio/           narration, one clip per beat
  manim_code/      generated scenes (+ .cues.json sound cues)
  media/           raw Manim renders
  work/            conformed clips, concatenated tracks
  qc/              sampled frames + review report
  final/           background.mp4 and the composited final cut
```

| Module | Role |
|---|---|
| `video.py` | the CLI — every stage |
| `src/project.py` | project folders and stage state |
| `src/script_parser.py` | script format → `VideoScript` |
| `src/script_writer.py` | topic → first-draft script |
| `src/tts_elevenlabs.py` | narration and measured timing |
| `src/scene_codegen.py` | Claude codegen + render-repair loop |
| `src/scene_templates.py` | fixed scenes for photo/answer beats |
| `src/manim_helpers.py` | injected scaffolding: theme, chroma, photos, cues |
| `src/sfx.py` | sound library + cue mixing |
| `src/avatar.py` | briefs, manual drop, HeyGen provider |
| `src/composite.py` | chromakey + despill + placement |
| `src/qc.py` | Claude vision review |
| `src/assemble.py` | conform → concat → mix → mux |
| `src/dashboard.py` | the browser UI |
| `src/llm.py` | Claude access (CLI or API backend) |

---

## Notes

- **Don't hand-edit build output** (`manim_code/`, `work/`, `media/`,
  `final/`) — it's regenerated. Change `script.md` and re-render.
- **`--no-audio`** estimates timing from word count and skips TTS, so you can
  validate the render path without spending ElevenLabs credit.
- **`--continue-on-error`** drops segments that won't render instead of aborting,
  which is usually what you want when reviewing a first pass.
- **`--scenes-dir`** renders hand-written scenes instead of calling Claude — see
  `scenes/quadratic_formula/` for a worked set.
