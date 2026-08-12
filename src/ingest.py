"""Turning a faculty document into a script the pipeline can render.

Real videos here don't start from a topic string — they start from a Word file
someone wrote, already broken into clips with the narration written out. That
document *is* the script; it just isn't in our format yet. So this reads it and
converts, rather than asking a model to invent something that already exists.

The shape we look for is the one the team already writes::

    सिकल सेल एनीमिया                 <- title
    CLIP 1 — सामान्य लाल रक्त कोशिका   <- beat heading (its own director note)
    <narration paragraph>              <- what the presenter says
    <narration paragraph>
    CLIP 2 — ...

Nothing is rewritten or "improved" on the way through: the narration lands in
the script verbatim. A document is somebody's approved copy, and silently
paraphrasing it would be the single fastest way to lose their trust in the tool.
"""
from __future__ import annotations

import html
import re
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

# "CLIP 1 — title", "Clip 2:", "CLIP 3 -", also tolerant of Hindi digits.
CLIP_RE = re.compile(
    r"^\s*(?:CLIP|Clip|CLIP\s*NO\.?|SCENE|Scene)\s*[#]?\s*([0-9०-९]+)\s*[—\-:–.]?\s*(.*)$"
)

DEVANAGARI = re.compile(r"[ऀ-ॿ]")


@dataclass
class Clip:
    number: int
    heading: str = ""
    paragraphs: list[str] = field(default_factory=list)

    @property
    def narration(self) -> str:
        # Paragraphs inside one clip are a single spoken run; the writer's line
        # breaks are layout, not pauses.
        return " ".join(" ".join(p.split()) for p in self.paragraphs).strip()


@dataclass
class Document:
    title: str
    clips: list[Clip]
    source: str = ""

    @property
    def is_devanagari(self) -> bool:
        text = " ".join(c.narration for c in self.clips)
        return bool(DEVANAGARI.search(text))

    @property
    def language(self) -> str:
        return "hindi" if self.is_devanagari else "hinglish"


def read_docx_paragraphs(path: str | Path) -> list[str]:
    """Extract paragraph text from a .docx without a third-party dependency.

    A .docx is a zip of XML; pulling the ``<w:t>`` runs out of ``document.xml``
    is enough for a plain narration document and keeps the install lean.
    """
    with zipfile.ZipFile(path) as z:
        xml = z.read("word/document.xml").decode("utf-8", "ignore")

    paragraphs: list[str] = []
    for block in re.findall(r"<w:p\b.*?</w:p>", xml, re.S):
        # <w:br/> and <w:tab/> are real separators inside a paragraph.
        block = re.sub(r"<w:(?:br|tab)\s*/>", " ", block)
        runs = re.findall(r"<w:t[^>]*>(.*?)</w:t>", block, re.S)
        text = html.unescape("".join(runs))
        text = " ".join(text.split())
        if text:
            paragraphs.append(text)
    return paragraphs


def read_paragraphs(path: str | Path) -> list[str]:
    p = Path(path)
    if p.suffix.lower() == ".docx":
        return read_docx_paragraphs(p)
    if p.suffix.lower() in (".md", ".txt"):
        return [" ".join(line.split())
                for line in p.read_text(encoding="utf-8").splitlines()
                if line.strip()]
    raise ValueError(
        f"Don't know how to read {p.suffix!r}. Use .docx, .md or .txt "
        f"(export Google Docs as .docx)."
    )


def parse_document(path: str | Path) -> Document:
    paragraphs = read_paragraphs(path)
    if not paragraphs:
        raise ValueError(f"{path} has no readable text.")

    title = ""
    clips: list[Clip] = []
    current: Clip | None = None

    for para in paragraphs:
        match = CLIP_RE.match(para)
        if match:
            if current is not None:
                clips.append(current)
            raw_number = match.group(1)
            try:
                number = int(raw_number)
            except ValueError:                      # Devanagari digits
                number = int(raw_number.translate(
                    str.maketrans("०१२३४५६७८९", "0123456789")))
            current = Clip(number=number, heading=match.group(2).strip())
            continue
        if current is None:
            # Anything before the first CLIP heading is the title.
            if not title:
                title = para
            continue
        current.paragraphs.append(para)

    if current is not None:
        clips.append(current)

    if not clips:
        raise ValueError(
            f"No 'CLIP n' headings found in {path}. The document should be "
            f"split into clips, e.g. 'CLIP 1 — <what it shows>'."
        )
    return Document(title=title or Path(path).stem, clips=clips,
                    source=str(path))


def to_script(doc: Document, *, orientation: str = "landscape",
              theme: str = "midnight", chroma: str = "none",
              voice: str = "George", answer_image: str | None = None) -> str:
    """Render a parsed document as a pipeline script, narration verbatim."""
    lines = [
        "---",
        f"title: {doc.title}",
        f"orientation: {orientation}",
        f"theme: {theme}",
        f"chroma: {chroma}",
        # The narration language decides which voice checks apply — a Devanagari
        # script must not be flagged for "not being Latin Hinglish".
        f"language: {doc.language}",
        "speakers:",
        f"  narrator: {{ voice: {voice} }}",
    ]
    if answer_image:
        lines += [
            f"answer_image: {answer_image}",
            "answer_caption: Exam answer",
        ]
    lines += [f"source_document: {Path(doc.source).name}", "---", ""]

    for clip in doc.clips:
        lines.append("[narrator]")
        lines.append(clip.narration)
        if clip.heading:
            # The author's clip heading is the clearest statement of what this
            # beat should show, so it becomes the animation direction.
            lines.append(f"%% {clip.heading}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def describe(doc: Document) -> str:
    out = [f"{doc.title}",
           f"  {len(doc.clips)} clips · language: {doc.language}"]
    for clip in doc.clips:
        words = len(doc.clips[0].narration.split()) if False else len(clip.narration.split())
        out.append(f"  [{clip.number}] {clip.heading or '(no heading)'}  "
                   f"— {words} words")
    return "\n".join(out)
