#!/usr/bin/env python3
"""Draft a part's caption edit: every HeyGen SRT cue placed on the transcript BY ITS TEXT.

    python3 tools/draft_captions.py <slug> <part> [--out PATH] [--srt PATH]

Reads   work/<slug>/inputs.json              the part's SRT and clip duration
        <the SRT>                            the script's wording, one cue per line
        work/<slug>/out/words_part<N>.json   the measured words
Writes  work/<slug>/out/caption_edit_part<N>.draft.json   (or --out)

    [ {"w": [0, 5],  "text": "MP Board कक्षा barvi के बच्चों,", "cue": 1},
      {"w": [6, 19], "text": "...", "cue": 2, "flag": "..."} ]

WHY IT EXISTS
-------------
`tools/lines_from_edit.py` takes the timing from the words and the wording from
a hand-written edit that names each caption as a RANGE OF WORD INDICES. Writing
that edit meant reading the SRT beside the transcript and counting words — about
ten minutes a part, all of it mechanical. The SRT's WORDING is the script and is
right; its TIMES drift 2-4s per cue and are not used to place anything. So the
ranges here come from the text alone, and the reviewer's job shrinks to
notation (`barvi` -> `12वीं`, spoken formulae -> notation) and the flags.

HOW A CUE IS PLACED
-------------------
Both sides are reduced to consonant skeletons with `tools.align.skel` and
`spoken`, as lines_from_edit's gate does, so Devanagari against romanised
whisper, dropped matras and notation are tolerated the same way. Two additions
for PLACEMENT only (`msk`): digits are read aloud (`2.303R` = `two point three
zero three R`, `0` = `zero`, `T₂` = `T two`), and a vowel-only token (`E`,
`ए`) keeps a letter instead of vanishing.

  1. ANCHOR. One global difflib pass over the whole part, skeleton CHARACTER
     against skeleton character. Characters, not tokens, because whisper splits
     and joins words freely (`दर-स्थिरांक` -> `दर इस्थिरांग`, `विद्युत् फ्लक्स` ->
     `विद्यूत्फलक्स`). Each cue's first matched character gives its rough start.
  2. SEGMENT. A dynamic programme chooses every boundary within WINDOW words
     of its anchor, maximising the skeleton characters each cue matches INSIDE
     ITS OWN RANGE (an exact LCS — see Matcher). Ranges are contiguous and
     ordered by construction, and every cue gets at least one word.
  3. TIE-BREAK. A word no cue matches (a filler, `21` heard for `इकाई`) scores
     the same on either side of a boundary, so the boundary goes where the
     SPEAKER stopped: after a word whisper punctuated or HELD (`held` — the
     word clock has no gaps, so a pause is the previous word stretched). Each
     is worth about one matched character: enough to settle a tie, never
     enough to overrule the text.

The SRT's times place nothing. They are only checked afterwards (FAR).

Measured against captions placed by hand: every hand caption that starts on
an SRT cue starts on the same word here — CHE-C3-SA-04 33/33, CHE-C3-SA-05
25/25, BIO-C2-LA-01 parts 2-3 48/48 (shipped lines). The hand files differ
only where a person SPLIT a cue, and the split suggestion agrees on 5 of 9.

WHAT IT FLAGS (`"flag"` on the entry — a human must look)
------------------------------------------------------------
  * over LONG characters: it cannot fit the band. `split_at` is the word the
    second half starts at (`[i, split_at-1]`, `[split_at, j]`), `split_text`
    the text cut there — at the cue's own punctuation if that lets both halves
    fit, else before a conjunction. Both halves keep the same `cue`.
  * similarity under LOW against its own words (under SIM, lines_from_edit
    refuses it). The flag says which kind: when the text matches its words
    once numbers are read aloud, the RANGE is right and the WORDING is what
    the gate cannot read (`two point three zero three` against `2.303`) —
    write the digits or notation; otherwise the range itself is suspect.
    Either way it quotes what whisper heard.
  * a cue that matched (almost) nothing — whisper lost it, or the SRT has a
    line the clip never says; it was placed by pauses alone.
  * placed more than FAR seconds from its SRT time.
  * too short to read by lines_from_edit's floor — merge it into the
    neighbour it is spoken closer to (named).
  * the whole SRT accounting for under WRONG_SRT of what was said: another
    part's SRT scores 0.33-0.40, a right one 0.91-0.98. Printed as a WARNING.

FAILURE MODES
-------------
  * A word nothing matches, with no punctuation and no hold on either side,
    goes to the later cue. On the nine parts checked that happened once
    (a 37 ms `K,` whisper invented) and was harmless — but it is not flagged.
  * Two adjacent cues that repeat a phrase, with no pause between them, can
    trade a word; similarity stays high either way, so this is NOT flagged.
  * Words whisper invented at the head or tail of the clip land in the first
    or last cue and pull its similarity down.
  * A split is a suggestion on TEXT: a person may prefer a balanced break to
    a comma, or split an 80-character cue this leaves whole.
  * The text is the SRT's spoken form. The draft is never the caption file:
    it goes to `.draft.json`, and this tool refuses to write
    caption_edit_part<N>.json itself.
  * A part with no SRT has no cues to place. The draft falls back to
    `tools/lines_from_words.py`'s grouping of whisper's own words, every entry
    flagged and no `cue` — the wording must be corrected against the script.

Exit 0 whenever a full contiguous cover was written, flags or not; exit 1 only
when one cannot be produced (fewer words than cues, missing input).
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.align import skel, spoken                                   # noqa: E402
from tools.lines_from_edit import GAP, HOLD, MIN_DUR, SIM, TAIL, sk  # noqa: E402

LONG = 100          # characters: over this a cue needs three band lines (CLIP_VIDEO_RUNBOOK §5)
LOW = 0.65          # similarity worth a human read; lines_from_edit refuses below SIM
NOTHING = 0.25      # a cue matching under this share of its skeleton matched nothing
READ_RATE = 4.5     # words/sec — the readability floor lines_from_edit and validate.py apply
WINDOW = 8          # words either side of the anchor a boundary may move
PUNCT_W = 1.0       # tie-break: whisper punctuated the word before the boundary
PAUSE_W = 1.0       # tie-break: the word before the boundary held PAUSE_CAP s or more (see held)
PAUSE_CAP = 0.4
END_PUNCT = re.compile(r"[,।.?!;:|]$")
SPLIT_AFTER = re.compile(r"[,।.?!;:]$")
SPLIT_BEFORE = {"और", "तो", "जो", "लेकिन", "या", "यानी", "यानि", "जबकि", "इसलिए", "क्योंकि",
                "जब", "तब", "वहीं", "जिससे", "अगर"}
CLAUSE_END = {"है", "हैं", "था", "थी", "थे", "हो", "हों"}
SPLIT_COST = (0, 10, 20, 40)   # punctuation, conjunction after a clause, conjunction, anything
FAR = 10.0          # seconds from its SRT time: SRT drift measured up to 5.3s on 9 parts
WRONG_SRT = 0.70    # share of the spoken skeleton the SRT accounts for, below which it is the wrong SRT


# --------------------------------------------------------------------------- inputs

def srt_cues(path: Path) -> list[dict]:
    """Cues in file order. Numbered by POSITION (1-based) and split into blocks
    exactly as tools/bind_design.py's srt_cues does, so `cue` means the same
    thing to both tools whatever the SRT's own numbering says."""
    blocks, cur = [], []
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if not line.strip():
            if cur:
                blocks.append(cur)
                cur = []
        else:
            cur.append(line)
    if cur:
        blocks.append(cur)
    out = []
    for b in (b for b in blocks if len(b) >= 3):
        m = re.match(r"\s*(\d+):(\d+):(\d+)[,.](\d+)", b[1])
        start = (int(m[1]) * 3600 + int(m[2]) * 60 + int(m[3]) + int(m[4]) / 1000) if m else None
        out.append({"n": len(out) + 1, "start": start, "text": " ".join(b[2:]).strip()})
    return out


