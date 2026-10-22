#!/bin/bash
# Side job: fetch pending Veo clips for several projects, optionally submit new prompts first.
#   bash lab/kit_test/veo_side.sh "<project> ..." "<prompt files to submit>"
cd "$(dirname "$0")/../.."
PROJS=$1; SUBMIT=${2:-}
L=lab/kit_test/out/veo_side.log
fetch_all() {
  for P in $PROJS; do D=projects/$P/veo; T=$D/_fetch; rm -rf $T; mkdir -p $T
    for f in $D/prompts/broll/*.txt; do b=$(basename $f .txt); [ -f $D/clips/$b.mp4 ] || cp $f $T/; done
    [ "$(ls $T | wc -l | tr -d ' ')" = "0" ] && continue
    .venv-tools/bin/python -u veo_kit/fetch.py --prompts $T --out $D/clips --aspect vertical --max 24 >> $L.fetch 2>&1
  done
}
missing() { n=0; for P in $PROJS; do D=projects/$P/veo; for f in $D/prompts/broll/*.txt; do b=$(basename $f .txt); [ -f $D/clips/$b.mp4 ] || n=$((n+1)); done; done; echo $n; }
echo "start: $(missing) clips missing" >> $L
fetch_all; echo "after first fetch: $(missing) missing" >> $L
if [ -n "$SUBMIT" ]; then sleep 20; .venv-tools/bin/python -u veo_kit/submit.py $SUBMIT --aspect vertical --no-refs >> $L.submit 2>&1; echo "submitted; rendering: $(grep -c 'rendering [0-9]' $L.submit)" >> $L; fi
for r in 1 2 3 4 5 6 7 8 9 10; do [ "$(missing)" = "0" ] && break; sleep 150; fetch_all; echo "round $r: $(missing) missing" >> $L; done
echo "DONE: $(missing) missing" >> $L
