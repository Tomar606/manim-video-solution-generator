#!/usr/bin/env node
/* The storyboard sheet: every segment at the moment it is most complete.
 *
 *   node tools/clip/sheet.mjs <slug> --part 1
 *     -> work/<slug>/out/tiles-part1/NN.png   one per segment
 *     -> work/<slug>/out/storyboard_part1.png the contact sheet a human approves
 *
 * Each tile carries the presenter's floor line (#frame.sheet in style.css) so
 * the sheet shows what the graphic may occupy and what belongs to him.
 *
 * The contact sheet used to be assembled by hand after the tiles, differently
 * each time (1490x1310 on one video, 2200x904 on the next). It is built here
 * now, with each tile headed by its segment, beat and absolute time span, so
 * the reviewer can say "segment 4 at 42s" and mean one thing.
 */
import fs from 'node:fs';
import path from 'node:path';
import { parseArgs, videoDir, loadVideo, specOf, outPath, serve, launch, newPage,
         openEngine, REPO } from './lib.mjs';

const a = parseArgs();
const dir = videoDir(a._[0]);
const cfg = loadVideo(dir);
const { rel: specRel, segs: specs } = specOf(dir, a);
const tiles = outPath(dir, a, 'tiles');
fs.rmSync(tiles, { recursive: true, force: true });   // stale tiles get reviewed as current
fs.mkdirSync(tiles, { recursive: true });
const sheetOut = path.join(dir, 'out', `storyboard${a.part ? `_part${a.part}` : ''}.png`);

/* The moment worth showing is after the LAST thing has arrived, not the middle
   of the segment: a counted list read at its midpoint is half a list. */
const showAt = s => {
  const ts = [
    ...(s.block?.items || []).map(i => i.t),
    ...(s.block?.lines || []).map(l => l.t ?? 0),
    ...(s.block?.cards || []).map(c => c.t),
    ...(s.diagram?.timeline || []).map(a => a.t + (a.dur ?? 0.45)),
    ...(s.labels || []).map(l => l.t_in),
    ...[].concat(s.equation?.highlight || []).map(h => h.t),
    // an equation that lands after the last label was shot before it arrived
    // (CHE-C3-SA-04's Eₐ tile showed only its heading)
    ...(s.equation ? [s.equation.t_in + 0.5] : []),
  ];
  const last = ts.length ? Math.max(...ts) : 0;
  return Math.min(s.duration - 0.4, last + 1.1);
};

const { server, port } = await serve(cfg);
const b = await launch();
const p = await newPage(b);
const errors = [];
p.on('pageerror', e => errors.push(e.message));

// the full spec, for absolute times — --segs may have narrowed `specs`
const all = JSON.parse(fs.readFileSync(path.join(dir, specRel), 'utf8'));
const startOf = new Map(); let t0 = 0;
for (const s of all) { startOf.set(s.seg_id, t0); t0 += s.duration; }

const made = [];
for (const s of specs) {
  const i = all.findIndex(x => x.seg_id === s.seg_id), t = showAt(s);
  await openEngine(p, port, specRel, i);
  await p.evaluate(() => document.getElementById('frame').classList.add('sheet'));
  await p.evaluate(t => window.RENDER.setTime(t), t);
  const out = path.join(tiles, String(s.seg_id).padStart(2, '0') + '.png');
  await p.screenshot({ path: out });
  const st = startOf.get(s.seg_id);
  made.push({ out, head: `${s.seg_id}  ${s.type}  ${st.toFixed(2)}-${(st + s.duration).toFixed(2)}s` });
  console.log(`  ${String(s.seg_id).padStart(2)}  ${s.type.padEnd(12)} t=${t.toFixed(2)}`);
}

/* the contact sheet: 4 across up to 8 tiles, 6 across beyond that */
const cols = made.length <= 8 ? 4 : 6, TW = 360, TH = 640, HEAD = 26, GAP = 10;
const rows = Math.ceil(made.length / cols);
const SW = cols * TW + (cols + 1) * GAP, SH = rows * (TH + HEAD) + (rows + 1) * GAP;
const sheet = await newPage(b, SW, SH);
const cells = made.map(m => `<figure><figcaption>${m.head}</figcaption>` +
  `<img src="data:image/png;base64,${fs.readFileSync(m.out).toString('base64')}"></figure>`).join('');
await sheet.setContent(`<!doctype html><meta charset="utf-8"><style>
  *{margin:0;padding:0;box-sizing:border-box}
  body{width:${SW}px;height:${SH}px;background:#0d0d0d;padding:${GAP}px;
       display:grid;grid-template-columns:repeat(${cols},${TW}px);gap:${GAP}px;align-content:start}
  figure{width:${TW}px;height:${TH + HEAD}px;background:#000}
  figcaption{height:${HEAD}px;line-height:${HEAD}px;padding:0 8px;font:500 12px/26px -apple-system,Helvetica,sans-serif;
             color:#F2C14E;white-space:pre}
  img{display:block;width:${TW}px;height:${TH}px}
</style>${cells}`, { waitUntil: 'load' });
await sheet.screenshot({ path: sheetOut });

await b.close(); server.close();
console.log(`\n${path.relative(REPO, sheetOut)}  (${made.length} tiles, ${SW}x${SH})`);
if (errors.length) {
  console.error('SPEC ERRORS:'); errors.forEach(e => console.error('  ' + e));
  process.exitCode = 1;
}
