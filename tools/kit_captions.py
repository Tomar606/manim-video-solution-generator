"""Caption lines for a kit-pipeline project, timed to the actual audio.

    python tools/kit_captions.py <project-slug> [n-parts]

For each part: lines from the HeyGen/recording .srt (tools/lines_from_srt.py), a
Whisper word clock (OpenAI whisper-1), any hole Whisper skipped re-transcribed on its
own, then tools/retime_lines.py moves each line onto the clock.  Spoken years written
out in words ("दो हज़ार पच्चीस") are put back as digits for the screen.

Writes projects/<slug>/{lines,words}_part<n>.json and prints the lines with times.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
PY = str(ROOT / ".venv-tools/bin/python")
YEARS = {"उन्नीस सौ इक्यानवे": "1991", "दो हज़ार बाईस": "2022", "दो हज़ार तेईस": "2023", "दो हज़ार चौबीस": "2024",
         "दो हज़ार पच्चीस": "2025", "दो हज़ार छब्बीस": "2026", "दो हज़ार सत्ताईस": "2027"}


def key() -> str:
    env = dict(l.split("=", 1) for l in (ROOT / ".env").read_text().splitlines() if "=" in l and not l.startswith("#"))
    return env["OPENAI_API_KEY"].strip().strip('"')


def transcribe(path: Path, off: float = 0.0) -> list[dict]:
    for _ in range(6):
        try:
            r = requests.post("https://api.openai.com/v1/audio/transcriptions", headers={"Authorization": f"Bearer {key()}"},
                              files={"file": open(path, "rb")},
                              data={"model": "whisper-1", "language": "hi", "response_format": "verbose_json",
                                    "timestamp_granularities[]": "word"}, timeout=300)
            r.raise_for_status()
            return [{"w": x["word"], "s": round(x["start"] + off, 2), "e": round(x["end"] + off, 2)} for x in r.json()["words"]]
        except Exception:                                      # noqa: BLE001  network is flaky: retry
            time.sleep(5)
    raise SystemExit(f"whisper failed on {path}")


def part(proj: Path, n: int) -> None:
    srt, lines, words = proj / f"src/part{n}.srt", proj / f"lines_part{n}.json", proj / f"words_part{n}.json"
    subprocess.run([PY, str(ROOT / "tools/lines_from_srt.py"), str(srt), str(lines)], check=True, capture_output=True)
    audio = proj / f"work_audio_part{n}.mp3"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(proj / f"src/part{n}.mp4"), "-vn", "-ac", "1", "-ar", "16000",
                    "-b:a", "64k", str(audio)], check=True)
    W = transcribe(audio)
    for a, b in [(a["e"], b["s"]) for a, b in zip(W, W[1:]) if b["s"] - a["e"] > 4]:       # Whisper skipped this stretch
        s0, gap = max(0.0, a - 0.5), proj / "gap.mp3"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{s0}", "-t", f"{b - a + 1}", "-i", str(audio), str(gap)], check=True)
        W += [w for w in transcribe(gap, s0) if a < w["s"] < b]
        gap.unlink(missing_ok=True)
    W.sort(key=lambda x: x["s"])
    words.write_text(json.dumps(W, ensure_ascii=False, indent=1))
    (proj / f"lines_part{n}.srt.json").write_text(lines.read_text())
    r = subprocess.run([PY, str(ROOT / "tools/retime_lines.py"), str(words), str(lines)], capture_output=True, text=True)
    print(f"part {n}: " + (r.stdout.strip().splitlines() or ["?"])[0])
    L = json.loads(lines.read_text())
    for l in L:
        for spoken, digits in YEARS.items():
            l["text"] = l["text"].replace(spoken, digits)
    lines.write_text(json.dumps(L, ensure_ascii=False, indent=1))
    audio.unlink(missing_ok=True)
    for i, l in enumerate(L):
        print(f"  {i:2d} {l['start']:6.2f} {l['text'][:70]}")


def main() -> int:
    proj = ROOT / "projects" / sys.argv[1]
    for n in range(1, int(sys.argv[2] if len(sys.argv) > 2 else 1) + 1):
        part(proj, n)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
