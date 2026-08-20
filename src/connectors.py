"""The spoken layer: deciding when a teacher would say anything at all.

This is NOT a pool of warm phrases to insert. That was the previous design and
it produced exactly the failure it was meant to prevent — a ready-made line
glued to the front of every important sentence:

    "ज़रा ठहरो, मुख्य बात आ रही है, यही लिखोगे तो पक्के मार्क्स मिलेंगे।"
    "अनन्त तनुता पर किसी विद्युत्-अपघट्य की सीमान्त मोलर चालकता…"

The teacher there sounds like an advertisement wrapped around a textbook. What a
real teacher says is quieter and shorter, and most of the time is nothing:

    "सबसे पहले Kohlrausch का law समझते हैं."
    "अनन्त तनुता पर किसी electrolyte की limiting molar conductivity…"
    "और यहाँ एक important बात है—हर ion का contribution दूसरे ion से
     independent होता है."

THE DECISION, NOT THE PHRASE
----------------------------
For each beat: classify what it is doing, ask whether a connector actually
helps, and only then pick a level. `LEVEL_0` — say nothing — is the default and
the most common outcome, and `speech_style` sets how often the others are even
considered.

THE TEST THAT SETTLES EVERY CASE
--------------------------------
Would the script be better with the connector removed? If yes, remove it. A
connector the student NOTICES has already been over-written; the language is
supposed to disappear into the teaching.

CONNECTORS OFTEN AREN'T SENTENCES
---------------------------------
The most natural result is usually a modification of the academic sentence, not
a new one in front of it:

    worse   "अब एक important point है." / "NaCl में एक Cl⁻ होता है."
    better  "NaCl में एक ही Cl⁻ है, इसलिए यहाँ एक ही λ°(Cl⁻) आएगा."

CONTENT IS THE HOOK
-------------------
Curiosity should come from the concept, not from language wrapped around it.
"अब देखो, BaCl₂ में coefficient दो कहाँ से आया" earns attention; "अब एक बहुत
important point समझते हैं" only announces it.
"""
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

HISTORY = Path("style/connector_history.json")

# Retention and casualness are different dimensions and were previously
# controlled by one knob, which is why turning retention up made the teacher
# sound salesy rather than interested.
DEFAULT_STYLE = {
    "teacher_personality": "warm_expert",
    "language": "simple_hinglish",
    "connector_density": "low",          # low | medium | high
    "emotional_intensity": "low_medium",  # low | low_medium | medium | high
    "academic_priority": "very_high",
    "naturalness_priority": "very_high",
    "student_address_frequency": "low",
    "exam_claim_intensity": "low",
    "creator_style_intensity": "low",
}

# Share of opportunities that should end in NO CONNECTOR at each density.
# Dense academic material wants more silence, not less.
QUIET_RATE = {"low": 0.50, "medium": 0.35, "high": 0.25}

# What a beat is doing. Classified before anything is chosen, because the
# decision follows the role — a formula introduction does not want the same
# treatment as a common mistake.
BEAT_TYPES = [
    "opening", "question_introduction", "concept_introduction", "definition",
    "explanation", "simplification", "example", "formula_introduction",
    "formula_explanation", "derivation", "application", "comparison",
    "common_mistake", "important_point", "exam_writing", "recap",
    "part_transition", "final_closure", "cta",
]

# Beats where a connector rarely earns its place: the academic sentence already
# flows, and anything added is announcement rather than teaching.
USUALLY_SILENT = {
    "explanation", "formula_explanation", "derivation", "application",
    "definition", "concept_introduction",
}

# Claims the system must never invent. They are marketing, and a teacher who
# guarantees marks stops sounding like a teacher.
BANNED = [
    "मार्क्स पक्के", "पक्के मार्क्स", "नंबर पक्के", "चार नंबर पक्के",
    "marks पक्के", "पक्का आएगा", "टॉपर बन जाओगे", "selection पक्का",
    "अबे", "भाई", "ओए", "इतना भी नहीं आता", "तुमसे नहीं होगा",
    "आप यकीन नहीं करेंगे", "99% बच्चे ये नहीं जानते",
]

