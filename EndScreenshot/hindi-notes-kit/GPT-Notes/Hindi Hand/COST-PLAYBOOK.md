# COST PLAYBOOK — read this before you render a single page

Written 16 Aug 2026 after a day that billed **93 image calls for 90 pages** across Hindi-Ch4,
Ch5 and Ch6. The per-page cost was running far higher than a teammate's on the same method, so
the whole billed path was measured and cut down. This file is the context for that work: what was
measured, what already changed in the repo, and what an agent must do before spending money.

If you are an agent picking up a chapter: **read all of §1–§4 before your first API call.**

---

## 1. What one page call actually costs you

Every billed page is one `client.images.edit` call from
[gen_from_mockup.py](mockup/gen_from_mockup.py). Before the change it shipped:

| part of the call | what it was |
|---|---|
| IMAGE 1 | `paper-hindi.png` — blank paper, 1024×1536 |
| IMAGE 2 | `hand-anchor.jpg` — stroke close-up, 958×662 |
| IMAGE 3 | `mockups/page-NN.png` — the blueprint, 1024×1536 |
| IMAGE 4 | `style-anchor.png` — a whole finished page, 1024×1536 |
| prompt | ~23,400 chars, of which only **~1,600 is this page's content** — the other ~93% was the same template re-sent on every call |
| output | 1024×1536 |

So: **three full page-sized input images plus a 22k-char constant, 93 times a day.** The mock-up
pipeline was introduced to cut cost, but the prompt never shrank when the blueprint arrived — the
blueprint was simply added as a fourth image on top of the prompt that used to do its job.

Regens were **not** the problem: 3 of 93 calls (3.2%), all Ch4 figure-label fixes. Do not spend
effort there.

---

## 2. What has already been changed (do not redo it)

**a. Four input images → three.** [make_anchor.py](make_anchor.py) merges the stroke close-up and
the finished style page onto one 1024×1536 sheet, `anchor-combined.png`:

* top band = `hand-anchor.jpg`, magnified — how a stroke LOOKS
* bottom band = a crop of `style-anchor.png` at **true page scale** — how BIG letters are, how dark
  the inks are. Cropped below the header band on purpose, so its chapter title can never be copied.
* a grey seam between them, and a prompt clause telling the model it is one sheet in two halves.

Rebuild it any time either anchor changes:

```bash
cd "GPT-Notes/Hindi Hand" && ../.venv/bin/python make_anchor.py
```

**b. A lean prompt template.** [mockup/prompt-mockup-lean.md](mockup/prompt-mockup-lean.md) is the
new default: same rules, ~29% fewer characters, and it describes THREE images instead of four.
Built prompts went from ~23.4k to ~18.1k chars.

**c. Token telemetry on every call.** `RENDER_LOG.md` now carries `fidelity`, `txt-in`, `img-in`,
`out` and `est $` columns straight off the API response, and the run prints a per-page and a
per-chapter total. Older logs keep their old table; a second table is started underneath.

**d. `input_fidelity` is explicit.** It used to be sent only when the model name started with
`gpt-image-1`, which means on `gpt-image-2` you were paying whatever the model defaults to. It is
now `IMAGE_INPUT_FIDELITY` (`low` | `high` | empty to send nothing), and a model that rejects the
parameter retries once without it instead of failing the run.

**Revert switch:** `LEGACY_REFS=1` restores the old four-image call with the old template. Use it
only to compare, never as a default.

---

## 3. MANDATORY: probe two pages before you render a chapter

A chapter is 20–40 billed calls. Never launch one blind.

```bash
cd "GPT-Notes/Hindi Hand/mockup"
../../.venv/bin/python gen_from_mockup.py Hindi-ChN page-01 page-02
```

Then **read the two new rows in `notes/Hindi-ChN/RENDER_LOG.md`** and answer, in your reply to the
user, before continuing:

1. What is `est $` per page, and does it match the real per-page figure the user sees on the OpenAI
   dashboard? If it does not, fix `PRICE_TEXT_IN` / `PRICE_IMAGE_IN` / `PRICE_IMAGE_OUT` in the
   environment so the log tells the truth from then on — those defaults are gpt-image-1's published
   rates and are almost certainly wrong for whatever model is actually set.
2. Which of `txt-in`, `img-in`, `out` dominates? That single number decides which lever below is
   worth pulling. Do not guess it — you now have it measured.
3. Do the two pages look right? Letter size, ink colours, ~28 rows, no font-like evenness.

Only then render the rest. The user gates every billed call — ask before each batch.

---

## 4. The levers, in the order they pay

**1. `input_fidelity`.** Most likely cause of a 2× gap against a teammate on the same method. Probe
two pages each way and compare `img-in` and the finished pages:

```bash
IMAGE_INPUT_FIDELITY=low  ../../.venv/bin/python gen_from_mockup.py Hindi-ChN page-01 page-02
IMAGE_INPUT_FIDELITY=high ../../.venv/bin/python gen_from_mockup.py Hindi-ChN page-03 page-04
```

If `low` holds the blueprint faithfully, it is a standing discount on every page ever rendered
again. Note: the blueprint is the one image whose detail actually matters — if fidelity drops the
page's word accuracy, stop and stay high.

