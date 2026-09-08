# Making a PYQ video, end to end

The operational playbook for the **PYQ track**: one question from the MP Board
sheet becomes a set of portrait Hindi reels with a keyed presenter, screen
graphics, captions and a handwritten answer page.

Read [`how-a-video-is-built.md`](how-a-video-is-built.md) alongside this. That
one explains *why the captions stay in sync* and is the authority on the clock;
this one is the inventory and the running order — every element, where it sits,
when it appears, and what refuses to let it ship.

Worked examples in the tree: **BIO-C1-LA-01** (4 parts, chips), **BIO-C4-LA-01**
(3 parts, chips), **BIO-C5-LA-03** (3 parts, animated clips).

---

## 0. The frame

Everything is **1080 × 1920, 30 fps**. Four horizontal zones, and every layout
rule below is about keeping them apart:

```
  y=0      ┌─────────────────────────────┐
           │  CAPTION BAND               │  one or two lines, centred
  y≈176    ├─────────────────────────────┤  CEIL — the highest a graphic may start
           │                             │
           │  STAGE BAND                 │  chips and animations live here
           │  default top y=380          │
           │                             │
  y≈1050   ├─────────────────────────────┤  the presenter's HEAD — measured, not assumed
           │  PRESENTER                  │
  y=1344   │  (bottom 30%)               │  FLOOR — nothing but the presenter below this
  y=1920   └─────────────────────────────┘
```

Two numbers do most of the work:

- **FLOOR = 1344** (bottom 30%). Graphics are *authored* never to cross it.
- **The presenter's head top is measured per clip and per moment**, typically
  1050–1100. It is *higher* than the floor suggests, so authoring to the floor
  is not enough — see §6.

---

## 1. Inputs

| what | where it comes from | notes |
|---|---|---|
| **presenter clips** | HeyGen, one `.mp4` per part | 1920×1080 landscape, green screen |
| **caption SRTs** | HeyGen, shipped beside the clips | accurate to ~1s; **verify, never assume** |
| **question, year, marks** | the Google sheet row | marks are *not* in the sheet — take them from the script header |
| **answer pages** | Drive, named `<QID>_1.png`, `<QID>_2.png` | the **house sheets**: ruled paper, blue handwriting, Arivihan watermark, pencil diagram inline |
| **figures** | `inbox/ncert_bio/figures/*.png` | textbook scans, traced — never generated |

**Two traps, both hit in practice:**

- The sheet's *"Question Answer Image Link"* column links **raw textbook scans**,
  not the house answer sheets. The house sheets are separate Drive files named by
  question ID. A textbook scan on the end of a video is the wrong artefact.
- A cached read of the sheet **goes stale**. Re-fetch it; the house sheets were
  added days after one snapshot and were invisible in it.

Stage everything under `inbox/<slug>/part<N>.mp4` and `part<N>.srt`.

---

## 2. Verify the SRT before trusting it

The SRT is the clock's starting point. Check it against the clip:

```bash
for p in 1 2 3; do
  echo "$(grep -o '[0-9][0-9]:[0-9][0-9]:[0-9][0-9],[0-9][0-9][0-9]' inbox/<slug>/part$p.srt | tail -1)" \
       "$(ffprobe -v error -show_entries format=duration -of csv=p=0 inbox/<slug>/part$p.mp4)"
done
```

Last cue within ~0.05s of the clip length means the file is honest. One vitamins
SRT disagreed with its own audio by up to **4 seconds** and had to be thrown away.

---

## 3. The project scaffold

```
projects/<slug>/
  meta.json                 question, years, marks, hilite terms, clip_end
  script.md                 front-matter only: theme, orientation, chroma
  assets/design/question_sheet.png   the card art, built per question
  beats_part<N>.json        [] for these videos (Manim beats unused)
  lines_part<N>.json        the caption track          ← generated
  words_part<N>.json        Whisper word timings       ← generated
  plan_part<N>.json         graphic windows            ← generated
  card_part<N>.json         [[0.0, handover]]          ← generated
  keys/part<N>.json         chroma key parameters      ← measured
  crop_part<N>.json         presenter crop             ← measured
  manim_code/pyq_composed.py         ← must be recomposed, see §4
  final/<pre>_part<N>.mp4
```

