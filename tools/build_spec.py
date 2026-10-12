#!/usr/bin/env python3
"""Lay a video's designed beats onto its MEASURED caption clock.

    python tools/build_spec.py <slug> <part> <clip_seconds>

Reads   work/<slug>/spec/anchors.json    which beat owns which caption lines
        work/<slug>/spec/design.json     the beats themselves (design payloads)
        work/<slug>/out/lines_part<N>.json  the measured caption track
Writes  work/<slug>/spec/segments_part<N>.json

WHY THIS IS A TOOL AND NOT A SCRIPT INSIDE THE VIDEO FOLDER
-----------------------------------------------------------
Five copies of `build_spec.py` exist under `work/`, each with one video's beat
table baked into it, which is why PROCESS.md marks it as a tool that goes
missing. The timing machinery here never changes; the beat table is data
(`anchors.json` + the payloads) and lives with the video.

THE THREE RULES THIS ENFORCES
-----------------------------
1. A SEGMENT MAY ONLY START WHERE A CAPTION STARTS. Every boundary below is a
   measured word onset, because it is a line's own start time. Nothing rounds,
   nothing is chosen.

2. SEGMENTS SUM TO THE CLIP. Lines no beat claims still become segments — quiet
   ones, presenter and captions only. BIO-C5-LA-01 previously planned 143.5s of
   262.6s and the missing 119s was invisible until someone added it up.

3. A CAPTION KEEPS ITS OWN END. `t_out` is the line's measured end, never
   "the next line's start minus a constant" — deriving it that way cut 0.2s off
   every caption in an earlier build and read as the captions running ahead of
   the voice.

WORD ANCHORS
------------
A timeline step, a label (`wi` in, `out_wi` out), a list item or a block/veo
entry may carry `wi`: an index into out/words_part<N>.json, plus optional `dt`.
It then lands on that word's MEASURED onset — the runbook's ideal, exact rather
than approximated. The word must be inside the beat's own lines (their `w`
ranges, written by tools/lines_from_edit.py), or the build stops.

Anything without an anchor is rescaled PROPORTIONALLY from the beat's designed
duration onto its real one, and a counted list without one lands item k on the
k-th caption of the beat. Both are compromises; prefer `wi`.

Every shape and label a beat shows is cleared at `end − 0.24` over 0.22s unless
the beat says `"clear": false` (a diagram carried into the next segment).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


MIN_BIG = 4.0        # seconds; below this the frame keeps its busy layout
MIN_ISLAND = 6.0     # seconds; a quiet patch with content on BOTH sides has to
                     # be at least this long to be worth changing the frame for


def first_is_card(n: int, has_card: bool) -> bool:
    """Segment 1 is under the question card, which is opaque to y=1344.

    Both caption positions are hidden behind it, so the choice is
    invisible — but the presenter must stay CARD-sized there, and
    marking it quiet would ask composite.py to grow him under the card.

    ONLY when the part actually opens on a card. This returned a bare
    `n == 1` and BIO-C5-LA-01 part 2, which carries the question forward
    instead of restating it, spent its first 11.5 seconds — quiet, nothing
    on the stage — with the caption low and the presenter at full size
    across it: 44% of the glyph pixels painted over. The exact defect the
    two-state layout exists to prevent, reintroduced by assuming every part
    opens the way part 1 does.
    """
    return has_card and n == 1


def rel(t: float, seg_start: float) -> float:
    return round(t - seg_start, 3)


def build(slug: str, part: int, clip_end: float, has_card: bool,
          suppress_on_graphics: bool = False,
          card_last: int | None = None) -> dict:
    root = Path("work") / slug
    lines = json.loads((root / "out" / f"lines_part{part}.json").read_text(encoding="utf-8"))
    anchors = json.loads((root / "spec" / "anchors.json").read_text(encoding="utf-8"))[f"part{part}"]
    # The DESIGN lives in design.json. segments.json is generated, and is what
    # the renderer loads — keeping the two apart is why overwriting one cannot
    # destroy the other.
    design = {s["type"]: s for s in
              json.loads((root / "spec" / "design.json").read_text(encoding="utf-8"))}
    wf = root / "out" / f"words_part{part}.json"
    words = json.loads(wf.read_text(encoding="utf-8")) if wf.is_file() else None
    anchors_log: list[str] = []

    # --- boundaries: every beat edge, plus the ends of the part ---------------
    owner: dict[int, str] = {}
    for name, (i, j) in anchors.items():
        for k in range(i, j + 1):
            if k in owner:
                raise SystemExit(f"line {k} claimed by both {owner[k]} and {name}")
            owner[k] = name

    runs: list[tuple[str | None, list[int]]] = []
    for k in range(len(lines)):
        who = owner.get(k)
        if runs and runs[-1][0] == who:
            runs[-1][1].append(k)
        else:
            runs.append((who, [k]))

    # THE CARD COVERS LINES, NOT THE WHOLE FIRST RUN.
    #
    # `first_is_card` marks segment 1 as card-covered: caption low, presenter
    # held small. That is right for exactly as long as the card is up. When the
    # first beat comes late the first run is long — BIO-C2-LA-01 part 1 has no
    # beat until line 10, so segment 1 ran 0-32.62s while the card left at
    # 12.3s — and for the twenty seconds after the card the presenter stood at
    # working size with his head at 51% of frame and the caption sitting at the
    # LOW position behind it. His hair cut straight through the text at t=20,
    # 26 and 31. The same defect first_is_card's own comment records on
    # BIO-C5-LA-01 part 2, reintroduced from the other direction.
    #
    # So when the card's last line is known, the first run is SPLIT there: the
    # lines under the card stay a card segment, and the rest become an ordinary
    # quiet run that gets the top caption and the grown presenter like any
    # other. `card_last` is a line INDEX (meta.json `card_lines`), and the
    # card's own window in card_part<N>.json should end where that line ends so
    # the one eased size change happens at the segment boundary.
    if has_card and card_last is not None and runs and runs[0][0] is None:
        head = runs[0][1]
        if card_last + 1 < len(head):
            under, after = head[:card_last + 1], head[card_last + 1:]
            runs[0] = (None, under)
            runs.insert(1, (None, after))
            print(f"     card covers lines 0-{card_last}; lines {after[0]}-{after[-1]} "
                  f"split off as a quiet segment (caption high, presenter big)")

    segs, under_card = [], []
    for n, (who, idx) in enumerate(runs, 1):
        s_start = lines[idx[0]]["start"]
        s_end = lines[idx[-1]]["end"] if idx[-1] + 1 == len(lines) else lines[idx[-1] + 1]["start"]
        if n == 1:
            s_start = 0.0                      # the part starts at frame 0
        if idx[-1] + 1 == len(lines):
            s_end = clip_end                   # and runs to the very end
        dur = round(s_end - s_start, 3)

        # `voiceover` is what he ACTUALLY says across this segment — the
        # captions joined. validate.py needs the field for its words/sec
        # warning, which the runbook rightly calls meaningless when the audio
        # already exists; supplying the real text keeps every other check in
        # that file working rather than stubbing one out to get past it.
        # A quiet segment puts its caption at the TOP and lets the presenter
        # grow into the empty frame; a busy one keeps the caption low, under
        # the stage. MIN_BIG guards the runbook's rule that a resize across a
        # short gap reads as a twitch rather than a move — a two-second quiet
        # patch keeps the busy layout rather than flipping twice.
        quiet = who is None and dur >= MIN_BIG and not first_is_card(n, has_card)
        seg = {"seg_id": n, "type": who or "quiet", "duration": dur,
               "caption_pos": "top" if quiet else "bottom",
               "voiceover": " ".join(lines[k]["text"] for k in idx),
               "phrases": [{"text": lines[k]["text"],
                            "t_in": rel(lines[k]["start"], s_start),
                            "t_out": rel(lines[k]["end"], s_start)} for k in idx]}

        # CAPTIONS UNDER THE CARD ARE NOT DRAWN.
        #
        # The card is opaque over both caption bands for its whole hold, so
        # these captions are never seen while it is up - but the card leaves
        # on a dissolve, and a caption still running under it reads straight
        # through the fading card. PHY-C1-SA-01 shipped that way: "और इस बार
        # भी आपके Board exam में आ सकता है" ends 8.77s, the card dissolved
        # 8.33-8.83s, and the line hung ghosted across the fading sheet.
        # Only when the card's last line is KNOWN (`card_last`): without it
        # segment 1 can run past the card, and those captions must show.
        if (first_is_card(n, has_card) and who is None and card_last is not None
                and idx[-1] <= card_last):
            seg["under_card"] = True
            under_card.append({"seg_id": n, "reason": "card", "phrases": seg["phrases"]})
            seg["phrases"] = []

        if who:
            d = design[who]
            span = max(d.get("duration", dur), 0.1)
            k = dur / span                      # designed -> real
            for key in ("diagram", "block", "veo", "labels", "equation"):
                if key not in d:
                    continue
                seg[key] = json.loads(json.dumps(d[key]))
            # A COUNTED LIST FILLS IN ON THE CAPTIONS THAT NAME ITS ITEMS.
            #
            # `at` is that caption's offset inside the beat's own run of lines.
            # Without it the m-th item lands on the m-th line, which assumes the
            # items are named on consecutive captions. They often are not:
            # BIO-C12-LA-02 part 3 names its three pyramid types three lines
            # apart — "सबसे पहले... संख्या के पिरामिड की" (offset 0), "फिर आता है
            # जैव मात्रा का" (3), "और आखिर में ऊर्जा का" (5) — and positionally
            # all three would have appeared inside the first sentence.
            def _when(m: int, spec: dict) -> float:
                at = spec.get("at")
                if at is None:
                    at = min(m, len(idx) - 1)
                if not 0 <= at < len(idx):
                    raise SystemExit(
                        f"seg {n} ({who}): item {m} says at={spec['at']}, but the "
                        f"beat owns only {len(idx)} caption line(s)")
                return rel(lines[idx[at]]["start"], s_start)

            # A WORD ANCHOR BEATS EVERYTHING ELSE.
            #
            # `wi` is an index into out/words_part<N>.json — the measured onset
            # of the word that step illustrates — plus an optional `dt`. It is
            # CLIP_VIDEO_RUNBOOK §5's ("w", word, n, dt) anchor made exact: no
            # proportional rescale, no fuzzy search that can land on the wrong
            # repetition of a word. The word must lie inside the lines this
            # beat owns, or the step would illustrate a sentence the segment
            # does not contain — that is a hard failure, printed with the word.
            lo_w = lines[idx[0]].get("w", [None])[0]
            hi_w = lines[idx[-1]].get("w", [None, None])[1]

            def _word(wi: int, dt: float = 0.0, what: str = "") -> float:
                if words is None or lo_w is None:
                    raise SystemExit(f"seg {n} ({who}): {what} anchors to word {wi} but "
                                     f"the lines carry no word ranges (lines_from_edit.py)")
                if not lo_w <= wi <= hi_w:
                    raise SystemExit(f"seg {n} ({who}): {what} anchors to word {wi} "
                                     f"{words[wi]['w']!r}, outside this beat's words "
                                     f"{lo_w}-{hi_w}")
                t = rel(words[wi]["s"] + dt, s_start)
                anchors_log.append(f"       seg {n:2d} {what:28.28s} @ word {wi:3d} "
                                   f"{words[wi]['w']!r:18s} t={t:6.2f}")
                return t

            blk = seg.get("block")
            for key in ("items", "cards"):
                for m, it in enumerate((blk or {}).get(key) or []):
                    if "wi" in it:
                        it["t"] = _word(it.pop("wi"), it.pop("dt", 0.0),
                                        f"item {(it.get('text') or it.get('head'))}")
                    else:
                        it["t"] = _when(m, it)
                    it.pop("at", None)          # consumed; the renderer wants `t`
            for key in ("block", "veo"):
                if key in seg:
                    seg[key]["t_in"] = round(min(seg[key].get("t_in", 0.3) * k, 0.6), 3)
                    seg[key]["t_out"] = round(dur - 0.24, 3)
            for key in ("block", "veo"):
                if key in seg and "wi" in seg[key]:
                    seg[key]["t_in"] = _word(seg[key].pop("wi"), seg[key].pop("dt", 0.0),
                                             f"{key} in")
            clear = round(dur - 0.24, 3)
            if "equation" in seg:
                eq = seg["equation"]
                eq["t_in"] = (_word(eq.pop("wi"), eq.pop("dt", 0.0), "equation in")
                              if "wi" in eq else round(eq.get("t_in", 0.3) * k, 3))
                hs = eq.get("highlight") or []
                for h in (hs if isinstance(hs, list) else [hs]):
                    h["t"] = (_word(h.pop("wi"), h.pop("dt", 0.0), "equation step")
                              if "wi" in h else round(h["t"] * k, 3))
                for a in eq.get("arcs") or []:
                    if "wi" in a:
                        a["t"] = _word(a.pop("wi"), a.pop("dt", 0.0), f"arc {a.get('label')}")
                if d.get("clear", True):
                    eq["t_out"] = clear
            if "diagram" in seg:
                # engine.js treats carry_over as optional; validate.py does not.
                # The generated spec states it explicitly so both are satisfied
                # without loosening a check.
                seg["diagram"].setdefault("carry_over", [])
                tl = seg["diagram"].get("timeline", [])
                for a in tl:
                    if "wi" in a:
                        a["t"] = _word(a.pop("wi"), a.pop("dt", 0.0), f"{a['action']} {a['id']}")
                    else:
                        a["t"] = round(a["t"] * k, 3)
                # CLEAR AT end - 0.24 OVER 0.22 (runbook §5). The DOM is
                # rebuilt at the boundary, so without this every shape cuts
                # out hard; with the old end-0.55/0.50 it dissolved through the
                # tail of the sentence. Opt out per beat with "keep": true for a
                # diagram that carries into the next segment.
                shown = {a["id"] for a in tl if a["action"] in
                         ("fade_in", "pop_in", "draw")}
                gone = {a["id"] for a in tl if a["action"] in ("fade_out", "pop_out")}
                if d.get("clear", True):
                    # carried-in shapes have no in-action here but are on
                    # screen all the same, so they clear with the rest
                    for sid in sorted((shown | set(seg["diagram"]["carry_over"])) - gone):
                        tl.append({"id": sid, "action": "fade_out", "t": clear, "dur": 0.22})
                else:
                    # carried into the next segment: say what is still on
                    # screen, which is what the next beat's carry_over is
                    # checked against
                    seg["end_state"] = sorted((shown | set(seg["diagram"]["carry_over"])) - gone)
            for l in seg.get("labels", []):
                if l.get("carry"):
                    l["t_in"] = 0.0             # already on screen; see engine.js
                if "wi" in l:
                    l["t_in"] = _word(l.pop("wi"), l.pop("dt", 0.0), f"label {l['text']}")
                else:
                    l["t_in"] = round(l["t_in"] * k, 3)
                if "out_wi" in l:
                    l["t_out"] = min(_word(l.pop("out_wi"), l.pop("out_dt", 0.0),
                                           f"label-out {l['text']}"), clear)
                elif l.get("t_out") is not None:
                    l["t_out"] = round(min(l["t_out"] * k, clear), 3)
                elif d.get("clear", True):
                    l["t_out"] = clear          # a label moves with its shapes
                if l.get("carry"):
                    l["t_in"] = 0.0
        segs.append(seg)

    # A GROW THAT IS ABOUT TO BE UNDONE IS A TWITCH, NOT A MOVE.
    #
    # MIN_BIG asks only "is this quiet patch long enough to grow into". That is
    # the wrong question when there is content on BOTH sides of it: the frame
    # then changes twice — out of the busy layout and straight back into it —
    # and the two changes read as one flinch rather than as two decisions.
    # A patch between two busy stretches has to earn the round trip.
    for i, s in enumerate(segs):
        if s["caption_pos"] != "top" or s["duration"] >= MIN_ISLAND:
            continue
        before = i > 0 and segs[i - 1]["type"] != "quiet"
        after = i + 1 < len(segs) and segs[i + 1]["type"] != "quiet"
        if before and after:
            s["caption_pos"] = "bottom"
            print(f"     seg {s['seg_id']}: {s['duration']:.1f}s of quiet between "
                  f"two busy segments — keeping the busy layout")

    # A CAPTION NEVER SHARES THE FRAME WITH A GRAPHIC.
    #
    # Standing instruction, given on the क्वथनांक build and repeated after two
    # stale preview frames still showed captions over graphics: captions run
    # ONLY when nothing else is on screen. The presenter is already speaking the
    # line and the graphic is already organising it, so a caption on top is a
    # third copy of the same information.
    #
    # THIS WAS IMPLEMENTED ONCE AND THEN LOST. work/quathanank-part1 and -part2
    # do it correctly — 0 of their 14 graphic segments carry captions — but the
    # code lived inside those folders and was never promoted here, which is the
    # exact failure PROCESS.md marks with ⬜. Every video built since ran
    # without it: bio-c5-la-01 and bio-c12-la-02 carry captions over 100% of
    # their graphic segments.
    #
    # It is a per-SEGMENT decision, not per-caption. Suppressing only the
    # captions that literally overlap a shape makes the band blink on and off
    # inside a sentence.
    #
    # Nothing is discarded: the text goes to spec/captions_suppressed_part<N>
    # so it can be read back, and the caller writes it.
    #
    # OFF BY DEFAULT, and that is a real decision rather than an oversight.
    # The rule was given when the caption band OVERLAPPED the stage. This
    # theme puts the band at --cap-top 1050 with the stage ending at 850, so
    # they share no pixels, and validate.py carries an explicit note that the
    # separated layout is the approved one. Pass --suppress-captions to turn
    # it on for a theme where the two bands meet, or if the house rule is
    # meant to hold regardless of overlap.
    # `suppress_on_graphics` is True (every graphic kind) or a set of kinds.
    # CHE-C3-SA-06: the user asked for captions off "while explaining the
    # equation" — the ladder on the stage is what he is reading out, so the
    # caption under it said the same thing twice — while the graph segments
    # keep theirs. Hence per kind: --suppress-captions=equation.
    kinds = ({"diagram", "equation", "block", "veo"} if suppress_on_graphics is True
             else set(suppress_on_graphics or ()))
    suppressed = []
    for s in (segs if kinds else []):
        why = next((k for k in ("diagram", "equation", "block", "veo") if s.get(k)), None)
        if why in kinds and s.get("phrases"):
            suppressed.append({"seg_id": s["seg_id"], "reason": why,
                               "phrases": s["phrases"]})
            s["phrases"] = []
    if under_card:
        print(f"     {sum(len(x['phrases']) for x in under_card)} caption(s) under the "
              f"question card left out of the render (the card covers them; its "
              f"dissolve would show them through it)")
    if suppressed:
        n_cap = sum(len(x["phrases"]) for x in suppressed)
        print(f"     captions suppressed on {len(suppressed)} graphic segment(s) "
              f"({n_cap} caption(s)) — a caption never shares the frame with a graphic")
    return {"segs": segs, "clip_end": clip_end, "suppressed": under_card + suppressed,
            "anchors": anchors_log}


def main() -> int:
    slug, part, clip_end = sys.argv[1], int(sys.argv[2]), float(sys.argv[3])
    # Whether THIS part opens under the question card. Passed, not read off
    # out/card_part<N>.json: that file is composite.py's card-window argument
    # and only parts that HAVE a card write one.
    has_card = "--card" in sys.argv[4:]
    suppress = False
    for a in sys.argv[4:]:
        if a == "--suppress-captions":
            suppress = True                          # every graphic kind
        elif a.startswith("--suppress-captions="):
            suppress = set(a.split("=", 1)[1].split(","))
    card_last = None
    for a in sys.argv[4:]:
        if a.startswith("--card-last="):
            card_last = int(a.split("=", 1)[1])
    # THE BODY MUST OUTLAST THE LAST CAPTION'S EXIT.
    # A HeyGen clip ends on its last word, so the last caption's t_out sits at
    # the clip's end and its 0.16s pop_out (engine.js) never gets to run: the
    # final frame still carries it. answer_outro.py freezes that frame and
    # dissolves it into the answer page, so on PHY-C1-SA-01 "और syllabus
    # complete करते जाओ" hung over the incoming page for a second. The body is
    # extended, on the 30fps grid, until the caption has fully cleared; the
    # audio is silent there and composite.py holds his last frame across it.
    POP_OUT, FPS = 0.16, 30
    last = json.loads((Path("work") / slug / "out" / f"lines_part{part}.json")
                      .read_text(encoding="utf-8"))[-1]
    need = last["end"] + POP_OUT + 1.0 / FPS
    if need > clip_end + 1e-6:
        grid = -(-round(need * FPS * 1000) // 1000) / FPS      # ceil to a frame
        print(f"     body extended {clip_end:.3f} -> {grid:.3f}s so the last caption "
              f"(ends {last['end']:.3f}) finishes leaving before the final frame")
        clip_end = round(grid, 3)
    out = build(slug, part, clip_end, has_card, suppress, card_last)
    segs = out["segs"]
    if out["anchors"]:
        print("     word anchors (every step on the onset of the word it illustrates):")
        print("\n".join(out["anchors"]))
    p = Path("work") / slug / "spec" / f"segments_part{part}.json"
    p.write_text(json.dumps(segs, ensure_ascii=False, indent=1), encoding="utf-8")

    # What the graphic segments would have said. Kept so the decision is
    # reversible and so nothing is silently lost — never read by the renderer.
    sp = Path("work") / slug / "spec" / f"captions_suppressed_part{part}.json"
    sp.write_text(json.dumps(out["suppressed"], ensure_ascii=False, indent=1),
                  encoding="utf-8")

    # The SAME list drives the caption position and the presenter size, so the
    # two states cannot drift apart. Written as absolute spans, which is what
    # composite.py's window arguments take.
    t, busy_w, big_w = 0.0, [], []
    for s in segs:
        # Segment 1 is left out of both lists only when the card is over it:
        # composite holds him at CARD_W there off the card window instead.
        if s["seg_id"] != 1 or not has_card:
            (big_w if s["caption_pos"] == "top" else busy_w).append(
                [round(t, 2), round(t + s["duration"], 2)])
        t += s["duration"]
    root = Path("work") / slug / "out"
    (root / f"windows_part{part}.json").write_text(json.dumps(busy_w, indent=1))
    (root / f"big_part{part}.json").write_text(json.dumps(big_w, indent=1))
    print(f"     {len(busy_w)} busy window(s) (caption low, presenter small), "
          f"{len(big_w)} empty window(s) (caption high, presenter big)")

    total = sum(s["duration"] for s in segs)
    busy = sum(s["duration"] for s in segs if s["type"] != "quiet")
    caps = sum(len(s["phrases"]) for s in segs)
    print(f"  part {part}: {len(segs)} segments, {caps} captions -> {p}")
    print(f"     total {total:.2f}s vs clip {clip_end:.2f}s  "
          f"(diff {abs(total-clip_end):.3f}s)")
    print(f"     stage busy {busy:.1f}s = {busy/clip_end:.0%}, "
          f"quiet {total-busy:.1f}s = {(total-busy)/clip_end:.0%}")
    bad = [s["seg_id"] for s in segs if s["duration"] <= 0]
    if abs(total - clip_end) > 0.05 or bad:
        print(f"  FAIL: sum is off, or empty segments {bad}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
