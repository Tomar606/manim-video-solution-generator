"""A render queue over a shared folder: plan on the Mac, render on the PC.

    # on the Mac, once (and after any code change)
    python tools/render_queue.py push-code  <share>

    # on the Mac, per reel
    python tools/render_queue.py push       <share> <slug> [<slug> ...]
    python tools/render_queue.py status     <share>
    python tools/render_queue.py pull       <share> [<slug> ...]

    # on the PC, left running
    python tools/render_queue.py work       <share> [--once]

<share> is either a folder both machines can see - the PC shares one over the
LAN and the Mac mounts it, /Volumes/kitjobs here and C:\\kitjobs there - or an
rclone remote such as myremote:kitjobs when they cannot see each other at all.
Same commands either way; only the transport differs.

WHY A FOLDER AND NOT SSH. A Windows PC has no rsync and no ssh server until
somebody installs them, and a queue that depends on both machines being awake
at the same moment is a queue that fails at midnight. A folder needs nothing
but file sharing, and either end can be asleep.

WHY THE CODE IS PUSHED SEPARATELY. The PC having "the pipeline" is not the
same as having THIS pipeline - compose.py, stage.html, gates.py and the theme
skins all moved without being committed, and a render against the old ones
either fails or quietly comes out in the wrong look. push-code puts the current
tree in the share; the worker syncs from it before every batch, so the PC can
never drift. It is pushed once rather than per job because it is ~550 MB and
the reel data is only ~450 MB.

THE HANDSHAKE. The Mac writes a job's payload first and its job.json last,
because job.json is the only thing the worker looks for: a half-copied job has
no marker and is invisible. The worker moves a job to running before touching
it, so two workers cannot take the same one.

    <share>/pipeline/        the code tree, refreshed by push-code
    <share>/jobs/<slug>/     reel data + job.json (queued -> running -> done/failed)
    <share>/done/<slug>/     the finished parts, delivery.json and the log
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
from stage_render_bundle import CODE, FILES, parts_for, rsync, shared_deps  # noqa: E402

NOW = lambda: datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")  # noqa: E731


# ─────────────────────────────── shared helpers ───────────────────────────
def copy_tree(src: Path, dst: Path, skip: tuple[str, ...] = ()) -> None:
    """shutil, not rsync: the worker runs on Windows, which has no rsync."""
    def ignore(_d, names):
        return [n for n in names
                if n in skip or n.endswith(".pyc") or n == "__pycache__"]
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst, ignore=ignore, dirs_exist_ok=False)


# ───────────────────────── the queue over Google Drive ───────────────────
# When the two machines cannot see each other - different subnets, no route -
# the same folder queue runs through an rclone remote instead. Nothing about
# the job format changes; only how the folder gets from one end to the other.
RCLONE = os.environ.get("RCLONE", "rclone")
# 16 parallel transfers, not 4: Drive charges a round trip per file, so a tree
# of small files is latency-bound rather than bandwidth-bound.
RC_FLAGS = ["--transfers", "16", "--checkers", "16", "--retries", "3",
            "--low-level-retries", "10", "--drive-chunk-size", "32M"]

# What the code push sends over Drive, as opposed to over a USB stick or a LAN
# share. The whole library/ is 555 MB in 7,400 files, and at Drive's per-file
# cost that measured out at roughly two hours - for a tree the render PC
# already has from its own setup. So the remote push carries only what
# actually changes (the pipeline code) and what the stage page loads at render
# time (the kit CSS, the typefaces, the face-gate reference). Anything a
# PARTICULAR reel needs - its theme, its plate, its sound effects - travels
# with the job itself through shared_deps().
CODE_REMOTE = [
    ("tools", ["edu/renderer/node_modules/", "edu/renderer/.browsers/",
               "edu/renderer/out/", "__pycache__/", "*.pyc"]),
    ("lab/kit_test", ["out/", "__pycache__/", "*.pyc", "lab/"]),
    ("veo_kit", ["__pycache__/", "*.pyc"]),
    ("library/elements/kit", []),
    ("library/elements/vendor/lottie", []),
    ("library/sfx", []),
    ("assets/fonts", []),
    ("assets/character", []),
]


def is_remote(s: str) -> bool:
    """An rclone path such as myremote:kitjobs, as opposed to a local folder.

    A Windows drive is the trap here: C:\\kitjobs also contains a colon, and on
    the PC the folder may not exist yet, so "has a colon and is not on disk"
    wrongly called it a remote. A drive letter is one character before the
    colon and a remote name is never one character, which separates them
    without having to know which OS we are on."""
    if "\\" in s or s.startswith("/") or ":" not in s:
        return False
    name = s.split(":", 1)[0]
    return len(name) > 1 and "/" not in name and not Path(s).exists()


def cache_for(remote: str) -> Path:
    d = Path.home() / ".cache/kitqueue" / remote.replace(":", "_").replace("/", "_")
    d.mkdir(parents=True, exist_ok=True)
    return d


def rc(*args: str, quiet: bool = False) -> int:
    cmd = [RCLONE, *args, *RC_FLAGS]
    if not quiet:
        cmd.append("--progress")
    r = subprocess.run(cmd, capture_output=quiet, text=True)
    if r.returncode and quiet and r.stderr:
        print(r.stderr.strip()[:400])
    return r.returncode


def rc_markers(remote: str, cache: Path) -> None:
    """Pull down only the job.json files - a few hundred bytes, not the GBs."""
    # heartbeats come too: they are what says whether a "running" job belongs
    # to a worker that is still alive or one that died mid-render.
    rc("copy", f"{remote}/jobs", str(cache / "jobs"),
       "--include", "*/job.json", "--include", "*/heartbeat.json", quiet=True)


CLAIM_WAIT = 8        # seconds to let other workers' claims become visible
STALE_AFTER = 1800    # a "running" job whose worker stopped reporting is free


def rc_claim(remote: str, slug: str, cache: Path, me: str) -> bool:
    """Decide which of several workers gets this job.

    Drive has no locking, and read-state-then-write-state is not atomic: with
    one worker it never mattered, with three it is two machines rendering the
    same reel and the second overwriting the first's delivery. So every worker
    writes a claim file, waits for the others' to appear, and the earliest
    (timestamp, name) wins. The losers delete their claim and look elsewhere.
    The wait costs eight seconds against a render of several minutes."""
    d = cache / "jobs" / slug
    d.mkdir(parents=True, exist_ok=True)
    mine = d / f"claim_{me}.json"
    mine.write_text(json.dumps({"worker": me, "t": time.time()}), encoding="utf-8")
    rc("copyto", str(mine), f"{remote}/jobs/{slug}/claim_{me}.json", quiet=True)
    time.sleep(CLAIM_WAIT)
    rc("copy", f"{remote}/jobs/{slug}", str(d), "--include", "claim_*.json", quiet=True)
    claims = []
    for c in d.glob("claim_*.json"):
        try:
            j = json.loads(c.read_text(encoding="utf-8"))
            claims.append((float(j["t"]), str(j["worker"])))
        except (OSError, ValueError, KeyError):
            continue
    if not claims:
        return False
    if min(claims)[1] != me:
        mine.unlink(missing_ok=True)
        rc("deletefile", f"{remote}/jobs/{slug}/claim_{me}.json", quiet=True)
        print(f"  {slug}: {min(claims)[1]} got it first")
        return False
    return True


def beat(remote: str, slug: str, cache: Path, me: str, stop) -> None:
    """Say we are still alive, so a crashed worker's job can be retaken."""
    f = cache / "jobs" / slug / "heartbeat.json"
    while not stop.is_set():
        try:
            f.write_text(json.dumps({"worker": me, "t": time.time()}), encoding="utf-8")
            rc("copyto", str(f), f"{remote}/jobs/{slug}/heartbeat.json", quiet=True)
        except Exception:                                   # noqa: BLE001
            pass
        stop.wait(120)


