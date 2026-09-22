# HIS-C2-LA-01 — मगध सबसे शक्तिशाली महाजनपद
## All-Veo scene plan

Script: "सबसे शक्तिशाली महाजनपद | History Reel Script" (Tab 1), 2025, 4 marks.
Character: `veo_kit/characters/ritesh.json`. Every generation carries the
three-image reference set, and the prompts are built by `veo_kit/build_prompts.py`
from `scenes.json` + `lines.json` (this table is the plan they were written
from). Check each clip with `veo_kit/face_gate.py` and `veo_kit/speech_qc.py`
before it goes anywhere near the edit. See `veo_kit/SETUP.md`.

**The wardrobe rule.** He is our teacher, not an actor in costume: the black polo
stays on in every shot. What changes is ONE accessory that belongs to the place —
a cream angavastram over the shoulder in the ancient scenes, and whatever the
cause hands him (grain, an iron sickle, a boat pole). He is a modern teacher who
has walked into the scene, which is the joke and the reason it reads as him.

**No Devanagari is ever generated.** Every label below is composited afterwards
with `src/veo_labels.py`. Veo renders Hindi as broken glyphs; this is the bug
ledger's first entry and it has not changed.

| # | t | narration beat | scene, and what he is DOING in it | composited label |
|---|---|---|---|---|
| 1 | 0–8 | MP Board intro, 2025, 4 नंबर | plain dark teaching wall. The only clip where he simply talks to camera. | — |
| 2 | 8–16 | "मगध सबसे शक्तिशाली महाजनपद कैसे बना?" | he is already **walking along a raised field bund** through the Gangetic plain at dawn, talking over his shoulder to the camera following him | मगध |
| 3 | 16–24 | "आधुनिक इतिहासकार कई कारण बताते हैं" | he stops, **crouches and picks up a handful of dark soil**, crumbling it between his fingers as he turns to camera; angavastram now over one shoulder | चार कारण |
| 4 | 24–32 | कारण 1 — खेती की उपज | **waist-deep in ripe rice, cutting a handful with a hand sickle** alongside two farmers working the same row; he straightens, holds the cut sheaf up | १. खेती |
| 5 | 32–40 | "ज्यादा अनाज → बड़ी सेना" | **helping heave a grain sack onto a bullock cart** at the field edge; he lets go, wipes his hands, looks at camera as the cart pulls away toward distant tents | बड़ी सेना |
| 6 | 40–48 | कारण 2 — लोहे की खदानें | **down in the ore cut with the diggers**, red dust on his forearms, **levering a lump of dark ore free with a pick** and lifting it | २. लोहा |
| 7 | 48–56 | "हथियार तथा उपकरण बनाना सरल" | inside the forge, firelight on his face: **he is working the bellows**, the bar glowing; the smith strikes; he takes the finished sickle and tests its edge with his thumb | हथियार और औज़ार |
| 8 | 56–64 | कारण 3 — जंगल में हाथी | sal forest in mist. **He walks beside the working elephant with the mahout**, one hand resting on its flank, matching its pace | ३. हाथी |
| 9 | 64–72 | "हाथी सबसे बड़ा हथियार" | **he is up on the elephant's back behind the mahout**, ducking a low branch, looking down at the camera as they pass | सेना की ताकत |
| 10 | 72–80 | कारण 4 — गंगा और उपनदियाँ | **he is poling a loaded cargo boat**, both hands on the pole, walking it down the deck as the bank slides past at first light | ४. नदियाँ |
| 11 | 80–88 | "सस्ता और तेज़ साधन" | at a river landing: **he passes a heavy clay jar down a human chain** from boat to bank, then steps back and gestures along the line of boats | सस्ता, तेज़ परिवहन |
| 12 | 88–96 | समरी — खेती, लोहा, हाथी, नदियाँ | he walks back up the landing steps toward camera, the river behind him, counting on four fingers as he climbs | four items fill in |
| 13 | 96–104 | "लेकिन आधा answer बाकी है" | he reaches the top step and stops dead; the sandstone palace gate stands over him. He looks up at it, then at camera | आधा उत्तर बाकी |
| 14 | 104–112 | जैन और बौद्ध लेखक — नीतियाँ | palace court. **He kneels at the scribe's low desk, steadying a palm leaf while the scribe cuts it**, then lifts the leaf and reads from it | जैन और बौद्ध लेखक |
| 15 | 112–120 | बिंबिसार, अजातशत्रु, महापद्मनंद | **he is standing among the ministers on the throne steps**, one of the group rather than in front of it, turning to camera mid-discussion | three names fill in |
| 16 | 120–128 | दो बातें याद रखो | he walks out of the court's shadow into the plain light, **pulling the angavastram off his shoulder as he comes**, back to being the teacher | भौगोलिक कारण / शासकों की नीतियाँ |
| 17 | 128–136 | "4 नंबर पक्के" + Notes + close | the modern dark wall again. Straight to camera. | — |

~17 clips of 8s. Notes on the shape:

- **He is in every single scene.** That is the ask and it is also what holds the
  video together — 17 generated places with no constant in them is a slideshow.
- **Two "quiet" bookends (1 and 17)** are him alone on a plain wall. They are the
  easiest clips to get right and they set the face the viewer will match the rest
  against, so generate these FIRST and keep the best one as the character
  reference for the others.
- **Scenes 4, 6, 7, 8, 10, 14 have him handling something.** Those are the ones
  worth the credits; a man standing in a field is stock footage, a man lifting a
  cut sheaf while saying "ज्यादा अनाज" is the lesson.
- **12 and 16 are the marks-earning summaries.** They carry composited lists, so
  frame him to one side and leave the other half of the frame clear.

## What this needs that it does not yet have

- **Narration.** There is no HeyGen take and no recording for this question. The
  audio has to exist before any clip can be cut to length, because segment length
  comes from the measured audio — that is the pipeline's oldest rule.
- **Credits.** 17 clips at ~15 each is ~255, before a single retry. Expect
  retries: the four chapter-2 clips this week took 3 attempts on one beat.
- **A character-consistency pass.** Every clip through `face_gate` at 0.90, and
  `character_qc.py` on the ones with unusual light (the forge, the river dawn).
