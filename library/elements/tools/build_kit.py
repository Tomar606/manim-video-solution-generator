"""Build the skinnable element kit: kit/svg/**, kit/cards/*.html, kit/preview.html
and manifest.json.  Re-run after any change; every output is regenerated.

    python3 library/elements/tools/build_kit.py

All art here is original (Arivihan).  Hand-drawn marks are generated from a
fixed seed so they come out identical on every build.  Every line is a
STROKED path with pathLength="1" so it can draw on with stroke-dashoffset.
"""
import json, math, random, re, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]          # library/elements
KIT = ROOT / "kit"
VENDOR = ROOT / "vendor"
SKINS = ["night-hud", "paper-editorial", "chalk-slate", "pastel-notebook"]

# ------------------------------------------------------------------ geometry
def f(v): return f"{v:.1f}".rstrip("0").rstrip(".")

def catmull(pts):
    """Smooth path through points (Catmull-Rom -> cubic Bezier)."""
    if len(pts) < 3:
        return "M" + " L".join(f"{f(x)} {f(y)}" for x, y in pts)
    d = [f"M{f(pts[0][0])} {f(pts[0][1])}"]
    P = [pts[0]] + pts + [pts[-1]]
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d.append(f"C{f(c1[0])} {f(c1[1])} {f(c2[0])} {f(c2[1])} {f(p2[0])} {f(p2[1])}")
    return " ".join(d)

def resample(poly, n):
    seg = [math.dist(poly[i], poly[i + 1]) for i in range(len(poly) - 1)]
    total = sum(seg); out = []
    for k in range(n + 1):
        t = total * k / n; i = 0
        while i < len(seg) - 1 and t > seg[i]:
            t -= seg[i]; i += 1
        a, b = poly[i], poly[i + 1]; u = t / seg[i] if seg[i] else 0
        out.append((a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u))
    return out

def wobble(poly, amp, seed, n=None, freq=1.6):
    """Hand tremor: low-frequency perpendicular drift, not noise."""
    rnd = random.Random(seed)
    pts = resample(poly, n or max(6, int(sum(math.dist(poly[i], poly[i + 1]) for i in range(len(poly) - 1)) / 40)))
    ph1, ph2 = rnd.uniform(0, 6.28), rnd.uniform(0, 6.28)
    out = []
    for k, (x, y) in enumerate(pts):
        a = pts[min(k + 1, len(pts) - 1)]; b = pts[max(k - 1, 0)]
        dx, dy = a[0] - b[0], a[1] - b[1]; L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        t = k / (len(pts) - 1)
        off = amp * (math.sin(t * freq * 6.28 + ph1) * .7 + math.sin(t * freq * 2.3 * 6.28 + ph2) * .3)
        out.append((x + nx * off, y + ny * off))
    return out

def head(tip, from_pt, L=30, ang=28):
    a = math.atan2(tip[1] - from_pt[1], tip[0] - from_pt[0]); r = math.radians(ang)
    p1 = (tip[0] - L * math.cos(a - r), tip[1] - L * math.sin(a - r))
    p2 = (tip[0] - L * math.cos(a + r), tip[1] - L * math.sin(a + r))
    return f"M{f(p1[0])} {f(p1[1])} L{f(tip[0])} {f(tip[1])} L{f(p2[0])} {f(p2[1])}"

def bez_pt(p0, c1, c2, p1, t):
    u = 1 - t
    return tuple(u**3 * p0[i] + 3 * u * u * t * c1[i] + 3 * u * t * t * c2[i] + t**3 * p1[i] for i in range(2))

# ------------------------------------------------------------------ svg writer
def stroke(var="--accent", fb="#D7262E", mult=1.0, extra=""):
    w = "var(--stroke-w,5)" if mult == 1 else f"calc(var(--stroke-w,5) * {mult})"
    return f"stroke:var({var},{fb});stroke-width:{w};{extra}"

def P(d, var="--accent", fb="#D7262E", mult=1.0, i=0, cls="draw", extra="", attrs=""):
    style = stroke(var, fb, mult, extra) + (f"--i:{i};" if i else "")
    return f'<path class="{cls}" pathLength="1" d="{d}" style="{style}"{attrs}/>'

def svg(id_, vb, body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" class="kel kel-{id_}" viewBox="{vb}" '
            f'fill="none" stroke-linecap="round" stroke-linejoin="round" role="img" aria-label="{title}">\n'
            f'  <!-- {title}. Arivihan element kit, original. Colours: CSS vars with fallbacks. -->\n  '
            + "\n  ".join(body) + "\n</svg>\n")

ELEMENTS = []   # manifest rows for svg elements

def add(kind, id_, vb, body, title, anim="draw-on", vars_=("--accent", "--stroke-w"), suits=None, notes=""):
    sub = {"arrow": "arrows", "mark": "marks", "frame": "frames"}[kind]
    path = KIT / "svg" / sub / f"{id_}.svg"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg(id_, vb, body, title))
    ELEMENTS.append(dict(id=id_, file=f"kit/svg/{sub}/{id_}.svg", kind=kind, animatable=anim,
                         variables_used=list(vars_), suits_skins=suits or SKINS, title=title, notes=notes))

