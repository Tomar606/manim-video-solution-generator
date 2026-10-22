"""Download finished clips out of Google Flow, without touching the mouse.

    python veo_kit/fetch.py --prompts projects/<slug>/veo/prompts/landscape \
        --out projects/<slug>/veo/clips --aspect landscape
    python veo_kit/fetch.py --prompts ... --list          # identify, download nothing
    python veo_kit/fetch.py --prompts ... --expect 4      # wait for four to finish

Next to each clip it writes <brief>.sent.txt: the prompt Flow's agent actually
generated from, which is NOT what was typed (see identify()).

`--prompts` is a folder of sNN.txt files (what build_prompts.py writes) or a
prompts.json list of {"brief", "prompt"}. Each clip is saved as <brief>.mp4.

WHY THIS EXISTS
---------------
The PYQ track's `tools/veo_manual.py` was written because the clip could not be got out of the
page: the grid is virtualised, finished clips render as <img> rather than
<video>, and neither URL family in the DOM is the video — the /image/ keys are
poster stills and the /asb/ keys do not download at all. That is all still true.

The way through is not to find the URL. It is to press Flow's own Download
button and let Chrome save the file, then pick it up from the download
directory. The clip editor carries `button[aria-label="Download media"]`, which
opens a quality menu — 270p GIF, 720p Original size, 1080p Upscaled, 4K
Upscaled. **720p is the real generation**; the others are upscales of it, so
this takes 720p and calls it what it is.

IDENTIFYING WHICH CLIP IS WHICH
-------------------------------
Not by position, and not by diffing media keys — both were tried and both are
unreliable while the grid virtualises. The GRID's tiles carry only generic
labels ("Scene video preview"); the descriptive ones Flow writes from the prompt
live in the EDITOR's filmstrip. So this opens one clip and then walks the
filmstrip with `Next media`, and identifies the clip it is looking at the way
src/veo.py does: by checking that slices of a known prompt appear on the page.

The probes are taken from the MIDDLE of each prompt, never the start — every
prompt in this track opens with the same house sentences, so a probe from the
beginning matches every clip equally.

ASPECT IS CHECKED ON ARRIVAL. Flow returns whatever the project's output
setting says, not what the prompt asked for: a clip ordered 16:9 came back
720x1280 and cost a rebuild. A clip in the wrong shape for --aspect is reported
loudly here rather than discovered in the edit.

THE TAB IS SHARED. If it is on a /character/ page, someone is building a Flow
Character there, and this stops rather than navigating their work away.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import flowkit as fk                                    # noqa: E402
from flowkit import FlowError, SCROLL_TOP_JS, ROOT      # noqa: E402

_tab_state = fk.tab_state

from src.flow_bridge import DOWNLOAD_DIR as DOWNLOADS   # noqa: E402  (FLOW_DOWNLOAD_DIR)
QUALITY = "720p"                 # the generation itself; everything else is upscaled
SETTLE = 2.5


def _eval(b, js, timeout=60):
    return fk.ev(b, js, timeout)


# WHICH <img> IS A CLIP TILE. Flow says so itself: grid tiles carry alt text
# "Generated video thumbnail" (clips), "Tile displaying a user's image"
# (uploads) and "Character thumbnail" (Flow Characters). The agent chat panel's
# inline previews carry the PROMPT as their alt. Image hosts and sizes were
# tried first and both flipped between Flow builds: on 22 Sept 2026 the grid
# moved to /asb/ images and the chat panel to /image/ ones, and a rule written
# for the old layout opened only the chat panel's six stale clips.
TILES_FN = r"""
function tiles(){
  var all = Array.prototype.slice.call(document.querySelectorAll('img'));
  var t = all.filter(function(i){ return /generated video/i.test(i.alt||'') &&
                                         i.getBoundingClientRect().width > 150; });
  if (!t.length) t = all.filter(function(i){ var r = i.getBoundingClientRect();
      return r.width > 150 && !/character|user's image/i.test(i.alt||'') &&
             /flow-content\.google\/image\//.test(i.currentSrc||i.src||''); });
  return t;
}
"""
TILES_JS = TILES_FN + "return tiles().length;"

# THE FILMSTRIP DOES NOT WALK BETWEEN CLIPS. `Next media` moves within a scene,
# not between generations, so each clip is opened from the GRID by index.
TILE_SRC_JS = TILES_FN + r"""
var t = tiles();
if (t.length <= %d) return null;
return t[%d].currentSrc || t[%d].src;
"""

PAGE_TEXT_JS = ("return (document.body.innerText || '')"
                ".split(String.fromCharCode(10)).join(' ').toLowerCase();")


def probes(prompt: str, n: int = 8, width: int = 46) -> list[str]:
    """Slices spread through a prompt, for recognising its clip's page.

    Never from the start: every prompt in this track opens with the same house
    sentences, so a probe from the beginning matches every clip equally.
    """
    flat = " ".join(prompt.split()).lower()
    fr = [0.15 + i * (0.70 / max(1, n - 1)) for i in range(n)]
    out = [flat[int(len(flat) * f):int(len(flat) * f) + width] for f in fr]
    return [x for x in out if len(x) == width]


QUOTED = re.compile(r'["“”]([^"“”]*[ऀ-ॿ][^"“”]*)["“”]')


def _norm(t: str) -> str:
    """The Devanagari only.

    The agent re-punctuates and re-spaces but never re-words, so the letters of
    the spoken line identify the clip — as long as what is compared is only
    those letters. Flow's page prints an em dash inside a prompt as the literal
    text "\u2014", and keeping the Latin in the comparison put "u2014" in the
    middle of the line, so the probe no longer matched its own clip."""
    return "".join(c for c in t if "\u0900" <= c <= "\u097f")


def spoken(prompt: str) -> list[str]:
    return [_norm(m) for m in QUOTED.findall(prompt) if len(_norm(m)) > 12]


def identify(page: str, known: dict[str, str]) -> str | None:
    """Which known prompt this clip page belongs to.

    BY THE SPOKEN LINE FIRST. The grid's prompt box is Flow's AGENT: it rewrites
    every prompt before generating, and the clip page shows the rewrite, not
    what was typed. It paraphrases the English freely ("the camera holding
    still" became "static camera") but has kept the quoted Hindi line verbatim
    every time, so the line is what survives to identify the clip.

    THEN BY PROMPT SLICES, for prompts with no dialogue: best score with a
    margin, because prompts share their house sentences and a slice can match
    several of them. A tie is reported as unknown rather than guessed — a
    misfiled clip puts one scene's picture under another scene's words.
    """
    flat = " ".join(page.split())
    squashed = _norm(flat)
    hits = [slug for slug, pr in known.items()
            if spoken(pr) and all(l in squashed for l in spoken(pr))]
    if len(hits) == 1:
        return hits[0]
    if len(hits) > 1:
        return None
    scores = []
    for slug, prompt in known.items():
        p = probes(prompt)
        scores.append((sum(1 for x in p if x in flat), len(p), slug))
    scores.sort(reverse=True)
    if not scores:
        return None
    best, total, slug = scores[0]
    # With one candidate there is no runner-up, so it must clear a high bar alone.
    if len(scores) == 1:
        if best >= max(3, int(total * 0.6)):
            return slug
    elif best >= 3 and best - scores[1][0] >= 2:
        return slug
    return by_content_words(flat, known)


# Words every b-roll prompt shares (house sentences, the negative list) and
# ordinary English: none of them says WHICH shot a page is.
_COMMON = set("""live action video footage filmed with real camera shot holding still framed
tall continuous motion throughout natural colour soft daylight vertical frame silent voiceover
negative their there these those where which while front behind through across along around
toward towards between beside under above about after before other every still keeps keep
moving moves wide medium close slowly small large long high very""".split())


def by_content_words(page: str, known: dict[str, str]) -> str | None:
    """B-ROLL HAS NO SPOKEN LINE, AND THE AGENT PARAPHRASES THE ENGLISH.

    The 46-character slices above never survive a rewrite ("the camera holding
    still" -> "static camera"), so every b-roll tile came back `unknown` and a
    finished, paid-for clip was skipped (GEO-C4-SA-02 b01, 9 Oct). What the
    rewrite DOES keep is the nouns that make the shot this shot: Changpa,
    Ladakh, yak, spindle, Rabari, camels. So score each prompt by the share of
    its distinctive words present on the page, and demand both a high share and
    a clear margin over the runner-up."""
    def words(t: str) -> set[str]:
        t = t.split("NEGATIVE:")[0].lower()
        return {w for w in re.findall(r"[a-z]{5,}", t) if w not in _COMMON}
    page_words = set(re.findall(r"[a-z]{5,}", page.lower()))
    scored = sorted(((len(words(p) & page_words) / max(1, len(words(p))), slug)
                     for slug, p in known.items() if words(p)), reverse=True)
    if not scored:
        return None
    best, slug = scored[0]
    runner = scored[1][0] if len(scored) > 1 else 0.0
    return slug if best >= 0.45 and best - runner >= 0.15 else None


# What the agent actually sent to the model sits between the player controls
# and the timeline on the clip page.
SENT_RE = re.compile(r"\brepeat\s+(?:add\s+)*(.*?)\s+keyboard_return\b", re.S)


def sent_prompt(raw_page: str) -> str:
    m = SENT_RE.search(" ".join(raw_page.split()))
    return re.sub(r"^(?:add\s+)+", "", m.group(1).strip()) if m else ""


def _to_top(b) -> None:
    """Put the virtualised media list back at the top before reading it.

    The grid renders only what is near the viewport, so the same page answered
    "5 tiles" and then "no tiles" a minute later depending on where it had been
    scrolled. Everything here counts and indexes tiles, so it has to start from
    a known position.
    """
    try:
        _eval(b, SCROLL_TOP_JS)
    except Exception:                                    # noqa: BLE001
        pass
    time.sleep(2.0)


def tile_count(b, tries: int = 4) -> int:
    """How many clip tiles the grid shows, WAITING for it to draw them.

    back_to_grid returns as soon as the prompt box exists, and the tile list is
    rendered after that: a count taken immediately reported "0 clip(s) in the
    project" on a project holding twelve."""
    for k in range(tries):
        _to_top(b)
        n = int(_eval(b, TILES_JS) or 0)
        if n:
            return n
        time.sleep(3.0)
    return 0


def open_nth(b, n: int) -> bool | str:
    """Open the n-th clip tile, surviving the grid re-rendering under us.

    The grid is virtualised: scrolling a tile into view REPLACES its DOM node,
    so a marker set before the scroll is gone by the time of the click — which
    raised "click target not found" and killed the whole fetch. The tile is
    therefore remembered by its image SOURCE, which survives a re-render, and
    looked up again after scrolling. One tile failing is reported, not fatal.
    """
    _to_top(b)
    src = _eval(b, (TILE_SRC_JS % (n, n, n)))
    if not src:
        return False
    find = ("var t=Array.prototype.slice.call(document.querySelectorAll('img'))"
            ".filter(function(i){return (i.currentSrc||i.src)===%s;});"
            "if(!t.length) return false; var e=t[0];"
            "for(var k=0;k<8&&e;k++){ if(e.getBoundingClientRect().width>150) break;"
            " e=e.parentElement; }"
            "document.querySelectorAll('[data-pyq-open]').forEach(function(x){"
            "x.removeAttribute('data-pyq-open');});"
            "(e||t[0]).setAttribute('data-pyq-open','1');"
            "(e||t[0]).scrollIntoView({block:'center'}); return true;") % json.dumps(src)
    for _ in range(3):
        if not _eval(b, find):
            time.sleep(1.5); continue
        time.sleep(1.5)
        if not _eval(b, find):                     # re-rendered by the scroll
            continue
        try:
            b.call("click", selector='[data-pyq-open="1"]', cdp=True, timeout=60)
        except FlowError:
            time.sleep(1.5); continue
        time.sleep(6.0)
        url = _tab_state(b).get("url") or ""
        if "/edit/" in url:
            return True
        # FLOW CHARACTERS ARE TILES TOO. A character card sits in the grid with
        # the same kind of poster image as a clip, and clicking it opens the
        # character's own page. WE opened it, so leaving is safe here; it is a
        # character page someone ELSE opened that back_to_grid refuses to leave.
        if "/character/" in url:
            _eval(b, "location.href = %s; return 1;" % json.dumps(url.split("/character/")[0]))
            time.sleep(4.0)
            fk.back_to_grid(b, url.split("/character/")[0])
            return "character"
    return False


def download_current(b, quality: str = QUALITY) -> bool:
    """Press Download, choose the quality, and let Chrome save it."""
    b.call("click", selector='button[aria-label="Download media"]', cdp=True, timeout=60)
    time.sleep(SETTLE)
    js = ("var hit=null;document.querySelectorAll('[role=menuitem]').forEach(function(e){"
          "if(/%s/.test(e.innerText||'')) hit=e;});"
          "if(!hit) return false; hit.setAttribute('data-pyq-q','1'); return true;" % quality)
    if not _eval(b, js):
        return False
    b.call("click", selector='[data-pyq-q="1"]', cdp=True, timeout=60)
    return True


def wait_for_file(before: set[Path], timeout: float = 180.0) -> Path | None:
    """The newest .mp4 that was not there before, once it stops growing.

    Chrome writes a .crdownload while the transfer is in flight; waiting for a
    stable size is what stops a half-written file being handed to ffprobe.
    """
    end = time.time() + timeout
    while time.time() < end:
        now = {p for p in DOWNLOADS.glob("*.mp4")}
        new = now - before
        if new:
            f = max(new, key=lambda p: p.stat().st_mtime)
            if not list(DOWNLOADS.glob(f"{f.stem}*.crdownload")):
                a = f.stat().st_size
                time.sleep(1.5)
                if f.stat().st_size == a and a > 0:
                    return f
        time.sleep(2.0)
    return None


def probe(path: Path) -> dict:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
         "stream=width,height", "-show_entries", "format=duration",
         "-of", "json", str(path)], capture_output=True, text=True).stdout
    d = json.loads(out or "{}")
    s = (d.get("streams") or [{}])[0]
    return {"w": s.get("width"), "h": s.get("height"),
            "dur": float((d.get("format") or {}).get("duration") or 0)}


UserBusy = fk.UserBusy


def back_to_grid(b, project_url: str) -> None:
    fk.back_to_grid(b, project_url)


def known_prompts(source: str, slugs: list[str]) -> dict[str, str]:
    """{brief: prompt}, from a folder of .txt files, a prompts.json, or (the
    PYQ track's layout) each slug's projects/<slug>/veo/prompts.json."""
    out = {}
    if source:
        src = Path(source)
        if src.is_dir():
            for f in sorted(src.glob("*.txt")):
                out[f.stem] = f.read_text(encoding="utf-8").strip()
        elif src.is_file():
            for i, r in enumerate(json.loads(src.read_text(encoding="utf-8")), 1):
                out[r.get("brief") or f"s{i:02d}"] = r["prompt"]
    for slug in slugs:
        f = ROOT / "projects" / slug / "veo" / "prompts.json"
        if f.is_file():
            recs = json.loads(f.read_text(encoding="utf-8"))
            if recs:
                out[slug] = recs[0]["prompt"]
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("slugs", nargs="*",
                    help="PYQ projects whose veo/prompts.json identify the clips")
    ap.add_argument("--prompts", default="",
                    help="folder of sNN.txt prompts, or a prompts.json list")
    ap.add_argument("--aspect", choices=("landscape", "vertical"), default="landscape",
                    help="the shape every clip must arrive in")
    ap.add_argument("--out", default="", help="where to save (default: each project's veo/)")
    ap.add_argument("--quality", default=QUALITY)
    ap.add_argument("--max", type=int, default=40, help="how many grid tiles to open at most")
    ap.add_argument("--have", default="",
                    help="comma-separated clip-key prefixes already downloaded; their "
                         "tiles are skipped without being opened, which is the whole "
                         "cost of a tile")
    ap.add_argument("--list", action="store_true", help="identify the clips and stop")
    ap.add_argument("--not-these", default="",
                    help="comma-separated clip-key prefixes already in the project; "
                         "a tile outside this set is taken as the one just made. For "
                         "prompts with no spoken line, where identify() cannot work.")
    ap.add_argument("--expect", type=int, default=0,
                    help="wait until this many clips exist before fetching")
    ap.add_argument("--wait", type=float, default=900.0,
                    help="seconds to wait for --expect")
    a = ap.parse_args()

    known = known_prompts(a.prompts, a.slugs)
    if not known:
        print("no prompts to identify clips by — give --prompts or project slugs"); return 1
    if not a.out and not a.slugs:
        print("give --out (where to save the clips)"); return 1

    try:
        b, project_url = fk.connect()
    except fk.KitError as exc:
        print(exc); return 1
    try:
        try:
            back_to_grid(b, project_url)
        except UserBusy as exc:
            print(f"stopped: {exc}"); return 2
        n = tile_count(b)
        if a.expect and n < a.expect:
            print(f"{n} of {a.expect} clip(s) ready — waiting for Flow to finish")
            end = time.time() + a.wait
            while time.time() < end and n < a.expect:
                time.sleep(20.0)
                back_to_grid(b, project_url)
                n = tile_count(b)
                print(f"   {n}/{a.expect}")
        print(f"{n} clip(s) in the project\n")

        have = {k.strip() for k in a.have.split(",") if k.strip()}
        known_new = {k.strip() for k in a.not_these.split(",") if k.strip()}
        if known_new and len(known) != 1:
            print("  --not-these needs exactly one prompt to attribute the new clip to")
            return 2
        seen, bad, got = set(), 0, 0
        for i in range(min(n, a.max)):
            # STOP WHEN THE ASK IS SATISFIED. Walking on to --max costs a page
            # navigation and a full-page read per tile for nothing.
            if not a.list and len(seen) >= len(known):
                print(f"  all {len(known)} clip(s) in hand — {n - i} tile(s) left unopened")
                break
            back_to_grid(b, project_url)
            opened = open_nth(b, i)
            if have:
                k = (_tab_state(b).get("url") or "").rsplit("/", 1)[-1][:12]
                if k in have:
                    print(f"[{i + 1}/{n}] {k}… already on disk — skipped")
                    continue
            if opened == "character":
                print(f"[{i + 1}] a Flow Character card, not a clip — skipped"); continue
            if not opened:
                print(f"[{i + 1}] could not open tile"); bad += 1; continue
            # THE PROMPT TEXT ARRIVES AFTER THE PAGE DOES. Read once and a clip
            # whose Hindi line has not rendered yet identifies as `unknown` and
            # is skipped — the clip is finished and paid for, and the run
            # reports nothing downloaded. Seen on a freshly generated clip that
            # matched perfectly when the same page was read a moment later.
            # So: re-read until the line shows up, and only then give up.
            # ONE re-read, not six. The race this guards against is a clip
            # page that has not painted its prompt yet, which resolves in about
            # a second. Six attempts at 2s each added 12s to every tile that was
            # never going to match — and when fetching b-roll, that is every
            # presenter clip in the project.
            for attempt in range(2):
                raw = _eval(b, "return document.body.innerText || '';") or ""
                page = " ".join(raw.split()).lower()
                slug = identify(page, known)
                if slug or attempt:
                    break
                time.sleep(1.2)
            url = (_tab_state(b).get("url") or "").rsplit("/", 1)[-1][:12]
            # B-ROLL HAS NO SPOKEN LINE TO IDENTIFY BY. identify() anchors on
            # the quoted Hindi, which Flow's agent keeps verbatim; a prompt with
            # no dialogue falls back to matching slices of an agent REWRITE and
            # that is too weak to trust. When the caller can say which clips were
            # already in the project, the new one is simply the tile that is not
            # among them — which is exact, not fuzzy. Only safe because the
            # build loop generates one clip at a time.
            if not slug and known_new and url and url not in known_new:
                slug = next(iter(known))
                print(f"   - not in the project before this run -> {slug}")
            print(f"[{i + 1}/{n}] {slug or 'unknown'}  ({url}…)")
            if not slug:
                print("   - not one of these prompts, skipping"); continue
            if slug in seen:
                print("   - already fetched"); continue
            seen.add(slug)
            if a.list:
                continue
            out = Path(a.out) if a.out else (ROOT / "projects" / slug / "veo")
            out.mkdir(parents=True, exist_ok=True)
            dest = out / (f"{slug}.mp4" if a.prompts else f"{slug}_raw.mp4")
            if dest.exists():
                print(f"   - {dest.name} already on disk, skipping"); continue
            before = {x for x in DOWNLOADS.glob("*.mp4")}
            if not download_current(b, a.quality):
                print(f"   ! no {a.quality} option in the menu"); bad += 1; continue
            f = wait_for_file(before)
            if not f:
                print("   ! nothing arrived in Downloads"); bad += 1; continue
            shutil.move(str(f), dest)
            sent = sent_prompt(raw)
            if sent:
                dest.with_suffix(".sent.txt").write_text(sent + "\n", encoding="utf-8")
                # The agent has been seen ADDING a "Negative: subtitles,
                # captions, watermark, logo" block of its own — the exact words
                # the prompts are written to keep out.
                if re.search(r"\bnegative\s*:", sent, re.I):
                    print("   ! Flow's agent added a NEGATIVE block to this one — "
                          "check the clip for drawn text or marks")
                if spoken(known[slug]) and not all(
                        l in _norm(sent) for l in spoken(known[slug])):
                    print("   ! the spoken line did not survive the agent's rewrite")
            pr = probe(dest)
            note = ""
            if pr["w"] and pr["h"]:
                got_shape = "vertical" if pr["h"] > pr["w"] else "landscape"
                if got_shape != a.aspect:
                    note = (f"  ** {got_shape.upper()} — Flow's output setting is not "
                            f"{a.aspect}; regenerate **"); bad += 1
            shown = dest.relative_to(ROOT) if dest.is_relative_to(ROOT) else dest
            print(f"   {shown}  {pr['w']}x{pr['h']}  "
                  f"{pr['dur']:.2f}s{note}")
            got += 1
        print(f"\n{got} downloaded, {bad} problem(s)")
        return 1 if bad else 0
    except UserBusy as exc:
        print(f"stopped: {exc}"); return 2
    finally:
        b.stop()


if __name__ == "__main__":
    raise SystemExit(main())
