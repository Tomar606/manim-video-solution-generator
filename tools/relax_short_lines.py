#!/usr/bin/env python3
"""Give a caption that is too short to READ the silence that follows it.

    python tools/relax_short_lines.py <lines.json> [--gap 0.06] [--rate 4.5]

A caption needs about `rate` words per second to be read. Some are spoken
faster than that — BIO-C5-LA-01 part 1 says "size के हिसाब से अलग किया", six
words, in 1.14s — and a caption that leaves before it can be read is a defect
even though its timing is perfectly correct.

The fix is not to start it early, which would put it over the previous
sentence, and not to shorten the words. It is to let it run INTO the pause that
follows, if there is one. That silence belongs to nobody: the speaker has
stopped and the next caption has not started. Extending into it costs nothing
and never moves a boundary that was measured.

Two things it will not do:
  * take time from the next caption — it stops `gap` short of that start;
  * invent time where there is no pause. A caption still too short afterwards
    is REPORTED, because the honest answer there is to merge it with its
    neighbour, and that is an editorial decision rather than a mechanical one.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("lines"); ap.add_argument("--gap", type=float, default=0.06)
    ap.add_argument("--rate", type=float, default=4.5)
    ap.add_argument("--floor", type=float, default=1.05)
    ap.add_argument("--lead", type=float, default=0.0,
                    help="seconds a still-short caption may start EARLY into "
                         "the silence before it (never into the previous "
                         "caption). A subtitle that leads is invisible; one "
                         "that lags is the defect this exists to prevent.")
    ap.add_argument("--merge", action="store_true",
                    help="merge a still-short caption into the one before it, "
                         "and print the old->new index map for anchors.json")
    a = ap.parse_args()
    p = Path(a.lines)
    L = json.loads(p.read_text(encoding="utf-8"))

    moved, stuck, led = [], [], []
    for i, l in enumerate(L):
        need = max(a.floor, len(l["text"].split()) / a.rate)
        have = l["end"] - l["start"]
        if have >= need:
            continue
        room = (L[i + 1]["start"] - a.gap) if i + 1 < len(L) else l["end"]
        # a hair of margin: padding to EXACTLY the floor leaves the caption
        # one rounding step away from failing the same check it just passed
        new_end = min(l["start"] + need + 0.05, room)
        if new_end > l["end"] + 1e-6:
            moved.append((i, have, new_end - l["start"]))
            l["end"] = round(new_end, 3)
        # STILL SHORT? BORROW FROM THE SILENCE IN FRONT OF IT.
        # A subtitle may LEAD the voice by a moment and nobody notices; one
        # that lags is the defect BIO-C12-LA-02 shipped. So when the pause
        # after a caption is not enough, the pause BEFORE it is offered next,
        # up to `lead` seconds and never back into the previous caption. The
        # words are not being spoken yet at that point, which is exactly why
        # it is capped small rather than taken freely.
        if a.lead > 0 and l["end"] - l["start"] < need - 2e-3:
            floor_s = (L[i - 1]["end"] + a.gap) if i > 0 else 0.0
            want = l["end"] - need - 0.05
            new_start = max(floor_s, want, l["start"] - a.lead)
            if new_start < l["start"] - 1e-6:
                led.append((i, l["start"], new_start))
                l["start"] = round(new_start, 3)
        if l["end"] - l["start"] < need - 2e-3:      # 3dp rounding, not a real miss
            stuck.append((i, l["end"] - l["start"], need, l["text"]))

    remap = None
    if a.merge and stuck:
        # A caption with no pause to borrow is merged BACKWARDS: it joins the
        # sentence it belongs to, which is almost always the one before it
        # ("अब चलते हैं अगले step पर," + "जो है संकरण।"). Merging forwards would
        # start the caption before its own first word.
        drop = {i for i, *_ in stuck if i > 0}
        out, remap, k = [], {}, 0
        for i, l in enumerate(L):
            if i in drop and out:
                out[-1]["text"] = out[-1]["text"].rstrip() + " " + l["text"].lstrip()
                out[-1]["end"] = l["end"]
                remap[i] = k - 1
                continue
            out.append(l); remap[i] = k; k += 1
        L = out
        stuck = [(i, e, n, t) for i, e, n, t in stuck if i == 0]

    p.write_text(json.dumps(L, ensure_ascii=False, indent=1), encoding="utf-8")
    for i, was, now in led:
        print(f"  line {i:3d}: started {was - now:.2f}s earlier, into the pause "
              f"before it")
    if remap:
        print(f"  merged {len(remap) - max(remap.values()) - 1} caption(s); "
              f"line index map (old -> new):")
        print("     " + ", ".join(f"{o}->{n}" for o, n in remap.items()
                                  if o != n or o in {i for i, *_ in stuck}) [:400])
        Path(str(p) + ".remap.json").write_text(json.dumps(remap), encoding="utf-8")
    print(f"  {p.name}: {len(moved)} caption(s) given the pause after them")
    for i, was, now in moved:
        print(f"     line {i:3d}  {was:.2f}s -> {now:.2f}s")
    if stuck:
        print(f"  {len(stuck)} still short — no pause to borrow; merge by hand:")
        for i, have, need, t in stuck:
            print(f"     line {i:3d}  {have:.2f}s < {need:.2f}s  {t[:40]!r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
