#!/usr/bin/env python3
"""Stage 1a for PYQ booklets — read a Top-5 PYQ HTML into tagged blocks, capturing EVERY word.

    import_pyq.py UP/Ch1        one chapter
    import_pyq.py --all         every UP chapter under the Top-5 tree

Output: notes/UP-Ch<N>/blocks.json  (+ notes/UP-Ch<N>/figures/ — the figures decoded to files)

This is the PYQ twin of import_notes.py, so that PYQ pages go through the SAME mock-up pipeline
as the notes chapters: typeset_mockup.py -> preflight.py -> gen_from_mockup.py. The older direct
path (../gen_hindi.py) sent an unmeasured page straight to the image model; here the page is laid
out and mechanically checked before a single call is billed.

HOW A CARD MAPS ONTO THE NOTES BLOCK KINDS
------------------------------------------
The two-ink rule is the whole reason this maps cleanly. In the notes prompt BLACK is the title and
every heading, BLUE is everything else — which is exactly the PYQ convention of a black question
and a blue answer. So:

    chapter title            -> title            (black, header band)
    "प्र.N  [type · years · marks · Nx]"  -> subhead, nogap_after   (black)
    the question text        -> subhead, nogap_before               (black, hard under the strap)
    "उत्तर : …" and the rest -> text / point / table                (blue)
    a figure                 -> fig                                 (blue, drawn INLINE in place)

Figures are inline blocks, exactly as in the notes chapters — there are no separate dia-NN pages.
The typesetter gives a fig its own rows in the page flow and the model draws it there.

SUPER/SUBSCRIPTS are folded to single Unicode characters through scripts_map, the same module
preflight.py checks against, so H<sub>2</sub>S becomes H₂S in the block, the blueprint and the
prompt alike rather than collapsing to "H2S".

AND THE IMPORT IS VERIFIED, NOT TRUSTED
---------------------------------------
verify() requires every source token to survive into a block, in order. Any loss aborts with the
missing runs printed, because a silent gap must never reach a billed render.
"""
from __future__ import annotations

import base64
import difflib
import json
import os
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString, Tag

from scripts_map import scriptify

HERE = Path(__file__).resolve().parent
# Top-5 PYQ HTML tree. Defaults to the copy shipped inside this kit; override with
# TOP5_HTML_ROOT=/path/to/.../Biology_PYQs/Hindi when you keep the source elsewhere.
SRC_ROOT = Path(os.environ.get(
    "TOP5_HTML_ROOT",
    HERE.parent.parent.parent / "top5_pyq_html" / "Class12" / "Biology_PYQs" / "Hindi"))
OUT_ROOT = HERE.parent / "notes"

# Web furniture that is not page content: the breadcrumb, the "माध्यम / Type / Total" strap, the
# "5 चुनिंदा प्रश्न" bar, the "चयन का आधार" lead-in and the footer credit. `title` is dropped too —
# it holds the ENGLISH chapter name beside the Hindi one, and only the Hindi is written on the
# page (it is taken straight from `.title .hi`, so nothing is being skipped unchecked).
DROP_CLASSES = {"crumb", "meta", "lead", "foot", "bar", "title"}

# Excluded from the word gate because they are RE-FORMATTED rather than copied: the badge strap is
# rebuilt as "प्र.N  [type · years · marks · Nx]", which joins the year tags with "/" and wraps the
# lot in brackets, so it can never match the source token-for-token. It is generated from these
# very tags by badge_line(), so there is nothing a comparison here would catch.
DROP_SELECTORS = ".qn, .al, .tag-rank, .badges"


DATA_URI_RE = re.compile(r"data:image/[a-z+]+;base64,[A-Za-z0-9+/=\s]+")


