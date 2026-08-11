---
name: video-qc
description: Review rendered video segments for defects and fix what QC finds — clipped equations, broken LaTeX, typos, content in the presenter zone, blank frames. Use when someone asks to check, review or QC a video, or asks what the QC report means.
---

# Reviewing a render

```bash
./bin/video qc <slug>            # Claude reviews sampled frames of every segment
```

Output lands in `projects/<slug>/qc/`:
- `report.md` — findings per segment, with the frames inline
- `report.json` — the same, machine-readable
- `frames/segment_NNN_*.png` — what was actually reviewed

QC reports; it never edits. Exit code 3 means at least one segment failed.

## Reading a finding

Each finding has a severity and names a specific defect. Confirm it against the
saved frame before acting — a finding is a claim, not a verdict, and fixing a
non-problem costs a full re-render.

Common findings and where the fix belongs:

| Finding | Real cause | Fix in |
|---|---|---|
| Equation runs off the frame | The scene didn't fit its group to the safe area | Director note: "keep the group inside the safe area"; re-render |
| Raw LaTeX / empty boxes | LaTeX missing, or a bad macro in the script | `./bin/video doctor`; or fix the `$$…$$` |
| Text overlapping | Too much on one beat | Split the beat in the script |
| Content in the presenter zone | Script direction ignored the chroma zone | Director note; check `chroma:` is what you meant |
| Blank frame | The animation ended early and padded | Usually harmless (the hold before the cut) — check the clip first |
| Misspelling | It's in the script | Fix `script.md` |

## Re-rendering one segment

Nothing re-renders a single beat in isolation yet — `background` walks the whole
script. For a quick check of one scene, render its generated file directly:

```bash
manim render --disable_caching -r 1920,1080 --fps 30 \
  projects/<slug>/manim_code/segment_003.py SegmentScene
```

## What not to report

Pacing, style, the absence of a presenter (composited later), and empty space
that is the reserved presenter zone are all expected. The QC prompt already
excludes these — if they show up in a report, the chroma settings in the script
are probably not what the author intended.
