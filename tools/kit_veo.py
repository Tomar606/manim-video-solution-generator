"""A kit reel's Veo clips, from prompt to cleaned, checked file.

    python tools/kit_veo.py go     <slug> [slug ...]   # setup + submit + watch: the usual way, started as soon
                                                       # as the prompts exist, left running while the plan is built
    python tools/kit_veo.py watch  <slug> [slug ...]   # fetch, clean and check until every clip is in
    python tools/kit_veo.py setup                      # set Flow to Video, Veo 3.1 Fast, 9:16, 1 output
    python tools/kit_veo.py submit <slug> [clip ...]   # queue the prompts that have no clip yet
    python tools/kit_veo.py fetch  <slug>              # download what was queued, file it by clip id
    python tools/kit_veo.py clean  <slug>              # remove Flow's sparkle into veo/clean/

WATCH. Every ~75 s: fetch whatever has finished, clean it, and run tools/veo_check.py on it. A clip that
fails a mechanical check (split screen, text on screen, landscape, cut short) is set aside (one frame kept
in veo/rejected/ as the record) and queued again, at most twice; then it is left for a person and the
reason printed. Everything is logged in veo/qc.json. What a clip MEANS is still judged by eye on
veo/contact.jpg: the watcher only removes what a machine can measure. Several reels can be watched by one
watcher (never run two: they would share the bridge's port).

The prompts are projects/<slug>/veo/prompts/broll/<clip>.txt, written by the pipeline (never by hand),
one 8-second vertical clip each. Needs Chrome open on a Flow project with this repo's extension
(flow/extension, "PYQ Flow Bridge") loaded. `setup` puts Flow's prompt bar in the right mode: it was
found on Nano Banana (an IMAGE model) at 16:9 with two outputs, which would have spent credits on
pictures. Veo 3.1 Fast is the model: real Veo at a moderate cost per clip.

WHICH TILE IS WHICH CLIP. Flow's new grid hides the prompt text, so a downloaded tile cannot be matched
to its prompt by reading it. `submit` records what it queued, when, and in which Flow project, in
veo/submitted.json. Flow's grid is newest first and holds every generation in that Flow project, from
EVERY reel queued there (two reels generated side by side share one grid), so `fetch` rebuilds the grid
order from all reels' records, merged by time, and files only this reel's tiles. 27 Oct 2026: counting one
reel's records alone filed CHE-C1-SA-02's saline drip as CHE-C1-SA-01's distillery. `fetch` also writes
veo/contact.jpg, a labelled frame from every filed clip, for the frames review to confirm before use.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
MARK = (570, 1132, 62, 60)      # Flow's sparkle on a 720x1280 clip (src/veo_delogo finds nothing at this size)


def veo(slug: str) -> Path:
    return ROOT / "projects" / slug / "veo"


def probe(f: Path) -> tuple[int, int, float]:
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                          "-show_entries", "format=duration", "-of", "json", str(f)], capture_output=True, text=True).stdout
    d = json.loads(out)
    return d["streams"][0]["width"], d["streams"][0]["height"], float(d["format"]["duration"])


def grid_order(flow: str) -> list[tuple[str, str, bool]]:
    """Every (reel, clip, rejected) ever queued in this Flow project, newest first: the order of Flow's grid.
    `rejected` marks a generation the watcher threw out, so it is never downloaded again. Records from before
    the Flow project was recorded count as this one; with no project known, every record counts."""
    rows = []
    for log in (ROOT / "projects").glob("*/veo/submitted.json"):
        for r in json.loads(log.read_text(encoding="utf-8")):
            if not flow or r.get("flow") in (flow, None, ""):
                rows += [(r["at"], k, log.parents[1].name, c, c in r.get("rejected", [])) for k, c in enumerate(r["clips"])]
    return [(slug, c, rj) for _, _, slug, c, rj in sorted(rows, reverse=True)]


def submit(slug: str, only: list[str]) -> int:
    V = veo(slug)
    prompts = sorted((V / "prompts/broll").glob("*.txt"))
    todo = [p for p in prompts if (not only or p.stem in only) and not (V / "clips" / f"{p.stem}.mp4").exists()]
    if not todo:
        print("every prompt already has a clip")
        return 0
    print(f"queueing {len(todo)}: {' '.join(p.stem for p in todo)}")
    proc = subprocess.Popen([PY, "-u", str(ROOT / "veo_kit/submit.py"), *map(str, todo), "--aspect", "vertical", "--no-refs"],
                            cwd=ROOT, stdout=subprocess.PIPE, text=True, encoding="utf-8", errors="replace",
                            env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    flow = ""
    for line in proc.stdout:                           # echo it, and keep the Flow project it queued in
        print(line, end="")
        if line.startswith("flow project: "):
            flow = line.split(": ", 1)[1].strip()
    if proc.wait() != 0:
        return proc.returncode
    log = V / "submitted.json"
    rec = json.loads(log.read_text(encoding="utf-8")) if log.exists() else []
    rec.append({"at": time.strftime("%Y-%m-%d %H:%M:%S"), "flow": flow, "clips": [p.stem for p in todo], "fetched": False})
    log.write_text(json.dumps(rec, indent=1), encoding="utf-8")
    print(f"queued; Flow takes a few minutes per clip. Then: python tools/kit_veo.py fetch {slug}")
    return 0


def fetch(slug: str) -> int:
    filed, waiting, bad = _fetch(slug)
    return 1 if bad or waiting else 0


def _fetch(slug: str) -> tuple[list[str], list[str], list[str]]:
    """Download this reel's finished tiles: (filed, still generating, problems)."""
    V = veo(slug)
    log = V / "submitted.json"
    rec = json.loads(log.read_text(encoding="utf-8")) if log.exists() else []
    # Flow's grid is newest first and holds EVERY generation in the Flow project, filed or not and from every
    # reel, so tile i is the i-th newest submission of all of them. A clip queued twice (resubmitted after it
    # stuck or was rejected) is taken from its LAST submission, the newer generation; a generation the watcher
    # rejected is never taken again.
    flow = next((r["flow"] for r in reversed(rec) if r.get("flow")), "")
    want, seen = {}, set()                             # grid position -> clip, for this reel's clips not filed yet
    for i, (s_, clip, rejected) in enumerate(grid_order(flow)):
        if s_ != slug or clip in seen:
            continue
        seen.add(clip)
        if not rejected and not (V / "clips" / f"{clip}.mp4").exists():
            want[i] = clip
    if not want:
        print("nothing waiting to be fetched")
        return [], [], []
    tmp = V / "_tiles"
    tmp.mkdir(parents=True, exist_ok=True)
    for f in tmp.glob("*.mp4"):
        f.unlink()
    # grab_tiles names each file by its GRID POSITION (a missing t03 = tile 3 not ready), so a stuck tile
    # never shifts the clips after it onto the wrong prompt; and only the positions still needed are fetched
    for i in sorted(want):
        subprocess.run([PY, str(ROOT / "veo_kit/grab_tiles.py"), str(tmp), "--skip", str(i), "--n", "1"], cwd=ROOT,
                       stdout=subprocess.DEVNULL)
    (V / "clips").mkdir(exist_ok=True)
    bad, filed, waiting = [], [], []
    for i, clip in sorted(want.items()):
        tile = tmp / f"t{i:02d}.mp4"
        if not tile.exists():
            waiting.append(clip)
            continue
        if tile.read_bytes()[:64].lstrip().lower().startswith((b"<!doctype html", b"<html")):
            tile.unlink()                              # Flow answered with a page, not a video: the session lapsed
            print(f"  {clip}: Flow sent a Google sign-in page instead of the video. Sign in to Flow in the browser "
                  "(the account that owns the project), then fetch again.")
            waiting.append(clip)
            continue
        w, h, d = probe(tile)
        if w >= h:
            bad.append(f"{clip}: {w}x{h} is landscape (set Flow to Portrait 9:16 and resubmit it)")
        shutil.move(str(tile), str(V / "clips" / f"{clip}.mp4"))
        filed.append(clip)
        print(f"  {clip}: {w}x{h}, {d:.1f} s (tile {i})")
    for r_ in rec:
        r_["fetched"] = all((V / "clips" / f"{c}.mp4").exists() or c in r_.get("rejected", []) for c in r_["clips"])
    log.write_text(json.dumps(rec, indent=1), encoding="utf-8")
    if filed:
        contact(slug)
    for b_ in bad:
        print("  !", b_)
    print(f"filed {len(filed)} clip(s)" + (f"; still generating: {' '.join(waiting)}" if waiting else "")
          + ("; check veo/contact.jpg, then: clean" if filed else ""))
    return filed, waiting, bad


