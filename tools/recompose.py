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

import re
from pathlib import Path

from src.script_parser import parse_script
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
    ("projects/che-c1-la-01/manim_code/pyq.py",
     "projects/che-c1-la-01/manim_code/pyq_composed.py",
     "projects/faraday-electrolysis/script.md"),
    ("projects/phy-c1-la-01/manim_code/pyq.py",
     "projects/phy-c1-la-01/manim_code/pyq_composed.py",
     "projects/faraday-electrolysis/script.md"),
    ("projects/che-c1-la-02/manim_code/pyq.py",
     "projects/che-c1-la-02/manim_code/pyq_composed.py",
     "projects/faraday-electrolysis/script.md"),
    ("projects/che-c2-la-05/manim_code/pyq.py",
     "projects/che-c2-la-05/manim_code/pyq_composed.py",
     "projects/faraday-electrolysis/script.md"),
    ("projects/che-c3-la-02/manim_code/pyq.py",
     "projects/che-c3-la-02/manim_code/pyq_composed.py",
     "projects/faraday-electrolysis/script.md"),
    ("projects/che-c2-la-01/manim_code/pyq.py",
     "projects/che-c2-la-01/manim_code/pyq_composed.py",
     "projects/faraday-electrolysis/script.md"),
    ("projects/che-c2-la-02/manim_code/pyq.py",
     "projects/che-c2-la-02/manim_code/pyq_composed.py",
     "projects/faraday-electrolysis/script.md"),
    ("projects/che-c2-la-03/manim_code/pyq.py",
     "projects/che-c2-la-03/manim_code/pyq_composed.py",
     "projects/faraday-electrolysis/script.md"),
    ("projects/che-c4-la-03/manim_code/pyq.py",
     "projects/che-c4-la-03/manim_code/pyq_composed.py",
     "projects/faraday-electrolysis/script.md"),
    ("projects/che-c5-la-01/manim_code/pyq.py",
     "projects/che-c5-la-01/manim_code/pyq_composed.py",
     "projects/faraday-electrolysis/script.md"),
    ("projects/che-c10-la-02/manim_code/pyq.py",
     "projects/che-c10-la-02/manim_code/pyq_composed.py",
     "projects/faraday-electrolysis/script.md"),
    ("projects/che-c10-la-01/manim_code/pyq.py",
     "projects/che-c10-la-01/manim_code/pyq_composed.py",
     "projects/faraday-electrolysis/script.md"),
    ("projects/che-c4-la-01/manim_code/pyq.py",
     "projects/che-c4-la-01/manim_code/pyq_composed.py",
     "projects/faraday-electrolysis/script.md"),
    ("projects/che-c4-la-02/manim_code/pyq.py",
     "projects/che-c4-la-02/manim_code/pyq_composed.py",
     "projects/faraday-electrolysis/script.md"),
]

# A parenthesised import spans several lines; stripping only the first left the
# continuation behind and the composed file failed with IndentationError.
# NOT stripped: src.reference_style is a plain constants module and is NOT
# inlined the way manim_helpers is, so the composed file still has to import it.
# manim is invoked from the repo root, so `src` is on the path.
STRIP = (r"^from manim import \*.*$",
         r"^import numpy as np$",
         r"^from src\.manim_helpers import \([^)]*\)",
         r"^from src\.manim_helpers import .*$")


def main(jobs=JOBS):
    for src, dst, script in jobs:
        body = Path(src).read_text(encoding="utf-8")
        # NOT re.S on the line patterns: with DOTALL, `^from manim import \*.*$`
        # matches from that line to the END OF THE FILE and silently deletes the
        # whole scene. Only the parenthesised import needs to span lines, and it
        # is bounded by `[^)]*` rather than by DOTALL.
        for pat in STRIP:
            body = re.sub(pat, "", body, flags=re.M)
        out = compose_file(parse_script(Path(script).read_text(encoding="utf-8")), body)
        Path(dst).write_text(out, encoding="utf-8")
        print(f"  {dst}  ({len(out.splitlines())} lines)")


if __name__ == "__main__":
    main()
