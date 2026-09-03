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

## Brave, and the permission that makes it look broken

Chrome is assumed everywhere below; Brave works and is what this was first run
on, with two differences that cost most of a session to find.

**Local Network Access blocks the bridge, silently.** Chromium 151 gates
requests to loopback behind a permission, and `LocalNetworkAccessForWorkers`
means an extension service worker is in scope. The failure has no error anywhere:
the TCP connection to 127.0.0.1:8765 is ESTABLISHED, and the HTTP request is
simply never delivered. From Python it looks exactly like an extension that was
never loaded; in the tab it looks like a permission dialog that does nothing when
you answer it, because a service worker has no tab for a prompt to attach to.

The fix is a policy allowlist rather than turning the feature off. On macOS,
`/Library/Managed Preferences/com.brave.Browser.plist`, root-owned:

```xml
<key>LocalNetworkAccessAllowedForUrls</key>
<array>
  <string>chrome-extension://YOUR_EXTENSION_ID</string>
  <string>http://127.0.0.1:8765</string>
  <string>http://localhost:8765</string>
</array>
```

Restart the browser and check `brave://policy`. LNA stays enforced everywhere
else. `--disable-features=LocalNetworkAccessChecks` also works and is worse: it
is browser-wide and has to be passed on every launch.

**The extension ID comes from the directory path.** An unpacked extension with no
`key` in its manifest is identified by where it lives, so moving or renaming this
repo changes the ID and the policy above silently stops matching — and the
symptom is the original one, a bridge that never connects with nothing logged.

## Two tools before you spend anything

    tools/flow_probe.py     free. Climbs a ladder: extension -> tab -> prompt box
                            -> submit button -> media list -> reference input ->
                            clearing it. Nothing is submitted. Run it first after
                            any Flow redesign; the rung that fails names the line
                            of selectors.json to edit.
    tools/flow_probe.py --find-clear
                            attaches an image, diffs the visible controls before
                            and after, and lists what appeared — which is how the
                            remove button is identified without guessing.
    tools/flow_smoke.py     ONE credit. Submit, wait, identify the clip, download
                            it, and ffprobe the result. This is the only thing
                            that exercises the half of the route the probe cannot.

## What live testing changed

Every item here passed review as correct code and was wrong against the real page.

- **The submit button is "Create", not "Generate", and the word is ambiguous.**
  Two visible controls contain it: the submit arrow, and an "Add media" dialog
  trigger. The text matcher prefers the SHORTEST match, which is the dialog. A
  run would have opened a dialog, submitted nothing, and then waited fifteen
  minutes per beat for a clip that was never queued. `generate_selector` is now
  set and takes precedence; see the comments in `selectors.json`.
- **An uploaded image is Flow media, with a URL shaped exactly like a clip's.**
  So "a media key that was not there before" does not mean "the clip" — the plate
  attached seconds earlier is also new. Snapshotting before the upload made the
  first poll return the plate, download a PNG named `.mp4`, and fail the visual
  review on a file that never decoded. The snapshot is now taken after the
  uploads settle, `list_media` reports whether each key came from a `<video>`,
  and both test fakes mint a media key on `set_image` so this cannot come back.
- **Flow mints a key when a generation is QUEUED, not when it finishes.** It
  arrives about 23 seconds after submit — far too fast to be a clip — rendered as
  an `<img>` preview, and the playable clip appears minutes later under a
  DIFFERENT key entirely. Measured on the first real generation: placeholder
  `8717f948…` as an `<img>`, finished clip `5174df01…` as a `<video>`. So waiting
  for "a new media key" returns when the render STARTS: the run downloads a
  JPEG, Chrome saves it under a `.jpeg` name of its own choosing, and the failure
  surfaces as "the download never landed" pointing nowhere near the cause. The
  wait is now for a key rendered by a `<video>`; a run that only ever sees
  placeholders says so rather than downloading one.