# ------------------------------------------------------------------ arrows
def arrows():
    add("arrow", "arrow-straight", "0 0 400 60",
        [P("M12 30 H384"), P(head((388, 30), (300, 30)), i=1)],
        "straight arrow", notes="Native size 400x60; scale by width.")
    # two bends: an S
    p0, c1, c2, p1 = (14, 168), (170, 168), (210, 34), (384, 34)
    add("arrow", "arrow-curved", "0 0 400 200",
        [P(f"M{p0[0]} {p0[1]} C{c1[0]} {c1[1]} {c2[0]} {c2[1]} {p1[0]} {p1[1]}"),
         P(head(p1, bez_pt(p0, c1, c2, p1, .93)), i=1)],
        "curved arrow, two bends")
    add("arrow", "arrow-elbow", "0 0 400 200",
        [P("M24 20 V150 Q24 172 46 172 H380"), P(head((384, 172), (300, 172)), i=1)],
        "elbow arrow")
    add("arrow", "arrow-double", "0 0 400 60",
        [P("M20 30 H380"), P(head((16, 30), (100, 30)), i=1), P(head((384, 30), (300, 30)), i=1)],
        "double-headed arrow", notes="Two-way relation, e.g. trade, exchange, equilibrium.")
    w = wobble([(14, 44), (386, 30)], 7, seed=11, n=9)
    add("arrow", "arrow-hand-wobbly", "0 0 400 80",
        [P(catmull(w)), P(head(w[-1], w[-3], L=34, ang=32), i=1)],
        "hand-drawn wobbly arrow")
    arc = [(20, 170), (90, 70), (210, 26), (330, 44), (382, 118)]
    w = wobble(resample(arc, 12), 4, seed=7, n=12)
    add("arrow", "arrow-hand-curved", "0 0 400 200",
        [P(catmull(w)), P(head(w[-1], w[-3], L=34, ang=34), i=1)],
        "hand-drawn curved arrow")
    add("arrow", "arrow-leader", "0 0 400 200",
        [f'<circle class="dot" cx="24" cy="176" r="11" style="fill:var(--accent,#D7262E);stroke:none"/>',
         P("M24 176 L170 40 H388")],
        "callout leader: dot + line", anim="draw-on",
        notes="Dot pops first (animate .dot scale), then the line draws to the label shelf.")
    add("arrow", "arrow-chain", "0 0 80 40",
        [P("M8 20 H66", mult=1.1), P(head((70, 20), (40, 20), L=16, ang=34), mult=1.1, i=1)],
        "chain arrow between chips", notes="Use between .k-pill chips: अशांति, पलायन, घनत्व कम.")
    add("arrow", "arrow-big-bold", "0 0 400 160",
        [P("M28 80 H318", mult=3.6, extra="stroke-linecap:butt;"),
         P("M262 22 L352 80 L262 138", mult=3.6, i=1, extra="stroke-linejoin:miter;stroke-linecap:butt;")],
        "big bold arrow", notes="Thick stroke, not a filled outline, so it still draws on.")
    add("arrow", "arrow-down", "0 0 80 260",
        [P("M40 14 V236"), P(head((40, 242), (40, 160)), i=1)],
        "down arrow", notes="Vertical steps: cause above, result below.")
    # loop / cycle: a 300 degree arc with head
    cx, cy, r = 150, 150, 112
    a0, a1 = math.radians(-60), math.radians(240)
    s = (cx + r * math.cos(a0), cy + r * math.sin(a0)); e = (cx + r * math.cos(a1), cy + r * math.sin(a1))
    tip_from = (cx + r * math.cos(a1 - .25), cy + r * math.sin(a1 - .25))
    add("arrow", "arrow-cycle", "0 0 300 300",
        [P(f"M{f(s[0])} {f(s[1])} A{r} {r} 0 1 1 {f(e[0])} {f(e[1])}"), P(head(e, tip_from, L=28, ang=30), i=1)],
        "loop / cycle arrow", notes="Single loop. Put the cycle's name in the middle as HTML.")
    # three-stage cycle: three arcs, each with a head
    body = []
    for k in range(3):
        b0 = math.radians(-90 + k * 120 + 16); b1 = math.radians(-90 + (k + 1) * 120 - 16)
        s = (cx + r * math.cos(b0), cy + r * math.sin(b0)); e = (cx + r * math.cos(b1), cy + r * math.sin(b1))
        tf = (cx + r * math.cos(b1 - .22), cy + r * math.sin(b1 - .22))
        body += [P(f"M{f(s[0])} {f(s[1])} A{r} {r} 0 0 1 {f(e[0])} {f(e[1])}", i=2 * k),
                 P(head(e, tf, L=24, ang=30), i=2 * k + 1)]
    add("arrow", "arrow-cycle-3", "0 0 300 300", body,
        "three-stage cycle arrows",
        notes="Biology/chemistry cycles: place three stage labels at 12, 4 and 8 o'clock as HTML.")

