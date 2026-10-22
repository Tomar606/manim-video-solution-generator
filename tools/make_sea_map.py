"""Coastline-only base map for the sea-route beats (land filled, NO political borders).

    python tools/make_sea_map.py                -> library/elements/maps/sea-route.json
    python tools/make_sea_map.py world-trade    -> library/elements/maps/world-trade.json (Rotterdam to Shanghai)

Mercator over the Atlantic-Africa-Indian Ocean window. The stage projects port
and route coordinates with the same parameters, so (lon, lat) is all a plan gives.
Coastlines only on purpose: a borderless map can never draw India's boundary wrong.
"""
import json, math, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
WINDOWS = {"sea-route": (-22.0, 118.0, -40.0, 47.0), "world-trade": (-12.0, 132.0, -12.0, 58.0),
           "subcontinent": (66.0, 92.5, 7.5, 36.5), "north-atlantic": (-84.0, 16.0, 24.0, 62.0)}
WIDTH = {"subcontinent": 760}
# rivers drawn on a window, by Natural Earth name (orientation only; still no borders)
RIVERS = {"subcontinent": {"Indus", "Ganges", "Ganga", "Yamuna", "Narmada", "Godavari", "Krishna", "Mahanadi", "Brahmaputra", "Son", "Chambal"}}
NAME = sys.argv[1] if len(sys.argv) > 1 else "sea-route"
LON0, LON1, LAT0, LAT1 = WINDOWS[NAME]; W = WIDTH.get(NAME, 960)
m = lambda la: math.log(math.tan(math.pi / 4 + math.radians(la) / 2))
Y0, Y1 = m(LAT1), m(LAT0)
H = round(W * (Y0 - Y1) / math.radians(LON1 - LON0))
def P(lon, lat):
    return ((lon - LON0) / (LON1 - LON0) * W, (Y0 - m(max(-80, min(80, lat)))) / (Y0 - Y1) * H)
gj = json.loads((ROOT / "library/elements/maps/ne_50m_land.geojson").read_text())
parts = []
for f in gj["features"]:
    g = f["geometry"]; polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
    for poly in polys:
        ring = poly[0]
        xs = [c[0] for c in ring]; ys = [c[1] for c in ring]
        if max(xs) < LON0 - 5 or min(xs) > LON1 + 5 or max(ys) < LAT0 - 5 or min(ys) > LAT1 + 5: continue
        pts, last = [], None
        for lon, lat in ring:
            x, y = P(lon, lat)
            if last and abs(x - last[0]) + abs(y - last[1]) < 1.6: continue
            pts.append((x, y)); last = (x, y)
        if len(pts) < 4: continue
        xs2 = [p[0] for p in pts]; ys2 = [p[1] for p in pts]
        if (max(xs2) - min(xs2)) * (max(ys2) - min(ys2)) < 6: continue
        parts.append("M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + "Z")
rivers = []
if NAME in RIVERS:
    rg = json.loads((ROOT / "library/elements/maps/ne_50m_rivers.geojson").read_text())
    for f in rg["features"]:
        if (f["properties"].get("name") or "") not in RIVERS[NAME]:
            continue
        g = f["geometry"]; lines = g["coordinates"] if g["type"] == "MultiLineString" else [g["coordinates"]]
        for ln in lines:
            pts = [P(lon, lat) for lon, lat in ln]
            rivers.append("M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in pts))
out = {"rivers": "".join(rivers), "w": W, "h": H, "lon0": LON0, "lon1": LON1, "lat0": LAT0, "lat1": LAT1, "land": "".join(parts)}
(ROOT / f"library/elements/maps/{NAME}.json").write_text(json.dumps(out))
print(W, H, len(parts), "polys", len(out["land"]) // 1024, "KB")
