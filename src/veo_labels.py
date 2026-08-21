"""Typeset the labels that go over a Veo clip.

WHY THE LABELS ARE NOT IN THE CLIP
----------------------------------
Because they cannot be. Every label in this track is Devanagari, and no video
model sets Devanagari — it produces letterforms that look like Hindi to someone
who does not read Hindi, which is worse than producing none. So the generated
clip carries the animation and nothing written on it at all (that rule is
enforced in `src/veo_prompts.py` and graded in `src/veo_qc.py`), and the naming
happens here, in Khand, at the right size, over the top.

That is not a workaround, it is the better arrangement. A generated label is
stuck to the frame it was generated in. One typeset here can arrive on the exact
caption that names the part — which is the rule the rest of this pipeline
already works to (`figure-label-sync`, and `tools/check_labels.py`). A label
that appears before the teacher has said the word is a label the student reads
instead of listening to.

WHY PILLOW AND NOT MANIM
------------------------
The Manim render happens once, for the whole part, and it draws NOTHING during a
video beat — a Veo clip is laid over those frames afterwards, so anything Manim
drew there would be underneath it. Rendering the part twice to get a transparent
label pass would cost an entire render for a few words. Pillow writes a
transparent PNG in milliseconds and `overlay ... enable=` places it, which is the
same mechanism the presenter fades already use.

THE THING THAT SILENTLY BREAKS THIS
-----------------------------------
Pillow without libraqm has no complex-script shaping: it draws codepoints in
storage order, so `विद्युत्` comes out `वदि्युत्` — the matra after its consonant
instead of before it. Nothing raises, and it is easy to read past. `_check_shaping`
refuses to run rather than write a garbled label into a finished video. See
CLAUDE.md for the fix.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FONT_DIR = ROOT / "assets" / "fonts"

# Khand Bold, matching the scene template's FONT/FONT_W, so a label over a Veo
# clip and a label over a Manim diagram are visibly the same voice.
FONT = FONT_DIR / "Khand-Bold.ttf"

FRAME_W, FRAME_H = 1080, 1920
INK = "#FFFFFF"
GOLD = "#FFC15C"
HALO = (0, 0, 0, 190)        # the animation underneath is arbitrary, so every
                             # label carries its own contrast rather than hoping
DEFAULT_SIZE = 0.026         # of frame height; ~50px, a touch under the caption
FADE = 0.35


def _check_shaping() -> None:
    from PIL import features
    if not features.check("raqm"):
        raise SystemExit(
            "❌ Pillow has no libraqm, so it cannot shape Devanagari — a label "
            "written now would be garbled in a way nothing downstream detects.\n"
            "   brew install libraqm\n"
            "   pip install pybind11 && pip install --force-reinstall "
            "--no-binary Pillow --no-build-isolation pillow")


def render(text: str, px: int, colour: str = INK):
    """One label, shaped, on transparency, with a soft dark halo behind it."""
    from PIL import Image, ImageDraw, ImageFont, ImageFilter

    _check_shaping()
    font = ImageFont.truetype(str(FONT), px)
    probe = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    x0, y0, x1, y1 = probe.textbbox((0, 0), text, font=font)
    pad = max(10, px // 3)          # room for the blur, or it clips at the edges
    img = Image.new("RGBA", (x1 - x0 + pad * 2, y1 - y0 + pad * 2), (0, 0, 0, 0))

    # The halo is the text drawn thick, blurred, and composited under itself.
    # A stroke alone is not enough over a bright animation, and a solid plate
    # behind the word would cover the thing being labelled.
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(glow).text((pad - x0, pad - y0), text, font=font, fill=HALO,
                              stroke_width=max(2, px // 12), stroke_fill=HALO)
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(px / 10)))
    ImageDraw.Draw(img).text((pad - x0, pad - y0), text, font=font, fill=colour)
    return img


def build(beat: dict, lines: list[dict], start: float, end: float,
          out_dir: Path, tag: str) -> list[dict]:
    """Render a video beat's labels and return overlay specs for the compositor.

    `x`/`y` are fractions of the FRAME, not of the clip — a Veo clip has no
    stable internal geometry to anchor to, so a label is placed where it should
    land on screen and checked against the frame's reserved bands.

    Each label arrives on the caption that names it (`at`) and stays for the
    rest of the clip. A label with no `at` is up for the whole window.
    """
    out = []
    for i, spec in enumerate(beat.get("labels") or []):
        text = str(spec.get("text", "")).strip()
        if not text:
            continue
        px = max(18, int(float(spec.get("size", DEFAULT_SIZE)) * FRAME_H))
        img = render(text, px, spec.get("colour", INK))
        dest = out_dir / f"{tag}_label{i:02d}.png"
        dest.parent.mkdir(parents=True, exist_ok=True)
        img.save(dest)

        at = spec.get("at")
        appears = start if at is None else float(
            lines[max(0, min(int(at), len(lines) - 1))]["start"])
        # A label may not arrive before the clip it names, and may not outlive it.
        appears = min(max(appears, start), max(start, end - 0.4))

        align = spec.get("align", "c")
        cx = float(spec.get("x", 0.5)) * FRAME_W
        x = {"l": cx, "r": cx - img.width, "c": cx - img.width / 2}[align]
        y = float(spec.get("y", 0.6)) * FRAME_H - img.height / 2
        out.append({
            "png": str(dest),
            "x": int(round(x)), "y": int(round(y)),
            "w": img.width, "h": img.height,
            "start": round(appears, 2), "end": round(end, 2),
            "text": text,
        })
    return out
