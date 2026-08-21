"""Write the Flow/Veo prompt for one PYQ beat, and rewrite it when it comes back wrong.

WHEN A BEAT GOES TO VEO AT ALL
------------------------------
Rarely, and never by default. PIPELINE.md's routing table stands: equation
chains, graphs, geometric construction and schematic apparatus all render
correctly in Manim by construction, and roughly half of every Veo NEGATIVE list
we have ever written exists only to suppress Veo's text failures. A beat earns a
Veo clip when the thing that has to move is *photoreal or organic* — rust
creeping across iron, a flame's colour changing, gas bubbling off an electrode,
tissue swelling under osmosis — and neither Manim nor a still image can show it
moving. Everything else stays where it is.

THE CONTRACT EVERY PROMPT HERE MUST HONOUR
------------------------------------------
Three of these come from the house skill, which already learned them the
expensive way (`.claude/skills/video-prompt/references/bug-ledger.md`); the
fourth is ours and is the strictest.

  §15 UPLOADED BACKGROUND. The subject plate from `assets/backgrounds/` is
       attached to the generation, so the prompt must never *describe* a
       background — describing one makes Veo build its own and discard ours, or
       blend the two and leave a seam. The animation sits ON the plate, and the
       plate is the same plate Manim renders, which is what lets a clip be
       dropped into the middle of a rendered part without a visible cut.

  §17 SILENT. The audio is the HeyGen presenter's. A clip that generates its own
       voiceover gives us two voices over each other AND makes Veo burn in its
       own captions.

  §18 BAND. Adapted: the reels track reserves the bottom half, this track
       reserves BOTH ends — the caption strip at the top and the presenter at
       the bottom. See LAYOUT.

  NOTHING BUT THE ANIMATION. Ours, and absolute. The clip contains the thing
       being demonstrated and nothing else — no text of any kind, and no
       decoration either: no border, no frame, no vignette, no panel, no title
       card, no end card, no sparkle, no lens flare, no floating particle, no
       progress bar, no interface furniture.

       The text half is forced on us: every word on screen in this track is
       Devanagari, Veo cannot set Devanagari, and a clip with mangled Hindi in
       it is unusable however good the animation is. Labels are not lost — they
       are rendered by us, in the right font, over the top of this clip
       (`labels` on a video beat; see src/veo.py and tools/composite.py), and
       they land on the caption that names the part, which a generated label
       could never do.

       The decoration half is a quality rule. Everything that reaches the
       screen has to be there because the student needs it; a lens flare over a
       corrosion demonstration is not a better video, it is a distraction with
       production value. One idea in the frame, cleanly shown.

       Both halves are stated POSITIVELY in the prompt and enumerated in the
       NEGATIVE list, never the other way round. Naming a thing in the positive
       section is a signal to draw it — that is the ledger's most expensive
       entry, and the reason `audit()` refuses a prompt containing certain words
       at all.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from src.llm import complete, strip_fences

ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = ROOT / ".claude" / "skills" / "video-prompt"
PLATES = ROOT / "assets" / "backgrounds"

# --------------------------------------------------------------------------- #
# The frame. These numbers are not style — they are measured off the two things
# that share the frame with the clip, and if either moves, these move with it.
#
#   CAPTION_BAND  tools/composite.py composites nothing here, but Manim writes
#                 the caption at 0.090 and it can run to two lines. 0.26 is the
#                 cut line the compositor uses, chosen to clear two lines and
#                 still sit above STAGE_TOP (0.290) in the scene template.
#   PRESENTER_TOP composite.py puts the presenter's head at FULL_Y=966 of 1920.
#                 A clip that draws below 0.503 draws behind him.
# --------------------------------------------------------------------------- #
LAYOUT = {
    "size": "1080x1920 vertical 9:16",
    "caption_cut": 0.26,       # everything above this is the caption strip
    "presenter_top": 0.50,     # everything below this is the presenter
    "full_bottom": 0.92,       # when the presenter steps aside, the usable floor
}

SUBJECTS = {"physics", "chemistry", "biology", "maths"}


def plate_for(subject: str) -> Path:
    """The background image this clip must be generated on top of."""
    s = (subject or "").strip().lower()
    if s not in SUBJECTS:
        raise ValueError(
            f"meta.json says subject={subject!r}; expected one of {sorted(SUBJECTS)} "
            f"so a background plate can be attached to the generation")
    p = PLATES / f"{s}.png"
    if not p.is_file():
        raise FileNotFoundError(f"no background plate at {p}")
    return p


def load_skill() -> str:
    """SKILL.md and its reference blocks, as one system prompt.

    Same three files `src/frames.py` loads. Kept as its own function rather than
    imported from there because importing frames drags in the image-generation
    stack and its OpenAI client, which this module never needs.
    """
    parts = []
    for name in ("SKILL.md", "references/blocks.md", "references/bug-ledger.md"):
        path = SKILL_DIR / name
        if path.is_file():
            parts.append(f"===== {name} =====\n{path.read_text(encoding='utf-8')}")
    if not parts:
        raise FileNotFoundError(
            f"The video-prompt skill isn't in {SKILL_DIR}. Unpack video-prompt.skill.")
    return "\n\n".join(parts)


# The part of the contract that is ours rather than the skill's, spelled out for
# the writer. Kept as prose because that is what the model reads best, and kept
# here rather than in the task string so a change is reviewable in one place.
def house_contract(*, full_frame: bool) -> str:
    top = LAYOUT["caption_cut"]
    bot = LAYOUT["full_bottom"] if full_frame else LAYOUT["presenter_top"]
    band = f"between {int(top * 100)}% and {int(bot * 100)}% of the frame height"
    reserved_bottom = (
        "The bottom 8% of the frame stays empty background."
        if full_frame else
        "The whole bottom half of the frame — everything below the middle line — "
        "stays empty background, because a presenter is composited there.")
    return f"""THIS TRACK'S CONTRACT — these override anything in the skill they disagree with.

