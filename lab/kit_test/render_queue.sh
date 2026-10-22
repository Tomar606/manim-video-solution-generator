#!/bin/bash
# One part at a time: compile -> graphics -> composite -> verify -> free the frames.
#   bash lab/kit_test/render_queue.sh "<plan-stem>|<music>" ...
cd "$(dirname "$0")/../.."
PY=.venv-tools/bin/python
for job in "$@"; do
  plan=${job%%|*}; music=${job#*|}
  echo "== $plan"
  # a part needs ~0.4 GB (frames + mp4); keep 1.5 GB spare so swap growth cannot fill the disk mid-render
  avail=$(df -m / | awk 'NR==2{print $4}'); [ "$avail" -lt 1500 ] && { echo "STOP: only ${avail} MB free"; exit 1; }
  $PY lab/kit_test/compile.py lab/kit_test/$plan.json > /dev/null || { echo "FAIL compile $plan"; continue; }
  node lab/kit_test/frames.mjs out/$plan 2>&1 | tail -1
  [ -f lab/kit_test/out/$plan/frames/g_00000.png ] || { echo "FAIL no frames for $plan"; continue; }
  out=$($PY -u lab/kit_test/compose.py lab/kit_test/$plan.json --music $music 2>/dev/null | tail -1)
  streams=$(ffprobe -v error -show_entries stream=codec_type -of csv=p=0 "$out" | sort -u | tr '\n' ' ')
  [ "$streams" = "audio video " ] && echo "OK $out" || { echo "FAIL streams [$streams] $out"; continue; }
  # the gates: sidecar first (the output gate reads the build geometry from it), then every gate
  $PY lab/kit_test/geom_sidecar.py lab/kit_test/$plan.json "$out" > /dev/null
  slug=$($PY -c "import json,sys; print(json.load(open(sys.argv[1]))['project'])" lab/kit_test/$plan.json)
  $PY tools/gates.py "$slug" "$out" 2>&1 | grep -E "FAIL|passed" | sed "s/^/  gates: /"
  rm -rf lab/kit_test/out/$plan/frames
done
echo "QUEUE DONE"
