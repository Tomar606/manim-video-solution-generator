"""Render every part of a kit reel and deliver it. Works on macOS, Windows and Linux.

    python lab/kit_test/render_reel.py <slug> [--wait] [--lanes N]

Uses the machine it is on:
  * LANES: the frames are split into N stretches rendered side by side, each with its own headless browser
    drawing the graphics and its own compositor, then joined. N comes from the cores and the free memory
    (about 1.2 GB per lane, at most one lane per 4 cores, at most 4), so an 8 GB laptop gets 1 and a 16-32 GB
    desktop gets 3-4. --lanes or KIT_LANES overrides.
  * GPU: every encode goes through tools/encoders.py, which picks NVENC, Quick Sync, AMF or VideoToolbox when
    the machine has one, and x264 on the CPU when it does not.
  * DISK: each lane's browser runs a little ahead of its compositor, and every frame the compositor has
    passed is deleted, so frames never pile up.
It keeps the machine awake while it runs (a laptop that idle-sleeps kills a render), and ends with
tools/deliver.py: gates, the answer page, the Final folder.

--wait: if the machine has no room yet, re-check every 30 s for up to 30 minutes instead of refusing,
so it can be started and then other apps closed.
"""
from __future__ import annotations

import json
import math
import os
import re
import subprocess
import sys
import threading
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PY = sys.executable
AHEAD, CHUNK = 900, 300          # frames a lane's browser may run ahead of its compositor, per browser launch
sys.path.insert(0, str(ROOT / "tools"))
from encoders import encoder, video_args  # noqa: E402


def keep_awake() -> subprocess.Popen | None:
    """macOS: caffeinate for as long as this process lives. Windows: ask the OS not to sleep."""
    if sys.platform == "darwin":
        return subprocess.Popen(["caffeinate", "-i", "-w", str(os.getpid())])
    if sys.platform == "win32":
        import ctypes
        ctypes.windll.kernel32.SetThreadExecutionState(0x80000000 | 0x00000001)   # ES_CONTINUOUS | ES_SYSTEM_REQUIRED
    return None


def free_gb() -> float:
    try:
        import psutil
        return psutil.virtual_memory().available / 1024**3
    except ImportError:
        return 1.5