def takeable(d: Path) -> bool:
    """queued, or running under a worker that has gone quiet."""
    j = read_job(d)
    if not j:
        return False
    if j["state"] == "queued":
        return True
    if j["state"] != "running":
        return False
    hb = d / "heartbeat.json"
    try:
        age = time.time() - json.loads(hb.read_text(encoding="utf-8"))["t"]
    except (OSError, ValueError, KeyError):
        return False
    return age > STALE_AFTER


def rc_put_job(remote: str, d: Path, slug: str) -> None:
    """Payload first, marker second - the same invariant as the folder queue.

    rclone uploads in arbitrary order, so sending the directory in one go
    would let the worker see job.json while the 500 MB payload was still
    arriving. Hence two calls, and job.json is always the second."""
    rc("copy", str(d), f"{remote}/jobs/{slug}", "--exclude", "job.json")
    rc("copyto", str(d / "job.json"), f"{remote}/jobs/{slug}/job.json", quiet=True)


def read_job(d: Path) -> dict | None:
    f = d / "job.json"
    if not f.exists():
        return None
    try:
        return json.loads(f.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None          # still being written; it will be there next pass


def write_job(d: Path, job: dict) -> None:
    tmp = d / "job.json.tmp"
    tmp.write_text(json.dumps(job, indent=1), encoding="utf-8")
    tmp.replace(d / "job.json")


# ───────────────────────────────── Mac side ───────────────────────────────
def push_code(share: Path, which: list | None = None) -> None:
    dest = share / "pipeline"
    dest.mkdir(parents=True, exist_ok=True)
    print(f"pushing code -> {dest}")
    for rel, ex in (which or CODE):
        print(f"  {rel}")
        rsync(ROOT / rel, dest / rel, ex, False)
    for name in FILES:
        if (ROOT / name).exists():
            shutil.copy2(ROOT / name, dest / name)
    (dest / "STAMP.json").write_text(json.dumps({
        "pushed_at": NOW(),
        "commit": subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                                 cwd=ROOT, capture_output=True,
                                 text=True).stdout.strip(),
        "dirty": bool(subprocess.run(["git", "status", "--porcelain"], cwd=ROOT,
                                     capture_output=True, text=True).stdout.strip()),
    }, indent=1), encoding="utf-8")
    print("  done. The worker syncs from here before every batch.")


