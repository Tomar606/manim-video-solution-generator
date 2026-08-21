#!/usr/bin/env python3
"""Stage 1a — read a chapter HTML into tagged blocks, capturing EVERY word.

    import_notes.py Hindi/Ch7        one chapter
    import_notes.py --all            every chapter under pulled_rj_biology/Hindi/

Output: notes/<Lang>-<Ch>/blocks.json

WHY THIS IS A DOM WALK AND NOT A LIST OF PATTERNS
-------------------------------------------------
The first version matched an allow-list of element shapes (p, h1-h3, ul, table, div.box, div.fc,
img). Anything outside that list vanished silently: this source also carries body text in plain
<div>s, mind maps as <div class="cards"><div class="card">, figures as <figure class="dfig">, and
h4 headings. Half of Ch7's text — 29,873 of 59,999 characters — was dropped without a murmur, and
25 pages were rendered from the remainder before anyone noticed.

So the rule is inverted. Every element is walked; an element is either handled specially or, if it
has no block-level descendant, its whole text is emitted. An unknown tag can no longer disappear —
at worst it arrives as a plain paragraph.

AND THE IMPORT IS VERIFIED, NOT TRUSTED
---------------------------------------
verify() tokenises the source's visible text and the captured text and requires that EVERY source
token is present, in order. Any loss aborts the import with the missing runs printed. Rendering is
billed per page, so a silent gap must never reach the image model again.
"""
from __future__ import annotations

import difflib
import json
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString, Tag

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent.parent
SRC_ROOT = REPO / "pulled_rj_biology"
OUT_ROOT = HERE.parent / "notes"

HEADING_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6"}
BLOCK_TAGS = HEADING_TAGS | {"p", "li", "ul", "ol", "table", "div", "figure", "figcaption",
                             "blockquote", "section", "img", "tr", "td", "th"}
# Chapter-front matter that is web furniture, not notes: the "कक्षा 12 ... NCERT अध्याय N" strap
# and the "इस अध्याय में :" contents list. These are EXCLUDED from the page, but kept in
# blocks.json as kind="dropped" so the word gate still sees them -- nothing vanishes silently,
# it is declared.
DROP_PATTERNS = (
    re.compile(r"^कक्षा\s*12\s*जीव\s*विज्ञान"),
    re.compile(r"इस\s*अध्याय\s*में\s*:"),
    re.compile(r"अरिविहान\s*टॉपर\s*नोट्स"),
    re.compile(r"चित्र\s*हिंदी\s*NCERT\s*से"),
    re.compile(r"पुनरावृत्ति\s*हेतु\s*फ्लोचार्ट\s*जोड़े\s*गए"),
)

HEADING_MAX = 90
SENTENCE_END = ("।", ".", "?", "!")

# <sup>/<sub> folding lives in scripts_map.py, because preflight.py verifies the same
# mapping and must not have to import an HTML parser to do it.
from scripts_map import script_runs, scriptify   # noqa: E402


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.replace("\xa0", " ")).strip()


def text_of(el) -> str:
    return norm(el.get_text(" ") if isinstance(el, Tag) else str(el))


def has_direct(el: Tag, cls: str) -> bool:
    """True when a DIRECT child (or grandchild wrapper) carries this class."""
    for c in el.children:
        if not isinstance(c, Tag):
            continue
        if cls in (c.get("class") or []):
            return True
        for g in c.children:
            if isinstance(g, Tag) and cls in (g.get("class") or []):
                return True
    return False


def has_block_child(el: Tag) -> bool:
    return any(isinstance(c, Tag) and c.name in BLOCK_TAGS for c in el.descendants)


def looks_like_heading(t: str) -> bool:
    return len(t) <= HEADING_MAX and not t.rstrip().endswith(SENTENCE_END)


