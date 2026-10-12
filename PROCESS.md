# The process

One fixed order for building a video from an already-shot HeyGen clip. The
**layout and design change every video; these steps never do.**

Read `CLIP_VIDEO_RUNBOOK.md` for the detail behind any step. This page is the
order, the gate on each step, and where the tool lives.

**You do not type these steps.** `tools/build_clip.py` runs them in this order,
behind these gates, with independent work at the same time — see "Running it"
below. The `clip-video` skill is how a Claude session drives it.

**Drawing anything for an arts reel?** Read [`arts/DESIGN_RULES.md`](arts/DESIGN_RULES.md)
first: the on-screen rules the user's reviews have set (memory devices, spacing,
maps and borders, presenter position, backgrounds). The arts process itself is
[`PROCESS_ARTS.md`](PROCESS_ARTS.md).

---

## The rule everything else follows from

**The video folder holds no code — only design.**

| | lives in | changes per video |
|---|---|---|
| **Process** — ingest, transcribe, retime, validate, render, composite, verify | `tools/` and `tools/clip/` — one copy | never |
| **Design** — which diagrams, which segments, background, theme | `work/<slug>/` — data + SVG only | every video |

This is not tidiness. `work/phy-c1-la-02-part1/` holds 23 files with the process
and the design mixed together, so a new video either copies the whole folder and
inherits the last video's design — BIO-C2-LA-01 rendered over chemistry test
tubes that way — or copies nothing and loses the process, which is how
BIO-C5-LA-01 ended up with zero Python files and re-derived its timing by hand.

If the video folder cannot hold a script, no step can be re-invented inside it.
**It now cannot:** every `tools/clip` script and `tools/build_clip.py` refuse a
folder that carries its own `.mjs`, `.py`, `engine.js` or `node_modules`.

---

## The renderer

**Headless Chromium** — KaTeX, hand-written SVG, Node and ffmpeg. No Manim, no
LaTeX. It renders a 121s part in ~131s against Manim's ~3min, and installs on any
machine. **It lives once, in `tools/clip/`**, with its own `node_modules`:

```bash
node tools/clip/full.mjs  <slug> --part 1      # render   -> out/render-part1.mp4
node tools/clip/qa.mjs    <slug> --part 1      # pixels
python3 tools/clip/validate.py <slug> --part 1 # paper
node tools/clip/sheet.mjs <slug> --part 1      # storyboard -> out/storyboard_part1.png
```

The video folder supplies only `video.json` (the background — required, no
default) and optionally `theme.css`. Until 2026-09-21 every video carried its
own copy: nine copies of `full.mjs` in six versions, nine of `engine.js` in
seven. `tools/clip` was built from the most-patched one (CHE-C3-SA-04, a
superset of all the others) and re-renders CHE-C3-SA-04 part 1 **byte-identical**
to the file that shipped (0 of 3630 frames differ).

Manim remains only for the older PYQ track. New videos do not use it.

> **Never copy a renderer.** `skill/edu-video/`, `tools/edu/` and the copies
> inside old `work/<slug>/` folders are records of how those videos were built,
> not starting points.

---

## The steps

Each step has one gate. **A gate blocks — it does not warn.** Step N does not
start until step N−1 is green.

| # | Step | Gate | Tool |
|---|---|---|---|
| # | Step | Gate | Tool | runner step |
|---|---|---|---|---|
| 1 | **Ingest** the drop folder | every part has a clip; audio and SRT agree with it within 1s | `tools/ingest.py` | `ingest` |
| 2 | **Transcribe** — whisper.cpp, word timings | no holes > 1.5s, no collapsed tokens > 1.3s — each one fixed or adjudicated in `out/transcript_adjudication_part<N>.json` | `tools/word_timings.py` | `wav` `transcribe` `words` |
| 3 | **Retime** — the SRT keeps its words and loses its clock | every boundary within 0.35s of the spoken word, **measured against a transcription this step did not produce**; each flagged cue fixed or adjudicated against silences in `out/drift_adjudication_part<N>.json` | `tools/draft_captions.py` (maps every SRT cue to its words; an agent reviews) · `tools/lines_from_edit.py` · `tools/srt_drift.py` | `transcribe_check` `draft` `captions` `retime` |
| 4a | **Design + route** — from the script and the SRT, **while the clip is still being transcribed**. Everything a beat may contain, measured, with templates: `tools/clip/DESIGN.md`. Derivations are written as `ladder`s and the layered LaTeX is generated at `bind` | `route_gate.py` exit 0 | `tools/clip/DESIGN.md` · `tools/route_gate.py` | `design` `route` |
| — | **Bind** the design to the measured clock | every `say` is spoken inside its beat's cues · `check_labels.py` exit 0 | `tools/bind_design.py` · `tools/merge_design.py --bound` · `tools/check_labels.py` | `bind` |
| 5 | **Build** the SVGs — starting from the closest shipped figure — and generate the Veo clips | `svg_lint.py` exit 0; Flow's per-project settings read back correct **before the first submission**; every clip graded pass | `tools/clip/figures/` (every shipped diagram, indexed; refresh with `build_index.py` after each delivery) · `tools/clip/svg_lint.py` · `flow-animator` `preflight` · `src/veo.py` | `svg` (one per diagram) `svgs` `clips` |
| 6 | **Spec** — every boundary on a measured onset | `validate.py` 0 errors · `qa.mjs` 0 fails · `dash_gate.py` 0 hits · **segments sum to clip length** | `tools/build_spec.py` · `tools/clip/validate.py` · `tools/clip/qa.mjs` · `tools/dash_gate.py` | `spec` |
| 4b | **Storyboard** — one tile per segment | a human looks at the sheet, and `approve` records a hash of exactly that sheet | `tools/clip/sheet.mjs` | `storyboard` `approve` |
| 7 | **Render** — two browser tabs; the question card drawn into the same frames | every string the spec promises is in the DOM (text audit) | `tools/clip/full.mjs --pages 2 --intro` | `render` |
| — | **Question card** — first part only | Devanagari drawn on a Pillow with libraqm | `tools/question_card.py` · `tools/clip/make_intro_layers.py` · `tools/clip/plate_frame.mjs` | `card_info` `card` |
| 8 | **Measure the presenter** — key + crop, per clip | key hole and leak ≤ 0.5% | `tools/calibrate_key.py` · `tools/avatar_crop.py` | `measure` |
| 9 | **Composite** | — | `tools/composite.py` | `composite` |
| 10 | **Close on the answer card** — last part only | every page whole, nothing cropped | `tools/answer_outro.py` | `answer` `outro` |
| 11 | **Verify the delivered file** — the one being shipped, not the one before the outro | `output_gate.py` exit 0 on the copy in `final/`, geometry sidecar alongside · `sync_check.py` | `tools/output_gate.py` · `tools/sync_check.py` | `deliver` |

