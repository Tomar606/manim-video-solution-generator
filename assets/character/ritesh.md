# Ritesh sir — the Arivihan presenter

Reference: `assets/character/ritesh_reference.jpeg` (1080x1920, from the HeyGen
shoot). Every measurement below is taken off that frame.

This file exists so a generated clip can be checked against something fixed. A
character described freshly each time drifts, and drift is exactly what went
wrong in HIS-C2-SA-06 — see "What went wrong already", at the bottom.

## Measured

| | |
|---|---|
| polo | `#1F2839` — near-black with a blue cast, NOT pure black |
| skin, lit forehead | `#DFB2AA` |
| skin, cheek in shadow | `#AC7B73` |
| hair and beard | `#242A34` / `#202833` — near-black, faintly cool |
| shoot backdrop | `#BAAF9D` warm taupe (replaced at composite; not part of him) |
| head top in frame | 16.7% down a 1080x1920 portrait frame |

## Looks

An Indian man in his early-to-mid thirties, medium-heavy build with broad
shoulders and a full chest — solid rather than athletic, and he reads as
somebody's favourite teacher rather than a model.

**Face.** Broad and full, rounded jaw, full cheeks. Warm medium-brown skin,
slightly ruddier across the cheeks, a little natural shine on the forehead under
key light. Faint shadow under the eyes.

**Beard.** The single most identifying feature. A FULL black beard, dense and
naturally thick — not sculpted, not faded, not a stubble. It covers the whole
jawline and rides high onto the cheeks, ending in a soft natural line about
halfway up the cheek rather than a sharp shaved edge. It is deep enough under
the chin to round the jaw off. The moustache is full, joined to the beard at
both corners, and covers the top edge of the upper lip.

**Hair.** Thick and black, worn swept back and a little to his left with real
volume at the front — a soft quiff, not gelled flat and not spiked. Shorter at
the temples. The hairline is beginning to recede at the two upper corners of the
forehead, which widens the forehead slightly; that recession is part of the
likeness and a generated version without it looks like a younger stranger.

**Eyes and brows.** Dark brown eyes, medium-set. Thick dark brows, almost
straight with a slight arch, sitting close over the eyes.

**Nose.** Straight, medium-broad, rounded tip.

**Clothing.** A plain black short-sleeve polo, soft matte cotton, worn loose.
Two-button placket, buttons fastened. Short sleeves ending mid-bicep.

## Behaviour

He TALKS WITH HIS HANDS, continuously and in the frame. Across the videos built
so far his hands are almost never at rest: index finger raised to make a point,
open palms turned up, both hands coming together in front of the chest, fingers
counting off items. The reference frame catches him mid-gesture with the right
index finger up and the left hand loosely closed at waist height — that is his
resting-busy state, not a pose.

He faces the camera square-on and speaks straight down the lens. Head and
shoulders move with the speech; he leans in slightly on an emphasis. Eyebrows
lift when he asks a question. The expression is warm and direct — engaged,
encouraging, a touch emphatic. Never stern, never theatrical.

Energy is steady and conversational, the register of a teacher who has decided
you will understand this. He does not pace or wander; he holds his ground and
works with his upper body.

## Writing him into a Veo prompt

**Superseded on 22 Sept 2026.** This section used to hold a locked text
description of his face, to be pasted into every prompt. The research in
`docs/veo-prompt-research.md` showed that was the wrong way round: with
reference images attached, the PICTURES carry the likeness, and a paragraph
re-describing the face competes with them (and is how the beard shortens).

What to do now is in `veo_kit/SETUP.md`:

- attach the THREE-image reference set (`veo_kit/characters/ritesh.json`),
  face first, in the aspect of the generation;
- call him only "the man from the reference images", plus the wardrobe line;
- give him something to DO before and after his line;
- no NEGATIVE block and no "do not", because Flow has no negative field.

The looks and behaviour above are still the checklist for judging a clip by
eye, and good material for a Flow Character's "Character info" text.

## What went wrong already

HIS-C2-SA-06 shipped with three different men in it. The composited HeyGen
presenter (~60s, over the map) is the real one. The two generated clips are not:

- **~8s, by the pillar** — narrower face, short trimmed beard, slighter build.
  A different person who happens to be bearded.
- **~30s, in the colonnade** — fuller beard but a different face again, and a
  different build from both.

Neither carries the receding hairline, the beard's height on the cheek, or the
heavy build. Nothing caught it: the clips passed their own reviews, because each
was graded against its own prompt rather than against him.

## The prompt to paste with the image

Replaced by the template in `veo_kit/build_prompts.py`. The old block (a
paragraph locking his face, a "Do not" list and a NEGATIVE list) is what
produced the gibberish clips: it said "silent", left seconds of dead air, and
Flow read its NEGATIVE list as things to include. Flow's own agent also rewrites
whatever is typed; see "Flow's agent rewrites your prompt" in `veo_kit/SETUP.md`.

## Checking it afterwards

    python veo_kit/face_gate.py <clip.mp4> --at 1 2.5 4 5.5 7 8.5 9.5

Measured, not judged: MTCNN finds the face, InceptionResnetV1 (VGGFace2) embeds
it, and the score is cosine similarity to `ritesh_reference.jpeg`. Calibrated on
HIS-C2-SA-06: his own frames score a median 0.94, the two generated strangers
0.86. **The decision is the MEDIAN over frames, at 0.90**, because one impostor
frame reached 0.901 and one genuine frame of him mid-word fell to 0.72.

First v2 results (22 Sept): the teal-wall clip scored 0.935 (pass); the rice
field scored 0.887 (fail), a wide shot where his face is about 110 px tall at
720p and the beard reads a little shorter than his.

`face_gate` also runs inside `tools/gates.py`, so no PYQ video ships without it.
