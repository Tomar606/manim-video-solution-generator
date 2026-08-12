"""Core data models for the authored-script pipeline.

Deliberately plain dataclasses (no pydantic) so parsing, config, and assembly
are testable without third-party packages. LLM structured-output models live
next to the code that calls the API.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.config import AvatarConfig, ChromaZone, Orientation, RenderSettings
from src.images import ImageRef
from src.themes import Theme


@dataclass
class SpeakerConfig:
    """A named voice. ``voice_id`` is an ElevenLabs voice id (or name resolved
    later). ``settings`` carries optional per-voice ElevenLabs knobs."""

    name: str
    voice_id: str
    settings: dict[str, Any] = field(default_factory=dict)


@dataclass
class DialogueSegment:
    """One spoken line and the math/visuals that accompany it."""

    index: int
    speaker: str                       # key into VideoScript.speakers
    narration: str                     # spoken text (LaTeX stripped)
    equations: list[str] = field(default_factory=list)  # LaTeX (no $ delims)
    images: list[ImageRef] = field(default_factory=list)  # photos on this beat
    note: str | None = None            # optional director hint from the script
    is_outro: bool = False             # the answer-image beat that ends the video

    # Populated during the pipeline:
    audio_path: str | None = None          # timed (padded) clip used for mux
    audio_duration: float | None = None    # raw spoken length, measured (s)
    target_duration: float | None = None   # audio_duration + inter-line gap (s)
    manim_path: str | None = None
    video_path: str | None = None
    avatar_path: str | None = None         # dropped/generated presenter clip

    @property
    def has_math(self) -> bool:
        return bool(self.equations)

    @property
    def has_images(self) -> bool:
        return bool(self.images)

    @property
    def is_photo_beat(self) -> bool:
        """A beat that is *about* a photo. These render from a fixed template
        instead of generated code — deterministic output keeps photo beats
        looking identical across every video we ship."""
        return bool(self.images) and not self.equations


@dataclass
class VideoScript:
    """A fully-parsed input script ready to drive the pipeline."""

    title: str
    orientation: Orientation
    theme: Theme
    chroma: ChromaZone
    speakers: dict[str, SpeakerConfig]
    segments: list[DialogueSegment]
    source_path: str | None = None
    fps: int = 30
    # Which script the narration is written in: hinglish (Latin) | hindi
    # (Devanagari) | english. Drives which voice checks apply.
    language: str = "hinglish"
    avatar: AvatarConfig = field(default_factory=AvatarConfig)

    @property
    def render_settings(self) -> RenderSettings:
        return RenderSettings(orientation=self.orientation, chroma=self.chroma,
                              fps=self.fps)

    @property
    def avatar_box(self):
        """Normalized (x, y, w, h) the presenter is composited into."""
        return self.avatar.box(self.chroma)

    @property
    def images(self) -> list[ImageRef]:
        """Every image the script references, in order of appearance."""
        return [img for seg in self.segments for img in seg.images]

    @property
    def outro(self) -> DialogueSegment | None:
        return next((s for s in self.segments if s.is_outro), None)

    def prior_equations(self, upto_index: int) -> list[str]:
        """All equations established before ``upto_index`` (for continuity)."""
        out: list[str] = []
        for seg in self.segments:
            if seg.index >= upto_index:
                break
            out.extend(seg.equations)
        return out
