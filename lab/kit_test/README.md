# The kit: Vox-style arts reels

Every arts video since October 2026 (all GEO, HIS and POL in `~/Desktop/Final Arts/`)
was built here.

A HeyGen presenter clip and its caption file become a portrait reel. The reel has:
- a themed background, real photos and Veo b-roll;
- a presenter card;
- captions pinned to the bottom;
- big hero text for every point;
- an answer sheet that builds across the parts;
- the official answer page on the end.

The page is HTML (`stage.html`), drawn frame by frame in headless Chromium. The
compositor (`compose.py`) lays the footage, the keyed presenter and the graphics
together and mixes the voice with sound effects.

```
part<N>.mp4 + .srt ─► kit_captions ─► lines_part<N>.json ─┐
photos / plates / Veo clips ──────────────────────────────┤
make_<id>_plans.py ─► plan_<id>_p<N>.json ─► compile.py ──┴─► stills (review) ─► render_queue.sh
                                              │ gates                                    │ gates.py
                                              ▼                                          ▼
                                         timeline.js                       final/<id>_part<N>.mp4
                                                                                         │
                                         answer page (sheet col. AK) ─► answer_outro ───► delivered
```

---

## One-time setup (on top of the repo README's setup)

```bash
# the page renderer: Playwright + its headless Chromium (the kit borrows this install)
cd tools/edu/renderer && npm install && npx playwright install chromium-headless-shell && cd -
# Devanagari shaping for anything Pillow draws (answer pages, plates with text)
brew install libraqm      # then see CLAUDE.md for the Pillow rebuild
```

Things that must be in `.env` (copy `.env.example`):

| Key | Used for |
|---|---|
| `OPENAI_API_KEY` | Whisper word timings in `tools/kit_captions.py` |

**Veo (Google Flow)** is driven through the Chrome extension in [`flow/`](../../flow/README.md):
1. Load `flow/extension` as an unpacked extension.
2. Sign in to `flow.google.com` and open a project.
3. Read [`veo_kit/SETUP.md`](../../veo_kit/SETUP.md) once.

Check that the bridge on port 8765 is THIS project's extension. Another project
ships one on the same port.

**This is an 8 GB machine's pipeline.**
- Run `tools/machine_guard.py` before rendering.
- Render one part at a time; `render_queue.sh` does this.
- When swap fills the disk, reboot. A reboot is the only thing that frees the swap file.

---

## Building one video

Work in this order. Each step has a check, and nothing renders until the stills
are approved.

### 1. Sources and captions

```bash
mkdir -p projects/<slug>/src        # slug = lower-case id, e.g. his-c3-sa-02
# part1.mp4 / part1.srt (and part2...) from HeyGen go in src/
.venv-tools/bin/python tools/kit_captions.py <slug> <n_parts>
```

It prints every caption line with its start time.
- **HeyGen's SRT timings are wrong**, so the lines are re-timed onto Whisper word times.
- Check any line whose start disagrees with its words. Usually it's where Whisper
  skipped a stretch; fix it against `words_part<N>.json`.
- Spoken years come out as digits.