# Phrases that ASK FOR ATTENTION. At most one may sit around any one academic
# point — the failure is not any single line but the pile-up:
#   "…परिभाषा एकदम सटीक तरीके से सुनो." + "इस बात को दिमाग में बिठा लो," +
#   "पेपर में यही लाइन मांगी जाती है." — three, back to back, before one
# definition. Each is defensible alone; together they are an advertisement.
ATTENTION = [
    "ध्यान से", "दिमाग में बिठा लो", "याद रखना", "मत भूलना", "miss मत करना",
    "ज़रा ठहरो", "सुनो", "important है", "ग़ौर", "note कर लो",
]
STACK_WINDOW = 3        # consecutive spoken lines that count as "one point"

# Frames that ANNOUNCE a mistake instead of naming it. These survive every
# rule about frequency because each script uses one — the defect only shows up
# when you read two scripts side by side and find the same sentence in both
# ("अब फोकस करो, इसी जगह पर उलझन होती है" landed verbatim in the Physics and
# Biology scripts). The fix is to state the wrong idea and the right one in one
# sentence, so flag the frame wherever it appears, even once.
FRAMES = [
    "इसी जगह पर उलझन होती है", "यहाँ उलझन होती है", "यहीं गड़बड़ होती है",
    "यहीं पर गलती होती है", "इसी जगह गलती होती है",
]

# Listing the phrases was not enough. Ban one wording and the next script opens
# the same slot with a different one — "अब फोकस करो, इसी जगह पर उलझन होती है"
# became "इस बात को मन में छाप लो, यही कॉमन गलती आंसर बिगाड़ देती है", again in
# two scripts at once. What repeats is the SHAPE: an announcing clause, then the
# claim that a mistake exists, and only then the actual correction. So match the
# shape — an attention imperative and a mistake word ahead of the em-dash that
# introduces the real content.
ANNOUNCE = re.compile(
    r"(छाप लो|बिठा लो|फ़ोकस|फोकस|ध्यान|याद रख|सुनो|note कर|मन में)")
MISTAKE = re.compile(r"(गलती|ग़लती|उलझन|confuse|बिगाड़|उलट जात|चूक)")


# Not banned — just not filler. Each needs a reason to be there.
RATIONED = {
    "बेटा": 2, "ध्यान से": 2, "दिमाग़ में बिठा लो": 1, "बस": 3,
    "चलो": 3, "देखो": 3, "important": 4, "बच्चों": 2,
}


def style_for(subject: str, topic_type: str = "") -> dict:
    """The speech settings for this script. Dense material gets quieter."""
    s = dict(DEFAULT_STYLE)
    if topic_type in {"derivation", "law", "formula", "numerical"}:
        s["connector_density"] = "low"
    elif topic_type in {"process", "definition"}:
        s["connector_density"] = "medium" if subject == "Biology" else "low"
    return s


def pattern_of(line: str) -> str:
    """A line reduced to its shape, so semantic twins are caught.

    "अब इस point को ध्यान से समझो" and "अब इस बात को ध्यान से समझो" are two
    strings and one sentence; tracking exact text alone lets one shape run
    through a whole script unnoticed.
    """
    words = re.findall(r"[^\s,।?!—:;]+", line)
    keep = {"अब", "चलो", "तो", "बस", "यहाँ", "लेकिन", "अगर", "ये", "इस"}
    return " ".join(w if w in keep else "X" for w in words[:6])


def load_history(n: int = 5) -> dict:
    if not HISTORY.exists():
        return {"lines": [], "patterns": []}
    try:
        rows = json.loads(HISTORY.read_text(encoding="utf-8"))[-n:]
    except (json.JSONDecodeError, OSError):
        return {"lines": [], "patterns": []}
    lines = [l for r in rows for l in r.get("lines", [])]
    return {"lines": lines, "patterns": sorted({pattern_of(l) for l in lines}),
            "used": _connectorish(lines)}


def _connectorish(lines: list[str]) -> list[str]:
    """Recently written lines that ASK for attention, verbatim.

    Shapes alone were not enough. `pattern_of()` truncates to six words and
    replaces most of them with X, so two scripts can share a whole sentence and
    still look different to it — which is how the same misconception line got
    written twice. Whole lines are fed back so the writer can see the actual
    sentence it must not repeat.
    """
    mark = [_norm(m) for m in ATTENTION + FRAMES]
    seen, out = set(), []
    for line in reversed(lines):
        n = _norm(line)
        if not any(m in n for m in mark) or n in seen:
            continue
        seen.add(n)
        out.append(line if len(line) <= 90 else line[:88] + "…")
        if len(out) >= 8:
            break
    return out


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


