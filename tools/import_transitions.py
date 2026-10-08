"""Take a folder of bought transition clips into assets/transitions/.

    python tools/import_transitions.py ~/Downloads/Transitions [--prefix pack1]

Two kinds arrive in the same folder and they are used in opposite ways, so the
first thing this does is tell them apart — by measuring, not by filename:

  LEAK   (a light leak, film burn, flare): mostly BLACK, green never leads.
         Used by SCREENING it over the cut; black screens to nothing, so the
         black is the transparency. Goes to overlay/.
  WIPE   (paper tear, crumple, shape): a bright shape on CHROMA GREEN, no dark
         frames at all. Used by KEYING the green and letting the shape cover
         the frame; the cut happens while it is covered. Goes to wipe/.

The test is `mean(G - max(R,B))` over the whole clip, which is strongly positive
for a real chroma green and negative for warm light. The same measurement that
made Veo's pale wall keyable (tools/key_veo_green.py) separates these.

A PACK IS NOT A TRANSITION. These files run to thirty seconds and hold six or
seven separate leaks with black between them; screening the whole file over one
cut would play six flares over six seconds. Each run of non-black frames is
extracted as its own overlay. A leak already starts and ends at black, which is
exactly what a transition needs, so the split costs nothing.

WHAT IS REFUSED, and why it is refused HERE rather than at use: a clip with no
dark frames and no green (a looping element like a wall of clocks) is neither —
it cannot be screened and it cannot be keyed, so it would silently composite as
a grey box over the cut.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "assets" / "transitions"
FLOOR = 10.0        # mean luma below this is "black" — the gap between leaks
MIN_LEN = 0.35      # a run shorter than this is a flicker, not a transition
MAX_LEN = 4.00      # and one longer than this is an element, not a transition
PAD = 0.05          # seconds of black kept either side, so it starts from nothing


def stats(p: Path, w: int = 40, h: int = 71):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(p), "-vf", f"scale={w}:{h}",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         capture_output=True).stdout
    n = len(raw) // (w * h * 3)
    if not n:
        return None
    a = np.frombuffer(raw[:n * w * h * 3], np.uint8).reshape(n, h, w, 3).astype(np.float32)
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                "-of", "csv=p=0", str(p)], capture_output=True,
                               text=True).stdout or 0)
    R, G, B = (a[..., i].mean(axis=(1, 2)) for i in range(3))
    # per-frame share of the picture that is NOT the green backing — for a wipe
    # this sweeps from nothing to nearly all of it (or back); for a looping
    # element it barely moves, which is how the two are told apart
    lead = a[..., 1] - np.maximum(a[..., 0], a[..., 2])
    cover = (lead < 25).mean(axis=(1, 2))
    return {"n": n, "dur": dur, "lum": a.mean(axis=(1, 2, 3)),
            "green": float((G - np.maximum(R, B)).mean()),
            "cover": cover, "sweep": float(cover.max() - cover.min()),
            "fps": n / dur if dur else 30.0}


def runs(lum: np.ndarray, fps: float) -> list[tuple[float, float]]:
    on = lum > FLOOR
    out, i = [], 0
    while i < len(on):
        if not on[i]:
            i += 1
            continue
        j = i
        while j < len(on) and on[j]:
            j += 1
        out.append((i / fps, j / fps))
        i = j
    return out


def cut(src: Path, dst: Path, t0: float, t1: float) -> None:
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t0:.3f}", "-i", str(src),
                    "-t", f"{t1 - t0:.3f}", "-an", "-c:v", "libx264", "-preset", "slow",
                    "-crf", "14", "-pix_fmt", "yuv420p", str(dst)], check=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--prefix", default="")
    a = ap.parse_args()
    src = Path(a.folder).expanduser()
    files = sorted(p for p in src.rglob("*") if p.suffix.lower() in (".mp4", ".mov", ".webm"))
    if not files:
        print(f"  nothing to import from {src}")
        return 1
    (DEST / "overlay").mkdir(parents=True, exist_ok=True)
    (DEST / "wipe").mkdir(parents=True, exist_ok=True)
    made = {"overlay": [], "wipe": []}
    refused = []
    for f in files:
        s = stats(f)
        if s is None:
            refused.append((f.name, "no frames"))
            continue
        # THE WHOLE FILENAME, not the author's half of it. Two files in this
        # pack were both "Anetaprorost" and two more both "wnebe1"; trimming at
        # _ssspin gave each pair the same stem and the second silently replaced
        # the first — a paper crumple was overwritten and 36 extracted leaks
        # registered as 32. The trailing id is what makes them distinct.
        raw_stem = f.stem.replace("_ssspin.io", "").lower()
        stem = (a.prefix + "_" if a.prefix else "") + raw_stem
        stem = "".join(c if c.isalnum() else "_" for c in stem).strip("_")
        dark = float((s["lum"] < FLOOR).mean())
        if s["green"] > 25 and dark < 0.02:
            if s["sweep"] < 0.45:
                refused.append((f.name, f"on green but it never sweeps "
                                        f"(coverage moves {s['sweep'] * 100:.0f}%) — "
                                        f"a looping element, not a transition"))
                continue
            dst = DEST / "wipe" / f"{stem}.mp4"
            cut(f, dst, 0.0, s["dur"])
            made["wipe"].append(dst)
            print(f"  WIPE  {f.name[:34]:36s} -> {dst.name}  ({s['dur']:.2f}s, "
                  f"green lead {s['green']:.0f})")
            continue
        if s["green"] > 0 or dark < 0.02:
            refused.append((f.name, f"neither: green lead {s['green']:.0f}, "
                                    f"{dark * 100:.0f}% dark — not screenable, not keyable"))
            continue
        segs = [(max(0.0, t0 - PAD), min(s["dur"], t1 + PAD))
                for t0, t1 in runs(s["lum"], s["fps"])]
        segs = [(t0, t1) for t0, t1 in segs if MIN_LEN <= t1 - t0 <= MAX_LEN]
        if not segs:
            refused.append((f.name, "no run of light between "
                                    f"{MIN_LEN}s and {MAX_LEN}s"))
            continue
        for k, (t0, t1) in enumerate(segs, 1):
            dst = DEST / "overlay" / (f"{stem}_{k:02d}.mp4" if len(segs) > 1
                                      else f"{stem}.mp4")
            cut(f, dst, t0, t1)
            made["overlay"].append(dst)
        print(f"  LEAK  {f.name[:34]:36s} -> {len(segs)} overlay(s)"
              + (f", {len(runs(s['lum'], s['fps'])) - len(segs)} run(s) outside "
                 f"{MIN_LEN}-{MAX_LEN}s dropped"
                 if len(runs(s["lum"], s["fps"])) != len(segs) else ""))

    reg = DEST / "registry.json"
    doc = json.loads(reg.read_text(encoding="utf-8")) if reg.is_file() else {}
    doc["overlay"] = {"use": "screened over a cut — light leak, film burn, flare",
                      "files": sorted(str(p.relative_to(ROOT))
                                      for p in (DEST / "overlay").glob("*.mp4"))}
    doc["wipe"] = {"use": "a bright shape on chroma green; keyed, it covers the cut",
                   "files": sorted(str(p.relative_to(ROOT))
                                   for p in (DEST / "wipe").glob("*.mp4"))}
    reg.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"\n  {len(made['overlay'])} leak(s), {len(made['wipe'])} wipe(s); registry lists "
          f"{len(doc['overlay']['files'])} and {len(doc['wipe']['files'])}")
    for name, why in refused:
        print(f"  refused  {name[:40]:42s} {why}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
