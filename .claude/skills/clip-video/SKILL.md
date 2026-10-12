---
name: clip-video
description: Build a video from an already-shot HeyGen clip (the PROCESS.md track) with tools/build_clip.py running the machine steps and agents writing captions, designs and SVGs in parallel. Use when someone drops a HeyGen clip in inbox/<QID>/ and asks for the video, says "is clip ka video bana do", "build CHE-…", or asks where a clip video's build stands. Not for the projects/ Manim track (that is make-video).
---

# Building a clip video

`PROCESS.md` is the order; `CLIP_VIDEO_RUNBOOK.md` is the reasoning behind each
step. `tools/build_clip.py` enforces the order: it knows every step, its gate,
what it depends on, and which steps can run at the same time. You never type
the machine commands yourself — you run the runner, and you dispatch the
writing work to agents.

## The loop

```bash
python3 tools/build_clip.py <QID> init        # once: ingest + work/<slug>/ from work/_template
python3 tools/build_clip.py <slug> status     # where it stands
python3 tools/build_clip.py <slug> run        # every machine step that can run, in parallel, until none can
python3 tools/build_clip.py <slug> tasks      # the writing that is ready now (JSON)
```

1. **init**, then fill `video.json` → `card.question` (the sheet's wording, OCR
   errors fixed against the script) and `card.year`. Everything else has a
   working default. Tell the user if `init` reported no background.
2. **Announce, then `run` in the background** (Bash `run_in_background`). Right
   after ingest it starts transcription, presenter measurement and the question
   card together — and `design:<N>` is ready at the same moment, so dispatch the
   designers straight away; their SVG tasks follow while transcription runs. This machine is an 8GB M2: say what heavy steps are about to
   run, and never start a render the user has not agreed to.
3. **While it runs, dispatch every ready task at once** — one Agent call per
   task, all in a single message so they run concurrently:

   | task | agent | one per |
   |---|---|---|
   | `design:<N>` | `clip-designer` | part — ready right after ingest |
   | `captions:<N>` | `clip-captions` | part — reviews the machine draft |
   | `svg:<N>:<name>` | `clip-svg` | diagram |
   | `card_info`, `answer:<N>` | you / the user | video |

   Give each agent the slug, the part and (for SVGs) the asset path from the
   task. When they report back, `run` again: their gates re-check the work, and
   the next wave of tasks appears in `tasks`.
4. **The storyboard is a human gate.** When `status` shows `approve:<N>`
   waiting, show the user `work/<slug>/out/storyboard_part<N>.png`. Only after
   they approve: `python3 tools/build_clip.py <slug> approve --part <N>`. If they
   waive review, record it: `approve --part <N> --note "user: continue without
   review"`. Never approve on their behalf.
5. **`run` again** — render, intro card, composite and delivery follow on their
   own, each behind its gate. Delivery gates the file in `final/`, not the one
   before it.
6. **Log it** with the `video-build-log` agent at the end.

## When a gate fails

`status` names the step and its log (`work/<slug>/out/logs/<step>.log`). Fix
the INPUT — the captions, the design, the SVG — never the gate, and never a
tool to make one video pass. A step goes stale by itself when its inputs
change, so after a fix just `run` again; everything downstream re-runs, nothing
upstream does.

## Rules that stay true

- The video folder holds design only. Every tool refuses a folder carrying its
  own `.mjs`/`.py`/`engine.js`/`node_modules`. Agents must never move, copy or
  symlink `node_modules`.
- One renderer: `tools/clip/`. Never copy it, never copy an old `work/<slug>/`.
- Chemistry and physics are SVG-only; biology keeps Veo (`clips:<N>` tasks,
  generated after the storyboard is approved).
- `plan` prints the schedule and what it saves over running the same steps
  one after another.
