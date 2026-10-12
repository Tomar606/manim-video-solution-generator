"""Turning one still into a moving video: hold on a region, glide to the next.

A poster is a *layout*, not a picture — five numbered points, a heading, a
diagram. Shown whole for thirty seconds it is unreadable on a phone; read one
region at a time it becomes a video. This module does that: it takes an image
and a list of regions, and produces a clip that settles on each region in turn.

Two things here are not obvious and are the whole reason this file exists.

**The move between two regions is not a straight pan.** Panning across a
zoomed-in poster at reading magnification smears everything between the two
points and tells the viewer nothing about where they just went. The fix is
van Wijk & Nuij's smooth-and-efficient zooming ( `_van_wijk` ): the camera
pulls back as it travels and dives in again on arrival, by an amount that falls
out of the geometry. Points that are neighbours get an almost flat move; points
at opposite ends of the poster get a visible pull-back that re-establishes the
whole layout on the way. Nobody has to hand-author that.

**Every view is corrected to the OUTPUT aspect before anything else happens.**
A region on a poster is whatever shape the designer made it; the frame is
9:16 or 16:9. `fit_view` widens or heightens the region to the frame's shape,
pads it, and clamps it inside the image — so the path is expressed in one
scalar (viewport width) and can never wander off the paper or letterbox.

Frames are cut with Pillow rather than ffmpeg's `zoompan`. `zoompan` rounds its
crop to whole pixels, which at these magnifications reads as a visible stutter
in the text, and its clock (`it`/`on`, never `t`) has cost this repo hours
before. `Image.resize(box=...)` takes a float box, so the motion is sub-pixel
and dead smooth; frames are piped raw into ffmpeg for encoding.

Usage::

    python -m src.poster_zoom poster.png --auto 5 -o out.mp4     # find the points
    python -m src.poster_zoom poster.png --spec points.json -o out.mp4
    python -m src.poster_zoom poster.png --spec points.json --stills check/
"""
from __future__ import annotations

import argparse
import json
import math
import shutil
import subprocess
import sys
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Callable, Iterable

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageOps

try:  # Pillow >= 9.1
    LANCZOS = Image.Resampling.LANCZOS
except AttributeError:  # pragma: no cover - very old Pillow
    LANCZOS = Image.LANCZOS

# Pillow refuses very large files by default; posters legitimately are.
Image.MAX_IMAGE_PIXELS = None


class PosterError(ValueError):
    """The spec, the image or the geometry cannot produce a video."""


# --------------------------------------------------------------------------
# Geometry
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class View:
    """A camera position over the image: centre, and viewport WIDTH in pixels.

    Height is implied — every view carries the output aspect ratio, which is
    enforced the moment a region is turned into a View and never violated
    afterwards. One scalar for zoom is what lets the path maths stay simple.
    """
    cx: float
    cy: float
    w: float

    def box(self, aspect: float) -> tuple[float, float, float, float]:
        h = self.w / aspect
        return (self.cx - self.w / 2, self.cy - h / 2,
                self.cx + self.w / 2, self.cy + h / 2)

    def scaled(self, factor: float) -> "View":
        return replace(self, w=self.w * factor)


def contain_width(img_w: int, img_h: int, aspect: float) -> float:
    """The viewport width at which the WHOLE image is inside the frame.

    Wider than this is pointless — it would only add more empty margin.
    """
    return max(float(img_w), img_h * aspect)


def clamp_view(v: View, img_w: int, img_h: int, aspect: float) -> View:
    """Pull a view back onto the paper without changing its shape.

    The ceiling is `contain_width`, not the image width: a view that is wider
    than the paper is legal and gets bars, which is the only way an
    establishing shot of a 2:3 poster can show the whole thing in a 16:9
    frame. Capping at the image width instead — the obvious thing — silently
    turns "the whole poster" into "the middle slice of the poster".

    Order matters: shrink first (a viewport wider than the ceiling can never
    be satisfied by shifting), then slide. And once an axis is bigger than the
    paper there is nothing left to slide along, so it centres.
    """
    w = min(v.w, contain_width(img_w, img_h, aspect))
    h = w / aspect
    cx = img_w / 2 if w >= img_w else min(max(v.cx, w / 2), img_w - w / 2)
    cy = img_h / 2 if h >= img_h else min(max(v.cy, h / 2), img_h - h / 2)
    return View(cx, cy, w)


def fit_view(rect: tuple[float, float, float, float], img_w: int, img_h: int,
             aspect: float, *, pad: float = 1.0, zoom: float = 1.0) -> View:
    """A region of the poster -> a legal camera view of it.

    ``rect`` is (x, y, w, h) in pixels. ``pad`` is breathing room around the
    region (1.08 = eight percent), ``zoom`` an author's override where >1 sits
    further back.
    """
    x, y, w, h = rect
    if w <= 0 or h <= 0:
        raise PosterError(f"region has no area: {rect}")
    cx, cy = x + w / 2, y + h / 2
    # Grow the shorter axis until the region matches the frame's shape.
    base = max(w, h * aspect) * zoom
    padded = base * pad
    # Padding is a nicety; bars are an artifact. A card that spans almost the
    # whole poster gets pushed past the edge by the margin alone, and then
    # every one of its frames is a letterboxed frame with a three-pixel black
    # stripe down the side. So the margin gives way where the region already
    # fits and the margin is the only thing that would not.
    cap = float("inf")
    if base <= img_w:
        cap = min(cap, float(img_w))
    if base / aspect <= img_h:
        cap = min(cap, img_h * aspect)
    view_w = max(base, min(padded, cap)) if cap != float("inf") else padded
    return clamp_view(View(cx, cy, view_w), img_w, img_h, aspect)


def full_view(img_w: int, img_h: int, aspect: float) -> View:
    """The establishing shot: the whole poster, bars where the shapes differ."""
    return View(img_w / 2, img_h / 2, contain_width(img_w, img_h, aspect))


# --------------------------------------------------------------------------
# The glow that marks which point the camera is on
# --------------------------------------------------------------------------

@dataclass
class Glow:
    """A lit border around the region currently being read.

    On a busy poster the crop alone does not say *which* card matters — half a
    neighbour is usually still in frame, and on a dense layout the eye has no
    reason to pick one. The border says it, and it says it before the camera
    has finished arriving, which is why it rises during the incoming move
    rather than after it.

    Sizes are fractions of the image's SHORT side, so one setting looks the
    same on a 900px WhatsApp export and a 4000px print file.
    """
    enabled: bool = True
    color: str = "#FFD24A"     # warm gold; reads as light on light and on dark
    width: float = 0.007       # the crisp line
    radius: float = 0.020      # corner rounding
    inset: float = 0.007       # how far outside the card the line sits
    blur: float = 0.017        # halo softness
    halo: float = 1.0          # halo strength, 0..1
    opacity: float = 1.0
    dim: float = 0.0           # how far to darken everything outside the point
    fade: float = 0.40         # seconds to rise on approach and fall on leaving
    pulse: float = 0.0         # 0 = steady; else how deep it breathes
    pulse_hz: float = 0.45


