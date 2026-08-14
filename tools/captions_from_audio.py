"""Build the caption track from what the presenter actually says.

Captions do NOT come from the script. They cannot: a shoot takes some lines from
the current script, some from an earlier draft, and paraphrases the rest, so no
script matches the recording. Aligning the approved Faraday master to its own
clips left 49% and 42% of the spoken words with no caption at all — whole
sentences, including the formal statement of the first law, went past silently
while the caption showed something else.

The transcript is the only source that matches the audio, and it carries
word-level timing with it. So the transcript supplies the WORDS and the CLOCK,
and the script supplies the correct spelling and the frozen terminology.

    python tools/captions_from_audio.py projects/<slug>/words_part1.json \
        projects/<slug>/script_master.md projects/<slug>/lines_part1.json

Verify with `coverage` afterwards: below about 0.80 means the transcript and the
reference disagree badly enough to look at by hand.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from src.llm import complete
from tools.align import coverage

SYSTEM = """You convert a raw speech-to-text transcript of a Hindi teaching video \
into clean on-screen captions.

The transcript is what the teacher ACTUALLY said. Do not add, remove or reorder \
content — you are fixing spelling and splitting into caption lines, nothing else.

Rules:
- Output proper Devanagari. If the transcript is romanised, transliterate it.
- Fix the recogniser's spelling: "मातरा" -> "मात्रा", "पदारथ" -> "पदार्थ",
  "तुलियांक" -> "तुल्यांक", "विद्यूत" -> "विद्युत्", "अब घट्यों" -> "अपघट्यों".
- Take terminology and spelling from the reference script wherever the same idea
  appears. The reference is authoritative for TERMS, never for content: if the
  teacher said something the reference does not contain, caption what was SAID.
- Spoken formulas stay as the teacher said them, in words:
  "w barabar z guna i guna t" -> "W बराबर Z गुना i गुना t".
- Split into caption lines of 5 to 9 words — one short readable line, the length
  a person says in one breath. Never a paragraph.
- Every line carries `w`: the index of the transcript word it STARTS at.

Return ONLY a JSON array, no prose, no code fence:
[{"w": 0, "text": "..."}, {"w": 7, "text": "..."}]"""


def build(words_path, reference_path, out_path, *, gap: float = 0.35):
    words = json.loads(Path(words_path).read_text(encoding="utf-8"))
    reference = Path(reference_path).read_text(encoding="utf-8")
    numbered = " ".join(f"[{i}]{w['w']}" for i, w in enumerate(words))

    raw = complete(SYSTEM, f"""REFERENCE SCRIPT (terminology and spelling only):
{reference}

TRANSCRIPT — each word tagged with its index:
{numbered}

Caption every word of the transcript, in order, from index 0 to {len(words)-1}.""",
                   effort="high")
    raw = re.sub(r"^```(?:json)?|```$", "", raw.strip(), flags=re.M).strip()
    rows = json.loads(raw[raw.index("["):raw.rindex("]") + 1])

    lines, prev = [], -1e9
    for r in rows:
        i = max(0, min(int(r["w"]), len(words) - 1))
        t = max(words[i]["s"], prev + gap)
        lines.append({"start": round(t, 2), "text": r["text"].strip()})
        prev = t

    Path(out_path).write_text(json.dumps(lines, ensure_ascii=False, indent=2),
                              encoding="utf-8")
    cov = coverage([l["text"] for l in lines], words)
    print(f"{len(lines)} caption lines from {len(words)} spoken words; "
          f"covers {cov:.0%} of the audio -> {out_path}")
    if cov < 0.80:
        print("  WARNING: low coverage — check the transcript and the reference")
    return lines


if __name__ == "__main__":
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    build(*sys.argv[1:4])
