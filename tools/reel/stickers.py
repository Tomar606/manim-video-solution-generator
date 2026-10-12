"""Cut paper-sticker figures out of a generated image.

    python3 tools/reel/stickers.py <image> <out_dir> [--name base] [--min 4000]

Flow's image model draws each figure as a sticker (the figure, a white paper edge
around it) on a plain pale background. This removes that background by flooding in
from the image's border, so the sticker's own white edge, which touches the
background only through its faint outline, is kept. Every separate sticker is
written as <name>_<n>.png (RGBA, cropped, numbered left to right then top to
bottom), plus <name>_sheet.png for checking.

Only the background that is CONNECTED to the image border is removed: white that
is inside a figure (eyes, a stripe on a suit) stays opaque.
"""
import argparse
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter


def background_mask(rgb, tol):
    """True where a pixel belongs to the border-connected background."""
    h, w, _ = rgb.shape
    border = np.concatenate([rgb[0], rgb[-1], rgb[:, 0], rgb[:, -1]]).astype(int)
    bg = np.median(border, axis=0)
    px = rgb.astype(int)
    mean, bgm = px.mean(axis=2), bg.mean()
    chroma = px.max(axis=2) - px.min(axis=2)
    # The sticker's paper is WARM (red above blue, it is cream); the background it was shot on
    # is neutral or cool, sometimes with a soft grey shadow. So background = close to the
    # background colour, or a colourless grey a little darker than it, and never warm.
    warm = (px[..., 0] - px[..., 2]) > (bg[0] - bg[2]) + 3
    near = (((np.abs(px - bg).max(axis=2) <= tol)
             | ((chroma <= 12) & (mean >= bgm - 70) & (mean <= bgm + 6)))
            & ~warm)
    seen = np.zeros((h, w), bool)
    q = deque()
    for x in range(w):
        for y in (0, h - 1):
            if near[y, x] and not seen[y, x]:
                seen[y, x] = True
                q.append((y, x))
    for y in range(h):
        for x in (0, w - 1):
            if near[y, x] and not seen[y, x]:
                seen[y, x] = True
                q.append((y, x))
    while q:
        y, x = q.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and near[ny, nx] and not seen[ny, nx]:
                seen[ny, nx] = True
                q.append((ny, nx))
    return seen


def components(fg, min_px):
    """Bounding boxes of the separate foreground blobs, big ones only."""
    h, w = fg.shape
    lab = np.zeros((h, w), np.int32)
    boxes, n = [], 0
    for sy, sx in zip(*np.nonzero(fg)):
        if lab[sy, sx]:
            continue
        n += 1
        q = deque([(sy, sx)])
        lab[sy, sx] = n
        ys, xs, cnt = [sy, sy], [sx, sx], 0
        while q:
            y, x = q.popleft()
            cnt += 1
            ys[0], ys[1] = min(ys[0], y), max(ys[1], y)
            xs[0], xs[1] = min(xs[0], x), max(xs[1], x)
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ny, nx = y + dy, x + dx
                if 0 <= ny < h and 0 <= nx < w and fg[ny, nx] and not lab[ny, nx]:
                    lab[ny, nx] = n
                    q.append((ny, nx))
        if cnt >= min_px:
            boxes.append((n, xs[0], ys[0], xs[1] + 1, ys[1] + 1))
    return lab, boxes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image")
    ap.add_argument("out_dir")
    ap.add_argument("--name")
    ap.add_argument("--tol", type=int, default=16, help="how far from the background colour still counts as background")
    ap.add_argument("--min", type=int, default=4000, help="smallest sticker kept, in pixels")
    ap.add_argument("--one", action="store_true", help="a single pose: keep only the biggest sticker")
    a = ap.parse_args()
    src = Path(a.image)
    name = a.name or src.stem
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    im = Image.open(src).convert("RGB")
    rgb = np.asarray(im)
    bg = background_mask(rgb, a.tol)
    fg = ~bg
    lab, boxes = components(fg, a.min)
    if a.one and boxes:
        boxes = [max(boxes, key=lambda b: int((lab[b[2]:b[4], b[1]:b[3]] == b[0]).sum()))]
    # left to right, then top to bottom (rows grouped by overlap)
    boxes.sort(key=lambda b: (round(b[2] / max(1, rgb.shape[0] / 3)), b[1]))
    # a soft one-pixel alpha edge, so the cut does not stair-step when scaled
    alpha_all = Image.fromarray((fg * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.7))
    rgba = im.convert("RGBA")
    tiles = []
    for i, (n, x0, y0, x1, y1) in enumerate(boxes, 1):
        keep = Image.fromarray(((lab == n) * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3))
        a_ = Image.fromarray(np.minimum(np.asarray(alpha_all), np.asarray(keep)))
        piece = rgba.copy()
        piece.putalpha(a_)
        pad = 4
        box = (max(0, x0 - pad), max(0, y0 - pad), min(rgb.shape[1], x1 + pad), min(rgb.shape[0], y1 + pad))
        piece = piece.crop(box)
        f = out / f"{name}_{i}.png"
        piece.save(f)
        tiles.append(piece)
        print(f"{f.name}: {piece.size[0]}x{piece.size[1]} at x {box[0]} y {box[1]}")
    if tiles:
        H = max(t.size[1] for t in tiles)
        W = sum(t.size[0] for t in tiles) + 20 * (len(tiles) + 1)
        sheet = Image.new("RGBA", (W, H + 40), (60, 120, 160, 255))
        x = 20
        for t in tiles:
            sheet.alpha_composite(t, (x, 20))
            x += t.size[0] + 20
        sheet.save(out / f"{name}_sheet.png")
    print(f"{len(tiles)} stickers")


if __name__ == "__main__":
    main()
