"""Generate and render one Manim scene per dialogue segment, with a
render-repair loop.

Pipeline per segment:
  1. Ask Claude for a ``SegmentScene(ThemedScene)`` class (class body only).
  2. Compose a full file: generated header (theme/orientation/chroma + Manim
     config)  +  the fixed manim_helpers scaffolding  +  the model's class.
  3. Syntax-check, then render at the target orientation.
  4. On any failure (syntax OR render traceback), feed the error back into the
     same conversation and regenerate — up to ``max_attempts``.

Backgrounds, chroma zones, safe-area math and color helpers all come from the
injected scaffolding, so the model only writes the animation itself.
"""
from __future__ import annotations

import ast
import re
from pathlib import Path

from src.config import RenderSettings
from src.llm import LLMError, new_conversation
from src.manim_render import render_scene
from src.scene_templates import can_template, photo_scene_source
from src.script_models import DialogueSegment, VideoScript

SCENE_CLASS = "SegmentScene"

# The scaffolding is injected as *source text*, so we only need its path — never
# import it here. manim_helpers imports manim, and composing/prompting must work
# on machines (and in the dashboard) where Manim isn't installed.
_helpers_file = str(Path(__file__).resolve().with_name("manim_helpers.py"))

SYSTEM_PROMPT = """You are a master Manim (Community Edition) animator producing \
ONE scene for an educational concept/derivation video. A themed background, \
color palette, chroma-key zones, and a safe drawing area are ALREADY built for \
you by a base class. You only write the animation.

HARD RULES:
- Output ONLY a Python class `class SegmentScene(ThemedScene):` with a \
`construct(self)` method. No imports, no `from manim import`, no `config.*`, no \
markdown fences, no prose.
- Do NOT build your own background, rectangle backdrop, or set camera color — it \
exists. Do NOT redefine ThemedScene.
- Keep ALL content inside the safe area. Use the provided helpers:
    self.eq(latex, color=None, scale=1.0)   -> themed MathTex
    self.caption(text) / self.heading(text) -> themed Text
    self.underline(mob)                      -> accent underline
    self.fit_safe(mob, pad=0.9)              -> scale+center a mobject into the safe area
    self.safe_center / self.safe_top() / self.safe_bottom()  -> np points
    self.safe_width / self.safe_height       -> floats (Manim units)
    THEME["primary"|"secondary"|"muted"|"accent"|"accent_2"|"line"]  -> hex colors
- Never use GrowArrow (use Create/GrowFromPoint). Never use self.camera.frame \
(this is a plain Scene — simulate zoom/pan by scaling/shifting a VGroup).
- Group multi-line equations in a VGroup and call self.fit_safe(group) so nothing \
overflows — especially important in portrait (tall, narrow) frames.
- Prefer smooth, purposeful motion: Write/FadeIn/TransformMatchingTex/Indicate. \
Animate the NEW step; show prior steps compactly and de-emphasized (THEME["muted"]).
- Aim for roughly the target duration, but exact length is conformed in post — \
do NOT stall with huge waits. End when the animation reads well.

SOUND: call `self.cue("<name>")` on the line immediately BEFORE an animation to \
score it. Available: pop (element appears), write (something is written), \
whoosh (slides/transforms in), ding (a step resolves / result lands), \
click (emphasis, underline), reveal (a new visual is revealed), impact (title \
or section break). Score only the moments that matter — roughly 2-5 cues for a \
typical beat, never one per animation. The render itself stays silent; cues are \
mixed onto the narration afterwards.

Return only the class."""


def _helper_body() -> str:
    """Load manim_helpers source, minus the __future__ import (illegal once it's
    no longer the first statement of the composed module)."""
    src = Path(_helpers_file).read_text(encoding="utf-8")
    return src.replace("from __future__ import annotations\n", "")


def _theme_literal(script: VideoScript) -> str:
    return repr(script.theme.to_dict())


def _chroma_literal(settings: RenderSettings) -> str:
    ch = settings.chroma
    return repr({
        "enabled": ch.enabled,
        "color": ch.color,
        "zone": ch.zone_rect(),
        "safe": ch.safe_rect(),
        "animate_in": ch.animate_in,
        "gradient": ch.gradient,
        "gradient_frac": ch.gradient_frac,
    })


def _asset_root() -> str:
    """Project root, used by the scaffolding to resolve bundled assets
    (background artwork, fonts) regardless of where the composed scene file
    ends up on disk."""
    return str(Path(_helpers_file).resolve().parents[1])


