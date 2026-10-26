"""Composite a compiled part into a finished video.

    .venv-tools/bin/python lab/kit_test/compose.py <plan.json> [--music <library path>] [--out <mp4>]

Layers, bottom to top, per frame:
  1. the plate, or the beat's Veo clip (cleaned of Flow's marker, slowed to fill
     the beat, held on its last frame if it runs out: never looped, never reversed)
  2. the presenter, keyed exactly as compile.py keys him for stills: standing, or
     masked inside the hub circle with the hub's own backdrop behind him
  3. the graphics layer from frames.mjs (panels, labels, spine, captions)
Audio: his voice, a music bed well under it, and one library sound per element
entrance with the sound's PEAK on the visual event.  Captions never trigger sound.
"""
from __future__ import annotations

import json
import itertools
import math
import subprocess
import time
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import compile as C  # noqa: E402

W, H, FPS = 1080, 1920, 30


def load_tl(out):
    s = (out / "timeline.js").read_text()
    return json.loads(s[len("window.TL = "):].rstrip().rstrip(";"))


def reader(args, w, h):
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-threads", "2"] + args + ["-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         stdout=subprocess.PIPE)
    size = w * h * 3
    last = None
    try:
        while True:
            b = p.stdout.read(size)
            if len(b) < size:
                break
            last = np.frombuffer(b, np.uint8).reshape(h, w, 3)
            yield last
        while True:                       # ran out: hold the last frame
            yield last
    finally:
        try:
            p.stdout.close()
        except Exception:
            pass
        p.terminate()
        p.wait()


def grade_full(dim):
    """The terrain-atlas footage grade: darker at the caption/masthead band and
    under the presenter, so light panels read; dimmed beats darker overall."""
    y = np.linspace(0, 1, H)[:, None, None]
    g = 1 - 0.35 * np.clip((0.18 - y) / 0.18, 0, 1) - 0.55 * np.clip((y - 0.6) / 0.4, 0, 1)
    return (g * (0.55 if dim else 1.0)).astype(np.float32)


def blend(dst, rgba, x, y):
    """Alpha-blend an RGBA image into dst (H, W, 3 float32) at (x, y), clipped."""
    h, w = rgba.shape[:2]
    x0, y0, x1, y1 = max(0, x), max(0, y), min(W, x + w), min(H, y + h)
    if x1 <= x0 or y1 <= y0:
        return
    src = rgba[y0 - y:y1 - y, x0 - x:x1 - x].astype(np.float32)
    a = src[..., 3:4] / 255.0
    dst[y0:y1, x0:x1] = dst[y0:y1, x0:x1] * (1 - a) + src[..., :3] * a


def theme_accent(theme):
    """--accent from the theme pack, as an RGB array (forest green if the theme names none).
    The presenter card was once hard-coded forest green — right for survey-light, and
    read as an unkeyed green screen on every other theme."""
    import re
    f = HERE / "themes" / f"{theme}.css"
    m = re.search(r"--accent:\s*#([0-9A-Fa-f]{6})", f.read_text()) if theme and f.exists() else None
    hx = m.group(1) if m else "1E7B4F"
    return np.array([int(hx[i:i + 2], 16) for i in (0, 2, 4)], np.float32)


def clip_seconds(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True).stdout
    return float(out or 10.0)


