"""The split-screen panel: a generated clip on top, the presenter below a tear.

WHY A PANEL AT ALL
------------------
The older layout laid a Veo clip over the WHOLE frame and cut its top off
(`VEO_CUT`), so the clip had to be generated full-bleed and the parts of it that
mattered had to survive an arbitrary crop. They often did not: a 16:9 generation
squeezed into a near-square hole loses a quarter of its width, and the
composition Veo actually built is thrown away.

Here the panel takes the CLIP's shape instead. The clip is cropped centred to
the panel's aspect and laid in whole, a torn-paper divider closes the bottom of
it, and the presenter works below. Nothing of the clip is scaled away.

THE ONE PIECE OF ARITHMETIC WORTH KNOWING
-----------------------------------------
A 9:16 clip can NEVER fill a full-width panel that is less than the whole frame:
at 1080 wide it needs all 1920 rows. So "a 60/40 split" and "an uncropped
portrait clip" are not both achievable, and the panel is the thing that gives
way. 4:3 at 1080 wide is 810 rows — 42% of the frame — which leaves room for a
divider and a presenter who stays under half the screen.

THE AVATAR NEVER EXCEEDS HALF THE FRAME. That is a house rule, enforced here by
`avatar_limits` and again by the gates. His largest size is whatever the panel
and the paper leave him, minus clearance, and then capped.

THE PANEL'S TOP EDGE DISSOLVES INTO THE PLATE. With a margin above it, that edge
is visible, and a hard line between a generated clip's near-black field and the
teal plate reads as a pasted rectangle. `TOP_FADE` rows of alpha ramp remove it.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

FRAME_W, FRAME_H, FPS = 1080, 1920, 30

PANEL_AR = 4 / 3        # Flow's video generation offers only 16:9 and 9:16, so a
                        # 4:3 panel is reached by composing the subject inside the
                        # middle of a 16:9 frame and cropping to it centred.
TOP_MARGIN = 84         # plate showing above the panel
TOP_FADE = 150          # rows over which the panel dissolves into the plate
AVATAR_CAP = FRAME_H // 2       # HOUSE RULE: never more than half the screen
AVATAR_CLEAR = 60               # daylight between the paper and his head
AVATAR_SHRINK = 60              # smaller again while a panel is up

WIPE = 0.55             # seconds the rip takes to travel across
LEAD = 95               # px the rip runs AHEAD of what it reveals
SOFT = 26               # px of softness on the travelling edge
OVER = 40               # px the finished wipe reaches PAST the frame edge


SIDE_FADE = 80          # px each side, where a NARROW panel meets the plate


def geometry(clip_w: int, clip_h: int, *, panel_ar: float = PANEL_AR,
             top_margin: int = TOP_MARGIN, crop: tuple | None = None) -> dict:
    """Where everything sits, derived from the clip's own size.

    A PORTRAIT GENERATION DOES NOT GET CROPPED TO A LETTERBOX. Flow offers 16:9
    and 9:16, and which one comes back is not always the one the prompt asked
    for — the raisin clip was ordered 16:9 and arrived 720x1280. Cropping that
    centred to a full-width 16:9 panel keeps a 720x404 strip: 68% of the picture
    thrown away, and the tumbler cut through its rim and its base, which is
    exactly the failure this module was written to stop.

    So when the clip is TALLER than the panel's aspect, the panel narrows
    instead. The clip is fitted to the band's height, centred, and `panel_x`
    says where it starts; the divider and the top dissolve stay full width,
    because they belong to the FRAME and not to the picture. A narrow panel has
    two side edges a full-width one does not, so `SIDE_FADE` ramps them into the
    plate — without it the clip's own ground meets ours at a hard vertical line.

    `crop` is an explicit (x, y, w, h) into the source, for trimming dead space
    a generation left around the subject. It is given per beat rather than
    guessed, because "empty" is a judgement about the picture.
    """
    panel_h = int(round(FRAME_W / panel_ar)) // 2 * 2
    if crop:
        cx, cy, cw, ch = (int(v) for v in crop)
    else:
        cx = cy = 0
        cw, ch = clip_w, clip_h
    if cw * panel_h >= ch * FRAME_W:
        # WIDE ENOUGH: fill the frame's width and take a centred crop down to
        # the panel's aspect, which is the original behaviour.
        src_w = min(cw, int(round(ch * panel_ar))) // 2 * 2
        src_h = min(ch, int(round(cw / panel_ar))) // 2 * 2
        return {
            "panel_w": FRAME_W, "panel_h": panel_h, "panel_x": 0,
            "top": top_margin, "seam": top_margin + panel_h,
            "crop": (src_w, src_h, cx + (cw - src_w) // 2, cy + (ch - src_h) // 2),
            "fade": TOP_FADE, "side_fade": 0,
        }
    # TALLER THAN THE BAND: keep the whole picture and narrow the panel.
    panel_w = max(2, int(round(panel_h * cw / ch)) // 2 * 2)
    return {
        "panel_w": panel_w, "panel_h": panel_h,
        "panel_x": (FRAME_W - panel_w) // 2,
        "top": top_margin, "seam": top_margin + panel_h,
        "crop": (cw // 2 * 2, ch // 2 * 2, cx, cy),
        "fade": TOP_FADE, "side_fade": min(SIDE_FADE, panel_w // 3),
    }


def plate_band(plate: Path, g: dict, gen_w: int = 1920) -> Path:
    """The part of the background plate a PANEL clip is generated on.

    src/veo.py uploads the plate so the clip is built on the same picture Manim
    renders and can be cut into the middle of it invisibly. Under `full` that is
    the whole portrait plate, because the generated frame IS the video frame.
    Under `panel` it is not: the clip occupies rows `top`..`seam` and is
    generated in landscape, so uploading the portrait plate hands Veo a picture
    of a different shape showing mostly parts of the frame the clip never
    covers — and Flow fits it to the generation however it likes.

    So the band is cut out and scaled to the generation's size. The round trip
    (up here, back down in the compositor) costs a little grain and nothing
    else: the band is already the panel's aspect, and the panel's only hard
    edges are the frame's own sides.
    """
    from PIL import Image
    out = Path("assets/backgrounds/panel") / (
        f"{Path(plate).stem}_{g['top']}_{g['panel_h']}_{gen_w}.png")
    if out.is_file():
        return out
    out.parent.mkdir(parents=True, exist_ok=True)
    im = Image.open(plate).convert("RGB")
    band = im.crop((0, g["top"], im.width, g["top"] + g["panel_h"]))
    gen_h = int(round(gen_w * g["panel_h"] / g["panel_w"])) // 2 * 2
    band.resize((gen_w, gen_h), Image.LANCZOS).save(out)
    return out


def avatar_limits(paper_bottom: int) -> tuple[int, int]:
    """(height while a panel is up, largest height) — derived, then capped.

    Picking a size and checking it afterwards is how the presenter ended up
    overlapping the divider; this takes whatever the layout leaves instead.
    """
    largest = min(AVATAR_CAP, FRAME_H - paper_bottom - AVATAR_CLEAR)
    return max(1, largest - AVATAR_SHRINK), largest


def tear(seam: int, *, build: bool = True) -> Path:
    """The divider PNG for this seam, built on demand and then cached on disk."""
    png = Path(f"assets/dividers/paper_tear_{seam}.png")
    if build and not png.is_file():
        subprocess.run([sys.executable, "tools/make_tear.py", "--seam", str(seam)],
                       check=True)
    return png


def fade_mask(panel_h: int, *, build: bool = True) -> Path:
    """The panel's top-edge fade, as a cached picture rather than an expression."""
    png = Path(f"assets/dividers/panel_fade_{panel_h}.png")
    if build and not png.is_file():
        subprocess.run([sys.executable, "tools/make_tear.py", "--fade-only",
                        "--fade-for", str(panel_h), "--fade-rows", str(TOP_FADE)],
                       check=True)
    return png


