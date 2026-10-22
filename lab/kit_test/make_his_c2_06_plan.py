"""HIS-C2-SA-06 (मौर्य साम्राज्य के पाँच प्रमुख राजनीतिक केंद्र): edict theme over a map, one part.

    python lab/kit_test/make_his_c2_06_plan.py  ->  plan_his_c2_sa_06_p1.json

The map is the spine of this answer: a coastline-and-rivers survey of the
subcontinent with NO political borders (tools/make_sea_map.py subcontinent), on
which the five centres are pinned as they are named.  Cues in seconds -> [line, offset].
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROJ = ROOT / "projects/his-c2-sa-06"
L = json.loads((PROJ / "lines_part1.json").read_text())


def A(sec):
    i = max(k for k, l in enumerate(L) if l["start"] <= sec + 1e-6)
    return [i, round(sec - L[i]["start"], 2)]


PAT, TAX, UJJ, TOS, SUV = [85.14, 25.61], [72.83, 33.75], [75.78, 23.18], [85.84, 20.19], [76.42, 15.82]
CENTRES = [("पाटलिपुत्र", "राजधानी · आज पटना", PAT, "s"), ("तक्षशिला", "आज पाकिस्तान में", TAX, "e"),
           ("उज्जयिनी", "आज उज्जैन, म.प्र.", UJJ, "s"), ("तोसलि", "ओडिशा · कलिंग", TOS, "s"),
           ("सुवर्णगिरि", "कर्नाटक · सोने की खदानें", SUV, "s")]
# long-distance trade: the northern road from Taxila down the Ganga plain, and the road up from Ujjayini
ROUTE_N = [TAX, [74.4, 31.6], [76.0, 30.3], [77.2, 28.6], [78.0, 27.3], [80.3, 26.5], [82.9, 25.4], PAT]
ROUTE_S = [UJJ, [76.6, 24.9], [77.4, 26.2], [78.0, 27.3]]
LABELS = [["सिंधु", [68.9, 25.4], "pre", "river"], ["गंगा", [87.2, 26.9], "pre", "river"],
          ["अरब सागर", [68.6, 16.0], "pre", "sea"], ["बंगाल की खाड़ी", [88.6, 15.0], "pre", "sea"]]


def centres(cues, names=None):
    """the five pins; a cue of 999 keeps a centre off this beat's map, a label of '?' hides its name"""
    out = []
    for (n, sub, ll, side), c in zip(CENTRES, cues):
        if c == 999:
            continue
        out.append([n if not names or names.get(n) != "?" else "?", "" if names and names.get(n) == "?" else sub, ll, c, side])
    return out


def seamap(ports, routes=None, extra_labels=()):
    return {"type": "seamap", "slot": "head", "map": "subcontinent", "labels": LABELS + list(extra_labels),
            "routes": routes or [], "ports": ports, "calm": False}


beats = []
B = lambda **k: beats.append(k)
B(id="ujjain", **{"in": 0, "out": 2}, presenter="standard", broll={"clip": "k01", "region": "full"}, elements=[
    {"type": "pill", "slot": "over-broll-low", "text": "हमारा उज्जैन, मध्यप्रदेश", "style": "accent", "at": 1}])
B(id="hook-map", **{"in": 2, "out": 5}, presenter="standard", elements=[
    seamap(centres([A(9.9), A(9.9), 2, A(10.3), A(10.6)], names={"पाटलिपुत्र": "?", "तक्षशिला": "?", "तोसलि": "?", "सुवर्णगिरि": "?"}))])
B(id="question", **{"in": 5, "out": 7}, presenter="small", broll={"clip": "k02", "region": "full", "dim": True}, elements=[
    {"type": "qcard", "slot": "upper", "question": "मौर्य साम्राज्य के कोई पाँच प्रमुख राजनीतिक केंद्रों के नाम लिखिए।",
     "year": "2022", "marks": "3 अंक", "t_marks": [6, 1.5], "at": 5}])
B(id="five", **{"in": 7, "out": 11}, presenter="standard", elements=[
    {"type": "counter", "slot": "upper", "num": "5", "label": "नाम, एक भी छूटा तो नंबर कटेगा", "at": 7},
    {"type": "stamp", "slot": "under-upper", "text": "जगह के साथ याद करें", "at": 9}])
