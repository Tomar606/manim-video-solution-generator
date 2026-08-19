"""Redraw the textbook's Daniell-cell figure as a clean line drawing."""
from PIL import Image, ImageDraw, ImageFont

DEV = "/System/Library/Fonts/Supplemental/Kohinoor.ttc"
LAT = "/System/Library/Fonts/Supplemental/Arial.ttf"
UNI = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"
W, H = 1400, 900
img = Image.new("RGB", (W, H), "white")
d = ImageDraw.Draw(img)
INK = (25, 25, 25)
def dev(s): return ImageFont.truetype(DEV, s)
def lat(s): return ImageFont.truetype(LAT, s)
def uni(s): return ImageFont.truetype(UNI, s)
def t(x, y, s, f, a="mm"): d.text((x, y), s, font=f, fill=INK, anchor=a)
def leader(pts): d.line(pts, fill=INK, width=2, joint="curve")

def chem(x, y, parts, size=26, centre=False):
    """parts = [(text, 0|1|2)] with 1 lowered, 2 raised. Baseline anchored."""
    f, fs = lat(size), lat(int(size * 0.68))
    if centre:
        x -= sum(d.textlength(s, font=(f if m == 0 else fs))
                 for s, m in parts) / 2
    for s, m in parts:
        ff = f if m == 0 else fs
        dy = 0 if m == 0 else (size * 0.22 if m == 1 else -size * 0.40)
        d.text((x, y + dy), s, font=ff, fill=INK, anchor="ls")
        x += d.textlength(s, font=ff)
    return x

# ---- geometry --------------------------------------------------------------
TOP = 150                       # the external wire
ZN, CU = 430, 980               # electrode centres
BL, BR = (320, 580), (830, 1090)  # beaker walls
BT, LIQ, BB = 500, 555, 740
BRL, BRR = 500, 910             # salt-bridge legs

# ---- beakers ---------------------------------------------------------------
for l, r in (BL, BR):
    d.line([l, BT, l, BB - 30], fill=INK, width=3)
    d.line([r, BT, r, BB - 30], fill=INK, width=3)
    d.line([l, BB - 30, l + 26, BB], fill=INK, width=3)
    d.line([r, BB - 30, r - 26, BB], fill=INK, width=3)
    d.line([l + 26, BB, r - 26, BB], fill=INK, width=3)
    d.line([l + 3, LIQ, r - 3, LIQ], fill=INK, width=3)

# ---- electrodes ------------------------------------------------------------
for x in (ZN, CU):
    d.rectangle([x - 9, 420, x + 9, 690], outline=INK, width=3)

# ---- external circuit ------------------------------------------------------
d.line([ZN, 420, ZN, TOP], fill=INK, width=3)
d.line([CU, 420, CU, TOP], fill=INK, width=3)
d.line([ZN, TOP, 500, TOP], fill=INK, width=3)
d.line([640, TOP, 692, TOP], fill=INK, width=3)
d.line([748, TOP, CU, TOP], fill=INK, width=3)
step = (640 - 500) / 8
d.line([(500, TOP)] + [(500 + step * (i + .5), TOP + (18 if i % 2 == 0 else -18))
                       for i in range(8)] + [(640, TOP)],
       fill=INK, width=3, joint="curve")
t(560, TOP - 46, "5", lat(26), "mm"); t(580, TOP - 46, "Ω", uni(26), "mm")
d.ellipse([692, TOP - 28, 748, TOP + 28], outline=INK, width=3)
t(720, TOP, "G", lat(26))

# the half-reaction the book prints over the circuit
x = chem(1060, 74, [("Zn", 0), ("(s)", 1)], 26)
t(x + 22, 66, "⇌", uni(26), "mm")
chem(x + 44, 74, [("Zn", 0), ("2+", 2), ("(aq)", 1), (" + 2e", 0), ("-", 2)], 26)

# ---- salt bridge -----------------------------------------------------------
d.arc([BRL, 300, BRR, 560], 180, 360, fill=INK, width=24)
d.line([BRL, 430, BRL, 610], fill=INK, width=24)
d.line([BRR, 430, BRR, 610], fill=INK, width=24)

# ---- labels ----------------------------------------------------------------
t(520, 236, "KNO", dev(26), "rm"); chem(520, 245, [("3", 1)], 26)
leader([(536, 238), (592, 296)])

t(800, 218, "विलयन से भीगा हुआ", dev(25), "mm")
t(800, 250, "फिल्टर पात्र", dev(25), "mm")
leader([(800, 268), (770, 302)])

t(1130, 330, "लवण-सेतु", dev(25), "lm"); leader([(1124, 332), (922, 372)])

# The rod labels are the book's, verbatim — it prints "(छड़ या जल)" on both.
t(300, 468, "जिंक रॉड (छड़ या जल)", dev(25), "rm"); leader([(306, 470), (418, 442)])
t(1110, 468, "कॉपर रॉड (छड़ या जल)", dev(25), "lm"); leader([(1104, 470), (992, 442)])
t(1110, 528, "रुई की डाँट", dev(25), "lm"); leader([(1104, 530), (1022, 548)])

# the ion label sits clear of the Hindi words, measured rather than guessed
_w = d.textlength("विलयन में ", font=dev(25))
# Set back from the beaker wall at x=320: at x=300 the "Zn2+" ran over it.
t(240 - _w, 596, "विलयन में", dev(25), "lm")
_x = chem(240, 606, [("Zn", 0), ("2+", 2)], 26)
leader([(_x + 12, 598), (356, 590)])
t(1110, 606, "विलयन में", dev(25), "lm")
chem(1110 + _w, 616, [("Cu", 0), ("2+", 2)], 26)
leader([(1104, 606), (1058, 596)])

chem(360, 648, [("2e", 0), ("-", 2)], 26)
chem(918, 648, [("2e", 0), ("-", 2)], 26)
chem(352, 706, [("ZnSO", 0), ("4", 1)], 28)
chem(862, 706, [("CuSO", 0), ("4", 1)], 28)

chem(450, 792, [("1M ZnSO", 0), ("4", 1), (" (aq)", 0)], 25, centre=True)
chem(960, 792, [("1M CuSO", 0), ("4", 1), (" (aq)", 0)], 25, centre=True)

t(700, 858, "चित्र—एक गैल्वेनिक सेल (डेनियल सेल)", dev(30), "mm")

img.save("EndScreenshot/content/diagrams/daniell_cell.png")
print("ok")
