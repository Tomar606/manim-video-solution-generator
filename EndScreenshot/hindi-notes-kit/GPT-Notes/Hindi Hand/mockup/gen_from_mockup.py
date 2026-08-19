#!/usr/bin/env python3
"""Stage 2 — hand-write each page from its mock-up. ONE billed image per page.

    gen_from_mockup.py Hindi-Ch7                 every page not already drawn
    gen_from_mockup.py Hindi-Ch7 page-01 page-02 named pages (always redrawn)
    DRY_RUN=1 gen_from_mockup.py Hindi-Ch7       build prompts only, no API call

Images, in the order the model reads them:
    1  paper-hindi.png            the real sheet that gets written on
    2  anchor-combined.png        the hand: magnified strokes over a true-scale finished page
    3  mockups/page-NN.png        WHAT GOES WHERE -- the blueprint for this exact page

THREE images, not four. The stroke close-up and the already-drawn style page used to be shipped
separately; make_anchor.py merges them onto one sheet, which drops a whole page-sized input image
off EVERY billed call. LEGACY_REFS=1 restores the old four-image call with the old template.

RESUMABLE: a page whose output already exists is skipped, because every redraw is billed.
Pass page ids explicitly to force a redraw.

COST GUARD: three input images, so COST_GUARD_MAX_IMAGES=3 (the default cap of 2 would silently
drop the mock-up, which is the whole method).

COST TELEMETRY: every call's real token usage is read off the response and written to
RENDER_LOG.md, with a USD estimate from the PRICE_* env vars. Tokens are logged raw so the
estimate can be recomputed later against whatever the model actually charges.
"""
from __future__ import annotations

import base64
import io
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

LEGACY_REFS = bool(os.environ.get("LEGACY_REFS"))
os.environ.setdefault("COST_GUARD_MAX_IMAGES", "4" if LEGACY_REFS else "3")

HERE = Path(__file__).resolve().parent
HAND = HERE.parent                      # .../Hindi Hand
GPT_NOTES = HAND.parent
NOTES = HAND / "notes"

sys.path.insert(0, str(HAND))
from scan_effect import scan_effect     # noqa: E402
from whiten import whiten               # noqa: E402

for line in (GPT_NOTES / ".env").read_text().splitlines():
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

MODEL = os.environ.get("OPENAI_IMAGE_MODEL", "gpt-image-1")
QUALITY, SIZE = "high", "1024x1536"
DRY_RUN = bool(os.environ.get("DRY_RUN"))
PROMPT_CAP = 32000                      # the image API's hard limit; fail loudly, never 400

# Attempts per page. ONE by default: no retries at all. Every attempt is a separate charge, and a
# page that fails is nearly always one whose blueprint needs changing — an anatomy figure tripping
# the output moderation filter, say — so an automatic retry usually just buys the same rejection
# again at full price. Failures are collected and printed at the end of the run to be looked at
# and re-driven deliberately. Raise with MAX_ATTEMPTS=2 if you really want one retry.
MAX_ATTEMPTS = int(os.environ.get("MAX_ATTEMPTS", "1"))

# How faithfully the model is asked to read the input images. This is a COST MULTIPLIER on the
# image-input side, and leaving it unset means paying whatever the model defaults to. Set it
# deliberately: IMAGE_INPUT_FIDELITY=low | high, or "" to send nothing at all.
INPUT_FIDELITY = os.environ.get("IMAGE_INPUT_FIDELITY",
                                "high" if MODEL.startswith("gpt-image-1") else "")

# Per-1M-token prices used only for the estimate in the log. Defaults are gpt-image-1's published
# rates; override per model so the log tells the truth.
PRICE_TEXT_IN = float(os.environ.get("PRICE_TEXT_IN", "5"))
PRICE_IMAGE_IN = float(os.environ.get("PRICE_IMAGE_IN", "10"))
PRICE_IMAGE_OUT = float(os.environ.get("PRICE_IMAGE_OUT", "40"))

