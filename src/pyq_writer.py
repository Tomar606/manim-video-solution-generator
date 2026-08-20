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
import json
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

# The MAIN TRACKING DASHBOARD sheet. It replaced an earlier sheet whose
# chapter-2 and chapter-3 numbering was off by one — that sheet called the
# dry cell C2-LA-05 and zero-order C3-LA-02, while every answer page, ending
# clip and folder from the team calls them C2-LA-04 and C3-LA-01. This one
# agrees with them, so IDs from here can be trusted against those files.
SHEET_ID = "1uJDts0O1Z4UER5sVpKmPp2jE8SNjEUy_xhcLpUXRn4Q"
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


def _clean(raw: str) -> str:
    """Strip the artefacts the sheet carries into every question and answer.

    The rows are OCR/mathpix exports: markdown image embeds pointing at
    cdn.mathpix.com, stray \\section*{} wrappers, and collapsed whitespace.
    None of it belongs in a script or in the question printed on the document.
    """
    s = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", raw or "")     # ![](https://cdn.mathpix…)
    s = re.sub(r"https?://\S+", " ", s)
    s = re.sub(r"\\section\*\{([^}]*)\}", r"\1", s)
    s = re.sub(r"\s*\bचित्र\b\s*$", "", s.strip())
    return " ".join(s.split()).lstrip(". ")


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
            text=_clean(r[7]),
            answer=_clean(r[8]),
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
HOOK_HISTORY = Path("style/hook_history.json")

# --------------------------------------------------------------------------- #
# Hook selection                                                              #
# --------------------------------------------------------------------------- #
# Chosen here rather than by the model. Both approved samples open on the
# board/year line, and style/ tells the model samples outrank written rules —
# so left to itself it copies that opening every time, whatever the topic. The
# retention spec's own tables are deterministic, so implement them.
TOPIC_PATTERNS = [
    ("derivation",  ("निगमन", "व्युत्पत्ति", "सिद्ध कीजिए", "स्थापित कीजिए",
                     "व्यंजक", "प्रमाणित")),
    ("numerical",   ("ज्ञात कीजिए", "गणना", "परिकलन")),
    ("comparison",  ("अंतर", "तुलना", "भेद", "बनाम")),
    ("process",     ("विधि", "सचित्र", "वर्णन", "बनाने", "निर्माण", "प्रक्रिया")),
    ("law",         ("नियम", "प्रमेय", "सिद्धांत")),
    ("exception",   ("अपवाद", "असामान्य")),
    ("definition",  ("किसे कहते हैं", "क्या है", "परिभाषा", "परिभाषित")),
]
# From retention_system.md, chemistry order: prediction, mistake, exam_fomo,
# challenge, contradiction, analogy — intersected with the per-type table.
TYPE_HOOKS = {
    "definition":  ["mistake", "payoff", "exam_fomo"],
    "law":         ["prediction", "challenge", "contradiction"],
    "formula":     ["prediction", "challenge", "problem"],
    "derivation":  ["problem", "payoff", "challenge"],
    "numerical":   ["challenge", "prediction", "mistake"],
    "process":     ["prediction", "problem", "challenge"],
    "comparison":  ["contradiction", "challenge", "prediction"],
    "exception":   ["contradiction", "mistake"],
    "factual":     ["exam_fomo", "payoff", "mistake"],
}


def classify_topic(q: "Question") -> str:
    blob = f"{q.text} {q.answer[:400]}"
    for kind, needles in TOPIC_PATTERNS:
        if any(n in blob for n in needles):
            return kind
    return "factual"


def choose_hook(q: "Question", history: dict) -> tuple[str, str]:
    """(topic_type, mechanism). Relevance first, recency only to break ties."""
    kind = classify_topic(q)
    candidates = TYPE_HOOKS.get(kind, TYPE_HOOKS["factual"])
    recent = list(history.get("hook_mechanism", []))[-4:]
    fresh = [c for c in candidates if c not in recent]
    return kind, (fresh or candidates)[0]


