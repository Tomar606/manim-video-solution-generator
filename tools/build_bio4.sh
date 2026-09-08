#!/bin/bash
# Build one part of BIO-C1-LA-01 against its HeyGen clip.
#
#   bash tools/build_bio1.sh <part>
#
# Same shape as rebuild_faraday.sh. Two differences worth knowing:
#   * the clock is the HeyGen srt, unrepaired — all four files end within 0.04s
#     of their own clip, so nothing is transcribed;
#   * the question card is cached per part. It does not depend on the audio, and
#     re-rendering it identically costs two minutes a go.
set -u
cd "$(dirname "$0")/.."
export PATH="$HOME/Library/TinyTeX/bin/universal-darwin:$PATH"
export PYTHONPATH="$PWD"
export FFMPEG_THREADS="${FFMPEG_THREADS:-3}"
PY="$PWD/.venv-tools/bin/python"
PART="$1"
P=projects/bio-c4-la-01
CLIP=inbox/bio4/part${PART}.mp4
SP="${SCRATCH:-/tmp}/bio4_${PART}"; mkdir -p "$SP"
log () { echo "[$(date +%H:%M:%S)] part$PART: $*"; }

TOTAL=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$CLIP")
CARDEND=$($PY -c "import json;print(json.load(open('$P/card_part${PART}.json'))[0][1])")

BODY="tools/edu/renderer/out/bio4_${PART}_body.mp4"
if [ -f "$BODY" ] && [ "$BODY" -nt "tools/edu/renderer/spec/_bio4_${PART}.json" ] \
                  && [ "$BODY" -nt "tools/edu/renderer/assets/biology-background.png" ]; then
  log "caption body — cached"
else
log "caption body"
# BG must be the BIOLOGY plate. full.mjs defaults to the chalk background
# and the Manim card uses the theme's biology plate, so leaving the default
# gives a video whose card and body have different backgrounds -- the first
# run shipped flasks and test tubes behind an ovule.
( cd tools/edu/renderer && cp spec/_bio4_${PART}.json spec/segments.json && \
  nice -n 10 env BG=assets/biology-background.png \
       OUT=out/bio4_${PART}_body.mp4 node full.mjs ) >"$SP/body.log" 2>&1 \
  || { log "!! body failed — $SP/body.log"; exit 1; }
fi

CARD="$P/manim_code/media/videos/pyq_composed/1920p30/card${PART}.mp4"
if [ -f "$CARD" ] && [ "$CARD" -nt "$P/meta.json" ] \
                  && [ "$CARD" -nt "$P/assets/design/question_sheet.png" ]; then
  log "question card — cached"
else
  log "question card"
  ( cd "$P/manim_code" && PYQ_PROJECT=bio-c4-la-01 PYQ_PART=$PART \
    PYQ_UNTIL=$($PY -c "print(int($CARDEND)+2)") \
    nice -n 10 "$PWD/../../../.venv-manim/bin/manim" -qh --disable_caching \
    -o card${PART} pyq_composed.py PyqPart ) >"$SP/card.log" 2>&1
  [ -f "$CARD" ] || { log "!! card failed — $SP/card.log"; exit 1; }
fi
nice -n 10 ffmpeg -v error -threads $FFMPEG_THREADS -i "$CARD" -t "$CARDEND" -an \
  -c:v libx264 -preset medium -crf 19 -pix_fmt yuv420p -r 30 "$SP/card.mp4" -y

log "background"
printf "file '%s'\nfile '%s'\n" "$SP/card.mp4" \
  "$PWD/tools/edu/renderer/out/bio4_${PART}_body.mp4" > "$SP/list"
nice -n 10 ffmpeg -v error -threads $FFMPEG_THREADS -f concat -safe 0 -i "$SP/list" \
  -vf "tpad=stop_mode=clone:stop_duration=0.5,fps=30" -t "$TOTAL" \
  -c:v libx264 -preset medium -crf 19 -pix_fmt yuv420p -r 30 -fps_mode cfr \
  "$SP/bg.mp4" -y || { log "!! background failed"; exit 1; }

log "compositing"
OUT="$P/final/bio4_part${PART}.mp4"; mkdir -p "$P/final"
nice -n 10 $PY tools/composite.py "$SP/bg.mp4" "$CLIP" "$P/keys/part${PART}.json" \
  "$OUT" - - - - "$P/crop_part${PART}.json" "$P/card_part${PART}.json" \
  >"$SP/comp.log" 2>&1 || { log "!! composite failed — $SP/comp.log"; exit 1; }
cp "$OUT" "$SP/prechip.mp4"

# FIT, LOCK, THEN GATE -- before the chips are burned, not after.
# On BIO-C1-LA-01 all four parts reached final/ with every chip 220px inside the
# presenter's face and the output gate passed them anyway: it checks encoding,
# not layout. Two of them sat there looking finished for forty minutes.
log "fitting chips above the presenter"
$PY tools/fit_chips_above_avatar.py "$SP/prechip.mp4" "$SP/bg.mp4" \
  "$P/plan_part${PART}.json" >"$SP/fit.log" 2>&1
$PY tools/lock_chip_family.py "$P/plan_part${PART}.json" \
  tools/edu/renderer/spec/chips/bio4.json >>"$SP/fit.log" 2>&1
$PY tools/avatar_clearance.py "$SP/prechip.mp4" "$SP/bg.mp4" \
  "$P/plan_part${PART}.json" | tee "$SP/clear.log"
grep -q "every chip clears the presenter" "$SP/clear.log" \
  || { log "!! a chip reaches the presenter - refusing to burn"; exit 1; }

# DASH GATE. Refuses to burn if any screen text still carries a long dash, or if
# an artefact is older than the spec that defines it. The second check is the
# one that matters: BIO-C1-LA-01's chip spec was de-dashed and the PNGs were
# never re-rendered, so two delivered parts kept showing an em dash.
$PY tools/dash_gate.py "$P" tools/edu/renderer/spec/chips/bio4.json "$P/plan_part${PART}.json" \
  || { log "!! dash gate failed - refusing to burn"; exit 1; }

log "chips"
nice -n 10 $PY tools/burn_chips.py "$SP/prechip.mp4" "$OUT" "$P/plan_part${PART}.json" \
  >"$SP/chips.log" 2>&1 || { log "!! chips failed — $SP/chips.log"; exit 1; }
$PY tools/output_gate.py "$OUT" || { log "!! output gate rejected"; exit 1; }
log "done -> $OUT"
