# Veo prompts for a speaking character: what the evidence says

Research done 22 Sept 2026 for the all-Veo History video (HIS-C2-LA-01), where
the first clips came back with Ritesh sir mouthing gibberish. Three goals:
accurate results, the same man in every clip, and speech at a natural pace.

Every claim below is tagged with where it comes from, because they are not
equally strong:

- **[Google]**: Google's own documentation or blog
- **[field]**: practitioners' reports; plausible, but not verified by us
- **[ours]**: measured on our own videos, or seen in our own generations

---

## 1. What is wrong with the prompts we have been sending

### 1a. The NEGATIVE block is read as part of the prompt, not as a negative prompt

The API has a separate `negativePrompt` parameter **[Google]**. Flow's UI has
no such field, so `src/veo.py` pastes the negatives into the prompt text
under a `NEGATIVE:` heading **[ours]**. The model then reads "burnt-in
subtitles, auto-generated captions, Devanagari letters, numerals, a logo" as
words in the prompt it is asked to follow.

Google's guidance on negatives says: *"Not recommended: using instructive
language or words such as 'no' or 'don't'… Recommended: Describe what you
don't want to see"*, and even that describes a separate parameter **[Google]**.
Practitioners report that telling Veo "no talking" backfires, because *"the
model interprets negative commands as concept introduction rather than
prohibition"* **[field]**. MIT Technology Review found that "no subtitles" in
the prompt does not stop garbled captions **[field]**.

This is our own rule already. CLAUDE.md says: *"Never write 'logo'… into a
generation prompt — not even as a negative. Naming a thing is a signal to draw
it."* The speaking-character prompts broke it. Their negative list **named
subtitles and captions first**, because that is the risk dialogue raises.

**Change:** in Flow, remove the NEGATIVE block entirely. Describe the frame
positively instead: "a clean image with nothing written anywhere in the
frame" does the job without naming subtitles or captions.

### 1b. The body of the prompt is full of prohibitions too

The dialogue section said *"does not repeat the line, does not improvise, does
not add a greeting… says no other word"*, and the character section said
*"Do not slim his face… Do not trim… Do not give him a full straight
hairline."* That is the same failure inside the positive text: every "do not"
names the thing it forbids **[Google]**, **[field]**.

**Change:** say what IS true. "His beard is full, thick and rides high onto his
cheeks" replaces "do not trim the beard". "After the line he closes his mouth
and nods" replaces "says no other word".

### 1c. Short lines leave dead time, and Veo fills it with invented speech

Reference-image clips can only be 8 seconds long: *"reference image to video
only supports 8 seconds"* **[Google, Veo 3.1 model page]**. When the line
finishes early, *"Veo tends to pad silence with sound effects or filler
dialogue to make the clip feel complete"* **[field]**.

I sized the History lines by word count (at most 19 words). Measured in
syllables, **12 of the 17 lines fill only 4.0 to 5.5 seconds** of the
8-second clip **[ours, §3]**. That leaves two to four seconds for Veo to fill,
which is where gibberish comes from even after the dialogue problem is fixed.

**Change:** size lines by syllables (§3), and describe what he DOES during the
seconds when he is not speaking.

### 1d. The prompts are about three times the length Google's own examples use

Google's formula is *"[Cinematography] + [Subject] + [Action] + [Context] +
[Style & Ambiance]"*, and its examples run to 40–70 words **[Google]**. Ours
ran to 370–400 words, followed by a long negative list **[ours]**. One
practitioner source says a long cinematic description plus dialogue *"risks
dropping the speech entirely"* and cites a 1,024-token limit **[field]**. I
could not find that limit stated on Google's model page, so treat it as
unverified.

The direction is still clear. Devanagari costs many tokens per word, and every
sentence of face description competes with the one line we most need the model
to keep.

**Change:** let the reference image carry the face. Keep the text to camera,
action, setting and the line.

### 1e. Hindi dialogue is outside what Google supports

The Veo 3.1 model page lists **"Prompt languages: English"** **[Google]**. A
practitioner summary quotes Google: *"English (EN) is fully supported, but
other languages have not been evaluated"* **[field]**. People do get usable
Hindi and Punjabi out of it **[field]**, but nothing guarantees it, and lip
sync outside English is reported to be weaker **[field]**.

**Consequence:** expect a higher reject rate on Hindi lines than on anything
else, and budget retries for it.

---

## 2. Keeping him the same man in every clip

### What we do now

We use one reference image (`ritesh_reference.jpeg`). It is **portrait
1080×1920**, shows him mid-gesture with a hand in frame, and sits on a taupe
backdrop. We attach it as an ingredient and then describe his face again in
100+ words of text **[ours]**.

