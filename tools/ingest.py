"""The front door. One place to drop a HeyGen delivery, one command to check it.

    python tools/ingest.py BIO-C5-LA-01          # read, measure, gate, write manifest
    python tools/ingest.py --survey              # what is in inbox/ right now
    python tools/ingest.py BIO-C5-LA-01 --tidy   # show the renames (dry run)
    python tools/ingest.py BIO-C5-LA-01 --tidy --apply    # perform them

WHY THIS EXISTS
---------------
Every build so far started by working out, by hand, which file was which. The
delivery for BIO-C5-LA-01 arrived in two folders using two different naming
conventions, and the build log records that the folder names "were not trusted"
— the parts had to be identified by transcribing them and reading what the
presenter said. That is a ten-minute job that a filename should have answered.

Worse, the names are actively misleading. `BIO-C5-LA-01_part1_caption.mp4` is
NOT the presenter clip: it is the same take with captions burned in. Glob for
`*.mp4` and you get both, and half the time you get the wrong one.

So this reads whatever arrived, under any of the six naming conventions seen in
this repo, measures every file with ffprobe rather than trusting the handover,
cross-checks them against each other, and writes one manifest that every later
stage reads instead of guessing.

WHAT IT REFUSES TO PASS
-----------------------
Exit code 1 — this is gate 1, and nothing downstream should run without it:

  * no presenter clip found for a part
  * two clips claiming the same part
  * a clip whose audio or captions disagree with it by more than a second
    (that is the shape of an SRT belonging to a different take)

Warnings (exit 0) cover things that are odd but survivable: a missing script, a
duplicate-looking `(1)` file, parts shot at different resolutions.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INBOX = ROOT / "inbox"
WORK = ROOT / "work"

VIDEO_EXT = {".mp4", ".mov", ".webm", ".mkv"}
AUDIO_EXT = {".mp3", ".wav", ".m4a", ".aac", ".flac"}
CAPTION_EXT = {".srt", ".vtt"}
DOC_EXT = {".pdf", ".docx", ".txt", ".md"}
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp"}

# A clip and its captions must agree this closely or the SRT is from another take.
DURATION_TOL = 1.0
SKIP_NAMES = {".DS_Store", ".gitkeep"}


def norm(name: str) -> str:
    """Lowercase, and flatten every separator this repo has used to one space.

    `BIO-C2-LA-01-part_1`, `BIO-C2-LA-01 part2_1080p`, `PHY-C1-LA-02_-_part_1`
    and `kmno4_parts_-_1` all have to end up somewhere a single regex can read.
    """
    return re.sub(r"[\s_\-]+", " ", name.lower()).strip()


def part_of(path: Path, base: Path) -> int | None:
    """Which part is this? Read the filename, then the folders above it.

    The number is only ever taken from AFTER the word "part", so the `01` in a
    qid like BIO-C2-LA-01 and the `1080` in a `_1080p` suffix cannot be mistaken
    for one.
    """
    candidates = [path.stem] + [p.name for p in path.relative_to(base).parents if p.name]
    for cand in candidates:
        m = re.search(r"\bparts?\s*(\d+)", norm(cand))
        if m:
            return int(m.group(1))
    return None


def probe(path: Path) -> dict:
    """Measure the file. Never trust what the handover said it was."""
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "format=duration,size:stream=codec_type,codec_name,width,height,r_frame_rate,nb_frames",
         "-of", "json", str(path)],
        capture_output=True, text=True,
    )
    if out.returncode != 0:
        return {"error": out.stderr.strip().splitlines()[-1] if out.stderr else "ffprobe failed"}

    data = json.loads(out.stdout or "{}")
    fmt = data.get("format", {})
    info: dict = {"bytes": int(fmt.get("size", 0))}
    if fmt.get("duration"):
        info["duration"] = round(float(fmt["duration"]), 3)

    for stream in data.get("streams", []):
        if stream.get("codec_type") == "video" and "width" not in info:
            info["width"] = stream.get("width")
            info["height"] = stream.get("height")
            info["codec"] = stream.get("codec_name")
            rate = stream.get("r_frame_rate", "0/1")
            if "/" in rate:
                num, den = rate.split("/")
                if float(den):
                    info["fps"] = round(float(num) / float(den), 3)
            if stream.get("nb_frames"):
                info["frames"] = int(stream["nb_frames"])
        elif stream.get("codec_type") == "audio" and "audio_codec" not in info:
            info["audio_codec"] = stream.get("codec_name")
    return info


def srt_end(path: Path) -> float | None:
    """Last timestamp in an SRT, in seconds — what the captions think the take is."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    stamps = re.findall(r"(\d{2}):(\d{2}):(\d{2})[,.](\d{3})", text)
    if not stamps:
        return None
    h, m, s, ms = stamps[-1]
    return round(int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000, 3)


