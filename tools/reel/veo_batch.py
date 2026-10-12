"""Generate a video's Veo clips through the Flow extension, from a prompts file.

    python3 tools/reel/veo_batch.py work/<slug>/assets/veo/prompts.json [V1 V2 ...]

prompts.json: {"style": "...", "negative": "...", "clips": {"V1": {"title": "...",
"prompt": "..."}}}. The shared style and negative are appended to every clip so
the batch matches. Clips land beside the prompts file as <id>.mp4, with a
manifest.json (Flow media key, full prompt, seconds). A clip already on disk is
skipped, so a run resumes. One clip in flight at a time: the clip is whichever
NEW video Flow shows.

    python3 tools/reel/veo_batch.py <prompts.json> --parallel 3 [V1 V2 ...]

submits the clips in WAVES of that many, back to back in the one tab, and
collects a wave when all of its tiles have landed (Flow renders them at the same
time, so three clips take about as long as one). A wave is refused until at
least one clip of this prompts file is already on disk: the first clip of any
batch runs alone and is looked at, because a defect in the shared style line
is paid for once per clip. Clips are matched to prompts by their place in the
grid (newest first), which is right unless a generation fails part-way, so every
collected clip is recorded with "matched_by": "grid order" and must be LOOKED
AT before it is used.

The browser half is flow-animator's extension (build 10). Read Flow's settings
back (9:16, confirm Never, a Veo model) before the first run: see
flow-animator/src/flowanim/preflight.py. Generalised from
docs/history-poc/flow_batch.py, which read its prompts out of a plan document.
"""
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "flow-animator/src"))
from flowanim.bridge import FlowBridge, FlowError                      # noqa: E402
import flowanim.drive as drive                                         # noqa: E402
from flowanim.drive import generate, fetch, load_selectors, DriveError  # noqa: E402

INBOX = Path.home() / "Downloads/flow_inbox"

# Flow's 2026-10-07 build serves a tile's still from /asb/<opaque token>, which
# the extension's list_media (build 10) does not recognise: it returns an empty
# list on a page full of clips, and every generation would poll out its whole
# timeout. The token is stable for as long as the page is not reloaded, and the
# extension's ui_download finds a tile by any substring of its src, so the
# token serves as the media key. Used only when list_media comes back empty.
_ASB = """
  var out = [], seen = new Set();
  for (const e of document.querySelectorAll("img")) {
    var m = (e.getAttribute("src") || "").match(/\\/asb\\/([A-Za-z0-9_-]{20,})/);
    if (!m || seen.has(m[1])) continue;
    var nw = e.naturalWidth || 0, nh = e.naturalHeight || 0;
    if (Math.max(nw, nh) < 256) continue;
    // Flow's session panel (2026-10-08) repeats each result as a 32 px thumbnail from the same
    // /asb/ store, ahead of the grid in the page: it is not a tile and does not open a clip.
    if (e.getBoundingClientRect().width < 90) continue;
    seen.add(m[1]);
    // Flow names each tile from its prompt ("People holding lit oil lamps"); the name survives
    // a reload, which the /asb/ token does not
    var lab = "", p = e;
    for (var k = 0; k < 6 && p; k++) { p = p.parentElement; var t = p ? (p.getAttribute("aria-label") || "") : ""; if (t.trim().length > 8) { lab = t.trim(); break; } }
    out.push({key: m[1], kind: "image", tag: "img", w: nw, h: nh, video: true, label: lab,
              shape: nw > nh ? "landscape" : "portrait", url: e.src});
  }
  return out;
"""
_ext_media = drive._media


def _media(bridge, **kw):
    # The grid's own tiles first. On 2026-10-07 the extension's list_media returned nothing on
    # this build; on 2026-10-08 it returned the session panel's square images instead, which
    # are not clips, and every download after the first failed on them.
    grid = bridge.call("eval", expr=_ASB, timeout=60).get("value") or []
    return grid or _ext_media(bridge, **kw)


drive._media = _media
_ext_new_video = drive._new_video


def _is_asb(media):
    return bool(media) and all(len(m["key"]) > 60 for m in media)


def _new_video(bridge, before):
    """On the /asb/ build, "a key that was not there before" is not a new clip: the
    grid loads its tiles lazily, and in a project that already holds other clips an
    OLD tile that finishes loading after the snapshot looks new. That delivered
    somebody else's clip as ours in 29 s. The newest clip is the grid's FIRST tile,
    so that is the only one accepted, and only once it has held still."""
    media = _media(bridge)
    if not _is_asb(media):
        return _ext_new_video(bridge, before)
    first = media[0]["key"]
    if first in before:
        return [], []
    time.sleep(6)
    again = _media(bridge)
    return ([first], []) if again and again[0]["key"] == first else ([], [])


drive._new_video = _new_video