# Some "figures" in this source are not drawings at all — they are printed FLOWCHARTS, boxes of
# text joined by arrows. Handing one to the image model as a picture asks it to hand-copy
# paragraphs, and that is exactly where it stops reading and starts inventing: UP-Ch10's ADA chart
# came back with a person, a retrovirus and cells that are nowhere in the source, and UP-Ch12's
# decomposition chart vanished from the page altogether.
#
# So they are transcribed instead. A <<FLOW>> block is TYPESET into the blueprint by
# typeset_mockup.py — the model copies words that are already laid out for it, with arrows drawn
# between them, rather than reading them off a grey guide. Same treatment as chapter 11's
# equations, which came back word-perfect.
#
# Keyed by the figure slot the transcription REPLACES. Read off the source images.
# Figures that get NO page at all. UP-Ch5/fig-03 is the RNA + nucleobase graphic: dark-ground art
# flattened onto white, so its label text arrives fragmented, and the render duly attached the
# base names to the WRONG ring structures. No clean version of it exists in any pool or in NCERT,
# which has no RNA-structure figure. The page's own text already carries the teaching points
# (uracil replacing thymine, and the three RNA types), so a wrong drawing is pure loss.
DROP_FIGURES = {"UP-Ch5/fig-03"}

FLOW_TRANSCRIPTION = {
    "UP-Ch12/fig-01": {
        "rows": [
            ["चरण", "विवरण"],
            ["प्रारंभ", "वृक्ष से हरी पत्ती / काष्ठ गिरता है, जिससे मृत कार्बनिक पदार्थ / अपरद (Detritus) बनता है"],
            ["(1) खडन (Fragmentation)", "अपरदाहारी (उदा. केंचुआ) अपरद को छोटे टुकड़ों में तोड़ते हैं; कुछ भाग कीटों / जीवों द्वारा खा लिया जाता है"],
            ["(2) निक्षालन (Leaching)", "जल में घुलनशील पोषक तत्व मृदा में गहराई में चले जाते हैं"],
            ["(3) अपचय (Catabolism)", "कवक एवं जीवाणुवीय एंजाइमों द्वारा सरल पदार्थों में अपघटन"],
            ["(4) ह्यूमीकरण (Humification)", "गहरे रंग का अमूर्त पदार्थ 'ह्यूमस' बनता है"],
            ["(5) खनिजभवन (Mineralisation)", "अकार्बनिक पोषक तत्व (जैसे- Ca, P, N) मृदा में मुक्त होते हैं"],
            ["अंत", "पौधों की जड़ों द्वारा पुनः अवशोषण"],
        ],
        "after": "",
    },
    "UP-Ch10/fig-01": {
        "rows": [
            ["चरण", "क्रिया"],
            ["1.", "रोगी के रक्त से लसिकाणु (Lymphocytes) को बाहर निकालकर संवर्धन (Culture) करना"],
            ["2.", "पश्चविषाणु (Retrovirus) संवाहक का उपयोग करके सामान्य/सक्रिय ADA-cDNA को लसिकाणु में प्रवेश कराना"],
            ["3.", "इस रूपांतरित (जीन-युक्त) लसिकाणु को रोगी के शरीर में पुनः वापस डालना"],
            ["4.", "परिणाम: रोगी के शरीर में कार्यात्मक ADA एंजाइम बनने लगता है"],
        ],
        "after": "इस प्रकार जीन चिकित्सा द्वारा ADA कमी रोग का उपचार किया जाता है।",
    },
}


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def scriptify_safe(raw: str) -> str:
    """scriptify() the markup WITHOUT letting it near the base64 figure payloads.

    scripts_map's second pass folds bare allow-listed forms ("32P" -> "³²P") straight on the HTML
    string. A base64 blob is arbitrary alphanumerics, so it can contain those forms by chance —
    and rewriting two characters inside one corrupts the image beyond decoding (Ch2 died on
    "Incorrect padding"). The payloads are lifted out, the markup is folded, then they go back.
    """
    stash: list[str] = []

    def hide(m):
        stash.append(m.group(0))
        return f"\x00DATAURI{len(stash) - 1}\x00"

    out = scriptify(DATA_URI_RE.sub(hide, raw))
    return re.sub(r"\x00DATAURI(\d+)\x00", lambda m: stash[int(m.group(1))], out)


def text_of(el: Tag) -> str:
    """Visible text of an element. The whole document was scriptified before parsing, so the
    super/subscripts are already single Unicode characters by this point."""
    return norm(el.get_text(" "))