def classify(path: Path) -> str:
    """What is this file for? Order matters — the caption-video trap is first.

    A `*_caption.mp4` is the take with captions burned in. It is never the plate,
    and treating it as one has already cost a build.
    """
    ext = path.suffix.lower()
    stem = norm(path.stem)
    if ext in VIDEO_EXT and "caption" in stem:
        return "caption_video"
    if ext in CAPTION_EXT:
        return "captions"
    if ext in AUDIO_EXT:
        return "audio"
    if ext in VIDEO_EXT:
        return "clip"
    if ext in DOC_EXT:
        return "script" if "script" in stem else "doc"
    if ext in IMAGE_EXT:
        return "image"
    return "other"


def collect(folder: Path) -> tuple[dict, list[str], list[str]]:
    """Walk a drop folder and sort everything into the manifest shape."""
    parts: dict[int, dict] = {}
    loose: dict[str, list] = {"scripts": [], "docs": [], "images": [], "unassigned": [], "ignored": []}
    warnings: list[str] = []
    errors: list[str] = []

    for path in sorted(folder.rglob("*")):
        if not path.is_file() or path.name in SKIP_NAMES:
            continue
        rel = str(path.relative_to(ROOT))
        kind = classify(path)

        if re.search(r"\(\d+\)", path.stem):
            warnings.append(f"looks like a duplicate copy: {path.name}")

        if kind in {"script", "doc"}:
            loose["scripts" if kind == "script" else "docs"].append(rel)
            continue
        if kind == "image":
            loose["images"].append(rel)
            continue
        if kind == "caption_video":
            loose["ignored"].append({"path": rel, "why": "captions burned in — not the plate"})
            continue
        if kind == "other":
            loose["ignored"].append({"path": rel, "why": "unrecognised type"})
            continue

        n = part_of(path, folder)
        if n is None:
            # One clip and no part number anywhere is a single-part video.
            loose["unassigned"].append({"path": rel, "kind": kind})
            continue

        entry = parts.setdefault(n, {"part": n})
        if kind in entry:
            errors.append(f"two files claim part {n} {kind}: "
                          f"{Path(entry[kind]['path']).name} and {path.name}")
            continue
        entry[kind] = {"path": rel, **probe(path)}

    # A lone unassigned clip is part 1. More than one and we refuse to guess.
    stray_clips = [u for u in loose["unassigned"] if u["kind"] == "clip"]
    if len(stray_clips) == 1 and not parts:
        c = Path(ROOT / stray_clips[0]["path"])
        parts[1] = {"part": 1, "clip": {"path": stray_clips[0]["path"], **probe(c)}}
        for u in list(loose["unassigned"]):
            if u["kind"] != "clip":
                p = Path(ROOT / u["path"])
                parts[1][u["kind"]] = {"path": u["path"], **probe(p)}
                loose["unassigned"].remove(u)
        loose["unassigned"] = [u for u in loose["unassigned"] if u["kind"] != "clip"]
        warnings.append("no part number in any filename — treated as a single-part video")
    elif len(stray_clips) > 1:
        errors.append(f"{len(stray_clips)} clips with no part number in the name — "
                      f"rename them part1/part2/... so they can be told apart")

    return {"parts": parts, **loose}, warnings, errors