FORMAT: {LAYOUT['size']}, and the clip is SILENT (skill §17 applies in full).

BACKGROUND: a background image IS attached to this generation. Skill §15 applies
in full: do not describe a background, do not invent one, do not recolour,
blur, extend, crop, scale or animate the one supplied. It must look identical in
the first frame and the last, and identical to the same plate rendered elsewhere
in the video — this clip is spliced into the middle of a longer render and any
drift in the plate reads as a jump cut.

ACTIVE BAND: every drawn element — including labels, arrows, glows, shadows and
any inset — sits {band}. The top {int(top * 100)}% of the frame stays empty
background, because a Hindi caption is composited there. {reserved_bottom}
If the subject would not fit, it is scaled down until it does. It never grows,
drifts downward or expands during the clip.

THE FRAME CONTAINS THE ANIMATION AND NOTHING ELSE. This is the strictest rule
in the pack and it has no exceptions. What is drawn is the thing being
demonstrated, on the supplied background, and that is the complete list of what
appears. Everything a viewer sees must be part of the demonstration itself.

Two consequences, and both are absolute:

  1. Nothing written. No words, no letters in any script, no numerals, no
     equations, no chemical formulae, no units, no axis numbers, no legend, no
     caption, no subtitle, no label of any kind. Everything written in this
     video is Devanagari and is typeset separately in the correct font and laid
     over this clip afterwards — so a generated letterform is a defect even when
     it is beautiful. Describe what is SHOWN, never what is named.

  2. Nothing decorative. No border, no frame, no vignette, no split panel, no
     title card, no end card, no sparkle, no glint, no lens flare, no floating
     particle, no dust mote, no light ray, no interface element, no arrow that
     is not itself part of the mechanism being taught. If a student could not
     say what an element is teaching them, it does not belong in the frame.

State both of these positively — say what IS in the frame. Put the forbidden
things ONLY in the NEGATIVE list, in the tool's own vocabulary, and never in the
body of the prompt: naming a thing where the tool is being told what to draw is
how it ends up drawn.

