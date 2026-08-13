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
    if captions:
        return cues_from_captions(captions)
    return cues_from_duration(spoken_lines(script_bhaag, part),
                              clip_duration(avatar_clip))


def write_plan(cues: list[CaptionCue], dest: str | Path) -> Path:
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(
        [{"i": c.index, "text": c.text, "start": c.start,
          "end": c.end, "dur": c.duration} for c in cues],
        ensure_ascii=False, indent=2), encoding="utf-8")
    return dest
