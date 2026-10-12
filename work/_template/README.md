# work/_template — what a video folder holds

`python3 tools/build_clip.py <QID> init` copies this folder to `work/<slug>/`,
fills in `qid`, `slug`, `subject` and `background`, and copies the subject's
plate from `assets/backgrounds/`. This README is not copied.

**A video folder holds design, never code.** The process — engine, render, QA,
gates — lives once in `tools/clip/` and `tools/`. The tools refuse a folder that
carries its own `.mjs`/`.py`/`engine.js`/`node_modules`, because a private copy
of the process is how a fix fails to reach the next video.

| file | what | written by |
|---|---|---|
| `video.json` | background, question card, answer pages, layout | `init`, then you |
| `theme.css` | design overrides of `tools/clip/engine/style.css` | you, rarely |
| `inputs.json` | the measured drop | `tools/ingest.py` |
| `out/caption_edit_part<N>.json` | caption wording per transcript word range | captions agent |
| `out/drift_adjudication_part<N>.json` | judgement on each cue the retime gate flags | captions agent |
| `spec/parts/design_part<N>.json` | the beats | design agent |
| `spec/parts/anchors_part<N>.json` | which caption lines each beat owns | design agent |
| `spec/route_part<N>.json` | SVG or Veo, per beat | design agent |
| `assets/svg/*.svg` | the diagrams, one per file | one SVG agent each |
| `state.json` | which steps are green, on which inputs; approvals | `tools/build_clip.py` |
| `out/` | everything generated | the tools |

## video.json

- `background` — the plate, relative to this folder (or the repo). Required;
  there is no default, because a default is how a biology video rendered over
  chemistry test tubes.
- `card` — the opening question card, on `card.part`. `question` is the exam
  sheet's wording (OCR errors fixed against the script, wording otherwise kept);
  `year` is what the pill says (`"2018, 2023"`); `marks` empty = no badge (the
  approved look); `last_line` = index of the last caption line the card covers
  (`build_spec.py --card-last`). Delete `card` for a part that carries the
  question forward instead of restating it.
- `answer` — the answer page image(s) the last part closes on, or `skip` with
  the reason when there are none yet.
- `suppress_captions` — segment kinds that carry no caption. Default
  `["equation"]`: while he reads an equation out, the ladder on the stage is
  the words, and a caption under it says them twice (user, 2026-09-21).
  Diagram segments keep their captions.
- `layout` — the theme's presenter geometry for `tools/composite.py`. Every
  video so far used `{"busy_w": 600, "floor": 1210}`.
