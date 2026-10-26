"""Compile a plan (data) + the caption track into an absolute timeline, and
prepare the frames a still needs.  Kit test only — see plan_*.json.

    .venv-tools/bin/python lab/kit_test/compile.py <plan.json> [--stills t1,t2,...]

The plan names caption LINES and SLOTS; this file is the only place either is
turned into seconds or pixels.  The HTML stage then draws any time t from the
timeline alone, so a frame never depends on the frame before it.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
W, H = 1080, 1920
LEAD = 0.30                       # a graphic starts this much before its line

# The presenter plate: same crop and key as projects/pol-c3-la-01/work/render_d.py,
# so he looks identical to the shipped cut.  Uniform scale only, never boxed
# (memory: presenter-is-never-framed).
CROP = (640, 150, 1400, 770)
CW, CH = CROP[2] - CROP[0], CROP[3] - CROP[1]
HEAD_IN_CROP = 32
PRESENTER = {                      # mode -> (width on screen, centre x)
    "hero": (1180, 540),
    "standard": (1000, 540),       # every free-standing mode centred horizontally (user, 23 Oct 2026)
    "small": (820, 540),
    "full": (1000, 540),           # free-standing even under presenter_style "card": the story beats (a walk, a zoom)
}

# Map crop: the peninsula only.  The project's atlas draws India's de facto
# northern boundary, which must never appear on screen, so the crop starts
# well south of it (y >= 700 of the 1080x1920 atlas).
MAP_CROP = (60, 700, 1020, 1340)
MAP_PINS = {"hyderabad": (539, 1013), "junagadh": (314, 890)}


FACE_IN_CROP = [316, 150]           # his face centre inside the crop; x is RE-MEASURED from each clip (measure_centre)


def measure_centre(proj, part):
    """Where he actually stands in this clip's crop, so every mode can centre him on screen.

    Each HeyGen take frames him differently: the Wheatstone stand-in had his body at x = 245 of the
    760 px crop, not the 316 the constant above assumed, so a free-standing presenter sat 120 px left
    of centre.  This keys 9 frames across the clip and takes the median centre of his shoulders and
    head (rows 5-60% of the crop; hands drop below and gesture out of it).  Cached per clip.
    """
    src = proj / f"src/part{part}.mp4"
    cache = proj / f"presenter_centre_part{part}.json"
    key = f"{src.resolve()}:{src.stat().st_size}"
    if cache.exists():
        c = json.loads(cache.read_text())
        if c.get("key") == key:
            return c["x"]
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(src)],
                               capture_output=True, text=True).stdout or 10)
    xs = []
    for k in range(1, 10):
        raw = grab(src, dur * k / 10, vf=f"crop={CW}:{CH}:{CROP[0]}:{CROP[1]}")
        a = np.asarray(key_np(raw))[..., 3].astype(np.float32)[int(CH * .05):int(CH * .60)]
        col = a.sum(0)
        if col.sum() > 0:
            xs.append(float((col * np.arange(CW)).sum() / col.sum()))
    x = round(float(np.median(xs)), 1) if xs else 316.0
    cache.write_text(json.dumps({"key": key, "x": x}))
    return x


def presenter_box(mode, hub=None):
    if mode == "hub":
        # A circle he sits INSIDE: one uniform scale, the circle centred on his
        # face (not on the crop), the rest masked away.  Never resized to fit.
        h_ = {"cx": 540, "cy": 960, "r": 235, "scale": 0.9, **(hub or {})}
        s = h_["scale"]
        fx, fy = FACE_IN_CROP
        x = round(h_["cx"] - fx * s)
        y = round(h_["cy"] - 45 - fy * s)
        r = h_["r"]
        return {"hub": True, "cx": h_["cx"], "cy": h_["cy"], "r": r, "x": x, "y": y,
                "w": round(CW * s), "h": round(CH * s), "scale": s, "head": h_["cy"] - h_["r"],
                "face": [h_["cx"] - r, h_["cy"] - r, h_["cx"] + r, h_["cy"] + r],
                "backdrop": h_.get("backdrop")}
    if mode == "card":
        # A rounded card at the bottom right, ABOVE the caption band. Same rule as
        # the hub: one uniform scale, his face centred in the card, the rest masked.
        c = {"x": 588, "y": 1130, "w": 452, "h": 560, "r": 44, "scale": 0.84, **(hub or {})}
        s = c["scale"]
        fx, fy = FACE_IN_CROP
        return {"card": True, "cx": c["x"] + c["w"] // 2, "cy": c["y"] + c["h"] // 2,
                "box": [c["x"], c["y"], c["w"], c["h"]], "radius": c["r"],
                "x": round(c["x"] + c["w"] / 2 - fx * s), "y": round(c["y"] + c["h"] * 0.36 - fy * s),
                "w": round(CW * s), "h": round(CH * s), "scale": s, "head": c["y"],
                "face": [c["x"], c["y"], c["x"] + c["w"], c["y"] + c["h"]], "backdrop": c.get("backdrop")}
    w, cx = PRESENTER[mode]
    s = w / CW
    h = round(CH * s)
    top = H - h
    # centred on HIM (his measured centre in the crop), not on the crop: the crop is not centred on him
    return {"x": round(cx - FACE_IN_CROP[0] * s), "y": top, "w": w, "h": h,
            "head": round(top + HEAD_IN_CROP * s), "scale": s,
            # the face, which no caption may cover: head top to about the collar
            "face": [round(cx - 170 * s), round(top + HEAD_IN_CROP * s),
                     round(cx + 170 * s), round(top + 290 * s)]}


def key_np(buf):
    """Green-dominance key, copied from render_d.key_np (read-only reuse)."""
    a = np.frombuffer(buf, np.uint8).reshape(CH, CW, 3).astype(np.float32)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    dom = g - np.maximum(r, b)
    alpha = np.clip((25 - dom) / 18.0, 0, 1)
    a[..., 1] = g - np.clip(dom, 0, None) * 0.92
    sh = np.clip(1.0 - a.mean(2) / 90.0, 0, 1)
    a[..., 1] -= np.clip(a[..., 1] - a[..., 0], 0, None) * 0.45 * sh
    a[..., 0] *= 1.02
    a[..., 2] *= 0.99
    lum = (a[..., 0] * .299 + a[..., 1] * .587 + a[..., 2] * .114)[..., None]
    a = np.clip(lum + (a - lum) * 1.05, 0, 255)
    return Image.fromarray(np.dstack([a.astype(np.uint8),
                                      (alpha * 255).astype(np.uint8)]), "RGBA")


def grade(cut, g=None):
    """Make the keyed presenter sit in the scene (user, 23 Oct 2026: "dark circles visible, looks alien").

    In order: (1) choke and soften the matte by a pixel, so hair and ears lose the jagged key edge;
    (2) kill the green-screen fringe in the edge band (the yellow-green on his ears); (3) lift skin
    that is darker than the skin around it, which is what dark circles are, without touching beard,
    brows or eyes (they are not skin-coloured); (4) a gentle global grade: a little brighter, warmer,
    softer contrast, a touch more colour, so he matches the warm footage around him.
    Every number is a plan setting ("presenter_grade"); {} or None leaves him untouched.
    """
    if not g:
        return cut
    from PIL import ImageFilter
    a = np.asarray(cut).astype(np.float32)
    rgb, al = a[..., :3], a[..., 3] / 255.0
    # (1) matte: blur 1 px, choke a little
    am = Image.fromarray((al * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(g.get("matte_soft", 1.0)))
    al2 = np.clip((np.asarray(am, np.float32) / 255.0 - g.get("matte_choke", 0.06)) / (1 - g.get("matte_choke", 0.06)), 0, 1)
    # (2) edge despill: within ~6 px of the matte edge, green no higher than the red/blue mean, and less saturated
    band = np.asarray(Image.fromarray((al * 255).astype(np.uint8)).filter(ImageFilter.BoxBlur(6)), np.float32) / 255.0
    edge = np.clip((0.985 - band) / 0.25, 0, 1)[..., None]
    r, gg, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    gcap = np.minimum(gg, (r + b) / 2 + 4)
    rgb = np.stack([r, gg * (1 - edge[..., 0]) + gcap * edge[..., 0], b], -1)
    lum = (rgb * [0.299, 0.587, 0.114]).sum(-1, keepdims=True)
    rgb = rgb * (1 - 0.45 * edge) + lum * 0.45 * edge
    # (3) dark circles: skin darker than its neighbourhood is lifted toward it
    r, gg, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    L = 0.299 * r + 0.587 * gg + 0.114 * b
    skin = np.clip(((r - b) - 12) / 25, 0, 1) * np.clip((r - gg + 2) / 10, 0, 1) * np.clip((L - 45) / 30, 0, 1) * np.clip((235 - L) / 30, 0, 1)
    skin = np.asarray(Image.fromarray((skin * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2)), np.float32) / 255.0
    Lb = np.asarray(Image.fromarray(np.clip(L, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(g.get("lift_radius", 10))), np.float32)
    d_ = Lb - L
    # only the gentle shading of mid-tone skin: brows, lashes and beard edges are far darker than their
    # surroundings and brown enough to pass the skin test, and lifting them is what faded the eyebrows
    # (user, 23 Oct 2026: "his eyebrows look so faded")
    gentle = np.clip((28 - d_) / 10, 0, 1) * np.clip((L - 85) / 25, 0, 1)
    lift = np.clip(d_, 0, 28) * g.get("shadow_lift", 0.7) * skin * gentle
    rgb = rgb * ((L + lift) / np.maximum(L, 1))[..., None]
    # dark features defined: anything much darker than its neighbourhood (brows, lashes) is deepened a little
    dfn = g.get("define", 0)
    if dfn:
        deep = np.clip((d_ - 14) / 24, 0, 1) * dfn
        rgb = rgb * (1 - deep)[..., None]
    # (4) global grade
    rgb = rgb * g.get("exposure", 1.06)
    rgb = (rgb - 128) * g.get("contrast", 0.94) + 128
    rgb = rgb * np.array([g.get("warm", 1.035), 1.0, 2 - g.get("warm", 1.035)], np.float32)
    lum = (rgb * [0.299, 0.587, 0.114]).sum(-1, keepdims=True)
    rgb = lum + (rgb - lum) * g.get("saturation", 1.08)
    # (5) soften (user, 24 Oct 2026: "soften a little bit so it looks smooth and high quality"): a small blur blended
    # into mid-tone skin only; eyes, brows, lashes and beard are outside the mask and keep their detail
    sf = g.get("soften")
    if sf:
        blur = np.asarray(Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(sf.get("radius", 1.6))), np.float32)
        m = (skin * gentle * sf.get("amount", 0.5))[..., None]
        rgb = rgb * (1 - m) + blur * m
    rgb = np.clip(rgb, 0, 255).astype(np.uint8)
    # (5) crispness back (user, 23 Oct 2026: "the avatar looks too faded and softened"): an unsharp mask on the
    # detail only (threshold), so eyes, brows, beard and shirt texture read at reel size without haloing the edge
    sh = g.get("sharpen")
    if sh:   # inside the outline only: sharpening across the matte edge draws a light rim round the face and hair
        sharp = np.asarray(Image.fromarray(rgb).filter(ImageFilter.UnsharpMask(sh.get("radius", 1.2), sh.get("percent", 60), sh.get("threshold", 2))), np.float32)
        # eroded by blur-and-threshold: a 9x9 MinFilter did the same job at 0.33 s a frame, most of a render's time
        inner = np.asarray(Image.fromarray((al2 * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(4)), np.float32)
        k = np.clip((inner - 215) / 30, 0, 1)[..., None]
        rgb = (rgb * (1 - k) + sharp * k).astype(np.uint8)
    out = np.dstack([rgb, (al2 * 255).astype(np.uint8)])
    return Image.fromarray(out, "RGBA")


def set_framing(f):
    """A plan's "framing": a different crop of the HeyGen frame (e.g. waist-up) and the free-standing width.
    Default stays the chest-up crop every delivered video used."""
    global CROP, CW, CH
    if not f:
        return
    CROP = tuple(f["crop"])
    CW, CH = CROP[2] - CROP[0], CROP[3] - CROP[1]
    if f.get("full_w"):
        PRESENTER["full"] = (f["full_w"], 540)
        PRESENTER["standard"] = (f["full_w"], 540)


def scene_match(cut, bg, g=None):
    """Sit him in THIS shot: tint toward the background's own colour, wrap its light round his edges,
    and fade the bottom edge of the cut (user's reference, 23 Oct 2026: "looks so natural with the background").
    `bg` is the background behind his box, same size as `cut`, RGB uint8/float."""
    if not g:
        return cut
    from PIL import ImageFilter
    a = np.asarray(cut).astype(np.float32); rgb, al = a[..., :3], a[..., 3] / 255.0
    bgf = np.asarray(bg, np.float32)[..., :3]
    m = bgf.reshape(-1, 3).mean(0); m = m / max(m.mean(), 1)
    rgb = rgb * (1 + g.get("tint", 0.14) * (m - 1))
    # light wrap: the blurred background bleeds into the outer edge of the matte
    blur = np.asarray(Image.fromarray(np.clip(bgf, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(12)), np.float32)
    inner = np.asarray(Image.fromarray((al * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(g.get("wrap_px", 10))), np.float32) / 255.0
    wrap = np.clip((1 - inner) * 2.2, 0, 1)[..., None] * al[..., None] * g.get("wrap", 0.35)
    rgb = rgb * (1 - wrap) + blur * wrap
    # soft bottom: the crop's hard horizontal edge fades out
    fb = g.get("bottom_fade", 0)
    if fb:
        n = int(al.shape[0] * fb); ramp = np.ones(al.shape[0], np.float32); ramp[-n:] = np.linspace(1, 0, n) ** 1.4
        al = al * ramp[:, None]
    return Image.fromarray(np.dstack([np.clip(rgb, 0, 255), al * 255]).astype(np.uint8), "RGBA")



def clip_path(proj, cid):
    """A beat's footage: an exact render in diagrams/ (Manim, HTML, SVG: anything where correctness matters),
    else the cleaned Veo clip, else the raw download. Returns a path that may not exist yet."""
    for c in (proj / f"diagrams/{cid}.mp4", proj / f"veo/clean/{cid}.mp4", proj / f"veo/clips/{cid}.mp4"):
        if c.exists():
            return c
    return proj / f"veo/clean/{cid}.mp4"

def grab(src, t, vf=None, w=None, h=None):
    args = ["ffmpeg", "-v", "error", "-threads", "2", "-ss", f"{t:.3f}", "-i", str(src),
            "-frames:v", "1"]
    if vf:
        args += ["-vf", vf]
    args += ["-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    return subprocess.run(args, capture_output=True, check=True).stdout


def mode_of(plan, b):
    """A plan may restyle every standing beat at once ("presenter_style": "card" or "hub")."""
    if plan.get("presenter_style") == "card" and b["presenter"] in ("standard", "small", "hero"):
        return "card"
    if plan.get("presenter_style") == "hub" and b["presenter"] in ("standard", "small", "hero"):
        return "hub"
    return b["presenter"]


def resolve(plan, lines, duration):
    t0 = lambda i: max(0.0, lines[i]["t0"] - LEAD)
    tl = {"skin": plan["skin"], "theme": plan.get("theme"), "plate": plan["plate"], "duration": duration,
          "spine": dict(plan["spine"]), "beats": [], "captions": [],
          "hilite": plan.get("hilite", [])}
    sp = tl["spine"]
    sp["lit_t"] = [t0(i) for i in sp.pop("lit_at")]
    sp["show_t"] = t0(sp.pop("show_from"))
    def ref(v, floor_t=0.0):
        """A cue: a line index, or [line index, seconds after it starts]."""
        if isinstance(v, list):
            return max(floor_t, lines[v[0]]["t0"] + v[1])
        if isinstance(v, int) and v >= len(lines):      # "not in this part"
            return 1e6
        return max(floor_t, t0(v))

    for b in plan["beats"]:
        cut = lambda v: ref(v) if isinstance(v, list) else t0(v)    # a beat may cut mid-line: [line, seconds]
        tin = 0.0 if b["in"] == 0 else cut(b["in"])
        tout = duration if b["out"] == "end" else cut(b["out"])
        els = []
        for e in b["elements"]:
            e = dict(e)
            if "at" in e:
                e["t"] = ref(e.pop("at"), tin)
            if "right_at" in e:
                e["t_right"] = ref(e.pop("right_at"))
            for k in [k for k in e if k.startswith("t_") and not isinstance(e[k], float)]:
                e[k] = ref(e[k], tin)
            if "lit_t" in e:
                e["lit_t"] = [None if v is None else ref(v) for v in e["lit_t"]]
            if "recount" in e:
                e["recount"] = [ref(v) for v in e["recount"]]
            for key in ("items", "stops", "states"):
                if key in e and e["type"] in ("pills", "chain", "radial", "cards3", "seasons", "quad", "tiles", "bars", "dots100", "timeline", "notify", "pins", "portraits"):
                    e[key] = [list(it[:-1]) + [ref(it[-1], tin)] for it in e[key]]
                    e.setdefault("t", e[key][0][-1])
            if e["type"] == "rewrite":                   # steps: [tex, cue]; subs: [photo, tex, label, cue]
                e["steps"] = [list(st[:-1]) + [ref(st[-1], tin)] for st in e.get("steps", [])]
                e["subs"] = [list(sb[:-1]) + [ref(sb[-1], tin)] for sb in e.get("subs", [])]
            if e["type"] == "qsheet":                    # lines: [top fraction, right fraction, cue]
                e["lines"] = [l[:2] + [ref(l[2], tin)] for l in e.get("lines", [])]
            if "legend" in e:                             # formula legend rows: [symbol, meaning, cue]
                e["legend"] = [it[:-1] + [ref(it[-1], tin)] for it in e["legend"]]
            if e["type"] in ("qhero", "papers"):         # years: [label, cue]
                e["years"] = [[y, ref(c_, tin)] for y, c_ in e.get("years", [])]
            if e["type"] == "hinterland":                # links: [label, rail|road|pipe|water, cue]
                e["links"] = [l[:2] + [ref(l[2], tin)] for l in e["links"]]
            if e["type"] == "pipeflow":                  # [label, colour, cue, star?]; "pre" = already flowing
                e["items"] = [it[:2] + [-100.0 if it[2] == "pre" else ref(it[2], tin)] + it[3:] for it in e["items"]]
                e.setdefault("t", max(tin, min(it[2] for it in e["items"])))
            if e["type"] == "seamap":                    # cues nested in routes, ports and labels; "pre" = already there
                cue = lambda v: -100.0 if v == "pre" else ref(v, tin)
                e["routes"] = [{**r, "t": cue(r["at"]), "stops": [[i, cue(c)] for i, c in r["stops"]] if "stops" in r else None,
                                "t_cross": cue(r["cross_at"]) if "cross_at" in r else None,
                                "t_tag": cue(r["tag_at"]) if "tag_at" in r else None} for r in e.get("routes", [])]
                for r in e["routes"]:
                    if r["stops"] is None:
                        del r["stops"]
                e["ports"] = [p[:3] + [cue(p[3])] + p[4:] for p in e.get("ports", [])]
                e["labels"] = [l[:2] + [cue(l[2])] + l[3:] for l in e.get("labels", [])]
                e["regions"] = [{**g, "t": cue(g["at"]), "t_label": cue(g.get("label_at", g["at"]))} for g in e.get("regions", [])]
                for k in ("t_beads", "t_thread", "t_region", "t_region_label"):     # pearls, thread and empire extent
                    if k in e and not isinstance(e[k], float):
                        e[k] = cue(e[k])
            if e["type"] == "inset":                     # always top right (or left); the slot is implied
                e.setdefault("slot", "over-broll-right")
            if e["type"] in ("ring", "pins", "qmarks", "verdict", "lottie", "page", "papers", "qsheet", "gift"):   # placed by frame coordinates, not by slot
                e.setdefault("slot", "over-broll")
            if e["slot"].startswith("map:"):
                px, py = MAP_PINS[e["slot"][4:]]
                e["map_xy"] = [(px - MAP_CROP[0]) / (MAP_CROP[2] - MAP_CROP[0]),
                               (py - MAP_CROP[1]) / (MAP_CROP[3] - MAP_CROP[1])]
            els.append(e)
        tl["beats"].append({"id": b["id"], "t_in": tin, "t_out": tout,
                            "presenter": mode_of(plan, b), "pbox": presenter_box(mode_of(plan, b), b.get("hub") or (plan.get("card") if mode_of(plan, b) == "card" else plan.get("hub") if mode_of(plan, b) == "hub" else None)),
                            "flood": b.get("flood"), "broll": b.get("broll"), "plate": b.get("plate"), "tracker": b.get("tracker"), "spine": b.get("spine"),
                            "elements": els})
    if plan.get("tracker"):                       # the points-done list in the corner, from this cue on
        tr = plan["tracker"] if isinstance(plan["tracker"], dict) else {}
        tl["tracker"] = {"show_t": ref(tr.get("from", 0)), "items": tr.get("items")}
    for i, l in enumerate(lines):
        tl["captions"].append({"t0": l["t0"], "t1": l["t1"], "text": l["text"]})
    return tl


def icons(plan):
    """Inline every icon the plan names ('tabler:shirt', 'ph:cow') as SVG text."""
    names = set(re.findall(r'"((?:tabler|tablerf|ph):[a-z0-9-]+)"', json.dumps(plan)))
    if '"badge"' in json.dumps(plan):
        names |= {"tabler:camera"}
    if '"igsave"' in json.dumps(plan):
        names |= {"tabler:bookmark", "tablerf:bookmark"}
    names |= {"tabler:check", "tabler:x", "tabler:droplet", "tabler:plant-2"}   # used by templates themselves
    out = {}
    for n in names:
        lib, name = n.split(":")
        f = (ROOT / "library/elements/vendor/tabler/icons/outline" / f"{name}.svg" if lib == "tabler"
             else ROOT / "library/elements/vendor/tabler/icons/filled" / f"{name}.svg" if lib == "tablerf"
             else ROOT / "library/elements/vendor/phosphor/assets/regular" / f"{name}.svg")
        out[n] = re.sub(r'<!--.*?-->', '', f.read_text(), flags=re.S)
    return out


def beat_at(tl, t):
    for b in tl["beats"]:
        if b["t_in"] <= t < b["t_out"]:
            return b
    return tl["beats"][-1]


def still_bg(tl, b, t, proj, out):
    """The full-frame background a still shows at t: the beat's broll frame, else its plate, else the plan plate."""
    br = b.get("broll") or {}
    if br.get("clip"):
        src = clip_path(proj, br["clip"])
        if src.exists():
            raw = grab(src, br.get("offset", 0) + 0.5, vf="scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920")
            return Image.frombytes("RGB", (W, H), raw)
    name = b.get("plate") or tl.get("plate")
    f = ROOT / "library/backgrounds/plates/generated" / f"{name}.jpg"
    return Image.open(f).convert("RGB").resize((W, H)) if f.exists() else Image.new("RGB", (W, H), (230, 236, 245))


def prep_still(tl, t, proj, out):
    """Write the presenter cut and b-roll frame for time t; return their paths."""
    out.mkdir(parents=True, exist_ok=True)
    b = beat_at(tl, t)
    pb = b["pbox"]
    raw = grab(proj / f"src/part{tl.get('part', 1)}.mp4", t,
               vf=f"crop={CW}:{CH}:{CROP[0]}:{CROP[1]}")
    cut = grade(key_np(raw), tl.get("presenter_grade")).resize((pb["w"], pb["h"]), Image.LANCZOS)
    if tl.get("scene_match") and not (pb.get("card") or pb.get("hub")):
        cut = scene_match(cut, still_bg(tl, b, t, proj, out).crop((pb["x"], pb["y"], pb["x"] + pb["w"], pb["y"] + pb["h"])), tl["scene_match"])
    pres = out / f"presenter_{t:07.2f}.png"
    cut.save(pres)
    assets = {"presenter": pres.name}
    if b.get("broll"):
        br = b["broll"]
        span = b["t_out"] - b["t_in"]
        src_ = clip_path(proj, br.get("clip"))
        clen = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(src_)],
                                    capture_output=True, text=True).stdout or 10.0) if br.get("clip") and src_.exists() else 10.0
        avail = clen - br.get("offset", 0) - 0.3        # 8 s or 10 s clips: slow by the real length, never reverse
        rate = min(1.0, avail / max(span, 0.1))
        local = br.get("offset", 0) + (t - b["t_in"]) * rate
        if br.get("span"):                                  # compose.py maps this stretch of the clip onto the beat
            a_, z_ = br["span"]
            local = a_ + (t - b["t_in"]) * (z_ - a_) / max(span, 0.1)
        local = min(local, clen - 0.3)
        if br.get("photo"):                       # a real photograph instead of a clip
            im = Image.open(ROOT / "library/backgrounds/photos" / br["photo"]).convert("RGB")
            im.thumbnail((1400, 1400)); im.save(out / f"broll_{t:07.2f}.jpg", quality=90)
        else:
            src = clip_path(proj, br["clip"])
            if not src.exists():                  # not generated yet: the still shows the plate
                return assets
            raw = grab(src, local, vf="scale=720:1280")
            Image.frombytes("RGB", (720, 1280), raw).save(out / f"broll_{t:07.2f}.jpg", quality=90)
        assets["broll"] = f"broll_{t:07.2f}.jpg"
    return assets


