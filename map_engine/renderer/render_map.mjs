/**
 * The CLI: a scene file in, an MP4 out.
 *
 *   node map_engine/renderer/render_map.mjs map_engine/scenes/1857_meerut_delhi.yaml \
 *        --output map_engine/output/1857.mp4 --width 1080 --height 1920 --fps 30
 *
 * Frames are JPEG and are piped straight into ffmpeg, the same shape as
 * tools/edu/renderer/full.mjs — capture is several times faster than PNG and
 * nothing large is left on disk, which matters on a machine that has had a
 * build die of a full disk.
 */
import { chromium } from 'playwright';
import { createServer } from 'http';
import { readFile, mkdir } from 'fs/promises';
import { spawn } from 'child_process';
import { extname, join, resolve, dirname } from 'path';
import { parse } from 'yaml';
import { loadScene, loadLocations, SceneError } from './lib/scene.mjs';
import { makeTimeline } from './lib/timeline.mjs';
import { fitBounds } from './lib/camera.mjs';

const ENGINE = resolve(dirname(new URL(import.meta.url).pathname), '..');
const REPO = resolve(ENGINE, '..');

const argv = process.argv.slice(2);
const flag = (n, d) => { const i = argv.indexOf('--' + n);
  return i >= 0 ? argv[i + 1] : d; };
const has = n => argv.includes('--' + n);
const scenePath = argv.find(a => !a.startsWith('--') &&
  (argv.indexOf(a) === 0 || !argv[argv.indexOf(a) - 1].startsWith('--')));
if (!scenePath) { console.error('usage: render_map.mjs <scene.yaml> [--output ...]'); process.exit(2); }

const W = +flag('width', 1080), H = +flag('height', 1920), FPS = +flag('fps', 30);
const themeName = flag('theme', 'textbook');
const OUT = resolve(flag('output', join(ENGINE, 'output', 'map.mp4')));
const DEBUG = has('debug');

const theme = parse(await readFile(join(ENGINE, `themes/${themeName}.yaml`), 'utf8'));
const locations = await loadLocations(ENGINE);

// Feature names come from the DATA, so validation can tell a scene author that
// "Madhya Pradesh" is fine and "Madya Pradesh" is not, before anything renders.
const featureNames = new Set();
const bboxes = new Map();
for (const f of ['derived/india_states.geojson', 'derived/countries.geojson',
                 'derived/mauryan_empire.geojson']) {
  const fc = JSON.parse(await readFile(join(ENGINE, 'data', f), 'utf8'));
  for (const ft of fc.features) {
    const n = ft.properties.name || ft.properties.NAME;
    if (n) featureNames.add(String(n).toLowerCase());
  }
}

let parsed;
try {
  parsed = await loadScene(resolve(scenePath), { locations, featureNames });
} catch (e) {
  if (e instanceof SceneError) { console.error('\nSCENE INVALID:' + e.message + '\n'); process.exit(1); }
  throw e;
}
const { scene, map } = parsed;
// a scene may switch the window off for a full-bleed map
const frameCfg = (map.frame === false) ? null : (theme.frame || null);

/* ---- a tiny static server, so the page can fetch data and d3 ------------- */
const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json',
                '.geojson': 'application/json', '.css': 'text/css', '.ttf': 'font/ttf',
                '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png' };
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
const page = await browser.newPage({ viewport: { width: W, height: H },
                                     deviceScaleFactor: 1 });
page.on('pageerror', e => console.error('page: ' + e.message));
await page.goto(`http://localhost:${port}/map_engine/renderer/map.html`,
                { waitUntil: 'domcontentloaded' });
await page.evaluate(async ([cfg]) => { await window.MAP.setup(cfg); }, [{
  width: W, height: H, theme,
  // a scene may turn the window off for a full-bleed map
  frame: frameCfg,
  datasets: {
    countries: '/map_engine/data/derived/countries.geojson',
    states: '/map_engine/data/derived/india_states.geojson',
    rivers: '/map_engine/data/derived/rivers.geojson',
    // historical extents, highlightable by name like any other feature
    eras: '/map_engine/data/derived/mauryan_empire.geojson',
    lakes: '/map_engine/data/derived/lakes.geojson',
  },
}]);
await page.waitForFunction(() => window.MAP_READY === true, null, { timeout: 30000 });