def chapter_title(soup: BeautifulSoup) -> str:
    hi = soup.select_one(".title .hi")
    if hi:
        return norm(hi.get_text(" "))
    t = soup.select_one(".title")
    return norm(t.get_text(" ")) if t else "जीव विज्ञान"


def badge_line(card: Tag, idx: int) -> str:
    def one(sel):
        el = card.select_one(sel)
        return norm(el.get_text(" ")) if el else ""

    years = [norm(y.get_text(" ")) for y in card.select(".tag-year")]
    parts = [p for p in (one(".tag-type"), "/".join(years),
                         one(".tag-marks"), one(".tag-rep")) if p]
    return f"प्र.{idx}  [{' · '.join(parts)}]" if parts else f"प्र.{idx}"


def emit_answer(ans: Tag, blocks: list, fig_out: Path, chapter_dir: Path, state: dict) -> None:
    """Walk the merged .ans body into blue blocks, in order."""
    first_text = True
    for el in ans.children:
        if isinstance(el, NavigableString):
            if norm(str(el)):
                blocks.append({"kind": "text", "text": norm(str(el))})
            continue
        if not isinstance(el, Tag):
            continue
        name = el.name.lower()
        if name == "img":
            if flow_instead(fig_out, blocks, state):
                continue
            src = save_figure(el, fig_out, state)
            if src:
                blocks.append({"kind": "fig", "src": src, "caption": ""})
            continue
        if name in ("ul", "ol"):
            for i, li in enumerate(el.find_all("li", recursive=False), 1):
                for img in li.find_all("img"):
                    if flow_instead(fig_out, blocks, state):
                        img.decompose()
                        continue
                    src = save_figure(img, fig_out, state)
                    img.decompose()
                    if src:
                        blocks.append({"kind": "fig", "src": src, "caption": ""})
                txt = text_of(li)
                if txt:
                    b = {"kind": "point", "text": txt}
                    if name == "ol":
                        b["num"] = i
                    blocks.append(b)
            continue
        if name == "table":
            rows = []
            for tr in el.find_all("tr"):
                cells = [text_of(c) for c in tr.find_all(["th", "td"])]
                if any(cells):
                    rows.append(cells)
            if rows:
                blocks.append({"kind": "table", "rows": rows})
            continue
        # <p> and anything else: pull out any nested figure, then take the text
        for img in el.find_all("img"):
            if flow_instead(fig_out, blocks, state):
                img.decompose()
                continue
            src = save_figure(img, fig_out, state)
            img.decompose()
            if src:
                blocks.append({"kind": "fig", "src": src, "caption": ""})
        txt = text_of(el)
        if not txt:
            continue
        if first_text:
            txt, first_text = f"उत्तर : {txt}", False
        blocks.append({"kind": "text", "text": txt})


def next_slot(fig_out: Path, state: dict) -> str:
    """The slot id the NEXT figure takes, e.g. "UP-Ch12/fig-01".

    Counts EVERY figure seen, transcribed ones included. A transcribed figure still consumes its
    number — otherwise the next real figure inherits the slot, which silently renumbered Ch12's
    trophic-levels chart onto the decomposition slot and emitted the transcription twice.
    """
    return f"{fig_out.parent.name}/fig-{state['n'] + 1:02d}"


def flow_instead(fig_out: Path, blocks: list, state: dict) -> bool:
    """If this figure slot is transcribed, emit the <<FLOW>> block and skip the image."""
    slot = next_slot(fig_out, state)
    if slot in DROP_FIGURES:
        state["n"] += 1
        return True
    spec = FLOW_TRANSCRIPTION.get(slot)
    if not spec:
        return False
    state["n"] += 1
    blocks.append({"kind": "table", "rows": spec["rows"]})
    if spec.get("after"):
        blocks.append({"kind": "text", "text": spec["after"]})
    return True


def save_figure(img: Tag, fig_out: Path, state: dict) -> str | None:
    """Decode a data: URI figure to a real file and return its relative src."""
    m = re.search(r"data:image/([a-z+]+);base64,([A-Za-z0-9+/=\s]+)", img.get("src", ""))
    if not m:
        return None
    ext = "jpg" if m.group(1) == "jpeg" else m.group(1)
    fig_out.mkdir(parents=True, exist_ok=True)
    state["n"] += 1
    name = f"fig-{state['n']:02d}.{ext}"
    (fig_out / name).write_bytes(base64.b64decode(m.group(2)))
    return f"figures/{name}"


