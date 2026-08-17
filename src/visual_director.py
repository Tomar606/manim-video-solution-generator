"""Decide what the student should SEE at each moment of a PYQ video.

This is the pedagogical decision layer. It sits between the caption track and
the renderer and answers one question per moment:

    what visual would make this sentence easier for a Class 12 Hindi-medium
    student to understand, remember, or reproduce in the exam?

NOT "what graphic can I put here". That second question is what produces visual
noise, and it is the failure this module exists to prevent — an earlier version
generated a block for every caption window, so the screen spent the whole video
restating what the captions already said.

WHAT IT IS ALLOWED TO SAY
-------------------------
`{"type": "none"}` is a first-class answer, not a failure. On the dry-cell part
the director returned a visual for 7 windows out of 58. A visually quiet moment
with the presenter, the captions and a clean plate is correct whenever a graphic
would not add understanding.

THE THREE KINDS OF TEXT, WHICH ARE NOT THE SAME THING
-----------------------------------------------------
  captions        what the presenter actually said. Continuous, timed to the
                  audio, never rewritten to look tidier.
  screen text     what the student should ORGANISE and remember. Never a copy
                  of the narration — a heading, a list, a comparison.
  equations and   things genuinely easier to see than to hear.
  diagrams

WHAT THIS MODULE DOES NOT DECIDE
--------------------------------
Which figure belongs to which question, and when each of its labels is named.
Those are judgements about the QUESTION, not about a sentence, so they stay
hand-placed in the beats file and are merged in. The director never overwrites
an `apparatus`, `graph` or `image` block.

THE QUESTION ITSELF IS A STRONG SIGNAL
--------------------------------------
"सचित्र वर्णन" means the diagram is the spine of the answer. "सिद्ध कीजिए" means
a derivation built step by step. "लाभ लिखिए" means a progressive list. See
QUESTION_STRATEGY.
"""
from __future__ import annotations

import json
import re

# --------------------------------------------------------------------------- #
# Teaching intents. Classify BEFORE choosing a visual — the intent is what makes
# the choice defensible, and it is recorded on the beat so it can be reviewed.
# --------------------------------------------------------------------------- #
INTENTS = [
    "DEFINITION", "LIST", "ADVANTAGES", "COMPARISON", "PROCESS", "CAUSE_EFFECT",
    "FORMULA", "DERIVATION", "DIAGRAM", "GRAPH", "EXAMPLE", "KEYWORD",
    "COMMON_MISTAKE", "RECAP", "TRANSITION", "PURE_NARRATION",
]

# Intent -> the visual that serves it. Anything not here gets no graphic.
INTENT_VISUAL = {
    "DEFINITION": "points", "LIST": "points", "ADVANTAGES": "points",
    "RECAP": "points", "KEYWORD": "points", "COMMON_MISTAKE": "points",
    "COMPARISON": "compare", "PROCESS": "flow", "CAUSE_EFFECT": "flow",
    "FORMULA": "formula", "DERIVATION": "formula", "EXAMPLE": "formula",
    "TRANSITION": "none", "PURE_NARRATION": "none",
}

# Intents whose items are counted off one at a time, so the list should FILL IN
# rather than land whole. All items stay on screen — the student needs the map —
# but the one being spoken is bright and the rest are quiet.
PROGRESSIVE = {"LIST", "ADVANTAGES", "RECAP", "PROCESS"}

# Intents whose equations are CONSTRUCTED rather than displayed. The brief is
# explicit: never show the final equation from the beginning, and the student
# must always be able to answer "what changed?".
BUILT = {"DERIVATION", "FORMULA"}

# Intents that earn the whole vertical frame. The presenter fades out over a
# slow opacity ramp and returns when the demonstration ends — the educational
# content has priority, and the presenter is a guide rather than a permanent
# centrepiece. Everything else keeps him on screen.
FULL_FRAME = {"DIAGRAM", "DERIVATION"}

