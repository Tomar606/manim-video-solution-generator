"""Verify every diagram label is named by the audio, at the moment it appears.

    python tools/check_labels.py che-c1-la-01 1

A figure label carries two risks and they are different. The first is being
WRONG — अर्धपारगम्य झिल्ली pointing at the capillary. The second is being
UNSYNCED — correct, but arriving while the presenter is talking about something
else, which reads to a student as the wrong label. Neither is visible in a
still, and both survive a render that looks fine when scrubbed.

So each label is checked against the caption track the video is cut to:

  spoken labels    the label's CUE must appear in the caption at its own index,
                   or the one either side of it. The cue defaults to the longest
                   word in the label — the most specific one — because matching
                   on any word passes "दाब मापक" against a caption that merely
                   says दाब, which is how an unspoken label slips through. Set
                   `"cue"` on the label to override.

  unspoken labels  some parts of a printed figure are never named aloud (the
                   गauge here). They are still part of the diagram the question
                   asks for, so they are allowed — but they must be declared
                   `"spoken": false` and must appear WITH the figure, not at some
                   later caption that would imply the presenter just named them.

Exits non-zero if any label fails, so preflight can refuse the render.
"""
from __future__ import annotations

import json
import sys
import unicodedata
from pathlib import Path

WINDOW = 1          # a label may land one caption early or late


def _norm(t: str) -> str:
    t = unicodedata.normalize("NFC", str(t))
    return t.replace("़", "").strip()


def cue_of(label: dict) -> str:
    if label.get("cue"):
        return _norm(label["cue"])
    words = [w.strip("।,?!—:;()") for w in _norm(label["text"]).split()]
    return max(words, key=len) if words else ""


def check(root: Path, part: int) -> list[str]:
    lines = json.loads((root / f"lines_part{part}.json").read_text(encoding="utf-8"))
    beats = json.loads((root / f"beats_part{part}.json").read_text(encoding="utf-8"))
    texts = [_norm(l.get("text", "")) for l in lines]
    problems = []

    for b in beats:
        if b.get("type") not in ("figure", "scan_figure"):
            continue
        for lab in b.get("labels", []):
            at, text = int(lab["at"]), lab["text"]
            if lab.get("spoken") is False:
                if at != int(b["at"]):
                    problems.append(
                        f"{text!r}: declared unspoken but appears at caption {at}, "
                        f"not with the figure at {b['at']}")
                continue
            cue = cue_of(lab)
            lo, hi = max(0, at - WINDOW), min(len(texts) - 1, at + WINDOW)
            # The label's OWN caption is checked first. Scanning the window in
            # order and comparing the first hit reports a false problem whenever
            # the cue runs across two captions — जिंक is said at 14 and again at
            # 15, and a label correctly sitting on 15 was flagged as belonging
            # at 14.
            if cue and 0 <= at < len(texts) and cue in texts[at]:
                continue
            hit = next((i for i in range(lo, hi + 1) if cue and cue in texts[i]), None)
            if hit is None:
                near = " | ".join(texts[i][:44] for i in range(lo, hi + 1))
                problems.append(
                    f"{text!r}: cue {cue!r} is not spoken at captions {lo}-{hi} "
                    f"({near})")
            elif hit != at:
                problems.append(
                    f"{text!r}: cue {cue!r} is spoken at caption {hit}, "
                    f"label is set to {at}")
    return problems


def _caption_at(lines: list, t: float) -> int:
    """Index of the caption on screen at absolute time `t`."""
    k = 0
    for i, l in enumerate(lines):
        if l["start"] <= t + 1e-6:
            k = i
    return k


