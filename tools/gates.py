"""Every gate, one command. Nothing ships without passing this.

    python tools/gates.py <slug> [final_video.mp4 ...]

WHY THIS EXISTS
---------------
The gates were there and the video still shipped wrong, twice over, because
running them was a separate act of remembering. Three things went wrong that
this removes:

1. A VIDEO BUILT OFF THE PIPELINE NEVER MEETS THEM. A hand-written scene and a
   hand-rolled composite have no step that calls a gate, so the gates were
   simply not on the path. One command that takes a slug is on every path.

2. A WRONG INVOCATION LOOKS LIKE A PASS. `preflight.py` prepends `projects/`
   itself, so `preflight.py projects/<slug>` checks `projects/projects/<slug>` —
   a directory that does not exist — and reports almost nothing. That is
   indistinguishable from a clean run. Every gate here is given the argument
   shape it actually wants, and a gate whose target is missing FAILS.

3. "NOT APPLICABLE" LOOKED THE SAME AS "PASSED". A gate that quietly does
   nothing teaches you to trust a report that checked nothing. Skips are printed
   with the reason they were skipped, and counted separately from passes.

Exit status is 1 if any gate failed, so this can be the last line of a build.

THE KIT'S GATES ONLY (26 Oct 2026). The retired tracks' gates (plate, font, figure anchor, layout, route,
avatar cover, sfx registry, Veo logo, chip label) either skipped on every kit reel or passed without
checking anything, which made a pass mean less than it said. They are preserved at the tag
archive/pre-kit. What runs now: kit_preflight, answer page, dashes, output, avatar shape, face, kit Veo,
loudness. The layout check that matters runs on the stills (stills.mjs) and frames (frames.mjs).
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable

# face_gate imports facenet-pytorch, which lives in .venv-tools; everything
# else is happy under whichever interpreter the build used.
_TOOLS_PY = ROOT / ".venv-tools" / "bin" / "python"
# font_gate needs manimpango, which lives in .venv-manim and NOT in .venv-tools.
# Run under the wrong one it cannot resolve any face, prints "cannot verify
# fonts", and then FAILS anyway — so a correct video failed because the checking
# library was missing, not because the font was. Same shape as face_gate needing
# facenet: each gate runs under the interpreter that can actually check it.
_MANIM_PY = ROOT / ".venv-manim" / "bin" / "python"
INTERPRETERS = {}
if _TOOLS_PY.exists():
    INTERPRETERS["face_gate"] = str(_TOOLS_PY)
    INTERPRETERS["answer_page_gate"] = str(_TOOLS_PY)
    # needs facenet-pytorch, same as face_gate
    INTERPRETERS["avatar_shape_gate"] = str(_TOOLS_PY)
    # needs Pillow, which only the tools venv has
    INTERPRETERS["figure_anchor_gate"] = str(_TOOLS_PY)
if _MANIM_PY.exists():
    INTERPRETERS["font_gate"] = str(_MANIM_PY)
# Gates that live outside tools/. face_gate belongs to the Veo character kit,
# which is packaged on its own so another machine can set it up from one folder.
SCRIPTS = {"face_gate": ROOT / "veo_kit" / "face_gate.py"}


def _presenter_times(proj, dur: float) -> list[float]:
    """Midpoints of the scenes the presenter is actually on screen in.

    Falls back to an even spread when the timings cannot be read, so the gate
    still runs rather than silently checking nothing.
    """
    import json as _json
    try:
        spec = _json.loads((proj / "reel.json").read_text(encoding="utf-8"))
        work = proj / "work" / "reel"
        at, mids = 0.0, []
        for i, sc in enumerate(spec["scenes"]):
            mid = work / f"mid_{i:02d}.mp4"
            d = _duration(mid) or 0.0
            if not sc.get("broll"):
                mids.append(at + d / 2)
            at += d
            br = work / f"br_{i + 1:02d}.mp4"
            if br.is_file():
                at += _duration(br) or 0.0
        mids = [m for m in mids if 0 < m < dur]
        if len(mids) >= 3:
            step = max(1, len(mids) // 7)
            return [round(m, 1) for m in mids[::step]][:7]
    except Exception:                                   # noqa: BLE001
        pass
    return [round(dur * f, 1) for f in (0.12, 0.25, 0.38, 0.5, 0.62, 0.75, 0.88)]

def _face_window(proj, video, dur: float) -> float:
    """How far into the video the presenter can still be looked for.

    Once the answer page comes up it covers the frame to the end, so a gate
    sampling an even spread across a `.withanswer` cut scores two or three
    frames of a sheet of paper. It found no face in them and reported "only 1
    usable face" on a video whose presenter was fine throughout — the same
    shape of false failure as the villager at the ballot box that
    `_presenter_times` fixes.

    So the window stops at the cue. The cue matcher is the one answer_overlay
    used to put the page there in the first place, so the two cannot drift.
    """
    if ".withanswer" not in Path(video).name:
        return dur
    try:
        sys.path.insert(0, str(ROOT / "tools"))
        from answer_overlay import cue_time            # noqa: PLC0415
        part = sorted(proj.glob("lines_part*.json"),
                      key=lambda q: int(q.stem.split("part")[-1]))[-1]
        at = cue_time(json.loads(part.read_text(encoding="utf-8")))
        if at and 0 < at < dur:
            return at
    except Exception:                                   # noqa: BLE001
        pass
    return dur


def _duration(path) -> float | None:
    """Seconds, or None if ffprobe cannot read it.

    Used to refuse an avatar-cover comparison between two different videos —
    see the note at the call site.
    """
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(path)], capture_output=True, text=True)
    try:
        return float(out.stdout.strip())
    except (TypeError, ValueError):
        return None


class Run:
    def __init__(self):
        self.passed, self.failed, self.skipped = [], [], []

    def gate(self, name: str, args: list[str], *, need: Path | None = None,
             why_skip: str | None = None):
        if why_skip:
            self.skipped.append((name, why_skip))
            print(f"  SKIP  {name:22s} {why_skip}")
            return
        if need is not None and not need.exists():
            self.failed.append((name, f"target missing: {need}"))
            print(f"  FAIL  {name:22s} target missing: {need}")
            return
        # SOME GATES NEED A DIFFERENT INTERPRETER. The builds run this under
        # .venv-manim, which has manimpango for font_gate but not the face
        # model; .venv-tools has the face model but no manimpango. Rather than
        # merge two environments, each gate names the one it needs.
        interp = INTERPRETERS.get(name, PY)
        script = SCRIPTS.get(name, ROOT / "tools" / f"{name}.py")
        r = subprocess.run([interp, str(script), *args],
                           cwd=ROOT, capture_output=True, text=True)
        out = (r.stdout + r.stderr).strip().splitlines()
        tail = "; ".join(l.strip() for l in out[-2:]) if out else ""
        if r.returncode == 0:
            self.passed.append(name)
            print(f"  ok    {name:22s} {tail[:90]}")
        else:
            self.failed.append((name, tail))
            print(f"  FAIL  {name:22s} {tail[:140]}")
            for l in out[-12:]:
                print(f"          {l.strip()}")


def main() -> int:
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    # accept a slug or a path and normalise, so the preflight trap cannot recur
    slug = sys.argv[1].rstrip("/").split("/")[-1]
    proj = ROOT / "projects" / slug
    if not proj.is_dir():
        print(f"  no such project: {slug}")
        return 1
    videos = [Path(a) for a in sys.argv[2:]]
    if not videos:
        videos = sorted((proj / "final").glob("*.mp4")) if (proj / "final").is_dir() else []

    print(f"gates — {slug}")
    r = Run()
    r.gate("kit_preflight", [slug])
    # IS THE ANSWER PAGE THE HOUSE SHEET, AND THIS QUESTION'S? Three wrong
    # pages reached a delivered list before a person spotted them by eye: a
    # scan of the printed textbook (which carried the watermark, so "has a
    # watermark" was not the test it was taken for), generated mock pages left
    # over from an early probe, and one answer held three times under three
    # filenames. See the note at the top of tools/answer_page_gate.py.
    r.gate("answer_page_gate", [slug])
    r.gate("dash_gate", [f"projects/{slug}"])



    if not videos:
        r.gate("output_gate", [], why_skip="no final video given or found")
    # THE ALL-VEO ROUTE HAS NO SIDECAR AND NEEDS NONE. The sidecar records where
    # a presenter was keyed into a panel; on this route the scene IS the
    # presenter, full frame, so there is no placement to record. reel.json
    # beside the project is what distinguishes the two. Skipped out loud — a
    # gate that quietly did not apply looks exactly like one that passed.
    all_veo = (proj / "reel.json").is_file()
    for v in videos:
        geom = Path(str(v) + ".geom.json")
        if not geom.exists() and all_veo:
            r.gate("output_gate", [str(v)],
                   why_skip="all-Veo route — full-frame scenes, no panel "
                            "placement to verify, so no geometry sidecar")
        elif not geom.exists():
            r.failed.append(("output_gate", f"no geometry sidecar beside {v.name}"))
            print(f"  FAIL  {'output_gate':22s} no geometry sidecar beside {v.name} "
                  f"— copy it from the compositor's output")
        else:
            r.gate("output_gate", [str(v)])

    import re as _re

    def _part_of(v):
        m = _re.search(r"part(\d+)", Path(v).name)
        return m.group(1) if m else None


    # AND HE MUST BE THE SHAPE HE ACTUALLY IS. A cut shipped with him squeezed
    # to 82% of his true width, because a circle and a card were filled by
    # resizing a 760x620 crop straight into them. Compares his face geometry in
    # the final against the plate it was cut from: same man, same lens, so any
    # difference is the compositor's.
    if videos:
        for v in videos:
            n = _part_of(v)
            src = next((s for s in (proj / "src" / f"part{n}.mp4",
                                    proj / "src" / f"{slug}_part{n}.mp4")
                        if n and s.exists()), None)
            if src is None:
                r.gate("avatar_shape_gate", [],
                       why_skip=f"no source plate found for {v.name}")
                continue
            r.gate("avatar_shape_gate", [str(v), str(src)])
    else:
        r.gate("avatar_shape_gate", [],
               why_skip="no final video given or found")

    # THE PRESENTER MUST BE THE REAL MAN. Measured, not judged: a face
    # embedding against assets/character/ritesh_reference.jpeg. Calibrated on
    # HIS-C2-SA-06, which shipped with three different men in it — his own
    # frames score a median 0.94 and the two generated strangers 0.86, and one
    # impostor frame reaches 0.901, which is why the decision is the MEDIAN and
    # not any single frame.
    if videos:
        ref = ROOT / "assets" / "character" / "ritesh_reference.jpeg"
        if not ref.is_file():
            r.gate("face_gate", [], why_skip="no character reference on disk")
        else:
            for v in videos:
                dur = _duration(v) or 0.0
                if dur < 8:
                    r.gate("face_gate", [], why_skip=f"{v.name} is too short to sample")
                    continue
                # SAMPLE WHERE HE IS SUPPOSED TO BE. On the all-Veo route some
                # scenes are cutaways with no presenter in them at all — an
                # empty railway platform, a crowd, a villager at a ballot box.
                # Spread evenly, the gate scored a VILLAGER'S face against his
                # reference, got -0.162, and reported "this is not him" on a
                # video that was correct. So on that route the sample points
                # come from the scenes he is actually in.
                # and never past the moment the answer page takes the frame
                win = _face_window(proj, v, dur)
                at = _presenter_times(proj, win) if (proj / "reel.json").is_file() \
                    else [round(win * f, 1) for f in
                          (0.12, 0.25, 0.38, 0.5, 0.62, 0.75, 0.88)]
                # NOR WHERE A FULL-FRAME PAGE COVERS HIM. The kit can show the official answer pages mid-video
                # (PHY Wheatstone, 23 Oct 2026); its geometry sidecar lists those stretches, and a sample that
                # lands in one moves to just before it. Scoring a sheet of paper dropped the median to 0.899.
                geo = Path(str(v) + ".geom.json")
                covered = json.loads(geo.read_text()).get("covered", []) if geo.is_file() else []
                merged = []                                   # back-to-back pages are one covered stretch
                for a_, b_ in sorted(covered):
                    if merged and a_ <= merged[-1][1] + 0.05:
                        merged[-1][1] = max(merged[-1][1], b_)
                    else:
                        merged.append([a_, b_])
                for a_, b_ in merged:
                    at = [round(max(0.5, a_ - 1.0), 1) if a_ <= x <= b_ else x for x in at]
                r.gate("face_gate", [str(v), "--min", "0.90", "--at", *map(str, at)])
    else:
        r.gate("face_gate", [], why_skip="no final video given or found")


    # the kit keeps its clips in veo/clean, which veo_logo_gate cannot see
    r.gate("kit_veo_gate", [slug])

    # one reel too quiet beside the last reads as broken; a peak over full scale distorts on a phone
    for v in videos:
        r.gate("loudness_gate", [str(v)])


    print()
    print(f"  {len(r.passed)} passed · {len(r.failed)} failed · {len(r.skipped)} skipped")
    for n, w in r.failed:
        print(f"    FAILED {n}: {w[:120]}")
    return 1 if r.failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