def lanes_for_machine() -> int:
    forced = os.environ.get("KIT_LANES") or (sys.argv[sys.argv.index("--lanes") + 1] if "--lanes" in sys.argv else "")
    if forced:
        return max(1, int(forced))
    return max(1, min(4, (os.cpu_count() or 4) // 4, int((free_gb() - 0.5) // 1.2)))


def guard(wait: bool) -> bool:
    # one lane peaks near 1 GB (one Chromium + one compositor), so it asks for less than the guard's default
    cmd = [PY, str(ROOT / "tools/machine_guard.py"), "--need-disk", "4", "--need-ram", "1.5"]
    for i in range(60):
        if subprocess.run(cmd, capture_output=True).returncode == 0:
            return True
        if not wait:
            subprocess.run(cmd)
            return False
        if i == 0:
            print(time.strftime("%H:%M:%S"), "waiting for memory: close other apps (browsers, music, chat)", flush=True)
        time.sleep(30)
    print("still no room after 30 minutes")
    return False


def progress(log: Path, start: int) -> int:
    try:
        hits = re.findall(r"^  (\d+)/\d+", log.read_text(errors="replace"), re.M)
    except OSError:
        return start
    return int(hits[-1]) if hits else start


def lane(stem: str, plan: Path, out: Path, a: int, b: int, seg_out: Path, k: int, whole: bool) -> int:
    """One stretch [a, b): a browser drawing its frames ahead of a compositor, and a reaper behind it."""
    frames, log = out / "frames", out / f"render_compose_{k}.log"
    log.unlink(missing_ok=True)
    done = threading.Event()

    def draw():
        for c0 in range(a, b, CHUNK):
            while c0 - progress(log, a) >= AHEAD and not done.is_set():
                time.sleep(2)
            env = {**os.environ, "RANGES": f"{c0}:{min(c0 + CHUNK, b)}"}
            # a chunk can die mid-way (a screenshot timed out while a laptop struggled on low battery, 27 Oct
            # 2026); its missing frames would leave the compositor waiting forever, so retry it
            for attempt in range(4):
                with open(out / f"render_frames_{k}.log", "a") as f:
                    if subprocess.run(["node", str(HERE / "frames.mjs"), f"out/{stem}"], env=env, stdout=f, stderr=f, cwd=ROOT).returncode == 0:
                        break
                time.sleep(5)

    def reap():                                   # only this lane's frames: other lanes are still reading theirs
        while not done.is_set():
            c = progress(log, a)
            for g in frames.glob("g_*.png"):
                i = int(g.stem[2:])
                if a <= i < c - 5:
                    g.unlink(missing_ok=True)
            time.sleep(10)

    t_draw, t_reap = threading.Thread(target=draw, daemon=True), threading.Thread(target=reap, daemon=True)
    t_draw.start(); t_reap.start()
    cmd = [PY, "-u", str(HERE / "compose.py"), str(plan), "--music", "none", "--out", str(seg_out)]
    if not whole:
        cmd += ["--range", f"{a}:{b}"] + (["--seek"] if a else [])
    with open(log, "w") as f:
        rc = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT, cwd=ROOT).returncode
    done.set(); t_draw.join(); t_reap.join()
    return rc


def render_part(slug: str, part: int, n_lanes: int) -> Path:
    stem = f"plan_{slug.replace('-', '_')}_p{part}"
    plan, out = HERE / f"{stem}.json", HERE / "out" / stem
    final = ROOT / "projects" / slug / "final" / f"{slug.replace('-', '_')}_part{part}.mp4"
    final.parent.mkdir(parents=True, exist_ok=True)
    if subprocess.run([PY, str(HERE / "compile.py"), str(plan)], stdout=subprocess.DEVNULL).returncode != 0:
        raise SystemExit(f"compile refused part {part} (see above)")
    tl = (out / "timeline.js").read_text()
    n = math.ceil(json.loads(tl[tl.index("=") + 1:].strip().rstrip(";"))["duration"] * 30)
    if "--test" in sys.argv:                      # check the lanes on the first N frames; writes out/<plan>/lanes_test.mp4
        n, final = int(sys.argv[sys.argv.index("--test") + 1]), out / "lanes_test.mp4"
    (out / "frames").mkdir(parents=True, exist_ok=True)
    cuts = [round(n * k / n_lanes) for k in range(n_lanes + 1)]
    print(time.strftime("%H:%M:%S"), f"part {part}: {n} frames in {n_lanes} lane(s), encoder {encoder()}", flush=True)
    if n_lanes == 1:
        if lane(stem, plan, out, 0, n, final, 0, whole=True) != 0:
            raise SystemExit(f"compose failed on part {part}: see {out / 'render_compose_0.log'}")
    else:
        segs = [out / f"seg_{k}.mp4" for k in range(n_lanes)]
        rcs = [0] * n_lanes
        threads = [threading.Thread(target=lambda k=k: rcs.__setitem__(k, lane(stem, plan, out, cuts[k], cuts[k + 1], segs[k], k, False)))
                   for k in range(n_lanes)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        if any(rcs):
            raise SystemExit(f"a lane failed on part {part}: see {out}/render_compose_*.log")
        mix = out / "mix.m4a"
        subprocess.run([PY, "-c", f"import sys; sys.path.insert(0, {str(HERE)!r}); import compose as M; out = M.HERE / 'out' / {stem!r}; "
                        f"M.mix_audio(M.load_tl(out), M.ROOT / 'projects' / {slug!r}, 'none', out / 'mix.m4a')"],
                       check=True, cwd=ROOT, stdout=subprocess.DEVNULL)
        ins, chain = [], ""
        for k, sg in enumerate(segs):
            ins += ["-i", str(sg)]
            chain += f"[{k}:v]trim=end_frame={cuts[k + 1] - cuts[k]},setpts=PTS-STARTPTS[v{k}];"
        chain += "".join(f"[v{k}]" for k in range(n_lanes)) + f"concat=n={n_lanes}:v=1:a=0[v]"
        subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-i", str(mix), "-filter_complex", chain, "-map", "[v]",
                        "-map", f"{n_lanes}:a", *video_args(), "-c:a", "copy", "-shortest", "-movflags", "+faststart", str(final)],
                       check=True)
        for sg in segs:
            sg.unlink(missing_ok=True)
    for g in (out / "frames").glob("*.png"):
        g.unlink(missing_ok=True)
    subprocess.run([PY, str(HERE / "geom_sidecar.py"), str(plan), str(final)], stdout=subprocess.DEVNULL)
    print(time.strftime("%H:%M:%S"), f"part {part} rendered: {final.name}", flush=True)
    return final


def main() -> int:
    args = [a for i, a in enumerate(sys.argv[1:], 1) if not a.startswith("--") and sys.argv[i - 1] not in ("--lanes", "--test")]
    if not args:
        sys.exit(__doc__)
    slug = args[0]
    awake = keep_awake()
    try:
        if not guard("--wait" in sys.argv):
            return 1
        n_lanes = lanes_for_machine()
        subprocess.run([PY, str(ROOT / "tools/kit_veo.py"), "clean", slug], stdout=subprocess.DEVNULL)
        parts = int(json.loads((ROOT / "projects" / slug / "meta.json").read_text()).get("parts", 1))
        for p in range(1, parts + 1):
            render_part(slug, p, n_lanes)
            if "--test" in sys.argv:
                return 0
        return subprocess.run([PY, str(ROOT / "tools/deliver.py"), slug]).returncode
    finally:
        if awake:
            awake.terminate()


if __name__ == "__main__":
    sys.exit(main())
