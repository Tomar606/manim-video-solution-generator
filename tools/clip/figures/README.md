# Figure library

Every diagram SVG from a shipped clip video that still passes
`tools/clip/svg_lint.py`, sorted by subject:

```
chemistry/<slug>--<name>.svg
physics/<slug>--<name>.svg
biology/<slug>--<name>.svg
index.json        one entry per figure, plus the files left out and why
build_index.py    rebuilds all of the above from work/
```

Each entry in `index.json` → `figures` has:

| field | what it is |
|---|---|
| `file` | path relative to this folder |
| `subject`, `video`, `beat` | where it shipped (`beats` lists every beat that drew it) |
| `shows` | what it shows: the beat's `_why`, or the SVG's own comment when the beat has none |
| `ids` | every element id in the SVG |
| `animated` | the ids that beat's timeline animated |
| `labels` | the words laid over it, with `x`/`y` as fractions of the 1080×470 stage |
| `topic_keywords` | English + Hindi topic words, then the figure's name and its Hindi labels |
| `used` | `false` = it was in the video's assets but no beat drew it, so it was never checked on screen |
| `lint_warnings` | id-prefix warnings (`g_`, `e_`, `cmp_`…) it carries |
| `source`, `also_in` | the original file, and byte-identical copies elsewhere in `work/` |

## Using it when drawing a diagram

1. Search `index.json` by `topic_keywords` or `subject`, e.g.
   `grep -n "सक्रियण ऊर्जा\|energy profile" tools/clip/figures/index.json`.
   Read `shows` and `labels` to judge how close a figure is.
2. Copy the closest one to the video's `assets/svg/<beat>.svg`. Do not point a
   design at a library file, and never edit a library file in place.
3. Adapt it: rename ids to the ones your beat's timeline animates, move the
   geometry to where your labels sit, delete what you do not need. Strip the
   id prefixes listed in `lint_warnings` unless your beat really compares two sides.
4. Lint it as usual: `python3 tools/clip/svg_lint.py --design work/<slug>/spec/parts/design_part<N>.json`.

Prefer figures with `"used": true`; `used: false` ones passed the lint but no
render ever showed them.

## Refreshing

After a video ships, run:

```bash
python3 tools/clip/figures/build_index.py          # copies + index.json
python3 tools/clip/figures/build_index.py --check  # exit 1 if the library is out of date
```

It only reads `work/`. It skips `work/_template`, any folder that
`tools/build_clip.py` has not delivered yet (its `state.json` has no finished
`deliver` step), and any `--skip <slug>`. The same inputs always give the same
output, and a second run writes nothing. To make a new topic searchable, add a
row to `LEXICON` in `build_index.py`. Never edit `index.json` or the copies by
hand: the next run overwrites them.
