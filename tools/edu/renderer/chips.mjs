// Render each overlay chip to a transparent PNG the size of the stage band.
//
//   node chips.mjs                 -> out/chips/<id>.png for every chip
//
// These go on top of a FINISHED video with one ffmpeg overlay pass, so they are
// cut to the band (1080x470) and carry no background of their own.
import { chromium } from 'playwright';
import { createServer } from 'http';
import { readFile, mkdir } from 'fs/promises';
import { extname, join } from 'path';

const ROOT = process.cwd();
const T = {'.html':'text/html','.js':'text/javascript','.css':'text/css','.json':'application/json',
  '.svg':'image/svg+xml','.png':'image/png','.woff2':'font/woff2','.woff':'font/woff','.ttf':'font/ttf'};
const server = createServer(async (rq, rs) => { try {
  const p = join(ROOT, decodeURIComponent(rq.url.split('?')[0]));
  const b = await readFile(p);
  rs.writeHead(200, {'Content-Type': T[extname(p)] || 'application/octet-stream'}); rs.end(b);
} catch { rs.writeHead(404); rs.end('nf'); }});
await new Promise(r => server.listen(0, r));
const port = server.address().port;

const CHIPS = ['p1-use', 'p1-principle', 'p1-inventor', 'p1-year',
               'p2-nh3', 'p2-complex', 'p2-pressure', 'p2-corrode',
               'p2-leak', 'p2-leakproof', 'p2-koh', 'p2-redox'];

await mkdir(join(ROOT, 'out', 'chips'), { recursive: true });
const browser = await chromium.launch();
for (const id of CHIPS) {
  const page = await browser.newPage({ viewport: { width: 1080, height: 470 } });
  page.on('pageerror', e => console.error(`${id}: ${e.message}`));
  await page.goto(`http://localhost:${port}/overlays/index.html?chip=${id}`,
                  { waitUntil: 'networkidle' });
  await page.waitForFunction(() => window.READY === true);
  await page.waitForTimeout(250);
  await page.locator('#band').screenshot({ path: `out/chips/${id}.png`,
                                           omitBackground: true });
  await page.close();
  console.log(`out/chips/${id}.png`);
}
await browser.close(); server.close(); process.exit(0);
