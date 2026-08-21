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
const FLOW_URL_RE = /^https:\/\/(labs\.google\/fx\/.*tools\/flow|flow\.google)/i;

let looping = false;      // false again whenever the worker is restarted
let tabId = null;
let attached = false;

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

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

chrome.debugger.onDetach.addListener((src) => {
  if (src.tabId === tabId) attached = false;
});
chrome.tabs.onRemoved.addListener((id) => {
  if (id === tabId) { tabId = null; attached = false; }
});

async function findFlowTab() {
  const tabs = await chrome.tabs.query({});
  // Prefer a tab already inside a project — that is the one with a prompt box.
  const inProject = tabs.find((t) => t.url && FLOW_URL_RE.test(t.url) && /\/project\//.test(t.url));
  return inProject || tabs.find((t) => t.url && FLOW_URL_RE.test(t.url)) || null;
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
  await new Promise((res, rej) => chrome.debugger.attach({ tabId }, "1.3", () => {
    const e = chrome.runtime.lastError;
    if (e && !/already attached/i.test(e.message)) rej(new Error(e.message));
    else res();
  }));
  attached = true;
  await cdp("Runtime.enable");
  await cdp("DOM.enable");
  await cdp("Page.enable");
  // THE line that makes a background tab work at all. See the header.
  try { await cdp("Emulation.setFocusEmulationEnabled", { enabled: true }); } catch (e) {}
  await chrome.storage.session.set({ tabId, flowUrl: tab.url });
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

/** Attach the background plate as Flow's reference image, by local file path. */
async function setImage(paths, selector) {
  await attach();
  const sel = selector || 'input[type="file"]';
  const doc = await cdp("DOM.getDocument", { depth: -1, pierce: true });
  const q = await cdp("DOM.querySelectorAll", { nodeId: doc.root.nodeId, selector: sel });
  const nodes = (q && q.nodeIds) || [];
  if (!nodes.length) {
    throw new Error("no file input matched " + sel +
                    " — open Flow's reference-image panel once so the input exists in the DOM");
  }
  // Prefer one that declares it accepts images.
  let target = nodes[0];
  for (const id of nodes) {
    const d = await cdp("DOM.describeNode", { nodeId: id });
    const attrs = (d.node && d.node.attributes) || [];
    const i = attrs.indexOf("accept");
    if (i >= 0 && /image/i.test(attrs[i + 1] || "")) { target = id; break; }
  }
  await cdp("DOM.setFileInputFiles", { nodeId: target, files: paths });
  return { input: target, files: paths.length };
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
  return await evaluate(`
    var attrs = ["src","poster","href","data-src"], seen = new Set(), out = [];
    for (const e of document.querySelectorAll("*")) {
      for (const a of attrs) {
        var v = e.getAttribute && e.getAttribute(a);
        if (v && v.indexOf("getMediaUrlRedirect") >= 0 && v.indexOf("MEDIA_URL_TYPE_THUMBNAIL") < 0) {
          var m = v.match(/name=([0-9a-fA-F-]{8,})/);
          var key = m ? m[1] : v;
          if (!seen.has(key)) {
            seen.add(key);
            out.push({key: key, url: v.indexOf("http") === 0 ? v : location.origin + v});
          }
        }
      }
    }
    return out;
  `);
}

/** Download one URL and resolve only once the file is actually on disk. */
function download(url, filename) {
  return new Promise((resolve, reject) => {
    chrome.downloads.download({ url, filename, conflictAction: "overwrite" }, (id) => {
      const err = chrome.runtime.lastError;
      if (err || id == null) return reject(new Error(err ? err.message : "download refused"));
      const done = (delta) => {
        if (delta.id !== id) return;
        const st = delta.state && delta.state.current;
        if (st === "complete") {
          chrome.downloads.onChanged.removeListener(done);
          resolve({ id: id, filename: filename });
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
      return { tab: tab ? tab.url : null, attached: attached, tabId: tabId };
    }
    case "attach":     await attach(); return { tabId: tabId, attached: attached };
    case "eval":       return { value: await evaluate(job.expr) };
    case "set_prompt": return await setPrompt(job.text, job.selector);
    case "set_image":  return await setImage(job.paths, job.selector);
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
      payload = { id: job.id, ok: true, data: await handle(job) };
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
