#!/usr/bin/env python3
"""Merge per-part design files into the two files build_spec.py reads.

    python3 tools/merge_design.py <slug> [--bound]

Reads   work/<slug>/spec/parts/design_part<N>.json   (a list of beats)
        work/<slug>/spec/parts/anchors_part<N>.json  ({"beat": [first, last]})
Writes  work/<slug>/spec/design.json, work/<slug>/spec/anchors.json

Parts are designed in parallel, by different hands. One shared design.json
edited concurrently loses whichever write lands first; one file per part cannot.
Beat names must be unique across parts. Writes are atomic.
"""
import json, os, sys
from pathlib import Path

root = Path("work") / sys.argv[1] / "spec"
# --bound: read the designs tools/bind_design.py resolved against the measured
# clock (spec/parts/bound/). A part with no bound file yet falls back to its
# authored one, so parts can be bound one at a time.
src = root / "parts"
if "--bound" in sys.argv[2:]:
    bound = root / "parts" / "bound"
    src = bound if bound.is_dir() else src
design, anchors, seen = [], {}, {}
parts = {f.name: f for f in (root / "parts").glob("design_part*.json")}
parts.update({f.name: f for f in src.glob("design_part*.json")})
for f in (parts[k] for k in sorted(parts)):
    n = f.stem.split("part")[-1]
    beats = json.loads(f.read_text(encoding="utf-8"))
    for b in beats:
        if b["type"] in seen:
            sys.exit(f"beat {b['type']} defined in both {seen[b['type']]} and {f.name}")
        seen[b["type"]] = f.name
    design += beats
    af = f.parent / f"anchors_part{n}.json"
    anchors[f"part{n}"] = json.loads(af.read_text(encoding="utf-8")) if af.is_file() else {}
    missing = set(anchors[f"part{n}"]) - {b["type"] for b in beats}
    if missing:
        sys.exit(f"part {n}: anchored beats with no design: {sorted(missing)}")
for name, obj in (("design.json", design), ("anchors.json", anchors)):
    tmp = root / f".{name}.tmp{os.getpid()}"
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(tmp, root / name)
print(f"merged {len(design)} beats across {len(anchors)} part(s)")