def push(share: Path, slugs: list[str]) -> None:
    for slug in slugs:
        proj, ps = ROOT / "projects" / slug, parts_for(slug)
        if not proj.is_dir():
            raise SystemExit(f"no projects/{slug}")
        if not ps:
            raise SystemExit(f"{slug} has no compiled parts in lab/kit_test/out "
                             f"- compile it before pushing")
        d = share / "jobs" / slug
        if (j := read_job(d)) and j.get("state") == "running":
            print(f"  {slug}: already running on {j.get('worker')}, skipped")
            continue
        if d.exists():
            shutil.rmtree(d)
        (d / "payload").mkdir(parents=True)
        print(f"{slug}: {len(ps)} part(s)")
        rsync(proj, d / "payload/projects" / slug, ["__pycache__/", "*.pyc"], False)
        for p in ps:
            rsync(p, d / "payload/out" / p.name, ["frames/"], False)
            src = ROOT / "lab/kit_test" / f"{p.name}.json"
            if src.exists():
                shutil.copy2(src, d / "payload/out" / f"{p.name}.json")
        for rel in shared_deps(ps):          # themes and plates it names
            s = ROOT / rel
            t = d / "payload/shared" / rel
            t.parent.mkdir(parents=True, exist_ok=True)
            if s.is_dir():
                rsync(s, t, [], False)
            else:
                shutil.copy2(s, t)
        # job.json LAST: it is the marker the worker waits for
        write_job(d, {"slug": slug, "parts": [p.name for p in ps],
                      "state": "queued", "pushed_at": NOW(),
                      "pushed_by": os.uname().nodename})
        print(f"  queued at {d}")


def status(share: Path) -> None:
    stamp = share / "pipeline" / "STAMP.json"
    if stamp.exists():
        s = json.loads(stamp.read_text())
        print(f"code in share: {s['commit']}"
              f"{' + uncommitted' if s.get('dirty') else ''}  ({s['pushed_at']})\n")
    jobs = sorted((share / "jobs").glob("*")) if (share / "jobs").is_dir() else []
    if not jobs:
        print("no jobs")
    for d in jobs:
        j = read_job(d)
        if not j:
            continue
        extra = j.get("error") or j.get("finished_at") or j.get("started_at") or ""
        print(f"  {j['slug']:<16} {j['state']:<8} {len(j['parts'])} part(s)  {extra}")
    done = sorted((share / "done").glob("*")) if (share / "done").is_dir() else []
    if done:
        print("\nready to pull: " + ", ".join(p.name for p in done))


