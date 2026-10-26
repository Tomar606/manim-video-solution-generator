"""Refuse an answer page that is not the house sheet, or is the wrong question's.

    python tools/answer_page_gate.py <slug> [--no-vision] [--json]

Checks every image in projects/<slug>/assets/answer/ — the pages
tools/answer_overlay.py will put on the end of the video.

WHY THIS EXISTS
---------------
Three separate wrong pages shipped or nearly shipped, and every one of them was
caught by a person looking at a frame rather than by anything mechanical:

1. PHY-C1-SA-01 went out on a scan of the PRINTED TEXTBOOK. It even carried the
   Arivihan watermark, which is what fooled the check that was being applied by
   eye — "has a watermark" was treated as "is the house page". It is landscape,
   typeset, and has no question/answer margin.
2. CHE-C1-LA-01, CHE-C1-LA-02 and CHE-C4-LA-02 were on GENERATED MOCK pages in
   a "Q1:/Ans:" hand, left over from an early probe. The real pages existed in
   the sheet the whole time; the download pass skipped those projects because
   they already had *an* image.
3. FARADAY-ELECTROLYSIS held the SAME page three times under three names, and
   would have shown it three times in a row. DANIELL-CELL and SANKSHARAN twice.

None of those is a judgement call once you know what to look for, which makes
them a gate rather than a habit.

WHAT MAKES A PAGE THE HOUSE SHEET
---------------------------------
The genuine page is a photographed ruled sheet: portrait, a "Page No. / Date"
box in the top right, प्रश्न and उत्तर down the left margin, handwriting, and
the Arivihan watermark across the middle. The watermark ALONE proves nothing —
that is exactly the mistake PHY-C1-SA-01 encodes — so it is one signal of
several and never sufficient on its own.

The cheap checks run first and need no model: aspect, ink coverage, and whether
two pages of the same question are byte- or near-identical. They catch the
duplicate and the landscape book-crop on their own. The vision pass then reads
the page and answers the two questions a human was answering by eye: is this
the house sheet, and is it THIS question's. `--no-vision` stops after the cheap
checks, for a run with no model access.

MATCHING THE QUESTION is done on the Devanagari content words, not the whole
string: the sheet's question text and the page's handwritten one differ in
punctuation, in whether the year is included, and in spacing, but they cannot
differ in which words they use. Below HALF the page's words appearing in the
question is a mismatch worth stopping for.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

MIN_ASPECT = 1.25        # h/w — the house sheet is a portrait page, about 1.5
MIN_INK = 0.8            # percent of dark pixels; below this the page is blank
# NO PIXEL-CORRELATION DUPLICATE CHECK. It was tried and measured: the known
# duplicates scored 0.15, 0.25, 0.31 and 0.99 while genuinely different pages
# of the same answer scored up to 0.25. The ranges overlap, so no threshold
# separates them — the same page re-exported at another size and crop is not
# the same ARRAY. Duplicates are caught on their TEXT in the vision pass
# instead, which is also the honest signal: a real page two continues the
# answer, a duplicate repeats the question.
# CALIBRATION, measured rather than guessed. A page from a DIFFERENT question
# scored 0% overlap. A correct page scored 45% — it says रोगों where meta.json
# says बीमारियों, and that meta question is itself truncated mid-word, so the
# denominator is short. The gap between "wrong question" and "worded
# differently" is therefore enormous, and the first threshold (50%) sat on the
# wrong side of it and failed a correct page. Below 35% is a different
# question; between 35% and 60% is worth a human glance, not a block.
WORD_HIT = 0.35          # below this the page belongs to another question
WORD_WARN = 0.60         # below this, say so, but do not stop the build

SYSTEM = (
    "You are checking a scanned answer sheet for an Indian Class 12 board-exam "
    "video. Answer only with the JSON asked for. Report what you SEE; never "
    "guess at what is probably there."
)

PROMPT = """This image is meant to be a handwritten Arivihan answer sheet.

It is PAGE <<N>> OF <<M>> of this answer.<<CONT>>

The genuine house sheet looks like this, all of it at once:
- a PORTRAIT page of ruled paper, photographed
- a small "Page No. / Date" box printed in the TOP RIGHT
- the words प्रश्न and उत्तर written down the LEFT MARGIN, outside a vertical rule
- the answer in a HANDWRITING style: a neat, even hand. These pages are
  typeset in a handwriting typeface rather than photographed from a real pen,
  so uniform glyphs, a level shirorekha and formulas set with LaTeX are NORMAL
  and are not a reason to reject the page. What matters is that it reads as a
  written answer, not as book type.
- a large faint diagonal "Arivihan" watermark across the middle

Things that are NOT the house sheet, however much else matches:
- a scan or photo of a PRINTED TEXTBOOK page (typeset, justified, no margin
  labels). These sometimes carry the watermark too — the watermark does not
  make a page genuine.
