# kit.mjs — the look of POL-C3-LA-02, used by part1/2/3.mjs

Functions run in Node, return an HTML string and REGISTER their timing, sound cue and line state.
`stage()` puts it all in one page; `cli()` renders it. Signatures are frozen: the kit only grows.

```js
import { load, stage, cli, browser, line, pips, heading, slip, stamp, text, box, wash } from './kit.mjs';
const { S, at, scope, dur } = load(2);               // scenes_part2.json + the word clock
line.start({ ink: '2002', pencil: 1, named: ['1990', '2002'], title: true, mode: 'strip' });
let H = pips({ at: 0, out: null, filled: 2, fill: [null, null, at('s2', 'जन-आंदोलन')] });
let s = scope('s2');                                 // from here `out` defaults to s2's end
H += heading({ n: 3, year: 'अप्रैल 2006', text: 'जन-आंदोलन', ink: 'blue', at: s.at('अगला'),
               atYear: s.at('अप्रैल'), atText: s.at('जन-आंदोलन'), x: 70, y: 330 });
H += slip({ text: '= जनता का देशव्यापी आंदोलन', at: s.at('यानी'), x: 90, y: 700 });
line.name('2006', s.at('2006')); wash('blue', s.t0, s.t1);
await cli({ html: stage({ html: H, part: 2, css: '', js: browser(function (T) { window.frame = t => {}; }, {}) }), part: 2, dur });
```
`node partN.mjs` layers (under, mask, overlay) -> out/layers/pN/ · `--stills 3.1,9 [--layer preview] [--full]`
half-size PNGs -> out/stills/pN/ · `--cues` -> out/cues_pN.json · `--sheet` -> out/stills/pN/sheet_pN.png

## Time
- `load(part)` -> `{S, K, at(sceneId, phrase, {nth, end}), scope(sceneId), dur, spec}`. `at` throws if he does not say it in that scene.
- `scope('s3')` -> `{t0, t1, len, shots, at(phrase, o)}` and makes s3's end the default `out`.
- Every component takes `at` (seconds, from the clock) and `out`: omitted = end of the current scope,
  `null` = holds to the end of the part. Items fade out over the 0.2 s before `out`.
- Common options: `x, y, w, h` (px), `cx: true` (centred), `right`, `ink: 'ink'|'red'|'blue'`, `id`, `fx`, `rot`, `style`, `cls`, `cue: false`.
- fx: `none fade press slam slideL slideR slideU slideD pop wipe draw`.

## Components (each returns HTML; concatenate into `html`)
- `heading({n, year, text, ink, at, atYear, atText, size})` poster heading; each piece presses in at its own time. `size: 'band'` = one row ~100 px tall for the band y 1040-1175.
- `slip({text, at, from: 'L'|'R'|'U'|'D', size})` pinned margin note (Mukta 44). `<b class="red">` inside colours a word.
- `stamp({text, ink, at, size, rot})` rubber stamp, slams in.
- `pips({at, filled, fill: [t|null x6], inks, x, y, size})` six point-pips; default place is the strip's top right (824, 66).
- `skeleton({at: [t, t, t], ticks: [t|null x3], done: [bool x3], arrow: {i, at}, x, y, w})` पृष्ठभूमि · छह points · भारत की भूमिका.
- `plate({title, name, ink, at})` type-only name plate. `card({html | parts: [{html, at}], label, at, w})` exam line in Tiro.
- `tiles({at, items: [{html, at, ink, sub}], cols, th, gap, size, count, x, y, w})` empty slots that fill, with "2 / 3".
- `text({html, at, size, font: 'head'|'body'|'serif', ink, wrap})` · `box(html, {at, ...})` any HTML of yours on the timeline.
- `sym(name, {size, ink, at?})`, `crown()`, `book()`: flat symbols (crown book tick cross people). Inline SVG unless `at` is given.
- `arrow({x1, y1, x2, y2, ink, at, sw, dash})` draws on in 0.3 s; `arrow({size})` is an inline "→" glyph (Khand has no arrow).
- `img({file, at, x, y, w, h})` a picture. `map({at, labels: {nepal: t, india: t}})` assets/map.png in the picture window with its two name plates; `mapPt('nepal'|'india'|'kathmandu'|'delhi')` -> frame `{x, y}`.
- `wash(ink, t0, t1, {a, edge})` the page goes red / blue (flat tint + page edge, in the under layer).
- `cue(kind, t, dur)` kinds: slide stamp scratch tick flip drop. Components record their own; add one for bespoke moves.
- `item(id, {at, out, fx, d, rot, len})` puts an element you wrote yourself on the timeline (class `it` or `sub`).

## THE LINE (`line`, chainable)
Points: `start 1990 peak edge 2002 floor 2006 sabha 2008 2015` (or a number 0..1). Colour and height are built in.
- `line.start({ink, pencil, named: [...], title, mode})` the state at t=0 (part 2: ink '2002'; part 3: ink '2015', all named).
- `line.mode(t, 'strip'|'full'|'mid'|'off'|{x, y, w, h, ...})` where it sits from cut t (0.5 s glide). `strip(t)`, `lineFull(t)` are shorthands.
  strip = y 60-250; full = plot y 560-1080 (he is hidden or small); mid = plot y 400-670 (he is large).
- `line.pencil(to, t, d)` dotted route · `line.ink(to, t, d, {drop, ease})` the inked line advances · `line.name('2006', t)` the dot gets its number.
- `line.title(t)` · `line.stop(t0, t1)` red bar रुक गई · `line.wobble(t0, t1)` · `line.mark('sabha', t, {label})` · `line.glow(pt, t)` · `line.clear(t)`.
- `line.pt('2002', 'full')` -> static `{x, y}` for placing your own drawings; in the browser `linePoint(u, t)`.

## Page and layers
`stage({html, css, js, part})`. Layers: `under` (opaque paper, hole at the picture window while a shot runs, shutter, wash),
`mask` (white = presenter shows), `overlay` (everything above), `preview` (all of it + his still; checking only).
Shots, presenter states and cuts are read from scenes_partN.json; you do nothing for them.
`browser(fn, data)` wraps bespoke browser code. In scope: `$ clamp P(t,a,b) env(t,a,b,din,dout) eout ein eio eback lerp f1 f2 f3 mix COL SC sceneAt linePoint`.
Set `window.frame = t => {...}` (overlay) or `window.frameUnder`. Draw as a pure function of t, through style/attributes only.

## Rules the kit cannot enforce
- Only frames whose DOM changed are written, as PNGs: no continuous motion, keep moving regions small, no soft shadows.
- Free zones (look.json `place`): you = y 280-800; explain = picture window y 300-1020 when no shot, band y 1040-1175,
  left column x 40-400 y 1200-1640; small = above y 1380. Nothing below y 1660. Text >= 40 px.
- Red = राजा/राजशाही, blue = जनता/लोकतंत्र, ink = neutral. Cream text only on a solid block.
- Fonts: Khand (headings, years), Mukta 800 (body), Tiro (exam line). All three shape this video's conjuncts correctly.
