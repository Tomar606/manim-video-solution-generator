"""Redraw the textbook's dry-cell section as a clean line drawing."""
from PIL import Image, ImageDraw, ImageFont

DEV = "/System/Library/Fonts/Supplemental/Kohinoor.ttc"
LAT = "/System/Library/Fonts/Supplemental/Arial.ttf"
W, H = 900, 980
img = Image.new("RGB", (W, H), "white")
d = ImageDraw.Draw(img)
INK = (25, 25, 25)
def dev(s): return ImageFont.truetype(DEV, s)
def lat(s): return ImageFont.truetype(LAT, s)
def t(x, y, s, f, a="mm"): d.text((x, y), s, font=f, fill=INK, anchor=a)
def leader(pts): d.line(pts, fill=INK, width=2, joint="curve")

def chem(x, y, parts, size=26, right=False):
    """parts = [(text, 0|1|2)], 1 lowered / 2 raised. Baseline anchored."""
    f, fs = lat(size), lat(int(size * 0.68))
    if right:
        x -= sum(d.textlength(s, font=(f if m == 0 else fs)) for s, m in parts)
    for s, m in parts:
        ff = f if m == 0 else fs
        dy = 0 if m == 0 else (size * 0.22 if m == 1 else -size * 0.40)
        d.text((x, y + dy), s, font=ff, fill=INK, anchor="ls")
        x += d.textlength(s, font=ff)
    return x

# ---- the cell, drawn as nested shells --------------------------------------
L, R, TOPY, BOT = 250, 470, 170, 830
d.rectangle([L, TOPY, R, BOT], outline=INK, width=4)          # Zn shell
d.rectangle([L + 24, TOPY + 44, R - 24, BOT - 22], outline=INK, width=3)
d.rectangle([L + 54, TOPY + 60, R - 54, BOT - 46], outline=INK, width=3)
CL, CR = 348, 372
d.rectangle([CL, TOPY + 16, CR, BOT - 70], outline=INK, width=3)   # carbon rod

# terminal cap
d.rectangle([336, TOPY - 40, 384, TOPY], outline=INK, width=4)
t(360, TOPY - 74, "(+)", lat(28))
t(360, BOT + 40, "(−)", lat(28))

# pitch seal — hatched band under the cap
for x in range(L + 28, R - 24, 14):
    d.line([x, TOPY + 44, x - 12, TOPY + 60], fill=INK, width=2)

# MnO2 + C paste — stippled, and kept strictly inside its own shell
SL, SR, ST, SB = L + 54, R - 54, TOPY + 60, BOT - 46
row = 0
while ST + 22 + row * 34 < SB - 12:
    y = ST + 22 + row * 34
    for col in range(9):
        x = SL + 10 + col * 12 + (6 if row % 2 else 0)
        if (x < CL - 5 or x > CR + 5) and SL < x < SR:
            d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=INK)
    row += 1

# ---- labels ----------------------------------------------------------------
t(520, TOPY - 22, "धातु की टोपी", dev(26), "lm"); leader([(514, TOPY - 22), (386, TOPY - 22)])
t(520, TOPY + 26, "पिच का सील", dev(26), "lm"); leader([(514, TOPY + 26), (420, TOPY + 52)])
t(520, TOPY + 100, "ग्रैफाइट कार्बन", dev(26), "lm"); leader([(514, TOPY + 100), (374, TOPY + 120)])

y = TOPY + 210
chem(520, y + 10, [("MnO", 0), ("2", 1), (" + C", 0)], 28)
leader([(514, y), (R - 62, y)])

y = TOPY + 330
chem(520, y + 10, [("NH", 0), ("4", 1), ("Cl + ZnCl", 0), ("2", 1)], 26)
t(520, y + 46, "का पेस्ट", dev(26), "lm")
leader([(514, y), (R - 34, y)])

y = TOPY + 470
t(520, y, "Zn का खोल", dev(26), "lm"); leader([(514, y), (R - 6, y)])

t(W // 2, 940, "चित्र—शुष्क सेल", dev(30), "mm")

img.save("EndScreenshot/content/diagrams/dry_cell.png")
print("ok")
