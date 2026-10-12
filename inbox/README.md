# inbox — the one place to drop things

Everything a video is built FROM lands here, in **one folder per question**,
named by its **QID**. Nothing else. No other folder in this repo is a drop
point; if material is anywhere else, it is lost.

```
inbox/BIO-C5-LA-01/          <- the QID, uppercase. This is the whole convention.
    part1.mp4                the presenter clip                  REQUIRED
    part1.srt                captions from HeyGen                optional
    part1_audio.mp3          audio, if it came separately        optional
    part2.mp4
    part2.srt
    script.pdf               the teaching script                 optional
    question.txt             question text, year, marks          optional
    answer.png               scan of the written answer          optional
```

Then, always, before anything else:

```bash
python tools/ingest.py BIO-C5-LA-01
```

That reads the folder, measures every file with `ffprobe`, checks the pieces
against each other, and writes `work/<slug>/inputs.json`. **Every later stage
reads that manifest.** Nothing downstream should ever glob `inbox/` itself.

`python tools/ingest.py --survey` shows every drop folder and whether it reads
cleanly.

---

## The naming rules, and why each one exists

**One folder per QID, uppercase.** BIO-C5-LA-01 arrived as two sub-folders using
two different conventions (`BIO-C5-LA-01_part1` and `BIO-C5-LA-01-part-2`), and
the build log records that the folder names "were not trusted" — the parts had
to be identified by transcribing both clips and reading what the presenter said.
That is a ten-minute job a filename should answer.

**`part<N>` — that exact spelling.** Six conventions are already in this repo:
`-part_1`, ` part2_1080p`, `-part-3_1080p`, `_-_part_1`, `parts_-_1`,
`- part 1_1080p`. BIO-C2-LA-01 uses three of them *in one folder*. `ingest.py`
reads all six so old deliveries still work, but new drops use `part1.mp4`.

**Never put captions in a file called `.mp4`.** HeyGen sometimes ships
`<name>_caption.mp4` — the same take with captions burned in. It is not the
plate, and compositing on it puts two sets of captions on screen. `ingest.py`
ignores anything matching `*caption*.mp4`; keep it out of the drop folder
entirely if you can.

**The SRT is reference, not a clock.** It ships wrong: measured at 20 of 27 cue
starts off by more than 0.5s on PHY-C1-LA-02, and 64 of 85 boundaries off by up
to 3s on BIO-C2-LA-01 — which cost a full rebuild of two parts. Timing always
comes from `whisper.cpp` word timings. The SRT is kept only so the *wording* can
be checked. A drop with no SRT (BIO-C5-LA-01) loses nothing important.

**One script per folder, called `script`.** Scripts have been landing in
`inbox/<QID>/`, in a top-level `scripts/`, and as `part1.md` inside a topic
folder. If it is not in the QID folder, the pipeline cannot find it.

---

## What `ingest.py` refuses to pass

It is **gate 1**. Exit code 1, and nothing downstream should run:

- a part with no presenter clip
- two files claiming to be the same part
- audio or captions more than 1s from the clip — that is an SRT from a
  different take, which is how captions end up three seconds ahead of the voice
- clips with no part number that cannot be told apart

Warnings (exit 0) are survivable: no SRT, no script, a `(1)` duplicate-looking
copy, parts shot at different resolutions.

---

## Legacy folders

Folders named by topic rather than QID — `chemistry`, `physics`, `quathanak`,
`iron chromite`, `che c4 la 03`, `complex ion geometry`, `misc`, `_duplicates` —
predate this convention. `ingest.py` still reads them. They are not a pattern to
copy, and old `work/` copies point at their exact paths, so they are left alone
rather than renamed.
