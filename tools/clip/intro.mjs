/* intro.mjs — the opening card, STAGED IN rather than cut to.
 *
 *   node tools/clip/intro.mjs <slug> --dur 7.7     -> work/<slug>/out/intro.mp4 (1080x1344, opaque)
 *
 * Reads out/plate.png (tools/clip/plate_frame.mjs) and out/layers/*.png
 * (tools/clip/make_intro_layers.py). --dur is how long the card holds: the
 * moment the first explanation caption arrives, i.e. the end of segment 1.
 * Without --dur it is read from video.json's "intro_dur", and failing that from
 * the first segment of spec/segments_part1.json.
 *
 * make_intro_layers.py writes each element as its own full-frame RGBA png, and
 * this stacks them in the same headless browser full.mjs uses, driving each on
 * its own clock.
 *
 * WHY 1080x1344 AND OPAQUE, NOT A FULL-FRAME ALPHA VIDEO
 * The card is opaque down to the presenter's floor and does nothing below it,
 * so rendering only that band means no alpha codec and a third of the pixels.
 * H was raised from 1290 to 1344: the theme puts captions at y 1178-1330, so a
 * 1290-tall card left the bottom 40px of every caption showing beneath it.
 *
 * THE PLATE IS A FRAME OF THE RENDER, not the raw background png — see
 * plate_frame.mjs.
 */
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { parseArgs, videoDir, loadVideo, serve, launch, newPage, die, REPO,
         INTRO_PLAN, cardPoser } from './lib.mjs';

const FPS = 30, W = 1080, H = 1344;
const a = parseArgs();
const dir = videoDir(a._[0]);
const cfg = loadVideo(dir);
let DUR = a.dur != null ? Number(a.dur) : cfg.intro_dur;
if (DUR == null) {
  const s1 = path.join(dir, 'spec', 'segments_part1.json');
  if (fs.existsSync(s1)) DUR = JSON.parse(fs.readFileSync(s1, 'utf8'))[0].duration;
}
if (!(DUR > 0)) die('how long does the card hold? pass --dur <seconds> (the end of segment 1)');
const OUT = path.join(dir, 'out', 'intro.mp4');
for (const f of ['out/plate.png', 'out/layers/ring.png'])
  if (!fs.existsSync(path.join(dir, f)))
    die(`missing ${f} — run plate_frame.mjs and make_intro_layers.py first`);

const PLAN = INTRO_PLAN;          // shared with full.mjs --intro (lib.mjs)

const { server, port } = await serve(cfg);
const browser = await launch();
const page = await newPage(browser, W, H);
page.on('pageerror', e => console.error('PAGE ERROR:', e.message));

// page.setContent gives the document an about:blank base URL, so a relative or
// root-relative src never reaches the static server and every layer loads as a
// broken image - which renders as a completely black frame, silently.
const BASE = `http://127.0.0.1:${port}`;
const imgs = PLAN.map(([n]) =>
  `<img id="${n}" src="${BASE}/out/layers/${n}.png" width="1080" height="1920">`).join('\n');

await page.setContent(`<!doctype html><meta charset="utf-8">
<style>
  *{margin:0;padding:0}
  html,body{width:${W}px;height:${H}px;overflow:hidden;background:#000}
  #wrap{position:relative;width:1080px;height:1920px}
  #wrap img{position:absolute;left:0;top:0;transform-origin:50% 50%;opacity:0;will-change:transform,opacity}
  /* the plate is NOT animated and must never inherit the start-hidden rule
     above - it is the card's opaque background and is up from frame 0. The
     runbook is explicit: no fade IN, or the captions underneath show through. */
  #plate{opacity:1 !important;width:1080px;height:1920px}
</style>
<div id="wrap">
  <img id="plate" src="${BASE}/out/plate.png">
  ${imgs}
</div>`, { waitUntil: 'load' });

// decode() rather than complete: a broken image is also "complete". Assert every
// layer actually has pixels, or the render is black and nothing says why.
const loaded = await page.evaluate(async () => {
  await Promise.all([...document.images].map(i => i.decode().catch(() => {})));
  return [...document.images].map(i => [i.id || 'plate', i.naturalWidth]);
});
const broken = loaded.filter(([, w]) => !w);
if (broken.length) { console.error('layers failed to load:', broken.map(b => b[0]).join(', ')); process.exit(1); }
console.log(`${loaded.length} layers loaded`);

await page.evaluate(`(${cardPoser.toString()})(${JSON.stringify(PLAN)}, '')`);
await page.evaluate(() => { window.SET = window.CARD_SET; });

const ff = spawn('ffmpeg', [
  '-y', '-f', 'image2pipe', '-vcodec', 'mjpeg', '-r', String(FPS), '-i', 'pipe:0',
  '-c:v', 'libx264', '-pix_fmt', 'yuvj420p', '-color_range', 'pc',
  '-crf', '18', '-preset', 'medium', '-movflags', '+faststart', OUT
], { stdio: ['pipe', 'ignore', 'pipe'] });
let err = '';
ff.stderr.on('data', d => { err += d; });
const done = new Promise((res, rej) =>
  ff.on('close', c => c === 0 ? res() : rej(new Error(`ffmpeg ${c}\n${err.slice(-600)}`))));
const write = b => ff.stdin.write(b) ? Promise.resolve()
                                     : new Promise(r => ff.stdin.once('drain', r));

const n = Math.round(DUR * FPS);
for (let f = 0; f < n; f++) {
  await page.evaluate(t => window.SET(t), f / FPS);
  await write(await page.screenshot({ type: 'jpeg', quality: 95 }));
  if (f % 60 === 0) process.stdout.write(`\r  ${f}/${n}   `);
}
ff.stdin.end();
await done;
await browser.close(); server.close();
console.log(`\n${path.relative(REPO, OUT)} - ${W}x${H}, ${DUR}s, ${n} frames`);
