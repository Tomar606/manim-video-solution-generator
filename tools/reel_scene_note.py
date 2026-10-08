"""One line saying what the student is looking at, on the cinematic scenes.

    python tools/reel_scene_note.py <slug> [--size 44]

Reads `note` off each scene in reel.json that has a `broll`, and writes
projects/<slug>/work/notes/<id>.png — a small card the reel builder lays over
the cutaway.

WHY ONLY THE CUTAWAYS NEED IT
-----------------------------
When the presenter is on screen the picture explains itself: he is talking and
the caption says what he said. A cutaway is different. The voice carries on but
the picture has changed to something the narration does not name — a shuttered
lane, an empty chamber, a hand on a ledger. A student who does not recognise it
spends the shot working out what they are looking at instead of listening.

So the note says what the PICTURE is, never what the voice is saying — that is
the caption's job, and repeating it underneath would be the failure the house
style already warns about (memory: screen-carries-only-what-teaches). One line,
because two would start competing with the caption for the same attention.

THE CARD: a dark ground with a gold rule down its left edge, which is the same
language as the recap panel's gold border, so the two read as one family rather
than two overlays that happen to share a video.
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
GROUND = (13, 18, 28, 196)


def card(text: str, size: int, max_w: int) -> Image.Image:
    f = ImageFont.truetype(str(FONTS / "NotoSansDevanagari.ttf"), size)
    probe = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    while size > 24 and probe.textlength(text, font=f) > max_w:
        size -= 2
        f = ImageFont.truetype(str(FONTS / "NotoSansDevanagari.ttf"), size)
    tw = int(probe.textlength(text, font=f))
    rule = max(4, int(size * 0.10))
    pad_x, pad_y = int(size * 0.62), int(size * 0.46)
    w = rule + pad_x * 2 + tw
    h = pad_y * 2 + int(size * 1.34)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    rad = int(size * 0.26)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=rad, fill=GROUND)
    # the gold rule, squared off against the card's left edge
    d.rounded_rectangle([0, 0, rule + rad, h - 1], radius=rad, fill=GOLD + (255,))
    d.rectangle([rule, 0, rule + rad, h - 1], fill=GROUND)
    d.text((rule + pad_x, h // 2), text, font=f, fill=WHITE + (255,), anchor="lm")
    return im


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--size", type=int, default=44)
    a = ap.parse_args()
    if not features.check("raqm"):
        print("  Pillow has no raqm — run with DYLD_LIBRARY_PATH=/opt/homebrew/lib")
        return 1

    proj = ROOT / "projects" / a.slug
    spec = json.loads((proj / "reel.json").read_text(encoding="utf-8"))
    fw, _ = (int(v) for v in spec.get("frame", "1080x1920").lower().split("x"))
    out = proj / "work" / "notes"
    out.mkdir(parents=True, exist_ok=True)

    n = 0
    for s in spec["scenes"]:
        note = s.get("note")
        if not note:
            continue
        if not s.get("broll"):
            print(f"  {s['id']}: has a note but is not a cutaway — skipped, the "
                  f"presenter's own scenes explain themselves")
            continue
        im = card(note, a.size, int(fw * 0.74))
        im.save(out / f"{s['id']}.png")
        print(f"  {s['id']}: {note}")
        n += 1
    print(f"\n  {n} scene note(s) -> {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
