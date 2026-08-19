# BUILD PROMPT — the mock-up ("temp") pipeline for handwritten notes

Hand this whole file to an engineer or a coding agent. It specifies a feature
to be built from scratch. Follow it in order; every numbered step is a
checkpoint you can verify before moving on.

---

## 0. What you are building, and why

There is an existing app that turns a Class-10 chapter PDF into a PDF of
notebook pages that look handwritten. Each page is produced by an image model
that is given a blank ruled sheet and a description of what to write.

**The old way (do not rebuild this).** The layout was described to the image
model *in prose*: "write the heading, then a paragraph, leave a blank row,
then five bullets, fill the page but do not overflow." The model had to guess
how much text fits on a sheet, where each line breaks, and how far down to
stop. It guessed badly and inconsistently. Recovering a page took repeated
regeneration — roughly **25 billed images for an 11-page chapter**.

**The way you are building.** Do the layout **in Python, deterministically,
with zero API calls**. Typeset the entire chapter onto pixel-accurate copies
of the real ruled sheet, at the real geometry, in the real colours — a
page-by-page **mock-up** of the finished notebook. Then hand each mock-up
page to the image model as a reference image and ask it to *re-write that
page by hand*.

The single idea that makes this work:

> **Stop describing the layout. Show it.**
> The model never has to work out how much fits on a page, because it can see
> a page that already fits. Its only remaining job is handwriting.

Target: **one billed image per page**, with the layout decided for free.

The mock-up is deliberately *typed*, not handwritten-looking. It is a
blueprint, not a style reference. Style comes from a separate scanned sample.

---

## 1. Deliverables

| File | Purpose |
|---|---|
| `typeset_mockup.py` | Stage 1 — the typesetter. No network access of any kind. |
| `draw_from_mockup.py` | Stage 2 — draw ONE page via the image model. |
| `gen_chapter.py` | Stage 2 runner — whole chapter, resumable, assembles the PDF. |

Stage 1 must run offline. If it imports an API client, you built it wrong.

---

## 2. Stage 0 — calibrate against reality (do this first, it gates everything)

Two measurements are load-bearing. Both must be **measured**, never guessed.

### 2.1 Measure the blank sheet

Take the actual `blank.png` the app writes on. Find, in pixels:

- image size (reference implementation: `1024 x 1536`);
- the y of every printed horizontal rule. Fit them to `y = Y0 + PITCH * n`
  (reference: `Y0 = 91.0`, `PITCH = 46.862`, `N_RULES = 30`);
- the x of the printed red vertical margin (reference: `105`).

Derive and hard-code:

```python
TEXT_X      = 126          # body text starts just right of the red margin
RIGHT_X     = 990          # ragged right edge stops here
FIRST_ROW   = 1            # the TOP rule stays blank
LAST_ROW    = N_RULES - 2  # the BOTTOM rule stays blank
USABLE      = LAST_ROW - FIRST_ROW + 1        # 28 writable rules
MARGIN_LABEL_X = 24        # Q1) / Ans) labels live LEFT of the red margin
BULLET_DOT_X   = TEXT_X + 10
BULLET_TEXT_X  = TEXT_X + 46
INK_BLUE  = (38, 58, 122)
INK_BLACK = (44, 40, 38)
```

Top and bottom rules stay blank because a real student does not write on the
first or last line of the page.

### 2.2 Calibrate the font to the real hand — DO NOT PICK A SIZE BY EYE

This is the step everyone skips and it breaks the whole pipeline if wrong.

Take a page of the **actual handwriting sample**. Pick a sentence on it that
spans most of the width. Measure its pixel width. Then choose the typeface
size whose rendering of that same sentence matches to within ~1%.

Worked example from the reference implementation: the sample writes
`"Economic activities can be classified on different"` at **780 px**, which
Arial 36 matches. Its headings are narrower — `"Classification of Economic
Activities"` at **544 px** — hence bold 32 for headings.

```python
FONT_BODY  = truetype("Arial.ttf",      36)
FONT_BOLD  = truetype("Arial Bold.ttf", 32)
FONT_TITLE = truetype("Arial Bold.ttf", 38)
```

Why it is load-bearing: the mock-up's line breaks become the drawn page's
line breaks. Too wide (Arial 38 was 7% wide) and the mock-up wraps early, so
every written line stops short of the margin and the page looks half-empty.
Too narrow and the real hand overflows the sheet.

