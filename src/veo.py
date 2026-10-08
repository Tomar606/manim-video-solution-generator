"""The Veo stage: beats marked `type: video` become checked, downloaded clips.

    video veo projects/che-c3-la-02 --part 1

WHAT IT DOES, IN ORDER, PER BEAT
--------------------------------
    write the prompt   -> src/veo_prompts.py, against the house skill
    audit it           -> mechanical checks, no model, before a credit is spent
    attach the plate   -> assets/backgrounds/<subject>.png, into Flow itself
    submit             -> the extension types it into Flow's editor
    wait               -> until a media URL Flow did not have before appears
    download           -> through the browser session, into the project
    review             -> src/veo_qc.py grades the frames
    revise and repeat  -> up to MAX_ATTEMPTS, then give up loudly

Nothing here needs the Flow tab to be visible or focused. See
`src/flow_bridge.py` and `flow/extension/background.js`.

WHY EACH CLIP IS SUBMITTED AND COLLECTED ONE AT A TIME
------------------------------------------------------
Flow will happily queue several generations at once, and the upstream bridge did
exactly that — then matched clips to scenes by reversing DOM order and hoping.
That is fine for an ad where every clip is of the same person in the same room;
it is not fine here, where clip 2 going into beat 3's slot means the student
watches the wrong process while the teacher describes this one. Submitting one
and waiting for exactly one new media key to appear makes the mapping a fact
rather than an inference. It costs wall-clock and nothing else, and the run is
unattended anyway.

WHY THE PLATE IS ATTACHED RATHER THAN DESCRIBED
-----------------------------------------------
The clip is spliced into the middle of a Manim render of the SAME background.
Any difference in that background — a shade, a grid offset, a brightness ramp —
reads as a jump cut at both ends of the window. Describing the background in
words guarantees that difference; uploading the exact PNG Manim renders removes
it. Skill §15, and check B in the visual review, both exist for this.
"""
from __future__ import annotations

import json
import re
import shutil
import tempfile
import time
from pathlib import Path

from src import (veo_sequence, veo_conform, veo_delogo, veo_holds,
                 veo_labels, veo_prompts, veo_qc)
from src.flow_bridge import (DOWNLOAD_DIR, FlowBridge, FlowError, inbox_dir,
                             inbox_rel, settled)

ROOT = Path(__file__).resolve().parent.parent
SELECTORS = ROOT / "flow" / "selectors.json"

MAX_ATTEMPTS = 3          # first try plus two revisions
GEN_SECONDS = 8           # what Flow actually produces; the window is fitted to
                          # it afterwards by src/veo_conform.py, so this is a
                          # hint about pacing rather than about length
MAX_ON_SCREEN = 25.0      # one generated clip held longer than this stops being
                          # a demonstration and becomes wallpaper
GENERATE_TIMEOUT = 1800.0  # Flow QUEUES generations now and says so — "in the
                           # queue due to high demand" — and 15 minutes was not
                           # enough to outlast it
FIRST_LOOK = 45.0         # seconds after submit before the first check
POLL_EVERY = 10.0
SETTLE_AFTER_SUBMIT = 3.0
UPLOAD_TIMEOUT = 120.0    # an upload has to become Flow media before it can be
                          # picked from the tray and added to the prompt


class VeoError(RuntimeError):
    pass


def _selectors() -> dict:
    return json.loads(SELECTORS.read_text(encoding="utf-8"))


def _rel(p: Path) -> str:
    """A path to print. Short when the project lives under the repo, absolute
    when `--projects-dir` puts it somewhere else — `relative_to` raises rather
    than falling back, and a crash while printing a summary loses the whole run's
    results after every clip has already been paid for."""
    try:
        return str(p.relative_to(ROOT))
    except ValueError:
        return str(p)


def panel_band(beat: dict) -> tuple[float, float] | None:
    """The rows a panel beat's labels may use, or None for the full-bleed layout.

    A label on a panel clip is bounded by the PANEL, not by the frame: below the
    torn-paper divider it is on the plate the presenter stands on, and above the
    panel's top dissolve it is on a strip that is barely there. Those bounds
    come from the same geometry the compositor uses, so the two cannot drift.
    """
    if veo_prompts.layout_of(beat) != "panel":
        return None
    from src import panel_layout as PL
    kw = {}
    if beat.get("panel_ar"):
        kw["panel_ar"] = float(beat["panel_ar"])
    if beat.get("panel_top") is not None:
        kw["top_margin"] = int(beat["panel_top"])
    # The clip's own size does not affect `top`/`seam`, so any 16:9 pair does.
    g = PL.geometry(1920, 1080, **kw)
    return float(g["top"] + g["fade"]), float(g["seam"])


def label_faults(labels: list[dict], *, frame: str = "presenter",
                 band: tuple[float, float] | None = None) -> list[str]:
    """Labels that would land somewhere the frame is not theirs to use.

    Warnings rather than errors: the clip is already generated and paid for, and
    a label two pixels into the caption strip is a nudge in the beats file, not a
    reason to throw the run away. `tools/preflight.py` reports the same thing
    before the render, which is where it can still be acted on cheaply.
    """
    from src.veo_prompts import LAYOUT, floor_for

    top = LAYOUT["caption_cut"] * veo_labels.FRAME_H
    if band:
        top, floor = band
        out = []
        for a in labels:
            if a["y"] < top:
                out.append(f"label {a['text']!r} sits in the panel's top "
                           f"dissolve (y={a['y']}, the picture is only solid "
                           f"below {int(top)})")
            if a["y"] + a["h"] > floor:
                out.append(f"label {a['text']!r} falls past the torn-paper "
                           f"divider (y={a['y'] + a['h']}, the panel ends at "
                           f"{int(floor)}) — below it the label is on the plate, "
                           f"not on the clip")
            if a["x"] < 0 or a["x"] + a["w"] > veo_labels.FRAME_W:
                out.append(f"label {a['text']!r} runs off the side of the frame")
        return out + _overlaps(labels)
    # The floor depends on whether the presenter is there. With him on screen a
    # label below the halfway line is not "low", it is BEHIND HIM — invisible,
    # and invisible in a way no frame check downstream would catch, because the
    # label really was composited, just underneath. Only a beat that fades him
    # out gets the rest of the frame.
    floor = floor_for(frame) * veo_labels.FRAME_H
    out = []
    for a in labels:
        if a["y"] < top:
            out.append(f"label {a['text']!r} sits in the caption strip "
                       f"(y={a['y']}, the strip ends at {int(top)})")
        if a["y"] + a["h"] > floor:
            out.append(
                f"label {a['text']!r} reaches past the usable floor "
                f"(y={a['y'] + a['h']}, floor {int(floor)})"
                + ("" if frame == "full" else
                   " — the presenter is on screen for this beat, so it would be "
                   "hidden behind him. Raise it, or give the beat more room with "
                   "`presenter: partial` (bottom third stays clear) or "
                   "`presenter: hidden`."))
        if a["x"] < 0 or a["x"] + a["w"] > veo_labels.FRAME_W:
            out.append(f"label {a['text']!r} runs off the side of the frame")
    return out + _overlaps(labels)


def _overlaps(labels: list[dict]) -> list[str]:
    out = []
    for i, a in enumerate(labels):
        for b in labels[i + 1:]:
            if (a["start"] < b["end"] and b["start"] < a["end"]
                    and abs(a["x"] - b["x"]) < (a["w"] + b["w"]) / 2
                    and abs(a["y"] - b["y"]) < (a["h"] + b["h"]) / 2):
                out.append(f"labels {a['text']!r} and {b['text']!r} overlap "
                           f"while both are on screen")
    return out


def _first_of(results: list[dict], sequence: str) -> dict | None:
    """The first clip of a sequence — the one legitimately generated without a
    carried frame, so it is not counted as a break in the sequence."""
    for r in results:
        if r.get("sequence") == sequence:
            return r
    return None


def resolve(project: str) -> Path:
    p = Path(project)
    if not p.is_dir():
        p = ROOT / "projects" / project
    if not p.is_dir():
        raise VeoError(f"no project at {project}")
    return p


