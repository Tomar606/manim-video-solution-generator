"""Hand-written scene templates for beats that shouldn't vary between videos.

Some beats have exactly one right answer visually — a photo held on screen, an
answer card at the end. Generating those with an LLM buys nothing and costs
consistency, so they render from these fixed templates instead: no model call,
no repair loop, and byte-identical staging in every video we ship.

Each function returns a ``SegmentScene(ThemedScene)`` class body, the same shape
:mod:`src.scene_codegen` expects back from Claude, so the two paths converge at
``compose_file``.
"""
from __future__ import annotations

from src.script_models import DialogueSegment

# A photo beat: fade the image in, hold (with a slow push-in for stills), and
# pad to the narration length so A/V stays locked.
PHOTO_SCENE = '''class SegmentScene(ThemedScene):
    """Photo beat (template — not model-generated)."""

    def construct(self):
        target = {target:.2f}
        elapsed = 0.0
{caption_block}
        # Leave a beat of air, then reveal the photo and hold it.
        hold = max(target - elapsed - 1.4, 0.8)
        self.cue("reveal")
        elapsed += self.show_photo(0, hold=hold, run_time=0.9)
        self.pad_to(target, elapsed)
'''

# The answer card that closes a solution video. Same motion as a photo beat but
# it never drifts (the viewer is reading it) and it carries a standing label.
ANSWER_SCENE = '''class SegmentScene(ThemedScene):
    """Answer card (template — not model-generated)."""

    def construct(self):
        target = {target:.2f}
        elapsed = 0.0

        title = self.heading({title!r})
        self.top_caption(title)
        self.cue("impact")
        self.play(FadeIn(title, shift=DOWN * 0.15), run_time=0.5)
        elapsed += 0.5

        photo = self.photo(0, height=self.safe_height * 0.70)
        photo.move_to(self.safe_center + DOWN * 0.25)
        self.cue("reveal")
        self.play(FadeIn(photo, scale=0.97), run_time=0.8)
        elapsed += 0.8

        underline = self.underline(title)
        self.cue("ding")
        self.play(Create(underline), run_time=0.4)
        elapsed += 0.4

        # Hold still — the viewer is reading, so no drift here.
        self.pad_to(target, elapsed)
'''


def _caption_block(seg: DialogueSegment) -> str:
    """Optional on-screen caption above a photo, drawn from the image caption."""
    caption = seg.images[0].caption if seg.images else ""
    if not caption:
        return ""
    return (
        f"        cap = self.label({caption!r})\n"
        "        self.top_caption(cap)\n"
        "        self.play(FadeIn(cap, shift=DOWN * 0.15), run_time=0.5)\n"
        "        elapsed += 0.5\n"
    )


def photo_scene_source(seg: DialogueSegment, *,
                       answer_title: str = "Answer") -> str:
    """Return the scene class for an image-only beat."""
    target = float(seg.target_duration or 4.0)
    if seg.is_outro:
        return ANSWER_SCENE.format(target=target, title=answer_title)
    return PHOTO_SCENE.format(target=target, caption_block=_caption_block(seg))


def can_template(seg: DialogueSegment) -> bool:
    """True when this beat renders from a template instead of the LLM."""
    return seg.is_photo_beat
