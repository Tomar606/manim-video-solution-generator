# Background music library

35 instrumental tracks for the bed under the teacher's narration, in 8 mood
buckets. `manifest.json` has one entry per track: licence, credit line,
duration, loudness, mood, and which skin and subjects it suits. Paths in
`file` are relative to `library/`.

Everything here was picked for one job: sitting under continuous Hindi speech
for about two minutes without fighting it. Tracks were screened on
metadata (composer notes and tags) plus three measurements (ffmpeg ebur128):

- `integrated_lufs`: the loudness of the master as downloaded. These range from -8 to -28,
  so normalise before ducking.
- `loudness_range_lu` (LRA): how much the track swells. Under 6 is steady.
  Anything over 12 was rejected.
- `speech_band_rel_lu`: loudness of the 1–4 kHz band minus total
  loudness. The more negative, the less the track competes with the voice.
  Tracks at -6 or louder (a busy lead melody in the speech band) were rejected,
  and the few borderline ones (-6 to -7) are flagged in `notes`.

**No track was auditioned by ear.** None of the metadata mentions vocals, but
preview a track once before its first use.

## What's here

| Bucket | Tracks | Use |
|---|---|---|
| `curious-underscore/` | easy-lemon, cherry-blossom, little-bells, the-snail | question setup, "let's see why", light science explanation |
| `documentary-calm/` | clean-soul, immersed, water-lily, forest-mist-whispers | the default calm bed; long derivations; any subject |
| `tech-pulse/` | floating-cities, galactic-rap, mesmerizing-galaxy-loop, sonnor, atoms-in-peace | **night-HUD skin**: physics, chemistry, space, data |
| `editorial-news-lite/` | on-my-way, groove-grove, backed-vibes-clean, percussions-04 | **paper-editorial skin**: Vox-style, Pol Sci, Economics |
| `history-reflective/` | lost-time, man-down, gold-virginia, staring-at-the-night-sky | History and Pol Sci on grave topics (partition, war, famine) |
| `indian-light/` | vadodora-chill-mix, jalandhar, hidden-wonders, mystery-bazaar | History, Pol Sci and Geography with an Indian setting |
| `uplifting-recap/` | inspired, dreamer, wallpaper, classical-vibes-4, crying-sea | the closing recap and answer-card stretch |
| `light-tension/` | stay-the-course, constance, crypto, relax-spy, a-newcomer | "exam trap / don't skip this" moments |

Loopable: `mesmerizing-galaxy-loop` (93 s, seamless per the composer) and
`a-newcomer` (113 s, built as a loop, with an Indian flavour). Every other track
is 95 s or longer, so a 2-minute video needs one track, or a crossfade between
two tracks from the same bucket.

## How to pick a track

1. **Pick the bucket from the skin, then the subject.**
   - night-HUD: `tech-pulse`, with `documentary-calm` as the quieter
     alternative.
   - paper-editorial: `editorial-news-lite` or `curious-underscore`.
   - History, Pol Sci or Geography on an Indian topic: `indian-light`. On a
     grave topic, use `history-reflective` instead.
   - Filter `manifest.json` on `suits_skins` and `suits_subjects`. Prefer
     `energy` 1–2 for dense derivations and 3 for recaps.
2. **Rotate.** Consecutive videos must not share a track. Two videos in a row
   should not share a bucket unless the skin forces it. Pairs that sound alike
   count as the same track: `hidden-wonders`/`mystery-bazaar` (same santur
   palette), and `lost-time`/`man-down` (same cello section).
3. **One bed per video.** You can switch to `light-tension` for a single
   "exam trap" section and to `uplifting-recap` for the closing recap. Cross at a
   sentence boundary with a 1 s crossfade. Don't change the bed more than twice
   in a 2-minute video.

## Mixing

- **Normalise first.** Source masters range from -8 to -28 LUFS. Run
  `loudnorm=I=-23` (or apply gain from `integrated_lufs`) so every track starts
  from the same level.
- **Duck under the voice** to about **-24 to -28 LUFS short-term** while the
  teacher is speaking, using sidechain compression keyed from the narration
  (`sidechaincompress`) or a fixed level, since the narration is continuous. Use
  the quiet end (-28) for tracks flagged in `notes` as having more energy in the
  speech band: sonnor, jalandhar, staring-at-the-night-sky,
  classical-vibes-4, forest-mist-whispers, percussions-04. A gentle 2–4 kHz dip
  (-3 dB) on the music also helps.
- **Fades:** 1 s fade in at the start and 2 s fade out at the end. Use 1 s
  crossfades between beds.
- **Trim around known moments:** galactic-rap has a key change at 1:34 that the
  composer says "will steal attention", so use 0:00–1:30 or cut around it.
  constance builds, so keep to the first ~60–90 s. clean-soul and water-lily are
  quiet, wide-range masters, so a little compression helps keep them audible.

## Credits and licences

| Licence | Count | Credit |
|---|---|---|
| CC BY 4.0: Kevin MacLeod, incompetech.com | 23 | **Required.** Paste `credit_line` into the video description. |
| Mixkit Stock Music Free License | 11 | Not required (optional line provided) |
| CC0 (OpenGameArt): a-newcomer | 1 | Licence field is CC0, but the page also shows a CC BY 3.0 credit line. **Credit it anyway.** |

All three licences allow commercial use on YouTube and Instagram, including
monetised and paid course content, and allow trimming, looping and fading.

- **Kevin MacLeod / Content ID.** His catalogue is *pre-registered* with
  YouTube Content ID, so **expect claims**. Put the credit in the description
  **before** publishing. If a claim arrives, dispute it; the incompetech page
  says claims are released within about 72 h. A bulk-release form is linked on
  https://incompetech.com/music/royalty-free/youtube-contentid.html. Credit
  format (from his FAQ):
  ```
  "Title" Kevin MacLeod (incompetech.com)
  Licensed under Creative Commons: By Attribution 4.0
  https://creativecommons.org/licenses/by/4.0/
  ```
- **Mixkit.** The licence allows web/social video, educational use and
  advertising. It does **not** allow TV/radio broadcast, CDs/DVDs, video games,
  using the music as a standalone music track or remix, or registering it with
  Content ID. If a claim arrives, email the details to team@mixkit.co. If the
  course content is ever sold as a DVD or broadcast, the Mixkit tracks cannot go
  with it.
- When several tracks are used in one video, list every credit.

## Gaps and things that could not be filled

- **FreePD.com, the preferred CC0 source, is offline.** The site now shows a
  shutdown notice, so there is no CC0 bulk source in this library.
- **Pixabay Music** returns HTTP 403 to automated requests, and **Free Music
  Archive** downloads redirect to a login page. Both were skipped as the rules
  require.
- **Indian-flavoured underscore is thin.** Only four tracks passed, and two of
  them (hidden-wonders, mystery-bazaar) lean Middle-Eastern/bazaar as much as
  Indian. Rejected for a busy lead in the speech band: *Dhaka* (sarod lead),
  Mixkit *Indian Meditations* (flute lead) and OGA *Mystical Enigmatic*. OGA
  *Electronic Indian tabla tune* was also left out because it is an unfinished
  "test mix" mastered very hot. There is no santoor- or bansuri-led calm bed yet.
- **Vox-style editorial percussion.** Only `percussions-04` is truly
  sparse-percussive. The rest of that bucket is light groove.
- **Credit load.** 24 of 35 tracks need a credit, and 23 of them carry Content
  ID claim risk (Kevin MacLeod). More Mixkit or CC0 tracks would cut that.
- Only one track in the library is truly short (93 s, loopable), so there is
  no set of 30–60 s stingers.
