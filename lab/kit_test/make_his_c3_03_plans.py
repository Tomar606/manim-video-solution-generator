"""HIS-C3-SA-03 (महाभारत को प्रगतिशील/गतिशील ग्रंथ क्यों कहा गया है?): ganga look, two parts.

    python lab/kit_test/make_his_c3_03_plans.py  ->  plan_his_c3_sa_03_p{1,2}.json

The narration runs one analogy end to end: the Ganga leaves Gangotri as a thread and grows as rivers
join it, and the Mahabharata grew the same way (over a thousand years, into many languages, absorbing
local tales, retold in art).  So the picture follows the river: glacier → confluence → Varanasi, and
each reason lands as one more stream joining.  The answer builds across both parts.  Cues are
[line, seconds into it].
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ANSWER = ["महाभारत कोई स्थिर ग्रंथ नहीं, बल्कि समय के साथ लगातार बढ़ता और बदलता रहा, इसलिए यह <b>गतिशील ग्रंथ</b> है। मुख्य कारण:",
          "<b>हज़ारों वर्षों तक विकास:</b> इसकी रचना 1000 से अधिक वर्षों तक होती रही और नए श्लोक जुड़ते गए।",
          "<b>अनेक भाषाओं में अनुवाद:</b> संस्कृत तक सीमित नहीं; भारत की कई क्षेत्रीय भाषाओं में अनुवाद हुआ।",
          "<b>स्थानीय कथाओं का समावेश:</b> अलग-अलग क्षेत्रों की स्थानीय कहानियाँ इसमें जुड़ती गईं।",
          "<b>कला व साहित्य में प्रयोग:</b> नाटक, मूर्तिकला और फिल्मों के ज़रिए इसकी नई-नई व्याख्याएँ होती हैं।"]
NUMS = ["", "1.", "2.", "3.", "4."]
SPINE = ["हज़ार वर्ष", "अनुवाद", "स्थानीय कथाएँ", "कला व फिल्में"]
FULL = "उत्तर: महाभारत: गतिशील ग्रंथ"


def V(clip, **k):
    return {"clip": clip, "region": "full", **k}


def hero(kicker, text, at, sub=None, hl=None, fx="rise"):
    e = {"type": "hero", "slot": "upper", "kicker": kicker, "text": text, "at": at, "hl": hl or [], "fx": fx}
    if sub:
        e["sub"] = sub
    return e


def sheet(k, at, plate="gg-river", animate=True, title="उत्तर बन रहा है…"):
    return dict(presenter="standard", plate=plate, tracker=False, elements=[
        {"type": "answer", "slot": "upper", "title": title, "points": ANSWER, "nums": NUMS, "show": k,
         "animate_from": k - 1 if animate else k, "at": at, "gap": 0.45}])


# ============================== PART 1 ==============================
b1 = []
B = lambda **k: b1.append(k)
B(id="glacier", **{"in": 0, "out": 3}, presenter="standard", broll=V("g1"), elements=[
    {"type": "note", "slot": "over-broll-top", "text": "गंगोत्री: एक पतली-सी धारा", "at": [1, 1.0], "fx": "blur"}])
B(id="join", **{"in": 3, "out": 4}, presenter="standard", broll=V("g2"), elements=[
    {"type": "pill", "slot": "over-broll-low", "text": "रास्ते में नई नदियाँ मिलती गईं", "at": [3, 0.6]}])
B(id="vast", **{"in": 4, "out": 5}, presenter="standard", broll=V("g3"), elements=[
    {"type": "stamp", "slot": "over-broll", "text": "और विशाल बनती गई", "at": [4, 0.3], "fx": "zoom"}])
B(id="same", **{"in": 5, "out": 6}, presenter="standard", plate="gg-relief", elements=[
    hero("बस, महाभारत भी", "बिल्कुल ऐसा ही ग्रंथ", [5, 0.8], hl=["ऐसा"])])
B(id="question", **{"in": 6, "out": 9}, presenter="standard", plate="gg-devprayag", elements=[
    {"type": "qhero", "slot": "upper", "ribbon": "Board Exam PYQ", "at": 6, "years": [["2023", [6, 0.8]]],
     "question": "महाभारत को एक प्रगतिशील ग्रंथ क्यों कहा गया है? स्पष्ट कीजिए।", "hl": ["प्रगतिशील"],
     "t_card": [7, 0.0], "marks": "3 अंक", "t_marks": [8, 0.2]}])
B(id="word", **{"in": 9, "out": 12}, presenter="standard", plate="gg-river", elements=[
    {"type": "headline", "slot": "head", "text": "पहले एक ज़रूरी बात", "size": "m", "at": 9, "fx": "drop", "sfx": [[0.05, "hud-blip/back-blip"]]},
    {"type": "yn", "slot": "upper", "no": "सवाल में: प्रगतिशील", "yes": "किताब में: गतिशील ग्रंथ", "at": [10, 0.3], "t_yes": [11, 0.2]}])
B(id="meaning", **{"in": 12, "out": 15}, presenter="standard", broll=V("g3", offset=3), elements=[
    {"type": "pill", "slot": "over-broll-top", "text": "गतिशील = जो रुका न हो", "style": "accent", "at": [12, 0.4]},
    {"type": "pill", "slot": "over-broll-low", "text": "लगातार चलता और बदलता रहे", "at": [13, 0.3]}])
B(id="opening", **{"in": 15, "out": 18}, presenter="standard", plate="gg-razmnama", elements=[
    {"type": "headline", "slot": "head", "text": "answer की शुरुआत", "size": "m", "at": 15, "fx": "drop"},
    {"type": "paper", "slot": "upper", "text": "महाभारत स्थिर ग्रंथ नहीं, समय के साथ लगातार बढ़ता और बदलता रहा।", "texture": "kraft", "at": [16, 0.3]}])
B(id="ans0", **{"in": 18, "out": 20}, **sheet(1, 18))
B(id="r1", **{"in": 20, "out": 21}, presenter="standard", plate="gg-devprayag", elements=[
    hero("पहला कारण", "हज़ारों वर्षों तक विकास", [20, 1.2], hl=["हज़ारों"])])
B(id="scribes", **{"in": 21, "out": 22}, presenter="standard", broll=V("w1"), elements=[
    {"type": "pill", "slot": "over-broll-low", "text": "किसी एक समय में नहीं बना", "at": [21, 0.4]}])
B(id="thousand", **{"in": 22, "out": 24}, presenter="standard", broll=V("w2"), elements=[
    {"type": "pill", "slot": "over-broll-top", "text": "1000+ वर्षों तक लिखा जाता रहा", "style": "accent", "at": [22, 0.6]},
    {"type": "pill", "slot": "over-broll-low", "text": "नए-नए श्लोक जुड़ते गए", "at": [23, 0.3]}])
B(id="like-river", **{"in": 24, "out": 26}, presenter="standard", broll=V("g2", offset=3), elements=[
    {"type": "pills", "slot": "over-broll-low", "items": [["गंगा: धीरे-धीरे पानी", [24, 0.6]], ["महाभारत: धीरे-धीरे श्लोक", [25, 0.6]]]}])
B(id="timespan", **{"in": 26, "out": 29}, presenter="standard", plate="gg-razmnama", elements=[
    {"type": "headline", "slot": "head", "text": "ये समय-सीमा ज़रूर लिखना", "size": "m", "at": 26, "fx": "drop"},
    hero("समय-सीमा", "1000 से अधिक वर्ष", [26, 1.0], hl=["1000"]),
    {"type": "pill", "slot": "under-upper", "text": "= एक बार में नहीं बना", "style": "accent", "at": [27, 1.0]}])
B(id="generations", **{"in": 29, "out": 31}, presenter="standard", broll=V("w1", offset=3), elements=[
    {"type": "ask", "slot": "upper", "text": "हज़ार साल: कितनी पीढ़ियों के लेखक?", "at": [29, 0.4]}])
B(id="ans1", **{"in": 31, "out": 32}, **sheet(2, 31))
B(id="spread", **{"in": 32, "out": 35}, presenter="standard", broll=V("t1"), elements=[
    {"type": "pills", "slot": "over-broll-low", "items": [["समय में बढ़ा", [32, 0.6]], ["पूरे देश में फैला", [33, 0.4]], ["हर जगह कुछ नया लिया", [34, 0.3]]]}])
B(id="next", **{"in": 35, "out": "end"}, presenter="full", broll=V("g3", offset=5, dim=True), elements=[
    {"type": "stamp", "slot": "over-broll", "text": "बाकी 3 कारण: Part 2", "at": [35, 0.4], "fx": "zoom"}])

# ============================== PART 2 ==============================
b2 = []
B = lambda **k: b2.append(k)
B(id="recap", **{"in": 0, "out": 3}, **sheet(2, 0, animate=False))
B(id="across", **{"in": 3, "out": 4}, presenter="standard", broll=V("t1", offset=2), elements=[
    {"type": "note", "slot": "over-broll-top", "text": "अब: देश भर में कैसे फैला?", "at": [3, 0.3], "fx": "rise"}])
B(id="r2", **{"in": 4, "out": 5}, presenter="standard", plate="gg-razmnama", elements=[
    hero("दूसरा कारण", "अनेक भाषाओं में अनुवाद", [4, 1.0], hl=["अनुवाद"])])
B(id="sanskrit", **{"in": 5, "out": 7}, presenter="standard", plate="gg-razmnama", elements=[
    {"type": "pill", "slot": "upper", "text": "सिर्फ संस्कृत तक सीमित नहीं", "at": [5, 0.4]},
    {"type": "pill", "slot": "under-upper", "text": "कई क्षेत्रीय भाषाओं में अनुवाद", "style": "accent", "at": [6, 0.6]}])
B(id="states", **{"in": 7, "out": 9}, presenter="standard", broll=V("g3", offset=2), elements=[
    {"type": "pills", "slot": "over-broll-low", "items": [["गंगा: अलग-अलग राज्य", [7, 0.6]], ["महाभारत: अलग-अलग भाषाएँ", [8, 0.6]]]}])
B(id="langs", **{"in": 9, "out": 11}, presenter="standard", broll=V("t1", offset=4), elements=[
    {"type": "pills", "slot": "over-broll-low", "items": [["बंगाली", [9, 0.8]], ["तमिल", [9, 1.6]], ["मराठी", [9, 2.2]]]},
    {"type": "pill", "slot": "over-broll-top", "text": "हर भाषा में अपनी कहानी", "style": "accent", "at": [10, 0.3]}])
B(id="ans2", **{"in": 11, "out": 13}, **sheet(3, 11))
B(id="r3", **{"in": 13, "out": 14}, presenter="standard", plate="gg-devprayag", elements=[
    hero("तीसरा कारण", "स्थानीय कथाओं का समावेश", [13, 1.4], hl=["स्थानीय"])])
B(id="phad", **{"in": 14, "out": 16}, presenter="standard", broll=V("l1"), elements=[
    {"type": "pill", "slot": "over-broll-low", "text": "वहाँ की स्थानीय कहानियाँ जुड़ती गईं", "style": "accent", "at": [15, 0.3]}])
B(id="tributary", **{"in": 16, "out": 17}, presenter="standard", broll=V("g2"), elements=[
    {"type": "lottie", "src": "arrow-dashed", "x": 540, "y": 560, "w": 520, "colour": "#FFFFFF", "at": [16, 0.6]},
    {"type": "pill", "slot": "over-broll-low", "text": "जैसे छोटी नदियाँ गंगा में", "at": [16, 1.2]}])
B(id="ans3", **{"in": 17, "out": [17, 1.6]}, **sheet(4, 17))
B(id="still", **{"in": [17, 1.6], "out": 19}, presenter="standard", broll=V("a1"), elements=[
    {"type": "note", "slot": "over-broll-top", "text": "आज भी रुका नहीं", "at": [18, 0.3], "fx": "rise"}])
B(id="r4", **{"in": 19, "out": 20}, presenter="standard", plate="gg-relief", elements=[
    hero("आखिरी कारण", "कला और साहित्य में प्रयोग", [19, 0.2], hl=["कला"])])
B(id="arts", **{"in": 20, "out": [21, 0.6]}, presenter="standard", broll=V("a2"), elements=[
    {"type": "pills", "slot": "over-broll-low", "items": [["नाटक", [20, 0.8]], ["मूर्तिकला", [20, 1.6]], ["फिल्में", [20, 2.4]]]}])
B(id="films", **{"in": [21, 0.6], "out": 22}, presenter="standard", broll=V("a4"), elements=[
    {"type": "pill", "slot": "over-broll-low", "text": "नई-नई व्याख्याएँ", "style": "accent", "at": [21, 0.8]}])
B(id="tv", **{"in": 22, "out": 25}, presenter="standard", broll=V("a3"), elements=[
    {"type": "note", "slot": "over-broll-top", "text": "TV का धारावाहिक भी!", "at": [23, 0.3], "fx": "rise"},
    {"type": "pill", "slot": "over-broll-low", "text": "वो भी एक नई व्याख्या", "style": "accent", "at": [24, 0.3]}])
B(id="ans4", **{"in": 25, "out": 26}, **sheet(5, 25))
B(id="timeline", **{"in": 26, "out": 30}, presenter="standard", plate="gg-river", elements=[
    {"type": "headline", "slot": "head", "text": "चारों कारण, गंगा की धारा पर", "size": "m", "at": 26, "fx": "drop"},
    {"type": "notify", "slot": "upper", "items": [["1", "हज़ार वर्षों तक विकास", "", [26, 0.3]], ["2", "अलग-अलग भाषाओं में अनुवाद", "", [27, 0.3]],
                                                   ["3", "स्थानीय कथाओं का जुड़ना", "", [28, 0.3]], ["4", "नाटक, मूर्तिकला, फिल्में", "", [29, 0.4]]]}])
B(id="marks", **{"in": 30, "out": 32}, presenter="standard", broll=V("g3", offset=4, dim=True), elements=[
    hero("गतिशील शब्द + चारों कारण", "पूरे 3 नंबर पक्के", [31, 0.2], hl=["पक्के"])])
B(id="full", **{"in": 32, "out": 33}, presenter="hub", hub={"cx": 905, "cy": 1450, "r": 125, "scale": 0.58, "backdrop": "plate"},
  plate="gg-river", tracker=False, elements=[
    {"type": "answer", "slot": "upper", "title": FULL, "points": ANSWER, "nums": NUMS, "show": 5, "animate_from": 5, "at": 32, "top": 360},
    {"type": "pill", "slot": "head", "text": "पूरा format: Notes button", "style": "accent", "at": [32, 0.6]}])
B(id="outro", **{"in": 33, "out": "end"}, presenter="full", broll=V("o1"), elements=[
    {"type": "note", "slot": "over-broll-top", "text": "सिलेबस भी गंगा की तरह, बढ़ता चले", "at": [33, 0.4], "fx": "rise"}])

for n, beats, lit in ((1, b1, [20]), (2, b2, [0, 4, 13, 19])):
    plan = {"_about": __doc__.strip().splitlines()[0], "project": "his-c3-sa-03", "part": n, "captions_at": "bottom",
            "skin": "paper-editorial", "theme": "ganga", "presenter_style": "card", "plate": "gg-river",
            "spine": {"title": "महाभारत: गतिशील ग्रंथ", "items": SPINE, "lit_at": lit, "show_from": 9 if n == 1 else 0},
            "tracker": {"from": 9 if n == 1 else 0}, "beats": beats}
    (ROOT / f"lab/kit_test/plan_his_c3_sa_03_p{n}.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1))
    print(f"part {n}: {len(beats)} beats")