def contact(slug: str) -> Path:
    V = veo(slug)
    clips = sorted((V / "clips").glob("*.mp4"))
    shots = json.loads((V / "shots.json").read_text(encoding="utf-8")) if (V / "shots.json").exists() else {}
    cw, ch, cols = 240, 427, 6
    rows = (len(clips) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * cw, rows * (ch + 70)), (20, 20, 20))
    d = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 17)
    except OSError:
        font = ImageFont.load_default()
    for i, c in enumerate(clips):
        raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", "3", "-i", str(c), "-frames:v", "1", "-vf", f"scale={cw}:{ch}",
                              "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
        x, y = (i % cols) * cw, (i // cols) * (ch + 70)
        if len(raw) == cw * ch * 3:
            sheet.paste(Image.fromarray(np.frombuffer(raw, np.uint8).reshape(ch, cw, 3)), (x, y))
        d.text((x + 6, y + ch + 4), c.stem, fill=(255, 210, 120), font=font)
        d.text((x + 6, y + ch + 26), shots.get(c.stem, "")[:30], fill=(220, 220, 220), font=font)
        d.text((x + 6, y + ch + 46), shots.get(c.stem, "")[30:60], fill=(220, 220, 220), font=font)
    out = V / "contact.jpg"
    sheet.save(out, quality=85)
    return out


def letterbox(clip: Path) -> tuple[int, int] | None:
    """Black bars that stay put through the whole clip (a dark frame or two is shadow, not a bar)."""
    w, h, d = probe(clip)
    seen = []
    for t in (d * 0.15, d * 0.5, d * 0.85):
        raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.2f}", "-i", str(clip), "-frames:v", "1",
                              "-f", "rawvideo", "-pix_fmt", "gray", "-"], capture_output=True).stdout
        rows = np.frombuffer(raw, np.uint8).reshape(h, w).mean(1)
        top = next((i for i, v in enumerate(rows) if v > 18), 0)
        bot = next((i for i, v in enumerate(rows[::-1]) if v > 18), 0)
        seen.append((top, bot))
    top, bot = min(t for t, _ in seen), min(b for _, b in seen)
    return (top + 2, bot + 2) if top > 40 and bot > 40 else None


