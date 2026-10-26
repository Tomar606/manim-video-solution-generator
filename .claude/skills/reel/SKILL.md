---
name: reel
description: Make and deliver an MP Board PYQ reel with the kit pipeline (lab/kit_test) from a dropped HeyGen clip + SRT (and any patch clip) and the question ID — splice, captions, sheet lookup, look, plan, Veo b-roll, frames review, render, gates, delivery. Use whenever someone says they dropped files for a question ID, or asks to create, build, render, fix or deliver a PYQ reel/video in any subject (PHY, CHE, BIO, HIS, GEO, POL).
---

# Making a PYQ reel

Every reel since October is built here. **Read `lab/kit_test/STANDARD.md` first**: it is what the finished
video must look like and how it is delivered, taken from the four reference videos. This file is the order of
work. The person running it is usually not technical: they drop files, review a frames sheet, and say go.
Everything else is your job, including every prompt.

Work in `projects/<slug>/`, where slug is the question ID in lower case (`his-c6-sa-04`). Commands below use
`.venv-tools/bin/python`; on Windows that is `.venv-tools\Scripts\python`.

## 0. Machine

```
.venv-tools/bin/python tools/doctor.py --flow
```

Fix whatever it lists before anything heavy.
- **Memory and disk:** this has frozen an 8 GB Mac. Ask the person to close apps, restart, or plug in.
- **The headless browser.**
- **Hindi shaping.**
- **Flow:** this repo's bridge extension must be the one loaded.

## 1. Inputs

The person drops the HeyGen video (`<ID>_1080p.mp4`) and its caption file (`<ID>-caption.srt`), sometimes a
patch clip with its own SRT, and gives the question ID.

- Link the files, never copy them (disk is tight): `projects/<slug>/src/main.mp4`, `patch.mp4`, `main.srt`,
  `patch.srt`.
- **No patch:** `part1.mp4` = the main clip, `part1.srt` = its SRT.
- **Patch:** it re-records some lines of the main take.
  1. Find which lines from the SRT text.
  2. Find the cut points in the AUDIO, because SRT times are out by up to 2.2 s. Print a loudness envelope
     (50 ms windows), cut in the pause after the last good line and in the pause before the first line that
     follows the patch, both on 25 fps frame boundaries.
  3. Grab one frame either side of each cut to check the framing matches.
  4. Concat main[0:a] + patch + main[b:] with 20–50 ms audio fades.
  5. Build `part1.srt` with the later cues shifted.
  6. Record the cut points in meta.json `_splice`. `projects/his-c6-sa-04/meta.json` is the worked example.

## 2. The question, from the sheet

```
.venv-tools/bin/python tools/sheet_fetch.py <ID>
```

This writes meta.json and pulls the in-house answer page from column AK. Then set by hand:
- **`marks`**: from the narration ("पूरे 3 नंबर"). Preflight fails without it.
- **`years`**: as spoken; the narration wins over the sheet.
- **`title`**: a short Hindi title, used for the delivery folder.
- **`hilite`**: the words the captions highlight.

It searches the whole row for the answer page (usually column AK, sometimes another column) and keeps only a
candidate that passes the answer-page checks, so the textbook scan is never taken.
- **No page found? Carry on.** It is marked pending, and the reel renders and delivers without it.
- Tell the person it is pending. When they add it to the sheet, run `tools/deliver.py --pending`.
- If they send it to you directly, run `tools/sheet_fetch.py <ID> --page <file or Drive link>`, then
  `tools/deliver.py <slug>`.
- Either way it is appended to the delivered video with no re-render.

## 3. Captions

```
.venv-tools/bin/python tools/kit_captions.py <slug>      # Whisper word clock
```

If Whisper fails (no credits), use the audio's own pauses:

```
.venv-tools/bin/python tools/lines_from_srt.py projects/<slug>/src/part1.srt projects/<slug>/lines_part1.json
.venv-tools/bin/python tools/pause_align.py projects/<slug> --write
```

Spot-check the risky joins against a loudness envelope.

## 4. Exam sheets

`tools/paper_header.py --subject <subject> --design projects/bio-c4-la-01/assets/design/question_sheet.png
--question "<question>" --year <YYYY> --out projects/<slug>/assets/papers --name sheet-<YYYY>`, once per year.

- Copy the latest year to `qsheet.png`.
- Check the Hindi shaped correctly, with no matra after its consonant.
- Measure each printed line's top and right edge (fractions of the image) for the qsheet highlight.
- The question text is baked into the PNG: editing meta.json changes nothing on screen.

## 5. The look: one theme pack, new for every video

- Pick the closest reference (STANDARD.md) and derive a theme from its CSS. Change every colour, the card band
  and the head font so it belongs to this topic's world. No two videos share a skin.
- Plates come from real photos. Find commercially licensed ones:
  `tools/fetch_photos.py <subjects.json> library/backgrounds/photos/<subject>/<topic>/`. It records
  `credits.json`, and every file must stay in it. Then crop to 1080×1920, blur about 6.5 px and darken to
  0.7–0.8 so cards read. Record the plate in `_generated.json`.