`meta.json`:

```json
{ "subject": "Biology", "years": "2019, 2022", "marks": 4,
  "question": "…", "hilite": ["…"],
  "clip_end": {"1": 123.80}, "card_lines": {"1": 5} }
```

`hilite` terms are picked out in gold in the captions when they appear as whole
words. **`marks` is required** — preflight fails without it.

**Recompose after scaffolding, or the card render fails:**

```bash
cp projects/_pyq_template/scene.py projects/<slug>/manim_code/pyq.py
PYTHONPATH="$PWD" python -c "
from tools.recompose import main
main([('projects/<slug>/manim_code/pyq.py',
       'projects/<slug>/manim_code/pyq_composed.py',
       'projects/<slug>/script.md')])"
```

---

## 4. The question card

A torn corner of the real exam paper, photographed. `tools/paper_header.py`
rewrites only the **subject line**, the **question** and the **year** on it,
leaving the creases, torn edge, QR and SET stamp exactly as approved.

```python
import paper_header as ph
ph.DESIGN = Path("inbox/sticky_note_design.png")   # the approved blank design
ph.build("biology", Path("projects/<slug>/assets/design/question_sheet.png"),
         question=meta["question"], year="2022")
```

- **`year=` is mandatory.** The design prints `वर्ष / Year - 2026`; without this
  every card claims 2026 whatever year the question was set. For a multi-year
  question use the latest — a paper header can only be one year.
- The **subject separator is a plain hyphen**: `जीव विज्ञान - BIOLOGY`. It was an
  en dash (U+2013) in the design, which a search for `—` will never find.
- If `inbox/sticky_note_design.png` is missing, a **finished sheet can stand in**
  — but only one whose own question fits inside the erase band, or the widened
  erase flattens the paper's diagonal fold into a pale block.

**The question text is baked into the PNG.** Editing `meta.json` afterwards
changes nothing on screen. Re-render the sheet, then re-render the card.

---

## 5. The caption track

Two stages, in this order.

**5.1 Text and rough times from the SRT**

```bash
python tools/lines_from_srt.py inbox/<slug>/part1.srt projects/<slug>/lines_part1.json
```

Splits export cues (up to 9s) into house-style lines: `MAX_WORDS 10`,
`MIN_WORDS 4`, cut at strong punctuation first and commas only as a last resort.
It also normalises: `B one → B₁`, `Notes button → नोट्स बटन` (that one matters —
`answer_overlay.py` finds the answer cue by matching it), and **every em/en dash
becomes a plain hyphen**.

**5.2 Both ends onto the audio's own word clock**

```bash
python tools/transcribe.py inbox/<slug>/part1.mp4 projects/<slug>/words_part1.json
python tools/retime_lines.py projects/<slug>/words_part1.json projects/<slug>/lines_part1.json
```

`retime_lines.py` sets `start` to when the line's first word is spoken and `end`
to when its last word finishes plus a short tail — so a caption **comes down
during a pause** instead of hanging on stale. Its design, all of it learned the
hard way:

- **Search is windowed (±2.5s) and forward-only.** A global match cannot separate
  two lines whose consonant skeletons are identical — `आई ए एलील A एंटीजन…` and
  `आई बी एलील B एंटीजन…` differ only in ए/बी — and it moved one by 3.5s onto the
  wrong occurrence.
- **A second pass** re-searches the lines that failed, centred on a time
  interpolated between the confident neighbours. Without it, a stretch drifting
  ~3s stays unplaced and shows the words spoken two lines later.
