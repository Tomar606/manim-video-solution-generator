#!/usr/bin/env python3
"""Image harness for the HINDI (Devanagari) handwritten notes style.

Two page types, routed by the page id:

  *-page-NN  THEORY page, rendered with prompt-hindi.md
             IMAGE 1 = paper-hindi.png   (blank sheet: left double margin rule + top rule band)
             IMAGE 2 = hand-anchor.jpg   (native-res CROP of the real page whose HAND we clone)
             IMAGE 3 = style-anchor.png  (the APPROVED page-01 render -- pins letter size, row
                       spacing, density and tone, which drift between runs when only the real
                       reference is supplied)

  *-dia-NN   DIAGRAM page, rendered with prompt-diagram-hindi.md
             IMAGE 1 = paper-hindi.png
             IMAGE 2 = diagram-anchor.jpg  (the same student's hand-drawn figure page -- the
                       drawing style AND the label handwriting both come from here)
             IMAGE 3 = the source figure named by the page's [[DIAGRAM <file>]] block

The built prompt is saved to page-prompts/<id>-prompt.md so it can be inspected/tuned.
Output: generated/clean/<id>.png (raw render) and generated/<id>.jpg (after scan_effect).
Run whiten.py afterwards for the hard blown-out scan look of the original reference.

COST TELEMETRY: every billed call's real token usage is read off the response and appended to
RENDER_LOG.md beside this file, with a USD estimate from the PRICE_* env vars. Retries and
blank/black renders are logged too, because both are charged.

COST GUARD: cost_guard.py (venv .pth) clamps quality to medium and downscales inputs to 1024px.
Its default input cap of 2 would silently DROP the source figure on diagram pages, so the cap is
raised to 3 here; the quality and downscale levers stay fully in force.

Usage:
  python gen_hindi.py mp-ch5-page-01 mp-ch5-dia-01   # explicit ids
  python gen_hindi.py                                # every id in page-contents/
  DRY_RUN=1 python gen_hindi.py                      # build prompts only, no API call
"""
from __future__ import annotations
import base64, io, os, re, sys, zlib
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image

# must be set BEFORE openai (and therefore cost_guard) is imported
os.environ.setdefault("COST_GUARD_MAX_IMAGES", "3")

from scan_effect import scan_effect

HERE = Path(__file__).resolve().parent
GPT_NOTES = HERE.parent
CHAPTER = "Hindi Hand"

for line in (GPT_NOTES / ".env").read_text().splitlines():
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

MODEL = os.environ.get("OPENAI_IMAGE_MODEL", "gpt-image-1")
QUALITY, SIZE = "high", "1024x1536"   # cost_guard clamps quality down to medium
WEAR = 0.4                             # light, even scan -- this reference is a clean scan
CLEAN_ONLY = bool(os.environ.get("CLEAN_ONLY"))
DRY_RUN = bool(os.environ.get("DRY_RUN"))

PROMPT_TMPL = HERE / "prompt-hindi.md"
DIAGRAM_TMPL = HERE / "prompt-diagram-hindi.md"
BASE_PAGE = HERE / "paper-hindi.png"
HAND_REF = HERE / "hand-anchor.jpg"
STYLE_REF = HERE / "style-anchor.png"
DIAGRAM_REF = HERE / "diagram-anchor.jpg"
CONTENT_DIR = HERE / "page-contents"
PROMPT_DIR = HERE / "page-prompts"
FIG_DIR = HERE / "figures"
OUT_DIR = HERE / "generated"
CLEAN_DIR = OUT_DIR / "clean"

FIG_RE = re.compile(r"\[\[DIAGRAM\s+([^\]\s]+)\s*\]\]")

# Per-1M-token prices used only for the estimate in the log. Defaults are gpt-image-1's published
# rates; override per model so the log tells the truth. Ported from mockup/gen_from_mockup.py so
# this path stops being the one billed path with no numbers on it.
PRICE_TEXT_IN = float(os.environ.get("PRICE_TEXT_IN", "5"))
PRICE_IMAGE_IN = float(os.environ.get("PRICE_IMAGE_IN", "10"))
PRICE_IMAGE_OUT = float(os.environ.get("PRICE_IMAGE_OUT", "40"))

