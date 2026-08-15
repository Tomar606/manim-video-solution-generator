---
name: endscreenshot
description: Produce the hand-written question-and-answer card a video ends on — review the answer, find or place a diagram, typeset the temp for approval, then draw it and watermark it. Use when someone asks for an EndScreenshot, an end card, a handwritten notes page, or a Q&A screenshot image.
---

# Making an EndScreenshot

The still a video ends on: a question and its full answer, hand-written in a
student's hand on ruled notebook paper, for the viewer to screenshot.

Three stages. **Stage 3 pauses for human approval — never skip that.**

```bash
# S1 + S2 + S3(temp) — free, no image is drawn
python -m EndScreenshot --question-file q.txt --answer-file a.txt \
    --topic "Berkeley and Hartley" [--diagram fig.jpg]

# only after the human has looked at the temp
python -m EndScreenshot ... --topic "Berkeley and Hartley" --approve
```

Run it with the repo's venv: `PYTHONPATH=. .venv/bin/python -m EndScreenshot …`

---

## S1 — input

The Q&A arrives one of three ways:

| Input | What to do |
|---|---|
| Question + answer as text | `--question-file` / `--answer-file` (or `--question` / `--answer`) |
| A screenshot of a textbook page | `--screenshot page.png` — the Q&A is read off it |
| Either, plus "generate a diagram" | see S2 below |

**Always pass `--topic`.** It names the output folder (`out/Berkeley and
Hartley/`) and the delivered file (`BerkeleyAndHartley.png`). Derive it from the
subject of the question, not the whole sentence — 2–4 words.

## S2 — review the answer, find the figure

The answer is checked and corrected before anything is drawn, because **every
later stage renders verbatim**. This is not optional polish: the first answer
this pipeline was given came from OCR and carried mangled conjuncts
(`अर्दापारमम्य` for `अर्द्धपारगम्य`), a `₹` standing in for a `न`, and half of a
different question's answer stapled on the end. All of it would have been
hand-written onto the page.

`--no-review` renders exactly what you were given. Use it only when the human
says the text is already final.

**Diagrams.** Resolution order:

1. `--diagram <path>` — a file the user gave you.
2. `--diagram <url>` — downloaded and verified.
3. **A link inside the answer text.** OCR'd textbook answers often embed their
   own figure (mathpix `![](https://cdn.mathpix.com/…)`). *Check for this
   first* — it is the figure that belongs to this exact question and beats
   anything a search returns. It is picked up automatically.
4. **You search for one.** If the user asked for a diagram and none of the
   above applies, use WebSearch/WebFetch, download a candidate, **look at it**
   to confirm it is the right apparatus, then pass `--diagram`.

The code deliberately does not auto-search. Judging whether an image is the
right figure needs eyes on it, and silently putting a wrong diagram on a
student's notes is worse than having none.

A diagram is placed on the right and **the text wraps around it** — no rows are
reserved. Tune with `--diagram-row` (which ruled row it starts on) and
`--diagram-width` (fraction of page width, default 0.44).

## S3 — temp, approve, draw, watermark

**The temp is free and instant** — it is typeset locally, no API call. Its whole
purpose is that layout, wording, spelling and figure placement are settled
before anything is paid for.

1. Run without `--approve`. It stops and prints `⏸ S3 paused after the temp`.
2. **Show the human the temp** (`out/<Topic>/temp_page_1.png`) and wait.
3. On approval, re-run with `--approve`. The page is drawn, watermarked and
   written as `<Topic>.png`.

---

## Rules

- **Never draw without approval of the temp.** That is the whole point of the
  shape, and drawing costs money.
- **Never redraw an approved page.** Watermark size, opacity and position are
  re-stamped from `<Topic>_raw.png` at zero cost — the clean master is always
  kept. A redraw is non-deterministic and will lose the approved render:
  ```python
  from EndScreenshot import watermark as W
  W.stamp_file(d+"Topic_raw.png", d+"Topic.png",
               "EndScreenshot/assets/watermark.png", scale=0.68, opacity=3.0)
  ```
- **Never delete `_raw.png`.**
- **Check the output before reporting success.** Read the image. Look for: the
  शिरोरेखा sitting *on* the ruled lines (not floating mid-gap), correct
  spelling of technical terms, `है` vs `हैं`, and — if there is a figure — that
  its labels are right and it is hand-drawn rather than traced.
- **Two baselines, by script.** Hindi hangs *from* the rule (शिरोरेखा on the
  line); a row of pure English letters or maths symbols sits vertically
  *centred* in the gap between two rules, touching neither. `typeset.py` lays
  the temp out this way and the master prompt tells the artist the same —
  check both scripts landed correctly in the final image.
- **Maths goes into the content as readable text, never LaTeX source.** The
  temp fonts have no `₀ ∴` (and Kohinoor no Greek or `→`), so: subscripts as
  `E_0`/`ε_0` (the artist draws them lowered), Greek and `→` only on
  pure-Latin equation lines, `अत:` instead of `∴`. LaTeX commands like
  `\frac{}{}` would be typeset — and hand-written — verbatim.

## What goes wrong, and why

| Symptom | Cause | Fix |
|---|---|---|
| Hindi floats between the lines | Devanagari hangs *from* its शिरोरेखा; the model drew its own faint grid and wrote between it | The sheet's rules are strengthened in `typeset.py` so the model can't ignore them. If it recurs, darken `RULE_INK` further |
| Text spaced out, ignoring the layout | A long trailing prompt block outweighed the head-line rule | `FINAL_BASELINE_REMINDER` is appended last — keep it last |
| A figure appears in a white box | Diagram pasted opaquely over the ruling | It composites as ink only (`ghost()` returns RGBA); don't paste it opaque |
| Diagram traced, not drawn | Reference too crisp | It is pasted ghosted (~42%). Do not raise `GHOST_STRENGTH` |
| A label is wrong (`प्रमुख` for `प्रयुक्त`) | Model guessed from the faint guide | Pin this job's exact label strings via `extra_rules` (the JOB-SPECIFIC OVERRIDES block) — `DIAGRAM_PROMPT` itself stays generic |
| A figure appears on a page that has none | The diagram spec reached every page | `generate()` sends `diagram_rules` only to the diagram's page and tells the others "draw NO diagram" — keep it that way |
| A term is misspelled | Model reconstructing Devanagari conjuncts | Name the exact spelling in the overrides — the temp shows the right glyphs, so say "copy IMAGE 3 letter for letter" |

## Layout

```
EndScreenshot/
  prompts.py    every prompt: temp, master V32, diagram, the closing baseline rule
  review.py     S2 — read a screenshot, correct the answer, resolve the figure
  typeset.py    S1/S3 — the free typeset temp: geometry, wrapping, diagram flow
  pipeline.py   run() = S1 -> S2 -> S3; generate() = the draw
  watermark.py  centred stamp, re-stampable from the raw master
  api.py        the images/edits call
  out/<Topic>/  temp_page_1.png · <Topic>.png · <Topic>_raw.png · question/answer/notes
```
