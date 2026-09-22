"""Build a presenter's three reference images, landscape AND vertical, from one take.

    python veo_kit/make_refset.py --character veo_kit/characters/ritesh.json
    python veo_kit/make_refset.py --character ... --zoom       # find the shirt mark

WHAT A REFERENCE HAS TO BE
--------------------------
Everything here comes from Google's own guidance or from a generation that went
wrong, and docs/veo-prompt-research.md has the sources:

* THREE views of the one person: the face square-on, the head turned, and the
  build. Veo takes up to three images of a single subject, and every impostor
  it produced so far was slimmer, with a shorter beard and a fuller hairline, so
  the three views are chosen to pin exactly those.
* On a PLAIN background. The presenter is keyed off the HeyGen green screen onto
  flat mid-grey, so the model learns him and nothing else.
* Cropped to the ASPECT OF THE GENERATION. A landscape clip gets 1920x1080
  references and a vertical clip gets 1080x1920; a reference in the other shape
  pulls the framing towards itself.
* NO MARK ON THE SHIRT. A reference that carries lettering is a reference that
  asks for lettering, and Veo renders it as garbage. The chest wordmark and
  badge are painted out with the shirt's own colour and grain.

THE SHIRT MARK
--------------
Automatic removal (local contrast: a stroke is much brighter than the cloth
10px away, a fold highlight is not) gets most of it and not all. Whatever
survives is painted with an explicit rectangle, in SOURCE-frame pixels, listed
per shot as "paint" in the character json. Run with --zoom to get a gridded
close-up of each shot's chest and read the rectangle off it.
"""
from __future__ import annotations

import argparse
import io
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
from face_gate import _models  # noqa: E402

# Framing per shot kind, in units of the detected face box. `k` is the crop
# width in face-widths, `head` the headroom above the face in face-heights.
# The landscape numbers reproduce the set that passed review on 22 Sept 2026.
FRAMING = {
    "landscape": {"head": (5.4, 0.85), "body": (8.6, 0.70)},
    "vertical":  {"head": (3.2, 0.85), "body": (3.6, 0.70)},
}
SIZE = {"landscape": (1920, 1080), "vertical": (1080, 1920)}


def grab(clip: str, t: float) -> Image.Image:
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", clip,
                          "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-"],
                         capture_output=True).stdout
    if not raw:
        raise SystemExit(f"no frame at {t}s in {clip}")
    return Image.open(io.BytesIO(raw)).convert("RGB")


def key_to_grey(im: Image.Image, grey: tuple) -> Image.Image:
    """Hue key: the screen sits near 85 degrees and skin nowhere near it, so hue
    separates them where an RGB distance would eat into the face."""
    hsv = np.asarray(im.convert("HSV")).astype(float)
    h = hsv[..., 0] * 360 / 255
    s = hsv[..., 1] / 255
    v = hsv[..., 2] / 255
    bg = (h > 60) & (h < 125) & (s > 0.22) & (v > 0.18)
    a = (Image.fromarray(((~bg) * 255).astype(np.uint8))
         .filter(ImageFilter.MinFilter(5)).filter(ImageFilter.GaussianBlur(1.6)))
    rgb = np.asarray(im).astype(float)
    g = rgb[..., 1]
    mx = np.maximum(rgb[..., 0], rgb[..., 2])
    rgb[..., 1] = np.where(g > mx, mx, g)            # despill the green edge
    out = Image.new("RGB", im.size, grey)
    out.paste(Image.fromarray(rgb.astype(np.uint8)), (0, 0), a)
    return out


def face_box(im: Image.Image):
    boxes, _ = _models()["mtcnn"].detect(im)
    if boxes is None or not len(boxes):
        raise SystemExit("no face found in that frame — pick another time")
    return boxes[0]


