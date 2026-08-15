"""Repair a wrong word on a generated handwritten page, instead of re-rolling it.

    python tools/fix_text.py projects/<slug>/assets/answer
    python tools/fix_text.py path/to/Answer.png          # a single page

Then open http://127.0.0.1:8790, drag a box over the wrong word, type the right
one, and click. The box is filled with the paper's own colour, the ruled lines
that ran through it are redrawn, and the correct text is written on top in
Kalam. Edits land in a `fix_work/` copy; the original is never touched.

WHY THIS EXISTS
---------------
The image model copies the typeset temp, and its copy is imperfect in a way
that is specific to Devanagari: it drops the halant that binds a conjunct
(`अपघट्यों` -> `अपघटयों`), loses the anusvara on a plural (`हैं` -> `है`), and
occasionally swaps a consonant outright (`इलेक्ट्रोड` -> `इलेब्ट्रोड`). Those
are one-word defects on an otherwise good page, and re-generating trades them
for a different set — five rolls of one card produced four different wrong
words and never the same one twice. Fixing the word costs nothing and is the
only approach that converges.

ON SHAPING
----------
The replacement text is drawn by Pillow, which is correct here ONLY because
libraqm is installed — without it Pillow lays out Devanagari in storage order
and the repair is as garbled as what it replaced. Startup refuses to run rather
than write a bad fix over a bad word. (The original of this tool drove a
headless Chromium purely to get shaping; that is 150MB of browser to do what
libraqm now does in-process. See the Pillow note in CLAUDE.md.)

ON THE RULED LINES
------------------
Filling the box with paper colour erases whatever rules crossed it, and a gap in
the ruling is more obvious than the misspelling was. They are found by probing a
column just outside the box — where the paper is unwritten, so a dark run there
is a rule and nothing else — and redrawn at the same rows in the same colour.
"""
from __future__ import annotations

import base64
import http.server
import io
import json
import shutil
import socketserver
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONT = ROOT / "assets" / "fonts" / "Kalam-Regular.ttf"
PORT = 8790

# Sampled off the generated pages: the ink is a dark navy ballpoint, and the
# alternatives are what a marked answer actually uses.
COLOURS = {"blue": "#1b2450", "darkblue": "#0d1a55",
           "red": "#b02a37", "black": "#1a1a1a"}

PAPER_MIN = 222      # a pixel this bright inside the box is unwritten paper
RULE_DROP = 22       # a probe pixel this far below paper is a ruled line
RULE_GAP = 3         # probe rows further apart than this are separate rules


def _check_shaping() -> None:
    from PIL import features
    if not features.check("raqm"):
        raise SystemExit(
            "❌ Pillow has no libraqm, so it cannot shape Devanagari — a fix "
            "written now would be as garbled as the word it replaces.\n"
            "   brew install libraqm\n"
            "   pip install pybind11 && pip install --force-reinstall "
            "--no-binary Pillow --no-build-isolation pillow")


