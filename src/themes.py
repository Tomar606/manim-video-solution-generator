"""Background/visual themes for concept & derivation videos.

A ``Theme`` is a flat, serializable description of colors, fonts, and background
style. The rendered background is produced by ``manim_helpers.build_background``
from these fields, so themes stay pure data (no manim import here) and can be
defined in code OR supplied/overridden from a script's frontmatter (brandable).

Design goal: clean, distraction-free backdrops that read well behind LaTeX and
diagrams, in both light and dark, landscape and portrait.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Any


class BackgroundStyle(str, Enum):
    SOLID = "solid"          # flat color
    GRADIENT = "gradient"    # smooth vertical/diagonal gradient
    GRID = "grid"            # subtle coordinate grid over solid
    DOTS = "dots"            # subtle dot matrix over solid
    VIGNETTE = "vignette"    # solid with darkened edges (cinematic)
    IMAGE = "image"          # a supplied artwork file, scaled to cover the frame


@dataclass(frozen=True)
class Theme:
    name: str
    background: str                      # base bg hex
    background_style: BackgroundStyle = BackgroundStyle.SOLID
    gradient_to: str | None = None       # second color for GRADIENT
    # Artwork backdrop for BackgroundStyle.IMAGE — a project-relative path.
    # ``background`` stays the matte color behind/around it (letterbox safety).
    background_image: str | None = None
    # Foreground palette
    primary: str = "#FFFFFF"             # main text / equations
    secondary: str = "#B8C1D9"           # supporting text
    muted: str = "#6B7280"               # de-emphasized / prior steps
    accent: str = "#4C8DFF"              # highlights, active step, underlines
    accent_2: str = "#FF7A59"            # secondary highlight
    # Structural line color (grid, dots, rules, diagram strokes)
    line: str = "#2A3350"
    # Typography
    font: str = "sans"                   # "sans" | "serif" | explicit font name
    is_dark: bool = True

    def with_overrides(self, **kwargs: Any) -> "Theme":
        """Return a copy with any fields overridden (brandable frontmatter)."""
        valid = {k: v for k, v in kwargs.items() if v is not None and hasattr(self, k)}
        if "background_style" in valid and isinstance(valid["background_style"], str):
            valid["background_style"] = BackgroundStyle(valid["background_style"])
        return replace(self, **valid)

    def to_dict(self) -> dict[str, Any]:
        d = self.__dict__.copy()
        d["background_style"] = self.background_style.value
        return d


THEMES: dict[str, Theme] = {
    # --- Dark variants ---
    "midnight": Theme(
        name="midnight",
        background="#0B1021",
        background_style=BackgroundStyle.GRADIENT,
        gradient_to="#161B33",
        primary="#F2F5FF", secondary="#AEB9DE", muted="#5C6890",
        accent="#5B8DEF", accent_2="#F2A65A", line="#232B47",
        font="serif", is_dark=True,
    ),
    "charcoal": Theme(
        name="charcoal",
        background="#141414",
        background_style=BackgroundStyle.SOLID,
        primary="#F5F5F5", secondary="#BDBDBD", muted="#6E6E6E",
        accent="#4DD0A7", accent_2="#E8B04B", line="#2A2A2A",
        font="sans", is_dark=True,
    ),
    "slate-grid": Theme(
        name="slate-grid",
        background="#0E1524",
        background_style=BackgroundStyle.GRID,
        primary="#EAF0FF", secondary="#9FB0D0", muted="#54627F",
        accent="#63B3ED", accent_2="#F6AD55", line="#1C2740",
        font="sans", is_dark=True,
    ),
    "deep-space": Theme(
        name="deep-space",
        background="#05070F",
        background_style=BackgroundStyle.DOTS,
        primary="#FFFFFF", secondary="#A6B0C3", muted="#4A5468",
        accent="#8B5CF6", accent_2="#22D3EE", line="#141A2B",
        font="serif", is_dark=True,
    ),
    "blackboard": Theme(
        name="blackboard",
        background="#0C1512",
        background_style=BackgroundStyle.VIGNETTE,
        primary="#EAF7EF", secondary="#A9C4B4", muted="#5B7367",
        accent="#F4D35E", accent_2="#7FD1AE", line="#17251F",
        font="serif", is_dark=True,
    ),
    "physics-bg": Theme(
        # Arivihan shorts backdrop: the supplied navy artwork, with a soft
        # educational palette tuned to read on it (never oversaturated).
        name="physics-bg",
        background="#0A1E3C",
        background_style=BackgroundStyle.IMAGE,
        background_image="background/physicsbg.jpeg",
        primary="#FFFFFF", secondary="#C9D8F0", muted="#7A93B8",
        accent="#5B9DF9", accent_2="#FFA75C", line="#2A4C7E",
        font="Poppins", is_dark=True,
    ),
    # --- Subject plates for the MP Board PYQ videos ---------------------- #
    # 1080x1920 portrait, downscaled 4:1 from the supplied 8K artwork. The art
    # sits in the left and right margins, so content must stay inside the safe
    # column measured per plate (see PIPELINE.md) as well as inside the top 60%.
    "chemistry-bg": Theme(
        name="chemistry-bg",
        background="#0B1B3A",
        background_style=BackgroundStyle.IMAGE,
        background_image="assets/backgrounds/chemistry.png",
        primary="#FFFFFF", secondary="#C9D8F0", muted="#7A93B8",
        accent="#5BC8F9", accent_2="#FFC15C", line="#2A4C7E",
        font="Poppins", is_dark=True,
    ),
    "physics-plate": Theme(
        name="physics-plate",
        background="#062A2E",
        background_style=BackgroundStyle.IMAGE,
        background_image="assets/backgrounds/physics.png",
        primary="#FFFFFF", secondary="#BFE0E4", muted="#6E9298",
        accent="#4FD1C5", accent_2="#FFC15C", line="#14484F",
        font="Poppins", is_dark=True,
    ),
    "biology-bg": Theme(
        name="biology-bg",
        background="#08302B",
        background_style=BackgroundStyle.IMAGE,
        background_image="assets/backgrounds/biology.png",
        primary="#FFFFFF", secondary="#BEE3D5", muted="#6E948A",
        accent="#57D9A3", accent_2="#FFC15C", line="#145043",
        font="Poppins", is_dark=True,
    ),
    "maths-bg": Theme(
        name="maths-bg",
        background="#1E1836",
        background_style=BackgroundStyle.IMAGE,
        background_image="assets/backgrounds/maths.png",
        primary="#FFFFFF", secondary="#D2C8EA", muted="#8B80AC",
        accent="#A78BFA", accent_2="#FFC15C", line="#3B3160",
        font="Poppins", is_dark=True,
    ),

    # --- Light variants ---
    "ivory": Theme(
        name="ivory",
        background="#F7F4EC",
        background_style=BackgroundStyle.SOLID,
        primary="#1F2430", secondary="#4A5060", muted="#9AA0AE",
        accent="#C05621", accent_2="#2C7A7B", line="#E4DFD2",
        font="serif", is_dark=False,
    ),
    "paper-grid": Theme(
        name="paper-grid",
        background="#FBFBF9",
        background_style=BackgroundStyle.GRID,
        primary="#1A1A1A", secondary="#444444", muted="#9A9A9A",
        accent="#2B6CB0", accent_2="#C53030", line="#E6E6E1",
        font="sans", is_dark=False,
    ),
}

DEFAULT_THEME = "midnight"


def get_theme(name: str | None) -> Theme:
    """Resolve a theme by name; falls back to the default with a clear error
    only when the name is given but unknown."""
    if not name:
        return THEMES[DEFAULT_THEME]
    key = name.strip().lower()
    if key not in THEMES:
        raise ValueError(
            f"Unknown theme {name!r}. Available: {', '.join(sorted(THEMES))}. "
            f"(Or define one inline in the script frontmatter under 'theme:'.)"
        )
    return THEMES[key]


def resolve_theme(spec: Any) -> Theme:
    """Resolve a theme from a frontmatter value.

    Accepts either a string (named theme) or a mapping. A mapping may name a
    base theme via ``base:`` and override any Theme field (brandable), e.g.::

        theme:
          base: midnight
          accent: "#FF3366"
          font: "Poppins"
    """
    if spec is None or isinstance(spec, str):
        return get_theme(spec if isinstance(spec, str) else None)
    if isinstance(spec, dict):
        base = get_theme(spec.get("base"))
        overrides = {k: v for k, v in spec.items() if k != "base"}
        return base.with_overrides(**overrides)
    raise ValueError(f"Invalid theme specification: {spec!r}")
