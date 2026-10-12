"""Is a delivered SRT actually in sync with the clip's audio?

    python tools/srt_drift.py <clip.srt> <words.json> [--silences anchors.json]

`CLIP_VIDEO_RUNBOOK.md` says the SRT owns the clock and that you confirm it by
cross-correlating its cues against the audio envelope. That check measures
whether the cue SPANS cover the speech, and it is necessary but NOT sufficient:
spans can cover the speech while every boundary inside them sits in the wrong
place. CHE-C4-LA-03 part 1 passed it at 98.2% with a best global shift of
−0.10s, and its cue starts were still wrong by −2.26s to +1.47s. Built on those,
the animation ran up to 2.3s from the voice.

So this checks each boundary instead: it takes the first few words of every cue
and finds where they are actually spoken.

HOW A CUE IS LOCATED
--------------------
Words are reduced to their consonant skeleton (`tools.align.skel`) before
matching. Whisper misspells Hindi freely — "उच्छतम" for "उच्चतम", "संक्रमन" for
"संक्रमण" — and returns one clip in Devanagari and the next romanised, from the
same model and settings. Matras and halant are exactly what it gets wrong, so
dropping them is what makes the comparison survive.

The search is WINDOWED to ±`--win` seconds of the SRT's own time, not global. A
global difflib pass over 26 short cues scored 0.78 here and returned nothing at
all for two of them, because a cue like "+ two, + three, ..." has no consonants
to match on. The SRT is wrong by seconds, not by minutes, so a window is both
safer and more accurate — but it does mean this tool can only ever CONFIRM or
CORRECT a roughly-right SRT, never resynchronise a badly broken one.

READING THE OUTPUT
------------------
`conf` is the difflib ratio of the skeletons. Below ~0.55 the match is a guess
and the row is not counted: a cue that is mostly digits or Latin ("+ two, +
three") frequently lands there, and a low-confidence row is a reason to look at
the transcript by hand, not evidence of drift.

**Where the speaker pauses, the measured silences outrank both this tool and the
SRT.** `--silences` prints the nearest silence to each cue start, and a run of
evenly spaced silences through a counted list marks each item exactly. That is
how part 1's six oxidation-state numbers were timed after both the SRT (1.9s
late) and Whisper's own word starts proved unreliable on them.

Exit status is 1 if any confident cue drifts past `--tol`, so this can gate a
build.
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.align import skel, spoken  # noqa: E402


def read_srt(path: Path) -> list[dict]:
    def t(s: str) -> float:
        h, m, rest = s.split(":")
        sec, ms = rest.split(",")
        return int(h) * 3600 + int(m) * 60 + int(sec) + int(ms) / 1000

    out = []
    for block in re.split(r"\n\s*\n", path.read_text(encoding="utf-8").strip()):
        lines = [x for x in block.splitlines() if x.strip()]
        if len(lines) < 2 or "-->" not in lines[1]:
            continue
        a, b = lines[1].split(" --> ")
        out.append({"i": int(lines[0]), "s": round(t(a), 3), "e": round(t(b), 3),
                    "text": " ".join(lines[2:]).strip()})
    return out


def onset(cue: dict, words: list[tuple[float, str]], win: float, n: int = 3):
    """Where this cue's opening words are actually spoken, and how sure we are."""
    # Hyphenated compounds are split the way lines_from_edit.sk() splits them.
    # "दर-स्थिरांक" was one cue token against whisper's two ("दर", "स्थिरांक"),
    # so the window started a word early: CHE-C3-SA-05's "लेकिन दर-स्थिरांक…"
    # matched 0.47s late. (Letting the window WIDTH vary to absorb fused tokens
    # was tried too and rejected: it raised new false drifts on PHY-C1-SA-01.)
    want = [x for x in (skel(w) for w in re.sub(r"-", " ", spoken(cue["text"])).split())
            if x][:n]
    if not want:
        return None, 0.0
    target = " ".join(want)
    best = None
    for i, (t0, _) in enumerate(words):
        if not (cue["s"] - win <= t0 <= cue["s"] + win):
            continue
        got = " ".join(w for _, w in words[i:i + len(want)])
        r = difflib.SequenceMatcher(None, target, got).ratio()
        if best is None or r > best[0]:
            best = (r, t0)
    return (best[1], best[0]) if best else (None, 0.0)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("srt", type=Path)
    p.add_argument("words", type=Path, help="from tools/transcribe.py")
    p.add_argument("--silences", type=Path, help="anchors.json, for a second opinion")
    p.add_argument("--win", type=float, default=3.2, help="search window, seconds")
    p.add_argument("--tol", type=float, default=0.50, help="drift that counts as an error")
    p.add_argument("--conf", type=float, default=0.55, help="ratio below which a match is a guess")
    a = p.parse_args()

    cues = read_srt(a.srt)
    # A token with no skeleton ("90", "0") cannot match anything, but left in
    # it still takes a slot in the comparison window. The cue side already
    # drops them, so the two sides were counting words differently: on
    # PHY-C1-SA-01 "और cos 90°" matched "cost 90 degree" 0.40s late instead of
    # "और cost 90" where it is spoken.
    words = [(float(w["s"]), s) for w in json.loads(a.words.read_text())
             if (s := skel(w["w"]))]
    sil = []
    if a.silences and a.silences.is_file():
        sil = [tuple(x) for x in json.loads(a.silences.read_text()).get("silences", [])]

    print(f"{len(cues)} cues vs {len(words)} transcript tokens, "
          f"window +-{a.win}s, tolerance {a.tol}s\n")
    head = f"{'cue':>3} {'SRT':>8} {'spoken':>8} {'drift':>7} {'conf':>5}"
    if sil:
        head += f" {'silence ends':>13}"
    print(head + "  text")

    bad, low, drifts = [], [], []
    for c in cues:
        t, r = onset(c, words, a.win)
        row = f"{c['i']:>3} {c['s']:8.3f}"
        if t is None:
            print(row + f" {'--':>8} {'--':>7} {'--':>5}  {c['text'][:40]}")
            low.append(c["i"]); continue
        d = c["s"] - t
        row += f" {t:8.2f} {d:+7.2f} {r:5.2f}"
        if sil:
            near = min(sil, key=lambda s: abs(s[1] - c["s"]))
            row += f" {near[1]:13.2f}" if abs(near[1] - c["s"]) < 2.5 else f" {'-':>13}"
        flag = ""
        if r < a.conf:
            low.append(c["i"]); flag = "   ? low confidence"
        else:
            drifts.append(abs(d))
            if abs(d) > a.tol:
                bad.append((c["i"], round(d, 2))); flag = "   <<< DRIFT"
        print(row + f"  {c['text'][:40]}{flag}")

    print()
    if drifts:
        drifts.sort()
        print(f"{len(drifts)} confident cues | median |drift| {drifts[len(drifts)//2]:.2f}s | "
              f"max {drifts[-1]:.2f}s")
    if low:
        print(f"{len(low)} cue(s) below the confidence floor - check by hand: {low}")
    if bad:
        print(f"\nX {len(bad)} cue(s) drift past {a.tol}s: {bad}")
        print("  Do NOT build spans off this SRT. Take each span from the measured")
        print("  onset instead, and prefer a silence wherever the speaker pauses.")
        return 1
    print(f"\nOK - every confident cue is within {a.tol}s of the words it carries.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
