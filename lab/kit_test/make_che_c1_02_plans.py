"""CHE-C1-SA-02: निम्न को परिभाषित कीजिए। 1. समपरासरी विलयन, 2. अर्द्धपारगम्य झिल्ली। (2018): osmos look.

    python lab/kit_test/make_che_c1_02_plans.py  ->  plan_che_c1_sa_02_p1.json

The redo of the 19 Oct delivery in the kit style, on the same HeyGen take. Two definitions, so the two are the
map (a pair of cards that returns when the second begins and at the recap). Isotonic solutions are their
formula, typeset with every symbol named as it is spoken: equal osmotic pressure (π₁ = π₂), and so equal molar
concentration (M₁ = M₂, the formula the narration gives). The semipermeable membrane is a picture drawn exactly
(the `membrane` element): small solvent molecules pass through its pores both ways, large solute particles bounce
off it, each labelled on the word. Its name is decoded first (अर्द्ध = आधा, पारगम्य = आर-पार जाने देने वाली),
and its examples are real micrographs: a red blood cell (animal) and onion epidermis (plant).

Look: osmos. Onion epidermis under the microscope as the plate; cell teal and plasmolysis magenta; white cards
under a membrane band of tiny pores; Mukta heads. Veo carries the atmosphere only (a microscope bench, an exam
hall, a saline drip, an onion peel, raisins swelling in water).

Timing: lines_part1.json is on the audio's own pauses (tools/pause_align.py, then lines 1 and 6-9 moved by hand
onto the pauses they belong to: the cue held four short lines). Cues use W(line, word): position in the line.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROJ = ROOT / "projects/che-c1-sa-02"
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


O = "chemistry/osmosis/"
ONION, ONION3, PLASMO, RBC = O + "onion-1.jpg", O + "onion-3.jpg", O + "plasmolysis-2.jpg", O + "rbc-3.jpg"
PAGE = "assets/answer/CHE-C1-SA-02-1_page.png"
TWO = dict(type="compare", slot="upper", left=["परिभाषा 1", "समपरासरी<br>विलयन"], right=["परिभाषा 2", "अर्द्धपारगम्य<br>झिल्ली"], vs="", val_size=66)
b = []
B = lambda **k: b.append({x: v for x, v in k.items() if v is not None})

# ---- hook: MP Board over a microscope bench ----
B(id="mp", **{"in": 0, "out": 1}, presenter="full", broll=BR("h1", ONION), elements=[
    {"type": "boardtag", "slot": "upper", "text": "MP Board", "sub": "कक्षा 12", "at": [0, 0.05]}])
# ---- the year on the real exam sheet, then the question ----
B(id="years", **{"in": 1, "out": 2}, presenter="full", broll=BR("e1", dim=True), elements=[
    {"type": "papers", "style": "row", "assets": "assets/papers", "at": 1, "top": 330, "left0": 350, "step": 420, "sheet_w": 380, "dy": 34,
     "title": "यही question, board exam में", "years": [["2018", W(1, "2018")]]}])
B(id="question", **{"in": 2, "out": 3}, presenter="full", broll=BR("e1", dim=True), elements=[
    {"type": "qsheet", "at": 2, "src": "qsheet.png", "src_path": "assets/papers/qsheet.png", "w": 840, "top": 64,
     "hl_left": 0.262, "line_h": 0.062,
     "lines": [[0.660, 0.815, W(2, "बार")], [0.736, 0.72, W(2, "board")], [0.810, 0.675, W(2, "सकता")]],
     "marks": "3 अंक", "t_marks": W(2, "सकता", 0.6), "marks_y": 0.80}])
# ---- the two definitions: the map ----
B(id="two", **{"in": 3, "out": 5}, presenter="standard", broll=BR("d1", ONION3, dim=True), elements=[
    {**TWO, "at": W(3, "दोनों"), "t_right": W(3, "दोनों", 0.5)}])
# ---- 1: isotonic solutions ----
B(id="iso", **{"in": 5, "out": 7}, presenter="standard", broll=BR("i1", ONION, dim=True), elements=[
    hero("परिभाषा 1", "समपरासरी विलयन", W(5, "समपरासरी"), hl=["समपरासरी"], sub="Isotonic solutions")])
B(id="iso_pi", **{"in": 7, "out": 9}, presenter="standard", broll=BR("i1", ONION, dim=True), elements=[
    head("1. समपरासरी विलयन", 7, "drop"),
    {"type": "formula", "slot": "upper", "title": "परासरण दाब समान", "tex": "\\pi_1 = \\pi_2", "at": W(7, "परासरण"), "t_glow": W(8, "समपरासरी"),
     "legend": [["\\pi_1", "पहले विलयन का परासरण दाब", W(7, "परासरण", 0.3)], ["\\pi_2", "दूसरे विलयन का परासरण दाब", W(7, "समान")]]}])
B(id="iso_m", **{"in": 9, "out": 11}, presenter="standard", broll=BR("d1", ONION, dim=True), elements=[
    head("1. समपरासरी विलयन", 9),
    {"type": "formula", "slot": "upper", "title": "मोलर सान्द्रता भी समान", "tex": "M_1 = M_2", "at": W(9, "मोलर"), "t_glow": W(10, "formula"),
     "legend": [["M_1", "पहले विलयन की मोलर सान्द्रता", W(9, "मोलर", 0.3)], ["M_2", "दूसरे विलयन की मोलर सान्द्रता", W(9, "क्रमशः")]]}])
# ---- 2: the semipermeable membrane ----
B(id="two2", **{"in": 11, "out": 12}, presenter="standard", broll=BR("d1", ONION3, dim=True), elements=[
    {**TWO, "at": 11, "t_right": W(11, "अर्द्धपारगम्य")}])
B(id="mem_name", **{"in": 12, "out": 14}, presenter="standard", broll=BR("o1", ONION3, dim=True), elements=[
    head("2. अर्द्धपारगम्य झिल्ली", 12, "drop"),
    {"type": "pills", "slot": "upper", "items": [["अर्द्ध = आधा", W(12, "याद")], ["पारगम्य = आर-पार जाने देने वाली", W(13, "आर")]]}])
B(id="mem", **{"in": 14, "out": 18}, presenter="standard", broll=BR("k1", ONION, dim=True), elements=[
    head("2. अर्द्धपारगम्य झिल्ली", 14),
    {"type": "membrane", "slot": "upper", "at": W(14, "अर्द्धपारगम्य"), "t_solvent": W(15, "विलायक"), "t_solute": W(16, "विलेय")}])
B(id="examples", **{"in": 18, "out": 19}, presenter="standard", broll=BR("k1", ONION, dim=True), elements=[
    head("उदाहरण", 18, "drop"),
    {"type": "portraits", "slot": "upper", "top": 230, "img_h": 330, "items": [
        [RBC, "जंतु झिल्ली", "जैसे: लाल रक्त कोशिका", W(18, "जंतु")], [ONION3, "पादप झिल्ली", "जैसे: प्याज़ की कोशिका", W(18, "पादप")]]}])
# ---- recap: both definitions in one line each ----
B(id="recap", **{"in": 19, "out": 21}, presenter="standard", broll=BR("r1", ONION3, dim=True), elements=[
    {"type": "compare", "slot": "upper", "left": ["समपरासरी विलयन", "परासरण दाब<br>समान"], "right": ["अर्द्धपारगम्य झिल्ली", "केवल विलायक<br>आर-पार"],
     "vs": "", "val_size": 58, "at": 19, "t_right": W(19, "परिभाषाओं")}])
# ---- the exact answer: the page at "answer ... Notes", to the end ----
if (PROJ / PAGE).exists():
    B(id="page", **{"in": 21, "out": "end"}, presenter="full", tracker=False, spine=False, elements=[
        {"type": "page", "src": PAGE, "at": 21, "badge": "Notes बटन में", "t_badge": W(21, "Notes")}])
else:
    B(id="notes", **{"in": 21, "out": "end"}, presenter="standard", broll=BR("r1", ONION3, dim=True), tracker=False, elements=[
        {"type": "pdfbadge", "slot": "upper", "text": "Exact answer", "sub": "Notes बटन में मिलेगा", "top": 110, "at": W(21, "Notes")}])

plan = {"_about": __doc__.strip().splitlines()[0], "project": "che-c1-sa-02", "part": 1, "captions_at": "bottom",
        "skin": "paper-editorial", "theme": "osmos", "presenter_style": "card", "plate": "os-onion",
        **({} if has("h1") else {"hook": "exempt"}),     # until the opening Veo clip exists, a real photo stands in
        "hilite": ["समपरासरी", "परासरण दाब", "मोलर सान्द्रताएँ", "M₁ = M₂", "अर्द्धपारगम्य", "विलायक", "विलेय", "आयन", "जंतु", "पादप"],
        "card_style": {"backdrop": "os-card"},
        # the Hindi reference reel's framing (HIN-SM-02), as approved for the Molarity reel
        "framing": {"crop": [600, 150, 1340, 1000], "full_w": 735},
        "scene_match": {"tint": 0.05, "wrap": 0.12, "wrap_px": 6},
        # the Molarity reel's approved grade (true to source, softened, contrast eased: user, 24 Oct 2026)
        "presenter_grade": {"exposure": 1.0, "contrast": 0.94, "warm": 0.99, "saturation": 0.96, "shadow_lift": 0.4, "lift_radius": 14,
                            "define": 0.04, "matte_soft": 1.0, "matte_choke": 0.05, "soften": {"amount": 0.55, "radius": 1.8}},
        "card": {"x": 314, "y": 1130, "w": 452, "h": 560},      # bottom centre: he is always centred horizontally
        "spine": {"title": "दो परिभाषाएँ", "items": ["समपरासरी विलयन", "अर्द्धपारगम्य झिल्ली"], "lit_at": [5, 11], "show_from": 5},
        "beats": b}
(ROOT / "lab/kit_test/plan_che_c1_sa_02_p1.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1))
print(len(b), "beats")
