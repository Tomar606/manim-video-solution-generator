"""Refuse a kit reel that uses a Veo clip still carrying Flow's sparkle, or one in the wrong shape.

    python tools/kit_veo_gate.py <slug>

Flow burns a small sparkle into every clip after generation, so no prompt prevents it. The kit removes
it into projects/<slug>/veo/clean/ (tools/kit_veo.py clean), and compile.py and compose.py read the
clean copy, but when it is missing they quietly fall back to the raw download in veo/clips/, sparkle
and all. veo_logo_gate cannot see this: it reads the PYQ route's clips_part*.json, which the kit
never writes. So this gate reads the kit's own plans and checks every clip a beat uses:

  * the clean copy exists and is newer than the raw download it was made from;
  * it is vertical (taller than wide), because a landscape clip centre-cropped into the frame keeps
    a third of its width and its resolution.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def clips_used(slug: str) -> set[str]:
    used = set()
    for plan in (ROOT / "lab/kit_test").glob("plan_*.json"):
        try:
            p = json.loads(plan.read_text())
        except json.JSONDecodeError:
            continue
        if p.get("project") != slug:
            continue
        for b in p.get("beats", []):
            br = b.get("broll") or {}
            if br.get("clip"):
                used.add(br["clip"])
    return used


def size(clip: Path) -> tuple[int, int]:
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                          "-of", "csv=p=0", str(clip)], capture_output=True, text=True).stdout.strip()
    w, h = (int(x) for x in out.split(",")[:2])
    return w, h


def main() -> int:
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    slug = sys.argv[1].rstrip("/").split("/")[-1]
    veo = ROOT / "projects" / slug / "veo"
    used = clips_used(slug)
    if not used:
        print("ok no Veo clips in this reel's plans")
        return 0
    bad = []
    exact = {c for c in used if (veo.parent / "diagrams" / f"{c}.mp4").exists()}   # Manim/HTML renders: not Veo
    for c in sorted(used - exact):
        clean, raw = veo / "clean" / f"{c}.mp4", veo / "clips" / f"{c}.mp4"
        if not clean.exists():
            bad.append(f"{c}: no cleaned copy (the raw download, sparkle and all, would be used)")
            continue
        if raw.exists() and raw.stat().st_mtime > clean.stat().st_mtime:
            bad.append(f"{c}: the raw download is newer than its cleaned copy (re-run the clean step)")
        w, h = size(clean)
        if w >= h:
            bad.append(f"{c}: {w}x{h} is not vertical")
    if bad:
        print("FAIL " + "; ".join(bad))
        return 1
    print(f"ok {len(used) - len(exact)} Veo clip(s) cleaned and vertical" + (f", {len(exact)} exact render(s)" if exact else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