def sfx_events(tl):
    """(time of the visual event, sound) for every element entrance."""
    S = {"pop": "element-pop/ui-click-soft", "fill": "list-fill/switch-soft-a", "slide": "card-slide/card-slide-b",
         "stamp": "stamp/soft-thud-a", "pin": "map-pin/wood-drop-a", "tick": "tick/box-check-click",
         "strike": "cross-strike/scratch-strike", "note": "marker-stroke/pen-on-paper-stroke",
         "paper": "paper/paper-slide", "count": "counter-tick/switch-click-a", "whoosh": "transition-whoosh/short-sweep"}
    ev = []
    prev_mode = None
    for b in tl["beats"]:
        if b["presenter"] == "hub" and prev_mode != "hub":
            ev.append((b["t_in"] + 0.15, S["whoosh"]))
        prev_mode = b["presenter"]
        for e in b["elements"]:
            t = e.get("t", b["t_in"])
            k = e["type"]
            ev += [(t + off, snd) for off, snd in e.get("sfx", [])]
            if k == "pills":
                ev += [(it[-1] + 0.12, S["pop"]) for it in e["items"]]
            elif k == "pill":
                ev.append((t + 0.12, S["pop"]))
            elif k == "note":
                ev.append((t + 0.1, S["note"]))
            elif k == "qcard":
                ev.append((t + 0.1, S["paper"]))
                ev.append((t + 0.6 + 0.25, S["stamp"]))
                if e.get("t_marks"):
                    ev.append((e["t_marks"] + 0.25, S["stamp"]))
            elif k in ("def", "section", "yn"):
                ev.append((t + 0.15, S["slide"]))
                if k == "yn":
                    ev.append((e["t_yes"] + 0.2, S["tick"]))
            elif k == "stamp":
                ev.append((t + 0.25, S["stamp"]))
            elif k == "radial":
                ev += [(it[-1] + 0.15, S["fill"]) for it in e["items"]]
                ev += [(r, S["count"]) for r in e.get("recount", [])]
            elif k == "territory":
                ev.append((e["t_cross"] + 0.1, S["strike"]))
                ev.append((e["t_right"] + 0.2, S["slide"]))
                ev.append((e["t_label"] + 0.15, S["pin"]))
            elif k == "hero":                         # an impact under the big words, a sweep with the underline
                n_ = len(e["text"].split())
                ev += [(t + 0.05, "colour-flood/low-thump-a"), (t + 0.2 + n_ * e.get("word_gap", 0.16), "arrow-draw/short-sweep")]
            elif k == "answer":                       # a sheet appearing, a scratch of the pen for each point that writes in now
                ev.append((t + 0.05, S["paper"]))
                a0, shown = e.get("animate_from", 0), e.get("show", len(e["points"]))
                ev += [(t + 0.5 + (i - a0) * e.get("gap", 0.35), S["tick"]) for i in range(a0, shown)]
            elif k == "qhero":
                ev.append((t + 0.05, S["whoosh"]))
                ev += [(ty + 0.12, S["stamp"]) for _, ty in e.get("years", [])]
                if e.get("t_next") is not None: ev.append((e["t_next"] + 0.15, S["stamp"]))
                if e.get("t_card") is not None: ev += [(e["t_card"] + 0.05, "page-turn/page-turn-a" if False else S["paper"])]
                if e.get("t_marks") is not None: ev.append((e["t_marks"] + 0.2, "colour-flood/low-thump-b"))
            elif k == "crowns":
                ev.append((e["t_one"] + 0.5, S["stamp"]))
                ev += [(e["t_many"] + 0.25 + i * 0.18, S["pop"]) for i in range(0, e.get("many", 8), 2)]
                ev += [(e[k2] + 0.12, S["pop"]) for k2 in ("t_left_sub", "t_right_sub") if e.get(k2)]
            elif k == "depth":
                ev += [(e["t_shallow"] + 0.2, S["whoosh"]), (e["t_stuck"] + 0.05, S["strike"]),
                       (e["t_deep"] + 0.2, S["whoosh"]), (e["t_deep"] + 1.7, S["tick"])]
            elif k == "hinterland":
                ev.append((e["t_region"] + 0.2, S["pop"]))
                ev += [(l[2] + 0.9, S["pin"]) for l in e["links"]]
                ev += [(e[k2] + 0.15, S["pop"]) for k2 in ("t_export", "t_import")]
            elif k == "pipeflow":
                ev += [(it[2] + 0.1, S["fill"]) for it in e["items"] if it[2] > b["t_in"] - 1]
            elif k == "seamap":                       # a sweep as each route sets off, a pin per port, a strike on the crossed route
                ev += [(r["t"] + 0.1, S["whoosh"]) for r in e["routes"] if r["t"] > b["t_in"] - 1]
                ev += [(p[3] + 0.1, S["pin"]) for p in e["ports"] if p[3] > b["t_in"] - 1]
                ev += [(r["t_cross"] + 0.1, S["strike"]) for r in e["routes"] if r.get("t_cross")]
                if e.get("beads") and e.get("t_beads", -1) > b["t_in"] - 1:
                    ev += [(e["t_beads"] + i * 0.24, S["pop"]) for i in range(0, len(e["beads"]), 3)]
                if e.get("t_thread"):
                    ev.append((e["t_thread"] + 0.1, S["whoosh"]))
                ev += [(g["t"] + 0.3, S["pop"]) for g in e.get("regions", []) if g["t"] > b["t_in"] - 1]
                if e.get("t_region"):
                    ev.append((e["t_region"] + 0.3, S["stamp"]))
            elif k == "seasons":
                ev += [(it[-1] + 0.15, S["pin"]) for it in e["stops"]]
            elif k == "quad":
                ev += [(it[-1] + 0.15, S["slide"]) for it in e["items"] if it[-1] < 1e5]
            elif k in ("chain", "cards3", "tiles"):
                ev += [(it[-1] + 0.15, S["pop" if k != "cards3" else "slide"]) for it in e["items"] if it[-1] < 1e5]
            elif k == "checklist":
                ev.append((t + 0.15, S["slide"]))
                ev += [(x + 0.5, S["tick"]) for x in (e.get("lit_t") or []) if x is not None]
            elif k == "blocs":
                ev += [(e["t_left"] + 0.15, S["pop"]), (e["t_right"] + 0.15, S["pop"]), (e["t_cross"] + 0.1, S["strike"])]
                if e.get("t_label"): ev.append((e["t_label"] + 0.15, S["stamp"]))
            elif k == "photo":
                ev.append((t + 0.1, S["paper"]))
            elif k == "ask":                          # the question pops, the answer ticks in under it
                ev.append((t + 0.1, S["pop"]))
                if e.get("answer") and e.get("t_answer"):
                    ev.append((e["t_answer"] + 0.25, S["tick"]))
            elif k == "inset":
                ev.append((t + 0.1, S["paper"]))
            # the reference-board elements (21 Oct 2026), with the Mixkit sounds from the team's zip
            elif k == "search":                       # keys while it types, a click on 'enter'
                per = 1 / e["cps"] if e.get("cps") else 0.07
                ev += [(t + 0.35, "typewriter/laptop-keys-loop"), (t + 0.35 + len(e["text"]) * per + 0.1, "button-press/double-click")]
            elif k == "toggle":
                ev.append((e.get("t_on", t + 0.6) + 0.05, "button-press/light-button"))
            elif k == "qmarks":
                ev += [(t + i * 0.24, S["pop"]) for i in range(0, e.get("n", 9), 3)]
            elif k == "timeline":
                ev += [(it[-1] + 0.12, "timeline-node/switch-soft-3") for it in e["items"] if it[-1] < 1e5]
            elif k == "progress":
                ev += [(t + 0.2, "clock/tick-tock"), (t + 0.2 + e.get("dur", 1.6), S["tick"])]
            elif k == "verdict":
                ev.append((t + 0.12, "stamp/metal-hit" if e.get("kind") == "cross" else S["tick"]))
            elif k == "notify":
                ev += [(it[-1] + 0.1, S["slide"]) for it in e["items"] if it[-1] < 1e5]
            elif k == "ring":
                ev.append((t + 0.05, "circle-scribble/scribble-on-paper"))
            elif k == "pins":
                ev += [(it[-1] + 0.3, S["pin"]) for it in e["items"] if it[-1] < 1e5]
            elif k == "formula":                      # the equation lands, then a tick per symbol as it is named
                ev.append((t + 0.1, S["pop"]))
                ev += [(it[-1] + 0.1, S["tick"]) for it in e.get("legend", []) if it[-1] < 1e5]
            elif k == "wheatstone":                   # each part clicks in as named; a soft thump when the needle comes to rest
                ev += [(e[c] + 0.1, S["pop"]) for c in ("t_P", "t_Q", "t_R", "t_S", "t_nodes", "t_cell", "t_galv") if e.get(c) is not None and e[c] < 1e5]
                if e.get("t_null") is not None: ev.append((e["t_null"] + 0.2, S["tick"]))
            elif k == "metrebridge":
                ev += [(e[c] + 0.1, S["pop"]) for c in ("t_wire", "t_strips", "t_R", "t_S", "t_galv", "t_jockey", "t_cell", "t_l") if e.get(c) is not None and 0 <= e[c] < 1e5]
                if e.get("t_slide") is not None and e["t_slide"] >= 0:
                    ev += [(e["t_slide"] + 0.05, "card-slide/card-slide-b"), (e["t_slide"] + 3.25, S["tick"])]
            elif k == "statemap":                     # the outline sweeps in, a soft thump as it fills
                ev += [(t + 0.05, "transition-whoosh/short-sweep"), (t + 1.0, "colour-flood/low-thump-a")]
            elif k == "pdfbadge":                     # the prize arrives: a thump, a pop as the crown lands, a tick
                ev += [(t + 0.1, "colour-flood/low-thump-b"), (t + 0.85, S["pop"]), (t + 1.2, S["tick"])]
            elif k == "flask":                        # the solution fills, the particles appear, the mole packets click in, M thuds
                for c, snd in (("t_fill", "card-slide/card-slide-b"), ("t_solute", S["pop"]), ("t_def", S["slide"]), ("t_m", S["pop"])):
                    if e.get(c) is not None and 0 <= e[c] < 1e5: ev.append((e[c] + 0.05, snd))
                if e.get("t_count") is not None and 0 <= e["t_count"] < 1e5: ev += [(e["t_count"] + 1.1 + k_ * 0.35, S["count"]) for k_ in range(3)]
                if e.get("t_M") is not None and 0 <= e["t_M"] < 1e5: ev.append((e["t_M"] + 0.15, "colour-flood/low-thump-b"))
            elif k == "rewrite":                      # the formula lands; each substitution slides in; each rewrite whooshes
                ev.append((t + 0.1, S["pop"]))
                ev += [(sb[-1] + 0.05, S["slide"]) for sb in e.get("subs", []) if sb[-1] < 1e5]
                ev += [(st[-1] + 0.05, S["whoosh"]) for st in e.get("steps", [])[1:] if st[-1] < 1e5]
            elif k == "cube":                         # the cube appears, the pour, the equality lands
                if e.get("t_cube") is not None: ev.append((e["t_cube"] + 0.05, S["pop"]))
                if e.get("t_pour") is not None: ev.append((e["t_pour"] + 0.2, "card-slide/card-slide-b"))
                if e.get("t_eq") is not None: ev.append((e["t_eq"] + 0.1, S["tick"]))
                if e.get("t_units") is not None: ev.append((e["t_units"] + 0.1, S["slide"]))
            elif k == "gift":                         # the gift arrives with a thump; it opens with a whoosh and a pop
                ev += [(t + 0.1, "colour-flood/low-thump-b"), (t + 0.85, S["pop"])]
                if e.get("t_open") is not None and e["t_open"] < 1e5: ev += [(e["t_open"] + 0.05, S["whoosh"]), (e["t_open"] + 0.6, S["pop"])]
            elif k == "qsheet":                       # the sheet lands; a marker squeak per highlighted line; the marks seal thuds
                ev.append((t + 0.1, S["paper"]))
                ev += [(l[2] + 0.05, S["note"]) for l in e.get("lines", [])]
                if e.get("t_marks") is not None: ev.append((e["t_marks"] + 0.2, "colour-flood/low-thump-b"))
            elif k == "papers":                       # each sheet lands with a paper slide, then its year stamp thuds
                ev += [(ty + 0.05, S["paper"]) for _, ty in e["years"]] + [(ty + 0.42, S["stamp"]) for _, ty in e["years"]]
                if e.get("t_after") is not None: ev.append((e["t_after"] + 0.1, S["tick"]))
                if e.get("t_next") is not None: ev.append((e["t_next"] + 0.15, S["stamp"]))
            elif k == "page":                         # the page lands with a paper slide; a shutter on "screenshot"
                ev.append((t + 0.05, S["paper"]))
                if e.get("badge") and e.get("t_badge") is not None:
                    ev.append((e["t_badge"] + 0.02, "photo-in/shutter-click"))
            elif k == "igsave":                       # a soft tap as the bookmark fills
                ev += [(t + 0.1, S["pop"]), (e.get("t_on", t + 0.6) + 0.05, "button-press/light-button")]
            elif k == "lottie":                       # a sound by what the animation is, unless the plan names one
                kind = e["src"].split("-")[0]
                snd = {"tick": S["tick"], "cross": "stamp/metal-hit", "pin": S["pin"], "circle": "circle-scribble/scribble-on-paper",
                       "arrow": "arrow-draw/arrow-whoosh", "toggle": "button-press/light-button", "question": S["pop"], "notify": S["slide"],
                       "chat": S["slide"], "magnifier": S["pop"], "growth": "arrow-draw/short-sweep", "clipboard": S["paper"]}.get(kind)
                if snd and not e.get("sfx"):
                    ev.append((t + e.get("sfx_at", 0.1), snd))
            elif k == "paper":
                ev += [(t + 0.1, "page-turn/book-page-flip"), (t + 0.35, "tape/duct-tape-pull")]
    tr = tl.get("tracker")
    if tr:                                            # a tick each time the corner list gains a point, where it is showing
        for x in tl["spine"]["lit_t"]:
            b = next((b for b in tl["beats"] if b["t_in"] <= x < b["t_out"]), None)
            if x >= tr["show_t"] and b and b["pbox"].get("card") and b.get("tracker") is not False:
                ev.append((x + 0.2, S["tick"]))
    return sorted(ev)


