# HIS-C2-SA-06 — the single HeyGen take, and where to cut it

Paste **`HEYGEN_SCRIPT.txt`** into HeyGen as one script and generate one clip.
Nothing in that file is a stage direction — every character in it is meant to be
spoken, so it can go in verbatim.

Checked before you paste it: **no digits and no symbols anywhere.** Spoken lines
go to TTS as written, so "दो हज़ार बाईस" is spelled out rather than written as a
number — a numeral there comes back read as English digits or skipped.

Estimated **1:44 of speech** plus the pauses HeyGen puts at the paragraph
breaks, so expect roughly two minutes.

## The eleven cuts

Each paragraph break in the script is a cut point. Cut on the silence.

| # | opens with | ~len | used as | goes under |
|---|---|---|---|---|
| 1 | दो हज़ार साल पहले… | 6.6s | audio spare | VEO-1 the pillar |
| 2 | अब सोचो, राजधानी में… | 6.6s | audio spare | VEO-2 the scale |
| 3 | और बच्चों, यही सवाल… | 10.9s | **picture + audio** | question card |
| 4 | मौर्यों ने पूरे साम्राज्य को… | 7.8s | audio spare | VEO-3 the courtyard |
| 5 | सबसे पहला और सबसे बड़ा… | 9.8s | **picture + audio** | MAP M1 Pataliputra |
| 6 | इनमें से दो केंद्र… | 6.2s | audio spare | VEO-4 the trade road |
| 7 | पहला, तक्षशिला… | 16.8s | **picture + audio** | MAP M2 three centres |
| 8 | और आख़िरी केंद्र? | 6.2s | audio spare | VEO-5 the gold hillside |
| 9 | कर्नाटक की सोने की खदानें… | 11.7s | **picture + audio** | MAP M3 all five |
| 10 | अब लिखने का तरीका… | 14.1s | **picture + audio** | the answer screen |
| 11 | बस इतना लिख दिया ना… | 7.0s | **picture + audio** | the close |

**Six cuts are used, five are spare.** On the data screens he is keyed in below
the map, so those need HeyGen's picture as well as its audio. Under the Veo
clips he is already on screen inside the generated place, so those five cuts are
not needed — unless Veo's Hindi disappoints, in which case you lay them over the
Veo picture and discard Veo's sound. Generating the whole script in one take
costs nothing extra and leaves that door open.

## What changed, and why

**The question is stated again.** The running order had lost the beat where he
names the question and the marks — cut 3. Every video in this house states it
early, because it is how a student knows this is their exam question rather
than a general history video. It sits after the hook has done its work, which
is the right place: the Veo pillar asks *how do you rule something this big*,
and then he says *this was asked in the board, six marks*.

**Two map segments need re-timing.** They were cut to estimates; the real
lengths are now known:

    M1  built 12s, needs ~10s   (cut 5 is 9.8s)
    M2  built 27s, needs ~17s   (cut 7 is 16.8s)
    M3  built 24s, needs ~12s   (cut 9 is 11.7s)

M2 and M3 are notably long. Once you send me the real audio, I will adjust the
scene YAML and re-render — about three minutes each, no code. Do not stretch
the map clips to fit instead: a map that drifts slowly for ten seconds longer
than the sentence is dead screen time, and the whole point of the timeline is
that the picture follows the voice.

## Two beats still have no picture

**Cut 3 — the question card.** Still undecided. It needs either a photograph of
a History paper to sit in the existing card design, or a different treatment.

**Cut 11 — the close.** He is not composited anywhere in this video, so this
line has nowhere to sit unless a sixth Veo clip is generated for it. That is
the cleaner fix and keeps the format consistent.
