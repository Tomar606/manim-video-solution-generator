"""Refuse to RENDER a beats file that will produce a broken frame.

    python tools/preflight_beats.py projects/<slug> [--batch b2]

Every rule here exists because the defect shipped and cost a render to find.
Checking the finished video is too late: a part takes minutes to render and
composite, and the same fault then has to be found by eye. These are all static
checks on the plan, so they cost nothing and run before Manim starts.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

DEV = re.compile(r"[ऀ-ॿ]")
FIGURES = {"berkeley", "dry_cell", "boiling"}      # what actually exists
MOTIONS = {"one_way", "cyclic", "settling"}        # src/veo_conform.STRATEGIES
MIN_GAP = 3                                        # captions between two beats


def _reference_exists(root: Path, name: str) -> bool:
    """Mirror of `veo_prompts.reference_for`, without importing it — this tool
    runs on machines that have no LLM stack installed, and veo_prompts pulls one
    in through src.llm."""
    figs = root / "assets" / "figures"
    return any((figs / f"{name}{sfx}").is_file()
               for sfx in ("_scan.png", "_preview.png"))


def check(root: Path, batch: str = "") -> list[str]:
    bad: list[str] = []
    pat = f"beats_b2_part[0-9].json" if batch == "b2" else "beats_part[0-9].json"
    meta = json.loads((root / "meta.json").read_text(encoding="utf-8"))
    for bf in sorted(root.glob(pat)):
        part = bf.stem[-1]
        lf = root / f"lines_part{part}.json"
        if not lf.is_file():
            bad.append(f"p{part}: no lines_part{part}.json — cannot render")
            continue
        L = json.loads(lf.read_text(encoding="utf-8"))
        if str(part) not in (meta.get("clip_end") or {}):
            bad.append(f"p{part}: meta.json has no clip_end['{part}'] — the "
                       f"render dies on KeyError partway through")
        if (meta.get("card_lines") or {}).get(str(part)) is None \
                and str(part) not in set(meta.get("no_card", [])):
            bad.append(f"p{part}: meta.json has no card_lines['{part}'] — the "
                       f"question card never clears")
        B = json.loads(bf.read_text(encoding="utf-8"))
        ats = sorted(int(b["at"]) for b in B)

        for b in B:
            at = int(b["at"])
            t = b.get("type", "?")
            where = f"p{part} @line {at} ({t})"
            if at >= len(L):
                bad.append(f"{where}: index past the end of the recording")

            # SHAPE, per beat type. A wrong shape does not crash — it renders
            # something absurd. `compare` expects ["title", ["line", ...]]; given
            # ["KMnO4", "ऑक्सीकारक"] it iterated the STRING and stacked the word
            # one letter per row, vertically, and shipped.
            if t == "compare":
                for side in ("left", "right"):
                    v = b.get(side)
                    if not (isinstance(v, list) and len(v) == 2
                            and isinstance(v[0], str) and isinstance(v[1], list)):
                        bad.append(f"{where}: '{side}' must be "
                                   f'["title", ["line", ...]] — got {str(v)[:46]}')
            if t == "points":
                if not isinstance(b.get("items"), list):
                    bad.append(f"{where}: 'items' must be a list")
                elif any(not isinstance(x, str) for x in b["items"]):
                    bad.append(f"{where}: every item must be a string")
            if t == "table":
                cols, rows = b.get("cols"), b.get("rows")
                if not isinstance(cols, list) or not isinstance(rows, list):
                    bad.append(f"{where}: 'cols' and 'rows' must be lists")
                else:
                    for r in rows:
                        cells = r if isinstance(r, list) else r.get("cells", [])
                        if len(cells) != len(cols):
                            bad.append(f"{where}: row has {len(cells)} cells for "
                                       f"{len(cols)} columns: {str(cells)[:40]}")
            if t == "chain":
                if not isinstance(b.get("items"), list) or not b.get("items"):
                    bad.append(f"{where}: 'items' must be a non-empty list")
            if t == "formula" and not isinstance(b.get("tex"), list):
                bad.append(f"{where}: 'tex' must be a list of strings")

            # maths and Devanagari in ONE string: the renderer only routes a
            # label through LaTeX when the WHOLE string is $...$, so a mixed
            # string prints its dollar signs. This shipped in the dry cell.
            for key in ("text", "label", "title", "caption"):
                v = b.get(key)
                if isinstance(v, str) and "$" in v and DEV.search(v):
                    bad.append(f"{where}: '{key}' mixes maths and Devanagari — "
                               f"split into two: {v[:40]}")
            for lab in b.get("labels", []):
                s = str(lab.get("text", ""))
                if "$" in s and DEV.search(s):
                    bad.append(f"{where}: label mixes maths and Devanagari — "
                               f"split into two: {s[:40]}")
                # a centred label straddles its anchor, so half of it lies back
                # across the figure. Anything outside the figure box must align
                # away from it.
                if float(lab.get("x", 0.5)) > 1.0 and lab.get("align") != "l":
                    bad.append(f"{where}: label right of the figure must be "
                               f"align='l' or it lies across it: {s[:30]}")
                if float(lab.get("x", 0.5)) < 0.0 and lab.get("align") != "r":
                    bad.append(f"{where}: label left of the figure must be "
                               f"align='r': {s[:30]}")

            # Devanagari inside MathTex is a LaTeX failure, not a fallback
            for tex in b.get("tex", []):
                if DEV.search(str(tex)):
                    bad.append(f"{where}: Devanagari inside maths: {str(tex)[:40]}")

            if t in ("figure", "scan_figure") and b.get("name") not in FIGURES:
                bad.append(f"{where}: no such figure {b.get('name')!r} — "
                           f"have {sorted(FIGURES)}")

            if t == "video":
                # `brief` is hand-written for the same reason a figure is: which
                # moment earns a generated clip is a judgement about the
                # question, not about a sentence. src/veo.py refuses without it
                # too, but it refuses after the bridge is up and the tab is
                # found, and finding out here costs nothing.
                if not b.get("brief"):
                    bad.append(f"{where}: a video beat needs a hand-written "
                               f"'brief' saying what has to be SEEN moving")
                if b.get("motion") and b["motion"] not in MOTIONS:
                    bad.append(f"{where}: motion {b['motion']!r} is not one of "
                               f"{sorted(MOTIONS)} — src/veo_conform.py would "
                               f"refuse it after every clip is already paid for")
                if b.get("reference") and not _reference_exists(root, b["reference"]):
                    bad.append(
                        f"{where}: reference figure {b['reference']!r} has no "
                        f"image in assets/figures/ — crop it out of the book scan "
                        f"with tools/figure_from_scan.py first")
                if b.get("sequence") is not None and not isinstance(b["sequence"], str):
                    bad.append(f"{where}: 'sequence' must be a string id shared "
                               f"with the neighbouring video beats")

            for r in b.get("reveal_at", []):
                if int(r) >= len(L):
                    bad.append(f"{where}: reveal_at {r} past the end")
                if int(r) < at:
                    bad.append(f"{where}: reveal_at {r} before its own beat")
            n_rows = len(b.get("rows", b.get("items", [])))
            if b.get("reveal_at") and n_rows and len(b["reveal_at"]) != n_rows:
                bad.append(f"{where}: {len(b['reveal_at'])} reveal times for "
                           f"{n_rows} rows")
            for a in b.get("images", []):
                if not (root / a["src"]).is_file():
                    bad.append(f"{where}: missing image {a['src']}")

        # two beats too close: the second replaces the first before it is read
        for a, z in zip(ats, ats[1:]):
            if z - a < MIN_GAP:
                bad.append(f"p{part}: beats at {a} and {z} are {z-a} captions "
                           f"apart — the second wipes the first")

        # the enlarged presenter must never reach the question card
        cw = root / f"biggrow_part{part}.json"
        cl = (meta.get("card_lines") or {}).get(part)
        if cw.is_file() and cl is not None:
            card_end = float(L[min(int(cl), len(L) - 1)]["start"])
            for a, _ in json.loads(cw.read_text(encoding="utf-8")):
                if a < card_end:
                    bad.append(f"p{part}: presenter grows at {a}s while the "
                               f"card is up until {card_end:.1f}s")
    return bad


def main() -> int:
    root = Path(sys.argv[1])
    batch = "b2" if "--batch" in sys.argv and "b2" in sys.argv else ""
    bad = check(root, batch)
    if not bad:
        print(f"  preflight ok: {root.name}")
        return 0
    print(f"  PREFLIGHT FAILED — {root.name} ({len(bad)}):")
    for b in bad:
        print(f"    {b}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
