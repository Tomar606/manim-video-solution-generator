"""Check what a generated clip actually SAYS, against the line it was given.

    python veo_kit/speech_qc.py <clip.mp4> "<the Hindi line>"
    python veo_kit/speech_qc.py <clip.mp4> --line-file lines.json --n 4

WHY THIS EXISTS
---------------
The first all-Veo History clips came back with the presenter mouthing
gibberish, and the audio of these clips is what gets voice-converted with
ElevenLabs afterwards — so a wrong word here is a wrong word in the finished
video, in his own voice. face_gate proves it is him; this proves he said the
line.

WHAT IT MEASURES
----------------
* COVERAGE — how much of the scripted line is heard. Words are compared by
  consonant skeleton (the same reduction as tools/align.py), because Whisper spells Hindi freely and
  sometimes answers in Latin script; "मातरा" for "मात्रा" still matches.
* INVENTED SPEECH — heard words that are not in the line. A generator handed
  dead time fills it with talk; this is where that shows up.
* TIMING — when speech starts and stops, from the audio itself, so a line that
  rushes, trails into the next clip, or leaves half the clip empty is visible.

Whisper is not perfect on Hindi, so coverage is a signal rather than proof:
anything below the pass mark gets listened to, not thrown away.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from difflib import SequenceMatcher
from pathlib import Path

# Consonant skeleton, copied from tools/align.py so the kit stands alone.
# Only consonants matter: Whisper gets matras and halant wrong, and answers the
# same clip in Devanagari one run and Latin the next. "समझते" == "samajhte".
DEVA_LAT = {
    "क": "k", "ख": "kh", "ग": "g", "घ": "gh", "ङ": "n", "च": "ch", "छ": "chh",
    "ज": "j", "झ": "jh", "ञ": "n", "ट": "t", "ठ": "th", "ड": "d", "ढ": "dh",
    "ण": "n", "त": "t", "थ": "th", "द": "d", "ध": "dh", "न": "n", "प": "p",
    "फ": "ph", "ब": "b", "भ": "bh", "म": "m", "य": "y", "र": "r", "ल": "l",
    "व": "v", "श": "sh", "ष": "sh", "स": "s", "ह": "h", "ळ": "l", "ऋ": "r",
    "क़": "k", "ख़": "kh", "ग़": "g", "ज़": "j", "ड़": "d", "ढ़": "dh", "फ़": "f",
}


def skel(word: str) -> str:
    word = re.sub(r"[ा-्ঁंःऀ-ः]", "", word)
    if any("ऀ" <= c <= "ॿ" for c in word):
        return "".join(DEVA_LAT.get(c, "") for c in word)
    return re.sub(r"[aeiou]", "", re.sub(r"[^A-Za-z]", "", word).lower())


PASS_COVERAGE = 0.75      # of the line's consonants, heard in order
MAX_INVENTED = 0.25       # heard consonants not in the line, as a share of it

# Whisper writes a spoken number as DIGITS: "दो हज़ार पच्चीस" comes back "2025".
# Compared as written, every year in an intro line reads as three missing words
# and one invented one, which failed a clip that said its line perfectly.
_ONES = ("शून्य एक दो तीन चार पाँच छह सात आठ नौ दस ग्यारह बारह तेरह चौदह पंद्रह "
         "सोलह सत्रह अठारह उन्नीस बीस इक्कीस बाईस तेईस चौबीस पच्चीस छब्बीस सत्ताईस "
         "अट्ठाईस उनतीस तीस इकतीस बत्तीस तैंतीस चौंतीस पैंतीस छत्तीस सैंतीस अड़तीस "
         "उनतालीस चालीस इकतालीस बयालीस तैंतालीस चवालीस पैंतालीस छियालीस सैंतालीस "
         "अड़तालीस उनचास पचास इक्यावन बावन तिरपन चौवन पचपन छप्पन सत्तावन अट्ठावन उनसठ "
         "साठ इकसठ बासठ तिरसठ चौंसठ पैंसठ छियासठ सड़सठ अड़सठ उनहत्तर सत्तर इकहत्तर "
         "बहत्तर तिहत्तर चौहत्तर पचहत्तर छिहत्तर सतहत्तर अठहत्तर उनासी अस्सी इक्यासी "
         "बयासी तिरासी चौरासी पचासी छियासी सत्तासी अट्ठासी नवासी नब्बे इक्यानवे बानवे "
         "तिरानवे चौरानवे पचानवे छियानवे सत्तानवे अट्ठानवे निन्यानवे").split()


def hindi_number(n: int) -> str:
    if n < 100:
        return _ONES[n]
    if 1100 <= n <= 1999:                      # years: उन्नीस सौ सैंतालीस
        return f"{_ONES[n // 100]} सौ" + (f" {_ONES[n % 100]}" if n % 100 else "")
    parts = []
    for size, word in ((100000, "लाख"), (1000, "हज़ार"), (100, "सौ")):
        if n >= size:
            parts.append(f"{hindi_number(n // size)} {word}")
            n %= size
    if n:
        parts.append(_ONES[n])
    return " ".join(parts)


def spell_numbers(text: str) -> str:
    return re.sub(r"\d+", lambda m: f" {hindi_number(int(m.group()))} "
                  if len(m.group()) < 7 else m.group(), text)


# Aspiration is the other thing Whisper drops on Hindi: पूछा -> पुचा, बहुत ->
# बहुड, मगध -> मगद. It says nothing about whether the words were right.
_LOOSE = (("chh", "ch"), ("kh", "k"), ("gh", "g"), ("jh", "j"), ("th", "t"),
          ("dh", "d"), ("ph", "p"), ("bh", "b"), ("sh", "s"))


def loose(text: str) -> str:
    """The line as ONE consonant string: no spaces (Whisper merges and splits
    words — "भी आ सकता" came back "बार्वी आसकता"), no aspiration."""
    out = "".join(skel(w) for w in spell_numbers(text).split())
    for a, b in _LOOSE:
        out = out.replace(a, b)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("clip")
    ap.add_argument("line", nargs="?")
    ap.add_argument("--line-file")
    ap.add_argument("--n")
    ap.add_argument("--model", default="small")
    ap.add_argument("--lang", default="hi", help="Whisper language code")
    a = ap.parse_args()
    line = a.line or json.loads(Path(a.line_file).read_text(encoding="utf-8"))[str(a.n)]

    import whisper
    m = whisper.load_model(a.model)
    r = m.transcribe(a.clip, language=a.lang, condition_on_previous_text=False,
                     word_timestamps=True, fp16=False)
    heard = " ".join(s["text"] for s in r["segments"]).strip()
    words = [w for s in r["segments"] for w in s.get("words", [])]

    want, got = loose(line), loose(heard)
    sm = SequenceMatcher(a=want, b=got, autojunk=False)
    matched = sum(b.size for b in sm.get_matching_blocks())
    coverage = matched / max(1, len(want))
    invented = max(0, len(got) - matched) / max(1, len(want))

    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                                "format=duration", "-of", "csv=p=0", a.clip],
                               capture_output=True, text=True).stdout.strip() or 0)
    # SPEECH, from Whisper's word timings. silencedetect cannot tell a voice
    # from the rustle of a rice field, and called both clips "cut off" because
    # the ambience ran to the last frame.
    first = words[0]["start"] if words else 0.0
    last = words[-1]["end"] if words else 0.0
    print(f"  {Path(a.clip).name}")
    print(f"    scripted : {line}")
    print(f"    heard    : {heard}")
    print(f"    coverage : {coverage:.0%} of the line's sounds, in order")
    print(f"    extra    : {invented:.0%} (heard, not in the line)")
    print(f"    speech   : {first:.2f}s -> {last:.2f}s of {dur:.2f}s "
          f"(lead-in {first:.2f}s, after {dur - last:.2f}s)")
    bad, note = [], []
    if coverage < PASS_COVERAGE:
        bad.append(f"only {coverage:.0%} of the line is heard")
    if invented > MAX_INVENTED:
        bad.append(f"{invented:.0%} extra speech — invented words")
    if words and dur - last < 0.15:
        bad.append("the last word ends on the last frame — it may be cut off")
    if words and dur - last > 3.0:
        note.append(f"{dur - last:.1f}s after the line — listen for filler speech")
    for n_ in note:
        print(f"    note     : {n_}")
    print("    " + ("SPEECH OK" if not bad else "SPEECH QC FAILED — " + "; ".join(bad)))
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
