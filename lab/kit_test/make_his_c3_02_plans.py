"""HIS-C3-SA-02 (प्राचीन काल में संपत्ति और महिलाओं की स्थिति): taala look, two parts.

    python lab/kit_test/make_his_c3_02_plans.py  ->  plan_his_c3_sa_02_p{1,2}.json

The narration opens on a contrast (a queen granting her own land, an ordinary woman who could not hide
a few coins) and closes on its own mnemonic, "तीन ताले और एक चाबी": three restrictions and one exception.
The look is that chest: rosewood and brass.  The answer builds across both parts; the official page
from the sheet is appended after the final render.  Cues are [line, seconds into it].
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ANSWER = ["प्राचीन भारत (<b>मनुस्मृति</b>) में महिलाओं के संपत्ति अधिकारों की स्थिति इन चार बिंदुओं से समझी जा सकती है:",
          "<b>पैतृक संपत्ति नहीं:</b> माता-पिता की संपत्ति पर केवल पुत्रों का अधिकार, बेटियों का नहीं।",
          "<b>केवल स्त्रीधन पर हक़:</b> विवाह के समय मिले उपहारों पर महिला का अधिकार; उस पर पति का दावा नहीं।",
          "<b>गुप्त संचय पर रोक:</b> पति की आज्ञा के बिना धन छिपाकर रखने की सख्त मनाही।",
          "<b>ऐतिहासिक अपवाद:</b> वाकाटक रानी प्रभावती गुप्त ज़मीन की मालकिन थीं और उन्होंने भूमि दान किया।"]
NUMS = ["", "1.", "2.", "3.", "4."]
SPINE = ["पैतृक संपत्ति नहीं", "सिर्फ स्त्रीधन", "संचय पर रोक", "अपवाद: प्रभावती गुप्त"]
FULL = "उत्तर: संपत्ति और महिलाओं की स्थिति"


def V(clip, **k):
    return {"clip": clip, "region": "full", **k}


def hero(kicker, text, at, sub=None, hl=None, fx="rise"):
    e = {"type": "hero", "slot": "upper", "kicker": kicker, "text": text, "at": at, "hl": hl or [], "fx": fx}
    if sub:
        e["sub"] = sub
    return e


def sheet(k, at, plate="ta-wood", animate=True, title="उत्तर बन रहा है…"):
    return dict(presenter="standard", plate=plate, tracker=False, elements=[
        {"type": "answer", "slot": "upper", "title": title, "points": ANSWER, "nums": NUMS, "show": k,
         "animate_from": k - 1 if animate else k, "at": at, "gap": 0.45}])


# ============================== PART 1 ==============================
b1 = []
B = lambda **k: b1.append(k)
B(id="queen", **{"in": 0, "out": 3}, presenter="standard", broll=V("q1"), elements=[
    {"type": "note", "slot": "over-broll-top", "text": "करीब 1500 साल पहले…", "at": [1, 0.3], "fx": "blur"},
    {"type": "pill", "slot": "over-broll-low", "text": "रानी: अपनी ज़मीन, खुद दान", "style": "accent", "at": [2, 0.6]}])
B(id="woman", **{"in": 3, "out": 6}, presenter="standard", broll=V("q2"), elements=[
    {"type": "pill", "slot": "over-broll-low", "text": "आम महिला: थोड़ा-सा पैसा भी नहीं बचा सकती", "at": [5, 0.2]}])
B(id="why", **{"in": 6, "out": 7}, presenter="standard", plate="ta-ajanta", elements=[
    {"type": "ask", "slot": "upper", "text": "एक ही समय में, इतना बड़ा फर्क क्यों?", "at": [6, 0.3]}])
B(id="question", **{"in": 7, "out": 11}, presenter="standard", plate="ta-wood", elements=[
    {"type": "qhero", "slot": "upper", "ribbon": "Board Exam PYQ", "at": 7, "years": [["2023", [7, 1.0]]],
     "question": "प्राचीन काल में संपत्ति के स्वामित्व के संदर्भ में महिलाओं की स्थिति की व्याख्या कीजिए।",
     "hl": ["संपत्ति", "महिलाओं"], "t_card": [9, 0.0], "marks": "3 अंक", "t_marks": [8, 0.3]}])
B(id="source", **{"in": 11, "out": 15}, presenter="standard", plate="ta-kraft", elements=[
    {"type": "headline", "slot": "head", "text": "पहली लाइन: आधार", "size": "m", "at": 11, "fx": "drop"},
    {"type": "paper", "slot": "upper", "text": "इसका आधार: मनुस्मृति", "texture": "crumpled", "at": [12, 0.3]},
    {"type": "lottie", "src": "circle-sketch", "x": 560, "y": 470, "w": 360, "colour": "#A3261B", "at": [12, 1.2]}])
B(id="four", **{"in": 15, "out": 19}, presenter="standard", plate="ta-wood", elements=[
    {"type": "headline", "slot": "head", "text": "चार points", "size": "m", "at": 15, "fx": "drop"},
    {"type": "cards3", "slot": "upper", "items": [["पाबंदी", [17, 0.2]], ["पाबंदी", [17, 0.6]], ["पाबंदी", [17, 1.0]], ["एक अपवाद", [17, 1.6]]]}])
B(id="p1", **{"in": 19, "out": 21}, presenter="standard", plate="ta-ajanta", elements=[
    hero("पहला point", "पैतृक संपत्ति नहीं", [20, 0.2], sub="माता-पिता की संपत्ति", hl=["नहीं"])])
B(id="sons", **{"in": 21, "out": 24}, presenter="standard", broll=V("m1"), elements=[
    {"type": "pill", "slot": "over-broll-top", "text": "मनुस्मृति: सिर्फ पुत्रों का अधिकार", "at": [22, 0.3]},
    {"type": "pills", "slot": "over-broll-low", "items": [["घर", [23, 0.6]], ["ज़मीन", [23, 1.8]], ["खेत", [23, 2.7]], ["सब बेटों को", [23, 3.1]]]}])
B(id="write-source", **{"in": 24, "out": 27}, presenter="standard", plate="ta-kraft", elements=[
    {"type": "yn", "slot": "upper", "no": "बेटियों को हक़ नहीं था", "yes": "मनुस्मृति के अनुसार बेटियों को हक़ नहीं था", "at": [24, 0.3], "t_yes": [26, 0.2]}])
B(id="ans1", **{"in": 27, "out": 28}, **sheet(2, 27))
B(id="ask2", **{"in": 28, "out": 29}, presenter="standard", broll=V("s2"), elements=[
    {"type": "ask", "slot": "upper", "text": "तो महिला के पास, अपना क्या था?", "at": [28, 0.3]}])
B(id="p2", **{"in": 29, "out": 30}, presenter="standard", plate="ta-ajanta", elements=[
    hero("दूसरा point", "केवल स्त्रीधन पर हक़", [29, 1.4], hl=["स्त्रीधन"])])
B(id="gifts", **{"in": 30, "out": 32}, presenter="standard", broll=V("s1"), elements=[
    {"type": "pill", "slot": "over-broll-low", "text": "स्त्रीधन = विवाह के समय मिले उपहार", "style": "accent", "at": [30, 0.8]}])
B(id="hers", **{"in": 32, "out": 34}, presenter="standard", broll=V("s2", offset=3), elements=[
    {"type": "stamp", "slot": "over-broll", "text": "पति का कोई दावा नहीं", "at": [33, 0.3], "fx": "zoom"}])
B(id="keyword", **{"in": 34, "out": 38}, presenter="standard", plate="ta-kraft", elements=[
    {"type": "headline", "slot": "head", "text": "सबसे ज़रूरी keyword", "size": "m", "at": 34, "fx": "drop", "sfx": [[0.05, "hud-blip/back-blip"]]},
    {"type": "paper", "slot": "upper", "text": "स्त्रीधन: पति का दावा नहीं", "texture": "crumpled", "at": [35, 0.3]},
    {"type": "lottie", "src": "tick-spark", "x": 820, "y": 600, "w": 460, "at": [37, 0.2]}])
B(id="ans2", **{"in": 38, "out": 40}, **sheet(3, 38))
B(id="more", **{"in": 40, "out": 43}, presenter="standard", broll=V("k1"), elements=[
    {"type": "pills", "slot": "over-broll-low", "items": [["एक और पाबंदी", [40, 0.4]], ["और वो रानी", [41, 0.6]]]}])
B(id="next", **{"in": 43, "out": "end"}, presenter="full", broll=V("q1", offset=4, dim=True), elements=[
    {"type": "stamp", "slot": "over-broll", "text": "बाकी 2 points: Part 2", "at": [43, 0.6], "fx": "zoom"}])

# ============================== PART 2 ==============================
b2 = []
B = lambda **k: b2.append(k)
B(id="recap", **{"in": 0, "out": 4}, **sheet(3, 0, animate=False))
B(id="savings", **{"in": 4, "out": 6}, presenter="standard", broll=V("q2"), elements=[
    {"type": "note", "slot": "over-broll-top", "text": "तीसरी पाबंदी: अपनी बचत पर भी", "at": [4, 0.3], "fx": "rise"}])
B(id="p3", **{"in": 6, "out": 8}, presenter="standard", plate="ta-ajanta", elements=[
    hero("तीसरा point", "गुप्त संचय पर रोक", [7, 0.0], sub="संचय = धन जोड़कर रखना", hl=["रोक"])])
B(id="husband", **{"in": 8, "out": 10}, presenter="standard", broll=V("g2"), elements=[
    {"type": "pill", "slot": "over-broll-low", "text": "पति की आज्ञा के बिना: सख्त मनाही", "style": "accent", "at": [9, 0.6]}])
B(id="aata", **{"in": 10, "out": 13}, presenter="standard", broll=V("g1"), elements=[
    {"type": "note", "slot": "over-broll-top", "text": "आज: आटे के डिब्बे में बचत", "at": [10, 1.0], "fx": "rise"},
    {"type": "pill", "slot": "over-broll-low", "text": "उस समय: ये भी मना", "at": [11, 0.6]}])
B(id="four-words", **{"in": 13, "out": 17}, presenter="standard", plate="ta-kraft", elements=[
    {"type": "headline", "slot": "head", "text": "ये चार शब्द ज़रूर लिखना", "size": "m", "at": 13, "fx": "drop"},
    {"type": "paper", "slot": "upper", "text": "पति की आज्ञा के बिना", "texture": "crumpled", "at": [13, 0.4]},
    {"type": "pill", "slot": "under-upper", "text": "बचत पर भी पति का नियंत्रण", "style": "accent", "at": [16, 0.2]}])
B(id="ans3", **{"in": 17, "out": 18}, **sheet(4, 17))
B(id="listen", **{"in": 18, "out": 19}, presenter="standard", broll=V("r1"), elements=[
    {"type": "note", "slot": "over-broll-top", "text": "आखिरी point, ध्यान से", "at": [18, 0.3], "fx": "rise"}])
B(id="p4", **{"in": 19, "out": 20}, presenter="standard", plate="ta-ajanta", elements=[
    hero("यही पूरे नंबर दिलाता है", "ऐतिहासिक अपवाद", [19, 2.4], hl=["अपवाद"])])
B(id="royal", **{"in": 20, "out": 22}, presenter="standard", broll=V("r1", offset=3), elements=[
    {"type": "pill", "slot": "over-broll-top", "text": "राजघरानों में नियम अलग", "at": [20, 0.3]},
    {"type": "pill", "slot": "over-broll-low", "text": "वाकाटक रानी प्रभावती गुप्त", "style": "accent", "at": [21, 0.4]}])
B(id="grant", **{"in": 22, "out": 24}, presenter="standard", broll=V("q1"), elements=[
    {"type": "pills", "slot": "over-broll-low", "items": [["ज़मीन की मालकिन", [22, 0.3]], ["भूमि दान भी किया", [23, 0.4]]]}])
B(id="same-queen", **{"in": 24, "out": 26}, presenter="standard", plate="ta-wood", elements=[
    {"type": "photo", "slot": "upper", "src": "history/c3/vakataka-copper-plate-1.jpg", "w": 860, "label": "ताम्रपत्र पर भूमि-दान का लेख (483 ई.)", "at": [24, 0.2]}])
B(id="dont-stop", **{"in": 26, "out": 29}, presenter="standard", plate="ta-kraft", elements=[
    {"type": "yn", "slot": "upper", "no": "सिर्फ तीन पाबंदियाँ", "yes": "पाबंदियाँ + प्रभावती गुप्त का उदाहरण", "at": [26, 0.4], "t_yes": [27, 0.6]}])
B(id="ans4", **{"in": 29, "out": [29, 1.4]}, **sheet(5, 29))
B(id="locks", **{"in": [29, 1.4], "out": 30}, presenter="standard", broll=V("k1"), elements=[
    {"type": "stamp", "slot": "over-broll", "text": "तीन ताले, एक चाबी", "at": [29, 1.5], "fx": "zoom"}])
B(id="mnemonic", **{"in": 30, "out": 35}, presenter="standard", plate="ta-wood", elements=[
    {"type": "notify", "slot": "upper", "items": [["1", "ताला: पैतृक संपत्ति नहीं", "", [30, 0.3]], ["2", "ताला: सिर्फ स्त्रीधन पर हक़", "", [31, 0.3]],
                                                   ["3", "ताला: पति की आज्ञा के बिना संचय नहीं", "", [32, 0.3]], ["★", "चाबी: रानी प्रभावती गुप्त", "ज़मीन की मालकिन", [33, 0.3]]]}])
B(id="full", **{"in": 35, "out": 38}, presenter="hub", hub={"cx": 905, "cy": 1450, "r": 125, "scale": 0.58, "backdrop": "plate"},
  plate="ta-wood", tracker=False, elements=[
    {"type": "answer", "slot": "upper", "title": FULL, "points": ANSWER, "nums": NUMS, "show": 5, "animate_from": 5, "at": 35, "top": 360},
    {"type": "pill", "slot": "head", "text": "पूरा format: Notes button", "style": "accent", "at": [38, 0.2]}])
B(id="notes", **{"in": 38, "out": 40}, presenter="hub", hub={"cx": 905, "cy": 1450, "r": 125, "scale": 0.58, "backdrop": "plate"},
  plate="ta-wood", tracker=False, elements=[
    {"type": "answer", "slot": "upper", "title": FULL, "points": ANSWER, "nums": NUMS, "show": 5, "animate_from": 5, "at": 38, "top": 360},
    {"type": "pill", "slot": "head", "text": "पूरा format: Notes button", "style": "accent", "at": 38}])
B(id="outro", **{"in": 40, "out": "end"}, presenter="full", broll=V("o1"), elements=[
    {"type": "note", "slot": "over-broll-top", "text": "90% की तैयारी पक्की", "at": [40, 0.4], "fx": "rise"}])

for n, beats, lit in ((1, b1, [20, 29]), (2, b2, [0, 0, 7, 19])):
    plan = {"_about": __doc__.strip().splitlines()[0], "project": "his-c3-sa-02", "part": n, "captions_at": "bottom",
            "skin": "paper-editorial", "theme": "taala", "presenter_style": "card", "plate": "ta-wood",
            "spine": {"title": "संपत्ति और महिलाएँ", "items": SPINE, "lit_at": lit, "show_from": 11 if n == 1 else 0},
            "tracker": {"from": 11 if n == 1 else 0}, "beats": beats}
    (ROOT / f"lab/kit_test/plan_his_c3_sa_02_p{n}.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1))
    print(f"part {n}: {len(beats)} beats")
