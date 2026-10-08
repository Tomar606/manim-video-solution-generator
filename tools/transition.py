"""Join two clips with a bought transition laid over the cut.

    python tools/transition.py <a.mp4> <b.mp4> <out.mp4> --name leak_warm_sweep
    python tools/transition.py <a.mp4> <b.mp4> <out.mp4> --name thuynguyen_1012_1790164986
    python tools/transition.py --list

The name is looked up in assets/transitions/ and the MODE follows from which
folder it is in (tools/import_transitions.py sorts them on the way in):

  overlay/  a LEAK — light leak, film burn, flare. Mostly black, so it is
            SCREENED: black screens to nothing and is its own transparency.
  wipe/     a SHAPE on chroma green — paper tear, crumple, circle. The green is
            KEYED and the shape covers the frame.

WHERE THE CUT GOES, AND WHY IT IS MEASURED
------------------------------------------
At the transition's PEAK — the brightest frame of a leak, the most-covered
frame of a wipe — never at its middle. A bought leak is not symmetrical: the
flare in filmsri_01 blows out a third of the way in and takes the rest of its
length to fall off, so cutting at the midpoint would change the picture while
the flare is already fading and leave the seam in plain sight. The peak is
measured off the file, so a pack whose timing is nothing like ours still lands
its cut in the right place.

Hiding the cut is the whole job: consecutive generated clips never match
(CLAUDE.md), so an unhidden seam between two of them reads as a mistake rather
than as an edit.

ONLY THE BRIDGE IS BLENDED — the transition's own length either side of the
cut, and not one frame more. Screening or keying across the whole reel would
put a per-pixel filter on every frame of the video for the sake of a second per
cut (memory: composite-perf).

SOUND IS NOT TRANSITIONED. The picture is bridged; the audio is concatenated
straight, because each clip here carries one spoken sentence and a crossfade
would blend the last syllable of one into the first of the next.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "assets" / "transitions"


def find(name: str):
    for mode, folder in (("screen", DEST / "overlay"), ("cover", DEST / "wipe")):
        p = folder / f"{name}.mp4"
        if p.is_file():
            return p, mode
    return None, None


def probe(p: Path) -> dict:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                          "format=duration:stream=codec_type,width,height",
                          "-of", "json", str(p)], capture_output=True, text=True).stdout
    doc = json.loads(out)
    v = next((s for s in doc["streams"] if s.get("codec_type") == "video"), {})
    return {"dur": float(doc["format"]["duration"]),
            "w": v.get("width"), "h": v.get("height"),
            "audio": any(s.get("codec_type") == "audio" for s in doc["streams"])}


def sample(p: Path, w: int = 40, h: int = 71):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(p), "-vf", f"scale={w}:{h}",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         capture_output=True).stdout
    n = len(raw) // (w * h * 3)
    if n < 3:
        return None
    return np.frombuffer(raw[:n * w * h * 3], np.uint8).reshape(n, h, w, 3).astype(np.float32)


MIN_SIDE = 0.15         # seconds of picture a bridge must get from EACH side


def peak(a, mode: str, dur: float) -> float:
    """Seconds into the transition at which it covers the picture most.

    KEPT AWAY FROM BOTH ENDS. Some bought leaks are brightest on their very
    first frame — wnebe1_..._14 peaks at 0.03s — and a cut there leaves the
    outgoing scene one frame to bridge with. The bridge then has no picture on
    one side and the join fails outright ("1080x1920 and NonexNone"), which
    reads as a broken clip rather than as a cut landing in the wrong place. The
    peak is clamped so each side always has MIN_SIDE of real picture.
    """
    if a is None:
        return dur / 2
    if mode == "screen":
        score = a.mean(axis=(1, 2, 3))                  # brightest
    else:
        lead = a[..., 1] - np.maximum(a[..., 0], a[..., 2])
        score = (lead < 25).mean(axis=(1, 2))           # least green left
    t = float(np.argmax(score)) / len(a) * dur
    if dur <= 2 * MIN_SIDE:
        return dur / 2
    return min(max(t, MIN_SIDE), dur - MIN_SIDE)


def green_of(a) -> str:
    """The wipe's OWN backing green, as 0xRRGGBB.

    Not a constant: the four wipes in the first pack back onto 0,111,5 /
    27,216,30 / 63,219,34 / 143,250,75. A single default keyed one of them and
    left the backing standing on the other three, so the colour is measured off
    whichever clip is being used. The sample is the pixels where green leads by
    a wide margin, which is the backing and never the shape on top of it.
    """
    if a is None:
        return "0x00FF00"
    lead = a[..., 1] - np.maximum(a[..., 0], a[..., 2])
    px = a.reshape(-1, 3)[lead.ravel() > 60]
    if len(px) < 50:
        return "0x00FF00"
    r, g, b = (int(v) for v in np.median(px, axis=0))
    return f"0x{r:02X}{g:02X}{b:02X}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("a", nargs="?")
    ap.add_argument("b", nargs="?")
    ap.add_argument("out", nargs="?")
    ap.add_argument("--name", default="leak_warm_sweep")
    ap.add_argument("--list", action="store_true", help="what is available, by mode")
    ap.add_argument("--dur", type=float, default=0.0, help="0 = the transition's own length")
    ap.add_argument("--key", default="", help="override the wipe's measured green")
    ap.add_argument("--similarity", type=float, default=0.28)
    # A LEAK AT FULL STRENGTH IS A WASH, NOT A TRANSITION. wnebe1_..._03 peaks
    # at a mean luma of 156; screened whole it turned two seconds of picture
    # into flat pink and the shot underneath was gone rather than hidden. The
    # leak is dimmed before it is screened, so the cut is still covered at the
    # peak but the shot either side stays readable.
    ap.add_argument("--opacity", type=float, default=0.72,
                    help="how strongly a leak is screened, 0..1")
    ap.add_argument("--no-audio", action="store_true")
    # THE TWO INPUTS ARE ALREADY THE FRAGMENTS. tools/veo_reel.py cuts the
    # outgoing scene's tail and the incoming scene's head to exactly the lengths
    # this transition wants, and asks for the bridge alone. Without being told
    # that, this recomputed pre/post from the fragments it was handed —
    # d = min(transition, tail, head) — which is far shorter than the
    # transition, so the leak was squeezed into a sliver in the middle of the
    # bridge and trimmed to its first frames. On screen that is a hard cut with
    # a flicker: the exact complaint that found this.
    ap.add_argument("--bridge", action="store_true",
                    help="A and B ARE the fragments; span the transition across both")
    a = ap.parse_args()

    if a.list or not (a.a and a.b and a.out):
        for mode, folder in (("screen (leak)", DEST / "overlay"),
                             ("cover  (wipe)", DEST / "wipe")):
            names = sorted(p.stem for p in folder.glob("*.mp4"))
            print(f"  {mode}: {len(names)}")
            for n in names:
                print(f"      {n}")
        return 0 if a.list else 1

    A, B, out = Path(a.a), Path(a.b), Path(a.out)
    tr, mode = find(a.name)
    if tr is None:
        print(f"  no transition named {a.name!r} — run with --list")
        return 1
    pa, pb, pt = probe(A), probe(B), probe(tr)
    if (pa["w"], pa["h"]) != (pb["w"], pb["h"]):
        print(f"  {A.name} is {pa['w']}x{pa['h']} and {B.name} is {pb['w']}x{pb['h']} — "
              f"the bridge concatenates them, so they must match")
        return 1
    grid = sample(tr)
    key = a.key or green_of(grid)
    if a.bridge:
        pre, post = pa["dur"], pb["dur"]
        d = pre + post
    else:
        d = min(a.dur or pt["dur"], pa["dur"], pb["dur"])
        pk = peak(grid, mode, pt["dur"])
        # A gives up everything before the peak, B everything after it
        pre, post = min(pk, d, pa["dur"]), min(d - min(pk, d), pb["dur"])
        if pre < 0.03 or post < 0.03:
            pre = post = min(d, pa["dur"], pb["dur"]) / 2
    sound = not a.no_audio and pa["audio"] and pb["audio"]

    keyed = (f"[2:v]scale={pa['w']}:{pa['h']},trim=0:{pre + post:.3f},setpts=PTS-STARTPTS,"
             f"colorkey={key}:{a.similarity}:0.10[tr]")
    if mode == "screen":
        keyed = (f"[2:v]scale={pa['w']}:{pa['h']},trim=0:{pre + post:.3f},"
                 f"setpts=PTS-STARTPTS,"
                 f"colorchannelmixer=rr={a.opacity}:gg={a.opacity}:bb={a.opacity}[tr]")
    # SCREEN IN RGB, NOT IN YUV. blend works on whatever planes it is handed,
    # and handed yuv420p it screens the CHROMA planes too — U and V both rise,
    # so every leak came out the same magenta whatever colour it actually was.
    # A cream flare and a red streak were indistinguishable on the output, which
    # is what made it look like a choice of clip rather than a bug.
    join = ("[br]format=gbrp[brr];[tr]format=gbrp[trr];"
            "[brr][trr]blend=all_mode=screen:shortest=1,format=yuv420p[brl]"
            if mode == "screen" else "[br][tr]overlay=shortest=1[brl]")
    fc = [
        f"[0:v]trim=0:{pa['dur'] - pre:.3f},setpts=PTS-STARTPTS[ah]",
        f"[0:v]trim={pa['dur'] - pre:.3f}:{pa['dur']:.3f},setpts=PTS-STARTPTS[at]",
        f"[1:v]trim=0:{post:.3f},setpts=PTS-STARTPTS[bh]",
        f"[1:v]trim={post:.3f}:{pb['dur']:.3f},setpts=PTS-STARTPTS[bt]",
        "[at][bh]concat=n=2:v=1:a=0[br]",
        keyed, join,
        "[ah][brl][bt]concat=n=3:v=1:a=0[v]",
    ]
    if sound:
        fc.append("[0:a][1:a]concat=n=2:v=0:a=1[aout]")
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", str(A), "-i", str(B), "-i", str(tr),
           "-filter_complex", ";".join(fc), "-map", "[v]"]
    cmd += (["-map", "[aout]", "-c:a", "aac", "-b:a", "192k", "-ar", "48000"]
            if sound else ["-an"])
    cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", "16",
            "-pix_fmt", "yuv420p", str(out)]
    subprocess.run(cmd, check=True)
    got = probe(out)
    print(f"  {out.name}: {A.name} + {B.name} under {a.name} [{mode}] — "
          f"{pre + post:.2f}s, cut at {pre:.2f}s in"
          + (f", at {a.opacity:.2f} strength" if mode == "screen" else "")
          + (f", key {key}" if mode == "cover" else "")
          + f" -> {got['dur']:.2f}s"
          + ("" if sound else "  [silent]"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
