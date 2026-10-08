#!/bin/bash
# Rebuild CHE-C10-LA-01 against the re-recorded presenter clip.
#
#   bash tools/rebuild_vit01.sh
#
# The narration changed, so everything derived from the CLOCK is rebuilt from
# the new audio: caption text and timing, the segment spec, the chip windows.
# What survives untouched is everything that does not depend on time -- the
# question card, the crop, the chroma key, the answer page, and the chip images
# themselves.
set -u
cd "$(dirname "$0")/.."
export PATH="$HOME/Library/TinyTeX/bin/universal-darwin:$PATH"
export PYTHONPATH="$PWD"
PY="$PWD/.venv-tools/bin/python"
MANIM="$PWD/.venv-manim/bin/manim"
SP="${SCRATCH:-/tmp}/vit01"; mkdir -p "$SP"
P=projects/che-c10-la-01
CLIP=inbox/CHE-C10-LA-01/part1_v2.mp4
TOTAL=139.48
log () { echo "[$(date +%H:%M:%S)] $*"; }

log "installing the new caption track"
cp "$P/lines_part1.json" "$P/lines_part1.old.json" 2>/dev/null || true
cp "$P/lines_v2.json" "$P/lines_part1.json"
$PY - <<'PY'
import json, pathlib
p = pathlib.Path("projects/che-c10-la-01/meta.json")
m = json.loads(p.read_text())
m["clip_end"]["1"] = 139.40
p.write_text(json.dumps(m, ensure_ascii=False, indent=1))
print("  clip_end -> 139.40")
PY

log "building the segment spec"
$PY - <<'PY'
import json, re
from pathlib import Path
R = Path("projects/che-c10-la-01")
meta = json.loads((R / "meta.json").read_text())
lines = json.loads((R / "lines_part1.json").read_text())
SEPS = set(" \t।॥.,;:!?()[]\"'—-")

def golden(t):
    """The one word in a line that gets the highlight, whole-word only."""
    for w in meta["hilite"]:
        for m in re.finditer(re.escape(w), t):
            b = t[m.start() - 1] if m.start() else None
            a = t[m.end()] if m.end() < len(t) else None
            if (b is None or b in SEPS) and (a is None or a in SEPS):
                return w
    return None

# The body plays AFTER the question card, so the spec must begin at the line
# the card hands over on. Starting it at line 0 instead shifted every caption
# in the video late by the card's length -- eighteen seconds, which put the B₂
# caption under the B₆ card. The card window is snapped to the nearest caption
# boundary so the two meet exactly rather than nearly.
card_end = json.loads((R / "card_part1.json").read_text())[0][1]
first = min(range(len(lines)), key=lambda i: abs(lines[i]["start"] - card_end))
card_end = lines[first]["start"]
(R / "card_part1.json").write_text(json.dumps([[0.0, card_end]]))
print(f"  card hands over at {card_end:.2f}s (caption line {first})")

# Segment boundaries are the presenter's own pauses, with a cap so no segment
# runs long. The previous build hard-coded the indices, which is only correct
# for the take they were measured on.
starts, n = [first], 0
for i in range(first, len(lines) - 1):
    gap = lines[i + 1]["start"] - lines[i]["end"]
    n += 1
    if gap > 0.30 or n >= 4:
        starts.append(i + 1)
        n = 0
END = 139.40
segs = []
for k, i0 in enumerate(starts):
    i1 = starts[k + 1] if k + 1 < len(starts) else len(lines)
    t0 = lines[i0]["start"]
    t1 = lines[i1]["start"] if i1 < len(lines) else END
    dur = round(t1 - t0, 2)
    ph = []
    for i in range(i0, i1):
        nxt = lines[i + 1]["start"] if i + 1 < len(lines) else END
        a = max(0.0, round(lines[i]["start"] - t0, 2))
        b = min(dur, round(min(nxt, t1) - t0, 2))
        if b - a < 0.25 and ph:
            ph[-1]["t_out"] = b
            continue
        ph.append({"text": lines[i]["text"], "golden": golden(lines[i]["text"]),
                   "t_in": a, "t_out": b})
    ph[-1]["t_out"] = dur
    segs.append({"seg_id": k + 1, "duration": dur, "type": "TEXT_ONLY",
                 "timing": "transcript", "labels": [],
                 "voiceover": " ".join(x["text"] for x in ph), "phrases": ph})
