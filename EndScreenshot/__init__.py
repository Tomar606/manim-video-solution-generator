"""EndScreenshot — the hand-written question-and-answer card a video ends on.

The video finishes on a still the viewer screenshots: the question and its full
answer, written out in a student's hand on ruled notebook paper. This package
makes that image, in two passes:

    step 1  TEMP        mint the base sheet through the image model
    step 2  MAIN PHOTO  write the question and answer onto it

Usage::

    from EndScreenshot import generate
    result = generate(question, answer,
                      sheet="EndScreenshot/assets/blank_ruled.jpeg",
                      style="EndScreenshot/assets/sample_hand.png",
                      out_dir="EndScreenshot/out")

or from the command line::

    python -m EndScreenshot --question-file ... --answer-file ...
    ./bin/video endscreenshot <project> --question-file ... --answer-file ...

Ported from the sibling ``notes-editor`` repo; see :mod:`EndScreenshot.prompts`
for the prompt lineage.
"""
from .api import EndScreenshotError, PAGE_SIZE
from .layout import (count_ruled_rows, normalize_lines, strip_links,
                     tag_content, usable_rows)
from .pipeline import draw_from_mockup, dry_run, generate
from .typeset import build_mockup, measure
from .prompts import PROMPT_VERSION, TEMP_PROMPT_VERSION

__all__ = [
    "generate", "dry_run", "draw_from_mockup", "build_mockup", "measure",
    "tag_content", "normalize_lines", "strip_links",
    "count_ruled_rows", "usable_rows",
    "EndScreenshotError", "PAGE_SIZE",
    "PROMPT_VERSION", "TEMP_PROMPT_VERSION",
]

# Default assets shipped with the feature.
from pathlib import Path as _Path

ASSETS = _Path(__file__).resolve().parent / "assets"
DEFAULT_SHEET = ASSETS / "blank_ruled.jpeg"
DEFAULT_STYLE = ASSETS / "sample_hand.jpg"
DEFAULT_OUT = _Path(__file__).resolve().parent / "out"
