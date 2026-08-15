"""Check everything a render depends on, before spending an hour on it.

Every check here exists because the corresponding bug reached a finished video
and had to be found by watching it. They are all mechanical, so none of them
should ever be found that way again.

    python tools/preflight.py                    # every project
    python tools/preflight.py daniell-cell       # one

Exit code is 1 if anything FAILED, so it can gate a render in a script.
"""
from __future__ import annotations

import ast
import json
import re
import subprocess
import sys
from pathlib import Path

OK, WARN, FAIL = "ok", "warn", "FAIL"
CLIP_TAIL = 2.5          # a caption may not start this close to the end
MAX_GAP = 4.0            # transcript hole worth reporting
CAPTION_MIN_MARGIN = 0.03   # of frame width, each side


class Report:
    def __init__(self):
        self.rows: list[tuple[str, str, str]] = []

    def add(self, level, check, detail=""):
        self.rows.append((level, check, detail))

    @property
    def failed(self):
        return any(r[0] == FAIL for r in self.rows)

    def show(self, title):
        bad = [r for r in self.rows if r[0] != OK]
        mark = "FAIL" if self.failed else ("warn" if bad else "ok")
        print(f"\n[{mark}] {title}")
        for level, check, detail in self.rows:
            if level == OK:
                continue
            print(f"   {level:>4}  {check}" + (f" — {detail}" if detail else ""))
        if not bad:
            print(f"   all {len(self.rows)} checks passed")


# --------------------------------------------------------------------------- #
def is_avatar_track(root: Path) -> bool:
    """This checker is for the avatar-synced track, not the older reels track.

    A reels project has generated `segment_*.py` and no caption track; checking
    it for a composed scene reports a failure that means nothing.
    """
    return any(root.glob("lines*.json")) or any(
        f for f in root.glob("manim_code/*.py")
        if not f.name.startswith("segment_") and not f.name.endswith("_composed.py"))


