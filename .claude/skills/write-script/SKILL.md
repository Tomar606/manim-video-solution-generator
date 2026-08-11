---
name: write-script
description: Write or revise a video script in this repo's format — beats, spoken lines, equations, director notes, photos and the answer card. Use when someone asks to write, rewrite, shorten, translate or fix a script, or when a script fails to parse.
---

# Writing a script

A script is a markdown file with YAML frontmatter and `[speaker]`-tagged beats.
It is the single source of truth: narration, timing, animation direction, photos
and the answer card all come from it.

```markdown
---
title: Deriving the Quadratic Formula
orientation: landscape          # landscape | portrait
theme: midnight
chroma: right_half              # region reserved for the presenter
avatar:
  placement: auto               # follow the chroma zone
  timing: audio                 # narration is the clock
answer_image: assets/answer.png # optional closing answer card
answer_narration: Toh yeh raha final answer.
speakers:
  narrator: { voice: George }
---

[narrator]
Hum general quadratic equation se shuru karte hain.
%% Fade the equation in centred; keep it large.
$$ a x^2 + b x + c = 0 $$

[narrator]
Dono sides ko a se divide karte hain.
%% Transform the previous equation; highlight the a in each term.
$$ x^2 + \frac{b}{a} x + \frac{c}{a} = 0 $$

[narrator]
Yeh raha apparatus jo experiment mein use hota hai.
![Millikan apparatus](assets/apparatus.png){full,kenburns}
```

## Rules that actually matter

**The spoken line is fed to text-to-speech verbatim.** No LaTeX, no symbols, no
markdown, no "as shown below". Write "b squared minus four a c", not `$b^2-4ac$`.
This is the single most common way a script goes wrong: it reads fine and sounds
broken.

**One idea per beat.** 8–30 words. The beat is also the animation's unit of
work — two ideas in one beat produce a cluttered scene.

**Introduce before you use.** Never reference a quantity the narration hasn't
named yet; the animation follows the same order.

**Director notes are visual instructions**, not restatements of the narration.
"Highlight the discriminant in amber, then fade the rest" is useful. "Show the
equation" is not.

**Photos must exist.** `![caption](assets/x.png)` resolves against the script's
folder and the project's `assets/`. A beat with a photo and no equation renders
from a fixed template, so it looks identical in every video.

**Language.** Our narration is usually Hinglish — conversational Hindi in Latin
script, English kept for technical terms ("Ab dono sides ko integrate karenge").
Never Devanagari; the TTS voice expects Latin script.

## Chroma and the presenter

If `chroma:` reserves a region, Manim paints it flat green and keeps all content
out of it, and the presenter is later keyed into exactly that box. So when a
script reserves `right_half`, write director notes for the left half only.

## The voice comes from `style/`

Don't invent a house style. `style/samples/` holds scripts the team has approved
and `style/variations.yaml` holds the approved phrasings for recurring moments
(opener, transition, emphasis, answer, closing). The writer matches those samples
and picks a different variation each time a moment recurs.

Read them before writing anything by hand — `video style` lists what's loaded.
When a slot has approved lines, use one rather than inventing a new phrasing.

## Score it — don't eyeball it

```bash
video eval <slug>            # mechanical checks, free and instant
video eval <slug> --judge    # + a model's read against the samples
```

The checks catch what makes narration sound synthetic: digits or symbols the
voice can't say, repeated sentence openers, uniform line lengths, written-register
connectives, references to things the listener can't see. Exit code 3 means
failures. `video script` runs this automatically and redrafts until it's clean.

Two rules that catch most problems before the evaluator does:
- **Numbers are words.** "paanch kilogram", never "5 kg". "pandrah bataa paanch",
  never "15/5".
- **Every beat opens differently.** If three beats start "Ab hum…", the script
  reads as machine-written no matter how good the content is.

## Checking your work

Parse it before rendering — this catches format errors in a second instead of
twenty minutes in:

```bash
python -c "from src.script_parser import parse_script_file as p; \
s = p('projects/<slug>/script.md'); \
print(len(s.segments), 'beats'); \
[print(i, repr(x.narration[:60])) for i, x in enumerate(s.segments)]"
```

Then `./bin/video narrate <slug>` to hear the timing, and only then render.
