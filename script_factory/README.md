# script_factory — question + answer → a checked script

Give a question and its answer; get back a script ready for HeyGen. The script is
delivered only after it passes a mechanical gate and five reviewer agents.

This sits **before** the existing process. Nothing here touches PROCESS.md, the
renderer, or any existing file: once the script is recorded, the build continues
exactly as now.

## How to run it

Ask for a script and supply the question and the answer. That invokes the
`pyq-script` skill (`.claude/skills/pyq-script/SKILL.md`), which does this:

```
question + answer
      ↓
  1. plan       deliverables, part count, which sentences are book lines
      ↓
  2. draft      written to script_factory/out/<QID>/draft.md
      ↓
  3. gate.py    mechanical checks — instant, no model calls          ← must exit 0
      ↓
  4. five reviewers, in parallel:
        script-accuracy   is anything factually wrong?
        script-scope      does it answer exactly what was asked?
        script-exam-fit   would the student score full marks?
        script-voice      would the editor rewrite any line?
        script-clarity    where would a student get lost?
      ↓
  5. fix only the flagged lines, re-run          (up to 3 rounds)
      ↓
  6. deliver    only when the gate is green and all five say PASS
```

The gate alone can be run by hand:

```bash
python3 script_factory/gate.py out/<QID>/draft.md \
    --answer out/<QID>/answer.txt --years 2019,2022 --category LA
```

Exit 0 means deliverable. Warnings never block on their own.

## Files

| File | What it does |
|---|---|
| `gate.py` | The mechanical checks. Parses the script, applies ~20 rules, prints findings with line numbers, exits 1 on any error |
| `calibrate.py` | Runs the gate over all 111 shipped scripts and reports what it flags — run this after changing any rule |
| `TEMPLATE.md` | The house script format, with the required opening, part mechanics and closing block |
| `out/<QID>/` | Per script: `question.txt`, `answer.txt`, `draft.md`, `gate.json` |

The style rules the gate and the reviewers enforce come from
[`../script_index/`](../script_index/), which catalogues the 111 shipped scripts.

## What the gate checks

**Errors — these block delivery**

| Code | Rule |
|---|---|
| `E-OPEN` | Part 1 opens on the board/class/year line (92 of 111 scripts), or an importance frame when there is no year |
| `E-YEAR` | The opener's year matches the one supplied |
| `E-CLOSE` / `E-CLOSE-EARLY` | The Notes-button close is in the final part, and only there |
| `E-MIXCLOSE` | The deprecated उन्नति बैच close is not mixed with the current one |
| `E-BANNED` | No phrase the editors strip out (मार्क्स, फॉलो, वेलकम बैक, वापस आ गए, …) |
| `E-BRIDGE` | Each later part opens by naming what the previous one established |
| `E-HANDOFF` | Each non-final part hands the student forward |
| `E-COUNT` | An announced count is matched by the ordinals in the body |
| `E-READOUT` | Every on-screen formula has a spoken read-out near it |
| `E-COVERAGE` | Every sentence of the source answer is covered by the script |
| `E-JUNK` | No LaTeX leftovers, Google Docs comment anchors, or collapsed formulas |

**Warnings — reported, not blocking:** long lines, romanised Hindi, English
discourse words spelled in Devanagari, a close that stops at the Notes button, no
year in the opener, no ON SCREEN blocks, a mixed तुम/आप register, length outside
the shipped range, a repeated line, part dividers that look like section headings,
and a meta ratio outside the corpus band.

## Calibration

A gate that fails the team's own work is a gate nobody keeps running — that is
what happened to the previous checker, which demanded त्रैमासिक परीक्षा and an
उन्नति बैच sign-off that no recent script uses.

So the rules here were tuned against the corpus:

- **85 of the 111 shipped scripts pass** with zero errors.
- **26 are blocked**, and they are the files [`../script_index/DEFECTS.md`](../script_index/DEFECTS.md)
  documents: Google Docs comment anchors left in spoken lines, `EaE_a` and `dSdS`
  LaTeX leftovers, a script whose opener names a different year from the sheet, a
  truncated file, and on-screen formulas with no spoken read-out.
- A deliberately broken draft — wrong year, banned word, broken count, missing CTA,
  romanised Hindi, an unspoken formula — is caught on all six counts.

Re-run `calibrate.py` after touching any rule. If a check starts firing on a large
share of the corpus, the check is wrong about the house style, not the corpus.

## Limits worth knowing

- **The gate cannot judge meaning.** It cannot tell whether a fact is right, whether
  the explanation teaches, or whether a line sounds like the presenter. That is why
  the five reviewers exist, and why the gate runs first — it removes the mechanical
  faults for free before any model reads the draft.
- **Coverage is word overlap**, not comprehension: it catches a dropped point, not a
  point that is mentioned but taught wrongly.
- **The source answer is taken as the authority.** If it is wrong, `script-accuracy`
  is the only thing standing between the error and the video — and the same answer
  is what the Notes page shows the student.
- **These scripts are for a human presenter**, so digits and symbols in spoken lines
  are fine, exactly as in the shipped corpus.
