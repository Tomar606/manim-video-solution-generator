/* full.mjs — render EVERY segment as ONE continuous video.
 *
 *   node full.mjs
 *
 * Differences from render.mjs (which makes 11 separate alpha .mov files):
 *   - background image is baked in, so there is no alpha channel to carry
 *   - frames are JPEG, not PNG  -> capture is several times faster
 *   - frames are piped straight into ffmpeg -> nothing large is left on disk
 *   - output is one H.264 mp4, tens of MB instead of gigabytes
 *
 * Result: out/full-video.mp4, 1080x1920, ready for the editor.
 * The only thing left to do there is drop the HeyGen avatar on top.
 */
import { chromium } from 'playwright';
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { serve } from './server.mjs';

const ROOT = path.dirname(fileURLToPath(import.meta.url));
const FPS = 30;
const BG = process.env.BG || 'assets/chalk-background.png';
const OUT = process.env.OUT
  ? path.resolve(ROOT, process.env.OUT)
  : path.join(ROOT, 'out', 'full-video.mp4');

let specs = JSON.parse(fs.readFileSync(path.join(ROOT, 'spec/segments.json'), 'utf8'));

/* optional: test a few segments first ->  node full.mjs 1,2  */
const pick = process.argv[2];
if (pick) {
  const want = new Set(pick.split(',').map(Number));
  specs = specs.filter(s => want.has(s.seg_id));
  if (!specs.length) { console.error(`no segments matched: ${pick}`); process.exit(1); }
  console.log(`TEST RUN — only segments ${[...want].join(', ')}`);
}
if (!fs.existsSync(path.join(ROOT, BG))) {
  console.error(`background not found: ${BG}`);
  console.error('put your background image there, or run:  BG=assets/your-file.png node full.mjs');
  process.exit(1);
}
fs.mkdirSync(path.join(ROOT, 'out'), { recursive: true });

const totalSec = specs.reduce((a, s) => a + s.duration, 0);
const totalFrames = Math.round(totalSec * FPS);
console.log(`${specs.length} segments, ${totalSec}s, ${totalFrames} frames`);
console.log(`background: ${BG}`);

const { server, port } = await serve(ROOT);
const browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined });
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });

await page.goto(`http://localhost:${port}/renderer/index.html?headless=1`, { waitUntil: 'networkidle' });
await page.waitForFunction(() => window.READY === true);

/* bake the background straight onto #frame */
await page.evaluate(bg => {
  const f = document.getElementById('frame');
  f.style.background = `#000 url('../${bg}') center/cover no-repeat`;
  document.body.style.background = '#000';
}, BG);

/* ffmpeg: JPEG frames in on stdin, one mp4 out */
const ff = spawn('ffmpeg', [
  '-y', '-f', 'image2pipe', '-vcodec', 'mjpeg', '-r', String(FPS), '-i', 'pipe:0',
  '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', '-preset', 'medium',
  '-movflags', '+faststart', OUT
], { stdio: ['pipe', 'ignore', 'pipe'] });

let ffErr = '';
ff.stderr.on('data', d => { ffErr += d; });
const ffDone = new Promise((res, rej) =>
  ff.on('close', c => c === 0 ? res() : rej(new Error(`ffmpeg exited ${c}\n${ffErr.slice(-800)}`))));

const write = buf => ff.stdin.write(buf) ? Promise.resolve()
                                         : new Promise(r => ff.stdin.once('drain', r));

const problems = [];
let done = 0;
const t0 = Date.now();

for (const seg of specs) {
  await page.evaluate(async s => {
    await window.RENDER.build(s);
    window.RENDER.setTime(0);
  }, seg);

  /* same text audit as render.mjs: what the spec promised must be on screen */
  const onScreen = await page.evaluate(() => {
    const out = [];
    document.querySelectorAll('#caption .phrase, #stage .lbl').forEach(e => out.push(e.textContent));
    document.querySelectorAll('#eq .katex-mathml annotation').forEach(e => out.push(e.textContent));
    return out;
  });
  const norm = s => s.replace(/\u2011/g, '-');
  const seen = onScreen.map(norm);
  const missing = [...(seg.phrases || []).map(p => p.text),
                   ...(seg.labels || []).map(l => l.text)]
                   .filter(t => !seen.includes(norm(t)));
  if (missing.length) problems.push(`seg ${seg.seg_id}: ${missing.join(' | ')}`);

  const n = Math.round(seg.duration * FPS);
  for (let f = 0; f < n; f++) {
    await page.evaluate(t => window.RENDER.setTime(t), f / FPS);
    await write(await page.screenshot({ type: 'jpeg', quality: 92 }));
    if (++done % 30 === 0) {
      const pct = (done / totalFrames * 100).toFixed(0);
      const eta = Math.round((Date.now() - t0) / done * (totalFrames - done) / 1000);
      process.stdout.write(`\r  ${pct}%  seg ${seg.seg_id}  ${done}/${totalFrames} frames  ~${eta}s left   `);
    }
  }
}

ff.stdin.end();
await ffDone;
await browser.close();
server.close();

const mb = (fs.statSync(OUT).size / 1048576).toFixed(1);
console.log(`\n\nout/full-video.mp4  —  ${totalSec}s, ${mb} MB, took ${Math.round((Date.now() - t0) / 1000)}s`);

if (problems.length) {
  console.error('\nTEXT MISMATCH — do not use this file:');
  problems.forEach(p => console.error('  ' + p));
  process.exitCode = 1;
} else {
  console.log('All text verified against the spec. Drop the HeyGen avatar on top and export.');
}
