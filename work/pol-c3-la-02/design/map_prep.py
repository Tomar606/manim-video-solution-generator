"""One-off: cut the map's window out of two Natural Earth downloads, then drop them.

    python3 -I work/pol-c3-la-02/design/map_prep.py work/pol-c3-la-02/assets/data

Expects in that folder (both public domain, naturalearthdata.com):
    SR_LR.zip                                  10m shaded relief, 16200x8100, 45 px/degree
    ne_10m_rivers_lake_centerlines.geojson     10m river centrelines
Writes relief_sr_<box>.png and rivers_<box>.geojson beside them and deletes the
originals (the disk is nearly full). map.mjs reads only the two small files.

NO country, admin or boundary layer is ever read here: rivers and relief only.
"""
import json, os, sys, zipfile
from PIL import Image

D = sys.argv[1]
LON0, LON1, LAT0, LAT1 = 72, 95, 19, 36          # the frame plus a margin
BOX = f"{LON0}-{LON1}E_{LAT0}-{LAT1}N"
PPD = 45                                          # SR_LR.tfw: 1/45 degree, edges at -180 / +90

# ---- relief: grayscale hillshade, cropped on whole pixels
zp = os.path.join(D, "SR_LR.zip")
with zipfile.ZipFile(zp) as z:
    tif = z.extract("SR_LR.tif", D)
Image.MAX_IMAGE_PIXELS = None
im = Image.open(tif)
assert im.size == (360 * PPD, 180 * PPD), im.size
crop = im.crop(((LON0 + 180) * PPD, (90 - LAT1) * PPD, (LON1 + 180) * PPD, (90 - LAT0) * PPD)).convert("L")
crop.save(os.path.join(D, f"relief_sr_{BOX}.png"), optimize=True)
im.close()
os.remove(tif)
os.remove(zp)

# ---- rivers: the runs of each centreline that fall inside the box
src = os.path.join(D, "ne_10m_rivers_lake_centerlines.geojson")
feats = []
for f in json.load(open(src, encoding="utf-8"))["features"]:
    g, p = f["geometry"], f["properties"]
    if not g:
        continue
    lines = [g["coordinates"]] if g["type"] == "LineString" else g["coordinates"]
    keep = []
    for ln in lines:
        run = []
        for x, y, *_ in ln:
            if LON0 <= x <= LON1 and LAT0 <= y <= LAT1:
                run.append([round(x, 4), round(y, 4)])
            else:
                if len(run) > 1:
                    keep.append(run)
                run = []
        if len(run) > 1:
            keep.append(run)
    if keep:
        feats.append({"type": "Feature",
                      "properties": {"name": p.get("name"), "scalerank": p.get("scalerank"), "cla": p.get("featurecla")},
                      "geometry": {"type": "MultiLineString", "coordinates": keep}})
json.dump({"type": "FeatureCollection", "features": feats},
          open(os.path.join(D, f"rivers_{BOX}.geojson"), "w", encoding="utf-8"),
          ensure_ascii=False, separators=(",", ":"))
os.remove(src)
print(crop.size, len(feats), "river features")
