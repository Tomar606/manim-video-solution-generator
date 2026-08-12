"""Write MP Board previous-year-question scripts from the question sheet.

Why this is separate from :mod:`src.script_writer`: that one emits the pipeline's
``[narrator]`` / ``$$LaTeX$$`` beat format, which is right for the reels but
wrong here. Every approved PYQ script in ``style/samples/`` is written as
``भाग`` sections with the formulas *outside* the quotes under ``On Screen:``, and
the samples are the strongest signal the model gets. Fighting them with a
different output format throws that away, so this writer produces the sample
format natively and :func:`to_pipeline_script` converts it down for Manim/TTS.

The mechanical checks here are the same idea as ``src/script_eval.py``: anything
that can be verified without a model gets verified without a model, and the
findings are fed back for a repair pass.
"""
from __future__ import annotations

import csv
import io
import os
import re
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

from src import style as style_mod
from src.llm import complete

# Who writes the script. Without this a bare complete() resolves to "auto",
# which prefers the Claude CLI — so the team's SCRIPT_LLM=openai setting was
# silently ignored and every script came from Claude instead.
SCRIPT_PROVIDER = os.getenv("SCRIPT_LLM", "auto")
# The NCERT cross-check is research, not voice, and stays on Claude per the
# per-stage split in CLAUDE.md. Override with VERIFY_LLM if that changes.
VERIFY_PROVIDER = os.getenv("VERIFY_LLM", "auto")

SHEET_ID = "1E0oZc96akGYf15Nu8v5Q0ZKGy--baAuKf8g-GUXRcEo"
SHEET_CSV = ("https://docs.google.com/spreadsheets/d/{id}/gviz/tq"
             "?tqx=out:csv&sheet={tab}")

# Years are spoken as Hindi words, never digits. Only the range the sheet can
# plausibly contain is listed — an unknown year raises rather than guessing,
# because a wrong number in the hook is the first thing a student hears.
_ONES = {
    1: "एक", 2: "दो", 3: "तीन", 4: "चार", 5: "पाँच", 6: "छह", 7: "सात",
    8: "आठ", 9: "नौ", 10: "दस", 11: "ग्यारह", 12: "बारह", 13: "तेरह",
    14: "चौदह", 15: "पंद्रह", 16: "सोलह", 17: "सत्रह", 18: "अठारह",
    19: "उन्नीस", 20: "बीस", 21: "इक्कीस", 22: "बाईस", 23: "तेईस",
    24: "चौबीस", 25: "पच्चीस", 26: "छब्बीस", 27: "सत्ताईस", 28: "अट्ठाईस",
    29: "उनतीस", 30: "तीस",
}


def year_words(year: int, *, short: bool = False) -> str:
    """2025 -> "दो हज़ार पच्चीस"; short=True -> just "पच्चीस"."""
    tail = year % 100
    if tail not in _ONES:
        raise ValueError(f"No Hindi spelling for year {year}; add it to _ONES.")
    return _ONES[tail] if short else f"दो हज़ार {_ONES[tail]}"


def year_phrase(years: list[int]) -> str:
    """The hook's year list: first full, middle shortened, last full.

    "दो हज़ार उन्नीस, बीस, बाईस और दो हज़ार चौबीस" — the shortened middle is how
    a teacher says it, and it keeps a long list speakable.
    """
    if not years:
        return ""
    if len(years) == 1:
        return year_words(years[0])
    if len(years) == 2:
        return f"{year_words(years[0])} और {year_words(years[1])}"
    middle = ", ".join(year_words(y, short=True) for y in years[1:-1])
    return f"{year_words(years[0])}, {middle} और {year_words(years[-1])}"


# --------------------------------------------------------------------------- #
# The question sheet                                                           #
# --------------------------------------------------------------------------- #
@dataclass
class Question:
    qid: str
    subject: str
    chapter_no: str
    chapter: str
    category: str
    text: str
    answer: str
    years: list[int]
    answer_image: str = ""

    @property
    def slug(self) -> str:
        return self.qid.lower().replace("_", "-")


