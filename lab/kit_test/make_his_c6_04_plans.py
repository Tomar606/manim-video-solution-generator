"""HIS-C6-SA-04: मध्यकालीन भक्ति परंपरा के कोई चार प्रमुख संतों के उपदेशों का वर्णन कीजिए। (2022, 2024): pothi look.

    python lab/kit_test/make_his_c6_04_plans.py  ->  plan_his_c6_sa_04_p1.json

The answer is four saints, each written as परिचय + उपदेश, and the narration says so itself ("हर संत के परिचय
के साथ, उनकी सीख ज़रूर लिखनी है").  So every saint gets the same two moves: who they were (a real period
painting, or Basavanna's statue, with the dates as the narrator says them), then their teaching as the one
thing set large.  The recap names one identity per saint ("कबीर की उलटबाँसी, नानक का नाम स्मरण, मीरा की कृष्ण
भक्ति, और बासवन्ना का लिंगायत"): that wording is the spine, and the four portraits that open the video come
back faded at the recap and light up one by one with it.  The common line (all four against caste and
untouchability) gets its own beat, because the narration flags it ("यही चारों संतों को जोड़ती है").

Generated footage never depicts Guru Nanak or Mirabai as people (Sikh tradition objects to portraying the
Gurus): their clips are a rabab, prayer beads, a palace courtyard with a tanpura, a Krishna shrine.  Their
faces come only from the period paintings.  No map: four regions are carried by the portraits' captions.

Timing: lines_part1.json is on the audio's own pauses (tools/pause_align.py; OpenAI Whisper credits exhausted,
26 Oct 2026).  Cues use W(line, word): the Whisper word clock when words_part1.json exists, else the word's
position in its line, so re-running the word clock re-anchors every cue without touching this file.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROJ = ROOT / "projects/his-c6-sa-04"
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


K = "history/bhakti/"
KABIR, NANAK, GURUS, MIRA, BASAVA = K + "kabir-2.jpg", K + "nanakc-4.jpg", K + "nanakc-2.jpg", K + "mira-3.jpg", K + "basava-2.jpg"
# where each painting's face sits in a 466x250 window
POS = ["center 52%", "center 35%", "center 22%", "center 12%"]
PAGE = "assets/answer/HIS-C6-SA-04-1_page.png"
b = []
B = lambda **k: b.append({x: v for x, v in k.items() if v is not None})

# ---- hook: MP Board over the Ganga at dawn, then four saints from four regions, one message ----
B(id="mp", **{"in": 0, "out": 1}, presenter="full", broll=BR("h1", K + "ghat-2.jpg"), elements=[
    {"type": "statemap", "slot": "upper", "state": "Madhya Pradesh", "text": "MP Board", "sub": "कक्षा 12वीं", "w": 880, "top": 170, "at": [0, 0.05]}])
B(id="four", **{"in": 1, "out": 3}, presenter="standard", broll=BR("h1", K + "ghat-2.jpg", dim=True), elements=[
    {"type": "portraits", "slot": "upper", "top": 150, "img_h": 250, "pos": POS, "items": [
        [KABIR, "कबीर", "काशी", W(1, "अलग")], [NANAK, "गुरु नानक", "पंजाब", W(1, "अलग", 0.35)],
        [MIRA, "मीराबाई", "राजस्थान", W(1, "अलग", 0.7)], [BASAVA, "बासवन्ना", "कर्नाटक", W(1, "अलग", 1.05)]]}])
B(id="ek", **{"in": 3, "out": 4}, presenter="standard", broll=BR("h1", K + "ghat-3.jpg", dim=True), elements=[
    hero("चारों की बात एक", "कोई ऊँचा-नीचा नहीं", 3, hl=["ऊँचा-नीचा"], sub="भगवान के सामने")])
# ---- the years, then the question on the paper ----
B(id="years", **{"in": 4, "out": 6}, presenter="full", broll=BR("e1", dim=True), elements=[
    {"type": "papers", "style": "row", "assets": "assets/papers", "at": 4, "top": 330, "left0": 150, "step": 420, "sheet_w": 380, "dy": 34,
     "title": "यही question, board exam में",
     "years": [["2022", W(4, "2022")], ["2024", W(4, "2024")]],
     "after": "दोनों साल पूछा गया", "t_after": W(5, "दोनों"), "after_dy": 510}])
B(id="question", **{"in": 6, "out": 7}, presenter="full", broll=BR("e1", dim=True), elements=[
    {"type": "qsheet", "at": 6, "src": "qsheet.png", "src_path": "assets/papers/qsheet.png", "w": 840, "top": 64,
     "hl_left": 0.262, "line_h": 0.058,
     "lines": [[0.662, 0.810, W(6, "मध्यकालीन")], [0.739, 0.820, W(6, "के कोई")], [0.810, 0.816, W(6, "उपदेशों")]],
     "marks": "3 अंक", "t_marks": W(6, "वर्णन"), "marks_y": 0.80}])
# ---- the key word, and the shape of every point: परिचय + उपदेश ----
B(id="updesh", **{"in": 7, "out": 8}, presenter="standard", broll=BR("u1", K + "kabir-1.jpg", dim=True), elements=[
    hero("ध्यान देने वाला शब्द", "उपदेश", W(7, "उपदेश"), hl=["उपदेश"], sub="यानी उनकी सीख")])
B(id="format", **{"in": 8, "out": 10}, presenter="standard", broll=BR("u1", K + "kabir-1.jpg", dim=True), elements=[
    head("हर संत के लिए लिखो", 8, "drop"),
    {"type": "compare", "slot": "upper", "left": ["परिचय", "वो कौन थे"], "right": ["उपदेश", "उनकी सीख"],
     "at": W(8, "परिचय"), "right_at": W(9, "सीख")}])
# ---- 1: कबीर ----
B(id="kabir", **{"in": 10, "out": 11}, presenter="standard", broll=BR("k1", K + "loom-1.jpg", dim=True), elements=[
    head("1. कबीर", 10, "drop"),
    {"type": "photo", "slot": "upper", "src": K + "kabir-loom.jpg", "w": 600, "label": "करघे पर कबीर", "at": W(10, "कबीरदास")},
    {"type": "pill", "slot": "under-upper", "text": "14वीं-15वीं शताब्दी", "style": "accent", "at": W(10, "चौदहवीं")}])
B(id="naam", **{"in": 11, "out": 12}, presenter="standard", broll=BR("k1", K + "loom-1.jpg", dim=True), elements=[
    head("1. कबीर", 11),
    {"type": "def", "slot": "upper", "term": "कबीर", "text": "अरबी में अर्थ: महान", "at": W(11, "अरबी")}])
B(id="janm", **{"in": 12, "out": 13}, presenter="standard", broll=BR("k2", K + "kabir-1.jpg", dim=True), elements=[
    head("1. कबीर", 12),
    {"type": "ask", "slot": "upper", "text": "कबीर हिंदू थे या मुसलमान?", "at": W(12, "जन्म"),
     "answer": "इस पर मतभेद है", "t_answer": W(12, "हिंदू")}])
B(id="satya", **{"in": 13, "out": 15}, presenter="standard", broll=BR("k3", K + "ghat-3.jpg", dim=True), elements=[
    hero("कबीर का उपदेश", "परम सत्य एक है", W(13, "परम"), hl=["एक"]),
    {"type": "stamp", "slot": "under-upper", "text": "अल्लाह कहो या राम", "at": W(14, "अल्लाह"), "fx": "zoom"}])
B(id="dikhava", **{"in": 15, "out": 16}, presenter="full", broll=BR("k2", K + "kabir-1.jpg"), elements=[
    {"type": "note", "slot": "over-broll-top", "text": "दोनों धर्मों के बाहरी दिखावे का विरोध", "at": W(15, "दोनों"), "fx": "rise"}])
B(id="ulat", **{"in": 16, "out": 19}, presenter="standard", broll=BR("k4", K + "ghat-1.jpg", dim=True), elements=[
    head("कबीर की उलटबाँसी", W(16, "उलटबाँसी"), "drop"),
    {"type": "compare", "slot": "upper", "left": ["ऊपर से", "अर्थ कुछ और"], "right": ["अंदर", "गहरा सत्य"],
     "at": W(17, "ऊपर"), "right_at": W(18, "अंदर")}])
# ---- 2: गुरु नानक ----
B(id="nanak", **{"in": 19, "out": 21}, presenter="standard", broll=BR("n1", K + "nanak-4.jpg", dim=True), elements=[
    head("2. गुरु नानक", 19, "drop"),
    {"type": "photo", "slot": "upper", "src": NANAK, "w": 700, "label": "गुरु नानक, भाई मरदाना और भाई बाला के साथ", "at": W(19, "नानक")},
    {"type": "pill", "slot": "under-upper", "text": "1469 – 1539", "style": "accent", "at": W(20, "चौदह")}])
B(id="guru", **{"in": 21, "out": 23}, presenter="standard", broll=BR("n1", K + "nanak-4.jpg", dim=True), elements=[
    head("2. गुरु नानक", 21),
    {"type": "photo", "slot": "upper", "src": GURUS, "w": 860, "label": "दस सिख गुरु, बीच में गुरु नानक", "at": 21},
    {"type": "pills", "slot": "under-upper", "items": [["हिंदू व्यापारी परिवार में जन्म", W(21, "हिंदू")], ["सिखों के पहले गुरु", W(22, "पहले")]]}])
B(id="nirakar", **{"in": 23, "out": W(23, "कर्मकांड", -0.3)}, presenter="standard", broll=BR("n2", K + "nanak-4.jpg", dim=True), elements=[
    hero("नानक का उपदेश", "निराकार ईश्वर की भक्ति", W(23, "निराकार"), hl=["निराकार"])])
B(id="smaran", **{"in": W(23, "कर्मकांड", -0.3), "out": 25}, presenter="standard", broll=BR("n2", K + "nanak-4.jpg", dim=True), elements=[
    head("नानक का उपदेश", W(23, "कर्मकांड", -0.3)),
    {"type": "yn", "slot": "upper", "no": "कर्मकांड", "yes": "ईश्वर के नाम का स्मरण", "at": W(23, "कर्मकांड"), "t_yes": W(24, "नाम")}])
# ---- 3: मीराबाई ----
B(id="mira", **{"in": 25, "out": 27}, presenter="standard", broll=BR("m1", K + "mira-2.jpg", dim=True), elements=[
    head("3. मीराबाई", 25, "drop"),
    {"type": "photo", "slot": "upper", "src": MIRA, "w": 480, "label": "मीराबाई", "at": W(25, "मीराबाई")},
    {"type": "pill", "slot": "under-upper", "text": "उत्तर भारत की प्रमुख कृष्ण भक्त", "style": "accent", "at": W(26, "कृष्ण")}])
B(id="samarpan", **{"in": 27, "out": 29}, presenter="standard", broll=BR("m2", K + "mira-2.jpg", dim=True), elements=[
    hero("मीरा का उपदेश", "कृष्ण के प्रति पूरा समर्पण", W(27, "कृष्ण"), hl=["समर्पण"]),
    {"type": "stamp", "slot": "under-upper", "text": "समाज की हर रोक-टोक से ऊपर", "at": W(28, "समाज"), "fx": "zoom"}])
# ---- 4: बासवन्ना ----
B(id="basava", **{"in": 29, "out": 31}, presenter="standard", broll=BR("b1", K + "kudalasangama-1.jpg", dim=True), elements=[
    head("4. बासवन्ना", 29, "drop"),
    {"type": "photo", "slot": "upper", "src": BASAVA, "w": 520, "label": "बासवन्ना की प्रतिमा, गदग (कर्नाटक)", "at": W(29, "बासवन्ना")},
    {"type": "pill", "slot": "under-upper", "text": "1106 – 1168", "style": "accent", "at": W(30, "ग्यारह")}])
B(id="mantri", **{"in": 31, "out": 32}, presenter="full", broll=BR("b2", K + "kudalasangama-1.jpg"), elements=[
    {"type": "note", "slot": "over-broll-top", "text": "कलचुरि राजा के दरबार में मंत्री", "at": W(31, "कलचुरि"), "fx": "rise"}])
B(id="lingayat", **{"in": 32, "out": 34}, presenter="standard", broll=BR("b3", K + "kudalasangama-1.jpg", dim=True), elements=[
    head("बासवन्ना का उपदेश", 32, "drop"),
    {"type": "def", "slot": "upper", "term": "वीरशैव", "text": "यानी लिंगायत परंपरा", "at": W(32, "वीरशैव")},
    {"type": "stamp", "slot": "under-upper", "text": "शिव की पूजा, लिंग के रूप में", "at": W(33, "शिव"), "fx": "zoom"}])
# ---- the line that joins all four ----
B(id="jod", **{"in": 34, "out": 36}, presenter="standard", broll=BR("c1", K + "ghat-2.jpg", dim=True), elements=[
    head("चारों संतों को जोड़ने वाली लाइन", W(35, "जोड़ती"), "drop"),
    {"type": "portraits", "slot": "upper", "top": 250, "img_h": 230, "pos": POS, "at": 34, "items": [
        [KABIR, "कबीर", "", 34], [NANAK, "गुरु नानक", "", [34, 0.15]], [MIRA, "मीराबाई", "", [34, 0.3]], [BASAVA, "बासवन्ना", "", [34, 0.45]]]}])
B(id="virodh", **{"in": 36, "out": 39}, presenter="standard", broll=BR("c1", K + "ghat-2.jpg", dim=True), elements=[
    head("सभी संतों ने कड़ा विरोध किया", 36, "drop"),
    {"type": "notify", "slot": "upper", "items": [["tabler:ban", "जाति-पाति", "", W(37, "जाति")],
                                               ["tabler:ban", "किसी को अछूत या दूषित मानना", "", W(37, "अछूत")],
                                               ["tabler:ban", "ब्राह्मणवादी परंपरा", "", W(38, "ब्राह्मणवादी")]]},
    {"type": "stamp", "slot": "under-upper", "text": "कड़ा विरोध", "at": W(38, "कड़ा"), "fx": "zoom"}])
B(id="teacher", **{"in": 39, "out": 42}, presenter="full", broll=BR("t1", K + "kabir-1.jpg", dim=True), elements=[
    {"type": "note", "slot": "over-broll-top", "text": "जैसे: अच्छा टीचर, हर बच्चा बराबर", "at": W(39, "टीचर"), "fx": "rise"},
    {"type": "stamp", "slot": "under-upper", "text": "ये संत: सब बराबर", "at": W(41, "सबको"), "fx": "zoom"}])
# ---- recap: the four portraits come back faded and light up with their one identity ----
B(id="recap", **{"in": 42, "out": 45}, presenter="standard", broll=BR("r1", K + "ghat-3.jpg", dim=True), elements=[
    head("एक-एक पहचान से याद रखो", 42, "drop"),
    {"type": "portraits", "slot": "upper", "img_h": 196, "pos": POS, "ghost": True, "focus": True, "at": 42, "items": [
        [KABIR, "कबीर", "उलटबाँसी", W(43, "कबीर")], [NANAK, "गुरु नानक", "नाम स्मरण", W(43, "नानक")],
        [MIRA, "मीराबाई", "कृष्ण भक्ति", W(44, "मीरा")], [BASAVA, "बासवन्ना", "लिंगायत", W(44, "बासवन्ना")]]}])
B(id="sure", **{"in": 45, "out": 48}, presenter="standard", broll=BR("r1", K + "ghat-3.jpg", dim=True), elements=[
    hero("पूरा answer दिमाग में बैठा लिया, इतना लिखा तो", "पूरे 3 नंबर पक्के", W(47, "पूरे"), hl=["पक्के"])])
# ---- the exact answer: the page itself once it is here, the notes button until then ----
if (PROJ / PAGE).exists():
    B(id="page", **{"in": 48, "out": "end"}, presenter="full", tracker=False, spine=False, elements=[
        {"type": "page", "src": PAGE, "at": 48, "badge": "Notes button में", "t_badge": W(48, "notes")}])
else:
    B(id="notes", **{"in": 48, "out": 49}, presenter="standard", broll=BR("r1", K + "ghat-3.jpg", dim=True), tracker=False, elements=[
        {"type": "pdfbadge", "slot": "upper", "text": "Exact answer", "sub": "notes button में मिलेगा", "top": 110, "at": W(48, "exact")}])
    B(id="end", **{"in": 49, "out": "end"}, presenter="standard", broll=BR("h1", K + "ghat-2.jpg", dim=True), tracker=False, elements=[
        hero("मज़ेदार reels के साथ", "हर topic पूरा करते जाओ", W(49, "मज़ेदार"), hl=["topic"])])

plan = {"_about": __doc__.strip().splitlines()[0], "project": "his-c6-sa-04", "part": 1, "captions_at": "bottom",
        "skin": "paper-editorial", "theme": "pothi", "presenter_style": "card", "plate": "bk-boats",
        **({} if has("h1") else {"hook": "exempt"}),     # until the opening Veo clip exists, a real photo stands in
        "hilite": ["उपदेश", "कबीर", "उलटबाँसी", "नानक", "स्मरण", "मीराबाई", "कृष्ण", "बासवन्ना", "लिंगायत", "वीरशैव", "जाति-पाति", "अछूत", "बराबर", "पक्के"],
        "card_style": {"backdrop": "bk-card"},
        # the Hindi reference reel's framing (HIN-SM-02), as approved for the Molarity reel
        "framing": {"crop": [600, 150, 1340, 1000], "full_w": 735},
        "scene_match": {"tint": 0.05, "wrap": 0.12, "wrap_px": 6},
        # the Molarity reel's approved grade (true to source, softened, contrast eased: user, 24 Oct 2026)
        "presenter_grade": {"exposure": 1.0, "contrast": 0.94, "warm": 0.99, "saturation": 0.96, "shadow_lift": 0.4, "lift_radius": 14,
                            "define": 0.04, "matte_soft": 1.0, "matte_choke": 0.05, "soften": {"amount": 0.55, "radius": 1.8}},
        "card": {"x": 314, "y": 1130, "w": 452, "h": 560},      # bottom centre: he is always centred horizontally
        "spine": {"title": "भक्ति के चार संत", "items": ["कबीर: उलटबाँसी", "नानक: नाम स्मरण", "मीरा: कृष्ण भक्ति", "बासवन्ना: लिंगायत"],
                  "lit_at": [19, 25, 29, 34], "show_from": 10},
        "beats": b}
(ROOT / "lab/kit_test/plan_his_c6_sa_04_p1.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1))
print(len(b), "beats")
