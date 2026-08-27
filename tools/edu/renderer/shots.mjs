// Stills at chosen moments, with the real background baked in, so the plan can
// be judged before paying for a render.
//
//   node shots.mjs 4:5.0 9:7.0 14:8.0     -> out/shot-4-5.png ...
//
// Each argument is <seg_id>:<seconds into that segment>.
import { chromium } from 'playwright';
import { createServer } from 'http';
import { readFile } from 'fs/promises';
import { extname, join } from 'path';

const ROOT = process.cwd();
const T = {'.html':'text/html','.js':'text/javascript','.css':'text/css','.json':'application/json',
  '.svg':'image/svg+xml','.png':'image/png','.woff2':'font/woff2','.woff':'font/woff','.ttf':'font/ttf'};
const server = createServer(async (rq,rs)=>{ try{
  const p = join(ROOT, decodeURIComponent(rq.url.split('?')[0]));
  const b = await readFile(p);
  rs.writeHead(200,{'Content-Type':T[extname(p)]||'application/octet-stream'}); rs.end(b);
}catch{ rs.writeHead(404); rs.end('nf'); }});
await new Promise(r=>server.listen(0,r));
const port = server.address().port;

const specs = JSON.parse(await readFile('spec/segments.json','utf8'));
const want = process.argv.slice(2).map(a => {
  const [id, t] = a.split(':');
  return { id: Number(id), t: Number(t ?? 1) };
});

const browser = await chromium.launch();
const out = [];
for (const { id, t } of want) {
  const i = specs.findIndex(s => s.seg_id === id);
  if (i < 0) { console.error(`no seg_id ${id}`); continue; }
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  page.on('pageerror', e => console.error(`SPEC ERROR seg ${id}: ${e.message}`));
  await page.goto(`http://localhost:${port}/renderer/index.html?headless=1&seg=${i}`,
                  { waitUntil: 'networkidle' });
  await page.waitForFunction(() => window.READY === true);
  await page.evaluate(bg => { const f = document.getElementById('frame');
    f.style.background = `#000 url('../${bg}') center/cover no-repeat`;
    document.body.style.background = '#000'; }, 'assets/chalk-background.png');
  await page.evaluate(t => window.RENDER.setTime(t), t);
  await page.waitForTimeout(350);
  const f = `out/review/shot-${id}-${String(t).replace('.', '_')}.png`;
  await page.screenshot({ path: f });
  await page.close();
  out.push(f);
}
await browser.close(); server.close();
console.log(out.join('\n'));
process.exit(0);
