# Veo character kit: setup and operating guide

This folder turns a scene plan into talking-presenter clips generated in Google
Flow (Veo), with the presenter looking like the real person and saying the
scripted Hindi line. It then downloads the clips and checks them. It is how the
all-Veo History video HIS-C2-LA-01 is being made, and it works in landscape
(16:9) and vertical (9:16).

**Written for a Claude Code instance setting this up on a new machine.** Follow
the steps in order. Every step ends with a check; do not continue past a failed
check. Commands assume the repo root as the working directory.

Read these rules before touching anything. Each one cost a failed generation or
a wasted afternoon:

1. **The Flow tab is shared with a person.** Never navigate it away from a
   `/character/` page, and never type into it while someone is using it. The
   kit refuses to leave a character page on its own; do not work around that.
2. **Never type a prompt into a clip editor** (`/project/<id>/edit/<clip>`).
   That box edits the open clip; it is not a new generation. The kit always
   returns to the project grid first.
3. **Never name a mark or text in a prompt**: no logo, watermark, badge,
   wordmark, subtitles, captions or lettering, not even as "no logo". Naming
   something is a request to draw it. `build_prompts.py` refuses such prompts.
4. **No NEGATIVE block and no "do not" / "never" / "without".** Flow has no
   negative-prompt field, so a negative list is read as a list of things to
   include. Say everything positively: "his is the only voice".
5. **No numbers in a prompt's layout or framing** (no "9:16", "30%", "1080px").
   A measurement in a generation prompt gets drawn. The aspect is set in Flow's
   settings, and the prompt says "a tall vertical frame".
6. **Spoken lines hold no digits.** Write "दो हज़ार पच्चीस", never "2025".
7. **The reference photos are never committed.** The repo is public and they
   are photographs of a real person. `.gitignore` covers
   `assets/character/**/*.png|jpg|jpeg`; keep it that way.
8. **Every clip goes through `face_gate.py` and `speech_qc.py`** before anyone
   uses it. A clip that passes its own look can still show a different man.
