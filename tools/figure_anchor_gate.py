"""Every diagram label must point at something that is actually drawn.

    python tools/figure_anchor_gate.py <slug>

`tools/check_labels.py` already asks whether a label is the RIGHT NAME and
whether it arrives on the caption that speaks it. Both of those can be perfect
while the leader line points into empty space, because the anchor is a pair of
fractions typed against a picture and nothing ever compared it to the picture.

That is not hypothetical. On BIO-C2-SA-02 the anchors were placed by eye and
checked by eye, and two of the fifteen were wrong:

  पेरीमेट्रियम   28px outside the organ. The perimetrium is the uterus's outer
                 serous coat, and this figure renders it as the 2px BLACK
                 OUTLINE rather than as a band of its own — so "just outside the
                 muscle" is the blank page, and the label pointed at nothing.
  फिंब्री        5px out, in the gap between two fingers of the fringe.

Neither is visible in a frame grab unless you already suspect it: the leader
ends near the right structure and the eye closes the gap. Both were found by
sampling the artwork underneath, which is what this gate does.

WHAT IT CHECKS

For every beat that draws an image figure with labels, each referenced anchor is
looked up in anchors.json, converted to a pixel, and the artwork is sampled
there. An anchor landing on the figure's own background colour FAILS.

It also resolves "#m" mirror anchors (see the template's figure loader), and for
those additionally checks that the figure really is symmetric — a mirrored
anchor is only meaningful if the structure it names exists on both sides.

WHY THE BACKGROUND IS SAMPLED, NOT ASSUMED WHITE
A figure arrives as whatever the source gave us. The corner pixel is the
background by construction for every figure in this repo (they are cut-outs on
a plain field), and sampling it beats hard-coding 255: the plates measured here
sit at 253-254, so a `== 255` test passes everything.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# How far an anchor may sit from drawn ink before it is a defect, as a fraction
# of the image's smaller side. Anti-aliased rims and 2px outlines mean an exact
# hit is too strict; a third of a percent is about 2px on the plates here.
TOL = 0.003


def _load_image(path: Path):
    try:
        from PIL import Image
        import numpy as np
    except ImportError:
        return None, None
    import numpy as np
    return np.array(Image.open(path).convert("RGB")).astype(int), np


def check(slug: str) -> int:
    proj = ROOT / "projects" / slug
    if not proj.is_dir():
        print(f"  no such project: {slug}")
        return 1
    af = proj / "anchors.json"
    beats = sorted(proj.glob("beats*part*.json"))
    if not af.is_file() or not beats:
        print(f"  SKIP  no anchors.json or no beats — nothing anchored here")
        return 0

    anchors = json.loads(af.read_text(encoding="utf-8"))
    problems, checked = [], 0

    for bf in beats:
        try:
            spec_list = json.loads(bf.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            problems.append(f"{bf.name}: unreadable ({e})")
            continue
        for spec in spec_list:
            if spec.get("type") != "figure" or spec.get("draw") != "image":
                continue
            img_path = proj / "assets" / f"{spec.get('name', 'figure')}.png"
            if not img_path.is_file():
                problems.append(f"{bf.name}: no artwork at {img_path.relative_to(ROOT)}")
                continue
            a, np = _load_image(img_path)
            if a is None:
                print("  SKIP  Pillow/numpy not available in this interpreter")
                return 0
            H, W = a.shape[:2]
            bg = a[0, 0]
            # "ink" is anything that differs from the background field.
            ink = np.abs(a - bg).sum(axis=2) > 24
            # Mirror symmetry, measured once per figure — a "#m" anchor is only
            # meaningful on a figure that draws the structure on both sides.
            sym = float(np.abs(a - a[:, ::-1]).mean())
            rad = max(2, int(TOL * min(H, W)))

            for lab in spec.get("labels", []):
                part = lab.get("part")
                if not part:
                    continue
                checked += 1
                base, mirrored = (part[:-2], True) if part.endswith("#m") else (part, False)
                if base not in anchors:
                    problems.append(f"{bf.name}: label {lab.get('text')!r} "
                                    f"names anchor {base!r}, which is not in anchors.json")
                    continue
                if mirrored and sym > 20:
                    problems.append(
                        f"{bf.name}: label {lab.get('text')!r} uses the mirror anchor "
                        f"{part!r}, but this figure is not symmetric "
                        f"(mean |image-mirror| = {sym:.1f}/255)")
                    continue
                fx, fy = anchors[base]
                if mirrored:
                    fx = 1.0 - fx
                x, y = min(W - 1, int(fx * W)), min(H - 1, int(fy * H))
                win = ink[max(0, y - rad):y + rad + 1, max(0, x - rad):x + rad + 1]
                if not win.any():
                    problems.append(
                        f"{bf.name}: label {lab.get('text')!r} points at blank page — "
                        f"anchor {part!r} at ({fx:.4f}, {fy:.4f}) = pixel ({x}, {y}) "
                        f"is background RGB{tuple(a[y, x])}, no ink within {rad}px")

    if problems:
        print(f"  {len(problems)} label(s) do not point at the drawing:")
        for p in problems:
            print(f"    - {p}")
        return 1
    print(f"  all {checked} anchored labels point at drawn structure")
    return 0


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    return check(sys.argv[1])


if __name__ == "__main__":
    raise SystemExit(main())
