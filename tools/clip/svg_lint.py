#!/usr/bin/env python3
"""Check a diagram SVG against the rules the engine depends on.

    python3 tools/clip/svg_lint.py assets/svg/p2-hill.svg [...]
    python3 tools/clip/svg_lint.py --design work/<slug>/spec/parts/design_part1.json

The second form lints every SVG a part's design names AND checks that every id
its timeline animates exists in that SVG — the check validate.py makes, moved
early enough that an agent drawing one diagram can run it on its own file
instead of finding out at the spec step.

Every rule is from CLIP_VIDEO_RUNBOOK.md §4 and names the defect it prevents:

  VIEWBOX   viewBox must be "0 0 1080 470" — the stage is 1080x470 and the
            engine never rescales; anything else lands off-stage or tiny.
  TEXT      no <text>, not even in a comment. Every word comes from the spec
            so the render's text audit can verify it; a word baked into the SVG
            can be wrong forever without anything noticing.
  OPACITY   transparency is fill-opacity / stroke-opacity, never `opacity`.
            The engine drives style.opacity 0->1 on every animated id, which
            overrides the attribute: a 55% violet solution rendered as a flat
            opaque slab.
  ID        an id the timeline animates is missing from the SVG (--design).
  PREFIX    (warning) ids starting g_ / e_ / cmp_g / cmp_e / gal_ / ele_ are
            read by qa.mjs as "two topics on screen at once".

Exit 1 on any error.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

PREFIX = re.compile(r"^(cmp_g|cmp_e|gal_|ele_|g_|e_)")


def lint(svg: Path, want_ids: set[str] = frozenset()) -> tuple[list[str], list[str]]:
    err, warn = [], []
    if not svg.is_file():
        return [f"{svg}: MISSING"], []
    s = svg.read_text(encoding="utf-8")
    vb = re.search(r'<svg\b[^>]*\bviewBox\s*=\s*"([^"]+)"', s)
    if not vb or vb.group(1).split() != ["0", "0", "1080", "470"]:
        err.append(f"VIEWBOX  viewBox is {vb.group(1)!r}" if vb else "VIEWBOX  no viewBox on <svg>")
    if re.search(r"<\s*text\b", s, re.I):
        err.append("TEXT     contains `<text` (words come from the spec, never the SVG)")
    for m in re.finditer(r'(?<![-\w])opacity\s*[=:]\s*"?([\d.]+)', s):
        if float(m.group(1)) < 1:
            err.append(f"OPACITY  `opacity {m.group(1)}` — use fill-opacity/stroke-opacity; "
                       "the engine overrides `opacity` on animated ids")
            break
    ids = set(re.findall(r'\bid\s*=\s*"([^"]+)"', s))
    for i in sorted(want_ids - ids):
        err.append(f"ID       timeline animates #{i}, which is not in the SVG")
    for i in sorted(ids):
        if PREFIX.match(i):
            warn.append(f"PREFIX   #{i} — qa.mjs reads this prefix as one side of a comparison")
    return err, warn


def from_design(path: Path) -> list[tuple[Path, set[str]]]:
    root = path.resolve().parents[2]            # work/<slug>/spec/parts/x.json -> work/<slug>
    out: dict[Path, set[str]] = {}
    for beat in json.loads(path.read_text(encoding="utf-8")):
        d = beat.get("diagram") or {}
        if not d.get("asset"):
            continue
        ids = {a["id"] for a in d.get("timeline", []) if a.get("id")} | set(d.get("carry_over", []))
        out.setdefault(root / d["asset"], set()).update(ids)
    return list(out.items())


def main(argv: list[str]) -> int:
    if not argv:
        sys.exit(__doc__)
    if argv[0] == "--design":
        items = from_design(Path(argv[1]))
        if not items:
            print(f"  {argv[1]}: no diagrams to check")
            return 0
    else:
        items = [(Path(a), set()) for a in argv]
    bad = 0
    for svg, ids in items:
        err, warn = lint(svg, ids)
        tag = "FAIL" if err else "ok  "
        print(f"  {tag} {svg}")
        for e in err:
            print(f"       X {e}")
        for w in warn:
            print(f"       ! {w}")
        bad += bool(err)
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
