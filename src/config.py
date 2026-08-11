"""Global configuration: orientation, resolution, and render settings.

Dependency-free (stdlib only) so it can be imported and tested without manim,
pydantic, or any API client installed.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


# Standard broadcast chroma-key green. Overridable per render (some editors
# prefer 0x00B140 "digital green"; 0x00FF00 keys most cleanly in Manim output).
DEFAULT_CHROMA_GREEN = "#00FF00"
ALT_CHROMA_BLUE = "#0047FF"


class Orientation(str, Enum):
    """Video orientation. Drives render resolution and Manim frame shape."""

    LANDSCAPE = "landscape"  # 16:9 — YouTube, lectures
    PORTRAIT = "portrait"    # 9:16 — Reels, Shorts, TikTok

    @classmethod
    def parse(cls, value: str) -> "Orientation":
        v = (value or "").strip().lower()
        aliases = {
            "landscape": cls.LANDSCAPE, "16:9": cls.LANDSCAPE, "wide": cls.LANDSCAPE,
            "horizontal": cls.LANDSCAPE, "l": cls.LANDSCAPE,
            "portrait": cls.PORTRAIT, "9:16": cls.PORTRAIT, "vertical": cls.PORTRAIT,
            "reel": cls.PORTRAIT, "short": cls.PORTRAIT, "p": cls.PORTRAIT,
        }
        if v not in aliases:
            raise ValueError(
                f"Unknown orientation {value!r}. Use 'landscape' or 'portrait'."
            )
        return aliases[v]

    @property
    def resolution(self) -> tuple[int, int]:
        """(pixel_width, pixel_height) at 1080p-class quality."""
        return (1920, 1080) if self is Orientation.LANDSCAPE else (1080, 1920)

    @property
    def aspect_ratio(self) -> float:
        w, h = self.resolution
        return w / h

    @property
    def manim_frame(self) -> tuple[float, float]:
        """(frame_width, frame_height) in Manim units.

        Manim keeps frame_height at 8.0 and scales frame_width by aspect.
        Landscape: 14.22 x 8.0. Portrait: 8.0 x 14.22 (tall & narrow).
        """
        if self is Orientation.LANDSCAPE:
            return (14.222222, 8.0)
        # Portrait: swap so the *height* is the long edge.
        return (8.0, 14.222222)


# Normalized rectangle: (x, y, w, h) in 0..1, origin at TOP-LEFT, y downward
# (standard video convention). Converted to Manim coords in manim_helpers.
NormRect = tuple[float, float, float, float]


class ChromaPreset(str, Enum):
    NONE = "none"
    LOWER_THIRD = "lower_third"
    UPPER_THIRD = "upper_third"
    BOTTOM_HALF = "bottom_half"
    LEFT_HALF = "left_half"
    RIGHT_HALF = "right_half"
    FULL = "full"          # entire frame keyed (Manim content only, over green)
    CUSTOM = "custom"

    @classmethod
    def parse(cls, value: str) -> "ChromaPreset":
        v = (value or "none").strip().lower()
        try:
            return cls(v)
        except ValueError:
            raise ValueError(
                f"Unknown chroma preset {value!r}. One of: "
                f"{', '.join(p.value for p in cls)}"
            )


@dataclass(frozen=True)
class ChromaZone:
    """A region rendered as flat chroma-key color for downstream compositing.

    ``preset`` picks a common region; ``custom_rect`` overrides it (normalized,
    top-left origin). ``animate_in`` makes the zone fade/slide in from the theme
    background instead of being present from frame one.
    """

    preset: ChromaPreset = ChromaPreset.NONE
    color: str = DEFAULT_CHROMA_GREEN
    animate_in: bool = False
    gradient: bool = False                     # blend the theme bg into the zone
    gradient_frac: float = 0.35                # top fraction of the zone that fades
    custom_rect: NormRect | None = None       # zone, when preset == CUSTOM
    custom_safe: NormRect | None = None        # safe area, when preset == CUSTOM

    @property
    def enabled(self) -> bool:
        return self.preset is not ChromaPreset.NONE

    def zone_rect(self) -> NormRect | None:
        """Normalized rect the chroma color fills. None when disabled."""
        p = self.preset
        table: dict[ChromaPreset, NormRect] = {
            ChromaPreset.LOWER_THIRD: (0.0, 2 / 3, 1.0, 1 / 3),
            ChromaPreset.UPPER_THIRD: (0.0, 0.0, 1.0, 1 / 3),
            ChromaPreset.BOTTOM_HALF: (0.0, 0.5, 1.0, 0.5),
            ChromaPreset.LEFT_HALF: (0.0, 0.0, 0.5, 1.0),
            ChromaPreset.RIGHT_HALF: (0.5, 0.0, 0.5, 1.0),
            ChromaPreset.FULL: (0.0, 0.0, 1.0, 1.0),
        }
        if p is ChromaPreset.NONE:
            return None
        if p is ChromaPreset.CUSTOM:
            return self.custom_rect
        return table[p]

    def safe_rect(self) -> NormRect:
        """Normalized rect where animated content may be drawn (avoids zone)."""
        p = self.preset
        table: dict[ChromaPreset, NormRect] = {
            ChromaPreset.LOWER_THIRD: (0.0, 0.0, 1.0, 2 / 3),
            ChromaPreset.UPPER_THIRD: (0.0, 1 / 3, 1.0, 2 / 3),
            ChromaPreset.BOTTOM_HALF: (0.0, 0.0, 1.0, 0.5),
            ChromaPreset.LEFT_HALF: (0.5, 0.0, 0.5, 1.0),
            ChromaPreset.RIGHT_HALF: (0.0, 0.0, 0.5, 1.0),
            ChromaPreset.FULL: (0.0, 0.0, 1.0, 1.0),  # content over green
            ChromaPreset.NONE: (0.0, 0.0, 1.0, 1.0),
        }
        if p is ChromaPreset.CUSTOM:
            return self.custom_safe or (0.0, 0.0, 1.0, 1.0)
        return table[p]


@dataclass(frozen=True)
class AvatarConfig:
    """Where the (chroma-keyed) presenter sits over the animation, and how
    aggressively the green is removed.

    ``placement: auto`` means "wherever the script's chroma zone is" — the
    keyed-out region of the Manim render is exactly the box the avatar fills,
    so a script that reserves space for a presenter automatically composites
    one into that space. Any preset overrides that.
    """

    enabled: bool = True
    placement: str = "auto"            # auto | <chroma preset name> | custom
    custom_rect: NormRect | None = None
    scale: float = 1.0                 # fine-tune size within the box
    offset: tuple[float, float] = (0.0, 0.0)   # normalized nudge (x, y)
    key_color: str = DEFAULT_CHROMA_GREEN
    similarity: float = 0.14           # chromakey tolerance (0.01–1.0)
    blend: float = 0.08                # edge softness
    despill: float = 0.5               # green fringe removal strength (0–1)
    timing: str = "audio"              # audio = TTS drives, avatar = clips drive

    def box(self, chroma: "ChromaZone") -> NormRect:
        """The normalized rect the avatar is fitted into."""
        if self.placement == "custom" and self.custom_rect:
            return self.custom_rect
        if self.placement == "auto":
            zone = chroma.zone_rect()
            # No keyed zone authored: stand the presenter in the right third.
            return zone if zone else (0.62, 0.30, 0.38, 0.70)
        preset = ChromaPreset.parse(self.placement)
        rect = ChromaZone(preset=preset).zone_rect()
        if rect is None:
            raise ValueError(
                f"Avatar placement {self.placement!r} does not define a region."
            )
        return rect


@dataclass(frozen=True)
class RenderSettings:
    """How Manim should render. Kept small and explicit."""

    orientation: Orientation = Orientation.LANDSCAPE
    fps: int = 30
    # Manim quality flag maps resolution; we pass explicit -r instead so both
    # orientations render at full 1080-class resolution.
    background_transparent: bool = False
    chroma: ChromaZone = field(default_factory=ChromaZone)

    @property
    def resolution_flag(self) -> list[str]:
        w, h = self.orientation.resolution
        return ["-r", f"{w},{h}"]
