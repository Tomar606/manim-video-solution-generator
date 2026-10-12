/* plate_frame.mjs — one frame of the bare plate, captions removed.
 *
 *   node tools/clip/plate_frame.mjs <slug>          -> work/<slug>/out/plate.png
 *
 * The intro card is drawn on the plate so it can cover the baked-in captions,
 * and the plate has to be EXACTLY what the render shows — style.css can lay a
 * radial scrim over the top 960px, so the raw PNG may be visibly lighter.
 *
 * This used to be lifted from the finished video at a moment when no caption
 * was up. Once captions were made to hold through every pause there is no such
 * moment left, so the frame is rendered here instead: same browser, same CSS,
 * same scrim, same background — with the caption element emptied.
 *
 * Writes out/plate.png directly (the old copies wrote plate-frame.png and every
 * build log then ran `cp out/plate-frame.png out/plate.png` by hand).
 */
import path from 'node:path';
import fs from 'node:fs';
import { parseArgs, videoDir, loadVideo, serve, launch, newPage, bakePlate, REPO } from './lib.mjs';

const a = parseArgs();
const dir = videoDir(a._[0]);
const cfg = loadVideo(dir);
const out = a.out ? path.resolve(dir, a.out) : path.join(dir, 'out', 'plate.png');
fs.mkdirSync(path.dirname(out), { recursive: true });

// Any segment will do — it is built only to be emptied. An empty spec is
// written to the page directly so this runs before any spec exists: the intro
// card can be made while the clip is still being transcribed.
const { server, port } = await serve(cfg);
const b = await launch();
const p = await newPage(b);
await p.route('**/__plate_spec.json', r => r.fulfill({ contentType: 'application/json',
  body: JSON.stringify([{ seg_id: 0, type: 'quiet', duration: 2, phrases: [] }]) }));
await p.goto(`http://127.0.0.1:${port}/renderer/index.html?headless=1&spec=__plate_spec.json`,
             { waitUntil: 'networkidle' });
await p.waitForFunction(() => window.READY === true);
await bakePlate(p, cfg.background);
await p.evaluate(() => {
  window.RENDER.setTime(1.0);
  document.getElementById('caption').innerHTML = '';   // the plate, and nothing else
  document.getElementById('stage').innerHTML = '';
});
await p.evaluate(() => document.fonts.ready);
await p.screenshot({ path: out });
await b.close(); server.close();
console.log(path.relative(REPO, out));
