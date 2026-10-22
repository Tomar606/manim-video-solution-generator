# The Arivihan teacher — character sheet

Written from the delivered videos, not from imagination: the description below
is what he actually looks like and does in BIO-C1-LA-01, C4, C5-LA-03 and
C5-LA-04. Blocks in code fences are meant to be pasted.

---

## 1 · Appearance — paste this

```
An Indian man in his early thirties, warm medium-brown skin, medium build, average height. A full, well-kept dark beard, trimmed close along the cheeks and fuller at the chin, with a connected moustache. Short black hair, neat at the sides and brushed up with a little volume at the front. Dark expressive eyebrows, open friendly eyes, an animated and readable face that moves a lot while he talks.

He wears a plain dark navy short-sleeved polo shirt — soft collar, a short three-button placket, matte fabric, no pattern, sleeves ending mid-bicep. A small neat wordmark sits on the left chest and a small circular emblem on the right chest. Nothing else: no jacket, no tie, no scarf, no visible jewellery, no wristwatch, no lanyard, no spectacles.

He is lit evenly from the front, standing, framed from mid-thigh up, facing the camera directly.
```

**Continuity note.** The polo is the uniform. If you are generating him across
several clips, the shirt colour drifting between navy and black, or the collar
changing shape, is the first thing that makes two clips look like two people.
Pin it in every prompt.

---

## 2 · Voice — paste this

```
A warm, energetic male Hindi voice, early thirties, mid-range and clear, with the easy confidence of a teacher who has explained this a hundred times and still wants you to get it. Conversational, never formal or declamatory — he speaks to one student, not to a hall.

He speaks Hindi with English words mixed in naturally where a student would use them: board exam, answer, direction, important, topic, notes. The English words are said the way an Indian teacher says them, not in an American accent.

Pace is brisk but unhurried, with real pauses before the point that matters. He warms and lifts slightly on the thing to remember, and drops to a confiding, lower register for asides — the "between us" tone. He is encouraging, never stern and never shouting.
```

**Register, with examples from the delivered scripts.** He addresses students
directly and familiarly — *बच्चों*, *देख लो*, *याद रखो*, *ध्यान से सुनना*,
*इसे एकदम दिमाग में बिठा लो*. He tells them what will be marked — *ये चार
नंबर पक्के*, *नंबर यहीं बनते हैं*. Keep that; it is the house voice, and it is
why the videos sound like a teacher rather than a narration.

---

## 3 · Body language — paste this

```
He gestures constantly but economically, and always between waist and upper chest — never above his head unless he is pointing at something shown above him, and never below the waist.

His default is both hands open, palms up or forward at waist height, as if offering the idea to you. When he is defining or holding a single concept, both hands rise to chest height, palms facing each other, fingers spread, as though holding something the size of a football. When he lists, he counts on the fingers of one hand. When he means "this is the key thing", one hand rises with the fingers loosely curled and pauses there.

Between points he returns to rest: hands loosely clasped together low and centred, shoulders dropped. That rest position is important — it is the punctuation between ideas.

He leans very slightly toward the camera, keeps his head steady, holds direct eye contact with the lens, and lets his eyebrows and mouth carry the emphasis. His feet stay planted; he does not pace, sway, or wander out of frame.
```

**Why the height limit matters here.** Graphics sit above him in this format —
maps, diagrams, chips. Gestures that go above his head collide with them, and
the layout gate that keeps graphics clear of his head cannot fix an arm.
Keeping hands below the collarbone is a production constraint, not a style
preference.

---

## 4 · What he never does — paste this into the negative

```
NEGATIVE: spectacles, glasses, tie, blazer, jacket, kurta, formal suit, patterned shirt, logo-heavy clothing, jewellery, wristwatch, lanyard, headset, microphone in frame, hat, long hair, clean-shaven, stubble only, arms crossed, hands in pockets, arms folded, pointing aggressively at the camera, gestures above the head, finger-wagging, pacing, swaying, turning away from camera, looking off-camera, exaggerated cartoon expressions, theatrical shouting, holding props, holding a pointer, holding a book, sitting, desk, chair, podium
```

---
---

# Notes for you — do not paste

## If you are generating him rather than filming him

Be careful here. A generated likeness of a real person drifts between clips —
a slightly different nose, a beard a shade lighter, a collar that sits
differently — and the effect on a viewer who knows the teacher is worse than
using a different person entirely. It lands in the uncanny valley of *your own
presenter*.

Two safer routes, in order:

1. **Keep filming/keying him** and use generated clips only for places and
   objects, which is what the rest of this handoff assumes. The Veo prompts in
   `his-c2-sa-06/` deliberately contain no people so he can be keyed in.
2. **If you must generate him**, lock one reference image and pass it as the
   first frame of every clip, and never let words alone carry the likeness.
   Words have already failed at this repeatedly on much simpler subjects.

## Making the character sheet do its job

Paste sections 1, 2 and 3 together as a single character block at the top of
any prompt, then describe the scene and the action after it. The order matters:
tools weight the opening of a prompt most heavily, and identity is the thing
you least want drifting.
