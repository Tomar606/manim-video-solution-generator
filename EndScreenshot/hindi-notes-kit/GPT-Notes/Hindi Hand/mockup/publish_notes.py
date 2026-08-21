#!/usr/bin/env python3
"""Stage 3 — file a finished Hindi chapter the way every other chapter in GPT-Notes is filed.

    publish_notes.py Hindi-Ch7        one chapter
    publish_notes.py                  every chapter that has drawn pages

The Bio and Maths chapters all look like this, so the Hindi notes match:

    GPT-Notes/Hindi Bio Notes/Ch07 Human Health and Disease/
        generated/page-01.jpg …        the finished pages (whitened)
        generated/clean/page-01.png    the raw renders, so the finish can be retuned for free
        mockups/page-01.png            the blueprint each page was drawn from
        ORDER.txt                      page order + what is still missing

The chapter's English title comes from the matching English HTML in pulled_rj_biology, so the
folder name reads like the others ("Ch07 Human Health and Disease") rather than a bare number.
"""
from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
HAND = HERE.parent
GPT_NOTES = HAND.parent
REPO = GPT_NOTES.parent
NOTES = HAND / "notes"
SRC = REPO / "pulled_rj_biology"
OUT_ROOT = GPT_NOTES / "Hindi Bio Notes"


def english_title(ch: str) -> str:
    """'Ch7' -> 'Human Health and Disease' (from the English half of the same source)."""
    f = SRC / "English" / ch / f"{ch}.html"
    if f.exists():
        m = re.search(r"<h1[^>]*>(.*?)</h1>", f.read_text(encoding="utf-8"), re.S)
        if m:
            return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", m.group(1))).strip()
    return ""


def publish(key: str) -> bool:
    root = NOTES / key
    pages = sorted((root / "pages").glob("page-*.jpg")) if (root / "pages").exists() else []
    if not pages:
        print(f"[{key}] nothing drawn yet", file=sys.stderr)
        return False

    ch = key.split("-")[-1]                       # Hindi-Ch7 -> Ch7
    num = int(re.sub(r"\D", "", ch) or 0)
    title = english_title(ch)
    out = OUT_ROOT / (f"Ch{num:02d} {title}".strip())
    (out / "generated" / "clean").mkdir(parents=True, exist_ok=True)
    (out / "mockups").mkdir(exist_ok=True)

    for p in pages:
        shutil.copy2(p, out / "generated" / p.name)
    for p in sorted((root / "pages" / "clean").glob("*.png")):
        shutil.copy2(p, out / "generated" / "clean" / p.name)
    for p in sorted((root / "mockups").glob("*.png")):
        shutil.copy2(p, out / "mockups" / p.name)

    total = len(list((root / "mockups").glob("page-*.png")))
    drawn = {p.stem for p in pages}
    missing = [f"page-{i:02d}" for i in range(1, total + 1) if f"page-{i:02d}" not in drawn]
    (out / "ORDER.txt").write_text(
        f"Ch{num:02d} · {title} · हिन्दी — RJ Biology\n\n"
        + "\n".join(f"{i:3d}. {p.name}" for i, p in enumerate(pages, 1))
        + (f"\n\nNOT YET DRAWN ({len(missing)} of {total}): " + " ".join(missing) if missing else
           f"\n\nCOMPLETE — all {total} pages drawn.")
        + "\n", encoding="utf-8")

    print(f"[{key}] -> {out.relative_to(GPT_NOTES)}/  ({len(pages)}/{total} pages"
          + (f", missing {len(missing)})" if missing else ", COMPLETE)"))
    return True


def main() -> int:
    keys = sys.argv[1:] or sorted(p.name for p in NOTES.iterdir() if (p / "pages").exists())
    if not keys:
        print("no chapters with drawn pages", file=sys.stderr)
        return 1
    for k in keys:
        publish(k)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