def pull(share: Path, slugs: list[str]) -> None:
    src_root = share / "done"
    names = slugs or [p.name for p in sorted(src_root.glob("*"))] if src_root.is_dir() else []
    for slug in names:
        s = src_root / slug
        if not s.is_dir():
            print(f"  {slug}: nothing in done/")
            continue
        dst = ROOT / "projects" / slug / "final"
        dst.mkdir(parents=True, exist_ok=True)
        n = 0
        for f in s.rglob("*"):
            if f.is_file() and f.name != "log.txt":
                shutil.copy2(f, dst / f.name)
                n += 1
        print(f"  {slug}: {n} file(s) -> {dst}")
        if (s / "log.txt").exists():
            print(f"     log: {s / 'log.txt'}")


# ───────────────────────────────── PC side ────────────────────────────────
def sync_code_in(share: Path) -> None:
    """Bring the share's pipeline into this checkout, keeping what is local.

    node_modules, the browser and the venv are deliberately never in the share
    and never touched here: they are built for this machine."""
    src = share / "pipeline"
    if not src.is_dir():
        print("  no pipeline/ in the share yet - push-code from the Mac first")
        return
    # Walk whatever was actually pushed rather than a fixed list: the LAN and
    # the Drive transports send different subsets, and installing "whatever
    # arrived" is right for both.
    n = 0
    for f in src.rglob("*"):
        if not f.is_file() or f.name == "STAMP.json":
            continue
        t = ROOT / f.relative_to(src)
        if t.exists() and t.stat().st_size == f.stat().st_size \
                and t.stat().st_mtime >= f.stat().st_mtime:
            continue
        t.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, t)
        n += 1
    print(f"  {n} file(s) updated")
    if (st := src / "STAMP.json").exists():
        s = json.loads(st.read_text())
        print(f"  code synced: {s['commit']}"
              f"{' + uncommitted' if s.get('dirty') else ''}")


def install_payload(d: Path, slug: str) -> None:
    p = d / "payload"
    copy_tree(p / "projects" / slug, ROOT / "projects" / slug)
    for part in (p / "out").glob("plan_*"):
        if part.is_dir():
            copy_tree(part, ROOT / "lab/kit_test/out" / part.name)
    for j in (p / "out").glob("plan_*.json"):
        shutil.copy2(j, ROOT / "lab/kit_test" / j.name)
    sh = p / "shared"
    if sh.is_dir():
        for f in sh.rglob("*"):
            if f.is_file():
                t = ROOT / f.relative_to(sh)
                t.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(f, t)