TEMPLATE = HERE / ("prompt-mockup.md" if LEGACY_REFS else "prompt-mockup-lean.md")
PAPER = HAND / "paper-hindi.png"
HAND_REF = HAND / "hand-anchor.jpg"
STYLE_REF = HAND / "style-anchor.png"
ANCHOR = HAND / "anchor-combined.png"    # HAND_REF + STYLE_REF on one sheet (make_anchor.py)


def png_bytes(path: Path):
    with Image.open(path) as im:
        buf = io.BytesIO()
        im.convert("RGB").save(buf, format="PNG")
    return (path.stem.replace(" ", "_") + ".png", buf.getvalue(), "image/png")


def gap_note(n: int) -> str:
    """A COUNTED requirement — prose alone does not stop the model closing the gaps up (§4.3)."""
    if n == 0:
        return ("This page's layout has NO blank rows: every row from the first to the last "
                "carries writing, exactly as IMAGE 3 shows.")
    return (f"IMAGE 3 leaves blank rows in the layout, and they are part of it: this page has "
            f"exactly {n} completely EMPTY rows, at exactly the points IMAGE 3 shows them. "
            f"EVERY heading has one under it — write the heading, leave the whole next row "
            f"empty, then start the body on the row after that. Count them before you finish: "
            f"{n} empty rows, no more and no fewer. Never leave two empty rows together.")


sys.path.insert(0, str(HERE))
from scripts_map import SCRIPT_CHARS     # noqa: E402  the exact set the importer can produce


def script_note(content: str) -> str:
    """Name this page's raised/lowered terms explicitly, when it has any.

    The blueprint shows them, but at 36px a subscript 2 is a handful of pixels and the model has
    been seen to normalise it to a full-size digit. Listing them costs a line and makes the
    requirement checkable by eye on the finished page."""
    terms = sorted({t for t in re.findall(r"\S*[" + SCRIPT_CHARS + r"]\S*", content)
                    if any(c in SCRIPT_CHARS for c in t)})
    if not terms:
        return ""
    return ("\n\nRAISED AND LOWERED CHARACTERS. This page carries these exact terms: "
            + ", ".join(terms[:14])
            + ". Write each one the way IMAGE 3 shows it — the small character sits ABOVE the "
              "line (a superscript) or BELOW it (a subscript), never level with the rest of the "
              "word and never as a separate full-size character with a space around it. "
              "IᴬIᴮ is not 'I A I B'; CO₂ is not 'CO 2'.")


def build_prompt(plan: dict) -> str:
    p = (TEMPLATE.read_text(encoding="utf-8")
         .replace("{GAPNOTE}", gap_note(plan["gaps"]))
         .replace("{CONTENT}", plan["content"] + script_note(plan["content"])))
    if len(p) > PROMPT_CAP:
        raise SystemExit(f"prompt for {plan['page']} is {len(p)} chars, over the {PROMPT_CAP} cap")
    # the content is copied verbatim, so a mismatch here means the template or a replace ate it
    for c in set(plan["content"]) & set(SCRIPT_CHARS):
        if p.count(c) < plan["content"].count(c):
            raise SystemExit(f"prompt for {plan['page']} lost the {c!r} super/subscript")
    return p


TABLE_HEAD = ("| UTC | page | attempt | result | model | quality | fidelity | size | prompt | refs "
              "| txt-in | img-in | out | est $ |\n"
              "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|\n")

LOG_HEAD = ("# Render log — {key}\n\n"
            "One row per **billed** image call (retries included, because a retry is a second\n"
            "charge). Token columns are what the API reported for that call; `est $` prices them\n"
            "with PRICE_TEXT_IN / PRICE_IMAGE_IN / PRICE_IMAGE_OUT (per 1M tokens), so it is only\n"
            "as right as those env vars. QA findings live in `DEFECTS.md` beside this file.\n\n"
            + TABLE_HEAD)


def usage_of(resp) -> dict:
    """Pull token counts off the response, tolerating a model that reports none."""
    u = getattr(resp, "usage", None)
    if u is None:
        return {}
    d = getattr(u, "input_tokens_details", None)
    return {"text_in": getattr(d, "text_tokens", None) if d else None,
            "image_in": getattr(d, "image_tokens", None) if d else None,
            "total_in": getattr(u, "input_tokens", None),
            "out": getattr(u, "output_tokens", None)}


