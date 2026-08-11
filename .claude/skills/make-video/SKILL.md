---
name: make-video
description: Produce an educational video end to end in this repo — create the project, draft and refine the script, render the animation, ingest the presenter clips, QC and composite. Use whenever someone asks to make, build, render or finish a video, or asks why a video stage failed.
---

# Making a video

The pipeline is one command with stages. Everything lives in `projects/<slug>/`,
and every stage is re-runnable, so prefer re-running a stage over hand-editing
its output.

```
./bin/video new "<topic>"        create the project + draft a script
./bin/video narrate <slug>       synthesize narration (sets all the timing)
./bin/video background <slug>    animate, render, assemble the Manim side
./bin/video avatar <slug>        briefs, or ingest dropped presenter clips
./bin/video qc <slug>            Claude reviews the rendered frames
./bin/video composite <slug>     key the presenter over the animation
./bin/video build <slug>         all of the above, in order
./bin/video status               where every project stands
```

## The order matters, and here is why

**Narration first, always.** Segment lengths come from the measured narration
audio, and every later stage reads those durations. Running `background` before
`narrate` fails on purpose rather than guessing timings.

**Background before composite.** Compositing keys the presenter onto the
conformed clips that `background` produced in `projects/<slug>/work/`.

**Avatar clips are usually not there yet.** That's the normal mid-production
state, not an error. `build` stops cleanly before compositing and leaves a
watchable background cut.

## Working on the script

The script *is* the video. To change what the video says or shows, edit
`projects/<slug>/script.md` and re-render — never patch generated scene code,
because the next render overwrites it.

Format essentials (full spec in `src/script_parser.py`):

- `[narrator]` starts a beat. The line under it is spoken aloud verbatim by TTS,
  so it must contain no LaTeX or markup — write "x squared", not `$x^2$`.
- `$$ ... $$` is the equation for that beat.
- `%% ...` is a director note passed to the animator, not spoken.
- `![caption](assets/photo.png){full,kenburns}` puts a real photograph on a beat.
- Frontmatter `answer_image:` appends the answer card as a final beat.

## When a stage fails

- **A segment won't render.** The repair loop already fed the traceback back to
  Claude `--max-attempts` times. Read the generated file in
  `projects/<slug>/manim_code/segment_NNN.py` and the error before re-running;
  usually the fix belongs in the script's director note. Use
  `--continue-on-error` to get a cut of everything else.
- **Equations render as blank boxes.** LaTeX isn't installed — run
  `./bin/video doctor`, or render in Docker.
- **Photo not found.** Paths resolve against the script's folder and the
  project's `assets/`. Put the file in `projects/<slug>/assets/`.
- **QC says fail.** Read `projects/<slug>/qc/report.md` — the frames are saved
  next to it. QC never edits anything; decide, then fix the script.

## Rules

- Don't hand-edit files under `manim_code/`, `work/`, `media/` or `final/` —
  they are build output and get overwritten.
- Don't invent image filenames in a script. Reference only files that exist in
  the project's `assets/`.
- Ask before re-running `script --force`; it overwrites a script someone may
  have edited by hand.