# the machine's fastest H.264 encoder: the GPU's (VideoToolbox, NVENC, Quick Sync, AMF) when it has one, else x264
sys.path.insert(0, str(ROOT / "tools"))
from encoders import video_args  # noqa: E402
VCODEC = video_args()


def mix_audio(tl, proj, music, out):
    sfx = json.loads((ROOT / "library/sfx/manifest.json").read_text())
    peak = {s["id"]: s["peak_offset"] for s in sfx["sounds"]}
    ev = sfx_events(tl)
    dur = tl["duration"]
    # no background music is the standard; the library was removed on 26 Oct 2026, so its manifest may be gone
    mf = ROOT / "library/music/manifest.json"
    mman = json.loads(mf.read_text()) if mf.exists() else []
    mman = mman if isinstance(mman, list) else mman.get("tracks", [])
    lufs = next((m["integrated_lufs"] for m in mman if m["file"] == music), -16.0)
    gain_db = -31.0 - lufs                   # the bed sits about 15 LU under his voice
    bed = music not in (None, "", "none")      # "--music none": voice and sound effects only
    args = ["ffmpeg", "-v", "error", "-y", "-i", str(proj / f"src/part{tl.get('part', 1)}.mp4")]
    if bed:
        args += ["-i", str(ROOT / "library" / music)]
    for _, sid in ev:
        args += ["-i", str(ROOT / "library/sfx" / f"{sid}.wav")]
    f = [f"[0:a]aresample=48000,aformat=channel_layouts=stereo[v]"]
    labels = ["[v]"]
    if bed:
        f.append(f"[1:a]aresample=48000,aformat=channel_layouts=stereo,volume={gain_db:.1f}dB,afade=t=in:d=1.5,"
                 f"afade=t=out:st={dur - 3:.2f}:d=3,atrim=0:{dur:.2f}[m]")
        labels.append("[m]")
    first = 2 if bed else 1
    for i, (t, sid) in enumerate(ev):
        start = max(0.0, t - peak.get(sid, 0.0))
        ms = int(round(start * 1000))
        f.append(f"[{i + first}:a]aresample=48000,aformat=channel_layouts=stereo,volume=-9dB,adelay={ms}|{ms}[s{i}]")
        labels.append(f"[s{i}]")
    f.append("".join(labels) + f"amix=inputs={len(labels)}:normalize=0:duration=first,alimiter=limit=0.95[a]")
    args += ["-filter_complex", ";".join(f), "-map", "[a]", "-c:a", "aac", "-b:a", "192k", str(out)]
    subprocess.run(args, check=True)
    return len(ev)


