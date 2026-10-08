"""The answer's SHAPE, held on screen: numbered steps that fill in as he speaks.

    python tools/reel_steps.py <slug> [--only s06] [--size 46]

Reads `steps` off reel.json — a title and an ordered list of {n, text, at} —
and writes projects/<slug>/work/steps/<id>.png, one per scene, which the reel
builder overlays exactly where tools/reel_points.py's point would go.

WHY THIS EXISTS, and what it replaces
-------------------------------------
The Nepal video put its five steps on screen only in the last twenty seconds.
For the three minutes before that a student had no map of the answer: each
scene stated its own point and the point then vanished, so at no moment could
you see that there were five of these and which one you were in. The question
is worth four marks for naming five causes, and the video never showed five of
anything until it was over.

A point says what to write down for THIS scene. A step says where this scene
sits in the answer. They are different jobs and this does the second.

WHY A STRIP AND NOT A LIST
--------------------------
There is no empty band for a five-item list. This route is a full-frame talking
head: his head is near the top, the caption owns the foot, and a list large
enough to read would sit on his face. So the steps are a single line of
numbered pills — the one being spoken is gold and carries its name, the rest
are bare circles. That costs one line and still answers "how many are there and
where am I", which is the part a student needs and the Nepal cut never gave.

The ones not yet reached stay on screen as empty circles ON PURPOSE: the shape
of the answer is visible from the first step, not assembled at the end. A step
already covered keeps its circle filled (memory: labels-persist-once-shown).
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
INK = (20, 28, 44)
PAD_X = 38               # from the frame edge
# (scale, glow) per pop frame: swell, hold the glow, settle back to true size.
POP = [(1.00, 0.9), (1.16, 1.0), (1.22, 0.8), (1.14, 0.5), (1.06, 0.25), (1.00, 0.0)]
POP_STEP = 0.085         # seconds each frame is held
GAP = 14                 # between pills


def strip(steps: list[dict], active: int, size: int, max_w: int) -> Image.Image:
    """An Ashoka chakra that fills as the causes are covered, then `n/N`, then
    the name of the one being spoken.

    WHY A WHEEL AND NOT FIVE PILLS. Five circles told you where you were but
    took a third of the frame's width and read as decoration. A chakra is the
    subject's own symbol — the same wheel on the flag the question is about —
    and its arc carries the fraction without any counting. The number is there
    in words as well because a student glancing up should not have to measure
    an angle.
    """
    total = len(steps)
    num = ImageFont.truetype(str(FONTS / "Khand-SemiBold.ttf"), int(size * 1.15))
    name = ImageFont.truetype(str(FONTS / "NotoSansDevanagari.ttf"), int(size * 1.02))
    probe = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    label = next((s["text"] for s in steps if int(s["n"]) == active), "")

    R = int(size * 0.95)                 # the wheel
    pad = 6
    frac = f"{active}/{total}"
    fw_ = int(probe.textlength(frac, font=num))
    lw = int(probe.textlength(label, font=name)) if label else 0
    w = 2 * R + 16 + fw_ + (18 + lw if label else 0) + pad * 2
    h = 2 * R + pad * 2
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    cx, cy = pad + R, pad + R
    box = [cx - R, cy - R, cx + R, cy + R]
    ring = max(4, int(R * 0.22))
    # the unfilled wheel, then the covered arc over it, clockwise from the top
    d.ellipse(box, outline=WHITE + (135,), width=ring)
    sweep = 360.0 * active / total
    if sweep > 0:
        d.arc(box, start=-90, end=-90 + sweep, fill=GOLD + (255,), width=ring)
    # 24 SPOKES FROM HUB TO RIM, which is what makes it a chakra rather than a
    # dial. The first cut ran them in a thin band just inside the ring and the
    # whole thing read as a stopwatch.
    import math
    ri, ro = int(R * 0.20), R - ring - int(R * 0.04)
    for k in range(24):
        a = math.radians(k * 15 - 90)
        d.line([cx + ri * math.cos(a), cy + ri * math.sin(a),
                cx + ro * math.cos(a), cy + ro * math.sin(a)],
               fill=WHITE + (150,), width=max(1, ring // 5))
    hub = max(3, int(R * 0.16))
    d.ellipse([cx - hub, cy - hub, cx + hub, cy + hub], fill=GOLD + (255,))

    x = pad + 2 * R + 16
    d.text((x, cy - int(size * 0.72)), frac, font=num, fill=GOLD + (255,))
    x += fw_ + 18
    if label:
        d.text((x, cy - int(size * 0.66)), label, font=name, fill=WHITE + (255,))
    bb = im.getbbox()
    return im.crop(bb) if bb else im


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--only", nargs="*", default=[])
    ap.add_argument("--size", type=int, default=62)
    a = ap.parse_args()
    if not features.check("raqm"):
        print("  Pillow has no raqm, so every i-matra would sit after its consonant. "
              "Run with DYLD_LIBRARY_PATH=/opt/homebrew/lib.")
        return 1

    proj = ROOT / "projects" / a.slug
    spec = json.loads((proj / "reel.json").read_text(encoding="utf-8"))
    steps = spec.get("steps")
    if not steps:
        print("  no `steps` in reel.json — nothing to draw")
        return 1
    fw, _ = (int(v) for v in spec.get("frame", "1080x1920").lower().split("x"))
    out = proj / "work" / "steps"
    out.mkdir(parents=True, exist_ok=True)

    # which step each scene is inside: a step stays active until the next begins
    order = [s["id"] for s in spec["scenes"]]
    active_at, cur = {}, 0
    for sid in order:
        for s in steps["items"]:
            if s.get("at") == sid:
                cur = int(s["n"])
        active_at[sid] = cur

    n = 0
    for sid in order:
        if a.only and sid not in a.only:
            continue
        if not active_at[sid]:
            continue                      # before the first step: nothing to show
        im = strip(steps["items"], active_at[sid], a.size, int(fw * 0.90))
        if im.width > fw * 0.92:
            im = im.resize((int(fw * 0.92), int(im.height * fw * 0.92 / im.width)),
                           Image.LANCZOS)
        im.save(out / f"{sid}.png")

        # THE POP, on the scene where the wheel actually advances. A tracker
        # that changes while nobody is looking has not told anyone anything,
        # so the moment a cause lands the wheel swells, glows and settles.
        # Drawn as frames rather than an ffmpeg expression because the glow has
        # to grow with the scale, and because the reel builder can then hold
        # each frame for its own slice with a plain overlay.
        if any(st.get("at") == sid for st in steps["items"]):
            for k, (scale, glow) in enumerate(POP):
                w2, h2 = int(im.width * scale), int(im.height * scale)
                big = im.resize((w2, h2), Image.LANCZOS)
                if glow:
                    from PIL import ImageFilter
                    aura = big.filter(ImageFilter.GaussianBlur(int(6 * glow) + 2))
                    lay = Image.new("RGBA", (w2, h2), (0, 0, 0, 0))
                    lay = Image.alpha_composite(lay, Image.merge("RGBA", (
                        *aura.split()[:3],
                        aura.split()[3].point(lambda v: int(v * glow)))))
                    big = Image.alpha_composite(lay, big)
                big.save(out / f"{sid}_pop{k}.png")
        lab = next((s["text"] for s in steps["items"]
                    if int(s["n"]) == active_at[sid]), "")
        print(f"  {sid}: step {active_at[sid]}/{len(steps['items'])}  {lab}")
        n += 1
    print(f"\n  {n} step strip(s) -> {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
