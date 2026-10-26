"""Re-time a caption track onto the audio's own word clock.

    python tools/retime_lines.py <words.json> <lines.json> [--tail 0.25]

The HeyGen srt gives cue times that are close but not exact, and its cue END is
just wherever the cue stopped -- so a caption built from it can linger through a
pause or leave while the phrase is still being said. This puts BOTH ends of every
line on measured word timings:

    start = the first word of the line, as spoken
    end   = the last word of the line, plus a short tail, and never past the
            next line's start

Two things it does NOT do, both deliberate:

  * it never moves a line it could not place. A line the aligner did not match
    keeps its srt time, because a guessed position is worse than a slightly
    imprecise one -- and the report says how many those were;
  * it does not close every gap. If the speaker pauses for two seconds the
    caption comes down; holding it there is what makes a track feel late, since
    the eye reads the stale line and waits for it to be wrong.
"""
from __future__ import annotations

import difflib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from align import coverage, monotonic, skel, toks  # noqa: E402

MIN_RUN = 2
# A word cannot really last this long. Whisper occasionally collapses a whole
# stretch of speech into ONE word span -- on BIO-C5-LA-04 part 3 it gave
# "परीक्षा" 11.4 seconds, swallowing four spoken lines. Anchoring on that drags
# every line near it to the same instant, and it also makes the sync score read
# 0% for captions that are in fact fine. Such words are dropped before matching.
MAX_WORD = 2.0
FLOOR = 0.60          # a caption is never shown for less than this
# A backstop only. Placement is already bounded by the search window, so this
# duplicates it -- kept because it is the thing that fails loudly if the window
# is ever widened without thinking about it.
#
# It was 1.20 while the aligner was global and unreliable, and that cap then
# fought the fix: measured against the transcript, part 1 scored 62% median
# word overlap at 1.20 and 78% at 2.50, with lines scoring under 30% falling
# from 20 to 6. A guard tuned for a broken aligner makes a working one worse.
#
# Without the cap the aligner moved 14 of 57 lines by more than two seconds, and
# checking two of them against Whisper's own words showed the aligner was wrong,
# not the srt: "आई ए एलील A एंटीजन..." and "आई बी एलील B एंटीजन..." differ only in
# ए/बी, and the consonant skeleton drops vowels, so the two lines are the same
# token sequence and it matched the second occurrence. The other big mover took
# its start from "की RBC", a phrase that recurs later in the same sentence.
MAX_MOVE = 2.50


def usable(words: list[dict]) -> list[dict]:
    """Words with a plausible duration. See MAX_WORD."""
    return [w for w in words if (w.get("e", w["s"]) - w["s"]) <= MAX_WORD]


def place(lines: list[dict], words: list[dict], win: float = 2.5):
    """First and last spoken word of each line, searched NEAR its srt time.

    The earlier version aligned the whole caption track against the whole
    transcript in one difflib pass and took each line's earliest matching word.
    That cannot separate two lines whose consonant skeletons are identical --
    "आई ए एलील A एंटीजन..." and "आई बी एलील B एंटीजन..." differ only in ए/बी and
    A/B, and skel() drops vowels -- so it matched the wrong occurrence and moved
    the line 3.5s. It also took a line's start from a phrase that recurred later
    in the same sentence ("की RBC"), which is the same failure with one line.

    Position resolves both. The srt is accurate to about a second, so the search
    is limited to a window around each line's own srt time, and the cursor only
    moves forward -- a line can never match words that belong to an earlier one.
    align.py warns that per-line windows score far worse than a global pass, and
    that is true of ITS problem: matching a written script to a clip, where a
    line may be absent entirely and the offset is unknown. Here the times are
    already close, and the ambiguity is local.
    """
    words = usable(words)
    tw = [skel(w["w"]) for w in words]
    out, cur = [], 0
    for l in lines:
        t0, t1 = l["start"], l["end"]
        lo = next((j for j in range(cur, len(words)) if words[j]["s"] >= t0 - win),
                  len(words))
        hi = next((j for j in range(lo, len(words)) if words[j]["s"] > t1 + win),
                  len(words))
        ct = toks(l["text"])
        if not ct or hi - lo < 1:
            out.append((None, None, 0.0))
            continue
        sm = difflib.SequenceMatcher(None, ct, tw[lo:hi], autojunk=False)
        blocks = [b for b in sm.get_matching_blocks() if b.size]
        if not blocks:
            out.append((None, None, 0.0))
            continue
        hit = sum(b.size for b in blocks)
        share = hit / len(ct)
        a = words[lo + blocks[0].b]["s"]
        lastb = blocks[-1]
        j = lo + lastb.b + lastb.size - 1
        b = words[j].get("e", words[j]["s"])
        out.append((a, b, share))
        cur = max(cur, lo + blocks[0].b)          # forward-only cursor
    return out


