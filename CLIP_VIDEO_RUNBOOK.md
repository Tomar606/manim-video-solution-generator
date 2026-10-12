# Building a PYQ video from an existing HeyGen clip

Follow this top to bottom and the video comes out right on the first render.
Every rule here exists because skipping it cost a full rebuild — each one names
the defect it prevents.

> **The commands below are what `tools/build_clip.py` runs for you** (PROCESS.md,
> "Running it"). This page is the reasoning behind each step and its gate; read
> it when a gate fails or a step needs judgement. The renderer is `tools/clip/`
> — one copy, never copied into a video folder.

> This is a **third track**, distinct from the two in `PIPELINE.md`:
>
> | | reels | PYQ / Manim | **this one** |
> |---|---|---|---|
> | Renders with | Manim | Manim | `skill/edu-video` — headless Chromium + KaTeX + hand-written SVG |
> | Clock | synthesized narration | the HeyGen clip | **the HeyGen clip** |
> | Needs | Manim + LaTeX | Manim + LaTeX | **Node + ffmpeg only** |
>
> The edu-video skill normally owns the clock: fixed ~10s segments, HeyGen
> records afterwards. **Here the clip already exists, so the clock runs the
> other way and everything bends to it.** That inversion is the source of most
> of the traps below.

---

## 0. One-time setup

```bash
brew install ffmpeg whisper-cpp                       # required
cd tools/clip && npm install && npx playwright install chromium   # ONCE, not per video

python3.11 -m venv .venv-tools                        # repo root
.venv-tools/bin/pip install numpy scipy pillow openai-whisper
```

**Anything that draws Devanagari must run on the SYSTEM python3, not
`.venv-tools`.** Its Pillow reports `features.check("raqm") == False`, and
without libraqm Pillow lays Devanagari out in storage order — every matra lands
after its consonant, silently, with no error. `.venv-tools` is for numpy/scipy/
whisper only. Check before writing any card:

```python
from PIL import features; assert features.check("raqm")
```

---

## 1. Gather and cross-check the inputs

| input | where |
|---|---|
| clip + SRT | `inbox/<subject>/` |
| script PDF | for correct notation only — **not** for caption wording |
| the question | Google Sheet, via `src.pyq_writer.load_questions("<Subject>")` |
| background plate | 4320×7680 → downscale 4:1 |

```bash
ffprobe -v error -show_entries format=duration -of csv=p=0 <clip>   # vs SRT last cue
sips --resampleHeightWidth 1920 1080 PLATE.png --out assets/<subject>-bg.png
```

The clip duration and the SRT's last cue end must agree within ~50ms. If they
don't, the SRT belongs to a different take — stop and check.

**The sheet's question text is OCR'd off the paper and carries scanning
errors.** On CHE-C4-LA-02 it read `छुदाहरण` for `उदाहरण` and `परमैंगनेंट` for
`परमैंगनेट` — and the card that shipped has the typo printed on it. Fix the
notation against the script PDF; keep the sheet's wording otherwise, because the
card is a picture of what the exam *asked*.

**Clip filenames lie.** Match on the question text and on the year the part 1
audio actually speaks.

---

## 2. Transcribe, and check the transcript before trusting it

```bash
PYTHONPATH=. .venv-tools/bin/python tools/transcribe.py <clip> work/<slug>/out/words_part1.json
```

Then two checks, both mandatory:

```python
w = json.load(open("out/words_part1.json"))
[ (a["e"], b["s"]) for a,b in zip(w,w[1:]) if b["s"]-a["e"] > 1.5 ]   # holes
[ x for x in w if float(x["e"])-float(x["s"]) > 1.3 ]                 # collapsed tokens
```

- **Holes** are Whisper dropping audio silently — the documented failure in
  `tools/README.md`. Fix with `tools/fill_gaps.py`.
- **Collapsed tokens** are the failure that bit this build: the `medium` model
  emitted `'अपचेएइत'` spanning 42.62–48.00 and `'होता'` spanning 48.00–53.96 —
  two "words" swallowing 11 seconds. A Hindi word cannot last six seconds.

**Whisper is used for ONE thing only: finding where a named word ends inside a
cue.** It is not the authority for cue boundaries. Confirm the SRT is, by
cross-correlating its cues against the audio envelope — expect ≳95% of speech
inside a cue and a global lag under ~0.15s.