CAMERA: locked and static. No push-in, no pull-back, no pan, no handheld drift,
no rack focus. The plate must not move, and a moving camera moves it.

STYLE: clean instructional illustration for a Class 12 exam answer — accurate
before it is pretty, and finished-looking rather than busy. One idea in the
frame, well lit, well composed, nothing a student could mistake for part of the
apparatus.

THE NEGATIVE LIST must include, at minimum, every category above: on-screen
text, letters, numerals, subtitles, captions, labels, equations; and borders,
frames, vignettes, title cards, sparkles, lens flares, floating particles and
interface elements."""


def _captions_around(lines: list[dict], at: int, span: int = 3) -> str:
    lo, hi = max(0, at - 1), min(len(lines), at + span)
    return "\n".join(f"[{i}] {lines[i]['text']}" for i in range(lo, hi))


def write_prompt(*, brief: str, lines: list[dict], at: int, subject: str,
                 question: str, accuracy: str = "", script: str = "",
                 full_frame: bool = True, duration: int = 8,
                 provider: str | None = None) -> dict:
    """Turn one beat's brief into a generation-ready Flow prompt.

    Returns ``{"prompt": ..., "negative": ..., "checks": [...]}``; `checks` is
    the list the visual review is graded against, written by the same pass that
    wrote the prompt so the two cannot drift apart.
    """
    skill = load_skill()
    task = f"""Write ONE Flow/Veo prompt for a single beat of a Hindi PYQ answer video.

{house_contract(full_frame=full_frame)}

THE QUESTION THIS VIDEO ANSWERS:
{question}