def _norm(t: str) -> str:
    """Fold nukta variants so दिमाग and दिमाग़ compare equal.

    The audit missed a stacked attention marker because the script wrote दिमाग
    and the list held दिमाग़ — the same word, two codepoint sequences.
    """
    return unicodedata.normalize("NFKD", t).replace("\u093c", "")


def audit(script: str) -> list[str]:
    """Everything in a finished script that the brief forbids or rations."""
    script = _norm(script)
    out = []
    for b in (_norm(x) for x in BANNED):
        if b in script:
            out.append(f"banned claim: {b!r}")
    for word, cap in RATIONED.items():
        n = script.count(_norm(word))
        if n > cap:
            out.append(f"{word!r} used {n}x (max {cap})")
    for f in (_norm(x) for x in FRAMES):
        if f in script:
            out.append(f"warning frame instead of naming the mistake: {f!r}")

    spoken = re.findall(r"“([^”]+)”", script)

    # CJK punctuation reaches TTS verbatim. A script shipped with "जाएगा。" —
    # a full-width stop instead of a danda — and nothing caught it because it
    # looks almost right at a glance.
    for ch in "。，、；：？！":
        if ch in script:
            out.append(f"CJK punctuation in a spoken line: {ch!r}")

    for line in spoken:
        head = re.split(r"[—:]", line, 1)[0]
        if ANNOUNCE.search(head) and MISTAKE.search(head):
            out.append(f"preamble before the correction: {head[:60]!r}")
            break

    # stacking: more than one attention marker inside a short run of lines
    marked = [any(_norm(a) in line for a in ATTENTION) for line in spoken]
    for i in range(len(marked)):
        window = marked[i:i + STACK_WINDOW]
        if sum(window) > 1:
            out.append(f"attention markers stacked around one point "
                       f"(lines {i + 1}-{i + len(window)})")
            break

    shapes = [pattern_of(s) for s in spoken]
    for shape in set(shapes):
        # An all-X shape carries no signal: it just means "a sentence of this
        # many words with none of the tracked opening words". Counting those as
        # repetition flagged every script for writing ordinary prose.
        if set(shape.split()) == {"X"}:
            continue
        if shapes.count(shape) > 3:
            out.append(f"sentence shape repeated {shapes.count(shape)}x: {shape}")
    return out


