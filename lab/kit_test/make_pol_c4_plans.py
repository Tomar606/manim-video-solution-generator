"""Three different plans for POL-C4-LA-05 from one beat list.
   A  un-blue      clip-led: Veo footage under most beats, presenter in a card
   B  newsprint    photo-led: real archival/press photos as prints, free-standing presenter
   C  globe        diagram-led: the four functions fill a 2x2 around him in a circle"""
import json
from pathlib import Path
HERE = Path(__file__).parent
ITEMS = ["शांति की स्थापना", "गैर-राजनीतिक कार्य", "सांस्कृतिक आदान-प्रदान", "अवैध व्यापार पर प्रतिबंध"]
QUAD = lambda times: {"type": "quad", "slot": "around-hub", "nums": ["1", "2", "3", "4"],
    "icons": ["tabler:shield", "tabler:heart-handshake", "tabler:masks-theater", "tabler:ban"],
    "items": [["शांति की स्थापना", "युद्ध रोककर विश्व में शांति", times[0]], ["गैर-राजनीतिक", "स्वास्थ्य, आर्थिक सहयोग, शोषण, शरणार्थी", times[1]],
              ["सांस्कृतिक आदान-प्रदान", "सभ्यता और संस्कृति का लेन-देन", times[2]], ["अवैध व्यापार पर रोक", "नशीली वस्तुओं के व्यापार पर", times[3]]]}
FAR = 999
B_CLIPS = {"v04", "v05"}   # generated for plan B: refugee camp, yoga crowd   # a cue past the end: the cell stays empty in this part


def bg(v, clip=None, photo=None, dim=False):
    if v == "A" and clip: return {"clip": clip, "region": "full", "dim": dim}
    if v == "B" and photo: return {"photo": photo, "region": "top", "treatment": "duotone-navy"}
    if v == "B" and clip in B_CLIPS: return {"clip": clip, "region": "top", "treatment": "duotone-navy"}
    if v == "C" and clip: return {"clip": clip, "region": "full", "dim": True}
    return None


def overview(v, lit, lit_t=None, slot="upper", times=None):
    if v == "C":
        return QUAD(times)
    e = {"type": "checklist", "slot": slot, "lit": lit, "at": None}
    if lit_t: e["lit_t"] = lit_t
    return e


