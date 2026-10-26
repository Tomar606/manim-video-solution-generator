"""CHE: मोलरता (Molarity) क्या है? इसका गणितीय सूत्र और मात्रक लिखिए। (2022, 23 और 2025): chemlab look.

    python lab/kit_test/make_che_molarity_plans.py  ->  plan_che_molarity_p1.json

One picture carries the definition: a 1 L volumetric flask of blue solution whose dissolved particles gather
into mole packets, so "per litre of SOLUTION" and "number of MOLES" are seen, not just heard; Capital M lands
beside it and the definition turns into M = n/V in the callouts' own colours (n copper, V teal).  The x1000 is
derived on screen (n = W_B/M_B from the balance, V(L) = V(mL)/1000 from the cylinder), and 1 dm3 = 1 L is shown
by pouring a 10 cm cube into a 1 L flask.  The question's three asks are the spine (परिभाषा, सूत्र, मात्रक).
The gift promised at 0:27 opens at 1:33.

Cues come straight off the take's Whisper word clock (T()).  This take's words came back romanized
("Kisi villian ke ek litre"), so the Devanagari text cannot be matched against them, and the caption
lines' own starts are off by up to 1.4 s around the years: every element is cued to the exact spoken word.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROJ = ROOT / "projects/che-molarity"
L = json.loads((PROJ / "lines_part1.json").read_text())
WORDS = json.loads((PROJ / "words_part1.json").read_text())


def at(t):
    """An absolute time on the take's clock, as the plan's cue: [caption line, seconds into it]."""
    i = max(k for k, l in enumerate(L) if l["start"] <= t + 1e-6)
    return [i, round(t - L[i]["start"], 2)]


def T(word, after=0.0, plus=0.0):
    """The moment `word` (as Whisper spelled it) is first spoken at or after `after` seconds, plus `plus`."""
    w = next(w for w in WORDS if w["s"] >= after - 0.05 and w["w"].strip(".,?!।").lower() == word.lower())
    return at(w["s"] + plus)


def PH(src, **k):                  # a real photograph as the beat's background
    return {"photo": src, "region": "full", **k}


def has(clip):
    return any((PROJ / d / f"{clip}.mp4").exists() for d in ("diagrams", "veo/clean", "veo/clips"))


def BR(clip, photo=None, **k):
    """The beat's footage: its Veo clip once generated; until then a real photograph, or the plate (None).
    Veo covers almost every beat (user, 24 Oct 2026: "use sufficient veo clips so that the plate shows at
    minimal places"); behind diagram cards the clip is dimmed so the card stays the thing read."""
    if has(clip):
        return {"clip": clip, "region": "full", **k}
    return PH(photo) if photo else None


def hero(kicker, text, at_, hl=None, fx="rise"):
    return {"type": "hero", "slot": "upper", "kicker": kicker, "text": text, "at": at_, "hl": hl or [], "fx": fx}


b = []
B = lambda **k: b.append({x: v for x, v in k.items() if v is not None})
H1 = "chemistry/chemistry-demos/chemistry-demos-1.jpg"        # copper sulphate crystals: the hook's stand-in
# ---- hook ----
B(id="mp", **{"in": 0, "out": T("pichli")}, presenter="full", broll=BR("h1", H1, span=[0.0, 2.6]), elements=[
    {"type": "statemap", "slot": "upper", "state": "Madhya Pradesh", "text": "MP Board", "sub": "कक्षा 12वीं", "w": 880, "top": 170, "at": [0, 0.05]}])
B(id="prev", **{"in": T("pichli"), "out": T("to", 6.5)}, presenter="standard", broll=BR("a1", dim=True, span=[0.0, 4.2]), elements=[
    {"type": "photo", "slot": "upper", "src": "chemistry/molarity/prev-reel.jpg", "w": 430, "label": "पिछली Reel: Physics (व्हीटस्टोन सेतु)", "at": T("physics")}])
B(id="today", **{"in": T("to", 6.5), "out": T("Bachchon", 11)}, presenter="standard", broll=BR("l1", "chemistry/chemistry-demos/chemistry-demos-3.jpg"), elements=[
    {"type": "pill", "slot": "over-broll-low", "text": "आज: Chemistry", "style": "accent", "at": T("chemistry")}])
# ---- the years: the reference reel's row of real exam sheets, over the exam hall ----
B(id="years", **{"in": T("Bachchon", 11), "out": T("Aur", 23)}, presenter="full", broll=BR("e1", dim=True), elements=[
    {"type": "papers", "style": "row", "assets": "assets/papers", "at": T("Bachchon", 11), "top": 330, "left0": 22, "step": 330, "sheet_w": 360, "dy": 34,
     "title": "यही question, board exam में",
     "years": [["2022", T("2022")], ["2023", T("2023")], ["2025", T("2025")]],
     "after": "तीनों साल पूछा गया", "t_after": T("teeno"), "after_dy": 490,
     "next": "2027 में भी आ सकता है!", "t_next": T("2027"), "next_dy": 490}])
# "3 नंबर" once the corrected HeyGen line replaces "2 नंबर"; until then the card carries no number (never contradict the voice)
B(id="marks", **{"in": T("Aur", 23), "out": T("Aur", 26.8)}, presenter="standard", broll=BR("h1", "chemistry/lab-glassware/lab-glassware-7.jpg", span=[4.4, 8.0]), elements=[
    hero("इसे अच्छे से समझ लिया तो", "पूरे नंबर पक्के", T("samajh", 23.5), hl=["पक्के"])])
B(id="gift", **{"in": T("Aur", 26.8), "out": T("To", 34)}, presenter="full", broll=BR("a2", dim=True), elements=[
    {"type": "gift", "slot": "upper", "at": T("special"), "text": "Special Gift", "sub": "Reel के end में", "cta": "Reel पूरी देखना!", "t_cta": T("poora"), "top": 100}])
# ---- the question, on the original paper; its three asks become the spine ----
B(id="question", **{"in": T("To", 34), "out": T("To", 38.5)}, presenter="full", broll=BR("e1", dim=True, span=[3.5, 8.0]), elements=[
    {"type": "qsheet", "at": T("To", 34), "src": "qsheet.png", "src_path": "assets/papers/qsheet.png", "w": 840, "top": 64,
     "hl_left": 0.258, "line_h": 0.056,
     "lines": [[0.666, 0.735, T("molarta", 34.5)], [0.755, 0.775, T("kya", 35)], [0.830, 0.785, T("sootr")]],
     "marks": "3 अंक", "t_marks": T("likhiye"), "marks_y": 0.80}])
# ---- 1 परिभाषा: the real flask first, then inside it (the moles a camera cannot show) ----
B(id="flaskreal", **{"in": T("To", 38.5), "out": T("Kisi")}, presenter="full", broll=BR("f1", "chemistry/lab-glassware/lab-glassware-1.jpg"), elements=[
    {"type": "headline", "slot": "head", "text": "1. मोलरता क्या है?", "size": "m", "at": T("sabse"), "fx": "drop"}])
B(id="define", **{"in": T("Kisi"), "out": T("Ab", 53)}, presenter="standard", broll=BR("a1", dim=True), elements=[
    {"type": "headline", "slot": "head", "text": "1. मोलरता क्या है?", "size": "m", "at": T("Kisi")},
    {"type": "flask", "slot": "upper", "top": 190, "h": 910, "at": T("Kisi"), "t_fill": T("villian", 42.4), "t_mark": T("litre", 43), "t_solute": T("ghule"),
     "t_count": T("molon"), "t_def": T("molarta", 47), "t_M": T("capital", 49), "t_m": T("likhte", 50), "t_eq": T("equals")}])
# ---- 2 सूत्र: grams from the balance, millilitres from the cylinder, then the formula derives itself ----
B(id="formula", **{"in": T("Ab", 53), "out": T("gram")}, presenter="standard", broll=BR("a2", dim=True, span=[0.0, 3.0]), elements=[
    {"type": "headline", "slot": "head", "text": "2. गणितीय सूत्र", "size": "m", "at": T("Ab", 53), "fx": "drop"},
    {"type": "formula", "slot": "upper", "title": "मोलरता का सूत्र", "tex": r"M=\dfrac{\textcolor{#B8692F}{n}}{\textcolor{#0E7C86}{V}}", "at": T("Ab", 53)}])
B(id="gram", **{"in": T("gram"), "out": T("millilitre")}, presenter="full", broll=BR("b1", "chemistry/molarity/balance-2.jpg"), elements=[
    {"type": "formula", "slot": "upper", "top": 140, "compact": True, "title": "विलेय का द्रव्यमान ग्राम में", "tex": r"\textcolor{#B8692F}{n}=\dfrac{W_B}{M_B}", "at": T("gram")}])
B(id="ml", **{"in": T("millilitre"), "out": T("to", 58.7)}, presenter="full", broll=BR("m1", "chemistry/molarity/cylinder-3.jpg"), elements=[
    {"type": "formula", "slot": "upper", "top": 140, "compact": True, "title": "विलयन का आयतन मिलीलीटर में", "tex": r"\textcolor{#0E7C86}{V}(\text{L})=\dfrac{V(\text{mL})}{1000}", "at": T("millilitre")}])
B(id="derive", **{"in": T("to", 58.7), "out": T("Yaha", 64)}, presenter="standard", broll=BR("a2", dim=True, span=[3.0, 8.0]), elements=[
    {"type": "headline", "slot": "head", "text": "2. गणितीय सूत्र", "size": "m", "at": T("to", 58.7)},
    {"type": "rewrite", "slot": "upper", "at": T("to", 58.7), "title": "जब द्रव्यमान ग्राम में, आयतन मिलीलीटर में", "box_last": True,
     "steps": [[r"M=\dfrac{\textcolor{#B8692F}{n}}{\textcolor{#0E7C86}{V}}", T("to", 58.7)],
               [r"M=\dfrac{W_B\,/\,M_B}{V\,/\,1000}", T("formula")],
               [r"\boxed{M=\dfrac{W_B\times\textcolor{#B8692F}{1000}}{M_B\times V}}", T("WB", 60)]],
     "subs": [["chemistry/molarity/balance-2.jpg", r"\textcolor{#B8692F}{n}=\dfrac{W_B}{M_B}", "विलेय का द्रव्यमान ग्राम में", T("to", 58.7)],
              ["chemistry/molarity/cylinder-3.jpg", r"\textcolor{#0E7C86}{V}(\text{L})=\dfrac{V(\text{mL})}{1000}", "विलयन का आयतन मिलीलीटर में", T("to", 58.7)]]}])
B(id="symbols", **{"in": T("Yaha", 64), "out": T("Ab", 70.5)}, presenter="standard", broll=BR("a1", dim=True, span=[2.0, 8.0]), elements=[
    {"type": "headline", "slot": "head", "text": "2. गणितीय सूत्र", "size": "m", "at": T("Yaha", 64)},
    {"type": "formula", "slot": "upper", "title": "मोलरता का सूत्र", "tex": r"M=\dfrac{W_B\times 1000}{M_B\times V}", "at": T("Yaha", 64),
     "legend": [["W_B", "विलेय का द्रव्यमान (g)", T("WB", 64.5)], ["M_B", "विलेय का मोलर द्रव्यमान (g/mol)", T("MB", 66)],
                ["V", "विलयन का आयतन (mL)", T("V", 68)]]}])
# ---- 3 मात्रक ----
B(id="unit", **{"in": T("Ab", 70.5), "out": T("Isse", 75.3)}, presenter="full", broll=BR("a2", dim=True, span=[1.0, 6.0]), elements=[
    {"type": "headline", "slot": "head", "text": "3. मात्रक (Unit)", "size": "m", "at": T("unit", 71), "fx": "drop"},
    {"type": "formula", "slot": "upper", "title": "मोलरता का मात्रक", "tex": r"\text{mol/L}\;=\;\text{mol L}^{-1}", "at": T("mol", 73)}])
if has("c1"):                      # the real pour first, then the comparison on the bench
    B(id="pour", **{"in": T("Isse", 75.3), "out": T("capital", 78)}, presenter="full", broll=BR("c1"), elements=[
        {"type": "pill", "slot": "upper", "text": "10 cm × 10 cm × 10 cm = 1 dm³", "style": "accent", "at": T("DM")}])
    B(id="cube", **{"in": T("capital", 78), "out": T("To", 81.3)}, presenter="standard", broll=BR("a1", dim=True), elements=[
        {"type": "cube", "slot": "upper", "top": 220, "at": T("capital", 78), "t_cube": T("capital", 78), "t_pour": T("capital", 78, plus=0.2),
         "t_eq": T("capital", 78, plus=2.2), "t_units": T("molarity")}])
else:
    B(id="cube", **{"in": T("Isse", 75.3), "out": T("To", 81.3)}, presenter="standard", broll=BR("a1", dim=True), elements=[
        {"type": "cube", "slot": "upper", "top": 220, "at": T("Isse", 75.3), "t_cube": T("DM"), "t_pour": T("cube", 76), "t_eq": T("cube", 76, plus=2.3),
         "t_units": T("molarity")}])
# ---- recap, then the answer, the gift opening, the asks ----
B(id="recap", **{"in": T("To", 81.3), "out": T("to", 84.9)}, presenter="full", broll=BR("a2", dim=True, span=[0.0, 4.0]), elements=[
    {"type": "checklist", "slot": "upper", "lit": [0, 1, 2], "at": T("dimaag")}])
B(id="sure", **{"in": T("to", 84.9), "out": T("Aur", 88)}, presenter="standard", broll=BR("h1", "chemistry/lab-glassware/lab-glassware-7.jpg", span=[5.0, 8.0]), elements=[
    hero("दिमाग में बैठा लिया तो", "पूरे 3 नंबर पक्के", T("poore"), hl=["पक्के"])])
B(id="page", **{"in": T("Aur", 88), "out": T("Bachchon", 92)}, presenter="full", tracker=False, spine=False, elements=[
    {"type": "page", "src": "assets/answer/MOL-1.png", "at": T("Aur", 88)}])
B(id="giftopen", **{"in": T("Bachchon", 92), "out": T("ke", 97.5)}, presenter="full", broll=BR("a2", dim=True, span=[2.0, 8.0]), elements=[
    {"type": "gift", "slot": "upper", "at": T("special", 93.5), "text": "Special Gift", "sub": "शुरुआत में जिसका वादा था", "text_open": "Answer की PDF",
     "sub_open": "यही है आपका Special Gift", "t_open": T("answer", 96), "top": 150}])
B(id="asks", **{"in": T("ke", 97.5), "out": T("Aur", 109)}, presenter="standard", broll=BR("s1", dim=True), tracker=False, elements=[
    {"type": "headline", "slot": "head", "text": "PDF के लिए बस 3 काम", "size": "m", "at": T("3", 98), "fx": "drop"},
    {"type": "notify", "slot": "upper", "items": [["tabler:send", "Reel share करो", "दोस्तों के साथ", T("share")],
                                               ["tabler:user-plus", "मुझे follow करो", "", T("follow", 102)],
                                               ["tabler:message-circle", "comment में PDF लिखो", "PDF सीधे आपके DM पर", T("comment")]]}])
B(id="save", **{"in": T("Aur", 109), "out": "end"}, presenter="full", broll=BR("r1"), elements=[
    {"type": "igsave", "slot": "over-broll-top", "text": "Reel save करो", "sub": "exam से पहले revision", "at": T("Aur", 109, plus=0.3), "t_on": T("save")}])

plan = {"_about": __doc__.strip().splitlines()[0], "project": "che-molarity", "part": 1, "captions_at": "bottom",
        "skin": "paper-editorial", "theme": "chemlab", "presenter_style": "card", "plate": "cl-lab-wall",
        **({} if has("h1") else {"hook": "exempt"}),     # until the opening Veo clip exists, a real photo stands in
        "hilite": ["मोलरता", "Molarity", "विलयन", "विलेय", "मोलों", "लीटर", "Capital", "ग्राम", "मिलीलीटर", "Unit", "Special", "PDF"],
        # the presenter's card: a measuring cylinder (glass walls, mL graduations) on a bright lab wall
        "card_style": {"frame": "glass", "backdrop": "card-chem-light"},
        # the Hindi reference reel's framing (HIN-SM-02): head top ~1110 of 1920, cut at mid-torso, face ~180 px wide
        "framing": {"crop": [600, 150, 1340, 1000], "full_w": 735},
        "scene_match": {"tint": 0.05, "wrap": 0.12, "wrap_px": 6},
        # true to the HeyGen source (user, 24 Oct 2026), softened a little: the key's warmth and saturation cancelled,
        # light brow definition, mid-tone skin smoothed while eyes, brows and beard keep their detail
        # contrast eased a touch (user, 24 Oct 2026: "the contrast of the avatar is a little high"): closer to the source,
        # softer cheek shadows, brows still defined
        "presenter_grade": {"exposure": 1.0, "contrast": 0.94, "warm": 0.99, "saturation": 0.96, "shadow_lift": 0.4, "lift_radius": 14,
                            "define": 0.04, "matte_soft": 1.0, "matte_choke": 0.05, "soften": {"amount": 0.55, "radius": 1.8}},
        "card": {"x": 314, "y": 1130, "w": 452, "h": 560},      # bottom centre: he is always centred horizontally
        "spine": {"title": "मोलरता", "items": ["परिभाषा", "सूत्र", "मात्रक"], "lit_at": [17, 20, 27], "show_from": 16},
        "beats": b}
(ROOT / "lab/kit_test/plan_che_molarity_p1.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1))
print(len(b), "beats")