def tear_band(seam: int) -> tuple[int, int]:
    """(top row, height) the divider image actually occupies.

    The rip travels across on a per-pixel expression, and running that over a
    full 1080x1920 canvas evaluates eleven transparent pixels for every one that
    matters. Only this band is passed to it.
    """
    import json
    meta = json.loads(tear(seam).with_suffix(".json").read_text(encoding="utf-8"))
    return tuple(meta.get("band", (0, FRAME_H)))


def wipe_expr(start: float, end: float, lead: int = 0) -> str:
    """Alpha multiplier for the rip travelling across, in geq's variables.

    The wipe lives INSIDE the clip's own window: it opens over the first `WIPE`
    seconds and closes over the last, so a beat never bleeds past its slot.

    OVERSHOOT is not decoration. Without it a finished wipe stops `lead + SOFT`
    pixels short of the frame edge, and the plate shows through down both sides
    for the whole shot — which is exactly what the first cut did. The lead rides
    the travelling threshold rather than being subtracted from X, or the closing
    side starts already-closed at x=0.
    """
    draw = f"clip((T-{start:.3f})/{WIPE},0,1)"
    erase = f"clip((T-{max(start, end - WIPE):.3f})/{WIPE},0,1)"
    span = FRAME_W + lead + OVER
    return (f"clip((({span}*{draw})-{lead}-X)/{SOFT},0,1)"
            f"*clip((X-(({span}*{erase})-{lead}))/{SOFT},0,1)")


def side_expr(g: dict) -> str:
    """Alpha multiplier for a NARROW panel's two side edges, in geq's X.

    Zero outside the panel, ramping in over `side_fade` px each side. A
    full-width panel has no such edges and returns a constant 1, so the caller
    does not have to care which kind it has. Like the rip this is a function of
    X alone, so it multiplies into the same one-row mask and costs nothing.
    """
    f = int(g.get("side_fade") or 0)
    if not f:
        return "1"
    x0 = int(g.get("panel_x", 0))
    x1 = x0 + int(g["panel_w"])
    return f"clip((X-{x0})/{f},0,1)*clip(({x1}-X)/{f},0,1)"