- **Bunched runs are spaced evenly.** Lines the aligner cannot separate land on
  one word and get fanned out by the minimum gap, producing 0.35s caption
  flashes. Unreadable, and worse than being slightly late.
- **`MAX_MOVE = 2.50`** is a backstop matching the window, not a tuning knob. At
  1.20 it fought the aligner and cost 16 points of accuracy.

**Score it. Do not eyeball it.** For every caption, take the words spoken while
it is on screen and measure what fraction of its tokens appear among them:

| median overlap | verdict |
|---|---|
| ≥ 75% | good |
| 60–75% | acceptable; weak transcript is usually the cause |
| < 50% | broken — investigate before building |

Measured before/after on real parts: 50→78%, 70→83%, **29→85%**, 40→74%.

A **global offset check is not this test.** A track can be perfectly centred and
still be wrong line by line; that mistake cost a full rebuild cycle.

---

## 6. Screen graphics

Two kinds. Both are burned onto a **finished, composited** video in one ffmpeg
pass, so nothing upstream is re-rendered or re-encoded.

### 6a. Chips — static PNGs

Authored in `tools/edu/renderer/spec/chips/<name>.json`, rendered by

```bash
cd tools/edu/renderer && node bands.mjs spec/chips/<name>.json out/chips/<name>
```

Each entry is `{slug, mode, …params, h}`. Modes in `overlays/band.html`:

| mode | for | key params |
|---|---|---|
| `points` | a numbered list | `title`, `items`, `show` |
| `table` | two or three columns | `head`, `rows` (`;` between rows) |
| `define` | a definition, 2–3 lines | `title`, `lines` (`|` between) |
| `cols` | a two-way contrast | `heads`, `items` |
| `math` | a derivation, KaTeX | `lines` (`@@` between), `lead`, `from` |
| `svg` | a figure with Devanagari labels | `svg`, `labels`, `hide` |
| `photo`/`triptych`/`compare` | photographs | `photo(s)`, `pins`, `tag` |

**`svg` mode is how a labelled diagram is done.** The SVG carries only the
picture and any Latin text (`RR`, `Rr`, `5'`); Devanagari labels are placed by
the chip renderer at normalised coordinates with leader lines drawn twice — dark
under, light over — because one colour vanishes against either the plate or the
figure.

Figures come from `tools/ncert_svg.py` (traced from the textbook scan as clean
vector art) or are authored per figure when the generic tracer can't cope —
`tools/embryo_sac_svg.py` exists because the generic path fits one ellipse
inside one silhouette, which swallowed all seven cells of the embryo sac.

### 6b. Animated clips — transparent `.mov`

Manim renders at 1080×1920 with `--transparent`, composited over the plate
afterwards. **Never add the plate as a fixed-in-frame `ImageMobject`** — it
silently hides every `Surface` and `Cylinder`, and the shaded helix vanishes
while the stroke-only callouts still draw.

Burned by `tools/burn_clips.py`. It **plays once and holds the last frame**:

- **Never loops.** All eight helix clips build and end still — measured, first
  frame against last differs by 6–15 grey levels. Looping replays the build and
  the labels pop in again every few seconds.
- **Never reverses.** Boomerang would show DNA un-coiling and hydrogen bonds
  coming apart — wrong in a way that looks completely fine.

---

## 7. Placement — the part that ships broken

A graphic must clear the presenter's head, and **the head is measured, not
assumed**. It moves: 978 to 1098 across one question's three parts.

```bash
python tools/fit_chips_above_avatar.py <prechip.mp4> <bg.mp4> <plan.json>   # chips
python tools/lock_chip_family.py <plan.json> <chips_spec.json>              # chips
python tools/fit_clips.py         <prechip.mp4> <bg.mp4> <plan.json>        # clips
python tools/avatar_clearance.py  <prechip.mp4> <bg.mp4> <plan.json>        # the gate
```

