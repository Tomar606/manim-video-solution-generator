"""HIS-C11-SA-01: किस प्रकार गाँधी जी एक जननेता बन गये? अथवा, किसान महात्मा गाँधी को किस तरह देखते थे? (2022, 2024, 2025): khadi look.

    python lab/kit_test/make_his_c11_01_plans.py  ->  plan_his_c11_sa_01_p1.json

The answer is four reasons, and the narration names them twice: once as it teaches them and once as a
one-line recap ("धोती और आम भाषा, किसानों के गाँधी बाबा, चरखा और श्रम, और सबको साथ लेकर चलना").  That
recap wording is the spine, so the corner list, the recap and the hero cards say each point the same way.
The अथवा question is answered by reason 2, and the narration says so ("यहाँ से अथवा वाले सवाल का जवाब
निकलता है"): that moment gets its own beat.  Each reason closes on the ACTUAL answer page, cropped to that
point (reviewer, 22 Oct 2026), and the whole page closes the video.  The look is the period itself: real
1930 photographs (Dandi, the Salt March, a village charkha) in sepia, unbleached-khadi cards, the saffron
and green of the 1931 charkha flag.

Timing: lines_part1.json is on the HeyGen SRT clock (OpenAI Whisper credits exhausted, 25 Oct 2026).  Cues
use W(line, word): the Whisper word clock when words_part1.json exists, else the word's position in its line,
so re-running the word clock re-anchors every cue without touching this file.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROJ = ROOT / "projects/his-c11-sa-01"
L = json.loads((PROJ / "lines_part1.json").read_text())
WORDS = json.loads((PROJ / "words_part1.json").read_text()) if (PROJ / "words_part1.json").exists() else []


def _n(x):
    return re.sub(r"[^\w]", "", x, flags=re.U).lower()


def W(i, word, after=0.0):
    """Cue = the moment `word` is spoken in line i, plus `after` seconds (word clock if present, else by position)."""
    txt, t0, t1 = L[i]["text"], L[i]["start"], L[i]["end"]
    k = txt.find(word)
    assert k >= 0, (i, word, txt)
    target = _n(word)
    if target and WORDS:
        nth = sum(1 for m in range(k) if txt.startswith(word, m))
        hits = [w for w in WORDS if t0 - 0.3 <= w["s"] < t1 + 0.3 and target in _n(w["w"])]
        if len(hits) > nth:
            return [i, round(max(0.0, hits[nth]["s"] - t0) + after, 2)]
    return [i, round((t1 - t0) * k / max(1, len(txt)) + after, 2)]


def has(clip):
    return any((PROJ / d / f"{clip}.mp4").exists() for d in ("diagrams", "veo/clean", "veo/clips"))


def BR(clip, photo=None, **k):
    """The beat's footage: its Veo clip once generated; until then a real photograph, or the plate (None)."""
    if has(clip):
        return {"clip": clip, "region": "full", **k}
    return {"photo": photo, "region": "full", **k} if photo else None


def hero(kicker, text, at_, hl=None, sub=None, fx="rise"):
    e = {"type": "hero", "slot": "upper", "kicker": kicker, "text": text, "at": at_, "hl": hl or [], "fx": fx}
    if sub:
        e["sub"] = sub
    return e


def crop(n, at_, label):
    """The real answer page, cropped to point n: what the student writes for the point just taught."""
    return {"type": "photo", "slot": "upper", "src": f"history/c11/ans-{n}.jpg", "w": 932, "label": label, "at": at_}


G = "history/gandhi/"
b = []
B = lambda **k: b.append({x: v for x, v in k.items() if v is not None})

# ---- hook: MP Board over the Salt March ----
B(id="mp", **{"in": 0, "out": 1}, presenter="full", broll=BR("h1", G + "dandi-3.jpg"), elements=[
    {"type": "statemap", "slot": "upper", "state": "Madhya Pradesh", "text": "MP Board", "sub": "कक्षा 12वीं", "w": 880, "top": 170, "at": [0, 0.05]}])
