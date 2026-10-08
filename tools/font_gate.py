"""Refuse to ship a video whose typeface is not the one the scene names.

    python tools/font_gate.py <slug>

WHY THIS EXISTS
---------------
`Text(font="Khand")` does not fail when Khand is missing. Pango substitutes a
system face and the render succeeds, so the only signal is that the video looks
subtly wrong — and on Devanagari, where every candidate face is unfamiliar, that
signal is easy to miss. The house fonts live in assets/fonts/ and are NOT
installed system-wide, so a scene that forgets register_fonts() is one import
away from shipping in the wrong face.

It also cost an hour of the other kind of mistake: checking it BY EYE, with a
colour mask loose enough to sweep in a neighbouring colour, and concluding the
font was wrong when it was right. A gate settles it in a way eyes cannot.

WHAT IT CHECKS
--------------
Every font named in the project's scene files resolves to a family Pango can
actually see, after the same registration the scene itself performs. A name that
does not resolve FAILS; there is no "probably fine".
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# font="X", font='X', and the FONT / UI constants a scene declares
PATTERNS = (
    re.compile(r"""font\s*=\s*["']([^"']+)["']"""),
    re.compile(r"""^\s*FONT\s*(?:,\s*FONT_W\s*)?=\s*["']([^"']+)["']""", re.M),
    re.compile(r"""^\s*UI\s*=\s*["']([^"']+)["']""", re.M),
)
# names that are not families
SKIP = {"", "sans", "serif", "monospace"}


def wanted(slug: str) -> set[str]:
    out: set[str] = set()
    for py in (ROOT / "projects" / slug / "manim_code").glob("*.py"):
        text = py.read_text(encoding="utf-8")
        for pat in PATTERNS:
            out |= {m.strip() for m in pat.findall(text)}
    return {f for f in out if f.lower() not in SKIP and not f.startswith("$")}


def available() -> set[str]:
    try:
        import manimpango
    except Exception:
        print("  ! manimpango unavailable — cannot verify fonts")
        return set()
    for ttf in sorted((ROOT / "assets" / "fonts").glob("*.ttf")):
        try:
            manimpango.register_font(str(ttf))
        except Exception:
            pass
    return {n.lower() for n in manimpango.list_fonts()}


def main() -> int:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    slug = sys.argv[1].strip("/").split("/")[-1]
    if not (ROOT / "projects" / slug).is_dir():
        print(f"  FONT GATE FAILED — no such project {slug!r} "
              f"(pass the SLUG, not a path)")
        return 1
    want, have = wanted(slug), available()
    if not want:
        print(f"  font gate: {slug} names no fonts — nothing to check")
        return 0
    bad = [f for f in sorted(want) if not any(f.lower() == h or f.lower() in h
                                              for h in have)]
    for f in sorted(want):
        print(f"    {f:28s} {'ok' if f not in bad else 'NOT AVAILABLE — would fall back'}")
    if bad:
        print(f"  FONT GATE FAILED — {slug}: {', '.join(bad)}")
        return 1
    print(f"  fonts ok: {slug}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