- **Chips are raised**, down to `CEIL = 176`, keeping `CLEAR = 28`px of daylight.
  If a chip still won't fit, it must be **shrunk** — `h` in the spec. Diagrams
  authored at 900px tall did not fit at any position; 820 (ovule) and 770 (sac)
  do.
- **Clips are scaled**, not raised — a full-frame render has its title at the top
  and moving it down pushes the whole thing into the presenter. `fit_clips.py`
  solves for the scale that clears the measured head.
- **`lock_chip_family.py` gives every chip drawing the same SVG one top per
  part.** The fitter places each chip as low as it can *at its own moment*, and
  the presenter moves between moments — so three views of one diagram got tops
  221, 230 and 223 and the figure visibly bobbed between them.

**All four parts of one question once reached `final/` with every chip 220px
inside the presenter's face, and the output gate passed them** — it checks
encoding, not layout. Run the clearance check *before* burning.

---

## 8. Timing — when each element appears

**The question card** holds from 0 to a handover time recorded in
`card_part<N>.json`, snapped to a caption boundary. The card *animates for about
3.3s* and is a still picture after that, so the handover number really means
"how long do we hold a frozen frame while he talks with no captions under him".

- Good: **5–8s** of hold after the animation.
- One part held **12.2s** and read to the reviewer as *"captions are late"* —
  the captions were fine; there simply weren't any.

**Graphic windows** are anchored to the *text* of a caption line, never to a
hard-coded second, so they survive the clock changing underneath:

```python
WINDOWS = { 1: [("p1-defn", "जब किसी विषमयुग्मजी", "और परीक्षा में ये परिभाषा"), … ] }
```

`(slug, comes-up-on, gives-way-to)`. Windows butt — one ends where the next
begins — because two graphics cross-fading reads as ghosting. `LEAD = 0.40`
brings a graphic up slightly before its line, since it fades in.

**Captions go quiet under a graphic.** A segment fully inside a window is emitted
with `"captions": "off"`. Typical quiet fraction 45–70%; higher for clips that
carry their own titles.

**"No graphic" is a valid answer** and the quiet stretches matter. `p4c-order`
was built and deliberately left unused because the faculty dropped that line from
the recording — a graphic the narration doesn't support is worse than none.

---

## 9. The build

```bash
bash tools/build_bio<N>.sh <part>
```

Stages, in order:

1. **caption body** — `node full.mjs` with `BG=assets/biology-background.png`.
   The default is the chalk plate; forgetting this puts flasks and test tubes
   behind a biology video.
2. **question card** — Manim, `PYQ_UNTIL=<handover+2>`. Cached, but the cache
   must watch the **sheet** as well as `meta.json`, or a corrected card never
   ships.
3. **background** — card + body concatenated, `tpad`-padded, cut to clip length.
4. **composite** — `tools/composite.py` keys the presenter using
   `keys/part<N>.json` (from `calibrate_key.py`) and `crop_part<N>.json` (from
   `avatar_crop.py`). Both are **per clip**: three clips from one shoot needed
   three different value references, and a fixed crop sliced a presenter's
   forearm mid-frame.
5. **fit → lock → clearance gate** (§7) — refuses to burn if anything reaches
   the presenter.
6. **dash gate** — `tools/dash_gate.py`.
7. **burn** chips or clips.
8. **output gate** — `tools/output_gate.py`.

Set `FFMPEG_THREADS=3`. Not higher: unbounded x264 took ~300% of eight cores and
left the machine unresponsive.

**Run one heavy job at a time.** On 8 GB, a composite alongside a Whisper
transcription put 13 GB into swap, doubled the composite (26 → 47 min) and got
another composite killed with SIGTERM. Sequential is the same total and delivers
sooner.

---

## 10. The answer page

```bash
python tools/answer_outro.py in.mp4 <QID>_1.png out.mp4 \
    --then <QID>_2.png --hold 7 --then-hold 7
```