def retime(lines: list[dict], words: list[dict], tail: float = 0.25):
    """Put both ends of every line on the word clock. Returns (lines, report)."""
    texts = [l["text"] for l in lines]
    sp3 = place(lines, words)
    ref: dict[int, float] = {}
    # SECOND PASS. A stretch of part 3 drifts nearly three seconds, which is
    # outside the window, so those lines cannot find themselves and keep their
    # srt time -- six consecutive captions showing the words spoken two lines
    # later. The lines that DID place are anchors: interpolating between them
    # gives a much better guess than the srt for the ones that did not, and the
    # window is re-centred on that.
    anch = [(l["start"], a) for l, (a, _, sh) in zip(lines, sp3)
            if a is not None and sh >= 0.34]
    if len(anch) >= 2:
        import bisect
        xs = [x for x, _ in anch]
        ys = [y for _, y in anch]

        def guess(t):
            i = bisect.bisect_left(xs, t)
            if i == 0:
                return t + (ys[0] - xs[0])
            if i >= len(xs):
                return t + (ys[-1] - xs[-1])
            f = (t - xs[i - 1]) / max(1e-6, xs[i] - xs[i - 1])
            return ys[i - 1] + f * (ys[i] - ys[i - 1])

        redo = [i for i, (a, _, sh) in enumerate(sp3) if a is None or sh < 0.34]
        if redo:
            shifted = [dict(l) for l in lines]
            for i in redo:
                d = guess(lines[i]["start"]) - lines[i]["start"]
                shifted[i]["start"] += d
                shifted[i]["end"] += d
            again = place(shifted, words)
            for i in redo:
                if again[i][0] is not None and again[i][2] >= 0.34:
                    sp3[i] = again[i]
                    # the guess, not the srt, is this line's prior now: it was
                    # re-searched precisely because the srt was too far out
                    ref[i] = shifted[i]["start"]
    # a line must match at least a third of its own tokens to be trusted
    sp = [(a, b) if (a is not None and sh >= 0.34) else (None, None)
          for a, b, sh in sp3]
    ratio = sum(1 for a, _ in sp if a is not None) / max(1, len(sp))
    placed = sum(1 for a, _ in sp if a is not None)
    cov = coverage(texts, words)

    starts, rejected = [], 0
    for i, (a, _) in enumerate(sp):
        srt = ref.get(i, lines[i]["start"])
        if a is None or abs(a - srt) > MAX_MOVE:
            rejected += a is not None
            starts.append(srt)
        else:
            starts.append(a)
    # Lines the aligner could not separate all land on the same word, and
    # monotonic() then fans them out by its minimum gap -- which produced runs of
    # 0.35s captions in BIO-C1-LA-01 part 3. A caption that flashes for a third
    # of a second is unreadable, and worse than one that is slightly late. Where
    # a run is bunched like that, space it evenly between the confident line
    # before it and the confident line after.
    starts = monotonic(starts)
    GAP, MIN_ON = 0.36, 0.80
    i = 0
    while i < len(starts) - 1:
        j = i
        while j + 1 < len(starts) and starts[j + 1] - starts[j] < GAP:
            j += 1
        if j > i:
            lo = starts[i]
            hi = starts[j + 1] if j + 1 < len(starts) else lo + (j - i + 1) * MIN_ON
            step = (hi - lo) / (j - i + 1)
            for k in range(i, j + 1):
                starts[k] = round(lo + (k - i) * step, 2)
        i = j + 1
    clip_end = lines[-1]["end"]
    moved = []
    for i, l in enumerate(lines):
        old = l["start"]
        l["start"] = starts[i]
        nxt = starts[i + 1] if i + 1 < len(starts) else clip_end
        a, b = sp[i]
        # the end is capped the same way: a last-word time that implies a wildly
        # long or short caption is the same mis-match, seen from the other side
        if b is not None and abs(b - l.get("end", nxt)) > MAX_MOVE + 1.0:
            b = None
        e = (b + tail) if b is not None else nxt
        l["end"] = round(min(max(e, starts[i] + FLOOR), nxt), 2)
        if abs(l["start"] - old) > 0.05:
            moved.append(l["start"] - old)

    # A caption shorter than MIN_ON is unreadable. Where the line before it
    # finished early there is room to start it SOONER, which both fixes the
    # flash and moves it closer to where the words actually are -- a line that
    # lands a little early reads far better than one that blinks. This catches
    # the case the aligner cannot: two lines whose only distinctive word occurs
    # twice, matched to the later occurrence and then squeezed against the next
    # confident line.
    MIN_ON = 0.80
    for i, l in enumerate(lines):
        if l["end"] - l["start"] >= MIN_ON:
            continue
        floor = lines[i - 1]["end"] if i else 0.0
        want = l["end"] - MIN_ON
        l["start"] = round(max(floor, want), 2)

    import statistics
    gaps = sum(1 for i, l in enumerate(lines[:-1]) if lines[i + 1]["start"] - l["end"] > 0.5)
    return lines, {"placed": placed, "rejected": rejected,
                   "total": len(lines), "ratio": ratio,
                   "coverage": cov, "moved": len(moved),
                   "median": statistics.median(moved) if moved else 0.0,
                   "largest": max(moved, key=abs) if moved else 0.0, "gaps": gaps}


def main() -> int:
    wf, lf = Path(sys.argv[1]), Path(sys.argv[2])
    tail = float(sys.argv[sys.argv.index("--tail") + 1]) if "--tail" in sys.argv else 0.25
    lines, r = retime(json.loads(lf.read_text()), json.loads(wf.read_text()), tail)
    lf.write_text(json.dumps(lines, ensure_ascii=False, indent=1))
    print(f"{lf.name}: {r['placed']}/{r['total']} lines placed on the word clock "
          f"(match {r['ratio']:.2f}, coverage {r['coverage']*100:.0f}%)")
    print(f"   moved {r['moved']} lines, median {r['median']:+.2f}s, "
          f"largest {r['largest']:+.2f}s "
          f"({r['rejected']} rejected as mis-matches, kept their srt time)")
    print(f"   {r['gaps']} gaps over 0.5s where the screen is deliberately clear")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
