#!/usr/bin/env python3
"""Speech spans cut on MEASURED silences, written as an SRT with no text.

    python3 tools/silence_cues.py <clip.wav> <out.srt> [--db -35] [--min 0.25]

`tools/word_timings.py` chunks the audio on SRT cue boundaries so a chunk edge
never lands in the middle of a word. A drop with NO SRT (BIO-C5-LA-01,
BIO-C4-LA-03) has nothing to chunk on, and BIO-C5-LA-01 stood in whisper's own
long-form `-osrt` output — whose 17-24s cues are the drifting segmentation the
chunking exists to avoid, and whose holes then excused themselves.

A pause the speaker actually took is a better boundary than any transcript's:
`silencedetect` finds it on the audio itself. Each output cue is one run of
speech between two silences. The cue TEXT is empty — this file is a clock for
the chunker and for `srt_gap`, never a caption source.

`word_timings.fill_gaps` excuses a hole only when this file calls it a pause AND
the audio measures quiet, so a cue break here cannot hide dropped speech.
"""
import re
import subprocess
import sys


def silences(wav, db, dmin):
    p = subprocess.run(["ffmpeg", "-nostdin", "-i", wav, "-af",
                        f"silencedetect=noise={db}dB:d={dmin}", "-f", "null", "-"],
                       capture_output=True, text=True)
    starts = [float(x) for x in re.findall(r"silence_start: (-?[\d.]+)", p.stderr)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", p.stderr)]
    dur = re.search(r"Duration: (\d+):(\d+):([\d.]+)", p.stderr)
    total = int(dur.group(1)) * 3600 + int(dur.group(2)) * 60 + float(dur.group(3))
    return list(zip(starts, ends + [total] * (len(starts) - len(ends)))), total


def stamp(t):
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def main():
    wav, out = sys.argv[1], sys.argv[2]
    args = sys.argv[3:]
    db = float(args[args.index("--db") + 1]) if "--db" in args else -35.0
    dmin = float(args[args.index("--min") + 1]) if "--min" in args else 0.25
    sil, total = silences(wav, db, dmin)
    spans, t = [], 0.0
    for s, e in sil:
        if s - t > 0.15:
            spans.append((t, s))
        t = max(t, e)
    if total - t > 0.15:
        spans.append((t, total))
    with open(out, "w", encoding="utf-8") as fh:
        for i, (s, e) in enumerate(spans, 1):
            fh.write(f"{i}\n{stamp(s)} --> {stamp(e)}\n-\n\n")
    print(f"{wav}: {len(sil)} silences -> {len(spans)} speech spans, "
          f"longest {max(e - s for s, e in spans):.2f}s  -> {out}")


if __name__ == "__main__":
    main()
