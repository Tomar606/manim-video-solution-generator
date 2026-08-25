# The Flow bridge

Google Flow, driven from the pipeline, with the tab in the background and you
doing something else.

Adapted from [pranshu0604/flow-bridge](https://github.com/pranshu0604/flow-bridge).
Two of that project's discoveries are load-bearing here and are worth knowing
before changing anything in `extension/`:

- **Flow's prompt box is a Slate editor that rejects synthetic input.** Setting
  `.value` or dispatching events leaves Send disabled. Text has to arrive as a
  *trusted* keystroke through the Chrome debugger protocol (`Input.insertText`),
  which is why the extension asks for the `debugger` permission and why Chrome
  shows a debugging banner while a run is going.
- **Scraping the UI to download a finished clip does not work.** Flow is a Radix
  SPA with hashed class names; the ⋮ button only renders on a genuine CSS
  `:hover` and its menu is a portalled overlay. The route that does work skips
  the UI: Flow embeds every clip's URL in the DOM as
  `/fx/api/trpc/media.getMediaUrlRedirect?name=<uuid>`, and handing those to
  `chrome.downloads.download` follows the redirect with session cookies attached.
  (Thumbnails carry `MEDIA_URL_TYPE_THUMBNAIL` and are filtered out.)

## What is different from upstream

**The run loop moved out of the page.** Upstream put its controls in an on-page
panel, so the Flow tab had to be in front of you for anything to happen. A PYQ
video's clips take minutes each and are reviewed and regenerated automatically,
so that was the one thing this could not inherit. Here the service worker owns
the tab and drives it entirely over CDP, which dispatches into the renderer and
does not care whether the tab is visible, foreground, or on the desktop you are
looking at. `content.js` is a status readout; the run works with it closed.

Two things break in a background tab, and both are handled in `background.js`:

| | |
|---|---|
| Slate drops input when `document.hasFocus()` is false | `Emulation.setFocusEmulationEnabled` makes the renderer believe it has focus |
| an MV3 worker is killed after 30s idle | a 20s timer calling a trivial extension API (what actually resets the idle timer — a pending `fetch` does not), plus a 30s alarm that restarts the poll loop if it was killed anyway |

**Python drives; the extension obeys.** Upstream served a list of prompts to the
browser and let it run. Our loop is not "fill N boxes" — it is submit, wait,
download, look at the frames, decide whether the animation is actually right,
rewrite the prompt, go again. None of that belongs in a service worker, so the
extension is reduced to a remote with eight verbs and everything else lives in
`src/veo.py`, where it is testable without a browser (`test_veo_flow.py`).

**Clips are collected one at a time.** Upstream queued several and matched them
to scenes by reversing DOM order. That is fine for an ad where every clip is the
same person in the same room. Here it would mean the student watching the wrong
process while the teacher describes this one, so each prompt is submitted alone
and the clip is whichever media key Flow did not have a moment ago.

**Consecutive clips are generated from each other.** Upstream's ad got its
continuity from the subject being the same person in the same room in every
prompt. Ours cannot: a topic that needs half a minute of continuous animation
gets it as several generations, and Veo remembers nothing between them. So the
frame a clip ends on is uploaded as the next clip's reference, and the seam
between them is graded before either is accepted. See `src/veo_sequence.py` and
the `sequence` route in `PIPELINE.md`.

## Setup, once

1. `chrome://extensions` → Developer mode → **Load unpacked** → `flow/extension/`
2. Open your Google Flow project in any tab. It can stay in the background.
3. `.venv-tools/bin/python video.py flow` — should print `extension connected`
   and the tab's URL.

There is no hot reload: after editing anything in `extension/`, reload the
extension **and** hard-reload the Flow page.

## Running

    video veo <project> --part 1

That starts the bridge itself, so `video flow --serve` is only needed if you want
the extension connected between runs.

## Reference images, and the one selector you have to fill in yourself

A generation can carry up to three images: the background plate, the figure as
the student's textbook prints it (`reference` on the beat), and — for beats in a
`sequence` — the frame the previous clip ended on. `src/veo_sequence.py` decides
what goes up and in what order; `PIPELINE.md` says why that order is what it is.

Two things about Flow's reference control are unknowable from here and are
handled rather than assumed:

- **It may take only one file.** `set_image` reads `multiple` off the input and
  attaches only what will fit, reporting the rest as `dropped`. The run prints
  what did not go in, because a chained clip silently missing its carry frame is
  a clip that looks perfectly fine on its own.
- **Emptying the input does not clear the chips.** Flow keeps its own state for
  the reference images it has rendered, so `clear_images` also clicks their
  remove buttons — if it knows the selector. `reference_clear` in
  `selectors.json` is **null** until somebody inspects that ✕ once and fills it
  in, and until then every sequenced run prints a warning. Guessing a selector
  here would be worse than leaving it empty: the failure is silent, and it is one
  clip's reference riding along into the clip after next.

`reference_panel` is the same story for the control that OPENS the panel, if
Flow only mounts the file input once it has been opened. Leave it null and open
the panel by hand once per session instead.

## When Flow moves its UI

Everything the pipeline touches is in `selectors.json`, and nothing else needs to
change. The failure looks like `prompt box not found` or `click target not
found`. Prefer a `data-` attribute or an `aria-label` over a class name — Flow's
classes are hashed and change on every deploy.

`plate_input` is the file input behind Flow's reference-image control. It is
often only mounted once you have opened that panel, so if `set_image` reports
`no file input matched`, open the panel by hand once and re-run.

## Files

    extension/manifest.json   permissions and matches
    extension/background.js   the entire driver: tab, CDP, downloads, poll loop
    extension/content.js      a read-only status panel
    selectors.json            every place we touch Flow's UI

and on the Python side:

    src/flow_bridge.py    the local server and the command/response protocol
    src/veo.py            the stage: beats -> prompts -> clips -> review -> fit
    src/veo_sequence.py   carrying the look from one clip into the next
    src/veo_prompts.py    writing and revising the prompt
    src/veo_qc.py         the visual check, and where a clip stops being usable
    src/veo_conform.py    cutting the tail and fitting the rest to the window
    src/veo_labels.py     the Devanagari labels that go over the clip
