#!/usr/bin/env python3
"""The opening card, as separate LAYERS so it can be animated.

    python3 tools/clip/make_intro_layers.py <slug> "2025" [marks]   # SYSTEM python3 - libraqm

Reads  work/<slug>/assets/question_sheet.png  (tools/question_card.py)
Writes work/<slug>/out/layers/*.png           (read by tools/clip/intro.mjs)

work/kmno4/make_intro.py builds this same card as ONE flat PNG. The runbook's
"Still open" note is that the flat card is static, while the Manim scene stages
it in over ~3s. Splitting it into layers is what makes that possible: intro.mjs
stacks these in a browser and drives each one on its own clock.

Every layer is a FULL 1080x1920 RGBA canvas with only its own element drawn, so
stacking them at (0,0) reproduces the flat card exactly and no layer needs to
carry a position. Cheap in pixels, and it means a layer can be moved or delayed
without recomputing anything.

Geometry is src/question_card.py - the same fractions the approved Manim scene
uses, measured off the approved still.

MUST RUN ON A PILLOW WITH LIBRAQM. The years pill and the marks badge are
Devanagari; without libraqm Pillow lays them out in storage order and every
matra lands after its consonant, silently. See CLAUDE.md.
"""
import sys, math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, features

if not features.check("raqm"):
    sys.exit("refusing to run: Pillow has no libraqm - Devanagari would be garbled")

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
if len(sys.argv) < 3:
    sys.exit('usage: make_intro_layers.py <slug|folder> "<years>" [marks]')
VIDEO = Path(sys.argv[1]).resolve() if "/" in sys.argv[1] else ROOT / "work" / sys.argv[1]
if not VIDEO.is_dir():
    sys.exit(f"no video folder: {VIDEO}")
from src import question_card as qc

W, H = 1080, 1920
U = H / 8.0
KHAND = str(ROOT / "assets" / "fonts" / "Khand-Bold.ttf")
YEARS = sys.argv[2]
MARKS = sys.argv[3] if len(sys.argv) > 3 else ""      # "" = no badge (approved look)
SHEET = VIDEO / "assets" / "question_sheet.png"
if not SHEET.exists():
    sys.exit(f"missing {SHEET} — make it with tools/question_card.py first")
OUT = VIDEO / "out" / "layers"
OUT.mkdir(parents=True, exist_ok=True)

GOLD = tuple(int(qc.GOLD[i:i + 2], 16) for i in (1, 3, 5))
TEAL = tuple(int(qc.TEAL[i:i + 2], 16) for i in (1, 3, 5))
CREAM = (255, 255, 255)

f = lambda px: ImageFont.truetype(KHAND, px)
blank = lambda: Image.new("RGBA", (W, H), (0, 0, 0, 0))


def tsize(d, s, fnt):
    b = d.textbbox((0, 0), s, font=fnt)
    return b[2] - b[0], b[3] - b[1]


def ticks(d, cx, cy, w, h, colour, n, pad):
    """The gold sparks. Same spots and taper as the approved scene's.

    The scene's wedge (0.24/0.020/0.062 units) is at Manim's stroke scale and
    comes out fat here - two of the pill's four landed on the sheet's torn edge.
    These are measured off the reference still instead."""
    hw, hh = w / 2 + pad, h / 2 + pad * 0.55
    spots = [(-hw, hh * .55), (-hw * .96, -hh * .15), (-hw * .80, hh * .95),
             (hw, hh * .55), (hw * .96, -hh * .15), (hw * .80, hh * .95)]
    L, w0, w1 = 0.155 * U, 0.013 * U, 0.038 * U
    for i, (dx, dy) in enumerate(spots[:n]):
        out = -1 if dx < 0 else 1
        ang = (math.pi if out < 0 else 0) + out * (0.30 + 0.32 * (i % 3))
        pts = [(0, -w0), (L, -w1), (L, w1), (0, w0)]
        ca, sa = math.cos(ang), math.sin(ang)
        pts = [(px - L / 2, py) for px, py in pts]
        d.polygon([(cx + dx + px * ca - py * sa, cy - dy + px * sa + py * ca)
                   for px, py in pts], fill=colour)