def check_work(root: Path, part: int) -> list[str]:
    """The same check, for a video built on the headless-Chromium track.

    That track has no beats_part<N>.json. A diagram's labels live in
    spec/design.json with `t_in` in seconds from the start of their beat, and
    the beat owns a run of caption lines named in spec/anchors.json. So the
    label's caption index is not written down anywhere — it is RECOVERED: beat
    start + the label's own time, looked up against the caption track. That is
    also what makes the check honest rather than circular: it measures where the
    label actually lands, not where somebody meant to put it.

    Written because PROCESS.md step 5 names this file as its gate, and on
    BIO-C12-LA-02 it could not open a single file — the gate existed, could not
    run, and nothing said so.
    """
    lines = json.loads((root / "out" / f"lines_part{part}.json").read_text(encoding="utf-8"))
    anchors = json.loads((root / "spec" / "anchors.json").read_text(encoding="utf-8"))
    anchors = anchors.get(f"part{part}", {})
    design = {d["type"]: d for d in
              json.loads((root / "spec" / "design.json").read_text(encoding="utf-8"))}
    texts = [_norm(l.get("text", "")) for l in lines]
    wf = root / "out" / f"words_part{part}.json"
    words = json.loads(wf.read_text(encoding="utf-8")) if wf.is_file() else None
    problems = []
    for beat, (i, j) in anchors.items():
        d = design.get(beat, {})
        if not d.get("labels"):
            continue
        s0 = 0.0 if i == 0 else lines[i]["start"]
        end = lines[j + 1]["start"] if j + 1 < len(lines) else lines[j]["end"]
        k = (end - s0) / max(d.get("duration", end - s0), 0.1)   # build_spec's scale
        for lab in d["labels"]:
            text = lab["text"]
            # A WORD-ANCHORED label lands on that word's measured onset, which
            # is exactly how build_spec.py places it. Reading only `t_in` here
            # put every `wi` label at its beat's FIRST caption: labels named
            # late in a beat failed while correctly synced, and labels named
            # near the start passed without being checked at all.
            if "wi" in lab and words is not None:
                t = words[lab["wi"]]["s"] + float(lab.get("dt", 0.0))
            else:
                t = s0 + float(lab.get("t_in", 0.0)) * k
            at = _caption_at(lines, t)
            if lab.get("spoken") is False:
                if not (i <= at <= j):
                    problems.append(f"{beat}: {text!r} declared unspoken but lands at "
                                    f"caption {at}, outside its figure's {i}-{j}")
                continue
            cue = cue_of(lab)
            # the SAME ±WINDOW as the Manim-track check, not clamped to the
            # beat: a label may land one caption after the word that names it,
            # and that word is often the last line of the beat before.
            lo, hi = max(0, at - WINDOW), min(len(texts) - 1, at + WINDOW)
            if cue and cue in texts[at]:
                continue
            hit = next((n for n in range(lo, hi + 1) if cue and cue in texts[n]), None)
            if hit is None:
                near = " | ".join(texts[n][:40] for n in range(lo, hi + 1))
                problems.append(f"{beat}: {text!r} cue {cue!r} is not spoken at "
                                f"captions {lo}-{hi} ({near})")
    return problems


def main() -> int:
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    # a slug (projects/<slug>, the Manim track) or a path to work/<slug>
    arg, part = sys.argv[1], int(sys.argv[2])
    work = Path(arg) if (Path(arg) / "spec" / "anchors.json").is_file() else None
    if work is None and (Path("work") / arg / "spec" / "anchors.json").is_file():
        work = Path("work") / arg
    if work is not None:
        problems = check_work(work, part)
    else:
        root = Path("projects") / arg
        if not (root / f"beats_part{part}.json").is_file():
            # never a silent pass: a gate that finds nothing to check has failed
            print(f"[FAIL] {arg} part {part} — no beats_part{part}.json under "
                  f"{root} and no spec/anchors.json under work/{arg}: nothing to check")
            return 1
        problems = check(root, part)
    if problems:
        print(f"[FAIL] {sys.argv[1]} part {part} — {len(problems)} label problem(s)")
        for p in problems:
            print("   ", p)
        return 1
    print(f"[ok] {sys.argv[1]} part {part} — every label is named by the audio")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
