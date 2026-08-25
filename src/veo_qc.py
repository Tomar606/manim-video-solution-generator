"""Look at a generated clip and decide whether it may go into the video.

Veo is stochastic, so this is not an optional polish pass — it is the gate. A
clip that is 90% right is not 90% usable: a rusting reaction running the wrong
way, or an electrode bubbling on the wrong side, teaches the student the error
we wrote `verification.md` to remove.

WHAT IS GRADED
--------------
Two things, kept separate because they fail for different reasons and want
different fixes:

  the checks   written by the same pass that wrote the prompt, in
               `src/veo_prompts.py`. Facts about this specific beat, phrased so
               a reviewer can confirm or deny each one from a still frame. A
               failure here means the prompt did not pin the fact down.

  the contract the rules that apply to every clip in this track — the plate
               unchanged, nothing above the caption line or below the presenter
               line, and above all NO TEXT. A failure here means the prompt lost
               a house clause, and the fix is to put it back rather than to
               reword the shot.

WHY IT SEES FIRST AND LAST FRAMES SPECIFICALLY
----------------------------------------------
The plate drifting is the defect this track cannot tolerate — the clip is
spliced into the middle of a Manim render of the *same* plate, so a background
that brightens over eight seconds reads as a jump cut at both ends. Comparing
the first and last frames is the only way to see it, and a reviewer given three
frames from the middle will never report it.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

from pydantic import BaseModel, Field

from src.llm import complete_json

PER_SECOND = 1.0     # sampling cadence; fine enough to locate where a clip rots
MAX_FRAMES = 12      # a vision call gets unreliable long before it gets expensive


class Defect(BaseModel):
    severity: str = Field(description="one of: fail, warn")
    issue: str = Field(description="one sentence naming the specific defect, "
                                   "phrased so a prompt could forbid it")


class ClipReview(BaseModel):
    verdict: str = Field(description="one of: pass, warn, fail")
    summary: str = Field(description="one sentence")
    failed_checks: list[str] = Field(
        default_factory=list,
        description="the supplied checks that the frames do NOT support")
    defects: list[Defect] = Field(default_factory=list)
    # Veo is usually right at the start and drifts later, so a clip is rarely
    # all-good or all-bad. Locating the turn is what lets the tail be cut
    # instead of the whole clip being thrown away and regenerated.
    last_good_frame: int = Field(
        default=-1,
        description="the number of the LAST frame that is still completely "
                    "correct. -1 if every frame is good. 0 if even the first is "
                    "wrong.")
    tail_problem: str = Field(
        default="",
        description="what goes wrong after that frame, in one sentence; empty "
                    "if nothing does")
    loopable: bool = Field(
        default=False,
        description="true only if the last good frame could cut straight back "
                    "to the first with no visible jump — i.e. the motion cycles "
                    "and does not end somewhere different from where it began")


class Continuity(BaseModel):
    """Whether clip N+1 actually starts where clip N stopped."""
    continuous: bool = Field(
        description="true only if the clip's first frame could cut straight "
                    "from the reference frame with no visible jump")
    changes: list[str] = Field(
        default_factory=list,
        description="each thing that differs between the two frames and would "
                    "be seen at the cut, one short phrase each")
    severity: str = Field(
        default="none",
        description="none, minor or major. major = a viewer would read it as a "
                    "different shot; minor = a viewer might notice on a rewatch")


SYSTEM = """You are grading a generated animation clip that is about to be spliced \
into a Class 12 Hindi exam-answer video. Be exacting: this clip teaches, and a \
plausible-looking error is worse than an obvious one because nobody catches it.

You are shown frames in order, first to last, from one clip.

Judge ONLY what you can see. Where a check cannot be confirmed from the frames, \
say so rather than assuming it passed — an unverifiable check is a failed one, \
because the whole point of this gate is that nobody will look again.

Report `fail` for: a check that the frames contradict, ANY text/letters/numerals \
anywhere in the frame, ANY decoration that is not part of the demonstration \
(borders, frames, vignettes, title cards, sparkles, lens flares, floating \
particles, interface furniture), the background changing between the first and \
last frame, drawn content above the caption line or below the presenter line, a \
process shown running the wrong way, or an apparatus wired or arranged wrongly.

The clip carries the animation and nothing else. That is a hard rule, not a \
preference: everything on this screen has to earn its place by teaching \
something, and anything else is a distraction with production value.

Report `warn` for: something ambiguous, ugly, or half-finished at the cut.