# ---- the years: one real exam sheet per year ----
B(id="years", **{"in": 1, "out": 4}, presenter="full", broll=BR("e1", dim=True), elements=[
    {"type": "papers", "style": "row", "assets": "assets/papers", "at": 1, "top": 330, "left0": 22, "step": 330, "sheet_w": 360, "dy": 34,
     "title": "यही question, board exam में",
     "years": [["2022", W(1, "2022")], ["2024", W(2, "2024")], ["2025", W(2, "2025")]],
     "after": "तीनों साल पूछा गया", "t_after": W(2, "पूछा"), "after_dy": 490,
     "next": "2027 में भी आ सकता है!", "t_next": W(3, "2027"), "next_dy": 490}])
B(id="marks", **{"in": 4, "out": 6}, presenter="standard", broll=BR("h1", G + "dandi-2.jpg", dim=True), elements=[
    hero("इसे अच्छे से समझ लिया तो", "3 नंबर पक्के", W(5, "3"), hl=["पक्के"])])
# ---- the question on the paper; both halves highlight as he reads them ----
B(id="question", **{"in": 6, "out": 8}, presenter="full", broll=BR("e1", dim=True), elements=[
    {"type": "qsheet", "at": 6, "src": "qsheet.png", "src_path": "assets/papers/qsheet.png", "w": 840, "top": 64,
     "hl_left": 0.264, "line_h": 0.055,
     "lines": [[0.662, 0.735, W(6, "किस")], [0.719, 0.742, W(6, "जननेता")], [0.776, 0.735, W(7, "किसान")], [0.833, 0.645, W(7, "महात्मा")]],
     "marks": "3 अंक", "t_marks": W(7, "किसान"), "marks_y": 0.80}])
# ---- what a जननेता is, and what Gandhi became ----
B(id="janneta", **{"in": 8, "out": 9}, presenter="standard", broll=BR("v0", G + "dandi-3.jpg", dim=True), elements=[
    {"type": "def", "slot": "upper", "term": "जननेता", "text": "वो नेता, जिसे आम जनता अपना माने", "at": W(8, "जननेता")}])
B(id="gandhi_jan", **{"in": 9, "out": 10}, presenter="standard", broll=BR("v0", G + "dandi-3.jpg", dim=True), elements=[
    {"type": "photo", "slot": "upper", "src": G + "dandi-3.jpg", "w": 880, "label": "आम जनता के बीच महात्मा गाँधी (1930)", "at": 9}])
B(id="masiha", **{"in": 10, "out": 12}, presenter="standard", broll=BR("v0", G + "dandi-3.jpg", dim=True), elements=[
    {"type": "yn", "slot": "upper", "no": "सिर्फ राजनेता", "yes": "चमत्कारी मसीहा", "at": W(10, "सिर्फ"), "t_yes": W(11, "चमत्कारी")}])
B(id="four", **{"in": 12, "out": 13}, presenter="standard", broll=BR("v0", G + "dandi-3.jpg", dim=True), elements=[
    hero("इसके पीछे", "4 वजहें", W(12, "चार"), hl=["4"])])
# ---- 1: रहन-सहन (dress and language) ----
B(id="p1", **{"in": 13, "out": 14}, presenter="standard", broll=BR("s0", G + "gandhi-dhoti-1.jpg", dim=True), elements=[
    hero("पहली वजह", "रहन-सहन", W(13, "रहन"), hl=["रहन-सहन"])])
B(id="suit", **{"in": 14, "out": 15}, presenter="standard", broll=BR("s1", dim=True), elements=[
    {"type": "headline", "slot": "head", "text": "1. धोती और आम भाषा", "size": "m", "at": 14, "fx": "drop"},
    {"type": "compare", "slot": "upper", "left": ["दूसरे नेता", "पश्चिमी सूट"], "right": ["गाँधी जी", "साधारण धोती"],
     "at": W(14, "दूसरे"), "right_at": W(14, "गाँधी")}])
