"""Write a part's edit list from its scene list and the video's look.

    python3 tools/reel/edit_from_scenes.py <slug> [part ...]
        work/<slug>/scenes_part<N>.json + work/<slug>/look.json + work/<slug>/inputs.json
        -> work/<slug>/edit_part<N>.json   (what tools/reel/build_part.py assembles)

PROCESS_ARTS.md section 6 owes this: scenes are DATA, and the edit list is
derived from them instead of being typed. On GEO-C2-LA-01 the three edit lists
were written by hand from the scene plans, and every change to a cut had to be
made twice.

What it knows how to lay out is the "page with a picture frame" arrangement:
the page itself is the `under` layer (opaque paper with a hole), so the
background track only has to put each Veo shot INSIDE the frame rectangle
(`look.window`) and plain paper everywhere else. A shot is printed in one ink:
grey -> a ramp from the ink to the paper colour.

scenes_part<N>.json, per scene:
    t0, t1, presenter: "you" | "explain" | "small" | "hidden"  (look.place[...])
    shots: [{clip: "V3", ink: "blue", t0, t1, start: 0.2, band_y?: 370, window?: "board"}]
    "window" names one of look["windows"] (a rect) for that shot instead of look["window"].
    ink "colour" = the clip unprinted, in its own colours; shot to shot it CUTS, because
    the page's own window closes over the cut (an iris drawn in the under layer), unless the
    shot names its own "xf" (and "transition", default slideleft). "blur" (px) and "dim" (0..1)
    put a clip behind drawn material; "saturation" overrides the look's.
    Any other ink is a one-ink print; it takes "blur" too, and "light": the look colour the
    ramp runs to (default "paper"). "pin": [x, y, w, h] puts the clip sharp and in colour in
    that rectangle over its own toned copy (GEO-C3-SA-01's blueprint).
A shot that is longer than its clip HOLDS on its last frame (never slowed,
never reversed). `band_y` picks which 4:3 band of the 9:16 clip is printed.
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FRAME = 0.034          # a cut between segments the page covers anyway


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def window(look, shot):
    """The rectangle a shot fills: look["window"], or one of look["windows"] named by the shot's
    "window" (GEO-C4-SA-01: "board" above the presenter, "full" behind him)."""
    if shot.get("window"):
        return look["windows"][shot["window"]]
    return look["window"]


def printed(look, shot, clip_wh=(720, 1280)):
    """The filter chain that prints a clip in one ink inside the picture frame."""
    w = window(look, shot)
    pr = look.get("print", {})
    cw = int(pr.get("band_w", clip_wh[0]))      # band_w/band_x: crop inside the clip's width too (keeps Veo's corner mark out)
    bx = int(pr.get("band_x", (clip_wh[0] - cw) // 2))
    bh = int(pr.get("band_h", round(cw * w["h"] / w["w"])))
    by = int(shot.get("band_y", pr.get("band_y", (clip_wh[1] - bh) // 2)))
    if shot["ink"] == "colour":
        # the clip as it was shot, only a touch of contrast so it sits in the page's light;
        # whatever shape the window has (POL-C3-LA-05: a round disc) is cut by the under layer
        # "blur": px and "dim": 0..1 put a clip BEHIND drawn material (POL-C3-LA-05 full-bleed look)
        # dim scales the light (an additive brightness cut turns a blurred clip to black blobs)
        soft = (f",gblur=sigma={shot['blur'] * 0.6:.1f}" if shot.get("blur") else "")
        k = 1 - shot.get("dim", 0)
        return (f"crop={cw}:{bh}:{bx}:{by},scale={w['w']}:{w['h']}:flags=lanczos{soft},"
                f"eq=contrast={pr.get('contrast', 1.04)}:saturation={shot.get('saturation', pr.get('saturation', 1.03))},"
                f"colorchannelmixer=rr={k:.3f}:gg={k:.3f}:bb={k:.3f},format=rgb24,"
                f"pad=1080:1920:{w['x']}:{w['y']}:color=0x{look['paper'].lstrip('#')}")
    tone = toned(look, shot)
    if shot.get("pin"):
        # GEO-C3-SA-01 (blueprint): the clip sharp and in colour inside a rectangle, over its own
        # blurred, toned copy filling the frame. The frame round the rectangle is drawn by the overlay.
        # Labels are unique per shot: this chain sits inside build_part.py's one filter graph.
        x, y, pw, ph = shot["pin"]
        full = clip_wh[0]
        cw_, ch_ = (full, round(full * ph / pw)) if full * ph / pw <= clip_wh[1] else (round(clip_wh[1] * pw / ph), clip_wh[1])
        cy = int(shot.get("pin_y", (clip_wh[1] - ch_) // 2))
        global _PIN
        _PIN += 1
        a, b, bg, fg = (f"pn{_PIN}{k}" for k in "abgf")
        return (f"split[{a}][{b}];[{a}]{tone}[{bg}];"
                f"[{b}]crop={cw_}:{ch_}:{(full - cw_) // 2}:{cy},scale={pw}:{ph}:flags=lanczos,"
                f"eq=contrast={pr.get('contrast', 1.04)}:saturation={shot.get('saturation', pr.get('saturation', 1.03))},format=rgb24[{fg}];"
                f"[{bg}][{fg}]overlay={x}:{y}")
    return tone


_PIN = 0


def toned(look, shot, clip_wh=(720, 1280)):
    """The clip printed in one ink: grey -> a ramp from look[ink] to look[light or "paper"].
    "blur" (px) softens it first, for a toned clip BEHIND drawn material (GEO-C3-SA-01)."""
    w = window(look, shot)
    pr = look.get("print", {})
    cw = int(pr.get("band_w", clip_wh[0]))
    bx = int(pr.get("band_x", (clip_wh[0] - cw) // 2))
    bh = int(pr.get("band_h", round(cw * w["h"] / w["w"])))
    by = int(shot.get("band_y", pr.get("band_y", (clip_wh[1] - bh) // 2)))
    ink, paper = rgb(look[shot["ink"]]), rgb(look[shot.get("light", "paper")])
    ramp = ":".join(f"{ch}='{i}+val*{(p - i) / 255:.4f}'" for ch, i, p in zip("rgb", ink, paper))
    soft = f",gblur=sigma={shot['blur'] * 0.6:.1f}" if shot.get("blur") else ""
    return (f"crop={cw}:{bh}:{bx}:{by},scale={w['w']}:{w['h']}:flags=lanczos{soft},format=gray,"
            f"eq=contrast={pr.get('contrast', 1.35)}:brightness={pr.get('brightness', 0.02)},format=rgb24,"
            f"lutrgb={ramp},pad=1080:1920:{w['x']}:{w['y']}:color=0x{look['paper'].lstrip('#')}")


def paper_clip(work, look):
    out = work / "out" / "paper.mp4"
    if not out.exists():
        out.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i",
                        f"color=c=0x{look['paper'].lstrip('#')}:s=1080x1920:r=30:d=2",
                        "-c:v", "libx264", "-crf", "12", "-pix_fmt", "yuv420p", str(out)], check=True)
    return "out/paper.mp4"


def build(slug, n):
    work = ROOT / "work" / slug
    look = json.loads((work / "look.json").read_text(encoding="utf-8"))
    spec = json.loads((work / f"scenes_part{n}.json").read_text(encoding="utf-8"))
    inputs = json.loads((work / "inputs.json").read_text(encoding="utf-8"))
    part = next(p for p in inputs["parts"] if p["part"] == n)
    dur = float(part["clip"]["duration"])
    paper = paper_clip(work, look)

    # every shot, in order; paper fills the time between them
    shots = sorted((dict(sh, scene=s["id"]) for s in spec["scenes"] for sh in s.get("shots", [])), key=lambda x: x["t0"])
    segs, t = [], 0.0

    def blank(a, b):
        if b - a > 1e-6:
            if segs and segs[-1]["src"] == paper:
                segs[-1]["t1"] = b
            else:
                segs.append({"id": f"paper@{a:.2f}", "t0": a, "t1": b, "src": paper, "crop": "null", "hold": True, "xf": FRAME})

    for i, sh in enumerate(shots):
        blank(t, sh["t0"])
        follows = bool(segs) and segs[-1]["src"] != paper and abs(segs[-1]["t1"] - sh["t0"]) < 1e-6 \
            and (sh["ink"] != "colour" or "xf" in sh)
        segs.append({"id": f"{sh['scene']}:{sh['clip']}", "t0": sh["t0"], "t1": sh["t1"],
                     "src": f"assets/veo/{sh['clip']}.mp4", "start": float(sh.get("start", 0.2)),
                     "crop": printed(look, sh), "push": sh.get("push", 0), "hold": True,
                     # shot to shot inside one scene: the new print slides in; otherwise the page's
                     # own shutter does the reveal and the track just cuts underneath it
                     "xf": sh.get("xf", 0.35) if follows else FRAME,
                     **({"transition": sh.get("transition", "slideleft")} if follows else {})})
        t = sh["t1"]
    blank(t, dur)
    segs[0]["t0"] = 0.0
    segs[-1]["t1"] = dur

    place = []
    for s in spec["scenes"]:
        if s["presenter"] == "hidden":
            place.append({"t0": s["t0"], "t1": s["t1"], "hidden": True})
        else:
            p = look["place"][s["presenter"]]
            place.append({"t0": s["t0"], "t1": s["t1"], "s": p["s"], "x0": p["x0"], "y0": p["y0"], "state": s["presenter"]})

    L = f"out/layers/p{n}"
    edit = {"part": n, "dur": dur, "_from": f"tools/reel/edit_from_scenes.py from scenes_part{n}.json + look.json",
            "heygen": part["clip"]["path"], "key": f"out/key_part{n}.json", "pcrop": look["pcrop"],
            "layers": {"under": f"{L}/under.mov", "mask": f"{L}/mask.mov", "overlay": f"{L}/overlay.mov", "captions": f"{L}/captions.mov"},
            "audio": f"out/audio/p{n}.wav", "bg_preset": "veryfast",
            **({"fps": look["fps"]} if look.get("fps") else {}),
            "segments": segs, "place": place}
    if look.get("cutout"):
        edit["cutout"] = look["cutout"]
    if (work / "out/layers/grain.png").exists():
        edit["grain"] = "out/layers/grain.png"
    out = work / f"edit_part{n}.json"
    out.write_text(json.dumps(edit, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"part {n}: {len(segs)} segments ({sum(1 for s in segs if s['src'] != paper)} printed shots), "
          f"{len(place)} placements -> {out.relative_to(ROOT)}")


if __name__ == "__main__":
    slug = sys.argv[1]
    for n in ([int(a) for a in sys.argv[2:]] or [1, 2, 3]):
        build(slug, n)