def clean(slug: str) -> int:
    from src.veo_delogo import delogo
    V = veo(slug)
    (V / "clean").mkdir(exist_ok=True)
    n = 0
    for c in sorted((V / "clips").glob("*.mp4")):
        out = V / "clean" / c.name
        if out.exists() and out.stat().st_mtime >= c.stat().st_mtime:
            continue
        w, h, _ = probe(c)
        if (w, h) != (720, 1280):
            print(f"  ! {c.stem}: {w}x{h}, the sparkle box is measured on 720x1280; check the cleaned clip by eye")
        delogo(c, out, MARK)
        bars = letterbox(out)
        if bars:                        # Veo sometimes letterboxes a vertical clip: crop the bars, keep 9:16
            top, bot = bars; hh = h - top - bot; ww = hh * w // h
            tmp = out.with_suffix(".crop.mp4")
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(out), "-vf",
                            f"crop={ww}:{hh}:{(w - ww) // 2}:{top},scale={w}:{h}:flags=lanczos",
                            "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-an", str(tmp)], check=True)
            tmp.replace(out)
            print(f"  {c.stem}: cropped letterbox bars ({top}px top, {bot}px bottom)")
        n += 1
        print(f"  cleaned {c.stem}")
    print(f"{n} clip(s) cleaned into veo/clean/")
    return 0


