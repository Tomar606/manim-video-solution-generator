"""The house transition vocabulary: which cut gets which effect, and when none.

A transition here is GRAMMAR, not decoration. The same kind of cut always gets
the same effect, so a viewer learns what a wipe means in these videos; and a cut
that is not a change of world gets NOTHING. That second rule is the one that
keeps this from looking overdone — the restraint is in the plan, not in the
taste of whoever is assembling that day.

    kinds = ["scene_change", "to_card", "from_card", ..., "continuous"]
    plan  = plan_transitions(kinds)      # -> [Transition | None, ...]
    audit(plan)                          # -> warnings, if it is getting busy

WHY A CUT CAN GET NOTHING
-------------------------
Narration runs across some cuts. Segments 9->10->11 of HIS-C2-SA-06 are three
data screens carrying one continuous explanation on one plate; a dip or a wipe
there punctuates a sentence that has not finished. The picture changing is not
by itself a reason to mark the change.

GHOSTING — READ THIS BEFORE CHOOSING A DISSOLVE
-----------------------------------------------
Every dissolve-family effect (fade, hblur, smoothleft/right, fadegrays,
dissolve) superimposes the two shots. In this house the presenter is centre
frame in BOTH shots either side of most cuts, so a plain cross dissolve shows
him on top of himself and reads as a double exposure rather than a transition.
Measured on HIS-C2-SA-06: it is clearly visible at every Veo-to-map cut.
  - `hblur` is the safe dissolve: it defocuses hard enough that the overlap
    reads as a rack focus rather than two people.
  - `smoothright` is next safest: only a moving band is blended at a time.
  - a plain `fade` is for cuts where the framing genuinely differs.

BANNED, WITH REASONS — do not re-try these without re-measuring
"""
from __future__ import annotations

from dataclasses import dataclass

# name -> why it is not used. Checked by `validate()` so a future plan cannot
# quietly reintroduce one.
BANNED: dict[str, str] = {
    "zoomin": "magnifies the outgoing shot until one flat patch fills the frame; "
              "measured a frame of std 0.7 (flat colour) at 0.25s, 0.35s and 0.50s",
    "pixelize": "reads as a compression failure, not a transition",
    "dissolve": "noise dissolve; looks like a bad encode at 1080x1920",
    "radial": "clock wipe; dated",
    "hlwind": "glitch family", "hrwind": "glitch family",
    "vuwind": "glitch family", "vdwind": "glitch family",
}


@dataclass(frozen=True)
class Transition:
    """One effect, its length, and the sound that belongs with it."""
    xfade: str                 # ffmpeg xfade transition name
    seconds: float
    cue: str | None            # sfx name laid at the cut
    cue_gain: float
    second_cue: str | None = None
    second_gain: float = 0.0
    label: str = ""
    loud: bool = False         # counts against the restraint budget
    peak_at: float | None = None   # seconds after the cut where the effect READS

    def reads_at(self) -> float:
        """When a viewer perceives the transition, for lining a cue up to it.

        MEASURED off the render, per effect, because the moment is not the same
        kind of thing in each: a dip or a bloom reads at its EXTREME (fully
        black, fully white), a move reads when it LANDS, a dissolve reads at its
        midpoint, and a rack focus reads when the picture RESOLVES. Assuming the
        midpoint everywhere put the sound up to 0.22s off the picture.
        """
        return self.seconds * 0.5 if self.peak_at is None else self.peak_at

    @property
    def frames(self) -> int:
        return round(self.seconds * 30)


# The vocabulary. Keyed by what the cut MEANS, never by what it looks like —
# a caller says "this is the cut out of the question card", not "use a wipe".
CUTS: dict[str, Transition | None] = {
    # Same world, new place, voice carrying straight on.
    "scene_change": Transition("fade", 0.50, "whoosh", +6.0,
                               label="cross dissolve"),
    # Into the question card: the formal beat of the video.
    "to_card": Transition("fadeblack", 0.40, "whoosh", +8.0, "impact", +6.0,
                          peak_at=0.083, label="dip to dark", loud=True),
    # Out of the card, which is near-white, into daylight. The bloom is
    # motivated by the card itself, and the shutter names it as a photograph.
    "from_card": Transition("fadewhite", 0.30, "shutter", 0.0,
                            peak_at=0.083, label="light bloom", loud=True),
    # The first time a map arrives, it travels in — the map is being introduced
    # as a device, not just shown.
    "to_map_first": Transition("coverup", 0.40, "whoosh", +8.0, "reveal", +4.0,
                               peak_at=0.367, label="cover up"),
    # Every later map arrival is the same move, so it reads as grammar.
    "to_map": Transition("smoothright", 0.45, "whoosh", +8.0, "reveal", +4.0,
                         peak_at=0.2, label="soft gradient wipe"),
    # Back out of a data screen to the world: rack focus off the graphic.
    # peak_at is the MIDPOINT here, not the measured largest frame-to-frame
    # change: hblur's biggest delta is the last frame, where the blur snaps back
    # to sharp, and putting the sound there lands it after the new shot is
    # already fully present. The moment a viewer registers is the mixed middle.
    "from_data": Transition("hblur", 0.50, "whoosh", +8.0, "impact", +6.0,
                            peak_at=0.250, label="blur dissolve"),
    # The voice has not stopped. Do nothing.
    "continuous": None,
}

# At most this many LOUD transitions in one video, however many cuts there are.
LOUD_BUDGET = 2
# If more than this share of cuts carry an effect, the effects have stopped
# meaning anything. Mirrors the visual director's "no graphic is a valid answer".
BUSY_SHARE = 0.85


def validate() -> None:
    for kind, tr in CUTS.items():
        if tr and tr.xfade in BANNED:
            raise ValueError(f"{kind} uses {tr.xfade}: {BANNED[tr.xfade]}")


def plan_transitions(kinds: list[str]) -> list[Transition | None]:
    """One transition per cut, with the loud ones rationed."""
    validate()
    out: list[Transition | None] = []
    spent = 0
    for k in kinds:
        if k not in CUTS:
            raise KeyError(f"unknown cut kind {k!r}; known: {sorted(CUTS)}")
        tr = CUTS[k]
        if tr and tr.loud:
            if spent >= LOUD_BUDGET:
                tr = CUTS["scene_change"]      # fall back to the quiet default
            else:
                spent += 1
        out.append(tr)
    return out


# Loud pairs that BRACKET one segment are not two effects piled up: you dip
# into the question card and bloom out of it, and the pair is what marks it off
# from the rest of the video. Only unrelated loud neighbours are a warning.
BRACKETS = {("dip to dark", "light bloom")}


def audit(plan: list[Transition | None]) -> list[str]:
    """Warnings, not errors. Says when the cutting has become busy."""
    warn = []
    if not plan:
        return warn
    used = [t for t in plan if t]
    share = len(used) / len(plan)
    if share > BUSY_SHARE:
        warn.append(f"{len(used)} of {len(plan)} cuts carry an effect "
                    f"({share:.0%}) — nothing is left as a plain cut")
    loud = sum(1 for t in used if t.loud)
    if loud > LOUD_BUDGET:
        warn.append(f"{loud} loud transitions; the budget is {LOUD_BUDGET}")
    for a, b in zip(used, used[1:]):
        if a.loud and b.loud and (a.label, b.label) not in BRACKETS:
            warn.append(f"two loud transitions back to back: {a.label}, {b.label}")
    return warn