# --------------------------------------------------------------------------- #
# Reading the part
# --------------------------------------------------------------------------- #
def video_beats(root: Path, part: int) -> tuple[list[dict], list[dict], dict]:
    """The `type: video` beats of one part, with its caption track and meta."""
    beats_f = root / f"beats_part{part}.json"
    lines_f = root / f"lines_part{part}.json"
    for f in (beats_f, lines_f, root / "meta.json"):
        if not f.is_file():
            raise VeoError(f"{f} is missing — run the beats stage for part {part} first")
    beats = json.loads(beats_f.read_text(encoding="utf-8"))
    lines = json.loads(lines_f.read_text(encoding="utf-8"))
    meta = json.loads((root / "meta.json").read_text(encoding="utf-8"))
    vids = [b for b in beats if b.get("type") == "video"]
    for b in vids:
        if not b.get("brief"):
            raise VeoError(
                f"the video beat at caption {b.get('at')} has no `brief`. A Veo beat "
                f"is a judgement about the question, not about a sentence, so the "
                f"brief is hand-written: say what has to be SEEN moving and why "
                f"Manim cannot show it.")
    return vids, lines, meta


def window(beat: dict, beats: list[dict], lines: list[dict],
           clip_end: float) -> tuple[float, float]:
    """The absolute [start, end] this beat OWNS — what the clip must be fitted to.

    Note what does not appear here: how long the generated clip is. The window is
    set by the presenter, because he is the clock — it opens on the caption the
    beat is anchored to and closes when the next beat takes the screen. A ten
    second clip under fifteen seconds of narration does not get to end early and
    leave the student looking at a plate; it gets conformed to the fifteen. That
    is `src/veo_conform.py`'s job, and this function is what tells it the number.

    `seconds` on the beat overrides the slot, for a demonstration that should
    finish before the teacher does. MAX_ON_SCREEN is the guard for the opposite
    case: a beat with nothing after it inherits the whole rest of the part, and
    stretching eight generated seconds across a minute is not a demonstration.
    """
    at = int(beat["at"])
    start = float(lines[max(0, min(at, len(lines) - 1))]["start"])
    later = [int(b["at"]) for b in beats if int(b["at"]) > at]
    ceiling = float(lines[min(later)]["start"]) if later else clip_end
    slot = max(0.0, min(ceiling, clip_end) - start)
    want = float(beat["seconds"]) if beat.get("seconds") else min(slot, MAX_ON_SCREEN)
    return start, start + max(0.0, min(want, slot))


# --------------------------------------------------------------------------- #
# Driving one generation
# --------------------------------------------------------------------------- #
def _media_keys(bridge: FlowBridge) -> set[str]:
    return {m["key"] for m in bridge.call("list_media", timeout=60).get("media", [])}


PROJECT_RE = re.compile(r"^(https://[^/]+/(?:[^/]+/)*?project/[0-9a-fA-F-]+)")


def _tab_state(bridge: FlowBridge) -> dict:
    """Where the tab is, and whether Flow is still rendering something.

    Both halves were found the expensive way on a live run.

    THE TAB DRIFTS. Submitting a generation navigates Flow to the new clip's own
    editor at /project/<id>/edit/<clip>. That page is not the grid: list_media
    read 42 items on the grid and 1 there, so the diff that identifies the new
    clip can never fire, and the run waits out its whole fifteen minutes on the
    wrong page. background.js already refuses to CHOOSE an /edit/ tab; nothing
    stopped it from being carried there afterwards.

    RENDERING IS SHOWN AS A PERCENTAGE, and that is the only honest "not yet"
    signal left — see _new_media for why the old one stopped working.
    """
    return bridge.call("eval", expr=r"""
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
    """, timeout=60)["value"]


def _back_to_grid(bridge: FlowBridge, project_url: str, *,
                  timeout: float = 60.0) -> None:
    """Go back to the project and WAIT FOR IT TO BE USABLE.

    This is a full page load, not a route change, so the Angular app has to boot
    again. A fixed sleep is a guess about how long that takes, and the guess was
    wrong: six seconds got as far as a rendered shell with no prompt box in it,
    and the run then reported the box as missing — which reads like Flow moved
    the editor rather than like the page was still starting.
    """
    bridge.call("eval",
                expr=f"location.href = {json.dumps(project_url)}; return 1;",
                timeout=60)
    deadline = time.time() + timeout
    while time.time() < deadline:
        time.sleep(2.0)
        try:
            if bridge.call("eval", expr=(
                    "return !!document.querySelector('.ProseMirror');"),
                    timeout=30)["value"]:
                return
        except FlowError:
            pass                      # the renderer is mid-navigation
    print(f"  ⚠ the project page had no prompt box {timeout:.0f}s after loading")


DOWNLOAD_QUALITY = "original"  # Flow offers 270p GIF / 720p original / 1080p / 4K

# Every visible entry in whatever menu is open. Kept as a module constant rather
# than inline so tools/check_bridge_page_code.py sees it: page code written in
# Python goes through a Python quote AND a JS parser, and has been mangled by
# both. Note split/join rather than a newline regex, for exactly that reason.
MENU_ENTRIES_JS = (
    "var out = [];"
    "document.querySelectorAll("
    "'[role=menuitem],[role=menuitemradio],[role=option],.cdk-overlay-pane button')"
    ".forEach(function (e) {"
    "  var t = (e.innerText || '').trim();"
    "  if (t && e.offsetParent !== null) out.push(t.split(String.fromCharCode(10)).join(' '));"
    "});"
    "return out;")


SCROLL_TOP_JS = (
    "var sc = null, best = 0;"
    "document.querySelectorAll('*').forEach(function (e) {"
    "  if (e.scrollHeight > e.clientHeight + 400 && e.clientHeight > 200"
    "      && e.scrollHeight > best) { best = e.scrollHeight; sc = e; }"
    "});"
    "if (!sc) return false;"
    "sc.scrollTop = 0;"
    "return true;")

# SHOW VIDEOS ONLY. The project grid defaults to "All media", and the newest
# item there is not the clip — it is the REFERENCE IMAGE this run just uploaded.
# So "open the newest tile" opened our own p2_at012.png, the prompt probes could
# not match a picture, and the run retried: back to the grid, scroll, click,
# fail, wait twenty seconds, again. From the outside that looks exactly like an
# old clip's editor reopening over and over, which is what was reported.
SELECT_VIDEOS_JS = (
    "var hit = null, area = 1e9;"
    "document.querySelectorAll('*').forEach(function (e) {"
    "  var t = (e.innerText || '').trim();"
    "  if (t !== 'Videos' && t !== 'videocam Videos') return;"
    "  var r = e.getBoundingClientRect();"
    "  if (r.width < 20 || r.height < 12) return;"
    "  var a = r.width * r.height;"
    "  if (a < area) { area = a; hit = e; }"
    "});"
    "if (!hit) return false;"
    "hit.setAttribute('data-pyq-videos', '1');"
    "return true;")

# The newest clip's tile, marked so a real mouse click can be aimed at it.
#
# BY THE THUMBNAIL, not by the play glyph. The old rule — smallest element whose
# text contains 'play_circle', with its top between -100 and 260 — matches
# nothing in the grid Flow ships now: real tiles sit at y=385 under "All media"
# and every element that passed the glyph test was a full-height page container,
# the smallest being a 360x752 side panel. It marked the panel, the click landed
# nowhere useful, and no clip ever opened.
#
# A tile is an <img> whose source is on the /asb/ media host, tile-sized and on
# screen; the clickable box is its `.container` ancestor. Newest is topmost then
# leftmost, with the row quantised so a few pixels of stagger cannot reorder it.
MARK_NEWEST_JS = (
    "var best = null, bk = null;"
    "document.querySelectorAll('img').forEach(function (im) {"
    "  var src = im.currentSrc || im.src || '';"
    "  if (src.indexOf('/asb/') < 0) return;"
    "  var r = im.getBoundingClientRect();"
    "  if (r.width < 120 || r.height < 70) return;"
    "  if (r.bottom < 0 || r.top > innerHeight) return;"
    "  var k = [Math.round(r.top / 40), Math.round(r.left)];"
    "  if (!bk || k[0] < bk[0] || (k[0] === bk[0] && k[1] < bk[1])) { bk = k; best = im; }"
    "});"
    "if (!best) return null;"
    "var tile = best.closest('.container') || best;"
    "tile.setAttribute('data-pyq-tile', '1');"
    "var r = tile.getBoundingClientRect();"
    "return {w: Math.round(r.width), h: Math.round(r.height),"
    "        y: Math.round(r.top), x: Math.round(r.left)};")


