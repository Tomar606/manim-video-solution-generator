"""Parse an authored script into a :class:`VideoScript`.

Script format — YAML frontmatter between ``---`` fences, then a tagged body::

    ---
    title: Deriving the Quadratic Formula
    orientation: portrait            # landscape | portrait
    theme: midnight                  # named theme, or an inline mapping
    chroma: lower_third              # optional green-screen zone
    speakers:
      narrator: { voice: Rachel }
      student:  { voice: Josh }
    ---

    [narrator] We start from the general quadratic equation.
    $$ a x^2 + b x + c = 0 $$

    [narrator] Divide through by a to normalise the leading coefficient.
    $$ x^2 + \\frac{b}{a} x + \\frac{c}{a} = 0 $$

    [student] Why divide by a first?

Body rules:
  * A line ``[speaker] text`` starts a new segment; text runs until the next tag.
  * ``$$ ... $$`` (may span lines) and ``\\[ ... \\]`` become that segment's
    equations; everything else on the segment is spoken narration.
  * ``%% ...`` inside a segment is a director note (not spoken, not an equation).
  * ``![caption](path.png){full,kenburns}`` puts a photo on that beat. The path
    resolves against the script's folder, its ``assets/`` sibling, the project's
    ``assets/``, or an ``https://`` URL (downloaded and cached once). Layouts:
    ``full`` | ``side`` | ``inset``; effects: ``kenburns`` | ``static`` |
    ``frame`` | ``noframe``. A beat with a photo and no equation renders from a
    fixed template, so photo beats look the same in every video.

Frontmatter also accepts ``answer_image:`` (plus optional ``answer_narration``,
``answer_caption``, ``answer_duration``), which appends the answer card as a
final beat, and an ``avatar:`` mapping describing where the presenter is keyed
in — see :class:`src.config.AvatarConfig`.

The body parser (:func:`parse_body`) is pure and dependency-free so it can be
tested without PyYAML installed.
"""
from __future__ import annotations

import re

from pathlib import Path

from src.config import AvatarConfig, ChromaPreset, ChromaZone, Orientation
from src.images import ImageError, ImageRef, parse_modifiers, resolve_path
from src.script_models import DialogueSegment, SpeakerConfig, VideoScript
from src.themes import resolve_theme

_TAG_RE = re.compile(r"^\s*\[([A-Za-z0-9_\-][A-Za-z0-9_\- ]*)\]\s*(.*)$")
_EQ_BLOCK_RE = re.compile(r"\$\$(.+?)\$\$|\\\[(.+?)\\\]", re.DOTALL)
_NOTE_RE = re.compile(r"^\s*%%\s?(.*)$")
# ![caption](path/to.png){side,kenburns}   — the optional {..} carries layout
# and effect hints; the optional "title" is markdown-standard and ignored.
_IMAGE_RE = re.compile(
    r"!\[([^\]]*)\]\(\s*([^)\s]+)(?:\s+\"[^\"]*\")?\s*\)(\{[^}]*\})?"
)

DEFAULT_OUTRO_DURATION = 4.0


class ScriptParseError(ValueError):
    """Raised when a script cannot be parsed into a valid VideoScript."""


# --------------------------------------------------------------------------- #
# Frontmatter                                                                  #
# --------------------------------------------------------------------------- #
def split_frontmatter(raw: str) -> tuple[dict, str]:
    """Return (frontmatter_dict, body). Frontmatter is optional."""
    text = raw.lstrip("﻿")  # strip BOM
    if not text.lstrip().startswith("---"):
        return {}, text
    # Find the opening fence and the next fence.
    stripped = text.lstrip()
    lead = len(text) - len(stripped)
    rest = stripped[3:]  # after first '---'
    end = rest.find("\n---")
    if end == -1:
        raise ScriptParseError("Frontmatter opened with '---' but never closed.")
    fm_text = rest[:end]
    body = rest[end + 4:]
    # drop rest of the closing fence line
    nl = body.find("\n")
    body = body[nl + 1:] if nl != -1 else ""
    try:
        import yaml  # imported lazily so body parsing needs no deps
    except ModuleNotFoundError as exc:  # pragma: no cover
        raise ScriptParseError(
            "PyYAML is required to read script frontmatter (pip install pyyaml)."
        ) from exc
    data = yaml.safe_load(fm_text) or {}
    if not isinstance(data, dict):
        raise ScriptParseError("Frontmatter must be a YAML mapping.")
    _ = lead  # kept for clarity; leading whitespace is discarded
    return data, body


