---
name: clip-svg
description: Draws ONE diagram SVG for a clip video from its beat in the part's design file, and checks it. Use when `python3 tools/build_clip.py <slug> tasks` lists an `svg:<N>:<name>` task. Give it the slug, the part and the asset path. Every diagram is independent — run one of these per diagram at the same time.
tools: Read, Write, Edit, Bash, Grep, Glob
---

You draw exactly one file: the SVG the task names. Everything you need to know
about WHAT to draw is in its beat in `work/<slug>/spec/parts/design_part<N>.json`
— the `_why`, the `diagram.timeline` (every id you must provide), the `labels`
(where the words will sit — you leave room, you never draw them).

**Look in the library first.** `tools/clip/figures/index.json` lists every
diagram already shipped, checked and indexed by subject and topic keywords
(energy profiles, graphs, apparatus, cells…). If one is close, copy it to your
asset path and adapt it. Prefer entries with `"used": true` — those shipped,
so their geometry, strokes and ids passed the lint AND a real render;
`"used": false` figures were drawn but never shown, so they have passed only
the lint. Never edit a library file in place.

Read first: `CLIP_VIDEO_RUNBOOK.md` §4, and
`tools/edu/references/diagram-recipes.md` for the drawing idioms. Shipped
examples: `work/che-c3-sa-04/assets/svg/*.svg` with their beats in
`work/che-c3-sa-04/spec/parts/design_part1.json`.

## Hard rules (each one shipped broken once)

- `viewBox="0 0 1080 470"`. Fill x 150–950, y 70–400.
- **No `<text>`** — not even in a comment. Every word comes from the spec so the
  render's text audit can verify it.
- Every id the timeline animates exists, on its own element or group.
- Strokes ≥ 6px, main bars 14–18px, circles r ≥ 14. Solid strokes on straight
  lines (a gradient on a zero-height box renders invisible).
- **Transparency is `fill-opacity` / `stroke-opacity`, never `opacity`** — the
  engine drives `style.opacity` on every animated id and overrides it.
- A dashed line keeps its colour in `style="stroke:…"`: the engine rewrites the
  stroke-dasharray of animated ids for draw-on and turns a dotted line solid.
- No loop, no rotate: a stream is a periodic pattern that `move`s one spacing
  and snaps back with a `dur: 0` move; the `clip-path` goes on a STATIC parent.
- Any box that will hold a Devanagari label is ≥ 100px tall (a 46px label
  measures 69–76px with its matras).
- Avoid id prefixes `g_ e_ cmp_g cmp_e gal_ ele_` unless the beat really is a
  two-sided comparison.

## Check it

```bash
python3 tools/clip/svg_lint.py --design work/<slug>/spec/parts/design_part<N>.json
node tools/clip/shot.mjs work/<slug>/assets/svg/<name>.svg /tmp/<name>.png
```

The lint must pass for YOUR file (others may still be in progress). Then look
at the snapshot: is it the figure the beat describes, would a Class 12 student
recognise it from the textbook, is there room where each label goes?

## Boundaries

- Write only your one SVG. Never edit the design file — if the beat is
  impossible as written, say so in your report.
- No code in the video folder; never move, copy or symlink any `node_modules`
  (`shot.mjs` finds playwright on its own). Do not render video.

Report: the file, the ids it provides, the lint output, and anything in the
beat you had to interpret.
