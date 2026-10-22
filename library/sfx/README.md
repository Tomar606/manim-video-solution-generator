# SFX candidate library

This folder holds candidate sounds for the Vox-style portrait explainers. Each
sound is filed under the on-screen moment it marks. Every file here has been
measured with `measure()` from `tools/sfx_registry.py` and passed that moment's
rules. **None of these sounds is live yet.** The live library is `assets/sfx/`
(see `assets/sfx/README.md`).

To make a sound live, copy it into the matching `assets/sfx/<role>/` folder and
run `python tools/sfx_registry.py`. The registry re-measures it against its own
role table, and that check is the one that counts. For example, a sound from
`element-pop/` goes to `label-lands/`, `list-fill/` goes to `list-item/`, and
`card-slide/` goes to `card-appears/`.

`manifest.json` lists every kept file with its measurements, source and licence.
It also has a `rejected` list showing what was tried and why each one failed.

## Rules applied (stricter than the registry)

| rule | here | registry |
|---|---|---|
| tonality | < 0.30 | < 0.30 |
| rising sweep | < +0.35 **at every length** | only checked from 0.8 s up |
| bursts, single-event moments | **exactly 1** | at most 2 |
| length | per moment, below | per role |

Processing applied to every file: silence trimmed (at most 10 ms pre-roll),
48 kHz 16-bit mono WAV, peak normalised to −3 dBFS, 20–40 ms fade-out and a
2 ms fade-in.

Some source files contained several hits. For those, the longest window that
contains the main peak and passes the rules was cut out. Those files are marked
`"excerpt": true`, and the window used is recorded under `processing`.

## Moments

| folder | marks | single event | max | kept |
|---|---|---|---|---|
| `element-pop/` | a chip, label or pill arrives | yes | 0.4 s | 6 |
| `list-fill/` | an item fills a slot | yes | 0.4 s | 6 |
| `card-slide/` | a card or panel slides in (soft, not rising) | yes | 0.8 s | 6 |
| `typewriter/` | text types on (texture) | no | 1.5 s | 6 |
| `arrow-draw/` | a line or arrow draws | yes | 0.6 s | 6 |
| `marker-stroke/` | a highlighter swipe or underline | yes | 0.6 s | 6 |
| `circle-scribble/` | a pen circles a word | no | 1.0 s | 6 |
| `tick/` | a checkmark | yes | 0.4 s | 5 |
| `cross-strike/` | a strike-through or cross | yes | 0.5 s | 5 |
| `stamp/` | a stamp or sticker slaps on | yes | 0.5 s | 6 (all stand-ins) |
| `tape/` | tape is applied or ripped | yes | 0.6 s | 5 (3 stand-ins) |
| `paper/` | a single paper slide or tap | yes | 0.6 s | 5 |
| `photo-in/` | a photo snaps in (shutter) | yes | 0.5 s | 6 |
| `map-pin/` | a pin drops | yes | 0.4 s | 6 |
| `counter-tick/` | a counter advances ("2/4") | yes | 0.3 s | 6 |
| `timeline-node/` | a timeline node lights | yes | 0.3 s | 6 |
| `colour-flood/` | a full-frame colour wash (low whoosh or thump) | yes | 1.2 s | 5 |
| `transition-whoosh/` | a scene transition (neutral or falling) | yes | 1.0 s | 6 |
| `hud-blip/` | a digital tick for the night-hud skin | yes | 0.3 s | 6 |
| `page-turn/` | a single page turns | yes | 1.0 s | 6 |

**115 files in total, 3.6 MB.**

`suits_skins` in the manifest suggests which skin each sound fits. Paper, tape,
stamp, page-turn, marker, scribble and cross sounds are tagged
`paper-editorial`, hud-blip is tagged `night-hud`, and everything else is
tagged `default`.

## Licences and credit

| source | files | licence | credit |
|---|---|---|---|
| Kenney.nl: Interface Sounds, UI Audio, Impact Sounds, RPG Audio, Casino Audio | 56 | CC0 1.0 | not required (a courtesy "Kenney.nl" is welcome) |
| Mixkit | 59 | Mixkit Sound Effects Free License (mixkit.co/license/#sfxFree) | not required |

Both licences allow commercial use with modification. Nothing here is under an
NC or ND licence, nothing comes from BBC, and nothing came from a source that
needs a login. A `credit_line` is still recorded for every file in case a
voluntary credit is wanted. Mixkit's licence does not allow redistributing the
sounds as standalone files (for example a public sound pack). Using them inside
videos is fine.

## Gaps and things to check by ear

- **There is no real rubber-stamp recording.** All of `stamp/` is a stand-in
  built from soft thuds, wood hits, a leather drop and a book slap
  (`"stand_in": true`).
- **Tape is thin.** `duct-tape-pull` and `duct-tape-pull-b` are short excerpts
  from a single Mixkit duct-tape file. `cloth-rip`, `leather-handle` and
  `belt-pull` are stand-ins. A proper tape rip or tape-apply recording is still
  needed.
- **colour-flood has no long soft swell.** The rule of exactly one burst kept
  cutting longer whooshes down. The passes are the low Kenney punch thumps
  (tonality 0.21–0.23, the closest of any file to the limit), one falling
  vacuum (`air-zoom-vacuum`), and a 0.21 s excerpt of an air woosh. These are
  short for a full-frame wash.
- **Some excerpts may sound clipped.** These were cut hard to reach one burst:
  - `page-turn/big-page-turn` (0.15 s)
  - `page-turn/page-turn-single` (0.18 s)
  - `photo-in/shutter-click` (0.05 s)
  - `hud-blip/scifi-glitch` (0.05 s)
  - `tick/box-check-click` (0.08 s)

  For page-turn, `book-flip-a` (0.64 s, a whole file) is the safest choice.
- **The typewriter files are 1.05–1.2 s cuts from longer typing takes.** They
  have soft edges but are not sample-accurate loops, so crossfade about 30 ms
  when looping. `typewriter-key-soft` is a single key, for placing one per
  character.
- **circle-scribble files are multi-burst by nature,** since a scribble is
  several strokes. That moment is treated as texture, not as one event.
- **Short UI clicks have no meaningful sweep reading.** Files under about
  25 ms after trimming measure a sweep of 0.00. Kenney `click_002`–`005` and
  `glitch_001`/`003` are under 20 ms, so `measure()` cannot read them at all
  and they were not used.
