#!/usr/bin/env python3
"""Put THIS video's question on the MP Board paper, without garbling it.

    python tools/question_card.py --base <sheet.png> --question "..." \
        --out <out.png> [--year 2019] [--renderer work/<slug>/renderer]

WHY THIS EXISTS ALONGSIDE paper_header.py
-----------------------------------------
`paper_header.py` does the same job and cannot run here, for two reasons:

  * it wants `inbox/sticky_note_design.png`, which is not in the repo;
  * it typesets the question with PIL, and **PIL on this machine has no
    complex-script shaping** — `PIL.features.check("raqm")` is False, with
    harfbuzz and fribidi both absent.

The second one is the dangerous half. Without raqm, Pillow draws Devanagari in
STORAGE order: every matra lands after its consonant instead of around it, so
`विद्युत्` sets as `वदि्युत्` and `नियम` as `नयिम`. Nothing errors and the
result looks like type until you read it. CLAUDE.md calls this out precisely
because it is easy to read past, and a question card is the one frame a student
looks at longest.

So the text is set by the thing in this repo that demonstrably sets Devanagari
correctly — the headless-Chromium renderer that draws every caption in the
video — and PIL is used only to move pixels around: erase the old ink, paste
the new.

WHAT IS KEPT FROM THE BASE SHEET
--------------------------------
Everything except the question and the year. The paper is photographed: creased,
unevenly lit, torn along two edges and rotated about 2.7 degrees. None of that
survives being redrawn, so the old ink is inpainted away by interpolating down
each column (which follows the shading instead of flattening it) and the new
line is rotated to match the sheet before it is pasted.

The subject line is NOT touched. Every sheet in this repo already reads
`जीव विज्ञान — BIOLOGY`, which is correct for a biology video; rewriting it
would mean setting Devanagari with PIL, which is the thing this file exists to
avoid.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Measured off the approved design by paper_header.py; re-used rather than
# re-derived so the two files cannot drift.
from tools.paper_header import TILT_DEG, inpaint_band  # noqa: E402

# MEASURED ON THE SHEET BEING EDITED, not inherited.
#
# paper_header's Q_BAND/Q_TOP/Q_BOTTOM were measured on a different sheet, and
# borrowing them here cleared the wrong rectangle: the inpainter found its
# "clean" rows inside the fold and flattened a pale block across the paper,
# which is the exact failure its own docstring warns about. These come from a
# column/row ink profile of inbox/BIO-C12-LA-02_bundle/card/question_sheet.png:
#
#   (1)            x  181- 262
#   question ink   x  326- 956   y  848-1112
#   year digits    x  718- 788   y  516- 548
#
# The bands are those plus a small margin, and no more: clearing further right
# or further down reaches the diagonal fold and the torn corner.
Q_BAND    = (300, 838, 1010, 1132)
Q_LEFT    = 326
Q_TOP     = 848
Q_BOTTOM  = 1112
Q_INK_H   = 90
YEAR_BAND = (724, 503, 800, 543)   # erase box: the digits plus a small margin
YEAR_INK_LEFT   = 730              # '2026' ink, measured: x 730-789
YEAR_INK_BOTTOM = 535              # bottom of its lowest (leftmost) digit
YEAR_INK_W      = 60               # '2026' ink width, measured - sets the type size

PAGE = """<!doctype html><meta charset="utf-8">
<style>
  @font-face {{ font-family:Mukta; src:url("{font}") format("woff2");
               font-weight:700; font-display:block }}
  html,body {{ margin:0; background:transparent }}
  #q {{ font-family:{family}; font-weight:700;
        color:rgb({r},{g},{b}); font-size:{size}px; line-height:{lh}px;
        width:{width}px; display:inline-block; white-space:pre-wrap }}
</style>
<div id="q">{text}</div>"""


def render_text(text: str, *, width: int, size: int, line_h: int,
                renderer: Path, ink=(26, 26, 26),
                family: str = 'Mukta,"Devanagari Sangam MN",sans-serif') -> Image.Image:
    """Set `text` in Chromium and return it as a transparent-background image."""
    font = (renderer / "vendor/fonts/mukta-devanagari-700-normal.woff2").resolve()
    if not font.is_file():
        raise SystemExit(f"font not found: {font}")
    html = PAGE.format(font=font.as_uri(), size=size, lh=line_h, width=width,
                       text=text, r=ink[0], g=ink[1], b=ink[2], family=family)
    with tempfile.TemporaryDirectory() as td:
        page = Path(td) / "q.html"
        page.write_text(html, encoding="utf-8")
        shot = Path(td) / "q.png"
        script = f"""
