"""Turning a question and answer into tagged lines, and those onto pages.

Two jobs, both ported from notes-editor:

*Tagging* — the master prompt styles a line by the ``<<TAG>>`` it starts with,
so plain text has to be turned into that vocabulary. notes-editor gets its tags
from a vision model reading a chapter PDF; here the exact text is given, so
:func:`tag_content` does it from simple markup instead. Asking a model to
rewrite text we were handed verbatim would risk it inventing or dropping
content, which is the one thing this feature cannot do.

*Packing* — a page break happens when the page is physically FULL, measured
against the real ruled lines counted off the base sheet, not at a guessed word
count. That is what keeps the writing at one steady size instead of the model
cramming or padding to fit.
"""
from __future__ import annotations

import re

# Row budget. WORDS_PER_ROW is notes-editor's English figure; Devanagari gets a
# lower one because the script runs wider per word (शिरोरेखा plus matras).
# Without the split, every Hindi page overflows its ruled rows.
WORDS_PER_ROW = 7
WORDS_PER_ROW_DEVANAGARI = 5
TOP_GAP_ROWS = 2                  # natural blank gap at the top of a page
BOTTOM_MARGIN_ROWS = 2            # the last ruled line always stays blank

_DEVANAGARI = re.compile(r"[ऀ-ॿ]")
_TAG_RE = re.compile(r"^<<(\w+)>>\s*(.*)$", re.S)

# Mathpix OCR of a textbook page leaves image links behind. They are not
# content — writing them out would put a URL on the notebook page.
_MD_IMAGE_RE = re.compile(r"!\[[^\]]*\]\([^)]*\)")
_BARE_URL_RE = re.compile(r"https?://\S+")


# --------------------------------------------------------------------------- #
# Cleaning + tagging                                                           #
# --------------------------------------------------------------------------- #
def strip_links(text: str) -> str:
    """Drop markdown image embeds and bare URLs from OCR'd answer text."""
    text = _MD_IMAGE_RE.sub(" ", text)
    text = _BARE_URL_RE.sub(" ", text)
    return re.sub(r"[ \t]{2,}", " ", text)


def tag_content(question: str, answer: str, *, question_label: str = "Q1",
                heading: str = "") -> list[str]:
    """Turn a question and answer into the master prompt's tagged line stream.

    Input conventions, so a caller can shape a page from plain text:
      * a blank line separates paragraphs;
      * a line starting ``#`` is a section heading;
      * a line starting ``-``, ``*``, ``(i)`` or ``1.`` is a list item.
    """
    lines: list[str] = []
    if heading:
        lines.append(f"<<TITLE>> {heading}")
    lines.append(f"<<Q>> {question_label}: {strip_links(question).strip()}")
    lines.append("<<GAP>>")

    first = True
    for block in re.split(r"\n\s*\n", strip_links(answer)):
        block = block.strip()
        if not block:
            continue
        for raw in block.splitlines():
            raw = raw.strip()
            if not raw:
                continue
            if raw.startswith("#"):
                lines.append("<<GAP>>")
                lines.append(f"<<SUBHEAD>> {raw.lstrip('#').strip()}")
                continue
            item = re.match(r"^(?:[-*•]|\(?[ivx]+\)|\(?\d+[.)])\s+(.*)$",
                            raw, re.I)
            if item:
                lines.append(f"<<POINT>> {item.group(1).strip()}")
                continue
            if first:
                lines.append(f"<<ANS>> {raw}")     # carries the "Ans:" label
                first = False
            else:
                lines.append(f"<<TEXT>> {raw}")
    return lines


def normalize_lines(lines: list[str]) -> list[str]:
    """Repair shapes the packer cannot read (ported from notes-editor).

    Chiefly a ``<<GAP>>`` merged onto the next tag's line: the packer would
    read it as a gap with no text and silently delete the heading behind it.
    """
    out: list[str] = []
    for raw in lines:
        line = str(raw).strip()
        for q in ('"', '“', '”', '″'):
            line = line.replace(q, "")
        # Source bullet glyphs would double up with the marker the writer draws.
        for g in ('●', '•', '▪', '◦', '​', '‍'):
            line = line.replace(g, "")
        while line:
            m = _TAG_RE.match(line)
            if not m:
                out.append(line)
                break
            tag, rest = f"<<{m.group(1)}>>", m.group(2).strip()
            if tag.upper() == "<<GAP>>":
                out.append("<<GAP>>")
                line = rest
                continue
            nxt = _TAG_RE.match(rest)
            if nxt:                       # two tagged lines glued together
                out.append(f"{tag} {rest[:nxt.start()]}".strip())
                line = rest
                continue
            out.append(f"{tag} {rest}".strip() if rest else tag)
            break
    return [ln for ln in out if ln]


