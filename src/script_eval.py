"""Does this script sound like a person talking?

Narration is read aloud by a TTS voice and lip-synced to an avatar, so the bar
isn't "is this good writing" — it's "would a teacher actually say this sentence
out loud". Those are different bars, and generated scripts fail the second one
in specific, repeatable ways: every beat opening with the same two words, digits
and symbols the voice can't pronounce, written-register connectives nobody
speaks, sentences too long to say in one breath.

All of that is measurable, which matters more than it sounds: a score you can
compute is a score the generator can be told to fix. :mod:`src.script_writer`
runs these checks on every draft and feeds the findings back for another pass,
the same way the renderer feeds tracebacks back to the animator.

The checks are heuristics, deliberately. They catch the mechanical tells cheaply
and reliably; judgement about whether a line actually sounds natural is left to
:func:`judge`, which compares a draft against real scripts you've approved.
"""
from __future__ import annotations

import re
import statistics
from dataclasses import dataclass, field

from src.script_models import VideoScript

# --------------------------------------------------------------------------- #
# What a TTS voice cannot say                                                  #
# --------------------------------------------------------------------------- #
# Devanagari: our voices are configured for Latin-script Hinglish. Any Devanagari
# is read wrong or skipped entirely.
DEVANAGARI = re.compile(r"[\u0900-\u097F]")

# LaTeX or maths that leaked into a spoken line. This is the single most common
# way a generated script breaks: it reads fine on screen and is unspeakable.
MATH_RESIDUE = re.compile(r"\\[a-zA-Z]+|[\^_]\s*\{|\$|\\\(|\\\)|[{}]")

# Symbols with no pronunciation. Written out they're fine; spoken they're noise.
# Includes the bare maths operators (= ^ _ +) that survive without any LaTeX
# around them — "x^2 + 2x = 5" reads fine on a page and is unsayable aloud.
UNSPEAKABLE = re.compile(r"[×÷±≤≥≠≈∞∑∫√°%&#@*/<>~|→←↔⇒=^_+]")

# Digits should be words — "do" not "2", "one half" not "1/2". TTS reads digits
# inconsistently across languages, and Hinglish is exactly where it goes wrong.
DIGITS = re.compile(r"\d")

# Written register. Nobody says these out loud, in either language.
WRITTEN_REGISTER = [
    "furthermore", "moreover", "hence we", "thus we", "it can be observed",
    "it is evident", "as we can see", "let us now", "we shall", "in conclusion",
    "firstly", "secondly", "thirdly", "the aforementioned", "aforementioned",
    "in order to obtain", "it should be noted", "note that we", "one can see",
]

# Narration can't point at anything — the viewer hears it, they don't read it.
SCREEN_REFERENCES = [
    "as shown", "shown below", "shown above", "in the figure", "in the diagram",
    "see the", "look at the figure", "the following equation", "below we",
    "as seen in", "refer to the",
]

# Filler that pads a line without adding meaning.
PADDING = [
    "basically", "essentially", "simply put", "in simple terms",
    "as you can imagine", "needless to say", "it goes without saying",
]

# A line this long can't be said in one breath; the avatar's delivery falls apart.
MAX_WORDS = 32
MIN_WORDS = 4
# Below this spread across beats, every line is the same length — the flattest
# possible delivery, and a reliable sign of machine-written copy.
MIN_LENGTH_STDEV = 2.5
# How many leading words define a "sentence opener" for repetition checks.
OPENER_WORDS = 2


@dataclass
class Finding:
    beat: int | None
    severity: str          # fail | warn
    check: str
    detail: str

    def to_dict(self) -> dict:
        return {"beat": self.beat, "severity": self.severity,
                "check": self.check, "detail": self.detail}


