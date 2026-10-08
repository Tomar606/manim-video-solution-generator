#!/bin/bash
# Re-burn BIO-C1-LA-01's chips onto the composites already approved.
#
#   bash tools/rebuild_bio1_chips.sh
#
# The ovule figure was redrawn; NOTHING else about these four videos changed.
# The chips are burned in the last step of tools/build_bio1.sh, onto a
# `prechip.mp4` that the build leaves in its scratch directory, so re-running
# that one step reproduces the delivered file exactly except for the figure.
# A full rebuild would re-composite four videos to reach the same frames.
#
# Each part is written to a temporary file and moved into place only once it
# has been written whole — burn_chips writes its output directly, and a run
# interrupted half way through would otherwise leave a delivered file truncated.
set -u
cd "$(dirname "$0")/.."
export PYTHONPATH="$PWD"
PY="$PWD/.venv-tools/bin/python"
P=projects/bio-c1-la-01
log () { echo "[$(date +%H:%M:%S)] $*"; }

$PY tools/dash_gate.py "$P" || { log "!! dash gate failed - refusing to burn"; exit 1; }

for N in 1 2 3 4; do
  PRE=/tmp/bio1_$N/prechip.mp4
  [ -f "$PRE" ] || { log "!! part$N: no prechip at $PRE - run tools/build_bio1.sh $N"; exit 1; }
  # Part 4 carries the answer pages, which are appended AFTER the chips; its
  # chip burn therefore produces the _noanswer file, not the delivered one.
  if [ "$N" = 4 ]; then OUT="$P/final/bio1_part4_noanswer.mp4"; else OUT="$P/final/bio1_part${N}.mp4"; fi
  log "part$N: burning chips"
  nice -n 10 $PY tools/burn_chips.py "$PRE" "$OUT.new.mp4" "$P/plan_part${N}.json" \
    >/tmp/bio1_$N/chips2.log 2>&1 || { log "!! part$N chips failed - /tmp/bio1_$N/chips2.log"; exit 1; }
  ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT.new.mp4" >/dev/null \
    || { log "!! part$N output will not decode"; exit 1; }
  mv "$OUT.new.mp4" "$OUT"
  log "part$N -> $OUT"
done

# The answer pages go at the END of the last part, always, whatever the outro
# says. A rebuild overwrites the file, so they are re-appended every time.
#
# FROM inbox/answers/house/, NOT inbox/answers/bio/. Both hold a c1 pair and
# they look alike in a listing, but bio/ is the TEXTBOOK SCAN the answer was
# written from — printed type on white — and house/ is the page Arivihan
# publishes: ruled paper, handwriting, the diagram in pencil, and the watermark.
# The scan shipped once, and it is the one thing in the video that is not ours.
#
# HOLD 7. Read it off the file that actually SHIPPED, not off a build log —
# the log of an earlier rebuild said 12.1s, but that rebuild had already
# shortened the card, and the copy in ~/Desktop/Final Biology runs 150.38s
# against the same 135.30s body. Only hold=7 gives that:
#   total = body - fade + card, card = fade + hold + xfade + hold2 + fade
#         = 135.30 - 1 + (1 + 7 + 0.08 + 7 + 1) = 150.4
# Passing 3 cut the pages to 8.1s on screen and 5 to 12.1s.
log "part4: appending the answer pages"
nice -n 10 $PY tools/answer_outro.py "$P/final/bio1_part4_noanswer.mp4" \
  inbox/answers/house/c1_1.png "$P/final/bio1_part4.mp4" \
  --hold 7 --then inbox/answers/house/c1_2.png \
  >/tmp/bio1_4/answer2.log 2>&1 || { log "!! answer pages failed - /tmp/bio1_4/answer2.log"; exit 1; }
log "done"
for N in 1 2 3 4; do
  F="$P/final/bio1_part${N}.mp4"
  printf "  %s  %ss  %sMB\n" "$F" \
    "$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$F" | cut -c1-6)" \
    "$(( $(stat -f%z "$F") / 1048576 ))"
done
