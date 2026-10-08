#!/bin/bash
# Build one part of BIO-C5-LA-04 (DNA replication) against its HeyGen clip.
#
#   bash tools/build_bio5b.sh <part>
#
# Same shape as build_bio4.sh, plus the two things this video is the first to
# carry: generated clips laid in as PANELS, and the route gate that decides
# which beats are allowed to be generated at all.
#
# ORDER MATTERS AND IT IS NOT THE OBVIOUS ONE.
#   composite lays the Veo panels in, because a panel is a background element:
#   it sits under the presenter and the presenter is resized around it.
#   burn_chips comes after, because a chip is an overlay. Burning a chip first
#   would put it under the panel; laying the panel last would put it over the
#   presenter's head.
set -u
cd "$(dirname "$0")/.."
export PATH="$HOME/Library/TinyTeX/bin/universal-darwin:$PATH"
export PYTHONPATH="$PWD"
export FFMPEG_THREADS="${FFMPEG_THREADS:-3}"
PY="$PWD/.venv-tools/bin/python"
PART="$1"
P=projects/bio-c5-la-04
CLIP=inbox/bio5b/part${PART}.mp4
CHIPS=tools/edu/renderer/spec/chips/bio5b.json
SP="${SCRATCH:-/tmp}/bio5b_${PART}"; mkdir -p "$SP"
log () { echo "[$(date +%H:%M:%S)] part$PART: $*"; }



TOTAL=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$CLIP")
CARDEND=$($PY -c "import json;print(json.load(open('$P/card_part${PART}.json'))[0][1])")

# ROUTE GATE, FIRST. It is the cheapest check and the only one that can still be
# acted on: it refuses a beat routed to Veo that has to get a count, an order, a
# direction or a pairing right, and it refuses a video that ended up with no
# generated clip at all. Both are decisions, not defects, so they are caught
# before anything is rendered rather than after.
$PY tools/route_gate.py "$P/route_part${PART}.json" \
  || { log "!! route gate failed"; exit 1; }

BODY="tools/edu/renderer/out/bio5b_${PART}_body.mp4"
if [ -f "$BODY" ] && [ "$BODY" -nt "tools/edu/renderer/spec/_bio5b_${PART}.json" ] \
                  && [ "$BODY" -nt "tools/edu/renderer/assets/biology-background.png" ]; then
  log "caption body — cached"
else
log "caption body"
# BG must be the BIOLOGY plate. full.mjs defaults to the chalk background and
# the Manim card uses the theme's biology plate, so leaving the default gives a
# video whose card and body have different backgrounds.
( cd tools/edu/renderer && cp spec/_bio5b_${PART}.json spec/segments.json && \
  nice -n 10 env BG=assets/biology-background.png \
       OUT=out/bio5b_${PART}_body.mp4 node full.mjs ) >"$SP/body.log" 2>&1 \
  || { log "!! body failed — $SP/body.log"; exit 1; }
fi

# The card cache watches the SHEET as well as meta.json. It used to watch only
# meta.json, so a corrected question card would never have shipped: the text is
# baked into the sheet PNG, and fixing meta.json changes nothing on screen.
CARD="$P/manim_code/media/videos/pyq_composed/1920p30/card${PART}.mp4"
if [ -f "$CARD" ] && [ "$CARD" -nt "$P/meta.json" ] \
                  && [ "$CARD" -nt "$P/assets/design/question_sheet.png" ]; then
  log "question card — cached"
else
  log "question card"
  ( cd "$P/manim_code" && PYQ_PROJECT=bio-c5-la-04 PYQ_PART=$PART \
    PYQ_UNTIL=$($PY -c "print(int($CARDEND)+2)") \
    nice -n 10 "$PWD/../../../.venv-manim/bin/manim" -qh --disable_caching \
    -o card${PART} pyq_composed.py PyqPart ) >"$SP/card.log" 2>&1
  [ -f "$CARD" ] || { log "!! card failed — $SP/card.log"; exit 1; }
fi
nice -n 10 ffmpeg -v error -threads $FFMPEG_THREADS -i "$CARD" -t "$CARDEND" -an \
  -c:v libx264 -preset medium -crf 19 -pix_fmt yuv420p -r 30 "$SP/card.mp4" -y

