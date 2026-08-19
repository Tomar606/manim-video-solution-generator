"""Turn an uploaded PDF (or image files) into a list of page images."""

from __future__ import annotations

import io
from pathlib import Path

import fitz  # PyMuPDF
from PIL import Image

IMG_EXTS = {".jpg", ".jpeg", ".png", ".webp"}


def pdf_to_images(pdf_bytes: bytes, dpi: int = 200) -> list[Image.Image]:
    """Render every page of a PDF to a PIL image at the given DPI."""
    pages: list[Image.Image] = []
    zoom = dpi / 72.0
    matrix = fitz.Matrix(zoom, zoom)
    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
        for page in doc:
            pix = page.get_pixmap(matrix=matrix, alpha=False)
            pages.append(Image.frombytes("RGB", (pix.width, pix.height), pix.samples))
    return pages


def image_bytes_to_image(data: bytes) -> Image.Image:
    return Image.open(io.BytesIO(data)).convert("RGB")


def load_uploads(files: list[tuple[str, bytes]], dpi: int = 200) -> list[Image.Image]:
    """Accept a mixed list of (filename, bytes); expand PDFs, keep images.

    Image files are sorted naturally by filename first so page order is
    predictable; a single PDF keeps its native page order.
    """
    from compositor import natural_key

    images: list[Image.Image] = []
    image_files = [(n, b) for n, b in files if Path(n).suffix.lower() in IMG_EXTS]
    pdf_files = [(n, b) for n, b in files if Path(n).suffix.lower() == ".pdf"]

    for _, data in pdf_files:
        images.extend(pdf_to_images(data, dpi=dpi))

    for name, data in sorted(image_files, key=lambda t: natural_key(t[0])):
        images.append(image_bytes_to_image(data))

    return images


def images_to_pdf_bytes(images: list[Image.Image]) -> bytes:
    """Combine composed pages into a single PDF (for optional download)."""
    if not images:
        return b""
    rgb = [im.convert("RGB") for im in images]
    buf = io.BytesIO()
    rgb[0].save(buf, "PDF", save_all=True, append_images=rgb[1:], resolution=150)
    return buf.getvalue()