**That test is necessary and NOT sufficient — check each boundary too.** It
measures whether the cue *spans* cover the speech, and they can cover it while
individual boundaries sit anywhere inside. CHE-C4-LA-03 part 1 passed it at
98.2% with a best global shift of −0.10s, and its cue starts were still wrong by
−2.26s to +1.47s: cue 8 was 1.43s late, cue 14 was 2.26s early, cue 23 put the
six-number count 1.89s after he began it. Built on those cues the ladder showed
its FIRST rung while he was saying the THIRD number.

So match every cue's opening words to the transcript and print the offset:

```python
from tools.align import skel          # consonant skeleton — Whisper misspells
                                      # freely and may answer in either script
want = [skel(x) for x in cue["text"].split()][:3]
# best difflib ratio over transcript positions within ±3.2s of cue["s"]
```

Anything over ~0.5s is a real boundary error, not transcription noise. Where he
pauses, the silences in `out/anchors.json` are an independent second opinion and
outrank both the SRT and Whisper — a run of evenly spaced silences through a
counted list marks each item exactly. When the SRT loses, **the spans come from
the measured onsets**: sync is about the words, not the clock, and that applies
to the file the words came in as much as to anything else.

---

## 3. Group the SRT cues into visual beats

One segment = one run of consecutive cues that share **one visual idea**. A
segment ends when the picture should change, not on a stopwatch. Part 1 of the
KMnO₄ video was 21 cues → 8 segments.

Segment boundaries are cue starts; a segment's duration is the next segment's
start minus its own. Round to 2dp and make the totals add to the clip length.

---

## 4. Draw the SVGs

Rules from `skill/edu-video/references/diagram-recipes.md`, plus two learned here:

- `viewBox` is always `0 0 1080 470`. Never change `--stage-h`.
- **No `<text>` elements.** Every word comes from the spec so the render audit
  can verify it. Don't write `<text` in a comment either.
- Every animated part needs its own `id` and `data-optional`.
- Strokes ≥6px, main bars 14–18px, circle r ≥14. Fill x 150–950, y 70–400.
- Solid strokes on straight lines — a gradient on a zero-height bounding box
  renders invisible.

**Any box that will hold a Devanagari label must be ≥100px tall.** A 46px
Devanagari label measures **69–76px high** — matras above and below — plus
`pop_in` overshoot. QA fails a label taller than its container minus 8. A 76px
box looks fine in the SVG and fails on every frame. *QA prints the label's
WIDTH in that message, so it reads as a width problem.*

**Transparency is `fill-opacity` / `stroke-opacity`, never `opacity`.** The
engine drives `style.opacity` 0→1 for every animated id, which overrides the
attribute — a 55% violet solution rendered as a flat opaque slab.

Avoid id prefixes `g_` / `e_` / `cmp_g` / `cmp_e` / `gal_` / `ele_` unless you
mean them: QA reads those as "two topics on screen at once".

---

## 5. Write the spec — the timing rules are the whole game

`build_spec.py` in the working copy. Author the beats by hand; let code do the
timing. **Getting any of these wrong means a full re-render.**

### Captions

**One caption per SRT cue.** The SRT is the script: it carries the exact span of
every line, so a caption should be a line.

```
t_in  = the SRT cue's START
t_out = the SRT cue's END          <- both ends. Not "next start minus 0.2".
```

Split a cue **only when its text cannot fit the band** — over about 100
characters, which is 3 lines at the smallest caption size. Every split is a time
the SRT did not give you, and therefore a chance to be wrong. Part 1 has 21 cues
and 23 captions: only two cues needed splitting.

**A caption must cover every word of its cue.** Shortening a long line instead
of splitting it drops words silently. Cue 13 lost `सबसे पहले — अम्लीय माध्यम`
that way, so for the last two seconds of the cue he was saying one thing and the
screen showed the sentence before it. The timing was perfect and it still read
as out of sync, **because sync is about the words, not only the clock.** Gate it:

```python
# Devanagari only - the SRT writes formulae in spoken Latin ("kmno four")
# and the caption writes them as notation, so those never match token for token
missing = difflib.SequenceMatcher(None, dev(cue_text), dev(captions_for_cue))
if any deleted/replaced: raise
```