RENDER_LOG = HERE / "RENDER_LOG.md"
TABLE_HEAD = ("| UTC | page | attempt | result | model | quality | size | prompt | refs "
              "| txt-in | img-in | out | est $ |\n"
              "|---|---|---|---|---|---|---|---|---|---|---|---|---|\n")
LOG_HEAD = ("# Render log — Hindi Hand PYQ pages\n\n"
            "One row per **billed** image call (retries included, because a retry is a second\n"
            "charge). The `page` id carries its own board+chapter, so all chapters share one log.\n"
            "Token columns are what the API reported; `est $` prices them with PRICE_TEXT_IN /\n"
            "PRICE_IMAGE_IN / PRICE_IMAGE_OUT (per 1M tokens), so it is only as right as those.\n\n"
            + TABLE_HEAD)


def is_diagram(page_id: str) -> bool:
    return "dia-" in page_id


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
    text_in, image_in = u.get("text_in"), u.get("image_in")
    if text_in is None or image_in is None:      # only a total: price it all as text
        text_in, image_in = (u.get("total_in") or 0), 0
    return (text_in * PRICE_TEXT_IN + image_in * PRICE_IMAGE_IN
            + u["out"] * PRICE_IMAGE_OUT) / 1_000_000


def log_call(page_id: str, attempt: int, result: str, chars: int, nrefs: int, u: dict | None = None):
    """Append one row to RENDER_LOG.md. Append-only, so a resumed run keeps the history."""
    if not RENDER_LOG.exists():
        RENDER_LOG.write_text(LOG_HEAD, encoding="utf-8")
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
    # log what the call was BILLED at, not what this file asked for: cost_guard rewrites the
    # quality on the way out, so logging QUALITY here would record a price we never paid
    eff = (os.environ.get("OPENAI_IMAGE_QUALITY") or "medium").strip().lower()
    u = u or {}
    usd = estimate_usd(u)
    cell = lambda v: "—" if v is None else str(v)   # noqa: E731
    with RENDER_LOG.open("a", encoding="utf-8") as fh:
        fh.write(f"| {stamp} | {page_id} | {attempt} | {result} | {MODEL} | {eff} | {SIZE} "
                 f"| {chars} ch | {nrefs} | {cell(u.get('text_in'))} | {cell(u.get('image_in'))} "
                 f"| {cell(u.get('out'))} | {'—' if usd is None else f'{usd:.3f}'} |\n")


def png_bytes(path: Path):
    with Image.open(path) as im:
        im = im.convert("RGB")
        buf = io.BytesIO()
        im.save(buf, format="PNG")
    return (path.stem.replace(" ", "_") + ".png", buf.getvalue(), "image/png")


def build_prompt(page_id: str):
    diagram = is_diagram(page_id)
    template = (DIAGRAM_TMPL if diagram else PROMPT_TMPL).read_text(encoding="utf-8")
    content = (CONTENT_DIR / f"{page_id}.md").read_text(encoding="utf-8").strip()
    prompt = template.replace("{CONTENT}", content)
    PROMPT_DIR.mkdir(exist_ok=True)
    (PROMPT_DIR / f"{page_id}-prompt.md").write_text(prompt, encoding="utf-8")
    figs = FIG_RE.findall(content) if diagram else []
    return prompt, figs