def main(argv):
    plan_p = Path(argv[0])
    plan = json.loads(plan_p.read_text())
    music = argv[argv.index("--music") + 1] if "--music" in argv else "music/documentary-calm/forest-mist-whispers.mp3"
    proj = ROOT / "projects" / plan["project"]
    out = HERE / "out" / plan_p.stem
    final = Path(argv[argv.index("--out") + 1]) if "--out" in argv else proj / "final" / f"{plan['project'].replace('-', '_')}_part{plan['part']}.mp4"
    final.parent.mkdir(parents=True, exist_ok=True)
    tl = load_tl(out)
    C.set_framing(tl.get("framing"))                  # the same presenter crop the stills were built with
    n = math.ceil(tl["duration"] * FPS)
    # --range a:b renders frames [a, b) as a video-only segment (--out), so one render can be split across cores;
    # the audio is mixed by a full run beforehand and joined when the segments are concatenated
    seg = "--range" in argv
    a0, a1 = (int(x) for x in argv[argv.index("--range") + 1].split(":")) if seg else (0, n)
    a1 = min(a1, n)

    audio = out / "mix.m4a"
    if not seg:
        k = mix_audio(tl, proj, music, audio)
        print(f"audio: voice + {Path(music).stem} + {k} sound cues")

    plate = np.asarray(Image.open(ROOT / "library/backgrounds/plates" / (tl.get("plate_path") or f"generated/{tl['plate']}.jpg")).convert("RGB").resize((W, H)), np.float32)
    fast_seek = seg and "--seek" in argv              # a late segment: let ffmpeg seek instead of decoding everything before it
    pres = reader((["-ss", f"{a0 / FPS:.4f}"] if fast_seek and a0 else []) + ["-i", str(proj / f"src/part{plan['part']}.mp4"), "-vf",
                   f"fps={FPS},crop={C.CW}:{C.CH}:{C.CROP[0]}:{C.CROP[1]}"], C.CW, C.CH)
    io = ["-i", "-"] + ([] if seg else ["-i", str(audio), "-map", "0:v", "-map", "1:a"])
    tail = [] if seg else ["-c:a", "copy", "-shortest", "-movflags", "+faststart"]
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS)] + io +
                           VCODEC + tail +
                           [str(final)], stdin=subprocess.PIPE)
    for _ in range(0 if fast_seek else a0):           # a segment starts mid-take: skip to the frame a full run would show
        next(pres)
    grades = {False: grade_full(False), True: grade_full(True)}
    beat_i, broll, bd_cache, mask_cache = -1, None, {}, {}
    g_ino, g_arr = None, None
    for i in range(a0, a1):
        t = i / FPS
        bi = next((j for j, b in enumerate(tl["beats"]) if b["t_in"] <= t < b["t_out"]), len(tl["beats"]) - 1)
        b = tl["beats"][bi]
        if bi != beat_i:                                  # a new beat: open its clip
            beat_i = bi
            broll = None
            br = b.get("broll")
            if br and br.get("clip"):
                src = C.clip_path(proj, br["clip"])
                # clips are 8 s (newer Flow) or 10 s: slow by the clip's REAL length so the beat never outruns it
                dur = clip_seconds(src) - br.get("offset", 0) - 0.3
                rate = min(1.0, dur / max(b["t_out"] - b["t_in"], 0.1))
                off = br.get("offset", 0)
                if br.get("span"):          # play exactly this stretch of the clip across the beat (sped up or slowed to fit),
                    a_, z_ = br["span"]     # so the beat ENDS on the clip's ending: a needle coming to rest, a balance going level
                    off, rate = a_, (z_ - a_) / max(b["t_out"] - b["t_in"], 0.1)
                broll = reader(["-ss", f"{off:.2f}", "-i", str(src), "-vf", f"setpts=PTS/{rate:.4f},fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}"], W, H)
                for _ in range(max(0, i - math.ceil(b["t_in"] * FPS - 1e-9))):   # a segment opening mid-beat
                    next(broll)
            elif br and br.get("photo") and br.get("region", "full") == "full":
                # a real photograph standing in for a clip: painted UNDER the presenter, like footage.  The page draws
                # photos itself only in stills; in a render its layer lies on top of him and hid him (Molarity, 24 Oct 2026)
                key = ("photo", br["photo"])
                if key not in bd_cache:
                    im = Image.open(ROOT / "library/backgrounds/photos" / br["photo"]).convert("RGB")
                    sc = max(W / im.width, H / im.height)
                    im = im.resize((math.ceil(im.width * sc), math.ceil(im.height * sc)), Image.LANCZOS)
                    l_, t_ = (im.width - W) // 2, (im.height - H) // 2
                    bd_cache[key] = np.asarray(im.crop((l_, t_, l_ + W, t_ + H)), np.float32)
                broll = itertools.repeat(bd_cache[key])          # the same picture, every frame (bound now: `key` is reused below)
        if broll is not None and b["broll"].get("region", "full") == "full":
            frame = next(broll).astype(np.float32) * grades[bool(b["broll"].get("dim"))]
        else:
            if b.get("plate"):                            # a beat that brings its own background
                if b["plate"] not in bd_cache:
                    bd_cache[b["plate"]] = np.asarray(Image.open(ROOT / "library/backgrounds/plates/generated" / f"{b['plate']}.jpg")
                                                     .convert("RGB").resize((W, H)), np.float32)
                frame = bd_cache[b["plate"]].copy()
            else:
                frame = plate.copy()
        if broll is not None and b["broll"].get("region", "full") != "full":
            # a print: the clip fills the hole inside the frame the page draws
            # (stage.html: left 44, width 992, top 178, height head-220, 18px border, unrotated)
            ix0, iy0 = 62, 196
            iw, ih = 956, b["pbox"]["head"] - 220 - 36
            src = next(broll)
            s_ = max(iw / W, ih / H)
            im = Image.fromarray(src).resize((math.ceil(W * s_), math.ceil(H * s_)), Image.BILINEAR)
            ox_, oy_ = (im.width - iw) // 2, (im.height - ih) // 2
            a_ = np.asarray(im.crop((ox_, oy_, ox_ + iw, oy_ + ih)), np.float32) / 255
            if b["broll"].get("treatment") == "duotone-navy":       # the page's duotone: navy screened under greyscale
                g_ = np.clip((a_.mean(2, keepdims=True) - .5) * 1.25 + .5 + .04, 0, 1)
                navy = np.array([0x1E, 0x2F, 0x5C], np.float32) / 255
                a_ = 1 - (1 - navy) * (1 - g_)
            frame[iy0:iy0 + ih, ix0:ix0 + iw] = a_ * 255

        cut = C.grade(C.key_np(next(pres).tobytes()), tl.get("presenter_grade"))
        if tl.get("scene_match") and not (b["pbox"].get("card") or b["pbox"].get("hub")):   # free-standing only: card/hub carry their own backdrop
            pbx = b["pbox"]; x0_, y0_ = max(0, pbx["x"]), max(0, pbx["y"])
            cut = cut.resize((pbx["w"], pbx["h"]), Image.BICUBIC)
            bgc = np.zeros((pbx["h"], pbx["w"], 3), np.float32)
            reg = frame[y0_:min(H, pbx["y"] + pbx["h"]), x0_:min(W, pbx["x"] + pbx["w"])]
            bgc[y0_ - pbx["y"]:y0_ - pbx["y"] + reg.shape[0], x0_ - pbx["x"]:x0_ - pbx["x"] + reg.shape[1]] = reg
            cut = C.scene_match(cut, bgc, tl["scene_match"])
        pb = b["pbox"]
        if pb.get("hub"):
            d, ox, oy = 2 * pb["r"], pb["cx"] - pb["r"], pb["cy"] - pb["r"]
            key = pb.get("backdrop")
            if key not in bd_cache and key == "plate":     # the plate itself, zoomed in and lifted
                cy_, cx_ = H // 2, W // 2
                z = plate[cy_ - d // 4:cy_ + d // 4, cx_ - d // 4:cx_ + d // 4]
                im = Image.fromarray(np.clip(z * 1.35, 0, 255).astype(np.uint8)).resize((d, d), Image.BICUBIC)
                bd_cache[key] = np.asarray(im, np.float32)
            if key not in bd_cache:
                if key and key.startswith("veo:"):
                    f = out / "assets" / f"bd_{key[4:].split('@')[0]}.png"
                elif key:
                    f = out / "assets" / (Path(key).stem + ".png")
                im = Image.open(f).convert("RGB")
                s = max(d / im.width, d / im.height)
                im = im.resize((math.ceil(im.width * s), math.ceil(im.height * s)), Image.LANCZOS)
                l, tp = (im.width - d) // 2, (im.height - d) // 2
                bd = np.asarray(im.crop((l, tp, l + d, tp + d)), np.float32) * 0.92
                bd_cache[key] = bd
            disc = bd_cache[key].copy()
            p = np.asarray(cut.resize((pb["w"], pb["h"]), Image.BICUBIC))
            blend_d = disc
            hh, ww = p.shape[:2]
            px, py = pb["x"] - ox, pb["y"] - oy
            x0, y0, x1, y1 = max(0, px), max(0, py), min(d, px + ww), min(d, py + hh)
            src = p[y0 - py:y1 - py, x0 - px:x1 - px].astype(np.float32)
            a = src[..., 3:4] / 255.0
            blend_d[y0:y1, x0:x1] = blend_d[y0:y1, x0:x1] * (1 - a) + src[..., :3] * a
            if d not in mask_cache:
                yy, xx = np.mgrid[0:d, 0:d]
                r = np.sqrt((xx - d / 2 + .5) ** 2 + (yy - d / 2 + .5) ** 2)
                mask_cache[d] = np.clip(d / 2 - r, 0, 1)[..., None].astype(np.float32)
            m = mask_cache[d]
            frame[oy:oy + d, ox:ox + d] = frame[oy:oy + d, ox:ox + d] * (1 - m) + blend_d * m
        elif pb.get("card"):
            bx, by, bw, bh = pb["box"]
            key = ("card", bw, bh)
            cs = tl.get("card_style") or {}
            if key not in bd_cache and cs.get("backdrop"):   # a topic backdrop image, cover-fitted to the card (stage.html draws the same)
                im = Image.open(ROOT / "library/backgrounds/plates/generated" / f"{cs['backdrop']}.jpg").convert("RGB")
                sc = max(bw / im.width, bh / im.height)
                im = im.resize((math.ceil(im.width * sc), math.ceil(im.height * sc)), Image.LANCZOS)
                l_, t_ = (im.width - bw) // 2, (im.height - bh) // 2
                bd_cache[key] = np.asarray(im.crop((l_, t_, l_ + bw, t_ + bh)), np.float32)
                r = pb["radius"]; yy, xx = np.mgrid[0:bh, 0:bw].astype(np.float32)
                qx = np.maximum(np.maximum(r - xx, xx - (bw - 1 - r)), 0); qy = np.maximum(np.maximum(r - yy, yy - (bh - 1 - r)), 0)
                mask_cache[key] = np.clip(r - np.sqrt(qx ** 2 + qy ** 2) + .5, 0, 1)[..., None]
            if key not in bd_cache:        # the THEME's accent, lighter behind his head: what stage.html draws in the stills
                yy, xx = np.mgrid[0:bh, 0:bw].astype(np.float32)
                d_ = np.sqrt(((xx - bw / 2) / bw) ** 2 + ((yy - bh * .25) / bh) ** 2)
                acc = theme_accent(tl.get("theme"))
                c0, c1 = acc * 0.7 + 255 * 0.3, acc * 0.6                    # color-mix(accent 70%, #fff) .. (accent 60%, #000)
                t_ = np.clip(d_ / 0.75, 0, 1)[..., None]
                mid = np.clip(t_ / 0.55, 0, 1)
                bd_cache[key] = np.where(t_ < 0.55, c0 * (1 - mid) + acc * mid, acc * (1 - (t_ - .55) / .45) + c1 * ((t_ - .55) / .45))
                r = pb["radius"]
                qx = np.maximum(np.maximum(r - xx, xx - (bw - 1 - r)), 0)
                qy = np.maximum(np.maximum(r - yy, yy - (bh - 1 - r)), 0)
                mask_cache[key] = np.clip(r - np.sqrt(qx ** 2 + qy ** 2) + .5, 0, 1)[..., None]
            disc = bd_cache[key].copy()
            p = np.asarray(cut.resize((pb["w"], pb["h"]), Image.BICUBIC))
            px, py = pb["x"] - bx, pb["y"] - by
            x0, y0, x1, y1 = max(0, px), max(0, py), min(bw, px + p.shape[1]), min(bh, py + p.shape[0])
            src = p[y0 - py:y1 - py, x0 - px:x1 - px].astype(np.float32)
            a = src[..., 3:4] / 255.0
            disc[y0:y1, x0:x1] = disc[y0:y1, x0:x1] * (1 - a) + src[..., :3] * a
            m = mask_cache[key]
            frame[by:by + bh, bx:bx + bw] = frame[by:by + bh, bx:bx + bw] * (1 - m) + disc * m
        else:
            p = np.asarray(cut.resize((pb["w"], pb["h"]), Image.BICUBIC))
            blend(frame, p, pb["x"], pb["y"])

        gp = out / "frames" / f"g_{i:05d}.png"
        while not gp.exists():                        # a partial re-render: the graphics layer may still be drawing it
            time.sleep(0.2)
        ino = gp.stat().st_ino
        if ino != g_ino:
            g_ino, g_arr = ino, np.asarray(Image.open(gp).convert("RGBA"))
        blend(frame, g_arr, 0, 0)
        enc.stdin.write(np.clip(frame, 0, 255).astype(np.uint8).tobytes())
        if i % 300 == 0:
            print(f"  {i}/{n}", flush=True)
    enc.stdin.close()
    enc.wait()
    print(final)


if __name__ == "__main__":
    main(sys.argv[1:])
