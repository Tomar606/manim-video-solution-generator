"""Download the newest clips in the open Flow project straight from the grid.

    python veo_kit/grab_tiles.py <out_dir> [--n 12] [--skip 0]

Flow moved to flow.google.com (Oct 2026) with a new grid: each clip is a
<flow-video-tile> whose <video> already carries a signed flow-content.google URL
for the full 720x1280 file.  fetch.py's click-through (open tile, menu, download)
finds no tiles there, so this reads the URLs and downloads them directly.

Tiles are newest first.  Files are written t00.mp4, t01.mp4 ... in grid order;
which prompt each one answers is decided by looking at them (the new account
hides the prompt text), so build a contact sheet before filing them.
"""
from __future__ import annotations

import argparse
import json
import time
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import flowkit as fk  # noqa: E402

# A tile shows only a thumbnail until it is hovered; hovering mounts its <video>. So hover each
# of the newest N in turn, wait for the element, and read its source (newest first).
JS = """return (async () => {
const N = %d, tiles = [...document.querySelectorAll('flow-video-tile')].slice(0, N), out = [];
const sleep = ms => new Promise(r => setTimeout(r, ms));
for (const t of tiles) {
  const c = t.querySelector('.container') || t;
  for (const ev of ['pointerover', 'pointerenter', 'mouseover', 'mouseenter', 'mousemove'])
    c.dispatchEvent(new MouseEvent(ev, { bubbles: true, cancelable: true, view: window }));
  let v = null;
  for (let k = 0; k < 30 && !(v && (v.currentSrc || v.src)); k++) { await sleep(150); v = t.querySelector('video'); }
  out.push(v ? (v.currentSrc || v.src) : null);
  for (const ev of ['pointerout', 'pointerleave', 'mouseout', 'mouseleave'])
    c.dispatchEvent(new MouseEvent(ev, { bubbles: true, cancelable: true, view: window }));
}
return JSON.stringify(out);
})();
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("out_dir", type=Path)
    ap.add_argument("--n", type=int, default=12, help="how many of the newest tiles")
    ap.add_argument("--skip", type=int, default=0, help="skip this many newest tiles first")
    a = ap.parse_args()
    a.out_dir.mkdir(parents=True, exist_ok=True)
    b, _ = fk.connect()
    try:
        srcs = json.loads(b.call("eval", expr=JS % (a.skip + a.n), timeout=120)["value"])
    finally:
        b.stop()
    print(len(srcs), "tiles in the project")
    for i in range(a.skip, min(len(srcs), a.skip + a.n)):
        if not srcs[i]:
            print(f"  t{i:02d}: no source yet (still rendering?)")
            continue
        dest = a.out_dir / f"t{i:02d}.mp4"
        if dest.exists() and dest.stat().st_size > 100_000:
            print(f"  t{i:02d}: already here")
            continue
        for attempt in range(8):                  # the CDN drops connections, sometimes SILENTLY mid-file
            try:
                with urllib.request.urlopen(srcs[i], timeout=60) as r:
                    want = int(r.headers.get("Content-Length") or 0)
                    data = r.read()
                if want and len(data) != want:
                    raise IOError(f"short read {len(data)}/{want}")
                dest.write_bytes(data)
                break
            except Exception as e:                # noqa: BLE001
                print(f"  t{i:02d}: retry after {type(e).__name__}: {e}"[:110])
                time.sleep(3)
        print(f"  t{i:02d} -> {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
