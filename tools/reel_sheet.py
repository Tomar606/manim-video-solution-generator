"""Review sheets for an all-Veo reel: one per scene, and one across every cut.

    python tools/reel_sheet.py <slug> [<reel.mp4>] [--out-dir DIR]

Two sheets, because a reel has two things that can be wrong and they are not
visible in the same picture:

  <slug>_scenes.png   one frame from the middle of each scene. Answers "is the
                      right thing on screen while he says this line", and for a
                      keyed studio scene, "is he standing on the background
                      cleanly".
  <slug>_cuts.png     three frames across every join — before, ON the
                      transition's peak, after. Answers the only question a
                      still of a scene cannot: does the seam between two
                      generations read as an edit or as a mistake. The middle
                      frame of each row is the one to look at; if the picture
                      has already changed there, the cut is landing off the
                      peak.

Scene times come from reel.json and the clips themselves, not from the finished
file, so the sheet is right even when a transition has borrowed frames either
side of a join.
"""
from __future__ import annotations

import argparse
import io
import json
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
FONT = ("/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc")
# THE LABEL UNDER EACH TILE IS THE SPOKEN LINE, so it is Devanagari, and Arial
# has none of it — the first sheet came out with a row of tofu boxes where the
# lines should have been. The vendored Noto face covers Devanagari AND Latin, so
# one font does both the scene id and the line.
DEVA = ROOT / "assets" / "fonts" / "NotoSansDevanagari.ttf"


def font(sz: int, deva: bool = False):
    for f in ([str(DEVA)] if deva else []) + list(FONT):
        if Path(f).is_file():
            try:
                return ImageFont.truetype(f, sz)
            except OSError:
                pass
    return ImageFont.load_default()


def dur(p: Path) -> float:
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                 "-of", "csv=p=0", str(p)], capture_output=True,
                                text=True).stdout or 0)