def render(client, refs, page_id: str, attempt: int = 1) -> dict:
    prompt, figs = build_prompt(page_id)
    diagram = is_diagram(page_id)
    kind = "DIAGRAM" if diagram else "THEORY"
    imgs = ([refs["base"], refs["dia"]] if diagram
            else [refs["base"], refs["hand"], refs["style"]])
    for f in figs:
        fp = FIG_DIR / f
        if not fp.exists():
            print(f"[{page_id}] WARN: missing figure {f}", file=sys.stderr)
            continue
        imgs.append(png_bytes(fp))
    print(f"[{page_id}] prompt built ({len(prompt)} chars, {kind}, "
          f"{len(imgs)} imgs, figs: {', '.join(figs) or 'none'})", flush=True)
    if DRY_RUN:
        return {}
    print(f"[{page_id}] rendering {MODEL} ...", flush=True)
    kwargs = dict(model=MODEL, prompt=prompt, size=SIZE, quality=QUALITY, image=imgs)
    if MODEL.startswith("gpt-image-1"):
        kwargs["input_fidelity"] = "high"
    result = client.images.edit(**kwargs)
    clean = Image.open(io.BytesIO(base64.b64decode(result.data[0].b64_json)))
    # A failed generation can come back as a solid black (or blank) sheet. Saving it as a success
    # ships a ruined page and hides a wasted call, so check before writing and let the retry loop
    # have another go. The call is billed either way, so it is logged either way.
    import numpy as _np
    _mean = _np.asarray(clean.convert("L"), dtype=float).mean()
    if _mean < 40 or _mean > 252:
        log_call(page_id, attempt, f"BLANK — mean {_mean:.0f}", len(prompt), len(imgs),
                 usage_of(result))
        raise RuntimeError(f"blank/black render (mean brightness {_mean:.0f})")
    CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    clean.convert("RGB").save(CLEAN_DIR / f"{page_id}.png", format="PNG")
    u = usage_of(result)
    usd = estimate_usd(u)
    cost = "" if usd is None else (f" | {u.get('text_in')}txt + {u.get('image_in')}img in, "
                                   f"{u.get('out')} out ≈ ${usd:.3f}")
    log_call(page_id, attempt, "saved", len(prompt), len(imgs), u)
    if CLEAN_ONLY:
        print(f"[{page_id}] saved -> clean/{page_id}.png (scan skipped){cost}", flush=True)
        return u
    seed = zlib.crc32(f"{CHAPTER}|{page_id}".encode())
    scan_effect(clean, seed=seed, wear_boost=WEAR).save(
        OUT_DIR / f"{page_id}.jpg", format="JPEG", quality=95)
    print(f"[{page_id}] saved -> generated/{page_id}.jpg (+ clean/{page_id}.png){cost}", flush=True)
    return u


def main() -> int:
    pages = sys.argv[1:] or sorted(p.stem for p in CONTENT_DIR.glob("*.md"))
    OUT_DIR.mkdir(exist_ok=True)
    client, refs = None, {"base": None, "hand": None, "style": None, "dia": None}
    if not DRY_RUN:
        if not os.environ.get("OPENAI_API_KEY"):
            print("ERROR: OPENAI_API_KEY not set", file=sys.stderr)
            return 1
        from openai import OpenAI
        client = OpenAI()
        refs = {"base": png_bytes(BASE_PAGE), "hand": png_bytes(HAND_REF),
                "style": png_bytes(STYLE_REF), "dia": png_bytes(DIAGRAM_REF)}

    failed, spent, priced = [], 0.0, 0
    for page_id in pages:
        for attempt in range(1, 4):
            try:
                u = render(client, refs, page_id, attempt)
                usd = estimate_usd(u)
                if usd is not None:
                    spent += usd
                    priced += 1
                break
            except Exception as e:  # noqa: BLE001
                print(f"[{page_id}] attempt {attempt}/3 FAILED: {type(e).__name__}: {e}", flush=True)
                if not DRY_RUN:
                    log_call(page_id, attempt, f"FAILED — {type(e).__name__}: {str(e)[:90]}", 0, 0)
                import time
                time.sleep(5 * attempt)
        else:
            failed.append(page_id)
    if priced:
        print(f"[COST] {priced} priced calls ≈ ${spent:.2f} (${spent / priced:.3f}/page at "
              f"PRICE_TEXT_IN={PRICE_TEXT_IN}, PRICE_IMAGE_IN={PRICE_IMAGE_IN}, "
              f"PRICE_IMAGE_OUT={PRICE_IMAGE_OUT} per 1M)", flush=True)
    elif not DRY_RUN:
        print("[COST] the model reported no usage on these calls — read the real figure off the "
              "OpenAI usage dashboard and correct the PRICE_* env vars.", flush=True)
    if failed:
        print(f"[SUMMARY] FAILED: {' '.join(failed)}", flush=True)
        return 1
    print("[SUMMARY] done", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
