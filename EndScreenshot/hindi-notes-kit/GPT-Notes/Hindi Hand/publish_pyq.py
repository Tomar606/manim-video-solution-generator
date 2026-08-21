#!/usr/bin/env python3
"""File the mock-up-pipeline PYQ chapters into chapters/<Board>/Ch<N>/, beside MP and Rajasthan.

    publish_pyq.py            every UP-Ch* chapter that has drawn pages
    publish_pyq.py UP-Ch1     one chapter

The MP and Rajasthan PYQ pages were built by the older direct path and published by publish.py,
which reads flat page ids out of generated/clean/. The UP pages come off the mock-up pipeline
instead, where each chapter owns its own notes/<key>/pages/ directory — so they need their own
two-line publisher rather than a special case bolted into publish.py.

The pages/*.jpg written by gen_from_mockup.py are ALREADY whitened, which is the finish asked
for here; the raw pre-whiten renders stay behind in pages/clean/ so the finish can be retuned
for free later.
"""
from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
NOTES = HERE / "notes"
OUT_ROOT = HERE / "chapters"

CHAPTER_NAMES = {
    1: "Sexual Reproduction in Flowering Plants",
    2: "Human Reproduction",
    3: "Reproductive Health",
    4: "Principles of Inheritance and Variation",
    5: "Molecular Basis of Inheritance",
    6: "Evolution",
    7: "Human Health and Disease",
    8: "Microbes in Human Welfare",
    9: "Biotechnology: Principles and Processes",
    10: "Biotechnology and its Applications",
    11: "Organisms and Populations",
    12: "Ecosystem",
    13: "Biodiversity and Conservation",
}
BOARDS = {"UP": "UP"}
NUM_RE = re.compile(r"\d+")


def publish(key: str) -> bool:
    m = re.match(r"(UP)-Ch(\d+)$", key)
    if not m:
        print(f"[{key}] SKIP: not a PYQ chapter key", file=sys.stderr)
        return False
    board, num = BOARDS[m.group(1)], int(m.group(2))

    src = NOTES / key / "pages"
    plans = NOTES / key / "mockups"
    expected = sorted(plans.glob("page-*.png"),
                      key=lambda p: [int(x) for x in NUM_RE.findall(p.stem)])
    have = [p for p in expected if (src / f"{p.stem}.jpg").exists()]
    missing = [p.stem for p in expected if not (src / f"{p.stem}.jpg").exists()]
    if not have:
        return False

    out = OUT_ROOT / board / f"Ch{num}"
    out.mkdir(parents=True, exist_ok=True)
    for p in have:
        shutil.copy2(src / f"{p.stem}.jpg", out / f"{p.stem}.jpg")

    name = CHAPTER_NAMES.get(num, "")
    (out / "ORDER.txt").write_text(
        f"{board} · Ch{num}{' · ' + name if name else ''} — reading order\n\n"
        + "\n".join(f"{i:2d}. {p.stem}.jpg" for i, p in enumerate(have, 1))
        + ("\n\nNOT YET RENDERED: " + " ".join(missing) if missing else "")
        + "\n", encoding="utf-8")

    print(f"[{key}] -> chapters/{board}/Ch{num}/  ({len(have)}/{len(expected)} pages)"
          + (f"  MISSING: {' '.join(missing)}" if missing else "  COMPLETE"))
    return True


def main() -> int:
    keys = sys.argv[1:] or sorted(
        (p.name for p in NOTES.glob("UP-Ch*") if (p / "pages").exists()),
        key=lambda k: int(NUM_RE.findall(k)[-1]))
    if not sum(publish(k) for k in keys):
        print("nothing published — no drawn pages found", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