def grab(clip: Path, t: float, w: int) -> Image.Image | None:
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{max(0.0, t):.2f}", "-i", str(clip),
                          "-frames:v", "1", "-vf", f"scale={w}:-1", "-f", "image2pipe",
                          "-vcodec", "png", "-"], capture_output=True).stdout
    return Image.open(io.BytesIO(raw)).convert("RGB") if raw else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("reel", nargs="?", default="")
    ap.add_argument("--out-dir", default=str(Path.home() / "Desktop" / "Frames for review"))
    ap.add_argument("--width", type=int, default=150)
    a = ap.parse_args()

    proj = ROOT / "projects" / a.slug
    spec = json.loads((proj / "reel.json").read_text(encoding="utf-8"))
    reel = Path(a.reel) if a.reel else proj / "final" / f"{a.slug.replace('-', '_')}.mp4"
    # A REEL TAKES HALF AN HOUR TO JOIN AND THE CONTENT IS REVIEWABLE BEFORE
    # THEN. Every scene is already conformed in work/reel/<id>_fit.mp4, so the
    # scene sheet is built from those when the finished reel is not there yet,
    # and the cut sheet from the furthest join that exists. What that costs is
    # only that the cut sheet is short — it shows the joins made so far.
    partial = not reel.is_file()
    if partial:
        # THE SCENE SHEET DOES NOT NEED THE JOINS. Every scene is already
        # conformed, captioned and carded in work/reel/<id>_fit.mp4, so the
        # content is reviewable the moment the fit stage ends — half an hour
        # before the joins finish. Only the CUT sheet needs a join, so a run
        # with none simply skips that half instead of refusing to do anything.
        joins = sorted((proj / "work" / "reel").glob("join_*.mp4"))
        reel = joins[-1] if joins else None
        print(f"  the finished reel is not there yet — scenes from their own "
              + (f"clips, cuts from {reel.name}" if reel else "clips; no join yet, "
                 f"so no cut sheet"))
    lines = {}
    lf = proj / "lines.json"
    if lf.is_file():
        lines = json.loads(lf.read_text(encoding="utf-8"))
    out_dir = Path(a.out_dir).expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)

    # where each scene sits in the finished reel: its own clips, cumulatively
    fit = proj / "work" / "reel"
    marks, at = [], 0.0
    for s in spec["scenes"]:
        f = fit / f"{s['id']}_fit.mp4"
        d = dur(f) if f.is_file() else 10.0
        marks.append((s, at, at + d))
        at += d
    total = at

    W = a.width
    small, tiny = font(11), font(12, deva=True)

    # ---- sheet 1: one frame per scene --------------------------------------
    tiles = []
    for s, t0, t1 in marks:
        if partial:
            f = fit / f"{s['id']}_fit.mp4"
            im = grab(f, (t1 - t0) / 2, W) if f.is_file() else None
        else:
            im = grab(reel, (t0 + t1) / 2, W)
        if im:
            tiles.append((s, im, (t0 + t1) / 2))
    cols = 7
    # EVERY TILE THE SAME SIZE. scale=W:-1 rounds the height to an even number,
    # so a 1080x1920 scene and a 720x1280 one come back 150x266 and 150x267 and
    # the last paste runs off the canvas ("tile cannot extend outside image").
    tw = max(im.width for _, im, _ in tiles)
    th = max(im.height for _, im, _ in tiles)
    tiles = [(s, im if im.size == (tw, th) else im.resize((tw, th)), t)
             for s, im, t in tiles]
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (tw * cols, (th + 34) * rows), "black")
    d = ImageDraw.Draw(sheet)
    for i, (s, im, t) in enumerate(tiles):
        x, y = (i % cols) * tw, (i // cols) * (th + 34)
        sheet.paste(im, (x, y))
        tag = f"{s['id']}  {t:.1f}s" + ("  [keyed]" if s.get("green") else "")
        d.text((x + 4, y + th + 3), tag, fill="white", font=small)
        ln = lines.get(str(int(s["id"][1:])), "")
        d.text((x + 4, y + th + 17), ln[:30], fill="#b0b0b0", font=tiny)
    p1 = out_dir / f"{a.slug.upper()}_scenes.png"
    sheet.save(p1)
    print(f"  {len(tiles)} scene still(s) -> {p1}")

    # ---- sheet 2: three frames across every cut ----------------------------
    if reel is None:
        print("  no join built yet — scene sheet only")
        return 0
    # A JOIN THAT IS STILL BEING WRITTEN PROBES AS ZERO SECONDS, which made
    # every cut fall outside the reel, left the sheet with no rows, and failed
    # on save with "tile cannot extend outside image" — an error that says
    # nothing about the real cause. Fall back down the joins until one has a
    # length, and say plainly when there is nothing to show yet.
    have = dur(reel)
    if have <= 0 and partial:
        for older in sorted((proj / "work" / "reel").glob("join_*.mp4"), reverse=True)[1:]:
            have = dur(older)
            if have > 0:
                reel = older
                break
    cuts = [(s, t0) for s, t0, _ in marks[1:] if s.get("transition") and t0 < have - 0.5]
    if not cuts:
        print(f"  no finished join to show cuts from yet ({reel.name} reads "
              f"{have:.1f}s) — scene sheet only")
        return 0
    rowh = th + 34
    sheet2 = Image.new("RGB", (tw * 3 + 150, rowh * len(cuts)), "black")
    d2 = ImageDraw.Draw(sheet2)
    for r, (s, t) in enumerate(cuts):
        for k, off in enumerate((-0.45, 0.0, 0.45)):
            im = grab(reel, min(max(0.0, t + off), have - 0.05), W)
            if im:
                if im.size != (tw, th):
                    im = im.resize((tw, th))
                sheet2.paste(im, (150 + k * tw, r * rowh))
        d2.text((6, r * rowh + 8), f"-> {s['id']}", fill="white", font=small)
        d2.text((6, r * rowh + 24), f"{t:.1f}s", fill="#9a9a9a", font=tiny)
        d2.text((6, r * rowh + 40), (s.get("transition") or "")[:20], fill="#c8a24a", font=tiny)
        d2.text((150, r * rowh + th + 3), "before", fill="#9a9a9a", font=tiny)
        d2.text((150 + tw, r * rowh + th + 3), "AT THE CUT", fill="#c8a24a", font=tiny)
        d2.text((150 + 2 * tw, r * rowh + th + 3), "after", fill="#9a9a9a", font=tiny)
    p2 = out_dir / f"{a.slug.upper()}_cuts.png"
    sheet2.save(p2)
    print(f"  {len(cuts)} cut(s) -> {p2}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
