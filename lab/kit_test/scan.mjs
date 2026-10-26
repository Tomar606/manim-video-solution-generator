// Every frame's layout report, without drawing a single PNG.
//   node lab/kit_test/scan.mjs <plan-stem>      (after compile.py)
// A stamp's slam-in starts oversized for ~0.1 s, so a 2-4 frame run on one
// stamp is that entrance; anything longer is a real overflow.
import { createRequire } from 'module'; import path from 'path'; import fs from 'fs'; import { fileURLToPath, pathToFileURL } from 'url';
const here = path.dirname(fileURLToPath(import.meta.url));
// this repo's own browser folder: a shared ~/Library/Caches/ms-playwright was emptied twice in one day by other
// Playwright installs and cache purges, killing renders mid-way (26 Oct 2026)
process.env.PLAYWRIGHT_BROWSERS_PATH ??= path.join(here, '../../tools/edu/renderer/.browsers');
const require = createRequire(path.join(here, '../../tools/edu/renderer/package.json'));
const { chromium } = require('playwright');
const outDir = path.join(here, 'out/' + process.argv[2]); const tlRel = path.relative(here, path.join(outDir, 'timeline.js')).split(path.sep).join('/');
const tl = JSON.parse(fs.readFileSync(path.join(outDir, 'timeline.js'), 'utf8').replace(/^window\.TL = /, '').replace(/;\s*$/, ''));
const b = await chromium.launch({ args: ['--allow-file-access-from-files'] }); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
await p.goto(pathToFileURL(path.join(here, 'stage.html')).href + `?tl=${encodeURIComponent(tlRel)}&render=1`);
await p.waitForFunction(() => document.title === 'ready'); await p.evaluate(() => document.fonts.ready);
for (let i = 0; i < Math.ceil(tl.duration * 30); i++) { const t = i / 30;
  const r = await p.evaluate(t => { window.renderAt(t); return window.REPORT; }, t);
  if (r.violations.length) console.log(t.toFixed(2), r.beat, r.violations.join('; ')); }
await b.close();
