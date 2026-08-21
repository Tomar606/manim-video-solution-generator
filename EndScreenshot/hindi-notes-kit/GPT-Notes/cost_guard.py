"""cost_guard — enforce image-API cost levers on EVERY ``images.edit`` call.

This module monkeypatches ``openai.resources.images.Images.edit`` (sync + async)
so the three cost levers below are applied to every image-generation call made
anywhere in this project, regardless of what an individual script passes. It is
auto-loaded by ``sitecustomize.py`` in the project venv, so new/future scripts
are covered automatically with no per-script edits.

Levers (all enforced on every call):
  1. QUALITY CEILING — "high" is never sent. Quality is forced to ``medium``,
     or to ``OPENAI_IMAGE_QUALITY`` when that is set to the cheaper ``low``.
  2. INPUT-IMAGE CAP — at most ``COST_GUARD_MAX_IMAGES`` (default 2) input images
     per call: the base page + the handwriting anchor. Extra references (e.g. the
     size-reference image appended 3rd) are dropped.
  3. DOWNSCALE — every input image's long edge is shrunk to
     ``COST_GUARD_MAX_EDGE`` (default 1024 px) before upload, cutting input-image
     tokens.

Escape hatches (env vars):
  COST_GUARD_DISABLE=1     bypass entirely (not recommended)
  OPENAI_IMAGE_QUALITY     low | medium   ("high" is clamped to medium)
  COST_GUARD_MAX_IMAGES    max input images kept (default 2)
  COST_GUARD_MAX_EDGE      max long edge in px for input images (default 1024)
"""
from __future__ import annotations

import functools
import io
import os
import sys

_ALLOWED_QUALITY = ("low", "medium")  # "high" is deliberately excluded


def _forced_quality() -> str:
    q = (os.environ.get("OPENAI_IMAGE_QUALITY") or "medium").strip().lower()
    return q if q in _ALLOWED_QUALITY else "medium"


def _max_images() -> int:
    try:
        return max(1, int(os.environ.get("COST_GUARD_MAX_IMAGES", "2")))
    except ValueError:
        return 2


def _max_edge() -> int:
    try:
        return max(256, int(os.environ.get("COST_GUARD_MAX_EDGE", "1024")))
    except ValueError:
        return 1024


def _log(msg: str) -> None:
    print(f"[cost_guard] {msg}", file=sys.stderr, flush=True)


def _downscale(data: bytes, label: str) -> bytes:
    """Return possibly-smaller PNG bytes; pass through unchanged on any failure."""
    try:
        from PIL import Image
    except Exception:
        return data
    try:
        with Image.open(io.BytesIO(data)) as im:
            w, h = im.size
            edge = _max_edge()
            if max(w, h) <= edge:
                return data
            scale = edge / float(max(w, h))
            nw, nh = max(1, round(w * scale)), max(1, round(h * scale))
            im = im.convert("RGB").resize((nw, nh))
            buf = io.BytesIO()
            im.save(buf, format="PNG")
        _log(f"downscaled {label} {w}x{h} -> {nw}x{nh}")
        return buf.getvalue()
    except Exception:
        return data


def _shrink_entry(entry):
    """Downscale a single ``image`` entry, preserving the SDK's accepted shapes."""
    # (filename, bytes, mimetype) — the shape every script in this repo uses.
    if isinstance(entry, tuple) and len(entry) >= 2 and isinstance(entry[1], (bytes, bytearray)):
        label = str(entry[0]) if entry[0] else "image"
        return (entry[0], _downscale(bytes(entry[1]), label)) + tuple(entry[2:])
    # raw bytes
    if isinstance(entry, (bytes, bytearray)):
        return _downscale(bytes(entry), "inline-bytes")
    # file object / PathLike / anything else — leave untouched
    return entry


def _process_images(image):
    """Apply the input-image cap (lever 2) and downscale (lever 3)."""
    if isinstance(image, list):
        cap = _max_images()
        if len(image) > cap:
            _log(f"trimming input images {len(image)} -> {cap} (dropped extras, e.g. size-reference)")
            image = image[:cap]
        return [_shrink_entry(e) for e in image]
    # A single entry (one image) — nothing to cap, still downscale it.
    return _shrink_entry(image)


def _wrap(orig):
    @functools.wraps(orig)
    def edit(self, *args, **kwargs):
        if os.environ.get("COST_GUARD_DISABLE"):
            return orig(self, *args, **kwargs)

        # `image` may arrive positionally (first positional arg) or as a kwarg.
        if "image" in kwargs:
            kwargs["image"] = _process_images(kwargs["image"])
        elif args:
            args = (_process_images(args[0]),) + args[1:]

        forced = _forced_quality()
        current = kwargs.get("quality")
        if current != forced:
            if current is not None:
                _log(f"quality {current} -> {forced}")
            kwargs["quality"] = forced

        return orig(self, *args, **kwargs)

    edit._cost_guarded = True  # type: ignore[attr-defined]
    return edit


def install() -> bool:
    """Patch Images.edit (sync + async). Idempotent; safe to call repeatedly."""
    try:
        from openai.resources.images import Images
    except Exception:
        return False

    classes = [Images]
    try:
        from openai.resources.images import AsyncImages
        classes.append(AsyncImages)
    except Exception:
        pass

    patched = False
    for cls in classes:
        orig = getattr(cls, "edit", None)
        if orig is None or getattr(orig, "_cost_guarded", False):
            continue
        cls.edit = _wrap(orig)
        patched = True
    return patched


# Patch on import.
install()
