"""Rebuild the composed scene files from their hand-written sources.

`compose_file()` INLINES src/manim_helpers.py under a generated header that
defines THEME, CHROMA, ORIENTATION, ASSET_ROOT and the frame size. A scene must
therefore never import the helpers itself — doing so once produced an 8x8 frame
with the caption at 37% and no background at all.

So the scene source keeps its own imports for editing and type checking, and
they are stripped here. Every edit to a scene source has to be re-composed
before rendering or the render silently uses the previous version.

    python tools/recompose.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from src.script_parser import parse_script
from src.themes import resolve_theme
from src.scene_codegen import compose_file

JOBS = [
    ("projects/sanksharan/manim_code/sanksharan.py",
     "projects/sanksharan/manim_code/sank_composed.py",
     "projects/sanksharan/script.md"),
    ("projects/faraday-electrolysis/manim_code/faraday_sync.py",
     "projects/faraday-electrolysis/manim_code/far_composed.py",
     "projects/faraday-electrolysis/script.md"),
    ("projects/style-sample/manim_code/qcard.py",
     "projects/style-sample/manim_code/qcard_composed.py",
     "projects/style-sample/script.md"),
    ("projects/style-sample/manim_code/sample.py",
     "projects/style-sample/manim_code/sample_composed.py",
     "projects/style-sample/script.md"),
    ("projects/daniell-cell/manim_code/daniell.py",
     "projects/daniell-cell/manim_code/dan_composed.py",
     "projects/daniell-cell/script.md"),
]

# EVERY PYQ PROJECT, FOUND ON DISK. This used to be thirteen hand-written
# entries of identical shape, one per project — so a new project that nobody
# remembered to add here got no composed file, and the build then rendered a
# pyq_composed.py that did not exist. The scene body is the same shared
# template in every case (build_one.sh copies it in), so there is nothing to
# hand-maintain: anything with a manim_code/pyq.py is a job.
PYQ_SCRIPT = "projects/faraday-electrolysis/script.md"

# THE SCRIPT IS WHAT CARRIES THE THEME, and the theme is what paints the
# backdrop. Handing every PYQ project the same chemistry script therefore put
# flasks and test tubes behind a PHYSICS question — the subject plates exist
# (assets/backgrounds/physics.png and friends) and nothing was choosing between
# them. The subject is in each project's own meta.json, so read it.
SUBJECT_THEME = {"physics": "physics-plate", "chemistry": "chemistry-bg",
                 "biology": "biology-bg", "maths": "maths-bg",
                 "mathematics": "maths-bg"}


def _theme_for(project: Path) -> str | None:
    meta = project / "meta.json"
    if not meta.is_file():
        return None
    try:
        subject = json.loads(meta.read_text(encoding="utf-8")).get("subject", "")
    except (json.JSONDecodeError, OSError):
        return None
    return SUBJECT_THEME.get(str(subject).strip().lower())


def pyq_jobs(root=Path(".")):
    out = []
    for src in sorted(root.glob("projects/*/manim_code/pyq.py")):
        out.append((str(src), str(src.with_name("pyq_composed.py")), PYQ_SCRIPT,
                    _theme_for(src.parent.parent)))
    return out


# A parenthesised import spans several lines; stripping only the first left the
# continuation behind and the composed file failed with IndentationError.
# NOT stripped: src.reference_style is a plain constants module and is NOT
# inlined the way manim_helpers is, so the composed file still has to import it.
# manim is invoked from the repo root, so `src` is on the path.
STRIP = (r"^from manim import \*.*$",
         r"^import numpy as np$",
         r"^from src\.manim_helpers import \([^)]*\)",
         r"^from src\.manim_helpers import .*$")


def main(jobs=None):
    jobs = JOBS + pyq_jobs() if jobs is None else jobs
    for job in jobs:
        src, dst, script = job[0], job[1], job[2]
        theme = job[3] if len(job) > 3 else None
        body = Path(src).read_text(encoding="utf-8")
        # NOT re.S on the line patterns: with DOTALL, `^from manim import \*.*$`
        # matches from that line to the END OF THE FILE and silently deletes the
        # whole scene. Only the parenthesised import needs to span lines, and it
        # is bounded by `[^)]*` rather than by DOTALL.
        for pat in STRIP:
            body = re.sub(pat, "", body, flags=re.M)
        parsed = parse_script(Path(script).read_text(encoding="utf-8"))
        if theme:
            parsed.theme = resolve_theme(theme)
        out = compose_file(parsed, body)
        Path(dst).write_text(out, encoding="utf-8")
        print(f"  {dst}  ({len(out.splitlines())} lines)"
              + (f"  [{theme}]" if theme else ""))


if __name__ == "__main__":
    main()
