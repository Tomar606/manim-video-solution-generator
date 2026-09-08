"""Caption lines from a HeyGen caption export.

    python tools/lines_from_srt.py <clip.srt> <projects/slug/lines_part1.json>

Preferred over transcribing when HeyGen ships an .srt with the clip: the timings
are the renderer's own, so there is no Whisper hole to hunt and no romanised /
Devanagari coin-flip to align around.

Two things it must still do, because the export is not caption-ready:

  * **Split.** Export cues run to nine seconds and two display lines. The
    delivered house style is ~2.3s and ~7 words, so cues are cut at clause
    boundaries and the time shared out by character count.
  * **Normalise.** The export mixes "B one", "B six" and "B₂" in one file, and
    leaves Latin words the delivered captions carry in Devanagari. The series
    already settled these — B with a SUBSCRIPT digit, numerals spelled out —
    and captions that disagree between videos of the same series read as errors.

The `नोट्स बटन` form matters beyond style: `tools/answer_overlay.py` finds the
answer-page cue by matching it, so leaving "Notes button" in Latin would silently
drop the answer page off the end of the video.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

SUB = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")

WORDY = [
    (r"\bB\s*one\b", "B₁"), (r"\bB\s*two\b", "B₂"), (r"\bB\s*three\b", "B₃"),
    (r"\bB\s*six\b", "B₆"), (r"\bB\s*nine\b", "B₉"), (r"\bB\s*twelve\b", "B₁₂"),
    (r"\bB\s*(\d{1,2})\b", lambda m: "B" + m.group(1).translate(SUB)),
    (r"\bbarvi\b", "बारहवीं"),
    # ENGLISH WORDS STAY IN LATIN. These used to be transliterated into
    # Devanagari — "answer" became आंसर, "right side" became राइट साइड — and the
    # user's rule is that a word a student is used to SEEING in English should be
    # written in English: *"not आंसर it should be answer"*. The narration is
    # unaffected; this is the caption only. Words that Hindi-medium textbooks
    # genuinely print in Devanagari (विटामिन, बारहवीं) are left alone, and so is
    # a translation like last -> आखिर, which is not a transliteration at all.
    (r"\blast\b", "आखिर"),
    (r"\bvitamin\b", "विटामिन"),
    (r"\bPernicious anaemia\b", "परनिशियस एनीमिया"),
    # ... and the reverse, for English the EXPORT already wrote in Devanagari
    (r"आंसर", "answer"), (r"स्क्रीन", "screen"),
    (r"राइट\s*साइड", "right side"), (r"\bराइट\b", "right"), (r"\bसाइड\b", "side"),
    (r"नोट्स\s*बटन", "Notes button"), (r"\bनोट्स\b", "Notes"),
    (r"सिलेबस", "syllabus"), (r"\bटेबल\b", "table"), (r"\bट्रिक\b", "trick"),
    (r"बोर्ड\s*एग्ज़ाम", "board exam"), (r"\bएग्ज़ाम\b", "exam"),
    (r"\bग्रुप\b", "group"),
    (r"\b2025\b", "दो हज़ार पच्चीस"), (r"\b4 नंबर\b", "चार नंबर"),
    (r"\b4 नम्बर\b", "चार नम्बर"),
    (r"90 percent\s*\+?", "नब्बे परसेंट प्लस"),
    (r"\bsyllabus\b", "सिलेबस"),
    # The export says डर्मेटिसिस; the chip, the table and the handwritten answer
    # page all say डर्मेटाइटिस. Two spellings of one word in a single frame reads
    # as an error, and the script is the authority on terminology.
    (r"डर्मेटिसिस", "डर्मेटाइटिस"),
    # EM AND EN DASHES BECOME A PLAIN HYPHEN. The house convention is that no
    # screen text carries an em dash; the HeyGen export is full of them because
    # the script was written in a word processor. Done here rather than per
    # project so a caption track cannot ship with one again.
    (r"\s*[—–]\s*", " - "),
]
MAX_WORDS, MIN_WORDS = 10, 4


def tidy(s: str) -> str:
    s = " ".join(s.split())
    for pat, rep in WORDY:
        s = re.sub(pat, rep, s)
    return s


def parse(srt: str):
    out = []
    for block in re.split(r"\n\s*\n", srt.strip()):
        lines = [l for l in block.splitlines() if l.strip()]
        if len(lines) < 2:
            continue
        m = re.search(r"(\d+):(\d+):(\d+)[,.](\d+)\s*-->\s*(\d+):(\d+):(\d+)[,.](\d+)",
                      block)
        if not m:
            continue
        g = [int(x) for x in m.groups()]
        a = g[0] * 3600 + g[1] * 60 + g[2] + g[3] / 1000
        b = g[4] * 3600 + g[5] * 60 + g[6] + g[7] / 1000
        text = tidy(" ".join(lines[lines.index(m.group(0)) + 1:]
                             if m.group(0) in lines else lines[2:]))
        if text:
            out.append((a, b, text))
    return out


def split_cue(a, b, text):
    """Cut at clause boundaries, then share the cue's time out by length.

    Strong punctuation only, at first. Splitting on commas as readily produced
    "अब C, D," followed by "E और K...", which cuts a list in half, and stranded
    "नब्बे" on one line with "परसेंट प्लस" on the next. Commas are a last resort
    and any fragment shorter than MIN_WORDS is folded back into its neighbour.
    """
    def by(pattern, chunks):
        out = []
        for c in chunks:
            if len(c.split()) <= MAX_WORDS:
                out.append(c)
                continue
            cur = ""
            for tok in re.split(pattern, c):
                trial = (cur + " " + tok).strip()
                if cur and len(trial.split()) > MAX_WORDS:
                    out.append(cur)
                    cur = tok
                else:
                    cur = trial
            if cur:
                out.append(cur)
        return out

    parts = by(r"(?<=[।?!])\s+", [text])           # strong breaks first
    parts = by(r"(?<=,)\s+", parts)                # commas only if still long
    parts = by(r"\s+", parts)                      # and finally anywhere

    merged = []
    for p in parts:                                # no orphan fragments
        if merged and len(p.split()) < MIN_WORDS:
            merged[-1] = merged[-1] + " " + p
        else:
            merged.append(p)
    if len(merged) > 1 and len(merged[0].split()) < MIN_WORDS:
        merged[1] = merged[0] + " " + merged[1]
        merged.pop(0)
    # A caption may not OPEN on the dash that used to be an em dash. The split
    # falls where the speaker pauses, which is exactly where that dash sits, so
    # without this every other long cue starts with a stray "- ".
    merged = [re.sub(r"^-\s+", "", p) for p in merged]

    total = sum(len(p) for p in merged) or 1
    span = b - a
    out, t = [], a
    for p in merged:
        d = span * len(p) / total
        out.append({"start": round(t, 2), "end": round(t + d, 2), "text": p})
        t += d
    return out


def main():
    srt, dst = Path(sys.argv[1]), Path(sys.argv[2])
    lines = []
    for a, b, text in parse(srt.read_text()):
        lines += split_cue(a, b, text)
    for i in range(len(lines) - 1):          # butt them so nothing goes uncaptioned
        lines[i]["end"] = min(lines[i]["end"], lines[i + 1]["start"])
    dst.write_text(json.dumps(lines, ensure_ascii=False, indent=1))
    durs = [l["end"] - l["start"] for l in lines]
    print(f"{len(lines)} lines  {lines[0]['start']:.2f}s .. {lines[-1]['end']:.2f}s")
    print(f"  median {sorted(durs)[len(durs)//2]:.2f}s   longest {max(durs):.2f}s")
    print(f"  longest by words: {max(len(l['text'].split()) for l in lines)}")


if __name__ == "__main__":
    main()