- Make 3–4 plate options and let the person choose on real frames.
- **Correctness first. Never use Veo for anything a student must reproduce:** circuits, apparatus, reactions,
  mechanisms, labelled structures, graphs, maps. Draw them exactly:
  - as an SVG/HTML element in `stage.html` (the `wheatstone`, `metrebridge`, `flask`, `cube` and `rewrite`
    elements are the examples);
  - or as a Manim render saved to `projects/<slug>/diagrams/<id>.mp4`, which a beat names like a clip.
- Get the mechanism's direction and order right, name every label as it is spoken, and use textbook colour
  conventions (red N, blue S, grey metal). Apparatus looks like real lab objects, not flat schematics.
- Veo is for atmosphere only: places, eras, people at work, the feeling of a moment.
- Political science: Indian iconography whatever the question's country.

## 6. The plan

Copy the closest `make_*_plans.py` to `lab/kit_test/make_<slug_>_plans.py`.
- Follow STANDARD.md's order:
  hook → years → question → each point (who/what, then the one thing) → recap → marks → answer page.
- Cue every element to the spoken word with `W(line, word)`.
- Give every beat footage with `BR(clip, photo)`: the Veo clip once it exists, a licensed photo until then.
- Screen text organises; it never repeats the caption.
- "No graphic" is a valid beat: presenter full, footage behind.
- New element types go in `stage.html` (and compile's asset copy and cue resolution), never as a one-off.
  `portraits` is the latest example.

## 7. Veo b-roll

1. Write one prompt per shot in `projects/<slug>/veo/prompts/broll/<id>.txt`, plus a one-line description in
   `veo/shots.json`. Copy the format of `projects/his-c6-sa-04/veo/prompts/broll/`:
   - live action, subject in the upper half, slow camera, "A tall vertical frame. Silent, no voiceover.";
   - then the NEGATIVE list.
2. Never put in a prompt:
   - digits or percentages;
   - the words logo, watermark, badge or wordmark;
   - generated people depicting the Sikh Gurus or other figures who must not be portrayed (show objects and
     places; their faces come from period paintings);
   - anything the answer contradicts.
3. Generate:

```
.venv-tools/bin/python tools/kit_veo.py setup            # Video, Veo 3.1 Fast, 9:16, x1
.venv-tools/bin/python tools/kit_veo.py submit <slug> h1 k1   # two first; fetch and look at them
.venv-tools/bin/python tools/kit_veo.py fetch <slug>
.venv-tools/bin/python tools/kit_veo.py submit <slug>         # then the rest
.venv-tools/bin/python tools/kit_veo.py fetch <slug>          # until all are filed
.venv-tools/bin/python tools/kit_veo.py clean <slug>          # removes Flow's sparkle
```

4. Check `veo/contact.jpg`: every clip should sit under its own label. Throw out and resubmit any clip with
   text, a wrong subject or a reversed process.
5. Regenerate the plan so `BR()` picks the clips up, and drop `"hook": "exempt"`.

## 8. Checkpoint 1: the frames review (nothing renders before this)

```
.venv-tools/bin/python lab/kit_test/make_<slug_>_plans.py
.venv-tools/bin/python lab/kit_test/compile.py lab/kit_test/plan_<slug_>_p1.json --stills auto
node lab/kit_test/stills.mjs out/plan_<slug_>_p1 review
.venv-tools/bin/python lab/kit_test/review_page.py <slug>
```

1. Fix every `VIOLATIONS` line first (something reaching into the presenter's box).
2. Look at every still yourself against `STANDARD.md` and the defect checklist:
   - text overlapping;
   - a photo too tall;
   - a face cropped out of a gallery window;
   - a label off its object;
   - captions under the question card;
   - the plate showing where a clip should be.
3. Then give the person `projects/<slug>/review/index.html`.
   - It opens in any browser; on Windows they double-click it.
   - It shows every frame with its time, its caption and a button that plays the narration there.
   - They write notes and press **Copy my review**, which gives you their notes, or "APPROVED".
4. Apply their notes, rebuild the page, and wait for their go.

## 9. Render and deliver

```
.venv-tools/bin/python lab/kit_test/render_reel.py <slug> --wait
```

- It keeps the machine awake.
- With `--wait`, if there is no room, it waits up to 30 min for the person to close apps.
- It renders in one lane, deleting frames as it goes, then runs `tools/deliver.py`: gates, then the answer page
  appended with a 7 s hold, then the Final folder.
- Delivery refuses on any failed gate. Fix the cause and run `tools/deliver.py <slug>` again.
- Never copy a video into a Final folder by hand.

## 10. Checkpoint 2: the final watch

Re-run `lab/kit_test/review_page.py <slug>`: the rendered video now appears at the top of the review page.
The person watches it once; check the delivered file against the defect checklist too. Then delete the
rejected samples and trial stills you made along the way.
