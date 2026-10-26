"""Driving Google Flow from Python: the pieces submit.py and fetch.py share.

Everything here talks to Flow through the PYQ Flow Bridge extension
(flow/extension) and its Python half (src/flow_bridge.py), which is stdlib-only.
It deliberately does NOT import src/veo.py: that module is the PYQ track's whole
Veo route and pulls in the rest of the pipeline, while this kit has to run on a
machine that has only cloned the repo and followed SETUP.md.

The helpers were lifted from src/veo.py and the old tools/flow_fetch.py, where each was
paid for on a live run. The comments say what went wrong without them; keep them
when you edit, because every one of these failures looks like something else.
"""
from __future__ import annotations

import json
import re
import time
from pathlib import Path

import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

from src.flow_bridge import FlowBridge, FlowError, StaleExtension  # noqa: E402,F401

SELECTORS = ROOT / "flow" / "selectors.json"
SETTLE_AFTER_SUBMIT = 3.0

# The account segment ("/u/3/") can sit between the host and "project"; a
# pattern that allows only one segment there silently falls through and every
# "go back to the project" goes nowhere.
PROJECT_RE = re.compile(r"^(https://[^/]+/(?:[^/]+/)*?project/[0-9a-fA-F-]+)")


class KitError(RuntimeError):
    """Something a person has to look at. The message says what."""


class UserBusy(KitError):
    """The Flow tab is on a page a person is working in."""


def selectors() -> dict:
    return json.loads(SELECTORS.read_text(encoding="utf-8"))


def ev(b: FlowBridge, js: str, timeout: float = 60):
    return b.call("eval", expr=js, timeout=timeout)["value"]


def connect() -> tuple[FlowBridge, str]:
    """Start the bridge, wait for the extension, return (bridge, project url).

    StaleExtension is raised when the extension answering on the port is not
    this repo's, or is an older build: flow-animator ships a bridge on the same
    port with the same protocol, drives Flow perfectly, and has none of the
    fixes here. Its message says exactly what to reload."""
    b = FlowBridge().start()
    info = b.wait_for_worker(timeout=90)
    tab = info.get("tab") or ""
    if not tab:
        b.stop()
        raise KitError("no Google Flow tab is open — open the Flow project in Chrome")
    m = PROJECT_RE.match(tab)
    if not m:
        b.stop()
        raise KitError(f"the Flow tab is not inside a project ({tab}) — open the "
                       f"project itself, not Flow's home page")
    return b, m.group(1)


def tab_state(b: FlowBridge) -> dict:
    """{url, progress, credits}: where the tab is, whether Flow is rendering.

    RENDERING SHOWS AS A PERCENTAGE, and that is the only honest "not yet"
    signal: a queued generation gets a media key and a placeholder <img>
    within seconds, long before there is a clip."""
    return ev(b, r"""
        var pct = [], warn = null;
        document.querySelectorAll('*').forEach(function (e) {
          if (e.children.length) return;
          var t = (e.textContent || '').trim();
          if (/^[0-9]{1,3}%$/.test(t)) pct.push(t);
          if (!warn && t.length < 200 &&
              /running low on .*credits|out of .*credits|no .*credits/i.test(t)) {
            warn = t;
          }
        });
        return {url: location.href, progress: pct, credits: warn};
    """)


def out_of_credits(banner: str) -> bool:
    """True only when Flow REFUSED the work, not when it warns about the balance.

    One banner area carries both "You're out of Google Flow credits" (nothing
    queued) and "You're running low on Google Flow credits" (queued normally).
    The second stays up on a low account, so reading any banner as refusal
    makes the account unusable."""
    low = (banner or "").lower()
    if "running low" in low and "out of" not in low:
        return False
    return bool(re.search(r"out of .*credits|no .*credits left|run out of", low))