# ------------------------------------------------------------------ marks
def marks():
    A, A2 = ("--accent", "#D7262E"), ("--accent-2", "#1F3A8A")
    add("mark", "underline-straight", "0 0 400 20", [P("M6 10 H394")], "straight underline")
    w1 = wobble([(8, 22), (392, 14)], 2.5, seed=3, n=8); w2 = wobble([(40, 28), (360, 22)], 2, seed=4, n=7)
    add("mark", "underline-brush", "0 0 400 40",
        [P(catmull(w1), mult=2.4), P(catmull(w2), mult=1.4, i=1, extra="opacity:.85;")],
        "brush underline", notes="Two overlapping strokes give the dry-brush edge; both draw on.")
    wav = [(6 + k * 4, 14 + 9 * math.sin(k * 4 / 40 * 6.283)) for k in range(98)]
    add("mark", "underline-wavy", "0 0 400 30", [P(catmull(wav[::2]))], "wavy underline")
    add("mark", "underline-double", "0 0 400 30", [P("M6 8 H394"), P("M26 22 H374", i=1)], "double underline")
    w = wobble([(8, 20), (300, 14), (392, 8)], 3, seed=21, n=9)
    flick = [(392, 8), (330, 22), (250, 26)]
    add("mark", "underline-hand", "0 0 400 34",
        [P(catmull(w)), P(catmull(flick), i=1, mult=.8)],
        "hand-drawn underline with return flick")
    # loose oval scribble: overshoots its start
    rnd = random.Random(5); pts = []
    for k in range(0, 27):
        t = -0.35 + k * (2 * math.pi + .8) / 26
        rr = 1 + rnd.uniform(-.035, .035) + .04 * (k / 26)
        pts.append((200 + 186 * rr * math.cos(t), 100 + 82 * rr * math.sin(t) - 6 * math.cos(t)))
    add("mark", "circle-scribble", "0 0 400 200", [P(catmull(pts))], "loose oval scribble",
        notes="Size the svg ~20% larger than the word it rings.")
    sides = [[(14, 18), (392, 12)], [(386, 6), (392, 192)], [(398, 186), (10, 190)], [(16, 198), (8, 10)]]
    body = [P(catmull(wobble(s_, 3, seed=40 + k, n=6)), i=k) for k, s_ in enumerate(sides)]
    add("mark", "box-hand", "0 0 400 200", body, "hand-drawn box",
        notes="Corners overshoot like a pen box; four strokes draw on in order.")
    add("mark", "highlight-swipe", "0 0 400 60",
        [P(catmull(wobble([(14, 32), (386, 28)], 2, seed=9, n=6)), var="--highlight", fb="rgba(255,214,0,.55)",
           mult=8, extra="stroke-linecap:square;")],
        "highlighter swipe", vars_=("--highlight", "--stroke-w"),
        notes="Goes BEHIND the words: wrap words in .k-mark-host, give the svg class k-under.")
    add("mark", "strike-through", "0 0 400 40",
        [P(catmull(wobble([(6, 24), (394, 16)], 2.5, seed=13, n=6)))], "strike-through")
    add("mark", "cross-out-x", "0 0 200 200",
        [P(catmull(wobble([(22, 26), (178, 176)], 4, seed=15, n=5))),
         P(catmull(wobble([(176, 22), (26, 180)], 4, seed=16, n=5)), i=1)], "cross-out X")
    add("mark", "check-clean", "0 0 120 100", [P("M12 54 L44 86 L108 14", var="--accent-2", fb="#1F3A8A", mult=1.4)], "clean checkmark",
        vars_=("--accent-2", "--stroke-w"))
    hc = [(10, 52), (26, 62), (44, 88), (70, 46), (110, 8)]
    add("mark", "check-hand", "0 0 120 100", [P(catmull(wobble(hc, 2, seed=17, n=8)), mult=1.4)],
        "hand-drawn checkmark")
    add("mark", "bracket-vertical", "0 0 60 400", [P("M48 8 H14 V392 H48")], "vertical square bracket",
        notes="Mirror with transform: scaleX(-1) for the right side.")
    add("mark", "brace-vertical", "0 0 70 400",
        [P("M58 8 C26 8 34 30 34 60 V160 C34 186 26 200 10 200 C26 200 34 214 34 240 V340 C34 370 26 392 58 392")],
        "vertical curly brace", notes="Groups list rows into one idea; point at the label on the left.")
    add("mark", "brace-horizontal", "0 0 400 70",
        [P("M8 12 C8 44 30 36 60 36 H160 C186 36 200 44 200 60 C200 44 214 36 240 36 H340 C370 36 392 44 392 12")],
        "horizontal curly brace", notes="Under a row of chips: 'these together = ...'.")
    add("mark", "bracket-horizontal", "0 0 400 50", [P("M8 8 V40 H392 V8")], "horizontal square bracket")
    # attention burst: short radial lines only
    body = []
    for k in range(8):
        a = math.radians(-90 + k * 45); r0, r1 = 52, 84 if k % 2 == 0 else 72
        body.append(P(f"M{f(100 + r0 * math.cos(a))} {f(100 + r0 * math.sin(a))} L{f(100 + r1 * math.cos(a))} {f(100 + r1 * math.sin(a))}", i=k % 2))
    add("mark", "attention-burst", "0 0 200 200", body, "attention lines",
        notes="Plain radial strokes around a word or number. Not a sparkle: use it only where the eye must go.")
    add("mark", "dotted-connector", "0 0 400 20",
        ['<path class="wipe" d="M8 10 H392" style="stroke:var(--muted,#8a8a8a);stroke-width:calc(var(--stroke-w,5) * 1.3);stroke-dasharray:0 16;clip-path:inset(0 0 0 0);transform-box:fill-box"/>'],
        "dotted connector", anim="draw-on", vars_=("--muted", "--stroke-w"),
        notes="Dotted, so it reveals with the .wipe clip animation, not dashoffset.")

# ------------------------------------------------------------------ HUD frames
def frames():
    # spotlight ring with corner ticks
    body = [f'<circle class="draw" pathLength="1" cx="150" cy="150" r="96" style="{stroke("--accent","#F5B82E")}"/>',
            f'<circle class="draw" pathLength="1" cx="150" cy="150" r="112" style="{stroke("--accent-2","#4FD1E8",.5)}--i:1;opacity:.7"/>']
    for k, (x, y, sx, sy) in enumerate([(22, 22, 1, 1), (278, 22, -1, 1), (22, 278, 1, -1), (278, 278, -1, -1)]):
        body.append(P(f"M{x} {y + 30 * sy} V{y} H{x + 30 * sx}", "--accent", "#F5B82E", i=2))
    for a in (0, 90, 180, 270):
        r = math.radians(a)
        body.append(P(f"M{f(150 + 118 * math.cos(r))} {f(150 + 118 * math.sin(r))} L{f(150 + 134 * math.cos(r))} {f(150 + 134 * math.sin(r))}", "--accent-2", "#4FD1E8", i=3))
    add("frame", "spotlight-ring-hud", "0 0 300 300", body, "HUD spotlight ring with corner ticks",
        vars_=("--accent", "--accent-2", "--stroke-w"), suits=["night-hud", "pastel-notebook"],
        notes="Rings one place on a map or one part of a diagram. Corner ticks frame it like a viewfinder.")
    body = []
    T = 60
    for k, (x, y, sx, sy) in enumerate([(8, 8, 1, 1), (592, 8, -1, 1), (8, 392, 1, -1), (592, 392, -1, -1)]):
        body.append(P(f"M{x} {y + T * sy} V{y} H{x + T * sx}", "--accent", "#F5B82E", i=k))
    add("frame", "frame-corner-ticks-hud", "0 0 600 400", body, "HUD corner-tick frame",
        vars_=("--accent", "--stroke-w"), suits=["night-hud", "chalk-slate", "pastel-notebook"],
        notes="Fixed aspect 3:2. For any other aspect use the .k-hud card, whose ticks never stretch.")

