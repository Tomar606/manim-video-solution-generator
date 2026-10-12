# The arts process

> **Working draft, 2026-10-07; tool column and section 9 updated 2026-10-08** after
> POL-C3-LA-02. The user's answers are folded in (section 10). `tools/reel/` now
> runs steps 3, 6a, 8 and 10; the storyboard and the gates of steps 7, 9 and 11
> are still followed by hand.
> `PROCESS.md` remains the process for science videos.

How an arts video (History, Geography, Political Science, Economics, …) is
built from an already-shot HeyGen clip. The reference point is the Magadha
video (`final/HISTORY-MAGADHA-POC/`, code in `docs/history-poc/`): the
presenter in front, generated scenes behind him, and everything that must be
exactly right drawn by us.

`PROCESS.md` is the science process. This page borrows its spine: one fixed
order, a gate on every step, the voice as the clock. It differs on one point:

> **In science the layout changes and the process never does.
> In arts the whole LOOK changes, every video, on purpose, and the process
> still never does.**

**The one test for every design choice: does it help the student understand
and remember the answer?** Each video must be unique, and it must never be
unique at the cost of that. A beautiful scene that does not teach its sentence
is cut.

**Before drawing anything, read [`arts/DESIGN_RULES.md`](arts/DESIGN_RULES.md):**
the rules from the user's reviews of delivered videos (every element a memory
device, spacing, maps with borders, presenter in the middle, footage backgrounds,
options as stills before a redesign). They apply whatever the look.

So this page has two halves. Sections 2 and 5 are the guard rails: they do not
move. Section 3 is the design space: it is meant to be explored, and each
video's choices are written down and approved before anything is built.

---

## 1. What is fixed before we start

| Given to us | We may not change it |
|---|---|
| The **script** | Not a word. A wrong fact goes back to the user as a list, with the NCERT line beside it. |
| The **HeyGen clip** (one continuous take preferred) | Not re-timed, not re-ordered, not cut for pace. His voice is the clock. |
| The **Notes answer** the video points to | The video and the Notes page must agree; a mismatch is reported, not papered over. |

Everything else is ours to design: what is behind him, where he stands,
whether he is on screen at all, every word and shape on screen, every sound.
**The job is to build a correct visual flow around a fixed voice.**

A fix to the voice after delivery is a re-shot sentence, spliced in with the
sentence-patch recipe, never a re-edit of the clip.

---

## 2. The guard rails (never vary)

Each one names what it prevents. They apply to every arts video, whatever it
looks like.

### Truth
1. **Veo draws manner, never fact.** A generated clip carries atmosphere and
   action: farming, a forge, a river, a court. Anything that is a count, a
   name, a date, a border, a number or a direction is drawn by us.
   *(Of fourteen graded science clips, seven failed, and every failure was a
   discrete quantity that was the answer.)*
2. **No text in a generated clip, and no proper name in a prompt.** Describe
   the place ("an ancient Indian capital"); typeset its name ourselves.
   *(Magadha V13 came back with "Rajagoriha" painted in the frame because the
   prompt named the city.)*
3. **A clip shows the sentence's CLAIM, not its setting.** Grain feeding rows
   of soldiers, not "a field". *(The classroom clip for "schools" was
   rejected.)*
4. **Maps come from data, never from Veo and never freehand.** Rivers, coasts
   and relief from a dataset through a real projection. *(The hand-drawn
   Magadha map was rejected; the d3 one was approved.)*
5. **Modern India's borders come from a dataset that matches the official
   Survey of India depiction.** Natural Earth's country borders do not; they
   are used for coastlines, rivers and relief only. Ancient-period maps show
   no modern borders at all.
6. **A real, identifiable modern person is never generated.** A named leader,
   judge or author appears as a licensed photograph or a typeset name plate.
   Ancient figures with no surviving likeness may be illustrated.
7. **Every video gets an accuracy brief** against NCERT before the storyboard:
   what the period, place and objects really looked like, and a list of the
   wrong pictures a generator is likely to draw (stone forts for 500 BCE,
   African elephants, modern caps).
8. **Screen text follows the voice.** Nothing appears on screen before he says
   it, and cards use his words.

### Flow
9. **Cuts sit in the gaps between his words**, measured from word timings.
   A transition finishes at the cut, so every sentence starts on its own scene.
10. **He moves or changes size only with a transition**, never mid-shot.
11. **A generated clip is never reversed and never slowed below 0.75×.** A
    scene longer than its clip gets a second clip, an extension, or our own
    drawn material.