import {{ chromium }} from '{(renderer.parent / "node_modules/playwright/index.mjs").resolve().as_uri()}';
const b = await chromium.launch();
const p = await b.newPage({{ viewport: {{ width: {width + 80}, height: 1200 }},
                            deviceScaleFactor: 2 }});
await p.goto('{page.as_uri()}');
await p.waitForTimeout(350);
const el = await p.$('#q');
await el.screenshot({{ path: '{shot}', omitBackground: true }});
await b.close();
"""
        mjs = Path(td) / "shot.mjs"
        mjs.write_text(script, encoding="utf-8")
        r = subprocess.run(["node", str(mjs)], capture_output=True, text=True,
                           cwd=str(renderer.parent))
        if r.returncode != 0 or not shot.is_file():
            raise SystemExit(f"chromium text render failed:\n{r.stderr[:900]}")
        return Image.open(shot).convert("RGBA").copy()


def erase_ink(im: Image.Image, box, *, dark: int = 150, grow: int = 3,
              sigma: float = 7.0) -> Image.Image:
    """Remove the INK inside `box` and leave the paper exactly as photographed.

    `paper_header.inpaint_band` rebuilds the whole rectangle by interpolating
    between a clean row above and a clean row below. On BIO-C2-LA-01's card that
    left a visibly FLATTER, lighter rectangle behind the new question: the
    sheet's diagonal crease runs through the question area, and a rectangle
    interpolated from its top and bottom edges cannot reproduce a fold that
    crosses it at an angle. The block edge was plain at normal contrast.

    So only the letters are replaced. The mask is the dark pixels, grown by a
    few pixels so the anti-aliased fringe goes too; every other pixel in the box
    is never touched. Each masked pixel is filled by NORMALISED CONVOLUTION -
    a Gaussian average over the unmasked pixels around it - so the fill follows
    the crease and shading of the paper right next to it and never reads a
    single inked pixel (which is what left grey ghosts in the median approach
    paper_header's docstring describes).
    """
    import numpy as np
    from scipy import ndimage
    x0, y0, x1, y1 = box
    rgba = np.asarray(im.convert("RGBA")).astype(np.float64)
    region = rgba[y0:y1, x0:x1, :3]
    lum = region.mean(axis=2)
    on_paper = rgba[y0:y1, x0:x1, 3] > 200
    ink = (lum < dark) & on_paper
    ink = ndimage.binary_dilation(ink, iterations=grow)
    keep = (~ink & on_paper).astype(np.float64)
    wsum = ndimage.gaussian_filter(keep, sigma) + 1e-6
    # Paper grain, put back. A normalised-convolution fill is smooth, and on a
    # large question the filled strokes cover enough area to read as a soft
    # patch - measured on this card, grain inside the question area dropped to
    # 0.84 of the untouched margin. The grain is sampled from THIS region's own
    # clean paper (its high-pass residual), so it has the photograph's texture
    # and level, and added only where ink was removed.
    lum_hp = lum - ndimage.gaussian_filter(lum, 1.5)
    pool = lum_hp[keep > 0]
    rng = np.random.default_rng(1)          # fixed: a rebuild is byte-identical
    grain = rng.choice(pool, size=lum.shape) if pool.size else 0.0
    for c in range(3):
        num = ndimage.gaussian_filter(region[..., c] * keep, sigma)
        region[..., c] = np.where(ink, num / wsum + grain, region[..., c])
    rgba[y0:y1, x0:x1, :3] = region
    return Image.fromarray(rgba.clip(0, 255).astype(np.uint8), "RGBA")


def _keep_alpha(before: Image.Image, after: Image.Image) -> Image.Image:
    """Put the sheet's cut-out back.

    The paper is a torn shape on transparency and `inpaint_band` returns RGB,
    so without this the tear flattens to a black rectangle the moment the card
    is composited over the video.
    """
    out = after.convert("RGBA")
    out.putalpha(before.getchannel("A"))
    return out


# The approved subject line per subject, measured off a sheet that already
# carries it (ink box). Biology: inbox/BIO-C12-LA-02_bundle/card/question_sheet.png.
SUBJECT_SOURCE = {"biology": ROOT / "inbox/BIO-C12-LA-02_bundle/card/question_sheet.png"}

SUBJECT_ERASE = (286, 560, 956, 640)   # subject ink on the approved sheet:
                                       # x 292-930, y 576-637

# A FLAT GREY BLOCK BAKED INTO THE PHOTOGRAPH, behind the last letters of the
# subject. Every sheet in this repo carries it (biology and chemistry alike,
# same pixels): an earlier rectangle inpaint, x 862-950 / y 555-642, measured at
# 204-210 against 219-225 paper around it. "CHEMISTRY" and "BIOLOGY" run over
# it and hide most of it; "PHYSICS" is shorter and left it standing beside the
# S as a visible box (PHY-C1-SA-01). BIO-C4-LA-03's log records the same thing
# as "a gray smudge next to BIOLOGY". The PAPER inside it is rebuilt from the
# paper around it; ink is not touched.
PAPER_PATCH = (860, 553, 952, 644)


def clean_paper(im: Image.Image, box, *, ring: int = 26, sigma: float = 12.0,
                ink: int = 150) -> Image.Image:
    """Rebuild the PAPER inside `box` from the clean paper around it.

    The mirror image of erase_ink: there the ink is replaced and the paper kept;
    here the paper is replaced and the ink kept. Known pixels are the paper in a
    `ring` outside the box only - nothing inside it is trusted, because the
    whole inside is the flat patch - filled inward by normalised convolution,
    with the photograph's own grain put back.
    """
    import numpy as np
    from scipy import ndimage
    x0, y0, x1, y1 = box
    X0, Y0, X1, Y1 = x0 - ring, y0 - ring, x1 + ring, y1 + ring
    rgba = np.asarray(im.convert("RGBA")).astype(np.float64)
    region = rgba[Y0:Y1, X0:X1, :3]
    lum = region.mean(axis=2)
    inside = np.zeros(lum.shape, bool)
    inside[ring:ring + (y1 - y0), ring:ring + (x1 - x0)] = True
    on_paper = rgba[Y0:Y1, X0:X1, 3] > 200
    known = (~inside & on_paper & (lum > ink)).astype(np.float64)
    wsum = ndimage.gaussian_filter(known, sigma) + 1e-6
    lum_hp = lum - ndimage.gaussian_filter(lum, 1.5)
    # Grain comes only from paper well clear of any ink, and without its tails:
    # a pixel next to a letter has a huge high-pass value, and sampling those
    # sprinkled the rebuilt block with white specks.
    clear = ndimage.binary_erosion(known > 0, iterations=4)
    pool = lum_hp[clear]
    if pool.size:
        lo, hi = np.percentile(pool, [5, 95])
        pool = pool[(pool >= lo) & (pool <= hi)]
    rng = np.random.default_rng(2)          # fixed: a rebuild is byte-identical
    grain = rng.choice(pool, size=lum.shape) if pool.size else 0.0
    target = inside & on_paper & (lum > ink)
    for c in range(3):
        num = ndimage.gaussian_filter(region[..., c] * known, sigma)
        region[..., c] = np.where(target, num / wsum + grain, region[..., c])
    rgba[Y0:Y1, X0:X1, :3] = region
    return Image.fromarray(rgba.clip(0, 255).astype(np.uint8), "RGBA")


def set_subject(sheet: Image.Image, subject: str) -> Image.Image:
    """Rewrite the subject line exactly the way paper_header.build does.

    build() always rewrites this line: it measures the original line's ink box,
    renders `hindi – english` scaled to that ink height, rotates it to the
    sheet, and lands it on the same horizontal centre and the same bottom row.
    So the chemistry line on the approved CHE-C4-LA-01 sheet and the biology
    line on BIO-C12-LA-02's are the same operation with a different word, and
    running it here on the approved sheet reproduces the biology line - checked
    against BIO-C12-LA-02's own, see the build log.

    The one change: the old line is removed with erase_ink, not inpaint_band,
    because inpaint_band is what baked a flat rectangle into every sheet it
    touched.
    """
    import numpy as np
    from tools import paper_header as ph
    hindi, english = ph.SUBJECTS[subject]
    g = np.asarray(sheet.convert("L")).astype(int)
    x0, y0, x1, y1 = ph.BAND
    ink = g[y0:y1, x0:x1] < 110
    rows = np.nonzero(ink.any(axis=1))[0]; cols = np.nonzero(ink.any(axis=0))[0]
    ox0, oy0 = x0 + int(cols.min()), y0 + int(rows.min())
    ox1, oy1 = x0 + int(cols.max()), y0 + int(rows.max())
    sheet = clean_paper(sheet, PAPER_PATCH)
    sheet = erase_ink(sheet, SUBJECT_ERASE)

    if subject in SUBJECT_SOURCE:
        # LIFT THE APPROVED LINE'S INK, don't re-typeset it.
        #
        # Re-rendering with subject_line came out 15% too big when sized off the
        # chemistry line (the स्त्र conjunct makes that ink box tall), and still
        # 3% wide with a looser dash when fitted to the approved width - the
        # approved line was set through a width clamp this cannot reproduce.
        # Every sheet here is the SAME photograph at the same geometry, so the
        # approved biology line already exists in exactly the right place on
        # BIO-C2-LA-02's sheet. Its ink is transferred as a coverage matte:
        # alpha from how much darker each pixel is than the paper under it, so
        # anti-aliasing survives - and ONLY the ink moves. That sheet's flat
        # inpaint patch lives in its paper, which is left behind.
        src = Image.open(SUBJECT_SOURCE[subject]).convert("RGBA")
        bx0, by0, bx1, by1 = SUBJECT_ERASE
        paper = np.asarray(erase_ink(src, SUBJECT_ERASE).convert("L")).astype(float)[by0:by1, bx0:bx1]
        lum = np.asarray(src.convert("L")).astype(float)[by0:by1, bx0:bx1]
        ink_level = float(ph.INK[0])
        alpha = np.clip((paper - lum) / np.maximum(paper - ink_level, 1.0), 0.0, 1.0)
        alpha[alpha < 0.08] = 0.0                  # paper noise is not ink
        dst = np.asarray(sheet).astype(float)
        region = dst[by0:by1, bx0:bx1, :3]
        a3 = alpha[..., None]
        region[:] = region * (1 - a3) + np.array(ph.INK, float) * a3
        dst[by0:by1, bx0:bx1, :3] = region
        return Image.fromarray(dst.clip(0, 255).astype(np.uint8), "RGBA")

    line = ph.subject_line(hindi, english, oy1 - oy0, ph.BAND[2] - ph.BAND[0] - 20)
    line = line.rotate(-ph.TILT_DEG, expand=True, resample=Image.BICUBIC)
    cx = (ox0 + ox1) // 2
    sheet.alpha_composite(line, (cx - line.width // 2, oy1 - line.height))
    return sheet


def build(base: Path, question: str, out: Path, renderer: Path,
          year: str | None = None, subject: str | None = None) -> dict:
    sheet = Image.open(base).convert("RGBA")
    alpha_src = sheet
    if subject:
        sheet = set_subject(sheet, subject)

    # 1. erase the old question, keeping the paper's shading and grain
    sheet = erase_ink(sheet, Q_BAND)
    if year:
        sheet = erase_ink(sheet, YEAR_BAND)

    # 2. set the new question EXACTLY the way the approved design sets it.
    #
    # The first version of this file set the question in bold Mukta through
    # Chromium and pasted it as ONE rotated block. It read, but it was the wrong
    # face at the wrong weight, and the block was rotated the wrong way round
    # (TILT_DEG, not -TILT_DEG) about its own centre - so every line after the
    # first drifted off the sheet's slant. Reported on 2026-09-14 against the
    # approved card as "the font and alignment of the question are wrong".
    #
    # paper_header.question_block IS the approved typesetting: Noto Sans
    # Devanagari sized to the design's measured ink height, wrapped on measured
    # width, every line on the same baseline rail, each line stepped LEFT as the
    # sheet rises to the right, shrunk to fit and truncated with "..." at the
    # torn edge. It could not be used before only because PIL had no raqm; now
    # that it does, re-implementing it would just be a second way to be wrong.
    from tools import paper_header as ph  # noqa: E402
    if not Path(ph.Q_FONT).is_file():
        raise SystemExit(f"question font missing: {ph.Q_FONT}")
    from PIL import features
    if not features.check("raqm"):
        raise SystemExit("refusing to set Devanagari: Pillow has no libraqm")
    import numpy as np
    rows, pitch, baseline = ph.question_block(question, ph.Q_INK_H,
                                              Q_BAND[2] - ph.Q_LEFT - 10,
                                              avail_h=ph.Q_BOTTOM - ph.Q_TOP)
    # Rotating a row with expand=True drops its LEFT end by width x sin(tilt)
    # inside the rotated image, so rows placed at a fixed pitch by their top
    # edge sat at different heights by WIDTH: on CHE-C3-SA-06 the short last
    # line ("निर्भर नहीं होता।", 287px against 613px above it) rode 16px up
    # into the line before it — pitches of 70, 76 and 56px where the rail is 72.
    # Each row is lifted by its width's share of that drop, measured from the
    # first row, so the first line sits exactly where the approved design put
    # it and every left end lands on the rail below it.
    slope = np.sin(np.radians(abs(TILT_DEG)))
    w0 = rows[0].width if rows else 0
    for i, row in enumerate(rows):
        lift = int(round((row.width - w0) * slope))
        row = row.rotate(-TILT_DEG, expand=True, resample=Image.BICUBIC)
        y = ph.Q_TOP + i * pitch - baseline + int(ph.Q_INK_H * 0.80) - lift
        x = ph.Q_LEFT - int(i * pitch * np.tan(np.radians(-TILT_DEG)))
        sheet.alpha_composite(row, (x, y))
    size = len(rows)

    # 3. the year - pinned to where the ORIGINAL digits sat, measured.
    #
    # The first version set it in Chromium and pasted the rendered box at a
    # guessed corner, so the digits floated off the line they belong to. Here
    # the printed year is matched on the three things that make it read as part
    # of the sheet: the face (the header's own Times New Roman Bold), the height
    # of the digit ink, and the position - its left edge and the bottom of its
    # lowest digit land exactly where "2026" did.
    if year:
        from PIL import ImageDraw, ImageFont
        import numpy as np
        # SIZE IS CALIBRATED ON THE ORIGINAL "2026", NOT ON THE TARGET YEAR.
        # Fitting digit HEIGHT came out 8% large (65px against 60) because the
        # measured height includes the slant. Width of the printed "2026" is the
        # unambiguous measurement, and calibrating on those exact four digits
        # means a narrower or wider year ("2019", "2011") keeps the same type size
        # instead of being stretched to fill the old width.
        f = None
        for size in range(14, 60):
            f = ImageFont.truetype(ph.LAT_FONT, size)
            probe = Image.new("L", (400, 120), 0)
            ImageDraw.Draw(probe).text((10, 90), "2026", font=f, fill=255, anchor="ls")
            xs = np.nonzero((np.asarray(probe) > 128).any(axis=0))[0]
            if xs.max() - xs.min() + 1 >= YEAR_INK_W:
                break
        tile = Image.new("RGBA", (400, 120), (0, 0, 0, 0))
        ImageDraw.Draw(tile).text((10, 90), year, font=f,
                                  fill=ph.INK + (255,), anchor="ls")
        tile = tile.rotate(-TILT_DEG, expand=True, resample=Image.BICUBIC)
        a = np.asarray(tile)[..., 3] > 60
        ys, xs = np.nonzero(a)
        tile = tile.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
        sheet.alpha_composite(tile, (YEAR_INK_LEFT, YEAR_INK_BOTTOM - tile.height + 1))

    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out)
    return {"out": str(out), "lines": size, "question": question,
            "year": year, "base": str(base)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base", required=True, type=Path,
                    help="a sheet with this design; its question is replaced")
    ap.add_argument("--question", required=True)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--year")
    ap.add_argument("--subject", choices=["physics", "chemistry", "biology", "maths",
                                         "geography", "history", "polsci", "economics"],
                    help="rewrite the subject line (needed when the base sheet is another subject's)")
    ap.add_argument("--renderer", type=Path,
                    default=ROOT / "work/bio-c2-la-01/renderer",
                    help="a renderer/ folder — supplies the Devanagari font and "
                         "the node_modules that Chromium is launched from")
    a = ap.parse_args(argv)
    info = build(a.base, a.question, a.out, a.renderer, a.year, a.subject)
    print(json.dumps(info, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
