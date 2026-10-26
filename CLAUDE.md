# Context for working on this repo

Read this before changing anything. It records *why* the pipeline is shaped the way it is: the
constraints that aren't visible from the code, and the decisions that look arbitrary until you know what
they avoid.

## What this is

One pipeline: **the kit** (`lab/kit_test/`). A HeyGen presenter clip, its caption file and a question ID
become an MP Board PYQ reel in any subject, delivered to a Final folder.
- [`lab/kit_test/STANDARD.md`](lab/kit_test/STANDARD.md): what a finished reel must be, taken from the four
  latest videos, which are the reference.
- The `reel` skill: the order of work.
- [`lab/kit_test/README.md`](lab/kit_test/README.md): setup on macOS and Windows, the gates, the files.
- [`lab/kit_test/ELEMENTS.md`](lab/kit_test/ELEMENTS.md): the element catalogue.

The people who run it are not technical. They drop files, review a page of frames, and watch the
delivered video. **You write every prompt, every plan and every fix.** Never ask them to edit a file,
write a prompt or run a command they did not ask for.

Older tracks (the Manim PYQ track, the reels track with `video.py`, the all-Veo route) were retired on
26 Oct 2026 and are preserved at the git tag `archive/pre-kit`. Do not resurrect them piecemeal; take the
idea and build it into the kit.

## The load-bearing ideas

**The presenter's audio is the clock.** Everything (captions, every element's entrance, every cut) is
cued to the moment a word is spoken: `W(line, word)` in the plan generator. The HeyGen SRT times are out by
up to 2.2 s both ways, so line times come from the Whisper word clock, or, without Whisper, from the
audio's own pauses (`tools/pause_align.py`).

**The plan is the source of truth.** `make_<id>_plans.py` writes `plan_<id>_p<N>.json`, and everything
downstream reads it. To change a video, change the generator and re-run it. Never hand-edit
`out/<plan>/timeline.js`, frames or renders.

**Correctness first.** Veo is for atmosphere: a place, an era, a feeling. Anything a student must
reproduce is drawn exactly, as an SVG/HTML element in `stage.html` or a Manim render in
`projects/<slug>/diagrams/`:
- a circuit, an apparatus, a reaction, a mechanism, a labelled structure, a graph;
- the mechanism's direction and order right;
- every label named as it is spoken;
- textbook colour conventions.

A generated clip that shows what the answer says is wrong is worse than no clip.

**Screen text organises; it does not repeat the caption.** A heading, a list that fills in, a comparison,
the one thing to remember set large. "No graphic" is a valid beat.

**One theme pack per video, never repeated.** Plate, fonts, card style, card backdrop and photo treatment
all come from the topic's world (Gandhi: khadi and 1930 sepia; Bhakti: manuscript pages and Varanasi).

**Gates, then delivery, and nothing else.** `tools/deliver.py` runs `tools/gates.py`, appends the answer
page and copies into the Final folder. It is the only way a reel is delivered. A skip prints its reason;
a skip is not a pass.

## Gotchas that cost time

- **Pillow needs raqm, or every Devanagari image is silently wrong.** Without it Pillow draws codepoints in
  storage order: `नियम` comes out `नयिम`, and nothing errors. On a Mac, run anything that draws Hindi with
  `DYLD_LIBRARY_PATH=/opt/homebrew/lib`. `tools/paper_header.py` refuses to run without shaping;
  `tools/doctor.py` checks it. Look at the rendered Hindi every time.
- **The question card's text is baked into the exam-sheet PNG.** Editing meta.json changes nothing on
  screen; rebuild the sheet with `tools/paper_header.py`.
- **A generation prompt draws what it names.**
  - Never write logo, watermark, badge or wordmark, not even as a negative.
  - No digits, percentages, pixel counts or layout zones.
  - Say "a tall vertical frame", and put text and decoration in the NEGATIVE list.
- **Flow burns a sparkle into every clip,** after generation, so no prompt prevents it.
  `tools/kit_veo.py clean` removes it and crops letterbox bars. `kit_veo_gate` refuses a reel that uses an
  uncleaned clip.
- **Flow's prompt bar remembers its last mode.** It was found on an image model at 16:9 with two outputs,
  which would have spent credits on pictures. Run `tools/kit_veo.py setup` before every batch.
- **Two projects ship a Flow bridge on port 8765.** Only this repo's "PYQ Flow Bridge" may be enabled.
- **A generated clip is never reversed to fill time.** Boomerang teaches rust un-rusting. Slow, loop or
  hold.
- **Never depict the Sikh Gurus, or any figure who must not be portrayed, in generated footage.** Show
  objects and places; faces come only from period paintings.
- **The presenter is never stretched.**
  - Scale him from a height only. A box with a width and a height squeezes him, and every frame is wrong
    by the same amount, so nobody sees it.
  - Always centred horizontally.
  - Full-frame he runs solid to the bottom edge, with no fade.
- **Captions never run under the question card.** That is a compile gate.
- **The answer page comes from the sheet's column AK** (the in-house page: handwriting, watermark), never
  column L (the textbook scan). `tools/sheet_fetch.py` takes the right one. Every reel ends on it, held
  7 s, whatever the narration says.
- **The sheets are readable by link, so their IDs are secrets in practice.** They live in `.env`, never in
  code or docs. This repo is public.
- **An 8 GB machine swaps, and the swap file eats the disk.**
  - When the disk reaches zero the machine freezes. `tools/machine_guard.py` refuses heavy work without
    room.
  - One heavy job at a time.
  - Only a restart frees the swap file.
- **A render uses the machine it is on.** Lanes scale with free memory and cores; encodes use the GPU's
  encoder when there is one (`tools/encoders.py`). Don't hard-code an encoder or a lane count anywhere.
- **A laptop idle-sleeps on battery and kills a render.** `render_reel.py` keeps it awake (caffeinate on
  macOS, SetThreadExecutionState on Windows).
- **The headless Chromium lives in the repo (`tools/edu/renderer/.browsers`), not the shared cache.**
  Other Playwright installs and cache purges emptied the shared one twice in one day, once mid-render,
  where it stalled the compositor at frame 3,000. The frame renderers set `PLAYWRIGHT_BROWSERS_PATH`
  themselves. Install with that variable set (see the kit README); `tools/doctor.py` checks it.
- **Never edit a shell script while it is running:** bash reads it as it goes. The render is Python for
  this reason, among others.
- **Manim, when used for an exact diagram:** Python 3.10–3.12. Hindi goes through `Text()` and formulae
  through `MathTex()`, never mixed in one string. Photos are `Group`, not `VGroup`.

## Conventions

- Every reel ends with `tools/deliver.py <slug>`, never a manual copy.
- Show the person the review page before rendering, and wait for their go.
- Delete rejected samples, trial stills and probes as soon as they are superseded.
- Photos come only from licences that allow commercial use and modification (`tools/fetch_photos.py`), each
  recorded in its folder's `credits.json`. Mixkit files are not redistributable: `tools/fetch_mixkit.py`
  rebuilds them, and they are gitignored.
- Don't commit `.env`, renders, frames, review pages or `inbox/`. `projects/<slug>/` keeps inputs only.
- New behaviour goes into the kit (a `stage.html` element, a compile check, a tool), so every video gets
  it. Never as a one-off script.