### What the evidence says to do

- **Use up to three images of the one person.** Asset references allow *"up to
  three images of a single person, character, or product"* **[Google]**. Give
  it three different views, not one.
- **Put the references on a plain background.** Flow's help page says: *"For
  the best results, provide subject or product references on a plain or
  segmented background"* **[Google, Flow Help]**.
- **Crop each image to the aspect of the generation, at more than 1024px.**
  We generate 16:9, and our reference is 9:16 **[field]**.
- **Put the character's image first.** When elements compete, the model gives
  earlier images more weight **[field]**.
- **Make the text agree with the images and refer to them.** *"Your text prompt
  should complement, not contradict, your visual inputs. Make sure your prompt
  references the frames or ingredients you've provided"* **[Google, Flow
  Help]**. In Flow you refer to an uploaded asset by typing `@`.
- **Use Flow's Characters feature.** It bundles the images, a "Character info"
  text (personality, mannerisms) and a voice into one reusable `@Name`.
  *"Your character's face, clothing, and voice remain strictly consistent
  across multiple generations without needing to upload the same images every
  time"* **[field, describing Flow]**. It needs at least two images: front on,
  plus a second angle **[field]**. The Characters tab has been in our Flow
  sidebar all along and we have not used it **[ours]**.

### The reference set to build

Take three frames from his HeyGen takes, all shot the same day in the same
polo:

1. **Front, head and shoulders, mouth closed, hands out of frame.** This is the
   identity anchor.
2. **Three-quarter view**, turned about 30°, so the model has seen the beard in
   profile and the hairline from the side. The beard's line on the cheek and
   the receding corners are what generations lose **[ours]**.
3. **Waist-up, standing**, so it learns his build. Every impostor so far was
   slimmer **[ours]**.

Cut each one out onto a plain mid-grey background (the house compositor
already keys him cleanly), crop to 16:9 at 1920×1080, and upload them in that
order. **Every clip still goes through `veo_kit/face_gate.py --min 0.90`**,
which measures identity instead of trusting the prompt.

---

## 3. How much he can say in one clip

### His measured rate [ours]

I measured 300 caption lines across the 8 short-answer videos he has
recorded, timing each line against its SRT:

| | median | middle half of lines |
|---|---|---|
| words / second | **2.69** | 2.35 – 3.12 |
| syllables / second | **5.79** | 5.12 – 6.43 |

Per video, the median ranges from 5.28 to 6.40 syllables/second. His pace is
stable.

**Budget by syllables, not words.** Hindi words vary too much: है is one
syllable and महत्वाकांक्षी is six. A word limit let lines through that fill
only half the clip.

### The budget for one 8-second clip

- 0.7 s of him existing before he speaks: a breath, eyes to camera. Practitioners
  say a clip that starts on the first syllable *"feels wrong"* **[field]**.
- **6.5 s of speech → about 38 syllables (33 to 42).**
- 0.8 s after the line: he closes his mouth and finishes the gesture.

A line below 33 syllables leaves time that Veo will fill (§1c). Either write
more, or give him an explicit silent action that takes the remaining time. A
line above 42 syllables gets rushed or cut off.

The counter is `veo_kit/syllables.py`, and `veo_kit/build_prompts.py` refuses
a line outside 33-42. Check every line with it before anything is generated.

---

## 4. The voice, and your plan to clone it

- **Veo keeps no voice between generations.** *"No voice-persistence mechanism
  exists"* in plain Veo **[field]**, so each clip comes back in a slightly
  different voice.
- **Flow Characters fix the drift, but not with his voice.** The voice is a
  preset, or a custom voice built on a preset; *"you currently cannot upload
  external audio files to clone a voice"* **[field]**.
- **Flow Avatars ("@me") use his real face and voice.** He records a selfie
  video and reads some numbers aloud in the Gemini app. The avatar belongs to
  that account only and cannot be shared **[field]**. It needs him in person,
  on the account that does the generating.
- **The common fallback:** generate with a consistent preset voice, then run
  the finished track through a voice changer such as ElevenLabs, set to his
  cloned voice **[field]**.

We have hours of his real voice in the HeyGen takes, and ElevenLabs is already
in the pipeline. That makes the last route the cheapest reliable one: a
consistent Flow character voice, converted to his cloned voice afterwards. The
Avatar route is higher fidelity but needs him in person.

---

## 5. The template, rewritten

In the order Google recommends. There is no NEGATIVE block, no "do not", and
the face is left to the references:

