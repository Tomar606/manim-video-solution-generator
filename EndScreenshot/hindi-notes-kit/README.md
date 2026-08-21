# Hindi Handwritten Notes — full pipeline kit

Everything needed to reproduce the Hindi (Devanagari) handwritten Biology notes and the
Top-5 PYQ booklets: the prompts, the scripts, the handwriting reference images, the source
HTML, one complete worked chapter, and finished sample output.

Two people-facing outputs come out of this:

* **Notes pages** — a chapter's notes, hand-written on ruled paper, 1024×1536 per page.
* **PYQ pages** — the Top-5 previous-year questions per chapter, black question / blue answer.

Both go through the **same** pipeline. One billed image API call per page, nothing more.

---

## 0. The 60-second version

```
chapter HTML ──► import ──► blocks.json ──► typeset ──► mockups/page-NN.png  (ZERO API calls)
                                                             │
                                                    preflight (mechanical gate)
                                                             │
                                                             ▼
                             3 images + prompt ──► gpt-image-1 ──► pages/page-NN.jpg
                             1 = blank paper                        (1 billed call per page)
                             2 = handwriting anchor
                             3 = the mock-up blueprint
```

The **mock-up** is the whole trick. We typeset the page in Python onto a blank white sheet
first — a blueprint that says *what goes where* — so the model's only remaining job is
handwriting. Before this, describing the layout in prose made the model guess what fits on a
sheet and cost ~25 renders for an 11-page chapter.

---

## 1. Setup (macOS, ~5 minutes)

```bash
bash setup.sh                     # venv + deps + chromium + cost guard + .env
```

Then put a real key in `GPT-Notes/.env`:

```
OPENAI_API_KEY=sk-...
OPENAI_IMAGE_MODEL=gpt-image-1
OPENAI_IMAGE_QUALITY=medium
```

**Run this on macOS.** The typesetter measures text in Chromium using the system font
*Devanagari Sangam MN*, and the page geometry (row pitch, how much fits on a line) is
calibrated against it. On Linux the font resolves to something else and pagination shifts.

**Do not swap Chromium for Pillow.** Pillow here has no libraqm, so it cannot shape
Devanagari — it garbles matras, conjuncts and every line break containing them. Same trap
applies to any Indic-script typesetting.

Verify with the zero-cost dry run printed at the end of `setup.sh`. All four commands were
run inside this kit before it was zipped; stage 1 reproduces the shipped `blocks.json`
byte-for-byte, and preflight passes.

---

## 2. Running a chapter

All commands from `GPT-Notes/Hindi Hand/`. `PY=../../.venv/bin/python`.

### Notes chapter (source: `pulled_rj_biology/Hindi/Ch<N>.html`)

```bash
$PY mockup/import_notes.py Hindi/Ch1        # HTML  -> notes/Hindi-Ch1/blocks.json
$PY mockup/typeset_mockup.py Hindi-Ch1      # blocks -> mockups/*.png + plans.json  (free)
$PY mockup/preflight.py Hindi-Ch1           # the gate. exit 0 = safe to spend
$PY mockup/gen_from_mockup.py Hindi-Ch1     # >>> BILLED: one image call per page <<<
$PY mockup/publish_notes.py Hindi-Ch1       # file it as a finished chapter
```

### PYQ booklet (source: `top5_pyq_html/Class12/Biology_PYQs/Hindi/<Board>/Ch<N>/`)

```bash
$PY mockup/import_pyq.py UP/Ch1             # -> notes/UP-Ch1/blocks.json + figures/
$PY mockup/typeset_mockup.py UP-Ch1
$PY mockup/preflight.py UP-Ch1
$PY mockup/gen_from_mockup.py UP-Ch1        # >>> BILLED <<<
$PY publish_pyq.py UP-Ch1                   # -> chapters/UP/Ch1/
```

Useful flags:

| | |
|---|---|
| `DRY_RUN=1 gen_from_mockup.py …` | build the prompts, call nothing, spend nothing |
| `gen_from_mockup.py Hindi-Ch1 page-04 page-09` | redraw only these pages (named pages are always redrawn) |
| *(resumability)* | a page whose output already exists is skipped — every redraw is billed |
| `MAX_ATTEMPTS=2` | allow one retry. Default is **1: no retries at all** |

### Post-processing (free, no API)

* `whiten.py` — the hard blown-out phone-scan look of the original reference (this is the
  finish the Hindi pages ship with). `gen_from_mockup.py` already applies it.
