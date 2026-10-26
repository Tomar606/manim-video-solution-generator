"""Match Hindi text to a transcript's word timings.

Shared by the caption builder and the cue re-timer. Two problems make naive
matching useless here, and both are handled by reducing every word to its
consonant skeleton:

  * Whisper returns one clip in Devanagari and another romanised, from the same
    model and settings. Dropping vowels makes "समझते" and "samajhte" comparable.
  * It misspells freely — "मातरा" for "मात्रा", "तुलियांक" for "तुल्यांक". Matras
    and halant are exactly what it gets wrong, so they are dropped too.

Alignment is global (difflib), never a per-line window search. A clip contains
lines the script lacks and vice versa, so a line has to be placed relative to
its neighbours; searched in isolation it lands on whichever similar phrase comes
first. A window search scored 2 of 30 lines on real input where the global pass
scored 22.
"""
from __future__ import annotations

import difflib
import re

# Only consonants matter. Vowel letters map to "" so "अब" and "ab" agree.
DEVA_LAT = {
    "क": "k", "ख": "kh", "ग": "g", "घ": "gh", "ङ": "n", "च": "ch", "छ": "chh",
    "ज": "j", "झ": "jh", "ञ": "n", "ट": "t", "ठ": "th", "ड": "d", "ढ": "dh",
    "ण": "n", "त": "t", "थ": "th", "द": "d", "ध": "dh", "न": "n", "प": "p",
    "फ": "ph", "ब": "b", "भ": "bh", "म": "m", "य": "y", "र": "r", "ल": "l",
    "व": "v", "श": "sh", "ष": "sh", "स": "s", "ह": "h", "ळ": "l", "ऋ": "r",
    "क़": "k", "ख़": "kh", "ग़": "g", "ज़": "j", "ड़": "d", "ढ़": "dh", "फ़": "f",
}


def skel(word: str) -> str:
    """Consonant skeleton, in latin, for either script."""
    word = re.sub(r"[ा-्ঁंःऀ-ः]", "", word)
    if any("ऀ" <= c <= "ॿ" for c in word):
        return "".join(DEVA_LAT.get(c, "") for c in word)
    return re.sub(r"[aeiou]", "", re.sub(r"[^A-Za-z]", "", word).lower())


def toks(text: str) -> list[str]:
    return [t for t in (skel(w) for w in text.split()) if t]


def anchor(lines: list[str], words: list[dict], *, min_run: int = 2):
    """Place each line on the transcript's clock.

    Returns (starts, ratio, hits) where `starts[i]` is None for a line that does
    not appear in this clip at all — which is normal, since a shoot splits one
    script across several clips.

    `min_run` ignores isolated single-token matches: one common word landing by
    chance is not evidence of position.
    """
    tw = [skel(w["w"]) for w in words]
    ctok, owner = [], []
    for i, line in enumerate(lines):
        for t in toks(line):
            ctok.append(t)
            owner.append(i)

    sm = difflib.SequenceMatcher(None, ctok, tw, autojunk=False)
    first: dict[int, float] = {}
    hits: dict[int, int] = {}
    for a, b, n in sm.get_matching_blocks():
        if n < min_run:
            continue
        for k in range(n):
            o = owner[a + k]
            hits[o] = hits.get(o, 0) + 1
            first.setdefault(o, words[b + k]["s"])

    starts = []
    for i, line in enumerate(lines):
        need = max(min_run, int(len(toks(line)) * 0.34))
        starts.append(first[i] if hits.get(i, 0) >= need else None)
    return starts, sm.ratio(), hits


def monotonic(starts: list[float], gap: float = 0.35) -> list[float]:
    """Force strictly increasing times; a caption may never precede the one before."""
    out, prev = [], -1e9
    for t in starts:
        t = max(t, prev + gap)
        out.append(round(t, 2))
        prev = t
    return out


def coverage(lines: list[str], words: list[dict]) -> float:
    """Fraction of SPOKEN words the text accounts for.

    The diagnostic that matters. Script-to-audio coverage looks fine even when
    the script is the wrong draft, because every script line does appear
    somewhere; it is the reverse direction that exposes a mismatch. On the
    Faraday clips the wrong draft covered 51% and 58% of the spoken words.
    """
    tw = [skel(w["w"]) for w in words]
    sw = [t for line in lines for t in toks(line)]
    sm = difflib.SequenceMatcher(None, tw, sw, autojunk=False)
    seen = sum(n for _, _, n in sm.get_matching_blocks())
    return seen / max(len(tw), 1)
