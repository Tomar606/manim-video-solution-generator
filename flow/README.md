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
    src/veo_prompts.py    writing and revising the prompt
    src/veo_qc.py         the visual check, and where a clip stops being usable
    src/veo_conform.py    cutting the tail and fitting the rest to the window
    src/veo_labels.py     the Devanagari labels that go over the clip