# Part endings and re-entries, from retention_system.md. Ordered by how well
# each suits the topic type; `direct_continuation` is deliberately kept in every
# list because the spec insists not every part needs a dramatic ending.
TYPE_TRANSITIONS = {
    "derivation":  ["partial_reveal", "future_payoff", "open_loop",
                    "direct_continuation"],
    "law":         ["question_carryover", "challenge", "future_payoff",
                    "direct_continuation"],
    "comparison":  ["contradiction", "question_carryover", "open_loop",
                    "direct_continuation"],
    "process":     ["open_loop", "question_carryover", "future_payoff",
                    "direct_continuation"],
    "numerical":   ["challenge", "partial_reveal", "future_payoff",
                    "direct_continuation"],
    "definition":  ["future_payoff", "open_loop", "question_carryover",
                    "direct_continuation"],
}
# Every re-entry mechanism here connects back to the part before it.
# `direct_continuation` is deliberately absent: the retention spec allows a part
# to simply carry on, but a student arriving at Part 2 on its own has no idea
# what Part 1 established, and the videos are published as separate clips. So
# each part opens by saying where we are — the MECHANISM varies, the bridge
# does not.
TYPE_OPENINGS = {
    "derivation":  ["callback", "resolution_first", "visual_first",
                    "recap_question"],
    "law":         ["answer_first", "recap_question", "callback",
                    "resolution_first"],
    "comparison":  ["resolution_first", "answer_first", "callback",
                    "visual_first"],
    "process":     ["visual_first", "callback", "recap_question",
                    "answer_first"],
    "numerical":   ["answer_first", "resolution_first", "callback",
                    "recap_question"],
    "definition":  ["callback", "answer_first", "recap_question",
                    "resolution_first"],
}
# Prose the writer needs, so the mechanism name is never guessed at.
MECHANISM_GLOSS = {
    "open_loop":           "raise the next question and leave it hanging",
    "question_carryover":  "end on a question this part cannot answer yet",
    "contradiction":       "end on the two facts that appear to clash",
    "partial_reveal":      "the result is reached, its use is still to come",
    "future_payoff":       "name what the next part makes possible",
    "challenge":           "ask the student to attempt it before the next part",
    "direct_continuation": "stop plainly, no device — the topic simply continues",
    "answer_first":        "answer what the last part left hanging, then say "
                           "in one line what that part had established",
    "callback":            "name what the previous part established, then carry "
                           "the one idea forward from it",
    "recap_question":      "restate where the previous part got to and the "
                           "question it left open",
    "visual_first":        "recall the previous part in a line, then open on the "
                           "diagram and explain from it",
    "resolution_first":    "give the resolution first, then say which part it "
                           "resolves and how it was reached",
}


def choose_part_plan(kind: str, parts: int, history: dict) -> dict:
    """Per-part endings and re-entries, all distinct inside one script.

    The user's rule: a three-part script must not end two parts the same way,
    nor open two the same way. Uniqueness is guaranteed here by consuming from
    an ordered list, so it cannot depend on the model remembering what it did
    in an earlier part it can no longer see.
    """
    if parts < 2:
        return {}

    def pick(table: dict, seen_key: str, n: int) -> list[str]:
        pool = table.get(kind) or table["definition"]
        recent = list(history.get(seen_key, []))[-3:]
        # least-recently-used first, order within the type table preserved
        ranked = [c for c in pool if c not in recent] + \
                 [c for c in pool if c in recent]
        return (ranked * 3)[:n]

    # parts-1 endings (the last part ends on the answer card, not a transition)
    return {
        "transition_mechanisms": pick(TYPE_TRANSITIONS,
                                      "transition_mechanisms", parts - 1),
        "part_opening_mechanisms": pick(TYPE_OPENINGS,
                                        "part_opening_mechanisms", parts - 1),
    }


def load_history(n: int = 8) -> dict:
    """Recent hook/transition choices — a preference signal, never a ban."""
    if not HOOK_HISTORY.exists():
        return {}
    try:
        rows = json.loads(HOOK_HISTORY.read_text(encoding="utf-8"))[-n:]
    except (json.JSONDecodeError, OSError):
        return {}
    out: dict[str, list] = {}
    for r in rows:
        for k in ("hook_mechanism", "hook_angle", "transition_mechanisms",
                  "part_opening_mechanisms"):
            v = r.get("meta", {}).get(k)
            if isinstance(v, list):
                out.setdefault(k, []).extend(v)
            elif v:
                out.setdefault(k, []).append(v)
    out["hooks"] = [r.get("hook", "")[:90] for r in rows if r.get("hook")]
    return out


