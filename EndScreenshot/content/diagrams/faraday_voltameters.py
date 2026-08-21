"""Redraw the textbook's series-voltameter figure as a clean line drawing."""
from PIL import Image, ImageDraw, ImageFont
import math

DEV = "/System/Library/Fonts/Supplemental/Kohinoor.ttc"
LAT = "/System/Library/Fonts/Supplemental/Arial.ttf"
W, H = 1240, 780
img = Image.new("RGB", (W, H), "white")
d = ImageDraw.Draw(img)
INK = (25, 25, 25)

def dev(s): return ImageFont.truetype(DEV, s)
def lat(s): return ImageFont.truetype(LAT, s)
def txt(x, y, t, f, a="mm"): d.text((x, y), t, font=f, fill=INK, anchor=a)

def sub(x, y, main, s, size=30):
    """H_2SO_4 style: normal glyph then a small lowered digit. Returns end x."""
    f, fs = lat(size), lat(int(size * 0.7))
    d.text((x, y), main, font=f, fill=INK, anchor="ls")
    x += d.textlength(main, font=f)
    if s:
        d.text((x, y + size * 0.22), s, font=fs, fill=INK, anchor="ls")
        x += d.textlength(s, font=fs)
    return x

def coil(x0, x1, y, n=9, r=15):
    """A spring/coil symbol drawn along a horizontal wire."""
    step = (x1 - x0) / n
    for i in range(n):
        cx = x0 + step * i
        d.arc([cx, y - r, cx + step, y + r], 180, 360, fill=INK, width=3)
    d.line([x0, y, x0 - 1, y], fill=INK, width=3)

# ---- the three voltameters ------------------------------------------------
CX = (250, 620, 990)
VW, VTOP, VBOT = 300, 400, 620
LIQ = 452

for cx in CX:
    l, r = cx - VW // 2, cx + VW // 2
    # vessel: straight sides, a slightly tapered foot, as in the book
    d.line([l, VTOP, l, VBOT - 34], fill=INK, width=3)
    d.line([r, VTOP, r, VBOT - 34], fill=INK, width=3)
    d.line([l, VBOT - 34, l + 40, VBOT], fill=INK, width=3)
    d.line([r, VBOT - 34, r - 40, VBOT], fill=INK, width=3)
    d.line([l + 40, VBOT, r - 40, VBOT], fill=INK, width=3)
    # liquid surface + a few level ticks
    d.line([l + 4, LIQ, r - 4, LIQ], fill=INK, width=3)
    for k in range(3):
        yy = LIQ + 42 + k * 34
        d.line([l + 26, yy, l + 74, yy], fill=INK, width=2)

# ---- electrodes ------------------------------------------------------------
ETOP, EBOT = 300, 575
EX = []
for cx in CX:
    a, b = cx - 78, cx + 78
    EX.append((a, b))
    for x in (a, b):
        d.line([x, ETOP, x, EBOT], fill=INK, width=6)

# ---- series wiring ---------------------------------------------------------
BUS = 150            # the top return wire
MID = 250            # the wire linking one cell to the next

# cell 1 left electrode -> up to the bus; bus -> cell 3 right electrode
d.line([EX[0][0], ETOP, EX[0][0], BUS], fill=INK, width=3)
d.line([EX[2][1], ETOP, EX[2][1], BUS], fill=INK, width=3)
d.line([EX[0][0], BUS, 500, BUS], fill=INK, width=3)
d.line([740, BUS, EX[2][1], BUS], fill=INK, width=3)

# battery, centred in the bus
for i, (dx, h) in enumerate(((0, 34), (26, 18), (52, 34), (78, 18))):
    d.line([560 + dx, BUS - h, 560 + dx, BUS + h], fill=INK,
           width=5 if h == 34 else 3)
d.line([500, BUS, 560, BUS], fill=INK, width=3)
d.line([638, BUS, 740, BUS], fill=INK, width=3)

# coils on the bus, either side of the battery
coil(300, 470, BUS)
coil(790, 960, BUS)

# cell 1 right -> cell 2 left, and cell 2 right -> cell 3 left
for (ax, bx) in ((EX[0][1], EX[1][0]), (EX[1][1], EX[2][0])):
    d.line([ax, ETOP, ax, MID], fill=INK, width=3)
    d.line([bx, ETOP, bx, MID], fill=INK, width=3)
    d.line([ax, MID, ax + 26, MID], fill=INK, width=3)
    d.line([bx - 26, MID, bx, MID], fill=INK, width=3)
    coil(ax + 26, bx - 26, MID, n=6)

# ---- labels ----------------------------------------------------------------
y = 672
x = sub(CX[0] - 108, y, "", "", 30)
d.text((CX[0] - 118, y), "तनु ", font=dev(30), fill=INK, anchor="ls")
x = CX[0] - 118 + d.textlength("तनु ", font=dev(30))
x = sub(x, y, "H", "2"); x = sub(x, y, "SO", "4")

x = sub(CX[1] - 132, y, "CuSO", "4")
d.text((x + 8, y), " विलयन", font=dev(30), fill=INK, anchor="ls")

x = sub(CX[2] - 140, y, "AgNO", "3")
d.text((x + 8, y), " विलयन", font=dev(30), fill=INK, anchor="ls")

txt(W // 2, 742, "चित्र—श्रेणीक्रम में व्यवस्थित विभिन्न वोल्टामीटर", dev(30), "mm")

img.save("EndScreenshot/content/diagrams/faraday_voltameters.png")
print("ok")