def part1(v):
    P = "political-science/united-nations/"
    B = [
     dict(id="hook", i=0, o=5, bg=bg(v, "v01", P + "peacekeepers-2.jpg"),
          els=[{"type": "note", "slot": "over-broll-top" if v != "C" else "head", "text": "दो देशों में लड़ाई की खबर", "at": 1},
               {"type": "pill", "slot": "over-broll-low" if v != "C" else "upper", "text": "UN: संयुक्त राष्ट्र संघ", "style": "accent", "at": 3}]),
     dict(id="question", i=5, o=8, bg=bg(v, "v02", P + "assembly-1.jpg", dim=True), mode="small",
          els=[{"type": "qcard", "slot": "upper", "question": "संयुक्त राष्ट्र संघ के कोई चार कार्य लिखिए।", "year": "2023", "marks": "4 अंक", "t_marks": [6, 0.3], "at": 5}]),
     dict(id="structure", i=8, o=10,
          els=[{"type": "headline", "slot": "head", "text": "answer का ढाँचा", "size": "m", "at": 8},
               {"type": "chain", "slot": "upper", "items": [["1. छोटा सा परिचय", 8], ["2. चार कार्य", 9]]}]),
     dict(id="intro", i=10, o=13, bg=bg(v, "v02", P + "charter-3.jpg"),
          els=[{"type": "def", "slot": "over-broll-top" if bg(v, "v02", P + "charter-3.jpg") else "head", "term": "संयुक्त राष्ट्र संघ", "text": "अंतर्राष्ट्रीय संगठन", "at": 10},
               {"type": "pills", "slot": "over-broll-low" if bg(v, "v02", P + "charter-3.jpg") else "upper", "items": [["स्थापना 1945", 11], ["विश्व शांति", [11, 1.6]], ["सुरक्षा", 12], ["सहयोग", [12, 1.2]]], "style": "accent"}]),
     dict(id="four", i=13, o=15, mode="hub" if v == "C" else None,
          els=[{"type": "headline", "slot": "head", "text": "अब मुख्य भाग: चार कार्य", "size": "m", "at": 14},
               overview(v, [], times=[FAR, FAR, FAR, FAR])]),
     dict(id="f1", i=15, o=18, bg=bg(v, "v01", P + "peacekeepers-1.jpg"),
          els=[{"type": "section", "slot": "over-broll-top" if bg(v, "v01", P + "peacekeepers-1.jpg") else "head", "num": "1", "text": "शांति की स्थापना", "at": 15},
               {"type": "chain", "slot": "over-broll-low" if bg(v, "v01", P + "peacekeepers-1.jpg") else "upper", "items": [["युद्ध को रोकना", 16], ["विश्व में शांति", [16, 1.6]], ["सहानुभूतिपूर्ण संबंध", 17]]}]),
     dict(id="f1-word", i=18, o=19,
          els=[{"type": "def", "slot": "head", "term": "सहानुभूतिपूर्ण", "text": "एक-दूसरे की तकलीफ़ समझने वाला", "at": 18}]),
     dict(id="f1-first", i=19, o=21, mode="hub" if v == "C" else None,
          els=[{"type": "stamp", "slot": "upper" if v != "C" else "hub-below", "text": "मुख्य कार्य: सबसे पहले लिखो", "at": 19}] +
              ([QUAD([19, FAR, FAR, FAR])] if v == "C" else [])),
     dict(id="teaser", i=21, o="end", mode="hub" if v == "C" else None,
          els=[{"type": "headline", "slot": "head", "text": "एक हो गया, तीन बाकी", "size": "m", "at": 21},
               overview(v, [0], times=[0, FAR, FAR, FAR]),
               {"type": "pill", "slot": "center-low" if v == "C" else "under-upper", "text": "बाकी तीन: Part 2", "style": "accent", "at": 22}]),
    ]
    return B


