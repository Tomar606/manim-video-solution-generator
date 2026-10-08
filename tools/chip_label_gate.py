"""Refuse a chip whose Devanagari label sits on top of its figure.

    python tools/chip_label_gate.py <chips_spec.json> <rendered_dir> [--max 0.06]

tools/layout_gate.py already blocks this for Manim scenes, by reading the
violations the scene's own audit writes. Band chips have no such audit: the
renderer checks that content does not OVERFLOW the band and nothing else, so a
label placed at a normalised coordinate can land squarely on the diagram and
still be written out. That is how "संश्लेषण असतत" ended up lying along the lower
strand of the replication fork.

HOW IT DECIDES
--------------
Pixels, not boxes. A bounding box round the figure covers most of the panel --
the fork's arms reach three corners -- so a box test calls every label an
overlap, including the ones sitting in genuinely empty space inside that box.

So the chip is rendered TWICE: once as authored, and once with `labels` emptied.
The difference is exactly the label ink. Overlap is that ink landing where the
figure already drew something, as a fraction of the label's own area.

A small overlap is legitimate and expected: a leader line has to touch the part
it names. Text lying ON the drawing is what this refuses.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
RENDERER = ROOT / "tools/edu/renderer"
MAX_OVERLAP = 0.06          # of the label's own ink


def render(spec: list[dict], out: Path) -> None:
    f = RENDERER / "spec/chips/_gate_tmp.json"
    f.write_text(json.dumps(spec, ensure_ascii=False))
    subprocess.run(["node", "bands.mjs", "spec/chips/_gate_tmp.json", str(out)],
                   cwd=RENDERER, check=True, capture_output=True)
    f.unlink(missing_ok=True)


def main() -> int:
    spec_p, rendered = Path(sys.argv[1]), Path(sys.argv[2])
    mx = float(sys.argv[sys.argv.index("--max") + 1]) if "--max" in sys.argv else MAX_OVERLAP
    chips = json.loads(spec_p.read_text())
    # only svg chips can have this defect: the other modes lay text out in flow
    svg = [c for c in chips if c.get("mode") == "svg" and json.loads(c.get("labels") or "[]")]
    if not svg:
        print("  chip label gate: no svg chips with labels")
        return 0

    bad = []
    with tempfile.TemporaryDirectory() as td:
        bare = [dict(c, labels="[]", slug=c["slug"]) for c in svg]
        render(bare, Path(td))
        for c in svg:
            a_p, b_p = rendered / f'{c["slug"]}.png', Path(td) / f'{c["slug"]}.png'
            if not (a_p.is_file() and b_p.is_file()):
                bad.append(f'{c["slug"]}: could not render for comparison')
                continue
            A = np.asarray(Image.open(a_p).convert("RGBA")).astype(int)
            B = np.asarray(Image.open(b_p).convert("RGBA")).astype(int)
            if A.shape != B.shape:
                bad.append(f'{c["slug"]}: sizes differ, cannot compare')
                continue
            label = (np.abs(A - B).sum(axis=2) > 24)      # what the labels added
            figure = (B[..., 3] > 8)                      # what the drawing occupies
            n = int(label.sum())
            if n < 50:
                continue
            frac = float((label & figure).sum()) / n
            mark = "" if frac <= mx else "   <<< ON THE FIGURE"
            print(f'  {c["slug"]:16s} label ink {n:6d}px  on figure {frac:5.1%}{mark}')
            if frac > mx:
                bad.append(f'{c["slug"]}: {frac:.0%} of the label sits on the '
                           f"figure (limit {mx:.0%}) — move the anchor into clear "
                           f"space, or give it a leader from outside")

    if bad:
        print("CHIP LABEL GATE FAILED:")
        for b in bad:
            print(f"  {b}")
        return 1
    print("  chip label gate ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