@dataclass
class Report:
    findings: list[Finding] = field(default_factory=list)
    stats: dict = field(default_factory=dict)

    @property
    def failures(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == "fail"]

    @property
    def warnings(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == "warn"]

    @property
    def score(self) -> int:
        """0-100. Failures cost more than warnings; the floor is 0."""
        penalty = 12 * len(self.failures) + 4 * len(self.warnings)
        return max(0, 100 - penalty)

    @property
    def ok(self) -> bool:
        return not self.failures

    def to_dict(self) -> dict:
        return {"score": self.score, "ok": self.ok, "stats": self.stats,
                "findings": [f.to_dict() for f in self.findings]}

    def describe(self, limit: int = 25) -> str:
        lines = [f"Human-ness score: {self.score}/100 "
                 f"({len(self.failures)} failures, {len(self.warnings)} warnings)"]
        for f in (self.failures + self.warnings)[:limit]:
            where = f"beat {f.beat}" if f.beat is not None else "script"
            lines.append(f"  [{f.severity}] {where}: {f.detail}")
        extra = len(self.findings) - limit
        if extra > 0:
            lines.append(f"  … and {extra} more")
        return "\n".join(lines)

    def as_feedback(self, limit: int = 18) -> str:
        """The findings, phrased as instructions for another drafting pass."""
        items = (self.failures + self.warnings)[:limit]
        if not items:
            return ""
        lines = ["Fix these specific problems, keeping everything else intact:"]
        for f in items:
            where = f"Beat {f.beat}" if f.beat is not None else "Overall"
            lines.append(f"- {where}: {f.detail}")
        return "\n".join(lines)


def _words(text: str) -> list[str]:
    return [w for w in re.split(r"\s+", text.strip()) if w]


def _phrase_hits(text: str, phrases: list[str]) -> list[str]:
    low = text.lower()
    return [p for p in phrases if p in low]


def evaluate(script: VideoScript) -> Report:
    """Run every mechanical check over a script's spoken lines."""
    report = Report()
    add = report.findings.append

    spoken = [(s.index, s.narration.strip()) for s in script.segments
              if s.narration.strip()]
    if not spoken:
        add(Finding(None, "fail", "empty", "No spoken narration in this script."))
        return report

    lengths: list[int] = []
    openers: dict[str, list[int]] = {}
    seen_sentences: dict[str, int] = {}

    for index, line in spoken:
        words = _words(line)
        lengths.append(len(words))

        # --- things the voice physically cannot say --------------------------
        if DEVANAGARI.search(line):
            add(Finding(index, "fail", "devanagari",
                        "Contains Devanagari; the voice expects Hinglish in "
                        "Latin script. Transliterate it."))
        if MATH_RESIDUE.search(line):
            found = MATH_RESIDUE.search(line).group(0)
            add(Finding(index, "fail", "math-in-speech",
                        f"Contains maths markup ({found!r}) in a spoken line. "
                        f"Say it in words — 'x squared', not 'x^2'."))
        sym = UNSPEAKABLE.search(line)
        if sym:
            add(Finding(index, "fail", "unspeakable-symbol",
                        f"Contains {sym.group(0)!r}, which the voice can't "
                        f"pronounce. Write the word instead."))
        if DIGITS.search(line):
            add(Finding(index, "warn", "digits",
                        "Contains digits. Spell numbers out so the voice reads "
                        "them the way you intend."))

        # --- register --------------------------------------------------------
        for hit in _phrase_hits(line, WRITTEN_REGISTER):
            add(Finding(index, "warn", "written-register",
                        f"{hit!r} is written English, not speech. Say it the way "
                        f"you'd say it to a student."))
        for hit in _phrase_hits(line, SCREEN_REFERENCES):
            add(Finding(index, "fail", "screen-reference",
                        f"{hit!r} points at something the listener can't see. "
                        f"Narration is heard, not read."))
        for hit in _phrase_hits(line, PADDING):
            add(Finding(index, "warn", "padding",
                        f"{hit!r} adds length without meaning."))

        # --- breath ----------------------------------------------------------
        if len(words) > MAX_WORDS:
            add(Finding(index, "warn", "too-long",
                        f"{len(words)} words — too long to say in one breath. "
                        f"Split it or cut it to about {MAX_WORDS}."))
        elif len(words) < MIN_WORDS:
            add(Finding(index, "warn", "too-short",
                        f"Only {len(words)} words; sounds clipped when spoken."))

        # --- repetition ------------------------------------------------------
        opener = " ".join(w.lower().strip(",.!?") for w in words[:OPENER_WORDS])
        openers.setdefault(opener, []).append(index)

        for sentence in re.split(r"(?<=[.!?])\s+", line):
            key = re.sub(r"[^a-z ]", "", sentence.lower()).strip()
            if len(key.split()) >= 5:
                if key in seen_sentences:
                    add(Finding(index, "warn", "repeated-sentence",
                                f"Repeats a sentence already used in beat "
                                f"{seen_sentences[key]}."))
                else:
                    seen_sentences[key] = index

    # --- whole-script shape --------------------------------------------------
    for opener, beats in openers.items():
        if len(beats) >= 3 and opener:
            add(Finding(beats[1], "fail", "repeated-opener",
                        f"{len(beats)} beats open with {opener!r} "
                        f"(beats {beats}). Vary how each line starts — this is "
                        f"the clearest sign a script was machine-written."))
        elif len(beats) == 2 and opener:
            add(Finding(beats[1], "warn", "repeated-opener",
                        f"Beats {beats} both open with {opener!r}."))

    if len(lengths) >= 6:
        spread = statistics.pstdev(lengths)
        if spread < MIN_LENGTH_STDEV:
            add(Finding(None, "warn", "uniform-rhythm",
                        f"Every line is nearly the same length "
                        f"(spread {spread:.1f} words). Real speech mixes short "
                        f"punchy lines with longer ones."))
        report.stats["length_stdev"] = round(spread, 2)

    report.stats.update({
        "beats": len(spoken),
        "avg_words": round(statistics.mean(lengths), 1),
        "longest": max(lengths),
        "shortest": min(lengths),
        "total_words": sum(lengths),
        "est_minutes": round(sum(lengths) / 130, 1),   # ~130 spoken wpm
    })
    return report