B(id="dhoti", **{"in": 15, "out": 16}, presenter="standard", broll=BR("s0", G + "gandhi-dhoti-1.jpg", dim=True), elements=[
    {"type": "headline", "slot": "head", "text": "1. धोती और आम भाषा", "size": "m", "at": 15},
    {"type": "photo", "slot": "upper", "src": G + "gandhi-khadi-dhoti-real.jpg", "w": 800, "label": "साधारण खादी धोती में महात्मा गाँधी", "at": 15}])
B(id="bhasha", **{"in": 16, "out": 17}, presenter="full", broll=BR("s2", G + "gandhi-dhoti-3.jpg"), elements=[
    {"type": "pill", "slot": "over-broll-low", "text": "उन्हीं की भाषा में बात", "style": "accent", "at": W(16, "भाषा")}])
B(id="ans1", **{"in": 17, "out": 18}, presenter="standard", broll=BR("s0", G + "gandhi-dhoti-1.jpg", dim=True), elements=[
    crop(1, 17, "Answer में: बिंदु 1")])
# ---- the अथवा flag, then 2: किसानों के गाँधी बाबा ----
B(id="athva", **{"in": 18, "out": 20}, presenter="standard", broll=BR("v1", G + "champaran-1.jpg", dim=True), elements=[
    {"type": "ask", "slot": "upper", "text": "अथवा: किसान गाँधी जी को कैसे देखते थे?", "at": W(18, "अथवा"),
     "answer": "जवाब यहीं से, ध्यान से सुनो", "t_answer": W(19, "ध्यान")}])
B(id="rumour", **{"in": 20, "out": [22, 2.0]}, presenter="full", broll=BR("v1", G + "champaran-1.jpg"), elements=[
    {"type": "headline", "slot": "head", "text": "2. किसानों के गाँधी बाबा", "size": "m", "at": 20, "fx": "drop"},
    {"type": "notify", "slot": "upper", "items": [["tabler:message-circle", "अफ़वाह फैली", "किसानों के बीच", W(20, "अफ़वाह")],
                                               ["tabler:crown", "राजा ने भेजा है", "", W(21, "राजा")],
                                               ["tabler:sparkles", "चमत्कारी शक्तियाँ", "", W(22, "चमत्कारी")]]}])
B(id="baba", **{"in": [22, 2.0], "out": 23}, presenter="standard", broll=BR("v1", G + "champaran-1.jpg", dim=True), elements=[
    hero("किसान उन्हें कहते थे", "गाँधी बाबा, महात्मा", W(22, "गाँधी बाबा"), hl=["बाबा,", "महात्मा"])])
B(id="mukti", **{"in": 23, "out": [24, 0.9]}, presenter="standard", broll=BR("v2", dim=True), elements=[
    {"type": "yn", "slot": "upper", "no": "भारी लगान, ज़मींदारों का अत्याचार", "yes": "मुक्ति दिलाएँगे", "at": W(23, "भारी"), "t_yes": W(24, "मुक्ति")}])
B(id="ans2", **{"in": [24, 0.9], "out": [25, 0.9]}, presenter="standard", broll=BR("v1", G + "champaran-1.jpg", dim=True), elements=[
    crop(2, [24, 0.9], "Answer में: बिंदु 2 (अथवा का जवाब)")])
# ---- 3: चरखा और श्रम ----
B(id="charkha", **{"in": [25, 0.9], "out": 27}, presenter="standard", broll=BR("c1", G + "gandhi-charkha-real-1.jpg", dim=True), elements=[
    {"type": "headline", "slot": "head", "text": "3. चरखा और श्रम", "size": "m", "at": [25, 0.9], "fx": "drop"},
    {"type": "photo", "slot": "upper", "src": G + "gandhi-charkha-real-1.jpg", "w": 800, "label": "चरखा चलाते महात्मा गाँधी", "at": [25, 0.9]}])
B(id="haath", **{"in": 27, "out": 29}, presenter="full", broll=BR("c2", G + "khadi-3.jpg"), elements=[
    {"type": "note", "slot": "over-broll-top", "text": "खुद हाथ से काम = शारीरिक श्रम", "at": W(27, "हाथ"), "fx": "rise"}])