def _hex_rgb(value: str) -> tuple[int, int, int]:
    v = value.strip().lstrip("#")
    if len(v) == 3:
        v = "".join(c * 2 for c in v)
    if len(v) != 6:
        raise PosterError(f"bad colour {value!r}, want #RRGGBB")
    return tuple(int(v[i:i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def _smoothstep(u: float) -> float:
    u = min(max(u, 0.0), 1.0)
    return u * u * (3 - 2 * u)


def build_glow_sprite(rect: tuple[float, float, float, float], img_w: int,
                      img_h: int, g: Glow) -> tuple[Image.Image, float, float]:
    """Render the border once, at image scale, as a premultiplied RGB sprite.

    Premultiplied and alpha-free on purpose: the sprite is *screened* onto the
    frame, not alpha-pasted. Screening adds light and leaves the artwork under
    the halo readable; an alpha paste would lay a flat gold wash over the card
    edge and swallow whatever the designer put there. Black pixels in the
    sprite screen to nothing, so the transparent margin needs no mask.

    Returns the sprite and its top-left corner in image coordinates.
    """
    x, y = rect[0] * img_w, rect[1] * img_h
    w, h = rect[2] * img_w, rect[3] * img_h
    short = min(img_w, img_h)
    lw = max(2.0, g.width * short)
    rad = g.radius * short
    ins = g.inset * short
    blur = max(0.8, g.blur * short)
    margin = blur * 3 + lw * 2 + 6

    sw = int(round(w + 2 * ins + 2 * margin))
    sh = int(round(h + 2 * ins + 2 * margin))
    # The path every band is centred on, in sprite-local coordinates.
    px0, py0 = margin, margin
    px1, py1 = margin + w + 2 * ins, margin + h + 2 * ins

    def band(width: float, blur_px: float, strength: float) -> Image.Image:
        # Pillow grows an outline INWARD from the rectangle it is given, so
        # each band is drawn on a rect pushed out by half its width. Without
        # that the halo eats into the card instead of blooming off it.
        d = width / 2
        m = Image.new("L", (sw, sh), 0)
        ImageDraw.Draw(m).rounded_rectangle(
            [px0 - d, py0 - d, px1 + d, py1 + d], radius=rad + d,
            outline=255, width=max(1, int(round(width))))
        if blur_px > 0:
            m = m.filter(ImageFilter.GaussianBlur(blur_px))
        if strength < 1.0:
            m = m.point(lambda v, k=strength: int(v * k))
        return m

    mask = ImageChops.add(
        ImageChops.add(band(lw * 3.0, blur * 1.5, g.halo),
                       band(lw * 1.6, blur * 0.5, 0.85)),
        band(lw, max(0.6, blur * 0.08), 1.0))
    sprite = ImageChops.multiply(Image.new("RGB", (sw, sh), _hex_rgb(g.color)),
                                 Image.merge("RGB", (mask, mask, mask)))
    return sprite, x - ins - margin, y - ins - margin


def build_dim_mask(rect: tuple[float, float, float, float], img_w: int,
                   img_h: int, g: Glow) -> Image.Image:
    """A poster-sized mask: lit inside the point, dark outside, soft at the edge.

    Full poster size rather than a sprite, because unlike the border this one
    has to say something about every pixel of the frame, most of which is
    nowhere near the card.
    """
    short = min(img_w, img_h)
    ins = g.inset * short
    rad = g.radius * short
    m = Image.new("L", (img_w, img_h), 0)
    ImageDraw.Draw(m).rounded_rectangle(
        [rect[0] * img_w - ins, rect[1] * img_h - ins,
         (rect[0] + rect[2]) * img_w + ins, (rect[1] + rect[3]) * img_h + ins],
        radius=rad, fill=255)
    return m.filter(ImageFilter.GaussianBlur(max(1.0, g.blur * short * 1.2)))


def screen_sprite(frame: Image.Image, sprite: Image.Image, sx0: float,
                  sy0: float, view: View, aspect: float, alpha: float) -> None:
    """Screen a sprite into the frame, aligned sub-pixel to the artwork.

    The sprite is resampled from a FLOAT source box computed back from the
    integer destination box, so the glow tracks the card exactly as the camera
    creeps. Resizing to an integer size and pasting at an integer offset would
    let the border shiver against the edge it is supposed to be hugging.
    """
    W, H = frame.size
    vx0, vy0, _, _ = view.box(aspect)
    s = W / view.w
    sw, sh = sprite.size

    X0 = max(0, math.floor((sx0 - vx0) * s))
    X1 = min(W, math.ceil((sx0 + sw - vx0) * s))
    Y0 = max(0, math.floor((sy0 - vy0) * s))
    Y1 = min(H, math.ceil((sy0 + sh - vy0) * s))
    if X1 - X0 < 1 or Y1 - Y0 < 1:
        return

    u0 = min(max(X0 / s + vx0 - sx0, 0.0), float(sw))
    u1 = min(max(X1 / s + vx0 - sx0, 0.0), float(sw))
    v0 = min(max(Y0 / s + vy0 - sy0, 0.0), float(sh))
    v1 = min(max(Y1 / s + vy0 - sy0, 0.0), float(sh))
    if u1 - u0 < 0.5 or v1 - v0 < 0.5:
        return

    g = sprite.resize((X1 - X0, Y1 - Y0), LANCZOS, box=(u0, v0, u1, v1))
    if alpha < 0.999:
        g = g.point(lambda v, a=alpha: int(v * a))
    frame.paste(ImageChops.screen(frame.crop((X0, Y0, X1, Y1)), g), (X0, Y0))


# --------------------------------------------------------------------------
# The move between two views
# --------------------------------------------------------------------------

def _van_wijk_peak(w0: float, w1: float, u: float, rho: float) -> float:
    """How far the camera would pull back on this move, in viewport width.

    Closed form, so the search for a usable ``rho`` below is cheap.
    """
    b0 = (w1 * w1 - w0 * w0 + rho ** 4 * u * u) / (2 * w0 * rho * rho * u)
    r0 = math.log(-b0 + math.sqrt(b0 * b0 + 1))
    b1 = (w1 * w1 - w0 * w0 - rho ** 4 * u * u) / (2 * w1 * rho * rho * u)
    r1 = math.log(-b1 + math.sqrt(b1 * b1 + 1))
    S = (r1 - r0) / rho
    if S <= 0:
        return max(w0, w1)
    # w(s) is widest where cosh(rho*s + r0) is smallest, i.e. at s = -r0/rho.
    s_peak = -r0 / rho
    if 0.0 <= s_peak <= S:
        return w0 * math.cosh(r0)
    return max(w0, w1)


def _van_wijk(v0: View, v1: View, rho: float) -> tuple[float, Callable[[float], View]]:
    """Smooth-and-efficient zooming, van Wijk & Nuij 2003.

    Returns ``(S, sample)`` where ``S`` is the path length in the metric's own
    units — a *perceptual* length, so pacing off it gives far jumps more time
    than near ones without anyone tuning per-move durations — and ``sample(s)``
    for ``s`` in ``[0, S]`` is the view at that point along the path.
    """
    dx, dy = v1.cx - v0.cx, v1.cy - v0.cy
    u1 = math.hypot(dx, dy)
    w0, w1 = v0.w, v1.w

    if u1 < 1e-6:  # same place, different zoom: pure exponential interpolation
        if abs(math.log(w1 / w0)) < 1e-9:
            return 0.0, lambda s: v0
        k = 1.0 if w1 > w0 else -1.0
        S = abs(math.log(w1 / w0)) / rho

        def sample_zoom(s: float) -> View:
            return View(v0.cx, v0.cy, w0 * math.exp(k * rho * s))

        return S, sample_zoom

    b0 = (w1 * w1 - w0 * w0 + rho ** 4 * u1 * u1) / (2 * w0 * rho * rho * u1)
    r0 = math.log(-b0 + math.sqrt(b0 * b0 + 1))
    b1 = (w1 * w1 - w0 * w0 - rho ** 4 * u1 * u1) / (2 * w1 * rho * rho * u1)
    r1 = math.log(-b1 + math.sqrt(b1 * b1 + 1))
    S = (r1 - r0) / rho

    if S <= 1e-9:  # degenerate; fall back to a straight interpolation
        def sample_lerp(s: float) -> View:
            return View(v0.cx + dx, v0.cy + dy, w1)
        return 0.0, sample_lerp

    ux, uy = dx / u1, dy / u1
    cosh_r0, sinh_r0 = math.cosh(r0), math.sinh(r0)

    def sample(s: float) -> View:
        t = rho * s + r0
        u = w0 / (rho * rho) * (cosh_r0 * math.tanh(t) - sinh_r0)
        w = w0 * cosh_r0 / math.cosh(t)
        return View(v0.cx + ux * u, v0.cy + uy * u, w)

    return S, sample


def plan_move(v0: View, v1: View, img_w: int, img_h: int, aspect: float,
              *, rho: float = 1.42) -> tuple[float, Callable[[float], View]]:
    """A move between two views, with the pull-back capped at the whole poster.

    Left alone, van Wijk will happily zoom out past the edge of the paper on a
    long jump — the arc is drawn in an unbounded plane. Clamping every sampled
    frame instead would flatten the top of the arc into a dead stall at full
    poster. So the pull-back is tuned *before* sampling: ``rho`` is walked down
    until the peak fits the paper, which keeps the motion continuous and simply
    makes the arc shallower on jumps that could not afford a deep one.
    """
    max_w = min(img_w, img_h * aspect)
    lo, hi = 1.02, max(rho, 1.03)
    if _van_wijk_peak(v0.w, v1.w, math.hypot(v1.cx - v0.cx, v1.cy - v0.cy) or 1e-6,
                      hi) > max_w:
        for _ in range(24):  # bisect: peak grows monotonically with rho
            mid = (lo + hi) / 2
            peak = _van_wijk_peak(v0.w, v1.w,
                                  math.hypot(v1.cx - v0.cx, v1.cy - v0.cy) or 1e-6,
                                  mid)
            if peak > max_w:
                hi = mid
            else:
                lo = mid
        rho = lo
    S, sample = _van_wijk(v0, v1, rho)

    def clamped(s: float) -> View:
        return clamp_view(sample(s), img_w, img_h, aspect)

    return S, clamped


def ease_in_out(u: float) -> float:
    """Cubic ease. Applied over the path parameter, not over position.

    Easing position directly would fight van Wijk's constant-perceived-velocity
    guarantee; easing ``s`` keeps that property and only shapes departure and
    arrival.
    """
    return 4 * u * u * u if u < 0.5 else 1 - (-2 * u + 2) ** 3 / 2


# --------------------------------------------------------------------------
# The timeline
# --------------------------------------------------------------------------

@dataclass
class Leg:
    """One stretch of the timeline: a hold on a point, or a move between two."""
    kind: str                      # "hold" | "move"
    duration: float
    at: Callable[[float], View]    # u in [0,1] -> view
    label: str = ""
    audio: Path | None = None
    point: int = -1                # index into spec.points, for the glow
    start: float = 0.0             # filled in by build_timeline


def hold_leg(view: View, duration: float, motion: str, drift: float,
             img_w: int, img_h: int, aspect: float, *,
             label: str = "", audio: Path | None = None,
             point: int = -1) -> Leg:
    """A hold is never actually still.

    A frozen frame in the middle of a moving video reads as a stall or a
    dropped render. A hold creeps — a few percent of zoom over its whole
    length, linear in log space so it never appears to stop.
    """
    if motion == "still" or drift <= 0:
        v0 = v1 = view
    elif motion == "pull":
        v0, v1 = view, view.scaled(1 + drift)
    else:  # "push" — the default; settle inward on the point
        v0, v1 = view.scaled(1 + drift), view
    v0 = clamp_view(v0, img_w, img_h, aspect)
    v1 = clamp_view(v1, img_w, img_h, aspect)
    lw0, lw1 = math.log(v0.w), math.log(v1.w)

    def at(u: float) -> View:
        v = View(v0.cx + (v1.cx - v0.cx) * u,
                 v0.cy + (v1.cy - v0.cy) * u,
                 math.exp(lw0 + (lw1 - lw0) * u))
        return clamp_view(v, img_w, img_h, aspect)

    return Leg("hold", duration, at, label=label, audio=audio, point=point)


def move_leg(v0: View, v1: View, img_w: int, img_h: int, aspect: float,
             *, duration: float | None, speed: float, rho: float,
             min_t: float, max_t: float) -> Leg:
    S, sample = plan_move(v0, v1, img_w, img_h, aspect, rho=rho)
    if duration is None:
        # Pace off the perceptual path length, so a jump from point 1 to
        # point 5 is given more time than point 1 to point 2 on its own.
        duration = min(max(S / speed, min_t), max_t)
    if S <= 0:
        return Leg("move", duration, lambda u: v1)

    def at(u: float) -> View:
        return sample(ease_in_out(u) * S)

    return Leg("move", duration, at)


def build_timeline(legs: list[Leg]) -> list[Leg]:
    t = 0.0
    for leg in legs:
        leg.start = t
        t += leg.duration
    return legs


def view_at_time(legs: list[Leg], t: float) -> View:
    for leg in legs:
        if t < leg.start + leg.duration or leg is legs[-1]:
            u = 0.0 if leg.duration <= 0 else min(max((t - leg.start) / leg.duration, 0.0), 1.0)
            return leg.at(u)
    return legs[-1].at(1.0)  # pragma: no cover


# --------------------------------------------------------------------------
# The spec
# --------------------------------------------------------------------------

@dataclass
class Bookend:
    """A still held at the top or tail of the video, dissolving into it.

    It is not part of the camera timeline — the camera holds on its first (or
    last) frame while the still dissolves — so adding one never reshuffles the
    pacing of the points or the narration underneath them.
    """
    image: str
    hold: float = 1.6          # seconds at full opacity
    fade: float = 0.8          # seconds of dissolve
    fit: str = "contain"       # "contain" keeps all of it; "cover" fills


def bookend_frame(path: Path, size: tuple[int, int], fit: str) -> Image.Image:
    """The bookend still, fitted to the frame once and reused for every frame.

    `contain` never crops — which matters when the still is a photograph
    someone chose, where the thing that would get cut is exactly the thing
    they chose it for — and fills the leftover with the same blurred bed the
    letterboxed camera views use, so the two never look like different videos.
    """
    im = open_poster(path)
    W, H = size
    scale = (max if fit == "cover" else min)(W / im.width, H / im.height)
    nw, nh = max(1, round(im.width * scale)), max(1, round(im.height * scale))
    piece = im.resize((nw, nh), LANCZOS, reducing_gap=2.5)
    if (nw, nh) == (W, H):
        return piece
    if fit == "cover":
        ox, oy = (nw - W) // 2, (nh - H) // 2
        return piece.crop((ox, oy, ox + W, oy + H))

    small = im.copy()
    small.thumbnail((320, 320), LANCZOS)
    bed = small.filter(ImageFilter.GaussianBlur(14)).point(lambda v: int(v * 0.45))
    bs = max(W / bed.width, H / bed.height)
    bed = bed.resize((max(1, round(bed.width * bs)), max(1, round(bed.height * bs))),
                     Image.BILINEAR)
    ox, oy = (bed.width - W) // 2, (bed.height - H) // 2
    frame = bed.crop((ox, oy, ox + W, oy + H))
    frame.paste(piece, ((W - nw) // 2, (H - nh) // 2))
    return frame


@dataclass
class Music:
    """A bed under the whole video, trimmed to it rather than the other way round.

    `gain` is in dB and defaults low: a bed that competes with narration is
    not a bed. `fade_out` matters more than it looks — a track cut dead on the
    last frame reads as the video having been chopped, so the tail is always
    faded even when the fade eats into the closing still.
    """
    path: str
    gain: float = -4.0
    start: float = 0.0         # seconds into the track to begin
    fade_in: float = 0.8
    fade_out: float = 2.0
    loop: bool = True          # repeat if the track is shorter than the video


@dataclass
class Point:
    rect: tuple[float, float, float, float]   # fractions of the image, (x,y,w,h)
    label: str = ""
    dwell: float | None = None
    transition: float | None = None
    zoom: float = 1.0
    motion: str = "push"
    audio: str | None = None
    glow: bool = True


@dataclass
class Spec:
    points: list[Point]
    width: int = 1080
    height: int = 1920
    fps: int = 30
    dwell: float = 3.0
    transition: float | None = None    # None = pace it off the distance
    speed: float = 1.6                 # van Wijk units per second
    min_transition: float = 0.55
    max_transition: float = 1.9
    rho: float = 1.42
    pad: float = 1.08
    drift: float = 0.05                # zoom creep across a hold
    open_full: float = 1.6             # establishing shot, seconds (0 = none)
    close_full: float = 1.6            # closing pull-out, seconds (0 = none)
    audio_pad: float = 0.35            # silence after a point's narration
    glow: Glow = field(default_factory=Glow)
    intro: Bookend | None = None
    outro: Bookend | None = None
    music: Music | None = None

    @property
    def aspect(self) -> float:
        return self.width / self.height


def load_spec(path: Path) -> Spec:
    raw = _read_structured(path)
    if isinstance(raw, list):
        raw = {"points": raw}
    if not isinstance(raw, dict):
        raise PosterError(f"{path}: expected an object or a list of points")
    pts_raw = raw.pop("points", None)
    if not pts_raw:
        raise PosterError(f"{path}: no 'points'")
    out = raw.pop("output", None)
    if isinstance(out, dict):
        raw.update(out)
    raw.pop("image", None)
    glow_raw = raw.pop("glow", None)
    if glow_raw is False:
        glow = Glow(enabled=False)
    elif isinstance(glow_raw, dict):
        unknown = set(glow_raw) - set(Glow.__dataclass_fields__)
        if unknown:
            raise PosterError(f"{path}: unknown glow settings {sorted(unknown)}")
        glow = Glow(**glow_raw)
    elif glow_raw is None or glow_raw is True:
        glow = Glow()
    else:
        raise PosterError(f"{path}: 'glow' must be an object or a boolean")
    def _bookend(raw_v, which):
        if raw_v is None:
            return None
        if isinstance(raw_v, str):
            return Bookend(image=raw_v)
        if isinstance(raw_v, dict):
            unknown = set(raw_v) - set(Bookend.__dataclass_fields__)
            if unknown:
                raise PosterError(f"{path}: unknown {which} settings {sorted(unknown)}")
            if "image" not in raw_v:
                raise PosterError(f"{path}: {which} needs an 'image'")
            return Bookend(**raw_v)
        raise PosterError(f"{path}: '{which}' must be a path or an object")

    intro = _bookend(raw.pop("intro", None), "intro")
    outro = _bookend(raw.pop("outro", None), "outro")

    music_raw = raw.pop("music", None)
    if music_raw is None:
        music = None
    elif isinstance(music_raw, str):
        music = Music(path=music_raw)
    elif isinstance(music_raw, dict):
        unknown = set(music_raw) - set(Music.__dataclass_fields__)
        if unknown:
            raise PosterError(f"{path}: unknown music settings {sorted(unknown)}")
        if "path" not in music_raw:
            raise PosterError(f"{path}: music needs a 'path'")
        music = Music(**music_raw)
    else:
        raise PosterError(f"{path}: 'music' must be a path or an object")
    points = []
    for i, p in enumerate(pts_raw, 1):
        if isinstance(p, (list, tuple)):
            p = {"rect": list(p)}
        rect = p.get("rect") or p.get("box")
        if not rect or len(rect) != 4:
            raise PosterError(f"point {i}: needs rect [x, y, w, h]")
        points.append(Point(
            rect=tuple(float(v) for v in rect),
            label=str(p.get("label", "") or ""),
            dwell=_opt_float(p.get("dwell")),
            transition=_opt_float(p.get("transition")),
            zoom=float(p.get("zoom", 1.0)),
            motion=str(p.get("motion", "push")),
            audio=p.get("audio"),
            glow=bool(p.get("glow", True)),
        ))
    known = {f for f in Spec.__dataclass_fields__
             if f not in {"points", "glow", "intro", "outro", "music"}}
    unknown = set(raw) - known
    if unknown:
        raise PosterError(f"{path}: unknown settings {sorted(unknown)}")
    return Spec(points=points, glow=glow, intro=intro, outro=outro,
                music=music, **{k: raw[k] for k in raw})


def _opt_float(v):
    return None if v is None else float(v)


def _read_structured(path: Path):
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in {".yaml", ".yml"}:
        try:
            import yaml
        except ModuleNotFoundError as exc:
            raise PosterError("YAML spec needs pyyaml; use JSON instead") from exc
        return yaml.safe_load(text)
    return json.loads(text)


# --------------------------------------------------------------------------
# Spec -> timeline
# --------------------------------------------------------------------------

def audio_duration(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", str(path)],
        capture_output=True, text=True, check=True).stdout.strip()
    return float(out)


def build_legs(spec: Spec, img_w: int, img_h: int, *,
               base_dir: Path = Path(".")) -> list[Leg]:
    aspect = spec.aspect
    whole = full_view(img_w, img_h, aspect)
    views, holds, audios = [], [], []
    for p in spec.points:
        x, y, w, h = p.rect
        px = (x * img_w, y * img_h, w * img_w, h * img_h)
        views.append(fit_view(px, img_w, img_h, aspect, pad=spec.pad, zoom=p.zoom))
        audio = None
        dwell = p.dwell if p.dwell is not None else spec.dwell
        if p.audio:
            audio = (base_dir / p.audio) if not Path(p.audio).is_absolute() else Path(p.audio)
            if not audio.exists():
                raise PosterError(f"missing narration for '{p.label}': {audio}")
            # Narration sets the clock, exactly as it does everywhere else here.
            dwell = audio_duration(audio) + spec.audio_pad
        holds.append(dwell)
        audios.append(audio)

    legs: list[Leg] = []
    cursor = None
    if spec.open_full > 0:
        legs.append(hold_leg(whole, spec.open_full, "push", spec.drift * 0.6,
                             img_w, img_h, aspect, label="(whole poster)"))
        cursor = legs[-1].at(1.0)

    for i, (p, v, dwell, audio) in enumerate(zip(spec.points, views, holds, audios)):
        hold = hold_leg(v, dwell, p.motion, spec.drift, img_w, img_h, aspect,
                        label=p.label or f"point {i + 1}", audio=audio, point=i)
        if cursor is not None:
            legs.append(move_leg(cursor, hold.at(0.0), img_w, img_h, aspect,
                                 duration=(p.transition if p.transition is not None
                                           else spec.transition),
                                 speed=spec.speed, rho=spec.rho,
                                 min_t=spec.min_transition, max_t=spec.max_transition))
        legs.append(hold)
        cursor = hold.at(1.0)

    if spec.close_full > 0 and cursor is not None:
        legs.append(move_leg(cursor, whole, img_w, img_h, aspect,
                             duration=spec.transition, speed=spec.speed,
                             rho=spec.rho, min_t=spec.min_transition,
                             max_t=spec.max_transition))
        legs.append(hold_leg(whole, spec.close_full, "pull", spec.drift * 0.6,
                             img_w, img_h, aspect, label="(whole poster)"))
    return build_timeline(legs)


# --------------------------------------------------------------------------
# Does this poster actually fit the frame you asked for?
# --------------------------------------------------------------------------

# Aspects worth suggesting, widest last.
_CANDIDATES = [("9:16", 1080, 1920), ("4:5", 1080, 1350), ("1:1", 1080, 1080),
               ("4:3", 1440, 1080), ("16:9", 1920, 1080)]


def _magnification(rect, img_w, img_h, out_w, out_h, pad, zoom):
    """Output pixels per image pixel for this region in this frame, and how
    much of the region's width the frame cannot hold."""
    aspect = out_w / out_h
    x, y, w, h = rect[0] * img_w, rect[1] * img_h, rect[2] * img_w, rect[3] * img_h
    want = max(w, h * aspect) * pad * zoom
    view_w = min(want, contain_width(img_w, img_h, aspect))
    bars = max(0.0, 1.0 - (img_h * aspect) / view_w)   # share of frame width in bars
    return out_w / view_w, bars


def fit_report(spec: Spec, img_w: int, img_h: int) -> tuple[list[str], list[str]]:
    """Warnings, and suggestions for a frame shape that would do better.

    A region wider than the frame can hold is silently side-cropped by
    ``clamp_view`` — it has to be, the alternative is letterboxing — and a
    region that is very wide and short forces a view so tall that the "zoom"
    magnifies nothing. Both fail quietly and look like a rendering bug rather
    than a geometry one, so they are said out loud here instead.
    """
    warn: list[str] = []
    base_mag = spec.width / contain_width(img_w, img_h, spec.aspect)
    for i, p in enumerate(spec.points):
        label = p.label or f"point {i + 1}"
        mag, bars = _magnification(p.rect, img_w, img_h, spec.width, spec.height,
                                   spec.pad, p.zoom)
        # Absolute magnification is the wrong yardstick: what matters is
        # whether the camera moves IN relative to the establishing shot. A
        # point at 1.27x next to a whole-poster shot at 1.27x has not zoomed
        # at all, and reporting "1.27x" would suggest it had.
        if mag < base_mag * 1.15:
            warn.append(f"{label}: {mag:.2f}x against {base_mag:.2f}x for the "
                        f"whole poster — the camera does not move in on it")
        elif bars > 0.06:
            warn.append(f"{label}: {bars * 100:.0f}% of the frame is bars")

    tips: list[str] = []
    if warn:
        scored = []
        for name, ow, oh in _CANDIDATES:
            base = ow / contain_width(img_w, img_h, ow / oh)
            worst = min((_magnification(p.rect, img_w, img_h, ow, oh, spec.pad,
                                        p.zoom)[0] / base for p in spec.points),
                        default=0.0)
            base = ow / contain_width(img_w, img_h, ow / oh)
            weak = sum(1 for p in spec.points
                       if _magnification(p.rect, img_w, img_h, ow, oh, spec.pad,
                                         p.zoom)[0] < base * 1.15)
            scored.append((weak, -worst, name, ow, oh, worst))
        scored.sort()
        weak, _, name, ow, oh, worst = scored[0]
        tips.append(f"{ow}x{oh} ({name}): weakest point still gets {worst:.2f}x "
                    f"more than the whole-poster shot"
                    f"{'' if not weak else f', {weak} point(s) still flat'}")
    return warn, tips


# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------

def open_poster(path: Path) -> Image.Image:
    img = Image.open(path)
    img = ImageOps.exif_transpose(img)
    if img.mode != "RGB":
        img = img.convert("RGB")
    return img


def place(view: View, img_w: int, img_h: int, size: tuple[int, int],
          aspect: float):
    """Where the paper lands in the frame.

    Returns ``(src_box, dest_box)`` — the part of the image that is visible,
    and the integer rectangle of the frame it fills — or ``None`` if the view
    has left the paper entirely. Everything that has to line up with the
    artwork goes through here, so a letterboxed frame and the mask drawn over
    it cannot disagree about where the poster is.
    """
    W, H = size
    x0, y0, x1, y1 = view.box(aspect)
    s = W / view.w
    ix0, iy0 = max(0.0, x0), max(0.0, y0)
    ix1, iy1 = min(float(img_w), x1), min(float(img_h), y1)
    if ix1 - ix0 < 1 or iy1 - iy0 < 1:
        return None
    dest = (max(0, int(round((ix0 - x0) * s))),
            max(0, int(round((iy0 - y0) * s))),
            min(W, int(round((ix1 - x0) * s))),
            min(H, int(round((iy1 - y0) * s))))
    return (ix0, iy0, ix1, iy1), dest


def crop_frame(img: Image.Image, view: View, size: tuple[int, int],
               aspect: float,
               backdrop: Callable[[View], Image.Image] | None = None
               ) -> Image.Image:
    """The frame the camera sees, letterboxed if the view runs off the paper.

    A float box is the whole reason this is Pillow and not ffmpeg's `zoompan`:
    the crop moves sub-pixel, so text does not shimmer as the camera creeps.
    `reducing_gap` makes the big early downscales cheap without visible loss.
    """
    W, H = size
    spot = place(view, img.width, img.height, size, aspect)
    if spot is None:
        return Image.new("RGB", size, (12, 12, 14))
    src, (dx0, dy0, dx1, dy1) = spot
    if (dx0, dy0, dx1, dy1) == (0, 0, W, H):
        return img.resize(size, LANCZOS, box=src, reducing_gap=2.5)

    # Pillow will not resample from outside the image, so the visible part is
    # resampled on its own and placed where it belongs on the backdrop.
    piece = img.resize((max(1, dx1 - dx0), max(1, dy1 - dy0)), LANCZOS,
                       box=src, reducing_gap=2.5)
    frame = backdrop(view) if backdrop else Image.new("RGB", size, (12, 12, 14))
    frame.paste(piece, (dx0, dy0))
    return frame


class Camera:
    """The poster, the path across it, and the glow that says where we are.

    Everything that has to agree between a still and a rendered frame lives
    here — the timeline, the sprites, the glow envelope — so a still is
    literally `camera.frame(t)` at the middle of a hold, not a second code
    path that drifts out of step with the video.
    """

    def __init__(self, image: Path, spec: Spec, *, base_dir: Path | None = None):
        self.spec = spec
        self.image = image
        self.img = open_poster(image)
        self.legs = build_legs(spec, self.img.width, self.img.height,
                               base_dir=base_dir or image.parent)
        self.total = sum(l.duration for l in self.legs)
        self.spans: dict[int, tuple[float, float]] = {
            leg.point: (leg.start, leg.start + leg.duration)
            for leg in self.legs if leg.kind == "hold" and leg.point >= 0
        }
        # The bars behind a letterboxed view are filled with a blurred,
        # darkened enlargement of the poster itself, cover-fitted and tracking
        # the same centre — flat black bars read as a mistake, this reads as a
        # choice. Built once from a small copy: blur is cheap at 320px and
        # upscaling a blur is indistinguishable from blurring at full size.
        small = self.img.copy()
        small.thumbnail((320, 320), LANCZOS)
        self._bed = small.filter(ImageFilter.GaussianBlur(14)).point(
            lambda v: int(v * 0.45))
        self._bed_scale = self._bed.width / self.img.width

        base = base_dir or image.parent
        self._intro_img = self._bookend(spec.intro, base)
        self._outro_img = self._bookend(spec.outro, base)

        self.sprites: dict[int, tuple[Image.Image, float, float]] = {}
        self.dims: dict[int, Image.Image] = {}
        if spec.glow.enabled:
            for i, pt in enumerate(spec.points):
                if i in self.spans and pt.glow:
                    self.sprites[i] = build_glow_sprite(
                        pt.rect, self.img.width, self.img.height, spec.glow)
                    if spec.glow.dim > 0:
                        self.dims[i] = build_dim_mask(
                            pt.rect, self.img.width, self.img.height, spec.glow)

    def glow_alpha(self, i: int, t: float) -> float:
        """How lit point ``i`` is at time ``t``.

        It rises during the move that is still on its way there. Arriving on a
        card that lights up only once the camera has stopped reads as a
        delayed reaction; arriving on one already lit reads as intent.
        """
        span = self.spans.get(i)
        if span is None:
            return 0.0
        g = self.spec.glow
        h0, h1 = span
        fade = max(g.fade, 1e-6)
        if t < h0 - fade or t > h1 + fade:
            return 0.0
        if t < h0:
            a = _smoothstep((t - (h0 - fade)) / fade)
        elif t <= h1:
            a = 1.0
        else:
            a = _smoothstep(1.0 - (t - h1) / fade)
        a *= g.opacity
        if g.pulse > 0:
            a *= 1.0 - g.pulse * 0.5 * (1.0 - math.cos(2 * math.pi * g.pulse_hz * t))
        return min(max(a, 0.0), 1.0)

    def backdrop(self, view: View) -> Image.Image:
        """A blurred cover-crop of the poster behind the bars."""
        aspect = self.spec.aspect
        cover = clamp_view(View(view.cx, view.cy,
                                min(self.img.width, self.img.height * aspect)),
                           self.img.width, self.img.height, aspect)
        k = self._bed_scale
        x0, y0, x1, y1 = cover.box(aspect)
        box = (max(0.0, x0 * k), max(0.0, y0 * k),
               min(float(self._bed.width), x1 * k),
               min(float(self._bed.height), y1 * k))
        return self._bed.resize((self.spec.width, self.spec.height),
                                Image.BILINEAR, box=box)

    def frame(self, t: float) -> Image.Image:
        view = view_at_time(self.legs, t)
        out = crop_frame(self.img, view, (self.spec.width, self.spec.height),
                         self.spec.aspect, backdrop=self.backdrop)
        lit = [(i, a) for i in self.sprites
               if (a := self.glow_alpha(i, t)) > 0.004]
        if self.dims and lit:
            out = self._spotlight(out, view, lit)
        for i, a in lit:
            sprite, sx0, sy0 = self.sprites[i]
            screen_sprite(out, sprite, sx0, sy0, view, self.spec.aspect, a)
        return out

    def _spotlight(self, out: Image.Image, view: View,
                   lit: list[tuple[int, float]]) -> Image.Image:
        """Darken everything the camera is not currently reading.

        The mask is poster-shaped, so on a letterboxed view it covers only the
        part of the frame the poster occupies and the bars stay dark — which
        is what you want, and is why this goes through the same `place` the
        frame itself did rather than deciding the geometry a second time.
        """
        size = (self.spec.width, self.spec.height)
        spot = place(view, self.img.width, self.img.height, size,
                     self.spec.aspect)
        if spot is None:
            return out
        src, (dx0, dy0, dx1, dy1) = spot
        mask = None
        for i, a in lit:
            m = self.dims.get(i)
            if m is None:
                continue
            m = m.resize((max(1, dx1 - dx0), max(1, dy1 - dy0)),
                         Image.BILINEAR, box=src)
            if a < 0.999:
                m = m.point(lambda v, k=a: int(v * k))
            mask = m if mask is None else ImageChops.lighter(mask, m)
        if mask is None:
            return out
        if (dx0, dy0, dx1, dy1) != (0, 0, size[0], size[1]):
            full = Image.new("L", size, 0)
            full.paste(mask, (dx0, dy0))
            mask = full
        k = 1.0 - min(max(self.spec.glow.dim, 0.0), 0.95)
        return Image.composite(out, out.point(lambda v: int(v * k)), mask)

    # -- bookends ---------------------------------------------------------

    def _bookend(self, b: Bookend | None, base_dir: Path) -> Image.Image | None:
        if b is None:
            return None
        # A bookend named in a spec file is relative to that file; one typed
        # on the command line is relative to where it was typed. Trying the
        # literal path first satisfies both without the caller declaring which.
        path = Path(b.image)
        if not path.exists() and not path.is_absolute():
            path = base_dir / b.image
        if not path.exists():
            raise PosterError(f"bookend image not found: {b.image}")
        return bookend_frame(path, (self.spec.width, self.spec.height), b.fit)

    @property
    def lead_in(self) -> float:
        """How long the video runs before the camera's clock starts."""
        b = self.spec.intro
        return 0.0 if b is None else b.hold + b.fade

    @property
    def duration(self) -> float:
        out = self.spec.outro
        return (self.lead_in + self.total
                + (0.0 if out is None else out.fade + out.hold))

    def full_frame(self, t: float) -> Image.Image:
        """A frame of the finished video, bookends included.

        The camera is *held*, not advanced, under a dissolve. Running it
        during the fade would mean the poster is already moving while it is
        still half-transparent, which reads as a glitch rather than an entry.
        """
        intro, outro = self.spec.intro, self.spec.outro
        if intro is not None:
            if t < intro.hold:
                return self._intro_img.copy()
            if t < intro.hold + intro.fade:
                u = _smoothstep((t - intro.hold) / max(intro.fade, 1e-6))
                return Image.blend(self._intro_img, self.frame(0.0), u)
        body_t = t - self.lead_in
        if body_t < self.total or outro is None:
            return self.frame(min(max(body_t, 0.0), self.total))
        tail = body_t - self.total
        if tail < outro.fade:
            u = _smoothstep(tail / max(outro.fade, 1e-6))
            return Image.blend(self.frame(self.total), self._outro_img, u)
        return self._outro_img.copy()

    def hold_times(self) -> list[tuple[Leg, float]]:
        """Each hold and the moment inside it that best represents it."""
        return [(leg, leg.start + leg.duration / 2)
                for leg in self.legs if leg.kind == "hold"]


def render(image: Path, spec: Spec, out: Path, *, base_dir: Path | None = None,
           quiet: bool = False) -> Path:
    if not shutil.which("ffmpeg"):
        raise PosterError("ffmpeg not on PATH")
    cam = Camera(image, spec, base_dir=base_dir or image.parent)
    warn, tips = fit_report(spec, cam.img.width, cam.img.height)
    for w in warn:
        print(f"  ! {w}", file=sys.stderr)
    for t in tips:
        print(f"  > try {t}", file=sys.stderr)
    n_frames = max(1, int(round(cam.duration * spec.fps)))
    out.parent.mkdir(parents=True, exist_ok=True)

    silent = out.with_suffix(".silent.mp4")
    cmd = ["ffmpeg", "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{spec.width}x{spec.height}", "-r", str(spec.fps), "-i", "-",
           "-c:v", "libx264", "-preset", "medium", "-crf", "18",
           "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(silent)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    try:
        for i in range(n_frames):
            proc.stdin.write(cam.full_frame(i / spec.fps).tobytes())
            if not quiet and (i % (spec.fps * 2) == 0 or i == n_frames - 1):
                pct = 100 * (i + 1) / n_frames
                print(f"\r  frame {i + 1}/{n_frames}  {pct:5.1f}%", end="", flush=True)
    finally:
        proc.stdin.close()
        rc = proc.wait()
    if not quiet:
        print()
    if rc != 0:
        raise PosterError(f"ffmpeg exited {rc}")

    # Narration is laid against the CAMERA clock, so it shifts with the
    # intro rather than starting under it.
    narration = [(l.start + cam.lead_in, l.audio) for l in cam.legs if l.audio]
    if narration or spec.music is not None:
        mux_audio(silent, out, cam.duration, narration=narration,
                  music=spec.music, base_dir=base_dir or image.parent)
        silent.unlink(missing_ok=True)
    else:
        silent.replace(out)
    return out


def resolve_asset(name: str, base_dir: Path) -> Path:
    """A path from a spec or a command line, whichever it was.

    Same rule as the bookends: try it literally first, then relative to the
    spec. Saves the caller from declaring which kind of path they hold.
    """
    path = Path(name).expanduser()
    if not path.exists() and not path.is_absolute():
        path = base_dir / name
    if not path.exists():
        raise PosterError(f"audio file not found: {name}")
    return path


def mux_audio(video: Path, out: Path, total: float, *,
              narration: list[tuple[float, Path]] | None = None,
              music: Music | None = None,
              base_dir: Path = Path(".")) -> Path:
    """Lay narration at each point's hold, and music under the whole thing.

    The bed is trimmed to the video, never the video to the bed, and it is
    always faded out — a track that stops dead on the last frame reads as a
    truncated file rather than an ending.
    """
    narration = narration or []
    if not narration and music is None:
        raise PosterError("nothing to mux")

    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", str(video)]
    parts, labels = [], []

    for i, (start, path) in enumerate(narration, start=1):
        cmd += ["-i", str(path)]
        parts.append(f"[{i}:a]aresample=48000,adelay={int(start * 1000)}"
                     f":all=1[a{i}]")
        labels.append(f"[a{i}]")

    if music is not None:
        idx = len(narration) + 1
        track = resolve_asset(music.path, base_dir)
        # -stream_loop repeats a bed shorter than the video; -ss picks the
        # section. Both are INPUT options, so they must precede -i.
        if music.loop:
            cmd += ["-stream_loop", "-1"]
        if music.start > 0:
            cmd += ["-ss", f"{music.start:.3f}"]
        cmd += ["-i", str(track)]
        fo = min(music.fade_out, total)
        chain = [f"[{idx}:a]aresample=48000",
                 f"atrim=0:{total:.3f}", "asetpts=N/SR/TB",
                 f"volume={music.gain:.2f}dB"]
        if music.fade_in > 0:
            chain.append(f"afade=t=in:st=0:d={music.fade_in:.3f}")
        if fo > 0:
            chain.append(f"afade=t=out:st={max(0.0, total - fo):.3f}:d={fo:.3f}")
        parts.append(",".join(chain) + "[mus]")
        labels.append("[mus]")

    if len(labels) == 1:
        parts.append(f"{labels[0]}apad,atrim=0:{total:.3f}[aout]")
    else:
        parts.append("".join(labels) +
                     f"amix=inputs={len(labels)}:normalize=0:dropout_transition=0,"
                     f"apad,atrim=0:{total:.3f}[aout]")

    cmd += ["-filter_complex", ";".join(parts), "-map", "0:v", "-map", "[aout]",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            "-movflags", "+faststart", str(out)]
    subprocess.run(cmd, check=True)
    return out


def write_stills(image: Path, spec: Spec, out_dir: Path) -> list[Path]:
    """One frame per point, so framing is checked before a full render.

    These are real frames off the real timeline — same crop, same glow — so
    what you approve here is what the video shows. Thirty seconds of encoding
    to discover that point 3 is cropped through the middle of a word is the
    expensive way to find out.
    """
    cam = Camera(image, spec, base_dir=image.parent)
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for n, (leg, t) in enumerate(cam.hold_times(), start=1):
        slug = "".join(c if c.isalnum() else "-" for c in leg.label)[:40].strip("-")
        path = out_dir / f"{n:02d}-{slug or 'view'}.png"
        cam.frame(t).save(path)
        written.append(path)
    return written


def contact_sheet(stills: list[Path], out: Path, *, cols: int = 4,
                  cell: int = 380, gap: int = 14) -> Path:
    """All the stills on one page, because that is how framing is judged.

    Flipping between eight PNGs hides the thing you actually need to see —
    whether the crops are consistent with each other.
    """
    if not stills:
        raise PosterError("no stills to lay out")
    thumbs = []
    for s in stills:
        im = Image.open(s)
        im.thumbnail((cell, cell), LANCZOS)
        thumbs.append(im)
    cw = max(t.width for t in thumbs)
    ch = max(t.height for t in thumbs)
    rows = math.ceil(len(thumbs) / cols)
    sheet = Image.new("RGB", (cols * cw + (cols + 1) * gap,
                              rows * ch + (rows + 1) * gap), (24, 24, 28))
    for i, t in enumerate(thumbs):
        r, c = divmod(i, cols)
        sheet.paste(t, (gap + c * (cw + gap) + (cw - t.width) // 2,
                        gap + r * (ch + gap) + (ch - t.height) // 2))
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out)
    return out


def describe(image: Path, spec: Spec) -> str:
    cam = Camera(image, spec, base_dir=image.parent)
    lines = [f"{image.name}  {cam.img.width}x{cam.img.height}  ->  "
             f"{spec.width}x{spec.height} @ {spec.fps}fps"]
    if spec.intro is not None:
        lines.append(f"    0.00s  {spec.intro.hold:5.2f}s  still  "
                     f"     {Path(spec.intro.image).name}")
        lines.append(f"  {spec.intro.hold:6.2f}s  {spec.intro.fade:5.2f}s  fade "
                     f"      into the poster")
    off = cam.lead_in
    for leg in cam.legs:
        v = leg.at(0.5)
        mag = spec.width / v.w
        lines.append(f"  {leg.start + off:6.2f}s  {leg.duration:5.2f}s  "
                     f"{leg.kind:5}  {mag:4.2f}x  {leg.label or '->'}")
    if spec.outro is not None:
        lines.append(f"  {off + cam.total:6.2f}s  {spec.outro.fade:5.2f}s  fade "
                     f"      out to {Path(spec.outro.image).name}")
        lines.append(f"  {off + cam.total + spec.outro.fade:6.2f}s  "
                     f"{spec.outro.hold:5.2f}s  still")
    lines.append(f"  {cam.duration:6.2f}s  total")
    warn, tips = fit_report(spec, cam.img.width, cam.img.height)
    for w in warn:
        lines.append(f"  ! {w}")
    for t in tips:
        lines.append(f"  > try {t}")
    return "\n".join(lines)


# --------------------------------------------------------------------------
# Finding the points automatically
# --------------------------------------------------------------------------

_DETECT_SYSTEM = """You read a poster or infographic and report where its
content sits, so a camera can be pointed at each part in turn.

Return one entry per distinct teaching unit — a numbered point, a step, a
labelled diagram, a heading block. Merge a point's number, its heading and its
body text into ONE box: they are read together. Do not return a box per line.

Boxes are [x, y, w, h] as FRACTIONS of the image, 0..1, x/y at the top-left
corner. Be generous: include the number/bullet and any icon that belongs to the
point. Order the entries in reading order.

The label is a short plain description of what that region says. It is never
shown to a viewer; it is for a human checking the framing."""


def detect_points(image: Path, count: int | None = None, *,
                  provider: str | None = None) -> list[Point]:
    """Ask a vision model where the poster's points are."""
    from pydantic import BaseModel, Field

    class _Box(BaseModel):
        label: str = Field(description="short description of this region")
        rect: list[float] = Field(description="[x, y, w, h] as fractions 0..1")

    class _Boxes(BaseModel):
        regions: list[_Box]

    from src import llm
    ask = ("Find the teaching units on this poster and give me a box for each."
           if count is None else
           f"Find the {count} main teaching units on this poster and give me a "
           f"box for each. Return exactly {count} regions.")
    res = llm.complete_json(_DETECT_SYSTEM, ask, _Boxes, images=[str(image)],
                            provider=provider)
    points = []
    for r in res.regions:
        if len(r.rect) != 4:
            continue
        x, y, w, h = (float(v) for v in r.rect)
        if max(x, y, w, h) > 1.5:      # model answered in 0..1000 or in pixels
            img = open_poster(image)
            scale_x = 1000.0 if max(x, w) <= 1000 else img.width
            scale_y = 1000.0 if max(y, h) <= 1000 else img.height
            x, w = x / scale_x, w / scale_x
            y, h = y / scale_y, h / scale_y
        points.append(Point(rect=(x, y, w, h), label=r.label))
    if not points:
        raise PosterError("the vision pass found no regions on this poster")
    return points


def spec_to_dict(spec: Spec, image: Path | None = None) -> dict:
    d: dict = {}
    if image is not None:
        d["image"] = image.name
    defaults = Spec(points=[])
    for f in Spec.__dataclass_fields__:
        if f == "points":
            continue
        if getattr(spec, f) != getattr(defaults, f):
            d[f] = getattr(spec, f)
    for name in ("intro", "outro"):
        b = getattr(spec, name)
        if b is not None:
            bdef = Bookend(image="")
            d[name] = {f: getattr(b, f) for f in Bookend.__dataclass_fields__
                       if f == "image" or getattr(b, f) != getattr(bdef, f)}
    if spec.music is not None:
        mdef = Music(path="")
        d["music"] = {f: getattr(spec.music, f) for f in Music.__dataclass_fields__
                      if f == "path" or getattr(spec.music, f) != getattr(mdef, f)}
    gdef = Glow()
    gd = {f: getattr(spec.glow, f) for f in Glow.__dataclass_fields__
          if getattr(spec.glow, f) != getattr(gdef, f)}
    if gd:
        d["glow"] = gd
    d["points"] = [
        {k: v for k, v in {
            "label": p.label,
            "rect": [round(c, 4) for c in p.rect],
            "dwell": p.dwell,
            "transition": p.transition,
            "zoom": p.zoom if p.zoom != 1.0 else None,
            "motion": p.motion if p.motion != "push" else None,
            "audio": p.audio,
            "glow": None if p.glow else False,
        }.items() if v is not None and v != ""}
        for p in spec.points
    ]
    return d


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def poster_size(image: Path, width: int = 1080) -> tuple[int, int]:
    """A frame the same shape as the poster, so nothing is cropped or barred.

    Rounded to even numbers because H.264 chroma subsampling needs them, and
    an odd height is rejected by the encoder rather than quietly fixed.
    """
    im = Image.open(image)
    im = ImageOps.exif_transpose(im)
    h = int(round(width * im.height / im.width))
    return (width - width % 2, h - h % 2)


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog="poster_zoom",
        description="Animate a still: hold on each region, glide to the next.")
    ap.add_argument("image", type=Path)
    ap.add_argument("--spec", type=Path, help="JSON/YAML file of points")
    ap.add_argument("--auto", nargs="?", type=int, const=0, metavar="N",
                    help="find the points with a vision pass (N = how many)")
    ap.add_argument("-o", "--out", type=Path, help="output .mp4")
    ap.add_argument("--write-spec", type=Path,
                    help="save the points as a spec file and stop")
    ap.add_argument("--stills", type=Path,
                    help="write one PNG per point to this directory and stop")
    ap.add_argument("--sheet", type=Path,
                    help="with --stills, also lay them out on one contact sheet")
    ap.add_argument("--plan", action="store_true",
                    help="print the timeline and stop")
    ap.add_argument("--size",
                    help="WxH, or 'poster' to match the image's own shape "
                         "(default 1080x1920)")
    ap.add_argument("--landscape", action="store_true", help="1920x1080")
    ap.add_argument("--fps", type=int)
    ap.add_argument("--dwell", type=float, help="seconds held on each point")
    ap.add_argument("--transition", type=float,
                    help="seconds per move (default: paced off the distance)")
    ap.add_argument("--pad", type=float, help="margin around a region, 1.08 default")
    ap.add_argument("--drift", type=float, help="zoom creep across a hold")
    ap.add_argument("--no-open", action="store_true", help="skip the establishing shot")
    ap.add_argument("--no-close", action="store_true", help="skip the closing pull-out")
    ap.add_argument("--no-glow", action="store_true",
                    help="do not light a border around the active point")
    ap.add_argument("--glow-color", help="border colour, #RRGGBB (default gold)")
    ap.add_argument("--glow-pulse", type=float,
                    help="how deeply the border breathes, 0..1 (default 0)")
    ap.add_argument("--dim", type=float,
                    help="darken everything outside the active point, 0..1")
    ap.add_argument("--intro", help="still to open on, dissolving into the video")
    ap.add_argument("--outro", help="still to close on")
    ap.add_argument("--bookend", help="one still used as both --intro and --outro")
    ap.add_argument("--bookend-hold", type=float,
                    help="seconds a bookend still is held (default 1.6)")
    ap.add_argument("--bookend-fade", type=float,
                    help="seconds of dissolve (default 0.8)")
    ap.add_argument("--bookend-fit", choices=["contain", "cover"],
                    help="contain keeps all of the still; cover fills the frame")
    ap.add_argument("--music", help="background track laid under the whole video")
    ap.add_argument("--music-gain", type=float,
                    help="dB, default -4 (negative is quieter)")
    ap.add_argument("--music-start", type=float,
                    help="seconds into the track to begin")
    ap.add_argument("--music-fade-in", type=float)
    ap.add_argument("--music-fade-out", type=float)
    ap.add_argument("--provider", help="llm backend for --auto")
    return ap


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    image: Path = args.image
    if not image.exists():
        print(f"no such image: {image}", file=sys.stderr)
        return 1

    if args.spec:
        spec = load_spec(args.spec)
        base_dir = args.spec.parent
    elif args.auto is not None:
        print("looking at the poster...", file=sys.stderr)
        pts = detect_points(image, args.auto or None, provider=args.provider)
        print(f"found {len(pts)} regions", file=sys.stderr)
        spec = Spec(points=pts)
        base_dir = image.parent
    else:
        print("need --spec FILE or --auto [N]", file=sys.stderr)
        return 1

    if args.landscape:
        spec.width, spec.height = 1920, 1080
    if args.size:
        if args.size.lower() == "poster":
            spec.width, spec.height = poster_size(image)
        else:
            try:
                w, h = args.size.lower().split("x")
                spec.width, spec.height = int(w), int(h)
            except ValueError:
                print(f"bad --size {args.size!r}, want WxH or 'poster'",
                      file=sys.stderr)
                return 1
    for name in ("fps", "dwell", "transition", "pad", "drift"):
        v = getattr(args, name)
        if v is not None:
            setattr(spec, name, v)
    if args.no_open:
        spec.open_full = 0.0
    if args.no_close:
        spec.close_full = 0.0
    if args.no_glow:
        spec.glow = replace(spec.glow, enabled=False)
    if args.glow_color:
        spec.glow = replace(spec.glow, color=args.glow_color)
    if args.glow_pulse is not None:
        spec.glow = replace(spec.glow, pulse=args.glow_pulse)
    if args.dim is not None:
        spec.glow = replace(spec.glow, dim=args.dim)

    if args.music:
        spec.music = Music(path=args.music)
    if spec.music is not None:
        for flag, field_name in (("music_gain", "gain"), ("music_start", "start"),
                                 ("music_fade_in", "fade_in"),
                                 ("music_fade_out", "fade_out")):
            v = getattr(args, flag)
            if v is not None:
                spec.music = replace(spec.music, **{field_name: v})

    for which in ("intro", "outro"):
        chosen = getattr(args, which) or args.bookend
        if chosen:
            setattr(spec, which, Bookend(image=chosen))
        b = getattr(spec, which)
        if b is not None:
            if args.bookend_hold is not None:
                b = replace(b, hold=args.bookend_hold)
            if args.bookend_fade is not None:
                b = replace(b, fade=args.bookend_fade)
            if args.bookend_fit:
                b = replace(b, fit=args.bookend_fit)
            setattr(spec, which, b)

    if args.write_spec:
        args.write_spec.write_text(
            json.dumps(spec_to_dict(spec, image), indent=2, ensure_ascii=False),
            encoding="utf-8")
        print(f"wrote {args.write_spec}")
        return 0
    if args.plan:
        print(describe(image, spec))
        return 0
    if args.stills:
        stills = write_stills(image, spec, args.stills)
        for p in stills:
            print(p)
        if args.sheet:
            print(contact_sheet(stills, args.sheet))
        return 0

    out = args.out or image.with_suffix(".zoom.mp4")
    print(describe(image, spec))
    render(image, spec, out, base_dir=base_dir)
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