def plain_shirt(im: Image.Image, fb, grey: tuple) -> tuple[Image.Image, int]:
    """Paint out sharp bright strokes on the torso (lettering), not soft folds."""
    fh = fb[3] - fb[1]
    a = np.asarray(im).astype(float)
    hsv = np.asarray(im.convert("HSV")).astype(float)
    h = hsv[..., 0] * 360 / 255
    s = hsv[..., 1] / 255
    v = hsv[..., 2] / 255
    fg = ~(np.abs(a - np.array(grey)).sum(axis=2) < 24)
    interior = np.asarray(Image.fromarray((fg * 255).astype(np.uint8))
                          .filter(ImageFilter.MinFilter(25))) > 0
    local = np.asarray(Image.fromarray((v * 255).astype(np.uint8))
                       .filter(ImageFilter.MedianFilter(21))).astype(float) / 255
    skin = (h < 55) & (s > 0.12) & (v > 0.22)
    torso = np.zeros_like(v, bool)
    torso[int(fb[3] + 0.5 * fh):, :] = True
    # NOT NEAR SKIN: a fingertip's pale edge is exactly a sharp bright stroke,
    # and painting it with shirt colour left dark blocks on his fingers.
    near_skin = np.asarray(Image.fromarray((skin * 255).astype(np.uint8))
                           .filter(ImageFilter.MaxFilter(15))) > 0
    mark = ((v - local) > 0.18) & interior & ~near_skin & torso
    dark = interior & torso & ~skin & (v < 0.22)
    if not dark.any():
        return im, 0
    mk = Image.fromarray((mark * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(11))
    cloth = tuple(int(x) for x in np.median(a[dark], axis=0))
    out = im.copy()
    out.paste(cloth, mask=mk.filter(ImageFilter.GaussianBlur(2.5)))
    return out, int(mark.sum())


def _skin(im: Image.Image) -> np.ndarray:
    hsv = np.asarray(im.convert("HSV")).astype(float)
    return ((hsv[..., 0] * 360 / 255 < 55) & (hsv[..., 1] / 255 > 0.12)
            & (hsv[..., 2] / 255 > 0.22))


def paint(im: Image.Image, rects: list, seed: int = 7) -> Image.Image:
    """Cover each rectangle with the shading AND grain of the cloth around it.

    The fill is DIFFUSED in from the rectangle's edges, so it carries the
    shirt's gradient across the patch. A flat median fill left a faint but
    visible box wherever the shirt was shaded, which is most of it. Grain is
    then added at the strength of the surrounding cloth's own fine texture.

    Learned on the turned shot, where the wordmark sits right against his hand:
      * SKIN IS NEVER PAINTED, and never used as a source. The rectangle may
        overlap a hand and can therefore be drawn generously.
      * THE GRAIN IS ONE CHANNEL. Independent noise per channel came out as
        coloured speckle."""
    rng = np.random.default_rng(seed)
    for x0, y0, x1, y1 in rects:
        a = np.asarray(im).astype(float)
        skin = _skin(im)
        m = 8
        X0, Y0 = max(0, x0 - m), max(0, y0 - m)
        X1, Y1 = min(im.width, x1 + m), min(im.height, y1 + m)
        sub = a[Y0:Y1, X0:X1].copy()
        sk = skin[Y0:Y1, X0:X1]
        hole = np.zeros(sk.shape, bool)
        hole[y0 - Y0:y1 - Y0, x0 - X0:x1 - X0] = True
        unknown = hole | sk
        known = ~unknown
        blur = np.asarray(Image.fromarray(sub.astype(np.uint8))
                          .filter(ImageFilter.GaussianBlur(2))).astype(float)
        # ROBUST, and capped: a seam or the edge of a hand inside the margin is
        # high-pass energy too, and a plain std turned it into a speckled box.
        hp = (sub - blur).mean(axis=2)[known]
        grain = min(2.5, 1.4826 * float(np.median(np.abs(hp)))) if hp.size else 1.5
        sub[unknown] = np.median(sub[known], axis=0)
        for _ in range(400):                          # heat equation, edges fixed
            q = np.pad(sub, ((1, 1), (1, 1), (0, 0)), mode="edge")
            avg = (q[:-2, 1:-1] + q[2:, 1:-1] + q[1:-1, :-2] + q[1:-1, 2:]) / 4
            sub[unknown] = avg[unknown]
        fill = sub[y0 - Y0:y1 - Y0, x0 - X0:x1 - X0]
        fill = np.clip(fill + rng.normal(0, 1, fill.shape[:2] + (1,)) * grain, 0, 255)
        mk = Image.new("L", (x1 - x0, y1 - y0), 0)
        ImageDraw.Draw(mk).rectangle((2, 2, x1 - x0 - 3, y1 - y0 - 3), fill=255)
        mk = np.asarray(mk.filter(ImageFilter.GaussianBlur(1.5))).astype(float)
        keep = np.asarray(Image.fromarray((skin[y0:y1, x0:x1] * 255).astype(np.uint8))
                          .filter(ImageFilter.MaxFilter(3))) > 0
        mk[keep] = 0
        im.paste(Image.fromarray(fill.astype(np.uint8)), (x0, y0),
                 Image.fromarray(mk.astype(np.uint8)))
    return im


def crop(im: Image.Image, fb, kind: str, aspect: str, grey: tuple) -> Image.Image:
    """Frame the shot for one aspect.

    The subject stands on flat grey, so the canvas can be extended with the same
    grey above and to the sides and nobody can see the join. NEVER below: the
    take cuts his body at the frame's bottom edge, and grey under that would
    show the cut as a floating torso. So a crop that runs off the bottom is
    slid up instead."""
    k, head = FRAMING[aspect][kind]
    W, H = SIZE[aspect]
    fw, fh = fb[2] - fb[0], fb[3] - fb[1]
    cx = (fb[0] + fb[2]) / 2
    w = int(k * fw)
    h = int(w * H / W)
    pad = max(w, h)
    canvas = Image.new("RGB", (im.width + 2 * pad, im.height + pad), grey)
    canvas.paste(im, (pad, pad))
    x0 = int(cx - w / 2) + pad
    y0 = int(fb[1] - head * fh) + pad
    y0 = min(y0, canvas.height - h)                  # slide up, never pad below
    return canvas.crop((x0, y0, x0 + w, y0 + h)).resize((W, H), Image.LANCZOS)


def chest_zoom(im: Image.Image, fb, path: Path) -> None:
    """A 2x close-up of the chest with a labelled pixel grid in SOURCE coords."""
    fw, fh = fb[2] - fb[0], fb[3] - fb[1]
    x0, y0 = int(fb[0] - 1.6 * fw), int(fb[3] + 0.4 * fh)
    x1, y1 = int(fb[2] + 1.6 * fw), int(fb[3] + 2.6 * fh)
    x0, y0 = max(0, x0), max(0, y0)
    x1, y1 = min(im.width, x1), min(im.height, y1)
    z = im.crop((x0, y0, x1, y1)).resize(((x1 - x0) * 2, (y1 - y0) * 2), Image.NEAREST)
    d = ImageDraw.Draw(z)
    for x in range((x0 // 50 + 1) * 50, x1, 50):
        d.line([((x - x0) * 2, 0), ((x - x0) * 2, z.height)], fill=(255, 0, 0))
        d.text(((x - x0) * 2 + 2, 2), str(x), fill=(255, 255, 0))
    for y in range((y0 // 50 + 1) * 50, y1, 50):
        d.line([(0, (y - y0) * 2), (z.width, (y - y0) * 2)], fill=(255, 0, 0))
        d.text((2, (y - y0) * 2 + 2), str(y), fill=(255, 255, 0))
    z.save(path)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--character", required=True)
    ap.add_argument("--aspect", choices=("both", "landscape", "vertical"), default="both")
    ap.add_argument("--zoom", action="store_true",
                    help="write a gridded chest close-up per shot and stop")
    ap.add_argument("--sheet", default="", help="contact sheet path (default: next to the refs)")
    a = ap.parse_args()

    ch = json.loads(Path(a.character).read_text(encoding="utf-8"))
    src = ch["source"]
    clip = str(ROOT / src["clip"])
    grey = tuple(src.get("grey", (128, 128, 128)))
    aspects = ("landscape", "vertical") if a.aspect == "both" else (a.aspect,)
    refs = {asp: [ROOT / p for p in ch["refs"][asp]] for asp in aspects}
    made = {asp: [] for asp in aspects}

    for i, shot in enumerate(src["shots"]):
        im = key_to_grey(grab(clip, shot["t"]), grey)
        fb = face_box(im)
        if a.zoom:
            first = next(iter(refs.values()))[0].parent
            first.mkdir(parents=True, exist_ok=True)
            p = first / f"_chest_{shot['name']}.png"
            chest_zoom(im, fb, p)
            print(f"  {shot['name']}: {p.relative_to(ROOT)}")
            continue
        im, n = plain_shirt(im, fb, grey)
        im = paint(im, shot.get("paint", []))
        for asp in aspects:
            out = refs[asp][i]
            out.parent.mkdir(parents=True, exist_ok=True)
            crop(im, fb, shot["kind"], asp, grey).save(out)
            made[asp].append(out)
        print(f"  {shot['name']:<14} t={shot['t']:>5}s  face {int(fb[2] - fb[0])}px  "
              f"{n} stroke px auto-painted, {len(shot.get('paint', []))} rect(s)")
    if a.zoom:
        print("\n  read each mark's rectangle off the grid (source pixels) into the\n"
              "  shot's \"paint\" list, e.g. \"paint\": [[963, 719, 1013, 768]]")
        return 0

    # One contact sheet per aspect, so the set is looked at before it is used.
    for asp, files in made.items():
        W, H = (480, 270) if asp == "landscape" else (270, 480)
        sh = Image.new("RGB", (W * len(files), H), "#111")
        for j, f in enumerate(files):
            sh.paste(Image.open(f).resize((W, H)), (j * W, 0))
        p = Path(a.sheet) if a.sheet else files[0].parent / "_sheet.png"
        sh.save(p)
        print(f"  {asp}: {', '.join(f.name for f in files)}  -> look at {p.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
