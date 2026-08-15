"""A short headline for each question card.

The card carries a NOTEPAPER, and paper is small. The approved reference fits
six words in three large lines; our generated titles run to fourteen, and at a
size that fits fourteen the handwriting is unreadable. So the card gets its own
headline — the exam question stays in full inside the document.

One short call per question, cached to `card_titles.json`, so a re-run of the
batch costs nothing.
"""
from __future__ import annotations

import glob, json, re, sys
from pathlib import Path
from src.llm import complete

OUT = Path("style/card_titles.json")
SYSTEM = """You write the headline that goes on a question card in a Hindi exam \
revision video — handwritten on a torn notepaper, three lines at most.

Rules:
- Devanagari only. Formulas and symbols stay as written (KMnO₄, [NiCl₄]²⁻).
- FIVE TO EIGHT WORDS. This is a hard limit; the paper is small.
- NO hyphenated compounds. "वाष्प-दाब-में-आपेक्षिक-अवनमन" is one unbreakable
  token to a line wrapper and runs off the paper at any readable size. Write it
  as separate words: "वाष्प दाब में आपेक्षिक अवनमन". A hyphen inside a single
  established term (विद्युत्-अपघटन, बायो-सेवर्ट) is fine — a chain of them is not.
- It must read like the question, not like a topic label: keep the imperative
  where there is one ("लिखिए", "समझाइए", "सिद्ध कीजिए").
- Keep the subject terminology exactly as given.

Return ONLY the headline. No quotes, no prose."""


def build(paths=None, force=False):
    cache = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
    paths = paths or sorted(glob.glob("projects/che-*/script_bhaag.md") +
                            glob.glob("projects/phy-*/script_bhaag.md"))
    for f in paths:
        slug = Path(f).parent.name
        if slug in cache and not force:
            continue
        text = Path(f).read_text(encoding="utf-8")
        title = re.sub(r"^प्रश्न\s*[—-]\s*", "", text.split("\n", 1)[0]).strip()
        full = ""
        m = re.search(r"पूरा प्रश्न:\s*\n\s*(.+)", text)
        if m:
            full = m.group(1).strip()
        head = complete(SYSTEM, f"""अध्याय का प्रश्न (पूरा):
{full or title}

वर्तमान शीर्षक ({len(title.split())} शब्द): {title}

Write the card headline, five to eight words.""",
                        provider="openai", effort="low").strip().strip('"“”')
        cache[slug] = head
        # flush after EVERY one. Writing at the end means one transient failure
        # throws away everything already paid for — that has happened here
        # before, with 24 completed segments.
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(cache, ensure_ascii=False, indent=2),
                       encoding="utf-8")
        print(f"  {slug:<15} {len(head.split())}w  {head}", flush=True)
    return cache


if __name__ == "__main__":
    c = build(force="--force" in sys.argv)
    print(f"\n{len(c)} headlines -> {OUT}")
