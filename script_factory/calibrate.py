#!/usr/bin/env python3
"""Run the gate over the 111 shipped scripts and report what it flags.

The point is not that every shipped script passes — DEFECTS.md lists real defects
in the corpus, and the gate SHOULD catch those. The point is that the gate must not
fire on the clean ones. If a check fires on most of the corpus, that check is wrong
about the house style, not the corpus.

    python3 script_factory/calibrate.py [--show E-COUNT] [--limit 5]
"""
from __future__ import annotations

import argparse
import collections
import csv
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gate import parse, check                                    # noqa: E402

REPO = Path(__file__).resolve().parents[1]
CORPUS = REPO / "sheet_scripts"


def years_for(row: dict) -> list[str]:
    return re.findall(r"20\d{2}", row.get("year", "") or "")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--show", help="print the scripts that raised this code")
    ap.add_argument("--limit", type=int, default=6)
    a = ap.parse_args()

    rows = {r["file"].replace("sheet_scripts/", ""): r
            for r in csv.DictReader(open(CORPUS / "index.csv", encoding="utf-8"))}
    codes = collections.Counter()
    per_file: dict[str, list] = {}
    clean = blocked = 0
    examples = collections.defaultdict(list)

    for rel, row in sorted(rows.items()):
        p = CORPUS / rel
        if not p.exists():
            continue
        cat = (re.search(r"-(VS|SA|LA|NM)-", rel) or [None, ""])[1]
        script = parse(p)
        f = check(script, years=years_for(row), category=cat)   # style auto-detected
        per_file[rel] = f
        for x in f:
            codes[(x.severity, x.code)] += 1
            examples[x.code].append((rel, x.line, x.message[:80], x.text[:70]))
        if any(x.severity == "error" for x in f):
            blocked += 1
        else:
            clean += 1

    total = len(per_file)
    print(f"corpus: {total} scripts · {clean} pass the gate · {blocked} blocked by ≥1 error\n")
    print(f"{'count':>5}  {'%':>5}  code")
    for (sev, code), n in sorted(codes.items(), key=lambda kv: -kv[1]):
        print(f"{n:5d}  {n/total:5.0%}  [{sev}] {code}")

    if a.show:
        print(f"\n--- {a.show}")
        for rel, line, msg, text in examples[a.show][:a.limit]:
            print(f"  {rel} line {line}: {msg}\n      {text}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
