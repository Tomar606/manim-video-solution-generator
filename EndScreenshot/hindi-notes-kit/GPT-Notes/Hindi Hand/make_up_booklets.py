#!/usr/bin/env python3
"""make_up_booklets.py — normalise the UP-Board Hindi PYQ HTMLs into canonical Top-5 booklets.

The UP set arrived already curated to five questions per chapter, so there is no ranking step
(that is what build_top5.py does for MP/Rajasthan). What it needs is a shape fix: the UP export
differs from the MP/RJ booklets in four ways that would each silently corrupt the import.

  1. Every answer PARAGRAPH is its own sibling `<div class="ans show">`. import_htmls.py reads a
     single `<div class="ans">` per card and only understands <p>/<ul>/<ol>/<table>/<img> inside
     it, so all the loose paragraphs — which is nearly the entire answer body, 65 cards of it —
     would be dropped and the pages would come out as questions with no answers.
  2. Figures are `figures/<file>` references. The importer decodes base64 data URIs only, so
     every figure (and its whole diagram page) would vanish.
  3. `class="ans show"` rather than `class="ans"`.
  4. Sub/superscripts are <sub>/<sup> MARKUP. strip_tags() flattens them, turning H<sub>2</sub>S
     into "H2S". The rest of this pipeline carries them as Unicode (the existing pages use F₂),
     so they are converted here — see the superscript-fidelity rule in the build notes.

Output goes into the same tree build_top5.py writes, so import_htmls.py picks it up with no
special case beyond the `up` board key:

    <SRC>/UP/Ch<N>/UP_Ch<N>_Top5_PYQ_Hindi.html

Nothing here calls an API and the user's source folder is only ever READ.

Usage:
  ../.venv/bin/python make_up_booklets.py          # all 13 chapters
  ../.venv/bin/python make_up_booklets.py 1 3      # named chapters
"""
from __future__ import annotations

import base64
import mimetypes
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString

SRC_ROOT = Path("/Users/vedanshsharma/PCMB Notes Final/GPT-Notes/bio pyqs/bio hindi/Biology PYQs")
OUT_ROOT = Path("/Users/vedanshsharma/GPT-Notes/top5_pyq_html/Class12/Biology_PYQs/Hindi/UP")

SUB = str.maketrans("0123456789+-=()n", "₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎ₙ")
SUP = str.maketrans("0123456789+-=()n", "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾ⁿ")

BLOCK_TAGS = {"ul", "ol", "table", "img", "p"}

# Chapter 11 shipped five of its six "figures" as screenshot crops of MATHS, not drawings: three
# rate formulae and the exponential/logistic growth equations. Hand-drawing an equation on a
# figure page reads badly, and dropping them would lose the maths outright — the theory text
# defines जन्म-दर/मृत्यु-दर but never states the formulae. So they are transcribed here, read off
# the images, and substituted for the <img> as ordinary paragraphs. They then flow into the page
# as <<TEXT>> and are written in the same hand as everything else.
#
# Fractions are written inline with "/" because a stacked fraction bar has no place in running
# handwritten prose. Sub/superscripts use the Unicode forms the rest of the pipeline carries.
# Keyed by the source file name, which is stable and unique per figure.
EQUATION_TEXT = {
    # up-ch11-fig-01
    "1786169387842-63u7bx.jpg": [
        "जन्म-दर = उत्पन्न नए व्यष्टियों की संख्या / आरंभिक समष्टि की कुल संख्या",
    ],
    # up-ch11-fig-02
    "1786169645900-v0p0xb.jpg": [
        "मृत्यु-दर = मरे हुए व्यष्टियों की संख्या / आरंभिक समष्टि की कुल संख्या",
    ],
    # up-ch11-fig-03
    "1786169693278-zyjjby.jpg": [
        "समष्टि घनत्व (N) = जीवों की कुल संख्या (n) / कुल क्षेत्रफल या आयतन (S)",
    ],
    # exponential growth, equation block with its own surrounding prose.
    # ⚠️ These two file names are NOT in the order the figures are numbered in. This entry was
    # first keyed to prrac2 by counting <img> positions, which silently transcribed away the real
    # growth-CURVE graph and left this equation block behind to be hand-drawn as a "figure". Both
    # files were opened and identified before the swap; do not re-derive these keys positionally.
    "1786173115899-11r9x3.jpg": [
        "समीकरण : यदि समष्टि का आकार N, जन्म-दर b, मृत्यु-दर d तथा समय t हो, "
        "तो समष्टि वृद्धि की दर —",
        "dN/dt = (b − d)N",
        "मान लीजिए (b − d) = r (प्राकृतिक वृद्धि की अंतर्जात दर), तो —",
        "dN/dt = rN",
        "इसका समाकलित रूप (Integral form) निम्नलिखित है —",
        "Nₜ = N₀eʳᵗ",
        "(जहाँ Nₜ = t समय में समष्टि घनत्व, N₀ = 0 समय में समष्टि घनत्व, "
        "r = अंतर्जात वृद्धि दर, e = प्राकृतिक लघुगणक का आधार ≈ 2.71828)",
    ],
    # up-ch11-fig-06 — logistic growth
    "1786173296535-an64mj.jpg": [
        "समीकरण : dN/dt = rN (K − N)/K",
        "(जहाँ N = समष्टि घनत्व, r = अंतर्जात वृद्धि दर, K = पोषण क्षमता)",
    ],
}