# What the question demands, read off its own wording. The question is the
# strongest single signal for the visual strategy of the whole video.
QUESTION_STRATEGY = [
    (r"सचित्र|नामांकित चित्र|चित्र बनाइए", "diagram",
     "the question names a diagram outright"),
    (r"ग्राफ|आरेख खीं", "graph", "the question asks for a graph"),
    (r"सिद्ध कीजिए|व्युत्पन्न|निगमन", "derivation",
     "the question asks for a proof, so the answer is built step by step"),
    (r"लाभ|हानि|गुण|दोष|कारक|उपाय|अंतर", "list",
     "the question enumerates, so the answer is a progressive list"),
    (r"परिभाषा|किसे कहते", "definition",
     "the question asks for a definition, so the term leads"),
]

SYSTEM = """तुम एक शैक्षिक वीडियो के Instructional Visual Director हो।
सिर्फ़ JSON लौटाओ, कोई और शब्द नहीं।"""

RULES = """नीचे कुछ कैप्शन लाइनें हैं जो शिक्षक अभी बोल रहा है।

पहले तय करो कि शिक्षक क्या कर रहा है (teaching intent), फिर तय करो कि क्या कोई
दृश्य वास्तव में समझने में मदद करेगा।

सबसे ज़रूरी नियम: हर वाक्य के लिए ग्राफ़िक मत बनाओ। अगर स्क्रीन पर कुछ दिखाने से
समझ बेहतर नहीं होती, तो {"type":"none"} लौटाओ। खाली स्क्रीन स्वीकार्य है।

दूसरा नियम: स्क्रीन-टेक्स्ट कैप्शन की नकल नहीं है। कैप्शन बताता है, स्क्रीन
व्यवस्थित करती है। जो शब्द बोले जा रहे हैं उन्हें दोबारा मत लिखो — उन्हें
शीर्षक, बिंदु, सूत्र या तुलना में बदलो। हर बिंदु अधिकतम 5 शब्द, अधिकतम 4 बिंदु।

तीसरा नियम: एक फ़्रेम में एक ही मुख्य चीज़। छात्र दो सेकंड में समझ पाए।

intent इनमें से चुनो:
<<INTENTS>>

फिर उसी के अनुसार दृश्य चुनो:
- गिनती/सूची/लाभ/कारक/उपाय ("तीन कारक", "चार बातें", "पहला… दूसरा…") -> points
  और "reveal":"progressive" — हर बिंदु तब आए जब वह बोला जाए
- दो चीज़ों की तुलना -> compare
- क्रम/प्रक्रिया/कारण-परिणाम -> flow
- समीकरण या सूत्र -> formula (LaTeX में देवनागरी कभी नहीं; वह label में)
- परिभाषा/मुख्य शब्द -> points, अधिकतम 2 बिंदु
- सिर्फ़ जोड़ने वाला वाक्य, प्रेरणा, दोहराव, "आगे देखेंगे" -> none

<<STRATEGY>>

सिर्फ़ JSON लौटाओ:
{"type":"points","intent":"...","reason":"...","title":"...","items":["..."],
 "reveal":"progressive"}
{"type":"formula","intent":"...","reason":"...","label":"...","tex":["..."]}
{"type":"compare","intent":"...","reason":"...","left":["शीर्षक",["..."]],
 "right":["शीर्षक",["..."]]}
{"type":"flow","intent":"...","reason":"...","items":["...","..."]}
{"type":"none","intent":"...","reason":"..."}

कैप्शन लाइनें:
"""

DEV = re.compile(r"[ऀ-ॿ]")
FIGURE_TYPES = {"apparatus", "graph", "image"}


def question_strategy(question: str):
    """What the question's own wording demands. Used to bias the whole part."""
    for pattern, strategy, why in QUESTION_STRATEGY:
        if re.search(pattern, question):
            return strategy, why
    return "explain", "no explicit visual demand in the question"


def prompt_for(question: str) -> str:
    strategy, why = question_strategy(question)
    line = (f"इस प्रश्न की माँग: {strategy} ({why})। इसे ध्यान में रखो।"
            if strategy != "explain" else "")
    # Substitution, not str.format: the rules text is full of JSON braces and
    # any example added to it later would break .format the same way an
    # unescaped {"type":"none"} already did.
    return (RULES.replace("<<INTENTS>>", ", ".join(INTENTS))
                 .replace("<<STRATEGY>>", line))


