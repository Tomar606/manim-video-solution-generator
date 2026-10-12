# script_index — what the shipped scripts are made of

An index of the 111 scripts linked from the tracking sheet, downloaded into
[`../sheet_scripts/`](../sheet_scripts/). It exists so a new script can be
assembled from moves the team has already approved, instead of invented from
scratch.

Nothing here changes any existing file or process.

## Read these first

| File | What it is |
|---|---|
| **[INDEX.md](INDEX.md)** | The browsable catalogue: 80 moves in 8 slots, each with description, shape, count and verbatim examples |
| **[RULES.md](RULES.md)** | The 12 rules a writer must follow, distilled from all 111 scripts |
| **[DEFECTS.md](DEFECTS.md)** | What NOT to copy: broken files, content errors, formatting traps |

## The data files

| File | Contents |
|---|---|
| `types.json` | The 80 moves, machine-readable: `id`, `label`, `slot`, `scripts`, `description`, `when_used`, `shape`, `examples[]` (with source file), `files[]` |
| `corpus.json` | One row per script: qid, subject, category, question type, parts, words, estimated seconds, the sequence of moves it uses, and its Google Doc link |
| `skeletons.json` | Per question type (definition, derivation, difference, process, list, numerical, reason, diagram, mixed): how many scripts, median parts and words, which moves it uses and how often, plus real example skeletons |
| `phrase_bank.json` | 53 slots of interchangeable verbatim lines — 32 ways the corpus moves to the next point, 24 memory-aid lines, 17 progress counts, and so on. Rotate within a slot so scripts don't sound identical |
| `vocabulary.json` | Word and phrase frequencies: English in Latin script, English in Devanagari, and phrase families (connectors, nudges, emphasis, gloss markers, counts, exam framing, address terms) |
| `metrics.json` | Length targets by question category, measured at 158 words per minute |
| `observations.json` | The raw, unedited notes from the four cataloguing passes |

## The eight slots

| Slot | Moves | Covers |
|---|---|---|
| `intro` | 10 | how a video opens |
| `bridge` | 4 | how parts 2, 3… open |
| `teach` | 27 | how content is actually explained |
| `hook` | 11 | attention moves inside the explanation |
| `screen` | 4 | the forms an ON SCREEN block takes |
| `handoff` | 6 | how a non-final part ends |
| `end` | 12 | the closing block |
| `tone` | 6 | register, address, English mixing |

## Length targets

| Category | Scripts | Median words | Parts | ≈ minutes |
|---|---|---|---|---|
| Long Answer (LA) | 31 | 913 | 3 | 5.8 |
| Numerical (NM) | 13 | 866 | 2 | 5.5 |
| Short Answer (SA) | 67 | 414 | 1 | 2.6 |

A shot part runs about 290 spoken words / 110 seconds, so a script is normally
longer than the clip made from it.

## The most common moves

`tone.address` and `tone.english_mixing` (111 of 111) · `end.notes_button` (103) ·
`intro.board_year_repeat` (92) · `teach.book_then_gloss` (79) ·
`hook.memory_aid` (75) · `end.keep_watching` (75) · `teach.recap_chain` (65) ·
`bridge.recap_result` (65) · `handoff.done_plus_left` (62) · `end.goal` (59)

## How it was built

1. All 111 script docs were downloaded from the tracking sheet as `.txt`.
2. A mechanical pass counted openings, closings, part transitions, phrase families
   and vocabulary across all of them.
3. Four passes each read a quarter of the corpus in full and catalogued its moves
   against one shared schema, so the results could be merged.
4. The four catalogues were merged; where they had named the same move differently
   (four names for "read the formula aloud"), the names were unified — each entry
   records what it was merged from.
5. **Every example was checked to be verbatim in its source file.** 341 of 344
   passed; the 3 that did not were dropped.

## What this does not tell you

- **Which scripts are good.** The index describes what the corpus does, and the
  corpus contains defects — see DEFECTS.md. Only 13 of the 111 are marked reviewed
  in the sheet.
- **How the scripts were edited.** These are the final docs. Their Google Docs
  version history still holds the earlier drafts, and a draft-to-final comparison
  would show what editors fix, which is the sharpest signal for checking generated
  scripts.
