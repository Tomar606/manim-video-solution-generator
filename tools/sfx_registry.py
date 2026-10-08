"""Index the sound and transition folders, and refuse what has been rejected before.

    python tools/sfx_registry.py [--transitions] [--verbose]

WHY THIS EXISTS
---------------
The sound library used to be a flat folder plus a hand-written registry, and the
knowledge about what may go in it lived in somebody's memory. That failed twice:
a synthesized sine shipped as `ding` and was sent back as "a ringtone", and a
swept tone shipped as a riser and was sent back as "a whistle". Both are
mechanically detectable, so both are detected here — at INGEST, which is the
earliest and cheapest place to catch anything.

Drop a file into the folder for the MOMENT it marks. This measures it, checks it
against that moment's rules, and rewrites `registry.json`.

WHAT IS MEASURED, AND WHAT EACH NUMBER CATCHES
----------------------------------------------
peak_offset  where the loudest moment sits. Effects with a build have to START
             EARLY so the peak lands on the event; the gate compares peak time,
             not start time, and reads this number to do it.
tonality     how much of the spectrum sits in a few bins. High means a musical
             pitch, which reads as a ringtone. `ding.wav` measures 0.73.
sweep        centroid of the second half against the first. Strongly positive
             is a riser — the "whistle" family.
bursts       separate loud events. A page RIFFLE is not one page arriving;
             `PAPER FLIP.mp3` measured six.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

SR = 22050
AUDIO = (".wav", ".mp3", ".m4a", ".aac", ".ogg", ".aif", ".aiff")
IMAGE = (".png", ".jpg", ".jpeg")
VIDEO = (".mp4", ".mov", ".webm")

# moment -> (single event?, longest it may be, one-line purpose)
ROLES: dict[str, tuple[bool, float, str]] = {
    "label-lands":   (True,  0.40, "a diagram label, list card or chip arrives"),
    "list-item":     (True,  0.40, "one item of a counted list fills in"),
    "step-resolves": (True,  1.00, "a derivation step completes; the boxed answer"),
    "card-appears":  (True,  0.80, "the question card at the head of a part"),
    "panel-arrives": (False, 1.50, "an animation panel wipes in, or away"),
    "page-arrives":  (True,  1.50, "the handwritten answer page at the end"),
    "handwriting":   (False, 4.00, "texture under the answer page as it appears"),
}
TRANSITION_ROLES = {
    "divider": "the edge between an animation panel and the presenter",
    "overlay": "a clip laid over a cut",
    "matte":   "a greyscale shape that drives a reveal",
}

TONAL_MAX = 0.30        # above this it reads as a musical pitch
SWEEP_MAX = 0.35        # above this, over SWEEP_MIN_DUR, it is a riser
SWEEP_MIN_DUR = 0.80


def measure(path: Path) -> dict | None:
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(SR),
         "-f", "f32le", "-"], capture_output=True).stdout
    a = np.frombuffer(raw, dtype=np.float32)
    if a.size < SR // 50:
        return None
    win = int(SR * 0.01)
    env = np.abs(a[:a.size // win * win].reshape(-1, win)).max(1)
    if env.max() <= 0:
        return None
    env = env / env.max()

    def centroid(x):
        if x.size < 512:
            return 0.0
        f = np.abs(np.fft.rfft(x * np.hanning(x.size)))
        return float((f * np.fft.rfftfreq(x.size, 1 / SR)).sum() / max(f.sum(), 1e-9))

    half = a.size // 2
    c1, c2 = centroid(a[:half]), centroid(a[half:])
    spec = np.abs(np.fft.rfft(a * np.hanning(a.size)))
    spec = np.sort(spec / max(spec.sum(), 1e-9))[::-1]
    loud = env > 0.25
    return {
        "seconds": round(a.size / SR, 3),
        "peak_offset": round(float(np.argmax(env)) * win / SR, 3),
        "tonality": round(float(spec[:max(1, len(spec) // 1000)].sum()), 3),
        "sweep": round((c2 - c1) / max(c1, 1e-9), 2),
        "bursts": int(np.sum(loud[1:] & ~loud[:-1])) + int(loud[0]),
        "peak_dbfs": round(float(20 * np.log10(max(np.abs(a).max(), 1e-9))), 1),
    }


def judge(role: str, m: dict) -> list[str]:
    """Why this file may not be used for this moment. Empty means it may."""
    single, longest, _ = ROLES[role]
    bad = []
    if m["tonality"] >= TONAL_MAX:
        bad.append(f"tonal {m['tonality']:.2f} — reads as a musical pitch, "
                   f"which has been sent back as 'a ringtone'")
    if m["sweep"] >= SWEEP_MAX and m["seconds"] >= SWEEP_MIN_DUR:
        bad.append(f"rising sweep {m['sweep']:+.2f} over {m['seconds']:.2f}s — "
                   f"the riser/whistle family, rejected twice")
    if m["seconds"] > longest:
        bad.append(f"{m['seconds']:.2f}s is longer than {longest:.2f}s, so it "
                   f"outlasts the thing it marks")
    if single and m["bursts"] > 2:
        bad.append(f"{m['bursts']} separate bursts — this role marks ONE event")
    return bad


def scan_sfx(root: Path, verbose: bool) -> tuple[dict, int]:
    reg, refused = {}, 0
    for role, (_, _, use) in ROLES.items():
        folder = root / "assets" / "sfx" / role
        files = sorted((p for p in folder.glob("*") if p.suffix.lower() in AUDIO),
                       key=lambda p: p.stat().st_mtime, reverse=True)
        chosen = None
        for p in files:
            m = measure(p)
            if m is None:
                print(f"  ✗ {role}/{p.name}: unreadable")
                continue
            why = judge(role, m)
            if why:
                refused += 1
                print(f"  ✗ {role}/{p.name}")
                for w in why:
                    print(f"      {w}")
                continue
            if chosen is None:
                chosen = (p, m)
                print(f"  ✓ {role}/{p.name}  {m['seconds']:.2f}s  "
                      f"peak@{m['peak_offset']:.3f}s  tonal {m['tonality']:.2f}")
            elif verbose:
                print(f"    · {role}/{p.name} (alternate)")
        if chosen:
            p, m = chosen
            reg[role] = {
                "file": str(p.relative_to(root)), "use": use,
                "seconds": m["seconds"], "peak_offset": m["peak_offset"],
                # Quiet sources need the gain doing real work: the pack's files
                # ranged from -14 to 0 dBFS, so this is not cosmetic trimming.
                "default_gain_db": round(-6.0 - max(0.0, m["peak_dbfs"]), 1),
                "measured": {k: m[k] for k in ("tonality", "sweep", "bursts")},
                "alternates": len(files) - 1,
            }
        else:
            print(f"  — {role}: nothing usable yet ({use})")

    # ALIAS THE FILENAME TOO. `tools/sfx_gate.py` looks peak_offset up by CUE
    # NAME, and every cue written before this layout existed names a file
    # ("pop", "page_swoosh"). Without the alias those lookups miss, the gate
    # falls back to an offset of 0.0, and it then checks the cue's START
    # against the event instead of its PEAK — silently passing sound that
    # lands late. The alias is what keeps old cue files honest.
    for role, entry in list(reg.items()):
        stem = Path(entry["file"]).stem
        if stem != role and stem not in reg:
            reg[stem] = dict(entry, alias_of=role)
    return reg, refused


def scan_transitions(root: Path) -> dict:
    """Index every transition folder on disk, MERGING with what is already there.

    Two things here are deliberate, and both exist because this file is not the
    only writer. `tools/import_transitions.py` populates `overlay/` and `wipe/`
    and writes the same registry.

    FOLDERS ARE DISCOVERED, not listed in code. A hardcoded role list meant a
    folder somebody else added — `wipe/`, four green-screen shape wipes — was
    not scanned, so regenerating the registry would have DELETED that key while
    reporting success.

    EXISTING DESCRIPTIONS WIN. Whoever created a role wrote the one-line `use`
    that says what goes in it; this only fills one in for a role it knows and
    that has none. Rewriting someone else's description is how the contract in
    the README quietly stops matching the registry.
    """
    dest = root / "assets" / "transitions" / "registry.json"
    existing = {}
    if dest.is_file():
        try:
            existing = json.loads(dest.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            existing = {}

    reg = {}
    folders = sorted(p for p in (root / "assets" / "transitions").iterdir()
                     if p.is_dir() and not p.name.startswith("_"))
    for folder in folders:
        role = folder.name
        files = sorted(p for p in folder.glob("*")
                       if p.suffix.lower() in IMAGE + VIDEO)
        use = (existing.get(role, {}).get("use")
               or TRANSITION_ROLES.get(role, "(no description yet)"))
        if files:
            reg[role] = {"use": use,
                         "files": [str(p.relative_to(root)) for p in files]}
            known = len(existing.get(role, {}).get("files", []))
            delta = "" if known == len(files) else f"  (was {known})"
            print(f"  ✓ {role}: {len(files)} file(s){delta}")
        else:
            print(f"  — {role}: empty ({use})")

    # A key whose folder has gone is KEPT, not dropped: another tool may have
    # written it, and silently losing it is the failure this function is
    # guarding against in the first place.
    for role, entry in existing.items():
        if role not in reg and role not in {f.name for f in folders}:
            reg[role] = entry
            print(f"  · {role}: kept (no folder on disk, written elsewhere)")
    return reg


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--transitions", action="store_true")
    ap.add_argument("--verbose", action="store_true")
    a = ap.parse_args()
    root = Path(__file__).resolve().parents[1]

    if a.transitions:
        print("transitions")
        reg = scan_transitions(root)
        dest = root / "assets" / "transitions" / "registry.json"
    else:
        print("sound effects")
        reg, refused = scan_sfx(root, a.verbose)
        dest = root / "assets" / "sfx" / "registry.json"
        if refused:
            print(f"\n  {refused} file(s) refused — see the reasons above and "
                  f"assets/sfx/README.md")
    dest.write_text(json.dumps(reg, indent=1, ensure_ascii=False) + "\n",
                    encoding="utf-8")
    print(f"\n  wrote {dest.relative_to(root)} — {len(reg)} role(s) filled")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