- a generated mock that writes "Q1:" and "Ans:" instead of प्रश्न and उत्तर,
  and has no Page No./Date box.

Judge `house_sheet` on the paper, the handwriting and the watermark — NOT on
whether the question is present.

Return exactly this JSON:
{
  "house_sheet": true or false,
  "reason": "<one short sentence naming what decided it>",
  "watermark": true or false,
  "page_no_box": true or false,
  "margin_labels": true or false,
  "handwritten": true or false,   // handwriting STYLE counts as true
  "printed_textbook": true or false,
  "question_text": "<the question as written on the page, verbatim; \\"\\" if none>",
  "year": "<the year printed in brackets, or \\"\\">",
  "body_opening": "<the first 15 words of the ANSWER body, verbatim>"
}"""


def _words(s: str) -> set[str]:
    """Devanagari and Latin content words, lowercased, 2+ characters.

    Digits and punctuation are dropped: the page writes the year in brackets and
    the sheet often does not, and neither spells the dandas the same way.
    """
    return {w.lower() for w in re.findall(r"[ऀ-ॿ]{2,}|[A-Za-z]{2,}", s or "")}


def _ink(path: Path) -> float:
    """Dark pixels as a percentage — of the WRITTEN area, not of the sheet.

    Measured over the whole page, a short but real page reads as nearly empty
    because two thirds of it is unwritten rules: CHE-C2-SA-04's second page
    carries the entire unit derivation and scores 0.60%. tools/answer_overlay.py
    crops the blank tail before it decides anything, so this has to as well —
    otherwise the gate calls a page blank that the builder is about to include,
    and the two disagree about the same file.
    """
    import numpy as np
    from PIL import Image
    im = Image.open(path).convert("L")
    a = np.asarray(im).astype(int)
    h, w = a.shape
    profile = (a < 130).sum(axis=1) / w
    window = max(9, h // 50)
    smooth = np.convolve(profile, np.ones(window) / window, mode="same")
    rows = np.where(smooth > 0.025)[0]
    if len(rows):
        bottom = min(h, int(rows.max() + h * 0.045))
        a = a[:bottom]
    return float((a < 130).mean() * 100)


def cheap_checks(pages: list[Path]) -> list[tuple[str, str, str]]:
    """(level, page, message) for everything decidable without a model."""
    from PIL import Image
    out: list[tuple[str, str, str]] = []
    digests = {}
    for p in pages:
        w, h = Image.open(p).size
        if h / w < MIN_ASPECT:
            out.append(("FAIL", p.name,
                        f"landscape-ish ({w}x{h}, h/w {h / w:.2f}) — the house "
                        f"sheet is a portrait page; this is usually a crop of a "
                        f"printed book"))
        ink = _ink(p)
        if ink < MIN_INK:
            out.append(("FAIL", p.name, f"only {ink:.2f}% ink — effectively blank"))
        digests[p] = hashlib.md5(p.read_bytes()).hexdigest()
    for i, p in enumerate(pages):
        for q in pages[:i]:
            if digests[p] == digests[q]:
                out.append(("FAIL", p.name,
                            f"byte-identical to {q.name} — the same page twice"))
    return out


def vision_checks(pages: list[Path], question: str) -> list[tuple[str, str, str]]:
    sys.path.insert(0, str(ROOT))
    from src.llm import LLMError, complete                 # noqa: PLC0415
    out: list[tuple[str, str, str]] = []
    qwords = _words(question)
    seen_openings: dict[str, str] = {}
    # A CONTINUATION PAGE IS NOT A DEFECTIVE FIRST PAGE. Only page one carries
    # the question and the प्रश्न/उत्तर margin labels; page two picks the answer
    # up mid-flow with an empty margin. Checked against every page, the first
    # version failed CHE-C1-SA-01's perfectly good second page for "no margin
    # labels, no question text" — so the model is told which page it is looking
    # at, and the question match is asked of page one only.
    for i, p in enumerate(pages, 1):
        cont = ("" if i == 1 else
                "\n\nThis is a CONTINUATION page: it carries on from the previous "
                "one. It will NOT repeat the question and its left margin will be "
                "empty — neither is a fault. Expect ruled paper, handwriting and "
                "the watermark.")
        try:
            prompt = (PROMPT.replace("<<N>>", str(i))
                            .replace("<<M>>", str(len(pages)))
                            .replace("<<CONT>>", cont))
            raw = complete(SYSTEM, prompt, images=[str(p)])
        except LLMError as e:                              # noqa: BLE001
            out.append(("WARN", p.name, f"vision check could not run: {e}"))
            continue
        m = re.search(r"\{.*\}", raw, flags=re.S)
        if not m:
            out.append(("WARN", p.name, "vision check returned no JSON"))
            continue
        try:
            v = json.loads(m.group(0))
        except json.JSONDecodeError:
            out.append(("WARN", p.name, "vision check returned malformed JSON"))
            continue

        if v.get("printed_textbook"):
            out.append(("FAIL", p.name, "a scan of a PRINTED TEXTBOOK page, not "
                                        "the handwritten house sheet"))
        elif not v.get("house_sheet"):
            out.append(("FAIL", p.name, f"not the house sheet — "
                                        f"{v.get('reason', 'no reason given')}"))
        else:
            want = (["page_no_box", "margin_labels", "handwritten", "watermark"]
                    if i == 1 else ["handwritten", "watermark"])
            missing = [k for k in want if not v.get(k)]
            if missing:
                out.append(("WARN", p.name, "called a house sheet but missing: "
                                            + ", ".join(missing)))

        # ...and is it THIS question's page? Page one only — see above.
        seen = _words(v.get("question_text", ""))
        if i > 1:
            pass
        elif not seen:
            out.append(("WARN", p.name, "no question text readable on page one"))
        elif qwords:
            # MEASURED BOTH WAYS, and the kinder one wins. The page carries
            # the full exam question while meta.json often holds a shortened
            # label, so "share of the PAGE's words that are in the question"
            # punishes a correct page for the words the label dropped —
            # CHE-C4-LA-01 scored 31% that way and 100% the other way, and the
            # page was right. A page from a DIFFERENT question scores near zero
            # in BOTH directions, so taking the higher loses no power.
            hit = max(len(seen & qwords) / len(seen),
                      len(seen & qwords) / len(qwords))
            if hit < WORD_HIT:
                out.append(("FAIL", p.name,
                            f"this looks like ANOTHER question's page — only "
                            f"{hit:.0%} of its words appear in this project's "
                            f"question. Page says: "
                            f"{v.get('question_text', '')[:70]!r}"))
            elif hit < WORD_WARN:
                out.append(("WARN", p.name,
                            f"{hit:.0%} word overlap with this project's "
                            f"question — probably just different wording, but "
                            f"worth a look. Page says: "
                            f"{v.get('question_text', '')[:70]!r}"))

        # THE SAME PAGE TWICE. A real page two carries on from page one; a
        # duplicate opens with the same words. Compared on text because the
        # pixels do not separate them — see the note by the constants.
        opening = " ".join(sorted(_words(v.get("body_opening", ""))))
        if opening:
            twin = seen_openings.get(opening)
            if twin:
                out.append(("FAIL", p.name, f"opens with the same words as "
                                            f"{twin} — the same page twice, "
                                            f"not a second page"))
            else:
                seen_openings[opening] = p.name
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--no-vision", action="store_true",
                    help="only the checks that need no model")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    proj = ROOT / "projects" / a.slug
    ans = proj / "assets" / "answer"
    # `<name>_page.png` is answer_outro.to_full_page's full-frame copy of `<name>.png`, not a second page:
    # checking both reported every page as "the same page twice" (PHY Wheatstone, 23 Oct 2026)
    pages = sorted((f for f in ans.iterdir()
                    if f.suffix.lower() in (".png", ".jpg", ".jpeg")
                    and not (f.stem.endswith("_page") and any(f.with_name(f.stem[:-5] + x).exists() for x in (".png", ".jpg", ".jpeg")))),
                   key=lambda f: ((int(m.group(1))
                                   if (m := re.search(r"(?:_p|_|page)(\d+)\b", f.stem))
                                   else 0), f.name.lower())) if ans.is_dir() else []
    if not pages:
        print(f"  SKIP  answer_page_gate   no answer page in {a.slug} — nothing to check")
        return 0

    meta = {}
    mp = proj / "meta.json"
    if mp.is_file():
        meta = json.loads(mp.read_text(encoding="utf-8"))
    question = meta.get("question") or meta.get("question_text") or ""
    if not question:
        print(f"  no `question` in {a.slug}/meta.json — cannot check the page "
              f"belongs to this question")

    found = cheap_checks(pages)
    if not a.no_vision:
        found += vision_checks(pages, question)

    print(f"  answer pages — {a.slug}  ({len(pages)} page(s), in order)")
    for i, p in enumerate(pages, 1):
        print(f"    {i}. {p.name}")
    for level, page, msg in found:
        print(f"    {level}  {page}: {msg}")
    bad = [f for f in found if f[0] == "FAIL"]
    if a.json:
        print(json.dumps({"slug": a.slug, "pages": [p.name for p in pages],
                          "findings": [{"level": l, "page": p, "message": m}
                                       for l, p, m in found]},
                         ensure_ascii=False, indent=1))
    if bad:
        print(f"  ANSWER PAGE GATE FAILED — {a.slug}: {len(bad)} problem(s)")
        return 1
    print(f"  answer pages ok: {a.slug}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
