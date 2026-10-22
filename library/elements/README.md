# Element library

Arrows, marks, cards and icons for the portrait 1080x1920 Hindi explainer
templates rendered by the headless-Chromium renderer (`tools/edu/renderer`).
One element works in every skin, so two videos built from the same template
need not look alike.

```
library/elements/
  kit/                    our own skinnable kit (original, Arivihan)
    svg/arrows/*.svg        12 arrows
    svg/marks/*.svg         18 marks
    svg/frames/*.svg        2 HUD frames
    cards/*.html            22 card snippets (HTML, because they hold Devanagari)
    cards/cards.css         every card's styling, all from skin variables
    skins/*.css             4 skins: night-hud, paper-editorial, chalk-slate, pastel-notebook
    kit.css                 draw-on / pop / stamp / slide helpers + mark hosting
    fonts.css               @font-face for assets/fonts (relative to kit/)
    preview.html            contact sheet; ?skin=<name>
  previews/<skin>.png     the contact sheet rendered per skin, 1080 wide
  vendor/                 collected open-licence vectors (see licences below)
    icon_picks.json         191 concepts -> one icon file, with Hindi gloss
  manifest.json           every element, card, skin and vendor set
  tools/                  build_kit.py, build_icon_picks.py,
                          excalidraw_to_svg.py, render_previews.mjs
```

Everything in `kit/svg`, `kit/cards/*.html`, `kit/preview.html` and
`manifest.json` is generated: edit `tools/build_kit.py` (or `cards.css`, the
skins) and rebuild, never the outputs.

```
python3 library/elements/tools/build_kit.py          # svg, cards, preview, manifest
python3 library/elements/tools/build_icon_picks.py   # vendor/icon_picks.json
node    library/elements/tools/render_previews.mjs   # previews/*.png, one Chromium
```

## Using an element in a template

1. **Load the CSS** in this order: `fonts.css`, one skin, `kit.css`,
   `cards/cards.css`. Copy `fonts.css` next to the template if it lives
   elsewhere and fix the `url()`s.
2. **Set the skin** with a class on any ancestor: `<body class="skin-night-hud">`.
   Every colour, font, radius and shadow comes from that class.
3. **Inline the SVG.** Paste the file's `<svg>` into the page (or read it
   in at build time). It must be inline: an `<img src="x.svg">` cannot see
   the page's CSS variables and falls back to the default red.
4. **Size it by width/height on the `<svg>`.** Stroke widths are in viewBox
   units, so the line scales with the element. To keep a fixed line weight
   while scaling by k, set `--stroke-w` to (px / k) on that svg.
5. **Paste a card** from `cards/*.html` and replace the sample Hindi.

### Animating

Every line in the kit is a stroked path with `pathLength="1"` and class
`draw`; `--i` orders the strokes (shaft, then head). Two ways to play it:

- CSS: add `.is-drawing` to the svg or an ancestor. Timing comes from
  `--dur` (0.7s), `--stagger` (0.22s) and `--delay`.
- Frame-driven (what the renderer wants for deterministic frames): set
  `stroke-dasharray: 1 1` and drive `stroke-dashoffset` from 1 to 0 per path.
  Or pause `document.getAnimations()` and set `currentTime` per frame.

Cards use `.is-popping` (badges, stamps, tiles, stickers), `.is-stamping`
(the stamp lands from 1.8x), `.is-sliding` (rows, strips). State classes do
the teaching: `.is-done` on a checklist row draws its tick, `.is-quiet` dims
the list rows not being spoken, `.is-filled` fills a slot or lights a tile,
`.is-done` / `.is-now` on timeline nodes.