def parse(raw: str):
    """The model's answer, validated. Anything malformed becomes no graphic."""
    m = re.search(r"\{.*\}", raw, re.S)
    if not m:
        return None
    try:
        spec = json.loads(m.group(0))
    except json.JSONDecodeError:
        return None
    if spec.get("type") in (None, "none"):
        return None
    if spec["type"] not in {"points", "formula", "compare", "flow"}:
        return None
    if spec["type"] == "formula":
        # Devanagari inside MathTex kills the whole render with a LaTeX Unicode
        # error. Stripped here rather than trusted to the prompt.
        keep = [t for t in spec.get("tex", []) if not DEV.search(t)]
        if not keep:
            return None
        spec["tex"] = keep
    if spec["type"] == "points" and not spec.get("items"):
        return None
    return spec


def with_build(spec, lo: int, hi: int):
    """Give a derivation the caption indices at which each line is written."""
    if spec.get("type") != "formula":
        return spec
    tex = spec.get("tex") or []
    if spec.get("intent") in BUILT and len(tex) > 1:
        spec["build"] = "progressive"
        step = max(1, (hi - lo) // max(1, len(tex)))
        spec["reveal_at"] = [lo + i * step for i in range(len(tex))]
    return spec


def with_presenter(spec):
    """Decide whether the presenter should step aside for this beat.

    Only where the visual genuinely needs the height — a diagram being walked
    through, a derivation being built. A talking head over a full-frame diagram
    is the presenter competing with the thing he is explaining.
    """
    if spec.get("intent") in FULL_FRAME or spec.get("type") in FIGURE_TYPES:
        spec.setdefault("presenter", "hidden")
    return spec


def with_reveal(spec, lo: int, hi: int):
    """Give a counted list the caption indices at which each item is named.

    The window is the span in which the teacher lists them, so spreading the
    items across it is the honest approximation — and it is what turns a block
    that lands whole into one that fills in as he counts.
    """
    if spec.get("intent") in PROGRESSIVE and spec.get("items"):
        spec.setdefault("reveal", "progressive")
    if spec.get("reveal") == "progressive" and spec.get("items"):
        n = len(spec["items"])
        step = max(1, (hi - lo) // max(1, n))
        spec["reveal_at"] = [lo + i * step for i in range(n)]
    return spec


def merge_sequences(beats):
    """Join consecutive blocks that are really ONE list into one that fills in.

    The director decides a window at a time, so it cannot see that four
    consecutive windows are the teacher counting off four advantages. Left
    alone it emits four separate list blocks — create, clear, create again —
    which is precisely the pattern the brief calls out: the student never gets
    a map, only a series of unrelated cards.

    Merged, they become one list anchored at the first window whose items
    reveal at the windows that named them. That is the "persistent context,
    changing focus" shape.
    """
    out, i = [], 0
    while i < len(beats):
        b = beats[i]
        if b.get("type") != "points" or b.get("intent") not in PROGRESSIVE:
            out.append(b); i += 1
            continue
        run = [b]
        j = i + 1
        while (j < len(beats) and beats[j].get("type") == "points"
               and beats[j].get("intent") == b.get("intent")):
            run.append(beats[j]); j += 1
        if len(run) == 1:
            out.append(b); i += 1
            continue

        # ONE line per window, not every line from every window. Each window is
        # the teacher naming one advantage, so taking them all gave two items
        # sharing a reveal time and pushed the fourth advantage off the cap —
        # the list stopped matching the thing being counted.
        items, seen, reveal = [], set(), []
        for blk in run:
            for it in blk.get("items", []):
                key = str(it).strip()
                if key and key not in seen:
                    seen.add(key); items.append(key); reveal.append(blk["at"])
                    break
        merged = dict(run[0])
        merged.update({
            "items": items[:5], "reveal_at": reveal[:5],
            "reveal": "progressive",
            "title": run[0].get("title") or run[-1].get("title"),
            "reason": (run[0].get("reason", "") +
                       f" [{len(run)} windows merged into one filling list]"),
        })
        out.append(merged)
        i = j
    return out


def merge_figures(generated, existing):
    """Figures win their slot. Which figure belongs where, and when each of its
    labels is named, is a judgement about the question — never regenerated."""
    figures = [b for b in existing if b.get("type") in FIGURE_TYPES]
    taken = {f["at"] for f in figures}
    out = [b for b in generated if b["at"] not in taken] + figures
    out.sort(key=lambda b: b["at"])
    return out
