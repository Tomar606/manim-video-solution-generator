#!/bin/bash
# Rebuild every delivered video from its surviving parts.
#
#   bash tools/rebuild_all.sh [part-name ...]     (default: all of them)
#
# Everything expensive already exists — the caption bodies, the band chips, the
# specs. What changes is the CARD, because the marks sticker is new, and a card
# change means a fresh composite: the presenter is keyed over the card as well as
# the body, so it cannot be patched on afterwards.
#
# One part at a time, on purpose. Two composites in parallel drove swap to
# 13.4 GB of 14.3 GB and the machine stopped responding.
set -u
cd "$(dirname "$0")/.."
export PATH="$HOME/Library/TinyTeX/bin/universal-darwin:$PATH"
export PYTHONPATH="$PWD"
export FFMPEG_THREADS=2
PY="$PWD/.venv-tools/bin/python"
MANIM="$PWD/.venv-manim/bin/manim"
NICE="nice -n 19"
SP="${SCRATCH:-/tmp}/rebuild"
mkdir -p "$SP"

# name | project | part | clip | key | crop | cardwin | body | chips | total | answer
PARTS=(
"dry1|che-c2-la-05|1|inbox/heygens/sushak_-_1.mp4|part1|crop_part1|card_part1|dry_p1|dry1|145.10|"
"dry2|che-c2-la-05|2|inbox/heygens/sushak_Part2.mp4|part2|crop_part2|card_part2|dry_p2|dry2|176.70|inbox/answers/endscreenshot/CHE-C2-LA-04.png"
"corr|sanksharan|1|inbox/corrosion_heygen_clip.mp4|main|crop_main|card_main|sank_body|sank|127.00|inbox/answers/endscreenshot/CHE-C2-LA-02.png"
"vit01|che-c10-la-01|1|inbox/CHE-C10-LA-01/part1.mp4|part1|crop_part1|card_part1|vit01_body|vit01|143.66|inbox/answers/endscreenshot/CHEC10LA01.png"
"vit1|che-c10-la-02|1|inbox/CHE-C10-LA-02/part1.mp4|part1|crop_part1|card_part1|vit_p1|vit1|112.25|"
"vit2|che-c10-la-02|2|inbox/CHE-C10-LA-02/part2.mp4|part2|crop_part2|card_part2|vit_p2|vit2|115.98|inbox/answers/endscreenshot/CHE-C10-LA-02.corrected.png"
)

want=("$@")
run_this () { [ ${#want[@]} -eq 0 ] && return 0; for w in "${want[@]}"; do [ "$w" = "$1" ] && return 0; done; return 1; }

for row in "${PARTS[@]}"; do
  IFS='|' read -r name proj part clip key crop cardwin body chips total answer <<<"$row"
  run_this "$name" || continue
  echo "════ $name  ($proj part $part)"

  # the scene, with the marks sticker
  cp projects/_pyq_template/scene.py "projects/$proj/manim_code/pyq.py"
  $PY -c "
from tools.recompose import main
main([('projects/$proj/manim_code/pyq.py',
       'projects/$proj/manim_code/pyq_composed.py',
       'projects/faraday-electrolysis/script.md')])" >/dev/null

  cardend=$($PY -c "import json;print(json.load(open('projects/$proj/$cardwin.json'))[0][1])")
  echo "  card 0 -> ${cardend}s"
  ( cd "projects/$proj/manim_code" && \
    PYQ_PROJECT=$proj PYQ_PART=$part PYQ_UNTIL=$($PY -c "print(int($cardend)+2)") \
    $NICE "$MANIM" -qh --disable_caching -o card$part pyq_composed.py PyqPart \
    >"$SP/$name.card.log" 2>&1 )
  M="projects/$proj/manim_code/media/videos/pyq_composed/1920p30/card$part.mp4"
  [ -f "$M" ] || { echo "  !! card render failed"; continue; }

  $NICE ffmpeg -v error -threads 2 -i "$M" -t "$cardend" -an \
      -c:v libx264 -preset medium -crf 19 -pix_fmt yuv420p -r 30 -threads 2 \
      "$SP/$name.card.mp4" -y
  printf "file '%s'\nfile '%s'\n" "$SP/$name.card.mp4" \
      "$PWD/tools/edu/renderer/out/$body.mp4" > "$SP/$name.list"
  $NICE ffmpeg -v error -threads 2 -filter_threads 2 -f concat -safe 0 -i "$SP/$name.list" \
      -vf "tpad=stop_mode=clone:stop_duration=0.5,fps=30" -t "$total" \
      -c:v libx264 -preset medium -crf 19 -pix_fmt yuv420p -r 30 -fps_mode cfr \
      -threads 2 "$SP/$name.bg.mp4" -y

  out="projects/$proj/final/rb_$name.mp4"
  mkdir -p "projects/$proj/final"
  echo "  compositing ..."
  $NICE $PY tools/composite.py "$SP/$name.bg.mp4" "$clip" \
      "projects/$proj/keys/$key.json" "$out" \
      - - - - "projects/$proj/$crop.json" "projects/$proj/$cardwin.json" \
      >"$SP/$name.comp.log" 2>&1 || { echo "  !! composite failed"; continue; }

  if [ -f "$SP/plan.$chips.json" ]; then
    echo "  burning chips ..."
    $NICE $PY tools/burn_chips.py "$out" "$SP/$name.chip.mp4" "$SP/plan.$chips.json" \
        >"$SP/$name.burn.log" 2>&1 \
      && mv "$SP/$name.chip.mp4" "$out" && mv "$SP/$name.chip.mp4.geom.json" "$out.geom.json"
  fi

  if [ -n "$answer" ] && [ -f "$answer" ]; then
    echo "  answer page ..."
    $NICE $PY tools/answer_overlay.py "projects/$proj" "$part" "$answer" --video "$out" \
        >"$SP/$name.ans.log" 2>&1
    [ -f "${out%.mp4}.withanswer.mp4" ] && \
      { mv "$out.geom.json" "$SP/g.json"; mv "${out%.mp4}.withanswer.mp4" "$out"; \
        mv "$SP/g.json" "$out.geom.json"; }
  fi

  if $PY tools/output_gate.py "$out"; then echo "  ✓ $name"; else echo "  !! $name REJECTED"; fi
done
