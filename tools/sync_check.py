#!/usr/bin/env python3
"""Is the DELIVERED file in sync — captions and graphics against the voice?

    python3 tools/sync_check.py <slug> <part> <video.mp4> [--plate out/plate.png]
                                [--skip-until SEC]

The spec can say every caption starts on its word and still ship wrong: an
engine fade that fires early, a stale renderer copy, a composite that shifts a
frame. So this reads the finished pixels, the way CLIP_VIDEO_RUNBOOK §12 asks,
and grades three things against the MEASURED clock in spec/segments_part<N>.json
and out/words_part<N>.json:

  CAPTION ON     the caption band carries text 0.25s after each caption's t_in
                 (past the 0.38s pop) and still carries it 0.08s before t_out —
                 "the caption left before he finished" is the defect this pins.
  CAPTION OFF    where the speaker really pauses (next caption > 0.40s away),
                 the band is empty 0.25s after t_out — a caption that hangs
                 over silence reads as lagging.
  STAGE HOLD     for every drawn segment, the last frame with graphic ink on the
                 stage is no earlier than 0.25s before the END OF THE LAST WORD
                 spoken inside that segment (runbook §5: "the animation ends
                 before he finishes speaking").

The video is decoded ONCE at 30 fps into two per-frame numbers per band (white
text pixels, and pixels that differ from the clean plate), so a 130s part costs
a single ffmpeg pass and a few MB of memory.

Exit 1 on any failure.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np

FPS = 30
W, H = 1080, 1920
BANDS = {"bottom": (1050, 1202), "top": (120, 400)}   # caption bands (style.css)
STAGE = (380, 850)                                     # the stage band
CAP_X = (70, 1010)
INK = 225            # a caption glyph is near-white; the plate's art never is
MIN_INK = 400        # pixels of text for "a caption is on screen"
CLEAR_INK = 120


def decode(video: Path, plate: np.ndarray | None):
    rows = []
    cmd = ["ffmpeg", "-v", "error", "-i", str(video), "-vf", f"fps={FPS},format=gray",
           "-f", "rawvideo", "-pix_fmt", "gray", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    n = W * H
    while True:
        buf = p.stdout.read(n)
        if len(buf) < n:
            break
        f = np.frombuffer(buf, np.uint8).reshape(H, W)
        r = {}
        for name, (y0, y1) in BANDS.items():
            r[name] = int((f[y0:y1, CAP_X[0]:CAP_X[1]] > INK).sum())
        s = f[STAGE[0]:STAGE[1], 110:970].astype(np.int16)
        if plate is not None:
            r["stage"] = int((np.abs(s - plate[STAGE[0]:STAGE[1], 110:970]) > 45).sum())
        else:
            r["stage"] = int((s > 175).sum())
        rows.append(r)
    p.wait()
    return rows


def main() -> int:
    slug, part, video = sys.argv[1], int(sys.argv[2]), Path(sys.argv[3])
    args = sys.argv[4:]
    root = Path("work") / slug
    plate = None
    if "--plate" in args:
        from PIL import Image
        plate = np.asarray(Image.open(root / args[args.index("--plate") + 1]).convert("L")).astype(np.int16)
    skip = float(args[args.index("--skip-until") + 1]) if "--skip-until" in args else -1.0
    segs = json.loads((root / "spec" / f"segments_part{part}.json").read_text(encoding="utf-8"))
    lines = json.loads((root / "out" / f"lines_part{part}.json").read_text(encoding="utf-8"))
    words = json.loads((root / "out" / f"words_part{part}.json").read_text(encoding="utf-8"))

    rows = decode(video, plate)
    at = lambda t, key: rows[min(max(int(round(t * FPS)), 0), len(rows) - 1)][key]
    fails, n_on, n_off = [], 0, 0

    t0 = 0.0
    caps = []
    for s in segs:
        band = "top" if s.get("caption_pos") == "top" else "bottom"
        for ph in s.get("phrases", []):
            caps.append((t0 + ph["t_in"], t0 + ph["t_out"], band, ph["text"]))
        s["_t0"] = t0
        t0 += s["duration"]

    for k, (a, b, band, text) in enumerate(caps):
        if b <= skip:
            continue
        n_on += 1
        on_in, on_out = at(a + 0.25, band), at(b - 0.08, band)
        if on_in < MIN_INK or on_out < MIN_INK:
            fails.append(f"CAPTION ON  {a:7.2f}-{b:7.2f} ink {on_in}/{on_out} ({band}) {text[:40]!r}")
        nxt = caps[k + 1][0] if k + 1 < len(caps) else None
        if nxt is not None and nxt - b > 0.40:
            n_off += 1
            off = at(b + 0.25, band)
            if off > CLEAR_INK:
                fails.append(f"CAPTION OFF {b:7.2f}+0.25 still ink {off} ({band}) {text[:40]!r}")

    held = []
    for s in segs:
        if not (s.get("diagram") or s.get("block") or s.get("equation")):
            continue
        a, b = s["_t0"], s["_t0"] + s["duration"]
        if b <= skip:
            continue
        # last word spoken inside this segment
        last_e = max((w["e"] for w in words if a <= w["s"] < b), default=b)
        ink = [at(t / FPS, "stage") for t in range(int(a * FPS), int(b * FPS))]
        base = max(ink) if ink else 0
        thr = max(1500, 0.12 * base)
        last = max((a + i / FPS for i, v in enumerate(ink) if v > thr), default=a)
        d = last - min(last_e, b)
        held.append((s["seg_id"], s["type"], last, last_e, d))
        if d < -0.25:
            fails.append(f"STAGE HOLD  seg {s['seg_id']} {s['type']}: graphic gone at {last:.2f}, "
                         f"last word ends {last_e:.2f} ({d:+.2f}s)")

    print(f"{video.name}: {len(rows)} frames decoded ({len(rows) / FPS:.2f}s)")
    print(f"  captions checked on: {n_on}   off-at-pause: {n_off}")
    for sid, typ, last, le, d in held:
        print(f"  stage seg {sid:2d} {typ:16s} last ink {last:7.2f}  last word ends {le:7.2f}  {d:+.2f}s")
    for f in fails:
        print("  FAIL", f)
    print("  PASS" if not fails else f"  {len(fails)} failure(s)")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