class Importer:
    def __init__(self):
        self.blocks: list[dict] = []
        self.seen_title = False

    def add(self, **kw):
        if kw.get("text") or kw.get("rows") or kw.get("steps") or kw.get("nodes") or kw.get("src"):
            self.blocks.append(kw)

    def emit_imgs(self, el: Tag):
        """Rescue images nested inside an element a handler is about to flatten to text."""
        for im in el.find_all("img"):
            if im.get("src"):
                self.add(kind="fig", src=im["src"], caption="")
            im.extract()

    # ---------------------------------------------------------------- special shapes
    def do_table(self, el: Tag):
        self.emit_imgs(el)
        rows = []
        for tr in el.find_all("tr"):
            cells = [text_of(c) for c in tr.find_all(["td", "th"])]
            if any(cells):
                rows.append(cells)
        self.add(kind="table", rows=rows)

    def do_flow(self, el: Tag):
        self.emit_imgs(el)
        steps = []
        for st in el.select(".step"):
            note = st.find("small")
            note_txt = text_of(note) if note else ""
            if note:
                note.extract()
            steps.append({"text": text_of(st), "note": note_txt})
        # keep the ACTUAL arrow glyphs -- vertical chains use down-arrows, not right-arrows
        arrows = [text_of(a) for a in el.select(".ar, .ardown") if text_of(a)]
        # a flow may carry SEVERAL captions; the first titles it, the rest are commentary that
        # must not be dropped (this is where an ELISA paragraph was being lost)
        caps = [text_of(c) for c in el.select(".fc-cap") if text_of(c)]
        self.add(kind="flow", steps=steps, arrows=arrows,
                 caption=caps[0] if caps else "", extra_caps=caps[1:])
        for extra in caps[1:]:
            self.add(kind="text", text=extra)

    def do_pairs(self, el: Tag):
        """<div class="pairs"> — a column of "A → B" rows, each in its own .pair wrapper.

        The .step boxes sit THREE levels below the .fc container, so the flow branch never saw
        them and every token was emitted as its own text block: the chain came out as one word
        per line with its caption stranded on the next page.
        """
        self.emit_imgs(el)
        steps = []
        for pr in el.select(".pair"):
            note = pr.find("small")
            note_txt = text_of(note) if note else ""
            if note:
                note.extract()
            parts = [text_of(s) for s in pr.select(".step") if text_of(s)]
            arrow = next((text_of(a) for a in pr.select(".ar, .ardown") if text_of(a)), "\u2192")
            if parts:
                steps.append({"text": f" {arrow} ".join(parts), "note": note_txt})
        # the caption lives on the .fc wrapper, one level up; take it here so it stays with the chart
        cap = el.parent.select_one(".fc-cap") if el.parent else None
        cap_txt = text_of(cap) if cap else ""
        if cap:
            cap.extract()
        self.add(kind="flow", steps=steps, arrows=[], caption=cap_txt, extra_caps=[], layout="pairs")

    def do_mindmap(self, el: Tag):
        self.emit_imgs(el)
        nodes = []
        for cd in el.select(".card"):
            note = cd.find("small")
            note_txt = text_of(note) if note else ""
            if note:
                note.extract()
            nodes.append({"text": text_of(cd), "note": note_txt})
        cap = el.select_one(".fc-cap") or (el.parent.select_one(".fc-cap") if el.parent else None)
        self.add(kind="mindmap", nodes=nodes, caption=text_of(cap) if cap else "")

    def do_box(self, el: Tag):
        self.emit_imgs(el)
        lab = el.select_one(".t")
        label_raw = text_of(lab) if lab else "ध्यान दें"
        label = label_raw.rstrip(":： ")
        if lab:
            lab.extract()
        self.add(kind="box", label=label, label_raw=label_raw, text=text_of(el))

    def do_figure(self, el: Tag):
        img = el.find("img")
        cap = el.find("figcaption")
        if img and img.get("src"):
            self.add(kind="fig", src=img["src"], caption=text_of(cap) if cap else "")
        elif cap:
            self.add(kind="text", text=text_of(cap))

    def do_heading(self, el: Tag):
        # some figures are wrapped in a heading tag (<h4><img>), which otherwise looks like an
        # empty heading and takes the image down with it
        self.emit_imgs(el)
        t = text_of(el)
        if not t:
            return
        if el.name == "h1" and not self.seen_title:
            self.seen_title = True
            self.add(kind="title", text=t)
        elif looks_like_heading(t):
            self.add(kind="subhead", text=t, level=int(el.name[1]))
        else:
            # a heading carrying a whole sentence is prose wearing a heading tag
            self.add(kind="point" if len(t) < 400 else "text", text=t)

    def do_para(self, el: Tag, kind="text"):
        # a <li> or <p> may hold ONLY an image; without this the element looks empty and both the
        # element and its figure are dropped
        self.emit_imgs(el)
        t = text_of(el)
        if not t:
            return
        num = re.match(r"^(\d+)[.)]\s+(.+)$", t)
        if kind == "text" and num and len(t) < 400:
            self.add(kind="point", text=num.group(2), num=int(num.group(1)))
        else:
            self.add(kind=kind, text=t)

    # ---------------------------------------------------------------- the walk
    def walk(self, el):
        for child in list(el.children):
            if isinstance(child, NavigableString):
                # loose text sitting directly inside a container still counts
                t = norm(str(child))
                if t:
                    self.add(kind="text", text=t)
                continue
            if not isinstance(child, Tag):
                continue
            if child.parent is None:
                continue   # a handler already consumed this element (e.g. do_pairs took the
                           # .fc-cap); the children list was snapshotted before that, so without
                           # this check the caption is emitted a SECOND time as loose prose
            name, classes = child.name, set(child.get("class") or [])

            if name in ("script", "style"):
                continue
            if name == "table":
                self.do_table(child)
            elif name == "figure":
                self.do_figure(child)
            elif name == "img":
                if child.get("src"):
                    self.add(kind="fig", src=child["src"], caption="")
            elif name in HEADING_TAGS:
                self.do_heading(child)
            elif name in ("ul", "ol"):
                for li in child.find_all("li", recursive=False) or child.find_all("li"):
                    self.do_para(li, kind="point")
            elif name == "li":
                self.do_para(child, kind="point")
            elif name == "figcaption":
                self.do_para(child)
            elif "cards" in classes or has_direct(child, "card"):
                # A mind map may be wrapped as <div class="fc"><div class="cards">, so cards must
                # win over the flowchart branch -- routed to do_flow it finds no .step and the
                # whole map vanishes (exactly how Ch7's mind map was lost). Test DIRECT children
                # only: ".card anywhere below" matches the page container and swallows the lot.
                self.do_mindmap(child)
            elif "pairs" in classes:
                self.do_pairs(child)
            elif "fc" in classes or "chain" in classes:
                if has_direct(child, "step"):
                    self.do_flow(child)
                else:
                    self.walk(child)             # unknown inner shape: keep descending
            elif "box" in classes:
                self.do_box(child)
            elif name in ("p", "blockquote"):
                self.do_para(child)
            elif has_block_child(child):
                self.walk(child)                 # a container: keep descending
            else:
                self.do_para(child)              # a leaf of unknown shape: keep its text