The highlight swipe goes **behind** words: wrap them in
`<span class="k-mark-host">` and give the svg class `k-under`. Underlines,
circles and strikes go over them with `k-over` (see the "Marks on Hindi
words" block in `preview.html` for working markup).

Vendor icons (Tabler, Lucide) are stroked with `stroke="currentColor"`: set
`color:` on the wrapper. To draw one on, add `pathLength="1" class="draw"` to
its paths, as `build_kit.py`'s `tabler()` does. Phosphor icons are filled
outlines and can only pop.

## Skins

| skin | surface | heading / body | accents | radius, shadow | photo hint |
|---|---|---|---|---|---|
| night-hud | navy-black radial | Khand 600 / Poppins | gold #F5B82E, cyan #4FD1E8 | 6px, gold glow | colour, night grade |
| paper-editorial | cream #F1E9D8 | Noto Devanagari 900 at 62.5% width / Noto 500 | red #D7262E, navy #1F3A8A | 2px, hard 6px offset | duotone red |
| chalk-slate (new) | slate green-black | Kalam / Kalam (digits from Khand) | chalk yellow, chalk blue, coral warn | 12px dashed, none | mono |
| pastel-notebook (new) | ruled white page + margin rule | Poppins 600 / Poppins | blue pen, green pen, yellow highlighter | 20px, soft lift | colour |

A skin defines the core six (`--ink --accent --accent-2 --paper --muted
--stroke-w`) that every SVG reads, plus card variables (`--card-bg`,
`--card-border`, `--radius`, `--shadow`, `--badge-*`, `--pill-*`,
`--on-accent`, `--tape`, `--stamp`, `--highlight`, `--warn`), fonts
(`--font-head`, `--head-weight`, `--head-stretch`, `--font-body`,
`--font-num`, `--font-hand`) and the photo hint (`--photo-treatment`,
`--photo-filter`, `--photo-tint`, `--photo-blend`, applied by `.k-photo`).
A new skin is a copy of one file with new values.

## Rules the kit already follows

- No em or en dashes in any screen text.
- Counted things use digits (badges, section tags, slots, counter), never
  bullets or dashes.
- No decoration without a teaching job: no sparkles, flares or vignettes.
  `attention-burst` is plain radial strokes, for the one place the eye must go.
- Hindi lives in HTML text. Nothing here puts Devanagari in a formula.
- **✓ ⚠ → are drawn, never typed.** None of the repo fonts (Khand, Poppins,
  Noto Sans Devanagari, Kalam) has those glyphs, so typing them makes
  Chromium substitute a system face. The kit has SVGs for each.

## Devanagari: what was checked and what was fixed

The preview ends with a shaping line (`विद्युत् नियम क्षेत्रफल श्रृंखला
द्वितीय राष्ट्रीय कृषि`) in all five faces, in every skin. All render with
correct matra order and conjuncts.

**Bug found and fixed:** chalk-slate takes its digits from Khand through a
`unicode-range` face (`'Khand Digits'`, because Kalam's 1 reads as a slash).
When that face pointed at the same file URL as the regular `Khand` 600
face, Chromium shared the font resource and Khand lost its conjunct shaping
everywhere on the page: `क्षेत्रफल` showed a broken `त्‍र`, `श्रृंखला` and `राष्ट्रीय`
fell apart. Fixed by giving the digits face a distinct URL
(`Khand-SemiBold.ttf?digits-only`). Any template that adds a unicode-range
face over a file already in use must do the same.

Also fixed while reviewing the sheets: text on an accent fill was invisible
in chalk-slate (badge ink equals accent there), so cards now use
`--on-accent`; the callout label was crossing its own leader line; the
counter's slash collided with its label; the sticker vanished into the
night-hud background.

**Draw-on gotcha:** do not add `vector-effect: non-scaling-stroke` to these
paths. Chromium then computes the dash pattern in screen space while
`pathLength` stays in user space, so a scaled-up arrow draws on as a row of
dashes. Verified both ways on a paused-animation frame.

## Licences

| set | files | licence | credit |
|---|---|---|---|
| kit (svg, cards, skins, tools) | 32 svg + 22 cards + 4 skins | original (Arivihan) | none |
| Tabler Icons 3.49.0 | 5184 outline + 1054 filled | MIT | keep `vendor/tabler/LICENSE`; no on-screen credit |
| Lucide (lucide-static 1.53.0) | 2133 | ISC | keep `vendor/lucide/LICENSE` |
| Phosphor (@phosphor-icons/core 2.1.1) | 1512 x 4 weights (regular, bold, fill, duotone) | MIT | keep `vendor/phosphor/LICENSE` |
| Excalidraw libraries, converted to SVG | 36 (2 hand-drawn signs, 22 stick figures, 12 maths diagrams) | MIT (excalidraw-libraries repo; libraries are published there under MIT) | keep `vendor/excalidraw/LICENSE`; sources in `vendor/excalidraw/source/` |
| rough-notation 0.5.1 | 1 runtime lib | MIT | keep LICENSE |
| roughjs 4.6.6 | 1 runtime lib | MIT | keep LICENSE |

Cards that embed a Tabler icon say so in `manifest.json`. Nothing in the
library needs an on-screen credit.

Not collected, on purpose: Freepik, Flaticon, and SVG sites with unclear
terms; `Eronred/handy-arrows` (hand-drawn arrows, but the repo carries no
licence file, so its "MIT" claim cannot be verified); Open Doodles (CC0,
but lifestyle poses with no teaching job here, and only available as React
components); Lottie (LottieFiles needs a login and uses its own licence).
Phosphor's thin and light weights were dropped to stay inside the size cap,
and they disappear at 1080 wide anyway.

## Gaps

- **No real hand-drawn arrow pack.** The hand-drawn arrows, underlines,
  circle and box are generated by `build_kit.py` from a seeded wobble. For
  marks that must hug arbitrary text at runtime, `vendor/rough-notation`
  does it (MIT), but it is a script, not an asset.
- **Icons are generic.** No Indian-specific icons (temple uses a generic
  arch, parliament a bank building, rupee is fine). `cattle` resolves to the
  only cow there is, Phosphor's, which is filled and cannot draw on.
- **No subject diagrams.** Cell, atom, magnet and so on are icon-level only;
  teaching figures still come from the textbook scan, as the repo requires.
- **No Lottie or motion assets.** All motion is CSS or frame-driven.
- **Corner-tick SVG frame is fixed 3:2.** For any other aspect use the
  `.k-hud` card, whose ticks never stretch.
- **The kit has not been wired into a template yet.** The renderer still uses
  its own components; this is a library to pull from.