# --------------------------------------------------------------------------- matching

ONES = ("zero one two three four five six seven eight nine ten eleven twelve thirteen "
        "fourteen fifteen sixteen seventeen eighteen nineteen").split()
TENS = "_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()
# `T₂` is said "T two" and whisper writes `T2`; spoken() has already taken
# the subscripts that are words (`₁₀` base ten, `₀` not, `⁻¹` inverse)
SCRIPT_DIGITS = str.maketrans("₀₁₂₃₄₅₆₇₈₉⁰¹²³⁴⁵⁶⁷⁸⁹", "01234567890123456789")
VOWEL = {"अ": "a", "आ": "a", "इ": "i", "ई": "i", "उ": "u", "ऊ": "u", "ए": "e", "ऐ": "e",
         "ओ": "o", "औ": "o"}


def say_int(n: int) -> str:
    if n < 20:
        return ONES[n]
    if n < 100:
        return TENS[n // 10] + ("" if n % 10 == 0 else " " + ONES[n % 10])
    if n < 1000:
        return ONES[n // 100] + " hundred" + ("" if n % 100 == 0 else " " + say_int(n % 100))
    if n < 10000:
        return say_int(n // 1000) + " thousand" + ("" if n % 1000 == 0 else " " + say_int(n % 1000))
    return " ".join(ONES[int(d)] for d in str(n))


def say_num(m: re.Match) -> str:
    whole, _, frac = m.group(0).partition(".")
    out = say_int(int(whole))
    if frac:
        out += " point " + " ".join(ONES[int(d)] for d in frac)
    return f" {out} "


def msk(text: str) -> str:
    """The skeleton used to PLACE cues. `sk` (what lines_from_edit judges by)
    plus two things it drops that decide boundaries:

      * digits, read aloud in English. Whisper writes what HeyGen's SRT spells
        out — `2.303R` for `two point three zero three R`, `0` for `zero`,
        `K2` for `k two`, and a notation SRT's `T₂` — and a digit has no
        skeleton, so a trailing `0` was free to join either caption and joined
        the wrong one (PHY-C1-SA-01).
      * a token that is only vowels keeps its first vowel: `E`, `a`, `ए` are
        whole words in a formula, and an empty skeleton cannot hold a boundary.
    """
    text = spoken(text).replace("%", " percent ").translate(SCRIPT_DIGITS)
    text = re.sub(r"\d+(?:\.\d+)?", say_num, text)
    out = []
    for tok in re.sub(r"[।,.?!;:()\"'-]", " ", text).split():
        s = skel(tok)
        if not s:
            c = next((ch for ch in tok if ch.isalpha()), "")
            s = VOWEL.get(c, c.lower() if c.isascii() else "")
        out.append(s)
    return "".join(out)


class Matcher:
    """Skeleton characters of a text matched inside a run of words: the exact
    longest common subsequence, not difflib's greedy blocks. difflib takes the
    longest block first and then cannot count a short tail after it —
    `...dffrncs d h` against `...dphrnsj dy h` scored the same with and without
    the last two words, so the boundary had nothing to hold it and slid two
    words early (CHE-C3-SA-05 cue 3).

    Bit-parallel (Crochemore et al.): one pass over the words from `a` gives
    the LCS against words[a:b] for every b at once, so the DP's many ranges
    cost one scan per start."""

    def __init__(self, wsk: list[str]):
        self.wsk = wsk
        self.runs: dict[tuple, list] = {}

    def count(self, text_sk: str, a: int, b: int) -> int:
        """Matched skeleton characters of `text_sk` against words[a:b]."""
        if not text_sk or b <= a:
            return 0
        run = self.runs.get((text_sk, a))
        if run is None:
            masks: dict[str, int] = {}
            for i, ch in enumerate(text_sk):
                masks[ch] = masks.get(ch, 0) | (1 << i)
            full = (1 << len(text_sk)) - 1
            run = self.runs[(text_sk, a)] = [masks, full, full, []]
        masks, full, v, got = run
        while len(got) < b - a:
            for ch in self.wsk[a + len(got)]:
                u = v & masks.get(ch, 0)
                v = ((v + u) | (v - u)) & full
            got.append(len(text_sk) - bin(v).count("1"))
        run[2] = v
        return got[b - a - 1]


def held(words: list[dict], i: int) -> float:
    """Seconds word i lasts beyond what its length needs, plus any gap after it.

    Whisper's word clock is gapless: a pause is not a gap between words but
    the END of the word before it, stretched (`हैं` 94.61-95.31, 0.70s, before
    a new cue on BIO-C2-LA-01). Measured on the three hand-captioned parts, a
    word that ends a caption overruns its length by a median 0.2s, a word
    inside one by 0.03s."""
    w = words[i]
    gap = float(words[i + 1]["s"]) - float(w["e"]) if i + 1 < len(words) else 0.0
    return float(w["e"]) - float(w["s"]) - (0.10 + 0.05 * len(w["w"].strip())) + max(gap, 0.0)


def boundary_bonus(words: list[dict], b: int) -> float:
    """How much a boundary before word b looks like the speaker stopping."""
    if b <= 0 or b >= len(words):
        return 0.0
    pause = min(max(held(words, b - 1), 0.0), PAUSE_CAP) / PAUSE_CAP
    punct = 1.0 if END_PUNCT.search(words[b - 1]["w"].strip()) else 0.0
    return PUNCT_W * punct + PAUSE_W * pause


def anchors(csk: list[str], wsk: list[str]) -> list[int | None]:
    """Rough first word of each cue, from one global character alignment."""
    cstr, cown, wstr, wown = [], [], [], []
    for k, s in enumerate(csk):
        cstr.append(s)
        cown += [k] * len(s)
    for i, s in enumerate(wsk):
        wstr.append(s)
        wown += [i] * len(s)
    sm = difflib.SequenceMatcher(None, "".join(cstr), "".join(wstr), autojunk=False)
    first: dict[int, int] = {}
    for a, b, n in sm.get_matching_blocks():
        for d in range(n):
            first.setdefault(cown[a + d], wown[b + d])
    return [first.get(k) for k in range(len(csk))]


def fill(est: list[int | None], csk: list[str], m: int) -> list[int]:
    """Interpolate cues that anchored nowhere by skeleton length; force order."""
    n = len(est)
    known = [(k, v) for k, v in enumerate(est) if v is not None]
    if not known:
        tot = sum(len(s) for s in csk) or n
        acc, out = 0, []
        for s in csk:
            out.append(int(m * acc / tot))
            acc += len(s) or 1
        est = out
        known = list(enumerate(est))
    out = list(est)
    for k in range(n):
        if out[k] is None:
            lo = max(((kk, v) for kk, v in known if kk < k), default=(-1, 0))
            hi = min(((kk, v) for kk, v in known if kk > k), default=(n, m))
            w = sum(len(csk[x]) or 1 for x in range(lo[0] + 1, k)) + (len(csk[lo[0]]) if lo[0] >= 0 else 0)
            span = sum(len(csk[x]) or 1 for x in range(max(lo[0], 0), hi[0]))
            out[k] = int(lo[1] + (hi[1] - lo[1]) * (w / span if span else 0))
    out[0] = 0
    for k in range(1, n):                           # monotonic, one word per cue at least
        out[k] = max(out[k], out[k - 1] + 1)
    for k in range(n - 1, 0, -1):
        out[k] = min(out[k], m - (n - k))
        out[k - 1] = min(out[k - 1], out[k] - 1)
    return out


def segment(csk: list[str], words: list[dict], mt: Matcher, est: list[int], window: int):
    """Boundaries b[0]=0 < b[1] < ... < b[n]=m maximising matched characters
    per cue inside its own range, each boundary within `window` of its anchor."""
    n, m = len(csk), len(words)
    cand = [[0]]
    for k in range(1, n):
        lo, hi = max(k, est[k] - window), min(m - (n - k), est[k] + window)
        cand.append(list(range(lo, hi + 1)))
    cand.append([m])
    NEG = float("-inf")
    f = [{0: 0.0}]
    back: list[dict] = [{}]
    for k in range(1, n + 1):
        fk, bk = {}, {}
        for b in cand[k]:
            best, arg = NEG, None
            for a, fa in f[k - 1].items():
                if a >= b or fa == NEG:
                    continue
                v = fa + mt.count(csk[k - 1], a, b)
                if v > best:
                    best, arg = v, a
            if arg is not None:
                fk[b] = best + (boundary_bonus(words, b) if k < n else 0.0)
                bk[b] = arg
        f.append(fk)
        back.append(bk)
    if m not in f[n]:
        return None
    bounds, b = [m], m
    for k in range(n, 0, -1):
        b = back[k][b]
        bounds.append(b)
    return bounds[::-1]


# --------------------------------------------------------------------------- flags

def ratio(got: str, text: str) -> float:
    """The number lines_from_edit refuses a line on."""
    return difflib.SequenceMatcher(None, sk(got), sk(text)).ratio()


def split_point(text: str, i: int, j: int, words: list[dict], mt: Matcher):
    """Where a long cue should break, chosen on the TEXT and then mapped onto
    the words by the same matching that placed the cue.

    Both halves must fit the band if any split lets them. Among those, a break
    at the cue's own punctuation beats a conjunction after a finished clause
    (`... चुका है | और इस बार ...`), which beats a bare conjunction, which beats
    anything else; nearness to the middle only orders breaks of one kind.
    Returns (split_at, left, right) or None."""
    toks = text.split()
    if len(toks) < 4 or j - i < 3:
        return None
    mid = len(text) / 2
    cands = []
    for t in range(2, len(toks) - 1):             # split BEFORE token t
        left, right = " ".join(toks[:t]), " ".join(toks[t:])
        prev = toks[t - 1].rstrip(",।.?!;:—-…\"'")
        if SPLIT_AFTER.search(toks[t - 1]):
            kind = 0
        elif toks[t] in SPLIT_BEFORE and (prev in CLAUSE_END or prev.endswith(("गा", "गी", "गे"))):
            kind = 1
        elif toks[t] in SPLIT_BEFORE:
            kind = 2
        else:
            kind = 3
        cands.append((max(len(left), len(right)) > LONG, SPLIT_COST[kind] + abs(len(left) - mid) / 2,
                      left, right))
    fit = [c for c in cands if not c[0]] or sorted(cands, key=lambda c: max(len(c[2]), len(c[3])))[:3]
    _, _, left, right = min(fit, key=lambda c: c[1])
    lsk, rsk = msk(left), msk(right)
    lw, rw = len(left.split()), len(right.split())
    share = lw / (lw + rw)
    score_best = None
    for p in range(i + 1, j + 1):
        # the matching decides; the word-count share only breaks a tie
        s = (mt.count(lsk, i, p) + mt.count(rsk, p, j + 1) + boundary_bonus(words, p)
             - 0.01 * abs((p - i) / (j + 1 - i) - share))
        if score_best is None or s > score_best[0]:
            score_best = (s, p)
    return score_best[1], left, right


def on_screen(entries: list[dict], words: list[dict], clip_end: float) -> list[float]:
    """Each caption's duration, derived exactly as lines_from_edit derives it."""
    out = []
    for k, e in enumerate(entries):
        i, j = e["w"]
        start, end = float(words[i]["s"]), float(words[j]["e"]) + TAIL
        if k + 1 < len(entries):
            ns = float(words[entries[k + 1]["w"][0]]["s"])
            end = ns - GAP if ns - float(words[j]["e"]) <= HOLD else min(end, ns - GAP)
        else:
            end = min(max(end, float(words[j]["e"])), clip_end)
        out.append(end - start)
    return out


# --------------------------------------------------------------------------- main

def draft(cues: list[dict], words: list[dict], clip_end: float):
    """Returns (entries, why-not, share of the spoken skeleton the cues account for)."""
    n, m = len(cues), len(words)
    if n == 0 or m < n:
        return None, f"{n} cue(s) and {m} word(s): cannot give every cue a word", 0.0
    csk = [msk(c["text"]) for c in cues]
    wsk = [msk(w["w"]) for w in words]
    mt = Matcher(wsk)
    est = fill(anchors(csk, wsk), csk, m)
    bounds = None
    for window in (WINDOW, 2 * WINDOW, 4 * WINDOW, m):
        bounds = segment(csk, words, mt, est, window)
        if bounds:
            break
    if not bounds:
        return None, "no contiguous segmentation found", 0.0

    entries = []
    for k, c in enumerate(cues):
        i, j = bounds[k], bounds[k + 1] - 1
        e = {"w": [i, j], "text": c["text"], "cue": c["n"]}
        got = " ".join(w["w"] for w in words[i:j + 1])
        r = ratio(got, c["text"])
        cover = mt.count(csk[k], i, j + 1) / len(csk[k]) if csk[k] else 0.0
        heard = got if len(got) <= 80 else got[:77] + "..."
        flags = []
        if cover < NOTHING:
            flags.append(f"matched nothing ({cover:.0%} of its skeleton) — placed by pauses; "
                         f"check the range against the voice; heard: {heard!r}")
        elif r < LOW:
            what = f"sim {r:.2f} < {SIM}: lines_from_edit will refuse" if r < SIM else f"sim {r:.2f}"
            placed = difflib.SequenceMatcher(None, msk(got), csk[k]).ratio()
            if placed >= LOW:
                # the gate's `sk` reads digits as nothing; the placement read them aloud
                flags.append(f"{what} — the WORDING, not the range (it matches {placed:.2f} with "
                             f"numbers read aloud): write numbers/formulae as digits or notation; "
                             f"heard: {heard!r}")
            else:
                flags.append(f"{what} — check the range; heard: {heard!r}")
        if c.get("start") is not None and abs(float(words[i]["s"]) - c["start"]) > FAR:
            flags.append(f"placed {float(words[i]['s']) - c['start']:+.1f}s from its SRT time "
                         f"(drift is normally under 5s) — check the range")
        if len(c["text"]) > LONG:
            sp = split_point(c["text"], i, j, words, mt)
            if sp:
                e["split_at"], e["split_text"] = sp[0], [sp[1], sp[2]]
                more = " (a half is still long: split again)" if max(len(sp[1]), len(sp[2])) > LONG else ""
                flags.append(f"{len(c['text'])} chars — split into [{i}, {sp[0] - 1}] + "
                             f"[{sp[0]}, {j}]{more}")
            else:
                flags.append(f"{len(c['text'])} chars — needs a split")
        e["_sim"] = r
        e["_flags"] = flags
        entries.append(e)
    readable(entries, words, clip_end)
    # align.coverage's direction: how much of what was SAID the SRT accounts for.
    # 0.91-0.98 on nine real parts; another part's SRT scores 0.33-0.40
    said = sum(len(s) for s in wsk) or 1
    share = sum(mt.count(csk[k], bounds[k], bounds[k + 1]) for k in range(n)) / said
    return entries, None, share


def readable(entries: list[dict], words: list[dict], clip_end: float):
    """Flag captions shorter than lines_from_edit's reading floor."""
    for k, (e, d) in enumerate(zip(entries, on_screen(entries, words, clip_end))):
        need = max(MIN_DUR, len(e["text"].split()) / READ_RATE)
        e["_short"] = d < need - 0.002
        if e["_short"]:
            # towards the neighbour it is spoken closer to
            i, j = e["w"]
            before = held(words, i - 1) if k > 0 else float("inf")
            after = held(words, j) if k + 1 < len(entries) else float("inf")
            other = entries[k - 1] if before <= after else entries[k + 1]
            e["_flags"].append(f"{d:.2f}s on screen, {len(e['text'].split())} words need {need:.2f}s "
                               f"— merge it with " + (f"cue {other['cue']}'s line" if "cue" in other
                                                      else "its neighbour"))


def from_words(words: list[dict], clip_end: float) -> list[dict]:
    """No SRT: whisper's own words, grouped where lines_from_words groups them."""
    from tools.lines_from_words import build
    entries, at = [], 0
    for line in build(words, clip_end):
        e = {"w": [at, at + line["words"] - 1], "text": line["text"], "_sim": 1.0,
             "_flags": ["no SRT: the wording is whisper's — correct it against the script"]}
        at += line["words"]
        entries.append(e)
    readable(entries, words, clip_end)
    return entries


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("slug")
    ap.add_argument("part", type=int)
    ap.add_argument("--out", help="default work/<slug>/out/caption_edit_part<N>.draft.json")
    ap.add_argument("--srt", help="use this SRT instead of the one inputs.json records")
    a = ap.parse_args()

    root = Path("work") / a.slug
    try:
        inputs = json.loads((root / "inputs.json").read_text(encoding="utf-8"))
        part = next(p for p in inputs["parts"] if int(p["part"]) == a.part)
        words = json.loads((root / "out" / f"words_part{a.part}.json").read_text(encoding="utf-8"))
    except (OSError, StopIteration, KeyError, ValueError) as ex:
        print(f"[FAIL] {a.slug} part {a.part}: cannot read inputs — {ex!r}")
        return 1
    clip_end = float((part.get("clip") or {}).get("duration") or words[-1]["e"])
    out = Path(a.out) if a.out else root / "out" / f"caption_edit_part{a.part}.draft.json"
    if out.name == f"caption_edit_part{a.part}.json":
        print(f"[FAIL] refusing to write {out}: that is the reviewed caption file, not a draft")
        return 1

    srt = a.srt or (part.get("captions") or {}).get("path")
    share = None
    if srt:
        try:
            cues = srt_cues(Path(srt))
        except OSError as ex:
            print(f"[FAIL] {a.slug} part {a.part}: cannot read the SRT — {ex!r}")
            return 1
        entries, why, share = draft(cues, words, clip_end)
        if entries is None:
            print(f"[FAIL] {a.slug} part {a.part}: {why}")
            return 1
    else:
        cues = []
        print(f"  no SRT for part {a.part}: falling back to whisper's words, grouped")
        entries = from_words(words, clip_end)

    # the full-cover invariant lines_from_edit checks first — never write a draft that breaks it
    nxt = 0
    for e in entries:
        if e["w"][0] != nxt or e["w"][1] < e["w"][0]:
            print(f"[FAIL] internal: range {e['w']} breaks the cover at word {nxt}")
            return 1
        nxt = e["w"][1] + 1
    if nxt != len(words):
        print(f"[FAIL] internal: ranges end at word {nxt - 1} of {len(words)}")
        return 1

    clean = []
    for e in entries:
        c = {k: v for k, v in e.items() if not k.startswith("_")}
        if e["_flags"]:
            c["flag"] = "; ".join(e["_flags"])
        clean.append(c)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("[\n" + ",\n".join(" " + json.dumps(c, ensure_ascii=False) for c in clean)
                   + "\n]\n", encoding="utf-8")

    flagged = [(k, e) for k, e in enumerate(entries) if e["_flags"]]
    refused = [(k, e) for k, e in enumerate(entries) if e["_sim"] < SIM or e["_short"]]
    sims = sorted(e["_sim"] for e in entries)
    if share is not None and share < WRONG_SRT:
        print(f"  WARNING: the SRT accounts for only {share:.0%} of the spoken words (a right SRT "
              f"scores over 90%) — is it this part's SRT? Every range below is suspect.")
    print(f"  {len(cues)} cues, {len(words)} words -> {len(entries)} entries -> {out}")
    print(f"     similarity min {sims[0]:.2f}  median {sims[len(sims) // 2]:.2f}   "
          f"flagged {len(flagged)}" + (f"   SRT accounts for {share:.0%} of the words"
                                       if share is not None else ""))
    for k, e in flagged:
        cue = f"cue {e['cue']:>2}" if "cue" in e else f"line {k:>2}"
        print(f"     {cue}  w{e['w']}  {e['_flags'][0] if len(e['_flags']) == 1 else '; '.join(e['_flags'])}")
    if refused:
        print(f"  lines_from_edit.py would REFUSE this draft as it stands: {len(refused)} line(s) "
              f"under sim {SIM} or too short to read (flagged above)")
    else:
        long_ = sum("split_at" in e or len(e["text"]) > LONG for e in entries)
        print(f"  lines_from_edit.py would accept this draft as it stands (every line sim >= {SIM}, "
              f"every line long enough to read)" + (f"; {long_} long cue(s) still need their split"
                                                     if long_ else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