12. **Something on screen changes at least every 4 seconds, and no background
    stays unchanged past 10.** A frozen screen is as dead as an empty one.
13. **His face is never covered.** Each scene's text zones are computed from
    where he stands in that scene.

### Craft
14. **One look per video.** Inside a single video: one palette, at most three
    font families, one banner family, one caption style, one transition
    family, one sound palette. The variety is BETWEEN videos, not inside one.
15. **Legible on a phone.** Body text at least 40 px and headings at least
    60 px on the 1080-wide frame; every string checked against its background.
16. **Captions say exactly what he said**, spelled correctly, digits as digits,
    timed word by word.

### Process
17. **Nothing is generated or rendered before the storyboard is approved**
    (section 4, step 5). Mock-ups and stills are allowed; Veo video and the
    full render are not.
18. **Process code lives once.** Ingest, transcription, timing, the builder,
    the compositor, the gates: one copy, never inside a video folder. Design
    code is different, see section 6.
19. **Every external asset is recorded with its licence**: photographs, fonts,
    datasets, sounds.
20. **A gate blocks; it does not warn.** And every finished video lands in
    `final/<QID>/` with a snapshot of the code that built it.
21. **One heavy job at a time on this machine.** Renders run with
    `ALLOW_LOW=1`, one video at a time.

---

## 3. The design space (meant to vary)

Every arts video chooses one option on each axis below, or invents a new one.
The choices are written into the storyboard as the video's **look card**.

| Axis | Explored so far | More to try |
|---|---|---|
| **Overall look** | Cinematic documentary (Magadha) | Comic illustration · carved stone relief · antique atlas · paper collage · newspaper front page · field notebook · blueprint · museum display · satellite/data |
| **Background source** | Veo scenes · parchment loop | Real photographs with slow camera moves · full-screen map · full-screen chart · our own drawn diagrams · solid colour with large type |
| **Presenter** | Centre large · bottom-left small · off-screen | Small circle in a corner · bottom-right · split screen (him below, picture above) · inside a frame or window · full-screen close-up for the hook |
| **When he is hidden** | Voice over the map | Voice over large word-by-word text · voice over a photo sequence · voice over a chart building |
| **Banners and labels** | Sign-boards with a swing | Wax seals · torn paper strips · chalk on slate · metal plaques · museum labels · newspaper headlines · sticky notes |
| **Fonts** | Poppins ExtraBold · Rozha One · Mukta ExtraBold | See the font shelf in section 7 |
| **Captions** | Bold pop, 2–3 words, bottom | Karaoke line · single huge word · typewriter · captions on a strip in the banner style · none during a title moment |
| **Transitions** | Dissolve | Wipe · push · circle open · page turn · ink spread · whip pan · match cut on shape |
| **Maps** | Relief, green "documentary" | Antique ink · satellite · choropleth by data · route drawn along a path · globe turning to India |
| **Counting and lists** | Numbered slots · pips · tiles | Timeline ribbon · ladder · wheel · stacking cards · checklist ticking |
| **Memory device** | One-word mnemonic · recap tiles | Chain of pictures · questions and answers · "fill the blank" pause |
| **Sound** | Tanpura bed, whoosh, thud, knock | Period instruments · paper and pen sounds · market or river ambience · a newsroom ticker |

### Where each subject naturally starts

A starting point, not a rule. The storyboard may go elsewhere and say why.

| Subject | The spine is usually… | Typical drawn material |
|---|---|---|
| **History** | the period itself: its places, objects and people | era maps, real photographs of inscriptions, coins and monuments, timelines |
| **Geography** | the land: maps, relief, the globe | data maps, process diagrams (monsoon, canal, soil), charts from census data |
| **Political Science** | events and institutions | timelines, structure diagrams, country maps, newspaper-style headlines, licensed photographs |
| **Economics** | quantities changing | bar and line charts that build, counters, flows of money or goods, tables |

### The spine

Each video names **one recurring visual thread** that holds it together: the
thing the viewer keeps returning to. Magadha's was the map and the four
sign-boards. A video about inscriptions might return to one stone. A video
without a spine is a slideshow of unrelated clips, whatever each clip looks
like.

### Uniqueness

There is no formula. Each video is designed fresh, the user is kept in the loop
through its storyboard, and we move video by video. After delivery the video's
look card is appended to `arts/LOOKS.md`, so the next storyboard can see what
has already been done and say how it differs.

---

## 4. The steps

One order. Step N does not start until step N−1 is green.

