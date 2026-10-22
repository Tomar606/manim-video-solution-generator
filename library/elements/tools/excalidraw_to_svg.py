"""Convert Excalidraw library items (MIT, excalidraw/excalidraw-libraries) into
standalone stroked SVGs that take the kit's colour variables.

Only geometry is converted: line, arrow, freedraw, ellipse, rectangle, diamond.
Text elements are dropped (screen text belongs in HTML, set in our fonts).
Every stroked shape carries pathLength="1" so it can draw on with dashoffset.

usage: python3 excalidraw_to_svg.py <lib.excalidrawlib> <out_dir> <prefix>
"""
import json, math, re, sys, pathlib

def slug(s):
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return s or "item"

def rot(px, py, cx, cy, a):
    if not a:
        return px, py
    c, s = math.cos(a), math.sin(a)
    dx, dy = px - cx, py - cy
    return cx + dx * c - dy * s, cy + dx * s + dy * c

def colour(c, var):
    if not c or c == "transparent":
        return None
    return f"var({var},{c})"

def convert(els):
    shapes, xs, ys = [], [], []
    for e in els:
        if e.get("isDeleted") or e["type"] == "text":
            continue
        x, y, w, h, a = e["x"], e["y"], e.get("width", 0), e.get("height", 0), e.get("angle", 0) or 0
        cx, cy = x + w / 2, y + h / 2
        sw = max(1.0, float(e.get("strokeWidth", 2)))
        stroke = colour(e.get("strokeColor"), "--ink") or "none"
        fill = colour(e.get("backgroundColor"), "--accent") or "none"
        dash = ' stroke-dasharray="0.02 0.015"' if e.get("strokeStyle") in ("dashed", "dotted") else ""
        t = e["type"]
        pts0 = e.get("points") or []
        closed = len(pts0) > 2 and math.dist(pts0[0], pts0[-1]) < 2
        if t in ("line", "arrow", "freedraw", "draw") and not closed:
            fill = "none"          # an open stroke never takes the shape fill
        # Excalidraw hachure / cross-hatch fills read as a light tint, not a solid
        fo = (1.0 if e.get("fillStyle") == "solid" else 0.25) * (e.get("opacity", 100) / 100)
        so = e.get("opacity", 100) / 100
        style = (f'style="stroke:{stroke};fill:{fill};fill-opacity:{fo:.2f};stroke-opacity:{so:.2f};'
                 f'stroke-width:calc(var(--stroke-w,4) * {sw/2:.2f})"')
        if t in ("line", "arrow", "freedraw", "draw"):
            pts = [rot(x + px, y + py, cx, cy, a) for px, py in e.get("points", [])]
            if len(pts) < 2:
                continue
            xs += [p[0] for p in pts]; ys += [p[1] for p in pts]
            d = "M" + " L".join(f"{px:.1f} {py:.1f}" for px, py in pts)
            shapes.append(f'<path class="draw" pathLength="1" d="{d}" {style}{dash}/>')
            if t == "arrow" and e.get("endArrowhead"):
                (x1, y1), (x2, y2) = pts[-2], pts[-1]
                ang = math.atan2(y2 - y1, x2 - x1); L = 6 + sw * 4
                p1 = (x2 - L * math.cos(ang - 0.5), y2 - L * math.sin(ang - 0.5))
                p2 = (x2 - L * math.cos(ang + 0.5), y2 - L * math.sin(ang + 0.5))
                shapes.append(f'<path class="draw head" pathLength="1" d="M{p1[0]:.1f} {p1[1]:.1f} L{x2:.1f} {y2:.1f} L{p2[0]:.1f} {p2[1]:.1f}" {style.replace("fill:"+fill, "fill:none")}/>')
        elif t == "ellipse":
            xs += [x, x + w]; ys += [y, y + h]
            tr = f' transform="rotate({math.degrees(a):.1f} {cx:.1f} {cy:.1f})"' if a else ""
            shapes.append(f'<ellipse class="draw" pathLength="1" cx="{cx:.1f}" cy="{cy:.1f}" rx="{w/2:.1f}" ry="{h/2:.1f}"{tr} {style}{dash}/>')
        elif t in ("rectangle", "diamond"):
            xs += [x, x + w]; ys += [y, y + h]
            tr = f' transform="rotate({math.degrees(a):.1f} {cx:.1f} {cy:.1f})"' if a else ""
            if t == "rectangle":
                r = min(w, h) * 0.12 if e.get("roundness") else 0
                shapes.append(f'<rect class="draw" pathLength="1" x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{r:.1f}"{tr} {style}{dash}/>')
            else:
                d = f"M{cx:.1f} {y:.1f} L{x+w:.1f} {cy:.1f} L{cx:.1f} {y+h:.1f} L{x:.1f} {cy:.1f} Z"
                shapes.append(f'<path class="draw" pathLength="1" d="{d}"{tr} {style}{dash}/>')
    if not shapes:
        return None
    pad = 8
    vx, vy = min(xs) - pad, min(ys) - pad
    vw, vh = max(xs) - min(xs) + 2 * pad, max(ys) - min(ys) + 2 * pad
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vx:.1f} {vy:.1f} {vw:.1f} {vh:.1f}" '
            f'fill="none" stroke-linecap="round" stroke-linejoin="round">\n  ' + "\n  ".join(shapes) + "\n</svg>\n")

def main(src, out, prefix):
    d = json.load(open(src))
    items = d.get("libraryItems") or d.get("library")
    out = pathlib.Path(out); out.mkdir(parents=True, exist_ok=True)
    seen, n = set(), 0
    for i, it in enumerate(items):
        els = it["elements"] if isinstance(it, dict) else it
        name = slug(it.get("name", "")) if isinstance(it, dict) and it.get("name") else f"{prefix}-{i+1:02d}"
        while name in seen:
            name += "-b"
        seen.add(name)
        svg = convert(els)
        if svg:
            (out / f"{name}.svg").write_text(svg); n += 1
    print(src, "->", n)

if __name__ == "__main__":
    main(*sys.argv[1:4])