def crosscheck(parts: dict) -> tuple[list[str], list[str]]:
    """The gate proper: does each part's own material agree with itself?"""
    warnings: list[str] = []
    errors: list[str] = []
    shapes: set[tuple] = set()

    for n in sorted(parts):
        p = parts[n]
        clip = p.get("clip")
        if not clip:
            errors.append(f"part {n} has no presenter clip")
            continue
        if "error" in clip:
            errors.append(f"part {n} clip unreadable: {clip['error']}")
            continue

        dur = clip.get("duration")
        if clip.get("width"):
            shapes.add((clip["width"], clip["height"], clip.get("fps")))

        if (aud := p.get("audio")) and dur and aud.get("duration"):
            delta = abs(aud["duration"] - dur)
            if delta > DURATION_TOL:
                errors.append(f"part {n}: audio is {delta:.2f}s from the clip "
                              f"({aud['duration']:.2f} vs {dur:.2f}) — different takes?")

        if (cap := p.get("captions")) and dur:
            end = srt_end(ROOT / cap["path"])
            if end is not None:
                cap["last_cue"] = end
                delta = abs(end - dur)
                if delta > DURATION_TOL:
                    errors.append(f"part {n}: captions end {delta:.2f}s from the clip "
                                  f"({end:.2f} vs {dur:.2f}) — this SRT is from another take")
        elif not cap:
            warnings.append(f"part {n} has no SRT — the clock comes from whisper anyway, "
                            f"but there is nothing to check the wording against")

    if len(shapes) > 1:
        warnings.append(f"parts were not all shot the same: {sorted(shapes)}")
    return warnings, errors


def tidy_plan(folder: Path, manifest: dict) -> list[tuple[Path, Path]]:
    """What the files WOULD be renamed to. Nothing is moved until --apply."""
    moves: list[tuple[Path, Path]] = []
    ext_for = {"clip": None, "captions": None, "audio": None}
    for n, p in sorted(manifest["parts"].items()):
        for kind in ext_for:
            if not (item := p.get(kind)):
                continue
            src = ROOT / item["path"]
            suffix = {"clip": "", "captions": "", "audio": ""}[kind]
            name = {"clip": f"part{n}{src.suffix}",
                    "captions": f"part{n}{src.suffix}",
                    "audio": f"part{n}_audio{src.suffix}"}[kind]
            dst = folder / name
            if src != dst:
                moves.append((src, dst))
    for s in manifest["scripts"]:
        src = ROOT / s
        dst = folder / f"script{src.suffix}"
        if src != dst:
            moves.append((src, dst))
    return moves


def report(qid: str, manifest: dict, warnings: list[str], errors: list[str]) -> None:
    print(f"\n\033[1m{qid}\033[0m")
    parts = manifest["parts"]
    if not parts:
        print("  no parts found")
    for n in sorted(parts):
        p = parts[n]
        clip = p.get("clip", {})
        bits = []
        if clip.get("duration"):
            bits.append(f"{clip['duration']:.2f}s")
        if clip.get("width"):
            bits.append(f"{clip['width']}x{clip['height']}")
        if clip.get("fps"):
            bits.append(f"{clip['fps']:g}fps")
        have = [k for k in ("captions", "audio") if k in p]
        print(f"  part {n}: {'  '.join(bits) or 'unreadable'}"
              f"{'   + ' + ', '.join(have) if have else ''}")
        print(f"           {Path(clip.get('path', '?')).name}")

    if manifest["scripts"]:
        for s in manifest["scripts"]:
            print(f"  script:  {Path(s).name}")
    if manifest["unassigned"]:
        print(f"  unassigned: {len(manifest['unassigned'])} file(s) with no part number")
        for u in manifest["unassigned"]:
            print(f"           {Path(u['path']).name}  ({u['kind']})")
    for item in manifest["ignored"]:
        print(f"  ignored: {Path(item['path']).name} — {item['why']}")
    for w in warnings:
        print(f"  \033[33mwarn\033[0m  {w}")
    for e in errors:
        print(f"  \033[31mFAIL\033[0m  {e}")


