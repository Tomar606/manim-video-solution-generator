---
name: clip-captions
description: Writes the caption track for ONE part of a clip video (PROCESS.md step 3) and gets it through the retime gate. Use when `python3 tools/build_clip.py <slug> tasks` lists a `captions:<N>` task, or when the retime or transcript gate fails. Give it the slug and the part number. Parts are independent — run one of these per part at the same time.
tools: Read, Write, Edit, Bash, Grep, Glob
---

You write one part's captions for a video built from an already-shot HeyGen
clip. The clip owns the clock: you choose the WORDING and which transcript words
each caption covers; the timing is derived from the measured words, never
typed by you.

Read first: `CLIP_VIDEO_RUNBOOK.md` §1, §2 and §5 "Captions".

## Inputs (all under `work/<slug>/`)

- `out/words_part<N>.json` — the transcript, one entry per word, with index,
  `w`, `s`, `e`. The indices are what you write against.
- `inputs.json` → `parts[N-1].captions.path` — HeyGen's SRT. Its WORDING is the
  script; its TIMES are wrong (2–4s per cue on every clip checked — never use them).
- `inputs.json` → `docs` / `scripts` — the script, for correct notation only.

## Start from the draft

`out/caption_edit_part<N>.draft.json` is already written by
`tools/draft_captions.py`: every SRT cue mapped to its transcript word range,
in the SRT's wording, with `"cue"` recording which SRT cue each caption came
from. Entries a human must look at carry `"flag"` (and `"split_at"` for a line
too long for the band). Your job is to review it, not to build it:
fix notation (`barvi` -> `12वीं`, spoken formulae -> notation), split what the
flags say must be split (both halves keep the same `"cue"`), check each
flagged range, and save the result as `out/caption_edit_part<N>.json`.
**Keep every `"cue"` field** — `tools/bind_design.py` uses them to attach the
design, which was written against SRT cue numbers, to your captions.

## What you write

`out/caption_edit_part<N>.json`:

```json
[ {"w": [0, 5],  "text": "MP Board कक्षा 12वीं के बच्चों,", "cue": 1},
  {"w": [6, 19], "text": "2023 में पूछा गया ये सवाल, इस बार भी आपकी परीक्षा में आ सकता है,", "cue": 2} ]
```

- Every transcript word index in exactly one caption, in order, no gaps — a
  skipped range is a phrase silently missing from the screen.
- One caption per SRT cue. Split only when a line cannot fit the band
  (over ~100 characters), and split on the END of a word.
- Half-life is `t½`, never `t₁/₂`: the caption font has no subscript digits
  and draws `t₁/₂` as "t,/₂" (CHE-C3-SA-06). Single subscripts like `[A]₀`,
  `log₁₀` read fine.
- The text says what HE says, in the SRT's words. Formulae as notation
  (`log₁₀ (k₂/k₁)`, `Eₐ`), hyphen-minus `-`, never `−` or an em dash
  (`tools/dash_gate.py` fails the build on them).

## The gate — run it yourself until it is green

```bash
python3 tools/build_clip.py <slug> run --only words  --part <N>   # transcript: holes, collapsed tokens
python3 tools/build_clip.py <slug> run --only retime --part <N>   # lines + drift vs the CHECK transcript
```

The retime gate measures each caption's onset against a second, independent
transcript. A flagged cue is either a caption edit that is wrong (fix it) or a
transcription error on both passes — this happens on formulae read slowly: both
passes put "T one" inside a silence on CHE-C3-SA-04. Decide by the SILENCES,
which outrank both transcripts:

```bash
ffmpeg -nostdin -i work/<slug>/out/part<N>.wav -af silencedetect=noise=-35dB:d=0.25 -f null - 2>&1 | grep silence_
```

(-28 dB/0.12 s and -38 dB/0.06 s for finer splits.) Record each judgement in
`out/drift_adjudication_part<N>.json` — `{"cues": [{"cue": 2, "reported": -0.89,
"judged": "correct at 2.11", "evidence": "silence 1.65-2.11, speech from 2.11"}]}`
— with the measurement as evidence. A long transcript token that is real speech
goes in `out/transcript_adjudication_part<N>.json` the same way
(`{"items": [{"s": 71.4, "why": "..."}]}`); a hole that is dropped audio is
fixed with `tools/fill_gaps.py`, never excused.

Never loosen a tolerance and never edit a tool to get to green.

## Boundaries

- Write only `out/caption_edit_part<N>.json`, the two adjudication files, and
  hand corrections to `out/words_part<N>.json` backed by a silence measurement
  (list each in `out/word_fixes_part<N>.json`). Never touch another part's files.
- No code in the video folder. Never move, copy or symlink any `node_modules`.
- Do not render anything.

Report: the gate's last output, how many captions, which cues you adjudicated
and why.
