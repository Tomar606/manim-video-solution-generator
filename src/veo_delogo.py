"""Find and remove the marker Flow burns into every generated clip.

    box = find_marker(clip)          # (x, y, w, h) at SOURCE resolution, or None
    delogo(clip, out, box)

WHY THIS IS CODE AND NOT A NOTE
-------------------------------
Google Flow stamps a small four-pointed sparkle into every clip it renders. It
is added AFTER generation, so no prompt prevents it: putting "sparkle" in the
NEGATIVE list does nothing except name a thing, which the bug ledger says is a
reason it gets drawn. It is the only text-like mark that survives a prompt whose
whole contract is that the frame carries the animation and NOT ONE character.

It was written down and then not implemented, so every clip that reached a
review was failed for carrying it — correctly, and uselessly, because the fix
belongs before the review rather than in it.

HOW IT IS FOUND
---------------
The marker is BRIGHT and it does not move; the subject moves. So the pixel-wise
MINIMUM across frames spread through the clip keeps the marker at full
brightness and darkens everything the subject passes through. Whatever is still
bright in that minimum, in the corner region where Flow puts it, is the marker.

Locating it per clip rather than trusting a constant matters: the position has
already moved between clips (1161,600 of 1280x720 in one, lower-right of
1920x1080 in another), and a delogo box in the wrong place smears a patch of
good picture instead.
"""
from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

# Where Flow has put it so far. Searching the whole frame invites a bright part
# of the subject to be mistaken for the marker; searching this corner does not
# cost anything, because that is where the mark lives.
CORNER = (0.62, 0.60, 1.00, 1.00)     # x0, y0, x1, y1 as fractions
# ADAPTIVE, NOT ABSOLUTE. The marker is a soft grey diamond, not a white one:
# on a slate plate it reads about 150 against a background about 80, and a fixed
# near-white threshold caught only its brightest tip and delogo'd a 22x21 hole
# out of the middle of a 100px mark, leaving the rest of it on screen looking
# deliberate. What identifies it is standing out from ITS OWN surroundings.
LIFT = 22             # grey levels above the corner's own median
MAX_AREA = 0.010      # of the frame; larger than this is subject, not a mark
PAD = 8               # px of margin, so the anti-aliased edge goes too
MIN_AREA = 40         # px; smaller than this is noise in the plate


def _frames(clip: Path, n: int = 9) -> list[np.ndarray]:
    dur = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", str(clip)],
        capture_output=True, text=True).stdout.strip()
    try:
        dur = float(dur)
    except ValueError:
        return []
    out = []
    with tempfile.TemporaryDirectory() as td:
        for i in range(n):
            t = dur * (i + 0.5) / n
            f = Path(td) / f"{i}.png"
            subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}",
                            "-i", str(clip), "-frames:v", "1", str(f), "-y"],
                           check=False)
            if f.is_file():
                out.append(np.asarray(Image.open(f).convert("L")).astype(np.uint8))
    return out


def find_marker(clip: Path) -> tuple[int, int, int, int] | None:
    """The marker's box at source resolution, or None if the clip has none."""
    fr = _frames(clip)
    if len(fr) < 3:
        return None
    stack = np.min(np.stack(fr), axis=0)          # static-and-bright survives
    h, w = stack.shape
    x0, y0 = int(CORNER[0] * w), int(CORNER[1] * h)
    region = stack[y0:, x0:].astype(int)
    hot = region >= (int(np.median(region)) + LIFT)
    if not hot.any():
        return None

    # One blob: take the brightest pixel and grow to its connected bright
    # neighbourhood by flood fill. scipy is not a dependency, so this is a
    # simple stack-based fill — the regions involved are a few hundred pixels.
    ys, xs = np.nonzero(hot)
    seed = int(np.argmax(region[ys, xs]))
    todo = [(int(ys[seed]), int(xs[seed]))]
    seen = set(todo)
    while todo:
        cy, cx = todo.pop()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = cy + dy, cx + dx
            if (0 <= ny < hot.shape[0] and 0 <= nx < hot.shape[1]
                    and (ny, nx) not in seen and hot[ny, nx]):
                seen.add((ny, nx))
                todo.append((ny, nx))
    if len(seen) / float(w * h) > MAX_AREA or len(seen) < MIN_AREA:
        return None                     # the subject, or noise in the plate
    by = [p[0] for p in seen]
    bx = [p[1] for p in seen]
    x = max(0, x0 + min(bx) - PAD)
    y = max(0, y0 + min(by) - PAD)
    bw = min(w - x, (max(bx) - min(bx) + 1) + 2 * PAD)
    bh = min(h - y, (max(by) - min(by) + 1) + 2 * PAD)
    # delogo needs at least one pixel of surround to interpolate from.
    if x + bw >= w:
        bw = w - x - 1
    if y + bh >= h:
        bh = h - y - 1
    if bw < 4 or bh < 4:
        return None
    return int(x), int(y), int(bw), int(bh)


def delogo(clip: Path, out: Path, box: tuple[int, int, int, int]) -> Path:
    """Interpolate the marker away, at SOURCE resolution and before any scale."""
    x, y, w, h = box
    subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(clip),
         "-vf", f"delogo=x={x}:y={y}:w={w}:h={h}",
         "-c:v", "libx264", "-preset", "medium", "-crf", "17",
         "-pix_fmt", "yuv420p", "-an", str(out), "-y"], check=True)
    return out


def strip(clip: Path, out: Path) -> tuple[Path, tuple[int, int, int, int] | None]:
    """Remove the marker if there is one. Returns (path to use, box found)."""
    box = find_marker(clip)
    if not box:
        return clip, None
    return delogo(clip, out, box), box
