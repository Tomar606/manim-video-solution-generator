"""Hindi (Vitan, अतीत में दबे पाँव): मोहनजोदड़ो के घरों की विशेषताएँ — Instagram-first draft.

    python lab/kit_test/make_hin_mohenjodaro_plan.py  ->  plan_hin_mohenjodaro_p1.json

Edited for retention: a new picture every 2-4 s, the hook a time-portal shot, each of
the six features landing as LARGE hero text over its own Veo shot, captions pinned to
the bottom, and the promised "surprise" answer sheet held on screen at the end.
Theme 1 (harappa) over four real Mohenjo-daro backgrounds.  Cues: line index, or
[line, seconds into it].
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROJ = ROOT / "projects/hin-mohenjodaro"

SPINE = {"title": "मोहनजोदड़ो के घर: 6 विशेषताएँ",
         "items": ["पिछला भाग सड़क की ओर", "सामने सिर्फ मुख्य द्वार", "खिड़कियाँ दूसरी मंज़िल पर",
                   "आँगन के चारों ओर कमरे", "कतार में छोटे-बड़े घर", "जैसलमेर जैसी बनावट"],
         "lit_at": [20, 23, 28, 33, 42, 46], "show_from": 16}
YEARS = [["2022", [1, 2.3]], ["2023", [2, 0.0]], ["2025", [2, 0.7]]]
ANSWER = ["मकानों का पिछला भाग मुख्य सड़क की ओर होता था, सामने का नहीं।",
          "सामने की दीवार में केवल एक मुख्य द्वार होता था, उसमें खिड़की नहीं होती थी।",
          "खिड़कियाँ संभवतः ऊपरी (दूसरी) मंज़िल पर होती थीं।",
          "घर के भीतर आँगन होता था; बड़े घरों में उसके चारों ओर खिड़कियों वाले कमरे बने थे।",
          "छोटे-बड़े घर कतार में बने थे और उनकी बाहरी दीवारें लगभग एक जैसी थीं।",
          "घरों की बनावट राजस्थान के जैसलमेर के पारंपरिक घरों जैसी थी।"]


def sheet(k, at, plate):
    """the answer as it stands after point k: 1..k-1 already written, k writing in, the rest faint blanks"""
    return dict(presenter="standard", plate=plate, elements=[
        {"type": "answer", "slot": "upper", "title": "उत्तर बन रहा है…" if k < 6 else "उत्तर: मोहनजोदड़ो के घरों की विशेषताएँ",
         "points": ANSWER, "show": k, "animate_from": k - 1, "at": at, "gap": 0.45}])


def hero(n, text, at, sub=None, hl=None):
    e = {"type": "hero", "slot": "upper", "kicker": n, "text": text, "at": at, "hl": hl or []}
    if sub:
        e["sub"] = sub
    return e


beats = []
B = lambda **k: beats.append(k)
# ---- hook: the time-portal shot, the years stamping as he says them --------------------------
B(id="hook", **{"in": 0, "out": 4}, presenter="standard", broll={"clip": "hka", "region": "full"}, elements=[
    {"type": "qhero", "slot": "upper", "ribbon": "Board Exam PYQ", "at": [1, 0.4], "years": YEARS}])
B(id="2027", **{"in": 4, "out": 6}, presenter="standard", plate="mjd-seals", elements=[
    {"type": "qhero", "slot": "upper", "ribbon": "Board Exam PYQ", "at": 4,
     "years": [["2022", 4], ["2023", [4, 0.1]], ["2025", [4, 0.2]]], "next": "2027 में भी आ सकता है!", "t_next": [4, 0.6]}])
B(id="pakke", **{"in": 6, "out": 7}, presenter="standard", broll={"clip": "hkc", "region": "full", "dim": True}, elements=[
    hero("समझ लिया तो", "2 नंबर पक्के", [6, 2.0], hl=["पक्के"])])
B(id="surprise", **{"in": 7, "out": 10}, presenter="standard", broll={"clip": "l2", "region": "full"}, elements=[
    {"type": "stamp", "slot": "over-broll", "text": "END में SURPRISE", "at": [7, 1.4], "fx": "zoom"},
    {"type": "note", "slot": "over-broll-top", "text": "reel पूरी देखना", "at": 9, "fx": "rise"}])
# ---- the long intro, kept moving: a craft shot every few seconds ----------------------------
B(id="potter", **{"in": 10, "out": 12}, presenter="standard", broll={"clip": "l1", "region": "full"}, elements=[
    {"type": "pill", "slot": "over-broll-low", "text": "नंबर पक्के करने वाले Important Questions", "style": "accent", "at": 11}])
B(id="well", **{"in": 12, "out": 13}, presenter="standard", broll={"clip": "l3", "region": "full"}, elements=[
    {"type": "note", "slot": "over-broll-top", "text": "आसान + मज़ेदार", "at": 12, "fx": "blur"}])
B(id="beads", **{"in": 13, "out": 15}, presenter="standard", broll={"clip": "l4", "region": "full"}, elements=[])
B(id="question", **{"in": 15, "out": 16}, presenter="standard", plate="mjd-seals", elements=[
    {"type": "qhero", "slot": "upper", "ribbon": "Board Exam PYQ", "at": 15, "years": [["2022", 15], ["2023", [15, 0.1]], ["2025", [15, 0.2]]],
     "question": "मोहनजोदड़ो के घरों की क्या विशेषताएँ थीं?", "hl": ["मोहनजोदड़ो", "घरों"], "t_card": [15, 0.3],
     "marks": "2 अंक", "t_marks": [15, 3.0]}])
# ---- the walk ---------------------------------------------------------------------------------
B(id="walk", **{"in": 16, "out": 18}, presenter="standard", broll={"clip": "w3", "region": "full"}, elements=[
    {"type": "note", "slot": "over-broll-top", "text": "चलो, 4500 साल पीछे…", "at": 16, "fx": "blur"}])
B(id="street", **{"in": 18, "out": 19}, presenter="standard", broll={"clip": "hka", "region": "full", "offset": 4.2}, elements=[])
B(id="f1", **{"in": 19, "out": 21}, presenter="standard", broll={"clip": "w4", "region": "full"}, elements=[
    hero("पहली विशेषता", "पिछला भाग सड़क की ओर", [20, 0.0], sub="सामने वाला हिस्सा नहीं", hl=["पिछला"])])
B(id="ans1", **{"in": 21, "out": 22}, **sheet(1, 21, "mjd-lanes"))
B(id="f2", **{"in": 22, "out": 24}, presenter="standard", broll={"clip": "w5", "region": "full"}, elements=[
    {"type": "note", "slot": "over-broll-top", "text": "फिर अंदर जाएँ कहाँ से?", "at": 22, "fx": "rise"},
    hero("दूसरी विशेषता", "सिर्फ एक मुख्य द्वार", [23, 1.6], hl=["एक"])])
B(id="ans2", **{"in": 24, "out": 26}, **sheet(2, 24, "mjd-lanes"))
B(id="f3", **{"in": 26, "out": 29}, presenter="standard", broll={"clip": "w6", "region": "full"}, elements=[
    hero("तीसरी विशेषता", "खिड़कियाँ दूसरी मंज़िल पर", [28, 1.4], sub="(शायद)", hl=["दूसरी"])])
B(id="ans3", **{"in": 29, "out": 32}, **sheet(3, 29, "mjd-lanes"))
B(id="door-in", **{"in": 32, "out": 33}, presenter="standard", broll={"clip": "w7", "region": "full"}, elements=[
    {"type": "note", "slot": "over-broll-top", "text": "अब घर के अंदर →", "at": 32, "fx": "rise"}])
B(id="f4", **{"in": 33, "out": 36}, presenter="standard", broll={"clip": "w8", "region": "full"}, elements=[
    hero("चौथी विशेषता", "आँगन + चारों ओर कमरे", [33, 1.6], sub="कमरों में खिड़कियाँ", hl=["आँगन"])])
B(id="myth", **{"in": 36, "out": 39}, presenter="standard", plate="mjd-greatbath", elements=[
    {"type": "headline", "slot": "head", "text": "ध्यान दें: यहीं गलती होती है", "size": "m", "at": 36, "fx": "drop",
     "sfx": [[0.05, "hud-blip/back-blip"]]},
    {"type": "yn", "slot": "upper", "no": "घरों में खिड़कियाँ होती ही नहीं थीं", "yes": "आँगन वाले कमरों में खिड़कियाँ थीं", "at": 37, "t_yes": [38, 1.8]}])
B(id="window-view", **{"in": 39, "out": 40}, presenter="standard", broll={"clip": "w9", "region": "full"}, elements=[
    {"type": "pills", "slot": "over-broll-low", "items": [["सड़क वाली दीवार: खिड़की नहीं", 39], ["आँगन वाले कमरे: खिड़की हाँ", [39, 1.6]]]}])
B(id="ans4", **{"in": 40, "out": 41}, **sheet(4, 40, "mjd-greatbath"))
B(id="rise", **{"in": 41, "out": 42}, presenter="standard", broll={"clip": "hkc", "region": "full"}, elements=[
    {"type": "note", "slot": "over-broll-top", "text": "अब पूरी बस्ती…", "at": 41, "fx": "blur"}])
B(id="f5", **{"in": 42, "out": [43, 1.8]}, presenter="standard", broll={"clip": "w11", "region": "full"}, elements=[
    hero("पाँचवीं विशेषता", "कतार में छोटे-बड़े घर", [42, 1.0], sub="बाहरी दीवारें लगभग एक जैसी", hl=["कतार"])])
B(id="ans5", **{"in": [43, 1.8], "out": 45}, **sheet(5, [43, 1.8], "mjd-city"))
B(id="f6", **{"in": 45, "out": 47}, presenter="standard", broll={"clip": "w12", "region": "full"}, elements=[
    hero("छठी विशेषता", "जैसलमेर जैसी बनावट", [46, 0.6], sub="राजस्थान के पारंपरिक घर", hl=["जैसलमेर"])])
B(id="ans6", **{"in": 47, "out": 48}, **sheet(6, 47, "mjd-city"))
B(id="marks", **{"in": 48, "out": 49}, presenter="standard", broll={"clip": "w13", "region": "full", "dim": True}, elements=[
    hero("answer में ये सब लिखा तो", "पूरे 2 नंबर पक्के", [48, 1.2], hl=["पक्के"])])
B(id="answer", **{"in": 49, "out": "end"}, presenter="hub", hub={"cx": 905, "cy": 1450, "r": 125, "scale": 0.58, "backdrop": "plate"}, plate="mjd-city", elements=[
    {"type": "answer", "slot": "upper", "title": "उत्तर: मोहनजोदड़ो के घरों की विशेषताएँ", "points": ANSWER, "show": 6, "animate_from": 6, "at": [49, 1.6], "top": 400},
    {"type": "pills", "slot": "head", "style": "accent", "items": [["screenshot ले लो", 51], ["PDF: पहला comment", 52], ["save करो", [53, 1.0]], ["share करो", 55]]}])

plan = {"_about": __doc__.strip().splitlines()[0], "project": "hin-mohenjodaro", "part": 1, "captions_at": "bottom",
        "skin": "paper-editorial", "theme": "harappa", "presenter_style": "card", "plate": "mjd-city",
        "spine": SPINE, "beats": beats}
(ROOT / "lab/kit_test/plan_hin_mohenjodaro_p1.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1))
shots = {"hka": "time portal: ruins to living street", "hkb": "sand blows off the buried city", "hkc": "rising out of a courtyard over the city",
         "l1": "potter at the wheel", "l2": "kids racing a toy cart down a lane", "l3": "women at a brick well", "l4": "carnelian bead drilling",
         "w3": "walking the main street", "w4": "blank back walls + covered drain", "w5": "single main door, no window", "w6": "tilt up to upper-floor windows",
         "w7": "through the door into the courtyard", "w8": "courtyard with rooms all round", "w9": "from a room, out of the window to the courtyard",
         "w11": "aerial: rows of houses", "w12": "Jaisalmer lane today", "w13": "sunset over the ruins"}
(PROJ / "veo/shots.json").write_text(json.dumps(shots, indent=1))
print(len(beats), "beats")
