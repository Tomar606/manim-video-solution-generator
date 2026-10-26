# The kit: how a PYQ reel is made

Every reel since October 2026 is built here, in all subjects (Physics, Chemistry, Biology, History,
Geography, Political Science). A HeyGen presenter clip and its caption file become a portrait reel:
- a themed background, with real photos and Veo b-roll;
- exact diagrams where correctness matters;
- a presenter card, captions at the bottom, a large line for every point;
- the official answer page on the end.

- **[STANDARD.md](STANDARD.md):** what a finished reel must look like and how it is delivered, taken from the
  four latest videos. Read it first.
- **The `reel` skill** (`.claude/skills/reel/SKILL.md`): the order of work, step by step. Claude follows it.
- **[ELEMENTS.md](ELEMENTS.md):** the element catalogue, and the lessons from the reference edits.

```
HeyGen mp4 + srt ──► splice ──► captions (Whisper or pause_align) ──► lines_part1.json ─┐
question ID ──► sheet_fetch ──► meta.json + answer page                                  │
photos / plates / Veo clips / exact diagrams ────────────────────────────────────────────┤
make_<id>_plans.py ──► plan_<id>_p1.json ──► compile.py ──► stills ──► review page ─┐    │
                                                    (person approves the frames)    ▼    │
                                         render_reel.py ──► compose ──► deliver.py ◄────┘
                                                                   (gates, answer page, Final folder)
```

The page is HTML (`stage.html`), drawn frame by frame in headless Chromium. `compose.py` lays the footage,
the keyed presenter and the graphics together and mixes the voice with sound effects.

## Setup (once per machine)

The person running it needs Claude Code and Chrome. The tools need Python 3.11–3.12, Node 20+, ffmpeg and
Poppler (`pdftoppm`).

**macOS**
```bash
brew install ffmpeg node poppler libraqm fribidi
python3 -m venv .venv-tools && .venv-tools/bin/pip install -r requirements-tools.txt
cd tools/edu/renderer && npm install && PLAYWRIGHT_BROWSERS_PATH=.browsers npx playwright install --only-shell chromium && cd -
cp .env.example .env          # then fill it in (below)
.venv-tools/bin/python tools/fetch_mixkit.py      # the sound effects the public repo cannot carry
.venv-tools/bin/python tools/doctor.py --flow
```

**Windows** (PowerShell)
```powershell
winget install Python.Python.3.12 OpenJS.NodeJS.LTS Gyan.FFmpeg Git.Git
# Poppler for Windows: download a release, unzip, and add its Library\bin folder to PATH
py -3.12 -m venv .venv-tools; .venv-tools\Scripts\pip install -r requirements-tools.txt
cd tools\edu\renderer; npm install; $env:PLAYWRIGHT_BROWSERS_PATH=".browsers"; npx playwright install --only-shell chromium; cd ..\..\..
copy .env.example .env        # then fill it in (below)
.venv-tools\Scripts\python tools\fetch_mixkit.py
.venv-tools\Scripts\python tools\doctor.py --flow
```
On Windows, every `.venv-tools/bin/python` in these docs is `.venv-tools\Scripts\python`. If the doctor
reports Hindi shaping missing, put FriBiDi's `fribidi-0.dll` on PATH.

**.env**

| Key | Used for |
|---|---|
| `OPENAI_API_KEY` | Whisper word timings (`tools/kit_captions.py`); without credits, captions fall back to `tools/pause_align.py` |
| `SHEET_ARTS`, `SHEET_SCIENCE` | the question sheets' IDs (`tools/sheet_fetch.py`); never commit them |
| `DELIVER_ROOT` | where finished reels go (default: the Desktop; on Windows often `...\OneDrive\Desktop`) |

**Veo (Google Flow):**
1. In Chrome, open `chrome://extensions`, turn on Developer mode, choose Load unpacked, and pick `flow/extension`
   ("PYQ Flow Bridge"). Only one bridge extension may be on; another project ships one on the same port.
2. Sign in at flow.google.com and open a project.
3. Run `tools/kit_veo.py setup`. It sets Video, Veo 3.1 Fast, 9:16 and 1 output.

**Using the machine's power.** `render_reel.py` sizes itself to the PC it runs on:
- it renders in parallel **lanes**, one per ~1.2 GB of free memory and 4 cores, up to 4. An 8 GB laptop gets
  1; a 16–32 GB, 8-core desktop gets 3–4. Set `KIT_LANES` to override;
- every encode uses the **GPU's video encoder** when there is one: NVIDIA NVENC, Intel Quick Sync, AMD AMF or
  Apple VideoToolbox. It falls back to x264 on the CPU. `python tools/encoders.py` prints which one this
  machine uses; `KIT_ENCODER` forces one;
