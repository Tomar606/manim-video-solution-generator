"""Reusable Manim scaffolding injected into every generated scene file.

The scene-code generator does NOT ask the model to hand-roll backgrounds. It
prepends a small generated config block (``THEME``, ``ORIENTATION``, ``CHROMA``,
and ``config.*`` render dimensions) followed by this module's body, then the
model's ``construct`` method. That guarantees:

  * consistent, clean backgrounds across all segments (identical -> seamless cuts)
  * theme colors available as helpers, not re-invented per scene
  * chroma-key zones painted uniformly, with a computed *safe area* so content
    never spills into the keyed region
  * one base class, ``ThemedScene``, that the model subclasses

Globals ``THEME`` / ``ORIENTATION`` / ``CHROMA`` are supplied by the injected
header; the fallback defaults below let this module import standalone for
linting/tests. Globals resolve at call time, so the header's assignments win.
"""
from __future__ import annotations

from manim import *  # noqa: F401,F403
import json as _json
import os as _os
import numpy as np
from pathlib import Path as _Path

# --- Fallback config so this file imports standalone (header overrides these) ---
try:  # pragma: no cover - exercised only when injected
    THEME  # type: ignore[used-before-def]
except NameError:
    THEME = {
        "name": "midnight",
        "background": "#0B1021",
        "background_style": "gradient",
        "gradient_to": "#161B33",
        "background_image": None,
        "primary": "#F2F5FF",
        "secondary": "#AEB9DE",
        "muted": "#5C6890",
        "accent": "#5B8DEF",
        "accent_2": "#F2A65A",
        "line": "#232B47",
        "font": "serif",
        "is_dark": True,
    }
    ORIENTATION = "landscape"
    CHROMA = {
        "enabled": False,
        "color": "#00FF00",
        "zone": None,      # normalized (x, y, w, h), top-left origin
        "safe": (0.0, 0.0, 1.0, 1.0),
        "animate_in": False,
    }
    ASSET_ROOT = str(_Path(__file__).resolve().parents[1])
    # One dict per photo on this segment (path/caption/layout/ken_burns/framed).
    IMAGES: list[dict] = []
    # Where this scene writes the sound cues it emitted (set by the header).
    CUES_PATH = ""


# --------------------------------------------------------------------------- #
# Bundled fonts                                                                #
# --------------------------------------------------------------------------- #
# Poppins ships in assets/fonts so renders look identical on the host and inside
# the (font-less) Docker image. Registration is best-effort: if manimpango can't
# take the file we silently fall back to the default sans, rather than failing
# the whole render over typography.
_FONTS_REGISTERED = False


def register_fonts() -> None:
    global _FONTS_REGISTERED
    if _FONTS_REGISTERED:
        return
    _FONTS_REGISTERED = True
    try:
        import manimpango
    except Exception:
        return
    font_dir = _Path(ASSET_ROOT) / "assets" / "fonts"
    if not font_dir.is_dir():
        return
    for ttf in sorted(font_dir.glob("*.ttf")):
        try:
            manimpango.register_font(str(ttf))
        except Exception:
            pass


def ui_font() -> str:
    """The display font for on-screen UI text (captions, labels)."""
    name = THEME.get("font", "sans")
    return "sans-serif" if name in ("sans", "serif") else name


# --------------------------------------------------------------------------- #
# Coordinate helpers (normalized top-left origin  ->  Manim world coords)      #
# --------------------------------------------------------------------------- #
def _fw() -> float:
    return float(config.frame_width)


def _fh() -> float:
    return float(config.frame_height)


def norm_point(nx: float, ny: float) -> np.ndarray:
    """Normalized (0..1, top-left origin) -> Manim point at frame depth 0."""
    return np.array([-_fw() / 2 + nx * _fw(), _fh() / 2 - ny * _fh(), 0.0])


def norm_rect_center(rect) -> np.ndarray:
    x, y, w, h = rect
    return norm_point(x + w / 2, y + h / 2)


def norm_rect_size(rect) -> tuple[float, float]:
    _, _, w, h = rect
    return (w * _fw(), h * _fh())


# --------------------------------------------------------------------------- #
# Background construction                                                      #
# --------------------------------------------------------------------------- #
def _full_rect(color: str, opacity: float = 1.0):
    r = Rectangle(width=_fw() + 0.2, height=_fh() + 0.2,
                  stroke_width=0, fill_color=color, fill_opacity=opacity)
    r.move_to(ORIGIN)
    return r


def _gradient_background(c1: str, c2: str, steps: int = 120):
    """Smooth vertical gradient built from stacked strips (robust across CE)."""
    group = VGroup()
    a = ManimColor(c1)
    b = ManimColor(c2)
    strip_h = (_fh() + 0.2) / steps
    for i in range(steps):
        t = i / max(steps - 1, 1)
        strip = Rectangle(width=_fw() + 0.2, height=strip_h + 0.02,
                          stroke_width=0,
                          fill_color=interpolate_color(a, b, t),
                          fill_opacity=1.0)
        strip.move_to(np.array([0.0, _fh() / 2 - strip_h * (i + 0.5), 0.0]))
        group.add(strip)
    return group


def _grid_overlay(line_color: str, spacing: float = 1.0, opacity: float = 0.14):
    lines = VGroup()
    x = spacing
    while x < _fw() / 2:
        for sx in (x, -x):
            lines.add(Line(np.array([sx, -_fh() / 2, 0]),
                           np.array([sx, _fh() / 2, 0]),
                           stroke_color=line_color, stroke_width=1.0,
                           stroke_opacity=opacity))
        x += spacing
    y = spacing
    while y < _fh() / 2:
        for sy in (y, -y):
            lines.add(Line(np.array([-_fw() / 2, sy, 0]),
                           np.array([_fw() / 2, sy, 0]),
                           stroke_color=line_color, stroke_width=1.0,
                           stroke_opacity=opacity))
        y += spacing
    return lines


def _dot_overlay(line_color: str, spacing: float = 0.9, opacity: float = 0.18):
    dots = VGroup()
    ny = -_fh() / 2 + spacing / 2
    while ny < _fh() / 2:
        nx = -_fw() / 2 + spacing / 2
        while nx < _fw() / 2:
            dots.add(Dot(np.array([nx, ny, 0]), radius=0.018,
                         fill_color=line_color, fill_opacity=opacity))
            nx += spacing
        ny += spacing
    return dots


def _vignette_overlay(steps: int = 40, strength: float = 0.55):
    """Darken top and bottom edges for a cinematic feel."""
    group = VGroup()
    band = (_fh() + 0.2) * 0.22
    strip_h = band / steps
    for edge in (1, -1):
        for i in range(steps):
            t = i / max(steps - 1, 1)
            op = strength * (1 - t)
            y_top = edge * (_fh() / 2)
            y = y_top - edge * strip_h * (i + 0.5)
            group.add(Rectangle(width=_fw() + 0.2, height=strip_h + 0.02,
                                stroke_width=0, fill_color="#000000",
                                fill_opacity=op).move_to([0, y, 0]))
    return group


def _image_background():
    """Artwork backdrop, scaled to *cover* the frame (no letterboxing).

    Returns None when the file is missing so a bad path degrades to the flat
    theme color instead of killing the render.
    """
    rel = THEME.get("background_image")
    if not rel:
        return None
    path = _Path(rel)
    if not path.is_absolute():
        path = _Path(ASSET_ROOT) / rel
    if not path.exists():
        return None
    img = ImageMobject(str(path))
    # Cover: scale by the larger factor so neither axis is short, then center.
    sx = (_fw() + 0.05) / img.width
    sy = (_fh() + 0.05) / img.height
    img.scale(max(sx, sy))
    img.move_to(ORIGIN)
    return img


def build_background():
    style = THEME.get("background_style", "solid")
    base = THEME["background"]
    if style == "image":
        img = _image_background()
        if img is not None:
            # Group (not VGroup) — ImageMobject is not a VMobject.
            bg = Group(_full_rect(base), img)
            bg.set_z_index(-10)
            return bg
        style = "solid"  # fall through to the flat matte
    bg = VGroup(_full_rect(base))
    if style == "gradient" and THEME.get("gradient_to"):
        bg = VGroup(_gradient_background(base, THEME["gradient_to"]))
    elif style == "grid":
        bg.add(_grid_overlay(THEME.get("line", "#2A3350")))
    elif style == "dots":
        bg.add(_dot_overlay(THEME.get("line", "#2A3350")))
    elif style == "vignette":
        bg.add(_vignette_overlay())
    bg.set_z_index(-10)
    return bg


def build_chroma_zone():
    """Return the chroma zone for the configured region, or None.

    Flat green by default. With ``gradient`` on, the top ``gradient_frac`` of the
    zone fades from the theme background into green (the Manim screen "mixes"
    into the key), while the lower part stays pure flat green so there's still a
    cleanly keyable band.
    """
    if not CHROMA.get("enabled") or not CHROMA.get("zone"):
        return None
    zone = CHROMA["zone"]
    color = CHROMA["color"]
    zw, zh = norm_rect_size(zone)
    center = norm_rect_center(zone)
    top_y = center[1] + zh / 2
    bottom_y = center[1] - zh / 2

    if not CHROMA.get("gradient"):
        rect = Rectangle(width=zw, height=zh, stroke_width=0,
                         fill_color=color, fill_opacity=1.0)
        rect.move_to(center)
        rect.set_z_index(-5)
        return rect

    grp = VGroup()
    frac = float(CHROMA.get("gradient_frac", 0.35))
    solid_h = zh * (1.0 - frac)
    band_h = zh * frac

    # Solid, fully-keyable green at the bottom.
    if solid_h > 0.001:
        solid = Rectangle(width=zw, height=solid_h, stroke_width=0,
                          fill_color=color, fill_opacity=1.0)
        solid.move_to([center[0], bottom_y + solid_h / 2, 0.0])
        grp.add(solid)

    # Gradient band on top: theme background (at the seam) -> green (downward).
    steps = 80
    strip_h = band_h / steps
    a = ManimColor(THEME["background"])
    b = ManimColor(color)
    for i in range(steps):
        t = i / max(steps - 1, 1)  # 0 = bg at the top seam, 1 = green
        y = top_y - strip_h * (i + 0.5)
        grp.add(Rectangle(width=zw, height=strip_h + 0.03, stroke_width=0,
                          fill_color=interpolate_color(a, b, t),
                          fill_opacity=1.0).move_to([center[0], y, 0.0]))
    grp.set_z_index(-5)
    return grp


# --------------------------------------------------------------------------- #
# Avatar-aware layout + educational captions                                   #
# --------------------------------------------------------------------------- #
# Normalized (top-left origin) regions. Portrait reserves the bottom ~40% for a
# presenter avatar; the caption sits in the strip above the stage so it can
# never collide with the graphics.
if ORIENTATION == "portrait":
    CAPTION_Y = 0.075                          # caption pill center
    STAGE_RECT = (0.06, 0.150, 0.88, 0.430)    # default working area (upper 58%)
    WIDE_RECT = (0.04, 0.145, 0.92, 0.575)     # temporary expansion (to 72%)
    CAPTION_FONT_SIZE = 42
    CAPTION_MAX_W = 0.88      # max width of the PILL, as a fraction of the frame
else:
    CAPTION_Y = 0.095
    STAGE_RECT = (0.08, 0.190, 0.84, 0.560)
    WIDE_RECT = (0.05, 0.185, 0.90, 0.680)
    CAPTION_FONT_SIZE = 34
    CAPTION_MAX_W = 0.78

CAPTION_BG = "#0A1526"      # dark translucent plate
CAPTION_BG_OPACITY = 0.75
CAPTION_RADIUS = 0.34
CAPTION_PAD_X = 0.46
CAPTION_PAD_Y = 0.30