def _images_literal(seg: DialogueSegment | None) -> str:
    """Bake this segment's photos into the scene file as absolute paths, so a
    rendered scene never depends on the working directory."""
    if seg is None:
        return "[]"
    return repr([img.to_dict() for img in seg.images])


def cues_file_for(manim_file: str | Path) -> Path:
    """Where the scene writes its sound cues — always beside its source file,
    so assembly can find them without threading another path around."""
    return Path(manim_file).with_suffix(".cues.json")


def build_header(script: VideoScript, seg: DialogueSegment | None = None,
                 cues_path: str | None = None) -> str:
    settings = script.render_settings
    pw, ph = settings.orientation.resolution
    fw, fh = settings.orientation.manim_frame
    return (
        "from __future__ import annotations\n"
        "from manim import *\n"
        "import numpy as np\n\n"
        f"config.pixel_width = {pw}\n"
        f"config.pixel_height = {ph}\n"
        f"config.frame_width = {fw}\n"
        f"config.frame_height = {fh}\n"
        f"config.frame_rate = {settings.fps}\n"
        f'config.background_color = "{script.theme.background}"\n\n'
        f"THEME = {_theme_literal(script)}\n"
        f'ORIENTATION = "{settings.orientation.value}"\n'
        f"CHROMA = {_chroma_literal(settings)}\n"
        f"ASSET_ROOT = {_asset_root()!r}\n"
        f"IMAGES = {_images_literal(seg)}\n"
        f"CUES_PATH = {cues_path or ''!r}\n\n"
    )


def compose_file(script: VideoScript, scene_class_src: str,
                 seg: DialogueSegment | None = None,
                 cues_path: str | None = None) -> str:
    return (
        build_header(script, seg, cues_path)
        + "# --- injected scaffolding (src/manim_helpers.py) ---\n"
        + _helper_body()
        + "\n\n# --- generated scene ---\n"
        + scene_class_src
        + "\n"
    )


def _strip_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n", "", text)
        text = re.sub(r"\n```$", "", text)
    return text.strip()


def _segment_prompt(script: VideoScript, seg: DialogueSegment) -> str:
    settings = script.render_settings
    prior = script.prior_equations(seg.index)
    prior_txt = "\n".join(f"  - {e}" for e in prior[-4:]) or "  (none — this is the opening)"
    new_txt = "\n".join(f"  - {e}" for e in seg.equations) or "  (no new equation — conceptual beat)"
    safe = settings.chroma.safe_rect()
    chroma = settings.chroma
    chroma_note = ""
    if chroma.enabled:
        chroma_note = (
            f"\nCHROMA: a flat {chroma.color} key zone occupies part of the frame; "
            f"keep all content in the safe area only."
        )
        if chroma.animate_in:
            chroma_note += (
                " The zone is NOT shown yet — call self.reveal_chroma() once, at a "
                "natural moment, to transition it in."
            )

    photo_note = ""
    if seg.images:
        listed = "\n".join(
            f"  [{i}] {img.caption or '(no caption)'} — layout={img.layout}"
            for i, img in enumerate(seg.images)
        )
        photo_note = f"""

PHOTOS: this beat has {len(seg.images)} real photograph(s) available:
{listed}
Show them with the built-in helpers — never construct ImageMobject yourself:
    self.photo(i)                  -> a fitted, framed, captioned Group
    self.show_photo(i, hold=2.0)   -> fade in, hold, returns elapsed seconds
Photos are Group members, not VGroup — do not pass them to VGroup(). For a
'side' layout put the photo on one half and the maths on the other; for 'full'
give the photo the frame to itself. The image must be clearly readable: never
cover it with equations."""

    return f"""Create the SegmentScene for one beat of "{script.title}".

Orientation: {settings.orientation.value} ({settings.orientation.resolution[0]}x{settings.orientation.resolution[1]}).
Theme: {script.theme.name} ({'dark' if script.theme.is_dark else 'light'} — colors already wired into THEME/helpers).
Safe area (normalized top-left origin, x,y,w,h): {tuple(round(v, 3) for v in safe)}.
Target duration: ~{seg.target_duration:.1f}s (conformed in post — approximate is fine).{chroma_note}{photo_note}

Speaker: {seg.speaker}
Narration (spoken over this beat — do NOT print it as on-screen text unless it helps; use it for emphasis/pacing):
  "{seg.narration}"
{f'Director note: {seg.note}' if seg.note else ''}

Equations already established (show compactly/de-emphasized for continuity):
{prior_txt}

New equation(s) to feature and animate this beat:
{new_txt}

Animate this beat cleanly over the existing background. Return only the class."""