# ------------------------------------------------------------------ own small icons (used inside cards)
ICON_PENCIL = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
               '<path class="draw" pathLength="1" d="M4 20 L5 15 L16 4 L20 8 L9 19 Z"/><path class="draw" pathLength="1" d="M13.5 6.5 L17.5 10.5"/>'
               '<path class="draw" pathLength="1" d="M4 20 L9 19"/></svg>')
ICON_WARN = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
             '<path class="draw" pathLength="1" d="M12 3 L22 20.5 H2 Z"/><path class="draw" pathLength="1" d="M12 9.5 V14"/>'
             '<circle cx="12" cy="17.2" r="1.1" fill="currentColor" stroke="none"/></svg>')
ICON_CHECK = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">'
              '<path class="draw" pathLength="1" d="M4 13 L9.5 18.5 L20 6"/></svg>')
ICON_QUOTE = ('<svg viewBox="0 0 48 48" fill="currentColor"><path d="M6 40 V26 C6 14 12 8 22 6 L23 11 C17 13 14 17 14 22 H20 V40 Z"/>'
              '<path d="M28 40 V26 C28 14 34 8 44 6 L45 11 C39 13 36 17 36 22 H42 V40 Z"/></svg>')
ICON_PIN = ('<svg viewBox="0 0 70 92" fill="none"><path class="draw" pathLength="1" d="M35 88 C35 88 6 54 6 34 A29 29 0 1 1 64 34 C64 54 35 88 35 88 Z" '
            'style="stroke:currentColor;stroke-width:5;fill:currentColor;fill-opacity:.18"/>'
            '<circle cx="35" cy="34" r="11" style="fill:currentColor"/></svg>')
ICON_CHAIN = ('<svg class="k-arrow" viewBox="0 0 80 40" fill="none" stroke-linecap="round" stroke-linejoin="round">'
              '<path class="draw" pathLength="1" d="M8 20 H66" style="stroke:currentColor;stroke-width:5"/>'
              '<path class="draw" pathLength="1" d="M52 10 L70 20 L52 30" style="stroke:currentColor;stroke-width:5;--i:1"/></svg>')

def tabler(name):
    """Inline a Tabler outline icon (MIT) with its classes normalised for the kit."""
    s = (VENDOR / "tabler/icons/outline" / f"{name}.svg").read_text()
    s = re.sub(r"<!--.*?-->", "", s, flags=re.S).strip()
    s = re.sub(r'\s(width|height|class)="[^"]*"', "", s, count=3)
    s = s.replace("<path ", '<path class="draw" pathLength="1" ')
    s = re.sub(r'<path class="draw" pathLength="1" stroke="none" d="M0 0h24v24H0z" fill="none"\s*/>', "", s)
    return re.sub(r"\s+", " ", s)

def ic(svg_):
    return f'<span class="k-icon">{svg_}</span>'

# ------------------------------------------------------------------ cards
CARDS = []

def card(id_, title, html, anim, notes="", icons=None):
    path = KIT / "cards" / f"{id_}.html"
    path.write_text(f"<!-- {title}. Arivihan element kit. Needs cards.css + a skin class on an ancestor. -->\n{html.strip()}\n")
    CARDS.append(dict(id=id_, file=f"kit/cards/{id_}.html", kind="card", animatable=anim, title=title,
                      notes=notes, icons=icons or []))

