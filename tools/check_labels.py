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


def main() -> int:
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    root = Path("projects") / sys.argv[1]
    part = int(sys.argv[2])
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
