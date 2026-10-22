"""POL-C1-SA-02 (शॉक थेरेपी क्या थी? क्या यह सबसे बेहतर तरीका था?): case-file look, two parts.

    python lab/kit_test/make_pol_c1_02_plans.py  ->  plan_pol_c1_sa_02_p{1,2}.json

The narration tells it as a treatment — patient, illness, doctor, medicine, side
effects — so the answer is a ℞ case sheet that BUILDS across both parts, one line each
time a point lands (the Hindi Mohenjo-daro pattern).  Backgrounds are real photos
(Kremlin, World Bank, a derelict Soviet plant, 1990 rouble coins); the metaphors are
shot in India (a town clinic, a kabadiwala) so students recognise them.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROJ = ROOT / "projects/pol-c1-sa-02"

POINTS = ["मरीज़: 1991 के बाद रूस, पूर्वी यूरोप और मध्य एशिया",
          "बीमारी: साम्यवाद से पूँजीवाद की ओर बदलाव",
          "डॉक्टर: IMF (अंतर्राष्ट्रीय मुद्रा कोष) और विश्व बैंक",
          "दवा: शॉक थेरेपी, यानी एक ही झटके में बदलाव",
          "क्या सबसे बेहतर तरीका था? नहीं",
          "आर्थिक तबाही: 90% उद्योग औने-पौने दाम पर बिके (गैराज सेल)",
          "रूबल गिरा, महँगाई बढ़ी, लोगों की जमापूँजी डूबी",
          "सामाजिक कल्याण का अंत: सब्सिडी बंद, अमीर-गरीब की खाई बढ़ी"]
SPINE = {"title": "शॉक थेरेपी: इलाज की कहानी", "items": ["मरीज़", "डॉक्टर", "दवा", "Side effects"]}


def sheet(show, at, plate, a0=None, title=None):
    return dict(presenter="standard", plate=plate, elements=[
        {"type": "answer", "slot": "upper", "title": title or ("Case File: उत्तर बन रहा है" if show < 8 else "Case File: पूरा उत्तर"),
         "points": POINTS, "show": show, "animate_from": show - 1 if a0 is None else a0, "at": at, "gap": 0.45}])


def hero(kicker, text, at, sub=None, hl=None, sfx=None):
    e = {"type": "hero", "slot": "upper", "kicker": kicker, "text": text, "at": at, "hl": hl or []}
    if sub:
        e["sub"] = sub
    if sfx:
        e["sfx"] = sfx
    return e


ZAP = [[0.05, "hud-blip/electric-glitch"]]


def part1():
    beats = []; B = lambda **k: beats.append(k)
    B(id="hook", **{"in": 0, "out": 3}, presenter="standard", broll={"clip": "r06", "region": "full"}, elements=[
        {"type": "qhero", "slot": "upper", "ribbon": "Board Exam PYQ", "at": [1, 0.0], "years": [["2025", [1, 0.3]]],
         "marks": "3 अंक", "t_marks": [2, 1.4], "sfx": ZAP}])
    B(id="question", **{"in": 3, "out": 6}, presenter="standard", plate="st-kremlin", elements=[
        {"type": "qhero", "slot": "upper", "ribbon": "Board Exam PYQ", "at": 3, "years": [["2025", 3]], "qsize": 52,
         "question": "शॉक थेरेपी क्या थी? क्या साम्यवाद से पूँजीवाद की ओर संक्रमण का यह सबसे बेहतर तरीका था?",
         "hl": ["शॉक", "थेरेपी", "बेहतर"], "t_card": [3, 0.2], "marks": "3 अंक", "t_marks": [5, 0.6]}])
    B(id="spoon", **{"in": 6, "out": 8}, presenter="standard", broll={"clip": "r14", "region": "full"}, elements=[
        {"type": "pill", "slot": "over-broll-low", "text": "थोड़ी-थोड़ी दवा", "style": "accent", "at": 7}])
    B(id="bottle", **{"in": 8, "out": 11}, presenter="standard", broll={"clip": "r01", "region": "full"}, elements=[
        {"type": "note", "slot": "over-broll-top", "text": "एक ही दिन में पूरी बोतल!", "at": 8, "fx": "zoom"},
        {"type": "pills", "slot": "over-broll-low", "items": [["मरीज़ ठीक होगा?", 9], ["या हालत बिगड़ेगी?", 10]]}])
    B(id="1991", **{"in": 11, "out": 12}, presenter="standard", broll={"clip": "r02", "region": "full"}, elements=[
        {"type": "stamp", "slot": "over-broll", "text": "1991 के बाद: रूस", "at": [11, 0.6]}])
    B(id="story", **{"in": 12, "out": 17}, presenter="standard", plate="st-kremlin", elements=[
        {"type": "headline", "slot": "head", "text": "एक इलाज की कहानी", "size": "m", "at": 12, "fx": "drop"},
        {"type": "tiles", "slot": "upper", "cols": 2, "items": [["tabler:bed", "मरीज़", 14], ["tabler:stethoscope", "डॉक्टर", [14, 1.0]],
                                                              ["tabler:pill", "दवा", [14, 2.0]], ["tabler:alert-triangle", "Side effects", 15]]}])
    B(id="breakup", **{"in": 17, "out": 21}, presenter="standard", broll={"clip": "r03", "region": "full"}, elements=[
        {"type": "note", "slot": "over-broll-top", "text": "1991: सोवियत संघ का विघटन", "at": 18, "fx": "blur"},
        {"type": "pill", "slot": "over-broll-low", "text": "टूटकर कई अलग देश", "style": "accent", "at": 20}])
    B(id="patient", **{"in": 21, "out": 23}, presenter="standard", plate="st-kremlin", elements=[
        hero("मरीज़", "रूस · पूर्वी यूरोप · मध्य एशिया", [21, 0.4], sub="तीनों नाम answer में ज़रूर", hl=["रूस"])])
    B(id="ans1", **{"in": 23, "out": 25}, **sheet(1, 23, "st-kremlin"))
    B(id="illness", **{"in": 25, "out": 27}, presenter="standard", broll={"clip": "r04", "region": "full"}, elements=[
        {"type": "note", "slot": "over-broll-top", "text": "बीमारी क्या थी?", "at": 25, "fx": "rise"},
        {"type": "pill", "slot": "over-broll-low", "text": "साम्यवाद → पूँजीवाद", "style": "accent", "at": 26}])
    B(id="two-systems", **{"in": 27, "out": 29}, presenter="standard", plate="st-factory", elements=[
        {"type": "cards3", "slot": "upper", "items": [["साम्यवाद: संपत्ति और उद्योग सरकार के हाथ", 27], ["पूँजीवाद: संपत्ति और उद्योग निजी हाथों में", 28]]}])
    B(id="ans2", **{"in": 29, "out": 30}, **sheet(2, 29, "st-factory"))
    B(id="doctors", **{"in": 30, "out": 32}, presenter="standard", broll={"clip": "r05", "region": "full"}, elements=[
        hero("डॉक्टर", "IMF + विश्व बैंक", [31, 0.3], sub="अंतर्राष्ट्रीय मुद्रा कोष", hl=["IMF"])])
    B(id="model", **{"in": 32, "out": 34}, presenter="standard", plate="st-worldbank", elements=[
        hero("इनका बताया मॉडल =", "शॉक थेरेपी", [33, 1.0], hl=["शॉक"], sfx=ZAP)])
    B(id="jolt", **{"in": 34, "out": 36}, presenter="standard", plate="st-worldbank", elements=[
        {"type": "yn", "slot": "upper", "no": "धीरे-धीरे बदलाव", "yes": "एक ही झटके में बदलाव", "at": 34, "t_yes": 35, "sfx": [[1.9, "hud-blip/electric-glitch"]]}])
    B(id="ans4", **{"in": 36, "out": 39}, **sheet(4, 36, "st-worldbank", a0=2, title="Case File: परिभाषा तैयार"))
    B(id="part-two", **{"in": 39, "out": 41}, presenter="standard", plate="st-kremlin", elements=[
        {"type": "headline", "slot": "head", "text": "सवाल का दूसरा हिस्सा", "size": "m", "at": 39, "fx": "drop"},
        {"type": "note", "slot": "upper", "text": "क्या ये सबसे बेहतर तरीका था?", "at": 40, "fx": "rise"}])
    B(id="no", **{"in": 41, "out": 42}, presenter="standard", plate="st-kremlin", elements=[
        hero("जवाब", "नहीं", [41, 0.6], hl=["नहीं"], sfx=[[0.1, "stamp/soft-thud-a"]])])
    B(id="ans5", **{"in": 42, "out": 44}, **sheet(5, 42, "st-factory"))
    B(id="teaser", **{"in": 44, "out": "end"}, presenter="standard", broll={"clip": "r07", "region": "full", "dim": True}, elements=[
        {"type": "pill", "slot": "over-broll-top", "text": "3 side effects", "style": "accent", "at": 44},
        {"type": "stamp", "slot": "over-broll", "text": "Part 2 में", "at": [44, 0.8]}])
    return {"captions_at": "bottom", "spine": {**SPINE, "lit_at": [21, 30, 33], "show_from": 12}, "beats": beats}


def part2():
    beats = []; B = lambda **k: beats.append(k)
    B(id="so-far", **{"in": 0, "out": 6}, **sheet(5, 0, "st-kremlin", a0=5, title="Part 1 तक का उत्तर"))
    B(id="se1", **{"in": 6, "out": 7}, presenter="standard", broll={"clip": "r07", "region": "full"}, elements=[
        hero("Side effect 1", "आर्थिक तबाही", [6, 1.4], hl=["तबाही"])])
    B(id="ninety", **{"in": 7, "out": 10}, presenter="standard", plate="st-factory", elements=[
        {"type": "pill", "slot": "head", "text": "पूरा औद्योगिक ढाँचा ढह गया", "at": 7, "fx": "rise"},
        {"type": "counter", "slot": "upper", "num": "90%", "label": "उद्योग, बहुत कम दाम पर निजी हाथों में", "at": [8, 0.6]}])
    B(id="garage", **{"in": 10, "out": 13}, presenter="standard", broll={"clip": "r15", "region": "full"}, elements=[
        hero("इसे कहा गया", "सबसे बड़ी गैराज सेल", [10, 1.0], sub="कीमती सामान, औने-पौने दाम", hl=["गैराज"])])
    B(id="ans6", **{"in": 13, "out": 14}, **sheet(6, 13, "st-factory"))
    B(id="se2", **{"in": 14, "out": 15}, presenter="standard", broll={"clip": "r09", "region": "full"}, elements=[
        hero("Side effect 2", "गरीबी + मुद्रास्फीति", [14, 0.8], hl=["मुद्रास्फीति"])])
    B(id="queue", **{"in": 15, "out": 18}, presenter="standard", broll={"clip": "r10", "region": "full"}, elements=[
        {"type": "pills", "slot": "over-broll-low", "items": [["रूबल में भारी गिरावट", 15], ["महँगाई बढ़ी", 16], ["जमापूँजी खत्म", 17]]}])
    B(id="chain", **{"in": 18, "out": 20}, presenter="standard", plate="st-roubles", elements=[
        {"type": "headline", "slot": "head", "text": "एक कड़ी में याद रखो", "size": "m", "at": 18},
        {"type": "chain", "slot": "upper", "items": [["रूबल गिरा", [18, 1.6]], ["महँगाई बढ़ी", [18, 2.7]], ["बचत डूब गई", 19]]}])
    B(id="ans7", **{"in": 20, "out": 21}, **sheet(7, 20, "st-roubles"))
    B(id="se3", **{"in": 21, "out": 23}, presenter="standard", broll={"clip": "r11", "region": "full"}, elements=[
        hero("Side effect 3", "सामाजिक कल्याण का अंत", [22, 0.2], hl=["अंत"])])
    B(id="welfare", **{"in": 23, "out": 26}, presenter="standard", plate="st-kremlin", elements=[
        {"type": "cards3", "slot": "upper", "items": [["सरकारी सब्सिडी खत्म", 23], ["सरकार की मदद बंद", 24], ["समाज कल्याण की व्यवस्था टूटी", 25]]}])
    B(id="gap", **{"in": 26, "out": 27}, presenter="standard", broll={"clip": "r12", "region": "full"}, elements=[
        {"type": "pill", "slot": "over-broll-low", "text": "अमीर-गरीब की खाई और चौड़ी", "style": "accent", "at": 26}])
    B(id="ans8", **{"in": 27, "out": 28}, **sheet(8, 27, "st-worldbank"))
    B(id="revise", **{"in": 28, "out": 39}, presenter="hub", hub={"cy": 980, "r": 200, "backdrop": "veo:r05@3"}, plate="st-kremlin", elements=[
        {"type": "headline", "slot": "head", "text": "पूरी कहानी, एक नज़र में", "size": "m", "at": 28},
        {"type": "quad", "slot": "full", "icons": ["tabler:bed", "tabler:stethoscope", "tabler:pill", "tabler:alert-triangle"], "items": [
            ["मरीज़", "रूस, पूर्वी यूरोप, मध्य एशिया", 28], ["डॉक्टर", "IMF और विश्व बैंक", 31],
            ["दवा", "एक झटके में बदलाव = शॉक थेरेपी", 33], ["Side effects", "तबाही · महँगाई · कल्याण का अंत", 35]]}])
    B(id="marks", **{"in": 39, "out": 42}, presenter="standard", plate="st-worldbank", elements=[
        hero("परिभाषा + 'नहीं' + 3 दुष्परिणाम", "पूरे 3 नंबर पक्के", [41, 0.2], hl=["पक्के"])])
    B(id="notes", **{"in": 42, "out": 44}, presenter="standard", plate="st-kremlin", elements=[
        {"type": "pill", "slot": "head", "text": "सही format: Notes button", "style": "accent", "at": 42, "fx": "drop"}])
    B(id="outro", **{"in": 44, "out": "end"}, presenter="standard", broll={"clip": "r16", "region": "full"}, elements=[
        {"type": "note", "slot": "over-broll-top", "text": "हर topic पूरा करते जाओ", "at": 44, "fx": "blur"}])
    return {"captions_at": "bottom", "spine": {**SPINE, "pre_lit": 3, "lit_at": [6], "show_from": 0}, "beats": beats}


shots = {"r01": "doctor empties a whole bottle for a patient", "r02": "Soviet flag lowered over the Kremlin, 1991",
         "r03": "Moscow crowds with tricolour flags, 1991", "r04": "state-owned Soviet factory floor", "r05": "bankers around a table",
         "r06": "a lever pulled: sparks, lights out (shock)", "r07": "abandoned Soviet factory in winter", "r08": "garage sale (western)",
         "r09": "old woman counting worthless notes", "r10": "winter queue, empty shelves", "r11": "pensioners selling belongings",
         "r12": "rich man by a luxury car, poor man at a bin", "r13": "student at a desk", "r14": "Indian clinic: one spoon of syrup",
         "r15": "Indian family selling furniture to a kabadiwala", "r16": "Indian teen on a rooftop at sunset"}
(PROJ / "veo/shots.json").write_text(json.dumps(shots, indent=1, ensure_ascii=False))
for n, f in ((1, part1), (2, part2)):
    body = f()
    plan = {"_about": f"POL-C1-SA-02 part {n}, case-file look", "project": "pol-c1-sa-02", "part": n,
            "skin": "paper-editorial", "theme": "rx", "presenter_style": "card", "plate": "st-kremlin", **body}
    (ROOT / f"lab/kit_test/plan_pol_c1_sa_02_p{n}.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1))
    print(f"part {n}: {len(body['beats'])} beats")
