"""HIS-C2-SA-08 (मौर्य साम्राज्य भारतीय इतिहास का प्रमुख काल क्यों): imperial look, one part.

    python lab/kit_test/make_his_c2_08_plan.py  ->  plan_his_c2_sa_08_p1.json

The narration's own image carries the opening: before the Mauryas, India was
"scattered pearls"; the Mauryas strung them on one thread.  On the borderless
subcontinent map the sixteen mahajanapadas appear as loose pearls, a gold thread
strings them, and later the empire's approximate extent shades in.
Cues in seconds -> [line, offset].
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROJ = ROOT / "projects/his-c2-sa-08"
L = json.loads((PROJ / "lines_part1.json").read_text())


def A(sec):
    i = max(k for k, l in enumerate(L) if l["start"] <= sec + 1e-6)
    return [i, round(sec - L[i]["start"], 2)]


# the sixteen mahajanapadas, approximately, threaded north-west to south
BEADS = [[70.5, 35.0], [72.0, 33.9], [77.2, 29.2], [76.3, 27.2], [77.7, 27.4], [79.4, 27.9], [82.2, 26.8], [83.9, 26.7],
         [85.2, 25.9], [87.0, 25.2], [85.4, 24.9], [83.0, 25.3], [81.8, 25.4], [80.2, 24.4], [75.8, 23.2], [77.8, 18.6]]
# the Mauryan realm under Ashoka, roughly: all but the far south (labelled "लगभग")
EMPIRE = [[66, 25], [66, 36.5], [74, 36.5], [76, 34], [79, 31], [81, 30], [84, 28], [88, 27], [89.5, 26], [88.5, 22],
          [86.5, 20], [85, 19], [82, 16.5], [80, 15.5], [80, 13.5], [78, 12.5], [76, 13], [74.5, 14.5], [73.2, 17],
          [72.8, 19], [72.6, 21], [70, 22.3], [68.5, 23.5], [67, 24.8]]
SEAS = [["अरब सागर", [68.6, 16.0], "pre", "sea"], ["बंगाल की खाड़ी", [88.6, 15.0], "pre", "sea"]]


def pearls(t_beads, t_thread, region=None, t_region=None, label_at=None):
    e = {"type": "seamap", "slot": "head", "map": "subcontinent", "labels": SEAS, "routes": [], "ports": [],
         "beads": BEADS, "t_beads": t_beads, "t_thread": t_thread}
    if region:
        e.update(region=EMPIRE, t_region=t_region, region_label="मौर्य साम्राज्य (लगभग)", region_xy=None,
                 region_label_xy=[79.5, 21.0], t_region_label=label_at)
    e.pop("region_xy", None)
    return e


beats = []
B = lambda **k: beats.append(k)
B(id="divided", **{"in": 0, "out": 2}, presenter="standard", broll={"clip": "m02", "region": "full"}, elements=[
    {"type": "pill", "slot": "over-broll-low", "text": "मौर्यों से पहले: छोटे-छोटे राज्य", "style": "accent", "at": A(3.88)}])
B(id="pearls-clip", **{"in": 2, "out": 3}, presenter="standard", broll={"clip": "m01", "region": "full"}, elements=[
    {"type": "note", "slot": "over-broll-top", "text": "जैसे बिखरे हुए मोती", "at": A(6.8)}])
B(id="pearls-map", **{"in": 3, "out": 5}, presenter="standard", elements=[pearls(3, A(10.64))])
B(id="question", **{"in": 5, "out": 8}, presenter="small", broll={"clip": "m03", "region": "full", "dim": True}, elements=[
    {"type": "qcard", "slot": "upper", "question": "मौर्य साम्राज्य को भारतीय इतिहास का प्रमुख काल क्यों माना जाता है?",
     "year": "2022", "marks": "3 अंक", "t_marks": [7, 1.5], "at": 5}])
B(id="chain", **{"in": 8, "out": 12}, presenter="standard", elements=[
    {"type": "headline", "slot": "head", "text": "चार कारण, एक कड़ी में", "size": "m", "at": 8},
    {"type": "chain", "slot": "upper", "items": [["देश जुड़ा", A(27.04)], ["तंत्र बना", A(27.9)], ["सही राह मिली", A(29.48)],
                                                  ["सब लिखकर हम तक पहुँचा", A(30.62)]]}])
B(id="unity", **{"in": 12, "out": 13}, presenter="standard", broll={"clip": "m03", "region": "full"}, elements=[
    {"type": "section", "slot": "over-broll-top", "num": "1", "text": "प्रथम अखिल भारतीय साम्राज्य", "at": A(35.82)}])
B(id="empire-map", **{"in": 13, "out": 15}, presenter="standard", elements=[
    pearls(13, 13, region=True, t_region=A(44.72), label_at=A(46.2))])
B(id="two-words", **{"in": 15, "out": 16}, presenter="standard", elements=[
    {"type": "stamp", "slot": "upper", "text": "प्रथम · अखिल भारतीय", "at": 15},
    {"type": "note", "slot": "under-upper", "text": "ये दोनों शब्द ज़रूर लिखें", "at": [15, 1.2]}])
B(id="who-runs", **{"in": 16, "out": 18}, presenter="standard", broll={"clip": "m06", "region": "full"}, elements=[
    {"type": "note", "slot": "over-broll-top", "text": "इतना बड़ा साम्राज्य… संभालेगा कौन?", "at": 16}])
B(id="admin", **{"in": 18, "out": 20}, presenter="standard", broll={"clip": "m04", "region": "full"}, elements=[
    {"type": "section", "slot": "over-broll-top", "num": "2", "text": "सुदृढ़ प्रशासन", "at": [18, 1.6]},
    {"type": "pills", "slot": "over-broll-low", "style": "accent", "items": [["चंद्रगुप्त मौर्य", A(62.3)], ["चाणक्य (कौटिल्य)", A(63.54)]]}])
B(id="admin-kind", **{"in": 20, "out": 22}, presenter="standard", elements=[
    {"type": "headline", "slot": "head", "text": "प्रशासन कैसा?", "size": "m", "at": 20},
    {"type": "cards3", "slot": "upper", "items": [["मज़बूत", A(68.58)], ["केंद्रीयकृत", A(69.42)], ["सुव्यवस्थित", A(70.36)]]}])
B(id="central", **{"in": 22, "out": 23}, presenter="standard", broll={"clip": "m05", "region": "full"}, elements=[
    {"type": "def", "slot": "over-broll-top", "term": "केंद्रीयकृत", "text": "बड़े फैसले राजधानी से", "at": 22}])
B(id="pair", **{"in": 23, "out": 25}, presenter="standard", elements=[
    {"type": "headline", "slot": "head", "text": "चंद्रगुप्त + चाणक्य", "size": "m", "at": A(80.28)},
    {"type": "stamp", "slot": "upper", "text": "दोनों नाम, जोड़ी में लिखें", "at": A(81.92)}])
B(id="kalinga", **{"in": 25, "out": 27}, presenter="standard", broll={"clip": "m07", "region": "full"}, elements=[
    {"type": "note", "slot": "over-broll-top", "text": "दुनिया भर में अलग पहचान", "at": 26},
    {"type": "section", "slot": "over-broll-low", "num": "3", "text": "अशोक का धम्म", "at": [26, 3.9]}])
B(id="drums", **{"in": 27, "out": 29}, presenter="standard", broll={"clip": "m08", "region": "full"}, elements=[
    {"type": "def", "slot": "over-broll-top", "term": "भेरीघोष", "text": "युद्ध के नगाड़े", "at": A(93.3)},
    {"type": "pill", "slot": "over-broll-low", "text": "छोड़कर → धम्म का रास्ता", "style": "accent", "at": A(95.9)}])
B(id="dhamma", **{"in": 29, "out": 30}, presenter="standard", broll={"clip": "m10", "region": "full"}, elements=[
    {"type": "pills", "slot": "over-broll-low", "style": "accent", "items": [["शांति", A(99.1)], ["सहिष्णुता", A(100.26)], ["नैतिकता", A(101.24)]]}])
B(id="world", **{"in": 30, "out": 31}, presenter="standard", broll={"clip": "m11", "region": "full"}, elements=[
    {"type": "note", "slot": "over-broll-top", "text": "पूरी दुनिया को प्रेरणा", "at": 30}])
B(id="bheri-mark", **{"in": 31, "out": 33}, presenter="standard", broll={"clip": "m09", "region": "full"}, elements=[
    {"type": "stamp", "slot": "over-broll", "text": "'भेरीघोष' ज़रूर लिखें", "at": 31},
    {"type": "note", "slot": "over-broll-low", "text": "यही इस point की पहचान", "at": 32}])
B(id="sources", **{"in": 33, "out": 37}, presenter="standard", elements=[
    {"type": "section", "slot": "head", "num": "4", "text": "प्रामाणिक ऐतिहासिक स्रोत", "at": [33, 4.0]},
    {"type": "cards3", "slot": "upper", "items": [["अशोक के अभिलेख", A(116.44)], ["कौटिल्य का अर्थशास्त्र", A(117.92)],
                                                   ["मेगस्थनीज की इंडिका", A(120.26)]]},
    {"type": "pill", "slot": "under-upper", "text": "ठोस लिखित सबूत", "style": "accent", "at": A(122.1)}])
B(id="four-words", **{"in": 37, "out": 40}, presenter="hub", hub={"cy": 980, "r": 200, "backdrop": "veo:m03@3"}, elements=[
    {"type": "headline", "slot": "head", "text": "चार शब्दों में", "size": "m", "at": 37},
    {"type": "quad", "slot": "full", "icons": ["tabler:map-2", "tabler:building-bank", "tabler:peace", "tabler:book"], "items": [
        ["एकता", "अखिल भारतीय साम्राज्य", A(127.84)], ["प्रशासन", "चंद्रगुप्त-चाणक्य", A(128.1)],
        ["धम्म", "अशोक का धम्म", A(129.16)], ["स्रोत", "अभिलेख, अर्थशास्त्र, इंडिका", A(129.94)]]}])
B(id="marks", **{"in": 40, "out": 42}, presenter="standard", broll={"clip": "m03", "region": "full", "dim": True, "offset": 4}, elements=[
    {"type": "pill", "slot": "over-broll-top", "text": "चारों कारण, नामों के साथ", "style": "accent", "at": 40},
    {"type": "stamp", "slot": "over-broll", "text": "पूरे 3 नंबर पक्के", "at": 41}])
B(id="notes", **{"in": 42, "out": 43}, presenter="hero", broll={"clip": "m11", "region": "full", "dim": True, "offset": 3}, elements=[
    {"type": "pill", "slot": "head", "text": "exact format: Notes button", "style": "accent", "at": 42}])
B(id="outro", **{"in": 43, "out": "end"}, presenter="hero", broll={"clip": "m12", "region": "full", "dim": True}, elements=[
    {"type": "note", "slot": "over-broll-top", "text": "हर topic पूरा, 90% की ओर", "at": 44}])

plan = {"_about": "HIS-C2-SA-08, imperial look", "project": "his-c2-sa-08", "part": 1, "captions_from": 8,
        "skin": "paper-editorial", "theme": "imperial", "presenter_style": "card", "plate": "imperial-maroon-lion",
        "spine": {"title": "मौर्य काल: 4 कारण", "items": ["अखिल भारतीय साम्राज्य", "सुदृढ़ प्रशासन", "अशोक का धम्म", "प्रामाणिक स्रोत"],
                  "lit_at": [12, 18, 26, 33], "show_from": 8},
        "beats": beats}
(ROOT / "lab/kit_test/plan_his_c2_sa_08_p1.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1))
shots = {"m01": "pearls strung on a gold thread", "m02": "two small kingdoms' armies across a river", "m03": "Mauryan army marching, aerial",
         "m04": "Chandragupta and Chanakya at court", "m05": "Chanakya writing by lamplight", "m06": "royal granary, officials weighing grain",
         "m07": "Kalinga battlefield at dusk, Ashoka in sorrow", "m08": "war drums fall silent", "m09": "Ashoka planting trees, wells for travellers",
         "m10": "royal officer speaking to villagers", "m11": "monks boarding a ship", "m12": "student studying"}
(PROJ / "veo/shots.json").write_text(json.dumps(shots, indent=1))
print(len(beats), "beats")
