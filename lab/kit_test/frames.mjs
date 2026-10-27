// The graphics layer of a whole part: one transparent PNG per frame.
//   node lab/kit_test/frames.mjs out/<plan> [fps]
// One Chromium, one page, seek-based: window.renderAt(t) redraws the frame for
// time t from the timeline alone.  A frame whose DOM is identical to the one
// before it is not screenshotted again; it is hard-linked, which is most of a
// video (a panel that has finished arriving does not change for seconds).
import { createRequire } from 'module';
import path from 'path';
import fs from 'fs';
import { fileURLToPath, pathToFileURL } from 'url';
const here = path.dirname(fileURLToPath(import.meta.url));
// this repo's own browser folder: a shared ~/Library/Caches/ms-playwright was emptied twice in one day by other
// Playwright installs and cache purges, killing renders mid-way (26 Oct 2026)
process.env.PLAYWRIGHT_BROWSERS_PATH ??= path.join(here, '../../tools/edu/renderer/.browsers');
const require = createRequire(path.join(here, '../../tools/edu/renderer/package.json'));
const { chromium } = require('playwright');

const outDir = path.resolve(here, process.argv[2]);
const fps = +(process.argv[3] || 30);
const frameDir = path.join(outDir, 'frames');
// RANGES="a:b,c:d" draws only those frames (a partial re-render) and leaves the rest of the folder alone
const ranges = process.env.RANGES ? process.env.RANGES.split(',').map(r => r.split(':').map(Number)) : null;
if (!ranges) fs.rmSync(frameDir, { recursive: true, force: true });
fs.mkdirSync(frameDir, { recursive: true });
const tlRel = path.relative(here, path.join(outDir, 'timeline.js')).split(path.sep).join('/');
const tl = JSON.parse(fs.readFileSync(path.join(outDir, 'timeline.js'), 'utf8').replace(/^window\.TL = /, '').replace(/;\s*$/, ''));
const n = Math.ceil(tl.duration * fps);

const browser = await chromium.launch({ args: ['--allow-file-access-from-files'] });
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
page.on('pageerror', e => console.error('PAGE ERROR:', e.message));
await page.goto(pathToFileURL(path.join(here, 'stage.html')).href + `?tl=${encodeURIComponent(tlRel)}&render=1`);
await page.waitForFunction(() => document.title === 'ready');
await page.evaluate(() => document.fonts.ready);

let prev = null, prevFile = null, shot = 0, violations = 0;
const t0 = Date.now();
for (const [ra, rb] of ranges || [[0, n]]) { prev = null;
for (let i = ra; i < Math.min(rb, n); i++) {
  const t = i / fps;
  const sig = await page.evaluate(t => { window.renderAt(t); return document.getElementById('frame').innerHTML; }, t);
  const file = path.join(frameDir, `g_${String(i).padStart(5, '0')}.png`);
  // a re-run over a range that partly exists (a chunk that died mid-way) must replace, not fail on EEXIST
  if (sig === prev) { fs.rmSync(file, { force: true }); fs.linkSync(prevFile, file); continue; }
  await page.waitForFunction(() => [...document.images].every(im => im.complete));
  const rep = await page.evaluate(() => window.REPORT);
  if (rep.violations.length) { violations++; if (violations < 6) console.log(`  ${t.toFixed(2)}s ${rep.beat}: ${rep.violations.join('; ')}`); }
  await page.screenshot({ path: file + '.tmp.png', omitBackground: true });
  fs.renameSync(file + '.tmp.png', file);          // appears whole: a compositor may be reading right behind
  prev = sig; prevFile = file; shot++;
  if (i % 300 === 0) console.log(`  ${i}/${n} frames, ${shot} drawn, ${((Date.now() - t0) / 1000).toFixed(0)}s`);
}
}
await browser.close();
console.log(`done: ${n} frames, ${shot} drawn, ${violations} frames with layout violations, ${((Date.now() - t0) / 1000).toFixed(0)}s`);