def part2(v):
    P = "political-science/united-nations/"
    B = [
     dict(id="bridge", i=0, o=4, mode="hub" if v == "C" else None,
          els=[{"type": "headline", "slot": "head", "text": "एक हो गया, तीन बाकी", "size": "m", "at": 0}, overview(v, [0], times=[0, FAR, FAR, FAR])]),
     dict(id="f2", i=4, o=8, bg=bg(v, "v03", None),
          els=[{"type": "note", "slot": "over-broll-top" if v == "A" else "head", "text": "राजनीति से कोई लेना-देना नहीं", "at": 5},
               {"type": "section", "slot": "over-broll-low" if v == "A" else "upper", "num": "2", "text": "गैर-राजनीतिक कार्य", "at": 6}]),
     dict(id="f2-tiles", i=8, o=11,
          els=[{"type": "section", "slot": "head", "num": "2", "text": "गैर-राजनीतिक कार्य", "at": 8},
               {"type": "tiles", "slot": "upper", "cols": 2, "items": [["tabler:stethoscope", "स्वास्थ्य", [8, 0.2]], ["tabler:coin", "आर्थिक सहयोग", [8, 1.8]],
                                                                       ["tabler:mood-kid", "स्त्री-बच्चों का शोषण रोकना", 9], ["tabler:tent", "शरणार्थी समस्या", 10]]}]),
     dict(id="refugee", i=11, o=14, bg=bg(v, "v04", None),
          els=[{"type": "def", "slot": "over-broll-low" if v in "AB" else "upper", "term": "शरणार्थी", "text": "युद्ध या संकट से घर-देश छोड़ने वाले", "at": 11}]),
     dict(id="two-done", i=14, o=16, mode="hub" if v == "C" else None,
          els=[overview(v, [0, 1], times=[0, 14, FAR, FAR])]),
     dict(id="f3", i=16, o=20, bg=bg(v, "v05", None),
          els=[{"type": "section", "slot": "over-broll-top" if v in "AB" else "head", "num": "3", "text": "सांस्कृतिक आदान-प्रदान", "at": 16},
               {"type": "pills", "slot": "over-broll-low" if v in "AB" else "upper", "items": [["सभ्यता का लेन-देन", 17], ["संस्कृति का लेन-देन", [17, 1.8]], ["विश्व संस्कृति", 18]], "style": "accent"},
               {"type": "note", "slot": "over-broll" if v in "AB" else "under-upper", "text": "जैसे: योग पूरी दुनिया तक पहुँचा", "at": 19}]),
     dict(id="f4", i=20, o=23, bg=bg(v, "v06", P + "drugs-1.jpg"),
          els=[{"type": "section", "slot": "over-broll-top" if bg(v, "v06", P + "drugs-1.jpg") else "head", "num": "4", "text": "अवैध व्यापार पर प्रतिबंध", "at": 20},
               {"type": "stamp", "slot": "over-broll" if bg(v, "v06", P + "drugs-1.jpg") else "upper", "text": "नशीली वस्तुओं के व्यापार पर रोक", "at": 22}]),
     dict(id="recap", i=23, o=28, mode="hub" if v == "C" else None,
          els=[{"type": "headline", "slot": "head", "text": "चारों कार्य, क्रम से", "size": "m", "at": 23},
               overview(v, [], lit_t=[24, 25, 26, 27], times=[24, 25, 26, 27])]),
     dict(id="marks", i=28, o=30, bg=bg(v, "v02", P + "unhq-1.jpg", dim=True),
          els=[{"type": "stamp", "slot": "over-broll" if bg(v, "v02", P + "unhq-1.jpg") else "upper", "text": "4 नंबर पक्के", "at": 29}]),
     dict(id="outro", i=30, o="end", mode="hero" if v != "C" else None,
          els=[{"type": "pill", "slot": "head", "text": "पूरा answer: Notes button", "style": "accent", "at": 31}]),
    ]
    return B


CFG = {"A": dict(theme="un-blue", plate="un-hq-blue", presenter_style="card"),
       "B": dict(theme="paper-archival", plate="paper-archival-folded"),
       "C": dict(theme="globe-night", plate="globe-night-asia")}


def build(v, part):
    beats = []
    for b in (part1(v) if part == 1 else part2(v)):
        mode = b.get("mode") or "standard"
        hub = None
        if v == "C":
            if mode == "hub":
                hub = {"cy": 960, "r": 200}
            else:
                mode, hub = "hub", {"cy": 1500, "r": 250}      # C: always in a circle, low centre
        els = []
        for e in b["els"]:
            e = dict(e)
            if e.get("at", 0) is None: e["at"] = b["i"]
            els.append(e)
        if v == "C" and mode == "hub" and hub["cy"] > 1200:
            for e in els:                                     # content stays above the low circle
                if e["slot"] in ("over-broll-low",): e["slot"] = "upper"
        beat = {"id": b["id"], "in": b["i"], "out": b["o"], "presenter": mode, "elements": els}
        if hub: beat["hub"] = hub
        if b.get("bg"): beat["broll"] = b["bg"]
        beats.append(beat)
    plan = {"_about": f"POL-C4-LA-05 part {part}, plan {v}: {CFG[v]['theme']}", "project": "pol-c4-la-05", "part": part,
            "skin": "paper-editorial", **CFG[v],
            "spine": {"title": "UN के चार कार्य", "items": ITEMS, "lit_at": [15] if part == 1 else [6, 16, 20],
                      "show_from": 13 if part == 1 else 0, **({"pre_lit": 1} if part == 2 else {})},
            "beats": beats}
    if part == 1: plan["captions_from"] = 8
    (HERE / f"plan_pol_c4_la_05_{v}_p{part}.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1))


for v in "ABC":
    for part in (1, 2):
        build(v, part)
print("6 plans written")
