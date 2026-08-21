"""The Veo stage: beats marked `type: video` become checked, downloaded clips.

    video veo projects/che-c3-la-02 --part 1

WHAT IT DOES, IN ORDER, PER BEAT
--------------------------------
    write the prompt   -> src/veo_prompts.py, against the house skill
    audit it           -> mechanical checks, no model, before a credit is spent
    attach the plate   -> assets/backgrounds/<subject>.png, into Flow itself
    submit             -> the extension types it into Flow's editor
    wait               -> until a media URL Flow did not have before appears
    download           -> through the browser session, into the project
    review             -> src/veo_qc.py grades the frames
    revise and repeat  -> up to MAX_ATTEMPTS, then give up loudly

Nothing here needs the Flow tab to be visible or focused. See
`src/flow_bridge.py` and `flow/extension/background.js`.

WHY EACH CLIP IS SUBMITTED AND COLLECTED ONE AT A TIME
------------------------------------------------------
Flow will happily queue several generations at once, and the upstream bridge did
exactly that — then matched clips to scenes by reversing DOM order and hoping.
That is fine for an ad where every clip is of the same person in the same room;
it is not fine here, where clip 2 going into beat 3's slot means the student
watches the wrong process while the teacher describes this one. Submitting one
and waiting for exactly one new media key to appear makes the mapping a fact
rather than an inference. It costs wall-clock and nothing else, and the run is
unattended anyway.

WHY THE PLATE IS ATTACHED RATHER THAN DESCRIBED
-----------------------------------------------
The clip is spliced into the middle of a Manim render of the SAME background.
Any difference in that background — a shade, a grid offset, a brightness ramp —
reads as a jump cut at both ends of the window. Describing the background in
words guarantees that difference; uploading the exact PNG Manim renders removes
it. Skill §15, and check B in the visual review, both exist for this.
"""
from __future__ import annotations

import json
import shutil
import time
from pathlib import Path

from src import veo_conform, veo_labels, veo_prompts, veo_qc
from src.flow_bridge import FlowBridge, FlowError, inbox_dir, inbox_rel, settled

ROOT = Path(__file__).resolve().parent.parent
SELECTORS = ROOT / "flow" / "selectors.json"

MAX_ATTEMPTS = 3          # first try plus two revisions
GEN_SECONDS = 8           # what Flow actually produces; the window is fitted to
                          # it afterwards by src/veo_conform.py, so this is a
                          # hint about pacing rather than about length
MAX_ON_SCREEN = 25.0      # one generated clip held longer than this stops being
                          # a demonstration and becomes wallpaper
GENERATE_TIMEOUT = 900.0  # Flow takes minutes; a stuck queue takes forever
POLL_EVERY = 10.0
SETTLE_AFTER_SUBMIT = 3.0


class VeoError(RuntimeError):
    pass


def _selectors() -> dict:
    return json.loads(SELECTORS.read_text(encoding="utf-8"))


def _rel(p: Path) -> str:
    """A path to print. Short when the project lives under the repo, absolute
    when `--projects-dir` puts it somewhere else — `relative_to` raises rather
    than falling back, and a crash while printing a summary loses the whole run's
    results after every clip has already been paid for."""
    try:
        return str(p.relative_to(ROOT))
    except ValueError:
        return str(p)