def scribble(d, cx, cy, width, colour, wobble, tilt):
    """The hand-drawn rule under the heading: two passes, the lower one faint."""
    for shift, sw, alpha in ((0, 7, 242), (wobble * 0.9, 4, 140)):
        pts = []
        for i in range(26):
            u = i / 25
            y = (math.sin(u * 5.2) * .3 + math.sin(u * 11.0 + 1.1) * .18) * wobble
            y += (u - .5) ** 2 * -wobble * 1.4
            x, y = (u - .5) * width, y + shift
            ca, sa = math.cos(tilt), math.sin(tilt)
            pts.append((cx + x * ca - y * sa, cy - (x * sa + y * ca)))
        d.line(pts, fill=colour + (alpha,), width=sw, joint="curve")


def rounded(size, radius, fill=None, outline=None, w=0, tilt=0.0):
    pad = 40
    im = Image.new("RGBA", (size[0] + pad * 2, size[1] + pad * 2), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle(
        [pad, pad, pad + size[0], pad + size[1]], radius=radius,
        fill=fill, outline=outline, width=w)
    return im.rotate(math.degrees(tilt), expand=True, resample=Image.BICUBIC)


geom = {}

# ---- 1. the ringed question mark ------------------------------------------- #
im = blank(); d = ImageDraw.Draw(im, "RGBA")
r = qc.Q_MARK_R * H
cy = qc.Q_MARK_Y * H
d.ellipse([540 - r, cy - r, 540 + r, cy + r], outline=TEAL + (255,), width=6)
d.text((540, cy + 2), "?", font=f(int(r * 1.75)), fill=TEAL + (255,), anchor="mm")
im.save(OUT / "ring.png"); geom["ring"] = [540, round(cy)]

# ---- 2. the heading, sized to a share of the frame -------------------------- #
im = blank(); d = ImageDraw.Draw(im, "RGBA")
size = 96
while True:
    fnt = f(size)
    tw, th = tsize(d, qc.HEAD_TEXT, fnt)
    if tw <= W * qc.HEAD_W_MAX or size <= 20:
        break
    size -= 2
hy = qc.Q_WORD_Y * H
d.text((540, hy), qc.HEAD_TEXT, font=fnt, fill=GOLD + (255,), anchor="mm")
im.save(OUT / "head.png"); geom["head"] = [540, round(hy)]

# ---- 3. its six sparks, on their own layer so they can lag ------------------ #
im = blank(); d = ImageDraw.Draw(im, "RGBA")
ticks(d, 540, hy, tw, th, GOLD + (255,), 6, max(qc.TICK_PAD * U, tw * 0.11))
im.save(OUT / "sparks.png")

# ---- 4. the hand-drawn rule ------------------------------------------------- #
im = blank(); d = ImageDraw.Draw(im, "RGBA")
rule_w = min(tw * qc.RULE_W, W * qc.RULE_W_MAX)
scribble(d, 540, qc.RULE_Y * H, rule_w, CREAM, 0.018 * U, qc.DECOR_TILT)
im.save(OUT / "rule.png")
geom["rule"] = [540, round(qc.RULE_Y * H), round(rule_w)]

# ---- 5. the exam sheet ------------------------------------------------------ #
im = blank()
sheet = Image.open(SHEET).convert("RGBA")
sw = int(W * qc.SHEET_W)
sh = int(sheet.height * sw / sheet.width)
sheet = sheet.resize((sw, sh), Image.LANCZOS)
sx, sy = (W - sw) // 2, int(qc.SHEET_Y * H - sh / 2)
im.alpha_composite(sheet, (sx, sy))
im.save(OUT / "sheet.png"); geom["sheet"] = [540, round(sy + sh / 2), sw, sh]

# ---- 6. the tape across its top edge ---------------------------------------- #
im = blank()
tape = rounded((int(W * qc.TAPE_W), int(H * qc.TAPE_H)), 14,
               fill=TEAL + (int(255 * qc.TAPE_OPACITY),), tilt=qc.TAPE_TILT)
ty = int(sy + sh * qc.TAPE_EDGE)
im.alpha_composite(tape, (540 - tape.width // 2, ty - tape.height // 2))
im.save(OUT / "tape.png"); geom["tape"] = [540, ty]

# ---- 7. the marks badge ----------------------------------------------------- #
# NOT in the approved Manim scene - added from the reference card. It sits on
# the sheet's top-right corner, so it is positioned off the SHEET's measured
# box rather than off the frame, and follows the sheet if that ever moves.
# OFF BY DEFAULT. The approved card - CHE-C4-LA-01 part 1, which the user
# pointed at as the reference on 2026-09-12 - carries no badge, and BIO-C2-LA-01
# went out with one before that was checked. Pass a marks value ("4") to draw
# it; an empty value writes a transparent layer so intro.mjs, which lists the
# badge by name, still finds a file and stacks nothing.
im = blank(); d = ImageDraw.Draw(im, "RGBA")
br = int(0.082 * W)
bcx, bcy = sx + sw - int(br * 0.55), sy + int(br * 1.25)
if MARKS.strip() and MARKS.strip().lower() not in ("0", "none", "no"):
    d.ellipse([bcx - br, bcy - br, bcx + br, bcy + br], fill=GOLD + (255,),
              outline=CREAM + (235,), width=5)
    fb, fs = f(int(br * 1.10)), f(int(br * 0.52))
    d.text((bcx, bcy - br * 0.22), MARKS, font=fb, fill=(20, 30, 55, 255), anchor="mm")
    d.text((bcx, bcy + br * 0.52), "अंक", font=fs, fill=(20, 30, 55, 255), anchor="mm")
im.save(OUT / "badge.png"); geom["badge"] = [bcx, bcy, br]

# ---- 8. the years pill ------------------------------------------------------ #
im = blank(); d = ImageDraw.Draw(im, "RGBA")
f36, f42 = f(52), f(60)
w1, _ = tsize(d, "वर्ष ", f36)
w2, _ = tsize(d, YEARS, f42)
w3, _ = tsize(d, " में", f36)
line2 = "ये प्रश्न था"
w4, _ = tsize(d, line2, f36)
tw2 = max(w1 + w2 + w3, w4)
pill_w, pill_h = int(tw2 + 0.85 * U * 0.55), 160
pill = rounded((pill_w, pill_h), 46, outline=GOLD + (255,), w=5, tilt=qc.DECOR_TILT)
pcx, pcy = 540, int(qc.SHEET_YEARS_Y * H)
im.alpha_composite(pill, (pcx - pill.width // 2, pcy - pill.height // 2))

lay = Image.new("RGBA", (pill_w + 80, pill_h + 40), (0, 0, 0, 0))
dl = ImageDraw.Draw(lay)
cx0 = lay.width / 2 - (w1 + w2 + w3) / 2
ytop = lay.height / 2 - 34
dl.text((cx0, ytop), "वर्ष ", font=f36, fill=CREAM + (255,), anchor="lm")
dl.text((cx0 + w1, ytop), YEARS, font=f42, fill=TEAL + (255,), anchor="lm")
dl.text((cx0 + w1 + w2, ytop), " में", font=f36, fill=CREAM + (255,), anchor="lm")
dl.text((lay.width / 2, ytop + 66), line2, font=f36, fill=CREAM + (255,), anchor="mm")
lay = lay.rotate(math.degrees(qc.DECOR_TILT), expand=True, resample=Image.BICUBIC)
im.alpha_composite(lay, (pcx - lay.width // 2, pcy - lay.height // 2))
im.save(OUT / "pill.png"); geom["pill"] = [pcx, pcy]

# ---- 9. the pill's four sparks ---------------------------------------------- #
im = blank(); d = ImageDraw.Draw(im, "RGBA")
ticks(d, pcx, pcy, pill_w, pill_h, GOLD + (255,), 4, 0.22 * U)
im.save(OUT / "pillsparks.png")

import json
(OUT / "geom.json").write_text(json.dumps(geom, indent=1))
print(f"9 layers -> {OUT}")
for k, v in geom.items():
    print(f"   {k:<6} {v}")
