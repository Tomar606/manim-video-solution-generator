"""GEO-C7-SA-01 (उत्तरी अटलांटिक समुद्री मार्ग की तीन विशेषताएँ): signal look, one part.

    python lab/kit_test/make_geo_c7_01_plan.py  ->  plan_geo_c7_sa_01_p1.json

Sister of GEO-C7-SA-02 with a deliberately different skin.  A North Atlantic map
(coastlines only) shades the two industrial regions and draws the lane between
them; "एक-चौथाई" is a 100-dot grid with 25 lit; "ट्रंक = तना" is a real tree trunk.
r_* clips are reused from GEO-C8-SA-01, GEO-C7-SA-02 and HIS-C2-SA-08.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROJ = ROOT / "projects/geo-c7-sa-01"
L = json.loads((PROJ / "lines_part1.json").read_text())


def A(sec):
    i = max(k for k, l in enumerate(L) if l["start"] <= sec + 1e-6)
    return [i, round(sec - L[i]["start"], 2)]


LANE = [[-74.0, 40.6], [-69, 41], [-60, 42.5], [-45, 46], [-30, 49], [-15, 49.8], [-6, 49.6], [1.5, 50.6], [4.1, 51.95]]
NE_USA = [[-82, 41.5], [-80, 43], [-76, 44.5], [-71, 45.3], [-67, 45], [-67.5, 44], [-70, 43], [-70.5, 41.6], [-74, 40.3],
          [-75.5, 38.8], [-77, 38], [-80, 39]]
W_EUROPE = [[-10.5, 51.5], [-8, 55.5], [-5, 58.7], [-1.5, 58.6], [2, 53], [5, 53.6], [8.5, 55], [11.5, 54.2], [12.5, 50.5],
            [10.5, 47.5], [7, 45.7], [3, 43.2], [-1.8, 43.3], [-9.5, 43.2], [-9, 47.8], [-5, 48.3]]
OCEAN = [["अटलांटिक महासागर", [-38, 36], "pre", "sea"]]


def amap(slot, route=None, regions=(), ports=(), labels=OCEAN):
    return {"type": "seamap", "slot": slot, "map": "north-atlantic", "labels": list(labels),
            "routes": [route] if route else [], "regions": list(regions), "ports": list(ports)}


REG_US = lambda at, lab=None: {"pts": NE_USA, "at": at, "label": "उत्तर-पूर्वी अमेरिका", "label_xy": [-66, 49.5], "label_at": lab or at}
REG_EU = lambda at, lab=None: {"pts": W_EUROPE, "at": at, "label": "पश्चिमी यूरोप", "label_xy": [-1, 61.0], "label_at": lab or at}

beats = []
B = lambda **k: beats.append(k)
B(id="storm", **{"in": 0, "out": 4}, presenter="standard", broll={"clip": "a01", "region": "full"}, elements=[
    {"type": "note", "slot": "over-broll-top", "text": "पूरी दुनिया का समुद्री व्यापार…", "at": 1},
    {"type": "pill", "slot": "over-broll-low", "text": "हर चौथा हिस्सा: एक ही रास्ते से", "style": "accent", "at": A(6.0)}])
B(id="name-map", **{"in": 4, "out": 5}, presenter="standard", elements=[
    amap("upper", route={"pts": LANE, "at": 4, "ship": True, "dur": 2.6, "tag": "उत्तरी अटलांटिक समुद्री मार्ग", "tag_xy": [-37, 51.5], "tag_at": [4, 1.2]})])
B(id="question", **{"in": 5, "out": 8}, presenter="small", broll={"clip": "a06", "region": "full", "dim": True}, elements=[
    {"type": "qcard", "slot": "upper", "question": "उत्तरी अटलांटिक समुद्री मार्ग की कोई तीन विशेषताएँ लिखिए।",
     "year": "2025", "marks": "3 अंक", "t_marks": [7, 1.5], "at": 5}])
B(id="start", **{"in": 8, "out": 10}, presenter="standard", broll={"clip": "a10", "region": "full"}, elements=[
    {"type": "note", "slot": "over-broll-top", "text": "answer की शुरुआत में…", "at": 8}])
B(id="industrial", **{"in": 10, "out": 11}, presenter="standard", broll={"clip": "a03", "region": "full"}, elements=[
    {"type": "pill", "slot": "over-broll-low", "text": "औद्योगिक दृष्टि से विकसित दो प्रदेश", "style": "accent", "at": A(26.22)}])
B(id="two-regions", **{"in": 11, "out": 12}, presenter="standard", elements=[
    {"type": "headline", "slot": "head", "text": "दो विकसित प्रदेशों को मिलाता है", "size": "m", "at": 11},
    amap("upper", route={"pts": LANE, "at": A(34.5), "dur": 1.6}, regions=[REG_US(11), REG_EU(A(34.06))])])
B(id="harbour", **{"in": 12, "out": 14}, presenter="standard", broll={"clip": "a05", "region": "full"}, elements=[
    {"type": "pills", "slot": "over-broll-low", "style": "accent", "items": [["पत्तन", A(37.22)], ["पोताश्रय", A(38.04)]]},
    {"type": "def", "slot": "over-broll-top", "term": "पोताश्रय", "text": "जहाज़ों के सुरक्षित ठहरने की जगह", "at": 13}])
B(id="write-first", **{"in": 14, "out": 16}, presenter="standard", elements=[
    {"type": "stamp", "slot": "upper", "text": "पत्तन + पोताश्रय: शुरुआत में ही", "at": 14},
    {"type": "note", "slot": "under-upper", "text": "examiner यहीं से समझ जाता है", "at": 15}])
B(id="joins", **{"in": 16, "out": 19}, presenter="standard", elements=[
    {"type": "section", "slot": "head", "num": "1", "text": "जोड़ता है", "at": A(55.9)},
    amap("upper", route={"pts": LANE, "at": A(57.6), "ship": True, "dur": 4.2}, regions=[REG_US("pre"), REG_EU("pre")],
         ports=[["पूर्वी तट", "उत्तरी अमेरिका", [-74.0, 40.6], A(59.22), "s"], ["पश्चिमी तट", "यूरोप", [4.1, 51.95], A(61.16), "sw"]])])
B(id="quarter", **{"in": 19, "out": 22}, presenter="standard", elements=[
    {"type": "dots100", "slot": "upper", "label": "विश्व का समुद्री व्यापार", "states": [[25, "एक-चौथाई इसी मार्ग से", A(65.64)]]},
    {"type": "stamp", "slot": "under-upper", "text": "एक-चौथाई = answer की जान", "at": A(68.0)}])
B(id="crowded", **{"in": 22, "out": 24}, presenter="standard", broll={"clip": "a06", "region": "full"}, elements=[
    {"type": "note", "slot": "over-broll-top", "text": "इतना व्यापार, एक ही रास्ता…", "at": 22}])
B(id="busy", **{"in": 24, "out": 26}, presenter="standard", broll={"clip": "a02", "region": "full"}, elements=[
    {"type": "section", "slot": "over-broll-top", "num": "2", "text": "व्यस्त मार्ग", "at": [24, 1.2]}])
B(id="tonnes", **{"in": 26, "out": 28}, presenter="standard", broll={"clip": "r_v11", "region": "full"}, elements=[
    {"type": "pill", "slot": "over-broll-low", "text": "हर साल लाखों टन माल", "style": "accent", "at": A(88.2)}])
B(id="trade", **{"in": 28, "out": 30}, presenter="standard", broll={"clip": "a08", "region": "full"}, elements=[
    {"type": "section", "slot": "over-broll-top", "num": "3", "text": "अंतर्राष्ट्रीय व्यापार", "at": A(96.46)}])
B(id="exchange", **{"in": 30, "out": 32}, presenter="standard", broll={"clip": "a04", "region": "full"}, elements=[
    {"type": "note", "slot": "over-broll-top", "text": "अलग-अलग देशों के बीच", "at": 30},
    {"type": "pills", "slot": "over-broll-low", "style": "accent", "items": [["वस्तुएँ", A(104.44)], ["सेवाएँ", A(105.46)], ["आदान-प्रदान", A(106.16)]]}])
B(id="trunk-name", **{"in": 32, "out": 33}, presenter="standard", elements=[
    {"type": "headline", "slot": "head", "text": "पहचान वाला नाम", "size": "m", "at": 32},
    {"type": "stamp", "slot": "upper", "text": "वृहद ट्रंक मार्ग", "at": [32, 3.4]}])
B(id="trunk", **{"in": 33, "out": 35}, presenter="standard", broll={"clip": "a09", "region": "full"}, elements=[
    {"type": "def", "slot": "over-broll-top", "term": "ट्रंक", "text": "पेड़ का तना", "at": 33},
    {"type": "note", "slot": "over-broll-low", "text": "पूरा पेड़ तने पर टिका", "at": 34}])
B(id="trunk-map", **{"in": 35, "out": 37}, presenter="standard", elements=[
    {"type": "headline", "slot": "head", "text": "पूरा व्यापार इसी पर टिका", "size": "m", "at": 35},
    amap("upper", route={"pts": LANE, "at": 35, "dur": 1.4, "tag": "वृहद ट्रंक मार्ग", "tag_xy": [-37, 51.5], "tag_at": [35, 1.0]},
         regions=[REG_US("pre"), REG_EU("pre")])])
B(id="three-words", **{"in": 37, "out": 41}, presenter="hub", hub={"cy": 1000, "r": 200, "backdrop": "veo:a06@3"}, elements=[
    {"type": "headline", "slot": "head", "text": "तीन शब्द + दो ज़रूरी चीज़ें", "size": "m", "at": 37},
    {"type": "radial", "slot": "around-hub", "radius": 330, "cumulative": True, "items": [
        ["tabler:link", "जोड़ता है", 37], ["tabler:ship", "व्यस्त है", 37], ["tabler:world", "व्यापार कराता है", 37]],
     "recount": [A(127.76), A(128.66), A(129.74)]},
    {"type": "pill", "slot": "center-low", "text": "एक-चौथाई + वृहद ट्रंक मार्ग", "style": "accent", "at": A(133.46)}])
B(id="marks", **{"in": 41, "out": 42}, presenter="standard", broll={"clip": "r_v12", "region": "full", "dim": True}, elements=[
    {"type": "stamp", "slot": "over-broll", "text": "पूरे 3 नंबर पक्के", "at": A(139.0)}])
B(id="notes", **{"in": 42, "out": 43}, presenter="hero", broll={"clip": "r_d16", "region": "full", "dim": True}, elements=[
    {"type": "pill", "slot": "head", "text": "exact answer: Notes button", "style": "accent", "at": 42}])
B(id="outro", **{"in": 43, "out": "end"}, presenter="hero", broll={"clip": "r_m12", "region": "full", "dim": True}, elements=[
    {"type": "note", "slot": "over-broll-top", "text": "जहाज़ों की तरह, पढ़ाई भी रोज़", "at": 44}])

plan = {"_about": "GEO-C7-SA-01, signal look", "project": "geo-c7-sa-01", "part": 1, "captions_from": 8,
        "skin": "paper-editorial", "theme": "signal", "presenter_style": "card", "plate": "atlantic-portland-light",
        "spine": {"title": "उत्तरी अटलांटिक समुद्री मार्ग", "items": ["जोड़ता है", "व्यस्त मार्ग", "अंतर्राष्ट्रीय व्यापार"],
                  "lit_at": [16, 24, 28], "show_from": 8},
        "beats": beats}
(ROOT / "lab/kit_test/plan_geo_c7_sa_01_p1.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1))
shots = {"a01": "container ship in a North Atlantic storm", "a02": "New York harbour container terminal", "a03": "industrial river valley, NE USA",
         "a04": "Rhine barges past factories", "a05": "sheltered harbour behind a breakwater", "a06": "busy shipping lane, aerial",
         "a08": "cars rolling onto a ro-ro ship", "a09": "giant tree trunk, tilt up", "a10": "Atlantic lighthouse, ship passing",
         "r_d03": "vast busy seaport (GEO-C8)", "r_d14": "European port at dusk (GEO-C8)", "r_d16": "port at night (GEO-C8)",
         "r_v11": "ship's bow (GEO-C7-SA-02)", "r_v12": "container ship at sunset (GEO-C7-SA-02)", "r_m12": "student studying (HIS-C2-SA-08)"}
(PROJ / "veo/shots.json").write_text(json.dumps(shots, indent=1))
print(len(beats), "beats")
