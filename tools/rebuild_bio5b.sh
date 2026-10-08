#!/bin/bash
# Rebuild BIO-C5-LA-04 parts 2 and 3, now that both had empty windows filled.
#
#   bash tools/rebuild_bio5b.sh
#
# Part 1 is NOT rebuilt: its two clips are unchanged since it was built, and a
# rebuild would only re-encode identical frames.
#
# The answer pages are re-appended afterwards, because build_bio5b.sh stops
# before them and a rebuild overwrites the delivered file. HOLD 3 for this
# video — recovered from its own delivered length (115.90s body, 122.98s total,
# so an 8.08s card), not copied from a sibling: BIO-C1 and BIO-C4 both use 7,
# and assuming one number for all of them is how two videos shipped with their
# answer pages cut in half.
set -u
cd "$(dirname "$0")/.."
export PYTHONPATH="$PWD"
PY="$PWD/.venv-tools/bin/python"
P=projects/bio-c5-la-04
log () { echo "[$(date +%H:%M:%S)] $*"; }

mkdir -p "$P/final/_prev"
cp "$P"/final/bio5b_part[23].mp4 "$P/final/_prev/" 2>/dev/null || true

for N in 2 3; do
  log "part$N: building"
  bash tools/build_bio5b.sh $N || { log "!! part$N failed"; exit 1; }
done

log "part3: appending the answer pages"
cp "$P/final/bio5b_part3.mp4" "$P/final/bio5b_part3_noanswer.mp4"
$PY tools/answer_outro.py "$P/final/bio5b_part3_noanswer.mp4" \
  inbox/answers/house/c5b_1.png "$P/final/bio5b_part3.mp4" \
  --hold 3 --then inbox/answers/house/c5b_2.png || { log "!! answer pages failed"; exit 1; }

log "done"
for N in 1 2 3; do
  F="$P/final/bio5b_part${N}.mp4"
  printf "  %s  %ss\n" "$(basename $F)" \
    "$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$F" | cut -c1-6)"
done
