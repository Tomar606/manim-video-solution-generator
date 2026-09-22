# Sound effects, cues, transitions and the character gate: how to use them

This covers the sound and transition layer of the recent chemistry videos
(CHE-C2-SA-01 to 04, CHE-C3-SA-10), and the two gates that check a finished
video:

- **the character gate**: is the presenter really him?
- **the cue gate**: does every sound land on something happening?

**Written for someone, or their Claude, building a video with these for the
first time.** Commands run from the repo root. `.venv-tools` is the Python
environment from `veo_kit/SETUP.md`, Step 2.

Two ideas hold it together:

- **A sound marks an event on screen.** It never marks a caption, and its
  loudest point lands on the frame where the picture changes. That frame is
  measured, not assumed.
- **A transition is grammar, not decoration.** The same kind of cut always gets
  the same effect, and a cut that is not a change of world gets nothing.

---

## 1. The effects

Sounds are filed by the **moment they mark**, not by what they sound like. The
folder name is the decision. `README.md` in this folder is the full ingest
contract.

| cue name | folder (moment) | fires when | file |
|---|---|---|---|
| `pop` | `label-lands/` | a diagram label, list card or chip arrives; most beat turnovers | `pop.wav`, 0.17 s |
| `click` | `list-item/` | one item of a counted list fills in (1, 2, 3, 4) | `click.wav`, 0.05 s |
| `reveal` | `card-appears/` | the question card; formula and table beats | `reveal.wav`, 0.75 s |
| `write` | `handwriting/` | a graph or figure being drawn; texture under the answer page | `write.wav`, 0.70 s |
| `page_swoosh` | `panel-arrives/` | an animation panel tears in or out | `page_swoosh.wav`, 1.08 s |
| `page_swoosh` | `page-arrives/` | the handwritten answer page at the end | `page_swoosh.wav`, 1.08 s |
| `shutter` | root | the light bloom out of the question card; a glow landing | `shutter.wav` (a supplied camera shutter) |
| `whoosh`, `impact` | root | the cut vocabulary in section 4 | `whoosh.wav`, `impact.wav` |

You can use either name. A cue called by its moment (`label-lands`) or by its
alias (`pop`) goes to the same file. `registry.json` holds the mapping, with
each file's measured length and **`peak_offset`**: how far into the file its
loudest point sits (0.419 s into the page swoosh, for example). `src/sfx.py`
looks every cue up there first.

**To swap or add a sound:** drop the file in the moment's folder and run:

```bash
.venv-tools/bin/python tools/sfx_registry.py
```

It measures the file and refuses anything:

- tonal (a pitch reads as a ringtone),
- with a rising sweep (the "whistle" family),
- too long for its moment,
- with several bursts where one event is expected.

The newest file that passes wins. To retire one, move it to `_rejected/` and
write why in `_rejected/REASONS.md`, so it is not re-added in six months.

**Never:**

- a sound on a caption or subtitle change;
- a sound on the focus boxes around equations;
- a riser or whistle;
- a "ding";
- two effects within a third of a second (that is one effect played twice).

---

## 2. The cues: from scene to finished audio

Manim renders **silently**. A scene does not play sound; it **reports when
sound should happen**, and the build mixes it in afterwards.

### 2a. The scene reports cues

Every scene built on `src/manim_helpers.py` has `self.cue()`. Call it
immediately before the animation it belongs to:

```python
self.cue("pop"); self.play(FadeIn(label))
self.cue("reveal", gain=-3); self.play(Write(eq))
self.cue("write", at=t)            # explicit time, in seconds from scene start
```

When the scene ends, the cues are written to `projects/<slug>/cues_part<N>.json`:

```json
{"cues": [{"time": 12.43, "name": "pop"}, {"time": 18.9, "name": "reveal", "gain": -3.0}]}
```

The chemistry scene cues **every stage turnover** automatically, by the type
of the beat arriving:

```python
TURNOVER_PEAK = 0.23   # clear_stage fades over 0.30 s; the visible change peaks 0.23 s in
if i in beats and beats[i].get("type") != "clear":
    self.cue({"graph": "write", "figure": "write", "scan_figure": "write",
              "formula": "reveal", "table": "reveal"}.get(beats[i].get("type"), "pop"),
             at=float(self.renderer.time) + TURNOVER_PEAK)
self.clear_stage()
```

