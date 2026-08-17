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

SYSTEM = """तुम एक शैक्षिक वीडियो के Instructional Visual Director हो।
सिर्फ़ JSON लौटाओ, कोई और शब्द नहीं।"""

PROMPT = """नीचे कुछ कैप्शन लाइनें हैं जो शिक्षक अभी बोल रहा है।

पहले तय करो कि शिक्षक क्या कर रहा है (teaching intent), फिर तय करो कि क्या कोई
दृश्य वास्तव में समझने में मदद करेगा।

सबसे ज़रूरी नियम: हर वाक्य के लिए ग्राफ़िक मत बनाओ। अगर स्क्रीन पर कुछ दिखाने से
समझ बेहतर नहीं होती, तो {"type":"none"} लौटाओ। खाली स्क्रीन स्वीकार्य है।

दूसरा नियम: स्क्रीन-टेक्स्ट कैप्शन की नकल नहीं है। कैप्शन बताता है, स्क्रीन
व्यवस्थित करती है। जो शब्द बोले जा रहे हैं उन्हें दोबारा मत लिखो — उन्हें
शीर्षक, बिंदु, सूत्र या तुलना में बदलो। हर बिंदु अधिकतम 5 शब्द।

intent इनमें से चुनो:
DEFINITION, LIST, ADVANTAGES, COMPARISON, PROCESS, CAUSE_EFFECT, FORMULA,
DERIVATION, DIAGRAM, GRAPH, EXAMPLE, KEYWORD, COMMON_MISTAKE, RECAP,
TRANSITION, PURE_NARRATION

फिर उसी के अनुसार दृश्य चुनो:
- गिनती/सूची/लाभ ("तीन कारक", "चार बातें", "पहला… दूसरा…") -> points,
  और "reveal":"progressive" दो ताकि हर बिंदु बोले जाने पर आए
- दो चीज़ों की तुलना -> compare
- क्रम/प्रक्रिया -> flow
- समीकरण या सूत्र -> formula (LaTeX में देवनागरी कभी नहीं; वह label में)
- परिभाषा/मुख्य शब्द -> points, अधिकतम 2 बिंदु
- सिर्फ़ जोड़ने वाला वाक्य, प्रेरणा, दोहराव -> none

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
    if spec.get("type") == "none":
        return None                     # a deliberate no-graphic decision
    if spec.get("type") not in {"points", "formula", "compare", "flow"}:
        return None
    # Devanagari inside MathTex kills the whole render with a LaTeX Unicode
    # error, so it is stripped here rather than trusted to the prompt.
    if spec["type"] == "formula":
        keep = [t for t in spec.get("tex", []) if not re.search(r"[ऀ-ॿ]", t)]
        if not keep:
            return None
        spec["tex"] = keep
    spec["at"] = lo
    # A progressive list needs to know WHEN each item is named. Spreading them
    # across the window is the honest approximation: the window is the span in
    # which the teacher lists them.
    if spec.get("reveal") == "progressive" and spec.get("items"):
        n = len(spec["items"])
        step = max(1, (hi - lo) // max(1, n))
        spec["reveal_at"] = [lo + i * step for i in range(n)]
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