Write `projects/<slug>/meta.json` (copy any arts project's):
- **Question:** take it from the sheet.
- **Year:** take it from the narration. When the sheet and the take disagree, the spoken year wins.
- **Marks:** required, because the question card carries a marks sticker.
- **`hilite`:** the keywords to underline in the captions.

### 2. Look and footage

- **Theme:** `themes/<name>.css`. Choose a different skin per video, picked by
  topic. Derive a new one from an existing theme by `sed`-swapping its colours,
  then append its own ornament.
- **Plates** (`library/backgrounds/plates/generated/*.jpg`, 1080x1920):
  - Make them from licensed photos: `tools/fetch_photos.py` searches Wikimedia
    Commons, keeps only commercially usable licences and writes `credits.json`.
  - Or from the CC0 textures in `library/elements/textures/`.
- **Veo b-roll:**
  1. Write one prompt per shot in `projects/<slug>/veo/prompts/broll/<id>.txt`,
     following the existing projects' format (a positive description, then the NEGATIVE list).
  2. Submit: `.venv-tools/bin/python veo_kit/submit.py <prompts> --aspect vertical --no-refs`
  3. Download: `.venv-tools/bin/python veo_kit/grab_tiles.py <dir> --n <count>`. Tiles come
     newest-first, in reverse submit order; check them on a contact sheet before filing.
  4. File each clip as `veo/clips/<id>.mp4`.
  5. Delogo it into `veo/clean/<id>.mp4` (`delogo=x=570:y=1132:w=62:h=60`). Flow burns a
     sparkle into every clip, and no prompt prevents it.
- **Prefer what a Class 12 MP Board student recognises,** and vary the shots and
  plates from video to video.
- **Check every clip against the answer.** A generated street that shows the very
  thing the answer says is wrong has shipped elsewhere.

### 3. The plan

Copy the closest `make_<id>_plans.py` and rewrite its beats. Cues are a caption
line index, or `[line, seconds into it]`.

Elements (see `stage.html` for every option):

| Kind | Elements |
|---|---|
| Text | `hero` (big text for each point), `headline`, `note`, `pill`, `pills`, `stamp`, `paper` |
| Question and answer | `qhero` (the question card with years and marks), `answer` (the sheet, building point by point; `show`/`animate_from`/`nums`), `ask` (a curiosity question, then its answer) |
| Lists and contrasts | `cards3`, `notify`, `yn` (✗ then ✓), `compare`, `checklist`, `chain` |
| Pictures | `photo`, `inset` (then and now), `lottie` (free animations in `library/elements/lottie/`), `pins`, `ring`, `seamap`, `timeline`, `progress`, `verdict`, `search`, `toggle`, `qmarks` |

Plan-level settings:
- **`theme`:** the skin.
- **`plate`:** the default background.
- **`presenter_style: "card"`.**
- **`captions_at: "bottom"`.**
- **`spine`:** the title bar and the points dots.
- **`tracker`:** the corner list of points done.

Per beat:
- **Background:** `broll` (a clip, with `offset` and `dim`) or `plate`.
- **Presenter:** `standard` (the card), `full` (free-standing), `hub` (a circle).

```bash
.venv-tools/bin/python lab/kit_test/make_<id>_plans.py
.venv-tools/bin/python lab/kit_test/compile.py lab/kit_test/plan_<id>_p1.json --stills auto
node lab/kit_test/stills.mjs out/plan_<id>_p1      # one still per beat, plus a layout check
```

**Show the stills and wait for a go before rendering.**

### 4. Render

```bash
bash lab/kit_test/render_queue.sh "plan_<id>_p1|none" "plan_<id>_p2|none"   # |none = no background music
```

The queue handles the bookkeeping:
- **Order:** one part at a time.
- **Disk:** it stops below 1.5 GB free.
- **Streams:** it checks that the file has audio and video.
- **Gates:** it writes the `.geom.json` sidecar and runs every gate on each part.

Output goes to `projects/<slug>/final/<id>_part<N>.mp4`.

### 5. Answer page and delivery

1. Download the answer page from **column AK** of the question sheet.
   - Read the sheet via the xlsx export. Connector snippets truncate long cells.
   - Check the page before using it: it must be the house sheet (ruled paper,
     प्रश्न/उत्तर margin, Arivihan watermark), and its question must match.
2. Append it to the **last** part:

```bash
.venv-tools/bin/python tools/answer_outro.py final/<id>_part2.mp4 assets/answer/<ID>-1.png \
    "~/Desktop/Final Arts/Final <Subject>/<ID — title>/2.mp4" --hold 7 [--then page2.png ...]
```

3. Copy the other parts in as `1.mp4`, and so on.
4. A delivery folder holds **only** the part videos.
5. Upload to the ARTS Drive folder.

---

## The gates

Each gate exists because the defect it catches shipped at least once. **A gate
failure stops the build; a warning prints and lets it through.**

| Where | Gate | Refuses |
|---|---|---|
| `compile.py` | `caption_after_question` | captions running under the question card |
| `compile.py` | `hook_visual` | a part 1 that opens on a title card instead of a Veo clip (a warning on later parts) |
| `compile.py` | `no_em_dash` | an em-dash anywhere in screen text |
| `compile.py` (warning) | `long_hold` / `dead_air` | more than 6 s with nothing changing; a beat of empty plate |
| `stills.mjs` / `frames.mjs` | layout check | anything reaching the presenter card, anything leaving the frame, a caption overlapping content |
| `render_queue.sh` | streams + disk | a file without audio or video; starting below 1.5 GB free |
| `tools/gates.py` | output, avatar shape, face, fonts, plates, dashes, answer page, … | see the script's header; it prints skips with their reason, and exits non-zero on any failure |
| `tools/answer_outro.py` | extension ink | handwriting copied into the paper extension under an answer page |
| `tools/machine_guard.py` | memory/disk | starting a heavy job when swap or disk is exhausted |

Run all of `tools/gates.py` on any video built off this path too:

```bash
.venv-tools/bin/python lab/kit_test/geom_sidecar.py lab/kit_test/plan_<id>_p<N>.json <video>
.venv-tools/bin/python tools/gates.py <slug> <video>
```

---

## Files

| File | What it does |
|---|---|
| `compile.py` | plan → `out/<plan>/timeline.js`: resolves cues, keys presenter stills, runs the plan gates |
| `stage.html` | draws one moment of the timeline; every element type lives here |
| `themes/*.css` | one skin per video (colours, fonts, card ornament) |
| `stills.mjs`, `frames.mjs`, `scan.mjs` | review stills, the full frame sequence, a per-frame layout report |
| `compose.py` | footage + keyed presenter + graphics + sound effects → mp4 |
| `render_queue.sh` | compile → frames → compose → checks → gates, one part at a time |
| `geom_sidecar.py` | the presenter geometry `tools/gates.py` checks against |
| `make_<id>_plans.py` | each delivered video's plan generator, so you can copy the closest one |

Plans named `_A`/`_B`/`_C`, `_O1`…, `_skin_*` and `_sample*` are design options
that were shown and not all chosen. Some fail today's gates; they are kept as a
record, not as templates.

Libraries the kit reads (each with its licence record):
- `library/sfx/` (`manifest.json`)
- `library/music/` (`manifest.json`)
- `library/backgrounds/photos/**/credits.json`
- `library/elements/lottie/manifest.json`
- `library/elements/textures/credits.json`
