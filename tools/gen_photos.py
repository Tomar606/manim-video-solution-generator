"""Generate the photographic beats for a video, cheaply.

    python tools/gen_photos.py <prompts.json> <out_dir> [--quality low]

`prompts.json` is a list of {slug, prompt}. An image whose file already exists
is skipped, so re-running costs nothing and an approved picture never changes
under you.

WHAT GOES IN A PROMPT
---------------------
Nothing but the photograph. No text of any kind: image models cannot set
Devanagari — matras land on the wrong consonant and it reads as gibberish to
the only people who matter here — so every label is typeset separately and
composited over the top.

Say what you want positively and put the exclusions in the NEGATIVE line, never
the other way round. Naming a thing in a prompt is a request to draw it, even
inside a sentence that says not to: a block that said "logo" five times while
asking for empty corners produced one in both corners. See
.claude/skills/video-prompt/references/bug-ledger.md.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Appended to every prompt. Kept here rather than in each entry so the whole
# set stays consistent — nine photographs that do not look like nine sources.
HOUSE = (" Real photograph, documentary style, sharp focus on the subject, "
         "soft even lighting, uncluttered composition with the subject filling "
         "the frame, muted natural colour. "
         "NEGATIVE: lettering, characters, numerals, signage, labels, arrows, "
         "diagrams, drawings, illustration, cartoon, 3d render, collage, "
         "borders, frames, vignette, colour fringing, people's faces.")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("prompts", type=Path)
    ap.add_argument("out_dir", type=Path)
    ap.add_argument("--quality", default="low",
                    help="low keeps a nine-image set to a few cents")
    ap.add_argument("--size", default="1536x1024", help="3:2, fits the stage band")
    args = ap.parse_args()

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from src.frames import generate_image

    entries = json.loads(args.prompts.read_text(encoding="utf-8"))
    args.out_dir.mkdir(parents=True, exist_ok=True)
    spent = 0.0
    for e in entries:
        dest = args.out_dir / f"{e['slug']}.png"
        if dest.exists():
            print(f"  = {e['slug']} (already there)")
            continue
        try:
            spent += generate_image(e["prompt"] + HOUSE, dest,
                                    size=args.size, quality=args.quality)
            print(f"  + {e['slug']}")
        except Exception as exc:                        # noqa: BLE001
            print(f"  ! {e['slug']}: {type(exc).__name__}: {exc}")
    print(f"\n{len(list(args.out_dir.glob('*.png')))} image(s) in {args.out_dir}"
          f" — about ${spent:.2f} this run")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
