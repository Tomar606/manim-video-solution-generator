"""The answer, whole, on the plate the video ends on.

    python tools/reel_recap_list.py <slug> [--size 58]

Reads `steps` off reel.json and writes projects/<slug>/work/recaplist/<id>.png —
one image per closing scene, five rows, one line each. The rows already covered
are written out; the ones this video does not reach are drawn dark, so the
student can see the shape of the rest of the answer without being told it.

WHY THIS REPLACES THE CHAKRA AT THE END
---------------------------------------
Through the body of the video the tracker has to be small: the picture is a
full-frame shot and anything larger sits on his face. The closing scenes are
different — he is keyed small onto the plate, and the whole top of the frame is
empty. That is the one place the answer can be shown in full rather than as a
fraction, so it is, and the chakra comes off: two trackers saying the same thing
in the same corner is worse than either.

The two unreached rows are NOT omitted. A student who has watched three causes
needs to know there are five, and that this video covered three — leaving them
out would quietly rewrite the question. Drawn dark, they read as "still to
come", which is what they are.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, features

ROOT = Path(__file__).resolve().parents[1]
FONTS = ROOT / "assets" / "fonts"
GOLD = (241, 175, 42)
WHITE = (250, 252, 253)
DARK = (150, 158, 170)           # a row this video does not reach
INK = (16, 21, 32)
ROW_GAP = 0.42                   # of the type size, between rows


def build(steps: list[dict], covered: int, size: int, width: int) -> Image.Image:
    # THE NUMERAL MUST FIT ITS CIRCLE. At size*1.06 in a circle of radius
    # size*0.42 the digits hung out of the bottom of the disc — 61px of type in
    # 48px of circle. The circle is now the larger of the two by construction
    # and the numeral is drawn from its centre, not from a guessed baseline.
    num = ImageFont.truetype(str(FONTS / "Khand-SemiBold.ttf"), int(size * 0.76))
    name = ImageFont.truetype(str(FONTS / "NotoSansDevanagari.ttf"), size)
    probe = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    row_h = int(size * (1.0 + ROW_GAP))
    pad = int(size * 0.55)
    h = pad * 2 + row_h * len(steps)
    # HUG THE CONTENT. A panel sized to the frame leaves a slab of empty ground
    # to the right of the longest word, which reads as a missing column rather
    # than as design.
    r_probe = int(size * 0.60)
    longest = max(probe.textlength(st["text"], font=name) for st in steps)
    width = min(width, int(pad * 2 + 2 * r_probe + size * 0.55 + longest))
    # ITS OWN GROUND. The closing plate is light cream at the top, and a dimmed
    # grey row sitting on it disappears completely — the two unreached rows were
    # invisible in the first cut, which defeats the whole point of showing them.
    # A dark panel makes white read as covered and grey as still to come, on any
    # plate. Same reasoning as the chakra's pill.
    im = Image.new("RGBA", (width, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, width - 1, h - 1], radius=int(size * 0.45),
                        fill=(13, 18, 28, 190))
    # a thin gold edge, so the panel reads as a card and not a black box
    d.rounded_rectangle([0, 0, width - 1, h - 1], radius=int(size * 0.45),
                        outline=GOLD + (120,), width=2)

    r = int(size * 0.60)
    x0 = pad
    for i, st in enumerate(steps):
        n = int(st["n"])
        done = n <= covered
        cy = pad + row_h * i + row_h // 2
        d.ellipse([x0, cy - r, x0 + 2 * r, cy + r],
                  fill=GOLD + (255,) if done else None,
                  outline=GOLD + (255,) if done else DARK + (150,),
                  width=max(2, r // 6))
        # anchor="mm" puts the glyph's own middle on the circle's middle, which
        # a hand-computed baseline had been getting wrong by a third of a line.
        d.text((x0 + r, cy), str(n), font=num, anchor="mm",
               fill=INK + (255,) if done else DARK + (190,))
        # A row still to come keeps its NUMBER and loses its words: the shape of
        # the answer is five, and what those two are is next video's business.
        label = st["text"] if done else "• • •"
        d.text((x0 + 2 * r + int(size * 0.55), cy - int(size * 0.62)), label,
               font=name, fill=(WHITE if done else DARK) + (255 if done else 140,))
    return im


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--size", type=int, default=74)
    a = ap.parse_args()
    if not features.check("raqm"):
        print("  Pillow has no raqm — run with DYLD_LIBRARY_PATH=/opt/homebrew/lib")
        return 1

    proj = ROOT / "projects" / a.slug
    spec = json.loads((proj / "reel.json").read_text(encoding="utf-8"))
    steps = (spec.get("steps") or {}).get("items")
    if not steps:
        print("  no `steps` in reel.json")
        return 1
    closing = spec.get("recap_list_on") or []
    if not closing:
        print("  no `recap_list_on` in reel.json — which closing scenes show it?")
        return 1
    fw, _ = (int(v) for v in spec.get("frame", "1080x1920").lower().split("x"))
    covered = max((int(s["n"]) for s in steps if s.get("at")), default=0)

    out = proj / "work" / "recaplist"
    out.mkdir(parents=True, exist_ok=True)
    im = build(steps, covered, a.size, int(fw * 0.88))
    for sid in closing:
        im.save(out / f"{sid}.png")
    print(f"  {covered} of {len(steps)} rows written, "
          f"{len(steps) - covered} left dark")
    print(f"  {len(closing)} scene(s) -> {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
