"""Transcribe every clip of a reel ONCE, and keep the word timings.

    python tools/reel_words.py <slug> [--only s03] [--model small]

Writes projects/<slug>/work/words.json: {"s03": [{"w":..,"s":..,"e":..}, ...]}.

WHY THIS IS ITS OWN STEP. Three things downstream need the same word clock —
where a clip's dead air starts and stops (tools/reel_trim.py), where each
caption chunk goes (tools/reel_captions.py), and what the clip actually said
(veo_kit/speech_qc.py). Whisper on twenty-one clips is minutes of work, and
doing it three times also gives three DIFFERENT answers, because it is not
deterministic on this audio: the same file has read 63%, 22% and 59% on
consecutive passes. Transcribing once and sharing the result makes the trim and
the captions agree with each other by construction.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--only", nargs="*", default=[])
    ap.add_argument("--model", default="small")
    ap.add_argument("--refresh", action="store_true", help="re-transcribe clips already cached")
    a = ap.parse_args()

    proj = ROOT / "projects" / a.slug
    spec = json.loads((proj / "reel.json").read_text(encoding="utf-8"))
    work = proj / "work"
    work.mkdir(parents=True, exist_ok=True)
    wj = work / "words.json"
    doc = json.loads(wj.read_text(encoding="utf-8")) if wj.is_file() else {}

    import whisper
    m = None
    for s in spec["scenes"]:
        sid = s["id"]
        if a.only and sid not in a.only:
            continue
        clip = proj / "veo" / "clips" / f"{sid}.mp4"
        if not clip.is_file():
            print(f"  {sid}: no clip")
            continue
        if sid in doc and not a.refresh:
            print(f"  {sid}: cached ({len(doc[sid]['words'])} words)")
            continue
        if m is None:
            m = whisper.load_model(a.model)
        r = m.transcribe(str(clip), language="hi", condition_on_previous_text=False,
                         word_timestamps=True, fp16=False)
        words = [{"w": w["word"], "s": round(float(w["start"]), 3),
                  "e": round(float(w["end"]), 3)}
                 for seg in r["segments"] for w in seg.get("words", [])]
        dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                                    "format=duration", "-of", "csv=p=0", str(clip)],
                                   capture_output=True, text=True).stdout or 0)
        doc[sid] = {"dur": round(dur, 3), "words": words,
                    "heard": " ".join(seg["text"] for seg in r["segments"]).strip()}
        lead = words[0]["s"] if words else 0.0
        tail = dur - (words[-1]["e"] if words else dur)
        print(f"  {sid}: {len(words)} words, speech {lead:.2f}s..{dur - tail:.2f}s of "
              f"{dur:.2f}s (lead {lead:.2f}s, tail {tail:.2f}s)")
        wj.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    wj.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"\n  {len(doc)} clip(s) -> {wj.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
