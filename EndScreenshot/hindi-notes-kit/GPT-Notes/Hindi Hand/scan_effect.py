#!/usr/bin/env python3
"""Scanned post-processing for Bio Ch1 — TONED-DOWN, UNIFORM version.

Same deterministic-per-seed structure as the maths chapters' scan_effect, but the
heavy "wear & tear" was dialled WAY down at the user's request: the notes should look
like a CLEAN, EVENLY-SCANNED notebook page — still handwritten, still a real scan, but
NOT beaten-up. The goal is UNIFORMITY across every page (all pages should feel scanned
on the same machine on the same day) while keeping the text/diagrams crisp.

What changed vs the maths scan_effect:
  * NO heavy "photo" capture mode (photo is effectively off) — every page is a flat scan.
  * Physical damage (water rings, grease smudges, ink streaks, faded patches, stray
    doodles, dog-ears, torn nibbles, old tape) is REMOVED or reduced to near-zero, so no
    single page stands out as "the damaged one".
  * Foxing/age-spots and creases kept only as a very light, occasional whisper.
  * Warm paper tone, uneven lighting, vignette, binding shadow, grain kept but GENTLER
    and in a narrow range so all pages match.
  * Soft focus stays light (crisp text). JPEG quality kept high.

Public API unchanged:  scan_effect(img, seed, wear_boost) -> PIL.Image
so gen_final.py needs no changes.

CLI:
    python scan_effect.py INPUT.png OUTPUT.jpg [--seed N] [--wear 0.5]
    python scan_effect.py INPUT.png OUTPUT.jpg --chapter "Bio Ch1 SRFP" --page 2
"""
from __future__ import annotations
import argparse, io, zlib
import random
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageChops

PAPER = (247, 246, 242)


# ---------- helpers ----------
def _find_coeffs(src, dst):
    """Perspective coeffs mapping dst quad -> src quad (for Image.transform)."""
    matrix = []
    for (sx, sy), (dx, dy) in zip(src, dst):
        matrix.append([dx, dy, 1, 0, 0, 0, -sx * dx, -sx * dy])
        matrix.append([0, 0, 0, dx, dy, 1, -sy * dx, -sy * dy])
    A = [row[:] for row in matrix]
    b = [s for pt in src for s in pt]
    n = 8
    for i in range(n):
        piv = max(range(i, n), key=lambda k: abs(A[k][i]))
        A[i], A[piv] = A[piv], A[i]
        b[i], b[piv] = b[piv], b[i]
        d = A[i][i] or 1e-9
        for j in range(i, n):
            A[i][j] /= d
        b[i] /= d
        for k in range(n):
            if k == i:
                continue
            f = A[k][i]
            for j in range(i, n):
                A[k][j] -= f * A[i][j]
            b[k] -= f * b[i]
    return b


def _overlay(base, top, alpha):
    try:
        blended = ImageChops.overlay(base, top)
    except Exception:
        blended = top
    return Image.blend(base, blended, alpha)


def _grad_mask(size, horizontal, dark_side_low, strength, blur):
    """Grey gradient (255=no change) darkening one side by `strength`."""
    W, H = size
    m = Image.new("L", size, 255)
    px = m.load()
    span = W if horizontal else H
    for i in range(span):
        t = i / max(1, span - 1)
        if not dark_side_low:
            t = 1 - t
        val = int(255 - strength * t)
        if horizontal:
            for y in range(H):
                px[i, y] = val
        else:
            for x in range(W):
                px[x, i] = val
    return m.filter(ImageFilter.GaussianBlur(blur))


