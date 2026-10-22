# HIS-C2-SA-06 — assembly plan

What is ready, what is waiting on you, and the order to put it together.

## Ready now

| piece | file | length |
|---|---|---|
| Map M1 — Pataliputra | `map_engine/output/his_c2_m1_pataliputra.mp4` | 12s |
| Map M2 — the three centres | `map_engine/output/his_c2_m2_three_centres.mp4` | 27s |
| Map M3 — the fifth, then all five | `map_engine/output/his_c2_m3_all_five.mp4` | 24s |
| Script | `projects/his-c2-sa-06/script.md` | — |
| Veo prompts | `handoff/his-c2-sa-06/VEO_PROMPTS.md` | 5 × 10s |
| Voice script | `handoff/his-c2-sa-06/HEYGEN.md` | — |
| Question metadata | `projects/his-c2-sa-06/meta.json` | — |

All three map segments are 1080×1920, on the history plate, in the halo window,
with India's complete territory and no label clipped.

## Waiting on you

1. **The five Veo clips** — 9:16, 10s each, him in every shot.
2. **The HeyGen voice recording** — one take, the ten blocks in `HEYGEN.md`.
3. **Two decisions**, below.

## The running order

    00:00 - 00:10   VEO-1   the pillar            he speaks
    00:10 - 00:20   VEO-2   the scale             he speaks
    00:20 - 00:30   VEO-3   the courtyard         he speaks
    00:30 - 00:42   MAP     M1  Pataliputra       voice over
    00:42 - 00:52   VEO-4   the trade road        he speaks
    00:52 - 01:19   MAP     M2  three centres     voice over
    01:19 - 01:29   VEO-5   the gold hillside     he speaks
    01:29 - 01:53   MAP     M3  all five          voice over
    01:53 - 02:08   DATA    the answer list       voice over
    02:08 - 02:20   ???     the close             see decision 2
    02:20 - ...     the answer pages

Total about 2:20 before the answer pages. Five Veo clips carry 50s; the maps
carry 63s.

## Order of assembly

1. **Lay the voice first.** Narration sets the clock in this pipeline —
   segment lengths come from the measured audio, and everything conforms to it.
   Cut the recording into the ten blocks and that gives the real timings.
2. **Fit each map segment to its block.** The three map scenes are timed to the
   estimates above; once the real audio lengths are known, adjust `duration`
   and the action times in the scene YAML and re-render. A re-render is about
   three minutes and needs no code.
3. **Lay the Veo clips in**, replacing their audio with the recording.
4. **Then the answer pages.**

## Two decisions still open

**1 · The question card.** There is no card in the running order yet. The
existing card is a Manim render built around a photograph of a science question
paper, with the MP Board header and the marks sticker. History needs either a
photograph of a History paper to sit in the same design, or a different
treatment. Tell me which and I will build it.

**2 · The close.** The script ends with him saying "पूरा answer आपकी स्क्रीन
पर आ जाएगा". He is not composited anywhere in this video, so that line has
nowhere to sit unless either a sixth Veo clip is generated for it, or he is
keyed onto the history plate for twelve seconds the way the science videos do
it. A sixth Veo clip is cleaner and keeps the format consistent.

## One thing that is missing and will be needed

**There are no answer pages for this question.** The sheet row has no image and
its status is "Not Started" — unlike the biology questions, which came with
reviewed pages. Somebody has to write and photograph the answer sheet before
this video can end the way the others do.
