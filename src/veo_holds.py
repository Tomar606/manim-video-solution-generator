"""Freeze a generated clip while a label is being read.

    holds = plan(beat, lines, start, end)
    apply_holds(clip, holds, out)

WHY
---
A label is typeset over a moving clip, and the clip keeps moving underneath it.
On a diagram that is exactly wrong: the student is being asked to find a named
part, and the part is drifting while the name arrives. The picture should stop,
the label should land on a still frame, and the motion should resume when the
teacher moves on.

HOW THE ARITHMETIC WORKS, because it is easy to get backwards
-------------------------------------------------------------
The beat owns a window of `W` seconds and that length is fixed — the narration
is already recorded against it. So a hold does not EXTEND the clip, it takes
time away from the motion:

    content time available  C = W - (sum of every hold)

The clip is conformed to `C` first, and the freezes are then inserted, so the
result is exactly `W` again. Insert first and conform after and the conform
speeds the freezes up along with everything else, which un-does them.

A hold is placed at the label's own arrival, so the picture stops on the frame
the label is describing. Because each hold shifts everything after it, the
position of hold `i` in the CONFORMED clip is its absolute arrival minus every
hold that already opened before it — `plan()` does that accumulation.

The freezes are made with the concat FILTER, not the concat demuxer: the demuxer
demands identical stream properties and returns exit 234 on a mismatch, which
cost an hour once already. Inside one graph the segments come from the same
decoder, so they match by construction.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

FPS = 30
MIN_HOLD = 0.25            # shorter than this is a stutter, not a pause


def plan(beat: dict, lines: list[dict], start: float, end: float) -> list[dict]:
    """Where to freeze the conformed clip, and for how long.

    Returns [{"at": seconds into the conformed clip, "hold": seconds}], in order.
    Labels with no `hold` do not stop the picture.
    """
    window = max(0.0, end - start)
    marked = []
    for spec in beat.get("labels") or []:
        hold = float(spec.get("hold", 0) or 0)
        if hold < MIN_HOLD:
            continue
        at = spec.get("at")
        arrives = start if at is None else float(
            lines[max(0, min(int(at), len(lines) - 1))]["start"])
        marked.append((min(max(arrives, start), end), hold))
    marked.sort()

    total = sum(h for _, h in marked)
    if total >= window:
        raise ValueError(
            f"holds total {total:.1f}s but the beat's window is only "
            f"{window:.1f}s — there would be no motion left to hold")

    out, shift = [], 0.0
    for arrives, hold in marked:
        pos = (arrives - start) - shift
        # a hold at the very end has nothing after it to resume into
        pos = min(max(pos, 0.0), max(0.0, window - total))
        out.append({"at": round(pos, 3), "hold": round(hold, 3)})
        shift += hold
    return out


def content_seconds(window: float, holds: list[dict]) -> float:
    """How long the clip itself must be so that window == motion + holds."""
    return max(0.1, window - sum(float(h["hold"]) for h in holds))


def apply_holds(clip: Path, holds: list[dict], out: Path, fps: int = FPS) -> Path:
    """Write `clip` with each freeze inserted. No holds means a plain copy."""
    clip, out = Path(clip), Path(out)
    if not holds:
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(clip),
                        "-c", "copy", str(out)], check=True)
        return out

    seg, n = [], 0
    prev = 0.0
    for h in holds:
        at, dur = float(h["at"]), float(h["hold"])
        if at > prev:
            seg.append(f"[0:v]trim={prev:.3f}:{at:.3f},setpts=PTS-STARTPTS[s{n}];")
            n += 1
        # One frame, held: `loop` repeats it, then PTS is rebuilt so the clone
        # frames carry real timestamps.
        #
        # `loop=loop=N` on a single frame emits N+1 frames — the original plus N
        # copies — so the count is dur*fps-1, not dur*fps. Getting that wrong put
        # one extra frame in every hold, and two holds made the beat 100ms longer
        # than the window it was conformed to fill.
        seg.append(
            f"[0:v]trim={at:.3f}:{at + 1.0 / fps:.4f},setpts=PTS-STARTPTS,"
            f"loop=loop={max(0, int(round(dur * fps)) - 1)}:size=1:start=0,"
            f"setpts=N/{fps}/TB[s{n}];")
        n += 1
        prev = at
    seg.append(f"[0:v]trim={prev:.3f},setpts=PTS-STARTPTS[s{n}];")
    n += 1
    chain = "".join(seg) + "".join(f"[s{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=0[v]"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(clip),
                    "-filter_complex", chain, "-map", "[v]",
                    "-r", str(fps), "-c:v", "libx264", "-crf", "17",
                    "-preset", "medium", "-pix_fmt", "yuv420p", str(out)], check=True)
    return out