def back_to_grid(b: FlowBridge, project_url: str, timeout: float = 60.0) -> None:
    """Return the tab to the project grid and WAIT until the prompt box exists.

    THE TAB IS SHARED WITH A PERSON. A /character/ page means someone is
    building a Flow Character — choosing its voice, writing its info — and
    navigating away throws that work away. That is refused, not risked.

    THE CLIP EDITOR IS A TRAP. Submitting navigates Flow to the new clip's
    editor (/edit/<id>), whose prompt box EDITS THAT CLIP. A prompt typed there
    is not a new generation. Always come back to the grid before typing.

    It is a full page load, so the Angular app boots again; a fixed sleep was a
    guess and guessed wrong (six seconds reached a shell with no prompt box)."""
    url = tab_state(b).get("url") or ""
    if "/character/" in url:
        raise UserBusy(f"the Flow tab is on a character page — someone is editing "
                       f"it. Finish there (or ask), then run this again.")
    if url.rstrip("/") == project_url.rstrip("/") and ev(
            b, "return !!document.querySelector('.ProseMirror');"):
        return
    ev(b, f"location.href = {json.dumps(project_url)}; return 1;")
    end = time.time() + timeout
    while time.time() < end:
        time.sleep(2.0)
        try:
            if ev(b, "return !!document.querySelector('.ProseMirror');", timeout=30):
                time.sleep(1.5)
                return
        except FlowError:
            pass                        # mid-navigation
    raise KitError(f"the project page had no prompt box {timeout:.0f}s after loading")


SCROLL_TOP_JS = (
    "var sc = null, best = 0;"
    "document.querySelectorAll('*').forEach(function (e) {"
    "  if (e.scrollHeight > e.clientHeight + 400 && e.clientHeight > 200"
    "      && e.scrollHeight > best) { best = e.scrollHeight; sc = e; }"
    "});"
    "if (!sc) return false;"
    "sc.scrollTop = 0;"
    "return true;")

# A chip is the element the extension's chipsJs means: a button holding an
# image and a remove control reading "cancel", at chip size. Counting "small
# pictures near the prompt bar" returned 3 for one chip, because the picker's
# own thumbnails are small pictures near the prompt bar too.
CHIPS_JS = (
    "var chips = [].slice.call(document.querySelectorAll('button,[role=\"button\"]'))"
    "  .filter(function (el) {"
    "    if (!el.querySelector('img')) return false;"
    "    var t = (el.innerText || '').trim().toLowerCase();"
    "    if (t.indexOf('cancel') < 0) return false;"
    "    var r = el.getBoundingClientRect();"
    "    return r.width > 20 && r.width < 160 && r.height > 20 && r.height < 160;"
    "  });"
    "return chips.length;")


def chip_count(b: FlowBridge) -> int:
    return int(ev(b, CHIPS_JS) or 0)


def clear_chips(b: FlowBridge, sel: dict) -> int:
    """Remove every reference chip from the prompt bar; return how many are left.

    Attaching is ADDITIVE. A chip left by an earlier generation or a hand test
    rides into this one as an extra reference and Veo blends them, with nothing
    in any log to say so."""
    got = b.call("clear_prompt_refs", selector=sel.get("reference_chip_clear"),
                 timeout=120)
    return int(got.get("left") or 0)


def _open_uploads(b: FlowBridge, sel: dict) -> None:
    opener = sel.get("reference_open") or 'button[aria-label^="Add ingredients"]'
    if ev(b, f"var t = document.querySelector({json.dumps(opener)});"
             "return !(t && t.getAttribute('aria-expanded') === 'true');"):
        b.call("click", selector=opener, cdp=True, timeout=60)
        time.sleep(3.0)
    if ev(b, "var t = [].slice.call(document.querySelectorAll('[role=tab]'))"
             "  .filter(function (e) { return (e.innerText || '').indexOf('Uploads') >= 0; })[0];"
             "if (!t) return false;"
             "if (t.getAttribute('aria-selected') !== 'true') t.setAttribute('data-pyq-up', '1');"
             "return t.getAttribute('aria-selected') !== 'true';"):
        b.call("click", selector='[data-pyq-up="1"]', cdp=True, timeout=60)
        time.sleep(2.5)


def _listed(b: FlowBridge, name: str) -> bool:
    """Whether Flow's Uploads shows this file.

    THE FILENAME MOVED, 2026-09. It used to sit in the tile's own text, so an
    innerText search found it. On the current build a tile renders as
    <flow-grid-tile-container aria-label="<filename>"> wrapping a
    <flow-image-tile> whose only text is "Favourite" — nothing in the pane's
    innerText carries the name, and no element has role=option any more.
    Against that build the old check answered False for files that were sitting
    right there, so every run tried to upload them again.

    Both are tried: the aria-label first, the old text search after it, so this
    keeps working if Flow moves the name back.
    """
    want = json.dumps(name)
    return bool(ev(b, "var want = " + want + ";"
                      "var pane = document.querySelector('.cdk-overlay-pane') || document;"
                      "var byLabel = [].slice.call("
                      "  pane.querySelectorAll('[aria-label]')).some(function (e) {"
                      "  return (e.getAttribute('aria-label') || '').indexOf(want) >= 0; });"
                      "return byLabel || (pane.innerText || '').indexOf(want) >= 0;"))