# --------------------------------------------------------------------------- verification
def captured_text(blocks) -> str:
    out = []
    for b in blocks:
        if b["kind"] == "table":
            out += [c for r in b["rows"] for c in r]
        elif b["kind"] == "flow":
            arrows = list(b.get("arrows") or [])
            for i, s in enumerate(b["steps"]):
                if i and arrows:
                    out.append(arrows.pop(0))            # the glyph actually drawn between steps
                out += [s["text"], s["note"]]
            out += arrows + [b.get("caption", "")]
            # extra_caps are emitted separately as text blocks; not counted twice here
        elif b["kind"] == "mindmap":
            out += [n["text"] + " " + n["note"] for n in b["nodes"]] + [b.get("caption", "")]
        elif b["kind"] == "box":
            out += [b.get("label_raw", b["label"]), b["text"]]
        elif b["kind"] == "fig":
            out.append(b.get("caption", ""))
        else:
            if b.get("num"):
                out.append(f"{b['num']}.")           # the marker precedes its text in the source
            out.append(b.get("text", ""))
    return " ".join(out)


def verify(soup: BeautifulSoup, blocks) -> list[str]:
    """Return the runs of source text that never made it into a block. Empty = nothing lost."""
    for bad in soup(["script", "style"]):
        bad.decompose()
    body = soup.body or soup                      # <head><title> is not page content
    src_tokens = norm(body.get_text(" ")).split()
    got_tokens = norm(captured_text(blocks)).split()
    sm = difflib.SequenceMatcher(None, src_tokens, got_tokens, autojunk=False)
    missing = []
    for tag, i1, i2, _, _ in sm.get_opcodes():
        if tag in ("delete", "replace"):
            missing.append(" ".join(src_tokens[i1:i2]))
    return [m for m in missing if m.strip()]