def render_text(text: str, px: int, colour: str) -> Image.Image:
    """The correct word, shaped, on transparency."""
    font = ImageFont.truetype(str(FONT), px)
    probe = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    x0, y0, x1, y1 = probe.textbbox((0, 0), text, font=font)
    pad = max(4, px // 8)
    img = Image.new("RGBA", (x1 - x0 + pad * 2, y1 - y0 + pad * 2), (0, 0, 0, 0))
    ImageDraw.Draw(img).text((pad - x0, pad - y0), text, font=font,
                             fill=COLOURS.get(colour, colour))
    return img


def ink_metrics(mask: np.ndarray) -> tuple[int, int, int] | None:
    """(shirorekha row, ink bottom, ink left) of a word, from its ink mask.

    Devanagari hangs from a headline, and that headline is the one row of a word
    that is almost solid — far more reliable than a Latin-style baseline, which
    Devanagari does not really have. Anchoring a replacement to it puts the new
    word on the same rail as its neighbours; matching headline-to-bottom depth
    sizes it to the same hand. Doing this by eye is what the nudge fields were
    for, and now they are mostly unnecessary.
    """
    rows = mask.sum(axis=1)
    if not rows.any():
        return None
    # the headline is the heaviest row in the upper half of the box
    head = int(np.argmax(rows[: max(1, len(rows) // 2)]))

    # A box drawn by hand almost always clips the line below — its headline is
    # the heaviest row in the whole box and would be read as this word's floor,
    # sizing the replacement half again too big. Walk out from the headline and
    # stop at the first clear gap: that is where this word actually ends.
    faint = max(1, mask.shape[1] // 50)
    gap, top, bottom = 3, 0, len(rows) - 1
    run = 0
    for y in range(head, len(rows)):
        run = run + 1 if rows[y] <= faint else 0
        if run >= gap:
            bottom = y - gap
            break
    run = 0
    for y in range(head, -1, -1):
        run = run + 1 if rows[y] <= faint else 0
        if run >= gap:
            top = y + gap
            break
    band = mask[top:bottom + 1]
    cols = np.nonzero(band.sum(axis=0))[0]
    if not len(cols) or bottom <= head:
        return None
    return head, int(bottom), int(cols[0])


def word_mask(region: np.ndarray, paper: float) -> np.ndarray:
    """Ink inside the box, with any ruled line that crosses it removed.

    A rule runs the full width of the box and the handwriting does not, so the
    rows a rule occupies are the rows that are almost entirely dark. Leaving
    them in would drag the measured headline onto the rule.
    """
    grey = region.astype(int).mean(axis=2)
    mask = grey < paper - RULE_DROP
    wide = mask.sum(axis=1) > mask.shape[1] * 0.9
    mask[wide] = False
    return mask


def find_rules(arr: np.ndarray, x: int, y0: int, y1: int, paper: float) -> list[int]:
    """Rows within [y0,y1) where a ruled line crosses, probed at column x."""
    col = arr[y0:y1, x].astype(int).mean(axis=1)
    dark = [i for i, v in enumerate(col) if v < paper - RULE_DROP]
    if not dark:
        return []
    runs, start, prev = [], dark[0], dark[0]
    for i in dark[1:]:
        if i - prev > RULE_GAP:
            runs.append((start + prev) // 2)
            start = i
        prev = i
    runs.append((start + prev) // 2)
    return runs


def apply_fix(page: Path, box, text: str, colour: str, size: int,
              dy: int, dx: int) -> None:
    img = Image.open(page).convert("RGB")
    arr = np.array(img)
    h, w = arr.shape[:2]
    x0, y0, x1, y1 = (int(v) for v in box)
    x0, y0 = max(0, x0), max(0, y0)
    x1, y1 = min(w, x1), min(h, y1)
    if x1 <= x0 or y1 <= y0:
        return

    region = arr[y0:y1, x0:x1].reshape(-1, 3)
    bright = region[region.min(axis=1) > PAPER_MIN]
    paper = (bright.mean(axis=0) if len(bright) > 20
             else np.array([252.0, 252.0, 252.0])).astype(np.uint8)

    # probe OUTSIDE the box: inside it the rules are interrupted by the very
    # word being removed, which is what made them hard to find in the first place
    probe_x = x0 - 10 if x0 >= 10 else min(w - 1, x1 + 10)
    rules = find_rules(arr, probe_x, y0, y1, float(paper.mean()))

    # measure the word BEFORE erasing it — it is the only guide to how big the
    # replacement should be and where it should sit
    target = ink_metrics(word_mask(arr[y0:y1, x0:x1], float(paper.mean())))

    arr[y0:y1, x0:x1] = paper
    for ry in rules:
        arr[max(y0, y0 + ry - 1):y0 + ry + 1, x0:x1] = arr[y0 + ry, probe_x]
    img = Image.fromarray(arr)

    if text.strip():
        px, glyphs, fitted = _match_hand(text.strip(), colour, size, target)
        if fitted:
            shiro, _, left = fitted
            t_shiro, _, t_left = target
            pos = (x0 + t_left - left + int(dx), y0 + t_shiro - shiro + int(dy))
        else:                       # nothing measurable — fall back to the box
            baseline = y0 + rules[-1] if rules else y1 - 4
            pos = (x0 + 4 + int(dx),
                   baseline - glyphs.height + int(glyphs.height * 0.16) + int(dy))
        img.paste(glyphs, pos, glyphs)
    img.save(page)


def _match_hand(text: str, colour: str, size: int, target):
    """Render `text` at the size that matches the word being replaced.

    Returns (px, image, metrics-or-None). With an explicit size, or when the box
    held nothing measurable, this is a single render at the requested size.
    """
    def measure(im):
        return ink_metrics(np.asarray(im)[:, :, 3] > 40)

    if size and size > 0:
        img = render_text(text, int(size), colour)
        return int(size), img, measure(img)
    if target is None:
        return 0, render_text(text, 32, colour), None

    t_shiro, t_bottom, _ = target
    probe_px = 64
    probe = render_text(text, probe_px, colour)
    m = measure(probe)
    if m is None or m[1] - m[0] < 2 or t_bottom - t_shiro < 2:
        return probe_px, probe, m
    px = max(8, round(probe_px * (t_bottom - t_shiro) / (m[1] - m[0])))
    img = render_text(text, px, colour)
    return px, img, measure(img)


# --------------------------------------------------------------------------- UI

PAGE_HTML = """<!doctype html><html><head><meta charset=utf-8>
<title>Fix handwritten text</title><style>
 body{font-family:-apple-system,Segoe UI,Roboto,sans-serif;margin:0;background:#0f1420;color:#e8ecf3;display:flex}
 #side{width:320px;padding:16px;background:#161d2e;height:100vh;overflow:auto;box-sizing:border-box}
 #main{flex:1;padding:16px;overflow:auto;height:100vh;box-sizing:border-box}
 h1{font-size:16px;margin:0 0 12px}
 label{display:block;font-size:12px;color:#9fb0c8;margin:10px 0 3px}
 select,input,button,textarea{width:100%;box-sizing:border-box;padding:8px;border-radius:7px;
   border:1px solid #2c3852;background:#0f1626;color:#e8ecf3;font-size:14px}
 textarea{font-size:20px;min-height:52px}
 .row{display:flex;gap:8px} .row>*{flex:1}
 button{background:#2f6bff;border:none;cursor:pointer;font-weight:600;margin-top:12px}
 button.sec{background:#33415e}
 canvas{border:1px solid #2c3852;max-width:100%;cursor:crosshair;background:#fff}
 .hint{font-size:12px;color:#8092ad;line-height:1.5}
</style></head><body>
<div id=side>
 <h1>Fix handwritten text</h1>
 <label>Page</label><select id=code></select>
 <label>Correct text</label><textarea id=text placeholder="e.g. इलेक्ट्रोड"></textarea>
 <div class=row><div><label>Ink</label><select id=color>
   <option value=blue>blue</option><option value=darkblue>dark blue</option>
   <option value=red>red</option><option value=black>black</option></select></div>
   <div><label>Size (0=auto)</label><input id=size type=number value=0></div></div>
 <div class=row><div><label>Nudge &#8597;</label><input id=dy type=number value=0></div>
   <div><label>Nudge &#8596;</label><input id=dx type=number value=0></div></div>
 <button id=apply>Hide &amp; write on selection</button>
 <button id=reset class=sec>Reset this page</button>
 <p class=hint>Drag a box over the wrong word, type the right one, click.
 Repeat per fix. Edits save to <b>fix_work/</b>; originals are untouched.</p>
</div>
<div id=main><div class=hint id=status>drag to select&hellip;</div><canvas id=cv></canvas></div>
<script>
let CODES=%CODES%;
let cv=document.getElementById('cv'),ctx=cv.getContext('2d'),img=new Image(),scale=1,box=null,drag=null;
let sel=document.getElementById('code');
CODES.forEach(c=>{let o=document.createElement('option');o.value=o.text=c;sel.add(o)});
function load(){img.onload=()=>{let dw=Math.min(760,img.naturalWidth);scale=img.naturalWidth/dw;
  cv.width=dw;cv.height=img.naturalHeight/scale;draw();};
  img.src='/img?code='+encodeURIComponent(sel.value)+'&t='+Date.now();box=null;}
function draw(){ctx.drawImage(img,0,0,cv.width,cv.height);if(box){ctx.strokeStyle='#ff3b6b';
  ctx.lineWidth=2;ctx.strokeRect(box.x,box.y,box.w,box.h);
  ctx.fillStyle='rgba(255,59,107,.12)';ctx.fillRect(box.x,box.y,box.w,box.h);}}
cv.onmousedown=e=>{let r=cv.getBoundingClientRect();drag={x:e.clientX-r.left,y:e.clientY-r.top};};
cv.onmousemove=e=>{if(!drag)return;let r=cv.getBoundingClientRect();
  let x=e.clientX-r.left,y=e.clientY-r.top;
  box={x:Math.min(drag.x,x),y:Math.min(drag.y,y),w:Math.abs(x-drag.x),h:Math.abs(y-drag.y)};draw();};
cv.onmouseup=()=>{drag=null;if(box)document.getElementById('status').textContent=
  'box '+Math.round(box.w*scale)+'x'+Math.round(box.h*scale)+' px - type the correct text, then click';};
sel.onchange=load;
document.getElementById('apply').onclick=async()=>{if(!box){alert('draw a box first');return;}
  let b=[box.x*scale,box.y*scale,(box.x+box.w)*scale,(box.y+box.h)*scale];
  document.getElementById('status').textContent='applying...';
  await fetch('/apply',{method:'POST',body:JSON.stringify({code:sel.value,box:b,
    text:document.getElementById('text').value,color:document.getElementById('color').value,
    size:+document.getElementById('size').value,dy:+document.getElementById('dy').value,
    dx:+document.getElementById('dx').value})});
  document.getElementById('text').value='';box=null;load();
  document.getElementById('status').textContent='done - drag the next one';};
document.getElementById('reset').onclick=async()=>{
  await fetch('/reset',{method:'POST',body:JSON.stringify({code:sel.value})});load();};
load();
</script></body></html>"""


def serve(orig: Path, work: Path, pages: list[str]) -> None:
    class Handler(http.server.BaseHTTPRequestHandler):
        def _send(self, code, ctype, data):
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def log_message(self, *a):
            pass

        def do_GET(self):
            u = urlparse(self.path)
            if u.path == "/":
                html = PAGE_HTML.replace("%CODES%", json.dumps(pages))
                self._send(200, "text/html; charset=utf-8", html.encode())
            elif u.path == "/img":
                name = parse_qs(u.query).get("code", pages[:1])[0]
                if name not in pages:
                    return self._send(404, "text/plain", b"no such page")
                self._send(200, "image/png", (work / f"{name}.png").read_bytes())
            else:
                self._send(404, "text/plain", b"no")

        def do_POST(self):
            n = int(self.headers.get("Content-Length", 0))
            d = json.loads(self.rfile.read(n) or b"{}")
            name = d.get("code")
            if name not in pages:
                return self._send(400, "text/plain", b"no such page")
            if self.path == "/apply":
                apply_fix(work / f"{name}.png", d["box"], d.get("text", ""),
                          d.get("color", "blue"), d.get("size", 0),
                          d.get("dy", 0), d.get("dx", 0))
            elif self.path == "/reset":
                shutil.copy(orig / f"{name}.png", work / f"{name}.png")
            else:
                return self._send(404, "text/plain", b"no")
            self._send(200, "application/json", b'{"ok":true}')

    with socketserver.TCPServer(("127.0.0.1", PORT), Handler) as srv:
        print(f"🖊  http://127.0.0.1:{PORT}   pages: {', '.join(pages)}")
        print(f"   edits -> {work}")
        srv.serve_forever()


def main() -> int:
    _check_shaping()
    if not FONT.exists():
        raise SystemExit(f"❌ handwriting font not found: {FONT}")
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)

    target = Path(sys.argv[1]).resolve()
    if target.is_file():
        orig, names = target.parent, [target.stem]
    elif target.is_dir():
        orig = target
        names = sorted(p.stem for p in target.glob("*.png")
                       if not p.stem.endswith("_trimmed"))
    else:
        raise SystemExit(f"❌ not found: {target}")
    if not names:
        raise SystemExit(f"❌ no .png pages in {target}")

    work = orig / "fix_work"
    work.mkdir(parents=True, exist_ok=True)
    for name in names:
        if not (work / f"{name}.png").exists():
            shutil.copy(orig / f"{name}.png", work / f"{name}.png")
    serve(orig, work, names)
    return 0


if __name__ == "__main__":
    sys.exit(main())
