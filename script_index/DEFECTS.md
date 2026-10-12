# What not to copy from the corpus

The 111 scripts are the style reference, not a clean training set. Everything below
was checked against the files. A generator that learns from the corpus naively will
reproduce these.

## Files that are not single clean scripts

| File | Problem |
|---|---|
| `chemistry/CHE-C2-LA-01.txt` | Two complete drafts of the same video, back to back — it has 2 board-line openings — plus Google Docs comment footnotes |
| `physics/PHY-C1-LA-01.txt` | Contains a second tab whose equations were stripped on export |
| `physics/PHY-C3-SA-03.txt` | Truncated mid-derivation: the file ends on a bare `स्पोकन:` with nothing after it |
| `physics/PHY-C5-LA-01.txt` | An orphan handoff sits above the title; the only script that mixes both registers |
| `chemistry/CHE-C3-SA-02.txt` | Part dividers are written `Tab 1` / `Tab 2` |

**Six files carry live Google Docs comment anchors** (`[a]`, `[b]` …) inside spoken
lines, with the comment bodies appended after the sign-off. These are production
TODOs ("image lagana hai", "heygen"), not narration:
`biology/BIO-C1-LA-01`, `chemistry/CHE-C10-LA-01`, `chemistry/CHE-C2-LA-01`,
`chemistry/CHE-C2-LA-03`, `chemistry/CHE-C5-LA-01`, `physics/PHY-C1-LA-01`.

## Content errors that survived review

Do not repeat these, and note that they show up on screen as well as in the voice:

- `chemistry/CHE-C4-SA-02` — puts `(n−1)¹⁻¹⁰ ns¹⁻²` on screen three times. The `d`
  is missing; it should be `(n−1)d¹⁻¹⁰ ns¹⁻²`. The error is read aloud too.
- `chemistry/CHE-C3-SA-04` — leaks the raw LaTeX artefact `EaE_a` into the text,
  and closes on 100% where the house line is 90%.
- `physics/PHY-C1-LA-02` — `dSdS` twice, from a collapsed `$dS$`, once inside a
  part bridge.
- `chemistry/CHE-C4-LA-02` — gives a neutral-medium reaction (→ MnO₂) as the
  alkaline-medium example, and misplaces the MnO₂ claim.
- `chemistry/CHE-C10-SA-07` — the closing mnemonic drops the D- prefixes that the
  correct answer needs.
- `chemistry/CHE-C2-SA-01` — teaches three salt-bridge functions for a question
  that asks for two.
- `chemistry/CHE-C4-LA-01` — attaches the KI equation to the ferrous-sulphate
  reaction and omits the Fe²⁺→Fe³⁺ equation.
- Spelling slips carried into shipped scripts: `उदारहण`, `celsious`, `तंथा`.

## Missing visuals

**15 of 111 scripts have no ON SCREEN block at all**, including difference and
process questions that clearly need one:

`biology/BIO-C12-LA-01`, `biology/BIO-C5-LA-01`, `chemistry/CHE-C1-LA-01`,
`chemistry/CHE-C1-NM-02`, `chemistry/CHE-C1-SA-01`, `chemistry/CHE-C1-SA-02`,
`chemistry/CHE-C2-LA-02`, `chemistry/CHE-C2-SA-01`, `chemistry/CHE-C2-SA-05`,
`chemistry/CHE-C3-LA-01`, `chemistry/CHE-C3-SA-04`, `chemistry/CHE-C3-SA-05`,
`chemistry/CHE-C3-SA-08`, `physics/PHY-C3-SA-01`, `physics/PHY-C3-SA-04`.

They are not simpler than the rest — they are unfinished on the visual side. Treat
a missing screen plan as a defect to fix, not a style to copy.

Figures are weaker still: only one script names a figure placeholder together with
the labels it needs. Others say "diagram को ध्यान से समझना" and supply nothing,
which leaves whoever draws it to invent the geometry.

## Formatting that no parser should trust

The corpus has no single format. Anything reading these files has to tolerate:

- **ON SCREEN markers:** at least eight spellings — `ON SCREEN:`, `ON SCREEN`,
  `On Screen:`, `On SCREEN`, `ON SCREEN-`, `ON SCREEN :`, inline `[On Screen: …]`
  inside a sentence, and `स्क्रीन पर:`. One file uses four of them.
- **Part dividers:** `PART 1`, `Part 1`, `🎬 Part 1`, `PART 1 — <subtitle>`,
  `भाग 1 — … 🎙️`, `Tab 1`, `Part 1 Ending:`.
- **`भाग N` is not `PART N`.** One chemistry script has five भाग headings but is a
  single video with one opening and one closing. Counting भाग as parts would split
  one script into five reels.
- **`शिक्षक:` is a beat separator, not a speaker change.** Some scripts tag it once
  per part, some before every paragraph, some never. One file has `Yशिक्षक:`, and
  one names the teacher instead.
- **Quote marks are unbalanced almost everywhere** — lines open with `“` and never
  close. Treat quotes as decoration; they do not mark what is spoken.
- **Tables arrive flattened** from Google Docs — one cell per line, with the next
  narration line swallowed into the last cell. Tables and Punnett squares are
  encoded three incompatible ways.
- Markdown bold survives inside spoken lines (`**0.34 nm**`), `★` prefixes teacher
  asides in some biology files, and `**` is sometimes opened and never closed.
