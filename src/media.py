"""ffmpeg/ffprobe helpers shared by the TTS and assembly stages.

Kept dependency-free (subprocess + ffmpeg on PATH) so timing math and A/V
muxing behave identically wherever ffmpeg is installed.
"""
from __future__ import annotations

import functools
import os
import subprocess
from pathlib import Path


class MediaError(RuntimeError):
    pass



def video_codec(final: bool = True) -> list[str]:
    """ffmpeg's output-codec arguments, for a FINAL file or a scratch one.

    A part is encoded end to end four times — background concat, composite,
    chips, answer card — and only the last of those is delivered. The other
    three do almost no work per pixel and still paid a full x264 `medium`
    encode, which is the bulk of a build's wall clock.

    The scratch passes now go to the hardware encoder when one exists.
    Measured on 300 frames against a lossless reference:

        x264 medium crf18   12.2s   3.0 MB   PSNR 36.65   SSIM 0.9932
        videotoolbox 12M     5.3s  11.3 MB   PSNR 36.62   SSIM 0.9925

    — a difference of 0.04 dB and 0.0007 SSIM, far below anything visible, for
    a third of the time. It costs file SIZE, which is why it is not used for
    the delivered file: x264 is much more bit-efficient, and the master should
    stay small as well as clean.

    `preset veryfast` was measured too and is NOT used: at 0.9904 SSIM it loses
    real quality, and a loss taken on a scratch pass is carried by every pass
    after it.

    FAST_INTERMEDIATE=0 forces software everywhere, for a like-for-like check.
    """
    if final or os.environ.get("FAST_INTERMEDIATE") == "0":
        return ["-c:v", "libx264", "-preset", "medium", "-crf", "18"]
    if not _has_videotoolbox():
        return ["-c:v", "libx264", "-preset", "medium", "-crf", "18"]
    return ["-c:v", "h264_videotoolbox", "-b:v", "12M"]


@functools.lru_cache(maxsize=1)
def _has_videotoolbox() -> bool:
    try:
        out = subprocess.run(["ffmpeg", "-hide_banner", "-encoders"],
                             capture_output=True, text=True, timeout=20).stdout
    except (OSError, subprocess.SubprocessError):
        return False
    return "h264_videotoolbox" in out


def _run(cmd: list[str]) -> subprocess.CompletedProcess:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise MediaError(
            f"Command failed ({' '.join(cmd[:3])}...):\n{proc.stderr[-2000:]}"
        )
    return proc


def probe_duration(path: str) -> float:
    """Return media duration in seconds (0.0 if unknown)."""
    try:
        out = _run([
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", path,
        ]).stdout.strip()
        return float(out)
    except (MediaError, ValueError):
        return 0.0


def has_streams(path: str) -> tuple[bool, bool]:
    """Return (has_video, has_audio)."""
    if not Path(path).exists():
        return (False, False)
    out = _run([
        "ffprobe", "-v", "error", "-show_entries", "stream=codec_type",
        "-of", "default=noprint_wrappers=1:nokey=1", path,
    ]).stdout
    return ("video" in out, "audio" in out)


def pad_audio(in_path: str, out_path: str, target_seconds: float,
              sample_rate: int = 44100) -> str:
    """Pad ``in_path`` with trailing silence to exactly ``target_seconds`` and
    re-encode to a uniform mp3 (so later concat is codec-consistent)."""
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    _run([
        "ffmpeg", "-y", "-i", in_path,
        "-af", f"apad,atrim=0:{target_seconds:.3f}",
        "-ar", str(sample_rate), "-ac", "2", "-c:a", "libmp3lame", "-b:a", "192k",
        out_path,
    ])
    return out_path


def concat_audio(paths: list[str], out_path: str) -> str:
    """Concatenate audio clips (re-encoded, order preserved)."""
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    list_file = Path(out_path).with_suffix(".txt")
    list_file.write_text(
        "".join(f"file '{Path(p).resolve()}'\n" for p in paths), encoding="utf-8"
    )
    try:
        _run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_file),
            "-ar", "44100", "-ac", "2", "-c:a", "libmp3lame", "-b:a", "192k",
            out_path,
        ])
    finally:
        list_file.unlink(missing_ok=True)
    return out_path


def concat_videos(paths: list[str], out_path: str) -> str:
    """Concatenate same-format video clips losslessly (concat demuxer copy)."""
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    list_file = Path(out_path).with_suffix(".txt")
    list_file.write_text(
        "".join(f"file '{Path(p).resolve()}'\n" for p in paths), encoding="utf-8"
    )
    try:
        _run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_file),
            "-c", "copy", out_path,
        ])
    finally:
        list_file.unlink(missing_ok=True)
    return out_path


def conform_video(in_path: str, out_path: str, target_seconds: float,
                  fps: int, width: int, height: int) -> str:
    """Force a rendered segment to exactly ``target_seconds`` and normalise its
    codec/fps/size so all segments concat cleanly.

    Short clips hold their final frame (tpad); long clips are trimmed. This is
    what guarantees each segment lines up with its (fixed-length) audio clip,
    independent of how accurately the animation hit its timing.
    """
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    # tpad clones the last frame so short clips have enough frames; the output
    # `-t` cap + CFR make the length frame-accurate (no 1-frame overshoot).
    vf = (
        f"tpad=stop_mode=clone:stop_duration={target_seconds:.3f},"
        f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
        f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={fps}"
    )
    _run([
        "ffmpeg", "-y", "-i", in_path, "-vf", vf,
        "-t", f"{target_seconds:.3f}", "-r", str(fps), "-vsync", "cfr",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-pix_fmt", "yuv420p", "-video_track_timescale", "90000",
        "-an", out_path,
    ])
    return out_path


def mux(video_path: str, audio_path: str, out_path: str) -> str:
    """Combine a (silent) video with an audio track. Video sets the length;
    audio is padded/trimmed to match via ``-shortest`` after apad."""
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    _run([
        "ffmpeg", "-y", "-i", video_path, "-i", audio_path,
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-map", "0:v:0", "-map", "1:a:0", "-shortest", out_path,
    ])
    return out_path