def check_composed(root: Path, rep: Report):
    """The composed file must parse AND still contain the whole scene.

    A regex in recompose.py once matched with DOTALL and deleted from its line
    to the end of the file. The result still parsed — it was simply missing most
    of the scene — and would have rendered a short, wrong video.
    """
    for src in root.glob("manim_code/*.py"):
        if src.name.endswith("_composed.py") or src.name.startswith("segment_"):
            continue
        comps = list(root.glob("manim_code/*_composed.py"))
        if not comps:
            rep.add(FAIL, "composed file", f"none built from {src.name}")
            return
        for comp in comps:
            text = comp.read_text(encoding="utf-8")
            try:
                ast.parse(text)
            except SyntaxError as e:
                rep.add(FAIL, f"{comp.name} parses", f"line {e.lineno}: {e.msg}")
                continue
            want = {n.name for n in ast.walk(ast.parse(src.read_text(encoding="utf-8")))
                    if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
            got = {n.name for n in ast.walk(ast.parse(text))
                   if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
            missing = want - got
            if missing:
                rep.add(FAIL, f"{comp.name} complete",
                        f"lost {len(missing)}: {sorted(missing)[:6]}")
            else:
                rep.add(OK, f"{comp.name} complete")


def check_no_stored_paths(root: Path, rep: Report):
    """Animating along remembered coordinates is always a bug.

    `place()` scales and moves a group; a point list captured beforehand does
    not follow, and the animation runs somewhere visibly wrong. In the Daniell
    cell the electrons crossed the gap between the beakers through the air.
    """
    for src in root.glob("manim_code/*.py"):
        if src.name.endswith("_composed.py"):
            continue
        text = src.read_text(encoding="utf-8")
        for m in re.finditer(r"MoveAlongPath\([^)]*\)", text):
            call = m.group(0)
            line = text[:m.start()].count("\n") + 1
            # the path argument should trace back to along(); flag the shapes
            # that historically did not
            if "_path" in call and "along(" not in call:
                rep.add(FAIL, "MoveAlongPath uses a stored point list",
                        f"{src.name}:{line} — use along(<the mobject>)")
        if re.search(r"\.\w*_path\s*=\s*\[", text):
            line = text[:re.search(r"\.\w*_path\s*=\s*\[", text).start()].count("\n") + 1
            rep.add(WARN, "a path is stored as coordinates",
                    f"{src.name}:{line} — it will not follow place()/scale()")
        if not any(rep.rows):
            pass
    rep.add(OK, "no stored-coordinate paths")


def check_captions(root: Path, rep: Report):
    for lines_f in sorted(root.glob("lines*.json")):
        try:
            lines = json.loads(lines_f.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            rep.add(FAIL, f"{lines_f.name} parses", str(e))
            continue
        if not lines:
            rep.add(FAIL, f"{lines_f.name} non-empty")
            continue

        if any("end" not in l for l in lines):
            rep.add(FAIL, f"{lines_f.name} has end times",
                    "without one a caption lingers until the next line replaces it")
        bad = [i for i in range(1, len(lines))
               if lines[i]["start"] <= lines[i - 1]["start"]]
        if bad:
            rep.add(FAIL, f"{lines_f.name} monotonic", f"{len(bad)} out of order")
        latin = [l["text"] for l in lines if re.search(r"[A-Za-z]{3,}", l["text"])]
        if latin:
            rep.add(WARN, f"{lines_f.name} Latin runs",
                    f"{len(latin)}, e.g. {latin[0][:44]}")

        # captions must not run past the audio they belong to
        words_f = root / lines_f.name.replace("lines", "words")
        if words_f.exists():
            words = json.loads(words_f.read_text(encoding="utf-8"))
            audio_end = words[-1]["e"]
            over = [l for l in lines if l["start"] > audio_end - 0.2]
            if over:
                rep.add(FAIL, f"{lines_f.name} within audio",
                        f"{len(over)} line(s) start after the audio ends")
            cov_gap = [l for l in lines if l.get("end", 0) - l["start"] > 12]
            if cov_gap:
                rep.add(WARN, f"{lines_f.name} long holds",
                        f"{len(cov_gap)} line(s) held over 12s")
        rep.add(OK, f"{lines_f.name}")


def check_transcripts(root: Path, rep: Report):
    for words_f in sorted(root.glob("words*.json")):
        words = json.loads(words_f.read_text(encoding="utf-8"))
        if not words:
            rep.add(FAIL, f"{words_f.name} non-empty")
            continue
        gaps = [(words[i]["e"], words[i + 1]["s"]) for i in range(len(words) - 1)
                if words[i + 1]["s"] - words[i]["e"] > MAX_GAP]
        if gaps:
            rep.add(FAIL, f"{words_f.name} has no holes",
                    f"{len(gaps)} gap(s), largest {max(b-a for a,b in gaps):.1f}s "
                    f"— run tools/fill_gaps.py")
        else:
            rep.add(OK, f"{words_f.name}")


def check_keys(root: Path, rep: Report):
    for key_f in sorted((root / "keys").glob("*.json")) if (root / "keys").exists() else []:
        k = json.loads(key_f.read_text(encoding="utf-8"))
        need = {"hue", "sat", "v1", "v2", "sim"}
        if not need <= set(k):
            rep.add(FAIL, f"keys/{key_f.name} complete", f"missing {need - set(k)}")
            continue
        if not 70 <= k["hue"] <= 110:
            rep.add(FAIL, f"keys/{key_f.name} hue", f"{k['hue']} is not green")
        if k.get("hole", 0) > 0.5:
            rep.add(FAIL, f"keys/{key_f.name} holes", f"{k['hole']}% of the presenter")
        if k.get("leak", 0) > 0.5:
            rep.add(WARN, f"keys/{key_f.name} leak", f"{k['leak']}% green left")
        rep.add(OK, f"keys/{key_f.name}")


def check_timing(root: Path, rep: Report):
    for t_f in sorted(root.glob("timing*.json")):
        cues = json.loads(t_f.read_text(encoding="utf-8"))
        bad = [i for i in range(1, len(cues)) if cues[i]["start"] <= cues[i - 1]["start"]]
        if bad:
            rep.add(FAIL, f"{t_f.name} monotonic", f"{len(bad)} out of order")
        else:
            rep.add(OK, f"{t_f.name}")


def check_windows(root: Path, rep: Report):
    for w_f in sorted(root.glob("windows*.json")):
        wins = json.loads(w_f.read_text(encoding="utf-8"))
        for a, b in wins:
            if b <= a:
                rep.add(FAIL, f"{w_f.name} ordered", f"[{a}, {b}]")
        rep.add(OK, f"{w_f.name}", f"{len(wins)} resize window(s)")


def check_images(root: Path, rep: Report):
    """A generated illustration must carry real alpha, or it composites as a
    hard rectangle on the plate."""
    for img in sorted((root / "images").glob("*.png")) if (root / "images").exists() else []:
        try:
            from PIL import Image
            im = Image.open(img)
        except Exception as e:
            rep.add(WARN, f"images/{img.name}", str(e)); continue
        if im.mode != "RGBA":
            rep.add(FAIL, f"images/{img.name} has alpha", f"mode is {im.mode}")
        else:
            import numpy as np
            a = np.asarray(im)[..., 3]
            if (a < 10).mean() < 0.05:
                rep.add(FAIL, f"images/{img.name} background cut",
                        "almost nothing is transparent")
            else:
                rep.add(OK, f"images/{img.name}")


def check_caption_margins(root: Path, rep: Report):
    """No caption may run to the frame edge.

    A wrap limit is only a limit if the wrapper measures what will actually be
    drawn. The one that shipped summed word widths and added a space — and Manim
    reports a space as 0.0000 wide, because it measures ink and a space has
    none. Spaces therefore cost nothing, every line took one word too many, and
    a 92% limit produced captions 4px from a 1080px edge. Nothing failed; it
    just looked wrong, which is exactly the class of bug this file exists for.

    Measured off the render rather than the source, so it holds however the
    scene was written.
    """
    import io

    import numpy as np
    from PIL import Image

    for video in sorted(root.glob("media/videos/**/*.mp4")):
        worst, at = 1.0, 0.0
        for t in range(3, 120, 6):
            raw = subprocess.run(
                ["ffmpeg", "-v", "error", "-ss", str(t), "-i", str(video),
                 "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-"],
                capture_output=True).stdout
            if not raw:
                break
            a = np.asarray(Image.open(io.BytesIO(raw)).convert("L")).astype(int)
            h, w = a.shape
            strip = a[int(h * 0.03):int(h * 0.16)]
            cols = np.nonzero((strip > 170).sum(axis=0) > 2)[0]
            if len(cols) < 10:
                continue
            margin = min(cols[0], w - 1 - cols[-1]) / w
            if margin < worst:
                worst, at = margin, t
        if worst > 0.5:
            continue                        # no caption found; nothing to judge
        name = f"{video.stem} caption margin"
        if worst < CAPTION_MIN_MARGIN:
            rep.add(FAIL, name, f"{worst * 100:.2f}% at {at:.0f}s "
                                f"(want >= {CAPTION_MIN_MARGIN * 100:.0f}%)")
        else:
            rep.add(OK, name, f"{worst * 100:.2f}% at {at:.0f}s")


def preflight(root: Path) -> Report:
    rep = Report()
    check_composed(root, rep)
    check_no_stored_paths(root, rep)
    check_transcripts(root, rep)
    check_captions(root, rep)
    check_timing(root, rep)
    check_keys(root, rep)
    check_windows(root, rep)
    check_images(root, rep)
    check_caption_margins(root, rep)
    return rep


if __name__ == "__main__":
    roots = ([Path("projects") / a for a in sys.argv[1:]] or
             [p for p in sorted(Path("projects").iterdir())
              if p.is_dir() and is_avatar_track(p)])
    failed = False
    for root in roots:
        rep = preflight(root)
        rep.show(root.name)
        failed |= rep.failed
    print()
    sys.exit(1 if failed else 0)
