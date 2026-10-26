"""GEO-C8-SA-01 (अंतर्राष्ट्रीय पत्तनों की चार विशेषताएँ), two parts: cargo look.

    python lab/kit_test/make_geo_c8_01_plans.py  ->  plan_geo_c8_sa_01_p{1,2}.json

Cues in SECONDS of narration become [line, offset].  Clips r_v08 / r_v10 are the
Mumbai port and Singapore Strait clips made for GEO-C7-SA-02, hard-linked in.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROJ = ROOT / "projects/geo-c8-sa-01"


def cues(n):
    L = json.loads((PROJ / f"lines_part{n}.json").read_text())
    def A(sec):
        i = max(k for k, l in enumerate(L) if l["start"] <= sec + 1e-6)
        return [i, round(sec - L[i]["start"], 2)]
    return A


FOUR = [["tabler:ripple", "गहरा जल"], ["tabler:crane", "आधुनिक सुविधाएँ"],
        ["tabler:map-2", "विशाल पृष्ठ प्रदेश"], ["tabler:world", "अंतर्राष्ट्रीय व्यापार केंद्र"]]
HUB = {"cy": 1000, "r": 215}
SPINE = {"title": "अंतर्राष्ट्रीय पत्तन: 4 विशेषताएँ", "items": [f[1] for f in FOUR]}


def radial(shown_at, recount):
    return {"type": "radial", "slot": "around-hub", "radius": 330, "cumulative": True,
            "items": [[ic, lb, at] for (ic, lb), at in zip(FOUR, shown_at)], "recount": recount}


def part1():
    A = cues(1); beats = []; B = lambda **k: beats.append(k)
    B(id="phone", **{"in": 0, "out": 3}, presenter="standard", broll={"clip": "d01", "region": "full"}, elements=[
        {"type": "pill", "slot": "over-broll-low", "text": "फोन के कई पुर्ज़े: दूसरे देश में बने", "style": "accent", "at": 1}])
    B(id="voyage", **{"in": 3, "out": 5}, presenter="standard", broll={"clip": "d02", "region": "full"}, elements=[
        {"type": "note", "slot": "over-broll-top", "text": "हज़ारों किलोमीटर दूर से…", "at": 3},
        {"type": "pill", "slot": "over-broll-low", "text": "आपके शहर तक कैसे?", "at": 4}])
    B(id="first-stop", **{"in": 5, "out": 6}, presenter="standard", broll={"clip": "d03", "region": "full"}, elements=[
        {"type": "stamp", "slot": "over-broll", "text": "पहला पड़ाव: अंतर्राष्ट्रीय पत्तन", "at": A(13.4)}])
    B(id="question", **{"in": 6, "out": 9}, presenter="small", broll={"clip": "r_v08", "region": "full", "dim": True}, elements=[
        {"type": "qcard", "slot": "upper", "question": "अंतर्राष्ट्रीय पत्तनों की कोई चार विशेषताएँ लिखिए।",
         "year": "2024", "marks": "3 अंक", "t_marks": [7, 0.8], "at": 6}])
    B(id="port-is", **{"in": 9, "out": 11}, presenter="standard", elements=[
        {"type": "def", "slot": "head", "term": "पत्तन", "text": "बंदरगाह", "at": 9},
        {"type": "chain", "slot": "upper", "items": [["जहाज़ आकर रुकते हैं", [9, 2.4]], ["माल चढ़ता-उतरता है", 10]]}])
    B(id="not-every", **{"in": 11, "out": 12}, presenter="standard", broll={"clip": "d04", "region": "full"}, elements=[
        {"type": "stamp", "slot": "over-broll", "text": "हर बंदरगाह अंतर्राष्ट्रीय नहीं", "at": 11}])
    B(id="four", **{"in": 12, "out": 14}, presenter="standard", elements=[
        {"type": "counter", "slot": "upper", "num": "4", "label": "विशेषताएँ जो पत्तन को अंतर्राष्ट्रीय बनाती हैं", "at": 12}])
    B(id="deep", **{"in": 14, "out": 15}, presenter="standard", broll={"clip": "d05", "region": "full"}, elements=[
        {"type": "section", "slot": "over-broll-top", "num": "1", "text": "गहरा जल, विशाल पोताश्रय", "at": 14}])
    B(id="big-ships", **{"in": 15, "out": 19}, presenter="standard", broll={"clip": "r_v10", "region": "full"}, elements=[
        {"type": "pills", "slot": "over-broll-low", "items": [["बड़े मालवाहक जहाज़", A(46.2)], ["टैंकर", A(47.6)], ["कंटेनर जहाज़", A(48.3)]]},
        {"type": "note", "slot": "over-broll-top", "text": "आसानी से आ-जा सकें, ठहर सकें", "at": 17}])
    B(id="draft", **{"in": 19, "out": 22}, presenter="standard", elements=[
        {"type": "depth", "slot": "upper", "t_shallow": A(53.02), "t_stuck": A(57.54), "t_deep": A(58.74)}])
    B(id="aground", **{"in": 22, "out": 23}, presenter="standard", broll={"clip": "d06", "region": "full"}, elements=[
        {"type": "stamp", "slot": "over-broll", "text": "गहराई: सबसे पहली शर्त", "at": 22}])
    B(id="write-both", **{"in": 23, "out": 25}, presenter="standard", elements=[
        {"type": "def", "slot": "head", "term": "गहरा जल + विशाल पोताश्रय", "text": "दोनों साथ", "at": 24},
        {"type": "stamp", "slot": "upper", "text": "एक ही point में लिखें", "at": [24, 1.4]}])
    B(id="one-done", **{"in": 25, "out": 26}, presenter="hub", hub={**HUB, "backdrop": "veo:d05@3"}, elements=[
        {"type": "headline", "slot": "head", "text": "पानी तैयार… अब माल?", "size": "m", "at": 25},
        radial([25, 999, 999, 999], [25])])
    B(id="modern", **{"in": 26, "out": 27}, presenter="standard", broll={"clip": "d07", "region": "full"}, elements=[
        {"type": "section", "slot": "over-broll-top", "num": "2", "text": "आधुनिक सुविधाएँ", "at": 26}])
    B(id="facilities", **{"in": 27, "out": 31}, presenter="standard", elements=[
        {"type": "tiles", "slot": "upper", "cols": 3, "items": [
            ["tabler:crane", "बड़ी क्रेनें", A(80.18)], ["tabler:building-warehouse", "गोदाम", A(82.44)],
            ["tabler:snowflake", "शीत भंडार", A(83.38)], ["tabler:container", "कंटेनर टर्मिनल", A(84.16)],
            ["tabler:anchor", "गोदी (डॉक)", A(85.28)], ["tabler:tools", "मरम्मत", A(87.8)]]}])
    B(id="cold", **{"in": 31, "out": 33}, presenter="standard", broll={"clip": "d08", "region": "full"}, elements=[
        {"type": "def", "slot": "over-broll-top", "term": "शीत भंडार", "text": "ठंडा रखने वाला गोदाम", "at": 31},
        {"type": "pill", "slot": "over-broll-low", "text": "फल-सब्ज़ी: जल्दी खराब होने वाला माल", "at": 32}])
    B(id="name-them", **{"in": 33, "out": 37}, presenter="standard", broll={"clip": "d09", "region": "full"}, elements=[
        {"type": "stamp", "slot": "over-broll", "text": "कम से कम 4-5 नाम गिनाएँ", "at": 34},
        {"type": "pill", "slot": "over-broll-low", "text": "गोदी (डॉक): ब्रैकेट में लिखें", "style": "accent", "at": 35}])
    B(id="two-done", **{"in": 37, "out": 38}, presenter="hub", hub={**HUB, "backdrop": "veo:d07@3"}, elements=[
        {"type": "headline", "slot": "head", "text": "दो विशेषताएँ हो गईं", "size": "m", "at": 37},
        radial([37, 37, 999, 999], [37, [37, 2.4]])])
    B(id="teaser", **{"in": 38, "out": "end"}, presenter="standard", broll={"clip": "d10", "region": "full", "dim": True}, elements=[
        {"type": "headline", "slot": "over-broll-top", "text": "माल देश के अंदर कैसे जाएगा?", "size": "m", "at": 38},
        {"type": "pill", "slot": "over-broll-low", "text": "जवाब: Part 2 में", "style": "accent", "at": 40}])
    return {"captions_from": 9, "spine": {**SPINE, "lit_at": [14, 26], "show_from": 9}, "beats": beats}


# the lane from Rotterdam round through Suez to Shanghai (lon, lat)
LANE = [[4.3, 52.0], [2.0, 51.2], [-5.0, 48.8], [-9.6, 43.0], [-9.8, 37.5], [-5.6, 35.95], [3, 37.6], [11.5, 37.4], [20, 34.2],
        [32.3, 31.4], [32.6, 29.8], [34.6, 27.2], [38.4, 20.5], [42.3, 14.6], [43.4, 12.6], [45, 12.7], [53, 14.3], [63, 17.5],
        [72.6, 18.9], [72.4, 15], [74.4, 10.5], [76.6, 7.3], [79.6, 6.9], [82.5, 5.6], [91, 6.2], [96.5, 5.9], [99.5, 3.6],
        [103.8, 1.25], [106, 3], [109.5, 9], [112, 15], [117, 21], [119.5, 24.5], [122.2, 28.5], [121.6, 31.1]]


def part2():
    A = cues(2); beats = []; B = lambda **k: beats.append(k)
    B(id="recall", **{"in": 0, "out": 2}, presenter="hub", hub={**HUB, "backdrop": "veo:d03@3"}, elements=[
        {"type": "headline", "slot": "head", "text": "Part 1 में", "size": "m", "at": 0},
        radial([0, 0, 999, 999], [[0, 3.5], [1, 1.6]])])
    B(id="unloaded", **{"in": 2, "out": 4}, presenter="standard", broll={"clip": "d07", "region": "full", "offset": 2}, elements=[
        {"type": "note", "slot": "over-broll-top", "text": "माल पत्तन पर उतर चुका…", "at": 3}])
    B(id="hinter-intro", **{"in": 4, "out": 5}, presenter="standard", broll={"clip": "d11", "region": "full"}, elements=[
        {"type": "section", "slot": "over-broll-top", "num": "3", "text": "विशाल पृष्ठ प्रदेश", "at": A(15.2)}])
    B(id="meaning", **{"in": 5, "out": 9}, presenter="standard", elements=[
        {"type": "headline", "slot": "head", "text": "नया शब्द, आसान मतलब", "size": "m", "at": 5},
        {"type": "cards3", "slot": "upper", "items": [["पृष्ठ = पीठ", A(20.4)], ["पृष्ठ प्रदेश = पत्तन के पीछे का पूरा इलाका", 7]]}])
    B(id="hinterland", **{"in": 9, "out": 13}, presenter="standard", elements=[
        {"type": "hinterland", "slot": "upper", "h": 760, "t_region": A(33.96),
         "links": [["रेल", "rail", A(28.86)], ["सड़क", "road", A(29.44)], ["पाइपलाइन", "pipe", A(30.32)], ["जलमार्ग", "water", A(30.84)]],
         "t_export": A(37.2), "t_import": A(39.02)}])
    B(id="weight", **{"in": 13, "out": 16}, presenter="standard", elements=[
        {"type": "headline", "slot": "head", "text": "पृष्ठ प्रदेश", "size": "m", "at": 13},
        {"type": "stamp", "slot": "upper", "text": "सबसे ज़्यादा वज़न वाला term", "at": [14, 1.0]},
        {"type": "note", "slot": "under-upper", "text": "साफ अक्षरों में लिखें", "at": 15}])
    B(id="three-done", **{"in": 16, "out": 18}, presenter="hub", hub={**HUB, "backdrop": "veo:d11@3"}, elements=[
        {"type": "headline", "slot": "head", "text": "पीछे बड़ा इलाका, आगे पूरी दुनिया", "size": "m", "at": 16},
        radial([16, 16, 16, 999], [16, 16, [16, 0.6]])])
    B(id="trade", **{"in": 18, "out": 19}, presenter="standard", broll={"clip": "d16", "region": "full"}, elements=[
        {"type": "section", "slot": "over-broll-top", "num": "4", "text": "अंतर्राष्ट्रीय व्यापार का केंद्र", "at": A(55.9)}])
    B(id="lanes", **{"in": 19, "out": 21}, presenter="standard", broll={"clip": "r_v10", "region": "full"}, elements=[
        {"type": "pills", "slot": "over-broll-low", "items": [["प्रमुख समुद्री मार्गों पर", 19], ["अनेक देशों से आयात-निर्यात", 20]]}])
    B(id="customs", **{"in": 21, "out": 24}, presenter="standard", broll={"clip": "d13", "region": "full"}, elements=[
        {"type": "def", "slot": "over-broll-top", "term": "सीमा शुल्क", "text": "कस्टम", "at": 21},
        {"type": "note", "slot": "over-broll-low", "text": "भारी मात्रा, तरह-तरह का माल", "at": 22}])
    B(id="examples", **{"in": 24, "out": 31}, presenter="standard", elements=[
        {"type": "headline", "slot": "head", "text": "उदाहरण, याद रखने के तरीके से", "size": "m", "at": 24},
        {"type": "seamap", "slot": "upper", "map": "world-trade",
         "labels": [["यूरोप", [22, 50], "pre"], ["अफ्रीका", [20, 8], "pre"], ["एशिया", [92, 40], "pre"]],
         "routes": [{"pts": LANE, "at": 24, "dur": 3.0}],
         "ports": [["रॉटरडैम", "नीदरलैंड", [4.3, 51.9], A(79.48), "e"], ["सिंगापुर", "", [103.8, 1.3], A(81.88), "s"],
                   ["शंघाई", "चीन", [121.5, 31.2], A(82.98), "nw"], ["मुंबई", "भारत", [72.8, 18.9], A(84.78), "w"]]},
        {"type": "pills", "slot": "under-upper", "style": "accent",
         "items": [["1 यूरोप", A(85.92)], ["2 एशिया", A(87.44)], ["1 भारत", A(88.86)]]}])
    B(id="adjectives", **{"in": 31, "out": 34}, presenter="hub", hub={**HUB, "backdrop": "veo:d16@3"}, elements=[
        {"type": "headline", "slot": "head", "text": "गहरा · आधुनिक · विशाल · अंतर्राष्ट्रीय", "size": "m", "at": 31},
        radial([31, 31, 31, 31], [A(93.44), A(94.24), A(94.76), A(95.52)])])
    B(id="marks", **{"in": 34, "out": 36}, presenter="standard", broll={"clip": "d14", "region": "full", "dim": True}, elements=[
        {"type": "pill", "slot": "over-broll-top", "text": "चारों विशेषताएँ + उदाहरण", "style": "accent", "at": 34},
        {"type": "stamp", "slot": "over-broll", "text": "3 नंबर पक्के", "at": 35}])
    B(id="notes", **{"in": 36, "out": 37}, presenter="hero", broll={"clip": "d15", "region": "full", "dim": True}, elements=[
        {"type": "pill", "slot": "head", "text": "exam-ready answer: Notes button", "style": "accent", "at": 36}])
    B(id="outro", **{"in": 37, "out": "end"}, presenter="hero", broll={"clip": "d16", "region": "full", "dim": True, "offset": 2}, elements=[
        {"type": "note", "slot": "over-broll-top", "text": "रोज़ थोड़ा-थोड़ा, पूरा syllabus", "at": 39}])
    return {"spine": {**SPINE, "pre_lit": 2, "lit_at": [4, 18], "show_from": 0}, "beats": beats}


shots = {"d01": "phone circuit-board assembly", "d02": "container ship guided in by tugs", "d03": "vast busy seaport, aerial",
         "d04": "small shallow fishing harbour", "d05": "deep sheltered natural harbour", "d06": "cargo ship aground in shallows",
         "d07": "gantry crane unloading a container", "d08": "cold-storage warehouse", "d09": "ship in dry dock for repair",
         "d10": "container train heading inland", "d11": "container trucks leaving the port", "d12": "container barge on a river",
         "d13": "customs inspecting a container", "d14": "European port at dusk (Rotterdam-like)", "d15": "Shanghai island terminal and sea bridge",
         "d16": "port at night", "r_v08": "Mumbai container port (from GEO-C7-SA-02)", "r_v10": "Singapore Strait ships (from GEO-C7-SA-02)"}
(PROJ / "veo/shots.json").write_text(json.dumps(shots, indent=1))
for n, f in ((1, part1), (2, part2)):
    body = f()
    plan = {"_about": f"GEO-C8-SA-01 part {n}, cargo look", "project": "geo-c8-sa-01", "part": n,
            "skin": "paper-editorial", "theme": "cargo", "presenter_style": "card", "plate": "sea-container-port", **body}
    out = ROOT / f"lab/kit_test/plan_geo_c8_sa_01_p{n}.json"
    out.write_text(json.dumps(plan, ensure_ascii=False, indent=1))
    print(out.name, len(body["beats"]), "beats")
