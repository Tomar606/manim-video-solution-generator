"""Find the chroma-key parameters for one presenter clip.

Run this for every new shoot. The numbers are not portable: the three clips
handled so far needed three different value references, and reusing another
clip's settings puts holes in the face or leaves green in the background.

WHY THE KEY IS HUE-BASED, not `chromakey`
-----------------------------------------
The green screen is lit unevenly — measured value ranges 0.67 to 0.99 across a
single frame. An RGB-distance key wide enough to cover the dark side of the
screen also matches skin midtones, and it punched holes through 8.3% of the
presenter: the background was visibly showing through his face. Widening or
narrowing the tolerance only trades one failure for the other.

Hue does not drift with the lighting. The screen sits at 85-90 degrees in every
clip while the subject's hue is nowhere near it (measured 2, 209, 354). So the
key is `hsvkey` on hue, and the value reference is what this script tunes.

WHY IT KEYS TWICE
-----------------
One key still cannot span the whole brightness range: set for the bright corner
it leaves an olive smudge in the dark one, set for the dark corner it eats the
subject. Two keys at different value references, combined with `blend=darken`
(transparent if EITHER says background), covers both ends.

The two failure modes are measured directly against the frame, with the ground
truth taken from hue: `subject` is far from the key hue and saturated, `bg` is
within a few degrees of it. Both masks are eroded so the soft edge between them
is excluded from scoring.
"""
from __future__ import annotations

import io
import json
import subprocess
import sys

import numpy as np
from PIL import Image, ImageFilter

CROP = "crop=650:930:650:150"          # the presenter inside a 1920x1080 plate
POST = ("dilation,dilation,erosion,erosion,eq=contrast=2.2:brightness=-0.10,"
        "erosion,erosion,gblur=sigma=1.0")


def graph(hue, sat, v1, v2, sim):
    k = (f"hsvkey=hue={hue}:sat={sat}:val=%s:similarity={sim}:blend=0.05,"
         f"format=rgba,alphaextract")
    return (f"[0:v]{CROP},format=rgba,split=2[d1][d2];"
            f"[d1]{k % v1}[a1];[d2]{k % v2}[a2];"
            f"[a1][a2]blend=all_mode=darken,{POST}[out]")


def _frame(src, t, vf=None, fc=None):
    cmd = ["ffmpeg", "-v", "error", "-ss", str(t), "-i", src, "-frames:v", "1"]
    cmd += ["-vf", vf] if vf else ["-filter_complex", fc, "-map", "[out]"]
    cmd += ["-f", "image2pipe", "-vcodec", "png", "-"]
    raw = subprocess.run(cmd, capture_output=True).stdout
    return Image.open(io.BytesIO(raw)) if raw else None


def _hsv(a):
    R, G, B = a[..., 0], a[..., 1], a[..., 2]
    mx, mn = a.max(2), a.min(2)
    d = mx - mn + 1e-6
    hue = np.where(mx == G, 60 * (2 + (B - R) / d),
                   np.where(mx == R, (60 * ((G - B) / d)) % 360, 60 * (4 + (R - G) / d)))
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1), 0)
    return hue, sat, mx / 255


def truth(src, t, key_hue=89.0):
    im = _frame(src, t, vf=CROP)
    if im is None:
        return None
    a = np.asarray(im.convert("RGB")).astype(float)
    hue, sat, val = _hsv(a)
    dh = np.minimum(np.abs(hue - key_hue), 360 - np.abs(hue - key_hue))
    er = lambda m, k: np.asarray(
        Image.fromarray((m * 255).astype("uint8")).filter(ImageFilter.MinFilter(k))) > 127
    return (er((dh > 40) & (sat > 0.12), 11), er(dh < 6, 11),
            float(np.median(hue[dh < 5])), float(np.median(sat[dh < 5])))


def calibrate(src, out=None, times=(14, 38, 54, 70, 86)):
    truths = {t: truth(src, t) for t in times}
    truths = {t: v for t, v in truths.items() if v}
    if not truths:
        raise SystemExit(f"could not read frames from {src}")
    hue = round(float(np.median([v[2] for v in truths.values()])), 2)
    sat = round(float(np.median([v[3] for v in truths.values()])), 2)
    print(f"{src}: key hue={hue} sat={sat}, {len(truths)} sample frames")

    best = None
    for sim in (0.34, 0.38, 0.42, 0.46):
        for v1 in (0.58, 0.62, 0.66):
            for v2 in (0.74, 0.78, 0.82):
                fc = graph(hue, sat, v1, v2, sim)
                holes, leaks = [], []
                for t, (sj, bg, _, _) in truths.items():
                    im = _frame(src, t, fc=fc)
                    if im is None:
                        break
                    al = np.asarray(im.convert("L")).astype(int)
                    holes.append((al[sj] < 235).mean() * 100)
                    leaks.append((al[bg] > 20).mean() * 100)
                if len(holes) != len(truths):
                    continue
                # a hole is what a viewer notices; weight it far above a leak
                cost = max(holes) * 4 + max(leaks)
                if best is None or cost < best[0]:
                    best = (cost, dict(hue=hue, sat=sat, v1=v1, v2=v2, sim=sim,
                                       hole=round(max(holes), 4),
                                       leak=round(max(leaks), 4)))
                    print(f"  v1={v1} v2={v2} sim={sim}  "
                          f"hole={max(holes):.3f}% leak={max(leaks):.3f}%")
    if out:
        json.dump(best[1], open(out, "w"), indent=2)
    print(f"-> {best[1]}")
    return best[1]


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    calibrate(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