def open_newest_clip(bridge: FlowBridge, project_url: str, *, expect: str,
                     tries: int = 4) -> str:
    """Open the newest clip in the project and prove it is the one we asked for.

    HOW THE CLIP IS FOUND, after several approaches that could not work.
    The media grid is a VIRTUALISED, lazily-loaded list: item counts drift
    between polls of an unchanging project, thumbnails are absent until drawn,
    and every tile reports a viewport position thousands of pixels off-screen
    while the list is scrolled elsewhere. So no key diff and no "first by
    position" is trustworthy. What is trustworthy is scrolling the list back to
    the top, where the newest item is, and clicking the tile that is then on
    screen.

    AND THEN CHECKING. Ordering is an assumption; the clip editor shows the
    prompt that produced it, so the assumption is verified rather than trusted.
    A run that opened the wrong clip would otherwise splice one beat's animation
    under another beat's narration, which is the failure this whole route exists
    to avoid.
    """
    # THREE PROBES, NOT ONE, AND NOT FROM THE START.
    # Every prompt in this track opens with the same house sentence — "Silent
    # photoreal three-dimensional scientific visualisation..." — so a probe
    # taken from the beginning matches EVERY beat and would happily accept the
    # previous beat's clip. Slices from further in are beat-specific. Two of
    # three, so a page that truncates the tail still verifies.
    flat = " ".join(expect.split()).lower()
    probes = [flat[int(len(flat) * f):int(len(flat) * f) + 40]
              for f in (0.20, 0.35, 0.50)]
    probes = [x for x in probes if len(x) == 40]
    for attempt in range(tries):
        if "/edit/" in _tab_state(bridge)["url"]:
            _back_to_grid(bridge, project_url)
        # Videos first, so an uploaded reference cannot be "the newest media".
        if bridge.call("eval", expr=SELECT_VIDEOS_JS, timeout=60)["value"]:
            bridge.call("click", selector='[data-pyq-videos="1"]', cdp=True,
                        timeout=60)
            time.sleep(3.0)
        if not bridge.call("eval", expr=SCROLL_TOP_JS, timeout=60)["value"]:
            raise VeoError("the project's media list has no scroll container")
        time.sleep(2.5)
        if not bridge.call("eval", expr=MARK_NEWEST_JS, timeout=60)["value"]:
            time.sleep(3.0)
            continue
        bridge.call("click", selector='[data-pyq-tile="1"]', cdp=True, timeout=60)
        time.sleep(6.0)

        url = _tab_state(bridge)["url"]
        if "/edit/" not in url:
            print(f"  the newest tile did not open (try {attempt + 1}/{tries})")
            continue
        shown = bridge.call("eval", expr=(
            "return (document.body.innerText || '')"
            ".split(String.fromCharCode(10)).join(' ').toLowerCase();"),
            timeout=60)["value"] or ""
        page = " ".join(shown.split())
        hits = sum(1 for x in probes if x in page)
        if probes and hits < 2:
            print(f"  the newest clip is not this beat's — {hits}/{len(probes)} "
                  f"of its prompt is on the page (try {attempt + 1}/{tries})")
            time.sleep(20.0)          # it may still be in the queue
            continue
        print(f"  opened {url.rsplit('/', 1)[-1][:12]}… and its prompt matches")
        return url
    raise VeoError(
        "could not open a clip whose page carries this beat's prompt. Either "
        "the generation has not finished, or Flow put it somewhere other than "
        "the top of the project's media list.")


def download_via_ui(bridge: FlowBridge, dest: Path, *, label: str,
                    timeout: float = 420.0) -> Path:
    """Save the clip the editor is showing, using Flow's OWN download control.

    WHY NOT THE MEDIA URL, which is what this used to do.
    The clip is no longer reachable from the DOM. The project grid is
    virtualised and lazily loaded, so a before/after key diff is not a fact
    about generations — item counts drifted 46, 42, 35, 32 between polls of an
    unchanging project. Finished clips render as <img>, so the old "wait for a
    <video>" test can never pass. And neither URL family in the page is the
    video: /image/ keys download as a 30 KB poster still and /asb/ keys do not
    download at all.

    Flow's own Download button has none of those problems. It is attached to the
    clip being edited, so there is no identification step to get wrong, and it
    hands the file to Chrome, which puts it where every other download goes.
    """
    dl_dir = Path(DOWNLOAD_DIR)
    before = {p.name for p in dl_dir.glob("*.mp4")}

    bridge.set_status(stage="downloading the clip", detail=label)
    marked = bridge.call("eval", expr=r"""
        var t = [].slice.call(document.querySelectorAll('button,[role=button],a'))
          .filter(function (e) {
            return /download/i.test(e.getAttribute('aria-label') || ''); })[0];
        if (!t) return 'missing';
        if (t.disabled || t.getAttribute('aria-disabled') === 'true') return 'disabled';
        t.setAttribute('data-pyq-dl', '1');
        return 'ok';
    """, timeout=60)["value"]
    if marked != "ok":
        raise VeoError(f"Flow's download control is {marked} on this page")
    # THE MENU IS OPENED, NOT ASSUMED. A click that lands while the page is
    # still settling after a generation opens nothing, and the failure then
    # reads as "Flow has no 1080p option" — a statement about a menu that was
    # never there. Retried, and the entries are reported either way.
    entries = []
    for tries in range(4):
        bridge.call("click", selector='[data-pyq-dl="1"]', cdp=True, timeout=60)
        time.sleep(2.5)
        entries = bridge.call("eval", expr=MENU_ENTRIES_JS, timeout=60)["value"] or []
        if entries:
            break
        print(f"  the download menu did not open (try {tries + 1}/4)")

    # THE ORIGINAL SIZE, not an upscale. 720p is what Veo actually rendered;
    # 1080p and 4K are Flow upscaling it afterwards, and the panel is 1080x608
    # so every one of those extra pixels is thrown away on the way in. Taking
    # the original avoids an upscale-then-downscale round trip for nothing.
    low = [e.lower() for e in entries]
    want = None
    for pick in ("original", "720p", "1080p", "4k"):
        for e, l in zip(entries, low):
            if pick in l and "gif" not in l:
                want = e
                break
        if want:
            break
    if not want:
        raise VeoError(
            "Flow's download menu offered nothing downloadable — it listed "
            + (", ".join(repr(e) for e in entries) if entries
               else "nothing at all, so it never opened"))

    # NORMALISE BOTH SIDES. The entries are listed with their newlines folded to
    # spaces ("720p Original size"), and the element's own innerText still has
    # the newline in it ("720p\nOriginal size"), so matching the folded string
    # against the raw one finds nothing and the menu "loses" what it just showed.
    picked = bridge.call("eval", expr=(
        "var want = " + json.dumps(want) + ";"
        "var flat = function (e) {"
        "  return (e.innerText || '').split(String.fromCharCode(10)).join(' ').trim(); };"
        "var t = [].slice.call(document.querySelectorAll("
        "'[role=menuitem],[role=menuitemradio],[role=option],.cdk-overlay-pane button'))"
        ".filter(function (e) { return flat(e).indexOf(want) >= 0; })[0];"
        "if (!t) return null;"
        "t.setAttribute('data-pyq-q', '1');"
        "return want;"), timeout=60)["value"]
    if not picked:
        raise VeoError(f"the menu listed {want!r} and then lost it")
    print(f"  downloading: {picked}  (menu offered: {', '.join(entries)})")
    bridge.call("click", selector='[data-pyq-q="1"]', cdp=True, timeout=60)

    deadline = time.time() + timeout
    while time.time() < deadline:
        time.sleep(2.0)
        # A .crdownload beside it means Chrome is still writing.
        fresh = [p for p in dl_dir.glob("*.mp4") if p.name not in before]
        if fresh and not any(dl_dir.glob("*.crdownload")):
            src = max(fresh, key=lambda p: p.stat().st_mtime)
            time.sleep(1.0)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), dest)
            print(f"  saved {dest.name} ({dest.stat().st_size / 1e6:.1f} MB)")
            return dest
    raise VeoError(f"the download never landed in {dl_dir} within {timeout:.0f}s")


