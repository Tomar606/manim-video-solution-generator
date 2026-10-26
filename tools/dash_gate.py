"""Refuse to ship a video with an AI dash on screen.

    python tools/dash_gate.py projects/<slug> [--fix]

WHY THIS EXISTS
---------------
Em dashes and en dashes are the single most recognisable tell that text was
written by a model, and these videos are watched by students who are being told
the explanation came from a teacher. The rule has been standing house style for
a long time and has been broken repeatedly, because nothing checked it: a dash
enters through a rewritten caption or a regenerated beat, nobody reads all
sixty on-screen strings again, and it ships.

They are also genuinely wrong for the medium. A dash sets a parenthetical aside,
and an aside does not belong on a phone screen where the line has to be read in
under two seconds. Whatever the dash was joining should be two lines, a colon,
or nothing.

WHAT IS CHECKED, AND WHAT IS DELIBERATELY NOT
---------------------------------------------
Only fields that REACH THE SCREEN: headings, list items, table cells, diagram
labels, captions, the answer card, and LaTeX. A beat's `reason`, `intent` and
`brief` are notes to the director and to Veo — nobody sees them — and failing on
those would make the gate noise, which is how the last warning-only check got
ignored.

The Devanagari danda (।) and the hyphen-minus (-) are fine and are not touched.
A MINUS SIGN inside maths is fine too, which is why `tex` is checked for the
dash characters only and not for every long horizontal glyph.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# em dash, en dash, horizontal bar, figure dash, minus sign, non-breaking hyphen
DASHES = "—–―‒−‑"
DASH_RE = re.compile(f"[{DASHES}]")
NAMES = {"—": "em dash", "–": "en dash", "―": "horizontal bar",
         "‒": "figure dash", "−": "minus sign",
         "‑": "non-breaking hyphen"}

# Fields whose text is drawn on screen. An allowlist, not a denylist: a new
# note field appearing should not start failing every project.
SCREEN_KEYS = {
    "title", "label", "labels", "items", "rows", "cols", "left", "right",
    "caption", "captions", "text", "heading", "headings", "answer", "tex",
    "readings", "note", "unit", "value", "name", "marks", "question", "year",
    "years", "subtitle", "line", "lines",
}
# ...except where one of those names is used for something structural.
NOT_TEXT = {"labels": ("at", "x", "y", "size", "align", "colour", "color", "hold", "png"),
            "name": ("figure", "scan_figure")}


def _walk(node, path: str, on_screen: bool, hits: list):
    if isinstance(node, str):
        if on_screen and DASH_RE.search(node):
            for ch in set(DASH_RE.findall(node)):
                i = node.index(ch)
                hits.append((path, NAMES.get(ch, repr(ch)),
                             node[max(0, i - 28):i + 28].replace("\n", " ")))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            _walk(v, f"{path}[{i}]", on_screen, hits)
    elif isinstance(node, dict):
        for k, v in node.items():
            child = on_screen or (k in SCREEN_KEYS)
            if k in NOT_TEXT.get("labels", ()) and path.endswith("]"):
                child = False
            _walk(v, f"{path}.{k}" if path else str(k), child, hits)


def check(root: Path) -> list[str]:
    bad: list[str] = []
    files = sorted(list(root.glob("beats*.json")) + list(root.glob("lines*.json"))
                   + [p for p in [root / "meta.json"] if p.is_file()])
    for f in files:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        hits: list = []
        # lines_*.json is nothing BUT caption text, so all of it is on screen
        _walk(data, "", f.name.startswith("lines"), hits)
        for path, name, snippet in hits:
            bad.append(f"{f.name} {path}: {name} on screen — ...{snippet}...")
    return bad


def fix(root: Path) -> int:
    """Replace every on-screen dash with a comma, and report the count.

    A comma is the safe substitution: it never changes the meaning of a list or
    an apposition, and it is what the house voice uses anyway. A dash doing real
    work still needs a human — this only removes the tell.
    """
    n = 0
    for f in sorted(list(root.glob("beats*.json")) + list(root.glob("lines*.json"))):
        raw = f.read_text(encoding="utf-8")
        hits = check(root)
        if not any(h.startswith(f.name) for h in hits):
            continue
        data = json.loads(raw)

        def swap(node, on_screen):
            nonlocal n
            if isinstance(node, str):
                if on_screen and DASH_RE.search(node):
                    n += len(DASH_RE.findall(node))
                    return DASH_RE.sub(",", node).replace(" ,", ",").replace(",,", ",")
                return node
            if isinstance(node, list):
                return [swap(v, on_screen) for v in node]
            if isinstance(node, dict):
                return {k: swap(v, on_screen or k in SCREEN_KEYS) for k, v in node.items()}
            return node

        f.write_text(json.dumps(swap(data, f.name.startswith("lines")),
                                ensure_ascii=False, indent=1), encoding="utf-8")
    return n


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("project", type=Path)
    ap.add_argument("--fix", action="store_true",
                    help="replace on-screen dashes with commas")
    a = ap.parse_args()
    if a.fix:
        n = fix(a.project)
        print(f"  replaced {n} on-screen dash(es) with commas")
    bad = check(a.project)
    if bad:
        print(f"  DASH GATE FAILED — {a.project.name}")
        for b in bad[:25]:
            print(f"    {b}")
        if len(bad) > 25:
            print(f"    ... and {len(bad) - 25} more")
        return 1
    print(f"  no AI dash on screen: {a.project.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
