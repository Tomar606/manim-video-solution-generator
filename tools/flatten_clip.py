#!/usr/bin/env python3
"""Turn a green-screen generation into a panel-ready opaque clip.

    python tools/flatten_clip.py <clip_alpha.webm> <out.mp4> [--ground '#05100F']

WHY THIS EXISTS
---------------
The two tracks take a generated clip in opposite ways.

The Manim/PYQ track KEYS it: the clip arrives as an alpha webm and is composited
into a stage band, so the field is discarded at composite time and whatever the
generator drew outside the subject is discarded with it.

The edu-video track PLAYS it: `tools/composite.py` lays the clip into the panel
the renderer drew (`#veo.panel`, 1080x810 on #05100F) as an opaque rectangle,
and `src/panel_layout.geometry()` reduces it with a CENTRED CROP TO THE PANEL'S
ASPECT. That crop is pure arithmetic — it does not know where the drawing is.
Every clip bio-c5 and bio-c12 use was generated photoreal on a dark plate, so
this never came up.

BIO-C2-LA-01's three clips are green-screen cartoons built for the keyed track,
and they carry two things a centred crop will not remove:

  * SPARKLES. Flow adds them despite the standing ban list, they are not the
    field colour, so a key keeps them. Measured on P2-F6: a 780px sparkle at
    y 1136-1183 of 1280, which scaled into place lands at frame y~973 — below
    the middle line, INSIDE THE PRESENTER.
  * A "Veo" WATERMARK along the bottom of every frame.

So the clip is cropped to the DRAWING before it is flattened, and both defects
fall outside the crop by construction. That measurement is `subject_bbox`,
promoted here out of `work/bio-c2-la-01/place_clip.py` where it was written.

WHY THE BBOX IS MEASURED ON THE SETTLED TAIL
--------------------------------------------
Not over the whole clip. Parts that arrive from off-screen are still crossing
the frame edge early on, so a union over every frame IS the whole frame and
sizes the drawing to nothing. P2-F7's follicle cells fly in, and it measures:

    settle 0.35 (11 frames): 720x1280   <- the whole frame, useless
    settle 0.20 ( 6 frames): 608x614
    settle 0.12 ( 3 frames): 608x600    <- stable

Every brief ends with "each part settles and stays", so the last sixth is the
finished picture. Default 0.15.

WHY IT PADS TO 4:3 RATHER THAN SCALING TO THE PANEL
---------------------------------------------------
`panel_layout.geometry()` runs its centred crop on whatever it is handed. Hand
it a clip that is ALREADY the panel's aspect and the crop is a no-op, so the
drawing survives whole. Scaling straight to 1080x810 here instead would work
today and break silently the day PANEL_AR changes.

`-c:v libvpx-vp9` MUST precede the input. VP9 alpha lives in a separate
BlockAdditional layer the native decoder ignores — without the flag the clip
decodes fully opaque and brings the green field with it.
"""
from __future__ import annotations

import argparse
import json
import subprocess as sp
import sys
from pathlib import Path

import numpy as np
from scipy import ndimage

MIN_PART = 3000        # px; below this a component is decoration, not drawing
SAMPLE_FPS = 4
PAD = 8                # px of margin kept around the drawing
PANEL_AR = 4 / 3       # must match src.panel_layout.PANEL_AR
GROUND = "#05100F"     # must match `#veo.panel{background:...}` in style.css
FPS = 30


def alpha_frames(clip, fps=SAMPLE_FPS):
    probe = sp.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                    "-show_entries", "stream=width,height", "-of", "csv=p=0",
                    str(clip)], capture_output=True, text=True).stdout.strip()
    w, h = (int(x) for x in probe.split(",")[:2])
    raw = sp.run(["ffmpeg", "-nostdin", "-v", "error", "-c:v", "libvpx-vp9",
                  "-i", str(clip), "-vf", f"fps={fps},format=rgba,alphaextract",
                  "-f", "rawvideo", "-pix_fmt", "gray", "-"],
                 capture_output=True, stdin=sp.DEVNULL).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, h, w), w, h


def subject_bbox(clip, settle=0.15):
    """Bbox of the SETTLED drawing, decoration excluded."""
    frames, w, h = alpha_frames(clip)
    if not len(frames):
        raise SystemExit(f"{clip}: no alpha decoded — is it a VP9 alpha webm?")
    frames = frames[-max(2, int(len(frames) * settle)):]
    x0, y0, x1, y1 = w, h, 0, 0
    dropped = 0
    for f in frames:
        lab, n = ndimage.label(f > 40)
        if not n:
            continue
        sizes = ndimage.sum(f > 40, lab, range(1, n + 1))
        keep = [i + 1 for i, s in enumerate(sizes) if s >= MIN_PART]
        dropped += sum(1 for s in sizes if 30 <= s < MIN_PART)
        if not keep:
            continue
        m = np.isin(lab, keep)
        ys, xs = np.where(m)
        x0, y0 = min(x0, xs.min()), min(y0, ys.min())
        x1, y1 = max(x1, xs.max()), max(y1, ys.max())
    if x1 <= x0 or y1 <= y0:
        raise SystemExit(f"{clip}: no component >= {MIN_PART}px in the settled "
                         f"tail — nothing to crop to")
    x0, y0 = max(0, x0 - PAD), max(0, y0 - PAD)
    x1, y1 = min(w - 1, x1 + PAD), min(h - 1, y1 + PAD)
    return dict(x=int(x0), y=int(y0), w=int(x1 - x0 + 1), h=int(y1 - y0 + 1),
                src_w=w, src_h=h, frames=len(frames), decoration_dropped=dropped)


