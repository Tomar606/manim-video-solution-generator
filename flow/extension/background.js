/* PYQ Flow Bridge — the whole driver lives in this service worker.
 *
 * WHY IT IS SHAPED THIS WAY
 * -------------------------
 * The upstream flow-bridge extension ran its loop inside an on-page panel: you
 * had to be looking at the Flow tab, and it had to be the foreground tab, for
 * anything to happen. That is exactly what we cannot have — a PYQ video's clips
 * take minutes each and the machine has to stay usable meanwhile.
 *
 * So nothing here runs on the page. The service worker owns a tabId and drives
 * it entirely through the Chrome debugger protocol, which dispatches into the
 * renderer directly and does not care whether the tab is visible, foreground,
 * or on the desktop you happen to be looking at. `content.js` is a status panel
 * and nothing else; the run works with it absent.
 *
 * THE TWO THINGS A BACKGROUND TAB BREAKS, AND THE FIXES
 * ----------------------------------------------------
 *  1. `document.hasFocus()` is false in a background tab, and Slate — Flow's
 *     prompt editor — drops input when the document is not focused. The fix is
 *     `Emulation.setFocusEmulationEnabled`, which makes the renderer believe it
 *     has focus. Without it the prompt box stays empty and Send stays disabled,
 *     silently.
 *  2. An MV3 service worker is killed after 30 seconds idle, which would end the
 *     run mid-clip. Two belts: a 20s timer calling a trivial extension API
 *     (that is what actually resets the idle timer — a pending fetch does not),
 *     and a 30s alarm that wakes the worker and restarts the poll loop if it
 *     was killed anyway. `looping` is a module global, so a restarted worker
 *     sees it false and picks the loop back up.
 *
 * PROTOCOL
 * --------
 * Python is the driver; this worker is a dumb remote. It long-polls
 * GET /job for one small command at a time and POSTs the result to /event.
 * Retries, prompt revision and the visual check all live in Python, where they
 * can be tested without a browser.
 */

const BRIDGE = "http://127.0.0.1:8765";

/* Bumped whenever a verb is added or its contract changes. There is no hot
 * reload for an unpacked extension, and a stale build does not fail like a
 * stale build — it fails like a Flow redesign, which is a much more expensive
 * thing to chase. Twice in one session a "the picker will not open" hunt turned
 * out to be code that was simply never reloaded. `ping` reports this and
 * src/flow_bridge.py refuses to run against a mismatch. */
const BRIDGE_BUILD = 14;
const FLOW_URL_RE = /^https:\/\/(labs\.google\/fx\/.*tools\/flow|flow\.google)/i;

let looping = false;      // false again whenever the worker is restarted
let tabId = null;
let attached = false;

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

/* Every await in this worker is a chrome.* callback, and a callback that never
 * fires is not hypothetical — `chrome.debugger.attach` does exactly that on some
 * builds. Without this the loop parks on it forever, and because `looping` stays
 * true the recovery alarm returns immediately and can never revive it: one hung
 * verb takes the extension out until the browser is restarted, with no error
 * anywhere. Racing a timer turns that into an error message on the Python side,
 * which is a bad run instead of a dead extension.
 */
function withTimeout(promise, ms, what) {
  let timer;
  return Promise.race([
    promise.finally(() => clearTimeout(timer)),
    new Promise((_, rej) => {
      timer = setTimeout(
        () => rej(new Error(what + " did not return within " + Math.round(ms / 1000) + "s")),
        ms);
    }),
  ]);
}

// Per-verb ceilings. `download` is the only genuinely slow one; everything else
// is a DOM call that either answers at once or is broken.
const VERB_TIMEOUT = { download: 900000, set_image: 180000, clear_images: 180000 };
const DEFAULT_VERB_TIMEOUT = 120000;

// ---------------------------------------------------------------- keepalive --
// Calling an extension API resets the 30s idle timer. An in-flight fetch does
// not, which is why the long poll alone is not enough to stay alive.
setInterval(() => {
  try { chrome.runtime.getPlatformInfo(() => void chrome.runtime.lastError); } catch (e) {}
}, 20000);
chrome.alarms.create("keepalive", { periodInMinutes: 0.5 });
chrome.alarms.onAlarm.addListener(() => loop());
chrome.runtime.onStartup.addListener(() => loop());
chrome.runtime.onInstalled.addListener(() => loop());

// ------------------------------------------------------------------- debug ---
function cdp(method, params) {
  return new Promise((resolve, reject) => {
    chrome.debugger.sendCommand({ tabId }, method, params || {}, (res) => {
      const err = chrome.runtime.lastError;
      if (err) reject(new Error(method + ": " + err.message));
      else resolve(res);
    });
  });
}

/* THE UPLOAD INPUT IS NEVER IN THE DOM.
 *
 * `findImageInput` searched the flattened tree with pierce:true and found
 * nothing, on a picker that was open, on its Uploads tab, in a project full of
 * files uploaded the same way by hand. Flow creates an <input type=file>, calls
 * .click() on it and throws it away — it is never attached, so no selector can
 * ever reach it and the old error ("open the panel once") asked a human to fix
 * something that was not broken.
 *
 * Page.setInterceptFileChooserDialog suppresses the native chooser and reports
 * the input's backendNodeId in Page.fileChooserOpened. That id is the only
 * handle the input ever has, and DOM.setFileInputFiles accepts it. This is the
 * same mechanism Puppeteer's fileChooser uses.
 */
let fileChooser = null;
chrome.debugger.onEvent.addListener((src, method, params) => {
  if (tabId != null && src.tabId === tabId && method === "Page.fileChooserOpened") {
    fileChooser = params;
  }
});

chrome.debugger.onDetach.addListener((src) => {
  if (src.tabId === tabId) attached = false;
});
chrome.tabs.onRemoved.addListener((id) => {
  if (id === tabId) { tabId = null; attached = false; }
});

