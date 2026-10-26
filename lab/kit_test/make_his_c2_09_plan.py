"""HIS-C2-SA-09 (राजा शब्द से क्या अभिप्राय है?): palm-leaf look, one part.

    python lab/kit_test/make_his_c2_09_plan.py  ->  plan_his_c2_sa_09_p1.json

Two meanings of the word, shown as two pictures: one crown on one throne, and a
ring of elders each of whom gets a crown (the 'crowns' template).  Cues in
seconds -> [line, offset].
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROJ = ROOT / "projects/his-c2-sa-09"
L = json.loads((PROJ / "lines_part1.json").read_text())
CORON = "s06" if (PROJ / "veo/clean/s06.mp4").exists() else "s01"     # the regenerated coronation, if it has come back


def A(sec):
    i = max(k for k, l in enumerate(L) if l["start"] <= sec + 1e-6)
    return [i, round(sec - L[i]["start"], 2)]


beats = []
B = lambda **k: beats.append(k)
B(id="throne", **{"in": 0, "out": 3}, presenter="standard", broll={"clip": "s01", "region": "full"}, elements=[
    {"type": "note", "slot": "over-broll-top", "text": "राजा = ?", "at": A(2.6)},
    {"type": "pills", "slot": "over-broll-low", "items": [["सिर पर मुकुट", A(7.26)], ["ऊँचा सिंहासन", A(8.38)]]}])
B(id="one-order", **{"in": 3, "out": 4}, presenter="standard", broll={"clip": "s05", "region": "full"}, elements=[
    {"type": "stamp", "slot": "over-broll", "text": "एक ही आदमी का हुक्म", "at": A(11.3)}])
B(id="many-kings", **{"in": 4, "out": 6}, presenter="standard", broll={"clip": "s03", "region": "full"}, elements=[
    {"type": "note", "slot": "over-broll-top", "text": "लेकिन प्राचीन भारत में कुछ जगहें…", "at": 4},
    {"type": "stamp", "slot": "over-broll", "text": "एक साथ कई-कई राजा!", "at": A(17.98)}])
B(id="question", **{"in": 6, "out": 8}, presenter="small", broll={"clip": "s02", "region": "full", "dim": True}, elements=[
    {"type": "qcard", "slot": "upper", "question": "राजा शब्द से क्या अभिप्राय है?", "year": "2022", "marks": "3 अंक",
     "t_marks": [7, 0.8], "at": 6}])
B(id="definition", **{"in": 8, "out": 11}, presenter="standard", elements=[
    {"type": "headline", "slot": "head", "text": "पहली लाइन: सीधी परिभाषा", "size": "m", "at": 8},
    {"type": "pills", "slot": "upper", "items": [["राज्य", A(31.74)], ["जनपद", A(32.26)], ["महाजनपद", A(33.0)]]},
    {"type": "def", "slot": "under-upper", "term": "राजा", "text": "सर्वोच्च शासक", "at": A(34.2)}])
B(id="powers", **{"in": 11, "out": 14}, presenter="standard", broll={"clip": "s05", "region": "full", "offset": 3}, elements=[
    {"type": "note", "slot": "over-broll-top", "text": "सबसे ऊपर बैठा व्यक्ति", "at": 11},
    {"type": "pills", "slot": "over-broll-low", "style": "accent", "items": [["प्रशासन", A(41.52)], ["न्याय", A(42.4)]]},
    {"type": "stamp", "slot": "over-broll", "text": "सारी शक्तियाँ एक हाथ में", "at": A(43.4)}])
B(id="hereditary", **{"in": 14, "out": 16}, presenter="standard", broll={"clip": CORON, "region": "full"}, elements=[
    {"type": "pill", "slot": "over-broll-top", "text": "वंश परंपरागत", "style": "accent", "at": A(48.7)},
    {"type": "note", "slot": "over-broll-low", "text": "पिता के बाद → बेटा", "at": A(51.0)}])
B(id="three", **{"in": 16, "out": 18}, presenter="standard", elements=[
    {"type": "headline", "slot": "head", "text": "परिभाषा में ये तीन ज़रूर", "size": "m", "at": 16},
    {"type": "cards3", "slot": "upper", "items": [["सर्वोच्च शासक", A(56.92)], ["प्रशासन और न्याय की शक्तियाँ", A(58.86)],
                                                   ["वंश परंपरागत पद", A(61.5)]]}])
B(id="but", **{"in": 18, "out": 20}, presenter="standard", broll={"clip": "s07", "region": "full"}, elements=[
    {"type": "stamp", "slot": "over-broll", "text": "लेकिन… सब जगह ऐसा नहीं", "at": 18}])
B(id="vajji", **{"in": 20, "out": A(69.86)}, presenter="standard", elements=[
    {"type": "photo", "slot": "upper", "src": "history/mahajanapada/vaishali-3.jpg", "w": 760, "label": "वैशाली (बिहार): वज्जि संघ की राजधानी", "at": 20},
    {"type": "pill", "slot": "under-upper", "text": "वज्जि", "style": "accent", "at": A(69.1)}])
B(id="malla", **{"in": A(69.86), "out": 21}, presenter="standard", broll={"clip": "s08", "region": "full"}, elements=[
    {"type": "pills", "slot": "over-broll-low", "style": "accent", "items": [["मल्ल (कुशीनारा)", A(69.86)], ["गण / संघ", A(70.54)]]}])
B(id="group", **{"in": 21, "out": 24}, presenter="standard", broll={"clip": "s03", "region": "full", "offset": 3}, elements=[
    {"type": "pills", "slot": "over-broll-low", "items": [["एक व्यक्ति नहीं", A(72.26)], ["कई लोगों का समूह", A(74.66)]]}])
B(id="each-raja", **{"in": 24, "out": 27}, presenter="standard", broll={"clip": "s04", "region": "full"}, elements=[
    {"type": "note", "slot": "over-broll-top", "text": "और मज़ेदार बात…", "at": 24},
    {"type": "stamp", "slot": "over-broll", "text": "हर सदस्य = राजा", "at": A(82.56)}])
B(id="crowns", **{"in": 27, "out": 33}, presenter="standard", elements=[
    {"type": "headline", "slot": "head", "text": "आज की भाषा में", "size": "m", "at": 27},
    {"type": "crowns", "slot": "upper", "h": 640, "many": 8,
     "left": "राजतंत्र: एक राजा", "t_one": A(87.62), "left_sub": "घर का एक मुखिया", "t_left_sub": A(90.72),
     "right": "गण-संघ: कई राजा", "t_many": A(92.08), "right_sub": "पंचायत", "t_right_sub": A(93.44)}])
B(id="panchayat", **{"in": 33, "out": 34}, presenter="standard", broll={"clip": "s09", "region": "full"}, elements=[
    {"type": "pill", "slot": "over-broll-low", "text": "सब बराबर के हकदार", "style": "accent", "at": 33}])
B(id="dont-stop", **{"in": 34, "out": 37}, presenter="standard", elements=[
    {"type": "yn", "slot": "upper", "no": "सिर्फ पहली परिभाषा", "yes": "परिभाषा + वज्जि-मल्ल का उदाहरण", "at": 34, "t_yes": A(106.26)},
    {"type": "stamp", "slot": "under-upper", "text": "यहीं नंबर कटते हैं", "at": A(103.8)}])
B(id="two-lines", **{"in": 37, "out": 41}, presenter="standard", elements=[
    {"type": "headline", "slot": "head", "text": "पूरा answer, दो लाइनों में", "size": "m", "at": 37},
    {"type": "cards3", "slot": "upper", "items": [["आमतौर पर: सर्वोच्च, वंश परंपरागत शासक", A(115.0)],
                                                   ["वज्जि-मल्ल जैसे गणों में: कई लोग मिलकर राजा", A(119.34)]]}])
B(id="marks", **{"in": 41, "out": 43}, presenter="standard", broll={"clip": "s02", "region": "full", "dim": True}, elements=[
    {"type": "pill", "slot": "over-broll-top", "text": "दोनों रूप लिखें", "style": "accent", "at": 41},
    {"type": "stamp", "slot": "over-broll", "text": "पूरे 3 नंबर पक्के", "at": 42}])
B(id="notes", **{"in": 43, "out": 45}, presenter="hero", broll={"clip": "s12", "region": "full", "dim": True}, elements=[
    {"type": "pill", "slot": "head", "text": "सही format: Notes button", "style": "accent", "at": 43}])
B(id="outro", **{"in": 45, "out": "end"}, presenter="hero", broll={"clip": "s10", "region": "full", "dim": True}, elements=[
    {"type": "note", "slot": "over-broll-top", "text": "पढ़ते रहो, तैयारी पक्की", "at": 45}])

plan = {"_about": "HIS-C2-SA-09, palm-leaf look", "project": "his-c2-sa-09", "part": 1, "captions_from": 8,
        "skin": "paper-editorial", "theme": "palmleaf", "presenter_style": "card", "plate": "palmleaf-stack",
        "spine": {"title": "राजा: दो रूप", "items": ["राजतंत्र: एक राजा", "गण-संघ: कई राजा"], "lit_at": [8, 18], "show_from": 8},
        "beats": beats}
(ROOT / "lab/kit_test/plan_his_c2_sa_09_p1.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1))
shots = {"s01": "king on a high throne, courtiers bowing", "s02": "golden crown on a red cushion", "s03": "elders debating in an assembly hall",
         "s04": "voting sticks dropped into a basket", "s05": "king giving judgment", "s06": "coronation: father crowns son",
         "s07": "ancient Gangetic city with a lotus pond", "s08": "sal grove beside an ancient town", "s09": "village panchayat under a banyan",
         "s10": "family dinner, grandfather at the head", "s11": "student writing an exam", "s12": "palm-leaf manuscripts turned"}
(PROJ / "veo/shots.json").write_text(json.dumps(shots, indent=1))
print(len(beats), "beats; coronation clip:", CORON)