- the frame drawing and compositing themselves run on the CPU (headless Chromium, numpy), which is why the
  lanes matter more than the GPU on a strong PC.

**Small machines.**
- `tools/machine_guard.py` refuses heavy work without room, and `render_reel.py --wait` waits for room
  instead.
- An 8 GB machine swaps, and its swap file eats the disk. Close browsers and music while rendering, and
  restart when swap is large.

## Making one reel (what the skill does)

| Step | Command (tools Python) | Who |
|---|---|---|
| 0 | `tools/doctor.py --flow` | Claude |
| 1 | splice the patch, if any (see the skill) | Claude |
| 2 | `tools/sheet_fetch.py <ID>`, then set marks, years, title in meta.json | Claude |
| 3 | `tools/kit_captions.py <slug>`, or `tools/lines_from_srt.py` + `tools/pause_align.py` | Claude |
| 4 | exam sheets: `tools/paper_header.py ... --year <Y>` | Claude |
| 5 | theme pack, plates (`tools/fetch_photos.py`), exact diagrams | Claude |
| 6 | `lab/kit_test/make_<id>_plans.py` from the closest reference | Claude |
| 7 | `tools/kit_veo.py setup / submit / fetch / clean <slug>` | Claude |
| 8 | `compile.py --stills auto`, `stills.mjs ... review`, `review_page.py <slug>` | Claude |
| 9 | **review the frames** in `projects/<slug>/review/index.html`, then "Copy my review" | the person |
| 10 | `lab/kit_test/render_reel.py <slug> --wait` (renders, then delivers) | Claude |
| 11 | **watch the delivered video** | the person |

## Correctness first: when not to use Veo

A generated clip is for atmosphere: a place, an era, a feeling.
- Anything a student must reproduce in the exam is drawn **exactly**, never generated: a circuit, an
  apparatus, a reaction setup, a mechanism, a cycle, a labelled biological structure, a graph, a map.
- Exact means an SVG/HTML element in `stage.html` (the Wheatstone bridge, metre bridge, flask, cube and
  rewrite elements are the examples), or a Manim render.
- A Manim or other exact render goes in `projects/<slug>/diagrams/<id>.mp4`. A beat names it like a clip, and
  it takes precedence over any Veo clip of the same id.
- Get the mechanism's direction and order right (electron flow, current, reaction direction); label every
  part as it is spoken; use textbook colour conventions.

## The gates

Each gate exists because the defect it catches shipped at least once. A gate failure stops the build; a
warning prints and lets it through. `tools/deliver.py` runs `tools/gates.py` and delivers nothing if any
gate fails.

| Where | Gate | Refuses |
|---|---|---|
| `compile.py` | `caption_after_question` | captions under the question card |
| `compile.py` | `hook_visual` | a part 1 that opens on a title card instead of moving footage |
| `compile.py` | `no_em_dash` | an em-dash in screen text |
| `compile.py` (warning) | `long_hold`, `dead_air` | over 6 s with nothing changing; a beat of empty plate |
| `stills.mjs` / `frames.mjs` | layout | anything reaching the presenter, leaving the frame, or under a caption |
| `tools/gates.py` | output, avatar shape, face, answer page, dashes, kit Veo, loudness, … | see its header; skips print their reason |
| `tools/machine_guard.py` | memory, disk | starting a heavy job without room |

## Files

| File | What it does |
|---|---|
| `compile.py` | plan → `out/<plan>/timeline.js`: resolves cues, keys presenter stills, runs the plan gates |
| `stage.html` | draws one moment of the timeline; every element type lives here |
| `themes/*.css` | one skin per video (colours, fonts, card ornament) |
| `stills.mjs`, `frames.mjs`, `scan.mjs` | review stills, the full frame sequence, a per-frame layout report |
| `compose.py` | footage + keyed presenter + graphics + sound effects → mp4 |
| `render_reel.py` | the render: one lane, keeps the machine awake, then `tools/deliver.py` |
| `review_page.py`, `review_sheet.py` | the review page (browser) and the labelled frame sheets |
| `geom_sidecar.py` | the presenter geometry `tools/gates.py` checks against |
| `make_<id>_plans.py` | each delivered video's plan generator; the four references are named in STANDARD.md |

Libraries the kit reads, each with its licence record:
- `library/sfx/` (`manifest.json`);
- `library/backgrounds/photos/**/credits.json`;
- `library/backgrounds/plates/generated/_generated.json`;
- `library/elements/lottie/manifest.json`;
- `library/elements/textures/credits.json`.
