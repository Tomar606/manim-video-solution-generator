"""A review sheet of stills across a finished part: one per beat, plus the card.

    python tools/frames_sheet.py <slug> <part> <final.mp4> <out.png>

Each still is taken a little AFTER its beat has built (and after its last
row/label has arrived when it fills in), so the sheet shows what the student
reads, not a half-faded transition. Labelled with the time and the beat.
"""
from __future__ import annotations

import io
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]


def grab(video, t, w=300):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.2f}", "-i", str(video),
                          "-frames:v", "1", "-vf", f"scale={w}:-2", "-f", "image2pipe",
                          "-vcodec", "png", "-"], capture_output=True).stdout
    return Image.open(io.BytesIO(raw)).convert("RGB")


def main() -> int:
    slug, part, video, out = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    proj = ROOT / "projects" / slug
    lines = json.loads((proj / f"lines_part{part}.json").read_text(encoding="utf-8"))
    beats = json.loads((proj / f"beats_part{part}.json").read_text(encoding="utf-8"))
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                "-of", "csv=p=0", video], capture_output=True, text=True).stdout)
    shots = [(4.0, "card"), (min(dur - 0.5, float(lines[-1]["start"]) + 1.0), "close")]
    for b in beats:
        if b["type"] == "clear":
            continue
        i = int(b["at"])
        nxt = sorted(int(x["at"]) for x in beats if int(x["at"]) > i)
        end = float(lines[nxt[0]]["start"]) - 0.5 if nxt else dur - 0.5
        # every time this beat changes the screen
        ats = [i]
        for k, v in b.items():
            if k == "at" or not (k.endswith("_at") or k == "reveal_at"):
                continue
            ats += [x for x in (v if isinstance(v, list) else [v]) if isinstance(x, int)]
        for r in b.get("rows", []):
            a = r.get("at")
            ats += [x for x in (a if isinstance(a, list) else [a]) if isinstance(x, int)]
        last = max(ats)
        t_mid = float(lines[i]["start"]) + 1.2
        # the beat's FINAL state: just before the next beat takes the stage,
        # once every row, label and animation has landed
        t_full = max(t_mid, end - 0.3)
        shots.append((t_mid, b["type"]))
        if t_full - t_mid > 2.5:
            shots.append((t_full, b["type"] + " (filled)"))
    shots.sort()
    font = ImageFont.load_default()
    tiles = []
    for t, name in shots:
        im = grab(video, max(0.0, t))
        # the label goes UNDER the still: drawn over it, it hid the caption and
        # the card's "?" ring — the two things a reviewer checks first
        tile = Image.new("RGB", (im.width, im.height + 20), (0, 0, 0))
        tile.paste(im, (0, 0))
        ImageDraw.Draw(tile).text((4, im.height + 4), f"{t:6.1f}s  {name}",
                                  fill=(255, 220, 90), font=font)
        tiles.append(tile)
    cols = 6
    w, h = tiles[0].size
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (w + 6) + 6, rows * (h + 6) + 6), (20, 20, 24))
    for n, im in enumerate(tiles):
        sheet.paste(im, (6 + (n % cols) * (w + 6), 6 + (n // cols) * (h + 6)))
    sheet.save(out)
    print(f"  {len(tiles)} stills -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