def cards():
    card("pill", "pill / chip", """
<div style="display:flex;gap:16px;flex-wrap:wrap">
  <span class="k-pill">जनसंख्या घनत्व</span>
  <span class="k-pill k-pill--accent">पलायन</span>
  <span class="k-pill k-pill--outline">उपजाऊ मिट्टी</span>
</div>""", "pop")
    card("section-tag", "section tag", """
<div class="k-section-tag k-head"><span class="k-section-tag__num">1</span><span class="k-section-tag__text">भौगोलिक कारक</span></div>""",
         "slide", notes="The number is a digit, never a bullet.")
    card("number-badge", "number badge", """
<div style="display:flex;gap:18px"><span class="k-badge">1</span><span class="k-badge">2</span><span class="k-badge k-badge--accent">3</span><span class="k-badge k-badge--sm">4</span></div>""", "pop")
    card("definition-chip", "definition chip (= text)", """
<div class="k-def"><span class="k-def__term k-head">जनसंख्या घनत्व</span><span class="k-def__eq">=</span><span class="k-def__text">प्रति वर्ग किमी लोग</span></div>""",
         "slide", notes="The '=' is a Poppins glyph in its own box; no formula engine involved.")
    card("statement-card", "statement card with pencil (Answer की पहली line)", f"""
<div class="k-card k-statement">
  <div class="k-statement__label">{ic(ICON_PENCIL)}<span>Answer की पहली line</span></div>
  <div class="k-statement__text">जनसंख्या का वितरण भौगोलिक, आर्थिक और सामाजिक कारकों पर निर्भर करता है।</div>
</div>""", "slide")
    card("warning-card", "warning card", f"""
<div class="k-card k-warn">{ic(ICON_WARN)}<div class="k-warn__text"><b>इस example को</b> छोड़ना मत, 2 नंबर इसी के हैं।</div></div>""",
         "pop", notes="The warning triangle is an SVG: none of the repo fonts has a ⚠ glyph.")
    card("sticker-tape", "sticker with tape (tilted)", """
<div class="k-sticker"><div class="k-head" style="font-size:52px">याद रखो</div><div style="font-size:34px;color:var(--muted,#777)">गंगा का मैदान सबसे घना</div></div>""",
         "pop", notes="Tilt comes from --tilt in the skin.")
    card("stamp", "stamp (rubber-stamp border, tilted)", """
<div class="k-stamp k-head">4 नंबर पक्के</div>""", "pop", notes="Animate with .is-stamping: lands from 1.8x.")
    card("quote-card", "quote card", f"""
<div class="k-card k-quote"><div class="k-quote__mark">{ICON_QUOTE}</div>
  <div class="k-quote__text">स्वराज मेरा जन्मसिद्ध अधिकार है और मैं इसे लेकर रहूँगा।</div>
  <div class="k-quote__by">बाल गंगाधर तिलक, 1916</div></div>""", "slide")
    card("checklist-row", "checklist row (number + text + check)", f"""
<div style="display:flex;flex-direction:column;gap:14px">
  <div class="k-card k-check-row is-done"><span class="k-badge k-badge--sm">1</span><span class="k-check-row__text">परिभाषा लिखी</span><span class="k-check-row__tick">{ICON_CHECK}</span></div>
  <div class="k-card k-check-row is-done"><span class="k-badge k-badge--sm">2</span><span class="k-check-row__text">चार कारक गिनाए</span><span class="k-check-row__tick">{ICON_CHECK}</span></div>
  <div class="k-card k-check-row"><span class="k-badge k-badge--sm">3</span><span class="k-check-row__text">भारत का उदाहरण</span><span class="k-check-row__tick">{ICON_CHECK}</span></div>
</div>""", "slide", notes="Add .is-done to light the row and draw its tick (tick paths have class draw).")
    card("list-row-thumb", "numbered list row with thumbnail slot", f"""
<div style="display:flex;flex-direction:column;gap:14px">
  <div class="k-card k-list-row"><span class="k-badge">1</span><span class="k-list-row__thumb">{ic(tabler('droplet'))}</span><span class="k-list-row__text k-head">जल की उपलब्धता</span></div>
  <div class="k-card k-list-row is-quiet"><span class="k-badge">2</span><span class="k-list-row__thumb">{ic(tabler('mountain'))}</span><span class="k-list-row__text k-head">भू आकृति</span></div>
</div>""", "slide", notes="Counted lists FILL IN: spoken row bright, the rest .is-quiet. Thumb takes an icon or a photo.",
         icons=["tabler:droplet", "tabler:mountain"])
    card("empty-slot", "empty slot (dotted) and filled", """
<div style="display:flex;flex-direction:column;gap:14px">
  <div class="k-slot is-filled"><span class="k-slot__num">1</span><span>जलवायु</span></div>
  <div class="k-slot"><span class="k-slot__num">2</span><span></span></div>
</div>""", "pop", notes="Toggle .is-filled when the item is spoken.")
    card("icon-tile", "icon tile (empty + filled)", f"""
<div style="display:flex;gap:28px">
  <div><span class="k-tile">{ic(tabler('droplet'))}</span><span class="k-tile-cap">पीना</span></div>
  <div><span class="k-tile is-filled">{ic(tabler('bath'))}</span><span class="k-tile-cap">नहाना</span></div>
  <div><span class="k-tile is-filled">{ic(tabler('chef-hat'))}</span><span class="k-tile-cap">खाना</span></div>
  <div><span class="k-tile">{ic(tabler('plant-2'))}</span><span class="k-tile-cap">खेती</span></div>
</div>""", "pop", icons=["tabler:droplet", "tabler:bath", "tabler:chef-hat", "tabler:plant-2"],
         notes="Tile lights up (.is-filled) as each use is named.")
    card("quadrant-recap", "quadrant recap panel", f"""
<div class="k-quad">
  <div class="k-card k-quad__cell"><div class="k-quad__top"><span class="k-badge k-badge--sm">1</span>{ic(tabler('mountain'))}</div><div class="k-quad__title k-head">भौगोलिक</div><div class="k-quad__note">जल, भू आकृति, जलवायु</div></div>
  <div class="k-card k-quad__cell"><div class="k-quad__top"><span class="k-badge k-badge--sm">2</span>{ic(tabler('building-factory-2'))}</div><div class="k-quad__title k-head">आर्थिक</div><div class="k-quad__note">खनिज, उद्योग</div></div>
  <div class="k-card k-quad__cell"><div class="k-quad__top"><span class="k-badge k-badge--sm">3</span>{ic(tabler('users-group'))}</div><div class="k-quad__title k-head">सामाजिक</div><div class="k-quad__note">धर्म, संस्कृति</div></div>
  <div class="k-card k-quad__cell"><div class="k-quad__top"><span class="k-badge k-badge--sm">4</span>{ic(tabler('building-bank'))}</div><div class="k-quad__title k-head">राजनीतिक</div><div class="k-quad__note">अशांति, नीति</div></div>
</div>""", "pop", icons=["tabler:mountain", "tabler:building-factory-2", "tabler:users-group", "tabler:building-bank"])
    card("timeline", "timeline: axis + nodes + years + progress dots", """
<div class="k-timeline">
  <div class="k-timeline__axis">
    <div class="k-timeline__line"></div>
    <div class="k-timeline__node is-done" style="left:13%"><div class="k-timeline__year">1857</div><div class="k-timeline__dot"></div><div class="k-timeline__label">पहला संग्राम</div></div>
    <div class="k-timeline__node is-done" style="left:38%"><div class="k-timeline__year">1905</div><div class="k-timeline__dot"></div><div class="k-timeline__label">बंग भंग</div></div>
    <div class="k-timeline__node is-done is-now" style="left:63%"><div class="k-timeline__year">1920</div><div class="k-timeline__dot"></div><div class="k-timeline__label">असहयोग</div></div>
    <div class="k-timeline__node" style="left:87%"><div class="k-timeline__year">1942</div><div class="k-timeline__dot"></div><div class="k-timeline__label">भारत छोड़ो</div></div>
  </div>
</div>""", "draw-on", notes="Axis is a dotted border: reveal it with a clip wipe; nodes pop in order.")
    card("progress-dots", "progress dots row", """
<div class="k-dots"><i class="on"></i><i class="on"></i><i class="now"></i><i></i><i></i></div>""", "pop")
    card("counter", "counter 2/4", """
<div class="k-counter"><div class="k-counter__num"><b>2</b><span class="sep">/</span><span>4</span></div><div class="k-counter__label">कारक हो गए</div></div>""",
         "pop", notes="Animate the first digit only (count up), the total stays.")
    card("torn-strip", "torn-paper caption strip", """
<div class="k-torn k-head">अशांति से पलायन होता है, इसलिए घनत्व कम</div>""", "slide")
    card("hud-panel", "HUD panel with corner ticks", """
<div class="k-hud"><div class="k-hud__kicker">भारत, 2011</div><div class="k-hud__title k-head">382 लोग प्रति वर्ग किमी</div>
  <div class="k-hud__text">बिहार सबसे घना, अरुणाचल सबसे विरल।</div></div>""", "draw-on",
         notes="Ticks are background gradients sized by --tick; they never stretch with the panel.")
    card("map-pin-label", "map pin label", f"""
<div class="k-pin"><span class="k-pin__mark">{ICON_PIN}</span><span class="k-pin__label k-head">गंगा का मैदान<small>सबसे घना क्षेत्र</small></span></div>""", "pop")
    card("arrow-chain", "chain of chips with arrows", f"""
<div class="k-chain"><span class="k-pill">अशांति</span>{ICON_CHAIN}<span class="k-pill">पलायन</span>{ICON_CHAIN}<span class="k-pill">जनसंख्या घनत्व कम</span></div>""",
         "draw-on", notes="Chips pop, arrows draw between them. Text arrow glyphs (→) are NOT in any repo font: always use the SVG.")
    card("callout", "labelled callout with leader line", """
<div class="k-callout">
  <svg viewBox="0 0 600 260" fill="none" stroke-linecap="round" stroke-linejoin="round">
    <circle cx="40" cy="226" r="13" style="fill:currentColor"/>
    <path class="draw" pathLength="1" d="M40 226 L220 60 H590" style="stroke:currentColor;stroke-width:var(--stroke-w,5)"/>
  </svg>
  <div class="k-callout__label k-head">केन्द्रक<small>कोशिका का नियंत्रण केंद्र</small></div>
</div>""", "draw-on", notes="Dot sits on the thing; label rides the shelf. Move by editing the path's middle point.")

