# Sound effects — drop files in the folder for the MOMENT, not the sound

> **Using them in a video** (cues, snapping, mixing, transitions, and the gates
> that check the result)? Read [HOW_TO_USE.md](HOW_TO_USE.md). This file is the
> contract for adding sounds to the library.

The folder name is the decision. You are not filing by what a sound *is*
("swoosh", "click"); you are filing by **when it fires on screen**. Drop a
candidate into the folder for that moment, run

    python tools/sfx_registry.py

and it is measured, checked against the rules below, and written into
`registry.json`. Nothing else needs editing.

Several candidates in one folder is fine — the newest usable one wins, and the
others stay as alternates. To retire a sound, move it to `_rejected/` and add a
line to `_rejected/REASONS.md` saying why, so nobody re-adds it in six months.

## The moments

| folder | fires when | single event? | at most |
|---|---|---|---|
| `label-lands/` | a diagram label, list card or chip ARRIVES | yes | 0.40s |
| `list-item/` | one item of a counted list fills in (1, 2, 3, 4) | yes | 0.40s |
| `step-resolves/` | a derivation step completes; the boxed final answer | yes | 1.00s |
| `card-appears/` | the question card at the head of a part | yes | 0.80s |
| `panel-arrives/` | an animation panel wipes in, or wipes away | no | 1.50s |
| `page-arrives/` | the handwritten answer page at the end | yes | 1.50s |
| `handwriting/` | texture UNDER the answer page while it appears | no | 4.00s |

"Single event" means one burst. A page *riffle* — several pages flipping — is
not one page arriving, and the ingest check will refuse it for those roles. That
is not hypothetical: `PAPER FLIP.mp3` was recommended for `page-arrives/` and
measured six separate bursts.

## What is refused, and why

These are not taste. Each one is a sound that was tried, shipped or demoed, and
sent back — so the check is mechanical now.

- **Tonal** (a musical pitch, `tonality >= 0.30`). Reads as a ringtone.
  `ding.wav` measures **0.73** — the most tonal file in the library, and it was
  rejected twice by ear before anyone measured it.
- **Rising sweep** (`sweep >= +0.35` over 0.8s or more). This is the "whistle"
  family — risers and swept synth tones. Rejected twice, explicitly.
- **Too long for its moment** — see the table. A cue that outlasts the thing it
  marks stops marking it.
- **Multiple bursts in a single-event role** — see above.

## Rules that no folder can express

- **A caption NEVER triggers a sound.** Subtitles say what was said; they are
  not events. `tools/sfx_gate.py` enforces this with a band that excludes the
  subtitle strip and the presenter.
- **No sound on the focus boxes** that appear around equations.
- **The PEAK lands on the event, not the file's start.** Effects with a build
  (the page swoosh peaks 43% in) must start early; `registry.json` carries the
  measured offset per sound and the gate compares peak time.
- **Detect the event, then place the cue. Never place by arithmetic.** Three
  pops once played over a static diagram whose labels had never appeared.
