"""Derive caption timings from the HeyGen avatar clip.

The avatar sets the clock. Its audio is what the student hears, so the caption
on screen must be the line the presenter is saying at that moment, and the
animation must hold until that line is finished — not the other way round.

Two ways in, best first:

1. **A caption file from HeyGen** (`.srt` or `.vtt`). Exact, because it comes
   from the same synthesis that produced the audio. Ask for this.
2. **The clip's duration alone.** Timings are apportioned by *syllable-ish*
   weight rather than word count, because Hindi words vary enormously in
   spoken length — "और" and "व्युत्क्रमानुपाती" are one word each and nowhere
   near the same duration. Devanagari vowel signs are counted, which tracks
   spoken length far better than characters or words.

Either way the output is the same: one ``CaptionCue`` per spoken line, which the
scene replays with ``self.wait()`` so the visuals land on the narration.
"""
from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

# Devanagari vowel signs and independent vowels — one per spoken syllable,
# near enough. Consonants without a sign carry the inherent 'a'.
_MATRA = re.compile(r"[ा-ौॢॣ]")
_INDEP_VOWEL = re.compile(r"[ऄ-औ]")
_CONSONANT = re.compile(r"[क-हक़-य़]")
_HALANT = re.compile(r"्")


def syllables(text: str) -> int:
    """Rough spoken length of a Devanagari line, in syllables.

    Consonants each carry an inherent vowel unless a halant kills it; explicit
    vowel signs and independent vowels add their own. Latin fragments fall back
    to vowel groups so "two-ell" and "Part 1" still count for something.
    """
    n = (len(_CONSONANT.findall(text))
         - len(_HALANT.findall(text))
         + len(_INDEP_VOWEL.findall(text)))
    n += len(re.findall(r"[aeiouAEIOU]+", re.sub(r"[ऀ-ॿ]", "", text)))
    return max(1, n)


@dataclass
class CaptionCue:
    index: int
    text: str
    start: float
    end: float

    @property
    def duration(self) -> float:
        return round(self.end - self.start, 3)


def clip_duration(path: str | Path) -> float:
    """Seconds of the avatar clip, from ffprobe."""
    out = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", str(path)],
        capture_output=True, text=True, check=True).stdout
    return float(json.loads(out)["format"]["duration"])


def _parse_timestamp(ts: str) -> float:
    ts = ts.replace(",", ".").strip()
    parts = [float(p) for p in ts.split(":")]
    while len(parts) < 3:
        parts.insert(0, 0.0)
    h, m, s = parts[-3:]
    return h * 3600 + m * 60 + s


def cues_from_captions(path: str | Path) -> list[CaptionCue]:
    """Read HeyGen's .srt/.vtt. This is the accurate path — prefer it."""
    raw = Path(path).read_text(encoding="utf-8")
    cues: list[CaptionCue] = []
    for block in re.split(r"\n\s*\n", raw.strip()):
        m = re.search(r"([\d:.,]+)\s*-->\s*([\d:.,]+)", block)
        if not m:
            continue
        text = " ".join(
            l.strip() for l in block.split("\n")
            if "-->" not in l and not l.strip().isdigit()
            and not l.strip().upper().startswith("WEBVTT")
        ).strip()
        if text:
            cues.append(CaptionCue(len(cues), text,
                                   _parse_timestamp(m.group(1)),
                                   _parse_timestamp(m.group(2))))
    return cues


def cues_from_duration(lines: list[str], total: float, *,
                       lead_in: float = 0.0,
                       gap: float = 0.12) -> list[CaptionCue]:
    """Apportion ``total`` seconds across ``lines`` by syllable weight.

    ``gap`` is the small silence between lines a presenter naturally leaves; it
    is taken off the top so the weighted split covers speech only.
    """
    if not lines:
        return []
    speech = max(0.1, total - lead_in - gap * (len(lines) - 1))
    weights = [syllables(l) for l in lines]
    unit = speech / sum(weights)

    cues, t = [], lead_in
    for i, (line, w) in enumerate(zip(lines, weights)):
        dur = w * unit
        cues.append(CaptionCue(i, line, round(t, 3), round(t + dur, 3)))
        t += dur + (gap if i < len(lines) - 1 else 0)
    return cues


def speech_segments(audio: str | Path, *, min_silence: float = 0.40,
                    noise_db: int = -32) -> list[tuple[float, float]]:
    """Spans of actual speech, found by detecting the pauses between them."""
    out = subprocess.run(
        ["ffmpeg", "-v", "info", "-i", str(audio),
         "-af", f"silencedetect=noise={noise_db}dB:d={min_silence}", "-f", "null", "-"],
        capture_output=True, text=True).stderr
    starts = [float(m) for m in re.findall(r"silence_start:\s*([\d.]+)", out)]
    ends = [float(m) for m in re.findall(r"silence_end:\s*([\d.]+)", out)]
    total = clip_duration(audio)

    spans, cursor = [], 0.0
    for s, e in zip(starts, ends + [total]):
        if s > cursor + 0.05:
            spans.append((round(cursor, 3), round(s, 3)))
        cursor = e
    if cursor < total - 0.05:
        spans.append((round(cursor, 3), round(total, 3)))
    return spans