B(id="judav", **{"in": 29, "out": 31}, presenter="standard", broll=BR("c1", G + "charkha-gandhi-1.jpg", dim=True), elements=[
    {"type": "pills", "slot": "upper", "items": [["गरीब मज़दूर", W(29, "मज़दूरों")], ["किसान", W(29, "किसानों")], ["दस्तकार", W(30, "दस्तकारों")]]},
    {"type": "stamp", "slot": "under-upper", "text": "गहरा भावनात्मक जुड़ाव", "at": W(30, "भावनात्मक"), "fx": "zoom"}])
B(id="teacher", **{"in": 31, "out": [32, 1.2]}, presenter="full", broll=BR("t1", dim=True), elements=[
    {"type": "note", "slot": "over-broll-top", "text": "जैसे: ज़मीन पर बैठकर पढ़ाने वाले teacher", "at": W(31, "teacher"), "fx": "rise"},
    {"type": "pill", "slot": "over-broll-low", "text": "बच्चे उन्हें अपना मानते हैं", "at": W(32, "अपना")}])
B(id="ans3", **{"in": [32, 1.2], "out": [33, 1.6]}, presenter="standard", broll=BR("c1", G + "charkha-gandhi-1.jpg", dim=True), elements=[
    crop(3, [32, 1.2], "Answer में: बिंदु 3")])
# ---- 4: सबको साथ ----
B(id="p4", **{"in": [33, 1.6], "out": 34}, presenter="standard", broll=BR("m1", G + "dandi-3.jpg", dim=True), elements=[
    {"type": "headline", "slot": "head", "text": "4. सबको साथ", "size": "m", "at": [33, 1.6], "fx": "drop"},
    {"type": "yn", "slot": "upper", "no": "सिर्फ अमीर और पढ़े-लिखे", "yes": "सबको शामिल किया", "at": W(33, "सिर्फ"), "t_yes": W(34, "बल्कि")}])
B(id="sab", **{"in": 34, "out": 36}, presenter="full", broll=BR("m1", G + "dandi-1.jpg", dim=True), elements=[
    {"type": "photo", "slot": "over-broll-top", "src": G + "gandhi-dhoti-3.jpg", "w": 680, "label": "हरिजन यात्रा में गाँधी जी (मद्रास)", "at": 34},
    {"type": "pills", "slot": "over-broll-low", "items": [["महिलाएँ", W(34, "महिलाओं")], ["किसान", W(34, "किसानों")],
                                                       ["मज़दूर", W(34, "मज़दूरों")], ["अछूत (हरिजन)", W(35, "हरिजन")]]}])
B(id="ans4", **{"in": 36, "out": 37}, presenter="standard", broll=BR("m1", G + "dandi-3.jpg", dim=True), elements=[
    crop(4, 36, "Answer में: बिंदु 4"),
    {"type": "stamp", "slot": "under-upper", "text": "सच्चा जन-आंदोलन", "at": W(36, "जन-आंदोलन"), "fx": "zoom"}])
# ---- recap, the page, the asks ----
B(id="recap", **{"in": 37, "out": 40}, presenter="standard", broll=BR("v0", G + "dandi-3.jpg", dim=True), elements=[
    {"type": "headline", "slot": "head", "text": "चारों वजहें, एक लाइन में", "size": "m", "at": 37, "fx": "drop"},
    {"type": "checklist", "slot": "upper", "lit": [], "at": 37,
     "lit_t": [W(37, "धोती"), W(38, "गाँधी बाबा"), W(38, "चरखा"), W(39, "सबको")]},
    {"type": "stamp", "slot": "under-upper", "text": "चारों बिंदु याद!", "at": W(38, "गाँधी बाबा"), "fx": "zoom"}])
B(id="sure", **{"in": 40, "out": 42}, presenter="standard", broll=BR("h1", G + "dandi-2.jpg", dim=True), elements=[
    hero("दिमाग में बैठा लिया तो", "पूरे 3 नंबर पक्के", W(41, "पूरे"), hl=["पक्के"])])
