"""Everything a kit reel depends on, checked before the gates look at the video.

    python tools/kit_preflight.py <slug>

FAIL stops the gates; WARN prints. Each check is something that has gone wrong:
  * meta.json without marks, years, question, ID or title: the marks sticker, the year line, the delivery
    folder's name all come from it;
  * caption lines that are empty, out of order or past the end of the audio;
  * no answer page, so delivery would have nothing to append;
  * a plan still marked "hook": "exempt" after its Veo clips arrived (the exemption is only for while they
    are being generated);
  * a theme or plate the plan names that does not exist (the page silently falls back);
  * a photo on screen that is not in its folder's credits.json: the reels are sold, so every photo needs a
    licence record.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KIT = ROOT / "lab" / "kit_test"


def duration(f: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)],
                         capture_output=True, text=True).stdout.strip()
    return float(out) if out else 0.0


def photos_in(plan: dict) -> set[str]:
    found = set()
    for b in plan.get("beats", []):
        br = b.get("broll") or {}
        if br.get("photo"):
            found.add(br["photo"])
        for e in b.get("elements", []):
            if e.get("type") in ("photo", "inset") and e.get("src"):
                found.add(e["src"])
            if e.get("type") == "portraits":
                found |= {it[0] for it in e.get("items", [])}
            if e.get("type") == "rewrite":
                found |= {s[0] for s in e.get("subs", [])}
    return found


def credited(photo: str) -> bool:
    f = ROOT / "library/backgrounds/photos" / photo
    cj = f.parent / "credits.json"
    if not cj.exists():
        return False
    try:
        data = json.loads(cj.read_text())
    except ValueError:
        return False
    entries = [h for v in (data.values() if isinstance(data, dict) else [data]) for h in (v if isinstance(v, list) else [v])]
    return any(isinstance(h, dict) and h.get("file") == f.name for h in entries) or f.name in cj.read_text()


def main() -> int:
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    slug = sys.argv[1].rstrip("/").split("/")[-1]
    proj = ROOT / "projects" / slug
    rows: list[tuple[str, str, str]] = []
    add = lambda level, what, detail="": rows.append((level, what, detail))

    meta = {}
    try:
        meta = json.loads((proj / "meta.json").read_text())
    except (OSError, ValueError) as e:
        add("FAIL", "meta.json", str(e))
    for k in ("sheet_id", "subject", "question", "years", "title"):
        if not str(meta.get(k, "")).strip() or meta.get(k) == "pending":
            add("FAIL" if k != "title" else "WARN", f"meta.json {k}", "missing (tools/sheet_fetch.py fills most of it)")
    if not isinstance(meta.get("marks"), int):
        add("FAIL", "meta.json marks", "set it from the narration, e.g. 3; the question card's sticker needs it")

    parts = int(meta.get("parts", 1) or 1)
    for n in range(1, parts + 1):
        src, lines_f = proj / f"src/part{n}.mp4", proj / f"lines_part{n}.json"
        if not src.exists():
            add("FAIL", f"src/part{n}.mp4", "missing")
            continue
        try:
            lines = json.loads(lines_f.read_text())
        except (OSError, ValueError) as e:
            add("FAIL", lines_f.name, str(e)); continue
        if not lines:
            add("FAIL", lines_f.name, "empty"); continue
        if any("end" not in l or l["end"] <= l["start"] for l in lines):
            add("FAIL", lines_f.name, "a line has no end, or ends before it starts")
        if any(b["start"] < a["start"] for a, b in zip(lines, lines[1:])):
            add("FAIL", lines_f.name, "lines out of order")
        dur = duration(src)
        if dur and lines[-1]["end"] > dur + 0.5:
            add("FAIL", lines_f.name, f"last line ends at {lines[-1]['end']:.1f}s, the audio at {dur:.1f}s")

        plan_f = KIT / f"plan_{slug.replace('-', '_')}_p{n}.json"
        if not plan_f.exists():
            add("FAIL", plan_f.name, "missing: run the plan generator")
            continue
        plan = json.loads(plan_f.read_text())
        clips = {(b.get("broll") or {}).get("clip") for b in plan.get("beats", [])} - {None}
        if plan.get("hook") == "exempt" and clips:
            add("FAIL", f"{plan_f.name} hook", '"hook": "exempt" is only for while the clips are generated; remove it')
        if plan.get("theme") and not (KIT / "themes" / f"{plan['theme']}.css").exists():
            add("FAIL", f"{plan_f.name} theme", f"themes/{plan['theme']}.css does not exist")
        if plan.get("plate") and not (ROOT / "library/backgrounds/plates/generated" / f"{plan['plate']}.jpg").exists():
            add("FAIL", f"{plan_f.name} plate", f"{plan['plate']}.jpg does not exist")
        missing = [p for p in sorted(photos_in(plan)) if not (ROOT / "library/backgrounds/photos" / p).exists()]
        if missing:
            add("FAIL", f"{plan_f.name} photos", "not on disk: " + ", ".join(missing[:4]))
        uncredited = [p for p in sorted(photos_in(plan) - set(missing)) if not credited(p)]
        if uncredited:
            add("FAIL", f"{plan_f.name} licences", "no credits.json entry: " + ", ".join(uncredited[:4]))

    # the page belongs on screen at the narrator's cue ("screenshot लो", "notes button में"), not only appended
    last = KIT / f"plan_{slug.replace('-', '_')}_p{parts}.json"
    if last.exists() and '"type": "page"' not in last.read_text():
        add("WARN", f"{last.name} answer page", "no page element: show the answer page at the narrator's cue (STANDARD.md)")

    qid = meta.get("sheet_id", "")
    pages = [p for p in (proj / "assets/answer").glob(f"{qid}-*.png") if not p.stem.endswith("_page")] if qid else []
    if not pages:
        add("WARN", "answer page", f"none yet for {qid}: the reel delivers without it and tools/deliver.py --pending adds it later")

    for level, what, detail in rows:
        print(f"  {level:4s} {what}" + (f": {detail}" if detail else ""))
    bad = [r for r in rows if r[0] == "FAIL"]
    print(f"FAIL {len(bad)} problem(s)" if bad else f"ok {slug}: meta, captions, plans, answer page, licences")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