def _already_uploaded(bridge: FlowBridge, sel: dict, name: str) -> bool:
    """Whether Flow's Uploads already lists this file, so it need not go again."""
    opener = sel.get("reference_open") or 'button[aria-label^="Add ingredients"]'
    try:
        if bridge.call("eval", expr=(
                f"var t = document.querySelector({json.dumps(opener)});"
                "return !(t && t.getAttribute('aria-expanded') === 'true');"),
                timeout=30)["value"]:
            bridge.call("click", selector=opener, cdp=True, timeout=60)
            time.sleep(3.0)
        bridge.call("eval", expr=(
            "var t = [].slice.call(document.querySelectorAll('[role=tab]'))"
            "  .filter(function (e) { return (e.innerText || '').indexOf('Uploads') >= 0; })[0];"
            "if (t && t.getAttribute('aria-selected') !== 'true') {"
            "  t.setAttribute('data-pyq-up', '1'); return true; }"
            "return false;"), timeout=30)
        try:
            bridge.call("click", selector='[data-pyq-up="1"]', cdp=True, timeout=30)
            time.sleep(2.0)
        except FlowError:
            pass
        return bool(bridge.call("eval", expr=(
            "var want = " + json.dumps(name) + ";"
            "var pane = document.querySelector('.cdk-overlay-pane') || document;"
            "return (pane.innerText || '').indexOf(want) >= 0;"), timeout=30)["value"])
    except FlowError:
        return False


def attach_by_name(bridge: FlowBridge, sel: dict, name: str) -> int:
    """Attach the upload called `name` to the prompt. Returns the chip count.

    BY FILENAME, BECAUSE KEYS CANNOT IDENTIFY IT.
    The media set was being diffed around the upload and the new key attached.
    That is wrong twice over. One file becomes TWO keys (Flow renders the same
    asset as /asb/<token> in the picker and /image/<uuid> elsewhere), and the
    grid is virtualised, so opening the picker renders assets for the FIRST TIME
    and long-existing files appear in the diff as brand new. The run attached an
    ovule uploaded weeks ago to a DNA prompt, reported "1 chip attached", and
    generated from it.

    The filename is not ambiguous, and Flow prints it under the tile.
    """
    def ev(expr: str):
        return bridge.call("eval", expr=expr, timeout=60)["value"]

    opener = sel.get("reference_open") or 'button[aria-label^="Add ingredients"]'
    if ev(f"var t = document.querySelector({json.dumps(opener)});"
          "return !(t && t.getAttribute('aria-expanded') === 'true');"):
        bridge.call("click", selector=opener, cdp=True, timeout=60)
        time.sleep(3.0)

    # Uploads live behind their own tab; the file is not listed until it is open.
    if ev("var t = [].slice.call(document.querySelectorAll('[role=tab]'))"
          "  .filter(function (e) { return (e.innerText || '').indexOf('Uploads') >= 0; })[0];"
          "if (!t) return false;"
          "if (t.getAttribute('aria-selected') !== 'true') t.setAttribute('data-pyq-up', '1');"
          "return t.getAttribute('aria-selected') !== 'true';"):
        bridge.call("click", selector='[data-pyq-up="1"]', cdp=True, timeout=60)
        time.sleep(2.5)

    # WAIT FOR THE UPLOAD TO BE LISTED. set_image hands the file to Flow; Flow
    # then processes it, and until it does there is no tile to select. The first
    # run after this was written clicked a tile that was not there yet, selected
    # nothing, and found "Add to prompt" disabled — which reads like a broken
    # button rather than like being early.
    for _ in range(30):
        if ev("var want = " + json.dumps(name) + ";"
              "var pane = document.querySelector('.cdk-overlay-pane') || document;"
              "return (pane.innerText || '').indexOf(want) >= 0;"):
            break
        time.sleep(2.0)

    mark_js = (
        "var want = " + json.dumps(name) + ";"
        "var pane = document.querySelector('.cdk-overlay-pane') || document;"
        # THE SELECTABLE ELEMENT, not the row that contains it. "Add to prompt"
        # attaches whatever the picker has SELECTED, and clicking a wrapper div
        # leaves the selection where it was — so the click looked fine, one chip
        # appeared, and it was the background plate uploaded hours earlier.
        # Flow marks the selectable tile with role="option".
        # THE LAST MATCH, not the first. A retry that re-uploads leaves two
        # tiles with the same filename, and the older one may be scrolled out of
        # the list — clicking it selects nothing and "Add to prompt" stays
        # disabled, which reads as "the file is there but will not select".
        "var all = [].slice.call(pane.querySelectorAll('[role=option]'))"
        "  .filter(function (e) { return (e.innerText || '').indexOf(want) >= 0; });"
        "var hit = all.length ? all[all.length - 1] : null;"
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
        # The tile's own thumbnail URL. The chip on the prompt bar renders the
        # SAME /image/<uuid>, and the chip carries no filename of its own (its
        # alt is just "Ingredient image"), so this is the only way to prove
        # afterwards that what got attached is what was clicked.
        "var im = hit.querySelector('img');"
        "return (im && im.getAttribute('src')) || 'no-thumb';")
    marked = ev(mark_js)
    uid = _asset_uid(marked or "")
    if not marked:
        raise VeoError(
            f"{name} is not listed in Flow's Uploads — the upload did not land, "
            f"so there is nothing to attach and the clip would be generated "
            f"from whatever else is on the prompt bar")
    # CLICK IT AND CHECK IT TOOK. "Add to prompt" attaches the SELECTION, so a
    # click that lands but does not select leaves the previous asset attached.
    # PATIENCE AFTER AN UPLOAD. A file Flow has accepted is listed before it is
    # selectable, so the first clicks land on a tile that cannot yet preview.
    # Four tries at two seconds was not enough on a freshly uploaded reference.
    selected = False
    for _ in range(8):
        # RE-MARK EVERY TIME. The attribute is put on a tile that Flow may
        # re-render between tries — the list is virtualised — and clicking a
        # selector whose element has been replaced fails with "click target not
        # found", which reads as the file having vanished.
        if not ev(mark_js):
            time.sleep(2.0)
            continue
        bridge.call("click", selector='[data-pyq-asset="1"]', cdp=True, timeout=60)
        time.sleep(3.0)
        # WHAT CAN AND CANNOT BE VERIFIED HERE.
        #
        # Three ways of confirming the click selected the right asset were tried
        # and none survives Flow's DOM. `aria-selected` never leaves "false".
        # The tile's thumbnail and the preview's carry DIFFERENT id forms for
        # the same asset (/asb/<token> in the list, /image/<uuid> in the
        # preview), so comparing them refuses every correct attach. And the tile
        # element itself is replaced by a re-render the moment it is clicked, so
        # there is nothing left to interrogate afterwards.
        #
        # So the guarantee is moved to the two ends, which ARE solid: the tile
        # is chosen by FILENAME — the thing that actually goes wrong is choosing
        # by media key, which is what attached an ovule to a DNA prompt — and
        # the chip count afterwards proves nothing else came with it. The click
        # is judged to have landed when the tile is gone, which is what its
        # re-render means.
        selected = not ev("return !!document.querySelector('[data-pyq-asset=\"1\"]');")
        if selected:
            break
    if not selected:
        raise VeoError(
            f"{name} is listed in Flow's Uploads but clicking its tile did "
            f"nothing at all — the tile is still sitting there unchanged, so "
            f"'Add to prompt' would attach whatever was selected before it")

    # SELECTING IS NOT ATTACHING: the tile click moves the selection and the
    # "Add to prompt" button under the preview does the attaching.
    if ev("var d = document.querySelector('.cdk-overlay-pane');"
          "if (!d) return false;"
          "var a = [].slice.call(d.querySelectorAll('button,[role=button]'))"
          "  .filter(function (e) { return /add to prompt/i.test(e.innerText || ''); })[0];"
          "if (!a) return false;"
          "a.setAttribute('data-pyq-add', '1');"
          "return true;"):
        bridge.call("click", selector='[data-pyq-add="1"]', cdp=True, timeout=60)
        time.sleep(2.5)

    # THE SAME DEFINITION OF A CHIP the extension uses (chipsJs in
    # background.js): a button carrying an image and a remove control, at chip
    # size. Counting "small pictures near the bottom of the window" instead
    # returned 3 for one attached reference, because the picker's own thumbnails
    # are also small pictures near the bottom of the window.
    chips = ev(
        "var chips = [].slice.call(document.querySelectorAll('button,[role=\"button\"]'))"
        "  .filter(function (el) {"
        "    if (!el.querySelector('img')) return false;"
        "    var t = (el.innerText || '').trim().toLowerCase();"
        "    if (t.indexOf('cancel') < 0) return false;"
        "    var r = el.getBoundingClientRect();"
        "    return r.width > 20 && r.width < 160 && r.height > 20 && r.height < 160;"
        "  });"
        "return chips.map(function (el) { var i = el.querySelector('img');"
        "  return (i && i.getAttribute('src')) || ''; });") or []

    # WHERE THE PROOF ACTUALLY LIVES.
    #
    # It is tempting to compare the chip's image against the tile's, and that
    # was tried: the chip carries its own id, not the asset's, so the two never
    # match and every correct attach was refused. The chip cannot identify
    # itself — its alt text is "Ingredient image" and nothing else.
    #
    # So the proof is moved one step earlier, to the INPUT of the action rather
    # than its output: "Add to prompt" attaches whatever the picker is
    # previewing, and the preview has been verified above to be the file we
    # asked for by name. What remains for the count to catch is a stale chip
    # riding along beside it, which is the failure clear_prompt_refs exists for.
    return len(chips)


