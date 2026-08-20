"""Put a photo of the real thing where the teacher names a real thing.

    python tools/example_images.py che-c2-la-02 [--dry]

Some topics are about objects a student has actually seen — a rusted nail, a
torch cell, an orange. A photograph of that object at the moment it is named
teaches faster than any diagram, and the corrosion video already did this by
hand. This finds those moments and does it everywhere.

WHERE IT WILL NOT PUT ONE
-------------------------
A beat replaces whatever is on stage, so dropping a photo into the middle of a
progressive reveal would wipe a list or a derivation halfway through. Indices
covered by another beat's `reveal_at` are therefore off limits, and so is any
index within LOCKOUT lines of another beat. The picture has to earn a slot of
its own, not steal one.

TRANSPARENCY
------------
gpt-image-2 refuses `background="transparent"`, so the subject is generated on
flat magenta and keyed out here — the same idea as the presenter's green screen,
including a despill pass, because a magenta rim on a navy plate is glaring.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, ".")

LOCKOUT = 2           # captions of clearance a photo needs either side
MAX_PER_PART = 2      # a photo is a highlight; more than two stops being one

GROUND = (
    " The subject is the ONLY object in the frame, photographed sharply and lit "
    "evenly. The ENTIRE background is one flat uniform saturated magenta "
    "(#FF00FF) — no gradient, no shadow, no reflection, no other colour, and "
    "nothing else in shot. Draw no text, no labels and no numerals."
)


def cut_out(path: Path) -> None:
    """Key the magenta away and take the spill off the edge."""
    import numpy as np
    from PIL import Image
    a = np.asarray(Image.open(path).convert("RGB")).astype(float)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    ground = (r > 140) & (b > 140) & (g < 110)
    al = np.where(ground, 0.0, 1.0)
    edge = ~ground & ((r > 120) & (b > 120) & (g < 110))
    a[..., 0] = np.where(edge, np.minimum(r, g * 1.15), r)
    a[..., 2] = np.where(edge, np.minimum(b, g * 1.15), b)
    Image.fromarray(np.dstack([a, al * 255]).astype(np.uint8), "RGBA").save(path)


def free_slots(beats: list[dict], n_lines: int) -> set[int]:
    taken: set[int] = set()
    for b in beats:
        at = int(b["at"])
        for i in range(at - LOCKOUT, at + LOCKOUT + 1):
            taken.add(i)
        for r in b.get("reveal_at", []):
            for i in range(int(r) - LOCKOUT, int(r) + LOCKOUT + 1):
                taken.add(i)
    return {i for i in range(n_lines) if i not in taken}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()
    from src.frames import generate_image
    from src.llm import complete

    root = Path("projects") / args.slug
    question = json.loads((root / "meta.json").read_text(encoding="utf-8")).get("question", "")

    for f in sorted(root.glob("lines_part*.json")):
        part = int(f.stem.split("part")[1])
        lines = json.loads(f.read_text(encoding="utf-8"))
        bp = root / f"beats_part{part}.json"
        beats = json.loads(bp.read_text(encoding="utf-8")) if bp.is_file() else []
        free = free_slots(beats, len(lines))
        if not free:
            continue
        numbered = "\n".join(f"{i}: {lines[i]['text']}" for i in sorted(free))
        reply = complete(
            "You pick moments in a Class 12 chemistry video where a PHOTOGRAPH of a "
            "real object would teach faster than words.\n\n"
            "Reply with at most " + str(MAX_PER_PART) + " lines, each exactly:\n"
            "<caption index>|<the object to photograph, in English>\n\n"
            "Only choose a line that NAMES a concrete everyday object or material "
            "the student could hold or has seen. Skip definitions, formulae, "
            "trends, exam advice and anything abstract — for those reply NONE. "
            "It is correct and normal to reply NONE.",
            f"QUESTION: {question}\n\nCANDIDATE LINES:\n{numbered}",
            effort="low").strip()

        picks = []
        for row in reply.splitlines():
            if "|" not in row:
                continue
            idx, obj = row.split("|", 1)
            idx = "".join(c for c in idx if c.isdigit())
            if idx and int(idx) in free:
                picks.append((int(idx), obj.strip()))
        picks = picks[:MAX_PER_PART]
        for i, obj in picks:
            print(f"  part{part} line {i} ({lines[i]['text'][:34]}…) -> {obj[:52]}")
            if args.dry:
                continue
            dest = root / "images" / f"example_p{part}_{i}.png"
            dest.parent.mkdir(parents=True, exist_ok=True)
            generate_image(obj + "." + GROUND, dest,
                           size="1024x1024", quality="medium")
            cut_out(dest)
            beats.append({"at": i, "type": "image",
                          "src": f"images/example_p{part}_{i}.png",
                          "intent": "EXAMPLE",
                          "reason": f"शिक्षक यहाँ {obj} का उदाहरण दे रहा है — असली"
                                    f" चीज़ दिखने पर बात तुरंत समझ आती है"})
        if picks and not args.dry:
            beats.sort(key=lambda x: x["at"])
            bp.write_text(json.dumps(beats, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
