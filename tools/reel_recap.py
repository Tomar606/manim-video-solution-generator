"""The numbered recap over the ending of an all-Veo reel, filling in as spoken.

    python tools/reel_recap.py <slug>

Reads `recap` from reel.json:

    "recap": {"scene": "s19", "title": "याद रखो: पाँच कदम",
              "items": [{"text": "लोकतंत्र की माँग", "word": "मांग"}, ...],
              "hold": ["s20", "s21"]}

and writes projects/<slug>/work/recap/state_N.png for N = 0..len(items), plus
recap.json with when each state starts inside the scene. The reel builder
overlays state N on the recap scene between its start and the next, and the
FULL list on every `hold` scene after it.

THIS IS THE PYQ LOOK, ON PURPOSE. The physics, chemistry and biology videos
end with a numbered list in the band above the presenter's head — every row
drawn from the start so the student sees the shape of the answer, each row's
text arriving as it is spoken, the one being spoken outlined in gold (memory:
reference-look-sept19; counted lists use digits). The ending of this reel keys
him small onto the subject background exactly as those videos do, so the same
list goes in the same place.

TIMED TO THE WORDS, NOT DIVIDED UP. Each item names the spoken word it belongs
to; the word's time comes from work/words.json (one transcription, shared with
the trim and the captions). An item whose word is not found is placed between
its neighbours rather than guessed — the same rule the captions follow.

Once a row is shown it stays: the list on the hold scenes is the finished list
(memory: labels-persist-once-shown).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, features

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.align import skel  # noqa: E402

FONTS = ROOT / "assets" / "fonts"
GOLD = (241, 175, 42)
INK = (250, 252, 253)
DIM = (150, 160, 175)
GRID = (105, 125, 150)
PILL = (24, 44, 70)
BAND_TOP, BAND_BOT = 0.16, 0.62      # the band above a 505x555 presenter
W_FRAC = 0.90


def row_png(items, title, k, FW, FH, size, finished=False):
    """The list with the first k rows filled, row k-1 outlined — or, with
    `finished`, every row in full ink and nothing outlined: the list as it is
    HELD on the scenes after the recap, where nothing is being spoken."""
    deva = ImageFont.truetype(str(FONTS / "NotoSansDevanagari.ttf"), size)
    tf = ImageFont.truetype(str(FONTS / "Khand-Bold.ttf"), int(size * 1.25))
    nf = ImageFont.truetype(str(FONTS / "Khand-Bold.ttf"), int(size * 0.85))
    W = int(FW * W_FRAC)
    rh = int(size * 2.35)
    n = len(items)
    title_h = int(size * 1.9) if title else 0
    H = title_h + rh * n
    im = Image.new("RGBA", (FW, FH), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x0 = (FW - W) // 2
    y0 = int(FH * (BAND_TOP + BAND_BOT) / 2) - H // 2
    # A BACKING, because this plate is light. The PYQ list sits on a navy plate
    # and needs none; on the political science background the dimmed rows
    # were grey on parchment. A soft dark panel behind the whole list keeps the
    # rows readable without turning it into a box stuck over the picture.
    m = int(size * 0.9)
    d.rounded_rectangle([x0 - m, y0 - m, x0 + W + m, y0 + H + m], radius=int(size * 0.7),
                        fill=(8, 18, 34, 168))
    if title:
        d.text((FW // 2, y0 + title_h // 2 - int(size * 0.15)), title, font=tf,
               fill=GOLD + (255,), anchor="mm")
    top = y0 + title_h
    # the frame, and every row's rule, from the start
    d.rounded_rectangle([x0, top, x0 + W, top + rh * n], radius=int(size * 0.4),
                        outline=GRID + (255,), width=3)
    for r in range(1, n):
        d.line([x0, top + rh * r, x0 + W, top + rh * r], fill=GRID + (255,), width=2)
    for r, it in enumerate(items):
        cy = top + rh * r + rh // 2
        # the number disc, always there
        rad = int(size * 0.55)
        cx = x0 + int(size * 1.35)
        d.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], fill=PILL + (255,),
                  outline=GOLD + (255,), width=3)
        d.text((cx, cy + int(size * 0.02)), str(r + 1), font=nf, fill=GOLD + (255,), anchor="mm")
        if r < k:
            bright = finished or (r == k - 1)
            d.text((x0 + int(size * 2.6), cy), it["text"], font=deva,
                   fill=(INK if bright else DIM) + (255,), anchor="lm")
    if 0 < k <= n and not finished:
        r = k - 1
        pad = 5
        d.rounded_rectangle([x0 - pad, top + rh * r + pad, x0 + W + pad,
                             top + rh * (r + 1) - pad],
                            radius=int(size * 0.3), outline=GOLD + (255,), width=4)
    return im


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--size", type=int, default=52)
    a = ap.parse_args()
    if not features.check("raqm"):
        print("  Pillow has no raqm — Devanagari would be mis-shaped silently "
              "(memory: pillow-raqm-needs-dyld).")
        return 1
    proj = ROOT / "projects" / a.slug
    spec = json.loads((proj / "reel.json").read_text(encoding="utf-8"))
    rc = spec.get("recap")
    if not rc:
        print("  reel.json has no recap")
        return 1
    FW, FH = (int(v) for v in spec.get("frame", "1080x1920").lower().split("x"))
    words = json.loads((proj / "work" / "words.json").read_text(encoding="utf-8"))
    sid = rc["scene"]
    rec = words.get(sid) or {"words": [], "dur": 10.0}
    sc = next(s for s in spec["scenes"] if s["id"] == sid)
    head = float((sc.get("trim") or [0.0, 0.0])[0])
    ws = [dict(w, s=w["s"] - head) for w in rec["words"]]
    dur = float(rec["dur"]) - head - float((sc.get("trim") or [0.0, 0.0])[1])

    items = rc["items"]
    starts = []
    for it in items:
        want = skel(it.get("word", ""))
        hit = next((w["s"] for w in ws if want and skel(w["w"]) == want), None)
        starts.append(hit)
    # interpolate the misses between their neighbours, then keep them in order
    known = [(i, t) for i, t in enumerate(starts) if t is not None]
    for i in range(len(starts)):
        if starts[i] is not None:
            continue
        lo = max([k for k, _ in known if k < i], default=None)
        hi = min([k for k, _ in known if k > i], default=None)
        if lo is None and hi is None:
            starts[i] = dur * (i + 1) / (len(items) + 1)
        elif lo is None:
            starts[i] = max(0.0, dict(known)[hi] - 0.9 * (hi - i))
        elif hi is None:
            starts[i] = dict(known)[lo] + 0.9 * (i - lo)
        else:
            t0, t1 = dict(known)[lo], dict(known)[hi]
            starts[i] = t0 + (t1 - t0) * (i - lo) / (hi - lo)
    for i in range(1, len(starts)):
        starts[i] = max(starts[i], starts[i - 1] + 0.35)

    out = proj / "work" / "recap"
    out.mkdir(parents=True, exist_ok=True)
    for k in range(len(items) + 1):
        row_png(items, rc.get("title", ""), k, FW, FH, a.size).save(out / f"state_{k}.png")
    row_png(items, rc.get("title", ""), len(items), FW, FH, a.size,
            finished=True).save(out / "state_all.png")
    doc = {"scene": sid, "hold": rc.get("hold", []), "n": len(items),
           "starts": [round(max(0.0, t - 0.20), 2) for t in starts]}
    (proj / "recap.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n",
                                     encoding="utf-8")
    for it, t in zip(items, starts):
        print(f"  {t:5.2f}s  {it['text']}" + ("" if it.get("word") else "  (no anchor)"))
    print(f"\n  {len(items) + 1} state(s) -> {out.relative_to(ROOT)}; "
          f"held on {', '.join(doc['hold']) or 'nothing'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
