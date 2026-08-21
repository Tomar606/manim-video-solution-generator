#!/usr/bin/env python3
"""preflight.py — prove a chapter's blueprints are sound BEFORE any billed render.

    preflight.py Hindi-Ch2          check one chapter
    preflight.py --all              check every chapter that has mock-ups

Exit code 0 = safe to render. Non-zero = do not spend.

WHY THIS EXISTS
---------------
Every defect that cost us a re-render was visible in the mock-up beforehand, and nobody looked:

  * flowchart captions were never typeset          -> content on no page at all
  * <<BOX>> rectangles were never drawn            -> the model guessed, 5 pages had no box
  * figures carried colour fills and stipple       -> the model copied them as shading
  * table cells were clipped by `nowrap`           -> text the model could not see
  * a heading sat right under the top rule         -> the model wrote it INTO the header band
  * rows collided after jitter                     -> overlapping lines on the drawn page

So the rule is now: the blueprint is checked mechanically, and Stage 2 refuses to run until it
passes. Prompt wording is a last resort; anything checkable is checked here for free.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
NOTES = HERE.parent / "notes"
REPO = HERE.parent.parent.parent            # blocks.json stores `source` relative to this

PITCH = 43.0
ROW0_BASE = 193.0
TEXT_X, RIGHT_X = 85, 990
HEADER_BAND = (0, 118)         # above the printed top rule: must be empty except on page 1
BOTTOM_LIMIT = 1500
MIN_FIG_INK = 0.015           # below this the guide has lost its line work (see check 6)
MAX_FIG_INK = 0.16             # a line-art figure is sparse; more than this means fills survived


class Report:
    def __init__(self, key):
        self.key, self.fail, self.warn = key, [], []

    def bad(self, page, msg):
        self.fail.append(f"{page}: {msg}")

    def note(self, page, msg):
        self.warn.append(f"{page}: {msg}")

    def show(self) -> bool:
        print(f"\n=== {self.key}")
        for w in self.warn:
            print(f"  ! {w}")
        for f in self.fail:
            print(f"  ✗ {f}")
        if not self.fail:
            print(f"  ✓ blueprints pass ({len(self.warn)} warning(s)) — safe to render")
        return not self.fail


def check(key: str) -> bool:
    root = NOTES / key
    rep = Report(key)
    blocks = json.loads((root / "blocks.json").read_text(encoding="utf-8"))["blocks"]
    plans = json.loads((root / "plans.json").read_text(encoding="utf-8"))
    rows = json.loads((root / "rows.json").read_text(encoding="utf-8"))
    mocks = {p.stem for p in (root / "mockups").glob("*.png")}
    ids = {p["page"] for p in plans}

    # 1. one mock-up per plan, no orphans either way
    if ids != mocks:
        rep.bad("chapter", f"plans vs mock-ups mismatch: {sorted(ids ^ mocks)}")

    # 2. NOTHING imported may be lost at the typeset stage (this is how flow captions vanished)
    laid = set()
    for pg in rows:
        for r in pg:
            if r.get("bid") is not None:
                laid.add(r["bid"])
    lost = [f"block {i} ({b['kind']})" for i, b in enumerate(blocks)
            if b["kind"] != "dropped" and i not in laid]
    if lost:
        rep.bad("chapter", f"{len(lost)} imported block(s) never reach a page: {lost[:6]}")

    # 3. every <<BOX>> must have its rectangle drawn in the blueprint
    for pi, pg in enumerate(rows, 1):
        boxes = {r["bid"] for r in pg if r.get("tag") == "BOX" and r["t"] == "line"}
        rects = {r["bid"] for r in pg if r["t"] == "boxrect"}
        if boxes - rects:
            rep.bad(f"page-{pi:02d}", "a <<BOX>> has no rectangle drawn — the model will guess")

    # 3b. no orphan box rectangle (its text paginated away), and no heading left stranded
    for pi, pg in enumerate(rows, 1):
        pid = f"page-{pi:02d}"
        for r in pg:
            if r["t"] == "boxrect" and not any(
                    q["t"] == "line" and q.get("tag") == "BOX" and q["bid"] == r["bid"] for q in pg):
                rep.bad(pid, "an empty box rectangle is drawn (its text is on another page)")
        tail = [r for r in pg if r["t"] != "gap"]
        if tail and tail[-1].get("head") and pi < len(rows):
            rep.bad(pid, "page ends on a heading with nothing under it")

    # 3c. a box rule must enclose its own last line, not cut through it
    for pi, pg in enumerate(rows, 1):
        pid = f"page-{pi:02d}"
        y = 0.0
        tops = {}
        for r in pg:
            if r["t"] == "boxrect":
                tops[r["bid"]] = y
            h = (0 if r["t"] == "boxrect" else
                 r.get("rows", 1) if r["t"] in ("fig", "trow") else
                 2 if r["t"] in ("step", "node") else 1)
            if r["t"] == "line" and r.get("tag") == "BOX" and r["bid"] in tops:
                rect = next((q for q in pg if q["t"] == "boxrect" and q["bid"] == r["bid"]), None)
                if rect and y > tops[r["bid"]] + rect["rows"] - 1 + 1e-6:
                    rep.bad(pid, "a <<BOX>> rule stops short — its last line falls outside/through it")
                    tops.pop(r["bid"])
            y += h

    # 4. pixel checks on the rendered blueprint
    for pi, pg in enumerate(rows, 1):
        pid = f"page-{pi:02d}"
        f = root / "mockups" / f"{pid}.png"
        if not f.exists():
            continue
        a = np.asarray(Image.open(f).convert("L"))
        ink = a < 160
        # 4a. the header band must be clear unless this page carries the chapter title
        has_title = any(r.get("tag") == "TITLE" for r in pg)
        band = ink[HEADER_BAND[0]:HEADER_BAND[1], TEXT_X:].sum()
        if band > 400 and not has_title:
            rep.bad(pid, f"blueprint puts ink in the header band ({band} px) — it will be copied there")
        # 4b. nothing may run past the right edge or off the foot
        if ink[:, RIGHT_X + 8:].sum() > 300:
            rep.bad(pid, "content extends past the right margin")
        if ink[BOTTOM_LIMIT:, :].sum() > 300:
            rep.bad(pid, "content runs off the bottom of the sheet")

    # 5. rows must not collide after jitter
    for pi, pg in enumerate(rows, 1):
        y = 0.0
        last_bottom = -1e9
        for r in pg:
            h = (0 if r["t"] == "boxrect" else
                 r.get("rows", 1) if r["t"] in ("fig", "trow") else
                 2 if r["t"] in ("step", "node") else 1)
            if r["t"] == "line":
                top = ROW0_BASE + PITCH * y - r.get("size", 36)
                if top < last_bottom - 6:
                    rep.note(f"page-{pi:02d}", "two rows sit very close after jitter")
                last_bottom = ROW0_BASE + PITCH * y + 4
            y += h

    # 6. figures: present, and converted to sparse line art
    figs = sorted({m for p in plans for m in re.findall(r"\[\[DIAGRAM ([^\]]+)\]\]", p["content"])})
    fig_dir = Path(json.loads((root / "blocks.json").read_text(encoding="utf-8"))["figures_dir"])
    # Existing on disk is not enough — what matters is what SURVIVES the line-art conversion.
    # Ch4 page-13's chart was on disk, was placed on the page, and still reached the model as a
    # few floating labels because the grey arrows fell below the ink threshold; the model drew no
    # figure at all and the page shipped with a blank lower quarter. So the guide is measured.
    sys.path.insert(0, str(HERE))
    from typeset_mockup import line_art          # noqa: E402
    import base64 as _b64, io as _io
    for fname in figs:
        fp = fig_dir / Path(fname).name
        if not fp.exists():
            rep.bad("chapter", f"figure missing on disk: {fname}")
            continue
        art = Image.open(_io.BytesIO(_b64.b64decode(line_art(fp))))
        cov = (np.asarray(art.convert("L")) < 200).mean()
        # Calibrated on Ch4's six figures: a healthy line-art guide lands at 2.1-3.3% ink. The one
        # that failed (mig02, whose grey arrows fell below the old cut) measured 1.23%. This is a
        # coarse guard -- it catches a figure that arrives mostly empty, NOT one that lost a single
        # connector -- so it is a floor to trip on gross loss, not a proof of fidelity. Eyeball a
        # new chapter's figure pages once before rendering.
        if cov < MIN_FIG_INK:
            rep.bad("chapter", f"figure {fname} converts to a nearly empty guide ({cov*100:.2f}% "
                               f"ink, healthy is >{MIN_FIG_INK*100:.1f}%) — its line work is being "
                               f"cut away and the model will draw little or nothing; raise FIG_THRESH")
        elif cov > MAX_FIG_INK:
            rep.bad("chapter", f"figure {fname} keeps solid tone ({cov*100:.1f}% ink) — it will be"
                               f" copied as shading; lower FIG_THRESH")

    # 7. every super/subscript in the source reaches the page as a super/subscript
    check_scripts(root, plans, rep)
    return rep.show()


def check_scripts(root: Path, plans, rep) -> None:
    """Fail the chapter if a <sup>/<sub> from the source is not on a page in raised form.

    Ch4 shipped its ABO page with "I A" for I^A and Ch7 wrote "H 2 L 2" for H2L2, because
    get_text(" ") had split the run off into its own token. The text is right in the source and
    wrong on the page, which no amount of eyeballing a 40-page chapter reliably catches -- so it
    is counted instead. This covers the prompts too: gen_from_mockup.py copies plans.json
    verbatim into the prompt, so a plan that is right cannot produce a prompt that is wrong.
    """
    sys.path.insert(0, str(HERE))
    from scripts_map import script_runs, flat_survivors   # noqa: E402

    # Forms the source never tagged at all. The parity check below cannot see these -- it only
    # compares what was marked up -- which is how "फॉस्फोरस (32P)" reached three drawn Ch5 pages.
    flat = flat_survivors(" ".join(p["content"] for p in plans))
    if flat:
        rep.bad("chapter", f"untagged super/subscript form(s) left flat on the pages: "
                           f"{', '.join(flat)} — re-import (scripts_map.BARE_FORMS folds these)")

    src = REPO / json.loads((root / "blocks.json").read_text(encoding="utf-8"))["source"]
    if not src.exists():
        rep.note("chapter", f"source HTML not found ({src}) — super/subscripts unverified")
        return

    runs = script_runs(src.read_text(encoding="utf-8"))
    if not runs:
        return
    want = Counter(conv for _, _, conv in runs if conv is not None)
    if any(conv is None for _, _, conv in runs):
        rep.bad("chapter", "a <sup>/<sub> in the source has no Unicode form — re-import "
                           "(import_notes.py now refuses these) before rendering")

    laid = " ".join(p["content"] for p in plans)
    for text, n in sorted(want.items()):
        got = laid.count(text)
        if got < n:
            kind = "superscript" if any(0x2070 <= ord(c) <= 0x207F or ord(c) in (0xB2, 0xB3, 0xB9)
                                        or 0x1D2C <= ord(c) <= 0x1D6B for c in text) else "subscript"
            rep.bad("chapter", f"{kind} '{text}' appears {n}× in the source but only {got}× on the "
                               f"pages — {n - got} of them got flattened into a separate full-size "
                               f"token (the 'I A' for Iᴬ defect); re-import the chapter")


def main() -> int:
    args = sys.argv[1:]
    keys = ([p.name for p in sorted(NOTES.iterdir()) if (p / "mockups").exists()]
            if not args or args[0] == "--all" else args)
    # every chapter is checked, THEN the verdict: all() short-circuits, so one stale chapter used
    # to hide the state of every chapter after it in the list
    ok = all([check(k) for k in keys])
    print()
    print("PREFLIGHT PASSED — safe to render" if ok else "PREFLIGHT FAILED — do not spend")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
