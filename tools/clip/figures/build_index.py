#!/usr/bin/env python3
"""Rebuild the figure library (tools/clip/figures/) from the shipped clip videos.

    python3 tools/clip/figures/build_index.py            # refresh copies + index.json
    python3 tools/clip/figures/build_index.py --check    # exit 1 if the library is stale
    python3 tools/clip/figures/build_index.py --skip <slug> [--skip <slug> ...]

Why it exists: every clip video draws its diagrams as hand-written SVGs, and a
drawing agent spends minutes on each one even when the same figure (an energy
profile, a graph on axes, a cell, a Punnett square) already shipped in an
earlier video. This script copies every shipped diagram that still passes
tools/clip/svg_lint.py into <subject>/<slug>--<name>.svg and writes index.json,
so an agent can search by subject or topic keyword and start from a figure whose
geometry, strokes and ids are already proven. Run it after each video ships;
never edit the library by hand, because the next run overwrites it.

What counts as shipped: every work/<slug>/ with assets/svg/*.svg or assets/*.svg,
except folders starting with "_" (the template), folders passed with --skip, and
folders that tools/build_clip.py is still building (a state.json whose "deliver"
step is not done). work/ is only ever read.

Where each figure's facts come from, in order of trust:
  beat      spec/parts/design_part<N>.json, then spec/design.json, then
            spec/segments_part<N>.json / spec/segments.json — the first beat
            whose diagram.asset names the SVG.
  shows     that beat's `_why`; else the SVG's own leading comment; else the
            route file's `mark`; else the narration spoken over it; else a line
            built from the SVG's ids and element counts.
  keywords  a fixed lexicon (LEXICON below) matched against the name, ids, beat
            text and labels, plus the figure's name and its short Hindi labels.
            No model call: the same inputs always give the same keywords.

Byte-identical SVGs (the quathanank parts share their assets folder) are kept
once; the other copies are listed in `also_in`. A figure no beat draws is kept
with "used": false — it was in a video's assets but never checked on screen.

Stdlib only. Deterministic: a second run with unchanged inputs writes nothing.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
WORK = ROOT / "work"
INDEX = HERE / "index.json"

sys.dont_write_bytecode = True     # importing svg_lint must not leave a __pycache__ in tools/clip/
sys.path.insert(0, str(HERE.parent))
from svg_lint import lint  # noqa: E402  (tools/clip/svg_lint.py, stdlib only)

SUBJECTS = {"che": "chemistry", "phy": "physics", "bio": "biology",
            "mat": "maths", "math": "maths", "quathanank": "chemistry"}

# Beat sources, most trusted first. Within a tier, files sort by part number.
TIERS = ("parts/design_part*.json", "design.json", "segments_part*.json", "segments.json")

SHOWS_MAX = 300
KEYWORDS_MAX = 20

# Sentences in an SVG's leading comment that describe the drawing rules rather
# than the figure. Dropped before the comment is used as a description.
BOILERPLATE = re.compile(r"no text|<text|no word|text elem|from the spec|segment spec|"
                         r"style=|engine|data-optional|RULES:", re.I)

# Topic lexicon: (english, hindi, triggers). A trigger matches as a whole word
# (Latin or Devanagari) in the figure's text; a trailing * makes it a prefix.
# A leading @ restricts it to the figure's STRUCTURE (its name, ids and beat
# types) — for id fragments like "pb 1" and for words such as "recap" that a
# beat's prose also uses about the design process rather than the figure.
# Add rows here when a new topic ships — the index picks them up on the next run.
LEXICON: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    # chemistry: kinetics
    ("activation energy", "सक्रियण ऊर्जा", ("activation energy", "सक्रियण", "@ea arrow", "@ea gap", "@ea u", "@ea c")),
    ("threshold energy", "देहली ऊर्जा", ("threshold", "देहली", "@thresh")),
    ("energy profile", "ऊर्जा आरेख", ("energy profile", "hump", "barrier", "अवरोध", "progress of the reaction",
                                      "अभिक्रिया की प्रगति", "@hill")),
    ("catalyst", "उत्प्रेरक", ("catalys*", "उत्प्रेरक")),
    ("rate of reaction", "अभिक्रिया का वेग", ("rate of reaction", "reaction rate", "अभिक्रिया का वेग",
                                              "अभिक्रिया की दर", "rate dial", "stopwatch", "unit of time")),
    ("rate law", "वेग नियम", ("rate law", "@ratelaw", "rate equation", "वेग नियम", "दर नियम")),
    ("rate constant", "वेग स्थिरांक", ("rate constant", "वेग स्थिरांक", "वेग नियतांक", "दर स्थिरांक", "@k ring", "@k box")),
    ("concentration vs time", "सांद्रता-समय ग्राफ", ("concentration against time", "concentration-time")),
    ("concentration", "सांद्रता", ("concentration*", "सांद्रता", "सान्द्रता")),
    ("equilibrium", "साम्यावस्था", ("equilibrium", "साम्यावस्था", "साम्य", "@eqm")),
    ("equilibrium constant", "साम्य स्थिरांक", ("equilibrium constant", "साम्य स्थिरांक")),
    ("forward and backward reaction", "अग्र एवं पश्च अभिक्रिया", ("forward", "backward", "अग्र", "पश्च",
                                                                    "@arrow f", "@arrow b")),
    ("reactants and products", "अभिकारक और उत्पाद", ("reactant*", "product", "products", "अभिकारक", "उत्पाद")),
    ("arrhenius equation", "आरेनियस समीकरण", ("arrhenius", "आरेनियस")),
    # chemistry: solutions
    ("boiling point elevation", "क्वथनांक में उन्नयन", ("boiling point", "elevation", "क्वथनांक", "उन्नयन", "@bp")),
    ("vapour pressure", "वाष्पदाब", ("vapour pressure", "vapor pressure", "वाष्पदाब", "@vp")),
    ("atmospheric pressure", "वायुमण्डलीय दाब", ("atmospheric", "atmosphere", "वायुमण्डलीय", "@patm")),
    ("solution and solvent", "विलयन और विलायक", ("solvent", "solute", "विलायक", "विलेय", "विलयन")),
    ("thermometer", "तापमापी", ("thermometer*", "तापमापी", "@thermo", "@merc")),
    # chemistry: electrochemistry, d-block
    ("galvanic cell", "गैल्वेनी सेल", ("galvanic", "salt bridge", "लवण सेतु", "गैल्वेनी")),
    ("electrolytic cell", "विद्युत अपघटनी सेल", ("electrolytic", "विद्युत अपघटनी")),
    ("electrode", "इलेक्ट्रोड", ("electrode*", "anode", "cathode", "एनोड", "कैथोड", "इलेक्ट्रोड")),
    ("electron flow", "इलेक्ट्रॉन प्रवाह", ("electrons flow", "electron flow", "@e flow")),
    ("redox", "अपचयोपचय", ("redox", "reduction", "oxidises", "अपचयन", "अपचयोपचय", "@ox arrow", "@red arrow")),
    ("oxidation state", "ऑक्सीकरण अवस्था", ("oxidation state*", "ऑक्सीकरण अवस्था", "@ox 2", "@ox 7")),
    ("gibbs energy", "गिब्स ऊर्जा", ("gibbs", "गिब्स")),
    ("electrical conductivity", "विद्युत चालकता", ("conductivity", "conductor", "चालकता")),
    ("metallic bonding", "धात्विक बंध", ("metallic bond*", "delocalised", "धात्विक", "@metal lattice", "@e sea")),
    ("d-block elements", "d-ब्लॉक तत्व", ("d block", "d-block", "transition element*", "संक्रमण", "@dblock", "@d cells")),
    ("periodic table", "आवर्त सारणी", ("periodic", "आवर्त", "@pt grid")),
    ("orbital energy levels", "कक्षक ऊर्जा स्तर", ("energy levels", "energy level", "orbital*", "कक्षक",
                                                   "@ns level", "@nd level")),
    # physics: electrostatics
    ("electric flux", "विद्युत फ्लक्स", ("flux", "फ्लक्स")),
    ("electric field lines", "विद्युत क्षेत्र रेखाएँ", ("field lines", "field line", "क्षेत्र रेखा*", "विद्युत क्षेत्र",
                                                      "@field in", "@field out", "@field heads", "@field lines")),
    ("area vector normal", "क्षेत्रफल सदिश अभिलम्ब", ("normally", "अभिलम्ब", "area vector", "surface element",
                                                    "@normal head")),
    ("angle theta", "कोण θ", ("angle", "theta", "θ", "कोण", "right angle", "@theta arc")),
    ("closed surface", "बंद पृष्ठ", ("closed surface", "बंद पृष्ठ", "@surf pos", "@surf neg")),
    ("gauss's law", "गाउस का नियम", ("gauss*", "गाउस")),
    # biology: ecology
    ("ecological pyramid", "पारिस्थितिक पिरामिड", ("pyramid*", "पिरामिड")),
    ("inverted pyramid", "उल्टा पिरामिड", ("inverted", "उल्टा", "उल्टे", "@invnumber", "@invbiomass")),
    ("trophic levels", "पोषी स्तर", ("trophic", "पोषी", "पोषक स्तर", "producer*", "consumer*",
                                     "उत्पादक", "उपभोक्ता", "शाकाहारी", "मांसाहारी", "@tier*")),
    ("pyramid of numbers", "संख्या का पिरामिड", ("pyramid of numbers", "संख्या के", "संख्या का",
                                                 "@invnumber", "@uprightnum")),
    ("pyramid of biomass", "जैवभार का पिरामिड", ("biomass", "जैवभार", "जैव,भार", "@invbiomass")),
    # biology: reproduction
    ("oogenesis", "अण्डजनन", ("oogenesis", "अण्डजनन", "अंडजनन", "अण्ड-जनन", "oogonia", "ऊगोनिया", "oocyte*", "अण्डक")),
    ("ovary", "अण्डाशय", ("ovary", "ovaries", "अण्डाशय", "अंडाशय")),
    ("follicle", "पुटक", ("follicle*", "पुटक")),
    ("ovulation", "अण्डोत्सर्ग", ("ovulation", "अण्डोत्सर्ग")),
    ("meiosis", "अर्द्धसूत्री विभाजन", ("meiosis*", "अर्द्धसूत्री", "अर्धसूत्री", "prophase*")),
    ("mitosis", "समसूत्री विभाजन", ("mitosis", "mitotic", "समसूत्री")),
    ("polar body", "ध्रुवीय काय", ("polar bod*", "ध्रुवीय काय", "ध्रुवीय पिंड", "@pb 1", "@pb 2")),
    ("germinal epithelium", "जनन एपीथीलियम", ("epithelium", "एपीथीलियम")),
    ("fertilisation", "निषेचन", ("sperm", "fertilis*", "fertiliz*", "निषेचित", "निषेचन", "शुक्राणु")),
    ("timeline", "समयरेखा", ("timeline", "जन्म", "puberty", "किशोरावस्था")),
    # biology: genetics
    ("x-linked inheritance", "X सहलग्न वंशागति", ("x-linked", "x linked", "सहलग्न", "haemophilia", "हीमोफीलिया",
                                                   "colour blind*", "वर्णान्ध*", "x^h")),
    ("sex chromosomes", "लिंग गुणसूत्र", ("sex-chromosome*", "sex chromosome*", "x chromosome*", "y chromosome*",
                                          "x गुणसूत्र", "x^h", "@x male", "@y male", "@fath y", "@son y")),
    ("recessive allele", "अप्रभावी जीन", ("recessive", "अप्रभावी", "allele*")),
    ("carrier", "वाहक", ("carrier*", "वाहक")),
    ("criss-cross inheritance", "क्रिस-क्रॉस वंशागति", ("criss*", "क्रिस-क्रॉस", "क्रिस क्रॉस", "@crisscross")),
    ("punnett square", "पुनेट वर्ग", ("punnett", "पुनेट", "gamete*", "युग्मक")),
    ("pedigree generations", "पीढ़ी", ("pedigree", "generations", "hidden generation", "skipped generation",
                                        "a generation", "grandson", "पीढ़ी", "नाती")),
    # biology: biotechnology
    ("dna fingerprinting", "DNA अंगुलीछापी", ("fingerprint*", "अंगुलीछापी", "vntr", "dna pattern")),
    ("vntr repeats", "VNTR दोहराव", ("vntr", "tandem repeat*", "दोहराव", "@rep a 1", "@rep b 1")),
    ("gel electrophoresis", "जेल वैद्युत कण संचलन", ("gel", "electrophoresis", "जेल", "इलेक्ट्रोफोरेसिस")),
    ("southern blotting", "सदर्न ब्लॉटिंग", ("blot*", "southern", "सदर्न", "ब्लॉटिंग", "nitrocellulose")),
    ("hybridisation probe", "संकरण प्रोब", ("probe", "प्रोब", "संकरण", "hybridi*")),
    ("identical twins", "समान जुड़वाँ", ("twin*", "जुड़वाँ")),
    # layouts that recur across subjects
    ("graph on axes", "ग्राफ", ("against time", "against temperature", "against the progress",
                                "@axes", "@axis", "@axis heads", "@energy axis", "@graph")),
    ("comparison two panels", "तुलना", ("comparison", "side-by-side", "two panels", "तुलना", "@compare", "@divider")),
    ("difference table", "अंतर सारणी", ("differences", "two-column table")),
    ("counted list recap", "सारांश सूची", ("@recap", "@agenda")),
    ("beaker apparatus", "बीकर", ("beaker*", "vessel*", "बीकर", "@tube*")),
)

# Devanagari block, spelt with chr() so no combining mark sits bare in the source.
DEVA = chr(0x0900) + "-" + chr(0x097F)
_LETTER = f"[0-9A-Za-z{DEVA}{chr(0x03B8)}]"
_TRIGGERS = [(en, hi, [(t.startswith("@"),
                        re.compile(rf"(?<!{_LETTER}){re.escape(t.lstrip('@').rstrip('*').lower())}"
                                   + ("" if t.endswith("*") else rf"(?!{_LETTER})")))
                       for t in trig])
             for en, hi, trig in LEXICON]

# Figure names too generic to be a search term on their own.
GENERIC_NAMES = {"define", "map", "types", "graph", "recap", "chain", "reaction", "angle", "conc", "ratio"}


# --------------------------------------------------------------------------- inputs

def read_json(p: Path):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def part_no(p: Path) -> int:
    m = re.search(r"(\d+)", p.stem)
    return int(m.group(1)) if m else 0


def subject_of(slug: str) -> str:
    return SUBJECTS.get(slug.split("-")[0].lower(), "misc")


def not_shipped(d: Path) -> str | None:
    """Why this folder is not a shipped video yet, or None if it is."""
    st = d / "state.json"
    if not st.is_file():
        return None                      # built before build_clip.py kept state
    data = read_json(st)
    if not isinstance(data, dict):
        return "state.json unreadable"
    if (data.get("steps", {}).get("deliver") or {}).get("status") != "done":
        return "still being built (state.json: deliver not done)"
    return None


def beats_of(d: Path) -> list[tuple[int, dict]]:
    """Every beat with a diagram, as (tier, beat), most trusted tier first."""
    out = []
    spec = d / "spec"
    for tier, pat in enumerate(TIERS):
        for f in sorted(spec.glob(pat), key=lambda p: (part_no(p), p.name)):
            data = read_json(f)
            if isinstance(data, dict):
                data = data.get("beats") or data.get("segments") or []
            for b in data if isinstance(data, list) else []:
                if isinstance(b, dict) and isinstance(b.get("diagram"), dict) and b["diagram"].get("asset"):
                    out.append((tier, b))
    return out


def routes_of(d: Path) -> list[dict]:
    out = []
    for f in sorted((d / "spec").glob("route_part*.json"), key=lambda p: (part_no(p), p.name)):
        data = read_json(f)
        if isinstance(data, dict):
            data = data.get("beats") or []
        for r in data if isinstance(data, list) else []:
            if isinstance(r, dict) and (r.get("route") == "svg" or r.get("svg")):
                out.append(r)
    return out


def norm_asset(a: str) -> str:
    return Path(a.strip().lstrip("./")).as_posix()


# --------------------------------------------------------------------------- facts

def svg_ids(s: str) -> list[str]:
    return list(dict.fromkeys(re.findall(r'\bid\s*=\s*"([^"]+)"', s)))


def leading_comment(s: str) -> str:
    """The SVG's opening comment, minus the sentences about drawing rules."""
    m = re.search(r"<!--(.*?)-->", s, re.S)
    if not m or re.search(r"<(path|circle|rect|line|g|polygon|polyline|ellipse)\b", s[:m.start()]):
        return ""
    sentences = re.split(r"(?<=[.!?])\s+", " ".join(m.group(1).split()))
    return " ".join(x for x in sentences if not BOILERPLATE.search(x)).strip()


