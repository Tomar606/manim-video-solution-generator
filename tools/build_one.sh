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
export FFMPEG_THREADS=6
PY=.venv-tools/bin/python
# NOT `taskpolicy -b`. That puts the job in macOS BACKGROUND QoS, which on
# Apple Silicon confines it to the efficiency cores and throttles its I/O — a
# measured 147% CPU out of 800% available, and a 135-second composite crawling
# at 1MB/min. The throttle was meant to keep the desktop responsive; under any
# contention it dominates instead, and the whole build becomes the bottleneck.
# `nice -n 5` yields the machine when something else wants it without giving up
# the performance cores. Diagnosed once already on this repo and fixed only in
# tools/finish_c5.sh, a one-off driver — so the pipeline's actual entry point
# kept the slow settings. FFMPEG_THREADS raised from 2 to 6 for the same reason.
NICE="nice -n 5"

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
built=""
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
  # STAMP THE START. `[ -f "$MC" ]` was the only check here, and a render that
  # died left the PREVIOUS run's file sitting at that path — so the composite ran
  # against a five-day-old background, the layout gate passed it, and the build
  # reported "ok p$p" while delivering the old plan with the old question card.
  # Freshness, not existence: the file has to be newer than this stamp.
  # PYQ_BATCH IS PASSED LITERALLY, never as ${batch:+PYQ_BATCH=$batch}. A shell
  # decides what is an assignment BEFORE it expands anything, so that form
  # produced the WORD `PYQ_BATCH=b2` in command position and the shell tried to
  # run it: "command not found", manim never started, and — with the old
  # existence-only check below — the previous run's render was composited
  # instead. `batch` is always set (defaulted at the top), and any value other
  # than b2 selects beats_part<N>.json, which is what batch 1 wants anyway.
  RLOG="projects/$slug/manim_code/render_p$p.log"
  STAMP="projects/$slug/manim_code/.render_stamp"
  : > "$RLOG"; touch "$STAMP"
  ( cd "projects/$slug/manim_code" && rm -f layout_violations.json && \
    PYQ_PROJECT=$slug PYQ_PART=$p PYQ_BATCH="$batch" $NICE ../../../.venv-manim/bin/manim \
      -qh --disable_caching -o "${OUT}${p}" pyq_composed.py PyqPart >"render_p$p.log" 2>&1 ) || true
  if [ ! -f "$MC" ] || [ ! "$MC" -nt "$STAMP" ]; then
    echo "  !! p$p render failed — last lines of $RLOG:"
    tail -6 "$RLOG" | sed 's/^/     /'
    rm -f "$STAMP"; ok=0; continue
  fi
  rm -f "$STAMP"
  # 2. does anything overlap? nothing composites if so
  $PY tools/layout_gate.py "projects/$slug" "$p" || { echo "  !! p$p blocked by layout gate"; ok=0; continue; }
  D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$MC" | cut -d. -f1)
  $PY tools/avatar_windows.py "$MC" "projects/$slug/${PRE}windows_part$p.json" "$D" >/dev/null 2>&1 || true
  # A beat that says `presenter: hidden` has to reach the COMPOSITOR too — the
  # scene can only declare it. Without this the diagram took the whole frame and
  # the presenter stayed standing in front of it.
  $PY tools/presenter_windows.py "projects/$slug" "$p" >/dev/null 2>&1 || true
  # THE CARD WINDOW AND THE SHRINK WINDOW MUST NOT OVERLAP. composite.py adds
  # both eases into one zoom expression on the assurance that they never
  # coincide — true for `big`, false for `card`: avatar_windows.py sees content
  # on the stage while the question card IS that content, so both fire at once
  # and z = 1 + (card_ratio - ratio) lands BELOW 1. zoompan cannot zoom out past
  # 1, so the presenter collapsed to a sliver at the bottom edge for the whole
  # card. Subtract the card spans here, where the data is, rather than teaching
  # the filter graph to reconcile them.
  $PY - "projects/$slug/${PRE}windows_part$p.json" "projects/$slug/card_part$p.json" <<'TRIM' || true
import json, sys
from pathlib import Path
w, c = Path(sys.argv[1]), Path(sys.argv[2])
if w.is_file() and c.is_file():
    wins = json.loads(w.read_text()); cards = json.loads(c.read_text())
    out = []
    for a, b in wins:
        spans = [(a, b)]
        for ca, cb in cards:
            nxt = []
            for sa, sb in spans:
                if cb <= sa or ca >= sb:
                    nxt.append((sa, sb)); continue
                if sa < ca: nxt.append((sa, ca))
                if cb < sb: nxt.append((cb, sb))
            spans = nxt
        out += [[round(x, 2), round(y, 2)] for x, y in spans if y - x >= 1.5]
    w.write_text(json.dumps(out, indent=1))
    print(f"  windows minus card: {wins} -> {out}")
TRIM
  KEY="projects/$slug/keys/part$p.json"; [ -f "$KEY" ] || KEY="projects/$slug/keys/part1.json"
  echo "  compositing p$p ..."
  if $NICE $PY tools/composite.py "$MC" "$src" "$KEY" \
       "projects/$slug/final/${PRE}${slug}_part$p.mp4" "projects/$slug/${PRE}windows_part$p.json" \
       "projects/$slug/presenter_part$p.json" - - - "projects/$slug/card_part$p.json" \
       </dev/null >/dev/null 2>&1; then echo "  ok p$p"; built="$built projects/$slug/final/${PRE}${slug}_part$p.mp4"; else echo "  !! p$p composite failed"; ok=0; fi
done

# ONLY STAMP A PART THIS RUN ACTUALLY PRODUCED. `last` used to be whatever file
# happened to be sitting in final/, so rebuilding ONE part re-stamped the answer
# page onto a DIFFERENT part that was already finished — it grew by the length of
# a second answer page every time, silently, and the build still said BUILD OK.
last=""; for g in $built; do [ -e "$g" ] && last="$g"; done
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
