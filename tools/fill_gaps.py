"""Re-transcribe the stretches Whisper dropped, and splice them back in.

Whisper silently loses chunks of a long clip — on a 107s Faraday part the small
model dropped 34 seconds and the medium model still dropped 10.6, with no error
either time, just a hole in the word list that became a hole in the captions.
The same audio transcribes fine when handed over on its own, so this cuts each
gap out, transcribes it alone, and merges the words back at the right offset.

    python tools/fill_gaps.py inbox/clip.mp4 projects/<slug>/words_part2.json

Run it until it reports no gaps. Anything still empty afterwards is silence.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

MIN_GAP = 3.0        # shorter than this is a breath, not a dropped sentence
# A SINGLE WORD IS NEVER THIS LONG. Whisper does not always leave a dropped
# stretch as a hole BETWEEN words — on BIO-C2-SA-02 part 2 it stretched the last
# word it heard over the stretch it lost, giving "पूरा" a duration of 11.6
# seconds and "गया" 4.7, with no inter-word gap anywhere. find_gaps saw a
# continuous word list and reported nothing, while three caption lines had been
# pushed past the end of the audio — one of them with an end time BEFORE its own
# start. So an over-long word is treated as a hole too: the word keeps a
# plausible head and the rest of its span is re-transcribed.
MAX_WORD = 2.5       # seconds; longer than this is a collapsed dropped stretch
WORD_HEAD = 0.6      # how much of an over-long word is kept as the word itself
PAD = 0.35           # a little context each side so the model has a run-up


def find_gaps(words, dur=None):
    gaps = []
    for w in words:
        if w["e"] - w["s"] > MAX_WORD:
            gaps.append((round(w["s"] + WORD_HEAD, 3), w["e"]))
    if words and words[0]["s"] > MIN_GAP:
        gaps.append((0.0, words[0]["s"]))
    for i in range(len(words) - 1):
        a, b = words[i]["e"], words[i + 1]["s"]
        if b - a > MIN_GAP:
            gaps.append((a, b))
    if dur and words and dur - words[-1]["e"] > MIN_GAP:
        gaps.append((words[-1]["e"], dur))
    return gaps


def fill(clip, words_path, model="medium"):
    import whisper

    clip, words_path = Path(clip), Path(words_path)
    words = json.loads(words_path.read_text(encoding="utf-8"))
    dur = float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(clip)], capture_output=True, text=True).stdout.strip())

    # Clamp the over-long words FIRST, so the stretch they were covering is free
    # for the words recovered from it — otherwise the bogus word still spans the
    # whole hole and every caption built from it inherits the bad timing.
    for w in words:
        if w["e"] - w["s"] > MAX_WORD:
            print(f"   over-long word {w['w']!r} "
                  f"({w['s']:.2f}-{w['e']:.2f}) clamped")
            w["e"] = round(w["s"] + WORD_HEAD, 3)

    gaps = sorted(set(find_gaps(words, dur)))
    if not gaps:
        print(f"{words_path.name}: no gaps")
        return words
    print(f"{words_path.name}: {len(gaps)} gap(s) to fill")

    m = whisper.load_model(model)
    added = []
    for a, b in gaps:
        start, length = max(0.0, a - PAD), (b - a) + 2 * PAD
        with tempfile.TemporaryDirectory() as td:
            wav = Path(td) / "gap.wav"
            subprocess.run(
                ["ffmpeg", "-v", "error", "-ss", f"{start:.2f}", "-t", f"{length:.2f}",
                 "-i", str(clip), "-vn", "-ac", "1", "-ar", "16000", str(wav), "-y"],
                check=True)
            res = m.transcribe(str(wav), language="hi", word_timestamps=True,
                               condition_on_previous_text=False,
                               no_speech_threshold=0.9, logprob_threshold=-2.0)
        got = [{"w": w["word"].strip(),
                "s": round(start + w["start"], 3),
                "e": round(start + w["end"], 3)}
               for seg in res["segments"] for w in seg.get("words", [])
               if w["word"].strip()]
        # keep only what lands inside the gap — the padding is context, not content
        got = [w for w in got if a - 0.05 <= w["s"] < b + 0.05]
        added += got
        print(f"   {a:6.1f}s - {b:6.1f}s -> {len(got)} words"
              + (f"   \"{' '.join(w['w'] for w in got)[:70]}\"" if got else "   (silence)"))

    merged = sorted(words + added, key=lambda w: w["s"])
    words_path.write_text(json.dumps(merged, ensure_ascii=False, indent=2),
                          encoding="utf-8")
    left = find_gaps(merged, dur)
    print(f"   {len(words)} -> {len(merged)} words; {len(left)} gap(s) remaining")
    return merged


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    fill(sys.argv[1], sys.argv[2], *(sys.argv[3:4] or []))
