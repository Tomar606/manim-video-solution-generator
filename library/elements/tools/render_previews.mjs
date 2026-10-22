// Render kit/preview.html once per skin to previews/<skin>.png (1080 wide,
// full page).  ONE Chromium, pages rendered one after another (8 GB box).
//
//   node library/elements/tools/render_previews.mjs [skin ...]
//
// Playwright is borrowed from tools/edu/renderer/node_modules; nothing is
// installed into the repo.
import { createRequire } from 'node:module';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const repo = path.resolve(here, '../../..');
const require = createRequire(path.join(repo, 'tools/edu/renderer/package.json'));
const { chromium } = require('playwright');

const skins = process.argv.slice(2).length ? process.argv.slice(2)
  : ['night-hud', 'paper-editorial', 'chalk-slate', 'pastel-notebook'];
const page_url = pathToFileURL(path.join(here, '../kit/preview.html')).href;
const out = path.join(here, '../previews');

const browser = await chromium.launch(process.env.CHROME_PATH ? { executablePath: process.env.CHROME_PATH } : {});
try {
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  const problems = [];
  page.on('console', m => { if (m.type() === 'error') problems.push(m.text()); });
  page.on('requestfailed', r => problems.push('failed: ' + r.url()));
  for (const skin of skins) {
    await page.goto(`${page_url}?skin=${skin}`);
    await page.waitForFunction('window.READY === true');
    // every face the page asked for must actually have loaded
    const faces = await page.evaluate(() => [...document.fonts].map(f => `${f.family} ${f.weight} ${f.status}`));
    const bad = faces.filter(f => !f.endsWith('loaded') && !f.endsWith('unloaded'));
    // text that overflows its box horizontally (clipped or spilling)
    const overflow = await page.evaluate(() => [...document.querySelectorAll('.demo *')]
      .filter(e => e.children.length === 0 && e.textContent.trim() && e.scrollWidth > e.clientWidth + 2 && getComputedStyle(e).overflow !== 'visible')
      .map(e => e.textContent.trim().slice(0, 30)));
    const file = path.join(out, `${skin}.png`);
    await page.screenshot({ path: file, fullPage: true });
    console.log(skin, '->', file, bad.length ? `BAD FONTS ${bad}` : 'fonts ok', overflow.length ? `OVERFLOW ${overflow}` : '');
  }
  if (problems.length) console.log('page problems:', problems);
} finally {
  await browser.close();
}
