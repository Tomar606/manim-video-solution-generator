"""The spoken layer: how a real teacher joins one idea to the next.

The academic explanation is already accurate and textbook-aligned. What this
module governs is whether it SOUNDS like a person saying it aloud, or like a
textbook being read out.

    not   "अब हम इस विषय को समझते हैं। तत्पश्चात हम इसके महत्वपूर्ण बिंदुओं का
           अध्ययन करेंगे।"
    but   "चलो, अब इसको थोड़ा ध्यान से समझते हैं। यहीं पर एक important point है।"

TWO LAYERS, KEPT SEPARATE
-------------------------
The ACADEMIC layer — definitions, terminology, formulae, exam points — is never
loosened to sound friendlier. The SPEECH layer around it is where the warmth
lives. A connector that changes what is being taught is a bug, not a flourish.

THE RULE THAT MATTERS MOST
--------------------------
"No connector" is a valid choice, and it is the right one roughly a quarter of
the time. `NO_CONNECTOR_RATE` exists so the writer is not pushed into gluing a
casual phrase onto every paragraph — a sentence that already sounds natural
spoken aloud is finished. The quality test is one line: if removing the
connector leaves the sentence sounding just as natural, it should not be there.

REPETITION IS TRACKED BY PATTERN, NOT JUST BY STRING
----------------------------------------------------
"अब इस point को ध्यान से समझो" and "अब इस बात को ध्यान से समझो" are different
strings and the same sentence. `pattern_of()` reduces a connector to its shape
so the writer can be told which SHAPES are stale, not merely which words.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

HISTORY = Path("style/connector_history.json")

# Roughly a quarter of the opportunities should take no connector at all.
NO_CONNECTOR_RATE = 0.25

# --------------------------------------------------------------------------- #
# The pools. Grouped by WHERE they belong and what they are for, because the
# selection rule is "classify the moment, then draw from the matching pool" —
# never "pick a nice-sounding phrase".
# --------------------------------------------------------------------------- #
POOLS: dict[str, list[str]] = {
    # ---- openings ---------------------------------------------------------
    "hook_exam": [
        "आज का ये question ध्यान से समझना, exam में काफ़ी काम आएगा।",
        "इस question को skip मत करना, इसका concept आगे भी बार-बार काम आएगा।",
        "ये concept clear हो गया, तो आगे के questions काफ़ी easy लगेंगे।",
        "आज का ये point छोटा है, लेकिन marks के लिए काफ़ी important है।",
        "ये topic tough लगता है, लेकिन एक बार logic समझ आ गया तो काफ़ी simple है।",
    ],
    "hook_curiosity": [
        "लेकिन यहाँ एक interesting बात है…",
        "अब यहाँ से actual concept start होता है।",
        "अब देखो, यहाँ actually होता क्या है।",
        "यहीं पर एक छोटी सी चीज़ पूरा concept change कर देती है।",
        "अब एक ऐसी बात समझते हैं जो students अक्सर miss कर देते हैं।",
    ],
    "hook_pain": [
        "अगर ये topic तुम्हें confusing लगता है, तो tension मत लो।",
        "इस question में students अक्सर यहीं अटक जाते हैं।",
        "ये part confusing लग सकता है, लेकिन logic बहुत simple है।",
        "बहुत students इस point को रटने की कोशिश करते हैं, लेकिन पहले इसका logic समझना ज़रूरी है।",
    ],
    "hook_reassure": [
        "tension की कोई बात नहीं है, इसको step by step करते हैं।",
        "पहले basic चीज़ clear करते हैं, फिर पूरा concept connect हो जाएगा।",
        "इसको रटने की ज़रूरत नहीं है, पहले समझते हैं।",
        "बस logic पकड़ लो, formula याद रखना भी easy हो जाएगा।",
    ],

    # ---- moving between ideas --------------------------------------------
    "transition": [
        "चलो, अब आगे बढ़ते हैं।",
        "ठीक है, अब इसको देखते हैं।",
        "तो अब तक का concept clear हो गया।",
        "यहाँ तक ठीक है? चलो, अब आगे बढ़ते हैं।",
        "ठीक है, अब इसी को आगे लेके चलते हैं।",
    ],
    "part_end": [
        "तो यहाँ तक ये part clear है।",
        "बस, ये part दिमाग़ में clear रखो।",
        "लेकिन अभी एक important चीज़ बाकी है।",
        "अब जो next point है, उसको miss मत करना।",
        "ये point याद रखना, क्योंकि आगे इसी की ज़रूरत पड़ेगी।",
    ],
    "part_open": [
        "चलो, अब वहीं से आगे बढ़ते हैं।",
        "तो जहाँ हमने छोड़ा था, वहीं से continue करते हैं।",
        "पिछले part में जो समझा था, अब उसी को आगे लेके चलते हैं।",
        "अब यहाँ से concept और clear होगा।",
    ],

    # ---- attention --------------------------------------------------------
    "focus_before": [
        "अब इस बात को एकदम ध्यान से समझना।",
        "यहाँ थोड़ा extra ध्यान देना।",
        "ये wala point दिमाग़ में बिठा लो।",
        "यहाँ एक छोटी सी बात है, लेकिन बहुत important है।",
        "अब ध्यान से देखो, यहीं पर concept clear होगा।",
    ],
    "focus_after": [
        "बस, ये point याद रखना।",
        "ये बात अब भूलनी नहीं है।",
        "इस point पर exam में ग़लती नहीं होनी चाहिए।",
        "ये point आगे question solve करते वक़्त काम आएगा।",
    ],

    # ---- formulae ---------------------------------------------------------
    "formula_before": [
        "अब formula देखने से पहले इसका logic समझ लो।",
        "formula तो याद हो जाएगा, पहले समझते हैं ये आया कहाँ से।",
        "ये formula रटना नहीं है, इसका meaning समझना है।",
    ],
    "formula_after": [
        "बस, ये relation दिमाग़ में बिठा लो।",
        "formula clear है, अब इसका application देखते हैं।",
        "अब question आए तो इसी relation को use करना है।",
    ],

    # ---- mistakes ---------------------------------------------------------
    "mistake_before": [
        "अब यहाँ एक mistake बिलकुल मत करना।",
        "यहीं पर students अक्सर confuse हो जाते हैं।",
        "ये दोनों similar लगते हैं, लेकिन difference बहुत important है।",
        "इस जगह पर एक छोटी सी mistake पूरा answer बिगाड़ सकती है।",
    ],
    "mistake_after": [
        "बस, ये mistake avoid करनी है।",
        "exam में इसी point का ध्यान रखना।",
        "इस difference को दिमाग़ में clear रखो।",
    ],

    # ---- reassurance, examples, recap, closing ---------------------------
    "reassure": [
        "अगर अभी थोड़ा confusing लग रहा है, tension मत लो।",
        "पहली बार में confusing लगना normal है।",
        "एक बार मेरे साथ step by step देखो, clear हो जाएगा।",
        "अगर यहाँ तक समझ आ रहा है, तो आगे का part भी easily समझ आ जाएगा।",
    ],
    "example": [
        "चलो, एक example से समझते हैं।",
        "theory समझ आ गई? अब example से पक्का करते हैं।",
        "अब देखते हैं actual question में ये कैसे use होता है।",
    ],
    "recap": [
        "एक बार quickly recap कर लेते हैं।",
        "चलो, अब जो पढ़ा उसको एक बार connect करते हैं।",
        "अब देखो, पूरा concept कैसे connect हो रहा है।",
    ],
    "closing": [
        "तो बस, अब ये concept एकदम clear है।",
        "अब ये question तुम्हें पहले जितना difficult नहीं लगेगा।",
        "concept clear है, तो अब question तुम handle कर सकते हो।",
        "इसको एक बार revise कर लेना, फिर concept और पक्का हो जाएगा।",
    ],
}

# Per video. The point of a cap is that emphasis only means something when it is
# rationed — a script where every paragraph is "बहुत important" has no important
# paragraphs in it.
LIMITS = {
    "hook": 1, "reassure": 3, "exam_emphasis": 3, "creator": 2,
    "beta": 2, "closing": 1,
}

# Never. Some are rude, some are false comfort on a genuinely hard topic, and
# some are simply worn out from overuse.
BANNED = [
    "अबे", "भाई", "ओए", "क्या कर रहे हो", "इतना भी नहीं आता", "दिमाग़ लगाओ",
    "ये तो बहुत easy है", "तुमसे नहीं होगा", "guys",
]

# Vocabulary that sounds native to each subject. A preference, not a quota —
# forcing "mechanism" into a maths script is worse than not having it.
SUBJECT_WORDS = {
    "Physics": ["logic", "direction", "relation", "formula", "approach", "application"],
    "Chemistry": ["reaction", "condition", "difference", "trend", "mechanism", "formula"],
    "Biology": ["process", "sequence", "function", "difference", "feature"],
    "Maths": ["approach", "step", "condition", "formula", "method", "application"],
}

# The shape a video's warmth should follow. Curiosity to open, reassurance where
# it is genuinely hard, confidence at the end — the student should travel from
# "मुझे नहीं समझ आ रहा" to "अच्छा, समझ आ गया".
ARC = ["hook_curiosity", "reassure", "focus_before", "example", "closing"]


def pattern_of(line: str) -> str:
    """A connector reduced to its shape, so near-duplicates can be spotted.

    "अब इस point को ध्यान से समझो" and "अब इस बात को ध्यान से समझो" are two
    strings and one sentence. Tracking exact text alone lets the same shape run
    through a whole script unnoticed.
    """
    words = re.findall(r"[^\s,।?!—:;]+", line)
    keep = {"अब", "चलो", "तो", "बस", "यहाँ", "लेकिन", "अगर", "ये"}
    return " ".join(w if w in keep else "X" for w in words[:6])


def load_history(n: int = 5) -> dict:
    """Connectors and shapes used in the last n videos — a preference, not a ban."""
    if not HISTORY.exists():
        return {"lines": [], "patterns": []}
    try:
        rows = json.loads(HISTORY.read_text(encoding="utf-8"))[-n:]
    except (json.JSONDecodeError, OSError):
        return {"lines": [], "patterns": []}
    lines = [l for r in rows for l in r.get("lines", [])]
    return {"lines": lines, "patterns": [pattern_of(l) for l in lines]}


def remember(qid: str, lines: list[str]) -> None:
    rows = []
    if HISTORY.exists():
        try:
            rows = json.loads(HISTORY.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            rows = []
    rows.append({"qid": qid, "lines": lines[:40]})
    HISTORY.parent.mkdir(parents=True, exist_ok=True)
    HISTORY.write_text(json.dumps(rows[-40:], ensure_ascii=False, indent=2),
                       encoding="utf-8")


def used_in(script: str) -> list[str]:
    """Connectors from the pools that appear in a finished script."""
    return [line for pool in POOLS.values() for line in pool if line in script]


def brief(subject: str = "Chemistry") -> str:
    """The connector rules, as the script writer is told them."""
    hist = load_history()
    stale = sorted(set(hist["patterns"]))[:12]
    words = ", ".join(SUBJECT_WORDS.get(subject, SUBJECT_WORDS["Chemistry"]))
    pools = "\n".join(
        f"  {name}:\n" + "\n".join(f"    - {l}" for l in lines)
        for name, lines in POOLS.items())
    return f"""