def _asset_uid(url: str) -> str:
    """The identity inside a Flow media URL, whichever form it takes."""
    m = re.search(r"/(?:image|video)/([0-9a-fA-F-]{20,})", url or "")
    if m:
        return m.group(1)
    m = re.search(r"/asb/([A-Za-z0-9_-]{12,})", url or "")
    return m.group(1) if m else "" 


def _new_media(bridge: FlowBridge, before: set[str]) -> tuple[list[str], list[str]]:
    """The keys that appeared since `before`, split into videos and stills.

    Two DIFFERENT things make a key that is not a clip, and both were found the
    expensive way:

      an upload   the plate and the textbook figure attached moments ago are
                  Flow media too, with a URL of exactly the same shape.
                  `generate_one` keeps those out by snapshotting after the
                  uploads settle.
      a placeholder
                  Flow mints a key as soon as a generation is QUEUED and renders
                  it as an <img> while the render runs. It appeared 23 seconds
                  after submit in the first real run — far too fast to be a
                  finished clip. Treating "a new key" as "the clip" therefore
                  does not merely risk the wrong file, it reliably returns a
                  still of a video that has not been made yet.

    So the wait is for a key rendered by a <video>, not for any key at all.
    """
    media = bridge.call("list_media", timeout=60).get("media", [])
    fresh = [m for m in media if m["key"] not in before]
    return (sorted(m["key"] for m in fresh if m.get("video")),
            sorted(m["key"] for m in fresh if not m.get("video")))


def _media_url(bridge: FlowBridge, key: str) -> str:
    for m in bridge.call("list_media", timeout=60).get("media", []):
        if m["key"] == key:
            return m["url"]
    raise VeoError(f"media {key} vanished from the page before it could be downloaded")


def _out_of_credits(banner: str) -> bool:
    """True only when Flow REFUSED the work, not when it warns about the balance.

    Flow shows one banner area for two different things: "You're out of Google
    Flow credits" (nothing was queued) and "You're running low on Google Flow
    credits" (queued normally). The second is persistent on a low account, so
    reading any banner as refusal makes the account unusable.
    """
    low = (banner or "").lower()
    if "running low" in low or "top up to get more now" in low and "out of" not in low:
        return False
    return bool(re.search(r"out of .*credits|no .*credits left|run out of", low))


def generate_one(bridge: FlowBridge, spec: dict, *, images: list[Path],
                 sel: dict, label: str, dest: Path,
                 project_url: str = "") -> Path:
    """Submit one prompt and block until Flow has rendered it, then save the file.

    Returns the path the clip was written to. The before/after key set is the
    mechanism — see the module header.

    `images` is ordered most-important-first and may hold the carry frame, the
    background plate and the textbook figure. They are cleared before they are
    set: Flow keeps its own state for the chips it has rendered, so attaching
    without clearing leaves the previous clip's reference attached to this one
    as well. See `clearImages` in flow/extension/background.js.
    """
    bridge.call("attach", timeout=60)

    # Recorded BEFORE anything is typed, because submitting navigates away from
    # it and there is then nothing to derive it from.
    if not project_url:
        here = _tab_state(bridge)["url"]
        m = PROJECT_RE.match(here)
        project_url = m.group(1) if m else here
    if "/edit/" in _tab_state(bridge)["url"]:
        print("  the tab is on a clip editor, not the project — going back")
        _back_to_grid(bridge, project_url)

    if images:
        # TWO STEPS, and skipping the second is silent. `set_image` drives
        # Flow's global uploader, which puts the file in the PROJECT LIBRARY;
        # it does not reference it from the prompt. Uploading alone therefore
        # looks completely successful and generates a clip with no reference at
        # all — Veo invents its own background and discards the plate, which is
        # exactly what §15 exists to prevent and exactly what shipped the first
        # time this ran. The asset has to be picked from the tray and added to
        # the prompt, and the proof is a chip on the prompt bar.
        # Clear FIRST. Attaching is additive, so anything already on the prompt
        # bar — a chip left by a previous beat, or by somebody testing by hand —
        # rides along into this generation as a second reference, and Veo blends
        # them. Nothing in the logs would say so; the run just quietly makes a
        # clip from two pictures.
        bridge.set_status(stage="clearing old references", detail=label)
        try:
            gone = bridge.call("clear_prompt_refs",
                               selector=sel.get("reference_chip_clear"), timeout=120)
            if gone.get("removed"):
                print(f"  cleared {gone['removed']} stale reference chip(s)")
            if gone.get("left"):
                print(f"  ⚠ {gone['left']} chip(s) would not clear — this clip is "
                      f"generated from more than its own reference")
        except FlowError as exc:
            print(f"  ⚠ could not clear old references: {exc}")

        bridge.set_status(stage="uploading reference images",
                          detail=", ".join(p.name for p in images))
        before = _media_keys(bridge)
        # ONE AT A TIME, deliberately. Uploading several and diffing the media
        # set afterwards leaves no way to say which key is which — the keys are
        # UUIDs, so ordering them is a coin flip, and attaching the wrong
        # picture looks exactly like attaching the right one.
        # UPLOAD ONCE. Every attempt re-uploaded the same reference, so a beat
        # on its third try had three identical tiles in Flow's Uploads and the
        # attach had to guess between them. The file does not change between
        # attempts; only the prompt does.
        for img in images:
            if _already_uploaded(bridge, sel, img.name):
                print(f"  {img.name} is already in Flow's Uploads")
                continue
            bridge.call("set_image", paths=[str(img)],
                        selector=sel["plate_input"],
                        open_selector=sel.get("reference_open"), timeout=180)
            time.sleep(2.0)

        # Attached BY FILENAME. See attach_by_name: the media keys cannot
        # identify an upload — one file becomes two of them, and the grid is
        # virtualised so files uploaded weeks ago show up in a before/after
        # diff as brand new. That is how an ovule ended up attached to a DNA
        # prompt with the run reporting "1 chip attached".
        time.sleep(3.0)
        for img in images:
            bridge.set_status(stage="attaching to the prompt", detail=img.name)
            chips = attach_by_name(bridge, sel, img.name)
            if chips != 1:
                raise VeoError(
                    f"attached {img.name} and the prompt bar carries {chips} "
                    f"reference chip(s), not 1 — a clip generated from more "
                    f"than its own reference is a blend of two pictures")
            print(f"  attached {img.name} ({chips} chip on the prompt)")

    # AFTER the uploads, never before. Every image attached above becomes Flow
    # media with a URL shaped exactly like a finished clip's, so a snapshot taken
    # earlier would leave the plate sitting in the "new since we started" set —
    # and the very first poll below would return it, download a PNG named .mp4,
    # and fail the visual review on a file that will not decode. That happens on
    # every beat that attaches anything, which since the plate is attached by
    # default is every beat.
    time.sleep(1.5)
    before = _media_keys(bridge)

    text = spec["prompt"]
    if spec.get("negative"):
        # Flow has no separate negative field; the house packs carry it inside
        # the prompt under its own heading, which is the form the tool was
        # tuned against.
        text = f"{text}\n\nNEGATIVE: {spec['negative']}"

    bridge.set_status(stage="typing the prompt", detail=label)
    bridge.call("set_prompt", text=text, selector=sel["prompt"], timeout=120)
    time.sleep(1.0)

    bridge.set_status(stage="submitting", detail=label)
    if sel.get("generate_selector"):
        bridge.call("click", selector=sel["generate_selector"], timeout=60)
    else:
        bridge.call("click", text=sel["generate_text"], timeout=60)

    time.sleep(SETTLE_AFTER_SUBMIT)
    deadline = time.time() + GENERATE_TIMEOUT

    # FLOW TELLS US WHICH CLIP IT MADE, so nothing has to be inferred.
    #
    # Submitting navigates the tab to /project/<id>/edit/<clip>: the new clip's
    # own editor. That used to be treated as the run going astray — the tab
    # drifting off the grid where the key diff was being taken — and it is
    # actually the answer. The page is the clip. It carries a Download control
    # attached to that clip, so there is no identification step left to get
    # wrong, and the whole before/after key business disappears with it.
    seen_progress = False
    submitted = time.time()
    while time.time() < deadline:
        left = int(deadline - time.time())
        st = _tab_state(bridge)
        editing = "/edit/" in st["url"]

        # OUT OF CREDITS IS NOT A SLOW GENERATION. Flow accepts the prompt,
        # queues nothing, and shows no progress — indistinguishable from a busy
        # queue until the timeout expires. It took thirty minutes to discover
        # once, and every further beat in the run would have taken thirty more.
        # The warning is in the page the whole time; read it.
        # "RUNNING LOW" IS NOT "OUT". The page shows a credits banner for both,
        # and treating either as fatal aborts every generation on an account
        # that is merely low — the banner is permanent there, so it fires before
        # progress can appear and no clip is ever made. Only refusal stops a run.
        if st.get("credits") and not seen_progress and _out_of_credits(st["credits"]):
            raise VeoError(
                f"Flow says: {st['credits']!r} — the generation was accepted by "
                f"the page but never queued, so nothing will arrive. Top up the "
                f"credits or switch account, then run this again; clips already "
                f"passed are kept and not regenerated.")

        if st["progress"]:
            seen_progress = True
            bridge.set_status(
                stage="waiting for Flow to render",
                detail=f"{label} — {st['progress'][0]}, up to {left // 60}m left")
            time.sleep(POLL_EVERY)
            continue

        # NOT WAITING TO BE CARRIED TO THE CLIP.
        #
        # Flow's prompt bar is a conversational agent now: it answers in text —
        # "I've started generating your DNA helix animation at 720p. It's
        # currently in the queue due to high demand" — and QUEUES the work, so
        # there is no dependable moment when it navigates to the result. Go and
        # look instead: open the newest clip and check its page carries THIS
        # prompt. Not carrying it means the queue has not got to us yet.
        if time.time() - submitted > FIRST_LOOK:
            try:
                open_newest_clip(bridge, project_url, expect=spec["prompt"],
                                 tries=1)
                return download_via_ui(bridge, dest, label=label)
            except VeoError as exc:
                print(f"  still waiting — {str(exc).split('. Either')[0]}")

        bridge.set_status(stage="waiting for Flow to render",
                          detail=f"{label} — up to {left // 60}m {left % 60}s left")
        time.sleep(POLL_EVERY)

    raise VeoError(
        f"Flow produced nothing for {label} within {GENERATE_TIMEOUT / 60:.0f} "
        f"minutes"
        + (" — it was rendering at some point, so it started and did not finish"
           if seen_progress else
           ", and it never showed a progress indicator, so the generation was "
           "probably never accepted. Check the tab: a prompt that fails its "
           "own safety or quota check shows an error in the UI")
        + ".")


