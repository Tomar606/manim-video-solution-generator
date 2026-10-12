/* full.mjs — render EVERY segment of one part as ONE continuous video.
 *
 *   node tools/clip/full.mjs <slug> --part 1                 -> work/<slug>/out/render-part1.mp4
 *   node tools/clip/full.mjs <slug> --part 1 --pages 2       -> the same file, captured by two tabs
 *   node tools/clip/full.mjs <slug> --part 1 --intro         -> with the question card drawn in
 *   node tools/clip/full.mjs <slug> --part 1 --segs 3,4      -> just those segments (a test)
 *   node tools/clip/full.mjs <slug> --spec spec/x.json --out out/x.mp4
 *
 * Background baked in, frames as JPEG piped straight into ffmpeg: one H.264
 * mp4, 1080x1920, ready for tools/composite.py to key the presenter over.
 *
 * --pages N. Capture is the bottleneck, not the machine: one tab screenshots
 * one frame at a time and a 121s part used ~1.5 of 8 cores for 131s. So the
 * part is cut at a segment boundary into N runs of roughly equal frames, each
 * captured by its own tab into its own encoder, and the pieces are joined with
 * `-c copy` — no second encode. Each frame's time still comes from the part's
 * CUMULATIVE clock (below), so a piece boundary can never shift a frame.
 *
 * --intro. The question card is drawn by this same browser into the first
 * segment's frames (installCard in lib.mjs), instead of being rendered as its
 * own video and laid over this one by a second full ffmpeg pass. It needs
 * out/plate.png and out/layers/ (plate_frame.mjs, make_intro_layers.py), and
 * holds for segment 1 — the question, read aloud.
 *
 * Exit 1 if any string the spec promises is missing from the DOM — the text
 * audit — and the file is then named *.REJECTED.mp4 so nothing downstream can
 * pick it up by its usual name.
 */
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { parseArgs, videoDir, loadVideo, specOf, outPath, serve, launch, newPage,
         openEngine, bakePlate, textAudit, installCard, FPS, REPO, die } from './lib.mjs';

const a = parseArgs();
const dir = videoDir(a._[0]);
const cfg = loadVideo(dir);
const { rel: specRel, segs: specs } = specOf(dir, a);
const OUT = outPath(dir, a, a.part ? 'render' : 'full-video', '.mp4');
const PARTIAL = OUT.replace(/\.mp4$/, '.partial.mp4');
const PAGES = Math.max(1, Number(a.pages || 1));
fs.mkdirSync(path.dirname(OUT), { recursive: true });
if (a.segs) console.log(`TEST RUN — only segments ${a.segs}`);
if (a.intro && a.segs) die('--intro needs the whole part: the card holds for segment 1');

/* Every segment's frame span on the part's own clock. Segment length in
   frames comes from CUMULATIVE time, not from each segment's own duration:
   rounding each duration independently makes the roundings ADD UP — on
   CHE-C3-SA-04's spec that was 2.00 frames of drift by the end and a render
   0.053s shorter than the clip it has to sit under. Both edges from the
   running total means an error never exceeds half a frame. */
let elapsed = 0;
const spans = specs.map(seg => {
  const start = elapsed;
  const startF = Math.round(elapsed * FPS);
  elapsed += seg.duration;
  return { seg, start, startF, endF: Math.round(elapsed * FPS) };
});
const totalSec = elapsed;
const totalFrames = spans.length ? spans[spans.length - 1].endF : 0;
const cardDur = a.intro ? specs[0].duration : 0;

/* Cut into PAGES runs of consecutive segments with roughly equal frames. */
const runs = [];
{
  let cur = [], acc = 0;
  const per = totalFrames / PAGES;
  for (const s of spans) {
    cur.push(s);
    acc += s.endF - s.startF;
    if (runs.length < PAGES - 1 && acc >= per * (runs.length + 1)) { runs.push(cur); cur = []; }
  }
  if (cur.length) runs.push(cur);
}

console.log(`${specs.length} segments, ${totalSec.toFixed(2)}s, ${totalFrames} frames, ` +
            `${runs.length} tab(s)${a.intro ? `, question card for ${cardDur.toFixed(2)}s` : ''}`);
console.log(`spec: ${specRel}   background: ${cfg.background}`);

