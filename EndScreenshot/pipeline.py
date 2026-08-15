"""The EndScreenshot flow, in three stages.

    S1  INPUT     a question + answer arrives as text, or as a screenshot of a
                  textbook page. A diagram may be supplied, linked inside the
                  text, or wanted but absent. Everything for this Q&A lands in
                  one folder under out/, named after the topic.
    S2  REVIEW    the answer is read and corrected before anything is drawn
                  (see review.py), and the figure is resolved to a local file.
                  This stage exists because every later stage renders VERBATIM:
                  an OCR-mangled conjunct or a stray paragraph from another
                  question would be faithfully hand-written onto the page.
    S3  DRAW      the temp is typeset (free) and shown for approval; only once
                  approved is the page drawn, and then watermarked.

The approval gate in S3 is the point of the whole shape: the temp costs
nothing, so the layout, wording and figure placement are all settled before a
single image is paid for.


Inside S3, the drawing itself is two passes — the shape notes-editor rebuilt
its own pipeline around:

    STEP 1 — TEMP        the question and answer are TYPESET onto a copy of the
                         real ruled sheet, in Python. No API call, instant and
                         free. This is the "typed version" you look at to check
                         the layout and fix the wording before spending
                         anything.
    STEP 2 — MAIN PHOTO  the temp is handed to the image model as IMAGE 3 — a
                         BLUEPRINT — and it re-writes that exact layout by hand.

Why it is built this way (notes-editor's HANDOFF.md records the history): the
old route described the layout to the model in prose — "write about 24 rows,
spread it to the bottom" — and paid an image every time the guess was wrong.
Pages came back with blank bottoms, crammed rows and floating text. Showing the
model a picture of the finished layout removed the guesswork and cut cost from
~25 images per chapter to one image per page.

The temp also makes pagination exact: rows are MEASURED by wrapping in the real
font rather than estimated from a words-per-row constant.
"""
from __future__ import annotations

import re
from pathlib import Path

from . import prompts
from .api import (EndScreenshotError, edit_image, fit_page, model_name,
                  quality_name)
from .layout import normalize_lines, tag_content
from .typeset import build_mockup

MAX_PAGES = 8


def build_prompt(content: str, page_no: int, total: int, *,
                 fill_note: str = "", highlight: bool = False,
                 extra_rules: str = "") -> str:
    """Fill the master prompt's placeholders for one page."""
    prompt = (prompts.MASTER_PROMPT
              .replace("{PAGE_NO}", str(page_no))
              .replace("{TOTAL}", str(total))
              .replace("{FILL_NOTE}", fill_note.strip()
                       or prompts.MOCKUP_FILL_NOTE)
              .replace("{CONTENT}",
                       "-----BEGIN CONTENT-----\n" + content.strip()
                       + "\n-----END CONTENT-----")
              .replace("{HIGHLIGHT_RULES}",
                       prompts.HIGHLIGHT_ON if highlight
                       else prompts.HIGHLIGHT_OFF))
    if extra_rules.strip():
        prompt += ("\n\nJOB-SPECIFIC OVERRIDES (these outrank every rule "
                   "above where they conflict):\n" + extra_rules.strip())
    return prompt


def draw_from_mockup(base, style, mockup, content: str, page_no: int,
                     total: int, *, highlight: bool = False,
                     extra_rules: str = "", anchor=None,
                     quality: str | None = None):
    """STEP 2, one page.

    IMAGE 1 = the blank ruled sheet (what gets written on)
    IMAGE 2 = the handwriting sample (whose hand to use)
    IMAGE 3 = the typeset temp of this very page (what goes where)
    IMAGE 4 = an already-drawn page of this run, so a multi-page answer stays
              in one hand (optional)
    """
    rules = prompts.MOCKUP_LAYOUT
    if extra_rules.strip():
        rules += "\n" + extra_rules.strip()
    # Restated LAST: a long trailing block (the diagram spec) otherwise
    # outweighs the head-line rule and the writing drifts to mid-gap.
    rules += "\n" + prompts.FINAL_BASELINE_REMINDER
    prompt = build_prompt(content, page_no, total,
                          fill_note=prompts.MOCKUP_FILL_NOTE,
                          highlight=highlight, extra_rules=rules)

    images = [fit_page(base), fit_page(style), fit_page(mockup)]
    if anchor is not None:
        images.append(fit_page(anchor))
        prompt += prompts.MOCKUP_ANCHOR_NOTE
    return edit_image(images, prompt, quality=quality)