def fetch(bridge: FlowBridge, key: str, dest: Path) -> Path:
    """Download one media key through the browser session and file it.

    Chrome refuses an absolute path or a `..` in `filename`, so the clip lands
    in ~/Downloads/pyq_flow_inbox first and is moved here afterwards. Do not try
    to shortcut that — the refusal surfaces as a bare "download refused".
    """
    url = _media_url(bridge, key)
    name = f"{dest.stem}.mp4"
    bridge.set_status(stage="downloading", detail=name)
    got = bridge.call("download", url=url, filename=inbox_rel(name), timeout=600)

    # Where the browser says it put the file beats where we asked it to. Chrome
    # drops the subdirectory from `filename` some of the time — the same
    # relative path landed in the inbox on one call and in ~/Downloads on the
    # next — and waiting at the path we asked for turns a download that
    # completed perfectly into "the download never landed".
    candidates = []
    if got.get("path"):
        candidates.append(Path(got["path"]))
    candidates += [inbox_dir() / name, DOWNLOAD_DIR / name]

    src = None
    for _ in range(30):
        src = next((c for c in candidates if c.is_file() and settled(c)), None)
        if src is not None:
            break
        time.sleep(1.0)
    if src is None:
        raise VeoError(
            "the download never landed. Looked in:\n  "
            + "\n  ".join(str(c) for c in candidates))
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(dest))
    return dest


