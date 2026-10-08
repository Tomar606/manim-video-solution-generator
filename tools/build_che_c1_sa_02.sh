#!/usr/bin/env bash
# CHE-C1-SA-02 — समपरासरी विलयन और अर्द्धपारगम्य झिल्ली.
#
# Same shape as build_che_c1_sa_01.sh: the house scene renders card + beats +
# captions, tools/composite.py keys the presenter and lays in the Veo panel,
# and tools/gates.py runs last so nothing ships unchecked.
#
# PYQ_PROJECT MUST BE SET — pyq_composed.py defaults it to "che-c2-la-05", so a
# render without it silently produces the DRY CELL video.
#
# THE KEY IS THIS TAKE'S OWN (hue 85.37). sa-01 measured 85.51 and the two are
# not interchangeable; carrying a neighbouring clip's key is what darkened the
# presenter's face by a uniform 0.815 on PHY-C1-SA-01.
#
# clips_part1.json may be EMPTY. The raisin panel is generated in Flow by hand
# (tools/veo_manual.py — the grid is virtualised and the bridge cannot reach a
# finished clip), so the video builds with or without it and gains the panel on
# a rebuild once the file lands.
set -euo pipefail
cd "$(dirname "$0")/.."
P=projects/che-c1-sa-02
HG=inbox/che-c1-sa-02/heygen_full.mp4
BODY=$P/manim_code/media/videos/pyq_composed/1920p30/c2_body.mp4
KEY=$P/keys/key_part1.json
OUT=$P/final/che_c1_sa_02.mp4
W=/tmp/che2_build; mkdir -p "$W" "$P/final"
for f in "$BODY" "$HG" "$KEY"; do [ -f "$f" ] || { echo "!! missing $f"; exit 1; }; done

AUD=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$HG")
echo "background (audio is ${AUD}s)"
ffmpeg -v error -i "$BODY" -vf "tpad=stop_mode=clone:stop_duration=3,fps=30" \
  -t "$AUD" -an -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -r 30 \
  "$W/bg.mp4" -y
# THE GATES NEED THIS VIDEO'S OWN BACKGROUND. gates.py used to hunt
# /tmp/<subject>_build/bg.mp4, so every chemistry slug found whichever
# chemistry video was built last and graded against it.
mkdir -p "$P/work" && cp "$W/bg.mp4" "$P/work/bg.mp4"

echo "avatar windows"
.venv-tools/bin/python tools/avatar_windows.py "$W/bg.mp4" "$P/windows_part1.json" "$AUD"

echo "compositing"
.venv-tools/bin/python tools/composite.py "$W/bg.mp4" "$HG" "$KEY" "$W/keyed.mp4" \
  "$P/windows_part1.json" - "$P/clips_part1.json" - - "$P/card_part1.json"

echo "sound"
ffmpeg -v error -i "$W/keyed.mp4" -i "$HG" -map 0:v -map 1:a \
  -c:v copy -c:a aac -b:a 192k -ar 48000 -ac 2 -shortest \
  -movflags +faststart "$OUT" -y
cp "$W/keyed.mp4.geom.json" "$OUT.geom.json"

echo
.venv-manim/bin/python tools/gates.py che-c1-sa-02 "$OUT"
