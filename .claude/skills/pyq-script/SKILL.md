---
name: pyq-script
description: Write a PYQ reel script from a question and its answer, and QA it with five reviewer agents before delivering. Use whenever someone supplies a question plus an answer (or a QID from the tracking sheet) and wants a script for HeyGen — "script bana do", "is question ka script", "write the script for this PYQ". Not for editing an existing shot video.
---

# Writing a PYQ script

Input: a **question** and its **answer**. Output: a script ready to paste into
HeyGen — but only after it passes the mechanical gate and five reviewer agents.

**A draft is never shown to the user before it passes.** The user asked for a
checked script, not a draft to proofread. If it cannot pass after three rounds,
hand over the failure report instead and say what is blocking.

## Step 0 — intake

Collect, and ask only for what is missing:

| | | |
|---|---|---|
| question | verbatim, with any `अथवा` variants | required |
| answer | the source answer the Notes page will show | required |
| years | which years it was asked | the opener states it; without it the opener falls back to an importance frame |
| QID | e.g. `CHE-C3-SA-04` | gives subject and category |
| marks | 4 for LA/derivation, 3 for SA | only promise marks if known |

Write them to `script_factory/out/<QID>/` as `question.txt` and `answer.txt`.
A truncated question is a hard stop: one shipped script invented a whole Part 3
because its question was cut off mid-sentence in the sheet. Ask for the full text.

## Step 1 — plan before writing

1. **Break the question into deliverables.** "परिभाषा + तीन प्रकार + उदाहरण" is
   three. Write the list down; the scope reviewer checks the script against it.
2. **Read the question's verb** and let it set the shape — `script_index/RULES.md`
   rule 1. सिद्ध कीजिए, अन्तर लिखिए, सचित्र and क्रियाविधि each produce a different
   script.
3. **Decide the parts from the content, not the length.** SA is usually 1 part
   (~414 words), LA 3 (~913), NM 2 (~866). A part is a reel of ~290 spoken words.
   Boundaries fall at a completed idea, never mid-derivation.
4. **Pick the moves.** Open `script_index/skeletons.json` at your question type and
   use its example skeletons. Read 2–3 real scripts of the same type in
   `sheet_scripts/` — they teach more than any rule.
5. **Mark the book lines.** Decide which sentences of the source answer must be
   spoken verbatim, because the student writes those in the exam.

## Speed — without trading away any check

Target: **about 8–10 minutes per script, ~15 for a batch of five.** The first
script took ~30. None of the time saved comes from weaker review — all five
reviewers still run, on the strongest model, each reading the whole script. It
comes from removing waste:

| Where the time went | What replaced it |
|---|---|
| The voice reviewer read the 130 KB INDEX.md and several scripts (6 min) | `script_factory/VOICE_CARD.md`, one page, plus one sibling script |
| Reviewers browsed the repo to learn conventions | Each reads only the draft, question and answer |
| Round 1 kept catching the same generic faults | The "Before the first draft" list in VOICE_CARD.md, and gate checks for them |
| Round 2 re-ran all five reviewers | Round 2 re-runs only the reviewers that FAILED (plus accuracy if any fact changed) |
| One script at a time | A batch runs in parallel: draft all, gate all, then all reviewers for all scripts in one message |

**Given several questions at once, batch them.** Draft every script, gate every
script, then spawn the reviewers for all of them in a single message. The wall
clock for five scripts is barely more than for one.

## Step 2 — write the draft

**Read `script_factory/VOICE_CARD.md` before writing** — especially "Before the
first draft", which lists what round 1 caught on the first script. Getting those
right up front is what makes round 2 unnecessary.

Follow `script_factory/TEMPLATE.md` for the format and
`script_index/RULES.md` for the style. The rules that are broken most often:

- Part 1 opens on the board/class/year line. No hook before it.
- **Spoken connectors everywhere** — ये not यह, वो not वह, और not तथा, लेकिन not किन्तु —
  even inside the textbook sentence. Terms stay exactly as the book writes them.
