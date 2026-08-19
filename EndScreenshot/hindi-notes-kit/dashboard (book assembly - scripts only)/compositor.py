"""Core image composition: fill the template slot with a page and draw the
editable chapter number + name into the header.

All layout numbers live in config.json so the header can be recalibrated when
the final blank templates arrive, without touching this code.
"""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).parent
IMG_EXTS = {".jpg", ".jpeg", ".png", ".webp"}


# --------------------------------------------------------------------------
# Config + fonts
# --------------------------------------------------------------------------
def load_config(path: Path | None = None) -> dict:
    path = path or (HERE / "config.json")
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


@lru_cache(maxsize=32)
def _font(font_path: str, size: int, weight: str) -> ImageFont.FreeTypeFont:
    font = ImageFont.truetype(font_path, size)
    try:  # variable font -> pick the weight axis
        font.set_variation_by_name(weight)
    except Exception:
        pass
    return font


def natural_key(name: str) -> list:
    """Sort page-2 before page-10, template-2 before template-10."""
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", name)]


# --------------------------------------------------------------------------
# Templates
# --------------------------------------------------------------------------
def list_templates(templates_dir: Path) -> list[Path]:
    files = [p for p in templates_dir.iterdir() if p.suffix.lower() in IMG_EXTS]
    return sorted(files, key=lambda p: natural_key(p.name))


@lru_cache(maxsize=128)
def _load_template(path_str: str, mtime: float) -> Image.Image:
    """Cache templates by (path, mtime) so re-uploads still refresh."""
    return Image.open(path_str).convert("RGBA")


def load_template(path: Path) -> Image.Image:
    return _load_template(str(path), path.stat().st_mtime)


# --------------------------------------------------------------------------
# Page fitting
# --------------------------------------------------------------------------
def fit_page(page: Image.Image, w: int, h: int, mode: str = "cover",
             bg=(255, 255, 255)) -> Image.Image:
    """Return the page sized exactly to (w, h) per fit mode.

    cover      -- scale to fill, center-crop the overflow (best for pages that
                  match the slot's A4 aspect). May trim edges.
    fit_width  -- scale so the page WIDTH fills the slot (left/right edges reach
                  the corners, never cropped horizontally); center vertically and
                  fill the top/bottom gap with `bg`. Use for non-A4 pages.
    contain    -- scale so the whole page fits inside the slot (never cropped at
                  all); center and fill all gaps with `bg`.
    stretch    -- distort to fill exactly.
    """
    page = page.convert("RGB")
    if mode == "stretch":
        return page.resize((w, h), Image.Resampling.LANCZOS)

    if mode == "cover":
        scale = max(w / page.width, h / page.height)
        nw, nh = round(page.width * scale), round(page.height * scale)
        page = page.resize((nw, nh), Image.Resampling.LANCZOS)
        left, top = (nw - w) // 2, (nh - h) // 2
        return page.crop((left, top, left + w, top + h))

    # fit_width / contain: scale, center on a bg tile of exactly (w, h).
    if mode == "fit_width":
        scale = w / page.width                       # fill width
    else:                                            # contain
        scale = min(w / page.width, h / page.height)
    nw, nh = round(page.width * scale), round(page.height * scale)
    resized = page.resize((nw, nh), Image.Resampling.LANCZOS)
    tile = Image.new("RGB", (w, h), tuple(bg[:3]))
    # Negative offsets let PIL clip a taller-than-slot page (top/bottom) while
    # keeping the full width -- corners never lost.
    tile.paste(resized, ((w - nw) // 2, (h - nh) // 2))
    return tile


# --------------------------------------------------------------------------
# Compose one page
# --------------------------------------------------------------------------
def compose(
    template: Image.Image,
    page: Image.Image,
    cfg: dict,
    header_overlay: Image.Image | None = None,
) -> Image.Image:
    """Compose one page with the template and the header overlay.

    The template has a transparent hole where the page shows through, so the
    page is placed on a background FIRST and the template composited ON TOP --
    its frame and rounded slot corners then mask the page edges cleanly. The
    header overlay (rendered once per job) goes on top of everything.
    """
    slot = cfg["slot"]
    bg = cfg.get("background_color", [255, 255, 255, 255])
    canvas = Image.new("RGBA", template.size, tuple(bg))
    mode = cfg.get("fit_mode", "cover")

    if mode == "cover":
        # Bleed past the hole so anti-aliased edges never show background.
        bleed = cfg.get("slot_bleed", 3)
        fitted = fit_page(page, slot["w"] + 2 * bleed, slot["h"] + 2 * bleed,
                          mode, bg)
        canvas.paste(fitted, (slot["x"] - bleed, slot["y"] - bleed))
    else:
        # fit_width / contain / stretch: exact slot-sized tile (white padded).
        fitted = fit_page(page, slot["w"], slot["h"], mode, bg)
        canvas.paste(fitted, (slot["x"], slot["y"]))

    canvas = Image.alpha_composite(canvas, template)

    if header_overlay is not None:
        if header_overlay.size != canvas.size:
            full = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
            full.paste(header_overlay, (0, 0))
            header_overlay = full
        canvas = Image.alpha_composite(canvas, header_overlay)
    return canvas


def save(image: Image.Image, out_path: Path, cfg: dict) -> Path:
    fmt = cfg.get("output_format", "PNG").upper()
    if fmt == "JPEG":
        out_path = out_path.with_suffix(".jpg")
        image.convert("RGB").save(out_path, "JPEG", quality=cfg.get("jpeg_quality", 95))
    else:
        out_path = out_path.with_suffix(".png")
        image.save(out_path, "PNG")
    return out_path
