/* frames.mjs — preview stills with the plate baked in, i.e. what the student sees.
 *
 *   node tools/clip/frames.mjs <slug> --part 1 3:12.0 4:14.0      -> out/frame-p1-3-12.png …
 *   node tools/clip/frames.mjs <slug> --part 1 --alpha 3:12.0     -> transparent, no plate
 *
 * Use this while tuning timing — seconds instead of a full render. Stills are
 * named per part so a still of part 2 can never be reviewed as part 1's.
 */
import fs from 'node:fs';
import path from 'node:path';
import { parseArgs, videoDir, loadVideo, specOf, serve, launch, newPage,
         openEngine, bakePlate, die } from './lib.mjs';

const a = parseArgs();
const dir = videoDir(a._[0]);
const cfg = loadVideo(dir);
const { rel: specRel, segs: specs } = specOf(dir, a);
const wants = a._.slice(1).map(x => { const [s, t] = x.split(':'); return { sid: +s, t: +t }; });
if (!wants.length || wants.some(w => Number.isNaN(w.sid) || Number.isNaN(w.t)))
  die('usage: node tools/clip/frames.mjs <slug> --part N <seg>:<t> ...');
fs.mkdirSync(path.join(dir, 'out'), { recursive: true });

const { server, port } = await serve(cfg);
const b = await launch();
const p = await newPage(b);
p.on('pageerror', e => console.error('SPEC ERROR:', e.message));
await openEngine(p, port, specRel);
if (!a.alpha) await bakePlate(p, cfg.background);

for (const { sid, t } of wants) {
  const seg = specs.find(s => s.seg_id === sid);
  if (!seg) { console.error(`no seg ${sid}`); process.exitCode = 1; continue; }
  await p.evaluate(async s => { await window.RENDER.build(s); window.RENDER.setTime(0); }, seg);
  await p.evaluate(() => document.fonts.ready);
  await p.evaluate(tt => window.RENDER.setTime(tt), t);
  const out = path.join(dir, 'out', `frame-${a.part ? `p${a.part}-` : ''}${sid}-${t}.png`);
  await p.screenshot({ path: out, omitBackground: !!a.alpha });
  console.log(out);
}
await b.close(); server.close();