def to_root(bridge):
    """Each generation starts from the project page with its grid settled, never from
    a clip's edit view: a generation made there takes THAT clip's aspect ratio."""
    url = bridge.call("eval", expr="return location.href;", timeout=30)["value"]
    root = url.split("/edit/")[0].split("?")[0]
    if "/project/" not in root:
        raise DriveError(f"the Flow tab is not on a project page: {url}")
    if root != url:
        bridge.call("eval", expr=f"location.href={json.dumps(root)}; return 1;", timeout=30)
        time.sleep(6)
    last, same = -1, 0
    for _ in range(40):
        n = len(_media(bridge))
        same = same + 1 if n == last and n else 0
        if same >= 3:
            break
        last = n
        time.sleep(1.5)
    box = bridge.call("eval", expr='var p=document.querySelector(".ProseMirror");'
                      'return p?Math.round(p.getBoundingClientRect().width):0;', timeout=30)["value"]
    if not box:
        raise DriveError("the prompt box is hidden (a panel is open over it?)")


def shape(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries",
                          "stream=width,height", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True).stdout.strip()
    w, h = (int(x) for x in out.split(",")[:2])
    return w, h


class Spec:
    """The shape flowanim.drive.generate expects of a brief."""
    def __init__(self, vid, title, prompt, negative):
        self.id, self.title, self._p, self._n = vid, f"{vid} {title}", prompt, negative

    def prompt(self):
        return self._p

    def negative(self):
        return self._n


def wave(bridge, ids, clips, spec, sel, out, man, man_path):
    """Submit `ids` back to back, wait for all of them, collect by grid position."""
    to_root(bridge)
    bridge.call("attach", timeout=60)
    time.sleep(1.5)
    # What is at the top of the grid now, by LABEL. New clips are whatever sits above it later.
    # (Counting tiles does not work: the grid is a window onto the project. Comparing /asb/
    # tokens does not work either: the open page never shows a clip Flow's agent finished
    # later, so the page is reloaded while waiting, and a reload changes every token.)
    before = [m.get("label") or "" for m in _media(bridge)[:3]]
    t0 = time.time()
    for vid in ids:
        c = clips[vid]
        text = f"{c['prompt'].strip()}\n{spec['style'].strip()}"
        neg = ", ".join(x for x in (spec.get("negative", ""), c.get("negative", "")) if x)
        bridge.call("set_prompt", text=f"{text}\n\nNEGATIVE: {neg}", selector=sel["prompt"], timeout=120)
        time.sleep(1.0)
        if sel.get("generate_selector"):
            bridge.call("click", selector=sel["generate_selector"], timeout=60)
        else:
            bridge.call("click", text=sel["generate_text"], timeout=60)
        print(f"{vid}: submitted — {c['title']}", flush=True)
        man[vid] = {"title": c["title"], "prompt": text, "negative": neg, "submitted": True}
        man_path.write_text(json.dumps(man, ensure_ascii=False, indent=1))
        # Flow takes the send button away while it is taking a request in; the next prompt can
        # only go in once it is back. (If it stays away until the clip is finished, a wave is
        # simply sequential: slower, never wrong.)
        time.sleep(6)
        # ...and after the LAST one too: the wait below reloads the page, and a reload while Flow is
        # still taking a request in drops it (GEO-C4-SA-01: the last clip of two waves never existed)
        if sel.get("generate_selector"):
            probe = f"return !!document.querySelector({json.dumps(sel['generate_selector'])});"
            for _ in range(60):
                if bridge.call("eval", expr=probe, timeout=30).get("value"):
                    break
                time.sleep(3)
            else:
                raise DriveError("the send button did not come back within 3 minutes")
            print(f"        send button back after {time.time() - t0:.0f}s of this wave", flush=True)
    deadline, last, same, fresh = time.time() + drive.GENERATE_TIMEOUT, -1, 0, []
    while time.time() < deadline:
        time.sleep(25)
        try:
            bridge.call("eval", expr="location.reload(); return 1;", timeout=30)
            time.sleep(8)
            to_root(bridge)
            now = _media(bridge)[:len(ids) + 8]
            labels = [m.get("label") or "" for m in now]
            # the first place where the old top of the grid starts again
            # an empty project has no old top: everything on the grid is new (GEO-C4-SA-01: an empty
            # `before` matched at 0, so nothing was ever fresh and a landed clip waited out the timeout)
            at = len(labels) if not before else next((i for i in range(len(labels)) if labels[i:i + len(before)] == before[:len(labels) - i]), None)
            fresh = now[:at] if at is not None else []
        except Exception:                                   # noqa: BLE001
            continue
        n = len(fresh)
        same = same + 1 if n == last else 0
        last = n
        if n >= len(ids) and same >= 1:
            break
    print(f"wave: {len(fresh)} of {len(ids)} landed in {time.time() - t0:.0f}s: "
          + " | ".join(m.get("label") or "?" for m in fresh), flush=True)
    if len(fresh) != len(ids):
        print("wave: NOT collecting — a generation failed or is still queued; look at the Flow tab "
              "(Flow's agent queues clips and the last of a wave can take several minutes more)", flush=True)
        return False
    # the grid is newest first: fresh[i] is the (i+1)-th from the END of what was submitted.
    # Each is then found again by its LABEL, because collecting one reloads the page.
    for vid, tile in zip(reversed(ids), fresh):
        label, got = tile.get("label") or "", None
        for attempt in range(4):
            try:
                to_root(bridge)
                time.sleep(3)
                now = _media(bridge)[:14]
                hit = next((m for m in now if label and m.get("label") == label), None)
                if hit is None:
                    raise DriveError(f"no tile labelled {label!r} among the newest")
                got = fetch(bridge, hit["key"], f"{vid}.mp4")
                break
            except (FlowError, DriveError) as e:
                print(f"{vid}: download attempt {attempt + 1} failed ({str(e)[:80]}); trying again", flush=True)
                time.sleep(4)
        if got is None:
            print(f"{vid}: could not be downloaded; its tile is labelled {label!r}", flush=True)
            return False
        w, h = shape(got)
        dst = out / f"{vid}.mp4" if h > w else out / "rejected" / f"{vid}_landscape.mp4"
        dst.parent.mkdir(exist_ok=True)
        shutil.move(str(got), dst)
        man[vid].update(file=str(dst), size=[w, h], flow_label=label, matched_by="grid order, then label", seconds=round(time.time() - t0))
        man_path.write_text(json.dumps(man, ensure_ascii=False, indent=1))
        print(f"{vid}: collected {w}x{h} -> {dst.name}   [{label}]", flush=True)
        if w > h:
            print("LANDSCAPE clip in a portrait job — stopping", flush=True)
            return False
    return True