Fades up over the last frame of the **last part only**, holds long enough to read
or screenshot, fades out. Card is `0.86 × 0.82` of frame; blank paper below the
last line is trimmed so the handwriting is as large as it can be.

Use `answer_overlay.py` instead — bringing the page up *on* its cue and holding
to the end — only when the narration promises it on screen
(*"स्क्रीन पर आ जाएगा"*). If the close is the Notes-button line, `answer_outro`
is correct.

---

## 11. The gates

| gate | catches | when |
|---|---|---|
| `dash_gate.py` | em/en dash in any screen text; **an artefact older than its spec** | before burning |
| `avatar_clearance.py` | a graphic reaching the presenter | before burning |
| `output_gate.py` | encoding, geometry sidecar, presenter placement | after burning |
| the caption overlap score (§5) | captions off the words | after re-timing |
| `band_check.sh` | pixels in the presenter band, in 3D scenes | after a Manim render |

**The staleness check is the important half of the dash gate.** A chip spec was
de-dashed and the PNGs were never re-rendered, so two delivered parts kept
showing an em dash. *A fix that stops at the source is not a fix* — only a
timestamp comparison catches it.

**No automatic gate sees 3D layout.** `bio_common`'s gate reasons about
world-space boxes, and a projected 3D body's box says nothing about where it
lands on screen. Every label defect in the helix clips — a base pair hidden
behind a strand, a diameter label sitting on the model, a ruler 28° out of
alignment because the camera kept turning after it was drawn — was found by
looking at frames.

---

## 12. Editing a finished part

```bash
python tools/cut_and_dissolve.py in.mp4 out.mp4 <cut_start> <cut_end> [dissolve]
```

For a stumble or false start. **Picture dissolves, sound butts** — a crossfade
would blend across the first syllable of the word the cut lands on and make it
sound like it fades in. Find the boundaries from the word timings, not by eye:

```python
[w for w in words if 128 <= w["s"] < 142]      # locate the stumble and the next word
```

---

## 13. Delivery

`~/Desktop/Final Biology/<QID> — <Hindi title>/<English Title> - Part N.mp4`,
matching the `Final Chemistry` / `Final Physics` convention, with the
`.geom.json` sidecars.

**Verify each delivered file by checksum against the source.** "Ready" and
"delivered" came apart once: a corrected video sat in `projects/` while the old
one stayed on the Desktop.

---

## 14. The checklist

Before calling a part done:

- [ ] SRT last cue within 0.05s of the clip
- [ ] caption overlap ≥ 75% median, few lines under 30%
- [ ] no caption shorter than 0.8s
- [ ] card handover leaves ≤ 8s of frozen card
- [ ] every graphic clears the presenter (positive clearance, printed)
- [ ] one top per figure family per part
- [ ] dash gate passes, **including the staleness half**
- [ ] output gate passes
- [ ] final duration matches the clip (unless deliberately cut)
- [ ] answer page appended to the last part, house sheet not textbook scan
- [ ] delivered copy checksum-matches the source

---

## 15. Failure modes seen in practice

| symptom | actual cause |
|---|---|
| "captions are late at the start" | the question card held 12s frozen; captions were fine |
| "captions out of sync at various points" | per-line error; the global offset was ~0 |
| captions flashing | aligner bunched lines; monotonic fanned them out by 0.35s |
| chips in the presenter's face | authored 900px tall; nothing that tall fits |
| a diagram bobbing between views | per-chip fitting, presenter moved between moments |
| em dash still on screen after the fix | spec corrected, PNG never re-rendered |
| wrong background | `full.mjs` defaults to the chalk plate |
| card render fails | `pyq_composed.py` never recomposed |
| body render fails, Playwright error | Chromium cache wiped — `npx playwright install chromium` |
| composite killed / very slow | another heavy job running; 8 GB machine swapping |
| textbook scan on the end of the video | wrong Drive column; house sheets are separate files |
