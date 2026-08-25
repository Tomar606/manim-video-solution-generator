#!/usr/bin/env node
/* ============================================================
   Arivihan Truth Layer — renderer
   node render.mjs               -> all segments
   node render.mjs 2             -> only seg_id 2
   node render.mjs 2 --contact   -> also a 12-frame contact sheet for QC

   Output per segment (in out/):
     seg-2.mov   ProRes 4444 with alpha  -> drop straight into the editor
     seg-2.webm  VP9 with alpha          -> lighter, for web/preview
     seg-2-qc.png contact sheet          -> eyeball 12 moments in 2 seconds
   ============================================================ */

import { chromium } from 'playwright';
import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { serve } from './server.mjs';

const ROOT = path.dirname(fileURLToPath(import.meta.url));
const FPS = 30, W = 1080, H = 1920;
const only = process.argv[2] && !process.argv[2].startsWith('--') ? Number(process.argv[2]) : null;
const wantContact = process.argv.includes('--contact');

const specs = JSON.parse(fs.readFileSync(path.join(ROOT, 'spec/segments.json'), 'utf8'));
const targets = only ? specs.filter(s => s.seg_id === only) : specs;
if (!targets.length) { console.error(`no segment with seg_id ${only}`); process.exit(1); }

fs.mkdirSync(path.join(ROOT, 'out'), { recursive: true });

// CHROME_PATH lets you point at an existing Chrome/Chromium instead of
// Playwright's bundled one (useful on locked-down machines).
const { server, port } = await serve(ROOT);
const browser = await chromium.launch(
  process.env.CHROME_PATH ? { executablePath: process.env.CHROME_PATH } : {}
);

for (const seg of targets) {
  const i = specs.indexOf(seg);
  const tmp = path.join(ROOT, 'out', `.frames-${seg.seg_id}`);
  fs.rmSync(tmp, { recursive: true, force: true });
  fs.mkdirSync(tmp, { recursive: true });

  const page = await browser.newPage({ viewport: { width: W, height: H },
                                       deviceScaleFactor: 1 });
  page.on('pageerror', e => { console.error(`\n  SPEC ERROR in seg ${seg.seg_id}: ${e.message}`); process.exitCode = 1; });

  const url = `http://127.0.0.1:${port}/renderer/index.html?seg=${i}&headless=1`;
  await page.goto(url);
  await page.waitForFunction('window.READY === true', null, { timeout: 15000 });
  await page.evaluate(() => document.fonts.ready);

  /* ---- audit: what text actually exists in the DOM, verbatim ---- */
  const onScreen = await page.evaluate(() => {
    const out = [];
    document.querySelectorAll('#caption .phrase, #stage .lbl').forEach(e => out.push(e.textContent));
    document.querySelectorAll('#eq .katex-mathml annotation').forEach(e => out.push(e.textContent));
    return out;
  });
  const expected = [...(seg.phrases || []).map(p => p.text),
                    ...(seg.labels  || []).map(l => l.text)];
  // the engine swaps in U+2011 non-breaking hyphens so "d-block" / "(n-1)d"
  // never split across lines. Normalise both sides before comparing.
  const norm = s => s.replace(/\u2011/g, '-');
  const seen = onScreen.map(norm);
  const missing = expected.filter(t => !seen.includes(norm(t)));
  if (missing.length) { console.error(`  TEXT MISMATCH seg ${seg.seg_id}:`, missing); process.exitCode = 1; }

  /* ---- capture ---- */
  const total = Math.round(seg.duration * FPS);
  for (let f = 0; f < total; f++) {
    await page.evaluate(t => window.RENDER.setTime(t), f / FPS);
    await page.screenshot({ path: path.join(tmp, String(f).padStart(5, '0') + '.png'),
                            omitBackground: true });
    if (f % 30 === 0) process.stdout.write(`\r  seg ${seg.seg_id}: ${f}/${total} frames`);
  }
  process.stdout.write(`\r  seg ${seg.seg_id}: ${total}/${total} frames  `);

  const inPat = path.join(tmp, '%05d.png');
  const mov  = path.join(ROOT, 'out', `seg-${seg.seg_id}.mov`);
  const webm = path.join(ROOT, 'out', `seg-${seg.seg_id}.webm`);

  if (!process.env.SKIP_PRORES)
    execFileSync('ffmpeg', ['-y','-loglevel','error','-framerate',String(FPS),'-i',inPat,
      '-c:v','prores_ks','-profile:v','4444','-pix_fmt','yuva444p10le', mov]);
  execFileSync('ffmpeg', ['-y','-loglevel','error','-framerate',String(FPS),'-i',inPat,
    '-c:v','libvpx-vp9','-pix_fmt','yuva420p','-b:v','0','-crf','28', webm]);

  if (wantContact) {
    const step = Math.max(1, Math.floor(total / 12));
    execFileSync('ffmpeg', ['-y','-loglevel','error','-framerate',String(FPS),'-i',inPat,
      '-vf',`select='not(mod(n\\,${step}))',scale=360:-1,tile=4x3`,'-frames:v','1',
      path.join(ROOT,'out',`seg-${seg.seg_id}-qc.png`)]);
  }

  fs.rmSync(tmp, { recursive: true, force: true });
  await page.close();
  console.log('->', path.basename(mov));
}

await browser.close();
server.close();
console.log(process.exitCode ? '\nFinished WITH ERRORS — read above before using output.' : '\nAll segments clean.');
