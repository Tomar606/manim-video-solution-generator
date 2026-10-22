"""Three plans for POL-C11-LA-02 (भारत की विदेश नीति के सिद्धांत).
   A  dossier       photo-led: a Cold-War briefing file, B&W archival prints clipped to typed cards
   B  two camps     diagram-led: India (the presenter, in a circle) between the two blocs; 2x2 recap
   C  un-blue       clip-led: Veo footage under most beats, presenter in a card"""
import json
from pathlib import Path
HERE = Path(__file__).parent
FP = "history/foreign-policy/"
ITEMS = ["गुटनिरपेक्षता", "साम्राज्यवाद-उपनिवेशवाद का विरोध", "UN और अंतर्राष्ट्रीय कानून", "सभी राष्ट्रों से मैत्री"]
FAR = 999
A_CLIP = {(1, "hook"): "v01", (2, "f2"): "v03", (2, "f4-friends"): "v05"}   # archival-style Veo clips (dossier)
QUAD = lambda times: {"type": "quad", "slot": "around-hub", "nums": ["1", "2", "3", "4"],
    "icons": ["tabler:scale", "tabler:ban", "tabler:building-bank", "tabler:heart-handshake"],
    "items": [["गुटनिरपेक्षता", "किसी गुट में नहीं, फैसले खुद", times[0]], ["साम्राज्यवाद-उपनिवेशवाद विरोध", "जो दर्द झेला, वो किसी और का न हो", times[1]],
              ["UN और अंतर्राष्ट्रीय कानून", "समस्याओं का शांतिपूर्वक हल", times[2]], ["सभी राष्ट्रों से मैत्री", "समानता; रंगभेद, नस्लवाद का विरोध", times[3]]]}


def bg(v, clip=None, photo=None, dim=False):
    if v == "A" and photo: return {"photo": photo, "region": "top", "treatment": "colour"}
    if v == "C" and clip: return {"clip": clip, "region": "full", "dim": dim}
    if v == "B" and photo: return {"photo": photo, "region": "top", "treatment": "colour"}
    return None


def ov(v, lit, lit_t=None, times=None):
    if v == "B": return QUAD(times)
    e = {"type": "checklist", "slot": "upper", "lit": lit, "at": None}
    if lit_t: e["lit_t"] = lit_t
    return e


def S(v, b, on, off):        # a slot over footage when the beat has footage, else the plate slot
    return on if b else off