B(id="page1", **{"in": 42, "out": [42, 2.2]}, presenter="full", tracker=False, spine=False, elements=[
    {"type": "page", "src": "assets/answer/HIS-C11-SA-01-1_page.png", "at": 42}])
B(id="page2", **{"in": [42, 2.2], "out": W(43, "PDF", -0.3)}, presenter="full", tracker=False, spine=False, elements=[
    {"type": "page", "src": "assets/answer/HIS-C11-SA-01-2_page.png", "at": [42, 2.2], "fx": "slide", "badge": "screenshot लो", "t_badge": [42, 2.6]}])
B(id="pdf", **{"in": W(43, "PDF", -0.3), "out": 48}, presenter="standard", broll=BR("p1", dim=True), tracker=False, elements=[
    {"type": "pdfbadge", "slot": "upper", "text": "Answer की PDF", "sub": "बस 3 काम करने होंगे", "top": 110, "at": W(43, "PDF", -0.2)},
    {"type": "stamp", "slot": "under-upper", "text": "एक भी छूटा तो PDF नहीं", "at": W(45, "छूट"), "fx": "zoom"}])
B(id="asks", **{"in": 48, "out": 52}, presenter="standard", broll=BR("p1", dim=True), tracker=False, elements=[
    {"type": "headline", "slot": "head", "text": "PDF के लिए बस 3 काम", "size": "m", "at": 48, "fx": "drop"},
    {"type": "notify", "slot": "upper", "items": [["tabler:send", "Reel share करो", "दोस्तों के साथ", W(48, "Share")],
                                               ["tabler:user-plus", "मुझे follow करो", "", W(49, "Follow")],
                                               ["tabler:message-circle", "comment में PDF लिखो", "PDF सीधे आपके DM पर", W(49, "Comment")]]}])
B(id="save", **{"in": 52, "out": "end"}, presenter="full", broll=BR("r1", G + "khadi-3.jpg"), elements=[
    {"type": "igsave", "slot": "over-broll-top", "text": "Reel save करो", "sub": "exam से पहले revision", "at": [52, 0.3], "t_on": W(52, "Save")}])

plan = {"_about": __doc__.strip().splitlines()[0], "project": "his-c11-sa-01", "part": 1, "captions_at": "bottom",
        "skin": "paper-editorial", "theme": "khadi", "presenter_style": "card", "plate": "kh-salt",
        **({} if has("h1") else {"hook": "exempt"}),     # until the opening Veo clip exists, a real photo stands in
        "hilite": ["जननेता", "मसीहा", "धोती", "भाषा", "अथवा", "गाँधी बाबा", "महात्मा", "लगान", "चरखा", "श्रम", "हरिजन", "जन-आंदोलन", "PDF"],
        "card_style": {"backdrop": "kh-card"},
        # the Hindi reference reel's framing (HIN-SM-02), as approved for the Molarity reel
        "framing": {"crop": [600, 150, 1340, 1000], "full_w": 735},
        "scene_match": {"tint": 0.05, "wrap": 0.12, "wrap_px": 6},
        # the Molarity reel's approved grade (true to source, softened, contrast eased: user, 24 Oct 2026)
        "presenter_grade": {"exposure": 1.0, "contrast": 0.94, "warm": 0.99, "saturation": 0.96, "shadow_lift": 0.4, "lift_radius": 14,
                            "define": 0.04, "matte_soft": 1.0, "matte_choke": 0.05, "soften": {"amount": 0.55, "radius": 1.8}},
        "card": {"x": 314, "y": 1130, "w": 452, "h": 560},      # bottom centre: he is always centred horizontally
        "spine": {"title": "जननेता गाँधी", "items": ["धोती और आम भाषा", "किसानों के गाँधी बाबा", "चरखा और श्रम", "सबको साथ"],
                  "lit_at": [17, 24, 31, 36], "show_from": 13},
        "beats": b}
(ROOT / "lab/kit_test/plan_his_c11_sa_01_p1.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1))
print(len(b), "beats")