# --- narration captions ---------------------------------------------------- #
# The other mode: instead of a short heading, the pill carries the teacher's
# spoken line verbatim (Hinglish). Those wrap to several lines, so the pill is
# anchored by its TOP edge — the block grows downward and short lines don't
# bounce the layout — and the stage sits lower to make room.
if ORIENTATION == "portrait":
    NARRATION_STAGE_RECT = (0.06, 0.1941, 0.88, 0.3973)
    NARRATION_FONT_SIZE = 30
    NARRATION_MAX_W = 0.90       # pill width as a fraction of the frame
    NARRATION_TOP_MARGIN = 0.42  # gap from the top of frame, in Manim units
else:
    NARRATION_STAGE_RECT = (0.08, 0.250, 0.84, 0.500)
    NARRATION_FONT_SIZE = 26
    NARRATION_MAX_W = 0.80
    NARRATION_TOP_MARGIN = 0.36

NARRATION_MAX_LINES = 4
NARRATION_LINE_BUFF = 0.15


# How much frame the caption may occupy, and so the gap it leaves at each side.
# The approved stills span 4.6%..96.2%, so the house margin is ~4.6% a side;
# 0.90 keeps that with a little room, and a little is the point — a caption that
# runs to the bezel reads as an error even when every word is right.
CAPTION_MAX_W = 0.90


def wrap_measured(text: str, max_w: float, build) -> list[str]:
    """Greedy wrap that measures the candidate LINE, not the sum of its words.

    Summing word widths and adding a space width is the obvious approach and it
    is wrong twice over. A space has NO INK, so `Text(" ").width` is not the
    advance the renderer will use — Manim reports a bounding box and a blank
    string has none, which makes spaces look free and packs more words onto the
    line than fit. Kerning across a join then adds a little more. Both errors
    push the same way, so the line always comes out wider than the wrapper
    believed: PYQ captions were landing 4px from a 1080px frame edge against a
    limit that should have left 43.

    Measuring the assembled line has neither problem, because it is the same
    string the scene will draw. `build(line)` returns a mobject for it; results
    are cached by the caller's own cache if it has one.

    A single word wider than `max_w` is kept on its own line rather than broken:
    Devanagari splits inside a cluster orphan their combining marks. Callers
    should scale such a line down — `fit_caption` does.
    """
    lines: list[str] = []
    cur = ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if cur and build(trial).width > max_w:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


def fit_caption(group, max_w: float):
    """Last line of defence: nothing leaves the caption's side margins.

    `wrap_measured` already makes overflow impossible for text that CAN be
    wrapped, so reaching the scale here means one unbreakable token is wider
    than the whole margin. That is worth knowing about, hence the note.
    """
    if group.width > max_w:
        print(f"   caption over width by "
              f"{(group.width - max_w) / max_w * 100:.1f}% — scaling to fit")
        group.scale_to_fit_width(max_w)
    return group


def _greedy_wrap(text: str, per_line: int) -> list[str]:
    lines: list[str] = []
    cur = ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if len(trial) <= per_line or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def _wrap_for_width(text: str, size: int, max_w: float) -> list[str]:
    """Split ``text`` into centred lines that fit ``max_w``, capped at
    NARRATION_MAX_LINES. Character width is probed from the real font so this
    holds for any string, not just the ones we happened to test."""
    probe = Text("abcdefghijklmnopqrstuvwxyz", font=ui_font(),
                 weight="SEMIBOLD", font_size=size)
    char_w = probe.width / 26.0
    per_line = max(12, int(max_w / char_w))
    lines = _greedy_wrap(text, per_line)
    if len(lines) > NARRATION_MAX_LINES:
        per_line = len(text) // NARRATION_MAX_LINES + 4
        lines = _greedy_wrap(text, per_line)
    return lines


def narration_caption(text: str, font_size: int | None = None):
    """The spoken line, centred in a dark translucent plate pinned to the top.

    Same visual language as ``caption_pill`` (soft shadow, large radius, no
    stroke) — just sized for a sentence instead of a heading.
    """
    size = font_size or NARRATION_FONT_SIZE
    max_w = _fw() * NARRATION_MAX_W - 2 * CAPTION_PAD_X
    lines = _wrap_for_width(text, size, max_w)

    body = VGroup(*[
        Text(ln, font=ui_font(), weight="SEMIBOLD", color="#FFFFFF",
             font_size=size)
        for ln in lines
    ])
    body.arrange(DOWN, buff=NARRATION_LINE_BUFF)
    if body.width > max_w:
        body.scale_to_fit_width(max_w)

    w = body.width + 2 * CAPTION_PAD_X
    h = body.height + 2 * CAPTION_PAD_Y
    radius = min(CAPTION_RADIUS, h / 2 - 0.02)

    shadow = VGroup()
    for grow, drop, op in ((0.05, 0.06, 0.10), (0.11, 0.11, 0.07), (0.19, 0.17, 0.05)):
        shadow.add(RoundedRectangle(
            width=w + grow, height=h + grow, corner_radius=radius + grow / 2,
            stroke_width=0, fill_color="#000000", fill_opacity=op,
        ).shift(DOWN * drop))
    plate = RoundedRectangle(
        width=w, height=h, corner_radius=radius, stroke_width=0,
        fill_color=CAPTION_BG, fill_opacity=CAPTION_BG_OPACITY,
    )
    pill = VGroup(shadow, plate, body)
    # Top-anchored: the block grows downward, so the stage below never moves.
    pill.move_to([0.0, _fh() / 2 - NARRATION_TOP_MARGIN - h / 2, 0.0])
    pill.set_z_index(20)
    return pill


def caption_pill(text: str, font_size: int | None = None):
    """An educational caption: white SemiBold text on a dark translucent
    rounded plate with generous padding and a soft shadow. Pinned top-center.

    Manim has no blur, so the shadow is three stacked plates at low opacity —
    reads as a soft drop shadow at 1080p without any hard edge.
    """
    label = Text(
        text,
        font=ui_font(),
        weight="SEMIBOLD",
        color="#FFFFFF",
        font_size=font_size or CAPTION_FONT_SIZE,
    )
    # Budget the PILL, not the text, so the plate always keeps a side margin.
    max_w = _fw() * CAPTION_MAX_W - 2 * CAPTION_PAD_X
    if label.width > max_w:
        label.scale_to_fit_width(max_w)

    w = label.width + 2 * CAPTION_PAD_X
    h = label.height + 2 * CAPTION_PAD_Y
    radius = min(CAPTION_RADIUS, h / 2 - 0.02)

    shadow = VGroup()
    for grow, drop, op in ((0.05, 0.06, 0.10), (0.11, 0.11, 0.07), (0.19, 0.17, 0.05)):
        shadow.add(
            RoundedRectangle(
                width=w + grow, height=h + grow, corner_radius=radius + grow / 2,
                stroke_width=0, fill_color="#000000", fill_opacity=op,
            ).shift(DOWN * drop)
        )
    plate = RoundedRectangle(
        width=w, height=h, corner_radius=radius,
        stroke_width=0, fill_color=CAPTION_BG, fill_opacity=CAPTION_BG_OPACITY,
    )
    pill = VGroup(shadow, plate, label)
    pill.move_to(norm_point(0.5, CAPTION_Y))
    pill.set_z_index(20)
    return pill


# --------------------------------------------------------------------------- #
# Base scene                                                                   #
# --------------------------------------------------------------------------- #

# --------------------------------------------------------------------------- #
# Layout guard                                                                 #
# --------------------------------------------------------------------------- #
# Two classes of bug kept reaching finished videos, and both are mechanical, so
# both are checked mechanically here rather than by watching the render:
#
#   1. Content overlapping other content — a rusted bar drawn on top of a word
#      equation, a label sitting across a diagram. `place()` fits one block
#      inside the stage band, but nothing stopped two blocks occupying the same
#      space, and a label attached with `next_to` after placement escapes the
#      band entirely.
#
#   2. Animating along STORED COORDINATES. Electrons in the Daniell cell flew
#      straight through the air between the beakers instead of following the
#      wire, because the path had been captured as a list of points at
#      construction time and `place()` then moved and scaled the cell out from
#      under it. `along()` exists so a path is always taken from the drawn
#      mobject, which moves with its group.

def along(mobject):
    """A path for MoveAlongPath, taken from the mobject actually on screen.

    Always use this instead of rebuilding a path from remembered points. A
    stored point list does not follow its group through `place()`, `scale()` or
    `move_to()`, and the animation then runs somewhere the viewer can see is
    wrong.
    """
    path = mobject.copy()
    path.set_stroke(width=0, opacity=0)
    path.set_fill(opacity=0)
    return path


def mark_group(mob, tag=None):
    """Tag every part of a composite so the guard treats them as one thing.

    A diagram is often revealed piece by piece — `FadeIn(cell.left.glass)`, then
    the rods, then the bridge — which puts the PARTS in the scene as top-level
    mobjects with no family relationship between them. They overlap each other
    by design, and without this they read as violations.
    """
    tag = tag if tag is not None else id(mob)
    mob._layout_group = tag
    for sub in mob.get_family():
        sub._layout_group = tag
    return mob


def _hides_things(m) -> bool:
    """Can this mobject actually occlude what is behind it?

    A stroke-only shape cannot: a SurroundingRectangle enclosing an equation, a
    beaker outline around its label, a wire crossing a caption. Only something
    with fill, or text, hides anything — so only those are worth reporting.
    """
    from manim import ImageMobject
    if isinstance(m, ImageMobject):
        return True
    fam = m.get_family()
    for s in fam:
        try:
            if float(s.get_fill_opacity()) > 0.25:
                return True
        except Exception:
            continue
    # Text and MathTex render as filled glyphs, but report fill through a
    # different path in some manim versions
    return type(m).__name__ in {"Text", "MathTex", "Tex", "MarkupText", "DecimalNumber"}


def _leaf_boxes(m, limit=64):
    """Bounding boxes of the leaves, not of the whole group.

    A sparse diagram has a huge bounding box that a nearby label sits inside
    without touching any of it. Comparing leaf to leaf is what distinguishes a
    label placed beside a beaker from a label printed across one.
    """
    fam = [s for s in m.get_family() if len(s.submobjects) == 0]
    if not fam or len(fam) > limit:
        b = _bbox(m)
        return [b] if b else []
    out = []
    for s in fam:
        b = _bbox(s)
        if b:
            out.append(b)
    return out


def _bbox(m):
    try:
        c = m.get_center()
        w, h = m.width, m.height
    except Exception:
        return None
    if not (np.isfinite(w) and np.isfinite(h)) or w <= 0 or h <= 0:
        return None
    return (c[0] - w / 2, c[1] - h / 2, c[0] + w / 2, c[1] + h / 2)


def _overlap_frac(a, b):
    """Intersection area as a fraction of the SMALLER box."""
    ix = min(a[2], b[2]) - max(a[0], b[0])
    iy = min(a[3], b[3]) - max(a[1], b[1])
    if ix <= 0 or iy <= 0:
        return 0.0
    inter = ix * iy
    sa = (a[2] - a[0]) * (a[3] - a[1])
    sb = (b[2] - b[0]) * (b[3] - b[1])
    return inter / max(min(sa, sb), 1e-9)