**2. Fewer / smaller input images.** Already 4 → 3. The remaining merge is paper + blueprint → one
image (§6), which would make it 2. Also worth knowing: `cost_guard` downscales every input to a
1024px long edge (`COST_GUARD_MAX_EDGE`), so a 1024×1536 sheet is already sent at 683×1024. Raising
that ceiling raises cost on every image; lowering it blurs the blueprint first.

**3. Quality.** `OPENAI_IMAGE_QUALITY=low|medium` (`high` is clamped away by `cost_guard`). Ch5 ran
40 pages at `low`, Ch4 and Ch6 at `medium` — compare those chapters side by side before defaulting
to `medium` again out of habit.

**4. Model tiering.** Theory pages are Hindi handwriting on ruled paper; diagram pages are the hard
ones. Try the cheaper image model on theory pages via `OPENAI_IMAGE_MODEL` and keep the expensive
one for figures. Probe two pages, do not switch a whole chapter.

**5. Prompt length.** Cheapest of the levers, already cut 29%. Further cuts trade against quality:
most of what remains was added to fix a specific observed defect (the subscript-र, the `r`/`x`
confusion, numerals turning into bullet dots, invented figure labels). **A re-render costs far more
than the tokens a rule occupies — do not delete rules to save characters.**

---

## 5. Standing rules for whoever renders next

* **Never a billed call without asking the user first.** Dry-run (`DRY_RUN=1`) freely.
* **Preflight is a hard gate.** `gen_from_mockup.py` refuses to render a chapter whose blueprints
  fail [mockup/preflight.py](mockup/preflight.py). Fix the blueprints or the typesetter — do not set
  `PREFLIGHT_SKIP=1` to get past it.
* **A mechanical defect gets a mechanical fix.** If a fault can be caught by measuring the blueprint
  (overflow, a box rule too short, a lost superscript), add a preflight check. Adding another
  paragraph of prompt text costs money on every future page and catches nothing.
* **Every billed call is logged**, retries included — a retry is a second charge.
* **Keep the two templates in sync.** [mockup/prompt-mockup.md](mockup/prompt-mockup.md) is the
  master history; the lean fork is what actually renders. When you add a rule, add it to BOTH, then
  check nothing was lost:

  ```bash
  cd "GPT-Notes/Hindi Hand/mockup" && ../../.venv/bin/python - <<'EOF'
  import re
  norm = lambda s: ' '.join(re.sub(r'[^A-Za-z ]', ' ', s).split()).lower()
  cur = open('prompt-mockup.md', encoding='utf-8').read()
  flat = norm(open('prompt-mockup-lean.md', encoding='utf-8').read())
  for r in re.findall(r'\*\*([A-Z⛔⚠️⭐][^*]{12,90})\*\*', cur):
      k = ' '.join(norm(r).split()[:4])
      if k and k not in flat:
          print('CHECK:', r.strip()[:100])
  EOF
  ```

  It matches on a rule's first four words, so a deliberately reworded rule still shows up — read
  each hit and confirm the rule exists in some form, rather than trusting the count. As of writing
  it flags 5, all reworded on purpose (the ones naming IMAGE 4, which no longer exists).
* **`COST_GUARD_MAX_IMAGES` must be ≥ the number of refs**, or images are silently dropped and you
  pay for a render that never saw the blueprint. It is set automatically in the script; if you add a
  figure reference, raise it in the same commit.

---

## 6. Open, not yet done

* **Paper + blueprint → one image (3 refs → 2).** Typeset the mock-up directly onto
  `paper-hindi.png` so the base sheet and the layout arrive together. Not implemented because the
  prompt body refers to IMAGE 1 / 2 / 3 in ~30 places and merging renumbers them; do it properly
  with a separate two-image template, and probe two pages. Risk: the model may lean toward the
  typeface look when the type sits on the real paper.
* **Ask the teammate for their exact call** — model, quality, size, number of input images,
  `input_fidelity`, prompt length. Their per-page cost is roughly half; one screenshot of their
  parameters settles in minutes what probing settles in dollars.
* **Confirm what the per-page figure includes.** If it is the whole bill rather than the image API
  alone, the agent-side spend (page authoring, QA passes that read rendered pages as images) is a
  separate budget with separate levers, and none of §4 will move it.

---

## 7. Files this touches

| file | role |
|---|---|
| [make_anchor.py](make_anchor.py) | builds `anchor-combined.png`, free, rerun after any anchor change |
| [mockup/gen_from_mockup.py](mockup/gen_from_mockup.py) | the only billed path; refs, fidelity, telemetry |
| [mockup/prompt-mockup-lean.md](mockup/prompt-mockup-lean.md) | the template that actually renders |
| [mockup/prompt-mockup.md](mockup/prompt-mockup.md) | master/history, 4-image, used only with `LEGACY_REFS=1` |
| [mockup/preflight.py](mockup/preflight.py) | the hard gate before spending |
| `notes/Hindi-ChN/RENDER_LOG.md` | one row per billed call, now with tokens and an estimate |
| `GPT-Notes/cost_guard.py` | clamps quality, caps image count, downscales inputs — applies to every call in the project |
