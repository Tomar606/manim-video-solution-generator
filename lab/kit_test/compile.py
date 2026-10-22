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
    "standard": (1000, 560),
    "small": (820, 600),
    "full": (1000, 560),           # free-standing even under presenter_style "card": the story beats (a walk, a zoom)
}

# Map crop: the peninsula only.  The project's atlas draws India's de facto
# northern boundary, which must never appear on screen, so the crop starts
# well south of it (y >= 700 of the 1080x1920 atlas).
MAP_CROP = (60, 700, 1020, 1340)
MAP_PINS = {"hyderabad": (539, 1013), "junagadh": (314, 890)}


FACE_IN_CROP = (316, 150)           # his face centre inside the crop, measured off the plate


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
    return {"x": round(cx - w / 2), "y": top, "w": w, "h": h,
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


def grab(src, t, vf=None, w=None, h=None):
    args = ["ffmpeg", "-v", "error", "-threads", "2", "-ss", f"{t:.3f}", "-i", str(src),
            "-frames:v", "1"]
    if vf:
        args += ["-vf", vf]
    args += ["-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    return subprocess.run(args, capture_output=True, check=True).stdout


def mode_of(plan, b):
    """A plan may restyle every standing beat at once ("presenter_style": "card")."""
    if plan.get("presenter_style") == "card" and b["presenter"] in ("standard", "small", "hero"):
        return "card"
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
                if key in e and e["type"] in ("pills", "chain", "radial", "cards3", "seasons", "quad", "tiles", "bars", "dots100", "timeline", "notify", "pins"):
                    e[key] = [list(it[:-1]) + [ref(it[-1], tin)] for it in e[key]]
                    e.setdefault("t", e[key][0][-1])
            if e["type"] == "qhero":                     # years: [label, cue]
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
            if e["type"] in ("ring", "pins", "qmarks", "verdict", "lottie"):   # placed by frame coordinates, not by slot
                e.setdefault("slot", "over-broll")
            if e["slot"].startswith("map:"):
                px, py = MAP_PINS[e["slot"][4:]]
                e["map_xy"] = [(px - MAP_CROP[0]) / (MAP_CROP[2] - MAP_CROP[0]),
                               (py - MAP_CROP[1]) / (MAP_CROP[3] - MAP_CROP[1])]
            els.append(e)
        tl["beats"].append({"id": b["id"], "t_in": tin, "t_out": tout,
                            "presenter": mode_of(plan, b), "pbox": presenter_box(mode_of(plan, b), b.get("hub") or (plan.get("card") if mode_of(plan, b) == "card" else None)),
                            "flood": b.get("flood"), "broll": b.get("broll"), "plate": b.get("plate"), "tracker": b.get("tracker"),
                            "elements": els})
    if plan.get("tracker"):                       # the points-done list in the corner, from this cue on
        tr = plan["tracker"] if isinstance(plan["tracker"], dict) else {}
        tl["tracker"] = {"show_t": ref(tr.get("from", 0)), "items": tr.get("items")}
    for i, l in enumerate(lines):
        tl["captions"].append({"t0": l["t0"], "t1": l["t1"], "text": l["text"]})
    return tl


def icons(plan):
    """Inline every icon the plan names ('tabler:shirt', 'ph:cow') as SVG text."""
    names = set(re.findall(r'"((?:tabler|ph):[a-z0-9-]+)"', json.dumps(plan)))
    names |= {"tabler:check", "tabler:x", "tabler:droplet", "tabler:plant-2"}   # used by templates themselves
    out = {}
    for n in names:
        lib, name = n.split(":")
        f = (ROOT / "library/elements/vendor/tabler/icons/outline" / f"{name}.svg" if lib == "tabler"
             else ROOT / "library/elements/vendor/phosphor/assets/regular" / f"{name}.svg")
        out[n] = re.sub(r'<!--.*?-->', '', f.read_text(), flags=re.S)
    return out


def beat_at(tl, t):
    for b in tl["beats"]:
        if b["t_in"] <= t < b["t_out"]:
            return b
    return tl["beats"][-1]


def prep_still(tl, t, proj, out):
    """Write the presenter cut and b-roll frame for time t; return their paths."""
    out.mkdir(parents=True, exist_ok=True)
    b = beat_at(tl, t)
    pb = b["pbox"]
    raw = grab(proj / f"src/part{tl.get('part', 1)}.mp4", t,
               vf=f"crop={CW}:{CH}:{CROP[0]}:{CROP[1]}")
    cut = key_np(raw).resize((pb["w"], pb["h"]), Image.LANCZOS)
    pres = out / f"presenter_{t:07.2f}.png"
    cut.save(pres)
    assets = {"presenter": pres.name}
    if b.get("broll"):
        br = b["broll"]
        span = b["t_out"] - b["t_in"]
        src_ = proj / f"veo/clean/{br.get('clip')}.mp4"
        clen = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(src_)],
                                    capture_output=True, text=True).stdout or 10.0) if br.get("clip") and src_.exists() else 10.0
        avail = clen - br.get("offset", 0) - 0.3        # 8 s or 10 s clips: slow by the real length, never reverse
        rate = min(1.0, avail / max(span, 0.1))
        local = br.get("offset", 0) + (t - b["t_in"]) * rate
        local = min(local, clen - 0.3)
        if br.get("photo"):                       # a real photograph instead of a clip
            im = Image.open(ROOT / "library/backgrounds/photos" / br["photo"]).convert("RGB")
            im.thumbnail((1400, 1400)); im.save(out / f"broll_{t:07.2f}.jpg", quality=90)
        else:
            src = proj / f"veo/clean/{br['clip']}.mp4"
            if not src.exists():
                src = proj / f"veo/clips/{br['clip']}.mp4"
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
        bd = (bt.get("hub") or {}).get("backdrop")
        if bd and bd.startswith("veo:"):           # a frame of one of this video's own clips
            cid, at = (bd[4:].split("@") + ["4"])[:2]
            src = proj / f"veo/clean/{cid}.mp4"
            src = src if src.exists() else proj / f"veo/clips/{cid}.mp4"
            if src.exists():
                Image.frombytes("RGB", (720, 1280), grab(src, float(at), vf="scale=720:1280")).save(out / f"bd_{cid}.png")
        elif bd and bd != "plate":
            im = Image.open(ROOT / "library/backgrounds/photos" / bd).convert("RGB")
            im.thumbnail((900, 900)); im.save(out / (Path(bd).stem + ".png"))
        for e in bt["elements"]:
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
            for key in ("items", "stops", "years"):
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
    tl = resolve(plan, lt["lines"], lt["duration"])
    tl["part"] = plan["part"]
    pf = ROOT / "library/backgrounds/plates/generated" / f"{plan['plate']}.jpg"
    tl["plate_path"] = f"generated/{plan['plate']}.jpg" if pf.exists() else None
    tl["captions_at"] = plan.get("captions_at")          # "bottom": the caption never moves
    if "captions_from" in plan:              # no captions until this caption line (e.g. after the question card)
        tl["captions_from"] = lt["lines"][plan["captions_from"]]["t0"] - 0.05
    # GATE: captions never run under the question card.  Without an explicit start, they begin
    # the moment the last question-card beat ends; an explicit start before that refuses to compile.
    q_end = max((b["t_out"] for b in tl["beats"] for e in b["elements"]
                 if e["type"] == "qcard" or (e["type"] == "qhero" and e.get("question"))), default=None)
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