def words(ident: str) -> str:
    """ea_arrow -> 'ea arrow', gSphere -> 'g sphere', ox2 -> 'ox 2'."""
    s = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", ident)
    s = re.sub(r"(?<=[A-Za-z])(?=[0-9])|(?<=[0-9])(?=[A-Za-z])", " ", s)
    return " ".join(re.split(r"[_\-\s]+", s)).strip().lower()


def trim(s: str, n: int = SHOWS_MAX) -> str:
    s = " ".join(s.split())
    if len(s) <= n:
        return s
    cut = s[: n - 1]
    return (cut.rsplit(" ", 1)[0] if " " in cut else cut).rstrip(",;:—-") + "…"


def structure_line(name: str, s: str, ids: list[str]) -> str:
    counts = []
    for tag in ("path", "circle", "ellipse", "rect", "line", "polygon", "polyline"):
        n = len(re.findall(rf"<{tag}\b", s))
        if n:
            counts.append(f"{n} {tag}{'s' if n > 1 else ''}")
    parts = ", ".join(words(i) for i in ids) or "no ids"
    return f"{words(name).capitalize()} figure — parts: {parts}. Built from {', '.join(counts) or 'no shapes'}."


def keywords(name: str, structure: str, prose: str, labels: list[dict]) -> list[str]:
    """Lexicon hits (English then Hindi), then the figure's name, then its short Hindi labels."""
    out: list[str] = []
    structure, prose = structure.lower(), prose.lower()
    for en, hi, pats in _TRIGGERS:
        if any(p.search(structure) or (not only_structure and p.search(prose))
               for only_structure, p in pats):
            out += [en, hi]
    phrase = re.sub(r"^p \d+ ", "", words(name))
    phrase = re.sub(r"( \d+)+$", "", phrase)
    if phrase and phrase not in GENERIC_NAMES:
        out.append(phrase)
    for lab in labels:
        t = " ".join(str(lab.get("text", "")).split())
        if len(t) >= 3 and re.fullmatch(f"[{DEVA}]+(?: [{DEVA}]+){{0,2}}", t):
            out.append(t)
    return list(dict.fromkeys(out))[:KEYWORDS_MAX]