body = sum(s["duration"] for s in segs)
assert abs(card_end + body - END) < 0.05, (
    f"card {card_end:.2f} + body {body:.2f} != {END} -- the captions would drift")
Path("tools/edu/renderer/spec/_vit01_v2.json").write_text(
    json.dumps(segs, ensure_ascii=False, indent=1))
print(f"  {len(segs)} segments, {sum(s['duration'] for s in segs):.2f}s")
PY

log "rendering the caption body"
( cd tools/edu/renderer && cp spec/_vit01_v2.json spec/segments.json && \
  nice -n 10 env OUT=out/vit01_v2_body.mp4 node full.mjs ) >"$SP/body.log" 2>&1 \
  || { log "!! body render failed — see $SP/body.log"; exit 1; }
log "body done"

log "rendering the question card"
cp projects/_pyq_template/scene.py "$P/manim_code/pyq.py"
$PY -c "
from tools.recompose import main
main([('$P/manim_code/pyq.py','$P/manim_code/pyq_composed.py',
       'projects/faraday-electrolysis/script.md')])" >/dev/null
CARDEND=$($PY -c "import json;print(json.load(open('$P/card_part1.json'))[0][1])")
( cd "$P/manim_code" && PYQ_PROJECT=che-c10-la-01 PYQ_PART=1 \
  PYQ_UNTIL=$($PY -c "print(int($CARDEND)+2)") \
  nice -n 10 "$PWD/../../../.venv-manim/bin/manim" -qh --disable_caching \
  -o card1_v2 pyq_composed.py PyqPart ) >"$SP/card.log" 2>&1
M="$P/manim_code/media/videos/pyq_composed/1920p30/card1_v2.mp4"
[ -f "$M" ] || { log "!! card render failed — see $SP/card.log"; exit 1; }
nice -n 10 ffmpeg -v error -threads 2 -i "$M" -t "$CARDEND" -an \
  -c:v libx264 -preset medium -crf 19 -pix_fmt yuv420p -r 30 "$SP/card.mp4" -y

log "assembling the background"
printf "file '%s'\nfile '%s'\n" "$SP/card.mp4" \
  "$PWD/tools/edu/renderer/out/vit01_v2_body.mp4" > "$SP/list"
nice -n 10 ffmpeg -v error -threads 2 -f concat -safe 0 -i "$SP/list" \
  -vf "tpad=stop_mode=clone:stop_duration=0.5,fps=30" -t "$TOTAL" \
  -c:v libx264 -preset medium -crf 19 -pix_fmt yuv420p -r 30 -fps_mode cfr \
  "$SP/bg.mp4" -y

log "compositing the presenter"
OUT="$P/final/vit01_v2.mp4"; mkdir -p "$P/final"
nice -n 10 $PY tools/composite.py "$SP/bg.mp4" "$CLIP" "$P/keys/part1.json" "$OUT" \
  - - - - "$P/crop_part1.json" "$P/card_part1.json" >"$SP/comp.log" 2>&1 \
  || { log "!! composite failed — see $SP/comp.log"; exit 1; }

log "burning chips"
nice -n 10 $PY tools/burn_chips.py "$OUT" "$SP/chip.mp4" "$P/plan_v2.json" \
  >"$SP/burn.log" 2>&1 && mv "$SP/chip.mp4" "$OUT" \
  && mv "$SP/chip.mp4.geom.json" "$OUT.geom.json" 2>/dev/null
log "chips done"

ANS=inbox/answers/endscreenshot/CHEC10LA01.png
if [ -f "$ANS" ]; then
  log "answer page"
  nice -n 10 $PY tools/answer_overlay.py "$P" 1 "$ANS" --video "$OUT" \
    >"$SP/ans.log" 2>&1
  [ -f "${OUT%.mp4}.withanswer.mp4" ] && \
    { mv "$OUT.geom.json" "$SP/g.json" 2>/dev/null
      mv "${OUT%.mp4}.withanswer.mp4" "$OUT"
      mv "$SP/g.json" "$OUT.geom.json" 2>/dev/null; }
else
  log "!! answer image not found at $ANS"
fi

log "output gate"
$PY tools/output_gate.py "$OUT" && log "PASS -> $OUT" || log "!! REJECTED by the gate"
