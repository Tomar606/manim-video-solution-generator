#!/usr/bin/env bash
# One part of a PYQ question in the REFERENCE LOOK (22 Sept 2026).
#
#     bash tools/build_ref.sh <slug> [part]        e.g. bio-c2-sa-04 2
#
# Scene: projects/<slug>/manim_code/pyq_composed.py, composed by
# tools/make_ref_scene.py (captions always on, one-line, numbered tables...).
# Presenter: ONE size all video (PRESENTER_ONE_SIZE), so no shrink windows.
# Veo panels: projects/<slug>/clips_part<N>.json, clips already cleaned of
# Flow's sparkle and fitted to their windows (tools/prep_veo_clip.py).
# Sound: the scene's cues, snapped to the picture, mixed under the narration.
# Ends on tools/gates.py, like every build.
set -euo pipefail
cd "$(dirname "$0")/.."
SLUG=$1; PART=${2:-1}
export FFMPEG_THREADS="${FFMPEG_THREADS:-4}"
export PATH="$HOME/Library/TinyTeX/bin/universal-darwin:$PATH"
export PRESENTER_ONE_SIZE="${PRESENTER_ONE_SIZE:-505}"
export DYLD_LIBRARY_PATH="/opt/homebrew/lib${DYLD_LIBRARY_PATH:+:$DYLD_LIBRARY_PATH}"   # Pillow shaping
P=projects/$SLUG
if [ -f inbox/$SLUG/part$PART.mp4 ]; then HG=inbox/$SLUG/part$PART.mp4; else HG=inbox/$SLUG/heygen_full.mp4; fi
KEY=$P/keys/key_part$PART.json
NAME=$(echo "$SLUG" | tr - _)
OUT=$P/final/${NAME}_part$PART.mp4
W=/tmp/ref_${NAME}_p$PART; mkdir -p "$W" "$P/final" "$P/work"
BODY=$P/manim_code/media/videos/pyq_composed/1920p30/PyqPart_part$PART.mp4

if [ ! -f "$KEY" ]; then
  echo "key"
  .venv-tools/bin/python tools/calibrate_key.py "$HG" "$KEY" | tail -1
fi
if [ ! -f "$BODY" ] || [ "$P/manim_code/pyq_composed.py" -nt "$BODY" ] || \
   [ "$P/beats_part$PART.json" -nt "$BODY" ] || [ "$P/lines_part$PART.json" -nt "$BODY" ]; then
  echo "scene"
  ( cd $P/manim_code && PYTHONPATH="$PWD/../../.." PYQ_PROJECT=$SLUG PYQ_PART=$PART \
      ../../../.venv-manim/bin/python -m manim -qh --disable_caching -o PyqPart_part$PART \
      pyq_composed.py PyqPart > "$W/manim.log" 2>&1 ) || { tail -20 "$W/manim.log"; exit 1; }
  cp $P/manim_code/layout_violations.json $P/work/layout_violations_part$PART.json
fi

AUD=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$HG")
echo "background (audio ${AUD}s)"
ffmpeg -v error -i "$BODY" -vf "tpad=stop_mode=clone:stop_duration=3,fps=30" \
  -t "$AUD" -an -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -r 30 "$W/bg.mp4" -y
cp "$W/bg.mp4" "$P/work/bg_part$PART.mp4"

echo "compositing (one presenter size: ${PRESENTER_ONE_SIZE}px)"
CLIPS=$P/clips_part$PART.json; [ -f "$CLIPS" ] || CLIPS=-
.venv-tools/bin/python tools/composite.py "$W/bg.mp4" "$HG" "$KEY" "$W/keyed.mp4" \
  - - "$CLIPS" - - "$P/card_part$PART.json"

echo "sound"
AUDIO="$HG"
CUES=$P/cues_part$PART.json
if [ -f "$CUES" ]; then
  # SNAP AGAINST THE COMPOSITED PICTURE, not the bare background: with a Veo
  # panel laid in, what the student sees change is the panel wiping in or out,
  # and sfx_gate measures that same picture. Snapping on bg.mp4 put a cue where
  # the background changed under a panel that was covering it.
  .venv-manim/bin/python tools/snap_cues.py "$W/keyed.mp4" "$CUES"
  .venv-tools/bin/python tools/mix_cues.py "$HG" "$CUES" "$W/narration.wav"
  [ -f "$W/narration.wav" ] && AUDIO="$W/narration.wav"
fi
ffmpeg -v error -i "$W/keyed.mp4" -i "$AUDIO" -map 0:v -map 1:a \
  -c:v copy -c:a aac -b:a 192k -ar 48000 -ac 2 -shortest -movflags +faststart "$OUT" -y
cp "$W/keyed.mp4.geom.json" "$OUT.geom.json" 2>/dev/null || true

echo
.venv-manim/bin/python tools/gates.py $SLUG "$OUT"
