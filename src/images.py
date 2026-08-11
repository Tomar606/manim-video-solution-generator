"""Resolving the photos a script refers to.

Scripts name images the way markdown does — ``![caption](path)`` — and the
path may be relative to the script, relative to the project's ``assets/``
directory, absolute, or an ``http(s)`` URL. This module turns any of those into
a verified absolute path that a Manim ``ImageMobject`` can open, downloading and
caching remote images once.

Resolution is deliberately eager: a missing or corrupt image is reported when
the script is parsed, not twenty minutes later when its segment renders.
"""
from __future__ import annotations

import hashlib
import re
import shutil
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

# Formats Manim's ImageMobject (Pillow) opens reliably.
SUPPORTED_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".tif", ".tiff"}

# Layout hints an author can attach: ![cap](p){side}
LAYOUTS = {"full", "side", "inset"}
EFFECTS = {"kenburns", "static", "frame", "noframe"}

_URL_RE = re.compile(r"^https?://", re.IGNORECASE)


class ImageError(ValueError):
    """Raised when an image reference cannot be resolved to a usable file."""


@dataclass
class ImageRef:
    """One image referenced by a script segment."""

    raw: str                      # exactly as written in the script
    path: str                     # resolved absolute path on disk
    caption: str = ""             # markdown alt text, shown under the photo
    layout: str = "full"          # full | side | inset
    effects: list[str] = field(default_factory=list)

    @property
    def ken_burns(self) -> bool:
        # A slow push-in is the default for full-frame photos; it keeps a still
        # image from reading as a frozen video.
        if "static" in self.effects:
            return False
        return "kenburns" in self.effects or self.layout == "full"

    @property
    def framed(self) -> bool:
        return "noframe" not in self.effects

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "caption": self.caption,
            "layout": self.layout,
            "ken_burns": self.ken_burns,
            "framed": self.framed,
        }


def parse_modifiers(blob: str | None) -> tuple[str, list[str]]:
    """Parse a ``{side,kenburns}`` suffix into (layout, effects)."""
    layout = "full"
    effects: list[str] = []
    if not blob:
        return layout, effects
    for token in re.split(r"[,\s]+", blob.strip("{} ").lower()):
        if not token:
            continue
        if token in LAYOUTS:
            layout = token
        elif token in EFFECTS:
            effects.append(token)
        else:
            raise ImageError(
                f"Unknown image modifier {token!r}. "
                f"Layouts: {', '.join(sorted(LAYOUTS))}. "
                f"Effects: {', '.join(sorted(EFFECTS))}."
            )
    return layout, effects


def _cache_dir(assets_dir: Path) -> Path:
    d = assets_dir / "_cache"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _download(url: str, assets_dir: Path) -> Path:
    """Fetch a remote image once; later runs reuse the cached copy."""
    suffix = Path(urllib.parse.urlparse(url).path).suffix.lower()
    if suffix not in SUPPORTED_SUFFIXES:
        suffix = ".png"
    name = hashlib.sha256(url.encode()).hexdigest()[:16] + suffix
    dest = _cache_dir(assets_dir) / name
    if dest.exists() and dest.stat().st_size > 0:
        return dest
    try:
        with urllib.request.urlopen(url, timeout=30) as resp, \
                open(dest, "wb") as out:
            shutil.copyfileobj(resp, out)
    except (urllib.error.URLError, OSError) as exc:
        dest.unlink(missing_ok=True)
        raise ImageError(f"Could not download image {url}: {exc}") from exc
    if dest.stat().st_size == 0:
        dest.unlink(missing_ok=True)
        raise ImageError(f"Downloaded image was empty: {url}")
    return dest


def resolve_path(raw: str, *, search_dirs: list[Path],
                 assets_dir: Path | None = None) -> Path:
    """Resolve one reference to an existing file, or raise ImageError."""
    raw = raw.strip()
    if not raw:
        raise ImageError("Empty image path.")

    if _URL_RE.match(raw):
        if assets_dir is None:
            raise ImageError(
                f"Cannot cache remote image {raw} — no project assets dir."
            )
        return _download(raw, assets_dir)

    candidate = Path(raw).expanduser()
    tried: list[Path] = []
    if candidate.is_absolute():
        tried.append(candidate)
    else:
        for base in search_dirs:
            tried.append((base / candidate))
    for path in tried:
        if path.is_file():
            resolved = path.resolve()
            if resolved.suffix.lower() not in SUPPORTED_SUFFIXES:
                raise ImageError(
                    f"Unsupported image format {resolved.suffix!r} for {raw}. "
                    f"Use one of: {', '.join(sorted(SUPPORTED_SUFFIXES))}"
                )
            if resolved.stat().st_size == 0:
                raise ImageError(f"Image file is empty: {resolved}")
            return resolved

    locations = "\n".join(f"    {p}" for p in tried)
    raise ImageError(
        f"Image not found: {raw}\n  Looked in:\n{locations}\n"
        f"  Put the file in the project's assets/ folder, or use an absolute "
        f"path or an https:// URL."
    )


def make_ref(raw: str, *, caption: str = "", modifiers: str | None = None,
             search_dirs: list[Path], assets_dir: Path | None = None) -> ImageRef:
    layout, effects = parse_modifiers(modifiers)
    path = resolve_path(raw, search_dirs=search_dirs, assets_dir=assets_dir)
    return ImageRef(raw=raw, path=str(path), caption=caption.strip(),
                    layout=layout, effects=effects)


def probe_size(path: str) -> tuple[int, int] | None:
    """(width, height) via ffprobe — ffmpeg is already a hard dependency, so
    this avoids importing Pillow outside the render container."""
    from src import media
    try:
        out = media._run([
            "ffprobe", "-v", "error", "-select_streams", "v:0",
            "-show_entries", "stream=width,height",
            "-of", "csv=p=0:s=x", str(path),
        ]).stdout.strip()
        w, h = out.split("x")[:2]
        return int(w), int(h)
    except Exception:
        return None
