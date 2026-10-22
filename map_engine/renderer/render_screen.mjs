/**
 * A non-map data screen: a spec JSON in, an MP4 out.
 *
 *   node map_engine/renderer/render_screen.mjs spec.json --output out.mp4
 *
 * Same shape as render_map.mjs — Chromium draws the frames (it shapes
 * Devanagari), JPEG is piped into ffmpeg, nothing large is left on disk.
 */
import { chromium } from 'playwright';
import { createServer } from 'http';
import { readFile, mkdir } from 'fs/promises';
import { spawn } from 'child_process';
import { extname, join, resolve, dirname } from 'path';
import { parse } from 'yaml';

const ENGINE = resolve(dirname(new URL(import.meta.url).pathname), '..');
const REPO = resolve(ENGINE, '..');
const argv = process.argv.slice(2);
const flag = (n, d) => { const i = argv.indexOf('--' + n); return i >= 0 ? argv[i + 1] : d; };
const specPath = argv.find(a => !a.startsWith('--') &&
  (argv.indexOf(a) === 0 || !argv[argv.indexOf(a) - 1].startsWith('--')));
if (!specPath) { console.error('usage: render_screen.mjs <spec.json> [--output ...]'); process.exit(2); }

const W = +flag('width', 1080), H = +flag('height', 1920), FPS = +flag('fps', 30);
const OUT = resolve(flag('output', join(ENGINE, 'output', 'screen.mp4')));
const theme = parse(await readFile(join(ENGINE, `themes/${flag('theme','textbook')}.yaml`), 'utf8'));
const spec = JSON.parse(await readFile(resolve(specPath), 'utf8'));

if (!(spec.duration > 0)) { console.error('spec needs a positive duration'); process.exit(1); }
for (const [i, it] of (spec.items || []).entries()) {
  if (it.at !== undefined && (it.at < 0 || it.at > spec.duration)) {
    console.error(`item[${i}] "${it.text ?? it.type}": at ${it.at}s is outside the ${spec.duration}s screen`);
    process.exit(1);
  }
}

const TYPES = { '.html':'text/html', '.js':'text/javascript', '.json':'application/json',
                '.png':'image/png', '.css':'text/css', '.ttf':'font/ttf' };
const server = createServer(async (rq, rs) => {
  try {
    const p = join(REPO, decodeURIComponent(rq.url.split('?')[0]));
    const b = await readFile(p);
    rs.writeHead(200, { 'Content-Type': TYPES[extname(p)] || 'application/octet-stream' });
    rs.end(b);
  } catch { rs.writeHead(404); rs.end('nf'); }
});
await new Promise(r => server.listen(0, r));
const port = server.address().port;

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
page.on('pageerror', e => console.error('page: ' + e.message));
await page.goto(`http://localhost:${port}/map_engine/renderer/screen.html`, { waitUntil: 'domcontentloaded' });
await page.evaluate(c => window.SCREEN.setup(c),
  { width: W, height: H, theme, frame: theme.frame });
await page.waitForFunction(() => window.SCREEN_READY === true, null, { timeout: 30000 });

const total = Math.round(spec.duration * FPS);
await mkdir(dirname(OUT), { recursive: true });
const ff = spawn('ffmpeg', ['-y','-f','image2pipe','-r',String(FPS),'-i','-',
  '-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-r',String(FPS),OUT],
  { stdio: ['pipe','ignore','pipe'] });
let ffErr = ''; ff.stderr.on('data', d => (ffErr += d));
const done = new Promise((res, rej) => ff.on('close',
  c => c === 0 ? res() : rej(new Error(`ffmpeg exited ${c}\n${ffErr.slice(-700)}`))));
const write = b => new Promise(r => ff.stdin.write(b) ? r() : ff.stdin.once('drain', r));

console.log(`  ${spec.id}: ${spec.duration}s, ${total} frames, ${W}x${H} @${FPS}`);
for (let i = 0; i < total; i++) {
  await page.evaluate(st => window.SCREEN.frame(st), { t: i / FPS, spec });
  await write(await page.screenshot({ type: 'jpeg', quality: 92 }));
  if (i % 30 === 0 || i === total - 1) process.stdout.write(`\r  ${Math.round((i+1)/total*100)}%   `);
}
ff.stdin.end(); await done; await browser.close(); server.close();
console.log(`\n  -> ${OUT}`);
process.exit(0);