const boundsOf = async name => page.evaluate(n => window.MAP.bounds(n), name);

/* the opening camera: an explicit viewport, or fitted to the base region */
let start;
if (map.viewport && map.viewport.center) {
  start = { center: map.viewport.center, zoom: map.viewport.zoom ?? 4.5 };
} else {
  const bb = await boundsOf(map.base || 'India');
  start = bb ? fitBounds(bb, frameCfg ? W - 2 * frameCfg.margin : W,
                             frameCfg ? frameCfg.height
                                      : (theme.content ? theme.content.height : H))
             : { center: [79, 22], zoom: 4.2 };
}

const bcache = new Map();
for (const a of parsed.actions)
  if (a._place && a._place.kind === 'feature' && !bcache.has(a._place.name))
    bcache.set(a._place.name, await boundsOf(a._place.name));
// FIT TO THE WINDOW, NOT THE FRAME. When the data screen's rounded window is
// in use the map occupies 940x900 of a 1080x1920 frame, and fitting a feature
// to the frame makes it far too large for the hole it is drawn into — India's
// northern tip was being cut off by 0.66 degrees, which on this subject is the
// whole point of the exercise, not a cosmetic crop.
// Fit to the CONTENT BOX, not the frame: see the note in map.html. A wide shot
// fitted to the full 1920 puts the southern half of the empire behind the
// presenter who is composited over it.
const contentCfg = (!frameCfg && theme.content) ? theme.content : null;
const vw = frameCfg ? W - 2 * frameCfg.margin : W;
const vh = frameCfg ? frameCfg.height : (contentCfg ? contentCfg.height : H);
const stateAt = makeTimeline(parsed, { width: vw, height: vh, start,
                                       bounds: n => bcache.get(n) });

const layers = Object.assign({ states: true, rivers: false, lakes: false,
                               districts: false, cities: false, labels: true },
                             map.layers || {});
const total = Math.round(scene.duration * FPS);
await mkdir(dirname(OUT), { recursive: true });

const ff = spawn('ffmpeg', ['-y', '-f', 'image2pipe', '-r', String(FPS), '-i', '-',
  '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p',
  '-r', String(FPS), OUT], { stdio: ['pipe', 'ignore', 'pipe'] });
let ffErr = '';
ff.stderr.on('data', d => (ffErr += d));
const done = new Promise((res, rej) =>
  ff.on('close', c => c === 0 ? res() : rej(new Error(`ffmpeg exited ${c}\n${ffErr.slice(-700)}`))));
const write = b => new Promise(r => ff.stdin.write(b) ? r() : ff.stdin.once('drain', r));

console.log(`  ${scene.id}: ${scene.duration}s, ${total} frames, ${W}x${H} @${FPS}`);
const t0 = Date.now();
for (let i = 0; i < total; i++) {
  const t = i / FPS;
  const s = stateAt(t);
  s.layers = layers;
  if (DEBUG) s.debug = `t ${t.toFixed(2)}s  frame ${i}/${total}\n`
    + `centre ${s.camera.center.map(v => v.toFixed(3)).join(', ')}\n`
    + `zoom ${s.camera.zoom.toFixed(2)}  scale ${Math.round(s.camera.scale)}\n`
    + `points ${s.points.length}  routes ${s.routes.length}  highlights ${s.highlights.length}`;
  await page.evaluate(st => window.MAP.frame(st), s);
  await write(await page.screenshot({ type: 'jpeg', quality: 92 }));
  if (i % 15 === 0 || i === total - 1) {
    const pct = Math.round((i + 1) / total * 100);
    process.stdout.write(`\r  ${pct}%  ${i + 1}/${total} frames   `);
  }
}
ff.stdin.end();
await done;
await browser.close(); server.close();
console.log(`\n  -> ${OUT}  (${((Date.now() - t0) / 1000).toFixed(1)}s)`);
process.exit(0);
