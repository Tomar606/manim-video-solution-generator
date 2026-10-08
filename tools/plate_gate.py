"""Refuse a project whose backdrop is not its subject's.

    python tools/plate_gate.py <slug> [--strict]

Every subject has its own plate in assets/backgrounds/ — chemistry's navy with
flasks, biology's green with a DNA helix and a leaf, physics, maths. The plate
is carried by the THEME baked into projects/<slug>/manim_code/pyq_composed.py,
and the subject is in that project's meta.json. This checks they agree.

WHY THIS EXISTS
---------------
Four biology videos shipped on the CHEMISTRY plate — flasks and test tubes
behind a question about energy pyramids — and nobody caught it until the fifth
was delivered. tools/make_ref_scene.py composes every project by copying the
newest composed scene, which happened to belong to a chemistry project, and the
theme travels with the file. Nothing ever read the project's own subject.

This is the second time the same shape of bug has shipped: tools/recompose.py
carries a comment about flasks appearing behind a PHYSICS question, fixed there
by reading meta.json. Fixing the cause in one composer did not stop the other
composer from reintroducing it, which is exactly the case for a gate rather
than a careful author.

IT RUNS BEFORE THE RENDER, on purpose. The plate is chosen when the scene is
composed, so a mismatch is knowable then — minutes before a render and an hour
before a build. Checked only at the end, the cost of being wrong is the whole
video again.

`--strict` also fails when the subject has no plate of its own, which is the
right behaviour once every subject in the batch has one; by default an unknown
subject is reported and allowed, since a new subject legitimately has none yet.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# The same mapping tools/recompose.py uses. Kept in both rather than imported,
# because this must keep working if that module is being edited.
SUBJECT_PLATE = {
    "physics": "physics.png",
    "chemistry": "chemistry.png",
    "biology": "biology.png",
    "maths": "maths.png",
    "mathematics": "maths.png",
}


def plate_of(scene: Path) -> str | None:
    """The backdrop the composed scene will actually paint."""
    src = scene.read_text(encoding="utf-8")
    m = re.search(r"^THEME = \{.*?\}$", src, flags=re.M | re.S)
    if not m:
        return None
    hit = re.search(r"'background_image':\s*'([^']*)'", m.group(0))
    return hit.group(1) if hit else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--strict", action="store_true")
    a = ap.parse_args()
    proj = ROOT / "projects" / a.slug.strip("/").replace("projects/", "")
    meta_p = proj / "meta.json"
    scene = proj / "manim_code" / "pyq_composed.py"
    if not meta_p.is_file():
        print(f"  no meta.json at {meta_p} — cannot tell what subject this is")
        return 1
    if not scene.is_file():
        print(f"  no composed scene yet at {scene.relative_to(ROOT)} — nothing to check")
        return 0
    subject = str(json.loads(meta_p.read_text(encoding="utf-8")).get("subject", "")).strip()
    want = SUBJECT_PLATE.get(subject.lower())
    got = plate_of(scene)
    if got is None:
        print(f"  {a.slug}: the composed scene has no THEME backdrop to check")
        return 0
    got_name = Path(got).name
    if want is None:
        msg = f"  {a.slug}: subject {subject!r} has no plate of its own; using {got_name}"
        print(msg)
        return 1 if a.strict else 0
    if got_name != want:
        print(f"  PLATE GATE FAILED — {a.slug}")
        print(f"    subject is {subject}, so the backdrop should be {want}")
        print(f"    the composed scene paints {got_name}")
        print(f"    fix: re-compose with the subject's theme, or the video ships "
              f"with another subject's artwork behind it")
        return 1
    print(f"  plate ok: {a.slug} is {subject} on {got_name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
