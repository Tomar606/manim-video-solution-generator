"""Give every chip that shows the SAME figure one height and one top, per part.

    python tools/lock_chip_family.py <plan.json> <chips_spec.json>

fit_chips_above_avatar places each chip as low as it can while clearing the
presenter, measured at that chip's own moment. That is right for unrelated
graphics and WRONG for a diagram that is being built up: the presenter moves, so
consecutive chips of one figure get tops nine or thirty pixels apart, and the
figure visibly bobs between them. In BIO-C1-LA-01 part 2 the ovule was placed at
221, 230 and 223 -- three views of one diagram, at three heights.

A family is the svg a chip draws, so text chips (points, tables) are each their
own family and keep their individual fit. Within a family the top becomes the
HIGHEST any member needs, which is the only value that clears the presenter at
every one of their moments.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    plan_p, spec_p = Path(sys.argv[1]), Path(sys.argv[2])
    plan = json.loads(plan_p.read_text())
    fam = {c["slug"]: c.get("svg", f"~{c['slug']}")
           for c in json.loads(spec_p.read_text())}

    groups: dict[str, list[dict]] = {}
    for c in plan:
        groups.setdefault(fam.get(Path(c["png"]).stem, Path(c["png"]).stem), []).append(c)

    moved = 0
    for key, members in groups.items():
        if len(members) < 2:
            continue
        top = min(int(m.get("top", 380)) for m in members)
        for m in members:
            if int(m.get("top", 380)) != top:
                moved += 1
            m["top"] = top
        print(f"  {Path(key).stem:14s} {len(members)} chips -> top={top}")
    plan_p.write_text(json.dumps(plan, ensure_ascii=False, indent=1))
    print(f"  {moved} chip(s) moved so the figure holds still")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
