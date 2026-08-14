"""Word-level timings for a presenter clip.

Everything downstream — caption text, caption timing, animation cue times — is
derived from this, so it runs first for any new HeyGen clip.

Whisper returns whatever script it feels like: of the three clips transcribed so
far it gave Devanagari for two and romanised Hindi for the third, from the same
model and the same settings. Nothing here may assume one or the other; see
`tools/align.py`, which compares consonant skeletons for exactly that reason.

    python tools/transcribe.py inbox/clip.mp4 projects/<slug>/words_part1.json
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


def transcribe(clip: str | Path, out: str | Path, model: str = "medium") -> list[dict]:
    """Word timings for one clip.

    `medium`, not `small`: on a real 107s clip the small model silently dropped
    a 34-second stretch — no error, just a hole in the middle of the word list,
    which became a hole in the captions. Verify the output covers the clip
    before using it (`gaps` below prints any).

    `condition_on_previous_text=False` stops one bad segment dragging the rest
    of the transcript with it, which is the usual cause of such a hole.
    """
    import whisper  # heavy; imported late so --help costs nothing

    clip, out = Path(clip), Path(out)
    with tempfile.TemporaryDirectory() as td:
        wav = Path(td) / "audio.wav"
        subprocess.run(
            ["ffmpeg", "-v", "error", "-i", str(clip), "-vn",
             "-ac", "1", "-ar", "16000", str(wav), "-y"], check=True)
        res = whisper.load_model(model).transcribe(
            str(wav), language="hi", word_timestamps=True,
            condition_on_previous_text=False, no_speech_threshold=0.9,
            logprob_threshold=-2.0, temperature=(0.0, 0.2, 0.4))

    words = [{"w": w["word"].strip(), "s": round(w["start"], 3), "e": round(w["end"], 3)}
             for seg in res["segments"] for w in seg.get("words", [])
             if w["word"].strip()]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(words, ensure_ascii=False, indent=2), encoding="utf-8")

    deva = sum(1 for w in words if any("ऀ" <= c <= "ॿ" for c in w["w"]))
    print(f"{clip.name}: {len(words)} words, {deva/max(len(words),1):.0%} Devanagari "
          f"-> {out}")

    # A silent hole is the failure mode that matters: the captions simply stop
    # for that stretch and nobody notices until the video is watched.
    gaps = [(words[i]["e"], words[i + 1]["s"])
            for i in range(len(words) - 1) if words[i + 1]["s"] - words[i]["e"] > 4.0]
    for a, b in gaps:
        print(f"  WARNING: {b - a:.1f}s with no words, {a:.1f}s - {b:.1f}s")
    if gaps:
        print("  -> re-run with model='large' before building captions")
    return words


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    transcribe(sys.argv[1], sys.argv[2], *(sys.argv[3:4] or []))
