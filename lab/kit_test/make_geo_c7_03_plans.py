"""GEO-C7-SA-03 (विश्व में पाइपलाइन परिवहन के चार महत्व), two parts: blueprint look.

    python lab/kit_test/make_geo_c7_03_plans.py  ->  plan_geo_c7_sa_03_p{1,2}.json

Cues in SECONDS of narration become [line, offset], so a pipe fills on the word
that names its contents.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROJ = ROOT / "projects/geo-c7-sa-03"


def cues(n):
    L = json.loads((PROJ / f"lines_part{n}.json").read_text())
    def A(sec):
        i = max(k for k, l in enumerate(L) if l["start"] <= sec + 1e-6)
        return [i, round(sec - L[i]["start"], 2)]
    return A


WATER, OIL, GAS, LPG, SLURRY, MILK = "#3D8BFD", "#A0522D", "#9FE3F7", "#F28C28", "#3A3A3A", "#F4F1E8"
FOUR = [["tabler:clock", "समय-श्रम की बचत"], ["tabler:infinity", "निरंतर आपूर्ति"],
        ["tabler:coin-rupee", "किफायती और कुशल"], ["tabler:leaf", "पर्यावरण के अनुकूल"]]
HUB = {"cy": 1000, "r": 215}
SPINE = {"title": "पाइपलाइन परिवहन के 4 महत्व", "items": [f[1] for f in FOUR]}


def radial(shown_at, recount, extra=None):
    """the four benefits round the hub; an item not yet taught is never drawn (cue 999 = not in this part)"""
    return {"type": "radial", "slot": "around-hub", "radius": 330, "cumulative": True,
            "items": [[ic, lb, at] for (ic, lb), at in zip(FOUR, shown_at)], "recount": recount, **(extra or {})}


def part1():
    A = cues(1); beats = []; B = lambda **k: beats.append(k)
    B(id="tap", **{"in": 0, "out": 2}, presenter="standard", broll={"clip": "c01", "region": "full"}, elements=[
        {"type": "pill", "slot": "over-broll-low", "text": "नल खोलो, पानी हाज़िर", "style": "accent", "at": 1}])
    B(id="gas", **{"in": 2, "out": 5}, presenter="standard", broll={"clip": "c02", "region": "full"}, elements=[
        {"type": "pill", "slot": "over-broll-top", "text": "रसोई गैस: सीधे पाइप से", "at": 3},
        {"type": "stamp", "slot": "over-broll", "text": "न ट्रक, न टैंकर", "at": 4}])
    B(id="alaska", **{"in": 5, "out": 6}, presenter="standard", broll={"clip": "c03", "region": "full"}, elements=[
        {"type": "headline", "slot": "over-broll-top", "text": "पाइपलाइन परिवहन", "size": "m", "at": 5}])
    B(id="question", **{"in": 6, "out": 9}, presenter="small", broll={"clip": "c14", "region": "full", "dim": True}, elements=[
        {"type": "qcard", "slot": "upper", "question": "विश्व में पाइपलाइन परिवहन के कोई चार महत्व लिखिए।",
         "year": "2024", "marks": "3 अंक", "t_marks": [7, 0.8], "at": 6}])
    B(id="count4", **{"in": 9, "out": 11}, presenter="standard", elements=[
        {"type": "counter", "slot": "upper", "num": "4", "label": "महत्व, गिनकर लिखें", "at": 9}])
    B(id="what-flows", **{"in": 11, "out": 14}, presenter="standard", broll={"clip": "c14", "region": "full"}, elements=[
        {"type": "note", "slot": "over-broll-top", "text": "पहले: पाइप में बहता क्या है?", "at": 12},
        {"type": "stamp", "slot": "over-broll", "text": "answer अलग बनेगा", "at": 13}])
    flows = [["जल", WATER, A(38.28)], ["पेट्रोलियम", OIL, A(39.54)], ["प्राकृतिक गैस", GAS, A(40.54)],
             ["LPG", LPG, A(41.68)], ["कोयले का स्लरी", SLURRY, A(42.72)]]
    B(id="flows", **{"in": 14, "out": 16}, presenter="standard", elements=[
        {"type": "pipeflow", "slot": "upper", "title": "पाइप में क्या बहता है?", "items": flows}])
    B(id="slurry", **{"in": 16, "out": 18}, presenter="standard", broll={"clip": "c05", "region": "full"}, elements=[
        {"type": "def", "slot": "over-broll-top", "term": "स्लरी", "text": "कोयला + पानी", "at": 16},
        {"type": "note", "slot": "over-broll-low", "text": "ताकि ठोस कोयला भी बह सके", "at": 17}])
    B(id="nz", **{"in": 18, "out": 21}, presenter="standard", broll={"clip": "c06", "region": "full"}, elements=[
        {"type": "pill", "slot": "over-broll-top", "text": "न्यूज़ीलैंड", "style": "accent", "at": 18},
        {"type": "pills", "slot": "over-broll-low", "items": [["खेत → कारखाना", 19], ["दूध भी पाइप से!", 20]]}])
    B(id="nz-answer", **{"in": 21, "out": 23}, presenter="standard", elements=[
        {"type": "pipeflow", "slot": "upper", "title": "★ ये उदाहरण answer को दमदार बनाएगा",
         "items": [f[:2] + ["pre"] for f in flows] + [["दूध (न्यूज़ीलैंड)", MILK, 21, True]]}])
    B(id="first", **{"in": 23, "out": 25}, presenter="hub", hub={**HUB, "backdrop": "veo:c03@3"}, elements=[
        {"type": "headline", "slot": "head", "text": "अब चार महत्व", "size": "m", "at": 23},
        radial([24, 999, 999, 999], [24])])
    B(id="no-loading", **{"in": 25, "out": 30}, presenter="standard", broll={"clip": "c07", "region": "full"}, elements=[
        {"type": "section", "slot": "over-broll-top", "num": "1", "text": "समय और श्रम की बचत", "at": 25},
        {"type": "pills", "slot": "over-broll-low", "items": [["लगातार बहाव", [25, 1.5]], ["बार-बार लदान-उतराई नहीं", 27]]},
        {"type": "def", "slot": "over-broll", "term": "लदान", "text": "गाड़ी में माल चढ़ाना", "at": 29}])
    B(id="truck-vs-pipe", **{"in": 30, "out": 33}, presenter="standard", elements=[
        {"type": "yn", "slot": "upper", "no": "ट्रक: भरो → ले जाओ → खाली करो", "yes": "पाइप: बस एक बार चालू करो",
         "at": A(80.86), "t_yes": A(84.96)},
        {"type": "pill", "slot": "under-upper", "text": "समय भी बचा, मेहनत भी", "style": "accent", "at": 32}])
    B(id="first-done", **{"in": 33, "out": 34}, presenter="hub", hub={**HUB, "backdrop": "veo:c08@2"}, elements=[
        {"type": "headline", "slot": "head", "text": "पहला महत्व पक्का", "size": "m", "at": 33},
        radial([33, 999, 999, 999], [33])])
    B(id="continuous", **{"in": 34, "out": 36}, presenter="standard", broll={"clip": "c08", "region": "full"}, elements=[
        {"type": "section", "slot": "over-broll-top", "num": "2", "text": "निरंतर आपूर्ति", "at": A(98.38)},
        {"type": "note", "slot": "over-broll-low", "text": "लगातार बहने से ही", "at": 34}])
    B(id="steady", **{"in": 36, "out": 38}, presenter="standard", elements=[
        {"type": "pipeflow", "slot": "upper", "title": "बिना रुके, हर समय",
         "items": [["जल", WATER, A(100.66)], ["पेट्रोलियम", OIL, A(102.02)], ["प्राकृतिक गैस", GAS, A(102.56)]]},
        {"type": "pill", "slot": "under-upper", "text": "निरंतर + नियमित आपूर्ति", "style": "accent", "at": 37}])
    B(id="mains", **{"in": 38, "out": 39}, presenter="standard", broll={"clip": "c09", "region": "full"}, elements=[
        {"type": "note", "slot": "over-broll-top", "text": "सप्लाई बीच में टूटती नहीं", "at": 38}])
    B(id="two-words", **{"in": 39, "out": 41}, presenter="standard", elements=[
        {"type": "def", "slot": "head", "term": "निरंतर + नियमित", "text": "दोनों शब्द जोड़कर", "at": 39},
        {"type": "stamp", "slot": "upper", "text": "इस point की पहचान", "at": 40}])
    B(id="two-done", **{"in": 41, "out": 43}, presenter="hub", hub={**HUB, "backdrop": "veo:c09@3"}, elements=[
        {"type": "headline", "slot": "head", "text": "दो महत्व हो गए", "size": "m", "at": 41},
        radial([41, 41, 999, 999], [41, [42, 1.0]])])
    B(id="teaser", **{"in": 43, "out": "end"}, presenter="standard", broll={"clip": "c13", "region": "full", "dim": True}, elements=[
        {"type": "headline", "slot": "over-broll-top", "text": "असली फायदा: पैसा और पर्यावरण", "size": "m", "at": 43},
        {"type": "pill", "slot": "over-broll-low", "text": "बाकी दो: Part 2 में", "style": "accent", "at": 45}])
    return {"captions_from": 9, "spine": {**SPINE, "lit_at": [24, 35], "show_from": 9}, "beats": beats}


def part2():
    A = cues(2); beats = []; B = lambda **k: beats.append(k)
    B(id="recall", **{"in": 0, "out": 2}, presenter="hub", hub={**HUB, "backdrop": "veo:c14@3"}, elements=[
        {"type": "headline", "slot": "head", "text": "Part 1 में", "size": "m", "at": 0},
        radial([0, 0, 999, 999], [[1, 0.0], [1, 1.6]])])
    B(id="recall-flows", **{"in": 2, "out": 5}, presenter="standard", elements=[
        {"type": "pipeflow", "slot": "upper", "title": "पानी से लेकर दूध तक",
         "items": [["जल", WATER, [3, 0.3]], ["पेट्रोलियम", OIL, [3, 0.6]], ["प्राकृतिक गैस", GAS, [3, 0.9]],
                   ["LPG", LPG, [3, 1.2]], ["कोयले का स्लरी", SLURRY, [3, 1.5]], ["दूध (न्यूज़ीलैंड)", MILK, [3, 1.9], True]]},
        {"type": "pill", "slot": "under-upper", "text": "अब बाकी दो महत्व", "style": "accent", "at": 4}])
    B(id="cheap", **{"in": 5, "out": 8}, presenter="standard", broll={"clip": "c11", "region": "full"}, elements=[
        {"type": "section", "slot": "over-broll-top", "num": "3", "text": "किफायती और कुशल परिवहन", "at": 5},
        {"type": "pills", "slot": "over-broll-low", "style": "accent",
         "items": [["तरल", A(18.96)], ["गैसीय", A(19.46)]]},
        {"type": "pills", "slot": "over-broll", "items": [["किफायती", A(20.9)], ["कुशल", A(21.64)], ["सुरक्षित", A(22.58)]]}])
    B(id="meaning", **{"in": 8, "out": 10}, presenter="standard", elements=[
        {"type": "cards3", "slot": "upper", "items": [["किफायती = सस्ता", 8], ["कुशल = काम अच्छे से करने वाला", 9]]}])
    B(id="tankers", **{"in": 10, "out": 11}, presenter="standard", broll={"clip": "c10", "region": "full"}, elements=[
        {"type": "note", "slot": "over-broll-top", "text": "टैंकरों में, हज़ारों किलोमीटर", "at": 10}])
    B(id="tanker-vs-pipe", **{"in": 11, "out": 13}, presenter="standard", elements=[
        {"type": "compare", "slot": "upper", "left": ["टैंकर से", "महँगा, हादसे का खतरा"],
         "right": ["पाइप से", "सस्ता, खतरा कम"], "at": 11, "right_at": [11, 0.6]}])
    B(id="liquid-gas", **{"in": 13, "out": 17}, presenter="standard", elements=[
        {"type": "headline", "slot": "head", "text": "ध्यान दें", "size": "m", "at": 13},
        {"type": "yn", "slot": "upper", "no": "ठोस पदार्थ", "yes": "तरल और गैसीय पदार्थ", "at": 14, "t_yes": A(41.5)},
        {"type": "stamp", "slot": "under-upper", "text": "ये दोनों शब्द लिखें", "at": 16}])
    B(id="three-done", **{"in": 17, "out": 18}, presenter="hub", hub={**HUB, "backdrop": "veo:c11@3"}, elements=[
        {"type": "headline", "slot": "head", "text": "तीसरा भी समझ आ गया", "size": "m", "at": 17},
        radial([17, 17, 17, 999], [17, 17, [17, 0.5]])])
    B(id="green", **{"in": 18, "out": 20}, presenter="standard", broll={"clip": "c13", "region": "full"}, elements=[
        {"type": "stamp", "slot": "over-broll", "text": "सबसे बड़ा point", "at": 18},
        {"type": "section", "slot": "over-broll-top", "num": "4", "text": "पर्यावरण के अनुकूल", "at": [19, 2.4]}])
    B(id="smoke", **{"in": 20, "out": 23}, presenter="standard", broll={"clip": "c12", "region": "full"}, elements=[
        {"type": "pills", "slot": "over-broll-low", "items": [["सड़क-रेल: बार-बार आना-जाना", 20], ["कम गाड़ियाँ = कम धुआँ", 22]]}])
    B(id="sentence", **{"in": 23, "out": 28}, presenter="standard", elements=[
        {"type": "chain", "slot": "upper", "items": [["पाइपलाइन", 23], ["अपेक्षाकृत", A(66.64)],
                                                      ["पर्यावरण-अनुकूल", A(67.92)], ["परिवहन माध्यम", A(69.5)]]}])
    B(id="relatively", **{"in": 28, "out": 30}, presenter="standard", elements=[
        {"type": "def", "slot": "head", "term": "अपेक्षाकृत", "text": "बाकी साधनों की तुलना में", "at": 29},
        {"type": "stamp", "slot": "upper", "text": "ये शब्द ज़रूर लिखें", "at": 28}])
    B(id="one-sentence", **{"in": 30, "out": 35}, presenter="hub", hub={**HUB, "backdrop": "veo:c13@3"}, elements=[
        {"type": "headline", "slot": "head", "text": "चारों, एक वाक्य में", "size": "m", "at": 30},
        radial([30, 30, 30, 30], [A(82.34), A(83.24), A(84.4), A(85.84)])])
    B(id="marks", **{"in": 35, "out": 38}, presenter="standard", broll={"clip": "c03", "region": "full", "dim": True}, elements=[
        {"type": "pill", "slot": "over-broll-top", "text": "चारों महत्व + न्यूज़ीलैंड उदाहरण", "style": "accent", "at": 36},
        {"type": "stamp", "slot": "over-broll", "text": "3 नंबर पक्के", "at": 37}])
    B(id="notes", **{"in": 38, "out": 39}, presenter="hero", broll={"clip": "c11", "region": "full", "dim": True}, elements=[
        {"type": "pill", "slot": "head", "text": "पूरा format: Notes button", "style": "accent", "at": 38}])
    B(id="outro", **{"in": 39, "out": "end"}, presenter="hero", broll={"clip": "c14", "region": "full", "dim": True}, elements=[
        {"type": "note", "slot": "over-broll-top", "text": "सप्लाई की तरह, पढ़ाई भी लगातार", "at": 40}])
    return {"spine": {**SPINE, "pre_lit": 2, "lit_at": [5, 19], "show_from": 0}, "beats": beats}


shots = {"c01": "tap opened, water pours", "c02": "piped gas: blue flame", "c03": "Trans-Alaska-style pipeline, aerial",
         "c04": "pipeline construction", "c05": "coal slurry being made", "c06": "New Zealand dairy: milk pipes",
         "c07": "tanker loading at depot", "c08": "gas pumping station, steady gauges", "c09": "giant city water mains",
         "c10": "tanker convoy on highway", "c11": "pipeline terminal at dusk", "c12": "truck traffic exhaust smoke",
         "c13": "buried pipeline corridor, green farmland", "c14": "inside a giant pipe"}
(PROJ / "veo/shots.json").write_text(json.dumps(shots, indent=1))
for n, f in ((1, part1), (2, part2)):
    body = f()
    plan = {"_about": f"GEO-C7-SA-03 part {n}, blueprint look", "project": "geo-c7-sa-03", "part": n,
            "skin": "paper-editorial", "theme": "blueprint", "presenter_style": "card", "plate": "blueprint-pipeline-alaska", **body}
    out = ROOT / f"lab/kit_test/plan_geo_c7_sa_03_p{n}.json"
    out.write_text(json.dumps(plan, ensure_ascii=False, indent=1))
    print(out.name, len(body["beats"]), "beats")