- A **clear** gets no sound, because nothing arrives.
- The cue sits at the **middle of the fade**, which is where the picture
  actually changes, not at its start.
- Cues closer together than 0.35 s are merged into one.

### 2b. Snap each cue onto the real change

```bash
.venv-manim/bin/python tools/snap_cues.py <background.mp4> projects/<slug>/cues_part1.json
```

`snap_cues` finds the frame-difference peak nearest each cue in the rendered
background (within `--window 0.8` s). It moves the cue there, then pulls it
**earlier by that sound's `peak_offset`**, so the sound's loudest point lands
on the change. It rewrites the cues file in place.

Always snap. The alternative, a constant offset tuned by ear, took four
rebuilds and still never fitted every beat type.

### 2c. Mix them under the narration

```bash
.venv-tools/bin/python tools/mix_cues.py <heygen_full.mp4> projects/<slug>/cues_part1.json <narration.wav>
```

This lays each effect under the HeyGen voice at the cue's own `gain`. A cue
without one sits **12 dB under the narration** (`DEFAULT_GAIN` in
`src/sfx.py`). The registry's `default_gain_db` is written at ingest, but the
mixer does not read it yet. Then mux `narration.wav` onto the composited
picture. With no
cues the narration passes through untouched, so the step is always safe to
run.

`tools/build_che_c3_sa_10.sh` is the complete reference recipe, in this order:
render, composite, snap, mix, mux, gates.

---

## 3. The two gates: run them on every finished video

### 3a. Character gate: is the presenter really him?

```bash
.venv-tools/bin/python veo_kit/face_gate.py projects/<slug>/final/<video>.mp4 --spread 7
```

How it works:

- It samples 7 frames evenly between 12% and 88% of the video.
- In each frame it finds the face (MTCNN) and embeds it (InceptionResnetV1,
  VGGFace2).
- It scores the embedding by cosine similarity against his reference photo,
  `assets/character/ritesh_reference.jpeg`.
- The video **passes when the median is 0.90 or more**.

It measures rather than judges, because the look-alikes all fit a written
description ("a bearded Indian man in a black polo"). Calibration:

- his real frames score about **0.94**;
- the generated strangers that shipped in HIS-C2-SA-06 scored about **0.86**;
- one of those strangers' frames reached 0.901, which is why the decision is
  the median, not any single frame.

Frames with no confident face (under 120 px, or detection confidence below
0.95) are skipped, and at least 3 usable frames are needed. On CHE-C3-SA-10 it
reads `median 0.945 over 6 frame(s)`: pass.

It matters most for **Veo clips**, where the generator can drift to a
different man. For a single clip, pass explicit times:

```bash
.venv-tools/bin/python veo_kit/face_gate.py clip.mp4 --at 1 2.5 4 5.5 7 8.5 9.5
```

A new presenter needs their own reference and threshold: see "Adding another
presenter" in `veo_kit/SETUP.md`.

### 3b. Cue gate: does every sound mark something?

```bash
.venv-tools/bin/python tools/sfx_gate.py projects/<slug>/final/<video>.mp4 projects/<slug>/cues_part1.json
```

It measures frame-to-frame change inside a **stage band**, which excludes the
subtitle strip and the presenter, and checks:

1. every cue has a real visual change within **0.20 s** of its peak (FAIL if
   not);
2. no two cues sit within 0.12 s of each other, unless the second is marked
   `"layer": true`;
3. visual changes with no sound are listed as a **note**, never a failure.
   Silence is a choice.

On CHE-C3-SA-10 it reads `9 cue(s) all land on a real change`.

**Before believing a FAIL, check the two things it cannot see.** A label
fading in over a moving background, or the arrival at the end of a fade, can
be correct and still read as "no change". Measure that specific moment before
moving the cue.

`tools/gates.py` runs both of these, plus the layout and font gates, as the
last line of every build. Its other gates are not all in git yet. Where it is
missing, run the two commands above by hand.

---

## 4. Transitions

### 4a. Between shots: `src/transitions.py`

The effect is chosen by **what the cut means**, never by taste:

