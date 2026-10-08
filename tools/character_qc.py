"""Check that the man in a generated clip is OUR presenter.

    python tools/character_qc.py <clip-or-video.mp4> [--at 2 6 10] [--json out.json]

WHY THIS IS A VISION CHECK AND NOT A MEASUREMENT
------------------------------------------------
Identity is not something pixel statistics answer. A first attempt measured
"head width" and "beard coverage" from dark-pixel masses and reported a 914px
head on a frame where it had actually found the shirt and the background — a
confident number about the wrong object. Skin tone, shirt colour and framing can
be measured; WHO THIS IS cannot, so that part is put to the vision model against
the reference photograph, which is the only thing that settles it.

The checklist comes from assets/character/ritesh.md, and the reference frame is
sent alongside every frame under test so the comparison is like-for-like rather
than against a description the model imagines for itself.

WHAT IT CAUGHT
--------------
HIS-C2-SA-06 shipped with three different men in it: the composited HeyGen
presenter and two generated clips showing bearded strangers. Every clip had
passed its own visual review, because each was graded against its own prompt —
nobody was asking whether it was HIM.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src import llm  # noqa: E402

REFERENCE = ROOT / "assets" / "character" / "ritesh_reference.jpeg"
NOTES = ROOT / "assets" / "character" / "ritesh.md"

ASK = """The FIRST image is the reference photograph of our presenter. The
images after it are frames from a video we generated.

For EACH generated frame, say whether the man in it is the SAME MAN as the
reference. Judge on these, which is the order they matter in:

1. THE BEARD — full, thick, black, covering the jaw and riding HIGH onto the
   cheeks with a soft natural edge. A short or trimmed beard is a different man.
2. THE HAIRLINE — receding at the two upper corners of the forehead, hair swept
   back with volume at the front. A full straight hairline is a different man.
3. BUILD — medium-heavy, broad shoulders and full chest. A slim man is not him.
4. FACE SHAPE — broad and full with a rounded jaw and full cheeks.
5. CLOTHING — plain black short-sleeve polo, two-button placket.

Answer as JSON only:
{"frames":[{"t":<seconds>,"same_person":true|false,"confidence":"high|medium|low",
"differences":["..."]}],"verdict":"pass|fail","summary":"one sentence"}

Be strict. "A bearded Indian man in a black polo" is not the test — plenty of
men match that and are not him. If the beard is shorter, the hairline is full,
or the build is slimmer, say so and mark same_person false."""


def grab(video: str, t: float, out: Path) -> Path | None:
    subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", video,
                    "-frames:v", "1", str(out), "-y"], capture_output=True)
    return out if out.is_file() and out.stat().st_size else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--at", type=float, nargs="*", default=[2.0, 6.0, 10.0])
    ap.add_argument("--json", default="")
    ap.add_argument("--provider", default=None)
    a = ap.parse_args()

    if not REFERENCE.is_file():
        print(f"  ! no reference at {REFERENCE}")
        return 1
    work = Path("/tmp/character_qc")
    work.mkdir(parents=True, exist_ok=True)
    shots = []
    for t in a.at:
        p = grab(a.video, t, work / f"f{int(t * 100):06d}.png")
        if p:
            shots.append((t, p))
    if not shots:
        print("  ! could not read any frame")
        return 1

    prompt = ASK + "\n\nThe generated frames are at: " + \
        ", ".join(f"{t}s" for t, _ in shots)
    system = ("You verify that a generated video shows OUR presenter and not "
              "some other bearded man. You are strict and you answer in JSON.")
    raw = llm.complete(system, prompt,
                       images=[str(REFERENCE)] + [str(p) for _, p in shots],
                       provider=a.provider)
    try:
        s = raw[raw.index("{"):raw.rindex("}") + 1]
        rep = json.loads(s)
    except (ValueError, json.JSONDecodeError):
        print("  ! could not parse the review:\n" + raw[:400])
        return 1

    print(f"  {Path(a.video).name}")
    for f in rep.get("frames", []):
        mark = "ok  " if f.get("same_person") else "NOT HIM"
        print(f"    {float(f.get('t', 0)):6.1f}s  {mark:<8} ({f.get('confidence')})")
        for d in f.get("differences") or []:
            print(f"             - {d}")
    print(f"  verdict: {rep.get('verdict')} — {rep.get('summary','')}")
    if a.json:
        Path(a.json).write_text(json.dumps(rep, indent=2), encoding="utf-8")
    return 0 if rep.get("verdict") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
