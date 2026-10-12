#!/bin/zsh
# Assemble one part of an arts reel, start to finish, and say how long each step took.
#
#     nohup caffeinate -i tools/reel/run_part.sh <slug> <part> [layers] > work/<slug>/out/run_p<N>.log 2>&1 &
#
# Start it DETACHED (as above): on GEO-C2-LA-01 the assembly ran as a session
# task, the session died at 04:55 and nothing ran for four hours.
#
# Steps, each skipped when its output is newer than its inputs is NOT attempted:
# this always rebuilds what it is asked for. `layers` also redraws the three
# drawn layers from work/<slug>/design/part<N>.mjs first (and its cue list, and
# the sound mix that depends on the cues).
set -e
cd "${0:A:h}/../.."
slug=$1; n=$2; what=$3
W=work/$slug
step() { print -- "$(date +%H:%M:%S) $*"; }
free() { df -m . | tail -1 | awk '{print $4}'; }
[[ $(free) -lt 250 ]] && { step "STOP: only $(free) MB free on the disk"; exit 3; }

if [[ $what == layers ]]; then
  step "layers p$n"; node $W/design/part$n.mjs
  step "cues p$n";   node $W/design/part$n.mjs --cues
  step "sound p$n";  python3 tools/reel/audio.py $slug $n
fi
# the mix is stale when it is missing or older than the cue list it is built from
if [[ ! -f $W/out/audio/p$n.wav || $W/out/cues_p$n.json -nt $W/out/audio/p$n.wav ]]; then
  step "sound p$n"; python3 tools/reel/audio.py $slug $n
fi
[[ -f $W/out/layers/p$n/captions.mov ]] || { step "captions p$n"; node tools/reel/captions_line.mjs $slug $n; }
step "edit list p$n";  python3 tools/reel/edit_from_scenes.py $slug $n
step "background p$n"; ALLOW_LOW=1 python3 tools/reel/build_part.py $W/edit_part$n.json bg
[[ $(free) -lt 200 ]] && { step "STOP: only $(free) MB free on the disk"; exit 3; }
step "composite p$n";  ALLOW_LOW=1 python3 tools/reel/build_part.py $W/edit_part$n.json comp
step "sheet p$n";      python3 tools/reel/build_part.py $W/edit_part$n.json sheet
rm -f $W/out/bg_part$n.mp4          # an intermediate; two minutes to rebuild, and the disk is the scarce thing
step "done p$n: $(ls -la $W/out/part$n.mp4 | awk '{print $5/1e6 " MB"}'), $(free) MB free"
