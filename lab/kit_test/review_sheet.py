"""The frames sheet a reviewer approves before the render: every review still, labelled with its time.

    python lab/kit_test/review_sheet.py <slug> [--label review]

Reads lab/kit_test/out/plan_<slug_>_p<N>/<label>/still_*.png (written by stills.mjs) and writes
projects/<slug>/review/frames <N>.jpg, fifteen stills a sheet, each under its m:ss time, so a reviewer
can say "1:24, the photo covers his face" without opening any tool but an image viewer.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def font(size: int):
    for f in ("/System/Library/Fonts/Supplemental/Arial Bold.ttf", "C:/Windows/Fonts/arialbd.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
        if Path(f).exists():
            return ImageFont.truetype(f, size)
    return ImageFont.load_default()


def main() -> int:
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    slug = sys.argv[1]
    label = sys.argv[sys.argv.index("--label") + 1] if "--label" in sys.argv else "review"
    out_dir = ROOT / "projects" / slug / "review"
    out_dir.mkdir(parents=True, exist_ok=True)
    f = font(26)
    made = []
    for plan_out in sorted((HERE / "out").glob(f"plan_{slug.replace('-', '_')}_p*")):
        stills = sorted((plan_out / label).glob("still_*.png"))
        if not stills:
            continue
        tl = json.loads((plan_out / "timeline.js").read_text().replace("window.TL = ", "").rstrip().rstrip(";"))
        times = [s["t"] if isinstance(s, dict) else s for s in tl.get("stills", [])]
        part = plan_out.name.rsplit("_p", 1)[1]
        cols, w, h = 5, 360, 640
        for k in range(0, len(stills), 15):
            grp = stills[k:k + 15]
            rows = (len(grp) + cols - 1) // cols
            sheet = Image.new("RGB", (cols * w, rows * (h + 40)), (24, 24, 24))
            d = ImageDraw.Draw(sheet)
            for i, p in enumerate(grp):
                x, y = (i % cols) * w, (i // cols) * (h + 40)
                sheet.paste(Image.open(p).convert("RGB").resize((w, h)), (x, y + 40))
                t = times[k + i] if k + i < len(times) else 0
                d.text((x + 8, y + 6), f"{int(t // 60)}:{t % 60:04.1f}", fill=(255, 210, 120), font=f)
            dest = out_dir / f"frames part{part} {k // 15 + 1}.jpg"
            sheet.save(dest, quality=86)
            made.append(dest)
    for m in made:
        print(m.relative_to(ROOT))
    return 0 if made else 1


if __name__ == "__main__":
    sys.exit(main())
