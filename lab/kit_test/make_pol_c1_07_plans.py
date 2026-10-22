"""POL-C1-SA-07 (सोवियत संघ के विघटन के कारण): constructivist-poster look, two parts.

    python lab/kit_test/make_pol_c1_07_plans.py  ->  plan_pol_c1_sa_07_p{1,2}.json

A Soviet topic straight after POL-C1-SA-02, so nothing visual is shared with it: new
plates (panel block, Berlin Wall, Baltic Way, Brandenburg Gate with its ГЛАСНОСТЬ
graffiti), new clips, a new skin.  Metaphors are shot in India (termites in a door
frame, a house under renovation, a chai-stall argument).  The answer builds one cause
at a time across both parts.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROJ = ROOT / "projects/pol-c1-sa-07"
POINTS = ["आर्थिक गतिहीनता: हथियारों और सेना पर भारी खर्च, ज़रूरी सामान की कमी",
          "राजनीतिक-प्रशासकीय ठहराव: पार्टी का शासन सत्तावादी, भ्रष्ट, गैर-जवाबदेह; जनता में असंतोष",
          "गोर्बाचेव के सुधार: पेरेस्त्रोइका (पुनर्संरचना) और ग्लासनोस्त (खुलापन)",
          "राष्ट्रवाद का उभार: बाल्टिक गणराज्य (एस्टोनिया, लातविया, लिथुआनिया), यूक्रेन, जॉर्जिया"]
FOUR = [["tabler:coin-off", "आर्थिक गतिहीनता"], ["tabler:building-bank", "प्रशासकीय ठहराव"], ["tabler:refresh", "गोर्बाचेव के सुधार"], ["tabler:flag", "राष्ट्रवाद का उभार"]]
SPINE = {"title": "सोवियत संघ का विघटन: 4 कारण", "items": [f[1] for f in FOUR]}


def sheet(show, at, plate, a0=None, title=None):
    return dict(presenter="standard", plate=plate, elements=[
        {"type": "answer", "slot": "upper", "title": title or ("उत्तर बन रहा है…" if show < 4 else "उत्तर: विघटन के चार कारण"),
         "points": POINTS, "show": show, "animate_from": show - 1 if a0 is None else a0, "at": at, "gap": 0.45}])


def hero(kicker, text, at, sub=None, hl=None):
    e = {"type": "hero", "slot": "upper", "kicker": kicker, "text": text, "at": at, "hl": hl or []}
    if sub:
        e["sub"] = sub
    return e


def part1():
    beats = []; B = lambda **k: beats.append(k)
    B(id="hook", **{"in": 0, "out": 5}, presenter="standard", broll={"clip": "s01", "region": "full"}, elements=[
        {"type": "pills", "slot": "over-broll-low", "items": [["बाहर से मज़बूत", 2], ["अंदर से कमज़ोर", 3]]},
        {"type": "stamp", "slot": "over-broll", "text": "अचानक धड़ाम!", "at": [4, 0.5], "fx": "zoom"}])
    B(id="termites", **{"in": 5, "out": 7}, presenter="standard", broll={"clip": "s02", "region": "full"}, elements=[
        {"type": "note", "slot": "over-broll-top", "text": "1991: एक महाशक्ति के साथ यही हुआ", "at": 5, "fx": "blur"}])
    B(id="question", **{"in": 7, "out": 11}, presenter="standard", plate="sc-block", elements=[
        {"type": "qhero", "slot": "upper", "ribbon": "Board Exam PYQ", "at": 7, "years": [["2023", [8, 0.6]]], "qsize": 60,
         "question": "सोवियत संघ के विघटन के कारणों को लिखिए।", "hl": ["विघटन", "कारणों"], "t_card": 10, "marks": "3 अंक", "t_marks": [8, 2.4]}])
    B(id="four", **{"in": 11, "out": 14}, presenter="hub", hub={"cy": 1000, "r": 190, "backdrop": "veo:s01@1"}, plate="sc-gate", elements=[
        {"type": "headline", "slot": "head", "text": "विघटन के 4 कारण", "size": "m", "at": 11, "fx": "drop"},
        {"type": "radial", "slot": "around-hub", "radius": 350, "cumulative": True,
         "items": [[ic, lb, at] for (ic, lb), at in zip(FOUR, [12, [12, 2.4], [13, 2.0], [13, 4.0]])],
         "recount": [[12, 0.3], [12, 2.6], [13, 2.2], [13, 4.2]]}])
    B(id="define", **{"in": 14, "out": 15}, presenter="standard", plate="sc-block", elements=[
        {"type": "def", "slot": "head", "term": "विघटन", "text": "टूटकर बिखर जाना", "at": 14}])
    B(id="c1", **{"in": 15, "out": 17}, presenter="standard", broll={"clip": "s03", "region": "full"}, elements=[
        hero("कारण 1", "आर्थिक गतिहीनता", [15, 0.8], sub="अर्थव्यवस्था आगे नहीं बढ़ी", hl=["गतिहीनता"])])
    B(id="army", **{"in": 17, "out": 19}, presenter="standard", broll={"clip": "s04", "region": "full"}, elements=[
        {"type": "pills", "slot": "over-broll-low", "style": "accent", "items": [["परमाणु हथियार", [17, 2.2]], ["पूर्वी यूरोप में सेना", 18]]}])
    B(id="shortage", **{"in": 19, "out": 21}, presenter="standard", broll={"clip": "s05", "region": "full"}, elements=[
        {"type": "pills", "slot": "over-broll-low", "items": [["ज़रूरी चीज़ों की भारी कमी", 19], ["अर्थव्यवस्था चरमराई", 20]]}])
    B(id="chain1", **{"in": 21, "out": [22, 1.6]}, presenter="standard", plate="sc-berlinwall", elements=[
        {"type": "chain", "slot": "upper", "items": [["हथियारों पर ज़्यादा खर्च", [21, 1.0]], ["ज़रूरी सामान की कमी", [21, 2.2]], ["अर्थव्यवस्था में गिरावट", [21, 2.8]]]}])
    B(id="ans1", **{"in": [22, 1.6], "out": 23}, **sheet(1, [22, 1.6], "sc-berlinwall"))
    B(id="c2", **{"in": 23, "out": 25}, presenter="standard", broll={"clip": "s06", "region": "full"}, elements=[
        hero("कारण 2", "राजनीतिक-प्रशासकीय ठहराव", [23, 0.2], sub="व्यवस्था जम गई, सुधार नहीं", hl=["ठहराव"])])
    B(id="corrupt", **{"in": 25, "out": 27}, presenter="standard", broll={"clip": "s07", "region": "full"}, elements=[
        {"type": "pills", "slot": "over-broll-low", "style": "accent", "items": [["सत्तावादी", [25, 2.0]], ["भ्रष्ट", 26], ["गैर-जवाबदेह", [26, 1.6]]]}])
    B(id="anger", **{"in": 27, "out": 28}, presenter="standard", broll={"clip": "s08", "region": "full"}, elements=[
        {"type": "pill", "slot": "over-broll-low", "text": "आम नागरिकों में असंतोष", "style": "accent", "at": 27}])
    B(id="three-words", **{"in": 28, "out": 29}, presenter="standard", plate="sc-block", elements=[
        hero("तीन शब्द याद रखो", "सत्तावादी · भ्रष्ट · गैर-जवाबदेह", [28, 1.2], hl=["भ्रष्ट"])])
    B(id="ans2", **{"in": 29, "out": 31}, **sheet(2, 29, "sc-block"))
    B(id="teaser", **{"in": 31, "out": "end"}, presenter="standard", plate="sc-gate", elements=[
        {"type": "pills", "slot": "upper", "style": "accent", "items": [["गोर्बाचेव के सुधार", [31, 1.0]], ["राष्ट्रवाद का उभार", [31, 2.6]]]},
        {"type": "stamp", "slot": "under-upper", "text": "Part 2 में", "at": 32}])
    return {"captions_at": "bottom", "spine": {**SPINE, "lit_at": [15, 23], "show_from": 11}, "beats": beats}


def part2():
    beats = []; B = lambda **k: beats.append(k)
    B(id="so-far", **{"in": 0, "out": 4}, **sheet(2, 0, "sc-block", a0=2, title="Part 1 तक का उत्तर"))
    B(id="c3", **{"in": 4, "out": 6}, presenter="standard", plate="sc-gate", elements=[
        hero("कारण 3", "गोर्बाचेव के सुधार", [5, 0.4], hl=["सुधार"])])
    B(id="gorbachev", **{"in": 6, "out": 8}, presenter="standard", plate="sc-gate", elements=[
        {"type": "pill", "slot": "head", "text": "दो प्रमुख नीतियाँ", "style": "accent", "at": 7},
        {"type": "photo", "slot": "upper", "src": "political-science/soviet-collapse/gorbachev-1.jpg", "w": 460, "label": "मिखाइल गोर्बाचेव (1987)", "at": 6}])
    B(id="perestroika", **{"in": 8, "out": 10}, presenter="standard", broll={"clip": "s09", "region": "full"}, elements=[
        {"type": "def", "slot": "over-broll-top", "term": "पेरेस्त्रोइका", "text": "पुनर्संरचना: व्यवस्था में बदलाव", "at": 8}])
    B(id="glasnost", **{"in": 10, "out": 12}, presenter="standard", broll={"clip": "s10", "region": "full"}, elements=[
        {"type": "def", "slot": "over-broll-top", "term": "ग्लासनोस्त", "text": "खुलापन: खुलकर बोलने की आज़ादी", "at": 10}])
    B(id="pressure", **{"in": 12, "out": 14}, presenter="standard", plate="sc-gate", elements=[
        {"type": "note", "slot": "head", "text": "पर पुरानी व्यवस्था पर दबाव बढ़ा", "at": 12, "fx": "rise"},
        {"type": "stamp", "slot": "upper", "text": "संभालना मुश्किल", "at": 13}])
    B(id="remember", **{"in": 14, "out": 15}, presenter="standard", plate="sc-gate", elements=[
        {"type": "cards3", "slot": "upper", "items": [["पेरेस्त्रोइका = व्यवस्था में बदलाव", [14, 1.2]], ["ग्लासनोस्त = खुलापन", [14, 2.6]]]}])
    B(id="ans3", **{"in": 15, "out": 16}, **sheet(3, 15, "sc-gate"))
    B(id="c4", **{"in": 16, "out": 17}, presenter="standard", broll={"clip": "s12", "region": "full"}, elements=[
        hero("कारण 4", "राष्ट्रवाद का उभार", [16, 0.6], hl=["राष्ट्रवाद"])])
    B(id="regions", **{"in": 17, "out": 18}, presenter="standard", broll={"clip": "s11", "region": "full"}, elements=[
        {"type": "pills", "slot": "over-broll-low", "style": "accent", "items": [["रूस", [17, 0.3]], ["बाल्टिक गणराज्य", [17, 1.2]], ["यूक्रेन", [17, 2.6]], ["जॉर्जिया", [17, 3.4]]]},
        {"type": "note", "slot": "over-broll-top", "text": "अलग पहचान, स्वतंत्रता की माँग", "at": [17, 4.5], "fx": "rise"}])
    B(id="sovereignty", **{"in": 18, "out": 20}, presenter="standard", plate="sc-baltic", elements=[
        {"type": "def", "slot": "head", "term": "संप्रभुता", "text": "अपने देश के फैसले खुद लेना", "at": 18},
        {"type": "stamp", "slot": "upper", "text": "विघटन में अहम भूमिका", "at": 19}])
    B(id="baltic", **{"in": 20, "out": 21}, presenter="standard", plate="sc-baltic", elements=[
        hero("3 बाल्टिक गणराज्य", "एस्टोनिया · लातविया · लिथुआनिया", [20, 2.0], hl=["लातविया"])])
    B(id="ans4", **{"in": 21, "out": 22}, **sheet(4, 21, "sc-berlinwall"))
    B(id="revise", **{"in": 22, "out": 29}, presenter="hub", hub={"cy": 980, "r": 200, "backdrop": "veo:s12@3"}, plate="sc-gate", elements=[
        {"type": "headline", "slot": "head", "text": "चारों कारण, जल्दी से", "size": "m", "at": 22},
        {"type": "quad", "slot": "full", "icons": [f[0] for f in FOUR], "items": [
            ["आर्थिक गतिहीनता", "हथियारों पर खर्च, सामान की कमी", 22], ["प्रशासकीय ठहराव", "सत्तावादी, भ्रष्ट, गैर-जवाबदेह", 24],
            ["गोर्बाचेव के सुधार", "पेरेस्त्रोइका + ग्लासनोस्त", 26], ["राष्ट्रवाद का उभार", "अलग होने की माँग", 27]]}])
    B(id="marks", **{"in": 29, "out": 31}, presenter="standard", plate="sc-block", elements=[
        hero("चारों कारण सही लिखे तो", "3 नंबर पक्के", [30, 0.0], hl=["पक्के"])])
    B(id="outro", **{"in": 31, "out": "end"}, presenter="standard", broll={"clip": "s13", "region": "full", "dim": True}, elements=[
        {"type": "pill", "slot": "head", "text": "exam का format: Notes button", "style": "accent", "at": 31, "fx": "drop"},
        {"type": "note", "slot": "over-broll-low", "text": "90% की तैयारी पक्की", "at": 33, "fx": "blur"}])
    return {"captions_at": "bottom", "spine": {**SPINE, "pre_lit": 2, "lit_at": [5, 16], "show_from": 0}, "beats": beats}


shots = {"s01": "strong-looking tower block collapses", "s02": "termites hollow an Indian door frame", "s03": "missiles on trucks in a parade",
         "s04": "Soviet army base in snowy Eastern Europe", "s05": "empty cupboard in a Soviet kitchen", "s06": "unanimous party vote",
         "s07": "official stamps papers, citizens ignored", "s08": "angry citizens in a square", "s09": "Indian house under renovation",
         "s10": "chai-stall newspaper debate", "s11": "Baltic Way human chain, 1989", "s12": "crowd waving many flags", "s13": "students leave the school gate"}
(PROJ / "veo/shots.json").write_text(json.dumps(shots, indent=1, ensure_ascii=False))
for n, f in ((1, part1), (2, part2)):
    body = f()
    plan = {"_about": f"POL-C1-SA-07 part {n}, poster look", "project": "pol-c1-sa-07", "part": n,
            "skin": "paper-editorial", "theme": "poster", "presenter_style": "card", "plate": "sc-block", **body}
    (ROOT / f"lab/kit_test/plan_pol_c1_sa_07_p{n}.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1))
    print(f"part {n}: {len(body['beats'])} beats")
