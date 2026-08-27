// Render each band chip to a transparent 1080x470 PNG for burn_chips.py.
//
//   node bands.mjs chips.json out/chips/sank
//
// chips.json is a list of {slug, ...params} where the params are whatever
// overlays/band.html takes for that mode. Everything is served from the REPO
// ROOT so a chip can reference a project's own photographs.
import { chromium } from 'playwright';
import { createServer } from 'http';
import { readFile, mkdir } from 'fs/promises';
import { extname, join } from 'path';

const T = {'.html':'text/html','.js':'text/javascript','.css':'text/css','.json':'application/json',
  '.svg':'image/svg+xml','.png':'image/png','.jpg':'image/jpeg','.woff2':'font/woff2','.ttf':'font/ttf'};
const ROOT = join(process.cwd(), '..', '..', '..');
const server = createServer(async (rq, rs) => { try {
  const p = join(ROOT, decodeURIComponent(rq.url.split('?')[0]));
  const b = await readFile(p);
  rs.writeHead(200, {'Content-Type': T[extname(p)] || 'application/octet-stream'}); rs.end(b);
} catch { rs.writeHead(404); rs.end('nf'); }});
await new Promise(r => server.listen(0, r));
const port = server.address().port;

const chips = JSON.parse(await readFile(process.argv[2], 'utf8'));
const outDir = process.argv[3] || 'out/chips';
await mkdir(outDir, { recursive: true });

const browser = await chromium.launch();
for (const c of chips) {
  const { slug, ...params } = c;
  const page = await browser.newPage({ viewport: { width: 1080, height: 470 } });
  page.on('pageerror', e => console.error(`${slug}: ${e.message}`));
  page.on('console', m => { if (m.type() === 'error') console.error(`${slug}: ${m.text()}`); });
  const qs = new URLSearchParams(Object.fromEntries(
    Object.entries(params).map(([k, v]) => [k, String(v)])));
  await page.goto(`http://localhost:${port}/tools/edu/renderer/overlays/band.html?${qs}`,
                  { waitUntil: 'networkidle' });
  await page.waitForFunction(() => window.READY === true, null, { timeout: 20000 })
            .catch(() => console.error(`${slug}: never became ready`));
  await page.waitForTimeout(200);
  await page.locator('#band').screenshot({ path: `${outDir}/${slug}.png`,
                                           omitBackground: true });
  await page.close();
  console.log(`${outDir}/${slug}.png`);
}
await browser.close(); server.close(); process.exit(0);
