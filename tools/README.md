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
