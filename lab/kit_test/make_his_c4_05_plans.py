"""HIS-C4-SA-05 (वैष्णववाद का वर्णन कीजिए): mandir look, two parts.

    python lab/kit_test/make_his_c4_05_plans.py  ->  plan_his_c4_sa_05_p{1,2}.json

The answer is a definition plus four points (अवतारवाद, दशावतार, भक्ति, मूर्ति-मंदिर), and it
BUILDS across both parts: after each point the sheet comes back with one more line written,
the rest faint blanks.  Each point lands as large hero text.  Backgrounds are real Gupta
sandstone (Deogarh, Udayagiri); the Veo shots are things a student has seen: a Ramlila, a
child dressed as Krishna, a bhajan mandali, a diya at a home shrine.  Cues: line index, or
[line, seconds into it].
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROJ = ROOT / "projects/his-c4-sa-05"

ANSWER = ["<b>वैष्णववाद</b> प्राचीन हिंदू (पौराणिक) धर्म की प्रमुख शाखा है, जिसमें भगवान विष्णु को ब्रह्मांड का <b>रक्षक</b> और <b>सर्वोच्च देवता</b> माना जाता है।",
          "<b>अवतारवाद:</b> पृथ्वी पर अधर्म बढ़ने पर विष्णु धर्म की रक्षा के लिए अवतार लेते हैं।",
          "<b>दशावतार:</b> विष्णु के दस प्रमुख अवतार (राम, कृष्ण, वराह, नरसिंह आदि) पूजे गए।",
          "<b>भक्ति मार्ग:</b> खर्चीले यज्ञों और कठोर तप के बजाय सच्चे प्रेम और भक्ति पर ज़ोर।",
          "<b>मूर्ति व मंदिर निर्माण:</b> गुप्त काल में विष्णु के अवतारों की मूर्तियाँ और मंदिर बने, जैसे देवगढ़ (उ.प्र.) का दशावतार मंदिर।"]
NUMS = ["", "1.", "2.", "3.", "4."]
SPINE_ITEMS = ["परिभाषा", "अवतारवाद", "दशावतार", "भक्ति मार्ग", "मूर्ति-मंदिर"]
FULL = "उत्तर: वैष्णववाद का वर्णन"


def sheet(k, at, plate, title="उत्तर बन रहा है…", animate=True, **extra):
    """the answer after k rows: those before k-1 already written, row k-1 writing in, the rest faint blanks"""
    return dict(presenter="standard", plate=plate, elements=[
        {"type": "answer", "slot": "upper", "title": title, "points": ANSWER, "nums": NUMS, "show": k,
         "animate_from": k - 1 if animate else k, "at": at, "gap": 0.45, **extra}])


def hero(kicker, text, at, sub=None, hl=None, fx=None):
    e = {"type": "hero", "slot": "upper", "kicker": kicker, "text": text, "at": at, "hl": hl or []}
    if sub:
        e["sub"] = sub
    if fx:
        e["fx"] = fx
    return e


def V(clip, **k):
    return {"clip": clip, "region": "full", **k}


# ============================== PART 1 ==============================
b1 = []
B = lambda **k: b1.append(k)
# ---- hook: the storm and the one lamp that will not go out ------------------------------------
B(id="storm", **{"in": 0, "out": 1}, presenter="standard", broll=V("h1"), elements=[
    {"type": "note", "slot": "over-broll-top", "text": "गीता की सबसे प्रसिद्ध बात…", "at": [0, 0.6], "fx": "blur"}])
B(id="gita", **{"in": 1, "out": 2}, presenter="standard", broll=V("h2"), elements=[])
B(id="adharma", **{"in": 2, "out": [2, 2.7]}, presenter="standard", broll=V("a1"), elements=[
    {"type": "stamp", "slot": "over-broll", "text": "जब-जब अधर्म बढ़ा…", "at": [2, 0.4], "fx": "zoom"}])
B(id="flame", **{"in": [2, 2.7], "out": 4}, presenter="standard", broll=V("h1", offset=4), elements=[
    hero("तब-तब भगवान", "अवतार लेते हैं", [3, 1.4], sub="धर्म की रक्षा के लिए", hl=["अवतार"], fx="rise")])
B(id="sanctum", **{"in": 4, "out": 5}, presenter="standard", broll=V("d1"), elements=[
    {"type": "note", "slot": "over-broll-top", "text": "यही विचार बना एक पूरी परंपरा की नींव", "at": [4, 0.5], "fx": "rise"}])
B(id="name", **{"in": 5, "out": [6, 0.7]}, presenter="standard", plate="vs-vishnu-head", elements=[
    hero("जिसे कहते हैं", "वैष्णववाद", [5, 1.4], hl=["वैष्णववाद"], fx="rise")])
B(id="question", **{"in": [6, 0.7], "out": 10}, presenter="standard", plate="vs-deogarh-door", elements=[
    {"type": "qhero", "slot": "upper", "ribbon": "Board Exam PYQ", "at": [6, 0.7], "years": [["2023", [6, 0.9]], ["2025", [6, 2.2]]],
     "question": "वैष्णववाद का वर्णन कीजिए।", "hl": ["वैष्णववाद"], "t_card": [8, 0.0],
     "marks": "3 अंक", "t_marks": [8, 0.9]}])
# ---- the definition (captions start here) ------------------------------------------------------
B(id="first-line", **{"in": 10, "out": 11}, presenter="standard", broll=V("d2"), elements=[
    {"type": "note", "slot": "over-broll-top", "text": "पहली लाइन: परिभाषा", "at": 10, "fx": "rise"}])
B(id="def", **{"in": 11, "out": 13}, presenter="standard", plate="vs-varaha", elements=[
    {"type": "headline", "slot": "head", "text": "परिभाषा", "size": "m", "at": 11, "fx": "drop"},
    {"type": "def", "slot": "upper", "term": "वैष्णववाद", "text": "पौराणिक धर्म की प्रमुख शाखा", "at": [12, 0.4]}])
B(id="preserver", **{"in": 13, "out": 15}, presenter="standard", broll=V("d2", offset=3), elements=[
    hero("भगवान विष्णु", "ब्रह्मांड के रक्षक", [14, 1.2], sub="और सर्वोच्च देवता", hl=["रक्षक"])])
B(id="vaishnav", **{"in": 15, "out": 17}, presenter="standard", plate="vs-vishnu-head", elements=[
    {"type": "pills", "slot": "upper", "items": [["विष्णु → वैष्णव", [15, 0.8]], ["= विष्णु को मानने वाले", 16]]}])
B(id="two-words", **{"in": 17, "out": 20}, presenter="standard", plate="vs-deogarh-temple", elements=[
    {"type": "headline", "slot": "head", "text": "परिभाषा में ये 2 शब्द ज़रूर", "size": "m", "at": 17, "fx": "drop"},
    {"type": "cards3", "slot": "upper", "items": [["रक्षक", [18, 0.0]], ["सर्वोच्च देवता", [18, 1.0]]]}])
B(id="ans0", **{"in": 20, "out": 21}, **sheet(1, 20, "vs-deogarh-temple"))
# ---- point 1: अवतारवाद -----------------------------------------------------------------------------
B(id="p1", **{"in": 21, "out": 23}, presenter="standard", plate="vs-varaha", elements=[
    hero("पहली बात", "अवतारवाद", [22, 0.6], sub="का सिद्धांत", hl=["अवतारवाद"], fx="rise")])
B(id="gita2", **{"in": 23, "out": 24}, presenter="standard", broll=V("h2", offset=3), elements=[
    {"type": "note", "slot": "over-broll-top", "text": "वही गीता वाली बात", "at": 23, "fx": "blur"}])
B(id="flood", **{"in": 24, "out": 25}, presenter="standard", broll=V("a1", offset=3.5), elements=[
    {"type": "pill", "slot": "over-broll-low", "text": "पाप और अधर्म बढ़ा", "at": [24, 0.6]}])
B(id="dawn", **{"in": 25, "out": 28}, presenter="standard", broll=V("a2"), elements=[
    {"type": "pills", "slot": "over-broll-low", "items": [["धर्म की रक्षा", [25, 1.0]], ["अलग-अलग रूप", 26]]},
    {"type": "stamp", "slot": "over-broll", "text": "= अवतार", "at": [27, 0.9], "fx": "zoom"}])
B(id="ans1", **{"in": 28, "out": 29}, **sheet(2, 28, "vs-varaha"))
# ---- point 2: दशावतार ------------------------------------------------------------------------------
B(id="how-many", **{"in": 29, "out": 30}, presenter="standard", broll=V("da3"), elements=[
    {"type": "note", "slot": "over-broll-top", "text": "विष्णु के अवतार कितने?", "at": [29, 0.8], "fx": "rise"}])
B(id="p2", **{"in": 30, "out": 31}, presenter="standard", plate="vs-deogarh-temple", elements=[
    hero("दूसरी बात", "दशावतार", [30, 2.2], sub="की मान्यता", hl=["दशावतार"], fx="rise")])
B(id="ten", **{"in": 31, "out": 32}, presenter="standard", broll=V("da3", offset=3), elements=[
    hero("विष्णु के", "दस प्रमुख अवतार", [31, 1.6], hl=["दस"])])
B(id="names", **{"in": 32, "out": 33}, presenter="standard", broll=V("da1"), elements=[
    {"type": "pills", "slot": "over-broll-low", "style": "accent",
     "items": [["राम", [32, 0.6]], ["श्रीकृष्ण", [32, 1.6]], ["वराह", [32, 2.6]], ["नरसिंह", [32, 3.6]]]}])
B(id="worship", **{"in": 33, "out": 34}, presenter="standard", broll=V("da2"), elements=[
    {"type": "pill", "slot": "over-broll-low", "text": "आज भी इनकी पूजा", "at": [33, 0.4]}])
B(id="mistake", **{"in": 34, "out": 37}, presenter="standard", plate="vs-deogarh-door", elements=[
    {"type": "headline", "slot": "head", "text": "ध्यान दें: यहीं गलती होती है", "size": "m", "at": 34, "fx": "drop",
     "sfx": [[0.05, "hud-blip/back-blip"]]},
    {"type": "yn", "slot": "upper", "no": "अवतारवाद + दशावतार = एक point", "yes": "दोनों अलग-अलग points", "at": 35, "t_yes": 36}])
B(id="diff", **{"in": 37, "out": 39}, presenter="standard", plate="vs-varaha", elements=[
    {"type": "headline", "slot": "head", "text": "फ़र्क याद रखो", "size": "m", "at": 37},
    {"type": "cards3", "slot": "upper", "items": [["अवतारवाद: अवतार क्यों होते हैं", [37, 0.6]], ["दशावतार: अवतार कौन-कौन से हैं", [38, 0.6]]]}])
B(id="ans2", **{"in": 39, "out": 41}, **sheet(3, 39, "vs-deogarh-temple"))
# ---- to part 2 ---------------------------------------------------------------------------------------
B(id="how-where", **{"in": 41, "out": 42}, presenter="standard", broll=V("b4"), elements=[
    {"type": "pills", "slot": "over-broll-low", "items": [["पूजा कैसे?", [41, 1.4]], ["और कहाँ?", [41, 3.4]]]}])
B(id="next", **{"in": 42, "out": "end"}, presenter="hero", broll=V("m3", dim=True), elements=[
    {"type": "stamp", "slot": "over-broll", "text": "बाकी 2 बातें: Part 2", "at": [42, 0.6], "fx": "zoom"}])

# ============================== PART 2 ==============================
b2 = []
B = lambda **k: b2.append(k)
B(id="recap-lamp", **{"in": 0, "out": 1}, presenter="standard", broll=V("h1", offset=5), elements=[
    {"type": "note", "slot": "over-broll-top", "text": "Part 1 में…", "at": [0, 0.4], "fx": "blur"}])
B(id="recap", **{"in": 1, "out": 4}, **sheet(3, 1, "vs-varaha", animate=False))
B(id="worship-how", **{"in": 4, "out": 5}, presenter="standard", broll=V("b4"), elements=[
    {"type": "note", "slot": "over-broll-top", "text": "अब: पूजा का तरीका", "at": [4, 0.4], "fx": "rise"}])
B(id="p3", **{"in": 5, "out": 6}, presenter="standard", plate="vs-vishnu-head", elements=[
    hero("तीसरी बात", "भक्ति का मार्ग", [5, 1.6], hl=["भक्ति"], fx="rise")])
B(id="yajna", **{"in": 6, "out": [7, 1.1]}, presenter="standard", broll=V("b1"), elements=[
    {"type": "pill", "slot": "over-broll-low", "text": "खर्चीले यज्ञ", "at": [7, 0.1]}])
B(id="tapas", **{"in": [7, 1.1], "out": 8}, presenter="standard", broll=V("b2"), elements=[
    {"type": "pill", "slot": "over-broll-low", "text": "कठोर तप", "at": [7, 1.3]}])
B(id="bhakti", **{"in": 8, "out": 9}, presenter="standard", broll=V("b3"), elements=[
    {"type": "pill", "slot": "over-broll-low", "text": "सच्चा प्रेम + भक्ति", "style": "accent", "at": [8, 0.6]}])
B(id="not-needed", **{"in": 9, "out": 12}, presenter="standard", plate="vs-deogarh-door", elements=[
    {"type": "yn", "slot": "upper", "no": "बड़े यज्ञ, शरीर को कष्ट", "yes": "बस सच्चा प्रेम", "at": [9, 0.8], "t_yes": 11}])
B(id="people", **{"in": 12, "out": 15}, presenter="standard", broll=V("b4", offset=3), elements=[
    {"type": "note", "slot": "over-broll-top", "text": "ध्यान से सुनो", "at": 12, "fx": "rise"},
    {"type": "stamp", "slot": "over-broll", "text": "आम लोगों तक पहुँचा", "at": [14, 0.4], "fx": "zoom"}])
B(id="rich-all", **{"in": 15, "out": 17}, presenter="standard", plate="vs-varaha", elements=[
    {"type": "yn", "slot": "upper", "no": "खर्चीले यज्ञ: सिर्फ अमीर", "yes": "भक्ति: कोई भी", "at": 15, "t_yes": 16}])
B(id="anyone", **{"in": 17, "out": 18}, presenter="standard", broll=V("b3", offset=4), elements=[
    {"type": "pill", "slot": "over-broll-low", "text": "गरीब हो या अमीर", "style": "accent", "at": [17, 0.3]}])
B(id="ans3", **{"in": 18, "out": 20}, **sheet(4, 18, "vs-vishnu-head"))
# ---- point 4: मूर्ति और मंदिर -------------------------------------------------------------------------
B(id="home", **{"in": 20, "out": 22}, presenter="standard", broll=V("a2"), elements=[
    {"type": "note", "slot": "over-broll-top", "text": "भगवान के लिए घर?", "at": [21, 0.6], "fx": "rise"}])
B(id="p4", **{"in": 22, "out": 23}, presenter="standard", plate="vs-deogarh-temple", elements=[
    hero("आखिरी बात", "मूर्ति और मंदिर निर्माण", [22, 2.0], hl=["मूर्ति", "मंदिर"], fx="rise")])
B(id="murti", **{"in": 23, "out": [24, 1.5]}, presenter="standard", broll=V("m1"), elements=[
    {"type": "pill", "slot": "over-broll-low", "text": "भव्य मूर्तियाँ", "at": [24, 0.0]}])
B(id="mandir", **{"in": [24, 1.5], "out": 25}, presenter="standard", broll=V("m2"), elements=[
    {"type": "pill", "slot": "over-broll-low", "text": "शानदार मंदिर", "at": [24, 1.6]}])
B(id="gupta", **{"in": 25, "out": 26}, presenter="standard", plate="vs-vishnu-head", elements=[
    hero("खासकर", "गुप्त काल में", [25, 0.6], hl=["गुप्त"])])
B(id="why-murti", **{"in": 26, "out": 28}, presenter="standard", broll=V("d1", offset=3), elements=[
    {"type": "pill", "slot": "over-broll-low", "text": "मूर्ति: भगवान आँखों के सामने", "at": [26, 1.0]}])
B(id="why-mandir", **{"in": 28, "out": 29}, presenter="standard", broll=V("b4", offset=5), elements=[
    {"type": "pill", "slot": "over-broll-low", "text": "मंदिर: सब मिलकर पूजा", "at": [28, 1.0]}])
B(id="example", **{"in": 29, "out": [30, 1.5]}, presenter="standard", broll=V("m3"), elements=[
    {"type": "note", "slot": "over-broll-top", "text": "उदाहरण →", "at": [29, 0.4], "fx": "rise"}])
B(id="deogarh", **{"in": [30, 1.5], "out": 31}, presenter="standard", plate="vs-deogarh-door", elements=[
    {"type": "photo", "slot": "upper", "src": "history/vaishnav/deogarh-4.jpg", "w": 760, "label": "दशावतार मंदिर, देवगढ़ (उत्तर प्रदेश)", "at": [30, 1.5]},
    {"type": "pill", "slot": "under-upper", "text": "गुप्त काल", "style": "accent", "at": [30, 3.6]}])
B(id="ans4", **{"in": 31, "out": 32}, **sheet(5, 31, "vs-deogarh-temple", title=FULL))
# ---- the four-question recap: each question over a picture, then the list grows -----------------
REC = [["अवतार क्यों? → अवतारवाद", 34], ["कितने अवतार? → दशावतार", 36], ["किस भाव से पूजा? → भक्ति", 38], ["मंदिर कब? → गुप्त काल", 40]]


def recap(k, at):
    return dict(presenter="standard", plate="vs-varaha", elements=[
        {"type": "headline", "slot": "head", "text": "चार सवाल = पूरा answer", "size": "m", "at": 32 if k == 1 else at},
        {"type": "cards3", "slot": "upper", "items": [[t, (c if i == k - 1 else 0)] for i, (t, c) in enumerate(REC[:k])]}])


B(id="four", **{"in": 32, "out": 33}, presenter="standard", broll=V("o1", offset=1), elements=[
    hero("तो अब पूरा answer", "4 सवालों से याद रखो", [32, 0.6], hl=["4"], fx="rise")])
B(id="q1", **{"in": 33, "out": 34}, presenter="standard", broll=V("a1", offset=1), elements=[
    {"type": "note", "slot": "over-broll-top", "text": "सवाल 1", "at": 33}])
B(id="r1", **{"in": 34, "out": 35}, **recap(1, 34))
B(id="q2", **{"in": 35, "out": 36}, presenter="standard", broll=V("da3", offset=5), elements=[
    {"type": "note", "slot": "over-broll-top", "text": "सवाल 2", "at": 35}])
B(id="r2", **{"in": 36, "out": 37}, **recap(2, 36))
B(id="q3", **{"in": 37, "out": 38}, presenter="standard", broll=V("b3", offset=2), elements=[
    {"type": "note", "slot": "over-broll-top", "text": "सवाल 3", "at": 37}])
B(id="r3", **{"in": 38, "out": 39}, **recap(3, 38))
B(id="q4", **{"in": 39, "out": 40}, presenter="standard", broll=V("m2", offset=4), elements=[
    {"type": "note", "slot": "over-broll-top", "text": "सवाल 4", "at": 39}])
B(id="r4", **{"in": 40, "out": 41}, **recap(4, 40))
B(id="marks", **{"in": 41, "out": 43}, presenter="standard", broll=V("m3", offset=4, dim=True), elements=[
    hero("परिभाषा + चारों बातें", "पूरे 3 नंबर पक्के", [42, 0.4], hl=["पक्के"], fx="rise")])
B(id="answer", **{"in": 43, "out": 44}, presenter="hub", hub={"cx": 905, "cy": 1450, "r": 125, "scale": 0.58, "backdrop": "plate"},
  plate="vs-deogarh-temple", elements=[
    {"type": "answer", "slot": "upper", "title": FULL, "points": ANSWER, "nums": NUMS, "show": 5, "animate_from": 5, "at": 43, "top": 360},
    {"type": "pill", "slot": "head", "text": "पूरा answer: Notes button", "style": "accent", "at": [43, 1.0]}])
B(id="outro", **{"in": 44, "out": "end"}, presenter="hero", broll=V("o1", offset=3), elements=[
    {"type": "note", "slot": "over-broll-top", "text": "हर topic, एक-एक reel", "at": [44, 0.6], "fx": "rise"}])

for n, beats, lit in ((1, b1, [11, 22, 30]), (2, b2, [0, 0, 0, 5, 22])):
    plan = {"_about": __doc__.strip().splitlines()[0], "project": "his-c4-sa-05", "part": n, "captions_at": "bottom",
            "skin": "paper-editorial", "theme": "mandir", "presenter_style": "card", "plate": "vs-deogarh-temple",
            "spine": {"title": "वैष्णववाद", "items": SPINE_ITEMS, "lit_at": lit, "show_from": 10 if n == 1 else 0},
            "beats": beats}
    (ROOT / f"lab/kit_test/plan_his_c4_sa_05_p{n}.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1))
    print(f"part {n}: {len(beats)} beats")