def reject(slug: str, clip: str, why: list[str]) -> int:
    """Set a failed clip aside: one frame kept as the record, the files removed, the generation marked so it
    is never fetched again. Returns how many times this clip has now been rejected."""
    V = veo(slug)
    qc = json.loads((V / "qc.json").read_text(encoding="utf-8")) if (V / "qc.json").exists() else {}
    n = 1 + sum(1 for e in qc.get(clip, []) if e["verdict"] == "rejected")
    (V / "rejected").mkdir(exist_ok=True)
    src = V / "clean" / f"{clip}.mp4"
    if not src.exists():
        src = V / "clips" / f"{clip}.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "4", "-i", str(src), "-frames:v", "1", "-vf", "scale=360:-2",
                    str(V / "rejected" / f"{clip}-{n}.jpg")])
    for d in ("clips", "clean"):
        (V / d / f"{clip}.mp4").unlink(missing_ok=True)
    log = V / "submitted.json"
    rec = json.loads(log.read_text(encoding="utf-8"))
    last = next(r for r in reversed(rec) if clip in r["clips"])
    last.setdefault("rejected", []).append(clip)
    log.write_text(json.dumps(rec, indent=1), encoding="utf-8")
    note(slug, clip, "rejected", why)
    return n


def note(slug: str, clip: str, verdict: str, why: list[str]) -> None:
    f = veo(slug) / "qc.json"
    qc = json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}
    qc.setdefault(clip, []).append({"at": time.strftime("%Y-%m-%d %H:%M:%S"), "verdict": verdict, "why": why})
    f.write_text(json.dumps(qc, ensure_ascii=False, indent=1), encoding="utf-8")


def watch(slugs: list[str], every: float = 75.0, limit_min: float = 60.0, retries: int = 2) -> int:
    """Fetch, clean and check every reel's clips until each prompt has an accepted clip (or a person must look)."""
    import veo_check
    if not veo_check.text_check_available():
        print("  (text check off: RapidOCR not installed; pip install -r requirements-tools.txt)")
    t_end, gave_up = time.time() + limit_min * 60, set()
    while True:
        waiting = []
        for slug in slugs:
            V = veo(slug)
            filed, _, _ = _fetch(slug)
            if filed:
                clean(slug)
            for clip in filed:
                why = veo_check.check(V / "clean" / f"{clip}.mp4")
                if not why:
                    note(slug, clip, "ok", [])
                    print(f"  {slug} {clip}: passed the checks")
                    continue
                n = reject(slug, clip, why)
                print(f"  {slug} {clip}: REJECTED ({'; '.join(why)})")
                if n <= retries:
                    print(f"  {slug} {clip}: generating it again ({n} of {retries})")
                    submit(slug, [clip])
                else:
                    gave_up.add((slug, clip))
                    print(f"  {slug} {clip}: rejected {n} times; left for a person (rewrite its prompt)")
            for p in sorted((V / "prompts/broll").glob("*.txt")):
                if not (V / "clean" / f"{p.stem}.mp4").exists() and (slug, p.stem) not in gave_up:
                    waiting.append(f"{slug}/{p.stem}")
        if not waiting:
            for slug in slugs:
                if any((veo(slug) / "clips").glob("*.mp4")):
                    contact(slug)
            print("every clip is in" + (f"; {len(gave_up)} left for a person: "
                                         + " ".join(f"{s}/{c}" for s, c in sorted(gave_up)) if gave_up else "")
                  + ". Check veo/contact.jpg for what the machine cannot judge.")
            return 1 if gave_up else 0
        if time.time() > t_end:
            print(f"stopped after {limit_min:.0f} min; still generating: {' '.join(waiting)} (run watch again)")
            return 1
        print(time.strftime("%H:%M:%S"), f"waiting for {len(waiting)}: {' '.join(waiting)}", flush=True)
        time.sleep(every)


