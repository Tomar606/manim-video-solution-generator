#!/usr/bin/env python3
"""publish.py — assemble finished chapters into a clean, chapter-wise output tree.

Takes the raw renders in generated/clean/, applies the whiten filter (whiten.py — the blown-out
scan look of the original reference) and files them by board and chapter, mirroring the layout of
the source HTMLs:

    chapters/
      MP/Ch5/
        page-01.jpg … page-06.jpg      theory pages, in order
        dia-01.jpg  dia-02.jpg         diagram pages
        ORDER.txt                      the reading order, pages and diagrams interleaved
      Rajasthan/Ch4/…
      Common/Ch3/…                     the board-less Ch3 HTML

Only pages that have actually been rendered are published; a chapter with missing pages is
reported rather than silently published half-finished.

Usage:
  python publish.py mp-ch5      # one chapter
  python publish.py             # every chapter that has renders
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from PIL import Image

from whiten import whiten

HERE = Path(__file__).resolve().parent
CLEAN_DIR = HERE / "generated" / "clean"
CONTENT_DIR = HERE / "page-contents"
OUT_ROOT = HERE / "chapters"

BOARDS = {"mp": "MP", "rj": "Rajasthan", "up": "UP"}

CHAPTER_NAMES = {
    "ch1": "Sexual Reproduction in Flowering Plants",
    "ch2": "Human Reproduction",
    "ch3": "Reproductive Health",
    "ch4": "Principles of Inheritance and Variation",
    "ch5": "Molecular Basis of Inheritance",
    "ch6": "Evolution",
    "ch7": "Human Health and Disease",
}


def split_key(key: str):
    """mp-ch5 -> ("MP", "Ch5"); ch3 -> ("Common", "Ch3")."""
    m = re.match(r"(?:(mp|rj|up)-)?(ch\d+)$", key)
    if not m:
        return None
    board = BOARDS.get(m.group(1), "Common")
    return board, m.group(2).capitalize()


def keys_with_content():
    keys = set()
    for p in CONTENT_DIR.glob("*.md"):
        m = re.match(r"((?:mp-|rj-)?ch\d+)-(?:page|dia)-\d+$", p.stem)
        if m:
            keys.add(m.group(1))
    return sorted(keys)


def reading_order(key: str):
    """Page ids in reading order: each theory page, followed by any diagram anchored to it.

    MANIFEST.md records that order when the pages are imported; fall back to a plain sort.
    """
    manifest = HERE / "MANIFEST.md"
    if manifest.exists():
        lines = manifest.read_text(encoding="utf-8").splitlines()
        for i, line in enumerate(lines):
            if line.startswith(f"## {key} "):
                for nxt in lines[i + 1:i + 3]:
                    ids = nxt.split()
                    if ids and ids[0].startswith(key):
                        return ids
    return sorted(p.stem for p in CONTENT_DIR.glob(f"{key}-*.md"))


def publish(key: str) -> bool:
    where = split_key(key)
    if not where:
        print(f"[{key}] SKIP: not a chapter key", file=sys.stderr)
        return False
    board, chapter = where
    order = reading_order(key)
    have = [pid for pid in order if (CLEAN_DIR / f"{pid}.png").exists()]
    missing = [pid for pid in order if pid not in have]
    if not have:
        return False

    out = OUT_ROOT / board / chapter
    out.mkdir(parents=True, exist_ok=True)
    for pid in have:
        short = pid[len(key) + 1:]                      # mp-ch5-page-01 -> page-01
        whiten(Image.open(CLEAN_DIR / f"{pid}.png")).save(out / f"{short}.jpg",
                                                          format="JPEG", quality=95)
    name = CHAPTER_NAMES.get(chapter.lower(), "")
    (out / "ORDER.txt").write_text(
        f"{board} · {chapter}{' · ' + name if name else ''} — reading order\n\n"
        + "\n".join(f"{i:2d}. {pid[len(key) + 1:]}.jpg" for i, pid in enumerate(have, 1))
        + ("\n\nNOT YET RENDERED: " + " ".join(p[len(key) + 1:] for p in missing) if missing else "")
        + "\n", encoding="utf-8")

    status = f"{len(have)}/{len(order)} pages"
    print(f"[{key}] -> chapters/{board}/{chapter}/  ({status})"
          + (f"  MISSING: {' '.join(p[len(key)+1:] for p in missing)}" if missing else "  COMPLETE"))
    return True


def main() -> int:
    keys = sys.argv[1:] or keys_with_content()
    published = sum(publish(k) for k in keys)
    if not published:
        print("nothing published — no renders found in generated/clean/", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
