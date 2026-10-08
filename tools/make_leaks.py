"""Build the light-leak / film-burn overlays the transitions library needs.

    python tools/make_leaks.py [--size 720x1280] [--fps 30]

Writes light-on-black mp4s into assets/transitions/overlay/ and registers them,
which is the format tools/transition.py screens over a cut.

WHY THESE ARE SYNTHESISED, AND WHAT THAT COSTS
----------------------------------------------
A real film leak is photographed: light creeping around the edge of a loaded
roll, halation blooming in the emulsion, grain moving underneath. None of that
is reproduced here exactly. What IS reproduced is the shape of the event — a
warm mass that grows, blows the frame out, and recedes — which is the part that
does the job over a cut. If a stock pack is dropped into the same folder it
wins: the registry lists whatever is there and transition.py takes it by name.

WHY A LEAK IS NOT THE DECORATION THE README REFUSES
---------------------------------------------------
assets/transitions/README.md refuses decoration with no teaching job — lens
flares, vignettes, grain. A leak over a CUT is a different thing and has a real
one: consecutive generated clips never match (CLAUDE.md), so the seam between
two of them reads as a mistake. The leak is what makes the seam deliberate.
It belongs ON a cut and nowhere else; laid over a held shot it is exactly the
decoration the README is talking about.

THE SHAPE OF EACH, in one line:
  leak_warm_sweep   a warm mass crossing the frame          — scene to scene
  film_burn_corner  a hot burn eating in from a corner      — a jump in time
  halation_flash    a soft white bloom, centred and quick   — a beat inside one idea
"""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "transitions" / "overlay"

# Each entry: duration, the luma field as a geq expression, and the warm tint
# applied to it. The expressions are written against T (seconds) and D (the
# clip's own length), with a sin envelope so every leak starts and ends BLACK —
# a leak that does not reach black at both ends leaves a bright stripe at the
# join instead of hiding it.
LEAKS = {
    "leak_warm_sweep": dict(
        d=0.90, tint=(1.00, 0.58, 0.24), grain=10, blur=34,
        # a mass sweeping left to right, taller than the frame so its top and
        # bottom never show as an edge
        lum=("255*sin(PI*T/{D})*exp(-(pow(X-({x0}+{dx}*T/{D})*W,2)/(2*pow(0.30*W,2))"
             "+pow(Y-0.46*H,2)/(2*pow(0.85*H,2))))"),
        x0=-0.25, dx=1.55,
    ),
    "film_burn_corner": dict(
        d=0.75, tint=(1.00, 0.72, 0.36), grain=14, blur=26,
        # a hot spot growing out of the lower right, the way a frame catches
        # light when the gate is opened
        lum=("255*sin(PI*T/{D})*exp(-(pow(X-1.02*W,2)+pow(Y-0.92*H,2))"
             "/(2*pow((0.18+0.72*T/{D})*W,2)))"),
        x0=0.0, dx=0.0,
    ),
    "halation_flash": dict(
        d=0.50, tint=(1.00, 0.88, 0.70), grain=6, blur=44,
        lum=("255*pow(sin(PI*T/{D}),1.6)*exp(-(pow(X-0.5*W,2)/(2*pow(0.62*W,2))"
             "+pow(Y-0.48*H,2)/(2*pow(0.62*H,2))))"),
        x0=0.0, dx=0.0,
    ),
}


def build(name: str, spec: dict, size: str, fps: int) -> Path:
    d = spec["d"]
    lum = spec["lum"].format(D=f"{d:.3f}", x0=spec["x0"], dx=spec["dx"])
    r, g, b = spec["tint"]
    dst = OUT / f"{name}.mp4"
    vf = (f"geq=lum='{lum}':cb=128:cr=128,"
          f"format=gray,gblur=sigma={spec['blur']},format=rgb24,"
          f"colorchannelmixer=rr={r}:gg={g}:bb={b},"
          f"noise=alls={spec['grain']}:allf=t,format=yuv420p")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi",
                    "-i", f"color=c=black:s={size}:d={d:.3f}:r={fps}",
                    "-vf", vf, "-an", "-c:v", "libx264", "-preset", "slow",
                    "-crf", "14", "-pix_fmt", "yuv420p", str(dst)], check=True)
    return dst


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--size", default="720x1280")
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--only", nargs="*", default=[])
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    made = []
    for name, spec in LEAKS.items():
        if a.only and name not in a.only:
            continue
        p = build(name, spec, a.size, a.fps)
        made.append(p)
        print(f"  {p.relative_to(ROOT)}  {spec['d']:.2f}s  {a.size}")
    reg = ROOT / "assets" / "transitions" / "registry.json"
    doc = json.loads(reg.read_text(encoding="utf-8")) if reg.is_file() else {}
    doc["overlay"] = {
        "use": "a clip laid OVER a cut — light leak, film burn, halation",
        "files": sorted(str(p.relative_to(ROOT))
                        for p in OUT.glob("*.mp4")),
    }
    reg.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"\n  {len(made)} overlay(s); registry lists "
          f"{len(doc['overlay']['files'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