---

## 3. Stage 1 — the typesetter

CLI:

```
typeset_mockup.py <source.pdf> <out.pdf>
    [--rows-json  out_rows.json]     # what landed on which rule — for debugging
    [--plans-json out_plans.json]    # tagged per-page content — Stage 2 eats this
    [--space-points] [--space-blocks] [--fractions]
```

Outputs: the PDF, **one PNG per page**, plus the two JSON files. The PNGs are
what Stage 2 shows the model.

### 3.1 Read the source

Use PyMuPDF. Extract per-line: `text`, `size` (max span size), `bold`
(**by majority — see below**), and the line's bounding box.

> **Rule: `bold` is a MAJORITY vote, not "any span".** Compute bold as
> `>60% of characters in the line are bold`. With an any-span test, a single
> emphasised fragment such as `3 x 10⁸` promoted its entire sentence to a
> heading.

Then drop page furniture: page numbers, running headers/footers, watermarks,
and repeated chapter titles after the first.

### 3.2 Classify each line: `title` / `subhead` / `point` / `text` / `drop`

Do **not** hard-code one house style. Different textbooks are set differently
— one uses 11pt regular body with bold sub-heads; another sets *every word in
bold* and marks headings by making them **smaller** than the body. A fixed
"bold means heading" rule reads that second kind of book as one giant heading.

Detect the house style first:

```python
body = the font size carrying the most characters in the document
body_all_bold = (bold chars at body size) > 0.6 * (all chars at body size)
```

Then apply the tests **in this exact order** — the order is the fix for four
separate real bugs:

1. **Numbered section heading** — `^\d+[.)]\s+[A-Z][A-Z \-]{3,}$` or
   `^\d+[.)]\s+[A-Z][^.!?]{2,55}$` → `subhead`.
   Catches `2. REFLECTION OF LIGHT` and `1. Rational Numbers` alike.
2. **Bullet glyph** at line start → `point`, strip the glyph.
3. **Bigger than body, and no title seen yet** → `title`.
4. **Bigger than body** → `subhead`.
5. **Bold, body is not all-bold, and `len(text) <= 130`** → `subhead`.
6. **Numbered line at body size** → `point`.
7. **body_all_bold and smaller than body** → `subhead` if short and not
   sentence-like; `drop` if it starts `Fig`/`Figure`/`Table`.
8. **Everything else** → `text`.

Four traps, each of which was a real bug:

- **The numbered test MUST come before the point test.** Classified as a
  point, `2. REFLECTION OF LIGHT` let the paragraph merger swallow the body
  beneath it, producing `"2. REFLECTION OF LIGHT When light falls on the"`.
- **The `len(t) <= 130` guard on the bold test.** A whole bold *paragraph* is
  emphasis, not a heading. Without the guard a bold paragraph longer than a
  page became an unbreakable block and the chapter could not be paginated at
  all.
- **The title is the FIRST heading-tier line, not the biggest.** A later
  section heading can be set slightly larger than the chapter header itself;
  comparing against the document maximum picked the wrong line as the title
  and split the real one apart.
- **EVERY branch must assign a kind. Add an explicit `else: "text"`.** A
  fall-through in the all-bold branch left the internal `line` kind, which the
  merger ignores — so every source line became its own short notebook row, and
  the image model then squeezed those short rows in at half size. This one bug
  corrupted 20 of 28 pages of a chapter and presented as "the font size is not
  good on page 24".

Also: put your bullet-glyph list in ONE constant and make it complete,
including arrow bullets:

```python
BULLETS = ("●","•","▪","◦","‣","-","–","➢","➣","➤","▶","►","❖","✓","*","·")
```

Missing `➢` left stray glyphs on the page AND caused those lines to be
misread as headings.

### 3.3 Reconstruct tables from geometry

The PDF has no table structure; you must infer it from coordinates.

- Group text spans into **rows by shared y** (band tolerance ~ the row gap).
- Group into **columns by x**, tolerance **30 px** (12 px was too tight and
  split single columns).
- A candidate row belongs to the table when its **cell count matches the
  header's**.
- **Wrapped line vs new row:** a vertical gap under `row_gap * 0.6` means the
  text wraps within the current row; more means a new row.
- **Column alignment must be judged against `groups[-1]` (the previous row),
  not `groups[0]`** — the header is often centred, so aligning to it
  mis-assigns every body cell.