def label_faults(labels: list[dict], *, full: bool) -> list[str]:
    """Labels that would land somewhere the frame is not theirs to use.

    Warnings rather than errors: the clip is already generated and paid for, and
    a label two pixels into the caption strip is a nudge in the beats file, not a
    reason to throw the run away. `tools/preflight.py` reports the same thing
    before the render, which is where it can still be acted on cheaply.
    """
    from src.veo_prompts import LAYOUT

    top = LAYOUT["caption_cut"] * veo_labels.FRAME_H
    # The floor depends on whether the presenter is there. With him on screen a
    # label below the halfway line is not "low", it is BEHIND HIM — invisible,
    # and invisible in a way no frame check downstream would catch, because the
    # label really was composited, just underneath. Only a beat that fades him
    # out gets the rest of the frame.
    floor = (LAYOUT["full_bottom"] if full else LAYOUT["presenter_top"]) * veo_labels.FRAME_H
    out = []
    for a in labels:
        if a["y"] < top:
            out.append(f"label {a['text']!r} sits in the caption strip "
                       f"(y={a['y']}, the strip ends at {int(top)})")
        if a["y"] + a["h"] > floor:
            out.append(
                f"label {a['text']!r} reaches past the usable floor "
                f"(y={a['y'] + a['h']}, floor {int(floor)})"
                + ("" if full else " — the presenter is on screen for this beat, "
                                  "so it would be hidden behind him. Either raise "
                                  "it or set `presenter: hidden` on the beat."))
        if a["x"] < 0 or a["x"] + a["w"] > veo_labels.FRAME_W:
            out.append(f"label {a['text']!r} runs off the side of the frame")
    for i, a in enumerate(labels):
        for b in labels[i + 1:]:
            if (a["start"] < b["end"] and b["start"] < a["end"]
                    and abs(a["x"] - b["x"]) < (a["w"] + b["w"]) / 2
                    and abs(a["y"] - b["y"]) < (a["h"] + b["h"]) / 2):
                out.append(f"labels {a['text']!r} and {b['text']!r} overlap "
                           f"while both are on screen")
    return out


def resolve(project: str) -> Path:
    p = Path(project)
    if not p.is_dir():
        p = ROOT / "projects" / project
    if not p.is_dir():
        raise VeoError(f"no project at {project}")
    return p


# --------------------------------------------------------------------------- #
# Reading the part
# --------------------------------------------------------------------------- #
def video_beats(root: Path, part: int) -> tuple[list[dict], list[dict], dict]:
    """The `type: video` beats of one part, with its caption track and meta."""
    beats_f = root / f"beats_part{part}.json"
    lines_f = root / f"lines_part{part}.json"
    for f in (beats_f, lines_f, root / "meta.json"):
        if not f.is_file():
            raise VeoError(f"{f} is missing — run the beats stage for part {part} first")
    beats = json.loads(beats_f.read_text(encoding="utf-8"))
    lines = json.loads(lines_f.read_text(encoding="utf-8"))
    meta = json.loads((root / "meta.json").read_text(encoding="utf-8"))
    vids = [b for b in beats if b.get("type") == "video"]
    for b in vids:
        if not b.get("brief"):
            raise VeoError(
                f"the video beat at caption {b.get('at')} has no `brief`. A Veo beat "
                f"is a judgement about the question, not about a sentence, so the "
                f"brief is hand-written: say what has to be SEEN moving and why "
                f"Manim cannot show it.")
    return vids, lines, meta


def window(beat: dict, beats: list[dict], lines: list[dict],
           clip_end: float) -> tuple[float, float]:
    """The absolute [start, end] this beat OWNS — what the clip must be fitted to.

    Note what does not appear here: how long the generated clip is. The window is
    set by the presenter, because he is the clock — it opens on the caption the
    beat is anchored to and closes when the next beat takes the screen. A ten
    second clip under fifteen seconds of narration does not get to end early and
    leave the student looking at a plate; it gets conformed to the fifteen. That
    is `src/veo_conform.py`'s job, and this function is what tells it the number.

    `seconds` on the beat overrides the slot, for a demonstration that should
    finish before the teacher does. MAX_ON_SCREEN is the guard for the opposite
    case: a beat with nothing after it inherits the whole rest of the part, and
    stretching eight generated seconds across a minute is not a demonstration.
    """
    at = int(beat["at"])
    start = float(lines[max(0, min(at, len(lines) - 1))]["start"])
    later = [int(b["at"]) for b in beats if int(b["at"]) > at]
    ceiling = float(lines[min(later)]["start"]) if later else clip_end
    slot = max(0.0, min(ceiling, clip_end) - start)
    want = float(beat["seconds"]) if beat.get("seconds") else min(slot, MAX_ON_SCREEN)
    return start, start + max(0.0, min(want, slot))


