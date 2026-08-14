# tools/ — the avatar-synced video pipeline

These build a **Manim video timed against a real HeyGen clip**, as opposed to
`video.py`, which builds a video whose clock comes from synthesized narration.
The difference matters: here the audio already exists and cannot be changed, so
everything conforms to it.

Everything in here was previously ad-hoc scratchpad code. It lived in
`/private/tmp`, which is wiped between sessions, and it was lost once — along
with the transcripts and the key calibration. Keep new pipeline code here.

## Order of operations

```bash
# 0. one env with manim, and one with whisper/numpy/pillow (manim pins numpy)
python3.11 -m venv .venv-manim && .venv-manim/bin/pip install manim
python3.11 -m venv .venv-tools && .venv-tools/bin/pip install openai-whisper numpy pillow python-docx

# 1. word-level timings for the clip — everything downstream derives from this
.venv-tools/bin/python tools/transcribe.py inbox/clip_part1.mp4 \
    projects/<slug>/words_part1.json

# 2. captions, from the AUDIO (never from the script — see below)
PYTHONPATH=. .venv-tools/bin/python tools/captions_from_audio.py \
    projects/<slug>/words_part1.json projects/<slug>/script_master.md \
    projects/<slug>/lines_part1.json

# 3. chroma parameters for THIS clip (not portable between shoots)
.venv-tools/bin/python tools/calibrate_key.py inbox/clip_part1.mp4 \
    projects/<slug>/key_part1.json

# 4. render
PYTHONPATH=. .venv-tools/bin/python tools/recompose.py
FARADAY_PART=1 .venv-manim/bin/python -m manim render --disable_caching \
    -r 1080,1920 --fps 30 --media_dir projects/<slug>/media -o Part1.mp4 \
    projects/<slug>/manim_code/<scene>_composed.py <SceneClass>

# 5. where does content sit behind the presenter?
.venv-tools/bin/python tools/avatar_windows.py <rendered bg> \
    projects/<slug>/windows_part1.json 91

# 6. composite
.venv-tools/bin/python tools/composite.py <rendered bg> inbox/clip_part1.mp4 \
    projects/<slug>/key_part1.json projects/<slug>/final/part1.mp4 \
    projects/<slug>/windows_part1.json
```

TinyTeX lives at `~/Library/TinyTeX` and must be on PATH for any render using
`MathTex`:

```bash
export PATH="$HOME/Library/TinyTeX/bin/universal-darwin:$PATH"
```

## The three things that are not obvious

**Captions come from the audio, not the script.** A shoot takes some lines from
the current script, some from an earlier draft, and paraphrases the rest. The
approved Faraday master covered only 51% and 58% of what its own clips actually
say — whole sentences, including the formal statement of the first law, played
with a caption showing something else. `tools/captions_from_audio.py` transcribes
the clip and uses the script only as a spelling and terminology reference.
Check `coverage()` after: below ~0.80 means look at it by hand.

**The chroma key is hue-based and calibrated per clip.** The screen is lit
unevenly (value 0.67–0.99 in one frame), so an RGB-distance `chromakey` wide
enough for its dark side also matches skin midtones — it was punching holes
through 8.3% of the presenter's face. Hue does not drift with lighting. Two keys
at different value references are combined with `blend=darken`, because one key
cannot span the whole range. Re-run `calibrate_key.py` for every new shoot.

**One caption line at a time, on its own clock.** A whole sentence held while
only its first half is spoken reads as out of sync even when the sentence is
timed correctly. The caption track is a flat list of `{start, text}` and is
deliberately NOT tied to the animation cues — a long animation must not hold a
stale caption. In the scene, `self.play` is overridden to flush any line that
falls due while an animation runs.

## Filter order in the composite

`despill` runs on the **colour branch only**, after the key has been taken from
the raw crop. Despilling first turns the green screen brown, `hsvkey` no longer
finds the hue it is looking for, nothing becomes transparent, and the whole
despilled background composites as a **brown rectangle behind the presenter**.

```
[1:v]crop,format=rgba,split=3[c][d1][d2];   <- raw crop feeds BOTH keys
[d1]hsvkey(v1),alphaextract[a1];
[d2]hsvkey(v2),alphaextract[a2];
[a1][a2]blend=darken,<repair>[al];
[c]despill[cc];                             <- colour only
[cc][al]alphamerge,...
```