- **Tables continue across source page breaks.** Do not stop at one.
- **Detect merged cells** rather than folding them into the previous row.

> **Critical bug to avoid: never mutate the source line objects while testing
> a table candidate.** The reference implementation wrote merged cell text
> back into the originals, so when a candidate was rejected the text was
> emitted twice — once as a table and once as prose. Copy first:
> `groups.append([dict(c) for c in sorted(band, key=...)])`

### 3.4 Merge lines into blocks

Rejoin consecutive `text` lines into paragraphs; keep `point`s separate;
never merge across a heading. Output is a flat list of blocks:
`{"kind": ..., "text": ..., optional "rows"/"cells"/"entries"/"img"/"gap"/"hl"}`.

### 3.5 Optional structural spacing (CLI flags)

- `--space-points` — blank rule between **consecutive list items**, never
  between a heading and its first item. *Science chapters need this*:
  properties, reactions and steps run together into a wall otherwise.
- `--space-blocks` — blank rule between consecutive prose/point blocks.
- `--fractions` — join `p` / `q` into `p/q`. **Gate this behind the flag and
  restrict numerators to 1–3 characters.** Ungated it welded `Convex` and
  `Mirror` into `Convex/Mirror`. Only maths books should use it.

### 3.6 Special block: the timeline

A run of 3 or more consecutive `<year> <event>` lines under a heading matching
`/timeline/i` becomes a `timeline` block, drawn as a **vertical spine with a
tick per date** — years in black to the left, events in blue to the right —
not as a list of lines.

### 3.7 Turn blocks into ROWS

The pagination unit is the **ruled row**, not the paragraph. Wrap every block
to `RIGHT_X` and emit one item per row. Each item carries `x`, `font`, `ink`,
`bid` (block id), `tag`, and flags: `centre`, `bullet`, `head`, `hl`, `hard`.

`hard` means "a page break may not fall immediately before this row" — set it
on continuation rows of a title or subhead.

> **Answer/question continuation rows must NOT be hard** beyond the first:
> `"hard": k > 0 and b["kind"] == "q"`. Marking them all unbreakable made
> three chapters impossible to paginate.

**Blank rows.** Write one helper and route every gap request through it:

```python
def _add_gap(items):
    if items and items[-1]["t"] != "gap":
        items.append({"t": "gap", ...})
```

One blank rule separates two topics; two in a row is just a hole. Gaps are
requested from several places at once — after a heading, before a table,
before a figure, between list items — and a table under a heading collected
three of them, which also made the heading group too tall to drop into the
space at the foot of a page.

**Every heading gets air BOTH above and below it.** Without the gap
underneath, the topic name and its first line read as one paragraph and the
section it opens has no visible start. Then: a heading may never be the last
thing on a sheet — glue the heading, its following blank, **and** the first
real line after it into one unbreakable group. Gluing only the next item
strands the heading above a blank foot.

### 3.8 Paginate — fill every sheet, slack only on the last

Two passes over the row list:

1. **Backwards DP** for `minp[i]` = the fewest sheets rows `i..n` can occupy.
2. **Forward greedy**: at each break take the **fullest** page that still
   leaves `minp` reachable.

```
if minp[0] == INF: raise "cannot paginate: a single block is taller than a page"
```

> **Do not minimise squared blank space.** That measure (the Knuth-Plass one)
> is convex, so it *spreads* the slack evenly and leaves two or three blank
> rules at the foot of **every** sheet. Packing greedily cannot cost a sheet
> because the minimum is enforced, and the slack it pushes forward ends up
> where it belongs — on the final page.

Trim leading/trailing gaps from each page. A chapter never ends on a blank
rule.

### 3.9 Elastic figures

Embedded images are extracted and pasted where they occur (skip anything
under 60x60 — those are icons and bullet glyphs, not figures).

A figure that just misses the foot of a page gets pushed to the next one and
leaves a hole behind it. Order cannot change, so let the figure **shrink**
into whatever room is left, down to a floor of `max(3, 0.6 * rows)`. Re-run
pagination after shrinking; iterate up to 3 times.

Note when computing available room: a figure always travels behind a blank
rule, and that separator is only free while it sits **on** the page break —
pull the figure up and the blank becomes an interior row you have to pay for.
So `room = USABLE - used - 1`.

### 3.10 Imperfection — the page must not look printed

Perfectly regular output reads as machine-made. Add **deterministic** jitter,
seeded from `(page, row, words)` so a rebuild is byte-identical.