def _years(raw: str) -> list[int]:
    """"2019, 20, 22 , 24" -> [2019, 2020, 2022, 2024]."""
    out: list[int] = []
    for tok in re.findall(r"\d{2,4}", raw or ""):
        n = int(tok)
        if n < 100:
            n += 2000
        if 2000 <= n <= 2099:
            out.append(n)
    return sorted(dict.fromkeys(out))


def load_questions(tab: str = "Chemistry", *, sheet_id: str = SHEET_ID,
                   csv_path: str | Path | None = None) -> list[Question]:
    if csv_path:
        raw = Path(csv_path).read_text(encoding="utf-8")
    else:
        with urllib.request.urlopen(SHEET_CSV.format(id=sheet_id, tab=tab)) as r:
            raw = r.read().decode("utf-8")

    rows = list(csv.reader(io.StringIO(raw)))
    prefix = tab[:3].upper()
    out: list[Question] = []
    for r in rows:
        if len(r) < 10 or not r[1].strip().upper().startswith(prefix):
            continue
        out.append(Question(
            qid=r[1].strip(), subject=r[2].strip(), chapter_no=r[3].strip(),
            chapter=r[4].strip(), category=r[5].strip(),
            text=" ".join(r[7].split()).lstrip(". "),
            answer=" ".join(r[8].split()),
            years=_years(r[9]),
            answer_image=r[11].strip() if len(r) > 11 else "",
        ))
    return out


# --------------------------------------------------------------------------- #
# Step 1 — check the sheet's answer before writing anything from it            #
# --------------------------------------------------------------------------- #
VERIFY_SYSTEM = """You check a Class 12 MP Board answer against NCERT before it \
is turned into a teaching video. The question bank is a starting point, not an \
authority — it has been wrong before, and a video repeats the error to thousands \
of students.

Report, briefly and concretely:
1. Anything factually wrong in the given answer, with the correction.
2. Anything missing that the exam expects for full marks.
3. The exact terminology the student must write (Hindi, as in the NCERT Hindi \
edition) — these words are frozen and must appear in the script unchanged.
4. For a derivation: the correct order of steps, and any relation that is \
commonly got backwards.
5. What must be drawn correctly if this is animated, and the errors to avoid.

No preamble. Under 400 words. If the answer is correct, say so in one line and \
spend the space on 3-5."""


def verify_answer(q: Question, *, provider: str | None = None) -> str:
    return complete(
        VERIFY_SYSTEM,
        f"CHAPTER: {q.chapter}\nQUESTION: {q.text}\n\n"
        f"QUESTION BANK'S ANSWER:\n{q.answer}",
        provider=provider or VERIFY_PROVIDER, effort="high",
    ).strip()


# --------------------------------------------------------------------------- #
# Step 2 — write the script                                                    #
# --------------------------------------------------------------------------- #
WRITE_SYSTEM = """You write scripts for MP Board Class 12 previous-year-question \
videos, in Hindi (Devanagari), for a Hindi-medium student.

Output the script and NOTHING else — no preamble, no code fences, no commentary.

Match the approved scripts you are shown exactly in form and voice. The house \
style notes are rules, not suggestions; where the notes and the samples \
disagree, the notes win.

FORMAT:

प्रश्न — <विषय>

भाग 1 — शुरुआत 🎙️
शिक्षक:
“<spoken line>”
“<spoken line>”

भाग 2 — <heading> 🎙️
शिक्षक:
“<spoken line>”
On Screen:
<formula, on its own line, OUTSIDE the quotes>
“<spoken line naming what the symbols mean>”

... भाग N — अंतिम भाग 🎙️

HARD RULES:
- Only text inside “ ” is spoken. Anything outside is on-screen text.
- Never recite an equation in a spoken line. Lead in with a short phrase ending \
in an em-dash, put the formula on its own line, then say what the symbols mean.
- No digits in any spoken line. Years become Hindi words; values in the working \
become English tokens ("two-ell", "two-p").
- The definition itself is textbook-exact and is followed immediately by a \
plain restatement opening with “मतलब,”.
- Before every important definition or tricky point, tell the student to focus \
AND give the reason (exam marks, or the mistake most students make).
- Subject terminology and nomenclature never change.
- 5 to 8 भाग. One concept per भाग."""