* `scan_effect.py` / `rescan_clean.py` — the softer warm-paper scan look, re-appliable to
  `pages/clean/*.png` for free whenever the filter is re-tuned.

---

## 3. Cost — read `GPT-Notes/Hindi Hand/COST-PLAYBOOK.md` before rendering a chapter

That file exists because one day billed **93 image calls for 90 pages**. Short version:

* Every call ships **3 input images**, not 4. `make_anchor.py` merges the stroke close-up and
  a true-scale finished page onto one sheet (`anchor-combined.png`), dropping a whole
  page-sized image off every call.
* `mockup/prompt-mockup-lean.md` is the default template (~29% fewer chars than
  `prompt-mockup.md`). Built prompts: ~18.1k chars, against the API's hard 32k cap.
* `cost_guard.py` clamps quality to `medium`, caps input images and downscales them on
  **every** `images.edit` call, whatever a script asks for. `COST_GUARD_MAX_IMAGES=3` and
  `COST_GUARD_MAX_EDGE=1536` are what the working pipeline sets.
* Settings that produced the signed-off output: `OPENAI_IMAGE_QUALITY=medium` +
  `COST_GUARD_MAX_EDGE=1536`. `low` destroys the hand entirely (rows go level, head-lines
  continuous, tables ruler-straight); `high` is not worth the difference.
* Every call's real token usage is appended to `RENDER_LOG.md` with a USD estimate.
* **Probe two pages before rendering a chapter** (playbook §3), then let it run.

---

## 4. The traps (each one cost us real money)

1. **The handwriting anchor must be a native-resolution CROP** (`hand-anchor.jpg`, 958×662),
   not the full page — cost_guard downscales any input to its max edge and that destroys the
   stroke detail the whole style depends on.
2. **Reference images leak CONTENT, not just style.** The style anchor's chapter title got
   copied into the header band of every mid-chapter page; a diagram anchor's helix and
   base-pair legend were drawn onto an unrelated figure page. Every anchor needs its explicit
   "nothing on this image is ever reproduced — take only stroke quality from it" clause. The
   shipped prompts have it; keep it if you edit them.
3. **Figures must be converted to LINE ART before entering the blueprint** (`line_art()` in
   `typeset_mockup.py`). Source figures carry colour fills and stipple, and the model
   faithfully copies them as shading. No amount of "no shading" prose beats what it can see.
4. **Diagram pages: zero shading.** Outlines only, bare white interiors.
5. **Sharper anatomy figures can trip the API's output moderation** (`[sexual]`) — one page
   was rejected 3×. Soften with `GHOST_OPACITY` on that page or leave it.
6. **The import is verified, not trusted.** `import_notes.py` requires every source token to
   appear in the captured text, in order, and aborts otherwise. An earlier allow-list version
   silently dropped 29,873 of 59,999 characters and 25 pages were rendered before anyone
   noticed.
7. **Preflight is not optional.** Every defect that cost a re-render was visible in the
   mock-up beforehand: un-typeset flowchart captions, undrawn `<<BOX>>` rectangles, clipped
   table cells, a heading colliding with the top rule, rows overlapping after jitter.
8. **Ship small matra slips.** Devanagari renders occasionally miss a matra. Harden the
   prompt and move on; do not re-render pages for it.
9. **Page order comes from `ORDER.txt`**, never from an alphabetical sort — a plain sort puts
   every `dia-NN` before every `page-NN`.

---

## 5. What's in the box