def slugify_topic(topic: str) -> str:
    """Folder name for a Q&A. Keeps it readable — spaces and case survive,
    only characters a filesystem dislikes are stripped."""
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "", (topic or "").strip())
    name = re.sub(r"\s+", " ", name).strip(" .")
    return name[:80] or "Untitled"


def pascal_name(topic: str) -> str:
    """"Berkeley and Hartley" -> "BerkeleyAndHartley" — the delivered file."""
    words = re.findall(r"[A-Za-z0-9]+", topic or "")
    return "".join(w[:1].upper() + w[1:] for w in words) or "EndScreenshot"


def generate(question: str, answer: str, *,
             sheet: str | Path, style: str | Path,
             out_dir: str | Path, topic: str = "", stem: str = "answer",
             temp_dir: str | Path | None = None,
             question_label: str = "Q1", heading: str = "",
             highlight: bool = False, extra_rules: str = "",
             diagram_rules: str = "",
             quality: str | None = None, max_pages: int = MAX_PAGES,
             temp_only: bool = True, chain: bool = True, diagram=None,
             watermark_path: str | Path | None = None,
             watermark_scale: float = 0.56, watermark_opacity: float = 2.5,
             log=None) -> dict:
    """Question + answer -> hand-written page image(s), in two steps."""
    from PIL import Image

    log = log or (lambda msg: None)
    # Each Q&A gets its own folder named after the topic, holding the temp and
    # the finished page together — so a generation is one self-contained unit
    # you can look at, hand over, or delete.
    folder = slugify_topic(topic or stem)
    out_dir = Path(out_dir) / folder
    out_dir.mkdir(parents=True, exist_ok=True)
    temp_dir = Path(temp_dir) if temp_dir else out_dir
    log(f"folder    {out_dir}")

    # -- STEP 1: typeset the temp (free) ----------------------------------- #
    log("step 1/2  temp — typesetting the mock-up (no API call)")
    lines = normalize_lines(tag_content(question, answer,
                                        question_label=question_label,
                                        heading=heading))
    temp = build_mockup(lines, sheet, temp_dir, stem="temp", diagram=diagram,
                        log=lambda m: log("          " + m))
    plans, mockups = temp["plans"][:max_pages], temp["pages"][:max_pages]
    base = Image.open(temp["base"]).convert("RGB")

    if temp_only:
        # The gate: the temp is free, so it is always produced first and shown
        # for review. Nothing is spent until someone has looked at it.
        return {"pages": [], "temps": mockups, "plans": plans,
                "base": temp["base"], "images_generated": 0,
                "geometry": temp["geometry"], "folder": out_dir,
                "awaiting_approval": True}

    # -- STEP 2: draw each page from its temp ------------------------------ #
    style_img = Image.open(style).convert("RGB")
    written: list[Path] = []
    anchor = None
    for i, (plan, mock) in enumerate(zip(plans, mockups)):
        log(f"step 2/2  main photo — page {i + 1} of {len(plans)} "
            f"({model_name()}, {quality_name(quality)})")
        # The diagram spec goes ONLY to the page that carries the ghost
        # figure. Sent to every page, the model drew the (absent) figure on
        # page 2 as well — inventing an apparatus from the spec's label text.
        rules_i = extra_rules
        if diagram is not None and diagram_rules.strip():
            if i == 0:
                rules_i = (extra_rules + "\n" + diagram_rules).strip()
            else:
                rules_i = (extra_rules + "\nTHIS PAGE HAS NO FIGURE: "
                           "IMAGE 3 shows no faint diagram on this page. "
                           "Draw NO diagram, chart or apparatus here — only "
                           "the written content.").strip()
        img = draw_from_mockup(base, style_img,
                               Image.open(mock).convert("RGB"),
                               plan, i + 1, len(plans),
                               highlight=highlight, extra_rules=rules_i,
                               anchor=anchor, quality=quality)
        stem_out = pascal_name(topic or stem)
        # The un-watermarked master is ALWAYS kept: re-stamping at a different
        # size or opacity is free, but only if the clean page still exists.
        raw = out_dir / (f"{stem_out}_raw.png" if len(plans) == 1
                         else f"{stem_out}_{i + 1}_raw.png")
        img.save(raw)

        # STEP 3: the watermark goes on every page, centred.
        if watermark_path:
            from . import watermark as _wm
            img = _wm.apply(img, watermark_path, scale=watermark_scale,
                            opacity=watermark_opacity)
        name = (f"{stem_out}.png" if len(plans) == 1
                else f"{stem_out}_{i + 1}.png")
        dest = out_dir / name
        img.save(dest)
        written.append(dest)
        if chain:
            anchor = img

    return {"pages": written, "temps": mockups, "plans": plans,
            "base": temp["base"], "images_generated": len(written),
            "geometry": temp["geometry"], "folder": out_dir,
            "awaiting_approval": False}