def work(share: Path, once: bool = False) -> None:
    # A worker REPLACES projects/<slug> with whatever was pushed, which is
    # correct on a machine whose only job is rendering and ruinous on the one
    # the work was planned on. So a machine has to opt in by name.
    if not (ROOT / ".queue-worker").exists():
        raise SystemExit(
            f"{ROOT} is not marked as a render worker.\n"
            f"A worker overwrites projects/<slug> from the queue, so this is "
            f"opt-in.\nOn the render PC only:  echo worker > "
            f"{ROOT / '.queue-worker'}")
    me = os.environ.get("COMPUTERNAME") or os.environ.get("HOSTNAME") or "worker"
    print(f"worker on {me}, watching {share}")
    synced = False
    while True:
        jobs = sorted((share / "jobs").glob("*")) if (share / "jobs").is_dir() else []
        queued = [d for d in jobs if (j := read_job(d)) and j["state"] == "queued"]
        if not queued:
            if once:
                print("nothing queued")
                return
            synced = False
            time.sleep(20)
            continue
        if not synced:                     # once per batch, not per job
            print("syncing code from the share")
            sync_code_in(share)
            synced = True

        d = queued[0]
        job = read_job(d)
        slug = job["slug"]
        job.update(state="running", worker=me, started_at=NOW())
        write_job(d, job)
        print(f"\n=== {slug}: {len(job['parts'])} part(s) ===")
        try:
            install_payload(d, slug)
            log = d / "log.txt"
            with open(log, "w", encoding="utf-8") as f:
                rc = subprocess.run(
                    [sys.executable, str(ROOT / "lab/kit_test/render_reel.py"),
                     slug, "--wait"],
                    cwd=ROOT, stdout=f, stderr=subprocess.STDOUT).returncode
            if rc:
                raise RuntimeError(f"render_reel exited {rc}; see log.txt")
            out = share / "done" / slug
            out.mkdir(parents=True, exist_ok=True)
            fin = ROOT / "projects" / slug / "final"
            for f in sorted(fin.glob("*")):
                if f.is_file():
                    shutil.copy2(f, out / f.name)
            shutil.copy2(log, out / "log.txt")
            job.update(state="done", finished_at=NOW())
            print(f"  done -> {out}")
        except Exception as e:                            # noqa: BLE001
            job.update(state="failed", error=str(e), finished_at=NOW())
            out = share / "done" / slug
            out.mkdir(parents=True, exist_ok=True)
            if (d / "log.txt").exists():
                shutil.copy2(d / "log.txt", out / "log.txt")
            print(f"  FAILED: {e}")
        write_job(d, job)
        if once:
            return


# ───────────────────── the same four commands, over rclone ────────────────
def lsf(path: str) -> list[str]:
    r = subprocess.run([RCLONE, "lsf", "--dirs-only", path],
                       capture_output=True, text=True)
    return [x.strip("/") for x in r.stdout.split() if x.strip()]


def push_code_remote(remote: str) -> None:
    cache = cache_for(remote)
    push_code(cache, CODE_REMOTE)
    print(f"uploading code to {remote}/pipeline ...")
    rc("copy", str(cache / "pipeline"), f"{remote}/pipeline")
    shutil.rmtree(cache / "pipeline", ignore_errors=True)   # 555 MB; disk is tight


def sync_code_remote(remote: str) -> None:
    cache = cache_for(remote)
    rc("copy", f"{remote}/pipeline", str(cache / "pipeline"), quiet=True)
    sync_code_in(cache)


def push_remote(remote: str, slugs: list[str]) -> None:
    cache = cache_for(remote)
    rc_markers(remote, cache)                 # so "already running" is current
    push(cache, slugs)
    for slug in slugs:
        d = cache / "jobs" / slug
        if (d / "job.json").exists():
            print(f"uploading {slug} ...")
            rc_put_job(remote, d, slug)
            # the upload is the copy that matters now, and this laptop has
            # about three gigabytes spare
            shutil.rmtree(d / "payload", ignore_errors=True)
            print(f"  {slug} is on {remote}")


def status_remote(remote: str) -> None:
    cache = cache_for(remote)
    rc_markers(remote, cache)
    jobs = sorted((cache / "jobs").glob("*")) if (cache / "jobs").is_dir() else []
    if not jobs:
        print("no jobs")
    for d in jobs:
        if j := read_job(d):
            extra = j.get("error") or j.get("finished_at") or j.get("started_at") or ""
            print(f"  {j['slug']:<16} {j['state']:<8} {len(j['parts'])} part(s)  {extra}")
    if done := lsf(f"{remote}/done"):
        print("\nready to pull: " + ", ".join(done))


def pull_remote(remote: str, slugs: list[str]) -> None:
    for slug in slugs or lsf(f"{remote}/done"):
        dst = ROOT / "projects" / slug / "final"
        dst.mkdir(parents=True, exist_ok=True)
        print(f"{slug} -> {dst}")
        rc("copy", f"{remote}/done/{slug}", str(dst), "--exclude", "log.txt")