```
Medium shot at eye level, the camera holding still.
@Ritesh, in his plain black short-sleeve polo with a cream cotton cloth over
his left shoulder, stands waist-deep in a field of ripe golden rice at low sun,
a short hand sickle in his right hand.
He gathers a handful of stalks, cuts them, straightens and lifts the sheaf,
then looks into the camera and says in Hindi, warmly and unhurried:
"पहला कारण — मगध में खेती की उपज अच्छी होती थी, इसलिए यहाँ अनाज भरपूर होता था।"
He finishes, closes his mouth and nods once, still holding the sheaf.
Two farmers in undyed cotton cut the same row behind him.
Warm natural light, chaff drifting in the air, the soft rustle of rice
stalks. A clean photographic image, nothing written anywhere in the frame.
```

About 110 words. The line is lengthened to 37 syllables, which is 6.4 seconds at
his median rate, so it fills the clip. The original 26-syllable version would
have left three seconds for Veo to fill. My first rewrite reached 42 syllables,
which is 7.3 seconds, and would have been rushed. Check every line with the
counter; don't estimate by eye. The setting keeps him working, as you asked, and his hands have
something to do while he speaks.

---

## 6. The order to change things in

1. **Build the three-image reference set and a Flow Character** for him. This
   is the biggest gain in consistency, and it costs no credits.
2. **Add the syllable counter** as a check on every line.
3. **Rewrite the prompt builder:** Google's element order, no NEGATIVE block
   in Flow, no "do not", and the face left to the references.
4. **Generate two test clips** (the wall scene and the rice field), then run
   `face_gate` on them and listen to the Hindi before generating the other 15.
5. **Decide the voice route** (§4). That one is your call.

## Sources

- Google Cloud Blog, *Ultimate prompting guide for Veo 3.1*:
  https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-veo-3-1
- Veo 3.1 model page, Vertex AI (prompt languages; 8 s limit with references):
  https://cloud.google.com/vertex-ai/generative-ai/docs/models/veo/3-1-generate
- Veo prompt guide, Vertex AI (negative prompts; dialogue syntax):
  https://cloud.google.com/vertex-ai/generative-ai/docs/video/video-gen-prompt-guide
- Google Flow Help, *Create videos in Google Flow* (ingredients, frames, voice references):
  https://support.google.com/flow/answer/16353334?hl=en
- Google blog, *Veo 3.1 Ingredients to Video*:
  https://blog.google/innovation-and-ai/technology/ai/veo-3-1-ingredients-to-video/
- MIT Technology Review, *Veo 3 has a subtitles problem*:
  https://www.technologyreview.com/2025/07/15/1120156/googles-generative-video-model-veo-3-has-a-subtitles-problem/
- Prompt Architects, *Dialogue Prompting in Veo 3.1*:
  https://prompt-architects.com/blog/101-veo-dialogue-prompts
- ApiPass, *Veo 3.1 keeps adding dialogue*:
  https://apipass.dev/blogs/how-to-solve-veo-3-keep-generating-unwanted-dialogue
- Kartaca, *Character and avatar creation in Google Flow*:
  https://kartaca.com/en/mastering-google-flow-the-ultimate-guide-to-character-avatar-creation/
- Voice consistency workflow (ElevenLabs voice changer):
  https://ai-for-real-life.beehiiv.com/p/the-secret-to-consistent-characters-in-veo-3-and-how-to-fix-the-voices-too

---

## Addendum, same day: what the first v2 clips showed [ours]

Two scenes (the wall, the rice field) were generated from the v2 prompts with
the three-image reference set, then fetched and checked with `veo_kit/`:

- **The speech is right.** Whisper hears 93% and 97% of each line's sounds, in
  order, with 2-6% extra, and nothing after the line. The gibberish is gone.
- **The clips are 10.0 s, not 8.** Flow returned 1280x720 at 10.01 s with three
  references attached, despite the 8-second note for Veo 3.1's API. The
  33-42 syllable budget still worked: speech filled 6.0-8.4 s, and the "before"
  and "after" actions took the rest.
- **Flow's agent rewrites every prompt.** The grid's prompt box feeds Flow's
  agent, which paraphrases the English ("the camera holding still" became
  "static camera", "Lip sync is perfect with the Hindi dialogue" was added)
  but kept the Hindi line verbatim both times. On an earlier round it ADDED its
  own "Negative: subtitles, captions, watermark, logo" block. `veo_kit/fetch.py`
  saves what was actually sent beside each clip and flags an added negative
  block.
- **Identity:** the wall scored 0.935 (pass) and the rice field 0.887 (fail,
  a wide shot with a small face). See `assets/character/ritesh.md`.

