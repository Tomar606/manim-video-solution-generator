"""Caption an all-Veo reel: one line at a time, on a vignette at the foot.

    python tools/reel_captions.py <slug> [--only s03] [--size 46]

Writes, per scene, projects/<slug>/work/captions/<id>/NNN.png and a
captions.json the reel builder overlays. Nothing is burned in here.

WHY THE CAPTIONS SIT AT THE BOTTOM, not the top
------------------------------------------------
The PYQ reference look puts one line across the TOP, which works because the
presenter is a small figure at the foot of a mostly-empty frame. This route is
the opposite: a Veo scene is a full-frame shot with his head near the top, so a
caption up there lands on his face. It goes at the foot, over a vignette that is
dark at the very bottom edge and fully transparent by the time it reaches him —
a scrim, not a bar, so it never reads as a band stuck over the picture.

WHY A VIGNETTE AT ALL. These are photographic backgrounds: a market, a lit
corridor, a white committee table. White text over any of them is unreadable
somewhere in the clip, and an outline or a drop shadow on Devanagari thickens
the matras until the word changes. Darkening what is behind the text is the only
treatment that leaves the letterforms alone.

TIMING COMES FROM THE AUDIO, never from dividing the clip up. Each clip is
transcribed for word timings and the line's chunks are anchored onto them with
tools.align — the same global aligner the PYQ captions use. A chunk that cannot
be placed is interpolated between its neighbours rather than guessed at.

SHAPING. Devanagari is drawn by Pillow, which needs libraqm or it lays the
codepoints out in storage order and every i-matra sits after its consonant
instead of before it — silently (memory: pillow-raqm-needs-dyld). This refuses
to run without it rather than write a folder of wrong pictures.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, features

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools import align as AL  # noqa: E402

FONT = ROOT / "assets" / "fonts" / "NotoSansDevanagari.ttf"
# WEIGHT AND A BORDER. The docstring below warns that an outline thickens
# Devanagari matras until the word changes, and that is true of a heavy one —
# so this is a THIN dark stroke, about a sixteenth of the type size, which
# separates the letters from a bright plate without closing up the counters.
# Checked by eye on a frame before it went in.
STROKE = 0.062           # stroke width as a share of the type size
STROKE_INK = (12, 16, 24)
INK = (255, 255, 255)
GOLD = (232, 176, 74)
# BIGGER THAN IT LOOKS ON A DESKTOP. At 46px on a 1080-wide frame a caption is
# 4% of the frame width; on the phone these are watched on that is smaller than
# the delivered videos' own captions. 62px matches them, and the chunk limit
# drops with it so a line still fits across the frame at the larger size — the
# two numbers are one decision, not two.
MAX_CHARS = 26          # one line at this size, comfortably inside the frame
SCRIM = 0.26            # share of the frame height the vignette covers
SCRIM_MAX = 0.88        # opacity at the very bottom edge


def screen_text(s: str) -> str:
    """The spoken line as it may appear ON SCREEN.

    A dash is fine in the script — it tells the reader where to breathe, and
    Veo reads it as a pause. On screen it is refused: no screen text in this
    series carries a long dash (memory: screen-text-conventions), and
    tools/gates.py has a dash_gate that fails the build over one. The spoken
    line is left alone; only the caption drawn from it is changed.
    """
    for d in ("\u2014", "\u2013"):
        s = s.replace(f" {d} ", ", ").replace(d, ",")
    return " ".join(s.split())


def chunks(text: str, limit: int = MAX_CHARS) -> list[str]:
    """Split at the word boundary nearest the middle, repeatedly."""
    if len(text) <= limit:
        return [text]
    words = text.split()
    if len(words) < 2:
        return [text]
    best, bk = None, 1
    for k in range(1, len(words)):
        d = abs(len(" ".join(words[:k])) - len(" ".join(words[k:])))
        if best is None or d < best:
            best, bk = d, k
    return chunks(" ".join(words[:bk]), limit) + chunks(" ".join(words[bk:]), limit)


def vignette(w: int, h: int) -> Image.Image:
    """Black at the bottom edge, gone by the top of the scrim. Not a bar."""
    g = Image.new("L", (1, h), 0)
    px = g.load()
    top = int(h * (1 - SCRIM))
    for y in range(top, h):
        f = (y - top) / max(1, h - 1 - top)
        px[0, y] = int(255 * SCRIM_MAX * (f ** 1.6))     # eased, so no visible edge
    band = g.resize((w, h))
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    out.putalpha(band)
    return out


def draw_line(text: str, hilite: set[str], size: int, w: int) -> Image.Image:
    f = ImageFont.truetype(str(FONT), size)
    probe = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    parts = [(t, any(k and k in t for k in hilite)) for t in text.split()]
    widths = [probe.textlength(t + " ", font=f) for t, _ in parts]
    sw = max(2, int(size * STROKE))
    total = sum(widths)
    im = Image.new("RGBA", (max(1, int(total) + size + 2 * sw), int(size * 2.2)),
                   (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x, base = size // 2, int(size * 1.5)
    for (t, hot), adv in zip(parts, widths):
        d.text((x, base), t, font=f, fill=(GOLD if hot else INK) + (255,), anchor="ls",
               stroke_width=sw, stroke_fill=STROKE_INK + (255,))
        x += adv
    bb = im.getbbox()
    return im.crop(bb) if bb else im


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--only", nargs="*", default=[])
    ap.add_argument("--size", type=int, default=62)
    ap.add_argument("--model", default="small")
    a = ap.parse_args()
    if not features.check("raqm"):
        print("  Pillow has no raqm, so Devanagari would be laid out in storage "
              "order and every i-matra would sit after its consonant. Run with "
              "DYLD_LIBRARY_PATH=/opt/homebrew/lib (memory: pillow-raqm-needs-dyld).")
        return 1

    proj = ROOT / "projects" / a.slug
    spec = json.loads((proj / "reel.json").read_text(encoding="utf-8"))
    lines = json.loads((proj / "lines.json").read_text(encoding="utf-8"))
    meta = json.loads((proj / "meta.json").read_text(encoding="utf-8")) \
        if (proj / "meta.json").is_file() else {}
    hil = set(meta.get("hilite", []))
    FW, FH = (int(v) for v in spec.get("frame", "1080x1920").lower().split("x"))
    out = proj / "work" / "captions"
    out.mkdir(parents=True, exist_ok=True)
    vignette(FW, FH).save(out / "vignette.png")

    # WORD TIMINGS COME FROM THE SHARED CACHE when it is there, so the captions
    # sit on exactly the clock tools/reel_trim.py measured the dead air against.
    # Transcribing again would give a different answer — Whisper is not
    # deterministic on this audio — and the captions would drift against the trim.
    wj = proj / "work" / "words.json"
    cache = json.loads(wj.read_text(encoding="utf-8")) if wj.is_file() else {}
    m = None
    doc = {}
    for s in spec["scenes"]:
        sid = s["id"]
        if a.only and sid not in a.only:
            continue
        clip = proj / "veo" / "clips" / f"{sid}.mp4"
        if not clip.is_file():
            print(f"  {sid}: no clip")
            continue
        line = screen_text(lines.get(str(int(sid[1:])), ""))
        cs = chunks(line)
        if sid in cache:
            words = cache[sid]["words"]
            dur = float(cache[sid]["dur"])
        else:
            if m is None:
                import whisper
                m = whisper.load_model(a.model)
            r = m.transcribe(str(clip), language="hi", condition_on_previous_text=False,
                             word_timestamps=True, fp16=False)
            words = [{"w": w["word"], "s": float(w["start"]), "e": float(w["end"])}
                     for seg in r["segments"] for w in seg.get("words", [])]
            dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                                        "format=duration", "-of", "csv=p=0", str(clip)],
                                       capture_output=True, text=True).stdout or 10)
        # a trim moves the clip's clock; the captions move with it
        head = float((s.get("trim") or [0.0, 0.0])[0])
        if head:
            words = [dict(w, s=w["s"] - head, e=w["e"] - head) for w in words]
            dur -= head + float((s.get("trim") or [0.0, 0.0])[1])
        starts, ratio, _ = AL.anchor(cs, words) if words else ([None] * len(cs), 0.0, {})
        # interpolate what could not be anchored, then force it forward
        first = words[0]["s"] if words else 0.4
        last = words[-1]["e"] if words else dur - 0.4
        known = [(i, t) for i, t in enumerate(starts) if t is not None]
        if not known:
            step = (last - first) / max(1, len(cs))
            starts = [first + i * step for i in range(len(cs))]
        else:
            for i in range(len(starts)):
                if starts[i] is not None:
                    continue
                lo = max([k for k, _ in known if k < i], default=None)
                hi = min([k for k, _ in known if k > i], default=None)
                if lo is None:
                    starts[i] = max(0.0, dict(known)[hi] - 0.6 * (hi - i))
                elif hi is None:
                    starts[i] = dict(known)[lo] + 0.6 * (i - lo)
                else:
                    t0, t1 = dict(known)[lo], dict(known)[hi]
                    starts[i] = t0 + (t1 - t0) * (i - lo) / (hi - lo)
        starts = AL.monotonic(starts)
        ends = [min(starts[i + 1], dur) if i + 1 < len(starts) else min(last + 0.45, dur)
                for i in range(len(starts))]

        d = out / sid
        d.mkdir(exist_ok=True)
        evs = []
        for i, (c, t0, t1) in enumerate(zip(cs, starts, ends)):
            im = draw_line(c, hil, a.size, FW)
            if im.width > FW * 0.90:
                im = im.resize((int(FW * 0.90), int(im.height * FW * 0.90 / im.width)),
                               Image.LANCZOS)
            p = d / f"{i:03d}.png"
            im.save(p)
            evs.append({"start": round(max(0.0, t0), 2), "end": round(max(t0 + 0.4, t1), 2),
                        "png": str(p.relative_to(proj)), "text": c})
        doc[sid] = evs
        print(f"  {sid}: {len(cs)} chunk(s), aligned {ratio:.2f}, "
              f"{evs[0]['start']:.1f}s..{evs[-1]['end']:.1f}s")
    cj = proj / "captions.json"
    old = json.loads(cj.read_text(encoding="utf-8")) if cj.is_file() else {}
    old.update(doc)
    cj.write_text(json.dumps(old, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"\n  {len(doc)} scene(s) -> {cj.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