def work_remote(remote: str, once: bool = False) -> None:
    if not (ROOT / ".queue-worker").exists():
        raise SystemExit(f"{ROOT} is not marked as a render worker.\n"
                         f"On the render PC only:  echo worker > "
                         f"{ROOT / '.queue-worker'}")
    me = os.environ.get("COMPUTERNAME") or os.environ.get("HOSTNAME") or "worker"
    cache = cache_for(remote)
    print(f"worker on {me}, watching {remote}")
    synced = False
    while True:
        rc_markers(remote, cache)
        queued = [d for d in sorted((cache / "jobs").glob("*")) if takeable(d)]
        if not queued:
            if once:
                print("nothing queued")
                return
            synced = False
            time.sleep(60)               # Drive, not a LAN: poll gently
            continue
        if not synced:                   # once per batch, before the first job
            print("syncing code from the queue")
            sync_code_remote(remote)
            synced = True
        d = queued[0]
        job = read_job(d)
        slug = job["slug"]
        if not rc_claim(remote, slug, cache, me):
            continue                      # another worker won it; look again
        # claim it BEFORE downloading half a gigabyte of payload
        job.update(state="running", worker=me, started_at=NOW())
        write_job(d, job)
        rc("copyto", str(d / "job.json"), f"{remote}/jobs/{slug}/job.json", quiet=True)
        print(f"\n=== {slug}: {len(job['parts'])} part(s) ===\n  downloading payload")
        stop = threading.Event()
        threading.Thread(target=beat, args=(remote, slug, cache, me, stop),
                         daemon=True).start()
        try:
            rc("copy", f"{remote}/jobs/{slug}", str(d), "--exclude", "job.json")
            install_payload(d, slug)
            log = d / "log.txt"
            with open(log, "w", encoding="utf-8") as f:
                code = subprocess.run(
                    [sys.executable, str(ROOT / "lab/kit_test/render_reel.py"),
                     slug, "--wait"],
                    cwd=ROOT, stdout=f, stderr=subprocess.STDOUT).returncode
            if code:
                raise RuntimeError(f"render_reel exited {code}; see log.txt")
            out = cache / "done" / slug
            out.mkdir(parents=True, exist_ok=True)
            for f in sorted((ROOT / "projects" / slug / "final").glob("*")):
                if f.is_file():
                    shutil.copy2(f, out / f.name)
            shutil.copy2(log, out / "log.txt")
            print("  uploading result")
            rc("copy", str(out), f"{remote}/done/{slug}")
            job.update(state="done", finished_at=NOW())
            print(f"  done -> {remote}/done/{slug}")
        except Exception as e:                            # noqa: BLE001
            job.update(state="failed", error=str(e), finished_at=NOW())
            if (d / "log.txt").exists():
                rc("copyto", str(d / "log.txt"), f"{remote}/done/{slug}/log.txt",
                   quiet=True)
            print(f"  FAILED: {e}")
        finally:
            stop.set()                      # the heartbeat must not outlive the job
        write_job(d, job)
        rc("copyto", str(d / "job.json"), f"{remote}/jobs/{slug}/job.json", quiet=True)
        rc("deletefile", f"{remote}/jobs/{slug}/claim_{me}.json", quiet=True)
        shutil.rmtree(d / "payload", ignore_errors=True)   # the disk is not free
        if once:
            return


# ──────────────────────────────────── cli ─────────────────────────────────
def main() -> None:
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    if len(a) < 2:
        raise SystemExit(__doc__)
    cmd, where, rest = a[0], a[1], a[2:]
    once = "--once" in sys.argv
    if is_remote(where):                 # e.g. myremote:kitjobs
        table = {"push-code": lambda: push_code_remote(where),
                 "push": lambda: push_remote(where, rest),
                 "status": lambda: status_remote(where),
                 "pull": lambda: pull_remote(where, rest),
                 "work": lambda: work_remote(where, once)}
    else:
        share = Path(where).expanduser()
        if cmd != "work" and not share.is_dir():
            raise SystemExit(f"{share} is not reachable - is the share mounted?")
        table = {"push-code": lambda: push_code(share),
                 "push": lambda: push(share, rest),
                 "status": lambda: status(share),
                 "pull": lambda: pull(share, rest),
                 "work": lambda: work(share, once)}
    table.get(cmd, lambda: (_ for _ in ()).throw(SystemExit(__doc__)))()


if __name__ == "__main__":
    main()
