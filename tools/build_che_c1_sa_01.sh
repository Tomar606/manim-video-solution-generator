#!/usr/bin/env bash
# CHE-C1-SA-01 — स्थिरक्वाथी मिश्रण (azeotropes).
#
# The house scene renders card + beats + captions; tools/composite.py keys the
# presenter and writes the geometry sidecar the output gate reads; the gates run
# last so nothing ships unchecked.
#
# PYQ_PROJECT MUST BE SET. pyq_composed.py defaults it to "che-c2-la-05", so a
# render without it silently produces the DRY CELL video — right format, wrong
# question, and only visible by looking at frames.
#
# CAPTION TIMINGS ARE NOT FROM THE DELIVERED SRT. Checked against the audio, it
# is out by up to 2.17s and in both directions. lines_part1.json is rebuilt from
# the transcription plus measured speech onsets where whisper could not read the
# audio; the original is kept as lines_srt_original.json.
set -euo pipefail
cd "$(dirname "$0")/.."
P=projects/che-c1-sa-01
HG=inbox/che-c1-sa-01/heygen_full.mp4
BODY=$P/manim_code/media/videos/pyq_composed/1920p30/che_body.mp4
KEY=$P/keys/key_part1.json
OUT=$P/final/che_c1_sa_01.mp4
W=/tmp/che_build; mkdir -p "$W" "$P/final"
for f in "$BODY" "$HG" "$KEY"; do [ -f "$f" ] || { echo "!! missing $f"; exit 1; }; done

AUD=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$HG")
echo "background (audio is ${AUD}s)"
# THE PICTURE IS A SECOND SHORT OF THE AUDIO. The scene ends on the last beat;
# the take carries on talking. Holding the final frame is right here — the close
# is "Notes button पर click करके", which needs no new picture — but the pad has
# to be explicit or the mux would simply cut the last line off.
ffmpeg -v error -i "$BODY" -vf "tpad=stop_mode=clone:stop_duration=3,fps=30" \
  -t "$AUD" -an -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -r 30 \
  "$W/bg.mp4" -y
# THE GATES NEED THIS VIDEO'S OWN BACKGROUND. gates.py used to hunt
# /tmp/<subject>_build/bg.mp4, so every chemistry slug found whichever
# chemistry video was built last and graded against it.
mkdir -p "$P/work" && cp "$W/bg.mp4" "$P/work/bg.mp4"

echo "compositing"
# WHERE CONTENT SITS BEHIND HIM, HE MOVES — not the content. avatar_windows.py
# measures the rendered background against the presenter's own rectangle and
# reports every stretch where ink falls inside it; composite.py shrinks and
# drops him for exactly those windows. Built without this, item 2 of a list
# printed across his forehead and his raised hand covered the word "नहीं".
.venv-tools/bin/python tools/avatar_windows.py "$W/bg.mp4" "$P/windows_part1.json" "$AUD"

.venv-tools/bin/python tools/composite.py "$W/bg.mp4" "$HG" "$KEY" "$W/keyed.mp4" \
  "$P/windows_part1.json" - - - - "$P/card_part1.json"

echo "sound"
ffmpeg -v error -i "$W/keyed.mp4" -i "$HG" -map 0:v -map 1:a \
  -c:v copy -c:a aac -b:a 192k -ar 48000 -ac 2 -shortest \
  -movflags +faststart "$OUT" -y
cp "$W/keyed.mp4.geom.json" "$OUT.geom.json"

echo
.venv-manim/bin/python tools/gates.py che-c1-sa-01 "$OUT"