Every tool is in `tools/` or `tools/clip/`; nothing is copied into a video folder.

The storyboard (4b) is built from the spec, after the SVGs exist, so the sheet
a human approves is the picture that will render — and it is approved BEFORE
anything expensive: the render, and for biology the Veo generations.

**Chemistry and physics never use Flow.** Every animation in a `CHE-…` or `PHY-…`
video is a composited SVG, so step 5 there is SVGs only: no Veo brief, no Flow
run, no browser. `route_gate.py` reads the subject off the slug and fails any
Veo beat in those videos. Biology keeps the Veo default.

---

## Running it

```bash
python3 tools/build_clip.py <QID> init            # ingest + work/<slug>/ from work/_template
python3 tools/build_clip.py <slug> run            # every machine step that can run, until none can
python3 tools/build_clip.py <slug> tasks          # the writing that is ready — one agent per task
python3 tools/build_clip.py <slug> approve --part N
python3 tools/build_clip.py <slug> status | plan
```

`work/<slug>/state.json` records each step's result against a fingerprint of its
inputs and of the tools it ran. **A step does not start until everything it
depends on is green, and a green result only counts while its inputs are
unchanged** — edit one caption and the retime, spec, storyboard sign-off,
render and composite all go stale; nothing upstream re-runs. Each step logs to
`work/<slug>/out/logs/<step>.log`.

**What runs at the same time.** Right after ingest: transcription, presenter
measurement, the question card — and the DESIGN. A beat names the SRT cues it
covers and the words it lands on (`"cues": [5, 7]`, `"say": "देहली ऊर्जा"`),
which exist the moment the drop lands; `bind` resolves them against the
measured clock afterwards. So the design and every SVG are drawn while the clip
is being transcribed, instead of after the captions. The check transcript runs
while the captions are being written, and the captions start from a machine
draft that has already mapped every SRT cue to its words. The writing is split into independent tasks — one
`clip-captions` agent per part, one `clip-designer` per part, one `clip-svg` per
diagram — and `tasks` lists every one that is ready, so they are dispatched
together. Parts never wait for each other until delivery.

**What limits it is memory, not cores.** Every machine step carries its measured
weight (whisper 1.9GB) and the scheduler keeps the total under `--budget`
(3.0GB by default on this 8GB machine); no heavy step starts unless
`tools/machine_ready.py` passes.

**What it is worth** (`plan`, from CHE-C3-SA-04's measured step times; the
writing times are that build's, not targets):

Rerun `plan` for the current figures; on 2026-09-21 the render measured
**77.6s with two tabs and the card drawn in**, against 131s + 12s (card video)
+ 35s (overlay pass) before, at 49 dB PSNR against the shipped output.

**Measured and rejected:** the M2's hardware encoder for the composite. x264
encodes a part in 45s of the composite's ~5 min (the keying filters, capped at
two threads so the machine stays usable, are the rest); VideoToolbox saved 27s
at SSIM 0.993 against 0.998, in files three times the size.

## Every gate maps to a bug that shipped

