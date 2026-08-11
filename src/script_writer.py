"""Turning a topic into a script a human can edit.

This writes the *first draft* — the thing that used to take an afternoon. It is
explicitly not the last word: the output is a plain ``.md`` file in the project
format, and the expectation is that someone reads it, fixes the phrasing, and
only then renders. Every downstream stage reads that file, so editing the script
is how you change the video.

Two loops run over each draft:

*Format* — the file has to parse under :mod:`src.script_parser`. A draft that
doesn't is handed back with the parser's own error, because a subtly malformed
script fails much later, at narration.

*Voice* — the draft is scored by :mod:`src.script_eval`, and specific defects
(repeated openers, maths in a spoken line, written-register phrasing) go back
for another pass. This is what "sounds human" means in practice: not a vibe, a
list of things the presenter would never actually say. The house voice itself
comes from :mod:`src.style`, learned from scripts the team has approved.

The provider is per-call, so script writing can run on OpenAI while Manim
codegen and QC stay on Claude — set ``SCRIPT_LLM=openai``.
"""
from __future__ import annotations

import os
import re
from pathlib import Path

from src import style as style_mod
from src.llm import strip_fences
from src.script_eval import Report, evaluate, judge, merge_judgement
from src.script_parser import ScriptParseError, parse_script

# Which model writes the scripts. Everything else stays on the pipeline default.
SCRIPT_PROVIDER = os.getenv("SCRIPT_LLM", "auto")

# Below this, another drafting pass is worth the tokens.
GOOD_ENOUGH_SCORE = 82

LANGUAGES = {
    "hinglish": (
        "Hinglish — conversational Hindi written in Latin script, with English "
        "kept for technical terms (force, velocity, integral, charge). This is "
        "how our presenters actually speak: 'Ab hum dono sides ko integrate "
        "karenge.' Never use Devanagari."
    ),
    "english": "Clear, plain English suited to a school or first-year student.",
}

SYSTEM_PROMPT = """You write scripts for short educational maths/physics videos \
that are animated with Manim and presented by an on-screen avatar.

Output a single markdown file and NOTHING else — no preamble, no code fences, \
no commentary. It must parse under this exact format:

---
title: <short title>
orientation: <landscape|portrait>
theme: <theme name>
chroma: <chroma preset>
speakers:
  narrator: { voice: <voice name> }
---

[narrator]
<one spoken line — this is what the presenter says out loud>
%% <director note: what the animation should do on this beat>
$$ <LaTeX for this beat, no $ delimiters inside> $$

Rules that make or break the render:
- Every beat starts with `[narrator]` on its own line. One idea per beat.
- The spoken line must read naturally out loud. It is narration, not a caption: \
never write "as shown in the figure" or refer to labels the viewer can't hear.
- Do NOT write LaTeX, symbols or markup inside the spoken line — write "x squared", \
not "$x^2$". The spoken line is fed to text-to-speech verbatim.
- `$$ ... $$` holds the equation for that beat. One equation per beat. Introduce \
an equation on the beat where the narration first mentions it.
- `%% ...` is a director note for the animator: say what should appear, move or \
be highlighted. Be concrete and visual.
- Photos: `![caption](assets/<file>.png)` on a beat that should show a real image. \
Only reference files that will actually exist — do not invent filenames unless \
the user asked for a photo beat.
- 8-14 beats. Each spoken line 8-30 words: long enough to breathe, short enough \
that the animation has one clear job.
- Build in order: state the problem, then each step, then the result. Never \
reference a quantity before the narration has introduced it.

MAKING IT SOUND SPOKEN — the lines are read aloud by a synthetic voice and \
lip-synced to a presenter, so they must survive being said out loud:
- Start every beat differently. Several beats opening the same way is the \
clearest sign a script was machine-written.
- Vary the length. Real speech mixes a short punchy line with a longer one; \
lines of uniform length sound flat no matter how good the words are.
- No digits and no symbols in the spoken line — write "do", "aadha", "x squared", \
never "2", "1/2", "x^2", "=", "%".
- No written-register connectives: no "furthermore", "hence we", "firstly", \
"as we can see". Say what a teacher standing at a board would say.
- Never point at the screen: no "as shown", "in the figure", "below". The \
listener hears this; they cannot follow a reference.
- Address one student who is trying, not a class.

Return only the markdown file."""