def brief(subject: str = "Chemistry", topic_type: str = "") -> str:
    """The speech-layer instruction the script writer is given."""
    st = style_for(subject, topic_type)
    quiet = int(QUIET_RATE[st["connector_density"]] * 100)
    hist = load_history()
    stale = hist["patterns"][:10]
    used = hist.get("used", [])
    return f"""
=== बोली की परत (यह academic परत को नहीं बदलती) ===

लक्ष्य: एक असली शिक्षक जो एक बच्चे के सामने बैठकर समझा रहा है। न YouTuber, न
motivational speaker, न विज्ञापन। परिभाषा, शब्दावली, सूत्र और exam points जस के
तस रहें — बोली सिर्फ़ उनके आस-पास के वाक्यों में आए।

क्रम कभी उलटा मत करो: पहले academic सटीकता, फिर स्वाभाविक बोली, उसके बाद कहीं
जाकर भावना।

सबसे ज़रूरी नियम — ज़्यादातर जगह कुछ भी मत जोड़ो।
लगभग {quiet}% मौक़ों पर कोई connector नहीं होना चाहिए। हर paragraph से पहले
casual line लगाना ही गलती है। कसौटी एक ही है: अगर connector हटाने पर script
बेहतर लगती है, तो उसे हटा दो। जिस connector पर बच्चे का ध्यान जाए, वह ज़्यादा
लिखा जा चुका है।

तीन स्तर:
  स्तर 0 — कुछ नहीं। यही default है और सबसे ज़्यादा इस्तेमाल होगा।
           जैसे: "BaCl₂ में दो Cl⁻ हैं, इसलिए यहाँ 2λ°(Cl⁻) आएगा."
  स्तर 1 — छोटा, सामान्य जोड़। सबसे आम connector यही हों।
           जैसे: "चलो, अब इसी को formula से समझते हैं." /
                 "Simple भाषा में समझो." / "यहाँ एक चीज़ ध्यान रखना."
  स्तर 2 — भावनात्मक। तभी, जब सचमुच कारण हो; कम ही आए।
           जैसे: "यहीं पर बच्चे अक्सर confuse होते हैं, इसलिए इसे ठीक से
                 समझ लेते हैं."
"important" लिखा होने भर से स्तर 2 मत लगाओ।

connector अक्सर अलग वाक्य नहीं होता — academic वाक्य को ही स्वाभाविक बना दो:
  कमज़ोर: "अब एक important point है." + "NaCl में एक Cl⁻ होता है."
  बेहतर : "NaCl में एक ही Cl⁻ है, इसलिए यहाँ एक ही λ°(Cl⁻) आएगा."

जिज्ञासा भाषा से नहीं, विषय से पैदा करो:
  कमज़ोर: "अब एक बहुत important बात समझते हैं."
  बेहतर : "अब देखो, BaCl₂ में coefficient दो कहाँ से आया."

जहाँ बच्चों की आम गलती बतानी हो, वहाँ गलती का नाम लो — यह मत बताओ कि यहाँ कोई
गलती होती है। "यहाँ उलझन होती है" जैसा ढाँचा हर विषय पर चिपक जाता है और हर
script में एक ही वाक्य बन जाता है:
  कमज़ोर: "अब फोकस करो, इसी जगह पर उलझन होती है, गलती से सतह के तल के साथ कोण
          ले लेते हैं."
  बेहतर : "कोण सतह के तल से नहीं लिया जाता — हमेशा बाहर की ओर अभिलम्ब से."
गलत बात और सही बात एक ही वाक्य में आमने-सामने रखो; चेतावनी अलग से मत लगाओ।

यह शब्दों की नहीं, ढाँचे की बात है। यह ढाँचा पूरी तरह मना है:
  [ध्यान माँगने वाला वाक्यांश] + [यहाँ गलती होती है] + "—" + [असली सुधार]
सिर्फ़ वाक्यांश बदल देने से बात नहीं बनती — "फोकस करो" की जगह "मन में छाप लो"
लिखना वही गलती दोबारा करना है। सुधार सीधे पहले शब्द से शुरू होना चाहिए।

exam की बात शिक्षक की सलाह जैसी हो, दावे जैसी नहीं:
  कमज़ोर: "ये लिख दिया तो मार्क्स पक्के."
  बेहतर : "Definition में ये दोनों points लिखना, तभी answer पूरा होगा."

ये कभी मत लिखो: {', '.join(BANNED[:8])}.
ये शब्द सीमित हैं (हर एक को कारण चाहिए):
{', '.join(f'{w} ≤ {c}' for w, c in RATIONED.items())}.

एक ही academic बिंदु के आस-पास एक से ज़्यादा attention marker मत लगाओ। लगातार
तीन पंक्तियों में एक से ज़्यादा नहीं। यह ढेर सबसे बड़ी गलती है:
  गलत: "…परिभाषा एकदम सटीक तरीके से सुनो." + "इस बात को दिमाग में बिठा लो," +
        "पेपर में यही लाइन मांगी जाती है." फिर परिभाषा।
  सही : "सबसे पहले कोलराउश का नियम समझते हैं." फिर सीधे परिभाषा।
हर एक अलग-अलग ठीक लगता है; तीनों साथ में विज्ञापन बन जाते हैं।

"एंड तक रहोगे तो…" वाली retention-promise सिर्फ़ शुरुआत की उस एक तय पंक्ति में
चलती है (hook → वर्ष-पंक्ति → promise)। उसके बाद पूरे script में दोबारा कहीं
भी दर्शक को रोके रखने का वादा मत लिखो।

एक ही video में कोई वाक्य-आकार बार-बार मत दोहराओ। पिछले scripts में ये आकार
पहले ही इस्तेमाल हो चुके हैं:
{chr(10).join('  - ' + p for p in stale) if stale else '  (कोई नहीं)'}

ये पूरी पंक्तियाँ पिछले scripts में लिखी जा चुकी हैं। इन्हें दोबारा मत लिखो —
न ज्यों की त्यों, न थोड़ा बदलकर:
{chr(10).join('  - ' + u for u in used) if used else '  (कोई नहीं)'}

भाग बदलते समय अंत और अगली शुरुआत को एक जोड़ी की तरह लिखो — अगला भाग वहीं से
उठे जहाँ पिछला छूटा। "अगले पार्ट में मिलते हैं" तभी, जब सचमुच ठीक बैठे।

अंत: संक्षेप → आत्मविश्वास → (ज़रूरत हो तो) एक CTA। "like/share/follow" अपने
आप मत जोड़ो।

भावनात्मक क्रम: जिज्ञासा → स्पष्टता → ध्यान → समझ → आत्मविश्वास → संतोष।
hook → hook → important → marks → hook नहीं।
"""
