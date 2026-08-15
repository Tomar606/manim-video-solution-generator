"""STEP 3 — stamp the finished page with the Arivihan watermark.

The supplied mark (``assets/watermark.png``) is a 1080x1920 RGBA sheet whose
ink is pure black at about 10% alpha, sitting off-centre in its own canvas. Two
things follow, and both are why this is not a straight paste:

* **The canvas is not the mark.** Its aspect (9:16) does not match a notebook
  page (2:3), so pasting the sheet whole would letterbox the mark and push it
  off centre. The mark's bounding box is found and cropped first, then scaled
  and centred on the page — so the watermark lands dead centre whatever the
  page size.
* **The alpha is the design.** The file already carries the intended ~10%
  opacity, so it is composited as-is by default. ``opacity`` scales that
  further (1.0 keeps the artwork's own weight) rather than replacing it, so
  the mark can be made fainter without ever becoming heavier than intended.
"""
from __future__ import annotations

from pathlib import Path

# Fraction of the page WIDTH the mark spans. The supplied artwork covers ~56%
# of its own canvas width, so this keeps its intended proportions by default.
DEFAULT_SCALE = 0.56
DEFAULT_OPACITY = 1.0


def load_mark(path: str | Path):
    """Open the watermark and crop it to its ink — the canvas is discarded."""
    from PIL import Image

    wm = Image.open(path).convert("RGBA")
    alpha = wm.getchannel("A")
    box = alpha.getbbox()
    if box is None:                      # fully transparent: fall back to ink
        rgb = wm.convert("RGB").point(lambda v: 255 - v)
        box = rgb.convert("L").getbbox() or (0, 0, wm.width, wm.height)
    return wm.crop(box)


def apply(page, mark_path: str | Path, *, scale: float = DEFAULT_SCALE,
          opacity: float = DEFAULT_OPACITY):
    """Return ``page`` with the watermark centred on it.

    ``scale`` is the mark's width as a fraction of the page width; ``opacity``
    multiplies the artwork's own alpha (1.0 = exactly as supplied).
    """
    from PIL import Image

    base = page.convert("RGBA")
    mark = load_mark(mark_path)

    target_w = max(1, int(base.width * scale))
    target_h = max(1, int(mark.height * target_w / mark.width))
    mark = mark.resize((target_w, target_h), Image.LANCZOS)

    if opacity != 1.0:
        a = mark.getchannel("A").point(
            lambda v: max(0, min(255, int(v * opacity))))
        mark.putalpha(a)

    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    layer.paste(mark, ((base.width - target_w) // 2,
                       (base.height - target_h) // 2), mark)
    return Image.alpha_composite(base, layer).convert("RGB")


def stamp_file(src: str | Path, dest: str | Path, mark_path: str | Path,
               *, scale: float = DEFAULT_SCALE,
               opacity: float = DEFAULT_OPACITY) -> Path:
    from PIL import Image

    out = apply(Image.open(src), mark_path, scale=scale, opacity=opacity)
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    out.save(dest)
    return dest
