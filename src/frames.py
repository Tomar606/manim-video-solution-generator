"""Reference frames for the topics Manim can't draw.

Some beats are cells, organs, molecules — things vector animation renders badly
and slowly. For those we generate a still *frame*, then hand that frame to a
video model (Veo) together with an animation prompt. The frame carries the
subject, the layout and the labels; the prompt carries the motion. Veo is much
more accurate when it is shown the scene rather than only told about it.

Two things make the output consistent across videos:

**The house style is derived from a real example, not invented.** Point this at
a frame sheet the team has already made and it writes a style spec — palette,
label treatment, panel structure — which every later prompt is built on. Ours
came from a Henry's Law sheet: numbered badge, caps title, leader-line callouts,
green/red state comparison, magnifier inset for molecular detail, caption box.

**Nothing regenerates silently.** Frames are cached by prompt hash, so a second
run costs nothing and an approved frame never changes under you.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path

from src import usage
from src.llm import LLMError, complete, strip_fences
from src.script_models import DialogueSegment, VideoScript

REPO_ROOT = Path(__file__).resolve().parents[1]
STYLE_SPEC_PATH = REPO_ROOT / "style" / "frame_style.md"

DEFAULT_IMAGE_MODEL = os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-2")
# Frame aspect is deliberately NOT tied to the video's aspect.
#
# The anchor frame is a *content and style* reference, not the literal first
# frame: Veo takes the subject, palette and label treatment from it, and takes
# the composition from the FRAME LAYOUT block in the prompt. Landscape is the
# proven default here because it spends the whole image budget on the diagram
# instead of on the empty half that the presenter will cover anyway.
#
# Portrait (1024x1536) is the alternative, and it matters if the frame is ever
# passed as a true first frame rather than a reference — then aspect must match
# the output. Which of the two wins is an empirical question; FRAME_LAYOUT below
# switches the composition rule to match whichever you're generating.
DEFAULT_SIZE = os.getenv("OPENAI_IMAGE_SIZE", "1536x1024")     # 3:2 landscape
# "full"      -> illustration uses the whole frame (proven default)
# "top_half"  -> composed for 9:16 with the bottom half left empty
FRAME_LAYOUT = os.getenv("FRAME_LAYOUT", "full")
DEFAULT_QUALITY = os.getenv("OPENAI_IMAGE_QUALITY", "medium")


# --------------------------------------------------------------------------- #
# Deriving the house style from an example sheet                               #
# --------------------------------------------------------------------------- #
STYLE_SYSTEM = """You are a design director writing a style guide that another \
system will follow to generate educational illustration frames.

You are shown a sheet of frames from a video the team has already shipped. \
Write the specification that would let someone reproduce that exact look for a \
completely different topic.

Be concrete and visual: palette with roles (what each colour MEANS), typography, \
how labels attach to the diagram, how comparisons are laid out, what the caption \
box looks like, background, level of realism, how molecular detail is shown. \
Note the recurring furniture — numbering, titles, badges — and where it sits.

Do NOT describe the subject matter of the example. The next topic will be \
unrelated; only the visual system carries over. Write it as instructions, under \
300 words, no preamble."""


def derive_style_spec(sample_image: str | Path, *, force: bool = False,
                      provider: str | None = None) -> str:
    """Write (and cache) the frame style guide from an example sheet."""
    if STYLE_SPEC_PATH.exists() and not force:
        return STYLE_SPEC_PATH.read_text(encoding="utf-8")

    spec = complete(
        STYLE_SYSTEM,
        "Write the style specification for reproducing these frames on any "
        "other topic.",
        images=[str(sample_image)],
        provider=provider,
        effort="medium",
    )
    spec = strip_fences(spec).strip()
    STYLE_SPEC_PATH.parent.mkdir(parents=True, exist_ok=True)
    STYLE_SPEC_PATH.write_text(spec, encoding="utf-8")
    return spec


# --------------------------------------------------------------------------- #
# Per-beat image prompt                                                        #
# --------------------------------------------------------------------------- #
PROMPT_SYSTEM = """You write prompts for an image model that produces single \
educational illustration frames for a science video.