| cut | effect (ffmpeg `xfade`) | sound |
|---|---|---|
| `scene_change` | `fade`, 0.50 s (cross dissolve) | whoosh |
| `to_card` | `fadeblack`, 0.40 s (dip to dark), loud | whoosh + impact |
| `from_card` | `fadewhite`, 0.30 s (light bloom), loud | shutter |
| `to_map_first` | `coverup`, 0.40 s | whoosh + reveal |
| `to_map` | `smoothright`, 0.45 s (soft wipe) | whoosh + reveal |
| `from_data` | `hblur`, 0.50 s (rack-focus dissolve) | whoosh + impact |
| `continuous` | **nothing**: the voice carries straight on | — |

```python
from src.transitions import plan_transitions, audit
plan = plan_transitions(["to_card", "from_card", "scene_change", "continuous", "to_map"])
print(audit(plan))    # warns if it is getting busy
```

- At most **2 loud** transitions per video.
- If more than 85% of cuts carry an effect, `audit()` warns.
- Each effect carries `peak_at`, its measured visual peak, so its sound can be
  placed there.

**Banned**, with the reason (`BANNED` in the module):

- `zoomin`: it magnifies to a flat patch;
- `pixelize` and `dissolve`: they look like encode failures;
- `radial`: dated;
- the wind family: glitch effects.

**Ghosting.** The presenter is centre frame on both sides of most cuts, so a
plain dissolve shows him over himself. Use `hblur`.

`tools/his_polish.py` is the worked example: the HIS-C2-SA-06 polish pass.
Its segment list is specific to that video.

### 4b. The panel tear (chemistry panels)

A Veo clip or figure panel comes in over the plate behind a **torn-paper
edge** that travels across, with `page_swoosh` on it. The settings live in
`src/panel_layout.py`:

| setting | what it does |
|---|---|
| `WIPE = 0.55` | seconds the tear takes to cross |
| `LEAD = 95` | px the tear runs ahead of what it reveals |
| `SOFT = 26` | px of softness on the travelling edge |
| `OVER = 40` | px the wipe reaches past the frame edge |
| `TOP_FADE = 150` | rows over which the panel's top dissolves into the plate |
| `SIDE_FADE = 80` | px of fade at each side of a narrow panel |

The tear image is built from `assets/transitions/divider/paper_tear_texture.jpg`:

```bash
.venv-tools/bin/python tools/make_tear.py --seam <y>
```

`tools/composite.py` places the panel and runs the wipe. Size the panel to the
clip's own aspect, and use landscape Veo clips: a portrait clip in a
full-width panel loses its background. `assets/transitions/README.md` explains
how to add more divider, overlay or matte shapes. Anything that writes text,
or decorates without teaching, is refused.

### 4c. Inside a Manim beat

- **Stage turnover:** `clear_stage()` fades the old beat out over 0.30 s, and
  the next beat builds in. The turnover cue sits at 0.23 s (section 2a).
- **Graphs are drawn**, not shown. The axes fade in, then the data traces on:

  ```python
  self.play(Create(data, lag_ratio=0.12), run_time=1.15)
  ```

  Figures are drawn on the same way, in the order a teacher would draw them.
- **Important data glows.** Use it on what the narration is pointing at, never
  on everything. Manim has no glow, so the helper stacks faint, fat-stroked
  copies **behind** the crisp original:

  ```python
  def glow(mob, colour=None, layers=4, spread=9.0, peak=0.16):
      g = VGroup(); g._is_glow = True
      for i in range(layers, 0, -1):
          c = mob.copy()
          for sub in c.get_family():
              sub._is_glow = True          # the layout audit skips decoration
          c.set_fill(opacity=0)
          c.set_stroke(colour or c.get_stroke_color(),
                       width=(c.get_stroke_width() or 4) + spread * i / layers,
                       opacity=peak * (1.0 - (i - 1) / layers))
          g.add(c)
      return g
  ```

  Mark glow copies `_is_glow`. Otherwise the overlap audit counts a word and
  its own halo as two overlapping labels.

---

## 5. Checklist for a new video

1. The scene cues its moments (`self.cue`), and nothing cues a caption.
2. Render, then run `snap_cues`, then `mix_cues`, then mux.
3. `sfx_gate`: every cue lands on a change.
4. `face_gate --spread 7`: median 0.90 or more.
5. Watch it once with sound. The gates catch misplacement; only a person
   catches "too much".
