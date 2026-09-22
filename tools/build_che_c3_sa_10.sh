#!/usr/bin/env bash
# CHE-C3-SA-10 — built the house way, WITH SOUND: the reference recipe for the
# sound pass (scene cues -> snap_cues -> mix_cues -> gates). See
# assets/sfx/HOW_TO_USE.md.
#
# PYQ_PROJECT MUST BE SET, or pyq_composed.py renders the dry cell instead.
# LATEX MUST BE ON PATH for the formula beats — TinyTeX lives in
# ~/Library/TinyTeX/bin and is not exported by default; without it the render
# dies on FileNotFoundError: 'latex'.
# THE KEY IS THIS TAKE'S OWN — never carried from a neighbouring video.
set -euo pipefail
cd "$(dirname "$0")/.."
export FFMPEG_THREADS="${FFMPEG_THREADS:-5}"   # ONE build at a time: two at 5 threads swapped this 8GB box to a standstill
export PATH="$HOME/Library/TinyTeX/bin/universal-darwin:$PATH"
P=projects/che-c3-sa-10
HG=inbox/che-c3-sa-10/heygen_full.mp4
BODY=$P/manim_code/media/videos/pyq_composed/1920p30/PyqPart.mp4
KEY=$P/keys/key_part1.json
OUT=$P/final/che_c3_sa_10.mp4
W=/tmp/c3_10_build; mkdir -p "$W" "$P/final"
for f in "$BODY" "$HG" "$KEY"; do [ -f "$f" ] || { echo "!! missing $f"; exit 1; }; done

AUD=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$HG")
echo "background (audio is ${AUD}s)"
ffmpeg -v error -i "$BODY" -vf "tpad=stop_mode=clone:stop_duration=3,fps=30" \
  -t "$AUD" -an -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -r 30 \
  "$W/bg.mp4" -y
# the gates need THIS video's own background, not whichever was built last
mkdir -p "$P/work" && cp "$W/bg.mp4" "$P/work/bg.mp4"

echo "avatar windows"
.venv-tools/bin/python tools/avatar_windows.py "$W/bg.mp4" "$P/windows_part1.json" "$AUD"

echo "compositing"
.venv-tools/bin/python tools/composite.py "$W/bg.mp4" "$HG" "$KEY" "$W/keyed.mp4" \
  "$P/windows_part1.json" - "$P/clips_part1.json" - - "$P/card_part1.json"

echo "sound"
# SOUND EFFECTS. The scene cues its own key moments while it renders
# (src/sfx.py); this mixes them onto the HeyGen narration so the effect peaks
# where the picture changes. Passes the narration through untouched if the
# scene emitted nothing, so it is always safe to run.
AUDIO="$HG"
CUES=$P/cues_part1.json
if [ -f "$CUES" ]; then
  # SNAP FIRST. A cue is emitted when the scene ASKS for an animation; the
  # picture changes some way into it, and how far in depends on the animation.
  # Chasing that with a constant offset took four rebuilds and never fitted
  # every beat type. This moves each cue onto the frame-difference peak that
  # sfx_gate will measure, so the sound is accurate by construction.
  .venv-manim/bin/python tools/snap_cues.py "$W/bg.mp4" "$CUES"
  .venv-tools/bin/python tools/mix_cues.py "$HG" "$CUES" "$W/narration.wav"
  [ -f "$W/narration.wav" ] && AUDIO="$W/narration.wav"
fi
ffmpeg -v error -i "$W/keyed.mp4" -i "$AUDIO" -map 0:v -map 1:a \
  -c:v copy -c:a aac -b:a 192k -ar 48000 -ac 2 -shortest \
  -movflags +faststart "$OUT" -y
cp "$W/keyed.mp4.geom.json" "$OUT.geom.json"

echo
.venv-manim/bin/python tools/gates.py che-c3-sa-10 "$OUT"
