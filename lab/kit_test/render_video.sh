#!/bin/bash
# Render every part of a kit-planned video once its Veo clips are in.
#   bash lab/kit_test/render_video.sh <project-slug> <plan-stem-prefix> <n-parts> <n-clips>
# e.g. bash lab/kit_test/render_video.sh geo-c14-la-02 plan_geo_c14_la_02 2 11
# Waits (up to 60 min) for veo/clips/b01..bNN, strips Flow's marker into veo/clean,
# then for each part: compile -> graphics layer -> composite + encode -> gates.
set -u
cd "$(dirname "$0")/../.."
SLUG=$1; PLAN=$2; PARTS=$3; NCLIPS=$4
V=projects/$SLUG/veo
PY=.venv-tools/bin/python
for i in $(seq 1 120); do
  have=0; for n in $(seq -f "%02g" 1 $NCLIPS); do [ -f $V/clips/b$n.mp4 ] && have=$((have+1)); done
  echo "clips: $have of $NCLIPS"
  [ $have -ge $NCLIPS ] && break
  sleep 30
done
$PY - <<EOF
from pathlib import Path
from src.veo_delogo import delogo
V = Path("$V")
for c in sorted((V / "clips").glob("b*.mp4")):
    out = V / "clean" / c.name
    if not out.exists():
        delogo(c, out, (570, 1132, 62, 60))      # Flow's marker on 720x1280; find_marker misses it at this size
        print("cleaned", c.name)
EOF
for p in $(seq 1 $PARTS); do
  echo "== part $p"
  $PY lab/kit_test/compile.py lab/kit_test/${PLAN}_p$p.json > /dev/null || exit 1
  node lab/kit_test/frames.mjs out/${PLAN}_p$p 2>&1 | tail -1
  $PY -u lab/kit_test/compose.py lab/kit_test/${PLAN}_p$p.json ${MUSIC:+--music $MUSIC} 2>/dev/null | grep -v "^  [0-9]"
  echo "composited part $p"
done
echo "ALL PARTS DONE"