/* Flow's per-clip editor lives at /project/<id>/edit/<clip>, and it passes every
 * test the generation view passes: same origin, /project/ in the path, a Slate
 * editor present on the page. But its editor is the "Describe your edits" box,
 * not the prompt bar, so a run that lands there types into the wrong control and
 * reports "prompt did not land in the editor" — which reads like a broken
 * selector or a Flow redesign rather than like the wrong page, and costs an
 * afternoon. Rank the generation view first, and report the URL either way so
 * the caller can refuse what it was handed. */
const FLOW_EDIT_RE = /\/project\/[^/]+\/edit\//i;

async function findFlowTab() {
  const tabs = await chrome.tabs.query({});
  const flow = tabs.filter((t) => t.url && FLOW_URL_RE.test(t.url));
  const gen = flow.find((t) => /\/project\//.test(t.url) && !FLOW_EDIT_RE.test(t.url));
  return gen || flow.find((t) => /\/project\//.test(t.url)) || flow[0] || null;
}

async function attach() {
  if (attached && tabId != null) {
    try { await chrome.tabs.get(tabId); return; }      // still there
    catch (e) { attached = false; tabId = null; }      // closed under us
  }
  const tab = await findFlowTab();
  if (!tab) {
    throw new Error("no Google Flow tab is open — open your Flow project in any tab (it may stay in the background)");
  }
  tabId = tab.id;
  // A background tab gets frozen, and eventually discarded, by the browser's
  // memory saver. A frozen renderer completes the debugger attach and then
  // answers no CDP command at all, which is indistinguishable from a hang. Ask
  // for it to be left alone, and if it has already been discarded, reload it —
  // a discarded tab has no renderer to drive.
  try { await chrome.tabs.update(tabId, { autoDiscardable: false }); } catch (e) {}
  // TWO different flags mean "this tab has no live document", and checking only
  // the obvious one is not enough. `discarded` is the memory saver reclaiming a
  // tab; `status === "unloaded"` is a tab that was restored with the session and
  // never actually loaded, which is the normal state of a background tab you
  // opened and did not click. Both attach cleanly and then answer every DOM
  // query with nothing — zero buttons, no editor, and a title from the marketing
  // page rather than the app.
  if (tab.discarded || tab.status === "unloaded") {
    await chrome.tabs.reload(tabId);
    for (let i = 0; i < 60; i++) {
      await sleep(500);
      const t = await chrome.tabs.get(tabId);
      if (!t.discarded && t.status === "complete") break;
    }
  }
  // Each step is timed and named separately. When attaching fails the useful
  // question is always WHICH call stopped answering — a refused attach is a
  // permission or another debugger client, a hung Runtime.enable is a wedged
  // renderer, and the two want different fixes.
  try {
    await withTimeout(new Promise((res, rej) => chrome.debugger.attach({ tabId }, "1.3", () => {
      const e = chrome.runtime.lastError;
      if (!e) return res();
      // Two different failures share the words "already attached", and treating
      // them alike is how a run gets a confusing error three calls later:
      //
      //   "Already attached to the target with given id"  -> OURS. Benign; the
      //       worker restarted and the old session is still live. Carry on.
      //   "Another debugger is already attached to the tab" -> SOMEBODY ELSE'S.
      //       DevTools, or the other unpacked flow extension. We are NOT
      //       attached, so calling res() here sets `attached = true` on a lie
      //       and the next sendCommand fails with "Debugger is not attached",
      //       which points nowhere near the real cause.
      if (/another debugger/i.test(e.message)) {
        return rej(new Error(
          "another debugger is already attached to the Flow tab (" + e.message +
          "). Close DevTools on that tab, and disable any other Flow extension " +
          "that holds the debugger permission."));
      }
      if (/already attached/i.test(e.message)) return res();
      rej(new Error(e.message));
    })), 20000, "chrome.debugger.attach");
    attached = true;
    // BEST EFFORT, on purpose. `.enable` turns on a domain's EVENTS, and this
    // worker subscribes to none of them — every verb here uses commands
    // (Runtime.evaluate, DOM.getDocument, Input.*), and CDP commands do not
    // require their domain to be enabled. Treating these as prerequisites made
    // a slow or frozen renderer fail the whole attach, which is how a working
    // setup reported "attach timed out" and pointed at the wrong thing.
    // If the renderer really is unreachable, the first real verb says so.
    for (const domain of ["Runtime", "DOM", "Page"]) {
      try {
        await withTimeout(cdp(domain + ".enable"), 8000, domain + ".enable");
      } catch (e) {
        console.warn("[flow-bridge] " + domain + ".enable: " + e.message +
                     " — continuing, commands do not need it");
      }
    }
    // THE line that makes a background tab work at all. See the header. It is
    // allowed to fail — a foreground tab does not need it — but it is NOT
    // allowed to hang, which a bare try/catch would not have caught.
    try {
      await withTimeout(cdp("Emulation.setFocusEmulationEnabled", { enabled: true }),
                        10000, "Emulation.setFocusEmulationEnabled");
    } catch (e) {
      console.warn("[flow-bridge] focus emulation unavailable:", e.message);
    }
    // `status === "complete"` says the DOCUMENT finished loading. Flow is a
    // client-rendered SPA, so at that moment the page can still be an empty
    // shell — which is indistinguishable, from a selector's point of view, from
    // Flow having renamed everything. Waiting for the app to actually mount is
    // what stops "prompt box not found" from being reported for a page that
    // simply had not drawn it yet.
    for (let i = 0; i < 40; i++) {
      let n = 0;
      try {
        const r = await withTimeout(cdp("Runtime.evaluate", {
          expression: "document.querySelectorAll('button,[role=\"button\"]').length",
          returnByValue: true,
        }), 5000, "readiness check");
        n = (r && r.result && r.result.value) || 0;
      } catch (e) { /* renderer still coming up */ }
      if (n > 0) break;
      await sleep(500);
    }
    await chrome.storage.session.set({ tabId, flowUrl: tab.url });
  } catch (e) {
    // Leave nothing half-attached: the next call would otherwise skip attach()
    // entirely on the strength of `attached` and fail somewhere less obvious.
    attached = false;
    try { await chrome.debugger.detach({ tabId }); } catch (_) {}
    throw new Error("attaching to the Flow tab failed at " + e.message);
  }
}

/** Evaluate in the page and return the value. Throws on a page-side exception. */
async function evaluate(expression) {
  await attach();
  const r = await cdp("Runtime.evaluate", {
    expression: "(function(){" + expression + "})()",
    returnByValue: true,
    awaitPromise: true,
    userGesture: true,
  });
  if (r.exceptionDetails) {
    const d = r.exceptionDetails;
    throw new Error("page: " + ((d.exception && d.exception.description) || d.text));
  }
  return r.result && r.result.value;
}

// ---------------------------------------------------------------- commands ---

const PROMPT_FALLBACK =
  "var el = document.querySelector(SEL) " +
  "|| document.querySelector('[data-slate-editor=\"true\"]') " +
  "|| document.querySelector('[contenteditable=\"true\"]') " +
  "|| document.querySelector('textarea');";

/** Insert text into Flow's Slate editor as a trusted keystroke. */
async function setPrompt(text, selector) {
  const sel = JSON.stringify(selector || '[data-slate-editor="true"]');
  const find = PROMPT_FALLBACK.replace("SEL", sel);

  const found = await evaluate(find + `
    if (!el) return null;
    el.scrollIntoView({block:'center'});
    el.focus();
    if (el.isContentEditable) {
      var r = document.createRange(); r.selectNodeContents(el);
      var s = window.getSelection(); s.removeAllRanges(); s.addRange(r);
    } else if (el.select) { el.select(); }
    return el.tagName + (el.getAttribute('contenteditable') ? '[contenteditable]' : '');
  `);
  if (!found) throw new Error("prompt box not found (tried " + sel + ")");

  // Select-all then insert, both as trusted events: Slate ignores .value and
  // ignores synthetic InputEvents, and leaves Send disabled either way.
  const mod = { modifiers: 4, key: "a", code: "KeyA", windowsVirtualKeyCode: 65 };
  await cdp("Input.dispatchKeyEvent", Object.assign({ type: "keyDown" }, mod));
  await cdp("Input.dispatchKeyEvent", Object.assign({ type: "keyUp" }, mod));
  await cdp("Input.insertText", { text });
  await sleep(200);

  const got = await evaluate(find + `
    return el ? (el.innerText || el.value || "").trim() : "";
  `);
  // Compare squashed: Slate normalises whitespace and line breaks.
  const norm = (s) => (s || "").replace(/\s+/g, " ").trim();
  const want = norm(text), have = norm(got);
  if (have.length < Math.min(40, want.length)) {
    throw new Error("prompt did not land in the editor (box holds " + have.length +
                    " chars, expected " + want.length + ")");
  }
  return { chars: have.length, editor: found };
}

/** Find Flow's reference-image file input and describe what it will accept. */
async function findImageInput(selector, openSelector) {
  await attach();
  const sel = selector || 'input[type="file"]';
  let doc = await cdp("DOM.getDocument", { depth: -1, pierce: true });
  let q = await cdp("DOM.querySelectorAll", { nodeId: doc.root.nodeId, selector: sel });
  let nodes = (q && q.nodeIds) || [];
  if (!nodes.length) {
    // Flow mounts its uploader lazily: after a hard reload the input does not
    // exist until the asset picker has been opened once. Opening it here is the
    // whole fix — the alternative was an error telling a human to go and click
    // something, in a pipeline whose entire point is running unattended.
    // Open with the CONFIGURED selector, not with a guess. This used to pass
    // null, which falls through to a heuristic looking for an `add_2` ligature
    // on a dialog trigger — and Flow's opener is now labelled "Add ingredients"
    // and carries no such text, so the heuristic found nothing, the input was
    // never mounted, and every run died telling a human to go and click
    // something. `reference_open` was already in selectors.json and already
    // matched; it simply was not being used here.
    await openPicker(openSelector || null);
    await sleep(1200);
    doc = await cdp("DOM.getDocument", { depth: -1, pierce: true });
    q = await cdp("DOM.querySelectorAll", { nodeId: doc.root.nodeId, selector: sel });
    nodes = (q && q.nodeIds) || [];
    try {
      await evaluate(`document.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true})); return 1;`);
    } catch (e) {}
  }
  if (!nodes.length) return null;      // the caller falls back to the chooser
  // Prefer one that declares it accepts images.
  let target = nodes[0], attrs = [];
  for (const id of nodes) {
    const d = await cdp("DOM.describeNode", { nodeId: id });
    const a = (d.node && d.node.attributes) || [];
    const i = a.indexOf("accept");
    if (i >= 0 && /image/i.test(a[i + 1] || "")) { target = id; attrs = a; break; }
    if (id === target) attrs = a;
  }
  // `multiple` is a boolean attribute: present at all means true.
  return { nodeId: target, multiple: attrs.indexOf("multiple") >= 0 };
}

/* Attach reference images to the next generation, by local file path.
 *
 * `paths` arrives ordered most-important-first (see src/veo_chain.py: the carry
 * frame outranks the plate, which outranks the textbook scan). That order is
 * load-bearing rather than cosmetic, because Flow's control may take only one
 * file — when it does, the extras are dropped here and `used` reports how many
 * actually went in, so Python can say what the generation was missing instead of
 * quietly producing an unchained clip that looks fine on its own.
 */
async function setImage(paths, selector, openSelector) {
  // The DOM path first: if a Flow build ever does mount a real input, use it —
  // it is one call and cannot be affected by a moved button.
  const input = await findImageInput(selector, openSelector);
  if (input) {
    const files = input.multiple ? paths : paths.slice(0, 1);
    await cdp("DOM.setFileInputFiles", { nodeId: input.nodeId, files: files });
    return { input: input.nodeId, files: paths.length, used: files.length,
             multiple: input.multiple, dropped: paths.slice(files.length),
             via: "dom" };
  }
  return await uploadViaChooser(paths, openSelector);
}

/* Upload by intercepting the file chooser Flow's own button opens.
 *
 * ONE FILE PER CALL. src/veo.py already uploads one at a time on purpose — the
 * media keys are UUIDs, so uploading several and diffing the set afterwards
 * leaves no way to say which key is which, and attaching the wrong picture
 * looks exactly like attaching the right one. */
async function uploadViaChooser(paths, openSelector) {
  await attach();
  await cdp("Page.enable", {});
  await cdp("Page.setInterceptFileChooserDialog", { enabled: true });
  fileChooser = null;
  try {
    if (!(await openPicker(openSelector || null))) {
      throw new Error("could not open Flow's asset picker — check `reference_open` " +
                      "in flow/selectors.json");
    }
    // The button that opens the chooser. Matched on its own text rather than a
    // selector: it carries no aria-label and no stable class, and its ligature
    // ("upload") is the only thing about it that has not moved.
    const at = await evaluate(`
      var pane = document.querySelector('.cdk-overlay-pane') || document;
      var t = [...pane.querySelectorAll('button,[role=button]')]
        .find(e => e.offsetParent !== null && /upload media/i.test(e.innerText || ""));
      if (!t) return null;
      t.scrollIntoView({block:'center'});
      var r = t.getBoundingClientRect();
      return {x: Math.round(r.left + r.width/2), y: Math.round(r.top + r.height/2)};`);
    if (!at) {
      throw new Error("no 'Upload media' control in Flow's asset picker — the " +
                      "picker opened but the upload button was not found");
    }
    const pt = { x: at.x, y: at.y, button: "left", clickCount: 1 };
    await cdp("Input.dispatchMouseEvent", Object.assign({ type: "mouseMoved", buttons: 0 }, pt));
    await cdp("Input.dispatchMouseEvent", Object.assign({ type: "mousePressed", buttons: 1 }, pt));
    await cdp("Input.dispatchMouseEvent", Object.assign({ type: "mouseReleased", buttons: 0 }, pt));

    for (let i = 0; i < 60 && !fileChooser; i++) await sleep(250);
    if (!fileChooser) {
      throw new Error("clicked 'Upload media' but no file chooser opened within " +
                      "15s — the click may not have reached the button");
    }
    const files = paths.slice(0, 1);
    await cdp("DOM.setFileInputFiles",
              { backendNodeId: fileChooser.backendNodeId, files: files });

    // AND THEN MAKE IT VISIBLE, which is not the same as uploading it.
    //
    // listMedia reads media URLs out of the DOM, so an asset Flow has accepted
    // but is not rendering does not exist as far as the caller is concerned.
    // src/veo.py diffs the media set before and after to learn the new asset's
    // key, so with the picker closed that diff stays empty and the upload times
    // out — the file sitting at the top of Flow's own Uploads list the whole
    // time, which is exactly what it did. Switching to Uploads renders it.
    const base = String(files[0]).split("/").pop();
    let shown = false;
    for (let i = 0; i < 40 && !shown; i++) {
      await sleep(500);
      shown = await evaluate(`
        var pane = document.querySelector('.cdk-overlay-pane');
        if (!pane) return false;
        var tab = [...pane.querySelectorAll('[role=tab]')]
          .find(e => /uploads/i.test(e.innerText || ""));
        if (tab && tab.getAttribute('aria-selected') !== 'true') tab.click();
        return (pane.innerText || "").indexOf(${JSON.stringify(base)}) >= 0;`);
    }
    return { files: paths.length, used: files.length,
             dropped: paths.slice(files.length), via: "chooser",
             mode: fileChooser.mode, name: base, listed: shown };
  } finally {
    // Leaving interception on would swallow a chooser somebody opens by hand.
    try { await cdp("Page.setInterceptFileChooserDialog", { enabled: false }); } catch (e) {}
    fileChooser = null;
  }
}

/* Drop whatever is already attached, before attaching this generation's images.
 *
 * Emptying the file input is necessary and is NOT sufficient: Flow keeps its own
 * React state for the chips it renders, and clearing the DOM input leaves those
 * on screen and still attached to the next submit. The last clip's final frame
 * silently riding along into the clip after next is the exact failure this
 * whole route exists to avoid, so the remove buttons get clicked too when a
 * selector for them is known.
 *
 * `reference_clear` in selectors.json is null until somebody inspects the panel
 * once and fills it in — and a null is honest rather than lazy. Guessing a
 * selector for a remove button that might be a chip's ✕, a context menu or a
 * drag-out gives an extension that reports success and clears nothing.
 */
async function clearImages(selector, clearSelector, openSelector) {
  // No DOM input is the normal case now (see uploadViaChooser); there is then
  // nothing to empty, and the chips are cleared by their own buttons below.
  const input = await findImageInput(selector, openSelector);
  if (input) await cdp("DOM.setFileInputFiles", { nodeId: input.nodeId, files: [] });
  let clicked = 0;
  if (clearSelector) {
    clicked = await evaluate(`
      var n = 0;
      for (const el of document.querySelectorAll(${JSON.stringify(clearSelector)})) {
        if (el.offsetParent === null) continue;
        el.click(); n++;
      }
      return n;
    `);
    await sleep(300);
  }
  return { cleared: true, removed: clicked, knows_clear_button: !!clearSelector };
}




/* A real mouse click at page coordinates. Everything in Flow that opens, picks
 * or confirms is Radix, and Radix acts on pointerdown — el.click() reaches
 * React's onClick and does nothing, with no error and no clue. */
async function realClick(x, y) {
  const pt = { x: Math.round(x), y: Math.round(y), button: "left", clickCount: 1 };
  await cdp("Input.dispatchMouseEvent", Object.assign({ type: "mouseMoved", buttons: 0 }, pt));
  await cdp("Input.dispatchMouseEvent", Object.assign({ type: "mousePressed", buttons: 1 }, pt));
  await cdp("Input.dispatchMouseEvent", Object.assign({ type: "mouseReleased", buttons: 0 }, pt));
}

/* The reference chips on the prompt bar, by their actual signature.
 *
 * Learned by watching the attach done by hand rather than guessed: an attached
 * reference renders as a ~50x50 control that CONTAINS AN <img> and whose own
 * text is "cancel" — the Material ligature for its X. So the chip and its remove
 * button are one element, which is also why the remove control could never be
 * found by looking for a separate button.
 *
 * Every previous version of this counted images by size and position instead,
 * and with the asset-library panel open that reported twelve chips on a prompt
 * bar holding none. A wrong count here is worse than no count, because "a chip
 * appeared" is the proof that the plate was actually attached — and a run that
 * believes a library thumbnail is generating on an invented background.
 */
function chipsJs() {
  return `
    var chips = [...document.querySelectorAll('button,[role="button"]')].filter(function (el) {
      if (!el.querySelector('img')) return false;
      var t = (el.innerText || '').trim().toLowerCase();
      if (t.indexOf('cancel') < 0) return false;
      var r = el.getBoundingClientRect();
      return r.width > 20 && r.width < 160 && r.height > 20 && r.height < 160;
    });
  `;
}

/* Remove every reference chip from the prompt bar.
 *
 * Attaching is additive, so without this a run stacks references: the second
 * clip of a sequence would carry its own carry frame PLUS the first clip's
 * plate, and Veo blends them. It bit on the very first run that attached
 * anything — a chip left behind by a manual test rode along into the next
 * generation, which then ran with two references and neither the operator nor
 * the logs would have said so.
 *
 * The chip's remove control only exists on hover in most builds, so this
 * dispatches a real pointerover/mouseover before looking for it. `selector` is
 * `reference_chip_clear` from selectors.json when the exact control is known;
 * without it we fall back to a small ✕/close button inside the chip.
 */
async function clearPromptRefs(selector) {
  await attach();
  let removed = 0;
  for (let pass = 0; pass < 10; pass++) {
    const got = await evaluate(chipsJs() + `
      if (!chips.length) return {done:true, left:0};
      var c = chips[0];
      c.scrollIntoView({block:'center'});
      var r = c.getBoundingClientRect();
      return {x: Math.round(r.left + r.width/2), y: Math.round(r.top + r.height/2),
              left: chips.length};
    `);
    if (got && got.done) return { removed: removed, left: 0 };
    // Real mouse: this is a Radix control like everything else here.
    const pt = { x: got.x, y: got.y, button: "left", clickCount: 1 };
    await cdp("Input.dispatchMouseEvent", Object.assign({ type: "mouseMoved", buttons: 0 }, pt));
    await cdp("Input.dispatchMouseEvent", Object.assign({ type: "mousePressed", buttons: 1 }, pt));
    await cdp("Input.dispatchMouseEvent", Object.assign({ type: "mouseReleased", buttons: 0 }, pt));
    removed++;
    await sleep(800);
  }
  const left = await evaluate(chipsJs() + `return chips.length;`);
  return { removed: removed, left: left };
}

/* Attach an already-uploaded asset to the NEXT generation.
 *
 * THIS IS THE STEP THAT WAS MISSING, and its absence is silent. `setImage`
 * drives Flow's global "Add media" input, which uploads into the PROJECT
 * LIBRARY — it does not reference the image from the prompt. Everything looked
 * right: the upload succeeded, the asset appeared, the generation ran. It just
 * ran with no reference at all, so Veo invented its own background and threw
 * away the plate the clip has to be spliced onto. Skill §15 is unenforceable
 * without this.
 *
 * The picker is a Radix dialog on the prompt bar. Clicking a tile attaches it
 * and closes the dialog in one go — there is an "Add to Prompt" button too, but
 * by the time it could be clicked the dialog has already gone.
 */
/* THE PAGE-SIDE HELPERS EVERY PICKER VERB SHARES.
 *
 * One definition, three users — listMedia, addToPrompt and openPicker — because
 * they disagreed and the disagreement is invisible until a run hangs. Flow's
 * media has appeared in THREE URL families so far and each one broke something
 * different when only some of the callers knew about it:
 *
 *   /fx/api/trpc/media.getMediaUrlRedirect?name=<uuid>   the original
 *   flow.google.com/asb/<token>                          generated clips now
 *   flow-content.google/image|video/<uuid>               UPLOADS now
 *
 * The last one is why a plate that had visibly uploaded — sitting at the top of
 * Flow's own Uploads list — was reported as "never became Flow media".
 *
 * NOTE THE DOUBLE BACKSLASHES throughout: this is a template literal, and a
 * single one is resolved before the page sees it.
 * tools/check_bridge_page_code.py checks what actually arrives.
 */
function pageHelpers() {
  return `
    function pickerRoot() {
      return document.querySelector('[role="dialog"]') ||
             document.querySelector('.cdk-overlay-pane');
    }
    function mediaKey(v) {
      if (!v || v.indexOf("MEDIA_URL_TYPE_THUMBNAIL") >= 0) return null;
      var m = v.match(/getMediaUrlRedirect.*[?&]name=([0-9a-fA-F\\-]{8,})/);
      if (m) return {key: m[1], kind: null};
      m = v.match(/\\/asb\\/([A-Za-z0-9_\\-]{12,})/);
      if (m) return {key: m[1], kind: null};
      m = v.match(/flow-content\\.google\\/(image|video)\\/([0-9a-fA-F\\-]{20,})/);
      if (m) return {key: m[2], kind: m[1]};
      return null;
    }
  `;
}

/* IS THE PICKER OPEN? The old test asked for [role="dialog"].
 *
 * Flow's ingredients picker is a CDK overlay and has no such role — measured on
 * the live page: aria-expanded="true", one .cdk-overlay-pane, zero
 * [role=dialog]. So the test was false with the panel plainly on screen, and
 * openPicker clicked again, which TOGGLES IT SHUT. Four times. Then it reported
 * that it could not open a panel it had opened and closed twice.
 *
 * The opener's own aria-expanded is the authority; the overlay pane is the
 * fallback for a build that does not set it. */
function pickerOpenExpr(selector) {
  const sel = selector ? JSON.stringify(selector) : "null";
  return `
    var sel = ${sel};
    var t = sel ? document.querySelector(sel) : null;
    if (t && t.hasAttribute('aria-expanded')) return t.getAttribute('aria-expanded') === 'true';
    return !!(document.querySelector('[role="dialog"]') ||
              document.querySelector('.cdk-overlay-pane'));`;
}

async function openPicker(selector) {
  await attach();
  const isOpen = pickerOpenExpr(selector);
  const find = selector
    ? `var t = document.querySelector(${JSON.stringify(selector)});`
    : `var t = [...document.querySelectorAll('button,[role=button]')].find(
         e => e.offsetParent !== null &&
              (/add ingredients/i.test(e.getAttribute('aria-label') || "") ||
               /add_2/.test(e.innerText || "")));`;
  for (let i = 0; i < 4; i++) {
    const open = await evaluate(isOpen);
    if (open) return true;
    // A REAL mouse event, not el.click(). Flow's controls are Radix, and Radix
    // opens its triggers on pointerdown — a synthetic click reaches the React
    // onClick and does nothing, silently. Measured on both this picker and the
    // settings menu: `.click()` left aria-expanded="false" every time, and the
    // same coordinates through Input.dispatchMouseEvent opened it at once.
    const at = await evaluate(find + `
      if (!t) return null;
      t.scrollIntoView({block:'center'});
      var r = t.getBoundingClientRect();
      return {x: Math.round(r.left + r.width/2), y: Math.round(r.top + r.height/2)};`);
    if (!at) return false;
    const pt = { x: at.x, y: at.y, button: "left", clickCount: 1 };
    await cdp("Input.dispatchMouseEvent", Object.assign({ type: "mouseMoved", buttons: 0 }, pt));
    await cdp("Input.dispatchMouseEvent", Object.assign({ type: "mousePressed", buttons: 1 }, pt));
    await cdp("Input.dispatchMouseEvent", Object.assign({ type: "mouseReleased", buttons: 0 }, pt));
    await sleep(1200);
  }
  return await evaluate(isOpen);
}

async function addToPrompt(key, selector) {
  if (!key) throw new Error("add_to_prompt needs the media key to attach");
  if (!(await openPicker(selector))) {
    throw new Error("could not open Flow's asset picker — check `reference_open` " +
                    "in flow/selectors.json");
  }
  const before = await evaluate(`return document.querySelectorAll('img').length;`);
  const hit = await evaluate(pageHelpers() + `
    var dlg = pickerRoot();
    if (!dlg) return {err:'the picker closed before the asset could be picked'};
    var want = ${JSON.stringify(String(key))};
    var im = [...dlg.querySelectorAll('img')].find(
      i => (i.src||'').indexOf(want) >= 0);
    if (!im) return {err:'that asset is not in the picker', tiles: dlg.querySelectorAll('img').length};
    var box = im.closest('button,[role=button],li') || im.parentElement;
    box.scrollIntoView({block:'center'});
    var r = box.getBoundingClientRect();
    return {x: Math.round(r.left + r.width/2), y: Math.round(r.top + r.height/2)};
  `);
  if (hit && hit.err) throw new Error(hit.err + (hit.tiles ? " (" + hit.tiles + " tiles visible)" : ""));
  if (hit && hit.x != null) await realClick(hit.x, hit.y);
  await sleep(1200);

  // SELECTING IS NOT ATTACHING. The picker is a list of assets on the left and a
  // preview on the right: clicking a tile only moves the SELECTION, and the
  // asset is attached by the "Add to Prompt" button under the preview. Leaving
  // that out leaves the dialog open and the prompt bar empty, which looks
  // exactly like a click that missed. An older project layout attached on the
  // tile click alone, which is why omitting this appeared to work once.
  const confirm = await evaluate(pageHelpers() + `
    var d = pickerRoot();
    if (!d) return {gone:true};
    var a = [...d.querySelectorAll('button,[role=button]')]
      .find(e => /add to prompt/i.test(e.innerText || ''));
    if (!a) return {noButton:true};
    var r = a.getBoundingClientRect();
    return {x: Math.round(r.left + r.width/2), y: Math.round(r.top + r.height/2)};
  `);
  if (confirm && confirm.x != null) {
    await realClick(confirm.x, confirm.y);
    await sleep(1800);
  }

  // The proof is a chip on the prompt bar, not the click returning.
  const chips = await evaluate(pageHelpers() + chipsJs() + `
    return {chips: chips.length, dialogOpen: !!pickerRoot(),
            keys: chips.map(function (el) {
              var im = el.querySelector('img');
              var hit = mediaKey((im && im.src) || '');
              return hit ? hit.key : '';
            })};
  `);
  if (!chips.chips) {
    throw new Error("the asset was clicked but no reference chip appeared on the " +
                    "prompt bar — the generation would run with no reference, on a " +
                    "background of its own invention");
  }
  // The picker attaches whatever is SELECTED, which is not necessarily what was
  // clicked. Attaching the wrong picture looks exactly like attaching the right
  // one, so it is checked rather than assumed.
  //
  // ONE ASSET HAS TWO IDENTITIES, though, and the strict check did not know it.
  // Flow keys the same upload as /asb/<token> in the picker and as
  // /image/<uuid> on the prompt-bar chip, so comparing the two forms fails on
  // every correct attachment. What the check is actually for is a STALE chip —
  // one left by an earlier generation riding along into this one — and that is
  // caught by the count: we attach one asset, so one chip is right and two are
  // not, whichever way each is keyed.
  if (chips.keys.indexOf(String(key)) < 0 && chips.chips !== 1) {
    throw new Error("the prompt bar carries " + chips.chips + " chips (" +
                    JSON.stringify(chips.keys) + ") but this generation asked " +
                    "for one asset, " + key + " — something else is attached " +
                    "and the clip would be generated from both");
  }
  if (chips.dialogOpen) await closePicker(selector);
  return { attached: true, chips: chips.chips, key: key, dialogOpen: chips.dialogOpen };
}

/* Shut the asset picker. Not tidiness: listMedia reads the DOM, and with the
 * picker open every clip in the project renders as an <img> thumbnail inside
 * it. generate_one waits for a NEW <video>, so an open picker turns a
 * two-minute generation into a fifteen-minute timeout. */
async function closePicker(selector) {
  for (let i = 0; i < 3; i++) {
    if (!(await evaluate(pickerOpenExpr(selector)))) return true;
    const at = await evaluate((selector
      ? `var t = document.querySelector(${JSON.stringify(selector)});`
      : `var t = null;`) + `
      if (!t) { document.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true})); return null; }
      var r = t.getBoundingClientRect();
      return {x: Math.round(r.left + r.width/2), y: Math.round(r.top + r.height/2)};`);
    if (at) await realClick(at.x, at.y);
    await sleep(900);
  }
  return !(await evaluate(pickerOpenExpr(selector)));
}

/** Click by selector, or by the tightest visible element containing `text`. */
async function click(selector, opts) {
  const o = opts || {};
  const byText = o.text
    ? `
      var want = ${JSON.stringify(String(o.text).toLowerCase())};
      var best = null, bestLen = 1e9;
      for (const n of document.querySelectorAll('button,[role="button"],a,[role="menuitem"]')) {
        if (n.offsetParent === null) continue;
        var t = ((n.innerText || "") + " " + (n.getAttribute('aria-label') || "")).trim().toLowerCase();
        if (t && t.indexOf(want) >= 0 && t.length < bestLen) { best = n; bestLen = t.length; }
      }
      var el = best;`
    : `var el = document.querySelector(${JSON.stringify(selector)});`;

  const rect = await evaluate(byText + `
    if (!el) return null;
    if (el.disabled || el.getAttribute('aria-disabled') === 'true') return {disabled: true};
    el.scrollIntoView({block:'center'});
    var r = el.getBoundingClientRect();
    ${o.cdpClick ? "" : "el.click();"}
    return {x: r.left + r.width/2, y: r.top + r.height/2, clicked: ${o.cdpClick ? "false" : "true"}};
  `);
  const what = o.text ? "text=" + o.text : selector;
  if (!rect) throw new Error("click target not found (" + what + ")");
  if (rect.disabled) {
    throw new Error("click target is disabled (" + what + ") — the prompt probably did not land");
  }
  if (!rect.clicked) {
    const p = { x: Math.round(rect.x), y: Math.round(rect.y), button: "left", clickCount: 1 };
    await cdp("Input.dispatchMouseEvent", Object.assign({ type: "mouseMoved", buttons: 0 }, p));
    await cdp("Input.dispatchMouseEvent", Object.assign({ type: "mousePressed", buttons: 1 }, p));
    await cdp("Input.dispatchMouseEvent", Object.assign({ type: "mouseReleased", buttons: 0 }, p));
  }
  return rect;
}

/* Flow embeds every finished clip's URL in the DOM as
 * /fx/api/trpc/media.getMediaUrlRedirect?name=<uuid>. Reading those is the only
 * reliable route to the files: the ⋮ download menu renders on genuine CSS
 * :hover and portals its menu, neither of which survives automation.
 * Thumbnails carry MEDIA_URL_TYPE_THUMBNAIL and are filtered out. */
async function listMedia() {
  return await evaluate(pageHelpers() + `
    var attrs = ["src","poster","href","data-src"], seen = new Set(), out = [];
    for (const e of document.querySelectorAll("*")) {
      for (const a of attrs) {
        var hit = mediaKey(e.getAttribute && e.getAttribute(a));
        if (!hit || seen.has(hit.key)) continue;
        seen.add(hit.key);
        // WHAT MAKES A KEY A CLIP. Flow mints a key the moment a generation is
        // QUEUED and renders it as an <img> while the render runs -- 23 seconds
        // after submit in the first real run, far too fast to be a finished
        // clip. So the caller waits for a key rendered by a <video>, and the
        // tag is how that is told. An uploaded reference says so in its URL
        // instead, which is more reliable than the tag and is used when present.
        var tag = e.tagName.toLowerCase();
        var v = e.getAttribute(a);
        out.push({key: hit.key, tag: tag, attr: a,
                  video: hit.kind ? hit.kind === "video"
                                  : (tag === "video" || a === "poster"),
                  upload: hit.kind === "image",
                  url: v.indexOf("http") === 0 ? v : location.origin + v});
      }
    }
    return out;
  `);
}

/** Download one URL and resolve only once the file is actually on disk. */
function download(url, filename) {
  return new Promise((resolve, reject) => {
    // saveAs:false EXPLICITLY. Omitting it does not mean "no dialog" — it means
    // "follow the browser's default", and with Settings -> Downloads -> "Ask
    // where to save each file" on, that default is a Save-As dialog per clip.
    // An unattended run then parks on a modal nobody is there to click, which
    // is the one thing this whole background-tab design exists to avoid.
    chrome.downloads.download({ url, filename, conflictAction: "overwrite",
                                saveAs: false }, (id) => {
      const err = chrome.runtime.lastError;
      if (err || id == null) return reject(new Error(err ? err.message : "download refused"));
      const done = (delta) => {
        if (delta.id !== id) return;
        const st = delta.state && delta.state.current;
        if (st === "complete") {
          chrome.downloads.onChanged.removeListener(done);
          // Report where the file ACTUALLY went, not where we asked for it.
          // Chrome silently drops the subdirectory from `filename` sometimes —
          // measured: the same relative path landed in ~/Downloads/sub/ on one
          // call and straight in ~/Downloads/ on the next. Python then waits at
          // a path nothing will ever appear at and reports "the download never
          // landed" about a download that completed perfectly.
          chrome.downloads.search({ id: id }, (items) => {
            var real = (items && items[0] && items[0].filename) || null;
            resolve({ id: id, filename: filename, path: real });
          });
        } else if (st === "interrupted") {
          chrome.downloads.onChanged.removeListener(done);
          reject(new Error("download interrupted: " + ((delta.error && delta.error.current) || "?")));
        }
      };
      chrome.downloads.onChanged.addListener(done);
    });
  });
}

async function handle(job) {
  switch (job.cmd) {
    case "ping": {
      const tab = await findFlowTab();
      // `discarded` and `status` are the difference between "no tab" and "a tab
      // whose renderer is not running", which fail identically from Python and
      // want completely different fixes.
      // WHICH EXTENSION THIS IS, not just which build.
      //
      // Another project (flow-animator) ships a bridge that speaks this exact
      // protocol on this exact port, and its BRIDGE_BUILD was 8 — the same
      // number ours had. So it answered every ping, drove Flow correctly, and
      // for two builds this pipeline was running somebody else's extension
      // while its own had never been loaded at all. Every fix landed in a file
      // the browser had never seen. The build number alone could not say that;
      // the name can.
      const mf = chrome.runtime.getManifest();
      return { build: BRIDGE_BUILD, name: mf.name, version: mf.version,
               tab: tab ? tab.url : null, attached: attached, tabId: tabId,
               discarded: tab ? !!tab.discarded : null,
               status: tab ? tab.status : null,
               active: tab ? !!tab.active : null,
               frozen: tab ? !!tab.frozen : null };
    }
    case "attach": {
      await attach();
      // The URL is part of the answer, not a diagnostic: only the caller knows
      // whether the page it got is the page it needed.
      let url = null;
      try { url = (await chrome.tabs.get(tabId)).url; } catch (e) {}
      return { tabId: tabId, attached: attached, url: url };
    }
    case "eval":       return { value: await evaluate(job.expr) };
    case "set_prompt": return await setPrompt(job.text, job.selector);
    case "set_image":  return await setImage(job.paths, job.selector, job.open_selector);
    case "clear_images": return await clearImages(job.selector, job.clear_selector,
                                                  job.open_selector);
    case "add_to_prompt": return await addToPrompt(job.key, job.selector);
    case "clear_prompt_refs": return await clearPromptRefs(job.selector);
    case "click":      return await click(job.selector, { cdpClick: !!job.cdp, text: job.text || null });
    case "list_media": return { media: await listMedia() };
    case "download":   return await download(job.url, job.filename);
    case "detach":
      if (tabId != null && attached) {
        try { await chrome.debugger.detach({ tabId: tabId }); } catch (e) {}
      }
      attached = false;
      return { detached: true };
    default:
      throw new Error("unknown command: " + job.cmd);
  }
}

// ------------------------------------------------------------ the poll loop --
async function loop() {
  if (looping) return;
  looping = true;
  let quiet = 0;
  try {
  for (;;) {
    let job = null;
    try {
      const r = await fetch(BRIDGE + "/job", { cache: "no-store" });
      if (r.status === 204) { quiet = 0; continue; }   // long poll timed out, go again
      job = await r.json();
      quiet = 0;
    } catch (e) {
      // The bridge is not running. Back off, but never stop: `video veo` may
      // start it minutes from now and we want to be waiting when it does.
      quiet = Math.min(quiet + 1, 10);
      await sleep(1000 + quiet * 500);
      continue;
    }
    let payload;
    try {
      const cap = VERB_TIMEOUT[job.cmd] || DEFAULT_VERB_TIMEOUT;
      payload = { id: job.id, ok: true,
                  data: await withTimeout(handle(job), cap, job.cmd) };
    } catch (e) {
      payload = { id: job.id, ok: false, error: String((e && e.message) || e) };
    }
    try {
      await fetch(BRIDGE + "/event", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
    } catch (e) { /* bridge vanished mid-job; the next poll re-syncs */ }
  }
  } finally {
    // The loop is not supposed to end, so if it does, the flag must not stay
    // latched — it is what the recovery alarm checks, and a latched flag turns
    // "the worker stopped" into "the worker can never be restarted".
    looping = false;
  }
}

chrome.action.onClicked.addListener(async (tab) => {
  if (tab && tab.id) {
    try {
      await chrome.scripting.executeScript({ target: { tabId: tab.id }, files: ["content.js"] });
    } catch (e) {}
  }
  loop();
});

loop();
