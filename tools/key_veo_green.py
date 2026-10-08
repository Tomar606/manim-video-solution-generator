"""Key a Veo "green screen" clip onto a background, and put his colour back.

    python tools/key_veo_green.py <clip.mp4> <background.png> <out.mp4>
        [--width 505] [--frame 1080x1920] [--thresh 25] [--soft 20]
        [--despill 0.92] [--warm 1.0]

WHY NOT chromakey / colorkey
----------------------------
Because Veo does not paint a chroma green. Asked for "a flat, evenly lit chroma
green wall" it renders a PALE, desaturated one — measured on POL-C1-LA-01 s01 at
RGB 124,194,141, luma 167. Both of ffmpeg's keyers measure DISTANCE to a colour,
and at that saturation the wall is no further from his skin and his black polo
than they are from each other. Swept across their whole range, every setting
either left the wall standing or ate holes through his face and hands; there is
no value in between, because the thing being asked for does not exist in the
picture.

WHAT DOES SEPARATE IT
---------------------
Not distance — DOMINANCE. On the same frame:

    wall      G - max(R,B) = +53 .. +57
    black polo             =  -7
    skin                   = -27

A wall that is barely green is still the only thing in the picture where green
LEADS the other two channels, and it leads them by sixty levels. So the matte is
built from `G - max(R, B)`, which is flat across the wall's uneven lighting
(both samples above are within four levels despite a 4-level luma difference)
and is the wrong sign everywhere else.

AND THEN HIS COLOUR GOES BACK
-----------------------------
A green wall bounces green onto whoever stands in front of it, so the despill is
not optional tidying — without it his navy polo reads green-grey and his skin
reads sallow. Green is pulled back to whatever the other two channels are doing
wherever it leads them, which is a no-op on every pixel that was never lit by
the wall, and `--warm` then lifts red slightly to undo what the bounce took out
of his skin.
"""
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def probe(p: Path) -> dict:
    g = lambda q: subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                                  "-show_entries", q, "-of", "csv=p=0", str(p)],
                                 capture_output=True, text=True).stdout.strip()
    w, h = (int(v) for v in g("stream=width,height").split(",")[:2])
    has_a = bool(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a:0",
                                 "-show_entries", "stream=codec_type", "-of", "csv=p=0",
                                 str(p)], capture_output=True, text=True).stdout.strip())
    fps = g("stream=r_frame_rate") or "30/1"
    n, d = (float(x) for x in fps.split("/"))
    return {"w": w, "h": h, "fps": n / max(d, 1), "audio": has_a}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("clip")
    ap.add_argument("background")
    ap.add_argument("out")
    ap.add_argument("--frame", default="1080x1920")
    ap.add_argument("--width", type=int, default=505,
                    help="how wide he stands in the finished frame, px")
    ap.add_argument("--bottom", type=int, default=0, help="px above the frame's foot")
    # HEAD AND SHOULDERS, NOT HEAD TO WAIST. A vertical Veo clip is framed with
    # his head near the top, so scaling the whole clip to the presenter's width
    # makes him 898px tall on a 1920 frame — nearly half of it. The delivered
    # videos crop their presenter to roughly a square: head and shoulders at the
    # foot of the frame, leaving the card and its years pill a clear field
    # above. Without this the pill lands across his face.
    ap.add_argument("--tall", type=float, default=1.10,
                    help="his height as a multiple of his width; 0 keeps the whole clip")
    ap.add_argument("--thresh", type=float, default=25.0,
                    help="green lead (G - max(R,B)) at which a pixel starts to go")
    ap.add_argument("--soft", type=float, default=20.0, help="levels of edge softness")
    ap.add_argument("--despill", type=float, default=0.92)
    ap.add_argument("--warm", type=float, default=1.0,
                    help="red lift on what is left, to undo the wall's bounce")
    a = ap.parse_args()

    clip, out = Path(a.clip), Path(a.out)
    FW, FH = (int(v) for v in a.frame.lower().split("x"))
    info = probe(clip)
    sw, sh = info["w"], info["h"]
    pw = a.width
    ph = max(1, round(sh * pw / sw))
    px, py = (FW - pw) // 2, FH - ph - a.bottom
    crop_h = int(pw * a.tall) if a.tall > 0 else 0

    bg = Image.open(a.background).convert("RGB")
    if bg.size != (FW, FH):
        s = max(FW / bg.width, FH / bg.height)
        bg = bg.resize((round(bg.width * s), round(bg.height * s)), Image.LANCZOS)
        bg = bg.crop(((bg.width - FW) // 2, (bg.height - FH) // 2,
                      (bg.width - FW) // 2 + FW, (bg.height - FH) // 2 + FH))
    base = np.asarray(bg).astype(np.float32)

    rd = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(clip), "-f", "rawvideo",
                           "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    enc = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{FW}x{FH}", "-r", f"{info['fps']:.5f}", "-i", "-"]
    if info["audio"]:
        enc += ["-i", str(clip), "-map", "0:v", "-map", "1:a",
                "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest"]
    else:
        enc += ["-an"]
    enc += ["-c:v", "libx264", "-preset", "medium", "-crf", "16",
            "-pix_fmt", "yuv420p", str(out)]
    wr = subprocess.Popen(enc, stdin=subprocess.PIPE)

    n_bytes = sw * sh * 3
    frames = 0
    covered = []
    while True:
        buf = rd.stdout.read(n_bytes)
        if len(buf) < n_bytes:
            break
        f = np.frombuffer(buf, np.uint8).reshape(sh, sw, 3).astype(np.float32)
        R, G, B = f[..., 0], f[..., 1].copy(), f[..., 2]
        lead = G - np.maximum(R, B)
        alpha = np.clip((a.thresh - lead) / max(a.soft, 1e-3), 0.0, 1.0)
        # green goes back to whatever the other two are doing, wherever it leads
        G -= np.maximum(lead, 0.0) * a.despill
        sub = np.stack([np.clip(R * a.warm, 0, 255), G, B], -1)
        rgba = Image.fromarray(sub.astype(np.uint8))
        rgba.putalpha(Image.fromarray((alpha * 255).astype(np.uint8)))
        small = rgba.resize((pw, ph), Image.LANCZOS)
        if crop_h and crop_h < small.height:
            bb = small.getbbox()                 # where he actually starts
            top = bb[1] if bb else 0
            small = small.crop((0, top, small.width, min(small.height, top + crop_h)))
        canvas = Image.fromarray(base.astype(np.uint8))
        canvas.paste(small, (px, FH - small.height - a.bottom), small)
        wr.stdin.write(np.asarray(canvas).tobytes())
        covered.append(float((alpha > 0.9).mean()))
        frames += 1
    wr.stdin.close()
    rd.stdout.close()
    wr.wait()
    rd.wait()
    if not frames:
        print(f"  no frames read from {clip}")
        return 1
    shown_h = min(crop_h, ph) if crop_h else ph
    print(f"  {out.name}: {frames} frames, he is {pw}x{shown_h} at the foot of "
          f"{FW}x{FH}; solid subject {100 * float(np.mean(covered)):.0f}% of the "
          f"source frame")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
