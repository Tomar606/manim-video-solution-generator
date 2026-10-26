"""Refuse to start heavy work this machine cannot survive.

    python tools/machine_guard.py [--need-disk GB] [--need-ram GB] [--wait]

WHY THIS EXISTS
---------------
This box has 8 GB of RAM and renders 1080x1920 video on it. A manim render, an
ffmpeg composite and a whisper transcription each want gigabytes, and run
together they do not fail — they SWAP. Measured mid-session: 4.1 million
swapouts, a swap file grown to 10 GB, and the boot disk falling from 6.0 GB
free to 3.8 GB with nothing of ours running, because the swap file itself was
eating the disk.

That is the crash. Swap lives on the boot volume, so memory pressure turns into
disk pressure, and when the disk reaches zero the machine stops: first ENOSPC on
every write (one command could not even create its output file), then a freeze,
then a shutdown. It cost a full day across two sessions — an interrupted encode,
a killed render, and the user restarting the machine repeatedly.

The rule this encodes: ONE heavy job at a time, and never start one without
room for it. Checked rather than remembered, because by the time the machine is
thrashing it is too late to notice.

HEADROOM, not free space. The disk check wants room for the output AND for the
swap file to grow into; a build that just fits is the build that fills the disk
and takes the machine with it.
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys


def swap_used_gb() -> tuple[float, float]:
    if sys.platform != "darwin":                  # Windows / Linux: psutil (requirements-tools.txt)
        try:
            import psutil
            sw = psutil.swap_memory()
            return sw.used / 1024**3, sw.free / 1024**3
        except ImportError:
            return 0.0, 0.0
    out = subprocess.run(["sysctl", "vm.swapusage"], capture_output=True, text=True).stdout
    used = re.search(r"used\s*=\s*([\d.]+)M", out)
    free = re.search(r"free\s*=\s*([\d.]+)M", out)
    return (float(used.group(1)) / 1024 if used else 0.0,
            float(free.group(1)) / 1024 if free else 0.0)


def free_ram_gb() -> float:
    if sys.platform != "darwin":
        try:
            import psutil
            return psutil.virtual_memory().available / 1024**3
        except ImportError:
            print("  note: install psutil to measure memory on this OS; not checking it")
            return 99.0
    out = subprocess.run(["vm_stat"], capture_output=True, text=True).stdout
    page = int(re.search(r"page size of (\d+)", out).group(1))
    def pages(name):
        m = re.search(rf"Pages {name}:\s+(\d+)", out)
        return int(m.group(1)) if m else 0
    # free + inactive + speculative is what a new process can actually take
    return (pages("free") + pages("inactive") + pages("speculative")) * page / 1024**3


def busy() -> list[str]:
    """Heavy jobs of ours already running — the thing that must never double up."""
    if sys.platform == "win32":
        try:
            import psutil
            out = "\n".join(" ".join(p.info["cmdline"] or []).replace("\\", "/") for p in psutil.process_iter(["cmdline"]))
        except ImportError:
            return []
    else:
        out = subprocess.run(["ps", "-Ao", "command"], capture_output=True, text=True).stdout
    hits = []
    for pat, name in (("manim", "a manim render"), ("compose.py", "a kit render"), ("composite.py", "a composite"),
                      ("transcribe.py", "a transcription"), ("answer_overlay.py", "an answer overlay")):
        for ln in out.splitlines():
            if "machine_guard" in ln:
                continue
            # MATCH THE PROGRAM, NOT THE PATH. This repo is called
            # manim-video-solution-generator, so every process it launches has
            # "manim" in its command line — including this guard's own
            # interpreter. A bare substring test therefore reported a render in
            # progress whenever anything at all was running here, and refused
            # every job. "manim" must be the executable's own name; the .py
            # tools must appear as a script argument.
            toks = ln.split()
            if pat == "manim":
                hit = any(t.rsplit("/", 1)[-1] == "manim" for t in toks)
            else:
                hit = any(t.rsplit("/", 1)[-1] == pat for t in toks)
            if not hit:
                continue
            # IGNORE THE SHELL THAT IS ABOUT TO RUN US. This guard is normally
            # invoked as `machine_guard.py && ... manim ...`, so the parent
            # shell's own command line contains the word we are looking for and
            # the guard reported the job it was being asked to clear — it
            # refused every render until this was fixed. Only a real executable
            # counts, never a shell holding the string as an argument.
            head = ln.split()[0] if ln.split() else ""
            if head.rsplit("/", 1)[-1] in ("sh", "zsh", "bash", "env", "nohup", "nice"):
                continue
            hits.append(name)
            break
    return hits


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--need-disk", type=float, default=8.0, help="GB of disk headroom")
    ap.add_argument("--need-ram", type=float, default=2.5, help="GB of usable RAM")
    ap.add_argument("--job", default="this job")
    a = ap.parse_args()

    disk = shutil.disk_usage("/").free / 1024**3
    ram = free_ram_gb()
    sw_used, sw_free = swap_used_gb()
    running = busy()

    print(f"  disk free {disk:.1f} GB (need {a.need_disk:.0f})   "
          f"usable RAM {ram:.1f} GB (need {a.need_ram:.1f})   "
          f"swap {sw_used:.1f} GB used, {sw_free:.1f} GB free")

    stop = []
    if running:
        stop.append("already running: " + ", ".join(running)
                    + " — ONE heavy job at a time on this machine")
    if disk < a.need_disk:
        stop.append(f"only {disk:.1f} GB of disk; the swap file grows into the same "
                    f"space, so a render here is what fills the disk and freezes the box")
    if ram < a.need_ram:
        stop.append(f"only {ram:.1f} GB of usable RAM")
    # SWAP IS REPORTED, NOT ENFORCED. macOS grows swap files on demand, so the
    # "free" figure is space inside the files ALREADY allocated, not remaining
    # capacity — this box idles at 0.7-1.4 GB free swap and is fine. Blocking on
    # it refused renders the machine could run. What actually bounds swap, and
    # what was at zero when the machine froze, is DISK, which is the hard gate
    # above. A big swap file is still worth saying out loud, because it is disk
    # that a reboot would hand back.
    if sw_free < 1.0:
        print(f"  note: only {sw_free:.1f} GB free inside the current swap files; "
              f"a reboot would return their {sw_used:.0f} GB to the disk")

    if stop:
        print(f"\n  REFUSING TO START {a.job}:")
        for s in stop:
            print(f"    - {s}")
        return 1
    print(f"  ok to start {a.job}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
