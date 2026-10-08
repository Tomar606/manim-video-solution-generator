#!/usr/bin/env bash
# PHY-C1-SA-01 — विद्युत् फ्लक्स.
#
# Card + Manim body + the HOUSE compositor + the take's own audio + the gates.
#
# USE tools/composite.py, NOT A HAND-ROLLED OVERLAY. Its key is hue-based and
# applied twice; an RGB-distance key wide enough for the screen's dark side also
# matches skin and holes the face — measured on the first cut of this video as a
# matte alpha of 216.9 instead of 255, which read as washed-out skin. It also
# sizes the presenter itself (CARD_W while the card is up, FULL_W after) and
# writes the geometry sidecar the output gate needs.
#
# CAPTION TIMINGS ARE NOT FROM THE DELIVERED SRT. Checked word by word against
# the audio, that SRT is out by up to 1.37s in BOTH directions, so it cannot be
# nudged into place either. lines_part1.json is rebuilt from the transcription;
# the original is kept as lines_srt_original.json.
set -euo pipefail
cd "$(dirname "$0")/.."
P=projects/phy-c1-sa-01
HG=inbox/phy-c1-sa-01/heygen_full.mp4
CARD=$P/manim_code/media/videos/pyq_composed/1920p30/card1.mp4
BODY=$P/manim_code/media/videos/flux_composed/1920p30/flux_v5.mp4
KEY=$P/keys/key_part1.json
OUT=$P/final/phy_c1_sa_01.mp4
W=/tmp/phy_build; mkdir -p "$W" "$P/final"
CARD_END=8.50        # line 3 "तो चलो पहले समझते हैं" begins here, measured

for f in "$CARD" "$BODY" "$HG" "$KEY"; do
  [ -f "$f" ] || { echo "!! missing $f"; exit 1; }
done

echo "background"
ffmpeg -v error -t $CARD_END -i "$CARD" -an -c:v libx264 -preset medium -crf 18 \
  -pix_fmt yuv420p -r 30 "$W/a.mp4" -y
ffmpeg -v error -ss $CARD_END -i "$BODY" -an -c:v libx264 -preset medium -crf 18 \
  -pix_fmt yuv420p -r 30 "$W/b.mp4" -y
printf "file '%s/a.mp4'\nfile '%s/b.mp4'\n" "$W" "$W" > "$W/bg.txt"
ffmpeg -v error -f concat -safe 0 -i "$W/bg.txt" -c copy "$W/bg.mp4" -y
# THE GATES NEED THIS VIDEO'S OWN BACKGROUND. gates.py used to hunt
# /tmp/<subject>_build/bg.mp4, so every chemistry slug found whichever
# chemistry video was built last and graded against it.
mkdir -p "$P/work" && cp "$W/bg.mp4" "$P/work/bg.mp4"

# where content sits behind him, HE moves — not the content
.venv-tools/bin/python tools/avatar_windows.py "$W/bg.mp4" "$P/windows_part1.json" \
  "$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$HG")"

echo "compositing"
.venv-tools/bin/python tools/composite.py "$W/bg.mp4" "$HG" "$KEY" "$W/keyed.mp4" \
  "$P/windows_part1.json" - - - - "$P/card_part1.json"

echo "sound"
ffmpeg -v error -i "$W/keyed.mp4" -i "$HG" -map 0:v -map 1:a \
  -c:v copy -c:a aac -b:a 192k -ar 48000 -ac 2 -shortest \
  -movflags +faststart "$OUT" -y
# the output gate reads this; without it the gate cannot verify placement
cp "$W/keyed.mp4.geom.json" "$OUT.geom.json"

echo "answer page"
# THE SHEET'S ANSWER IMAGE, WATERMARKED. No reviewed house page exists for this
# question — not in EndScreenshot.zip, not in inbox/answers/house — so the page
# is the sheet's own image (column 11), which is the textbook scan. It carries
# no Arivihan mark of its own; EndScreenshot/watermark.py stamps it, flattened
# onto white first so the scan's transparent margin does not show the plate
# through the paper. Named here, not passed by hand, so a rebuild cannot pick a
# different page.
# The page is LANDSCAPE (a textbook scan, 1640x934 after upscaling) and
# answer_outro expects a portrait 2:3 page: handed this one it padded it into a
# portrait page itself, crammed the answer into the top 40%, and stretched the
# scan's edge column into a smeared stripe down the middle of the frame. So the
# end frame is composed ahead of time at exactly 1080x1920 — the watermarked
# card centred full-width on the video's own plate — and the outro's fit is then
# a no-op.
ANSWER=$P/assets/answer/PHY-C1-SA-01_end_frame.png
[ -f "$ANSWER" ] || { echo "!! missing $ANSWER"; exit 1; }
.venv-tools/bin/python tools/answer_outro.py "$OUT" "$ANSWER" "$W/with_answer.mp4" --hold 7
mv "$W/with_answer.mp4" "$OUT"
# the gates compare this background against the final, so it gets the same page
# on the end — otherwise the durations differ and avatar_cover_gate refuses to
# grade the pair at all
# bg.mp4 carries no audio, and answer_outro maps one — so it gets a silent track
# first, or the outro fails on "stream specifier ':a' matches no streams".
ffmpeg -v error -i "$P/work/bg.mp4" -f lavfi -i anullsrc=r=48000:cl=stereo \
  -shortest -c:v copy -c:a aac "$W/bg_sil.mp4" -y
.venv-tools/bin/python tools/answer_outro.py "$W/bg_sil.mp4" "$ANSWER" "$W/bg_answer.mp4" --hold 7
mv "$W/bg_answer.mp4" "$P/work/bg.mp4"

echo
.venv-manim/bin/python tools/gates.py phy-c1-sa-01 "$OUT"