- **UPLOADING AN IMAGE IS NOT ATTACHING IT, and the difference is silent.** This
  is the most expensive thing in this file. `set_image` drives Flow's global
  file input, which uploads into the PROJECT LIBRARY. It does not reference the
  image from the prompt. Every signal said it had worked — the upload succeeded,
  the asset appeared in the project, the generation ran and returned a clip — and
  the clip came back on a plain white background Veo had invented, when the plate
  is dark navy with line art. Skill §15 is simply unenforceable without the
  second step, and the failure is invisible from the Python side.

  The second step is Flow's asset picker, on the prompt bar (the `add_2` button,
  `aria-haspopup="dialog"`). Clicking a tile in it attaches that asset and closes
  the dialog in one action — there is an "Add to Prompt" button too, but the
  dialog has already gone by the time it could be clicked. The proof that it
  worked is a reference CHIP on the prompt bar; `add_to_prompt` checks for one
  and fails if it is missing, because a generation submitted without a chip is a
  generation on an invented background.

  So the real sequence is: upload → wait for it to become Flow media → diff the
  media keys to learn its key → open the picker → click THAT tile → confirm the
  chip. `src/veo.py` does all five, and both test fakes refuse to generate while
  an uploaded asset is still unattached.
- **The frame review could not catch that on its own.** It compared the first
  frame against the last and asked whether the background DRIFTED — which a clip
  generated on an invented background passes cleanly, because its invented
  background is perfectly consistent with itself. The plate is now passed into
  the review as image 1 and check B0 compares against it; a different background
  is a `fail` before anything else is considered.
- **Uploads accumulate.** Every `set_image` adds an asset to the project and
  nothing removes it. Set `reference_clear` or they pile up across a run.
- **A generated clip carries an audio track** even when the prompt declares it
  silent, so §17 is not self-enforcing. `veo_conform.conform()` passes `-an` and
  drops it; nothing else should assume the file is mute.
- **`.enable` is not a prerequisite.** `Runtime.enable`, `DOM.enable` and
  `Page.enable` turn on a domain's EVENTS, and this worker subscribes to none —
  every verb uses commands, which do not need it. Treating them as required made
  a slow renderer fail the whole attach and report a hang pointing nowhere near
  the cause. They are best-effort now.
- **A background tab is often `status: "unloaded"`.** Not discarded — restored
  with the session and never loaded. It attaches cleanly and answers every DOM
  query with nothing: no editor, no buttons, and a title from Flow's marketing
  page. That reads as "Flow renamed its selectors" and is not. `attach()` now
  reloads on either flag and waits for the app to actually mount, because
  `status: "complete"` is about the document, not about React.
- **Flow is a Radix UI, and Radix opens things on `pointerdown`.** A synthetic
  `el.click()` reaches React's `onClick` and does nothing at all — `aria-expanded`
  just stays `"false"`, no error, no clue. This cost two separate
  investigations before the pattern was obvious: the settings menu "would not
  open", and `add_to_prompt` worked once by luck and then failed. Every one of
  those controls opened first try once the click became a real
  `Input.dispatchMouseEvent` at the element's centre. The plain Generate button
  is an ordinary `<button>` and works either way, which is exactly why the
  problem stayed hidden for so long. **Use CDP mouse events for anything that
  opens a menu, dialog, tray or tab; `.click()` only for plain buttons.**
- **The extension has no hot reload, and a stale build does not fail like stale
  code — it fails like a Flow redesign.** Twice in one session a "the picker
  will not open" hunt turned out to be code that was never reloaded. So
  `background.js` carries `BRIDGE_BUILD` and `src/flow_bridge.py` carries
  `EXPECTED_BUILD`; `wait_for_worker` compares them and raises `StaleExtension`
  immediately — outside the connect retry, because retrying a mismatch only
  burns the timeout before reporting the one thing that was wrong. **Bump both
  numbers whenever you add a verb or change one's contract.** The failure now
  reads "the loaded extension is build N but this code expects M. Reload it…",
  which is two seconds instead of a wasted generation.
- **A hung verb used to be permanent.** Nothing capped a chrome.* callback that
  never fired, and `looping` latched true, so the recovery alarm could never
  restart a stuck loop: one bad attach took the extension out until the browser
  was restarted. Verbs are now capped and the flag is released.

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