Deriving the end as `next_t_in - 0.2` throws away the SRT's own end times, and
many cues run **back to back** (cue 2 ends 9.541, cue 3 starts 9.541). That cut
0.2s off every caption. Combined with the engine bug in §6 the caption was gone
**0.42s before the teacher finished the sentence, on every line** — which is
what "the captions run faster than the dialogue" is.

**Splitting a long cue.** An 8-second, 20-word cue is three caption lines and
must be split. The split is the **end of the last word of the earlier caption**,
found by fuzzy-matching that word in the Whisper transcript — with the caption's
word count giving the search a place to start.

Do *not* apportion the cue's duration by syllable weight, and do not snap to the
quietest moment. Both put the split 1–2 words early: the caption changed on
"KMnO4" while the line still had "का" to go. Verify each split lands on the
right word:

```
6.60   caption ends "है"      -> word "है" ends 6.60      ✓
26.84  caption ends "उदासीन"  -> word "उदासीन," ends 26.84 ✓
```

**Hold through short pauses.** Where the SRT leaves a gap ≤0.8s, run the caption
on to the next one. An empty band across a breath reads as the caption leaving
early. Only a real beat (>0.8s) is left blank.

### Animation

**Anchor every step to the cue it illustrates — or to the spoken word.** Never
write a bare offset into the segment, and never author times by hand and correct
them afterwards; that is backwards, and it is why the screen keeps ending up a
beat away from the voice.

```
("c",  n, dt)         dt seconds after cue n starts
("ce", n, dt)         dt after cue n ENDS (dt usually negative)
("w", "शब्द", n, dt)  dt after that word is spoken, searched inside cue n
```

Word anchors are what make the screen *relevant*: the three medium chips appear
on `अम्लीय`, `क्षारीय`, `उदासीन` as he names them; `Mn²⁺` lands on the cue that
states it. Whisper spells its own way and sometimes breaks one word across two
tokens (`ऑक्सीकारक` came out `AUXI` + `कारग`), so an anchor may carry alternate
spellings and the search also tries adjacent pairs. **A miss must print loudly** —
a silent fallback to the cue start is exactly the half-second drift being
removed.

**Every label needs a `t_out`.** A label without one stays until the segment ends
and the DOM is rebuilt — when the diagram faded at 14.2s, seven labels went on
floating alone on a bare plate for the last 0.9s. Set each segment's label
fade-out to the moment its shapes fade. A segment whose diagram *carries* into
the next one gets no `t_out`.

**Clear at `end − 0.24` over 0.22s, not at `end − 0.55` over 0.50s.** The DOM is
rebuilt at the segment boundary, so a long dissolve buys nothing — and it is
spent in exactly the wrong place. A fade scheduled at `end − 0.55` is visibly
taking the picture down for the last half-second of the sentence, which is what
"the animation ends before he finishes speaking" looks like from the classroom.
CHE-C4-LA-03 part 2 shipped that way on all eight of its fade schedules: even
after its spans were re-synced, the stage still read empty 0.32–0.50s before he
stopped talking, and tightening the fades took that to 0 of 10 segments.

Label `t_out`s move with the shapes they name — a label outliving its diagram by
a third of a second is the floating-label defect above, in miniature.

Measure it on the delivered pixels rather than believing the spec: sample the
stage band at 10 fps, take the last tick above the ink threshold in each
segment, and compare it against the end of the last word the transcript puts
inside that segment. Anything under about −0.25s reads as early to a viewer.

### Equations

Hindi through the caption, formulae through KaTeX — the two render by different
paths and cannot be mixed. Wrap each row of a `gathered` block in `\mathrm{}`:
KaTeX defaults to italic, so `KMnO_4` renders as the product of variables K, M,
n and O, and no board answer sheet prints it that way.

Never give a segment both a `diagram` and an `equation` — `#stage` and `#eqWrap`
occupy the same 470px band.

---

## 6. Engine patches that must be present

These live in `tools/clip/engine/engine.js`, the one engine every video renders
with (bug ledger entries 26–29). `skill/edu-video/` and `tools/edu/` are older
copies and do NOT all have them — never start from either.

