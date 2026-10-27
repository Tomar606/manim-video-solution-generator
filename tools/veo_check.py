"""The mechanical checks a generated clip must pass before a person ever looks at it.

    python tools/veo_check.py <clip.mp4> [...]        # prints each clip's verdict

Only faults a machine can measure reliably are rejected here; what a clip MEANS (the right subject, the
process running the right way, nothing the answer contradicts) is still judged by eye on veo/contact.jpg
and on the frames review. A false reject costs a regeneration, never quality.

  * SHAPE: a landscape clip, or one much shorter than Flow's 8 seconds.
  * SPLIT SCREEN: two shots stacked or side by side. Veo does this despite "one single continuous shot"
    and "no split screen" in the prompt (HIS-C7-SA-01 h1, CHE-C1-SA-02 e1, 27 Oct 2026). The seam is a
    straight line across most of the frame that stays at the same height while the camera moves, and it is a
    CUT: the picture jumps within a pixel, nothing continues across it, and it is ruler-straight. A horizon
    in a still shot also stays put, but it is soft, or things run through it, or it wanders a pixel or two
    along its length (see line_features for the measurements on real splits and horizons).
  * TEXT: lettering big enough to read (a caption, a sign, a title). The small scribble on an exam booklet,
    which every exam-hall clip has, is below the size floor. Needs RapidOCR (requirements-tools.txt); without
    it the check is skipped and says so.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np

SAMPLES = 8              # frames looked at per clip, spread over its length
GW, GH = 540, 960        # the split-screen check works at this size
SEAM_COVER = 0.60        # a candidate seam: the picture changes across the line along this much of it...
SEAM_FRAMES = 0.75       # ...at the same place in this fraction of the sampled frames
SEAM_SHARP = 6.0         # a seam is a cut: the step across it is this many times the steps beside it
SEAM_CORR = 0.30         # and nothing continues across it (structure either side correlates below this)
SEAM_STRAIGHT = 0.75     # and it is ruler-straight: this fraction of columns step at the very same row
TEXT_MIN_H = 0.028       # lettering this tall (of the frame height) or taller counts
TEXT_MIN_CHARS = 3
TEXT_MIN_SCORE = 0.80


def probe(f: Path) -> tuple[int, int, float]:
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                          "-show_entries", "format=duration", "-of", "json", str(f)], capture_output=True, text=True).stdout
    d = json.loads(out or "{}")
    if not d.get("streams"):
        raise ValueError(f"{f.name} is not a readable video")
    return d["streams"][0]["width"], d["streams"][0]["height"], float(d["format"]["duration"])


def frames(clip: Path, w: int, h: int, n: int, gray: bool) -> list[np.ndarray]:
    _, _, d = probe(clip)
    out = []
    for k in range(n):
        t = d * (0.06 + 0.88 * k / max(1, n - 1))
        raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.2f}", "-i", str(clip), "-frames:v", "1", "-vf",
                              f"scale={w}:{h}", "-f", "rawvideo", "-pix_fmt", "gray" if gray else "rgb24", "-"],
                             capture_output=True).stdout
        size = w * h * (1 if gray else 3)
        if len(raw) >= size:
            a = np.frombuffer(raw[:size], np.uint8)
            out.append(a.reshape(h, w) if gray else a.reshape(h, w, 3))
    return out


def seam_lines(g: np.ndarray, axis: int) -> np.ndarray:
    """For every line across the frame (rows for axis 0, columns for axis 1), the fraction of its length where
    the picture changes sharply from one side of the line to the other."""
    a = g.astype(np.float32) if axis == 0 else g.astype(np.float32).T
    k = 3
    c = np.cumsum(np.vstack([np.zeros((1, a.shape[1]), np.float32), a]), 0)
    above = (c[k:-k - 1] - c[:-2 * k - 1]) / k          # mean of the k lines before line y
    below = (c[2 * k + 1:] - c[k + 1:-k]) / k           # mean of the k lines after it
    cover = (np.abs(above - below) > 16).mean(1)
    return np.concatenate([np.zeros(k), cover, np.zeros(k)])


def line_features(gs: list[np.ndarray], axis: int, y: int) -> tuple[float, float, float]:
    """(sharpness, continuity, straightness) of line y, from the sampled frames.

    sharpness: the biggest one-pixel step within 8 px of the line over the typical step there. A seam is a
      cut (about 10 on the real ones); a soft horizon or table edge is 2-4, but a sea horizon is 10 too.
    continuity: how well the vertical structure 4 px either side lines up. A horizon in a desert or a camp has
      towers, tents and people running through it (0.5-0.9); a seam has nothing (about 0); a sea horizon has
      nothing either.
    straightness: the fraction of columns whose own biggest step is on the same row, within a pixel. This is
      what tells a seam from a sea horizon: a cut is ruler-straight (0.86 and 0.88 on the real splits), any
      horizon wanders a pixel or two along its length (0.38-0.53)."""
    sharp, corr, straight = [], [], []
    for g in gs:
        a = (g if axis == 0 else g.T).astype(np.float32)
        if y - 8 < 0 or y + 9 > a.shape[0]:
            continue
        steps = np.abs(np.diff(a[y - 8:y + 9], axis=0))          # 16 steps x columns
        d = steps.mean(1)
        k = int(np.argmax(d))
        side = np.median(np.r_[d[:max(0, k - 2)], d[k + 3:]])
        sharp.append(d[k] / max(side, 0.5))
        straight.append(float(np.mean(np.abs(steps.argmax(0) - k) <= 1)))
        u, l = np.abs(np.diff(a[y - 4])), np.abs(np.diff(a[y + 4]))
        if u.std() > 1 and l.std() > 1:
            corr.append(np.corrcoef(u, l)[0, 1])
    med = lambda v, empty: float(np.median(v)) if v else empty
    return med(sharp, 0.0), med(corr, 1.0), med(straight, 0.0)


def split_screen(gs: list[np.ndarray]) -> str | None:
    for axis, name in ((0, "stacked"), (1, "side by side")):
        covers = np.array([seam_lines(g, axis) for g in gs])          # frames x lines
        n = covers.shape[1]
        lo, hi = int(n * 0.12), int(n * 0.88)                         # a seam is never at the very edge
        strong = covers >= SEAM_COVER
        held = [y for y in range(lo, hi) if strong[:, y - 1:y + 2].any(1).mean() >= SEAM_FRAMES]
        groups, cur = [], []
        for y in held:                                                 # neighbouring lines are one candidate
            if cur and y > cur[-1] + 2:
                groups.append(cur); cur = []
            cur.append(y)
        if cur:
            groups.append(cur)
        for grp in groups:
            y = max(grp, key=lambda v: covers[:, v].mean())
            sharp, corr, straight = line_features(gs, axis, y)
            if sharp >= SEAM_SHARP and corr <= SEAM_CORR and straight >= SEAM_STRAIGHT:
                return f"split screen: two shots {name}, seam at {100 * y / n:.0f}% of the frame (sharpness {sharp:.1f})"
    return None


_OCR: list = []


def ocr_engine():
    if not _OCR:
        try:
            from rapidocr_onnxruntime import RapidOCR
            _OCR.append(RapidOCR())
        except Exception:                                  # noqa: BLE001  not installed: the check is skipped
            _OCR.append(None)
    return _OCR[0]


def text(cs: list[np.ndarray]) -> str | None:
    eng = ocr_engine()
    if eng is None:
        return None
    h = cs[0].shape[0]
    for c in cs:
        res, _ = eng(c)
        for box, txt, score in res or []:
            ys = [p[1] for p in box]
            tall = (max(ys) - min(ys)) / h
            chars = len(re.sub(r"\W", "", txt, flags=re.U))
            if score >= TEXT_MIN_SCORE and chars >= TEXT_MIN_CHARS and tall >= TEXT_MIN_H:
                return f"text on screen: '{txt}'"
    return None


def check(clip: Path) -> list[str]:
    """Every mechanical reason to reject the clip; empty when it passes."""
    try:
        w, h, d = probe(clip)
    except ValueError as e:
        return [str(e)]
    why = []
    if w >= h:
        why.append(f"landscape {w}x{h}: Flow must be set to 9:16")
    if d < 5.0:
        why.append(f"only {d:.1f} s long")
    s = split_screen(frames(clip, GW, GH, SAMPLES, gray=True))
    if s:
        why.append(s)
    t = text(frames(clip, 720, 1280, 3, gray=False))
    if t:
        why.append(t)
    return why


def text_check_available() -> bool:
    return ocr_engine() is not None


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    if not text_check_available():
        print("(text check skipped: RapidOCR is not installed; pip install -r requirements-tools.txt)")
    bad = 0
    for p in sys.argv[1:]:
        why = check(Path(p))
        bad += bool(why)
        print(f"{'REJECT' if why else 'ok    '} {Path(p).parent.parent.parent.name}/{Path(p).name}" + ("".join(f"\n         {w}" for w in why)))
    sys.exit(1 if bad else 0)
