"""Refuse to start a render when the machine cannot take one.

    python tools/machine_ready.py

An 8GB Mac running two render streams drove swap to 13.4GB of 14.3GB. macOS
does not give swap back, so long after the renders stopped every allocation was
competing for the last 900MB and the user's windows stopped responding — apps
were being killed while the project sat idle.

So the check runs BEFORE a render starts, not after the machine is on its knees.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys

MIN_SWAP_FREE_GB = 3.0
MIN_DISK_FREE_GB = 3.0


def swap_free_gb() -> float | None:
    out = subprocess.run(["sysctl", "vm.swapusage"], capture_output=True, text=True).stdout
    m = re.search(r"free = ([\d.]+)M", out)
    return float(m.group(1)) / 1024 if m else None


def disk_free_gb() -> float:
    out = subprocess.run(["df", "-g", "/System/Volumes/Data"], capture_output=True, text=True).stdout
    return float(out.splitlines()[1].split()[3])


def main() -> int:
    # ALLOW_LOW=1 turns the block into a warning. The user may have other work
    # running that keeps swap high permanently; refusing forever is not useful.
    override = os.environ.get("ALLOW_LOW") == "1"
    problems = []
    sf = swap_free_gb()
    if sf is not None and sf < MIN_SWAP_FREE_GB:
        problems.append(
            f"swap has only {sf:.1f}GB free — the machine is thrashing and "
            f"windows will stop responding. RESTART to clear swap, then re-run.")
    df = disk_free_gb()
    if df < MIN_DISK_FREE_GB:
        problems.append(f"disk has only {df:.0f}GB free — renders fail silently "
                        f"when the disk fills.")
    if not problems:
        print(f"  machine ok: swap {sf:.1f}GB free, disk {df:.0f}GB free")
        return 0
    head = "  proceeding anyway (ALLOW_LOW=1) —" if override else \
           "  NOT STARTING — the machine is not in a state to render:"
    print(head)
    for p in problems:
        print(f"    {p}")
    return 0 if override else 1


if __name__ == "__main__":
    raise SystemExit(main())
