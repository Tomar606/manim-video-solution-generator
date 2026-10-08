#!/bin/bash
# Rebuild all three parts of BIO-C4-LA-01 and put its answer pages back.
#
#   bash tools/rebuild_bio4.sh
#
# `tools/build_bio4.sh` builds ONE part and stops before the answer pages, which
# are appended to the last part only. Driving it by hand is how the wrong pages
# got shipped on BIO-C1-LA-01, so the pages are named here instead.
#
# The question card re-renders by itself: build_bio4.sh caches it against
# meta.json's timestamp, so editing the marks invalidates it.
set -u
cd "$(dirname "$0")/.."
export PYTHONPATH="$PWD"
PY="$PWD/.venv-tools/bin/python"
P=projects/bio-c4-la-01
log () { echo "[$(date +%H:%M:%S)] $*"; }

for N in 1 2 3; do
  log "part$N: building"
  bash tools/build_bio4.sh $N || { log "!! part$N failed"; exit 1; }
done

# The answer pages go at the END of the last part, always. FROM
# inbox/answers/house/ — that is the Arivihan page with the watermark;
# inbox/answers/bio/ is the textbook scan it was written from.
#
# HOLD 7, NOT 3. The dwell is a per-video decision and it is NOT the three
# seconds another project happened to use — these pages are dense handwritten
# text a student reads or screenshots. Measured off the previous delivery of
# this video: it ran 144.55s against a 129.47s body, and
# card_dur = fade + hold + xfade + hold2 + fade = 1 + 7 + 0.08 + 7 + 1 = 16.1s
# is the only value that reproduces it. Copying 3 from BIO-C1-LA-01 cut the
# pages from 15.5s on screen to 7.5s.
log "part3: appending the answer pages"
cp "$P/final/bio4_part3.mp4" "$P/final/bio4_part3_noanswer.mp4"
$PY tools/answer_outro.py "$P/final/bio4_part3_noanswer.mp4" \
  inbox/answers/house/c4_1.png "$P/final/bio4_part3.mp4" \
  --hold 7 --then inbox/answers/house/c4_2.png || { log "!! answer pages failed"; exit 1; }

log "done"
for N in 1 2 3; do
  F="$P/final/bio4_part${N}.mp4"
  printf "  %s  %ss\n" "$(basename $F)" \
    "$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$F" | cut -c1-6)"
done
