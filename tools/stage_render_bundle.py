"""Copy everything a second machine needs to render and deliver given reels.

    python tools/stage_render_bundle.py <dest> <slug> [<slug> ...] [--dry-run]

Why a tool and not a zip of the repo: the repo is 21 GB, almost all of it other
videos' media, and two of its directories must NOT travel because they are
built for this machine's CPU - tools/edu/renderer/.browsers holds a macOS
Chromium, and node_modules holds platform binaries. Both get reinstalled on the
far side.

What travels, and why:
  code          tools/, lab/kit_test/ - the pipeline itself
  library/      compose.py reads plates, photos, music and sfx from here
  assets/       fonts and the transition pieces
  out/plan_*    the compiled timeline and its assets for each part
  projects/<slug>
                meta, the answer pages, and src/ - the take the gates measure
                the finished video against, and the audio the mix is rebuilt
                from when out/ has no mix.m4a

What does not travel: .env. Nothing in the render, gate or deliver path reads
it, the answer pages are already fetched into projects/, and the sheet IDs in
it are secrets.

The copy streams straight to <dest>, so it never needs a second copy of itself
on this disk - which matters, because the machine that wants this tool is
usually the one that has run out of room.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# (source, rsync excludes). Order is the order they are copied.
CODE = [
    ("tools", ["edu/renderer/node_modules/", "edu/renderer/.browsers/",
               "edu/renderer/out/", "__pycache__/", "*.pyc"]),
    ("lab/kit_test", ["out/", "__pycache__/", "*.pyc", "lab/"]),
    # gates.py runs face_gate out of veo_kit, not tools; its reference
    # photograph is assets/character/ritesh_reference.jpeg, so assets must
    # travel too even though compose.py never opens it.
    ("veo_kit", ["__pycache__/", "*.pyc"]),
    ("library", []),
    ("assets", []),
]
FILES = ["requirements-tools.txt", "CLAUDE.md", "PIPELINE.md"]

GUIDE = """# Render these reels on this PC

Nothing here needs the internet, an API key or a `.env`. The answer pages and
the presenter takes are already inside `projects/`.

## 1. Install the tools (once per PC)

```powershell
winget install Python.Python.3.12 OpenJS.NodeJS.LTS Gyan.FFmpeg Git.Git
py -3.12 -m venv .venv-tools
.venv-tools\\Scripts\\pip install -r requirements-tools.txt
cd tools\\edu\\renderer
npm install
$env:PLAYWRIGHT_BROWSERS_PATH=".browsers"
npx playwright install --only-shell chromium
cd ..\\..\\..
```

`node_modules` and the browser were deliberately left out of this bundle: the
copies on the Mac are built for macOS and will not run here.

## 2. Check the machine

```powershell
.venv-tools\\Scripts\\python tools\\doctor.py
```

If it reports Hindi text shaping missing, put FriBiDi's `fribidi-0.dll` on
PATH and run it again. Do not skip this: without shaping every Devanagari
label is drawn with its vowel signs in the wrong place, and nothing errors.

## 3. Render and deliver, one reel at a time

{commands}

Each command renders every part, runs the full gate suite, appends the answer
page and writes the finished video into the Final folder. If a gate fails it
stops and copies nothing; the reason is printed.

Expect roughly 6 to 10 minutes a part on a 16-core, 32 GB machine - it splits
the work into 4 lanes and uses the GPU encoder. Add `--lanes N` to override.

## 4. Bring back