9. **Queue two test scenes before a whole video.** Each clip costs credits
   (about 15 on the account used in Sept 2026; check Flow's own counter).
10. **Show stills before any full render**, and wait for a go-ahead. That is a
    house rule for the whole repo (see `CLAUDE.md`).

---

## What is in the kit

```
veo_kit/
  SETUP.md            this file
  requirements.txt    pinned Python deps for the QC tools
  characters/
    ritesh.json       one presenter: refs per aspect, wardrobe, voice, how refs were made
  make_refset.py      HeyGen green-screen take -> 3 reference images, landscape AND vertical
  syllables.py        is a spoken line the right length for one clip? (33-42 syllables)
  build_prompts.py    scenes.json + lines.json -> one audited prompt per clip, per aspect
  flowkit.py          the Flow-driving helpers the two tools below share
  submit.py           queue prompts in Flow with the 3 references attached
  fetch.py            download finished clips, identify each by its spoken line
  face_gate.py        is it him? face-embedding similarity, median >= 0.90
  speech_qc.py        did he say the line? Whisper vs the script
  example/his-c2-la-01/
    SCENES.md         the scene plan (the thinking)
    scenes.json       the scene table the prompts are built from
    lines.json        the 17 spoken lines, all 33-42 syllables
    prompts/landscape, prompts/vertical   what build_prompts.py writes

outside the kit, used by it:
  flow/extension/     the Chrome extension ("PYQ Flow Bridge", build 14)
  flow/selectors.json every Flow UI selector in one file
  src/flow_bridge.py  the Python half of the bridge (stdlib only), port 8765
  tools/flow_probe.py free step-by-step check of the bridge
  assets/character/   reference photos (NOT in git) + ritesh.md (his looks, measured)
  docs/veo-prompt-research.md   why the prompts look the way they do, with sources
```

---

## Step 1: System prerequisites

- macOS (the kit was built and run on macOS 26). Linux should work; it is
  untested.
- **Google Chrome.** Brave works but needs a policy change first; see
  Troubleshooting.
- **Python 3.11.** 3.10 and 3.12 also work. 3.13 has no torch 2.2 wheels.
- **ffmpeg and ffprobe**: `brew install ffmpeg`.
- A Google account with **Google Flow** access and credits. Open
  <https://flow.google.com>, create or open the project the team uses, and
  sign in to the account that owns the credits.

**Check:** `python3.11 --version && ffmpeg -version | head -1` prints both.

## Step 2: Python environment

The kit runs in its own venv. It must not share one with Manim: Manim 0.18 pins
an old numpy, and whichever is installed second breaks the other.

```bash
python3.11 -m venv .venv-tools
.venv-tools/bin/pip install -r veo_kit/requirements.txt
```

If `.venv-tools` already exists from the PYQ track, install into it anyway; the
pins are compatible with `requirements-tools.txt`.

The first run of each QC tool downloads model weights: about 110 MB for the
face model (VGGFace2) and about 460 MB for Whisper `small`. That is normal.

**Check:**

```bash
.venv-tools/bin/python -c "import facenet_pytorch, whisper, torch; print('ok', torch.__version__)"
```

prints `ok 2.2.2`.

## Step 3: The reference images

The kit needs, for each presenter:

| file | what |
|---|---|
| `assets/character/ritesh_reference.jpeg` | the face photo `face_gate` compares every clip against |
| `assets/character/refset/ritesh_ref_{1_front_face,2_turned,3_waist_up}.png` | landscape set, 1920x1080 |
| `assets/character/refset_vertical/ritesh_vref_{1_front_face,2_turned,3_waist_up}.png` | vertical set, 1080x1920 |

They are **not in git**. There are two ways to get them.

**A. From the team.** Ask for the reference-image zip and unpack it at the repo
root so the paths above exist.

**B. Rebuild them from a HeyGen take.** Any green-screen HeyGen clip of him
works. The set in use was made from `inbox/che-c3-sa-10/heygen_full.mp4`, and
`characters/ritesh.json` records exactly how (the `source` block):

```bash
.venv-tools/bin/python veo_kit/make_refset.py --character veo_kit/characters/ritesh.json
```

For a different clip, first change `source.clip` and pick three times: face
square-on with the mouth nearly closed, head turned about 30 degrees, and a
waist-up frame. Then run with `--zoom` to get a gridded close-up of each shot's
chest (`_chest_<shot>.png` next to the refs). Read the rectangles of the
embroidered badge and wordmark off the grid, in source pixels, into each shot's
`paint` list, and rebuild. A reference that carries lettering asks for
lettering.

What the builder does, and why:

- It keys him off the green onto flat mid-grey. Google's guidance is subject
  references on a plain background.
- It crops to the aspect of the generation: 1920x1080 for landscape, 1080x1920
  for vertical. A reference in the other shape pulls the framing towards
  itself.
- It paints out the shirt's wordmark and badge using the cloth's own shading
  and grain, and never paints over skin.
- It gives the two sets **different filenames**. Flow attaches uploads by name,
  so two sets with the same names in one project would be a coin flip.

**Check:** open `assets/character/refset/_sheet.png` and
`assets/character/refset_vertical/_sheet.png`. You should see three views of
him on grey, with no lettering or badge on the shirt. Then score each image
against the face photo:

```bash
.venv-tools/bin/python - <<'PY'
import sys; sys.path.insert(0, "veo_kit")
import numpy as np, json
from PIL import Image
from face_gate import embed
ch = json.load(open("veo_kit/characters/ritesh.json"))
ref = embed(Image.open(ch["face_reference"]))
for aspect, files in ch["refs"].items():
    for f in files:
        print(aspect, f.rsplit("/", 1)[-1], round(float(np.dot(ref, embed(Image.open(f)))), 3))
PY
```

Every image should score **0.93 or more**. The current sets score 0.933–0.952.

## Step 4: Install the Chrome extension

1. Open `chrome://extensions` and turn on **Developer mode** (top right).
2. Click **Load unpacked** and choose this repo's `flow/extension/` folder.
3. The card must read **PYQ Flow Bridge 0.2.0**.
4. **Disable any other Flow bridge.** Another project (flow-animator) ships an
   extension that speaks the same protocol on the same port, 8765. It drives
   Flow and looks like it is working, but none of this repo's fixes are in it.
   `src/flow_bridge.py` refuses to run against it, and against any build other
   than 14, with a message naming what to reload.
5. Open the Flow project in **one** tab. It can stay in the background. Pin the
   tab, so Chrome's memory saver does not discard it.

After any change under `flow/extension/`, click reload on the extension card,
**then** hard-reload the Flow tab. There is no hot reload, and a stale build
fails like a Flow redesign.

**Check:** the free probe climbs a ladder and names the rung that fails:

```bash
.venv-tools/bin/python tools/flow_probe.py
```

Each rung should report ok: connect, page, prompt box, submit button, media
list, reference input. Nothing is submitted. If the prompt box or a button is
not found, Flow has changed its UI; fix the selector in `flow/selectors.json`,
where the comments explain how.

## Step 5: Flow settings (done by hand in Flow, not by the kit)

- **Aspect ratio.** Open the settings control on the prompt bar (the tune icon)
  and choose landscape or vertical. **The bridge cannot change this.**
  `submit.py` warns when it cannot read the setting, and `fetch.py` flags any
  clip that arrives in the wrong shape.
- Leave the output count at 1 per prompt, so that one prompt makes one clip.
- The project grid has **Characters** too. The team's project has a Flow
  Character called "Ritesh Sir". The kit skips character cards when
  downloading. It generates from the three uploaded references, which is the
  verified route; generating from the Character with `@` is untested.

## Step 6: A dry run (costs nothing)

```bash
.venv-tools/bin/python veo_kit/build_prompts.py veo_kit/example/his-c2-la-01 --aspect landscape
.venv-tools/bin/python veo_kit/submit.py veo_kit/example/his-c2-la-01/prompts/landscape/s02.txt \
    --aspect landscape --check
```

`--check` goes back to the grid, clears old reference chips, uploads the three
references if Flow does not have them yet, attaches them, and types the prompt.
It stops before pressing generate.

**Check:** the output ends with `3 reference chip(s) on the prompt bar`,
`typed N of N characters` and `checked — NOT submitted`. Look at the Flow tab:
three thumbnails on the prompt bar and the prompt in the box. Clear the box by
hand, or leave it; the next submission replaces both.

---

## Making a video

### 1. Plan the scenes

Write the scene plan first. `example/his-c2-la-01/SCENES.md` is the model:

- **One scene is one clip is one spoken line.** A clip is about 8–10 seconds.
- **He is in the scene, doing something.** Not standing in front of a
  backdrop: he cuts rice with the farmers, works the forge bellows, poles the
  boat. His hands have something to do while he speaks. Stiff clips read as a
  stranger even when the face is close.
- **The black polo stays on in every shot.** He is our teacher walking into
  the scene. One accessory that belongs to the place is allowed, the same one
  through the video (here a cream cotton cloth over one shoulder).
- **No text is ever generated.** Labels (Devanagari especially) are composited
  afterwards. Veo renders Hindi letters as broken glyphs.

### 2. Write and size the lines

`lines.json` maps scene number to the spoken line: `{"1": "...", "2": "..."}`.

```bash
.venv-tools/bin/python veo_kit/syllables.py --file path/to/lines.json
```

Every line must be **33–42 syllables**, which is about 6.5 seconds at his
measured pace (5.79 syllables a second, from 300 lines of his real videos).
Budget by syllables, not words: है is one syllable and महत्वाकांक्षी is six.

- **Too short** leaves dead air, and Veo fills dead air with invented speech.
  That is exactly the gibberish the first HIS-C2-LA-01 clips had.
- **Too long** and he rushes, or the line is cut off.

Keep the register casual and spoken, the way he talks to a class-12 student.
Numbers go in words.

### 3. Fill the scene table

`scenes.json` has one entry per scene; see `example/his-c2-la-01/scenes.json`:

| field | what goes in it |
|---|---|
| `camera` | one sentence, e.g. "Medium shot at eye level, the camera holding still." |
| `accessory` | `true` to add the video-wide accessory for this scene |
| `setting` | where he is, written as a clause after his wardrobe: "stands waist-deep in a field of ripe golden rice at low sun, a short hand sickle in his right hand" |
| `before` | what he does before speaking: "He gathers a handful of stalks, cuts them, straightens and lifts the sheaf, then looks into the camera" |
| `after` | what he does after: "He finishes, closes his mouth and nods once" |
| `others` | other people, said positively; empty if he is alone |
| `sound` | the ambient sound, one sentence |

`before` and `after` are **never empty**. They are what fills the rest of the
clip once the line is said.

### 4. Build and audit the prompts

```bash
.venv-tools/bin/python veo_kit/build_prompts.py projects/<slug>/veo --aspect landscape
.venv-tools/bin/python veo_kit/build_prompts.py projects/<slug>/veo --aspect vertical
```

This writes `prompts/<aspect>/sNN.txt` and `prompts.json`. The template follows
Google's order (camera, subject, action, context, style) and runs 100–150
words. It calls him only "the man from the reference images" plus his wardrobe:
**the pictures carry his face**, and describing the face again competes with
them.

The audit fails a prompt that names a mark or text, contains a negation, holds
a measurement, describes his face, is outside 80–170 words, or carries a line
outside 33–42 syllables. **Fix the scene or the line and rebuild; do not
submit a failing prompt.**

**Vertical differences** (the builder handles these):

- It ends on "a tall vertical frame, with him centred, his head near the top
  and his hands in view in front of his chest". The ratio is never written.
- Lateral tracking shots become "framed tall". Prefer scenes where he moves
  towards or away from the camera. Wide scenery is what a tall frame loses.
- It attaches the vertical reference set.

### 5. Generate: two scenes first

Set the aspect in Flow (Step 5), then:

```bash
.venv-tools/bin/python veo_kit/submit.py projects/<slug>/veo/prompts/landscape/s01.txt \
    projects/<slug>/veo/prompts/landscape/s04.txt --aspect landscape
```

For each prompt it: returns to the grid; clears stale chips; uploads any
missing references (once); attaches the three references **in order** (face,
turned, build; earlier references weigh more); **verifies exactly three
chips**; types the prompt and **reads it back**; presses generate; and confirms
Flow started (a progress percentage) or queued it. Flow often queues under load
("waiting in the queue due to high demand"); a clip can take several minutes.

Only after both test clips pass QC (below) should you queue the remaining
scenes.

### 6. Download

```bash
.venv-tools/bin/python veo_kit/fetch.py --prompts projects/<slug>/veo/prompts/landscape \
    --out projects/<slug>/veo/clips --aspect landscape
```

Add `--expect N` to wait until N clips exist, or `--list` to identify without
downloading. It presses Flow's own Download button, takes **720p Original
size** (the real generation; the other sizes are upscales of it), and moves the
file from `~/Downloads` (or `$FLOW_DOWNLOAD_DIR`) to `<out>/sNN.mp4`. Clips
already on disk are skipped. Beside each clip it writes **`sNN.sent.txt`: the
prompt Flow actually generated from.** See the next section for why that
differs from yours.

It identifies each clip by **the spoken line**, which is unique per scene and
survives Flow's rewrite. Tiles that match nothing (older clips, other videos)
are skipped.

**Check:** each line of output shows the file, `1280x720` (or `720x1280` for
vertical) and about `10.01s`, with no `**` warning.

### Flow's agent rewrites your prompt

The prompt box on Flow's project grid feeds **Flow's agent**, which rewrites
the prompt before the video model sees it. On the HIS-C2-LA-01 test clips it:

- paraphrased the English ("the camera holding still" became "static camera");
- added "Lip sync is perfect with the Hindi dialogue";
- **kept the quoted Hindi line verbatim**, both times;
- on an earlier round with old-style prompts, **added its own "Negative:
  subtitles, captions, on-screen text, watermark, logo" block**, which is
  exactly what our rules keep out.

We have not found a way to turn the rewrite off. So `fetch.py` saves the
rewrite, prints `! Flow's agent added a NEGATIVE block` when it happens, and
prints `! the spoken line did not survive` if the line was changed. When either
appears, look hard at that clip: text drawn somewhere, or the wrong words.

### 7. QC every clip

**Is it him?**

```bash
.venv-tools/bin/python veo_kit/face_gate.py projects/<slug>/veo/clips/s01.mp4 --at 1 2.5 4 5.5 7 8.5 9.5
```

It finds the face in each sampled frame, embeds it (VGGFace2), and scores
cosine similarity against `ritesh_reference.jpeg`. **It passes when the median
is 0.90 or more.** The threshold is calibrated: his real frames score around a
0.94 median, and generated look-alikes around 0.86. Faces under 120 px or with
detection confidence below 0.95 are skipped, and it needs at least 3 usable
frames. In a wide shot his face is small at 720p, so sample more frames, or
make the scene closer.

**Did he say the line?**

```bash
.venv-tools/bin/python veo_kit/speech_qc.py projects/<slug>/veo/clips/s01.mp4 \
    --line-file projects/<slug>/veo/lines.json --n 1
```

Whisper (`small`, Hindi) transcribes the clip. The line and the transcript are
compared as one consonant string: vowels, spaces and aspiration are dropped,
and Whisper's digits are spelled out as Hindi words. Whisper writes Hindi
loosely ("2025" for "दो हज़ार पच्चीस", "पुचा" for "पूछा", "आसकता" for
"आ सकता"), and comparing word by word failed clips that said their line
perfectly. **It passes at 75% or more of the line heard, in order, with at
most 25% extra**, and the last word must not end on the final frame. More than
3 seconds of silence after the line is printed as a note: listen for filler.

**Look at it.** Pull stills across the clip
(`ffmpeg -ss <t> -i clip.mp4 -frames:v 1 f.png`) and check for:

- lettering or a badge on the shirt;
- any drawn text;
- a second speaking person;
- the right accessory;
- hands and props that make sense.

Also look for things that look like **player controls**. s01 carried a static
rounded tab with a "<" arrow at its right edge (around x 1266–1280, y 572–616
on 1280x720) for the whole clip: an invented UI element, not Flow's marker.
Crop or cover it at edit time, or regenerate.

Flow burns a small **four-pointed sparkle AI marker** into every clip, after
generation, so no prompt prevents it. (Do not mention it in a prompt either;
see rule 3.) On the 1280x720 clips it sits centred at about (1160, 600), about
48 px across. Measure it per clip, because it has moved between projects.
Covering it:

```bash
ffmpeg -i s01.mp4 -vf "delogo=x=1132:y=572:w=56:h=56" -c:a copy s01_clean.mp4
```

That is invisible on a plain background, like the teal wall. On busy texture,
like the rice field, it leaves a soft patch. There, put a composited label over
it, or crop and scale the frame slightly at edit time. For vertical clips,
locate the marker by eye before covering it.

**Decide:**

| result | action |
|---|---|
| face ≥ 0.90, speech OK, looks right | keep |
| face < 0.90 | regenerate. If it is a wide shot, move the camera closer first |
| speech coverage low, or extra speech | listen. If the words are wrong, check `sNN.sent.txt` and the line's syllable count, then regenerate |
| wrong aspect | fix Flow's setting (Step 5), regenerate |
| agent added a NEGATIVE block | inspect frames for text; regenerate if any |

Delete rejected clips once they are superseded. Do not keep piles of failed
takes.

### 8. The voice

Veo keeps no voice between generations, so each clip's voice differs slightly.
The plan is to run the finished audio through **ElevenLabs voice changer** with
his cloned voice (cloned from the hours of HeyGen takes). The voice changer
keeps the words and the timing and replaces the voice, so the lip-sync stays
right. That is why the **words must be right in the Veo clip itself**, and why
`speech_qc` exists.

---

## Results so far (22 Sept 2026)

| | verified? |
|---|---|
| landscape references built, logo removed, score 0.933–0.945 | yes |
| vertical references built, logo removed, score 0.940–0.952 | yes (scored), but **no vertical clip generated yet** |
| submit with 3 references, landscape | yes: s01 and s04 generated; `--check` run on the current Flow build |
| fetch, identifying by spoken line | yes: s01 and s04 downloaded, 1280x720, 10.01 s |
| speech: s01 93% / s04 97% of the line, no filler | yes: **the gibberish is fixed** |
| face: s01 0.935 pass, s04 0.887 fail (wide rice-field shot) | yes |
| reading Flow's aspect setting from the page | not yet: it returned "unknown" on this build, so it warns |
| generating from the Flow Character (`@Ritesh Sir`) | untested |

The first vertical run should be treated like the first landscape run: two
test scenes, fetch, face gate, speech QC, and a look at the frames before
queueing more.

---

## Troubleshooting

| symptom | cause and fix |
|---|---|
| `StaleExtension ... is 'X' ... not 'PYQ Flow Bridge'` | another project's bridge is loaded on port 8765. Disable it; load `flow/extension` from this repo |
| `StaleExtension ... build N but this code expects 14` | the loaded copy is old. Reload the extension card, then hard-reload the Flow tab |
| `no Google Flow tab is open` | open the Flow project in Chrome; any tab, can be in the background |
| `the Flow tab is not inside a project` | open the project itself, not Flow's home page |
| hangs at connect, nothing logged (Brave) | Brave's Local Network Access silently blocks the extension from reaching 127.0.0.1. Allowlist it by policy; see `flow/README.md`, section "Brave" |
| it worked, then the repo was moved or renamed | an unpacked extension's ID comes from its folder path. Reload it from the new path (and update any Brave policy) |
| `the tab has been DISCARDED` (flow_probe) | Chrome's memory saver unloaded the tab. Pin it, or keep it in the foreground |
| `stopped: the Flow tab is on a character page` | someone is editing a Flow Character in that tab. Wait until they finish, or ask. Never force it |
| `prompt box not found` / `click target not found` | Flow changed its UI. Run `tools/flow_probe.py`; the failing rung names the selector to fix in `flow/selectors.json` |
| `expected 3 chips, found N` | leftover chips that would not clear, or an attach that did not take. Look at the prompt bar, remove extras by hand, run again |
| `X is not listed in Flow's Uploads` | the upload did not land. Open the + (Add ingredients) panel once by hand, then run again |
| `the prompt did not land in the box` | the tab was mid-load, or on a clip editor. Run again. If it repeats, check the `prompt` selector |
| `Flow refused the generation: ... out of credits` | the account is out of credits. "Running low" is only a warning and does not stop the kit |
| fetch: every tile `unknown` | Flow may have changed the tile alt text ("Generated video thumbnail") or the clip page layout. See `TILES_FN` and `identify()` in `fetch.py` |
| clip arrives in the wrong shape | Flow's aspect setting. Change it by hand, then regenerate |
| clip is fine but he mouths nonsense after the line | the line is too short for the clip (under 33 syllables), or `after` gives him nothing to do |
| a different-looking man | face gate fails. Check that the 3 chips were attached, then regenerate. Wide shots score lower: move closer |
| the on-page status panel does not appear | cosmetic. The panel's content script matches `flow.google/*`; the bridge itself drives the tab over the debugger and works regardless |

---

## Adding another presenter

1. Copy `characters/ritesh.json` to `characters/<name>.json`. Change `name`,
   `face_reference`, `refs` (keep the vertical filenames different from the
   landscape ones), `wardrobe`, `voice` and `source`.
2. Build and check the references (Step 3).
3. Calibrate the face gate before trusting 0.90 for someone new. Score frames
   of the real person and frames of generated look-alikes, and put the
   threshold in the gap between them (`face_min` in the json).
4. Pass `--character veo_kit/characters/<name>.json` to `build_prompts.py`,
   `submit.py` and `face_gate.py`.

## Where the reasoning lives

- `docs/veo-prompt-research.md`: the research behind the prompt shape, the
  reference set, the syllable budget and the voice plan, with each claim
  tagged Google, field report, or measured by us.
- `assets/character/ritesh.md`: his looks and behaviour, measured, and what
  went wrong in HIS-C2-SA-06 (three different men in one video).
- `flow/README.md`: how the bridge works, and why it is shaped the way it is.
- `CLAUDE.md`: house rules for the whole repo.