log "background"
printf "file '%s'\nfile '%s'\n" "$SP/card.mp4" "$PWD/$BODY" > "$SP/list"
nice -n 10 ffmpeg -v error -threads $FFMPEG_THREADS -f concat -safe 0 -i "$SP/list" \
  -vf "tpad=stop_mode=clone:stop_duration=0.5,fps=30" -t "$TOTAL" \
  -c:v libx264 -preset medium -crf 19 -pix_fmt yuv420p -r 30 -fps_mode cfr \
  "$SP/bg.mp4" -y || { log "!! background failed"; exit 1; }

# The generated clips, if this part has any. Argument 7 of composite.py is the
# clips file; the `-` before it are the optional resize windows this project
# does not use. A part with no Veo beat passes `-` and behaves exactly as the
# earlier videos did.
# VEO=0 builds the video WITHOUT the generated clips, so the rest can ship while
# they are still being made. Adding them later is a re-run of this script with
# VEO=1 — nothing else changes, because the clips are a composite-time input.
CLIPS="$P/clips_part${PART}.json"
[ "${VEO:-1}" = "0" ] && CLIPS="-"
[ -f "$CLIPS" ] || CLIPS="-"
if [ "$CLIPS" != "-" ]; then
  log "generated clips: $($PY -c "import json;c=json.load(open('$CLIPS'));print(sum(1 for x in c if x.get('usable',True)),'usable of',len(c))")"
fi

log "compositing"
OUT="$P/final/bio5b_part${PART}.mp4"; mkdir -p "$P/final"
nice -n 10 $PY tools/composite.py "$SP/bg.mp4" "$CLIP" "$P/keys/part${PART}.json" \
  "$OUT" - - "$CLIPS" - "$P/crop_part${PART}.json" "$P/card_part${PART}.json" \
  >"$SP/comp.log" 2>&1 || { log "!! composite failed — $SP/comp.log"; exit 1; }
cp "$OUT" "$SP/prechip.mp4"

# FIT, LOCK, THEN GATE — before the chips are burned, not after.
# On BIO-C1-LA-01 all four parts reached final/ with every chip 220px inside the
# presenter's face and the output gate passed them anyway: it checks encoding,
# not layout.
log "fitting chips above the presenter"
$PY tools/fit_chips_above_avatar.py "$SP/prechip.mp4" "$SP/bg.mp4" \
  "$P/plan_part${PART}.json" >"$SP/fit.log" 2>&1
$PY tools/lock_chip_family.py "$P/plan_part${PART}.json" "$CHIPS" >>"$SP/fit.log" 2>&1
$PY tools/avatar_clearance.py "$SP/prechip.mp4" "$SP/bg.mp4" \
  "$P/plan_part${PART}.json" | tee "$SP/clear.log"
grep -q "every chip clears the presenter" "$SP/clear.log" \
  || { log "!! a chip reaches the presenter - refusing to burn"; exit 1; }

# DASH GATE. Refuses to burn if any screen text still carries a long dash, or if
# an artefact is older than the spec that defines it. The second check is the
# one that matters: BIO-C1-LA-01's chip spec was de-dashed and the PNGs were
# never re-rendered, so two delivered parts kept showing an em dash.
# dash_gate takes the PROJECT and works out what to inspect itself; it used to
# take the spec and plan as well. Passing the old arguments fails argparse AFTER
# the composite has run, which is the most expensive place in the script to
# discover a CLI change.
$PY tools/dash_gate.py "$P" \
  || { log "!! dash gate failed - refusing to burn"; exit 1; }

# CHIP LABEL GATE. Pixels, not boxes: the chip is rendered twice, once with its
# labels emptied, and the difference is the label ink. A label lying on the
# drawing is what this refuses — "संश्लेषण असतत" once ran along the lower strand
# of the replication fork and every other check passed it.
$PY tools/chip_label_gate.py "$CHIPS" tools/edu/renderer/out/chips/bio5b \
  || { log "!! chip label gate failed - refusing to burn"; exit 1; }

log "chips"
nice -n 10 $PY tools/burn_chips.py "$SP/prechip.mp4" "$OUT" "$P/plan_part${PART}.json" \
  >"$SP/chips.log" 2>&1 || { log "!! chips failed — $SP/chips.log"; exit 1; }
$PY tools/output_gate.py "$OUT" || { log "!! output gate rejected"; exit 1; }
log "done -> $OUT"
