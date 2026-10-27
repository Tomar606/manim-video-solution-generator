"""CHE-C1-SA-01: स्थिरक्वाथी मिश्रण (Azeotropes) किसे कहते हैं? ये कितने प्रकार के होते हैं? (2018): still look.

    python lab/kit_test/make_che_c1_01_plans.py  ->  plan_che_c1_sa_01_p1.json

The redo of the 19 Oct delivery in the kit style, on the same HeyGen take. The definition is a picture, drawn
exactly (the `azeo` element): a round-bottom flask on a hot plate boils, the thermometer climbs once and then
HOLDS, and the vapour leaving by the side arm carries exactly the liquid's composition, shown as two identical
bars. The same picture, with the real numbers (95.6% alcohol, 4.4% water, 78.13 °C), is the example, and it is
where "cannot be separated by fractional distillation" is stamped, because the reason is on screen: the vapour
is the liquid. The two types each get their cause chain as a staircase (deviation from Raoult's law, then
vapour pressure, then boiling point) and their boiling-point diagram (`bpgraph`: the curves dip to a minimum for
positive deviation, peak at a maximum for negative), with the examples beside it.

Look: still. A laboratory distillation rig as the plate; ethanol amber and vapour steel-blue; cool white cards
under a steel band riveted in amber; Khand heads. Veo carries the atmosphere only (a distillery at sunrise, an
exam hall, a boiling flask, a student at the bench); every diagram is drawn.

Timing: lines_part1.json is on the audio's own pauses (tools/pause_align.py; Whisper credits exhausted), every
join checked against the pause list. Cues use W(line, word): position in the line.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROJ = ROOT / "projects/che-c1-sa-01"
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


A = "chemistry/azeotropes/"
RIG, COLUMN = A + "distillation-3.jpg", A + "column-3.jpg"   # distillation-2 carries lab signage: not used
PAGE = "assets/answer/CHE-C1-SA-01-1_page.png"
TYPES = dict(type="compare", slot="upper", left=["प्रकार 1", "न्यूनतम<br>क्वथनांकी"], right=["प्रकार 2", "अधिकतम<br>क्वथनांकी"], vs="", val_size=72)
b = []
B = lambda **k: b.append({x: v for x, v in k.items() if v is not None})

# ---- hook: MP Board over a distillery at sunrise ----
B(id="mp", **{"in": 0, "out": 1}, presenter="full", broll=BR("h1", COLUMN), elements=[
    {"type": "boardtag", "slot": "upper", "text": "MP Board", "sub": "कक्षा 12", "at": [0, 0.05]}])
# ---- the year on the real exam sheet, then the question ----
B(id="years", **{"in": 1, "out": 2}, presenter="full", broll=BR("e1", dim=True), elements=[
    {"type": "papers", "style": "row", "assets": "assets/papers", "at": 1, "top": 330, "left0": 350, "step": 420, "sheet_w": 380, "dy": 34,
     "title": "यही question, board exam में", "years": [["2018", W(1, "2018")]]}])
B(id="question", **{"in": 2, "out": 4}, presenter="full", broll=BR("e1", dim=True), elements=[
    {"type": "qsheet", "at": 2, "src": "qsheet.png", "src_path": "assets/papers/qsheet.png", "w": 840, "top": 64,
     "hl_left": 0.262, "line_h": 0.062,
     "lines": [[0.660, 0.625, W(2, "बार")], [0.736, 0.835, W(3, "definition")], [0.810, 0.815, W(3, "समझते")]],
     "marks": "3 अंक", "t_marks": W(2, "सकता"), "marks_y": 0.80}])
# ---- the definition: the term, then the picture ----
B(id="term", **{"in": 4, "out": 5}, presenter="standard", broll=BR("d1", RIG, dim=True), elements=[
    hero("परिभाषा", "स्थिरक्वाथी मिश्रण", W(4, "स्थिरक्वाथी"), hl=["स्थिरक्वाथी"], sub="Azeotrope")])
B(id="define", **{"in": 5, "out": 8}, presenter="standard", elements=[
    head("स्थिरक्वाथी मिश्रण", 5, "drop"),
    {"type": "azeo", "slot": "upper", "top": 274, "h": 860, "scale": 0.94, "at": 5, "a_label": "घटक A", "b_label": "घटक B", "t_liq": W(5, "संघटन"), "t_boil": W(6, "एक"), "t_vap": W(6, "उबलते", 0.6),
     "temp": "स्थिर क्वथनांक", "t_temp": W(7, "स्थिर"), "same": "संघटन वही", "t_same": W(7, "स्थिरक्वाथी")}])
# ---- a quiet moment before the example ----
B(id="quiet", **{"in": 8, "out": 10}, presenter="full", broll=BR("q1", RIG), elements=[])
# ---- the example, with its real numbers; and why distillation cannot separate it ----
B(id="example", **{"in": 10, "out": 17}, presenter="standard", elements=[
    head("उदाहरण: एल्कोहॉल + जल", 10, "drop"),
    {"type": "azeo", "slot": "upper", "top": 274, "h": 860, "scale": 0.94, "at": 10, "split": 0.956, "a_label": "एल्कोहॉल 95.6%", "b_label": "जल 4.4%",
     "t_liq": W(10, "95.6"), "t_b": W(11, "4.4"), "t_boil": W(13, "जो"), "temp": "78.13 °C", "temp_sub": "पर उबलता है", "t_temp": W(13, "78.13"),
     "t_vap": W(13, "उबलता"), "same": "संघटन वही", "t_same": W(13, "उबलता", 0.9), "t_focus": W(15, "अवयवों"), "t_cross": W(16, "पृथक्")}])
# ---- how many types: two ----
B(id="kinds", **{"in": 17, "out": 19}, presenter="standard", broll=BR("t1", RIG, dim=True), elements=[
    {"type": "ask", "slot": "upper", "text": "स्थिरक्वाथी मिश्रण: कितने प्रकार?", "at": W(17, "स्थिरक्वाथी")}])
B(id="types", **{"in": 19, "out": 21}, presenter="standard", broll=BR("t1", RIG, dim=True), elements=[
    {**TYPES, "at": W(19, "दो"), "t_right": W(19, "प्रकार")}])
# ---- 1: minimum boiling ----
B(id="min_name", **{"in": 21, "out": 23}, presenter="standard", broll=BR("m1", RIG, dim=True), elements=[
    head("1. न्यूनतम क्वथनांकी", 21, "drop"),
    {"type": "pills", "slot": "upper", "items": [["न्यूनतम = सबसे कम", W(21, "न्यूनतम")], ["क्वथनांक = boiling point", W(22, "क्वथनांक")]]}])
B(id="min_why", **{"in": 23, "out": 27}, presenter="standard", broll=BR("m2", RIG, dim=True), elements=[
    head("1. न्यूनतम क्वथनांकी", 23),
    {"type": "ladder", "slot": "upper", "focus": True, "items": [
        ["tabler:trending-up", "धनात्मक विचलन", "राउल्ट के नियम से", W(24, "धनात्मक")],
        ["tabler:arrow-big-up-lines", "वाष्पदाब उच्च", "अणु आसानी से वाष्प बनते हैं", W(25, "वाष्पदाब")],
        ["tabler:temperature-minus", "क्वथनांक कम", "कम ताप पर ही उबल जाता है", W(26, "क्वथनांक")]]}])
B(id="min_graph", **{"in": 27, "out": 30}, presenter="standard", broll=BR("m2", RIG, dim=True), elements=[
    {"type": "bpgraph", "slot": "upper", "top": 150, "kind": "min", "title": "न्यूनतम क्वथनांकी स्थिरक्वाथी", "t_curve": 27,
     "t_point": W(27, "स्थिरक्वाथी"), "point_label": "न्यूनतम क्वथनांक"},
    {"type": "pills", "slot": "under-upper", "items": [["एसीटोन + CS₂", W(28, "एसीटोन")], ["C₂H₅OH + n-हेक्सेन", W(29, "C₂H₅OH")]]}])
# ---- 2: maximum boiling ----
B(id="type2", **{"in": 30, "out": 31}, presenter="standard", broll=BR("t1", RIG, dim=True), elements=[
    {**TYPES, "at": 30, "t_right": W(30, "दूसरा")}])
B(id="max_name", **{"in": 31, "out": 33}, presenter="standard", broll=BR("x1", RIG, dim=True), elements=[
    head("2. अधिकतम क्वथनांकी", 31, "drop"),
    {"type": "pills", "slot": "upper", "items": [["अधिकतम = सबसे ज़्यादा", W(31, "अधिकतम")], ["क्वथनांक = boiling point", W(31, "क्वथनांकी")]]}])
B(id="max_why", **{"in": 33, "out": 35}, presenter="standard", broll=BR("x2", RIG, dim=True), elements=[
    head("2. अधिकतम क्वथनांकी", 33),
    {"type": "ladder", "slot": "upper", "focus": True, "items": [
        ["tabler:trending-down", "ऋणात्मक विचलन", "राउल्ट के नियम से", W(33, "ऋणात्मक")],
        ["tabler:arrow-big-down-lines", "वाष्पदाब कम", "अणु मुश्किल से वाष्प बनते हैं", W(34, "वाष्पदाब")],
        ["tabler:temperature-plus", "क्वथनांक उच्च", "ज़्यादा ताप पर उबलता है", W(34, "क्वथनांक")]]}])
B(id="max_graph", **{"in": 35, "out": 37}, presenter="standard", broll=BR("x2", RIG, dim=True), elements=[
    {"type": "bpgraph", "slot": "upper", "top": 150, "kind": "max", "title": "अधिकतम क्वथनांकी स्थिरक्वाथी", "t_curve": 35,
     "t_point": W(35, "उदाहरण"), "point_label": "अधिकतम क्वथनांक"},
    {"type": "pills", "slot": "under-upper", "items": [["एसीटोन + क्लोरोफॉर्म", W(35, "एसीटोन")], ["ईथर + क्लोरोफॉर्म", W(36, "ईथर")]]}])
# ---- recap: both types, by their cause ----
B(id="recap", **{"in": 37, "out": 38}, presenter="standard", broll=BR("r1", COLUMN, dim=True), elements=[
    {"type": "compare", "slot": "upper", "left": ["धनात्मक विचलन", "न्यूनतम<br>क्वथनांकी"], "right": ["ऋणात्मक विचलन", "अधिकतम<br>क्वथनांकी"],
     "vs": "", "val_size": 72, "at": 37, "t_right": W(37, "समझ")}])
# ---- the exact answer: the page at "answer ... Notes button", to the end ----
if (PROJ / PAGE).exists():
    B(id="page", **{"in": 38, "out": "end"}, presenter="full", tracker=False, spine=False, elements=[
        {"type": "page", "src": PAGE, "at": 38, "badge": "Notes बटन में", "t_badge": W(39, "Notes")}])
else:
    B(id="notes", **{"in": 38, "out": "end"}, presenter="standard", broll=BR("r1", COLUMN, dim=True), tracker=False, elements=[
        {"type": "pdfbadge", "slot": "upper", "text": "Exact answer", "sub": "Notes बटन में मिलेगा", "top": 110, "at": W(39, "Notes")}])

plan = {"_about": __doc__.strip().splitlines()[0], "project": "che-c1-sa-01", "part": 1, "captions_at": "bottom",
        "skin": "paper-editorial", "theme": "still", "presenter_style": "card", "plate": "st-rig",
        **({} if has("h1") else {"hook": "exempt"}),     # until the opening Veo clip exists, a real photo stands in
        "hilite": ["स्थिरक्वाथी", "संघटन", "स्थिर क्वथनांक", "95.6%", "4.4%", "78.13°C", "प्रभाजी आसवन", "पृथक्", "दो प्रकार",
                   "न्यूनतम क्वथनांकी", "धनात्मक विचलन", "अधिकतम क्वथनांकी", "ऋणात्मक विचलन"],
        "card_style": {"backdrop": "st-card"},
        # the Hindi reference reel's framing (HIN-SM-02), as approved for the Molarity reel
        "framing": {"crop": [600, 150, 1340, 1000], "full_w": 735},
        "scene_match": {"tint": 0.05, "wrap": 0.12, "wrap_px": 6},
        # the Molarity reel's approved grade (true to source, softened, contrast eased: user, 24 Oct 2026)
        "presenter_grade": {"exposure": 1.0, "contrast": 0.94, "warm": 0.99, "saturation": 0.96, "shadow_lift": 0.4, "lift_radius": 14,
                            "define": 0.04, "matte_soft": 1.0, "matte_choke": 0.05, "soften": {"amount": 0.55, "radius": 1.8}},
        "card": {"x": 314, "y": 1130, "w": 452, "h": 560},      # bottom centre: he is always centred horizontally
        "spine": {"title": "स्थिरक्वाथी मिश्रण", "items": ["परिभाषा", "उदाहरण", "न्यूनतम क्वथनांकी", "अधिकतम क्वथनांकी"],
                  "lit_at": [4, 10, 20, 31], "show_from": 4},
        "beats": b}
(ROOT / "lab/kit_test/plan_che_c1_sa_01_p1.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1))
print(len(b), "beats")