def write_script(q: Question, verification: str, *,
                 provider: str | None = None,
                 style: style_mod.StyleGuide | None = None,
                 effort: str = "high",
                 findings: str = "", previous: str = "") -> str:
    guide = style if style is not None else style_mod.load()

    task = f"""Write the script for this question.

प्रश्न ({q.qid}, अध्याय {q.chapter_no} — {q.chapter}): {q.text}

THE YEAR LINE — use exactly this phrasing for the years, it is already in the
house form: "{year_phrase(q.years)}"

QUESTION BANK'S ANSWER (a starting point, not the authority):
{q.answer}

ACCURACY CHECK — this overrides the answer above wherever they disagree:
{verification}"""

    if findings:
        task = (f"{task}\n\nYOUR PREVIOUS DRAFT FAILED THESE MECHANICAL CHECKS. "
                f"Fix every one and return the complete corrected script:\n"
                f"{findings}\n\nPREVIOUS DRAFT:\n{previous}")

    section = guide.prompt_section()
    prompt = f"{section}\n\n{'=' * 60}\n\n{task}" if section else task
    out = complete(WRITE_SYSTEM, prompt,
                   provider=provider or SCRIPT_PROVIDER, effort=effort)
    return re.sub(r"^```[a-z]*\n|\n```$", "", out.strip()).strip()


# --------------------------------------------------------------------------- #
# Step 3 — mechanical checks                                                   #
# --------------------------------------------------------------------------- #
# No DOTALL: a spoken line is one line. With it, a stray unclosed quote — the
# samples have one — swallows everything down to the next quote, including the
# भाग heading in between, and reports nonsense.
SPOKEN_RE = re.compile(r"[“\"]([^“”\"\n]+)[”\"]")
CLOSERS = ("स्क्रीनशॉट", "उन्नति बैच")
# `=` and `+` between Hindi words are a spoken memory aid and are approved —
# "धातु + वायुमण्डल की गैसें + नमी = संक्षारण।" is in a verified script. What
# must never be spoken is algebra, which always carries Latin variables or one
# of the operator glyphs below.
# Subscripts are NOT listed: a verified script says "अब अगर दो पदार्थों की
# मात्राएँ W₁ और W₂ … हैं, तो—" out loud. Naming a subscripted variable in prose
# is normal speech; what must never be spoken is a relation between them.
ALGEBRA_GLYPH = re.compile(r"[∝×÷√^]")
LATIN_VAR = re.compile(r"(?<![A-Za-z])[A-Za-z](?![A-Za-z])")
FOCUS_CUE = re.compile(r"ध्यान से|याद रख|गलती करते|ज़रा देख|नोट कर")


@dataclass
class Check:
    findings: list[str] = field(default_factory=list)
    spoken: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.findings


def check_script(text: str, q: Question) -> Check:
    c = Check()
    lines = [l.strip() for l in text.split("\n")]
    spoken = [" ".join(m.split()) for m in SPOKEN_RE.findall(text)]
    c.spoken = spoken

    # The samples number the question ("प्रश्न 3 — फैराडे …"), so the number
    # between the word and the dash is optional, not absent.
    if not re.search(r"^प्रश्न\s*\d*\s*[—-]", text, re.M):
        c.findings.append("Missing the `प्रश्न — <विषय>` title line.")

    bhaag = re.findall(r"^भाग\s*\d+\s*[—-].*$", text, re.M)
    if not 5 <= len(bhaag) <= 8:
        c.findings.append(f"Found {len(bhaag)} भाग; the house format uses 5 to 8.")
    if bhaag and "🎙️" not in "".join(bhaag):
        c.findings.append("भाग headings must carry the 🎙️ marker.")

    for s in spoken:
        if re.search(r"\d", s):
            c.findings.append(
                f'Digit in a spoken line — years become Hindi words, values '
                f'become English tokens: "{s[:70]}"')
        if ALGEBRA_GLYPH.search(s) or (("=" in s or "/" in s) and LATIN_VAR.search(s)):
            c.findings.append(
                f'Algebra inside a spoken line; formulas go on their own line '
                f'outside the quotes: "{s[:70]}"')
        if len(s.split()) > 34:
            c.findings.append(f'Spoken line too long to say in one breath '
                              f'({len(s.split())} words): "{s[:60]}…"')

    joined = " ".join(spoken)
    if q.years and year_phrase(q.years) not in joined:
        c.findings.append(
            f'The hook must name the year(s) as "{year_phrase(q.years)}".')
    if "त्रैमासिक परीक्षा" not in joined:
        c.findings.append('The hook must say "त्रैमासिक परीक्षा", not a bare परीक्षा.')
    if "मतलब" not in joined:
        c.findings.append('No “मतलब,” gloss — every definition needs a plain '
                          'restatement right after it.')
    if not FOCUS_CUE.search(joined):
        c.findings.append("No focus cue before the important parts.")
    for needle in CLOSERS:
        if needle not in joined:
            c.findings.append(f'Closing is incomplete — "{needle}" is missing.')
    return c


