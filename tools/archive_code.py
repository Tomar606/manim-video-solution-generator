#!/usr/bin/env python3
"""Snapshot a video's code next to the video: final/<QID>/code/.

    python3 tools/archive_code.py <QID> <source> [<source> ...]

Each source (a folder or a file, repo-relative) is copied to
final/<QID>/code/<source>, keeping its repo path so it is obvious where it came
from — work/<slug>/ lands at final/<QID>/code/work/<slug>/. A re-run replaces
that source's snapshot, so the copy is always the code of the video that ships.

Media, node_modules and caches are left out: the video is already one folder up,
and a snapshot of a renderer's dependencies is 100 MB of nothing. The shared
process — tools/, tools/clip/, src/ — is NOT copied either; it exists once, and
code/SOURCES.md records which commit it was at.
"""
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SKIP_DIRS = {"node_modules", "__pycache__", "media", ".git"}
SKIP_EXT = {".mp4", ".mov", ".webm", ".mkv", ".wav", ".mp3", ".m4a", ".aac"}
SKIP_NAMES = {".DS_Store", "state.lock"}


def _ignore(_dir, names):
    return [n for n in names
            if n in SKIP_DIRS or n in SKIP_NAMES or Path(n).suffix.lower() in SKIP_EXT]


def snapshot(qid: str, sources: list[str]) -> Path:
    code = REPO / "final" / qid / "code"
    for rel in sources:
        src = REPO / rel
        if not src.exists():
            sys.exit(f"archive_code: no such source {rel}")
        dst = code / rel
        if dst.is_dir():
            shutil.rmtree(dst)
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.is_dir():
            shutil.copytree(src, dst, ignore=_ignore)
        else:
            shutil.copy2(src, dst)
    listed = sorted(p.relative_to(code).as_posix() + ("/" if p.is_dir() else "")
                    for p in code.glob("*/*"))
    head = subprocess.run(["git", "-C", str(REPO), "rev-parse", "--short", "HEAD"],
                          capture_output=True, text=True).stdout.strip() or "unknown"
    (code / "SOURCES.md").write_text(
        f"# Code for {qid}\n\n"
        f"Snapshot taken {datetime.now():%Y-%m-%d %H:%M} by tools/archive_code.py.\n\n"
        + "".join(f"- `{s}`\n" for s in listed)
        + f"\nShared process (tools/, tools/clip/, src/) is not copied; repo HEAD was `{head}` "
          "(tools/clip/ may be uncommitted at that point).\n"
          "Media, node_modules and caches are left out.\n")
    return code


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    out = snapshot(sys.argv[1], sys.argv[2:])
    print(f"code -> {out.relative_to(REPO)}")