# ------------------------------------------------------------------ preview
DEMO_WORD = "जनसंख्या घनत्व"

def inline(rel):
    s = (ROOT / rel).read_text()
    return re.sub(r"<!--.*?-->\s*", "", s, flags=re.S)

def preview():
    css_skins = "\n".join(f'<link rel="stylesheet" href="skins/{s}.css">' for s in SKINS)
    cells = []
    for kind, head_ in (("arrow", "Arrows"), ("mark", "Markings"), ("frame", "HUD frames")):
        items = [e for e in ELEMENTS if e["kind"] == kind]
        g = []
        for e in items:
            g.append(f'<figure class="cell"><div class="art">{inline(e["file"])}</div><figcaption>{e["id"]}</figcaption></figure>')
        cells.append(f'<h2 class="sec">{head_} <span>{len(items)}</span></h2><div class="grid">{"".join(g)}</div>')
    # marks in use, on Hindi words
    used = f"""
<h2 class="sec">Marks on Hindi words</h2>
<div class="inuse">
  <div class="word"><span class="k-mark-host k-head">{DEMO_WORD}<span class="k-over" style="left:0;right:0;bottom:-22px;height:30px">{inline('kit/svg/marks/underline-hand.svg')}</span></span></div>
  <div class="word"><span class="k-mark-host k-head">पलायन<span class="k-over" style="left:-18%;right:-18%;top:-26%;bottom:-30%">{inline('kit/svg/marks/circle-scribble.svg').replace('viewBox=', 'preserveAspectRatio="none" viewBox=')}</span></span></div>
  <div class="word"><span class="k-mark-host k-head"><span class="k-under" style="top:22%;height:70%">{inline('kit/svg/marks/highlight-swipe.svg').replace('viewBox=', 'preserveAspectRatio="none" viewBox=')}</span>उपजाऊ मिट्टी</span></div>
  <div class="word"><span class="k-mark-host k-head" style="color:var(--muted)">घनी आबादी<span class="k-over" style="left:-3%;right:-3%;top:38%;height:30px">{inline('kit/svg/marks/strike-through.svg').replace('viewBox=', 'preserveAspectRatio="none" viewBox=')}</span></span></div>
</div>"""
    card_html = "".join(
        f'<section class="card-demo"><div class="cap">{c["id"]}</div><div class="demo">{inline(c["file"])}</div></section>' for c in CARDS)
    font_test = ('<h2 class="sec">Devanagari shaping check</h2><div class="fonttest">'
                 + "".join(f'<div style="font-family:{fam};font-weight:{wt};{extra}"><span class="fn">{lab}</span>विद्युत् नियम क्षेत्रफल श्रृंखला द्वितीय राष्ट्रीय कृषि</div>'
                           for lab, fam, wt, extra in [
                               ("Khand 600", "Khand", 600, ""), ("Noto 900 / 62.5%", "'Noto Sans Devanagari'", 900, "font-stretch:62.5%"),
                               ("Noto 500", "'Noto Sans Devanagari'", 500, ""), ("Poppins 600", "Poppins", 600, ""), ("Kalam", "Kalam", 400, "")])
                 + "</div>")
    html = f"""<!doctype html>
<html lang="hi"><head><meta charset="utf-8"><meta name="viewport" content="width=1080">
<title>Element Kit Preview</title>
<link rel="stylesheet" href="fonts.css">
{css_skins}
<link rel="stylesheet" href="kit.css">
<link rel="stylesheet" href="cards/cards.css">
<style>
  html, body {{ margin: 0; }}
  body {{ width: 1080px; background: var(--bg, var(--paper)); color: var(--ink); font-family: var(--font-body); }}
  .page {{ padding: 56px 60px 80px; }}
  .title {{ font-family: var(--font-head); font-weight: var(--head-weight); font-stretch: var(--head-stretch); font-size: 84px; line-height: 1.15; margin: 0; }}
  .sub {{ font-family: Poppins, sans-serif; font-size: 26px; color: var(--muted); margin: 6px 0 30px; }}
  .swatches {{ display: flex; gap: 14px; margin-bottom: 20px; }}
  .swatches div {{ width: 120px; font: 500 20px Poppins, sans-serif; color: var(--muted); }}
  .swatches i {{ display: block; height: 56px; border-radius: 8px; margin-bottom: 6px; border: 1px solid rgba(128,128,128,.4); }}
  .sec {{ font: 600 30px Poppins, sans-serif; color: var(--muted); letter-spacing: .06em; text-transform: uppercase;
          margin: 54px 0 22px; padding-bottom: 10px; border-bottom: 2px solid color-mix(in srgb, var(--muted) 40%, transparent); }}
  .sec span {{ font-weight: 400; }}
  .grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 22px; }}
  .cell {{ margin: 0; padding: 18px; border-radius: 12px; background: color-mix(in srgb, var(--ink) 4%, transparent); }}
  .cell .art {{ height: 150px; display: grid; place-items: center; }}
  .cell .art svg {{ max-width: 100%; max-height: 150px; width: 260px; height: 150px; }}
  .cell figcaption {{ font: 500 20px Poppins, sans-serif; color: var(--muted); text-align: center; margin-top: 8px; }}
  .inuse {{ display: grid; grid-template-columns: 1fr 1fr; gap: 54px 30px; padding: 20px 10px; }}
  .word {{ font-size: 64px; text-align: center; }}
  .word .k-over svg, .word .k-under svg {{ width: 100%; height: 100%; }}
  .card-demo {{ margin: 0 0 40px; }}
  .card-demo .cap {{ font: 500 20px Poppins, sans-serif; color: var(--muted); margin-bottom: 14px; }}
  .card-demo .demo {{ padding: 26px 8px 4px; }}
  .fonttest div {{ font-size: 34px; line-height: 1.7; white-space: nowrap; }}
  .fonttest .fn {{ display: inline-block; width: 230px; font: 500 20px Poppins, sans-serif; color: var(--muted); }}
  .photo-row {{ display: flex; gap: 20px; }}
  .photo-row .k-photo {{ width: 300px; height: 200px; }}
</style></head>
<body>
<div class="page">
  <h1 class="title" id="skinname">skin</h1>
  <div class="sub">Arivihan element kit preview. Every element below takes its colour from the skin.</div>
  <div class="swatches">
    <div><i style="background:var(--paper)"></i>--paper</div><div><i style="background:var(--ink)"></i>--ink</div>
    <div><i style="background:var(--accent)"></i>--accent</div><div><i style="background:var(--accent-2)"></i>--accent-2</div>
    <div><i style="background:var(--muted)"></i>--muted</div><div><i style="background:var(--highlight)"></i>--highlight</div>
  </div>
  <h2 class="sec">Photo treatment hint</h2>
  <div class="photo-row"><div class="k-photo"><img src="photo-sample.svg" alt=""></div><div class="sub" id="phototext" style="align-self:center"></div></div>
  {''.join(cells)}
  {used}
  <h2 class="sec">Cards <span>{len(CARDS)}</span></h2>
  {card_html}
  {font_test}
</div>
<script>
  const skin = new URLSearchParams(location.search).get('skin') || 'paper-editorial';
  document.body.className = 'skin-' + skin;
  document.getElementById('skinname').textContent = skin;
  document.getElementById('phototext').textContent =
    getComputedStyle(document.body).getPropertyValue('--photo-treatment').replace(/"/g, '').trim();
  document.fonts.ready.then(() => {{ window.READY = true; }});
</script>
</body></html>
"""
    (KIT / "preview.html").write_text(html)

