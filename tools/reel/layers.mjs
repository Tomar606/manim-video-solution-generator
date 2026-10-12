// Transparent layers for a reel, drawn by a page and written as sparse movies.
//
//   import { renderLayers, renderStills } from '../../../tools/reel/layers.mjs';
//   await renderLayers({ html, outDir, dur: 137.24, layers: ['under', 'mask', 'overlay'] });
//   await renderStills({ html, outDir, times: [3.1, 9.4], layers: ['preview'] });
//
// The page contract:
//   window.render(t, layer)   draws layer `layer` at time t (seconds); may return a promise
//   window.READY              optional promise; fonts are awaited either way
//   #st                       everything that is drawn lives under this element
//
// Grown out of docs/history-poc/overlay_render.mjs (which stays where it is).
// What is different, and why:
//
//   * ONLY FRAMES THAT CHANGE ARE WRITTEN. The old harness skipped the
//     screenshot of an unchanged frame but still piped it to ffmpeg, which
//     decoded and re-encoded it: a 2:22 part came to 1.1 GB of layers. Here an
//     unchanged frame costs nothing at all; each layer is <layer>.mov with one
//     PNG per CHANGE and real timestamps. build_part.py reads it through
//     `fps=30`, which holds each picture until the next one.
//   * "Changed" is a hash of #st's whole serialised DOM, so an SVG attribute or
//     a text node counts, not just style="". A page that draws on a canvas must
//     define window.frameKey(layer) itself.
//   * THE WORK IS SPLIT ACROSS PAGES. render(t) is a function of absolute time,
//     so any frame can be drawn by any page; `workers` pages take 15 s chunks
//     off one queue. Chunk seams are stitched by the same hash.
//   * PNGs are muxed, not transcoded (-c copy).
import { createRequire } from 'node:module';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, '../..');
// Playwright lives in tools/clip/node_modules and nowhere else.
const require = createRequire(path.join(ROOT, 'tools/clip/package.json'));
const { chromium } = require('playwright');

const CHUNK_SECONDS = 15;

// FNV-1a over the serialised stage; runs in the page.
const KEY_JS = `(layer => {
  if (window.frameKey) return String(window.frameKey(layer));
  const s = document.getElementById('st').outerHTML;
  let h = 0x811c9dc5;
  for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 0x01000193); }
  return (h >>> 0).toString(36) + ':' + s.length;
})`;

async function openPage(browser, html, size) {
  const [W, H] = size;
  const pg = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
  const errors = [];
  pg.on('pageerror', e => { errors.push(e.message); console.error('pageerror:', e.message); });
  pg.on('console', m => { if (m.type() === 'error') console.error('page:', m.text()); });
  await pg.setContent(html, { waitUntil: 'load' });
  await pg.evaluate(() => Promise.all([document.fonts.ready, window.READY]));
  if (errors.length) throw new Error('the page threw while loading: ' + errors[0]);
  const cdp = await pg.context().newCDPSession(pg);
  await cdp.send('Emulation.setDefaultBackgroundColorOverride', { color: { r: 0, g: 0, b: 0, a: 0 } });
  const draw = (t, layer) => pg.evaluate(
    `Promise.resolve(window.render(${t}, ${JSON.stringify(layer)})).then(() => ${KEY_JS}(${JSON.stringify(layer)}))`);
  const shot = async () => Buffer.from((await cdp.send('Page.captureScreenshot',
    { format: 'png', optimizeForSpeed: true, captureBeyondViewport: false })).data, 'base64');
  return { pg, draw, shot, errors };
}

