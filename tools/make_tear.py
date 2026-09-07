"""Key the paper-tear divider out of the supplied photograph.

    python tools/make_tear.py --seam 810 [--out assets/dividers/paper_tear_810.png]

WHY THIS EXISTS
---------------
The divider used to be a drawn sine wave. It read as patchy and too thick, and
no amount of tuning made a drawn line look like a torn edge. This keys the real
thing out of `paper_tear_texture.jpg` (a white strip on black) instead.

Two decisions are load-bearing:

MIRROR-TILE, don't repeat. The photo is 626px wide and the frame is 1080. A
plain tile shows an obvious repeat at the seam; mirroring makes the edges match
exactly there, so the join is continuous and invisible on a ragged edge.

PLACE BY THE DEEPEST POINT OF THE RIP, not by the strip's centre. The panel
above ends on a straight line at `seam`. If the paper is centred there, every
column where the rip runs BELOW the seam shows a stripe of bare plate between
the panel and the paper, and it reads as a gap rather than a tear. Anchoring the
rip's lowest top-edge pixel to the seam guarantees the paper always has panel
above it, everywhere, and the visible bottom edge of the panel becomes the rip.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageFilter

SRC = Path("assets/dividers/paper_tear_texture.jpg")
W, H = 1080, 1920
UPSCALE = 1.30          # so the fibre detail still reads at 1080 wide
TONE = (244, 241, 232)  # warm off-white; pure white glares against the plate


def build(seam: int, src: Path = SRC) -> tuple[Image.Image, dict]:
    g = Image.open(src).convert("L")
    g = g.resize((int(g.width * UPSCALE), int(g.height * UPSCALE)), Image.LANCZOS)
    tile = Image.new("L", (g.width * 2, g.height))
    tile.paste(g, (0, 0))
    tile.paste(g.transpose(Image.FLIP_LEFT_RIGHT), (g.width, 0))
    x0 = (tile.width - W) // 2
    strip = tile.crop((x0, 0, x0 + W, g.height))

    a = np.asarray(strip).astype(np.float32)
    alpha = np.clip((a - 26) / 46.0, 0, 1)

    rows = np.where(alpha.max(axis=1) > 0.5)[0]
    top_edge = np.array([(np.where(alpha[:, x] > 0.5)[0][:1] or [rows[-1]])[0]
                         for x in range(W)])
    off = seam - int(top_edge.max())          # deepest point of the rip on the seam

    canvas = np.zeros((H, W, 4), dtype=np.float32)
    shade = (np.clip(a / 255.0 * 0.45 + 0.55, 0, 1))[..., None]
    dst = slice(max(0, off), min(H, off + alpha.shape[0]))
    src_s = slice(max(0, -off), max(0, -off) + (dst.stop - dst.start))
    canvas[dst, :, :3] = np.array(TONE, dtype=np.float32) * shade[src_s]
    canvas[dst, :, 3] = alpha[src_s] * 255

    img = Image.fromarray(canvas.astype(np.uint8), "RGBA")
    sh = Image.fromarray(canvas[..., 3].astype(np.uint8), "L").filter(ImageFilter.GaussianBlur(9))
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shadow.putalpha(ImageChops.offset(sh, 0, 10).point(lambda v: int(v * 0.55)))
    img = Image.alpha_composite(shadow, img)

    # The rows the finished image (paper AND its shadow) actually touches. The
    # compositor runs a per-pixel expression over this band to make the rip
    # travel, so handing it the whole 1080x1920 canvas costs eleven times more
    # than it needs to for pixels that are transparent everywhere.
    a = np.asarray(img)[..., 3]
    used = np.where(a.max(axis=1) > 2)[0]
    band_top = int(max(0, used[0] - 2))
    band_h = int(min(H - band_top, used[-1] - band_top + 4))
    meta = {"seam": seam, "rip_top": int(off + top_edge.min()), "rip_bottom": seam,
            "paper_bottom": int(off + rows[-1]), "band": [band_top, band_h],
            "source": src.name}
    return img, meta


def fade_mask(panel_h: int, fade: int) -> Image.Image:
    """A white panel whose top `fade` rows ramp up from black.

    The panel's top edge dissolves into the plate. That ramp is a function of Y
    ALONE, so it is a picture, not a per-pixel expression: baking it once and
    multiplying is ~800x cheaper per frame than asking geq for it, and the
    compositor is already the slowest stage in the pipeline.
    """
    col = np.clip(np.arange(panel_h, dtype=np.float32) / max(fade, 1), 0, 1) * 255
    return Image.fromarray(np.repeat(col[:, None], W, axis=1).astype(np.uint8), "L")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seam", type=int)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--src", type=Path, default=SRC)
    ap.add_argument("--fade-for", type=int, help="also write the panel fade mask "
                    "for a panel of this height")
    ap.add_argument("--fade-rows", type=int, default=150)
    ap.add_argument("--fade-only", action="store_true",
                    help="write only the fade mask, not the divider")
    args = ap.parse_args()
    if not args.fade_only:
        if args.seam is None:
            ap.error("--seam is required unless --fade-only")
        out = args.out or Path(f"assets/dividers/paper_tear_{args.seam}.png")
        img, meta = build(args.seam, args.src)
        out.parent.mkdir(parents=True, exist_ok=True)
        img.save(out)
        out.with_suffix(".json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
        print(f"  {out}  rip {meta['rip_top']}..{meta['rip_bottom']}, "
              f"paper ends {meta['paper_bottom']}")
    if args.fade_for:
        f = Path(f"assets/dividers/panel_fade_{args.fade_for}.png")
        f.parent.mkdir(parents=True, exist_ok=True)
        fade_mask(args.fade_for, args.fade_rows).save(f)
        print(f"  {f}  top {args.fade_rows} rows ramp in")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
