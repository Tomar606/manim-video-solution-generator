#!/usr/bin/env python3
"""import_htmls.py — turn the Top-5 PYQ HTMLs into page-contents/*.md for the Hindi hand pipeline.

Source: top5_pyq_html/Class12/Biology_PYQs/Hindi/**/*_Top5_PYQ_Hindi.html
Each HTML is one board+chapter: a header (chapter name) plus five ".card" blocks, each holding
badges (rank / type / year(s) / marks / repeat count), a question, and an answer built from
<p>, <ul>/<ol>, <table> and <img> (figures are embedded as base64 data URIs).

What this produces, per source HTML with key <board>-ch<N> (e.g. mp-ch5, rj-ch4, ch3):
  figures/<key>-fig-NN.<ext>      every embedded figure, decoded to a real file
  page-contents/<key>-page-NN.md  theory pages in the <<TAG>> language of prompt-hindi.md
  page-contents/<key>-dia-NN.md   one diagram page per figure, placed after the page that
                                  carries the question the figure belongs to
  MANIFEST.md                     what was produced, in render order

Pagination is by ESTIMATED ROWS (Devanagari at our notes size fits roughly 56 characters per
row, a little less when indented under a bullet). A page takes ROWS_PER_PAGE rows; a <<SUBHEAD>>
is never left orphaned at the foot of a page.

Nothing here calls an API -- it only writes .md files. Render them with gen_hindi.py.

Usage:
  python import_htmls.py            # rebuild every page-content from the HTMLs
  python import_htmls.py --dry      # report the page split without writing files
"""
from __future__ import annotations

import base64
import html as htmlmod
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
# Top-5 PYQ HTML tree — see the note in mockup/import_pyq.py; TOP5_HTML_ROOT overrides it.
SRC = Path(os.environ.get(
    "TOP5_HTML_ROOT",
    HERE.parent.parent / "top5_pyq_html" / "Class12" / "Biology_PYQs" / "Hindi"))
FIG_DIR = HERE / "figures"
CONTENT_DIR = HERE / "page-contents"
MANIFEST = HERE / "MANIFEST.md"

ROWS_PER_PAGE = 30   # calibrated against the approved page-01: it estimates 30 rows and renders
                     # as a full 28-row sheet. A lower budget under-fills, and the model then
                     # stretches the row spacing to compensate, which breaks the target look.
CHARS_PER_ROW = 56        # plain <<TEXT>> row
CHARS_PER_POINT_ROW = 52  # <<POINT>> rows lose width to the bullet + hanging indent

# Page 1 also carries the <<TITLE>> line, which is added AFTER pagination and so used to cost
# nothing in the budget. On a chapter whose page 1 filled all 30 rows the renderer then had to
# find room for a 31st, and what it silently dropped was the title itself — the page came back
# with an empty top band. Reserve the title's row (plus the gap under it) up front instead.
TITLE_ROWS = 2

# ...but NOT for chapters already rendered and published under chapters/. Reserving the row
# reflows their page 1, which pushes content across every later page boundary, and their images
# are already shipped — the .md files would stop describing the pages on disk. Their page 1
# happened to be short enough to fit the title anyway, which is why the defect never showed there.
TITLE_ROWS_EXEMPT = {"mp-ch3", "mp-ch4", "mp-ch5", "rj-ch3", "rj-ch4", "rj-ch5"}

# page-01.md is the hand-tuned sample page; never clobber it.
KEEP = {"page-01"}