# --------------------------------------------------------------------------- #
# Driving one generation
# --------------------------------------------------------------------------- #
def _media_keys(bridge: FlowBridge) -> set[str]:
    return {m["key"] for m in bridge.call("list_media", timeout=60).get("media", [])}


def _media_url(bridge: FlowBridge, key: str) -> str:
    for m in bridge.call("list_media", timeout=60).get("media", []):
        if m["key"] == key:
            return m["url"]
    raise VeoError(f"media {key} vanished from the page before it could be downloaded")


def generate_one(bridge: FlowBridge, spec: dict, *, plate: Path | None,
                 sel: dict, label: str) -> str:
    """Submit one prompt and block until Flow has a clip that was not there before.

    Returns the new media key. The before/after key set is the whole mapping
    mechanism — see the module header.
    """
    bridge.call("attach", timeout=60)
    before = _media_keys(bridge)

    if plate is not None:
        bridge.set_status(stage="attaching background plate", detail=plate.name)
        bridge.call("set_image", paths=[str(plate)], selector=sel["plate_input"],
                    timeout=120)

    text = spec["prompt"]
    if spec.get("negative"):
        # Flow has no separate negative field; the house packs carry it inside
        # the prompt under its own heading, which is the form the tool was
        # tuned against.
        text = f"{text}\n\nNEGATIVE: {spec['negative']}"

    bridge.set_status(stage="typing the prompt", detail=label)
    bridge.call("set_prompt", text=text, selector=sel["prompt"], timeout=120)
    time.sleep(1.0)

    bridge.set_status(stage="submitting", detail=label)
    if sel.get("generate_selector"):
        bridge.call("click", selector=sel["generate_selector"], timeout=60)
    else:
        bridge.call("click", text=sel["generate_text"], timeout=60)

    time.sleep(SETTLE_AFTER_SUBMIT)
    deadline = time.time() + GENERATE_TIMEOUT
    while time.time() < deadline:
        left = int(deadline - time.time())
        bridge.set_status(stage="waiting for Flow to render",
                          detail=f"{label} — up to {left // 60}m {left % 60}s left")
        new = _media_keys(bridge) - before
        if new:
            # If Flow emitted several at once (it sometimes returns variants),
            # take the first — they are all this prompt's output.
            return sorted(new)[0]
        time.sleep(POLL_EVERY)
    raise VeoError(
        f"Flow produced nothing for {label} within {GENERATE_TIMEOUT / 60:.0f} minutes. "
        f"Check the tab: a generation that failed its own safety or quota check "
        f"shows an error in the UI and never emits a media URL.")