def estimate_usd(u: dict) -> float | None:
    if not u or u.get("out") is None:
        return None
    text_in = u.get("text_in")
    image_in = u.get("image_in")
    if text_in is None or image_in is None:      # only a total: price it all as text, and say so
        text_in, image_in = (u.get("total_in") or 0), 0
    return (text_in * PRICE_TEXT_IN + image_in * PRICE_IMAGE_IN
            + (u["out"]) * PRICE_IMAGE_OUT) / 1_000_000


def log_call(root: Path, key: str, pid: str, attempt: int, result: str, chars: int, nrefs: int,
             u: dict | None = None):
    """Append one line to the chapter's render log. Append-only so resumes keep the history."""
    f = root / "RENDER_LOG.md"
    if not f.exists():
        f.write_text(LOG_HEAD.format(key=key), encoding="utf-8")
    elif TABLE_HEAD.splitlines()[0] not in f.read_text(encoding="utf-8"):
        # an older log with fewer columns: start a second table rather than append cells that
        # would not line up under its header, so the whole history stays readable
        with f.open("a", encoding="utf-8") as fh:
            fh.write("\n### with token telemetry\n\n" + TABLE_HEAD)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
    # log what the call was BILLED at, not what this file asked for: cost_guard rewrites the
    # quality on the way out, so logging QUALITY here would record a price we never paid
    eff = (os.environ.get("OPENAI_IMAGE_QUALITY") or "medium").strip().lower()
    u = u or {}
    usd = estimate_usd(u)
    cell = lambda v: "—" if v is None else str(v)   # noqa: E731
    with f.open("a", encoding="utf-8") as fh:
        fh.write(f"| {stamp} | {pid} | {attempt} | {result} | {MODEL} | {eff} "
                 f"| {INPUT_FIDELITY or '—'} | {SIZE} | {chars} ch | {nrefs} "
                 f"| {cell(u.get('text_in'))} | {cell(u.get('image_in'))} | {cell(u.get('out'))} "
                 f"| {'—' if usd is None else f'{usd:.3f}'} |\n")


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    key = sys.argv[1]
    only = set(sys.argv[2:])
    root = NOTES / key
    plans = {p["page"]: p for p in json.loads((root / "plans.json").read_text(encoding="utf-8"))}
    out_dir, clean_dir, prompt_dir = root / "pages", root / "pages" / "clean", root / "page-prompts"
    for d in (out_dir, clean_dir, prompt_dir):
        d.mkdir(parents=True, exist_ok=True)

    # HARD GATE: never spend on a chapter whose blueprints have not been proven sound.
    # Set PREFLIGHT_SKIP=1 only to deliberately override, and only knowingly.
    if not DRY_RUN and not os.environ.get("PREFLIGHT_SKIP"):
        import subprocess
        pre = subprocess.run([sys.executable, str(HERE / "preflight.py"), key],
                             capture_output=True, text=True)
        print(pre.stdout.rstrip())
        if pre.returncode != 0:
            print(f"\nREFUSING TO RENDER {key}: preflight failed (see above). "
                  f"Fix the blueprints, or set PREFLIGHT_SKIP=1 to override.", file=sys.stderr)
            return 1

    todo = [p for p in sorted(plans) if (p in only if only else not (clean_dir / f"{p}.png").exists())]
    print(f"{key}: {len(plans)} pages, {len(todo)} to draw"
          + (f" (skipping {len(plans) - len(todo)} already drawn)" if not only else ""))
    if not todo:
        return 0

    client = refs = None
    if not DRY_RUN:
        if not os.environ.get("OPENAI_API_KEY"):
            print("ERROR: OPENAI_API_KEY not set", file=sys.stderr)
            return 1
        from openai import OpenAI
        client = OpenAI()
        if LEGACY_REFS:
            refs = [png_bytes(PAPER), png_bytes(HAND_REF), None, png_bytes(STYLE_REF)]
        else:
            if not ANCHOR.exists():
                print(f"ERROR: {ANCHOR.name} is missing — run `python make_anchor.py` in "
                      f"{HAND.name}/ first (it costs nothing).", file=sys.stderr)
                return 1
            refs = [png_bytes(PAPER), png_bytes(ANCHOR), None]
        print(f"refs: {len(refs)} images | template: {TEMPLATE.name} | "
              f"input_fidelity: {INPUT_FIDELITY or 'not sent'}")

    failed = []
    spent = 0.0
    priced = 0
    for pid in todo:
        prompt = build_prompt(plans[pid])
        (prompt_dir / f"{pid}-prompt.md").write_text(prompt, encoding="utf-8")
        print(f"[{pid}] prompt {len(prompt)} chars, {plans[pid]['gaps']} gaps", flush=True)
        if DRY_RUN:
            continue
        refs[2] = png_bytes(root / "mockups" / f"{pid}.png")
        for attempt in range(1, MAX_ATTEMPTS + 1):
            try:
                kwargs = dict(model=MODEL, prompt=prompt, size=SIZE, quality=QUALITY, image=refs)
                if INPUT_FIDELITY:
                    kwargs["input_fidelity"] = INPUT_FIDELITY
                try:
                    r = client.images.edit(**kwargs)
                except TypeError:
                    r = client.images.edit(**{k: v for k, v in kwargs.items()
                                              if k != "input_fidelity"})
                except Exception as e:  # noqa: BLE001
                    # a model that does not take this parameter must not cost a whole run
                    if "input_fidelity" not in str(e):
                        raise
                    print(f"[{pid}] model rejected input_fidelity — retrying without it",
                          flush=True)
                    r = client.images.edit(**{k: v for k, v in kwargs.items()
                                              if k != "input_fidelity"})
                img = Image.open(io.BytesIO(base64.b64decode(r.data[0].b64_json)))
                # A failed generation can come back as a solid black (or blank) sheet. Saving it
                # as a success ships a ruined page and hides a wasted call, so check before
                # writing and let the retry loop have another go.
                import numpy as _np
                _g = _np.asarray(img.convert("L"), dtype=float)
                if _g.mean() < 40 or _g.mean() > 252:
                    raise RuntimeError(f"blank/black render (mean brightness {_g.mean():.0f})")
                img.convert("RGB").save(clean_dir / f"{pid}.png")
                whiten(img).save(out_dir / f"{pid}.jpg", format="JPEG", quality=95)
                u = usage_of(r)
                usd = estimate_usd(u)
                if usd is not None:
                    spent += usd
                    priced += 1
                cost = "" if usd is None else (
                    f" | {u.get('text_in')}txt + {u.get('image_in')}img in, "
                    f"{u.get('out')} out ≈ ${usd:.3f}")
                print(f"[{pid}] saved -> pages/{pid}.jpg{cost}", flush=True)
                log_call(root, key, pid, attempt, "saved", len(prompt), len(refs), u)
                break
            except Exception as e:  # noqa: BLE001
                print(f"[{pid}] attempt {attempt}/{MAX_ATTEMPTS} FAILED: "
                      f"{type(e).__name__}: {e}", flush=True)
                log_call(root, key, pid, attempt,
                         f"FAILED — {type(e).__name__}: {str(e)[:90]}", len(prompt), len(refs))
                import time
                time.sleep(5 * attempt)
        else:
            failed.append(pid)
    if priced:
        print(f"[COST] {priced} priced calls ≈ ${spent:.2f} "
              f"(${spent / priced:.3f}/page at PRICE_TEXT_IN={PRICE_TEXT_IN}, "
              f"PRICE_IMAGE_IN={PRICE_IMAGE_IN}, PRICE_IMAGE_OUT={PRICE_IMAGE_OUT} per 1M)")
    elif not DRY_RUN:
        print("[COST] the model reported no usage on these calls — read the real figure off the "
              "OpenAI usage dashboard and correct the PRICE_* env vars.")
    if failed:
        print(f"[SUMMARY] FAILED: {' '.join(failed)}")
        return 1
    print("[SUMMARY] done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