B(id="pataliputra", **{"in": 11, "out": 13}, presenter="standard", broll={"clip": "k02", "region": "full"}, elements=[
    {"type": "pill", "slot": "over-broll-top", "text": "1 · पाटलिपुत्र", "style": "accent", "at": A(35.04)},
    {"type": "note", "slot": "over-broll-low", "text": "मौर्य साम्राज्य की राजधानी", "at": A(37.4)}])
B(id="patna", **{"in": 13, "out": 14}, presenter="standard", broll={"clip": "k03", "region": "full"}, elements=[
    {"type": "note", "slot": "over-broll-top", "text": "आज: पटना", "at": A(39.4)}])
B(id="capital", **{"in": 14, "out": 16}, presenter="standard", elements=[
    {"type": "def", "slot": "head", "term": "पाटलिपुत्र", "text": "राजधानी", "at": A(42.9)},
    {"type": "stamp", "slot": "upper", "text": "आगे 'राजधानी' ज़रूर लिखें", "at": 15}])
B(id="provinces", **{"in": 16, "out": 17}, presenter="standard", broll={"clip": "k08", "region": "full"}, elements=[
    {"type": "pill", "slot": "over-broll-low", "text": "बाकी चार: प्रांतीय केंद्र", "style": "accent", "at": A(47.9)}])
B(id="west-map", **{"in": 17, "out": 22}, presenter="standard", elements=[
    seamap(centres(["pre", A(50.7), A(54.1), 999, 999]),
           routes=[{"pts": ROUTE_N, "at": A(61.6), "dur": 1.6, "tag": "लंबी दूरी के व्यापार मार्ग", "tag_xy": [82.6, 30.2], "tag_at": A(62.44)},
                   {"pts": ROUTE_S, "at": A(62.0), "dur": 1.0}])])
B(id="caravan", **{"in": 22, "out": 26}, presenter="standard", broll={"clip": "k05", "region": "full"}, elements=[
    {"type": "note", "slot": "over-broll-top", "text": "इसीलिए इतने ज़रूरी", "at": 22},
    {"type": "stamp", "slot": "over-broll", "text": "व्यापार वाले: तक्षशिला, उज्जयिनी", "at": 23}])
B(id="east", **{"in": 26, "out": 28}, presenter="standard", broll={"clip": "k07", "region": "full"}, elements=[
    {"type": "pill", "slot": "over-broll-top", "text": "पूरब की ओर →", "at": 26},
    {"type": "pills", "slot": "over-broll-low", "style": "accent", "items": [["4 · तोसलि", A(71.38)], ["(तोशाली)", A(72.48)]]}])
B(id="dhauli", **{"in": 28, "out": 30}, presenter="standard", elements=[
    {"type": "photo", "slot": "upper", "src": "history/mauryan-centres/dhauli-3.jpg", "w": 760,
     "label": "धौली, ओडिशा: तोसलि के अधिकारियों को अशोक का आदेश", "at": 28},
    {"type": "pill", "slot": "under-upper", "text": "आज ओडिशा = कलिंग वाला इलाका", "style": "accent", "at": A(76.58)}])
B(id="golden-hill", **{"in": 30, "out": 32}, presenter="standard", broll={"clip": "k11", "region": "full"}, elements=[
    {"type": "note", "slot": "over-broll-top", "text": "नाम ही कहानी बताता है", "at": A(80.3)},
    {"type": "stamp", "slot": "over-broll", "text": "5 · सुवर्ण-गिरि", "at": A(82.08)}])
B(id="gold-meaning", **{"in": 32, "out": 33}, presenter="standard", broll={"clip": "k10", "region": "full"}, elements=[
    {"type": "def", "slot": "over-broll-top", "term": "सुवर्ण-गिरि", "text": "सोने का पहाड़", "at": 32}])
B(id="gold-mine", **{"in": 33, "out": 35}, presenter="standard", broll={"clip": "k09", "region": "full"}, elements=[
    {"type": "pill", "slot": "over-broll-low", "text": "कर्नाटक की सोने की खदानें", "style": "accent", "at": A(88.84)}])