def cues_from_speech(lines: list[str], audio: str | Path, *,
                     min_silence: float | None = None) -> list[CaptionCue] | None:
    """Align lines to real speech spans, when the counts agree.

    Far better than apportioning a total: the presenter's own pauses mark where
    one line ends and the next begins. The pause threshold is searched for the
    value that yields exactly one span per line — if none does, the caller
    should fall back to weighting, because a mismatched alignment is worse than
    an estimated one.
    """
    # Search both axes. Pause length alone is not enough: one recording split
    # cleanly at 0.40s/-32dB, another needed 0.35s/-36dB — between -35dB (one
    # segment too many) and -40dB (one too few). Studio noise floor and the
    # presenter's pacing both move, so fix neither.
    durations = [min_silence] if min_silence else [
        0.25, 0.30, 0.32, 0.35, 0.38, 0.40, 0.45, 0.50, 0.55, 0.60, 0.70]
    for d in durations:
        for noise in (-30, -32, -34, -35, -36, -37, -38, -40):
            spans = speech_segments(audio, min_silence=d, noise_db=noise)
            if len(spans) == len(lines):
                return [CaptionCue(i, ln, s, e)
                        for i, (ln, (s, e)) in enumerate(zip(lines, spans))]
    return None


def cues_from_transcript(lines: list[str], words: list[dict],
                         total: float | None = None) -> list[CaptionCue]:
    """Anchor lines to a transcript's word timings by syllable progress.

    Literal word matching is not available: Whisper returns one clip in
    Devanagari and another romanised, and it mishears names besides. What is
    stable is *how far through the speech* a word is. So both sides are
    measured in syllables, a progress curve is built from the transcript's own
    word times, and each script line's syllable span is read off that curve.

    Pauses need no special handling — they sit in the gaps between word
    timestamps and are therefore already in the curve.
    """
    if not lines or not words:
        return []
    cum, running = [], 0
    for w in words:
        running += syllables(w["w"])
        cum.append((running, w["s"], w["e"]))
    spoken_total = running

    line_syl = [syllables(l) for l in lines]
    script_total = sum(line_syl)

    def time_at(progress: float, use_end: bool) -> float:
        """Time at a 0..1 point through the speech."""
        target = progress * spoken_total
        prev_t = 0.0
        for n, s, e in cum:
            if n >= target:
                return e if use_end else s
            prev_t = e
        return prev_t

    cues, acc = [], 0
    for i, (line, syl) in enumerate(zip(lines, line_syl)):
        start = time_at(acc / script_total, use_end=False)
        acc += syl
        end = time_at(acc / script_total, use_end=True)
        if cues and start < cues[-1].end:
            start = cues[-1].end
        cues.append(CaptionCue(i, line, round(start, 3), round(max(end, start + 0.4), 3)))
    if total:
        cues[-1] = CaptionCue(cues[-1].index, cues[-1].text, cues[-1].start, round(total, 3))
    return cues


def spoken_lines(script_bhaag: str | Path, part: int | None = None) -> list[str]:
    """The quoted lines of a भाग-format script, optionally one PART only."""
    text = Path(script_bhaag).read_text(encoding="utf-8")
    if part is not None:
        chunks = re.split(r"^\s*PART\s+\d+\s*$", text, flags=re.M)
        if len(chunks) > part:
            text = chunks[part]
    return [" ".join(m.split())
            for m in re.findall(r"[“\"]([^“”\"\n]+)[”\"]", text)]


def plan(script_bhaag: str | Path, avatar_clip: str | Path, *,
         captions: str | Path | None = None,
         part: int | None = None) -> list[CaptionCue]:
    """The timing plan a scene should follow, from whichever input exists."""
    lines = spoken_lines(script_bhaag, part)
    if captions:
        return cues_from_captions(captions)
    aligned = cues_from_speech(lines, avatar_clip)
    if aligned:
        return aligned
    return cues_from_duration(lines, clip_duration(avatar_clip))


def write_plan(cues: list[CaptionCue], dest: str | Path) -> Path:
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(
        [{"i": c.index, "text": c.text, "start": c.start,
          "end": c.end, "dur": c.duration} for c in cues],
        ensure_ascii=False, indent=2), encoding="utf-8")
    return dest
