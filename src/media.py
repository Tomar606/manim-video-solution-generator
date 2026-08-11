"""ffmpeg/ffprobe helpers shared by the TTS and assembly stages.

Kept dependency-free (subprocess + ffmpeg on PATH) so timing math and A/V
muxing behave identically wherever ffmpeg is installed.
"""
from __future__ import annotations

import subprocess
from pathlib import Path


class MediaError(RuntimeError):
    pass


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
