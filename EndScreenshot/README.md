# EndScreenshot

The still the video ends on — a question and its full answer, hand-written in a
student's hand on ruled notebook paper, for the viewer to screenshot.

```
blank ruled sheet ──STEP 1──► temp (base sheet) ──STEP 2──► the photo
                    TEMP_PROMPT                   MASTER_PROMPT + handwriting ref
```

Ported from the sibling `notes-editor` repo (`handwrite.py`, master prompt
**V32**). The prompt lineage lives in [`prompts.py`](prompts.py).

---

## Two steps, always

Every EndScreenshot photo is generated in two passes:

**Step 1 — the temp.** The blank ruled sheet is sent through the image model on
its own and comes back as the base page. In `notes-editor` this pass erases the
ink from a written sample; here the sheet is already blank, so its real job is
to *re-photograph the paper through the same model that will write on it*.

That matters because step 2 is an image **edit**. The model holds a page it
generated itself far more faithfully than a flat synthetic PNG — hand it a
model-native sheet and the ink lands on paper that already has the grain, tint
and lighting the writing has to sit in, instead of the model quietly
re-rendering the paper underneath the text as it writes.

**Step 2 — the main photo.** The question and answer are written onto that base
page in the reference hand, using master prompt V32 — the prompt whose entire
point is *imperfection*: variable pen pressure, dry-pen skips, ink pooling,
non-uniform letterforms, a gently jagged left edge.

### The temp is cached

It depends only on `(sheet, TEMP_PROMPT_VERSION, model, quality)`, so a second
question on the same sheet reuses it and pays for step 2 alone. Cached temps and
their provenance sit in `out/temp/temp_<fingerprint>.{png,json}`. Force a new
one with `--fresh-temp`.

---

## Use it

```bash
# standalone
python -m EndScreenshot \
    --question-file EndScreenshot/content/q1_question.txt \
    --answer-file   EndScreenshot/content/q1_answer.txt \
    --stem q1_berkeley_hartley

# into a project's assets/, ready for the script's answer_image:
./bin/video endscreenshot <slug> --question-file ... --answer-file ...

# see the tagged lines and the page split, no API calls
python -m EndScreenshot --question-file ... --answer-file ... --dry-run
```

```python
from EndScreenshot import generate
result = generate(question, answer,
                  sheet="EndScreenshot/assets/blank_ruled.jpeg",
                  style="EndScreenshot/assets/sample_hand.png",
                  out_dir="EndScreenshot/out")
```

Needs `OPENAI_API_KEY`; honours `OPENAI_IMAGE_MODEL` (default `gpt-image-2`)
and `OPENAI_HANDWRITE_QUALITY` (default `medium`).

---

## Writing the answer

Plain text with three conventions, turned into the master prompt's control tags
by `tag_content()`:

| You write | Becomes | Rendered as |
|---|---|---|
| first paragraph | `<<ANS>>` | carries the "Ans:" label |
| later paragraph | `<<TEXT>>` | prose, wraps naturally, no marker |
| `# कार्यविधि` | `<<SUBHEAD>>` | section heading in the heading ink |
| `(i) …`, `- …`, `1. …` | `<<POINT>>` | one list item with one dot marker |
| blank line before a heading | `<<GAP>>` | one deliberately empty ruled row |

Markdown image embeds and bare URLs are stripped — OCR'd textbook answers carry
mathpix links, and writing a URL onto a notebook page is never right.

**The text is rendered verbatim.** Nothing summarises, expands or "corrects" it,
so whatever you put in `content/` is exactly what appears. Fix the wording there,
not in the prompt.

---

## Pages are measured, not guessed

The ruled lines on the temp are **counted**, and each tagged line is costed in
rows. A page breaks only when it is physically full, so the writing stays one
steady size instead of the model cramming or padding to fit. Each page then
carries a measured fill note (`FILL_FULL` / `FILL_SPREAD` / `FILL_PARTIAL`)
telling the model how much of the sheet it should end up covering.

Devanagari gets a lower words-per-row budget than Latin (5 vs 7) — Hindi words
carry a शिरोरेखा plus matras and run visibly wider. Without that split, every
Hindi page overflows.

Run `--dry-run` before spending an image call; it prints the row cost of every
line and the resulting page split.

---

## Layout

```
EndScreenshot/
  __init__.py      public API + default asset paths
  __main__.py      python -m EndScreenshot
  prompts.py       TEMP_PROMPT (step 1) + MASTER_PROMPT V32 (step 2) + fill notes
  api.py           the images/edits call (stdlib urllib + multipart)
  layout.py        tagging, row measurement, page packing
  pipeline.py      the two-step flow, temp caching
  assets/
    blank_ruled.jpeg   the sheet written on
    sample_hand.png    the handwriting copied
  content/           question + answer text
  out/               generated pages (+ out/temp/ cache) — gitignored
```

## Known limits

- **The style reference is English handwriting.** `sample_hand.png` is an
  approved page from `notes-editor`, which sets the ink colours, pen habits and
  layout well, but it shows no Devanagari. For the best Hindi output, drop in a
  real page of Hindi handwriting and pass `--style`.
- **The sheet has no vertical margin rule.** Master prompt V32 puts "Q1:" and
  "Ans:" out in that margin, so `NO_MARGIN_OVERRIDE` is applied by default to
  keep the labels inline. Pass `--margin-line` if your sheet has one.
- **No diagram yet.** The master prompt supports `[[DIAGRAM …]]` blocks, but
  `tag_content()` does not emit them. An answer whose textbook figure matters
  needs that wired up.