Copy `projects\\<slug>\\final\\` for each reel, or the whole Final folder.
"""


def rsync(src: Path, dst: Path, excludes: list[str], dry: bool) -> None:
    # NOT --delete-excluded. The bundle is often rsynced straight into an
    # existing checkout on the far machine, and --delete-excluded removes the
    # excluded paths FROM THE DESTINATION - which would delete that machine's
    # node_modules and its own Chromium, the two things it has to keep.
    cmd = ["rsync", "-a"]
    for e in excludes:
        cmd += ["--exclude", e]
    if dry:
        cmd.append("--dry-run")
    cmd += [f"{src}/", str(dst)]
    dst.mkdir(parents=True, exist_ok=True)
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(f"rsync failed for {src}:\n{r.stderr}")


def du_mb(p: Path, excludes: list[str] | None = None) -> int:
    """What rsync will actually send, not what du reports.

    macOS du has no --exclude, so measuring the directory and then excluding
    half of it at copy time reported 413 MB for a tools/ tree that sends about
    two. The number is used to check the drive has room, so it has to be the
    transferred size.
    """
    if not p.exists():
        return 0
    cmd = ["rsync", "-a", "--dry-run", "--stats"]
    for e in excludes or []:
        cmd += ["--exclude", e]
    cmd += [f"{p}/", "/dev/null/"]
    out = subprocess.run(cmd, capture_output=True, text=True).stdout
    for line in out.splitlines():
        if line.startswith("Total transferred file size"):
            return int(int(line.split(":")[1].strip().split()[0].replace(",", "")) / 1024**2)
    return 0


def parts_for(slug: str) -> list[Path]:
    stem = "plan_" + slug.replace("-", "_") + "_p"
    return sorted((ROOT / "lab/kit_test/out").glob(stem + "[0-9]"))


def shared_deps(parts: list[Path]) -> list[str]:
    """Files outside the plan dir that these timelines name.

    Only a handful, because compile.py has already inlined the icons and
    render_reel.py mixes with music 'none', so library/music never opens. Worth
    carrying even into a PC that has the pipeline: a plate added since that PC
    was set up is a mid-render failure, and these are a few megabytes.
    """
    import json as _json
    want = {"plate", "plate_path", "backdrop", "skin", "theme"}
    vals: dict[str, set[str]] = {k: set() for k in want}

    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k in want and isinstance(v, str):
                    vals[k].add(v)
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)

    for p in parts:
        t = (p / "timeline.js").read_text(encoding="utf-8")
        walk(_json.loads(t[t.index("{"):t.rindex("}") + 1]))

    # library/sfx is NOT here. The mix picks its sounds by beat type, so the
    # whole folder must be present at render time - but it is 120 small files,
    # and over Drive that is 120 round trips PER JOB for a 4 MB folder that
    # never changes between reels. It travels with the code push instead,
    # which both transports do before any job runs.
    out: set[str] = set()
    for name in vals["plate"] | vals["backdrop"]:
        out.add(f"library/backgrounds/plates/generated/{name}.jpg")
    for rel in vals["plate_path"]:
        out.add(f"library/backgrounds/plates/{rel}")
    for name in vals["skin"] | vals["theme"]:
        out.add(f"lab/kit_test/themes/{name}.css")
    return sorted(x for x in out if (ROOT / x).exists())


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry = "--dry-run" in sys.argv
    if len(args) < 2:
        raise SystemExit(__doc__)
    dest, slugs = Path(args[0]).expanduser(), args[1:]

    plan = []
    for slug in slugs:
        proj = ROOT / "projects" / slug
        if not proj.is_dir():
            raise SystemExit(f"no projects/{slug}")
        ps = parts_for(slug)
        if not ps:
            raise SystemExit(f"no compiled parts in lab/kit_test/out for {slug} "
                             f"- it has not been compiled yet")
        plan.append((slug, proj, ps))

    reels_only = "--reels-only" in sys.argv
    deps = shared_deps([p for _, _, ps in plan for p in ps]) if reels_only else []

    print(f"bundle -> {dest}\n")
    total = 0
    if reels_only:
        print("  reels only: the PC already has the pipeline\n"
              "  shared files these timelines name, carried anyway:")
        for d in deps:
            mb = du_mb(ROOT / d) if (ROOT / d).is_dir() else \
                int((ROOT / d).stat().st_size / 1024**2)
            total += mb
            print(f"    {d}")
    else:
        print("  code and libraries")
        for rel, ex in CODE:
            mb = du_mb(ROOT / rel, ex)
            total += mb
            shown = f"{mb:>6}" if mb else "    <1"
            print(f"    {rel:<22} {shown} MB"
                  + (f"   (minus {len(ex)} excluded)" if ex else ""))
    print("\n  reels")
    for slug, proj, ps in plan:
        pmb = du_mb(proj, ["__pycache__/", "*.pyc"])
        omb = sum(du_mb(p, ["frames/"]) for p in ps)
        total += pmb + omb
        print(f"    {slug:<18} projects {pmb:>5} MB   out {omb:>4} MB "
              f"({len(ps)} part{'s' if len(ps) > 1 else ''})")
    print(f"\n  total {total} MB ({total / 1024:.2f} GB)")

    if dest.exists():
        free = shutil.disk_usage(dest).free / 1024**2
        print(f"  free at destination: {free / 1024:.1f} GB"
              + ("   NOT ENOUGH" if free < total * 1.05 else ""))
    elif not dry:
        raise SystemExit(f"\n{dest} does not exist - plug the drive in, or make the folder")

    if dry:
        print("\ndry run: nothing copied")
        return

    print("\ncopying ...")
    if reels_only:
        for d in deps:
            print(f"  {d}")
            s = ROOT / d
            if s.is_dir():
                rsync(s, dest / d, [], False)
            else:
                (dest / d).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(s, dest / d)
    else:
        for rel, ex in CODE:
            print(f"  {rel}")
            rsync(ROOT / rel, dest / rel, ex, False)
        for name in FILES:
            if (ROOT / name).exists():
                shutil.copy2(ROOT / name, dest / name)
    for slug, proj, ps in plan:
        print(f"  projects/{slug}")
        rsync(proj, dest / "projects" / slug, ["__pycache__/", "*.pyc"], False)
        for p in ps:
            print(f"  lab/kit_test/out/{p.name}")
            # frames/ is transient - a lane deletes each frame once the
            # compositor has passed it, so there is never a set worth copying
            rsync(p, dest / "lab/kit_test/out" / p.name, ["frames/"], False)
            j = ROOT / "lab/kit_test" / f"{p.name}.json"
            if j.exists():
                shutil.copy2(j, dest / "lab/kit_test" / j.name)

    cmds = "\n".join(
        f"```powershell\n.venv-tools\\Scripts\\python lab\\kit_test\\render_reel.py {s}\n```"
        for s, _, _ in plan)
    (dest / "RENDER_ON_THIS_PC.md").write_text(GUIDE.format(commands=cmds),
                                               encoding="utf-8")
    print(f"\ndone. Read {dest / 'RENDER_ON_THIS_PC.md'} on the PC.")


if __name__ == "__main__":
    main()