- **2–5 hooks in the middle of a Short Answer**, each right before the trap or key line it
  flags, naming it, worded differently each time. Lean intro, lean close; the hooks
  live in the explanation.
- Textbook sentence first, then the plain gloss with मतलब / यानी.
- Every ON SCREEN formula has a spoken read-out, in one read-out dialect.
- Announced count = ordinals in the body = items in the recap.
- Each later part opens by naming what the last one established; each earlier part
  ends with what is done and what is left.
- Only the final part carries the close: question done → Notes button → keep
  watching → syllabus / 90%.
- Vary the wording — take alternatives from `script_index/phrase_bank.json` rather
  than repeating one construction.

Save as `script_factory/out/<QID>/draft.md`.

## Step 3 — the mechanical gate

```bash
python3 script_factory/gate.py script_factory/out/<QID>/draft.md \
    --answer script_factory/out/<QID>/answer.txt \
    --years 2019,2022 --category LA --strict \
    --json script_factory/out/<QID>/gate.json
```

`--strict` is for every new script: it turns the user's review into blocking errors —
length over the corpus 75th percentile, too many hook lines, an intro longer than
three lines — and bracket spell-outs of formulas always block. Fix every error and
re-run until it exits 0. Read the warnings; most are worth
fixing, and you must be able to say why if you leave one.

Do not spawn the reviewers until the gate is green — they are expensive and the
gate catches the mechanical faults for free.

## Step 4 — the five reviewers, in parallel

Spawn all five in ONE message so they run concurrently. Each gets the draft path,
the question, the answer, the category and the marks.

| Agent | Asks |
|---|---|
| `script-accuracy` | is anything factually wrong? |
| `script-scope` | does it answer exactly what was asked? |
| `script-exam-fit` | would the student score full marks? |
| `script-voice` | would the editor rewrite any line? |
| `script-clarity` | where would a student get lost? |

They are deliberately narrow and deliberately separate: a single reviewer asked to
judge everything at once passes things.

## Step 5 — fix, then re-check

**Edit only the lines that were flagged.** Do not rewrite the draft wholesale —
a rewrite reintroduces defects the reviewers already cleared, and the corpus shows
that full rewrites are what produced the unusable drafts in the first place.

Where two reviewers conflict, accuracy wins, then exam-fit, then scope, then
clarity, then voice. Note the conflict in the report.

**The length budget outranks clarity and voice.** A fix that would push the script
past the budget is not taken as offered: find a line to cut, or rewrite the confusing
line in place. The first script grew from 690 to 907 words by accepting every
clarity request, and the user returned it as too long.

Then re-run the gate, and re-run **only the reviewers that returned FAIL** — plus
`script-accuracy` whenever an edit touched a fact, a formula or a term, since a fix
for clarity can quietly break the chemistry. A reviewer that passed does not
re-run for edits outside its lane. Each re-run still reviews the whole script, with
its own round-1 findings listed so it can confirm they are fixed.

**A reviewer's own replacement wording, applied verbatim, counts as checked by that
reviewer** — re-running it just to approve its own sentence is time with no
check in it. Anything you reword yourself, or combine from two reviewers, is not
covered by this and goes back to the reviewers whose lanes it touches.

Repeat up to three rounds.

## Step 6 — deliver

Only when the gate exits 0 and all five reviewers return `VERDICT: PASS`. Give the
user:

1. the script itself, formatted for the Google Doc / HeyGen;
2. a QA line: what each reviewer checked and that it passed, plus any warning left
   open and why;
3. anything you had to decide for them — a gap filled in the source answer, an
   `अथवा` variant chosen, a year that looked wrong.

If three rounds are not enough, deliver the failure report and the blocking
findings instead. A script that quietly ships unchecked is the failure this whole
process exists to prevent.

## Keep the system learning

If the user edits the delivered script before recording, save both versions in
`script_factory/out/<QID>/` as `delivered.md` and `final.md`. Those pairs show
what the checks are still missing, and they are the sharpest material for tightening
the gate and the reviewers.