| what | why |
|---|---|
| `goldenize` uses Unicode lookarounds `(?<![\p{L}\p{M}\p{N}])…` | JS `\b` is defined against `[A-Za-z0-9_]`, so it never fires beside a Devanagari letter or a subscript digit. `\bक्षारीय\b` and `\bKMnO₄\b` both fail on text that plainly contains them, and goldenize **threw on every Hindi phrase**. |
| equation auto-fit to 900×250 | A balanced chemical equation is 1706px wide in a 940px box and ran off **both** edges. Two traps: make `eqWrap` `display:flex` **before** measuring (a `display:none` subtree measures 0×0 and the fit silently becomes 1.0), and `document.fonts.load()` the KaTeX faces explicitly (`fonts.ready` resolves instantly for a face nothing has asked for, so the measure is taken against a fallback). |
| caption `pop_out` at `t_out`, durations 0.16 | It fired at `t_out - 0.22`, taking the caption down before its own end time. `t_out` means "the line is finished". |
| equation fit scale capped at `MAX_K 1.85`, not at `1` | The cap belongs on GROWTH, not on shrinkage. A balanced chemical equation needs shrinking; a SHORT one — `(n-1)d¹⁰ ns²` is 380px inside a 900px box — was pinned at k=1 and rendered smaller than the caption band above it. The two ratios beside `MAX_K` still make overflow impossible. |

---

## 7. Gates — run all three, in this order

```bash
python3 tools/clip/validate.py <slug> --part N   # the spec on paper
node tools/clip/qa.mjs <slug> --part N           # the spec on PIXELS, 0.2s steps in a real browser
node tools/clip/full.mjs <slug> --part N         # renders, and audits every string against the spec
```

`validate.py` must be adapted for a clip-driven clock, and this is not bending
QA to pass — the original rules assume the *spec* owns the clock:

- **gap between phrases**: was "exactly 0.2s". The gap is now whatever pause the
  teacher takes — 0.0 back-to-back, 0.4 where he stops. Overlap is still an
  error. Forcing 0.2 everywhere is what cut every caption short.
- **minimum phrase duration**: was 2.5s. A caption lasts as long as he spends on
  that line; stretching a 1.6s line to 2.5s puts it over the next sentence.
  Below 1.4s errors, 1.4–2.5s warns.

`words/sec` warnings are meaningless here — the audio already exists.

Never render past a FAIL. Fix the timing or the diagram, not the check.

---

## 8. Render, then build the intro card

```bash
node tools/clip/plate_frame.mjs <slug>                       # -> out/plate.png, captions removed
python3 tools/clip/make_intro_layers.py <slug> "<year>"      # a Pillow WITH libraqm
node tools/clip/full.mjs <slug> --part 1 --pages 2 --intro   # -> out/render-part1.mp4, card drawn in
```

The card is drawn into the render's own frames (§9 describes the overlay it
replaced: same timing — opaque from frame 0, dissolving over the last 0.5s of
segment 1 — without a second encode of the part). `tools/clip/intro.mjs` still
renders the card as its own video when one is needed on its own.