| # | Step | Gate | Tool today |
|---|---|---|---|
| 1 | **Ingest** the drop in `inbox/<QID>/`: clip, SRT, script, Notes answer | clip, audio and SRT agree within 1 s | `tools/ingest.py` |
| 2 | **Transcribe** to word timings | no hole over 1.5 s, no collapsed token over 1.3 s | `tools/word_timings.py` |
| 3 | **Captions**: the script's spelling on the measured clock | every boundary within 0.35 s of the spoken word, against a second transcription cut on real pauses (HeyGen's SRT has been 3.5 s out inside a part) | `tools/reel/words.mjs` (the clock) · `tools/reel/captions_line.mjs` (the layer) |
| 4 | **Read**: the accuracy brief, then every sentence broken into its claim and what could show it | brief written; every sentence has a claim | written by Claude |
| 5 | **STORYBOARD** (section 5) | **the user approves it**; the approval records a hash of exactly that board | new: `tools/reel/board` |
| 6 | **Build**, in parallel: Veo clips · maps, charts, diagrams · photographs · overlays · captions · sound | per item, below | see section 6 |
| 6a | Veo clips | Flow settings read back before the first submission; each clip graded (no text, right period, subject clear of him, shows the claim); three attempts, then the scene falls back to drawn material | `tools/reel/veo_batch.py` (first clip alone, then `--parallel 3`) |
| 6b | Maps, charts, diagrams | built from a recorded dataset; projection or scale stated; borders rule checked | `docs/history-poc/map-d3/` |
| 6c | Photographs | licence recorded; source resolution enough for the move | — |
| 7 | **Clip sheet**: one frame of every background, side by side | Claude grades every tile and regenerates failures; no second approval, the build carries on | contact sheet |
| 8 | **Spec**: scenes on measured word gaps, his placement per scene | scenes sum to the clip length; every cut in a gap; rule 12 holds | `scenes_part<N>.json` + `look.json` → `tools/reel/edit_from_scenes.py` |
| 9 | **Stills check**: a frame at every scene and every transition | every promised string is on screen; no face covered; legibility | contact sheet |
| 10 | **Render and composite**, with the sound mix | picture as long as the part (the file's own duration hides a short picture) | `tools/reel/run_part.sh` (detached): `layers.mjs` · `audio.py` · `build_part.py` |
| 11 | **Verify the delivered file** | audio and picture the same length; 30 fps; presenter where the spec says; loudness of his voice unchanged | `tools/output_gate.py`, taught the per-scene placements |
| 12 | **Deliver** to `final/<QID>/` with the code snapshot, and append the look card to `arts/LOOKS.md` | — | `tools/archive_code.py` |

**What runs at the same time.** Steps 2–4 start together the moment the drop
lands. After approval, everything in step 6 runs in parallel, with one agent
per independent piece: one for the Veo batch, one per map or chart, one for
the overlays, one for captions, one for sound.

**What a change costs after approval.** A scene's design changes: that scene
is re-approved, not the whole board. The look card changes: the whole board is
re-approved.

---

## 5. The storyboard: the one human gate

Nothing expensive happens before this is approved. **It is a rough sketch, not
a polished mock-up.** Its only job is to let the user see what this video is
going to be, and say yes or change it.

**It contains:**

1. **The direction, in a few sentences.** What this video feels like, what its
   spine is, and why that helps a student learn this answer.
2. **The look, in words and a few samples.** Colours, fonts, the banner and
   caption style, how scenes change, the sound.
3. **The scene list.** One row per scene:

   | Time | He says | The point to land | What is behind him | Where he is | On screen |
   |---|---|---|---|---|---|

   "What is behind him" says what each Veo clip is OF, or that the scene is a
   map, a chart, a photograph or text. "Where he is" covers every presenter
   choice: centre, corner, small circle, split screen, hidden.
4. **How it differs** from earlier videos.
5. **What is untested**, with the fallback if it does not work.

A sketch of a frame is welcome wherever words are not enough; none is required.

**The user answers one of three ways:** approve · approve with changes to
named scenes · change the direction. Approval is the only stop. After it, all
Veo clips are generated, checked and redone where needed, and the complete
video is built without a second approval.

---

## 6. Where things live

```
inbox/<QID>/                 the drop: clip, SRT, script, Notes answer
work/<slug>/
    inputs.json              from ingest
    brief.md                 the accuracy brief
    board/                   the storyboard: board.md, look.json, style frames, sheet.png
    scenes.json              the spec: every scene, on the measured clock
    assets/                  veo clips, photos, map data, drawn SVGs, with a sources.json of licences
    design/                  THIS video's drawing code: components and styles
    out/                     everything generated
tools/reel/                  the process, one copy (to be promoted from docs/history-poc/)
    build                    background track, presenter placement, composite, join
    overlay harness          transparent layers from a page with render(t)
    captions · audio · maps · charts · presenter modes
    components/              drawing pieces that have earned a second use
    styles/                  banner families, caption styles, looks
arts/LOOKS.md                every delivered video's look card
```

**Process code never, design code yes.** The science rule is "the video folder
holds no code". Arts cannot keep it as written, because a unique look means
unique drawing code. So the line is drawn here:

- `work/<slug>/design/` may hold code that **draws**: a banner style, a
  component, a chart, a map style.
- It may not hold code that **builds**: no ffmpeg, no timing, no transcription,
  no gate. The tools refuse a video folder that carries any.
- A component used well in one video is promoted to `tools/reel/components/`
  when a second video wants it. Nothing is copied from an old video folder.

**Getting there.** The working code is the Magadha proof of concept in
`docs/history-poc/` (snapshot in `final/HISTORY-MAGADHA-POC/code/`). **It is
kept as the reference and is not tidied now** (user, 2026-10-07): a new video
takes from it whatever it needs. Promoting it into `tools/reel/` is a later
job. Three things are owed when that happens: scenes read from
`scenes.json` rather than written into a script, the d3 library bundled
instead of loaded from the internet, and the gates in steps 8, 9 and 11.

---

## 7. The toolbox

**The rule for anything new.** A library or source is usable only if it:

1. runs in headless Chromium **offline**, from a bundled copy;
2. can be driven by an **absolute time**, so frame 137 is the same on every
   render (a timeline we can seek, not one that just plays);
3. has a licence that allows this use, recorded when it is added;
4. passes a **5-second test clip** on this machine before a storyboard
   depends on it.

"Proven" below means a delivered video used it. "Candidate" means it looks
right and has not passed that test here yet.

### Drawing and motion

| Tool | Good for | Status |
|---|---|---|
| **d3-geo** | Maps on any projection; camera moves across a map | Proven (Magadha) |
| **d3-shape, d3-scale** | Bar, line, area and pie charts that build over time | Candidate |
| **d3-hierarchy** | Trees and structures: how a government or an administration is organised | Candidate |
| **d3-sankey** | Flows: where a budget goes, what a region trades | Candidate |
| **flubber** | One shape morphing into another: a border changing between two years | Candidate |
| **topojson-client** | Smaller map files; shared borders drawn once | Candidate |
| **turf.js** | Geographic sums: a point moving along a river, distances, buffers | Candidate |
| **rough.js** | A hand-drawn, sketched look for shapes, charts and maps | Candidate |
| **GSAP** (seekable timelines) | Complex choreographed motion; text split into letters and words | Candidate |
| **lottie-web** | Playing ready-made vector animations frame by frame | Candidate |
| **three.js** | A globe turning to India; terrain in 3D | Candidate, heavy: test memory first |
| **KaTeX** | Formulas (economics) | Proven (science track) |
| **SVG and CSS filters** | Paper grain, ink bleed, glow, rough edges | Proven (map glow, sign-boards) |
| **ffmpeg transitions** | Dozens of wipes, pushes and reveals between scenes | Proven for dissolve; others candidate |
| **ffmpeg colour** | One grade over every clip so mixed sources match | Candidate |

### Data and pictures

| Source | Good for | Status |
|---|---|---|
| **Natural Earth** | Coastlines, rivers, lakes, shaded relief | Proven (Magadha) |
| **Official-boundary India dataset** | Modern India, states, districts | Needed before the first geography video; source to be chosen and checked |
| **Census and government open data** | Population, crops, irrigation, energy | Candidate; each figure quoted with its year |
| **Wikimedia Commons** | Real photographs of inscriptions, coins, monuments, manuscripts, old maps | Candidate; licence checked per image |
| **Flow stills** | A single generated frame for a style frame or a scene's first frame | Candidate |
| **Flow video (Veo)** | The scenes themselves | Proven (15 clips, 2 redone) |

### Type: the font shelf (all free, Devanagari)

Used: Poppins · Rozha One · Mukta · Khand.
On the shelf: Baloo 2 · Hind · Yatra One · Tiro Devanagari Hindi · Noto Serif
Devanagari · Anek Devanagari · Kalam (handwriting) · Modak · Teko · Rajdhani ·
Martel · Eczar · Laila · Palanquin Dark · Amita · Gotu.
Every new font is set in this video's real words first: conjuncts such as
क्ष, त्र, द्ध and श्र are where a font fails.

### Sound

Proven: effects and a bed synthesised in code (`audio/build_audio.py`), mixed
under an untouched voice. Candidate: licensed recordings where synthesis
sounds false (an elephant, a crowd, a period instrument).

---

## 8. What Magadha taught us

| What happened | The rule it became |
|---|---|
| The city's name in a prompt was painted into the clip, misspelled | Rule 2 |
| Two kings came back with the same face | One subject per clip; ask for visible differences |
| The hand-drawn map was rejected, the data map approved | Rule 4 |
| The key turned a black shirt navy on a real green cloth | Calibrate the key and the spill removal per clip |
| Captions sat where the platform draws its own text | Caption position is shown on the storyboard, on a phone-shaped frame |
| An overlay word pulsed and swallowed its space | The stills check samples mid-animation, not only at rest |
| The proof of concept's overlays were written as code per part | Scenes are data; only drawing code is per video (section 6) |

---

## 9. What a video costs (from Magadha, 1:42)

| Piece | Time |
|---|---|
| Transcription, key calibration | about 3 min |
| 15 Veo clips, one at a time | about 25 min, plus 2 redone |
| Map animation, 10 s | 1.5 min per render |
| Overlay and caption layers | about 8 min |
| Composite and join | about 10 min |
| Storyboard, review and fixes | the real time, and the point of this page |

---

### What the second production video cost (POL-C3-LA-02, three parts, 6:33)

Measured on 2026-10-08, after the changes below. Per part unless it says otherwise.

| Piece | Time | Was (GEO-C2-LA-01) |
|---|---|---|
| Ingest, word timings, key, for all three parts | about 6 min, **before approval**, while the board is written | about 10 min, after approval |
| Drawn layers (under, mask, overlay) | 20–50 s | 7–9 min |
| Captions layer | about 30 s | 15 min the first time, 2 min after |
| Sound mix | about 10 s | 4–18 min |
| 10 Veo clips | about 3 min per wave of three | 18 clips, one at a time, 13 wasted |
| Background track | 15–25 s | 2–11 min |
| Composite | 4–8 min | 5–10 min |
| One part, end to end, once its pieces exist | **about 8 min** | — |

**What made the difference, in the order it mattered:**

1. **One kit, three parts.** `work/<slug>/design/kit.mjs` is written once (the
   look, the components, the spine); each part is a short file of scenes on it.
   GEO wrote three overlay files and three HUD files, one agent each.
2. **Design code quotes his words, never seconds.** `clock.at('संवैधानिक राजतंत्र')`
   asks the word clock and throws if he does not say it. A retimed cut costs
   nothing, and no scene spec has to be typed.
3. **Layers hold only the frames that change** (`tools/reel/layers.mjs`), drawn by
   several pages at once. A layer file must keep ONE pixel format: an opaque
   frame is RGB, a frame with a hole RGBA, and a mix makes ffmpeg rebuild its
   graph at every change (4 GB in half a minute, killed by macOS).
4. **Sound cues come from the drawing code** (`--cues`), not from a hand-written
   cue list; the engine fits each one under the voice.
5. **Pre-approval work is done before approval**: steps 1–3, the key, the
   question card and the Veo prompts all exist when the user says yes.
6. **No heavy centrepiece.** The spine is SVG; the globe cost 25 + 58 min.
7. **One detached command per part** (`run_part.sh`), with gates that stop it.

**What still loses time, and is not a tool problem:** a closed lid stops
everything and kills the agents (14 h lost overnight); Flow's bridge extension
can go silent until it is reloaded by hand (15 h, the same night); and Flow's
grid no longer shows a finished clip until the page is reloaded.

## 10. Decisions

**Settled with the user, 2026-10-07:**

1. **The storyboard is a rough sketch** showing what each Veo clip is of,
   where the presenter is, and what is on screen. It is the one approval.
2. **No second approval.** Once every clip is generated and has passed
   Claude's own checks, the complete video is built.
3. **No uniqueness formula.** Open creatively, user in the loop, video by video.
4. **The Magadha code is not tidied now.** It stays in `docs/history-poc/` as
   the reference every new video may borrow from; tidying comes later. The
   next video is geography.
5. **Drawing code may live in a video's own folder**; building code may not
   (section 6).

**Taken as the default unless the user objects:**

6. **Captions sit at the bottom of the frame** by default; another position is
   fine when the storyboard shows it.
7. **A wrong fact in a fixed script is reported and the video waits**, rather
   than being built as written.