def part1(v):
    out = []
    b = bg(v, "v01", FP + "nehru-1.jpg")
    out.append(dict(id="hook", i=0, o=4, bg=b, els=[{"type": "pill", "slot": "over-broll-low", "text": "1947: दुनिया से रिश्ते कैसे रखें?", "style": "accent", "at": 1}] if v == "A" else
                    [{"type": "headline", "slot": "head", "text": "1947: दुनिया से रिश्ते कैसे रखें?", "size": "m", "at": 1}]))
    out.append(dict(id="question", i=4, o=8, mode="small", bg=bg(v, "v01", FP + "potsdam-1.jpg", dim=True),
                    els=[{"type": "qcard", "slot": "upper", "question": "भारत की विदेश नीति के प्रमुख सिद्धांत क्या हैं?", "year": "2025", "marks": "4 अंक", "t_marks": [5, 1.0], "at": 5}]))
    b = bg(v, "v02", FP + "potsdam-1.jpg")
    out.append(dict(id="bhumika", i=8, o=14, bg=b,
                    els=[{"type": "pill", "slot": S(v, b, "over-broll-top", "head"), "text": "पहले: छोटी-सी भूमिका", "style": "accent", "at": 8},
                         {"type": "chain", "slot": S(v, b, "over-broll-low", "upper"), "items": [["15 अगस्त 1947: आज़ादी", 9], ["अपनी स्वतंत्र विदेश नीति", 10], ["पर विश्व दो खेमों में बँटा", 13]]}]))
    b = bg(v, None, FP + "nehru-1.jpg")
    out.append(dict(id="nehru", i=14, o=18, bg=b,
                    els=[{"type": "def", "slot": S(v, b, "over-broll-low", "head"), "term": "पहले विदेश मंत्री", "text": "पं. जवाहरलाल नेहरू", "at": 14},
                         {"type": "note", "slot": S(v, b, "over-broll-top", "upper"), "text": "सोच-समझकर बनाई नीति, आज भी विकास की ओर", "at": 16}]))
    out.append(dict(id="bhumika3", i=18, o=20,
                    els=[{"type": "headline", "slot": "head", "text": "भूमिका में तीन बातें", "size": "m", "at": 18},
                         {"type": "cards3", "slot": "upper", "items": [["15 अगस्त 1947", 19], ["दुनिया के दो खेमे", [19, 2.2]], ["नेहरू जी", [19, 4.4]]]}]))
    out.append(dict(id="f1", i=20, o=22,
                    els=[{"type": "section", "slot": "head", "num": "1", "text": "गुटनिरपेक्षता", "at": 20},
                         {"type": "def", "slot": "upper", "term": "गुटनिरपेक्ष", "text": "किसी गुट में शामिल न होना", "at": [20, 3.5]}]))
    out.append(dict(id="blocs", i=22, o=29, mode="hub" if v == "B" else None,
                    els=[{"type": "blocs", "slot": "upper", "left": ["साम्यवादी", "सोवियत संघ"], "right": ["पूँजीवादी", "अमेरिका"],
                          "t_left": 23, "t_right": 24, "t_india": 22, "t_cross": 26, "t_label": 28, "label": "किसी गुट में नहीं", "at": 22}]))
    b = bg(v, "v05", FP + "belgrade-2.jpg")
    out.append(dict(id="f1-meaning", i=29, o=32, bg=None if v == "A" else (bg(v, None, FP + "belgrade-2.jpg") if v == "B" else b),
                    els=[{"type": "yn", "slot": "upper", "no": "दुनिया से दूर रहना", "yes": "सबसे दोस्ती, फैसले खुद", "t_yes": 30, "at": 29}]))
    out.append(dict(id="f1-key", i=32, o=35, bg=b if v == "A" else None,
                    els=[{"type": "stamp", "slot": S(v, b if v == "A" else None, "over-broll", "upper"), "text": "सबसे ज़रूरी सिद्धांत", "at": 32},
                         {"type": "note", "slot": S(v, b if v == "A" else None, "over-broll-low", "under-upper"), "text": "बाकी सिद्धांत इसी सोच से निकले", "at": 33}]))
    out.append(dict(id="teaser", i=35, o="end", mode="hub" if v == "B" else None,
                    els=[{"type": "headline", "slot": "head", "text": "एक हो गया, तीन बाकी", "size": "m", "at": 35}, ov(v, [0], times=[0, FAR, FAR, FAR]),
                         {"type": "pill", "slot": "center-low" if v == "B" else "under-upper", "text": "बाकी तीन: Part 2", "style": "accent", "at": 36}]))
    return out