# --------------------------------------------------------------------------- #
# Body                                                                         #
# --------------------------------------------------------------------------- #
def _clean_narration(text: str) -> str:
    # Remove any residual inline math delimiters; collapse whitespace.
    text = re.sub(r"\$(.+?)\$", r"\1", text)  # inline $x$ -> x
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def parse_body(body: str) -> list[DialogueSegment]:
    """Parse the tagged body into ordered dialogue segments. Pure function."""
    # Group lines into segments keyed by speaker tags.
    raw_segments: list[tuple[str, list[str]]] = []
    current: tuple[str, list[str]] | None = None

    for line in body.splitlines():
        m = _TAG_RE.match(line)
        if m:
            if current is not None:
                raw_segments.append(current)
            speaker = m.group(1).strip().lower().replace(" ", "_")
            current = (speaker, [m.group(2)])
        else:
            if current is None:
                if line.strip():
                    raise ScriptParseError(
                        "Text appears before the first [speaker] tag: "
                        f"{line.strip()!r}"
                    )
                continue
            current[1].append(line)
    if current is not None:
        raw_segments.append(current)

    if not raw_segments:
        raise ScriptParseError("No [speaker] segments found in script body.")

    segments: list[DialogueSegment] = []
    for idx, (speaker, lines) in enumerate(raw_segments):
        chunk = "\n".join(lines)

        # Pull out director notes first (line-based).
        note_parts: list[str] = []
        kept_lines: list[str] = []
        for ln in chunk.splitlines():
            nm = _NOTE_RE.match(ln)
            if nm:
                note_parts.append(nm.group(1).strip())
            else:
                kept_lines.append(ln)
        chunk = "\n".join(kept_lines)

        # Extract image references, remove them from the narration text.
        # Paths stay unresolved here so parse_body remains filesystem-free;
        # resolve_images() fills them in once we know where the script lives.
        images: list[ImageRef] = []
        for im in _IMAGE_RE.finditer(chunk):
            caption, raw_path, mods = im.group(1), im.group(2), im.group(3)
            layout, effects = parse_modifiers(mods)
            images.append(ImageRef(raw=raw_path.strip(), path="",
                                   caption=(caption or "").strip(),
                                   layout=layout, effects=effects))
        chunk = _IMAGE_RE.sub(" ", chunk)

        # Extract equations, remove them from the narration text.
        equations: list[str] = []
        for em in _EQ_BLOCK_RE.finditer(chunk):
            eq = (em.group(1) or em.group(2) or "").strip()
            if eq:
                equations.append(eq)
        narration = _clean_narration(_EQ_BLOCK_RE.sub(" ", chunk))

        if not narration and not equations and not images:
            # An empty segment (e.g. stray tag) is skipped rather than fatal.
            continue

        segments.append(
            DialogueSegment(
                index=idx,
                speaker=speaker,
                narration=narration,
                equations=equations,
                images=images,
                note=" ".join(note_parts) or None,
            )
        )

    # Re-index compactly after any skips.
    for new_idx, seg in enumerate(segments):
        seg.index = new_idx
    return segments


# --------------------------------------------------------------------------- #
# Assembly                                                                     #
# --------------------------------------------------------------------------- #
def _parse_speakers(fm: dict) -> dict[str, SpeakerConfig]:
    speakers: dict[str, SpeakerConfig] = {}
    raw = fm.get("speakers") or {}
    if isinstance(raw, dict):
        for name, cfg in raw.items():
            key = str(name).strip().lower().replace(" ", "_")
            if isinstance(cfg, str):
                speakers[key] = SpeakerConfig(name=key, voice_id=cfg)
            elif isinstance(cfg, dict):
                voice_id = cfg.get("voice_id") or cfg.get("voice") or ""
                settings = {
                    k: v for k, v in cfg.items()
                    if k not in ("voice_id", "voice")
                }
                speakers[key] = SpeakerConfig(
                    name=key, voice_id=str(voice_id), settings=settings
                )
            else:
                raise ScriptParseError(f"Invalid speaker config for {name!r}.")
    return speakers


def _parse_chroma(fm: dict) -> ChromaZone:
    raw = fm.get("chroma")
    if raw is None:
        return ChromaZone()
    if isinstance(raw, str):
        return ChromaZone(preset=ChromaPreset.parse(raw))
    if isinstance(raw, dict):
        preset = ChromaPreset.parse(str(raw.get("preset", "none")))
        kwargs: dict = {"preset": preset}
        if raw.get("color"):
            kwargs["color"] = str(raw["color"])
        if raw.get("animate_in") is not None:
            kwargs["animate_in"] = bool(raw["animate_in"])
        if raw.get("rect"):
            kwargs["custom_rect"] = tuple(raw["rect"])
        if raw.get("safe"):
            kwargs["custom_safe"] = tuple(raw["safe"])
        return ChromaZone(**kwargs)
    raise ScriptParseError(f"Invalid chroma specification: {raw!r}")