def go(slugs: list[str]) -> int:
    """The usual way: set Flow up, queue every reel's prompts, then watch them all in."""
    if setup() != 0:
        return 1
    for slug in slugs:
        if submit(slug, []) != 0:
            return 1
    return watch(slugs)


SETUP_MODE = ["videocam Video", "crop_9_16 9:16", "x1"]
SETUP_MODEL = "Veo 3.1 - Fast"


def setup() -> int:
    sys.path.insert(0, str(ROOT / "veo_kit"))
    import flowkit as fk
    b, proj = fk.connect()
    ev = lambda js: b.call("eval", expr=js, timeout=20)["value"]
    vis = "const vis = e => { const r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0; };"
    fire = "['pointerdown','mousedown','pointerup','mouseup','click'].forEach(k=>r.dispatchEvent(new MouseEvent(k,{bubbles:true,cancelable:true,view:window})));"
    def click(sel: str, text: str, exact: bool = True) -> str:
        match = f"(e.innerText||'').replace(/\\s+/g,' ').trim() === {json.dumps(text)}" if exact else f"(e.innerText||'').includes({json.dumps(text)})"
        return ev(vis + f"const r = [...document.querySelectorAll({json.dumps(sel)})].filter(vis).find(e => {match}); "
                  f"if (!r) return 'missing'; " + fire + " return 'ok';")
    try:
        if click('[aria-label="Settings trigger"]', "", exact=False) == "missing":
            print("no settings control on the prompt bar: is the Flow tab on a project grid?")
            return 1
        time.sleep(1.2)
        for want in SETUP_MODE:
            if click("[role=radio]", want) == "missing":
                print(f"Flow's settings have no '{want.split(' ', 1)[-1]}' option: Flow's panel changed, set it by hand")
                return 1
            time.sleep(0.8)
        click("button,[role=combobox],[role=button]", "arrow_drop_down", exact=False)       # the model menu
        time.sleep(1.2)
        if click("[role=option],[role=menuitem],[role=menuitemradio],li,[role=radio]", SETUP_MODEL, exact=False) == "missing":
            print(f"no '{SETUP_MODEL}' in Flow's model menu: choose a Veo model by hand")
            return 1
        time.sleep(1.0)
        ev("document.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true})); return 1;")
        time.sleep(0.8)
        now = ev(vis + "const t=[...document.querySelectorAll('[aria-label=\"Settings trigger\"]')].filter(vis)[0]; "
                 "return t ? (t.innerText||'').replace(/\\s+/g,' ').trim() : '';")
        print(f"Flow: {now}  (model {SETUP_MODEL})")
        return 0 if "crop_9_16" in now and "x1" in now and "Video" in now else 1
    finally:
        b.stop()


def main() -> int:
    if len(sys.argv) >= 2 and sys.argv[1] == "setup":
        return setup()
    if len(sys.argv) < 3 or sys.argv[1] not in ("go", "watch", "submit", "fetch", "clean"):
        sys.exit(__doc__)
    cmd, slug, rest = sys.argv[1], sys.argv[2], sys.argv[3:]
    if cmd in ("go", "watch"):
        try:
            return (go if cmd == "go" else watch)(sys.argv[2:])
        except KeyboardInterrupt:
            print("\nstopped; run watch again to carry on")
            return 1
    return {"submit": lambda: submit(slug, rest), "fetch": lambda: fetch(slug), "clean": lambda: clean(slug)}[cmd]()


if __name__ == "__main__":
    sys.exit(main())