WHAT THIS BEAT MUST SHOW (the author's brief — this is the whole job):
{brief}

WHAT THE PRESENTER IS SAYING WHILE IT PLAYS (for timing and emphasis only; do
NOT put any of these words on screen):
{_captions_around(lines, at)}

THE VERIFIED ANSWER — this is the corrected version, not the question paper's.
Every fact the animation shows must agree with it, and each error named here
must be impossible to read into the clip:
{accuracy or '(none supplied — still refuse to draw anything you are unsure of)'}

THE SCRIPT THIS VIDEO IS BUILT FROM, for context on how the topic is being
taught and which parts the teacher leans on. Illustrate the explanation actually
being given, not the topic in general:
{script[:4000] or '(not supplied)'}

LENGTH: about {duration} seconds. Describe a change that RESOLVES inside that
time — a process still halfway through at the end reads as a glitch when the
clip cuts. The clip is fitted to the narration afterwards, so do NOT try to make
it fill a longer window; a short, correct, finished movement is worth more than
a long one, because the finished state can be held and a wrong one cannot.

Return JSON and nothing else:
{{"prompt": "the full prompt, 90-160 words, in the house block style",
  "negative": "the NEGATIVE list, comma separated",
  "checks": ["a short factual statement a reviewer can confirm or deny by
              looking at a frame", "..."]}}

`checks` is what a vision model will grade the finished clip against, so make
each one observable in a still frame and specific enough to fail: not "the
diagram is correct" but "the copper strip is in the blue solution and the zinc
strip is in the colourless one"."""

    raw = strip_fences(complete(skill, task, effort="high", provider=provider))
    return _parse(raw)


def revise_prompt(previous: dict, defects: list[str], *,
                  provider: str | None = None) -> dict:
    """Rewrite a prompt to kill the specific defects the review found.

    Deliberately narrow. A rewrite that reconsiders the whole shot usually
    trades the defect for a new one; the ledger's entries are almost all of the
    form "one clause was missing", so the instruction is to add or tighten
    clauses and change nothing else.
    """
    skill = load_skill()
    task = f"""This prompt was generated and the clip came back wrong.

THE PROMPT THAT WAS USED:
{previous['prompt']}

ITS NEGATIVE LIST:
{previous.get('negative', '')}

WHAT THE REVIEW SAW WRONG:
{chr(10).join('- ' + d for d in defects)}

Fix exactly these defects and change nothing else. Keep the shot, the subject,
the framing and the band. Prefer adding an explicit clause that forbids the
defect and an explicit clause that states the correct alternative, over
rewriting a sentence that was already working — a full rewrite usually swaps one
defect for another. Add each defect to the NEGATIVE list in the tool's own
vocabulary.

Return the same JSON shape: {{"prompt": ..., "negative": ..., "checks": [...]}}
Keep every check from before and add one per defect."""

    raw = strip_fences(complete(skill, task, effort="high", provider=provider))
    return _parse(raw)


def _parse(raw: str) -> dict:
    try:
        data = json.loads(raw)
    except ValueError:
        m = re.search(r"\{.*\}", raw, re.S)
        if not m:
            raise ValueError(f"the prompt writer did not return JSON:\n{raw[:400]}")
        data = json.loads(m.group(0))
    if not data.get("prompt"):
        raise ValueError(f"the prompt writer returned no prompt:\n{raw[:400]}")
    data.setdefault("negative", "")
    data.setdefault("checks", [])
    return data


BANNED = ("logo", "watermark", "badge", "wordmark")

# The two families the NEGATIVE list must cover, because the prompt body is not
# allowed to name them. One term from each pair is enough — the point is that
# the category was thought about, not that a particular synonym was used.
REQUIRED_NEGATIVES = {
    "on-screen text": ("text", "letter", "word", "caption", "subtitle",
                       "numeral", "number", "label", "typography", "writing"),
    "decoration": ("border", "frame", "vignette", "sparkle", "flare",
                   "particle", "title card", "glow", "overlay", "panel"),
}


def audit(spec: dict) -> list[str]:
    """Mechanical checks on a written prompt. No model — these are the mistakes
    that are cheap to detect and expensive to discover in a rendered clip."""
    bad = []
    text = spec["prompt"]
    low = text.lower()
    neg = (spec.get("negative") or "").lower()

    # The hard rule: the frame carries the animation and nothing else. The
    # prompt body may not name the forbidden things (naming is drawing), so the
    # only place the rule can be checked mechanically is the negative list —
    # which makes an incomplete negative list a real failure, not a nit.
    for family, terms in REQUIRED_NEGATIVES.items():
        if not any(t in neg for t in terms):
            bad.append(f"the NEGATIVE list says nothing about {family}; the clip "
                       f"must carry the animation and nothing else, and the "
                       f"prompt body is not allowed to say so")

    # The ledger's most expensive entry: naming a thing is a signal to draw it.
    # A prompt that says "no logo" produced a logo in both top corners.
    for w in BANNED:
        if w in low:
            bad.append(f"the prompt contains the word {w!r} — naming it makes Veo "
                       f"draw it, even in a negative (bug-ledger)")

    if not re.search(r"silent|no voiceover|no narration", low):
        bad.append("the prompt does not declare the clip silent (§17), so Veo "
                   "will generate a voice and burn in its own captions")
    if not re.search(r"supplied|attached|uploaded", low):
        bad.append("the prompt does not refer to the supplied background image "
                   "(§15), so Veo will generate its own and discard the plate")
    if re.search(r"\bcamera\b.*\b(pan|push|pull|zoom|dolly|handheld)\b", low) \
            and not re.search(r"no (pan|push|pull|zoom|dolly|camera move)", low):
        bad.append("the prompt moves the camera, which moves the plate")

    words = len(text.split())
    if words < 70:
        bad.append(f"the prompt is {words} words; under-specified prompts drift "
                   f"(the house target is 90-160)")
    if words > 220:
        bad.append(f"the prompt is {words} words; past ~200 Veo starts dropping "
                   f"clauses, and the dropped one is never the one you would pick")
    if not spec.get("checks"):
        bad.append("no checks were written, so the visual review has nothing to "
                   "grade the clip against")
    return bad