def load_prewritten_source(scenes_dir: str, index: int) -> str | None:
    """Read a hand-written / pre-generated SegmentScene body for offline mode.

    Looks for ``segment_{index:03d}.py`` (also accepts ``segment_{index}.py``).
    Returns the class source, or None if absent.
    """
    d = Path(scenes_dir)
    for cand in (d / f"segment_{index:03d}.py", d / f"segment_{index}.py"):
        if cand.exists():
            return _strip_fences(cand.read_text(encoding="utf-8"))
    return None


def render_prewritten(script: VideoScript, seg: DialogueSegment,
                      scene_src: str, out_dir: str,
                      media_dir: str) -> tuple[str, str] | None:
    """Compose + render a supplied SegmentScene (no LLM, no repair loop)."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    manim_file = out / f"segment_{seg.index:03d}.py"
    out_name = f"segment_{seg.index:03d}"

    full = compose_file(script, scene_src, seg, str(cues_file_for(manim_file)))
    manim_file.write_text(full, encoding="utf-8")
    try:
        ast.parse(full)
    except SyntaxError as e:
        print(f"   seg {seg.index}: pre-written scene has a SyntaxError: {e}")
        return None

    result = render_scene(str(manim_file), SCENE_CLASS, out_name,
                          script.render_settings, media_dir)
    if result.ok:
        print(f"   seg {seg.index}: rendered (offline)")
        return (str(manim_file), result.video_path)  # type: ignore[return-value]
    print(f"   seg {seg.index}: render failed (offline)\n{result.error}")
    return None


def generate_segment_code(script: VideoScript, seg: DialogueSegment,
                          out_dir: str, media_dir: str,
                          max_attempts: int = 4,
                          answer_title: str = "Answer") -> tuple[str, str] | None:
    """Generate + render one segment with repair. Returns (manim_file, video)
    on success, or None on exhaustion."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    manim_file = out / f"segment_{seg.index:03d}.py"
    out_name = f"segment_{seg.index:03d}"

    # Photo-only beats (including the answer card) have one correct staging.
    # Render them from the template — no model call, no variance between videos.
    if can_template(seg):
        kind = "answer card" if seg.is_outro else "photo beat"
        print(f"   seg {seg.index}: {kind} — rendering from template")
        return render_prewritten(
            script, seg, photo_scene_source(seg, answer_title=answer_title),
            out_dir=out_dir, media_dir=media_dir,
        )

    # One conversation for the whole segment: each repair turn continues it, so
    # the model still sees the code it wrote and the prompt cache stays warm.
    conv = new_conversation(SYSTEM_PROMPT, effort="high")
    turn = _segment_prompt(script, seg)

    for attempt in range(1, max_attempts + 1):
        try:
            scene_src = _strip_fences(conv.send(turn))
        except LLMError as e:
            print(f"   seg {seg.index}: Claude call failed (attempt {attempt}) — {e}")
            if attempt == max_attempts:
                break
            continue
        full = compose_file(script, scene_src, seg, str(cues_file_for(manim_file)))
        manim_file.write_text(full, encoding="utf-8")

        # Cheap gate: syntax-check before spending a render.
        try:
            ast.parse(full)
        except SyntaxError as e:
            print(f"   seg {seg.index}: syntax error (attempt {attempt}) — retrying")
            turn = (f"The composed file has a SyntaxError: {e}. Return the FULL "
                    f"corrected SegmentScene class only.")
            continue

        result = render_scene(str(manim_file), SCENE_CLASS, out_name,
                              script.render_settings, media_dir)
        if result.ok:
            print(f"   seg {seg.index}: rendered (attempt {attempt})")
            return (str(manim_file), result.video_path)  # type: ignore[return-value]

        print(f"   seg {seg.index}: render failed (attempt {attempt}) — repairing")
        turn = ("Rendering failed. Fix the code so it renders. Error output:\n\n"
                f"{result.error}\n\nReturn the FULL corrected SegmentScene class "
                "only — no prose, no fences.")

    print(f"   seg {seg.index}: FAILED after {max_attempts} attempts")
    return None