def _parse_avatar(fm: dict) -> AvatarConfig:
    raw = fm.get("avatar")
    if raw is None:
        return AvatarConfig()
    if isinstance(raw, bool):
        return AvatarConfig(enabled=raw)
    if isinstance(raw, str):
        return AvatarConfig(placement=raw.strip().lower())
    if not isinstance(raw, dict):
        raise ScriptParseError(f"Invalid avatar specification: {raw!r}")

    kwargs: dict = {}
    if raw.get("enabled") is not None:
        kwargs["enabled"] = bool(raw["enabled"])
    if raw.get("placement"):
        kwargs["placement"] = str(raw["placement"]).strip().lower()
    if raw.get("rect"):
        kwargs["custom_rect"] = tuple(raw["rect"])
        kwargs.setdefault("placement", "custom")
    for key in ("scale", "similarity", "blend", "despill"):
        if raw.get(key) is not None:
            kwargs[key] = float(raw[key])
    if raw.get("offset"):
        off = tuple(raw["offset"])
        if len(off) != 2:
            raise ScriptParseError("avatar.offset must be [x, y].")
        kwargs["offset"] = (float(off[0]), float(off[1]))
    if raw.get("key_color"):
        kwargs["key_color"] = str(raw["key_color"])
    if raw.get("timing"):
        timing = str(raw["timing"]).strip().lower()
        if timing not in ("audio", "avatar"):
            raise ScriptParseError(
                f"avatar.timing must be 'audio' or 'avatar', got {timing!r}."
            )
        kwargs["timing"] = timing
    try:
        return AvatarConfig(**kwargs)
    except (TypeError, ValueError) as exc:
        raise ScriptParseError(f"Invalid avatar config: {exc}") from exc


def _append_outro(fm: dict, segments: list[DialogueSegment]) -> None:
    """Turn ``answer_image:`` into a real final beat.

    Making the answer image an ordinary segment (rather than something bolted
    on at assembly time) means it gets narration, timing, QC and compositing
    from the same code paths as every other beat.
    """
    raw = fm.get("answer_image")
    if not raw:
        return
    layout, effects = parse_modifiers(fm.get("answer_layout"))
    caption = str(fm.get("answer_caption") or "").strip()
    narration = str(fm.get("answer_narration") or "").strip()
    speaker = segments[-1].speaker if segments else "narrator"

    seg = DialogueSegment(
        index=len(segments),
        speaker=speaker,
        narration=narration,
        images=[ImageRef(raw=str(raw).strip(), path="", caption=caption,
                         layout=layout or "full", effects=effects)],
        note="Final answer card — hold the image so a viewer can read it.",
        is_outro=True,
    )
    if not narration:
        # Silent card: nothing to synthesize, so fix its length here.
        seg.target_duration = float(fm.get("answer_duration")
                                    or DEFAULT_OUTRO_DURATION)
    segments.append(seg)


def resolve_images(script: VideoScript, *, assets_dir: str | None = None,
                   extra_dirs: list[str] | None = None) -> None:
    """Point every ImageRef at a real file, or fail with a clear message.

    Searched in order: the script's own directory, a sibling ``assets/``, the
    project's ``assets/``, and the working directory.
    """
    search: list[Path] = []
    if script.source_path:
        script_dir = Path(script.source_path).resolve().parent
        search += [script_dir, script_dir / "assets"]
    if assets_dir:
        search.append(Path(assets_dir))
    for extra in (extra_dirs or []):
        search.append(Path(extra))
    search.append(Path.cwd())

    cache_root = Path(assets_dir) if assets_dir else (search[0] if search else Path.cwd())
    for seg in script.segments:
        for img in seg.images:
            if img.path:
                continue
            try:
                img.path = str(resolve_path(img.raw, search_dirs=search,
                                            assets_dir=cache_root))
            except ImageError as exc:
                raise ScriptParseError(
                    f"Segment {seg.index} ({seg.speaker}): {exc}"
                ) from exc


def build_script(fm: dict, segments: list[DialogueSegment],
                 source_path: str | None = None) -> VideoScript:
    orientation = Orientation.parse(str(fm.get("orientation", "landscape")))
    theme = resolve_theme(fm.get("theme"))
    chroma = _parse_chroma(fm)
    speakers = _parse_speakers(fm)
    avatar = _parse_avatar(fm)

    _append_outro(fm, segments)

    # Auto-declare any speaker used in the body but missing from frontmatter,
    # so an under-specified script still runs (TTS assigns a default voice).
    for seg in segments:
        if seg.speaker not in speakers:
            speakers[seg.speaker] = SpeakerConfig(name=seg.speaker, voice_id="")

    title = str(fm.get("title") or "Untitled").strip()
    fps = int(fm.get("fps") or 30)
    language = str(fm.get("language") or "hinglish").strip().lower()
    return VideoScript(
        title=title,
        orientation=orientation,
        theme=theme,
        chroma=chroma,
        speakers=speakers,
        segments=segments,
        source_path=source_path,
        fps=fps,
        language=language,
        avatar=avatar,
    )


def parse_script(raw: str, source_path: str | None = None, *,
                 assets_dir: str | None = None,
                 resolve: bool = True) -> VideoScript:
    fm, body = split_frontmatter(raw)
    segments = parse_body(body)
    script = build_script(fm, segments, source_path=source_path)
    if resolve:
        # Fail here, not mid-render, if a photo is missing.
        resolve_images(script, assets_dir=assets_dir)
    return script


def parse_script_file(path: str, *, assets_dir: str | None = None,
                      resolve: bool = True) -> VideoScript:
    with open(path, "r", encoding="utf-8") as f:
        return parse_script(f.read(), source_path=path,
                            assets_dir=assets_dir, resolve=resolve)
