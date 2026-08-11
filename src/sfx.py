"""Sound effects, driven by cues the scenes emit while they render.

A scene knows *when* something happens — an equation lands, a photo appears, a
step is revealed — but the render itself is silent (we strip audio when
conforming clips so A/V stays locked). So instead of baking sound into the
render, a scene calls ``self.cue("pop")`` and Manim writes a sidecar JSON of
``(time, name, gain)`` next to the video. At assembly time every cue is offset
by its segment's start in the final timeline and mixed onto the narration track.

That split is what makes the effects automatic: the templates cue themselves,
and generated scenes are told to cue their own key moments, so a video gets its
sound design from the animation rather than from someone scrubbing a timeline.

The default library is synthesized locally with ffmpeg — no downloads, no
licensing questions, identical on every machine. Drop a file with the same name
into ``assets/sfx/`` to override any of them with your own.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from src import media

SFX_DIRNAME = "sfx"

# Default gain per effect (dB relative to the narration bed). Effects sit under
# the voice — they punctuate, they don't compete.
DEFAULT_GAIN = -12.0

# name -> ffmpeg lavfi recipe producing a short mono cue.
# Kept deliberately plain: clean synthesized shapes read as "designed" rather
# than as stock sound, and they never clash with narration.
_RECIPES: dict[str, str] = {
    # Soft percussive tick for an element appearing.
    "pop": (
        "sine=frequency=760:duration=0.16,"
        "afade=t=out:st=0.02:d=0.14:curve=exp,volume=0.7"
    ),
    # Brighter confirmation — a step resolving, a result landing.
    "ding": (
        "sine=frequency=1180:duration=0.55,"
        "afade=t=out:st=0.05:d=0.50:curve=exp,volume=0.6"
    ),
    # Air movement for something sliding/transforming in.
    "whoosh": (
        "anoisesrc=color=brown:duration=0.42:amplitude=0.5,"
        "highpass=f=300,lowpass=f=3600,"
        "afade=t=in:st=0:d=0.16,afade=t=out:st=0.18:d=0.24,volume=0.55"
    ),
    # Tiny tick for emphasis/underline.
    "click": (
        "anoisesrc=color=white:duration=0.05:amplitude=0.4,"
        "highpass=f=1200,afade=t=out:st=0:d=0.05,volume=0.5"
    ),
    # Pen-on-paper texture while something is being written.
    "write": (
        "anoisesrc=color=pink:duration=0.7:amplitude=0.28,"
        "highpass=f=900,lowpass=f=5200,"
        "afade=t=in:st=0:d=0.08,afade=t=out:st=0.45:d=0.25,volume=0.45"
    ),
    # Scene change / photo reveal.
    "reveal": (
        "anoisesrc=color=brown:duration=0.75:amplitude=0.55,"
        "highpass=f=200,lowpass=f=5000,"
        "afade=t=in:st=0:d=0.35,afade=t=out:st=0.4:d=0.35,volume=0.5"
    ),
    # Low accent under a title or a section break.
    "impact": (
        "sine=frequency=120:duration=0.6,"
        "afade=t=out:st=0.03:d=0.57:curve=exp,volume=0.75"
    ),
}

CUE_NAMES = tuple(sorted(_RECIPES))

# Above this many cues the ffmpeg command gets unwieldy; we mix the first N and
# say so rather than silently dropping the rest.
MAX_CUES = 80


@dataclass
class Cue:
    """One sound placed at ``time`` seconds into the final video."""

    time: float
    name: str
    gain: float = DEFAULT_GAIN

    @classmethod
    def from_dict(cls, raw: dict, *, offset: float = 0.0) -> "Cue":
        return cls(
            time=max(0.0, float(raw.get("time", 0.0)) + offset),
            name=str(raw.get("name", "pop")),
            gain=float(raw.get("gain", DEFAULT_GAIN)),
        )


def sfx_dir(asset_root: str | Path) -> Path:
    return Path(asset_root) / "assets" / SFX_DIRNAME


def ensure_library(asset_root: str | Path, *, force: bool = False) -> list[Path]:
    """Synthesize any missing default effects. Returns the files present."""
    out_dir = sfx_dir(asset_root)
    out_dir.mkdir(parents=True, exist_ok=True)
    built: list[Path] = []
    for name, recipe in _RECIPES.items():
        dest = out_dir / f"{name}.wav"
        if dest.exists() and dest.stat().st_size > 0 and not force:
            built.append(dest)
            continue
        try:
            media._run([
                "ffmpeg", "-y", "-f", "lavfi", "-i", recipe,
                "-ac", "1", "-ar", "44100", "-c:a", "pcm_s16le", str(dest),
            ])
            built.append(dest)
        except media.MediaError as exc:
            print(f"   ⚠️  could not synthesize sfx {name}: {exc}")
    return built


def resolve(name: str, asset_root: str | Path) -> Path | None:
    """Find the file for a cue name. User-supplied files win over defaults."""
    directory = sfx_dir(asset_root)
    for suffix in (".wav", ".mp3", ".m4a", ".aac", ".ogg"):
        candidate = directory / f"{name}{suffix}"
        if candidate.is_file():
            return candidate
    return None


def read_cue_file(path: str | Path, *, offset: float = 0.0) -> list[Cue]:
    """Load a scene's sidecar cue file. A missing/broken file means no sound —
    never a failed build."""
    p = Path(path)
    if not p.is_file():
        return []
    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    entries = raw.get("cues", raw) if isinstance(raw, dict) else raw
    if not isinstance(entries, list):
        return []
    cues: list[Cue] = []
    for item in entries:
        if isinstance(item, dict):
            try:
                cues.append(Cue.from_dict(item, offset=offset))
            except (TypeError, ValueError):
                continue
    return cues


def cue_path_for(video_path: str | Path) -> Path:
    """Sidecar path a scene writes its cues to, given its output video."""
    return Path(video_path).with_suffix(".cues.json")


def mix(narration_path: str, cues: list[Cue], out_path: str,
        *, asset_root: str | Path, duration: float | None = None) -> str:
    """Mix cues onto the narration track. Returns the written path.

    If there is nothing to mix (no cues, or no matching sound files) the
    narration is passed through untouched, so this is always safe to call.
    """
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    placed: list[tuple[Cue, Path]] = []
    missing: set[str] = set()
    for cue in sorted(cues, key=lambda c: c.time):
        if duration is not None and cue.time >= duration:
            continue
        path = resolve(cue.name, asset_root)
        if path is None:
            missing.add(cue.name)
            continue
        placed.append((cue, path))

    if missing:
        print(f"   ⚠️  no sound file for cue(s): {', '.join(sorted(missing))}")
    if len(placed) > MAX_CUES:
        print(f"   ⚠️  {len(placed)} cues found; mixing the first {MAX_CUES}")
        placed = placed[:MAX_CUES]
    if not placed:
        import shutil
        shutil.copy(narration_path, out_path)
        return out_path

    cmd = ["ffmpeg", "-y", "-i", narration_path]
    for _, path in placed:
        cmd += ["-i", str(path)]

    filters = []
    labels = ["[0:a]"]
    for i, (cue, _) in enumerate(placed, start=1):
        delay_ms = int(round(cue.time * 1000))
        filters.append(
            f"[{i}:a]adelay={delay_ms}|{delay_ms},volume={cue.gain}dB[s{i}]"
        )
        labels.append(f"[s{i}]")
    # normalize=0 keeps the narration at its original level; without it ffmpeg
    # divides every input by the number of streams and the voice drops away.
    filters.append(
        f"{''.join(labels)}amix=inputs={len(labels)}:duration=first:"
        f"dropout_transition=0:normalize=0[out]"
    )

    cmd += [
        "-filter_complex", ";".join(filters),
        "-map", "[out]",
        "-ar", "44100", "-ac", "2", "-c:a", "libmp3lame", "-b:a", "192k",
        out_path,
    ]
    media._run(cmd)
    print(f"   mixed {len(placed)} sound effect(s) into the narration")
    return out_path