def flatten(clip: Path, out: Path, ground: str = GROUND, settle: float = 0.15,
            raw: Path | None = None, field: str | None = None):
    """Crop to the drawing and lay it on the panel ground.

    THE PIXELS COME FROM THE RAW GENERATION, NOT THE KEYED WEBM.
    ------------------------------------------------------------
    The delivered `_alpha.webm` has a despill baked in, and on these clips it
    did not stay on the edges - it took the green out of the SUBJECT. Measured
    on P2-F7 at t=7s, the cytoplasm reads

        raw   (154, 228, 246)   cyan, as drawn
        webm  (156, 162, 247)   periwinkle

    a 66-level drop in green across the whole cell body, while the magenta
    nucleus is untouched (158,116,203 -> 161,117,205). A cell drawn cyan should
    not ship purple, so when the raw generation is available the alpha webm is
    used ONLY to measure where the drawing is, and the picture is keyed here
    from the raw against its own sampled field colour. Cyan sits far enough
    from green in hue that a modest similarity leaves the subject alone.
    """
    b = subject_bbox(clip, settle)
    cw, ch = b["w"] // 2 * 2, b["h"] // 2 * 2

    # Pad the cropped drawing out to 4:3, centred, on the panel ground. The
    # drawing keeps its own scale; only the surround grows.
    if cw / ch > PANEL_AR:
        pw, ph = cw, int(round(cw / PANEL_AR)) // 2 * 2
    else:
        pw, ph = int(round(ch * PANEL_AR)) // 2 * 2, ch

    vf = (f"crop={cw}:{ch}:{b['x']}:{b['y']},"
          f"pad={pw}:{ph}:(ow-iw)/2:(oh-ih)/2:color={ground}@1.0,"
          f"fps={FPS},format=yuv420p")

    out.parent.mkdir(parents=True, exist_ok=True)
    if raw:
        # Key the raw generation against its own sampled field, then flatten.
        # `chromakey` works in YUV on hue+chroma distance, so a cyan subject is
        # far from a green field and survives; `similarity` is deliberately
        # modest and `blend` softens only the boundary.
        key = (f"chromakey={field or '0x00DA00'}:similarity=0.16:blend=0.04,"
               f"despill=type=green:mix=0.35:expand=0")
        cmd = ["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", str(raw),
               "-filter_complex",
               f"color=c={ground}:s={b['src_w']}x{b['src_h']}:r={FPS}[bg];"
               f"[0:v]fps={FPS},format=rgba,{key}[fg];"
               f"[bg][fg]overlay=0:0:format=auto:shortest=1,{vf}[v]",
               "-map", "[v]", "-an",
               "-c:v", "libx264", "-crf", "17", "-preset", "medium",
               "-pix_fmt", "yuv420p", str(out)]
        sp.run(cmd, check=True, stdin=sp.DEVNULL)
        b.update(out=str(out), crop_w=cw, crop_h=ch, panel_w=pw, panel_h=ph,
                 ground=ground, settle=settle, source="raw+chromakey",
                 field=field)
        return b
    cmd = ["ffmpeg", "-nostdin", "-v", "error", "-y",
           "-c:v", "libvpx-vp9", "-i", str(clip),
           "-filter_complex",
           # The clip's own alpha over a solid ground: what the panel shows.
           #
           # `shortest=1` is load-bearing. `color` is an INFINITE source, and
           # overlay's default eof_action repeats the last frame of the clip
           # forever against it, so without this the encode never ends: an 8s
           # generation was 56MB and still growing after twelve minutes.
           f"color=c={ground}:s={b['src_w']}x{b['src_h']}:r={FPS}[bg];"
           f"[0:v]fps={FPS},format=rgba[fg];"
           f"[bg][fg]overlay=0:0:format=auto:shortest=1,{vf}[v]",
           "-map", "[v]", "-an",
           "-c:v", "libx264", "-crf", "17", "-preset", "medium",
           "-pix_fmt", "yuv420p", str(out)]
    sp.run(cmd, check=True, stdin=sp.DEVNULL)

    b.update(out=str(out), crop_w=cw, crop_h=ch, panel_w=pw, panel_h=ph,
             ground=ground, settle=settle)
    return b


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("clip")
    ap.add_argument("out")
    ap.add_argument("--ground", default=GROUND)
    ap.add_argument("--settle", type=float, default=0.15)
    ap.add_argument("--raw", help="the raw generation; its pixels are used and "
                                  "the webm supplies only the bbox")
    ap.add_argument("--field", help="sampled field colour, e.g. 0x00DA00")
    a = ap.parse_args(argv)
    b = flatten(Path(a.clip), Path(a.out), a.ground, a.settle,
                Path(a.raw) if a.raw else None, a.field)
    print(f"  {Path(a.clip).name}")
    print(f"    drawing   {b['w']}x{b['h']} at ({b['x']},{b['y']}) "
          f"of {b['src_w']}x{b['src_h']}  [{b['frames']} settled frames]")
    print(f"    decoration dropped: {b['decoration_dropped']} component(s)")
    print(f"    -> {b['out']}  {b['panel_w']}x{b['panel_h']} (4:3, opaque)")
    print(json.dumps(b))
    return 0


if __name__ == "__main__":
    sys.exit(main())
