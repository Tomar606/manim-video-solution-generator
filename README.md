# Arivihan PYQ reels

Turns one MP Board previous-year question into a finished portrait reel. The presenter is a HeyGen clip.
Around him go the question on a real exam sheet, the teaching built point by point with exact diagrams and
real footage, Hindi captions, and the official answer page at the end.

```
you drop: HeyGen video + caption file (+ any patch clip) + the question ID
              │
Claude builds: splice ─ captions ─ sheet lookup ─ look ─ plan ─ Veo b-roll / exact diagrams ─ frames
              │
you review:   projects/<id>/review/index.html  (every frame, its words, its sound)  ──► "Copy my review"
              │
Claude renders and delivers: gates ─ answer page appended ─ Final <Subject>/<ID — title>/1.mp4
              │
you watch the delivered video once
```

The presenter's recorded audio is fixed, so **everything else is timed to it**.

## Start here

| You want to | Read |
|---|---|
| set up a machine (Mac or Windows) | [lab/kit_test/README.md](lab/kit_test/README.md#setup-once-per-machine) |
| know what a finished reel must look like and how it is delivered | [lab/kit_test/STANDARD.md](lab/kit_test/STANDARD.md) |
| make a reel | ask Claude Code: *"I dropped the files for HIS-C6-SA-04, make the reel"*. It follows `.claude/skills/reel` |
| see the screen elements available | [lab/kit_test/ELEMENTS.md](lab/kit_test/ELEMENTS.md) |
| work on the pipeline itself | [CLAUDE.md](CLAUDE.md) |

## Reviewing on any computer

Claude writes `projects/<id>/review/index.html` before every render. Open it in Edge, Chrome or Safari; on
Windows, double-click it. In VS Code, use the **Live Preview** extension (Microsoft), then *Open in Browser*.
VS Code's own preview cannot play H.264 video, so watch the finished cut in the browser.

On the page:
- scroll through every frame, click one to enlarge it, and press **▶ hear it** to hear the narration at that
  moment;
- write a note under any frame that needs a change;
- press **Copy my review** and paste it to Claude. With no notes it says APPROVED.

The rendered video appears at the top of the same page once it exists.

## Where finished reels go

`tools/deliver.py` is the only way a reel reaches a Final folder. It refuses if any gate fails. It appends
the answer page, held 7 seconds, and names everything the same way every time:

```
<DELIVER_ROOT>/Final Physics/PHY-C3-SA-04 — प्रतिरोध बनाम विशिष्ट प्रतिरोध/1.mp4
<DELIVER_ROOT>/Final Arts/Final History/HIS-C6-SA-04 — भक्ति संतों के उपदेश/1.mp4   (2.mp4 … for parts)
```

`DELIVER_ROOT` is the Desktop unless `.env` says otherwise.

**No answer page yet?** The reel is delivered without it and marked pending. Once the page is in the sheet
(any column), ask Claude to *"add the pending answer pages"* (`tools/deliver.py --pending`). If you have the
page as a file, give it to Claude. It is appended to the delivered video with no re-render.

A re-delivery keeps the previous file in `projects/<id>/final/previous_1.mp4`.

## Repository

| Path | What |
|---|---|
| `lab/kit_test/` | the pipeline: plans, the HTML stage, compiler, compositor, render, review |
| `tools/` | sheet lookup, captions, exam sheets, photos, Veo, gates, delivery, doctor |
| `flow/extension/` | the Chrome extension that drives Google Flow (Veo) |
| `veo_kit/` | Flow submission and download, and the presenter face check |
| `library/` | licensed photos, plates, fonts, textures, sound effects, icons, each with its licence record |
| `projects/<id>/` | one reel's inputs: meta, captions, prompts, answer page, review page |
| `src/` | shared modules the tools import (Flow bridge, delogo, LLM access) |

Older tracks (the Manim PYQ track, the reels track, the all-Veo route) were retired on 26 Oct 2026. They
are preserved at the git tag `archive/pre-kit`.
