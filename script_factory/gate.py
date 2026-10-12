#!/usr/bin/env python3
"""Mechanical checks on a PYQ reel script. No model calls — regex, counts, coverage.

Everything here was derived from the 111 shipped scripts catalogued in
``script_index/``; each check names the corpus pattern it enforces. A check only
exists if breaking it would be a visible defect in the delivered video, and every
threshold was calibrated so that the clean shipped scripts pass (see
``calibrate.py``). A gate that fails the team's own approved work is a gate nobody
will keep running.

    python3 script_factory/gate.py draft.md --answer answer.txt --years 2019,2022 \
        --category LA --json report.json

Exit 0 = deliverable. Exit 1 = errors. Warnings never block on their own.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from dataclasses import dataclass, asdict, field
from pathlib import Path

# --------------------------------------------------------------------------- #
# Parsing                                                                      #
# --------------------------------------------------------------------------- #
# The corpus writes these eight ways (DEFECTS.md); accept all of them, plus the
# clean form new scripts use.
SCREEN_RE = re.compile(r"^\s*[\[\(]?\s*(?:ON\s*SCREEN|On\s*Screen|On\s*SCREEN|स्क्रीन\s*पर)\s*[:：\-–—]?", re.I)
SPOKEN_LABEL_RE = re.compile(r"^\s*(?:स्पोकन|SPOKEN)\s*[:：]?", re.I)
# "भाग N" is NOT a part — one chemistry script has five भाग in a single video.
# "Part N Ending" is the last beat OF part N, not the start of a new one.
PART_RE = re.compile(r"^\s*[*_#\s]*(?:🎬\s*)?(?:PART|Part)\s*[-–—]?\s*(\d+|एक|दो|तीन|One|Two|Three)\b"
                     r"(?!\s*(?:Ending|ending|एंडिंग))", re.I)
SPEAKER_RE = re.compile(r"^\s*[*_#\s]*[Yy]?(?:शिक्षक|Teacher|[A-Z][a-z]+\s+Sir)\s*[:：]")
HEADER_RE = re.compile(r"^\s*[*_#\s]*(?:प्रश्न|Question|Qsn|QID|वर्ष|श्रेणी|MP Board कक्षा 12\b|अथवा)\s*[-:：]", re.I)
RULE_RE = re.compile(r"^[\s*_=─━—–\-•★🎙️🎬]+$")

DECOR = "“”\"'‘’*_#★•🎙️🎬"


def clean_line(s: str) -> str:
    s = s.strip()
    s = s.replace("**", "").replace("__", "")      # markdown survives from Google Docs
    s = re.sub(r"^[*_#\s]+|[*_\s]+$", "", s)
    return s.strip(DECOR).strip()


@dataclass
class Part:
    number: int
    spoken: list[tuple[int, str]] = field(default_factory=list)   # (line_no, text)
    screen: list[tuple[int, str]] = field(default_factory=list)
    lines: list[tuple[int, str, str]] = field(default_factory=list)  # (line_no, kind, text)


@dataclass
class Script:
    path: str
    header: list[str]
    parts: list[Part]

    @property
    def all_spoken(self) -> list[tuple[int, str]]:
        return [t for p in self.parts for t in p.spoken]

    @property
    def spoken_text(self) -> str:
        return " ".join(t for _, t in self.all_spoken)


def parse(path: str | Path) -> Script:
    raw = Path(path).read_text(encoding="utf-8-sig")
    all_lines = raw.split("\n")

    # The script BEGINS at the opener ("MP Board कक्षा 12वीं के बच्चों…"), or at the
    # first part divider. Everything above it — the title, the question, the अथवा
    # variants, the year — is the header. Without this the first spoken line is a
    # title like "पारिस्थितिक पिरामिड — Biology Reel Script" and every opening
    # check fires on a script that is in fact correct.
    body_start = 0
    for i, line in enumerate(all_lines):
        if OPENER_RE.search(line) or PART_RE.match(line.strip()):
            body_start = i
            break

    header: list[str] = [l.strip() for l in all_lines[:body_start] if l.strip()]
    parts: list[Part] = []
    cur = Part(number=1)
    in_screen = False
    seen_body = False

    for n, line in enumerate(all_lines[body_start:], body_start + 1):
        stripped = line.strip()
        if not stripped or RULE_RE.match(stripped):
            in_screen = False
            continue
        if PART_RE.match(stripped):
            m = PART_RE.match(stripped)
            word = {"एक": 1, "one": 1, "दो": 2, "two": 2, "तीन": 3, "three": 3}
            try:
                num = int(m.group(1))
            except ValueError:
                num = word.get(m.group(1).lower(), len(parts) + 1)
            # A "PART 1" divider that arrives after we have already collected lines
            # is the heading of the part we are in, not the start of a second one.
            # Without this every script ends up with two part 1s and the bridge
            # check fires on the opening line of the video.
            if num == cur.number and cur.lines:
                in_screen = False
                continue
            if cur.lines:
                parts.append(cur)
            cur = Part(number=num)
            in_screen = False
            seen_body = True
            continue
        if SPEAKER_RE.match(stripped):          # a beat separator, not a speaker
            in_screen = False
            continue
        if SCREEN_RE.match(stripped):
            rest = SCREEN_RE.sub("", stripped).strip(" :：[]()").strip()
            in_screen = True
            if rest:                            # inline form: [On Screen: …]
                cur.screen.append((n, rest))
                cur.lines.append((n, "screen", rest))
            continue
        if SPOKEN_LABEL_RE.match(stripped):     # physics' explicit read-out label
            rest = SPOKEN_LABEL_RE.sub("", stripped).strip()
            in_screen = False
            if rest:
                txt = clean_line(rest)
                cur.spoken.append((n, txt))
                cur.lines.append((n, "spoken", txt))
            continue
        if not seen_body and HEADER_RE.match(stripped):
            header.append(stripped)
            continue
        txt = clean_line(stripped)
        if not txt:
            continue
        seen_body = True
        # An ON SCREEN block ends at a blank line — but plenty of scripts have none,
        # and then every later line was being read as screen text (the whole closing
        # CTA included). Screen items are short labels; narration is a sentence, is
        # quoted, or carries the ★ aside marker.
        if in_screen and (len(txt.split()) > 10 or stripped[0] in "★“\"'"):
            in_screen = False
        if in_screen:
            cur.screen.append((n, txt))
            cur.lines.append((n, "screen", txt))
        else:
            cur.spoken.append((n, txt))
            cur.lines.append((n, "spoken", txt))
    if cur.lines:
        parts.append(cur)
    return Script(path=str(path), header=header, parts=parts or [Part(1)])


# --------------------------------------------------------------------------- #
# Findings                                                                     #
# --------------------------------------------------------------------------- #
@dataclass
class Finding:
    code: str
    severity: str        # error | warn
    message: str
    line: int | None = None
    text: str = ""

    def fmt(self) -> str:
        where = f"line {self.line}" if self.line else "script"
        tail = f'\n      “{self.text[:110]}”' if self.text else ""
        return f"  [{self.severity.upper():5}] {self.code:12} {where}: {self.message}{tail}"


# --------------------------------------------------------------------------- #
# Vocabulary the corpus rejects                                                #
# --------------------------------------------------------------------------- #
# Every phrase here is one the editors removed from an AI draft before shooting,
# or that appears only in the deprecated 2-script closing block.
BANNED = {
    "मार्क्स": "the corpus says नंबर, never मार्क्स",
    "वेलकम बैक": "no script welcomes the student back; open by naming what the last part established",
    "वापस आ गए": "same — open a part with its recap, not a greeting",
    "सेट है": "creator filler; not in the corpus",
    "सेट हो गया": "creator filler; not in the corpus",
    "फॉलो कर": "the corpus never asks for a follow; the close is the Notes button",
    "फॉलो करना": "the corpus never asks for a follow; the close is the Notes button",
    "टेंशन खत्म": "creator filler; not in the corpus",
    "दोस्तों": "the address term is बच्चों",
    "यकीन नहीं करेंगे": "hype; banned house-wide",
    "चौंका देगा": "hype; banned house-hwide",
    "99%": "invented statistic",
    "बहुत सारे बच्चे यहीं गलती करते हैं": "generic mistake line — zero of the 111 scripts keep it; name the actual confusion",
}
ROMAN_HINDI = re.compile(
    r"\b(?:bacho|bachho|yaad|rakho|karo|karna|karte|kyoki|kyunki|samajh|samjho|dhyan|"
    r"matlab|tarika|aasani|milenge|dekho|dekhna|sunna|likhna|likho|paoge|yaani|yani|"
    r"shareer|hota|hoti|hain|thoda|zyada|jyada|wala|wale|isliye|phir|bhool|"
    r"hi\s+number)\b", re.I)
# Devanagari-script English that the corpus writes in Latin instead.
DEVA_ENGLISH = {"आंसर": "answer", "नेक्स्ट": "next", "एंड": "end", "फॉर्मैट": "format",
                "कन्फर्म": "confirm", "फोकस": "focus"}

JUNK = [(re.compile(r"\\[a-zA-Z]+"), "raw LaTeX"),
        (re.compile(r"\$[^$]{1,60}\$"), "LaTeX math delimiters"),
        (re.compile(r"(?<![\w])\[[a-z]\](?![\w])"), "Google Docs comment anchor"),
        (re.compile(r"[A-Za-z]_[A-Za-z]"), "LaTeX subscript leftover (EaE_a style)"),
        (re.compile(r"\b([A-Za-z]{2,4})\1\b"), "doubled token from a collapsed formula (dSdS style)")]

HINDI_NUM = {"एक": 1, "दो": 2, "तीन": 3, "चार": 4, "पाँच": 5, "पांच": 5, "छह": 6,
             "दोनों": 2, "तीनों": 3, "चारों": 4, "पाँचों": 5}
ORDINALS = [("पहला", "पहली", "पहले"), ("दूसरा", "दूसरी", "दूसरे"), ("तीसरा", "तीसरी", "तीसरे"),
            ("चौथा", "चौथी", "चौथे"), ("पाँचवाँ", "पाँचवीं", "पांचवा"), ("छठा", "छठी", "छठवाँ")]

OPENER_RE = re.compile(r"(MP\s*Board|एमपी\s*बोर्ड)\s*कक्षा\s*(12|बारहवीं|12वीं)")
IMPORTANCE_OPENER_RE = re.compile(r"(महत्वपूर्ण|important|अध्याय|चैप्टर|बहुत\s*ज़रूरी)")
NOTES_RE = re.compile(r"(Notes|नोट्स)")   # "Notes button", "Notes पर", "Notes में"
KEEP_WATCHING_RE = re.compile(r"(reels?|रील|रील्स|पढ़ाई\s*वाली)", re.I)
GOAL_RE = re.compile(r"(90|नब्बे|syllabus|सिलेबस|तैयारी|लक्ष्य)", re.I)
OLD_CLOSE_RE = re.compile(r"(उन्नति\s*बैच|स्क्रीनशॉट|screenshot)", re.I)
BRIDGE_RE = re.compile(r"(Part|पार्ट|भाग)\s*(1|2|3|एक|दो|तीन|one|two|वन|टू)\s*(में|me)|"
                       r"(पिछले|पहले)\s*(पार्ट|भाग|part)|अब\s*तक|यहाँ\s*तक", re.I)
DONE_RE = re.compile(r"(हो\s*गय[ाीे]|हो\s*गए|कर\s*ल[ियीे]|समझ\s*(आ\s*गया|गए|ल[ियीे])|देख\\s*ल[ियीे]|पूरा\\s*(हुआ|हो)|यहाँ\\s*तक|अभी\\s*तक)")
LEFT_RE = re.compile(r"(बाकी|बचा|बचे|अभी\s*और|next\s*part|नेक्स्ट|अगल[ेा]|आगे\s*वाल|"
                     r"(?:पार्ट|part)\s*(?:टू|थ्री|दो|तीन|two|three|\d))", re.I)
WATCH_RE = re.compile(r"(ज़रूर\s*देखना|जरूर\s*देखना|मिस\s*मत|देखते\s*रहो|miss\s*mat)", re.I)
EMPHASIS_RE = re.compile(r"(ध्यान\s*से\s*(सुनना|समझना|देखना)|याद\s*रख|दिमाग\s*में\s*(बिठा|बैठा)|"
                         r"गाँठ\s*बाँध|मन\s*में\s*छाप|ध्यान\s*रखना)")
REASON_RE = re.compile(r"(क्योंकि|इसलिए|वरना|तभी|ताकि|kyoki|यही\s*तो|इसी\s*(वजह|कारण))")
DEVA_RE = re.compile(r"[ऀ-ॿ]")


def is_formula(s: str) -> bool:
    """True for an equation or a chemical reaction, false for a labelled arrow chain.

    The corpus uses → for both "Zn → Zn²⁺ + 2e⁻" (a reaction, which must be read
    aloud) and "Micropyle के opposite end → निभाग" (a label map, which is just the
    caption of something already said). Treating the second as a formula made this
    check fire 460 times on the team's own scripts.
    """
    if re.search(r"[\w₀-₉⁰-⁹)]\s*=\s*[\w₀-₉⁰-⁹(√-]", s) or re.search(r"[⇌∝∮∫]", s):
        return True
    if re.search(r"[→←]", s) and not DEVA_RE.search(s):
        # a reaction ("Zn → Zn²⁺ + 2e⁻"), not a flow of English phrases
        toks = [t for t in s.replace("→", " ").replace("+", " ").split() if t]
        return bool(re.search(r"[₀-₉⁰-⁹⁺⁻²³]", s)) or all(len(t) <= 6 for t in toks)
    return bool(re.search(r"\b\d+(\.\d+)?\s*[×x*/]\s*\d", s))
READOUT_RE = re.compile(r"(बराबर|गुना|बटा|बटे|upon|plus|minus|into|equals|जोड़|घटा|"
                        r"वर्ग|स्क्वायर|माइनस|प्लस|पॉइंट|by\s+\w)", re.I)
META_RE = re.compile(r"(exam|परीक्षा|नंबर|नम्बर|answer|आंसर|उत्तर|लिखना|लिखोगे|कॉपी|"
                     r"Notes|नोट्स|marks|पेपर|board)", re.I)
AAP_RE = re.compile(r"(लीजिए|कीजिए|समझिए|देखिए|रखिए|लिखिए|सुनिए|आपको\s*चाहिए)")
TUM_RE = re.compile(r"(समझ\s*लो|देख\s*लो|याद\s*रखो|लिख\s*लो|सुनो|कर\s*लो|रखना|बिठा\s*लो|जाओ)")


def tokens(s: str) -> set[str]:
    s = unicodedata.normalize("NFC", s)
    return {w for w in re.split(r"[^\wऀ-ॿ]+", s.lower()) if len(w) > 2}


# --------------------------------------------------------------------------- #
# The checks                                                                   #
# --------------------------------------------------------------------------- #
def check(script: Script, *, answer: str = "", question: str = "",
          years: list[str] | None = None, category: str = "",
          style: str = "auto", strict: bool = False) -> list[Finding]:
    F: list[Finding] = []
    add = lambda *a, **k: F.append(Finding(*a, **k))
    parts = script.parts
    spoken = script.all_spoken
    if not spoken:
        add("E-EMPTY", "error", "No spoken lines found — check the script's format.")
        return F
    joined = script.spoken_text
    if style == "auto":
        # A script naming the उन्नति बैच belongs to the older closing generation
        # and must not be judged against the Notes-button stack.
        style = "legacy" if re.search(r"उन्नति\s*बैच", joined) else "current"

    # --- opening (intro.board_year_repeat — 92/111 scripts) ------------------
    # Allow the opener to be in the first three spoken lines: a few scripts read the
    # question back before it. Anything later is not an opening.
    opening = spoken[:3]
    if not any(OPENER_RE.search(t) for _, t in opening):
        if not any(IMPORTANCE_OPENER_RE.search(t) for _, t in opening):
            add("E-OPEN", "error",
                "Part 1 must open on the board/class/year line (92 of 111 shipped scripts), "
                "or on an importance/chapter frame when the question has no year.",
                spoken[0][0], spoken[0][1])
    head = " ".join(t for _, t in spoken[:4])
    said_years = set(re.findall(r"\b20[0-2]\d\b", head))
    for y in (years or []):
        if y in said_years:
            continue
        if said_years:
            add("E-YEAR", "error",
                f"The opener names {', '.join(sorted(said_years))} but the sheet says this question "
                f"was asked in {y}. Verify it — a wrong year is the first thing the student hears.",
                spoken[0][0], head[:120])
        else:
            add("W-YEAR", "warn",
                f"The opener names no year, though this question was asked in {y}.",
                spoken[0][0], head[:120])
    if not years and re.search(r"\b20[0-2]\d\b", head):
        add("W-YEAR", "warn", "The opener names a year but none was supplied — verify it.",
            spoken[0][0], head[:120])

    # --- closing block (end.* — fixed stack, only in the final part) ---------
    last = parts[-1]
    # Search the whole final part: several scripts have production notes appended
    # after the sign-off, which pushes the CTA well above the last lines.
    tail = " ".join(t for _, t in last.spoken)
    if style == "current":
        if not NOTES_RE.search(tail):
            add("E-CLOSE", "error",
                "The final part must close on the Notes button line (103 of 111 scripts).",
                last.spoken[-1][0] if last.spoken else None, tail[-120:])
        if not KEEP_WATCHING_RE.search(tail) and not GOAL_RE.search(tail):
            add("W-CLOSE", "warn",
                "The close stops at the Notes button. The usual stack continues: keep "
                "watching the reels → finish the syllabus → 90%.", None, tail[-120:])
        if re.search(r"उन्नति\s*बैच", tail):
            add("E-MIXCLOSE", "error",
                "The deprecated उन्नति बैच close is mixed with the current Notes-button "
                "close. The two closing blocks are mutually exclusive.", None, tail[-120:])
        elif OLD_CLOSE_RE.search(tail):
            add("W-MIXCLOSE", "warn",
                "The close asks for a screenshot as well as pointing at the Notes button. "
                "Recent scripts use the Notes button alone.", None, tail[-120:])
    for p in parts[:-1]:
        for ln, t in p.spoken:
            if NOTES_RE.search(t) or OLD_CLOSE_RE.search(t):
                add("E-CLOSE-EARLY", "error",
                    f"The closing CTA appears in part {p.number}; only the final part carries it.",
                    ln, t)

    # --- banned vocabulary ---------------------------------------------------
    for ln, t in spoken:
        for phrase, why in BANNED.items():
            if phrase in t:
                add("E-BANNED", "error", f"“{phrase}” — {why}.", ln, t)
        if ROMAN_HINDI.search(t):
            add("W-ROMAN", "warn",
                "Romanised Hindi — a typing artefact in the corpus, not house style. "
                "Write it in Devanagari.", ln, t)
        for deva, eng in DEVA_ENGLISH.items():
            if deva in t:
                add("W-DEVA-ENG", "warn",
                    f"“{deva}” — the corpus writes this English word in Latin script ({eng}).", ln, t)
        for rx, what in JUNK:
            if rx.search(t):
                add("E-JUNK", "error", f"{what} in a spoken line.", ln, t)
        # HeyGen voices the line as written: "Ni²⁺" and "संरचना-I" come out as
        # symbol names or "आई". The corpus's own fix is the spoken read-out
        # ("Ni two plus", "संरचना एक"). Three reviewers caught this on the first
        # generated script after the gate had passed it.
        # ¹ ² ³ live in Latin-1 (U+00B9/B2/B3), not in the U+2070 block with the rest
        sym = re.findall(r"[A-Za-z)\]][⁰¹²³⁴-⁹⁺⁻]+|[A-Za-z)\]][₀-₉]+", t)
        roman = re.findall(r"(?:संरचना|भाग|प्रकार|चरण|पद)\s*[-–]?\s*(?:I{1,3}|IV|V)\b", t)
        if sym or roman:
            add("W-SYMBOL", "warn",
                f"Symbols in a spoken line ({', '.join((sym + roman)[:4])}) — HeyGen reads them "
                f"literally. Speak them: “Ni two plus”, “S O four two minus”, “संरचना एक”.", ln, t)
        if len(t.split()) > 38:
            add("W-LINE", "warn",
                f"{len(t.split())} words in one line — the corpus median is 12, p90 is 26.", ln, t)

    # --- part mechanics (bridge.* / handoff.*) -------------------------------
    # In some scripts "Part 1/2/3" are section headings inside ONE video — one
    # opening, one closing, no recaps (DEFECTS.md). Those must not be judged as
    # separate reels, so detect the shape before checking it.
    real_parts = len(parts) > 1 and any(
        BRIDGE_RE.search(" ".join(t for _, t in p.spoken[:2])) or
        WATCH_RE.search(" ".join(t for _, t in p.spoken[-4:])) for p in parts[1:])
    if len(parts) > 1 and not real_parts:
        add("W-SECTIONS", "warn",
            f"{len(parts)} `PART` dividers, but no part opens with a recap and none points "
            f"at the next one. These read as section headings inside one video, not as "
            f"separate reels. If they are separate reels, each needs a bridge and a handoff.")
    if real_parts:
        for p in parts[1:]:
            opening = " ".join(t for _, t in p.spoken[:2])
            if not BRIDGE_RE.search(opening):
                add("E-BRIDGE", "error",
                    f"Part {p.number} must open by naming what the previous part established "
                    f"— each part publishes as its own reel (65 of 111 scripts).",
                    p.spoken[0][0] if p.spoken else None, opening[:120])
        for p in parts[:-1]:
            ending = " ".join(t for _, t in p.spoken[-5:])
            # The corpus fills this slot three ways (handoff.done_plus_left,
            # handoff.open_question, handoff.watch_next). Any one of them hands the
            # student forward; requiring all three failed 143% of the corpus.
            if not (DONE_RE.search(ending) or LEFT_RE.search(ending) or WATCH_RE.search(ending)):
                add("E-HANDOFF", "error",
                    f"Part {p.number} ends without handing the student forward. Name what is "
                    f"done and what is left (“X हो गया, अब Y बाकी”), or point at the next part.",
                    p.spoken[-1][0] if p.spoken else None, ending[-140:])

    # --- the count contract (rule 2) -----------------------------------------
    announced = None
    for ln, t in spoken[:14]:
        m = re.search(r"\b(दोनों|तीनों|चारों|पाँचों)\b", t) or \
            re.search(r"\b(दो|तीन|चार|पाँच|पांच)\s+(?:अलग|अंतर|difference|कारण|गुण|step|steps|"
                      r"बात|बातें|प्रकार|type|types|विशेषता|नियम|चीज)", t)
        if m:
            announced = HINDI_NUM.get(m.group(1))
            if announced:
                break
    if announced:
        found = sum(1 for grp in ORDINALS[:announced]
                    if any(any(w in t for w in grp) for _, t in spoken))
        if found < announced:
            add("E-COUNT", "error",
                f"The opening announces {announced} items but only {found} are counted out "
                f"(पहला / दूसरा / …). The announced count is a contract the recap must honour.")

    # --- every on-screen formula needs a spoken read-out (rule 4) ------------
    for p in parts:
        for ln, s in p.screen:
            # "I → [Ni(NH₃)₅(SCN)]Cl" reads as "I reacts to give …"; a student copies
            # the arrow. Labels take a colon. Caught by review on the first script.
            if re.match(r"^\s*(?:I{1,3}|IV|V|\d|[A-Za-z])\s*[→⟶]\s*[\[(A-Z]", s):
                add("W-LABEL-ARROW", "warn",
                    "An arrow used as a label on screen reads as a reaction and gets copied "
                    "into answers. Use a colon: “I : [Ni(NH₃)₅(SCN)]Cl”.", ln, s)
            if not is_formula(s):
                continue
            near = [t for l2, t in p.spoken if abs(l2 - ln) <= 12]
            spoken_near = " ".join(near)
            has_readout = any(READOUT_RE.search(t) for t in near)
            # include 2-character symbols (Ca, Mg, dS, q₁) — tokens() drops them
            need = tokens(s) | {w.lower() for w in re.findall(r"[A-Za-zα-ωΑ-Ω]{2,}", s)}
            near_tok = tokens(spoken_near) | {w.lower() for w in
                                              re.findall(r"[A-Za-zα-ωΑ-Ω]{2,}", spoken_near)}
            names_it = bool(need) and len(need & near_tok) / len(need) >= 0.4
            if not (has_readout or names_it):
                add("E-READOUT", "error",
                    "This on-screen formula has no spoken read-out near it. Nothing on "
                    "screen is ever left unspoken.", ln, s)
    if not any(p.screen for p in parts):
        add("W-NOSCREEN", "warn",
            "No ON SCREEN blocks. 15 of 111 shipped scripts have none and all 15 are "
            "unfinished on the visual side.")

    # --- register consistency (rule 5) ---------------------------------------
    aap, tum = len(AAP_RE.findall(joined)), len(TUM_RE.findall(joined))
    if aap >= 3 and tum >= 3 and min(aap, tum) / max(aap, tum) > 0.35:
        add("W-REGISTER", "warn",
            f"Mixed register: {aap} आप-form and {tum} तुम-form imperatives. Pick one and hold it.")

    # --- length targets (metrics.json) ---------------------------------------
    words = len(joined.split())
    # Ceiling = the corpus 75th percentile per category (SA 633, LA 1087, NM 1092).
    # The first generated script ran 907 words for a Short Answer and the user sent it
    # back as "too long, too much explanation" — the old 900 ceiling let it through.
    TARGET = {"LA": (400, 1087), "NM": (300, 1092), "SA": (150, 633), "VS": (100, 450)}
    if category.upper() in TARGET:
        lo, hi = TARGET[category.upper()]
        if not lo <= words <= hi:
            add("W-LENGTH", "warn",
                f"{words} spoken words for a {category.upper()} question; the shipped range "
                f"is {lo}–{hi} (≈{words/158:.1f} min at 158 wpm).")
    for p in parts:
        pw = sum(len(t.split()) for _, t in p.spoken)
        if len(parts) > 1 and pw > 480:
            add("W-PART-LEN", "warn",
                f"Part {p.number} is {pw} words (≈{pw/158:.1f} min). Shipped parts run ~290 words.")

    # --- the user's review: direct intro, few hooks, equations described -------
    # Intro: the corpus spends a median of 2 spoken lines before teaching starts
    # (p75 = 3). The first generated script spent 6.
    TEACH_START = re.compile(r"(कहते हैं|कहलाते|कहलाती|कहलाता|होता है|होती है|होते हैं|"
                             r"सबसे पहले|पहला|पहली)")
    intro_n = 0
    for i, (ln, t) in enumerate(parts[0].spoken):
        if i > 0 and TEACH_START.search(t):
            break
        intro_n += 1
    if intro_n > 3:
        add("W-INTRO", "warn",
            f"{intro_n} spoken lines before teaching starts; the corpus median is 2. "
            f"Open with the board line, then go straight into the first item.",
            parts[0].spoken[0][0], " / ".join(t for _, t in parts[0].spoken[:intro_n])[:160])

    # Hooks: count the casual/meta lines. Corpus p75 per category.
    HOOK_RE = re.compile(r"(ध्यान\s*से|ध्यान\s*रख|ध्यान\s*दो|याद\s*रख|दिमाग\s*में|गाँठ|"
                         r"मन\s*में\s*छाप|पक्का\s*कर|important|ज़रूर\s*देख|जरूर\s*देख|मिस\s*मत|"
                         r"नंबर\s*कट|पूरे\s*नंबर|नंबर\s*पक्के|बच्चे\s*अक्सर|confus|गलती|सवाल\s*ये\s*है|"
                         r"चलो|तो\s*बच्चों|exam\s*में|परीक्षा\s*में)")
    HOOK_MAX = {"SA": 8, "LA": 19, "NM": 9, "VS": 6}
    hooks = [(ln, t) for ln, t in spoken if HOOK_RE.search(t)]
    cap = HOOK_MAX.get(category.upper())
    if cap and len(hooks) > cap:
        add("W-HOOKS", "warn",
            f"{len(hooks)} hook/meta lines; the corpus 75th percentile for {category.upper()} "
            f"is {cap} (median {dict(SA=6, LA=15, NM=8, VS=4)[category.upper()]}). Cut the ones the "
            f"line works without.", None, " | ".join(t[:40] for _, t in hooks[:6]))

    # Equations are described, not spelled out bracket by bracket.
    for ln, t in spoken:
        if re.search(r"\b(?:open|close)\s+(?:square\s+)?bracket\b", t, re.I):
            add("E-SPELLOUT", "error",
                "A formula spelled out bracket by bracket. Describe it in Hindi instead: "
                "“इसमें Co के साथ पाँच अमोनिया और ब्रोमाइड अंदर हैं, और सल्फेट बाहर।” / "
                "“लेड, सल्फेट आयन से मिलकर PbSO₄ बनाता है।” The user rejected the spell-out.",
                ln, t)

    # --- spoken register: connectors the presenter would never say ----------
    # Measured on the 111 scripts: outside textbook sentences they say ये 76% of the
    # time (यह 24%), वो 82%, लेकिन 99%, और 98% — and even INSIDE the textbook
    # sentences they say लेकिन 12 : किन्तु 0 and और 392 : तथा 19. Technical terms
    # stay exactly as the book writes them; connectors are always spoken ones.
    FORMAL = {"यह": "ये", "वह": "वो", "तथा": "और", "एवं": "और", "किन्तु": "लेकिन",
              "किंतु": "लेकिन", "परन्तु": "पर", "परंतु": "पर", "अतः": "इसलिए",
              "अर्थात्": "यानी", "अर्थात": "यानी", "केवल": "सिर्फ", "हेतु": "के लिए",
              "इस प्रकार": "ऐसे / इस तरह"}
    for ln, t in spoken:
        hit = [f"{w}→{r}" for w, r in FORMAL.items()
               if re.search(rf"(?<![\u0900-\u097F]){re.escape(w)}(?![\u0900-\u097F])", t)]
        if hit:
            add("W-FORMAL", "warn",
                f"Written-Hindi connector in a spoken line ({', '.join(hit)}). Nobody says these "
                f"aloud; the corpus uses the spoken form even inside textbook sentences. "
                f"Keep the technical terms, change the connector.", ln, t)

    # --- hooks in the MIDDLE, where they keep the student watching ------------
    # The corpus spreads attention hooks evenly (~20% in every fifth of a script)
    # and a Short Answer carries a median of 2 (p75 5) between 12% and 85% of the
    # way through — each one right before the trap or key line it flags, and
    # usually naming it: "अब ये ध्यान से समझो कि …", "यहीं पर सबसे ज्यादा बच्चे
    # उलझते हैं". A script with hooks only at the seams reads flat.
    ATTN = re.compile(r"(ध्यान\s*(से|दो|देना|रखना|रखो)|important|ज़रूरी|जरूरी|गलती|confus|उलझ|"
                      r"याद\s*रख|दिमाग\s*में|गाँठ|पक्का|असली\s*(बात|फर्क|सवाल)|सबसे\s*ज़रूरी|"
                      r"हल्के\s*में\s*मत)")
    n_sp = len(spoken)
    mid_hooks = [(i, ln, t) for i, (ln, t) in enumerate(spoken)
                 if ATTN.search(t) and n_sp > 5 and 0.12 <= i / (n_sp - 1) <= 0.85]
    need = {"SA": 2, "LA": 3, "NM": 2, "VS": 1}.get(category.upper(), 2)
    if n_sp > 8 and len(mid_hooks) < need:
        add("W-FLAT", "warn",
            f"{len(mid_hooks)} attention hook(s) in the middle of the script; a "
            f"{category.upper() or 'script'} in the corpus has at least {need}. Put one right "
            f"before each trap or key line — “अब ध्यान दो, …”, “अब ये ध्यान से समझना, "
            f"यहीं बच्चे सबसे ज्यादा उलझते हैं।”")
    # every hook the same kind ("ध्यान से सुनना / ध्यान दो / ध्यान से समझना") reads as one
    # hook said three times — the second review of CHE-C5-SA-05 failed on exactly that
    if len(mid_hooks) >= 2 and all(re.search(r"ध्यान", t) for _, _, t in mid_hooks):
        add("W-HOOK-SAME", "warn",
            "Every mid-script hook is a ध्यान hook. Vary the kind: importance (“ये बहुत "
            "important है, क्योंकि …”), trap (“यहीं पर बच्चे अक्सर उलझते हैं कि …”), "
            "curiosity (“तो फिर फर्क कहाँ है?”).")
    # a hook dropped between a line and its gloss orphans the gloss
    for i, ln, t in mid_hooks:
        if i + 1 < n_sp and re.match(r"^\s*(यानी|यानि|मतलब)", spoken[i + 1][1]):
            add("W-HOOK-SPLIT", "warn",
                "This hook sits between a line and its यानी/मतलब gloss, so the gloss now "
                "seems to explain the hook. Move the hook before the line it flags.", ln, t)
    for (i1, l1, t1), (i2, l2, t2) in zip(mid_hooks, mid_hooks[1:]):
        if i2 == i1 + 1:
            add("W-HOOK-STACK", "warn",
                "Two attention hooks back to back. One hook, then the point it flags.", l2, t2)

    # --- answer coverage (only when the source answer is supplied) -----------
    if answer.strip():
        script_tok = tokens(joined + " " + " ".join(t for p in parts for _, t in p.screen))
        for sent in re.split(r"(?<=[।?!\n])\s+", answer):
            st = sent.strip()
            if len(st.split()) < 4:
                continue
            need = tokens(st)
            if not need:
                continue
            hit = len(need & script_tok) / len(need)
            if hit < 0.5:
                add("E-COVERAGE", "error",
                    f"This sentence of the source answer is not covered by the script "
                    f"({hit:.0%} of its terms appear). Every mark-bearing point must be spoken.",
                    None, st[:160])

    # --- meta ratio (rule 10) -------------------------------------------------
    meta = sum(1 for _, t in spoken if META_RE.search(t))
    ratio = meta / len(spoken)
    if ratio < 0.08:
        add("W-META", "warn",
            f"Only {ratio:.0%} of lines mention the exam/answer/marks. The corpus runs about "
            f"one line in four; too few and it reads like a textbook.")
    elif ratio > 0.50:
        add("W-META", "warn",
            f"{ratio:.0%} of lines are about the exam rather than the subject. The corpus runs "
            f"about one in four; more than that reads like an advertisement.")

    # --- repeated lines -------------------------------------------------------
    # Repetition ACROSS parts is deliberate (rule 11: a viewer can join mid-way);
    # the same sentence twice inside ONE part is padding.
    for p in parts:
        seen: dict[str, int] = {}
        for ln, t in p.spoken:
            key = " ".join(t.split())
            if len(key) > 40 and key in seen:
                add("W-REPEAT", "warn",
                    f"Identical line already said at line {seen[key]} in this part.", ln, t)
            seen[key] = ln
    if strict:
        # A new script is held to the user's review, not to the corpus's spread:
        # too long, too many hooks and an indirect intro all block delivery.
        for f in F:
            if f.code in ("W-LENGTH", "W-HOOKS", "W-INTRO", "W-PART-LEN", "W-SYMBOL",
                          "W-FORMAL", "W-FLAT", "W-HOOK-STACK", "W-HOOK-SAME",
                          "W-HOOK-SPLIT"):
                f.severity = "error"
                f.code = "E" + f.code[1:]
    return F


# --------------------------------------------------------------------------- #
def main() -> int:
    ap = argparse.ArgumentParser(description="Mechanical checks on a PYQ reel script.")
    ap.add_argument("script")
    ap.add_argument("--answer", help="file holding the source answer (enables coverage checks)")
    ap.add_argument("--question", help="file holding the question text")
    ap.add_argument("--years", default="", help="comma-separated, e.g. 2019,2022")
    ap.add_argument("--category", default="", help="LA | SA | NM | VS")
    ap.add_argument("--style", default="auto", choices=["auto", "current", "legacy"],
                help="which closing generation to expect; auto detects it")
    ap.add_argument("--strict", action="store_true",
                    help="new scripts: length, hook count and intro length block delivery")
    ap.add_argument("--json", help="write the findings to this file")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()

    read = lambda p: Path(p).read_text(encoding="utf-8-sig") if p else ""
    script = parse(a.script)
    findings = check(script, answer=read(a.answer), question=read(a.question),
                     years=[y.strip() for y in a.years.split(",") if y.strip()],
                     category=a.category, style=a.style, strict=a.strict)

    errors = [f for f in findings if f.severity == "error"]
    warns = [f for f in findings if f.severity == "warn"]
    if a.json:
        Path(a.json).write_text(json.dumps(
            dict(script=str(a.script), parts=len(script.parts),
                 spoken_lines=len(script.all_spoken),
                 words=len(script.spoken_text.split()),
                 errors=len(errors), warnings=len(warns),
                 findings=[asdict(f) for f in findings]), ensure_ascii=False, indent=1),
            encoding="utf-8")
    if not a.quiet:
        print(f"{a.script}: {len(script.parts)} part(s), {len(script.all_spoken)} spoken lines, "
              f"{len(script.spoken_text.split())} words")
        for f in errors + warns:
            print(f.fmt())
        print(f"\n{len(errors)} error(s), {len(warns)} warning(s) — "
              f"{'BLOCKED' if errors else 'passes the mechanical gate'}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