def captured_text(blocks) -> str:
    out = []
    for b in blocks:
        k = b["kind"]
        if k in ("title", "subhead", "text", "point"):
            out.append(b["text"])
        elif k == "table":
            for r in b["rows"]:
                out.extend(r)
        elif k == "flow":
            for st in b["steps"]:
                out.append(st["text"])
                if st.get("note"):
                    out.append(st["note"])
            if b.get("caption"):
                out.append(b["caption"])
    return " ".join(out)


def verify(soup: BeautifulSoup, blocks) -> list[str]:
    """Runs of source text that never reached a block. Empty = nothing lost."""
    doc = BeautifulSoup(str(soup), "html.parser")
    for bad in doc(["script", "style", "button"]):
        bad.decompose()
    for cls in DROP_CLASSES:
        for el in doc.select(f".{cls}"):
            el.decompose()
    for el in doc.select(DROP_SELECTORS):
        el.decompose()
    body = doc.body or doc
    src_tokens = norm(body.get_text(" ")).split()
    got_tokens = norm(captured_text(blocks)).split()
    sm = difflib.SequenceMatcher(None, src_tokens, got_tokens, autojunk=False)
    missing = []
    for tag, i1, i2, _, _ in sm.get_opcodes():
        if tag in ("delete", "replace"):
            missing.append(" ".join(src_tokens[i1:i2]))
    return [m for m in missing if m.strip()]


def run(rel: str) -> bool:
    board, ch = rel.split("/")
    src = SRC_ROOT / board / ch / f"{board}_{ch}_Top5_PYQ_Hindi.html"
    if not src.exists():
        print(f"[{rel}] ERROR: {src} not found", file=sys.stderr)
        return False
    # scriptify the RAW html before parsing, so the <sup>/<sub> runs are already single Unicode
    # characters on BOTH sides of the verify() comparison below
    soup = BeautifulSoup(scriptify_safe(src.read_text(encoding="utf-8")), "html.parser")

    out_dir = OUT_ROOT / f"{board}-{ch}"
    fig_out = out_dir / "figures"
    if fig_out.exists():
        for old in fig_out.glob("fig-*"):
            old.unlink()

    state = {"n": 0}          # figures seen so far in this chapter, transcribed included
    blocks: list[dict] = [{"kind": "title", "text": chapter_title(soup)}]
    for idx, card in enumerate(soup.select(".card"), 1):
        blocks.append({"kind": "subhead", "text": badge_line(card, idx), "nogap_after": True})
        q = card.select_one(".q")
        if q:
            qn = q.select_one(".qn")
            if qn:
                qn.decompose()
            blocks.append({"kind": "subhead", "text": text_of(q), "nogap_before": True})
        ans = card.select_one(".ans")
        if ans:
            emit_answer(ans, blocks, fig_out, src.parent, state)

    missing = verify(soup, blocks)
    if missing:
        print(f"[{rel}] IMPORT ABORTED — {len(missing)} run(s) of source text lost:",
              file=sys.stderr)
        for m in missing[:12]:
            print(f"    · {m[:140]}", file=sys.stderr)
        return False

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "blocks.json").write_text(json.dumps(
        {"source": str(src), "figures_dir": str(fig_out),
         "src_chars": len(norm((soup.body or soup).get_text(" "))),
         "captured_chars": len(norm(captured_text(blocks))),
         "blocks": blocks}, ensure_ascii=False, indent=1), encoding="utf-8")

    kinds: dict[str, int] = {}
    for b in blocks:
        kinds[b["kind"]] = kinds.get(b["kind"], 0) + 1
    print(f"[{board}-{ch}] {len(blocks)} blocks  " +
          "  ".join(f"{k}={v}" for k, v in sorted(kinds.items())))
    return True


def main() -> int:
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 1
    rels = ([f"UP/Ch{n}" for n in range(1, 14)] if args[0] == "--all" else args)
    ok = all([run(r) for r in rels])
    print("[SUMMARY] " + ("all imported" if ok else "FAILURES — see above"))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
