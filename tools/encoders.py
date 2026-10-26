"""The fastest H.264 encoder this machine actually has: the GPU's when there is one, x264 otherwise.

    from encoders import video_args          # tools/ on sys.path
    ffmpeg ... + video_args() + [out.mp4]

    python tools/encoders.py                  # which one this machine would use

Order: Apple VideoToolbox on a Mac; then NVIDIA NVENC, Intel Quick Sync, AMD AMF; then libx264 on the CPU.
Each GPU encoder is proved with a tenth of a second of test encode before it is chosen: ffmpeg lists
encoders whose driver or hardware is missing, and a listed-but-broken encoder would fail a render 40 minutes
in. KIT_ENCODER=<name> forces one (for example libx264, to compare).

All of them get the same targets (about 14 Mbit/s, capped at 20), so a reel looks the same whichever
machine made it.
"""
from __future__ import annotations

import functools
import os
import subprocess
import sys

RATE = ["-b:v", "14M", "-maxrate", "20M", "-bufsize", "28M"]
ARGS = {
    "h264_videotoolbox": ["-c:v", "h264_videotoolbox", *RATE, "-pix_fmt", "yuv420p"],
    "h264_nvenc": ["-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "19", *RATE, "-pix_fmt", "yuv420p"],
    "h264_qsv": ["-c:v", "h264_qsv", "-preset", "slow", *RATE, "-pix_fmt", "nv12"],
    "h264_amf": ["-c:v", "h264_amf", "-quality", "quality", *RATE, "-pix_fmt", "yuv420p"],
    "libx264": ["-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-maxrate", "20M", "-bufsize", "28M",
                "-pix_fmt", "yuv420p"],
}


def works(name: str) -> bool:
    if name == "libx264":
        return True
    try:
        r = subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "color=c=gray:s=320x568:d=0.1:r=30",
                            *ARGS[name], "-f", "null", "-"], capture_output=True, timeout=30)
        return r.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


@functools.lru_cache(maxsize=1)
def encoder() -> str:
    forced = os.environ.get("KIT_ENCODER", "").strip()
    if forced in ARGS:
        return forced
    order = (["h264_videotoolbox"] if sys.platform == "darwin" else []) + ["h264_nvenc", "h264_qsv", "h264_amf"]
    return next((e for e in order if works(e)), "libx264")


def video_args() -> list[str]:
    return list(ARGS[encoder()])


if __name__ == "__main__":
    print(encoder())