def to_unicode_scripts(soup: BeautifulSoup) -> None:
    """<sub>2</sub> -> ₂ so the text survives strip_tags() downstream.

    Only digits and the few operators in the tables above translate; anything else is left as
    plain text rather than silently mangled into a lookalike.
    """
    for tag_name, table in (("sub", SUB), ("sup", SUP)):
        for t in soup.find_all(tag_name):
            txt = t.get_text()
            t.replace_with(NavigableString(txt.translate(table) if txt.strip() else txt))


def inline_figures(soup: BeautifulSoup, chapter_dir: Path) -> int:
    """figures/<file> -> data: URI, and unwrap the <figure class="dfig"> shell around it."""
    n = 0
    for fig in soup.find_all("figure"):
        fig.unwrap()
    for img in soup.find_all("img"):
        src = img.get("src", "")
        lines = EQUATION_TEXT.get(Path(src).name)
        if lines is not None:
            # transcribed maths: becomes prose, and no diagram page is built for it
            for line in lines:
                p = soup.new_tag("p")
                p["class"] = ["eqn"]     # tagged so the sweep below can find it again
                p.string = line
                img.insert_before(p)
            img.decompose()
            continue
        if src.startswith("data:"):
            n += 1
            continue
        f = chapter_dir / src
        if not f.exists():
            print(f"    ! missing figure {src} — dropping the <img>", file=sys.stderr)
            img.decompose()
            continue
        mime = mimetypes.guess_type(f.name)[0] or "image/jpeg"
        img["src"] = f"data:{mime};base64,{base64.b64encode(f.read_bytes()).decode()}"
        img.attrs.pop("style", None)
        n += 1
    return n


def merge_answer(card, soup: BeautifulSoup):
    """Fold the card's many `.ans` divs into ONE `<div class="ans">` of block-level children.

    Loose text (the common case here) becomes a <p>; a div that already wraps a list/table/image
    contributes that element unchanged. Order is preserved exactly.
    """
    ans_divs = card.find_all("div", class_="ans")
    if not ans_divs:
        return None
    merged = soup.new_tag("div")
    merged["class"] = ["ans"]

    for div in ans_divs:
        # the "उत्तर:" label is re-added by the importer itself; drop the source's copy
        for al in div.find_all("span", class_="al"):
            al.decompose()
        children = [c for c in div.contents
                    if not (isinstance(c, NavigableString) and not c.strip())]
        # a div holding only block elements: move them across as they are
        if children and all(getattr(c, "name", None) in BLOCK_TAGS for c in children):
            for c in list(children):
                merged.append(c.extract())
            continue
        # otherwise it is a text paragraph (possibly with <b>/<i>/<br> inside) -> one <p>
        p = soup.new_tag("p")
        for c in list(children):
            p.append(c.extract())
        if p.get_text(strip=True) or p.find("img"):
            merged.append(p)

    for div in ans_divs:
        div.decompose()

    # Some figures sit OUTSIDE the .ans divs — loose in the card, or attached to the question.
    # The merged .ans is appended last, and the importer reads only from the first `<div
    # class="ans">` to the end of the card, so anything left behind here is invisible to it and
    # its diagram page never gets built. Sweep them in; a card's figures belong to that card
    # either way.
    # ...and the same is true of a transcribed equation that REPLACED such a figure: it inherits
    # the figure's position, so it can be left stranded between the question and the answer where
    # the importer's word gate reports it as lost text.
    for el in card.find_all(["img"]) + card.find_all("p", class_="eqn"):
        merged.append(el.extract())
    return merged


def build(num: int) -> tuple[Path, int, int] | None:
    chapter_dir = SRC_ROOT / f"Ch{num}"
    src = chapter_dir / f"Ch{num}.html"
    if not src.exists():
        print(f"[Ch{num}] SKIP: {src} not found", file=sys.stderr)
        return None
    soup = BeautifulSoup(src.read_text(encoding="utf-8"), "html.parser")

    to_unicode_scripts(soup)
    nfig = inline_figures(soup, chapter_dir)

    for btn in soup.find_all("button"):
        btn.decompose()

    cards = soup.find_all("div", class_="card")
    for rank, card in enumerate(cards, 1):
        merged = merge_answer(card, soup)
        if merged is not None:
            card.append(merged)
        badges = card.find("div", class_="badges")
        if badges is not None and not badges.find("span", class_="tag-rank"):
            rank_tag = soup.new_tag("span")
            rank_tag["class"] = ["tag", "tag-rank"]
            rank_tag.string = f"#{rank}"
            badges.insert(0, rank_tag)
        qn = card.select_one(".qn")
        if qn:
            qn.string = f"Q{rank}."

    out = OUT_ROOT / f"Ch{num}" / f"UP_Ch{num}_Top5_PYQ_Hindi.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(str(soup), encoding="utf-8")
    return out, len(cards), nfig


def main() -> int:
    nums = [int(a) for a in sys.argv[1:]] or list(range(1, 14))
    total_cards = total_figs = 0
    for n in nums:
        r = build(n)
        if r is None:
            continue
        out, ncards, nfig = r
        total_cards += ncards
        total_figs += nfig
        print(f"[Ch{n:2d}] {ncards} cards, {nfig} figure(s) -> {out.parent.name}/{out.name}")
    print(f"\nTOTAL: {total_cards} cards, {total_figs} figures")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