# --------------------------------------------------------------------------- build

def collect(skip: set[str]):
    figures, skipped = [], []
    candidates = []                                   # (slug, rel, path, bytes)
    for d in sorted(p for p in WORK.iterdir() if p.is_dir()):
        slug = d.name
        svgs = sorted(d.glob("assets/svg/*.svg")) + sorted(d.glob("assets/*.svg"))
        if not svgs or slug.startswith((".", "_")):
            continue
        why = "passed with --skip" if slug in skip else not_shipped(d)
        if why:
            skipped.append({"source": f"work/{slug}/", "reason": why})
            continue
        for p in svgs:
            candidates.append((slug, p.relative_to(d).as_posix(), p, p.read_bytes()))

    # one library file per distinct figure
    groups: dict[str, list] = {}
    beats_cache: dict[str, list] = {}
    for slug, rel, p, data in candidates:
        if slug not in beats_cache:
            beats_cache[slug] = beats_of(WORK / slug)
        groups.setdefault(hashlib.sha256(data).hexdigest(), []).append((slug, rel, p, data))

    def uses(slug, rel):
        bs = beats_cache[slug]
        exact = [(t, b) for t, b in bs if norm_asset(b["diagram"]["asset"]) == rel]
        return exact or [(t, b) for t, b in bs if Path(b["diagram"]["asset"]).name == Path(rel).name]

    names_taken: set[str] = set()
    for members in groups.values():
        members.sort(key=lambda m: (not uses(m[0], m[1]), m[0], m[1]))
        slug, rel, p, data = members[0]
        err, warn = lint(p)
        if err:
            for m in members:
                skipped.append({"source": f"work/{m[0]}/{m[1]}",
                                "reason": "; ".join(" ".join(e.split()) for e in err)})
            continue
        s = data.decode("utf-8")
        subject = subject_of(slug)
        name = p.stem
        fname = f"{slug}--{name}.svg"
        if f"{subject}/{fname}" in names_taken:       # same stem in assets/ and assets/svg/
            fname = f"{slug}--{name}-{Path(rel).parent.name}.svg"
        names_taken.add(f"{subject}/{fname}")

        found = uses(slug, rel)
        top = min((t for t, _ in found), default=None)
        primary = [b for t, b in found if t == top]
        ids = svg_ids(s)
        comment = leading_comment(s)
        route = None
        if primary:
            types = [b.get("type") for b in primary]
            rs = routes_of(WORK / slug)
            route = (next((r for r in rs if r.get("svg") and Path(r["svg"]).name == p.name), None)
                     or next((r for r in rs if r.get("slug") in types), None)
                     or next((r for r in rs if r.get("slug") == name), None))

        whys = [b["_why"] for b in primary if isinstance(b.get("_why"), str) and b["_why"].strip()]
        narration = ""
        for _, b in found:
            vo = b.get("voiceover") or " ".join(ph.get("text", "") for ph in b.get("phrases") or []
                                                if isinstance(ph, dict))
            if vo.strip():
                narration = vo
                break
        mark = (route or {}).get("mark") or ""
        if whys:
            shows = whys[0]
        elif comment:
            shows = comment
        elif mark:
            shows = mark
        elif narration:
            shows = f"Drawn while he says: {narration}"
        else:
            shows = structure_line(name, s, ids)
        if not primary:
            shows = f"No beat in {slug} draws this figure. " + shows

        animated: list[str] = []
        labels: list[dict] = []
        seen_labels = set()
        for b in primary:
            for a in b["diagram"].get("timeline") or []:
                if isinstance(a, dict) and a.get("id") and a["id"] not in animated:
                    animated.append(a["id"])
            for lab in b.get("labels") or []:
                if not isinstance(lab, dict) or not lab.get("text"):
                    continue
                entry = {"text": lab["text"]}
                for k in ("x", "y"):
                    if isinstance(lab.get(k), (int, float)):
                        entry[k] = lab[k]
                key = (entry["text"], entry.get("x"), entry.get("y"))
                if key not in seen_labels:
                    seen_labels.add(key)
                    labels.append(entry)

        structure = " \n ".join([words(name), " ".join(words(i) for i in ids),
                                  " ".join(words(str(b.get("type", ""))) for b in primary)])
        prose = " \n ".join([" ".join(whys), comment, mark, (route or {}).get("why_drawn") or "",
                             narration if not whys else "", " ".join(lab["text"] for lab in labels)])

        figures.append({
            "file": f"{subject}/{fname}",
            "subject": subject,
            "video": slug,
            "beat": primary[0].get("type") if primary else None,
            "beats": list(dict.fromkeys(str(b.get("type")) for b in primary)),
            "used": bool(primary),
            "shows": trim(shows),
            "ids": ids,
            "animated": animated,
            "labels": labels,
            "topic_keywords": keywords(name, structure, prose, labels),
            "lint_warnings": [" ".join(w.split()) for w in warn],
            "source": f"work/{slug}/{rel}",
            "also_in": [f"work/{m[0]}/{m[1]}" for m in members[1:]],
            "_bytes": data,
        })

    figures.sort(key=lambda f: (f["subject"], f["video"], f["file"]))
    skipped.sort(key=lambda x: x["source"])
    return figures, skipped


