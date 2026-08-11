"""Writing script changes back out, one beat at a time.

The dashboard edits a video the way an editor expects — click a clip, change its
line — but ``script.md`` is still the source of truth, so those edits have to
land back in the file losslessly enough that a human can keep hand-editing it.

Two rules make that safe:

* **Frontmatter is never re-serialized.** It's copied through verbatim, so
  comments, key order and formatting survive. YAML round-tripping would quietly
  eat all three.
* **The body is regenerated from the parsed segments.** That normalizes spacing
  and collapses multiple director notes on one beat into a single note — the
  only lossy part, and it's visible in the file straight after saving rather
  than surprising someone later.
"""
from __future__ import annotations

import re

from src.script_models import DialogueSegment

_FENCE_RE = re.compile(r"^\s*---\s*$", re.MULTILINE)


def split_frontmatter_raw(text: str) -> tuple[str, str]:
    """Return (frontmatter_block_including_fences, body).

    The frontmatter is returned as raw text so it can be written straight back.
    A script with no frontmatter yields ("", text).
    """
    stripped = text.lstrip("﻿")
    if not stripped.lstrip().startswith("---"):
        return "", stripped

    lead = len(stripped) - len(stripped.lstrip())
    after_open = stripped[lead + 3:]
    match = re.search(r"\n---[ \t]*(?:\n|$)", after_open)
    if not match:
        return "", stripped
    end = lead + 3 + match.end()
    return stripped[:end], stripped[end:]


def segment_to_markdown(seg: DialogueSegment) -> str:
    """Render one beat back into the script format."""
    lines = [f"[{seg.speaker}]"]
    narration = (seg.narration or "").strip()
    if narration:
        lines.append(narration)
    if seg.note:
        note = " ".join(seg.note.split())
        lines.append(f"%% {note}")
    for img in seg.images:
        mods = ""
        flags = ([img.layout] if img.layout != "full" else []) + list(img.effects)
        if flags:
            mods = "{" + ",".join(flags) + "}"
        lines.append(f"![{img.caption}]({img.raw}){mods}")
    for eq in seg.equations:
        eq = eq.strip()
        if "\n" in eq:
            lines.append(f"$$\n{eq}\n$$")
        else:
            lines.append(f"$$ {eq} $$")
    return "\n".join(lines)


def body_to_markdown(segments: list[DialogueSegment]) -> str:
    """Render every beat, skipping the outro (it lives in the frontmatter)."""
    blocks = [segment_to_markdown(s) for s in segments if not s.is_outro]
    return "\n\n".join(blocks) + "\n"


def rebuild(text: str, segments: list[DialogueSegment]) -> str:
    """Original script text + edited segments -> new script text."""
    frontmatter, _ = split_frontmatter_raw(text)
    body = body_to_markdown(segments)
    if not frontmatter:
        return body
    return f"{frontmatter.rstrip()}\n\n{body}"


# Fields the dashboard is allowed to change on a beat. Anything structural
# (adding beats, changing the answer image) goes through the script file.
EDITABLE = ("narration", "note", "speaker", "equations", "caption")


def apply_edit(seg: DialogueSegment, changes: dict) -> None:
    """Apply an inspector edit to one segment, in place."""
    if "narration" in changes:
        seg.narration = " ".join(str(changes["narration"]).split())
    if "note" in changes:
        note = " ".join(str(changes["note"]).split())
        seg.note = note or None
    if "speaker" in changes:
        speaker = str(changes["speaker"]).strip().lower().replace(" ", "_")
        if speaker:
            seg.speaker = speaker
    if "equations" in changes:
        raw = changes["equations"]
        if isinstance(raw, str):
            raw = [raw]
        seg.equations = [e.strip() for e in raw if str(e).strip()]
    if "caption" in changes and seg.images:
        seg.images[0].caption = str(changes["caption"]).strip()
