"""One frame of a video that does not exist yet — plate, chip, presenter, caption.

    python tools/mock_frame.py <clip.mp4> <t> <chip.png|-> "<caption|->" <out.png> \
        --crop <crop.json> --key <key.json> [--plate <plate.png>]

For approving a visual plan before spending half an hour rendering it. Every
layer is the real asset in its real place: the actual plate, the actual chip PNG
at the band's y, the presenter keyed out of the actual clip and positioned by the
project's own crop. Only the caption is a stand-in, drawn with PIL, because it is
the one layer that does not exist until the body renders.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
BAND_TOP = 380
W, H = 1080, 1920


def keyed(clip, t, crop, key):
    with tempfile.TemporaryDirectory() as td:
        png = Path(td) / "f.png"
        vf = (f"crop={crop['w']}:{crop['h']}:{crop['x']}:{crop['y']},"
              f"hsvkey=hue={key['hue']}:sat={key['sat']}:val={key['v1']}"
              f":similarity={key['sim']}:blend=0.08,despill=type=green,format=rgba")
        subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", str(clip),
                        "-frames:v", "1", "-vf", vf, "-y", str(png)], check=True)
        return Image.open(png).convert("RGBA")


def main():
    clip, t, chip, caption, out = sys.argv[1:6]
    args = dict(zip(sys.argv[6::2], sys.argv[7::2]))
    plate = Image.open(args.get("--plate", ROOT / "assets/backgrounds/chemistry.png")
                       ).convert("RGBA").resize((W, H))
    crop = json.loads(Path(args["--crop"]).read_text())
    key = json.loads(Path(args["--key"]).read_text())

    frame = plate.copy()
    if chip != "-":
        frame.alpha_composite(Image.open(chip).convert("RGBA"), (0, BAND_TOP))

    p = keyed(clip, t, crop, key)
    p = p.resize((int(p.width * (H * 0.50) / p.height), int(H * 0.50)))
    frame.alpha_composite(p, ((W - p.width) // 2, H - p.height))

    if caption != "-":
        d = ImageDraw.Draw(frame)
        f = ImageFont.truetype(str(ROOT / "assets/fonts/Khand-Bold.ttf"), 46)
        for i, ln in enumerate(caption.split("|")):
            w = d.textbbox((0, 0), ln, font=f)[2]
            d.text(((W - w) / 2, 44 + i * 58), ln, font=f, fill=(255, 255, 255),
                   stroke_width=4, stroke_fill=(0, 0, 0))
    frame.convert("RGB").save(out)
    print(out)


if __name__ == "__main__":
    main()
