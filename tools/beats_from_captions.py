"""Derive a part's on-screen beats from its own caption track.

    python tools/beats_from_captions.py che-c2-la-05 1

Hand-written beats drift from the narration. They are summaries of the script,
they persist for ten or fifteen caption lines, and the presenter moves on while
the screen still shows the previous point — which reads exactly like the screen
saying something different from the voice, because it is.

So the beats are generated FROM the captions instead. The track is cut into
windows of a few lines each, and a model turns each window into one block that
says what is being said in it — a formula if the window is an equation, a
comparison if it contrasts two things, a short list otherwise. The on-screen
text can then only ever be about the words currently being spoken.

What it does NOT do is invent content. The window's captions are the entire
input, and the instruction is to compress them, not to add. Anything the block
claims has just been said aloud.

Diagrams stay hand-placed: `--keep` merges an existing beats file's `apparatus`,
`graph` and `image` blocks back in, because which figure belongs where is a
judgement about the question, not about the sentence.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

WINDOW = 4              # caption lines per on-screen block
MIN_WINDOW = 3          # never leave a stub of one line at the end

SYSTEM = """तुम एक शिक्षण वीडियो के लिए स्क्रीन-टेक्स्ट बनाते हो।
सिर्फ़ JSON लौटाओ, कोई और शब्द नहीं।"""

PROMPT = """नीचे कुछ कैप्शन लाइनें हैं जो शिक्षक इस समय बोल रहा है। इन्हीं के आधार पर
स्क्रीन पर दिखाने के लिए एक छोटा ब्लॉक बनाओ।

नियम:
- सिर्फ़ इन्हीं लाइनों की बात कहो। कोई नई जानकारी मत जोड़ो।
- बहुत छोटा रखो: शीर्षक 2-4 शब्द, हर बिंदु अधिकतम 6 शब्द, अधिकतम 3 बिंदु।
- अगर इनमें कोई समीकरण या सूत्र है तो type "formula" दो और tex में LaTeX लिखो
  (LaTeX में देवनागरी कभी मत लिखो — वह label में जाए)।
- अगर दो चीज़ों की तुलना है तो type "compare" दो।
- वरना type "points" दो।

सिर्फ़ JSON लौटाओ, इस आकार में:
{"type":"points","title":"...","items":["...","..."]}
{"type":"formula","label":"...","tex":["..."]}
{"type":"compare","left":["शीर्षक",["..."]],"right":["शीर्षक",["..."]]}

कैप्शन लाइनें:
"""


def windows(lines, start, size=WINDOW):
    """Index ranges over the caption track, skipping the opening card lines."""
    out, i = [], start
    while i < len(lines):
        end = min(i + size, len(lines))
        if len(lines) - end < MIN_WINDOW:
            end = len(lines)
        out.append((i, end))
        i = end
    return out


def block_for(lines, lo, hi, complete):
    text = "\n".join(l["text"] for l in lines[lo:hi])
    raw = complete(SYSTEM, PROMPT + text)
    m = re.search(r"\{.*\}", raw, re.S)
    if not m:
        return None
    try:
        spec = json.loads(m.group(0))
    except json.JSONDecodeError:
        return None
    if spec.get("type") not in {"points", "formula", "compare"}:
        return None
    # Devanagari inside MathTex kills the whole render with a LaTeX Unicode
    # error, so it is stripped here rather than trusted to the prompt.
    if spec["type"] == "formula":
        keep = [t for t in spec.get("tex", []) if not re.search(r"[ऀ-ॿ]", t)]
        if not keep:
            return None
        spec["tex"] = keep
    spec["at"] = lo
    return spec


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("project")
    p.add_argument("part")
    p.add_argument("--keep", action="store_true",
                   help="merge figures from the existing beats file")
    p.add_argument("--window", type=int, default=WINDOW)
    a = p.parse_args()

    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from src.llm import complete

    root = Path("projects") / a.project
    lines = json.loads((root / f"lines_part{a.part}.json").read_text(encoding="utf-8"))
    meta = json.loads((root / "meta.json").read_text(encoding="utf-8"))
    cl = meta.get("card_lines", 0)
    start = int(cl[str(a.part)] if isinstance(cl, dict) else cl)

    figures = []
    old_path = root / f"beats_part{a.part}.json"
    if a.keep and old_path.exists():
        figures = [b for b in json.loads(old_path.read_text(encoding="utf-8"))
                   if b.get("type") in {"apparatus", "graph", "image"}]

    out = []
    for lo, hi in windows(lines, start, a.window):
        spec = block_for(lines, lo, hi, complete)
        if spec:
            out.append(spec)

    # A figure wins its slot: it was placed by judgement about the question.
    taken = {f["at"] for f in figures}
    out = [b for b in out if b["at"] not in taken] + figures
    out.sort(key=lambda b: b["at"])
    old_path.write_text(json.dumps(out, ensure_ascii=False, indent=2),
                        encoding="utf-8")
    print(f"{a.project} part {a.part}: {len(out)} blocks "
          f"({len(figures)} figure(s) kept) over {len(lines)} caption lines")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
