#!/bin/bash
# Finish CHE-C5-LA-01: render both parts against the current card, composite,
# stamp the faculty's answer page on the last part, gate. Unattended.
#
# LIVES IN tools/, NOT the scratchpad. The first version of this script was
# written to the session scratchpad and the scratchpad was cleaned mid-run —
# the script vanished, the job died, and it had already deleted part 1's render.
# Anything long-running must survive a scratchpad sweep. Logs go to the project.
set -u
cd "$(dirname "$0")/.."
export PATH="$HOME/Library/TinyTeX/bin/universal-darwin:$PATH"
export PYTHONPATH="$PWD"; export FFMPEG_THREADS=6
PY=.venv-tools/bin/python; M=.venv-manim/bin/manim
slug=che-c5-la-01; PRE=b2_
LOG="projects/$slug/finish.log"; : > "$LOG"
# NOT `taskpolicy -b`. That puts the job in macOS's background QoS band, which
# throttles CPU and I/O hard — under contention it was the dominant cost, not the
# work itself. Plain low-ish nice keeps the machine usable without surrendering
# the cores. FFMPEG_THREADS raised from 2 to 6 for the same reason.
NICE="nice -n 5"
say(){ echo "$@" | tee -a "$LOG"; }

for p in 1 2; do
  MC="projects/$slug/manim_code/media/videos/pyq_composed/1920p30/b2_part$p.mp4"
  say "=== render p$p ==="
  ( cd projects/$slug/manim_code && rm -f media/videos/pyq_composed/1920p30/b2_part$p.mp4 && \
    PYQ_PROJECT=$slug PYQ_PART=$p PYQ_BATCH=b2 $NICE ../../../$M -qh --disable_caching \
      -o b2_part$p pyq_composed.py PyqPart >"render_p$p.log" 2>&1 )
  if [ -f "$MC" ]; then say "  rendered p$p"; else
    say "  !! p$p RENDER FAILED"; tail -4 "projects/$slug/manim_code/render_p$p.log" | tee -a "$LOG"; exit 1; fi
done

built=""
for p in 1 2; do
  MC="projects/$slug/manim_code/media/videos/pyq_composed/1920p30/b2_part$p.mp4"
  src="inbox/CHE-C5-LA-01/part${p}.mp4"
  D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$MC" | cut -d. -f1)
  $PY tools/avatar_windows.py "$MC" "projects/$slug/${PRE}windows_part$p.json" "$D" >/dev/null 2>&1 || true
  $PY tools/presenter_windows.py "projects/$slug" "$p" >/dev/null 2>&1 || true
  $PY - "projects/$slug/${PRE}windows_part$p.json" "projects/$slug/card_part$p.json" >>"$LOG" 2>&1 <<'TRIM' || true
import json, sys
from pathlib import Path
w, c = Path(sys.argv[1]), Path(sys.argv[2])
if w.is_file() and c.is_file():
    wins = json.loads(w.read_text()); cards = json.loads(c.read_text()); out = []
    for a, b in wins:
        spans = [(a, b)]
        for ca, cb in cards:
            nxt = []
            for sa, sb in spans:
                if cb <= sa or ca >= sb: nxt.append((sa, sb)); continue
                if sa < ca: nxt.append((sa, ca))
                if cb < sb: nxt.append((cb, sb))
            spans = nxt
        out += [[round(x,2), round(y,2)] for x, y in spans if y - x >= 1.5]
    w.write_text(json.dumps(out, indent=1)); print(f"  windows minus card -> {out}")
TRIM
  KEY="projects/$slug/keys/part$p.json"; [ -f "$KEY" ] || KEY="projects/$slug/keys/part1.json"
  say "=== composite p$p ==="
  if $NICE $PY tools/composite.py "$MC" "$src" "$KEY" \
       "projects/$slug/final/${PRE}${slug}_part$p.mp4" "projects/$slug/${PRE}windows_part$p.json" \
       "projects/$slug/presenter_part$p.json" - - - "projects/$slug/card_part$p.json" \
       </dev/null >/dev/null 2>&1; then
    say "  ok p$p"; built="$built projects/$slug/final/${PRE}${slug}_part$p.mp4"
  else say "  !! p$p COMPOSITE FAILED"; fi
done

last=""; for g in $built; do [ -e "$g" ] && last="$g"; done
if [ -n "$last" ]; then
  $PY tools/answer_outro.py "$last" "inbox/answers/${slug}_1.png" "$last.a.mp4" --hold 7 >/dev/null 2>&1 \
    && mv "$last.a.mp4" "$last" && say "  answer page on $(basename "$last")"
  $PY tools/output_gate.py "$last" >>"$LOG" 2>&1 && say "  OUTPUT OK"
fi
say "=== DONE ==="
