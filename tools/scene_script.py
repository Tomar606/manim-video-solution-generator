"""What a video WILL show, written out for approval before anything renders.

    python tools/scene_script.py che-c2-la-03           # one topic
    python tools/scene_script.py --all > scenes.md      # the whole batch

Every visual decision on this project has so far been reviewed by watching a
finished composite — and each change found that way costs a full render and
composite per part. The Daniell cell held one block for 59 of its 112 seconds
and nobody could see that until it was built.

So the plan is reviewable as text first. For each part this prints, in order:
the caption timeline, what is on screen against it, when each thing arrives, and
— the point of the exercise — every stretch where the screen is EMPTY or FROZEN,
with the words being spoken over it, so it is obvious what is missing and what
should replace it.

Read it as: "at 0:56 the teacher starts explaining ion movement, and the screen
shows the same comparison table it has shown since 0:54, for the next 57
seconds." That is a decision to take before rendering, not after.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, ".")
from tools.visual_gaps import gaps, static_spans          # noqa: E402


def mmss(t: float) -> str:
    return f"{int(t) // 60}:{int(t) % 60:02d}"


def part_script(root: Path, part: int) -> str:
    lines = json.loads((root / f"lines_part{part}.json").read_text(encoding="utf-8"))
    beats = sorted(json.loads((root / f"beats_part{part}.json").read_text(encoding="utf-8")),
                   key=lambda b: int(b["at"]))
    meta = json.loads((root / "meta.json").read_text(encoding="utf-8"))
    end = float(meta["clip_end"][str(part)])
    out = [f"\n### Part {part}  ({mmss(end)})\n"]

    for n, b in enumerate(beats):
        at = int(b["at"])
        start = float(lines[at]["start"])
        stop = float(lines[int(beats[n + 1]["at"])]["start"]) if n + 1 < len(beats) else end
        what = b.get("title") or b.get("label") or b.get("caption") or b.get("name") or ""
        out.append(f"**{mmss(start)}–{mmss(stop)}  {b['type']}**  {what}")
        said = " ".join(l["text"] for l in lines[at:at + 3])
        out.append(f"  > says: {said[:110]}")
        for key, label in (("items", "list"), ("tex", "maths")):
            for x in b.get(key, [])[:5]:
                out.append(f"     - {label}: {str(x)[:80]}")
        arrivals = [(int(r), "item") for r in b.get("reveal_at", [])]
        arrivals += [(int(l["at"]), f"label {l['text']}") for l in b.get("labels", [])]
        for i, kind in sorted(arrivals):
            out.append(f"     · {mmss(float(lines[min(i, len(lines) - 1)]['start']))} {kind}")
        out.append("")

    problems = []
    for a, z in gaps(root, part):
        said = " ".join(l["text"] for l in lines if a <= float(l["start"]) < z)
        problems.append(f"- **EMPTY {mmss(a)}–{mmss(z)}** ({z - a:.0f}s) — nothing on screen while: "
                        f"{said[:120]}")
    for a, z, what in static_spans(root, part):
        said = " ".join(l["text"] for l in lines if a <= float(l["start"]) < z)
        problems.append(f"- **FROZEN {mmss(a)}–{mmss(z)}** ({z - a:.0f}s) — `{what}` unchanged while: "
                        f"{said[:120]}")
    if problems:
        out.append("**Needs a decision:**")
        out += problems
        out.append("")
    return "\n".join(out)


def script_for(slug: str) -> str:
    root = Path("projects") / slug
    meta = json.loads((root / "meta.json").read_text(encoding="utf-8"))
    out = [f"\n## {slug} — {meta.get('question', '')[:90]}"]
    for f in sorted(root.glob("lines_part[0-9].json")):
        out.append(part_script(root, int(f.stem.split("part")[1])))
    return "\n".join(out)


def main() -> int:
    if "--all" in sys.argv:
        slugs = sorted(p.name for p in Path("projects").glob("che-*")
                       if (p / "meta.json").is_file() and list(p.glob("beats_part[0-9].json")))
    else:
        slugs = [a for a in sys.argv[1:] if not a.startswith("-")]
    for s in slugs:
        try:
            print(script_for(s))
        except (OSError, KeyError, json.JSONDecodeError) as e:
            print(f"\n## {s} — cannot read plan: {type(e).__name__}: {e}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
