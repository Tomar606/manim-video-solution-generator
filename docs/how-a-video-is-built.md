# How one of these videos is built — and why the captions stay in sync

Written after building the शुष्क सेल, संक्षारण and विटामिन videos. It covers the
whole pipeline in order, then the part that actually causes trouble: keeping
captions and animation locked to the presenter's recorded voice.

If you are here because **captions drift — sometimes late, sometimes early** —
skip to [Why captions drift](#why-captions-drift). That symptom has four
distinct causes and they need different fixes.

---

## The one rule everything else follows

> **The presenter's audio is fixed. Everything else conforms to it.**

The recording already exists. It cannot be stretched, nudged or re-cut to suit a
caption. So nothing downstream is allowed to *decide* a time — every time is
**measured from the audio itself**, once, and then reused by every later stage.

The moment anything estimates a time — a caption placed by reading the script, a
segment given a round 6.0 seconds, an animation timed by eye in an editor — the
video and the voice start telling different stories, and no amount of nudging
later fixes it, because the error is not constant.

---

## The pipeline, in order

### 1. Word-level timings — the clock everything derives from

```bash
.venv-tools/bin/python tools/transcribe.py inbox/CHE-C10-LA-02/part1.mp4 \
    projects/che-c10-la-02/words_part1.json
```

Whisper `medium`, `word_timestamps=True`. The output is every word with a start
and end in seconds, against the **original, untrimmed clip**.

**Check it before going on.** Two Whisper failures both hit us, and neither
raises an error:

| failure | what it looks like | how to spot it |
|---|---|---|
| **dropped stretch** | 15 s of speech with no words at all | a gap between one word's `e` and the next word's `s` |
| **repetition loop** | the same 2–3 words repeated 20× with zero duration | many words where `e - s == 0` |

On विटामिन part 1 the words jumped **71.61 → 86.76** — fifteen seconds of real
speech, silently missing — and at ~101 s Whisper looped on *"पूर्वाज करने पर"*
until the caption builder gave up and wrote `[अस्पष्ट ऑडियो]` on screen.

```python
# both checks, on the words file
w = json.load(open("projects/<slug>/words_part1.json"))
holes = [(a["e"], b["s"]) for a, b in zip(w, w[1:]) if b["s"] - a["e"] > 1.0]
loops = [x for x in w if x["e"] - x["s"] == 0]
```

Confirm a hole is real speech before re-running — `silencedetect` will tell you
whether he was simply not talking:

```bash
ffmpeg -v error -ss 70 -t 36 -i clip.mp4 \
  -af "silencedetect=noise=-35dB:d=0.8,ametadata=print:file=-" -f null - 2>&1 \
  | grep silence
```

Re-transcribe **just that window** with the loop guards on, and splice the result
back in:

```python
m.transcribe(window_wav, language="hi", word_timestamps=True,
             condition_on_previous_text=False,   # stops the loop
             no_speech_threshold=0.9, logprob_threshold=-2.0,
             temperature=(0.0, 0.2, 0.4))
```

### 2. Captions — timing from the transcript, words from the script

```bash
PYTHONPATH=. .venv-tools/bin/python tools/captions_from_audio.py \
    projects/<slug>/words_part1.json \
    projects/<slug>/script_master.md \
    projects/<slug>/lines_part1.json
```

The transcript gives **when**, the recorded script gives **what**. Whisper's
Hindi spelling is unreliable (`वितामिन`, `देफिनिशन`) and it is not what should
appear on screen; the script's wording is. Alignment maps script words onto
transcript timings.

`script_master.md` must be **the draft that was actually recorded**. An earlier
draft looks close enough to pass a read-through and puts wrong wording on screen.
Coverage below ~0.80 in the tool's output means the two disagree — check by hand.

Then assert the caption track is monotonic. On विटामिन part 1, line 39 ended at
101.82 while line 40 began at 101.59 — a **backwards** caption, which renders as
a flicker:

```python
for a, b in zip(lines, lines[1:]):
    assert a["end"] <= b["start"], (a, b)
```

### 3. The scene spec — segment boundaries land on caption boundaries

A segment is a group of caption lines. The rule that matters:

> **A segment may only start where a caption starts.**

Segment lengths come from the caption track, never from a clock:

```python
t0   = lines[i0]["start"]                       # a real caption boundary
t1   = lines[i1]["start"]                       # the next one
dur  = round(t1 - t0, 2)
# phrase times are RELATIVE to the segment, derived from the same lines
t_in  = round(lines[i]["start"] - t0, 2)
t_out = round(min(next_line_start, t1) - t0, 2)
```

Put a boundary mid-line and that caption is clipped at the segment end and never
re-shown in the next one. That is what left seven captions in an earlier dry-cell
build flashing for two frames with the band blank for seconds afterwards.

Check the plan before rendering anything:

```bash
python3 validate.py     # gaps, unknown SVG ids, golden word not in its phrase
node qa.mjs             # steps a real browser frame by frame: overlaps, out-of-band
```

### 4. Rendering — frame-exact, never wall-clock

`full.mjs` does not play anything. For each segment it renders exactly
`round(duration × 30)` frames and asks the page for the state at `f / 30`:

```js
const n = Math.round(seg.duration * FPS);
for (let f = 0; f < n; f++) await page.evaluate(t => window.RENDER.setTime(t), f / FPS);
```

Because time is *computed per frame* rather than advanced by a timer, a slow
frame cannot push everything after it later. A caption with `t_in = 2.34`
appears on frame 71 of that segment, always, on any machine.

### 5. The overlay fades in — so it must start BEFORE the words

`burn_chips.py` fades each overlay in over `FADE = 0.35 s`. Start a chip at the
same second as the caption it belongs to and it is only half-visible when the
words land; the *previous* chip is still fading out on top of it. On a
rapid-fire list this reads as the wrong thing on screen.

Measured on the vitamins video before the fix: he says **"और B फोर यानी
निकोटिनिक अम्ल"** at 52.71 s, the chip was set to 53.00 s, and at 52.90 s the
band was **blank** — the previous vitamin gone, the next one not yet arrived.

**Rule:** a chip starts `LEAD = 0.40 s` before its caption line, so the fade
completes as the phrase is spoken.

```python
LEAD = 0.40          # slightly more than burn_chips.FADE
start = round(lines[i]["start"] - LEAD, 2)
```

Let consecutive chips overlap rather than leaving a gap between them — the later
one is drawn on top, so an overlap is a clean hand-off and a gap is a flash of
empty band.

### 6. Where the narration is wrong, the screen must not argue with it

The vitamins narration calls nicotinic acid *"B फोर"* (it is B₃) and folic acid
*"B टेन"* (it is B₉). Neither number can go on screen:

- showing **B4** teaches an error the student writes in the exam
- showing **B3** contradicts what they are hearing at that exact second

So those two tiles carry the **chemical name only** — निकोटिनिक अम्ल, फोलिक अम्ल
— which is unambiguous and is what he says in the same breath. The end-of-video
summary table, which is the written answer, uses the correct B₃ and B₉.

### 7. Compositing the presenter — where frame rate bites

The HeyGen clips are **25 fps**. The stage is **30 fps**. Combine them without
forcing constant frame rate and the picture slides against the audio, slowly and
increasingly.

```bash
FFMPEG_THREADS=2 PYTHONPATH=. .venv-tools/bin/python tools/composite.py \
    background.mp4 inbox/<clip>.mp4 projects/<slug>/keys/part1.json \
    out.mp4 - - - - crop_part1.json card_part1.json
```

The flags that matter, all inside `composite.py`:

| flag | why |
|---|---|
| `[1:v]fps=30` | resample the 25 fps presenter **before** any other filter |
| `-fps_mode cfr -r 30` | constant frame rate out; without it ffmpeg keeps source timestamps and the mux drifts |
| `-map 1:a` | **audio comes from the presenter clip, never re-encoded from anywhere else** |
| `-af aresample=async=1:first_pts=0` | pins audio to start at 0 and resamples rather than dropping samples |
| `-max_muxing_queue_size 512` | stops ffmpeg dropping video packets when the queue fills on a long filter chain |

The background must also be **at least as long as the audio**, then cut to
length. A background that ends early makes the last section slide:

```bash
ffmpeg ... -vf "tpad=stop_mode=clone:stop_duration=0.5,fps=30" -t 115.98 ...
```

> `tpad` after `minterpolate` needs an explicit `fps` between them — minterpolate
> emits timestamps off the 1/30 grid, so the padded frames land past where `-t`
> cuts, get generated, and are immediately discarded. That cost an hour once and
> produced a clip 7.87 s long where 8.00 s was asked for.

### 8. Additions on a finished video

Anything that goes into empty screen space *after* the video is approved is laid
on top — never re-rendered:

```bash
.venv-tools/bin/python tools/burn_chips.py in.mp4 out.mp4 plan.json
```

One ffmpeg pass, `-c:a copy` so the audio is bit-identical, so **an addition
cannot introduce drift**. Each overlay is padded at the front with transparent
frames (`tpad=start_duration=…:color=black@0`) followed by `fps=30`, so it lands
on its window rather than at the start of the video.

### 9. The gate

```bash
PYTHONPATH=. .venv-tools/bin/python tools/output_gate.py <file>.mp4
```

It refuses the file if audio and video durations differ by more than **0.30 s**,
if the effective frame rate is not 30, or if the presenter is floating,
off-centre or clipped. It reads placement from the `<file>.mp4.geom.json`
sidecar written at composite time — which `burn_chips.py` now carries forward, so
a patched file is still checkable.

---

## Why captions drift

"Sometimes late, sometimes early" is the signature of an error that **grows and
then resets**, rather than a constant offset. Here are the four causes, in the
order they are worth checking.

### 1. The times were estimated, not measured  ← most likely

Placing captions by reading the script, or by dragging them in an editor, means
every caption inherits the error of the ones before it. At a pause the presenter
catches up and the error resets — which is exactly why it looks like lagging
*and* running ahead in the same video.

**Test:** take three captions — one near the start, one in the middle, one near
the end — and check each against the waveform. If the error at 0:20 is small, at
1:00 is large, and at 1:10 is small again, it is this.

**Fix:** stop placing times by hand. Derive every one from `words_*.json`.

### 2. Transcribed one file, delivered another

If the clip was trimmed, re-encoded, or had a slate removed **after**
transcription, every caption is off by the trim — constantly, not progressively.

**Test:** compare durations.

```bash
ffprobe -v error -show_entries format=duration -of csv=p=0 clip.mp4
python3 -c "import json;w=json.load(open('words_part1.json'));print(w[-1]['e'])"
```

Those two should agree to within a few hundredths. Ours: clip 143.56 s, last word
143.32 s.

**Fix:** transcribe the exact file you will mux, and never re-cut afterwards.

### 3. Frame-rate conversion  ← the one specific to these clips

25 fps source into a 30 fps timeline. Without `-fps_mode cfr` ffmpeg preserves
the source timestamps and the video slowly separates from the audio. This is
*progressive* — imperceptible at 0:10, obvious by 2:00.

**Test:**

```bash
ffprobe -v error -select_streams v -count_frames \
        -show_entries stream=nb_read_frames,r_frame_rate,avg_frame_rate \
        -of csv=p=0 out.mp4
```

`nb_read_frames / duration` must equal 30.00. If `r_frame_rate` and
`avg_frame_rate` disagree, the file is variable frame rate and will drift in any
player that trusts timestamps.

**Fix:** `fps=30` on the presenter input, `-fps_mode cfr -r 30` on the output.

### 4. Per-segment frame rounding

Rendering segments separately and concatenating rounds each length to a whole
frame, and those roundings add up. Measured on our own specs:

| video | segments | worst mid-video drift | final |
|---|---|---|---|
| विटामिन LA-01 | 16 | 0.040 s (1.2 frames) | −0.027 s |
| विटामिन LA-02 p1 | 12 | 0.023 s (0.7 frames) | +0.023 s |
| विटामिन LA-02 p2 | 11 | 0.020 s (0.6 frames) | −0.007 s |
| शुष्क सेल p2 | 17 | 0.000 s | 0.000 s |

Under two frames, so inaudible here — but it is real, it scales with segment
count, and it is worth removing when a video needs many short segments:

```js
// instead of  n = Math.round(seg.duration * FPS)  per segment,
// take boundaries from cumulative time so roundings cannot accumulate
const startF = Math.round(cumulativeSeconds * FPS);
const endF   = Math.round((cumulativeSeconds + seg.duration) * FPS);
const n      = endF - startF;
```

### Not drift, but looks like it

A caption sitting on screen while he says something else is usually a **Whisper
hole** (step 1), not a sync problem. Check `words_*.json` for gaps before
touching any timing.

---

## The checklist

Before rendering:

- [ ] `words_*.json` has no gap > 1 s and no zero-duration words
- [ ] last word's end ≈ clip duration
- [ ] caption times are monotonic — no `end > next start`
- [ ] every segment starts on a caption boundary
- [ ] segment durations sum to the section length
- [ ] `validate.py` and `qa.mjs` both clean

After compositing:

- [ ] `nb_read_frames / duration` = 30.00
- [ ] audio and video durations within 0.30 s
- [ ] audio stream came from the presenter clip, not re-encoded from elsewhere
- [ ] `output_gate.py` passes
- [ ] every overlay is UP before the words it belongs to — check the frame 0.2 s after each cue, not the middle of the window
- [ ] watch 0:10, mid-point and the last 10 s — drift shows at the ends first

---

## Where things live

| | |
|---|---|
| `tools/transcribe.py` | word-level timings |
| `tools/captions_from_audio.py` | transcript for the clock, script for the words |
| `tools/edu/renderer/full.mjs` | frame-exact rendering |
| `tools/composite.py` | chroma key, presenter geometry, frame-rate conformance |
| `tools/burn_chips.py` | additions onto a finished file, audio copied |
| `tools/output_gate.py` | the last check before anything is delivered |
