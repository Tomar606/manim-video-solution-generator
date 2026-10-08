"""Write one Veo prompt per scene, landscape or vertical, and audit every one.

    python veo_kit/build_prompts.py veo_kit/example/his-c2-la-01 --aspect landscape
    python veo_kit/build_prompts.py projects/<slug>/veo --aspect vertical \\
        --character veo_kit/characters/ritesh.json

The folder holds scenes.json (the scene table) and lines.json ({"1": "<line>"}).
Output goes to <folder>/prompts/<aspect>/sNN.txt plus prompts.json beside them,
which is what submit.py queues and fetch.py identifies clips by.

THE SHAPE, and why (docs/veo-prompt-research.md has the sources)
----------------------------------------------------------------
* GOOGLE'S ORDER: camera, subject, action, context, style. Short: 100 to 150
  words. Our first prompts ran 370-400 and Google's own examples run 40-70.
* THE FACE IS THE REFERENCES' JOB. Three reference images carry his identity;
  the text calls him "the man from the reference images" and says only what he
  wears. Describing the face again competes with the pictures, and is how the
  beard shortens.
* NO NEGATIVE BLOCK AND NO "DO NOT". Flow has no negative-prompt field, so a
  NEGATIVE list is read as part of the prompt and every noun in it is a request.
  Everything is said positively: "his is the only voice", never "nobody else
  speaks".
* NO DEAD AIR. Each line is 33-42 syllables (syllables.py), and he has something
  to DO before and after it. Handed empty seconds, Veo invents speech, which is
  the gibberish the first HIS-C2-LA-01 clips came back with.
* THE SHAPE IS WORDS, NOT NUMBERS. A measurement in a generation prompt is a
  thing that gets drawn (CLAUDE.md), so vertical is "a tall vertical frame",
  never a ratio. The aspect itself is set in Flow's settings panel.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from syllables import verdict  # noqa: E402

DEFAULT_CHARACTER = HERE / "characters" / "ritesh.json"

FRAME = {
    "landscape": "Natural, true-to-life colour; a clean, uncluttered documentary frame.",
    # Vertical keeps him centred with his head high, so a phone screen shows his
    # face and his hands together; wide scenery is what a tall frame loses.
    "vertical": ("Natural, true-to-life colour; a clean, uncluttered tall vertical "
                 "frame, with him centred, his head near the top and his hands in "
                 "view in front of his chest."),
}

# Words that must not reach a Flow prompt. Each one has a story in the bug ledger
# (.claude/skills/video-prompt/references/bug-ledger.md) or in the research.
BANNED = [
    (r"\b(logo|watermark|badge|wordmark|emblem|brand)\b",
     "naming a mark is a request to draw one, even as a negative"),
    (r"\b(subtitles?|captions?|on-screen text|lettering|title card)\b",
     "names text, which Veo then draws"),
    (r"\bnegative\b", "Flow has no negative field; the block is read as asked for"),
    (r"\b(do not|don't|never|avoid|without|no one|nobody)\b",
     "say it positively; Veo reads the noun, not the negation"),
    (r"\d+\s*%|\d+\s*px|\b\d+:\d+\b|\b\d{3,4}\s*x\s*\d{3,4}\b",
     "a measurement in a prompt gets drawn"),
    (r"\b(face|beard|hairline|eyebrows?|skin tone)\b",
     "the face is the references' job; describing it competes with them"),
]


def build(sc: dict, line: str, ch: dict, accessory: str, aspect: str) -> str:
    cam = sc["camera"].strip()
    if aspect == "vertical":
        # A lateral tracking shot in a tall frame is mostly empty sides.
        if "framed tall" not in cam:
            cam = cam.replace("Medium tracking shot", "Medium tracking shot, framed tall")
    wear = ch["wardrobe"] + (accessory if sc.get("accessory") else "")
    others = (sc.get("others") or "").strip()
    return (f"{cam} The man from the reference images, {wear}, {sc['setting']}. "
            f"{sc['before']}. He says in {ch.get('language', 'Hindi')}, {ch['voice']}: "
            f"\"{line}\" {sc['after']}. "
            f"{(others + ' ') if others else ''}His is the only voice. {sc['sound']} "
            f"{FRAME[aspect]}")


def audit(prompt: str, line: str) -> list[str]:
    faults = []
    # the spoken line is checked separately and may legitimately hold anything
    body = prompt.replace(f"\"{line}\"", "\"\"")
    for pat, why in BANNED:
        m = re.search(pat, body, flags=re.I)
        if m:
            faults.append(f"'{m.group(0)}': {why}")
    if re.search(r"[0-9]", line):
        faults.append("the spoken line holds a digit; write the number as words")
    n = len(prompt.split())
    if not 80 <= n <= 170:
        faults.append(f"{n} words; aim for 100-150")
    if prompt.count('"') != 2:
        faults.append("the line must be quoted exactly once")
    s, sec, v = verdict(line)
    if v != "ok":
        faults.append(f"line is {s} syllables ({sec:.1f}s): {v}")
    return faults


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("folder", help="holds scenes.json and lines.json")
    ap.add_argument("--aspect", choices=("landscape", "vertical"), required=True)
    ap.add_argument("--character", default=str(DEFAULT_CHARACTER))
    ap.add_argument("--only", nargs="*", default=[], help="scene numbers to build")
    a = ap.parse_args()

    folder = Path(a.folder)
    doc = json.loads((folder / "scenes.json").read_text(encoding="utf-8"))
    lines = json.loads((folder / "lines.json").read_text(encoding="utf-8"))
    ch = json.loads(Path(a.character).read_text(encoding="utf-8"))
    out = folder / "prompts" / a.aspect
    out.mkdir(parents=True, exist_ok=True)

    recs, bad = [], 0
    for n, sc in doc["scenes"].items():
        if a.only and n not in a.only:
            continue
        if n not in lines:
            print(f"  s{int(n):02d}  no line in lines.json"); bad += 1; continue
        p = build(sc, lines[n], ch, doc.get("accessory", ""), a.aspect)
        faults = audit(p, lines[n])
        name = f"s{int(n):02d}"
        (out / f"{name}.txt").write_text(p + "\n", encoding="utf-8")
        recs.append({"brief": name, "prompt": p, "aspect": a.aspect})
        s, sec, _ = verdict(lines[n])
        print(f"  {name}  {len(p.split()):3d} words  line {s} syl / {sec:.1f}s"
              + ("" if not faults else "   FAIL: " + "; ".join(faults)))
        bad += bool(faults)
    (out / "prompts.json").write_text(json.dumps(recs, ensure_ascii=False, indent=1) + "\n",
                                      encoding="utf-8")
    print(f"\n  {len(recs)} prompt(s) -> {out}"
          + ("" if not bad else f"   {bad} FAILED the audit — fix before submitting"))
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
