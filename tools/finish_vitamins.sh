#!/bin/bash
# Finish the three vitamins parts and deliver them. Runs unattended.
#
#   SCRATCH=<dir> bash tools/finish_vitamins.sh
#
# Picks up from a rebuild that is already part-way: waits for it, repairs the
# part whose chip burn was killed mid-run, rebuilds CHE-C10-LA-01 because its
# captions changed (B वन -> B₁, B फोर -> B₃, B टेन -> B₉), then verifies every
# part actually carries its overlays before anything is delivered.
#
# The output gate does NOT check for chips -- it checks placement, sync and
# frame rate. A burn that dies leaves a file that gates clean and is missing
# every graphic, which is exactly what happened to vit1.
set -u
cd "$(dirname "$0")/.."
export PATH="$HOME/Library/TinyTeX/bin/universal-darwin:$PATH"
export PYTHONPATH="$PWD"
export FFMPEG_THREADS=2
PY="$PWD/.venv-tools/bin/python"
SP="${SCRATCH:-/tmp}/rebuild"
NICE="nice -n 19"
D="$HOME/Desktop/Final Chemistry"
log () { echo "[$(date +%H:%M:%S)] $*"; }

log "waiting for any rebuild in flight ..."
while pgrep -f rebuild_all.sh >/dev/null; do sleep 20; done
log "clear"

# ── CHE-C10-LA-01: captions changed, so the body and the whole part go again ──
log "re-rendering the LA-01 caption body"
$PY - <<'PY'
import json, re
from pathlib import Path
R = Path("projects/che-c10-la-01")
meta = json.loads((R / "meta.json").read_text())
lines = json.loads((R / "lines_part1.json").read_text())
SEPS = set(" \t।॥.,;:!?()[]\"'—-")
def golden(t):
    for w in meta["hilite"]:
        for m in re.finditer(re.escape(w), t):
            b = t[m.start()-1] if m.start() else None
            a = t[m.end()] if m.end() < len(t) else None
            if (b is None or b in SEPS) and (a is None or a in SEPS):
                return w
    return None
STARTS = [6, 12, 13, 17, 20, 24, 27, 28, 30, 32, 35, 38, 40, 42, 48, 51]
END = 143.56
segs = []
for n, i0 in enumerate(STARTS):
    i1 = STARTS[n+1] if n+1 < len(STARTS) else len(lines)
    t0 = lines[i0]["start"]; t1 = lines[i1]["start"] if i1 < len(lines) else END
    dur = round(t1 - t0, 2); ph = []
    for i in range(i0, i1):
        nxt = lines[i+1]["start"] if i+1 < len(lines) else END
        a = max(0.0, round(lines[i]["start"] - t0, 2))
        b = min(dur, round(min(nxt, t1) - t0, 2))
        if b - a < 0.25 and ph: ph[-1]["t_out"] = b; continue
        ph.append({"text": lines[i]["text"], "golden": golden(lines[i]["text"]),
                   "t_in": a, "t_out": b})
    ph[-1]["t_out"] = dur
    segs.append({"seg_id": n+1, "duration": dur, "type": "TEXT_ONLY",
                 "timing": "transcript", "labels": [],
                 "voiceover": " ".join(x["text"] for x in ph), "phrases": ph})
Path("tools/edu/renderer/spec/_vit01.json").write_text(
    json.dumps(segs, ensure_ascii=False, indent=1))
print(f"  spec: {len(segs)} segments")
PY
( cd tools/edu/renderer && cp spec/_vit01.json spec/segments.json && \
  $NICE env OUT=out/vit01_body.mp4 node full.mjs ) >"$SP/vit01.body.log" 2>&1
log "body done"

log "rebuilding vit01"
SCRATCH="${SCRATCH:-/tmp}" bash tools/rebuild_all.sh vit01 >>"$SP/rebuild.log" 2>&1

# ── every part must actually carry its chips ──────────────────────────────────
# name | project | a second INSIDE a chip window | desktop folder | file name
CHECKS=(
"vit01|che-c10-la-01|54|CHE-C10-LA-01 — विटामिन (स्रोत व रोग)|Vitamins — sources and diseases.mp4"
"vit1|che-c10-la-02|30|CHE-C10-LA-02 — विटामिन (परिभाषा व रोग)|Vitamins — Part 1.mp4"
"vit2|che-c10-la-02|30|CHE-C10-LA-02 — विटामिन (परिभाषा व रोग)|Vitamins — Part 2.mp4"
)
for row in "${CHECKS[@]}"; do
  IFS='|' read -r name proj at folder fname <<<"$row"
  out="projects/$proj/final/rb_$name.mp4"
  [ -f "$out" ] || { log "!! $name missing — skipped"; continue; }

  # Does the stage band carry anything? PEAK brightness, not mean: a chip puts
  # near-white text in the band (YMAX 247) while the bare plate peaks at 132.
  # The mean barely moves -- 32 against 29 -- and cannot tell them apart.
  ink=$($NICE ffmpeg -v error -ss "$at" -i "$out" -frames:v 1 \
        -vf "crop=1080:520:0:390,signalstats,metadata=print:file=-" -f null - 2>/dev/null \
        | grep -m1 -o 'YMAX=[0-9]*' | cut -d= -f2)
  if [ "${ink:-0}" -lt 190 ]; then
    log "$name: band looks empty (${ink:-0}) — re-burning"
    $NICE $PY tools/burn_chips.py "$out" "$SP/$name.fix.mp4" "$SP/plan.$name.json" \
        >"$SP/$name.reburn.log" 2>&1 \
      && mv "$SP/$name.fix.mp4" "$out" \
      && mv "$SP/$name.fix.mp4.geom.json" "$out.geom.json" \
      && log "$name: re-burned"
  else
    log "$name: chips present (${ink})"
  fi

  $PY tools/output_gate.py "$out" >/dev/null 2>&1 \
    && { mkdir -p "$D/$folder"
         cp "$out" "$D/$folder/$fname"
         cp "$out.geom.json" "$D/$folder/$fname.geom.json" 2>/dev/null
         log "delivered: $folder/$fname"; } \
    || log "!! $name REJECTED by the output gate — not delivered"
done
log "finished"
