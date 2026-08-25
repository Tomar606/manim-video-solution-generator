"""Everything in the Flow/Veo route that can be checked without Chrome or credits.

    .venv-tools/bin/python test_veo_flow.py

Three layers, and the middle one is the reason this file exists:

  bridge        the command/response protocol, against a stand-in worker. The
                browser half cannot be unit-tested, so the protocol boundary is
                made as small and as tested as possible instead.
  orchestration src/veo.py's real loop — submit, download, review, revise, give
                up — with the browser and both model calls stubbed. This is where
                the expensive bugs live: a clip filed under the wrong beat, a
                retry that does not retry, a failed clip shipped anyway.
  composite     the ffmpeg graph, checked by sampling pixels out of a rendered
                file. A filter graph that is subtly wrong still exits 0.

Everything is built from synthetic media, so it runs anywhere ffmpeg does.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

FAILURES: list[str] = []


def check(name, cond, extra=""):
    print(f"  {'PASS' if cond else 'FAIL'}  {name}" + (f"  {extra}" if extra else ""))
    if not cond:
        FAILURES.append(name)


def ffmpeg(*args):
    subprocess.run(["ffmpeg", "-v", "error", "-y", *args], check=True)


# --------------------------------------------------------------------------- #
def test_bridge():
    from src.flow_bridge import FlowBridge, FlowError

    print("\nbridge protocol")
    port = 8791
    b = FlowBridge(port).start()
    stop = threading.Event()

    def worker():
        """What flow/extension/background.js does: long-poll, run, report."""
        while not stop.is_set():
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/job", timeout=40) as r:
                    status, body = r.status, r.read()
            except Exception:
                time.sleep(0.2)
                continue
            if status == 204:
                continue
            job = json.loads(body)
            if job["cmd"] == "set_image":
                out = {"ok": False, "error": "simulated failure"}
            elif job["cmd"] == "ping":
                out = {"ok": True, "data": {"tab": "https://labs.google/fx/tools/flow/project/x"}}
            else:
                out = {"ok": True, "data": {"echo": job["cmd"]}}
            req = urllib.request.Request(
                f"http://127.0.0.1:{port}/event",
                data=json.dumps(dict(out, id=job["id"])).encode(),
                headers={"Content-Type": "application/json"}, method="POST")
            urllib.request.urlopen(req, timeout=10).read()

    t = threading.Thread(target=worker, daemon=True)
    t.start()
    try:
        info = b.wait_for_worker(timeout=10)
        check("ping round-trips", info.get("tab", "").startswith("https://labs.google"))
        check("a command round-trips",
              b.call("set_prompt", text="x", timeout=10) == {"echo": "set_prompt"})
        try:
            b.call("set_image", paths=["/tmp/x.png"], timeout=10)
            check("a worker error becomes FlowError", False)
        except FlowError as e:
            check("a worker error becomes FlowError", "simulated failure" in str(e))
    finally:
        stop.set()
        b.stop()

    # On its own bridge with no worker at all. Signalling the worker above to
    # stop does NOT make it deaf: it is parked inside a long poll, so the next
    # command is handed to it and answered before it ever re-checks the flag.
    # That made this assertion a race rather than a test.
    quiet = FlowBridge(8792).start()
    try:
        quiet.call("attach", timeout=2)
        check("no worker means a clear timeout, not a hang", False)
    except FlowError as e:
        check("no worker means a clear timeout, not a hang",
              "timed out" in str(e) and "extension" in str(e))
    finally:
        quiet.stop()


# --------------------------------------------------------------------------- #
def test_orchestration(tmp: Path):
    from src import veo, veo_conform, veo_prompts, veo_qc
    from src.flow_bridge import inbox_dir

    print("\norchestration")
    proj = tmp / "proj"
    (proj / "veo").mkdir(parents=True)
    lines = [{"start": i * 3.0, "end": i * 3.0 + 2.8, "text": f"line {i}"}
             for i in range(20)]
    beats = [
        {"at": 2, "type": "points", "title": "क", "items": ["a", "b"]},
        {"at": 5, "type": "video", "brief": "rust creeping across wet iron",
         "seconds": 8, "presenter": "hidden",
         "labels": [{"at": 6, "text": "जंग की परत", "x": 0.42, "y": 0.60}]},
        {"at": 9, "type": "video", "brief": "gas bubbling off an electrode",
         "seconds": 8, "labels": [{"at": 10, "text": "गैस", "x": 0.5, "y": 0.80}]},
        {"at": 12, "type": "image", "src": "images/x.png"},
    ]
    (proj / "lines_part1.json").write_text(json.dumps(lines))
    (proj / "beats_part1.json").write_text(json.dumps(beats, ensure_ascii=False))
    (proj / "meta.json").write_text(json.dumps(
        {"subject": "chemistry", "question": "संक्षारण को समझाइए।",
         "clip_end": {"1": 60.0}}, ensure_ascii=False))
    (proj / "verification.md").write_text("Rust is hydrated iron(III) oxide.")

    # Big enough that settled() reads it as a finished download, not a stub.
    sample = tmp / "sample.mp4"
    ffmpeg("-f", "lavfi", "-i",
           "color=c=0x1b2838:s=1080x1920:d=8:r=24,noise=alls=18:allf=t",
           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "44", str(sample))

    spec = {
        "prompt": ("Rust spreads across a wet iron nail. " * 12).strip() +
                  " The clip is silent. The supplied background image is unchanged.",
        "negative": "on-screen text, letters, numerals, captions, borders, "
                    "vignette, sparkles, lens flare",
        "checks": ["the rust is orange-brown", "the nail is wet"],
    }
    calls = {"revise": 0, "review": 0, "submits": 0}

    def fake_review(video, s, *, work, brief="", full_frame=True, provider=None):
        calls["review"] += 1
        # beat@5 fails once then recovers; beat@9 never does.
        bad = "electrode" in brief or calls["review"] == 1
        return {"verdict": "fail" if bad else "pass", "summary": "stubbed",
                "failed_checks": ["the nail is wet"] if bad else [],
                "defects": [{"severity": "fail", "issue": "a letter W is visible"}]
                           if bad else [], "frames": [],
                # the clip rots after 5 of its 8 seconds
                "good_until": 5.0, "last_good_frame": 6, "loopable": False,
                "tail_problem": "a second nail appears"}

    def fake_revise(prev, defects, **kw):
        calls["revise"] += 1
        return dict(prev, prompt=prev["prompt"] + " Revised.")

    veo_prompts.write_prompt = lambda **kw: dict(spec)
    veo_prompts.revise_prompt = fake_revise
    veo_qc.review = fake_review
    veo.SETTLE_AFTER_SUBMIT, veo.POLL_EVERY = 0.0, 0.01

    class FakeBridge:
        """Mirrors the extension's contract, including the one that matters:
        a new media key appears only after a submit."""
        def __init__(self):
            self.keys = []

        def start(self):
            return self

        def stop(self):
            pass

        def set_status(self, **kw):
            pass

        def wait_for_worker(self, timeout=90):
            return {"tab": "https://labs.google/fx/tools/flow/project/x"}

        def call(self, cmd, timeout=None, **kw):
            if cmd == "set_image":
                assert Path(kw["paths"][0]).is_file(), "the plate must be a real file"
            elif cmd == "set_prompt":
                assert "NEGATIVE:" in kw["text"], "the negative list must ride along"
                calls["submits"] += 1
            elif cmd == "click":
                self.keys.append(f"key{len(self.keys) + 1}")
            elif cmd == "list_media":
                return {"media": [{"key": k, "url": f"https://x/{k}"} for k in self.keys]}
            elif cmd == "download":
                shutil.copy(sample, inbox_dir() / Path(kw["filename"]).name)
            return {}

    clips = veo.run(str(proj), 1, attempts=3, bridge=FakeBridge())["clips"]

    check("one entry per video beat", len(clips) == 2, str([c["at"] for c in clips]))
    check("a beat recovers on a revision",
          clips[0]["verdict"] == "pass" and clips[0]["attempts"] == 2)
    check("a beat that never passes is marked unusable",
          clips[1]["verdict"] == "fail" and clips[1]["usable"] is False
          and clips[1]["attempts"] == 3)
    check("every attempt was really submitted", calls["submits"] == 5, str(calls))
    check("every attempt is kept on disk, not just the winner",
          len(list((proj / "veo").glob("*_try*.mp4"))) == 5,
          str(sorted(p.name for p in (proj / "veo").glob("*.mp4"))))
    check("the window starts on the beat's own caption", clips[0]["start"] == 15.0)
    check("the window is clipped by the next beat", clips[0]["end"] == 23.0,
          str(clips[0]["end"]))
    check("presenter:hidden becomes a full-frame clip",
          clips[0]["full"] is True and clips[1]["full"] is False)
    check("paths are project-relative",
          all(not Path(c["src"]).is_absolute() and (proj / c["src"]).is_file()
              for c in clips))

    fit = clips[0]["fit"]
    check("the hallucinated tail was cut", fit["usable"] == 5.0 and fit["trimmed"] == 3.0,
          str(fit))
    check("the clip was fitted to the window, not the other way round",
          abs(veo_conform.duration(proj / clips[0]["src"])
              - (clips[0]["end"] - clips[0]["start"])) < 0.10,
          f"{veo_conform.duration(proj / clips[0]['src']):.2f}s for a "
          f"{clips[0]['end'] - clips[0]['start']:.2f}s window")
    check("the unconformed original is kept beside it",
          (proj / clips[0]["raw"]).is_file() and clips[0]["raw"] != clips[0]["src"])

    lab = clips[0]["labels"][0]
    check("labels are typeset by us, not generated",
          (proj / lab["png"]).is_file() and lab["text"] == "जंग की परत")
    check("a label arrives on the caption that names it", lab["start"] == 18.0)
    check("a label never outlives its clip", lab["end"] <= clips[0]["end"])
    faults = veo.label_faults(clips[1]["labels"], full=clips[1]["full"])
    check("a label behind the presenter is caught",
          any("hidden behind him" in f for f in faults), str(faults))
    check("the same label is fine once he steps aside",
          veo.label_faults(clips[1]["labels"], full=True) == [])

    import preflight as pf
    rep = pf.Report()
    pf.check_veo_clips(proj, rep)
    check("preflight warns about the clip that failed review",
          any(r[1].endswith("failed review") for r in rep.rows))
    check("preflight passes a part whose clips are all present", not rep.failed)
    (proj / "clips_part1.json").unlink()
    rep2 = pf.Report()
    pf.check_veo_clips(proj, rep2)
    check("preflight FAILS a part whose video beats were never generated",
          rep2.failed)

    print("\nprompt audit")
    bad = veo_prompts.audit({"prompt": "Draw a logo in a corner. " * 20, "checks": []})
    check("catches a word that is a signal to draw it",
          any("logo" in b for b in bad))
    check("catches a missing silent clause", any("silent" in b for b in bad))
    check("catches a missing plate reference",
          any("background image" in b for b in bad))
    check("catches missing checks", any("no checks" in b for b in bad))
    check("catches a negative list with no text clause",
          any("on-screen text" in b for b in
              veo_prompts.audit(dict(spec, negative="borders, vignette"))))
    check("catches a negative list with no decoration clause",
          any("decoration" in b for b in
              veo_prompts.audit(dict(spec, negative="text, captions"))))
    check("a complete prompt passes clean", veo_prompts.audit(spec) == [],
          str(veo_prompts.audit(spec)))


# --------------------------------------------------------------------------- #
def test_conform(tmp: Path):
    """Fitting a fixed-length generation to the presenter's variable window.

    The fixture is a green block sweeping left to right for 7 seconds, followed
    by 3 seconds of a red band standing in for the hallucinated tail. That tail
    has to disappear from every output, and the sweep has to keep going the way
    it was going — a boomerang would satisfy the length requirement and teach
    the process running backwards.
    """
    from src import veo_conform as vc
    from src.veo_qc import good_until

    print("\nconform")
    src = tmp / "gen.mp4"
    ffmpeg("-f", "lavfi", "-i", "color=c=0x102030:s=540x960:d=10:r=24",
           "-f", "lavfi", "-i", "color=c=0x33cc66:s=80x80:d=10:r=24",
           "-filter_complex",
           "[0:v][1:v]overlay=x='40+40*t':y=400:eval=frame[v];"
           "[v]drawbox=x=0:y=0:w=540:h=200:color=red@1:t=fill:enable='gt(t,7)'[o]",
           "-map", "[o]", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(src))

    import numpy as np
    from PIL import Image

    def probe(f, t):
        png = tmp / "probe.png"
        ffmpeg("-ss", f"{t:.2f}", "-i", str(f), "-frames:v", "1", str(png))
        a = np.asarray(Image.open(png).convert("RGB")).astype(int)
        m = (a[..., 1] > 150) & (a[..., 0] < 130) & (a[..., 2] < 160)
        xs = np.where(m.any(axis=0))[0]
        return (int(xs.mean()) if len(xs) else None,
                float(((a[:200, ..., 0] > 150) & (a[:200, ..., 1] < 80)).mean()))

    check("the fixture really does go wrong after 7s", probe(src, 8.5)[1] > 0.9)

    plans = {
        "one_way slows to the cap then holds": vc.plan(7.0, 15.0, "one_way"),
        "cyclic loops": vc.plan(7.0, 15.0, "cyclic"),
        "settling holds": vc.plan(7.0, 15.0, "settling"),
        "a clip longer than its window is cut from the END":
            vc.plan(10.0, 4.0, "one_way"),
    }
    check("one_way slows to the cap then holds",
          any("setpts=2.0" in x for x in plans["one_way slows to the cap then holds"])
          and any("tpad" in x for x in plans["one_way slows to the cap then holds"]))
    check("cyclic loops", any("loop=loop=-1" in x for x in plans["cyclic loops"]))
    check("settling holds", any("stop_duration=8" in x for x in plans["settling holds"]))
    check("a clip longer than its window is cut from the END",
          plans["a clip longer than its window is cut from the END"][0] == "trim=0:4.000")
    check("no strategy ever reverses the clip",
          not any("reverse" in step for steps in plans.values() for step in steps))
    try:
        vc.plan(0.8, 10.0, "one_way")
        check("a clip with almost nothing usable is refused", False)
    except vc.ConformError:
        check("a clip with almost nothing usable is refused", True)

    for strategy, need in (("one_way", 15.0), ("cyclic", 15.0),
                           ("settling", 12.0), ("one_way", 4.0)):
        dest = tmp / f"fit_{strategy}_{int(need)}.mp4"
        info = vc.conform(src, dest, good_until=7.0, need=need, strategy=strategy)
        got = vc.duration(dest)
        check(f"{strategy} -> {need:.0f}s is exactly that long",
              abs(got - need) < 0.25, f"{got:.2f}s, cut {info['trimmed']}s")
        reds = [probe(dest, got * i / 11)[1] for i in range(12)]
        check(f"{strategy} -> {need:.0f}s: the bad tail is gone from every frame",
              max(reds) < 0.05, f"max {max(reds):.2f}")

    d = tmp / "fit_one_way_15.mp4"
    xs = [probe(d, t)[0] for t in (0.2, 2, 4, 6, 8, 10, 12, 13.5)]
    check("one_way never runs backwards",
          all(b >= a - 4 for a, b in zip(xs, xs[1:]) if a and b), str(xs))
    check("one_way is genuinely slowed, not merely padded",
          xs[3] is not None and xs[-1] is not None and xs[-1] - xs[3] > 100)
    held = [probe(d, t)[0] for t in (14.1, 14.5, 14.9)]
    check("one_way ends holding the finished state", len(set(held)) == 1, str(held))

    xs = [probe(tmp / "fit_cyclic_15.mp4", t)[0] for t in (0.2, 3, 6, 7.5, 10, 13)]
    check("cyclic restarts from the beginning",
          any(b < a - 50 for a, b in zip(xs, xs[1:]) if a and b), str(xs))

    xs = [probe(tmp / "fit_settling_12.mp4", t)[0] for t in (0.2, 3, 6, 8, 11)]
    check("settling plays at speed and then freezes",
          xs[-1] == xs[-2] and xs[0] < xs[2], str(xs))

    stamps = [0.0, 1.0, 2.0, 3.0, 4.0]
    check("a review that says 'all good' uses the whole clip",
          good_until({"last_good_frame": -1}, stamps) == 4.0)
    check("a review that names a frame stops there",
          good_until({"last_good_frame": 3}, stamps) == 2.0)
    check("a review that condemns the first frame yields nothing usable",
          good_until({"last_good_frame": 0}, stamps) == 0.0)


# --------------------------------------------------------------------------- #
def test_composite(tmp: Path):
    import composite as comp
    from src import veo_labels

    print("\ncomposite")
    bg, av = tmp / "bg.mp4", tmp / "av.mp4"
    ca, cb = tmp / "a.mp4", tmp / "b.mp4"
    # A caption strip Manim would have drawn, so we can prove it survives.
    ffmpeg("-f", "lavfi", "-i", "color=c=0x1b2838:s=1080x1920:d=14:r=30,"
           "drawbox=x=0:y=0:w=1080:h=500:color=0x882222:t=fill",
           "-c:v", "libx264", "-pix_fmt", "yuv420p", str(bg))
    ffmpeg("-f", "lavfi", "-i", "color=c=0x00b140:s=1920x1080:d=14:r=25,"
           "drawbox=x=900:y=300:w=200:h=500:color=0xddaa88:t=fill",
           "-f", "lavfi", "-i", "sine=f=300:d=14",
           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(av))
    ffmpeg("-f", "lavfi", "-i", "color=c=0x1b2838:s=1080x1920:d=8:r=24,"
           "drawbox=x=200:y=700:w=600:h=400:color=0x33cc66:t=fill",
           "-c:v", "libx264", "-pix_fmt", "yuv420p", str(ca))
    ffmpeg("-f", "lavfi", "-i", "color=c=0x1b2838:s=720x1280:d=6:r=24,"
           "drawbox=x=100:y=500:w=400:h=300:color=0xcc6633:t=fill",
           "-c:v", "libx264", "-pix_fmt", "yuv420p", str(cb))
    key = {"hue": 120, "sat": 0.35, "v1": 0.25, "v2": 0.55, "sim": 0.32}

    img = veo_labels.render("जंग की परत", 50)
    png = tmp / "lab.png"
    img.save(png)
    lab = {"png": png, "x": 300, "y": 1150, "w": img.width, "h": img.height,
           "start": 3.0, "end": 9.0, "text": "जंग"}
    clips = [
        {"at": 10, "start": 2.0, "end": 9.0, "path": ca, "labels": [lab]},
        {"at": 30, "start": 10.0, "end": 13.5, "path": cb, "labels": []},
    ]

    out = tmp / "out.mp4"
    comp.composite(bg, av, key, out, clips=clips)
    check("the composite decodes and lands", out.is_file())

    # The existing paths must still work with clips absent and present.
    comp.composite(bg, av, key, tmp / "none.mp4")
    check("the no-clips path still works", (tmp / "none.mp4").is_file())
    comp.composite(bg, av, key, tmp / "all.mp4", windows=[[3.0, 9.0]],
                   presenter=[[4.0, 11.0]], clips=clips)
    check("resize windows, presenter fades and clips coexist",
          (tmp / "all.mp4").is_file())

    from PIL import Image
    import numpy as np

    def frame(t):
        f = tmp / f"f{t}.png"
        ffmpeg("-ss", str(t), "-i", str(out), "-frames:v", "1", str(f))
        return np.asarray(Image.open(f).convert("RGB")).astype(int)

    def near(px, want, tol=26):
        return all(abs(int(p) - q) <= tol for p, q in zip(px, want))

    PLATE, CAP = (0x1b, 0x28, 0x38), (0x88, 0x22, 0x22)
    A, B = (0x33, 0xcc, 0x66), (0xcc, 0x66, 0x33)
    f0, f5, f11 = frame(0.5), frame(5.0), frame(11.5)

    check("before any clip the plate is untouched", near(f0[900, 540], PLATE))
    check("a clip lands at its own time and place", near(f5[900, 500], A))
    check("the caption strip stays Manim's while a clip plays",
          near(f5[250, 540], CAP))
    check("nothing bleeds above the caption cut", near(f5[450, 500], CAP))
    check("a clip is scaled to the frame", near(f11[950, 400], B))
    check("a clip is gone once its window closes", near(f11[900, 900], PLATE))

    region = f5[lab["y"]:lab["y"] + lab["h"], lab["x"]:lab["x"] + lab["w"]]
    check("the label is composited over its clip",
          int((region > 200).all(axis=2).sum()) > 300)
    early = frame(2.5)[lab["y"]:lab["y"] + lab["h"], lab["x"]:lab["x"] + lab["w"]]
    check("the label is not up before its caption",
          int((early > 200).all(axis=2).sum()) < 40)


# --------------------------------------------------------------------------- #
def test_sequence(tmp: Path):
    """The chained route: several clips that have to look like one take.

    The unit half is grouping and frame extraction. The orchestration half is
    the one worth having, and it is aimed at a single question: when a clip in
    the middle of a sequence is rejected, does the next one continue from the
    last GOOD frame rather than from the bad one? Carrying a rejected frame
    forward is the failure mode that would look more consistent than the correct
    behaviour, and so would never be spotted by watching the output.
    """
    from src import veo, veo_prompts, veo_qc, veo_sequence
    from src.flow_bridge import inbox_dir

    print("\nsequence grouping")
    B = [{"at": 1, "sequence": "d"}, {"at": 2, "sequence": "d"},
         {"at": 3}, {"at": 4, "sequence": "e"}]
    runs = veo_sequence.spans(B)
    check("adjacent beats sharing an id become one run",
          [len(r) for r in runs] == [2, 1, 1], str([len(r) for r in runs]))
    check("an unmarked beat is a run of one", runs[1][0]["at"] == 3)
    check("a standalone beat keeps the old behaviour",
          veo_sequence.spans([{"at": 1}]) == [[{"at": 1}]])
    split = [{"at": 1, "sequence": "d"}, {"at": 2, "sequence": "e"},
             {"at": 3, "sequence": "d"}]
    try:
        veo_sequence.spans(split)
        check("a split sequence is refused", False)
    except veo_sequence.SequenceError as e:
        check("a split sequence is refused, not silently rejoined",
              "ADJACENT" in str(e), str(e)[:60])

    print("\nthe carry frame")
    # A clip whose two halves are unmistakably different colours, so the frame
    # taken from the end can be proved to be the END rather than the start.
    two = tmp / "two.mp4"
    ffmpeg("-f", "lavfi", "-i", "color=c=red:s=320x240:d=3:r=24",
           "-f", "lavfi", "-i", "color=c=blue:s=320x240:d=3:r=24",
           "-filter_complex", "[0][1]concat=n=2:v=1", "-c:v", "libx264",
           "-pix_fmt", "yuv420p", str(two))
    frame = veo_sequence.carry_frame(two, tmp / "carry" / "c.png")
    from PIL import Image
    r, g, b = Image.open(frame).convert("RGB").getpixel((160, 120))
    check("the carried frame comes from the END of the clip", b > 120 and r < 90,
          f"rgb({r},{g},{b})")
    try:
        veo_sequence.carry_frame(tmp / "nope.mp4", tmp / "carry" / "x.png")
        check("an unreadable clip is refused", False)
    except veo_sequence.SequenceError:
        check("an unreadable clip is refused rather than carried as a blank", True)

    print("\nwhat gets uploaded")
    plate = veo_prompts.plate_for("chemistry")
    ref = tmp / "ref.png"
    Image.new("RGB", (40, 40), "white").save(ref)
    # Compared resolved on both sides: uploads() resolves, and on macOS that
    # rewrites /var to /private/var, which is correct and not the thing under
    # test here.
    R = lambda ps: [Path(x).resolve() for x in ps]  # noqa: E731
    first = veo_sequence.uploads(plate=plate, reference=ref, carry=None)
    check("the first clip goes up on the plate", first == R([plate, ref]), str(first))
    later = veo_sequence.uploads(plate=plate, reference=ref, carry=frame)
    check("a carried frame REPLACES the plate rather than joining it",
          later == R([frame, ref]), str(later))
    check("the carried frame is offered first, so a one-file control keeps it",
          later[0] == frame.resolve())
    check("the textbook figure stays attached for every clip of the sequence",
          ref.resolve() in first and ref.resolve() in later)
    try:
        veo_sequence.uploads(plate=tmp / "gone.png", reference=None, carry=None)
        check("a missing reference is refused", False)
    except veo_sequence.SequenceError:
        check("a missing reference is refused before a credit is spent", True)
    # Chrome resolves nothing and reports nothing: a relative path attaches no
    # file and the clip comes back merely inconsistent rather than broken.
    import os
    here = Path(os.getcwd())
    rel = Path(os.path.relpath(ref, here))
    check("a relative path is made absolute before it reaches the browser",
          all(u.is_absolute() for u in
              veo_sequence.uploads(plate=None, reference=rel, carry=None)),
          str(rel))

    print("\nthe reference figure")
    figs = tmp / "proj2" / "assets" / "figures"
    figs.mkdir(parents=True)
    Image.new("RGB", (40, 40), "white").save(figs / "cell_preview.png")
    check("the traced preview serves when there is no raw crop",
          veo_prompts.reference_for(tmp / "proj2", "cell").name == "cell_preview.png")
    Image.new("RGB", (40, 40), "white").save(figs / "cell_scan.png")
    check("the book's own crop is preferred over the trace",
          veo_prompts.reference_for(tmp / "proj2", "cell").name == "cell_scan.png")
    try:
        veo_prompts.reference_for(tmp / "proj2", "missing")
        check("an unknown figure is refused", False)
    except FileNotFoundError as e:
        check("an unknown figure names the command that would make it",
              "figure_from_scan" in str(e))

    print("\nthe chained prompt audit")
    fresh = {"prompt": ("A wide shot of a beaker on a bench. " * 12).strip()
                       + " The clip is silent. The supplied image is unchanged.",
             "negative": "text, letters, captions, borders, vignette, sparkles",
             "checks": ["the beaker is full"]}
    check("a chained prompt that reads as a fresh shot is caught",
          any("re-stage" in x for x in veo_prompts.audit(fresh, carried=True)))
    check("the same prompt is fine when nothing is being continued",
          veo_prompts.audit(fresh) == [])
    cont = dict(fresh, prompt=fresh["prompt"] + " The scene continues unchanged "
                                                "from the supplied first frame.")
    check("a prompt that says it continues passes",
          veo_prompts.audit(cont, carried=True) == [],
          str(veo_prompts.audit(cont, carried=True)))

    print("\norchestration: a sequence with a rejected clip in the middle")
    proj = tmp / "seq"
    (proj / "veo").mkdir(parents=True)
    lines = [{"start": i * 3.0, "end": i * 3.0 + 2.8, "text": f"line {i}"}
             for i in range(20)]
    beats = [{"at": at, "type": "video", "sequence": "daniell", "seconds": 8,
              "presenter": "hidden", "brief": f"stage {n} of the cell"}
             for n, at in enumerate((2, 5, 8), 1)]
    (proj / "lines_part1.json").write_text(json.dumps(lines))
    (proj / "beats_part1.json").write_text(json.dumps(beats, ensure_ascii=False))
    (proj / "meta.json").write_text(json.dumps(
        {"subject": "chemistry", "question": "q", "clip_end": {"1": 60.0}},
        ensure_ascii=False))

    sample = tmp / "seq_sample.mp4"
    ffmpeg("-f", "lavfi", "-i",
           "color=c=0x1b2838:s=1080x1920:d=8:r=24,noise=alls=18:allf=t",
           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "44", str(sample))

    spec = dict(cont)
    seen = {"uploads": [], "carried": [], "previous": [], "positions": [],
            "continuity": []}

    def fake_write(**kw):
        seen["carried"].append(kw.get("carried"))
        seen["previous"].append(bool(kw.get("previous")))
        seen["positions"].append(kw.get("position"))
        return dict(spec)

    # The middle clip is rejected however many times it is tried.
    def fake_review(video, s, *, work, brief="", full_frame=True, provider=None):
        bad = "stage 2" in brief
        return {"verdict": "fail" if bad else "pass", "summary": "stubbed",
                "failed_checks": ["nope"] if bad else [], "defects": [],
                "frames": [], "good_until": 8.0, "last_good_frame": -1,
                "loopable": False, "tail_problem": ""}

    def fake_continuity(reference, clip, *, work, provider=None):
        seen["continuity"].append(Path(reference).name)
        return {"continuous": True, "severity": "none", "changes": []}

    veo_prompts.write_prompt = fake_write
    veo_prompts.revise_prompt = lambda prev, defects, **kw: dict(prev)
    veo_qc.review = fake_review
    veo_qc.continuity = fake_continuity

    class SeqBridge:
        def __init__(self):
            self.keys = []

        def start(self):
            return self

        def stop(self):
            pass

        def set_status(self, **kw):
            pass

        def wait_for_worker(self, timeout=90):
            return {"tab": "https://labs.google/fx/tools/flow/project/x"}

        def call(self, cmd, timeout=None, **kw):
            if cmd == "set_image":
                seen["uploads"].append([Path(p).name for p in kw["paths"]])
                return {"files": len(kw["paths"]), "used": len(kw["paths"]),
                        "multiple": True, "dropped": []}
            if cmd == "click":
                self.keys.append(f"key{len(self.keys) + 1}")
            elif cmd == "list_media":
                return {"media": [{"key": k, "url": f"https://x/{k}"} for k in self.keys]}
            elif cmd == "download":
                shutil.copy(sample, inbox_dir() / Path(kw["filename"]).name)
            return {}

    clips = veo.run(str(proj), 1, attempts=2, bridge=SeqBridge())["clips"]

    check("every beat of the sequence produced a clip", len(clips) == 3)
    check("the first clip is not continued from anything",
          clips[0]["continues_from"] is None and seen["carried"][0] is False)
    check("the second clip continues from the first",
          seen["carried"][1] is True and clips[1]["continues_from"] == 2,
          str(clips[1]["continues_from"]))
    check("THE REJECTED CLIP IS NOT CARRIED FORWARD — the third continues from "
          "the first, not the second",
          clips[2]["continues_from"] == 2, str(clips[2]["continues_from"]))
    check("the hole is recorded on the clip, not just printed",
          clips[1]["verdict"] == "fail" and clips[1]["usable"] is False)
    check("the previous prompt is shown to the writer so wording is reused",
          seen["previous"] == [False, True, True], str(seen["previous"]))
    check("the writer is told where in the sequence it is",
          seen["positions"] == ["clip 1 of 3", "clip 2 of 3", "clip 3 of 3"],
          str(seen["positions"]))

    firsts = [u for u in seen["uploads"]]
    check("the first generation went up on the plate",
          firsts[0][0] == "chemistry.png", str(firsts[0]))
    check("every later generation went up on a carried frame, never the plate",
          all(u[0].endswith(".png") and u[0] != "chemistry.png" for u in firsts[1:]),
          str(firsts[1:]))
    # Once, not twice: the middle clip failed its facts and was going to be
    # regenerated anyway, and "does this wrong clip match the previous frame"
    # is a question with no useful answer. Only the third clip reached the seam
    # check, and it was graded against the frame actually carried to it.
    check("the seam is graded only on a clip that is otherwise good",
          seen["continuity"] == ["part1_at002.png"], str(seen["continuity"]))
    check("the carried frames are kept on disk for inspection",
          len(list((proj / "veo" / "carry").glob("*.png"))) == 2,
          str(sorted(p.name for p in (proj / "veo" / "carry").glob("*.png"))))

    print("\na seam that does not hold forces a regeneration")
    tries = {"n": 0}

    def broken_seam(reference, clip, *, work, provider=None):
        tries["n"] += 1
        return {"continuous": False, "severity": "major",
                "changes": ["the beaker is a different shape"]}

    veo_qc.review = lambda *a, **k: {
        "verdict": "pass", "summary": "stubbed", "failed_checks": [], "defects": [],
        "frames": [], "good_until": 8.0, "last_good_frame": -1,
        "loopable": False, "tail_problem": ""}
    veo_qc.continuity = broken_seam
    proj2 = tmp / "seq2"
    (proj2 / "veo").mkdir(parents=True)
    for f in ("lines_part1.json", "beats_part1.json", "meta.json"):
        shutil.copy(proj / f, proj2 / f)
    clips2 = veo.run(str(proj2), 1, attempts=2, bridge=SeqBridge())["clips"]
    check("a clip whose facts are right but whose seam is broken still fails",
          clips2[1]["verdict"] == "fail", str(clips2[1]["verdict"]))
    check("and it was retried rather than accepted", tries["n"] >= 2, str(tries))
    check("the seam finding is kept with the clip",
          (clips2[1].get("continuity") or {}).get("severity") == "major")


# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg is required")
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        test_bridge()
        test_orchestration(tmp)
        test_sequence(tmp)
        test_conform(tmp)
        test_composite(tmp)
    print()
    if FAILURES:
        print(f"{len(FAILURES)} FAILED:")
        for f in FAILURES:
            print(f"  - {f}")
        sys.exit(1)
    print("all pass")