def part2(v):
    out = []
    out.append(dict(id="bridge", i=0, o=4, mode="hub" if v == "B" else None,
                    els=[{"type": "headline", "slot": "head", "text": "Part 1: गुटनिरपेक्षता", "size": "m", "at": 0}, ov(v, [0], times=[0, FAR, FAR, FAR])]))
    b = bg(v, "v03", None) if v == "C" else None
    out.append(dict(id="f2", i=4, o=10, bg=b,
                    els=[{"type": "section", "slot": S(v, b, "over-broll-top", "head"), "num": "2", "text": "साम्राज्यवाद-उपनिवेशवाद का विरोध", "at": 4},
                         {"type": "pills", "slot": S(v, b, "over-broll-low", "upper"), "items": [["200 वर्ष उपनिवेश", 5], ["अंग्रेज़ों का गुलाम", 6], ["पीड़ा को समझता है", 7]], "style": "accent"}]))
    out.append(dict(id="f2-pain", i=10, o=12,
                    els=[{"type": "stamp", "slot": "upper", "text": "जो दर्द झेला, वो किसी और का न हो", "at": 10}]))
    out.append(dict(id="half", i=12, o=13, mode="hub" if v == "B" else None,
                    els=[{"type": "headline", "slot": "head", "text": "आधा answer तैयार", "size": "m", "at": 12}, ov(v, [0, 1], times=[0, 12, FAR, FAR])]))
    b = bg(v, "v04", "political-science/united-nations/assembly-1.jpg")
    out.append(dict(id="f3", i=13, o=19, bg=b,
                    els=[{"type": "section", "slot": S(v, b, "over-broll-top", "head"), "num": "3", "text": "UN और अंतर्राष्ट्रीय कानून का पालन", "at": 13},
                         {"type": "pills", "slot": S(v, b, "over-broll-low", "upper"), "items": [["UN में आस्था", 15], ["अंतर्राष्ट्रीय कानून का पालन", 16], ["समस्याओं का हल", 17]], "style": "accent"}]))
    out.append(dict(id="f3-word", i=19, o=21,
                    els=[{"type": "stamp", "slot": "upper", "text": "शांतिपूर्वक: यही इसकी जान", "at": 19}]))
    b = bg(v, "v05", FP + "apartheid-3.jpg")
    out.append(dict(id="f4", i=21, o=25, bg=b,
                    els=[{"type": "section", "slot": S(v, b, "over-broll-top", "head"), "num": "4", "text": "सभी राष्ट्रों से मैत्रीपूर्ण संबंध", "at": 21},
                         {"type": "pill", "slot": S(v, b, "over-broll-low", "upper"), "text": "सभी राष्ट्रों की समानता", "style": "accent", "at": 23}]))
    out.append(dict(id="f4-words", i=25, o=27,
                    els=[{"type": "cards3", "slot": "upper", "items": [["रंगभेद: चमड़ी के रंग के आधार पर भेदभाव", 25], ["नस्लवाद: नस्ल के आधार पर भेदभाव", 26]]}]))
    out.append(dict(id="f4-friends", i=27, o=30,
                    els=[{"type": "chain", "slot": "upper", "items": [["साम्यवादी हो या पूँजीवादी", 27], ["भारत सबसे दोस्ती चाहता है", 28], ["पड़ोसी देश: विशेष प्राथमिकता", [28, 2.6]]]}]))
    out.append(dict(id="recap", i=30, o=36, mode="hub" if v == "B" else None,
                    els=[{"type": "headline", "slot": "head", "text": "चारों सिद्धांत, एक बार", "size": "m", "at": 30}, ov(v, [], lit_t=[32, 33, 34, 35], times=[32, 33, 34, 35])]))
    out.append(dict(id="marks", i=36, o=38,
                    els=[{"type": "stamp", "slot": "upper", "text": "भूमिका + चारों = 4 नंबर", "at": 37}]))
    out.append(dict(id="outro", i=38, o="end", mode="hero" if v != "B" else None,
                    els=[{"type": "pill", "slot": "head", "text": "पूरा answer: Notes button", "style": "accent", "at": 39}]))
    return out


CFG = {"A": dict(theme="dossier", plate="dossier-manila"),
       "B": dict(theme="globe-night", plate="globe-night-asia"),
       "C": dict(theme="un-blue", plate="un-hq-blue", presenter_style="card")}


def build(v, part):
    beats = []
    for b in (part1(v) if part == 1 else part2(v)):
        mode, hub = b.get("mode") or "standard", None
        if v == "B":
            hub = {"cy": 1080, "r": 200, "backdrop": "plate"} if mode == "hub" else {"cy": 1500, "r": 250, "backdrop": "plate"}
            mode = "hub"
        els = []
        for e in b["els"]:
            e = dict(e)
            if e.get("at", 0) is None: e["at"] = b["i"]
            if v == "B" and hub["cy"] > 1200 and e["slot"] == "over-broll-low": e["slot"] = "upper"
            els.append(e)
        clip = A_CLIP.get((part, b["id"])) if v == "A" else None
        if clip:
            b["bg"] = {"clip": clip, "region": "top", "treatment": "colour"}
            for e in els:
                e["slot"] = {"head": "over-broll-top", "upper": "over-broll-low"}.get(e["slot"], e["slot"])
        beat = {"id": b["id"], "in": b["i"], "out": b["o"], "presenter": mode, "elements": els}
        if hub: beat["hub"] = hub
        if b.get("bg"): beat["broll"] = b["bg"]
        beats.append(beat)
    plan = {"_about": f"POL-C11-LA-02 part {part}, plan {v}: {CFG[v]['theme']}", "project": "pol-c11-la-02", "part": part,
            "skin": "paper-editorial", **CFG[v],
            "spine": {"title": "विदेश नीति के सिद्धांत", "items": ITEMS, "lit_at": [20] if part == 1 else [4, 13, 21],
                      "show_from": 20 if part == 1 else 0, **({"pre_lit": 1} if part == 2 else {})},
            "beats": beats}
    if part == 1: plan["captions_from"] = 8
    (HERE / f"plan_pol_c11_la_02_{v}_p{part}.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1))


for v in "ABC":
    for part in (1, 2):
        build(v, part)
print("6 plans written")