बोलचाल की परत (speech layer) — ये academic परत से अलग है और उसे बदलती नहीं।

काम एक ही है: script ऐसी लगे जैसे एक असली शिक्षक बच्चे से बात कर रहा हो, न कि
किताब पढ़ी जा रही हो। परिभाषा, शब्दावली, सूत्र और exam points जस के तस रहें।

सबसे ज़रूरी नियम: हर पैराग्राफ़ से पहले casual line चिपकाना ज़रूरी नहीं।
लगभग एक-चौथाई जगहों पर कोई connector नहीं होना चाहिए। कसौटी यह है — अगर
connector हटाने पर वाक्य उतना ही स्वाभाविक लगता है, तो उसे मत रखो।

नीचे दिए pools से ही चुनो, और मौक़े के हिसाब से चुनो (opening, transition,
important point, formula, mistake, example, recap, closing):

{pools}

एक ही video में एक connector दोबारा मत दोहराओ, और एक ही आकार (pattern) बार-बार
मत लाओ। पिछले videos में ये आकार पहले ही इस्तेमाल हो चुके हैं, इनसे बचो:
{chr(10).join('  - ' + p for p in stale) if stale else '  (कोई नहीं)'}

सीमाएँ: hook अधिकतम {LIMITS['hook']}, reassurance अधिकतम {LIMITS['reassure']},
exam-emphasis अधिकतम {LIMITS['exam_emphasis']}, "बेटा" अधिकतम {LIMITS['beta']},
closing अधिकतम {LIMITS['closing']}.

{subject} के लिए स्वाभाविक शब्द: {words}.

ये कभी मत लिखो: {', '.join(BANNED)}.

भावनात्मक क्रम: जिज्ञासा → समझ → ध्यान → आश्वासन → आत्मविश्वास → संतोष।
लगातार hype नहीं — सिर्फ़ वहाँ ज़ोर दो जहाँ बात सचमुच ज़रूरी है।
"""
