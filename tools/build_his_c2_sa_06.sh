#!/usr/bin/env bash
# HIS-C2-SA-06 — assemble the eleven segments.
#
# Five carry a Veo clip and its own generated dialogue; six are a data screen
# with the HeyGen presenter keyed in below it and HeyGen's audio.
#
# SYNC. Every segment takes its picture and its sound from ONE source and one
# time range, so nothing can drift: a Veo segment is the clip's own video and
# the clip's own audio, and a screen segment is the map/card plus the HeyGen
# video AND HeyGen audio cut from the same [start, start+dur]. Nothing is
# dubbed. Laying HeyGen's block 1 under Veo clip 1 was tried and dropped —
# two recordings of one line at different speeds cannot be lip-synced.
#
# The Veo clips are 10s but speak for 6 to 7.5 of it; each is cut to its own
# speech with a short head and tail, which removed 8.8s of dead air.
#
# WHY VIDEO AND AUDIO ARE ASSEMBLED SEPARATELY. Encoding each segment to AAC and
# concatenating with -c copy drifts: every AAC stream carries 1024 samples of
# encoder priming and is padded up to a frame boundary, and across eleven
# segments that accumulated to +395ms by the close — measured, segment 1 was off
# by exactly 1024 samples. So each segment writes a video-only MP4 and a PCM
# WAV; the WAVs concatenate sample-exactly and the whole track is encoded to AAC
# ONCE at the mux. Re-run the alignment check after touching this.
#
# And each WAV is cut to the segment's OWN frame count, not to the duration that
# was asked for. A video segment rounds up to a whole frame at 30fps and its
# audio does not, so the audio ran short by up to 33ms per segment — 0.36s over
# eleven, drifting the other way. `wav_for` measures the rendered video and pads
# or trims the sound to match it exactly.
set -euo pipefail
cd "$(dirname "$0")/.."
HG=inbox/his-c2-sa-06/heygen_full.mp4
CARD=projects/his-c2-sa-06/manim_code/media/videos/pyq_composed/1920p30/card_his.mp4
W=/tmp/his_build
OUT=projects/his-c2-sa-06/final
mkdir -p "$W" "$OUT"
# a stale wav from an earlier run must not stand in for one that failed
rm -f "$W"/seg*.wav
[ -f "$CARD" ] || { echo "!! question card not rendered: $CARD"; exit 1; }

# The presenter, measured off this take: head top 170 at its highest, head
# centre x 933 of the 1920x1080 plate. Scaled so his head lands at y 1060 of
# the 1080x1920 frame, clearing the map window (bottom 980) by 80px.
KEY="format=yuva420p,chromakey=0xA1EC32:0.14:0.10,despill=type=green:mix=0.55:expand=0,\
split[k1][k2];[k2]alphaextract,boxblur=1.0:1[am];[k1][am]alphamerge,\
scale=1815:1021,setsar=1,fps=30[fg];[0:v][fg]overlay=x=-342:y=899:format=auto[v]"

# THE CARD IS A DIFFERENT LAYOUT. It owns the whole frame by design and its
# years pill runs down to y 1347, which the placement above covers completely.
# The shipped science videos put him smaller and lower under the card for the
# same reason (measured there: head top ~1374). Nothing compares the two on
# screen — segment 3 is bracketed by Veo clips, not by other keyed segments.
KEYCARD="format=yuva420p,chromakey=0xA1EC32:0.14:0.10,despill=type=green:mix=0.55:expand=0,\
split[k1][k2];[k2]alphaextract,boxblur=1.0:1[am];[k1][am]alphamerge,\
scale=1139:641,setsar=1,fps=30[fg];[0:v][fg]overlay=x=-14:y=1279:format=auto[v]"

# the sound for a segment, exactly as long as that segment's video
wav_for () {           # $1 seg  $2 src  $3 start
  local frames dur
  # csv=p=0 can come back as "296," — strip anything that is not a digit, or
  # bc gets "296," and the whole -t argument comes out empty.
  frames=$(ffprobe -v error -count_frames -select_streams v:0 \
           -show_entries stream=nb_read_frames -of csv=p=0 "$W/seg$1.mp4" \
           | tr -dc '0-9')
  [ -n "$frames" ] || { echo "!! could not count frames for seg$1"; exit 1; }
  dur=$(echo "scale=6; $frames / 30" | bc)
  ffmpeg -v error -ss "$3" -i "$2" -vn -af apad -t "$dur" \
    -ac 2 -ar 48000 -c:a pcm_s16le "$W/seg$1.wav" -y
  echo "$frames"
}

