"""Put a topic image where the graphic area would otherwise sit empty.

    python tools/fill_visual_gaps.py che-c1-la-01 [--dry]

`tools/visual_gaps.py` finds the holes: the stage clears when the question card
comes down and nothing replaces it until the first beat, so the presenter talks
for ten or twenty seconds against a blank strip. Measured across the first six
videos that came to 111 seconds of dead screen.

The image is generated from WHAT IS BEING SAID during the hole, not from the
question title — the hole usually sits over the hook and the framing, where the
teacher is setting up the idea rather than stating it, and an illustration of
the apparatus would pre-empt the beat that follows.

House style, so it reads as part of the video rather than a stock picture:
white line art on the deep navy plate, the same drawn-on-a-board look as the
background. No lettering — generated text comes out garbled, and the caption
already carries the words.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, ".")
from tools.visual_gaps import gaps                       # noqa: E402

# A real photograph, not a line drawing. The line-art version read as a small
# white sketch floating in the middle of the frame and taught nothing; a student
# recognises the actual substance or apparatus instantly. Generated on flat
# magenta and keyed out here, because gpt-image-2 refuses a transparent
# background.
STYLE = (
    "Photographic, sharply focused, evenly lit, realistic — a real object, not "
    "an illustration or a drawing. The subject fills most of the frame and is "
    "the ONLY thing in it. The entire background is one flat uniform saturated "
    "magenta (#FF00FF): no gradient, no shadow, no reflection, no surface, no "
    "other colour. No text, no labels, no numerals anywhere."
)


GREY_GROUND = (
    "Photographic, sharply focused, evenly lit, realistic — a real object, not "
    "an illustration. The subject fills most of the frame and is the ONLY thing "
    "in it. The entire background is one flat uniform NEUTRAL MID-GREY (#808080) "
    "with no gradient, no shadow and no other object. Keep the subject's own "
    "colours strong and clearly darker or brighter than the grey. No text."
)

GLASSY = ("beaker", "glass", "test tube", "flask", "jar", "bottle", "water",
          "liquid", "solution", "tube", "pot", "boiling")


def _cut_magenta(path: Path) -> None:
    """Key the magenta ground away and despill the edge.

    Same idea as the presenter's green screen. Without the despill a magenta rim
    survives on every edge, which is glaring against the navy plate.
    """
    import numpy as np
    from PIL import Image
    a = np.asarray(Image.open(path).convert("RGB")).astype(float)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    ground = (r > 140) & (b > 140) & (g < 110)
    al = np.where(ground, 0.0, 1.0)
    edge = ~ground & (r > 120) & (b > 120) & (g < 110)
    a[..., 0] = np.where(edge, np.minimum(r, g * 1.15), r)
    a[..., 2] = np.where(edge, np.minimum(b, g * 1.15), b)
    Image.fromarray(np.dstack([a, al * 255]).astype(np.uint8), "RGBA").save(path)


def _cut_grey(path: Path) -> None:
    """Cut a transparent subject off a flat grey ground.

    A magenta key is wrong for glassware: the ground is visible THROUGH the
    glass, so the key removes the liquid as well and the beaker comes out pink
    and hollow. Grey is keyed on how close a pixel is to neutral instead, which
    leaves anything coloured or bright — glass edges, liquid, meniscus — intact.
    """
    import numpy as np
    from PIL import Image
    a = np.asarray(Image.open(path).convert("RGB")).astype(float)
    mx, mn = a.max(axis=2), a.min(axis=2)
    sat = mx - mn                                   # neutral ground has none
    lum = a.mean(axis=2)
    ground = (sat < 26) & (np.abs(lum - 128) < 34)
    from scipy.ndimage import binary_opening, binary_fill_holes  # noqa
    keep = binary_fill_holes(~ground)
    al = np.where(keep, 1.0, 0.0)
    Image.fromarray(np.dstack([a, al * 255]).astype(np.uint8), "RGBA").save(path)


def _trim(path: Path) -> None:
    """Crop the transparent margin away.

    The subject sits inside a square canvas, so a diagonal nail was mostly empty
    space — and the beat sizes the whole canvas, which made the nail tiny on
    screen. Cropping to the subject lets the picture fill the room it is given.
    """
    import numpy as np
    from PIL import Image
    im = Image.open(path).convert("RGBA")
    a = np.asarray(im)
    ys, xs = np.where(a[..., 3] > 12)
    if not len(ys):
        return
    pad = 8
    im.crop((max(0, xs.min()-pad), max(0, ys.min()-pad),
             min(a.shape[1], xs.max()+pad), min(a.shape[0], ys.max()+pad))).save(path)


def subject_of(root: Path, part: int, a: float, b: float) -> str:
    lines = json.loads((root / f"lines_part{part}.json").read_text(encoding="utf-8"))
    said = " ".join(l["text"] for l in lines if a <= float(l["start"]) < b)
    return " ".join(said.split())[:400]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()

    root = Path("projects") / args.slug
    meta = json.loads((root / "meta.json").read_text(encoding="utf-8"))
    question = meta.get("question", "")
    from src.llm import complete
    from src.frames import generate_image

    for f in sorted(root.glob("lines_part*.json")):
        part = int(f.stem.split("part")[1])
        for a, b in gaps(root, part):
            said = subject_of(root, part, a, b)
            # What follows the hole matters as much as what fills it: without
            # this the model drew the Berkeley apparatus into the gap that sits
            # directly before the Berkeley apparatus beat.
            beats_now = json.loads((root / f"beats_part{part}.json").read_text(encoding="utf-8"))
            after = [x for x in beats_now if float(x.get("at", 0)) >= 0]
            nxt = "; ".join(
                str(x.get("name") or x.get("title") or x.get("label") or x["type"])
                for x in sorted(after, key=lambda z: z["at"])[:2]) or "nothing"
            brief = complete(
                "You choose ONE simple picture for a Class 12 chemistry video. "
                "Reply with exactly two lines:\n"
                "1) an English sentence naming what to photograph — a concrete "
                "object, substance or apparatus\n"
                "2) a Hindi label of two to four words naming that object, as a "
                "student would read it on screen\n\n"
                "The picture must be about the QUESTION'S CHEMISTRY. The teacher "
                "is often just framing the exam at this moment ('this came in "
                "2018', 'write it like this and the marks are yours') — never "
                "illustrate THAT. A pen, an answer sheet, a student writing, a "
                "clock, a trophy: all wrong. Draw the substance or apparatus the "
                "question is about.\n\n"
                "Never an abstract idea, never text. Do not give away the "
                "specific diagram the next beat will show.",
                f"QUESTION: {question}\nTEACHER IS SAYING: {said}\n"
                f"THE NEXT BEAT ALREADY SHOWS: {nxt}\n"
                f"Draw something different from that — the idea underneath it, "
                f"a material, or a everyday instance of it.",
                effort="low").strip()
            rows = [x.strip().lstrip("12).- ").strip() for x in brief.splitlines() if x.strip()]
            brief, label = (rows + ["", ""])[0], (rows + ["", ""])[1]
            dest = root / "images" / f"gap_part{part}.png"
            print(f"  part{part} {a:.0f}-{b:.0f}s: {brief[:88]}")
            if args.dry:
                continue
            dest.parent.mkdir(parents=True, exist_ok=True)
            # 1024x1024 at medium quality: these are support images behind a
            # talking presenter, and the larger sizes cost more for detail the
            # viewer never sees at this scale.
            glassy = any(k in brief.lower() for k in GLASSY)
            ground = GREY_GROUND if glassy else STYLE
            generate_image(f"{brief}\n\n{ground}", dest,
                           size="1024x1024", quality="medium")
            _cut_grey(dest) if glassy else _cut_magenta(dest)
            _trim(dest)

            beats_p = root / f"beats_part{part}.json"
            beats = json.loads(beats_p.read_text(encoding="utf-8"))
            lines = json.loads((root / f"lines_part{part}.json").read_text(encoding="utf-8"))
            at = next(i for i, l in enumerate(lines) if float(l["start"]) >= a)
            beats = [x for x in beats if not (x["at"] == at and x["type"] == "image")]
            beats.append({"at": at, "type": "image",
                          "src": f"images/gap_part{part}.png",
                          "caption": label,
                          "intent": "SUPPORT",
                          "reason": "यहाँ स्क्रीन खाली रह जाती थी — शिक्षक बोल रहा है"
                                    " और ऊपर कुछ नहीं; विषय से जुड़ा चित्र रखा गया है"})
            beats.sort(key=lambda x: x["at"])
            beats_p.write_text(json.dumps(beats, ensure_ascii=False, indent=1),
                               encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