| Gate | What it would have caught |
|---|---|
| 1 | BIO-C5-LA-01's parts arriving in two naming conventions, identified by transcribing them |
| 1 | An SRT from a different take — the shape of a 3-second caption lead |
| 2 | Whisper silently dropping **18.1 seconds** of BIO-C5-LA-01 part 1 |
| 3 | BIO-C2-LA-01's captions running up to **3s ahead** of the voice — cost a full rebuild of two parts |
| 3 | BIO-C12-LA-02's captions **5 seconds behind the voice** on a drop whose own report read "worst drift 0.00s" |
| 5 | Five clips that never generated: Flow's "Confirm before generating" was Always, so three runs waited out a 15-minute timeout each and returned nothing |
| 6 | BIO-C5-LA-01's **119 seconds of 262** with nothing planned on screen |
| 6 | Em dashes on screen in two finished videos — standing house style, and nothing ran the gate that checks it |
| 11 | A floating presenter, and audio drifting against picture |
| 11 | An answer card appended after the gate ran, so the file that shipped was never the file that passed |

None of these are new checks. They all existed. They were skipped because
nothing refused to continue without them.

> `tools/layout_gate.py` says it best: *"A warning nobody blocks on is not a
> check."* The dry-cell labels overlapped at 65%, the log said so, and the video
> shipped anyway.

---

## A drop that arrives already built

Some videos arrive as a **bundle**: not raw clips, but a finished tree with
captions, transcripts, specs and rendered parts, built on another machine.
BIO-C12-LA-02 came that way.

**Derived artefacts that arrive with a drop are re-verified, never trusted.**
Its bundle reported *"worst drift 0.00s"*, and that was true: the drift had been
measured against the same transcript the captions were built from, so it could
only ever agree with itself. Measured against a fresh transcription of the
delivered audio, part 1 ran **five seconds** behind the voice for eight
consecutive captions. Two of the four defects reported back on the finished
video were that one number.

So a bundle is ingested like any other drop, and step 3 is re-run:

```bash
tools/word_timings.py  <clip.wav> <srt> <seconds> words.json   # OUR measurement
tools/retime_lines.py  lines_partN.json words.json --write     # move the clock
```

`retime_lines.py` keeps the line PARTITION and changes only the timing, because
anchors, beat design and every `at` offset are expressed in line INDICES — a
rebuilt caption track silently invalidates the plan while looking fine.

**A number that checks itself is not a check.** Any drift, coverage or accuracy
figure quoted by a drop names what it was measured against, or it is re-measured
here.

---

## The render and the compositor share a frame — and must not draw the same thing

`tools/composite.py` lays a generated clip into the panel the renderer drew, and
ramps its alpha over `VEO_FADE` at each edge. **Whatever the render put inside
that panel is visible through both ramps.** The renderer's clip placeholder —
kicker, description, "played, not keyed" — ghosted up at the start and end of
every clip in two finished videos.

Anything the compositor covers is drawn for the STORYBOARD only
(`#frame.sheet`), never in the render. What stays is what the clip fades onto:
the panel's dark ground and the torn divider.

---

## A video folder must be able to build on its own

Four video folders symlinked `node_modules` at a fifth, `work/kmno4/`. When that
folder was cleaned up mid-session, all four lost the ability to render, and the
failure read as a missing module rather than as a missing sibling. The
Playwright browser cache went with it.

The dependencies now live with the one copy of the code that uses them,
`tools/clip/node_modules`. A video folder has none, and the tools refuse one
that does. Agents must never move, copy or symlink it.

---

## Where things live

```
inbox/<QID>/              the ONE drop point — clips, SRTs, script
                          see inbox/README.md
work/_template/           what `build_clip.py <QID> init` starts a video from
work/<slug>/
    inputs.json           written by ingest.py — every stage reads this,
                          nothing globs inbox/ again
    video.json            background (required), question card, answer pages
    theme.css             optional design overrides of the engine's stylesheet
    spec/parts/           design_part<N>.json + anchors_part<N>.json (authored)
    spec/segments_part<N>.json   what is on screen, when (generated)
    assets/svg/           the diagrams
    state.json            which steps are green, on which inputs; approvals
    out/                  everything generated; out/logs/ one log per step
tools/                    the process. One copy. Never inside a video folder.
tools/clip/               the renderer: engine, render, QA, storyboard, intro card
tools/build_clip.py       the steps, in order, behind their gates
```

---

## Done (2026-09-21)

The three open items this page used to list:

1. **The ⬜ tools are promoted** — into `tools/clip/`, taking a slug instead of
   assuming they run inside the folder. So are the steps that were typed by hand
   every time: the storyboard contact sheet, `plate-frame.png -> plate.png`, the
   lines-to-SRT conversion the retime gate reads, the card overlay, the card and
   layout windows, and copying the delivered file WITH its geometry sidecar.
2. **`tools/build_clip.py`** runs the steps in order and refuses step N while
   N−1 is not green (it is Python, not the `build_clip.sh` this list named, so
   it can hold state and schedule in parallel).
3. **`work/_template/`** — `build_clip.py <QID> init` starts a video from it.

Still open:
- The card overlay (`bg` step) was reconstructed from the runbook, because the
  build logs recorded it only as "ffmpeg overlay". Check its first output against
  a shipped `bg-part1.mp4` before trusting it.
- The old `work/<slug>/` folders keep their own copies of the process as records.
  To re-render one with `tools/clip`, give it a `video.json`, move its code out,
  and check the result against what shipped.