def ingest(qid: str, *, write: bool = True) -> int:
    folder = INBOX / qid
    if not folder.is_dir():
        matches = [d for d in INBOX.iterdir() if d.is_dir() and d.name.lower() == qid.lower()]
        if not matches:
            print(f"no such drop folder: inbox/{qid}", file=sys.stderr)
            return 1
        folder = matches[0]

    manifest, warnings, errors = collect(folder)
    w2, e2 = crosscheck(manifest["parts"])
    warnings += w2
    errors += e2

    report(folder.name, manifest, warnings, errors)

    if write and not errors:
        slug = folder.name.lower()
        out = WORK / slug / "inputs.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "qid": folder.name.upper(),
            "slug": slug,
            "drop": str(folder.relative_to(ROOT)),
            "parts": [manifest["parts"][n] for n in sorted(manifest["parts"])],
            "scripts": manifest["scripts"],
            "docs": manifest["docs"],
            "images": manifest["images"],
            "warnings": warnings,
        }
        out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"  \033[32m->\033[0m {out.relative_to(ROOT)}")

    return 1 if errors else 0


def survey() -> int:
    print("inbox/ — every drop folder, and whether it reads cleanly\n")
    worst = 0
    for d in sorted(INBOX.iterdir()):
        if not d.is_dir() or d.name.startswith("_"):
            continue
        manifest, warnings, errors = collect(d)
        w2, e2 = crosscheck(manifest["parts"])
        n = len(manifest["parts"])
        status = "\033[31mFAIL\033[0m" if (errors or e2) else (
            "\033[33mwarn\033[0m" if (warnings or w2) else "\033[32m ok \033[0m")
        print(f"  {status}  {d.name:<28} {n} part(s)"
              f"{'  ' + str(len(errors + e2)) + ' error(s)' if errors + e2 else ''}")
        worst = max(worst, 1 if (errors or e2) else 0)
    return worst


def main() -> int:
    ap = argparse.ArgumentParser(description="Read and gate a HeyGen drop folder.")
    ap.add_argument("qid", nargs="?", help="the drop folder name, e.g. BIO-C5-LA-01")
    ap.add_argument("--survey", action="store_true", help="list every drop folder")
    ap.add_argument("--tidy", action="store_true", help="show the renames that would standardise names")
    ap.add_argument("--apply", action="store_true", help="with --tidy, actually rename")
    args = ap.parse_args()

    if args.survey or not args.qid:
        return survey()

    if args.tidy:
        folder = INBOX / args.qid
        if not folder.is_dir():
            print(f"no such drop folder: inbox/{args.qid}", file=sys.stderr)
            return 1
        manifest, _, _ = collect(folder)
        moves = tidy_plan(folder, manifest)
        if not moves:
            print("already standard — nothing to rename")
            return 0
        for src, dst in moves:
            print(f"  {src.relative_to(ROOT)}\n    -> {dst.relative_to(ROOT)}")
        if not args.apply:
            print(f"\n{len(moves)} rename(s). Nothing moved — re-run with --apply.")
            return 0
        for src, dst in moves:
            if dst.exists():
                print(f"refusing to overwrite {dst.relative_to(ROOT)}", file=sys.stderr)
                return 1
        for src, dst in moves:
            src.rename(dst)
        print(f"\nrenamed {len(moves)} file(s)")
        return ingest(args.qid)

    return ingest(args.qid)


if __name__ == "__main__":
    raise SystemExit(main())