def shared_assets(proj, out, plan):
    out.mkdir(parents=True, exist_ok=True)
    if (proj / "work/card_cut.png").exists():
        card = Image.open(proj / "work/card_cut.png")
        card.crop(card.getbbox()).save(out / "card.png")
    for bt in plan["beats"]:                      # photo b-roll is drawn by the page itself in a render
        ph = (bt.get("broll") or {}).get("photo")
        if ph:
            im = Image.open(ROOT / "library/backgrounds/photos" / ph).convert("RGB")
            im.thumbnail((1400, 1400)); im.save(out / f"bp_{Path(ph).stem}.jpg", quality=90)
    for bt in plan["beats"]:                      # photo clippings named by the plan
        bd = (bt.get("hub") or plan.get("hub") or {}).get("backdrop")
        if bd and bd.startswith("veo:"):           # a frame of one of this video's own clips
            cid, at = (bd[4:].split("@") + ["4"])[:2]
            src = clip_path(proj, cid)
            if src.exists():
                Image.frombytes("RGB", (720, 1280), grab(src, float(at), vf="scale=720:1280")).save(out / f"bd_{cid}.png")
        elif bd and bd != "plate":
            im = Image.open(ROOT / "library/backgrounds/photos" / bd).convert("RGB")
            im.thumbnail((900, 900)); im.save(out / (Path(bd).stem + ".png"))
        for e in bt["elements"]:
            if e["type"] == "qsheet":                    # the question on the torn exam sheet (keep its transparent edges)
                Image.open(proj / e["src_path"]).save(out / Path(e["src_path"]).name)
                continue
            if e["type"] == "papers" and e.get("assets"):   # the real-paper look: paper texture + one QR per year
                for f in (proj / e["assets"]).glob("*.png"):     # keep alpha: the sheets have torn, transparent edges
                    Image.open(f).save(out / f.name)
                continue
            if e["type"] == "page":                      # a full-frame answer page from the project (to_full_page output)
                Image.open(proj / e["src"]).convert("RGB").save(out / (Path(e["src"]).stem + ".png"))
                continue
            if e["type"] == "rewrite":                   # each substitution's photo (where its number comes from)
                for sub in e.get("subs", []):
                    im = Image.open(ROOT / "library/backgrounds/photos" / sub[0]).convert("RGB")
                    im.thumbnail((600, 600)); im.save(out / (Path(sub[0]).stem + ".png"))
                continue
            if e["type"] == "portraits":                 # each framed painting: [photo, name, sub, cue]
                for it in e["items"]:
                    im = Image.open(ROOT / "library/backgrounds/photos" / it[0]).convert("RGB")
                    im.thumbnail((700, 700)); im.save(out / ("pt_" + Path(it[0]).stem + ".png"))
                continue
            if e["type"] in ("photo", "inset"):
                im = Image.open(ROOT / "library/backgrounds/photos" / e["src"]).convert("RGB")
                if e.get("crop_bottom"):
                    im = im.crop((0, 0, im.width, round(im.height * (1 - e["crop_bottom"]))))
                im.thumbnail((900, 900)); im.save(out / (Path(e["src"]).stem + ".png"))
    if plan.get("question_sheet"):
        sh = Image.open(ROOT / plan["question_sheet"])
        sh.crop(sh.getbbox()).save(out / "sheet.png")
    for name, atlas in (("map-peninsula-1", "atlas_1"), ("map-peninsula-2", "atlas_2")):
        if not (proj / f"assets/maps/{atlas}.mp4").exists():
            continue
        raw = subprocess.run(["ffmpeg", "-v", "error", "-sseof", "-0.1", "-i",
                              str(proj / f"assets/maps/{atlas}.mp4"), "-frames:v", "1",
                              "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                             capture_output=True, check=True).stdout
        Image.frombytes("RGB", (W, H), raw).crop(MAP_CROP).save(out / f"{name}.png")
    return {p.stem: list(Image.open(p).size) for p in out.glob("*.png")
            if not p.name.startswith(("presenter_", "broll_"))}


def visual_changes(tl):
    """Every moment the picture changes: a cut, an element landing, a list item, a year, a cue inside an element."""
    ts = {b["t_in"] for b in tl["beats"]}
    for b in tl["beats"]:
        for e in b["elements"]:
            ts.add(e.get("t", b["t_in"]))
            ts.update(v for k, v in e.items() if k.startswith("t_") and isinstance(v, (int, float)) and v < 1e5)
            for key in ("items", "stops", "years", "lines", "steps", "subs", "legend"):
                ts.update(it[-1] for it in e.get(key, []) if isinstance(it, list) and isinstance(it[-1], (int, float)) and it[-1] < 1e5)
    ts.update(tl["spine"]["lit_t"])
    return sorted(t for t in ts if 0 <= t <= tl["duration"])


def gates(plan, tl):
    """Checks learned from reviewing a competing edit of the Mohenjo-daro reel (HIN-SM-02 T01, 19 Oct 2026).
    GATES refuse to compile; WARNINGS print and let the plan through, because a hold is sometimes right."""
    # GATE hook_visual: the first frame is a moving picture, not a title card over a talking head
    first = tl["beats"][0]
    if plan.get("hook") != "exempt" and not (first.get("broll") or {}).get("clip") and plan.get("part", 1) > 1:
        print("WARN hook_visual: this part opens without a Veo clip (a gate on part 1, a warning after it)", file=sys.stderr)
    elif plan.get("hook") != "exempt" and not (first.get("broll") or {}).get("clip"):
        raise SystemExit("GATE hook_visual: the video opens without a Veo clip; give the first beat a broll clip "
                         "(the visual hook) or set \"hook\": \"exempt\" in the plan and say why in _about")
    # GATE no_em_dash: screen text never carries an em-dash (memory: screen-text-conventions)
    def strings(v):
        if isinstance(v, str): yield v
        elif isinstance(v, list):
            for x in v: yield from strings(x)
        elif isinstance(v, dict):
            for k, x in v.items():
                if k not in ("src", "sfx", "fx"): yield from strings(x)
    dashed = sorted({f"{b['id']}: {s_}" for b in tl["beats"] for e in b["elements"] for s_ in strings(e) if "\u2014" in s_})
    if dashed:
        raise SystemExit("GATE no_em_dash: screen text with an em-dash:\n  " + "\n  ".join(dashed))
    # WARN long_hold: Instagram retention wants a new picture every few seconds
    ch = visual_changes(tl) + [tl["duration"]]
    holds = [(a, b) for a, b in zip(ch, ch[1:]) if b - a > plan.get("max_hold", 6.0)]
    for a, b in holds:
        print(f"WARN long_hold: nothing changes on screen {a:.1f}s to {b:.1f}s ({b - a:.1f}s)", file=sys.stderr)
    # WARN dead_air: a beat with no footage and nothing on it
    for b in tl["beats"]:
        if not b["elements"] and not (b.get("broll") or {}).get("clip") and b["t_out"] - b["t_in"] > 2.0:
            print(f"WARN dead_air: beat {b['id']} is {b['t_out'] - b['t_in']:.1f}s of plate with nothing on it", file=sys.stderr)


def main(argv):
    plan_p = Path(argv[0])
    plan = json.loads(plan_p.read_text())
    proj = ROOT / "projects" / plan["project"]
    meta = json.loads((proj / "meta.json").read_text())
    lt = json.loads((proj / f"lines_part{plan['part']}.json").read_text())
    if isinstance(lt, list):                 # tools/lines_from_srt.py format
        dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                    str(proj / f"src/part{plan['part']}.mp4")], capture_output=True, text=True).stdout)
        lt = {"duration": dur, "lines": [{"t0": l["start"], "t1": l["end"], "text": l["text"]} for l in lt]}
    plan["hilite"] = meta.get("hilite", [])
    set_framing(plan.get("framing"))
    FACE_IN_CROP[0] = measure_centre(proj, plan["part"])     # centre him on screen in every mode
    tl = resolve(plan, lt["lines"], lt["duration"])
    tl["part"] = plan["part"]
    pf = ROOT / "library/backgrounds/plates/generated" / f"{plan['plate']}.jpg"
    tl["plate_path"] = f"generated/{plan['plate']}.jpg" if pf.exists() else None
    tl["presenter_grade"] = plan.get("presenter_grade")
    tl["scene_match"] = plan.get("scene_match")
    tl["framing"] = plan.get("framing")    # colour, lighting and edge fixes for the keyed presenter
    tl["card_style"] = plan.get("card_style")             # the presenter card's topic frame and backdrop
    tl["captions_at"] = plan.get("captions_at")          # "bottom": the caption never moves
    if "captions_from" in plan:              # no captions until this caption line (e.g. after the question card)
        tl["captions_from"] = lt["lines"][plan["captions_from"]]["t0"] - 0.05
    # GATE: captions never run under the question card.  Without an explicit start, they begin
    # the moment the last question-card beat ends; an explicit start before that refuses to compile.
    q_end = max((b["t_out"] for b in tl["beats"] for e in b["elements"]
                 if e["type"] in ("qcard", "qsheet") or (e["type"] == "qhero" and e.get("question"))), default=None)
    if q_end is not None:
        if "captions_from" not in tl:
            tl["captions_from"] = q_end
        elif tl["captions_from"] < q_end - 0.1:
            raise SystemExit(f"GATE caption_after_question: captions start at {tl['captions_from']:.2f}s but the "
                             f"question card runs until {q_end:.2f}s — drop captions_from or move it after the card")
    tl["q_end"] = q_end
    gates(plan, tl)
    tl["spine"]["title"] = plan["spine"]["title"]
    tl["icons"] = icons(plan)
    if '"seamap"' in json.dumps(plan):                # every base map the plan names; "sea-route" by default
        names = {e.get("map", "sea-route") for b in plan["beats"] for e in b["elements"] if e["type"] == "seamap"}
        tl["seamaps"] = {m: json.loads((ROOT / f"library/elements/maps/{m}.json").read_text()) for m in names}
    states = {e["state"] for b in plan["beats"] for e in b["elements"] if e["type"] == "statemap"}
    if states:                                        # one Indian state's outline (Natural Earth, public domain), normalised to 0..1
        gj = json.loads((ROOT / "map_engine/data/derived/india_states.geojson").read_text())
        tl["shapes"] = {}
        for f in gj["features"]:
            if f["properties"]["name"] in states:
                g = f["geometry"]; rings = g["coordinates"] if g["type"] == "Polygon" else [p_[0] for p_ in g["coordinates"]]
                ring = max(rings, key=len) if g["type"] == "Polygon" else max(rings, key=len)
                import math
                lat0 = sum(y for _, y in ring) / len(ring); k = math.cos(math.radians(lat0))
                xs = [x * k for x, _ in ring]; ys = [-y for _, y in ring]
                x0, y0, sc = min(xs), min(ys), max(max(xs) - min(xs), max(ys) - min(ys))
                tl["shapes"][f["properties"]["name"]] = {"pts": [[round((x - x0) / sc, 4), round((y - y0) / sc, 4)] for x, y in zip(xs, ys)],
                                                       "aspect": round((max(ys) - min(ys)) / (max(xs) - min(xs)), 4)}
    lot = {e["src"] for b in plan["beats"] for e in b["elements"] if e["type"] == "lottie"}     # free Lottie animations the plan names
    tl["lotties"] = {k: json.loads((ROOT / f"library/elements/lottie/{k}.json").read_text()) for k in lot}
    shots = proj / "veo/shots.json"              # what each clip is meant to show, for plan views
    tl["shots"] = json.loads(shots.read_text()) if shots.exists() else {}
    out = HERE / "out" / plan_p.stem
    tl["dims"] = shared_assets(proj, out / "assets", plan)
    stills = []
    if "--stills" in argv:
        spec = argv[argv.index("--stills") + 1]
        # "auto": one still per beat, half a second before it ends, when everything has landed
        ts = ([round(b["t_out"] - 0.5, 2) for b in tl["beats"]] if spec == "auto"
              else [float(x) for x in spec.split(",")])
        for t in ts:
            stills.append({"t": t, **prep_still(tl, t, proj, out / "assets")})
    tl["stills"] = stills
    (out / "timeline.js").write_text("window.TL = " + json.dumps(tl, ensure_ascii=False, indent=1) + ";\n")
    print(out)


if __name__ == "__main__":
    main(sys.argv[1:])