Do not report: the absence of a presenter or captions (both are composited \
afterwards), empty background in the reserved bands (that is correct), or \
stylistic preference."""


def frames(video: Path, out: Path) -> list[tuple[str, float]]:
    """Sample about one frame per second, with the true first and last included.

    Two departures from `src/qc.py`, both deliberate:

    It does NOT trim 15% off each end. The ends are exactly where the two
    defects this gate exists for show up — the plate drifting, and motion that
    has not resolved by the cut — so trimming them hides them.

    It samples on a CADENCE rather than a fixed count, and every frame's
    timestamp is returned with it. A verdict alone would only let us regenerate;
    knowing which second the clip stopped being right lets us keep the part that
    was, which is usually most of it.
    """
    out.mkdir(parents=True, exist_ok=True)
    dur = duration(video)
    if dur <= 0:
        return []
    n = max(2, min(MAX_FRAMES, int(dur / PER_SECOND) + 1))
    stamps = [dur * i / (n - 1) for i in range(n)]
    stamps[-1] = max(0.0, dur - 0.05)          # -ss past the last frame yields nothing
    got = []
    for i, at in enumerate(stamps):
        dest = out / f"{video.stem}_f{i}.png"
        r = subprocess.run(
            ["ffmpeg", "-y", "-v", "error", "-ss", f"{at:.3f}", "-i", str(video),
             "-frames:v", "1", "-q:v", "2", str(dest)],
            capture_output=True, text=True)
        if r.returncode == 0 and dest.is_file() and dest.stat().st_size > 0:
            got.append((str(dest), at))
    return got


def duration(video: Path) -> float:
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", str(video)],
        capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def review(video: Path, spec: dict, *, work: Path,
           brief: str = "", full_frame: bool = True,
           provider: str | None = None) -> dict:
    """Grade one clip. Returns the review as a plain dict, `frames` included."""
    from src.veo_prompts import LAYOUT

    shots = frames(video, work)
    if not shots:
        return {"verdict": "fail", "summary": "the clip has no readable frames",
                "failed_checks": [], "defects": [
                    {"severity": "fail", "issue": "the downloaded file did not decode"}],
                "frames": [], "good_until": 0.0}

    paths = [p for p, _ in shots]
    stamps = [t for _, t in shots]
    roll = "\n".join(f"  frame {i + 1}: {t:.1f}s" for i, t in enumerate(stamps))

    bottom = LAYOUT["full_bottom"] if full_frame else LAYOUT["presenter_top"]
    checks = spec.get("checks") or []
    prompt = f"""There are {len(shots)} frames below, in order from the first frame of
the clip to the last. They are evenly spaced through it:

{roll}

WHAT THIS BEAT WAS COMMISSIONED TO SHOW:
{brief or spec.get('prompt', '')[:600]}

THE CHECKS THIS CLIP MUST SATISFY — grade each one and list by name any that the
frames do not support:
{chr(10).join(f'  {i + 1}. {c}' for i, c in enumerate(checks)) or '  (none supplied)'}

THE CONTRACT EVERY CLIP IN THIS TRACK MUST SATISFY — grade these too:
  A. The frame carries the animation and NOTHING else. Two separate fails:
     A1. No text anywhere in any frame — no words, no letters in any script, no
         numerals, no equations, no units, no axis numbers, no legend, no
         caption. Any letterform at all is a fail, however small or blurred.
     A2. No decoration anywhere — no border, no frame, no vignette, no split
         panel, no title or end card, no sparkle, no glint, no lens flare, no
         floating particle, no interface element. Anything a student could not
         name a teaching purpose for is a fail.
  B. The background is byte-for-byte the same idea in the first and last frame:
     same colour, same texture, same brightness, same border art, nothing added
     to it, nothing removed, no seam or band across the middle. Compare frame 1
     with the last frame directly and say if it drifted.
  C. Every drawn element sits between {int(LAYOUT['caption_cut'] * 100)}% and
     {int(bottom * 100)}% of the frame height. Nothing is drawn in the top
     {int(LAYOUT['caption_cut'] * 100)}% (a Hindi caption goes there) or below
     {int(bottom * 100)}%.
  D. The camera never moves.
  E. Whatever change the clip depicts has finished by the last frame — it is not
     cut off mid-motion.

WHERE THE CLIP STOPS BEING USABLE — answer this even when the verdict is `pass`.
These clips are typically right at the start and drift later: the process
completes and then keeps going, an extra object appears, a letterform creeps in,
the background shifts. Give `last_good_frame` as the number of the LAST frame
that is still completely correct against everything above, and say in
`tail_problem` what goes wrong after it. Use -1 only when the clip is good all
the way to the final frame. The tail will be CUT at that point, so err early: a
second of good footage lost costs nothing, and a second of wrong footage kept
goes into the finished video.

