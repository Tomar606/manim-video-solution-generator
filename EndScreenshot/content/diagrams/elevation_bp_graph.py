"""Redraw the textbook's elevation-of-boiling-point graph as a clean line figure."""
from PIL import Image, ImageDraw, ImageFont
import math

DEV = "/System/Library/Fonts/Supplemental/Kohinoor.ttc"
LAT = "/System/Library/Fonts/Supplemental/Arial.ttf"
LATI = "/System/Library/Fonts/Supplemental/Arial Italic.ttf"

W, H = 1010, 900
img = Image.new("RGB", (W, H), "white")
d = ImageDraw.Draw(img)
INK = (25, 25, 25)

def dev(sz):  return ImageFont.truetype(DEV, sz)
def lat(sz):  return ImageFont.truetype(LAT, sz)
def lati(sz): return ImageFont.truetype(LATI, sz)

def ctext(x, y, s, f, anchor="mm"):
    d.text((x, y), s, font=f, fill=INK, anchor=anchor)

def rot(x, y, s, f, deg):
    """Draw rotated text centred on (x, y)."""
    box = f.getbbox(s)
    tw, th = box[2] - box[0] + 12, box[3] - box[1] + 12
    tile = Image.new("RGBA", (tw, th), (255, 255, 255, 0))
    ImageDraw.Draw(tile).text((6 - box[0], 6 - box[1]), s, font=f, fill=INK)
    tile = tile.rotate(deg, expand=True, resample=Image.BICUBIC)
    img.paste(tile, (int(x - tile.width / 2), int(y - tile.height / 2)), tile)

def dashes(p0, p1, on=9, off=8, w=2):
    (x0, y0), (x1, y1) = p0, p1
    L = math.hypot(x1 - x0, y1 - y0)
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    t = 0.0
    while t < L:
        e = min(t + on, L)
        d.line([x0 + ux * t, y0 + uy * t, x0 + ux * e, y0 + uy * e], fill=INK, width=w)
        t = e + off

# ---- axes -----------------------------------------------------------------
OX, OY, XR, YT = 230.0, 740.0, 985.0, 130.0
d.line([OX, OY, XR, OY], fill=INK, width=3)     # x axis
d.line([OX, OY, OX, YT], fill=INK, width=3)     # y axis

ATM = 235.0                                     # the 1 atm level

# ---- the two vapour-pressure curves ---------------------------------------
def curve(xs, xe, ybase, ytop, p=3.2):
    pts = []
    for i in range(241):
        u = i / 240
        pts.append((xs + u * (xe - xs), ybase - (ybase - ytop) * u ** p))
    return pts

solvent  = curve(310, 800, 590, 150)            # विलायक — higher vapour pressure
solution = curve(415, 905, 645, 155)            # विलयन

for pts in (solvent, solution):
    d.line(pts, fill=INK, width=3, joint="curve")

def cross(pts, y):
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if y0 >= y >= y1:
            t = (y0 - y) / (y0 - y1)
            return x0 + t * (x1 - x0)
    return pts[-1][0]

XB = cross(solvent, ATM)                        # X — solvent boils
XD = cross(solution, ATM)                       # Y — solution boils

# ---- 1 atm line and the two boiling-point ordinates -----------------------
dashes((OX + 3, ATM), (XR - 15, ATM))
ctext(OX - 12, ATM - 16, "1 atm.", lat(30), anchor="rm")
for x in (XB, XD):
    dashes((x, ATM), (x, OY - 3), on=7, off=7)

# ---- point letters ---------------------------------------------------------
ctext(solvent[0][0] - 22, solvent[0][1] - 4, "A", lat(34))
ctext(solution[0][0] - 22, solution[0][1] - 4, "C", lat(34))
ctext(solvent[-1][0] - 30, solvent[-1][1] - 30, "B", lat(34))
ctext(solution[-1][0] + 26, solution[-1][1] - 26, "D", lat(34))
ctext(XB - 26, ATM + 26, "X", lat(34))
ctext(XD + 26, ATM + 26, "Y", lat(34))

# short lead-in stubs at A and C, as in the book
d.line([solvent[0][0] - 14, solvent[0][1], solvent[0][0], solvent[0][1]], fill=INK, width=3)
d.line([solution[0][0] - 14, solution[0][1], solution[0][0], solution[0][1]], fill=INK, width=3)

# ---- curve names, written along the curves --------------------------------
rot(560, 470, "विलायक", dev(34), 32)
rot(672, 545, "विलयन",  dev(34), 32)

# ---- headings over the two boiling points ---------------------------------
ctext(700, 22, "विलायक का", dev(30), anchor="ma")
ctext(700, 60, "क्वथनांक",  dev(30), anchor="ma")
ctext(905, 22, "विलयन का", dev(30), anchor="ma")
ctext(905, 60, "क्वथनांक",  dev(30), anchor="ma")
d.line([(700, 104), (720, 130), (752, 150)], fill=INK, width=2, joint="curve")
d.line([(905, 104), (900, 132), (888, 152)], fill=INK, width=2, joint="curve")

# ---- ΔT_b, spanned between the two ordinates ------------------------------
AY = 585.0
d.line([XB, AY, XD, AY], fill=INK, width=2)
for x, s in ((XB, 1), (XD, -1)):
    d.polygon([(x, AY), (x + s * 15, AY - 7), (x + s * 15, AY + 7)], fill=INK)

def sub_sup(x, y, main, sub="", sup="", size=34):
    """T with a lowered b and, optionally, a raised 0 — returns the end x."""
    f, fs = lati(size), lat(int(size * 0.68))
    d.text((x, y), main, font=f, fill=INK, anchor="ls")
    x += d.textlength(main, font=f)
    if sub:
        d.text((x, y + size * 0.20), sub, font=lati(int(size * 0.68)), fill=INK, anchor="ls")
    if sup:
        d.text((x, y - size * 0.42), sup, font=fs, fill=INK, anchor="ls")
    return x + d.textlength(sub or sup or "", font=fs)

d.text(((XB + XD) / 2 - 34, AY - 58), "Δ", font=lat(34), fill=INK, anchor="ls")
sub_sup((XB + XD) / 2 - 8, AY - 58, "T", sub="b")

# ---- x-axis labels ---------------------------------------------------------
ctext(520, 790, "परम ताप", dev(32), anchor="ma")
# XB is where the SOLVENT boils, XD where the SOLUTION boils. The superscript
# zero marks the pure solvent, so it belongs on XB — the textbook prints these
# the other way round, which contradicts the answer's own "T_b > T_b^0".
sub_sup(XB - 22, 812, "T", sub="b", sup="0")
sub_sup(XD - 20, 812, "T", sub="b")

# ---- y-axis label ----------------------------------------------------------
rot(52, 470, "वाष्पदाब", dev(32), 90)

# ---- caption ---------------------------------------------------------------
ctext(560, 858, "चित्र—क्वथनांक में उन्नयन", dev(32), anchor="ma")

img.save("EndScreenshot/content/diagrams/elevation_bp_graph.png")
print("X at", round(XB), " Y at", round(XD))
