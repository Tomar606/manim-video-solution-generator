"""Join a project's Veo scenes into one reel, with transitions over every cut.

    python tools/veo_reel.py <slug> [--out final.mp4] [--only s01 s02] [--dry]

Reads projects/<slug>/reel.json:

    {"frame": "1080x1920", "fps": 30,
     "scenes": [{"id": "s01", "green": true, "transition": null},
                {"id": "s02", "green": true, "transition": "wnebe1_..._17"},
                ...]}

`transition` is the one laid over the cut INTO that scene, so the first scene's
is null. A name is looked up by tools/transition.py, which decides from the
folder whether it is screened (leak) or keyed (wipe).

WHAT EACH SCENE GOES THROUGH, and why in this order
---------------------------------------------------
1. DELOGO. Flow burns its sparkle in after generation, so no prompt prevents it
   (memory: flow-burns-an-ai-marker). It is covered first, while the clip is
   still at its native size — the box was measured in native pixels, and
   covering after a rescale smears it instead of replacing it.
2. KEY, for a scene marked `green`. Veo's "green screen" is a pale wall that
   neither ffmpeg keyer can separate; tools/key_veo_green.py keys it on green
   DOMINANCE and puts his colour back (memory: veo-green-wall-is-not-keyable).
   A green scene ends up at the reel's frame size, standing on the project's
   background.
3. FIT. Every other scene is scaled and padded to the reel's frame, because the
   bridge in a transition CONCATENATES two clips and they must match exactly.

ONE FPS FOR THE WHOLE REEL. Veo returns 24fps here and the rest of the pipeline
is 30; concatenating the two silently resamples at every join and the audio
drifts against the picture over twenty-one scenes. Everything is conformed once,
at the start, rather than wherever ffmpeg happens to notice.

HOW THE JOINING IS DONE, and why it is not the obvious way
----------------------------------------------------------
The obvious way is to join scene 1 to scene 2, then that to scene 3, and so on.
It is also quadratic: each join re-encodes the whole reel built so far, so the
last of twenty joins re-encodes three minutes of 1080x1920 and the run takes
twenty-five minutes. Measured on this project the joins ran 41s, 43s, 51s, 61s,
69s, 70s — growing by about seven seconds every time.

Nothing about a transition needs that. A transition only ever touches the
frames either side of ONE cut: it takes `pre` seconds off the end of the scene
before and `post` off the start of the scene after, and gives back a bridge of
exactly pre+post. Everything else in both scenes is untouched. So this cuts each
scene's MIDDLE (the part no transition reaches), builds each BRIDGE on its own
from just the two fragments it needs, and concatenates middle, bridge, middle,
bridge... in one pass with `-c copy`. Every segment is encoded once, by the same
encoder with the same settings, and the final concat re-encodes nothing.

Same output, about two minutes instead of twenty-five.

AND THE SCENES ARE LAYERED IN PARALLEL. Preparing a scene — trim and delogo,
key or fit, then captions, point and card — is three or four encodes of one
ten-second clip, and no scene depends on any other. Run one at a time they took
longer than the joins did. `--workers` runs them side by side; a finished
`<id>_fit.mp4` newer than everything that feeds it is reused, so a re-run after
changing one caption does not rebuild twenty-one scenes.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.transition import find as _find_tr, peak as _peak, sample as _sample  # noqa: E402
MARK = {"landscape": (1132, 572, 56, 56), "vertical": (576, 1131, 56, 56)}

# A CUT YOU CAN SEE AND NOT HEAR READS AS A GLITCH. The leak covers the join;
# the sound is what makes it read as an edit somebody made. Each scene names its
# own `sound`; these are the defaults when it does not, picked from the same
# meaning that picked the picture — a hard burn lands on an impact, the softest
# flash on the softest reveal.
#
# The cue goes at the CUT, which is the cumulative end of the scene before it:
# a transition takes `pre` seconds from A and `post` from B but gives the same
# total back, so the join never moves off the running total. And it peaks on the
# picture, not near it (memory: sound-comes-from-beats-not-captions).
# GAIN IS dB, NOT A MULTIPLIER. src/sfx.py mixes each cue with
# `volume={gain}dB` and its own default is -12. Written as 0.5 and 0.55 these
# read as half a decibel — no boost at all — so the cue sat at its raw level and
# the scene's own ambience buried it: measured across four cuts, only the one
# that happened to fall in a quiet moment showed any lift, and the other three
# came out 1 to 7 dB DOWN on the second before them. A transition you can see
# and not hear is the thing this was added to prevent.
# Measured by the other session on this repo: assets/sfx/whoosh.wav peaks
# INTERMEDIATES ENCODE FAST. Each scene is delogo'd, then fitted or keyed, then
# captioned — three encodes before the concat re-encodes it a fourth time. At
# preset medium that was most of the build's wall clock for no gain: the only
# encode a viewer ever sees is the last one, which is still medium.
FAST = ["-preset", "veryfast"]
# 0.120s in and has no registry entry to carry that offset, so mix_cues lands
# its START on the cut and its peak three frames after it. Until it has a
# proper `transition/` role in the registry, the cue is placed early by its
# own peak. impact peaks at 0.02s, which is close enough to zero.
PEAK_OF = {"whoosh": 0.120, "impact": 0.020}
SOUND_FOR = {
    "halation_flash": ("reveal", -6.0),
    "leak_warm_sweep": ("whoosh", -4.0),
    "film_burn_corner": ("whoosh", -4.0),
}
DEFAULT_SOUND = ("whoosh", -4.0)
# Where the caption's BASELINE sits, as a share of frame height. Low enough to
# stay inside the vignette, high enough to clear a phone's home indicator.
CAP_BOTTOM = 0.915
# The point sits at the TOP, inside its own scrim, and comes up a beat after the
# scene starts so the shot registers before text lands on it.
PT_TOP = 0.045
PT_IN = 0.60
POP_STEP = 0.085         # how long each chakra pop frame is held
NOTE_Y = 0.775           # the scene note, above the caption and clear of it
# The closing card is not a tracker in the corner; it is the answer, and it sits
# where the eye already is rather than tucked under the top edge.
RECAP_Y = 0.20
NOTE_IN = 0.45           # a beat after the cut, so the shot registers first
PT_H = 61                # the settled strip's height, so a swollen frame grows
                         # about its own centre instead of dropping downwards
HARD_SOUND = ("impact", -2.0)      # for the burns that mark a turn or a year
WIPE_SOUND = ("page_swoosh", -4.0)


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(f"  failed: {' '.join(str(c) for c in cmd[:6])}...\n{r.stderr[-800:]}")
    return r


def probe(p: Path) -> dict:
    out = run(["ffprobe", "-v", "error", "-show_entries",
               "format=duration:stream=codec_type,width,height", "-of", "json", str(p)]).stdout
    doc = json.loads(out)
    v = next((s for s in doc["streams"] if s.get("codec_type") == "video"), {})
    return {"dur": float(doc["format"]["duration"]), "w": v.get("width"), "h": v.get("height"),
            "audio": any(s.get("codec_type") == "audio" for s in doc["streams"])}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--out", default="")
    ap.add_argument("--only", nargs="*", default=[])
    ap.add_argument("--dry", action="store_true", help="say what would happen, build nothing")
    ap.add_argument("--opacity", type=float, default=0.72)
    # WORKERS ARE NOT FREE THREADS. Each one runs its own ffmpeg, and ffmpeg
    # decides its own thread count from the core count — so N workers is not N
    # threads, it is N x cores. Run at 8 on an 8-core machine this drove the
    # load average to 26 and took the whole machine down twice. Half the cores,
    # capped, leaves headroom for everything else the build needs.
    ap.add_argument("--workers", type=int,
                    default=max(2, min(4, (os.cpu_count() or 4) // 2)),
                    help="scenes prepared side by side; they do not depend on each other")
    ap.add_argument("--rebuild", action="store_true",
                    help="re-prepare every scene even if its output is already current")
    a = ap.parse_args()

    proj = ROOT / "projects" / a.slug
    spec = json.loads((proj / "reel.json").read_text(encoding="utf-8"))
    FW, FH = (int(v) for v in spec.get("frame", "1080x1920").lower().split("x"))
    fps = int(spec.get("fps", 30))
    bg = proj / spec.get("background", "assets/background.png")
    clips = proj / "veo" / "clips"
    work = proj / "work" / "reel"
    work.mkdir(parents=True, exist_ok=True)
    out = Path(a.out) if a.out else proj / "final" / f"{a.slug.replace('-', '_')}.mp4"
    out.parent.mkdir(parents=True, exist_ok=True)

    caps = json.loads((proj / "captions.json").read_text(encoding="utf-8")) \
        if (proj / "captions.json").is_file() else {}
    vig = proj / "work" / "captions" / "vignette.png"
    card = proj / "work" / "card.png"
    pts = proj / "work" / "points"
    recap = json.loads((proj / "recap.json").read_text(encoding="utf-8")) \
        if (proj / "recap.json").is_file() else None
    rdir = proj / "work" / "recap"
    scenes = [s for s in spec["scenes"] if not a.only or s["id"] in a.only]
    missing = [s["id"] for s in scenes if not (clips / f"{s['id']}.mp4").is_file()]
    if missing:
        print(f"  not downloaded yet: {', '.join(missing)}")
        return 1
    if a.dry:
        for i, s in enumerate(scenes):
            t = s.get("transition")
            print(f"  {s['id']}  {'green->background' if s.get('green') else 'full frame'}"
                  + (f"   <- {t}" if t else "   (opens the reel)"))
        return 0

    # ---- 1..3: every scene conformed to one frame, one fps, sparkle covered --
    def prepare(s):
        src = clips / f"{s['id']}.mp4"
        info = probe(src)
        x, y, w, h = MARK["vertical" if info["h"] > info["w"] else "landscape"]
        clean = work / f"{s['id']}_clean.mp4"
        # THE TRIM COMES OFF FIRST, with the sparkle, so everything after it —
        # captions, the card, the transitions' borrowed frames — is measured
        # against the clip the viewer actually sees. tools/reel_trim.py only
        # ever takes silence, and leaves a handle at each end so the shot still
        # establishes and still lands.
        head, tail = (s.get("trim") or [0.0, 0.0])[:2]
        keep = info["dur"] - float(head) - float(tail)
        run(["ffmpeg", "-v", "error", "-y", "-ss", f"{float(head):.3f}", "-i", str(src),
             "-t", f"{keep:.3f}",
             "-vf", f"delogo=x={x}:y={y}:w={w}:h={h}", "-c:v", "libx264", "-preset", "veryfast",
             "-crf", "16", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
             "-ar", "48000", str(clean)])
        dst = work / f"{s['id']}_fit.mp4"
        if s.get("green"):
            run([sys.executable, str(ROOT / "tools" / "key_veo_green.py"), str(clean),
                 str(bg), str(dst), "--frame", f"{FW}x{FH}",
                 *(["--width", str(s["width"])] if s.get("width") else [])])
            # key_veo_green keeps the source fps; conform it like the rest
            tmp = work / f"{s['id']}_fit30.mp4"
            run(["ffmpeg", "-v", "error", "-y", "-i", str(dst), "-r", str(fps),
                 "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "-pix_fmt", "yuv420p",
                 "-c:a", "copy", str(tmp)])
            tmp.replace(dst)
        else:
            # A CINEMATIC SCENE: the picture comes from the b-roll clip and the
            # NARRATION STAYS his. `broll` names a silent clip with no presenter
            # in it; the audio is the presenter take generated for this very
            # scene, which is why all 23 takes exist even though he is on screen
            # in 15. Cutting away therefore costs no extra voice — the clip we
            # already paid for keeps talking underneath.
            #
            # The b-roll is 10.01s like everything Veo makes; if the trimmed
            # narration is shorter the picture is cut to match, and if it is
            # longer the last frame holds. Never reversed to fill a gap
            # (memory: veo-clips-fit-the-avatar).
            bname = s.get("broll")
            bsrc = clips / f"{bname}.mp4" if bname else None
            if bsrc and bsrc.is_file():
                bclean = work / f"{s['id']}_broll.mp4"
                bx, by, bw, bh = MARK["vertical"]
                run(["ffmpeg", "-v", "error", "-y", "-i", str(bsrc),
                     "-vf", f"delogo=x={bx}:y={by}:w={bw}:h={bh},"
                            f"scale={FW}:{FH}:force_original_aspect_ratio=increase,"
                            f"crop={FW}:{FH},fps={fps},tpad=stop_mode=clone:stop_duration=6",
                     "-t", f"{keep:.3f}", "-an",
                     "-c:v", "libx264", "-preset", "veryfast", "-crf", "16",
                     "-pix_fmt", "yuv420p", str(bclean)])
                run(["ffmpeg", "-v", "error", "-y", "-i", str(bclean), "-i", str(clean),
                     "-map", "0:v:0", "-map", "1:a:0", "-shortest",
                     "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                     str(dst)])
                print(f"  {s['id']}: cinematic {bname} over his narration")
            else:
                if bname:
                    print(f"  {s['id']}: broll {bname}.mp4 missing — using his picture")
                run(["ffmpeg", "-v", "error", "-y", "-i", str(clean), "-vf",
                     f"scale={FW}:{FH}:force_original_aspect_ratio=increase,"
                     f"crop={FW}:{FH},fps={fps}",
                     "-c:v", "libx264", "-preset", "veryfast", "-crf", "16",
                     "-pix_fmt", "yuv420p",
                     "-c:a", "aac", "-b:a", "192k", "-ar", "48000", str(dst)])
        # ---- the caption layer, and the card over the opening ------------
        evs = caps.get(s["id"], [])
        want_card = bool(s.get("card")) and card.is_file()
        # THE STEP STRIP WINS OVER THE POINT. Both live at the top of the
        # frame on the same scrim, so drawing both stacks two gold lines over
        # his hair. The strip carries the point's job (what this scene is) and
        # adds the one the point could not do — how many causes there are and
        # which one we are in (tools/reel_steps.py).
        # ON THE CLOSING PLATE THE WHOLE ANSWER REPLACES THE FRACTION. Through
        # the body the tracker must be small because the picture is full-frame;
        # on the closing scenes he is keyed small and the top is empty, so the
        # five rows go up instead and the chakra comes off. Two trackers saying
        # the same thing in the same corner is worse than either alone.
        rc_png = proj / "work" / "recaplist" / f"{s['id']}.png"
        stp_png = proj / "work" / "steps" / f"{s['id']}.png"
        if rc_png.is_file():
            pt_png = rc_png
        else:
            pt_png = stp_png if stp_png.is_file() else pts / f"{s['id']}.png"
        pt_vig = pts / "vignette_top.png"
        want_pt = pt_png.is_file() and pt_vig.is_file()
        # the recap list: fills in on its own scene, stays whole on the holds
        rc_states = []
        if recap and rdir.is_dir():
            if s["id"] == recap["scene"]:
                st = recap["starts"]
                for k in range(1, recap["n"] + 1):
                    t0 = st[k - 1]
                    t1 = st[k] if k < recap["n"] else 10_000
                    rc_states.append((rdir / f"state_{k}.png", t0, t1))
                rc_states.insert(0, (rdir / "state_0.png", 0.0, st[0]))
            elif s["id"] in recap.get("hold", []):
                held = rdir / "state_all.png"
                if not held.is_file():
                    held = rdir / f"state_{recap['n']}.png"
                rc_states.append((held, 0.0, 10_000))
        if (evs and vig.is_file()) or want_card or want_pt or rc_states:
            lay = work / f"{s['id']}_cap.mp4"
            ins, fc, cur, n = [], [], "[0:v]", 1
            if evs and vig.is_file():
                ins += ["-i", str(vig)]
                fc.append(f"{cur}[{n}:v]overlay=0:0[v{n}]")
                cur, n = f"[v{n}]", n + 1
                for ev in evs:
                    ins += ["-i", str(proj / ev["png"])]
                    fc.append(f"{cur}[{n}:v]overlay=x=(W-w)/2:"
                              f"y={CAP_BOTTOM}*H-h:"
                              f"enable='between(t,{ev['start']:.2f},{ev['end']:.2f})'[v{n}]")
                    cur, n = f"[v{n}]", n + 1
            if want_pt:
                # the scrim first, then the point on top of it, both held from
                # PT_IN to the end of the scene — the point is what the student
                # copies down, so it stays up rather than flashing past
                ins += ["-i", str(pt_vig)]
                fc.append(f"{cur}[{n}:v]overlay=0:0:enable='gte(t,{PT_IN})'[v{n}]")
                cur, n = f"[v{n}]", n + 1
                # THE POP, where the chakra advances: a few frames of swell and
                # glow before the settled strip takes over. Each frame is held
                # for POP_STEP and centred like the strip, so the wheel grows
                # about its own middle rather than jumping sideways.
                pops = [] if rc_png.is_file() else \
                    sorted((proj / "work" / "steps").glob(f"{s['id']}_pop*.png"))
                t = PT_IN
                for pf in pops:
                    ins += ["-i", str(pf)]
                    fc.append(f"{cur}[{n}:v]overlay=x=(W-w)/2:"
                              f"y={PT_TOP}*H-(h-{PT_H})/2:"
                              f"enable='between(t,{t:.3f},{t + POP_STEP:.3f})'[v{n}]")
                    cur, n = f"[v{n}]", n + 1
                    t += POP_STEP
                ins += ["-i", str(pt_png)]
                y_top = RECAP_Y if rc_png.is_file() else PT_TOP
                fc.append(f"{cur}[{n}:v]overlay=x=(W-w)/2:y={y_top}*H:"
                          f"enable='gte(t,{t:.3f})'[v{n}]")
                cur, n = f"[v{n}]", n + 1
            # THE SCENE NOTE, on a cutaway only. It sits above the caption,
            # below the picture's middle, so the three overlays stack in the
            # order the eye reads them: tracker at the top, note, caption.
            note_png = proj / "work" / "notes" / f"{s['id']}.png"
            if note_png.is_file():
                ins += ["-i", str(note_png)]
                fc.append(f"{cur}[{n}:v]overlay=x=(W-w)/2:y={NOTE_Y}*H:"
                          f"enable='gte(t,{NOTE_IN})'[v{n}]")
                cur, n = f"[v{n}]", n + 1
            if want_card:
                ins += ["-i", str(card)]
                fc.append(f"{cur}[{n}:v]overlay=0:0[v{n}]")
                cur, n = f"[v{n}]", n + 1
            for png, t0, t1 in rc_states:
                ins += ["-i", str(png)]
                fc.append(f"{cur}[{n}:v]overlay=0:0:enable='between(t,{t0:.2f},{t1:.2f})'[v{n}]")
                cur, n = f"[v{n}]", n + 1
            run(["ffmpeg", "-v", "error", "-y", "-i", str(dst), *ins,
                 "-filter_complex", ";".join(fc), "-map", cur, "-map", "0:a?",
                 "-c:v", "libx264", "-preset", "veryfast", "-crf", "16",
                 "-pix_fmt", "yuv420p", "-c:a", "copy", str(lay)])
            lay.replace(dst)
        print(f"  {s['id']}: {'keyed onto the background' if s.get('green') else 'fitted'}"
              f" -> {probe(dst)['dur']:.2f}s"
              + (f", {len(evs)} caption(s)" if evs else "")
              + ("  + point" if want_pt else "")
              + ("  + question card" if want_card else "")
              + (f"  + recap ({len(rc_states)} state(s))" if rc_states else ""))
        dst.with_suffix(".sig").write_text(
            json.dumps({k: s.get(k) for k in ("green", "width", "card", "point", "trim")},
                       ensure_ascii=False, sort_keys=True), encoding="utf-8")
        return dst

    def current(s) -> Path | None:
        """The prepared scene, if it is newer than everything that feeds it AND
        actually readable.

        A TIMESTAMP IS NOT PROOF OF A FILE. A build killed part-way leaves a
        scene half written: recent mtime, no moov atom. Reused on trust it
        passed this check and then took the whole join down with "Invalid data
        found when processing input", pointing at a scene nothing was wrong
        with. Anything that cannot be probed is simply rebuilt.
        """
        dst = work / f"{s['id']}_fit.mp4"
        if a.rebuild or not dst.is_file():
            return None
        try:
            if probe(dst)["dur"] <= 0:
                return None
        except SystemExit:
            return None
        # WHAT FEEDS A SCENE IS ITS OWN FIELDS, NOT THE WHOLE FILE. Keying the
        # check to reel.json's mtime meant renaming one transition re-layered
        # all twenty-one scenes — nine minutes to change a word that touches no
        # scene at all. The fields that shape a scene are written to a sidecar
        # when it is built and compared on the next run.
        feeds = [clips / f"{s['id']}.mp4", proj / "captions.json", card,
                 proj / "work" / "points" / f"{s['id']}.png",
                 proj / "work" / "captions" / "vignette.png"]
        if recap and s["id"] in [recap["scene"], *recap.get("hold", [])]:
            feeds += [proj / "recap.json", *rdir.glob("state_*.png")]
        newest = max((f.stat().st_mtime for f in feeds if f.is_file()), default=0)
        if dst.stat().st_mtime < newest:
            return None
        sig = dst.with_suffix(".sig")
        want = json.dumps({k: s.get(k) for k in ("green", "width", "card", "point", "trim")},
                          ensure_ascii=False, sort_keys=True)
        if not sig.is_file() or sig.read_text(encoding="utf-8") != want:
            return None
        return dst

    todo = [s for s in scenes if current(s) is None]
    for s in scenes:
        if s not in todo:
            print(f"  {s['id']}: up to date, reused")
    if todo:
        with ThreadPoolExecutor(max_workers=max(1, a.workers)) as pool:
            list(pool.map(prepare, todo))
    made = [(s, work / f"{s['id']}_fit.mp4") for s in scenes]

    # ---- how much each cut eats off the scenes either side -----------------
    ENC = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-video_track_timescale", "30000"]

    def cut(src: Path, t0: float, t1: float, dst: Path) -> Path:
        run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t0:.3f}", "-i", str(src),
             "-t", f"{max(0.04, t1 - t0):.3f}", *ENC, str(dst)])
        return dst

    # A DISSOLVE IS NOT A BRIDGE OF TWO HALVES. A leak or a wipe COVERS a cut:
    # the scenes play one after the other and the transition hides the join, so
    # the bridge is as long as what each side gave up, added together. A
    # dissolve OVERLAPS them instead — both scenes give up D seconds and D
    # seconds come back, not 2D. Getting that wrong does not look wrong, it
    # makes the reel a second longer per cut and slides the sound cues off the
    # picture, which is exactly the kind of drift this build has already been
    # bitten by once.
    def dissolve_of(name):
        if not name or not str(name).startswith("dissolve"):
            return None
        bits = str(name).split(":")
        return float(bits[1]) if len(bits) > 1 else 0.40

    durs = [probe(c)["dur"] for _, c in made]
    eat = [(0.0, 0.0)] * len(made)          # (pre off the PREVIOUS scene, post off this one)
    for i, (s, _) in enumerate(made):
        if not i or not s.get("transition"):
            continue
        dz = dissolve_of(s["transition"])
        if dz is not None:
            d = min(dz, durs[i - 1] * 0.45, durs[i] * 0.45)
            eat[i] = (d, d)
            continue
        tr, mode = _find_tr(s["transition"])
        if tr is None:
            print(f"  {s['id']}: no transition named {s['transition']!r} — hard cut")
            continue
        td = probe(tr)["dur"]
        d = min(td, durs[i - 1], durs[i])
        pk = _peak(_sample(tr), mode, td)
        pre, post = min(pk, d, durs[i - 1]), min(d - min(pk, d), durs[i])
        if pre < 0.12 or post < 0.12:      # a handful of frames, not one
            pre = post = min(d, durs[i - 1], durs[i]) / 2
        eat[i] = (pre, post)

    # ---- the middles, the bridges, and one concat --------------------------
    parts, cues, at = [], [], 0.0
    starts = {}                    # scene id -> where it begins in the reel
    for i, (s, clip) in enumerate(made):
        starts[s["id"]] = at
        pre_next = eat[i + 1][0] if i + 1 < len(made) else 0.0
        post_here = eat[i][1]
        m0, m1 = post_here, durs[i] - pre_next
        if m1 - m0 < 0.10:                  # a short scene both cuts reach into
            mid = (m0 + m1) / 2
            m0, m1 = max(0.0, mid - 0.05), min(durs[i], mid + 0.05)
        if i:
            name = s.get("transition")
            pre, post = eat[i]
            dz = dissolve_of(name)
            if dz is not None and pre and post:
                ta = cut(made[i - 1][1], durs[i - 1] - pre, durs[i - 1], work / f"ta_{i:02d}.mp4")
                hb = cut(clip, 0.0, post, work / f"hb_{i:02d}.mp4")
                br = work / f"br_{i:02d}.mp4"
                # PICTURE DISSOLVES, SOUND DOES NOT. acrossfade here faded the
                # OUTGOING voice down over the whole bridge — and the tails are
                # tight on this route, so what was being faded was his last
                # word. Measured on the Nepal cut: 0.40s of speech attenuated
                # to nothing at every one of 20 joins, then met by the head
                # silence of the next take. That is most of why the cuts read
                # as abrupt. The audio now butt-joins at full level while the
                # picture crossfades over it — an L-cut, which is what stops a
                # join announcing itself.
                run(["ffmpeg", "-v", "error", "-y", "-i", str(ta), "-i", str(hb),
                     "-filter_complex",
                     f"[0:v][1:v]xfade=transition=fade:duration={pre:.3f}:offset=0[v];"
                     f"[0:a][1:a]concat=n=2:v=0:a=1,atrim=0:{pre:.3f},asetpts=PTS-STARTPTS[a]",
                     "-map", "[v]", "-map", "[a]", *ENC, str(br)])
                parts.append(br)
                if s.get("sound") != "none":
                    cue, gain = (s["sound"], float(s.get("gain", -4.0))) if s.get("sound") \
                        else DEFAULT_SOUND
                    cues.append({"time": round(at + pre / 2 - PEAK_OF.get(cue, 0.0), 3),
                                 "name": cue, "gain": gain})
                at += pre                      # ONE D back, not two
                print(f"  {s['id']}: dissolve {pre:.2f}s at {at - pre / 2:.2f}s")
            elif name and pre and post:
                ta = cut(made[i - 1][1], durs[i - 1] - pre, durs[i - 1], work / f"ta_{i:02d}.mp4")
                hb = cut(clip, 0.0, post, work / f"hb_{i:02d}.mp4")
                br = work / f"br_{i:02d}.mp4"
                run([sys.executable, str(ROOT / "tools" / "transition.py"), str(ta), str(hb),
                     str(br), "--name", name, "--opacity", str(a.opacity), "--bridge"])
                parts.append(br)
                if s.get("sound") != "none":
                    if s.get("sound"):
                        cue, gain = s["sound"], float(s.get("gain", -4.0))
                    elif (ROOT / "assets" / "transitions" / "wipe" / f"{name}.mp4").is_file():
                        cue, gain = WIPE_SOUND
                    elif name in SOUND_FOR:
                        cue, gain = SOUND_FOR[name]
                    else:
                        # a burn that marks a turn is the loudest thing in the
                        # cut; everything else gets the house whoosh
                        cue, gain = HARD_SOUND if name.endswith(("_14", "_07")) else DEFAULT_SOUND
                    cues.append({"time": round(at + pre - PEAK_OF.get(cue, 0.0), 3),
                                 "name": cue, "gain": gain})
                at += pre + post
                print(f"  {s['id']}: bridge under {name} ({pre + post:.2f}s), "
                      f"cut at {at - post:.2f}s")
            else:
                print(f"  {s['id']}: hard cut at {at:.2f}s")
        mid = cut(clip, m0, m1, work / f"mid_{i:02d}.mp4")
        parts.append(mid)
        at += m1 - m0
    # ONE CONCAT, BOTH STREAMS, THROUGH THE FILTER — not the demuxer.
    # Measured on this reel: every segment's audio is within one frame of its
    # video, so nothing drifts INSIDE a leg. But the copy-concat demuxer stitches
    # by each file's CONTAINER length, and containers run a packet longer than
    # their frames — the 41 video streams summed to 161.27s, the containers to
    # 162.08s, and the demuxer built a picture 0.8s longer than its frames by
    # leaving a sliver of nothing at every join. Sound built any other way could
    # not match it, and the mismatch is lip drift by the end. The concat FILTER
    # stitches frames to frames and samples to samples, both streams through
    # the same joins, so they cannot come apart. It costs one re-encode of the
    # reel, about two minutes; the joins are still built independently.
    ins, legs = [], []
    for k, seg in enumerate(parts):
        ins += ["-i", str(seg)]
        legs.append(f"[{k}:v][{k}:a]")
    reel = work / "reel_raw.mp4"
    run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex",
         "".join(legs) + f"concat=n={len(parts)}:v=1:a=1[v][a]",
         "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "medium", "-crf", "16",
         "-pix_fmt", "yuv420p", "-r", str(fps), "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
         "-movflags", "+faststart", str(reel)])
    vd = float(run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                    "stream=duration", "-of", "csv=p=0", str(reel)]).stdout or 0)
    ad = float(run(["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries",
                    "stream=duration", "-of", "csv=p=0", str(reel)]).stdout or 0)
    print(f"  concatenated {len(parts)} segment(s): picture {vd:.2f}s, sound "
          f"{ad:.2f}s, drift {ad - vd:+.3f}s")
    if abs(ad - vd) > 0.12:
        print(f"  SOUND IS OUT BY {ad - vd:+.2f}s — do not ship this")

    # ---- the transition sound, mixed onto the reel's own audio -------------
    # ---- sound that marks the TEACHING beats, not just the cuts ----------
    # A whoosh on every join says "something changed". It does not say "that is
    # a new cause, write it down". The chakra advancing is the moment the
    # student is meant to notice, so it gets its own sound, and the cinematic
    # beats get the sound of the thing on screen — the slip going into the box,
    # the page turning. Effects peak on the PICTURE, never on a caption
    # (memory: sound-comes-from-beats-not-captions).
    beat_sfx = spec.get("sfx") or {}
    for sid, want in beat_sfx.items():
        t0 = starts.get(sid)
        if t0 is None:
            print(f"  sfx: no scene {sid}")
            continue
        for ev in (want if isinstance(want, list) else [want]):
            nm = ev["name"]
            cues.append({"time": round(t0 + float(ev.get("at", 0.0))
                                       - PEAK_OF.get(nm, 0.0), 3),
                         "name": nm, "gain": float(ev.get("gain", -8.0))})
        print(f"  {sid}: {len(want) if isinstance(want, list) else 1} beat sound(s)")
    cues.sort(key=lambda c: c["time"])

    if cues:
        cj = proj / "cues_reel.json"
        cj.write_text(json.dumps({"cues": cues}, indent=1) + "\n", encoding="utf-8")
        mixed = work / "narration.wav"
        run([sys.executable, str(ROOT / "tools" / "mix_cues.py"), str(reel), str(cj), str(mixed)])
        run(["ffmpeg", "-v", "error", "-y", "-i", str(reel), "-i", str(mixed),
             "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
             "-ar", "48000", "-shortest", "-movflags", "+faststart", str(out)])
        print(f"  {len(cues)} transition cue(s) mixed onto the narration")
    else:
        Path(reel).replace(out)
    got = probe(out)
    try:
        shown = out.relative_to(ROOT)
    except ValueError:            # --out may point anywhere, e.g. a scratch dir
        shown = out
    print(f"\n  {shown}  {got['dur']:.2f}s  {got['w']}x{got['h']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