## The question card owns the screen

A `cue(i, caption=False)` suppresses the caption track until the next cue. The
track is on its own clock now, so the flag alone no longer stops it — `cue()`
drops any line falling before the next cue's start. Without this the first
captions play over the question card.

## When to reach for a generated image

Almost never. Equations, graphs and labelled apparatus are sharper, exactly
controllable and free as Manim vectors. Use an image when a drawn diagram
genuinely fails to teach — the Faraday series apparatus rendered as vectors was
two empty rectangles joined by a bar, with the electrolytes, the electrode
metals and the shared circuit all invisible.

**Never ask the model for text in the image.** Generated lettering is
unreliable, and unreliable lettering on an exam diagram is worse than none. Ask
for the apparatus only and draw every label in Manim over the top. Do not name a
label, sign or symbol in the prompt either — naming a thing is an instruction to
draw it (`.claude/skills/video-prompt/references/bug-ledger.md`).

`src/concept_images.py` handles the alpha: gpt-image-2 has no transparency and
paints the checkerboard if asked for it, so the prompt requests a white studio
sweep which is cut to real alpha afterwards.

## Whisper drops audio silently — always check

On real clips the `small` model lost a **34-second stretch** of a 107s part and
`medium` still lost 10.6s, with no error either time: just a hole in the word
list, which becomes a hole in the captions that nobody notices until the video
is watched. `transcribe.py` warns about any gap over 4s.

The same audio transcribes fine when handed over on its own, so
`tools/fill_gaps.py` cuts each gap out, transcribes it alone and merges the
words back at the right offset. Run it until it reports no gaps — that recovered
`"E के समानुपाती हैं"`, which the caption had been showing as `"W के"`.

## Captions need an end, not just a start

A line with only a start stays up until the next one replaces it, so it hangs
through every pause between sentences and reads as out of sync even though its
start was right. Each line carries `end` — the moment its last word stops being
spoken — and the scene takes the caption down there if the next line is not due
within ~0.45s.

## The composite writes atomically and verifies

A run killed mid-write left a partial file at the destination, and the next run
wrote to the same path while the dying process still held it. The result had a
valid duration and a plausible size but decoded with 2604 errors and played
wrongly. `composite.py` now encodes to `<name>.partial.mp4`, decodes it to check
it is clean, and only then moves it into place — so a destination file is either
absent or good.

If you ever kill a composite, confirm it is gone before restarting:

```bash
pkill -9 -f composite.py; pkill -9 ffmpeg; sleep 3; pgrep -fl ffmpeg
```

To check any delivered file:

```bash
ffmpeg -v error -i final/clip.mp4 -f null -    # silence means clean
```

## Preflight — run it before every render

```bash
.venv-tools/bin/python tools/preflight.py              # all avatar-track projects
.venv-tools/bin/python tools/preflight.py daniell-cell # one
```

Exit code 1 on any FAIL, so it can gate a render. Every check exists because
that exact bug reached a finished video and had to be found by watching it:

| check | the bug it caught |
|---|---|
| composed file complete | a DOTALL regex in `recompose.py` deleted from its line to end-of-file; the result still parsed, just missing most of the scene |
| no stored-coordinate paths | electrons crossed the gap between the beakers through the air, because the path was captured before `place()` scaled the cell |
| transcript has no holes | Whisper silently dropped 34s, and the captions in that stretch were wrong |
| captions have end times | without one a caption hangs through every pause between sentences |
| captions monotonic / within audio | a caption starting after the audio ends is never shown |
| key hue is green, holes ≈ 0 | a mistuned key put the background through the presenter's face |
| generated image has real alpha | an opaque PNG composites as a hard rectangle on the plate |

## The layout guard runs inside every render

`src/manim_helpers.ThemedScene` audits after every animation and prints what it
found at tear-down. It reports rather than raises — one frame of a transition
legitimately has two things crossing, and failing there would be worse than the
bug.

It catches content overlapping content, and content leaving the stage band. Two
things a scene must do for it to be accurate:

- set `STAGE_BAND = (top, bottom)` so it knows the reserved area
- call `mark_group(diagram)` on any composite revealed **piece by piece**, or a
  rod inside its own beaker reads as an overlap

And use `along(mobject)` for `MoveAlongPath` — never a remembered point list.
