"""Refuse to ship a part whose content overlaps.

`audit_layout` has always DETECTED overlaps — it wrote them to
layout_violations.json and the build printed a warning and carried on. A warning
nobody blocks on is not a check: the dry-cell electrode labels overlapped at
65%, the log said so, and the video shipped anyway.

This is the gate. Non-zero exit means the part does not get composited.

    python tools/layout_gate.py projects/<slug> <part>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# A little overlap between a label and the figure it points at is normal — the
# leader line touches the part. Text sitting on OTHER TEXT never is.
TEXT_ON_TEXT_MAX = 0.02


def check(root: Path, part: int) -> list[str]:
    f = root / "manim_code" / "layout_violations.json"
    if not f.is_file():
        return []
    data = json.loads(f.read_text(encoding="utf-8"))
    bad = []
    for p in data.get("problems", []):
        s = str(p)
        if "TEXT-ON-TEXT" in s:
            pct = 0.0
            for tok in s.split():
                if tok.endswith("%"):
                    try:
                        pct = float(tok.rstrip("%")) / 100.0
                    except ValueError:
                        pass
            if pct > TEXT_ON_TEXT_MAX:
                bad.append(s)
        elif "OUT-OF-BAND" in s or "OFF-SCREEN" in s:
            bad.append(s)
    return bad


def main() -> int:
    root, part = Path(sys.argv[1]), int(sys.argv[2])
    bad = check(root, part)
    if not bad:
        print(f"  layout ok: {root.name} p{part}")
        return 0
    print(f"  LAYOUT FAILED — {root.name} p{part} will NOT be composited:")
    for b in bad:
        print(f"    {b}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