def draft(q: Question, *, provider: str | None = None,
          max_attempts: int = 3, style: style_mod.StyleGuide | None = None,
          verification: str | None = None) -> tuple[str, Check, str]:
    """Verify, write, then repair until the mechanical checks pass."""
    ver = verification if verification is not None else verify_answer(q)
    text = write_script(q, ver, provider=provider, style=style)
    chk = check_script(text, q)
    for _ in range(max_attempts - 1):
        if chk.ok:
            break
        text = write_script(q, ver, provider=provider, style=style,
                            findings="\n".join(f"- {f}" for f in chk.findings),
                            previous=text)
        chk = check_script(text, q)
    return text, chk, ver


# --------------------------------------------------------------------------- #
# The header that goes on every delivered document                             #
# --------------------------------------------------------------------------- #
def doc_header(q: Question) -> str:
    """Title block for the reviewable document.

    The **whole question** goes at the top, verbatim from the sheet. A reviewer
    has to be able to check the script against what was actually asked without
    opening the sheet in another tab — and the count the question asks for
    ("तीन कारक", "दो अनुप्रयोग") is the thing most likely to be under-delivered.
    """
    years = ", ".join(str(y) for y in q.years) if q.years else "—"
    return "\n".join([
        f"प्रश्न क्रमांक: {q.qid}  |  अध्याय {q.chapter_no} — {q.chapter}",
        f"श्रेणी: {q.category}  |  वर्ष: {years}",
        "MP Board कक्षा 12 (हिन्दी माध्यम)",
        "",
        "पूरा प्रश्न:",
        f"  {q.text}",
        "",
        "=" * 60,
        "",
    ])


# --------------------------------------------------------------------------- #
# Down-convert to the pipeline's script format                                 #
# --------------------------------------------------------------------------- #
def to_pipeline_script(text: str, *, chroma_band: float = 0.60) -> str:
    """भाग format -> the `[narrator]` format Manim and TTS read.

    On-screen formulas become part of the director note, explicitly marked, so
    they can never reach text-to-speech.
    """
    title = ""
    beats: list[dict] = []
    cur: dict | None = None

    for ln in text.split("\n"):
        s = ln.strip()
        if not s:
            continue
        if s.startswith("प्रश्न"):
            title = re.sub(r"^प्रश्न\s*\d*\s*[—-]\s*", "", s).strip()
            continue
        if s.startswith("भाग"):
            cur = {"note": re.sub(r"\s*🎙️\s*$", "", s), "spoken": [], "screen": []}
            beats.append(cur)
            continue
        if s in ("शिक्षक:", "On Screen:"):
            continue
        if cur is None:
            continue
        if s[0] in "“\"" or s.endswith("”"):
            cur["spoken"].append(s.strip("“”\""))
        else:
            cur["screen"].append(s)

    out = [
        "---", f"title: {title}", "orientation: portrait", "theme: midnight",
        "language: hindi", "chroma:", "  preset: custom",
        f"  rect: [0.0, {chroma_band}, 1.0, {round(1 - chroma_band, 2)}]"
        "   # bottom band = HeyGen presenter",
        "avatar:", "  placement: auto", "  timing: audio",
        "speakers:", "  narrator: { voice: George }", "---", "",
    ]
    for b in beats:
        if not b["spoken"]:
            continue
        note = b["note"]
        if b["screen"]:
            note += (" || ON SCREEN (exact, never spoken): "
                     + " ; ".join(b["screen"]))
        out += ["[narrator]", " ".join(b["spoken"]), f"%% {note}", ""]
    return "\n".join(out)