/** Write <outDir>/<layer>.mov for every layer. Returns per-layer stats. */
export async function renderLayers({ html, outDir, dur, layers, fps = 30, size = [1080, 1920], workers = 4, log = console.log }) {
  const t0 = Date.now();
  fs.mkdirSync(outDir, { recursive: true });
  const N = Math.ceil(dur * fps - 1e-6);
  const per = Math.round(CHUNK_SECONDS * fps);
  const jobs = [];
  for (const layer of layers) {
    const dir = path.join(outDir, `.frames_${layer}`);
    fs.rmSync(dir, { recursive: true, force: true });
    fs.mkdirSync(dir);
    for (let a = 0; a < N; a += per) jobs.push({ layer, dir, a, b: Math.min(N, a + per) });
  }
  // longest-looking work first is not knowable; interleave layers so pages stay busy
  jobs.sort((x, y) => x.a - y.a);
  const kept = Object.fromEntries(layers.map(l => [l, []]));   // {f, key, file}
  const browser = await chromium.launch();
  let done = 0;
  try {
    const n = Math.max(1, Math.min(workers, jobs.length));
    await Promise.all(Array.from({ length: n }, async () => {
      const { draw, shot, errors } = await openPage(browser, html, size);
      for (let job; (job = jobs.shift());) {
        let last = null;
        for (let f = job.a; f < job.b; f++) {
          const key = await draw(f / fps, job.layer);
          // the very last frame is always written, so the stream is as long as the part
          if (key === last && f !== N - 1) continue;
          const file = path.join(job.dir, `f${String(f).padStart(6, '0')}.png`);
          fs.writeFileSync(file, await shot());
          kept[job.layer].push({ f, key, file });
          last = key;
        }
        if (errors.length) throw new Error('the page threw while drawing: ' + errors[0]);
        log(`  ${job.layer} ${job.a}-${job.b}  (${++done} chunks, ${((Date.now() - t0) / 1000).toFixed(0)}s)`);
      }
    }));
  } finally {
    await browser.close();
  }
  const stats = {};
  for (const layer of layers) {
    const fr = kept[layer].sort((x, y) => x.f - y.f);
    // a chunk always writes its first frame; drop it where it repeats the chunk before
    const uniq = [];
    for (const k of fr) {
      if (uniq.length && uniq[uniq.length - 1].key === k.key && k.f !== N - 1) { fs.rmSync(k.file); continue; }
      uniq.push(k);
    }
    const dir = path.join(outDir, `.frames_${layer}`);
    let list = 'ffconcat version 1.0\n';
    uniq.forEach((k, i) => {
      const next = i + 1 < uniq.length ? uniq[i + 1].f : N;
      // `option framerate` puts every still on the 1/fps grid: without it the stream takes the
      // image demuxer's 1/25 timebase and each start time is rounded to a multiple of 0.04 s
      list += `file '${path.basename(k.file)}'\noption framerate ${fps}\nduration ${((next - k.f) / fps).toFixed(6)}\n`;
    });
    fs.writeFileSync(path.join(dir, 'list.txt'), list);
    const mov = path.join(outDir, `${layer}.mov`), tmp = path.join(outDir, `${layer}.part.mov`);
    // ONE PIXEL FORMAT PER FILE. Chromium writes a fully opaque frame as RGB and any other as
    // RGBA (byte 25 of a PNG: 2 or 6). A layer that is opaque in some frames and not in others
    // (a page with a hole that opens) would change format mid-stream, and ffmpeg then tears
    // down and rebuilds the whole filter graph at each change: the composite of POL-C3-LA-02
    // part 1 grew past 4 GB in half a minute and macOS killed it. Such a layer is re-encoded
    // as RGBA throughout; a layer that is already uniform is muxed untouched.
    const kinds = new Set(uniq.map(k => { const fd = fs.openSync(k.file, 'r'), b = Buffer.alloc(1); fs.readSync(fd, b, 0, 1, 25); fs.closeSync(fd); return b[0]; }));
    const codec = kinds.size > 1 ? ['-c:v', 'png', '-pix_fmt', 'rgba', '-fps_mode', 'passthrough'] : ['-c:v', 'copy'];
    const r = spawnSync('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', path.join(dir, 'list.txt'),
      ...codec, '-video_track_timescale', String(fps * 1000), tmp], { stdio: 'inherit' });
    if (r.status !== 0) throw new Error(`ffmpeg could not mux ${layer}`);
    fs.renameSync(tmp, mov);
    fs.rmSync(dir, { recursive: true, force: true });
    stats[layer] = { frames: N, written: uniq.length, mb: +(fs.statSync(mov).size / 1e6).toFixed(1) };
    log(`wrote ${mov}: ${uniq.length} of ${N} frames, ${stats[layer].mb} MB${kinds.size > 1 ? ' (mixed RGB/RGBA frames, re-encoded as RGBA)' : ''}`);
  }
  log(`layers done in ${((Date.now() - t0) / 1000).toFixed(0)}s`);
  return stats;
}

/** One PNG per layer per time: <outDir>/<layer>_<seconds>.png. Returns the file list. */
export async function renderStills({ html, outDir, times, layers, size = [1080, 1920], log = console.log }) {
  fs.mkdirSync(outDir, { recursive: true });
  const browser = await chromium.launch();
  const files = [];
  try {
    const { draw, shot, errors } = await openPage(browser, html, size);
    for (const layer of layers) for (const t of times) {
      await draw(t, layer);
      const file = path.join(outDir, `${layer}_${t.toFixed(2).padStart(6, '0')}.png`);
      fs.writeFileSync(file, await shot());
      files.push(file);
    }
    if (errors.length) throw new Error('the page threw while drawing: ' + errors[0]);
  } finally {
    await browser.close();
  }
  log(`stills: ${times.length} x ${layers.join(', ')} -> ${outDir}`);
  return files;
}
