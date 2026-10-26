"""The review page: every frame of a reel, its words, its sound, and the finished video, in one HTML file.

    python lab/kit_test/review_page.py <slug> [--label review]

Writes projects/<slug>/review/index.html (with frames/ and voice.m4a beside it). Open it in any browser
(Edge on Windows, Chrome, Safari) or in VS Code with the Live Preview extension. Nothing to install:
  * every still large, under its time and the caption being spoken there;
  * a play button on each that plays the narration from that moment, so sync is checked by ear;
  * a note box on each, kept in the browser, and "Copy my review", which copies every note (or
    APPROVED when there are none) to paste back to Claude;
  * the rendered video at the top once it exists (projects/<slug>/final/), to watch the final cut.

It replaces sending contact-sheet JPGs around: a Windows machine has no Preview, and a sheet cannot
play the sound or take a note.
"""
from __future__ import annotations

import html
import json
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def caption_at(lines: list[dict], t: float) -> str:
    for l in lines:
        if l["start"] - 0.05 <= t < l["end"] + 0.05:
            return l["text"]
    return ""


def main() -> int:
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    slug = sys.argv[1]
    label = sys.argv[sys.argv.index("--label") + 1] if "--label" in sys.argv else "review"
    proj = ROOT / "projects" / slug
    meta = json.loads((proj / "meta.json").read_text())
    rv = proj / "review"
    (rv / "frames").mkdir(parents=True, exist_ok=True)
    for old in (rv / "frames").glob("*.jpg"):
        old.unlink()
    parts = []
    for plan_out in sorted((HERE / "out").glob(f"plan_{slug.replace('-', '_')}_p*")):
        part = plan_out.name.rsplit("_p", 1)[1]
        stills = sorted((plan_out / label).glob("still_*.png"))
        if not stills:
            continue
        tl = json.loads((plan_out / "timeline.js").read_text().replace("window.TL = ", "").rstrip().rstrip(";"))
        lines = json.loads((proj / f"lines_part{part}.json").read_text())
        items = []
        for i, p in enumerate(stills):
            s = tl["stills"][i] if i < len(tl["stills"]) else {"t": 0}
            t = s["t"] if isinstance(s, dict) else s
            name = f"p{part}_{i:02d}.jpg"
            Image.open(p).convert("RGB").resize((540, 960), Image.LANCZOS).save(rv / "frames" / name, quality=86)
            items.append({"img": f"frames/{name}", "t": round(t, 2), "cap": caption_at(lines, t)})
        voice = rv / f"voice_part{part}.m4a"
        src = proj / f"src/part{part}.mp4"
        if src.exists() and (not voice.exists() or voice.stat().st_mtime < src.stat().st_mtime):
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-vn", "-c:a", "aac", "-b:a", "96k", str(voice)], check=True)
        final = proj / "final" / f"{slug.replace('-', '_')}_part{part}.mp4"
        parts.append({"part": part, "items": items, "voice": voice.name if voice.exists() else "",
                      "video": f"../final/{final.name}" if final.exists() else ""})
    if not parts:
        raise SystemExit(f"no review stills yet: run stills.mjs out/plan_{slug.replace('-', '_')}_p1 {label} first")
    title = html.escape(f"{meta.get('sheet_id', slug)} — {meta.get('title', '')}")
    data = json.dumps({"slug": slug, "parts": parts}, ensure_ascii=False)
    page = PAGE.replace("__TITLE__", title).replace("__QUESTION__", html.escape(meta.get("question", ""))).replace("__DATA__", data)
    (rv / "index.html").write_text(page, encoding="utf-8")
    print(rv.relative_to(ROOT) / "index.html")
    return 0