You are given the house style, and one beat of a script: what the presenter says \
and what the beat is meant to show. Write the image prompt for that beat's frame.

Rules:
- Describe ONE frame. It must stand alone and teach its point without motion.
- Name every on-screen label explicitly, with the exact text to render, in the \
LABEL LANGUAGE given below. Keep each label to 1-3 words: image models garble \
long strings, and the risk rises sharply for non-Latin scripts.
- State the layout: what is centre, what is compared against what, where the \
callouts point, whether a magnified inset is needed.
- Carry the house style through: palette roles, badge, title, caption box.
- Scientific accuracy matters more than beauty. If the beat is about a shape \
change, the two shapes must be unmistakably different and correct.
- State the subject's TRUE colour explicitly in the prompt (red blood cells are \
red, not blue). The house palette applies to labels, arrows and boxes — never to \
the specimen itself. A style rule that recolours the subject is being misread.
- No text in the prompt about video, motion, animation or camera work.
- COMPOSITION (non-negotiable): the frame is vertical 9:16. EVERYTHING — badge, title, diagram, labels, caption — sits in the TOP HALF of the frame. The BOTTOM HALF is empty background only: no diagram, no text, no labels, no shadow, no glow, no marks. That space is reserved for a presenter composited in later. Say this explicitly in the prompt, and never draw a line, band or divider marking the halfway point.