screen () {            # $1 seg  $2 picture  $3 hg_start  $4 dur  $5 filter
  ffmpeg -v error -i "$2" -ss "$3" -t "$4" -i "$HG" \
    -filter_complex "[1:v]${5}" -map "[v]" -an -t "$4" \
    -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -r 30 "$W/seg$1.mp4" -y
  local f; f=$(wav_for "$1" "$HG" "$3")
  printf "  seg%-3s %-32s %6.2fs  %4s frames   HeyGen %6.2f-%6.2f\n" \
    "$1" "$(basename "$2")" "$4" "$f" "$3" "$(echo "$3 + $4" | bc)"
}
veo () {               # $1 seg  $2 clip  $3 in  $4 dur
  ffmpeg -v error -ss "$3" -t "$4" -i "$2" \
    -vf "scale=1080:1920:flags=lanczos,setsar=1,fps=30" -an \
    -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -r 30 "$W/seg$1.mp4" -y
  local f; f=$(wav_for "$1" "$2" "$3")
  printf "  seg%-3s %-32s %6.2fs  %4s frames   clip   %6.2f-%6.2f\n" \
    "$1" "$(basename "$2")" "$4" "$f" "$3" "$(echo "$3 + $4" | bc)"
}

echo "segments:"
veo    01 "$W/veo1_clean.mp4"  0.47 7.96
# SEGMENT 2 SAYS "हज़ार" TWICE. Veo generated the phrase, then generated it
# again: clip audio [3.80,4.50] matches [4.54,5.24] at a DTW distance of 0.025
# where unrelated speech in the same clip scores 0.16 to 0.21. The first copy is
# cut out and the join is a 0.24s cross dissolve — the two copies are nearly
# identical, so the blend is inaudible. Removing 0.74s here is the one place a
# transition is ALLOWED to change duration; everything downstream is measured
# from the rendered segments, so the shift carries through on its own.
veo2_cut () {
  local IN=0.31 OUT=8.65 C0=3.80 C1=4.54 D=0.24
  local aEnd bStart offset
  aEnd=$(echo "scale=4; $C0 + $D/2" | bc)          # 3.92
  bStart=$(echo "scale=4; $C1 - $D/2" | bc)        # 4.42
  offset=$(echo "scale=4; $aEnd - $IN - $D" | bc)  # 3.3700
  ffmpeg -v error \
    -ss "$IN"     -to "$aEnd" -i "$W/veo2_clean.mp4" \
    -ss "$bStart" -to "$OUT"  -i "$W/veo2_clean.mp4" \
    -filter_complex \
      "[0:v]scale=1080:1920:flags=lanczos,setsar=1,fps=30[v0];\
       [1:v]scale=1080:1920:flags=lanczos,setsar=1,fps=30[v1];\
       [v0][v1]xfade=transition=fade:duration=$D:offset=$offset[v];\
       [0:a][1:a]acrossfade=d=$D:c1=tri:c2=tri[a]" \
    -map "[v]" -map "[a]" \
    -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -r 30 \
    -c:a pcm_s16le -ar 48000 -ac 2 "$W/seg02_full.mov" -y
  ffmpeg -v error -i "$W/seg02_full.mov" -an -c:v copy "$W/seg02.mp4" -y
  # match the sound to the segment's own frame count, exactly as wav_for does
  # for every other segment — the crossfade output does not land on a frame.
  local fr d
  fr=$(ffprobe -v error -count_frames -select_streams v:0 \
       -show_entries stream=nb_read_frames -of csv=p=0 "$W/seg02.mp4" | tr -dc '0-9')
  d=$(echo "scale=6; $fr / 30" | bc)
  ffmpeg -v error -i "$W/seg02_full.mov" -vn -af apad -t "$d" \
    -c:a pcm_s16le -ar 48000 -ac 2 "$W/seg02.wav" -y
  printf "  seg%-3s %-32s %6.2fs  %4s frames   clip   %6.2f-%6.2f  (repeat cut)\n" \
    "02" "veo2_clean.mp4" "$(echo "scale=2; 8.34 - 0.74" | bc)" \
    "$(ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames \
       -of csv=p=0 "$W/seg02.mp4" | tr -dc '0-9')" "$IN" "$OUT"
}
veo2_cut
screen 03 "$CARD"                                        14.60  9.30 "$KEYCARD"
veo    04 "$W/veo3_clean.mp4"  0.63 8.42
screen 05 map_engine/output/his_c2_m1_relief.mp4     40.45  9.85 "$KEY"
veo    06 "$W/veo4_clean.mp4"  0.55 6.80
screen 07 map_engine/output/his_c2_m2_relief.mp4   55.70 20.70 "$KEY"
veo    08 "$W/veo5_clean.mp4"  0.77 7.02
screen 09 map_engine/output/his_c2_m3_relief.mp4        83.90 15.10 "$KEY"
screen 10 map_engine/output/his_c2_s10_method.mp4         99.00 13.90 "$KEY"
screen 11 map_engine/output/his_c2_s11_close.mp4         112.90  5.12 "$KEY"