def _prompt(topic: str, *, language: str, orientation: str, theme: str,
            chroma: str, voice: str, beats: str, answer_image: str | None,
            extra: str) -> str:
    parts = [
        f"Topic: {topic}",
        "",
        f"Language for spoken lines: {LANGUAGES.get(language, LANGUAGES['english'])}",
        f"Orientation: {orientation}",
        f"Theme to put in the frontmatter: {theme}",
        f"Chroma preset to put in the frontmatter: {chroma}",
        f"Narrator voice name to put in the frontmatter: {voice}",
        f"Aim for {beats} beats.",
    ]
    if chroma != "none":
        parts.append(
            f"A presenter is composited into the {chroma.replace('_', ' ')} of the "
            f"frame, so the animation must not need that area — keep director "
            f"notes to the remaining space."
        )
    if answer_image:
        parts.append(
            f"\nThis video answers a question, and the final answer is a supplied "
            f"image. Add these frontmatter keys so it plays as the closing card:\n"
            f"  answer_image: {answer_image}\n"
            f"  answer_narration: <one short spoken line presenting the answer>\n"
            f"  answer_caption: <a few words naming what the image shows>"
        )
    if extra:
        parts.append(f"\nAdditional instructions from the user:\n{extra}")
    return "\n".join(parts)


def _sanitize(text: str) -> str:
    """Strip anything the model wrapped around the file."""
    text = strip_fences(text.strip())
    # If it chattered before the frontmatter, drop everything up to it.
    if not text.lstrip().startswith("---"):
        match = re.search(r"^---\s*$", text, re.MULTILINE)
        if match:
            text = text[match.start():]
    return text.strip() + "\n"


# Script drafting is a writing task, not a reasoning one, and a human edits the
# result anyway — medium effort produces the same quality far faster, which
# matters when someone is watching a progress bar in the dashboard.
def write_script(topic: str, *, language: str = "hinglish",
                 orientation: str = "landscape", theme: str = "midnight",
                 chroma: str = "none", voice: str = "George",
                 beats: str = "8-12", answer_image: str | None = None,
                 extra: str = "", effort: str = "medium",
                 max_attempts: int = 3, provider: str | None = None,
                 style: "style_mod.StyleGuide | None" = None,
                 use_judge: bool = False,
                 target_score: int = GOOD_ENOUGH_SCORE) -> tuple[str, Report]:
    """Draft a script, then keep fixing what doesn't sound spoken.

    Returns ``(markdown, report)``. The report is the final voice evaluation, so
    the caller can show what was fixed — and what still isn't right.
    """
    from src.llm import new_conversation

    guide = style if style is not None else style_mod.load()
    provider = provider or SCRIPT_PROVIDER

    prompt = _prompt(topic, language=language, orientation=orientation,
                     theme=theme, chroma=chroma, voice=voice, beats=beats,
                     answer_image=answer_image, extra=extra)
    style_section = guide.prompt_section()
    if style_section:
        prompt = f"{style_section}\n\n{'=' * 60}\n\n{prompt}"

    conv = new_conversation(SYSTEM_PROMPT, effort=effort, provider=provider)
    turn = prompt
    last_error: Exception | None = None
    best: tuple[str, Report] | None = None

    for attempt in range(1, max_attempts + 1):
        markdown = _sanitize(conv.send(turn))

        # --- does it parse? -------------------------------------------------
        try:
            # Parse without touching the filesystem — images may not exist yet.
            script = parse_script(markdown, resolve=False)
        except ScriptParseError as exc:
            last_error = exc
            print(f"   draft {attempt}: does not parse ({exc}) — asking for a fix")
            turn = (f"That did not parse: {exc}\n"
                    f"Return the corrected markdown file only.")
            continue
        if not script.segments:
            last_error = ScriptParseError("no [narrator] beats")
            turn = "That produced no [narrator] beats. Return a corrected file."
            continue

        # --- does it sound spoken? ------------------------------------------
        report = evaluate(script)
        if use_judge:
            report = merge_judgement(
                report, judge(script, samples=guide.sample_text(4000),
                              provider=provider))
        print(f"   draft {attempt}: parses, voice score {report.score}/100 "
              f"({len(report.failures)} failures, {len(report.warnings)} warnings)")

        if best is None or report.score > best[1].score:
            best = (markdown, report)
        if report.score >= target_score and report.ok:
            return markdown, report
        if attempt == max_attempts:
            break

        feedback = report.as_feedback()
        turn = (f"{feedback}\n\nReturn the complete corrected markdown file "
                f"only — keep every beat's meaning, change only the wording "
                f"that needs it.")

    if best is not None:
        # A script that parses but scores poorly is still worth handing over —
        # it's editable, and the report says exactly what to look at.
        return best

    raise ScriptParseError(
        f"Could not produce a parseable script after {max_attempts} attempts: "
        f"{last_error}"
    )


def save_script(markdown: str, path: str | Path) -> Path:
    dest = Path(path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(markdown, encoding="utf-8")
    return dest
