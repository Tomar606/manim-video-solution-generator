"""Generate the illustration for a beat that a diagram cannot carry.

Some concepts are better shown than drawn. Rust on an iron nail is one: the
colour, the flaking texture and the way it spreads from patches are the whole
point, and vector shapes only approximate them. A generated photograph carries
it in one frame.

Most beats do NOT want this. Equations, graphs, circuits and labelled apparatus
are clearer as Manim vectors — sharper, exactly controllable, and free. Use an
image only when the *appearance of a real object* is the teaching content.

Images are transparent PNGs so they sit on the subject plate without a card of
their own, cached by prompt hash so a re-render costs nothing.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from src.frames import generate_image


def _cut_background(path: Path, tol: int = 34, feather: int = 2) -> None:
    """Replace the white sweep with real alpha, in place.

    Alpha comes from distance to the corner colour, so the cut follows the
    subject rather than a fixed threshold, and the edge is feathered so it does
    not alias against a dark page.
    """
    from PIL import Image, ImageFilter
    import numpy as np

    im = Image.open(path).convert("RGB")
    a = np.asarray(im).astype(int)
    # the four corners are background by construction
    corners = np.vstack([a[:8, :8].reshape(-1, 3), a[:8, -8:].reshape(-1, 3),
                         a[-8:, :8].reshape(-1, 3), a[-8:, -8:].reshape(-1, 3)])
    bg = corners.mean(axis=0)

    dist = np.sqrt(((a - bg) ** 2).sum(axis=2))
    alpha = np.clip((dist - tol) * (255.0 / max(tol, 1)), 0, 255).astype("uint8")

    mask = Image.fromarray(alpha, "L")
    if feather:
        mask = mask.filter(ImageFilter.GaussianBlur(feather))
    out = im.convert("RGBA")
    out.putalpha(mask)
    out.save(path)

# Never ask the model for a "transparent background": gpt-image-2 has no
# transparency support and instead PAINTS the grey checkerboard that represents
# it, which arrives as opaque RGB. Ask for a plain white studio sweep and cut it
# out afterwards — that yields real alpha, which matters because the subject
# plate has a vignette gradient and a flat colour patch would show as a square.
STYLE = (
    "Studio product photograph on a plain pure white seamless background, "
    "evenly lit, no shadow on the background, no floor line, no props, no "
    "scene, no border, no text, no watermark, no checkerboard. Subject centred "
    "and filling most of the frame, sharp focus, high detail, photographic "
    "realism, not an illustration."
)


def _key(prompt: str, size: str) -> str:
    return hashlib.sha256(f"{prompt}|{size}".encode()).hexdigest()[:16]


def concept_image(prompt: str, out_dir: str | Path, name: str, *,
                  size: str = "1024x1024", quality: str = "medium") -> Path:
    """Generate (or reuse) one transparent illustration.

    The cache key is the prompt, and the prompt here is written by hand rather
    than by a model — so unlike the anchor frames in `src/frames.py`, this cache
    actually hits and a re-render is free.
    """
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    full = f"{prompt.strip()} {STYLE}"
    dest = out / f"{name}_{_key(full, size)}.png"
    if dest.exists():
        print(f"   {name}: cached, no spend")
        return dest

    cost = generate_image(full, dest, size=size, quality=quality)
    _cut_background(dest)
    print(f"   {name}: generated (~${cost:.3f}) -> {dest.name}")

    manifest = out / "concept_images.json"
    rows = {}
    if manifest.exists():
        try:
            rows = json.loads(manifest.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            rows = {}
    rows[name] = {"file": dest.name, "prompt": full}
    manifest.write_text(json.dumps(rows, ensure_ascii=False, indent=2),
                        encoding="utf-8")
    return dest
