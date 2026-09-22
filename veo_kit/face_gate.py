"""Refuse a video whose presenter is not the real man, by measured face similarity.

    python veo_kit/face_gate.py <video.mp4> [--at 2 6 10] [--min 0.90]
    python veo_kit/face_gate.py <final.mp4> --spread 7     # 7 frames, 12%-88% of it
    python veo_kit/face_gate.py <clip.mp4> --character veo_kit/characters/ritesh.json
    python veo_kit/face_gate.py --calibrate            # show the separation

WHY A NUMBER AND NOT AN OPINION
-------------------------------
A vision model asked whether a frame shows our presenter whether a frame shows our presenter and
it answers well, but "90% similar" is not something a written judgement can
honestly report. This measures it: MTCNN finds the face, InceptionResnetV1
(VGGFace2) embeds it as a 512-vector, and the score is the cosine similarity to
the reference photograph. Same person, different lighting and pose, scores high;
a different bearded man in the same polo scores low. That is the whole point —
"a bearded Indian man in black" is not the test, because the clips that failed
all matched that description.

THE THRESHOLD IS CALIBRATED, NOT PICKED
---------------------------------------
Run --calibrate. It scores frames of the real presenter (HeyGen composites,
which ARE him) against frames of the two generated impostors in HIS-C2-SA-06,
and prints both distributions. Set --min inside the gap. A number chosen without
looking at that separation is a number that fails honest clips and passes
strangers.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

REFERENCE = ROOT / "assets" / "character" / "ritesh_reference.jpeg"
DEFAULT_CHARACTER = Path(__file__).resolve().parent / "characters" / "ritesh.json"
_MODELS = {}


def _models():
    if not _MODELS:
        import torch
        from facenet_pytorch import MTCNN, InceptionResnetV1
        _MODELS["torch"] = torch
        _MODELS["mtcnn"] = MTCNN(image_size=160, margin=24, post_process=True,
                                 select_largest=True, device="cpu")
        _MODELS["net"] = InceptionResnetV1(pretrained="vggface2").eval()
    return _MODELS


MIN_PROB = 0.95        # below this it is not confidently a face
MIN_FACE = 120         # px on the long side, on a 1920-tall frame


def embed(img: Image.Image):
    """512-vector for the largest CONFIDENT face, or None.

    The size and probability floors are not fussiness. Without them MTCNN
    returned a 92x131 box at probability 0.87 on a raised HAND and the frame
    scored 0.030 against the reference — a number that says "different person"
    about a hand. A face that small in a 1080x1920 frame is not the presenter
    anyway; he fills a third of the height.
    """
    m = _models()
    rgb = img.convert("RGB")
    boxes, probs = m["mtcnn"].detect(rgb)
    if boxes is None or not len(boxes):
        return None
    best = None
    for b, pr in zip(boxes, probs):
        if pr is None or pr < MIN_PROB:
            continue
        side = max(b[2] - b[0], b[3] - b[1])
        if side < MIN_FACE:
            continue
        if best is None or side > best[1]:
            best = (b, side)
    if best is None:
        return None
    # Crop and normalise by hand: MTCNN.extract wants a batch and a save path,
    # and the one-box call signature is awkward. This is what it does anyway —
    # square-ish crop with margin, 160x160, fixed image standardisation.
    b = best[0]
    mx = 0.15 * (b[2] - b[0])
    box = (max(0, int(b[0] - mx)), max(0, int(b[1] - mx)),
           min(rgb.width, int(b[2] + mx)), min(rgb.height, int(b[3] + mx)))
    crop = rgb.crop(box).resize((160, 160), Image.BILINEAR)
    arr = np.asarray(crop).astype(np.float32)
    t = m["torch"].from_numpy(arr).permute(2, 0, 1)
    face = (t - 127.5) / 128.0
    with m["torch"].no_grad():
        v = m["net"](face.unsqueeze(0))[0].numpy()
    return v / (np.linalg.norm(v) + 1e-9)


def grab(video: str, t: float) -> Image.Image | None:
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-ss", str(t), "-i", str(video), "-frames:v", "1",
         "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True).stdout
    if not raw:
        return None
    import io
    return Image.open(io.BytesIO(raw))


def score_video(video: str, times: list[float], ref) -> list[tuple[float, float | None]]:
    out = []
    for t in times:
        im = grab(video, t)
        v = embed(im) if im is not None else None
        out.append((t, None if v is None else float(np.dot(ref, v))))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("video", nargs="?")
    ap.add_argument("--at", type=float, nargs="*", default=[2.0, 6.0, 10.0])
    ap.add_argument("--spread", type=int, default=0,
                    help="sample N frames evenly from 12%% to 88%% of the video "
                         "(what tools/gates.py does on a finished video); overrides --at")
    ap.add_argument("--min", type=float, default=None,
                    help="default: the character's face_min, else 0.90")
    ap.add_argument("--character", default=str(DEFAULT_CHARACTER),
                    help="character json; its face_reference is what is matched")
    ap.add_argument("--ref", default="", help="a reference photo, overriding --character")
    ap.add_argument("--calibrate", action="store_true")
    a = ap.parse_args()

    reference, floor = REFERENCE, 0.90
    if Path(a.character).is_file():
        ch = json.loads(Path(a.character).read_text(encoding="utf-8"))
        reference = ROOT / ch.get("face_reference", reference)
        floor = float(ch.get("face_min", floor))
    if a.ref:
        reference = Path(a.ref)
    if a.min is None:
        a.min = floor
    if not reference.is_file():
        print(f"  ! no reference at {reference} — "
              f"see veo_kit/SETUP.md, step 3")
        return 1
    ref = embed(Image.open(reference))
    if ref is None:
        print("  ! no face found in the reference")
        return 1

    if a.calibrate:
        print("  KNOWN HIM (composited HeyGen takes):")
        for v, ts in (("projects/his-c2-sa-06/final/his_c2_sa_06.mp4", [60, 75, 95]),
                      ("projects/che-c2-sa-01/final/che_c2_sa_01.mp4", [30, 70, 110]),
                      ("projects/che-c3-sa-10/final/che_c3_sa_10.mp4", [30, 60, 95])):
            if not Path(v).is_file():
                continue
            for t, s in score_video(v, ts, ref):
                print(f"    {Path(v).name:<22} {t:5.0f}s  "
                      + ("no face" if s is None else f"{s:+.3f}"))
        print("  KNOWN NOT HIM (generated clips in HIS-C2-SA-06):")
        for t, s in score_video("projects/his-c2-sa-06/final/his_c2_sa_06.mp4",
                                [8, 12, 28, 30, 34], ref):
            print(f"    {'his_c2_sa_06.mp4':<22} {t:5.0f}s  "
                  + ("no face" if s is None else f"{s:+.3f}"))
        return 0

    if not a.video:
        ap.error("give a video, or --calibrate")
    if a.spread:
        dur = float(subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "csv=p=0", a.video], capture_output=True, text=True).stdout or 0)
        n = max(3, a.spread)
        a.at = [round(dur * (0.12 + 0.76 * i / (n - 1)), 1) for i in range(n)]
    rows = score_video(a.video, a.at, ref)
    seen = [s for _, s in rows if s is not None]
    print(f"  {Path(a.video).name}  (threshold {a.min:.2f} on the median)")
    for t, s in rows:
        if s is None:
            print(f"    {t:6.1f}s  no usable face")
            continue
        print(f"    {t:6.1f}s  {s:+.3f}")
    if len(seen) < 3:
        print(f"  FACE GATE FAILED — only {len(seen)} usable face(s); "
              f"sample more frames with --at")
        return 1
    # THE MEDIAN, NOT THE WORST. He turns his head, purses his lips mid-word and
    # puts a hand in front of his chin; one such frame scored 0.700 and is still
    # unmistakably him. Identity is what the frames agree on.
    med = float(np.median(seen))
    print(f"  median {med:.3f} over {len(seen)} frame(s), "
          f"range {min(seen):.3f}..{max(seen):.3f}")
    if med < a.min:
        print(f"  FACE GATE FAILED — {med:.3f} < {a.min:.2f}: this is not him")
        return 1
    print(f"  face ok: {med:.3f} >= {a.min:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
