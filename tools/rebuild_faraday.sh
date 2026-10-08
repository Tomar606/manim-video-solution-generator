#!/bin/bash
# Rebuild one part of CHE-C2-LA-01 against a re-recorded presenter clip.
#
#   bash tools/rebuild_faraday.sh <part>
#
# Faster than the vitamins script it grew out of, in three ways that cost
# nothing in quality:
#
#   * the QUESTION CARD IS CACHED. It is a Manim render of a still card whose
#     content does not depend on the audio, yet every previous rebuild spent two
#     minutes re-rendering it identically. It is rebuilt only if the scene file
#     or meta.json is newer than the cached mp4.
#   * the chip burn and the answer page were two full re-encodes of the whole
#     video, back to back. They are now ONE pass, which removes an encode and a
#     generation of loss with it.
#   * FFMPEG_THREADS goes 2 -> 3. NOT higher: the cap exists because unbounded
#     x264 took ~300% of eight cores and left the machine unresponsive mid-render,
#     and the user often has a second video rendering alongside this one. Three
#     is roughly half the encode time while still leaving room for a Manim render
#     that is already taking two cores of the eight.
set -u
cd "$(dirname "$0")/.."
export PATH="$HOME/Library/TinyTeX/bin/universal-darwin:$PATH"
export PYTHONPATH="$PWD"
export FFMPEG_THREADS="${FFMPEG_THREADS:-3}"
PY="$PWD/.venv-tools/bin/python"
MANIM="$PWD/.venv-manim/bin/manim"
PART="$1"
P=projects/che-c2-la-01
CLIP=inbox/CHE-C2-LA-01_part${PART}_v2.mp4
SP="${SCRATCH:-/tmp}/far${PART}"; mkdir -p "$SP"
log () { echo "[$(date +%H:%M:%S)] $*"; }

log "planning (clock from the audio, captions off under graphics)"
$PY tools/plan_faraday.py "$PART" || exit 1
cp "$P/lines_part${PART}_v2.json" "$P/lines_part${PART}.json"
# Length comes from the CLIP, not from a transcript. It used to be read from a
# Whisper words file; when transcription was dropped the variable came out empty
# and ffmpeg was handed `-t ""`, which failed the background silently enough
# that the composite was the thing that appeared to break.
TOTAL=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$CLIP")
CARDEND=$($PY -c "import json;print(json.load(open('$P/card_part${PART}.json'))[0][1])")

log "caption body"
( cd tools/edu/renderer && cp spec/_far${PART}_v2.json spec/segments.json && \
  nice -n 10 env OUT=out/far${PART}_v2_body.mp4 node full.mjs ) >"$SP/body.log" 2>&1 \
  || { log "!! body failed — $SP/body.log"; exit 1; }

CARD="$P/manim_code/media/videos/pyq_composed/1920p30/card${PART}_v2.mp4"
if [ -f "$CARD" ] && [ "$CARD" -nt "projects/_pyq_template/scene.py" ] \
                  && [ "$CARD" -nt "$P/meta.json" ]; then
  log "question card — cached, skipping the render"
else
  log "question card"
  cp projects/_pyq_template/scene.py "$P/manim_code/pyq.py"
  $PY -c "
from tools.recompose import main
main([('$P/manim_code/pyq.py','$P/manim_code/pyq_composed.py',
       'projects/faraday-electrolysis/script.md')])" >/dev/null
  ( cd "$P/manim_code" && PYQ_PROJECT=che-c2-la-01 PYQ_PART=$PART \
    PYQ_UNTIL=$($PY -c "print(int($CARDEND)+2)") \
    nice -n 10 "$PWD/../../../.venv-manim/bin/manim" -qh --disable_caching \
    -o card${PART}_v2 pyq_composed.py PyqPart ) >"$SP/card.log" 2>&1
  [ -f "$CARD" ] || { log "!! card failed — $SP/card.log"; exit 1; }
fi
nice -n 10 ffmpeg -v error -threads $FFMPEG_THREADS -i "$CARD" -t "$CARDEND" -an \
  -c:v libx264 -preset medium -crf 19 -pix_fmt yuv420p -r 30 "$SP/card.mp4" -y

log "background"
printf "file '%s'\nfile '%s'\n" "$SP/card.mp4" \
  "$PWD/tools/edu/renderer/out/far${PART}_v2_body.mp4" > "$SP/list"
nice -n 10 ffmpeg -v error -threads $FFMPEG_THREADS -f concat -safe 0 -i "$SP/list" \
  -vf "tpad=stop_mode=clone:stop_duration=0.5,fps=30" -t "$TOTAL" \
  -c:v libx264 -preset medium -crf 19 -pix_fmt yuv420p -r 30 -fps_mode cfr \
  "$SP/bg.mp4" -y

log "compositing (FFMPEG_THREADS=$FFMPEG_THREADS)"
OUT="$P/final/far${PART}_v2.mp4"; mkdir -p "$P/final"
nice -n 10 $PY tools/composite.py "$SP/bg.mp4" "$CLIP" "$P/keys/part${PART}.json" \
  "$OUT" - - - - "$P/crop_part${PART}.json" "$P/card_part${PART}.json" \
  >"$SP/comp.log" 2>&1 || { log "!! composite failed — $SP/comp.log"; exit 1; }
cp "$OUT" "$SP/prechip.mp4"          # keep it: an overlay-only change is then cheap

log "chips + answer page (one pass)"
nice -n 10 $PY tools/burn_chips.py "$OUT" "$SP/chip.mp4" "$P/plan_part${PART}_v2.json" \
  >"$SP/burn.log" 2>&1 && mv "$SP/chip.mp4" "$OUT" \
  && mv "$SP/chip.mp4.geom.json" "$OUT.geom.json" 2>/dev/null
ANS=inbox/answers/endscreenshot/CHE-C2-LA-01.png
if [ "$PART" = "2" ] && [ -f "$ANS" ]; then
  nice -n 10 $PY tools/answer_overlay.py "$P" "$PART" "$ANS" --video "$OUT" \
    >"$SP/ans.log" 2>&1
  [ -f "${OUT%.mp4}.withanswer.mp4" ] && \
    { mv "$OUT.geom.json" "$SP/g.json" 2>/dev/null
      mv "${OUT%.mp4}.withanswer.mp4" "$OUT"
      mv "$SP/g.json" "$OUT.geom.json" 2>/dev/null; }
fi

log "output gate"
$PY tools/output_gate.py "$OUT" && log "PASS -> $OUT" || log "!! REJECTED"
