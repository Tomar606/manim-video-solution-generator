"""GEO-C7-SA-02 (भूमध्य सागर-हिन्द महासागरीय समुद्री मार्ग की तीन विशेषताएँ): orbit look.

    python lab/kit_test/make_geo_c7_plan.py  ->  lab/kit_test/plan_geo_c7_sa_02_p1.json

Cues are written in SECONDS of the narration and turned into [line, offset] here,
so a port lights on the word that names it rather than on its line.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
L = json.loads((ROOT / "projects/geo-c7-sa-02/lines_part1.json").read_text())


def A(sec):
    """seconds -> [line index, offset] (the compile step's cue form)."""
    i = max(k for k, l in enumerate(L) if l["start"] <= sec + 1e-6)
    return [i, round(sec - L[i]["start"], 2)]


# (lon, lat).  The sea lane from Gibraltar east, and the old way round the Cape.
GIB = [-5.8, 35.95]
SUEZ = [GIB, [3, 37.6], [11.5, 37.4], [20, 34.2], [32.3, 31.4],                 # 4 Port Said
        [32.6, 29.8], [34.6, 27.2], [38.4, 20.5], [42.3, 14.6], [43.4, 12.6],
        [45.0, 12.7],                                                             # 10 Aden
        [53, 14.3], [63, 17.5], [72.6, 18.9],                                     # 13 Mumbai
        [72.4, 15], [74.4, 10.5], [76.6, 7.3], [79.6, 6.9],                       # 17 Colombo
        [82.5, 5.6], [91, 6.2], [96.5, 5.9], [99.5, 3.6], [103.8, 1.25]]          # 22 Singapore
CAPE = [GIB, [-10.5, 32], [-18.5, 22], [-19, 13], [-12, 4], [-1, 0.5], [6, -6],
        [11.5, -16], [14, -26], [18.4, -35.6], [24, -36.4], [33, -31.5], [38.5, -24],
        [41.8, -17.5], [44, -11], [50, -2], [59, 8], [72.6, 18.9]]                # ends at Mumbai
SUEZ_TO_MUMBAI = SUEZ[:14]

PORTS = [["पोर्ट सईद", "मिस्र", SUEZ[4], None, "nw"],
         ["अदन", "यमन", SUEZ[10], None, "s"],
         ["मुंबई", "भारत", SUEZ[13], None, "n"],
         ["कोलंबो", "श्रीलंका", SUEZ[17], None, "s"],
         ["सिंगापुर", "", SUEZ[22], None, "n"]]


def ports(times):
    return [p[:3] + [t] + p[4:] for p, t in zip(PORTS, times)]


LANDS = [["यूरोप", [14, 44.5], "pre"], ["अफ्रीका", [20, 4], "pre"], ["अरब", [46, 23.5], "pre"],
         ["भारत", [78.5, 22], "pre"], ["दक्षिण-पूर्व एशिया", [104, 15], "pre"]]
SEAS = [["भूमध्य सागर", [18.5, 37.4], "pre", "sea"], ["अरब सागर", [63, 11], "pre", "sea"],
        ["हिन्द महासागर", [78, -14], "pre", "sea"], ["अटलांटिक महासागर", [-1, -14], "pre", "sea"]]

beats = []
B = lambda **k: beats.append(k)

# ---- hook: the long way, then the canal --------------------------------------------------
B(id="cape-storm", **{"in": 0, "out": 3}, presenter="standard", broll={"clip": "v01", "region": "full"}, elements=[
    {"type": "pills", "slot": "over-broll-low", "items": [["यूरोप → भारत", A(3.0)], ["पूरा अफ्रीका घूमकर", A(6.2)]]}])
B(id="suez-glide", **{"in": 3, "out": 5}, presenter="standard", broll={"clip": "v02", "region": "full"}, elements=[
    {"type": "stamp", "slot": "over-broll", "text": "स्वेज नहर", "at": A(8.2)},
    {"type": "note", "slot": "over-broll-low", "text": "लंबा सफर, एकदम छोटा", "at": A(10.4)}])
B(id="question", **{"in": 5, "out": 8}, presenter="small", broll={"clip": "v03", "region": "full", "dim": True}, elements=[
    {"type": "qcard", "slot": "upper", "question": "भूमध्य सागर-हिन्द महासागरीय समुद्री मार्ग की कोई तीन विशेषताएँ लिखिए।",
     "year": "2025", "marks": "3 अंक", "t_marks": A(21.0), "at": 5}])

# ---- 1: more countries and people --------------------------------------------------------
B(id="f1", **{"in": 8, "out": 10}, presenter="standard", broll={"clip": "v05", "region": "full"}, elements=[
    {"type": "section", "slot": "over-broll-top", "num": "1", "text": "अधिक देश, अधिक लोग", "at": 9}])
B(id="heartland", **{"in": 10, "out": 13}, presenter="standard", broll={"clip": "v04", "region": "full"}, elements=[
    {"type": "pill", "slot": "over-broll-top", "text": "प्राचीन विश्व का हृदय स्थल", "style": "accent", "at": A(30.6)},
    {"type": "pills", "slot": "over-broll-low", "items": [["पुरानी सभ्यताएँ", A(35.2)], ["घनी आबादी", A(37.6)]]}])
B(id="heartland-map", **{"in": 13, "out": 15}, presenter="standard", elements=[
    {"type": "seamap", "slot": "upper", "labels": LANDS + SEAS,
     "routes": [{"pts": SUEZ, "at": 13, "ship": True, "dur": 4.0}]},
    {"type": "pill", "slot": "under-upper", "text": "बाकी मार्गों से ज़्यादा देश, ज़्यादा लोग", "style": "accent", "at": 14}])
B(id="write-word", **{"in": 15, "out": 17}, presenter="standard", elements=[
    {"type": "def", "slot": "head", "term": "हृदय स्थल", "text": "इस बिंदु की पहचान", "at": 15},
    {"type": "stamp", "slot": "upper", "text": "answer में ज़रूर लिखें", "at": A(47.6)}])
B(id="hub-two", **{"in": 17, "out": 20}, presenter="hub", hub={"cy": 1000, "r": 215, "backdrop": "veo:v12@2"}, elements=[
    {"type": "headline", "slot": "head", "text": "तीन विशेषताएँ", "size": "m", "at": 17},
    {"type": "radial", "slot": "around-hub", "radius": 370, "cumulative": True, "items": [
        ["tabler:users-group", "अधिक देश-लोग", 17], ["tabler:anchor", "प्रमुख पत्तन", 17], ["tabler:route", "स्वेज नहर", 17]],
     "recount": [A(52.0), A(60.2)]}])

# ---- 2: ports — a quick cut per port as it is named, then the west-to-east trick --------
B(id="f2", **{"in": 19, "out": A(62.3)}, presenter="standard", broll={"clip": "v08", "region": "full"}, elements=[
    {"type": "section", "slot": "over-broll-top", "num": "2", "text": "प्रमुख पत्तन", "at": A(60.0)}])
# Mumbai and Colombo are named 0.3 s apart: one cut carries both rather than a flash frame
cuts = [("v06", 62.3, 63.6), ("v07", 63.6, 64.9), ("v09", 64.9, 65.75), ("v10", 65.75, 67.3)]
names = [("पोर्ट सईद", 62.42), ("अदन", 63.7), ("मुंबई", 64.96), ("कोलंबो", 65.28), ("सिंगापुर", 65.82)]
for clip, a, b in cuts:
    B(id=f"port-{clip}", **{"in": A(a), "out": A(b) if b < 67.3 else 22}, presenter="standard", broll={"clip": clip, "region": "full"}, elements=[
        {"type": "pills", "slot": "over-broll-low", "style": "accent",
         "items": [[n, A(max(t, a))] for n, t in names if t < b]}])
B(id="trick-map", **{"in": 22, "out": 28}, presenter="standard", elements=[
    {"type": "headline", "slot": "head", "text": "नक्शे पर: पश्चिम → पूरब", "size": "m", "at": 22},
    {"type": "seamap", "slot": "upper", "labels": [l for l in SEAS if l[0] != "भूमध्य सागर"],
     "routes": [{"pts": SUEZ, "at": A(71.3), "ship": True,
                 "stops": [[4, A(74.1)], [10, A(75.1)], [13, A(76.45)], [17, A(78.0)], [22, A(79.7)]]}],
     "ports": ports([A(74.1), A(75.1), A(76.45), A(78.0), A(79.7)])},
    {"type": "pill", "slot": "under-upper", "text": "जहाज़ के रुकने का क्रम = लिखने का क्रम", "style": "accent", "at": A(81.2)}])

# ---- 3: the canal -------------------------------------------------------------------------
B(id="f3", **{"in": 28, "out": 30}, presenter="standard", broll={"clip": "v03", "region": "full"}, elements=[
    {"type": "stamp", "slot": "over-broll", "text": "सबसे ज़रूरी", "at": 28},
    {"type": "section", "slot": "over-broll-top", "num": "3", "text": "स्वेज नहर का महत्व", "at": A(87.6)}])
B(id="cape-vs-suez", **{"in": 30, "out": 35}, presenter="standard", elements=[
    {"type": "headline", "slot": "head", "text": "यूरोप से एशिया: दो रास्ते", "size": "m", "at": 30},
    {"type": "seamap", "slot": "upper", "labels": [l for l in LANDS if l[0] in ("यूरोप", "अफ्रीका")],
     "routes": [{"pts": CAPE, "at": A(91.3), "color": "warn", "ship": True,
                 "stops": [[9, A(94.6)], [17, A(99.0)]], "tag": "उत्तमाशा अंतरीप", "tag_xy": [24, -31], "tag_at": A(93.3),
                 "cross_at": A(102.5), "cross_xy": [5, -10]},
                {"pts": SUEZ_TO_MUMBAI, "at": A(99.86), "ship": True, "dur": 2.4,
                 "tag": "स्वेज नहर", "tag_xy": [44, 32], "tag_at": A(100.3)}],
     "ports": [["मुंबई", "", SUEZ[13], A(91.3), "n"]], "calm": True},
    {"type": "pills", "slot": "under-upper", "style": "accent", "items": [["दूरी कम", A(103.86)], ["समय कम", A(104.78)]]}])
B(id="spelling", **{"in": 35, "out": 37}, presenter="standard", elements=[
    {"type": "headline", "slot": "head", "text": "spelling पर ध्यान", "size": "m", "at": 35},
    {"type": "stamp", "slot": "upper", "text": "उत्तमाशा अंतरीप", "at": A(105.8)},
    {"type": "chain", "slot": "under-upper", "items": [["उत्तम + आशा = उत्तमाशा", A(108.5)], ["Cape of Good Hope", A(110.0)]]}])

# ---- recap, marks, outro -------------------------------------------------------------------
B(id="recap", **{"in": 37, "out": 41}, presenter="hub", hub={"cy": 1000, "r": 215, "backdrop": "veo:v11@2"}, elements=[
    {"type": "headline", "slot": "head", "text": "पूरे मार्ग की सैर", "size": "m", "at": 37},
    {"type": "radial", "slot": "around-hub", "radius": 370, "cumulative": True, "items": [
        ["tabler:users-group", "हृदय स्थल: अधिक देश", 37], ["tabler:anchor", "पोर्ट सईद → सिंगापुर", 37], ["tabler:route", "स्वेज: दूरी-समय कम", 37]],
     "recount": [38, 39, 40]}])
B(id="marks", **{"in": 41, "out": 44}, presenter="standard", broll={"clip": "v12", "region": "full", "dim": True}, elements=[
    {"type": "pill", "slot": "over-broll-top", "text": "तीन विशेषताएँ + पत्तनों के नाम", "style": "accent", "at": 41},
    {"type": "stamp", "slot": "over-broll", "text": "3 नंबर पक्के", "at": A(127.6)}])
B(id="notes", **{"in": 44, "out": 46}, presenter="hero", broll={"clip": "v11", "region": "full", "dim": True}, elements=[
    {"type": "pill", "slot": "head", "text": "पूरा answer: Notes button", "style": "accent", "at": A(131.4)}])
B(id="outro", **{"in": 46, "out": "end"}, presenter="hero", broll={"clip": "v02", "region": "full", "dim": True, "offset": 3}, elements=[
    {"type": "note", "slot": "over-broll-top", "text": "लंबा रास्ता छोटा, लंबी पढ़ाई आसान", "at": 47}])

plan = {"_about": __doc__.strip().splitlines()[0], "project": "geo-c7-sa-02", "part": 1, "captions_from": 8,
        "skin": "paper-editorial", "theme": "orbit", "presenter_style": "card", "plate": "sea-suez-orbit",
        "spine": {"title": "भूमध्य सागर–हिन्द महासागर मार्ग", "items": ["अधिक देश-लोग", "प्रमुख पत्तन", "स्वेज नहर"],
                  "lit_at": [9, 19, 29], "show_from": 8},
        "beats": beats}
out = ROOT / "lab/kit_test/plan_geo_c7_sa_02_p1.json"
out.write_text(json.dumps(plan, ensure_ascii=False, indent=1))
shots = {"v01": "hook: steamship in storm off the Cape", "v02": "ship gliding through Suez Canal", "v03": "Suez Canal from above, convoy",
         "v04": "Nile feluccas, ancient temple (heartland)", "v05": "crowded Arabian Sea harbour", "v06": "Port Said canal entrance",
         "v07": "Aden harbour under volcanic hills", "v08": "Mumbai container port", "v09": "Colombo port", "v10": "Singapore Strait ships",
         "v11": "ship's bow cutting the sea", "v12": "container ship at sunset", "v13": "Arab dhows"}
(ROOT / "projects/geo-c7-sa-02/veo/shots.json").write_text(json.dumps(shots, indent=1))
print(out, len(beats), "beats")
