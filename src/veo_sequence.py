"""Carrying the look from one generated clip into the next.

WHY THIS EXISTS, AND WHY IT DID NOT BEFORE
------------------------------------------
The original Veo route generates one clip per beat, and each of those clips is
an ISLAND: a rusting nail dropped into the middle of an otherwise-Manim part,
with Manim content on both sides of it. Two Veo clips are never adjacent, so
there is no seam between them, and continuity is bought entirely by the
background plate — the same PNG Manim renders is uploaded into Flow, so the
splice is invisible at both ends. That is `src/veo.py` and it is unchanged.

A whole PART routed to Veo is a different problem. Now the clips ARE adjacent:
five generations play back to back with nothing between them, and Veo has no
memory across generations. Same prompt, same plate, and the apparatus is a
slightly different apparatus each time — the glass a shade greener, the copper
strip two millimetres wider, the light coming from the other side. Each clip
looks fine alone. Played in sequence they read as five different videos of five
different experiments, which for a student comparing what they see now against
what they saw four seconds ago is worse than not animating the topic at all.

The fix is to hand Veo the thing it is missing: the frame the previous clip
ENDED on, uploaded as a reference for the next generation. The tool is being
asked to continue a picture rather than to invent one, and the picture it is
continuing is the one the student is looking at when the cut happens.

WHAT A SEQUENCE IS
------------------
Consecutive `type: video` beats that share a `sequence` id:

    {"at": 12, "type": "video", "sequence": "daniell", "brief": "...", ...}
    {"at": 16, "type": "video", "sequence": "daniell", "brief": "...", ...}
    {"at": 21, "type": "video", "sequence": "daniell", "brief": "...", ...}

A beat with no `sequence` is a sequence of one, which is exactly the old behaviour —
that is the whole compatibility story. Nothing about an existing project changes
until somebody writes a `sequence` key.

Every beat keeps its OWN window, computed from the caption it is anchored to
(`veo.window`). A sequence is not one long clip cut into pieces; it is N clips that
each land on a sentence boundary and each get conformed to their own slot. That
is what keeps the existing conform, label and QC machinery working unchanged,
and it is also better teaching: the cut happens where the teacher moves on.

WHAT GETS UPLOADED, AND IN WHAT ORDER
-------------------------------------
    first clip of a sequence    the plate, then the NCERT reference
    every clip after it      the carry frame, then the NCERT reference

The carry frame REPLACES the plate rather than joining it, and that is not an
economy — it is the point. The carry frame is a full 1080x1920 frame of a clip
that was itself generated on the plate, so it already contains the plate,
already contains the apparatus, and already contains the lighting. It is a
strictly better background than the background.

The NCERT scan stays attached for every clip in the sequence, because the thing it
pins down is the one thing a carry frame cannot fix: a carry frame propagates
whatever apparatus clip 1 invented, so if clip 1 drew the wrong Daniell cell the
whole sequence draws the wrong Daniell cell, consistently. See `reference_for`.

WHEN A CLIP FAILS ITS REVIEW
----------------------------
The next clip continues from the last ACCEPTED frame, never from a rejected one.
Propagating a frame the review just called wrong is how one bad generation
becomes five, and it would do it while looking more consistent than the correct
version. `Carry.broken` records that it happened so the run's summary can say
so — a sequence with a hole in it is still worth shipping, but somebody has to know
where the hole is.
"""
from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from src.veo_conform import duration

# How far back from the true end of the clip the carry frame is taken. The last
# frame of an h264 file is the one most likely to carry compression mush, and a
# blocky reference teaches Veo to generate blocky. A twelfth of a second earlier
# is visually the same frame and a cleaner one.
CARRY_BACKOFF = 0.08


class SequenceError(RuntimeError):
    pass


@dataclass
class Carry:
    """What clip N hands to clip N+1."""
    sequence: str
    frame: Path | None = None       # the accepted final frame, or None at the start
    source_at: int | None = None    # which beat that frame came from
    broken: bool = False            # a clip in between failed and was not carried
    history: list[dict] = field(default_factory=list)

    def accept(self, at: int, frame: Path) -> None:
        self.frame, self.source_at, self.broken = frame, at, False
        self.history.append({"at": at, "frame": str(frame), "carried": True})

    def reject(self, at: int) -> None:
        """A clip failed review. Keep the previous frame; mark the seam."""
        self.broken = True
        self.history.append({"at": at, "frame": None, "carried": False})


