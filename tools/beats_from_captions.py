"""Run the visual director over a part's caption track.

    python tools/beats_from_captions.py che-c2-la-05 1
    video beats che-c2-la-05 --part 1          # same thing, through the CLI

The decisions live in `src/visual_director.py`; this is the loop that feeds it
caption windows and writes the beats file. Keeping the rules in one importable
module means they can be changed once and every video that is rebuilt picks them
up — which is the point of having a director at all, rather than a script that
happened to be run over one video by hand.

Figures are never regenerated. `apparatus`, `graph` and `image` blocks already in
the beats file are merged back in untouched, because which figure belongs where
is a judgement about the question rather than about a sentence.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.visual_director import (SYSTEM, merge_figures, merge_sequences,
                                 parse, prompt_for, with_build,
                                 with_presenter, with_reveal)

WINDOW = 5              # caption lines per decision
MIN_WINDOW = 3          # never leave a stub of one line at the end


def windows(lines, start, size=WINDOW):
    out, i = [], start
    while i < len(lines):
        end = min(i + size, len(lines))
        if len(lines) - end < MIN_WINDOW:
            end = len(lines)
        out.append((i, end))
        i = end
    return out


def run(project: str, part: str, window: int = WINDOW, log=print) -> int:
    from src.llm import complete

    root = Path("projects") / project
    lines = json.loads((root / f"lines_part{part}.json").read_text(encoding="utf-8"))
    meta = json.loads((root / "meta.json").read_text(encoding="utf-8"))
    cl = meta.get("card_lines", 0)
    start = int(cl[str(part)] if isinstance(cl, dict) else cl)
    prompt = prompt_for(meta.get("question", ""))

    out_path = root / f"beats_part{part}.json"
    existing = (json.loads(out_path.read_text(encoding="utf-8"))
                if out_path.exists() else [])

    generated, quiet = [], 0
    for lo, hi in windows(lines, start, window):
        text = "\n".join(l["text"] for l in lines[lo:hi])
        spec = parse(complete(SYSTEM, prompt + text))
        if spec is None:
            quiet += 1                      # a deliberate no-graphic decision
            continue
        spec["at"] = lo
        spec = with_reveal(spec, lo, hi)
        spec = with_build(spec, lo, hi)
        generated.append(with_presenter(spec))

    generated = merge_sequences(generated)
    beats = merge_figures(generated, existing)
    out_path.write_text(json.dumps(beats, ensure_ascii=False, indent=2),
                        encoding="utf-8")
    figs = sum(1 for b in beats if b.get("type") in {"apparatus", "graph", "image"})
    log(f"{project} part {part}: {len(beats)} beats over {len(lines)} caption "
        f"lines — {quiet} window(s) left visually quiet, {figs} figure(s) kept")
    return len(beats)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("project")
    p.add_argument("part")
    p.add_argument("--window", type=int, default=WINDOW)
    a = p.parse_args()
    run(a.project, a.part, a.window)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