# a stand-in landscape for the photo-treatment demo (original, flat shapes)
PHOTO = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 200">
<defs><linearGradient id="s" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#7EC8F0"/><stop offset="1" stop-color="#F8E2B0"/></linearGradient></defs>
<rect width="300" height="200" fill="url(#s)"/><circle cx="220" cy="60" r="26" fill="#FFD25A"/>
<path d="M0 140 L70 70 L120 120 L170 60 L250 140 L300 110 V200 H0 Z" fill="#5B7F4A"/>
<path d="M0 165 C80 150 160 185 300 160 V200 H0 Z" fill="#3E7CB1"/></svg>"""

# ------------------------------------------------------------------ manifest
def manifest():
    rows = []
    for e in ELEMENTS:
        rows.append(dict(id=e["id"], file=e["file"], kind=e["kind"], animatable=e["animatable"],
                         variables_used=e["variables_used"], suits_skins=e["suits_skins"],
                         source="Arivihan element kit (tools/build_kit.py)", licence="original (Arivihan)",
                         licence_url=None, credit_required=False, notes=f'{e["title"]}. {e["notes"]}'.strip()))
    card_vars = ["--ink", "--accent", "--accent-2", "--paper", "--muted", "--card-bg", "--card-border", "--radius",
                 "--shadow", "--font-head", "--font-body"]
    for c in CARDS:
        extra = f' Contains Tabler icons ({", ".join(c["icons"])}), MIT: keep vendor/tabler/LICENSE with any redistribution.' if c["icons"] else ""
        rows.append(dict(id=c["id"], file=c["file"], kind="card", animatable=c["animatable"],
                         variables_used=card_vars, suits_skins=SKINS,
                         source="Arivihan element kit (tools/build_kit.py) + kit/cards/cards.css",
                         licence="original (Arivihan)" + (" + MIT (Tabler icons inside)" if c["icons"] else ""),
                         licence_url="https://github.com/tabler/tabler-icons/blob/main/LICENSE" if c["icons"] else None,
                         credit_required=False, notes=f'{c["title"]}. {c["notes"]}{extra}'.strip()))
    for s in SKINS:
        rows.append(dict(id=f"skin-{s}", file=f"kit/skins/{s}.css", kind="skin", animatable="none",
                         variables_used=["--ink", "--accent", "--accent-2", "--paper", "--muted", "--stroke-w"],
                         suits_skins=[s], source="Arivihan element kit", licence="original (Arivihan)",
                         licence_url=None, credit_required=False,
                         notes="Scope class .skin-" + s + "; defines colours, fonts, card radius, shadow and photo-treatment hint."))
    # vendor sets
    def count(p): return len(list((ROOT / p).glob("*.svg")))
    vend = [
        ("tabler-outline", "vendor/tabler/icons/outline", "icon-set", "draw-on", "MIT", "https://github.com/tabler/tabler-icons/blob/main/LICENSE", "Tabler Icons 3.49.0, stroke 2 on 24 grid, stroke=currentColor."),
        ("tabler-filled", "vendor/tabler/icons/filled", "icon-set", "pop", "MIT", "https://github.com/tabler/tabler-icons/blob/main/LICENSE", "Tabler Icons 3.49.0 filled variants."),
        ("lucide", "vendor/lucide/icons", "icon-set", "draw-on", "ISC", "https://github.com/lucide-icons/lucide/blob/main/LICENSE", "lucide-static 1.53.0, stroked, currentColor."),
    ] + [(f"phosphor-{w}", f"vendor/phosphor/assets/{w}", "icon-set", "pop", "MIT", "https://github.com/phosphor-icons/core/blob/main/LICENSE",
          f"@phosphor-icons/core 2.1.1, {w} weight; filled outlines (cannot draw on). thin/light weights dropped: too fine at 1080 wide.")
         for w in ("regular", "bold", "fill", "duotone")] + [
        (f"excalidraw-{d}", f"vendor/excalidraw/{d}", "icon-set", "draw-on", "MIT", "https://github.com/excalidraw/excalidraw-libraries/blob/main/LICENSE",
         f"Converted from excalidraw-libraries ({src}) by tools/excalidraw_to_svg.py; text dropped, colours mapped to --ink/--accent.")
        for d, src in (("handdrawn-signs", "kwirke/some-handdrawn-signs"), ("stick-people", "dhtoran/stick-people"),
                       ("stick-figures", "youritjang/stick-figures"), ("stick-figures-collaboration", "gianpaima/stick-figures-collaboration"),
                       ("math-teacher", "ytrkptl/math-teacher-library"))]
    for id_, p, kind, anim, lic, url, note in vend:
        rows.append(dict(id=id_, file=p + "/", count=count(p), kind=kind, animatable=anim, variables_used=["currentColor"] if "excalidraw" not in id_ else ["--ink", "--accent", "--stroke-w"],
                         suits_skins=SKINS, source=note.split(",")[0], licence=lic, licence_url=url,
                         credit_required=False, notes=note + " MIT/ISC: no on-screen credit; keep the LICENSE file with the set."))
    for id_, p, url, note in (("rough-notation", "vendor/rough-notation/lib/rough-notation.iife.js", "https://github.com/rough-stuff/rough-notation/blob/master/LICENSE",
                               "rough-notation 0.5.1: runtime generator for sketchy underline/box/circle/highlight/strike/crossed-off/bracket annotations that animate on. Use in the renderer page when a mark must hug arbitrary text."),
                              ("roughjs", "vendor/roughjs/bundled/rough.js", "https://github.com/rough-stuff/rough/blob/master/LICENSE",
                               "roughjs 4.6.6: hand-drawn line/curve/ellipse generator to SVG paths.")):
        rows.append(dict(id=id_, file=p, kind="mark", animatable="draw-on", variables_used=[], suits_skins=["paper-editorial", "chalk-slate", "pastel-notebook"],
                         source=note.split(":")[0], licence="MIT", licence_url=url, credit_required=False, notes=note))
    rows.append(dict(id="icon-picks", file="vendor/icon_picks.json", kind="icon-set", animatable="draw-on", variables_used=["currentColor"],
                     suits_skins=SKINS, source="curated index", licence="index original; icons per their set", licence_url=None,
                     credit_required=False, notes="Concept -> icon (with Hindi gloss and alternates). Built by tools/build_icon_picks.py."))
    (ROOT / "manifest.json").write_text(json.dumps({"_about": "Every element, card, skin and vendor set in library/elements. Paths relative to library/elements/.",
                                                    "elements": rows}, ensure_ascii=False, indent=1))
    return rows

if __name__ == "__main__":
    for sub in ("arrows", "marks", "frames"):
        for p in (KIT / "svg" / sub).glob("*.svg"):
            p.unlink()
    for p in (KIT / "cards").glob("*.html"):
        p.unlink()
    arrows(); marks(); frames(); cards()
    (KIT / "photo-sample.svg").write_text(PHOTO)
    preview()
    rows = manifest()
    print(f"svg elements: {len(ELEMENTS)}  cards: {len(CARDS)}  manifest rows: {len(rows)}")
