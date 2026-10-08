"""Make a downloaded Flow clip ready to lay into a PYQ part, and register it.

    python tools/prep_veo_clip.py <slug> <part> <raw.mp4> --at <line> [--until <line>]
        [--from 0.0] [--mark 1132,572,56,56] [--top 160]

* COVERS FLOW'S SPARKLE. Flow burns a four-pointed marker into every clip after
  generation, so no prompt removes it. Its place depends on the SHAPE: centred
  at about (1160, 600) on a 1280x720 clip and (604, 1159) on a 720x1280 one.
  The default is chosen from the clip; `--mark x,y,w,h` overrides. Look at the
  result — and tools/veo_logo_gate.py checks it.
* FITS THE WINDOW, never by reversing (a reversed birth or a family un-laughing
  is wrong in a way that looks fine). The window runs from the start of line
  `--at` to the start of line `--until` (default: the next beat's line). A clip
  longer than the window is cut from `--from`; a shorter one is SLOWED up to
  1.35x and then held on its last frame.
* SILENT. The narration is the only audio; Veo's own track is dropped.
* Registers the clip in clips_part<N>.json as a torn-paper PANEL whose top sits
  below the one-line caption (`--top`, px), which the compositor lays in.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# WHERE FLOW PUTS ITS SPARKLE, per output shape — measured, not guessed. It is
# NOT the same corner in a tall frame: on 1280x720 it sits at (1160, 600) and on
# 720x1280 at (604, 1159), so a landscape box on a vertical clip covers green
# and leaves the mark on screen. tools/veo_logo_gate.py catches that.
MARK = {"landscape": (1132, 572, 56, 56), "vertical": (576, 1131, 56, 56)}
MAX_SLOW = 1.35


def dur(p) -> float:
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                 "-of", "csv=p=0", str(p)], capture_output=True, text=True).stdout)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("part", type=int)
    ap.add_argument("raw")
    ap.add_argument("--at", type=int, required=True)
    ap.add_argument("--until", type=int)
    ap.add_argument("--from", dest="t0", type=float, default=0.0)
    ap.add_argument("--mark", default="", help="x,y,w,h; default: by the clip's shape")
    ap.add_argument("--top", type=int, default=160)
    a = ap.parse_args()

    proj = ROOT / "projects" / a.slug
    lines = json.loads((proj / f"lines_part{a.part}.json").read_text(encoding="utf-8"))
    beats = json.loads((proj / f"beats_part{a.part}.json").read_text(encoding="utf-8"))
    until = a.until
    if until is None:
        later = sorted(int(b["at"]) for b in beats if int(b["at"]) > a.at)
        until = later[0] if later else len(lines)
    start = float(lines[a.at]["start"]) - 0.35          # the beat turns over 0.35s early
    end = float(lines[until]["start"]) - 0.35 if until < len(lines) else float(lines[-1]["end"])
    win = end - start
    src_len = dur(a.raw) - a.t0
    if a.mark:
        x, y, w, h = map(int, a.mark.split(","))
    else:
        dims = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                               "-show_entries", "stream=width,height", "-of", "csv=p=0",
                               a.raw], capture_output=True, text=True).stdout.strip()
        cw, chh = (int(v) for v in dims.split(",")[:2])
        x, y, w, h = MARK["vertical" if chh > cw else "landscape"]
    out = proj / "veo" / f"part{a.part}_at{a.at:03d}.mp4"
    out.parent.mkdir(parents=True, exist_ok=True)
    if src_len >= win:
        speed, note = 1.0, f"cut {src_len:.2f}s to {win:.2f}s from {a.t0:.2f}s"
        vf = f"delogo=x={x}:y={y}:w={w}:h={h},fps=30"
    else:
        speed = min(MAX_SLOW, win / src_len)
        hold = max(0.0, win - src_len * speed)
        note = f"slowed x{speed:.2f}" + (f", held last frame {hold:.2f}s" if hold > 0.02 else "")
        vf = (f"delogo=x={x}:y={y}:w={w}:h={h},setpts={speed:.4f}*PTS,fps=30"
              + (f",tpad=stop_mode=clone:stop_duration={hold:.3f}" if hold > 0.02 else ""))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a.t0:.3f}", "-i", a.raw,
                    "-vf", vf, "-t", f"{win:.3f}", "-an", "-c:v", "libx264", "-preset", "medium",
                    "-crf", "16", "-pix_fmt", "yuv420p", str(out)], check=True)
    got = dur(out)
    cj = proj / f"clips_part{a.part}.json"
    clips = json.loads(cj.read_text(encoding="utf-8")) if cj.is_file() else []
    clips = [c for c in clips if int(c["at"]) != a.at]
    clips.append({"at": a.at, "start": round(start, 3), "end": round(end, 3),
                  "src": str(out.relative_to(proj)), "raw": str(Path(a.raw)),
                  "full": False, "frame": "partial", "layout": "panel", "green": False,
                  "backdrop": "own", "panel_ar": 1280 / 720, "panel_top": a.top,
                  # the box covered, so tools/veo_logo_gate.py can check THIS
                  # clip rather than guessing what a watermark looks like
                  "mark": [x, y, w, h], "labels": []})
    clips.sort(key=lambda c: c["start"])
    cj.write_text(json.dumps(clips, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"  {out.relative_to(ROOT)}: window {start:.2f}-{end:.2f}s ({win:.2f}s), {note}; "
          f"file {got:.2f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
