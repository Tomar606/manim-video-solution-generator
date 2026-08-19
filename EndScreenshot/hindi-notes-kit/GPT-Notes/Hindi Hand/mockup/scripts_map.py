#!/usr/bin/env python3
"""Super/subscript folding, shared by the importer and the preflight gate.

`<sup>`/`<sub>` carry meaning in these chapters -- I^A, F_1, ^32-P, ^15-N, CO_2, N_t, 3.3x10^9 --
but BeautifulSoup's `get_text(" ")` splits the run off into its own token, so I^A reaches the page
as "I A" and CO_2 as "CO 2". Folding them to single Unicode characters fixes it.

This lives in its own module, with no dependencies, because preflight.py needs the same mapping to
verify a chapter and has no business importing an HTML parser to get at a regex.
"""
from __future__ import annotations

import re

# Only the letters Unicode actually HAS in each position are listed. There is no superscript
# C, F, Q, S, X, Y or Z, and no capital subscript at all.
SUP_MAP = str.maketrans(
    "0123456789+-=()"          "abdeghijklmnoprstuvwxyz"  "ABDEGHIJKLMNOPRTUVW",
    "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾"          "ᵃᵇᵈᵉᵍʰⁱʲᵏˡᵐⁿᵒᵖʳˢᵗᵘᵛʷˣʸᶻ"  "ᴬᴮᴰᴱᴳᴴᴵᴶᴷᴸᴹᴺᴼᴾᴿᵀᵁⱽᵂ")
SUB_MAP = str.maketrans(
    "0123456789+-=()"          "aehijklmnoprstuvx",
    "₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎"          "ₐₑₕᵢⱼₖₗₘₙₒₚᵣₛₜᵤᵥₓ")
SCRIPT_RE = re.compile(r"<(sup|sub)\b[^>]*>(.*?)</\1>", re.S | re.I)

# Every character the two maps can produce -- what a "this is a super/subscript" test looks for.
SCRIPT_CHARS = "".join(sorted({chr(v) for v in list(SUP_MAP.values()) + list(SUB_MAP.values())}))


# Not every raised character is tagged in the source. Ch5 writes the Hershey-Chase and
# Meselson-Stahl isotopes as bare text -- "32P", "35S", "15N", "14N" -- with no <sup> at all, so
# three drawn pages read "फॉस्फोरस (32P)" instead of ³²P and the tag-parity gate could not see it:
# it can only compare what the source marked up.
#
# So a second, SEPARATE pass folds a short ALLOW-LIST of forms that are unambiguous in this
# corpus. It is a list, not a pattern, on purpose: a rule like "digits before a capital letter"
# would also catch 16S rRNA, RY13 and a dozen accidents. Every entry here was read off a real
# occurrence in pulled_rj_biology/Hindi (see the audit in BARE_FORMS_AUDIT below).
BARE_FORMS = {
    # isotopes: the mass number RISES and labels the element that follows it
    "32P": "³²P", "33P": "³³P", "35S": "³⁵S", "15N": "¹⁵N", "14N": "¹⁴N",
    "13C": "¹³C", "14C": "¹⁴C", "3H": "³H", "125I": "¹²⁵I",
    # labelled molecule and density-gradient band pairs: BOTH kinds in one token, which is why
    # this is a table and not a rule -- in "15NH4Cl" the 15 rises and the 4 drops, in "15N15N"
    # both rise. No inference gets that right; every entry is written out and can be read.
    "15NH4Cl": "¹⁵NH₄Cl", "14NH4Cl": "¹⁴NH₄Cl",
    "15N15N": "¹⁵N¹⁵N", "14N14N": "¹⁴N¹⁴N", "15N14N": "¹⁵N¹⁴N", "14N15N": "¹⁴N¹⁵N",
    # formulae: the count DROPS under the element before it
    "NH4Cl": "NH₄Cl", "NH4": "NH₄", "NH3": "NH₃", "CO2": "CO₂", "CH4": "CH₄",
    "H2O": "H₂O", "H2S": "H₂S", "H2": "H₂", "N2": "N₂", "O2": "O₂", "B12": "B₁₂",
    "F1": "F₁", "F2": "F₂",
}
# where each was found, so a new chapter's audit can be diffed against this
BARE_FORMS_AUDIT = {"Ch5": ("14N", "15N", "32P", "35S"), "Ch4": ("F1", "F2"),
                    "Ch6": ("CH4", "NH3", "H2"), "Ch8": ("CO2", "B12")}

# longest first, so 15NH4Cl wins over 15N and NH4Cl over NH4. The guards keep RY13, 16S rRNA
# and IgG2a intact, and '<' keeps the pass off tag internals like <h2>.
BARE_RE = re.compile(r"(?<![A-Za-z0-9<])("
                     + "|".join(re.escape(k) for k in sorted(BARE_FORMS, key=len, reverse=True))
                     + r")(?![A-Za-z0-9])")


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.replace("\xa0", " ")).strip()


def script_runs(raw: str) -> list[tuple[str, str, str | None]]:
    """Every <sup>/<sub> in the source as (kind, source text, converted text).

    `converted is None` marks a run Unicode cannot express -- the one case scriptify() cannot fix,
    and the case the importer refuses outright rather than write flattened.
    """
    out = []
    for m in SCRIPT_RE.finditer(raw):
        kind, body = m.group(1).lower(), _norm(m.group(2))
        table = SUP_MAP if kind == "sup" else SUB_MAP
        ok = bool(body) and all(ord(c) in table for c in body)
        out.append((kind, body, body.translate(table) if ok else None))
    return out


def scriptify(raw: str) -> str:
    """Fold every mappable <sup>/<sub> in the RAW HTML to Unicode.

    It must be applied to the raw string rather than to a parsed tree: import_notes.verify()
    re-parses the source independently to prove no word was lost, so converting only one side
    would make that word gate abort on every converted run.
    """
    def sub(m):
        body = _norm(m.group(2))
        table = SUP_MAP if m.group(1).lower() == "sup" else SUB_MAP
        if not body or any(ord(c) not in table for c in body):
            return m.group(0)                      # not fully mappable -- leave it alone
        return body.translate(table)
    raw = SCRIPT_RE.sub(sub, raw)
    return bare_forms(raw)


def bare_forms(raw: str) -> str:
    """Second pass: fold the allow-listed forms the source never tagged at all.

    Runs on HTML, so it must not touch tag internals -- the lookbehind excludes '<' and the
    trailing guard excludes a following letter or digit, which keeps <h2>, RY13 and IgG2a intact.
    """
    return BARE_RE.sub(lambda m: BARE_FORMS[m.group(1)], raw)


def flat_survivors(text: str) -> list[str]:
    """Allow-listed forms still sitting flat in already-laid-out text. Used by preflight."""
    return sorted({m.group(1) for m in BARE_RE.finditer(text)})