# --------------------------------------------------------------------------- #
# Row measurement and packing                                                  #
# --------------------------------------------------------------------------- #
def count_ruled_rows(page, default: int = 30) -> int:
    """Count printed ruled lines on a page (darkness peaks down its profile)."""
    try:
        import numpy as np
    except ImportError:
        return default
    g = np.asarray(page.convert("L"), dtype=float)
    x0, x1 = int(g.shape[1] * 0.18), int(g.shape[1] * 0.92)
    prof = np.median(g[:, x0:x1], axis=1)
    base = float(np.median(prof))
    dark = prof < base - 6
    runs, prev = 0, False
    for d in dark:
        if d and not prev:
            runs += 1
        prev = bool(d)
    return runs if 10 <= runs <= 60 else default


def usable_rows(page, default: int = 30) -> tuple[int, int]:
    """(ruled rows on the page, rows actually writable on it)."""
    rows = count_ruled_rows(page, default)
    return rows, max(10, rows - TOP_GAP_ROWS - BOTTOM_MARGIN_ROWS)


def words_per_row(text: str) -> int:
    """Devanagari runs wider per word than Latin, so it gets fewer per row."""
    return WORDS_PER_ROW_DEVANAGARI if _DEVANAGARI.search(text) \
        else WORDS_PER_ROW


def rows_needed(line: str) -> tuple[int, int]:
    """(gap_rows_before, rows) this tagged line occupies on the page."""
    m = _TAG_RE.match(line)
    if m:
        tag, text = m.group(1).upper(), m.group(2)
    elif line.startswith("[["):
        # A sketch eats real vertical space; costing it too cheaply makes the
        # packer believe a page has room it does not, and it comes out half
        # empty.
        return 1, 10 if line.upper().startswith("[[DIAGRAM") else 2
    else:
        tag, text = "TEXT", line
    words = len(text.split())
    if tag == "GAP":
        return 0, 1
    if tag == "TITLE":
        return 0, 2
    if tag == "SUBHEAD":
        return 1, 1
    rows = max(1, -(-words // words_per_row(text)))       # ceil
    return (1 if tag in ("Q", "ANS") else 0), rows


def _group_blocks(lines: list[str]) -> list[list[str]]:
    """Group into atomic units: a figure block owns the body lines after it."""
    groups: list[list[str]] = []
    for line in lines:
        s = line.strip()
        if s.startswith("[["):
            groups.append([line])
        elif groups and groups[-1][0].strip().startswith("[[") \
                and not s.startswith("<<"):
            groups[-1].append(line)
        else:
            groups.append([line])
    return groups


def split_by_rows(lines: list[str], usable: int) -> list[dict]:
    """Pack the line stream onto pages by simulated row count.

    A page breaks only when the next line no longer fits, so no page is left
    part-empty in the middle, and a heading is never stranded at the foot of a
    page. Returns ``[{"content", "rows"}]``.
    """
    MIN_ROWS_UNDER_HEAD = 3

    costed = []
    for g in _group_blocks(lines):
        rows = sum(rows_needed(ln)[1] for ln in g)
        is_block = g[0].strip().startswith("[[")
        if is_block:
            rows += 1
        costed.append({
            "lines": g, "rows": rows, "block": is_block,
            "head": g[0].upper().startswith(("<<SUBHEAD>>", "<<TITLE>>")),
        })

    pages: list[dict] = []
    cur: list[str] = []
    used = 0
    for i, item in enumerate(costed):
        line = item["lines"][0]
        # A gap that lands on a page break IS the page break.
        if line.upper().startswith("<<GAP>>") and not cur:
            continue
        gap = 1 if item["block"] else rows_needed(line)[0]
        need = item["rows"] + (gap if cur else 0)
        room = usable - used

        if cur and need > room:
            pages.append({"content": "\n".join(cur), "rows": used})
            cur, used = list(item["lines"]), item["rows"]
            continue

        # Never strand a heading at the foot of a page. Requiring only
        # MIN_ROWS_UNDER_HEAD is not enough: whatever comes FIRST under the
        # heading — a figure block or a long paragraph — must itself fit,
        # otherwise the heading is written with a blank page bottom under it
        # and its content starts on the next page anyway.
        if item["head"] and cur:
            after, first_rows = 0, 0
            for nxt in costed[i + 1:]:
                if nxt["rows"] and not first_rows:
                    first_rows = nxt["rows"]
                after += nxt["rows"]
                if nxt["head"] or after >= MIN_ROWS_UNDER_HEAD:
                    break
            required = max(min(after, MIN_ROWS_UNDER_HEAD),
                           min(first_rows, MIN_ROWS_UNDER_HEAD)
                           if first_rows <= room - need else first_rows)
            if room - need < required:
                pages.append({"content": "\n".join(cur), "rows": used})
                cur, used = list(item["lines"]), item["rows"]
                continue

        used += need
        cur.extend(item["lines"])

    if cur:
        pages.append({"content": "\n".join(cur), "rows": used})
    return pages


def total_rows(lines: list[str]) -> int:
    """Rows the whole stream wants, gaps included — for a dry run."""
    return sum(sum(rows_needed(ln)) for ln in lines)