# ---------- main effect ----------
def scan_effect(img: Image.Image, seed: int, wear_boost: float = 0.5) -> Image.Image:
    """wear_boost defaults LOW (0.5) here; heavy artifacts are already near-zero."""
    r = random.Random(seed)
    img = img.convert("RGB")
    W, H = img.size
    # Heavy "photo" capture is essentially OFF for uniformity — flat scan on every page.
    photo = r.random() < 0.03

    def fires(p):
        return r.random() < min(1.0, p * wear_boost)

    def layer():
        return Image.new("RGBA", (W, H), (0, 0, 0, 0))

    def comp(lyr):
        nonlocal img
        img = Image.alpha_composite(img.convert("RGBA"), lyr).convert("RGB")

    # ============ A) LIGHT AGE ONLY (uniform, subtle) ============
    # A faint whisper of foxing on some pages — small, pale, easy to miss. No stains,
    # no smudges, no streaks, no doodles, no tears, no tape, no dog-ears (all removed).
    if fires(0.28):
        L = layer(); d = ImageDraw.Draw(L)
        for _ in range(r.randint(3, 7)):
            cx, cy = r.randint(0, W), r.randint(0, H)
            rad = r.randint(2, 7)
            d.ellipse([cx - rad, cy - rad, cx + rad, cy + rad],
                      fill=(150, 120, 75, r.randint(8, 20)))
        comp(L.filter(ImageFilter.GaussianBlur(2)))

    # A single very soft crease, only occasionally, kept subtle.
    if fires(0.18):
        L = layer(); d = ImageDraw.Draw(L)
        vertical = r.random() < 0.5
        pos = r.randint(int(W * 0.25), int(W * 0.75)) if vertical else r.randint(int(H * 0.25), int(H * 0.75))
        if vertical:
            d.line([pos, 0, pos + r.randint(-16, 16), H], fill=(255, 255, 255, 34), width=2)
            d.line([pos + 3, 0, pos + 3 + r.randint(-16, 16), H], fill=(60, 55, 50, 26), width=2)
        else:
            d.line([0, pos, W, pos + r.randint(-16, 16)], fill=(255, 255, 255, 34), width=2)
            d.line([0, pos + 3, W, pos + 3 + r.randint(-16, 16)], fill=(60, 55, 50, 26), width=2)
        comp(L.filter(ImageFilter.GaussianBlur(1)))

    # ============ B) SCANNING CAPTURE (gentle, uniform) ============
    # Elastic micro-warp (breaks pixel-identical letterforms) — kept, it is subtle.
    img = _elastic_warp(img, r, W, H)

    # Perspective — tiny, rare (kept flat for a scanner look).
    if photo or (r.random() < 0.10):
        amt = W * (r.uniform(0.010, 0.020) if photo else r.uniform(0.003, 0.008))
        def j():
            return r.uniform(-amt, amt)
        dst = [(0, 0), (W, 0), (W, H), (0, H)]
        src = [(j(), j()), (W + j(), j()), (W + j(), H + j()), (j(), H + j())]
        coeffs = _find_coeffs(src, dst)
        img = img.transform((W, H), Image.PERSPECTIVE, coeffs,
                            Image.BICUBIC, fillcolor=PAPER)

    # Brightness / Contrast / Colour — narrow ranges so pages match each other.
    img = ImageEnhance.Brightness(img).enhance(r.uniform(0.94, 1.06))
    img = ImageEnhance.Contrast(img).enhance(r.uniform(0.95, 1.08))
    img = ImageEnhance.Color(img).enhance(r.uniform(0.94, 1.02))

    # Warm paper tone (always warm, gentle, narrow).
    warm = r.uniform(0.25, 0.55)
    rr, gg, bb = img.split()
    rr = rr.point(lambda v: min(255, v * (1 + 0.030 * warm)))
    gg = gg.point(lambda v: min(255, v * (1 + 0.015 * warm)))
    bb = bb.point(lambda v: v * (1 - 0.040 * warm))
    img = Image.merge("RGB", (rr, gg, bb))

    # Uneven lighting: very gentle one-side falloff.
    strength = r.uniform(16, 34)
    m = _grad_mask((W, H), horizontal=r.random() < 0.5,
                   dark_side_low=r.random() < 0.5, strength=strength, blur=70)
    img = ImageChops.multiply(img, Image.merge("RGB", (m, m, m)))

    # Show-through (faint mirror of the reverse side) — barely there.
    mirror = img.transpose(Image.FLIP_LEFT_RIGHT)
    mirror = Image.blend(mirror, Image.new("RGB", (W, H), (255, 255, 255)), 0.85)
    img = Image.blend(img, mirror, r.uniform(0.03, 0.06))

    # Vignette — soft, narrow.
    vig = Image.new("L", (W, H), 0)
    ImageDraw.Draw(vig).ellipse([-W * 0.12, -H * 0.12, W * 1.12, H * 1.12], fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(120))
    dark = r.uniform(12, 26)
    vig = vig.point(lambda v: int(255 - (255 - v) / 255 * dark))
    img = ImageChops.multiply(img, Image.merge("RGB", (vig, vig, vig)))

    # Binding / gutter shadow down one edge — present but light (spiral side).
    if r.random() < 0.9:
        bw = int(W * r.uniform(0.12, 0.20))
        left = True  # spiral binding is on the left of paper.png
        s = r.uniform(26, 46)
        band = Image.new("L", (W, H), 255); px = band.load()
        for x in range(bw):
            t = 1 - x / max(1, bw)
            val = int(255 - s * t)
            xx = x if left else W - 1 - x
            for y in range(H):
                px[xx, y] = val
        band = band.filter(ImageFilter.GaussianBlur(18))
        img = ImageChops.multiply(img, Image.merge("RGB", (band, band, band)))

    # Worn edges frame — very light darkening at the extreme border only.
    frame = Image.new("L", (W, H), 255)
    fd = ImageDraw.Draw(frame)
    fw = r.uniform(6, 12)
    fd.rectangle([0, 0, W - 1, H - 1], outline=int(255 - fw * 6), width=int(5 + fw / 4))
    frame = frame.filter(ImageFilter.GaussianBlur(10))
    img = ImageChops.multiply(img, Image.merge("RGB", (frame, frame, frame)))

    # A few fine specks + one dust hair — sparse, so pages stay clean.
    L = layer(); d = ImageDraw.Draw(L)
    for _ in range(r.randint(6, 16)):
        x, y = r.randint(0, W), r.randint(0, H)
        rad = r.randint(1, 3); g = r.randint(140, 205)
        d.ellipse([x, y, x + rad, y + rad], fill=(g, g, g, 170))
    if r.random() < 0.5:
        x, y = r.randint(0, W), r.randint(0, H)
        pts = [(x, y)]
        for _ in range(r.randint(5, 10)):
            x += r.randint(-6, 6); y += r.randint(-6, 6); pts.append((x, y))
        d.line(pts, fill=(150, 150, 150, 120), width=1)
    comp(L)

    # Chromatic aberration — essentially off (it softens edges); rare + 1px only.
    if r.random() < 0.15:
        rr, gg, bb = img.split()
        rr = ImageChops.offset(rr, 1, 0)
        bb = ImageChops.offset(bb, -1, 0)
        img = Image.merge("RGB", (rr, gg, bb))

    # Blotchy paper texture (low-freq) — subtle, uniform, does not blur the ink.
    small = Image.effect_noise((max(1, W // 12), max(1, H // 12)), 12).resize((W, H))
    small = small.filter(ImageFilter.GaussianBlur(8)).point(lambda v: 222 + v // 8)
    img = ImageChops.multiply(img, Image.merge("RGB", (small, small, small)))

    # Scanner grain (fine) — very light overlay so text stays crisp.
    grain = Image.effect_noise((W, H), r.randint(6, 10)).convert("RGB")
    img = _overlay(img, grain, r.uniform(0.04, 0.08))

    # Soft focus — OFF for crisp text/diagrams (only the rare "photo" page gets a whisper).
    if photo:
        img = img.filter(ImageFilter.GaussianBlur(r.uniform(0.10, 0.22)))

    # Light sharpening pass to keep the handwriting/pencil edges clean after resampling.
    img = img.filter(ImageFilter.UnsharpMask(radius=1.2, percent=70, threshold=2))

    # Skew — tiny, so pages sit almost straight and uniform.
    img = img.rotate(r.uniform(-0.6, 0.6), resample=Image.BICUBIC, fillcolor=PAPER)

    # JPEG round-trip (authentic scan artifact) — high quality, crisp.
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=r.randint(92, 96))
    buf.seek(0)
    return Image.open(buf).convert("RGB")


def _elastic_warp(im, r, W, H, cols=6, rows=8):
    dx, dy = W / cols, H / rows
    pts = {}
    for gy in range(rows + 1):
        for gx in range(cols + 1):
            x, y = gx * dx, gy * dy
            if 0 < gx < cols:
                x += r.uniform(0.4, 1.0) * r.choice([-1, 1])
            if 0 < gy < rows:
                y += r.uniform(0.4, 1.0) * r.choice([-1, 1])
            pts[(gx, gy)] = (x, y)
    mesh = []
    for gy in range(rows):
        for gx in range(cols):
            box = (int(gx * dx), int(gy * dy), int((gx + 1) * dx), int((gy + 1) * dy))
            nw, ne = pts[(gx, gy)], pts[(gx + 1, gy)]
            se, sw = pts[(gx + 1, gy + 1)], pts[(gx, gy + 1)]
            quad = (nw[0], nw[1], sw[0], sw[1], se[0], se[1], ne[0], ne[1])
            mesh.append((box, quad))
    return im.transform((W, H), Image.MESH, mesh, Image.BILINEAR, fillcolor=PAPER)


def _seed_for(chapter, page):
    return zlib.crc32(f"{chapter}|{page}".encode())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("output")
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--wear", type=float, default=0.5)
    ap.add_argument("--chapter", default=None)
    ap.add_argument("--page", default=None)
    a = ap.parse_args()
    if a.seed is not None:
        seed = a.seed
    elif a.chapter is not None and a.page is not None:
        seed = _seed_for(a.chapter, a.page)
    else:
        seed = zlib.crc32(a.input.encode())
    out = scan_effect(Image.open(a.input), seed=seed, wear_boost=a.wear)
    out.save(a.output, format="JPEG", quality=92)
    print(f"saved {a.output}  (seed={seed}, wear={a.wear})")


if __name__ == "__main__":
    main()