```python
JIT_BLOCK_X = (-9.0, 17.0)   # per-paragraph horizontal scatter
JIT_ROW_X   = (-7.0,  8.0)   # per-row horizontal scatter
JIT_SPACE   = (-1.3,  2.4)   # per-word-gap
JIT_Y       = (0.0, 0.0)     # ZERO
JIT_WORD_Y  = 0.0            # ZERO
JIT_SLOPE   = 0.0            # ZERO
```

> **All vertical jitter is ZERO, by explicit instruction. Horizontal only.**
> Words that float above or below their rule look like a rendering fault, not
> like handwriting. Every baseline sits on its printed rule; the variation is
> left-right.

The visible target is that **bullet dots and the numbers 1. 2. 3. do NOT line
up on one vertical**. Make sure the bullet dot carries its own row's offset —
forgetting that leaves a perfect column of dots beside jittered text.

### 3.11 Deliberate slips of the pen

Inject a small number of misspellings (roughly one every 2–3 pages), typeset
as `wrong` struck through followed by `right`. Carry the pair through the
pipeline as a single word joined by a separator (`"\x00"`) so wrapping cannot
split it, and emit it to the plan as `[[FIX wrong|right]]` with trailing
punctuation left outside the marker.

Order matters: paginate → inject (needs the page boundaries) → **paginate
again** (the slips shift the text).

### 3.12 Draw the mock-up and emit the plans

Draw onto a copy of the real `blank.png`: text on rules, headings in black,
body in blue, hand-made bullet dots, hand-ruled tables (a wavy `_wobble`
stroke, not a straight line), highlighted rows on a yellow band, figures
pasted at low contrast.

`--plans-json` emits, per page, the **logical** lines — wrapped rows rejoined,
so Stage 2's text prompt sees whole sentences while the *image* carries the
line breaks:

```
<<TITLE>> FEDERALISM
<<GAP>>
<<SUBHEAD>> What is Federalism?
<<GAP>>
<<TEXT>> Federalism is a system of government in which powers are divided...
<<POINT>> Two or more levels of government.
[[TABLE hand-ruled, 2 columns]]
Row: Giuseppe Mazzini | Founded Young Italy
[[DIAGRAM a figure from the textbook]]
[[HIGHLIGHT]]   (prefix on the line it applies to)
[[FIX sysdem|system]]
```

A block split across a page break appears on **both** pages, each carrying its
own part.

---

## 4. Stage 2 — hand-write each page

### 4.1 The images, in this order

| | Image | Role |
|---|---|---|
| 1 | the real blank ruled sheet | what gets written on |
| 2 | the scanned handwriting sample | **whose hand** to use |
| 3 | **the mock-up PNG of this exact page** | **what goes where** |
| 4 | an already-drawn page of this chapter | style anchor, so the notebook is consistent |

Draw page 1 first with no anchor; every later page passes page 1 as IMAGE 4.

### 4.2 The override prompt

Append to the base prompt, marked as outranking everything above it:

- **IMAGE 3 IS THE LAYOUT OF THIS EXACT PAGE. It is a BLUEPRINT, not
  something to copy the look of.** Same lines, same order, same ruled rows;
  each line breaks at the same word; the page ends where IMAGE 3 ends. If the
  handwriting runs wider than the typed line, keep the same words on that row
  and let the right edge stay ragged — never drop a word, never shrink to
  catch up.
- **IMAGE 3 is TYPED only so the layout is legible.** Your page is
  handwritten throughout; never imitate the typeface.
- **COPY IMAGE 3's IRREGULARITY, NOT JUST ITS WORDS.** The left edge is
  ragged; bullets and numbers sit at visibly different distances from the
  margin; word spacing is uneven. Do not regularise it into a grid.
- **TWO PENS**: every line IMAGE 3 shows in black is written in black —
  the title and **every** topic heading, *including numbered ones* like
  `1. Union List:-`. Blue headings are wrong.
- **EVERY BLANK RULED ROW IN IMAGE 3 STAYS BLANK** — see 4.3, this needs
  reinforcement.
- **LINES REST ON THE PRINTED RULES.** State it as *"the rule is a shelf; a
  line may sit a whisker above or below the way a real hand does"* — **not**
  as "EVERY LINE SITS ON A PRINTED RULE". The absolute phrasing snaps every
  baseline back to a perfect grid and cancels your jitter. This was measured:
  mock-up bullet spread 24 px, drawn page 12 px. Amplifying the jitter did
  almost nothing; softening this one sentence was the actual fix.