# Short Hindi captions for the six embedded figures. There are few enough to name properly, and
# a real caption ("द्विकुंडली डीएनए") beats anything derivable from the surrounding markup.
FIG_CAPTIONS = {
    "mp-ch4-fig-01": "हीमोफीलिया की वंशागति",
    "mp-ch4-fig-02": "द्विसंकर क्रॉस — पुनेट वर्ग (9 : 3 : 3 : 1)",
    "mp-ch5-fig-01": "द्विकुंडली डीएनए",
    "mp-ch5-fig-02": "हर्शे एवं चेज़ का प्रयोग",
    "rj-ch4-fig-01": "दात्र कोशिका अरक्तता — HbS",
    "rj-ch5-fig-01": "अनुलेखन इकाई",
    # Ch1 / Ch2 / Ch6 — captions written after looking at each extracted figure, not guessed
    # from the surrounding markup (the source order does not follow the question order).
    "mp-ch1-fig-01": "प्ररूपी आवृतबीजी बीजाण्ड",
    "mp-ch2-fig-01": "अण्डाशय की अनुप्रस्थ काट",
    "mp-ch2-fig-03": "अण्डाणु तथा उसके आवरण",
    "mp-ch2-fig-04": "शुक्राणु की संरचना",
    "mp-ch6-fig-01": "मिलर एवं यूरे का प्रयोग",
    "rj-ch1-fig-01": "बीजाण्ड (गुरुबीजाणुधानी) की संरचना",
    "rj-ch1-fig-02": "परिपक्व भ्रूणकोश — 7-कोशिकीय, 8-केन्द्रकीय",
    "rj-ch2-fig-01": "अण्डजनन (ऊजेनेसिस)",
    # UP board — captions written after looking at each extracted figure. Five of chapter 11's
    # six "figures" are equation snippets rather than drawings; they are KEPT rather than dropped
    # because the theory text defines जन्म-दर/मृत्यु-दर etc. but never states the formulae, so
    # dropping them would lose the maths from the booklet altogether.
    "up-ch1-fig-01": "परागकण का अंकुरण",
    "up-ch1-fig-02": "प्रारूपी आवृतबीजी बीजाण्ड",
    "up-ch1-fig-03": "परागकोश एवं लघुबीजाणुधानी की काट",
    "up-ch1-fig-04": "लघुबीजाणुजनन",
    "up-ch2-fig-01": "मानव मादा जनन तंत्र",
    "up-ch2-fig-02": "आर्तव चक्र",
    "up-ch2-fig-03": "शुक्राणुजनन एवं अण्डाणुजनन",
    "up-ch2-fig-04": "अण्डाशय की अनुप्रस्थ काट",
    "up-ch2-fig-05": "मानव नर जनन तंत्र",
    "up-ch4-fig-01": "पुनेट वर्ग (चैकर बोर्ड)",
    "up-ch4-fig-02": "मेण्डल का एकसंकर संकरण",
    "up-ch4-fig-03": "परीक्षार्थ संकरण (टेस्ट क्रॉस)",
    "up-ch5-fig-01": "हर्षे व चेज का प्रयोग",
    "up-ch5-fig-02": "डीएनए प्रतिकृतिकरण द्विशाख",
    "up-ch5-fig-03": "आरएनए की संरचना",
    "up-ch6-fig-01": "मिलर का प्रयोग",
    "up-ch7-fig-01": "मलेरिया परजीवी का जीवन-चक्र",
    "up-ch7-fig-02": "प्रतिरक्षी अणु की संरचना",
    "up-ch9-fig-01": "संवाहक pBR322",
    "up-ch9-fig-02": "पॉलीमरेज श्रृंखला अभिक्रिया (PCR)",
    "up-ch10-fig-01": "जीन चिकित्सा (ADA कमी) के चरण",
    # The five equation crops are transcribed to prose in make_up_booklets.py, so the growth-curve
    # graph — chapter 11's only real drawing — is now fig-01 rather than fig-04.
    "up-ch11-fig-01": "समष्टि वृद्धि वक्र",
    "up-ch12-fig-01": "अपघटन की प्रक्रिया",
    "up-ch12-fig-02": "पारितंत्र के पोषण स्तर",
}

# Some source figures are photographs of a textbook page taken sideways.
FIG_ROTATE = {"mp-ch4-fig-02": -90}   # degrees, PIL convention (negative = clockwise)

# Figures that get NO diagram page. A 4x4 Punnett square is text-in-cells, and the image model
# garbles the genotypes every time; the same square is already rendered correctly as a hand-ruled
# [[TABLE]] on mp-ch4-page-05, along with the parents, gametes, F1 and both F2 ratios in prose.
#
# mp-ch2-fig-02 is a MALE reproductive tract diagram carried on the question that asks for the
# FEMALE tract — a mismatch in the source pull, not something the renderer can fix. Drawing it
# would put a confidently-labelled wrong answer in the booklet.
DROP_FIGURES = {"mp-ch4-fig-02", "mp-ch2-fig-02"}

# Chapters whose LAST TWO pages should be evened out. Without this, a chapter can end with one
# over-full page followed by a short tail page; the model then shrinks the writing on the full page
# and enlarges it on the short one, so the letter height drifts off-spec in both directions.
BALANCE_TAIL = {"rj-ch5"}