def remember(qid: str, meta: dict, hook: str) -> None:
    rows = []
    if HOOK_HISTORY.exists():
        try:
            rows = json.loads(HOOK_HISTORY.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            rows = []
    rows = [r for r in rows if r.get("qid") != qid]
    rows.append({"qid": qid, "meta": meta, "hook": hook})
    HOOK_HISTORY.parent.mkdir(parents=True, exist_ok=True)
    HOOK_HISTORY.write_text(json.dumps(rows, ensure_ascii=False, indent=2),
                            encoding="utf-8")


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
- Do NOT put a focus line before every important definition or tricky point. \
That rule produced a script where each definition arrived behind "ज़रा ठहरो, \
मुख्य बात आ रही है, यही लिखोगे तो पक्के मार्क्स मिलेंगे" — an advertisement \
wrapped around a textbook. Say it only where a real teacher would: a genuine \
confusion, a step that is easy to get wrong. At most ONE such marker around any \
one academic point, and never a marks guarantee.
- Subject terminology and nomenclature never change.
- 5 to 8 भाग. One concept per भाग.

RETENTION AND STRUCTURE — read the priority order first and never reverse it:
correctness, then clarity, then conceptual progression, then comprehension, then
retention, then variation, then drama. A creative hook that makes the
explanation worse is a bad hook; a repetitive but highly relevant hook beats
forced novelty.

Open with ONE of these mechanisms, chosen for the topic, not at random:
  exam_fomo    the question genuinely repeats in boards and carries real marks
  prediction   the concept explains an observable consequence — "क्या होगा अगर…"
  challenge    the student could reasonably answer before being taught
  mistake      students genuinely confuse two things or misuse a formula
  contradiction  intuition differs from the result, or two rules seem to clash
  analogy      abstract concept with a real analogy that genuinely simplifies
  payoff       procedural content, clear exam outcome, little natural curiosity
  problem      the concept is a tool and the application beats the definition

By topic type — definition: payoff/mistake · law: prediction/challenge/
contradiction · formula: prediction/challenge/problem · derivation: problem/
payoff/partial reveal · numerical: challenge/prediction · process: curiosity/
prediction · comparison: contradiction/challenge · exception: surprise/mistake ·
diagram: prediction/visual-first · exam answer: marks payoff/mistake.
For chemistry prefer, in order: prediction, mistake, exam_fomo, challenge,
contradiction, analogy.

THE HOOK AND THE EXAM LINE ARE SEPARATE BEATS. The hook — whichever mechanism
you chose — is spoken FIRST. The board/class/year/त्रैमासिक परीक्षा line comes
SECOND, right after it. They merge into one opening ONLY when the chosen
mechanism is exam_fomo. Do not open every script with the board-and-year line:
that is one mechanism among eight, and using it every time is precisely the
template sameness this system exists to prevent. Across a run of scripts the
mechanisms must genuinely vary with the topic type.

NEVER manufacture exam relevance that is weak, and never call a mistake common
unless it plausibly is. BANNED outright: "आप यकीन नहीं करेंगे", "आगे जो होगा",
"इसका जवाब आपको चौंका देगा", "99% बच्चे ये नहीं जानते", "वीडियो के अंत तक जरूर
देखना", artificial suspense, fake urgency, and REPEATED "ध्यान से सुनो",
"बच्चों", "आज हम सीखेंगे". If the content is interesting, let the content do the
retention work.

DO NOT put a retention beat after every section. The video must still sound like
a teacher explaining something, with stretches of ordinary teaching between the
curiosity beats.

WHEN THE SCRIPT IS SPLIT, break at a cognitive boundary — a concept fully
established, a question raised but unanswered, a formula derived with its
application still to come. Never mid-explanation, and never invent a cliffhanger
where nothing is genuinely unresolved. End a part with one of: open_loop,
question_carryover, contradiction, cliffhanger (rarely), partial_reveal,
future_payoff, challenge, or direct_continuation — not every part needs a
dramatic ending. Open the next part with a DIFFERENT mechanism: answer_first,
callback, direct_continuation, recap_question, visual_first or
resolution_first. Do not recap merely because it is Part 2; recap only when the
earlier concept is actually needed. Whatever a transition promises, the next
part must actually pay off.

The CTA is not a retention device: concept, then exam payoff, then summary, then
CTA.

BEFORE THE SCRIPT, output one line of metadata and nothing else on that line:
META: {"topic_type": "...", "hook_mechanism": "...", "hook_angle": "...",
"transition_mechanisms": [...], "part_opening_mechanisms": [...],
"retention_intensity": "low|medium|high", "connector_density": "low|medium",
"emotional_intensity": "low|low_medium|medium"}
Retention and casualness are DIFFERENT dimensions: a script can be highly
retentive because the concept is interesting and still be sparse in
conversational asides. Do not raise one because the other is high.
Then a blank line, then the script. The metadata is internal — never let its
wording leak into the spoken lines."""

# Roughly 120 spoken words per minute — the rate implied by the team's own
# prompt skill, which chunks narration into 10-second segments of 18-22 words.
WORDS_PER_MIN = 120

SPLIT_RULES = """
THIS SCRIPT IS TOO LONG FOR ONE VIDEO AND MUST BE WRITTEN IN {n} PARTS, in ONE
document. Follow this convention exactly:

- Divide with a bare `PART 1`, `PART 2`{extra} line.
- Inside a part, headings lose their numbers: `फैराडे का प्रथम नियम 🎙️`, not
  `भाग 2 — …`. Numbering does not run across parts.
- Cut at a CONCEPT boundary, not at a word count. One law, one case, one stage
  of the derivation per part.
- PART 1's hook is shorter and names the marks instead of promising:
    “एमपी बोर्ड कक्षा बारहवीं के बच्चों! ये सवाल {{वर्ष}} में आ चुका है, और इस
     बार भी आपकी त्रैमासिक परीक्षा में आ सकता है।”
    “तो चलो, इसे ऐसे याद करते हैं कि परीक्षा में आपके चार नंबर पक्के हो जाएँ!”
- Every part except the last ends with a `Part N Ending 🎙️` section: first the
  one thing to remember with its formula, then what the next part will answer.
  Say it the way a person would, and prefer “नेक्स्ट पार्ट में मिलते हैं”:
  “तो यहाँ तक तो कर लिया? सही बात है! अब आंसर में कैसे लिखना है, ये नेक्स्ट
  पार्ट में मिलते हैं।”
- Parts after the first open with a bridge, NOT the hook. No exam years, no
  board/class line — those are spent:
    “बच्चों, Part 1 में हमने समझा …, और अब समझते हैं …”
  Write "Part 1" in Latin, not transliterated.
- ONLY the final part carries the closing: answer on screen, save it, take a
  screenshot, अरिविहान के उन्नति बैच से जुड़ो. Earlier parts must NOT have it.
- Splitting is a chance to tighten. Do not pad a part to fill it."""


def estimate_parts(text: str) -> int:
    """How many videos this script becomes: >3 min -> 2, >5 min -> 3."""
    spoken = SPOKEN_RE.findall(text)
    mins = sum(len(s.split()) for s in spoken) / WORDS_PER_MIN
    return 1 if mins <= 3 else (2 if mins <= 5 else 3)


def write_script(q: Question, verification: str, *,
                 provider: str | None = None,
                 style: style_mod.StyleGuide | None = None,
                 effort: str = "high", parts: int = 1,
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

    hist = load_history()
    kind, mech = choose_hook(q, hist)
    task += (f"\n\nTOPIC TYPE: {kind}\nUSE THIS HOOK MECHANISM: {mech}\n"
             "This is decided for you from the retention system's topic table — "
             "do not substitute another. If the mechanism is NOT exam_fomo, the "
             "first spoken line must be that hook, and the board/class/year/"
             "त्रैमासिक परीक्षा line comes SECOND. The approved samples all open "
             "on the exam line because they happen to use exam_fomo; do not copy "
             "their opening when a different mechanism is specified. Report the "
             "mechanism you were given in the META line.")
    plan = choose_part_plan(kind, parts, hist)
    if plan:
        trans, opens = plan["transition_mechanisms"], plan["part_opening_mechanisms"]
        rows = []
        for i, (t, o) in enumerate(zip(trans, opens), start=1):
            rows.append(f"  Part {i} ENDS with   : {t} — {MECHANISM_GLOSS[t]}")
            rows.append(f"  Part {i + 1} OPENS with : {o} — {MECHANISM_GLOSS[o]}")
        task += (
            f"\n\nPART STRUCTURE — this script is {parts} parts. Use exactly "
            "these endings and re-entries, in this order:\n" + "\n".join(rows) +
            "\n\nNo two parts may end the same way and no two may open the same "
            "way — that is the point of the list.\n\n"
            "EVERY part after the first must still say, in its FIRST spoken "
            "line, what the previous part established — these publish as "
            "separate clips and a student may arrive at Part 2 with no idea "
            "what came before. What varies is HOW, per the mechanism above; "
            "what never varies is that the bridge is there. Do not reuse the "
            "wording “बच्चों, पिछले पार्ट में हमने...” in more than one part of "
            "the same script — name the actual result carried forward instead "
            "(“पिछले पार्ट में फ्लक्स q बटा ε-नॉट निकला था — अब…”). "
            "Report these in the META line.")

    if hist:
        task += ("\n\nRECENT CHOICES ACROSS THE LAST FEW VIDEOS — a preference "
                 "signal, not a ban. If the best mechanism for THIS topic is one "
                 "of these, use it anyway but change the wording, framing and "
                 "angle. If two mechanisms fit equally, prefer the less recent.\n"
                 f"  hook mechanisms : {hist.get('hook_mechanism', [])}\n"
                 f"  hook angles     : {hist.get('hook_angle', [])}\n"
                 f"  transitions     : {hist.get('transition_mechanisms', [])}\n"
                 f"  part openings   : {hist.get('part_opening_mechanisms', [])}\n"
                 "  opening lines already used (do not echo their phrasing):\n"
                 + "\n".join(f"    - {h}" for h in hist.get("hooks", [])))

    if findings:
        task = (f"{task}\n\nYOUR PREVIOUS DRAFT FAILED THESE MECHANICAL CHECKS. "
                f"Fix every one and return the complete corrected script:\n"
                f"{findings}\n\nPREVIOUS DRAFT:\n{previous}")

    system = WRITE_SYSTEM
    # The spoken layer. Kept in src/connectors.py so the pools, the limits and
    # the cross-video repetition history live in one place and every script
    # written from here on picks up a change to them.
    from src.connectors import brief as connector_brief
    system += "\n" + connector_brief(getattr(q, "subject", "Chemistry"),
                                      topic_type=classify_topic(q))
    if parts > 1:
        system += "\n" + SPLIT_RULES.format(
            n=parts, extra=" and `PART 3`" if parts > 2 else "")

    section = guide.prompt_section()
    prompt = f"{section}\n\n{'=' * 60}\n\n{task}" if section else task
    out = complete(system, prompt,
                   provider=provider or SCRIPT_PROVIDER, effort=effort)
    return re.sub(r"^```[a-z]*\n|\n```$", "", out.strip()).strip()


def split_meta(text: str) -> tuple[dict, str]:
    """Peel the META line off the front of a draft."""
    m = re.match(r"\s*META:\s*(\{.*?\})\s*\n", text, re.S)
    if not m:
        return {}, text
    try:
        meta = json.loads(m.group(1))
    except json.JSONDecodeError:
        meta = {}
    return meta, text[m.end():].lstrip("\n")


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
LATIN_RUN = re.compile(r"[A-Za-z]{2,}")
# "Part 1" is the one Latin run the split convention requires — a later part
# opens by naming the one before it. Everything else must be spelled the way it
# is spoken.
SPOKEN_LATIN_OK = {"Part"}
FOCUS_CUE = re.compile(r"ध्यान से|याद रख|गलती करते|ज़रा देख|नोट कर")


@dataclass
class Check:
    findings: list[str] = field(default_factory=list)
    spoken: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.findings


# A bridge can be worded many ways and the point is that the student is told
# where we are — not that a particular phrase was used. Matching only
# "पिछले पार्ट" rejected perfectly good openings like "पिछले हिस्से में…" and
# sent the repair loop round in circles.
# The handoff at the end of a part. Wording is the writer's choice; pointing
# forward is not.
HANDOFF_RE = re.compile(r"नेक्स्ट\s*पार्ट|अगले\s*पार्ट|अगली\s*कड़ी|"
                        r"आगे\s*वाले\s*पार्ट|अगले\s*भाग")

BRIDGE_RE = re.compile(
    r"पिछल[ेीा]\s*(पार्ट|भाग|हिस्से|हिस्सा|कड़ी|वीडियो|बार)|"
    r"पहल[ेा]\s*(पार्ट|भाग|हिस्से)|Part\s*\d|"
    r"अब\s*तक|अभी\s*तक|इससे\s*पहले|यहाँ\s*तक|"
    r"(हमने|आपने)\s+(देखा|समझा|निकाला|पाया|सीखा|जाना|लिखा|स्थापित)")


def check_script(text: str, q: Question, *, parts: int = 1,
                 hook_mech: str | None = None) -> Check:
    c = Check()
    lines = [l.strip() for l in text.split("\n")]
    spoken = [" ".join(m.split()) for m in SPOKEN_RE.findall(text)]
    c.spoken = spoken

    # The samples number the question ("प्रश्न 3 — फैराडे …"), so the number
    # between the word and the dash is optional, not absent.
    if not re.search(r"^प्रश्न\s*\d*\s*[—-]", text, re.M):
        c.findings.append("Missing the `प्रश्न — <विषय>` title line.")

    if parts > 1:
        found = re.findall(r"^\s*PART\s+(\d+)\s*$", text, re.M | re.I)
        if len(found) < 2:
            c.findings.append(
                f"This script needs splitting but has {len(found)} `PART n` divider(s).")
        else:
            # What matters is that no single part runs past three minutes —
            # not that the count matches a formula. A 5.5-minute script split
            # into two 2.8-minute parts is correct even though the >5 min rule
            # would have suggested three.
            chunks = re.split(r"^\s*PART\s+\d+\s*$", text, flags=re.M)[1:]
            for n, chunk in enumerate(chunks, 1):
                mins = sum(len(s.split()) for s in SPOKEN_RE.findall(chunk)) / WORDS_PER_MIN
                if mins > 3.0:
                    c.findings.append(
                        f"Part {n} runs about {mins:.1f} min — over the three-minute limit.")
        if not re.search(r"Part\s+\d+\s+Ending", text, re.I):
            c.findings.append(
                "A split script needs a `Part N Ending 🎙️` section with the "
                "recap and the handoff to the next part.")

        # No two parts may open the same way, and none may end the same way.
        # The prompt asks for this; left unchecked the model still opens every
        # part with "बच्चों, पिछले पार्ट में हमने…". Compare on the opening
        # content words, so a reworded copy of the same move is still caught.
        def _shape(s: str) -> str:
            words = [w for w in re.sub(r"[^\w\s]", " ", s).split()
                     if w not in ("बच्चों", "तो", "अब", "और", "चलिए", "बस")]
            return " ".join(words[:5])

        chunks = re.split(r"^\s*PART\s+\d+\s*$", text, flags=re.M)[1:]
        for label, idx in (("open", 0), ("end", -1)):
            shapes = {}
            for n, chunk in enumerate(chunks, 1):
                sp = SPOKEN_RE.findall(chunk)
                if not sp:
                    continue
                sh = _shape(" ".join(sp[idx].split()))
                if sh and sh in shapes:
                    c.findings.append(
                        f"Part {shapes[sh]} and Part {n} {'open' if idx == 0 else 'end'} "
                        f"on the same line — every part must {'open' if idx == 0 else 'end'} "
                        f"differently. Rewrite Part {n}'s "
                        f"{'first' if idx == 0 else 'last'} spoken line.")
                shapes[sh] = n
        # The handoff must NAME what comes next; the wording is free. It used to
        # demand "…ये समझेंगे अगले पार्ट में।" verbatim, which the team then asked
        # us to drop in favour of "नेक्स्ट पार्ट में मिलते हैं" and similar — the
        # check would have failed every script written to the new guidance.
        if not HANDOFF_RE.search(text):
            c.findings.append(
                'Every part but the last must hand off by naming what the next '
                'one covers — "…नेक्स्ट पार्ट में मिलते हैं", "…ये समझेंगे अगले '
                'पार्ट में", or any wording that points forward.')
        head, tail = text.split("PART 2", 1) if "PART 2" in text else (text, "")
        if "उन्नति बैच" in head:
            c.findings.append(
                "The उन्नति बैच closing belongs only to the final part.")
    else:
        bhaag = re.findall(r"^भाग\s*\d+\s*[—-].*$", text, re.M)
        if not 5 <= len(bhaag) <= 8:
            c.findings.append(f"Found {len(bhaag)} भाग; the house format uses 5 to 8.")
        if bhaag and "🎙️" not in "".join(bhaag):
            c.findings.append("भाग headings must carry the 🎙️ marker.")

    for s in spoken:
        # "Part 1" is required verbatim by the split convention — a later part
        # opens by naming the one before it — so it is not a stray digit.
        s_nodigit = re.sub(r"\bPart\s*\d+\b", "Part", s)
        if re.search(r"\d", s_nodigit):
            c.findings.append(
                f'Digit in a spoken line — years become Hindi words, values '
                f'become English tokens: "{s[:70]}"')
        del s_nodigit
        if ALGEBRA_GLYPH.search(s) or (("=" in s or "/" in s) and LATIN_VAR.search(s)):
            c.findings.append(
                f'Algebra inside a spoken line; formulas go on their own line '
                f'outside the quotes: "{s[:70]}"')
        if len(s.split()) > 34:
            c.findings.append(f'Spoken line too long to say in one breath '
                              f'({len(s.split())} words): "{s[:60]}…"')
        # A single Latin letter in prose is fine — a verified script names W₁
        # and W₂ out loud. A RUN of them is not: physics calculus notation
        # (dS, dl, dB), function names (cos, sin) and vertex labels (AOP) went
        # to TTS verbatim, which reads them as English words rather than
        # spelling them out. They must be written the way they are said.
        for tok in LATIN_RUN.findall(s):
            if tok in SPOKEN_LATIN_OK:
                continue
            c.findings.append(
                f'"{tok}" is Latin text inside a spoken line — TTS reads it '
                f'verbatim. Write it as it is pronounced in Hindi '
                f'(dS -> "डी-एस", dl -> "डी-एल", cos -> "कॉस", AOP -> '
                f'"ए-ओ-पी"), and keep the symbol itself for the On Screen '
                f'line: "{s[:60]}"')

    # Every part after the first must open by saying where the last one got to.
    # These publish as separate clips, so a student can land on Part 2 cold.
    if parts > 1:
        for n, chunk in enumerate(
                re.split(r"^\s*PART\s+\d+\s*$", text, flags=re.M)[2:], start=2):
            sp = SPOKEN_RE.findall(chunk)
            if sp and not BRIDGE_RE.search(" ".join(sp[:2])):
                c.findings.append(
                    f"Part {n} opens without saying what the previous part "
                    f"established — it publishes as its own clip, so a student "
                    f"may arrive here with no context. Open it with a one-line "
                    f"bridge naming the actual result carried forward, then "
                    f"continue. Word it differently from the other parts. "
                    f'Currently: "{sp[0][:60]}"')

    # The assigned mechanism has to be the OPENING, not a label in the META. The
    # samples all open on the board/year line because they happen to use
    # exam_fomo, and left to itself the model copies that opening for every
    # topic — which is how five scripts in a row began with the same sentence.
    if hook_mech and hook_mech != "exam_fomo" and spoken:
        first = spoken[0]
        if "एमपी बोर्ड" in first or (q.years and year_phrase(q.years) in first):
            c.findings.append(
                f"The hook mechanism for this topic is {hook_mech}, so the "
                f"FIRST spoken line must be that hook. It is currently the "
                f"board/year line, which belongs SECOND. Rewrite line 1 as a "
                f"{hook_mech} hook about this specific question and move the "
                f'exam line after it. Currently: "{first[:60]}"')

    joined = " ".join(spoken)
    # The year must appear near the top, but NOT necessarily in the first line:
    # requiring it there forced every script to open on exam_fomo regardless of
    # which hook mechanism suited the topic.
    if q.years and year_phrase(q.years) not in " ".join(spoken[:4]):
        c.findings.append(
            f'The exam line must name the year(s) as "{year_phrase(q.years)}" '
            f'within the first few lines (it follows the hook, and is only the '
            f'opening itself when the hook mechanism is exam_fomo).')
    if "त्रैमासिक परीक्षा" not in joined:
        c.findings.append('The hook must say "त्रैमासिक परीक्षा", not a bare परीक्षा.')
    if "मतलब" not in joined:
        c.findings.append('No “मतलब,” gloss — every definition needs a plain '
                          'restatement right after it.')
    if not FOCUS_CUE.search(joined):
        c.findings.append("No focus cue before the important parts.")
    # The sheet's answers are LaTeX dumps and it leaks through. \vec{E} in a
    # spoken line would be read aloud by TTS; on screen it just prints as
    # backslash-vee-e-c. The samples show clean glyphs (W ∝ Q, W₁).
    latex = re.findall(r"\\[a-zA-Z]+", text)
    if latex:
        c.findings.append(
            f"Raw LaTeX left in the script ({', '.join(sorted(set(latex))[:4])}) "
            f"— convert to clean glyphs: \\vec{{E}} -> E⃗, \\frac{{a}}{{b}} -> a/b.")
    # A Bengali sha once slipped into a शिक्षक tag from the source document.
    stray = set(re.findall(r"[\u0980-\u09FF]", text))
    if stray:
        c.findings.append(
            f"Non-Devanagari Indic characters present: {''.join(sorted(stray))}")

    for needle in CLOSERS:
        if needle not in joined:
            c.findings.append(f'Closing is incomplete — "{needle}" is missing.')
    return c


def draft(q: Question, *, provider: str | None = None,
          max_attempts: int = 3, style: style_mod.StyleGuide | None = None,
          verification: str | None = None) -> tuple[str, Check, str]:
    """Verify, write, then repair until the mechanical checks pass."""
    ver = verification if verification is not None else verify_answer(q)
    meta, text = split_meta(write_script(q, ver, provider=provider, style=style))

    # A script only reveals its length once written, so measure the draft and
    # rewrite it as parts if the render would run past three minutes.
    # Writing it as parts makes it longer — the re-entries and part endings are
    # new material — so a draft that measured 2 parts can come back needing 3.
    # Re-measure and rewrite until the count settles, or the part plan is short
    # by one and the last part silently ends like an earlier one.
    parts = estimate_parts(text)
    for _ in range(3):
        if parts <= 1:
            break
        meta, text = split_meta(
            write_script(q, ver, provider=provider, style=style, parts=parts))
        again = estimate_parts(text)
        if again == parts:
            break
        parts = again

    mech = choose_hook(q, load_history())[1]
    chk = check_script(text, q, parts=parts, hook_mech=mech)
    for _ in range(max_attempts - 1):
        if chk.ok:
            break
        meta, text = split_meta(write_script(
            q, ver, provider=provider, style=style, parts=parts,
            findings="\n".join(f"- {f}" for f in chk.findings), previous=text))
        chk = check_script(text, q, parts=parts, hook_mech=mech)

    # Record what was ASKED for, not what the model said it did. The META line
    # is the model's own report and it drifts — it named the mechanism it felt
    # it had used rather than the one it was given, so `problem` went into the
    # history three times running and the rotation never actually rotated.
    # `load_history()` is stable across this whole call because `remember()`
    # only fires below, so this reproduces exactly what write_script() decided.
    hist = load_history()
    kind = classify_topic(q)
    meta["topic_type"] = kind
    meta["hook_mechanism"] = choose_hook(q, hist)[1]
    meta.update(choose_part_plan(kind, estimate_parts(text), hist))
    hook = (chk.spoken or [""])[0]
    remember(q.qid, meta, hook)

    # Sentence shapes go into a SEPARATE history, and it has to be written here
    # rather than by the caller: three scripts written in one run all read the
    # same snapshot, so a phrase the model likes ("अब फोकस करो, इसी जगह पर उलझन
    # होती है") landed verbatim in two of them. Recording per script makes the
    # second one see the first.
    from src.connectors import remember as connector_remember
    connector_remember(q.qid, list(chk.spoken or []))
    return text, chk, ver, meta


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