# THE CLOSE FADES TO DARK. Without it the last frame is wherever the presenter's
# hands happened to be when the take ran out, which reads as the video being cut
# off rather than ended. The fade lives inside segment 11's own frames, so it
# costs no time; the black tail is a new segment with matching silence.
ffmpeg -v error -i "$W/seg11.mp4" -vf "fade=t=out:st=4.10:d=0.80" -an   -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -r 30 "$W/seg11f.mp4" -y
mv "$W/seg11f.mp4" "$W/seg11.mp4"
# THE TAIL IS SEGMENT 11'S OWN LAST FRAME, HELD — not a lavfi black. A
# `color=black` source carries a different colour range from the rest of the
# chain, so in the finished file its Y read 16 where the end of the fade read
# 5: the screen visibly LIFTS at the very end, which is the opposite of landing
# on dark. Cloning the last frame cannot drift from what precedes it.
ffmpeg -v error -i "$W/seg11.mp4" -vf "tpad=stop_mode=clone:stop_duration=0.8,fps=30" -an -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -r 30 "$W/seg11p.mp4" -y
ffmpeg -v error -sseof -0.8 -i "$W/seg11p.mp4" -an -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -r 30 "$W/seg12.mp4" -y
rm -f "$W/seg11p.mp4"
ffmpeg -v error -f lavfi -i anullsrc=r=48000:cl=stereo -t 0.8   -c:a pcm_s16le "$W/seg12.wav" -y
printf "  seg%-3s %-32s %6.2fs  %4s frames   fade to dark, then black\n" "12" "(black)" 0.80 24

: > "$W/list.txt"; : > "$W/alist.txt"
for i in 01 02 03 04 05 06 07 08 09 10 11 12; do
  echo "file '$W/seg$i.mp4'" >> "$W/list.txt"
  echo "file '$W/seg$i.wav'" >> "$W/alist.txt"
done
ffmpeg -v error -f concat -safe 0 -i "$W/list.txt"  -c copy -an "$W/video.mp4" -y
ffmpeg -v error -f concat -safe 0 -i "$W/alist.txt" -c copy      "$W/audio.wav" -y
echo
printf "  video %ss   audio %ss\n" \
  "$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$W/video.mp4")" \
  "$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$W/audio.wav")"
ffmpeg -v error -i "$W/video.mp4" -i "$W/audio.wav" \
  -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -ar 48000 -ac 2 \
  -movflags +faststart "$OUT/his_c2_sa_06.mp4" -y
echo
echo "-> $OUT/his_c2_sa_06.mp4  $(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT/his_c2_sa_06.mp4")s"


# NOTHING SHIPS WITHOUT THE GATES. See tools/gates.py for why this is the
# last line of the build rather than a thing to remember afterwards.
.venv-manim/bin/python tools/gates.py his-c2-sa-06 "$OUT/his_c2_sa_06.mp4"
