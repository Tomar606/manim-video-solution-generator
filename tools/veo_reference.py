"""Build the still that shows Veo what a beat must LOOK like, and be made of.

    python tools/veo_reference.py <project> --part N --at K [--open]
    python tools/veo_reference.py <project> --all

WHY A PICTURE INSTEAD OF MORE WORDS
-----------------------------------
The prompt for one DNA beat reached 611 words and the clip still came back with
a third backbone, rungs floating free, and hexagonal caps that were never asked
for. Words are how you specify a MECHANISM; they are a poor way to specify a
LOOK, and they turn out to be a poor way to pin down structure the model has its
own habits about. Every extra clause also competes with the ones that matter —
past ~320 words the tool starts dropping them, and the dropped clause is never
the one you would pick.

An image does not compete with itself. Attached as a reference it fixes the
palette, the materials, the lighting, the background and — the part the words
kept losing — how many strands there are and what a rung is made of. The prompt
is then free to describe only the CHANGE, which is the thing it is good at.

WHAT THE IMAGE IS
-----------------
The beat's FIRST FRAME, not a mood board. A grid of examples invites the tool to
draw a grid; one clean still of the correct starting arrangement is what
image-to-video conditioning actually wants.

It is written from three things, in this order of authority: the beat's own
`look` if it has one, the house realistic style, and the beat's brief for the
structure that has to be right.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src import frames, veo, veo_prompts  # noqa: E402

# The look, in the words an image model responds to. Deliberately not the same
# string as the video contract's STYLE line: that one argues with a video model
# about motion, and this one is describing a photograph.
LOOK = (
    "Photoreal three-dimensional scientific visualisation, the kind a "
    "natural-history documentary uses. Real materials with real surface "
    "quality, lit by one soft directional key with gentle fill, soft contact "
    "shading where forms meet, shallow depth of field. Rendered as a physical "
    "object with volume and weight, not drawn as a diagram: no flat fills, no "
    "outlines, no cel shading, no cartoon proportions."
)

GROUND = (
    "The subject is the only thing in focus. Behind it is a soft, heavily "
    "out-of-focus wash of deep, dark, desaturated colour, dark enough that the "
    "lit subject is clearly the brightest thing in the picture. Nothing behind "
    "it is sharp and nothing in it is identifiable: no leaf, wall, floor, "
    "table, horizon, room, instrument, cell or blurred copy of the subject "
    "itself, only smooth dark tone."
)

FRAMING = (
    "Wide 16:9 frame. The subject is centred, complete, with both ends well "
    "inside the picture and an even margin of background on all four sides. "
    "Nothing is cut off by any edge. Nothing is written anywhere in the "
    "picture: no lettering, no numerals, no markings of any kind on the "
    "subject or the background."
)


def brief_for(root: Path, part: int, at: int) -> dict:
    beats, _lines, _meta = veo.video_beats(root, part)
    beat = next((b for b in beats if int(b["at"]) == at), None)
    if beat is None:
        raise SystemExit(f"part {part} has no video beat at caption {at}")
    return beat


def image_prompt(beat: dict) -> str:
    """The still to make: the beat's opening arrangement, in the house look."""
    # `look` lets a beat name the structure precisely without the video prompt
    # having to carry it. Falling back to the brief keeps every existing beat
    # working, at the cost of describing a movement to a still-image model —
    # which is why `look` is worth writing.
    subject = (beat.get("look") or "").strip() or beat["brief"]
    return (f"{LOOK}\n\n"
            f"THE SUBJECT, exactly as it must be built: {subject}\n\n"
            f"{GROUND}\n\n{FRAMING}\n\n"
            f"This is a single still frame, not a sequence and not a montage: "
            f"one subject, one picture, no panels, no grid, no inset and no "
            f"border.")


def from_clip(root: Path, part: int, at: int, clip: Path, when: float) -> Path:
    """Take the reference from a frame of a clip we already have.

    A generation that got the STRUCTURE right and the motion wrong is still a
    correct picture of the starting arrangement, and using its own frame costs
    nothing and needs no image model. It is also the strongest possible
    reference: the tool is being shown its own output, so there is no style gap
    to cross.
    """
    import subprocess
    beat = brief_for(root, part, at)
    name = beat.get("reference") or f"p{part}_at{at:03d}"
    dest = root / "assets" / "references" / f"{name}.png"
    dest.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{when:.3f}", "-i", str(clip),
                    "-frames:v", "1", str(dest), "-y"], check=True)
    print(f"  {dest.relative_to(root)} <- {clip.name} at {when:.2f}s")
    return dest


def build(root: Path, part: int, at: int, *, force: bool = False) -> Path:
    beat = brief_for(root, part, at)
    name = beat.get("reference") or f"p{part}_at{at:03d}"
    dest = root / "assets" / "references" / f"{name}.png"
    if dest.is_file() and not force:
        print(f"  {dest.relative_to(root)} — already built")
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    prompt = image_prompt(beat)
    print(f"\n=== part{part} beat@{at} -> {dest.relative_to(root)}")
    print(prompt[:400] + ("…" if len(prompt) > 400 else ""))
    frames.generate_image(prompt, dest, size="1536x1024")
    print(f"  wrote {dest} ({dest.stat().st_size / 1e6:.2f} MB)")
    return dest


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--part", type=int)
    ap.add_argument("--at", type=int)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--from-clip", help="take the reference from this clip instead")
    ap.add_argument("--at-time", type=float, default=0.3,
                    help="seconds into --from-clip to grab (default 0.3)")
    a = ap.parse_args()
    root = veo.resolve(a.project)

    if a.from_clip:
        if a.part is None or a.at is None:
            raise SystemExit("--from-clip needs --part and --at")
        from_clip(root, a.part, a.at, Path(a.from_clip), a.at_time)
        return 0

    jobs: list[tuple[int, int]] = []
    if a.all:
        for f in sorted(root.glob("beats_part*.json")):
            part = int(f.stem.split("part")[-1])
            for b in json.loads(f.read_text(encoding="utf-8")):
                if b.get("type") == "video":
                    jobs.append((part, int(b["at"])))
    else:
        if a.part is None or a.at is None:
            raise SystemExit("give --part and --at, or --all")
        jobs = [(a.part, a.at)]

    for part, at in jobs:
        build(root, part, at, force=a.force)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