B(id="full-map", **{"in": 35, "out": 37}, presenter="standard", elements=[
    seamap(centres(["pre", "pre", "pre", A(92.0), A(92.6)]),
           routes=[{"pts": ROUTE_N, "at": "pre"}, {"pts": ROUTE_S, "at": "pre"}])])
B(id="chosen", **{"in": 37, "out": 41}, presenter="standard", elements=[
    {"type": "headline", "slot": "head", "text": "प्रांतीय केंद्र: सोच-समझकर चुने गए", "size": "m", "at": 37},
    {"type": "cards3", "slot": "upper", "items": [["व्यापार मार्ग पर: तक्षशिला, उज्जयिनी", A(103.66)],
                                                   ["सोने की खदानों के पास: सुवर्णगिरि", A(105.52)]]},
    {"type": "stamp", "slot": "under-upper", "text": "answer के आखिर में लिखें", "at": [37, 1.0]}])
B(id="recall", **{"in": 41, "out": 44}, presenter="hub", hub={"cy": 1000, "r": 200, "backdrop": "veo:k06@3"}, elements=[
    {"type": "headline", "slot": "head", "text": "पाँचों एक साथ", "size": "m", "at": 41},
    {"type": "radial", "slot": "around-hub", "radius": 330, "cumulative": True, "items": [
        ["tabler:crown", "पाटलिपुत्र (राजधानी)", 41], ["tabler:route", "तक्षशिला", 41], ["tabler:route", "उज्जयिनी", 41],
        ["tabler:building-castle", "तोसलि", 41], ["tabler:coin", "सुवर्णगिरि", 41]],
     "recount": [A(109.04), A(111.62), A(112.74), A(113.70), A(115.06)]}])
B(id="marks", **{"in": 44, "out": 46}, presenter="standard", broll={"clip": "k02", "region": "full", "dim": True, "offset": 4}, elements=[
    {"type": "pill", "slot": "over-broll-top", "text": "पाँचों नाम + पाटलिपुत्र के आगे 'राजधानी'", "style": "accent", "at": 44},
    {"type": "stamp", "slot": "over-broll", "text": "पूरे 3 नंबर पक्के", "at": 45}])
B(id="notes", **{"in": 46, "out": 47}, presenter="hero", broll={"clip": "k05", "region": "full", "dim": True, "offset": 4}, elements=[
    {"type": "pill", "slot": "head", "text": "exam वाला answer: Notes button", "style": "accent", "at": 46}])
B(id="outro", **{"in": 47, "out": "end"}, presenter="hero", broll={"clip": "k13", "region": "full", "dim": True}, elements=[
    {"type": "note", "slot": "over-broll-top", "text": "रोज़ एक topic, सोच-समझकर", "at": 48}])

plan = {"_about": "HIS-C2-SA-06, edict theme on a borderless map", "project": "his-c2-sa-06", "part": 1, "captions_from": 7,
        "skin": "paper-editorial", "theme": "edict", "presenter_style": "card", "plate": "edict-sandstone-girnar",
        "spine": {"title": "मौर्य साम्राज्य: 5 राजनीतिक केंद्र", "items": [c[0] for c in CENTRES],
                  "lit_at": [11, 17, 19, 27, 31], "show_from": 7},
        "beats": beats}
(ROOT / "lab/kit_test/plan_his_c2_sa_06_p1.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1))
shots = {"k01": "Ujjain ghats on the Shipra at dawn", "k02": "Mauryan Pataliputra on the Ganga, aerial", "k03": "modern Patna on the Ganga",
         "k04": "hillside monastery ruins, north-west", "k05": "trade caravan heading to a walled city", "k06": "ancient Indian market street",
         "k07": "Odisha river and paddy fields, aerial", "k08": "provincial governor arriving on an elephant", "k09": "ancient gold mine by lamplight",
         "k10": "gold panning, flakes in the pan", "k11": "golden granite hills of Karnataka", "k12": "royal messenger on horseback",
         "k13": "student studying an atlas"}
(PROJ / "veo/shots.json").write_text(json.dumps(shots, indent=1))
print(len(beats), "beats")
