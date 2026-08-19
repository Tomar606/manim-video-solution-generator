"""Board + stream front (cover) pages.

Drop cover images into `front_pages/`, named `<Board>__<Stream>.<ext>`, e.g.:
    CBSE__PCM.png
    CBSE__PCB.png
    MP Board__PCB.png
    MP Board__PCMB.png

The dashboard reads whatever files exist and auto-populates the board and
stream dropdowns -- no code changes needed to add a new board/stream. The
double underscore `__` separates board from stream (either may contain spaces).
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image

IMG_EXTS = {".png", ".jpg", ".jpeg", ".webp"}
SEP = "__"


def scan(front_dir: Path) -> list[dict]:
    """Return [{board, stream, file}] for every valid front page found."""
    if not front_dir.exists():
        return []
    out = []
    for p in sorted(front_dir.iterdir()):
        if p.suffix.lower() not in IMG_EXTS or p.name.startswith("_"):
            continue
        stem = p.stem
        if SEP not in stem:
            continue
        board, stream = (s.strip() for s in stem.split(SEP, 1))
        if board and stream:
            out.append({"board": board, "stream": stream, "file": p.name})
    return out


def options(front_dir: Path) -> dict:
    """Boards, and the streams available per board, for the UI dropdowns."""
    combos = scan(front_dir)
    boards: list[str] = []
    streams_by_board: dict[str, list[str]] = {}
    for c in combos:
        if c["board"] not in streams_by_board:
            streams_by_board[c["board"]] = []
            boards.append(c["board"])
        if c["stream"] not in streams_by_board[c["board"]]:
            streams_by_board[c["board"]].append(c["stream"])
    return {"boards": boards, "streams_by_board": streams_by_board,
            "count": len(combos)}


def find(front_dir: Path, board: str, stream: str) -> Path | None:
    for c in scan(front_dir):
        if c["board"] == board and c["stream"] == stream:
            return front_dir / c["file"]
    return None


def load_cover(path: Path, size: tuple[int, int], bg=(255, 255, 255, 255)) -> Image.Image:
    """Load a cover sized exactly to `size` (the notes-page size) so every page
    in the output PDF/ZIP shares the same dimensions. Covers with the same
    aspect ratio (the normal case) fill edge-to-edge; a differing aspect is
    cover-fitted (scaled to fill, minimal center-crop) to avoid white bars."""
    size = tuple(size)
    cover = Image.open(path).convert("RGBA")
    if cover.size == size:
        return cover
    scale = max(size[0] / cover.width, size[1] / cover.height)
    nw, nh = round(cover.width * scale), round(cover.height * scale)
    cover = cover.resize((nw, nh), Image.Resampling.LANCZOS)
    left, top = (nw - size[0]) // 2, (nh - size[1]) // 2
    return cover.crop((left, top, left + size[0], top + size[1]))