class ThemedScene(Scene):
    """Base class: paints the themed background + chroma zone and exposes a
    safe content area plus color/typeset helpers. Subclasses implement
    ``construct`` and should keep drawn content inside ``self.safe_*``.
    """


    # --- layout guard ---------------------------------------------------- #
    # Set by a scene that reserves bands: (top, bottom) as fractions of the
    # frame height from the top. Content outside this is reported.
    STAGE_BAND: tuple[float, float] | None = None
    OVERLAP_TOL = 0.22        # ignore touching; flag real occlusion
    AUDIT_LAYOUT = True

    def _stage_mobjects(self):
        """Top-level content — not the background, chroma zone or caption."""
        skip = {id(getattr(self, "background", None)),
                id(getattr(self, "chroma_zone", None)),
                id(getattr(self, "caption_mob", None))}
        return [m for m in self.mobjects if id(m) not in skip]

    def audit_layout(self, label=""):
        """Report content that overlaps other content or leaves its band.

        Called automatically after every animation. It records rather than
        raises: one frame of a transition legitimately has two things crossing,
        and failing the render there would be worse than the bug. The report is
        printed at the end, where it is impossible to miss.
        """
        if not self.AUDIT_LAYOUT:
            return
        band_top = norm_point(0.5, self.STAGE_BAND[0])[1] if self.STAGE_BAND else None
        band_bot = norm_point(0.5, self.STAGE_BAND[1])[1] if self.STAGE_BAND else None

        items = []
        for m in self._stage_mobjects():
            b = _bbox(m)
            if b is None:
                continue
            # anything living entirely above the stage is a caption, including
            # the outgoing one that is still on screen mid-swap
            if band_top is not None and b[1] > band_top:
                continue
            items.append((m, b, _leaf_boxes(m)))

        for i in range(len(items)):
            mi, bi, li = items[i]
            for j in range(i + 1, len(items)):
                mj, bj, lj = items[j]
                if mj in mi.get_family() or mi in mj.get_family():
                    continue
                # parts of one diagram, revealed separately
                gi = getattr(mi, "_layout_group", None)
                if gi is not None and gi == getattr(mj, "_layout_group", None):
                    continue
                if _overlap_frac(bi, bj) <= 0.01:
                    continue                      # boxes do not even touch
                # an outline cannot hide anything it encloses
                if not (_hides_things(mi) and _hides_things(mj)):
                    continue
                f = max((_overlap_frac(a, b) for a in li for b in lj), default=0.0)
                if f > self.OVERLAP_TOL:
                    self._layout_violations.append(
                        f"t={self.time:6.2f}s {label} OVERLAP {f:.0%} between "
                        f"{type(mi).__name__} and {type(mj).__name__}")

        if band_top is not None:
            for m, b, _ in items:
                if b[3] > band_top + 0.05 or b[1] < band_bot - 0.05:
                    self._layout_violations.append(
                        f"t={self.time:6.2f}s {label} OUTSIDE BAND "
                        f"{type(m).__name__} spans y {b[1]:.2f}..{b[3]:.2f}, "
                        f"band is {band_bot:.2f}..{band_top:.2f}")

    def play(self, *args, **kwargs):
        super().play(*args, **kwargs)
        if not getattr(self, "audit_enabled", True):
            return                          # e.g. while the question card is up
        try:
            self.audit_layout()
        except Exception as exc:            # a guard must never break a render
            self._layout_violations.append(f"audit failed: {exc}")


    # ---------------------------------------------------------------- beats --
    # A small set of vetted blocks that every PYQ scene is built from. They
    # exist so nine parts can be authored as DATA rather than as nine hand-laid
    # scenes: each one returns a mobject that has already been through
    # `place()`, so it cannot cross the caption above it or the presenter below,
    # and the whole batch inherits one set of layout decisions instead of nine.
    #
    # `hi` colours the load-bearing word in a line — "make sure important
    # equations don't get missed" means the equation has to be the thing the eye
    # lands on, not one more grey line among several.

    def beat_points(self, items, title=None, size=34, hi=None, colour=None):
        """A short list. Anything longer than five lines is split by the caller;
        six lines at a readable size do not fit the stage band and shrinking
        them to fit is how a slide becomes unreadable on a phone."""
        rows = VGroup()
        if title:
            rows.add(Text(str(title), font=ui_font(), font_size=size + 6,
                          color=colour or "#FFC15C", weight="BOLD"))
        for it in items[:5]:
            t2c = {hi: "#FFC15C"} if hi and hi in str(it) else {}
            rows.add(Text(str(it), font=ui_font(), font_size=size,
                          color="#FFFFFF", weight="MEDIUM", t2c=t2c))
        rows.arrange(DOWN, buff=0.34, aligned_edge=LEFT)
        return self.place(rows)

    def beat_formula(self, tex, label=None, size=1.15, colour="#FFFFFF"):
        """One or more equations, large, boxed if labelled.

        Equations are the part of an answer a student copies verbatim, so they
        are given the whole stage and the largest type any block uses.
        """
        items = [tex] if isinstance(tex, str) else list(tex)

        # Break a long equation at its ARROW rather than letting place() shrink
        # it. A full chemical equation is wider than the stage, and scaling it to
        # fit made the KMnO4 line small enough that the thing a student is meant
        # to copy was the least readable mark on screen. Splitting at the arrow
        # is how it would be written on a board anyway.
        lines = []
        for t in items:
            if len(t) > 44 and r"\rightarrow" in t:
                lhs, rhs = t.split(r"\rightarrow", 1)
                lines.append(lhs.strip())
                lines.append(r"\rightarrow " + rhs.strip())
            else:
                lines.append(t)

        eqs = VGroup(*[MathTex(t).scale(size).set_color(colour) for t in lines])
        eqs.arrange(DOWN, buff=0.34, aligned_edge=LEFT)
        if label:
            cap = Text(str(label), font=ui_font(), font_size=30,
                       color="#7CE0B0", weight="BOLD")
            eqs = VGroup(cap, eqs).arrange(DOWN, buff=0.40)
        return self.place(eqs)

    def beat_flow(self, items, size=30):
        """a -> b -> c, wrapped to two rows if it will not fit one."""
        chain = VGroup()
        for i, it in enumerate(items):
            if i:
                chain.add(Text("→", font=ui_font(), font_size=size + 4,
                               color="#B9C6DC"))
            chain.add(Text(str(it), font=ui_font(), font_size=size,
                           color="#FFFFFF", weight="MEDIUM"))
        chain.arrange(RIGHT, buff=0.26)
        _, w, _ = self.stage_box()
        if chain.width > w:                     # wrap rather than shrink to fit
            half = len(chain) // 2 // 2 * 2
            chain = VGroup(VGroup(*chain[:half]).arrange(RIGHT, buff=0.26),
                           VGroup(*chain[half:]).arrange(RIGHT, buff=0.26)
                           ).arrange(DOWN, buff=0.34)
        return self.place(chain)

    def beat_compare(self, left, right, size=28):
        """Two labelled columns — the shape most 'compare these' answers want.

        A divider is drawn BETWEEN the columns rather than the columns being
        spaced apart and hoped over: with a rule there, a long line on one side
        reads as belonging to that side even when it runs close to the middle.
        """
        def col(spec):
            g = VGroup(Text(str(spec[0]), font=ui_font(), font_size=size + 5,
                            color="#FFC15C", weight="BOLD"))
            for line in spec[1][:4]:
                g.add(Text(str(line), font=ui_font(), font_size=size,
                           color="#FFFFFF", weight="MEDIUM"))
            return g.arrange(DOWN, buff=0.26, aligned_edge=LEFT)

        l, r = col(left), col(right)
        bar = Line(UP, DOWN).set_stroke("#2A3C57", 3)
        bar.set_height(max(l.height, r.height) * 1.06)
        return self.place(VGroup(l, bar, r).arrange(RIGHT, buff=0.55))

    def beat_image(self, path, caption=None, height=None):
        """A generated illustration. ImageMobject is NOT a VMobject, so it can
        never go in a VGroup — see CLAUDE.md."""
        img = ImageMobject(str(path))
        _, w, h = self.stage_box()
        img.height = min(height or h * 0.80, h * 0.86)
        if img.width > w * 0.92:
            img.width = w * 0.92
        grp = Group(img)
        if caption:
            cap = Text(str(caption), font=ui_font(), font_size=26,
                       color="#B9C6DC", weight="MEDIUM")
            cap.next_to(img, DOWN, buff=0.24)
            grp = Group(img, cap)
        return self.place(grp)

    def question_card(self, question, highlight="", years="", sheet=None,
                      sheet_head="प्रश्न"):
        """The approved opening card: ringed ?, gold प्रश्न, notepaper, years.

        Geometry lives in src/question_card.py, measured off the approved still.
        The text wraps and shrinks to the paper's writable area and asserts
        containment, so a long question cannot leak off the paper.
        """
        from src.question_card import (CREAM, DECOR_TILT, GOLD, HEAD_TEXT,
                                       HEAD_W_MAX, PAPER,
                                       PAPER_HILITE, PAPER_INK, PAPER_TILT,
                                       PAPER_W, PAPER_Y, Q_MARK_R, Q_MARK_Y,
                                       Q_WORD_SIZE, Q_WORD_Y, RULE_W, RULE_W_MAX,
                                       SHEET_W, SHEET_Y, SHEET_YEARS_Y,
                                       RULE_Y, TEAL, TICK_PAD, YEARS_Y,
                                       fit_lines, fits, writable_box)
        fw, fh = config.frame_width, config.frame_height
        F = "Khand"
        cache = {}

        def txt(s, size, colour=CREAM):
            return Text(s, font=F, font_size=size, color=colour, weight="BOLD")

        def wid(word, size):
            k = (word, size)
            if k not in cache:
                cache[k] = Text(word, font=F, font_size=size, weight="BOLD").width
            return cache[k]

        def ticks(around, colour, n, pad):
            g = VGroup()
            hw, hh = around.width / 2 + pad, around.height / 2 + pad * 0.55
            spots = [(-hw, hh * .55), (-hw * .96, -hh * .15), (-hw * .80, hh * .95),
                     (hw, hh * .55), (hw * .96, -hh * .15), (hw * .80, hh * .95)]
            for i, (x, y) in enumerate(spots[:n]):
                L, w0, w1 = 0.24, 0.020, 0.062
                tk = Polygon([0, -w0, 0], [L, -w1, 0], [L, w1, 0], [0, w0, 0])
                tk.set_fill(colour, 1).set_stroke(width=0)
                out = -1 if x < 0 else 1
                tk.rotate(PI if out < 0 else 0).rotate(out * (0.30 + 0.32 * (i % 3)))
                tk.move_to(around.get_center() + np.array([x, y, 0]))
                g.add(tk)
            return g

        def scribble(width, colour, wobble=0.035, n=26):
            pts = []
            for i in range(n):
                u = i / (n - 1)
                y = (np.sin(u * 5.2) * .3 + np.sin(u * 11.0 + 1.1) * .18) * wobble
                y += (u - .5) ** 2 * -wobble * 1.4
                pts.append(np.array([(u - .5) * width, y, 0]))
            s = VMobject().set_points_smoothly(pts).set_stroke(colour, 7, opacity=.95)
            s2 = s.copy().shift(DOWN * wobble * .9).set_stroke(colour, 4, opacity=.55)
            return VGroup(s, s2)

        ring = Circle(radius=fh * Q_MARK_R).set_stroke(TEAL, 5).set_fill(opacity=0)
        qm = txt("?", int(fh * Q_MARK_R * 105), TEAL).move_to(ring.get_center())
        head = VGroup(ring, qm).move_to(norm_point(0.5, Q_MARK_Y))
        # Back to "प्रश्न". It was "MP Board - 12th" while the sheet below was
        # plain notepaper and named nothing; the exam-paper sheet prints the
        # board, class, year and subject itself, so repeating them here says the
        # same thing twice. Still scaled to a share of the frame rather than set
        # at a fixed point size — the sparks and the rule are sized FROM the
        # word, so a longer heading pushes all three past the frame edge.
        word = txt(sheet_head or HEAD_TEXT, Q_WORD_SIZE, GOLD)
        if word.width > fw * HEAD_W_MAX:
            word.scale(fw * HEAD_W_MAX / word.width)
        word.move_to(norm_point(0.5, Q_WORD_Y))
        # Sparks clear the text by a share of ITS width, not a fixed pad: a
        # fixed 0.30 sat right against a heading this wide, and two of the six
        # spots are placed at 80% of the half-width, which falls INSIDE a wide
        # word where it fell outside a short one.
        sp = ticks(word, GOLD, 6, max(TICK_PAD, word.width * 0.11))
        rule = scribble(min(word.width * RULE_W, fw * RULE_W_MAX),
                        CREAM, wobble=0.018)
        rule.rotate(DECOR_TILT).move_to(norm_point(0.5, RULE_Y))

        # `sheet` is a torn corner of the real exam paper with the question
        # already PRINTED on it (tools/paper_header.py). When one is given the
        # card places it as-is and draws nothing on top — the question, the
        # board line and the subject are all part of that photograph. Without
        # one the card falls back to the lined notepaper and typesets the
        # question onto it, which is what every earlier video used.
        # The card deliberately fills the FRAME, not the stage band, so every
        # animation in it trips the layout guard: 29-60 "OUTSIDE BAND" reports
        # per scene, which made preflight fail on every project and turned the
        # guard into noise. It is off while the card is up and on for everything
        # that follows, which is what it was written to police.
        self.audit_enabled = False
        paper = ImageMobject(str(sheet) if sheet else PAPER)
        paper.width = fw * (SHEET_W if sheet else PAPER_W)
        paper.move_to(norm_point(0.5, SHEET_Y if sheet else PAPER_Y))
        if sheet:
            self.play(FadeIn(head, scale=1.15), run_time=0.5)
            self.play(FadeIn(word, shift=UP * .14), run_time=0.45)
            self.play(LaggedStart(*[GrowFromCenter(t) for t in sp],
                                  lag_ratio=.08), run_time=0.5)
            self.play(Create(rule), run_time=0.4)
            self.play(FadeIn(paper, shift=DOWN * .30, scale=1.04), run_time=0.8)
            yr = VGroup(txt("वर्ष ", 36), txt(years, 42, TEAL),
                        txt(" में", 36)).arrange(RIGHT, buff=0.10)
            ytxt = VGroup(yr, txt("ये प्रश्न था", 36)).arrange(DOWN, buff=0.12)
            pill = RoundedRectangle(width=ytxt.width + .85,
                                    height=ytxt.height + .48,
                                    corner_radius=.30
                                    ).set_stroke(GOLD, 4).set_fill(opacity=0)
            pills = VGroup(pill, ytxt)
            pills.rotate(DECOR_TILT).move_to(norm_point(0.5, SHEET_YEARS_Y))
            psp = ticks(pill, GOLD, 4, 0.22)
            self.play(FadeIn(pills, shift=UP * .12),
                      LaggedStart(*[GrowFromCenter(t) for t in psp],
                                  lag_ratio=.08), run_time=0.6)
            # Nothing is registered anywhere: the original branch does not
            # either. The scene's own cue() clears the screen at the next cue,
            # which is how the card leaves.
            self.audit_enabled = True
            return

        (cx, cy), bw, bh = writable_box(paper)
        lh = {}

        def line_h(s):
            if s not in lh:
                lh[s] = Text("नियम", font=F, font_size=s, weight="BOLD").height + 0.16
            return lh[s]

        size, lines = fit_lines(question, wid, bw, bh, line_h,
                                lambda s: wid(" ", s))
        rows = VGroup()
        for words in lines:
            line = " ".join(words)
            t2c = {highlight: PAPER_HILITE} if highlight and highlight in line else {}
            rows.add(Text(line, font=F, font_size=size, color=PAPER_INK,
                          weight="BOLD", t2c=t2c))
        rows.arrange(DOWN, buff=0.16, aligned_edge=LEFT)
        if rows.width > bw:
            rows.scale(bw / rows.width)
        # Rotate FIRST, then fit. A block rotated by θ has a bounding box of
        # w·cosθ + h·sinθ by w·sinθ + h·cosθ — at 5.75° that is 5% wider and
        # nearly 20% taller than the block that was wrapped. Fitting before the
        # rotation therefore measures the wrong rectangle, and the containment
        # assert below rejected a question that does fit the paper.
        rows.rotate(PAPER_TILT)
        shrink = min(bw / rows.width, bh / rows.height, 1.0)
        if shrink < 1.0:
            rows.scale(shrink)
        rows.move_to([cx, cy, 0])
        if not fits(rows, paper):
            raise ValueError(f"question does not fit the paper at size {size}")
        swoosh = scribble(rows.width * .62, PAPER_INK, wobble=.045)
        swoosh.rotate(PAPER_TILT).next_to(rows, DOWN, buff=0.20)

        yr = VGroup(txt("वर्ष ", 36), txt(years, 42, TEAL),
                    txt(" में", 36)).arrange(RIGHT, buff=0.10)
        ytxt = VGroup(yr, txt("ये प्रश्न था", 36)).arrange(DOWN, buff=0.12)
        pill = RoundedRectangle(width=ytxt.width + .85, height=ytxt.height + .48,
                                corner_radius=.30).set_stroke(GOLD, 4).set_fill(opacity=0)
        pills = VGroup(pill, ytxt)
        pills.rotate(DECOR_TILT).move_to(norm_point(0.5, YEARS_Y))
        psp = ticks(pill, GOLD, 4, 0.22)

        self.play(FadeIn(head, scale=1.15), run_time=0.5)
        self.play(FadeIn(word, shift=UP * .14), run_time=0.45)
        self.play(LaggedStart(*[GrowFromCenter(s) for s in sp], lag_ratio=.08),
                  Create(rule), run_time=0.55)
        self.play(FadeIn(paper, shift=DOWN * .30, scale=1.04), run_time=0.7)
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * .14) for r in rows],
                              lag_ratio=.20), run_time=0.9)
        self.play(Create(swoosh), run_time=0.45)
        self.play(FadeIn(pills, shift=UP * .12),
                  LaggedStart(*[GrowFromCenter(s) for s in psp], lag_ratio=.08),
                  run_time=0.6)

    def label_pointer(self, target, label, colour, sub=(), side=-1,
                      band_y=None, size=34, sub_size=21):
        """A colour-coded label joined to a diagram part by a dashed curve.

        The reference style: the term in its own colour, one or two smaller
        white lines under it, and a dashed arc rising to what it names with an
        arrowhead at the top.

        Labels are PINNED TO A BAND rather than hung off the target with
        `next_to`. Hung off the target they land wherever the diagram happens to
        end — which put them under the presenter once, and across the beaker
        another time. A fixed band means the left and right labels always share
        a baseline and the arc absorbs the difference.

        `band_y` defaults to just below the stage, so a caller that has not
        thought about it still gets a label clear of the diagram.
        """
        F = getattr(self, "LABEL_FONT", "Khand")
        lab = Text(label, font=F, font_size=size, color=colour, weight="BOLD")
        parts = [lab]
        if sub:
            subs = VGroup(*[Text(s, font=F, font_size=sub_size, color="#FFFFFF",
                                 weight="BOLD") for s in sub])
            subs.arrange(DOWN, buff=0.08)
            parts.append(subs)
        block = VGroup(*parts).arrange(DOWN, buff=0.16)

        if band_y is None:
            band_y = getattr(self, "STAGE_BAND", (0.29, 0.60))[1] - 0.045
        block.move_to([target.get_x() + side * 0.62, norm_point(0.5, band_y)[1], 0])

        arc = DashedVMobject(
            ArcBetweenPoints(block.get_top() + UP * 0.06,
                             target.get_bottom() + DOWN * 0.04,
                             angle=side * 0.5), num_dashes=9)
        arc.set_stroke(colour, 3, opacity=0.85)
        tip = Triangle(fill_opacity=1, color=colour).scale(0.072)
        tip.rotate(PI).move_to(target.get_bottom() + DOWN * 0.04)
        g = VGroup(block, arc, tip)
        g.block, g.arc = block, arc
        return g

    def spread_labels(self, *groups, gap=0.28):
        """Push labels apart until none of them touch.

        Two labels under one diagram will collide the moment either term is
        long — "यहाँ ऑक्सीकरण होता है" under one electrode and "यहाँ अपचयन होता
        है" under the other ran into each other and neither could be read. This
        walks them outward until they clear, then re-aims their arcs.
        """
        if len(groups) < 2:
            return VGroup(*groups)
        blocks = sorted(groups, key=lambda g: g.block.get_x())
        for i in range(1, len(blocks)):
            a, b = blocks[i - 1].block, blocks[i].block
            overlap = (a.get_right()[0] + gap) - b.get_left()[0]
            if overlap > 0:
                blocks[i - 1].shift(LEFT * overlap / 2)
                blocks[i].shift(RIGHT * overlap / 2)
        return VGroup(*groups)

    def end_card(self, image, hold=5.0, fade_in=0.6, fade_out=0.8):
        """Close on the hand-written answer photo, then fade to black.

        Only ever on the LAST part of a question — the earlier parts hand off to
        the next one instead. The image comes from the EndScreenshot package
        (`video endscreenshot`), which draws the Q&A card.

        This runs PAST the presenter's audio: the clip has finished talking by
        here, so the composite lets the background continue after the avatar
        ends (overlay `eof_action=pass`) and the tail is silent.

        The black is a real mobject rather than a camera fade, so it composites
        over the presenter too — otherwise he keeps talking on top of a black
        screen.
        """
        from pathlib import Path as _P
        img = ImageMobject(str(_P(ASSET_ROOT) / image) if not _P(image).is_absolute()
                           else str(image))
        # fit the frame, leaving a hair of margin
        img.height = config.frame_height * 0.96
        if img.width > config.frame_width * 0.96:
            img.width = config.frame_width * 0.96
        img.move_to(ORIGIN).set_z_index(50)

        black = Rectangle(width=config.frame_width * 1.02,
                          height=config.frame_height * 1.02)
        black.set_fill("#000000", 1).set_stroke(width=0).set_z_index(60)

        self.play(FadeIn(img), run_time=fade_in)
        self.wait(hold)
        self.play(FadeIn(black), run_time=fade_out)
        self.wait(0.3)

    def report_layout(self) -> None:
        """Print what the guard caught. Run at tear-down, where it cannot be
        missed by whoever kicked off the render."""
        v = getattr(self, "_layout_violations", [])
        if not v:
            return
        seen, uniq = set(), []
        for line in v:
            k = line.split(" ", 1)[1]
            if k not in seen:
                seen.add(k); uniq.append(line)
        print("\n" + "=" * 70)
        print(f"LAYOUT GUARD: {len(uniq)} distinct problem(s) in this scene")
        for line in uniq[:40]:
            print("  " + line)
        print("=" * 70 + "\n")

        # Printing is not enough. A Manim render prints thousands of lines and
        # this block scrolls past; labels sitting on the beaker walls were
        # reported here and still reached a finished video. Write it beside the
        # scene as well, where preflight reads it and FAILS the next render.
        try:
            import json as _json
            from pathlib import Path as _P
            out = _P(__file__).resolve().parent / "layout_violations.json"
            out.write_text(_json.dumps(
                {"scene": type(self).__name__, "problems": uniq[:60]},
                ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            pass                    # a guard must never break a render

    # PREVIEW collapses the waits that conform the scene to the audio clock.
    # A 113-second part spends almost all of its render sitting still; the
    # animations are a small fraction of it. With the waits clamped the same
    # scene draws every beat in a fraction of the time, which is what makes a
    # storyboard cheap enough to look at BEFORE committing to a real render.
    PREVIEW = bool(_os.getenv("PREVIEW"))
    PREVIEW_WAIT = 0.10

    def wait(self, duration=1.0, *args, **kwargs):
        if self.PREVIEW:
            duration = min(duration, self.PREVIEW_WAIT)
        return super().wait(duration, *args, **kwargs)

    def setup(self) -> None:
        super().setup()
        register_fonts()
        self.theme = THEME
        self.camera.background_color = THEME["background"]
        self._cues: list[dict] = []   # sound cues emitted by this scene

        self.background = build_background()
        self.add(self.background)

        # Chroma zone + safe area
        safe = CHROMA.get("safe", (0.0, 0.0, 1.0, 1.0))
        self.safe_rect = safe
        self.safe_center = norm_rect_center(safe)
        self.safe_width, self.safe_height = norm_rect_size(safe)

        self.chroma_zone = build_chroma_zone()
        if self.chroma_zone is not None and not CHROMA.get("animate_in"):
            self.add(self.chroma_zone)

        self._layout_violations: list[str] = []

        # Upper-half content region (reels layout: graphics + labels up top).
        self.upper_w = _fw()
        self.upper_h = _fh() * 0.5
        self.upper_center = np.array([0.0, _fh() * 0.25, 0.0])

        # --- Avatar-aware layout ------------------------------------------- #
        # STAGE is the default working area: the band between the caption and
        # the presenter, i.e. roughly the upper 58% of the frame. WIDE is the
        # temporary expansion for beats that genuinely need vertical room
        # (diffraction spread, comparison table); it still stops well clear of
        # the avatar so the presenter is never covered.
        #
        # A scene sets CAPTION_MODE = "narration" to carry the spoken line
        # verbatim instead of a short heading; the stage drops to make room.
        self.caption_mode = getattr(self, "CAPTION_MODE", "heading")
        stage = (NARRATION_STAGE_RECT if self.caption_mode == "narration"
                 else STAGE_RECT)
        self.stage_rect = stage
        self.wide_rect = WIDE_RECT
        self.stage_center = norm_rect_center(stage)
        self.stage_w, self.stage_h = norm_rect_size(stage)
        self.wide_center = norm_rect_center(WIDE_RECT)
        self.wide_w, self.wide_h = norm_rect_size(WIDE_RECT)
        self.caption_point = norm_point(0.5, CAPTION_Y)
        self.caption_mob = None

    def top_caption(self, mob, buff: float = 0.7):
        """Pin a caption to the top edge (fully on-screen)."""
        mob.to_edge(UP, buff=buff)
        return mob

    # --- educational caption pill ------------------------------------------ #
    def make_caption(self, text: str):
        """Build (but don't add) the top-center caption pill."""
        if getattr(self, "caption_mode", "heading") == "narration":
            return narration_caption(text)
        return caption_pill(text)

    def show_caption(self, text: str, run_time: float = 0.55):
        """Fade+slide the caption in, cross-fading out any previous one.

        In "heading" mode these are short educational headings; in "narration"
        mode the pill carries the teacher's spoken line verbatim.
        """
        new = self.make_caption(text)
        old = self.caption_mob
        if old is None:
            self.play(FadeIn(new, shift=UP * 0.35), run_time=run_time)
        else:
            self.play(
                FadeOut(old, shift=UP * 0.25),
                FadeIn(new, shift=UP * 0.35),
                run_time=run_time,
            )
        self.caption_mob = new
        return new

    def clear_caption(self, run_time: float = 0.4):
        if self.caption_mob is not None:
            self.play(FadeOut(self.caption_mob, shift=UP * 0.2), run_time=run_time)
            self.caption_mob = None

    # --- stage helpers ------------------------------------------------------ #
    def fit_stage(self, mob, pad: float = 0.94, wide: bool = False):
        """Scale+center a mobject into the working area (stage, or wide)."""
        w, h = (self.wide_w, self.wide_h) if wide else (self.stage_w, self.stage_h)
        center = self.wide_center if wide else self.stage_center
        max_w, max_h = w * pad, h * pad
        if mob.width > max_w:
            mob.scale_to_fit_width(max_w)
        if mob.height > max_h:
            mob.scale_to_fit_height(max_h)
        mob.move_to(center)
        return mob

    def stage_top(self, wide: bool = False) -> np.ndarray:
        c = self.wide_center if wide else self.stage_center
        h = self.wide_h if wide else self.stage_h
        return c + np.array([0.0, h / 2, 0.0])

    def stage_bottom(self, wide: bool = False) -> np.ndarray:
        c = self.wide_center if wide else self.stage_center
        h = self.wide_h if wide else self.stage_h
        return c + np.array([0.0, -h / 2, 0.0])

    def stage_left(self, wide: bool = False) -> np.ndarray:
        c = self.wide_center if wide else self.stage_center
        w = self.wide_w if wide else self.stage_w
        return c + np.array([-w / 2, 0.0, 0.0])

    def stage_right(self, wide: bool = False) -> np.ndarray:
        c = self.wide_center if wide else self.stage_center
        w = self.wide_w if wide else self.stage_w
        return c + np.array([w / 2, 0.0, 0.0])

    def half_center(self, side: str, wide: bool = False) -> np.ndarray:
        """Center of the left/right column in the comparison layout."""
        c = self.wide_center if wide else self.stage_center
        w = self.wide_w if wide else self.stage_w
        dx = w / 4 * (-1 if side == "left" else 1)
        return c + np.array([dx, 0.0, 0.0])

    # --- color/typeset helpers -------------------------------------------- #
    def eq(self, latex: str, color: str | None = None, scale: float = 1.0):
        m = MathTex(latex, color=color or THEME["primary"])
        if scale != 1.0:
            m.scale(scale)
        return m

    def caption(self, text: str, color: str | None = None, scale: float = 0.7):
        return Text(text, color=color or THEME["secondary"]).scale(scale)

    def heading(self, text: str, color: str | None = None):
        return Text(text, color=color or THEME["primary"], weight=BOLD).scale(0.9)

    def underline(self, mob, color: str | None = None, buff: float = 0.12):
        return Underline(mob, color=color or THEME["accent"], buff=buff)

    # --- layout helpers ---------------------------------------------------- #
    def fit_safe(self, mob, pad: float = 0.9):
        """Scale ``mob`` to fit inside the safe area (with padding) and center
        it there. Returns the mobject."""
        max_w = self.safe_width * pad
        max_h = self.safe_height * pad
        if mob.width > max_w:
            mob.scale_to_fit_width(max_w)
        if mob.height > max_h:
            mob.scale_to_fit_height(max_h)
        mob.move_to(self.safe_center)
        return mob

    def label(self, text: str, color: str | None = None, scale: float = 0.62,
              width: float | None = None):
        """A clean English on-screen caption. Wraps to fit the frame width."""
        t = Text(text, color=color or THEME["secondary"], line_spacing=1.0).scale(scale)
        max_w = (width if width is not None else _fw()) * 0.92
        if t.width > max_w:
            t.scale_to_fit_width(max_w)
        return t

    def fit_upper(self, mob, pad: float = 0.86):
        """Scale + center a mobject into the upper half of the frame."""
        max_w = self.upper_w * pad
        max_h = self.upper_h * pad
        if mob.width > max_w:
            mob.scale_to_fit_width(max_w)
        if mob.height > max_h:
            mob.scale_to_fit_height(max_h)
        mob.move_to(self.upper_center)
        return mob

    def safe_top(self) -> np.ndarray:
        return self.safe_center + np.array([0, self.safe_height / 2, 0])

    def safe_bottom(self) -> np.ndarray:
        return self.safe_center + np.array([0, -self.safe_height / 2, 0])

    # --- chroma ------------------------------------------------------------ #
    def reveal_chroma(self, run_time: float = 0.8):
        """Animate the chroma zone in (for ``animate_in`` renders)."""
        if self.chroma_zone is None:
            return
        self.play(FadeIn(self.chroma_zone, shift=UP * 0.2), run_time=run_time)

    def pad_to(self, target_seconds: float, elapsed: float) -> None:
        """Hold on the final frame so the scene lasts exactly ``target_seconds``
        to match its narration clip. Never waits a negative amount."""
        remaining = target_seconds - elapsed
        if remaining > 0.05:
            self.wait(remaining)

    # --- sound cues --------------------------------------------------------- #
    # The render is silent by design (audio is stripped when clips are conformed),
    # so a scene doesn't play sound — it *reports* when sound should happen. The
    # cues land in a sidecar JSON and are mixed onto the narration at assembly.
    def cue(self, name: str = "pop", *, gain: float | None = None,
            at: float | None = None) -> None:
        """Mark a moment for a sound effect.

        Call it immediately before the animation it belongs to::

            self.cue("whoosh"); self.play(FadeIn(eq))

        ``at`` overrides the timestamp (seconds from the start of this scene);
        by default the current render time is used.
        """
        when = at if at is not None else float(
            getattr(getattr(self, "renderer", None), "time", 0.0) or 0.0
        )
        entry = {"time": round(max(0.0, when), 3), "name": str(name)}
        if gain is not None:
            entry["gain"] = float(gain)
        if not hasattr(self, "_cues"):
            self._cues = []
        self._cues.append(entry)

    def _write_cues(self) -> None:
        path = globals().get("CUES_PATH") or ""
        if not path or not getattr(self, "_cues", None):
            return
        try:
            _Path(path).parent.mkdir(parents=True, exist_ok=True)
            _Path(path).write_text(
                _json.dumps({"cues": self._cues}, indent=2), encoding="utf-8"
            )
        except OSError:
            # Sound is a nicety; never fail a render over it.
            pass

    def tear_down(self) -> None:
        self._write_cues()
        self.report_layout()
        try:
            super().tear_down()
        except AttributeError:
            pass

    # --- photos ------------------------------------------------------------ #
    # IMAGES is injected by the header: one entry per image on this segment,
    # in the order they appear in the script. Photos are Group (not VGroup)
    # members throughout — ImageMobject is not a VMobject.
    def photo(self, which=0, *, height: float | None = None,
              width: float | None = None, framed: bool | None = None):
        """Build a themed photo for this segment.

        ``which`` is an index into IMAGES, or a path. The image is fitted to the
        safe area, given a subtle themed border and a caption if the script
        supplied one. Returns a Group you can position, scale and animate.
        """
        spec = self._image_spec(which)
        img = ImageMobject(spec["path"])

        # Fit inside the safe area by default, leaving room for a caption.
        max_w = self.safe_width * 0.86
        max_h = self.safe_height * (0.72 if spec.get("caption") else 0.84)
        if width is not None:
            max_w = width
        if height is not None:
            max_h = height
        scale = min(max_w / img.width, max_h / img.height)
        img.scale(scale)

        parts = [img]
        show_frame = spec.get("framed", True) if framed is None else framed
        if show_frame:
            border = Rectangle(
                width=img.width, height=img.height,
                stroke_color=THEME.get("line", "#2A3350"), stroke_width=3,
                fill_opacity=0,
            ).move_to(img.get_center())
            parts.append(border)

        group = Group(*parts)
        if spec.get("caption"):
            cap = self.label(spec["caption"], scale=0.55)
            cap.next_to(group, DOWN, buff=0.3)
            group = Group(group, cap)
        group.move_to(self.safe_center)
        return group

    def _image_spec(self, which) -> dict:
        images = globals().get("IMAGES") or []
        if isinstance(which, int):
            if not images:
                raise ValueError(
                    "This segment has no images; add one to the script with "
                    "![caption](path.png)"
                )
            if which >= len(images):
                raise IndexError(
                    f"Image index {which} out of range — this segment has "
                    f"{len(images)} image(s)."
                )
            return images[which]
        return {"path": str(which), "caption": "", "framed": True,
                "ken_burns": False}

    def show_photo(self, which=0, *, hold: float = 2.0, run_time: float = 0.9,
                   ken_burns: bool | None = None):
        """Fade a photo in, optionally drift/zoom it, and hold.

        This is the whole visual language of a photo beat, so every photo in
        every video moves the same way. Returns the elapsed seconds so the
        caller can ``pad_to`` the narration length.
        """
        spec = self._image_spec(which)
        group = self.photo(which)
        drift = spec.get("ken_burns", False) if ken_burns is None else ken_burns

        self.play(FadeIn(group, scale=0.96), run_time=run_time)
        elapsed = run_time
        if drift and hold > 0.4:
            # A slow push-in: still images read as dead frames without it.
            self.play(group.animate.scale(1.06), run_time=hold,
                      rate_func=linear)
            elapsed += hold
        elif hold > 0:
            self.wait(hold)
            elapsed += hold
        self._last_photo = group
        return elapsed

    def hide_photo(self, run_time: float = 0.5) -> float:
        """Fade out the photo from the last ``show_photo``."""
        group = getattr(self, "_last_photo", None)
        if group is None:
            return 0.0
        self.play(FadeOut(group), run_time=run_time)
        self._last_photo = None
        return run_time


# --------------------------------------------------------------------------- #
# Physics graphic builders (used by concept scenes)                           #
# --------------------------------------------------------------------------- #
CHARGE_COLOR = "#FF5A3C"
FIELD_COLOR = "#6FE7FF"
GOLD_A, GOLD_B = "#F4C842", "#FBE7A6"


def make_charge(center=ORIGIN, radius: float = 0.42, color: str = CHARGE_COLOR):
    """A glowing positive point charge with a '+'."""
    glow = Circle(radius=radius * 2.1, stroke_width=0,
                  fill_color=color, fill_opacity=0.18).move_to(center)
    core = Circle(radius=radius, stroke_color="#FFD8CC", stroke_width=3,
                  fill_color=color, fill_opacity=1.0).move_to(center)
    plus = MathTex("+", color=WHITE).scale(1.1).move_to(center)
    return VGroup(glow, core, plus)


def make_radial_field(center=ORIGIN, n: int = 12, r_in: float = 0.6,
                      r_out: float = 2.3, color: str = FIELD_COLOR):
    """Radial field arrows pointing outward from ``center`` (2D)."""
    arrows = VGroup()
    for i in range(n):
        ang = i * TAU / n
        d = np.array([np.cos(ang), np.sin(ang), 0.0])
        arrows.add(Arrow(center + d * r_in, center + d * r_out, buff=0,
                         color=color, stroke_width=5,
                         max_tip_length_to_length_ratio=0.16,
                         max_stroke_width_to_length_ratio=8))
    return arrows


def make_gaussian_circle(center=ORIGIN, radius: float = 2.15,
                         color: str = "#BFE9FF"):
    """A translucent 'Gaussian surface' cross-section (2D dashed sphere)."""
    disc = Circle(radius=radius, stroke_width=0,
                  fill_color=color, fill_opacity=0.10).move_to(center)
    ring = DashedVMobject(
        Circle(radius=radius, stroke_color=color, stroke_width=3).move_to(center),
        num_dashes=48,
    )
    return VGroup(disc, ring)


def sphere_point(u, v, radius: float = 2.1):
    return np.array([radius * np.cos(u) * np.sin(v),
                     radius * np.sin(u) * np.sin(v),
                     radius * np.cos(v)])


def make_gold_sphere(radius: float = 2.1, resolution=(32, 32)):
    """Checkerboard gold sphere (Image #1 Gaussian surface)."""
    return Surface(
        lambda u, v: sphere_point(u, v, radius),
        u_range=[0, TAU], v_range=[0, PI], resolution=resolution,
        checkerboard_colors=[GOLD_A, GOLD_B],
        fill_opacity=1.0, stroke_width=0.4, stroke_color="#B8860B",
    )


def make_area_patch(u0, v0, radius: float = 2.1, half: float = 0.16,
                    color: str = "#E5484D"):
    """A single clean red area element (dA) sitting on the sphere surface."""
    return Surface(
        lambda u, v: sphere_point(u, v, radius) * 1.012,
        u_range=[u0 - half, u0 + half], v_range=[v0 - half, v0 + half],
        resolution=(1, 1), checkerboard_colors=[color, color],
        fill_opacity=1.0, stroke_width=1.0, stroke_color="#7A1F22",
    )


# --------------------------------------------------------------------------- #
# Wave-optics builders (interference & diffraction)                           #
# --------------------------------------------------------------------------- #
# Palette: soft/educational, never oversaturated.
WAVE_BLUE = "#6FA8F5"      # light waves (source A)
WAVE_PURPLE = "#A78BFA"    # light waves (source B)
FRINGE_WHITE = "#FFFFFF"   # bright fringes
FRINGE_YELLOW = "#FDE68A"  # bright fringes, warm variant
OBSTACLE_GRAY = "#495468"  # barriers / obstacles
OBSTACLE_EDGE = "#6B7890"
HL_ORANGE = "#FFA75C"      # highlight
HL_GREEN = "#4ADE80"       # highlight / correct
SCREEN_DARK = "#0A1322"    # the observation screen plate


def opt_label(text: str, color: str = "#FFFFFF", size: int = 26,
              weight: str = "MEDIUM", line_spacing: float = 0.85):
    """A small on-diagram label in the UI font. Supports '\\n' for two-liners.

    Labels sit above diagram strokes so a wavefront can never cut through text.
    """
    t = Text(text, font=ui_font(), weight=weight, color=color, font_size=size,
             line_spacing=line_spacing)
    t.set_z_index(8)
    return t


def check_mark(size: float = 1.0, color: str = HL_GREEN, stroke_width: float = 9.0):
    """A hand-drawn-feeling tick (Poppins has no ✓ glyph, so we draw it)."""
    pts = [np.array([-0.34, 0.04, 0.0]),
           np.array([-0.10, -0.22, 0.0]),
           np.array([0.36, 0.30, 0.0])]
    vm = VMobject()
    vm.set_points_as_corners(pts)
    vm.set_stroke(color=color, width=stroke_width)
    vm.joint_type = LineJointType.ROUND
    vm.scale(size)
    return vm


def flow_arrow(length: float = 0.62, color: str = "#8FA6C8",
               stroke_width: float = 5.0):
    """A short downward arrow for `A ↓ B` flow diagrams."""
    return Arrow(
        ORIGIN, DOWN * length, buff=0, color=color, stroke_width=stroke_width,
        max_tip_length_to_length_ratio=0.34, max_stroke_width_to_length_ratio=12,
    )


def point_source(center=ORIGIN, radius: float = 0.13, color: str = FRINGE_YELLOW):
    """A glowing point source of light."""
    glow = Circle(radius=radius * 3.0, stroke_width=0,
                  fill_color=color, fill_opacity=0.16).move_to(center)
    halo = Circle(radius=radius * 1.8, stroke_width=0,
                  fill_color=color, fill_opacity=0.26).move_to(center)
    core = Circle(radius=radius, stroke_width=0,
                  fill_color="#FFFFFF", fill_opacity=1.0).move_to(center)
    return VGroup(glow, halo, core)


def slit_barrier(width: float, gaps: list[tuple[float, float]],
                 thickness: float = 0.20, y: float = 0.0,
                 center_x: float = 0.0, color: str = OBSTACLE_GRAY):
    """A horizontal opaque barrier with gaps cut out.

    The bar spans ``center_x ± width/2``; ``gaps`` is a list of (center_x,
    gap_width) in the SAME absolute coordinates. Segments are built between the
    gaps so the openings are genuinely empty (not just drawn over).
    """
    edges = [center_x - width / 2]
    for cx, gw in sorted(gaps):
        edges += [cx - gw / 2, cx + gw / 2]
    edges.append(center_x + width / 2)

    bar = VGroup()
    for i in range(0, len(edges) - 1, 2):
        x0, x1 = edges[i], edges[i + 1]
        if x1 - x0 <= 1e-6:
            continue
        seg = Rectangle(
            width=x1 - x0, height=thickness,
            stroke_width=1.6, stroke_color=OBSTACLE_EDGE,
            fill_color=color, fill_opacity=1.0,
        )
        seg.move_to(np.array([(x0 + x1) / 2, y, 0.0]))
        bar.add(seg)
    return bar


def circular_wavefronts(center, n: int = 7, r0: float = 0.30,
                        dr: float = 0.42, color: str = WAVE_BLUE,
                        start_angle: float = PI, sweep: float = PI,
                        stroke_width: float = 2.6, max_radius: float | None = None):
    """Concentric arcs = successive crests of a circular (Huygens) wavefront.

    Defaults sweep the lower half-plane, i.e. light propagating downward. Outer
    crests fade slightly, which reads as the 1/r amplitude drop.
    """
    arcs = VGroup()
    for i in range(n):
        r = r0 + i * dr
        if max_radius is not None and r > max_radius:
            break
        op = float(np.interp(i, [0, max(n - 1, 1)], [0.95, 0.34]))
        arcs.add(Arc(radius=r, start_angle=start_angle, angle=sweep,
                     arc_center=center, stroke_color=color,
                     stroke_width=stroke_width, stroke_opacity=op))
    return arcs


def plane_wavefronts(width: float, n: int = 5, y_top: float = 0.0,
                     dy: float = 0.42, color: str = WAVE_BLUE,
                     stroke_width: float = 2.6, center_x: float = 0.0):
    """Straight, evenly spaced crests = a plane wave travelling downward."""
    lines = VGroup()
    for i in range(n):
        y = y_top - i * dy
        lines.add(Line(np.array([center_x - width / 2, y, 0.0]),
                       np.array([center_x + width / 2, y, 0.0]),
                       stroke_color=color, stroke_width=stroke_width,
                       stroke_opacity=0.85))
    return lines


def ydse_bright_positions(d: float, D: float, lam: float,
                          half_width: float, max_order: int = 8) -> list[float]:
    """Exact screen positions of constructive interference in a double slit.

    Points of path difference ``n·λ`` lie on a hyperbola with the slits as foci
    (semi-axis a = nλ/2, c = d/2). Intersecting it with the screen at distance
    ``D`` gives x = a·√(1 + D²/b²), b² = c² − a². This is exact — no paraxial
    approximation — so the diagram stays correct at the exaggerated wavelengths
    a readable figure needs.
    """
    out = [0.0]
    c = d / 2.0
    for n in range(1, max_order + 1):
        a = n * lam / 2.0
        if a >= c:
            break
        b2 = c * c - a * a
        x = a * np.sqrt(1.0 + (D * D) / b2)
        if x > half_width:
            break
        out += [x, -x]
    return sorted(out)


def ydse_antinodal_curve(d: float, lam: float, n: int, y_slit: float,
                         y_screen: float, color: str = HL_ORANGE,
                         samples: int = 60, stroke_width: float = 2.4):
    """The exact locus of constructive interference for order ``n``.

    Points of constant path difference nλ form a hyperbola with the slits as
    foci: X = a·√(1 + Y²/b²), a = nλ/2, b² = (d/2)² − a². Drawing the real
    branch (rather than a straight ray from the slit midpoint) means the curve
    meets the screen exactly where the bright fringe is.
    """
    a = abs(n) * lam / 2.0
    b2 = (d / 2.0) ** 2 - a * a
    if b2 <= 0:
        return None
    sign = 1.0 if n >= 0 else -1.0
    pts = []
    for i in range(samples + 1):
        Y = (y_slit - y_screen) * i / samples
        x = sign * a * np.sqrt(1.0 + (Y * Y) / b2)
        pts.append([x, y_slit - Y, 0.0])
    return DashedVMobject(_polyline(pts, color, stroke_width), num_dashes=22)


def ydse_dark_positions(d: float, D: float, lam: float,
                        half_width: float, max_order: int = 8) -> list[float]:
    """Destructive positions: path difference (n + ½)·λ."""
    out: list[float] = []
    c = d / 2.0
    for n in range(max_order + 1):
        a = (2 * n + 1) * lam / 4.0
        if a >= c:
            break
        b2 = c * c - a * a
        x = a * np.sqrt(1.0 + (D * D) / b2)
        if x > half_width:
            break
        out += [x, -x]
    return sorted(out)


def bright_band(x: float, width: float, height: float, intensity: float = 1.0,
                color: str = FRINGE_WHITE, center_y: float = 0.0):
    """A bright fringe with a soft glow falloff (stacked rects, no blur needed).

    The glow is kept tight — wide halos bleed adjacent maxima into one another
    and the dark fringes between them stop reading.
    """
    grp = VGroup()
    for scale, op in ((1.85, 0.06), (1.45, 0.13), (1.16, 0.30), (1.0, 1.0)):
        grp.add(Rectangle(
            width=width * scale, height=height, stroke_width=0,
            fill_color=color, fill_opacity=op * intensity,
        ).move_to(np.array([x, center_y, 0.0])))
    return grp


def screen_plate(width: float, height: float, corner: float = 0.10):
    """The observation screen the fringes are cast on."""
    return RoundedRectangle(
        width=width, height=height, corner_radius=corner,
        stroke_width=2.0, stroke_color="#2A4C7E",
        fill_color=SCREEN_DARK, fill_opacity=0.94,
    )


def interference_pattern(width: float, height: float, n_bright: int = 9,
                         color: str = FRINGE_WHITE):
    """Double-slit fringes: equal width, equal spacing, equal intensity.

    Returns (plate, bands) with bands ordered centre-outwards so a LaggedStart
    reveal grows symmetrically from the central maximum.
    """
    plate = screen_plate(width, height)
    period = width / (n_bright + 0.4)
    band_w = period * 0.44
    half = (n_bright - 1) / 2.0
    order = sorted(range(n_bright), key=lambda i: abs(i - half))

    bands = VGroup()
    for i in order:
        x = (i - half) * period
        bands.add(bright_band(x, band_w, height * 0.90, 1.0, color))
    return plate, bands


# Single-slit geometry in units of β = πa·sinθ/λ, plotted over β ∈ [−4π, 4π].
# Minima at β = ±π, ±2π, ±3π ⇒ the central maximum (width 2π) is exactly twice
# as wide as each side maximum (width π). Peak intensities are the true sinc²
# values, perceptually boosted so the side fringes stay visible on screen —
# the same exaggeration NCERT's figure uses.
_DIFF_SIDE_INTENSITY = (0.30, 0.17, 0.09)


def diffraction_pattern(width: float, height: float,
                        color: str = FRINGE_WHITE, n_side: int = 3):
    """Single-slit fringes: wide central maximum, narrower/dimmer side maxima."""
    plate = screen_plate(width, height)
    unit = width / 8.0            # one π of β
    bands = VGroup()
    bands.add(bright_band(0.0, unit * 2.0 * 0.66, height * 0.90, 1.0, color))
    for k in range(1, min(n_side, 3) + 1):
        cx = unit * (k + 0.5)
        intensity = _DIFF_SIDE_INTENSITY[k - 1]
        for sx in (cx, -cx):
            bands.add(bright_band(sx, unit * 0.50, height * 0.90, intensity, color))
    return plate, bands


def _polyline(points, color: str, stroke_width: float = 3.4):
    vm = VMobject()
    vm.set_points_as_corners([np.array(p) for p in points])
    vm.set_stroke(color=color, width=stroke_width)
    vm.joint_type = LineJointType.ROUND
    return vm


def interference_intensity_curve(width: float, height: float, n_bright: int = 9,
                                 color: str = WAVE_BLUE, samples: int = 260):
    """I(x) = I₀·cos²(πx/period) — every maximum reaches the same height."""
    period = width / (n_bright + 0.4)
    pts = []
    for i in range(samples + 1):
        x = -width / 2 + width * i / samples
        y = np.cos(PI * x / period) ** 2
        pts.append([x, y * height, 0.0])
    return _polyline(pts, color)


def diffraction_intensity_curve(width: float, height: float,
                                color: str = WAVE_PURPLE, samples: int = 420):
    """I(β) = I₀·(sin β / β)² over β ∈ [−4π, 4π] — the true single-slit curve."""
    pts = []
    for i in range(samples + 1):
        x = -width / 2 + width * i / samples
        beta = (x / (width / 2)) * 4 * PI
        y = 1.0 if abs(beta) < 1e-9 else (np.sin(beta) / beta) ** 2
        pts.append([x, y * height, 0.0])
    return _polyline(pts, color)


def chip(text: str, color: str = "#FFFFFF", size: int = 28,
         fill: str = "#0B1830", fill_opacity: float = 0.92,
         pad_x: float = 0.30, pad_y: float = 0.18, weight: str = "SEMIBOLD",
         line_spacing: float = 0.85):
    """A small rounded label plate — used for column headers and card titles.

    Nearly opaque and z-lifted, so a chip stays legible when it has to sit over
    a dense wavefront diagram.
    """
    label = Text(text, font=ui_font(), weight=weight, color=color,
                 font_size=size, line_spacing=line_spacing)
    h = label.height + 2 * pad_y
    plate = RoundedRectangle(
        width=label.width + 2 * pad_x, height=h,
        corner_radius=min(0.22, h / 2 - 0.01),
        stroke_width=1.6, stroke_color=color, stroke_opacity=0.45,
        fill_color=fill, fill_opacity=fill_opacity,
    )
    grp = VGroup(plate, label)
    grp.set_z_index(10)
    return grp


def divider_line(x: float, y_top: float, y_bottom: float,
                 color: str = "#3C5C8C", opacity: float = 0.55):
    """The vertical rule separating the Interference / Diffraction columns."""
    return DashedVMobject(
        Line(np.array([x, y_top, 0.0]), np.array([x, y_bottom, 0.0]),
             stroke_color=color, stroke_width=2.2, stroke_opacity=opacity),
        num_dashes=26,
    )


def measure_bracket(x0: float, x1: float, y: float, color: str = HL_ORANGE,
                    tick: float = 0.11, stroke_width: float = 3.0):
    """A |<--->| width marker used to compare fringe widths."""
    grp = VGroup()
    grp.add(Line([x0, y - tick, 0], [x0, y + tick, 0],
                 stroke_color=color, stroke_width=stroke_width))
    grp.add(Line([x1, y - tick, 0], [x1, y + tick, 0],
                 stroke_color=color, stroke_width=stroke_width))
    grp.add(DoubleArrow([x0, y, 0], [x1, y, 0], buff=0, color=color,
                        stroke_width=stroke_width * 0.8,
                        max_tip_length_to_length_ratio=0.16))
    return grp


def compare_layout(center, width: float):
    """Shared geometry for the LEFT=Interference / RIGHT=Diffraction split.

    Every scene from "Kab Hote Hain?" through "Brightness Difference" builds
    from this, so the divider, headers, screens, curves and labels land on the
    exact same pixels across segment boundaries and the cuts read as one
    continuous shot.
    """
    cx, cy = float(center[0]), float(center[1])
    gap = 0.34
    col_w = (width - gap) / 2.0
    return {
        "left_x": cx - (col_w + gap) / 2.0,
        "right_x": cx + (col_w + gap) / 2.0,
        "col_w": col_w,
        "divider_x": cx,
        "divider_top": cy + 2.23,
        "divider_bottom": cy - 2.77,
        "header_y": cy + 2.68,
        "plate_y": cy + 1.38,
        "plate_w": col_w * 0.93,
        "plate_h": 1.10,
        "curve_y": cy - 0.87,     # intensity-curve baseline
        "curve_h": 1.30,
        "label_y": cy - 1.62,
        "sub_y": cy - 2.37,
    }


def compare_base(center, width: float, screen_label: str = "Screen"):
    """Build the shared furniture of the comparison scenes.

    Returns ``(lay, parts)`` where ``parts`` is a dict of individually
    animatable mobjects. Every scene from "Fringe Pattern" through "Brightness
    Difference" builds from this, so the divider, headers and screens are
    pixel-identical across segment boundaries.
    """
    lay = compare_layout(center, width)
    parts = {
        "divider": divider_line(lay["divider_x"], lay["header_y"] - 0.55,
                                lay["sub_y"] - 0.30),
        "head_l": chip("Interference", WAVE_BLUE, size=28
                       ).move_to([lay["left_x"], lay["header_y"], 0]),
        "head_r": chip("Diffraction", WAVE_PURPLE, size=28
                       ).move_to([lay["right_x"], lay["header_y"], 0]),
        "plate_l": screen_plate(lay["plate_w"], lay["plate_h"]
                                ).move_to([lay["left_x"], lay["plate_y"], 0]),
        "plate_r": screen_plate(lay["plate_w"], lay["plate_h"]
                                ).move_to([lay["right_x"], lay["plate_y"], 0]),
    }
    cap_y = lay["plate_y"] - lay["plate_h"] / 2 - 0.34
    parts["cap_l"] = opt_label(screen_label, "#9FB6D8", size=20
                               ).move_to([lay["left_x"], cap_y, 0])
    parts["cap_r"] = opt_label(screen_label, "#9FB6D8", size=20
                               ).move_to([lay["right_x"], cap_y, 0])
    return lay, parts


def recap_card(cx: float, accent: str, cy: float = 2.72,
               width: float = 3.25, height: float = 3.40):
    """A concept card for the closing recap — sits high in the frame so the
    lower third stays clear for the answer-writing transition."""
    return RoundedRectangle(
        width=width, height=height, corner_radius=0.26,
        stroke_width=2.0, stroke_color=accent, stroke_opacity=0.55,
        fill_color="#0B1830", fill_opacity=0.55,
    ).move_to([cx, cy, 0])


N_INTERFERENCE_FRINGES = 9
DIFF_PLATE_FRAC = 0.94        # diffraction pattern inset inside its screen


def fringe_bands(lay):
    """The two finished patterns, positioned on their screens.

    Shared so every segment that shows them rebuilds identical geometry.
    """
    _, left = interference_pattern(lay["plate_w"], lay["plate_h"] * 0.86,
                                   n_bright=N_INTERFERENCE_FRINGES)
    left.move_to([lay["left_x"], lay["plate_y"], 0])
    _, right = diffraction_pattern(lay["plate_w"] * DIFF_PLATE_FRAC,
                                   lay["plate_h"] * 0.86)
    right.move_to([lay["right_x"], lay["plate_y"], 0])
    return left, right


def intensity_axis(cx: float, lay, color: str = "#5E7BA8"):
    """An I-vs-position axis sitting under one of the screens."""
    x0 = cx - lay["plate_w"] / 2
    base = Line([x0, lay["curve_y"], 0],
                [cx + lay["plate_w"] / 2, lay["curve_y"], 0],
                stroke_color=color, stroke_width=2.2)
    up = Arrow([x0, lay["curve_y"], 0], [x0, lay["curve_y"] + lay["curve_h"], 0],
               buff=0, color=color, stroke_width=2.6,
               max_tip_length_to_length_ratio=0.12)
    tag = opt_label("I", "#8FA6C8", size=20)
    tag.move_to([x0 - 0.26, lay["curve_y"] + lay["curve_h"] * 0.78, 0])
    return VGroup(base, up, tag)


def mini_interference_icon(width: float = 2.0, color_a: str = WAVE_BLUE,
                           color_b: str = WAVE_PURPLE):
    """Two overlapping wave trains — the 'interference' thumbnail."""
    def train(phase: float, color: str, amp: float):
        pts = []
        for i in range(121):
            x = -width / 2 + width * i / 120
            pts.append([x, amp * np.sin(2 * PI * 2.0 * x / width + phase), 0.0])
        return _polyline(pts, color, stroke_width=3.0)
    return VGroup(train(0.0, color_a, 0.30), train(PI * 0.55, color_b, 0.30))


def mini_diffraction_icon(width: float = 2.0):
    """Light through one narrow slit, spreading — the 'diffraction' thumbnail."""
    barrier = slit_barrier(width, [(0.0, 0.18)], thickness=0.14, y=0.42)
    fronts = circular_wavefronts(
        np.array([0.0, 0.42, 0.0]), n=4, r0=0.22, dr=0.24,
        color=WAVE_PURPLE, stroke_width=2.4,
    )
    return VGroup(barrier, fronts)


# --------------------------------------------------------------------------- #
# Chemistry builders (d-block elements)                                        #
# --------------------------------------------------------------------------- #
DB_BLUE = "#5B9DF9"
DB_ORANGE = "#FFA75C"
DB_GREEN = "#4ADE80"
DB_RED = "#F87171"
DB_PURPLE = "#A78BFA"
DB_GRAY = "#64748B"

# Which columns exist in each period — the real staircase outline of the table.
_PT_ROWS = {
    1: [1, 18],
    2: [1, 2] + list(range(13, 19)),
    3: [1, 2] + list(range(13, 19)),
    4: list(range(1, 19)),
    5: list(range(1, 19)),
    6: list(range(1, 19)),
    7: list(range(1, 19)),
}
D_BLOCK_GROUPS = list(range(3, 13))     # groups 3-12
D_BLOCK_PERIODS = [4, 5, 6, 7]


def periodic_table(width: float, gap: float = 0.028):
    """A schematic periodic table with the correct staircase outline.

    Returns ``(table, cells)`` where ``cells`` maps (period, group) -> square,
    so callers can recolour or glow any region — here, the d-block.
    """
    cell = (width - 17 * gap) / 18.0
    step = cell + gap
    table = VGroup()
    cells: dict[tuple[int, int], "Mobject"] = {}
    for period, groups in _PT_ROWS.items():
        for group in groups:
            sq = RoundedRectangle(
                width=cell, height=cell, corner_radius=cell * 0.20,
                stroke_width=1.0, stroke_color="#3E5D8C", stroke_opacity=0.85,
                fill_color="#16294A", fill_opacity=0.85,
            )
            sq.move_to([(group - 9.5) * step, -(period - 4) * step, 0.0])
            cells[(period, group)] = sq
            table.add(sq)
    return table, cells


def d_block_cells(cells) -> "VGroup":
    """Just the d-block squares (groups 3-12, periods 4-7)."""
    return VGroup(*[cells[(p, g)] for p in D_BLOCK_PERIODS
                    for g in D_BLOCK_GROUPS if (p, g) in cells])


def other_cells(cells) -> "VGroup":
    d = {(p, g) for p in D_BLOCK_PERIODS for g in D_BLOCK_GROUPS}
    return VGroup(*[m for k, m in cells.items() if k not in d])


def atom_shells(center=ORIGIN, radii=(0.42, 0.72, 1.02, 1.34),
                color: str = DB_BLUE):
    """A Bohr-style atom: nucleus plus shell circles (no electrons yet)."""
    nucleus = VGroup(
        Circle(radius=0.20, stroke_width=0, fill_color=DB_ORANGE,
               fill_opacity=0.22).move_to(center),
        Circle(radius=0.13, stroke_width=0, fill_color=DB_ORANGE,
               fill_opacity=1.0).move_to(center),
    )
    shells = VGroup(*[
        Circle(radius=r, stroke_color=color, stroke_width=2.0,
               stroke_opacity=0.55).move_to(center)
        for r in radii
    ])
    return VGroup(nucleus, shells)


def shell_electrons(center, radius: float, n: int, color: str = "#DCE8FF",
                    phase: float = 0.0, dot_radius: float = 0.055):
    """``n`` electrons spaced evenly around one shell."""
    grp = VGroup()
    for i in range(n):
        ang = phase + i * TAU / max(n, 1)
        grp.add(Dot(center + np.array([radius * np.cos(ang),
                                       radius * np.sin(ang), 0.0]),
                    radius=dot_radius, color=color))
    return grp


def orbital_boxes(n: int, filled: list[int], width: float = 0.34,
                  gap: float = 0.07, color: str = DB_BLUE,
                  paired: list[int] | None = None):
    """``n`` orbital boxes; ``filled`` lists indices holding an electron.

    ``paired`` indices get an up+down pair, the rest a single up arrow — so a
    partially filled d-subshell reads correctly at a glance.
    """
    paired = paired or []
    boxes = VGroup()
    arrows = VGroup()
    step = width + gap
    for i in range(n):
        x = (i - (n - 1) / 2) * step
        box = Rectangle(width=width, height=width * 0.86, stroke_width=1.8,
                        stroke_color=color, fill_color="#12203C",
                        fill_opacity=0.7).move_to([x, 0, 0])
        boxes.add(box)
        if i in filled:
            up = Arrow([x - width * 0.13, -width * 0.30, 0],
                       [x - width * 0.13, width * 0.30, 0], buff=0,
                       color="#FFFFFF", stroke_width=3.0,
                       max_tip_length_to_length_ratio=0.34)
            arrows.add(up)
            if i in paired:
                dn = Arrow([x + width * 0.13, width * 0.30, 0],
                           [x + width * 0.13, -width * 0.30, 0], buff=0,
                           color="#FFFFFF", stroke_width=3.0,
                           max_tip_length_to_length_ratio=0.34)
                arrows.add(dn)
    return boxes, arrows


def electron_sea(nx: int = 4, ny: int = 3, spacing: float = 0.62,
                 ion_color: str = DB_BLUE, e_color: str = "#FDE68A"):
    """Metal cations on a lattice inside a delocalised sea of electrons."""
    ions = VGroup()
    for j in range(ny):
        for i in range(nx):
            p = np.array([(i - (nx - 1) / 2) * spacing,
                          (j - (ny - 1) / 2) * spacing, 0.0])
            ions.add(VGroup(
                Circle(radius=0.20, stroke_width=0, fill_color=ion_color,
                       fill_opacity=0.20).move_to(p),
                Circle(radius=0.145, stroke_width=1.6, stroke_color="#BFD8FF",
                       fill_color=ion_color, fill_opacity=0.95).move_to(p),
                opt_label("+", "#FFFFFF", size=17).move_to(p),
            ))
    electrons = VGroup()
    for j in range(ny + 1):
        for i in range(nx + 1):
            p = np.array([(i - nx / 2) * spacing, (j - ny / 2) * spacing, 0.0])
            electrons.add(Dot(p, radius=0.048, color=e_color))
    return ions, electrons


def _rr(w, h, r, fill, stroke=None, sw=0.0, op=1.0):
    return RoundedRectangle(width=w, height=h, corner_radius=r,
                            stroke_width=sw, stroke_color=stroke or fill,
                            fill_color=fill, fill_opacity=op)


def icon_hammer(color: str = DB_GRAY, accent: str = DB_ORANGE):
    """Hardness."""
    head = _rr(0.62, 0.26, 0.07, color)
    claw = _rr(0.16, 0.26, 0.06, color).next_to(head, LEFT, buff=0.0)
    handle = _rr(0.11, 0.62, 0.05, accent)
    handle.next_to(head, DOWN, buff=0.0).shift(RIGHT * 0.14)
    return VGroup(claw, head, handle)


def icon_wire(color: str = DB_ORANGE):
    """Ductility: a wire drawn out between two pulls."""
    wire = _polyline([[-0.62, 0.0, 0], [-0.22, 0.0, 0], [0.0, 0.0, 0],
                      [0.22, 0.0, 0], [0.62, 0.0, 0]], color, 5.0)
    left = Arrow([-0.42, 0.30, 0], [-0.80, 0.30, 0], buff=0, color="#DCE8FF",
                 stroke_width=3.0, max_tip_length_to_length_ratio=0.32)
    right = Arrow([0.42, 0.30, 0], [0.80, 0.30, 0], buff=0, color="#DCE8FF",
                  stroke_width=3.0, max_tip_length_to_length_ratio=0.32)
    return VGroup(wire, left, right)


def icon_sheet(color: str = DB_BLUE):
    """Malleability: a block beaten flat into a sheet."""
    sheet = Polygon([-0.72, -0.10, 0], [0.52, -0.10, 0],
                    [0.72, 0.12, 0], [-0.52, 0.12, 0],
                    stroke_width=1.6, stroke_color="#BFD8FF",
                    fill_color=color, fill_opacity=0.85)
    down = VGroup(*[
        Arrow([x, 0.62, 0], [x, 0.24, 0], buff=0, color="#DCE8FF",
              stroke_width=3.0, max_tip_length_to_length_ratio=0.36)
        for x in (-0.30, 0.0, 0.30)])
    return VGroup(sheet, down)


def icon_thermometer(fill_frac: float = 0.78, color: str = DB_RED):
    """High melting / boiling point."""
    tube = _rr(0.20, 0.86, 0.10, "#0E1E38", stroke="#BFD8FF", sw=1.8, op=0.9)
    tube.shift(UP * 0.18)
    bulb = Circle(radius=0.17, stroke_width=1.8, stroke_color="#BFD8FF",
                  fill_color=color, fill_opacity=1.0).shift(DOWN * 0.42)
    col_h = 0.70 * fill_frac
    column = _rr(0.09, col_h, 0.045, color)
    column.move_to([0.0, -0.28 + col_h / 2, 0.0])
    return VGroup(tube, column, bulb)


def icon_flame(color: str = DB_ORANGE):
    """Boiling point / heat."""
    outer = Polygon([0.0, 0.62, 0], [0.30, 0.16, 0], [0.20, -0.22, 0],
                    [0.0, -0.40, 0], [-0.20, -0.22, 0], [-0.30, 0.16, 0],
                    stroke_width=0, fill_color=color, fill_opacity=0.85)
    inner = Polygon([0.0, 0.30, 0], [0.15, 0.02, 0], [0.0, -0.26, 0],
                    [-0.15, 0.02, 0], stroke_width=0,
                    fill_color=FRINGE_YELLOW, fill_opacity=0.95)
    return VGroup(outer, inner)


def icon_bolt(color: str = FRINGE_YELLOW):
    """Electrical conductivity."""
    return Polygon([0.10, 0.62, 0], [-0.28, 0.06, 0], [-0.02, 0.06, 0],
                   [-0.12, -0.60, 0], [0.28, -0.02, 0], [0.02, -0.02, 0],
                   stroke_width=0, fill_color=color, fill_opacity=0.95)


def icon_heatwave(color: str = DB_RED, n: int = 3):
    """Thermal conductivity: rising heat squiggles."""
    waves = VGroup()
    for k in range(n):
        pts = []
        for i in range(41):
            t = i / 40
            pts.append([(-0.26 + k * 0.26), -0.42 + t * 0.92, 0.0])
            pts[-1][0] += 0.09 * np.sin(t * TAU * 1.5)
        waves.add(_polyline(pts, color, 3.2))
    return waves


def energy_bar(height: float, width: float = 0.52, color: str = DB_BLUE,
               label: str = ""):
    """A vertical energy-level bar with its label underneath."""
    bar = _rr(width, max(height, 0.02), min(0.10, width / 3), color, op=0.88)
    grp = VGroup(bar)
    if label:
        tag = opt_label(label, "#DCE8FF", size=21)
        tag.next_to(bar, DOWN, buff=0.16)
        grp.add(tag)
    return grp


class Themed3DScene(ThreeDScene):
    """3D counterpart of ThemedScene: themed background, an orbiting camera,
    content raised into the upper half, and a fixed-in-frame HUD for labels."""

    def setup(self) -> None:
        super().setup()
        self.theme = THEME
        self.camera.background_color = THEME["background"]
        self.set_camera_orientation(phi=64 * DEGREES, theta=-46 * DEGREES)
        self.up_shift = OUT * 3.0  # +z reads as screen-up under this camera

    def stage(self, *mobs):
        """Group 3D content and raise it into the upper half. Returns the Group."""
        g = Group(*mobs)
        g.shift(self.up_shift)
        return g

    def hud(self, mob):
        """Add a screen-space (non-rotating) label."""
        self.add_fixed_in_frame_mobjects(mob)
        return mob

    def eq(self, latex: str, color: str | None = None, scale: float = 1.0):
        m = MathTex(latex, color=color or THEME["primary"])
        return m.scale(scale) if scale != 1.0 else m

    def label(self, text: str, color: str | None = None, scale: float = 0.62):
        t = Text(text, color=color or THEME["secondary"], line_spacing=1.0).scale(scale)
        if t.width > _fw() * 0.92:
            t.scale_to_fit_width(_fw() * 0.92)
        return t