- **LETTER SIZE IS FIXED AND NEVER CHANGES** — one line of text occupies one
  ruled row at full size. Never shrink to fit more in; content continues on
  the next page.
- **FIGURES: any figure in IMAGE 3 is a FADED GREY GUIDE, NOT ARTWORK.** It
  is there at low contrast for one reason — to show *what* the figure is,
  *where* it sits and *how big*. Ignore how it looks and draw the same
  subject freehand in pencil: varying pressure, wobbling curves, boxes not
  square, each arrowhead a different size, repeated elements each drawn
  separately. Labels in the page's own handwriting on crooked leader lines.
- **TABLES are ruled by hand** — wavy, corners not meeting, never ruler-drawn.
- **HIGHLIGHTER**: rows on a yellow band, or marked `[[HIGHLIGHT]]`, get one
  quick yellow stroke, wider than the text, overshooting one end. **Never
  write the literal words `[[HIGHLIGHT]]`.**
- **CORRECTIONS**: where IMAGE 3 shows a struck word followed by another,
  write the struck word as spelled, strike it end to end, then write the
  correct word. Both words must appear. Add no corrections of your own.

### 4.3 Make the blank rows a COUNTED requirement

The model will otherwise close the gaps up — it writes a heading and starts
the body on the very next rule, silently deleting exactly the spacing you
typeset. Prose instructions alone do not fix this; it complied about half the
time.

What works is giving it a number to check itself against, computed per page:

```python
n = content.count("<<GAP>>")
prompt += (f"\n* THE BLANK ROWS ARE PART OF THE LAYOUT: this page's content "
           f"has {n} <<GAP>> lines, so your page shows exactly {n} completely "
           f"EMPTY ruled rows, one at each of those points. EVERY heading is "
           f"followed by one — write the heading, skip the next rule "
           f"entirely, then start the body on the rule after it.")
```

**Watch the prompt length.** The image API caps the prompt at **32,000
characters**. Assert on it and fail loudly rather than letting the API 400.
Budget the worst-case page, plus the gap note, plus the IMAGE 4 note.

### 4.4 The runner

- **Resumable**: skip any page whose PNG already exists on disk. Chapters are
  regenerated often and every redrawn page is billed.
- **Diff and keep**: when a temp is rebuilt, compare page by page and redraw
  only what changed. On one chapter this turned 132 images into 51 across
  three rounds.
- Draw page 1, then the rest with bounded concurrency; retry failures a
  couple of times.
- Assemble the PNGs into `<CHAPTER> — AI handwritten.pdf` at 150 dpi.
- Write a `meta.json` recording the image count.

---

## 5. Acceptance criteria

Build is not done until all of these hold on a real chapter:

1. Stage 1 makes **zero network calls** and is byte-deterministic across runs.
2. Every sheet except the last is full to its last writable rule.
3. Top and bottom rules are blank on every sheet.
4. Every heading has exactly one blank rule above **and** one below it, and no
   heading is the last written thing on a sheet.
5. Never two blank rules in a row.
6. Headings and title are black; body is blue; the drawn page matches.
7. Bullet dots and numerals do **not** form a vertical column, in the mock-up
   **and** in the drawn page — measure the spread in pixels, do not eyeball it.
8. No word sits above or below its rule.
9. Tables carry the source's real header row, keep each source row on one row,
   and continue correctly across source page breaks. Cross-check every table
   against the source PDF by hand once.
10. Rebuilding a temp and redrawing costs images **only** for pages that
    actually changed.
11. Cost check: an N-page chapter costs N images on a clean run.

---

## 6. Known limits — do not claim these are solved

- **Fractions.** At line level a PDF gives `p` and `q` as separate lines, so
  `p/q` typesets as a stray `p` and `½, −¾, 5, 0, 7/9` comes out
  `1 2 , −3 4 , 5, 0, 7 9`. Maths chapters need **word-level position
  extraction** before they are drawable. Do not draw a maths chapter until
  this is fixed.
- Where a PDF stores two table cells as a single text run, the column
  boundary is unrecoverable at line level.
- Figures are still partly traced despite the low-contrast ghosting.
- The model still normalises bullet columns somewhat, and still eats the blank
  rule under a heading that lands at the very foot of a page.
