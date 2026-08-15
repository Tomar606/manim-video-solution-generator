"""STAGE 2 — read the input, check the answer, and find the figure.

Between "here is a question" and "typeset it" sits the work a person would
otherwise do by hand: read the material (which may be a screenshot), notice
that the answer is garbled or incomplete, fix it, and dig out the diagram.

Three jobs, and they are deliberately split by who is good at what:

``extract_qa``      a screenshot of a textbook page -> question + answer text.
                    Vision model; this is OCR plus judgement about which part
                    is the question.
``review_answer``   the answer is checked and corrected. This matters more
                    than it sounds: the first answer we were handed came from
                    OCR and carried mangled conjuncts (अर्दापारमम्य for
                    अर्द्धपारगम्य), a stray ₹ where a न belonged, and half of a
                    completely different question's answer stapled to the end.
                    All of that would have been faithfully hand-written onto
                    the page, because every later stage renders verbatim.
``resolve_diagram`` a figure supplied as a path, or a URL, or a markdown image
                    link buried in the OCR text, becomes a local file.

What is NOT here: searching the web for a diagram. That needs judgement about
whether a candidate image is actually the right apparatus, so it belongs to
the agent driving this (see .claude/skills/endscreenshot/), which finds a
figure and passes it in with ``--diagram``. A silent auto-download of whatever
an image search returned first is exactly the kind of thing that puts a wrong
diagram on a student's notes.

Model access goes through :mod:`src.llm`, so this runs on the Claude Code CLI
(no API key, billed to the subscription) unless configured otherwise.
"""
from __future__ import annotations

import re
import urllib.request
from pathlib import Path

# Markdown image embeds / bare URLs the OCR left behind. A textbook answer
# scanned with mathpix carries its own figure as a link — that IS the diagram,
# and it is better than anything a search would turn up.
_MD_IMAGE_RE = re.compile(r"!\[[^\]]*\]\(\s*(https?://[^)\s]+)")
_URL_RE = re.compile(r"https?://\S+\.(?:png|jpe?g|gif|webp)(?:\?\S*)?", re.I)

EXTRACT_SYSTEM = """You are reading a photograph or screenshot of a textbook \
or exam paper. Return the QUESTION and its ANSWER as plain text, exactly as \
printed — same language, same wording, same order.

Rules:
- Do not translate, summarise, shorten or explain anything.
- Do not include figure captions, page numbers, headers or question numbers \
that belong to OTHER questions.
- If the page shows several questions, return only the FIRST complete \
question and its answer.
- Mark a section heading inside the answer by starting its line with '# '.
- Mark a numbered or bulleted point by starting its line with '(i) ', '(ii) ' \
etc., or '- '.
- Separate paragraphs with a blank line."""

REVIEW_SYSTEM = """You are a subject expert checking a textbook answer before \
it is hand-written onto a student's notes page. Every later stage renders your \
output VERBATIM, so anything you leave wrong ends up on the page.

Fix, in this order:
1. OCR corruption — mangled conjuncts, wrong letters, stray symbols standing \
in for real characters (a '₹' or a digit where a न or similar belongs).
2. Content that does not belong — text from a DIFFERENT question, figure \
links, page furniture, repeated fragments. Delete it.
3. Factual and scientific errors. Correct them.
4. Gaps — if the answer is missing a step the question explicitly asks for \
(for example "and state its advantages" with no advantages given), add it, \
briefly and in the same voice.

Do NOT rewrite good prose, do not translate, do not change the language, and \
do not pad. Keep the author's register and terminology. If the answer is \
already correct, return it unchanged.

Formatting for the page:
- A section heading is its own line starting with '# '.
- A list item is its own line starting with '(i) ', '(ii) ' … or '- '.
- Paragraphs separated by a blank line.
- No markdown emphasis, no links, no images."""


def extract_qa(image_path: str | Path, *, provider: str | None = None) -> dict:
    """Screenshot of a Q&A -> ``{"question", "answer"}``."""
    from src.llm import complete

    prompt = ("Read the attached page and return exactly this shape:\n\n"
              "QUESTION:\n<the question>\n\nANSWER:\n<the full answer>")
    raw = complete(EXTRACT_SYSTEM, prompt, images=[str(image_path)],
                   effort="medium", provider=provider)
    q, a = "", raw.strip()
    m = re.search(r"QUESTION:\s*(.*?)\s*ANSWER:\s*(.*)$", raw, re.S | re.I)
    if m:
        q, a = m.group(1).strip(), m.group(2).strip()
    return {"question": q, "answer": a}


def review_answer(question: str, answer: str, *,
                  provider: str | None = None) -> dict:
    """Check and correct the answer. Returns ``{"answer", "changed", "notes"}``."""
    from src.llm import complete

    prompt = (f"QUESTION:\n{question.strip()}\n\n"
              f"ANSWER AS SUPPLIED:\n{answer.strip()}\n\n"
              "Return the corrected answer only — no preamble, no commentary, "
              "no code fences. Then, after a line containing exactly '---NOTES---', "
              "list in one short line each what you changed (or write 'no changes').")
    raw = complete(REVIEW_SYSTEM, prompt, effort="medium", provider=provider)

    body, _, notes = raw.partition("---NOTES---")
    fixed = body.strip()
    # A refusal or an empty completion must never silently blank the answer.
    if len(fixed) < max(40, len(answer) * 0.4):
        return {"answer": answer, "changed": False,
                "notes": "review returned too little text — kept the original"}
    return {"answer": fixed, "changed": fixed.strip() != answer.strip(),
            "notes": notes.strip() or "no notes"}


def find_figure_links(text: str) -> list[str]:
    """Image URLs embedded in the supplied text, best first.

    A mathpix-OCR'd textbook answer carries its own figure this way, which is
    the most reliable diagram there is — it is the one that belongs to this
    exact question.
    """
    return _MD_IMAGE_RE.findall(text) or _URL_RE.findall(text)


def download(url: str, dest_dir: str | Path, *, name: str = "diagram") -> Path:
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    suffix = Path(url.split("?")[0]).suffix.lower() or ".jpg"
    dest = dest_dir / f"{name}{suffix}"
    req = urllib.request.Request(url, headers={"User-Agent": "EndScreenshot/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r, open(dest, "wb") as fh:
        fh.write(r.read())
    # Verify it decodes — a 404 HTML page saved as .jpg fails here, not later
    # in the middle of typesetting.
    from PIL import Image
    with Image.open(dest) as im:
        im.verify()
    return dest


def resolve_diagram(source: str | None, answer_text: str, dest_dir: str | Path,
                    *, log=None) -> Path | None:
    """Turn a diagram reference into a local file.

    ``source`` may be a local path or a URL. With no source, any image link
    inside the answer text is used. Returns None when there is nothing to use —
    finding a figure on the web is the agent's job, not this module's.
    """
    log = log or (lambda m: None)
    if source:
        p = Path(source)
        if p.exists():
            log(f"diagram: using {p}")
            return p
        if source.startswith(("http://", "https://")):
            got = download(source, dest_dir)
            log(f"diagram: downloaded {source[:60]}… -> {got}")
            return got
        raise FileNotFoundError(f"No diagram at {source}")

    for url in find_figure_links(answer_text):
        try:
            got = download(url, dest_dir)
            log(f"diagram: recovered from a link in the answer -> {got}")
            return got
        except Exception as exc:
            log(f"diagram: link failed ({exc}); trying the next one")
    return None