Output only the prompt, one paragraph, no preamble."""


# Our audience is Hindi-medium, so labels, terms and the caption are written in
# Devanagari — matching the language the narration is in.
# How the frame is composed. Set by FRAME_LAYOUT; the prompt writer is told one
# or the other, never both.
FRAME_COMPOSITIONS = {
    "full": (
        "The illustration uses the whole frame, edge to edge, like a printed "
        "poster. This frame is a content and style reference — the video's own "
        "layout is set separately in the animation prompt, so do not leave "
        "space for anything else here."
    ),
    "top_half": (
        "The frame is vertical 9:16. EVERYTHING — badge, title, diagram, labels, "
        "caption — sits in the TOP HALF. The BOTTOM HALF is empty background "
        "only: no diagram, no text, no shadow, no glow, no marks, reserved for a "
        "presenter composited in later. Never draw a line, band or divider at "
        "the halfway point."
    ),
}

LABEL_LANGUAGES = {
    "hindi": (
        "Hindi in DEVANAGARI script. Every label, title, header pill and the "
        "caption box must be Devanagari. Scientific symbols and gene/protein "
        "names that are conventionally Latin (HbA, HbS, GAG, GTG, DNA, O2) stay "
        "Latin — Hindi-medium textbooks print them that way too. Render the "
        "Devanagari precisely, with correct matras and conjuncts; the text must "
        "be sharp and readable."
    ),
    "hinglish": (
        "English for labels and titles; the caption box may be Hinglish written "
        "in Latin script."
    ),
    "english": "English throughout.",
}


def _beat_context(script: VideoScript, seg: DialogueSegment,
                  index: int, total: int) -> str:
    return (
        f'Video: "{script.title}" (beat {index} of {total})\n'
        f"What this beat shows: {seg.note or '(not specified)'}\n"
        f"Narration for this beat:\n\"{seg.narration}\"\n"
    )


def build_prompt(script: VideoScript, seg: DialogueSegment, style_spec: str,
                 index: int, total: int, *, provider: str | None = None,
                 label_language: str | None = None) -> str:
    language = (label_language or getattr(script, "language", "hinglish")).lower()
    directive = LABEL_LANGUAGES.get(language, LABEL_LANGUAGES["english"])
    composition = FRAME_COMPOSITIONS.get(
        os.getenv("FRAME_LAYOUT", FRAME_LAYOUT), FRAME_COMPOSITIONS["full"])
    prompt = complete(
        f"{PROMPT_SYSTEM}\n\nCOMPOSITION: {composition}"
        f"\n\nLABEL LANGUAGE: {directive}"
        f"\n\nHOUSE STYLE:\n{style_spec}",
        _beat_context(script, seg, index, total),
        provider=provider,
        effort="medium",
    )
    return strip_fences(prompt).strip()


# --------------------------------------------------------------------------- #
# Generation                                                                   #
# --------------------------------------------------------------------------- #
@dataclass
class Frame:
    index: int
    path: str
    prompt: str
    cached: bool = False
    cost_usd: float = 0.0

    def to_dict(self) -> dict:
        return {"beat": self.index, "file": Path(self.path).name,
                "prompt": self.prompt, "cached": self.cached}


def _cache_key(prompt: str, model: str, size: str, quality: str) -> str:
    blob = json.dumps([prompt, model, size, quality], sort_keys=True)
    return hashlib.sha256(blob.encode()).hexdigest()[:16]


def generate_image(prompt: str, dest: Path, *, model: str = DEFAULT_IMAGE_MODEL,
                   size: str = DEFAULT_SIZE,
                   quality: str = DEFAULT_QUALITY) -> float:
    """Generate one image to ``dest``. Returns the estimated cost."""
    import openai

    from src.llm import _openai_client

    usage.check_budget(usage.image_cost(model, 1, quality))
    client = _openai_client()
    try:
        result = client.images.generate(model=model, prompt=prompt,
                                        size=size, quality=quality, n=1)
    except openai.APIStatusError as exc:
        raise LLMError(f"Image generation failed ({exc.status_code}): {exc}") from exc
    except openai.APIConnectionError as exc:
        raise LLMError(f"Could not reach OpenAI: {exc}") from exc

    item = result.data[0]
    dest.parent.mkdir(parents=True, exist_ok=True)
    if getattr(item, "b64_json", None):
        dest.write_bytes(base64.b64decode(item.b64_json))
    elif getattr(item, "url", None):
        import urllib.request
        with urllib.request.urlopen(item.url, timeout=120) as resp:
            dest.write_bytes(resp.read())
    else:
        raise LLMError("Image response contained neither b64_json nor url.")

    usage.record_image(model, 1, quality=quality, note=dest.name)
    return usage.image_cost(model, 1, quality)


def generate_for_script(script: VideoScript, out_dir: str | Path, *,
                        style_spec: str, beats: list[int] | None = None,
                        provider: str | None = None,
                        model: str = DEFAULT_IMAGE_MODEL,
                        size: str = DEFAULT_SIZE,
                        quality: str = DEFAULT_QUALITY,
                        label_language: str | None = None,
                        dry_run: bool = False) -> list[Frame]:
    """Write one frame per requested beat. Cached frames cost nothing."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    targets = [s for s in script.segments
               if beats is None or s.index in beats]
    total = len(script.segments)
    frames: list[Frame] = []

    # The image cache is keyed on the prompt — but the prompt is *written by a
    # model*, so it comes out different every run and the cache could never hit.
    # A re-run after any downstream failure therefore paid for the same frame
    # again. Keep the prompt beside the frames and reuse it.
    prompt_cache_path = out / "prompts.json"
    prompt_cache: dict[str, str] = {}
    if prompt_cache_path.exists():
        try:
            prompt_cache = json.loads(prompt_cache_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            prompt_cache = {}

    for seg in targets:
        prompt = prompt_cache.get(str(seg.index))
        if not prompt:
            prompt = build_prompt(script, seg, style_spec, seg.index + 1, total,
                                  provider=provider, label_language=label_language)
            prompt_cache[str(seg.index)] = prompt
            prompt_cache_path.write_text(
                json.dumps(prompt_cache, indent=2, ensure_ascii=False),
                encoding="utf-8")
        key = _cache_key(prompt, model, size, quality)
        dest = out / f"frame_{seg.index:03d}_{key}.png"

        if dest.exists():
            frames.append(Frame(seg.index, str(dest), prompt, cached=True))
            print(f"   beat {seg.index}: frame cached, no spend")
            continue
        if dry_run:
            frames.append(Frame(seg.index, str(dest), prompt))
            print(f"   beat {seg.index}: prompt ready (dry run, nothing generated)")
            continue

        cost = generate_image(prompt, dest, model=model, size=size,
                              quality=quality)
        frames.append(Frame(seg.index, str(dest), prompt, cost_usd=cost))
        print(f"   beat {seg.index}: frame generated (~${cost:.3f})")

    # Save the prompts beside the frames. Without this you can't tell why a
    # frame came out wrong — which is exactly the situation that produced the
    # blue-red-blood-cell bug.
    manifest = out / "frames.json"
    existing = {}
    if manifest.exists():
        try:
            existing = {str(f["beat"]): f
                        for f in json.loads(manifest.read_text(encoding="utf-8"))}
        except (json.JSONDecodeError, OSError, TypeError):
            existing = {}
    for frame in frames:
        existing[str(frame.index)] = frame.to_dict()
    manifest.write_text(
        json.dumps([existing[k] for k in sorted(existing, key=int)],
                   indent=2, ensure_ascii=False), encoding="utf-8")

    return frames


# --------------------------------------------------------------------------- #
# The animation prompt that goes to Veo alongside the frame                    #
# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
# Accuracy brief — established before any prompt is written                    #
# --------------------------------------------------------------------------- #
# A video model will happily render a confident, wrong picture: a sickle cell
# that curls the wrong way, mitosis with the wrong chromosome count, blood that
# is blue. Neither the narration nor the house style constrains any of that, so
# the specifics are pinned down first and every prompt is written against them.
FACTS_SYSTEM = """You are a subject expert preparing an accuracy brief for an \
illustrator and an animator who do NOT know this topic.

From the script, list the visual facts they could plausibly get wrong. Only \
things that are SEEN — shape, colour, relative size, count, spatial arrangement, \
the order a process happens in, and what must never appear.

Be specific and checkable: "red blood cells are red, biconcave, about 7-8 \
micrometres across, no nucleus in mammals" — not "draw it accurately". Where the \
school syllabus simplifies something, follow the syllabus and say so, since the \
video must match what students are taught.

End with a short "COMMON ERRORS TO AVOID" list naming the specific wrong images \
that show up for this topic.

Under 400 words. No preamble."""


def research_visual_facts(script: VideoScript, *,
                          provider: str | None = None) -> str:
    """Pin down what must be visually correct for this topic."""
    beats = "\n".join(f"[{s.index}] {s.note or ''} — {s.narration}"
                      for s in script.segments if s.narration.strip())
    return strip_fences(complete(
        FACTS_SYSTEM,
        f'Video: "{script.title}"\n\nScript beats:\n{beats}',
        provider=provider, effort="high",
    )).strip()


# --------------------------------------------------------------------------- #
# Choosing the one or two frames that anchor the whole video                   #
# --------------------------------------------------------------------------- #
ANCHOR_SYSTEM = """You choose which beats of a science video get a generated \
reference frame. Frames are expensive, so a video gets one or two — not one per \
beat.

A good anchor frame is the one whose subject recurs through the video, drawn in \
the state most of the other beats build on or refer back to. Every other beat's \
animation is then described as a continuation of that same subject, which is \
what keeps the clips looking like one video.

Pick a second frame only when the video genuinely has two visually unrelated \
subjects (e.g. a cell AND an inheritance chart) that one image cannot serve.

Return JSON only: {"beats": [0], "reason": "one sentence"} — zero-based beat \
numbers, at most two."""


def select_anchor_beats(script: VideoScript, *, max_frames: int = 2,
                        provider: str | None = None) -> tuple[list[int], str]:
    """Ask which 1-2 beats should carry the generated frames."""
    from src.llm import extract_json

    beats = "\n".join(f"[{s.index}] {s.note or ''} — {s.narration[:160]}"
                      for s in script.segments if s.narration.strip())
    raw = complete(
        ANCHOR_SYSTEM,
        f'Video: "{script.title}"\nAt most {max_frames} frame(s).\n\n'
        f"Beats:\n{beats}",
        provider=provider, effort="medium",
    )
    try:
        data = extract_json(raw)
        picked = [int(b) for b in data.get("beats", [])][:max_frames]
        return picked, str(data.get("reason", ""))
    except Exception:                                # noqa: BLE001
        # Falling back to the first beat is safe: it's the establishing shot.
        return [0], "fallback: first beat"


# --------------------------------------------------------------------------- #
# The Veo prompt                                                               #
# --------------------------------------------------------------------------- #
# Structure follows Google's documented formula for Veo — cinematography,
# subject, action, context, style — because the model weights what comes first
# most heavily. The text-stability rule is ours: the official guide doesn't
# cover labelled diagrams, and warping label text is the failure mode that makes
# an otherwise good clip unusable.
VEO_SYSTEM = """You write prompts for Google Veo, which turns a starting still \
frame into a short educational clip.

Write ONE paragraph, 100-200 words, in this order — Veo weights what comes \
first most heavily:

1. CAMERA. Name the shot and any move. For a labelled diagram prefer "locked-off \
static shot" or at most "very slow push-in"; camera movement across text is what \
makes labels warp and smear.
2. SUBJECT. Restate the subject exactly as it appears in the frame, including its \
true colour and form, so Veo holds it steady instead of reinventing it.
3. ACTION. What moves, in the order it happens, timed across the clip ("over the \
first two seconds… then…"). Use physical, force-carrying verbs — bends, stiffens, \
polymerises, wedges, ruptures, flows — never "shows", "demonstrates" or \
"illustrates". Vague verbs produce floaty, weightless motion.
4. CONTEXT. What stays fixed: background, layout, every label in place.
5. STYLE. Match the frame: clean educational illustration, even lighting, no \
film grain, no lens flare, no depth-of-field blur that would soften text.

Always end with an explicit stability clause: all on-screen text and labels stay \
exactly as they are — same words, same position, sharp and legible, never \
warping, redrawing or animating.

Hard rules: one continuous shot, no cuts, no new elements that aren't in the \
frame, nothing that contradicts the accuracy brief, and no on-screen text that \
isn't already in the frame.

Output only the prompt. No preamble, no headings, no numbering."""


def build_animation_prompt(script: VideoScript, seg: DialogueSegment,
                           frame_path: str | None, duration: float,
                           *, provider: str | None = None,
                           facts: str = "", anchor_note: str = "") -> str:
    """Write the Veo prompt for one beat.

    ``frame_path`` is the anchor frame — usually shared with other beats, not
    generated for this one — so the prompt must describe how this beat's motion
    continues from it.
    """
    parts = [
        f'Video: "{script.title}"',
        f"Clip length: about {duration:.0f} seconds",
        f"What this beat must show: {seg.note or '(not specified)'}",
        f'Narration playing over it: "{seg.narration}"',
    ]
    if facts:
        parts.append(f"\nACCURACY BRIEF — nothing may contradict this:\n{facts}")
    if frame_path:
        parts.append(
            f"\nThe attached image is the video's reference frame. "
            f"{anchor_note}Keep the subject's design, colour and style identical "
            f"to it so every clip in this video matches."
        )
    else:
        parts.append(
            "\nThere is no frame for this beat. Describe the scene fully enough "
            "that Veo can build it, matching the video's established look."
        )
    return strip_fences(complete(
        VEO_SYSTEM, "\n".join(parts),
        images=[frame_path] if frame_path else None,
        provider=provider, effort="medium",
    )).strip()


def build_briefs(script: VideoScript, out_dir: str | Path, *,
                 anchor_frames: dict[int, str], facts: str = "",
                 provider: str | None = None,
                 default_duration: float = 8.0) -> Path:
    """Write the per-beat Veo package: prompt, which frame to attach, timing.

    This is the hand-off an editor works from until the Gemini API is wired in —
    the same shape as the avatar briefs.
    """
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    # One frame anchors every beat unless a nearer one was generated.
    def frame_for(index: int) -> str | None:
        if not anchor_frames:
            return None
        if index in anchor_frames:
            return anchor_frames[index]
        nearest = min(anchor_frames, key=lambda a: abs(a - index))
        return anchor_frames[nearest]

    entries = []
    for seg in script.segments:
        if not seg.narration.strip():
            continue
        frame = frame_for(seg.index)
        anchor_note = ("This frame is this beat's own. " if seg.index in anchor_frames
                       else "This frame belongs to another beat of the same video. ")
        duration = seg.target_duration or default_duration
        prompt = build_animation_prompt(script, seg, frame, duration,
                                        provider=provider, facts=facts,
                                        anchor_note=anchor_note)
        entry = {
            "beat": seg.index,
            "duration_seconds": round(duration, 2),
            "reference_frame": Path(frame).name if frame else None,
            "narration": seg.narration,
            "shows": seg.note or "",
            "veo_prompt": prompt,
        }
        entries.append(entry)
        (out / f"beat_{seg.index:03d}.txt").write_text(
            f"BEAT {seg.index}  ·  ~{duration:.0f}s\n"
            f"Reference frame: {entry['reference_frame'] or '(none)'}\n"
            f"Shows: {entry['shows']}\n"
            f"Narration: {seg.narration}\n\n"
            f"--- VEO PROMPT ---\n{prompt}\n",
            encoding="utf-8")

    (out / "veo_briefs.json").write_text(
        json.dumps({"title": script.title, "facts": facts, "beats": entries},
                   indent=2, ensure_ascii=False), encoding="utf-8")
    if facts:
        (out / "accuracy_brief.md").write_text(facts, encoding="utf-8")
    return out / "veo_briefs.json"


# --------------------------------------------------------------------------- #
# Driving the team's own prompt skill                                          #
# --------------------------------------------------------------------------- #
# The /video-prompt skill is the authority on what Veo actually responds to —
# every rule in it came from a generation that broke. So rather than write our
# own prompts, we hand the skill and its locked blocks to the model as the
# system prompt and let it produce the pack in the house format.
SKILL_DIR = REPO_ROOT / ".claude" / "skills" / "video-prompt"


def load_prompt_skill() -> str:
    """SKILL.md + its reference blocks, as one system prompt."""
    parts = []
    for name in ("SKILL.md", "references/blocks.md", "references/bug-ledger.md"):
        path = SKILL_DIR / name
        if path.is_file():
            parts.append(f"===== {name} =====\n{path.read_text(encoding='utf-8')}")
    if not parts:
        raise FileNotFoundError(
            f"The video-prompt skill isn't in {SKILL_DIR}. Unpack video-prompt.skill."
        )
    return "\n\n".join(parts)


def build_prompt_pack(script: VideoScript, facts: str, *,
                      out_path: str | Path,
                      reference_frames: list[str] | None = None,
                      provider: str | None = None,
                      background_uploaded: bool = True) -> Path:
    """Produce the full segment prompt pack in the house format."""
    skill = load_prompt_skill()
    beats = "\n\n".join(
        f"CLIP {s.index + 1} — {s.note or ''}\n{s.narration}"
        for s in script.segments if s.narration.strip()
    )
    task = f"""Write the complete prompt pack for this video.

TOPIC: {script.title}
NARRATION LANGUAGE: {script.language} (on-screen text follows the script text
exactly as written — do not translate or transliterate it)

The source script is written as long clips. Apply Step 1 and re-chunk it into
10-second segments of roughly 18-22 words, cutting only at natural pauses.

BACKGROUND: {'a background image is uploaded to the tool, so use blocks.md §15 (uploaded-background block) and its negatives, NOT §12.' if background_uploaded else 'no background image is uploaded; use §12.'}
§16 is REMOVED — do not reinstate it. The prompt must never contain the words
logo, watermark, badge or wordmark anywhere, not even in a negative: naming a
thing is a signal to draw it, and that block produced a logo in both top
corners. The Arivihan patch is composited after generation, not prompted for.

ACCURACY BRIEF — every diagram spec and NEGATIVE list must respect this, and
each COMMON ERROR must appear as an explicit ban:
{facts}

SOURCE SCRIPT:
{beats}

Output the complete .md pack and nothing else."""

    pack = strip_fences(complete(skill, task, provider=provider, effort="high",
                                 images=reference_frames or None))
    dest = Path(out_path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(pack, encoding="utf-8")
    return dest


def _batch_with_retry(system: str, prompt: str, *, provider, effort, images,
                      attempts: int = 4) -> str:
    """One pack batch, retried through transient overload.

    529 is a server-side blip, and a pack is a chain of long calls — losing the
    chain to one of them is the difference between a finished pack and nothing.
    """
    import time
    for attempt in range(attempts):
        try:
            return strip_fences(complete(system, prompt, provider=provider,
                                         effort=effort, images=images)).strip()
        except Exception as exc:                       # noqa: BLE001
            if attempt == attempts - 1 or "529" not in str(exc):
                raise
            wait = 20 * (attempt + 1)
            print(f"   529 overloaded, retrying in {wait}s "
                  f"(attempt {attempt + 2}/{attempts})")
            time.sleep(wait)
    raise RuntimeError("unreachable")


def build_prompt_pack_batched(script: VideoScript, facts: str, *,
                              out_path: str | Path,
                              reference_frames: list[str] | None = None,
                              provider: str | None = None,
                              background_uploaded: bool = True,
                              batch_size: int = 4,
                              batch_effort: str = "medium") -> Path:
    """Build the pack in batches, carrying the continuity chain across them.

    One call can't emit 20+ full segments — each carries ~1.5k characters of
    locked blocks, so the response is truncated long before the pack is done.
    Batching keeps every call comfortably inside the limit; the previous batch's
    closing state is passed forward so `SCREEN AT START` still chains correctly,
    which is the one thing splitting the work could otherwise break.
    """
    skill = load_prompt_skill()
    beats = "\n\n".join(
        f"CLIP {s.index + 1} — {s.note or ''}\n{s.narration}"
        for s in script.segments if s.narration.strip()
    )
    background_rule = (
        "a background image is uploaded to the tool: use blocks.md §15 "
        "(uploaded-background block) and its negatives, NOT §12."
        if background_uploaded else
        "no background image is uploaded; use §12."
    )

    # Pass 1 — plan only. Small output, and it fixes the chunking once so the
    # batches below can't disagree about where segments start and end.
    plan = strip_fences(complete(
        skill,
        f"""Do Step 1 and Step 2 ONLY for this video. Do not write any segment
prompts yet.

TOPIC: {script.title}
NARRATION LANGUAGE: {script.language} — on-screen text uses the script's own
words exactly; do not translate or transliterate.

Output:
1. Total segment count.
2. The segment map table: | Seg | Phrases (exact words) | Type | Diagram Y/N |
3. For each segment, one line: "Seg N ends with: <objects left on screen>".

SOURCE SCRIPT:
{beats}""",
        provider=provider, effort="high")).strip()

    total = len(re.findall(r"^\s*\|\s*\d+\s*\|", plan, re.M)) or 0
    print(f"   plan: {total or 'unknown'} segments")

    dest = Path(out_path)
    dest.parent.mkdir(parents=True, exist_ok=True)

    packs: list[str] = [f"# {script.title} — SEGMENT PROMPT SET\n\n{plan}\n"]
    start = 1
    carry = "This is the first segment; the screen starts empty."
    while start <= (total or 0):
        end = min(start + batch_size - 1, total)
        chunk = _batch_with_retry(
            skill,
            f"""Using the plan below, write the FULL prompt for segments
{start} to {end} only — every block in the tested order, nothing abbreviated,
each in its own ``` code block.

BACKGROUND: {background_rule}
§16 is REMOVED — do not reinstate it. The prompt must never contain the words
logo, watermark, badge or wordmark anywhere, not even in a negative: naming a
thing is a signal to draw it, and that block produced a logo in both top
corners. The Arivihan patch is composited after generation, not prompted for.

CONTINUITY: segment {start} starts from — {carry}

ACCURACY BRIEF (every diagram spec and NEGATIVE must respect this; each COMMON
ERROR becomes an explicit ban):
{facts}

PLAN:
{plan}""",
            provider=provider, effort=batch_effort,
            images=reference_frames or None)
        packs.append(chunk)
        print(f"   segments {start}-{end} written")

        # Flush after every batch. A pack is six or seven expensive calls; when
        # the last one died on a transient 529 the whole run used to return
        # nothing, discarding every batch before it.
        dest.write_text("\n\n".join(packs), encoding="utf-8")

        match = re.findall(rf"Seg {end} ends with:\s*(.+)", plan)
        carry = match[0].strip() if match else "the previous segment's end state"
        start = end + 1

    return dest
