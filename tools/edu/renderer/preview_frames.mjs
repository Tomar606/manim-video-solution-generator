/* preview_frames.mjs — grab a handful of still PNGs per segment via Playwright,
 * no ffmpeg needed. For eyeballing the whole video before a real render.
 *   node preview_frames.mjs            3 frames/segment (15%, 50%, 85%)
 */
import { chromium } from 'playwright';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { serve } from './server.mjs';

const ROOT = path.dirname(fileURLToPath(import.meta.url));
const specs = JSON.parse(fs.readFileSync(path.join(ROOT, 'spec/segments.json'), 'utf8'));
const outDir = path.join(ROOT, 'out', 'preview');
fs.mkdirSync(outDir, { recursive: true });

const { server, port } = await serve(ROOT);
const browser = await chromium.launch(process.env.CHROME_PATH ? { executablePath: process.env.CHROME_PATH } : {});
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 0.5 });
page.on('pageerror', e => console.error('SPEC ERROR:', e.message));

for (let i = 0; i < specs.length; i++) {
  const seg = specs[i];
  await page.goto(`http://127.0.0.1:${port}/renderer/index.html?seg=${i}&headless=1`);
  await page.waitForFunction('window.READY === true');
  await page.evaluate(() => document.fonts.ready);
  for (const frac of [0.15, 0.5, 0.85]) {
    const t = +(seg.duration * frac).toFixed(2);
    await page.evaluate(t => window.RENDER.setTime(t), t);
    const out = path.join(outDir, `seg${String(seg.seg_id).padStart(2, '0')}-${seg.type}-t${t}.png`);
    await page.screenshot({ path: out });
    console.log(out);
  }
}

await browser.close();
server.close();
