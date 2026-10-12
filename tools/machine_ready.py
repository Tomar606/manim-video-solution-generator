"""Refuse to start a render when the machine cannot take one.

    python tools/machine_ready.py

An 8GB Mac running two render streams drove swap to 13.4GB of 14.3GB. macOS
does not give swap back, so long after the renders stopped every allocation was
competing for the last 900MB and the user's windows stopped responding — apps
were being killed while the project sat idle.

So the check runs BEFORE a render starts, not after the machine is on its knees.

WHAT IS MEASURED: SWAP USED, NOT SWAP FREE
------------------------------------------
This used to require 3GB of swap FREE. macOS grows swap one file at a time as
it needs it, so "free" is only the unused part of whatever files exist at that
moment — and a freshly restarted Mac has 3GB of swap in total. On 2026-09-21,
straight after the restart this check itself asked for, it read 1.4GB used,
1.7GB free and refused: the one state it could never pass was the healthy one.
What marks the meltdown is how much is USED — 13.4GB in the incident above,
10.4-13.6GB on 2026-09-21 before the restart — against ~4.4GB in ordinary use
on this machine. So: refuse above MAX_SWAP_USED_GB, and whenever the kernel
itself reports CRITICAL memory pressure.

The ceiling was 8GB until 2026-09-24. That day the machine sat at 7.8-9.3GB
with only VS Code and a music tab open, pressure level 2 (warn), and the
presenter measurement ran normally — the user: "the laptop always used this
much swap". 8GB refused the machine's ordinary state, so the ceiling sits just
under the lowest meltdown reading instead.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys

MAX_SWAP_USED_GB = 10.0  # ordinary use 7.8-9.3GB (2026-09-24); the meltdowns were 10.4-13.6GB
MIN_DISK_FREE_GB = 3.0
CRITICAL = 4             # kern.memorystatus_vm_pressure_level: 1 normal, 2 warn, 4 critical


def swap_used_gb() -> float | None:
    out = subprocess.run(["sysctl", "vm.swapusage"], capture_output=True, text=True).stdout
    m = re.search(r"used = ([\d.]+)M", out)
    return float(m.group(1)) / 1024 if m else None


def pressure_level() -> int | None:
    out = subprocess.run(["sysctl", "-n", "kern.memorystatus_vm_pressure_level"],
                         capture_output=True, text=True).stdout.strip()
    return int(out) if out.isdigit() else None


def disk_free_gb() -> float:
    out = subprocess.run(["df", "-g", "/System/Volumes/Data"], capture_output=True, text=True).stdout
    return float(out.splitlines()[1].split()[3])


def main() -> int:
    # ALLOW_LOW=1 turns the block into a warning. The user may have other work
    # running that keeps swap high permanently; refusing forever is not useful.
    override = os.environ.get("ALLOW_LOW") == "1"
    problems = []
    su = swap_used_gb()
    if su is not None and su > MAX_SWAP_USED_GB:
        problems.append(
            f"{su:.1f}GB of swap in use — the machine is thrashing and "
            f"windows will stop responding. RESTART to clear swap, then re-run.")
    pl = pressure_level()
    if pl is not None and pl >= CRITICAL:
        problems.append("the kernel reports CRITICAL memory pressure — close something "
                        "large before starting a render.")
    df = disk_free_gb()
    if df < MIN_DISK_FREE_GB:
        problems.append(f"disk has only {df:.0f}GB free — renders fail silently "
                        f"when the disk fills.")
    if not problems:
        print(f"  machine ok: swap {su:.1f}GB used, pressure level {pl}, disk {df:.0f}GB free")
        return 0
    head = "  proceeding anyway (ALLOW_LOW=1) —" if override else \
           "  NOT STARTING — the machine is not in a state to render:"
    print(head)
    for p in problems:
        print(f"    {p}")
    return 0 if override else 1


if __name__ == "__main__":
    raise SystemExit(main())
