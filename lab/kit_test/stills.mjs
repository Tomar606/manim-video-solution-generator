// Render every still listed in a compiled timeline, one Chromium, one page at a time.
//   node lab/kit_test/stills.mjs out/<plan>
import { createRequire } from 'module';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';
const here = path.dirname(fileURLToPath(import.meta.url));
const require = createRequire(path.join(here, '../../tools/edu/renderer/package.json'));
const { chromium } = require('playwright');

const outDir = path.resolve(here, process.argv[2]);
const label = process.argv[3] || '';            // output folder name
const skin = process.argv[4] ?? (['night-hud','chalk-slate','pastel-notebook'].includes(label) ? label : '');
const shotDir = label ? path.join(outDir, label) : outDir;
fs.mkdirSync(shotDir, { recursive: true });
const tlRel = path.relative(here, path.join(outDir, 'timeline.js'));
const src = fs.readFileSync(path.join(outDir, 'timeline.js'), 'utf8');
const n = JSON.parse(src.replace(/^window\.TL = /, '').replace(/;\s*$/, '')).stills.length;
const browser = await chromium.launch({ args: ['--allow-file-access-from-files'] });
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
const reports = [];
page.on('pageerror', e => console.error('PAGE ERROR:', e.message));
for (let i = 0; i < n; i++) {
  await page.goto('file://' + path.join(here, 'stage.html') + `?tl=${encodeURIComponent(tlRel)}&still=${i}` + (skin ? `&skin=${skin}` : '') + (process.env.PLATE ? `&plate=${process.env.PLATE}` : '') + (process.env.PLACEHOLDER ? '&placeholder=1' : ''));
  await page.waitForFunction(() => document.title === 'ready');
  await page.evaluate(() => document.fonts.ready);
  await page.waitForFunction(() => [...document.images].every(im => im.complete));
  const rep = await page.evaluate(() => window.REPORT);
  reports.push(rep);
  await page.screenshot({ path: path.join(shotDir, `still_${String(i).padStart(2, '0')}.png`) });
  console.log(i, rep.t, rep.beat, rep.violations.length ? 'VIOLATIONS: ' + rep.violations.join('; ') : 'ok', 'caption@' + rep.caption_at);
}
fs.writeFileSync(path.join(shotDir, 'gate_report.json'), JSON.stringify(reports, null, 1));
await browser.close();