`loopable` is a separate question: could the last good frame cut straight back to
frame 1 without a visible jump? That is true only when the motion genuinely
cycles and ends where it began. If the clip shows a one-way change — something
spreading, filling, rising, reacting, accumulating — the answer is false, even
if the two frames look similar.

Answer strictly about these frames."""

    r = complete_json(SYSTEM, prompt, ClipReview, effort="high",
                      images=paths, provider=provider)
    out = r.model_dump()
    out["frames"] = paths
    out["stamps"] = [round(t, 2) for t in stamps]
    out["good_until"] = good_until(out, stamps)
    return out


def good_until(review_dict: dict, stamps: list[float]) -> float:
    """Seconds of the clip that may be used, from `last_good_frame`.

    Rounded DOWN to the reported frame's own timestamp rather than up to the
    next sample. The frames are a second apart, so the real moment the clip
    turned is somewhere in between, and the half-second this gives away is worth
    strictly less than the half-second of hallucination it avoids keeping.
    """
    n = int(review_dict.get("last_good_frame", -1))
    if n < 0 or not stamps:
        return stamps[-1] if stamps else 0.0
    if n == 0:
        return 0.0
    return float(stamps[min(n, len(stamps)) - 1])


CONTINUITY_SYSTEM = """You are checking whether two frames belong to the same \
continuous take.

The FIRST image is the last frame of a clip that has already been accepted. The \
SECOND is the first frame of the clip generated to follow it, and in the finished \
video they are adjacent: the first is on screen, then the second is, with no \
transition between them.

Judge only whether the cut would be VISIBLE. You are not grading whether the \
second frame is attractive or correct — another pass does that. You are asking \
one question: would a viewer watching this cut at normal speed perceive the \
picture as continuing, or as being replaced?

Things that make it a cut, and all of them are `major`: the apparatus is a \
different shape, size or proportion; a part of it has moved, appeared or gone; \
the colours or materials differ; the light comes from somewhere else or has a \
different warmth; the camera is at a different distance or angle; the background \
has changed at all.

Motion that has CONTINUED is not a cut and is the whole point — a liquid a \
little higher, rust spread a little further, a bubble in a different place. \
Judge the setting, not the state of the process."""


def continuity(reference: Path, clip: Path, *, work: Path,
               provider: str | None = None) -> dict:
    """Compare the frame handed forward against the frame the new clip opens on.

    This is the defect that only exists once clips are adjacent, and it is
    invisible to the main review, which sees one clip at a time and would call
    a beautifully-rendered wrong apparatus a pass. It is also the defect a
    reference upload is most likely to half-solve: Flow usually honours the
    frame, and "usually" across five clips is a sequence with a jump in it.

    Kept out of `review()` deliberately. The two graders disagree about
    different things and want different repairs — a failed check means the
    prompt did not pin a fact down, a failed seam means the prompt stopped
    saying it was a continuation — and folding the reference frame into the
    review's frame roll would also shift the numbering `last_good_frame` is
    counted in.
    """
    work.mkdir(parents=True, exist_ok=True)
    opening = work / f"{Path(clip).stem}_open.png"
    r = subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-ss", "0", "-i", str(clip),
         "-frames:v", "1", "-q:v", "2", str(opening)],
        capture_output=True, text=True)
    if r.returncode != 0 or not opening.is_file():
        return {"continuous": False, "severity": "major",
                "changes": ["the clip's first frame could not be read"]}

    got = complete_json(
        CONTINUITY_SYSTEM,
        "Frame 1 is the end of the accepted clip. Frame 2 is the start of the "
        "clip meant to continue it. Would the cut between them be visible?",
        Continuity, effort="high", images=[str(reference), str(opening)],
        provider=provider)
    out = got.model_dump()
    out["reference"] = str(reference)
    out["opening"] = str(opening)
    return out


def seam_defects(cont: dict) -> list[str]:
    """The seam findings, phrased so `revise_prompt` can act on them."""
    if not cont or cont.get("severity") != "major":
        return []
    return [f"this clip must continue the previous one seamlessly, but it "
            f"restarts the shot: {c}" for c in cont.get("changes", [])] or \
           ["this clip must continue the previous one seamlessly, but its first "
            "frame does not match the frame it was generated from"]


def defect_lines(review_dict: dict) -> list[str]:
    """Everything a prompt rewrite needs to fix, as flat sentences."""
    lines = [f"a required check was not satisfied: {c}"
             for c in review_dict.get("failed_checks", [])]
    lines += [d["issue"] for d in review_dict.get("defects", [])
              if d.get("severity") == "fail"]
    return lines


def write_report(path: Path, entries: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(entries, ensure_ascii=False, indent=2),
                    encoding="utf-8")
