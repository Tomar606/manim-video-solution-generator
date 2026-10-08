"""Find the dead air at each end of a reel's clips, and say what cutting it saves.

    python tools/reel_trim.py <slug>            # propose, change nothing
    python tools/reel_trim.py <slug> --write    # write the trims into reel.json

A Veo clip is always 10.01s whatever the line needs, so the difference turns up
as silence at one end or the other — measured across POL-C1-LA-01, a lead-in of
up to 2.4s before he says anything.

WHAT IS CUT, AND WHAT IS NOT
----------------------------
Only silence, and not all of it. Two handles are kept on purpose:

  HEAD_KEEP  before the first word, because the head of a clip is where the
             shot establishes — he walks up to camera, the crowd comes into
             view, the flag goes up. Cutting to the first syllable throws that
             away and the scene starts on a face with no place behind it.
  TAIL_KEEP  after the last word, because he is still finishing the gesture,
             and a cut on the closing consonant reads as the clip running out
             rather than ending.

So a clip is only shortened where the silence is LONGER than its handle, and
never by more than MAX_CUT at either end — past that the shot is doing
something, whatever the audio says, and it is a judgement to make by eye rather
than a rule to apply.

Nothing here touches the transitions: they borrow frames from either side of a
join, and a trim is applied before that, so the bridge still has frames to take.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# THE HANDLE DEPENDS ON THE SHOT, and this is the fix for the complaint that
# the Nepal cut felt abrupt. 0.55s was applied to every clip, and measured
# across that video it left exactly 0.55s of a silent man standing there at 12
# of 20 cuts — so the grammar at every join was: voice stops, picture changes,
# pause, new voice. The edit was audible before anything motivated it.
#
# The reasoning behind 0.55 is still right for a shot that has to ESTABLISH —
# he walks up, the crowd comes into view. It is wrong for a man already framed
# and about to speak, which is what nearly every clip on this route is. So a
# piece to camera gets a few frames and an establishing shot keeps its beat.
HEAD_KEEP = 0.12        # seconds of picture kept before the first word
HEAD_KEEP_ESTABLISH = 0.55      # for a shot that has to arrive somewhere first
# THE GAP A VIEWER HEARS IS HEAD + TAIL, across the join. With the head at
# 0.12s a 0.65s tail still leaves about three quarters of a second of nobody
# speaking at every cut, which is the pause being complained about. 0.30s is
# enough to let a closing gesture finish without the clip hanging.
TAIL_KEEP = 0.30        # and after the last
MAX_CUT = 2.60          # never take more than this off one end
MIN_GAIN = 0.25         # ignore a saving smaller than this; not worth a re-encode


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--head-keep", type=float, default=HEAD_KEEP)
    ap.add_argument("--tail-keep", type=float, default=TAIL_KEEP)
    a = ap.parse_args()

    proj = ROOT / "projects" / a.slug
    rj = proj / "reel.json"
    spec = json.loads(rj.read_text(encoding="utf-8"))
    wj = proj / "work" / "words.json"
    if not wj.is_file():
        print(f"  no word timings yet — run tools/reel_words.py {a.slug} first")
        return 1
    words = json.loads(wj.read_text(encoding="utf-8"))

    total_before = total_after = 0.0
    rows = []
    for s in spec["scenes"]:
        sid = s["id"]
        rec = words.get(sid)
        if not rec or not rec["words"]:
            rows.append((sid, None, None, 0.0, "no words heard — left whole"))
            continue
        dur = float(rec["dur"])
        first = float(rec["words"][0]["s"])
        last = float(rec["words"][-1]["e"])
        # A scene that has to arrive somewhere keeps its establishing beat; a
        # piece to camera does not (see HEAD_KEEP above). `establish: true` in
        # reel.json marks the first kind.
        keep = HEAD_KEEP_ESTABLISH if s.get("establish") else a.head_keep
        head = max(0.0, min(first - keep, MAX_CUT))
        tail = max(0.0, min(dur - last - a.tail_keep, MAX_CUT))
        head = head if head >= MIN_GAIN else 0.0
        tail = tail if tail >= MIN_GAIN else 0.0
        kept = dur - head - tail
        total_before += dur
        total_after += kept
        why = []
        if head:
            why.append(f"head -{head:.2f}s (silent to {first:.2f}s)")
        if tail:
            why.append(f"tail -{tail:.2f}s (silent from {last:.2f}s)")
        rows.append((sid, head, tail, kept, ", ".join(why) or "nothing to take"))
        if a.write:
            if head or tail:
                s["trim"] = [round(head, 2), round(tail, 2)]
            else:
                s.pop("trim", None)

    for sid, head, tail, kept, why in rows:
        print(f"  {sid}  {kept:5.2f}s   {why}")
    saved = total_before - total_after
    print(f"\n  {total_before:.1f}s -> {total_after:.1f}s   saves {saved:.1f}s "
          f"({saved / max(1, total_before):.0%})")
    if a.write:
        rj.write_text(json.dumps(spec, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"  written into {rj.relative_to(ROOT)}")
    else:
        print("  nothing written — re-run with --write to keep these")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
