"""Cut a generated clip down to its good part, then fit that to the avatar's window.

THE TWO PROBLEMS THIS SOLVES, WHICH ARE OPPOSITE
------------------------------------------------
A Flow clip is a fixed length — around eight or ten seconds — and the window it
has to fill is however long the presenter spends talking about it. Those two
numbers are never the same, and they go wrong in both directions:

  TOO LONG.  Veo is usually right at the start and drifts later: the reaction
             completes and then keeps going, an extra electrode grows, the label
             the prompt banned appears in the last second. The usable part might
             be the first seven seconds of ten. That tail must be cut, not
             faded over, because it is wrong rather than merely surplus.

  TOO SHORT. Seven usable seconds under fifteen seconds of narration. The
             remaining eight have to come from somewhere, and where they come
             from is a teaching decision, not a technical one.

HOW THE SHORTFALL IS FILLED, AND WHY IT DEPENDS ON THE MOTION
-------------------------------------------------------------
    one_way   a process with a direction — rust spreading, a solution rising, a
              reaction proceeding. Slowed to fit, up to MAX_STRETCH; past that
              it is slowed to MAX_STRETCH and the final state is held. The end
              state is the answer, so holding it is not padding — it is the
              same thing a teacher does when they finish a diagram and leave it
              on the board.
    cyclic    a process with no end state — bubbles rising, current flowing,
              something oscillating. Looped, which is invisible when the motion
              genuinely cycles.
    settling  something arrives and stays. Held from the moment it settles.

**Nothing is ever reversed.** Boomerang is the obvious way to double a clip's
length and it is forbidden here, because almost every demonstration in this
track has a direction and reversing it teaches the opposite of the truth: rust
un-rusting, gas dissolving back into the electrode, a titration un-mixing. It
would also look completely fine to anyone not paying attention, which is what
makes it dangerous rather than merely wrong. See `animate-mechanisms`.

WHY BLEND INTERPOLATION AND NOT MOTION COMPENSATION
---------------------------------------------------
Slowing 2x by duplicating frames judders. `minterpolate` fixes that, but its
`mci` mode SYNTHESISES intermediate positions by warping — and a warp artefact
on a teaching diagram is not a blemish, it is a bubble that morphs into a
different shape or an electrode that bends. `blend` cross-dissolves instead: it
softens fast motion and cannot invent geometry. On the slow organic movement
these clips are for, it is both cheaper and safer.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

FPS = 30
MAX_STRETCH = 2.0        # past this a slowdown reads as slow motion, not as pace
MIN_USABLE = 1.5         # a clip good for less than this is not a clip
STRATEGIES = ("one_way", "cyclic", "settling")


class ConformError(RuntimeError):
    pass


def duration(path: Path) -> float:
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", str(path)],
        capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def plan(usable: float, need: float, strategy: str) -> list[str]:
    """The filter steps that turn `usable` seconds into exactly `need`.

    Split out from `conform` so it can be reasoned about and tested without
    encoding anything — the arithmetic is where this goes wrong, not the ffmpeg.
    """
    if strategy not in STRATEGIES:
        raise ConformError(f"unknown motion {strategy!r}; expected one of {STRATEGIES}")
    if usable < MIN_USABLE:
        raise ConformError(
            f"only {usable:.1f}s of this clip is usable, under the {MIN_USABLE}s "
            f"floor — there is nothing here to stretch, and stretching it would "
            f"only make the little that is right look wrong too")

    steps = [f"trim=0:{usable:.3f}", "setpts=PTS-STARTPTS"]
    if need <= usable + 0.05:
        # Enough already: take the FIRST `need` seconds. The front of a Veo clip
        # is its best part, so trimming from the end is the right end to trim.
        return [f"trim=0:{need:.3f}", "setpts=PTS-STARTPTS", f"fps={FPS}"]

    if strategy == "cyclic":
        # `loop` counts FRAMES, not seconds, and it loops the first `size` of
        # them. Feeding it a normalised framerate first is what makes that count
        # mean what it says.
        n = max(1, int(round(usable * FPS)))
        steps += [f"fps={FPS}", f"loop=loop=-1:size={n}:start=0",
                  f"trim=0:{need:.3f}", "setpts=PTS-STARTPTS"]
        return steps

    if strategy == "settling":
        steps += [f"fps={FPS}",
                  f"tpad=stop_mode=clone:stop_duration={need - usable:.3f}"]
        return steps

    # one_way: slow as far as is honest, then hold the finished state.
    stretch = min(need / usable, MAX_STRETCH)
    slowed = usable * stretch
    steps += [f"setpts={stretch:.5f}*PTS"]
    if stretch > 1.02:
        # blend, not mci — see the module header.
        steps += [f"minterpolate=fps={FPS}:mi_mode=blend"]
    else:
        steps += [f"fps={FPS}"]
    if need > slowed + 0.05:
        steps += [f"tpad=stop_mode=clone:stop_duration={need - slowed:.3f}"]
    return steps


def conform(src: Path, dest: Path, *, good_until: float | None, need: float,
            strategy: str = "one_way") -> dict:
    """Write `dest` as exactly `need` seconds of the usable part of `src`."""
    src, dest = Path(src), Path(dest)
    have = duration(src)
    if have <= 0:
        raise ConformError(f"{src} has no readable duration")
    usable = have if good_until is None else min(float(good_until), have)
    # A short clone-pad on the end of whatever the strategy produced, so `-t`
    # below always has frames to cut at. Without it the output lands a fraction
    # SHORT of the window, and those few frames show as a flash of bare plate
    # exactly where the clip should still be playing.
    #
    # The `fps` before it is not decoration and took a while to find. Measured:
    # 7.87s where 8.00s was asked for, with the pad present and doing nothing.
    # `minterpolate` emits timestamps that are not on a clean 1/FPS grid, so
    # tpad's clones inherit that grid and land past where `-t` cuts — the pad is
    # generated and then immediately discarded. Normalising first puts them
    # where `-t` can use them.
    steps = plan(usable, need, strategy) + [
        f"fps={FPS}", "tpad=stop_mode=clone:stop_duration=0.5"]

    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(".partial.mp4")
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-i", str(src),
         "-vf", ",".join(steps), "-an",
         # -t is a belt on top of the filter arithmetic: `tpad` and `loop` both
         # produce open-ended streams if a number above is off by a frame, and
         # an open-ended stream here would encode until the disk filled.
         "-t", f"{need:.3f}",
         "-c:v", "libx264", "-preset", "medium", "-crf", "19",
         "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(tmp)],
        check=True)

    got = duration(tmp)
    if abs(got - need) > 0.10:
        tmp.unlink(missing_ok=True)
        raise ConformError(
            f"conform produced {got:.2f}s where {need:.2f}s was asked for "
            f"(usable {usable:.2f}s, {strategy}). The window and the clip would "
            f"not line up, so nothing was written.")
    tmp.replace(dest)
    return {"src": str(src), "dest": str(dest), "had": round(have, 2),
            "usable": round(usable, 2), "need": round(need, 2),
            "strategy": strategy, "trimmed": round(have - usable, 2),
            "filters": ",".join(steps)}
