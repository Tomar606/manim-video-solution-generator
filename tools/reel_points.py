"""The point a scene is making, on screen, beside the clip.

    python tools/reel_points.py <slug> [--only s06] [--size 54]

Reads `point` off each scene in reel.json and writes
projects/<slug>/work/points/<id>.png plus a top vignette. The reel builder
overlays them the way it overlays captions.

A POINT IS NOT THE CAPTION AGAIN
--------------------------------
The caption says what he said; the point says what to WRITE DOWN. So it is
short, it carries the year as digits where there is one, and it is the thing a
student would put in an answer — "2008: राजतंत्र समाप्त, गणराज्य घोषित", not the
sentence that was spoken around it. A scene whose line is pure narration
("चलो, कहानी शुरू से देखते हैं") gets no point at all, and preflight-style
judgement applies: if the screen would only be restating the caption, leave it
quiet (memory: screen-carries-only-what-teaches).

WHERE IT GOES, and why that is the awkward part
-----------------------------------------------
The PYQ route puts its content above the presenter because the presenter is a
small figure at the foot of a mostly empty frame. Here he is FULL FRAME with his
head near the top, so there is no empty band to put anything in. The point
therefore sits at the very top, on a scrim that is dark at the top edge and gone
by a fifth of the way down — the mirror of the caption's vignette, so the two
read as a pair rather than as two unrelated overlays. It is kept to one short
line for the same reason: a second line would reach his hair.
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
SCRIM = 0.20             # share of frame height the top scrim covers
SCRIM_MAX = 0.86


def top_vignette(w: int, h: int) -> Image.Image:
    g = Image.new("L", (1, h), 0)
    px = g.load()
    bot = int(h * SCRIM)
    for y in range(0, bot):
        f = 1.0 - (y / max(1, bot - 1))
        px[0, y] = int(255 * SCRIM_MAX * (f ** 1.5))
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    out.putalpha(g.resize((w, h)))
    return out


def draw_point(text: str, size: int, max_w: int) -> Image.Image:
    """The point, gold, with a short gold rule under it."""
    khand = FONTS / "Khand-Bold.ttf"
    f = ImageFont.truetype(str(khand), size)
    probe = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    while size > 22 and probe.textlength(text, font=f) > max_w:
        size -= 2
        f = ImageFont.truetype(str(khand), size)
    tw = int(probe.textlength(text, font=f))
    im = Image.new("RGBA", (tw + size, int(size * 2.1)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    base = int(size * 1.25)
    d.text((size // 2, base), text, font=f, fill=GOLD + (255,), anchor="ls")
    d.line([size // 2, base + int(size * 0.32), size // 2 + tw, base + int(size * 0.32)],
           fill=WHITE + (200,), width=max(3, size // 18))
    bb = im.getbbox()
    return im.crop(bb) if bb else im


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--only", nargs="*", default=[])
    ap.add_argument("--size", type=int, default=58)
    a = ap.parse_args()
    if not features.check("raqm"):
        print("  Pillow has no raqm — Devanagari would be mis-shaped silently "
              "(memory: pillow-raqm-needs-dyld).")
        return 1
    proj = ROOT / "projects" / a.slug
    spec = json.loads((proj / "reel.json").read_text(encoding="utf-8"))
    FW, FH = (int(v) for v in spec.get("frame", "1080x1920").lower().split("x"))
    out = proj / "work" / "points"
    out.mkdir(parents=True, exist_ok=True)
    top_vignette(FW, FH).save(out / "vignette_top.png")

    n = 0
    quiet = []
    for s in spec["scenes"]:
        sid = s["id"]
        if a.only and sid not in a.only:
            continue
        txt = (s.get("point") or "").strip()
        if not txt:
            quiet.append(sid)
            continue
        im = draw_point(txt, a.size, int(FW * 0.88))
        im.save(out / f"{sid}.png")
        n += 1
        print(f"  {sid}: {txt}")
    print(f"\n  {n} point(s) -> {out.relative_to(ROOT)}")
    if quiet:
        print(f"  quiet, on purpose: {' '.join(quiet)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
