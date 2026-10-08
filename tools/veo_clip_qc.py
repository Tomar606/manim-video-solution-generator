"""Run every clip check on a batch of generated presenter scenes, and say what to reshoot.

    python tools/veo_clip_qc.py projects/<slug>/veo --aspect vertical
    python tools/veo_clip_qc.py projects/<slug>/veo --only 3 7 12

One row per scene, one verdict per scene, and a non-zero exit if anything failed.
The point is that a clip is never accepted on a glance: each of these caught a
real defect that had already shipped once.

WHAT IS CHECKED, AND WHY EACH ONE EXISTS
----------------------------------------
SHAPE     A vertical reel built from a landscape generation loses its background
          in the narrow panel. Flow's aspect setting cannot be read by the
          bridge, so the only honest check is on the downloaded file.
FACE      veo_kit/face_gate.py — measured cosine similarity to the reference
          photograph, not an opinion. "A bearded Indian man in black" is not the
          test, because the clips that failed all matched that description.
SPEECH    veo_kit/speech_qc.py with three passes — Whisper is not deterministic
          on this audio, and a single pass once failed the same file at 63%,
          22% and 59%. Three passes and the spread reported.
SPEECH    A Veo clip is always 10.01s whatever the line needs, so a line of 5.7s
SPAN      arrives with ~4s of padding. That padding is NOT a defect — it is what
          tools/reel_trim.py cuts. Judging a raw clip against a trimmed clip's
          dead-air budget fails every correct generation, which is exactly what
          the first version of this file did.
          What matters on a RAW clip is different:
            * the speech is CONTIGUOUS — a silence longer than MID_GAP inside it
              means he stopped and restarted, or the generation stitched itself;
            * the span roughly matches the line, so nothing was dropped or an
              extra sentence invented in the padding.
          Head and tail silence are reported for the trim to use, never failed.
MARK      Flow burns a translucent four-pointed sparkle into every generation
          after the fact; no prompt prevents it. tools/veo_logo_gate.py checks
          the cover once the clip is laid in — here we only record where it is.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "veo_kit"))
from syllables import verdict  # noqa: E402

# THE RATIO, NOT THE PIXELS. veo_kit/fetch.py pulls 720p because that is the real
# generation and everything above it is an upscale, so a vertical clip lands as
# 720x1280 and a landscape one as 1280x720. Checking for 1080x1920 here would
# fail every correct clip.
SHAPE = {"vertical": 9 / 16, "landscape": 16 / 9}
RATIO_TOL = 0.02
# A silence this long INSIDE the speech means he stopped and restarted.
# CALIBRATED, not picked. At 1.10 this flagged ten of twenty-three clips; every
# one of them then passed speech_qc at 83-100% coverage, so the gaps were the
# natural pauses of a teacher at a sentence boundary, not a broken generation.
# The largest such pause measured was 2.32s (s20, which reads fine), so the
# threshold sits above it. Speech content is speech_qc's job; this only catches
# a clip that visibly stopped.
MID_GAP = 2.60
# How far the measured speech span may sit from what the line needs, either way.
SPAN_TOL = 2.20


def probe(p: Path) -> dict:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
         "stream=width,height,duration", "-of", "json", str(p)],
        capture_output=True, text=True).stdout
    s = (json.loads(out).get("streams") or [{}])[0]
    return {"w": int(s.get("width", 0)), "h": int(s.get("height", 0)),
            "dur": float(s.get("duration") or 0.0)}


def speech_span(clip: Path, dur: float, needs: float) -> tuple[float, float, float, str]:
    """Where the speech sits in a raw clip, and whether it is one unbroken run.

    Returns (head, span, tail, fault). Head and tail are handed back for the
    trim to use; only a mid-gap or a span that does not match the line is a
    fault, for the reason in the module docstring.
    """
    r = subprocess.run(
        ["ffmpeg", "-v", "info", "-i", str(clip), "-vn",
         "-af", "silencedetect=noise=-32dB:d=0.18", "-f", "null", "-"],
        capture_output=True, text=True).stderr
    runs = []                                  # (silence_start, silence_end)
    start = None
    for ln in r.splitlines():
        if "silence_start:" in ln:
            start = float(ln.split("silence_start:")[1].split()[0])
        elif "silence_end:" in ln and start is not None:
            runs.append((start, float(ln.split("silence_end:")[1].split()[0])))
            start = None
    if start is not None:
        runs.append((start, dur))

    head = runs[0][1] if runs and runs[0][0] <= 0.05 else 0.0
    tail = dur - runs[-1][0] if runs and runs[-1][1] >= dur - 0.05 else 0.0
    inner = [(a, b) for a, b in runs if a > 0.05 and b < dur - 0.05]
    span = max(0.0, dur - head - tail)

    faults = []
    worst = max((b - a for a, b in inner), default=0.0)
    if worst > MID_GAP:
        faults.append(f"BROKEN: {worst:.2f}s gap mid-speech")
    if abs(span - needs) > SPAN_TOL:
        faults.append(f"span {span:.1f}s vs line {needs:.1f}s")
    return head, span, tail, "; ".join(faults)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("folder", help="projects/<slug>/veo")
    ap.add_argument("--aspect", choices=tuple(SHAPE), default="vertical")
    ap.add_argument("--only", nargs="*", type=int, default=[])
    ap.add_argument("--clips", default="clips", help="subfolder holding sNN.mp4")
    ap.add_argument("--character", default=str(ROOT / "veo_kit" / "characters" / "ritesh.json"))
    ap.add_argument("--passes", type=int, default=3)
    ap.add_argument("--skip-speech", action="store_true", help="shape/face/dead-air only")
    a = ap.parse_args()

    folder = Path(a.folder)
    lines = json.loads((folder / "lines.json").read_text(encoding="utf-8"))
    want_ratio = SHAPE[a.aspect]
    clips = folder / a.clips
    ids = sorted(int(k) for k in lines) if not a.only else sorted(a.only)

    print(f"  {'scene':6} {'shape':11} {'dur':>5} {'face':>6} {'speech':>7} "
          f"{'head':>5} {'span':>5}  notes")
    bad, missing = [], []
    for i in ids:
        clip = clips / f"s{i:02d}.mp4"
        if not clip.is_file():
            missing.append(i)
            continue
        m = probe(clip)
        shape = f"{m['w']}x{m['h']}"
        faults = []
        got = m["w"] / m["h"] if m["h"] else 0.0
        if abs(got - want_ratio) > RATIO_TOL:
            faults.append(f"NOT {a.aspect} ({shape})")
        needs = verdict(lines[str(i)])[1]
        head, span, tail, da = speech_span(clip, m["dur"], needs)
        if da:
            faults.append(da)

        face = "-"
        try:
            r = subprocess.run(
                [sys.executable, str(ROOT / "veo_kit" / "face_gate.py"), str(clip),
                 "--character", a.character, "--spread", "5"],
                capture_output=True, text=True, timeout=600)
            for ln in r.stdout.splitlines():
                if "median" in ln:
                    face = ln.split("median")[1].split()[0]
            if r.returncode != 0:
                faults.append("FACE")
        except Exception as e:                       # noqa: BLE001
            face = f"err"
            faults.append(f"face check failed: {type(e).__name__}")

        speech = "-"
        if not a.skip_speech:
            try:
                r = subprocess.run(
                    [sys.executable, str(ROOT / "veo_kit" / "speech_qc.py"), str(clip),
                     lines[str(i)], "--passes", str(a.passes)],
                    capture_output=True, text=True, timeout=1800)
                for ln in r.stdout.splitlines():
                    if "%" in ln:
                        speech = ln.strip().split()[-1]
                if r.returncode != 0:
                    faults.append("SPEECH")
            except Exception as e:                   # noqa: BLE001
                speech = "err"
                faults.append(f"speech check failed: {type(e).__name__}")

        ok = not faults
        if not ok:
            bad.append(i)
        print(f"  s{i:02d}    {shape:11} {m['dur']:5.2f} {face:>6} {speech:>7} "
              f"{head:5.2f} {span:5.2f}  {'ok' if ok else '; '.join(faults)}")

    print()
    if missing:
        print(f"  {len(missing)} clip(s) not downloaded yet: "
              f"{', '.join(f's{i:02d}' for i in missing)}")
    n = len(ids) - len(missing)
    print(f"  {n - len(bad)} of {n} passed"
          + (f"; RESHOOT {', '.join(f's{i:02d}' for i in bad)}" if bad else ""))
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
