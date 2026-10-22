"""HIS-C2-SA-05 (मौर्य साम्राज्य के चार प्रमुख ऐतिहासिक स्रोत): edict look, one part.

    python lab/kit_test/make_his_c2_05_plan.py  ->  plan_his_c2_sa_05_p1.json

Real artefacts are PHOTOGRAPHS (Didarganj Yakshi, Sarnath capital, Kalsi edict):
a generated clip would invent the carving and fake the script.  Veo carries the
scenes around them.  Cues in seconds become [line, offset].
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROJ = ROOT / "projects/his-c2-sa-05"
L = json.loads((PROJ / "lines_part1.json").read_text())


def A(sec):
    i = max(k for k, l in enumerate(L) if l["start"] <= sec + 1e-6)
    return [i, round(sec - L[i]["start"], 2)]


PH = "history/mauryan/"
beats = []
B = lambda **k: beats.append(k)

B(id="phone", **{"in": 0, "out": 3}, presenter="standard", broll={"clip": "h01", "region": "full"}, elements=[
    {"type": "pill", "slot": "over-broll-low", "text": "आज: बस search कर लो", "style": "accent", "at": 2}])
B(id="court", **{"in": 3, "out": 4}, presenter="standard", broll={"clip": "h02", "region": "full"}, elements=[
    {"type": "note", "slot": "over-broll-top", "text": "मौर्य साम्राज्य", "at": 3},
    {"type": "stamp", "slot": "over-broll", "text": "करीब 2300 साल पुराना", "at": A(8.0)}])
B(id="how", **{"in": 4, "out": 5}, presenter="standard", broll={"clip": "h04", "region": "full", "dim": True}, elements=[
    {"type": "headline", "slot": "over-broll-top", "text": "इतिहासकारों को पता कैसे चला?", "size": "m", "at": 4}])
B(id="question", **{"in": 5, "out": 7}, presenter="small", broll={"clip": "h02", "region": "full", "dim": True, "offset": 3}, elements=[
    {"type": "qcard", "slot": "upper", "question": "मौर्य साम्राज्य के कोई चार प्रमुख ऐतिहासिक स्रोतों के नाम लिखिए।",
     "year": "2022", "marks": "3 अंक", "t_marks": [6, 1.5], "at": 5}])
B(id="names-plus", **{"in": 7, "out": 11}, presenter="standard", elements=[
    {"type": "yn", "slot": "upper", "no": "सिर्फ नाम", "yes": "नाम + एक लाइन का परिचय", "at": 7, "t_yes": 8},
    {"type": "pill", "slot": "under-upper", "text": "तब answer दमदार", "style": "accent", "at": A(26.9)}])
# ---- 1 archaeology ----------------------------------------------------------------------------
B(id="dig", **{"in": 11, "out": 13}, presenter="standard", broll={"clip": "h03", "region": "full"}, elements=[
    {"type": "section", "slot": "over-broll-top", "num": "1", "text": "पुरातात्विक स्रोत", "at": A(33.26)},
    {"type": "pill", "slot": "over-broll-low", "text": "ज़मीन की खुदाई से मिली चीज़ें", "at": A(34.62)}])
B(id="sculpture", **{"in": 13, "out": 15}, presenter="standard", elements=[
    {"type": "photo", "slot": "upper", "src": PH + "yakshi-3.jpg", "w": 430, "tilt": -2, "label": "दीदारगंज यक्षी", "at": A(38.72)},
    {"type": "photo", "slot": "over-broll-right", "src": PH + "lion-3.jpg", "w": 430, "tilt": 2, "label": "सारनाथ सिंह-शीर्ष", "at": A(40.0)},
    {"type": "note", "slot": "under-upper", "text": "मूर्तिकला पर विशेष बल: कला और सोच", "at": 14}])
B(id="half-done", **{"in": 15, "out": 18}, presenter="standard", broll={"clip": "h05", "region": "full"}, elements=[
    {"type": "stamp", "slot": "over-broll", "text": "मूर्तिकला लिखा = आधा काम", "at": 15},
    {"type": "note", "slot": "over-broll-low", "text": "पहला स्रोत: ज़मीन से", "at": 17}])
# ---- 2 contemporary writings ------------------------------------------------------------------
B(id="writings", **{"in": 18, "out": 20}, presenter="standard", broll={"clip": "h07", "region": "full"}, elements=[
    {"type": "section", "slot": "over-broll-top", "num": "2", "text": "समकालीन रचनाएँ", "at": A(55.38)},
    {"type": "pill", "slot": "over-broll-low", "text": "उसी समय लिखी गई किताबें", "at": A(57.44)}])
B(id="megasthenes", **{"in": 20, "out": 23}, presenter="standard", broll={"clip": "h06", "region": "full"}, elements=[
    {"type": "pills", "slot": "over-broll-low", "style": "accent", "items": [["मेगस्थनीज", A(62.74)], ["यूनानी राजदूत", A(64.72)]]},
    {"type": "note", "slot": "over-broll-top", "text": "चंद्रगुप्त मौर्य के दरबार में", "at": A(66.44)}])
B(id="indica", **{"in": 23, "out": 26}, presenter="standard", elements=[
    {"type": "def", "slot": "head", "term": "मेगस्थनीज", "text": "इंडिका", "at": A(70.36)},
    {"type": "stamp", "slot": "upper", "text": "ये जोड़ी याद रखें", "at": 24},
    {"type": "note", "slot": "under-upper", "text": "एक विदेशी की नज़र", "at": 25}])
# ---- 3 religious texts ------------------------------------------------------------------------
B(id="religious", **{"in": 26, "out": 28}, presenter="standard", broll={"clip": "h08", "region": "full"}, elements=[
    {"type": "section", "slot": "over-broll-top", "num": "3", "text": "धार्मिक ग्रंथ", "at": A(80.08)}])
B(id="three-texts", **{"in": 28, "out": 30}, presenter="standard", elements=[
    {"type": "headline", "slot": "head", "text": "किन ग्रंथों में?", "size": "m", "at": 28},
    {"type": "cards3", "slot": "upper", "items": [["जैन ग्रंथ", A(82.56)], ["बौद्ध ग्रंथ", A(83.26)], ["पौराणिक ग्रंथ", A(83.62)]]},
    {"type": "pill", "slot": "under-upper", "text": "मौर्य शासकों का उल्लेख", "style": "accent", "at": A(85.2)}])
B(id="all-three", **{"in": 30, "out": 32}, presenter="standard", broll={"clip": "h10", "region": "full"}, elements=[
    {"type": "stamp", "slot": "over-broll", "text": "तीनों नाम लिखें", "at": 30},
    {"type": "note", "slot": "over-broll-low", "text": "एक भी छूटा, बिन्दु कमज़ोर", "at": 31}])
# ---- 4 Ashoka's edicts ------------------------------------------------------------------------
B(id="special", **{"in": 32, "out": 33}, presenter="standard", broll={"clip": "h12", "region": "full"}, elements=[
    {"type": "stamp", "slot": "over-broll", "text": "सबसे खास", "at": A(95.6)}])
B(id="edict", **{"in": 33, "out": 34}, presenter="standard", elements=[
    {"type": "section", "slot": "head", "num": "4", "text": "अशोक के शिलालेख", "at": 33},
    {"type": "photo", "slot": "upper", "src": PH + "kalsi-3.jpg", "w": 760, "label": "कालसी का शिलालेख (उत्तराखंड)", "at": A(97.7)},
    {"type": "pill", "slot": "under-upper", "text": "= राज्यादेश", "style": "accent", "at": A(98.48)}])
B(id="carved", **{"in": 34, "out": 35}, presenter="standard", broll={"clip": "h11", "region": "full"}, elements=[
    {"type": "pill", "slot": "over-broll-low", "text": "पत्थरों पर लिखवाए गए राजा के आदेश", "style": "accent", "at": 34}])
B(id="herald", **{"in": 35, "out": 37}, presenter="standard", broll={"clip": "h13", "region": "full"}, elements=[
    {"type": "note", "slot": "over-broll-top", "text": "लिखित इतिहास में अनोखे", "at": 35},
    {"type": "stamp", "slot": "over-broll", "text": "राजा खुद अपनी बात कह रहा है", "at": 36}])
# ---- recall: four things -> four sources ------------------------------------------------------
B(id="four-things", **{"in": 37, "out": 42}, presenter="hub", hub={"cy": 980, "r": 200, "backdrop": "veo:h12@3"}, elements=[
    {"type": "headline", "slot": "head", "text": "चार चीज़ें, चार स्रोत", "size": "m", "at": 37},
    {"type": "quad", "slot": "full", "icons": ["tabler:shovel", "tabler:feather", "tabler:book", "tabler:crown"], "items": [
        ["पत्थर की मूर्ति", "पुरातात्विक स्रोत", A(114.34)], ["विदेशी की कलम", "समकालीन रचनाएँ", A(115.1)],
        ["धर्म की किताब", "धार्मिक ग्रंथ", A(115.98)], ["राजा का आदेश", "अशोक के शिलालेख", A(117.34)]]}])
B(id="marks", **{"in": 42, "out": 44}, presenter="standard", broll={"clip": "h12", "region": "full", "dim": True, "offset": 4}, elements=[
    {"type": "pill", "slot": "over-broll-top", "text": "चारों नाम + एक-एक लाइन परिचय", "style": "accent", "at": 42},
    {"type": "stamp", "slot": "over-broll", "text": "पूरे 3 नंबर आपके", "at": 43}])
B(id="notes", **{"in": 44, "out": 46}, presenter="hero", broll={"clip": "h02", "region": "full", "dim": True, "offset": 5}, elements=[
    {"type": "pill", "slot": "head", "text": "लिखने का तरीका: Notes button", "style": "accent", "at": 44}])
B(id="outro", **{"in": 46, "out": "end"}, presenter="hero", broll={"clip": "h01", "region": "full", "dim": True, "offset": 3}, elements=[
    {"type": "note", "slot": "over-broll-top", "text": "एक-एक topic, 90% की ओर", "at": 46}])

plan = {"_about": "HIS-C2-SA-05, edict look", "project": "his-c2-sa-05", "part": 1, "captions_from": 7,
        "skin": "paper-editorial", "theme": "edict", "presenter_style": "card", "plate": "edict-sandstone-girnar",
        "spine": {"title": "मौर्य साम्राज्य: 4 स्रोत", "items": ["पुरातात्विक स्रोत", "समकालीन रचनाएँ", "धार्मिक ग्रंथ", "अशोक के शिलालेख"],
                  "lit_at": [11, 19, 27, 33], "show_from": 7},
        "beats": beats}
(ROOT / "lab/kit_test/plan_his_c2_sa_05_p1.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1))
shots = {"h01": "student scrolling a phone at night", "h02": "Mauryan royal hall, Pataliputra", "h03": "archaeologist brushing a carved fragment",
         "h04": "large excavation, Gangetic plain", "h05": "polished sandstone statue in a museum", "h06": "Greek ambassador at the palace gates",
         "h07": "reed pen writing on a scroll by lamplight", "h08": "Buddhist monks chanting, palm-leaf bundles", "h09": "Jain monks walking at dawn",
         "h10": "priest unwrapping palm-leaf manuscripts", "h11": "stonemason carving grooves into a boulder", "h12": "polished pillar with lion, sunrise",
         "h13": "royal herald reading a proclamation to villagers", "h14": "student studying under a lamp"}
(PROJ / "veo/shots.json").write_text(json.dumps(shots, indent=1))
print(len(beats), "beats")