```
setup.sh, requirements.txt          one-command setup

GPT-Notes/
  cost_guard.py                     the cost levers, enforced on every API call
  .env.example                      key goes here (the real .env is NOT in this zip)
  BUILD_PROMPT_mockup_pipeline.md   the spec the mock-up method was built from
  Hindi Hand/
    COST-PLAYBOOK.md                READ FIRST before spending
    STYLE-ANALYSIS.md               trait-by-trait breakdown of the handwriting
    MANIFEST.md / RENDER_LOG.md / PENDING.md
    prompt-hindi.md                 legacy theory-page prompt
    prompt-diagram-hindi.md         diagram-page prompt
    mockup/
      prompt-mockup-lean.md         >>> THE PROMPT IN USE TODAY (default template) <<<
      prompt-mockup.md              the older, longer template it replaced
      import_notes.py               stage 1a — chapter HTML -> blocks.json (word-gated)
      import_pyq.py                 stage 1a — PYQ HTML -> blocks.json + figures
      typeset_mockup.py             stage 1b — blocks -> blueprint PNGs (zero API)
      preflight.py                  the mechanical gate
      gen_from_mockup.py            stage 2 — the ONE billed call per page
      publish_notes.py              stage 3
      scripts_map.py                sub/superscript handling
    paper-hindi.png                 IMAGE 1 — the blank sheet (built by make_paper.py)
    hand-anchor.jpg                 the native-res handwriting crop
    hand-anchor-full.jpg            the full reference page
    anchor-combined.png             IMAGE 2 — the merged anchor actually sent
    style-anchor.png                the approved page-01 render (size/tone reference)
    diagram-anchor.jpg, -2.jpg      hand-drawn figure references
    WhatsApp Image ….jpeg           the original photo of the real handwriting
    make_paper.py / make_anchor.py  rebuild the paper and the merged anchor
    whiten.py / scan_effect.py / rescan_clean.py    finishing filters (free)
    gen_hindi.py, import_htmls.py, publish.py       LEGACY direct path (see §6)
    figures/, updated figures/      figures used by the PYQ diagram pages
    page-contents/, page-prompts/   235 page contents + 243 built prompts (legacy path)
    notes/Hindi-Ch1/                >>> ONE COMPLETE WORKED CHAPTER <<<
      blocks.json, rows.json, plans.json
      expected/page-NN.txt          what the page is supposed to say
      mockups/page-NN.png           the blueprints
      page-prompts/page-NN-prompt.md  the exact prompt each page was rendered from
      pages/page-NN.jpg             the 23 finished pages
    chapters/MP/Ch3/                a finished PYQ booklet + its ORDER.txt

pulled_rj_biology/Hindi/            source chapter HTMLs, Ch1–Ch13 (+ their figures)
top5_pyq_html/…/Hindi/              source Top-5 PYQ HTMLs (MP, Rajasthan, UP, Ch3)

dashboard (book assembly - scripts only)/   optional stage 4 — see §7

SAMPLE OUTPUT/                      >>> START HERE when showing this to someone <<<
  1 - handwriting reference/        the real hand, the crop, the merged anchor, the paper
  2 - blueprint vs render/          page-01/04/09: blueprint PNG beside the finished page
  3 - finished notes pages (Ch1)/   6 finished notes pages
  4 - finished PYQ pages (MP Ch3)/  a whole finished PYQ booklet
  5 - finished book PDF/            MP Board Chapter 03, cover + notes + PYQs, as shipped
```

---

## 6. Legacy path (kept because the MP/RJ PYQ pages were made with it)

`import_htmls.py` → `page-contents/` + `page-prompts/` → `gen_hindi.py` → `generated/` →
`publish.py`. It sent an unmeasured page straight to the image model. Everything new should
go through the mock-up pipeline instead — same output, laid out and checked before a call is
billed. The legacy prompts (`prompt-hindi.md`, `prompt-diagram-hindi.md`) are still the
reference for the two-ink rule and the diagram style.

**Two-ink rule** (both paths): questions and every heading in **black**, everything else in
**muted blue**. That is also exactly the PYQ convention — black question, blue answer — which
is why PYQ cards map onto the notes block kinds with no special casing.

---

## 7. Stage 4 — assembling board books (optional, scripts only)

`build_bio_hindi_books.py` composes cover + notes + that board's PYQ pages into the shippable
per-chapter PDF (see `SAMPLE OUTPUT/5`). Two things before it will run:

* Its `ROOT`, `NOTES_ROOT`, `PYQ_ROOT`, `OUT_ROOT` are absolute paths to the original
  machine — edit them.
* Its frame templates and board cover pages (`dashboard/templates_assets/`,
  `dashboard/front_pages/`) are **not in this zip** — 147 MB of PNGs. Ask for them
  separately if the team needs to build books rather than pages.

`fit_mode` must stay `stretch` for Hindi: the renders are 1024×1536 and the template slot is
1791×2793, so cover-fit centre-crops ~2% off each side and clips the outer ruling.

---

## 8. Deliberately not included

* the real API key (`GPT-Notes/.env` — copy `.env.example` and fill it in)
* book template/cover assets (147 MB, see §7)
* the other 25 worked chapters and their renders (~1.2 GB) — one full chapter is shipped
  instead, plus a finished PYQ booklet and a finished book PDF