# --------------------------------------------------------------------------- html helpers
def strip_tags(s: str) -> str:
    s = re.sub(r"<br\s*/?>", " ", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = htmlmod.unescape(s)
    return re.sub(r"\s+", " ", s).strip()


def board_key(path: Path) -> str:
    """mp-ch5 / rj-ch4 / ch3 from the file's location."""
    parts = [p.lower() for p in path.parts]
    ch = re.search(r"ch(\d+)", path.stem.lower())
    ch = f"ch{ch.group(1)}" if ch else "ch0"
    if "mp" in parts:
        return f"mp-{ch}"
    if "rajasthan" in parts:
        return f"rj-{ch}"
    if "up" in parts:
        return f"up-{ch}"
    return ch


def chapter_title(doc: str) -> str:
    """The Hindi chapter title from <div class="title">...<span class="hi">HINDI</span>."""
    m = re.search(r'<span class="hi">(.*?)</span>', doc, re.S)
    if m:
        return strip_tags(m.group(1))
    m = re.search(r'<div class="title">(.*?)</div>', doc, re.S)
    return strip_tags(m.group(1)) if m else "जीव विज्ञान"


# --------------------------------------------------------------------------- card parsing
def parse_cards(doc: str):
    """[{badges: {...}, q: str, blocks: [(kind, payload), ...]}] for each .card in order."""
    cards = []
    for chunk in re.findall(r'<div class="card">(.*?)</div>\s*(?=<div class="card">|</div>\s*<div class="foot"|$)',
                            doc, re.S):
        badges = {
            "rank": (re.search(r'tag-rank">(.*?)</span>', chunk) or [None, ""])[1],
            "type": (re.search(r'tag-type">(.*?)</span>', chunk) or [None, ""])[1],
            "years": re.findall(r'tag-year">(.*?)</span>', chunk),
            "marks": (re.search(r'tag-marks">(.*?)</span>', chunk) or [None, ""])[1],
            "rep": (re.search(r'tag-rep">(.*?)</span>', chunk) or [None, ""])[1],
        }
        qm = re.search(r'<div class="q">(.*?)</div>', chunk, re.S)
        q = strip_tags(re.sub(r'<span class="qn">.*?</span>', "", qm.group(1), flags=re.S)) if qm else ""
        am = re.search(r'<div class="ans">(.*?)$', chunk, re.S)
        cards.append({"badges": badges, "q": q,
                      "blocks": parse_answer(am.group(1) if am else "")})
    return cards


def parse_answer(ans: str):
    """Ordered blocks from an answer body: TEXT / POINT / TABLE / FIG.

    Figures are pulled out FIRST, before the block scan. Roughly half the source figures sit
    inside a <p> or an <li> rather than as a direct child of .ans, and the block regex below
    matches the enclosing <p>/<ul> as one unit — so an <img> nested in one used to be consumed
    with the text and silently lost, taking its whole diagram page with it. Position inside the
    card does not matter: card_lines() collects a card's figures separately and anchors them to
    the card's last line either way.
    """
    ans = re.sub(r'<span class="al">.*?</span>', "", ans, flags=re.S)
    figs = []
    for m in re.finditer(r"<img\b[^>]*>", ans, re.S):
        m2 = re.search(r"data:image/([a-z+]+);base64,([A-Za-z0-9+/=]+)", m.group(0))
        if m2:
            figs.append(("FIG", (m2.group(1), m2.group(2))))
    ans = re.sub(r"<img\b[^>]*>", "", ans, flags=re.S)
    blocks, pos = list(figs), 0
    pattern = re.compile(r"<(p|ul|ol|table|img)\b(.*?)(?:/>|>(.*?)</\1>)", re.S)
    for m in pattern.finditer(ans):
        tag, attrs, inner = m.group(1), m.group(2), m.group(3) or ""
        pos = m.end()
        if tag == "p":
            txt = strip_tags(inner)
            if txt:
                blocks.append(("TEXT", txt))
        elif tag in ("ul", "ol"):
            for li in re.findall(r"<li[^>]*>(.*?)</li>", inner, re.S):
                txt = strip_tags(li)
                if txt:
                    blocks.append(("POINT", txt))
        elif tag == "table":
            rows = []
            for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", inner, re.S):
                cells = [strip_tags(c) for c in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", tr, re.S)]
                if any(cells):
                    rows.append(cells)
            if rows:
                blocks.append(("TABLE", rows))
        elif tag == "img":
            m2 = re.search(r"data:image/([a-z+]+);base64,([A-Za-z0-9+/=]+)", attrs)
            if m2:
                blocks.append(("FIG", (m2.group(1), m2.group(2))))
    del pos
    return blocks


# --------------------------------------------------------------------------- layout
def rows_for(kind: str, payload) -> int:
    if kind == "SUBHEAD":
        return 1
    if kind in ("TEXT", "QUESTION"):
        return max(1, -(-len(payload) // CHARS_PER_ROW))
    if kind == "POINT":
        return max(1, -(-len(payload) // CHARS_PER_POINT_ROW))
    if kind == "TABLE":
        return len(payload) + 2          # ruled rows plus the border/heading allowance
    if kind == "BLANK":
        return 1
    return 1


def card_lines(card, idx):
    """A card -> the tagged lines it becomes.

    Figures are pulled out separately, and so is any "चित्र — ..." paragraph: that paragraph is
    the source's own brief for what the drawing must show, so it belongs on the DIAGRAM page as
    the drawing instruction, not in the middle of the theory prose.
    """
    b = card["badges"]
    meta = " · ".join(x for x in [b["type"], "/".join(b["years"]), b["marks"], b["rep"]] if x)
    lines = [("SUBHEAD", f"प्र.{idx}  [{meta}]" if meta else f"प्र.{idx}")]
    lines.append(("QUESTION", card["q"]))   # black ink; the answer below it stays blue
    figs, brief = [], ""
    first_text = True
    for kind, payload in card["blocks"]:
        if kind == "FIG":
            figs.append(payload)
            continue
        if kind == "TEXT" and re.match(r"^चित्र\s*[—:-]", payload):
            brief = re.sub(r"^चित्र\s*[—:-]\s*", "", payload)
            continue
        if kind == "TEXT" and first_text:
            payload, first_text = f"उत्तर : {payload}", False
        lines.append((kind, payload))
    return lines, [(ext, data, brief) for ext, data in figs]


def paginate(lines, key=""):
    """Greedy fill to ROWS_PER_PAGE, never orphaning a <<SUBHEAD>> at the foot of a page.

    Page 1 is budgeted TITLE_ROWS shorter, because the <<TITLE>> line is prepended to it later.
    """
    pages, cur, used = [], [], 0
    budget = ROWS_PER_PAGE - (0 if key in TITLE_ROWS_EXEMPT else TITLE_ROWS)
    for i, (kind, payload) in enumerate(lines):
        need = rows_for(kind, payload)
        # a heading needs itself plus the first two rows of what follows, or it moves on
        if kind == "SUBHEAD":
            look = sum(rows_for(k, p) for k, p in lines[i + 1:i + 2]) or 1
            need_here = need + min(2, look)
        else:
            need_here = need
        if cur and used + need_here > budget:
            pages.append(cur)
            cur, used = [], 0
            budget = ROWS_PER_PAGE
        cur.append((kind, payload))
        used += need
    if cur:
        pages.append(cur)
    return pages


def balance_tail(pages):
    """Even out the final two pages by shifting whole blocks from the fuller one to the shorter.

    Stops as soon as moving another block would make the imbalance worse, so both pages end up
    near the same row count and neither forces the renderer to squeeze or stretch its writing.
    """
    if len(pages) < 2:
        return pages
    a, b = pages[-2], pages[-1]

    def rows(pg):
        return sum(rows_for(k, p) for k, p in pg)

    while True:
        gap = abs(rows(a) - rows(b))
        best = None
        if len(a) > 1:                       # push the last block of A onto the front of B
            r = rows_for(*a[-1])
            cand = abs((rows(a) - r) - (rows(b) + r))
            if cand < gap:
                best = ("a2b", cand)
        if len(b) > 1:                       # pull the first block of B onto the end of A
            r = rows_for(*b[0])
            cand = abs((rows(a) + r) - (rows(b) - r))
            if best is None or cand < best[1]:
                if cand < gap:
                    best = ("b2a", cand)
        if best is None:
            break
        if best[0] == "a2b":
            a, b = a[:-1], [a[-1]] + b
        else:
            a, b = a + [b[0]], b[1:]
    pages[-2], pages[-1] = a, b
    return pages


def render_line(kind, payload) -> str:
    if kind == "TABLE":
        head, *body = payload
        rows = " ; ".join(" | ".join(r) for r in body)
        return (f"[[TABLE columns: {' | '.join(head)} :: rows: {rows}]]")
    if kind == "BLANK":
        return ""
    return f"<<{kind}>> {payload}"


# --------------------------------------------------------------------------- main
def main() -> int:
    dry = "--dry" in sys.argv
    FIG_DIR.mkdir(exist_ok=True)
    CONTENT_DIR.mkdir(exist_ok=True)

    if not dry:  # clear previously imported pages, keep the hand-tuned sample
        for p in CONTENT_DIR.glob("*.md"):
            if p.stem not in KEEP:
                p.unlink()

    manifest = ["# Imported pages (generated by import_htmls.py — do not hand-edit)", ""]
    total_pages = total_dia = 0

    for src in sorted(SRC.glob("**/*_Top5_PYQ_Hindi.html")):
        doc = src.read_text(encoding="utf-8")
        key = board_key(src)
        title = chapter_title(doc)
        cards = parse_cards(doc)
        if not cards:
            print(f"[{key}] WARN: no cards parsed from {src.name}", file=sys.stderr)
            continue

        # Build one flat tagged stream, remembering which page each figure should follow.
        stream, fig_after = [], []      # fig_after: (line_index, ext, b64, brief)
        for idx, card in enumerate(cards, 1):
            lines, figs = card_lines(card, idx)
            stream.extend(lines)
            for ext, data, brief in figs:
                fig_after.append((len(stream) - 1, ext, data, brief))
            stream.append(("BLANK", ""))

        pages = paginate(stream, key)
        if key in BALANCE_TAIL:
            pages = balance_tail(pages)

        # map each figure to the page index whose content ends at/after its anchor line
        bounds, run = [], 0
        for pg in pages:
            run += len(pg)
            bounds.append(run)
        fig_page = {}
        for n, (line_i, ext, data, brief) in enumerate(fig_after, 1):
            pidx = next((i for i, b in enumerate(bounds) if line_i < b), len(pages) - 1)
            fig_page.setdefault(pidx, []).append((n, ext, data, brief))

        manifest.append(f"## {key} — {title}  ({src.relative_to(SRC)})")
        out_order = []
        for pidx, pg in enumerate(pages, 1):
            page_id = f"{key}-page-{pidx:02d}"
            body = []
            if pidx == 1:
                body.append(f"<<TITLE>> {title}")
            body += [render_line(k, p) for k, p in pg]
            text = "\n".join(body).strip("\n") + "\n"
            if not dry:
                (CONTENT_DIR / f"{page_id}.md").write_text(text, encoding="utf-8")
            out_order.append(page_id)
            total_pages += 1

            for n, ext, data, brief in fig_page.get(pidx - 1, []):
                fext = "jpg" if ext == "jpeg" else ext
                stem = f"{key}-fig-{n:02d}"
                if stem in DROP_FIGURES:
                    print(f"[{key}] dropping diagram page for {stem} (covered in the theory text)")
                    continue
                fig_name = f"{stem}.{fext}"
                if not dry:
                    fp = FIG_DIR / fig_name
                    fp.write_bytes(base64.b64decode(data))
                    if stem in FIG_ROTATE:
                        from PIL import Image
                        with Image.open(fp) as im:
                            im.rotate(FIG_ROTATE[stem], expand=True).save(fp)
                caption = FIG_CAPTIONS.get(stem, title.split("—")[0].strip())
                dia = [f"[[DIAGRAM {fig_name}]]"]
                if brief:
                    dia.append(f"[[SHOW {brief}]]")
                dia.append(f"<<CAPTION>> चित्र : {caption}")
                dia_id = f"{key}-dia-{n:02d}"
                if not dry:
                    (CONTENT_DIR / f"{dia_id}.md").write_text("\n".join(dia) + "\n", encoding="utf-8")
                out_order.append(dia_id)
                total_dia += 1
        manifest.append("  " + " ".join(out_order))
        manifest.append("")
        print(f"[{key}] {len(pages)} theory page(s), {sum(len(v) for v in fig_page.values())} diagram page(s)"
              f"  — {title}")

    manifest.append(f"\nTOTAL: {total_pages} theory pages + {total_dia} diagram pages")
    if not dry:
        MANIFEST.write_text("\n".join(manifest), encoding="utf-8")
    print(f"\nTOTAL: {total_pages} theory pages + {total_dia} diagram pages"
          f"{' (dry run, nothing written)' if dry else ''}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
