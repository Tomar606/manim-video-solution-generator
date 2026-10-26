"""A kit reel's Veo clips, from prompt to cleaned file, in three steps.

    python tools/kit_veo.py setup                      # set Flow to Video, Veo 3.1 Fast, 9:16, 1 output
    python tools/kit_veo.py submit <slug> [clip ...]   # queue the prompts that have no clip yet
    python tools/kit_veo.py fetch  <slug>              # download what was queued, file it by clip id
    python tools/kit_veo.py clean  <slug>              # remove Flow's sparkle into veo/clean/

The prompts are projects/<slug>/veo/prompts/broll/<clip>.txt, written by the pipeline (never by hand),
one 8-second vertical clip each. Needs Chrome open on a Flow project with this repo's extension
(flow/extension, "PYQ Flow Bridge") loaded. `setup` puts Flow's prompt bar in the right mode: it was
found on Nano Banana (an IMAGE model) at 16:9 with two outputs, which would have spent credits on
pictures. Veo 3.1 Fast is the model: real Veo at a moderate cost per clip.

WHICH TILE IS WHICH CLIP. Flow's new grid hides the prompt text, so a downloaded tile cannot be matched
to its prompt by reading it. `submit` records the order it queued in veo/submitted.json; Flow lists
newest first, so `fetch` takes the newest N tiles and files them in reverse submission order. That only
holds if nobody else queued in the same project in between, so `fetch` also writes veo/contact.jpg, a
labelled frame from every filed clip, for the frames review to confirm before the clips are used.
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable
sys.path.insert(0, str(ROOT))
MARK = (570, 1132, 62, 60)      # Flow's sparkle on a 720x1280 clip (src/veo_delogo finds nothing at this size)


def veo(slug: str) -> Path:
    return ROOT / "projects" / slug / "veo"


def probe(f: Path) -> tuple[int, int, float]:
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                          "-show_entries", "format=duration", "-of", "json", str(f)], capture_output=True, text=True).stdout
    d = json.loads(out)
    return d["streams"][0]["width"], d["streams"][0]["height"], float(d["format"]["duration"])


def submit(slug: str, only: list[str]) -> int:
    V = veo(slug)
    prompts = sorted((V / "prompts/broll").glob("*.txt"))
    todo = [p for p in prompts if (not only or p.stem in only) and not (V / "clips" / f"{p.stem}.mp4").exists()]
    if not todo:
        print("every prompt already has a clip")
        return 0
    print(f"queueing {len(todo)}: {' '.join(p.stem for p in todo)}")
    r = subprocess.run([PY, str(ROOT / "veo_kit/submit.py"), *map(str, todo), "--aspect", "vertical", "--no-refs"], cwd=ROOT)
    if r.returncode != 0:
        return r.returncode
    log = V / "submitted.json"
    rec = json.loads(log.read_text()) if log.exists() else []
    rec.append({"at": time.strftime("%Y-%m-%d %H:%M:%S"), "clips": [p.stem for p in todo], "fetched": False})
    log.write_text(json.dumps(rec, indent=1))
    print(f"queued; Flow takes a few minutes per clip. Then: python tools/kit_veo.py fetch {slug}")
    return 0


def fetch(slug: str) -> int:
    V = veo(slug)
    log = V / "submitted.json"
    rec = json.loads(log.read_text()) if log.exists() else []
    pending = [c for r in rec if not r["fetched"] for c in r["clips"] if not (V / "clips" / f"{c}.mp4").exists()]
    if not pending:
        print("nothing waiting to be fetched")
        return 0
    tmp = V / "_tiles"
    tmp.mkdir(parents=True, exist_ok=True)
    for f in tmp.glob("*.mp4"):
        f.unlink()
    r = subprocess.run([PY, str(ROOT / "veo_kit/grab_tiles.py"), str(tmp), "--n", str(len(pending))], cwd=ROOT)
    tiles = sorted(tmp.glob("t*.mp4"))
    if r.returncode != 0 or len(tiles) < len(pending):
        print(f"got {len(tiles)} of {len(pending)} tiles: some are still generating; run fetch again in a few minutes")
        return 1
    (V / "clips").mkdir(exist_ok=True)
    bad = []
    for tile, clip in zip(tiles, reversed(pending)):           # newest tile = last submitted
        w, h, d = probe(tile)
        if w >= h:
            bad.append(f"{clip}: {w}x{h} is landscape (set Flow to Portrait 9:16 and resubmit it)")
        tile.rename(V / "clips" / f"{clip}.mp4")
        print(f"  {clip}: {w}x{h}, {d:.1f} s")
    for r_ in rec:
        r_["fetched"] = r_["fetched"] or all((V / "clips" / f"{c}.mp4").exists() for c in r_["clips"])
    log.write_text(json.dumps(rec, indent=1))
    contact(slug)
    for b in bad:
        print("  !", b)
    print(f"filed {len(pending)} clip(s); check veo/contact.jpg shows each clip under its own label, then: clean")
    return 1 if bad else 0


def contact(slug: str) -> Path:
    V = veo(slug)
    clips = sorted((V / "clips").glob("*.mp4"))
    shots = json.loads((V / "shots.json").read_text()) if (V / "shots.json").exists() else {}
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
    if len(sys.argv) < 3 or sys.argv[1] not in ("submit", "fetch", "clean"):
        sys.exit(__doc__)
    cmd, slug, rest = sys.argv[1], sys.argv[2], sys.argv[3:]
    return {"submit": lambda: submit(slug, rest), "fetch": lambda: fetch(slug), "clean": lambda: clean(slug)}[cmd]()


if __name__ == "__main__":
    sys.exit(main())