def render_index(figures, skipped) -> bytes:
    counts: dict[str, int] = {}
    for f in figures:
        counts[f["subject"]] = counts.get(f["subject"], 0) + 1
    doc = {
        "about": "Generated by tools/clip/figures/build_index.py from the shipped videos in work/. "
                 "Do not edit by hand: re-run the script. Stage is viewBox 0 0 1080 470; label x/y are "
                 "fractions of that stage. used=false means no beat of that video drew the figure.",
        "counts": dict(sorted(counts.items())),
        "figures": [{k: v for k, v in f.items() if not k.startswith("_")} for f in figures],
        "skipped": skipped,
    }
    return (json.dumps(doc, ensure_ascii=False, indent=1) + "\n").encode("utf-8")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true", help="report what would change and exit 1 if anything would")
    ap.add_argument("--skip", action="append", default=[], metavar="SLUG", help="leave this work/<slug> out")
    args = ap.parse_args(argv)

    figures, skipped = collect(set(args.skip))
    want = {HERE / f["file"]: f["_bytes"] for f in figures}
    want[INDEX] = render_index(figures, skipped)

    changes = []
    for path, data in sorted(want.items()):
        if not path.is_file() or path.read_bytes() != data:
            changes.append(("write", path, data))
    for sub in sorted(p for p in HERE.iterdir() if p.is_dir() and not p.name.startswith((".", "_"))):
        for svg in sorted(sub.glob("*.svg")):
            if svg not in want:
                changes.append(("remove", svg, None))

    for op, path, data in changes:
        rel = path.relative_to(ROOT)
        if args.check:
            print(f"  stale  {op:6} {rel}")
            continue
        if op == "write":
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        else:
            path.unlink()
        print(f"  {op:6} {rel}")
    if not args.check:
        for sub in sorted(p for p in HERE.iterdir() if p.is_dir() and not p.name.startswith((".", "_"))):
            if not any(sub.iterdir()):
                sub.rmdir()

    counts: dict[str, int] = {}
    for f in figures:
        counts[f["subject"]] = counts.get(f["subject"], 0) + 1
    print(f"figures: {len(figures)}  " + "  ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    for sk in skipped:
        print(f"  skipped {sk['source']}: {sk['reason']}")
    print(("stale: " if args.check else "changed: ") + str(len(changes)))
    return 1 if (args.check and changes) else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
