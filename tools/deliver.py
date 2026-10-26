"""The only way a reel reaches a Final folder: gates, answer page, copy, all or nothing.

    python tools/deliver.py <slug> [--hold 7] [--dry-run]
    python tools/deliver.py --pending          # every delivered reel still waiting for its answer page

1. Every part named by meta.json "parts" must exist as projects/<slug>/final/<slug_>_part<N>.mp4.
2. tools/gates.py runs on all of them. Any failure stops here and nothing is copied.
3. The last part gets the answer pages appended (tools/answer_outro.py --hold 7, --then for page 2),
   from projects/<slug>/assets/answer/<ID>-1.png, -2.png ... (tools/sheet_fetch.py puts them there).
   NO PAGE YET IS NOT A STOP: the reel is delivered without it and recorded as pending. --pending later
   looks for each pending page again (the whole sheet row, any column) and, when it is there, re-delivers
   that reel with the page appended. Nothing is re-rendered: the page goes on the end of the rendered part.
4. Each part is copied to its Final folder as 1.mp4, 2.mp4 ...; a file already there is moved to
   projects/<slug>/final/previous_<N>.mp4 first, so a re-delivery can be undone.
5. The delivered files are measured again (length, loudness) and the report is written to
   projects/<slug>/final/delivery.json.

WHERE: science goes to <root>/Final <Subject>/<ID — title>/, arts to <root>/Final Arts/Final <Subject>/
<ID — title>/. <root> is ~/Desktop unless DELIVER_ROOT says otherwise. The title is meta.json "title";
when it is missing, an existing folder for the same ID is reused, so a re-delivery keeps its name.

WHY ONE COMMAND: delivery used to be the last `cp` of a hand-written render script. Nothing stopped a
reel that failed its gates being copied, and the answer page depended on someone remembering --hold 7.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable
ARTS = {"History", "Geography", "Political Science", "Economics", "Sociology"}


def duration(f: Path) -> float:
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)],
                                capture_output=True, text=True).stdout.strip() or 0)


def dest_dir(meta: dict) -> Path:
    # DELIVER_ROOT (environment or .env): on many Windows PCs the visible Desktop lives inside OneDrive
    envf = ROOT / ".env"
    kv = dict(l.split("=", 1) for l in envf.read_text().splitlines() if "=" in l and not l.startswith("#")) if envf.exists() else {}
    root = Path(os.environ.get("DELIVER_ROOT") or kv.get("DELIVER_ROOT", "").strip().strip('"') or Path.home() / "Desktop")
    subject, qid = meta["subject"], meta.get("sheet_id", "")
    base = root / "Final Arts" / f"Final {subject}" if subject in ARTS else root / f"Final {subject}"
    if meta.get("title"):
        return base / f"{qid} — {meta['title']}"
    found = sorted(base.glob(f"{qid} — *")) if qid and qid != "pending" else []
    if found:
        return found[0]
    raise SystemExit(f'meta.json has no "title" and no folder for {qid} exists yet: add a short Hindi title, '
                     f'e.g. "title": "भक्ति संतों के उपदेश"')


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("slug", nargs="?")
    ap.add_argument("--pending", action="store_true", help="add answer pages that have turned up since delivery")
    ap.add_argument("--hold", type=float, default=7.0, help="seconds each answer page holds (the standard is 7)")
    ap.add_argument("--dry-run", action="store_true", help="check and report; copy nothing")
    a = ap.parse_args()
    if a.pending:
        return pending()
    if not a.slug:
        ap.error("give a slug, or --pending")
    proj = ROOT / "projects" / a.slug
    meta = json.loads((proj / "meta.json").read_text())
    stem = a.slug.replace("-", "_")
    parts = [proj / "final" / f"{stem}_part{n}.mp4" for n in range(1, int(meta.get("parts", 1)) + 1)]
    missing = [p.name for p in parts if not p.exists()]
    if missing:
        raise SystemExit(f"not rendered yet: {', '.join(missing)}")
    qid = meta.get("sheet_id", "")
    pages = sorted(p for p in (proj / "assets" / "answer").glob(f"{qid}-*.png") if not p.stem.endswith("_page"))
    if not pages:
        print(f"no answer page for {qid} yet: delivering without it, recorded as pending (tools/deliver.py --pending adds it later)")
    dest = dest_dir(meta)

    print(f"deliver {a.slug} -> {dest}")
    g = subprocess.run([PY, str(ROOT / "tools/gates.py"), a.slug, *map(str, parts)], cwd=ROOT)
    if g.returncode != 0:
        print("\nNOT DELIVERED: a gate failed (above). Fix it and run this again.")
        return 1
    if a.dry_run:
        print(f"\ndry run: gates pass; would deliver {len(parts)} part(s) with {len(pages)} answer page(s)")
        return 0

    dest.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    if Path("/opt/homebrew/lib").exists():                     # Pillow's shaping libraries on a Mac
        env["DYLD_LIBRARY_PATH"] = "/opt/homebrew/lib"
    report = {"slug": a.slug, "id": qid, "folder": str(dest), "parts": [],
              "answer_page": [p.name for p in pages] if pages else "pending"}
    for n, part in enumerate(parts, 1):
        out = dest / f"{n}.mp4"
        if out.exists():
            shutil.move(str(out), proj / "final" / f"previous_{n}.mp4")
        if n == len(parts) and pages:
            cmd = [PY, str(ROOT / "tools/answer_outro.py"), str(part), str(pages[0]), str(out), "--hold", str(a.hold)]
            for p in pages[1:]:
                cmd += ["--then", str(p)]
            if subprocess.run(cmd, cwd=ROOT, env=env).returncode != 0 or not out.exists():
                print(f"\nNOT DELIVERED: appending the answer page to part {n} failed (above).")
                return 1
        else:
            shutil.copy2(part, out)
        loud = subprocess.run([PY, str(ROOT / "tools/loudness_gate.py"), str(out)], capture_output=True, text=True)
        report["parts"].append({"file": out.name, "seconds": round(duration(out), 2), "loudness": loud.stdout.strip()})
        print(f"  {out.name}: {duration(out):.1f} s, {loud.stdout.strip()}")
    (proj / "final" / "delivery.json").write_text(json.dumps(report, ensure_ascii=False, indent=1))
    print(f"\nDELIVERED {len(parts)} part(s) to {dest}" + ("" if pages else "  (answer page PENDING)"))
    return 0


def pending() -> int:
    """Re-deliver every reel whose answer page was missing, once the page can be found."""
    waiting = []
    for rep in sorted((ROOT / "projects").glob("*/final/delivery.json")):
        if json.loads(rep.read_text()).get("answer_page") == "pending":
            waiting.append(rep.parent.parent.name)
    if not waiting:
        print("no delivered reel is waiting for an answer page")
        return 0
    still = []
    for slug in waiting:
        qid = json.loads((ROOT / "projects" / slug / "meta.json").read_text()).get("sheet_id", "")
        print(f"== {slug}: looking for the {qid} answer page")
        subprocess.run([PY, str(ROOT / "tools/sheet_fetch.py"), qid, "--project", slug, "--refresh"], cwd=ROOT)
        if any(p for p in (ROOT / "projects" / slug / "assets/answer").glob(f"{qid}-*.png") if not p.stem.endswith("_page")):
            if subprocess.run([PY, str(ROOT / "tools/deliver.py"), slug], cwd=ROOT).returncode != 0:
                still.append(slug)
        else:
            still.append(slug)
    print(f"\n{len(waiting) - len(still)} reel(s) now have their answer page; still pending: {', '.join(still) or 'none'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