def dry_run(question: str, answer: str, *, sheet: str | Path,
            question_label: str = "Q1", heading: str = "",
            out_dir: str | Path = "EndScreenshot/out/temp") -> dict:
    """Typeset the temp only — the free preview of what step 2 will draw."""
    lines = normalize_lines(tag_content(question, answer,
                                        question_label=question_label,
                                        heading=heading))
    temp = build_mockup(lines, sheet, out_dir, stem="dryrun")
    geo = temp["geometry"]
    return {"lines": lines, "pages": temp["pages"], "plans": temp["plans"],
            "rows": temp["rows"], "usable_rows": geo.usable,
            "ruled_rows": len(geo.rule_ys)}


# --------------------------------------------------------------------------- #
# S1 + S2 + S3 in one call                                                     #
# --------------------------------------------------------------------------- #
def run(*, question: str = "", answer: str = "", screenshot: str | Path = "",
        topic: str = "", diagram: str | None = None, want_diagram: bool = False,
        sheet: str | Path | None = None, style: str | Path | None = None,
        out_root: str | Path | None = None, approve: bool = False,
        review: bool = True, question_label: str = "Q1",
        watermark_path: str | Path | None = None,
        watermark_scale: float = 0.68, watermark_opacity: float = 3.0,
        diagram_row: int = 2, diagram_width: float = 0.44,
        quality: str | None = None, provider: str | None = None,
        log=None) -> dict:
    """Drive S1 -> S2 -> S3.

    Without ``approve`` this stops after the temp and returns
    ``awaiting_approval``. Re-run with ``approve=True`` to draw and watermark.
    """
    from . import DEFAULT_OUT, DEFAULT_SHEET, DEFAULT_STYLE, prompts
    from .review import extract_qa, resolve_diagram, review_answer
    from .typeset import Diagram

    log = log or (lambda m: None)
    sheet = sheet or DEFAULT_SHEET
    style = style or DEFAULT_STYLE
    out_root = Path(out_root or DEFAULT_OUT)

    # -- S1: input ---------------------------------------------------------- #
    if screenshot and not (question and answer):
        log(f"S1 input   reading the Q&A out of {Path(screenshot).name}")
        got = extract_qa(screenshot, provider=provider)
        question = question or got["question"]
        answer = answer or got["answer"]
    if not question.strip() or not answer.strip():
        raise ValueError("Need a question and an answer (text or --screenshot).")

    folder = out_root / slugify_topic(topic or question[:60])
    folder.mkdir(parents=True, exist_ok=True)
    log(f"S1 folder  {folder}")

    # -- S2: review + figure ------------------------------------------------ #
    notes = "review skipped"
    if review:
        log("S2 review  checking the answer before anything is drawn")
        res = review_answer(question, answer, provider=provider)
        answer, notes = res["answer"], res["notes"]
        log(f"S2 review  {'corrected' if res['changed'] else 'no changes'}")

    fig = None
    if diagram or want_diagram or "![" in answer:
        try:
            fig = resolve_diagram(diagram, answer, folder / "diagram",
                                  log=lambda m: log("S2 " + m))
        except FileNotFoundError as exc:
            log(f"S2 diagram {exc}")
        if fig is None and want_diagram:
            log("S2 diagram none found — pass one with --diagram "
                "(searching the web is the agent's job, not this module's)")

    (folder / "question.txt").write_text(question.strip() + "\n", encoding="utf-8")
    (folder / "answer.txt").write_text(answer.strip() + "\n", encoding="utf-8")
    (folder / "review_notes.txt").write_text(notes + "\n", encoding="utf-8")

    # -- S3: temp, then (once approved) the page ---------------------------- #
    dia = None
    if fig is not None:
        dia = Diagram(path=str(fig), row=diagram_row, rows=0,
                      width_frac=diagram_width, side="right")

    result = generate(
        question, answer, sheet=sheet, style=style, out_dir=out_root,
        topic=topic or folder.name, question_label=question_label,
        diagram_rules=prompts.DIAGRAM_PROMPT if dia is not None else "",
        quality=quality, temp_only=not approve,
        diagram=dia, watermark_path=watermark_path,
        watermark_scale=watermark_scale, watermark_opacity=watermark_opacity,
        log=log)
    result["review_notes"] = notes
    result["diagram"] = str(fig) if fig else None
    return result