def run(rel: str) -> bool:
    src_dir = SRC_ROOT / rel
    html_file = next(src_dir.glob("*.html"), None)
    if not html_file:
        print(f"ERROR: no html under {src_dir}", file=sys.stderr)
        return False

    source = html_file.read_text(encoding="utf-8")

    # A <sup>/<sub> Unicode cannot express would otherwise pass through flattened -- "I A" for
    # I^A -- and only be noticed on a drawn page. Nothing silently degrades: stop here instead.
    unmappable = [(k, b) for k, b, conv in script_runs(source) if conv is None]
    if unmappable:
        print(f"  ✗ ABORTED — {len(unmappable)} <sup>/<sub> run(s) have no Unicode form; they "
              f"would be written flattened:", file=sys.stderr)
        for k, b in unmappable[:12]:
            print(f"      <{k}>{b}</{k}>", file=sys.stderr)
        print("      Extend SUP_MAP/SUB_MAP, or rewrite the run in the source HTML.",
              file=sys.stderr)
        return False

    raw = scriptify(source)
    imp = Importer()
    imp.walk(BeautifulSoup(raw, "lxml").body or BeautifulSoup(raw, "lxml"))
    blocks = imp.blocks

    for b in blocks:
        if b.get("text") and any(p.search(b["text"]) for p in DROP_PATTERNS):
            b["kind"], b["why"] = "dropped", "chapter intro / contents list"

    lost = verify(BeautifulSoup(raw, "lxml"), blocks)
    src_imgs = [i["src"] for i in BeautifulSoup(raw, "lxml").find_all("img") if i.get("src")]
    got_imgs = [b["src"] for b in blocks if b["kind"] == "fig"]
    missing_imgs = [s for s in src_imgs if s not in got_imgs]
    _s = BeautifulSoup(raw, "lxml")
    src_chars = len(norm((_s.body or _s).get_text(" ")))
    got_chars = len(norm(captured_text(blocks)))

    kinds = {}
    for b in blocks:
        kinds[b["kind"]] = kinds.get(b["kind"], 0) + 1
    print(f"{rel}: {len(blocks)} blocks  {got_chars:,}/{src_chars:,} chars  "
          + " ".join(f"{k}={v}" for k, v in sorted(kinds.items()))
          + f"  imgs {len(got_imgs)}/{len(src_imgs)}")

    if missing_imgs:
        print(f"  \u2717 ABORTED \u2014 {len(missing_imgs)} figure(s) in the source never reached a "
              f"block:", file=sys.stderr)
        for m in missing_imgs:
            print(f"      {m}", file=sys.stderr)
        return False
    if lost:
        print(f"  ✗ ABORTED — {len(lost)} run(s) of source text were not captured:", file=sys.stderr)
        for m in lost[:12]:
            print(f"      {m[:110]}", file=sys.stderr)
        return False

    out = OUT_ROOT / rel.replace("/", "-")
    out.mkdir(parents=True, exist_ok=True)
    (out / "blocks.json").write_text(json.dumps(
        {"source": str(html_file.relative_to(REPO)), "figures_dir": str(src_dir / "figures"),
         "src_chars": src_chars, "captured_chars": got_chars, "blocks": blocks},
        ensure_ascii=False, indent=1), encoding="utf-8")
    print("  ✓ every word captured")
    return True


def main() -> int:
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 1
    rels = ([f"Hindi/{p.name}" for p in sorted((SRC_ROOT / "Hindi").iterdir()) if p.is_dir()]
            if args[0] == "--all" else [a.strip("/") for a in args])
    ok = [run(r) for r in rels]
    print(f"\n{sum(ok)}/{len(ok)} chapters imported cleanly")
    return 0 if all(ok) else 1


if __name__ == "__main__":
    raise SystemExit(main())
