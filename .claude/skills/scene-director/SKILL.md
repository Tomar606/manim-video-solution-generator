---
name: scene-director
description: Educational Video Scene Director — turn a teaching script into a complete scene-by-scene visual production plan (storyboard) for the topic section of a PYQ video. Use when producing a batch-2 video, when asked for a scene plan, storyboard, visual production plan or scene director output, or before authoring beats for any new video. Outputs a specification for the rendering agent, never rendering code.
---

# Educational Video Scene Director

Read `reference/director-prompt.md` — the full directive, verbatim, as supplied
by the user. It is the specification; follow it exactly.

Then read `reference/hard-constraints.md` — the defects this pipeline has
actually shipped. Every plan must satisfy them, and they OVERRIDE any visual
ambition in the directive: a beautiful plan that clips the presenter or overlaps
a caption is a failed plan.

## Working order

1. Read the topic's script (`projects/<slug>/script_bhaag.md`) — it carries the
   authored `On Screen:` directions, which are teaching intent, not decoration.
2. Read the recording (`projects/<slug>/lines_part<N>.json`) — the CLOCK, and the
   arbiter of what was actually said. The shoot paraphrases; a scripted visual
   with no spoken moment is dropped or moved, never forced in.
3. Read the question — what the exam asks the student to reproduce.
4. Produce the plan in the directive's output format.
5. Check it against `reference/hard-constraints.md` before handing it on.

## Scope

Plan the TOPIC TEACHING SECTION only. The opening, question card, ending, CTA,
answer page, background, captions, typography and avatar system are templates
that already exist — do not plan or redesign them. The first scene is the first
actual teaching moment.