def fetch(bridge: FlowBridge, key: str, dest: Path) -> Path:
    """Download one media key through the browser session and file it.

    Chrome refuses an absolute path or a `..` in `filename`, so the clip lands
    in ~/Downloads/pyq_flow_inbox first and is moved here afterwards. Do not try
    to shortcut that — the refusal surfaces as a bare "download refused".
    """
    url = _media_url(bridge, key)
    name = f"{dest.stem}.mp4"
    bridge.set_status(stage="downloading", detail=name)
    bridge.call("download", url=url, filename=inbox_rel(name), timeout=600)

    src = inbox_dir() / name
    for _ in range(30):
        if src.is_file() and settled(src):
            break
        time.sleep(1.0)
    else:
        raise VeoError(f"the download never landed at {src}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(dest))
    return dest


# --------------------------------------------------------------------------- #
# The stage
# --------------------------------------------------------------------------- #
def run(project: str, part: int, *, attempts: int = MAX_ATTEMPTS,
        use_plate: bool = True, provider: str | None = None,
        bridge: FlowBridge | None = None) -> dict:
    root = resolve(project)
    beats, lines, meta = video_beats(root, part)
    all_beats = json.loads((root / f"beats_part{part}.json").read_text(encoding="utf-8"))
    if not beats:
        print(f"no `type: video` beats in part {part} — nothing for Veo to do")
        return {"clips": []}

    clip_end = float(meta["clip_end"][str(part)])

    # The three inputs a prompt is written from, in the order they carry weight.
    #   question   what was asked, and therefore what the answer owes the student
    #   accuracy   the CORRECTED answer. verification.md exists because every
    #              sheet answer checked so far has contained real errors, and an
    #              animation of a wrong answer is worse than no animation
    #   script     what the teacher actually says, so the clip illustrates the
    #              explanation being given rather than the topic in general
    question = meta.get("question", "")
    accuracy = ""
    for name in ("accuracy_brief.md", "verification.md"):
        f = root / name
        if f.is_file():
            accuracy = f.read_text(encoding="utf-8")[:6000]
            break
    script = ""
    for name in ("script_bhaag.md", "script.md"):
        f = root / name
        if f.is_file():
            script = f.read_text(encoding="utf-8")[:8000]
            break

    plate = veo_prompts.plate_for(meta.get("subject", "")) if use_plate else None
    sel = _selectors()
    out_dir = root / "veo"
    work = out_dir / "review"
    out_dir.mkdir(parents=True, exist_ok=True)

    own = bridge is None
    b = bridge or FlowBridge().start()
    results, reviews = [], []
    try:
        info = b.wait_for_worker(timeout=90)
        print(f"extension connected — flow tab: {info.get('tab')}")
        if not info.get("tab"):
            raise VeoError("no Google Flow tab is open. Open your Flow project in "
                           "any tab — it can stay in the background.")

        for n, beat in enumerate(beats, 1):
            label = f"part{part} beat@{beat['at']} ({n}/{len(beats)})"
            b.set_status(run=root.name, scene=label, stage="writing the prompt")
            print(f"\n=== {label} ===\n{beat['brief']}")

            full = beat.get("presenter") == "hidden"
            spec = veo_prompts.write_prompt(
                brief=beat["brief"], lines=lines, at=int(beat["at"]),
                subject=meta.get("subject", ""), question=question,
                accuracy=accuracy, full_frame=full,
                script=script, duration=GEN_SECONDS, provider=provider)

            history, clip, review = [], None, None
            for attempt in range(1, attempts + 1):
                bad = veo_prompts.audit(spec)
                if bad:
                    # Fixed before a credit is spent: these are the failures we
                    # already know the shape of, so paying Veo to demonstrate
                    # them again would be a waste.
                    print(f"  prompt audit found {len(bad)} problem(s); revising")
                    for line in bad:
                        print(f"    - {line}")
                    spec = veo_prompts.revise_prompt(spec, bad, provider=provider)

                print(f"  attempt {attempt}/{attempts}: submitting")
                key = generate_one(b, spec, plate=plate, sel=sel, label=label)
                dest = out_dir / f"part{part}_at{beat['at']:03d}_try{attempt}.mp4"
                clip = fetch(b, key, dest)

                b.set_status(stage="reviewing the frames", detail=dest.name)
                review = veo_qc.review(clip, spec, work=work, brief=beat["brief"],
                                       full_frame=full, provider=provider)
                review.update(attempt=attempt, clip=str(clip.relative_to(root)),
                              at=int(beat["at"]), prompt=spec["prompt"],
                              negative=spec.get("negative", ""))
                reviews.append(review)
                print(f"  review: {review['verdict']} — {review['summary']}")

                if review["verdict"] != "fail":
                    break
                defects = veo_qc.defect_lines(review)
                for d in defects:
                    print(f"    - {d}")
                history.append(spec)
                if attempt < attempts:
                    spec = veo_prompts.revise_prompt(spec, defects, provider=provider)

            start, end = window(beat, all_beats, lines, clip_end)
            # THE CLIP IS FITTED TO THE PRESENTER, NEVER THE OTHER WAY ROUND.
            # Flow returns a fixed ~8s and the presenter talks for as long as he
            # talks; the tail Veo hallucinated is cut here and the good part is
            # slowed, looped or held to cover the window. See src/veo_conform.py
            # for why the choice between those three is a teaching decision.
            motion = beat.get("motion", "one_way")
            if motion == "cyclic" and not review.get("loopable"):
                print("  ⚠ the beat says the motion is cyclic but the review says "
                      "this clip does not return to where it started; holding the "
                      "final state instead of looping a visible jump")
                motion = "settling"
            good = review.get("good_until")
            b.set_status(stage="fitting the clip to the window", detail=label)
            fitted = out_dir / f"part{part}_at{beat['at']:03d}.mp4"
            try:
                fit = veo_conform.conform(clip, fitted, good_until=good,
                                          need=end - start, strategy=motion)
                print(f"  fitted: {fit['had']}s generated, {fit['usable']}s usable"
                      + (f" ({fit['trimmed']}s of tail cut)" if fit["trimmed"] > 0.05
                         else "")
                      + f" -> {fit['need']}s on screen by {motion}")
                if review.get("tail_problem") and fit["trimmed"] > 0.05:
                    print(f"    the cut tail: {review['tail_problem']}")
            except veo_conform.ConformError as exc:
                # Not fatal: the unconformed clip is still on disk and still
                # reviewable, and a run that has already paid for every clip
                # should not end with nothing written.
                print(f"  ⚠ could not fit this clip to its window: {exc}")
                fit, fitted = None, clip
                review["verdict"] = "fail"
            # The one thing besides the animation allowed on screen. Typeset
            # here rather than generated, because Veo cannot set Devanagari —
            # see src/veo_labels.py.
            labels = veo_labels.build(beat, lines, start, end, out_dir / "labels",
                                      f"part{part}_at{beat['at']:03d}")
            for a in labels:
                # Stored project-relative, like `src`, so the project survives
                # being moved or rendered on another machine.
                a["png"] = str(Path(a["png"]).relative_to(root))
            for bad in label_faults(labels, full=full):
                print(f"  ⚠ {bad}")
            results.append({
                "at": int(beat["at"]),
                "start": round(start, 2),
                "end": round(end, 2),
                "src": str(fitted.relative_to(root)),
                "raw": str(clip.relative_to(root)),
                "full": full,
                "labels": labels,
                "fit": fit,
                "verdict": review["verdict"],
                "attempts": review["attempt"],
                # A `fail` still gets written out. Deleting it would leave the
                # part with a silent hole and nothing to look at; recorded as a
                # failure, it is a clip somebody can watch and overrule.
                "usable": review["verdict"] != "fail",
            })
    finally:
        b.set_status(stage="idle", scene=None, detail="")
        if own:
            try:
                b.call("detach", timeout=15)
            except FlowError:
                pass
            b.stop()

    (root / f"veo_prompts_part{part}.json").write_text(
        json.dumps([{"at": r["at"], "src": r["src"], "verdict": r["verdict"]}
                    for r in results], ensure_ascii=False, indent=2), encoding="utf-8")
    veo_qc.write_report(root / f"veo_review_part{part}.json", reviews)
    clips_f = root / f"clips_part{part}.json"
    clips_f.write_text(json.dumps(results, ensure_ascii=False, indent=2),
                       encoding="utf-8")

    bad = [r for r in results if not r["usable"]]
    print(f"\n{len(results)} clip(s) -> {_rel(clips_f)}")
    if bad:
        print(f"{len(bad)} did NOT pass the visual check after {attempts} attempts:")
        for r in bad:
            print(f"  beat@{r['at']}  {r['src']}")
        print(f"see {_rel(root / f'veo_review_part{part}.json')} "
              f"for what the review saw, and the sampled frames in "
              f"{_rel(work)}")
    return {"clips": results, "reviews": reviews}