PAGE = """<!doctype html>
<html lang="hi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Review: __TITLE__</title>
<style>
  :root { --bg: #f4f1ea; --ink: #1d1b16; --muted: #6b6457; --card: #fff; --line: #ddd5c4; --accent: #b4500f; }
  @media (prefers-color-scheme: dark) { :root { --bg: #16150f; --ink: #eee8da; --muted: #a39b8b; --card: #22201a; --line: #3a362c; } }
  body { margin: 0; background: var(--bg); color: var(--ink); font: 16px/1.5 system-ui, "Segoe UI", sans-serif; }
  header { position: sticky; top: 0; z-index: 2; background: var(--bg); border-bottom: 1px solid var(--line); padding: 12px 16px; }
  h1 { font-size: 20px; margin: 0; } .q { color: var(--muted); margin: 2px 0 8px; }
  button { font: inherit; padding: 6px 14px; border-radius: 8px; border: 1px solid var(--line); background: var(--card); color: var(--ink); cursor: pointer; }
  button.main { background: var(--accent); color: #fff; border-color: var(--accent); }
  main { padding: 16px; max-width: 1200px; margin: 0 auto; }
  video { width: min(360px, 100%); border-radius: 10px; background: #000; display: block; margin: 8px 0 20px; }
  .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 16px; }
  .f { background: var(--card); border: 1px solid var(--line); border-radius: 12px; overflow: hidden; }
  .f img { width: 100%; display: block; cursor: zoom-in; }
  .f .meta { padding: 8px 10px; } .t { font-weight: 700; color: var(--accent); }
  .cap { font-size: 15px; margin: 4px 0 6px; } textarea { width: 100%; box-sizing: border-box; min-height: 44px; font: inherit; border-radius: 8px; border: 1px solid var(--line); background: var(--bg); color: var(--ink); padding: 6px; }
  .zoom { position: fixed; inset: 0; background: rgba(0,0,0,.85); display: none; place-items: center; z-index: 5; }
  .zoom img { max-height: 96vh; max-width: 96vw; } .ok { color: #2e7d32; margin-left: 8px; }
</style></head><body>
<header><h1>__TITLE__</h1><div class="q">__QUESTION__</div>
  <button class="main" id="copy">Copy my review</button><span class="ok" id="copied"></span>
  <span style="color:var(--muted);margin-left:8px">Write a note under any frame that needs a change; leave the rest empty.</span></header>
<main id="m"></main>
<div class="zoom" id="z"><img id="zi" alt=""></div>
<script>
const D = __DATA__;
const key = 'review:' + D.slug;
let notes = {}; try { notes = JSON.parse(localStorage.getItem(key) || '{}'); } catch (e) {}
const save = () => { try { localStorage.setItem(key, JSON.stringify(notes)); } catch (e) {} };
const mmss = t => Math.floor(t / 60) + ':' + (t % 60).toFixed(1).padStart(4, '0');
const m = document.getElementById('m');
for (const P of D.parts) {
  const sec = document.createElement('section');
  sec.innerHTML = `<h2>Part ${P.part}</h2>` + (P.video ? `<div>Rendered video</div><video controls preload="metadata" src="${P.video}"></video>` : '');
  const audio = new Audio(P.voice); let stop = null;
  const g = document.createElement('div'); g.className = 'grid';
  P.items.forEach((it, i) => {
    const id = P.part + ':' + i, f = document.createElement('div'); f.className = 'f';
    f.innerHTML = `<img src="${it.img}" alt="frame at ${mmss(it.t)}"><div class="meta"><span class="t">${mmss(it.t)}</span>
      <button style="float:right">&#9654; hear it</button><div class="cap">${it.cap || '<i>(no caption here)</i>'}</div>
      <textarea placeholder="what should change here?"></textarea></div>`;
    f.querySelector('img').onclick = () => { document.getElementById('zi').src = it.img; document.getElementById('z').style.display = 'grid'; };
    f.querySelector('button').onclick = () => { clearTimeout(stop); audio.currentTime = Math.max(0, it.t - 2); audio.play(); stop = setTimeout(() => audio.pause(), 6000); };
    const ta = f.querySelector('textarea'); ta.value = notes[id] || ''; ta.oninput = () => { notes[id] = ta.value; save(); };
    g.appendChild(f);
  });
  sec.appendChild(g); m.appendChild(sec);
}
document.getElementById('z').onclick = e => { e.currentTarget.style.display = 'none'; };
document.getElementById('copy').onclick = async () => {
  const out = [];
  for (const P of D.parts) P.items.forEach((it, i) => { const n = (notes[P.part + ':' + i] || '').trim(); if (n) out.push(`part ${P.part} ${mmss(it.t)}: ${n}`); });
  const text = `${D.slug} review: ` + (out.length ? '\\n' + out.join('\\n') : 'APPROVED, no changes');
  try { await navigator.clipboard.writeText(text); document.getElementById('copied').textContent = 'copied: paste it to Claude'; }
  catch (e) { prompt('Copy this and paste it to Claude:', text); }
};
</script></body></html>
"""

if __name__ == "__main__":
    sys.exit(main())
