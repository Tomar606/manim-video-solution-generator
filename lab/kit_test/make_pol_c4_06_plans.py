"""POL-C4-LA-06 (UN के प्रमुख अंग व उद्देश्य): charter look, two parts.

    python lab/kit_test/make_pol_c4_06_plans.py  ->  plan_pol_c4_la_06_p{1,2}.json

The 1945 Charter as the motif (POL-C4-LA-05 already used UN blue and the HQ tower).  The
narration carries its own memory hooks, and each becomes a picture: school → hospital → UN
("बनी किसलिए?"); "एक सभा, तीन परिषद, एक अदालत, एक दफ़्तर"; "बनाए रखना, हटाना, दबाना"; and
"शान्ति, दोस्ती, सहयोग, तालमेल".  The answer builds across both parts; the official page from
the sheet is appended after the final render.  Cues are seconds on the word clock, turned into
[line, offset].
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROJ = ROOT / "projects/pol-c4-la-06"

ANSWER = ["<b>प्रमुख अंग:</b> महासभा, सुरक्षा परिषद, आर्थिक एवं सामाजिक परिषद, अन्तर्राष्ट्रीय न्यायालय, न्यास परिषद और सचिवालय।",
          "<b>युद्ध एवं विवादों का शान्तिपूर्ण समाधान:</b> शान्ति व सुरक्षा बनाए रखना, शान्ति विरोधी तत्वों को हटाना, आक्रामक कृत्यों का दमन।",
          "<b>समानाधिकार एवं आत्मनिर्णय:</b> इन आधारों पर देशों में मैत्रीपूर्ण संबंधों का विकास।",
          "<b>विभिन्न समस्याओं का समाधान:</b> अन्तर्राष्ट्रीय सहयोग, और मानवाधिकारों का सम्मान।",
          "<b>समन्वय की स्थापना:</b> देशों में तालमेल के लिए एक केन्द्र की स्थापना।"]
NUMS = ["", "1.", "2.", "3.", "4."]
SPINE = ["छह अंग", "शान्ति", "दोस्ती", "सहयोग", "तालमेल"]
FULL = "उत्तर: UN के अंग व उद्देश्य"


def cue_fn(n):
    L = json.loads((PROJ / f"lines_part{n}.json").read_text())

    def A(sec):
        i = max(k for k, l in enumerate(L) if l["start"] <= sec + 1e-6)
        return [i, round(sec - L[i]["start"], 2)]
    return A


def V(clip, **k):
    return {"clip": clip, "region": "full", **k}


def hero(kicker, text, at, sub=None, hl=None, fx="rise"):
    e = {"type": "hero", "slot": "upper", "kicker": kicker, "text": text, "at": at, "hl": hl or [], "fx": fx}
    if sub:
        e["sub"] = sub
    return e


def sheet(k, at, plate, animate=True, title="उत्तर बन रहा है…"):
    return dict(presenter="standard", plate=plate, tracker=False, elements=[
        {"type": "answer", "slot": "upper", "title": title, "points": ANSWER, "nums": NUMS, "show": k,
         "animate_from": k - 1 if animate else k, "at": at, "gap": 0.45}])


# ============================== PART 1 ==============================
A = cue_fn(1)
b1 = []
B = lambda **k: b1.append(k)
B(id="world", **{"in": 0, "out": 1}, presenter="standard", broll=V("h3"), elements=[
    {"type": "qmarks", "at": A(0.4), "n": 8}])
B(id="why", **{"in": 1, "out": 3}, presenter="standard", broll=V("h3", offset=3), elements=[
    {"type": "ask", "slot": "upper", "text": "कोई भी संस्था बनी किसलिए?", "at": A(3.9)}])
B(id="school", **{"in": 3, "out": 4}, presenter="standard", broll=V("h1"), elements=[
    {"type": "pill", "slot": "over-broll-low", "text": "स्कूल → पढ़ाने के लिए", "at": A(7.6)}])
B(id="hospital", **{"in": 4, "out": 5}, presenter="standard", broll=V("h2"), elements=[
    {"type": "pill", "slot": "over-broll-low", "text": "अस्पताल → इलाज के लिए", "at": A(9.7)}])
B(id="un-why", **{"in": 5, "out": 6}, presenter="standard", plate="ch-charter", elements=[
    {"type": "ask", "slot": "upper", "text": "संयुक्त राष्ट्र संघ → किसलिए?", "at": A(11.2)}])
B(id="question", **{"in": 6, "out": 12}, presenter="standard", plate="ch-council", elements=[
    {"type": "qhero", "slot": "upper", "ribbon": "Board Exam PYQ", "at": 6, "years": [["2022", A(15.3)]],
     "question": "संयुक्त राष्ट्र संघ के प्रमुख अंगों के नाम लिखिए व उसके उद्देश्य समझाइए।", "hl": ["अंगों", "उद्देश्य"],
     "t_card": A(21.2), "marks": "4 अंक", "t_marks": A(17.4)}])
# ---- part one of the question: the six organs (captions start here) ----------------------------
B(id="six", **{"in": 12, "out": 15}, presenter="standard", plate="ch-council", elements=[
    {"type": "headline", "slot": "head", "text": "पहले: कुल छह अंग", "size": "m", "at": 12, "fx": "drop"},
    {"type": "notify", "slot": "upper", "items": [["1", "महासभा", "", A(30.3)], ["2", "सुरक्षा परिषद", "", A(31.4)],
                                                   ["3", "आर्थिक एवं सामाजिक परिषद", "", A(32.8)], ["4", "अन्तर्राष्ट्रीय न्यायालय", "", A(34.8)],
                                                   ["5", "न्यास परिषद", "", A(36.2)], ["6", "सचिवालय", "", A(37.5)]]}])
B(id="trick", **{"in": 15, "out": 17}, presenter="standard", plate="ch-mural", elements=[
    {"type": "headline", "slot": "head", "text": "याद रखने का आसान तरीका", "size": "m", "at": 15, "fx": "drop"},
    {"type": "cards3", "slot": "upper", "items": [["एक सभा", A(41.0)], ["तीन परिषद", A(41.9)], ["एक अदालत", A(43.0)], ["एक दफ़्तर", A(44.1)]]}])
B(id="sabha", **{"in": 17, "out": A(47.3)}, presenter="standard", broll=V("o1"), elements=[
    {"type": "pill", "slot": "over-broll-low", "text": "एक सभा = महासभा", "style": "accent", "at": A(46.0)}])
B(id="parishad", **{"in": A(47.3), "out": 18}, presenter="standard", plate="ch-council", elements=[
    {"type": "headline", "slot": "head", "text": "तीन परिषद", "size": "m", "at": A(47.3)},
    {"type": "pills", "slot": "upper", "items": [["सुरक्षा परिषद", A(48.2)], ["आर्थिक-सामाजिक परिषद", A(49.5)], ["न्यास परिषद", A(50.3)]]}])
B(id="adalat", **{"in": 18, "out": A(53.6)}, presenter="standard", broll=V("o2"), elements=[
    {"type": "pill", "slot": "over-broll-low", "text": "एक अदालत = अन्तर्राष्ट्रीय न्यायालय", "style": "accent", "at": A(51.9)}])
B(id="daftar", **{"in": A(53.6), "out": 19}, presenter="standard", broll=V("o3"), elements=[
    {"type": "pill", "slot": "over-broll-low", "text": "एक दफ़्तर = सचिवालय", "style": "accent", "at": A(54.6)}])
B(id="half-done", **{"in": 19, "out": 21}, presenter="standard", plate="ch-peacepalace", elements=[
    {"type": "progress", "slot": "upper", "value": 50, "text": "सवाल का पहला हिस्सा पूरा", "at": A(56.2)}])
B(id="ans0", **{"in": 21, "out": 22}, **sheet(1, 21, "ch-mural"))
# ---- part two: the objectives, from the Charter ----------------------------------------------------
B(id="charter", **{"in": 22, "out": 24}, presenter="standard", plate="ch-charter", elements=[
    hero("संयुक्त राष्ट्र संघ के", "घोषणा-पत्र के अनुसार", A(64.6), sub="चार प्रमुख उद्देश्य", hl=["घोषणा-पत्र"])])
B(id="write-it", **{"in": 24, "out": 26}, presenter="standard", plate="ch-charter", elements=[
    {"type": "paper", "slot": "upper", "text": "घोषणा-पत्र के अनुसार इसके चार प्रमुख उद्देश्य हैं…", "texture": "crumpled", "at": 24},
    {"type": "lottie", "src": "tick-spark", "x": 760, "y": 640, "w": 560, "at": [25, 0.3]}])
B(id="obj1", **{"in": 26, "out": 28}, presenter="standard", broll=V("p1"), elements=[
    hero("पहला और मुख्य उद्देश्य", "युद्ध एवं विवादों का शान्तिपूर्ण समाधान", [26, 1.0], hl=["शान्तिपूर्ण"])])
B(id="three-jobs", **{"in": 28, "out": 29}, presenter="standard", plate="ch-peacepalace", elements=[
    {"type": "headline", "slot": "head", "text": "इसमें तीन काम", "size": "m", "at": 28, "fx": "drop"}])
B(id="keep", **{"in": 29, "out": 30}, presenter="standard", broll=V("p1", offset=3), elements=[
    {"type": "pill", "slot": "over-broll-top", "text": "1. शान्ति एवं सुरक्षा का अनुरक्षण", "at": [29, 0.4]},
    {"type": "pill", "slot": "over-broll-low", "text": "अनुरक्षण = बनाए रखना", "style": "accent", "at": [29, 3.0]}])
B(id="remove", **{"in": 30, "out": 31}, presenter="standard", broll=V("p2"), elements=[
    {"type": "pill", "slot": "over-broll-top", "text": "2. शान्ति विरोधी तत्वों का निराकरण", "at": [30, 0.4]},
    {"type": "pill", "slot": "over-broll-low", "text": "निराकरण = हटाना", "style": "accent", "at": [30, 3.6]}])
B(id="suppress", **{"in": 31, "out": 32}, presenter="standard", broll=V("p3"), elements=[
    {"type": "pill", "slot": "over-broll-top", "text": "3. आक्रामक कृत्यों का दमन", "at": [31, 0.6]},
    {"type": "pill", "slot": "over-broll-low", "text": "दमन = दबाना", "style": "accent", "at": [31, 5.0]}])
B(id="collective", **{"in": 32, "out": 34}, presenter="standard", broll=V("p3", offset=3.5), elements=[
    {"type": "stamp", "slot": "over-broll", "text": "सामूहिक = सारे देश मिलकर", "at": [33, 0.4], "fx": "zoom"}])
B(id="three-words", **{"in": 34, "out": 37}, presenter="standard", plate="ch-mural", elements=[
    {"type": "headline", "slot": "head", "text": "पहले उद्देश्य का सार", "size": "m", "at": 34, "fx": "drop"},
    {"type": "cards3", "slot": "upper", "items": [["बनाए रखना", A(112.3)], ["हटाना", A(113.7)], ["दबाना", A(114.8)]]},
    {"type": "pill", "slot": "under-upper", "text": "तीनों का मकसद: शान्ति", "style": "accent", "at": A(116.9)}])
B(id="ans1", **{"in": 37, "out": 39}, **sheet(2, 37, "ch-mural"))
B(id="after-peace", **{"in": 39, "out": 41}, presenter="standard", broll=V("f1"), elements=[
    {"type": "ask", "slot": "upper", "text": "शान्ति के बाद UN क्या चाहेगा?", "at": [39, 0.4], "answer": "देश आपस में दोस्त बनें", "t_answer": [40, 0.3]}])
B(id="part2", **{"in": 41, "out": "end"}, presenter="full", broll=V("h3", offset=5, dim=True), elements=[
    {"type": "stamp", "slot": "over-broll", "text": "बाकी 3 उद्देश्य: Part 2", "at": [42, 0.8], "fx": "zoom"}])

# ============================== PART 2 ==============================
A = cue_fn(2)
b2 = []
B = lambda **k: b2.append(k)
B(id="recap", **{"in": 0, "out": 3}, **sheet(2, 0, "ch-mural", animate=False))
B(id="obj2", **{"in": 3, "out": 4}, presenter="standard", plate="ch-charter", elements=[
    hero("दूसरा उद्देश्य", "समानाधिकार एवं आत्मनिर्णय", [3, 1.4], hl=["समानाधिकार", "आत्मनिर्णय"])])
B(id="equal", **{"in": 4, "out": 6}, presenter="standard", broll=V("f1"), elements=[
    {"type": "pill", "slot": "over-broll-top", "text": "समानाधिकार = हर देश के बराबर अधिकार", "at": [4, 0.4]},
    {"type": "pill", "slot": "over-broll-low", "text": "छोटा हो या बड़ा", "style": "accent", "at": [5, 0.3]}])
B(id="self", **{"in": 6, "out": 7}, presenter="standard", broll=V("f2"), elements=[
    {"type": "pill", "slot": "over-broll-low", "text": "आत्मनिर्णय = अपने भविष्य का फैसला खुद", "style": "accent", "at": [6, 1.4]}])
B(id="friends", **{"in": 7, "out": 11}, presenter="standard", broll=V("h3", offset=2), elements=[
    {"type": "note", "slot": "over-broll-top", "text": "इन दो आधारों पर…", "at": 7, "fx": "rise"},
    {"type": "pills", "slot": "over-broll-low", "items": [["मैत्रीपूर्ण संबंधों का विकास", [8, 0.6]], ["विश्व शान्ति मज़बूत", [9, 0.8]]]}])
B(id="half", **{"in": 11, "out": 12}, presenter="standard", plate="ch-peacepalace", elements=[
    {"type": "progress", "slot": "upper", "value": 50, "text": "उद्देश्यों वाला आधा answer तैयार", "at": [11, 0.3]}])
B(id="ans2", **{"in": 12, "out": 13}, **sheet(3, 12, "ch-mural"))
B(id="obj3", **{"in": 13, "out": 14}, presenter="standard", plate="ch-council", elements=[
    hero("तीसरा उद्देश्य", "विभिन्न समस्याओं का समाधान", [13, 1.0], hl=["समाधान"])])
B(id="relief", **{"in": 14, "out": [14, 4.0]}, presenter="standard", broll=V("c1"), elements=[
    {"type": "pills", "slot": "over-broll-low", "items": [["आर्थिक", [14, 0.6]], ["सामाजिक", [14, 1.3]], ["अन्तर्राष्ट्रीय समस्याएँ", [14, 2.4]]]}])
B(id="polio", **{"in": [14, 4.0], "out": 15}, presenter="standard", broll=V("c2"), elements=[
    {"type": "pill", "slot": "over-broll-low", "text": "अन्तर्राष्ट्रीय सहयोग", "style": "accent", "at": [14, 4.6]}])
B(id="rights", **{"in": 15, "out": 17}, presenter="standard", broll=V("c3"), elements=[
    {"type": "pill", "slot": "over-broll-low", "text": "मानवाधिकारों का सम्मान", "style": "accent", "at": [15, 0.6]}])
B(id="two-parts", **{"in": 17, "out": [19, 1.6]}, presenter="standard", plate="ch-council", elements=[
    {"type": "headline", "slot": "head", "text": "ध्यान दो: इसके दो हिस्से", "size": "m", "at": 17, "fx": "drop", "sfx": [[0.05, "hud-blip/back-blip"]]},
    {"type": "yn", "slot": "upper", "no": "सिर्फ समस्याओं का हल", "yes": "हल + मानवाधिकारों का सम्मान", "at": [18, 0.2], "t_yes": [18, 1.8]}])
B(id="ans3", **{"in": [19, 1.6], "out": 20}, **sheet(4, [19, 1.6], "ch-mural"))
B(id="obj4", **{"in": 20, "out": 21}, presenter="standard", plate="ch-charter", elements=[
    hero("आखिरी उद्देश्य", "समन्वय की स्थापना", [20, 1.2], hl=["समन्वय"])])
B(id="rhythm", **{"in": 21, "out": 22}, presenter="standard", broll=V("t2"), elements=[
    {"type": "pill", "slot": "over-broll-low", "text": "समन्वय = तालमेल", "style": "accent", "at": [21, 0.6]}])
B(id="chowk", **{"in": 22, "out": 25}, presenter="standard", broll=V("t1"), elements=[
    {"type": "note", "slot": "over-broll-top", "text": "देशों के बीच तालमेल के लिए…", "at": 22, "fx": "rise"},
    {"type": "pill", "slot": "over-broll-low", "text": "एक केन्द्र की स्थापना", "style": "accent", "at": [24, 0.4]}])
B(id="centre", **{"in": 25, "out": 27}, presenter="standard", plate="ch-council", elements=[
    hero("और वो केन्द्र", "खुद UN", [25, 0.6], sub="जहाँ सारे देश मिलकर काम करते हैं", hl=["UN"])])
B(id="ans4", **{"in": 27, "out": 28}, **sheet(5, 27, "ch-mural"))
B(id="four-words", **{"in": 28, "out": 30}, presenter="standard", plate="ch-mural", elements=[
    {"type": "headline", "slot": "head", "text": "चार उद्देश्य, चार शब्द", "size": "m", "at": 28, "fx": "drop"},
    {"type": "cards3", "slot": "upper", "items": [["शान्ति", A(94.4)], ["दोस्ती", A(95.7)], ["सहयोग", A(96.5)], ["तालमेल", A(97.2)]]}])
B(id="recall", **{"in": 30, "out": 34}, presenter="standard", plate="ch-peacepalace", elements=[
    {"type": "notify", "slot": "upper", "items": [["1", "शान्ति", "युद्ध एवं विवादों का शान्तिपूर्ण समाधान", [30, 0.3]],
                                                   ["2", "दोस्ती", "समानाधिकार एवं आत्मनिर्णय", [31, 0.3]],
                                                   ["3", "सहयोग", "समस्याओं का समाधान + मानवाधिकारों का सम्मान", [32, 0.3]],
                                                   ["4", "तालमेल", "समन्वय की स्थापना", [33, 0.3]]]}])
B(id="full", **{"in": 34, "out": 36}, **sheet(5, 34, "ch-mural", animate=False, title=FULL))
B(id="marks", **{"in": 36, "out": 39}, presenter="hub", hub={"cx": 905, "cy": 1450, "r": 125, "scale": 0.58, "backdrop": "plate"},
  plate="ch-mural", tracker=False, elements=[
    {"type": "answer", "slot": "upper", "title": FULL, "points": ANSWER, "nums": NUMS, "show": 5, "animate_from": 5, "at": 36, "top": 360},
    {"type": "pill", "slot": "head", "text": "पूरा format: Notes button", "style": "accent", "at": [37, 0.4]}])
B(id="outro", **{"in": 39, "out": "end"}, presenter="full", broll=V("z1"), elements=[
    {"type": "note", "slot": "over-broll-top", "text": "पढ़ाई में भी तालमेल", "at": [39, 0.6], "fx": "rise"}])

for n, beats, lit in ((1, b1, [12, 26]), (2, b2, [0, 0, 3, 13, 20])):
    plan = {"_about": __doc__.strip().splitlines()[0], "project": "pol-c4-la-06", "part": n, "captions_at": "bottom",
            "skin": "paper-editorial", "theme": "charter", "presenter_style": "card", "plate": "ch-council",
            "spine": {"title": "UN: अंग + उद्देश्य", "items": SPINE, "lit_at": lit, "show_from": 12 if n == 1 else 0},
            "tracker": {"from": 12 if n == 1 else 0}, "beats": beats}
    (ROOT / f"lab/kit_test/plan_pol_c4_la_06_p{n}.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1))
    print(f"part {n}: {len(beats)} beats")