# --------------------------------------------------------------------------- #
# The stage
# --------------------------------------------------------------------------- #
def run(project: str, part: int, *, attempts: int = MAX_ATTEMPTS, dry_run: bool = False,
        use_plate: bool = True, provider: str | None = None,
        regenerate: bool = False, bridge: FlowBridge | None = None) -> dict:
    root = resolve(project)
    beats, lines, meta = video_beats(root, part)
    all_beats = json.loads((root / f"beats_part{part}.json").read_text(encoding="utf-8"))
    if not beats:
        print(f"no `type: video` beats in part {part} — nothing for Veo to do")
        return {"clips": []}

    clip_end = float(meta["clip_end"][str(part)])

    # The three inputs a prompt is written from, in the order they carry weight.
    #   question   what was asked, and therefore what the answer owes the student
    #   accuracy   the CORRECTED answer. verification.md exists because every
    #              sheet answer checked so far has contained real errors, and an
    #              animation of a wrong answer is worse than no animation
    #   script     what the teacher actually says, so the clip illustrates the
    #              explanation being given rather than the topic in general
    question = meta.get("question", "")
    accuracy = ""
    for name in ("accuracy_brief.md", "verification.md"):
        f = root / name
        if f.is_file():
            accuracy = f.read_text(encoding="utf-8")[:6000]
            break
    script = ""
    for name in ("script_bhaag.md", "script.md"):
        f = root / name
        if f.is_file():
            script = f.read_text(encoding="utf-8")[:8000]
            break

    full_plate = veo_prompts.plate_for(meta.get("subject", "")) if use_plate else None
    # Resolved for every beat up front. Doing it lazily inside the loop means a
    # missing crop is discovered after the earlier clips have been generated and
    # paid for, and the run then dies holding results it never writes out.
    # `tools/preflight_beats.py` checks the same thing earlier still; this is the
    # backstop for a run that skipped it.
    refs = {int(b["at"]): veo_prompts.reference_for(root, b["reference"])
            for b in beats if b.get("reference")}
    sel = _selectors()
    out_dir = root / "veo"
    work = out_dir / "review"
    out_dir.mkdir(parents=True, exist_ok=True)

    # ALREADY DONE IS ALREADY PAID FOR. A part is written out only when every
    # beat in it is finished, so one crash on the last beat threw away a clip
    # that had passed its review — and the next run generated it again. Beats
    # with a usable clip on record are skipped and carried through untouched.
    done = {}
    prior = root / f"clips_part{part}.json"
    if prior.is_file() and not regenerate:
        for c in json.loads(prior.read_text(encoding="utf-8")):
            if c.get("usable"):
                done[int(c["at"])] = c
    if done:
        print(f"{len(done)} clip(s) already passed: "
              + ", ".join(f"beat@{a}" for a in sorted(done)))

    own = bridge is None
    b = bridge or FlowBridge().start()
    results, reviews = [], []
    try:
        info = b.wait_for_worker(timeout=90)
        print(f"extension connected — flow tab: {info.get('tab')}")
        m = PROJECT_RE.match(info.get("tab") or "")
        project_url = m.group(1) if m else (info.get("tab") or "")
        if not info.get("tab"):
            raise VeoError("no Google Flow tab is open. Open your Flow project in "
                           "any tab — it can stay in the background.")

        runs = veo_sequence.spans(beats)
        number = {id(bt): i for i, bt in enumerate(beats, 1)}
        sequenced = [r for r in runs if len(r) > 1]
        if sequenced and not sel.get("reference_clear"):
            # Said once, loudly, at the top of the run rather than per clip.
            print("  ⚠ flow/selectors.json has no `reference_clear` selector. "
                  "Emptying the file input does not remove the reference chips "
                  "Flow has already rendered, so a carry frame may stay attached "
                  "to the clip after next. Inspect the ✕ on a reference chip once "
                  "and put its selector there.")
        for seq_run in runs:
            if len(seq_run) > 1:
                print(f"\n--- {veo_sequence.describe(seq_run)} ---")
            carry = veo_sequence.Carry(sequence=seq_run[0].get("sequence") or "")
            prev_spec: dict | None = None

            for k, beat in enumerate(seq_run):
                n = number[id(beat)]
                if int(beat["at"]) in done:
                    print(f"\n=== part{part} beat@{beat['at']} ({n}/{len(beats)}) "
                          f"— already done, keeping it ===")
                    results.append(done[int(beat["at"])])
                    continue
                label = f"part{part} beat@{beat['at']} ({n}/{len(beats)})"
                b.set_status(run=root.name, scene=label, stage="writing the prompt")
                print(f"\n=== {label} ===\n{beat['brief']}")

                frame = veo_prompts.frame_of(beat)
                green = veo_prompts.is_green(beat)
                layout = veo_prompts.layout_of(beat)
                backdrop = veo_prompts.backdrop_of(beat)
                style = veo_prompts.style_of(beat)
                # THE PLATE IS PER BEAT, because a panel clip does not cover the
                # whole frame. It is generated in landscape and laid into rows
                # `top`..`seam`, so the picture it must be built on is that band
                # — not the portrait plate, which is a different shape showing
                # mostly frame the clip never reaches.
                plate = full_plate if backdrop == "plate" else None
                if plate is not None and layout == "panel":
                    from src import panel_layout as PL
                    kw = {}
                    if beat.get("panel_ar"):
                        kw["panel_ar"] = float(beat["panel_ar"])
                    if beat.get("panel_top") is not None:
                        kw["top_margin"] = int(beat["panel_top"])
                    plate = PL.plate_band(full_plate, PL.geometry(1920, 1080, **kw))
                full = frame == "full"          # kept for clips_part<N>.json

                # What this generation is built from. A standalone beat resolves
                # to exactly what it always did — plate, no carry, no reference —
                # which is what keeps every existing project's behaviour intact.
                ref = refs.get(int(beat["at"]))
                carried = carry.frame is not None
                # Captured HERE, not read back at the end. By the time this
                # beat's result is written the carry has already advanced to
                # this beat's own frame, so reading `carry.source_at` there
                # records every clip as continuing from itself — and it does it
                # only for the clips that PASSED, which is the half of the data
                # somebody would be reading to find the seams.
                continues_from = carry.source_at if carried else None
                position = (f"clip {k + 1} of {len(seq_run)}"
                            if len(seq_run) > 1 else "")
                if carried:
                    note = f"continuing beat@{carry.source_at}"
                    if carry.broken:
                        note += " (the clip in between failed its review and was "
                        note += "not carried forward)"
                    print(f"  chained: {note}")
                if ref:
                    print(f"  textbook reference: {_rel(ref)}")

                spec = veo_prompts.write_prompt(
                    brief=beat["brief"], lines=lines, at=int(beat["at"]),
                    look=beat.get("look", ""),
                    subject=meta.get("subject", ""), question=question,
                    accuracy=accuracy, frame=frame, green=green,
                    script=script, duration=GEN_SECONDS, layout=layout,
                    backdrop=backdrop, style=style, provider=provider,
                    carried=carried, referenced=ref is not None,
                    previous=prev_spec, position=position)

                history, clip, review, cont = [], None, None, None
                for attempt in range(1, attempts + 1):
                    bad = veo_prompts.audit(spec, carried=carried,
                                            backdrop=backdrop, style=style,
                                            referenced=ref is not None)
                    if bad:
                        # Fixed before a credit is spent: these are the failures
                        # we already know the shape of, so paying Veo to
                        # demonstrate them again would be a waste.
                        print(f"  prompt audit found {len(bad)} problem(s); revising")
                        for line in bad:
                            print(f"    - {line}")
                        spec = veo_prompts.revise_prompt(spec, bad, provider=provider)

                    if dry_run:
                        # SAVE IT. The prompt is written by a model, so a second
                        # run writes a different one — reviewing prompt A and
                        # then generating from prompt B is no review at all.
                        # veo_manual.py grades a hand-made clip against the
                        # `checks` stored here, so they have to be the checks
                        # that belong to the prompt actually used.
                        pj = root / "veo" / "prompts.json"
                        rec = json.loads(pj.read_text(encoding="utf-8")) if pj.is_file() else []
                        rec = [r for r in rec
                               if not (str(r.get("part")) == str(part)
                                       and str(r.get("at")) == str(beat["at"]))]
                        rec.append({"part": str(part), "at": str(beat["at"]),
                                    "brief": beat["brief"],
                                    "words": len(spec["prompt"].split()),
                                    "audit": [], **spec})
                        pj.parent.mkdir(parents=True, exist_ok=True)
                        pj.write_text(json.dumps(rec, ensure_ascii=False, indent=1),
                                      encoding="utf-8")
                        print(f"  saved to {pj.relative_to(root.parent.parent)}")

                        # PROMPT REVIEW BEFORE CREDITS. A generation costs
                        # twelve credits and a bad prompt costs three of them
                        # before anyone reads what was actually asked for. The
                        # prompt is the whole job on this route, so it gets to
                        # be looked at first.
                        print(f"\n  ---- part{part} beat@{beat['at']} prompt "
                              f"({len(spec['prompt'].split())} words) ----")
                        print("  " + spec["prompt"].replace("\n", "\n  "))
                        print(f"\n  ---- negative ----\n  "
                              + spec["negative"][:900].replace("\n", "\n  "))
                        print("\n  ---- checks the review will grade against ----")
                        for c in spec["checks"]:
                            print(f"    - {c}")
                        print()
                        break

                    print(f"  attempt {attempt}/{attempts}: submitting")
                    # A keyed clip needs NO reference at all — no plate, and no
                    # carry frame either, because continuity across a sequence
                    # comes from compositing onto the same rendered background
                    # rather than from Veo remembering anything. That removes the
                    # upload-and-attach path, which is the most fragile thing in
                    # this route and the source of most of its failures.
                    # NO REFERENCE AT ALL unless the clip is generated ON the
                    # plate. `green` is keyed and `own` is laid into a
                    # designated panel, and neither has anything to match — so
                    # the whole upload-and-attach path drops out, and with it
                    # the asset picker, the reference chips and every failure
                    # that comes with driving them.
                    # THE PLATE is only for a clip generated ON the house
                    # background. A REFERENCE is for any clip at all: it is the
                    # strongest way to fix what the subject is made of, and
                    # words had already failed at that four generations running
                    # — a third backbone, rungs floating free, hexagonal caps
                    # nobody asked for, at 611 words of prompt.
                    images = veo_sequence.uploads(
                        plate=plate if backdrop == "plate" else None,
                        reference=ref,
                        carry=carry.frame if backdrop == "plate" else None)
                    dest = out_dir / f"part{part}_at{beat['at']:03d}_try{attempt}.mp4"
                    clip = generate_one(b, spec, images=images, sel=sel,
                                        label=label, dest=dest,
                                        project_url=project_url)
                    # Back to the grid so the next beat starts from the prompt
                    # bar rather than from this clip's editor.
                    _back_to_grid(b, project_url)

                    # THE MARKER COMES OFF BEFORE THE REVIEW.
                    # Flow stamps a sparkle into every clip after generation, so
                    # no prompt prevents it and every reviewer reports it — a
                    # fail that costs a regeneration and comes back identical.
                    stripped = clip.with_name(clip.stem + "_clean.mp4")
                    clip, mark = veo_delogo.strip(clip, stripped)
                    if mark:
                        print(f"  removed Flow's marker at {mark}")

                    b.set_status(stage="reviewing the frames", detail=dest.name)
                    review = veo_qc.review(clip, spec, work=work, brief=beat["brief"],
                                           frame=frame,
                                           plate=None if green else plate,
                                           green=green, layout=layout,
                                           backdrop=backdrop, style=style,
                                           provider=provider)
                    review.update(attempt=attempt, clip=str(clip.relative_to(root)),
                                  at=int(beat["at"]), prompt=spec["prompt"],
                                  negative=spec.get("negative", ""))

                    # The seam is graded only when there is one, and only once
                    # the clip is otherwise good: a clip that failed its facts is
                    # being regenerated anyway, and asking whether a wrong clip
                    # matches the previous frame is a question with no useful
                    # answer.
                    cont, seam = None, []
                    if carried and review["verdict"] != "fail":
                        b.set_status(stage="checking the seam", detail=label)
                        cont = veo_qc.continuity(carry.frame, clip, work=work,
                                                 provider=provider)
                        review["continuity"] = cont
                        seam = veo_qc.seam_defects(cont)
                        if seam:
                            review["verdict"] = "fail"
                            print("  seam: the clip does not continue the previous one")
                    elif carried:
                        review["continuity"] = None
                    reviews.append(review)
                    print(f"  review: {review['verdict']} — {review['summary']}")

                    if review["verdict"] != "fail":
                        if cont:
                            print("  seam: continuous")
                        break
                    defects = veo_qc.defect_lines(review) + seam
                    for d in defects:
                        print(f"    - {d}")
                    history.append(spec)
                    if attempt < attempts:
                        spec = veo_prompts.revise_prompt(spec, defects, provider=provider)

                start, end = window(beat, all_beats, lines, clip_end)
                # THE CLIP IS FITTED TO THE PRESENTER, NEVER THE OTHER WAY ROUND.
                # Flow returns a fixed ~8s and the presenter talks for as long as
                # he talks; the tail Veo hallucinated is cut here and the good
                # part is slowed, looped or held to cover the window. See
                # src/veo_conform.py for why the choice between those three is a
                # teaching decision.
                if dry_run:
                    # Nothing was generated, so there is no clip to grade, fit
                    # or label. Straight on to the next beat's prompt.
                    continue

                motion = beat.get("motion", "one_way")
                if motion == "cyclic" and not review.get("loopable"):
                    print("  ⚠ the beat says the motion is cyclic but the review says "
                          "this clip does not return to where it started; holding the "
                          "final state instead of looping a visible jump")
                    motion = "settling"
                good = review.get("good_until")
                b.set_status(stage="fitting the clip to the window", detail=label)
                fitted = out_dir / f"part{part}_at{beat['at']:03d}.mp4"
                # A LABEL THAT ASKS FOR A PAUSE TAKES ITS TIME FROM THE MOTION,
                # not from the window: conform to what is left, then freeze. Fit
                # the other way round and the conform speeds the freezes up
                # along with everything else, undoing them. src/veo_holds.py.
                try:
                    holds = veo_holds.plan(beat, lines, start, end)
                except ValueError as exc:
                    print(f"  ⚠ {exc} — the pauses are dropped for this beat")
                    holds = []
                need = veo_holds.content_seconds(end - start, holds)
                if holds:
                    print(f"  {len(holds)} label pause(s): {need:.1f}s of motion "
                          f"+ {sum(h['hold'] for h in holds):.1f}s frozen "
                          f"= {end - start:.1f}s on screen")
                try:
                    fit = veo_conform.conform(clip, fitted, good_until=good,
                                              need=need, strategy=motion)
                    if holds:
                        veo_holds.apply_holds(fitted, holds,
                                              fitted.with_name(fitted.stem + "_held.mp4"))
                        fitted.with_name(fitted.stem + "_held.mp4").replace(fitted)
                    print(f"  fitted: {fit['had']}s generated, {fit['usable']}s usable"
                          + (f" ({fit['trimmed']}s of tail cut)" if fit["trimmed"] > 0.05
                             else "")
                          + f" -> {fit['need']}s on screen by {motion}")
                    if review.get("tail_problem") and fit["trimmed"] > 0.05:
                        print(f"    the cut tail: {review['tail_problem']}")
                except veo_conform.ConformError as exc:
                    # Not fatal: the unconformed clip is still on disk and still
                    # reviewable, and a run that has already paid for every clip
                    # should not end with nothing written.
                    print(f"  ⚠ could not fit this clip to its window: {exc}")
                    fit, fitted = None, clip
                    review["verdict"] = "fail"

                # Hand this clip's last frame to the next one in the sequence — but
                # only if the review accepted it. Carrying a rejected frame is
                # how one bad generation becomes the whole sequence, and it does
                # it while looking MORE consistent than the correct version.
                passed = review["verdict"] != "fail"
                if len(seq_run) > 1:
                    if passed:
                        try:
                            carry.accept(int(beat["at"]), veo_sequence.carry_frame(
                                fitted, out_dir / "carry"
                                / f"part{part}_at{beat['at']:03d}.png"))
                        except veo_sequence.SequenceError as exc:
                            print(f"  ⚠ {exc}")
                            carry.reject(int(beat["at"]))
                    else:
                        print("  this clip was not accepted, so the next clip in "
                              "the sequence continues from "
                              + (f"beat@{carry.source_at} instead"
                                 if carry.frame else "nothing"))
                        carry.reject(int(beat["at"]))
                    if passed:
                        prev_spec = spec

                # The one thing besides the animation allowed on screen. Typeset
                # here rather than generated, because Veo cannot set Devanagari —
                # see src/veo_labels.py.
                labels = veo_labels.build(beat, lines, start, end, out_dir / "labels",
                                          f"part{part}_at{beat['at']:03d}")
                for a in labels:
                    # Stored project-relative, like `src`, so the project survives
                    # being moved or rendered on another machine.
                    a["png"] = str(Path(a["png"]).relative_to(root))
                for bad in label_faults(labels, frame=frame,
                                        band=panel_band(beat)):
                    print(f"  ⚠ {bad}")
                results.append({
                    "at": int(beat["at"]),
                    "start": round(start, 2),
                    "end": round(end, 2),
                    "src": str(fitted.relative_to(root)),
                    "raw": str(clip.relative_to(root)),
                    "full": full,
                    "frame": frame,
                    # The compositor keys this clip rather than laying it in
                    # opaque, so it has to travel with the clip. Without it a
                    # chroma clip is composited green side out.
                    "green": green,
                    "backdrop": backdrop,
                    "labels": labels,
                    "fit": fit,
                    "verdict": review["verdict"],
                    "attempts": review["attempt"],
                    "layout": layout,
                    # Panel geometry travels with the clip because it is a
                    # property of the RENDERER the clip is laid into, not of the
                    # generation. The HTML band renderer puts its caption at
                    # y=58..252, so the 84px default top margin erases it; a beat
                    # rendered there says where its panel actually goes.
                    "panel_ar": beat.get("panel_ar"),
                    "panel_top": beat.get("panel_top"),
                    "sequence": beat.get("sequence"),
                    "continues_from": continues_from,
                    "continuity": review.get("continuity"),
                    "reference": str(ref.relative_to(root)) if ref else None,
                    # A `fail` still gets written out. Deleting it would leave the
                    # part with a silent hole and nothing to look at; recorded as a
                    # failure, it is a clip somebody can watch and overrule.
                    "usable": review["verdict"] != "fail",
                })
    finally:
        b.set_status(stage="idle", scene=None, detail="")
        if own:
            try:
                b.call("detach", timeout=15)
            except FlowError:
                pass
            b.stop()

    (root / f"veo_prompts_part{part}.json").write_text(
        json.dumps([{"at": r["at"], "src": r["src"], "verdict": r["verdict"]}
                    for r in results], ensure_ascii=False, indent=2), encoding="utf-8")
    veo_qc.write_report(root / f"veo_review_part{part}.json", reviews)
    clips_f = root / f"clips_part{part}.json"
    clips_f.write_text(json.dumps(results, ensure_ascii=False, indent=2),
                       encoding="utf-8")

    bad = [r for r in results if not r["usable"]]
    print(f"\n{len(results)} clip(s) -> {_rel(clips_f)}")

    # A sequence with a hole in it still ships — the clips on either side of the
    # hole are fine and the part is better with them than without. But the hole
    # is exactly the thing that is invisible in the output files, so it is said
    # here rather than left to be discovered in the finished video.
    holes = [r for r in results if r.get("sequence") and r["usable"]
             and r.get("continues_from") is None and r is not _first_of(results, r["sequence"])]
    for r in holes:
        print(f"⚠ sequence {r['sequence']!r} restarts at beat@{r['at']} — the clip "
              f"before it was rejected, so this one was generated from the plate "
              f"rather than from a carried frame. Expect a visible cut there.")
    if bad:
        print(f"{len(bad)} did NOT pass the visual check after {attempts} attempts:")
        for r in bad:
            print(f"  beat@{r['at']}  {r['src']}")
        print(f"see {_rel(root / f'veo_review_part{part}.json')} "
              f"for what the review saw, and the sampled frames in "
              f"{_rel(work)}")
    return {"clips": results, "reviews": reviews}