def already_uploaded(b: FlowBridge, sel: dict, name: str) -> bool:
    """Whether Flow's Uploads already lists this file. UPLOAD ONCE: a re-upload
    leaves two tiles with the same name and the attach has to guess."""
    try:
        _open_uploads(b, sel)
        return _listed(b, name)
    except FlowError:
        return False


def upload(b: FlowBridge, sel: dict, path: Path) -> None:
    b.call("set_image", paths=[str(path)], selector=sel["plate_input"],
           open_selector=sel.get("reference_open"), timeout=180)
    time.sleep(3.0)


def attach_by_name(b: FlowBridge, sel: dict, name: str) -> int:
    """Attach the upload called `name` to the prompt; return the chip count.

    BY FILENAME, because media keys cannot identify it: one file shows as two
    keys (/asb/<token> in the picker, /image/<uuid> elsewhere), and the picker
    renders long-existing assets for the first time when opened, so a key diff
    once attached an ovule uploaded weeks earlier to a DNA prompt.

    SELECT, THEN CONFIRM. Clicking a tile only moves the picker's selection;
    "Add to prompt" attaches whatever is selected."""
    _open_uploads(b, sel)
    for _ in range(30):                    # an upload is listed before it is usable
        if _listed(b, name):
            break
        time.sleep(2.0)
    mark_js = (
        "var want = " + json.dumps(name) + ";"
        "var pane = document.querySelector('.cdk-overlay-pane') || document;"
        # 2026-09 build: the tile is <flow-grid-tile-container aria-label=NAME>
        # and carries the filename nowhere else — no role=option, and the only
        # text inside it is "Favourite". Tried first; the older strategies
        # below still run if this finds nothing.
        "var lab = [].slice.call(pane.querySelectorAll('[aria-label]'))"
        "  .filter(function (e) {"
        "    return (e.getAttribute('aria-label') || '').indexOf(want) >= 0; });"
        "var hit = lab.length ? lab[lab.length - 1] : null;"
        # the SELECTABLE tile (role=option), and the LAST match: a retry that
        # re-uploaded leaves an older twin that may be scrolled out of reach
        "if (!hit) {"
        "  var all = [].slice.call(pane.querySelectorAll('[role=option]'))"
        "    .filter(function (e) { return (e.innerText || '').indexOf(want) >= 0; });"
        "  hit = all.length ? all[all.length - 1] : null;"
        "}"
        # older layouts had no role=option: climb from the filename's text to
        # the row that holds the thumbnail
        "if (!hit) {"
        "  pane.querySelectorAll('*').forEach(function (e) {"
        "    if (hit || e.children.length) return;"
        "    if ((e.textContent || '').indexOf(want) < 0) return;"
        "    var row = e;"
        "    for (var i = 0; i < 6 && row.parentElement; i++) {"
        "      row = row.parentElement;"
        "      if (row.getAttribute('role') === 'option') break;"
        "      if (row.querySelector('img')) break;"
        "    }"
        "    hit = row;"
        "  });"
        "}"
        "if (!hit) return null;"
        "hit.setAttribute('data-pyq-asset', '1');"
        "hit.scrollIntoView({block: 'center'});"
        "return true;")
    if not ev(b, mark_js):
        raise KitError(f"{name} is not listed in Flow's Uploads — the upload did not "
                       f"land, so there is nothing to attach")
    selected = False
    for _ in range(8):
        # RE-MARK EVERY TIME: the list is virtualised and the tile may have been
        # replaced, and a click on a vanished element reads as "file missing"
        if not ev(b, mark_js):
            time.sleep(2.0)
            continue
        b.call("click", selector='[data-pyq-asset="1"]', cdp=True, timeout=60)
        time.sleep(3.0)
        # the click took when the marked tile re-rendered away
        selected = not ev(b, "return !!document.querySelector('[data-pyq-asset=\"1\"]');")
        if selected:
            break
    if not selected:
        raise KitError(f"{name} is listed but clicking its tile did nothing, so "
                       f"'Add to prompt' would attach whatever was selected before")
    if ev(b, "var d = document.querySelector('.cdk-overlay-pane');"
             "if (!d) return false;"
             "var a = [].slice.call(d.querySelectorAll('button,[role=button]'))"
             "  .filter(function (e) { return /add to prompt/i.test(e.innerText || ''); })[0];"
             "if (!a) return false;"
             "a.setAttribute('data-pyq-add', '1'); return true;"):
        b.call("click", selector='[data-pyq-add="1"]', cdp=True, timeout=60)
        time.sleep(2.5)
    return chip_count(b)


