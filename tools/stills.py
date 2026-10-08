"""Review stills of a part WITHOUT compositing the whole video.

    python tools/stills.py <slug> <part> [--out sheet.png]

The point of stills is to see whether the video will come out right BEFORE the
expensive build (memory: frames-before-rendering). This needs only the Manim
render: for each beat it takes the scene frame and the presenter frame at the
same moment, holds each for one second, and runs the REAL compositor over just
those seconds — the real key, the real one-size placement, the real Veo panel
with its tear — then keeps the last frame of each second. A dozen stills cost a
dozen seconds of compositing instead of the whole part.

Also runs what can be judged from stills: the presenter-covers-content check
and the face match on these frames. Sound (sfx_gate) needs the full mix and is
checked on the real build.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.frames_sheet import main as _unused  # noqa: F401,E402  (keeps one shot rule)


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, capture_output=True, text=True, **kw)


def shots_for(lines, beats, dur):
    """Same moments as tools/frames_sheet.py: each beat as it lands, and as it ends."""
    shots = [(4.0, "card")]
    for b in beats:
        if b["type"] == "clear":
            continue
        i = int(b["at"])
        nxt = sorted(int(x["at"]) for x in beats if int(x["at"]) > i)
        end = float(lines[nxt[0]]["start"]) - 0.5 if nxt else dur - 0.5
        t_mid = float(lines[i]["start"]) + 1.2
        t_full = max(t_mid, end - 0.3)
        shots.append((t_mid, b["type"]))
        if t_full - t_mid > 2.5:
            shots.append((t_full, b["type"] + " (filled)"))
    shots.append((min(dur - 0.5, float(lines[-1]["start"]) + 1.0), "close"))
    return sorted(shots)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("part", type=int)
    ap.add_argument("--out", default="")
    a = ap.parse_args()
    proj = ROOT / "projects" / a.slug
    part = a.part
    inbox = ROOT / "inbox" / a.slug
    hg = inbox / f"part{part}.mp4" if (inbox / f"part{part}.mp4").is_file() else inbox / "heygen_full.mp4"
    body = proj / "manim_code" / "media" / "videos" / "pyq_composed" / "1920p30" / f"PyqPart_part{part}.mp4"
    if not body.is_file():
        raise SystemExit(f"no scene render at {body} — render the scene first")
    lines = json.loads((proj / f"lines_part{part}.json").read_text(encoding="utf-8"))
    beats = json.loads((proj / f"beats_part{part}.json").read_text(encoding="utf-8"))
    dur = float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                     "-of", "csv=p=0", str(hg)]).stdout)
    shots = shots_for(lines, beats, dur)
    W = proj / "work" / f"stills_part{part}"
    shutil.rmtree(W, ignore_errors=True)
    W.mkdir(parents=True)
    cj = proj / f"clips_part{part}.json"
    veo = json.loads(cj.read_text(encoding="utf-8")) if cj.is_file() else []
    env = dict(os.environ, PRESENTER_ONE_SIZE=os.environ.get("PRESENTER_ONE_SIZE", "505"))
    # ONE STILL AT A TIME. Compositing all the stills as a single clip built one
    # filtergraph carrying every panel, tear and key at once, and ffmpeg refused
    # it (exit 234). A second of video per still keeps each graph the size of a
    # real one, and the whole sheet still costs a fraction of a build.
    for k, (t, name) in enumerate(shots):
        run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", str(body), "-frames:v", "1",
             str(W / f"bg_{k:03d}.png")])
        run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", str(hg), "-frames:v", "1",
             str(W / f"hg_{k:03d}.png")])
        run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-i", str(W / f"bg_{k:03d}.png"),
             "-t", "2.0", "-r", "30", "-pix_fmt", "yuv420p", "-c:v", "libx264", "-crf", "16",
             str(W / f"bg_{k:03d}.mp4")])
        # THE PRESENTER CLIP NEEDS AN AUDIO TRACK. composite.py maps 1:a from it
        # (the narration rides along), and a silent still refused to encode at
        # all — "-map 1:a" with no audio stream is ffmpeg exit 234.
        run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-i", str(W / f"hg_{k:03d}.png"),
             "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-t", "2.0", "-r", "30",
             "-pix_fmt", "yuv420p", "-c:v", "libx264", "-crf", "16", "-c:a", "aac", "-shortest",
             str(W / f"hg_{k:03d}.mp4")])
        shot_clips = []
        for c in veo:
            if float(c["start"]) <= t <= float(c["end"]):
                srcf = proj / c["src"]
                run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t - float(c['start']):.2f}",
                     "-i", str(srcf), "-frames:v", "1", str(W / f"veo_{k:03d}.png")])
                run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-i", str(W / f"veo_{k:03d}.png"),
                     "-t", "2.0", "-r", "30", "-pix_fmt", "yuv420p", "-c:v", "libx264",
                     str(W / f"veo_{k:03d}.mp4")])
                # THE PANEL WINDOW MAY NOT START AT ZERO. composite builds the
                # tear's mask from a source whose LENGTH is the window's start
                # time, so a window at 0.0s gave an empty mask and most of the
                # panel stayed masked out — the still showed a sliver. Start the
                # window a second in and sample after the 0.55s tear finishes.
                shot_clips.append(dict(c, at=0, start=1.0, end=2.0, src=f"veo_{k:03d}.mp4", labels=[]))
        (W / f"clips_{k:03d}.json").write_text(json.dumps(shot_clips, ensure_ascii=False), encoding="utf-8")
        r = subprocess.run([sys.executable, "tools/composite.py", str(W / f"bg_{k:03d}.mp4"),
                            str(W / f"hg_{k:03d}.mp4"),
                            str(proj / "keys" / f"key_part{part}.json"), str(W / f"out_{k:03d}.mp4"),
                            "-", "-", str(W / f"clips_{k:03d}.json") if shot_clips else "-",
                            "-", "-", "-"],
                           cwd=ROOT, capture_output=True, text=True, env=env)
        if r.returncode:
            print((r.stdout + r.stderr)[-800:])
            raise SystemExit(f"composite failed on still {k} ({name})")
        # MID-WINDOW. A panel wipes IN at its window's start and OUT at its end,
        # so a sample near the end caught the tear leaving and showed a sliver.
        run(["ffmpeg", "-v", "error", "-y", "-ss", "1.45", "-i", str(W / f"out_{k:03d}.mp4"),
             "-frames:v", "1", str(W / f"still_{k:03d}.png")])
    # the gates that can be judged from stills want one file each
    for kind in ("bg", "out"):
        lst = W / f"{kind}.txt"
        lst.write_text("".join(f"file '{W / f'{kind}_{k:03d}.mp4'}'\n" for k in range(len(shots))))
        run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
             "-c", "copy", str(W / f"{kind}.mp4")])
    shutil.move(str(W / "out.mp4"), str(W / "keyed.mp4"))
    tiles = []
    font = ImageFont.load_default()
    for k, (t, name) in enumerate(shots):
        im = Image.open(W / f"still_{k:03d}.png").convert("RGB")
        im = im.resize((300, int(300 * im.height / im.width)))
        tile = Image.new("RGB", (im.width, im.height + 20), (0, 0, 0))
        tile.paste(im, (0, 0))
        ImageDraw.Draw(tile).text((4, im.height + 4), f"{t:6.1f}s  {name}", fill=(255, 220, 90), font=font)
        tiles.append(tile)
    cols = 6
    w, h = tiles[0].size
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (w + 6) + 6, rows * (h + 6) + 6), (20, 20, 24))
    for n, im in enumerate(tiles):
        sheet.paste(im, (6 + (n % cols) * (w + 6), 6 + (n // cols) * (h + 6)))
    out = Path(a.out) if a.out else W / "sheet.png"
    sheet.save(out)
    print(f"  {len(tiles)} stills -> {out}")
    # what stills can prove: nothing covered, and it is him
    tools_py = str(ROOT / ".venv-tools" / "bin" / "python")
    for gate, args in (("avatar_cover_gate", [str(ROOT / "tools" / "avatar_cover_gate.py"),
                                               str(W / "bg.mp4"), str(W / "keyed.mp4")]),
                       ("face_gate", [str(ROOT / "veo_kit" / "face_gate.py"), str(W / "keyed.mp4"),
                                      "--at", *[f"{k * 2.0 + 1.45:.2f}" for k in range(len(shots))]])):
        g = subprocess.run([tools_py, *args], cwd=ROOT, capture_output=True, text=True)
        tail = [l for l in (g.stdout + g.stderr).splitlines() if l.strip() and "Warning" not in l][-1:]
        print(f"  {'ok  ' if g.returncode == 0 else 'FAIL'} {gate:18s} {tail[0].strip() if tail else ''}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