const { server, port } = await serve(cfg);
const browser = await launch();
const problems = [];
let done = 0;
const t0 = Date.now();

function encoder(file) {
  const ff = spawn('ffmpeg', [
    '-y', '-f', 'image2pipe', '-vcodec', 'mjpeg', '-r', String(FPS), '-i', 'pipe:0',
    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', '-preset', 'medium',
    '-movflags', '+faststart', file
  ], { stdio: ['pipe', 'ignore', 'pipe'] });
  let err = '';
  ff.stderr.on('data', d => { err += d; });
  const closed = new Promise((res, rej) =>
    ff.on('close', c => c === 0 ? res() : rej(new Error(`ffmpeg exited ${c}\n${err.slice(-800)}`))));
  const write = buf => ff.stdin.write(buf) ? Promise.resolve()
                                           : new Promise(r => ff.stdin.once('drain', r));
  return { write, end: () => { ff.stdin.end(); return closed; } };
}

async function capture(run, file) {
  const page = await newPage(browser);
  page.on('pageerror', e => problems.push(`page error: ${e.message}`));
  await openEngine(page, port, specRel);
  await bakePlate(page, cfg.background);
  const card = a.intro && run[0].startF === 0;
  if (card) await installCard(page, port, cardDur);
  const enc = encoder(file);
  for (const { seg, start, startF, endF } of run) {
    await page.evaluate(async s => {
      await window.RENDER.build(s);
      window.RENDER.setTime(0);
    }, seg);
    const missing = await textAudit(page, seg);
    if (missing.length) problems.push(`seg ${seg.seg_id}: ${missing.join(' | ')}`);
    for (let f = startF; f < endF; f++) {
      /* the time asked for is this frame's position measured from the SEGMENT
         start, so a segment that begins half a frame late still shows its own
         t=0 content on its first frame */
      const tg = f / FPS;
      await page.evaluate(({ t, tg, card }) => {
        window.RENDER.setTime(t);
        if (card) window.CARD(tg);
      }, { t: tg - start, tg, card });
      await enc.write(await page.screenshot({ type: 'jpeg', quality: 92 }));
      if (++done % 30 === 0) {
        const pct = (done / totalFrames * 100).toFixed(0);
        const eta = Math.round((Date.now() - t0) / done * (totalFrames - done) / 1000);
        process.stdout.write(`\r  ${pct}%  ${done}/${totalFrames} frames  ~${eta}s left   `);
      }
    }
  }
  await enc.end();
  await page.close();
}

const pieces = runs.length === 1 ? [PARTIAL]
             : runs.map((_, i) => OUT.replace(/\.mp4$/, `.piece${i}.mp4`));
await Promise.all(runs.map((run, i) => capture(run, pieces[i])));
await browser.close();
server.close();

if (pieces.length > 1) {
  /* join without re-encoding: every piece has the same size, rate and codec */
  const list = OUT.replace(/\.mp4$/, '.pieces.txt');
  fs.writeFileSync(list, pieces.map(p => `file '${p.replace(/'/g, "'\\''")}'`).join('\n') + '\n');
  await new Promise((res, rej) => {
    const ff = spawn('ffmpeg', ['-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', list,
                                '-c', 'copy', '-movflags', '+faststart', PARTIAL],
                     { stdio: ['ignore', 'ignore', 'pipe'] });
    let err = ''; ff.stderr.on('data', d => { err += d; });
    ff.on('close', c => c === 0 ? res() : rej(new Error(`concat failed\n${err}`)));
  });
  for (const p of [...pieces, list]) fs.rmSync(p, { force: true });
}

const took = Math.round((Date.now() - t0) / 1000);
if (problems.length) {
  const rejected = OUT.replace(/\.mp4$/, '.REJECTED.mp4');
  fs.renameSync(PARTIAL, rejected);
  console.error(`\n\nTEXT MISMATCH — ${path.relative(REPO, rejected)} is not usable:`);
  [...new Set(problems)].forEach(p => console.error('  ' + p));
  process.exitCode = 1;
} else {
  fs.renameSync(PARTIAL, OUT);
  const mb = (fs.statSync(OUT).size / 1048576).toFixed(1);
  console.log(`\n\n${path.relative(REPO, OUT)}  —  ${totalSec.toFixed(2)}s, ${mb} MB, took ${took}s`);
  console.log('All text verified against the spec.');
}
