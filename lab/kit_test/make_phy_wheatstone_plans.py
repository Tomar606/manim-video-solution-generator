"""PHY: व्हीटस्टोन सेतु / मीटर सेतु (2020, 22, 24, 25): labbook look.

    python lab/kit_test/make_phy_wheatstone_plans.py  ->  plan_phy_wheatstone_p1.json

The two circuits ARE the answer, so they are drawn, not filmed: each part of the bridge appears on
the word that names it, current flows, the galvanometer needle swings and settles at zero at
balance; on the metre bridge the jockey slides along a scaled wire to the null point and l and
100 - l are marked.  Equations are typeset (KaTeX) with every symbol named under them.  Veo carries
the hook (a real needle coming to rest dead centre), the lab, and the two precautions done right
and wrong.  The answer builds point by point.

Timing: until the HeyGen clip arrives, lines_part1.json is an ESTIMATE from the script at speaking
pace, and word cues are found by position in the line (W()).  Re-run tools/kit_captions.py on the
real clip and everything re-anchors; the beats are written against line text, not seconds.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROJ = ROOT / "projects/phy-wheatstone"
L = json.loads((PROJ / "lines_part1.json").read_text())


WORDS = json.loads((PROJ / "words_part1.json").read_text()) if (PROJ / "words_part1.json").exists() else []


def _n(x):
    import re
    return re.sub(r"[^\w]", "", x.replace("हिंदी", "Hindi"), flags=re.U).lower()


def W(i, word, after=0.0):
    """Cue = the moment `word` is spoken in line i, plus `after` seconds.

    From the Whisper word clock when the word is found inside the line's time window (the real
    moment); otherwise by the word's position in the line's text (an estimate)."""
    txt, t0, t1 = L[i]["text"], L[i]["start"], L[i]["end"]
    k = txt.find(word)
    assert k >= 0, (i, word, txt)
    target = _n(word)
    if target:
        # which occurrence of the word in this line (e.g. the second "R"), so repeats map to the right one
        nth = sum(1 for m in range(k) if txt.startswith(word, m))
        hits = [w for w in WORDS if t0 - 0.3 <= w["s"] < t1 + 0.3 and target in _n(w["w"])]
        if len(hits) > nth:
            return [i, round(max(0.0, hits[nth]["s"] - t0) + after, 2)]
    return [i, round((t1 - t0) * k / max(1, len(txt)) + after, 2)]


def V(clip, **k):
    return {"clip": clip, "region": "full", **k}


def hero(kicker, text, at, sub=None, hl=None, fx="rise"):
    e = {"type": "hero", "slot": "upper", "kicker": kicker, "text": text, "at": at, "hl": hl or [], "fx": fx}
    if sub:
        e["sub"] = sub
    return e


ANSWER = ["<b>व्हीटस्टोन सेतु:</b> चार प्रतिरोध <i>P, Q, R, S</i> चतुर्भुज <i>ABCD</i> की भुजाओं में; <i>A–C</i> के बीच सेल व कुंजी, <i>B–D</i> के बीच धारामापी।",
          "<b>सिद्धांत / संतुलन की शर्त:</b> धारामापी में धारा शून्य होने पर सेतु संतुलित होता है, तब $P/Q = R/S$।",
          "<b>उपयोग:</b> अज्ञात प्रतिरोध का मान ज्ञात करना।",
          "<b>मीटर सेतु:</b> 1 m एकसमान तार ताँबे की पट्टियों <i>A, C</i> के बीच; बाएँ <i>R</i>, दाएँ <i>S</i>; पट्टी <i>B</i> से धारामापी व जॉकी।",
          "<b>सिद्धांत:</b> व्हीटस्टोन सेतु; शून्य विक्षेप बिंदु <i>A</i> से <i>l</i> cm पर हो तो $R/S = l/(100-l)$।",
          "<b>सावधानियाँ:</b> (i) जॉकी को तार पर रगड़ें नहीं, हल्के से स्पर्श कराएँ; (ii) संतुलन बिंदु तार के मध्य के पास हो।"]
FULL = "उत्तर: व्हीटस्टोन सेतु / मीटर सेतु"


def sheet(k, at, animate=True, title="उत्तर बन रहा है…"):
    return dict(presenter="standard", plate="lb-blur-lab", tracker=False, elements=[
        {"type": "answer", "slot": "upper", "title": title, "points": ANSWER, "show": k,
         "animate_from": k - 1 if animate else k, "at": at, "gap": 0.45}])


WB_LEGEND = [["P, Q", "भुजा AB और BC के प्रतिरोध", W(20, "Q", 0.3)], ["R, S", "भुजा AD और DC के प्रतिरोध", W(20, "S", 0.3)],
             ["I_g = 0", "धारामापी में धारा शून्य: सेतु संतुलित", W(21, "संतुलन")]]
MB_LEGEND = [["R", "प्रतिरोध बॉक्स का प्रतिरोध", W(33, "R", 0.2)], ["S", "अज्ञात प्रतिरोध", W(33, "S", 0.2)],
             ["l", "A से शून्य विक्षेप बिंदु की दूरी (cm)", W(33, "l by", 0.2)], ["100-l", "तार का शेष भाग (cm)", W(33, "hundred", 0.3)]]

b = []
B = lambda **k: b.append(k)
# ---- hook: the needle coming to rest dead centre (that IS the balance this question is about) ----
B(id="mp", **{"in": 0, "out": 1}, presenter="full", broll=V("c3", dim=True), elements=[       # "MP Board कक्षा 12वीं के बच्चों!"
    {"type": "statemap", "slot": "upper", "state": "Madhya Pradesh", "text": "MP Board", "sub": "कक्षा 12वीं", "w": 880, "top": 170, "at": [0, 0.05]}])
B(id="lab", **{"in": 1, "out": 2}, presenter="standard", broll=V("h2"), elements=[
    {"type": "pill", "slot": "over-broll-low", "text": "पिछली Reel: Hindi", "at": W(1, "Hindi")}])
B(id="physics", **{"in": 2, "out": 3}, presenter="standard", plate="lb-resistors", elements=[
    {"type": "search", "slot": "over-broll-top", "text": "Physics: Important Question", "at": W(2, "Physics"), "cps": 18},
    {"type": "pill", "slot": "over-broll-low", "text": "आज: Physics", "style": "accent", "at": W(2, "Physics", 0.6)}])
B(id="years", **{"in": 3, "out": 6}, presenter="full", plate="lb-blur-lab", elements=[
    # the reference reel's layout: a blurred backdrop, one real exam sheet per year landing in a cascading row, a red year tag on each
    {"type": "papers", "style": "row", "assets": "assets/papers", "at": 3, "top": 340, "left0": 12, "step": 236, "sheet_w": 320, "dy": 34,
     "title": "यही question, board exam में",
     "years": [["2020", W(3, "2020")], ["2022", W(3, "2022")], ["2024", W(3, "2024")], ["2025", W(3, "2025")]],
     "after": "चार बार पूछा गया", "t_after": W(4, "चार"), "after_dy": 470,
     "next": "2027 में भी आ सकता है!", "t_next": W(5, "2027"), "next_dy": 470}])
B(id="pakka", **{"in": 6, "out": 7}, presenter="standard", broll=V("h1", span=[3.0, 7.9]), elements=[   # needle settles at centre on "पक्के"
    hero("इसे समझ लिया तो", "3 नंबर पक्के", W(6, "3 नंबर"), hl=["पक्के"])])
SPLICE = [8, 2.02]     # src/part1.mp4 changes HeyGen take here (src/SPLICE.md): the cut to the question card hides it
B(id="pdf", **{"in": 7, "out": SPLICE}, presenter="full", plate="lb-navy", elements=[      # plain navy: the bench clip read as hands on his head
    {"type": "pdfbadge", "slot": "upper", "text": "ज़रूरी PDF", "sub": "Reel के end में", "top": 140, "at": W(7, "PDF", -0.2)},
    {"type": "note", "slot": "over-broll-top", "text": "Reel पूरी देखना", "at": 8, "fx": "rise"}])
B(id="question", **{"in": SPLICE, "out": 12}, presenter="full", plate="lb-blur-lab", elements=[
    # the question on the original exam-paper sheet, large; each printed line highlights as he reads it
    {"type": "qsheet", "at": SPLICE, "src": "qsheet.png", "src_path": "assets/papers/qsheet.png", "w": 840, "top": 64,
     "hl_left": 0.262, "line_h": 0.046,
     "lines": [[0.686, 0.815, W(9, "व्हीटस्टोन")], [0.745, 0.805, W(10, "संतुलन")], [0.792, 0.805, W(11, "मीटर")], [0.842, 0.595, W(11, "सावधानियाँ")]],
     "marks": "3 अंक", "t_marks": W(11, "सावधानियाँ"), "marks_y": 0.80}])
# ---- Wheatstone bridge: one diagram, built on the words that name each part (captions start here) ----
B(id="who", **{"in": 12, "out": 13}, presenter="full", plate="lb-blur-lab", elements=[
    {"type": "headline", "slot": "head", "text": "पहले: व्हीटस्टोन सेतु", "size": "m", "at": 12, "fx": "drop"},
    {"type": "photo", "slot": "upper", "src": "physics/wheatstone/wheatstone-portrait-1.jpg", "w": 420, "label": "चार्ल्स व्हीटस्टोन (1802–1875)", "at": [12, 0.6]}])
B(id="bridge", **{"in": 13, "out": 17}, presenter="standard", plate="lb-blur-lab", elements=[
    {"type": "wheatstone", "look": "real", "slot": "upper", "at": 13, "sfx": [[0.0, "transition-whoosh/short-sweep"]],
     "t_P": W(13, "P"), "t_Q": W(13, "Q"), "t_R": W(13, "R ", 0), "t_S": W(13, "S"), "t_nodes": W(14, "ABCD"),
     "t_cell": W(15, "सेल"), "t_galv": W(16, "धारामापी")}])
B(id="galvo", **{"in": 17, "out": 18}, presenter="full", plate="lb-blur-lab", elements=[
    {"type": "photo", "slot": "upper", "src": "physics/wheatstone/galvanometer-1.jpg", "w": 640, "label": "धारामापी (G): सुई बीच में = धारा शून्य", "at": 17},
    {"type": "ring", "x": 277, "y": 395, "w": 230, "h": 230, "at": [17, 1.0]}])
B(id="balance-flow", **{"in": 18, "out": 20}, presenter="standard", plate="lb-blur-lab", elements=[
    {"type": "wheatstone", "look": "real", "slot": "upper", "at": 18, "t_P": -10.0, "t_Q": -10.0, "t_R": -10.0, "t_S": -10.0, "t_nodes": -10.0,
     "t_cell": -10.0, "t_galv": -10.0, "t_flow": W(18, "धारा"), "t_null": W(19, "संतुलित")}])
B(id="condition", **{"in": 20, "out": 22}, presenter="hub", plate="lb-blur-lab", elements=[
    # the balanced bridge stays in view while the condition is read: current in all four arms, none through G
    {"type": "wheatstone", "look": "real", "slot": "upper", "at": 20, "scale": 0.5, "top": 150, "t_P": -10.0, "t_Q": -10.0, "t_R": -10.0, "t_S": -10.0,
     "t_nodes": -10.0, "t_cell": -10.0, "t_galv": -10.0, "t_flow": -10.0, "t_null": -10.0},
    {"type": "formula", "slot": "upper", "title": "संतुलन की शर्त", "tex": r"\dfrac{P}{Q}=\dfrac{R}{S}", "at": 20, "top": 560, "compact": True, "legend": WB_LEGEND, "t_glow": W(21, "शर्त")}])
B(id="use", **{"in": 22, "out": [22, 2.5]}, presenter="full", broll=V("u1"), elements=[
    {"type": "pill", "slot": "over-broll-low", "text": "उपयोग: अज्ञात प्रतिरोध का मान ज्ञात करना", "style": "accent", "at": W(22, "उपयोग")},
    {"type": "inset", "src": "physics/wheatstone/multimeter-2.jpg", "w": 340, "label": "आज: मल्टीमीटर", "main_label": "मरम्मत की दुकान", "at": W(22, "अज्ञात")}])
B(id="ans1", **{"in": [22, 2.5], "out": 23}, **sheet(3, [22, 2.5]))
# ---- metre bridge: the real apparatus, then the diagram built part by part, then the null point ----
B(id="real", **{"in": 23, "out": 24}, presenter="full", plate="lb-bridge", elements=[
    {"type": "pill", "slot": "upper", "text": "असली मीटर सेतु: इसी सिद्धांत पर", "style": "accent", "at": W(23, "मीटर"), "sfx": [[0.0, "transition-whoosh/short-sweep"]]},
    {"type": "pins", "items": [[720, 640, "मीटर स्केल (cm)", W(23, "मीटर", 0.8)], [370, 820, "धातु की पट्टियाँ", W(23, "मीटर", 1.4)]]}])
B(id="metre", **{"in": 24, "out": 33}, presenter="standard", plate="lb-blur-lab", elements=[
    {"type": "metrebridge", "look": "real", "slot": "upper", "at": 24, "l": 40,
     "t_wire": W(24, "तार"), "t_strips": W(25, "पट्टियों"), "t_R": W(26, "R"), "t_S": W(27, "S"),
     "t_galv": W(28, "धारामापी"), "t_jockey": W(29, "जॉकी"), "t_cell": W(30, "सेल"),
     "t_slide": W(31, "खिसकाकर"), "t_l": W(32, "l ")}])
B(id="ratio", **{"in": 33, "out": 34}, presenter="hub", plate="lb-blur-lab", elements=[
    {"type": "formula", "slot": "upper", "title": "मीटर सेतु का सूत्र", "tex": r"\dfrac{R}{S}=\dfrac{l}{100-l}", "at": 33, "legend": MB_LEGEND}])
B(id="ans2", **{"in": 34, "out": [34, 2.4]}, **sheet(5, 34))
# ---- precautions: shown done wrong, then right ----
B(id="rub", **{"in": [34, 2.4], "out": 36}, presenter="full", broll=V("c2"), elements=[
    {"type": "headline", "slot": "head", "text": "सावधानी 1", "size": "m", "at": [34, 2.5], "fx": "drop", "sfx": [[0.0, "transition-whoosh/short-sweep"]]},
    {"type": "pill", "slot": "over-broll-low", "text": "जॉकी को तार पर रगड़ना नहीं", "at": W(35, "रगड़ना")},
    {"type": "verdict", "kind": "cross", "x": 760, "y": 640, "at": W(35, "नहीं")}])
B(id="touch", **{"in": 36, "out": 37}, presenter="standard", broll=V("c1"), elements=[
    {"type": "pill", "slot": "over-broll-low", "text": "हल्के से स्पर्श कराना", "style": "accent", "at": W(36, "हल्के")},
    {"type": "verdict", "kind": "tick", "x": 760, "y": 640, "at": W(36, "स्पर्श")}])
B(id="middle", **{"in": 37, "out": 38}, presenter="hub", plate="lb-blur-lab", elements=[
    {"type": "headline", "slot": "head", "text": "सावधानी 2: संतुलन बिंदु बीच में", "size": "m", "at": [37, 0.3], "fx": "drop"},
    {"type": "metrebridge", "look": "real", "slot": "upper", "at": 37, "l": 50, "h": 700, "t_wire": -10.0, "t_strips": -10.0, "t_R": -10.0, "t_S": -10.0,
     "t_galv": -10.0, "t_jockey": -10.0, "t_cell": -10.0, "t_slide": -10.0, "t_l": W(37, "बीच")}])
B(id="ans3", **{"in": 38, "out": [38, 2.6]}, **sheet(6, 38))
B(id="balance", **{"in": [38, 2.6], "out": 39}, presenter="full", broll=V("h3"), elements=[
    hero("दिमाग में बैठा लिया तो", "पूरे 3 नंबर पक्के", W(38, "पूरे"), hl=["पक्के"])])
# ---- the answer page and the asks ----
# "format आपकी screen पर है… screenshot ले लो": the OFFICIAL answer pages (assets/answer, from the sheet), 3 s each
B(id="page1", **{"in": 39, "out": [39, 3.0]}, presenter="full", plate="lb-blur-lab", tracker=False, spine=False, elements=[
    {"type": "page", "src": "assets/answer/WB-1_page.png", "at": 39}])
# page 2 stays up through the whole "इसका screenshot ले लो", until he moves on to the PDF
B(id="page2", **{"in": [39, 3.0], "out": W(40, "PDF")}, presenter="full", plate="lb-blur-lab", tracker=False, spine=False, elements=[
    {"type": "page", "src": "assets/answer/WB-2_page.png", "at": [39, 3.0], "fx": "slide", "badge": "screenshot लो", "t_badge": W(40, "screenshot")}])
B(id="asks", **{"in": W(40, "PDF"), "out": 44}, presenter="hub", plate="lb-blur-lab", tracker=False, elements=[
    {"type": "headline", "slot": "head", "text": "PDF चाहिए? बस 3 काम", "size": "m", "at": W(40, "PDF"), "fx": "drop"},
    {"type": "notify", "slot": "upper", "items": [["tabler:send", "Reel share करो", "दोस्तों के साथ", W(41, "share")], ["tabler:user-plus", "मुझे follow करो", "", W(41, "follow")],
                                                   ["tabler:message-circle", "comment में PDF लिखो", "PDF सीधे आपके DM पर", W(42, "PDF")]]}])
B(id="save", **{"in": 44, "out": "end"}, presenter="full", broll=V("o1"), elements=[
    {"type": "igsave", "slot": "over-broll-top", "text": "Reel save करो", "sub": "exam से पहले revision", "at": [44, 0.3], "t_on": W(44, "save")},
])

plan = {"_about": __doc__.strip().splitlines()[0], "project": "phy-wheatstone", "part": 1, "captions_at": "bottom",
        "skin": "paper-editorial", "theme": "labbook", "presenter_style": "card", "plate": "lb-blur-lab",
        # opens on the MP map, as the user asked (23 Oct): "MP Board कक्षा 12वीं" on Madhya Pradesh over the moving
        # lab macro (copper strips, terminals, resistors).  The needle clip moves to "3 नंबर पक्के", where it comes to rest.
        # the presenter's frames: a copper circuit loop round the card, a galvanometer dial round the hub; "full"
        # beats stand free, anchored bottom centre.  One uniform scale in every mode (memory: presenter-is-never-framed).
        "card_style": {"frame": "circuit", "backdrop": "card-blueprint", "hub_frame": "dial"},
        # framing and colour after the user's reference reel (23 Oct): waist-up, centred, the shot's own light on him
        # the Hindi reference reel's framing (HIN-SM-02): head top ~1110 of 1920, cut at mid-torso, same head size
        "framing": {"crop": [600, 150, 1340, 1000], "full_w": 735},
        # crisp, not washed (user, 23 Oct 2026: "the avatar looks too faded and softened"): contrast up, a light
        # dark-circle lift only, a small tint and wrap, and an unsharp mask inside his outline
        "scene_match": {"tint": 0.07, "wrap": 0.16, "wrap_px": 6},
        # neutral like the reference: no added warmth, brows kept dark ("define"), the dark-circle lift on mid-tone skin only
        "presenter_grade": {"exposure": 1.0, "contrast": 1.03, "warm": 1.0, "saturation": 1.02, "shadow_lift": 0.5, "lift_radius": 14, "define": 0.24,
                            "matte_soft": 1.0, "matte_choke": 0.05, "sharpen": {"radius": 1.0, "percent": 50, "threshold": 3}},
        "hub": {"cx": 540, "cy": 1420, "r": 230, "scale": 0.7, "backdrop": "cards/card-dial.jpg"},
        "card": {"x": 314, "y": 1130, "w": 452, "h": 560},      # bottom CENTRE: he is always centred horizontally
        "spine": {"title": "व्हीटस्टोन + मीटर सेतु", "items": ["परिपथ", "संतुलन शर्त", "उपयोग", "मीटर सेतु", "सूत्र", "सावधानियाँ"],
                  "lit_at": [13, 20, 22, 24, 33, 35], "show_from": 12},
        "beats": b}
(ROOT / "lab/kit_test/plan_phy_wheatstone_p1.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1))
print(len(b), "beats")
