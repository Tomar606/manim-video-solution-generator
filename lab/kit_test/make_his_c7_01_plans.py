"""HIS-C7-SA-01: विजयनगर साम्राज्य की शासन व्यवस्था का वर्णन कीजिए। अथवा, अमर नायक प्रणाली को समझाइए। (2024): hampi look.

    python lab/kit_test/make_his_c7_01_plans.py  ->  plan_his_c7_sa_01_p1.json

The answer is a hierarchy, and the narration ends by saying so: "ऊपर से नीचे की सीढ़ी की तरह याद रखो, सबसे ऊपर
राय, फिर किलों वाले घूमते नायक, और फिर अमर नायक". So the spine of the video is a staircase (the `ladder`
element), drawn exactly rather than generated: it fills in as each rank is introduced, and returns faded at
the recap and lights up rank by rank. The four numbered points follow the answer page: नायक (forts and
armed followers), भ्रमणशील (roaming, peasants following, Telugu or Kannada), प्रभुसत्ता but rebellion, and
the अमर नायक system (territory instead of a salary). The अथवा half of the question gets its own beat, at the
moment the narrator says its whole answer starts here.

The exam sheet carries the main question only. With its अथवा half the question needs five lines, which the
torn sheet cannot hold without cutting it, so the अथवा half is shown on screen when it is spoken.

Look: Hampi. Real photographs (the stone chariot, the stepped tank, the Mahanavami platform, a period bronze
of Krishnadevaraya, a cavalry relief), a sandstone card under a carved granite band studded with gold, laterite
red and pagoda gold. Veo carries the atmosphere: the court, the forts, the roaming columns, the revenue yard.

Timing: lines_part1.json is on the audio's own pauses (tools/pause_align.py; OpenAI Whisper credits exhausted,
26 Oct 2026). Cues use W(line, word): the word clock when words_part1.json exists, else position in the line.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROJ = ROOT / "projects/his-c7-sa-01"
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


def head(text, at_, fx=None):
    e = {"type": "headline", "slot": "head", "text": text, "size": "m", "at": at_}
    if fx:
        e["fx"] = fx
    return e




V = "history/vijayanagara/"
CHARIOT, TANK, DIBBA, RAYA, HORSE = V + "chariot-2.jpg", V + "tank-2.jpg", V + "dibba-1.jpg", V + "krishnadevaraya-2.jpg", V + "virupaksha-3.jpg"
PAGE = "assets/answer/HIS-C7-SA-01-1_page.png"
RAYA_STEP = ["tabler:crown", "राय", "विजयनगर के शासक"]
NAYAK_STEP = ["tabler:building-castle", "नायक", "सेना प्रमुख, किलों के मालिक"]
AMARA_STEP = ["tabler:map-2", "अमर नायक", "वेतन नहीं, इलाका"]
b = []
B = lambda **k: b.append({x: v for x, v in k.items() if v is not None})

# ---- hook: MP Board over Hampi at sunrise ----
B(id="mp", **{"in": 0, "out": 1}, presenter="full", broll=BR("h1", CHARIOT), elements=[
    {"type": "statemap", "slot": "upper", "state": "Madhya Pradesh", "text": "MP Board", "sub": "कक्षा 12वीं", "w": 880, "top": 170, "at": [0, 0.05]}])
# ---- the year on the real exam sheet, then the question ----
B(id="years", **{"in": 1, "out": W(1, "विजयनगर", -0.2)}, presenter="full", broll=BR("e1", dim=True), elements=[
    {"type": "papers", "style": "row", "assets": "assets/papers", "at": 1, "top": 330, "left0": 350, "step": 420, "sheet_w": 380, "dy": 34,
     "title": "यही question, board exam में", "years": [["2024", W(1, "2024")]]}])
B(id="question", **{"in": W(1, "विजयनगर", -0.2), "out": 3}, presenter="full", broll=BR("e1", dim=True), elements=[
    {"type": "qsheet", "at": W(1, "विजयनगर", -0.2), "src": "qsheet.png", "src_path": "assets/papers/qsheet.png", "w": 840, "top": 64,
     "hl_left": 0.262, "line_h": 0.062,
     "lines": [[0.660, 0.792, W(1, "विजयनगर")], [0.736, 0.79, W(1, "शासन")], [0.810, 0.75, W(1, "व्यवस्था")]],
     "marks": "3 अंक", "t_marks": W(2, "अमर"), "marks_y": 0.80}])
# ---- the hook question: a commander paid in territory ----
B(id="hookq", **{"in": 3, "out": 5}, presenter="standard", broll=BR("v1", CHARIOT, dim=True), elements=[
    {"type": "ask", "slot": "upper", "text": "तनख्वाह की जगह पूरा इलाका?", "at": W(3, "तनख्वाह"),
     "answer": "तो शासन कैसे चलेगा?", "t_answer": W(4, "शासन")}])
B(id="amara0", **{"in": 5, "out": 6}, presenter="standard", broll=BR("v1", CHARIOT, dim=True), elements=[
    hero("विजयनगर में", "अमर नायक प्रणाली", W(5, "अमर"), hl=["अमर"])])
# ---- the staircase builds: राय, then नायक ----
B(id="raya", **{"in": 6, "out": 8}, presenter="standard", broll=BR("r1", DIBBA, dim=True), elements=[
    head("शासन की सीढ़ी", 6, "drop"),
    {"type": "ladder", "slot": "upper", "items": [RAYA_STEP + [W(6, "राय")]]},
    {"type": "photo", "slot": "under-upper", "src": RAYA, "w": 380, "label": "जैसे: कृष्णदेवराय", "at": W(7, "शासक")}])
B(id="nayak", **{"in": 8, "out": 12}, presenter="standard", broll=BR("n1", HORSE, dim=True), elements=[
    head("1. नायक", 8, "drop"),
    {"type": "ladder", "slot": "upper", "focus": True, "items": [RAYA_STEP + [8], NAYAK_STEP + [W(8, "नायक")]]},
    {"type": "pills", "slot": "under-upper", "items": [["किलों पर नियंत्रण", W(10, "किलों")], ["हथियारबंद समर्थक", W(11, "हथियारबंद")]]}])
# ---- 2: roaming, peasants follow, Telugu or Kannada ----
B(id="roam", **{"in": 12, "out": 17}, presenter="standard", broll=BR("n2", HORSE, dim=True), elements=[
    head("2. भ्रमणशील नायक", 12, "drop"),
    {"type": "def", "slot": "upper", "term": "भ्रमणशील", "text": "जगह-जगह घूमने वाले", "at": W(13, "भ्रमणशील")},
    {"type": "stamp", "slot": "under-upper", "text": "उपजाऊ ज़मीन की तलाश में किसान भी साथ", "at": W(15, "उपजाऊ"), "fx": "zoom"}])
B(id="lang", **{"in": 17, "out": 18}, presenter="standard", broll=BR("n2", HORSE, dim=True), elements=[
    head("2. भ्रमणशील नायक", 17),
    {"type": "def", "slot": "upper", "term": "भाषा", "text": "तेलुगु या कन्नड़", "at": W(17, "तेलुगु")}])
# ---- 3: sovereignty accepted, rebellion all the same ----
B(id="obey", **{"in": 18, "out": 19}, presenter="standard", broll=BR("r2", DIBBA, dim=True), elements=[
    {"type": "ask", "slot": "upper", "text": "क्या नायक हमेशा राय की बात मानते थे?", "at": W(18, "नायक")}])
B(id="sov", **{"in": 19, "out": 21}, presenter="standard", broll=BR("r2", DIBBA, dim=True), elements=[
    head("3. प्रभुसत्ता, फिर भी विद्रोह", 19, "drop"),
    {"type": "compare", "slot": "upper", "left": ["स्वीकार की", "राय की प्रभुसत्ता"], "right": ["फिर भी", "अक्सर विद्रोह"],
     "at": W(19, "प्रभुसत्ता"), "right_at": W(21, "विद्रोह")}])
B(id="revolt", **{"in": 21, "out": 23}, presenter="standard", broll=BR("w1", HORSE, dim=True), elements=[
    head("3. प्रभुसत्ता, फिर भी विद्रोह", 21),
    {"type": "compare", "slot": "upper", "left": ["स्वीकार की", "राय की प्रभुसत्ता"], "right": ["फिर भी", "अक्सर विद्रोह"],
     "at": 21, "right_at": W(21, "विद्रोह")},
    {"type": "stamp", "slot": "under-upper", "text": "सैन्य कार्रवाई से काबू", "at": W(22, "सैन्य"), "fx": "zoom"}])
# ---- the अथवा flag, then 4: the amara-nayaka system ----
B(id="athva", **{"in": 23, "out": 25}, presenter="standard", broll=BR("a1", CHARIOT, dim=True), elements=[
    {"type": "ask", "slot": "upper", "text": "अथवा: अमर नायक प्रणाली को समझाइए", "at": W(24, "अथवा"),
     "answer": "पूरा जवाब यहीं से", "t_answer": W(24, "पूरा")}])
B(id="amara", **{"in": 25, "out": 27}, presenter="standard", broll=BR("a1", CHARIOT, dim=True), elements=[
    head("4. अमर नायक प्रणाली", 25, "drop"),
    {"type": "def", "slot": "upper", "term": "अमर नायक", "text": "सैनिक कमांडर", "at": W(25, "सैनिक")},
    {"type": "stamp", "slot": "under-upper", "text": "राय से मिला राज्य-क्षेत्र", "at": W(26, "राज्य"), "fx": "zoom"}])
B(id="revenue", **{"in": 27, "out": 29}, presenter="standard", broll=BR("a2", CHARIOT, dim=True), elements=[
    head("इलाके से राजस्व और कर", 27, "drop"),
    {"type": "notify", "slot": "upper", "items": [["tabler:plant-2", "किसान", "", W(27, "किसानों")],
                                               ["tabler:hammer", "शिल्पकर्मी", "", W(28, "शिल्पकर्मियों")],
                                               ["tabler:coins", "व्यापारी", "", W(28, "व्यापारियों")]]}])
B(id="salary", **{"in": 29, "out": 32}, presenter="standard", broll=BR("a3", CHARIOT, dim=True), elements=[
    head("4. अमर नायक प्रणाली", 29),
    {"type": "yn", "slot": "upper", "no": "वेतन", "yes": "पूरा इलाका", "at": W(29, "वेतन"), "t_yes": W(29, "इलाका")},
    {"type": "pills", "slot": "under-upper", "items": [["खुद कमाई", W(31, "कमाई")], ["खुद अपनी सेना पालना", W(31, "सेना")]]}])
B(id="analogy", **{"in": 32, "out": 34}, presenter="full", broll=BR("m1", CHARIOT, dim=True), elements=[
    {"type": "note", "slot": "over-broll-top", "text": "जैसे: कंपनी अपने manager को एक शाखा सौंप दे", "at": W(32, "कंपनी"), "fx": "rise"},
    {"type": "stamp", "slot": "under-upper", "text": "खुद चलाओ, खुद कमाओ", "at": W(33, "चलाओ"), "fx": "zoom"}])
# ---- recap: the whole staircase comes back and lights rank by rank ----
B(id="recap", **{"in": 34, "out": 38}, presenter="standard", broll=BR("s1", TANK, dim=True), elements=[
    head("ऊपर से नीचे की सीढ़ी", 34, "drop"),
    {"type": "ladder", "slot": "upper", "ghost": True, "focus": True, "at": 34, "items": [
        RAYA_STEP[:2] + ["सबसे ऊपर", W(35, "सबसे")], NAYAK_STEP[:2] + ["किलों वाले, घूमते", W(36, "नायक")],
        AMARA_STEP + [W(36, "अमर")]]}])
B(id="sure", **{"in": 38, "out": 40}, presenter="standard", broll=BR("k1", TANK, dim=True), elements=[
    hero("exam में अच्छे से लिख दिया, तो", "पूरे 3 नंबर पक्के", W(39, "3"), hl=["पक्के"])])
# ---- the exact answer: the page at "answer ... Notes बटन", to the end ----
if (PROJ / PAGE).exists():
    B(id="page", **{"in": 40, "out": "end"}, presenter="full", tracker=False, spine=False, elements=[
        {"type": "page", "src": PAGE, "at": 40, "badge": "Notes बटन में", "t_badge": W(41, "Notes")}])
else:
    B(id="notes", **{"in": 40, "out": "end"}, presenter="standard", broll=BR("k1", TANK, dim=True), tracker=False, elements=[
        {"type": "pdfbadge", "slot": "upper", "text": "Exact answer", "sub": "Notes बटन में मिलेगा", "top": 110, "at": W(41, "answer")}])

plan = {"_about": __doc__.strip().splitlines()[0], "project": "his-c7-sa-01", "part": 1, "captions_at": "bottom",
        "skin": "paper-editorial", "theme": "hampi", "presenter_style": "card", "plate": "hp-chariot",
        **({} if has("h1") else {"hook": "exempt"}),     # until the opening Veo clip exists, a real photo stands in
        "hilite": ["राय", "नायक", "किलों", "भ्रमणशील", "तेलुगु", "कन्नड़", "प्रभुसत्ता", "विद्रोह", "अथवा", "अमर नायक", "वेतन", "इलाका", "राजस्व", "पक्के"],
        "card_style": {"backdrop": "hp-card"},
        # the Hindi reference reel's framing (HIN-SM-02), as approved for the Molarity reel
        "framing": {"crop": [600, 150, 1340, 1000], "full_w": 735},
        "scene_match": {"tint": 0.05, "wrap": 0.12, "wrap_px": 6},
        # the Molarity reel's approved grade (true to source, softened, contrast eased: user, 24 Oct 2026)
        "presenter_grade": {"exposure": 1.0, "contrast": 0.94, "warm": 0.99, "saturation": 0.96, "shadow_lift": 0.4, "lift_radius": 14,
                            "define": 0.04, "matte_soft": 1.0, "matte_choke": 0.05, "soften": {"amount": 0.55, "radius": 1.8}},
        "card": {"x": 314, "y": 1130, "w": 452, "h": 560},      # bottom centre: he is always centred horizontally
        "spine": {"title": "विजयनगर की शासन व्यवस्था", "items": ["नायक: सेना प्रमुख", "भ्रमणशील नायक", "प्रभुसत्ता, फिर भी विद्रोह", "अमर नायक: इलाका"],
                  "lit_at": [12, 18, 23, 32], "show_from": 8},
        "beats": b}
(ROOT / "lab/kit_test/plan_his_c7_sa_01_p1.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1))
print(len(b), "beats")
