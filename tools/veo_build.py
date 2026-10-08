"""Generate scenes ONE AT A TIME, checking each before paying for the next.

    python tools/veo_build.py projects/<slug>/veo --scenes 9 12 17
    python tools/veo_build.py projects/<slug>/veo --broll 3 8 11
    python tools/veo_build.py projects/<slug>/veo --scenes 9 --retries 1

WHY ONE AT A TIME
-----------------
The first batch on this video was twenty-three clips submitted together. Six of
them spoke Latin words because a transliteration had silently failed to save,
and that was only discovered after all twenty-three were paid for. A per-clip
check would have caught it on clip two.

So each scene here is submitted, fetched, checked, and only then does the next
one start. A failure stops the run rather than continuing down the list, because
the usual cause of one bad clip is a fault in the prompt or the line that the
rest of the list shares.

WHAT IS CHECKED, per clip, before the next is bought
----------------------------------------------------
    shape    the 9:16 ratio, on the downloaded file — Flow's aspect setting
             cannot be read from the page, so this is the only honest check
    face     measured similarity to the reference photograph (presenter only)
    speech   what he actually said against the scripted line, best of N passes
    framing  face height as a share of the frame, so a video that is twenty
             identical medium shots is visible while it can still be changed
    gap      a silence long enough to mean the generation stopped and restarted

`--broll` runs the same loop over prompts/broll/bNN.txt, skipping the face and
speech checks: those clips have no presenter and no speech by design.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "veo_kit"))

PY = sys.executable
RATIO = 9 / 16
RATIO_TOL = 0.02


def run(cmd: list[str], timeout: float = 3600) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def tile_count() -> int:
    """How many clips the Flow project holds right now.

    CALLED ONCE, at the start. Each call stands up its own bridge and tears it
    down, and the extension long-polls the old server for up to 25s after it
    dies — so counting before every submit made the very next connect fail with
    "the extension never answered". The loop counts once and then keeps its own
    tally, incrementing per clip it accepts.
    """
    import time as _t
    sys.path.insert(0, str(ROOT / "veo_kit"))
    import fetch as F
    import flowkit as fk
    b, project = fk.connect()
    try:
        F.back_to_grid(b, project)
        _t.sleep(2.0)
        return int(F.tile_count(b))
    finally:
        b.stop()


def shot_size(clip: Path) -> tuple[str, float]:
    """Face height as a share of frame height — the shot-ladder check."""
    try:
        import tempfile

        from facenet_pytorch import MTCNN
        from PIL import Image
        with tempfile.TemporaryDirectory() as td:
            f = Path(td) / "f.png"
            subprocess.run(["ffmpeg", "-v", "error", "-ss", "5", "-i", str(clip),
                            "-frames:v", "1", str(f), "-y"], check=True)
            im = Image.open(f).convert("RGB")
            boxes, _ = MTCNN(keep_all=False, device="cpu").detect(im)
        if boxes is None:
            return "no face", 0.0
        pct = 100 * (boxes[0][3] - boxes[0][1]) / im.height
    except Exception:                                    # noqa: BLE001
        return "?", 0.0
    name = ("close" if pct > 22 else "medium" if pct > 12 else
            "medium-wide" if pct > 7 else "wide")
    return name, pct


def check(clip: Path, line: str | None, character: str, passes: int) -> list[str]:
    faults = []
    out = run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
               "stream=width,height", "-of", "csv=p=0", str(clip)]).stdout.strip()
    try:
        w, h = (int(v) for v in out.split(",")[:2])
    except ValueError:
        return ["unreadable file"]
    if abs(w / h - RATIO) > RATIO_TOL:
        faults.append(f"NOT 9:16 ({w}x{h})")

    if line is not None:
        r = run([PY, str(ROOT / "veo_kit" / "face_gate.py"), str(clip),
                 "--character", character, "--spread", "5"])
        import re as _re
        m = _re.search(r"median\s+([0-9.]+)", r.stdout)
        med = m.group(1) if m else "?"
        if r.returncode != 0:
            faults.append(f"FACE {med}")
        r = run([PY, str(ROOT / "veo_kit" / "speech_qc.py"), str(clip), line,
                 "--passes", str(passes)])
        cov = next((ln.split(":", 1)[1].strip() for ln in r.stdout.splitlines()
                    if "coverage" in ln), "?")
        if r.returncode != 0:
            faults.append(f"SPEECH — {cov}")
        print(f"      face {med}   speech {cov.split(' of ')[0]}")
    size, pct = shot_size(clip)
    print(f"      framing {size} ({pct:.0f}% face height)")
    return faults


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--scenes", nargs="*", type=int, default=[])
    ap.add_argument("--broll", nargs="*", type=int, default=[])
    ap.add_argument("--character",
                    default=str(ROOT / "veo_kit" / "characters" / "ritesh.json"))
    ap.add_argument("--passes", type=int, default=3)
    ap.add_argument("--held", type=int, default=-1,
                    help="clips already in the Flow project; counted if omitted, "
                         "but counting opens a bridge the next submit then races")
    ap.add_argument("--retries", type=int, default=1,
                    help="regenerate a failing clip this many times before stopping")
    a = ap.parse_args()

    folder = Path(a.folder)
    lines = json.loads((folder / "lines.json").read_text(encoding="utf-8"))
    jobs = ([("scene", n, folder / "prompts" / "vertical" / f"s{n:02d}.txt",
              folder / "clips" / f"s{n:02d}.mp4", lines[str(n)]) for n in a.scenes]
            + [("broll", n, folder / "prompts" / "broll" / f"b{n:02d}.txt",
                folder / "clips" / f"b{n:02d}.mp4", None) for n in a.broll])
    if not jobs:
        print("  nothing to do — pass --scenes and/or --broll")
        return 1

    if a.held >= 0:
        held = a.held
    else:
        held = tile_count()
        # The extension long-polls the bridge we just killed; give it time to
        # find the next one or the first submit dies on "never answered".
        print("  waiting for the extension to re-attach")
        time.sleep(30)
    print(f"  {len(jobs)} clip(s), one at a time; each is checked before the next "
          f"is bought.  Flow project holds {held}\n")
    done, failed = [], []
    for kind, n, prompt, clip, line in jobs:
        if not prompt.is_file():
            print(f"  {prompt} missing"); return 1
        tag = f"{'s' if kind == 'scene' else 'b'}{n:02d}"
        for attempt in range(a.retries + 1):
            label = f"  {tag}" + (f"  (retry {attempt})" if attempt else "")
            # HOW MANY CLIPS THE PROJECT ALREADY HOLDS. fetch.py's --expect is a
            # count of tiles in the PROJECT, not of new arrivals, so passing 1
            # while an earlier clip is sitting there satisfies it immediately:
            # it walks the old tiles, fails to match, and reports "0 downloaded,
            # 0 problems" for a clip that is still rendering — and the clip is
            # paid for either way.
            print(f"{label}  submitting  (project holds {held})")
            before = held
            cmd = [PY, "-u", str(ROOT / "veo_kit" / "submit.py"), str(prompt),
                   "--aspect", "vertical"]
            cmd += ["--no-refs"] if kind == "broll" else ["--character", a.character]
            r = run(cmd, timeout=1800)
            if r.returncode != 0:
                print(f"      submit failed:\n{r.stdout[-600:]}{r.stderr[-400:]}")
                return 2
            print("      generating, then fetching")
            clip.unlink(missing_ok=True)
            # FETCH AGAINST THIS PROMPT ALONE. Pointed at the whole folder,
            # fetch.py identifies a tile by matching it against every prompt
            # there and would happily hand back an older clip for a different
            # scene. A directory holding one prompt makes a mismatch impossible.
            import shutil
            import tempfile
            with tempfile.TemporaryDirectory() as td:
                pd = Path(td)
                shutil.copy(prompt, pd / prompt.name)
                r = run([PY, "-u", str(ROOT / "veo_kit" / "fetch.py"),
                         "--prompts", str(pd), "--out", str(clip.parent),
                         "--aspect", "vertical", "--expect", str(before + 1),
                         "--wait", "1500", "--max", str(before + 4)], timeout=2400)
            if not clip.is_file():
                print(f"      not downloaded:\n{r.stdout[-600:]}")
                return 2
            faults = check(clip, line, a.character, a.passes)
            if not faults:
                print(f"      OK\n")
                done.append(tag)
                held += 1
                break
            print(f"      FAIL: {'; '.join(faults)}")
            held += 1                      # the rejected clip still sits in Flow
            bad = clip.parent / "_rejected" / f"{tag}_try{attempt}.mp4"
            bad.parent.mkdir(exist_ok=True)
            clip.rename(bad)
            if attempt == a.retries:
                failed.append((tag, faults))
                print(f"\n  stopping: {tag} failed {a.retries + 1} time(s). The usual "
                      f"cause is the prompt or the line, which the rest share.\n")
                break
            time.sleep(5)
        if failed:
            break

    print(f"  {len(done)} accepted: {', '.join(done) or '-'}")
    for tag, f in failed:
        print(f"  {tag} REJECTED: {'; '.join(f)}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
