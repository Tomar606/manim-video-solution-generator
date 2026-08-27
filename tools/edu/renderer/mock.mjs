// Full-frame mocks: background + caption + photo card, before anything renders.
//
//   node mock.mjs mocks.json          -> out/mock-<slug>.png (1080x1920)
//
// mocks.json: [{slug, photo, cap, gold, tag}] where `photo` is a path relative
// to the renderer folder. The presenter is keyed on separately.
import { chromium } from 'playwright';
import { createServer } from 'http';
import { readFile, mkdir } from 'fs/promises';
import { extname, join } from 'path';

// Serve the REPO ROOT, not the renderer folder: the photographs live under
// projects/<slug>/assets/, which is outside the renderer and cannot be
// reached with `../` from a page the renderer serves.
const ROOT = join(process.cwd(), '..', '..', '..');
const T = {'.html':'text/html','.js':'text/javascript','.css':'text/css','.json':'application/json',
  '.svg':'image/svg+xml','.png':'image/png','.jpg':'image/jpeg','.woff2':'font/woff2','.ttf':'font/ttf'};
const server = createServer(async (rq, rs) => { try {
  const p = join(ROOT, decodeURIComponent(rq.url.split('?')[0]));
  const b = await readFile(p);
  rs.writeHead(200, {'Content-Type': T[extname(p)] || 'application/octet-stream'}); rs.end(b);
} catch { rs.writeHead(404); rs.end('nf'); }});
await new Promise(r => server.listen(0, r));
const port = server.address().port;

const mocks = JSON.parse(await readFile(process.argv[2], 'utf8'));
await mkdir(join(ROOT, 'out', 'review'), { recursive: true });
const browser = await chromium.launch();
for (const m of mocks) {
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  page.on('pageerror', e => console.error(`${m.slug}: ${e.message}`));
  const qs = new URLSearchParams({ photo: m.photo, cap: m.cap || '',
                                   gold: m.gold || '', tag: m.tag || '',
                                   el: m.el || '' });
  await page.goto(`http://localhost:${port}/tools/edu/renderer/overlays/mock.html?${qs}`,
                  { waitUntil: 'networkidle' });
  await page.waitForFunction(() => window.READY === true);
  await page.waitForTimeout(200);
  await page.screenshot({ path: `out/review/mock-${m.slug}.png` });
  await page.close();
  console.log(`out/mock-${m.slug}.png`);
}
await browser.close(); server.close(); process.exit(0);