def main(pfile, ids, parallel=1):
    pfile = Path(pfile).resolve()
    out = pfile.parent
    spec = json.loads(pfile.read_text(encoding="utf-8"))
    clips = spec["clips"]
    ids = ids or list(clips)
    man_path = out / "manifest.json"
    man = json.loads(man_path.read_text()) if man_path.exists() else {}
    sel = load_selectors(ROOT / "flow-animator/selectors.json")
    bridge = FlowBridge(port=8765, inbox=INBOX).start()
    try:
        info = bridge.wait_for_worker(timeout=90)
        print("extension connected; tab:", info.get("tab"), flush=True)
        if parallel > 1:
            if not any((out / f"{v}.mp4").is_file() for v in clips):
                raise SystemExit("no clip of this batch is on disk yet: run the first one alone and look at it")
            todo = [v for v in ids if not (out / f"{v}.mp4").is_file()]
            for a in range(0, len(todo), parallel):
                try:
                    if not wave(bridge, todo[a:a + parallel], clips, spec, sel, out, man, man_path):
                        break
                except (FlowError, DriveError) as e:
                    print(f"wave FAILED — {e}", flush=True)
                    break
            return
        for vid in ids:
            dst = out / f"{vid}.mp4"
            if dst.is_file():
                print(f"{vid}: already on disk, skipping", flush=True)
                continue
            c = clips[vid]
            text = f"{c['prompt'].strip()}\n{spec['style'].strip()}"
            neg = ", ".join(x for x in (spec.get("negative", ""), c.get("negative", "")) if x)
            t0 = time.time()
            print(f"{vid}: generating — {c['title']}", flush=True)
            try:
                to_root(bridge)
                key = generate(bridge, Spec(vid, c["title"], text, neg), sel)
                got = fetch(bridge, key, f"{vid}.mp4")
            except (FlowError, DriveError) as e:
                print(f"{vid}: FAILED — {e}", flush=True)
                man[vid] = {"title": c["title"], "error": str(e)}
                man_path.write_text(json.dumps(man, ensure_ascii=False, indent=1))
                continue
            w, h = shape(got)
            if w > h:
                # The project setting is 9:16, but a generation made from inside a
                # landscape clip's edit view comes back landscape. Kept, never used
                # as if it were right.
                dst = out / "rejected" / f"{vid}_landscape.mp4"
                dst.parent.mkdir(exist_ok=True)
                print(f"{vid}: LANDSCAPE {w}x{h} — set aside as {dst.name}; stopping the batch", flush=True)
                shutil.move(str(got), dst)
                break
            shutil.move(str(got), dst)
            man[vid] = {"title": c["title"], "key": key, "file": str(dst),
                        "prompt": text, "negative": neg, "seconds": round(time.time() - t0)}
            man_path.write_text(json.dumps(man, ensure_ascii=False, indent=1))
            print(f"{vid}: done in {time.time() - t0:.0f}s", flush=True)
    finally:
        bridge.stop()


if __name__ == "__main__":
    par = int(sys.argv[sys.argv.index("--parallel") + 1]) if "--parallel" in sys.argv else 1
    main(sys.argv[1], [a for a in sys.argv[2:] if a.startswith("V")], par)
