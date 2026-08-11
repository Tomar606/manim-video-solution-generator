"""ElevenLabs multi-voice text-to-speech.

Each dialogue segment is synthesized with its speaker's voice, measured, then
padded to ``audio_duration + gap`` so the segment's animation can be timed to
the exact spoken length. Voices may be given as ElevenLabs voice IDs or as
voice names (resolved against the account's voice library).
"""
from __future__ import annotations

import os
import re
from pathlib import Path

from src.media import pad_audio, probe_duration
from src.script_models import VideoScript

DEFAULT_MODEL_ID = os.getenv("ELEVENLABS_MODEL", "eleven_multilingual_v2")
DEFAULT_OUTPUT_FORMAT = "mp3_44100_128"
INTER_LINE_GAP = float(os.getenv("TTS_GAP_SECONDS", "0.4"))

_client = None
_voice_cache: dict[str, str] = {}


def get_client():
    global _client
    if _client is None:
        from elevenlabs.client import ElevenLabs  # lazy import

        api_key = os.getenv("ELEVENLABS_API_KEY")
        if not api_key:
            raise RuntimeError(
                "ELEVENLABS_API_KEY is not set. Add it to your environment/.env."
            )
        _client = ElevenLabs(api_key=api_key)
    return _client


def _looks_like_id(value: str) -> bool:
    # ElevenLabs voice IDs are ~20-char alphanumeric tokens with no spaces.
    return bool(value) and " " not in value and len(value) >= 18


def resolve_voice_id(voice: str) -> str:
    """Resolve a voice name/ID to a concrete voice ID.

    Order: explicit ID -> exact name match in the account library ->
    ELEVENLABS_DEFAULT_VOICE env fallback.
    """
    if not voice:
        fallback = os.getenv("ELEVENLABS_DEFAULT_VOICE")
        if fallback:
            return fallback
        raise RuntimeError(
            "A speaker has no voice and ELEVENLABS_DEFAULT_VOICE is unset."
        )
    if voice in _voice_cache:
        return _voice_cache[voice]
    if _looks_like_id(voice):
        _voice_cache[voice] = voice
        return voice

    # Resolve by name against the library. ElevenLabs display names are often
    # "Name - descriptor" (e.g. "Alice - Clear, Engaging Educator"), so match on
    # the leading name token as well as the full string.
    client = get_client()
    try:
        library = client.voices.get_all().voices
    except Exception as exc:  # network / auth
        raise RuntimeError(f"Could not list ElevenLabs voices: {exc}") from exc

    def _lead(name: str) -> str:
        return re.split(r"\s*[-,]\s*", name.strip(), maxsplit=1)[0].strip().lower()

    want = voice.strip().lower()
    # Priority: exact full > exact leading token > leading startswith > substring.
    matchers = [
        lambda n: n.strip().lower() == want,
        lambda n: _lead(n) == want,
        lambda n: _lead(n).startswith(want),
        lambda n: want in n.strip().lower(),
    ]
    for match in matchers:
        for v in library:
            if match(getattr(v, "name", "")):
                _voice_cache[voice] = v.voice_id
                return v.voice_id

    fallback = os.getenv("ELEVENLABS_DEFAULT_VOICE")
    if fallback:
        print(f"   ⚠️  Voice {voice!r} not found; using ELEVENLABS_DEFAULT_VOICE.")
        _voice_cache[voice] = fallback
        return fallback
    raise RuntimeError(
        f"Voice {voice!r} not found in your ElevenLabs library and no "
        f"ELEVENLABS_DEFAULT_VOICE fallback is set."
    )


def _voice_settings(settings: dict):
    if not settings:
        return None
    try:
        from elevenlabs import VoiceSettings

        return VoiceSettings(
            stability=float(settings.get("stability", 0.5)),
            similarity_boost=float(settings.get("similarity_boost", 0.75)),
            style=float(settings.get("style", 0.0)),
            use_speaker_boost=bool(settings.get("use_speaker_boost", True)),
        )
    except Exception:
        return None


def synthesize_line(text: str, voice_id: str, out_path: str,
                    settings: dict | None = None) -> str:
    """Synthesize one line to an mp3 file and return the path."""
    client = get_client()
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    audio = client.text_to_speech.convert(
        voice_id=voice_id,
        model_id=DEFAULT_MODEL_ID,
        text=text,
        output_format=DEFAULT_OUTPUT_FORMAT,
        voice_settings=_voice_settings(settings or {}),
    )
    with open(out_path, "wb") as f:
        for chunk in audio:
            if chunk:
                f.write(chunk)
    return out_path


def synthesize_script(script: VideoScript, audio_dir: str,
                      gap: float = INTER_LINE_GAP) -> None:
    """Synthesize every segment in place: sets ``audio_path`` (timed/padded),
    ``audio_duration`` (raw) and ``target_duration`` (raw + gap)."""
    audio_dir_p = Path(audio_dir)
    audio_dir_p.mkdir(parents=True, exist_ok=True)

    for seg in script.segments:
        if not seg.narration.strip():
            # No spoken line — give it a short silent beat so visuals still show.
            seg.audio_duration = 0.0
            seg.target_duration = max(gap, 1.2)
            silent = str(audio_dir_p / f"seg_{seg.index:03d}_timed.mp3")
            _make_silence(silent, seg.target_duration)
            seg.audio_path = silent
            continue

        speaker = script.speakers.get(seg.speaker)
        voice_id = resolve_voice_id(speaker.voice_id if speaker else "")
        raw = str(audio_dir_p / f"seg_{seg.index:03d}_raw.mp3")
        synthesize_line(seg.narration, voice_id, raw,
                        settings=speaker.settings if speaker else None)

        seg.audio_duration = probe_duration(raw)
        seg.target_duration = round(seg.audio_duration + gap, 3)
        timed = str(audio_dir_p / f"seg_{seg.index:03d}_timed.mp3")
        pad_audio(raw, timed, seg.target_duration)
        seg.audio_path = timed
        print(f"   🎙️  seg {seg.index} [{seg.speaker}] "
              f"{seg.audio_duration:.2f}s -> target {seg.target_duration:.2f}s")


def _make_silence(out_path: str, seconds: float) -> str:
    from src.media import _run

    _run([
        "ffmpeg", "-y", "-f", "lavfi", "-i",
        "anullsrc=channel_layout=stereo:sample_rate=44100",
        "-t", f"{seconds:.3f}", "-c:a", "libmp3lame", "-b:a", "192k", out_path,
    ])
    return out_path
