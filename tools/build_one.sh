#!/bin/bash
# Build ONE video, end to end, with every gate in the right order.
#
#   bash tools/build_one.sh <slug> [batch]
#
# One video at a time, by design. Parallel streams on this machine drove swap to
# 13.4GB of 14.3GB and the user's windows stopped responding.
set -u
cd "$(dirname "$0")/.."
export PATH="$HOME/Library/TinyTeX/bin/universal-darwin:$PATH"
export PYTHONPATH="$PWD"
export FFMPEG_THREADS=2
PY=.venv-tools/bin/python
NICE="nice -n 19"; command -v taskpolicy >/dev/null && NICE="taskpolicy -b nice -n 19"

slug="${1:?usage: build_one.sh <slug> [batch]}"
batch="${2:-b2}"
[ "$batch" = "b2" ] && BF="beats_b2_part" && OUT="b2_part" && PRE="b2_" || { BF="beats_part"; OUT="part"; PRE=""; }

# 0. is the machine fit to render at all?
$PY tools/machine_ready.py || exit 1
# 1. is the PLAN sound? nothing renders if not
$PY tools/preflight_beats.py "projects/$slug" ${batch:+--batch $batch} || exit 1

cp projects/_pyq_template/scene.py "projects/$slug/manim_code/pyq.py"
$PY tools/recompose.py >/dev/null 2>&1

ok=1
for f in projects/$slug/${BF}[0-9].json; do
  [ -e "$f" ] || continue
  p=$(basename "$f" .json); p=${p##*part}
  src=$($PY - "$slug" "$p" <<'EOF'
import sys, json
from pathlib import Path
slug, p = sys.argv[1], sys.argv[2]
special = {
 ("che-c1-la-01","1"):"inbox/heygens/brakely - 1_1080p.mp4",
 ("che-c1-la-01","2"):"inbox/heygens/barkale_Part2_1080p.mp4",
 ("che-c1-la-02","1"):"inbox/heygens/Quathanank - 1_1080p.mp4",
 ("che-c1-la-02","2"):"inbox/CHE-C1-LA-02/part2.mp4",
 ("che-c2-la-05","1"):"inbox/heygens/sushak_-_1.mp4",
 ("che-c2-la-05","2"):"inbox/heygens/sushak_Part2.mp4",
 ("che-c3-la-02","1"):"inbox/heygens/suhunya koti 1part - 1_1080p.mp4",
 ("che-c3-la-02","2"):"inbox/heygens/shunya koti -Part2_1080p.mp4",
 ("che-c4-la-02","1"):"inbox/heygens/kmno4 parts - 1_1080p.mp4",
 ("che-c4-la-02","2"):"inbox/heygens/kmno4_Part2_1080p.mp4",
}
print(special.get((slug,p), f"inbox/{slug.upper()}/part{p}.mp4"))
EOF
)
  [ -f "$src" ] || { echo "  -- p$p: no presenter clip ($src)"; ok=0; continue; }
  MC="projects/$slug/manim_code/media/videos/pyq_composed/1920p30/${OUT}${p}.mp4"
  echo "  rendering p$p ..."
  ( cd "projects/$slug/manim_code" && rm -f layout_violations.json && \
    PYQ_PROJECT=$slug PYQ_PART=$p ${batch:+PYQ_BATCH=$batch} $NICE ../../../.venv-manim/bin/manim \
      -qh --disable_caching -o "${OUT}${p}" pyq_composed.py PyqPart >/dev/null 2>&1 ) || true
  [ -f "$MC" ] || { echo "  !! p$p render failed"; ok=0; continue; }
  # 2. does anything overlap? nothing composites if so
  $PY tools/layout_gate.py "projects/$slug" "$p" || { echo "  !! p$p blocked by layout gate"; ok=0; continue; }
  D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$MC" | cut -d. -f1)
  $PY tools/avatar_windows.py "$MC" "projects/$slug/${PRE}windows_part$p.json" "$D" >/dev/null 2>&1 || true
  KEY="projects/$slug/keys/part$p.json"; [ -f "$KEY" ] || KEY="projects/$slug/keys/part1.json"
  echo "  compositing p$p ..."
  if $NICE $PY tools/composite.py "$MC" "$src" "$KEY" \
       "projects/$slug/final/${PRE}${slug}_part$p.mp4" "projects/$slug/${PRE}windows_part$p.json" \
       "projects/$slug/presenter_part$p.json" - - - "projects/$slug/card_part$p.json" \
       </dev/null >/dev/null 2>&1; then echo "  ok p$p"; else echo "  !! p$p composite failed"; ok=0; fi
done

last=""; for g in projects/$slug/final/${PRE}${slug}_part[0-9].mp4; do [ -e "$g" ] && last="$g"; done
pg=$(ls inbox/answers/${slug}_*.png 2>/dev/null | head -1)
if [ "$ok" = "1" ] && [ -n "$pg" ] && [ -n "$last" ]; then
  $PY tools/answer_outro.py "$last" "$pg" "$last.a.mp4" --hold 7 >/dev/null 2>&1 \
    && mv "$last.a.mp4" "$last" && echo "  answer on the last part"
fi
# LAST GATE: the finished file itself. The layout gate checks the render and the
# preflight checks the plan, but neither can see a floating presenter or audio
# drifting against picture — both of which were "fixed" in source more than once
# and came back, because nothing stopped the file being handed over.
if [ "$ok" = "1" ] && [ -n "$last" ]; then
  if ! $PY tools/output_gate.py "$last" ${GRAPHICS_FROM:+--graphics-from $GRAPHICS_FROM}; then
    echo "  BUILD REJECTED by the output gate — not delivering"; exit 1
  fi
  echo "  BUILD OK — not delivered yet; review first, then copy"
else
  echo "  BUILD FAILED — nothing delivered, existing folder untouched"; exit 1
fi