**The intro card carries the plate.** Captions are baked into the render and
cannot be suppressed afterwards, and the card's heading, rule and sheet have
gaps that a caption reads straight through. So the card is drawn *on* the plate,
opaque down to y=1290 (just above the presenter's head at 1344) and transparent
below.

**The plate must be a render of the page, not the raw PNG.** `style.css` lays a
radial `--scrim` over the top 960px for legibility; the raw plate is visibly
lighter and leaves a hard tonal seam where the card ends. Lifting a frame from
the finished video also works *only if* a caption-free moment exists — once
captions hold through pauses, none does. `tools/clip/plate_frame.mjs` renders one with the
caption element emptied: same browser, same CSS, same scrim.

Card geometry comes from `src/question_card.py` — every number is a fraction of
the frame, measured off the approved still. One thing does not transfer: the
spark wedges are specified at Manim's stroke scale and come out fat; use
`0.155 / 0.013 / 0.038` of a unit, not `0.24 / 0.020 / 0.062`.

The question sheet itself is `tools/paper_header.py`. It rewrites two lines on a
photograph rather than redrawing it, because the paper is creased, unevenly lit,
torn and rotated 2.7°. Notes:

- `Q_FONT` points at `~/Library/Fonts/NotoSansDevanagari.ttf`. If absent, the
  repo's vendored `Poppins-Regular.ttf` is a clean substitute.
- **`Q_INK_H = 78`, not the default 98** — 98 renders visibly heavier than the
  batch. Match by measuring ink-pixels per character against a shipped card.
- Reducing the ink height **raises the whole block**, because rows are anchored
  at `Q_TOP + i·pitch − baseline + Q_INK_H×0.80`. Compensate, or the first line
  sits 11px above the `(1)` it should share a baseline with. Target: numeral
  bottom − line-1 bottom within **+0 to +3**.
- If you use another project's sheet as a stand-in design, **pre-clear a wider
  band first**. `build()` only erases x 345–1020 / y 815–1032, but text starts at
  x=330 and runs to ~y=1100, so a sliver of the old question survives and prints
  under the new one. Those were the stray ticks before `माध्यम` and `ऑक्सीकारक`
  — every font showed them; it was never the font.

---

## 9. Overlay the card

```bash
ffmpeg -v error -i out/<slug>-part1.mp4 -framerate 30 -loop 1 -i assets/intro_card.png \
  -filter_complex "[1:v]format=rgba,fade=t=out:st=9.50:d=0.45:alpha=1[card];
                   [0:v][card]overlay=0:0:enable='lt(t,9.96)':format=auto,format=yuv420p[v]" \
  -map "[v]" -c:v libx264 -crf 20 -preset medium -movflags +faststart \
  -t <clip_dur> out/bg-intro.mp4 -y
```

No fade **in** — an opaque panel fading in would reveal the captions beneath it.
Hold from frame 0, then dissolve out as the first explanation caption arrives.

---

## 10. Measure the presenter, per clip

Neither of these is portable. A crop right for one shoot slices a forearm off
the next; a key tuned for one lighting punches holes through the next face.

```bash
PYTHONPATH=. .venv-tools/bin/python tools/calibrate_key.py <clip> out/key_part1.json
PYTHONPATH=. .venv-tools/bin/python -c "
from pathlib import Path; from tools.avatar_crop import measure; import json
json.dump(measure(Path('<clip>')), open('out/crop_part1.json','w'), indent=1)"
```

`calibrate_key.py` should report **hole ≈ 0%, leak ≈ 0%**. The key is hue-based
and applied twice at different value references — an RGB-distance `chromakey`
wide enough for the screen's dark side also matches skin midtones and punches
through the face.

`avatar_crop.py` needs scipy. It grows out from the bottom centre rather than
boxing everything not-green, because the shoot has a whiteboard at the left edge
that a plain not-green box swallows.

---

## 11. Composite

```bash
PYTHONPATH=. .venv-tools/bin/python tools/composite.py \
  out/bg-intro.mp4 <clip> out/key_part1.json out/<slug>-final.mp4 \
  - - - - out/crop_part1.json out/card_part1.json
```

Positional, `-` to skip: `5 windows · 6 presenter · 7 clips · 8 big · 9 crop · 10 card`.

Presenter sizing — `composite.py`'s constants already target this renderer
("the edu-video stage ends at y=850"):

| state | width | head | when |
|---|---|---|---|
| `CARD_W` 423 | | 69% | the question card is up |
| `FULL_W` 645 | | 51% | **anything on the stage** — strictly below half |
| `BIG_W` 780 | | 41% | captions only, nothing on the stage |

Write the card window as `[[-1.0, <end>]]` — the ease straddles each edge by
`EASE/2`, so starting at 0.0 leaves him mid-size on frame 1.

**Don't reach for the "big" size if there's a card** — the card occupies the
stage. Derive genuinely-empty stretches from the spec (ask the engine, don't
guess) and drop any under ~4s; a resize across a 1s gap reads as a twitch.

Five recorded failures live in `composite.py`'s comments. The one that matters:
**`scale` cannot resize per frame.** It is `zoompan` on colour and alpha as
separate streams, keyed to `on` (the output frame number) — not `it`, not `ot`.
Testing `scale=eval=frame` with `-ss` on both inputs *looks* like it works,
because `-ss` resets the filter clock and the expression never varies.

---

## 12. Verify before delivering

```bash
ffmpeg -v error -i out/<slug>-final.mp4 -f null -     # silence = clean
```

Then, on the delivered pixels, not the spec:

- **captions hold to the end** — sample the caption band 0.06s before and 0.30s
  after each `t_out`; ink before must be substantial, and different after.
- **presenter geometry** — diff the final against `bg-intro.mp4` (the *same*
  encode it was composited onto; diffing the pre-card render makes the card and
  re-encode noise read as "presenter") and take the topmost differing row. Expect
  ~70% under the card, 53–55% after, never above 50% while anything is on stage.
- **stage fills and empties** — count bright pixels in y 380–900 at a few
  timestamps. A beat that should be clear must read near zero.
- **captions only on an empty screen** — `check_captions.py <file>.mp4`. Attribute
  each sample to the segment owning the SOURCE FRAME it came from, on the 30fps
  grid the render is laid out on. Deriving the range from the 4fps sample clock
  puts the tick at 94.500s (frame 2835) inside a segment that ends at frame 2834,
  and reports the NEXT segment's own first caption as a caption over a graphic.
  A gate that cries wolf gets ignored.

---

## The order, in one block

```
0  setup                      ffmpeg · whisper-cpp · npm in tools/clip ONCE · .venv-tools
1  inputs                     clip+SRT · sheet question · plate 4:1 · duration cross-check
2  transcribe                 whisper medium -> words.json · CHECK holes + collapsed tokens
3  segments                   group cues into visual beats
4  SVGs                       boxes >=100px tall · fill-opacity · no <text>
5  spec                       t_in=cue start · t_out=cue END · splits on word ends
                              · hold through pauses · labels get t_out · warp the animation
6  gates                      tools/clip/validate.py -> qa.mjs -> full.mjs   (0 errors, 0 fails)
7  render                     tools/clip/full.mjs
8  intro card                 plate_frame.mjs -> make_intro_layers.py (SYSTEM python3) -> intro.mjs
9  overlay                    ffmpeg, no fade-in
10 measure presenter          calibrate_key.py + avatar_crop.py   (per clip)
11 composite                  composite.py with the card window
12 verify                     decode · caption hold · head geometry · stage fill
```

A full pass is roughly **6–8 minutes of machine time**: render ~110s,
overlay ~40s, composite ~4min. Whisper adds ~10min the first time per clip.

---

## What is in the video folder

Design only — the tools refuse a folder that carries code. See
`work/_template/README.md` for every file.

| file | role |
|---|---|
| `video.json` | background (required, no default), question card, answer pages, layout |
| `theme.css` | optional overrides of `tools/clip/engine/style.css` |
| `spec/parts/design_part<N>.json`, `anchors_part<N>.json` | beats and which caption lines they own |
| `out/caption_edit_part<N>.json` | caption wording per transcript word range |
| `spec/segments_part<N>.json` | generated by `tools/build_spec.py` — never hand-edit |
| `state.json` | which steps are green on which inputs; the storyboard approval |

## Still open

- ~~The intro card is **static**.~~ **Done** — see `work/quathanank-part1/`.
  `make_intro_layers.py` writes the card as nine full-frame RGBA layers instead
  of one flat PNG, and `intro.mjs` stacks them in the same headless browser and
  drives each on its own clock (ring, heading, sparks lagging their word, rule
  drawing outward, sheet dropping, tape, badge, pill rising) over 2.6s. It
  renders 1080x1290 and opaque rather than a full-frame alpha video, because the
  card does nothing below y=1290.

  Two traps it cost:
  - **The presenter must be told about the card.** `stage_windows.mjs` reports
    the card's stretch as an empty stage and grows him straight through it. Drop
    that window and pass a card window instead.
  - **A plate checked at luma > 150 is not checked.** A caption caught mid
    `pop_out` is semi-transparent, lands around 110-130, and ships a ghost
    caption through the card. Use `plate_frame.mjs`, and check at 110.
- Part 2 of any question is a separate pass. **Re-measure the key and crop** —
  they are per clip, not per project. Measured on CHE-C4-LA-03 part 2: this
  presenter gestures wide, so `union_w` came out 1001 against 605 and 769 on the
  two earlier shoots and the crop is 1180 wide. That is correct and must not be
  tightened: `composite.py` already sizes him from the MEDIAN subject width via
  `pad_k`, so the delivered presenter matches the shipped builds to within a
  couple of points (full 48-56% of frame width, big 59-67%). Check the delivered
  pixels before concluding he is too small — he looks it beside a wide crop box
  and is not.