# --------------------------------------------------------------------------- #
# The subjective half                                                          #
# --------------------------------------------------------------------------- #
JUDGE_SYSTEM = """You review scripts that a synthetic presenter will read aloud \
to students. You are judging ONE thing: does this sound like a real teacher \
talking, or like generated text being performed?

You are given reference scripts the team has already approved. Those define the \
voice. Judge the draft against them — not against your own idea of good writing.

Report only concrete, fixable problems, each tied to a beat number: a line no \
one would say out loud, a rhythm that repeats, a register that slips into \
writing, phrasing that drifts from the reference voice. If a beat is fine, say \
nothing about it. A short, specific list beats a thorough vague one."""


def judge(script: VideoScript, *, samples: str = "", effort: str = "medium",
          provider: str = "auto"):
    """Ask a model whether the draft sounds like the approved scripts.

    Returns a :class:`Report`-shaped dict. Kept separate from :func:`evaluate`
    so the mechanical checks stay free, deterministic and always available.
    """
    from pydantic import BaseModel, Field

    from src.llm import LLMError, complete_json

    class JudgeFinding(BaseModel):
        beat: int = Field(description="beat number, or -1 for the whole script")
        severity: str = Field(description="fail or warn")
        detail: str = Field(description="what to change, in one sentence")

    class Judgement(BaseModel):
        sounds_human: bool
        summary: str
        findings: list[JudgeFinding] = Field(default_factory=list)

    beats = "\n".join(
        f"[{s.index}] {s.narration}" for s in script.segments if s.narration.strip()
    )
    reference = (f"Reference scripts the team approved:\n\n{samples}\n\n"
                 if samples else
                 "No reference scripts were supplied — judge against natural "
                 "spoken teaching style.\n\n")
    prompt = f"{reference}Draft to review, one line per beat:\n\n{beats}"

    try:
        result = complete_json(JUDGE_SYSTEM, prompt, Judgement,
                               effort=effort, provider=provider)
    except LLMError as exc:
        return {"available": False, "error": str(exc)}

    return {
        "available": True,
        "sounds_human": result.sounds_human,
        "summary": result.summary,
        "findings": [f.model_dump() for f in result.findings],
    }


def merge_judgement(report: Report, judgement: dict) -> Report:
    """Fold judge findings into a mechanical report so both drive one loop."""
    if not judgement.get("available"):
        return report
    for raw in judgement.get("findings", []):
        beat = raw.get("beat")
        report.findings.append(Finding(
            beat=None if beat in (None, -1) else int(beat),
            severity="fail" if raw.get("severity") == "fail" else "warn",
            check="voice",
            detail=str(raw.get("detail", "")).strip(),
        ))
    return report
