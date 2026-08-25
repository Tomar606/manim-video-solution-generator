"""Everything the scene director needs for one topic, in one compact dump.

    python tools/director_input.py che-c1-la-01

The director reads three things and they live in three places: the question (what
the exam asks the student to reproduce), the script's own `On Screen:` directions
(authored teaching intent), and the recording (the clock, and the arbiter of what
was actually said — the shoot paraphrases). Printing them together stops the
director working from the transcript alone, which is what dropped the middle of a
derivation in batch 1.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path


def dump(slug: str) -> None:
    root = Path("projects") / slug
    meta = json.loads((root / "meta.json").read_text(encoding="utf-8"))
    print(f"# {slug}")
    print(f"\n## QUESTION\n{meta.get('question', '(none recorded)')}")

    sf = root / "script_bhaag.md"
    if sf.is_file():
        s = sf.read_text(encoding="utf-8")
        vis = re.findall(r"On Screen:\s*\n([^\n“\"]*)", s)
        print(f"\n## SCRIPT'S OWN On Screen DIRECTIONS ({len(vis)})")
        for v in vis:
            if v.strip():
                print(f"  - {v.strip()}")

    for f in sorted(root.glob("lines_part[0-9].json")):
        part = int(f.stem[-1])
        L = json.loads(f.read_text(encoding="utf-8"))
        print(f"\n## PART {part} — recording ({L[-1]['start']:.0f}s, {len(L)} lines)")
        for i, l in enumerate(L):
            print(f"  [{i:3}] {l['start']:6.1f}  {l['text']}")


if __name__ == "__main__":
    for a in sys.argv[1:]:
        dump(a)
        print("\n" + "=" * 70 + "\n")


def brief(slug: str) -> None:
    """Condensed: question, script directions, and the caption timeline with
    only the lines that START a teaching move — enough to storyboard from."""
    root = Path("projects") / slug
    meta = json.loads((root / "meta.json").read_text(encoding="utf-8"))
    print(f"# {slug}\nQ: {meta.get('question','')[:200]}")
    sf = root / "script_bhaag.md"
    if sf.is_file():
        vis = re.findall(r"On Screen:\s*\n([^\n“\"]*)", sf.read_text(encoding="utf-8"))
        print("On Screen:", " | ".join(v.strip() for v in vis if v.strip())[:400])
    for f in sorted(root.glob("lines_part[0-9].json")):
        L = json.loads(f.read_text(encoding="utf-8"))
        print(f"\nPART {f.stem[-1]} ({L[-1]['start']:.0f}s)")
        for i, l in enumerate(L):
            print(f" [{i}] {l['start']:.0f} {l['text']}")