def set_prompt(b: FlowBridge, sel: dict, text: str) -> int:
    """Type the prompt and READ IT BACK; return the length that landed.

    The read-back is the real guard. Flow's submit button reports itself enabled
    with an EMPTY box, so a prompt that failed to land would submit nothing and
    the run would wait for a clip that was never queued.

    Two insertion paths, in the order they are trusted. The extension's verb
    (select-all, then a trusted Input.insertText) is what every submission on
    22 Sept 2026 used, against the ProseMirror box. FlowBridge.set_prompt
    dispatches a paste instead, which is the path src/veo.py moved to when an
    earlier Flow build dropped typed input; it is the fallback here. Both select
    the existing contents first, so a leftover prompt is replaced, never
    appended to."""
    probe = (f"var e = document.querySelector({json.dumps(sel['prompt'])});"
             "return e ? (e.innerText || '').length : -1;")
    want = len(" ".join(text.split()))
    try:
        b.call("set_prompt", text=text, selector=sel["prompt"], timeout=120)
    except FlowError:
        pass
    time.sleep(1.5)
    n = int(ev(b, probe) or 0)
    if n >= 0.9 * want:
        return n
    try:
        return b.set_prompt(text, selector=sel["prompt"], timeout=60)
    except FlowError:
        return int(ev(b, probe) or 0)


def wait_for_submit(b: FlowBridge, sel: dict, budget: float = 900.0) -> bool:
    """Wait until Flow will accept another generation; True if it will.

    THE MISSING BUTTON IS A QUEUE, NOT A GLITCH. Flow runs at most two
    generations at once, and while both slots are full it does not disable the
    submit arrow — it REMOVES it from the prompt bar. So a third submission
    dies on 'click target not found' with the prompt sitting typed and ready,
    which reads like a selector that went stale and is nothing of the kind.
    Waiting is the whole fix: a slot opens when a clip finishes, typically
    within a couple of minutes, and the button comes back on its own."""
    js = (f"return document.querySelector({json.dumps(sel['generate_selector'])}) "
          f"? 1 : 0;")
    end = time.time() + budget
    said = False
    while time.time() < end:
        if int(ev(b, js) or 0):
            return True
        if not said:
            pct = (tab_state(b).get("progress") or [""])[0]
            print(f"    waiting for a free slot — Flow is at capacity"
                  + (f" ({pct} on the clip in front)" if pct else ""))
            said = True
        time.sleep(15.0)
    return False


def start_generation(b: FlowBridge, sel: dict) -> str:
    """Press the submit arrow and confirm Flow took it; return what was seen.

    THE BUTTON CAN BE MISSING FOR A MOMENT. Queueing a third clip while two
    were rendering, the submit arrow was absent when the click fired and present
    a few seconds later: Flow re-renders the prompt bar as the previous
    submission's chat message lands. One retry after a pause, then a real error.
    Under that, wait_for_submit sits out Flow's two-at-a-time limit."""
    if not wait_for_submit(b, sel):
        raise KitError("Flow's submit arrow never came back — it has been at "
                       "capacity for fifteen minutes. Look at the tab.")
    try:
        b.call("click", selector=sel["generate_selector"], cdp=True, timeout=60)
    except FlowError:
        time.sleep(5.0)
        if not wait_for_submit(b, sel, budget=120.0):
            raise
        b.call("click", selector=sel["generate_selector"], cdp=True, timeout=60)
    time.sleep(SETTLE_AFTER_SUBMIT)
    for _ in range(10):
        st = tab_state(b)
        if out_of_credits(st.get("credits") or ""):
            raise KitError(f"Flow refused the generation: {st['credits']}")
        if st.get("progress"):
            return f"rendering {st['progress'][0]}"
        if "/edit/" in (st.get("url") or ""):
            return "opened the new clip"
        time.sleep(6.0)
    return "queued (no progress indicator yet — check the tab)"