# --------------------------------------------------------------------------- #
# Grouping
# --------------------------------------------------------------------------- #
def spans(video_beats: list[dict]) -> list[list[dict]]:
    """Split the video beats into runs that share a `sequence` id.

    The beats arrive in caption order and are kept in it — a sequence is a run of
    ADJACENT beats, so `sequence` is a marker on a run rather than a set
    membership. Two beats with the same id and a differently-marked beat
    between them is a mistake in the beats file and is reported as one, because
    the alternative is silently generating clip 3 from clip 1's frame and
    leaving the seam nobody expected.
    """
    runs: list[list[dict]] = []
    for b in video_beats:
        cid = b.get("sequence")
        if cid and runs and runs[-1][0].get("sequence") == cid:
            runs[-1].append(b)
        else:
            runs.append([b])

    seen: set[str] = set()
    for run in runs:
        cid = run[0].get("sequence")
        if not cid:
            continue
        if cid in seen:
            raise SequenceError(
                f"sequence {cid!r} appears in two separate runs of video beats. A "
                f"sequence is a run of ADJACENT beats — if these are meant to be one "
                f"sequence, move them together; if they are two sequences, give "
                f"the second one its own id.")
        seen.add(cid)
    return runs


def describe(run: list[dict]) -> str:
    cid = run[0].get("sequence")
    if len(run) == 1 and not cid:
        return f"beat@{run[0]['at']} (standalone)"
    ats = ", ".join(str(b["at"]) for b in run)
    return f"sequence {cid!r}: {len(run)} clips at captions {ats}"


# --------------------------------------------------------------------------- #
# The carry frame
# --------------------------------------------------------------------------- #
def carry_frame(clip: Path, dest: Path) -> Path:
    """Write the frame `clip` ends on, as a PNG Flow can be handed.

    Taken from the CONFORMED clip, not the raw generation, and the distinction
    matters in both directions. The raw clip's tail is often the part the review
    cut off for being wrong, so carrying its last frame would propagate exactly
    the defect that was just removed. And where the conform looped or held, the
    conformed clip's final frame is genuinely the last thing on screen before
    the next clip starts — which is the only frame the next clip has to continue
    from without a visible jump.
    """
    clip, dest = Path(clip), Path(dest)
    dur = duration(clip)
    if dur <= 0:
        raise SequenceError(f"{clip} has no readable duration, so it has no final "
                         f"frame to carry into the next clip")
    at = max(0.0, dur - CARRY_BACKOFF)
    dest.parent.mkdir(parents=True, exist_ok=True)
    r = subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-ss", f"{at:.3f}", "-i", str(clip),
         "-frames:v", "1", "-q:v", "2", str(dest)],
        capture_output=True, text=True)
    if r.returncode != 0 or not dest.is_file() or dest.stat().st_size == 0:
        raise SequenceError(
            f"could not read the final frame of {clip.name} at {at:.2f}s of "
            f"{dur:.2f}s: {r.stderr.strip()[:200]}")
    return dest


# --------------------------------------------------------------------------- #
# What goes into Flow
# --------------------------------------------------------------------------- #
def uploads(*, plate: Path | None, reference: Path | None,
            carry: Path | None) -> list[Path]:
    """The images to attach to one generation, most important first.

    Ordered rather than a set, because Flow's reference control may only accept
    one file (`src/flow_bridge.py` reports which), and when it does the first
    entry is the one that gets used. So the order encodes what this generation
    would rather lose:

      the carry frame outranks the plate    it contains the plate and more
      the plate outranks the NCERT scan     §15 — an unmatched background is a
                                            visible cut at both ends of the
                                            window, where an unfamiliar-looking
                                            apparatus is only a missed
                                            opportunity
    """
    out = [Path(p) for p in (carry or plate, reference) if p is not None]
    missing = [p for p in out if not p.is_file()]
    if missing:
        raise SequenceError("these reference images do not exist: "
                            + ", ".join(str(p) for p in missing))
    # ABSOLUTE, always. Chrome's DOM.setFileInputFiles resolves nothing: a
    # relative path attaches no file and does not report a failure, so the clip
    # generates without its carry frame and comes back merely inconsistent
    # rather than broken. `veo.resolve()` hands back whatever it was given, so a
    # run started as `video veo projects/x` reaches here relative — this is the
    # one place every path handed to the browser passes through, so it is the
    # place to make that impossible.
    return [p.resolve() for p in out]
