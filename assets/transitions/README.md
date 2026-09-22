# Transitions and visual effects — same contract as sound

Drop a file into the folder for what it DOES. `python tools/sfx_registry.py
--transitions` indexes them.

| folder | what goes in | format |
|---|---|---|
| `divider/` | the edge between an animation panel and the presenter | PNG or JPG, a light shape on black |
| `overlay/` | a clip laid OVER a cut — paper tear, light leak, film burn | mp4/mov, light-on-black (luma keyed) or with real alpha |
| `matte/` | a greyscale shape that drives a reveal (white = show) | PNG, or an image sequence |

`divider/paper_tear_texture.jpg` is the live example: a white torn strip on
black, keyed by `tools/make_tear.py` into the divider the biology split-screen
uses. Anything in `divider/` should look like that — the SHAPE in white, the
background pure black, nothing else in frame.

## What is refused

- **Punch-in zooms.** Tried and rejected: *"the sudden zoom and back to normal
  does not look good because no clip or avatar is changing."* A camera move has
  to be motivated by something moving.
- **Anything that writes text.** The frame carries the animation and not one
  character; every label is typeset separately so it can be Devanagari.
- **Decoration with no teaching job** — sparkles, lens flares, vignettes,
  borders, film grain. If it does not help a Class 12 student understand,
  remember or reproduce the answer, it does not go on screen.
- **Reversing a clip to fill time.** Boomerang teaches rust un-rusting.
